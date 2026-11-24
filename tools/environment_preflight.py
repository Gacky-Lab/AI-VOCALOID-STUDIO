#!/usr/bin/env python3
"""Read-only local OS preflight for VOCALOID6 design: never checks licensing or claims GUI success."""
import argparse
import ctypes
import json
import platform
import shutil
import sys
from pathlib import Path


def _ram_gib_windows():
    class Mem(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]
    mem = Mem()
    mem.dwLength = ctypes.sizeof(mem)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)):
        return None
    return round(mem.ullTotalPhys / (1024 ** 3), 2)


def capture(path=Path(".")):
    """Read only host OS, CPU and storage; absence of software on PATH is not proof of absence."""
    system = platform.system()
    return {
        "os_name": system,
        "os_release": platform.release(),
        "cpu_description": platform.processor() or "UNKNOWN",
        "architecture": platform.machine(),
        "memory_gib": _ram_gib_windows() if system == "Windows" else None,
        "free_disk_gib": round(shutil.disk_usage(str(path)).free / (1024 ** 3), 2),
        "reaper_on_path": bool(shutil.which("reaper") or shutil.which("reaper.exe")),
    }


def classify_host(h):
    fields = {"os_name", "os_release", "cpu_description", "architecture", "memory_gib",
              "free_disk_gib", "reaper_on_path"}
    if not isinstance(h, dict) or set(h) != fields:
        raise ValueError("host preflight data missing/unknown")
    os_status = "POSSIBLE" if h["os_name"] == "Windows" and h["os_release"] == "11" else "REVIEW_REQUIRED"
    cpu = h["cpu_description"].lower()
    cpu_status = "VENDOR_LISTED_FAMILY_CHECK_BUILD" if "intel" in cpu else "COMPATIBILITY_REVIEW_REQUIRED"
    mem = h["memory_gib"]
    disk = h["free_disk_gib"]
    mem_status = "UNKNOWN" if mem is None else "MAY_MEET_MINIMUM" if mem >= 8 else "BELOW_MINIMUM"
    disk_status = "MAY_MEET_MINIMUM" if type(disk) in (float, int) and disk >= 25 else "BELOW_MINIMUM"
    return {
        "official_v6_minimum_reference": "Windows 11 22H2+, Intel Core 4th gen+/Xeon, 8 GiB RAM, 25 GiB free",
        "os": os_status,
        "cpu": cpu_status,
        "memory": mem_status,
        "free_disk": disk_status,
        "reaper_path": "FOUND_ON_PATH_NOT_TESTED" if h["reaper_on_path"] else "UNKNOWN_NOT_ON_PATH",
        "windows_build_22h2": "NOT_CHECKED",
        "v6_editor_executable": "NOT_CHECKED",
        "v6_voicebank_license_and_identity": "NOT_CHECKED",
        "suno_entitlement": "NOT_CHECKED",
        "mcp_auth_and_tool_schemas": "NOT_CHECKED",
        "actual_voice_render": "NOT_RUN",
        "actual_reaper_import": "NOT_RUN",
        "summary": "Only a read-only environment hint; never a device acceptance or license check"
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, default=Path("."))
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    try:
        result = {"host": capture(args.workspace), "requirements": None}
        result["requirements"] = classify_host(result["host"])
        serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized, encoding="utf-8")
        else:
            print(serialized, end="")
        return 0
    except (ValueError, OSError, TypeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
