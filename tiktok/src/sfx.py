"""Synthetische Soundeffekte, zeitlich passend zu den Animationen in main.js."""
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _lp(x, n):
    return np.convolve(x, np.ones(n) / n, 'same')


def splat():
    t = _t(0.28)
    n = _lp(rng.standard_normal(len(t)), 40)
    tone = np.sin(2 * np.pi * (260 - 600 * t) * t)
    return (n * 3 + 0.5 * tone) * np.exp(-t * 14) * 0.22


def pop():
    t = _t(0.07)
    return np.sin(2 * np.pi * (500 + 9000 * t) * t) * np.exp(-t * 50) * 0.16


def whoosh():
    t = _t(0.32)
    n = rng.standard_normal(len(t))
    b = _lp(n, 6) - _lp(n, 40)
    return b * np.sin(np.pi * t / t[-1]) ** 2 * 0.35


def click():
    t = _t(0.012)
    return rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.35


def thud():
    t = _t(0.18)
    return np.sin(2 * np.pi * (110 - 200 * t) * t) * np.exp(-t * 22) * 0.35


def squelch():
    t = _t(0.22)
    n = _lp(rng.standard_normal(len(t)), 25)
    return n * 4 * np.sin(2 * np.pi * 9 * t) ** 2 * np.exp(-t * 9) * 0.18


def ding():
    t = _t(0.6)
    return (np.sin(2 * np.pi * 1318 * t) + 0.7 * np.sin(2 * np.pi * 1760 * t) * (t > 0.09)) * np.exp(-t * 6) * 0.13


def kaching():
    t = _t(0.9)
    bell = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(2093, 1), (2637, .7), (3136, .5), (4186, .3)])
    mech = np.zeros(len(t)); k = int(0.04 * SR)
    mech[:k] = rng.standard_normal(k) * np.exp(-np.arange(k) / 300)
    return (bell * np.exp(-t * 4) * (t > 0.06) * 0.09 + mech * 0.25)


def coin(two=False):
    f = 2050 if two else 2600
    t = _t(0.35)
    s = sum(np.sin(2 * np.pi * f * r * t) * a for r, a in [(1, 1), (2.76, .5), (5.4, .25)]) * np.exp(-t * 14)
    out = s * 0.12
    if two:  # zweiter Aufpraller
        d = int(0.07 * SR); out[d:] += s[:-d] * 0.06
    return out


def clack():
    t = _t(0.15)
    return (rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.25 + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30) * 0.2)


def capclink():
    t = _t(0.3)
    return sum(np.sin(2 * np.pi * f * t) for f in (3400, 5100)) * np.exp(-t * 20) * 0.08


def _brass(f, d, vib=0.0):
    t = _t(d)
    ph = 2 * np.pi * f * t + vib * np.sin(2 * np.pi * 5.5 * t)
    x = sum(np.sin(k * ph) / k for k in range(1, 8))
    env = np.minimum(1, t / 0.03) * np.minimum(1, (t[-1] - t) / 0.05 + 0.001)
    return _lp(x, 3) * env


def sad_trombone(total=1.86):
    k = total / 1.86
    notes = [(233, .32 * k), (220, .32 * k), (207.6, .32 * k), (196, .9 * k)]
    out = []
    for i, (f, d) in enumerate(notes):
        out.append(_brass(f, d, vib=1.5 if i == 3 else 0.3))
    return np.concatenate(out) * 0.09


def fanfare():
    notes = [(523, .12), (659, .12), (784, .12), (1047, .45)]
    return np.concatenate([_brass(f, d) for f, d in notes]) * 0.06


def whistle():
    t = _t(0.65)
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * 32 * t)
    s = np.sin(2 * np.pi * 2950 * t + 3 * np.sin(2 * np.pi * 32 * t)) * trem
    return (s + rng.standard_normal(len(t)) * 0.08) * np.minimum(1, t / 0.02) * np.minimum(1, (t[-1] - t) / 0.05) * 0.1


def bus_horn():
    t = _t(0.45)
    s = sum(_brass(f, 0.45) for f in (277, 349))
    return s * np.minimum(1, (t[-1] - t) / 0.06 + 0.0) * 0.05


def flicker_buzz(dur, on_fn):
    t = _t(dur)
    on = np.array([1.0 if on_fn(x) else 0.0 for x in t[::441]]).repeat(441)[:len(t)]
    on = np.pad(on, (0, len(t) - len(on)))
    hum = (2 * ((t * 100) % 1) - 1) * 0.5 + np.sin(2 * np.pi * 50 * t)
    out = _lp(hum, 4) * on * 0.035
    edges = np.where(np.abs(np.diff(on)) > 0)[0]
    for e in edges:
        c = click(); out[e:e + len(c)] += c[:len(out) - e] * 0.6
    return out


def cheer(d=2.8):
    """Stadionjubel: viele gefilterte Rausch-Stimmen, Klatschen und ein paar Pfiffe."""
    t = _t(d); n = len(t)
    crowd = np.zeros(n)
    for i in range(36):
        x = rng.standard_normal(n)
        lo, hi = int(SR / (500 + 900 * rng.random())), int(SR / (2500 + 1500 * rng.random()))
        b = _lp(x, max(hi, 2)) - _lp(x, lo)
        k = np.repeat(rng.random(int(d * 8) + 2), SR // 8)[:n]
        am = _lp(np.pad(k, (0, n - len(k))), 2000)
        crowd += b * (0.4 + am)
    crowd /= np.max(np.abs(crowd)) + 1e-9
    claps = np.zeros(n)
    for p in rng.integers(0, n - 2000, int(d * 70)):
        m = 600; claps[p:p + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / 90) * (0.3 + 0.7 * rng.random())
    claps = claps - _lp(claps, 6)
    wh = np.zeros(n)
    for _ in range(3):
        st = int(rng.random() * (d - 0.8) * SR); tt = _t(0.45 + 0.3 * rng.random())
        f = 2400 + 900 * rng.random()
        w = np.sin(2 * np.pi * f * tt + 8 * np.sin(2 * np.pi * 6 * tt)) * np.sin(np.pi * tt / tt[-1])
        wh[st:st + len(w)] += w[:n - st]
    env = np.minimum(1, t / 0.35) * np.clip((d - t) / 1.4, 0, 1)
    return (crowd * 0.55 + claps * 0.25 + wh * 0.05) * env * 1.1


def croak():
    """Kurzes Frosch-Quaken: zwei schnelle Pulsfolgen mit Formant."""
    out = []
    for f0, d in ((190, 0.16), (230, 0.2)):
        t = _t(d)
        puls = (np.sin(2 * np.pi * f0 * t) > 0.6).astype(float)
        x = _lp(puls - puls.mean(), 6) * np.sin(2 * np.pi * 38 * t) ** 2
        out.append(x * np.minimum(1, t / 0.01) * np.minimum(1, (t[-1] - t) / 0.03))
        out.append(np.zeros(int(0.06 * SR)))
    return np.concatenate(out) * 0.5


def _fft_shape(x, gain_fn):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * gain_fn(f), len(x))


def stadium(d, swell_at, swell_len=0.7, fade_out=0.9):
    """Grossstadion von weitem (TV-Stadionton): Grundteppich + anschwellender Jubel aus vielen
    gefilterten Stimmen, lange Hallfahne, Tiefen abgesenkt, Fokus 1,5-5 kHz, vereinzelte ferne Pfiffe."""
    t = _t(d); n = len(t)
    # Lautstaerkekurve: Grundteppich -> Anschwellen -> Plateau -> Ausblenden
    bed = 0.35
    curve = bed + (1 - bed) * np.clip((t - swell_at) / swell_len, 0, 1) ** 1.5
    curve *= np.clip((d - t) / fade_out, 0, 1) ** 0.8
    curve *= np.minimum(1, t / 0.15)
    # 1) Rauschteppich (Menge als Masse)
    rumble = _fft_shape(rng.standard_normal(n), lambda f: np.exp(-((np.log(f + 1) - np.log(1400)) ** 2) / 1.1) * (f > 220))
    rumble /= np.max(np.abs(rumble)) + 1e-9
    # 2) Viele Stimmen: Rauschen mit Vokal-Formanten, stimmhaft moduliert, eigene Ein-/Ausschwingkurve
    voices = np.zeros(n)
    for i in range(70):
        st = rng.random() * d * 0.9
        ln = 0.5 + rng.random() * 1.8
        a0, a1 = int(st * SR), min(n, int((st + ln) * SR))
        if a1 - a0 < 2000: continue
        tt = np.arange(a1 - a0) / SR
        F1 = 450 + 500 * rng.random(); F2 = 1100 + 1600 * rng.random(); F3 = 2600 + 1200 * rng.random()
        v = _fft_shape(rng.standard_normal(a1 - a0), lambda f: np.exp(-((f - F1) / 160) ** 2) + 0.8 * np.exp(-((f - F2) / 260) ** 2) + 0.5 * np.exp(-((f - F3) / 400) ** 2))
        f0 = 170 + 260 * rng.random()
        v *= 0.55 + 0.45 * np.sin(2 * np.pi * f0 * tt + 2 * np.sin(2 * np.pi * 5 * tt))
        env = np.clip(np.sin(np.pi * tt / tt[-1]), 0, 1) ** 0.7 * (0.7 + 0.3 * np.sin(2 * np.pi * (3 + 4 * rng.random()) * tt))
        voices[a0:a1] += v / (np.max(np.abs(v)) + 1e-9) * env * (0.4 + 0.6 * rng.random())
    voices /= np.max(np.abs(voices)) + 1e-9
    # 3) vereinzelte ferne Pfiffe
    wh = np.zeros(n)
    for _ in range(3):
        st = int((swell_at + rng.random() * (d - swell_at - 0.6)) * SR); tt = _t(0.35 + 0.25 * rng.random())
        f = 2300 + 900 * rng.random()
        w = np.sin(2 * np.pi * f * tt + 6 * np.sin(2 * np.pi * 5 * tt)) * np.sin(np.pi * tt / tt[-1])
        wh[st:st + len(w)] += w[:max(0, n - st)]
    dry = (rumble * 0.45 + voices * 0.75 + wh * 0.06) * curve
    # 4) Stadion-Hall: lange, dichte Hallfahne
    irl = int(2.2 * SR); ir = rng.standard_normal(irl) * np.exp(-np.arange(irl) / (0.55 * SR))
    ir = _fft_shape(ir, lambda f: 1 / (1 + (f / 3500) ** 2)); ir /= np.sqrt(np.sum(ir ** 2))
    L = n + irl; wet = np.fft.irfft(np.fft.rfft(dry, L) * np.fft.rfft(ir, L), L)[:n]
    wet /= np.max(np.abs(wet)) + 1e-9
    out = dry / (np.max(np.abs(dry)) + 1e-9) * 0.45 + wet * 0.7
    # 5) Broadcast-EQ: Tiefen weg, Fokus 1,5-5 kHz
    out = _fft_shape(out, lambda f: (1 / (1 + (250 / (f + 1)) ** 4)) * (0.6 + 0.6 * np.exp(-((f - 3000) / 1800) ** 2)) / (1 + (f / 9000) ** 4))
    out *= np.clip((d - t) / fade_out, 0, 1) ** 0.5
    return out / (np.max(np.abs(out)) + 1e-9) * 0.3


def build_sfx(segs, N):
    # Stadionjubel (cheer) ist vorhanden, wird in Folge 1 aber bewusst NICHT genutzt (veroeffentlichte Fassung = gemini_v3)
    fx = np.zeros(N, np.float32)

    def put(at, snd):
        i = int(at * SR)
        if i < 0 or i >= N: return
        n = min(len(snd), N - i); fx[i:i + n] += snd[:n]

    for k, s in enumerate(segs):
        st, en = s['start'], s['end']
        c = [x['t0'] - st for x in s['caps']]
        L = lambda lt, snd: put(st + lt, snd)
        if k > 0: L(0, splat())
        sid = s['id']
        if sid == 'intro': L(0.0, whoosh()); L(0.3, thud()); L(0.3, pop()); L(0.6, pop()); L(0.0, stadium((en - st) + 0.9, swell_at=0.8, swell_len=0.8, fade_out=1.1) / 0.6)
        elif sid == 'follow': L(0.6, pop())
        elif sid == 'chairs':
            L(0.0, pop()); L(0.9, pop())
            for x in (0.15, 0.45, 0.75): L(x + 0.1, clack())
        elif sid == 'welcome': L(0.0, whoosh()); L(0.05, pop())
        elif sid == 'field': L(0.1, pop())
        elif sid == 'light':
            L(0, flicker_buzz(en - st, lambda x: np.sin(x * 37) + np.sin(x * 13.3) > -0.6))
            L(0.5, pop()); L(1.4, pop())
        elif sid == 'league': L(0.1, pop()); L(0.8, pop())
        elif sid in ('vlad', 'opa'): L(0.1, pop())
        elif sid == 'pichu': L(0.1, pop())
        elif sid == 'bus': L(0.1, pop()); L(c[-1], pop())
        elif sid == 'goal': L(0.0, pop()); L(0.6, fanfare()); L(1.0, pop())
        elif sid == 'sunday': L(0.0, pop()); L(0.6, whistle())
        elif sid == 'fans': L(0.1, pop()); L(0.8, sad_trombone(max(0.5, (en - st) - 0.8 - 0.12)))
        elif sid == 'seat':
            L(0.0, pop()); L(0.6, click()); L(1.0, ding())
            for x in (1.3, 1.55, 1.8): L(x, pop())
            L(2.1, pop())
        elif sid == 'money': L(0.0, pop()); L(0.4, clack()); L(0.9, kaching())
        elif sid == 'rule':
            L(c[0], pop()); L(c[3], pop())
            for i in range(14):
                t0 = c[0] + 0.15 + i * 0.36
                if t0 + 0.6 < en - st: L(t0 + 0.6, coin(t0 >= c[3]))
        elif sid == 'options':
            L(0.0, pop())
            for x in c[2:5]: L(x, whoosh())
        elif sid == 'comment': L(0.0, ding()); L(0.6, pop())
    return fx * 0.6
