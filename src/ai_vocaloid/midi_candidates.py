"""Offline SMF -> 48 kHz MIDI candidates, explicitly NOT lyric-aligned Song IR."""
from collections import defaultdict, deque
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import re
import mido

SAMPLE_RATE = 48000


def _maps(midi):
    tempo, meter = {0: 500000}, {0: (4, 4)}
    explicit_tempo, explicit_meter = {}, {}
    for track in midi.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == "set_tempo":
                if msg.tempo <= 0 or (tick in explicit_tempo and explicit_tempo[tick] != msg.tempo):
                    raise ValueError("contradictory MIDI tempo events")
                explicit_tempo[tick] = msg.tempo
                tempo[tick] = msg.tempo
            if msg.type == "time_signature":
                pair = (msg.numerator, msg.denominator)
                if tick in explicit_meter and explicit_meter[tick] != pair:
                    raise ValueError("contradictory MIDI meter events")
                explicit_meter[tick] = pair
                meter[tick] = pair
    return sorted(tempo.items()), sorted(meter.items())


def _sample_at_tick(tempo_map, ppq):
    segments = []
    sample = Fraction(0)
    last_tick = 0
    last_tempo = tempo_map[0][1]
    for tick, tempo in tempo_map:
        sample += Fraction((tick - last_tick) * last_tempo * SAMPLE_RATE, ppq * 1000000)
        segments.append((tick, sample, tempo))
        last_tick, last_tempo = tick, tempo

    def convert(tick):
        origin = segments[0]
        for entry in segments:
            if entry[0] > tick:
                break
            origin = entry
        value = origin[1] + Fraction((tick - origin[0]) * origin[2] * SAMPLE_RATE, ppq * 1000000)
        return int(value + Fraction(1, 2))

    return convert


def extract_midi_candidates(filename, song_id, track_index, lyric_reference=None):
    path = Path(filename)
    if not path.is_file():
        raise ValueError("MIDI file not found")
    if not isinstance(song_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", song_id):
        raise ValueError("invalid song_id")
    midi = mido.MidiFile(str(path))
    if midi.type == 2 or midi.ticks_per_beat <= 0:
        raise ValueError("SMPTE and asynchronous type-2 SMF are unsupported")
    if not isinstance(track_index, int) or not 0 <= track_index < len(midi.tracks):
        raise ValueError("track_index out of range")
    tempo_map, meter_map = _maps(midi)
    sample_at = _sample_at_tick(tempo_map, midi.ticks_per_beat)
    held = defaultdict(deque)
    notes = []
    tick = 0
    for msg in midi.tracks[track_index]:
        tick += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            held[(msg.channel, msg.note)].append((tick, msg.velocity))
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            key = (msg.channel, msg.note)
            if not held[key]:
                raise ValueError("unmatched note_off")
            on_tick, velocity = held[key].popleft()
            start, end = sample_at(on_tick), sample_at(tick)
            if end <= start:
                raise ValueError("note length must be positive after sample rounding")
            notes.append({"pitch_midi": msg.note, "channel": msg.channel, "velocity": velocity,
                          "start_tick": on_tick, "end_tick": tick, "start_sample": start, "end_sample": end})
    if any(queue for queue in held.values()):
        raise ValueError("unmatched note_on")
    if not notes:
        raise ValueError("selected track has no complete MIDI notes")
    notes.sort(key=lambda n: (n["start_tick"], n["channel"], n["pitch_midi"], n["end_tick"]))
    for i, note in enumerate(notes, 1):
        note["id"] = f"n{i:04d}"
    last_tick = max(sum(message.time for message in track) for track in midi.tracks)
    result = {
        "candidate_contract_version": "0.1.0", "alignment_status": "needs_lyric_and_voice_review",
        "song_id": song_id, "source_midi_sha256": sha256(path.read_bytes()).hexdigest(),
        "sample_rate_hz": SAMPLE_RATE, "ppq": midi.ticks_per_beat,
        "selected_track_index": track_index,
        "duration_samples": max(sample_at(last_tick), max(n["end_sample"] for n in notes)),
        "tempo_map": [{"tick": tick, "microseconds_per_quarter": value} for tick, value in tempo_map],
        "meter_map": [{"tick": tick, "numerator": num, "denominator": den} for tick, (num, den) in meter_map],
        "notes": notes,
    }
    if lyric_reference is not None:
        if lyric_reference["song_id"] != song_id:
            raise ValueError("lyric handoff song_id mismatch")
        result["lyric_reference"] = lyric_reference
    return result
