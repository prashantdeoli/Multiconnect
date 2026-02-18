#include "multiconnect/beep_generator.h"

#include <algorithm>
#include <cassert>
#include <cstdint>

int main() {
    multiconnect::BeepConfig config;
    config.sampleRateHz = 48000;
    config.durationMs = 1000;
    config.frequencyHz = 1000.0F;
    config.amplitude = 0.5F;

    const auto samples = multiconnect::generateBeepPcm16(config);
    assert(samples.size() == 48000);

    const auto maxIt = std::max_element(samples.begin(), samples.end());
    const auto minIt = std::min_element(samples.begin(), samples.end());
    assert(maxIt != samples.end());
    assert(minIt != samples.end());
    assert(*maxIt > 0);
    assert(*minIt < 0);
    assert(*maxIt <= static_cast<int16_t>(INT16_MAX / 2 + 64));

    multiconnect::BeepConfig clamped = config;
    clamped.amplitude = 2.0F;
    const auto loud = multiconnect::generateBeepPcm16(clamped);
    const auto loudMaxIt = std::max_element(loud.begin(), loud.end());
    assert(loudMaxIt != loud.end());
    assert(*loudMaxIt <= INT16_MAX);

    return 0;
}
