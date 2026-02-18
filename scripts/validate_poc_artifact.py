#!/usr/bin/env python3
"""Validate a generated poc_cli artifact JSON file."""

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a MultiConnect POC artifact JSON file.")
    parser.add_argument("artifact_dir", type=Path, help="Directory containing poc_run_*.json files")
    parser.add_argument("--expected-device-a", required=True)
    parser.add_argument("--expected-device-b", required=True)
    parser.add_argument("--expected-notes", required=True)
    parser.add_argument("--expected-outcome", default="PASS")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates = sorted(args.artifact_dir.glob("poc_run_*.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise SystemExit(f"No artifact files found in: {args.artifact_dir}")

    latest = candidates[-1]
    payload = json.loads(latest.read_text(encoding="utf-8"))

    assert payload.get("deviceA") == args.expected_device_a
    assert payload.get("deviceB") == args.expected_device_b
    assert payload.get("notes") == args.expected_notes
    assert payload.get("outcome") == args.expected_outcome
    assert isinstance(payload.get("requestedOffsetMs"), int)
    assert isinstance(payload.get("measuredOffsetMs"), (int, float))

    print(f"Validated artifact: {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
