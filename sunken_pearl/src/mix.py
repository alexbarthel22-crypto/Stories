"""Tonmischung: Erzählstimme + selbst synthetisierte Filmmusik + Freesound-Geräusche (CC0)."""
import numpy as np, subprocess, json, os
SR = 48000
DUR = 69.6
BASE = '/home/user/Stories/sunken_pearl/audio'
rng = np.random.default_rng(3)


def load(path, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if af: cmd += ['-af', af]
    cmd += ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2)
    return a.copy()


out = np.zeros((int(DUR * SR), 2), np.float32)
mus = np.zeros_like(out)


def place(buf, a, t, gain=1.0, fade_in=0.01, fade_out=0.05, length=None, loop=False):
    s = int(t * SR)
    if length is not None:
        n = int(length * SR)
        if loop and len(a) < n:
            a = np.tile(a, (n // len(a) + 1, 1))
        a = a[:n]
    a = a * gain
    n = len(a)
    fi, fo = max(1, int(fade_in * SR)), max(1, int(fade_out * SR))
    env = np.ones(n, np.float32)
    env[:fi] *= np.linspace(0, 1, min(fi, n))[:n] if fi <= n else np.linspace(0, 1, n)
    env[-fo:] *= np.linspace(1, 0, min(fo, n))
    a = a * env[:, None]
    e = min(len(buf), s + n)
    if e > s:
        buf[s:e] += a[:e - s]


def fs(k, af=None):
    a = load(f'{BASE}/fs/{k}.mp3', af)
    m = np.abs(a).mean(1)
    act = a[m > m.max() * 0.05]
    rms = np.sqrt((act ** 2).mean()) + 1e-9
    return a * (0.1 / rms)  # -20 dBFS RMS


# ---------------------------------------------------------------- Geräusche
place(out, fs('waves', 'lowpass=f=3000'), 0.0, 0.3, 0.3, 0.5, length=2.9)
place(out, fs('plunge'), 2.3, 0.8, 0.01, 0.6)
place(out, fs('bubbles', 'lowpass=f=2500'), 2.75, 0.4, 0.05, 1.0)
amb = fs('deepamb', 'lowpass=f=700,volume=2')
place(out, amb, 2.6, 0.12, 1.0, 1.0, length=11.9, loop=True)
place(out, fs('whoosh', 'asetrate=48000*0.6,aresample=48000,lowpass=f=1500'), 7.9, 0.7, 0.02, 0.5)
ch = fs('chime', 'aecho=0.8:0.6:180:0.3')
place(out, ch, 14.4, 0.35, 0.005, 0.6, length=1.2)
place(out, fs('clink'), 15.35, 0.5, 0.002, 0.5, length=1.2)
place(out, fs('shimmer'), 16.3, 0.35, 0.05, 0.6, length=1.4)
place(out, amb, 17.4, 0.08, 0.8, 0.8, length=4.1, loop=True)
place(out, fs('bubbles', 'lowpass=f=1800'), 17.5, 0.25, 0.5, 1.0, length=3.5)
pp = fs('paper', 'highpass=f=200')
place(out, pp, 22.1, 0.55, 0.01, 0.4, length=1.4)
place(out, pp, 24.2, 0.6, 0.01, 0.4, length=1.6)
place(out, pp, 27.5, 0.55, 0.01, 0.4, length=1.6)
place(out, ch, 31.8, 0.45, 0.005, 1.0, length=2.5)
place(out, fs('whoosh', 'asetrate=48000*0.8,aresample=48000'), 35.9, 0.55, 0.02, 0.5)
place(out, fs('shimmer'), 36.1, 0.5, 0.05, 0.8)
place(out, fs('plunge', 'lowpass=f=2000'), 38.0, 0.5, 0.05, 0.6)
place(out, fs('bubbles', 'lowpass=f=2000'), 38.1, 0.3, 0.05, 0.6, length=1.6)
place(out, fs('elev', 'lowpass=f=1200'), 39.7, 0.14, 0.3, 0.4, length=6.4, loop=True)
place(out, fs('ding', 'aecho=0.8:0.7:60|130:0.5|0.3'), 44.6, 0.7, 0.002, 1.0)
place(out, fs('doors'), 46.2, 0.7, 0.05, 1.0, length=2.0)
place(out, fs('reveal'), 47.6, 0.7, 0.02, 1.0)
place(out, fs('shimmer'), 50.8, 0.35, 0.3, 1.0)
place(out, fs('cave'), 47.8, 0.12, 1.5, 2.5, length=21.8, loop=True)
place(out, ch, 55.2, 0.3, 0.005, 1.0, length=2.0)
place(out, fs('riser', 'lowpass=f=6000'), 58.6, 0.3, 1.5, 0.2, length=2.8)
place(out, fs('harp'), 59.75, 0.55, 0.005, 1.0, length=3.0)
place(out, fs('reveal', 'asetrate=48000*0.85,aresample=48000'), 61.35, 0.8, 0.005, 1.5)
place(out, fs('shimmer'), 62.0, 0.5, 0.2, 2.0)
place(out, fs('boom', 'lowpass=f=300,volume=0.6'), 62.15, 0.5, 0.002, 1.5, length=2.0)
place(out, fs('harp', 'asetrate=48000*1.12,aresample=48000'), 64.1, 0.35, 0.005, 1.5)

# ---------------------------------------------------------------- Musik (synthetisch, magisch-elegant)
T = np.arange(len(out)) / SR


def env_lin(pts):
    xs, ys = zip(*pts)
    return np.interp(T, xs, ys).astype(np.float32)


try:
    import scipy  # noqa
except ImportError:
    subprocess.run(['pip', 'install', '-q', 'scipy'])


def lp(x, a):
    from scipy.signal import lfilter
    return lfilter([a], [1, a - 1], x).astype(np.float32)


def mf(m):
    return 440 * 2 ** ((m - 69) / 12)


def bell(f, dur=2.4, bright=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    return ((np.sin(2 * np.pi * f * tt) + 0.4 * bright * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 2)
             + 0.15 * bright * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt * 4)) * np.exp(-tt * 2.6)).astype(np.float32)


def pad_chord(ms, t0, t1, g, buf=None):
    buf = mus if buf is None else buf
    s, e = int(t0 * SR), int(min(t1, DUR) * SR)
    tt = T[s:e]
    w = np.zeros((e - s, 2), np.float32)
    for i, m in enumerate(ms):
        f = mf(m)
        for dt in (-0.0025, 0.0025):
            ph = 2 * np.pi * f * (1 + dt) * tt
            saw = 2 * ((f * (1 + dt) * tt) % 1.0) - 1
            w[:, (i + (dt > 0)) % 2] += (0.6 * np.sin(ph) + 0.25 * saw).astype(np.float32)
    w[:, 0] = lp(w[:, 0], 0.06); w[:, 1] = lp(w[:, 1], 0.06)
    n = e - s; a = int(min(0.8, (t1 - t0) / 3) * SR)
    env = np.ones(n, np.float32); env[:a] = np.linspace(0, 1, a); env[-a:] = np.linspace(1, 0, a)
    buf[s:e] += w * env[:, None] * g


def arp(seq, t0, t1, step, g, oct_=0, bright=1.0):
    t, k = t0, 0
    while t < t1:
        m = seq[k % len(seq)] + oct_
        b = bell(mf(m), 2.2, bright)
        pan = 0.5 + 0.35 * np.sin(k * 1.3)
        place(mus, np.stack([b * (1 - pan), b * pan], 1), t, g, 0.002, 0.3)
        k += 1; t += step


# Akte: D-Dur Luxus (2.5–21.5) | d-Moll Geheimnis (21.5–35.8) | Aufbruch (35.8–46.1) | Perlmutt-Saal (46.1–64) | Ende
prog1 = [([50, 57, 62, 66, 69], 0), ([47, 54, 59, 62, 66], 1), ([43, 55, 59, 62, 67], 0), ([45, 57, 61, 64, 69], 1)]
t = 2.5
i = 0
while t < 21.5:
    ch_, _ = prog1[i % 4]
    pad_chord(ch_, t, t + 4.6, 0.05)
    t += 4.0; i += 1
arp([74, 78, 81, 86, 81, 78, 76, 79, 83, 86, 83, 79], 2.6, 21.3, 0.3, 0.07)
prog2 = [[50, 57, 62, 65, 69], [46, 53, 58, 62, 65], [48, 55, 60, 64, 67], [45, 52, 57, 61, 64]]
t = 21.5; i = 0
while t < 35.8:
    pad_chord(prog2[i % 4], t, min(t + 3.9, 35.9), 0.055)
    t += 3.6; i += 1
arp([62, 65, 69, 74, 72, 69, 65, 64], 21.6, 32.6, 0.36, 0.06, 12)
# Pizzicato-Puls ab Umschlag
t = 24.1
while t < 46.0:
    bpm = 70 + max(0, t - 35.8) / 10 * 60
    n = int(0.4 * SR); tt = np.arange(n) / SR
    f0 = 60 * np.exp(-tt * 12) + 42
    kick = np.sin(2 * np.pi * np.cumsum(f0) / SR) * np.exp(-tt * 9)
    g = 0.18 + 0.3 * max(0, t - 35.8) / 10
    place(mus, np.stack([kick, kick], 1).astype(np.float32), t, g, 0.001, 0.1)
    t += 60 / bpm
# Pause nach "zweihundert Etagen" (Spannung), dann Aufbruch in G-Dur/D
pad_chord([55, 62, 67, 71, 74], 35.8, 40.0, 0.06)
pad_chord([57, 64, 69, 73, 76], 40.0, 44.6, 0.065)
arp([79, 83, 86, 91, 86, 83], 35.9, 44.5, 0.2, 0.05)
pad_chord([50, 57, 62, 66, 69, 74], 44.6, 47.0, 0.08)
# Saal: großes Fis-Moll->D-Dur Schimmern
for (ms, a, b_) in [([50, 57, 62, 66, 69, 74], 46.1, 51.5), ([47, 54, 59, 62, 66, 71], 51.0, 55.5),
                    ([43, 50, 55, 59, 62, 67], 55.0, 59.8), ([45, 52, 57, 61, 64, 69], 59.5, 61.6),
                    ([50, 57, 62, 66, 69, 74, 78], 61.3, 64.2), ([43, 50, 55, 59, 62, 69], 64.0, 69.6)]:
    pad_chord(ms, a, b_, 0.07)
arp([86, 90, 93, 98, 93, 90], 47.9, 61.0, 0.24, 0.04)
arp([74, 78, 81, 86, 90, 93, 98, 102], 61.35, 62.6, 0.08, 0.06)
arp([86, 81, 79, 74], 64.2, 66.0, 0.45, 0.05)
# ---------------------------------------------------------------- Stimme + Ducking
vo = load(f'{BASE}/vo_otto.mp3', 'highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.6')
voice = np.zeros_like(out)
place(voice, vo, 0.05, 1.0, 0.001, 0.05)
lvl = np.abs(voice).mean(1)
win = int(0.25 * SR)
sm = np.convolve(lvl, np.ones(win) / win, 'same')
duck = 1 - 0.5 * np.clip(sm / (sm.max() * 0.25 + 1e-9), 0, 1)
mix = voice + (out * 0.3 + mus * 0.0) * duck[:, None]
peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.3) * 0.89
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-',
                '-af', 'loudnorm=I=-12:TP=-1.0:LRA=7', '-ar', '48000', f'{BASE}/final_mix.wav'],
               input=mix.astype(np.float32).tobytes(), check=True)
print('mix ok', mix.shape[0] / SR)
if os.environ.get('DBG'):
    bed = (out * 0.3 + mus * 0.0) * duck[:, None]
    for i in range(0, int(DUR), 3):
        s, e = i * SR, (i + 3) * SR
        rv = 20 * np.log10(np.sqrt((voice[s:e] ** 2).mean()) + 1e-9); rb = 20 * np.log10(np.sqrt((bed[s:e] ** 2).mean()) + 1e-9)
        ro = 20 * np.log10(np.sqrt((out[s:e] ** 2).mean()) + 1e-9); rm = 20 * np.log10(np.sqrt((mus[s:e] ** 2).mean()) + 1e-9)
        print(f'{i:2d}s voice {rv:6.1f} bed {rb:6.1f} (sfx {ro:6.1f} mus {rm:6.1f})')
