# Day-1 Execution Checklist

## Objective
Establish a reproducible feasibility baseline for MultiConnect.

## Workstreams

### A. Hardware Readiness
- [ ] Collect at least 3 speaker brands (example: Sony, Tribit, Niye).
- [ ] Record model numbers, Bluetooth versions, and battery health state.
- [ ] Build a compatibility matrix sheet for repeated test runs.

### B. Android/NDK Environment
- [ ] Initialize Android Studio project with NDK + CMake enabled.
- [ ] Add native module stubs for `sync-core` and `bt-router`.
- [ ] Configure build variants: `pocDebug`, `alphaDebug`.
- [ ] Add logging baseline (Logcat tags + native logging macros).

### C. POC Harness
- [ ] Implement native beep generator (1-second test pattern).
- [ ] Build two-device parallel output prototype.
- [ ] Add timing telemetry and pass/fail threshold report.
- [x] Store run artifacts (timestamp, devices, outcome, notes) via `poc_cli --artifact-dir ...`.

### D. Team Alignment
- [ ] Confirm owner mapping (Engine, Android, UX, QA).
- [ ] Approve weekly acceptance criteria for Phases 1-4.
- [ ] Lock first test phone(s) and fallback phone(s).

## First Meeting Acceptance Questions
- Can we push a raw test signal to two mixed-brand targets simultaneously?
- What is the baseline latency gap between target devices?
- Is there audible crackle/popping under current buffer strategy?
- Does app/UI responsiveness degrade while native routing runs?

## End-of-Day Deliverables
1. Committed repo skeleton + architecture docs.
2. Shared hardware matrix template.
3. Agreed POC pass/fail metric and test ritual.
