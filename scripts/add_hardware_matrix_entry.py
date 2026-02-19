#!/usr/bin/env python3
"""Append a validated hardware-run entry to docs/hardware-matrix-template.csv."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

HEADER = [
    "run_id",
    "date",
    "phone_model",
    "phone_bt_version",
    "speaker_brand",
    "speaker_model",
    "speaker_bt_version",
    "battery_percent",
    "signal_strength_dbm",
    "observed_latency_ms",
    "drift_after_30m_ms",
    "drift_after_120m_ms",
    "dropouts_count",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="docs/hardware-matrix-template.csv")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--phone-model", required=True)
    parser.add_argument("--phone-bt-version", required=True)
    parser.add_argument("--speaker-brand", required=True)
    parser.add_argument("--speaker-model", required=True)
    parser.add_argument("--speaker-bt-version", required=True)
    parser.add_argument("--battery-percent", required=True, type=int)
    parser.add_argument("--signal-strength-dbm", required=True, type=int)
    parser.add_argument("--observed-latency-ms", required=True, type=float)
    parser.add_argument("--drift-after-30m-ms", required=True, type=float)
    parser.add_argument("--drift-after-120m-ms", required=True, type=float)
    parser.add_argument("--dropouts-count", required=True, type=int)
    parser.add_argument("--notes", default="")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
        return 1

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    if not rows or rows[0] != HEADER:
        print("ERROR: CSV header mismatch; run validate_hardware_matrix.py first.", file=sys.stderr)
        return 1

    new_row = [
        args.run_id,
        args.date,
        args.phone_model,
        args.phone_bt_version,
        args.speaker_brand,
        args.speaker_model,
        args.speaker_bt_version,
        str(args.battery_percent),
        str(args.signal_strength_dbm),
        str(args.observed_latency_ms),
        str(args.drift_after_30m_ms),
        str(args.drift_after_120m_ms),
        str(args.dropouts_count),
        args.notes,
    ]

    if args.dry_run:
        print("Dry run; would append row:")
        print(",".join(new_row))
        return 0

    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(new_row)

    print(f"Appended hardware-matrix row to {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
