#!/usr/bin/env python3
"""Generate a concise blockers report from current project evidence files."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase1-status", default="docs/phase1-status.md")
    parser.add_argument("--baseline-report", default="docs/day1-baseline-report.md")
    parser.add_argument("--output", default="docs/project-blockers.md")
    return parser.parse_args()


def phase1_gate(phase1_text: str) -> str:
    match = re.search(r"\*\*Overall Phase-1 gate:\*\*\s*(.+)", phase1_text)
    return match.group(1).strip() if match else "UNKNOWN"


def pending_acceptance_items(baseline_text: str) -> list[str]:
    lines = baseline_text.splitlines()
    pending: list[str] = []
    current_question = ""
    question_re = re.compile(r"^\d+\.\s+\*\*(.+)\*\*")

    for line in lines:
        qmatch = question_re.match(line.strip())
        if qmatch:
            current_question = qmatch.group(1)
            continue

        if "**Status:** Pending" in line and current_question:
            pending.append(current_question)

    return pending


def main() -> int:
    args = parse_args()
    phase1_path = Path(args.phase1_status)
    baseline_path = Path(args.baseline_report)
    output_path = Path(args.output)

    phase1_text = phase1_path.read_text(encoding="utf-8")
    baseline_text = baseline_path.read_text(encoding="utf-8")

    gate_value = phase1_gate(phase1_text)
    pending_items = pending_acceptance_items(baseline_text)

    blockers: list[str] = []
    if "READY" not in gate_value:
        blockers.append(f"Phase-1 gate is not ready ({gate_value}).")
    for item in pending_items:
        blockers.append(f"Acceptance item pending: {item}")

    status = "NO ACTIVE BLOCKERS ✅" if not blockers else "OPEN BLOCKERS ⚠️"

    report = [
        "# Project Blockers Snapshot",
        "",
        f"_Last updated (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}_",
        "",
        f"**Status:** {status}",
        "",
        "## Signals Reviewed",
        "",
        f"- Phase-1 gate: `{gate_value}`",
        f"- Pending acceptance items in baseline report: `{len(pending_items)}`",
        "",
        "## Open Blockers",
        "",
    ]

    if blockers:
        report.extend([f"- {item}" for item in blockers])
    else:
        report.append("- None.")

    report.extend(
        [
            "",
            "## Recommended Next Step",
            "",
            "- If blockers remain, resolve the listed acceptance items and rerun `./scripts/run_native_checks.sh`.",
            "- If no blockers remain, keep running weekly evidence refresh and signoff checks.",
            "",
        ]
    )

    output_path.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote blockers report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
