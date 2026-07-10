import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = ROOT / "07_agent_loop"
STEP_DIR = ROOT / "19_engineering_baseline"
sys.path.insert(0, str(AGENT_DIR))
sys.path.insert(0, str(STEP_DIR))

import afsim_ai
import agent_loop
import engineering_benchmark


class ScenarioValidationTests(unittest.TestCase):
    def setUp(self):
        self.scenario = afsim_ai.local_rule_draft()

    def test_rule_draft_is_valid(self):
        self.assertEqual(afsim_ai.validate_scenario(self.scenario), [])

    def test_event_pipe_requires_aer_and_distinct_file(self):
        self.scenario["event_pipe"]["file"] = self.scenario["event_output"]["file"]
        errors = afsim_ai.validate_scenario(self.scenario)
        self.assertTrue(any("output/*.aer" in error for error in errors))
        self.assertTrue(any("must be different" in error for error in errors))

    def test_execute_script_rejects_combined_or_single_quote_commands(self):
        self.scenario["actors"][0]["execute"][0]["script"] = "BeginImaging('eoir', '', -90, 68000); EndImaging();"
        errors = afsim_ai.validate_scenario(self.scenario)
        self.assertTrue(any("one allowed BeginImaging or EndImaging" in error for error in errors))


class SemanticGateTests(unittest.TestCase):
    def setUp(self):
        self.scenario = afsim_ai.local_rule_draft()

    def test_parameter_fidelity_passes_for_matching_values(self):
        expected = {
            "required_platform_refs": ["uav_eoir", "ground_site"],
            "required_target_refs": ["eoir_short_long_targets"],
            "event_set_ref": "eoir_sensor_events",
            "position_contains": ["34:30:00n 116:00w"],
            "route_contains": ["60000 ft", "350 kts", "0 deg"],
            "script_contains": ["BeginImaging", "EndImaging"],
            "minimum_execute_count": 4,
            "maximum_end_minutes": 20,
        }
        checks = engineering_benchmark.semantic_checks(self.scenario, expected)
        self.assertTrue(all(item["passed"] for item in checks))

    def test_missing_three_windows_fails(self):
        expected = {
            "required_platform_refs": ["uav_eoir", "ground_site"],
            "required_target_refs": ["eoir_short_long_targets"],
            "event_set_ref": "eoir_sensor_events",
            "minimum_begin_imaging_count": 3,
            "minimum_end_imaging_count": 3,
            "minimum_execute_count": 6,
        }
        checks = {item["name"]: item["passed"] for item in engineering_benchmark.semantic_checks(self.scenario, expected)}
        self.assertFalse(checks["minimum_begin_imaging_count"])
        self.assertFalse(checks["minimum_end_imaging_count"])
        self.assertFalse(checks["minimum_execute_count"])


class ConfigurationTests(unittest.TestCase):
    def test_production_and_smoke_models_are_separate(self):
        config = engineering_benchmark.load_json(engineering_benchmark.CONFIG_PATH)
        self.assertEqual(config["models"]["production_baseline"], "qwen2.5:7b")
        self.assertEqual(config["models"]["smoke_test"], "qwen2.5:0.5b")
        self.assertNotEqual(config["models"]["production_baseline"], config["models"]["smoke_test"])
        self.assertFalse(config["generation"]["allow_rules_fallback_in_acceptance"])
        self.assertGreater(config["generation"]["case_timeout_seconds"], 0)


class ScopeGateTests(unittest.TestCase):
    def test_eoir_request_is_allowed(self):
        self.assertEqual(agent_loop.validate_request_scope("生成 EOIR 无人机侦察想定"), [])

    def test_radar_request_is_rejected(self):
        errors = agent_loop.validate_request_scope("生成雷达搜索跟踪想定")
        self.assertEqual(len(errors), 1)
        self.assertIn("radar", errors[0])

    def test_empty_request_is_rejected(self):
        self.assertEqual(agent_loop.validate_request_scope("  "), ["request is empty"])


if __name__ == "__main__":
    unittest.main()
