#pragma once

#include "multiconnect/master_ring_buffer.h"

#include <cstddef>
#include <cstdint>
#include <string>
#include <unordered_map>

namespace multiconnect {

struct DeviceStreamState {
    int32_t offsetSamples = 0;
    std::size_t readHead = 0;
};

class SyncEngine {
  public:
    explicit SyncEngine(std::size_t masterCapacitySamples);

    void pushPcm16(const int16_t* input, std::size_t sampleCount);

    bool registerDevice(const std::string& deviceId, int32_t initialOffsetSamples = 0);
    bool unregisterDevice(const std::string& deviceId);

    bool setDeviceOffsetSamples(const std::string& deviceId, int32_t offsetSamples);
    bool applyDriftCorrectionMs(const std::string& deviceId, float driftMs, int32_t sampleRateHz);

    // Pulls cloned samples for a specific device based on its read head and offset.
    // Returns false if device is unknown. When true, outReadSamples contains actual sample count read.
    bool pullForDevice(const std::string& deviceId,
                       int16_t* output,
                       std::size_t sampleCount,
                       std::size_t* outReadSamples = nullptr);

    [[nodiscard]] std::size_t bufferedSamples() const;
    [[nodiscard]] bool hasDevice(const std::string& deviceId) const;
    [[nodiscard]] DeviceStreamState deviceState(const std::string& deviceId) const;

  private:
    MasterRingBuffer ring_;
    std::unordered_map<std::string, DeviceStreamState> devices_;
};

}  // namespace multiconnect
