# Prepare the requested 20–26 C range

The owner requested 20–26 C, then became busy before confirming the capture
wiring. **Preparation is complete; no capture-profile upload was performed.**
The running controller still sends only the previously captured 24/25 C states.
New 20/21/22/23/26 C commands are not enabled.

## Prepared and checked

- `capture.yaml` adds ESPHome's native GPIO19 IR receiver/raw dumper to the
  existing controller package. It uses the same device name, private keys and
  ESP-IDF version. It does not add transmit buttons or startup/reconnect sends.
- Logger code is compiled at INFO, initially runs at WARN, and selectively
  enables only the `remote.raw` INFO tag. Web logs remain disabled.
- ESPHome 2026.10.0 / ESP-IDF 5.5.6 validation and compilation passed. Flash
  estimate: 844,335 bytes (46.0% of the app partition); static DRAM: 45,688 bytes.
- The RX hardware allocation is 192 RMT symbols, with 192 receive symbols;
  the existing TX uses 64. GPIO19 is inverted with an input pull-up, a 50 us
  filter and a 10 ms frame idle timeout.
- All **13 Python tests pass**. The analyzer reproduces the existing verdicts
  for all eight historical captures, including the two incomplete ones.
  Separate synthetic tests cover range boundaries, repeats, changed settings,
  malformed logs, overflow, private-log filtering and evidence-file protection.
- Actual ESPHome/KY-022 reception, fresh range captures and wider AC responses
  remain untested. Synthetic frames are not physical observations.

The native raw dumper emits signed durations in wrapped lines. In this pinned
implementation it omits the final idle space, so the complete target frame has
227 printed durations, including its footer mark. Missing data is rejected,
never padded. [Pinned dumper source](https://github.com/esphome/esphome/blob/2026.10.0/esphome/components/remote_base/raw_protocol.cpp).

## Analysis rules

`analyse_capture.py` accepts only the `remote.raw` tag and excludes unrelated
log text from the report. It validates frame length, signed mark/space order,
header/footer, fixed signature and checksum. Empirical timing windows, in us:
header mark 2500–4250; header space 1000–1750; bit/footer mark 400–850;
zero space 80–450; one space 800–1300. These windows cover the saved KY-022
captures, not every possible receiver or environment.

Temperature remains a **candidate**, decoded as `31 - reverse(byte 7)`.
Every non-temperature byte preceding the checksum must match the known state;
changed power/mode/fan/swing or other fields are flagged for review. A receiver,
UART or logger overflow warning invalidates the entire session. Counts require
two matching eligible frames per requested temperature. Repeats from one held
press are not proof of two independent human actions: manually confirm the
remote display and obtain separate presses. `manual_confirmation_required`
remains true even when coverage is complete. No script edits firmware controls.

Raw logs stay private; only review sanitized IR reports for publication.
CLI input is limited to 4 MiB, frame parsing to 512 durations, and an existing
output file cannot be overwritten.

## Expected states for comparison only

These are **predictions**, not newly captured remote frames. The common bytes
are `EA 32 0A 00 00 24 C4 [temperature] 1C 00 00 00 00 [checksum]`.

| Target | Temperature byte | Checksum byte | Physical evidence |
|---|---|---|---|
| 20 C | D0 | BE | Pending |
| 21 C | 50 | 3E | Pending |
| 22 C | 90 | DE | Pending |
| 23 C | 10 | 5E | Pending |
| 24 C | E0 | 9E | Existing remote capture and owner-reported AC response |
| 25 C | 60 | 1E | Existing remote capture and owner-reported AC response |
| 26 C | A0 | EE | Pending |

An offline assertion-based comparison reproduced all seven predictions with
the inspected peer encoder using `remoteState=0`, matching our known non-temp
state. That does not establish the meaning of every field or physical support
on this AC. No peer implementation was copied into the firmware.
[Pinned peer implementation](https://github.com/0xPiyush/irtxrx/blob/b23013a75c0e9eec9150ebd08b2d388f7d1d3337/src/protocols/whirlpool_magicool.ts).

## Resume when the owner is available

1. With USB power unplugged, disconnect transmitter +5V and check KY-022 wiring:
   supply to 3V3, ground to GND, signal to GPIO19. Reconnect PC USB and confirm
   the setup. No wiring changes while powered.
2. Upload the already built capture profile only after that confirmation. Use a
   separate `ESPHOME_BUILD_PATH` for capture builds to preserve the controller
   build. Verify frame self-checks, receiver startup and absence of RMT faults.
3. Save serial logs privately while obtaining separate captures for each target,
   confirming the original remote LCD. Use individual presses about a second
   apart, initially about 50–100 cm from the receiver. Aim away from the AC
   when possible. Do not change mode/fan/swing as part of a temperature capture.
4. Run the analysis below and review repeated payloads against the LCD values.
   Stop on receiver faults or overflow and start a new clean session.
5. Only then extend the send allowlist/UI and run supervised AC trials for the
   new targets. Keep power controls, schedules and inferred actual AC state out
   of scope. Restore the normal non-capture profile after learning.

From this folder, using the configured ESPHome environment:

```powershell
esphome compile capture.yaml
esphome upload capture.yaml --device COM3 --upload_speed 115200
# Logs may contain local network diagnostics; never commit the full log.
New-Item -ItemType Directory -Force .private | Out-Null
esphome logs capture.yaml --device COM3 2>&1 |
  Out-File -LiteralPath .private\range-capture.log -Encoding utf8 -NoClobber
python analyse_capture.py .private\range-capture.log --output .private\range-analysis.json
python -m unittest discover -s tests -p 'test_*.py' -v
```

Check the current port; COM3 is historical. Stop the log command after the
capture session. The Windows short-path/cache workaround remains documented
in the main README. None of these instructions qualifies the unmeasured
transmitter current, thermal behavior or USB-to-VIN power path.
