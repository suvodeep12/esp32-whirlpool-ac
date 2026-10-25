import importlib.util
import contextlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("analyse_capture", PROJECT / "analyse_capture.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def raw_frames(filename):
    text = (PROJECT.parent / "ir-receiver/captures" / filename).read_text()
    return [[int(x.strip()) * (1 if i % 2 == 0 else -1)
             for i, x in enumerate(match.split(","))]
            for match in re.findall(r"rawData\[\d+\] = \{([^}]+)\}", text)]


def log_frame(pulses):
    chunks = []
    for index in range(0, len(pulses), 31):
        prefix = "Received Raw: " if index == 0 else "  "
        chunks.append("\x1b[0;32m[I][remote.raw:015]: " + prefix +
                      ", ".join(map(str, pulses[index:index + 31])) +
                      ("," if index + 31 < len(pulses) else "") + "\x1b[0m")
    return "\n".join(chunks)


def synthetic_frame(temperature, change_settings=False):
    # Synthetic cases exercise the parser, not physical AC compatibility.
    state = bytearray.fromhex("57 4c 50 00 00 24 23 07 38 00 00 00 00 79")
    state[7] = 31 - temperature
    if change_settings:
        state[8] = 0
    state[13] = sum(state[:13]) % 256
    pulses = [3370, -1365]
    for byte in state:
        for bit in range(8):
            pulses.extend([580, -1003 if byte & (1 << bit) else -250])
    return pulses + [600]


class CaptureAnalysisTests(unittest.TestCase):
    def test_all_real_recorded_frames_keep_their_original_verdicts(self):
        for stem in ("initial", "repeat"):
            expected = json.loads((PROJECT.parent / "ir-receiver/captures" / (stem + "-analysis.json")).read_text())
            frames = raw_frames(stem + ".txt")
            self.assertEqual(len(frames), len(expected))
            for frame, old in zip(frames, expected):
                with self.subTest(stem=stem, capture=old["capture"]):
                    got = analysis.analyse_frame(frame)
                    self.assertEqual(got["candidate_valid"], old["checksum_valid"])
                    if old["checksum_valid"]:
                        self.assertEqual(got["msb_bytes"], old["msb_bytes"])

    def test_wrapped_ansi_logs_ignore_other_tags_and_do_not_export_their_text(self):
        frame = raw_frames("repeat.txt")[1]
        log = log_frame(frame) + "\n[W][wifi:012]: DO_NOT_EXPORT_THIS_WIFI\n" + log_frame(frame)
        result = analysis.analyse_log(log)
        self.assertEqual(len(result["captures"]), 2)
        self.assertEqual(result["repeat_counts"]["24"], 2)
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(result))
        self.assertTrue(result["manual_confirmation_required"])

    def test_truncation_bad_sign_bad_timing_and_checksum_are_rejected(self):
        frame = raw_frames("repeat.txt")[1]
        cases = [frame[:-2], frame + [-10000], [0] + frame[1:]]
        wrong_sign = frame.copy(); wrong_sign[1] *= -1; cases.append(wrong_sign)
        ambiguous = frame.copy(); ambiguous[3] = -650; cases.append(ambiguous)
        corrupt = frame.copy(); corrupt[3] = -250 if frame[3] < -700 else -1003; cases.append(corrupt)
        for case in cases:
            self.assertFalse(analysis.analyse_frame(case)["candidate_valid"])

    def test_overflow_poisoning_blocks_an_otherwise_valid_session(self):
        for tag in ("remote_receiver", "logger", "uart.esp32"):
            log = log_frame(raw_frames("repeat.txt")[1]) + f"\n[W][{tag}:104]: Buffer overflow\n"
            result = analysis.analyse_log(log)
            self.assertTrue(result["overflow_seen"])
            self.assertFalse(result["range_capture_complete"])
            self.assertEqual(result["repeat_counts"]["24"], 0)

    def test_malformed_or_oversized_chunk_is_not_partially_accepted(self):
        log = log_frame(raw_frames("repeat.txt")[1])
        for extra in ("not-a-pulse", "9" * 5000, ", ".join(["580"] * 600)):
            got = analysis.analyse_log(log + "\n[I][remote.raw:015]:   " + extra)
            self.assertFalse(got["captures"][0]["candidate_valid"])

    def test_existing_24_25_data_does_not_complete_20_26(self):
        got = analysis.analyse_log("\n".join(log_frame(frame) for frame in raw_frames("repeat.txt")))
        self.assertFalse(got["range_capture_complete"])
        self.assertEqual(got["missing_candidate_repeats"], [20, 21, 22, 23, 26])

    def test_synthetic_range_needs_two_repeats_and_still_requires_manual_confirmation(self):
        logs = [log_frame(synthetic_frame(temp)) for temp in range(20, 27)]
        once = analysis.analyse_log("\n".join(logs))
        self.assertFalse(once["range_capture_complete"])
        twice = analysis.analyse_log("\n".join(logs + logs))
        self.assertTrue(twice["range_capture_complete"])
        self.assertTrue(twice["manual_confirmation_required"])
        self.assertEqual(list(twice["repeat_counts"].values()), [2] * 7)

    def test_checksum_valid_other_settings_and_out_of_range_are_not_eligible(self):
        self.assertEqual(analysis.analyse_frame(synthetic_frame(24, True))["reason"], "other_settings_differ")
        for temperature in (19, 27):
            self.assertEqual(analysis.analyse_frame(synthetic_frame(temperature))["reason"], "outside_requested_range")

    def test_unrelated_wifi_text_is_not_an_overflow_event(self):
        log = log_frame(raw_frames("repeat.txt")[1]) + "\n[W][wifi:012]: SSID named OVERFLOW\n"
        result = analysis.analyse_log(log)
        self.assertFalse(result["overflow_seen"])
        self.assertTrue(result["captures"][0]["candidate_valid"])

    def test_cli_does_not_overwrite_existing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / "private.log"
            raw.write_text(log_frame(raw_frames("repeat.txt")[1]))
            output = Path(directory) / "evidence.json"
            output.write_text("preserve this existing record")
            with patch("sys.argv", ["analyse_capture.py", str(raw), "--output", str(output)]):
                with self.assertRaises(FileExistsError):
                    analysis.main()
            self.assertEqual(output.read_text(), "preserve this existing record")

    def test_cli_overflow_exit_and_oversized_input_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / "private.log"
            raw.write_text("[W][remote_receiver:104]: Buffer overflow\n")
            output = Path(directory) / "evidence.json"
            with patch("sys.argv", ["analyse_capture.py", str(raw), "--output", str(output)]):
                self.assertEqual(analysis.main(), 2)
            self.assertTrue(json.loads(output.read_text())["overflow_seen"])
            with raw.open("wb") as stream:
                stream.truncate(4 * 1024 * 1024 + 1)
            with patch("sys.argv", ["analyse_capture.py", str(raw)]), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    analysis.main()
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
