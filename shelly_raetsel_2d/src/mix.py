"""Tonmischung: Stimme (mit Pausen), leise Ukulele-Musik, Geräusche."""
import subprocess, numpy as np, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import g, gn, GAPS, END, T_DANN, TW, NEW, nw, _norm

SR = 48000
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


N = int(END * SR) + SR
out = np.zeros((N, 2), np.float32)
fs = {k: load(f'{ROOT}/audio/fs/{k}.mp3') for k in
      ['bubbles', 'click', 'ding', 'doors', 'elev', 'gull', 'heels', 'music', 'pop', 'rain', 'steps', 'swoosh', 'tada', 'boom',
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
t_eve, t_ride, t_home, t_aber = TW('jeden'), TW('boot') + 0.2, TW('geht') + 0.1, TW('aber')
t_ride2, t_dort, t_ihre, t_denn = TW('shelly', 1), TW('dort'), TW('nachbar') - 0.2, TW('denn')
t_eines, t_rain2 = TW('eines'), TW('shelly', 3)
t_top = TW('oben', 0) + 0.1
t_am = TW('nächsten') - 0.2
t_und = gn(next(w[1] for w in NEW if _norm(w[0]) == 'und' and w[1] > nw('sonne')))
t10b = TW('zehnten')
t_warum = TW('warum')
put('boom', 0.0, -4, fade=0.01)
POPS = [0.3, t_eve + 0.05, t_eve + 0.4, TW('ganz'), TW('morgen'), TW('seltsam'),
        t_dort + 0.4, TW('letzten'), TW('soph'), TW('laura'), TW('wundern'), TW('wundern') + 0.18,
        TW('gesund'), TW('sportlich'), TW('probleme'), t_eines + 0.05, TW('regnet'), t_rain2 + 0.1, TW('direkt'),
        t_am + 0.05, t10b, t_warum, g(48.05), g(49.52), g(51.93), g(54.77), g(55.89), g(56.91), g(61.71),
        g(65.10), g(66.97), g(69.79), g(70.64), g(71.10), g(71.60), TW('willst') - 0.15, TW('willst') + 0.45,
        TW('willst') + 0.75, TW('willst') + 0.85, T_DANN]
for t in POPS:
    put('pop', t, -9)
for t in [t_eve, t_aber, t_dort, t_ihre, t_denn, t_eines, t_rain2, t_am, t_und, t_warum, g(54.77), g(70.64)]:
    put('swoosh', t - 0.12, -12)
# Aufzug-Fahrten (Summen) + Ankunft
for a, b in [(t_ride, t_home - 0.25), (t_ride2 + 0.3, TW('zehnte')), (t_rain2 + 0.95, t_top), (t_und + 0.2, t10b)]:
    bed('elev', a, b + 0.2, -20, 0.25)
for t in [t_home - 0.25, TW('zehnte'), t_top, t10b]:
    put('ding', t, -10)
for t in [t_ride - 0.6, t_home - 0.15, t_aber + 1.3, t_dort - 0.5, t10b + 0.15, t_top + 0.1]:
    put('doors', t, -16, dur=1.2)
# Schritte
bed('steps', t_dort + 0.2, t_denn, -16, 0.3)
bed('steps', t_denn, t_denn + 1.2, -18, 0.2, off=3)
bed('heels', t_eve + 0.3, t_ride - 0.7, -18, 0.2)
# Strand: Wellen + Möwen
for a, b in [(t_eve, t_ride), (t_denn, t_eines), (t_am, t_und), (g(70.64), END)]:
    bed('waves', a, b, -20, 0.3)
    bed('gull', a, b, -24, 0.3, off=2)
# Regen
bed('rain', t_eines, t_rain2, -12, 0.3)
bed('rain', t_rain2, t_top + 0.1, -24, 0.3)
bed('rain', t_top + 0.1, t_am, -12, 0.15)
bed('rain', g(65.10), g(70.64), -28, 0.6)
# Unterwasser
bed('bubbles', 0.0, t_eve, -20, 0.3)
bed('bubbles', t_warum, g(54.77), -24, 0.5)
# Knopfdrücke
for t in [g(60.31), g(64.23), g(68.97)]:
    put('click', t, -6)
put('ding', g(68.97) + 0.15, -9)
put('tada', g(69.79), -14, fade=0.1)
put('click', T_DANN + 0.7, -6)

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
mix = voice * db(5) + out   # ohne Musik
mix = mix[:int(END * SR)]
tmp = f'{ROOT}/audio/mix_raw.wav'
import wave
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(tmp, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', 'acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=4,alimiter=limit=0.9:level=false,loudnorm=I=-9:TP=-0.8:LRA=6', '-ar', str(SR),
                f'{ROOT}/audio/final_mix.wav'], check=True)
os.remove(tmp)
print('ok', END)
