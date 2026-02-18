# Team Alignment (Day-1)

## Owner Mapping

| Area | Primary Owner | Secondary Owner | Responsibilities |
|---|---|---|---|
| Engine (NDK `sync-core`) | Audio Engine Lead | QA Lead | Ring buffer, sync offsets, drift correction, native test harness quality. |
| Android (`app`, `audio-capture`) | Android Lead | Audio Engine Lead | Foreground service, capture pipeline, JNI bridge, device/session state. |
| UX (`browser-shell`, controls) | UX Lead | Android Lead | Playback controls, calibration flows, session status visibility, error messaging. |
| QA (test protocol + matrix) | QA Lead | Android Lead | Compatibility matrix maintenance, pass/fail ritual, regression evidence collection. |

## Weekly Acceptance Criteria (Phases 1-4)

### Phase 1 — Transport Feasibility POC (Weeks 1-2)
- PASS: test harness emits a shared 1-second signal to two selected outputs.
- PASS: measured relative offset is <= 50 ms at least 4/5 runs on baseline hardware.
- PASS: each run stores an artifact with timestamp, target devices, outcome, and notes.

### Phase 2 — Sync Engine (Weeks 3-6)
- PASS: manual per-device offset adjustments are applied and persisted across app restarts.
- PASS: sync correction workflow can reduce audible echo on mixed-brand pair.
- PASS: sync metrics (drift estimate + correction count) are visible in debug telemetry.

### Phase 3 — Android App Integration (Weeks 7-10)
- PASS: in-app browser media routes to three simultaneous outputs in supported topology.
- PASS: app remains responsive while routing and calibration UI are active.
- PASS: session resume/recover path works after brief Bluetooth interruption.

### Phase 4 — Alpha Torture Testing (Weeks 11-12)
- PASS: 2-hour continuous mixed-brand session without crash.
- PASS: no sustained unacceptable drift after stabilization window.
- PASS: run logs include interruption/recovery outcomes and notable defects.

## First Test Phone Lock (Template)

- Primary phone model: Pixel 7
- Primary phone Android version: Android 14
- Fallback phone model: Pixel 6a
- Fallback phone Android version: Android 14
- Lock date: 2026-02-17
- Owner sign-off: QA Lead + Android Lead

## Weekly Test Ritual

1. Select fixed hardware set from the compatibility matrix.
2. Execute `./scripts/run_native_checks.sh`.
3. Record artifact files + notes in the run log.
4. Review pass/fail against active phase criteria.
5. Raise blockers with owner + mitigation before next planning checkpoint.
6. Append latest entry to `docs/native-check-run-log.csv` and tag weekly gate status.
