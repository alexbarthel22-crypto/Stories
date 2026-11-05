"""Eigenes, lizenzfreies Serien-Thema „Alex ist heute“ (komplett per Code synthetisiert).

Lo-Fi-Loop, 96 BPM, Am–F–C–G. Einprägsame 4-Takt-Melodie (Glockenspiel), weiche Keys,
Bass, leise Kick/Shaker. Keine Samples, keine fremden Aufnahmen -> keine Lizenzfragen.

    from music import theme
    m = theme(seconds, sr)          # numpy-Array, Spitze ~1.0
"""
import numpy as np
from scipy.signal import butter, sosfilt

BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT

CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]   # Am F C G (MIDI)
BASS = [45, 41, 36, 43]
# Hook: (Takt, Schlag, MIDI, Länge in Schlägen)
MELODY = [(0, 0, 76, 1), (0, 1, 79, 1), (0, 2, 81, 1.5), (0, 3.5, 79, .5),
          (1, 0, 77, 1), (1, 1, 76, 1), (1, 2, 72, 2),
          (2, 0, 76, 1), (2, 1, 79, 1), (2, 2, 84, 1.5), (2, 3.5, 83, .5),
          (3, 0, 79, 1), (3, 1, 76, 1), (3, 2, 74, 2)]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _tone(f, dur, sr, partials, decay, attack=0.004):
    t = np.arange(int(dur * sr)) / sr
    y = sum(a * np.sin(2 * np.pi * f * r * t) for r, a in partials)
    env = np.minimum(1, t / attack) * np.exp(-t * decay)
    return y * env


def _add(buf, sig, t0, sr, g=1.0):
    i = int(t0 * sr)
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += g * sig[: j - i]


def _loop(sr, with_melody=True, seed=0):
    n = int(4 * BAR * sr)
    keys, bass, mel, drums = (np.zeros(n) for _ in range(4))
    rnd = np.random.default_rng(seed)
    for b in range(4):
        t0 = b * BAR
        for beat in (0, 1.5, 2, 3.5):                         # synkopierte Keys
            for m in CHORDS[b]:
                _add(keys, _tone(hz(m), 1.2, sr, [(1, 1), (2, .35), (3, .12)], 3.2), t0 + beat * BEAT, sr,
                     0.55 if beat in (0, 2) else 0.35)
        for beat, g in ((0, 1), (2, .8), (3.5, .5)):
            _add(bass, _tone(hz(BASS[b]), 0.9, sr, [(1, 1), (2, .25)], 2.6, 0.01), t0 + beat * BEAT, sr, g)
        for beat in (0, 2):                                    # weiche Kick
            tt = np.arange(int(0.25 * sr)) / sr
            k = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-tt * 30)) / sr) * np.exp(-tt * 14)
            _add(drums, k, t0 + beat * BEAT, sr, 0.9)
        for e in range(8):                                     # Shaker
            sh = rnd.standard_normal(int(0.05 * sr)) * np.exp(-np.arange(int(0.05 * sr)) / sr * 70)
            _add(drums, sh, t0 + e * BEAT / 2, sr, 0.06 if e % 2 else 0.03)
    if with_melody:
        for bar, beat, m, L in MELODY:
            _add(mel, _tone(hz(m), L * BEAT + 0.6, sr, [(1, 1), (2.76, .25), (5.4, .08)], 4.5, 0.002),
                 bar * BAR + beat * BEAT, sr, 0.9)
    lp = butter(2, 3200, "lowpass", fs=sr, output="sos")      # Lo-Fi-Wärme
    out = sosfilt(lp, 0.55 * keys + 0.75 * bass + 0.5 * mel + 0.45 * drums)
    return out


def theme(seconds, sr=44100):
    """Theme in gewünschter Länge: Loops mit/ohne Melodie im Wechsel, weich ein- und ausgeblendet."""
    parts, total, i = [], 0, 0
    while total < seconds * sr:
        p = _loop(sr, with_melody=(i % 2 == 0), seed=i)
        parts.append(p); total += len(p); i += 1
    y = np.concatenate(parts)[: int(seconds * sr)]
    fi, fo = int(1.2 * sr), int(2.0 * sr)
    y[:fi] *= np.linspace(0, 1, fi)
    y[-fo:] *= np.linspace(1, 0, fo) ** 2
    return y / (np.abs(y).max() + 1e-9)


if __name__ == "__main__":
    import sys, soundfile as sf
    sf.write(sys.argv[1], theme(float(sys.argv[2]) if len(sys.argv) > 2 else 20), 44100)
