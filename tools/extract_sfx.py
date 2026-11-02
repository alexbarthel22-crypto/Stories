"""Extrahiert die Auswahl-Sound-Effekte (Ticks + Reveal-Burst) aus dem Referenzvideo.

Nutzung: python3 extract_sfx.py <referenz-audio.wav> <ausgabe-ordner>
"""
import sys, json, os
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, find_peaks, stft, istft
from scipy.ndimage import median_filter

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
a, sr = sf.read(src)
if a.ndim > 1:
    a = a.mean(1)

# --- 1) Tick-Zeitpunkte: schmalbandige Energie um 1914 Hz (Grundton 957 Hz)
sos = butter(4, [1820, 2010], 'bandpass', fs=sr, output='sos')
b = sosfiltfilt(sos, a[: int(1.5 * sr)])
env = np.sqrt(np.convolve(b ** 2, np.ones(int(0.004 * sr)) / int(0.004 * sr), 'same'))
d = np.diff(env, prepend=0)
peaks, _ = find_peaks(env, height=env.max() * 0.25, distance=int(0.05 * sr))
# Onset = erster Punkt vor dem Peak, an dem die Hüllkurve 20% des Peaks erreicht
onsets = []
for p in peaks:
    i = p
    while i > 0 and env[i] > env[p] * 0.2:
        i -= 1
    onsets.append(i / sr)
print('Tick-Onsets:', [round(t, 3) for t in onsets])

# --- 2) Sauberer Tick: der letzte (keine Stimme darunter)
last = onsets[-1]
t0 = int((last - 0.004) * sr)
t1 = int((last + 0.13) * sr)
tick = a[t0:t1].copy()
fade = int(0.03 * sr)
tick[-fade:] *= np.linspace(1, 0, fade) ** 2
tick[: int(0.001 * sr)] *= np.linspace(0, 1, int(0.001 * sr))
sf.write(f'{out}/tick.wav', tick, sr)

# --- 3) Reveal-Burst (1.53 s – 2.55 s): Stimme spektral entfernen.
# Rauschen ist über die Frequenz glatt, Sprach-Harmonische sind spitz -> Medianfilter
# über die Frequenzachse schätzt den Rauschanteil, daraus eine weiche Maske.
s0, s1 = int(1.53 * sr), int(2.60 * sr)
seg = a[s0:s1]
f, t, Z = stft(seg, fs=sr, nperseg=2048, noverlap=2048 - 256)
M = np.abs(Z)
noise = median_filter(M, size=(31, 1))           # glatte Hüllkurve je Frame
noise = median_filter(noise, size=(1, 5))         # leicht zeitlich glätten
mask = np.clip(noise / (M + 1e-9), 0, 1) ** 1.5
# Unter 300 Hz liegt kaum Burst, dort vor allem Stimme -> stärker dämpfen
mask[f < 300] *= 0.3
# Bereich 300-3500 Hz (Stimmformanten) zusätzlich etwas dämpfen
band = (f >= 300) & (f < 3500)
mask[band] *= 0.75
_, clean = istft(Z * mask, fs=sr, nperseg=2048, noverlap=2048 - 256)
clean = clean[: len(seg)]
n_in = int(0.03 * sr)
clean[:n_in] *= np.linspace(0, 1, n_in)
n_out = int(0.25 * sr)
clean[-n_out:] *= np.linspace(1, 0, n_out) ** 2
# Pegel an Original-Hochband angleichen
sf.write(f'{out}/reveal.wav', clean, sr)

json.dump({'tick_onsets': onsets, 'flash_start': round(last + 0.06, 3),
           'reveal_onset': 1.57 - 1.53, 'sr': sr}, open(f'{out}/sfx_meta.json', 'w'), indent=1)
print('ok', len(tick) / sr, len(clean) / sr)
