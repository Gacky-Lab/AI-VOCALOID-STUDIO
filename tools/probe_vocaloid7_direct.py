"""Read-only VOCALOID7 MCP transport probe, independent of Copilot tool discovery.

Run from repository root with the bridge's own Python:
  & .\\private\\vocaloid_bridge\\.venv\\Scripts\\python.exe .\\tools\\probe_vocaloid7_direct.py

This starts its own local stdio MCP subprocess, lists tools, and calls only
vocaloid_status and voicebanks. Never creates/changes a project or renders audio.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE = REPO_ROOT / "private" / "vocaloid_bridge"
TARGETS = ("vocaloid_status", "voicebanks")


async def run() -> int:
    if not BRIDGE.is_dir():
        print("ERROR: private/vocaloid_bridge does not exist. Install the bridge first.", file=sys.stderr)
        return 2

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "vocaloid_bridge"],
        cwd=str(BRIDGE),
        env={
            **os.environ,
            "VOCALOID_WORKSPACE": str(BRIDGE),
            "PYTHONPATH": str(BRIDGE),
            "PYTHONUTF8": "1",
        },
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as client:
            await client.initialize()
            response = await client.list_tools()
            names = {tool.name for tool in response.tools}
            print(f"MCP_INITIALIZED: true")
            print(f"MCP_TOOL_COUNT: {len(response.tools)}")
            print(f"REQUIRED_TOOLS_PRESENT: {all(name in names for name in TARGETS)}")
            for name in TARGETS:
                if name not in names:
                    print(f"ERROR: missing tool {name}", file=sys.stderr)
                    return 3
                result = await client.call_tool(name, {})
                if result.isError:
                    print(f"ERROR: {name} returned MCP error", file=sys.stderr)
                    for item in result.content:
                        print(str(item)[:1000], file=sys.stderr)
                    return 4
                data = result.structuredContent
                if data is None:
                    data = [
                        item.text for item in result.content
                        if getattr(item, "type", "") == "text"
                    ]
                print(f"{name}:")
                print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
            print("RESULT: PASS (local stdio MCP direct calls)")
            return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(run()))
    except Exception as exc:
        print(f"RESULT: FAIL ({type(exc).__name__}: {exc})", file=sys.stderr)
        sys.exit(1)
