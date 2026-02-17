#include "multiconnect/master_ring_buffer.h"
#include "multiconnect/sync_math.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <string_view>
#include <chrono>
#include <vector>

namespace {
std::vector<int16_t> makeImpulsePattern(int32_t sampleRateHz, int32_t durationMs) {
    const int sampleCount = static_cast<int>((static_cast<int64_t>(sampleRateHz) * durationMs) / 1000);
    std::vector<int16_t> signal(sampleCount, 0);

    const int impulseA = static_cast<int>((static_cast<int64_t>(sampleRateHz) * 100) / 1000);
    const int impulseB = static_cast<int>((static_cast<int64_t>(sampleRateHz) * 320) / 1000);
    if (impulseA < sampleCount) signal[impulseA] = INT16_MAX;
    if (impulseB < sampleCount) signal[impulseB] = INT16_MAX / 2;

    return signal;
}

std::size_t findFirstImpulse(const std::vector<int16_t>& signal, int16_t threshold) {
    for (std::size_t i = 0; i < signal.size(); ++i) {
        if (signal[i] >= threshold) {
            return i;
        }
    }
    return signal.size();
}

struct CliOptions {
    int32_t offsetMsDeviceB = 35;
    double thresholdMs = 1.0;
    std::string artifactDir;
    std::string deviceA = "deviceA";
    std::string deviceB = "deviceB";
    std::string notes;
};

bool parseDouble(std::string_view text, double* outValue) {
    if (outValue == nullptr) {
        return false;
    }

    char* end = nullptr;
    const std::string owned(text);
    const double value = std::strtod(owned.c_str(), &end);
    if (end == owned.c_str() || *end != '\0') {
        return false;
    }

    *outValue = value;
    return true;
}

CliOptions parseArgs(int argc, char** argv) {
    CliOptions options;
    bool offsetAssigned = false;

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];

        if (arg == "--threshold-ms" && i + 1 < argc) {
            double parsed = 0.0;
            if (parseDouble(argv[++i], &parsed) && parsed >= 0.0) {
                options.thresholdMs = parsed;
            }
            continue;
        }

        if (arg == "--artifact-dir" && i + 1 < argc) {
            options.artifactDir = argv[++i];
            continue;
        }

        if (arg == "--device-a" && i + 1 < argc) {
            options.deviceA = argv[++i];
            continue;
        }

        if (arg == "--device-b" && i + 1 < argc) {
            options.deviceB = argv[++i];
            continue;
        }

        if (arg == "--notes" && i + 1 < argc) {
            options.notes = argv[++i];
            continue;
        }

        if (!offsetAssigned) {
            options.offsetMsDeviceB = std::atoi(arg.c_str());
            offsetAssigned = true;
        }
    }

    return options;
}

std::string makeRunTimestamp() {
    const auto now = std::chrono::system_clock::now();
    const auto nowTime = std::chrono::system_clock::to_time_t(now);
    std::tm tm = *std::gmtime(&nowTime);

    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y%m%dT%H%M%SZ");
    return oss.str();
}

void writeArtifactReport(const CliOptions& options,
                         int32_t sampleRateHz,
                         int32_t durationMs,
                         double measuredOffsetMs,
                         double errorFromRequestedMs,
                         bool pass) {
    if (options.artifactDir.empty()) {
        return;
    }

    namespace fs = std::filesystem;
    fs::create_directories(options.artifactDir);

    const auto timestamp = makeRunTimestamp();
    const fs::path outputPath = fs::path(options.artifactDir) / ("poc_run_" + timestamp + ".json");
    std::ofstream out(outputPath);
    if (!out.is_open()) {
        std::cerr << "WARN unable to open artifact report path=" << outputPath << '\n';
        return;
    }

    out << "{\n"
        << "  \"timestamp\": \"" << timestamp << "\",\n"
        << "  \"sampleRateHz\": " << sampleRateHz << ",\n"
        << "  \"durationMs\": " << durationMs << ",\n"
        << "  \"deviceA\": \"" << options.deviceA << "\",\n"
        << "  \"deviceB\": \"" << options.deviceB << "\",\n"
        << "  \"requestedOffsetMs\": " << options.offsetMsDeviceB << ",\n"
        << "  \"measuredOffsetMs\": " << measuredOffsetMs << ",\n"
        << "  \"errorFromRequestedMs\": " << errorFromRequestedMs << ",\n"
        << "  \"thresholdMs\": " << options.thresholdMs << ",\n"
        << "  \"outcome\": \"" << (pass ? "PASS" : "FAIL") << "\",\n"
        << "  \"notes\": \"" << options.notes << "\"\n"
        << "}\n";
}
}  // namespace

int main(int argc, char** argv) {
    constexpr int32_t sampleRateHz = 44100;
    constexpr int32_t durationMs = 1000;
    const CliOptions options = parseArgs(argc, argv);

    auto pattern = makeImpulsePattern(sampleRateHz, durationMs);
    multiconnect::MasterRingBuffer ring(pattern.size());
    ring.write(pattern.data(), pattern.size());

    std::vector<int16_t> deviceA(pattern.size(), 0);
    std::vector<int16_t> deviceB(pattern.size(), 0);

    ring.readWithOffset(0, 0, deviceA.data(), deviceA.size());

    const int32_t targetOffsetSamples = multiconnect::delayMsToSamples(options.offsetMsDeviceB, sampleRateHz);
    ring.readWithOffset(0, targetOffsetSamples, deviceB.data(), deviceB.size());

    const auto impulseA = findFirstImpulse(deviceA, INT16_MAX / 2);
    const auto impulseB = findFirstImpulse(deviceB, INT16_MAX / 2);

    const int64_t sampleDelta = static_cast<int64_t>(impulseA) - static_cast<int64_t>(impulseB);
    const double measuredOffsetMs = static_cast<double>(sampleDelta) * 1000.0 / sampleRateHz;

    const double errorFromRequestedMs = std::abs(measuredOffsetMs - static_cast<double>(options.offsetMsDeviceB));

    std::cout << "POC_RESULT sampleRate=" << sampleRateHz << "Hz"
              << " requestedOffsetMs=" << options.offsetMsDeviceB << " measuredOffsetMs=" << measuredOffsetMs
              << " errorFromRequestedMs=" << errorFromRequestedMs << " thresholdMs=" << options.thresholdMs
              << " deviceA=" << options.deviceA << " deviceB=" << options.deviceB << '\n';

    const bool pass = errorFromRequestedMs <= options.thresholdMs;

    writeArtifactReport(options, sampleRateHz, durationMs, measuredOffsetMs, errorFromRequestedMs, pass);

    std::cout << (pass ? "PASS" : "FAIL") << '\n';
    return pass ? 0 : 1;
}
