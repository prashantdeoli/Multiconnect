#pragma once

#include "multiconnect/master_ring_buffer.h"

#include <cstddef>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

namespace multiconnect {

struct DeviceStreamState {
    int32_t offsetSamples = 0;
    std::size_t readHead = 0;
};

struct DeviceOffset {
    std::string deviceId;
    int32_t offsetSamples = 0;
};

class SyncEngine {
  public:
    explicit SyncEngine(std::size_t masterCapacitySamples, int32_t maxCorrectionSamplesPerCall = 0);

    void pushPcm16(const int16_t* input, std::size_t sampleCount);

    bool registerDevice(const std::string& deviceId, int32_t initialOffsetSamples = 0);
    bool unregisterDevice(const std::string& deviceId);

    bool setDeviceOffsetSamples(const std::string& deviceId, int32_t offsetSamples);
    bool applyDriftCorrectionMs(const std::string& deviceId, float driftMs, int32_t sampleRateHz);

    // Pulls cloned samples for a specific device based on its read head and offset.
    bool pullForDevice(const std::string& deviceId, int16_t* output, std::size_t sampleCount);
    bool pullForDevice(const std::string& deviceId,
                       int16_t* output,
                       std::size_t sampleCount,
                       std::size_t* outReadSamples);

    [[nodiscard]] std::size_t bufferedSamples() const;
    [[nodiscard]] bool hasDevice(const std::string& deviceId) const;
    [[nodiscard]] DeviceStreamState deviceState(const std::string& deviceId) const;

    [[nodiscard]] std::size_t deviceCount() const;
    [[nodiscard]] std::vector<DeviceOffset> deviceOffsets() const;
    std::size_t applyDeviceOffsets(const std::vector<DeviceOffset>& offsets);
    std::size_t resetAllDeviceOffsets(int32_t offsetSamples);

  private:
    MasterRingBuffer ring_;
    std::unordered_map<std::string, DeviceStreamState> devices_;
    int32_t maxCorrectionSamplesPerCall_;
};

}  // namespace multiconnect
