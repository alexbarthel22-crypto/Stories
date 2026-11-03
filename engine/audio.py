"""Procedural background music + sound effects, and the final mix."""
import numpy as np, soundfile as sf

SR = 44100


def _env(n, a=0.005, d=0.6):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def tone(f, dur, harm=(1, .5, .25, .12), d=0.5, a=0.005):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm))
    return s * _env(n, a, d)


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def music(length, bpm=104, seed=1):
    """Light, playful pluck/marimba loop (I–vi–IV–V in C)."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int(length * SR) + SR)
    beat = 60 / bpm
    prog = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    bar = 4 * beat
    t, i = 0.0, 0
    while t < length:
        ch = prog[i % 4]
        # bass
        for b in (0, 2):
            s = tone(note(ch[0] - 24), beat * 1.8, (1, .3, .1), d=0.35) * 0.55
            place(out, s, t + b * beat)
        # marimba arpeggio in 8ths
        pat = [0, 1, 2, 1, 2, 0, 1, 2]
        for j, p in enumerate(pat):
            m = ch[p] + 12 + (12 if (j == 7 and i % 2) else 0)
            s = tone(note(m), 0.6, (1, 0, .18, 0, .05), d=0.16) * (0.32 if j % 2 == 0 else 0.22)
            place(out, s, t + j * beat / 2)
        # shaker
        for j in range(8):
            n = int(0.05 * SR)
            s = rng.standard_normal(n) * _env(n, 0.002, 0.012) * (0.05 if j % 2 else 0.03)
            place(out, s, t + j * beat / 2)
        t += bar; i += 1
    return out[:int(length * SR)]


def ding(two=True):
    s = tone(note(88), 1.2, (1, .3, .1), d=0.5) * 0.5
    if two:
        s2 = tone(note(84), 1.2, (1, .3, .1), d=0.6) * 0.5
        out = np.zeros(len(s) + int(0.22 * SR)); out[:len(s)] += s; out[int(0.22 * SR):] += s2
        return out
    return s


def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 500 + 900 * t / t[-1]
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.04) * 0.35


def click():
    """light switch click"""
    n = int(0.03 * SR)
    x = np.random.default_rng(3).standard_normal(n) * _env(n, 0.0005, 0.004)
    return (x * 0.6 + tone(3200, 0.03, (1,), d=0.006) * 0.4) * 0.8


def tick():
    n = int(0.04 * SR)
    return np.random.default_rng(0).standard_normal(n) * _env(n, 0.001, 0.006) * 0.5 + \
        tone(2200, 0.04, (1,), d=0.01) * 0.3


def rain_noise(dur, seed=2):
    n = int(dur * SR)
    x = np.random.default_rng(seed).standard_normal(n)
    # crude low-pass via moving average + some high crackle
    k = 6
    lp = np.convolve(x, np.ones(k) / k, mode="same")
    return lp * 0.25


def place(buf, s, t, gain=1.0):
    k = int(t * SR)
    if k >= len(buf):
        return
    e = min(len(buf), k + len(s))
    buf[k:e] += s[:e - k] * gain


def load_music(path, n):
    """Decode any audio file to mono float at SR, trimmed/padded to n samples."""
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).astype(np.float64)
    out = np.zeros(n)
    out[:min(n, len(m))] = m[:n]
    return out


def mix(voice_path, length, events, out_path, music_gain=0.16, duck=0.45, music_path=None, music_db=-15.0):
    """music_path: use this track (e.g. Lyria) instead of the procedural loop, placed music_db below the voice."""
    v, sr = sf.read(voice_path, dtype="float32")
    if v.ndim > 1:
        v = v.mean(1)
    if sr != SR:  # resample (linear)
        x = np.arange(int(len(v) * SR / sr)) / SR
        v = np.interp(x, np.arange(len(v)) / sr, v)
    n = int(length * SR)
    voice = np.zeros(n); voice[:min(n, len(v))] = v[:n]
    if music_path:
        mus = load_music(music_path, n)
        speech = np.abs(voice) > 0.02
        v_rms = np.sqrt((voice[speech] ** 2).mean()) if speech.any() else 0.1
        m_rms = np.sqrt((mus ** 2).mean()) + 1e-9
        mus *= v_rms * 10 ** (music_db / 20) / m_rms
    else:
        mus = music(length) * music_gain
    # duck music under voice (smoothed envelope)
    env = np.abs(voice)
    win = int(0.25 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    g = 1 - duck * np.clip(env / 0.05, 0, 1)
    mus *= g
    fade = np.ones(n); fl = int(1.5 * SR); fade[-fl:] = np.linspace(1, 0, fl); fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
    sfx = np.zeros(n)
    for kind, t, gain, *extra in events:
        s = {"ding": ding, "pop": pop, "tick": tick, "click": click}.get(kind)
        if kind == "rain":
            s = rain_noise(extra[0]); r = int(0.4 * SR)
            s[:r] *= np.linspace(0, 1, r); s[-r:] *= np.linspace(1, 0, r)
        else:
            s = s()
        place(sfx, s, t, gain)
    out = voice * 1.0 + mus * fade + sfx * 0.6
    out = out / max(1.0, np.abs(out).max() / 0.95)
    sf.write(out_path, np.stack([out, out], 1).astype(np.float32), SR)
