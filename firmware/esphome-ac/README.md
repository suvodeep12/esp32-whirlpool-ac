# Standalone ESPHome phone control

Selected by the owner on 25 October 2026. This uses the standard ESPHome web
interface, without Home Assistant, MQTT, a cloud account or an always-on PC.
Home Assistant can be added later by configuring a protected native API.
No native API is enabled now, avoiding a dependency on an API client staying
connected. No room-temperature sensor or AC acknowledgement is present.

## Scope and limits

- Exact captured 24/25 C frames only; whole-state commands may also restore
  other settings. **The owner reports successful ESPHome changes from 25 C to
  24 C and then back to 25 C** in supervised wall-powered trials. These are
  separate from the earlier Arduino success; repeated reliability is unverified.
- GPIO18, 38 kHz carrier, 33% carrier duty, one frame, no repeats.
- Only explicit button presses call the send script. Extra presses during the
  approximately 118 ms send and following two-second cooldown are dropped.
  The user may press again after the cooldown. No queue, schedules or retries.
- Frame self-check failure blocks both commands. Self-checks operate on arrays;
  they do not emit IR or prove an optical/electrical result.
- Status says **send requested**, not AC confirmed. A driver fault, blocked
  emitter, out-of-range position or power issue can still prevent delivery.
- Physical-remote changes are **not tracked** by this initial configuration.
  The receiver can remain on GPIO19 but is unused by this firmware. Check the AC
  display rather than trusting the web page as its current state.
- Power, fan, mode and wider temperature controls are deliberately absent.

## Private setup

Use Python 3.12 or newer supported by the pinned ESPHome release. From this
repository's root:

```powershell
py -3.12 -m venv work\esphome-tools
.\work\esphome-tools\Scripts\python.exe -m pip install -r firmware\esphome-ac\requirements.txt
.\work\esphome-tools\Scripts\python.exe firmware\esphome-ac\create_secrets.py
.\work\esphome-tools\Scripts\esphome.exe config firmware\esphome-ac\bedroom-ac.yaml
.\work\esphome-tools\Scripts\esphome.exe compile firmware\esphome-ac\bedroom-ac.yaml
```

`create_secrets.py` creates random, distinct setup/control passwords in ignored
`secrets.yaml` and refuses to overwrite an existing file. Keep it private and
back it up locally. Replacing either password requires rebuilding/reflashing.
The home SSID/password are entered directly into the device's setup page;
they do not belong in chat, public YAML or GitHub.

For long Windows paths, use an unused drive alias, e.g. `subst X: <workspace>`
and run from that alias with `ESPHOME_BUILD_PATH=X:\work\esphome-build` and
`ESPHOME_DATA_DIR=X:\work\esphome-data`. Do not reuse an occupied drive.
Remove the alias with `subst X: /D` after tools using it have stopped.
The existing Arduino rollback uses its original PlatformIO toolchain, while this
configuration pins ESPHome 2026.10.0 / ESP-IDF 5.5.6.

In the Microsoft Store Codex process, ESP-IDF initially recorded its cache
through Windows' package-private AppData path while a later export used the
ordinary AppData spelling. The resulting target-record mismatch incorrectly
requested RISC-V/DFU tools. Setting `ESPHOME_ESP_IDF_PREFIX` to the actual cache
directory recorded in that machine's `idf-env.json` fixed tool export without
modifying ESPHome/IDF source or installing unrelated tools. This is a local
environment workaround; do not copy another machine's private absolute path.

## Upload and first phone connection

1. Keep the transmitter's **+5V disconnected** while USB is connected to the PC.
   Verify the current serial port. Build before uploading:
   `esphome upload firmware\esphome-ac\bedroom-ac.yaml --device COM3`.
2. Check serial at 115200 for `FRAME_SELF_TEST=PASS` and absence of boot/RMT
   faults. Do not press a command to make a startup check pass.
3. On your phone, join **Bedroom-AC-Setup** using `setup_password` from your
   local `secrets.yaml`. Stay connected despite the no-Internet notice.
4. Open **http://192.168.4.1/** and enter your home 2.4 GHz Wi-Fi credentials.
   If asked for HTTP login, use **owner** and `control_password`.
5. Rejoin home Wi-Fi and open **http://bedroom-ac.local/**, or the device's
   current IP from the router/serial discovery. Guest/client isolation can block
   access; `.local` availability depends on the phone/network.
6. Login as **owner** with `control_password`. First test the page and cooldown
   with transmitter power still disconnected. A successful HTTP request does
   not establish IR delivery.

The classic ESP32 uses 2.4 GHz Wi-Fi; a 5 GHz-only network will not work. During
a router outage it should retain credentials and retry; a protected fallback
AP becomes available. No IR is tied to either event. Validate this on hardware.

If `bedroom-ac.local` does not open, use the assigned IPv4 address directly,
with an explicit `http://` prefix. The firmware prints `HOME_IP=...` at 115200
baud whenever it joins home Wi-Fi, without printing the SSID or password. This
provides a fallback when mDNS is unavailable; it does not make the DHCP address
permanent. Verify that the phone is on the same home LAN, with guest/client
isolation or a VPN ruled out if the IP also fails. A saved bookmark may need
updating after the router assigns a different address.

## Power and security

The emitter's current and board's USB-to-VIN power path remain unmeasured.
Do not reconnect its power during PC testing. The prior wall-charger trial is
not qualification for unattended installation. Never supply it from 3V3 or a
GPIO, and never join separate 5 V sources together. See the root README for
the supervised experiment and residual power uncertainty.

Web assets are embedded (`local: true`), Digest authentication is explicit,
web logs are off, and normal web OTA is disabled. This is still HTTP, not TLS:
keep it on the trusted local network; do not forward its port to the Internet.
Credentials/configuration and the built binary are not encrypted against
physical flash access. The protected captive portal includes a firmware-upload
facility during setup; anyone with its AP password may have that access.

## Verification

`captured::selfTest()` runs on every device boot and checks allowlisting,
checksums, waveform shape, durations, decoded payloads and a corrupted checksum.
For a host with a C++ compiler, an independent assert-based harness is also
available:

```sh
g++ -std=c++11 tests/frame_test.cpp -o frame-test
./frame-test
```

It is not automatically run by the ESPHome build. Software checks do not
replace the acceptance matrix in [verification.md](verification.md).

The Python evidence/secrets tests need no host C++ compiler. From the repository
root: `python -m unittest discover -s firmware/esphome-ac/tests -p test_evidence.py -v`.

Sources: [web server](https://esphome.io/components/web_server/),
[raw transmitter](https://esphome.io/components/remote_transmitter/),
[captive portal](https://esphome.io/components/captive_portal/).
