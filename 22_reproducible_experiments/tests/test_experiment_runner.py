import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import experiment_runner


class ExperimentTests(unittest.TestCase):
    def test_random_seed_is_rendered_in_afsim_main(self):
        scenario = experiment_runner.build_scenario(45000, 13579, "test_run")
        self.assertEqual(experiment_runner.afsim_ai.validate_scenario(scenario), [])
        platform_types = experiment_runner.afsim_ai.load_platform_types(scenario)
        main = experiment_runner.afsim_ai.render_main(scenario, platform_types, "scenario_generated.txt")
        self.assertIn("random_seed 13579", main)

    def test_aggregate_computes_mean_and_sample_stdev(self):
        spec = {"factor": {"values": [30000]}, "metrics": ["successful_detections"]}
        records = [
            {"altitude_ft": 30000, "passed": True, "successful_detections": 8},
            {"altitude_ft": 30000, "passed": True, "successful_detections": 10},
            {"altitude_ft": 30000, "passed": True, "successful_detections": 12},
        ]
        group = experiment_runner.aggregate(records, spec)[0]
        self.assertEqual(group["successful_detections"]["mean"], 10.0)
        self.assertEqual(group["successful_detections"]["sample_stdev"], 2.0)


if __name__ == "__main__":
    unittest.main()
