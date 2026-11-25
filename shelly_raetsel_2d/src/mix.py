"""Tonmischung: Stimme (mit Pausen), leise Ukulele-Musik, Geräusche."""
import subprocess, numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import g, gn, GAPS, END

SR = 48000
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


N = int(END * SR) + SR
out = np.zeros((N, 2), np.float32)
fs = {k: load(f'{ROOT}/audio/fs/{k}.mp3') for k in
      ['bubbles', 'click', 'ding', 'doors', 'elev', 'gull', 'music', 'pop', 'rain', 'steps', 'swoosh', 'tada', 'train',
       'waves', 'whoosh']}


def db(x):
    return 10 ** (x / 20)


def put(name, t, gain_db=0.0, dur=None, fade=0.05, off=0.0):
    s = fs[name]
    a = int(off * SR)
    s = s[a:a + int(dur * SR)] if dur else s[a:]
    s = s.copy()
    f = int(fade * SR)
    if f and len(s) > 2 * f:
        ramp = np.linspace(0, 1, f)[:, None]
        s[:f] *= ramp
        s[-f:] *= ramp[::-1]
    i = int(t * SR)
    n = min(len(s), N - i)
    if n > 0:
        out[i:i + n] += s[:n] * db(gain_db)


def bed(name, t0, t1, gain_db, fade=0.4, off=0.0):
    """Schleife zwischen t0 und t1."""
    s = fs[name]
    L = int((t1 - t0) * SR)
    reps = int(np.ceil((L + int(off * SR)) / len(s))) + 1
    lp = np.concatenate([s] * reps)[int(off * SR):int(off * SR) + L].copy()
    f = int(fade * SR)
    if len(lp) > 2 * f:
        r = np.linspace(0, 1, f)[:, None]
        lp[:f] *= r
        lp[-f:] *= r[::-1]
    i = int(t0 * SR)
    out[i:i + len(lp)] += lp * db(gain_db)


# ---------------- Geräusche
POPS = [1.1, 2.6, 4.9, 8.42, 9.2, g(6.36), g(8.86), g(12.57), g(14.85), g(19.93), g(21.26), g(24.02), g(25.11),
        g(25.57), g(25.75), g(27.20), g(27.69), g(29.83), g(30.86), g(33.41), g(35.28), g(35.93), g(38.59), g(40.73),
        g(42.37), g(45.78), g(47.35), g(48.05), g(49.52), g(51.93), g(54.77), g(55.89), g(56.91), g(61.71),
        g(65.10), g(66.97), g(69.79), g(70.64), g(71.10), g(71.60), g(72.99), g(72.99) + 0.6,
        g(72.99) + 0.9, g(72.99) + 1.0, gn(81.2)]
for t in POPS:
    put('pop', t, -9)
for t in [6.94, 9.0, g(10.95), g(13.86), g(30.81), g(35.23), g(42.32), g(47.35), g(54.77), g(70.64)]:
    put('swoosh', t - 0.12, -12)
# Aufzug-Fahrten (Summen) + Ankunft
for a, b in [(g(6.26) + 3.2, g(10.95)), (g(16.57), g(18.7)), (g(30.81) + 2.0, g(34.2)), (g(37.87) + 2.1, g(41.66)),
             (g(44.63), g(46.4))]:
    bed('elev', a, b + 0.2, -20, 0.25)
for t in [g(18.72), g(34.2), g(41.66), g(46.4)]:
    put('ding', t, -10)
for t in [g(6.26) + 1.4, g(19.0), g(46.6), g(30.81) + 1.5, g(41.75) + 0.1]:
    put('doors', t, -16, dur=1.2)
# Schritte (Treppe)
bed('steps', g(19.33) + 0.2, g(26.47), -16, 0.3)
bed('steps', g(26.47), g(26.47) + 1.2, -18, 0.2, off=3)
# Strand: Wellen + Möwen
for a, b in [(g(10.95), g(13.86)), (g(26.47), g(30.81) + 1.9), (g(42.32), g(44.43)), (g(70.64), END)]:
    bed('waves', a, b, -20, 0.3)
    bed('gull', a, b, -24, 0.3, off=2)
put('train', g(10.95), -18, dur=2.9, fade=0.4)
# Regen
bed('rain', g(35.23), g(37.87), -12, 0.3)
bed('rain', g(37.87), g(41.75), -24, 0.3)
bed('rain', g(41.75), g(42.32), -12, 0.15)
bed('rain', g(65.10), g(70.64), -28, 0.6)
# Unterwasser
bed('bubbles', 0.0, 9.0, -20, 0.3)
bed('bubbles', g(47.35), g(54.77), -24, 0.5)
# Knopfdrücke
for t in [g(60.31), g(64.23), g(68.97)]:
    put('click', t, -6)
put('ding', g(68.97) + 0.15, -9)
put('tada', g(69.79), -14, fade=0.1)
put('click', gn(81.2) + 0.7, -6)

# ---------------- Musik (leise, Schleife)
mus = np.zeros_like(out)
s = fs['music']
reps = int(np.ceil(N / len(s))) + 1
xf = int(0.5 * SR)
seq = s.copy()
for _ in range(reps):
    r = np.linspace(0, 1, xf)[:, None]
    seq = np.concatenate([seq[:-xf], seq[-xf:] * r[::-1] + s[:xf] * r, s[xf:]])
    if len(seq) > N:
        break
mus[:] = seq[:N]
fade_out = int(1.5 * SR)
end_i = int(END * SR)
mus[end_i - fade_out:end_i] *= np.linspace(1, 0, fade_out)[:, None]
mus[end_i:] = 0

# ---------------- Stimme mit Pausen
vo = load(f'{ROOT}/audio/vo.wav')
voice = np.zeros_like(out)
cuts = [0.0] + [a for a, d in GAPS] + [len(vo) / SR]
shift = 0.0
for k in range(len(cuts) - 1):
    a, b = int(cuts[k] * SR), int(cuts[k + 1] * SR)
    i = int((cuts[k] + shift) * SR)
    voice[i:i + (b - a)] += vo[a:b]
    if k < len(GAPS):
        shift += GAPS[k][1]

# Ducking der Musik unter der Stimme
env = np.abs(voice).mean(1)
win = int(0.25 * SR)
env = np.convolve(env, np.ones(win) / win, 'same')
duck = 1 - 0.45 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
mix = voice * db(2) + out + mus * db(-17) * duck[:, None]
mix = mix[:int(END * SR)]
tmp = f'{ROOT}/audio/mix_raw.wav'
import wave
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(tmp, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', 'loudnorm=I=-13:TP=-1.0:LRA=8', '-ar', str(SR),
                f'{ROOT}/audio/final_mix.wav'], check=True)
os.remove(tmp)
print('ok', END)
