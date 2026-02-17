#pragma once

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct MC_SyncEngine MC_SyncEngine;

typedef struct {
    char device_id[128];
    int32_t offset_samples;
} MC_DeviceOffset;

MC_SyncEngine* mc_sync_engine_create(size_t master_capacity_samples,
                                     int32_t max_correction_samples_per_call);
void mc_sync_engine_destroy(MC_SyncEngine* engine);

int mc_sync_engine_register_device(MC_SyncEngine* engine, const char* device_id, int32_t initial_offset_samples);
int mc_sync_engine_unregister_device(MC_SyncEngine* engine, const char* device_id);

void mc_sync_engine_push_pcm16(MC_SyncEngine* engine, const int16_t* input, size_t sample_count);

int mc_sync_engine_pull_for_device(MC_SyncEngine* engine,
                                   const char* device_id,
                                   int16_t* output,
                                   size_t sample_count,
                                   size_t* out_read_samples);

int mc_sync_engine_set_device_offset_samples(MC_SyncEngine* engine,
                                             const char* device_id,
                                             int32_t offset_samples);
int mc_sync_engine_apply_drift_correction_ms(MC_SyncEngine* engine,
                                             const char* device_id,
                                             float drift_ms,
                                             int32_t sample_rate_hz);

size_t mc_sync_engine_device_count(const MC_SyncEngine* engine);
size_t mc_sync_engine_get_device_offsets(const MC_SyncEngine* engine,
                                         MC_DeviceOffset* out_offsets,
                                         size_t max_offsets);
size_t mc_sync_engine_apply_device_offsets(MC_SyncEngine* engine,
                                           const MC_DeviceOffset* offsets,
                                           size_t offset_count);
size_t mc_sync_engine_reset_all_device_offsets(MC_SyncEngine* engine, int32_t offset_samples);

#ifdef __cplusplus
}
#endif
