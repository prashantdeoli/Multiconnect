#include "multiconnect/sync_engine.h"

#include <cassert>
#include <cstdint>
#include <vector>

int main() {
    multiconnect::SyncEngine engine(32);

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

    // 1.6ms at 1kHz should round to 2ms -> 2 samples correction.
    assert(engine.applyDriftCorrectionMs("tribit", 1.6F, 1000));
    const auto state = engine.deviceState("tribit");
    assert(state.offsetSamples == 0);

    assert(engine.setDeviceOffsetSamples("tribit", -1));
    assert(engine.deviceState("tribit").offsetSamples == -1);

    assert(!engine.pullForDevice("missing", tribit.data(), tribit.size(), nullptr));
    assert(!engine.applyDriftCorrectionMs("missing", 1.0F, 1000));

    assert(engine.unregisterDevice("sony"));
    assert(!engine.hasDevice("sony"));

    return 0;
}
