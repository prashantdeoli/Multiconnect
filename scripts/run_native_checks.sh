#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/native/build"
ARTIFACT_DIR="$BUILD_DIR/artifacts"
ESCAPE_ARTIFACT_DIR="$BUILD_DIR/artifacts_escape"

python "$ROOT_DIR/scripts/validate_hardware_matrix.py" --csv "$ROOT_DIR/docs/hardware-matrix-template.csv"

cmake -S "$ROOT_DIR/native" -B "$BUILD_DIR"
cmake --build "$BUILD_DIR"
ctest --test-dir "$BUILD_DIR" --output-on-failure

"$BUILD_DIR/poc_cli" 35 --threshold-ms 1.0 --artifact-dir "$ARTIFACT_DIR" --device-a "sony-sim" --device-b "tribit-sim" --notes "native-check"
python "$ROOT_DIR/scripts/validate_poc_artifact.py" "$ARTIFACT_DIR" \
  --expected-device-a "sony-sim" \
  --expected-device-b "tribit-sim" \
  --expected-notes "native-check" \
  --expected-outcome "PASS"

"$BUILD_DIR/poc_cli" 35 --threshold-ms 1.0 --artifact-dir "$ESCAPE_ARTIFACT_DIR" --device-a "sony\"sim" --device-b "tribit\\sim" --notes $'quote " + slash \\ + newline\ncheck'
python "$ROOT_DIR/scripts/validate_poc_artifact.py" "$ESCAPE_ARTIFACT_DIR" \
  --expected-device-a "sony\"sim" \
  --expected-device-b "tribit\\sim" \
  --expected-notes $'quote " + slash \\ + newline\ncheck' \
  --expected-outcome "PASS"

python "$ROOT_DIR/scripts/archive_native_run_log.py" \
  --artifact-dir "$ARTIFACT_DIR" \
  --escape-artifact-dir "$ESCAPE_ARTIFACT_DIR" \
  --run-log "$ROOT_DIR/docs/native-check-run-log.csv"

python "$ROOT_DIR/scripts/validate_native_run_log.py" --run-log "$ROOT_DIR/docs/native-check-run-log.csv"
