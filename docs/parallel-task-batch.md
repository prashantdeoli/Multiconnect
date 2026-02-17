# Parallel Task Batch (Day-1 Remaining Tracks)

This plan groups the remaining Day-1 work so multiple owners can execute in parallel without blocking the native POC lane.

## Batch A — Hardware Readiness (QA + Android)

1. Collect at least 3 speaker brands and capture model + Bluetooth version.
2. Fill `docs/hardware-matrix-template.csv` for baseline runs.
3. Add battery health + firmware notes before each benchmark cycle.

**Deliverable:** completed hardware matrix sheet for baseline set.

## Batch B — Android/NDK Bootstrap (Android + Engine)

1. Initialize Android project with NDK + CMake.
2. Add module stubs for `sync-core` and `bt-router` JNI integration.
3. Add build variants (`pocDebug`, `alphaDebug`) and baseline logging tags.

**Deliverable:** bootable app shell with native bridge stubs + variant wiring.

## Batch C — Native Stability Guardrail (Engine + QA)

1. Run `./scripts/run_native_checks.sh` on each PR touching native code.
2. Keep artifact validation green for both normal and escape-heavy metadata.
3. Archive latest artifacts in a shared run log for trend visibility.

**Deliverable:** green native check runs + validated JSON artifacts attached per run.

## Coordination Cadence

- Daily 15-minute sync: blockers + owner handoff updates.
- End-of-day update: checklist delta + artifact links.
- Weekly gate review: evaluate progress against `docs/team-alignment.md` phase criteria.
