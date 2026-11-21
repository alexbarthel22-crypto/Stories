"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge08_baumwolle.mp4
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
VANISH, RETURN = 10.0, 50.0
WK = [[10, 10], [17, 9.0], [24, 7.8], [31, 6.4], [39, 4.6], [47, 1.6], [50, 0]]
NOTE_GONE, MITT_GONE, POT_DROP, FLARE, VAULT_ALARM, MONITOR_ALARM, IGNITE = 18.6, 25.6, 26.0, 26.35, 31.8, 41.5, 59.5


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

# ---------------- Skatepark ----------------
amb('fsd_birdsong', 0, 17.05, -22)
amb('fsd_city_hum', 0, 17.05, -26)
add('fsd_skate_roll', 0.0, 3.0, db=-20, off=2.0, fin=0.3, fout=0.4)
add('fsd_skate_roll', 3.0, 6.6, db=-10, off=6.0, fin=0.4, fout=0.2)                   # rollt auf den Kicker zu
add('fsd_plastic_clatter', 9.55, 0.35, db=-8, peak_win=0.1, fout=0.1)                  # Ollie
add('fsd_sub_rumble', 7.0, 3.05, db=-12, off=1.0, fin=2.5, fout=0.05)
add('fsd_whoosh_fast', 9.9, 1.2, db=-2, fout=0.4)                                      # Baumwolle weg
add('fsd_air_burst', 9.98, 1.1, db=-8, fout=0.5)
add('fsd_plastic_clatter', 10.56, 0.5, db=-4, peak_win=0.1, fout=0.2)                  # Landung
add('fsd_skate_roll', 10.6, 2.8, db=-12, off=12.0, fin=0.05, fout=1.2)
add('fsd_shout_hey', 11.0, 1.2, db=-12, fout=0.3, pan=0.3)
add('fsd_teens_laugh', 11.3, 5.0, db=-6, fin=0.2, fout=1.2, pan=0.2)
add('fsd_kid_laugh', 12.4, 3.0, db=-16, fout=0.8, pan=-0.4)
# ---------------- Imbiss: Kasse ----------------
amb('fsd_crowd_murmur2', 17, 24.05, -24)
amb('fsd_sizzle', 17, 24.05, -24, off=1.0)
add('fsd_cash_drawer', 17.1, 1.4, db=-8, fout=0.3)
add('fsd_air_burst', NOTE_GONE - 0.02, 1.0, db=-14, fout=0.5)
add('fsd_coins', NOTE_GONE + 0.25, 0.85, db=-6, fout=0.2)                             # Münzen bleiben liegen
add('fsd_gasp', 19.0, 1.5, db=-10, fout=0.4)
add('fsd_crowd_gasp', 19.6, 2.0, db=-18, fout=0.6, pan=0.4)
# ---------------- Imbiss: Küche ----------------
add('fsd_sizzle', 24.0, 2.2, db=-10, off=2.0, fin=0.2, fout=0.2)
add('fsd_footsteps_run', 24.1, 1.3, db=-20, fout=0.3)
add('fsd_shout_hey', MITT_GONE + 0.15, 1.0, db=-6, fout=0.3)                            # heißer Griff
add('fsd_metal_crash', POT_DROP + 0.05, 1.6, db=-4, peak_win=0.2, fout=0.8)              # Pfanne schlägt auf
add('fsd_sizzle', POT_DROP + 0.15, 4.5, db=-2, off=0.0, fin=0.02, fout=1.5)             # Fett spritzt
add('fsd_whoosh_boom', FLARE - 0.03, 2.4, db=0, fout=1.2)                                # Stichflamme
add('fsd_fire_roar', FLARE, 4.65, db=-4, off=0.3, fin=0.05, fout=0.6)
add('fsd_fire_crackle', 28.0, 3.05, db=-12, fin=0.5, fout=0.1)
add('fsd_smoke_alarm', 27.6, 3.45, db=-16, fin=0.1, fout=0.1)
add('fsd_screams', 26.6, 1.4, db=-14, off=1.0, fout=0.6)
# ---------------- Tresor ----------------
add('fsd_whoosh_fast', 31.45, 1.2, db=-6, fout=0.4)
add('fsd_air_burst', 31.55, 1.1, db=-6, fout=0.5)
add('fsd_klaxon', VAULT_ALARM, 7.25, db=-12, fin=0.05, fout=0.3)
add('fsd_gasp_f', 31.9, 1.4, db=-10, fout=0.4)
add('fsd_footsteps_run', 32.6, 3.4, db=-14, fout=0.5, pan=0.3)
# ---------------- OP-Saal ----------------
for k in range(12):                                                                     # Herzmonitor-Piepen, wird schneller
    hr = 78 if k < 4 else 78 + (k - 3) * 8; tt = 39.2 + sum(60 / (78 if j < 4 else 78 + (j - 3) * 8) for j in range(k))
    if tt < MONITOR_ALARM: add('fsd_alarm_beep', tt, 0.12, db=-18, fout=0.04)
add('fsd_air_burst', 40.08, 1.0, db=-14, fout=0.5)
add('fsd_gasp', 40.7, 1.4, db=-14, fout=0.4)
add('fsd_monitor_alarm', MONITOR_ALARM, 5.55, db=-12, fin=0.05, fout=0.4)
add('fsd_heartbeat', 43.0, 4.0, db=-12, fin=0.5, fout=0.3)
add('fsd_footsteps_run', 43.0, 2.2, db=-18, fout=0.4, pan=0.4)
add('fsd_sub_rumble', 45.0, 2.05, db=-12, off=1.0, fin=1.5, fout=0.05)
# ---------------- Straße: Fasern kommen zurück ----------------
amb('fsd_city_day', 47, 50.0, -18)
add('fsd_sub_rumble', 47.0, 3.0, db=-14, off=1.0, fin=1.0, fout=0.1)
add('fsd_whoosh_boom', RETURN - 0.1, 3.0, db=-2, speed=0.8, fout=1.5)
amb('fsd_wind_winter', RETURN, 58.05, -14)                                             # weiches Treiben der Flocken
amb('fsd_crowd_outdoor', RETURN, 58.05, -20)
add('fsd_crowd_gasp', RETURN + 0.6, 2.4, db=-10, fout=0.6)
add('fsd_kid_laugh', 52.4, 2.5, db=-16, fout=0.6, pan=0.4)
add('fsd_car_horn', 55.2, 1.0, db=-22, fout=0.3, pan=-0.5)
# ---------------- Straße: Feuer ----------------
add('fsd_fire_crackle', 58.0, 1.6, db=-16, fin=0.3, fout=0.1)
add('fsd_whoosh_boom', IGNITE - 0.05, 2.6, db=0, fout=1.2)
add('fsd_fire_roar', IGNITE, 8.1, db=-4, off=0.2, fin=0.05, fout=1.0)
add('fsd_fire', 62.0, 6.05, db=-8, fin=0.5, fout=0.3)
add('fsd_screams', IGNITE + 1.0, 3.0, db=-8, fin=0.1, fout=1.0)
add('fsd_footsteps_run', IGNITE + 1.5, 6.5, db=-10, fout=0.8)
add('fsd_glass_break', 63.2, 1.5, db=-10, fout=0.5, pan=0.5)
add('fsd_siren_eu', 62.5, 5.55, db=-18, fin=1.0, fout=0.3, pan=-0.3)
add('fsd_explosion', 65.6, 2.4, db=-8, fout=1.0, pan=0.4)                                # Auto geht hoch
# ---------------- Luftbild ----------------
add('fsd_helicopter', 68.0, 12.0, db=-14, fin=0.5, fout=1.5)
add('fsd_fire_roar', 68.0, 5.0, db=-12, fin=0.3, fout=1.5)
add('fsd_thunder_far', 70.2, 5.0, db=-8, fin=0.1, fout=2.0)
add('fsd_air_raid', 72.5, 7.5, db=-22, fin=1.5, fout=1.5)                              # Sirenen über der Stadt
add('fsd_thunder_far2', 75.6, 4.0, db=-8, fin=0.1, fout=1.5, pan=-0.3)
add('fsd_wind', 76.0, 4.05, db=-16, fin=1.0, fout=0.3)
# ---------------- Schluss: Skatepark ----------------
amb('fsd_wind', 80, 90.0, -14)
add('fsd_fire_crackle', 80.0, 8.5, db=-24, fin=1.0, fout=2.0)
add('fsd_siren_pass', 81.5, 5.0, db=-24, fin=1.0, fout=2.0, pan=0.5)
add('fsd_thunder_far', 83.5, 4.0, db=-14, fin=0.2, fout=2.0)
add('fsd_impact_boom2', 88.9, 1.1, db=-6, fout=0.8)
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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge08_baumwolle.mp4')
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
