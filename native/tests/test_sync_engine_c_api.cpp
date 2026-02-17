#include "multiconnect/sync_engine_c_api.h"

#include <cassert>
#include <cstdint>
#include <cstring>
#include <vector>

int main() {
    MC_SyncEngine* engine = mc_sync_engine_create(32, 3);
    assert(engine != nullptr);

    assert(mc_sync_engine_register_device(engine, "sony", 0) == 1);
    assert(mc_sync_engine_register_device(engine, "tribit", 2) == 1);
    assert(mc_sync_engine_device_count(engine) == 2);

    const std::vector<int16_t> source = {1, 2, 3, 4};
    mc_sync_engine_push_pcm16(engine, source.data(), source.size());

    std::vector<int16_t> sonyOut(4, 0);
    std::size_t read = 0;
    assert(mc_sync_engine_pull_for_device(engine, "sony", sonyOut.data(), sonyOut.size(), &read) == 1);
    assert(read == 4);
    assert(sonyOut[0] == 1);

    MC_DeviceOffset offsets[2] = {};
    const std::size_t totalOffsets = mc_sync_engine_get_device_offsets(engine, offsets, 2);
    assert(totalOffsets == 2);
    assert(std::strcmp(offsets[0].device_id, "sony") == 0);
    assert(offsets[0].offset_samples == 0);

    MC_DeviceOffset newOffsets[3] = {};
    std::strncpy(newOffsets[0].device_id, "sony", sizeof(newOffsets[0].device_id) - 1);
    newOffsets[0].offset_samples = 5;
    std::strncpy(newOffsets[1].device_id, "tribit", sizeof(newOffsets[1].device_id) - 1);
    newOffsets[1].offset_samples = -2;
    std::strncpy(newOffsets[2].device_id, "missing", sizeof(newOffsets[2].device_id) - 1);
    newOffsets[2].offset_samples = 99;

    assert(mc_sync_engine_apply_device_offsets(engine, newOffsets, 3) == 2);
    assert(mc_sync_engine_reset_all_device_offsets(engine, 4) == 2);

    MC_DeviceOffset afterReset[2] = {};
    assert(mc_sync_engine_get_device_offsets(engine, afterReset, 2) == 2);
    assert(afterReset[0].offset_samples == 4);
    assert(afterReset[1].offset_samples == 4);

    assert(mc_sync_engine_unregister_device(engine, "sony") == 1);
    assert(mc_sync_engine_device_count(engine) == 1);

    mc_sync_engine_destroy(engine);
    return 0;
}
