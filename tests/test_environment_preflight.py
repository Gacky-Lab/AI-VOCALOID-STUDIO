"""No machine scan during tests; simulated snapshots only."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from environment_preflight import classify_host


class PreflightTests(unittest.TestCase):
    def snapshot(self):
        return {"os_name": "Windows", "os_release": "11", "cpu_description": "Intel Core i7",
                "architecture": "AMD64", "memory_gib": 16.0, "free_disk_gib": 70.0,
                "reaper_on_path": False}

    def test_hardware_is_not_voice_success(self):
        result = classify_host(self.snapshot())
        self.assertEqual(result["memory"], "MAY_MEET_MINIMUM")
        self.assertEqual(result["actual_voice_render"], "NOT_RUN")
        self.assertEqual(result["actual_reaper_import"], "NOT_RUN")
        self.assertEqual(result["reaper_path"], "UNKNOWN_NOT_ON_PATH")

    def test_amd_requires_specific_confirmation_not_automatic_rejection(self):
        snap = self.snapshot()
        snap["cpu_description"] = "AMD Ryzen 7"
        self.assertEqual(classify_host(snap)["cpu"], "COMPATIBILITY_REVIEW_REQUIRED")

    def test_insufficient_memory_and_disk(self):
        snap = self.snapshot()
        snap["memory_gib"], snap["free_disk_gib"] = 4, 7
        result = classify_host(snap)
        self.assertEqual(result["memory"], "BELOW_MINIMUM")
        self.assertEqual(result["free_disk"], "BELOW_MINIMUM")

    def test_nonwindows_does_not_claim_v6_supported(self):
        snap = self.snapshot()
        snap["os_name"], snap["os_release"] = "Linux", "6.7"
        self.assertEqual(classify_host(snap)["os"], "REVIEW_REQUIRED")

    def test_unknown_memory_is_unknown_not_zero(self):
        snap = self.snapshot()
        snap["memory_gib"] = None
        self.assertEqual(classify_host(snap)["memory"], "UNKNOWN")

    def test_schema_drift_detected(self):
        snap = self.snapshot()
        snap["editor_licensed"] = True
        with self.assertRaises(ValueError):
            classify_host(snap)
