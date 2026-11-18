"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge02_sonne.mp4
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
VANISH, DARK, RETURN = 5.0, 18.0, 59.0
WK = [[18, 10], [24, 9.3], [31, 8.4], [39, 7.0], [45.5, 5.6], [52, 3.6], [58, 0.8], [59, 0]]


def world_left(T):
    if T <= WK[0][0]: return 10
    for i in range(1, len(WK)):
        if T <= WK[i][0]:
            a, va = WK[i - 1]; b, vb = WK[i]
            return va + (vb - va) * (T - a) / (b - a)
    return 0


def light_left(T):
    if T <= VANISH: return 500
    if T >= DARK: return 0
    a, b = VANISH, DARK - 3
    if T < b: u = (T - a) / (b - a); return 3 + 497 * (1 - u) ** 2.2
    return DARK - T


def amb(name, t0, t1, db, off=0.0, xf=0.8, speed=1.0):
    """Atmo über längere Strecken: Clip wiederholt mit Überblendung."""
    x = load(name)
    if x is None: return
    L = len(x) / SR / speed - off
    t = t0
    while t < t1:
        d = min(L, t1 - t + xf)
        add(name, t, d, db=db, off=off, fin=xf if t > t0 else 0.3, fout=xf, speed=speed)
        t += max(1.0, L - xf)


def tick(T, db):
    add('fsd_clock_tick', T - 0.005, 0.16, db=db, off=0.0, fout=0.05)


# ---------------- Strand ----------------
amb('fsd_beach_waves', 0, 3.55, -8)
amb('fsd_seagulls', 0, 3.55, -14)
add('fsd_beach_kids', 0, 3.5, db=-20, fin=0.2, fout=0.2)
amb('fsd_wind', 0, 3.55, -22, off=1.0)
amb('fsd_beach_waves', 11.5, 24.05, -7)
amb('fsd_seagulls', 11.5, 18.0, -13)
add('fsd_seagulls', 18.0, 2.5, db=-6, off=6, fin=0.02, fout=2.0)          # Möwen schrecken auf
amb('fsd_beach_kids', 11.5, 18.0, -18)
amb('fsd_wind', 11.5, 24.05, -20, off=1.0)
add('fsd_crowd_gasp', 18.25, 2.8, db=-6, fout=0.6)
add('fsd_screams', 19.2, 2.0, db=-24, off=1.0, fin=0.3, fout=1.0)
add('fsd_beach_kids', 20.5, 3.5, db=-26, fin=0.5, fout=0.5)

# ---------------- Weltall ----------------
amb('fsd_sub_rumble', 3.5, 11.55, -16, off=0.5)
add('fsd_whoosh_boom', 4.99, 3.0, db=4, fout=1.5)                         # Sonne verschwindet
add('fsd_sub_rumble', 5.0, 6.0, db=-6, off=6.0, fin=0.05, fout=2.0)
for s in [1, 2, 3, 4]: tick(s, -4)
# Lichtlaufzeit: Ticks im Zeitraffer (alle 20 s Restzeit), die letzten 3 Sekunden einzeln und laut
last = 500
for f in range(int(5 * 30), int(15 * 30)):
    v = light_left(f / 30)
    if int(v / 20) < int(last / 20): tick(f / 30, -14)
    last = v
for s in [15, 16, 17]: tick(s, 0)
add('fsd_sub_rumble', 14.5, 3.6, db=-10, off=1.0, fin=2.5, fout=0.05)    # Spannung bis zur Dunkelheit
add('fsd_whoosh_boom', 17.99, 3.0, db=3, fout=1.8)                        # Licht aus

# ---------------- Countdown der 10 Sekunden ----------------
ticks = []; last = 10
for f in range(int(DARK * 30), int(RETURN * 30) + 1):
    v = world_left(f / 30)
    if int(v * 10) < int(last * 10): ticks.append(f / 30)
    last = v
for T in ticks: tick(T, -12 + (4 if T > 52 else 0))

# ---------------- Stufe 2: Stadt im Dunkeln ----------------
amb('fsd_city_day', 24, 31.05, -16)
amb('fsd_crowd_murmur', 24, 31.05, -14)
add('fsd_birds_flap', 24.3, 1.5, db=-8, off=0.7, fout=0.3, pan=0.4)
add('fsd_car_horn', 25.6, 2.1, db=-14, off=1.8, fout=0.3, pan=-0.4)
add('fsd_dog_howl', 26.8, 4.2, db=-12, off=2.5, fin=0.3, fout=1.0, pan=0.5)
add('fsd_car_horn', 29.2, 1.0, db=-17, off=0.2, fout=0.2, pan=0.3)
add('fsd_crowd_gasp', 24.4, 2.0, db=-16, fout=0.6)

# ---------------- Stufe 3: Autobahn ----------------
amb('fsd_highway', 31, 39.05, -8)
add('fsd_tire_screech', 34.0, 2.0, db=-6, off=10.2, fin=0.05, fout=0.4, pan=0.0)   # Wagen vorn bremst
add('fsd_tire_screech', 34.9, 1.8, db=-8, off=10.3, fin=0.05, fout=0.4, pan=-0.3)
add('fsd_tire_screech', 35.55, 1.8, db=-1, off=10.2, fin=0.05, fout=0.3)            # eigene Vollbremsung
add('fsd_car_crash', 35.72 - 3.2, 4.0, db=-8, off=0.0, fin=2.9, fout=0.6, pan=-0.3) # nur Aufprallteil hörbar
add('fsd_car_crash', 36.10 - 3.2 + 3.2, 2.3, db=4, off=3.15, fout=0.8)             # eigener Aufprall
add('fsd_car_crash2', 36.12, 3.5, db=-2, off=1.7, fout=1.2, pan=0.3)
add('fsd_glass_break', 36.15, 2.5, db=-6, fout=0.8)
add('fsd_car_crash', 36.52, 2.0, db=-6, off=3.15, fout=0.8, pan=-0.4)
add('fsd_car_horn', 37.0, 2.1, db=-10, off=1.8, fout=0.4, pan=0.4)                 # Hupe klemmt

# ---------------- Stufe 4: Solarpark ----------------
amb('fsd_wind', 39, 45.55, -16, off=1.0)
amb('fsd_electric_hum', 39, 45.55, -14)
add('fsd_power_down', 41.3, 4.2, db=-10, off=12, fin=0.05, fout=1.0)
amb('fsd_alarm_beep', 41.55, 45.55, -14)

# ---------------- Stufe 5: Netz bricht zusammen ----------------
amb('fsd_electric_hum', 45.5, 49.95, -6)
amb('fsd_alarm_beep', 45.5, 49.95, -12)
for k in range(21):  # Leistungsschalter lösen aus
    ti = 45.5 + 1.2 + (k % 7) * 0.45 + (k // 7) * 0.2
    add('fsd_breaker', ti, 0.35, db=-12 - (k % 3) * 2, off=0.85, fout=0.1, pan=((k % 7) - 3) * 0.12)
for ta in [1.4, 2.6, 3.5, 4.25]:   # Lichtbögen
    add('fsd_electric_arc', 45.5 + ta, 0.45, db=-4, off=0.6, fin=0.005, fout=0.25)
add('fsd_power_down', 47.0, 3.0, db=-6, off=2, fin=0.5, fout=0.05)
add('fsd_whoosh_boom', 49.9, 3.0, db=0, speed=0.8, fout=1.5)               # alles aus
add('fsd_sub_rumble', 50.0, 8.0, db=-10, off=6.0, fin=0.3, fout=1.5)

# ---------------- Europa ----------------
add('fsd_sub_rumble', 52.0, 6.0, db=-12, off=1.0, fin=0.5, fout=0.5)

# ---------------- Stufe 6: Sonne zurück, Strom nicht ----------------
add('fsd_siren2', 58.0, 8.0, db=-18, fin=0.5, fout=0.6, pan=-0.4)
add('fsd_whoosh_boom', 58.98, 3.0, db=1, fout=1.5)
add('fsd_crowd_gasp', 59.2, 2.4, db=-10, fout=0.5)
amb('fsd_city_day', 59.2, 66.05, -18)
amb('fsd_crowd_murmur', 59.2, 66.05, -16)
add('fsd_birdsong', 60.0, 6.0, db=-22, fin=1.5, fout=0.5)
add('fsd_siren', 60.4, 5.6, db=-12, off=4.0, fin=0.4, fout=0.6)
add('fsd_car_horn', 62.2, 2.1, db=-14, off=1.8, fout=0.3, pan=0.4)

# ---------------- Stufe 7: Abends ohne Strom ----------------
amb('fsd_crickets', 66, 90, -20)
add('fsd_siren2', 66.5, 11.0, db=-24, off=5, fin=1.0, fout=1.0, pan=0.5)
add('fsd_alarm_beep', 67.8, 0.5, db=-12)                                  # Anruf fehlgeschlagen
add('fsd_alarm_beep', 68.3, 0.5, db=-12)
amb('fsd_crowd_murmur', 71.0, 78.05, -14)
amb('fsd_fire_crackle', 71.0, 78.05, -18)
add('fsd_generator', 71.0, 7.0, db=-24, fin=0.5, fout=0.5, pan=-0.6)
add('fsd_footsteps_run', 72.5, 4.0, db=-14, off=2.5, fin=0.2, fout=0.5, pan=0.4)
add('fsd_dog_howl', 74.5, 3.4, db=-18, off=3.0, fin=0.3, fout=1.0, pan=-0.5)
add('fsd_helicopter', 76.0, 14.0, db=-8, fin=2.5, fout=3.0)
amb('fsd_fire_crackle', 78.0, 90, -22)
add('fsd_siren', 79.0, 10.0, db=-20, fin=1.0, fout=2.5, pan=-0.3)
add('fsd_sub_rumble', 84.0, 6.0, db=-12, off=1.0, fin=2.0, fout=2.5)

# ---------------- Ausgabe ----------------
peak = np.abs(mix).max()
if peak > 0.98: mix *= 0.98 / peak
tmp = os.path.join(HERE, 'mix_roh.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', tmp], input=mix.tobytes(), check=True)
out = os.path.join(HERE, 'mix.wav')
# TikTok-Lautheit: ca. -14 LUFS, Spitzen begrenzt
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'acompressor=threshold=-30dB:ratio=3:attack=15:release=400:makeup=6,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.85:attack=2:release=60', '-ar', str(SR), '-c:a', 'pcm_s16le', out], check=True)
os.remove(tmp)
print('mix.wav fertig, Ticks:', len(ticks))

if '--mux' in sys.argv:
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge02_sonne.mp4')
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
