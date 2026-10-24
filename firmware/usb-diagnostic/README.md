# ESP32 USB diagnostic

This project checks basic USB programming and operation before AC automation.
It uses serial at 115200 baud, reports chip/flash/heap information, replies to
`I` with information and `P` with `PONG`, and sends one heartbeat per second.
It does not initialize Wi-Fi, Bluetooth, an IR driver or GPIO outputs.

## Hardware identified on 24 October 2026

- USB serial: CH340, Windows COM3, signed WCH driver 4.0.2026.2.
- Chip: ESP32-D0WD-V3 revision 3.1, two cores, 40 MHz crystal.
- Flash: 4 MB, flash voltage reported as 3.3 V.
- Full original flash backup: workspace `work/esp32-original-flash.bin`.
- Backup was verified against the device using esptool's digest comparison before upload.

The flash backup is private working material, excluded from this deliverable.
Its restore has not been exercised. Never restore it onto a different board.

## Build and verify on this Windows workspace

PlatformIO Core 6.2.0 and esptool 5.6.0 are in the workspace virtual environment
`work/esp32-tools`. PlatformIO packages are in `work/platformio-core`.
The project pins platform-espressif32 6.12.0 / Arduino 2.0.17. PlatformIO supplies
its own upload tool, esptool 4.9.0. This is a diagnostic baseline, not a claim
that an older toolchain is the only compatible option.

Long workspace paths caused compiler process-start failures. A short temporary
drive alias allowed the same compiler and project to build. From the original
workspace root, with X: unused:

```powershell
subst X: "$PWD"
$env:PLATFORMIO_CORE_DIR = 'X:\work\platformio-core'
& 'X:\work\esp32-tools\Scripts\pio.exe' run -d 'X:\firmware\usb-diagnostic'
# The next command overwrites firmware; only use with the intended board connected.
& 'X:\work\esp32-tools\Scripts\pio.exe' run -d 'X:\firmware\usb-diagnostic' -t upload --upload-port COM3
& 'X:\work\esp32-tools\Scripts\python.exe' 'X:\firmware\usb-diagnostic\verify_serial.py' --port COM3 --log 'X:\work\esp32-serial-check.txt'
subst X: /D
```

Do not remove a drive mapping belonging to another task. Close any serial
monitor before using esptool, uploading or running the checker. COM numbers
can change after reconnecting. Keep this diagnostic's first test USB-only.

The checker observes about 35 seconds, checks info and bidirectional responses,
heap integrity, at least 25 heartbeats, monotonic uptime and gaps below 2.5 seconds.
This does not test IR compatibility, GPIO wiring, radio operation, long-term
stability, high-current emitter power or cold starts from a wall adapter.

## Verified result

On 24 October 2026, the build completed without compiler warnings, upload
succeeded and all written image regions passed esptool's hash verification.
The physical-board checker passed: expected chip identity, two cores, 4 MB
flash, heap-integrity checks, bidirectional serial responses and 35 consecutive
heartbeats in its observation window. Reported free heap stayed at 351408 bytes;
uptime increased without an observed reboot or excessive heartbeat gap.
See [captured serial output](serial-check.txt).

The board is left running this USB diagnostic, with IR modules disconnected.
The temporary X: drive alias was removed after verification.

## References

- [PlatformIO ESP32 development board profile](https://docs.platformio.org/en/stable/boards/espressif32/esp32dev.html)
- [Pinned platform release](https://github.com/platformio/platform-espressif32/releases/tag/v6.12.0)
- [Espressif flash read and verification commands](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-commands.html)
