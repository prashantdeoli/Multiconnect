#include "multiconnect/sync_math.h"

#include <algorithm>

namespace multiconnect {

int32_t delayMsToSamples(int32_t delayMs, int32_t sampleRateHz) {
    const int32_t safeSampleRate = std::max(sampleRateHz, 1);
    return static_cast<int32_t>((static_cast<int64_t>(delayMs) * safeSampleRate) / 1000);
}

}  // namespace multiconnect
