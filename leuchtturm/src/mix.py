"""Ton: Stimme (mit Denkpause) + Geräusche, ohne Musik."""
import subprocess, numpy as np, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lt as h
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
for t in [nw('hundertzwanzig') - 0.2, nw('neunzig') - 0.2, nw('niemand') - 0.2, nw('trotzdem') - 0.1, nw('meerhexe') - 0.1,
          nw('tür') - 0.2, nw('heute') - 0.15, nw('morgen') - 0.1, nw('schau') - 0.05, nw('eisenring') - 0.2, nw('eisenring', 1) - 0.2,
          nw('seil', 1) - 0.2, nw('schere') - 0.2, nw('erste') - 0.05, nw('aber', 1) - 0.1, nw('zweite') - 0.05, nw('fehlen') - 0.2,
          nw('bei') - 0.05, nw('wie') - 0.1, nw('schreibt') - 0.1, TW('hier'), TW('schneidet') - 0.2, TW('kurzes') - 0.1,
          TW('langes') - 0.1, TW('genau') - 0.2, TW('hände') - 0.2, TW('frei') - 0.2, TW('hättest') - 0.05, TW('muscheltal') - 0.5,
          TW('folge') - 0.05, TW('hütte') - 0.2]:
    put('pop', t, -9)
put('whoosh', nw('heute') - 0.2, -10)
put('click', TW('schneidet') - 0.1, -4)
put('swoosh', TW('zieht'), -8)
put('tada', TW('frei') - 0.2, -12)
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
