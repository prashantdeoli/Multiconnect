# Day-1 Baseline Report

This report captures the current reproducible baseline from the native POC harness and maps it to the Day-1 acceptance questions.

## Baseline Run Snapshot

- Source command: `./scripts/run_native_checks.sh`
- Latest standard artifact: `native/build/artifacts/poc_run_20260218T062053Z.json`
- Result: `PASS`

### Key Metrics

| metric | value |
|---|---|
| sampleRateHz | 44100 |
| durationMs | 1000 |
| requestedOffsetMs | 35 |
| measuredOffsetMs | 34.9887 |
| errorFromRequestedMs | 0.0113379 |
| thresholdMs | 1 |
| deviceA | sony-sim |
| deviceB | tribit-sim |

## Acceptance Question Status

1. **Can we push a raw test signal to two mixed-brand targets simultaneously?**
   - **Status:** Yes (simulated baseline).
   - **Evidence:** `deviceA` + `deviceB` pass result in artifact output.
2. **What is the baseline latency gap between target devices?**
   - **Status:** Captured in current native simulation.
   - **Evidence:** measured offset `34.9887 ms` vs requested `35 ms` (error `0.0113379 ms`).
3. **Is there audible crackle/popping under current buffer strategy?**
   - **Status:** Pending physical-device validation.
   - **Next step:** run hardware matrix sessions with real speaker pairs and annotate `notes`.
4. **Does app/UI responsiveness degrade while native routing runs?**
   - **Status:** Pending Android app integration benchmark.
   - **Next step:** capture frame/render responsiveness once browser/audio routing UI is integrated.

## Follow-up

- Use `docs/hardware-inventory.md` + `docs/hardware-matrix-template.csv` for real-device runs.
- Update this report weekly with latest artifact IDs and observed hardware notes.
- Check trend history in `docs/native-check-run-log.csv` for run-over-run deltas.
- First-test-phone lock is recorded in `docs/team-alignment.md` (Primary: Pixel 7, Fallback: Pixel 6a).
