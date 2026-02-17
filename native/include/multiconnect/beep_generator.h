#pragma once

#include <cstdint>
#include <vector>

namespace multiconnect {

struct BeepConfig {
    int32_t sampleRateHz = 44100;
    int32_t durationMs = 1000;
    float frequencyHz = 1000.0F;
    float amplitude = 0.6F;
};

// Returns signed 16-bit mono PCM samples.
std::vector<int16_t> generateBeepPcm16(const BeepConfig& config);

}  // namespace multiconnect
