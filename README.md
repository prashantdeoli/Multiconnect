# MultiConnect

MultiConnect is an Android-first audio hub concept that aims to route one source stream to multiple Bluetooth speakers across different brands.

## Mission

Break the single-speaker limitation on phones by building a brand-agnostic multi-speaker playback engine with user-facing sync controls.

## Product Principles

- **Brand agnostic output:** connect mixed speaker brands in one session.
- **Precision synchronization:** manual + assisted latency calibration.
- **No extra hardware:** rely on phone, software routing, and existing speakers.
- **Browser-first media ingestion:** if it plays in the in-app browser, it can be routed.

## Lean Prototype Roadmap

### Phase 1 (Weeks 1-2): Transport Feasibility POC
- Build a minimal native test harness to target two devices and emit a shared beep.
- Goal: determine whether the test handset can maintain parallel Bluetooth transport paths.
- Exit metric: both devices render a 1-second test signal with <= 50 ms relative offset.

### Phase 2 (Weeks 3-6): Sync Engine
- Implement master ring buffer and per-device read offset.
- Add manual sync sliders and persistent calibration state.
- Exit metric: user can audibly remove echo between two mixed-brand speakers.

### Phase 3 (Weeks 7-10): Android App Integration
- Integrate browser shell, audio capture path, and native engine bridge.
- Build initial dark-theme “Audio Matrix” controls.
- Exit metric: browser media routed to 3 simultaneous connected outputs.

### Phase 4 (Weeks 11-12): Alpha Torture Testing
- Stress test mixed Bluetooth generations over long sessions.
- Validate interruption handling and recovery logic.
- Exit metric: 2-hour continuous session without crash or unacceptable drift.

## Repository Layout

- `docs/architecture.md` — technical architecture and module contracts.
- `docs/day1-checklist.md` — immediate execution checklist and owners.
- `docs/hardware-matrix-template.csv` — starter sheet for compatibility and drift benchmarking.
- `docs/hardware-readiness.md` — runbook for collecting and validating hardware readiness matrix entries.
- `docs/hardware-inventory.md` — baseline phone/speaker inventory (models, BT versions, battery state) for Day-1 readiness.
- `docs/team-alignment.md` — owner mapping, phase acceptance criteria, phone-lock template, and weekly test ritual.
- `docs/parallel-task-batch.md` — parallel Day-1 execution plan for hardware, Android/NDK bootstrap, and native stability guardrails.
- `docs/day1-baseline-report.md` — current baseline metrics mapped to Day-1 acceptance questions.
- `docs/native-check-run-log.csv` — shared history of native check/artifact runs for trend visibility.
- `scripts/validate_native_run_log.py` — integrity checks for native run-log schema, ordering, and values.
- `scripts/validate_day1_baseline_report.py` — ensures baseline report metrics match latest archived artifact.
- `android/` — Android Studio bootstrap project with NDK/CMake wiring, native stubs, and `poc`/`alpha` product flavors.

## Day-1 Goal

Create a reproducible baseline for feasibility: hardware matrix, Android/NDK project setup, and POC acceptance harness.

## Native POC Harness

Run the baseline native checks (build + unit tests + POC pass/fail run):

```bash
./scripts/run_native_checks.sh
```

The POC harness now writes run artifacts (`timestamp`, `devices`, `outcome`, and `notes`) to `native/build/artifacts/` when invoked with `--artifact-dir`.

The native checks also execute sync-engine and beep-generator unit tests to keep core timing primitives covered in CI/local runs.

Run-log archiving keeps the latest entries bounded (`archive_native_run_log.py --max-rows`, default: 200) to avoid unbounded CSV growth.

Native logging macros are available in `native/include/multiconnect/logging.h` and map to Logcat on Android builds.
