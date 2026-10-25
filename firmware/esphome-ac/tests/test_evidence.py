"""Cross-check fixed firmware payloads against the recorded physical captures."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[1]


class EvidenceTests(unittest.TestCase):
    def test_payloads_match_every_valid_repeat_capture(self):
        header = (PROJECT / "captured_frames.h").read_text()
        frames = json.loads((REPO / "firmware/ir-receiver/captures/repeat-analysis.json").read_text())
        for temperature, duration in ((24, 117873), (25, 116367)):
            with self.subTest(temperature=temperature):
                match = re.search(r"state" + str(temperature) + r"\[\] = \{([^}]+)", header)
                state = bytes(int(value, 0) for value in match[1].split(","))
                valid = [f for f in frames if f["checksum_valid"] and f["temperature_candidate"] == temperature]
                self.assertTrue(valid)
                for frame in valid:
                    self.assertEqual(state.hex(" "), frame["msb_bytes"])
                self.assertEqual(len(state), 14)
                measured = 3370 + 1365 + 112 * 580 + 600
                measured += sum(1003 if byte & (1 << bit) else 250 for byte in state for bit in range(8))
                self.assertEqual(measured, duration)

    def test_secrets_creation_preserves_existing_credentials(self):
        spec = importlib.util.spec_from_file_location("create_secrets", PROJECT / "create_secrets.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            module.__file__ = str(Path(directory) / "create_secrets.py")
            module.main()
            path = Path(directory) / "secrets.yaml"
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                module.main()
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
