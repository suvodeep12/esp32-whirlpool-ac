# ESPHome acceptance record

25 October 2026. Pending rows are not passes. Transmitter +5V must remain
disconnected during PC-powered testing.

| Check | Result |
|---|---|
| ESPHome 2026.10.0 configuration schema | Passed |
| ESP-IDF 5.5.6 firmware build | Passed; latest app 834,976 bytes; 45.5% of app partition used |
| USB upload | Passed on COM3 at 115200 baud; written-data hash verified |
| Python fixture/secrets tests | 2 passed; exact 24/25 C bytes match recorded valid captures; existing keys preserved |
| Native C++ assert harness | Not run; no host C++ compiler found |
| On-device frame self-checks | PASS after reset; observed over USB |
| Startup without a command | Source has no startup send; 32-second reset observation showed no crash/brownout/RMT fault. GPIO/optical signal was not instrumented |
| Home Wi-Fi provisioning | Owner completed setup; assigned home IPv4 observed over USB after update/reset without re-entering credentials |
| Setup AP password rejection | Pending negative phone test |
| Unauthenticated web page | HTTP 401 with Digest challenge, verified from PC |
| Authenticated web page | HTTP 200, 77,862-byte embedded page, verified from PC |
| Wrong password / unauthenticated control | Both actual button POST requests returned HTTP 401 in an emitter-unpowered trial |
| Phone browser access | Owner reports controls open at the direct IP; detailed layout and Internet-disconnected phone checks remain pending |
| Software state over authenticated REST | Frame checks PASS, initial last transmission None since restart, actual AC state Unknown |
| Two-second cooldown, no queued extra press | Unpowered trial: 24 C followed immediately by 25 C (0.141 seconds total) left status at 24 C; a 25 C press after 2.2 seconds changed status to 25 C |
| Restart and router outage/recovery, no automatic command | Pending device test |
| ESPHome 24 C AC response | Owner reports AC changed from 25 C to 24 C after pressing the phone button in the supervised wall-powered trial; optical waveform not measured |
| ESPHome 25 C AC response | Owner reports AC changed from 24 C to 25 C after pressing the phone button in the supervised wall-powered trial; optical waveform not measured |
| Repeating an already-current temperature | Owner reports one additional 25 C press left the AC at 25 C and on. This bounded observation does not establish all power-state semantics or all repeated commands |
| Long-run/thermal/current/power-path suitability | Unverified; no multimeter |

The ESPHome 24 C and 25 C results are new owner-reported observations, separate
from the earlier Arduino 24 C report. They do not establish a long-run success
rate, complete protocol compatibility or electrical/thermal qualification.

The owner reported that `bedroom-ac.local` did not open. Windows name lookup and
a 12-second mDNS service discovery also failed. A minimal `wifi.on_connect`
diagnostic now prints the assigned IP over USB. Direct HTTP requests at that
address demonstrated successful Wi-Fi joining and authenticated page serving.
This provides a fallback; it does not prove why mDNS failed on the phone.

One subsequent state-stream connection attempt timed out; a following page
request returned the expected 401, with no serial crash/brownout observed.
Intermittent reachability and long-run behavior remain open checks. The attempted
short-name text-sensor REST paths returned 404. Source inspection showed this
version matches literal entity names, so URL-encoded full names subsequently
returned HTTP 200 with the expected states. This required no firmware change.

The owner subsequently confirmed the phone control page opens. An authenticated,
emitter-unpowered button trial verified software cooldown and repeated manual
commands. The actual-state entity remained Unknown; the last-command text only
reported a send request. No GPIO waveform, optical output or AC response was
measured in this trial. The transmitter +5V remained disconnected throughout.
