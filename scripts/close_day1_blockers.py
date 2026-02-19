#!/usr/bin/env python3
"""Apply Day-1 acceptance evidence and optionally run follow-up checks."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio-evidence")
    parser.add_argument("--ui-evidence")
    parser.add_argument("--audio-next-step")
    parser.add_argument("--ui-next-step")
    parser.add_argument("--audio-status", choices=["Pending", "Pass", "Fail"])
    parser.add_argument("--ui-status", choices=["Pending", "Pass", "Fail"])
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


def validate_group(name: str, status: str | None, evidence: str | None, next_step: str | None) -> None:
    provided = [status is not None, evidence is not None, next_step is not None]
    if any(provided) and not all(provided):
        raise SystemExit(
            f"ERROR: {name} updates require --{name}-status, --{name}-evidence, and --{name}-next-step together."
        )


def run_refresh_only(repo: Path) -> None:
    # Lightweight mode: reuse current baseline metrics and only reapply acceptance
    # evidence + regenerate status/blocker summaries.
    run(["python3", "scripts/apply_day1_acceptance_updates.py", "--from-config"], cwd=repo)
    run(["python3", "scripts/generate_phase1_status_report.py"], cwd=repo)
    run(["python3", "scripts/generate_project_blockers_report.py"], cwd=repo)
    run(["python3", "scripts/validate_phase1_readiness.py"], cwd=repo)


def maybe_update_acceptance_config(args: argparse.Namespace, repo: Path) -> None:
    validate_group("audio", args.audio_status, args.audio_evidence, args.audio_next_step)
    validate_group("ui", args.ui_status, args.ui_evidence, args.ui_next_step)

    has_updates = any(
        value is not None
        for value in [
            args.audio_status,
            args.audio_evidence,
            args.audio_next_step,
            args.ui_status,
            args.ui_evidence,
            args.ui_next_step,
        ]
    )

    if not has_updates:
        print("Using existing acceptance config (no override flags provided).")
        return

    cmd = ["python3", "scripts/apply_day1_acceptance_updates.py", "--write-config"]
    if args.audio_status is not None:
        cmd.extend(
            [
                "--audio-status",
                args.audio_status,
                "--audio-evidence",
                args.audio_evidence,
                "--audio-next-step",
                args.audio_next_step,
            ]
        )
    if args.ui_status is not None:
        cmd.extend(
            [
                "--ui-status",
                args.ui_status,
                "--ui-evidence",
                args.ui_evidence,
                "--ui-next-step",
                args.ui_next_step,
            ]
        )
    run(cmd, cwd=repo)


def print_blockers_snapshot(repo: Path) -> None:
    print("\nUpdated blockers snapshot:")
    with (repo / "docs/project-blockers.md").open(encoding="utf-8") as handle:
        for _ in range(20):
            line = handle.readline()
            if not line:
                break
            print(line.rstrip())


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()

    maybe_update_acceptance_config(args, repo)

    if args.skip_checks:
        return 0

    if args.refresh_only:
        run_refresh_only(repo)
    else:
        run(["bash", "scripts/run_native_checks.sh"], cwd=repo)

    print_blockers_snapshot(repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
