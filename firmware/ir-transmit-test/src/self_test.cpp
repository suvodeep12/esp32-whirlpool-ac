#include "TestLogic.h"
#include <cstring>

bool runSelfTests() {
  OneShotButton held;
  if (held.update(true, 0) || held.update(true, 6000)) return false;
  if (held.update(false, 7000) || held.update(true, 8000)) return false;
  if (held.update(true, 8049) || !held.update(true, 8050)) return false;
  if (held.update(true, 9000) || held.update(false, 10000) ||
      held.update(true, 11000) || held.update(true, 12000)) return false;

  OneShotButton bounce;
  if (bounce.update(false, 0) || bounce.update(false, 4999)) return false;
  if (bounce.update(false, 5000) || bounce.update(true, 6000) ||
      bounce.update(false, 6020) || bounce.update(true, 6030) ||
      bounce.update(true, 6079) || !bounce.update(true, 6080)) return false;

  OneShotButton rollover;
  if (rollover.update(false, UINT32_MAX - 100) ||
      rollover.update(true, UINT32_MAX - 20) ||
      !rollover.update(true, 40)) return false;

  if (!validChecksum(kState24)) return false;
  uint8_t corrupt[14];
  std::memcpy(corrupt, kState24, sizeof(corrupt));
  corrupt[7] ^= 1;
  return !validChecksum(corrupt);
}
