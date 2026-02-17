#include "multiconnect/sync_engine.h"

#include "multiconnect/sync_math.h"

namespace multiconnect {

SyncEngine::SyncEngine(std::size_t masterCapacitySamples) : ring_(masterCapacitySamples) {}

void SyncEngine::pushPcm16(const int16_t* input, std::size_t sampleCount) {
    ring_.write(input, sampleCount);
}

bool SyncEngine::registerDevice(const std::string& deviceId, int32_t initialOffsetSamples) {
    return devices_.emplace(deviceId, DeviceStreamState{.offsetSamples = initialOffsetSamples, .readHead = 0})
        .second;
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

    // Positive drift means device is effectively late; advance reader by reducing offset.
    const auto correction = delayMsToSamples(static_cast<int32_t>(driftMs), sampleRateHz);
    it->second.offsetSamples -= correction;
    return true;
}

bool SyncEngine::pullForDevice(const std::string& deviceId, int16_t* output, std::size_t sampleCount) {
    const auto it = devices_.find(deviceId);
    if (it == devices_.end()) {
        return false;
    }

    auto& state = it->second;
    const auto read = ring_.readWithOffset(state.readHead, state.offsetSamples, output, sampleCount);
    state.readHead += read;
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

}  // namespace multiconnect
