# AFSIM Event Evidence Report

Source: `D:\AFsim\Agent\01_json_to_afsim_main\build\output\eoir_demo_generated.evt`
SHA-256: `9396fa716d941848a65714fdd38afdb6474c72467583a3a63e37c7b06a38cf7e`
Records: `1670`

## Mission Metrics

- Detection attempts: `1638`
- Successful detections: `90`
- Detection success rate: `5.49%`
- Targets detected: `7/9`
- Tracks initiated/dropped: `7/7`
- Open track balance: `0`

## Detected Targets

- `lr_target_01`
- `sr_target_01`
- `sr_target_01a`
- `sr_target_02`
- `sr_target_02_nosee_02`
- `sr_target_03`
- `sr_target_04`

## Verification

Passed: `PASS`

- `PASS` event_minimum:SENSOR_TURNED_ON: expected `2`, actual `2`
- `PASS` event_minimum:SENSOR_DETECTION_ATTEMPT: expected `800`, actual `1638`
- `PASS` event_minimum:SENSOR_TRACK_INITIATED: expected `7`, actual `7`
- `PASS` event_minimum:SENSOR_TRACK_DROPPED: expected `7`, actual `7`
- `PASS` event_minimum:SENSOR_TURNED_OFF: expected `2`, actual `2`
- `PASS` metric_minimum:successful_detections: expected `90`, actual `90`
- `PASS` metric_minimum:unique_targets_attempted: expected `9`, actual `9`
- `PASS` metric_minimum:unique_targets_detected: expected `7`, actual `7`
- `PASS` metric_minimum:tracks_initiated: expected `7`, actual `7`
- `PASS` metric_minimum:tracks_dropped: expected `7`, actual `7`
- `PASS` metric_maximum:open_track_balance: expected `0`, actual `0`
- `PASS` target_must_be_detected:sr_target_01: expected `True`, actual `True`
- `PASS` target_must_be_detected:sr_target_01a: expected `True`, actual `True`
- `PASS` target_must_be_detected:sr_target_02: expected `True`, actual `True`
- `PASS` target_must_be_detected:sr_target_03: expected `True`, actual `True`
- `PASS` target_must_be_detected:sr_target_04: expected `True`, actual `True`
- `PASS` target_must_be_detected:lr_target_01: expected `True`, actual `True`
- `PASS` target_must_not_be_detected:sr_target_05_no_see: expected `False`, actual `False`

## Failure Reasons

- `Rcvr_Angle_Limits_Exceeded`: 1555
- `Rcvr_Noise`: 97
