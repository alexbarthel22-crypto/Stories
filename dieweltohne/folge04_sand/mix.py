"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge04_sand.mp4
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
VANISH, RETURN = 10.0, 57.0
WK = [[10, 10], [17, 9.3], [24, 8.4], [31, 7.4], [39, 6.0], [47, 4.0], [57, 0]]
SKY_DROP, STAND_FALL, TOWER_FALL, DUNE_BREAK, CRUMBLE = 26.0, 33.5, 42.5, 48.5, 59.0


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


# ---------------- Strand ----------------
amb('fsd_beach_crowd', 0, 10.4, -16)
amb('fsd_beach_waves', 0, 17.05, -12)
amb('fsd_seagulls', 0, 10.4, -18)
for k in range(1, 8): add('fsd_volleyball', k * 1.3 - 0.02, 0.3, db=-4, off=1.6, fout=0.1, pan=0.3 * (-1) ** k)   # Ballwechsel
add('fsd_teens_laugh', 5.0, 2.5, db=-18, off=0.7, fin=0.2, fout=0.5)
for s_ in range(1, 10): tick(s_, -6 if s_ < 7 else 0)
add('fsd_sub_rumble', 7.0, 3.05, db=-10, off=1.0, fin=2.5, fout=0.05)
add('fsd_whoosh_boom', 9.99, 3.0, db=2, fout=1.5)
add('fsd_sand_pour2', 9.95, 1.0, db=-2, off=5.5, fin=0.02, fout=0.3)                  # Sand rieselt weg
for k, tt in enumerate([10.42, 10.46, 10.5, 10.55]): add('fsd_body_fall', tt, 0.6, db=-2 - k, off=0.45 if k % 2 else 4.55, fout=0.2, pan=(k - 1.5) * 0.4)
add('fsd_crowd_gasp', 10.5, 2.4, db=-8, fout=0.6)
add('fsd_screams', 10.6, 1.6, db=-16, off=1.0, fin=0.1, fout=0.8)
amb('fsd_flood_rush2', 10.5, 17.05, -16)                                            # Meer läuft nach
add('fsd_teens_laugh', 12.8, 4.0, db=-10, fin=0.3, fout=1.0)

# ---------------- Countdown der 10 Sekunden ----------------
ticks = []; last = 10
for f in range(int(VANISH * 30), int(RETURN * 30) + 1):
    v = world_left(f / 30)
    if int(v * 10) < int(last * 10): ticks.append(f / 30)
    last = v
for T in ticks: tick(T, -15 + (4 if T > 52 else 0))

# ---------------- Stufe 2: Gaming ----------------
add('fsd_mouse_clicks', 17.0, 0.9, db=-8, off=7.0, fout=0.1)
add('fsd_static', 17.05, 0.8, db=-8, fout=0.3)                                       # Bildschirm stirbt
add('fsd_pc_fan', 17.3, 2.2, db=-6, off=23.9, fin=0.02, fout=0.5)                    # Lüfter laufen aus
add('fsd_dust_wind', 17.4, 6.6, db=-12, off=4.0, fin=0.2, fout=0.6)                   # Fenster weg, Vorhang fliegt
amb('fsd_city_day', 17.4, 24.05, -22)
add('fsd_keyboard', 19.5, 0.5, db=-4, off=13.3, fout=0.2)                             # Faust auf die Tastatur
add('fsd_screams', 19.6, 1.4, db=-14, off=1.0, fout=0.6)

# ---------------- Stufe 3: Glasboden ----------------
amb('fsd_canyon_wind', 24, 31.05, -10)
add('fsd_teens_laugh', 24.3, 1.6, db=-16, off=0.7, fout=0.4)
add('fsd_whoosh_boom', SKY_DROP - 0.01, 3.0, db=0, fout=1.5)
add('fsd_screams', SKY_DROP + 0.1, 2.5, db=-4, fin=0.02, fout=1.0)
add('fsd_metal_crash2', SKY_DROP + 0.3, 1.5, db=-10, off=0.1, fout=0.6)               # Griff ans Geländer
add('fsd_wind_rush', SKY_DROP, 5.0, db=-12, fin=0.3, fout=1.0)
add('fsd_crowd_gasp', SKY_DROP + 0.2, 2.0, db=-12, fout=0.6)

# ---------------- Stufe 4: Stadion ----------------
amb('fsd_football_crowd', 31, STAND_FALL + 0.4, -6, off=3.0)
add('fsd_football_crowd2', 31.4, 2.0, db=-10, off=0.5, fout=0.4)
add('fsd_referee_whistle', 32.4, 0.4, db=-8)
add('fsd_building_collapse', STAND_FALL - 0.9, 9.0, db=2, fin=0.02, fout=2.0)
add('fsd_rubble', STAND_FALL, 3.0, db=-2, fout=1.0)
add('fsd_screams', STAND_FALL + 0.4, 3.5, db=-4, fin=0.1, fout=1.5)
add('fsd_sub_rumble', STAND_FALL, 5.5, db=-6, off=1.0, fin=0.1, fout=1.5)
add('fsd_metal_crash', 36.5, 2.5, db=-2, peak_win=0.2, fout=1.0)                     # Mast schlägt auf
add('fsd_impact_boom2', 36.55, 2.4, db=-6, fout=1.2)

# ---------------- Stufe 5: Dubai ----------------
amb('fsd_helicopter', 39, 47.0, -14)
for k, tt in enumerate([39.7, 40.4, 41.1, 41.9, 43.3, 44.2]): add('fsd_splash_big', tt, 2.0, db=-8 - (k % 2) * 3, off=0.7, fout=0.8, pan=((k % 3) - 1) * 0.5)
add('fsd_wave_crash', 40.0, 6.0, db=-10, off=2.0, fin=0.5, fout=1.0)
add('fsd_building_collapse', TOWER_FALL - 0.9, 5.0, db=0, fout=1.5)
add('fsd_rubble', TOWER_FALL + 0.1, 3.0, db=-4, fout=1.0)
add('fsd_building_collapse', 44.4 - 0.9, 3.6, db=0, fout=0.5, pan=0.3)                # Nadelturm
add('fsd_sub_rumble', TOWER_FALL, 4.55, db=-6, off=1.0, fin=0.3, fout=0.05)

# ---------------- Stufe 6: Flut ----------------
amb('fsd_wave_crash', 47, DUNE_BREAK + 0.3, -8)
amb('fsd_dust_wind', 47, 57.05, -18)
add('fsd_sand_rush', DUNE_BREAK - 0.4, 6.0, db=-2, fin=0.02, fout=1.5)
add('fsd_whoosh_boom', DUNE_BREAK - 0.01, 3.0, db=-2, fout=1.5)
add('fsd_flood_rush', 48.9, 7.0, db=-2, off=0.5, fin=0.6, fout=0.5)
amb('fsd_flood_rush2', 49.5, 57.05, -6)
add('fsd_cows', 49.6, 2.5, db=-12, off=10.4, fout=0.6, pan=0.4)
add('fsd_building_collapse', 51.8 - 0.9, 5.0, db=-6, fout=1.5)
add('fsd_church_bell', 53.0, 2.4, db=-10, off=0.4, fout=1.2)
add('fsd_rubble', 55.3, 3.0, db=-2, fout=1.0)

# ---------------- Stufe 7: Sand zurück ----------------
add('fsd_sand_pour2', RETURN - 0.5, 4.0, db=0, off=5.5, fin=0.1, fout=0.6)
amb('fsd_sand_pour', RETURN, 68.05, -6)
add('fsd_whoosh_boom', RETURN - 0.02, 3.0, db=-2, speed=0.8, fout=1.5)
amb('fsd_dust_wind', RETURN, 90.0, -14)
add('fsd_building_collapse', CRUMBLE - 0.9, 9.0, db=0, fout=2.0)
add('fsd_sand_rush', CRUMBLE, 8.0, db=-4, fin=0.1, fout=2.0, pan=-0.3)
add('fsd_crowd_gasp', CRUMBLE + 0.6, 2.4, db=-12, fout=0.6)
add('fsd_building_collapse', 61.5 - 0.9, 5.0, db=-8, fout=1.5, pan=0.4)
add('fsd_screams', 62.0, 3.0, db=-20, off=1.0, fin=0.4, fout=1.2)
amb('fsd_sub_rumble', 68, 80.05, -16)
amb('fsd_sand_pour', 68, 80.05, -16)
add('fsd_helicopter', 70.0, 9.0, db=-22, fin=2.0, fout=2.0, pan=0.5)
add('fsd_sand_pour2', 80.6, 4.0, db=-4, off=5.5, fin=0.3, fout=0.8)                  # Handy zerrinnt
add('fsd_sand_pour', 81.0, 6.5, db=-6, fin=0.5, fout=1.5)
add('fsd_sub_rumble', 84.0, 5.9, db=-10, off=1.0, fin=2.0, fout=2.0)
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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge04_sand.mp4')
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
