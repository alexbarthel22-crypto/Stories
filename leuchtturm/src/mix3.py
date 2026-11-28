"""Ton für die Rapunzel-Fassung: Stimme (mit Denkpause) + Gewitter, Hexe, Effekte – ohne Musik."""
import subprocess, numpy as np, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lt3 as h
SR = 48000
ROOT = h.ROOT
G = h.G


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def db(x):
    return 10 ** (x / 20)


N = int(h.END * SR) + SR
out = np.zeros((N, 2), np.float32)
fs = {k: load(f'{ROOT}/audio/fs/{k}.mp3') for k in
      ['pop', 'swoosh', 'click', 'whoosh', 'waves', 'gull', 'tada', 'thunder', 'cackle', 'cackle2', 'wind', 'rain', 'boom']}
for k in fs:
    fs[k] *= 0.8 / max(1e-6, float(np.abs(fs[k]).max()))


def put(name, t, g=0.0, maxlen=None):
    s = fs[name].copy()
    if maxlen:
        s = s[:int(maxlen * SR)]
    f = min(int(0.01 * SR), len(s) // 4)
    s[:f] *= np.linspace(0, 1, f)[:, None]
    s[-f * 8:] *= np.linspace(1, 0, f * 8)[:, None]
    i = int(t * SR)
    n = min(len(s), N - i)
    if n > 0 and i >= 0:
        out[i:i + n] += s[:n] * db(g)


def bed(name, a, b, g, fade=0.8):
    s = fs[name]
    L = int((b - a) * SR)
    lp = np.concatenate([s] * (L // len(s) + 2))[:L].copy()
    f = int(fade * SR)
    r = np.linspace(0, 1, f)[:, None]
    lp[:f] *= r
    lp[-f:] *= r[::-1]
    out[int(a * SR):int(a * SR) + L] += lp * db(g)


# Atmosphäre
bed('rain', 0.0, 56.9, -25)
bed('wind', 0.0, 56.9, -27)
bed('rain', G(66.15), G(104.3), -27)
bed('waves', 56.9, G(66.15), -24)
bed('waves', G(104.3), h.END, -24)
put('gull', 57.3, -18)
put('gull', G(105.0), -18)
for t in h.FLASHES:
    put('thunder', t, -10 if t > 1 else -4, maxlen=6)
put('boom', 0.05, -10)
# Szenenwechsel
for s_ in h.SC[1:]:
    put('swoosh', s_[0] - 0.1, -13)
# Hexe
put('cackle', 12.3, -7)
put('whoosh', 11.9, -8)
put('cackle2', 17.2, -12)
put('whoosh', 19.3, -9)
put('cackle', G(98.6), -9)
put('cackle2', G(105.6), -7)
# Effekte
for t in [0.15, 3.3, 5.4, 7.3, 8.78, 14.0, 15.7, 20.86, 24.75, 26.6, 28.2, 30.1, 31.4, 32.3, 35.9, 36.55, 41.3, 44.2, 45.65, 51.7,
          54.0, 57.0, 59.8, 61.6, 63.1, G(66.2), G(70.48), G(72.18), G(73.3), G(76.2), G(77.8), G(82.4), G(85.0), G(86.5), G(88.94),
          G(92.1), G(96.5), G(100.4), G(105.28), G(107.86), G(111.08), G(112.9), G(114.98), G(116.0)]:
    put('pop', t, -10)
put('whoosh', 5.4, -9)
for t in (35.9, 38.0, G(67.72), G(68.82)):
    put('click', t, -4)
put('swoosh', G(93.4), -8)
put('whoosh', G(102.0), -9)
put('tada', G(104.5), -12)
for i in range(6):
    put('click', 55.4 + i * 0.25, -14)
    put('click', h.GAP_AT + 0.3 + i * 0.3, -16)
# Stimme
vo = load(f'{ROOT}/audio/vo.wav')
last = h.NEW[-1][2] + 0.15
m = int(last * SR)
vo[m:] = 0
f = int(0.05 * SR)
vo[m - f:m] *= np.linspace(1, 0, f)[:, None]
voice = np.zeros_like(out)
ga = int(h.GAP_AT * SR)
voice[:ga] = vo[:ga]
gi = int(G(h.GAP_AT) * SR)
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
