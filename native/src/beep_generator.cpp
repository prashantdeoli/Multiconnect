#include "multiconnect/beep_generator.h"

#include <algorithm>
#include <cmath>

namespace multiconnect {

namespace {
constexpr float kPi = 3.14159265358979323846F;
}

std::vector<int16_t> generateBeepPcm16(const BeepConfig& config) {
    const int32_t sampleRate = std::max(config.sampleRateHz, 1);
    const int32_t durationMs = std::max(config.durationMs, 1);
    const int32_t sampleCount = static_cast<int32_t>((static_cast<int64_t>(sampleRate) * durationMs) / 1000);

    const float clampedAmplitude = std::clamp(config.amplitude, 0.0F, 1.0F);
    std::vector<int16_t> buffer;
    buffer.reserve(sampleCount);

    for (int32_t i = 0; i < sampleCount; ++i) {
        const float t = static_cast<float>(i) / static_cast<float>(sampleRate);
        const float sample = std::sin(2.0F * kPi * config.frequencyHz * t);
        const float scaled = sample * clampedAmplitude * static_cast<float>(INT16_MAX);
        buffer.push_back(static_cast<int16_t>(scaled));
    }

    return buffer;
}

}  // namespace multiconnect
