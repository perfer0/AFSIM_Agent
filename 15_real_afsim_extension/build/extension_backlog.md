# Step 15 Real AFSIM Extension Backlog

Generated at: 2026-07-10T15:53:17
AFSIM demos root: `D:\AFsim\AFSim\afsim-2.9.0-win64\demos`
Passed: True

## Extension Order

1. Radar search/track: use radar demos to build a minimal radar component set.
2. Communications link: extract sender/receiver and message routing examples.
3. Weapon engagement: only after radar track generation is stable.
4. Electronic warfare: only after radar and RF snippets are understood.

## Demo Evidence

### radar

- score=71 `electronic_warfare\jam_strobe_tracking.txt`
- score=67 `air_to_air\sensor_observer.txt`
- score=47 `base_types\sensors\radar\generic_fire_control_radar.txt`
- score=46 `air_to_air\processors\sensor_cue_processor.txt`
- score=43 `sensor_demos\passive_detector_df_demo.txt`

### communications

- score=30 `space_operations\lasercomm_scripted.txt`
- score=21 `space_operations\scripts\comm_link.txt`
- score=15 `multiresolution_demos\comm_demo.txt`
- score=13 `electronic_warfare\comm_jamming.txt`
- score=13 `satellite_demos\TLE\x-comm_platforms.txt`

### weapon

- score=81 `base_types\processors\quantum_agents\aiww\behavior_buddy_engage_weapon_task_target.txt`
- score=69 `air_to_air\weapons\aam\mrm_launch_computer_results.1.1.txt`
- score=65 `air_to_air\weapons\aam\srm_launch_computer_results.1.1.txt`
- score=54 `base_types\processors\timeline_agents\weapon_defs.txt`
- score=45 `base_types\weapons\aam\simple_blue_lr_a2a_rf_missile_air_to_air_launch_computer_table.txt`

### electronic_warfare

- score=32 `base_types\processors\ripr_agents\aijam\aijam_processor.txt`
- score=24 `electronic_warfare\semi-auto_repeater_jamming_1.txt`
- score=20 `electronic_warfare\agile_repeater_jamming-rt1.txt`
- score=20 `electronic_warfare\agile_repeater_jamming-rt2.txt`
- score=20 `electronic_warfare\agile_repeater_jamming.txt`

### multi_platform

- score=5 `orwaca_iads\orwaca_northern_area.txt`
- score=4 `aea_iads\iads-rt.txt`
- score=4 `aea_iads\setup.txt`
- score=4 `electronic_warfare\test_false_targets\platforms\iads_cmdr.txt`
- score=4 `iads\iads-rt.txt`
