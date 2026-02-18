#!/usr/bin/env python3
"""Generate a ready-to-execute Phase-1 hardware run checklist."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    sequence: int
    speaker_brand: str
    speaker_model: str
    speaker_bt_version: str
    focus: str


SCENARIOS = [
    Scenario(1, "Sony", "SRS-XB23", "5.0", "baseline stable environment"),
    Scenario(2, "Tribit", "StormBox Micro 2", "5.3", "mid-signal strength routing"),
    Scenario(3, "Niye", "Portable BT Speaker V5.0", "5.0", "battery sag risk validation"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/phase1-hardware-test-plan.md")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--initials", default="qa")
    parser.add_argument("--phone-model", default="Pixel 7")
    parser.add_argument("--phone-bt-version", default="5.3")
    parser.add_argument("--matrix", default="docs/hardware-matrix-template.csv")
    parser.add_argument("--checks-command", default="./scripts/run_native_checks.sh")
    return parser.parse_args()


def build_command(args: argparse.Namespace, scenario: Scenario) -> str:
    run_id = f"{args.date.replace('-', '')}-{args.initials}-{scenario.sequence:02d}"
    return " \\\n".join(
        [
            "python scripts/add_hardware_matrix_entry.py",
            f"  --run-id {run_id}",
            f"  --date {args.date}",
            f"  --phone-model \"{args.phone_model}\"",
            f"  --phone-bt-version \"{args.phone_bt_version}\"",
            f"  --speaker-brand \"{scenario.speaker_brand}\"",
            f"  --speaker-model \"{scenario.speaker_model}\"",
            f"  --speaker-bt-version \"{scenario.speaker_bt_version}\"",
            "  --battery-percent <measured-int>",
            "  --signal-strength-dbm <measured-int>",
            "  --observed-latency-ms <measured-float>",
            "  --drift-after-30m-ms <measured-float>",
            "  --drift-after-120m-ms <measured-float>",
            "  --dropouts-count <measured-int>",
            f"  --notes \"phase1 scenario {scenario.sequence}: {scenario.focus}\"",
        ]
    )


def render_markdown(args: argparse.Namespace) -> str:
    sections = [
        "# Phase-1 Hardware Unblock Checklist",
        "",
        f"_Generated for test date: **{args.date}** (initials: **{args.initials}**)_",
        "",
        "Use this checklist to quickly collect the minimum 3 real-device runs needed to unblock the Phase-1 readiness gate.",
        "",
        "## Gate Targets",
        "",
        "- Hardware matrix rows required: **3**",
        "- PASS native harness runs required: **5** (already met by pipeline history)",
        f"- Matrix CSV: `{args.matrix}`",
        "",
        "## Execution Sequence",
        "",
        f"1. Run the harness once and confirm it passes: `{args.checks_command}`",
        "2. Execute the three scenario commands below and replace all `<measured-...>` placeholders.",
        "3. Validate collected rows: `python scripts/validate_hardware_matrix.py --csv docs/hardware-matrix-template.csv --min-rows 3`",
        "4. Re-run `./scripts/run_native_checks.sh` and check `docs/phase1-status.md` for READY status.",
        "",
        "## Scenario Commands",
        "",
    ]

    for scenario in SCENARIOS:
        sections.extend(
            [
                f"### Scenario {scenario.sequence}: {scenario.speaker_brand} {scenario.speaker_model}",
                "",
                f"Focus: {scenario.focus}.",
                "",
                "```bash",
                build_command(args, scenario),
                "```",
                "",
            ]
        )

    sections.extend(
        [
            "## Completion Checklist",
            "",
            "- [ ] 3 real-device rows added to the hardware matrix.",
            "- [ ] Matrix validation with `--min-rows 3` passes.",
            "- [ ] `./scripts/run_native_checks.sh` passes.",
            "- [ ] `docs/phase1-status.md` shows `Overall Phase-1 gate: READY ✅`.",
            "",
        ]
    )

    return "\n".join(sections)


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    output_path.write_text(render_markdown(args), encoding="utf-8")
    print(f"Wrote Phase-1 hardware checklist: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
