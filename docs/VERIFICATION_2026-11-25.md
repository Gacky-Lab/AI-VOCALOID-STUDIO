# VOCALOID7 trial MCP — owner-reported Windows verification (2026-11-25)

> **Evidence classification:** This record is transcribed from the owner's actual VS Code MCP server log and the Copilot agent's test summaries pasted into the chat. It is not CI, a reproduced test in a separate environment, or an independent inspection of the audio files. Do **not** present all stages as verified on the basis of MCP tool discovery alone.

## 1. Setup prerequisites and installation

- Windows PC project root reported: `C:\Users\smily\AI-VOCALOID-STUDIO`.
- The `-Action Check` script reported Python at `C:\Users\smily\AppData\Local\Programs\Python\Python312\python.exe`, .NET 10 SDK **OK**, and the pinned `vocaloid_bridge` upstream commit `8ac1f0287e227ccae8be51b8de3d5aaf60b51cdf`.
- The `-Action Install` command reportedly completed, selecting `VOCALOID7 7.0.1.1` in `C:\Program Files\VOCALOID7\Editor`, building the .NET 10 native host, and installing `vocaloid6-mcp-0.30.0` bridge package.
- The native host is community-developed and unofficial.

## 2. Local MCP server initialization: passed

Owner pasted the exact VS Code output:

```text
2026-11-25 02:48:25.401 [info] Starting server vocaloid7-native
2026-11-25 02:48:25.402 [info] Connection state: Starting
2026-11-25 02:48:25.402 [info] Starting server from LocalProcess extension host
2026-11-25 02:48:25.415 [info] Connection state: Starting
2026-11-25 02:48:25.415 [info] Connection state: Running
2026-11-25 02:48:30.428 [info] Waiting for server to respond to `initialize` request...
2026-11-25 02:48:35.425 [info] Waiting for server to respond to `initialize` request...
2026-11-25 02:48:40.424 [info] Waiting for server to respond to `initialize` request...
2026-11-25 02:48:41.756 [warning] [server stderr] Processing request of type ListPromptsRequest
2026-11-25 02:48:41.757 [warning] [server stderr] Processing request of type ListToolsRequest
2026-11-25 02:48:41.759 [info] Discovered 41 tools
```

**Interpretation:** Local VS Code MCP client initialized the server and discovered 41 exposed tools. The initial `Waiting for server` messages resolved; they do not indicate a sustained initialization failure.

**Important limitation:** The Copilot agent subsequently said it did not directly see VOCALOID tool invocations in its chat tool list. It said it used an available local MCP connection route for two read-only calls. Thus "MCP server connected" is **not** proof that every chat agent mode automatically exposes the tools directly.

## 3. Read-only VOCALOID engine/voicebank query: passed per Copilot report

The Copilot agent reported:

| Property | Reported result |
|---|---|
| `vocaloid_status` | Succeeded |
| `voicebanks` | Succeeded |
| VOCALOID7 editor version | `7.0.1.1` |
| Synthesis engine availability | Available, `native-vsm` |
| Voicebank | `asa` `7.0.0`, AI-capable, usable for sequence and synthesis |
| Errors | None |
| Sessions, render cache | 0 sessions, 0 cache entries |
| Side effects | No new project, edits, or audio render in the read-only check |
| Engine process | Test process shutdown reported |

This report is sufficient to characterize the user's read-only check as **owner-reported successful**; the raw MCP JSON responses have not been archived.

## 4. New, original native singing test: passed per Copilot report

- New composition, not the linked Suno song.
- Voicebank: `asa` 7.0.0; VOCALOID7 7.0.1.1.
- Tempo `80 BPM`, meter `4/4`, `5 bars`, `20 MIDI notes` mapped to original kana lyrics.
- Lyrics supplied by the Copilot summary: `あさひのひかりがまどべにそそぐあさだよね`.
- Project filename: `mcp_v7_asa_song_20261125_0251.vpr`.
- Render filename: `mcp_v7_asa_song_20261125_0251.wav`.
- WAV according to Copilot inspection: **15.0 s**, **44,100 Hz**, **mono**, **16-bit PCM**.
- Non-silence metrics: peak **0.3560**, RMS **0.0807**.
- Synthesis reported via native mixdown `native=true`, `VAE.Manual+VEM`; no substitute synth.
- Copilot said it checked saved project summary for `asa`, 20 notes, 80 BPM, discarded its unsaved preliminary session and retained only final outputs.
- **No human auditory check performed.**
- File absolute paths and SHA-256 hashes were **not** included in the pasted report. Output file contents have **not** been uploaded to the chat or committed to GitHub; WAV claims are based on Copilot's report rather than independent audio inspection.
- **Project format caution:** Observed filename ends in `.vpr`, even though this project's preferred native V7 output format was `.vprx`. Do not change its extension or claim VPRX validity without opening/inspecting it.

**Acceptance status:** Native non-silent 15 s render was successful according to owner Copilot report. Auditory quality and editability in the actual GUI remain pending.

## 5. Suno source track — NOT reproduced

Requested URL: https://suno.com/s/RVDcj9JvsVPCWJGu

- The link uses a 16-character short share token; it is **not** the canonical UUID needed for direct Suno MCP audio endpoints.
- In the ChatGPT-side read-only Suno MCP query, passing the short token as an `id` returned `audio not found` on `audio_retrieve`, `audio_lyrics_alignment` and `audio_analysis`. This does **not** mean the underlying public song is absent; the canonical UUID must be resolved.
- Suno MCP is declared in the workspace `.mcp.json`, but **Copilot-side login/authentication, direct tool discovery, full song metadata, owned MIDI transcription and stems availability have not been demonstrated**.
- No lyrics-to-note alignment, original vocal melody MIDI conversion, stem split, native rendering or full mix has been reported for the specific Suno URL.
- The existing 15-second test must not be called a cover/recreation of this Suno source.

## 6. Outstanding validation and next gates

1. Resolve the exact canonical Suno song UUID and confirm title, owner and rights in the authenticated Suno session.
2. Connect the Suno official MCP in VS Code, enumerate tools and verify that both Suno and VOCALOID7 endpoints are usable in the same agent workflow.
3. Prefer previously created MIDI and stems; obtain approval **before** operations that spend Suno credits.
4. Verify lead vocal MIDI extraction and word/kana alignment against source recording (not arbitrary autogenerated notes).
5. Synthesize a 15–30-second phrase through VOCALOID7 native asa, with a recorded output location and SHA-256; listen to the WAV and compare melody and timing with the Suno original.
6. Only if source fidelity passes, render the entire song and mix with separated instrumental.
7. Keep the exact source, output artifacts and detailed QA logs locally; do not upload proprietary songs, account credentials or large private assets to a public GitHub repository without explicit consent.

### Current milestone table

| Milestone | Status |
|---|---|
| Windows dependencies and bridge install | OWNER-REPORTED PASS |
| Local VS Code MCP init, tools/list=41 | RAW LOG PROVIDED / PASS |
| Native status and asa enumeration | COPILOT-REPORTED PASS |
| 15-second original native asa WAV | COPILOT-REPORTED PASS |
| Playback/quality by human | NOT RUN |
| Save project can be opened in VOCALOID7 GUI | NOT VERIFIED |
| Suno official MCP in local Copilot | NOT VERIFIED |
| Target Suno song metadata/MIDI/stems | NOT VERIFIED |
| Target Suno song recreated by VOCALOID7 | **NOT RUN** |

---

## 7. Canonical Suno song and ChatGPT-side Suno MCP results (2026-11-25 update)

This **supersedes older blockers in section 5** about not knowing the canonical song ID or being unable to retrieve source metadata. It does **not** supersede the missing local VOCALOID7 rendering.

- Short link: https://suno.com/s/RVDcj9JvsVPCWJGu
- Canonical UUID: `f60cd638-8c59-428c-97c2-1eabd86b6a76`.
- Canonical URL: https://suno.com/song/f60cd638-8c59-428c-97c2-1eabd86b6a76
- Official Suno MCP `audio_retrieve`: **PASS** via ChatGPT session.
- Title: `何もなかったように青い`; creator handle `gacky`; model `v6`; length `196.4 seconds`; complete/public; lyrics were returned.
- Suno MCP `audio_lyrics_alignment`: **PASS**; word-level timestamp data returned. Word timings are estimates and do not supply vocal note pitch.
- Suno MCP `audio_analysis`: **processing** on initial check; key/BPM/beat map not yet returned.
- Suno MCP `audio_download` no-confirm preflight for WAV: `status=ok` and expiring signed URL returned; no download-credit confirmation needed. **File not verified on Windows**.
- Suno MCP `audio_midi`: `status=ok` and expiring MIDI URL returned. Instruments: Electric Piano 1 (2,539 notes), Synth Choir (685), Electric Bass finger (581), Electric Bass pick (558), drums (1,200). **The vocal melody track has not yet been identified**, and a full MIDI file should not be passed blindly to VOCALOID7 as vocals.
- Suno MCP `audio_stems_create` with `mode=two`: submitted within the user's reported **up-to-60 Suno song credit approval**. Stem group: `stemgrp_7e71d95c-0ceb-4c15-bf17-31788ecc02b6`, with two takes each of vocals/instrumental (expected total 10 credits on completion if both vocal takes succeeded). Most recent polling: take 2 vocals `6eb23c0e-0290-44b2-a1b6-37f130e4ebf5` and instrumental `40d2e75d-04ff-4736-968b-0f9fce1298bc` **complete**; take 1 pending. The final billed credit count has **not** been verified; do not claim zero.
- The ChatGPT-connected Suno MCP is separate from the Windows VS Code Copilot MCP session. The latter reported **Suno and vocaloid7-native chat tools missing** even when VS Code MCP configurations were present. Windows project/WAV synthesis with this original Suno song is **still not done**.
- No Suno credential, signed temporary download URL, proprietary MIDI/WAV data or lyrics were committed here. Signed URLs expire quickly and must be freshly requested in an authenticated session.

### Next priority

1. On Windows VS Code **MCP: List Servers**, verify `suno` and `vocaloid7-native` both show Running; use **Show Output** for either that fails; check per-chat **Configure Tools** in Copilot Agent mode and start a **new chat** after server startup. The presence of servers in the list is not enough if chat Agent tools are disabled. If necessary, continue with direct Python bridge invocation, as in the prior successful original 15-second synthesis.
2. Download approved MIDI and both source stems to a local, ignored input folder with refreshed URLs. Verify local media without exposing credentials.
3. Determine which MIDI notes belong to the lead vocal, compare against vocal stem and word timing; manually validate tricky Japanese kana.
4. Render a first 15–30-second source-matched asa phrase, review the actual WAV and timing, then proceed with whole song.
5. Archive stdout/stderr, actual output paths and checksums locally; track extra metered operations under the user's approval limit. Never count synthetic song test as this target's finished recreation.

---

## 8. Owner-executed standalone MCP read-only probe: VERIFIED BY RAW CONSOLE OUTPUT

The user ran:

```powershell
cd $HOME\AI-VOCALOID-STUDIO
git pull
& .\private\vocaloid_bridge\.venv\Scripts\python.exe .\tools\probe_vocaloid7_direct.py
```

The full pasted PowerShell result ended in:

```text
MCP_INITIALIZED: true
MCP_TOOL_COUNT: 41
REQUIRED_TOOLS_PRESENT: True
vocaloid_status: ... backend=native-vsm, version=7.0.1.1, product=VOCALOID7
voicebanks: ... name=asa, version=7.0.0, is_ai=true, available_in_sequence=true, synthesizable_version=true
RESULT: PASS (local stdio MCP direct calls)
```

Additional confirmed details: private workspace `C:\Users\smily\AI-VOCALOID-STUDIO\private\vocaloid_bridge`; bridge MCP version `0.30.0`; 0 active sessions and 0 render cache bytes at query time. The installed asa voicebank has `comp_id=BXHPECHANDRW3XEL`, `kind=Dnn`, and 3 voice types. These are **direct local MCP calls** independent of the Copilot Agent session's tool-visibility issue.

**Outcome:** Direct Windows Python→MCP stdio→VOCALOID7 native host handshake and actual `vocaloid_status` / `voicebanks` calls are now directly evidenced in the pasted console output. There were no project writes or audio renders during this probe. This result does not prove the selected Suno song was yet rendered.

### Latest Suno source status

Suno MIDI transcription for target UUID `f60cd638-8c59-428c-97c2-1eabd86b6a76` returned `status=ok` again (download URL is ephemeral). Stem group `stemgrp_7e71d95c-0ceb-4c15-bf17-31788ecc02b6` returned `status=complete` with **both vocal and both instrumental stem takes complete**, confirmed via ChatGPT-side Suno MCP. Local copies on Windows have **not** been verified; these results do not resolve the Copilot tool-discovery gap.

Next task: acquire the exact MIDI and stem files into an ignored local directory without checking source media or auth tokens into Git; inspect/select the vocal melody from MIDI, align original lyrics and synthesize a short phrase with the proven direct stdio transport.


---

## 9. Executable local Suno-to-asa preview runner added (NOT YET TESTED)

- Script: `tools/render_suno_v7_preview.py`.
- Input: Suno MIDI URL obtained by already-completed `audio_midi`, or a local MIDI file.
- The local Windows script downloads that MIDI (without initiating a new Suno conversion), checks the Synth Choir instrument track and interpolates the Suno-aligned opening lyric reading into candidate pitches, then calls the **previously validated direct stdio MCP** to do `score_compose`, `project_ai_adjust`, `project_audio mixdown`, `project_save` and `project_close`.
- Intended output: ignored `output/suno_v7_previews/<run-id>/` directory with source MIDI, draft/full editable VPRX and asa singing WAV plus `verification.json`.
- **This is an approximate first 9.4-second prototype, not the entire original song and not proven melody recognition.** The Synth Choir track is a heuristic candidate, word alignment doesn't specify pitch, and small sokuon handling is approximate. It may fail, and source fidelity needs human auditory review.
- **Historical status at script creation:** execution was unverified. Subsequent owner-run success is recorded in section 10 below.
- Signed Suno download URLs expire; do not commit them to GitHub, and do not display them in logs. The raw MIDI/WAV is private local output.


---

## 10. VERIFIED: User-executed Suno MIDI → VOCALOID7 asa native 10-second WAV and project

Owner-supplied PowerShell output following commit `804da0edc91e4af0c1cfe0dd2966ad93f3cbc67d` conclusively records:

```text
REUSING_MIDI: ...\output\suno_v7_previews\20261124T184036Z_22412\f60cd638-8c59-428c-97c2-1eabd86b6a76.mid
MONOPHONIC_PREFLIGHT: PASS (24 notes; 480 PPQ; 1-tick gaps)
Rendering native VOCALOID7 asa preview (not full song)...
MCP_STAGE: vocaloid_status
MCP_STAGE: voicebanks
MCP_STAGE: vocaloid_workflow
USING_INSTALLED_ASA_TEMPLATE: ...\private\vocaloid_bridge\output\mcp_v7_asa_song_20261125_0251.vpr
MCP_STAGE: score_compose
MCP_STAGE: project_edit
MCP_STAGE: project_edit
MCP_STAGE: project_ai_adjust
MCP_STAGE: project_audio
MCP_STAGE: project_save
MCP_STAGE: project_close
"status": "PREVIEW_RENDERED"
```

- Candidate source: `Synth Choir` MIDI track index **1**; **24 syllabic notes**. The track is **not proven to be actual source lead-vocal**.
- Native output: `VOCALOID7 7.0.1.1`, `project_audio mixdown` reports `native=true`, `backend=VAE.Manual+VEM`.
- Local folder: `C:\Users\smily\AI-VOCALOID-STUDIO\output\suno_v7_previews\20261124T184447Z_23972`.
- WAV: `20261124T184447Z_23972_asa.wav` (10.0 s, 44100 Hz, mono, 16-bit), peak `0.510040283203125`, RMS `0.09656472511359551`.
- Editable project: `20261124T184447Z_23972_asa.vprx`.
- WAV sha256: `0aaeaff19f84d26c378710da4b2cfe863f743db41088f48a6a0d9861e8d1e341`.
- VPR sha256: `8b1d8dfdbc246047cbeabac777f02c7a9c82e4b66c56f455d8a40130fd8bbfd8`.
- Human listening and fidelity to original Suno vocal **not yet assessed**. This proves a real native synthesized first-10-second preview; **not** completion of full 196.4-second Suno-to-VOCALOID7 recreation.
- Known risks: Synth Choir candidate may not represent sung lead; lyric syllables are heuristically interpolated from word alignment; small sokuon dropped; notes quantized to mono with 1 tick gaps.
- Next evidence needed: owner auditions the WAV (ideally compare source 0–10 s), and attach the WAV if audio quality assessment is requested. Keep all audio/MIDI/project artifacts ignored; do not commit private media to repository.
