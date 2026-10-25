# ESP32 Whirlpool AC experiments

Local IR-control research and firmware for a non-Wi-Fi Whirlpool split inverter
AC, model **SAI18B31N0D/2021**, using an ESP32, KY-022 receiver and a
transistor-driven 940 nm emitter. No Raspberry Pi, cloud account or always-on
PC is required for the standalone button-triggered experiment.

**Status: experimental. The owner reports one successful ESP32 transmission:
the running AC changed from 25 C to 24 C. Wider controls and long-term
reliability remain unverified.**

## Evidence so far

| Check | Observed result |
|---|---|
| Board | ESP32-D0WD-V3 rev 3.1, two cores, 4 MB flash; CH340 USB serial |
| USB diagnostic | Build/upload passed; 35 heartbeats, bidirectional serial and heap-integrity checks passed |
| First remote trial | One complete checksum-valid 24 C frame; one incomplete frame rejected |
| Six-press repeat trial | Five complete checksum-valid frames; one incomplete frame rejected |
| State comparison | Repeated valid 24/25 C payloads were identical at each temperature; only temperature byte and checksum differed |
| Transmit-test software | On-device self-checks passed; no sends during a 25-second startup observation with emitter disconnected |
| Actual AC acceptance | Owner reports one 24 C command changed the running AC from 25 C to 24 C |

These are bounded observations from 24 October 2026, not long-term reliability
figures. The default IRremoteESP8266 v2.9.0 decoder reports UNKNOWN. The captured
frame matches the separate 112-bit Whirlpool India format reported in
[upstream issue 2204](https://github.com/crankyoldgit/IRremoteESP8266/issues/2204),
including checksum and a temperature confirmed on the physical remote.
The library's built-in 168-bit Whirlpool protocol is a different format.

## Projects and records

- [USB diagnostic](firmware/usb-diagnostic/README.md): basic board checks and a reusable serial checker.
- [Receive-only capture](firmware/ir-receiver/README.md): GPIO19 capture firmware, original raw timings and offline analysis results.
- [One-command transmit experiment](firmware/ir-transmit-test/README.md): GPIO18, one manual BOOT-button trigger per boot, no startup send or automatic retry.
- [ESPHome phone controller](firmware/esphome-ac/README.md): selected standalone web interface, captured 24/25 C buttons, private phone provisioning; see its acceptance record before treating it as validated.
- [GitHub / Home Assistant comparison](docs/github-reuse.md): reuse decision and independent peer-protocol experiment.
- [Research and parts comparison](docs/ac-ir-research.md): sources, Indian seller observations, electrical unknowns, power-state limitations and future steps.

## Local setup

Python 3.11 and USB serial access are needed. On Windows PowerShell, from this
repository's root:

```powershell
python -m venv work\esp32-tools
.\work\esp32-tools\Scripts\python.exe -m pip install -r requirements-lock.txt
$env:PLATFORMIO_CORE_DIR = Join-Path $PWD 'work\platformio-core'
.\work\esp32-tools\Scripts\pio.exe run -d firmware\ir-receiver
```

The recorded Python versions are in requirements-lock.txt. Project configurations
pin platform-espressif32 6.12.0 and IRremoteESP8266 2.9.0 where used. The observed
Arduino framework package was 3.20017.241212+sha.dcc1105b (Arduino 2.0.17), and
the upload tool was esptool 4.9.0 supplied by PlatformIO. Platform package
dependencies are not a fully vendored/offline toolchain.

Long Windows paths caused compiler subprocess failures in the original workspace.
The project READMEs document the tested short-drive-alias workaround. Verify that
the alias is unused before creating it. COM3 was the original observed port;
check the current port rather than assuming it stays the same.

Install the CH340 driver only if required, using the
[chip manufacturer's driver page](https://www.wch-ic.com/downloads/ch341ser_exe.html).
An installed driver or successful build does not establish working optical IR.

## Receiver connection

With USB unplugged, connect KY-022 ground to ESP32 GND, supply to 3V3, and S/OUT
to GPIO19. Verify labels on the actual module. A module header's order differs
from the bare receiver IC's pin numbering. Do not feed a 5 V output into ESP32 GPIO.

## Transmitter and power limits

The existing emitter module is advertised for a 5 V supply and 3.3 V-compatible
input, with an onboard transistor. Its actual current, thermal behavior and the
development board's USB-to-VIN current capacity are **unmeasured**. No verified
board schematic was found. The owner requested no further purchases and no
multimeter; the transmit project documents a conditional short experiment,
not an electrically qualified installation.

That experiment uses a wall charger instead of PC power. It sends a single
approximately 118 ms frame at a nominal 38 kHz / 33 percent carrier duty.
Short duration limits energy and average on-time; it does not limit peak current
or prove a power path safe. Never connect the emitter's power input to a GPIO
or 3V3, and do not join independent 5 V supplies together.

## AC state and reliability

The captured command carries a whole AC state. It must not be treated as an
isolated temperature adjustment or assumed to have the built-in Whirlpool
protocol's power-toggle semantics. The exact power behavior remains untested.

Receiving a physical remote command establishes observed intent, not that the
AC received it. Missing frames, ESP32 restarts and AC power interruptions can
desynchronise an estimated state. Start power as unknown until independently
confirmed. No firmware here automatically restores AC power after a restart.

The ESPHome Wi-Fi interface is implemented; its phone provisioning and optical
acceptance gates are tracked separately. Unattended automation is not enabled.
Raw original flash backups, local tool installations, personal photos, account
credentials and delivery-location details are not part of this public source
snapshot. All included capture evidence is local AC-remote test data.
