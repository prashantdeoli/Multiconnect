#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/native/build"
ARTIFACT_DIR="$BUILD_DIR/artifacts"
ESCAPE_ARTIFACT_DIR="$BUILD_DIR/artifacts_escape"

cmake -S "$ROOT_DIR/native" -B "$BUILD_DIR"
cmake --build "$BUILD_DIR"
ctest --test-dir "$BUILD_DIR" --output-on-failure
"$BUILD_DIR/poc_cli" 35 --threshold-ms 1.0 --artifact-dir "$ARTIFACT_DIR" --device-a "sony-sim" --device-b "tribit-sim" --notes "native-check"
"$BUILD_DIR/poc_cli" 35 --threshold-ms 1.0 --artifact-dir "$ESCAPE_ARTIFACT_DIR" --device-a "sony\"sim" --device-b "tribit\\sim" --notes $'quote " + slash \\ + newline\ncheck'

ESCAPE_ARTIFACT_DIR="$ESCAPE_ARTIFACT_DIR" python - <<'PY'
import json
import os
from pathlib import Path

artifact_dir = Path(os.environ["ESCAPE_ARTIFACT_DIR"])
latest = max(artifact_dir.glob("poc_run_*.json"), key=lambda p: p.stat().st_mtime)
with latest.open("r", encoding="utf-8") as fh:
    payload = json.load(fh)

assert payload["deviceA"] == 'sony"sim'
assert payload["deviceB"] == 'tribit\\sim'
assert payload["notes"] == 'quote " + slash \\ + newline\ncheck'
print(f"Validated JSON escaping artifact: {latest}")
PY
