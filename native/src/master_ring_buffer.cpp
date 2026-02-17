#include "multiconnect/master_ring_buffer.h"

#include <algorithm>

namespace multiconnect {

MasterRingBuffer::MasterRingBuffer(std::size_t capacitySamples)
    : data_(std::max<std::size_t>(capacitySamples, 1), 0) {}

std::size_t MasterRingBuffer::write(const int16_t* input, std::size_t sampleCount) {
    if (input == nullptr || sampleCount == 0) {
        return 0;
    }

    for (std::size_t i = 0; i < sampleCount; ++i) {
        data_[writeHead_] = input[i];
        writeHead_ = (writeHead_ + 1) % data_.size();
        size_ = std::min(size_ + 1, data_.size());
    }

    return sampleCount;
}

std::size_t MasterRingBuffer::readWithOffset(std::size_t logicalReadHead,
                                             int32_t offsetSamples,
                                             int16_t* output,
                                             std::size_t sampleCount) const {
    if (output == nullptr || sampleCount == 0 || size_ == 0) {
        return 0;
    }

    const std::size_t readable = std::min(sampleCount, size_);
    for (std::size_t i = 0; i < readable; ++i) {
        const int64_t shifted = static_cast<int64_t>(logicalReadHead + i) + offsetSamples;
        const int64_t normalized = ((shifted % static_cast<int64_t>(data_.size())) +
                                    static_cast<int64_t>(data_.size())) %
                                   static_cast<int64_t>(data_.size());
        output[i] = data_[static_cast<std::size_t>(normalized)];
    }

    // Clear tail when caller asked for more samples than currently readable,
    // so downstream audio paths never consume stale buffer values.
    for (std::size_t i = readable; i < sampleCount; ++i) {
        output[i] = 0;
    }

    return readable;
}

std::size_t MasterRingBuffer::size() const { return size_; }

std::size_t MasterRingBuffer::capacity() const { return data_.size(); }

}  // namespace multiconnect
