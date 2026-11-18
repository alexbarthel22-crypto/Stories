#!/usr/bin/env python3
"""Erzeugt die Geräuschbibliothek in sfx/ per Synthese (frei verwendbar, keine Lizenzfragen).

  python3 tools/sfx_synth.py          # alle Geräusche neu erzeugen

Alle Dateien: 44.1 kHz, Stereo-WAV.
"""
import os, wave
import numpy as np
from scipy import signal

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sfx')
R = np.random.default_rng(42)


def t_(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi, o=4): return signal.sosfilt(signal.butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def noise(d): return R.standard_normal(int(d * SR))
def brown(d):
    b = np.cumsum(noise(d)); b = hp(b, 20, 2); return b / (np.abs(b).max() + 1e-9)
def pink(d):
    w = noise(d); f = np.fft.rfft(w); k = np.arange(len(f)); k[0] = 1
    p = np.fft.irfft(f / np.sqrt(k), len(w)); return p / (np.abs(p).max() + 1e-9)
def smooth_rand(d, rate, lo=0.0, hi=1.0):
    """langsam schwankende Zufallskurve (z. B. Windböen)"""
    n = max(4, int(d * rate) + 4); pts = R.random(n)
    x = np.interp(np.linspace(0, n - 3, int(d * SR)), np.arange(n), pts)
    x = lp(x, max(rate, 0.05) * 1.5, 2)
    x = (x - x.min()) / (np.ptp(x) + 1e-9); return lo + (hi - lo) * x
def reverb(x, rt=1.2, wet=0.35, pre=0.02):
    n = int(rt * SR); ir = R.standard_normal(n) * np.exp(-6.9 * np.arange(n) / n)
    ir = lp(ir, 5000, 2); ir[:int(pre * SR)] = 0; ir /= np.sqrt(np.sum(ir ** 2))
    y = signal.fftconvolve(x, ir)[:len(x)]
    return x * (1 - wet) + y * wet
def env_ad(n, a, d):
    e = np.ones(n); ia = max(1, int(a * SR)); e[:ia] = np.linspace(0, 1, ia)
    e[ia:] = np.exp(-np.arange(n - ia) / (d * SR)); return e
def pan(x, p):  # p: -1 links .. 1 rechts (Konstante oder Array)
    p = np.broadcast_to(p, x.shape); a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)
def stereo(l, r): return np.stack([l, r], 1)
def fade(x, fi=0.05, fo=0.2):
    n = len(x); a = np.ones(n); i = int(fi * SR); o = int(fo * SR)
    if i: a[:i] = np.linspace(0, 1, i)
    if o: a[-o:] = np.minimum(a[-o:], np.linspace(1, 0, o))
    return x * (a[:, None] if x.ndim == 2 else a)
def save(name, x, peak=0.9):
    if x.ndim == 1: x = stereo(x, x)
    x = x / (np.abs(x).max() + 1e-9) * peak
    w = wave.open(os.path.join(OUT, name), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype('<i2').tobytes()); w.close(); print('  ', name, f'{len(x) / SR:.1f}s')
def loopable(x, xf=2.0):
    """Ende weich in den Anfang überblenden -> nahtlose Schleife"""
    n = int(xf * SR); a = np.linspace(0, 1, n)[:, None] if x.ndim == 2 else np.linspace(0, 1, n)
    y = x[:-n].copy(); y[:n] = x[:n] * a + x[-n:] * (1 - a); return y


def wind(d=64):
    # Böen: unregelmäßige Anstiege + schnelle Verwirbelungen; Resonanz wandert mit der Windstärke
    g = smooth_rand(d, 0.18, 0.05, 1.0) ** 2.2
    turb = smooth_rand(d, 3.0, 0.6, 1.0)
    ch = []
    for k in range(2):
        b = brown(d)
        body = lp(b, 400, 2) * (0.3 + g)
        # gefilterte Rauschbänder, deren Mittenfrequenz der Böe folgt (das "Heulen")
        howl = np.zeros(int(d * SR)); src = noise(d); seg = SR // 10
        for i in range(0, len(howl) - seg, seg):
            fc = 220 + 650 * g[i]
            howl[i:i + seg] = bp(src[max(0, i - seg):i + seg], fc * 0.85, fc * 1.15, 2)[-seg:] if i >= seg else 0
        howl = lp(howl, 1500) * g * turb * 1.8
        gust_hiss = bp(noise(d), 800, 4000, 2) * g ** 3 * 0.35
        ch.append(body * 0.6 + howl + gust_hiss)
    return loopable(stereo(*ch))

def stadt(d=64):
    rumble = [lp(brown(d), 180, 2) for _ in range(2)]
    traffic = [bp(pink(d), 250, 1800, 2) * smooth_rand(d, 0.15, 0.4, 1.0) * 0.35 for _ in range(2)]
    x = stereo(rumble[0] + traffic[0], rumble[1] + traffic[1])
    # ferne Hupen
    for _ in range(5):
        st = R.uniform(2, d - 3); f = R.choice([360, 410, 470]); dur = R.uniform(0.25, 0.7)
        tt = t_(dur); h = signal.sawtooth(2 * np.pi * f * tt) + 0.6 * signal.sawtooth(2 * np.pi * f * 1.26 * tt)
        h = lp(h, 1400) * env_ad(len(tt), 0.02, dur) * 0.06
        h = reverb(np.concatenate([h, np.zeros(SR * 2)]), 2.0, 0.85)
        i = int(st * SR); seg = pan(h, R.uniform(-0.8, 0.8)); x[i:i + len(seg)] += seg[:len(x) - i]
    return loopable(x)

def voegel(d=64):
    x = np.zeros((int(d * SR), 2))
    s = 0.5
    while s < d - 2:
        p = R.uniform(-0.9, 0.9); base = R.uniform(2800, 5200); kind = R.integers(3)
        for k in range(R.integers(2, 7)):
            dur = R.uniform(0.04, 0.12); tt = t_(dur)
            if kind == 0: f = base * (1 + 0.35 * np.sin(np.pi * tt / dur))
            elif kind == 1: f = np.linspace(base * 1.3, base * 0.8, len(tt))
            else: f = base + 400 * np.sin(2 * np.pi * 40 * tt)
            c = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / dur) ** 2 * R.uniform(0.3, 1)
            i = int((s + k * R.uniform(0.09, 0.2)) * SR); seg = pan(c, p); x[i:i + len(seg)] += seg[:len(x) - i]
        s += R.uniform(0.8, 4.5)
    x[:, 0] = reverb(x[:, 0], 0.9, 0.3); x[:, 1] = reverb(x[:, 1], 0.9, 0.3)
    return loopable(x)

def auto_vorbei(d=7.0):
    tt = t_(d); c = d / 2; prox = 1 / (1 + ((tt - c) / 0.9) ** 2)
    dop = 1 + 0.07 * np.tanh(-(tt - c) / 0.6)
    f0 = 52 * dop; ph = 2 * np.pi * np.cumsum(f0) / SR
    eng = lp(sum(np.sin(ph * k) / k for k in range(1, 9)), 900)
    tire = bp(noise(d), 400, 3500, 2) * 0.6
    x = (eng * 0.6 + tire) * prox
    x = pan(x, np.tanh((tt - c) / 0.8) * 0.9)
    return fade(x, 0.5, 0.8)

def schritte(n=16, iv=0.56):
    # Turnschuhe auf Gehweg: weicher Aufsatz (Ferse), Abrollen, Schleifen auf Sand/Splitt
    d = n * iv + 1; x = np.zeros(int(d * SR))
    for k in range(n):
        i = int((0.2 + k * iv + R.uniform(-0.025, 0.025)) * SR); v = R.uniform(0.7, 1.0)
        L = int(0.25 * SR); e = np.zeros(L)
        heel = env_ad(int(0.12 * SR), 0.008, 0.035); e[:len(heel)] += heel
        j = int(R.uniform(0.07, 0.1) * SR); roll = env_ad(int(0.15 * SR), 0.02, 0.05) * 0.7; e[j:j + len(roll)] += roll[:L - j]
        body = lp(noise(0.25), 900, 2) * e
        scuff = bp(noise(0.25), 1500, 6000, 2) * e * 0.35 * (0.5 + R.random(L) * 0.5)
        x[i:i + L] += (body + scuff) * v
    return reverb(x, 0.45, 0.1)

def vibration():
    x = np.zeros(int(1.6 * SR))
    for st in (0.0, 0.75):
        tt = t_(0.45); b = signal.square(2 * np.pi * 165 * tt) * (0.6 + 0.4 * signal.square(2 * np.pi * 28 * tt))
        b = lp(b, 1200) * env_ad(len(tt), 0.01, 0.6)
        i = int(st * SR); x[i:i + len(b)] += b
    return x

def klingelton(rep=3):
    notes = [76, 79, 83, 79, 81, 84, 81, 79]; x = np.zeros(int((len(notes) * 0.18 * rep + rep * 0.5 + 1) * SR)); s = 0
    for r in range(rep):
        for m in notes:
            f = 440 * 2 ** ((m - 69) / 12); tt = t_(0.5)
            n = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 3 * tt) * np.exp(-tt * 30)) * np.exp(-tt * 8)
            i = int(s * SR); x[i:i + len(n)] += n; s += 0.18
        s += 0.5
    return lp(hp(x, 300), 3400)  # klingt wie aus dem Handylautsprecher

def anruf_ende():
    x = np.zeros(int(1.6 * SR))
    for k in range(3):
        tt = t_(0.22); b = np.sin(2 * np.pi * 425 * tt) * np.minimum(1, np.minimum(tt, 0.22 - tt) * 200)
        i = int(k * 0.45 * SR); x[i:i + len(b)] += b
    return lp(hp(x, 300), 3400)

def sirene_fern(d=16):
    # deutsches Martinshorn ("Tatütata"): Wechsel zwischen ~466 Hz und ~622 Hz, aus der Ferne
    tt = t_(d); per = 1.3
    f = np.where((tt % per) < per / 2, 466.0, 622.0)
    f = lp(f, 25, 1) * (1 + 0.012 * np.sin(2 * np.pi * 0.15 * tt))   # weiche Übergänge + leichter Doppler
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(ph * k) / k ** 1.3 for k in range(1, 7))
    s = lp(s, 1800, 2) * np.minimum(1, tt / 5) * (0.75 + 0.25 * smooth_rand(d, 0.4))
    s = reverb(s, 2.8, 0.7, 0.05)
    return fade(pan(s, -0.35 + 0.25 * np.sin(tt * 0.25)), 3, 3)

def stromausfall():
    d = 5.0; tt = t_(d)
    thunk = (np.sin(2 * np.pi * 42 * tt * (1 - 0.2 * tt / d)) * np.exp(-tt * 3.2) + lp(noise(d), 300) * np.exp(-tt * 6) * 0.5)
    fh = 50 * np.maximum(0.25, 1 - tt / 2.6); ph = 2 * np.pi * np.cumsum(fh) / SR
    hum = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)) * np.exp(-tt * 0.9) * 0.6
    crack = np.zeros(len(tt))
    for _ in range(14):
        i = int(R.uniform(0.0, 1.2) * SR); c = hp(noise(0.02), 2000) * env_ad(int(0.02 * SR), 0.001, 0.004); crack[i:i + len(c)] += c * 0.5
    x = reverb(thunk + hum + crack, 2.2, 0.5)
    return pan(x, 0)

def herzschlag(d=12, bpm0=72, bpm1=96):
    x = np.zeros(int(d * SR)); s = 0.2
    while s < d - 1:
        bpm = bpm0 + (bpm1 - bpm0) * s / d
        for off, a in ((0, 1.0), (0.24, 0.7)):
            tt = t_(0.18); b = np.sin(2 * np.pi * (55 - 20 * tt / 0.18) * tt) * env_ad(len(tt), 0.006, 0.05) * a
            i = int((s + off) * SR); x[i:i + len(b)] += b
        s += 60 / bpm
    return lp(x, 160)

def hubschrauber_fern(d=16):
    # Rotor-"Blade Slap": kurze, tiefe Knatter-Impulse ~9 pro Sekunde + Turbine
    tt = t_(d); x = np.zeros(len(tt)); rate = 9.2; k = 0
    src = noise(d)
    while k / rate < d - 0.2:
        i = int(k / rate * SR); n = int(0.07 * SR)
        imp = bp(src[i:i + n], 60, 900, 2) * env_ad(n, 0.003, 0.018) * (1 + 0.25 * np.sin(k * 0.7))
        x[i:i + n] += imp; k += 1
    body = lp(pink(d), 250, 2) * 0.25
    whine = np.sin(2 * np.pi * 2350 * tt + 3 * np.sin(2 * np.pi * 0.3 * tt)) * 0.025
    x = (x * 1.4 + body + whine) * np.minimum(1, np.minimum(tt / 4, (d - tt) / 4))
    x = reverb(hp(lp(x, 1800), 110, 2), 1.6, 0.45)
    return pan(x, np.linspace(0.7, -0.6, len(x)))

def riser(d=5):
    tt = t_(d); k = tt / d
    s = bp(noise(d), 300, 6000, 2) * k ** 3 + np.sin(2 * np.pi * np.cumsum(120 + 900 * k ** 2) / SR) * k ** 2 * 0.4
    return pan(reverb(s, 1.5, 0.4), 0)

def stille_drone(d=20):
    tt = t_(d); x = sum(np.sin(2 * np.pi * f * tt + R.uniform(0, 6)) * a for f, a in ((55, 1), (82.4, 0.5), (110.3, 0.3)))
    x = x * (0.7 + 0.3 * smooth_rand(d, 0.2)) + lp(brown(d), 120) * 0.3
    return fade(stereo(x, np.roll(x, 900)), 3, 3)

# ---------- Spannung & Umgebung (Story "Jens – 18:30") ----------
def tippen(d=3.0):
    x = np.zeros(int(d * SR)); s = 0.05
    while s < d - 0.1:
        n = int(0.03 * SR); c = hp(noise(0.03), 2500, 2) * env_ad(n, 0.0005, 0.004) + bp(noise(0.03), 300, 900, 2) * env_ad(n, 0.001, 0.006) * 0.4
        i = int(s * SR); x[i:i + n] += c * R.uniform(0.5, 1.0); s += R.uniform(0.07, 0.16)
    return reverb(x, 0.2, 0.08)

def gesendet():
    d = 0.45; tt = t_(d); k = tt / d
    w = bp(noise(d), 600, 5000, 2) * np.sin(np.pi * k) ** 2
    blip = np.sin(2 * np.pi * np.cumsum(900 + 900 * k) / SR) * np.exp(-((tt - 0.3) / 0.05) ** 2) * 0.5
    return lp(w * 0.6 + blip, 6000)

def stich(d=5.0):
    # Kino-"Hit": tiefer Schlag + metallischer Nachklang + Sub-Abfall
    tt = t_(d)
    boom = np.sin(2 * np.pi * (48 * np.exp(-tt * 0.6) + 22) * tt) * np.exp(-tt * 1.2)
    crack = lp(noise(d), 2500) * np.exp(-tt * 18) * 0.8
    metal = sum(np.sin(2 * np.pi * f * tt + R.uniform(0, 6)) * np.exp(-tt * dk) * a for f, dk, a in ((311, 1.1, 0.3), (437, 1.6, 0.22), (622, 2.2, 0.15), (893, 3.0, 0.1), (1291, 4.0, 0.06)))
    x = reverb(boom * 1.2 + crack + metal, 3.0, 0.45)
    return stereo(x, np.roll(x, 400))

def braam(d=4.0):
    tt = t_(d); e = np.minimum(1, tt / 0.08) * np.exp(-tt * 0.5)
    x = sum(signal.sawtooth(2 * np.pi * f * tt * (1 + 0.002 * k)) for k, f in enumerate((41.2, 41.4, 82.4, 61.7, 123.5))) * e
    cut = 200 + 1800 * np.exp(-tt * 1.4); y = np.zeros_like(x); seg = SR // 50
    for i in range(0, len(x), seg): y[i:i + seg] = lp(x[max(0, i - seg):i + seg], max(80, cut[i]), 2)[-len(x[i:i + seg]):]
    y = reverb(y, 2.5, 0.4)
    return stereo(y, np.roll(y, 300))

def summen(d=4.0):
    # Laterne flackert: Netzbrummen, das an- und abreißt, mit Knacksern
    tt = t_(d); b = signal.sawtooth(2 * np.pi * 100 * tt) * 0.6 + np.sin(2 * np.pi * 50 * tt) * 0.5 + signal.square(2 * np.pi * 200 * tt) * 0.15
    b = bp(b, 80, 4000, 2) + hp(noise(d), 3000, 2) * 0.06
    gate = (np.sin(tt * 31) + np.sin(tt * 53) + (np.sin(tt * 7) > 0.6) * 2 > 1.2).astype(float)
    gate = lp(gate, 200, 1)
    x = b * (0.45 + 0.55 * gate)
    for _ in range(int(d * 2)):
        i = int(R.uniform(0, d - 0.03) * SR); c = hp(noise(0.015), 1500) * env_ad(int(0.015 * SR), 0.0005, 0.003); x[i:i + len(c)] += c * 0.5
    return pan(reverb(x * np.minimum(1, np.minimum(tt / 0.1, (d - tt) / 0.3)), 0.6, 0.2), 0.25)

def schritt(hart=1.0):
    n = int(0.16 * SR); tt = t_(0.16)
    thump = np.sin(2 * np.pi * 70 * tt) * env_ad(n, 0.002, 0.025) * 0.7
    grit = bp(noise(0.16), 900, 5000, 2) * env_ad(n, 0.001, 0.03) * 0.5 * hart
    grit2 = bp(noise(0.16), 2000, 8000, 2) * env_ad(n, 0.02, 0.04) * 0.25 * np.roll(np.ones(n), 0)
    return thump + grit + np.roll(grit2, int(0.03 * SR))

def atmer(d, rate=1.6, laut=1.0, rau=1.0):
    """schweres Atmen: ein/aus als gefiltertes Rauschen mit Formanten"""
    x = np.zeros(int(d * SR)); s = 0.0; k = 0
    while s < d - 0.6:
        per = 1 / rate * R.uniform(0.9, 1.1); inh = k % 2 == 0; L = int(per * 0.5 * SR); e = np.sin(np.linspace(0, np.pi, L)) ** (1.5 if inh else 1.0)
        src = noise(per * 0.5)
        v = (bp(src, 500, 1300, 2) * 0.8 + bp(src, 1600, 2600, 2) * 0.5 + bp(src, 2800, 4200, 2) * 0.25 * rau) * e * (0.7 if inh else 1.0)
        i = int(s * SR); x[i:i + L] += v[:len(x) - i] * laut; s += per * 0.5; k += 1
    return x

def jogger(d=5.0):
    tt = t_(d); x = np.zeros(len(tt)); c = 2.4; s = 0.1
    while s < d - 0.2:
        st = schritt(0.8) * R.uniform(0.7, 1.0); i = int(s * SR); x[i:i + len(st)] += st[:len(x) - i]; s += 1 / 2.9
    x += atmer(d, 2.9, 0.6)
    prox = 1 / (1 + ((tt - c) / 0.8) ** 2)
    x = lp(x, 6000) * prox
    return fade(pan(reverb(x, 0.5, 0.15), np.tanh((tt - c) / 0.9) * -0.85), 0.2, 0.4)

def transporter(d=9.0, stop=4.2):
    # Motor nähert sich (Drehzahl steigt), Reifen quietschen, dann Leerlauf
    tt = t_(d); rpm = np.where(tt < stop - 0.6, 34 + 10 * np.minimum(1, tt / 2.5), 0.0)
    rpm = np.where(tt >= stop - 0.6, 24, rpm); rpm = lp(rpm, 3, 1)
    ph = 2 * np.pi * np.cumsum(rpm) / SR
    eng = sum(np.sin(ph * k + 0.3 * k) / k ** 0.8 for k in range(1, 14)) * (1 + 0.3 * np.sin(ph * 0.5))
    eng = lp(eng, 1300) + lp(brown(d), 200) * 0.4
    near = np.minimum(1, (0.15 + tt / stop) ** 2); near = np.where(tt > stop, 1.0, near)
    eng *= near * np.where(tt > stop, 0.55, 1.0)
    tire = bp(noise(d), 300, 2500, 2) * near * np.where(tt < stop, 0.35, 0.0)
    sq = np.zeros(len(tt)); i0 = int((stop - 0.85) * SR); L = int(0.95 * SR); k = np.linspace(0, 1, L)
    f = 1900 + 300 * np.sin(2 * np.pi * 7 * k) - 400 * k
    sq[i0:i0 + L] = (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + bp(noise(0.95), 1500, 4000, 2)[:L] * 0.6) * np.sin(np.pi * k) ** 0.5
    x = eng * 0.9 + tire + sq * 0.8
    x = reverb(x, 0.9, 0.25)
    return fade(pan(x, np.clip(0.85 - tt / stop * 0.6, 0.25, 0.85)), 0.8, 0.8)

def tueren():
    d = 2.0; x = np.zeros(int(d * SR))
    for st, v in ((0.05, 1.0), (0.62, 0.8)):
        n = int(0.4 * SR); tt = t_(0.4)
        slam = np.sin(2 * np.pi * 62 * tt) * env_ad(n, 0.002, 0.06) + bp(noise(0.4), 150, 1400, 2) * env_ad(n, 0.001, 0.035) * 0.9
        latch = hp(noise(0.4), 2500) * env_ad(n, 0.0005, 0.006) * 0.4
        i = int(st * SR); x[i:i + n] += (slam + np.roll(latch, int(0.012 * SR))) * v
    return pan(reverb(x, 1.0, 0.3), 0.3)

def glocke(d=12.0, f0=98.0):
    # Kirchturmglocke in der Ferne, schlägt einmal (halbe Stunde)
    tt = t_(d); x = np.zeros(len(tt))
    for r_, a, dk in ((0.5, 0.5, 0.35), (1.0, 1.0, 0.6), (1.183, 0.6, 0.9), (1.506, 0.45, 1.1), (2.0, 0.5, 1.3), (2.514, 0.25, 1.8), (2.662, 0.2, 2.0), (3.011, 0.15, 2.4)):
        x += np.sin(2 * np.pi * f0 * r_ * tt * (1 + 0.0007 * np.sin(2 * np.pi * 1.5 * tt))) * a * np.exp(-tt * dk * 0.45)
    x[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    x = lp(x, 1800) + bp(noise(d), 600, 2500) * np.exp(-tt * 30) * 0.3
    x = reverb(x, 5.0, 0.7, 0.12)
    return pan(x, -0.45)

def rennen(d=7.0, rate=3.3):
    # eigene Schritte im Sprint + Kleidung + schweres Atmen
    x = np.zeros(int(d * SR)); s = 0.05
    while s < d - 0.2:
        st = schritt(1.1) * R.uniform(0.75, 1.0) * 1.3; i = int(s * SR); x[i:i + len(st)] += st[:len(x) - i]; s += 1 / rate * R.uniform(0.96, 1.04)
    rust = bp(noise(d), 1000, 5000, 2) * (0.5 + 0.5 * np.abs(np.sin(np.pi * rate * t_(d)))) * 0.08
    br = atmer(d, 2.4, 0.9)
    tt = t_(d); env = np.minimum(1, np.minimum(tt / 0.3, (d - tt) / 0.6))
    return pan(reverb((x + rust + br) * env, 0.5, 0.15), 0.0)

def atem_schwer(d=8.0):
    tt = t_(d); rate = 2.4 - 1.1 * tt / d
    x = np.zeros(int(d * SR)); s = 0
    seg = atmer(d, 1.0, 1.0)  # Platzhalter für Länge
    x = atmer(d, 2.0, 1.0) * np.linspace(1, 0.6, len(x))
    return pan(reverb(x, 0.4, 0.12), 0.0)

def laub(d=60):
    # Blätterrascheln im Wind (loop)
    g = smooth_rand(d, 0.25, 0.1, 1.0) ** 1.6
    ch = []
    for k in range(2):
        grains = (R.random(int(d * SR)) < 0.004 * (0.3 + g)).astype(float)
        grains = lp(grains * R.uniform(0.3, 1, int(d * SR)), 9000, 1)
        g2 = signal.fftconvolve(grains, np.exp(-np.arange(int(0.006 * SR)) / (0.0015 * SR)))[:int(d * SR)]
        ch.append(hp(g2 * noise(d), 1800, 2) * 0.6 + bp(noise(d), 2500, 7000, 2) * g * 0.12)
    return loopable(stereo(*ch))

def zug_fern(d=22.0):
    tt = t_(d); env = np.minimum(1, np.minimum(tt / 6, (d - tt) / 6)) ** 1.5
    rum = lp(brown(d), 160) * 0.9; cl = np.zeros(len(tt)); s = 0.4
    while s < d - 0.5:
        for o in (0, 0.13):
            n = int(0.08 * SR); c = bp(noise(0.08), 150, 900, 2) * env_ad(n, 0.002, 0.02); i = int((s + o) * SR); cl[i:i + n] += c
        s += 0.92
    horn = (np.sin(2 * np.pi * 370 * tt) + np.sin(2 * np.pi * 440 * tt) * 0.8) * ((tt > 7) & (tt < 8.6)) * 0.25
    horn = lp(horn, 1500) * np.minimum(1, np.minimum((tt - 7) / 0.15, (8.6 - tt) / 0.3)).clip(0, 1)
    x = reverb((rum + cl * 0.6 + horn) * env, 3.0, 0.6)
    return pan(lp(x, 1500), np.linspace(-0.6, 0.4, len(x)))

def funk_knacken():
    d = 0.35; x = bp(noise(d), 800, 3500, 2) * env_ad(int(d * SR), 0.003, 0.08)
    beep = np.sin(2 * np.pi * 1200 * t_(0.08)) * 0.4; x[:len(beep)] += beep
    return x

def hund_fern(d=6.0):
    # entfernter Hund: kurze, raue Bell-Laute
    x = np.zeros(int(d * SR)); s = 0.4
    for k in range(4):
        L = int(0.18 * SR); tt = t_(0.18); f = 520 - 900 * (tt - 0.05) ** 2 * 10
        v = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.18) ** 0.6
        v = bp(v, 400, 2200, 2) + bp(noise(0.18), 600, 1800, 2) * 0.3 * np.sin(np.pi * tt / 0.18)
        i = int(s * SR); x[i:i + L] += v; s += R.uniform(0.35, 0.6) if k % 2 == 0 else R.uniform(0.9, 1.3)
    return pan(lp(reverb(x, 2.0, 0.65), 2500), 0.6)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); print('Erzeuge Geräusche in', OUT)
    save('atmo_wind.wav', wind(), 0.8); save('atmo_stadt.wav', stadt(), 0.8); save('voegel.wav', voegel(), 0.7)
    save('auto_vorbei.wav', auto_vorbei()); save('vibration.wav', vibration())
    save('klingelton.wav', klingelton()); save('anruf_ende.wav', anruf_ende()); save('sirene_fern.wav', sirene_fern())
    save('stromausfall.wav', stromausfall()); save('herzschlag.wav', herzschlag()); save('hubschrauber_fern.wav', hubschrauber_fern())
    save('riser.wav', riser()); save('drone.wav', stille_drone())
    save('tippen.wav', tippen(), 0.5); save('gesendet.wav', gesendet(), 0.5); save('stich.wav', stich()); save('braam.wav', braam())
    save('summen.wav', summen(), 0.7); save('jogger.wav', jogger(), 0.8); save('transporter.wav', transporter()); save('tueren.wav', tueren())
    save('glocke.wav', glocke(), 0.8); save('rennen.wav', rennen()); save('atem_schwer.wav', atem_schwer(), 0.8); save('atmo_laub.wav', laub(), 0.6)
    save('zug_fern.wav', zug_fern(), 0.7); save('funk_knacken.wav', funk_knacken(), 0.6); save('hund_fern.wav', hund_fern(), 0.6)
