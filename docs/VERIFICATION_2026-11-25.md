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
