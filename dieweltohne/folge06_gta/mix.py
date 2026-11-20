"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge06_gta.mp4
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
VANISH, RETURN = 10.0, 58.0
WK = [[10, 10], [17, 9.3], [24, 8.4], [31, 7.4], [39, 6.0], [48, 4.0], [58, 0]]
THROW, STREAM_BLACK, RUSH, SHELF_FALL, OVERHEAT, FIRE, GAS = 13.6, 18.6, 27.4, 28.6, 33.8, 35.6, 37.2
WALL_BLACK, WALL_FALL, NET_DOWN, SUNRISE = 40.6, 43.4, 61.5, 66.0
HIT = THROW + 0.42


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


# ---------------- Wohnzimmer: Verfolgungsjagd im Spiel ----------------
amb('fsd_car_rev', 0, 10.0, -14, off=0.5)                                            # Motor im Spiel (aus dem Fernseher)
add('fsd_siren_pass', 0.0, 10.0, db=-16, off=2.0, fin=0.5, fout=0.05, pan=-0.2)
add('fsd_tire_screech', 3.2, 1.4, db=-14, fout=0.4, pan=0.3)
add('fsd_tire_screech', 7.6, 1.2, db=-14, off=0.5, fout=0.4, pan=-0.3)
amb('fsd_pc_fan', 0, 17.05, -28)                                                     # Konsolenlüfter
for s_ in range(1, 10): tick(s_, -8 if s_ < 7 else -2)
add('fsd_sub_rumble', 7.0, 3.05, db=-12, off=1.0, fin=2.5, fout=0.05)
# Verschwinden: Bildfehler, dann Stille, dann Fehlerton
add('fsd_glitch', 9.98, 0.6, db=-2, fout=0.2)
add('fsd_static', 10.0, 0.5, db=-8, fout=0.2)
add('fsd_power_down', 10.3, 1.2, db=-8, fout=0.4)
add('fsd_alarm_beep', 11.42, 0.35, db=-14, fout=0.1)                                 # Fehlermeldung
add('fsd_crowd_gasp', 11.6, 1.6, db=-18, fout=0.5)
add('fsd_whoosh_fast', THROW - 0.05, 0.6, db=-4, fout=0.2)                            # Wurf
add('fsd_glass_break', HIT, 2.0, db=-2, peak_win=0.2, fout=0.8)                        # Controller trifft Fernseher
add('fsd_impact_boom2', HIT, 1.0, db=-12, fout=0.5)
add('fsd_plastic_clatter', HIT + 0.55, 0.8, db=-10, fout=0.3)                          # Controller fällt auf den Boden
add('fsd_electric_arc', HIT + 0.1, 0.5, db=-16, fout=0.2)

# ---------------- Stream im Bett ----------------
amb('fsd_crickets', 17, 24.05, -26)
add('fsd_keyboard', 17.0, 1.5, db=-24, off=4.0, fout=0.3)                             # Streamer tippt (leise aus dem Handy)
add('fsd_car_rev', 17.0, STREAM_BLACK - 17.0 + 0.1, db=-24, off=2.0, fout=0.1)
add('fsd_glitch2', STREAM_BLACK - 0.02, 0.5, db=-8, fout=0.2)
for k in range(10): add('fsd_phone_buzz', STREAM_BLACK + 0.8 + k * 0.42, 0.3, db=-16 - (k % 3) * 2, fout=0.1)  # Chat-Benachrichtigungen
add('fsd_notify', STREAM_BLACK + 1.2, 1.0, db=-18, fout=0.3)
add('fsd_dog_howl', 21.5, 2.4, db=-22, fin=0.3, fout=0.8, pan=0.5)                    # draußen wird es unruhig
add('fsd_door_slam', 22.3, 0.5, db=-18, pan=-0.4)
add('fsd_door_slam', 23.1, 0.5, db=-22, pan=0.5)

# ---------------- Elektromarkt ----------------
amb('fsd_crowd_murmur', 24, RUSH + 0.5, -14)
amb('fsd_electric_hum', 24, 31.05, -26)
add('fsd_whoosh_fast', 24.75, 0.5, db=-12, speed=1.3, fout=0.2)                        # Disc löst sich auf
add('fsd_glitch', 24.8, 0.3, db=-14, fout=0.1)
add('fsd_crowd_gasp', 25.2, 2.0, db=-10, fout=0.5)
add('fsd_crowd_murmur', 26.2, 2.0, db=-10, off=3.0, fin=0.3, fout=0.5)
add('fsd_footsteps_run', RUSH, 3.6, db=-6, fin=0.1, fout=0.6)                          # Schlange stürmt los
add('fsd_football_crowd', RUSH, 3.6, db=-10, off=3.0, fin=0.2, fout=0.6)
add('fsd_screams', RUSH + 0.3, 2.0, db=-14, off=1.0, fout=0.6)
add('fsd_klaxon', RUSH + 0.2, 3.4, db=-14, fout=0.3)                                   # Alarm
add('fsd_metal_groan', SHELF_FALL - 0.2, 1.2, db=-8, fout=0.3)
add('fsd_metal_crash', SHELF_FALL + 0.85, 2.0, db=-2, peak_win=0.2, fout=0.8)          # Regal schlägt auf
add('fsd_plastic_clatter', SHELF_FALL + 0.9, 2.2, db=-2, fout=0.6)

# ---------------- Rechenzentrum ----------------
amb('fsd_pc_fan', 31, 39.05, -12, off=5.0)
amb('fsd_electric_hum', 31, 39.05, -16)
add('fsd_generator', 31.8, 7.25, db=-16, fin=1.5, fout=0.05)                             # Lüfter drehen hoch
add('fsd_alarm_beep', OVERHEAT, 5.25, db=-12, fout=0.1)
add('fsd_klaxon2', OVERHEAT + 0.4, 4.85, db=-18, fin=0.3, fout=0.05)
add('fsd_electric_arc', FIRE - 0.6, 1.2, db=-4, fout=0.3)                              # Kurzschluss
add('fsd_impact_boom', FIRE, 1.6, db=-8, fout=0.8)
add('fsd_fire_crackle', FIRE, 39.05 - FIRE, db=-6, fin=0.3, fout=0.05)
add('fsd_gas_hiss', GAS, 39.05 - GAS, db=-2, fin=0.05, fout=0.05)                      # Löschgas
add('fsd_hiss', GAS + 0.2, 1.6, db=-10, fout=0.3)

# ---------------- Launch-Party ----------------
amb('fsd_party_beat', 39, WALL_BLACK + 0.05, -8)                                       # Beat der Party
amb('fsd_crowd_cheer', 39, WALL_BLACK + 0.3, -8)
amb('fsd_football_crowd', 39, WALL_FALL, -18, off=3.0)
add('fsd_glitch', WALL_BLACK - 0.02, 0.6, db=-4, fout=0.2)
add('fsd_power_down', WALL_BLACK + 0.1, 1.2, db=-6, fout=0.4)
add('fsd_crowd_gasp', WALL_BLACK + 0.5, 2.0, db=-6, fout=0.5)
add('fsd_crowd_murmur', WALL_BLACK + 1.0, 3.0, db=-8, fin=0.3, fout=0.5)
add('fsd_football_crowd', WALL_BLACK + 1.4, 2.4, db=-10, off=6.0, fin=0.2, fout=0.5)                     # Menge drängt nach vorn
add('fsd_metal_groan', WALL_FALL - 0.7, 1.4, db=-4, fout=0.2)
add('fsd_metal_crash2', WALL_FALL, 1.5, db=-2, off=0.1, fout=0.5)                      # Halterung reißt
add('fsd_electric_arc', WALL_FALL + 0.1, 1.4, db=-8, fout=0.5)
add('fsd_screams', WALL_FALL + 0.2, 3.5, db=-4, fin=0.05, fout=1.2)
add('fsd_rubble', WALL_FALL + 0.8, 3.0, db=-4, fout=1.0)                               # Module schlagen auf
add('fsd_metal_crash', WALL_FALL + 0.9, 2.0, db=-6, peak_win=0.2, fout=0.8)
add('fsd_footsteps_run', WALL_FALL + 0.5, 4.1, db=-8, fin=0.2, fout=0.8)

# ---------------- Straßen: alle gehen raus ----------------
amb('fsd_city_day', 48, 66.05, -24)
for k, tt in enumerate([48.4, 48.9, 49.3, 49.9, 50.6, 51.2, 52.1]): add('fsd_door_slam', tt, 0.5, db=-10 - k, pan=((k % 3) - 1) * 0.6)
add('fsd_footsteps_run', 48.6, 6.0, db=-12, fin=0.5, fout=1.0)
add('fsd_crowd_murmur', 49.5, 8.6, db=-12, fin=2.0, fout=0.05)
add('fsd_football_crowd', 52.0, 6.1, db=-20, off=10.0, fin=2.0, fout=0.05)
add('fsd_car_horn', 51.2, 1.2, db=-14, fout=0.3, pan=0.4)
add('fsd_car_horn', 53.8, 1.6, db=-12, fout=0.3, pan=-0.5)
add('fsd_car_horn', 55.6, 0.8, db=-16, fout=0.2, pan=0.2)
for s_ in range(55, 58): tick(s_ + 0.0, -12)
# GTA 6 ist zurück: Jubel, Benachrichtigungen, dann bricht das Netz zusammen
add('fsd_whoosh_boom', RETURN - 0.02, 3.0, db=-6, fout=1.5)
add('fsd_crowd_cheer', RETURN + 0.2, 3.2, db=-6, fin=0.05, fout=0.8)
for k in range(8): add('fsd_notify', RETURN + 0.4 + k * 0.33, 0.9, db=-14 - (k % 3) * 3, fout=0.3, pan=((k % 5) - 2) * 0.3)
add('fsd_crowd_murmur', RETURN + 2.0, NET_DOWN - RETURN - 1.6, db=-10, fin=0.4, fout=0.3)
add('fsd_power_down', NET_DOWN - 0.05, 1.4, db=-4, fout=0.5)                          # Netz weg
add('fsd_crowd_gasp', NET_DOWN + 0.2, 2.4, db=-4, fout=0.6)
add('fsd_crowd_murmur', NET_DOWN + 1.4, 3.0, db=-10, off=5.0, fin=0.3, fout=0.8)
add('fsd_siren_pass', 62.5, 6.0, db=-20, off=4.0, fin=1.0, fout=2.0, pan=-0.4)
# Sonnenaufgang: Vögel, Hahn, ruhige Menge
add('fsd_crowd_murmur', 66, 8.0, db=-18, fin=1.0, fout=3.0)
amb('fsd_wind', 66, 80.05, -20)
amb('fsd_birdsong', 67, 80.05, -14)
add('fsd_rooster', 69.0, 2.3, db=-10, fout=0.5, pan=0.4)                               # Hahn kräht
add('fsd_church_bell', 72.5, 4.0, db=-20, off=0.4, fout=1.5)
add('fsd_birds_flap', 75.0, 2.0, db=-14, fout=0.6, pan=-0.3)

# ---------------- Morgens im Wohnzimmer ----------------
amb('fsd_birdsong', 80, 89.9, -22)
amb('fsd_snore', 80.3, 89.9, -10)                                                       # eingeschlafen
amb('fsd_pc_fan', 80, 89.9, -26)
add('fsd_clock_tick', 80, 9.9, db=-22)
add('fsd_notify', 86.0, 1.0, db=-18, fout=0.3)                                          # Download 2 %

# ---------------- Countdown der 10 Sekunden ----------------
ticks = []; last = 10
for f in range(int(VANISH * 30), int(RETURN * 30) + 1):
    v = world_left(f / 30)
    if int(v * 10) < int(last * 10): ticks.append(f / 30)
    last = v
for T in ticks: tick(T, -17 + (4 if T > 53 else 0))
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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge06_gta.mp4')
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
