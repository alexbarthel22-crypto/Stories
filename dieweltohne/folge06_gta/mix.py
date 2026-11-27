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
VANISH, RETURN = 10.0, 55.0
WK = [[10, 10], [17, 9.0], [24, 7.8], [31, 6.4], [39, 4.6], [47, 2.4], [55, 0]]
PAPA_UP, BRAKE, STOP, FREQ0, CITY_OUT, EU_OUT = 18.6, 26.6, 28.2, 32.0, 40.5, 48.4
FLASH_ON, POWER_BACK, TV_ON, DOOR, CEIL, TV_OFF = 58.6, 66.0, 73.6, 81.0, 82.4, 84.6


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


# Fernseher-Klang: dumpfer (Tiefpass) – Spielgeräusche kommen aus dem TV
def tv(name, at, dur, db, **k):
    global mix
    keep = mix.copy(); mix[:] = 0
    add(name, at, dur, db=db, **k)
    s, e = int(at * SR), int(min(DUR, at + dur + 0.5) * SR)
    seg = mix[s:e].copy(); a = 0.25
    for i in range(1, len(seg)): seg[i] = seg[i - 1] + a * (seg[i] - seg[i - 1])
    mix = keep; mix[s:e] += seg


# ---------------- Countdown-Ticks ----------------
ticks = [float(s_) for s_ in range(1, 10)]
T_ = 10.0
while T_ < RETURN:
    if int(world_left(T_)) != int(world_left(T_ + 0.01)): ticks.append(T_ + 0.01)
    T_ += 0.01
for tt in ticks: tick(tt, -12 if tt < 7 or (VANISH < tt < 52) else -6)

# ---------------- Sein Zimmer: Spiel läuft (0–10) ----------------
amb('fsd_pc_fan', 0.0, 10.0, -34)
tv('fsd_car_rev', 0.0, 3.4, -15, off=0.3)
tv('fsd_siren_pass', 1.0, 6.0, -20)
tv('fsd_tire_screech', 3.5, 1.6, -17, peak_win=1.0)
tv('fsd_car_rev', 5.2, 4.8, -17, off=1.5)
for tt in [0.6, 1.4, 2.2, 4.1, 5.0, 6.3, 7.7, 8.6, 9.3]: add('fsd_switch', tt, 0.12, db=-30, peak_win=0.05)

# ---------------- Stufe 1: weg (10–17) ----------------
add('fsd_glitch', 9.95, 0.5, db=-12, peak_win=0.3)
add('fsd_notif', 10.45, 1.2, db=-16)
amb('fsd_pc_fan', 10.0, 17.0, -36)
add('fsd_gasp', 10.9, 1.2, db=-14, peak_win=0.6)
add('fsd_heartbeat', 11.5, 5.5, db=-18)
for k, tt in enumerate([13.3, 13.5, 13.62, 13.8, 13.95, 14.1, 14.4, 14.55, 14.7]): add('fsd_switch', tt, 0.1, db=-22, peak_win=0.05, pan=0.1 * (-1) ** k)

# ---------------- Stufe 2: Papa (17–24) ----------------
amb('fsd_electric_hum', 17.0, 24.0, -36)
add('fsd_soft_thud', PAPA_UP + 0.05, 0.6, db=-12, peak_win=0.2)
add('fsd_shout_man', PAPA_UP + 0.3, 1.8, db=-8, peak_win=1.0)
add('fsd_plastic_clatter', PAPA_UP + 0.62, 0.8, db=-16, peak_win=0.3)
add('fsd_sigh', 21.4, 1.6, db=-15, peak_win=1.0)

# ---------------- Stufe 3: Straße (24–31) ----------------
amb('fsd_city_hum', 24.0, 31.0, -24)
add('fsd_door', 24.0, 1.0, db=-15, peak_win=0.5)
for k, tt in enumerate([24.3 + i * 0.44 for i in range(6)]): add('fsd_steps_slow', tt, 0.35, db=-20, peak_win=0.2)
add('fsd_car_pass', BRAKE - 2.2, 2.4, db=-14, fin=1.5, peak_win=2.0)
add('fsd_tire_screech', BRAKE, STOP - BRAKE + 0.2, db=-6, peak_win=1.2, fout=0.25)
add('fsd_gasp', BRAKE + 0.25, 1.0, db=-11, peak_win=0.6)
add('fsd_car_horn', STOP + 0.5, 1.2, db=-9, peak_win=1.0)
add('fsd_heartbeat2', STOP + 0.2, 2.6, db=-15)

# ---------------- Stufe 4: Netzleitstelle (31–39) ----------------
amb('fsd_electric_hum', 31.0, 39.0, -28)
add('fsd_keyboard', 31.2, 2.5, db=-24)
add('fsd_monitor_alarm', 35.2, 3.8, db=-15)
add('fsd_klaxon', 36.2, 2.8, db=-17, fin=0.3)
add('fsd_chair_scrape', 36.0, 0.8, db=-17, peak_win=0.5)
add('fsd_sub_rumble', 34.0, 5.0, db=-20, fin=2.0)

# ---------------- Stufe 5: Stadt (39–47) ----------------
amb('fsd_wind', 39.0, 47.0, -27)
for k, tt in enumerate([CITY_OUT - 0.1, CITY_OUT + 1.5, CITY_OUT + 3.4]):
    add('fsd_electric_arc', tt, 0.6, db=-12 - k, peak_win=0.3)
    add('fsd_impact_boom', tt + 0.05, 1.8, db=-12 - 2 * k, peak_win=0.4)
for i in range(14): add('fsd_power_down', CITY_OUT + i * 0.48, 0.6, db=-26 - (i % 3) * 2, peak_win=0.4, pan=(i % 5 - 2) * 0.2)
add('fsd_dog', 43.5, 2.0, db=-26, pan=-0.4); add('fsd_dog_howl', 45.0, 2.0, db=-30, pan=0.4)

# ---------------- Stufe 6: Europa (47–55) ----------------
add('fsd_sub_rumble', 47.0, 8.0, db=-17, fin=0.8)
add('fsd_whoosh_fast', 47.0, 1.2, db=-20)
for i, o in enumerate([0.0, 0.5, 0.9, 1.2, 1.6, 1.9, 2.3, 2.7, 3.1, 3.5, 4.2, 4.8]): add('fsd_impact_boom2', EU_OUT + o, 1.4, db=-21 - (i % 3), peak_win=0.4, pan=(i % 4 - 1.5) * 0.25)

# ---------------- Stufe 7: dunkel (55–64) ----------------
add('fsd_power_down', 55.0, 1.2, db=-18, peak_win=0.8)
amb('fsd_crickets', 55.3, 64.0, -34)
add('fsd_breathing', 56.0, 7.0, db=-24)
add('fsd_switch', FLASH_ON - 0.02, 0.15, db=-17, peak_win=0.05)
add('fsd_siren_eu', 60.0, 4.0, db=-30, fin=1.0, fout=1.0)

# ---------------- Strom zurück (64–72) ----------------
add('fsd_electric_hum', POWER_BACK - 0.2, 6.0, db=-22, fin=0.8)
for i in range(14): add('fsd_breaker', POWER_BACK + i * 0.38, 0.4, db=-24 - (i % 3) * 2, peak_win=0.2, pan=(i % 5 - 2) * 0.2)
add('fsd_cheer2', POWER_BACK + 1.2, 4.5, db=-25, fin=1.0, fout=1.5)
amb('fsd_city_hum', POWER_BACK + 0.5, 72.0, -30)

# ---------------- Fernseher an, volle Lautstärke (72–84.6) ----------------
amb('fsd_crickets', 72.0, TV_ON, -34)
add('fsd_switch', TV_ON - 0.05, 0.15, db=-14, peak_win=0.05)
add('fsd_techno', TV_ON, TV_OFF - TV_ON, db=-5, fout=0.05)
add('fsd_car_rev', TV_ON + 0.1, 3.0, db=-6)
add('fsd_tire_screech', TV_ON + 2.8, 1.5, db=-7, peak_win=1.0)
add('fsd_siren_pass', TV_ON + 1.0, 5.5, db=-12)
add('fsd_explosion', TV_ON + 4.6, 2.0, db=-8, peak_win=0.5)
add('fsd_gasp', TV_ON + 0.12, 1.0, db=-6, peak_win=0.6)
add('fsd_soft_thud', TV_ON + 0.35, 0.6, db=-10, peak_win=0.2)
add('fsd_door', DOOR - 0.1, 1.0, db=-10, peak_win=0.5)
add('fsd_switch', CEIL - 0.03, 0.15, db=-10, peak_win=0.05)
# Er schaltet aus: Stille
add('fsd_power_down', TV_OFF, 0.9, db=-14, peak_win=0.6)
add('fsd_sigh', 85.4, 1.6, db=-17, peak_win=1.0)
add('fsd_impact_boom2', 86.7, 2.6, db=-12, peak_win=0.4)
# ---------------- Ausgabe ----------------
peak = np.abs(mix).max()
if peak > 0.98: mix *= 0.98 / peak
tmp = os.path.join(HERE, 'mix_roh.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', tmp], input=mix.tobytes(), check=True)
out = os.path.join(HERE, 'mix.wav')
# TikTok-Lautheit: ca. -14 LUFS, Spitzen begrenzt
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'acompressor=threshold=-30dB:ratio=3:attack=15:release=400:makeup=6,loudnorm=I=-13.5:TP=-1.5:LRA=11,alimiter=limit=0.74:attack=1:release=60:level=false', '-ar', str(SR), '-c:a', 'pcm_s16le', out], check=True)
os.remove(tmp)
print('mix.wav fertig, Ticks:', len(ticks))

if '--mux' in sys.argv:
    vid = os.path.join(HERE, 'video_stumm.mp4'); fin = os.path.join(HERE, 'folge06_gta.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', out, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-b:v', '6800k', '-maxrate', '9500k', '-bufsize', '14000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-t', '90', '-movflags', '+faststart', fin], check=True)
    print('fertig:', fin)

# Quellenangaben für die Videobeschreibung
cred = []
for f in sorted(os.listdir(RAW)):
    if f.endswith('.json') and f[:-5] in _cache and _cache[f[:-5]] is not None:
        m = json.load(open(os.path.join(RAW, f)))
        src = 'Freesound, über den Datensatz FSD50K' if m['artist'].startswith('Freesound') else 'Wikimedia Commons'
        cred.append(f"- {m['title'][5:]} – {m['license']} ({src})")
open(os.path.join(HERE, 'quellen_geraeusche.md'), 'w').write('# Geräusche (echte Aufnahmen)\n\nAlle Geräusche sind echte Aufnahmen unter CC0 (frei nutzbar, keine Namensnennung nötig).\n\n' + '\n'.join(cred) + '\n')
