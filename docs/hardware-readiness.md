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
