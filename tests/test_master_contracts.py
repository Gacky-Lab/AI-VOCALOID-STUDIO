"""Machine-readable master schemas must be semantically identical to design.md."""
import json
import re
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MASTER = ("acceptance", "manifest", "reaper_job", "reaper_result",
          "report", "song_ir", "state")


class MasterSchemaTests(unittest.TestCase):
    def test_7_design_schemas_stay_in_sync(self):
        source = (ROOT / "docs/design.md").read_text(encoding="utf-8")
        fence = re.escape(chr(96) * 3)
        for name in MASTER:
            with self.subTest(name=name):
                pattern = (r"^## " + re.escape(name) + r"\.schema\.json\s*\n\s*" +
                           fence + r"json\s*\n(.*?)\n" + fence)
                match = re.search(pattern, source, flags=re.MULTILINE | re.DOTALL)
                self.assertIsNotNone(match, "Source schema section is missing")
                expected = json.loads(match.group(1))
                actual = json.loads((ROOT / "schemas" / (name + ".schema.json")).read_text(encoding="utf-8"))
                self.assertEqual(expected, actual, "Schema drift from master design")
                Draft202012Validator.check_schema(actual)
