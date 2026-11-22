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


# ---------- Teil 2: Regen, Gewitter, Gasse, Hinterzimmer ----------
def grains(d, rate, f_lo, f_hi, dec=(0.004, 0.02), amp=(0.2, 1.0)):
    """viele kurze, resonante Tropfen-Klicks (für Regen/Tropfen)"""
    x = np.zeros(int(d * SR)); n = int(d * rate)
    for _ in range(n):
        i = int(R.uniform(0, d - 0.1) * SR); f = R.uniform(f_lo, f_hi); dk = R.uniform(*dec); L = int(dk * 6 * SR)
        tt = np.arange(L) / SR; g = np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / (dk * 6))) * np.exp(-tt / dk) * R.uniform(*amp)
        x[i:i + L] += g[:len(x) - i]
    return x

def regen(d=60):
    ch = []
    for k in range(2):
        g = 0.75 + 0.25 * smooth_rand(d, 0.15, 0, 1)
        hiss = bp(pink(d), 500, 9000, 2) * 0.55 * g + hp(noise(d), 6000, 2) * 0.12
        drops = hp(grains(d, 900, 2500, 7000, (0.0008, 0.003), (0.1, 0.6)), 1500, 2) * 0.5
        near = grains(d, 70, 900, 2500, (0.002, 0.008), (0.2, 0.8)) * 0.35
        low = lp(brown(d), 250) * 0.25
        ch.append(hiss + drops + near + low)
    return loopable(stereo(*ch))

def tropfen(d=60):
    # einzelne Tropfen in Pfützen / auf Blech + eine plätschernde Regenrinne links
    ch = []
    for k in range(2):
        x = np.zeros(int(d * SR)); s_ = R.uniform(0, 0.5)
        while s_ < d - 0.3:
            f = R.uniform(700, 2400); L = int(0.12 * SR); tt = t_(0.12)
            pl = np.sin(2 * np.pi * f * tt * (1 + 0.6 * tt / 0.12)) * np.exp(-tt / R.uniform(0.012, 0.04)) * R.uniform(0.2, 0.7)
            i = int(s_ * SR); x[i:i + L] += pl[:len(x) - i]; s_ += R.exponential(0.22)
        gush = bp(noise(d), 250, 2800, 2) * (0.5 + 0.5 * smooth_rand(d, 3.0, 0.2, 1.0)) * (0.5 if k == 0 else 0.15)
        gush += grains(d, 400, 500, 1800, (0.003, 0.01), (0.1, 0.5)) * (0.4 if k == 0 else 0.12)
        ch.append(reverb(x, 0.8, 0.3) + gush)
    return loopable(stereo(*ch))

def donner(d=9.0, nah=True):
    tt = t_(d); x = np.zeros(len(tt))
    if nah:
        crack = hp(noise(0.5), 1200, 2) * env_ad(int(0.5 * SR), 0.001, 0.12) * 2.6
        crack += bp(noise(0.5), 300, 3000, 2) * env_ad(int(0.5 * SR), 0.001, 0.15) * 0.9
        x[:len(crack)] += crack
    rum = lp(brown(d), 160 if nah else 110, 4) * 3.0
    env = np.zeros(len(tt)); t0 = 0.05 if nah else 0.6
    for k in range(6):
        c = t0 + k * R.uniform(0.35, 0.9); a = R.uniform(0.5, 1.0) * (0.85 ** k)
        env += a * np.exp(-np.maximum(0, tt - c) / R.uniform(0.6, 1.4)) * (tt >= c - 0.15) * np.clip((tt - c + 0.15) / 0.15, 0, 1)
    x += rum * env * (1.0 if nah else 0.7)
    x = reverb(x, 3.5, 0.5, 0.05)
    return fade(pan(x, np.linspace(-0.3, 0.3, len(x))), 0.01, 1.5)

def bubbles(d, n, f_lo=500, f_hi=2600):
    # Minnaert-Blasen: kurze, nach oben gleitende Sinus-Pieper = typischer Wasserklang
    x = np.zeros(int(d * SR))
    for _ in range(n):
        i = int(R.uniform(0, d * 0.7) * SR); f0 = R.uniform(f_lo, f_hi); tau = R.uniform(0.003, 0.012); L = int(tau * 7 * SR); tt = np.arange(L) / SR
        b = np.sin(2 * np.pi * f0 * tt * (1 + tt / (tau * 3))) * np.exp(-tt / tau) * R.uniform(0.3, 1.0); x[i:i + L] += b[:len(x) - i]
    return x

def splash_step(hart=1.0):
    # Fuß tritt in eine Pfütze: Platschen + Blasen + Sprühtropfen, kaum Absatz
    n = int(0.4 * SR); tt = t_(0.4)
    thump = np.sin(2 * np.pi * 85 * tt) * env_ad(n, 0.002, 0.015) * 0.15 * hart
    slosh = bp(noise(0.4), 400, 6000, 2) * (np.minimum(1, tt / 0.004) * np.exp(-tt / 0.05)) * 0.9
    bub = bubbles(0.4, 14) * 0.9
    spray = grains(0.4, 300, 2500, 7000, (0.0008, 0.003), (0.1, 0.5)) * np.exp(-tt / 0.1)
    return thump + slosh + bub + spray

def rennen_nass(d=4.0, rate=3.3):
    x = np.zeros(int(d * SR)); s_ = 0.05
    while s_ < d - 0.3:
        st = splash_step(1.0) * R.uniform(0.8, 1.0); i = int(s_ * SR); x[i:i + len(st)] += st[:len(x) - i]; s_ += 1 / rate * R.uniform(0.95, 1.05)
    x += atmer(d, 2.4, 0.45)
    return pan(reverb(x, 0.8, 0.25), 0.0)

def stiefel_nass(d=8.0):
    x = np.zeros(int(d * SR))
    for off, rate in ((0.0, 1.9), (0.24, 1.85)):
        s_ = off
        while s_ < d - 0.4:
            near = 0.1 + 0.9 * (s_ / d) ** 1.4
            st = splash_step(1.0) * R.uniform(0.8, 1.0)
            st = lp(st, 1500) * (1 - near) + st * near
            i = int(s_ * SR); x[i:i + len(st)] += st[:len(x) - i] * near; s_ += 1 / rate * R.uniform(0.97, 1.03)
    return pan(reverb(x, 1.6, 0.45, 0.05), 0.0)

def tonne_katze(d=2.6):
    x = np.zeros(int(d * SR))
    # Katze: "Miau"-Schrei (Formant wandert i -> a -> u) + Fauchen
    L = int(0.6 * SR); tt = t_(0.6); k = tt / 0.6
    f0 = 520 + 380 * np.sin(np.pi * k) ** 0.6
    src = signal.sawtooth(2 * np.pi * np.cumsum(f0) / SR) * np.sin(np.pi * k) ** 0.5
    v = np.zeros(L)
    for a, b in ((0, 0.3), (0.3, 0.7), (0.7, 1.0)):
        m = (k >= a) & (k < b); fc = 2600 if a == 0 else 1500 if a == 0.3 else 900
        v += bp(src, fc * 0.7, fc * 1.3, 2) * m
    hiss = bp(noise(0.6), 2500, 8000, 2) * np.exp(-np.maximum(0, tt - 0.45) / 0.08) * (tt > 0.45) * 0.7
    x[:L] += (v * 1.6 + hiss)
    # Blechdeckel scheppert: harte, helle Schläge + metallisches Rasseln, kurze Nachklänge
    for st, v_ in ((0.15, 1.0), (0.42, 0.9), (0.55, 0.6), (0.63, 0.45), (0.69, 0.35), (0.74, 0.25), (0.78, 0.18)):
        n = int(0.5 * SR); tt = t_(0.5)
        hit = bp(noise(0.5), 1200, 9000, 2) * np.exp(-tt / 0.03) * 1.4
        for fr, a, dk in ((1320, 0.4, 0.09), (2170, 0.45, 0.07), (3390, 0.35, 0.05), (4730, 0.25, 0.04), (6110, 0.15, 0.03)):
            hit += np.sin(2 * np.pi * fr * R.uniform(0.96, 1.04) * tt) * np.exp(-tt / dk) * a
        i = int(st * SR); x[i:i + n] += hit[:len(x) - i] * v_ * 1.2
    return pan(reverb(x, 1.0, 0.3), np.linspace(-0.5, -0.1, len(x)))

def knarren(d=3.2):
    # alte Holztür: unregelmäßige Reibimpulse, jeder Impuls regt Holzresonanzen an
    tt = t_(d); rate = 16 + 55 * np.sin(np.pi * np.clip(tt / d, 0, 1)) ** 1.5 + smooth_rand(d, 3, -10, 10)
    ph = np.cumsum(np.maximum(6, rate)) / SR; idx = np.nonzero(np.diff(np.floor(ph)) > 0)[0]
    imp = np.zeros(len(tt)); imp[idx] = R.uniform(0.3, 1.0, len(idx)) * (0.5 + 0.5 * np.sin(np.pi * tt[idx] / d))
    L = int(0.04 * SR); k = np.arange(L) / SR
    ir = sum(np.sin(2 * np.pi * f * k) * np.exp(-k / dk) * a for f, a, dk in ((480, 1.0, 0.012), (1090, 0.8, 0.009), (1730, 0.6, 0.007), (2480, 0.4, 0.005), (3400, 0.2, 0.004)))
    x = signal.fftconvolve(imp, ir)[:len(tt)]
    x += bp(noise(d), 800, 3000, 2) * signal.fftconvolve(imp, np.ones(int(0.004 * SR)))[:len(tt)] * 0.15
    x *= np.minimum(1, np.minimum(tt / 0.15, (d - tt) / 0.3)).clip(0, 1)
    return pan(reverb(x, 0.9, 0.35), 0.55)

def tuer_knall():
    d = 3.0; n = int(0.6 * SR); tt = t_(0.6); x = np.zeros(int(d * SR))
    slam = np.sin(2 * np.pi * 48 * tt) * env_ad(n, 0.002, 0.12) * 1.3 + bp(noise(0.6), 80, 1800, 2) * env_ad(n, 0.001, 0.06) * 1.1
    latch = hp(noise(0.6), 2500) * env_ad(n, 0.0005, 0.008) * 0.6
    frame = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.12) * a for f, a in ((140, 0.4), (310, 0.3), (720, 0.15)))
    rattle = grains(0.5, 60, 1500, 4000, (0.003, 0.012), (0.1, 0.35))
    x[:n] += slam + frame + np.roll(latch, int(0.015 * SR)); x[int(0.04 * SR):int(0.04 * SR) + len(rattle)] += rattle
    return pan(reverb(x, 1.6, 0.5, 0.02), -0.5)

def klopfen(d=2.6):
    x = np.zeros(int(d * SR))
    for st, v in ((0.0, 1.0), (0.33, 0.95), (0.62, 1.0), (1.25, 1.0), (1.5, 0.9)):
        n = int(0.35 * SR); tt = t_(0.35)
        bang = np.sin(2 * np.pi * 75 * tt) * env_ad(n, 0.002, 0.07) * 1.2 + bp(noise(0.35), 150, 900, 2) * env_ad(n, 0.001, 0.04)
        bang += grains(0.35, 25, 1500, 3500, (0.003, 0.008), (0.05, 0.2))
        i = int(st * SR); x[i:i + n] += bang * v
    return pan(reverb(x, 0.8, 0.3), -0.6)

def ticken(d=30.0):
    x = np.zeros(int(d * SR)); k = 0
    for s_ in np.arange(0.1, d - 0.1, 0.5):
        n = int(0.05 * SR); tt = t_(0.05); f = 2600 if k % 2 == 0 else 2100
        c = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.004) + bp(noise(0.05), 1000, 6000, 2) * np.exp(-tt / 0.002) * 0.6
        i = int(s_ * SR); x[i:i + n] += c; k += 1
    return pan(reverb(x, 0.5, 0.2), 0.3)

def drinnen(d=60):
    # Regen draußen, gehört durch Fenster und Wand (tiefpassgefiltert) + Prasseln an der Scheibe + Kerzenknistern
    r_ = regen(d + 2.0)
    ch = []
    for k in range(2):
        x = lp(r_[:, k], 2600, 2) * 0.7 + lp(r_[:, k], 500, 2) * 0.5 + lp(brown(d), 90) * 0.15
        x += grains(d, 1.5, 3000, 7000, (0.001, 0.004), (0.05, 0.25))
        ch.append(x[:int(d * SR)])
    return loopable(stereo(*ch))

def heli_nah(d=14.0):
    tt = t_(d); near = np.clip(tt / 6.0, 0, 1) ** 1.5 * np.where(tt > 10, np.clip(1 - (tt - 10) / 4, 0.3, 1), 1)
    br = 14.5 + 0.5 * np.sin(2 * np.pi * 0.07 * tt); ph = np.cumsum(br) / SR
    chop = (0.5 + 0.5 * np.cos(2 * np.pi * ph)) ** 6
    blade = lp(noise(d), 900, 2) * chop * 1.4 + np.sin(2 * np.pi * np.cumsum(br * 2) / SR) * chop * 0.4
    turb = (np.sin(2 * np.pi * 2350 * tt) * 0.05 + bp(noise(d), 1800, 4000, 2) * 0.08) * near
    rumble = lp(brown(d), 120) * 0.8
    x = (blade + rumble) * (0.2 + 0.8 * near) + turb
    x = lp(x, 900) * (1 - near) + lp(x, 6000) * near
    return fade(pan(reverb(x, 1.2, 0.3), np.linspace(-0.6, 0.2, len(x))), 1.5, 2.0)

def autoalarm_fern(d=10.0):
    # typische Autoalarm-Folge: Trillern, Auf-und-ab, schnelle Zwitscher-Töne, dazu Hupe
    tt = t_(d); seg = tt % 6.0
    f = np.where(seg < 2.0, np.where((tt * 8) % 2 < 1, 1050, 1450), np.where(seg < 4.0, 900 + 900 * ((tt * 3) % 1), np.where((tt * 14) % 2 < 1, 2100, 1600)))
    x = signal.square(2 * np.pi * np.cumsum(f) / SR) * 0.3
    honk = (seg < 2.0) * ((tt * 2) % 1 < 0.5)
    x = x * (1 - 0.5 * honk) + signal.sawtooth(2 * np.pi * 420 * tt) * honk * 0.25
    x = lp(bp(x, 400, 4000, 2), 2200)
    return fade(pan(reverb(x, 2.2, 0.65, 0.08), 0.7), 0.3, 1.5)

TEIL2 = {'atmo_regen.wav': (lambda: regen(), 0.7), 'atmo_tropfen.wav': (lambda: tropfen(), 0.6), 'donner_nah.wav': (lambda: donner(9.0, True), 0.95),
         'donner_fern.wav': (lambda: donner(10.0, False), 0.8), 'rennen_nass.wav': (rennen_nass, 0.9), 'stiefel_nass.wav': (stiefel_nass, 0.8),
         'tonne_katze.wav': (tonne_katze, 0.9), 'knarren.wav': (knarren, 0.8), 'tuer_knall.wav': (tuer_knall, 0.95), 'klopfen.wav': (klopfen, 0.95),
         'ticken.wav': (ticken, 0.5), 'atmo_drinnen.wav': (lambda: drinnen(), 0.6), 'heli_nah.wav': (heli_nah, 0.85), 'autoalarm_fern.wav': (autoalarm_fern, 0.6)}


# ---------- Teil 3: U-Bahnhof ----------
def big_hall(x, rt=2.8, wet=0.5): return reverb(x, rt, wet, 0.04)

def tuer_aufbrechen(d=3.0):
    # Holz bricht: Wumms + viele kurze, harte Knackser (Splitter) + herabfallende Teile
    x = np.zeros(int(d * SR)); n = int(0.8 * SR); tt = t_(0.8)
    x[:n] += np.sin(2 * np.pi * 55 * tt) * env_ad(n, 0.001, 0.1) * 1.3 + bp(noise(0.8), 200, 2500, 2) * env_ad(n, 0.001, 0.06) * 1.2
    for k in range(40):
        L = int(0.015 * SR); tk = np.arange(L) / SR; f = R.uniform(900, 3200)
        c = (np.sin(2 * np.pi * f * tk) * 0.6 + R.standard_normal(L) * 0.8) * np.exp(-tk / 0.003)
        i = int((0.005 + R.exponential(0.06)) * SR); x[i:i + L] += c * R.uniform(0.3, 1.0)
    deb = grains(1.6, 18, 300, 1200, (0.008, 0.03), (0.2, 0.6)); i = int(0.6 * SR); x[i:i + len(deb)] += deb * 0.5
    return pan(lp(reverb(x, 1.0, 0.35), 3500), -0.2)

def leiter(d=2.6):
    # Schuhe auf Eisensprossen: dumpfer, kurzer Metallschlag + Schaben, kein Klingeln
    x = np.zeros(int(d * SR))
    for st in np.arange(0.05, d - 0.3, 0.42):
        n = int(0.25 * SR); tt = t_(0.25)
        hit = np.sin(2 * np.pi * 140 * tt) * np.exp(-tt / 0.03) * 0.8 + bp(noise(0.25), 300, 1800, 2) * np.exp(-tt / 0.02) * 1.0
        hit += sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.018) * a for f, a in ((410, 0.25), (930, 0.15)))
        scuff = bp(noise(0.25), 1500, 5000, 2) * np.exp(-np.maximum(0, tt - 0.03) / 0.04) * (tt > 0.03) * 0.25
        i = int((st + R.uniform(-0.03, 0.03)) * SR); x[i:i + n] += (hit + scuff) * R.uniform(0.6, 1.0)
    return pan(big_hall(x, 1.6, 0.4), -0.3)

def falltuer():
    d = 3.5; n = int(1.5 * SR); tt = t_(1.5); x = np.zeros(int(d * SR))
    slam = np.sin(2 * np.pi * 50 * tt) * env_ad(n, 0.002, 0.15) * 1.2 + bp(noise(1.5), 100, 2000, 2) * env_ad(n, 0.001, 0.05)
    ring = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / dk) * a for f, a, dk in ((180, 0.5, 0.5), (433, 0.35, 0.4), (967, 0.2, 0.3), (1733, 0.12, 0.2)))
    x[:n] += slam + ring
    return pan(big_hall(x, 3.0, 0.55), -0.4)

def tunnel(d=60):
    ch = []
    for k in range(2):
        rum = lp(brown(d), 90, 4) * 1.2 * (0.7 + 0.3 * smooth_rand(d, 0.08, 0, 1))
        air = bp(pink(d), 150, 900, 2) * 0.35 * (0.6 + 0.4 * smooth_rand(d, 0.12, 0, 1))
        hum = np.sin(2 * np.pi * 50 * t_(d)) * 0.04 + np.sin(2 * np.pi * 100 * t_(d)) * 0.02
        ch.append(rum + air + hum)
    return loopable(stereo(*ch))

def tropfen_hall(d=60):
    ch = []
    for k in range(2):
        x = np.zeros(int(d * SR)); s_ = R.uniform(0, 1)
        while s_ < d - 0.5:
            L = int(0.08 * SR); tt = t_(0.08); f = R.uniform(500, 1100)
            pl = (np.sin(2 * np.pi * f * tt * (1 + 1.5 * tt / 0.08)) * np.exp(-tt / 0.012) + bp(noise(0.08), 800, 4000, 2) * np.exp(-tt / 0.003) * 0.6) * R.uniform(0.3, 1.0)
            i = int(s_ * SR); x[i:i + L] += pl[:len(x) - i]; s_ += R.exponential(0.9)
        ch.append(reverb(x, 3.5, 0.8, 0.05))
    return loopable(stereo(*ch))

def neon_summen(d=30):
    tt = t_(d)
    x = sum(np.sin(2 * np.pi * 100 * k * tt) / k for k in range(1, 12)) * 0.15
    x = bp(x, 90, 3000, 2) * (0.8 + 0.2 * smooth_rand(d, 1.0, 0, 1))
    clicks = (R.random(len(tt)) < 0.00008).astype(float); x += hp(signal.fftconvolve(clicks, np.exp(-np.arange(400) / 60))[:len(tt)], 1500) * 0.6
    return loopable(stereo(x, x * 0.9))

def schritte_hall(d=13.0):
    x = np.zeros(int(d * SR)); s_ = 0.1
    while s_ < d - 0.4:
        for off, v in ((0, 1.0), (0.27, 0.7)):
            st = schritt(0.9) * R.uniform(0.7, 1.0) * v; i = int((s_ + off) * SR); x[i:i + len(st)] += st[:len(x) - i]
        s_ += 0.58
    return pan(big_hall(lp(x, 5000), 2.4, 0.5), 0.0)

def rennen_hall(d=6.5):
    x = rennen(d, 3.5); x = x[:, 0] if x.ndim == 2 else x
    return pan(reverb(x, 1.8, 0.32, 0.03), 0.0)

def ratten(d=3.2):
    # Krallen auf Beton, Rascheln von Papier, wenige kurze, raue Quiekser
    tt = t_(d); env = np.clip(1.3 - tt / d, 0, 1)
    claws = grains(d, 220, 1800, 6000, (0.0006, 0.002), (0.1, 0.6)) * env
    rustle = bp(noise(d), 1500, 7000, 2) * (0.3 + 0.7 * smooth_rand(d, 12, 0, 1)) * 0.25 * env
    x = claws + rustle
    for k in range(3):
        L = int(0.07 * SR); tk = np.arange(L) / SR; f = R.uniform(2600, 3600)
        sq = (signal.sawtooth(2 * np.pi * f * tk) * 0.5 + noise(0.07)[:L] * 0.5) * np.sin(np.pi * tk / tk[-1]) ** 0.7
        sq = bp(sq, 2000, 6000, 2) * 0.5; i = int(R.uniform(0.1, d - 0.5) * SR); x[i:i + L] += sq
    return pan(big_hall(x, 1.2, 0.25), np.linspace(-0.6, 0.5, len(x)))

def hund_hall(d=5.0):
    x = hund_fern(d)
    return pan(big_hall(x[:, 0] if x.ndim == 2 else x, 2.8, 0.55), 0.3)

def zug_kommt(d=16.0):
    # U-Bahn: anschwellendes Rollgeräusch, Motor-Heulen, Schienenstöße, Bremsquietschen, Stillstand, Zischen
    tt = t_(d); stop = 13.5
    near = np.clip(tt / stop, 0, 1) ** 2.0 * (tt < stop) + (tt >= stop) * 1.0
    speed = np.where(tt < stop, 1 - (tt / stop) ** 2.5 * 0.92, 0.0)
    roar = (bp(noise(d), 200, 2500, 2) * 0.9 + lp(brown(d), 160, 4) * 1.6) * (0.1 + 0.9 * near) * (0.25 + 0.75 * speed + (tt >= stop) * 0.08)
    f_m = 180 + 520 * speed; ph = 2 * np.pi * np.cumsum(f_m) / SR
    whine = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) * 0.12 * near * (tt < stop)
    clack = np.zeros(len(tt)); s_ = 0.5
    while s_ < stop:
        v = 0.1 + 0.9 * np.clip(s_ / stop, 0, 1) ** 2; per = 1.0 / max(0.25, speed[int(s_ * SR)] * 1.8)
        for off in (0, 0.09):
            n = int(0.06 * SR); c = bp(noise(0.06), 400, 2500, 2) * env_ad(n, 0.001, 0.012) * v; i = int((s_ + off) * SR); clack[i:i + n] += c
        s_ += per
    sq = np.zeros(len(tt)); a0 = int(9.8 * SR); a1 = int(stop * SR); kk = np.linspace(0, 1, a1 - a0)
    f = 2600 + 400 * np.sin(2 * np.pi * 6 * kk) - 300 * kk
    sq[a0:a1] = lp(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * kk) ** 0.5 * 0.16 + bp(noise((a1 - a0) / SR), 2200, 5000, 2)[:a1 - a0] * np.sin(np.pi * kk) * 0.15, 3500)
    hiss = hp(noise(d), 2500) * np.exp(-np.maximum(0, tt - stop - 0.3) / 0.5) * (tt > stop + 0.3) * 0.45
    x = roar + whine + clack * 0.6 + sq + hiss
    return fade(pan(reverb(x, 2.4, 0.4, 0.04), np.clip(-0.7 + tt / stop * 1.1, -0.7, 0.4)), 2.0, 1.5)

def zug_tueren():
    d = 3.0; tt = t_(d); x = np.zeros(len(tt))
    hiss = hp(noise(0.6), 1800) * np.exp(-t_(0.6) / 0.18) * 0.7; x[:len(hiss)] += hiss
    slide = bp(noise(0.9), 300, 1500, 2) * np.sin(np.pi * t_(0.9) / 0.9) * 0.5; i = int(0.15 * SR); x[i:i + len(slide)] += slide
    thunk = np.sin(2 * np.pi * 90 * t_(0.2)) * env_ad(int(0.2 * SR), 0.002, 0.04) * 0.6; i = int(1.0 * SR); x[i:i + len(thunk)] += thunk
    for st, f in ((1.4, 880), (1.75, 698)):
        n = int(0.6 * SR); tk = t_(0.6); ch = (np.sin(2 * np.pi * f * tk) + 0.3 * np.sin(2 * np.pi * f * 2.01 * tk)) * np.exp(-tk / 0.25) * 0.4; i = int(st * SR); x[i:i + n] += ch
    return pan(big_hall(x, 2.0, 0.4), 0.5)

TEIL3 = {'tuer_aufbrechen.wav': (tuer_aufbrechen, 0.95), 'leiter.wav': (leiter, 0.8), 'falltuer.wav': (falltuer, 0.95), 'atmo_tunnel.wav': (lambda: tunnel(), 0.7),
         'atmo_tropfen_hall.wav': (lambda: tropfen_hall(), 0.6), 'neon_summen.wav': (lambda: neon_summen(), 0.5), 'schritte_hall.wav': (schritte_hall, 0.8),
         'rennen_hall.wav': (rennen_hall, 0.9), 'ratten.wav': (ratten, 0.8), 'hund_hall.wav': (hund_hall, 0.8), 'zug_kommt.wav': (zug_kommt, 0.95), 'zug_tueren.wav': (zug_tueren, 0.8)}


# ---------- Teil 4: im fahrenden Zug ----------
def zug_innen(d=60):
    # Fahrgeräusch innen: Rollen, Schienenstöße im Takt, klappernde Fenster, Motorsurren
    tt = t_(d); ch = []
    clack = np.zeros(len(tt)); s_ = 0.2
    while s_ < d - 0.3:
        for off, v in ((0, 1.0), (0.12, 0.8)):
            n = int(0.08 * SR); c = bp(noise(0.08), 300, 2000, 2) * env_ad(n, 0.001, 0.015) * v; i = int((s_ + off) * SR); clack[i:i + n] += c
        s_ += 1.05 + R.uniform(-0.03, 0.03)
    for k in range(2):
        roll = lp(brown(d), 180, 4) * 1.4 + bp(noise(d), 300, 1500, 2) * 0.35
        rattle = grains(d, 40, 1500, 4000, (0.002, 0.008), (0.05, 0.25))
        whine = np.sin(2 * np.pi * 620 * tt) * 0.03 + np.sin(2 * np.pi * 1240 * tt) * 0.015
        ch.append(roll + clack * 0.8 + rattle + whine)
    return loopable(stereo(*ch))

def zug_anfahrt(d=9.0):
    tt = t_(d); k = np.clip(tt / 8, 0, 1); f = 150 + 500 * k ** 1.3; ph = 2 * np.pi * np.cumsum(f) / SR
    whine = (np.sin(ph) + 0.4 * np.sin(2 * ph)) * 0.12 * (0.3 + 0.7 * k)
    roll = (lp(brown(d), 160, 4) * 1.2 + bp(noise(d), 300, 1800, 2) * 0.3) * (0.15 + 0.85 * k)
    clunk = np.zeros(len(tt)); n = int(0.3 * SR); clunk[:n] = np.sin(2 * np.pi * 60 * t_(0.3)) * env_ad(n, 0.002, 0.06) * 0.8 + bp(noise(0.3), 200, 1500, 2) * env_ad(n, 0.001, 0.04) * 0.6
    return fade(pan(reverb(whine + roll + clunk, 1.0, 0.2), 0.0), 0.05, 1.5)

def notbremse(d=4.0):
    tt = t_(d); stop = 2.4
    f = 2300 + 600 * np.sin(2 * np.pi * 7 * tt) - 500 * np.clip(tt / stop, 0, 1)
    sq = lp(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + bp(noise(d), 1800, 4500, 2) * 0.35, 4000) * (tt < stop) * np.clip(tt / 0.1, 0, 1)
    rum = lp(brown(d), 150, 4) * 1.6 * np.clip(1 - tt / stop, 0, 1)
    jolt = np.zeros(len(tt)); i = int(stop * SR); n = int(0.6 * SR); jolt[i:i + n] = (np.sin(2 * np.pi * 50 * t_(0.6)) * env_ad(n, 0.002, 0.1) * 1.2 + grains(0.6, 120, 800, 3000, (0.003, 0.012), (0.2, 0.6)))[:len(jolt) - i]
    hiss = hp(noise(d), 2500) * np.exp(-np.maximum(0, tt - stop - 0.2) / 0.4) * (tt > stop + 0.2) * 0.4
    return pan(reverb(sq + rum + jolt + hiss, 1.4, 0.3), 0.0)

def dach_schlag():
    d = 2.0; n = int(1.2 * SR); tt = t_(1.2); x = np.zeros(int(d * SR))
    boom = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / dk) * a for f, a, dk in ((58, 1.2, 0.18), (131, 0.6, 0.15), (287, 0.35, 0.12), (512, 0.2, 0.08)))
    boom += bp(noise(1.2), 80, 1200, 2) * np.exp(-tt / 0.03) * 1.0
    x[:n] += boom
    return pan(reverb(x, 0.8, 0.25), 0.0)

def schaben(d=3.6):
    # Metall kratzt über das Dach, bewegt sich nach vorne
    tt = t_(d); rate = 70 + 50 * smooth_rand(d, 3, 0, 1)
    ph = np.cumsum(rate) / SR; idx = np.nonzero(np.diff(np.floor(ph)) > 0)[0]
    imp = np.zeros(len(tt)); imp[idx] = R.uniform(0.3, 1.0, len(idx))
    L = int(0.03 * SR); k = np.arange(L) / SR
    ir = sum(np.sin(2 * np.pi * f * k) * np.exp(-k / dk) * a for f, a, dk in ((820, 1.0, 0.01), (1630, 0.7, 0.008), (2950, 0.5, 0.006)))
    x = signal.fftconvolve(imp, ir)[:len(tt)] + bp(noise(d), 1500, 6000, 2) * 0.25
    x *= np.minimum(1, np.minimum(tt / 0.3, (d - tt) / 0.4)).clip(0, 1)
    for st in (0.4, 1.6, 2.7):  # schwere Schritte auf dem Dach
        n = int(0.4 * SR); i = int(st * SR); x[i:i + n] += np.sin(2 * np.pi * 70 * t_(0.4)) * np.exp(-t_(0.4) / 0.08) * 1.2
    return pan(reverb(x, 0.9, 0.3), np.linspace(0.3, -0.3, len(x)))

TEIL4 = {'atmo_zug_innen.wav': (lambda: zug_innen(), 0.7), 'zug_anfahrt.wav': (zug_anfahrt, 0.85), 'notbremse.wav': (notbremse, 0.95), 'dach_schlag.wav': (dach_schlag, 0.95), 'schaben.wav': (schaben, 0.8)}


# ---------- Teil 5: Umspannwerk ----------
def brummen(d=60):
    # Trafo-Brummen 100 Hz mit Obertönen, leichtes Knistern (Korona), schwankend
    tt = t_(d); ch = []
    for k in range(2):
        hum = sum(np.sin(2 * np.pi * 100 * n * tt + k * n) / n ** 1.2 for n in range(1, 9)) * (0.85 + 0.15 * smooth_rand(d, 0.3, 0, 1))
        corona = hp(noise(d), 3000) * (smooth_rand(d, 2.0, 0, 1) ** 4) * 0.25 + grains(d, 15, 3000, 8000, (0.0005, 0.002), (0.05, 0.3))
        ch.append(bp(hum, 80, 2500, 2) * 0.4 + corona + lp(brown(d), 80) * 0.3)
    return loopable(stereo(*ch))

def schritte_kies(d=13.0):
    # Kies: langes, körniges Knirschen (Steinchen reiben), weicher Anfang, kein Klatschen
    x = np.zeros(int(d * SR)); s_ = 0.1
    while s_ < d - 0.5:
        for off, v in ((0, 1.0), (0.3, 0.8)):
            n = int(0.35 * SR); tt = t_(0.35); env = np.clip(tt / 0.03, 0, 1) * np.exp(-tt / 0.11)
            stones = grains(0.35, 2200, 700, 4000, (0.0004, 0.0015), (0.05, 0.5)) * env
            rub = bp(noise(0.35), 500, 2500, 2) * env * 0.35
            i = int((s_ + off) * SR); x[i:i + n] += ((stones + rub) * v * R.uniform(0.7, 1.0))[:len(x) - i]
        s_ += 0.62
    return pan(lp(reverb(x, 0.5, 0.12), 6000), 0.0)

def funken(d=1.8):
    # Lichtbogen: harter Knall, dann raues 50-Hz-Brummen mit Verzerrung und Knistern
    tt = t_(d)
    crack = hp(noise(d), 600, 2) * np.exp(-tt / 0.02) * 2.0 + np.sin(2 * np.pi * 60 * tt) * np.exp(-tt / 0.08) * 1.0
    buzz = np.tanh(6 * (signal.square(2 * np.pi * 100 * tt) * 0.5 + signal.sawtooth(2 * np.pi * 50 * tt) * 0.5 + noise(d) * 0.3)) * 0.5
    buzz = bp(buzz, 80, 5000, 2) * np.clip(tt / 0.02, 0, 1) * np.exp(-tt / 0.5) * (0.6 + 0.4 * (R.random(len(tt)) < 0.3))
    crk = grains(d, 200, 1500, 6000, (0.0005, 0.002), (0.2, 1.0)) * np.exp(-tt / 0.5)
    return pan(reverb(crack + buzz + crk, 0.9, 0.3), 0.4)

def tor(d=2.5):
    # Maschendrahttor rasselt auf, Kette fällt
    tt = t_(d); x = grains(d, 260, 1500, 6000, (0.002, 0.008), (0.1, 0.6)) * np.clip(1.4 - tt, 0, 1)
    for st in (0.0, 0.5, 1.1):
        n = int(0.4 * SR); hit = sum(np.sin(2 * np.pi * f * t_(0.4)) * np.exp(-t_(0.4) / 0.08) * a for f, a in ((540, 0.4), (1270, 0.3), (2210, 0.2))); i = int(st * SR); x[i:i + n] += hit
    return pan(reverb(x, 1.4, 0.4), 0.0)

def flutlicht(d=3.0):
    # Schütz klackt, Lampen zünden mit dumpfem Wumm, dann Summen
    tt = t_(d); x = np.zeros(len(tt))
    for k, st in enumerate((0.0, 0.12, 0.25, 0.37)):
        n = int(0.5 * SR); i = int(st * SR)
        x[i:i + n] += (np.sin(2 * np.pi * 70 * t_(0.5)) * np.exp(-t_(0.5) / 0.1) * 0.9 + hp(noise(0.5), 2500) * np.exp(-t_(0.5) / 0.004) * 0.8)
    x += sum(np.sin(2 * np.pi * 100 * n * tt) / n for n in range(1, 6)) * 0.08 * np.clip((tt - 0.4) * 2, 0, 1)
    return pan(reverb(x, 2.0, 0.45), 0.0)

def schluessel():
    d = 1.2; x = np.zeros(int(d * SR))
    for st, f in ((0.0, 3200), (0.25, 2600), (0.3, 2900)):
        n = int(0.06 * SR); c = (np.sin(2 * np.pi * f * t_(0.06)) * 0.6 + noise(0.06) * 0.5) * np.exp(-t_(0.06) / 0.006); i = int(st * SR); x[i:i + n] += c
    n = int(0.3 * SR); i = int(0.3 * SR); x[i:i + n] += np.sin(2 * np.pi * 120 * t_(0.3)) * np.exp(-t_(0.3) / 0.05) * 0.6
    return pan(reverb(x, 0.4, 0.15), 0.2)

def knall(d=7.0):
    # riesiger Überschlag: Explosion, Zischen, tiefes Grollen, abklingendes Knistern, dann Stille
    tt = t_(d); x = np.zeros(len(tt))
    boom = lp(noise(d), 300, 2) * np.exp(-tt / 0.6) * 2.4 + np.sin(2 * np.pi * 38 * tt) * np.exp(-tt / 0.9) * 1.6
    crack = hp(noise(d), 1000, 2) * np.exp(-tt / 0.08) * 2.2
    crk = grains(d, 260, 1500, 8000, (0.0005, 0.004), (0.2, 1.0)) * np.exp(-tt / 1.8)
    hum = sum(np.sin(2 * np.pi * 100 * n * tt) / n for n in range(1, 6)) * 0.25 * np.exp(-tt / 0.8) * np.linspace(1, 0.2, len(tt))
    return pan(reverb(boom + crack + crk + hum, 3.5, 0.5, 0.03), 0.0)

def stadt_an(d=8.0):
    # die Stadt erwacht: anschwellender Verkehr, ferne Hupen, Hunde, Jubel in der Ferne, Netzbrummen
    tt = t_(d); env = np.clip(tt / 3, 0, 1)
    city = lp(brown(d), 400, 4) * 0.8 * env + bp(pink(d), 200, 2000, 2) * 0.25 * env
    cheer = bp(noise(d), 300, 3000, 2) * (0.4 + 0.6 * smooth_rand(d, 1.5, 0, 1)) * np.clip((tt - 1.5) / 2, 0, 1) * 0.6
    horns = np.zeros(len(tt))
    for st, f in ((2.2, 392), (3.4, 466), (4.8, 349)):
        n = int(0.5 * SR); h = signal.square(2 * np.pi * f * t_(0.5)) * 0.4 * np.sin(np.pi * t_(0.5) / 0.5); i = int(st * SR); horns[i:i + n] += lp(h, 1500)
    hum = np.sin(2 * np.pi * 100 * tt) * 0.06 * np.clip(tt * 2, 0, 1)
    return fade(pan(reverb(city + cheer + horns + hum, 2.5, 0.6), -0.4), 0.5, 1.5)

TEIL5 = {'atmo_brummen.wav': (lambda: brummen(), 0.6), 'schritte_kies.wav': (schritte_kies, 0.8), 'funken.wav': (funken, 0.95), 'tor.wav': (tor, 0.8),
         'flutlicht.wav': (flutlicht, 0.85), 'schluessel.wav': (schluessel, 0.7), 'knall.wav': (knall, 0.98), 'stadt_an.wav': (stadt_an, 0.8)}


# ---------- Teil 6: Leitwarte ----------
def tastatur(d=10.0):
    x = np.zeros(int(d * SR)); s_ = 0.1
    while s_ < d - 0.2:
        n = int(0.04 * SR); tt = t_(0.04); f = R.uniform(1800, 3200)
        k = (bp(noise(0.04), 1500, 6000, 2) * np.exp(-tt / 0.004) + np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.003) * 0.3) * R.uniform(0.4, 1.0)
        i = int(s_ * SR); x[i:i + n] += k[:len(x) - i]; s_ += R.exponential(0.11) + 0.04 if R.random() > 0.08 else 0.6
    return pan(reverb(x, 0.5, 0.15), -0.2)

def luefter(d=60):
    tt = t_(d); ch = []
    for k in range(2):
        fan = bp(pink(d), 200, 3000, 2) * 0.5 + np.sin(2 * np.pi * (118 + k * 3) * tt) * 0.06 + np.sin(2 * np.pi * 236 * tt) * 0.03
        beeps = np.zeros(len(tt))
        for st in np.arange(5 + k * 7, d - 1, 17.3):
            n = int(0.08 * SR); i = int(st * SR); beeps[i:i + n] += np.sin(2 * np.pi * 1600 * t_(0.08)) * 0.08
        ch.append(fan + beeps)
    return loopable(stereo(*ch))

def fenster_klopfen(d=2.0):
    x = np.zeros(int(d * SR))
    for st in (0.0, 0.22, 0.44, 0.9, 1.1):
        n = int(0.25 * SR); tt = t_(0.25)
        hit = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / dk) * a for f, a, dk in ((240, 0.8, 0.05), (780, 0.5, 0.03), (1900, 0.3, 0.02))) + bp(noise(0.25), 500, 3000, 2) * np.exp(-tt / 0.006) * 0.8
        i = int(st * SR); x[i:i + n] += hit
    return pan(reverb(x, 0.9, 0.3), 0.0)

def glas_splitter(d=2.0):
    tt = t_(d); x = hp(noise(d), 2000, 2) * np.exp(-tt / 0.09) * 1.6 + bp(noise(d), 300, 2500, 2) * np.exp(-tt / 0.03) * 1.2 + np.sin(2 * np.pi * 90 * tt) * np.exp(-tt / 0.05) * 0.8
    x += grains(d, 500, 3000, 9000, (0.002, 0.012), (0.2, 0.8)) * np.exp(-tt / 0.35)
    for k in range(60):
        L = int(0.05 * SR); tk = np.arange(L) / SR; f = R.uniform(2500, 9000)
        c = np.sin(2 * np.pi * f * tk) * np.exp(-tk / R.uniform(0.005, 0.03)) * R.uniform(0.2, 0.8)
        i = int((R.exponential(0.12) + (0.25 if k > 40 else 0)) * SR); x[i:i + L] += c[:len(x) - i]
    return pan(reverb(x, 0.7, 0.25), 0.0)

def notaus_aus(d=6.0):
    # schwerer Schalter, dann fahren Lüfter und Netzbrummen herunter (Tonhöhe fällt), Relais klacken
    tt = t_(d); x = np.zeros(len(tt))
    n = int(0.6 * SR); x[:n] += np.sin(2 * np.pi * 55 * t_(0.6)) * np.exp(-t_(0.6) / 0.12) * 1.4 + hp(noise(0.6), 1500) * np.exp(-t_(0.6) / 0.01) * 0.8
    f = 600 * np.exp(-tt / 1.2) + 30; ph = 2 * np.pi * np.cumsum(f) / SR
    whine = (np.sin(ph) + 0.4 * np.sin(2 * ph)) * 0.25 * np.exp(-tt / 2.0)
    fans = bp(pink(d), 200, 3000, 2) * 0.5 * np.exp(-tt / 1.2)
    for st in (0.3, 0.45, 0.7, 1.1, 1.6):
        m = int(0.05 * SR); i = int(st * SR); x[i:i + m] += hp(noise(0.05), 2000) * np.exp(-t_(0.05) / 0.004) * 0.7
    return pan(reverb(x + whine + fans, 1.2, 0.3), 0.0)

def sirenen_nah(d=12.0):
    tt = t_(d); out = []
    for k, (f0, f1, rate, p) in enumerate(((650, 950, 0.55, -0.4), (700, 1000, 0.48, 0.4))):
        f = f0 + (f1 - f0) * (0.5 + 0.5 * signal.square(2 * np.pi * rate * tt + k))
        x = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * 0.3; x = lp(bp(x, 400, 3500, 2), 2600)
        near = np.clip(tt / 5, 0, 1) ** 1.5; out.append(pan(x * (0.2 + 0.8 * near), p))
    x = out[0] + out[1]
    car = (lp(brown(d), 200, 4) * 0.5 + bp(noise(d), 300, 1500, 2) * 0.15) * np.clip(tt / 5, 0, 1) * np.clip((8 - tt) / 2, 0.2, 1)
    y = x + stereo(car, car)
    return fade(stereo(reverb(y[:, 0], 1.8, 0.4), reverb(y[:, 1], 1.8, 0.4)), 0.5, 2.0)

TEIL6 = {'tastatur.wav': (tastatur, 0.7), 'atmo_luefter.wav': (lambda: luefter(), 0.55), 'fenster_klopfen.wav': (fenster_klopfen, 0.9), 'glas_splitter.wav': (glas_splitter, 0.9),
         'notaus_aus.wav': (notaus_aus, 0.95), 'sirenen_nah.wav': (sirenen_nah, 0.85)}


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ALL = {**TEIL2, **TEIL3, **TEIL4, **TEIL5, **TEIL6}
        for n_ in (TEIL2 if sys.argv[1] == 'teil2' else TEIL3 if sys.argv[1] == 'teil3' else TEIL4 if sys.argv[1] == 'teil4' else TEIL5 if sys.argv[1] == 'teil5' else TEIL6 if sys.argv[1] == 'teil6' else {k: ALL[k] for k in sys.argv[1:]}):
            f_, pk = ALL[n_]; save(n_, f_(), pk); print(' ', n_)
        sys.exit()
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
