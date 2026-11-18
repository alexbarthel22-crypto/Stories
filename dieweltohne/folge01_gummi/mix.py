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
    c = np.convolve(e, np.ones(n), 'valid')
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
            reps = int(np.ceil(n / max(1, len(seg) - SR))) + 1
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
WK = [[5, 10], [8.4, 9.55], [13, 9.1], [20, 8.2], [27, 7.3], [33, 6.5], [40, 5.6], [47, 4.6], [55, 3.5], [62, 1.8], [68, 0.3], [70, 0]]


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

# ---------------- Atmosphäre ----------------
add('rain_street', 0, 40, db=-10, off=120, fin=0.3, fout=0.3)          # Straße im Regen
add('city_berlin', 0, 5.1, db=-12, off=20, fin=0.3, fout=0.15)          # Verkehr bis zum Verschwinden
add('car_away', 0.6, 4.4, db=-8, off=1.0, fout=0.1, pan=-0.3)            # vorbeifahrendes Auto
add('rain_street', 40, 7, db=-27, off=300, fin=0.2, fout=0.2)           # Küche: Regen gedämpft draußen
add('rain_street', 47, 8, db=-18, off=420, fin=0.2, fout=0.3)           # Flughafen
add('thunder', 55, 7, db=-6, off=40, fin=0.4, fout=0.5, speed=0.6)     # Globus: tiefes Grollen
add('rain_street', 62, 6, db=-26, off=600, fin=0.2, fout=0.2)           # Kinderzimmer
add('rain_street', 68, 18.5, db=-11, off=900, fin=0.3, fout=3.0)        # danach wieder draußen

# ---------------- Countdown-Ticks ----------------
clock = load('clock')
if clock is not None:
    on = onsets(clock)
    tick_off = on[2] if len(on) > 2 else 0
    for s in [1, 2, 3, 4]: add('clock', s - 0.01, 0.16, db=-4, off=tick_off - 0.005, fout=0.04)
    for T in ticks: add('clock', T, 0.16, db=-9 + (6 if T > 66 else 0), off=tick_off - 0.005, fout=0.04)

# ---------------- Ereignisse ----------------
add('thunder', 4.98, 2.5, db=0, peak_win=0.4, fout=1.5)                 # Moment des Verschwindens
# Felgen auf Asphalt
add('metal_scratch', 5.08, 3.4, db=-3, peak_win=1.0, fout=0.4, pan=0.2)
add('metal_rub', 5.15, 3.2, db=-6, peak_win=1.0, fout=0.4, pan=-0.2)
add('metal_scratch', 8.4, 2.4, db=0, peak_win=1.5, speed=0.85, fout=0.2)  # Nahaufnahme Rad
add('fireworks', 8.4, 2.4, db=-12, peak_win=2, fout=0.2)                  # Funkenknistern
add('metal_rub', 10.8, 0.95, db=-4, peak_win=1.0, fout=0.1)
add('metal_hits', 11.68, 1.5, db=2, peak_win=0.4, fout=0.8)               # Aufprall
add('thud', 11.68, 0.6, db=4, fout=0.3)
add('metal_hit', 11.72, 0.8, db=-2, fout=0.4)
# Handy
add('rain_street', 13, 7, db=-6, off=1500, fin=0.05, fout=0.1)          # Regen ganz nah
add('splashes', 13, 7, db=-24, off=5, fout=0.2)
add('buzz', 17.6, 1.7, db=-16, fin=0.6, fout=0.02)
add('buzz', 19.0, 0.32, db=-6, peak_win=0.3, fout=0.02)
# Schuhsohlen: Ausrutschen und Aufschlagen
for i in range(6):
    fall = 20 + 3.0 + i * 0.32 + (i % 2) * 0.25
    add('thud', fall + 0.62, 0.5, db=0 - i, fout=0.2, pan=(i % 3 - 1) * 0.4)
add('crowd', 23.5, 3.5, db=-20, off=10, fin=0.5, fout=0.5)
# Hosen
add('crowd', 27, 6, db=-22, off=20, fin=0.3, fout=0.3)
add('laugh', 28.6, 4.2, db=-13, off=0.5, fin=0.2, fout=0.8)
# Ballons
add('crowd', 33, 7, db=-24, off=30, fin=0.3, fout=0.3)
# Küche
add('faucet', 40.5, 6.5, db=-4, off=5, fin=0.05, fout=0.3)
add('stream', 40.55, 6.4, db=-6, off=10, fin=0.08, fout=0.3)
add('splashes', 43.1, 3.9, db=-2, off=10, fin=0.05, fout=0.3)
# Flugzeug
add('plane', 47, 8, db=-2, peak_win=5, fin=0.3, fout=0.6)
add('metal_scratch', 49.6, 5.4, db=0, peak_win=2.0, speed=0.7, fout=0.6)
add('metal_rub', 49.65, 5.3, db=-3, peak_win=2.0, speed=0.6, fout=0.6)
add('thud', 49.6, 0.8, db=4, speed=0.6, fout=0.3)
add('fireworks', 49.7, 5.3, db=-10, peak_win=3, fout=0.6)
# Weltweit
add('siren_police', 56, 6, db=-26, off=3, fin=1.0, fout=0.8)
add('horn', 58.5, 1.2, db=-24, fout=0.4)
# Gummibärchen
add('bag', 62.2, 2.2, db=-10, peak_win=1.5, fin=0.05, fout=0.4)
# Rückkehr
add('thunder', 69.98, 2.5, db=-1, peak_win=0.4, fout=1.5)
add('horn', 71.6, 1.0, db=-10, fout=0.2, pan=0.3)
add('horn', 74.3, 1.4, db=-14, fout=0.3, pan=-0.4)
add('siren_police', 73, 5, db=-20, off=3, fin=1.5, fout=0.5)
# 5 Minuten später
add('siren_fire', 78, 7.2, db=-10, off=2, fin=0.3, fout=0.8)
add('siren_police', 78, 7.2, db=-16, off=10, fin=0.3, fout=0.8, pan=0.4)
add('horn', 79.2, 0.9, db=-14, pan=-0.5)
add('horn', 81.0, 1.4, db=-17, pan=0.5)
add('horn', 83.1, 0.7, db=-15)
add('crowd', 78, 7, db=-22, off=40, fin=0.5, fout=1.0)

# ---------------- Ausgabe ----------------
peak = np.abs(mix).max()
if peak > 0.98: mix *= 0.98 / peak
tmp = os.path.join(HERE, 'mix_roh.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', tmp], input=mix.tobytes(), check=True)
out = os.path.join(HERE, 'mix.wav')
# TikTok-Lautheit: ca. -14 LUFS, Spitzen begrenzt
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=14', '-ar', str(SR), out], check=True)
os.remove(tmp)
print('mix.wav fertig, Ticks:', len(ticks))

if '--mux' in sys.argv:
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge01_gummi.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', out, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', '90', '-movflags', '+faststart', fin], check=True)
    print('fertig:', fin)

# Quellenangaben für die Videobeschreibung
cred = []
for f in sorted(os.listdir(RAW)):
    if f.endswith('.json'):
        m = json.load(open(os.path.join(RAW, f)))
        cred.append(f"- {m['title'][5:]} – {m['artist'] or 'unbekannt'} – {m['license']} (Wikimedia Commons)")
open(os.path.join(HERE, 'quellen_geraeusche.md'), 'w').write('# Geräusche (echte Aufnahmen)\n\n' + '\n'.join(cred) + '\n\nErde bei Nacht: NASA Black Marble, gemeinfrei (Wikimedia Commons: The earth at night.jpg)\n')
