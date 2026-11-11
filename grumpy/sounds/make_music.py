"""Eigener Hintergrund-Track für Clara (selbst komponiert/synthetisiert -> keine Rechte Dritter).
Leichter Minimal-Techno, A-Moll, 122 BPM, trocken-genervte Hook-Melodie (nicht fröhlich).
Aufruf: python3 make_music.py [länge_in_s] [ausgabe.wav]"""
import sys, wave
import numpy as np

SR = 44100
LEN = float(sys.argv[1]) if len(sys.argv) > 1 else 32.0
OUT = sys.argv[2] if len(sys.argv) > 2 else "clara_theme.wav"
BPM = 122
BEAT = 60 / BPM
S16 = BEAT / 4
N = int(LEN * SR)
rng = np.random.default_rng(7)
mixL, mixR = np.zeros(N), np.zeros(N)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    mixL[i:i + len(sig)] += sig * gain * (1 - pan) ** 0.5
    mixR[i:i + len(sig)] += sig * gain * (1 + pan) ** 0.5


def env(n, a=0.003, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for k in range(len(x)):
        acc = (1 - a) * x[k] + a * acc
        y[k] = acc
    return y


def note_hz(n):  # MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)


def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    s = 2 * ((t * f) % 1) - 1
    if detune:
        s = 0.5 * s + 0.5 * (2 * ((t * f * (1 + detune)) % 1) - 1)
    return s


# --- Klänge vorberechnen
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 45 + 85 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.16)


def hat():
    n = int(0.05 * SR)
    x = rng.standard_normal(n)
    x = x - lowpass(x, 7000)
    return x * env(n, 0.0005, 0.012)


def clap():
    n = int(0.18 * SR)
    x = rng.standard_normal(n)
    x = lowpass(x, 2500) - lowpass(x, 900)
    e = env(n, 0.001, 0.05)
    for off in (0.008, 0.016):
        e[int(off * SR):] += 0.6 * env(n - int(off * SR), 0.001, 0.05)
    return x * e


KICK, HAT, CLAP = kick(), hat(), clap()
BASS_CACHE, LEAD_CACHE = {}, {}


def bass(m):
    if m not in BASS_CACHE:
        n = int(S16 * 1.6 * SR)
        BASS_CACHE[m] = lowpass(saw(note_hz(m), n, 0.004), 380) * env(n, 0.004, 0.09)
    return BASS_CACHE[m]


def lead(m, length):
    key = (m, round(length, 3))
    if key not in LEAD_CACHE:
        n = int(length * SR)
        t = np.arange(n) / SR
        vib = 1 + 0.003 * np.sin(2 * np.pi * 5 * t)
        ph = np.cumsum(note_hz(m) * vib) / SR
        tone = 0.6 * (2 * np.abs(2 * (ph % 1) - 1) - 1) + 0.4 * (2 * (ph % 1) - 1)   # Dreieck + Säge
        LEAD_CACHE[key] = lowpass(tone, 2200) * env(n, 0.005, 0.22)
    return LEAD_CACHE[key]


def pad(chord, length):
    n = int(length * SR)
    s = sum(saw(note_hz(m), n, 0.006) for m in chord) / len(chord)
    a = np.minimum(np.arange(n) / (0.4 * SR), 1) * np.minimum((n - np.arange(n)) / (0.4 * SR), 1)
    return lowpass(s, 900) * a


# --- Arrangement
BAR = 4 * BEAT
bars = int(LEN / BAR) + 1
BASS_PAT = [45, None, 45, 45, None, 45, 48, None, 45, None, 45, 43, None, 45, 52, None]   # A-Moll, rollend
# Hook: trocken, absteigend, endet „unaufgelöst“ (genervt statt fröhlich)
HOOK = [(69, 0), (72, 2), (76, 4), (74, 6), (72, 7), (71, 8), (69, 10),
        (69, 16), (72, 18), (76, 20), (77, 22), (76, 23), (74, 24), (71, 26), (69, 28)]
CHORDS = [[57, 60, 64], [57, 60, 64], [53, 57, 60], [52, 56, 59]]   # Am Am F E

for b in range(bars):
    t0 = b * BAR
    for k in range(4):
        add(KICK, t0 + k * BEAT, 0.9)
        add(HAT, t0 + k * BEAT + BEAT / 2, 0.25, pan=0.3)
        if k in (1, 3):
            add(CLAP, t0 + k * BEAT, 0.35, pan=-0.1)
    for k in range(16):
        if k % 2 == 1 and rng.random() < 0.5:
            add(HAT, t0 + k * S16, 0.1, pan=-0.3)
        m = BASS_PAT[k]
        if m is not None:
            add(bass(m), t0 + k * S16, 0.5)
    add(pad(CHORDS[b % 4], BAR), t0, 0.12)
    if b >= 1:   # Melodie ab Takt 2, 2-taktige Phrase
        phrase_t0 = t0 if b % 2 == 1 else None
        if phrase_t0 is not None:
            for m, step in HOOK:
                add(lead(m, S16 * 3), phrase_t0 + step * S16, 0.22, pan=0.15)
                add(lead(m, S16 * 3), phrase_t0 + step * S16 + 3 * S16, 0.08, pan=-0.35)   # Echo

# Seitenkette: Pumpen im Takt (typisch Techno)
t = np.arange(N) / SR
pump = 0.55 + 0.45 * np.minimum(((t % BEAT) / 0.18), 1)
mixL *= pump; mixR *= pump
# Ein-/Ausblenden
fade = np.minimum(t / 0.05, 1) * np.minimum((LEN - t) / 1.5, 1)
mixL *= fade; mixR *= fade
peak = max(np.abs(mixL).max(), np.abs(mixR).max())
st = np.stack([mixL, mixR], 1) / peak * 0.89
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print(OUT, LEN, "s")
