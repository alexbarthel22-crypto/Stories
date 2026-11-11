"""Claras Techno-Track (selbst komponiert/synthetisiert -> keine Rechte Dritter).
Echter Techno: 128 BPM, A-Moll, wuchtige Kick + Rumble, Offbeat-Bass, Acid-Linie (resonanter Filter),
Hi-Hats, Clap und ein eingängiges, düsteres Stab-Riff. Nicht fröhlich/euphorisch.
Aufruf: python3 make_music.py [länge_in_s] [ausgabe.wav]"""
import sys, wave
import numpy as np

SR = 44100
LEN = float(sys.argv[1]) if len(sys.argv) > 1 else 32.0
OUT = sys.argv[2] if len(sys.argv) > 2 else "clara_theme.wav"
BPM = 128
BEAT = 60 / BPM
S16 = BEAT / 4
BAR = 4 * BEAT
N = int(LEN * SR)
rng = np.random.default_rng(11)
L, R = np.zeros(N), np.zeros(N)


def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * g * (1 - pan) ** 0.5
    R[i:i + len(sig)] += sig * g * (1 + pan) ** 0.5


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def onepole(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for k in range(len(x)):
        s = (1 - a) * x[k] + a * s; y[k] = s
    return y


def svf_lp(x, fc_curve, q=0.15):
    """Resonanter 2-Pol-Tiefpass (State-Variable) mit Cutoff-Verlauf – für die Acid-Linie."""
    low = band = 0.0; y = np.empty_like(x)
    for k in range(len(x)):
        f = 2 * np.sin(np.pi * min(fc_curve[k], 8000) / SR)
        low += f * band
        high = x[k] - low - q * band
        band += f * high
        y[k] = low
    return y


def saw(f, n):
    t = np.arange(n) / SR
    return 2 * ((t * f) % 1) - 1


# --- Drums
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t / 0.025)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.0008, 0.22)
    click = rng.standard_normal(n) * env(n, 0.0003, 0.003) * 0.4
    return np.tanh(1.8 * (body + click))


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    x = rng.standard_normal(n); x = x - onepole(x, 8000)
    return x * env(n, 0.0004, 0.08 if open_ else 0.014)


def clap():
    n = int(0.2 * SR); x = rng.standard_normal(n)
    x = onepole(x, 3000) - onepole(x, 1000)
    e = env(n, 0.001, 0.06)
    for off in (0.01, 0.02):
        e[int(off * SR):] += 0.7 * env(n - int(off * SR), 0.001, 0.04)
    return x * e


KICK, HAT, OHAT, CLAP = kick(), hat(), hat(True), clap()

# Rumble: verhallte, tiefpassgefilterte Kick-Fahne
_r = np.zeros(int(BEAT * SR)); _r[: len(KICK)] = KICK[: len(_r)]
RUMBLE = onepole(np.convolve(_r, np.exp(-np.arange(int(0.25 * SR)) / (0.08 * SR)) * rng.standard_normal(int(0.25 * SR)) * 0.02)[: len(_r)], 180)
RUMBLE = RUMBLE / (np.abs(RUMBLE).max() + 1e-9)


def bass(m):
    n = int(S16 * 1.8 * SR)
    return onepole(saw(hz(m), n), 260) * env(n, 0.002, 0.07)


BASS = {m: bass(m) for m in (33, 36, 40, 31)}


def acid(m, accent, cut):
    n = int(S16 * 1.1 * SR); t = np.arange(n) / SR
    fc = 200 + cut * (1 + accent) * np.exp(-t / 0.09)
    return np.tanh(2.2 * svf_lp(saw(hz(m), n), fc, 0.12)) * env(n, 0.002, 0.12) * (1 + 0.5 * accent)


def stab(chord, length):
    n = int(length * SR)
    s = sum(saw(hz(m), n) + saw(hz(m) * 1.004, n) for m in chord) / (2 * len(chord))
    return onepole(s, 1800) * env(n, 0.002, 0.11)


# --- Pattern (16tel)
BASS_PAT = [None, None, 33, None, None, None, 33, None, None, None, 33, None, None, None, 36, None]   # Offbeat-Bass
ACID = [(45, 1), (45, 0), (57, 0), (45, 0), (48, 1), (45, 0), (52, 0), (45, 0),
        (45, 1), (57, 0), (45, 0), (55, 0), (45, 1), (48, 0), (45, 0), (52, 0)]
# eingängiges, düsteres Stab-Riff (Am7 / Fmaj7 / Em7) – synkopiert, über 2 Takte
STAB_HITS = [(0, [57, 60, 64, 67]), (3, [57, 60, 64, 67]), (6, [57, 60, 64, 67]), (10, [53, 57, 60, 64]),
             (16, [57, 60, 64, 67]), (19, [57, 60, 64, 67]), (22, [52, 55, 59, 62]), (27, [52, 55, 59, 62])]
ACID_CACHE = {}

bars = int(LEN / BAR) + 1
for b in range(bars):
    t0 = b * BAR
    intro = b == 0
    for k in range(4):
        add(KICK, t0 + k * BEAT, 1.0)
        add(RUMBLE, t0 + k * BEAT + 0.03, 0.35)
        add(OHAT, t0 + k * BEAT + BEAT / 2, 0.22, 0.25)
        if k in (1, 3):
            add(CLAP, t0 + k * BEAT, 0.42, -0.1)
    for k in range(16):
        add(HAT, t0 + k * S16, 0.12 if k % 2 else 0.07, -0.3)
        m = BASS_PAT[k]
        if m is not None:
            add(BASS[m], t0 + k * S16, 0.55)
        if not intro:
            note, acc = ACID[k]
            cut = 900 + 1800 * (0.5 + 0.5 * np.sin(2 * np.pi * (b * 16 + k) / 128))   # langsame Filterfahrt
            key = (note, acc, int(cut / 100))
            if key not in ACID_CACHE:
                ACID_CACHE[key] = acid(note, acc, cut)
            add(ACID_CACHE[key], t0 + k * S16, 0.16, 0.2)
    if b >= 2 and b % 2 == 0:   # Riff ab Takt 3
        for step, ch in STAB_HITS:
            s = stab(ch, S16 * 2)
            add(s, t0 + step * S16, 0.2, -0.15)
            add(s, t0 + step * S16 + 3 * S16, 0.07, 0.4)   # Delay-Echo

# Sidechain-Pumpen auf allem außer der Kick-Spitze
t = np.arange(N) / SR
pump = 0.5 + 0.5 * np.minimum((t % BEAT) / 0.15, 1)
L *= pump; R *= pump
fade = np.minimum(t / 0.03, 1) * np.minimum((LEN - t) / 1.5, 1)
L *= fade; R *= fade
st = np.tanh(1.2 * np.stack([L, R], 1) / max(np.abs(L).max(), np.abs(R).max()))
st = st / np.abs(st).max() * 0.89
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print(OUT, LEN, "s")
