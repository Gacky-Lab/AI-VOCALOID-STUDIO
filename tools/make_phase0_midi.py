#!/usr/bin/env python3
"""Generate a 15-second synthetic MIDI timing fixture; no singing voice."""
import argparse
from pathlib import Path
import mido


def generate(path):
    midi = mido.MidiFile(type=1, ticks_per_beat=480)
    conductor = mido.MidiTrack([
        mido.MetaMessage("set_tempo", tempo=500000, time=0),
        mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0),
        mido.MetaMessage("end_of_track", time=14400),
    ])
    lead = mido.MidiTrack()
    last = 0
    for tick, pitch in ((960, 60), (5760, 64), (11520, 67)):
        lead.append(mido.Message("note_on", note=pitch, velocity=90, time=tick - last))
        lead.append(mido.Message("note_off", note=pitch, velocity=0, time=480))
        last = tick + 480
    lead.append(mido.MetaMessage("end_of_track", time=14400 - last))
    midi.tracks.extend([conductor, lead])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    midi.save(str(path))
    return path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print("Synthetic 15s SMF generated:", generate(args.output))
