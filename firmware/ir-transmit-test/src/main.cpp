#include <Arduino.h>
#include <IRsend.h>
#include "TestLogic.h"

constexpr uint16_t kEmitterPin = 18;
constexpr uint8_t kBootButton = 0;
IRsend emitter(kEmitterPin);
OneShotButton button;
bool testsPassed = false;
bool sent = false;

void printInfo() {
  Serial.printf("TX_TEST gpio=18 button=BOOT self_tests=%s sent=%u\n",
                testsPassed ? "PASS" : "FAIL", sent);
}

void setup() {
  digitalWrite(kEmitterPin, LOW);
  emitter.begin();
  pinMode(kBootButton, INPUT_PULLUP);
  Serial.begin(115200);
  testsPassed = runSelfTests();
  printInfo();
}

void loop() {
  if (Serial.available() && Serial.read() == 'I') printInfo();
  if (testsPassed && button.update(digitalRead(kBootButton) == LOW, millis())) {
    sent = true;
    // Timings/carrier follow issue 2204; the original carrier was not measured.
    emitter.sendGeneric(3370, 1365, 580, 1003, 580, 250, 600, 0,
                        kState24, sizeof(kState24), 38, true, 0, 33);
    digitalWrite(kEmitterPin, LOW);
    Serial.println("SENT_ONE_FRAME state=24C carrier_khz=38 duty_percent=33");
  }
  static uint32_t previous = 0;
  const uint32_t now = millis();
  if (now - previous >= 5000) {
    previous = now;
    Serial.printf("HEARTBEAT uptime_ms=%u sent=%u\n", now, sent);
  }
  delay(1);
}
