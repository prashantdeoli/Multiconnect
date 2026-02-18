# Hardware Readiness Runbook

Use this runbook to keep the Day-1 hardware compatibility matrix consistent across QA/Android test passes.

## Matrix File

- Source of truth: `docs/hardware-matrix-template.csv`
- Required schema is enforced by: `scripts/validate_hardware_matrix.py`

## Data Collection Rules

1. One row per phone + speaker pairing run.
2. Use a stable `run_id` format: `YYYYMMDD-<initials>-<index>`.
3. Keep units explicit:
   - latency/drift in milliseconds,
   - signal strength in dBm,
   - battery as integer percent.
4. Put firmware/version caveats in `notes`.

## Validation

Validate schema only (allows empty sheet during bootstrap):

```bash
python scripts/validate_hardware_matrix.py --csv docs/hardware-matrix-template.csv
```

Require at least 3 collected runs before weekly review:

```bash
python scripts/validate_hardware_matrix.py --csv docs/hardware-matrix-template.csv --min-rows 3
```


## Entry Helper

Use the helper script to append a complete row without manual CSV editing:

```bash
python scripts/add_hardware_matrix_entry.py \
  --run-id 20260218-qa-01 \
  --date 2026-02-18 \
  --phone-model "Pixel 7" \
  --phone-bt-version "5.3" \
  --speaker-brand "Sony" \
  --speaker-model "SRS-XB23" \
  --speaker-bt-version "5.0" \
  --battery-percent 84 \
  --signal-strength-dbm -58 \
  --observed-latency-ms 41.2 \
  --drift-after-30m-ms 7.5 \
  --drift-after-120m-ms 18.9 \
  --dropouts-count 0 \
  --notes "baseline evening run"
```

Add `--dry-run` to preview the row without writing.
