#!/usr/bin/env python3
"""Apply Day-1 acceptance status/evidence updates to the baseline report."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="docs/day1-baseline-report.md")

    parser.add_argument("--audio-status", choices=["Pending", "Pass", "Fail"], required=True)
    parser.add_argument("--audio-evidence", required=True)
    parser.add_argument("--audio-next-step", required=True)

    parser.add_argument("--ui-status", choices=["Pending", "Pass", "Fail"], required=True)
    parser.add_argument("--ui-evidence", required=True)
    parser.add_argument("--ui-next-step", required=True)
    return parser.parse_args()


def replace_question_block(lines: list[str], question_number: int, status: str, evidence: str, next_step: str) -> list[str]:
    start_idx = None
    end_idx = None
    needle = f"{question_number}. **"

    for idx, line in enumerate(lines):
        if line.startswith(needle):
            start_idx = idx
            continue
        if start_idx is not None and line.startswith(f"{question_number + 1}. **"):
            end_idx = idx
            break

    if start_idx is None:
        raise ValueError(f"Could not find question {question_number} block in baseline report.")
    if end_idx is None:
        end_idx = len(lines)

    header = lines[start_idx]
    indent = "   "
    new_block = [
        header,
        f"{indent}- **Status:** {status}.",
        f"{indent}- **Evidence:** {evidence}",
        f"{indent}- **Next step:** {next_step}",
    ]

    return lines[:start_idx] + new_block + lines[end_idx:]


def main() -> int:
    args = parse_args()
    report_path = Path(args.report)

    lines = report_path.read_text(encoding="utf-8").splitlines()

    lines = replace_question_block(
        lines,
        question_number=3,
        status=args.audio_status,
        evidence=args.audio_evidence,
        next_step=args.audio_next_step,
    )
    lines = replace_question_block(
        lines,
        question_number=4,
        status=args.ui_status,
        evidence=args.ui_evidence,
        next_step=args.ui_next_step,
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Updated baseline acceptance items in: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
