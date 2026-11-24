#!/usr/bin/env python3
"""Verify a versioned lyric handoff (no network requests)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ai_vocaloid.handoff import read_handoff


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path)
    p.add_argument("--song-id")
    a = p.parse_args()
    try:
        print(json.dumps(read_handoff(a.path, a.song_id), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
