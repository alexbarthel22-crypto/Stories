import json, wave, re
import numpy as np

FPS = 30; GAP = 0.22; TAIL = 0.9; SR = 44100
segs = json.load(open('segs.json'))


def load(fn):
    w = wave.open(fn)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    sr = w.getframerate()
    n = int(len(a) * SR / sr)
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)


t = 0.15; voice = []; out = []
for i, s in enumerate(segs):
    a = load(s['id'] + '.wav'); d = len(a) / SR
    vs = t
    caps = s['cap']
    L = [len(c.replace('*', '').replace('!', '')) + 3 for c in caps]; tot = sum(L); ct = vs
    cl = []
    for c, l in zip(caps, L):
        dd = d * l / tot
        cl.append({'text': c, 't0': round(ct, 3), 't1': round(ct + dd, 3)}); ct += dd
    end = vs + d + GAP + (TAIL if i == len(segs) - 1 else 0)
    out.append({'id': s['id'], 'start': round(t if i else 0, 3), 'end': round(end, 3), 'caps': cl})
    voice.append((vs, a)); t = end
total = t
N = int(total * SR) + SR
v = np.zeros(N, np.float32)
for st, a in voice:
    i = int(st * SR); v[i:i + len(a)] += a

nf = int(total * FPS)
env = []
for f in range(nf):
    i = int(f / FPS * SR); seg = v[i:i + SR // FPS]
    env.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0)
mx = max(env)
env = [round(min(1, (e / mx) * 1.8), 3) for e in env]
env = [e if e > 0.08 else 0 for e in env]

rng = np.random.default_rng(1)
noise = rng.standard_normal(N).astype(np.float32)
rain = np.convolve(noise, np.ones(6) / 6, 'same').astype(np.float32) * 0.013
drops = np.zeros(N, np.float32)
for p in rng.integers(0, N - 2000, int(total * 25)):
    drops[p:p + 300] += rng.standard_normal(300) * np.exp(-np.arange(300) / 40) * 0.022
fx = np.zeros(N, np.float32)
for o in out[1:]:
    i = int(o['start'] * SR); n = int(0.09 * SR); tt = np.arange(n) / SR
    fx[i:i + n] += 0.18 * np.sin(2 * np.pi * (500 + 3000 * tt) * tt) * np.exp(-tt * 35)
# leiser Musik-Teppich (gezupfte Akkorde)
mus = np.zeros(N, np.float32); beat = 60 / 112
chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
k = 0
while k * beat / 2 < total:
    bt = k * beat / 2
    for j, fq in enumerate(chords[(k // 8) % 4]):
        i = int((bt + j * 0.02) * SR); n = min(int(0.35 * SR), N - i)
        if n <= 0: continue
        tt = np.arange(n) / SR
        mus[i:i + n] += ((np.sin(2 * np.pi * fq * tt) + 0.4 * np.sin(4 * np.pi * fq * tt)) * np.exp(-tt * 9) * 0.035).astype(np.float32)
    k += 1
mix = np.clip(v * 0.95 + rain + drops + fx + mus, -1, 1)
o = wave.open('mix.wav', 'w'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((mix[:int(total * SR)] * 32767).astype(np.int16).tobytes()); o.close()

data = {'fps': FPS, 'segs': out, 'env': env, 'total': total}
json.dump(data, open('data.json', 'w'), ensure_ascii=False)
open('data.js', 'w').write('const DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n')
s = open('logo.svg').read(); s = re.sub(r'^<svg[^>]*>', '', s).replace('</svg>', '').strip()
open('logo.js', 'w').write('const LOGO = ' + json.dumps(s) + ';\n')
open('page.html', 'w').write('''<!doctype html><html><head><meta charset="utf-8"><style>@font-face{font-family:Lilita;src:url(lilita.woff2) format('woff2')}@font-face{font-family:Lilita;src:url(lilita-ext.woff2) format('woff2');unicode-range:U+0100-024F}html,body{margin:0;background:#000}svg{display:block}</style></head>
<body><svg id="root" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920"></svg>
<script src="logo.js"></script><script src="chars.js"></script><script src="scenes.js"></script><script src="style.js"></script><script src="team.js"></script><script src="pichu_kasse.js"></script><script src="data.js"></script><script src="main.js"></script></body></html>''')
print('total', round(total, 2), 'frames', nf)
