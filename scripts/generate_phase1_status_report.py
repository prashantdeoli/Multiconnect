#!/usr/bin/env python3
"""Generate a compact Phase-1 status snapshot from current project evidence."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hardware-matrix", default="docs/hardware-matrix-template.csv")
    parser.add_argument("--run-log", default="docs/native-check-run-log.csv")
    parser.add_argument("--output", default="docs/phase1-status.md")
    parser.add_argument("--min-hardware-runs", type=int, default=3)
    parser.add_argument("--min-pass-runs", type=int, default=5)
    return parser.parse_args()


def count_matrix_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    return len([row for row in rows[1:] if row and any(cell.strip() for cell in row)])


def read_run_log(path: Path) -> tuple[int, int, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    total = len(rows)
    passed = len(
        [
            r
            for r in rows
            if r.get("outcome_standard") == "PASS" and r.get("outcome_escape") == "PASS"
        ]
    )
    latest = rows[-1]["standard_artifact"] if rows else "N/A"
    return total, passed, latest


def main() -> int:
    args = parse_args()
    hardware_matrix = Path(args.hardware_matrix)
    run_log = Path(args.run_log)
    output = Path(args.output)

    hardware_runs = count_matrix_rows(hardware_matrix)
    total_runs, pass_runs, latest_artifact = read_run_log(run_log)

    ready = hardware_runs >= args.min_hardware_runs and pass_runs >= args.min_pass_runs

    content = f"""# Phase-1 Status Snapshot

_Last updated (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}_

## Readiness Summary

| signal | current | target | status |
|---|---:|---:|---|
| real-device hardware runs | {hardware_runs} | {args.min_hardware_runs} | {'✅' if hardware_runs >= args.min_hardware_runs else '⚠️'} |
| PASS harness runs | {pass_runs} | {args.min_pass_runs} | {'✅' if pass_runs >= args.min_pass_runs else '⚠️'} |
| total logged harness runs | {total_runs} | n/a | ℹ️ |

**Overall Phase-1 gate:** {'READY ✅' if ready else 'NOT READY ⚠️'}

## Latest Evidence

- Latest standard artifact: `{latest_artifact}`
- Hardware matrix file: `{hardware_matrix.as_posix()}`
- Native run-log file: `{run_log.as_posix()}`
"""

    output.write_text(content, encoding="utf-8")
    print(f"Wrote Phase-1 status snapshot: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
