"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge10_fleisch.mp4
"""
import json
import os
import subprocess
import sys

import numpy as np

SR = 48000
DUR = 90.0
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'sfx_raw')
_cache = {}


def load(name):
    if name not in _cache:
        p = os.path.join(RAW, name + '.wav')
        if not os.path.exists(p):
            print('fehlt:', name); _cache[name] = None; return None
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
        # Lautheit angleichen: jede Aufnahme auf etwa -24 dBFS RMS (lauteste Sekunden), damit die Pegel unten vergleichbar sind
        e = (x ** 2).mean(1); n = SR
        if len(e) > n:
            cs = np.concatenate([[0], np.cumsum(e)]); r = np.sqrt(((cs[n:] - cs[:-n]) / n).max())
        else:
            r = np.sqrt(e.mean())
        x *= min(30.0, 10 ** (-18 / 20) / max(r, 1e-6))
        _cache[name] = x
    return _cache[name]


def loudest(x, win):
    """Startsekunde des lautesten Fensters (für Einschläge, Kratzer usw.)."""
    e = (x ** 2).sum(1); n = int(win * SR)
    cs = np.concatenate([[0], np.cumsum(e, dtype=np.float64)])
    if len(e) <= n: return 0.0
    c = cs[n:] - cs[:-n]
    return max(0, int(c.argmax()) / SR)


def onsets(x, thresh=0.35, gap=0.15):
    env = np.abs(x).max(1); m = env.max() * thresh; out = []; last = -9
    for i in np.nonzero(env > m)[0]:
        if i / SR - last > gap: out.append(i / SR); last = i / SR
    return out


mix = np.zeros((int(DUR * SR), 2), np.float32)


def add(name, at, dur=None, db=0.0, off=0.0, fin=0.02, fout=0.05, speed=1.0, pan=0.0, peak_win=None):
    x = load(name)
    if x is None: return
    if peak_win: off = max(0, loudest(x, peak_win) - 0.03)
    seg = x[int(off * SR):]
    if speed != 1.0:  # Tonhöhe/Tempo ändern (wie langsames Abspielen)
        idx = np.arange(0, len(seg) - 1, speed)
        seg = np.stack([np.interp(idx, np.arange(len(seg)), seg[:, c]) for c in (0, 1)], 1).astype(np.float32)
    if dur is not None:
        n = int(dur * SR)
        if len(seg) < n:  # zu kurz: schleifen mit Überblendung
            if len(seg) == 0: return
            reps = int(np.ceil(n / len(seg))) + 1
            seg = np.concatenate([seg] * reps)
        seg = seg[:n].copy()
    seg = seg.copy()
    n = len(seg); a = int(fin * SR); b = int(fout * SR)
    if a: seg[:a] *= np.linspace(0, 1, a)[:, None]
    if b: seg[-b:] *= np.linspace(1, 0, b)[:, None]
    seg *= 10 ** (db / 20)
    if pan: seg[:, 0] *= 1 - max(0, pan); seg[:, 1] *= 1 + min(0, pan)
    s = int(at * SR); e = min(len(mix), s + n)
    mix[s:e] += seg[:e - s]


# ---------------- Zeitleiste (identisch zu src/timeline.js) ----------------
VANISH, RETURN = 10.0, 48.0
WK = [[10, 10], [17, 9.0], [24, 7.8], [31, 6.4], [39, 4.6], [48, 0]]
CLOCHE, ROTATE, TAILSTRIKE, STALL, BUCKET, FENCE_HIT, FENCE_BREAK, LION_JUMP, DOOR_SLAM = 19.2, 25.6, 26.3, 28.0, 32.2, 35.4, 37.4, 70.2, 73.8


def world_left(T):
    if T <= WK[0][0]: return 10
    for i in range(1, len(WK)):
        if T <= WK[i][0]:
            a, va = WK[i - 1]; b, vb = WK[i]
            return va + (vb - va) * (T - a) / (b - a)
    return 0


def amb(name, t0, t1, db, off=0.0, xf=0.8, speed=1.0, seg=None):
    x = load(name)
    if x is None: return
    L = (seg if seg else len(x) / SR / speed - off)
    t = t0
    while t < t1:
        d = min(L, t1 - t + xf)
        add(name, t, d, db=db, off=off, fin=xf if t > t0 else 0.3, fout=xf, speed=speed)
        t += max(1.0, L - xf)


def tick(T, db):
    add('fsd_clock_tick', T - 0.005, 0.16, db=db, off=0.0, fout=0.05)


# ---------------- Countdown-Ticks: jede volle Sekunde (Weltzeit) ----------------
ticks = []
for s_ in range(1, 10): ticks.append(float(s_))
T_ = 10.0
while T_ < RETURN:
    if int(world_left(T_)) != int(world_left(T_ + 0.01)): ticks.append(T_ + 0.01)
    T_ += 0.01
for tt in ticks: tick(tt, -8 if tt < 7 or (VANISH < tt < 46) else -2)

# ---------------- Garten: Grillfest ----------------
amb('fsd_birdsong', 0, 10.05, -20)
amb('fsd_sizzle', 0, 10.0, -17)
add('fsd_kid_laugh', 5.2, 1.6, db=-22, fout=0.5, pan=-0.4)
add('fsd_dog_yip', 8.6, 0.6, db=-18, fout=0.2, pan=0.2)
# Stufe 1: Fleisch weg
add('fsd_whoosh_fast', VANISH - 0.08, 0.8, db=-8, fout=0.3)
add('fsd_air_burst', VANISH - 0.02, 0.6, db=-12, fout=0.3)
add('fsd_sizzle', VANISH, 1.2, db=-22, fin=0.0, fout=1.0)     # Brutzeln bricht ab
add('fsd_gas_hiss', VANISH + 0.2, 4.0, db=-24, fin=0.3, fout=1.0)
add('fsd_spoon_clink', VANISH + 0.35, 0.4, db=-14, fout=0.1)    # Zange greift ins Leere
add('fsd_dog_yap', VANISH + 1.0, 1.2, db=-14, fout=0.3, pan=0.2)
add('fsd_teens_laugh', VANISH + 1.5, 4.0, db=-12, fin=0.2, fout=1.0, pan=-0.3)
amb('fsd_birdsong', 10, 17.05, -24)
# ---------------- Stufe 2: Date ----------------
amb('fsd_restaurant', 17, 24.05, -16)
add('fsd_footsteps_run', 17.0, 1.4, db=-26, speed=0.6, fout=0.4)
add('fsd_spoon_clink', 18.6, 0.5, db=-10, fout=0.1)                # Teller wird abgestellt
add('fsd_thump_clank', CLOCHE - 0.02, 0.6, db=-14, fout=0.2)       # Glocke wird angehoben
add('fsd_gasp', CLOCHE + 0.5, 1.2, db=-14, fout=0.3)
add('fsd_giggle', CLOCHE + 1.0, 2.6, db=-10, fout=0.6, pan=0.3)
add('fsd_sigh', CLOCHE + 2.7, 1.6, db=-12, fout=0.4, pan=-0.3)
# ---------------- Stufe 3: Frachtjet ----------------
add('fsd_jet_roar', 24.0, 7.05, db=-4, fin=0.3, fout=0.8)
add('fsd_jet_flyby', 26.0, 5.0, db=-8, fin=0.5, fout=1.0)
add('fsd_metal_grind', TAILSTRIKE - 0.02, 1.0, db=-4, off=0.8, fout=0.3)  # Heck schleift über die Piste
add('fsd_scrape', TAILSTRIKE + 0.05, 0.8, db=-8, fout=0.3)
add('fsd_crash_thud', TAILSTRIKE - 0.02, 0.8, db=-6, fout=0.4)
add('fsd_cockpit_alarm', STALL - 0.1, 2.4, db=-10, fout=0.4)        # Überziehwarnung (aus der Ferne)
add('fsd_sub_rumble', STALL + 0.4, 2.6, db=-10, fin=0.3, fout=0.8)
# ---------------- Stufe 4: Zoo ----------------
amb('fsd_crowd_murmur', 31, FENCE_BREAK + 0.2, -22)
add('fsd_soft_thud', BUCKET + 1.3, 0.5, db=-14)                       # Eimer umgedreht: nichts
add('fsd_growl', BUCKET + 1.2, 2.5, db=-8, fin=0.3, fout=0.8)
add('fsd_lion_roar2', 34.2, 2.6, db=-6, peak_win=0.3, fin=0.05, fout=0.8)
add('fsd_chain_clank', FENCE_HIT - 0.03, 1.4, db=-2, peak_win=0.2, fout=0.5)
add('fsd_crowd_gasp', FENCE_HIT + 0.2, 1.6, db=-12, fout=0.5)
add('fsd_lion_roar', FENCE_BREAK - 1.0, 3.0, db=-2, peak_win=0.3, fin=0.05, fout=1.0)
add('fsd_chain_clank', FENCE_BREAK - 0.03, 1.6, db=0, off=0.3, fout=0.6)
add('fsd_metal_crash2', FENCE_BREAK + 0.45, 1.2, db=-4, fout=0.6)     # Gitter schlägt auf
add('fsd_screams', FENCE_BREAK + 0.3, 1.5, db=-8, fin=0.1, fout=0.4)
# ---------------- Stufe 5: Löwen in der Stadt ----------------
amb('fsd_city_day', 39, 48.05, -18)
add('fsd_scream_girl', 40.6, 1.6, db=-12, fout=0.5, pan=-0.4)
add('fsd_footsteps_run', 40.8, 3.0, db=-14, fout=0.6)
add('fsd_screams', 41.2, 3.0, db=-14, fin=0.2, fout=0.8, pan=0.3)
add('fsd_car_horn', 41.6, 0.9, db=-14, fout=0.2, pan=0.5)
add('fsd_bell', 42.0, 1.2, db=-12, fout=0.4)                         # Straßenbahnglocke
add('fsd_train_brake', 42.2, 2.2, db=-4, fin=0.05, fout=0.6)
add('fsd_growl', 44.0, 1.6, db=-12, fout=0.5, pan=-0.3)
add('fsd_crash_thud', 45.95, 0.6, db=-4, fout=0.3)                   # Löwe landet auf dem Autodach
add('fsd_glass_rattle', 45.97, 0.8, db=-12, fout=0.3)
add('fsd_lion_roar', 46.3, 2.0, db=0, peak_win=0.3, fin=0.03, fout=0.7)
# ---------------- Stufe 6: Rückkehr, Siedlung ----------------
add('fsd_whoosh_fast', RETURN - 0.4, 0.8, db=-8, speed=0.8, fout=0.3)
add('fsd_lighter_whoosh', RETURN + 0.1, 1.0, db=-10, fout=0.4)
amb('fsd_wind', 48, 58.05, -15)
amb('fsd_birdsong', 48, 58.05, -26)
for k, tt in enumerate([48.3, 48.8, 49.5, 50.4]): add('fsd_sizzle', tt, 2.5, db=-18 - 2 * k, fin=0.3, fout=1.0, pan=(k % 3 - 1) * 0.5)
add('fsd_dog', 52.0, 1.5, db=-13, fout=0.4, pan=-0.5)
add('fsd_dog_yap', 53.2, 1.0, db=-16, fout=0.3, pan=0.5)
add('fsd_run', 54.2, 3.8, db=-14, fin=0.4, fout=0.5)                  # Pfoten auf Asphalt
add('fsd_growl', 56.0, 1.8, db=-14, fout=0.5)
# ---------------- Stufe 7: Garten ----------------
amb('fsd_sizzle', 58, 70.5, -21)
amb('fsd_birdsong', 58, 68.05, -22)
add('fsd_growl', 62.4, 2.0, db=-12, fout=0.6, pan=0.4)
add('fsd_gasp', 63.1, 1.0, db=-12, fout=0.3)
add('fsd_lion_roar2', 66.0, 2.0, db=-2, peak_win=0.3, fin=0.03, fout=0.7)
add('fsd_dog_yap', 66.4, 1.0, db=-14, fout=0.3, pan=-0.3)
add('fsd_chain_clank', LION_JUMP - 0.2, 0.6, db=-12, fout=0.3)
add('fsd_body_fall', LION_JUMP + 0.65, 0.6, db=-6, peak_win=0.2, fout=0.3)   # Landung im Gras
add('fsd_scream_girl', LION_JUMP + 0.2, 1.6, db=-8, fout=0.5, pan=-0.3)
add('fsd_screams', LION_JUMP + 0.5, 1.6, db=-12, fout=0.5)
add('fsd_footsteps_run', LION_JUMP + 0.3, 2.8, db=-12, fout=0.6)
add('fsd_door_slam', DOOR_SLAM, 1.0, db=-4, peak_win=0.2, fout=0.4)
add('fsd_lion_roar', 73.0, 1.6, db=-4, peak_win=0.3, fin=0.03, fout=0.6)
add('fsd_metal_crash', 76.6, 1.0, db=-10, fout=0.4)                    # Platte fällt von der Ablage
add('fsd_growl', 77.4, 2.2, db=-12, fout=0.6)
# Schluss: hinter der Glastür, gedämpft
add('fsd_growl', 81.0, 3.0, db=-20, fin=0.4, fout=0.8)
add('fsd_sigh', 83.6, 1.8, db=-10, fout=0.5)
amb('fsd_birdsong', 80, 89.0, -28)
add('fsd_sizzle', 80, 9.0, db=-24, fin=0.5, fout=1.5)
add('fsd_lion_roar2', 87.3, 2.4, db=-10, peak_win=0.3, fin=0.05, fout=1.5)
# ---------------- Ausgabe ----------------
peak = np.abs(mix).max()
if peak > 0.98: mix *= 0.98 / peak
tmp = os.path.join(HERE, 'mix_roh.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', tmp], input=mix.tobytes(), check=True)
out = os.path.join(HERE, 'mix.wav')
# TikTok-Lautheit: ca. -14 LUFS, Spitzen begrenzt
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'acompressor=threshold=-30dB:ratio=3:attack=15:release=400:makeup=6,loudnorm=I=-14.5:TP=-2:LRA=11,alimiter=limit=0.79:attack=2:release=60', '-ar', str(SR), '-c:a', 'pcm_s16le', out], check=True)
os.remove(tmp)
print('mix.wav fertig, Ticks:', len(ticks))

if '--mux' in sys.argv:
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge10_fleisch.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', out, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', '90', '-movflags', '+faststart', fin], check=True)
    print('fertig:', fin)

# Quellenangaben für die Videobeschreibung
cred = []
for f in sorted(os.listdir(RAW)):
    if f.endswith('.json') and f[:-5] in _cache and _cache[f[:-5]] is not None:
        m = json.load(open(os.path.join(RAW, f)))
        src = 'Freesound, über den Datensatz FSD50K' if m['artist'].startswith('Freesound') else 'Wikimedia Commons'
        cred.append(f"- {m['title'][5:]} – {m['license']} ({src})")
open(os.path.join(HERE, 'quellen_geraeusche.md'), 'w').write('# Geräusche (echte Aufnahmen)\n\nAlle Geräusche sind echte Aufnahmen unter CC0 (frei nutzbar, keine Namensnennung nötig).\n\n' + '\n'.join(cred) + '\n\nBilder: NASA Black Marble (Erde bei Nacht) und NASA Blue Marble (Erde bei Tag), gemeinfrei, über Wikimedia Commons\n')
