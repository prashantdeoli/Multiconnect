#include "multiconnect/master_ring_buffer.h"
#include "multiconnect/sync_math.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
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
}  // namespace

int main(int argc, char** argv) {
    constexpr int32_t sampleRateHz = 44100;
    constexpr int32_t durationMs = 1000;

    int32_t offsetMsDeviceB = 35;
    if (argc > 1) {
        offsetMsDeviceB = std::atoi(argv[1]);
    }

    auto pattern = makeImpulsePattern(sampleRateHz, durationMs);
    multiconnect::MasterRingBuffer ring(pattern.size());
    ring.write(pattern.data(), pattern.size());

    std::vector<int16_t> deviceA(pattern.size(), 0);
    std::vector<int16_t> deviceB(pattern.size(), 0);

    ring.readWithOffset(0, 0, deviceA.data(), deviceA.size());

    const int32_t targetOffsetSamples = multiconnect::delayMsToSamples(offsetMsDeviceB, sampleRateHz);
    ring.readWithOffset(0, targetOffsetSamples, deviceB.data(), deviceB.size());

    const auto impulseA = findFirstImpulse(deviceA, INT16_MAX / 2);
    const auto impulseB = findFirstImpulse(deviceB, INT16_MAX / 2);

    const int64_t sampleDelta = static_cast<int64_t>(impulseA) - static_cast<int64_t>(impulseB);
    const double measuredOffsetMs = static_cast<double>(sampleDelta) * 1000.0 / sampleRateHz;

    std::cout << "POC_RESULT sampleRate=" << sampleRateHz << "Hz"
              << " requestedOffsetMs=" << offsetMsDeviceB << " measuredOffsetMs=" << measuredOffsetMs
              << '\n';

    const bool pass = std::abs(measuredOffsetMs - static_cast<double>(offsetMsDeviceB)) <= 1.0;
    std::cout << (pass ? "PASS" : "FAIL") << '\n';
    return pass ? 0 : 1;
}
