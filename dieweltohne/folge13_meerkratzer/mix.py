"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge13_meerkratzer.mp4
"""
import json
import os
import subprocess
import sys

import numpy as np

SR = 48000
DUR = 60.0
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
PRESS, START, NO_NET, SHADOW, WHALE_FLEE, LIGHTS_OUT = 7.9, 9.0, 11.4, 13.2, 18.6, 26.3
LURE, LIGHTS_ON, CRACK, ARRIVE, KNOCK, SUB, BOX, DELIVERED = 29.2, 31.8, 42.0, 52.0, 53.3, 54.4, 55.5, 56.2
DIVE = 2.25


def amb(name, t0, t1, db, off=0.0, xf=0.6, speed=1.0):
    add(name, t0, t1 - t0, db=db, off=off, fin=xf, fout=xf, speed=speed)


# Hook: Meer, Möwen, Eintauchen
amb('fsd_beach_waves', 0.0, DIVE + 0.2, -16, xf=0.3)
add('fsd_seagulls', 0.2, 2.0, db=-22, fout=0.5)
add('fsd_splash_big', DIVE - 0.08, 1.2, db=-7, peak_win=0.3, fout=0.4)
add('fsd_dive_bubble', DIVE - 0.02, 2.6, db=-8, fout=0.8)
add('fsd_sub_rumble', DIVE, 2.75, db=-20, fin=0.4, fout=0.3)
add('fsd_whoosh_fast', 4.75, 0.4, db=-15, fout=0.1)
# Aufzug: abgeklebter Knopf
amb('fsd_electric_hum', 5.0, 9.0, -30, xf=0.3)
add('fsd_heartbeat', 6.2, 1.8, db=-17, fin=0.3, fout=0.4)
add('fsd_switch', PRESS - 0.02, 0.4, db=-6)
add('fsd_bell', PRESS + 0.35, 1.4, db=-11, fout=0.6)
add('fsd_lift_clack', 8.75, 0.6, db=-12, fout=0.2)
# Abfahrt, flach: Fische, Handy, kein Netz, ein Schatten
add('fsd_metal_groan', START, 1.5, db=-20, fout=0.5)
add('fsd_gurgle', 9.2, 1.4, db=-24, fout=0.5)
add('fsd_whoosh_fast', 10.0, 0.6, db=-23, speed=0.8, fout=0.2)
add('fsd_notif', 9.6, 0.6, db=-14)
add('fsd_glitch', NO_NET - 0.02, 0.6, db=-16, fout=0.2)
add('fsd_whale_moan', SHADOW - 0.2, 1.9, db=-10, speed=0.75, fin=0.3, fout=0.5)
add('fsd_sub_rumble', SHADOW, 1.8, db=-14, fin=0.2, fout=0.5)
# Schnitte: Zähler rollt, Sonar
for t, dbv in [(15.0, -14), (21.0, -15), (27.0, -16), (33.5, -15), (39.5, -15), (46.5, -16), (51.0, -15)]:
    add('fsd_whoosh_fast', t - 0.15, 0.55, db=dbv, speed=0.85, fout=0.15)
for t in [15.25, 21.25, 33.8, 39.8, 46.8]:
    add('fsd_radar_ping', t, 1.3, db=-19, fout=0.6)
# Pottwal
add('fsd_whale_moan', 15.4, 2.2, db=-8, speed=0.6, fin=0.4, fout=0.6)
add('fsd_gurgle', 16.6, 1.0, db=-24, fout=0.4)
add('fsd_whale_moan', 18.0, 1.0, db=-11, speed=0.9, fin=0.2, fout=0.4)
add('fsd_dive_bubble', WHALE_FLEE + 0.1, 2.0, db=-10, off=0.2, fout=0.7)
add('fsd_sub_rumble', WHALE_FLEE, 2.2, db=-11, fin=0.1, fout=0.8)
# Riesenkalmar
add('fsd_slurp', 21.9, 0.8, db=-15, speed=0.7, fout=0.2)
add('fsd_slurp', 23.1, 0.8, db=-17, speed=0.6, fout=0.2)
add('fsd_heartbeat', 22.4, 3.8, db=-14, fin=0.4, fout=0.4)
add('fsd_metal_groan', 24.6, 1.4, db=-19, fout=0.5)
for t in [25.8, 26.0, 26.15]:
    add('fsd_static', t, 0.12, db=-14, fout=0.03)
add('fsd_power_down', LIGHTS_OUT - 0.1, 1.2, db=-7, fout=0.4)
# Dunkel: Herzschlag, Atem, Licht kommt näher
add('fsd_heartbeat2', 27.3, 4.4, db=-12, fin=0.3, fout=0.4)
add('fsd_breathing', 28.1, 1.6, db=-19, fout=0.4)
add('fsd_chime', LURE, 1.6, db=-23, speed=0.8, fout=0.8)
add('fsd_gasp', 30.95, 0.8, db=-9, fout=0.2)
add('fsd_switch', LIGHTS_ON - 0.02, 0.3, db=-7)
add('fsd_electric_hum', LIGHTS_ON, 1.2, db=-27, fin=0.05, fout=0.4)
add('fsd_chime', 32.1, 0.9, db=-17, speed=1.3, fout=0.4)
# Schwarze Raucher
add('fsd_fire_roar', 33.6, 5.6, db=-19, speed=0.55, fin=0.5, fout=0.8)
add('fsd_gurgle', 34.4, 1.2, db=-20, speed=0.7, fout=0.4)
add('fsd_gurgle', 37.0, 1.2, db=-21, speed=0.6, fout=0.4)
add('fsd_sub_rumble', 35.5, 3.6, db=-20, fin=0.4, fout=0.8)
# Der Druck: Knarzen, Knack
add('fsd_metal_groan', 40.0, 1.5, db=-13, fout=0.5)
add('fsd_heartbeat', 40.4, 1.6, db=-13, fin=0.2, fout=0.2)
add('fsd_metal_groan', 41.2, 0.9, db=-11, speed=0.8, fout=0.3)
add('fsd_crack', CRACK - 0.02, 0.9, db=-1, peak_win=0.1, fout=0.4)
add('fsd_glass', CRACK + 0.02, 1.0, db=-12, peak_win=0.2, fout=0.5)
add('fsd_sub_rumble', CRACK, 1.6, db=-9, fout=0.8)
add('fsd_breathing', 43.6, 1.8, db=-17, fout=0.5)
add('fsd_metal_groan', 45.0, 1.2, db=-21, speed=0.7, fout=0.5)
# Scheibenbauch
add('fsd_gurgle', 47.5, 1.0, db=-26, speed=0.8, fout=0.4)
add('fsd_sub_rumble', 49.0, 2.0, db=-23, fin=0.4, fout=0.6)
# Ganz unten
add('fsd_lift_clack', ARRIVE - 0.05, 0.7, db=-7, fout=0.2)
add('fsd_bell', ARRIVE + 0.25, 1.3, db=-12, fout=0.6)
add('fsd_knock', KNOCK - 0.02, 0.9, db=-3, speed=0.85, peak_win=0.05, fout=0.3)
add('fsd_heartbeat', KNOCK + 0.6, 1.4, db=-15, fout=0.3)
add('fsd_switch', SUB - 0.22, 0.3, db=-9)
add('fsd_sub_motor', SUB - 0.1, 5.0, db=-17, fin=0.5, fout=1.0)
add('fsd_notif', DELIVERED, 0.6, db=-11)
add('fsd_sigh', 57.7, 1.5, db=-11, fout=0.5)
add('fsd_soft_thud', BOX + 0.2, 0.4, db=-16)
# Mehr Details: Aufzugsmechanik, Druckknarzen, Blasen, Sonar
add('fsd_elevator', START - 0.35, 2.6, db=-15, fin=0.1, fout=0.6)
for t, o in [(15.0, 2.0), (21.0, 3.5), (33.5, 1.0), (39.5, 4.5), (51.0, 2.8)]:
    add('fsd_elevator', t - 0.1, 1.1, db=-23, off=o, fin=0.15, fout=0.4)
add('fsd_bubbles', 9.3, 1.6, db=-23, off=3.0, fin=0.3, fout=0.6)
add('fsd_bubbles', 34.0, 2.2, db=-24, off=8.0, fin=0.4, fout=0.7, speed=0.8)
add('fsd_bubbles', ARRIVE + 0.15, 1.4, db=-20, off=12.0, fin=0.1, fout=0.6)
add('fsd_bubbles', SUB + 0.2, 1.8, db=-19, off=16.0, fin=0.3, fout=0.7)
for t, dbv, sp in [(22.0, -22, 0.9), (28.5, -20, 0.8), (36.0, -22, 0.85), (40.3, -15, 0.9), (44.5, -18, 0.8), (49.5, -20, 0.75), (52.6, -18, 0.8)]:
    add('fsd_hull_creak', t, 1.4, db=dbv, off=(t * 0.37) % 9, speed=sp, fin=0.2, fout=0.5)
add('fsd_strain_creak', 41.0, 0.9, db=-16, speed=0.7, peak_win=0.6, fin=0.05, fout=0.3)
for t, dbv in [(28.0, -25), (48.0, -22), (51.3, -21)]:
    add('fsd_radar_ping', t, 1.3, db=dbv, fout=0.6)

# ---------------- Ausgabe ----------------
peak = np.abs(mix).max()
if peak > 0.98: mix *= 0.98 / peak
tmp = os.path.join(HERE, 'mix_roh.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', tmp], input=mix.tobytes(), check=True)
out = os.path.join(HERE, 'mix.wav')
# TikTok-Lautheit: ca. -14 LUFS, Spitzen begrenzt
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'acompressor=threshold=-32dB:ratio=3.5:attack=10:release=350:makeup=7,loudnorm=I=-10.4:TP=-2.5:LRA=8,alimiter=limit=0.7:attack=1:release=60:level=false', '-ar', str(SR), '-c:a', 'pcm_s16le', out], check=True)
os.remove(tmp)
print('mix.wav fertig')

if '--mux' in sys.argv:
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge13_meerkratzer.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', out, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-t', '60', '-movflags', '+faststart', fin], check=True)
    print('fertig:', fin)

# Quellenangaben für die Videobeschreibung
cred = []
for f in sorted(os.listdir(RAW)):
    if f.endswith('.json') and f[:-5] in _cache and _cache[f[:-5]] is not None:
        m = json.load(open(os.path.join(RAW, f)))
        src = 'Freesound, über den Datensatz FSD50K' if m['artist'].startswith('Freesound') else 'Wikimedia Commons'
        cred.append(f"- {m['title'][5:]} – {m['license']} ({src})")
open(os.path.join(HERE, 'quellen_geraeusche.md'), 'w').write('# Geräusche (echte Aufnahmen)\n\nAlle Geräusche sind echte Aufnahmen unter CC0 (frei nutzbar, keine Namensnennung nötig).\n\n' + '\n'.join(cred) + '\n')
