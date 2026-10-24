#include <Arduino.h>
#include <esp_heap_caps.h>
#include <esp_system.h>

void printInfo() {
  Serial.printf("READY chip=%s cores=%u flash_bytes=%u heap_ok=%u reset=%d\n",
                ESP.getChipModel(), ESP.getChipCores(), ESP.getFlashChipSize(),
                heap_caps_check_integrity_all(true), esp_reset_reason());
}

void setup() {
  Serial.begin(115200);
  delay(200);
  printInfo();
}

void loop() {
  if (Serial.available()) {
    const int command = Serial.read();
    if (command == 'I') printInfo();
    if (command == 'P') Serial.println("PONG");
  }

  static uint32_t previous = 0;
  const uint32_t now = millis();
  if (now - previous >= 1000) {
    previous = now;
    Serial.printf("HEARTBEAT uptime_ms=%u free_heap=%u\n", now, ESP.getFreeHeap());
  }
  delay(1);
}
