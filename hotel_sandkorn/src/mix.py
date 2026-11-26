"""Ton: Stimme (mit Denkpause) + Geräusche, ohne Musik."""
import subprocess, numpy as np, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hotel as h
SR = 48000
ROOT = h.ROOT


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


N = int(h.END * SR) + SR
out = np.zeros((N, 2), np.float32)
fs = {k: load(f'{ROOT}/audio/fs/{k}.mp3') for k in ['pop', 'swoosh', 'waves', 'gull', 'boom', 'tada', 'click']}


def db(x):
    return 10 ** (x / 20)


def put(name, t, g=0.0):
    s = fs[name].copy()
    s *= 0.8 / max(1e-6, float(np.abs(s).max()))
    f = int(0.004 * SR)
    s[:f] *= np.linspace(0, 1, f)[:, None]
    s[-f:] *= np.linspace(1, 0, f)[:, None]
    i = int(t * SR)
    n = min(len(s), N - i)
    if n > 0 and i >= 0:
        out[i:i + n] += s[:n] * db(g)


def bed(name, a, b, g, fade=0.6):
    s = fs[name]
    L = int((b - a) * SR)
    lp = np.concatenate([s] * (L // len(s) + 2))[:L].copy()
    f = int(fade * SR)
    r = np.linspace(0, 1, f)[:, None]
    lp[:f] *= r
    lp[-f:] *= r[::-1]
    out[int(a * SR):int(a * SR) + L] += lp * db(g)


TW, nw = h.TW, h.nw
put('boom', 0.0, -5)
for s_ in h.SC[1:]:
    put('swoosh', s_[1] - 0.1, -11)
for t in [nw('ausgebucht'), nw('und', 0), nw('unendlich', 0), nw('shelly', 0) + 0.05, nw('viele', 1) - 0.1, nw('sandkörner'),
          nw('unendlich', 1), nw('eins'), nw('zwei'), nw('drei'), nw('ende'), nw('belegt'), nw('fähre'), nw('unendlich', 2),
          nw('eins', 1) - 0.1, nw('niemand') - 0.1, nw('nur', 0, after=nw('shelly', 1)), nw('welche') - 0.05, nw('schreibe'),
          TW('hier'), TW('jeder') - 0.1, TW('geraden') - 0.2, TW('frei') - 0.3, TW('ausgebucht', 1) - 0.1, TW('hilbert') - 0.2,
          TW('was', 0, after=nw('hilbert')) - 0.1, TW('wohnst'), TW('muscheltal'), TW('hütte') - 0.2, TW('folge')]:
    put('pop', t, -9)
for t in [TW('geht') - 0.4, TW('vier') - 0.5, TW('sechs') - 0.5]:
    put('swoosh', t, -14)
put('tada', TW('frei') - 0.2, -12)
bed('waves', 0, h.END, -24, 1.0)
bed('gull', h.SC[5][1], h.SC[6][1], -26)

vo = load(f'{ROOT}/audio/vo.wav')
voice = np.zeros_like(out)
ga = int(h.GAP_AT * SR)
voice[:ga] = vo[:ga]
gi = int(h.gn(h.GAP_AT) * SR)
rest = vo[ga:]
voice[gi:gi + len(rest)] = rest[:N - gi]
mix = (voice * db(5) + out)[:int(h.END * SR)]
tmp = f'{ROOT}/audio/mix_raw.wav'
with wave.open(tmp, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af',
                'acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=4,alimiter=limit=0.9:level=false,loudnorm=I=-9:TP=-0.8:LRA=6,afade=t=out:st=%.2f:d=0.6' % (h.END - 0.6),
                '-ar', str(SR), f'{ROOT}/audio/final_mix.wav'], check=True)
os.remove(tmp)
print('ok', h.END)
