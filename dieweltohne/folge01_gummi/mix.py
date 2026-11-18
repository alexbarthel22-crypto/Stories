"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge01_gummi.mp4
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
        _cache[name] = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
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
WK = [[5, 10], [10, 9.3], [14.5, 8.8], [20, 8.2], [26.5, 7.5], [32.5, 6.8], [41.5, 5.6], [47, 4.8], [54, 3.6], [61, 2.4], [66.5, 1.2], [70, 0]]


def world_left(T):
    if T <= WK[0][0]: return 10
    for i in range(1, len(WK)):
        if T <= WK[i][0]:
            a, va = WK[i - 1]; b, vb = WK[i]
            return va + (vb - va) * (T - a) / (b - a)
    return 0


ticks = []; last = 10
for f in range(150, 2101):
    v = world_left(f / 30)
    if int(v * 10) < int(last * 10): ticks.append(f / 30)
    last = v


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


# ---------------- Atmosphäre ----------------
amb('fsd_rain_heavy', 0, 10.2, -11, off=3)
amb('fsd_traffic', 0, 5.2, -12)
add('fsd_crowd', 4.2, 5.8, db=-15, fin=0.3)
amb('fsd_rain_heavy', 10, 14.5, -19, off=3)                 # Gummibärchen: drinnen
amb('fsd_rain_heavy', 14.5, 26.5, -12, off=3)
add('fsd_crowd', 14.5, 5.5, db=-21, off=5)
amb('fsd_rain_heavy', 26.5, 32.6, -4, off=3)                 # Handy ganz nah im Regen
amb('fsd_rain_heavy', 32.5, 41.5, -19, off=3)
amb('fsd_rain_heavy', 41.5, 47, -34, off=3)                 # Küche
amb('fsd_rain_heavy', 47, 54, -18, off=3)
amb('fsd_rain_heavy', 54, 61, -26, off=3)
add('fsd_thunder', 66.5, 3.6, db=-4, off=2, speed=0.6, fin=0.3, fout=0.4)  # Grollen über der Erde
amb('fsd_rain_heavy', 70, 90, -14, off=3)
amb('fsd_fire', 70, 90, -8)

# ---------------- Stadt ----------------
amb('fsd_city_hum', 0, 5.4, -10)                                              # Verkehr läuft noch
add('fsd_car_pass', 0.3, 4.6, db=-8, peak_win=3, fin=0.3, fout=0.4, pan=-0.4)
add('fsd_bus', 1.5, 3.6, db=-16, fin=0.6, fout=0.5, pan=0.5)
add('fsd_bell', 2.4, 0.3, db=-18, pan=0.6)
add('fsd_crowd2', 0, 5.3, db=-18, fin=0.3, fout=0.3)
amb('fsd_city_hum', 5.0, 10.2, -16)                                           # danach: Stadt verstummt nicht ganz
amb('fsd_crowd2', 4.2, 10.0, -16)
add('fsd_bus_brake', 6.0, 4.0, db=-17, off=2, fin=0.3, fout=0.8, pan=-0.5)
amb('fsd_city_hum', 14.5, 26.5, -17)
amb('fsd_crowd2', 14.5, 20.0, -17)
add('fsd_dog', 21.0, 5.5, db=-24, fin=0.3, fout=1.0, pan=0.6)
amb('fsd_crowd', 20.0, 26.5, -18)
amb('fsd_city_hum', 32.5, 41.5, -18)
amb('fsd_crowd2', 32.5, 41.5, -19)
add('fsd_horn1', 34.8, 1.6, db=-15, pan=-0.6)
add('fsd_horn3', 37.0, 1.6, db=-17, pan=0.5)
add('fsd_horn1', 40.2, 1.6, db=-13, pan=0.3)
amb('fsd_city_hum', 47, 54, -18)
amb('fsd_crowd2', 47, 51.2, -18)
add('fsd_dog', 51.5, 2.5, db=-18, off=8, fin=0.1, fout=0.8, pan=-0.6)
amb('fsd_city_hum', 70, 90, -20)
add('fsd_horn3', 71.2, 1.6, db=-15, pan=0.5)

# ---------------- Countdown-Ticks ----------------
clock = load('fsd_clock')
if clock is not None:
    on = onsets(clock, 0.4)
    tick_off = on[3] if len(on) > 3 else 0
    for s in [1, 2, 3, 4]: add('fsd_clock', s - 0.005, 0.14, db=-2, off=tick_off - 0.005, fout=0.04)
    for T in ticks: add('fsd_clock', T, 0.14, db=-8 + (5 if T > 66.5 else 0), off=tick_off - 0.005, fout=0.04)

# ---------------- Stufe 1: harmlos ----------------
add('fsd_thunder', 4.98, 3.0, db=-1, peak_win=0.4, fout=2.0)      # Moment des Verschwindens
add('fsd_gasp', 5.35, 1.6, db=-15, fout=0.4)
add('fsd_crinkle', 10.15, 3.5, db=-3, fin=0.05, fout=0.6)
# ---------------- Stufe 2: peinlich ----------------
add('fsd_gasp', 15.4, 1.8, db=-14, fout=0.5)                                 # erschrockenes Luftholen statt Gelächter
# ---------------- Stufe 3: schmerzhaft ----------------
for i in range(6):
    hit = 20 + 3.0 + i * 0.32 + (i % 2) * 0.25 + 0.56
    add('fsd_thud2', hit, 0.45, db=-1 - i, peak_win=0.2, fout=0.2, pan=(i % 3 - 1) * 0.4)
add('fsd_gasp', 23.3, 2.0, db=-9, fout=0.5)
# ---------------- Stufe 4: teuer ----------------
add('fsd_ebuzz', 30.3, 0.6, db=-14, fin=0.2)
add('fsd_ebuzz', 30.9, 0.6, db=-9)
add('fsd_ebuzz', 31.45, 0.25, db=-4, fout=0.02)
# ---------------- Stufe 5: gefährlich ----------------
add('fsd_screech', 32.5, 6.0, db=-5, peak_win=2.0, fin=0.05, fout=0.3)      # Felgen kreischen
add('fsd_scrape', 32.6, 3.9, db=-4, fin=0.05, fout=0.4, pan=0.3)
add('fsd_screech', 33.2, 3.2, db=-9, off=8, fout=0.4, pan=-0.3)
add('fsd_scrape', 36.5, 2.0, db=0, speed=0.8, fout=0.2)                      # Nahaufnahme Rad
add('fsd_screech', 38.5, 0.95, db=-6, peak_win=1.0, fout=0.1)
add('fsd_crash', 39.38, 2.9, db=1, fout=1.0)                                 # Auffahrunfall
add('fsd_crash_thud', 39.38, 1.0, db=2, fout=0.4)
add('fsd_glass', 39.45, 1.9, db=-5, fout=0.5)
add('fsd_gush', 42.0, 5.0, db=-4, peak_win=3, fin=0.05, fout=0.3)            # Rohre platzen
add('fsd_spray', 42.0, 5.0, db=-6, fin=0.05, fout=0.3)
add('fsd_spray2', 42.05, 5.0, db=-9, peak_win=3, fin=0.05, fout=0.3, pan=0.4)
add('fsd_splash2', 44.6, 2.4, db=-3, peak_win=2, fin=0.05, fout=0.3)
# ---------------- Stufe 6: tödlich ----------------
add('fsd_hiss', 47.0, 4.3, db=-7, peak_win=3, fin=0.1, fout=0.05)            # Gas strömt aus
add('fsd_screech', 48.6, 2.6, db=-12, peak_win=2.0, fin=1.2, fout=0.05)      # Auto mit Funken kommt näher
add('fsd_explosion', 51.18, 5.0, db=3, fout=1.5)                             # Zündung
add('fsd_explosion2', 51.2, 3.0, db=-2, peak_win=0.5, fout=1.5)
add('fsd_glass', 51.25, 1.9, db=-3, fout=0.5)
add('fsd_screams', 51.8, 2.2, db=-14, fin=0.2, fout=0.8)
add('fsd_fire', 51.8, 2.3, db=-6, fin=0.4, fout=0.3)
add('fsd_plane', 54.0, 7.0, db=-1, peak_win=5, fin=0.2, fout=0.8)            # Flugzeug
add('fsd_screech', 55.9, 1.6, db=-4, peak_win=1.5, fout=0.3)                 # Aufsetzen auf Felgen
add('fsd_crash', 57.3, 2.9, db=2, fout=1.0)                                  # Fahrwerk bricht
add('fsd_crash_thud', 57.3, 1.0, db=3, speed=0.7, fout=0.4)
add('fsd_scrape', 57.5, 3.5, db=-2, speed=0.7, fout=0.5)
add('fsd_fire', 57.8, 3.2, db=-4, fin=0.5, fout=0.3)
add('fsd_explosion2', 59.2, 1.8, db=0, peak_win=0.5, fout=0.6)
# ---------------- Stufe 7: Weltuntergang ----------------
add('fsd_rocket', 61.0, 3.2, db=-1, peak_win=3, fin=0.4, fout=0.1)          # Start
add('fsd_explosion', 64.15, 5.0, db=4, speed=0.75, fout=1.0)                 # Explosion der Rakete
add('fsd_thunder', 64.15, 2.4, db=-2, peak_win=0.4, speed=0.8, fout=1.0)
add('fsd_siren_eu', 66.6, 3.4, db=-22, fin=1.0, fout=0.3)
add('fsd_screams', 67.5, 2.5, db=-24, fin=0.5, fout=0.5)
# ---------------- Rückkehr und danach ----------------
add('fsd_thunder', 69.98, 2.5, db=-2, peak_win=0.4, fout=1.5)
add('fsd_siren_eu', 72.0, 6.0, db=-11, off=4, fin=1.0, fout=0.6)
add('fsd_horn1', 73.4, 1.6, db=-12, pan=0.3)
add('fsd_horn3', 76.0, 1.6, db=-14, pan=-0.4)
add('fsd_siren_eu', 78.0, 12.0, db=-9, off=10, fin=0.3, fout=2.5)
add('fsd_siren2', 78.0, 11.3, db=-13, fin=0.3, fout=2.0, pan=0.4)
add('fsd_horn1', 79.3, 1.6, db=-13, pan=-0.5)
add('fsd_horn3', 81.2, 1.6, db=-15, pan=0.5)
add('fsd_horn1', 83.0, 1.2, db=-14)
add('fsd_crowd', 78.0, 12.0, db=-22, fin=0.5, fout=2.5)
add('fsd_horn3', 86.2, 1.6, db=-17, pan=-0.3)
add('fsd_dog', 84.0, 6.0, db=-26, off=2, fin=0.5, fout=2.0)

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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge01_gummi.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', out, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', '90', '-movflags', '+faststart', fin], check=True)
    print('fertig:', fin)

# Quellenangaben für die Videobeschreibung
cred = []
for f in sorted(os.listdir(RAW)):
    if f.endswith('.json') and f[:-5] in _cache and _cache[f[:-5]] is not None:
        m = json.load(open(os.path.join(RAW, f)))
        src = 'Freesound, über den Datensatz FSD50K' if m['artist'].startswith('Freesound') else 'Wikimedia Commons'
        cred.append(f"- {m['title'][5:]} – {m['license']} ({src})")
open(os.path.join(HERE, 'quellen_geraeusche.md'), 'w').write('# Geräusche (echte Aufnahmen)\n\nAlle Geräusche sind echte Aufnahmen unter CC0 (frei nutzbar, keine Namensnennung nötig).\n\n' + '\n'.join(cred) + '\n\nErde bei Nacht: NASA Black Marble, gemeinfrei (Wikimedia Commons: The earth at night.jpg)\n')
