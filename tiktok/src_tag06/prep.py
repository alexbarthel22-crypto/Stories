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
    if s.get('cap_off') and len(s['cap_off']) == len(caps):
        offs = list(s['cap_off']) + [d]
        for j, c in enumerate(caps):
            cl.append({'text': c, 't0': round(vs + offs[j], 3), 't1': round(vs + offs[j + 1], 3)})
    else:
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
from sfx import build_sfx
fx = build_sfx(out, N)
from music2 import make_music
mus = make_music(total, v)[:N] * 1.35
if len(mus) < N: mus = np.pad(mus, (0, N - len(mus)))
mix = v * 1.3 + rain + drops + fx + mus
_m = np.abs(mix); mix = np.where(_m > 0.85, np.sign(mix) * (0.85 + 0.14 * np.tanh((_m - 0.85) / 0.14)), mix)
mix = np.clip(mix, -1, 1)
o = wave.open('mix.wav', 'w'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((mix[:int(total * SR)] * 32767).astype(np.int16).tobytes()); o.close()

data = {'fps': FPS, 'segs': out, 'env': env, 'total': total}
json.dump(data, open('data.json', 'w'), ensure_ascii=False)
open('data.js', 'w').write('const DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n')
s = open('logo.svg').read(); s = re.sub(r'^<svg[^>]*>', '', s).replace('</svg>', '').strip()
open('logo.js', 'w').write('const LOGO = ' + json.dumps(s) + ';\n')
import base64
open('icon.js', 'w').write('const SHARE_ICON = "data:image/jpeg;base64,' + base64.b64encode(open('teilen_icon.jpg', 'rb').read()).decode() + '";\n')
open('page.html', 'w').write('''<!doctype html><html><head><meta charset="utf-8"><style>@font-face{font-family:Lilita;src:url(lilita.woff2) format('woff2')}@font-face{font-family:Lilita;src:url(lilita-ext.woff2) format('woff2');unicode-range:U+0100-024F}html,body{margin:0;background:#000}svg{display:block}</style></head>
<body><svg id="root" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920"></svg>
<script src="logo.js"></script><script src="icon.js"></script><script src="chars.js"></script><script src="scenes.js"></script><script src="style.js"></script><script src="team.js"></script><script src="pichu_kasse.js"></script><script src="tag2props.js"></script><script src="fanpics.js"></script><script src="lkzpic.js"></script><script src="ultra.js"></script><script src="pics4.js"></script><script src="pic13.js"></script><script src="picnico.js"></script><script src="tag6props.js"></script><script src="tag4props.js"></script><script src="tag3props.js"></script><script src="data.js"></script><script src="main.js"></script></body></html>''')
print('total', round(total, 2), 'frames', nf)
