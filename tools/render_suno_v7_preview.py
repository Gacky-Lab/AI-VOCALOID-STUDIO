"""Render an APPROXIMATE asa singing preview of a specific Suno track.

This is a Windows-only native MCP client, NOT a full-song/verified melody
transcription. A Synth Choir MIDI part is a candidate, not proven lead vocals.
The opening word-level Suno alignment has manually checked kana readings;
its pitch association is heuristic. The script refuses missing candidate notes.

Usage (from repo root, with bridge venv Python):
    python tools/render_suno_v7_preview.py --midi-url "TEMPORARY_SIGNED_SUNO_MIDI_URL"
or: python tools/render_suno_v7_preview.py --midi "path/to/export.mid"

The user has already authorized rendering. No Suno credits are charged by
this script. It only downloads the existing MIDI (if --midi-url is given).
All outputs go to ignored output/suno_v7_previews/, never overwrite sources.
"""

from __future__ import annotations

import argparse
import asyncio
from bisect import bisect_right
from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from urllib.request import Request, urlopen

import mido
import numpy as np
import soundfile as sf
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


REPO = Path(__file__).resolve().parents[1]
BRIDGE = REPO / "private" / "vocaloid_bridge"
OUTROOT = REPO / "output" / "suno_v7_previews"
SONG_ID = "f60cd638-8c59-428c-97c2-1eabd86b6a76"
SINGER_COMP_ID = "BXHPECHANDRW3XEL"

# Only the intro, aligned by Suno MCP's audio_lyrics_alignment tool.
# Readings are reviewed for this passage only. A small 'っ' is not a
# separate note; omit it and record that approximation explicitly.
WORDS = [
    (0.908, 2.400, "きのう"),
    (2.432, 2.975, "と"),
    (3.106, 3.879, "おなじ"),
    (4.054, 4.898, "そら"),
    (4.898, 5.138, "だった"),
    (5.400, 5.480, "ぼく"),
    (6.426, 6.666, "だけが"),
    (7.652, 7.982, "すこし"),
    (7.982, 8.970, "ちが"),
    (8.970, 9.426, "っていた"),
]
SMALL_SUFFIX = set("ゃゅょぁぃぅぇぉゎ")


def moras(kana):
    result = []
    dropped_sokuon = 0
    for ch in kana:
        if ch == "っ":
            dropped_sokuon += 1
        elif ch in SMALL_SUFFIX and result:
            result[-1] += ch
        else:
            result.append(ch)
    return result, dropped_sokuon


def tick_map(midi):
    changes = []
    for track in midi.tracks:
        pos = 0
        for msg in track:
            pos += msg.time
            if msg.type == "set_tempo":
                changes.append((pos, msg.tempo))
    changes.sort()
    positions = [0]
    secs = [0.0]
    tempos = [500000]
    for tick, tempo in changes:
        if tick == positions[-1]:
            tempos[-1] = tempo
        elif tick > positions[-1]:
            secs.append(secs[-1] + (tick - positions[-1]) * tempos[-1] / (midi.ticks_per_beat * 1e6))
            positions.append(tick)
            tempos.append(tempo)

    def at(tick):
        idx = bisect_right(positions, tick) - 1
        return secs[idx] + (tick - positions[idx]) * tempos[idx] / (midi.ticks_per_beat * 1e6)
    return at, positions, tempos


def extract_instruments(midi, to_seconds):
    tracks = []
    for index, track in enumerate(midi.tracks):
        tick = 0
        programs = defaultdict(lambda: -1)
        pending = defaultdict(deque)
        names = []
        notes = []
        for message in track:
            tick += message.time
            if message.type == "track_name":
                names.append(message.name)
            if not hasattr(message, "channel"):
                continue
            channel = message.channel
            if message.type == "program_change":
                programs[channel] = message.program
            if message.type == "note_on" and message.velocity > 0:
                pending[(channel, message.note)].append((tick, programs[channel]))
            elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
                if pending[(channel, message.note)]:
                    start_tick, program = pending[(channel, message.note)].popleft()
                    if tick > start_tick:
                        notes.append({
                            "start": to_seconds(start_tick),
                            "end": to_seconds(tick),
                            "pitch": message.note,
                            "program": program,
                            "channel": channel,
                        })
        tracks.append({
            "index": index,
            "name": "/".join(names),
            "notes": notes,
            "all_count": len(notes),
        })
    return tracks


def candidate_notes(tracks):
    found = []
    for track in tracks:
        name = track["name"].lower()
        choir = [n for n in track["notes"] if n["program"] == 54]
        if not choir and ("synth choir" in name or "voice" in name or "vocal" in name):
            choir = track["notes"]
        intro = [n for n in choir if n["start"] < 10 and n["end"] > 0.6 and 48 <= n["pitch"] <= 91]
        if intro:
            found.append((len(intro), track["index"], intro, len(choir)))
    if not found:
        raise RuntimeError(
            "Cannot identify Synth Choir/voice MIDI notes in first 10s; "
            "stop instead of replacing the lead vocal with another instrument."
        )
    # Select the greatest early note coverage. This is ONLY a vocal candidate.
    count, index, notes, total = max(found, key=lambda obj: obj[0])
    return index, notes, count, total


def build_notes(intro_notes, bpm):
    out = []
    details = []
    dropped = 0
    starts = []
    for start, end, reading in WORDS:
        syllables, small_tsus = moras(reading)
        dropped += small_tsus
        for i, syllable in enumerate(syllables):
            t0 = start + (end - start) * i / len(syllables)
            t1 = start + (end - start) * (i + 1) / len(syllables)
            midpoint = (t0 + t1) / 2
            overlapping = [
                n for n in intro_notes if n["start"] <= midpoint < n["end"]
            ]
            if overlapping:
                choice = max(overlapping, key=lambda n: (n["pitch"], -abs(n["start"] - midpoint)))
                gap = 0
            else:
                choice = min(intro_notes, key=lambda n:
                             min(abs(n["start"] - midpoint), abs(n["end"] - midpoint)))
                gap = min(abs(choice["start"] - midpoint), abs(choice["end"] - midpoint))
                if gap > 0.75:
                    raise RuntimeError(f"No choir pitch within 0.75s of lyric {syllable!r} at {midpoint:.2f}s")
            pos = round(t0 * bpm / 60, 5)
            duration = round(max((t1 - t0) * bpm / 60, 0.035), 5)
            # Tiny overlap for adjacent words is rejected by score_compose;
            # the timestamps are non-overlapping here.
            out.append({"start": pos, "duration": duration,
                        "pitch": choice["pitch"], "lyric": syllable, "lang_id": 0})
            details.append({"lyric": syllable, "time_s": round(t0, 3),
                            "pitch": choice["pitch"], "midi_gap_s": round(gap, 3)})
            starts.append(t0)
    return out, details, dropped


def download_existing_midi(url, dest):
    if not url.lower().startswith("https://"):
        raise ValueError("Only HTTPS MIDI download URLs are accepted")
    if not url.split("?", 1)[0].lower().endswith(".mid"):
        raise ValueError("URL must point to a .mid file")
    host = __import__("urllib.parse", fromlist=["urlparse"]).urlparse(url).hostname
    if host != "suno-data-uploads.s3.amazonaws.com":
        raise ValueError("Unexpected MIDI host; use the official Suno MIDI download URL")
    request = Request(url, headers={"User-Agent": "AI-VOCALOID-STUDIO/1.0"})
    with urlopen(request, timeout=60) as response:
        with dest.open("xb") as handle:
            shutil.copyfileobj(response, handle)
    if dest.stat().st_size < 100 or dest.read_bytes()[:4] != b"MThd":
        raise ValueError("Downloaded file is not an expected standard MIDI file")


def unpack(result):
    if result.isError:
        raise RuntimeError("MCP error: " + repr(result.content)[:1500])
    if result.structuredContent is not None:
        return result.structuredContent
    blocks = [getattr(item, "text", "") for item in result.content]
    if len(blocks) == 1:
        return json.loads(blocks[0])
    raise RuntimeError("MCP tool response did not return parseable JSON")


async def run_mcp(score, bpm, name, destination):
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "vocaloid_bridge"],
        cwd=str(BRIDGE),
        env={**os.environ, "VOCALOID_WORKSPACE": str(BRIDGE),
             "PYTHONPATH": str(BRIDGE), "PYTHONUTF8": "1"},
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as client:
            await client.initialize()
            tools = {tool.name for tool in (await client.list_tools()).tools}
            required = {"vocaloid_status", "voicebanks", "vocaloid_workflow", "score_compose",
                        "project_ai_adjust", "project_audio", "project_save", "project_close"}
            if not required.issubset(tools):
                raise RuntimeError(f"Required tools missing: {sorted(required-tools)}")

            async def call(tool, **kwargs):
                return unpack(await client.call_tool(tool, kwargs))

            status = await call("vocaloid_status")
            voices = await call("voicebanks")
            await call("vocaloid_workflow")
            if status.get("product") != "VOCALOID7" or status.get("version") != "7.0.1.1":
                raise RuntimeError("Installed version differs from recorded 7.0.1.1; manual review")
            installed = voices.get("voices", [])
            if not any(v.get("comp_id") == SINGER_COMP_ID and v.get("synthesizable_version") for v in installed):
                raise RuntimeError("asa voicebank is not synthesizable/installed")

            composed = await call(
                "score_compose", output_name=name + "_draft.vpr", title="Suno intro asa approximate",
                bpm=bpm, notes=score, voice_comp_id=SINGER_COMP_ID
            )
            session = composed.get("native_session", {}).get("session_id")
            if not session:
                raise RuntimeError(f"score_compose returned no session: {str(composed)[:1500]}")
            try:
                adjusted = await call("project_ai_adjust", session_id=session,
                                      track_index=0, part_index=0)
                mixed = await call("project_audio", session_id=session,
                                   operation="mixdown", options={
                                       "output_name": name + "_asa.wav", "sample_rate": 44100,
                                       "bits_per_sample": 16, "channels": 1,
                                   })
                saved = await call("project_save", session_id=session,
                                   output_name=name + "_asa.vprx")
            finally:
                await call("project_close", session_id=session)

    wav = (BRIDGE / "output" / (name + "_asa.wav"))
    vpr = Path(saved.get("path", BRIDGE / "output" / (name + "_asa.vprx")))
    if not wav.is_file():
        raise RuntimeError(f"Mixdown reports success but WAV not found at {wav}: {mixed}")
    if not vpr.is_file():
        raise RuntimeError(f"Saved project not found at {vpr}")
    audio, samplerate = sf.read(wav, dtype="float32", always_2d=True)
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2))) if audio.size else 0.0
    if peak < 0.0001 or rms < 0.00001:
        raise RuntimeError(f"Native WAV was silent/near-silent (peak={peak}, RMS={rms})")
    output_wav = destination / wav.name
    output_vpr = destination / vpr.name
    shutil.copy2(wav, output_wav)
    shutil.copy2(vpr, output_vpr)
    return {
        "native_status": status.get("product") + " " + status.get("version", ""),
        "project": str(output_vpr),
        "voice_wav": str(output_wav),
        "duration_seconds": round(len(audio) / samplerate, 4),
        "sample_rate": samplerate,
        "peak": peak, "rms": rms,
        "vpr_sha256": hashlib.sha256(output_vpr.read_bytes()).hexdigest(),
        "wav_sha256": hashlib.sha256(output_wav.read_bytes()).hexdigest(),
        "ai_adjust": str(adjusted)[:600],
        "mixdown_result": str(mixed)[:600],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--midi", help="Existing Suno Studio MIDI export")
    inputs.add_argument("--midi-url", help="Suno MCP temporary signed MIDI URL")
    parser.add_argument("--dry-run", action="store_true",
                        help="Analyze only; never start VOCALOID or generate audio")
    args = parser.parse_args()

    if not BRIDGE.is_dir():
        print(f"ERROR: expected {BRIDGE}; run setup first", file=sys.stderr)
        return 2
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + str(os.getpid())
    destination = OUTROOT / run_id
    destination.mkdir(parents=True, exist_ok=False)
    if args.midi_url:
        source = destination / (SONG_ID + ".mid")
        download_existing_midi(args.midi_url, source)
    else:
        source = Path(args.midi).resolve(strict=True)
        if source.suffix.lower() not in {".mid", ".midi"}:
            raise ValueError("Expected .mid or .midi file")
    midi = mido.MidiFile(str(source))
    to_seconds, ticks, tempos = tick_map(midi)
    if any(t <= midi.ticks_per_beat * 20 and tempo != tempos[0]
           for t, tempo in zip(ticks, tempos)):
        raise RuntimeError("Tempo changed in intro; conservative single-tempo preview refused")
    bpm = round(60_000_000 / tempos[0], 4)
    tracks = extract_instruments(midi, to_seconds)
    chosen_track, choir, intro_notes, whole_notes = candidate_notes(tracks)
    score, mapping, dropped_sokuon = build_notes(choir, bpm)
    report = {
        "source_uuid": SONG_ID,
        "source_title": "何もなかったように青い",
        "source_midi_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "tempo_bpm": bpm, "suno_intro_alignment": [0.908, 9.426],
        "candidate_midi_track_index": chosen_track,
        "candidate_intro_notes": intro_notes, "candidate_full_notes": whole_notes,
        "renderable_syllable_count": len(score),
        "omitted_small_tsu_count": dropped_sokuon,
        "mapping": mapping,
        "fidelity": (
            "APPROXIMATE PROTOTYPE: Synth Choir program 54 may NOT be the actual "
            "lead vocal. Pitches are selected heuristically at syllable times; "
            "timings are interpolated from Suno word-level alignment. "
            "No claim of faithful source reconstruction until auditory comparison."
        ),
        "dry_run": args.dry_run,
    }
    if not args.dry_run:
        print("Rendering native VOCALOID7 asa preview (not full song)...", flush=True)
        native = asyncio.run(run_mcp(score, bpm, run_id, destination))
        report["native_render"] = native
    report_path = destination / "verification.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "PREVIEW_RENDERED" if not args.dry_run else "ANALYZED_ONLY",
        "output_directory": str(destination),
        "selected_track": chosen_track,
        "syllables": len(score),
        "sample": report.get("native_render"),
        "warning": report["fidelity"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
