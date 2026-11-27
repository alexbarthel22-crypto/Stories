"""Ton: Stimme (mit Denkpause) + Geräusche, ohne Musik."""
import subprocess, numpy as np, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hats as h
SR = 48000
ROOT = h.ROOT


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


N = int(h.END * SR) + SR
out = np.zeros((N, 2), np.float32)
fs = {k: load(f'{ROOT}/audio/fs/{k}.mp3') for k in ['pop', 'swoosh', 'click', 'ding', 'whoosh', 'waves', 'gull', 'tada']}


def bed(name, a, b, g, fade=0.6):
    s = fs[name]
    L = int((b - a) * SR)
    lp = np.concatenate([s] * (L // len(s) + 2))[:L].copy()
    f = int(fade * SR)
    r = np.linspace(0, 1, f)[:, None]
    lp[:f] *= r
    lp[-f:] *= r[::-1]
    out[int(a * SR):int(a * SR) + L] += lp * db(g)


def db(x):
    return 10 ** (x / 20)


def put(name, t, g=0.0, rev=False):
    s = fs[name].copy()
    if rev:
        s = s[::-1].copy()
    s *= 0.8 / max(1e-6, float(np.abs(s).max()))
    f = int(0.004 * SR)
    s[:f] *= np.linspace(0, 1, f)[:, None]
    s[-f:] *= np.linspace(1, 0, f)[:, None]
    i = int(t * SR)
    n = min(len(s), N - i)
    if n > 0 and i >= 0:
        out[i:i + n] += s[:n] * db(g)


nw, TW = h.nw, h.TW
for s_ in h.SC[1:]:
    put('swoosh', s_[1] - 0.1, -12)
for t in [0.05, nw('wer') - 0.1, h.SC[1][1] + 0.05, nw('dahinter') - 0.1, nw('gibt') - 0.1, nw('gibt') + 0.5, h.SC[2][1] + 0.05,
          nw('rosa', 1) - 0.2, nw('blau', 1) - 0.2, nw('sieht', 1) - 0.2, nw('sieht', 2) - 0.2, nw('sieht', 3) - 0.2,
          TW('umdrehen') - 0.1, TW('bewegen') - 0.1, TW('zeichen') - 0.1, nw('nur', 1) - 0.1, h.SC[4][1] + 0.05, nw('schreibt') - 0.1,
          TW('hier'), TW('shelly', 0, after=nw('lösung')) - 0.1, TW('bleibt') - 0.1, TW('während') - 0.1, TW('aber', 0, after=nw('während')) - 0.1,
          TW('schweigt') - 0.2, TW('verschieden') - 0.3, TW('hast') - 0.05, TW('wohnst') - 0.05, TW('folge') - 0.05, TW('hütte') - 0.2]:
    put('pop', t, -9)
put('whoosh', TW('verboten') - 0.1, -12)
put('tada', TW('rosa', 0, after=nw('meiner', 1) - 0.5) - 0.2, -12)
for i in range(6):
    put('click', h.GAP_AT + 0.3 + i * 0.3, -16)
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
