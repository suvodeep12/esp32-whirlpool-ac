# ESP32 receive-only AC remote capture

Receiver wiring is confirmed by the owner; it has not been independently
inspected after connection. KY-022 supply goes to ESP32 3V3, ground to GND,
and S to GPIO19 (D19). The transmitter remains disconnected.

This firmware initializes only USB serial and IR reception on GPIO19.
It has no transmitter instance, transmit call, Wi-Fi setup or AC-control API.
It replaces the earlier USB diagnostic; that source and original-flash backup
remain in the workspace.

## Configuration

- PlatformIO platform-espressif32 6.12.0 / Arduino 2.0.17.
- IRremoteESP8266 2.9.0, all default decoders available.
- Serial: 115200 baud; send `I` for readiness information.
- Capture buffer: 1024 entries, 50 ms end-of-message timeout, save buffer enabled.
- Unknown-message threshold: 12, following the upstream example.
- Every five seconds: heartbeat, capture count, current input level and free heap.
- Each capture: timestamp, overflow flag, decoded result, AC description when
  available, raw timings/state in library source-code format and END_CAPTURE.

Saved-buffer mode resumes reception inside the library before decoding; the
application does not reset that buffer again after printing. Serial printing
and decoding still impose finite throughput. Do not hold remote buttons during
initial tests. Do not use captures with overflow=1 as complete protocol evidence.
The 50 ms timeout is an initial AC baseline, not a universal optimum.

## Build and upload

From the original workspace root, use the same short-path workaround documented
in the USB diagnostic project. X: must be unused:

```powershell
subst X: "$PWD"
$env:PLATFORMIO_CORE_DIR = 'X:\work\platformio-core'
& 'X:\work\esp32-tools\Scripts\pio.exe' run -d 'X:\firmware\ir-receiver'
& 'X:\work\esp32-tools\Scripts\pio.exe' run -d 'X:\firmware\ir-receiver' -t upload --upload-port COM3
& 'X:\work\esp32-tools\Scripts\pio.exe' device monitor --port COM3 --baud 115200
# Close the monitor before removing the mapping or running another serial tool.
subst X: /D
```

## Initial physical test

Point the physical remote's IR window at the receiver window from 20–50 cm.
Face away from the AC to reduce the chance of changing it during testing.
Press temperature up once, wait three seconds, then temperature down once.
Keep the displayed temperature/settings as ground truth for comparison with
decoded values. Reception alone does not establish that the AC accepts a replay,
and this firmware cannot determine actual AC power state.

An idle HIGH input and passing firmware self-check prove neither correct wiring
nor working optical reception. That requires a recorded remote signal. A 38 kHz
demodulating receiver cannot precisely measure the source carrier frequency.

## Verification on 24 October 2026

Final firmware compiled without warnings and uploaded successfully, with image
hash verification. A 75-second serial observation passed the library sanity
check and recorded 15 heartbeats with free heap 344940 bytes and monotonic uptime.
GPIO19 sampled HIGH at each heartbeat. No IR messages were captured during that
initial window; optical reception and Whirlpool compatibility remain unverified.

## First remote captures

The owner performed temperature up followed by down and confirmed the remote
displayed 25 C then 24 C. Both captures had overflow=0 and the default library
decoder reported UNKNOWN. Saved evidence: [raw serial log](captures/initial.txt)
and [offline analysis](captures/initial-analysis.json).

- First capture: 225 raw entries / 111 candidate data bits, incomplete. Excluded
  from replay or a reliable checksum claim; no missing bit was repaired.
- Second capture: 227 raw entries / 112 candidate data bits. MSB-first bytes:
  `EA 32 0A 00 00 24 C4 E0 1C 00 00 00 00 9E`.
- The second frame matches the prefix, length, timing family, temperature field
  and checksum algorithm reported in upstream [Whirlpool India issue 2204](https://github.com/crankyoldgit/IRremoteESP8266/issues/2204).
  The reported E0 temperature field maps to 24 C, confirmed by the owner.
- With each byte viewed LSB-first, its byte-sum checksum is 0x79 and matches
  the received final byte; bit reversal gives the 0x9E MSB-first representation.

This is strong evidence for that reported 112-bit variant, not a tested AC
transmitter implementation. UNKNOWN's printed bit count and hash are not a
validated protocol identifier. The cause of the first incomplete frame is
unknown; buffer capacity was not exhausted. More repeat captures are needed.

The built-in 168-bit WHIRLPOOL_AC decoder/sender is a different format. Its
power-toggle behavior must not be assumed to apply to this captured variant.
The issue reporter describes off/mode fields, but the owner's exact AC power
semantics remain untested. No power, fan or swing command has been replayed.

## Six-press repeat test

The owner repeated up/down three times at the requested 50–100 cm range.
See [raw repeat log](captures/repeat.txt) and [analysis](captures/repeat-analysis.json).
Five frames had 112 candidate data bits, valid checksums and temperatures
24, 25, 24, 25, 24 C. The first frame contained only 109 candidate data bits
and was rejected. All six reported overflow=0. These are observations from
one short trial, not a long-term reception success-rate estimate.

Every valid 24 C frame was byte-identical to the earlier valid 24 C capture.
Both valid 25 C frames were byte-identical:
`EA 32 0A 00 00 24 C4 60 1C 00 00 00 00 1E`.
Between the valid 24/25 C payloads, only byte 7 (temperature, zero-based)
and byte 13 (checksum) differed. Offline assertions checked these invariants.

This strengthens the 112-bit protocol match. Physical-remote synchronisation
remains unreliable with missing frames; a decoder cannot reconstruct a missed
command with certainty. These receive trials preceded the owner-reported
successful 24 C transmission documented in the transmit-test project.
A replay carries a whole AC state, so it must not be assumed to change only
temperature. Power and mode effects require supervised observation.

The owner has no multimeter. Availability and rating of a phone charger and a
safe 5 V connection method are pending; leave the transmitter disconnected.

## Sources

- [Upstream IRrecvDumpV3 at v2.9.0](https://github.com/crankyoldgit/IRremoteESP8266/blob/v2.9.0/examples/IRrecvDumpV3/IRrecvDumpV3.ino)
- [Saved-buffer behavior in IRrecv.cpp](https://github.com/crankyoldgit/IRremoteESP8266/blob/v2.9.0/src/IRrecv.cpp)
