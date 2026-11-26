"""Measure the published excerpts using the original song clock."""
import csv
import json
from pathlib import Path

import numpy as np
import parselmouth
import soundfile as sf

ROOT = Path(__file__).resolve().parent
SR = 48000
sources = json.loads((ROOT / "sources.json").read_text())
audio = {}
for name in sources:
    x, rate = sf.read(ROOT / (name + ".flac"), dtype="float32", always_2d=True)
    assert rate == SR and x.shape == (20 * SR, 2)
    audio[name] = x

t = np.arange(96 * SR, 116 * SR, 240) / SR
centers = np.rint((t - 96) * SR).astype(int)


def pitch(name):
    # Full duration preserves Praat's centered analysis grid on cropped data.
    samples = np.zeros(sources[name]["frames_full"])
    samples[96 * SR:116 * SR] = audio[name].mean(axis=1)
    p = parselmouth.Sound(samples, SR).to_pitch_ac(
        time_step=.005, pitch_floor=100, pitch_ceiling=950)
    ids = np.rint((t - p.x1) / p.dx).astype(int)
    return p.selected_array["frequency"][ids]


def reference_peak(mono, center, low, high):
    spectrum = abs(np.fft.rfft(mono[center-1152:center+1152] * np.hanning(2304), 16384))
    peaks = np.flatnonzero((spectrum[1:-1] > spectrum[:-2]) &
                           (spectrum[1:-1] >= spectrum[2:])) + 1
    peaks = peaks[(peaks >= low * 16384 / SR) & (peaks <= high * 16384 / SR)]
    if not len(peaks):
        return None
    k = peaks[np.argmax(spectrum[peaks])]
    if spectrum[k] < max(2, .08 * spectrum.max()):
        return None
    a, b, c = np.log(spectrum[k-1:k+2] + 1e-12)
    shift = .5 * (a-c) / (a+c-2*b+1e-12)
    return (k + np.clip(shift, -.5, .5)) * SR / 16384


def level(stereo):
    energy = np.mean(stereo**2, axis=1, dtype=np.float64)
    sums = np.r_[0, np.cumsum(energy)]
    left = np.maximum(0, centers-480)
    right = np.minimum(len(energy), centers+480)
    return 10*np.log10((sums[right]-sums[left])/(right-left)+1e-12)


before, after = pitch("before"), pitch("after")
ref = audio["reference"].mean(axis=1)
results = {}
frames = []
for word, start, end, low, high in [
    ("We", 105.800, 105.890, 475, 569),
    ("flowed_start", 106.025, 106.075, 695, 830),
    ("flowed_end", 106.150, 106.230, 695, 830),
]:
    rows = []
    for i in np.flatnonzero((t >= start) & (t <= end)):
        hz = reference_peak(ref, centers[i], low, high)
        values = [round(float(v), 1) if v else None for v in (hz, before[i], after[i])]
        rows.append(values)
        frames.append([word, t[i], *values])
    results[word] = [round(float(np.median([v for v in col if v is not None])), 1)
                     for col in zip(*rows)]

ref_db, inst_db, band_db = [level(audio[n]) for n in ("reference", "instrumental", "band")]
old, new = [level(audio[n]-audio["band"]) for n in ("mix-before", "mix-after")]
near = ((abs(t-106) < 2.5) & ((t < 105.61) | (t > 106.38)) &
        (old > -43) & (ref_db > -38) & (inst_db > -42))
body = (t >= 105.79) & (t <= 106.27) & (ref_db > -36)
delta = [v-band_db-(ref_db-inst_db) for v in (old, new)]
context = np.median(delta[0][near])
results["context_error_db"] = [round(float(np.median(abs(d[body]-context))), 2) for d in delta]
if __name__ == "__main__":
    import sys
    writer = csv.writer(sys.stdout)
    writer.writerow(["region", "song_seconds", "reference_Hz", "before_Hz", "after_Hz"])
    writer.writerows(frames)
    print(json.dumps(results), file=sys.stderr)
    if results != json.loads((ROOT / "expected.json").read_text()):
        raise SystemExit("Mismatch with published medians")
