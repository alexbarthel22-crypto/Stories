#!/usr/bin/env python3
"""Baut aus dem CC0-MakeHuman-Grundkörper (base.obj, Targets, Skelett, Gewichte) eine Figur für three.js.
Aufruf: python3 mh_build.py ausgabe.json '{"male":1,"eth":{"caucasian":1},"height":1.0,"top":0.012,"bottom":0.008}'
Daten aus /home/user/mh_cc0 (heruntergeladen von github.com/makehumancommunity/makehuman, Assets CC0 seit 09/2020)."""
import json, sys, numpy as np
MH = '/home/user/mh_cc0'
out, prm = sys.argv[1], json.loads(sys.argv[2] if len(sys.argv) > 2 else '{}')
V = []; UV = []; G = {}; cur = None
for l in open(f'{MH}/base.obj'):
    if l.startswith('v '): V.append([float(x) for x in l.split()[1:4]])
    elif l.startswith('vt '): UV.append([float(x) for x in l.split()[1:3]])
    elif l.startswith('g '): cur = l.split()[1]
    elif l.startswith('f '):
        G.setdefault(cur, []).append([(int(x.split('/')[0]) - 1, int(x.split('/')[1]) - 1 if '/' in x else -1) for x in l.split()[1:]])
V = np.array(V); UV = np.array(UV)
def target(name):
    d = np.zeros_like(V)
    for l in open(f'{MH}/t/{name}.target'):
        if l[0] == '#' or not l.strip(): continue
        p = l.split(); d[int(p[0])] = [float(x) for x in p[1:4]]
    return d
male = prm.get('male', 1.0); eth = prm.get('eth', {'caucasian': 1.0}); s = sum(eth.values())
for e, w in eth.items():
    V += (w / s) * (male * target(f'{e}-male-young') + (1 - male) * target(f'{e}-female-young'))
V += male * target('prop-male') + (1 - male) * target('prop-female')
V *= 0.1 * prm.get('height', 1.0)              # Dezimeter -> Meter
sk = json.load(open(f'{MH}/default.mhskel')); W = json.load(open(f'{MH}/default_weights.mhw'))['weights']
J = {k: V[v].mean(0) for k, v in sk['joints'].items()}
for g, fs in G.items():
    if g.startswith('joint-'): J[g] = V[sorted({a for f in fs for a, _ in f})].mean(0)
ground = V[sorted({a for f in G['body'] for a, _ in f}), 1].min(); V[:, 1] -= ground; J = {k: v - [0, ground, 0] for k, v in J.items()}
def jp(ref):
    return J[ref] if isinstance(ref, str) else np.mean([J[r] for r in ref], 0)
names = list(sk['bones'].keys())
order = []; seen = set()
def add(n):
    if n in seen: return
    p = sk['bones'][n]['parent']
    if p: add(p)
    seen.add(n); order.append(n)
for n in names: add(n)
bones = [{'name': n, 'parent': order.index(sk['bones'][n]['parent']) if sk['bones'][n]['parent'] else -1,
          'head': jp(sk['bones'][n]['head']).round(5).tolist(), 'tail': jp(sk['bones'][n]['tail']).round(5).tolist()} for n in order]
bi = {n: i for i, n in enumerate(order)}
# Gewichte: höchstens 4 pro Punkt
wl = [[] for _ in V]
for b, lst in W.items():
    for i, w in lst: wl[i].append((w, bi[b]))
SI = np.zeros((len(V), 4), int); SW = np.zeros((len(V), 4))
for i, l in enumerate(wl):
    l.sort(reverse=True); l = l[:4]; t = sum(w for w, _ in l) or 1
    for k, (w, b) in enumerate(l): SI[i, k] = b; SW[i, k] = w / t
# Kleidungsbereiche aus den Knochen
def grp(bn):
    if bn.startswith(('foot', 'toe')): return 3
    if bn.startswith(('upperleg', 'lowerleg', 'pelvis')): return 2
    if bn.startswith(('spine', 'clavicle', 'shoulder', 'upperarm', 'lowerarm', 'breast')) or bn == 'root': return 1
    return 0
R = np.zeros((len(V), 4))
for i, l in enumerate(wl):
    for w, b in l: R[i, grp(order[b])] += w
    if R[i].sum() == 0: R[i, 0] = 1
R /= R.sum(1, keepdims=True)
# Normalen
F = []
for f in G['body']:
    vs = [a for a, _ in f]; F += [[vs[0], vs[1], vs[2]], [vs[0], vs[2], vs[3]]] if len(vs) == 4 else [vs]
F = np.array(F); N = np.zeros_like(V)
fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
for k in range(3): np.add.at(N, F[:, k], fn)
N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
# Saum: Oberteil endet an der Hüfte (darunter Hose), Ärmel nach Wunsch
hem = bones[0]['head'][1] + prm.get('hem', 0.03)
for i in range(len(V)):
    c = R[i, 1] + R[i, 2]
    if c > 0.3 and abs(V[i, 0]) < 0.21:
        k = np.clip((V[i, 1] - hem) / 0.012 + 0.5, 0, 1)   # weicher Übergang über 1,2 cm
        R[i, 1] = c * k; R[i, 2] = c * (1 - k)
if prm.get('short'):   # kurze Ärmel: Unterarm ist Haut
    for i, l in enumerate(wl):
        la = sum(w for w, b in l if order[b].startswith('lowerarm'))
        R[i, 0] += la * 0.98; R[i, 1] = max(0, R[i, 1] - la * 0.98)
if prm.get('shorts'):  # kurze Hose: Unterschenkel Haut
    for i, l in enumerate(wl):
        ll = sum(w for w, b in l if order[b].startswith('lowerleg'))
        R[i, 0] += ll; R[i, 2] = max(0, R[i, 2] - ll)
R /= R.sum(1, keepdims=True)
th = np.array([0, prm.get('top', 0.012), prm.get('bottom', 0.008), prm.get('shoe', 0.004)])
sm = lambda x: np.clip((x - 0.25) / 0.5, 0, 1) ** 2 * (3 - 2 * np.clip((x - 0.25) / 0.5, 0, 1))
cw = np.clip(sm(R[:, 1]) + sm(R[:, 2]) + sm(R[:, 3]), 0, 1)
thick = (sm(R[:, 1]) * th[1] + sm(R[:, 2]) * th[2] + sm(R[:, 3]) * th[3])
Vc = V + N * thick[:, None]
# Schnitt: Hosenbeine fallen gerade (Mindestradius um die Beinachse), Ärmel locker, Pulli hängt von der Brust
def axis_push(sel, a, b, rmin):
    a = np.array(a); b = np.array(b); ab = b - a; L2 = (ab ** 2).sum()
    for i in np.where(sel)[0]:
        t = np.clip(((Vc[i] - a) * ab).sum() / L2, 0, 1); c = a + ab * t; d = Vc[i] - c; r = np.linalg.norm(d)
        rm = rmin(t)
        if 1e-6 < r < rm: Vc[i] = c + d / r * rm
jp_ = lambda n: np.array(J[n]) if n in J else None
for sd, sx in [('l', 1), ('r', -1)]:
    hipj, knee, ank = J[f'joint-{sd}-upper-leg'], J[f'joint-{sd}-knee'], J[f'joint-{sd}-ankle']
    legsel = (R[:, 2] > 0.5) & (V[:, 1] < hipj[1] - 0.06) & (V[:, 0] * sx > 0.02)
    rb = prm.get('baggy', 0.07)
    axis_push(legsel, hipj, ank, lambda t: rb + 0.012 * (1 - t))
    sh, el, wr = J[f'joint-{sd}-shoulder'], J[f'joint-{sd}-elbow'], J[f'joint-{sd}-hand']
    armsel = (R[:, 1] > 0.5) & (np.abs(V[:, 0]) > np.abs(sh[0]) - 0.0)
    ra = prm.get('sleeve', 0.05)
    axis_push(armsel, sh, wr, lambda t: ra + 0.012 * (1 - t))
# Oberkörper: vorne/hinten nicht unter die Linie von Brust bzw. Schulterblatt
tor = (R[:, 1] > 0.5) & (np.abs(V[:, 0]) < 0.2) & (V[:, 1] < J['joint-neck'][1] - 0.08)
chestY = J['joint-neck'][1] - 0.2
if tor.any():
    fz = Vc[tor & (np.abs(V[:, 1] - chestY) < 0.03) & (np.abs(V[:, 0]) < 0.08), 2]
    front = fz.max() if len(fz) else 0.12
    for i in np.where(tor)[0]:
        y = Vc[i, 1]
        if y < chestY and Vc[i, 2] > 0:
            lim = front - (chestY - y) * prm.get('drape', 0.12) - 0.15 * (Vc[i, 0] / 0.2) ** 2
            if Vc[i, 2] < lim: Vc[i, 2] = lim
# Kleidung glätten: Körperdetails (Po, Bauchmuskeln, Schritt) verschwinden unter dem Stoff
adj = [set() for _ in V]
for f in F:
    for a in range(3):
        adj[f[a]].add(f[(a + 1) % 3]); adj[f[a]].add(f[(a + 2) % 3])
nb = [np.array(sorted(x)) if x else np.array([i]) for i, x in enumerate(adj)]
it = prm.get('smooth', 14)
for _ in range(it):
    avg = np.array([Vc[n].mean(0) for n in nb])
    Vc = Vc + (avg - Vc) * (0.55 * cw)[:, None]
    # nie in den Körper einsinken: Mindestabstand entlang der Normalen
    d = ((Vc - V) * N).sum(1); low = d < thick * 0.7
    Vc[low] += N[low] * (thick[low] * 0.7 - d[low])[:, None]
# Normalen der Kleidung neu
Nc = np.zeros_like(V); fn2 = np.cross(Vc[F[:, 1]] - Vc[F[:, 0]], Vc[F[:, 2]] - Vc[F[:, 0]])
for k in range(3): np.add.at(Nc, F[:, k], fn2)
Nc /= np.linalg.norm(Nc, axis=1, keepdims=True) + 1e-9
N = N * (1 - cw[:, None]) + Nc * cw[:, None]; N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
def tri(group):
    t = []
    for f in G[group]:
        if len(f) == 4: t += [[f[0], f[1], f[2]], [f[0], f[2], f[3]]]
        else: t.append(f)
    return t
body = tri('body')
key = ['skin', 'top', 'bottom', 'shoe']
def pack(tris, src, groups=None):
    idx = {}; P = []; U = []; I = []; S = []; Wt = []; RR = []; orig = []
    for t in tris:
        for a, uv in t:
            k = (a, uv)
            if k not in idx:
                idx[k] = len(P); P.append(src[a].round(5).tolist()); U.append(UV[uv].round(5).tolist() if uv >= 0 else [0, 0])
                S.append(SI[a].tolist()); Wt.append(SW[a].round(4).tolist()); RR.append(R[a].round(3).tolist()); orig.append(a)
            I.append(idx[k])
    return {'pos': P, 'uv': U, 'idx': I, 'si': S, 'sw': Wt, 'reg': RR, 'orig': orig}
# Körper: ein Netz, Material je Dreieck nach Mehrheit
fr = [int(R[[a for a, _ in t]].mean(0).argmax()) for t in body]
order_t = sorted(range(len(body)), key=lambda i: fr[i])
res = {'bones': bones, 'meshes': {}}
res['meshes']['body'] = pack([body[i] for i in order_t], Vc)
grp_list = []; start = 0
for k in range(4):
    n = sum(1 for i in order_t if fr[i] == k)
    if n: grp_list.append([start * 3, n * 3, k])
    start += n
res['meshes']['body']['groups'] = grp_list
for g in ['helper-l-eye', 'helper-r-eye', 'helper-upper-teeth', 'helper-lower-teeth', 'helper-tongue']:
    res['meshes'][g] = pack(tri(g), V)
lash = [t for g in G if 'eyelashes' in g for t in tri(g)]
res['meshes']['lashes'] = pack(lash, V)
# Kopfhaut (für Haare): Haaransatz als Kurve um den Kopf, weicher Übergang je Punkt
eyeY = (J['joint-l-eye'][1] + J['joint-r-eye'][1]) / 2
hv = [i for i, l in enumerate(wl) if sum(w for w, b in l if order[b] == 'head') > 0.6]
Hc = (V[hv].min(0) + V[hv].max(0)) / 2
style = prm.get('hairStyle', 'short')
HL = {'short': [(0, .062), (.45, .06), (.8, .052), (1.15, .036), (1.3, .004), (1.45, -.006), (1.6, .03), (1.95, .03), (2.3, -.055), (3.15, -.07)],
      'long': [(0, .066), (.45, .062), (.8, .05), (1.15, .03), (1.3, -.01), (1.45, -.02), (1.6, .0), (1.95, -.02), (2.3, -.08), (3.15, -.1)],
      'bald': [(0, .2), (3.15, .2)], 'receding': [(0, .085), (.45, .08), (.8, .07), (1.15, .04), (1.3, .004), (1.45, -.006), (1.6, .03), (1.95, .03), (2.3, -.05), (3.15, -.065)]}[style]
def hairline(th):
    th = abs(th)
    for (a0, h0), (a1, h1) in zip(HL, HL[1:]):
        if th <= a1: return h0 + (h1 - h0) * (th - a0) / (a1 - a0)
    return HL[-1][1]
HA = np.zeros(len(V))
for i in hv + [i for i, l in enumerate(wl) if sum(w for w, b in l if order[b].startswith('neck')) > 0.3]:
    x, y, z = V[i]; th = np.arctan2(x, z - Hc[2]); up = y - eyeY; hl = hairline(th)
    if R[i, 0] < 0.6: continue
    k = np.clip((up - hl + 0.004) / 0.016, 0, 1); HA[i] = k * k * (3 - 2 * k)
scalp = [t for t in body if max(HA[a] for a, _ in t) > 0.01]
res['meshes']['scalp'] = pack(scalp, V)
res['meshes']['scalp']['nrm'] = [N[a].round(4).tolist() for a in res['meshes']['scalp']['orig']]
res['meshes']['scalp']['ha'] = [round(float(HA[a]), 3) for a in res['meshes']['scalp']['orig']]
res['meshes']['scalp'].pop('reg')
res['meshes']['body']['nrm'] = [N[a].round(4).tolist() for a in res['meshes']['body']['orig']]
res['meshes']['body']['ha'] = [round(float(HA[a]), 3) for a in res['meshes']['body']['orig']]
res['joints'] = {k: J[k].round(5).tolist() for k in ['joint-l-eye', 'joint-r-eye', 'joint-head', 'joint-mouth', 'joint-jaw', 'joint-head-2', 'joint-neck', 'joint-l-hand', 'joint-r-hand']}
res['eyeY'] = float(eyeY)
for m in res['meshes'].values(): m.pop('orig', None)
for k in list(res['meshes']):
    if k != 'body': res['meshes'][k].pop('reg', None)
json.dump(res, open(out, 'w'), separators=(',', ':'))
print(out, {k: len(v['idx']) // 3 for k, v in res['meshes'].items()}, 'Höhe', round(V[:, 1].max(), 3))
