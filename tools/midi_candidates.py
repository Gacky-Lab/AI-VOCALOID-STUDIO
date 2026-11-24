#!/usr/bin/env python3
"""Convert one selected MIDI track to REVIEW-ONLY candidates."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ai_vocaloid.handoff import read_handoff
from ai_vocaloid.midi_candidates import extract_midi_candidates


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--midi", required=True, type=Path)
    p.add_argument("--song-id", required=True)
    p.add_argument("--track-index", required=True, type=int)
    p.add_argument("--lyric-handoff", type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    try:
        ref = read_handoff(a.lyric_handoff, a.song_id) if a.lyric_handoff else None
        result = extract_midi_candidates(a.midi, a.song_id, a.track_index, ref)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Saved review-only MIDI candidates:", a.output)
        return 0
    except (ValueError, OSError, EOFError, json.JSONDecodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
