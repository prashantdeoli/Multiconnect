# Day-1 Execution Checklist

## Objective
Establish a reproducible feasibility baseline for MultiConnect.

## Workstreams

### A. Hardware Readiness
- [x] Collect at least 3 speaker brands (example: Sony, Tribit, Niye) in `docs/hardware-inventory.md`.
- [x] Record model numbers, Bluetooth versions, and battery health state in `docs/hardware-inventory.md`.
- [x] Build a compatibility matrix sheet for repeated test runs (`docs/hardware-matrix-template.csv`, validated by `scripts/validate_hardware_matrix.py`).

### B. Android/NDK Environment
- [x] Initialize Android Studio project with NDK + CMake enabled (`android/`).
- [x] Add native module stubs for `sync-core` and `bt-router` (`android/app/src/main/cpp/*_stub.cpp`).
- [x] Configure build variants: `pocDebug`, `alphaDebug` (`android/app/build.gradle.kts` product flavors).
- [x] Add logging baseline (Logcat tags + native logging macros) via `native/include/multiconnect/logging.h`.

### C. POC Harness
- [x] Implement native beep generator (1-second test pattern).
- [x] Build two-device parallel output prototype.
- [x] Add timing telemetry and pass/fail threshold report.
- [x] Store run artifacts (timestamp, devices, outcome, notes) via `poc_cli --artifact-dir ...`.

### D. Team Alignment
- [x] Confirm owner mapping (Engine, Android, UX, QA).
- [x] Approve weekly acceptance criteria for Phases 1-4.
- [x] Lock first test phone(s) and fallback phone(s) using the team alignment template.

## First Meeting Acceptance Questions
- Can we push a raw test signal to two mixed-brand targets simultaneously?
- What is the baseline latency gap between target devices?
- Is there audible crackle/popping under current buffer strategy?
- Does app/UI responsiveness degrade while native routing runs?

## End-of-Day Deliverables
1. Committed repo skeleton + architecture docs.
2. Shared hardware matrix template.
3. Agreed POC pass/fail metric and test ritual.
