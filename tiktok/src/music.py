"""Eigene, lizenzfreie Hintergrundmusik: gut gelaunte Marimba-Melodie mit Bass, Shaker und weicher Kick.
112 BPM, F-Dur, 4-taktiges Motiv das sich wiederholt (einpraegsam, dezent). Wird unter der Stimme abgesenkt."""
import numpy as np

SR = 44100
BPM = 112
BEAT = 60 / BPM
rng = np.random.default_rng(3)


def hz(n):  # MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)


def marimba(f, d=0.5):
    t = np.arange(int(d * SR)) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 28)
    return s * np.minimum(1, t / 0.004)


def bass(f, d):
    t = np.arange(int(d * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return s * np.exp(-t * 3.5) * np.minimum(1, t / 0.01)


def kick():
    t = np.arange(int(0.25 * SR)) / SR
    return np.sin(2 * np.pi * (55 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 14)


def shaker():
    n = int(0.06 * SR)
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(8) / 8, 'same')
    return x * np.exp(-np.arange(n) / (0.012 * SR))


# Motiv in Achteln (None = Pause), F-Dur: F4=65
F, G, A, Bb, C, D, E = 65, 67, 69, 70, 72, 74, 76
MOTIF = [C, A, C, D, C, A, F, None,   G, A, Bb, A, G, None, None, None,
         A, F, A, C, D, C, A, None,   G, E - 12 + 12, G, A, F, None, None, None]
CHORDS = [41, 41, 43, 36, 38, 38, 36, 41]  # Basstoene pro halbem Takt (F, F, G, C, D, D, C, F)


def make_music(total, voice=None):
    N = int(total * SR) + SR
    mel = np.zeros(N); bs = np.zeros(N); dr = np.zeros(N)
    e8 = BEAT / 2
    k = 0
    while k * e8 < total:
        t0 = int(k * e8 * SR)
        note = MOTIF[k % len(MOTIF)]
        bar_section = (k // 32) % 2  # jede 2. Runde eine Oktave hoeher fuer Abwechslung
        if note is not None:
            s = marimba(hz(note + 12 * bar_section), 0.6)
            n = min(len(s), N - t0); mel[t0:t0 + n] += s[:n] * (1.0 if k % 2 == 0 else 0.75)
        if k % 4 == 0:
            f = hz(CHORDS[(k // 4) % len(CHORDS)])
            s = bass(f, 2 * BEAT); n = min(len(s), N - t0); bs[t0:t0 + n] += s[:n]
        if k % 4 == 0:
            s = kick(); n = min(len(s), N - t0); dr[t0:t0 + n] += s[:n] * 0.6
        s = shaker(); n = min(len(s), N - t0); dr[t0:t0 + n] += s[:n] * (0.10 if k % 2 else 0.05)
        k += 1
    mus = mel * 0.05 + bs * 0.045 + dr * 0.05
    # sanft ein- und ausblenden
    fade = int(1.0 * SR)
    mus[:fade] *= np.linspace(0, 1, fade)
    end = int(total * SR)
    mus[end - fade:end] *= np.linspace(1, 0, fade)
    mus[end:] = 0
    if voice is not None:  # Ducking: Musik leiser, waehrend gesprochen wird
        env = np.convolve(np.abs(voice[:N]), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
        g = 1 - 0.45 * np.clip(env / 0.03, 0, 1)
        mus[:len(g)] *= g
    return mus.astype(np.float32)
