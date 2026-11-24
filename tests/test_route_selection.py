"""Route matrix regression tests; NO real device/proprietary software access."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from select_interface_routes import evaluate

CATALOG = json.loads((ROOT / "config/interface_routes.v1.json").read_text(encoding="utf-8"))


class RouteSelectionTests(unittest.TestCase):
    def test_offline_demo_does_not_pretend_to_render(self):
        p = json.loads((ROOT / "examples/interface_profiles/offline_demo.json").read_text(encoding="utf-8"))
        result = evaluate(CATALOG, p)
        self.assertEqual(result["stages"]["source"]["selected"], "synthetic_phase0")
        self.assertEqual(result["stages"]["notes"]["selected"], "mido_midi_candidates")
        self.assertEqual(result["stages"]["render"]["state"], "BLOCKED")
        self.assertEqual(result["actual_windows_acceptance"], "NOT_RUN")

    def test_zero_evidence_blocks_every_production_stage(self):
        p = {"mode": "production", "asserted_true": []}
        result = evaluate(CATALOG, p)
        self.assertTrue(all(s["state"] == "BLOCKED" for s in result["stages"].values()))
        self.assertEqual(result["end_to_end_state"], "NOT_READY")

    def test_lite_prefers_standalone_not_mcp_or_vst3(self):
        p = json.loads((ROOT / "examples/interface_profiles/hypothetical_lite.json").read_text(encoding="utf-8"))
        result = evaluate(CATALOG, p)
        self.assertEqual(result["stages"]["render"]["selected"], "v6_lite_manual")
        self.assertEqual(result["end_to_end_state"], "CONDITIONAL_NEEDS_REAL_EVIDENCE")
        self.assertTrue(result["assertions_are_unverified"])
        self.assertIn("v6_lite_vst3", [r["id"] for r in CATALOG["excluded"]])
        self.assertNotIn("v6_lite_vst3", [r["id"] for r in CATALOG["routes"]])

    def test_unattended_mcp_requires_independent_render_evidence(self):
        p = json.loads((ROOT / "examples/interface_profiles/hypothetical_lite.json").read_text(encoding="utf-8"))
        p["asserted_true"] = [x for x in p["asserted_true"] if x != "v6_lite_editor_ready"]
        p["asserted_true"] += ["v6_full_editor_ready"]
        result = evaluate(CATALOG, p)
        self.assertEqual(result["stages"]["render"]["selected"], "v6_full_manual")
        p["asserted_true"] += ["mcp_schema_pinned", "three_independent_renders_passed"]
        result = evaluate(CATALOG, p)
        self.assertEqual(result["stages"]["render"]["selected"], "v6_mcp_unattended")
        self.assertEqual(result["actual_windows_acceptance"], "NOT_RUN")

    def test_lite_prohibited_vst3_and_all_external_options_are_sourced(self):
        self.assertTrue(any("VST3" in r["reason"] for r in CATALOG["excluded"]))
        self.assertTrue(all(r["source"].startswith("https://") for r in CATALOG["routes"]))

    def test_reject_unknown_claim(self):
        with self.assertRaises(ValueError):
            evaluate(CATALOG, {"mode": "production", "asserted_true": ["claimed_success_without_evidence"]})

    def test_profile_inputs_are_scenarios(self):
        self.assertTrue(all(
            evaluate(CATALOG, json.loads(path.read_text(encoding="utf-8")))["actual_windows_acceptance"] == "NOT_RUN"
            for path in (ROOT / "examples/interface_profiles").glob("*.json")
        ))

    def test_external_requirements_never_implicitly_true(self):
        result = evaluate(CATALOG, {"mode": "production", "asserted_true": ["mido_available"]})
        self.assertIsNone(result["stages"]["notes"]["selected"])
        self.assertIn("midi_file_inspected", result["stages"]["notes"]["options"][0]["missing"])


if __name__ == "__main__":
    unittest.main()
