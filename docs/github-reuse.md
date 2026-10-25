# Reuse assessment: GitHub, ESPHome and Home Assistant

Assessed 25 October 2026. The owner selected ESPHome's standard interface after
this comparison. This is a software/source assessment; it is not electrical
qualification or proof of complete compatibility with SAI18B31N0D/2021.

## Decision

Use **ESPHome on the existing ESP32 now**, with two buttons that transmit the
captured 24/25 C frames. Keep **Home Assistant optional for later bedroom
automation**. This avoids building our own browser UI, provisioning portal and
device web server while retaining the working Arduino experiments as rollback.

Home Assistant is a separate automation server, installed on hardware such as
an existing computer, a VM or a dedicated hub. The server must be running when
its dashboards/automations are used. It is not firmware for an ESP32, and the
phone app is not a substitute for that server. No additional host is needed for
our proposed standalone ESPHome web controls.
[Home Assistant installation](https://www.home-assistant.io/installation/),
[ESPHome web server](https://esphome.io/components/web_server/).

| Candidate | Useful part | Decision / limitation |
|---|---|---|
| [ESPHome](https://github.com/esphome/esphome/tree/2026.10.0) | Standard device web controls, provisioning, ESP32 RMT transmission | Selected for validation; use captured raw frames |
| [Home Assistant](https://www.home-assistant.io/) | Shared dashboards and automations across bedroom devices | Later, when an always-running host is wanted |
| [IRremoteESP8266](https://github.com/crankyoldgit/IRremoteESP8266) | Existing working capture/send tools | Keep; its built-in Whirlpool protocol differs from ours |
| [0xPiyush/irtxrx](https://github.com/0xPiyush/irtxrx/tree/b23013a75c0e9eec9150ebd08b2d388f7d1d3337) | Separate Whirlpool Magicool 112-bit encoder/decoder | Excellent protocol reference; TypeScript, not ESP32 firmware |
| [WiFiManager](https://github.com/tzapu/WiFiManager/tree/v2.0.17) | Phone provisioning for an Arduino controller | Good fallback if ESPHome fails validation; separate [source assessment](github-wifi-reuse.md) |
| [IRMQTTServer](https://github.com/crankyoldgit/IRremoteESP8266/tree/master/examples/IRMQTTServer) | Complete generic IR web/MQTT example | Larger than needed; MQTT can be disabled, but its climate protocol still needs adapting |
| [dockdv/esp32-ir-control](https://github.com/dockdv/esp32-ir-control) | Small local web remote | NEC-specific, open setup AP and GET-based sends; requires changes |
| [Alexeyisme/ACWebRemote](https://github.com/Alexeyisme/ACWebRemote) | Multi-brand ESP32 remote | Whirlpool maps to IRac WHIRLPOOL_AC; branding alone does not establish our 112-bit compatibility |

The IRMQTTServer documentation describes optional MQTT, startup climate-state
restoration and default HTTP security limits. Those defaults need auditing before
reuse. [Upstream example](https://github.com/crankyoldgit/IRremoteESP8266/blob/1e2f0f3ef0a93cbf2a8ddb2e95130f8f4c584b3f/examples/IRMQTTServer/IRMQTTServer.ino).
The NEC project's own README documents its protocol and setup behavior.
[Source README](https://github.com/dockdv/esp32-ir-control/blob/main/README.md).

## New protocol evidence

The peer library's 112-bit Magicool format has a `57 4C 50` ("WLP") LSB-first
signature, `31 - temperature` byte and modulo-256 sum. Reversing each byte of
our MSB-first captures gives that representation. The peer's default trailing
state bytes differ; setting its `remoteState` to zero reproduces ours.
[Pinned implementation](https://github.com/0xPiyush/irtxrx/blob/b23013a75c0e9eec9150ebd08b2d388f7d1d3337/src/protocols/whirlpool_magicool.ts).

Local experiment with Bun 1.3.14, without installing packages or running install
hooks:

- Upstream Magicool suite: **25 passed, 0 failed; 1,748 assertions**.
- All five complete local repeat captures: peer encoder produced **identical
  bytes**, including checksum, for their 24/25 C values.
- Peer decoder accepted ideal waveforms generated using our existing send timings.
- Peer decoder accepted **0/5 measured complete receiver captures** unchanged.
- It also rejected the incomplete capture. No missing bits were repaired.

The measured zero spaces frequently fall below the peer decoder's timing window.
This supports investigating receiver timing/tolerance, not calling that decoder
drop-in compatible or widening tolerance blindly. No frames were transmitted in
this experiment. See [reproduction script](../tools/check-peer-magicool.ts).

The repository's package metadata declares MIT, but no top-level LICENSE was
present in the inspected tree. We have not copied its implementation into the
firmware. Broad power/fan/mode claims remain peer observations until tested on our
unit. [Package metadata](https://github.com/0xPiyush/irtxrx/blob/b23013a75c0e9eec9150ebd08b2d388f7d1d3337/package.json).

## ESPHome compatibility boundary

The built-in `whirlpool` climate component still uses a 21-byte state and DG11J1
models. It is **not** selected. Use `remote_transmitter.transmit_raw` for the
captured 14-byte commands instead.
[Pinned Whirlpool source](https://github.com/esphome/esphome/blob/2026.10.0/esphome/components/whirlpool/whirlpool.cpp),
[raw transmitter documentation](https://esphome.io/components/remote_transmitter/).

ESPHome's web server supports embedded local assets and explicitly selected
Digest authentication. Local assets avoid needing a CDN at runtime. A protected
fallback AP supplies home credentials through the captive portal. Its captive
portal also exposes a firmware-update facility during setup, even when normal
web OTA is disabled; keep the setup password private.
[Web server](https://esphome.io/components/web_server/),
[captive portal](https://esphome.io/components/captive_portal/).

Acceptance still needs a successful build, on-device frame self-checks, phone
provisioning, web authentication, cooldown behavior, restart/reconnect checks,
and supervised optical/AC trials. The old 24 C owner report does not validate a
new RMT firmware implementation. No software choice resolves the unmeasured
transmitter current or USB-to-VIN power path.
