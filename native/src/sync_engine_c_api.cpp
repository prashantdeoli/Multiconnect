#include "multiconnect/sync_engine_c_api.h"

#include "multiconnect/sync_engine.h"

#include <cstring>
#include <vector>

struct MC_SyncEngine {
    multiconnect::SyncEngine impl;

    explicit MC_SyncEngine(std::size_t masterCapacitySamples, int32_t maxCorrectionSamplesPerCall)
        : impl(masterCapacitySamples, maxCorrectionSamplesPerCall) {}
};

extern "C" {

MC_SyncEngine* mc_sync_engine_create(size_t master_capacity_samples,
                                     int32_t max_correction_samples_per_call) {
    return new MC_SyncEngine(master_capacity_samples, max_correction_samples_per_call);
}

void mc_sync_engine_destroy(MC_SyncEngine* engine) {
    delete engine;
}

int mc_sync_engine_register_device(MC_SyncEngine* engine, const char* device_id, int32_t initial_offset_samples) {
    if (engine == nullptr || device_id == nullptr) {
        return 0;
    }

    return engine->impl.registerDevice(device_id, initial_offset_samples) ? 1 : 0;
}

int mc_sync_engine_unregister_device(MC_SyncEngine* engine, const char* device_id) {
    if (engine == nullptr || device_id == nullptr) {
        return 0;
    }

    return engine->impl.unregisterDevice(device_id) ? 1 : 0;
}

void mc_sync_engine_push_pcm16(MC_SyncEngine* engine, const int16_t* input, size_t sample_count) {
    if (engine == nullptr) {
        return;
    }

    engine->impl.pushPcm16(input, sample_count);
}

int mc_sync_engine_pull_for_device(MC_SyncEngine* engine,
                                   const char* device_id,
                                   int16_t* output,
                                   size_t sample_count,
                                   size_t* out_read_samples) {
    if (engine == nullptr || device_id == nullptr) {
        return 0;
    }

    return engine->impl.pullForDevice(device_id, output, sample_count, out_read_samples) ? 1 : 0;
}

int mc_sync_engine_set_device_offset_samples(MC_SyncEngine* engine,
                                             const char* device_id,
                                             int32_t offset_samples) {
    if (engine == nullptr || device_id == nullptr) {
        return 0;
    }

    return engine->impl.setDeviceOffsetSamples(device_id, offset_samples) ? 1 : 0;
}

int mc_sync_engine_apply_drift_correction_ms(MC_SyncEngine* engine,
                                             const char* device_id,
                                             float drift_ms,
                                             int32_t sample_rate_hz) {
    if (engine == nullptr || device_id == nullptr) {
        return 0;
    }

    return engine->impl.applyDriftCorrectionMs(device_id, drift_ms, sample_rate_hz) ? 1 : 0;
}

size_t mc_sync_engine_device_count(const MC_SyncEngine* engine) {
    if (engine == nullptr) {
        return 0;
    }

    return engine->impl.deviceCount();
}

size_t mc_sync_engine_get_device_offsets(const MC_SyncEngine* engine,
                                         MC_DeviceOffset* out_offsets,
                                         size_t max_offsets) {
    if (engine == nullptr) {
        return 0;
    }

    const auto offsets = engine->impl.deviceOffsets();
    if (out_offsets == nullptr || max_offsets == 0) {
        return offsets.size();
    }

    const std::size_t writeCount = offsets.size() < max_offsets ? offsets.size() : max_offsets;
    for (std::size_t i = 0; i < writeCount; ++i) {
        std::strncpy(out_offsets[i].device_id, offsets[i].deviceId.c_str(), sizeof(out_offsets[i].device_id) - 1);
        out_offsets[i].device_id[sizeof(out_offsets[i].device_id) - 1] = '\0';
        out_offsets[i].offset_samples = offsets[i].offsetSamples;
    }

    return offsets.size();
}

size_t mc_sync_engine_apply_device_offsets(MC_SyncEngine* engine,
                                           const MC_DeviceOffset* offsets,
                                           size_t offset_count) {
    if (engine == nullptr || offsets == nullptr || offset_count == 0) {
        return 0;
    }

    std::vector<multiconnect::DeviceOffset> converted;
    converted.reserve(offset_count);
    for (std::size_t i = 0; i < offset_count; ++i) {
        if (offsets[i].device_id[0] == '\0') {
            continue;
        }

        converted.push_back({offsets[i].device_id, offsets[i].offset_samples});
    }

    return engine->impl.applyDeviceOffsets(converted);
}

size_t mc_sync_engine_reset_all_device_offsets(MC_SyncEngine* engine, int32_t offset_samples) {
    if (engine == nullptr) {
        return 0;
    }

    return engine->impl.resetAllDeviceOffsets(offset_samples);
}

}  // extern "C"
