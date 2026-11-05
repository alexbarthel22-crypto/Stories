"""Builds mix.wav = voice + channel theme music + sound effects (synced to timing.json)."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
st = mv.st
t1, t2, t3 = st("Im alten"), st("Wer vorbei"), st("Was geht")
a1, a2, a3, t_end = st("Am Morgen"), st("Am Mittag"), st("Und am Abend"), st("Hättest")
tq, tsol = st("PAUSE"), st("Hier kommt")
ev = [
    # --- opener: WARTE!
    ("impact", 0.0, 1.0), ("gong", 0.0, 0.4), ("drum", 0.0, 0.6), ("whoosh", 0.02, 0.5),
    ("pop", mv.word_time("WARTE", "Dieses", 0.1), 0.45), ("pop", mv.word_time("WARTE", "niemand", 0.1), 0.5),
    ("wind", 0.0, 0.35, tq + 0.3),                                           # desert wind under the story
    # --- Egypt intro: camera flight to the Sphinx
    ("riser", t1 - 1.0, 0.35), ("whoosh", t1 - 0.05, 0.6), ("sistrum", t1 + 0.3, 0.6), ("pop", t1 + 0.35, 0.5),
    ("chirp", t1 + 0.9, 0.35), ("pop", t1 + 1.3, 0.5), ("splash", t1 + 2.4, 0.4), ("chirp", t1 + 3.1, 0.25),
    ("drum", t2, 0.7), ("pop", t2 + 0.25, 0.55), ("whoosh", t2 + 0.2, 0.4),
    # --- riddle: sphinx awakens
    ("rumble", t3 - 0.25, 0.9, 1.8), ("growl", t3 - 0.1, 0.3), ("sparkle", t3 + 0.2, 0.45), ("drum", t3, 0.6),
    *[("click", t3 + 0.25 + k * 0.18, 0.25) for k in range(8)],                # glyphs lighting up
    # enumeration: each time of day gets its own sound
    ("drum", mv.T_MORNING - 0.1, 0.75), ("chirp", mv.T_MORNING, 0.55), ("sparkle", mv.T_MORNING - 0.05, 0.3),
    ("drum", mv.T_NOON - 0.1, 0.75), ("ding", mv.T_NOON - 0.05, 0.45), ("sistrum", mv.T_NOON + 0.1, 0.45),
    ("drum", mv.T_EVENING - 0.1, 0.8), ("gong", mv.T_EVENING - 0.05, 0.45), ("owl", mv.T_EVENING + 0.4, 0.4),
    # --- question / thinking time
    ("whoosh", tq - 0.2, 0.6), ("owl", tq + 0.5, 0.3),
    *[("tick", tq + 0.25 + k * 0.5, 0.9) for k in range(3)],
    ("sparkle", st("Kleiner Tipp"), 0.45), ("pop", st("Kleiner Tipp") + 0.05, 0.6), ("pop", st("Schreib deine"), 0.6),
    # --- solution
    ("riser", tsol - 1.1, 0.45), ("whoosh", tsol - 0.15, 0.6), ("pop", tsol, 0.8), ("wind", tsol, 0.25, t_end - tsol + 1),
    ("gong", st("Es ist der"), 0.5), ("tada", st("Es ist der"), 0.8), ("pop", st("Es ist der") + 0.25, 0.5),
    ("pop", st("Es ist der") + 0.5, 0.5), ("pop", st("Es ist der") + 0.75, 0.5),
    ("whoosh", a1, 0.5), ("chirp", a1 + 0.4, 0.45), ("drum", a1, 0.5),
    *[("click", a1 + 0.5 + k * 0.32, 0.35) for k in range(int((a2 - a1 - 0.6) / 0.32))],   # baby crawls
    ("sparkle", a2 - 0.15, 0.5), ("whoosh", a2 - 0.1, 0.45), ("drum", a2, 0.5), ("ding", a2 + 0.05, 0.4),
    *[("step", a2 + 0.3 + k * 0.3, 0.8) for k in range(int((a3 - a2 - 0.4) / 0.3))],        # adult walks
    ("sparkle", a3 - 0.15, 0.5), ("whoosh", a3 - 0.1, 0.45), ("drum", a3, 0.5), ("owl", a3 + 0.6, 0.3),
    *[(("clink" if k % 2 else "step"), a3 + 0.3 + k * 0.52, 0.5) for k in range(int((t_end - a3 - 0.4) / 0.52))],
    # --- outro
    ("whoosh", t_end - 0.15, 0.6), ("sistrum", t_end, 0.5), ("pop", t_end, 0.7), ("pop", t_end + 0.2, 0.6),
    ("pop", st("Schreib's") + 0.3, 0.7), ("ding", st("Schreib's") + 1.3, 0.6)]
# shout "WARTE!" louder: boost the first word with soft saturation
import numpy as np, soundfile as sf
v, sr = sf.read(os.path.join(HERE, "voice.wav"), dtype="float32")
env = np.convolve(np.abs(v), np.ones(int(0.03 * sr)) / int(0.03 * sr), mode="same")
quiet = np.where(env[int(0.25 * sr):int(1.2 * sr)] < 0.02)[0]
w_end = int(0.25 * sr) + (quiet[0] if len(quiet) else int(0.45 * sr))
g = np.ones(len(v), np.float32)
g[:w_end] = 2.6
ramp = int(0.05 * sr)
g[w_end:w_end + ramp] = np.linspace(2.6, 1.0, ramp)
v = v * 0.62                                    # rest of the voice a bit lower, WARTE stands out
v = np.tanh(v * g * 1.3) / np.tanh(1.3)
sf.write(os.path.join(HERE, "cache", "voice_boost.wav"), v, sr)
print("WARTE boosted until", round(w_end / sr, 2), "s")
mix(os.path.join(HERE, "cache", "voice_boost.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-16.0)
print("mix.wav", round(mv.END, 2), "s")
