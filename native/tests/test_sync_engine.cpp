#include "multiconnect/sync_engine.h"

#include <cassert>
#include <cstdint>
#include <vector>

int main() {
    multiconnect::SyncEngine engine(32, 3);

    assert(engine.registerDevice("sony", 0));
    assert(engine.registerDevice("tribit", 2));
    assert(!engine.registerDevice("sony", 0));

    const std::vector<int16_t> source = {1, 2, 3, 4, 5, 6, 7, 8};
    engine.pushPcm16(source.data(), source.size());

    std::vector<int16_t> sony(4, 0);
    std::vector<int16_t> tribit(4, 0);

    std::size_t sonyRead = 0;
    std::size_t tribitRead = 0;
    assert(engine.pullForDevice("sony", sony.data(), sony.size(), &sonyRead));
    assert(engine.pullForDevice("tribit", tribit.data(), tribit.size(), &tribitRead));
    assert(sonyRead == 4);
    assert(tribitRead == 4);

    assert(sony[0] == 1);
    assert(tribit[0] == 3);

    const auto sonyMetrics = engine.deviceMetrics("sony");
    const auto tribitMetrics = engine.deviceMetrics("tribit");
    assert(sonyMetrics.pullCalls == 1);
    assert(sonyMetrics.pulledSamples == 4);
    assert(sonyMetrics.lastReadSamples == 4);
    assert(tribitMetrics.pullCalls == 1);
    assert(tribitMetrics.pulledSamples == 4);

    // 1.6ms at 1kHz should round to 2ms -> 2 samples correction.
    assert(engine.applyDriftCorrectionMs("tribit", 1.6F, 1000));
    auto state = engine.deviceState("tribit");
    assert(state.offsetSamples == 0);

    // Large requested correction (20 samples) should clamp to maxCorrectionSamplesPerCall (3).
    assert(engine.applyDriftCorrectionMs("tribit", 20.0F, 1000));
    state = engine.deviceState("tribit");
    assert(state.offsetSamples == -3);

    const auto postDriftMetrics = engine.deviceMetrics("tribit");
    assert(postDriftMetrics.driftCorrectionsApplied == 2);
    assert(postDriftMetrics.lastDriftCorrectionSamples == 3);

    assert(engine.setDeviceOffsetSamples("tribit", -1));
    assert(engine.deviceState("tribit").offsetSamples == -1);

    assert(!engine.pullForDevice("missing", tribit.data(), tribit.size(), nullptr));
    assert(!engine.applyDriftCorrectionMs("missing", 1.0F, 1000));

    // Invalid output buffer should be rejected for non-zero reads.
    assert(!engine.pullForDevice("tribit", nullptr, 4, nullptr));

    multiconnect::SyncEngine partialEngine(16);
    assert(partialEngine.registerDevice("partial", 0));
    const std::vector<int16_t> tiny = {42, 43};
    partialEngine.pushPcm16(tiny.data(), tiny.size());
    std::vector<int16_t> out(5, -7);
    std::size_t outRead = 0;
    assert(partialEngine.pullForDevice("partial", out.data(), out.size(), &outRead));
    assert(outRead == 2);
    assert(out[0] == 42);
    assert(out[1] == 43);
    assert(out[2] == 0);
    assert(out[3] == 0);
    assert(out[4] == 0);

    assert(engine.unregisterDevice("sony"));
    assert(!engine.hasDevice("sony"));
    const auto removedMetrics = engine.deviceMetrics("sony");
    assert(removedMetrics.pullCalls == 0);

    return 0;
}
