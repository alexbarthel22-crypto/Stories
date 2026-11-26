"""Ton: Stimme + Geräusche (ohne Musik)."""
import subprocess, numpy as np, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pm
SR = 48000
ROOT = pm.ROOT


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


N = int(pm.END * SR) + SR
out = np.zeros((N, 2), np.float32)
fs = {k: load(f'{ROOT}/audio/fs/{k}.mp3') for k in ['pop', 'swoosh', 'click', 'ding', 'waves', 'gull', 'boom', 'tada']}


def db(x):
    return 10 ** (x / 20)


def put(name, t, g=0.0, dur=None):
    s = fs[name]
    s = s[:int(dur * SR)] if dur else s
    i = int(t * SR)
    n = min(len(s), N - i)
    if n > 0 and i >= 0:
        out[i:i + n] += s[:n] * db(g)


def bed(name, a, b, g, fade=0.4):
    s = fs[name]
    L = int((b - a) * SR)
    lp = np.concatenate([s] * (L // len(s) + 2))[:L].copy()
    f = int(fade * SR)
    r = np.linspace(0, 1, f)[:, None]
    lp[:f] *= r
    lp[-f:] *= r[::-1]
    out[int(a * SR):int(a * SR) + L] += lp * db(g)


TW = pm.TW
put('boom', pm.TW('ein', 0) - 0.12, -6)
for c in pm.CH[1:]:
    put('swoosh', c[1] - 0.1, -10)
    put('pop', c[1] + 0.12, -10)
for t in [TW('ausgewählt'), TW('lieblings') + 0.5, TW('stunde') - 0.1, TW('hasse') - 0.2, TW('ich', 2), TW('muschel', 1),
          TW('ich', 3) - 0.1, TW('gegessen'), TW('ich', 4) - 0.1, TW('mädchen', 2) - 0.1, TW('zuschauen'), TW('sagt', 1) - 0.1,
          TW('kennst'), TW('markier'), TW('was')]:
    put('pop', t, -9)
for t in [TW('du', 0) - 0.15, TW('weiss') - 0.15, TW('ich', 6) - 0.15]:
    put('click', t, -8)
_n = TW('nervigsten')
for t in [TW('sie', 0, after=_n), TW('sie', 1, after=_n), TW('sie', 2, after=_n), TW('braucht') - 0.3]:
    put('ding', t - 0.05, -14)
bed('waves', 0, pm.END, -26, 1.0)
bed('gull', pm.CH[3][1], pm.CH[4][1], -24)
bed('gull', pm.CH[6][1], pm.CH[7][1], -26)

vo = load(f'{ROOT}/audio/vo.wav')
voice = np.zeros_like(out)
voice[:len(vo)] = vo[:N]
mix = (voice * db(5) + out)[:int(pm.END * SR)]
tmp = f'{ROOT}/audio/mix_raw.wav'
with wave.open(tmp, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af',
                'acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=4,alimiter=limit=0.9:level=false,loudnorm=I=-9:TP=-0.8:LRA=6',
                '-ar', str(SR), f'{ROOT}/audio/final_mix.wav'], check=True)
os.remove(tmp)
print('ok', pm.END)
