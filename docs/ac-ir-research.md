# ESP32 local AC control: research and purchase decision

**Latest physical result:** The owner reports that the wall-charger-powered
ESP32 sent the captured 24 C state and the running AC changed from 25 C to
24 C. The next BOOT press did nothing because that firmware deliberately
allows only one send per power-up. This is one successful observed outcome,
not a measured long-term success rate or power-path qualification. Historical
"not transmitted" notes below describe the preceding research/capture phases.

**Current owner constraint: no additional purchases.** Earlier shopping tables
and breakout suggestions are reference research only and are not the active
plan. The new back-of-board photograph does not establish the exact USB-to-VIN
power circuit or its load rating. FlyRobo SKU 4073 specifies USB-C 5 V input,
but its published product page does not provide the VIN output current rating
or a schematic. The high-power transmitter remains disconnected. A borrowed
meter plus power-path/component verification is a possible no-purchase next
step; photos or firmware alone do not establish this electrical capability.

Research date: 24 October 2026 (India). Target supplied by owner: Whirlpool SAI18B31N0D/2021, non-Wi-Fi inverter split AC. Existing board: USB-C CH340 ESP32 development board; parent task has independently identified an ESP32-D0WD-V3 rev 3.1 with 4 MB flash. This report does not claim the AC or any IR hardware has been tested.

## Current owner inventory and immediate decision

Owner already has the ESP32, working USB cable, jumper cables, **FlyRobo KY-022 receiver** and **FlyRobo 3 W 940 nm transmitter**, identified by the owner's order screenshot. The remote has no visible model number. **Buy nothing yet: incremental hardware purchase for the next receiver test is provisionally ₹0**, subject to actual pin-label inspection and having suitable jumper ends.

The [owned KY-022 listing](https://www.flyrobo.in/ky-022-infrared-sensor-module) specifies 3.3–5 V operation and 38 kHz reception. Use its **3.3 V** supply option with ESP32, not the page's Arduino 5 V wiring example. After verifying the actual module's labels, connect VCC/+ to ESP32 3V3, GND/− to GND, and S/OUT to GPIO19. Pin order must come from the actual board; a bare receiver's pin numbering below does not apply to the module header.

The [owned transmitter listing](https://www.flyrobo.in/3w-high-power-940nm-infrared-transmitter-module) specifies an onboard transistor driver, 5 V supply, and 3.3/5 V TTL input. **Do not buy a second discrete driver solely on the assumption that this module lacks one.** After actual-board inspection, its intended signal is GPIO18 to IN and common GND, with a suitable verified 5 V supply. Do not power this 3 W-labelled module from 3V3 or GPIO. Actual current, current limiting, thermal behavior, default-on/off behavior and clone-board USB power-path capacity are unverified. Begin receiver-only; leave the transmitter disconnected until these questions are resolved. The advertised 3 W rating is not a measurement of this board's actual input current.

The replacement baskets and bare-component schematic below are **reference alternatives**, not a recommendation to repurchase owned parts. The latest inventory takes precedence over the earlier shopping assumptions. Location-specific shipping has not been quoted at checkout.

## New physical evidence: 112-bit Whirlpool India candidate

The connected receiver recorded the owner's temperature-up/down presses.
The owner confirmed the remote displayed 25 C then 24 C. One frame was
incomplete (111 candidate data bits); the second contained 112 bits with
MSB-first bytes `EA 32 0A 00 00 24 C4 E0 1C 00 00 00 00 9E` and a valid
checksum. Its prefix, length, timing family and temperature field match the
first-person report in [upstream issue 2204](https://github.com/crankyoldgit/IRremoteESP8266/issues/2204).
The default v2.9.0 decoder reports UNKNOWN. This is a strong protocol candidate
and successful optical reception, but repeated capture fidelity and actual AC
acceptance of an ESP32 transmission are not yet established. Raw captures and
analysis are saved under `../firmware/ir-receiver/captures/` beside this report.

**The generic 168-bit WHIRLPOOL_AC support and its power-toggle semantics below
are background information, not an established description of this newly
captured 112-bit variant.** Do not select the built-in Whirlpool sender solely
from the brand name. Keep actual power state unknown until separately verified.

Follow-up six-press trial: five complete checksum-valid frames, with identical
payloads at each repeated temperature; one incomplete frame rejected. Only the
temperature byte and checksum differed between valid 24/25 C messages. This
supports the candidate format but does not establish reliable remote-state
synchronisation. No ESP32 transmission has occurred. Owner has no multimeter;
phone-charger rating and a safe module power connection remain to be established.

## Transmitter power accessory decision

Owner reports a Motorola 90 W USB-C charger labelled 5 V / 3 A, a USB-C to
USB-C cable and a USB-C/USB-A converter. There is no multimeter and soldering
access is uncertain. The converter's direction/specification is unverified;
the simpler candidate path uses the C-to-C cable directly.

A suitable listed assembled candidate is **one Silicon TechnoLabs S10042 USB-C
breakout**, [product page](https://silicontechnolabs.in/products/usb-c-breakout-board-with-female-usb-c-port),
listed at **Rs 30 including GST**. The product photograph shows fitted right-angle
header pins and two 512-marked resistors, consistent with 5.1 kOhm USB-C sink
resistors. Its FAQ explicitly says the header is pre-soldered. These are seller
claims/photos, not inspection of a delivered part. The page simultaneously
contains Sold out and In stock text; actual stock requires checkout confirmation.
The [shipping policy](https://silicontechnolabs.in/policies/shipping-policy)
states flat Rs 70 India shipping. **Rs 100 is therefore the listed one-item
estimate, not a verified location-specific checkout/delivery quote.** A direct product
availability request encountered the site's connection-verification page.

Intended later topology: PC USB powers ESP32; charger/C-to-C/breakout VBUS powers
only transmitter +5V; breakout/transmitter/ESP32 grounds join; GPIO18 drives IN.
Do not join breakout VBUS to the ESP32 VIN/3V3 while PC USB is connected. No wiring
or transmitter test has been performed. Actual current draw, supply voltage,
thermal behavior and driver input behavior remain unmeasured.

For comparison, [Hubtronics SKU 08177](https://hubtronics.in/usb-c-female-breakout-board)
lists Rs 49 and two 5.1 kOhm CC resistors but exposes solder pads.
[Hubtronics SKU 05166](https://hubtronics.in/usb-type-c-female-connector-breakout-board)
also lists Rs 49; its photo shows a separate loose header, so With Header does
not establish a solder-free assembly. Neither is the present no-solder choice.
Avoid an adjustable PD voltage-trigger module for this simple fixed-5V task.

## General architecture

Keep the existing ESP32. A Raspberry Pi, paid cloud service, MQTT server and always-on PC are unnecessary for a first local controller. Start with remote capture, then prove one controlled transmission, then add a local phone web interface. A receiver and a transistor-driven emitter are the right architecture, but the exact AC protocol remains an acceptance gate. There is no evidence-based basis for calling the current parts or compatibility “10/10”.

Test the existing KY-022 first. If it proves unsuitable, **one Vishay TSOP38238 from DigiKey India** is a documented replacement option with a named manufacturer and datasheet. Shipping may make it poor value for a standalone order. A receiver is optional for a known fixed transmit-only installation, but effectively essential here for compatibility investigation and useful later for observing physical-remote commands. It cannot establish that the AC received a command.

## What the protocol evidence establishes

IRremoteESP8266 v2.9.0 explicitly lists Whirlpool remotes DG11J1-3A, DG11J1-04 and DG11J1-91, alongside SPIS409L/SPIS412L/SPIW409L/SPIW412L/SPIW418L ACs. **SAI18B31N0D/2021 is absent from this list.** Brand matching and an energy-label model number are insufficient to select a protocol. The library has separate DG11J13A and DG11J191 variants, including different temperature ranges. Its header also flags several advanced Whirlpool functions as unsupported, even though APIs exist for some related state fields; do not promise complete remote replacement. [Tagged Whirlpool header](https://raw.githubusercontent.com/crankyoldgit/IRremoteESP8266/v2.9.0/src/ir_Whirlpool.h), [model enum](https://github.com/crankyoldgit/IRremoteESP8266/blob/v2.9.0/src/IRsend.h).

The Whirlpool sender emits a 21-byte, three-section state message at 38 kHz. Crucially, its source describes the carrier choice as a guess and the implementation as beta. The power field is explicitly a **toggle**, and conversion to a common state flips the previous assumed power state. `setPowerToggle(true)` therefore does not mean “definitely turn on”. [Tagged implementation](https://raw.githubusercontent.com/crankyoldgit/IRremoteESP8266/v2.9.0/src/ir_Whirlpool.cpp).

The exact retail model is independently listed by Croma as an IR-remote Whirlpool Nitrocool inverter AC, but that retailer listing does not disclose the wire protocol or remote part number. It corroborates appliance identity only. [Croma product listing](https://www.croma.com/whirlpool-nitrocool-1-5-ton-3-star-inverter-split-ac-copper-condenser-sai18b31n0d-white-/p/233016).

The owner has now confirmed **there is no model number on the remote**. We therefore have no remote-model evidence and should not keep asking for an unavailable identifier. Physical IR captures are the required next compatibility evidence. Clear front/back photos may still help identify layout, but appearance alone is not proof. If captures decode as another protocol, follow the capture evidence instead of forcing Whirlpool.

## Electrical compatibility and safe layout

ESP32 GPIO uses 3.3 V logic. Its documented input range extends only to its supply plus 0.3 V; a 5 V receiver output must not go directly into it. The dev board accepts USB power through its regulator, which does not make its GPIO 5 V tolerant. GPIO18 and GPIO19 are sensible initial transmit/receive choices; verify their labels on the actual board. Avoid boot-strapping pins, flash pins and USB UART pins for this first build. [Espressif module datasheet](https://documentation.espressif.com/esp32-wroom-32_datasheet_en.html).

A genuine TSOP38238 operates at 3.3 V and provides active-low demodulated output. Its pin numbers are 1 OUT, 2 GND, 3 supply; orient it using the manufacturer's drawing, not another module's photograph. Put a 100 nF capacitor close across supply and ground. The current Vishay datasheet lists 38 kHz variants and explains the AGC/noise versus code-compatibility tradeoff. [Vishay receiver datasheet](https://www.vishay.com/docs/82491/tsop382.pdf).

```text
Receiver (TSOP38238, verify physical orientation):
ESP32 3V3 -------- pin 3 VS
ESP32 GND -------- pin 2 GND
ESP32 GPIO19 ----- pin 1 OUT
100 nF ceramic between VS and GND, close to receiver

Transmitter, low-side NPN switch:
verified USB 5 V -- 220 ohm resistor -- IR LED anode (+)
IR LED cathode (-) ------------------- NPN collector
ESP32 GPIO18 ----- 1k ohm ------------ NPN base
NPN base --------- 10k ohm ----------- NPN emitter
NPN emitter -------------------------- common GND
ESP32 GND ---------------------------- common GND
```

This is a conservative initial prototype, not a measured final range design. At 5 V, about 1.3 V LED drop and 0.2 V transistor drop, 220 ohms gives approximately 16 mA while the carrier is on; instantaneous resistor power is about 0.06 W, so a 0.25 W part is adequate. The ESP32 supplies only the roughly 2–3 mA base current. The library creates the 38 kHz carrier: a bare IR LED has no fixed “38 kHz” property. A BC547 is sufficient at this modest current; check the actual device marking and collector/base/emitter pinout. Different 2N2222/PN2222/BC547 packages are not pin-compatible by assumption. [onsemi BC547 family datasheet](https://www.onsemi.com/pdf/datasheet/bc546-d.pdf).

For an identified TSAL6200, 100 ohms would give roughly 35 mA and remain below its 100 mA continuous rating at room temperature. That is an optional range improvement after confirming the delivered emitter and current; do not apply a named part's ratings to an unknown generic LED. Do not use 1 A surge ratings as permission for sustained 38 kHz operation. [Vishay TSAL6200 datasheet](https://www.vishay.com/docs/81010/tsal6200.pdf).

Unplug USB before wiring. Measure the board's proposed 5 V/VIN pin under USB power before using it as a 5 V source; clone board layouts differ. If that rail is not verified, begin with the receiver only. Do not connect independent supplies to the board's 5 V rail and USB together without confirming its power-path circuit. No AC covers, mains wires, relay switching or compressor wiring are involved. Mount the emitter with a clear view of the indoor unit, receiver facing the room, and shield the receiver from direct emitter glare. Move from breadboard to a secured soldered board and enclosure only after testing.

## Purchase links and prices

Prices below are website observations, not an order or a guaranteed checkout quotation. Search snippets and freshly opened product pages disagreed on some Robocraze prices and stock; the table uses the more recent opened page where available. Shipping and PIN-code serviceability were not checked. No merchant's generic component authenticity or batch quality has been independently audited.

### Lowest-cost prototype basket

The ESP32 and working USB data cable are already present and add **₹0 incremental cost**. This basket is an economical experiment; it is not a fully characterized production BOM.

| Item and exact purchase page | Buy quantity | Used in build | Listed merchandise cost |
|---|---:|---:|---:|
| [Robu 38 kHz receiver module, SKU 44258](https://robu.in/product/infrared-receiver-module-arduino/) | 1 | 1 | ₹29 |
| [Robocraze 940 nm IR LED + photodiode pair](https://robocraze.com/products/5mm-ir-transmitter-receiver-pair) | 1 pair | emitter only | ₹14 |
| [BC547, pack of 5](https://robocraze.com/products/bc547-transistor-ic-pack-of-5) | 1 pack | 1 transistor | ₹10 |
| [220 ohm resistors, pack of 10](https://robocraze.com/products/220-ohm-resistor-pack-of-10) | 1 pack | 1 | ₹9 |
| [1k resistors, pack of 10](https://robocraze.com/products/1k-resistor-pack-of-10) | 1 pack | 1 | ₹12 |
| [10k resistors, pack of 10](https://robocraze.com/products/10k-resistor-pack-of-10) | 1 pack | 1 | ₹13 |
| [100 nF / 0.1 uF 50 V ceramic capacitors, pack of 10](https://robocraze.com/products/0-1-uf-50v-ceramic-capacitor) | 1 pack | 1 | ₹17 |
| [170-point mini breadboard](https://robocraze.com/products/mini-breadboard) | 1 | 1 | ₹18 |
| [Male-to-female 20 cm jumpers, 40](https://robocraze.com/products/f2m-jumper-wires-20cm-40pcs) | 1 pack | approximately 5–7 | ₹46 |
| [Male-to-male 20 cm jumpers, 20](https://robocraze.com/products/m2m-jumper-wires-20cm-20pcs) | 1 pack | as needed | ₹29 |
| **Component subtotal including listed GST** | | | **₹197** |

The Robu receiver's indexed listing says 2.7–5.5 V operation and approximately 38 kHz, but an inconsistent seller Q&A and an incomplete fresh page retrieval prevent treating it as an independently verified ESP32 reference design. Power it at 3.3 V, inspect its actual markings and test it. The photodiode in the LED pair is **not** a substitute for this demodulating receiver. The generic emitter listing gives no manufacturer datasheet/current rating; begin conservatively and do not call its range or lifetime verified. [Robu receiver listing](https://robu.in/product/infrared-receiver-module-arduino/), [LED pair listing](https://robocraze.com/products/5mm-ir-transmitter-receiver-pair).

The 170-point board holds only the peripheral circuit. Keep the ESP32 beside it and connect with female-to-male wires; do not try to fit a wide 30-pin ESP32 board on it. If more workspace is wanted, [FlyRobo's 400-point board](https://www.flyrobo.in/solderless-breadboard-400-point/) is listed in stock at ₹37, but an extra shop's shipping may erase the saving. No additional breadboard power module is needed.

### Better component traceability

| Item | Seller / observed price | Why consider it |
|---|---|---|
| [Vishay TSOP38238, recommended receiver](https://www.digikey.in/en/products/detail/vishay-semiconductor-opto-division/TSOP38238/1681362) | DigiKey India, ₹80.26 for one, stock listed; MOQ 1 | Named manufacturer, datasheet, documented logic-level operation; listing is stronger provenance evidence, not a test of delivered hardware |
| [Vishay TSAL6200 emitter](https://www.digikey.in/en/products/detail/vishay-semiconductor-opto-division/TSAL6200/1681339) | DigiKey India, ₹47.78 for one, stock listed | Known wavelength, optical pattern and current ratings |
| [TSOP38238](https://silicontechnolabs.in/products/tsop38238-ir-receiver-module-38khz-through-hole) | Silicon TechnoLabs, ₹45 incl GST | Local named-part listing, but page simultaneously says “Sold out” and “In stock”; confirm availability before relying on it |
| [TSOP38238](https://roboticsdna.in/product/ir-receiver-diode-tsop38238/) | RoboticsDNA, ₹35.40 incl GST | Explicitly out of stock; not a current purchase recommendation |
| [TSAL6200](https://www.mouser.in/en/ProductDetail/Vishay-Semiconductors/TSAL6200?qs=sGAEpiMZZMv0DJfhVcWlK63IlmfJGuLDZDVM91mQt2g%3D) | Mouser India, ₹46.59 for one, stock listed | Named-source alternative; delivery/import cost matters |

Replacing the budget receiver and emitter with the two DigiKey parts gives **₹154 + ₹128.04 = ₹282.04 at displayed price bases**. The DigiKey tax basis differs from the GST-inclusive hobby-store amounts; if 18% GST is added to its two parts, the merchandise estimate becomes **₹305.09**, before shipping or other checkout fees. This is an estimate with an explicit tax assumption, not a delivered total. An exact total requires the delivery PIN code and final checkout. Do not open multiple tiny orders merely to save a few rupees on parts. Local pickup or combining these with an existing component order may produce the actual best ROI.

### Modules previously considered

The [Horizocart IR transmitter](https://www.horizocart.com/products/ir-transmitter-module/2392387000000229191) is ₹59 and claims 3.3–5 V/ESP32 compatibility. The page does not provide a transistor schematic, input threshold, LED current or measured range. That is insufficient to call it a verified transistor-driven, room-reliable emitter. Ask for its schematic or inspect the delivered PCB first. A [FlyRobo 3 W 940 nm module](https://www.flyrobo.in/3w-high-power-940nm-infrared-transmitter-module) is ₹349, listed in stock, and explicitly claims onboard transistor drive, 5 V supply and 3.3 V TTL input. This is better specified but still seller evidence; its actual current, thermal behavior and default input state need testing. It is not the first max-ROI purchase for a single nearby AC.

Robocraze and Robu provide business/contact/return infrastructure, but that does not prove every generic part's provenance. DigiKey/Mouser named parts provide a stronger traceability route at potentially disproportionate shipping cost. Reliability should be bought with appropriate specifications and tested installation, not a retailer's “high power” wording.

### Standalone USB power

Reuse a reputable regulated 5 V USB wall adapter rated at least 1 A if one is already available; 2 A provides comfortable margin. Do not buy another unless needed. [Compoden 5 V 2 A USB-A adapter](https://compoden.com/products/5v-2a-usb-a-power-adapter-wall-brick-without-cable) lists ₹179 incl GST plus ₹75 prepaid shipping below ₹999: **₹254 delivered under its stated standard policy**, with delivery serviceability still unchecked. Adding it gives the budget basket **₹376 merchandise** or **₹451 including only that shop's stated ₹75 shipping**, plus Robu/Robocraze shipping. Its listing is not an independent electrical/safety test; a known existing branded adapter is preferable to buying an unverified cheap one. Do not count power-bank operation as reliable without checking low-load auto-shutoff.

## Implementation route and acceptance gates

1. **USB hardware diagnostic.** Complete the parent's chip/flash identification, original-flash backup, compilation/upload and serial-output check. This verifies programming and basic operation, not IR or radio reliability.
2. **Receive first.** Install a pinned IRremoteESP8266 version and begin from upstream [IRrecvDumpV3](https://github.com/crankyoldgit/IRremoteESP8266/blob/v2.9.0/examples/IRrecvDumpV3/IRrecvDumpV3.ino). Use GPIO19, a 1024-entry capture buffer, 50 ms timeout for long AC frames, and 115200 serial. Check overflow status. Record raw timings, decoded protocol, byte count, state and checksums for power, temperature, mode, fan and swing. Capture each relevant action several times; preserve clock/timer-dependent differences. Do not reduce an AC message to a TV-style 32-bit code.
3. **Select implementation from captures.** If Whirlpool is decoded consistently, compare model variants and decoded state with the physical remote, then use `IRWhirlpoolAc`. If unknown, retain full raw timings and characterize the protocol before adding schedules. A 38 kHz demodulating receiver removes the carrier and cannot measure the original carrier frequency precisely; persistent failures may require a photodiode/oscilloscope or appropriate measurement tool rather than repeated software guesses.
4. **Single supervised transmit.** Wire GPIO18 driver, initialize output LOW before use, and send only on an explicit user command. First replay a non-power action while the AC is visibly on. Keep power-toggle bit false in ordinary settings packets. Do not blindly repeat complete power commands: a second accepted toggle may undo the first. A receiver seeing our transmission proves optical output, not AC acceptance.
5. **Physical-remote coexistence.** Decode verified remote messages to update an *estimated* state. Start power as UNKNOWN after ESP32 reboot or known AC power loss; saving the last state does not establish present reality. Missed IR, remote use outside receiver view, delayed packets, AC timers and AC mains interruptions can all desynchronize it. Mark uncertainty honestly and require manual confirmation before state-dependent power automation. Clear/suppress self-reception around transmit and deduplicate only measured repeats without suppressing deliberate consecutive presses.
6. **Local phone control.** After IR works, serve a small local web interface directly on the ESP32 over the home Wi-Fi, with a DHCP reservation. The ESP32 runs the logic without the PC. Expose no Internet port, use no cloud dependency, and keep credentials out of committed source. A SoftAP can provide isolated setup/control, but joining the existing LAN is more convenient. No broker is required.
7. **Reliability gate.** At the final position, test normal commands repeatedly under daylight/night lighting, different remote angles, remote use during control, Wi-Fi reconnect, ESP32 restart and AC mains interruption. Document attempts, successes and any uncertain state; do not extrapolate a short test to perfect reliability. On restart, network reconnect or failed command, do not automatically send a power toggle. Avoid rapid compressor cycling and follow the exact AC manual's restart guidance; do not invent a universal model-specific delay.
8. **Future additions.** Add a suitable room-temperature/humidity sensor, then occupancy sensing only if a concrete automation needs it. PIR alone cannot reliably establish that a sleeping person is absent. Keep IR transport/state logic independent of the phone UI so later MQTT/Home Assistant integration can reuse it; do not install that infrastructure now. If verified absolute AC power feedback becomes necessary, investigate a non-invasive indicator sensor or appropriately installed rated metering rather than an improvised mains circuit.

IRremoteESP8266 **v2.9.0 explicitly adds ESP32 Arduino Core 3 support**; old v2.8.6 timer compilation failures do not establish a current incompatibility. Pin and compile the chosen toolchain/library pair. A stable Arduino 2.0.17 baseline remains a conservative option, but is not the only theoretically compatible route. No source-only check proves the user's actual IR timing under Wi-Fi load. [Release notes](https://raw.githubusercontent.com/crankyoldgit/IRremoteESP8266/master/ReleaseNotes.md), [v2.9.0 ESP32 receiver implementation](https://raw.githubusercontent.com/crankyoldgit/IRremoteESP8266/v2.9.0/src/IRrecv.cpp).

## Remaining unknowns

- Remote is unmarked; decoded protocol, exact carrier, and whether this Indian Whirlpool model uses the library's documented toggle semantics remain unknown.
- Whether the AC accepts every basic or advanced command and which functions need captured raw frames.
- Final distance/angle, ambient IR noise, actual purchased component markings, emitter current/range and board 5 V pin routing.
- Existing USB wall-adapter suitability; shipping PIN code and actual multi-store checkout totals.
- Long-term runtime stability, physical-remote capture coverage and any independent feedback of actual AC power.

No purchases, IR wiring, AC commands or mains changes were performed for this report. Research establishes a defensible test plan; it does not establish perfect hardware compatibility.
