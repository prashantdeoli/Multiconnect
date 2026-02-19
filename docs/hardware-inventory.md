# Hardware Inventory Baseline (Day-1)

This inventory captures the first-pass mixed-brand speaker set and phone baseline for reproducible POC runs.

## Test Phone

| field | value |
|---|---|
| phone_model | Pixel 7 |
| phone_bt_version | 5.3 |
| os_build | Android 14 |
| battery_health_state | Good |
| notes | Dedicated for POC + sync-engine baseline runs |

## Speaker Baseline Set

| speaker_brand | speaker_model | bluetooth_version | battery_health_state | firmware_notes |
|---|---|---|---|---|
| Sony | SRS-XB23 | 5.0 | Good | FW validated; no pairing errors in baseline pass |
| Tribit | StormBox Micro 2 | 5.3 | Good | Stable reconnect behavior |
| Niye | Portable BT Speaker V5.0 | 5.0 | Fair | Monitor battery sag during 2h runs |

## Maintenance Rule

- Keep this inventory updated whenever test hardware rotates.
- Mirror speaker/phone combinations into `docs/hardware-matrix-template.csv` for latency/drift entries.
