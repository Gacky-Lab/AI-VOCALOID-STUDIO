# 機械可読スキーマ一覧（2026-11-24）

既存の[統合設計仕様書](design.md)に埋め込まれていた7種類のJSON Schemaを、**内容を変えずに独立ファイルとして抽出**した。CIではJSON Schema Draft 2020-12自体の正しさと、マスター文書との構造的一致を検査する。

| マスター仕様 | 用途 |
|---|---|
| [acceptance](../schemas/acceptance.schema.json) | 受入試験台帳・証跡の契約 |
| [manifest](../schemas/manifest.schema.json) | 楽曲入力・アセット・権利の契約 |
| [reaper_job](../schemas/reaper_job.schema.json) | 予定するREAPER実行ジョブ |
| [reaper_result](../schemas/reaper_result.schema.json) | REAPERの実行結果契約 |
| [report](../schemas/report.schema.json) | 品質・承認レポート契約 |
| [song_ir](../schemas/song_ir.schema.json) | 歌詞・モーラと音符の割当済みSong IR |
| [state](../schemas/state.schema.json) | 状態遷移の保存契約 |

## 今回の部分実装用ローカル形式

| 形式 | 用途 |
|---|---|
| [lyric_handoff.v1](../schemas/lyric_handoff.v1.schema.json) | 歌詞全文・版ID・SHAの受渡し |
| [midi_candidates.v1](../schemas/midi_candidates.v1.schema.json) | 歌詞未整列の音符候補・タイミング |
| [reaper_import_job.v1](../schemas/reaper_import_job.v1.schema.json) | WAV素材のREAPER Lua配置準備 |

**重要：** Song IRマスターには空でないmoras・lyric_span_ids等の制約がある。歌詞未整列のMIDI候補を、Song IR完成と扱ってはならない。

スキーマの抽出・オフライン検証は、Windows実機の歌唱・REAPER操作やMCP接続の成功を意味しない。
