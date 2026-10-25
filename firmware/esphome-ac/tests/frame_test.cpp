#include "../captured_frames.h"
#include <cassert>

int main() {
  assert(captured::selfTest());
  for (const auto invalid : {-1, 0, 16, 23, 26, 30, 256})
    assert(captured::waveform(invalid).empty());
  for (const int temp : {24, 25}) {
    const auto data = captured::waveform(temp);
    assert(data.size() == 227);
    assert(data[0] == 3370 && data[1] == -1365 && data.back() == 600);
    unsigned duration = 0;
    uint8_t decoded[14] = {};
    for (const auto pulse : data) duration += pulse > 0 ? pulse : -pulse;
    assert(duration == (temp == 24 ? 117873U : 116367U));
    for (unsigned bit = 0; bit < 112; ++bit) {
      assert(data[2 + bit * 2] == 580);
      const auto space = data[3 + bit * 2];
      assert(space == -250 || space == -1003);
      decoded[bit / 8] = (decoded[bit / 8] << 1) | (space == -1003);
    }
    const auto *expected = temp == 24 ? captured::state24 : captured::state25;
    for (unsigned i = 0; i < 14; ++i) assert(decoded[i] == expected[i]);
  }
}
