#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace multiconnect {

class MasterRingBuffer {
  public:
    explicit MasterRingBuffer(std::size_t capacitySamples);

    std::size_t write(const int16_t* input, std::size_t sampleCount);
    std::size_t readWithOffset(std::size_t logicalReadHead,
                               int32_t offsetSamples,
                               int16_t* output,
                               std::size_t sampleCount) const;

    [[nodiscard]] std::size_t size() const;
    [[nodiscard]] std::size_t capacity() const;

  private:
    std::vector<int16_t> data_;
    std::size_t writeHead_ = 0;
    std::size_t size_ = 0;
};

}  // namespace multiconnect
