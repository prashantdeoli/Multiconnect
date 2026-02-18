#!/usr/bin/env python3
"""Validate that docs/day1-baseline-report.md matches archived run-log entries."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
import sys

LATEST_ARTIFACT_PREFIX = "- Latest standard artifact: `"
METRIC_ROW_RE = re.compile(r"^\|\s*([a-zA-Z0-9_]+)\s*\|\s*([^|]+?)\s*\|$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="docs/day1-baseline-report.md")
    parser.add_argument("--run-log", default="docs/native-check-run-log.csv")
    return parser.parse_args()


def read_run_log_rows(run_log: Path) -> list[dict[str, str]]:
    with run_log.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"run log has no entries: {run_log}")
    return rows


def read_report_artifact(report_text: str) -> str:
    for line in report_text.splitlines():
        if line.startswith(LATEST_ARTIFACT_PREFIX) and line.endswith("`"):
            return line[len(LATEST_ARTIFACT_PREFIX) : -1]
    raise ValueError("baseline report missing latest artifact line")


def read_report_metrics(report_text: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for line in report_text.splitlines():
        match = METRIC_ROW_RE.match(line.strip())
        if not match:
            continue
        key, value = match.groups()
        if key == "metric":
            continue
        metrics[key] = value
    return metrics


def almost_equal(a: str, b: str, tol: float = 1e-3) -> bool:
    return abs(float(a) - float(b)) <= tol


def main() -> int:
    args = parse_args()
    report_path = Path(args.report)
    run_log_path = Path(args.run_log)

    if not report_path.exists():
        print(f"ERROR: report not found: {report_path}", file=sys.stderr)
        return 1
    if not run_log_path.exists():
        print(f"ERROR: run log not found: {run_log_path}", file=sys.stderr)
        return 1

    try:
        run_rows = read_run_log_rows(run_log_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    report_text = report_path.read_text(encoding="utf-8")

    try:
        reported_artifact = read_report_artifact(report_text)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    row_for_artifact = None
    for row in run_rows:
        if row.get("standard_artifact", "").strip() == reported_artifact:
            row_for_artifact = row
            break

    if row_for_artifact is None:
        print(
            f"ERROR: reported artifact not present in run log: {reported_artifact}",
            file=sys.stderr,
        )
        return 1

    reported_metrics = read_report_metrics(report_text)

    required_metric_keys = [
        "sampleRateHz",
        "durationMs",
        "requestedOffsetMs",
        "measuredOffsetMs",
        "errorFromRequestedMs",
        "thresholdMs",
        "deviceA",
        "deviceB",
    ]
    for key in required_metric_keys:
        if key not in reported_metrics or not reported_metrics[key].strip():
            print(f"ERROR: baseline report missing metric row: {key}", file=sys.stderr)
            return 1

    if reported_metrics.get("requestedOffsetMs") != str(int(float(row_for_artifact["requested_offset_ms"]))):
        print(
            "ERROR: metric mismatch for requestedOffsetMs.",
            file=sys.stderr,
        )
        return 1

    for key, source in {
        "measuredOffsetMs": "measured_offset_ms",
        "thresholdMs": "threshold_ms",
        "errorFromRequestedMs": "error_from_requested_ms",
    }.items():
        actual = reported_metrics.get(key, "")
        expected = row_for_artifact[source]
        if not almost_equal(actual, expected):
            print(
                f"ERROR: metric mismatch for {key}. expected~={expected} actual={actual}",
                file=sys.stderr,
            )
            return 1

    print(f"Baseline report OK: {report_path} is consistent with run-log entry {reported_artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
