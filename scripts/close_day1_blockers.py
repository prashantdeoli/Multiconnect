#!/usr/bin/env python3
"""Apply Day-1 acceptance evidence and optionally run full native checks."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio-evidence", required=True)
    parser.add_argument("--ui-evidence", required=True)
    parser.add_argument(
        "--audio-next-step",
        default="Track weekly regressions in hardware matrix notes.",
    )
    parser.add_argument(
        "--ui-next-step",
        default="Re-check responsiveness on each new Android build.",
    )
    parser.add_argument("--audio-status", choices=["Pending", "Pass", "Fail"], default="Pass")
    parser.add_argument("--ui-status", choices=["Pending", "Pass", "Fail"], default="Pass")
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Only update acceptance config/report; skip follow-up regeneration checks.",
    )
    parser.add_argument(
        "--refresh-only",
        action="store_true",
        help="Regenerate report artifacts without running full native build/test pipeline.",
    )
    parser.add_argument("--repo", default=".")
    return parser.parse_args()


def run(cmd: list[str], cwd: Path) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)



def run_refresh_only(repo: Path) -> None:
    # Lightweight mode: reuse current baseline metrics and only reapply acceptance
    # evidence + regenerate status/blocker summaries.
    run(
        [
            "python3",
            "scripts/apply_day1_acceptance_updates.py",
            "--from-config",
        ],
        cwd=repo,
    )
    run(["python3", "scripts/generate_phase1_status_report.py"], cwd=repo)
    run(["python3", "scripts/generate_project_blockers_report.py"], cwd=repo)
    run(["python3", "scripts/validate_phase1_readiness.py"], cwd=repo)


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()

    run(
        [
            "python3",
            "scripts/apply_day1_acceptance_updates.py",
            "--audio-status",
            args.audio_status,
            "--audio-evidence",
            args.audio_evidence,
            "--audio-next-step",
            args.audio_next_step,
            "--ui-status",
            args.ui_status,
            "--ui-evidence",
            args.ui_evidence,
            "--ui-next-step",
            args.ui_next_step,
            "--write-config",
        ],
        cwd=repo,
    )

    if args.skip_checks:
        return 0

    if args.refresh_only:
        run_refresh_only(repo)
    else:
        run(["bash", "scripts/run_native_checks.sh"], cwd=repo)

    print("\nUpdated blockers snapshot:")
    with (repo / "docs/project-blockers.md").open(encoding="utf-8") as handle:
        for _ in range(20):
            line = handle.readline()
            if not line:
                break
            print(line.rstrip())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
