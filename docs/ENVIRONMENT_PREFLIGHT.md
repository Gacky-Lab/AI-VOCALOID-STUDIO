# Windows実機への導入前チェック（読み取り専用）

最初にローカルPCで`python tools/environment_preflight.py --workspace .`を実行する。OS名・CPU表示名・RAM容量・作業ドライブの空き容量を読み取り、VOCALOID6のメーカー公表要件と概略比較する。**プログラムの導入・ログイン・ライセンス認証・MCP接続は一切行わない。**

## 公式システム要件の根拠

- [VOCALOID6 Editor動作環境](https://www.vocaloid.com/en/vocaloid6/specs/)：Windows 11 22H2以降（64bit）、Intel Core第4世代以降/Xeon、最低8GB、空き25GB。認証にインターネットが必要。
- [初音ミクV6](https://www.vocaloid.com/en/news/news_34/)はVOCALOID6 6.12以上が前提。ボイスバンクは単独では動かない。
- [VOCALOID6 Editor Lite](https://www.vocaloid.com/vocaloid6/specs/)はスタンドアロンのみ、最大2トラックでVST3不可。
- [VOCALOID7互換](https://www.vocaloid.com/support/faq/932)はVPR/VSQXの取り込みを案内。非公式V6 MCPが動くかは未確認。

## 仕様上の限界

- `os_release`の表示だけではWindows 11 22H2以降のビルド番号まで判定しない。
- `cpu_description`にIntelと表示されても世代要件をチェックしない。AMD環境は非対応と断定せず、メーカーの対象製品・体験版で互換性を確認する。
- REAPERがPATHにないだけでは未インストールと判断しない。
- メモリ・ディスクが最低値以上でも、VST3の要求、音声認識モデル、オーディオインターフェース、認証環境などの互換性は保証されない。
- 判定結果の`actual_voice_render`と`actual_reaper_import`は**常にNOT_RUN**。実音源のSHA・手動試聴・REAPER再読込が必要。
- PC名、ユーザー名、ライセンスキー、アクセストークン、認証情報をレポートに収録しない。

## 接続方式を選ぶ流れ

1. 環境の概略情報を収集する。
2. [接続方式の選定器](INTERFACE_SELECTION.md)に必要条件を入力する（メーカー仕様や本人申告は実機証跡ではない）。
3. 正規Editorと初音ミクV6のライセンスを確認し、**15秒の手動WAV出力**で実機の成立性を確かめる。
4. 同一のテストファイルをREAPERに読み込み、楽譜と音声の時間原点・再生・再保存を検証する。
5. その後に非公式MCPのschema固定と3回独立試験へ進む。
