# ESPHome acceptance record

25 October 2026. Pending rows are not passes. Transmitter +5V must remain
disconnected during PC-powered testing.

| Check | Result |
|---|---|
| ESPHome 2026.10.0 configuration schema | Passed |
| ESP-IDF 5.5.6 firmware build | Passed; app 834,736 bytes; 45.5% of app partition used |
| USB upload | Passed on COM3 at 115200 baud; written-data hash verified |
| Python fixture/secrets tests | 2 passed; exact 24/25 C bytes match recorded valid captures; existing keys preserved |
| Native C++ assert harness | Not run; no host C++ compiler found |
| On-device frame self-checks | PASS after reset; observed over USB |
| Startup without a command | Source has no startup send; 32-second reset observation showed no crash/brownout/RMT fault. GPIO/optical signal was not instrumented |
| Protected setup AP and home Wi-Fi provisioning | Pending phone test |
| Wrong web password / unauthenticated control rejected | Pending device test |
| Phone browser layout, local assets, explicit buttons | Pending phone test |
| Two-second cooldown, no queued extra press | Pending device test |
| Restart and router outage/recovery, no automatic command | Pending device test |
| ESPHome 24 C optical/AC response | Pending supervised wall-powered trial |
| ESPHome 25 C optical/AC response | Pending supervised wall-powered trial |
| Long-run/thermal/current/power-path suitability | Unverified; no multimeter |

The original Arduino 24 C owner report remains valid for that earlier firmware;
it is not carried forward as a pass for ESPHome.
