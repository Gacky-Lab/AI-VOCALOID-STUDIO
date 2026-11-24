import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_reaper_import import build_lua, lua_literal


def make_wav(path):
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"\x00\x00" * 480)


class ReaperJobTests(unittest.TestCase):
    def test_generates_official_reascript_calls(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            wav = folder / "伴奏.wav"
            make_wav(wav)
            job = {"job_version": "1.0.0", "tracks": [
                {"name": "伴奏", "source_path": "伴奏.wav", "position_seconds": 0.5}
            ]}
            schema = json.loads((ROOT / "schemas/reaper_import_job.v1.schema.json").read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(job)
            f = folder / "job.json"
            f.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
            lua = build_lua(f)
            self.assertIn("reaper.PCM_Source_CreateFromFile", lua)
            self.assertIn("reaper.SetMediaItemTake_Source", lua)
            self.assertIn("reaper.GetMediaSourceLength", lua)
            self.assertIn("position=0.5", lua)
            self.assertIn("伴奏", lua)

    def test_reject_missing_media(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "job.json"
            f.write_text(json.dumps({"job_version": "1.0.0", "tracks": [
                {"name": "Lead", "source_path": "not_there.wav", "position_seconds": 0}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                build_lua(f)

    def test_reject_negative_position_and_unknown_fields(self):
        with tempfile.TemporaryDirectory() as d:
            wav = Path(d) / "audio.wav"; make_wav(wav)
            f = Path(d) / "job.json"
            for entry in [
                {"name": "Lead", "source_path": str(wav), "position_seconds": -1},
                {"name": "Lead", "source_path": str(wav), "position_seconds": 0, "unsafe": True},
            ]:
                f.write_text(json.dumps({"job_version": "1.0.0", "tracks": [entry]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    build_lua(f)

    def test_lua_long_brackets_are_not_injectable(self):
        literal = lua_literal("a]=]b")
        self.assertTrue(literal.startswith("[==["))
        self.assertTrue(literal.endswith("]==]"))
