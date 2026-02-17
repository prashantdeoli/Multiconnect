#include "multiconnect/sync_engine.h"

#include "multiconnect/sync_math.h"

#include <algorithm>
#include <cmath>

namespace multiconnect {

SyncEngine::SyncEngine(std::size_t masterCapacitySamples, int32_t maxCorrectionSamplesPerCall)
    : ring_(masterCapacitySamples), maxCorrectionSamplesPerCall_(std::max(maxCorrectionSamplesPerCall, 0)) {}

void SyncEngine::pushPcm16(const int16_t* input, std::size_t sampleCount) {
    ring_.write(input, sampleCount);
}

bool SyncEngine::registerDevice(const std::string& deviceId, int32_t initialOffsetSamples) {
    DeviceStreamState state;
    state.offsetSamples = initialOffsetSamples;
    state.readHead = 0;

    const bool inserted = devices_.emplace(deviceId, state).second;
    if (inserted) {
        metrics_.emplace(deviceId, DeviceStreamMetrics{});
    }

    return inserted;
}

bool SyncEngine::unregisterDevice(const std::string& deviceId) {
    metrics_.erase(deviceId);
    return devices_.erase(deviceId) > 0;
}

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

    auto metricIt = metrics_.find(deviceId);
    if (metricIt == metrics_.end()) {
        metricIt = metrics_.emplace(deviceId, DeviceStreamMetrics{}).first;
    }

    // Positive drift means device is effectively late; advance reader by reducing offset.
    const auto driftRoundedMs = static_cast<int32_t>(std::lround(driftMs));
    const auto requestedCorrectionSamples = delayMsToSamples(driftRoundedMs, sampleRateHz);
    const auto clampedCorrectionSamples = std::clamp(requestedCorrectionSamples,
                                                     -maxCorrectionSamplesPerCall_,
                                                     maxCorrectionSamplesPerCall_);

    it->second.offsetSamples -= clampedCorrectionSamples;

    auto& metric = metricIt->second;
    metric.driftCorrectionsApplied += 1;
    metric.lastDriftCorrectionSamples = clampedCorrectionSamples;

    return true;
}

bool SyncEngine::pullForDevice(const std::string& deviceId,
                               int16_t* output,
                               std::size_t sampleCount,
                               std::size_t* outReadSamples) {
    const auto it = devices_.find(deviceId);
    if (it == devices_.end() || (output == nullptr && sampleCount > 0)) {
        return false;
    }

    auto& state = it->second;
    auto metricIt = metrics_.find(deviceId);
    if (metricIt == metrics_.end()) {
        metricIt = metrics_.emplace(deviceId, DeviceStreamMetrics{}).first;
    }
    auto& metric = metricIt->second;

    const auto read = ring_.readWithOffset(state.readHead, state.offsetSamples, output, sampleCount);
    state.readHead += read;

    metric.pullCalls += 1;
    metric.pulledSamples += read;
    metric.lastReadSamples = read;

    if (outReadSamples != nullptr) {
        *outReadSamples = read;
    }

    return true;
}


bool SyncEngine::resetDeviceMetrics(const std::string& deviceId) {
    const auto it = metrics_.find(deviceId);
    if (it == metrics_.end()) {
        return false;
    }

    it->second = DeviceStreamMetrics{};
    return true;
}

void SyncEngine::resetAllMetrics() {
    for (auto& [deviceId, metric] : metrics_) {
        (void)deviceId;
        metric = DeviceStreamMetrics{};
    }
}

std::size_t SyncEngine::deviceCount() const { return devices_.size(); }

std::vector<std::string> SyncEngine::registeredDeviceIds() const {
    std::vector<std::string> ids;
    ids.reserve(devices_.size());
    for (const auto& [deviceId, state] : devices_) {
        (void)state;
        ids.push_back(deviceId);
    }
    return ids;
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

DeviceStreamMetrics SyncEngine::deviceMetrics(const std::string& deviceId) const {
    const auto it = metrics_.find(deviceId);
    if (it == metrics_.end()) {
        return {};
    }

    return it->second;
}

}  // namespace multiconnect
