# 外部インターフェース監査（2026-11-24）

公式製品の機能、非公式接続、Gacky-Lab独自フォーマット、ローカル動作成功は別レベルの証拠。GitHub Actionsのオフライン試験は**実機の歌声合成成功ではありません**。

| 対象 | 公開資料 | このリポジトリの状況 | Windows実機 |
|---|---|---|---|
| Suno StudioのMIDI/WAV・ステム書出し | [公式ヘルプ](https://help.suno.com/en/articles/13925249) | 保存済みSMFを入力。ダウンロード自動化なし | NOT_RUN |
| Suno MCP | [概要](https://help.suno.com/en/articles/14551361)、[接続](https://help.suno.com/en/articles/14551425) | 公式URL https://api.suno.com/mcp は存在。認証後のtools/listを取得するまで呼出名・引数を固定しない | NOT_RUN |
| Standard MIDI File / テンポ・拍子 | [Mido API](https://mido.readthedocs.io/en/stable/api.html) | 1トラック選択、全トラックからテンポと拍子を抽出、絶対tick→48kHzサンプルへ変換 | オフラインCI対象 |
| VOCALOID6のVSQX/VPR読込 | [公式FAQ](https://www.vocaloid.com/en/support/faq/603) | ファイル形式の存在を確認。エディターへの自動投入は未実装 | NOT_RUN |
| VOCALOID7のVSQX/VPR読込 | [公式FAQ](https://www.vocaloid.com/support/faq/932) | V6用非公式MCPのV7互換は仮定しない | NOT_RUN |
| VOCALOID6非公式MCP | [公開実装](https://github.com/Tehcnological/vocaloid6MCP) | バージョン固定、tools/list、音源ID、GUI動作を自環境で試験する必要あり | NOT_RUN |
| REAPER | [公式ReaScript API](https://www.reaper.fm/sdk/reascript/reascripthelp.html) | WAV配置Luaの生成器とテストを追加。REAPER本体の実行は未実施 | NOT_RUN |

## データ契約上の重要な区別

- 新規実装のMIDI抽出結果は『未整列音符候補』。既存の[マスターSong IR](design.md)ではモーラと音符の対応が必須であり、候補をSong IR完成と見なさない。
- MIDIのnote-on/offは音声の発音境界ではない。サスティン、ピッチベンド、発音の立ち上がりを含まない。
- 歌詞HandoffはGacky-Lab内部JSON。Suno MCPやVOCALOIDのAPIリクエストと取り違えない。
- 非公式MCPの導入はコミット固定、権利確認、未保存のGUIプロジェクトの保全、実機受入試験を行うまで保留。
- 最初の実機受入は15秒、同一音符・同一音源、手動WAV出力から開始。合否未確定のまま成功率を表示しない。
