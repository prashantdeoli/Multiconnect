#!/usr/bin/env python3
"""Archive latest native-check artifact metadata into a shared CSV run log."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent

HEADER = [
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


def latest_json(path: Path) -> Path:
    candidates = sorted(path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No JSON artifacts found in {path}")
    return candidates[0]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def ensure_header(path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)


def to_repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def trim_rows(path: Path, max_rows: int) -> None:
    if max_rows <= 0 or not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    if len(rows) <= 1:
        return

    header, data_rows = rows[0], rows[1:]
    if len(data_rows) <= max_rows:
        return

    kept = data_rows[-max_rows:]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(kept)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--escape-artifact-dir", required=True)
    parser.add_argument("--run-log", default="docs/native-check-run-log.csv")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=200,
        help="Maximum data rows to keep in the run log (0 disables trimming).",
    )
    args = parser.parse_args()

    artifact_dir = Path(args.artifact_dir)
    escape_dir = Path(args.escape_artifact_dir)
    run_log = Path(args.run_log)

    try:
        standard_path = latest_json(artifact_dir)
        escape_path = latest_json(escape_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    standard = load_json(standard_path)
    escape = load_json(escape_path)

    ensure_header(run_log)
    with run_log.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                to_repo_relative(standard_path),
                to_repo_relative(escape_path),
                standard.get("outcome", ""),
                escape.get("outcome", ""),
                standard.get("requestedOffsetMs", ""),
                standard.get("measuredOffsetMs", ""),
                standard.get("thresholdMs", ""),
                standard.get("errorFromRequestedMs", ""),
            ]
        )

    trim_rows(run_log, args.max_rows)
    print(f"Archived run metadata to {run_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
