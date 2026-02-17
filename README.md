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
- `native/` — C++ proof-of-concept primitives (beep generator, sync math, ring buffer, sync engine, CLI harness).
- `scripts/run_native_checks.sh` — local build/test command for the native POC components.

## Run Native POC Checks

```bash
./scripts/run_native_checks.sh
```

This builds the native project, runs unit checks, and executes `poc_cli` with a 35ms synthetic device offset.

The sync engine now also tracks per-device pull telemetry (`pullCalls`, `pulledSamples`, `lastReadSamples`) to support upcoming JNI-facing runtime diagnostics.

## Day-1 Goal

Create a reproducible baseline for feasibility: hardware matrix, Android/NDK project setup, and POC acceptance harness.
