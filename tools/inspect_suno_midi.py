"""Read-only Suno multi-track MIDI timing and lead-vocal-candidate inspector.

Usage:
  & .\private\vocaloid_bridge\.venv\Scripts\python.exe .\tools\inspect_suno_midi.py "path\to\original.mid"

Uses mido from the existing Vocaloid bridge venv. Prints a JSON report and
writes a copy under ignored output/ without modifying source.
Do not automatically assume a Synth Choir (or another) track is the lead vocal.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
import json
from pathlib import Path
from statistics import median
import sys

try:
    import mido
except ImportError:
    print("ERROR: install the bridge first (mido is included in its venv).", file=sys.stderr)
    raise


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "suno_midi_inventory.json"


def tick_to_seconds_factory(midi):
    changes = [(0, 500000)]
    for track in midi.tracks:
        clock = 0
        for msg in track:
            clock += msg.time
            if msg.type == "set_tempo":
                changes.append((clock, msg.tempo))
    changes.sort(key=lambda item: item[0])
    ticks = [0]
    seconds = [0.0]
    tempos = [500000]
    for tick, tempo in changes:
        if tick == 0:
            tempos[0] = tempo
        elif tick == ticks[-1]:
            tempos[-1] = tempo
        else:
            seconds.append(seconds[-1] + (tick - ticks[-1]) * tempos[-1] / (midi.ticks_per_beat * 1e6))
            ticks.append(tick)
            tempos.append(tempo)

    def convert(tick):
        i = bisect_right(ticks, tick) - 1
        return seconds[i] + (tick - ticks[i]) * tempos[i] / (midi.ticks_per_beat * 1e6)

    return convert, list(zip(ticks, tempos))


def inspect_track(track, index, midi, to_sec):
    tick = 0
    active = {}
    notes = []
    names = []
    programs = []
    channels = set()
    for message in track:
        tick += message.time
        if message.type == "track_name":
            names.append(message.name)
        elif message.type == "program_change":
            programs.append({"program": message.program, "channel": message.channel})
        if not hasattr(message, "channel"):
            continue
        channels.add(message.channel)
        if message.type == "note_on" and message.velocity > 0:
            active.setdefault((message.channel, message.note), []).append((tick, message.velocity))
        elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
            stack = active.get((message.channel, message.note))
            if stack:
                start, velocity = stack.pop(0)
                if tick > start:
                    notes.append({
                        "pitch": message.note,
                        "start_s": round(to_sec(start), 4),
                        "end_s": round(to_sec(tick), 4),
                        "velocity": velocity,
                    })

    notes.sort(key=lambda note: (note["start_s"], note["pitch"]))
    first = [note for note in notes if note["start_s"] < 32]
    pitches = [note["pitch"] for note in notes]
    count_by_32_s = [
        sum(a["start_s"] < end and a["end_s"] > start for a in notes)
        for start, end in [(0, 16), (16, 32), (32, 64), (64, 128)]
    ]
    simultaneous = 0
    events = []
    for note in notes:
        events.extend([(note["start_s"], +1), (note["end_s"], -1)])
    # End a note before starting another on the exact same timestamp.
    events.sort(key=lambda item: (item[0], item[1]))
    level = 0
    for _, delta in events:
        level += delta
        simultaneous = max(simultaneous, level)
    return {
        "track_index": index,
        "name": " / ".join(names) or f"Track {index}",
        "channels": sorted(channels),
        "program_changes": programs[:12],
        "notes": len(notes),
        "unclosed_note_ons": sum(len(v) for v in active.values()),
        "pitch_low": min(pitches) if pitches else None,
        "pitch_high": max(pitches) if pitches else None,
        "pitch_median": median(pitches) if pitches else None,
        "max_simultaneous_notes": simultaneous,
        "first_note_s": notes[0]["start_s"] if notes else None,
        "last_note_end_s": max((n["end_s"] for n in notes), default=None),
        "notes_by_time_window": dict(zip(["0-16", "16-32", "32-64", "64-128"], count_by_32_s)),
        "first_32_s_note_preview": first[:40],
        "warning": (
            "Candidate only: track name/program or monophony does not prove vocal identity."
            if notes else "No note pairs"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("midi_file", help="Suno Studio-exported .mid file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = Path(args.midi_file).expanduser().resolve()
    if not source.is_file():
        print(f"ERROR: MIDI not found: {source}", file=sys.stderr)
        return 2
    if source.suffix.lower() not in (".mid", ".midi"):
        print(f"ERROR: expected .mid or .midi, got {source.suffix}", file=sys.stderr)
        return 3
    midi = mido.MidiFile(str(source))
    to_sec, tempo_changes = tick_to_seconds_factory(midi)
    tracks = [
        inspect_track(track, index, midi, to_sec)
        for index, track in enumerate(midi.tracks)
    ]
    report = {
        "input": str(source),
        "format": midi.type,
        "ticks_per_beat": midi.ticks_per_beat,
        "track_count": len(tracks),
        "tempo_changes": [{"tick": tick, "bpm": round(60_000_000 / tempo, 3)} for tick, tempo in tempo_changes][:100],
        "tracks": tracks,
        "recommendation": (
            "Review the likely lead vocal with Suno separated vocal audio and lyric alignment. "
            "A full band MIDI must not be interpreted as a vocal melody automatically."
        ),
        "source_modified": False,
    }
    destination = args.output.expanduser().resolve()
    if destination == source:
        print("ERROR: report path must not overwrite MIDI source", file=sys.stderr)
        return 4
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "track_count": len(tracks),
        "tracks": [
            {k: t[k] for k in ("track_index", "name", "notes", "pitch_low", "pitch_high", "max_simultaneous_notes", "first_note_s")}
            for t in tracks
        ],
        "report": str(destination),
        "note": "This is an inventory, NOT a verified vocal melody.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
