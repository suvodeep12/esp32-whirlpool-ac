# GitHub reuse: WiFiManager provisioning

Assessed 25 October 2026. Target: the existing ESP32, Arduino core 2.0.17, PlatformIO 6.12. This is a source assessment, not a tested installation or a security certification.

**Recommendation: reuse `tzapu/WiFiManager` v2.0.17 for temporary phone-based Wi-Fi provisioning, then run a separate authenticated AC-control page.** It covers captive DNS, scanning, credential entry and saved-network reconnection. It is not an AC protocol library or a complete secured appliance controller. Its metadata declares ESP32 support; compilation against this project's pinned core remains the compatibility check. [Pinned library metadata](https://github.com/tzapu/WiFiManager/blob/v2.0.17/library.properties), [pinned README](https://github.com/tzapu/WiFiManager/blob/v2.0.17/README.md).

## Small integration seam

Pin the dependency, rather than taking the moving default branch:

```ini
lib_deps =
  tzapu/WiFiManager@2.0.17
build_flags =
  -DWM_NODEBUG
  -DCORE_DEBUG_LEVEL=0
```

Keep the `WiFiManager` object global if using its nonblocking portal. Before the initial `autoConnect`, configure:

```cpp
wm.setDebugOutput(false);
wm.setConfigPortalBlocking(false);
wm.setConnectTimeout(15);       // seconds
wm.setSaveConnectTimeout(15);
wm.setConfigPortalTimeout(180);
wm.setAPClientCheck(false);
wm.setWebPortalClientCheck(false);
wm.setShowPassword(false);
wm.setDisableConfigPortal(true);
wm.setBreakAfterConfig(false);
```

Start with `WiFi.mode(WIFI_STA)`, initialize/load a unique device setup password, and call `wm.autoConnect(apName.c_str(), apKey.c_str())`. Supply a random 32-character hex key, never an empty argument or the example's shared password. The API accepts a protected AP password of 8–63 characters. Repeatedly call `wm.process()` in `loop`, and inspect `WiFi.status()` plus `wm.getConfigPortalActive()`; a false initial result in this mode can mean the portal is running, not that setup permanently failed. [Pinned API header](https://github.com/tzapu/WiFiManager/blob/v2.0.17/WiFiManager.h), [upstream nonblocking example](https://github.com/tzapu/WiFiManager/blob/v2.0.17/examples/NonBlocking/AutoConnectNonBlocking/AutoConnectNonBlocking.ino).

Application-owned device setup/admin secrets can remain in Preferences. Let WiFiManager own the normal SDK Wi-Fi credential storage; do not add a competing saved-network record or assume `WiFi.persistent(false)` overrides all library saving. Device secrets need a deliberate private USB retrieval/setup path and must stay out of ordinary logs and Git. Generate fresh keys after Wi-Fi RF is enabled: [Espressif RNG requirements](https://docs.espressif.com/projects/esp-idf/en/v4.4.7/esp32/api-reference/system/random.html).

When provisioning ends, ensure its portal/server is stopped, explicitly select STA-only mode, verify the AP mode bit is absent, and then start the AC-control server. Stop that controller before reopening provisioning; both otherwise compete for port 80. Later router loss needs a small application recovery policy with a retry interval and bounded fallback setup. Neither initial `autoConnect` nor the example supplies a complete lifetime policy. Keep **every** IR action out of Wi-Fi callbacks and state transitions: only the already-authorized 24 C/25 C POST handlers should transmit.

## Limits found in the pinned implementation

- HTTP authentication in `handleRequest` is disabled test code. Portal routes include restart, erase and OTA; hiding menu entries does not remove them. Use the portal temporarily on a password-protected setup AP, not as a persistent home-LAN management server.
- Debug levels can expose submitted credentials. Suppress both library and ESP32 framework logging before entering passwords.
- “Nonblocking” describes the outer portal loop. Connection attempts still wait and shutdown includes a one-second delay. Bound both join timeouts; do not claim strict loop-latency guarantees.
- The implementation's `process()` checks portal timeouts despite a stale contrary header comment. Verify actual expiry and shutdown on hardware.
- New credentials are passed to persistent Wi-Fi configuration before the join result. It does not provide an application-level “retain the old known-good credentials until candidate success” transaction.

These findings come from `setupHTTPServer`, `handleRequest`, `process`, `connectWifi`, `wifiConnectNew`, and `shutdownConfigPortal` in the [pinned implementation](https://github.com/tzapu/WiFiManager/blob/v2.0.17/WiFiManager.cpp). They favor a small integration around upstream provisioning, not copying an entire unrelated automation project or treating upstream defaults as hardened.

## License and acceptance gate

The library uses the MIT license. Retain its copyright and permission notice when redistributing substantial library code. The license does not imply a warranty. [Pinned license](https://github.com/tzapu/WiFiManager/blob/v2.0.17/LICENSE).

Before calling provisioning complete: compile the pinned combination, then physically test a fresh setup, wrong password, router outage/rejoin, portal expiry, AP disappearance after success, full-phone-browser behavior and absence of IR at boot/reconnect. The phone may need to stay connected to the setup network despite its lack of Internet. No IR command is inherently added by this Wi-Fi-only library; application callbacks remain the relevant risk.

No installation, firmware change, Wi-Fi-secret retrieval or device test was performed for this note.
