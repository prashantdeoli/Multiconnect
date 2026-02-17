#include "multiconnect/sync_engine.h"

#include "multiconnect/sync_math.h"

#include <algorithm>
#include <cmath>

namespace multiconnect {

SyncEngine::SyncEngine(std::size_t masterCapacitySamples, int32_t maxCorrectionSamplesPerCall)
    : ring_(masterCapacitySamples), maxCorrectionSamplesPerCall_(std::max(maxCorrectionSamplesPerCall, 0)) {}

void SyncEngine::pushPcm16(const int16_t* input, std::size_t sampleCount) { ring_.write(input, sampleCount); }

bool SyncEngine::registerDevice(const std::string& deviceId, int32_t initialOffsetSamples) {
    return devices_.emplace(deviceId, DeviceStreamState{initialOffsetSamples, 0}).second;
}

bool SyncEngine::unregisterDevice(const std::string& deviceId) { return devices_.erase(deviceId) > 0; }

bool SyncEngine::setDeviceOffsetSamples(const std::string& deviceId, int32_t offsetSamples) {
    const auto it = devices_.find(deviceId);
    if (it == devices_.end()) {
        return false;
    }

    it->second.offsetSamples = offsetSamples;
    return true;
}

bool SyncEngine::applyDriftCorrectionMs(const std::string& deviceId, float driftMs, int32_t sampleRateHz) {
    const auto it = devices_.find(deviceId);
    if (it == devices_.end()) {
        return false;
    }

    int32_t correction = delayMsToSamples(static_cast<int32_t>(std::lround(driftMs)), sampleRateHz);
    if (maxCorrectionSamplesPerCall_ > 0) {
        correction = std::clamp(correction, -maxCorrectionSamplesPerCall_, maxCorrectionSamplesPerCall_);
    }

    // Positive drift means device is effectively late; advance reader by reducing offset.
    it->second.offsetSamples -= correction;
    return true;
}

bool SyncEngine::pullForDevice(const std::string& deviceId, int16_t* output, std::size_t sampleCount) {
    return pullForDevice(deviceId, output, sampleCount, nullptr);
}

bool SyncEngine::pullForDevice(const std::string& deviceId,
                               int16_t* output,
                               std::size_t sampleCount,
                               std::size_t* outReadSamples) {
    const auto it = devices_.find(deviceId);
    if (it == devices_.end()) {
        if (outReadSamples != nullptr) {
            *outReadSamples = 0;
        }
        return false;
    }

    auto& state = it->second;
    const auto read = ring_.readWithOffset(state.readHead, state.offsetSamples, output, sampleCount);
    state.readHead += read;

    if (outReadSamples != nullptr) {
        *outReadSamples = read;
    }
    return true;
}

std::size_t SyncEngine::bufferedSamples() const { return ring_.size(); }

bool SyncEngine::hasDevice(const std::string& deviceId) const {
    return devices_.find(deviceId) != devices_.end();
}

DeviceStreamState SyncEngine::deviceState(const std::string& deviceId) const {
    const auto it = devices_.find(deviceId);
    if (it == devices_.end()) {
        return {};
    }

    return it->second;
}

std::size_t SyncEngine::deviceCount() const { return devices_.size(); }

std::vector<DeviceOffset> SyncEngine::deviceOffsets() const {
    std::vector<DeviceOffset> offsets;
    offsets.reserve(devices_.size());

    for (const auto& [deviceId, state] : devices_) {
        offsets.push_back({deviceId, state.offsetSamples});
    }

    std::sort(offsets.begin(), offsets.end(), [](const DeviceOffset& lhs, const DeviceOffset& rhs) {
        return lhs.deviceId < rhs.deviceId;
    });
    return offsets;
}

std::size_t SyncEngine::applyDeviceOffsets(const std::vector<DeviceOffset>& offsets) {
    std::size_t applied = 0;
    for (const auto& entry : offsets) {
        if (setDeviceOffsetSamples(entry.deviceId, entry.offsetSamples)) {
            ++applied;
        }
    }

    return applied;
}

std::size_t SyncEngine::resetAllDeviceOffsets(int32_t offsetSamples) {
    for (auto& [_, state] : devices_) {
        state.offsetSamples = offsetSamples;
    }

    return devices_.size();
}

}  // namespace multiconnect
