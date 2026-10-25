# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

ESPHome 2026.10.0 with its standard local web interface is the selected phone
controller. Earlier Arduino/IRremoteESP8266 projects remain as capture evidence
and rollback firmware. No cloud server or always-on PC is required for control.

## Users and purpose

The owner wants reliable, low-cost local control of a non-Wi-Fi Whirlpool
SAI18B31N0D/2021 AC from a phone browser on the existing home Wi-Fi.
Longer-term bedroom automation is a future goal, not this implementation.

## Confirmed constraints

- No additional hardware purchases and no multimeter.
- Existing ESP32, KY-022 receiver, transistor-driven 940 nm emitter and USB charger.
- Physical remote captures and checksums support 24 C and 25 C state frames.
- The owner reports one successful 25 C to 24 C AC response.
- No automatic sends on boot, reconnect, page load or retry.
- Actual AC state is not queryable; command delivery must not be presented as acknowledgement.
- Home network credentials and device access secrets must stay outside chat, logs and GitHub.
- Transmitter power remains disconnected during PC-powered software testing.
- The owner selected ESPHome's built-in interface after the GitHub/Home Assistant comparison.

## Current implementation decisions

Use ESPHome phone-based Wi-Fi provisioning and device-local credentials. Initially
allow only captured 24/25 C commands; additional temperatures require capture
evidence. The browser can select a value and explicitly send it repeatedly,
with a cooldown and no hidden resend. Power, mode and fan controls are outside
the present verified scope. These decisions preserve existing evidence gates.

## Evidence

Raw captures and bounded test records live under firmware/ir-receiver and
firmware/ir-transmit-test. Public docs distinguish owner reports, software
checks, unmeasured electrical limits and outstanding physical tests.

## Busy-session assumptions

The user returned and selected the standard ESPHome interface. Its existing
visual system is inherited; no new visual identity or bespoke page is required.
Home Assistant remains an optional later host, not an initial prerequisite.
