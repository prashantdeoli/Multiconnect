#!/usr/bin/env python3
"""Evaluate Phase-1 readiness signals from hardware matrix and run-log artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hardware-matrix", default="docs/hardware-matrix-template.csv")
    parser.add_argument("--run-log", default="docs/native-check-run-log.csv")
    parser.add_argument("--min-hardware-runs", type=int, default=3)
    parser.add_argument("--min-pass-runs", type=int, default=5)
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Fail with non-zero exit code when thresholds are not met.",
    )
    return parser.parse_args()


def count_data_rows(csv_path: Path) -> int:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    return len([row for row in rows[1:] if row and any(cell.strip() for cell in row)])


def count_pass_rows(run_log: Path) -> tuple[int, int]:
    with run_log.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    pass_rows = [
        row
        for row in rows
        if row.get("outcome_standard") == "PASS" and row.get("outcome_escape") == "PASS"
    ]
    return len(rows), len(pass_rows)


def main() -> int:
    args = parse_args()
    matrix_path = Path(args.hardware_matrix)
    run_log_path = Path(args.run_log)

    if not matrix_path.exists():
        print(f"ERROR: hardware matrix not found: {matrix_path}", file=sys.stderr)
        return 1
    if not run_log_path.exists():
        print(f"ERROR: run log not found: {run_log_path}", file=sys.stderr)
        return 1

    hardware_runs = count_data_rows(matrix_path)
    total_runs, pass_runs = count_pass_rows(run_log_path)

    ok_hardware = hardware_runs >= args.min_hardware_runs
    ok_pass = pass_runs >= args.min_pass_runs

    print(
        "Phase-1 readiness summary: "
        f"hardware_runs={hardware_runs}/{args.min_hardware_runs}, "
        f"pass_runs={pass_runs}/{args.min_pass_runs}, total_logged_runs={total_runs}"
    )

    if ok_hardware and ok_pass:
        print("Phase-1 readiness gate: READY")
        return 0

    print("Phase-1 readiness gate: NOT READY")
    if not ok_hardware:
        print("- Missing required real-device hardware matrix entries.")
    if not ok_pass:
        print("- Missing required number of PASS run-log entries.")

    if args.enforce:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
