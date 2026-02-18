#!/usr/bin/env python3
"""Validate the hardware compatibility matrix CSV structure."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

REQUIRED_COLUMNS = [
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
    parser.add_argument(
        "--csv",
        default="docs/hardware-matrix-template.csv",
        help="Path to the matrix CSV file.",
    )
    parser.add_argument(
        "--min-rows",
        type=int,
        default=0,
        help="Minimum required number of data rows (excluding header).",
    )
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

    if not rows:
        print(f"ERROR: CSV is empty: {csv_path}", file=sys.stderr)
        return 1

    header = rows[0]
    if header != REQUIRED_COLUMNS:
        print("ERROR: CSV header does not match expected schema.", file=sys.stderr)
        print("Expected:", ",".join(REQUIRED_COLUMNS), file=sys.stderr)
        print("Actual:  ", ",".join(header), file=sys.stderr)
        return 1

    data_rows = [row for row in rows[1:] if row and any(cell.strip() for cell in row)]
    if len(data_rows) < args.min_rows:
        print(
            f"ERROR: Expected at least {args.min_rows} data rows, found {len(data_rows)}.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Hardware matrix OK: {csv_path} (rows={len(data_rows)}, schema={len(header)} columns)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
