"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge12_schwerkraft.mp4
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
VANISH, RETURN = 10.0, 55.0
WK = [[10, 10], [17, 9.0], [24, 7.8], [31, 6.4], [39, 4.6], [47, 2.4], [55, 0]]
SAUCE_HIT, JUMP, BONK, BOMB, BUMP = 14.3, 17.9, 20.3, 25.2, 32.4
BUS_SPLASH, GYM_LAND, POOL_LAND, CRASH, CRACK, PUD = 56.2, 59.4, 62.6, 64.6, 73.4, 86.2


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
for tt in ticks: tick(tt, -9 if tt < 7 or (VANISH < tt < 52) else -3)

# ---------------- Mensa (0–17) ----------------
amb('fsd_restaurant', 0.0, VANISH + 0.3, -17)
amb('fsd_crowd_murmur2', 0.0, VANISH + 0.3, -23)
for tt, pn in [(1.2, -0.4), (2.9, 0.3), (4.4, -0.2), (6.1, 0.5), (7.6, -0.5), (8.4, 0.2)]: add('fsd_spoon_clink', tt, 0.5, db=-19, fout=0.2, pan=pn)
add('fsd_slurp', 8.75, 0.9, db=-9, fout=0.3)                                               # er saugt schon vor
add('fsd_chime', VANISH - 0.05, 1.4, db=-13, fout=0.7)
add('fsd_whoosh_fast', VANISH, 0.9, db=-12, speed=0.6, fout=0.4)                            # alles hebt ab
add('fsd_boing', VANISH + 0.15, 0.8, db=-12, fout=0.3)                                     # Gabel fliegt weg
add('fsd_crowd_gasp', VANISH + 0.5, 2.0, db=-10, fout=0.7)
add('fsd_squeak', 11.0, 0.4, db=-17, pan=-0.3)
add('fsd_giggle', 11.4, 1.6, db=-15, fout=0.5, pan=0.4)
add('fsd_teens_laugh', 11.9, 1.6, db=-17, fin=0.1, fout=0.6, pan=-0.3)
add('fsd_soft_thud', 12.8, 0.4, db=-12)                                                   # Teller angestoßen
add('fsd_whoosh_fast', 13.0, 0.9, db=-12, fout=0.3)                                        # Soße fliegt
add('fsd_splash2', SAUCE_HIT - 0.02, 0.5, db=-6, peak_win=0.2, fout=0.2)                  # Klatsch ins Gesicht
add('fsd_gasp', SAUCE_HIT + 0.2, 1.0, db=-11, fout=0.3)
add('fsd_teens_laugh', SAUCE_HIT + 0.4, 2.4, db=-9, fin=0.05, fout=0.8)
add('fsd_laugh', SAUCE_HIT + 0.9, 1.6, db=-15, fout=0.6, pan=0.4)
add('fsd_shout_hey', 15.4, 0.9, db=-15, fout=0.3, pan=-0.4)
add('fsd_kid_laugh', 15.7, 1.2, db=-17, fout=0.4, pan=0.5)
add('fsd_whoosh_fast', 16.75, 0.6, db=-12, fout=0.2)

# ---------------- Turnhalle (17–24) ----------------
amb('fsd_classroom2', 17.0, 24.05, -24)
add('fsd_referee_whistle', 17.05, 0.7, db=-9, peak_win=0.4, fout=0.2)
for tt in [17.1, 17.45, 17.75]: add('fsd_basketball', tt, 0.3, db=-11, peak_win=0.15, fout=0.1)
add('fsd_squeak', JUMP - 0.1, 0.35, db=-13)                                               # Turnschuh beim Absprung
add('fsd_whoosh_fast', JUMP, 0.8, db=-10, fout=0.3)
add('fsd_crowd_gasp', 18.7, 1.8, db=-11, fout=0.6)
add('fsd_giggle', 19.4, 1.4, db=-15, fout=0.4, pan=0.3)
add('fsd_crash_thud', BONK - 0.02, 0.9, db=-4, peak_win=0.3, fout=0.4)                     # Kopf an die Decke
add('fsd_metal_crash', BONK + 0.02, 1.0, db=-14, peak_win=0.3, fout=0.5)
add('fsd_teens_laugh', BONK + 0.4, 2.6, db=-8, fin=0.05, fout=0.8)
for k, tt in enumerate([21.3, 21.8, 22.4, 23.0]): add('fsd_camera_click', tt, 0.3, db=-15 - k, pan=[-0.5, 0.4, -0.2, 0.5][k])
add('fsd_kids_cheer', 22.3, 1.6, db=-15, fin=0.2, fout=0.6)
add('fsd_whoosh_fast', 23.75, 0.6, db=-12, fout=0.2)

# ---------------- Freibad (24–31) ----------------
amb('fsd_beach_kids', 24.0, 31.05, -22)
add('fsd_flood_rush', 24.0, 7.0, db=-24, speed=0.55, fin=0.8, fout=0.8)                     # schwebendes, glucksendes Wasser
add('fsd_crowd_gasp', 24.6, 1.6, db=-15, fout=0.5, pan=-0.3)
amb('fsd_crowd_outdoor', 24.0, 31.05, -26)
add('fsd_shout_hey', BOMB - 0.45, 0.9, db=-8, fout=0.3)                                    # „ARSCHBOMBE!“
add('fsd_whoosh_fast', BOMB, 0.9, db=-9, fout=0.3)
add('fsd_gasp', 26.0, 1.0, db=-10, fout=0.3)                                             # er sieht die leeren Fliesen
add('fsd_wind_rush', 26.2, 3.2, db=-19, fin=0.8, fout=0.8)
add('fsd_crowd_gasp', 26.6, 2.0, db=-11, fout=0.6)
add('fsd_referee_whistle', 27.3, 0.9, db=-11, peak_win=0.5, fout=0.3, pan=0.5)             # Bademeister pfeift
add('fsd_scream_man', 28.3, 1.2, db=-10, peak_win=1.0, fout=0.4, speed=1.1)
add('fsd_kid_laugh', 29.6, 1.3, db=-15, fout=0.4, pan=-0.4)
add('fsd_whoosh_fast', 30.75, 0.6, db=-12, fout=0.2)

# ---------------- Schulbus (31–39) ----------------
add('fsd_bus_engine', 31.0, BUMP + 0.1, db=-10, fin=0.3, fout=0.1)
add('fsd_car_pass', 31.1, 1.6, db=-18, fout=0.5, pan=0.5)
add('fsd_thud2', BUMP - 0.02, 0.6, db=-4, peak_win=0.3, fout=0.2)                          # Bodenwelle
add('fsd_crash_thud', BUMP + 0.03, 0.6, db=-13, peak_win=0.3, fout=0.3)
add('fsd_bus_engine', BUMP + 0.1, 3.4, db=-12, off=2.0, speed=1.3, fout=1.2)               # Räder drehen frei hoch
add('fsd_screams', 33.0, 2.6, db=-11, off=1.0, fin=0.1, fout=0.8)
add('fsd_car_horn', 34.2, 1.2, db=-15, fout=0.4, pan=-0.5)
add('fsd_wind_rush', 35.4, 3.5, db=-15, fin=0.6, fout=0.4)
add('fsd_kids_cheer', 36.8, 1.6, db=-20, fout=0.5, pan=0.3)
add('fsd_whoosh_fast', 38.75, 0.6, db=-12, fout=0.2)

# ---------------- Weltall (39–55) ----------------
add('fsd_sub_rumble', 39.0, 8.2, db=-17, fin=1.0, fout=0.5)
add('fsd_electric_hum', 39.0, 8.0, db=-30, fin=1.0, fout=0.8)
add('fsd_chime', 39.2, 1.6, db=-17, fout=0.8)
add('fsd_canyon_wind', 43.0, 4.2, db=-16, speed=0.6, fin=1.2, fout=0.4)                    # Luft entweicht
add('fsd_sub_rumble', 47.0, 8.1, db=-10, off=1.0, fin=0.5, fout=0.2)
add('fsd_fire_roar', 48.5, 6.6, db=-17, speed=0.6, fin=1.5, fout=0.3)                      # Magma
add('fsd_heartbeat', 50.6, 4.3, db=-9, fin=0.6, fout=0.2)
add('fsd_stone_clatter', 51.8, 3.0, db=-16, fin=0.4, fout=0.4)
add('fsd_glass_rattle', 53.0, 2.0, db=-17, fin=0.8, fout=0.1)
add('fsd_whoosh_boom', 54.5, 1.4, db=-10, speed=0.8, fout=0.4)

# ---------------- Schwerkraft zurück (55–64) ----------------
add('fsd_impact_boom2', RETURN - 0.02, 1.8, db=-5, fout=0.8)
add('fsd_screams', 55.2, 1.4, db=-9, off=2.0, fin=0.05, fout=0.4)
add('fsd_wind_rush', 55.3, 1.0, db=-12, fout=0.2)
add('fsd_rain_heavy', 55.3, 2.9, db=-8, fin=0.4, fout=0.3)                                    # Flusswasser prasselt zurück
add('fsd_splash_big', BUS_SPLASH - 0.03, 1.8, db=0, peak_win=0.3, fout=0.8)               # Bus fällt in den Fluss
add('fsd_wave_crash', BUS_SPLASH + 0.5, 1.4, db=-12, fout=0.6)
add('fsd_scream_man', 58.4, 1.0, db=-9, peak_win=1.0, fout=0.2)                            # „AAAH“
add('fsd_whoosh_fast', 58.7, 0.7, db=-11, fout=0.2)
add('fsd_soft_thud', GYM_LAND - 0.02, 0.6, db=-1)                                          # Bauchklatscher auf die Matte
add('fsd_body_fall', GYM_LAND, 0.5, db=-10, off=0.45, fout=0.2)
add('fsd_kids_cheer', GYM_LAND + 0.4, 1.6, db=-12, fin=0.1, fout=0.6)
add('fsd_applause', 60.0, 1.0, db=-17, fin=0.2, fout=0.5)
add('fsd_rain_heavy', 61.2, 2.9, db=-6, off=3.0, fin=0.3, fout=0.4)                          # Beckenwasser als Platzregen
add('fsd_rain_street', 61.4, 2.6, db=-14, fin=0.4, fout=0.4)
add('fsd_scream_man', 61.1, 1.2, db=-11, peak_win=1.0, speed=1.15, fout=0.3)
add('fsd_whoosh_fast', 61.6, 1.0, db=-11, speed=0.8, fout=0.2)
add('fsd_splash_big', POOL_LAND - 0.03, 1.4, db=-3, peak_win=0.3, speed=1.15, fout=0.6)  # Planschbecken
add('fsd_kid_laugh', 63.0, 1.0, db=-12, fout=0.3)

# ---------------- Das große Beben (64–80) ----------------
add('fsd_sub_rumble', 63.6, 1.1, db=-12, fin=0.8, fout=0.1)
add('fsd_impact_boom', CRASH - 0.03, 2.4, db=0, fout=1.0)
add('fsd_explosion', CRASH + 0.05, 2.6, db=-5, peak_win=0.5, fout=1.0)
add('fsd_thunder', CRASH + 0.3, 3.4, db=-9, fout=1.2)
add('fsd_sub_rumble', CRASH + 0.2, 7.6, db=-7, off=0.5, fin=0.3, fout=1.0)
add('fsd_rubble', 66.0, 2.6, db=-12, fout=0.8)
add('fsd_fire_roar', 67.5, 4.6, db=-15, fin=0.8, fout=0.6)
add('fsd_building_collapse', 69.0, 3.0, db=-11, speed=0.85, fout=1.0)
add('fsd_whoosh_fast', 71.75, 0.5, db=-13, fout=0.2)
amb('fsd_dust_wind', 72.0, 80.05, -20)
amb('fsd_siren_eu', 72.3, 80.05, -24)
add('fsd_sub_rumble', 72.0, 8.0, db=-9, off=1.0, fin=0.5, fout=0.6)
for tt, pn in [(72.4, -0.3), (72.9, 0.3)]: add('fsd_stone_clatter', tt, 0.6, db=-17, fout=0.2, pan=pn)  # Knirschen vor dem Riss
add('fsd_impact_boom2', CRACK - 0.05, 2.2, db=-5, speed=0.8, fout=1.0)                    # Riss geht auf
add('fsd_rubble', CRACK + 0.05, 2.8, db=-4, fout=1.0)                                       # Brechen der Platten
add('fsd_metal_crash2', CRACK + 0.3, 1.2, db=-14, peak_win=0.3, fout=0.5, pan=0.3)          # Rohr bricht
add('fsd_stone_clatter', CRACK + 0.8, 2.4, db=-10, fin=0.1, fout=0.8)                       # Brocken fallen in den Spalt
for tt, pn in [(75.2, -0.4), (76.1, 0.4), (77.3, -0.2), (78.6, 0.3)]: add('fsd_gravel', tt, 0.9, db=-15, fin=0.05, fout=0.4, pan=pn)   # Rieseln
add('fsd_debris', 75.0, 1.6, db=-12, fout=0.6, pan=-0.3)
add('fsd_car_horn', 76.4, 1.4, db=-18, fout=0.4, pan=0.5)
add('fsd_screams', 76.8, 2.4, db=-18, off=1.0, fin=0.2, fout=0.8)
add('fsd_kids_cheer', 77.8, 1.4, db=-21, fout=0.4, pan=-0.4)                             # Kinder auf dem Busdach
add('fsd_thunder_far', 78.0, 2.0, db=-14, fout=0.8)
add('fsd_whoosh_fast', 79.75, 0.5, db=-13, fout=0.2)

# ---------------- Finale: Mensa, Pudding ----------------
amb('fsd_dust_wind', 80.0, 90.0, -27)
add('fsd_sigh', 80.6, 1.6, db=-9, fout=0.5)
add('fsd_static', 81.4, 0.35, db=-20, fout=0.1)                                            # Lampe flackert
add('fsd_static', 82.7, 0.3, db=-21, fout=0.1)
add('fsd_glass_rattle', 81.8, 1.2, db=-22, fout=0.4)
add('fsd_debris', 83.0, 0.9, db=-21, fout=0.4, pan=0.4)
add('fsd_whoosh_fast', PUD - 0.75, 0.8, db=-10, speed=1.2, fout=0.1)                       # Pudding fällt
add('fsd_soft_thud', PUD - 0.02, 0.4, db=-6)                                               # genau in die Hand
add('fsd_chime', PUD + 0.05, 1.4, db=-15, fout=0.7)
add('fsd_spoon_clink', 87.3, 0.5, db=-11, fout=0.2)
add('fsd_slurp', 87.6, 0.8, db=-7, fout=0.2)
add('fsd_giggle', 88.4, 1.3, db=-16, fout=0.5, pan=-0.3)
# ---------------- Ausgabe ----------------
peak = np.abs(mix).max()
if peak > 0.98: mix *= 0.98 / peak
tmp = os.path.join(HERE, 'mix_roh.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', tmp], input=mix.tobytes(), check=True)
out = os.path.join(HERE, 'mix.wav')
# TikTok-Lautheit: ca. -14 LUFS, Spitzen begrenzt
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'acompressor=threshold=-30dB:ratio=3:attack=15:release=400:makeup=6,loudnorm=I=-13.5:TP=-1.5:LRA=11,alimiter=limit=0.8:attack=1:release=60:level=false', '-ar', str(SR), '-c:a', 'pcm_s16le', out], check=True)
os.remove(tmp)
print('mix.wav fertig, Ticks:', len(ticks))

if '--mux' in sys.argv:
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge12_schwerkraft.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', out, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-t', '90', '-movflags', '+faststart', fin], check=True)
    print('fertig:', fin)

# Quellenangaben für die Videobeschreibung
cred = []
for f in sorted(os.listdir(RAW)):
    if f.endswith('.json') and f[:-5] in _cache and _cache[f[:-5]] is not None:
        m = json.load(open(os.path.join(RAW, f)))
        src = 'Freesound, über den Datensatz FSD50K' if m['artist'].startswith('Freesound') else 'Wikimedia Commons'
        cred.append(f"- {m['title'][5:]} – {m['license']} ({src})")
open(os.path.join(HERE, 'quellen_geraeusche.md'), 'w').write('# Geräusche (echte Aufnahmen)\n\nAlle Geräusche sind echte Aufnahmen unter CC0 (frei nutzbar, keine Namensnennung nötig).\n\n' + '\n'.join(cred) + '\n')
