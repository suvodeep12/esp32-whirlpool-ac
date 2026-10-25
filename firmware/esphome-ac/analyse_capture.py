"""Analyse native ESPHome raw logs; candidates never automatically enable controls."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

BASELINE = bytes.fromhex("ea 32 0a 00 00 24 c4 e0 1c 00 00 00 00 9e")
REQUESTED = range(20, 27)
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
RAW_TAG = re.compile(r"\[remote\.raw:\d+\]: (.*)")
NUMBERS = re.compile(r"[+-]?\d{1,7}(?:\s*,\s*[+-]?\d{1,7})*\s*,?\s*")
OVERFLOW = re.compile(r"\[(?:remote_receiver|logger|uart)(?:\.[\w.]+)?(?::\d+)?\]:[^\n]*\boverflow\b", re.IGNORECASE)


def reverse_byte(value):
    return int(f"{value:08b}"[::-1], 2)


def analyse_frame(pulses):
    result = {"raw_entries": len(pulses), "candidate_valid": False}
    if len(pulses) != 227:
        return result | {"reason": "wrong_length"}
    if not (2500 <= pulses[0] <= 4250 and -1750 <= pulses[1] <= -1000):
        return result | {"reason": "wrong_header"}
    if not 400 <= pulses[-1] <= 850:
        return result | {"reason": "bad_footer"}
    state = bytearray(14)
    for bit in range(112):
        mark, space = pulses[2 + 2 * bit:4 + 2 * bit]
        if not 400 <= mark <= 850:
            return result | {"reason": "bad_mark"}
        if -450 <= space <= -80:
            value = 0
        elif -1300 <= space <= -800:
            value = 1
        else:
            return result | {"reason": "ambiguous_or_bad_space"}
        state[bit // 8] = (state[bit // 8] << 1) | value
    if state[:3] != BASELINE[:3]:
        return result | {"reason": "wrong_signature"}
    if reverse_byte(state[13]) != sum(map(reverse_byte, state[:13])) % 256:
        return result | {"reason": "bad_checksum"}
    temperature = 31 - reverse_byte(state[7])
    result.update(msb_bytes=state.hex(" "), temperature_candidate=temperature)
    if temperature not in REQUESTED:
        return result | {"reason": "outside_requested_range"}
    if any(state[i] != BASELINE[i] for i in range(13) if i != 7):
        return result | {"reason": "other_settings_differ"}
    return result | {"candidate_valid": True, "reason": "candidate_only",
                     "raw_signed_us": pulses}


def analyse_log(text):
    text = ANSI.sub("", text)
    overflow = bool(OVERFLOW.search(text))
    frames, current, malformed = [], None, False

    def finish():
        if current is None:
            return
        frame = analyse_frame(current)
        if malformed:
            frame.update(candidate_valid=False, reason="malformed_or_oversized_log")
        if overflow:
            frame.update(candidate_valid=False, reason="session_overflow")
        frame["capture"] = len(frames) + 1
        frames.append(frame)

    for line in text.splitlines():
        match = RAW_TAG.search(line)
        if not match:
            continue
        message = match[1].strip()
        if message.startswith("Received Raw:"):
            finish()
            current, malformed = [], False
            message = message[len("Received Raw:"):].strip()
        if current is None:
            continue
        if not NUMBERS.fullmatch(message):
            malformed = True
            continue
        values = [int(value.strip()) for value in message.rstrip(", ").split(",")]
        if len(current) + len(values) > 512:
            malformed = True
            continue
        current.extend(values)
    finish()
    counts = Counter(frame["temperature_candidate"] for frame in frames if frame["candidate_valid"])
    return {"requested_range": [20, 26], "overflow_seen": overflow,
            "manual_confirmation_required": True,
            "range_capture_complete": all(counts[temp] >= 2 for temp in REQUESTED),
            "repeat_counts": {str(temp): counts[temp] for temp in REQUESTED},
            "missing_candidate_repeats": [temp for temp in REQUESTED if counts[temp] < 2],
            "captures": frames}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.log.stat().st_size > 4 * 1024 * 1024:
        parser.error("Capture log exceeds the 4 MiB analysis limit; use a shorter session")
    report = analyse_log(args.log.read_text(encoding="utf-8", errors="replace"))
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as output:
            output.write(encoded)
    else:
        print(encoded, end="")
    return 2 if report["overflow_seen"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
