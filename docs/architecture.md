# MultiConnect Architecture (MVP to Alpha)

## 1) High-Level System

```text
[WebView/GeckoView Media]
        |
        v
[Android Audio Capture Layer] --PCM--> [Native Sync Core (C++/NDK)] --frames--> [Per-Device Bluetooth Output Workers]
        |                                                      |
        |                                                      +--> drift monitor + micro-correction
        v
[Foreground Service + Session Orchestrator] <--> [UI Audio Matrix + Calibration]
```

## 2) Proposed Modules

### `app` (Android/Kotlin)
Responsibilities:
- App lifecycle, onboarding, permissions.
- Foreground audio service startup/shutdown.
- UI state binding and device/session controls.

Primary classes (proposed):
- `MainActivity`
- `AudioSessionService`
- `DeviceDiscoveryManager`
- `PermissionsCoordinator`

### `browser-shell` (Android/Kotlin)
Responsibilities:
- Embedded WebView/GeckoView host.
- Media playback UX and source controls.
- Capture compatibility checks.

Primary classes (proposed):
- `BrowserFragment`
- `MediaRouteController`

### `audio-capture` (Android/Kotlin)
Responsibilities:
- AudioPlaybackCapture integration (Android 10+).
- PCM frame normalization (sample rate/channel format).
- Backpressure-safe handoff to JNI.

Primary classes (proposed):
- `PlaybackCaptureEngine`
- `PcmFrameDispatcher`

### `sync-core` (C++ via NDK)
Responsibilities:
- Master ring buffer.
- Per-device reader offsets.
- Drift detection and micro-adjustments.
- Audio quality safeguards (underrun/overrun handling).

Primary components (proposed):
- `MasterRingBuffer`
- `DeviceStreamContext`
- `DriftController`
- `SyncEngineFacade`

### `bt-router` (C++/platform integration)
Responsibilities:
- Parallel output worker abstraction.
- Transport capability probing per device/firmware.
- Encapsulation for future alternate transports.

Primary components (proposed):
- `TransportProbe`
- `OutputWorker`
- `RouterSupervisor`

## 3) Key Data Contracts (Draft)

### PCM frame packet to native
- `timestampNs: long`
- `sampleRateHz: int`
- `channels: int`
- `encoding: PCM16|PCMFloat`
- `payload: byte[]`

### Device calibration state
- `deviceId: String` (MAC alias or stable session id)
- `manualOffsetMs: Int`
- `gainDb: Float`
- `lastMeasuredDriftMs: Float`

### Runtime metrics
- buffer fill level (%), underrun count, overrun count
- per-device effective latency estimate
- correction operations per minute

## 4) Execution Risks + Mitigations

1. **Bluetooth transport limitations differ by OEM/firmware**
   - Mitigation: ship transport probe first; gate unsupported topologies early.
2. **Long-session drift across heterogeneous speaker DSP pipelines**
   - Mitigation: periodic drift measurement + bounded micro-correction.
3. **Foreground/background lifecycle instability**
   - Mitigation: strict service ownership and watchdog-style health checks.
4. **Thermal throttling under heavy media + multi-output load**
   - Mitigation: adaptive quality strategy, instrumentation, and CPU budget alerts.

## 5) Definition of Done (POC Gate)

A test harness can:
- detect two selected target devices,
- initialize parallel output workers,
- emit the same 1-second test signal,
- capture and log relative playback timing estimate,
- produce a pass/fail record against <= 50 ms offset target.
