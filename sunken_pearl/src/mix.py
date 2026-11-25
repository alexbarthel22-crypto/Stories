"""Tonmischung: Erzählstimme + selbst synthetisierte Filmmusik + Freesound-Geräusche (CC0)."""
import numpy as np, subprocess, json, os
SR = 48000
DUR = 70.6
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
place(out, fs('plunge'), 2.35, 0.9, 0.01, 0.6)
place(out, fs('bubbles', 'lowpass=f=2500'), 2.8, 0.45, 0.05, 1.0)
amb = fs('deepamb', 'lowpass=f=700,volume=2')
place(out, amb, 2.6, 0.14, 1.0, 1.5, length=45.6, loop=True)
place(out, fs('whoosh', 'asetrate=48000*0.55,aresample=48000,lowpass=f=1200'), 7.85, 0.9, 0.02, 0.5)
place(out, fs('sonar', 'aecho=0.8:0.7:400|900:0.4|0.25'), 9.6, 0.35, 0.01, 1.0)
place(out, fs('sonar', 'aecho=0.8:0.7:400|900:0.4|0.25,lowpass=f=1500'), 12.4, 0.22, 0.01, 1.0)
place(out, fs('clock'), 18.3, 0.75, 0.05, 0.3, length=3.3)
kn = fs('knock', 'lowpass=f=2200,asetrate=48000*0.7,aresample=48000,aecho=0.8:0.6:120:0.3')
for t in (20.5, 20.78, 21.06):
    place(out, kn, t, 1.4, 0.002, 0.3, length=0.9)
place(out, kn, 23.35, 1.6, 0.002, 0.5, length=1.0)
gr = fs('groan', 'asetrate=48000*0.35,aresample=48000,lowpass=f=900,volume=2')
place(out, gr, 24.4, 0.8, 0.3, 1.0)
place(out, gr, 27.6, 0.6, 0.3, 1.0)
place(out, fs('heart', 'lowpass=f=300'), 24.3, 0.3, 1.0, 1.0, length=10.0, loop=True)
place(out, fs('flicker'), 28.6, 0.8, 0.01, 0.4, length=2.2)
place(out, fs('hiss', 'highpass=f=300'), 30.45, 0.45, 0.2, 0.5, length=2.0)
place(out, gr, 30.5, 0.7, 0.1, 0.8, length=2.0)
cr = fs('crack')
place(out, cr, 32.3, 1.2, 0.002, 0.3)
place(out, fs('crack', 'asetrate=48000*0.8,aresample=48000'), 32.75, 1.0, 0.002, 0.3)
place(out, fs('crack', 'asetrate=48000*0.65,aresample=48000'), 33.35, 0.8, 0.002, 0.3)
place(out, fs('drip', 'aecho=0.8:0.6:200:0.3'), 33.6, 0.5, 0.05, 0.5, length=3.0)
al = fs('alarm', 'lowpass=f=2500')
place(out, al, 32.6, 0.12, 0.5, 0.2, length=2.0, loop=True)
place(out, al, 34.6, 0.2, 0.05, 1.5, length=4.6, loop=True)
place(out, fs('run'), 34.6, 0.9, 0.05, 0.2, length=1.95, loop=True)
place(out, fs('elev', 'lowpass=f=1200'), 36.5, 0.16, 0.3, 0.6, length=11.7, loop=True)
place(out, fs('ding', 'asetrate=48000*0.84,aresample=48000,aecho=0.8:0.7:60|130:0.5|0.3'), 44.25, 0.8, 0.002, 1.0)
place(out, fs('doors'), 48.05, 0.9, 0.05, 1.0, length=2.5)
place(out, fs('whoosh', 'asetrate=48000*0.45,aresample=48000,lowpass=f=900'), 49.0, 0.8, 0.05, 0.8)
place(out, fs('cave'), 48.9, 0.2, 1.5, 2.5, length=21.7, loop=True)
br = fs('breath', 'asetrate=48000*0.45,aresample=48000,lowpass=f=700,aecho=0.8:0.7:300:0.3,volume=2')
place(out, br, 53.9, 0.7, 0.5, 1.5, length=6.5)
bm = fs('boom', 'lowpass=f=500,aecho=0.8:0.7:250|600:0.5|0.3,volume=1.5')
for t in (61.15, 61.55, 62.3):
    place(out, bm, t - 0.05, 1.1, 0.002, 1.2, length=1.6)
place(out, fs('growl', 'asetrate=48000*0.5,aresample=48000,lowpass=f=900,volume=1.5'), 63.6, 0.75, 0.2, 1.5)
place(out, fs('riser', 'lowpass=f=6000'), 54.4, 0.35, 2.0, 0.2)
place(out, fs('sting', 'lowpass=f=8000'), 64.45, 0.8, 0.002, 2.5)

# ---------------------------------------------------------------- Musik (synthetisch)
T = np.arange(len(out)) / SR


def env_lin(pts):
    xs, ys = zip(*pts)
    return np.interp(T, xs, ys).astype(np.float32)


def lp(x, a):
    """Einfacher 1-Pol-Tiefpass (a: 0..1, klein = dunkler)."""
    from scipy.signal import lfilter
    return lfilter([a], [1, a - 1], x).astype(np.float32)


try:
    import scipy  # noqa
except ImportError:
    subprocess.run(['pip', 'install', '-q', 'scipy'])

# Drone D1/A1 mit Sägezahn, gefiltert, langsame Schwebung
d = np.zeros(len(T), np.float32)
for f, g in ((36.71, 0.5), (36.9, 0.4), (55.0, 0.35), (73.42, 0.2)):
    ph = (f * T) % 1.0
    d += g * (2 * ph - 1)
d = lp(d, 0.02) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * T))
drone_env = env_lin([(0, 0.0), (2.6, 0.0), (4.0, 0.5), (18.0, 0.55), (24, 0.8), (36, 1.0), (48.0, 1.1), (48.3, 0.0),
                     (49.5, 0.0), (52, 0.5), (64.4, 0.8), (64.5, 1.3), (70.6, 0.0)])
mus[:, 0] += d * drone_env * 0.5
mus[:, 1] += d * drone_env * 0.5

# Spieluhr-Arpeggio (D-Moll) 2.6 – 18.4: geheimnisvoll
notes = [62, 65, 69, 74, 72, 69, 65, 64, 62, 65, 69, 76, 74, 69, 65, 61]
t0, step = 2.9, 0.38
k = 0
t = t0
while t < 18.2:
    m = notes[k % len(notes)] + (12 if (k // 16) % 2 else 0)
    f = 440 * 2 ** ((m - 69) / 12)
    n = int(2.2 * SR)
    tt = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.01 * tt) + 0.12 * np.sin(2 * np.pi * f * 4.2 * tt)) * np.exp(-tt * 3.2)
    pan = 0.5 + 0.35 * np.sin(k * 1.3)
    g = 0.11 * (1 - 0.6 * max(0, (t - 15.5) / 3))
    st = np.stack([tone * (1 - pan), tone * pan], 1).astype(np.float32)
    place(mus, st, t, g, 0.002, 0.3)
    k += 1; t += step
# Hall auf Spieluhr: einfache Echos
# Puls (Herzschlag-Bass) beschleunigend 21 – 48
t = 21.0
while t < 48.0:
    bpm = 62 + (t - 21) / 27 * 70
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f0 = 55 * np.exp(-tt * 10) + 38
    kick = np.sin(2 * np.pi * np.cumsum(f0) / SR) * np.exp(-tt * 7)
    g = 0.35 + 0.35 * (t - 21) / 27
    place(mus, np.stack([kick, kick], 1).astype(np.float32), t, g, 0.001, 0.1)
    place(mus, np.stack([kick, kick], 1).astype(np.float32), t + 60 / bpm * 0.32, g * 0.55, 0.001, 0.1)
    t += 60 / bpm
# Streicher-Dissonanz (Cluster) 28 – 48, steigend
cl = np.zeros(len(T), np.float32)
for f in (293.66, 311.13, 440.0, 466.16):
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * T + f)
    ph = np.cumsum(f * vib) / SR
    cl += ((2 * (ph % 1.0) - 1)).astype(np.float32)
cl = lp(cl, 0.08)
cl_env = env_lin([(0, 0), (28.5, 0), (34, 0.25), (42.8, 0.35), (44.3, 0.6), (48.0, 0.7), (48.25, 0.0), (70.6, 0)])
mus[:, 0] += cl * cl_env * 0.08
mus[:, 1] += np.roll(cl, 200) * cl_env * 0.08
# Sphärisches Pad 49.9 – 70 (Perle): D-Dur-ish mit hohen Sinus-Schimmern
pad = np.zeros((len(T), 2), np.float32)
for i, f in enumerate((146.83, 220.0, 293.66, 369.99, 440.0, 587.33, 880.0, 1174.66)):
    ph = 2 * np.pi * f * T + 0.3 * np.sin(2 * np.pi * (0.1 + i * 0.03) * T)
    w = np.sin(ph) * (0.6 if f < 600 else 0.25)
    pad[:, i % 2] += w.astype(np.float32)
pad_env = env_lin([(0, 0), (49.6, 0), (52.5, 0.09), (60.5, 0.11), (63.4, 0.06), (64.4, 0.0), (70.6, 0)])
mus += pad * pad_env[:, None]
# Moll-Pad-Ende nach dem Auge
endp = np.zeros((len(T), 2), np.float32)
for i, f in enumerate((73.42, 87.31, 110.0, 155.56, 207.65)):
    endp[:, i % 2] += np.sin(2 * np.pi * f * T).astype(np.float32)
end_env = env_lin([(0, 0), (64.4, 0), (64.6, 0.12), (68.5, 0.09), (70.6, 0)])
mus += endp * end_env[:, None]

# ---------------------------------------------------------------- Stimme + Ducking
vo = load(f'{BASE}/vo_otto.mp3', 'highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.6')
voice = np.zeros_like(out)
place(voice, vo, 0.05, 1.0, 0.001, 0.05)
lvl = np.abs(voice).mean(1)
win = int(0.25 * SR)
sm = np.convolve(lvl, np.ones(win) / win, 'same')
duck = 1 - 0.5 * np.clip(sm / (sm.max() * 0.25 + 1e-9), 0, 1)
mix = voice + (out * 0.42 + mus * 0.13) * duck[:, None]
peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.3) * 0.89
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-',
                '-af', 'loudnorm=I=-14:TP=-1.0:LRA=9', '-ar', '48000', f'{BASE}/final_mix.wav'],
               input=mix.astype(np.float32).tobytes(), check=True)
print('mix ok', mix.shape[0] / SR)
if os.environ.get('DBG'):
    bed = (out * 0.42 + mus * 0.13) * duck[:, None]
    for i in range(0, int(DUR), 3):
        s, e = i * SR, (i + 3) * SR
        rv = 20 * np.log10(np.sqrt((voice[s:e] ** 2).mean()) + 1e-9); rb = 20 * np.log10(np.sqrt((bed[s:e] ** 2).mean()) + 1e-9)
        ro = 20 * np.log10(np.sqrt((out[s:e] ** 2).mean()) + 1e-9); rm = 20 * np.log10(np.sqrt((mus[s:e] ** 2).mean()) + 1e-9)
        print(f'{i:2d}s voice {rv:6.1f} bed {rb:6.1f} (sfx {ro:6.1f} mus {rm:6.1f})')
