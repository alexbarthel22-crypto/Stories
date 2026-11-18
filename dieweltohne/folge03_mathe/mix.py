"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge03_mathe.mp4
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
VANISH, RETURN, ALARM = 10.0, 59.0, 56.0
WK = [[10, 10], [17, 9.3], [24, 8.5], [31, 7.6], [38, 6.6], [47, 4.6], [53, 2.6], [59, 0]]
TRAIN_HIT, ORBIT_HIT, COUNTER, IGNITION, LIFTOFF, FLASH0 = 35.8, 50.0, 71.5, 77.0, 78.2, 85.0
PLANE_WARN, PLANE_DIVE = 39.2, 42.5   # Cockpit: Hauptwarnung, Sturzflug


def world_left(T):
    if T <= WK[0][0]: return 10
    for i in range(1, len(WK)):
        if T <= WK[i][0]:
            a, va = WK[i - 1]; b, vb = WK[i]
            return va + (vb - va) * (T - a) / (b - a)
    return 0


def amb(name, t0, t1, db, off=0.0, xf=0.8, speed=1.0, seg=None):
    """Atmo über längere Strecken: Clip (ab off, Länge seg) wiederholt mit Überblendung."""
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


# ---------------- Einstieg: Klassenzimmer ----------------
amb('fsd_classroom', 0, 10.05, -22, off=5.0, seg=13.0)
amb('fsd_classroom2', 0, 10.05, -26)
for k, tt in enumerate([0.6, 1.0, 1.3, 1.8]): add('fsd_keyboard', tt, 0.12, db=-16, off=1.0 + k * 0.6, fout=0.05)   # Tasten am Handy
add('fsd_pencil', 3.5, 6.5, db=-20, off=2.0, fin=0.3, fout=0.3, pan=0.3)
add('fsd_chalk', 4.2, 1.8, db=-10, fout=0.3, pan=-0.2)
add('fsd_chalk', 6.6, 1.8, db=-11, fout=0.3, pan=-0.2)
for s_ in range(1, 10): tick(s_, -6 if s_ < 7 else 0)
add('fsd_sub_rumble', 7.0, 3.05, db=-10, off=1.0, fin=2.5, fout=0.05)

# ---------------- Stufe 1: Mathe weg ----------------
add('fsd_whoosh_boom', 9.99, 3.0, db=2, fout=1.5)
add('fsd_glitch', 10.0, 1.4, db=-2, off=6.5, fin=0.005, fout=0.3)
add('fsd_glitch2', 10.0, 1.0, db=-6, fout=0.3)
add('fsd_chalk_screech', 10.15, 0.7, db=-8, fout=0.2)
amb('fsd_glitch', 10.8, 17.05, -24, off=7.0, seg=9.0)
add('fsd_kids_cheer', 10.95, 4.0, db=-3, fout=0.8)
add('fsd_kids_cheer2', 11.5, 5.5, db=-7, fin=0.1, fout=1.0, pan=0.3)
amb('fsd_classroom2', 11.0, 17.05, -14)

# ---------------- Countdown der 10 Sekunden ----------------
ticks = []; last = 10
for f in range(int(VANISH * 30), int(RETURN * 30) + 1):
    v = world_left(f / 30)
    if int(v * 10) < int(last * 10): ticks.append(f / 30)
    last = v
for T in ticks: tick(T, -14 + (4 if T > 53 else 0))

# ---------------- Stufe 2: Stadt, Bildschirme ----------------
amb('fsd_city_day', 17, 31.05, -16)
amb('fsd_crowd_murmur', 17, 24.05, -16)
amb('fsd_glitch', 17, 24.05, -16, off=7.0, seg=9.0)
add('fsd_static', 17.0, 5.0, db=-14, fin=0.05, fout=0.5, pan=-0.4)
for k, tt in enumerate([17.6, 18.9, 20.2, 21.6, 22.8]): add('fsd_phone_buzz', tt, 1.3, db=-20, off=0.25, fout=0.2, pan=(-1) ** k * 0.5)
add('fsd_car_horn', 20.8, 1.2, db=-16, off=0.2, fout=0.2, pan=-0.4)
add('fsd_crowd_gasp', 18.0, 2.0, db=-16, fout=0.6)

# ---------------- Stufe 3: Konto und Börse ----------------
amb('fsd_city_day', 24, 31.05, -20)
amb('fsd_crowd_murmur', 24, 31.05, -20)
add('fsd_phone_buzz', 24.4, 1.3, db=-10, off=0.25, fout=0.2)
add('fsd_glitch', 25.0, 1.6, db=-12, off=11.0, fin=0.02, fout=0.2)
add('fsd_alarm_beep', 26.6, 1.0, db=-8)                                           # Konto gesperrt
add('fsd_register_bell', 27.4, 1.5, db=-10, off=0.3, fout=0.8)
add('fsd_sub_rumble', 27.6, 3.45, db=-8, off=1.0, fin=0.6, fout=0.05)
amb('fsd_alarm_beep', 28.0, 31.05, -16)
add('fsd_crowd_gasp', 28.5, 2.0, db=-14, fout=0.6)

# ---------------- Stufe 4: Zug ----------------
amb('fsd_wind', 31, 38.05, -20, off=1.0)
amb('fsd_birdsong', 31, 33.5, -22)
amb('fsd_train_rumble', 31, TRAIN_HIT + 0.05, -10)
add('fsd_train_pass', TRAIN_HIT - 3.5, 3.5, db=-6, off=1.5, fin=2.0, fout=0.03)
add('fsd_train_horn', 32.6, 2.2, db=-6, fout=0.4, pan=-0.4)
add('fsd_train_horn', 33.6, 2.2, db=-8, fout=0.4, pan=0.4)
add('fsd_train_brake', 34.0, TRAIN_HIT - 34.0 + 0.1, db=-4, off=4.0, fin=0.1, fout=0.05)
add('fsd_metal_crash', TRAIN_HIT - 0.02, 3.0, db=4, peak_win=0.2, fout=1.0)
add('fsd_metal_crash2', TRAIN_HIT + 0.1, 3.0, db=0, peak_win=0.2, fout=1.0, pan=0.3)
add('fsd_car_crash', TRAIN_HIT + 0.05, 2.3, db=-2, off=3.15, fout=0.8, pan=-0.3)
add('fsd_glass_break', TRAIN_HIT + 0.05, 2.5, db=-6, fout=0.8)
add('fsd_impact_boom2', TRAIN_HIT, 2.5, db=-6, fout=1.5)
add('fsd_electric_arc', TRAIN_HIT + 0.3, 0.6, db=-8, off=0.6, fout=0.3)     # Oberleitung reißt
add('fsd_train_brake', TRAIN_HIT + 0.2, 2.0, db=-10, off=6.0, fout=0.8)

# ---------------- Stufe 5: Cockpit ----------------
amb('fsd_jet_cabin', 38, 47.0, -8)
add('fsd_jet_roar', 38.0, 9.0, db=-18, fin=0.5, fout=0.05)
amb('fsd_cockpit_alarm', PLANE_WARN, 47.0, -8, seg=9.0)
add('fsd_glitch', 39.0, 1.0, db=-12, off=12.0, fin=0.02, fout=0.2)
add('fsd_wind_rush', PLANE_DIVE, 47.0 - PLANE_DIVE, db=-6, fin=3.0, fout=0.03)
add('fsd_jet_flyby2', PLANE_DIVE + 0.5, 47.0 - PLANE_DIVE - 0.5, db=-6, off=1.0, fin=2.0, fout=0.03)
amb('fsd_alarm_beep', PLANE_DIVE, 47.0, -10)

# ---------------- Stufe 6: Satelliten (im All: nur dumpfe Körperschall-Geräusche) ----------------
add('fsd_impact_boom2', 46.98, 2.0, db=-12, fout=1.0)                          # Ende Sturzflug, harter Schnitt
amb('fsd_sub_rumble', 47.0, 53.05, -14)
amb('fsd_electric_hum', 47.0, 53.05, -22)
for k, tt in enumerate([47.6, 48.3, 48.9, 49.4]): add('fsd_static', tt, 0.35, db=-16, off=0.5 + k * 0.7, fout=0.1)  # Düsen zünden
add('fsd_whoosh_boom', ORBIT_HIT - 0.02, 3.0, db=0, speed=0.75, fout=1.5)
add('fsd_debris', ORBIT_HIT + 0.02, 2.0, db=-8, peak_win=0.2, fout=1.0)
add('fsd_glass_break', ORBIT_HIT + 0.05, 2.0, db=-12, speed=0.7, fout=1.0)

# ---------------- Stufe 7: Bunker ----------------
amb('fsd_electric_hum', 53, 66.05, -20)
add('fsd_keyboard', 53.0, 3.0, db=-16, off=1.0, fin=0.2, fout=0.2, pan=0.3)
add('fsd_printer', 53.2, 2.8, db=-18, off=11.5, fin=0.2, fout=0.2, pan=-0.4)
add('fsd_static', 53.0, 3.0, db=-20, fin=0.2, fout=0.2)
for tt in [53.4, 55.0]: add('fsd_radar_ping', tt, 1.6, db=-14, speed=0.5, fout=0.8)
add('fsd_whoosh_boom', ALARM - 0.01, 3.0, db=1, fout=1.5)
amb('fsd_klaxon', ALARM, 66.05, -6, seg=8.0)
amb('fsd_klaxon2', ALARM, 76.0, -14)
add('fsd_air_raid2', ALARM + 0.3, 9.3, db=-14, fin=0.5, fout=1.5, pan=0.3)
add('fsd_crowd_gasp', ALARM + 0.2, 2.0, db=-12, fout=0.6)
add('fsd_footsteps_run', 57.0, 3.0, db=-16, off=2.5, fin=0.2, fout=0.5)
add('fsd_phone_ring', 57.6, 6.0, db=-10, off=0.75, fin=0.02, fout=0.4, pan=-0.3)
add('fsd_glitch2', RETURN - 0.02, 0.6, db=-8, fout=0.2)                           # Mathe zurück
add('fsd_printer', 59.6, 3.0, db=-14, off=11.5, fin=0.1, fout=0.3, pan=0.4)

# ---------------- Rückblick 1983, Gegenschlag ----------------
amb('fsd_sub_rumble', 66, 76.05, -14)
add('fsd_air_raid', 66.0, 10.0, db=-12, off=3.0, fin=1.0, fout=1.0)
for k in range(5): add('fsd_radar_ping', 66.2 + k * 0.45, 1.8, db=-12, speed=0.55, fout=1.0, pan=(k - 2) * 0.2)
for tt in [68.0, 70.0]: add('fsd_radar_ping', tt, 1.6, db=-18, speed=0.5, fout=1.0)
add('fsd_whoosh_boom', COUNTER - 0.02, 3.0, db=1, fout=1.5)
add('fsd_air_raid2', COUNTER + 0.2, 4.3, db=-8, off=4.5, fin=0.3, fout=0.8)
for k in range(10): add('fsd_radar_ping', COUNTER + 0.2 + k * 0.22, 1.2, db=-14, speed=0.6, fout=0.6, pan=((k % 5) - 2) * 0.2)

# ---------------- Raketenstart ----------------
add('fsd_klaxon2', 76.0, 1.4, db=-8, fout=0.2)
add('fsd_sub_rumble', 76.0, 1.2, db=-8, off=1.0, fin=0.2, fout=0.1)                # Silodeckel
add('fsd_breaker', 76.95, 0.4, db=-4, off=0.85, fout=0.1)
add('fsd_rocket_ignite', IGNITION - 0.02, 2.5, db=2, peak_win=0.3, fout=1.0)
add('fsd_rocket_roar', IGNITION + 0.2, 84.0 - IGNITION - 0.2, db=0, fin=1.0, fout=0.05)
add('fsd_jet_roar', LIFTOFF - 0.3, 84.0 - LIFTOFF + 0.3, db=-6, fin=0.4, fout=0.05)
add('fsd_impact_boom', LIFTOFF - 0.02, 4.0, db=-4, fout=2.0)
add('fsd_thunder_far', 80.5, 3.5, db=-10, off=2.5, fin=0.3, fout=1.0, pan=0.5)              # zweite Rakete in der Ferne

# ---------------- Finale ----------------
amb('fsd_wind', 84.0, 90.0, -18, off=1.0)
for k in range(8): add('fsd_thunder_far' + ('2' if k % 2 else ''), FLASH0 + k * 0.55, 2.5, db=-8 - k * 0.5, fin=0.05, fout=1.2, pan=((k % 3) - 1) * 0.5)
add('fsd_impact_boom', FLASH0, 5.0, db=-6, fout=3.0)
add('fsd_sub_rumble', 85.5, 4.45, db=-6, off=1.0, fin=0.5, fout=2.0)

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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge03_mathe.mp4')
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
