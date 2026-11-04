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


def clink():
    """glass/plastic bucket set down"""
    out = sum(tone(f, 0.35, (1,), d=0.09) * g for f, g in ((2150, 0.5), (3310, 0.35), (5230, 0.2)))
    n = int(0.02 * SR)
    out[:n] += np.random.default_rng(5).standard_normal(n) * _env(n, 0.0005, 0.004) * 0.4
    return out * 0.6


def whoosh(dur=0.45):
    n = int(dur * SR)
    x = np.random.default_rng(9).standard_normal(n)
    k = 14
    x = np.convolve(x, np.ones(k) / k, mode="same")
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return x * env * 0.9


def tada():
    out = np.zeros(int(1.6 * SR))
    for i, m in enumerate((72, 76, 79, 84)):
        place(out, tone(note(m), 0.9, (1, .4, .15), d=0.35) * 0.45, i * 0.09)
    for m in (72, 76, 79, 84):
        place(out, tone(note(m), 1.2, (1, .3, .1), d=0.6) * 0.3, 0.42)
    return out


def glug():
    out = np.zeros(int(0.6 * SR))
    rng = np.random.default_rng(4)
    for i in range(5):
        f = rng.uniform(170, 280)
        n = int(0.07 * SR)
        tt = np.arange(n) / SR
        b = np.sin(2 * np.pi * (f + 900 * tt) * tt) * _env(n, 0.003, 0.025)
        place(out, b * 0.7, i * 0.11 + rng.uniform(0, 0.03))
    return out


def fw_launch():
    """rising whistle of a firework rocket"""
    n = int(0.38 * SR)
    tt = np.arange(n) / SR
    f = 900 + 1700 * (tt / tt[-1]) ** 1.5
    tone_ = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    hiss = np.random.default_rng(31).standard_normal(n) * 0.18
    env = np.minimum(1, tt / 0.05) * (0.6 + 0.4 * tt / tt[-1])
    return (tone_ + hiss) * env


def fw_boom():
    """low thump + noise burst"""
    n = int(1.1 * SR)
    tt = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt / 0.18)
    x = np.random.default_rng(32).standard_normal(n)
    x = np.convolve(x, np.ones(10) / 10, mode="same") * np.exp(-tt / 0.25) * 1.2
    return (thump * 0.9 + x) * np.minimum(1, tt / 0.004)


def fw_crackle():
    """sparkling crackle after the burst"""
    n = int(0.9 * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(33)
    for _ in range(45):
        k = int(rng.uniform(0, n - 600))
        m = int(rng.uniform(120, 400))
        out[k:k + m] += rng.standard_normal(m) * _env(m, 0.0003, 0.002) * rng.uniform(0.3, 1.0)
    return out * np.linspace(1, 0.2, n)


def creak(dur=0.9):
    """old wooden door creak: wobbling, rough mid-frequency tone"""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 420 + 160 * np.sin(2 * np.pi * 1.7 * tt) + 90 * tt / dur
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.35 + np.sin(ph * 2.01) * 0.25
    am = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 23 * tt))
    env = np.minimum(1, tt / 0.08) * np.minimum(1, (dur - tt) / 0.15)
    x = np.convolve(x * am * env, np.ones(6) / 6, mode="same")
    return x * 0.5


def growl(dur=1.1):
    """big cat growl / roar: low rough noise with pitch contour"""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 95 + 60 * np.sin(np.pi * tt / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = (ph / np.pi) % 2 - 1
    noise = np.random.default_rng(41).standard_normal(n)
    noise = np.convolve(noise, np.ones(30) / 30, mode="same") * 4
    am = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 31 * tt))
    env = np.minimum(1, tt / 0.12) * np.minimum(1, (dur - tt) / 0.3)
    x = (saw * 0.5 + noise * 0.6) * am * env
    return np.convolve(x, np.ones(8) / 8, mode="same") * 0.8


def buzzer():
    n = int(0.45 * SR)
    tt = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * 140 * tt)) * 0.25 + np.sign(np.sin(2 * np.pi * 147 * tt)) * 0.25
    return x * np.minimum(1, tt / 0.01) * np.minimum(1, (0.45 - tt) / 0.05)


def step():
    n = int(0.12 * SR)
    tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * (110 - 300 * tt) * tt) * np.exp(-tt / 0.03)
    x += np.random.default_rng(42).standard_normal(n) * np.exp(-tt / 0.01) * 0.3
    return x * 0.7


def drip():
    n = int(0.25 * SR)
    tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (1300 + 900 * tt) * tt) * np.exp(-tt / 0.035) * 0.5


def swish():
    return whoosh(0.28) * 1.1


def crackle_bed(dur):
    """quiet torch crackle for the whole cellar scene"""
    n = int(dur * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(43)
    for _ in range(int(dur * 14)):
        k = int(rng.uniform(0, n - 400))
        m = int(rng.uniform(60, 300))
        out[k:k + m] += rng.standard_normal(m) * _env(m, 0.0003, 0.002) * rng.uniform(0.2, 1.0)
    return out


def chainsaw(dur=2.0):
    """two-stroke engine: buzzy saw tone with revving"""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    rev = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 0.75 * tt))
    f = 85 + 75 * rev
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = ((ph / np.pi) % 2 - 1)
    buzz = saw * (0.6 + 0.4 * np.sign(np.sin(ph * 0.5)))
    noise = np.random.default_rng(51).standard_normal(n)
    noise = np.convolve(noise, np.ones(4) / 4, mode="same") * 0.35 * rev
    env = np.minimum(1, tt / 0.15) * np.minimum(1, (dur - tt) / 0.25)
    x = (buzz * 0.45 + noise) * env
    return np.convolve(x, np.ones(5) / 5, mode="same") * 0.7


def shing():
    """metallic blade ring"""
    out = sum(tone(f, 0.8, (1,), d=d) * g for f, d, g in ((2630, 0.35, 0.4), (3950, 0.25, 0.3), (5480, 0.18, 0.2)))
    n = int(0.03 * SR)
    out[:n] += np.random.default_rng(52).standard_normal(n) * _env(n, 0.0005, 0.006) * 0.5
    return out * 0.7


def squawk():
    """short parrot squawk"""
    n = int(0.22 * SR)
    tt = np.arange(n) / SR
    f = 1500 + 700 * np.sin(2 * np.pi * 9 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.3 + np.random.default_rng(53).standard_normal(n) * 0.15
    return x * np.minimum(1, tt / 0.01) * np.minimum(1, (0.22 - tt) / 0.06)


def wrong():
    """soft two-tone 'nope' (replaces the harsh buzzer)"""
    out = np.zeros(int(0.6 * SR))
    place(out, tone(note(64), 0.35, (1, .3), d=0.2) * 0.5, 0.0)
    place(out, tone(note(59), 0.45, (1, .3), d=0.25) * 0.5, 0.16)
    return out


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
        s = {"ding": ding, "pop": pop, "tick": tick, "click": click, "clink": clink, "whoosh": whoosh,
             "tada": tada, "glug": glug, "fw_launch": fw_launch, "fw_boom": fw_boom,
             "fw_crackle": fw_crackle, "creak": creak, "growl": growl, "buzzer": buzzer, "step": step,
             "drip": drip, "swish": swish, "shing": shing, "squawk": squawk, "wrong": wrong}.get(kind)
        if kind == "bed":
            s = crackle_bed(extra[0])
        elif kind == "chainsaw":
            s = chainsaw(extra[0])
        elif kind == "rain":
            s = rain_noise(extra[0]); r = int(0.4 * SR)
            s[:r] *= np.linspace(0, 1, r); s[-r:] *= np.linspace(1, 0, r)
        else:
            s = s()
        place(sfx, s, t, gain)
    out = voice * 1.0 + mus * fade + sfx * 0.6
    out = out / max(1.0, np.abs(out).max() / 0.95)
    sf.write(out_path, np.stack([out, out], 1).astype(np.float32), SR)
