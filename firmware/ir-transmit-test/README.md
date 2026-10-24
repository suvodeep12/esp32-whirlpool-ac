# One-command ESP32 IR transmission experiment

The owner explicitly requested continuing without buying parts or using a
multimeter. This project prepares a bounded experiment using the existing
ESP32 and 3 W-labelled transistor-driven IR module. It is not evidence that
the board's USB-to-VIN power path or the module's current draw has been verified.

## Behavior

- GPIO18 is initialized LOW. No transmission occurs on startup.
- A released BOOT button must be observed after five seconds of uptime.
- A subsequent press held for at least 50 ms sends one frame, once per boot.
- Held startup button, switch bounce, later presses and timer rollover are
  covered by pure-logic self-checks at startup, before transmission is enabled.
- Self-check failure prevents sending. Serial `I` only reports status.
- No Wi-Fi, network API, automatic retry, schedule or power-toggle command exists.
- A reset returns to waiting for a new deliberate button press, not auto-send.

The state is the complete captured 24 C message, not an isolated temperature
instruction: `EA 32 0A 00 00 24 C4 E0 1C 00 00 00 00 9E`.
It may restore other settings in that message; its power semantics are untested.
It is not sent through the unrelated built-in 168-bit Whirlpool protocol.

The generated MSB-first waveform uses the timings and 38 kHz carrier reported
in [upstream issue 2204](https://github.com/crankyoldgit/IRremoteESP8266/issues/2204):
3370/1365 us header, 580 us bit marks, 1003/250 us one/zero spaces and 600 us
footer. The original carrier has not been measured. Initial carrier duty is
33 percent to limit average on-time. It does not limit peak LED current.
Nominal frame length is 117873 us; the software requests zero extra repeats.

## Conditional physical experiment

The VIN supply connection below is an **unverified power-path trial**. Photos
and the generic board listing do not establish the path rating. A short burst
reduces duration and average energy but cannot prove electrical suitability.
The wall charger keeps the PC out of this trial; it does not itself protect
the development board against overload. Do not treat successful operation as
a current measurement or a long-term reliability certification.

1. Upload and verify firmware with the transmitter completely disconnected.
2. Unplug the ESP32 USB cable before adding any wires.
3. Connect module IN to D18, module GND to ESP32 GND, module +5V to ESP32 VIN.
   Receiver wiring can stay on 3V3/GND/D19. Never connect +5V to 3V3 or a GPIO.
4. Power the ESP32 USB socket from the existing 5 V-capable Motorola charger.
   Disconnect the PC USB connection. Do not add a second supply to VIN.
5. Check the board powers normally. Wait ten seconds without holding BOOT.
6. With the AC already running, use its physical remote to select 25 C.
   Aim the emitter at the indoor unit from close range for this first test.
7. Press and release BOOT once after startup, not while plugging in power.
   Observe the AC beep/display/settings and report the result. Do not repeatedly
   power-cycle or retry during this first observation.
8. If the board resets or operation is abnormal, disconnect power. The software
   does not make overheating, wrong wiring or a failed switching transistor safe.

The exposed board should rest on a nonconductive surface with no loose contacts.
No AC enclosure, mains wiring, relay or compressor connection is involved.

## Build

Pinned PlatformIO espressif32 6.12.0, Arduino 2.0.17 and IRremoteESP8266 2.9.0.
Use the existing workspace tools and short X: alias as in the receiver project.
Project directory: `firmware/ir-transmit-test`; serial baud: 115200.
The source self-checks are in src/self_test.cpp. Do not attach the transmitter
to a PC-powered board merely to perform the software self-checks.

## Verification on 24 October 2026

The final build passed without compiler warnings, upload succeeded with image
hash verification, and on-device self-checks reported PASS. During a 25-second
serial observation, every status and heartbeat reported sent=0; no automatic
transmission occurred. An offline check verified the payload equals the recorded
checksum-valid 24 C captures and the nominal frame duration is 117873 us.
See [startup observation](startup-check.txt).

Physical emitter output, VIN voltage/current capacity, carrier accuracy and AC
acceptance remain untested. The module was disconnected during these checks.

## Hardware source limits

[Emitter listing](https://www.flyrobo.in/3w-high-power-940nm-infrared-transmitter-module)
specifies 5 V supply, 3.3 V-compatible input and an onboard transistor driver.
[Board listing](https://www.flyrobo.in/esp32-development-board-with-type-c-and-ch340)
specifies USB 5 V input but supplies no VIN output current rating or schematic.
