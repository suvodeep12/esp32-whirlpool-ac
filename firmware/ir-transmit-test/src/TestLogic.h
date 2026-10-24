#pragma once
#include <cstdint>

constexpr uint8_t kState24[14] = {
    0xEA, 0x32, 0x0A, 0x00, 0x00, 0x24, 0xC4,
    0xE0, 0x1C, 0x00, 0x00, 0x00, 0x00, 0x9E};

inline uint8_t reverseByte(uint8_t value) {
  uint8_t reversed = 0;
  for (uint8_t bit = 0; bit < 8; ++bit) {
    reversed = (reversed << 1) | (value & 1);
    value >>= 1;
  }
  return reversed;
}

inline bool validChecksum(const uint8_t (&state)[14]) {
  uint8_t sum = 0;
  for (uint8_t i = 0; i < 13; ++i) sum += reverseByte(state[i]);
  return state[13] == reverseByte(sum);
}

class OneShotButton {
 public:
  bool update(bool pressed, uint32_t now) {
    if (used_) return false;
    if (!released_) {
      if (!pressed && now >= 5000) released_ = true;
      return false;
    }
    if (!pressed) {
      pressing_ = false;
      return false;
    }
    if (!pressing_) {
      pressing_ = true;
      since_ = now;
      return false;
    }
    if (uint32_t(now - since_) < 50) return false;
    used_ = true;
    return true;
  }

 private:
  bool released_ = false;
  bool pressing_ = false;
  bool used_ = false;
  uint32_t since_ = 0;
};

bool runSelfTests();
