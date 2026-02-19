#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/native/build"
ARTIFACT_DIR="$BUILD_DIR/artifacts"
ESCAPE_ARTIFACT_DIR="$BUILD_DIR/artifacts_escape"

if [[ -n "${PYTHON_BIN:-}" ]]; then
  PYTHON="$PYTHON_BIN"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  echo "ERROR: python/python3 not found. Install Python 3 or set PYTHON_BIN." >&2
  exit 1
fi

"$PYTHON" "$ROOT_DIR/scripts/validate_hardware_matrix.py" --csv "$ROOT_DIR/docs/hardware-matrix-template.csv"

cmake -S "$ROOT_DIR/native" -B "$BUILD_DIR"
cmake --build "$BUILD_DIR"
ctest --test-dir "$BUILD_DIR" --output-on-failure

"$BUILD_DIR/poc_cli" 35 --threshold-ms 1.0 --artifact-dir "$ARTIFACT_DIR" --device-a "sony-sim" --device-b "tribit-sim" --notes "native-check"
"$PYTHON" "$ROOT_DIR/scripts/validate_poc_artifact.py" "$ARTIFACT_DIR" \
  --expected-device-a "sony-sim" \
  --expected-device-b "tribit-sim" \
  --expected-notes "native-check" \
  --expected-outcome "PASS"

"$BUILD_DIR/poc_cli" 35 --threshold-ms 1.0 --artifact-dir "$ESCAPE_ARTIFACT_DIR" --device-a "sony\"sim" --device-b "tribit\\sim" --notes $'quote " + slash \\ + newline\ncheck'
"$PYTHON" "$ROOT_DIR/scripts/validate_poc_artifact.py" "$ESCAPE_ARTIFACT_DIR" \
  --expected-device-a "sony\"sim" \
  --expected-device-b "tribit\\sim" \
  --expected-notes $'quote " + slash \\ + newline\ncheck' \
  --expected-outcome "PASS"

"$PYTHON" "$ROOT_DIR/scripts/archive_native_run_log.py" \
  --artifact-dir "$ARTIFACT_DIR" \
  --escape-artifact-dir "$ESCAPE_ARTIFACT_DIR" \
  --run-log "$ROOT_DIR/docs/native-check-run-log.csv"

"$PYTHON" "$ROOT_DIR/scripts/validate_native_run_log.py" --run-log "$ROOT_DIR/docs/native-check-run-log.csv"

"$PYTHON" "$ROOT_DIR/scripts/validate_day1_acceptance_config.py" --config "$ROOT_DIR/docs/day1-acceptance-evidence.json"

"$PYTHON" "$ROOT_DIR/scripts/update_day1_baseline_report.py" --report "$ROOT_DIR/docs/day1-baseline-report.md" --run-log "$ROOT_DIR/docs/native-check-run-log.csv"

"$PYTHON" "$ROOT_DIR/scripts/apply_day1_acceptance_updates.py" --report "$ROOT_DIR/docs/day1-baseline-report.md" --acceptance-config "$ROOT_DIR/docs/day1-acceptance-evidence.json" --from-config

"$PYTHON" "$ROOT_DIR/scripts/validate_day1_baseline_report.py" --report "$ROOT_DIR/docs/day1-baseline-report.md" --run-log "$ROOT_DIR/docs/native-check-run-log.csv"

"$PYTHON" "$ROOT_DIR/scripts/generate_phase1_status_report.py" --hardware-matrix "$ROOT_DIR/docs/hardware-matrix-template.csv" --run-log "$ROOT_DIR/docs/native-check-run-log.csv" --output "$ROOT_DIR/docs/phase1-status.md"

"$PYTHON" "$ROOT_DIR/scripts/generate_project_blockers_report.py" --phase1-status "$ROOT_DIR/docs/phase1-status.md" --baseline-report "$ROOT_DIR/docs/day1-baseline-report.md" --output "$ROOT_DIR/docs/project-blockers.md"

if [[ "${PHASE1_ENFORCE:-0}" == "1" ]]; then
  "$PYTHON" "$ROOT_DIR/scripts/validate_phase1_readiness.py" --hardware-matrix "$ROOT_DIR/docs/hardware-matrix-template.csv" --run-log "$ROOT_DIR/docs/native-check-run-log.csv" --enforce
else
  "$PYTHON" "$ROOT_DIR/scripts/validate_phase1_readiness.py" --hardware-matrix "$ROOT_DIR/docs/hardware-matrix-template.csv" --run-log "$ROOT_DIR/docs/native-check-run-log.csv"
fi
