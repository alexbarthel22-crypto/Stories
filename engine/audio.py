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


def wind(dur, seed=5):
    """soft desert wind: low-passed noise with slow gusts"""
    n = int(dur * SR)
    x = np.random.default_rng(seed).standard_normal(n)
    for k in (40, 25):
        x = np.convolve(x, np.ones(k) / k, mode="same")
    tt = np.arange(n) / SR
    gust = 0.55 + 0.45 * np.sin(tt * 0.9) * np.sin(tt * 0.37 + 1)
    s = x * gust * 2.2
    r = int(min(1.0, dur / 3) * SR)
    s[:r] *= np.linspace(0, 1, r); s[-r:] *= np.linspace(1, 0, r)
    return s


def impact():
    """deep cinematic hit for a shouted opener"""
    d = 1.4
    tt = np.arange(int(d * SR)) / SR
    f = 55 * np.exp(-tt * 1.5) + 30
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.0)
    noise = np.random.default_rng(9).standard_normal(len(tt)) * np.exp(-tt * 18) * 0.5
    return (body + noise) * 0.9


def _t(d):
    return np.arange(int(d * SR)) / SR


def drum():
    """deep frame drum / taiko hit"""
    tt = _t(0.9)
    f = 48 + 70 * np.exp(-tt * 28)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6)
    slap = np.random.default_rng(3).standard_normal(len(tt)) * np.exp(-tt * 60) * 0.35
    return (body + slap) * 0.55


def gong(dur=3.0):
    tt = _t(dur)
    s = sum(a * np.sin(2 * np.pi * f * tt + p) * np.exp(-tt * d)
            for f, a, d, p in ((110, 1, 0.9, 0), (174, .6, 1.3, 1), (232, .45, 1.6, 2), (297, .3, 2.2, .5), (411, .2, 3, 1.5)))
    wob = 1 + 0.25 * np.sin(2 * np.pi * 4.5 * tt) * np.exp(-tt * 1.2)
    att = np.clip(tt / 0.01, 0, 1)
    return s * wob * att * 0.45


def chirp():
    """two little bird tweets"""
    out = np.zeros(int(0.55 * SR))
    for k, t0 in enumerate((0.0, 0.22)):
        tt = _t(0.12)
        f = 3200 + 1800 * np.sin(np.pi * tt / 0.12) + 400 * k
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.12) ** 2
        i = int(t0 * SR)
        out[i:i + len(s)] += s * 0.5
    return out


def sparkle():
    """bright magical shimmer (rising arpeggio of bells)"""
    out = np.zeros(int(1.2 * SR))
    for k, m in enumerate((84, 88, 91, 96, 100)):
        tt = _t(0.7)
        f = 440 * 2 ** ((m - 69) / 12)
        s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt * 7)
        i = int(k * 0.055 * SR)
        out[i:i + len(s)] += s * 0.25
    return out


def riser(dur=1.2):
    tt = _t(dur)
    noise = np.random.default_rng(4).standard_normal(len(tt))
    k = np.linspace(30, 2, len(tt)).astype(int)
    lp = np.convolve(noise, np.ones(8) / 8, mode="same")
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (tt / dur) ** 2) / SR) * 0.3
    env = (tt / dur) ** 2
    return (lp * 0.6 + tone) * env * 0.7


def sistrum():
    """egyptian metal rattle"""
    tt = _t(0.6)
    rng = np.random.default_rng(8)
    out = np.zeros(len(tt))
    for k in range(5):
        i = int(k * 0.07 * SR)
        n = int(0.08 * SR)
        x = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 50)
        jing = sum(np.sin(2 * np.pi * f * np.arange(n) / SR) for f in (5200, 6800, 8100)) * np.exp(-np.arange(n) / SR * 40)
        out[i:i + n] += (x * 0.3 + jing * 0.25) * (1 - k * 0.12)
    return out * 0.65


def rumble(dur=2.0):
    tt = _t(dur)
    x = np.random.default_rng(11).standard_normal(len(tt))
    for k in (120, 80):
        x = np.convolve(x, np.ones(k) / k, mode="same")
    env = np.sin(np.pi * tt / dur) ** 0.7
    return (x * 14 + 0.4 * np.sin(2 * np.pi * 38 * tt)) * env * 0.27


def owl():
    out = np.zeros(int(1.0 * SR))
    for t0, d in ((0.0, 0.18), (0.32, 0.45)):
        tt = _t(d)
        f = 420 - 60 * tt / d
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / d) * 0.5
        i = int(t0 * SR)
        out[i:i + len(s)] += s
    return out


def splash():
    tt = _t(0.5)
    x = np.random.default_rng(13).standard_normal(len(tt))
    x = np.convolve(x, np.ones(3) / 3, mode="same")
    return x * np.exp(-tt * 9) * 0.35


def kaching():
    """cash register: bell + coin rattle"""
    out = np.zeros(int(0.9 * SR))
    tt = _t(0.8)
    bell = sum(a * np.sin(2 * np.pi * f * tt) for f, a in ((2093, 1), (2637, .6), (3136, .4))) * np.exp(-tt * 5)
    out[int(0.06 * SR):int(0.06 * SR) + len(bell)] += bell * 0.35
    rng = np.random.default_rng(21)
    for k in range(6):
        n = int(0.05 * SR)
        x = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 70) * 0.25
        i = int(k * 0.03 * SR)
        out[i:i + n] += x
    return out


def engine(dur=1.6):
    """sports car rev: rising sawtooth + rumble"""
    tt = _t(dur)
    f = 55 + 140 * np.clip(tt / (dur * 0.6), 0, 1) ** 1.5 + 8 * np.sin(2 * np.pi * 7 * tt)
    ph = np.cumsum(f) / SR
    saw = 2 * (ph % 1) - 1
    s = saw * 0.5 + 0.3 * np.sin(2 * np.pi * ph * 2)
    s = np.convolve(s, np.ones(6) / 6, mode="same")
    env = np.clip(tt / 0.1, 0, 1) * np.clip((dur - tt) / 0.4, 0, 1)
    return s * env * 0.6


def beep(f=880, d=0.18):
    tt = _t(d)
    return np.sin(2 * np.pi * f * tt) * np.clip((d - tt) / 0.03, 0, 1) * np.clip(tt / 0.005, 0, 1) * 0.4


def cheer(dur=1.8):
    """crowd cheer: band-passed noise swell with whistles"""
    tt = _t(dur)
    x = np.random.default_rng(31).standard_normal(len(tt))
    lp = np.convolve(x, np.ones(4) / 4, mode="same") - np.convolve(x, np.ones(40) / 40, mode="same")
    env = np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 0.6
    wh = np.sin(2 * np.pi * np.cumsum(1800 + 700 * np.sin(tt * 9)) / SR) * 0.06 * (tt > 0.3) * (tt < 1.0)
    return (lp * 0.9 + wh) * env * 0.6


def notify():
    out = np.zeros(int(0.45 * SR))
    for k, f in enumerate((1318, 1760)):
        b = beep(f, 0.14) * np.exp(-_t(0.14) * 8)
        i = int(k * 0.12 * SR)
        out[i:i + len(b)] += b
    return out


def heartbeat():
    out = np.zeros(int(0.7 * SR))
    for k, g in ((0, 1.0), (0.18, 0.7)):
        tt = _t(0.25)
        b = np.sin(2 * np.pi * (45 + 30 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) * g
        i = int(k * SR)
        out[i:i + len(b)] += b * 0.8
    return out


def place(buf, s, t, gain=1.0):
    k = int(t * SR)
    if k >= len(buf):
        return
    e = min(len(buf), k + len(s))
    buf[k:e] += s[:e - k] * gain


def load_music(path, n, loop=False):
    """Decode any audio file to mono float at SR, trimmed/padded to n samples."""
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).astype(np.float64)
    if loop and 0 < len(m) < n:            # loop with a 1 s crossfade
        xf = SR
        while len(m) < n:
            seg = np.frombuffer(raw, np.float32).astype(np.float64)
            r = np.linspace(0, 1, xf)
            m = np.concatenate([m[:-xf], m[-xf:] * (1 - r) + seg[:xf] * r, seg[xf:]])
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
        mus = load_music(music_path, n, loop=True)
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
             "drip": drip, "swish": swish, "shing": shing, "squawk": squawk, "wrong": wrong, "impact": impact, "drum": drum,
             "gong": gong, "chirp": chirp, "sparkle": sparkle, "riser": riser, "sistrum": sistrum, "rumble": rumble,
             "owl": owl, "splash": splash, "kaching": kaching,
             "cheer": cheer, "notify": notify, "heartbeat": heartbeat, "beep": beep, "beep_hi": lambda: beep(1760, 0.4)}.get(kind)
        if kind == "file":          # external sound file: ("file", t, gain, path, duration)
            path, dur = extra[0], extra[1]
            s = load_music(path, int(dur * SR))
            fo = int(min(0.5, dur / 3) * SR)
            s[-fo:] *= np.linspace(1, 0, fo)
            s[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
        elif kind == "bed":
            s = crackle_bed(extra[0])
        elif kind == "chainsaw":
            s = chainsaw(extra[0])
        elif kind == "engine":
            s = engine(extra[0])
        elif kind == "wind":
            s = wind(extra[0])
        elif kind == "rain":
            s = rain_noise(extra[0]); r = int(0.4 * SR)
            s[:r] *= np.linspace(0, 1, r); s[-r:] *= np.linspace(1, 0, r)
        else:
            s = s()
        place(sfx, s, t, gain)
    out = voice * 1.0 + mus * fade + sfx * 0.6
    out = out / max(1.0, np.abs(out).max() / 0.95)
    sf.write(out_path, np.stack([out, out], 1).astype(np.float32), SR)
