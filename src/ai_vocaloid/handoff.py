"""Consumer-side validation of Gacky-Lab's local lyric handoff v1."""
import hashlib
import json
import re
from pathlib import Path

SID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
VID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


def verify_handoff(data, expected_song_id=None):
    required = {"contract_version", "song_id", "lyric_version_id", "language", "lyrics_text", "lyrics_sha256"}
    if not isinstance(data, dict) or not required <= set(data) or set(data) - (required | {"editorial_assessment"}):
        raise ValueError("unknown or missing handoff fields")
    if data["contract_version"] != "1.0.0" or data["language"] != "ja":
        raise ValueError("unsupported handoff contract/language")
    if not isinstance(data["song_id"], str) or not SID.fullmatch(data["song_id"]):
        raise ValueError("invalid song ID")
    if not isinstance(data["lyric_version_id"], str) or not VID.fullmatch(data["lyric_version_id"]):
        raise ValueError("invalid version ID")
    if expected_song_id is not None and expected_song_id != data["song_id"]:
        raise ValueError("song_id mismatch")
    lyric = data["lyrics_text"]
    if not isinstance(lyric, str) or not lyric.strip() or "\r" in lyric or "\x00" in lyric or lyric.startswith("\ufeff"):
        raise ValueError("invalid LF-normalized lyric text")
    if len(lyric.encode("utf-8")) > 1000000:
        raise ValueError("lyrics exceed 1 MB")
    actual = hashlib.sha256(lyric.encode("utf-8")).hexdigest()
    if data["lyrics_sha256"] != actual:
        raise ValueError("lyrics_sha256 mismatch")
    if "editorial_assessment" in data:
        a = data["editorial_assessment"]
        if not isinstance(a, dict) or a.get("method") != "editorial_weighted_1_to_5" or a.get("evidence_status") != "author_editorial_not_listener_validated":
            raise ValueError("editorial provenance invalid")
        complete, score = a.get("complete"), a.get("score_100")
        if type(complete) is not bool or (complete and (type(score) not in (int, float) or not 20 <= score <= 100)) or (not complete and score is not None):
            raise ValueError("editorial score invalid")
    return {key: data[key] for key in ("contract_version", "song_id", "lyric_version_id", "lyrics_sha256")}


def read_handoff(path, expected_song_id=None):
    return verify_handoff(json.loads(Path(path).read_text(encoding="utf-8")), expected_song_id)
