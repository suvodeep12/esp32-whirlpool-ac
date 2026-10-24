"""Bounded hardware check; run with the workspace Python containing pyserial."""
import argparse
import re
import time
from pathlib import Path

import serial

parser = argparse.ArgumentParser()
parser.add_argument("--port", required=True)
parser.add_argument("--log", required=True)
args = parser.parse_args()
lines = []
heartbeats = []
ready = False
pong = False
deadline = time.monotonic() + 35
with serial.Serial(port=None, baudrate=115200, timeout=0.5) as port:
    port.port = args.port
    port.dtr = False
    port.rts = False
    port.open()
    next_request = 0.0
    while time.monotonic() < deadline:
        if time.monotonic() >= next_request:
            port.write(b"IP")
            next_request = time.monotonic() + 5
        line = port.readline().decode("utf-8", errors="replace").strip()
        if not line:
            continue
        lines.append(line)
        print(line, flush=True)
        if line.startswith("READY "):
            assert "cores=2" in line and "flash_bytes=4194304" in line, line
            assert "heap_ok=1" in line, line
            ready = True
        pong = pong or line == "PONG"
        match = re.fullmatch(r"HEARTBEAT uptime_ms=(\d+) free_heap=(\d+)", line)
        if match:
            heartbeats.append(tuple(map(int, match.groups())))
Path(args.log).write_text("\n".join(lines) + "\n", encoding="utf-8")
assert ready and pong, "Missing hardware info or serial command response"
assert len(heartbeats) >= 25, "Insufficient heartbeat samples"
assert all(b[0] > a[0] for a, b in zip(heartbeats, heartbeats[1:])), "Unexpected reboot"
assert all(b[0] - a[0] < 2500 for a, b in zip(heartbeats, heartbeats[1:])), "Heartbeat gap"
assert all(heap > 0 for _, heap in heartbeats), "Invalid heap reading"
print(f"PASS: identity, heap integrity, bidirectional serial, {len(heartbeats)} heartbeats, no observed reboot")
