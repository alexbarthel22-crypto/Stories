"""Ton: Stimme (mit Denkpause) + Geräusche, ohne Musik."""
import subprocess, numpy as np, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe as h
SR = 48000
ROOT = h.ROOT


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


N = int(h.END * SR) + SR
out = np.zeros((N, 2), np.float32)
fs = {k: load(f'{ROOT}/audio/fs/{k}.mp3') for k in ['pop', 'swoosh', 'click', 'ding', 'heels', 'doors', 'whoosh']}


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
for t in [nw('sandkorn') - 0.1, nw('zimmersafe') - 0.2, nw('nie') - 0.1, h.SC[2][1] + 0.1, nw('ritual') - 0.2, nw('bett') - 0.2,
          h.SC[4][1] + 0.1, nw('seltsam') - 0.2, nw('rätselhafter') - 0.3, h.SC[6][1] + 0.05, nw('nur', 0, after=h.SC[6][1]) - 0.1,
          h.SC[7][1] + 0.05, nw('schreib') - 0.05, h.GAP_AT + 0.05, TW('hier'), TW('muschelpass') - 0.2, TW('vergesslich') - 0.2,
          TW('beide') - 0.1, TW('öffnen') - 0.6, TW('hast'), TW('wohnst') - 0.05, TW('folge') - 0.05, TW('hütte') - 0.2]:
    put('pop', t, -9)
# Safe: zu / auf
for t in [nw('zimmersafe') + 0.6, nw('ab', 0, after=nw('schliesst', 1) - 0.1) - 0.1, TW('safe', 1) + 0.5]:
    put('click', t, -6)
    put('ding', t + 0.08, -18)
for t in [h.SC[4][1] + 0.3, TW('öffnen') - 0.6]:
    put('click', t, -6)
put('whoosh', TW('flugbegl') - 0.25, -8)
put('swoosh', h.SC[12][1], -6, rev=True)
put('click', TW('nimmt') + 0.85, -8)
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
