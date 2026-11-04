"""Baut eine Folge: Zeitachse, Audio-Mix, Rendering, Muxen.

Nutzung:
  python3 tools/build.py <episode-ordner>                 # komplettes Video
  python3 tools/build.py <episode-ordner> --stills 1.0,5,12  # nur Standbilder (PNG)
Voraussetzung: tools/tts.py wurde vorher ausgeführt (build/tts.json).
"""
import sys, os, json, math, subprocess, importlib.util, multiprocessing as mp, random
import numpy as np, soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cairo
from alexlib import *  # noqa

EP = os.path.abspath(sys.argv[1])
sys.path.insert(0, EP)


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(EP, name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


script = load("script")
import alexlib as _alexlib
_alexlib.SAFE_MODE = getattr(script, "SAFE_MODE", "default")
scenes = load("scenes")
tts = json.load(open(os.path.join(EP, "build", "tts.json")))
sfx_meta = json.load(open(os.path.join(ROOT, "assets", "sfx", "sfx_meta.json")))

SR = 44100
TICKS = sfx_meta["tick_onsets"]
FLASH = round(TICKS[-1] + 0.07, 3)        # weißer Blitz nach dem letzten Tick
REVEAL = 1.57                              # Burst-Einsatz wie im Original
INTRO_LEN = 3.75
GAP, PRE, POST, END_HOLD = 0.15, 0.12, 0.28, 1.5


# ------------------------------------------------------------------ Zeitachse
def chunk_caption(s):
    words = s.split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        txt = " ".join(cur)
        if (len(cur) >= 3 or len(txt) >= 17 or w[-1] in ".,:!?") and len(txt) >= 6:
            chunks.append(txt)
            cur = []
    if cur:
        if chunks and len(" ".join(cur)) < 7:
            chunks[-1] += " " + " ".join(cur)
        else:
            chunks.append(" ".join(cur))
    return chunks


class Scene:
    pass


timeline = []
t = INTRO_LEN
for sc_def, sc_tts in zip(script.SCENES, tts["scenes"]):
    S = Scene()
    S.id, S.bg, S.clock, S.title = sc_def["id"], sc_def["bg"], sc_def["clock"], sc_def["title"]
    S.dark = sc_def.get("dark", is_dark(sc_def["bg"]))
    S.start = t
    lt = PRE
    S.starts, S.durs, S.caps = [], [], []
    for li_, ln in enumerate(sc_tts["lines"]):
        S.starts.append(lt)
        S.durs.append(ln["dur"])
        chunks = chunk_caption(ln["caption"])
        weights = [len(cn) + 4 for cn in chunks]
        tot = sum(weights)
        acc = lt
        for cn, wt in zip(chunks, weights):
            S.caps.append((acc, cn))
            acc += ln["dur"] * wt / tot
        lt += ln["dur"] + GAP + getattr(script, "PAUSE_AFTER", {}).get((sc_def["id"], li_), 0.0)
    S.dur = lt - GAP + (END_HOLD if sc_def is script.SCENES[-1] else POST)
    S.files = [ln["file"] for ln in sc_tts["lines"]]
    t += S.dur
    timeline.append(S)
TOTAL = t
NFRAMES = int(math.ceil(TOTAL * FPS))


class Ctx:
    def __init__(self, S, tl):
        self.t, self.dur, self.S = tl, S.dur, S

    def at(self, i, f=0.0):
        S = self.S
        if i >= len(S.starts):
            return S.dur
        return S.starts[i] + f * S.durs[i]


# ------------------------------------------------------------------ Frame
def draw_frame(c, tg):
    if tg < INTRO_LEN:
        scenes.draw_intro(c, tg, script.SHUFFLE, TICKS, FLASH, REVEAL, script.ROLE)
        return
    S = next((s for s in timeline if s.start <= tg < s.start + s.dur), timeline[-1])
    tl = tg - S.start
    background(c, S.bg, tg, rays=0.06)
    safe_zone(c)
    ctx = Ctx(S, tl)
    tcol = "#FFFFFF" if S.dark else INK
    if S.clock:
        clock_pill(c, S.clock, 118, pop(tl, 0.0, 0.25))
        if S.title:
            title(c, S.title, 222, tcol, pop(tl, 0.06, 0.3), size=72)
    elif S.title:
        title(c, S.title, 170, tcol, pop(tl, 0.0, 0.3), size=72)
    scenes.SCENE_DRAW[S.id](c, ctx)
    # Untertitel
    cur, since = None, 0
    for i, (ct, txt) in enumerate(S.caps):
        if tl >= ct:
            cur, since = txt, tl - ct
    # nach dem letzten Wort der Zeile kurz stehen lassen, in Pausen ausblenden
    li = max([i for i, st in enumerate(S.starts) if tl >= st] or [0])
    if tl > S.starts[li] + S.durs[li] + 0.18:
        cur = None
    caption(c, cur, since)


def render_range(args):
    a, b, path = args
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for f in range(a, b):
        c = cairo.Context(surf)
        c.set_operator(cairo.OPERATOR_SOURCE); c.set_source_rgb(0, 0, 0); c.paint(); c.set_operator(cairo.OPERATOR_OVER)
        draw_frame(c, f / FPS)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    return path


# ------------------------------------------------------------------ Audio
def load_wav(p):
    a, sr = sf.read(p)
    if a.ndim > 1:
        a = a.mean(1)
    if sr != SR:
        g = math.gcd(sr, SR)
        a = resample_poly(a, SR // g, sr // g)
    return a


def synth_pop(f0=520, dur=0.09, amp=0.18):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = f0 * (1 + 1.4 * np.exp(-tt * 60))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(ph) * np.exp(-tt * 38)


def synth_whoosh(dur=0.35, amp=0.07, seed=1):
    rnd = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rnd.standard_normal(n)
    from scipy.signal import butter, sosfilt
    out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        u = i / n
        fc = 600 + 3500 * math.sin(math.pi * u)
        sos = butter(2, [fc * 0.6, min(fc * 1.6, 16000)], "bandpass", fs=SR, output="sos")
        out[i:i + seg] = sosfilt(sos, x[i:i + seg])
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return amp * out * env / (np.abs(out).max() + 1e-9)


def synth_crickets(dur=2.2, amp=0.12, seed=3):
    """Grillenzirpen (Running Gag: niemand lacht)."""
    n = int(dur * SR); tt = np.arange(n) / SR
    out = np.zeros(n)
    rnd = np.random.default_rng(seed)
    t0 = 0.0
    while t0 < dur - 0.2:
        for k in range(3):                      # 3 Pulse pro Zirp
            a = int((t0 + k * 0.045) * SR); b = min(n, a + int(0.03 * SR))
            seg = tt[a:b] - tt[a]
            f = 4300 + rnd.uniform(-80, 80)
            out[a:b] += np.sin(2 * np.pi * f * seg) * np.sin(np.pi * seg / 0.03) ** 2
        t0 += 0.42 + rnd.uniform(-0.04, 0.04)
    env = np.minimum(1, np.minimum(tt / 0.2, (dur - tt) / 0.4))
    return amp * out * env


def build_audio(path):
    n = int((TOTAL + 0.5) * SR)
    voice = np.zeros(n)
    fx = np.zeros(n)

    def add(buf, sig, t0, g=1.0):
        i = int(t0 * SR)
        j = min(n, i + len(sig))
        if j > i:
            buf[i:j] += g * sig[: j - i]

    # Intro: Original-Ticks im Original-Rhythmus + Reveal-Burst
    tick = load_wav(os.path.join(ROOT, "assets", "sfx", "tick.wav"))
    for tk in TICKS:
        add(fx, tick, tk - 0.004, 1.0)
    rev = load_wav(os.path.join(ROOT, "assets", "sfx", "reveal.wav"))
    add(fx, rev, REVEAL - sfx_meta["reveal_onset"], 2.6)
    tdir = os.path.join(EP, "build", "tts")
    add(voice, load_wav(os.path.join(tdir, "intro_pre.wav")), 0.12)
    add(voice, load_wav(os.path.join(tdir, "intro_role.wav")), REVEAL + 0.3)
    # Szenen
    rnd = random.Random(7)
    for S in timeline:
        add(fx, synth_whoosh(seed=rnd.randint(0, 999)), S.start - 0.12)
        add(fx, synth_pop(440, amp=0.10), S.start + 0.02)
        for st, f in zip(S.starts, S.files):
            add(voice, load_wav(f), S.start + st)
            add(fx, synth_pop(rnd.choice([480, 560, 640, 720]), amp=0.08), S.start + st + 0.05)
    # Zusätzliche Effekte der Folge: script.SFX = [(szenen_id, zeile, anteil, "crickets"), ...]
    for sid, li, frac, kind in getattr(script, "SFX", []):
        S = next(s_ for s_ in timeline if s_.id == sid)
        t0 = S.start + S.starts[li] + frac * S.durs[li]
        if kind == "crickets":
            add(fx, synth_crickets(), t0)
    voice /= (np.abs(voice).max() + 1e-9)
    voice *= 0.9
    mix = voice + fx
    mix /= max(1.0, np.abs(mix).max() / 0.98)
    sf.write(path, np.stack([mix, mix], 1), SR)


# ------------------------------------------------------------------ main
if __name__ == "__main__":
    out_dir = os.path.join(EP, "build")
    os.makedirs(out_dir, exist_ok=True)
    print(f"Gesamtlänge: {TOTAL:.2f}s, {NFRAMES} Frames")
    for S in timeline:
        print(f"  {S.id:8s} {S.start:6.2f}s  +{S.dur:5.2f}s")
    if len(sys.argv) > 3 and sys.argv[2] == "--stills":
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        for ts in sys.argv[3].split(","):
            c = cairo.Context(surf)
            draw_frame(c, float(ts))
            surf.write_to_png(os.path.join(out_dir, f"still_{float(ts):06.2f}.png"))
        sys.exit(0)
    wav = os.path.join(out_dir, "mix.wav")
    build_audio(wav)
    nproc = max(1, os.cpu_count() or 1)
    per = math.ceil(NFRAMES / nproc)
    jobs = [(i * per, min(NFRAMES, (i + 1) * per), os.path.join(out_dir, f"seg_{i}.mp4")) for i in range(nproc)]
    with mp.get_context("fork").Pool(nproc) as pool:
        segs = pool.map(render_range, jobs)
    lst = os.path.join(out_dir, "segs.txt")
    with open(lst, "w") as fh:
        for s in segs:
            fh.write(f"file '{s}'\n")
    final = os.path.join(EP, os.path.basename(EP.rstrip("/")) + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-shortest", "-movflags", "+faststart", final], check=True)
    for s in segs:
        os.remove(s)
    print("fertig:", final)
