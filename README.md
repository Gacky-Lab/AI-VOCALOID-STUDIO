# AI VOCALOID STUDIO

**AIボカロ自動制作基盤 / AI-powered VOCALOID production pipeline**  
Designed by **Gacky (Gacky-Lab)** | Concept announced: 2026-11-24 (JST)

Sunoで生成した楽曲をVOCALOIDで再歌唱し、歌詞同期・調声・楽器置換・編曲・ミックス・品質検査まで一貫処理する制作基盤です。**Windows実機の技術検証はVOCALOID7体験版＋asa歌声で実施**しており、初音ミク V6を用いた完成パイプラインは今後の目標です。

A proposed automated music production architecture integrating Suno Studio, Hatsune Miku V6, VOCALOID6, VS Code, GitHub Copilot, Python, MCP, REAPER and VST3. The project explores reproducible music production using a common Song IR (JSON), independent production stages, quality gates and recovery paths.

**Status (2026-11-25): Phase-0 implemented; native Suno MIDI → VOCALOID7 asa 10-second proof-of-concept verified on Windows.** The user ran the direct stdio MCP process, which generated a real 44.1 kHz singing WAV and editable `.vprx`. This does **not** establish accurate reproduction of the Suno lead melody or an automated full-song production engine. One-click full-length production and Hatsune Miku integration remain goals.

![AI VOCALOID STUDIO architecture](images/architecture.png)

## Architecture / 技術構成

| Layer | Design |
| --- | --- |
| Input | Verified official Suno MCP MIDI retrieval and lyrics alignment for a user-owned track; local MIDI caching; stems retrieved in Suno library |
| Development | VS Code + GitHub Copilot |
| Execution | Python Production Engine; CLI, MCP and UI Automation as appropriate |
| Analysis | Vocal2Midi, RMVPE, mido |
| Data contract | Song IR (JSON): notes, lyrics, phonemes, pitch, tempo and time |
| Singing | Verified VOCALOID7 7.0.1.1 native stdio MCP + installed `asa` AI voice on Windows; Hatsune Miku V6 and production-grade full-song flow not yet verified |
| Arrangement | REAPER (ReaScript / CLI), VST3 instruments |
| Quality | Lyrics and timing checks, human listening, logging, recovery and reproducibility |

## Data flow / 制作フロー

**Proved limited path:** Suno MIDI + word alignment → heuristic opening vocal candidate (24 notes) → VOCALOID7 native asa synthesis → real 10-second WAV + editable VPRX. **Proposed full path:** Suno → MIDI/WAV/lyrics → analysis and alignment → Song IR → VOCALOID score and singing WAV → REAPER/VST3 → quality checks → WAV/FLAC/MP3.

## Native VOCALOID7 PoC verified（2026-11-25）

Windowsの実機で、オフィシャルSuno MCPから取得した「何もなかったように青い」のMIDIを再利用し、直接stdioのVOCALOID7 MCP経由でasaの歌唱データを合成しました。**実音声のある10.0秒WAV**（44.1kHz/mono/16-bit）と**編集可能なVPRX**を出力し、MCPの`score_compose` → `project_edit` → `project_ai_adjust` → `project_audio mixdown` → `project_save`まで動作を確認しています。対象は原曲196.4秒のうち冒頭の短い試験区間です。

**検証範囲の注意:** MIDIの`Synth Choir`トラックを歌声候補とする試作です。原曲の歌メロを正しく抽出できているか、歌詞・音高・音色の忠実度は**未検証**。全曲自動変換も未実装です。録音・プロジェクト・MIDI本体は`.gitignore`で除外し、GitHubには載せません。

- [Windowsの実行記録・音声のSHA-256・制限事項](docs/VERIFICATION_2026-11-25.md)
- [実行スクリプト（取得済みMIDI再利用：`--reuse-midi`）](tools/render_suno_v7_preview.py)
- [直接stdio MCP接続検査](tools/probe_vocaloid7_direct.py)
- [VOCALOID7 MCP構築手順](docs/VOCALOID7_MCP_SETUP.md)
- [Suno実曲からVOCALOID7に変換する試験仕様](docs/SUNO_TO_VOCALOID7_REAL_SONG.md)
- [Draft PR #1：mainへの統合は未実施](https://github.com/Gacky-Lab/AI-VOCALOID-STUDIO/pull/1)

## Executable Phase-0 interfaces（2026-11-24）

実際に実行できる**MIDI→音符候補（Mido）**、歌詞Handoff v1の照合、2種のJSON Schema、オフライン自動テストを追加しました。ここで得られる音符候補は**歌詞・モーラ未整列**であり、完成したSong IRやVOCALOID歌唱音声とは異なります。

- [公開IFの根拠と検証状況](docs/INTERFACES_VERIFIED_2026-11-24.md)
- [15秒の合成MIDIで試す](docs/PHASE0_OFFLINE.md)
- [REAPERの公式ReaScriptに沿ったWAV配置スクリプト生成](docs/REAPER_IMPORT_BRIDGE.md)（GUI実行は未検証）
- [Actionsの実行結果](https://github.com/Gacky-Lab/AI-VOCALOID-STUDIO/actions)

## 接続方式を実測状況で層別

[推奨・条件付き・代替・不採用の選定表とFail-Closed選定コード](docs/INTERFACE_SELECTION.md)、[Windows読み取り専用環境チェック](docs/ENVIRONMENT_PREFLIGHT.md)を追加。実機の成功証拠がなければ`BLOCKED`とし、仮のプロファイルを渡してもWindows実機の動作成功とは表示しません。

## Documents / 公開資料

- [Integrated design specification (Japanese)](docs/design.md) — 統合設計仕様書、詳細仕様、試験計画、データ契約、可視化契約。
- [Architecture PNG (4K)](images/architecture.png) — HTMLから生成した設計図。
- [Architecture HTML source](docs/architecture.html) — ダウンロードしてブラウザで開くと閲覧できます（GitHubのファイル画面はHTMLソース表示）。
- [Original concept illustration](images/original-concept.png) — Gackyの透かし入り構想図。画像生成AIを用いた初期の説明資料であり、最新の技術仕様はMDを優先します。
- [Visualization validation report](docs/render-report.json) — 可視化資料の参照環境での検査証跡。音楽制作エンジンの実機試験結果ではありません。

## Design principles / 設計思想

製造業の生産技術・DXの考え方を音楽制作に応用する。単にAIで曲を生成するだけでなく、複数の音楽制作技術を接続した再現性のある制作基盤を目指す。

- Preserve original source materials; keep deterministic processing independent of the development assistant.
- Distinguish supported external features, unofficial integrations and locally verified behavior.
- Provide manual fallbacks, logs and checkpoints; require human approval before release.
- Initial test: a 15-second vocal render with the licensed Hatsune Miku voicebank. Automated completion and quality thresholds are acceptance targets, not measured achievements.

## Project history / 公開記録

- 2026-11-24: [Initial concept announcement on X (Gacky)](https://x.com/VG4HsenZZY/status/2125190195372794254).
- 2026-11-25: Verified Suno MIDI → native VOCALOID7 trial asa 10-second WAV and editable VPRX on user's Windows PC (feature branch, not merged).
- This repository collects the design-stage documentation. GitHub publication and subsequent changes are recorded by commit history. The attached specification preserves the original pre-publication wording.

## Author / Links

- Gacky — [X / @VG4HsenZZY](https://x.com/VG4HsenZZY)
- [Gacky-Lab](https://github.com/Gacky-Lab)

## Scope and rights / 権利・注意事項

This is an independent design project, not an official product or partnership with Suno, Yamaha, Crypton Future Media, GitHub, Cockos or other tool providers. Product names and character imagery belong to their respective rights holders. No voicebank, commercial software, third-party music or access credentials are distributed here. Use only legally authorized materials. No blanket reuse license is granted by this initial documentation release; third-party material remains subject to its own terms.
