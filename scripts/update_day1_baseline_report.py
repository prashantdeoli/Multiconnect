#!/usr/bin/env python3
"""Refresh docs/day1-baseline-report.md from the latest run-log artifact."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="docs/day1-baseline-report.md")
    parser.add_argument("--run-log", default="docs/native-check-run-log.csv")
    return parser.parse_args()


def latest_artifact_from_runlog(run_log: Path) -> str:
    with run_log.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("run log has no entries")
    artifact = rows[-1].get("standard_artifact", "").strip()
    if not artifact:
        raise ValueError("latest run-log row missing standard_artifact")
    return artifact


def replace_line(text: str, prefix: str, new_line: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}.*$", re.MULTILINE)
    if not pattern.search(text):
        raise ValueError(f"missing line with prefix: {prefix}")
    return pattern.sub(new_line, text)


def replace_metric_row(text: str, metric: str, value: str) -> str:
    pattern = re.compile(rf"^\|\s*{re.escape(metric)}\s*\|\s*[^|]*\|$", re.MULTILINE)
    new_row = f"| {metric} | {value} |"
    if not pattern.search(text):
        raise ValueError(f"missing metric row: {metric}")
    return pattern.sub(new_row, text)


def main() -> int:
    args = parse_args()
    report = Path(args.report)
    run_log = Path(args.run_log)

    if not report.exists():
        print(f"ERROR: report not found: {report}", file=sys.stderr)
        return 1
    if not run_log.exists():
        print(f"ERROR: run log not found: {run_log}", file=sys.stderr)
        return 1

    try:
        artifact_rel = latest_artifact_from_runlog(run_log)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    artifact_path = Path(artifact_rel)
    if not artifact_path.is_absolute():
        artifact_path = Path.cwd() / artifact_path
    if not artifact_path.exists():
        print(f"ERROR: artifact does not exist: {artifact_path}", file=sys.stderr)
        return 1

    with artifact_path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    text = report.read_text(encoding="utf-8")

    try:
        text = replace_line(text, "- Latest standard artifact:", f"- Latest standard artifact: `{artifact_rel}`")
        text = replace_line(text, "- Result:", f"- Result: `{data.get('outcome', 'UNKNOWN')}`")

        metrics = {
            "sampleRateHz": str(data.get("sampleRateHz", "")),
            "durationMs": str(data.get("durationMs", "")),
            "requestedOffsetMs": str(data.get("requestedOffsetMs", "")),
            "measuredOffsetMs": str(data.get("measuredOffsetMs", "")),
            "errorFromRequestedMs": str(data.get("errorFromRequestedMs", "")),
            "thresholdMs": str(data.get("thresholdMs", "")),
            "deviceA": str(data.get("deviceA", "")),
            "deviceB": str(data.get("deviceB", "")),
        }
        for key, value in metrics.items():
            text = replace_metric_row(text, key, value)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    report.write_text(text, encoding="utf-8")
    print(f"Updated baseline report from artifact: {artifact_rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
