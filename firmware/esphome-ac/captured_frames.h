#pragma once
#include <cstdint>
#include <vector>

namespace captured {
// Exact captured MSB-first states; never substitute the library's 168-bit protocol.
constexpr uint8_t state24[] = {0xEA,0x32,0x0A,0,0,0x24,0xC4,0xE0,0x1C,0,0,0,0,0x9E};
constexpr uint8_t state25[] = {0xEA,0x32,0x0A,0,0,0x24,0xC4,0x60,0x1C,0,0,0,0,0x1E};

inline uint8_t reverseByte(uint8_t value) {
  uint8_t out = 0;
  for (unsigned bit = 0; bit < 8; ++bit) {
    out = (out << 1) | (value & 1);
    value >>= 1;
  }
  return out;
}

inline bool checksum(const uint8_t *state) {
  uint8_t sum = 0;
  for (unsigned i = 0; i < 13; ++i) sum += reverseByte(state[i]);
  return reverseByte(state[13]) == sum;
}

inline std::vector<int32_t> waveform(int temperature) {
  if (temperature != 24 && temperature != 25) return {};
  const uint8_t *state = temperature == 24 ? state24 : state25;
  std::vector<int32_t> pulses;
  pulses.reserve(227);
  pulses.push_back(3370);
  pulses.push_back(-1365);
  for (unsigned i = 0; i < 14; ++i) {
    for (int bit = 7; bit >= 0; --bit) {
      pulses.push_back(580);
      pulses.push_back(state[i] & (1 << bit) ? -1003 : -250);
    }
  }
  pulses.push_back(600);
  return pulses;
}

inline bool selfTest() {
  if (!waveform(23).empty() || !waveform(26).empty()) return false;
  for (int temperature : {24, 25}) {
    const uint8_t *state = temperature == 24 ? state24 : state25;
    if (!checksum(state)) return false;
    auto pulses = waveform(temperature);
    if (pulses.size() != 227 || pulses[0] != 3370 ||
        pulses[1] != -1365 || pulses.back() != 600) return false;
    uint32_t duration = 0;
    for (auto pulse : pulses) duration += pulse > 0 ? pulse : -pulse;
    if (duration != (temperature == 24 ? 117873U : 116367U)) return false;
    uint8_t decoded[14] = {};
    for (unsigned bit = 0; bit < 112; ++bit) {
      if (pulses[2 + 2 * bit] != 580) return false;
      const auto space = pulses[3 + 2 * bit];
      if (space != -250 && space != -1003) return false;
      decoded[bit / 8] = (decoded[bit / 8] << 1) | (space == -1003);
    }
    for (unsigned i = 0; i < 14; ++i) if (decoded[i] != state[i]) return false;
  }
  uint8_t corrupt[14];
  for (unsigned i = 0; i < 14; ++i) corrupt[i] = state24[i];
  corrupt[7] ^= 1;
  return !checksum(corrupt);
}
}  // namespace captured
