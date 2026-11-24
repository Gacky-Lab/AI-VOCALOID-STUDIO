"""Offline contract tests: no Suno/VOCALOID/REAPER installation required."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import mido
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from ai_vocaloid.handoff import verify_handoff
from ai_vocaloid.midi_candidates import extract_midi_candidates
from make_phase0_midi import generate


class OfflineTests(unittest.TestCase):
    def test_handoff_and_corruption(self):
        lyrics = "今日は晴れ\n"
        obj = {"contract_version":"1.0.0","song_id":"song1","lyric_version_id":"v1",
               "language":"ja","lyrics_text":lyrics,
               "lyrics_sha256":hashlib.sha256(lyrics.encode("utf-8")).hexdigest()}
        self.assertEqual(verify_handoff(obj)["lyric_version_id"], "v1")
        schema = json.loads((ROOT/"schemas/lyric_handoff.v1.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(obj)
        obj["lyrics_text"] += "改変"
        with self.assertRaises(ValueError):
            verify_handoff(obj)

    def test_handoff_other_song_rejected(self):
        lyrics = "あ"
        obj = {"contract_version":"1.0.0","song_id":"song1","lyric_version_id":"v1",
               "language":"ja","lyrics_text":lyrics,
               "lyrics_sha256":hashlib.sha256(lyrics.encode()).hexdigest()}
        with self.assertRaises(ValueError):
            verify_handoff(obj, "song2")

    def test_three_notes_at_1_6_12_seconds(self):
        with tempfile.TemporaryDirectory() as temp:
            path = generate(Path(temp)/"probe.mid")
            record = extract_midi_candidates(path, "p0", 1)
            self.assertEqual([note["start_sample"] for note in record["notes"]], [48000, 288000, 576000])
            self.assertEqual([note["end_sample"]-note["start_sample"] for note in record["notes"]], [24000]*3)
            self.assertEqual(record["duration_samples"], 720000)
            self.assertEqual(record["alignment_status"], "needs_lyric_and_voice_review")
            self.assertNotIn("moras", record)
            schema = json.loads((ROOT/"schemas/midi_candidates.v1.schema.json").read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(record)

    def test_tempo_change_from_conductor_track(self):
        with tempfile.TemporaryDirectory() as temp:
            midi=mido.MidiFile(type=1, ticks_per_beat=480)
            midi.tracks.append(mido.MidiTrack([
                mido.MetaMessage("set_tempo", tempo=500000, time=0),
                mido.MetaMessage("set_tempo", tempo=1000000, time=480)
            ]))
            midi.tracks.append(mido.MidiTrack([
                mido.Message("note_on", note=64, velocity=90, time=480),
                mido.Message("note_off", note=64, velocity=0, time=480)
            ]))
            path=Path(temp)/"tempo.mid"
            midi.save(str(path))
            notes=extract_midi_candidates(path,"song1",1)["notes"]
            self.assertEqual((notes[0]["start_sample"],notes[0]["end_sample"]),(24000,72000))

    def test_velocity_zero_note_off(self):
        with tempfile.TemporaryDirectory() as temp:
            midi=mido.MidiFile(type=0)
            midi.tracks.append(mido.MidiTrack([
                mido.Message("note_on", note=60, velocity=70, time=0),
                mido.Message("note_on", note=60, velocity=0, time=480)
            ]))
            path=Path(temp)/"m.mid"
            midi.save(str(path))
            self.assertEqual(len(extract_midi_candidates(path,"song1",0)["notes"]),1)

    def test_unmatched_note_off_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            midi=mido.MidiFile(type=0)
            midi.tracks.append(mido.MidiTrack([mido.Message("note_off", note=60, time=100)]))
            path=Path(temp)/"m.mid"
            midi.save(str(path))
            with self.assertRaises(ValueError):
                extract_midi_candidates(path,"song1",0)

    def test_requires_user_selected_lead_track(self):
        with tempfile.TemporaryDirectory() as temp:
            path=generate(Path(temp)/"probe.mid")
            with self.assertRaises(ValueError):
                extract_midi_candidates(path,"song1",0)

    def test_mismatch_lyric_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            path=generate(Path(temp)/"probe.mid")
            with self.assertRaises(ValueError):
                extract_midi_candidates(path,"song1",1,{"song_id":"song2"})

    def test_reject_conflicting_tempo_events(self):
        with tempfile.TemporaryDirectory() as temp:
            midi=mido.MidiFile(type=1)
            midi.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo", tempo=500000, time=0)]))
            midi.tracks.append(mido.MidiTrack([
                mido.MetaMessage("set_tempo", tempo=600000, time=0),
                mido.Message("note_on",note=60,velocity=80,time=10),
                mido.Message("note_off",note=60,time=480)
            ]))
            path=Path(temp)/"m.mid";midi.save(str(path))
            with self.assertRaises(ValueError):
                extract_midi_candidates(path,"song1",1)
