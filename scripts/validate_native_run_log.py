#!/usr/bin/env python3
"""Validate native check run-log CSV structure and entry integrity."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys

EXPECTED_HEADER = [
    "recorded_at_utc",
    "standard_artifact",
    "escape_artifact",
    "outcome_standard",
    "outcome_escape",
    "requested_offset_ms",
    "measured_offset_ms",
    "threshold_ms",
    "error_from_requested_ms",
]

ALLOWED_OUTCOMES = {"PASS", "FAIL"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-log", default="docs/native-check-run-log.csv")
    parser.add_argument("--min-rows", type=int, default=1)
    return parser.parse_args()


def parse_utc(value: str) -> None:
    datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def parse_number(value: str, field_name: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} is not numeric: {value}") from exc


def validate_row(row: dict[str, str], index: int) -> None:
    parse_utc(row["recorded_at_utc"])

    if row["outcome_standard"] not in ALLOWED_OUTCOMES:
        raise ValueError(f"row {index}: invalid outcome_standard={row['outcome_standard']}")
    if row["outcome_escape"] not in ALLOWED_OUTCOMES:
        raise ValueError(f"row {index}: invalid outcome_escape={row['outcome_escape']}")

    for path_field in ("standard_artifact", "escape_artifact"):
        if not row[path_field].endswith(".json"):
            raise ValueError(f"row {index}: {path_field} must end with .json")

    parse_number(row["requested_offset_ms"], "requested_offset_ms")
    parse_number(row["measured_offset_ms"], "measured_offset_ms")
    threshold = parse_number(row["threshold_ms"], "threshold_ms")
    error = parse_number(row["error_from_requested_ms"], "error_from_requested_ms")

    if threshold < 0:
        raise ValueError(f"row {index}: threshold_ms must be non-negative")
    if error < 0:
        raise ValueError(f"row {index}: error_from_requested_ms must be non-negative")


def main() -> int:
    args = parse_args()
    run_log = Path(args.run_log)

    if not run_log.exists():
        print(f"ERROR: run log not found: {run_log}", file=sys.stderr)
        return 1

    with run_log.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_HEADER:
            print("ERROR: run-log header mismatch", file=sys.stderr)
            print(f"Expected: {','.join(EXPECTED_HEADER)}", file=sys.stderr)
            print(f"Actual:   {','.join(reader.fieldnames or [])}", file=sys.stderr)
            return 1

        rows = list(reader)

    if len(rows) < args.min_rows:
        print(
            f"ERROR: expected at least {args.min_rows} rows, found {len(rows)}",
            file=sys.stderr,
        )
        return 1

    try:
        for i, row in enumerate(rows, start=2):
            validate_row(row, i)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Native run log OK: {run_log} (rows={len(rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
