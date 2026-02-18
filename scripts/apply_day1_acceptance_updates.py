#!/usr/bin/env python3
"""Apply Day-1 acceptance status/evidence updates to the baseline report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


QUESTION_CONFIG = {
    3: {
        "key": "audio",
        "title": "Is there audible crackle/popping under current buffer strategy?",
    },
    4: {
        "key": "ui",
        "title": "Does app/UI responsiveness degrade while native routing runs?",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default="docs/day1-baseline-report.md")
    parser.add_argument("--acceptance-config", default="docs/day1-acceptance-evidence.json")

    parser.add_argument("--audio-status", choices=["Pending", "Pass", "Fail"])
    parser.add_argument("--audio-evidence")
    parser.add_argument("--audio-next-step")

    parser.add_argument("--ui-status", choices=["Pending", "Pass", "Fail"])
    parser.add_argument("--ui-evidence")
    parser.add_argument("--ui-next-step")

    parser.add_argument(
        "--from-config",
        action="store_true",
        help="Apply updates from --acceptance-config only.",
    )
    parser.add_argument(
        "--write-config",
        action="store_true",
        help="Persist provided --audio-* / --ui-* values to --acceptance-config.",
    )
    return parser.parse_args()


def ensure_block(line: str, question_number: int) -> bool:
    return line.startswith(f"{question_number}. **")


def replace_question_block(lines: list[str], question_number: int, status: str, evidence: str, next_step: str) -> list[str]:
    start_idx = None
    end_idx = None

    for idx, line in enumerate(lines):
        if ensure_block(line, question_number):
            start_idx = idx
            continue
        if start_idx is not None and ensure_block(line, question_number + 1):
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


def validate_group(label: str, status: str | None, evidence: str | None, next_step: str | None) -> None:
    provided = [status is not None, evidence is not None, next_step is not None]
    if any(provided) and not all(provided):
        raise ValueError(f"{label} updates require status, evidence, and next-step together.")


def load_config(path: Path) -> dict:
    if not path.exists():
        raise ValueError(f"acceptance config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_config(path: Path, updates: dict) -> None:
    payload = {
        "audio": updates["audio"],
        "ui": updates["ui"],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def merge_cli_updates(base: dict, args: argparse.Namespace) -> dict:
    result = {
        "audio": dict(base["audio"]),
        "ui": dict(base["ui"]),
    }

    if args.audio_status is not None:
        result["audio"] = {
            "status": args.audio_status,
            "evidence": args.audio_evidence,
            "next_step": args.audio_next_step,
        }

    if args.ui_status is not None:
        result["ui"] = {
            "status": args.ui_status,
            "evidence": args.ui_evidence,
            "next_step": args.ui_next_step,
        }

    return result


def main() -> int:
    args = parse_args()

    try:
        validate_group("audio", args.audio_status, args.audio_evidence, args.audio_next_step)
        validate_group("ui", args.ui_status, args.ui_evidence, args.ui_next_step)
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}")

    report_path = Path(args.report)
    config_path = Path(args.acceptance_config)
    config = load_config(config_path)
    updates = merge_cli_updates(config, args)

    if args.write_config:
        write_config(config_path, updates)
        print(f"Wrote acceptance config: {config_path}")

    lines = report_path.read_text(encoding="utf-8").splitlines()
    for question_number, metadata in QUESTION_CONFIG.items():
        key = metadata["key"]
        lines = replace_question_block(
            lines,
            question_number=question_number,
            status=updates[key]["status"],
            evidence=updates[key]["evidence"],
            next_step=updates[key]["next_step"],
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Updated baseline acceptance items in: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
