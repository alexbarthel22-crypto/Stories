"""Tonmischung: Erzählstimme + selbst synthetisierte Filmmusik + Freesound-Geräusche (CC0)."""
import numpy as np, subprocess, json, os
SR = 48000
DUR = 52.4
BASE = '/home/user/Stories/sunken_pearl_raetsel/audio'
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
    return a * (0.1 / rms)  # -20 dBF# ---------------------------------------------------------------- Geräusche (keine Musik)
waves = fs('waves', 'lowpass=f=3500')
place(out, waves, 0.0, 0.35, 0.4, 0.4, length=5.1, loop=True)
place(out, fs('whoosh', 'lowpass=f=2500'), 1.6, 0.6, 0.05, 0.6)
place(out, fs('plunge'), 4.9, 0.7, 0.01, 0.6)
place(out, fs('bubbles', 'lowpass=f=2500'), 5.3, 0.4, 0.05, 1.0, length=3.0)
place(out, fs('chime', 'aecho=0.8:0.6:180:0.3'), 8.55, 0.3, 0.005, 0.6, length=1.4)
heels = fs('heels')
place(out, heels, 10.5, 0.3, 0.05, 0.3, length=2.7, loop=True)
place(out, waves, 13.25, 0.25, 0.2, 0.3, length=3.1, loop=True)
place(out, fs('train', 'lowpass=f=2200,volume=1.2'), 13.3, 0.45, 0.2, 0.6, length=2.9)
place(out, fs('doors'), 16.0, 0.35, 0.02, 0.3, length=0.4)
elev = fs('elev', 'lowpass=f=900')
place(out, elev, 16.35, 0.45, 0.2, 0.3, length=4.25, loop=True)
place(out, fs('ding'), 20.3, 0.5, 0.002, 0.5)
rainsfx = fs('rain', 'volume=1.0')
place(out, rainsfx, 20.6, 0.8, 0.05, 0.3, length=1.85, loop=True)
place(out, elev, 22.45, 0.45, 0.2, 0.3, length=3.6, loop=True)
place(out, fs('ding'), 25.95, 0.5, 0.002, 0.5)
place(out, fs('doors'), 26.2, 0.4, 0.02, 0.3)
place(out, heels, 26.8, 0.4, 0.1, 0.3, length=4.5, loop=True)
place(out, fs('whoosh'), 31.25, 0.5, 0.01, 0.4)
place(out, fs('chime'), 31.4, 0.3, 0.005, 0.5, length=1.2)
place(out, fs('clock'), 34.7, 0.7, 0.05, 0.1, length=3.4, loop=True)
place(out, fs('reveal'), 38.05, 0.5, 0.01, 1.0, length=3.0)
click = fs('click')
place(out, click, 42.05, 0.8, 0.001, 0.05)
place(out, fs('ding'), 42.12, 0.35, 0.002, 0.5)
place(out, click, 47.85, 0.9, 0.001, 0.05)
place(out, fs('ding'), 47.92, 0.6, 0.002, 0.8)
place(out, fs('tada'), 48.3, 0.3, 0.01, 0.8)
place(out, rainsfx, 49.6, 0.7, 0.1, 0.8, length=2.8, loop=True)
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
