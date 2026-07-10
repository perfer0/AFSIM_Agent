import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(ROOT))

import event_evidence


PROFILE = {
    "name": "test",
    "version": 1,
    "event_minimums": {
        "SENSOR_TURNED_ON": 1,
        "SENSOR_DETECTION_ATTEMPT": 1,
        "SENSOR_TRACK_INITIATED": 1,
        "SENSOR_TURNED_OFF": 1,
    },
    "metric_minimums": {
        "successful_detections": 1,
        "unique_targets_detected": 1,
    },
    "metric_maximums": {"open_track_balance": 0},
    "required_detected_targets": ["target_01"],
}


class EventParserTests(unittest.TestCase):
    def test_multiline_detection_record_is_parsed(self):
        records = event_evidence.parse_records(FIXTURES / "eoir_success.evt")
        self.assertEqual(len(records), 5)
        attempt = records[1]
        self.assertEqual(attempt["event"], "SENSOR_DETECTION_ATTEMPT")
        self.assertEqual(attempt["target"], "target_01")
        self.assertTrue(attempt["detected"])
        self.assertEqual(attempt["range_km"], 10.5)

    def test_success_metrics_and_profile_pass(self):
        summary = event_evidence.summarize(FIXTURES / "eoir_success.evt")
        self.assertEqual(summary["metrics"]["successful_detections"], 1)
        self.assertEqual(summary["metrics"]["open_track_balance"], 0)
        self.assertEqual(summary["detected_targets"], ["target_01"])
        self.assertTrue(event_evidence.verify(summary, PROFILE)["passed"])

    def test_failure_profile_is_rejected_with_reason(self):
        summary = event_evidence.summarize(FIXTURES / "eoir_failure.evt")
        verification = event_evidence.verify(summary, PROFILE)
        self.assertFalse(verification["passed"])
        self.assertEqual(summary["failure_reasons"]["Rcvr_Angle_Limits_Exceeded"], 1)
        self.assertEqual(summary["failure_reasons"]["Rcvr_Masked_By_Horizon"], 1)
        self.assertEqual(summary["metrics"]["successful_detections"], 0)


if __name__ == "__main__":
    unittest.main()
