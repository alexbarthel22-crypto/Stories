"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge11_muscheln.mp4
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
LEMON, POP, FLASH, TRAY, SINK, HOLES, TILT, TOWER_HIT, WINDOW, BURIED, HAND_UP, HEAD_UP, GULP = 12.4, 17.5, 19.8, 24.9, 32.0, 40.0, 43.4, 45.2, 62.6, 75.6, 84.7, 85.7, 88.0
POT_HITS = [25.75, 26.0, 26.25, 26.55, 26.8, 27.35]


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

# ---------------- Livestream: Austern ----------------
amb('fsd_party_music', 0, 10.0, -31)                                                       # leise Stream-Musik
for tt in [1.0, 4.6, 8.2]: add('fsd_notify', tt, 0.45, db=-26, fout=0.15, pan=0.4)          # Chat-Ping
add('fsd_slurp', 9.75, 1.5, db=-3, peak_win=0.4, fout=0.3)                                # er schlürft – Luft
add('fsd_chime', VANISH - 0.05, 1.3, db=-15, fout=0.6)                                     # Verschwinden
add('fsd_scratch', VANISH, 1.0, db=-5, fout=0.3)                                           # Plattenkratzer: Musik bricht ab
add('fsd_laugh', 11.2, 2.0, db=-15, fin=0.1, fout=0.6)                                     # Lacher
add('fsd_squeak', LEMON - 0.02, 0.5, db=-9, fout=0.1)                                       # Zitrone quietscht
add('fsd_scream_girl', LEMON + 0.15, 1.4, db=-11, speed=0.72, fout=0.4)                    # Aua, das Auge
add('fsd_laugh', 13.6, 3.2, db=-12, off=1.5, fin=0.2, fout=1.0)
for tt in [14.4, 15.4, 16.2]: add('fsd_notify', tt, 0.4, db=-28, fout=0.1, pan=0.4)
add('fsd_whoosh_fast', 16.75, 0.6, db=-12, fout=0.2)

# ---------------- Stufe 2: Abiball-Foto ----------------
amb('fsd_crowd_murmur', 17.0, FLASH + 0.1, -21)
amb('fsd_party_music', 17.0, FLASH + 0.1, -33)
add('fsd_chime', POP - 0.05, 0.9, db=-17, fout=0.4)
for k in range(5): add('fsd_squeak', POP + 0.04 + k * 0.07, 0.25, db=-15 - k, fout=0.05, pan=(k - 2) * 0.3)  # Hemden springen auf
add('fsd_crowd_gasp', POP + 0.35, 2.0, db=-10, fout=0.6)
add('fsd_giggle', POP + 0.8, 2.2, db=-11, fout=0.6, pan=-0.3)
add('fsd_teens_laugh', POP + 1.2, 2.3, db=-10, fout=0.6)
add('fsd_camera_click', FLASH - 0.02, 0.6, db=-2, fout=0.1)                                 # Klick – Foto
add('fsd_laugh', FLASH + 0.4, 3.4, db=-14, fin=0.3, fout=1.0)                              # eingefrorenes Foto
add('fsd_whoosh_fast', 23.75, 0.6, db=-12, fout=0.2)

# ---------------- Stufe 3: Muscheltöpfe ----------------
amb('fsd_restaurant', 24.0, 31.05, -17)
amb('fsd_city_day', 24.0, 31.05, -25)
add('fsd_chime', TRAY - 0.05, 0.9, db=-16, fout=0.4)
add('fsd_whoosh_fast', TRAY, 0.7, db=-6, fout=0.2)                                         # Tablett schießt hoch
add('fsd_crowd_gasp', TRAY + 0.35, 2.0, db=-10, fout=0.6)
for k, th in enumerate(POT_HITS):                                                          # Töpfe landen auf Köpfen
    add('fsd_clang', th - 0.01, 1.2, db=-4 - (k % 3) * 2 + (3 if k == 5 else 0), peak_win=0.1, fout=0.6, pan=[-0.5, -0.2, 0.1, 0.4, 0.0, 0.25][k], speed=[1.0, 1.12, 0.9, 1.2, 1.05, 0.85][k])
add('fsd_soft_thud', 28.3, 0.5, db=-10)                                                    # Tablett fällt
add('fsd_laugh', 27.7, 3.2, db=-13, off=0.5, fin=0.2, fout=1.0)
add('fsd_whoosh_fast', 30.75, 0.6, db=-12, fout=0.2)

# ---------------- Stufe 4: Watt ----------------
amb('fsd_wind', 31.0, 39.05, -15)
amb('fsd_seagulls', 31.0, 34.5, -22)
add('fsd_chime', SINK - 0.05, 0.9, db=-16, fout=0.4)
add('fsd_splash_big', SINK + 0.05, 2.0, db=-4, speed=0.55, peak_win=0.3, fout=0.8)        # Plumps in den Schlick
add('fsd_body_fall', SINK + 0.1, 0.6, db=-9, off=0.45, fout=0.2)
add('fsd_screams', SINK + 0.35, 2.2, db=-14, off=1.0, fin=0.05, fout=0.8)
add('fsd_splash_big', 33.6, 1.2, db=-14, speed=0.5, off=1.5, fout=0.5, pan=-0.3)          # Schmatzen
add('fsd_squeak', 34.1, 0.4, db=-15, speed=0.8, pan=0.3)                                    # Gummistiefel
add('fsd_seagulls', 34.6, 1.6, db=-9, peak_win=0.6, fout=0.4, pan=-0.4)                    # Möwe landet auf dem Kopf
add('fsd_laugh', 35.6, 2.4, db=-15, fin=0.2, fout=0.8)
add('fsd_wave_crash', 35.8, 3.4, db=-15, fin=1.2, fout=0.4)                                # Flut
add('fsd_helicopter', 35.6, 3.5, db=-21, fin=1.5, fout=0.3)
add('fsd_whoosh_fast', 38.75, 0.6, db=-12, fout=0.2)

# ---------------- Stufe 5: Kirchturm ----------------
amb('fsd_city_day', 39.0, 48.05, -20)
amb('fsd_crowd_murmur', 39.0, 43.2, -22)
add('fsd_chime', HOLES - 0.05, 0.9, db=-17, fout=0.4)
add('fsd_stone_clatter', HOLES + 0.2, 3.2, db=-10, fin=0.3, fout=0.8)                      # Gestein bröselt
add('fsd_debris', 41.5, 1.6, db=-16, fout=0.6, pan=-0.3)
add('fsd_sub_rumble', 41.0, 4.6, db=-10, off=1.0, fin=1.0, fout=0.3)
add('fsd_church_bell', 42.7, 2.6, db=-8, off=0.4, fout=0.6)                                # Glocke schlägt beim Kippen
add('fsd_crowd_gasp', 43.0, 2.0, db=-9, fout=0.6)
add('fsd_screams', 43.5, 2.5, db=-13, off=1.0, fin=0.1, fout=0.8)
add('fsd_footsteps_run', 43.6, 3.0, db=-15, fin=0.2, fout=0.8)
add('fsd_building_collapse', TOWER_HIT - 0.9, 3.4, db=0, fout=1.2)
add('fsd_impact_boom2', TOWER_HIT, 2.0, db=-4, fout=1.0)
add('fsd_rubble', TOWER_HIT + 0.1, 2.6, db=-5, fout=1.0)
add('fsd_debris', TOWER_HIT + 0.3, 1.6, db=-10, fout=0.6, pan=-0.4)
add('fsd_whoosh_fast', 47.6, 0.5, db=-14, fout=0.2)

# ---------------- Stufe 6: Muschelregen ----------------
add('fsd_whoosh_boom', RETURN - 0.05, 2.4, db=-6, speed=0.85, fout=1.0)
add('fsd_chime', RETURN - 0.5, 1.2, db=-14, fout=0.6)
amb('fsd_plastic_clatter', RETURN + 0.4, 58.05, -9)                                         # Muscheln prasseln
amb('fsd_gravel', RETURN + 0.6, 58.05, -15)
for tt, pn in [(49.1, -0.5), (50.4, 0.4), (51.9, -0.2), (53.3, 0.5), (55.0, -0.4), (56.6, 0.2)]: add('fsd_coins', tt, 0.8, db=-17, fout=0.3, pan=pn)
add('fsd_screams', 48.8, 2.4, db=-15, off=2.0, fin=0.2, fout=0.8)
add('fsd_car_horn', 50.6, 1.6, db=-16, fout=0.4, pan=0.5)                                  # Auto wird getroffen
add('fsd_glass_break', 51.3, 1.4, db=-13, peak_win=0.2, fout=0.5, pan=0.4)
add('fsd_crowd_gasp', 52.2, 2.0, db=-14, fout=0.6)
add('fsd_stone_clatter', 54.0, 3.6, db=-15, off=4.0, fin=0.3, fout=0.8)
add('fsd_whoosh_fast', 57.7, 0.5, db=-14, fout=0.2)

# ---------------- Stufe 7: Zurück im Stream ----------------
add('fsd_sigh', 58.6, 2.0, db=-7, fout=0.6)
for tt in [58.6, 59.6, 60.6, 61.4, 62.0]: add('fsd_notify', tt, 0.4, db=-27, fout=0.1, pan=0.4)
add('fsd_sub_rumble', 60.2, 2.6, db=-9, off=1.0, fin=2.0, fout=0.1)
add('fsd_glass_rattle', 60.6, 2.0, db=-15, fin=0.8, fout=0.2)                              # Regal klirrt
add('fsd_glass_break', WINDOW - 0.02, 1.6, db=0, peak_win=0.2, fout=0.6)                  # Fenster birst
add('fsd_whoosh_boom', WINDOW, 2.2, db=-6, fout=1.0)
amb('fsd_plastic_clatter', WINDOW + 0.05, 77.7, -5, off=0.5)                               # Muschelflut
amb('fsd_gravel', WINDOW + 0.2, 77.7, -10)
amb('fsd_stone_clatter', WINDOW + 0.3, 77.7, -13, off=2.0)
add('fsd_scream_girl', 63.0, 1.4, db=-9, speed=0.72, fout=0.4)
add('fsd_body_fall', 63.9, 0.6, db=-9, off=4.55, fout=0.2)
add('fsd_metal_crash', 64.0, 1.4, db=-13, peak_win=0.3, fout=0.6)                          # Stuhl kippt
for tt in [64.8, 65.6, 66.6, 67.4, 68.4, 69.3, 70.4, 71.6, 72.6, 73.6]: add('fsd_notify', tt, 0.35, db=-25, fout=0.1, pan=0.4)
add('fsd_scream_girl', 69.1, 1.2, db=-12, speed=0.75, fout=0.4)
add('fsd_metal_crash', 70.5, 1.6, db=-12, peak_win=0.3, fout=0.6, pan=0.4)                # Ringlicht kippt
add('fsd_scream_girl', 73.3, 1.6, db=-13, speed=0.7, fout=0.8)
add('fsd_sub_rumble', 75.0, 3.0, db=-12, off=1.0, fin=0.5, fout=0.3)
add('fsd_soft_thud', BURIED, 0.5, db=-12)
add('fsd_whoosh_fast', 77.7, 0.5, db=-14, fout=0.2)

# ---------------- Stufe 7: Luftbild ----------------
amb('fsd_wind', 78.0, 84.05, -13)
add('fsd_sub_rumble', 78.0, 6.0, db=-15, off=1.0, fin=0.4, fout=1.0)
add('fsd_helicopter', 78.5, 5.5, db=-22, fin=1.0, fout=1.0, pan=-0.4)
add('fsd_seagulls', 80.0, 3.0, db=-21, fout=0.8, pan=0.4)

# ---------------- Finale: Auster ----------------
amb('fsd_wind', 84.0, 90.0, -17)
add('fsd_plastic_clatter', HAND_UP - 0.05, 0.9, db=-11, fout=0.4)                          # Hand bricht durch
add('fsd_plastic_clatter', HEAD_UP - 0.05, 1.0, db=-9, off=1.5, fout=0.4)                 # Kopf taucht auf
add('fsd_gasp', HEAD_UP + 0.25, 1.4, db=-7, fout=0.4)                                      # tief Luft holen
add('fsd_slurp', 87.65, 1.4, db=-1, peak_win=0.4, fout=0.4)                                # endlich: Auster
add('fsd_applause', 88.35, 1.55, db=-14, fin=0.2, fout=0.8)
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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge11_muscheln.mp4')
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
