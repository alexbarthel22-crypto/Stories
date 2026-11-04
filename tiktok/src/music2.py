"""Eigene, lizenzfreie Hintergrundmusik Nr. 2: Lo-Fi-Hip-Hop, 92 BPM, a-Moll.
E-Piano-Akkorde (Am7 - Fmaj7 - C - G), Boom-Bap-Drums, Bass und eine Pfeif-Melodie als Hook.
Unter der Stimme wird die Musik automatisch abgesenkt (Ducking)."""
import numpy as np

SR = 44100
BPM = 92
BEAT = 60 / BPM
rng = np.random.default_rng(11)


def hz(n):
    return 440 * 2 ** ((n - 69) / 12)


def _t(d):
    return np.arange(int(d * SR)) / SR


def epiano(notes, d):
    t = _t(d)
    s = np.zeros(len(t))
    for n in notes:
        f = hz(n)
        s += (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
              + 0.12 * np.sin(2 * np.pi * 7 * f * t) * np.exp(-t * 18))
    trem = 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    return s * trem * np.exp(-t * 0.9) * np.minimum(1, t / 0.01) / len(notes)


def bass(n, d):
    t = _t(d)
    f = hz(n)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 2.2) * np.minimum(1, t / 0.01)


def kick():
    t = _t(0.3)
    return np.sin(2 * np.pi * (48 + 110 * np.exp(-t * 28)) * t) * np.exp(-t * 9)


def snare():
    t = _t(0.25)
    n = rng.standard_normal(len(t))
    n = n - np.convolve(n, np.ones(6) / 6, 'same')
    return (n * 0.6 * np.exp(-t * 18) + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.5)


def hat(open_=False):
    t = _t(0.12 if open_ else 0.05)
    n = rng.standard_normal(len(t))
    n = n - np.convolve(n, np.ones(3) / 3, 'same')
    return n * np.exp(-t * (25 if open_ else 70))


def whistle(n, d):
    t = _t(d)
    f = hz(n)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.15)
    s = np.sin(2 * np.pi * f * np.cumsum(vib) / SR) + 0.08 * rng.standard_normal(len(t)) * 0.3
    env = np.minimum(1, t / 0.04) * np.minimum(1, (t[-1] - t) / 0.06 + 0.001)
    return s * env


CHORDS = [([57, 60, 64, 67], 45), ([53, 57, 60, 64], 41), ([52, 55, 60, 64], 48), ([50, 55, 59, 62], 43)]
# Hook (Achtel, None = Pause), 2 Takte, danach 2 Takte Pause -> nicht aufdringlich
HOOK = [76, None, 74, 72, None, 69, 72, None,   74, None, 72, 69, 67, None, None, None]


def put(buf, at, snd, g=1.0):
    i = int(at * SR)
    if i >= len(buf): return
    n = min(len(snd), len(buf) - i)
    buf[i:i + n] += snd[:n] * g


def make_music(total, voice=None):
    N = int(total * SR) + SR
    keys = np.zeros(N); bs = np.zeros(N); dr = np.zeros(N); mel = np.zeros(N)
    bar = 4 * BEAT
    b = 0
    while b * bar < total:
        t0 = b * bar
        notes, root = CHORDS[b % 4]
        put(keys, t0, epiano(notes, bar * 1.05))
        put(bs, t0, bass(root, BEAT * 1.5)); put(bs, t0 + 2.5 * BEAT, bass(root, BEAT * 1.2), 0.8)
        # Boom-Bap mit leichtem Swing
        sw = BEAT * 0.08
        put(dr, t0, kick()); put(dr, t0 + 1.5 * BEAT + sw, kick(), 0.6); put(dr, t0 + 2.5 * BEAT, kick(), 0.8)
        put(dr, t0 + BEAT, snare(), 0.7); put(dr, t0 + 3 * BEAT, snare(), 0.7)
        for k in range(8):
            put(dr, t0 + k * BEAT / 2 + (sw if k % 2 else 0), hat(k == 7), 0.18 if k % 2 else 0.28)
        if b % 4 in (0, 1):  # Hook in den ersten beiden Takten jedes 4-Takt-Blocks
            for k, n in enumerate(HOOK[(b % 2) * 8:(b % 2) * 8 + 8]):
                if n is not None: put(mel, t0 + k * BEAT / 2, whistle(n, BEAT / 2 * 0.9))
        b += 1
    mus = (keys * 0.10 + bs * 0.05 + dr * 0.06 + mel * 0.03) * 0.71
    # leichtes Vinyl-Knistern fuer den Lo-Fi-Charakter
    crackle = np.zeros(N)
    for p in rng.integers(0, N - 50, int(total * 30)): crackle[p] += rng.standard_normal() * 0.5
    mus += np.convolve(crackle, np.ones(3) / 3, 'same') * 0.01
    fade = int(1.0 * SR); end = int(total * SR)
    mus[:fade] *= np.linspace(0, 1, fade)
    mus[end - fade:end] *= np.linspace(1, 0, fade); mus[end:] = 0
    if voice is not None:
        env = np.convolve(np.abs(voice[:N]), np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
        g = 1 - 0.45 * np.clip(env / 0.03, 0, 1)
        mus[:len(g)] *= g
    return mus.astype(np.float32)
