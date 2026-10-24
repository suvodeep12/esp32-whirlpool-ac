#include <Arduino.h>
#include <IRrecv.h>
#include <IRremoteESP8266.h>
#include <IRac.h>
#include <IRutils.h>
#include <assert.h>

constexpr uint16_t kReceiverPin = 19;
IRrecv receiver(kReceiverPin, 1024, 50, true);
decode_results result;
uint32_t captures = 0;

void printInfo() {
  Serial.printf("READY receiver_gpio=%u buffer=1024 timeout_ms=50 sanity=%u library=%s\n",
                kReceiverPin, irutils::lowLevelSanityCheck(),
                _IRREMOTEESP8266_VERSION_STR);
}

void setup() {
  Serial.begin(115200);
  delay(200);
  assert(irutils::lowLevelSanityCheck() == 0);
  receiver.setUnknownThreshold(12);
  receiver.enableIRIn();
  printInfo();
}

void loop() {
  if (Serial.available() && Serial.read() == 'I') printInfo();

  if (receiver.decode(&result)) {
    Serial.printf("CAPTURE number=%u uptime_ms=%lu overflow=%u\n",
                  ++captures, millis(), result.overflow);
    Serial.print(resultToHumanReadableBasic(&result));
    const String description = IRAcUtils::resultAcToString(&result);
    if (description.length()) Serial.println(description);
    Serial.println(resultToSourceCode(&result));
    Serial.println("END_CAPTURE");
  }

  static uint32_t previous = 0;
  const uint32_t now = millis();
  if (now - previous >= 5000) {
    previous = now;
    Serial.printf("HEARTBEAT uptime_ms=%u captures=%u input=%d free_heap=%u\n",
                  now, captures, digitalRead(kReceiverPin), ESP.getFreeHeap());
  }
  delay(1);
}
