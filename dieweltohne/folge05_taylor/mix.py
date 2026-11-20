"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge05_taylor.mp4
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
VANISH, RETURN = 10.0, 57.0
WK = [[10, 10], [17, 9.3], [24, 8.5], [32, 7.4], [40, 6.0], [48, 4.0], [57, 0]]
PARTY_STOP, MIC_DROP, SURGE, BARRIER, OVERLOAD, SPARK, NEEDLE, JUMP, SNAP = 18.2, 24.6, 34.5, 36.8, 43.5, 45.2, 50.0, 59.0, 69.0
BLACKOUT = 46.4


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


# ---------------- Zimmer: sie singt mit ----------------
amb('fsd_party_music2', 0, 10.02, -24)                                             # Musik leise aus den Kopfhörern
add('fsd_girl_sing', 3.6, 6.4, db=-12, fin=0.4, fout=0.05)                          # singt mit
for s_ in range(1, 10): tick(s_, -8 if s_ < 7 else -2)
add('fsd_sub_rumble', 7.0, 3.05, db=-12, off=1.0, fin=2.5, fout=0.05)
add('fsd_whoosh_boom', 9.99, 3.0, db=0, fout=1.5)
add('fsd_static', 10.0, 0.25, db=-10, fout=0.1)                                     # Kopfhörer: Musik weg
# ---------------- Stufe 1: Sie singt allein weiter ----------------
add('fsd_girl_sing', 10.05, 1.5, db=-4, off=6.4, fin=0.02, fout=0.3)                # jetzt ohne Musik, allein
add('fsd_switch', 12.05, 0.4, db=-14, fout=0.1)                                      # tippt an den Kopfhörer
add('fsd_door', 12.0, 1.6, db=-10, fin=0.05, fout=0.4)                               # Tür geht auf
add('fsd_camera_click', 13.35, 0.6, db=-12, fout=0.1)                                # Aufnahme startet
add('fsd_gasp_f', 14.65, 1.0, db=-6, fout=0.3)
add('fsd_kid_laugh', 14.4, 2.6, db=-6, fin=0.05, fout=0.6)
add('fsd_footsteps_run', 16.2, 0.9, db=-10, fout=0.3)

# ---------------- Countdown der 10 Sekunden ----------------
ticks = []; last = 10
for f in range(int(VANISH * 30), int(RETURN * 30) + 1):
    v = world_left(f / 30)
    if int(v * 10) < int(last * 10): ticks.append(f / 30)
    last = v
for T in ticks: tick(T, -16 + (4 if T > 52 else 0))

# ---------------- Stufe 2: Schulparty ----------------
add('fsd_party_music', 17.0, PARTY_STOP - 17.0 + 0.02, db=-2, fin=0.05, fout=0.02)
add('fsd_kids_cheer', 17.0, 1.3, db=-14, fout=0.3)
add('fsd_scratch', PARTY_STOP - 0.02, 0.55, db=-6, off=0.1, fout=0.1)               # Plattenkratzer, dann Stille
amb('fsd_crowd_murmur', PARTY_STOP + 0.9, 24.05, -14)
add('fsd_teens_laugh', 20.0, 1.8, db=-16, fin=0.1, fout=0.6)
add('fsd_switch', PARTY_STOP + 3.6, 0.4, db=-8, fout=0.1)                            # Hallenlicht an
add('fsd_electric_hum', PARTY_STOP + 3.65, 24.05 - PARTY_STOP - 3.65, db=-20, fin=0.3)

# ---------------- Stufe 3: Stadionkonzert, Bühne leer ----------------
amb('fsd_stadium_roar', 24, 32.05, -9)
amb('fsd_rock_drums', 24, 32.05, -12)                                                # Band spielt weiter
for tt in [24.1, 26.7, 29.3]: add('fsd_guitar', tt, 2.6, db=-15, fout=0.6, pan=0.3)
add('fsd_book_thud', MIC_DROP - 0.03, 0.5, db=-2, peak_win=0.1, fout=0.2)          # Mikro schlägt auf
add('fsd_static', MIC_DROP, 0.5, db=-8, fout=0.2)                                    # Knacken in der Anlage
add('fsd_crowd_gasp', 24.9, 2.4, db=-6, fout=0.6)
add('fsd_screams', 26.0, 4.0, db=-16, off=1.0, fin=0.5, fout=1.0)

# ---------------- Stufe 4: 70.000 drängen nach vorn ----------------
amb('fsd_stadium_roar', 32, 40.05, -6)
add('fsd_sub_rumble', 32.5, 7.5, db=-8, off=1.0, fin=1.5, fout=0.5)
add('fsd_screams', SURGE, 5.5, db=-6, fin=0.3, fout=1.0)
for k, tt in enumerate([SURGE + 0.2, SURGE + 1.4, SURGE + 2.6]): add('fsd_footsteps_run', tt, 2.0, db=-8, off=k * 3.0, fout=0.5, pan=(k - 1) * 0.5)
add('fsd_metal_crash', BARRIER, 2.5, db=-2, peak_win=0.2, fout=1.0)                 # Absperrung bricht
add('fsd_metal_crash2', BARRIER + 0.35, 1.5, db=-8, off=0.1, fout=0.6, pan=-0.4)
add('fsd_crowd_gasp', BARRIER + 0.2, 2.4, db=-6, fout=0.6)

# ---------------- Stufe 5: Rechenzentrum ----------------
add('fsd_pc_fan', 40.0, BLACKOUT - 40.0, db=-10, off=2.0, fin=0.3, fout=0.05)
add('fsd_pc_fan', 42.0, BLACKOUT - 42.0, db=-8, off=12.0, fin=1.0, fout=0.05, speed=1.15)   # Lüfter drehen hoch
add('fsd_electric_hum', 40.0, BLACKOUT - 40.0, db=-14, fout=0.05)
add('fsd_alarm_beep', OVERLOAD, BLACKOUT - OVERLOAD + 1.6, db=-8, fout=0.6)
add('fsd_electric_arc', SPARK, 2.6, db=-2, fout=0.5)
add('fsd_fire_crackle', SPARK + 0.4, 48.05 - SPARK - 0.4, db=-10, fin=0.3)
add('fsd_power_down', BLACKOUT - 0.05, 1.7, db=-4, fout=0.5)
add('fsd_wind_rush', BLACKOUT + 0.2, 48.05 - BLACKOUT - 0.2, db=-16, fin=0.4)         # Löschgas strömt

# ---------------- Stufe 6: Erdbebenwarte ----------------
add('fsd_electric_hum', 48.0, 8.4, db=-22, fout=0.3)
add('fsd_phone_ring', 48.8, 3.0, db=-16, fout=0.5)
add('fsd_alarm_beep', 51.8, 4.6, db=-14, fout=0.4)
add('fsd_sub_rumble', 49.5, 6.9, db=-6, off=1.0, fin=2.0, fout=0.4)
add('fsd_glass_rattle', 51.0, 5.4, db=-14, fin=1.0, fout=0.4)
add('fsd_siren', 52.5, 3.9, db=-22, fin=1.0, fout=0.4)
add('fsd_stadium_roar', 50.5, 5.9, db=-22, off=6.0, fin=1.5, fout=0.4)              # Fans draußen auf der Straße
# 56,4 bis 57: Stille

# ---------------- Stufe 7: Sie ist zurück ----------------
add('fsd_whoosh_boom', RETURN - 0.02, 3.0, db=2, fout=1.5)
add('fsd_concert_scream', RETURN + 0.1, 5.7, db=0, fout=1.0)
add('fsd_cheer_big', RETURN + 0.3, 5.0, db=-4, fout=1.0)
amb('fsd_stadium_roar', RETURN + 1.0, 66.05, -5)
add('fsd_cheer2', 60.0, 6.05, db=-8, fin=0.5)
add('fsd_wind_rush', RETURN + 0.25, 1.4, db=-8, fout=0.6)                            # Pyro
add('fsd_wind_rush', JUMP + 1.95, 1.0, db=-10, fout=0.5)
add('fsd_fireworks', 57.6, 4.5, db=-6, fout=1.0)
add('fsd_fireworks2', 59.6, 4.0, db=-8, fout=1.0, pan=0.4)
add('fsd_fireworks3', 61.5, 4.5, db=-8, fout=1.0, pan=-0.4)
add('fsd_sub_rumble', JUMP - 0.3, 66.05 - JUMP + 0.3, db=-2, off=1.0, fin=0.6)
for k in range(int((66 - JUMP) * 2.1)): add('fsd_impact_boom2', JUMP + k / 2.1, 0.4, db=-16, fout=0.25)   # Sprünge im Takt

# ---------------- Stufe 7: das Fan-Beben ----------------
add('fsd_sub_rumble', 66.0, 9.05, db=-2, off=3.0, fin=0.3, fout=0.8)
amb('fsd_glass_rattle', 66.0, 74.5, -6)
add('fsd_alarm_beep', 66.2, 8.6, db=-16, fout=0.5)
for k, tt in enumerate([67.3, 67.9, 68.6, 69.5, 70.4, 71.6, 72.9]): add('fsd_book_thud', tt, 0.5, db=-6 - (k % 3) * 2, peak_win=0.1, fout=0.2, pan=-0.5)
add('fsd_metal_crash2', SNAP - 0.03, 1.0, db=-8, peak_win=0.1, fout=0.4)           # Feder bricht ab
add('fsd_debris', SNAP + 0.5, 1.5, db=-14, fout=0.5)
add('fsd_thunder_far', 70.2, 4.8, db=-10, fin=0.3, fout=1.5)
add('fsd_siren', 70.5, 4.3, db=-20, fin=0.5, fout=1.0)

# ---------------- Stufe 7: das Video geht viral ----------------
add('fsd_electric_hum', 75.0, 15.0, db=-28)
pings = []; t_ = 76.6
while t_ < 88.4: pings.append(t_); t_ += max(0.18, 1.1 * 0.85 ** len(pings))
for k, tt in enumerate(pings): add('fsd_notif' if k % 2 == 0 else 'fsd_notif2', tt, 0.6, db=-10 - (k % 3) * 2, fout=0.2, pan=((k * 7) % 5 - 2) * 0.15)
add('fsd_sigh', 79.3, 2.4, db=-4, fout=0.4)
add('fsd_kid_laugh', 81.2, 3.0, db=-12, off=4.0, fin=0.1, fout=0.8)
add('fsd_phone_buzz', 84.0, 1.2, db=-16, fout=0.3)
add('fsd_sigh', 86.6, 2.2, db=-8, fout=0.6, speed=0.92)

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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge05_taylor.mp4')
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
