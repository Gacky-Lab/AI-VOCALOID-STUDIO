# REAPERの公式ReaScript APIへの受渡し（実機実行は未検証）

本リポジトリの[ローカルジョブJSON Schema](../schemas/reaper_import_job.v1.schema.json)は独自設計であり、REAPERが直接JSONを読めるという意味ではありません。Pythonが事前検査を行い、REAPERで手動実行するLuaを生成します。

## 操作手順

1. 権利のあるWAVファイルをPCへ保存し、コピーしたREAPERプロジェクトを準備する。
2. 次の形式のJSONを作成し、WAVのパスを指定する（source_pathはJSONからの相対または絶対パス）。

    {"job_version":"1.0.0","tracks":[{"name":"Instrumental","source_path":"backing.wav","position_seconds":0}]}

3. `python tools/build_reaper_import.py --job path/to/job.json --output work/reaper_import.lua` を実行。
4. REAPERのActions → ReaScript: Load...でLuaを読み込み、保存済みの作業コピー上で実行する。
5. トラック名・ファイル・配置位置・波形・長さ・再生を目視・試聴確認。必要ならUndoし、ログを残す。

## 実装が実際に使う公式API

- [reaper.PCM_Source_CreateFromFile](https://www.reaper.fm/sdk/reascript/reascripthelp.html) — WAVのソース取得。
- reaper.InsertTrackAtIndex、GetTrack、GetSetMediaTrackInfo_String — トラックの追加・命名。
- reaper.AddMediaItemToTrack、AddTakeToMediaItem、SetMediaItemTake_Source — メディアの配置。
- reaper.GetMediaSourceLength、SetMediaItemInfo_Value — 長さ・時間位置の設定。

事前にWAVの存在を確認してLuaに絶対パスを書き込みますが、再生可否・素材の実フォーマット・プロジェクトの状態は**REAPERで実行しないと確定しません**。作業コピーを推奨します。GUIの操作成功、VST3音源の読込、混合、マスタリング、headlessレンダーまでは実装していません。

作成したLuaにはPCの絶対パスが入ります。**GitHubにコミットしない**でください。
