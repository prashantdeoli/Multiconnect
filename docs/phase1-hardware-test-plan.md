# Phase-1 Hardware Unblock Checklist

_Generated for test date: **2026-02-18** (initials: **qa**)_

Use this checklist to quickly collect the minimum 3 real-device runs needed to unblock the Phase-1 readiness gate.

## Gate Targets

- Hardware matrix rows required: **3**
- PASS native harness runs required: **5** (already met by pipeline history)
- Matrix CSV: `docs/hardware-matrix-template.csv`

## Execution Sequence

1. Run the harness once and confirm it passes: `./scripts/run_native_checks.sh`
2. Execute the three scenario commands below and replace all `<measured-...>` placeholders.
3. Validate collected rows: `python scripts/validate_hardware_matrix.py --csv docs/hardware-matrix-template.csv --min-rows 3`
4. Re-run `./scripts/run_native_checks.sh` and check `docs/phase1-status.md` for READY status.

## Scenario Commands

### Scenario 1: Sony SRS-XB23

Focus: baseline stable environment.

```bash
python scripts/add_hardware_matrix_entry.py \
  --run-id 20260218-qa-01 \
  --date 2026-02-18 \
  --phone-model "Pixel 7" \
  --phone-bt-version "5.3" \
  --speaker-brand "Sony" \
  --speaker-model "SRS-XB23" \
  --speaker-bt-version "5.0" \
  --battery-percent <measured-int> \
  --signal-strength-dbm <measured-int> \
  --observed-latency-ms <measured-float> \
  --drift-after-30m-ms <measured-float> \
  --drift-after-120m-ms <measured-float> \
  --dropouts-count <measured-int> \
  --notes "phase1 scenario 1: baseline stable environment"
```

### Scenario 2: Tribit StormBox Micro 2

Focus: mid-signal strength routing.

```bash
python scripts/add_hardware_matrix_entry.py \
  --run-id 20260218-qa-02 \
  --date 2026-02-18 \
  --phone-model "Pixel 7" \
  --phone-bt-version "5.3" \
  --speaker-brand "Tribit" \
  --speaker-model "StormBox Micro 2" \
  --speaker-bt-version "5.3" \
  --battery-percent <measured-int> \
  --signal-strength-dbm <measured-int> \
  --observed-latency-ms <measured-float> \
  --drift-after-30m-ms <measured-float> \
  --drift-after-120m-ms <measured-float> \
  --dropouts-count <measured-int> \
  --notes "phase1 scenario 2: mid-signal strength routing"
```

### Scenario 3: Niye Portable BT Speaker V5.0

Focus: battery sag risk validation.

```bash
python scripts/add_hardware_matrix_entry.py \
  --run-id 20260218-qa-03 \
  --date 2026-02-18 \
  --phone-model "Pixel 7" \
  --phone-bt-version "5.3" \
  --speaker-brand "Niye" \
  --speaker-model "Portable BT Speaker V5.0" \
  --speaker-bt-version "5.0" \
  --battery-percent <measured-int> \
  --signal-strength-dbm <measured-int> \
  --observed-latency-ms <measured-float> \
  --drift-after-30m-ms <measured-float> \
  --drift-after-120m-ms <measured-float> \
  --dropouts-count <measured-int> \
  --notes "phase1 scenario 3: battery sag risk validation"
```

## Completion Checklist

- [ ] 3 real-device rows added to the hardware matrix.
- [ ] Matrix validation with `--min-rows 3` passes.
- [ ] `./scripts/run_native_checks.sh` passes.
- [ ] `docs/phase1-status.md` shows `Overall Phase-1 gate: READY ✅`.
