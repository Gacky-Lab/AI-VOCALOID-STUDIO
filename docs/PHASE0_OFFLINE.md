# オフラインで試せる実インターフェース（Phase 0）

## Windows PowerShell / macOS / Linux

Python 3.11以上。Mido 1.3.3とJSON Schema検証用ライブラリを導入。

    python -m pip install -r requirements-dev.txt
    python -m unittest discover -s tests -v
    python tools/make_phase0_midi.py --output work/phase0/probe.mid
    python tools/midi_candidates.py --midi work/phase0/probe.mid --song-id phase0 --track-index 1 --output work/phase0/candidates.json

合成probe.midは**歌声ではない**。PPQ480、BPM120、15秒、トラック0にテンポ・拍子、トラック1にC4/E4/G4。1、6、12秒からそれぞれ0.5秒の音符。48kHz基準の開始位置は48000、288000、576000サンプル、音源全長720000サンプル。

実際のSuno Studioから合法的に手動取得したMIDIを使用する場合は、意図するリードボーカルトラックを解析し、0始まりのtrack-indexを**手動指定**。複数トラックから自動的にメロディーを決定したとは主張しない。

## LYRIC-DESIGN-FRAMEWORKとの連携

歌詞側が出力したHandoff v1を使う場合、両方に同じsong_idを指定。

    python tools/verify_handoff.py path/to/handoff.json --song-id phase0
    python tools/midi_candidates.py --midi work/phase0/probe.mid --song-id phase0 --track-index 1 --lyric-handoff path/to/handoff.json --output work/phase0/candidates_with_ref.json

この段階は歌詞の版IDと本文SHAの**参照結合**だけを行う。音符への歌詞割当・音素解析・VOCALOID再歌唱・REAPERの実行は別工程で、未実装／実機検証待ち。

## 今後の実機試験

正規のVOCALOID Editorと初音ミクV6の利用可能性をまず確認し、手動で15秒の歌唱を出力。次に非公式MCPのバージョンと実tools/listを記録し、同一素材で3回の独立レンダリングを検証する。失敗したら手動経路で継続し、無人成功としては集計しない。
