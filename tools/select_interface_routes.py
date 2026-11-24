#!/usr/bin/env python3
"""Fail-closed route selection. User-provided facts are scenarios, NOT verified device evidence.

Read config/interface_routes.v1.json and a JSON profile containing:
 {"mode":"production"|"demo", "asserted_true":["..."]}
No network requests or system inspection; do not interpret output as actual render success.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "interface_routes.v1.json"
ALLOWED_STAGES = ("source", "lyrics", "notes", "alignment", "render", "mix")


def evaluate(catalog, profile):
    if not isinstance(catalog, dict) or catalog.get("catalog_version") != "1.0.0":
        raise ValueError("unsupported catalog")
    if catalog.get("stages") != list(ALLOWED_STAGES):
        raise ValueError("invalid stage list")
    if not isinstance(profile, dict) or set(profile) != {"mode", "asserted_true"}:
        raise ValueError("profile must contain only mode and asserted_true")
    mode = profile["mode"]
    if mode not in ("demo", "production"):
        raise ValueError("mode must be demo or production")
    flags = profile["asserted_true"]
    if not isinstance(flags, list) or not all(isinstance(x, str) for x in flags) or len(flags) != len(set(flags)):
        raise ValueError("asserted_true must be unique string flags")
    routes = catalog.get("routes")
    if not isinstance(routes, list):
        raise ValueError("routes missing")
    known = set()
    seen_ids = set()
    for route in routes:
        if not isinstance(route, dict):
            raise ValueError("route must be an object")
        if route.get("stage") not in ALLOWED_STAGES or not isinstance(route.get("priority"), int):
            raise ValueError("invalid route stage/priority")
        if route.get("id") in seen_ids or not isinstance(route.get("requires"), list) or not all(isinstance(x, str) for x in route["requires"]):
            raise ValueError("invalid duplicate/route prerequisites")
        seen_ids.add(route["id"])
        known.update(route["requires"])
    unknown = set(flags) - known
    if unknown:
        raise ValueError("unknown assertion flags: " + ", ".join(sorted(unknown)))
    asserted = set(flags)
    by_stage = {}
    for stage in ALLOWED_STAGES:
        options = [r for r in routes if r["stage"] == stage and mode in r["modes"]]
        options.sort(key=lambda r: (-r["priority"], r["id"]))
        eligible = [r for r in options if set(r["requires"]) <= asserted]
        if not eligible:
            by_stage[stage] = {
                "state": "BLOCKED", "selected": None,
                "options": [{"id": r["id"], "missing": sorted(set(r["requires"]) - asserted)}
                            for r in options]
            }
        else:
            r = eligible[0]
            state = "OFFLINE_DEMO_ONLY" if mode == "demo" else "CONDITIONAL_USER_ASSERTIONS"
            by_stage[stage] = {
                "state": state, "selected": r["id"], "basis": r["evidence"],
                "kind": r["kind"], "source": r["source"],
                "warning": "This is a route hypothesis based on user assertions, not an observed Windows/voice render."
            }
    all_ready = mode == "production" and all(by_stage[s]["selected"] is not None for s in ALLOWED_STAGES)
    # Never return an unconditional production-pass without Windows/audio evidence collected externally.
    return {
        "mode": mode, "assertions_are_unverified": True, "stages": by_stage,
        "end_to_end_state": "CONDITIONAL_NEEDS_REAL_EVIDENCE" if all_ready else "NOT_READY",
        "actual_windows_acceptance": "NOT_RUN",
        "note": "CI success proves route logic, not Suno/MCP/voicebank/REAPER functionality."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        c = json.loads(args.catalog.read_text(encoding="utf-8"))
        p = json.loads(args.profile.read_text(encoding="utf-8"))
        result = evaluate(c, p)
        data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(data, encoding="utf-8")
        else:
            print(data, end="")
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
