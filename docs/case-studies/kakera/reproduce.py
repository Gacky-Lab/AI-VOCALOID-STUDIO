"""Recompute the published boundary metrics with Python 3.10+."""
import csv
import json
import math
from bisect import bisect_left
from pathlib import Path
from statistics import mean, median, quantiles

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def summarize(pairs):
    columns = list(zip(*pairs))
    return {
        "count": len(pairs),
        "median": [median(c) for c in columns],
        "mean": [mean(c) for c in columns],
        "p90": [quantiles(c, n=10, method="inclusive")[8] for c in columns],
    }


def main():
    phones = rows("phones.csv")
    score = rows("score-audit.csv")
    # Keep the last phoneme in each note in alignment order.
    last_phone = {int(r["音符"]): r for r in phones if r["音符"]}
    track = rows("pitch.csv")
    times = [float(r["seconds"]) for r in track]
    assert times == [i / 200 for i in range(38440)]
    assert sorted(last_phone) == [int(r["id"]) for r in score] == list(range(1, 589))
    pitch = []
    for r in track:
        hz = [r[col] for col in ("reference_Hz", "before_Hz", "after_Hz")]
        pitch.append([1200 * math.log2(float(v) / 440) for v in hz] if all(hz) else None)
    spacing, target, leaps = [], [], []
    previous_onsets = previous_pitch = None
    for note in range(1, len(score) + 1):
        ph = last_phone[note]
        onsets = [float(ph[s + "開始 秒"]) for s in ("原唱", "直前", "新版")]
        a, b = bisect_left(times, onsets[0]), bisect_left(times, float(ph["原唱終了 秒"]))
        common = [v for v in pitch[a:b] if v is not None]
        current_pitch = [median(c) for c in zip(*common)] if len(common) >= 5 else None
        if previous_onsets is not None:
            step = [(y - x) * 1000 for x, y in zip(previous_onsets, onsets)]
            error = [abs(v - step[0]) for v in step[1:]]
            spacing.append(error)
            if 15 <= note <= 24:
                target.append([round(v) for v in error])
            if previous_pitch is not None and current_pitch is not None:
                delta = [y - x for x, y in zip(previous_pitch, current_pitch)]
                leaps.append([abs(v - delta[0]) for v in delta[1:]])
        previous_onsets, previous_pitch = onsets, current_pitch
    result = dict(spacing=summarize(spacing), target_spacing=summarize(target),
                  pitch_step=summarize(leaps), worse_40=sum(round(b)-round(a) >= 40 for a, b in spacing))
    expected = json.loads((HERE / "comparison.json").read_text())
    for group in ("spacing", "target_spacing", "pitch_step"):
        assert result[group]["count"] == expected[group]["count"], group
        for key in ("median", "mean", "p90"):
            for got, want in zip(result[group][key], expected[group][key], strict=True):
                assert math.isclose(got, want, abs_tol=1e-7), (group, key, got, want)
    assert result["worse_40"] == expected["worse_40"]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
