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

struct DeviceStreamMetrics {
    std::size_t pullCalls = 0;
    std::size_t pulledSamples = 0;
    std::size_t lastReadSamples = 0;
    std::size_t driftCorrectionsApplied = 0;
    int32_t lastDriftCorrectionSamples = 0;
};

class SyncEngine {
  public:
    explicit SyncEngine(std::size_t masterCapacitySamples, int32_t maxCorrectionSamplesPerCall = 256);

    void pushPcm16(const int16_t* input, std::size_t sampleCount);

    bool registerDevice(const std::string& deviceId, int32_t initialOffsetSamples = 0);
    bool unregisterDevice(const std::string& deviceId);

    bool setDeviceOffsetSamples(const std::string& deviceId, int32_t offsetSamples);
    bool applyDriftCorrectionMs(const std::string& deviceId, float driftMs, int32_t sampleRateHz);

    // Pulls cloned samples for a specific device based on its read head and offset.
    // Returns false if device is unknown or output is null when sampleCount > 0.
    // When true, outReadSamples contains actual sample count read.
    bool pullForDevice(const std::string& deviceId,
                       int16_t* output,
                       std::size_t sampleCount,
                       std::size_t* outReadSamples = nullptr);

    [[nodiscard]] std::size_t bufferedSamples() const;
    [[nodiscard]] bool hasDevice(const std::string& deviceId) const;
    [[nodiscard]] DeviceStreamState deviceState(const std::string& deviceId) const;
    [[nodiscard]] DeviceStreamMetrics deviceMetrics(const std::string& deviceId) const;

  private:
    MasterRingBuffer ring_;
    int32_t maxCorrectionSamplesPerCall_;
    std::unordered_map<std::string, DeviceStreamState> devices_;
    std::unordered_map<std::string, DeviceStreamMetrics> metrics_;
};

}  // namespace multiconnect
