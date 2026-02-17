#include "multiconnect/sync_math.h"

#include <cassert>

int main() {
    assert(multiconnect::delayMsToSamples(50, 44100) == 2205);
    assert(multiconnect::delayMsToSamples(0, 44100) == 0);
    assert(multiconnect::delayMsToSamples(-10, 44100) == -441);
    return 0;
}
