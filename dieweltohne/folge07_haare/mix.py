"""Mischt die echten Aufnahmen (sfx_raw/*.wav) bildgenau zur Zeitleiste und legt sie unter das Video.

python3 mix.py            -> mix.wav
python3 mix.py --mux      -> zusätzlich fertiges Video folge07_haare.mp4
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


def lowpass(seg, fc):
    """Dumpf wie durch Watte: weicher Tiefpass im Frequenzbereich."""
    F = np.fft.rfft(seg, axis=0); f = np.fft.rfftfreq(len(seg), 1 / SR)
    F *= (1 / np.sqrt(1 + (f / fc) ** 4))[:, None]
    return np.fft.irfft(F, n=len(seg), axis=0).astype(np.float32)


def add(name, at, dur=None, db=0.0, off=0.0, fin=0.02, fout=0.05, speed=1.0, pan=0.0, peak_win=None, lp=None):
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
    if lp: seg = lowpass(seg, lp)
    n = len(seg); a = int(fin * SR); b = int(fout * SR)
    if a: seg[:a] *= np.linspace(0, 1, a)[:, None]
    if b: seg[-b:] *= np.linspace(1, 0, b)[:, None]
    seg *= 10 ** (db / 20)
    if pan: seg[:, 0] *= 1 - max(0, pan); seg[:, 1] *= 1 + min(0, pan)
    s = int(at * SR); e = min(len(mix), s + n)
    mix[s:e] += seg[:e - s]


# ---------------- Zeitleiste (identisch zu src/timeline.js) ----------------
VANISH, RETURN = 10.0, 56.0
WK = [[10, 10], [17, 9.3], [24, 8.4], [31, 7.4], [38, 6.2], [46, 4.2], [56, 0]]
DEAF, CROWD_FALL, JUMP, MISS, FLOCK_BREAK, SWING, CRANE_HIT, CRANE_FALL = 24.0, 26.2, 33.0, 34.1, 40.6, 49.0, 51.6, 52.6
D = 500  # Grenzfrequenz für "taub" (Hz)


def world_left(T):
    if T <= WK[0][0]: return 10
    for i in range(1, len(WK)):
        if T <= WK[i][0]:
            a, va = WK[i - 1]; b, vb = WK[i]
            return va + (vb - va) * (T - a) / (b - a)
    return 0


def amb(name, t0, t1, db, off=0.0, xf=0.8, speed=1.0, seg=None, lp=None):
    x = load(name)
    if x is None: return
    L = (seg if seg else len(x) / SR / speed - off)
    t = t0
    while t < t1:
        d = min(L, t1 - t + xf)
        add(name, t, d, db=db, off=off, fin=xf if t > t0 else 0.3, fout=xf, speed=speed, lp=lp)
        t += max(1.0, L - xf)


def tick(T, db):
    add('fsd_clock_tick', T - 0.005, 0.16, db=db, off=0.0, fout=0.05)


# ---------------- Zimmer: Selfie ----------------
amb('fsd_birdsong', 0, 17.05, -26)
add('fsd_giggle', 0.7, 2.0, db=-10, fout=0.4)
add('fsd_wind_rush', 1.15, 0.8, db=-20, fin=0.1, fout=0.4)                              # Haare werfen
add('fsd_wind_rush', 6.35, 0.8, db=-20, fin=0.1, fout=0.4)
add('fsd_giggle', 6.9, 2.0, db=-12, off=0.4, fout=0.5)
for s_ in range(1, 10): tick(s_, -6 if s_ < 7 else 0)
add('fsd_sub_rumble', 7.0, 3.05, db=-10, off=1.0, fin=2.5, fout=0.05)
add('fsd_whoosh_boom', 9.99, 2.5, db=0, fout=1.2)
add('fsd_gasp_f', 10.25, 1.0, db=-4, peak_win=0.3, fout=0.3)
add('fsd_scream_girl', 10.6, 2.0, db=-3, peak_win=1.0, fin=0.02, fout=0.6)
add('fsd_cat_meow', 13.7, 1.0, db=-6, peak_win=0.5, fout=0.3)
add('fsd_cat_meow', 15.3, 1.0, db=-9, peak_win=0.5, fout=0.3, speed=0.9)
add('fsd_heartbeat2', 14.5, 2.6, db=-18, fin=1.0, fout=0.6)                              # erster Schwindel

# ---------------- Stufe 2: Winter ----------------
amb('fsd_wind_winter', 17, 24.05, -10)
add('fsd_crowd_gasp', 17.25, 2.0, db=-8, fout=0.5)
add('fsd_shout_hey', 17.6, 0.8, db=-12, peak_win=0.3, fout=0.2, pan=-0.3)
add('fsd_snow_steps', 18.2, 3.5, db=-14, fin=0.2, fout=0.6, pan=0.3)                     # Herumhüpfen im Schnee
add('fsd_dog_yip', 19.0, 1.4, db=-10, peak_win=0.4, fout=0.3, pan=0.4)
add('fsd_dog_yip', 21.3, 1.2, db=-13, peak_win=0.4, fout=0.3, pan=0.4, speed=0.95)
add('fsd_screams', 20.5, 1.6, db=-18, off=1.0, fin=0.1, fout=0.6, pan=-0.4)
add('fsd_heartbeat2', 22.2, 1.85, db=-16, fin=0.8, fout=0.2)

# ---------------- Stufe 3: Festival (ab DEAF: alles dumpf) ----------------
amb('fsd_techno2', 24.0, 24.95, 2)
add('fsd_fest_cheer', 24.0, 0.95, db=-6, fout=0.05)
amb('fsd_techno2', 24.95, 31.05, -18, lp=D)
add('fsd_fest_cheer', 24.95, 6.1, db=-24, lp=D, fout=1.0)
add('fsd_ring_tone', 24.95, 3.0, db=-20, fin=0.05, fout=2.0)                            # Pfeifen im Ohr
amb('fsd_heartbeat2', 25.0, 56.0, -8)
for k in range(9): add('fsd_body_fall', CROWD_FALL + 0.15 + k * 0.28, 0.5, db=-6 - k, off=0.45 if k % 2 else 4.55, fout=0.2, pan=((k % 3) - 1) * 0.5, lp=900)
add('fsd_sub_rumble', CROWD_FALL, 4.0, db=-8, off=1.0, fin=0.1, fout=1.5)

# ---------------- Stufe 4: Parkour ----------------
amb('fsd_dust_wind', 31, 38.05, -16, lp=D)
add('fsd_run', 31.0, 2.0, db=-8, off=1.0, fout=0.1, lp=900)
add('fsd_wind_rush', JUMP, 1.4, db=-10, fin=0.1, fout=0.4, lp=1200)
add('fsd_body_fall', MISS, 0.7, db=0, off=0.45, fout=0.3, lp=1000)                      # Aufprall an der Kante
add('fsd_soft_thud', MISS + 0.02, 0.5, db=-4, peak_win=0.1, lp=800)
add('fsd_body_fall', MISS + 1.27, 0.8, db=0, off=4.55, fout=0.3, lp=1000)               # Vordach
add('fsd_gravel', MISS + 1.3, 1.2, db=-10, peak_win=0.3, fout=0.4, lp=1500)

# ---------------- Stufe 5: Stare ----------------
amb('fsd_bird_flock', 38, FLOCK_BREAK + 0.6, -12, lp=D)
add('fsd_birds_flap', 38.5, 3.0, db=-14, lp=1200, fout=0.8)
add('fsd_birds_flap', FLOCK_BREAK, 3.0, db=-8, lp=1200, fout=1.0)
import random as _r
_r.seed(7)
for k in range(26):
    tt = 42.6 + _r.random() * 3.3
    add('fsd_soft_thud', tt, 0.4, db=-10 - _r.random() * 12, peak_win=0.1, pan=_r.uniform(-0.7, 0.7), lp=1500)
add('fsd_car_horn', 44.6, 1.2, db=-18, lp=D, fout=0.3)

# ---------------- Stufe 6: Kran ----------------
amb('fsd_city_day', 46, 56.0, -20, lp=D)
add('fsd_winch', 46.4, 3.0, db=-14, lp=1200, fout=0.6)
add('fsd_metal_groan', SWING + 0.2, 3.0, db=-4, lp=1200, fout=0.8)
add('fsd_metal_groan', 50.6, 2.0, db=-8, lp=1200, fout=0.6, speed=0.85)
add('fsd_glass_big', CRANE_HIT, 4.0, db=0, peak_win=0.2, lp=1500, fout=1.5)
add('fsd_impact_boom2', CRANE_HIT, 2.0, db=-6, fout=1.0)
add('fsd_metal_crash', CRANE_FALL, 2.5, db=-4, peak_win=0.2, lp=1200, fout=1.0)
add('fsd_building_collapse', CRANE_FALL + 2.6 - 0.9, 4.5, db=0, lp=900, fout=1.5)
add('fsd_rubble', CRANE_FALL + 2.7, 2.5, db=-4, lp=900, fout=0.8)
add('fsd_sub_rumble', CRANE_FALL + 2.6, 3.0, db=-4, off=1.0, fin=0.05, fout=1.2)

# ---------------- Stufe 7: Haare zurück, Gehör nicht ----------------
add('fsd_whoosh_boom', RETURN - 0.3, 2.5, db=-6, speed=1.2, fout=1.2, lp=1200)
amb('fsd_heartbeat2', 56.0, 89.5, -14)
amb('fsd_ring_tone', 56.3, 89.0, -27)                                                    # leises Dauerpfeifen
add('fsd_crowd_murmur2', 56.2, 7.8, db=-22, lp=350, fin=1.0, fout=1.0)
amb('fsd_wind_winter', 64, 76.05, -16, lp=D)
add('fsd_siren', 66.0, 9.0, db=-22, lp=D, fin=2.0, fout=2.0)
add('fsd_dog_yip', 69.5, 1.2, db=-20, peak_win=0.4, lp=D)
amb('fsd_birdsong', 76, 89.5, -28, lp=D)
add('fsd_sub_rumble', 80.0, 9.0, db=-14, off=1.0, fin=3.0, fout=3.0)

# ---------------- Countdown der 10 Sekunden ----------------
ticks = []; last = 10
for f in range(int(VANISH * 30), int(RETURN * 30) + 1):
    v = world_left(f / 30)
    if int(v * 10) < int(last * 10): ticks.append(f / 30)
    last = v
for T in ticks: tick(T, -15 + (4 if T > 51 else 0))

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
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge07_haare.mp4')
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
