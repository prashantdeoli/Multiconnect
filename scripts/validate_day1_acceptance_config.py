#!/usr/bin/env python3
"""Validate Day-1 acceptance evidence config schema and values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

EXPECTED_TOP_LEVEL = {"audio", "ui"}
EXPECTED_FIELDS = {"status", "evidence", "next_step"}
ALLOWED_STATUS = {"Pending", "Pass", "Fail"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="docs/day1-acceptance-evidence.json")
    return parser.parse_args()


def validate_section(name: str, section: dict) -> None:
    keys = set(section.keys())
    missing = EXPECTED_FIELDS - keys
    extra = keys - EXPECTED_FIELDS
    if missing:
        raise ValueError(f"{name}: missing fields: {sorted(missing)}")
    if extra:
        raise ValueError(f"{name}: unexpected fields: {sorted(extra)}")

    status = section["status"]
    if status not in ALLOWED_STATUS:
        raise ValueError(f"{name}: invalid status '{status}', expected one of {sorted(ALLOWED_STATUS)}")

    for field in ["evidence", "next_step"]:
        value = section[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name}: '{field}' must be a non-empty string")


def main() -> int:
    args = parse_args()
    path = Path(args.config)

    if not path.exists():
        print(f"ERROR: acceptance config not found: {path}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {path}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(payload, dict):
        print("ERROR: config root must be a JSON object", file=sys.stderr)
        return 1

    keys = set(payload.keys())
    missing = EXPECTED_TOP_LEVEL - keys
    extra = keys - EXPECTED_TOP_LEVEL
    if missing:
        print(f"ERROR: missing top-level sections: {sorted(missing)}", file=sys.stderr)
        return 1
    if extra:
        print(f"ERROR: unexpected top-level sections: {sorted(extra)}", file=sys.stderr)
        return 1

    try:
        validate_section("audio", payload["audio"])
        validate_section("ui", payload["ui"])
    except (ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Acceptance config OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
