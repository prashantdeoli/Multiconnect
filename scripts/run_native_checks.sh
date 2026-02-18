#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/native/build"
ARTIFACT_DIR="$BUILD_DIR/artifacts"
ESCAPE_ARTIFACT_DIR="$BUILD_DIR/artifacts_escape"

cmake -S "$ROOT_DIR/native" -B "$BUILD_DIR"
cmake --build "$BUILD_DIR"
ctest --test-dir "$BUILD_DIR" --output-on-failure
"$BUILD_DIR/poc_cli" 35 --threshold-ms 1.0 --artifact-dir "$BUILD_DIR/artifacts" --device-a "sony-sim" --device-b "tribit-sim" --notes "native-check"
