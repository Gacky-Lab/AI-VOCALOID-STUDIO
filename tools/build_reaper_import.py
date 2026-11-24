#!/usr/bin/env python3
"""Validated local WAV manifest -> a manually-run REAPER ReaScript (Lua).

This tool itself does not launch REAPER, modify projects or render any audio.
"""
import argparse
import json
import math
import sys
from pathlib import Path


def lua_literal(text):
    if not isinstance(text, str) or not text or "\x00" in text or "\n" in text or "\r" in text:
        raise ValueError("invalid Lua string")
    delim = "="
    while "]" + delim + "]" in text:
        delim += "="
    return "[" + delim + "[" + text + "]" + delim + "]"


def build_lua(job_path):
    job_path = Path(job_path)
    data = json.loads(job_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"job_version", "tracks"} or data["job_version"] != "1.0.0":
        raise ValueError("unsupported local REAPER job schema")
    tracks = data["tracks"]
    if not isinstance(tracks, list) or not 1 <= len(tracks) <= 64:
        raise ValueError("expected 1..64 WAV tracks")
    entries = []
    for i, track in enumerate(tracks):
        if not isinstance(track, dict) or set(track) != {"name", "source_path", "position_seconds"}:
            raise ValueError("invalid track record")
        name, source, pos = track["name"], track["source_path"], track["position_seconds"]
        if not isinstance(name, str) or len(name) > 128 or not name.strip():
            raise ValueError("invalid track name")
        if type(pos) not in (float, int) or not math.isfinite(pos) or pos < 0:
            raise ValueError("position_seconds must be nonnegative finite number")
        name_quoted = lua_literal(name)
        source_quoted = lua_literal(source)
        path = Path(source)
        if not path.is_absolute():
            path = job_path.parent / path
        path = path.resolve()
        if not path.is_file() or path.suffix.lower() != ".wav":
            raise ValueError("WAV file missing or unsupported at index " + str(i))
        entries.append("  {name=" + name_quoted + ",path=" + lua_literal(str(path)) +
                       ",position=" + repr(float(pos)) + "},")
    return "\n".join([
        "-- Generated from a validated local job. Use ONLY in a saved copy of a REAPER project.",
        "-- Not a headless render, not a plugin-installer, and not a successful GUI test.",
        "local specs = {", *entries, "}",
        "local sources = {}",
        "for i, spec in ipairs(specs) do",
        "  local src = reaper.PCM_Source_CreateFromFile(spec.path)",
        "  if not src then",
        "    reaper.ShowMessageBox('Could not open WAV source. No tracks added.','Preflight failed',0)",
        "    return",
        "  end",
        "  sources[i] = src",
        "end",
        "reaper.Undo_BeginBlock()",
        "reaper.PreventUIRefresh(1)",
        "local ok, err = pcall(function()",
        "  for i, spec in ipairs(specs) do",
        "    local index = reaper.CountTracks(0)",
        "    reaper.InsertTrackAtIndex(index, true)",
        "    local track = reaper.GetTrack(0, index)",
        "    if not track then error('GetTrack returned nil') end",
        "    reaper.GetSetMediaTrackInfo_String(track, 'P_NAME', spec.name, true)",
        "    local item = reaper.AddMediaItemToTrack(track)",
        "    local take = item and reaper.AddTakeToMediaItem(item)",
        "    if not take then error('Unable to create take') end",
        "    if not reaper.SetMediaItemTake_Source(take, sources[i]) then error('Unable to attach source') end",
        "    local duration, isQN = reaper.GetMediaSourceLength(sources[i])",
        "    if isQN or duration <= 0 then error('Invalid source duration') end",
        "    reaper.SetMediaItemInfo_Value(item, 'D_POSITION', spec.position)",
        "    reaper.SetMediaItemInfo_Value(item, 'D_LENGTH', duration)",
        "  end",
        "end)",
        "reaper.PreventUIRefresh(-1)",
        "reaper.TrackList_AdjustWindows(false)",
        "reaper.UpdateArrange()",
        "reaper.Undo_EndBlock('Import verified WAV sources', -1)",
        "if not ok then",
        "  reaper.ShowMessageBox('Import may be partial. Inspect and Undo if needed.','REAPER import error',0)",
        "end",
        ""
    ])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    try:
        script = build_lua(a.job)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(script, encoding="utf-8")
        print("Generated manually-run REAPER Lua script:", a.output)
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
