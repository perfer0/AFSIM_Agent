# Step 15 Real AFSIM Extension Backlog

Generated at: 2026-07-10T15:55:54
AFSIM demos root: `D:\AFsim\AFSim\afsim-2.9.0-win64\demos`
Passed: True

## Extension Order

1. Radar search/track: use radar demos to build a minimal radar component set.
2. Communications link: extract sender/receiver and message routing examples.
3. Weapon engagement: only after radar track generation is stable.
4. Electronic warfare: only after radar and RF snippets are understood.

## Demo Evidence

### radar

- score=129 `air_to_air\prdata\rules_utils.txt`
- score=129 `base_types\processors\ripr_agents\aiss\aiss_processor.txt`
- score=75 `air_to_air\rules\shoot_it.txt`
- score=71 `air_to_air\sensor_observer.txt`
- score=71 `electronic_warfare\jam_strobe_tracking.txt`

### communications

- score=1440 `space_operations\scenarios\starlink_autogen.txt`
- score=133 `satellite_demos\satellites\orbit_nominal\iridium.txt`
- score=133 `space_operations\scenarios\iridium.txt`
- score=73 `satellite_demos\platforms\satellite_based_navigation_system.txt`
- score=67 `space_operations\scenarios\iridium_constellation.txt`

### weapon

- score=2652 `base_types\weapons\aam\test_medium_range_missile_air_to_air_launch_computer_table.txt`
- score=1770 `base_types\weapons\aam\simple_blue_lr_a2a_rf_missile_air_to_air_launch_computer_table.txt`
- score=489 `behavior_tree\weapons\aam\launch_computer_simple_mrm_table.txt`
- score=115 `air_to_air\weapons\aam\mrm_launch_computer_results.1.1.txt`
- score=115 `air_to_air\weapons\aam\srm_launch_computer_results.1.1.txt`

### electronic_warfare

- score=34 `base_types\processors\ripr_agents\aijam\aijam_processor.txt`
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
