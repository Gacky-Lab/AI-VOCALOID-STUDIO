# 接続方式の層別とFail-Closed選定（2026-11-25）

**この資料は機種の購入・導入を自動的に承認しない。** GitHubのオフラインCI・メーカー公表仕様・コミュニティ実装・Windows実機受入は4種類の異なる証拠である。新しい外部APIや実機成功を推定しない。

## 接続する技術の分類

| 層 | 現時点の採用候補 | 判定・制約 |
|---|---|---|
| Suno出力 | **Suno Studioから手動MIDI/WAV取得**を優先 | 実際のStudioアクセス権と書出し成功を記録。Suno MCPは認証後のtools/listが必要。公式MCPの存在だけではVPR生成可とはしない |
| 歌詞受渡し | **Lyric Handoff v1** | 独自JSON、歌詞版IDとSHA照合。両リポジトリ間のCIは成功済み |
| 音符候補 | **MidoでMIDIを検証・抽出** | 合成fixtureでCI成功。生歌唱しかなければVocal2Midiは探索的候補 |
| 歌詞整列 | **人によるモーラ／音符対応のレビュー** | Song IR Schema合格が必須。自動整列の品質は未検証 |
| 歌唱 | **正規Editor＋初音ミクV6での15秒手動試験が最優先** | V6 FullならDAWプラグイン可、Liteはスタンドアロン最大2トラック・VST3不可 |
| 歌唱の無人化 | **非公式VOCALOID6 MCPは条件付き** | Editorビルド・ツールSchema固定・3回独立レンダリングの実証がない限り未採用 |
| 代替Editor | **VOCALOID7手動取込** | 公式VPR/VSQX読込は確認済み。V6用非公式MCP互換は未確認 |
| ミックス | **REAPERの手動操作を最初の合格経路** | ReaScript用Lua生成はCI成功。GUIでの素材読戻し・異常復旧は未検証 |

## 重要な設計選択

1. **推奨：File-first**。Suno→ローカルWAV/MIDI→音符候補→整列済み楽譜→手動VOCALOID→REAPER。サブスクリプション・認証・ファイル実体のチェックを必須にする。
2. **条件付き：MCP-first**。Suno MCPの公式URLが存在しても、書出しツールが接続中のアカウントに存在するかはtools/listで確認。非公式VOCALOID6 MCPはコミュニティによる実装であり、実機検査前の本番利用は禁止。
3. **代替：VOCALOID7**。公式がVPR/VSQX読込を案内。ただし同じ歌声になるか、V6用MCPが流用できるかは実機で確かめる。
4. **不採用：V6 Editor LiteのVST3・MIDI候補を完成Song IRとみなす経路**。公式仕様・Song IR必須条件に反する。

## 実行できる選定器

    python tools/select_interface_routes.py --profile examples/interface_profiles/no_windows_evidence.json
    python tools/select_interface_routes.py --profile examples/interface_profiles/offline_demo.json
    python tools/select_interface_routes.py --profile examples/interface_profiles/hypothetical_lite.json

設定・選択基準：[`config/interface_routes.v1.json`](../config/interface_routes.v1.json)。

`asserted_true`は利用者が入力した**仮の申告**。機器・ライセンス・手動歌唱の真正性を自動調査していない。生体音声の合格証拠は別途必要。標準出力の`actual_windows_acceptance`は常に`NOT_RUN`。完成が未確認の経路はBLOCKED、条件を入力した場合でも`CONDITIONAL_USER_ASSERTIONS`を返す。

## 外部根拠（2026-11-25確認）

- [Suno StudioのMIDI/WAV等の書出し](https://help.suno.com/en/articles/13925249)
- [Suno MCP FAQ・エンドポイント](https://help.suno.com/en/articles/14486145)
- [VOCALOID6 EditorのLite／Full対応表](https://www.vocaloid.com/vocaloid6/specs/)
- [VOCALOID7の旧プロジェクト読込](https://www.vocaloid.com/support/faq/932)
- [非公式VOCALOID6 MCP](https://github.com/Tehcnological/vocaloid6MCP)
- [Vocal2Midi](https://github.com/Xiantaidu/Vocal2Midi)
- [REAPER ReaScript API](https://www.reaper.fm/sdk/reascript/reascripthelp.html)

外部資料の存在だけでは、対象ユーザー環境での動作合格にはならない。
