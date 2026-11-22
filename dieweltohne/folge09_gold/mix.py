"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge09_gold.mp4
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
MEDAL_GONE, VISOR_GONE, GLARE, CHIP_DEAD, BRAKE, BLACKOUT, SHIP_HIT, SPAN_FALL, CUBE_LAND = 18.4, 25.0, 26.0, 33.0, 33.3, 40.4, 45.0, 45.6, 49.4


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

# ---------------- Parkdeck: Musikvideo-Dreh ----------------
amb('fsd_hiphop_beat', 0, 10.05, -9)                                                   # Playback für den Dreh
amb('fsd_city_hum', 0, 17.05, -26)
amb('fsd_wind', 0, 17.05, -28)
add('fsd_sub_rumble', 7.0, 3.05, db=-14, off=1.0, fin=2.5, fout=0.05)
add('fsd_scratch', VANISH - 0.02, 0.55, db=-4, off=0.1, fout=0.1)                       # Musik bricht ab
add('fsd_chime', VANISH - 0.05, 1.6, db=-8, fin=0.02, fout=1.0)                         # Gold verschwindet
add('fsd_whoosh_fast', VANISH - 0.1, 1.0, db=-6, fout=0.4)
add('fsd_shout_hey', 11.0, 1.2, db=-12, fout=0.3, pan=0.3)
add('fsd_teens_laugh', 11.3, 5.0, db=-6, fin=0.2, fout=1.2, pan=-0.2)
add('fsd_kid_laugh', 12.6, 3.0, db=-16, fout=0.8, pan=0.4)
# ---------------- Siegerehrung ----------------
amb('fsd_crowd_cheer', 17, 18.6, -10)
for tt in [17.2, 17.5, 17.62, 17.9, 18.1, 18.25, 20.4, 20.55, 21.3, 22.1, 22.3, 23.0]: add('fsd_camera_click', tt, 0.35, db=-14, fout=0.1, pan=((tt * 7) % 2) - 1)
add('fsd_chime', MEDAL_GONE - 0.03, 1.4, db=-8, fout=0.8)
add('fsd_crowd_gasp', MEDAL_GONE + 0.3, 2.2, db=-8, fout=0.6)
amb('fsd_crowd_murmur', MEDAL_GONE + 1.0, 24.05, -18)
add('fsd_laugh', 21.2, 2.6, db=-14, fin=0.2, fout=0.8, pan=-0.3)
# ---------------- Außeneinsatz im All ----------------
amb('fsd_breathing', 24, 26.1, -10)
amb('fsd_electric_hum', 24, 31.05, -26)
add('fsd_static', 24.15, 0.5, db=-16, fout=0.2)
add('fsd_chime', VISOR_GONE - 0.03, 1.2, db=-10, fout=0.7)
add('fsd_whoosh_boom', GLARE - 0.05, 2.0, db=-6, fout=1.0)                              # das grelle Licht
add('fsd_gasp', GLARE + 0.1, 1.0, db=-6, fout=0.3)
amb('fsd_breathing', GLARE + 0.6, 31.05, -6, speed=1.35)                                 # er hechelt
add('fsd_heartbeat', 26.8, 4.25, db=-6, fin=0.4, fout=0.6)
add('fsd_alarm_beep', 27.6, 3.4, db=-16, fout=0.4)
# ---------------- Achterbahn ----------------
add('fsd_lift_clack', 31.0, CHIP_DEAD - 31.0, db=-8, speed=0.7, fout=0.05)             # Kettenlift
amb('fsd_party_music2', 31, CHIP_DEAD + 0.02, -22)                                       # Parkmusik
amb('fsd_wind', 31, 39.05, -20)
add('fsd_power_down', CHIP_DEAD - 0.02, 1.6, db=-6, fout=0.5)
add('fsd_gas_hiss', BRAKE, 0.8, db=-10, fout=0.3)                                         # Bremsen schließen
add('fsd_metal_crash2', BRAKE + 0.02, 0.9, db=-8, off=0.1, fout=0.4)
add('fsd_metal_groan', BRAKE + 0.3, 1.6, db=-10, fout=0.5)
add('fsd_screams', BRAKE + 0.6, 4.4, db=-6, fin=0.1, fout=1.0)
add('fsd_wind_rush', 34.2, 2.4, db=-10, fin=0.2, fout=0.6)                               # Blick nach unten
add('fsd_scream_girl', 35.0, 1.6, db=-12, fout=0.5, pan=0.3)
add('fsd_crowd_gasp', 36.8, 2.0, db=-18, fout=0.6)
# ---------------- Containerschiff und Brücke ----------------
amb('fsd_flood_rush', 39, 48.05, -26)                                                     # Wasser am Rumpf
add('fsd_generator', 39.0, BLACKOUT - 39.0 + 0.05, db=-14, fin=0.3, fout=0.05)           # Maschinen
add('fsd_power_down', BLACKOUT - 0.02, 1.8, db=-6, fout=0.5)
add('fsd_ship_horn', 41.6, 2.4, db=-6, fin=0.05, fout=0.6, peak_win=0.4)                # Warnsignal
add('fsd_ship_horn', 43.3, 1.6, db=-8, fin=0.05, fout=0.5, peak_win=0.4)
add('fsd_metal_crash', SHIP_HIT - 0.02, 2.0, db=0, peak_win=0.2, fout=0.8)               # Aufprall am Pfeiler
add('fsd_impact_boom', SHIP_HIT, 2.4, db=-4, fout=1.0)
add('fsd_metal_groan', SHIP_HIT + 0.4, 1.8, db=-4, fout=0.6)
add('fsd_building_collapse', SPAN_FALL - 0.6, 2.4, db=-2, fout=0.8)                      # Brücke stürzt
add('fsd_splash_big', SPAN_FALL + 1.5, 1.0, db=-2, off=0.7, fout=0.4)
add('fsd_splash_big', SPAN_FALL + 1.95, 0.5, db=-6, off=0.7, fout=0.3, pan=0.4)
# ---------------- Rückkehr: der Würfel ----------------
add('fsd_chime', RETURN - 0.7, 2.2, db=-6, fin=0.2, fout=0.6)                             # Gold kommt zusammen
add('fsd_whoosh_boom', CUBE_LAND - 1.3, 1.3, db=-8, fin=0.4, fout=0.05)
add('fsd_impact_boom2', CUBE_LAND - 0.02, 3.0, db=0, fout=1.2)                            # Aufschlag
add('fsd_impact_boom', CUBE_LAND, 2.5, db=-4, fout=1.0)
add('fsd_glass_big', CUBE_LAND + 0.15, 3.0, db=-8, peak_win=0.2, fout=1.2)             # Fenster rundum
add('fsd_rubble', CUBE_LAND + 0.3, 2.5, db=-10, fout=1.0)
add('fsd_screams', CUBE_LAND + 0.5, 2.5, db=-12, fin=0.1, fout=1.0)
add('fsd_sub_rumble', CUBE_LAND, 3.5, db=-6, off=1.0, fin=0.05, fout=1.5)
amb('fsd_wind', 50, 58.05, -22)
add('fsd_debris', 51.2, 1.4, db=-14, fout=0.5, pan=-0.4)
add('fsd_crowd_murmur2', 53.5, 4.6, db=-18, fin=1.0, fout=0.5)
# ---------------- Nacht: alle kommen zum Würfel ----------------
amb('fsd_fire_crackle', 58, 68.05, -14)
amb('fsd_crowd_outdoor', 58, 80.05, -16)
add('fsd_crowd_murmur', 59.0, 8.0, db=-16, fin=1.0, fout=1.0)
add('fsd_dog_howl', 61.0, 3.0, db=-20, fin=0.3, fout=1.0, pan=-0.6)
add('fsd_footsteps_run', 63.0, 3.0, db=-14, fout=0.8, pan=0.4)
add('fsd_shout_hey', 65.2, 1.0, db=-16, fout=0.3, pan=-0.3)
# ---------------- Luftbild ----------------
amb('fsd_canyon_wind', 68, 80.05, -16)
add('fsd_fire_roar', 70.0, 5.0, db=-22, fin=1.0, fout=1.5)
add('fsd_church_bell', 73.5, 5.0, db=-16, off=0.4, fout=2.0)                              # mechanische Glocken läuten noch
add('fsd_sub_rumble', 76.0, 4.0, db=-14, off=1.0, fin=1.5, fout=1.0)
# ---------------- Schluss: totes Handy ----------------
amb('fsd_wind', 80, 89.9, -20)
amb('fsd_fire_crackle', 80, 89.9, -20)
add('fsd_crowd_murmur2', 80.0, 9.9, db=-20, fin=0.5, fout=1.0)
add('fsd_sub_rumble', 84.0, 5.9, db=-10, off=1.0, fin=2.0, fout=1.0)
add('fsd_impact_boom2', 88.9, 1.1, db=-6, fout=0.8)                                       # Schlussschlag in die Abblende
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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge09_gold.mp4')
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
