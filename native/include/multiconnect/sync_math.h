#pragma once

#include <cstdint>

namespace multiconnect {

constexpr int kDefaultSampleRateHz = 44100;

// Converts milliseconds of delay into sample count.
// Example: 50ms at 44100Hz => 2205 samples.
int32_t delayMsToSamples(int32_t delayMs, int32_t sampleRateHz = kDefaultSampleRateHz);

}  // namespace multiconnect
