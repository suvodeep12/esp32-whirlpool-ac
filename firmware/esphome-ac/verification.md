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
| Wrong password / unauthenticated control rejected | Pending control-endpoint tests |
| Phone browser layout, local assets, explicit buttons | Pending phone test |
| Two-second cooldown, no queued extra press | Pending device test |
| Restart and router outage/recovery, no automatic command | Pending device test |
| ESPHome 24 C optical/AC response | Pending supervised wall-powered trial |
| ESPHome 25 C optical/AC response | Pending supervised wall-powered trial |
| Long-run/thermal/current/power-path suitability | Unverified; no multimeter |

The original Arduino 24 C owner report remains valid for that earlier firmware;
it is not carried forward as a pass for ESPHome.

The owner reported that `bedroom-ac.local` did not open. Windows name lookup and
a 12-second mDNS service discovery also failed. A minimal `wifi.on_connect`
diagnostic now prints the assigned IP over USB. Direct HTTP requests at that
address demonstrated successful Wi-Fi joining and authenticated page serving.
This provides a fallback; it does not prove why mDNS failed on the phone.

One subsequent state-stream connection attempt timed out; a following page
request returned the expected 401, with no serial crash/brownout observed.
Intermittent reachability and long-run behavior remain open checks. The attempted
short-name text-sensor REST paths returned 404 and are not claimed as entity
verification. Phone control and actual AC acknowledgement remain separate gates.
