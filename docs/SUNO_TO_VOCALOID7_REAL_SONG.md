# Suno real-song → VOCALOID7 via dual MCP (2026-11-25)

## Goal / target

- Target public short link: https://suno.com/s/RVDcj9JvsVPCWJGu
- Original Suno song → vocal MIDI + exact lyrics/word timing + instrumental stems → VOCALOID7 installed **asa** voicebank → editable project and native synthesized voice WAV, then aligned mix for listening.
- This is an integration plan, **NOT proof** that the short link has been resolved or the track synthesized.
- Previously validated locally by user/Copilot: VOCALOID7 7.0.1.1, asa 7.0.0, native MCP tools/list 41, 15-second original asa synthetic test (44.1 kHz PCM non-silent); user listening and this specific Suno song are still unverified.

## Dual-MCP setup

Workspace-root \`.mcp.json\` declares:
- \`vocaloid7-native\`: local Windows stdio native V7 bridge, installed under ignored \`private/vocaloid_bridge\`.
- \`suno\`: **official** https://api.suno.com/mcp remote HTTP MCP. First use needs separate OAuth sign-in in VS Code Copilot, even if Suno is already authorized in a ChatGPT browser conversation.

On the user Windows PC:

    cd $HOME\AI-VOCALOID-STUDIO
    git pull

Then VS Code > Developer: Reload Window, MCP: List Servers, choose **suno**, Start Server, follow Suno login/OAuth, check list of Suno tools. Keep \`vocaloid7-native\` running. Authenticate only via the official OAuth page, not by pasting tokens into files.

**WARNING:** GitHub Copilot may have many available tools; make sure the current agent session has the relevant Suno and vocaloid7-native tools enabled before running.

## Target identification: short share link vs UUID

Suno MCP \`audio_retrieve\`, \`audio_lyrics_alignment\`, etc. require the **canonical song UUID**, not the 16-character short-link code \`RVDcj9JvsVPCWJGu\`. In the ChatGPT-side read-only MCP test, treating that short code as an ID returned \`audio not found\`; this does **not** establish that the actual song is absent.

First open the short link in the logged-in Suno browser and capture the canonical \`https://suno.com/song/<UUID>\` or \`https://suno.com/@handle/song/<UUID>\` address. A public redirect can also be attempted through the Windows terminal/browser, but must not guess an ID. Match the title and creator to the share page. When the canonical UUID is known, use \`audio_retrieve\`, \`audio_lyrics_alignment\` and \`audio_analysis\` on Suno MCP.

If the song is not in the authenticated account library, confirm ownership/rights and whether Suno MCP authorizes reading it; do not silently substitute a similarly named song.

## Metered operations / approvals

Suno MCP media and MIDI feature access depends on plan and OAuth scopes. The **first** \`audio_midi\` transcription of a whole song uses **10 Suno song credits** (unless already transcribed; then free). Two-stem split costs **10 song credits total** (two takes × 5 credits each); 12-stem split costs **50** (two takes × 25). \`audio_download\` may spend a download credit, determined by a no-confirm preflight. Do not call a paid operation or \`confirm: true\` until the user explicitly approves its actual cost. Prefer existing Studio MIDI, stems and already-owned downloads if available. If metered operation cannot be approved, stop at NEEDS_APPROVAL and give the exact missing asset/cost.

The Suno MCP only provides download URLs; the **local Copilot agent** needs to download binary source material from authorized URLs into the ignored local project \`input/<UUID>\` directory. The ChatGPT browser alone does not have access to the Windows local bridge.

## Input acceptance

- Actual Suno lead vocal melody MIDI, not an arbitrary MIDI track; document selected track index and check note lengths/timing/tempo.
- Original lyrics + word alignment; check kana/phonemes by listening. MIDI transcription may contain all instruments and multiple potential melody tracks.
- Separate instrumental and vocal stems (when authorized), with verified duration, sample rates and time zero. Do not assume Suno's MIDI estimate perfectly matches the original audio.
- Rights and source IDs recorded locally. Never commit proprietary binaries or Suno access tokens to GitHub.
- If syllable/notes misalign, mark NEEDS_REVIEW and do not claim a faithful recreation.

## VOCALOID / delivery

1. Call \`vocaloid_status\`, \`voicebanks\`, \`vocaloid_workflow\`; verify native host availability and \`asa\` in the current V7 trial.
2. Create an isolated new project in bridge workspace. Preserve source offsets, time signature and tempos. Align singing kana one syllable per note or supported lyric-phoneme method; handle multi-note vowels and rests explicitly.
3. For each phrase, explicitly select \`asa\` voicebank and V7 AI track scope, call native AI generation where required, native rendering, and save native project (\`.vprx\` preferred; inspect actual tool's supported extensions).
4. Verify each generated WAV's actual samples, non-silence, correct durations and relationship to original backing. A waveform/RMS test is NOT a human listen.
5. Produce dry run for first 15–30 s with user's approval of song/voice and then extend to full length. Mix vocal with instrumental only after voice alignment; absence of instrumental stems is not permission to use the original mix under a second lead vocal.
6. Save final voice WAV, full mix WAV, editable project, source manifest and per-stage QA report to a durable local non-temporary directory. Bridge's private temporary output may be automatically cleaned.
7. Report independent validations separately: native render status, non-silent WAV, timing difference vs source, lyric mapping coverage and human listening. Do not call the result "finished" if any missing check.

## Copilot instruction ready to paste (safe read-only phase)

> Read docs/SUNO_TO_VOCALOID7_REAL_SONG.md. Confirm \`suno\` MCP and \`vocaloid7-native\` MCP are both available. Open/resolve https://suno.com/s/RVDcj9JvsVPCWJGu to its canonical Suno UUID (do not guess). Check song title, owner, length, lyrics and whether the source lead MIDI and instrumental stems are already available. Via \`vocaloid_status\` and \`voicebanks\`, verify V7 and asa. Only read data; do NOT start any feature that charges Suno credits, calls an external download requiring a credit, writes files, or creates/renders projects. Report the UUID, available assets, any required credit costs and blockers.

After this succeeds, the user can separately authorize a budget and the first 15–30 s prototype. The final full-song reconstruction requires a successful fidelity/lyric alignment check; the example 15-second synthetic-song success alone is insufficient.
