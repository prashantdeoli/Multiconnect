#!/usr/bin/env python3
"""Check local environment prerequisites for running native checks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


REQUIRED_PATHS = [
    Path("scripts/run_native_checks.sh"),
    Path("native/CMakeLists.txt"),
    Path("docs/hardware-matrix-template.csv"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root to validate")
    return parser.parse_args()


def check_command(name: str) -> tuple[bool, str]:
    path = shutil.which(name)
    if not path:
        return False, f"{name}: missing"

    try:
        out = subprocess.check_output([name, "--version"], text=True, stderr=subprocess.STDOUT)
        first = out.strip().splitlines()[0] if out.strip() else "version unknown"
    except Exception:
        first = "version unknown"
    return True, f"{name}: {path} ({first})"


def main() -> int:
    args = parse_args()
    root = Path(args.repo).resolve()

    print(f"Repo root: {root}")

    ok = True
    for rel in REQUIRED_PATHS:
        target = root / rel
        exists = target.exists()
        ok &= exists
        print(f"{'OK' if exists else 'ERROR'} path: {rel}")

    python_cmd = shutil.which("python") or shutil.which("python3")
    if python_cmd:
        print(f"OK python: {python_cmd}")
    else:
        ok = False
        print("ERROR python: neither 'python' nor 'python3' found")

    for cmd in ["cmake", "ctest", "git"]:
        cmd_ok, msg = check_command(cmd)
        ok &= cmd_ok
        print(("OK " if cmd_ok else "ERROR ") + msg)

    if ok:
        print("\nEnvironment looks ready. Run: bash scripts/run_native_checks.sh")
        return 0

    print("\nEnvironment missing prerequisites. On macOS, install with:")
    print("  xcode-select --install")
    print("  brew install cmake python")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
