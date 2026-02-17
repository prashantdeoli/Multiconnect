#include "multiconnect/master_ring_buffer.h"

#include <cassert>
#include <cstdint>
#include <vector>

int main() {
    multiconnect::MasterRingBuffer ring(8);
    const std::vector<int16_t> source = {1, 2, 3, 4, 5, 6, 7, 8};
    ring.write(source.data(), source.size());

    std::vector<int16_t> noOffset(8, 0);
    ring.readWithOffset(0, 0, noOffset.data(), noOffset.size());
    assert(noOffset[0] == 1);
    assert(noOffset[7] == 8);

    std::vector<int16_t> plusTwo(8, 0);
    ring.readWithOffset(0, 2, plusTwo.data(), plusTwo.size());
    assert(plusTwo[0] == 3);

    std::vector<int16_t> minusOne(8, 0);
    ring.readWithOffset(0, -1, minusOne.data(), minusOne.size());
    assert(minusOne[0] == 8);

    return 0;
}
