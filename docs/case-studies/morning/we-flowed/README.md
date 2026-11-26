# 1分46秒の “We flowed” を聴き比べる

『We Flowed Past the Morning』の **1:36.000–1:56.000**（指摘時刻の前後各10秒）を同じ位置で切り出した。各プレーヤーでは **0:00 原唱 → 0:20.5 初音ミク修正前 → 0:41 初音ミク修正後** の順に流れる。“We flowed” はそれぞれ約 **0:10、0:30.5、0:51**。まず母音の途中で音が下がるかを聴き、次に伴奏に戻して言葉のつながりを確かめてほしい。

- [声だけで比較する（MP3）](https://cdn.jsdelivr.net/gh/Gacky-Lab/AI-VOCALOID-STUDIO@main/docs/case-studies/morning/we-flowed/voices.mp3) · [GitHubの音源](voices.mp3)
- [伴奏ありで比較する（MP3）](https://cdn.jsdelivr.net/gh/Gacky-Lab/AI-VOCALOID-STUDIO@main/docs/case-studies/morning/we-flowed/mixes.mp3) · [GitHubの音源](mixes.mp3)
- [完成MVの該当箇所へ（YouTube）](https://youtu.be/fWGwUCiSeAE?t=96)

試聴用MP3は各テイクの20秒全体でRMSを揃え、端に10 msのフェードをかけ、間に0.5秒の無音を入れた。原曲側の伴奏あり試聴は原唱ステムと伴奏ステムの和。測定にはゲイン変更・フェード前の48 kHzステレオFLACを使う。

## 音符と歌詞を読む

[修正前の譜面](score-before.json)と[修正後の譜面](score-after.json)は、対象区間にかかる主旋律トラックの音符を元VPRXから抜き出したもの。曲頭からの秒、1始まりの音符番号、歌詞・音素、ノートナンバー、長さ、音符内ピッチ曲線を収録した。この譜面では960 tickが1秒。326番の “We” と327番の “flowed” を比較すると、どの音を置き直し、どこを曲線で動かしたか追える。

## 測定を再現する

このフォルダを取得して以下を実行する。VOCALOIDのライセンスを必要とする再合成工程はすでに済んでおり、測定だけならPythonで実行できる。検証環境はWindows、Python 3.12、NumPy 2.5.5、SoundFile 0.14.0、praat-parselmouth 0.4.7。

```sh
python -m pip install numpy==2.5.5 soundfile==0.14.0 praat-parselmouth==0.4.7
python measure.py > reproduced-frames.csv
```

標準出力は5 msごとの測定表、標準エラー出力は中央値。[公開時のフレーム表](frames.csv)と[期待値](expected.json)を同梱し、中央値が不一致なら終了コードが非ゼロになる。[各FLACの由来](sources.json)には元レンダーの長さも記録した。スクリプトはPraatの分析窓の位置を全曲測定時と揃えるため、抜粋の外側を無音で埋める。

| 曲頭からの測定区間 | 原唱の旋律候補 | ミク修正前 | ミク修正後 |
|---|---:|---:|---:|
| We 母音 105.800–105.890秒 | 522.5 Hz | 130.4 Hz | 519.5 Hz |
| flowed 入り 106.025–106.075秒 | 722.6 Hz | 721.2 Hz | 720.9 Hz |
| flowed 後半 106.150–106.230秒 | 785.5 Hz | 659.2 Hz | 785.3 Hz |

原唱は重唱を含むため、このフレーズ用に選んだ帯域のスペクトルピークを採用した。ミクは再合成した声の自己相関で推定した。特に “We” の130.4 Hzにはオクターブ単位の推定誤りの可能性がある。伴奏に対する声量も、前後2.5秒の近傍を基準に追試できる。105.79–106.27秒の有効窓の絶対偏差中央値は **9.05 → 1.57 dB**。歌詞の聞きやすさや自然さの判定は試聴者に委ねる。

[曲全体の設計・測定方法](../README.md)
