# VOCALOID7 trial + local MCP guide (2026-11-25)

**Status (2026-11-25): Owner/Copilot reports Windows VOCALOID7 native MCP connectivity, voicebank enumeration and a 15-second native asa singing WAV render SUCCESS.** This is user-supplied test output, not an independently inspected local file or CI test. See [verification report](VERIFICATION_2026-11-25.md) for exact observations, output metadata and outstanding checks. The community bridge is **unofficial**. Its author's validation alone is not acceptance evidence.

## Bridge and requirements

- Third-party bridge: https://github.com/Asakitan/vocaloid_bridge
- Pinned upstream revision: 8ac1f0287e227ccae8be51b8de3d5aaf60b51cdf
- Windows, correctly licensed VOCALOID7 trial, Git, Python 3.11+, .NET **10 SDK**, VS Code Copilot Agent or local Codex CLI/IDE.
- Initial voicebank: **asa** bundled with the trial. Do not claim Hatsune Miku V6 is installed.
- Bridge uses a private **background** host, not mouse/keyboard automation of the editor shown on screen.
- Avoid running the third-party code as Administrator. Review its source first. Do not bypass license checks.

## Instructions on the owner's Windows PC

Get this setup branch in a fresh folder to avoid altering existing local work:

    git clone -b feat/vocaloid7-trial-mcp-setup https://github.com/Gacky-Lab/AI-VOCALOID-STUDIO.git
    cd AI-VOCALOID-STUDIO

Check prerequisites without installing anything:

    powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\setup_vocaloid7_mcp.ps1 -Action Check

If Python is not on PATH, supply your actual Python executable using -PythonExe.

After reviewing the pinned third-party source and accepting the risks, install:

    powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\setup_vocaloid7_mcp.ps1 -Action Install

The script clones the pinned bridge into ignored private/vocaloid_bridge, passes the **real Python path** to its setup.ps1, requests VOCALOID7, installs Python dependencies and builds the native .NET host. It does not start MCP automatically. Do not put private songs or credentials in Git.

### VS Code Copilot Agent

Open this repository as a trusted local VS Code workspace. The checked-in workspace-root **.mcp.json** declares **vocaloid7-native** as a Windows-local Python stdio process and also declares the **Suno official remote MCP** (`https://api.suno.com/mcp`). The Suno MCP still needs user authorization in the Copilot session; the successful VOCALOID7 tests below do **not** prove that Suno MCP is authenticated or that a real Suno song has been reproduced. (The old .vscode/mcp.json servers format is deprecated for the newer Copilot harness.) Start the server in VS Code's MCP management UI and review the tool approval prompt. This config does not install anything. If your Copilot harness requires it, approve workspace MCP trust when asked.

### Codex CLI / Codex IDE extension

After installing the bridge, optionally register it in local Codex user configuration:

    powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\setup_vocaloid7_mcp.ps1 -Action RegisterCodex
    codex mcp list

Restart Codex and use /mcp to verify availability. To remove this registration later:

    codex mcp remove vocaloid7-native

Local Codex MCP configuration and VS Code Copilot MCP configuration are **different**. This does not make the local server available to the ChatGPT browser chat.

## Acceptance sequence

1. Connect and get tools/list; confirm vocaloid_status and voicebanks exist, and record actual VOCALOID7 version.
2. Query voicebanks and confirm **asa** is installed. Run vocaloid_workflow to read the server's workflow.
3. First request ONLY read-only status + voicebank inspection. Do not write, play, render or close anything yet.
4. With approval, create a **new** short original kana-based score under the private workspace, explicitly select asa, render 15 seconds, save VPRX and WAV.
5. Verify files on disk, non-silent PCM, audible playback. Repeat three independent renders and record durations / SHA-256 locally.
6. Report BLOCKED rather than success if anything fails; use the official manual MIDI import / WAV export route as fallback.

Read-only first prompt:

    Call vocaloid_status and voicebanks on vocaloid7-native, nothing else.
    Report detected Editor version, installed voicebank list and errors.
    Do not create or change projects, play audio, start a render or close any processes.

**Test outcome (2026-11-25):** Copilot reported `vocaloid_status` and `voicebanks` passed for VOCALOID7 7.0.1.1, asa 7.0.0. A short original-score test produced a 15.0 s, 44.1 kHz mono 16-bit PCM native WAV (peak 0.3560, RMS 0.0807), with 20 notes at 80 BPM and a `.vpr` project. Files have not been independently retrieved or listened to. The canonical Suno URL https://suno.com/s/RVDcj9JvsVPCWJGu has **not** yet been synthesized. Exact evidence and pending checks: [verification report](VERIFICATION_2026-11-25.md).

**Isolation:** VOCALOID_WORKSPACE points to private/vocaloid_bridge, not this main repository. The third-party bridge cleans older temporary output files in its own workspace; review and copy final media somewhere permanent before cleanup. private/ and output/ are ignored by Git.

References:
- https://www.vocaloid.com/en/vocaloid7/specs/
- https://github.com/Asakitan/vocaloid_bridge/blob/master/docs/vocaloid7.md
- https://code.visualstudio.com/docs/agent-customization/mcp-servers
- https://learn.chatgpt.com/docs/extend/mcp
