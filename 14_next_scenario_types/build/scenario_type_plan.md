# Step 14 Next Scenario Types

Generated at: 2026-07-10T15:50:38

## Baseline

EOIR reconnaissance with UAV, ground targets, sensor event output, local Ollama JSON drafting, Agent validation, and mission.exe verification.

## Recommended Next

Next scenario type: **雷达搜索与跟踪**

Reason: priority=2, risk=medium, score=6

## Scenario Matrix

### EOIR 侦察

- id: `eoir_recon`
- status: `implemented_baseline`
- risk: `low`
- readiness_score: `19`
- next_action: Keep as regression scenario for every future extension.
- required_components: uav_eoir, ground_site, eoir_sensor_events

### 雷达搜索与跟踪

- id: `radar_search_track`
- status: `planned`
- risk: `medium`
- readiness_score: `6`
- next_action: Scan AFSIM demos for radar platform and sensor event patterns.
- required_components: airborne_radar_platform, radar_sensor, radar_event_outputs, track_targets

### 通信链路

- id: `communications_link`
- status: `planned`
- risk: `medium`
- readiness_score: `5`
- next_action: Find AFSIM comm demos and extract minimal sender/receiver script.
- required_components: sender_platform, receiver_platform, comm_processor, comm_event_outputs

### 多平台协同

- id: `multi_platform_coordination`
- status: `planned`
- risk: `medium`
- readiness_score: `2`
- next_action: Use EOIR baseline and add a second UAV after radar/comm components exist.
- required_components: multiple_blue_platforms, target_set, coordination_timeline

### 武器交战

- id: `weapon_engagement`
- status: `planned`
- risk: `high`
- readiness_score: `1`
- next_action: Defer until radar/track scenario is stable.
- required_components: shooter, target, weapon, weapon_event_outputs

### 电子战/干扰

- id: `electronic_warfare`
- status: `planned`
- risk: `high`
- readiness_score: `0`
- next_action: Build only after radar scenario and RF snippets are understood.
- required_components: jammer, victim_sensor, emitter, ew_event_outputs
