# ピクニック・オン・ムーン ｜ 初音ミクV6 実機制作例

**[試聴プレーヤーを開く（フル・サビ・調声前後）](https://gacky-lab.github.io/AI-VOCALOID-STUDIO/)**

[ミク版フルを聴く（MP3・3分48秒）](https://raw.githubusercontent.com/Gacky-Lab/AI-VOCALOID-STUDIO/codex/picnic-miku-listening/examples/picnic-miku/full-mix.mp3) · [原曲をSunoで聴く](https://suno.com/song/07a71f55-32c9-40bd-8c00-d95b62ab8fbc) · [調声前後を聴く（WAV）](https://raw.githubusercontent.com/Gacky-Lab/AI-VOCALOID-STUDIO/codex/picnic-miku-listening/examples/picnic-miku/tuning-comparison.wav)

原曲「ピクニック・オン・ムーン (Cover)」の伴奏に、VOCALOID7で合成した初音ミクV6の歌唱を合わせた研究用の試聴版です。主旋律とユニゾンにはMIKU ORIGINAL、ハモリにはMIKU SOFTを使用しています。[歌詞と音符を開く（VOCALOID編集譜面）](./miku-expression.vprx)

## 同じ歌詞で聴き比べる

原曲とミク版をそれぞれ **0:54.6** から再生すると、サビの言葉の入り方、伸ばす母音、語尾を比較できます。調声前後の短いWAVには、そこから6.15秒間の **旧ミク版 → 短い無音 → 今回のミク版** を収録しました。比較区間の実効音量をそろえています。

## 制作と検証の範囲

- サビは原唱のボーカルステムを53.50秒から25.73秒間解析。10ミリ秒間隔の基本周波数から103音符候補を得て、歌詞の時刻とかな読みを割り当て、100音符に整理しました。音高を近傍音で補った箇所は3か所です。
- フル尺には既存ボーカルMIDIも使用し、調声したサビを2か所に配置しました。ハモリとユニゾンは制作側で配置したトラックです。
- 語尾33音では原唱と旧ミク版の音量変化を参照し、主旋律のExpressionと息成分を調整しました。歌声を書き出した後、伴奏との音量バランスと残響を整えています。編集譜面では歌唱を編集でき、MP3では伴奏・後処理込みの結果を確認できます。
- 本例は1曲の制作記録です。採譜の正答率、別環境での再生成、最終的な歌唱品質の第三者評価は未検証です。
