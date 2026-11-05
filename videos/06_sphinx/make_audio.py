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
ev = [("impact", 0.0, 0.9), ("whoosh", 0.02, 0.5),                     # shouted "WARTE!"
      ("wind", 0.0, 0.35, st("PAUSE")),                                  # desert wind under the story
      ("whoosh", t1 - 0.1, 0.5), ("pop", t1 + 0.3, 0.6), ("pop", t1 + 1.2, 0.5),
      ("pop", t2, 0.6), ("pop", t2 + 0.25, 0.6),
      ("growl", t3 - 0.2, 0.35), ("pop", t3, 0.6),                       # sphinx eyes light up
      ("ding", mv.T_MORNING - 0.1, 0.4), ("ding", mv.T_NOON - 0.1, 0.4), ("ding", mv.T_EVENING - 0.1, 0.4),
      ("whoosh", st("PAUSE") - 0.2, 0.6),
      *[("tick", st("PAUSE") + 0.25 + k * 0.5, 0.9) for k in range(3)],
      ("pop", st("Kleiner Tipp"), 0.7), ("pop", st("Schreib deine"), 0.6),
      ("whoosh", st("Hier kommt") - 0.15, 0.6), ("pop", st("Hier kommt"), 0.8),
      ("wind", st("Hier kommt"), 0.25, t_end - st("Hier kommt") + 1),
      ("tada", st("Es ist der"), 0.8),
      ("pop", a1, 0.6), ("pop", a1 + 0.35, 0.6),
      *[("click", a1 + 0.5 + k * 0.32, 0.35) for k in range(int((a2 - a1 - 0.6) / 0.32))],     # baby crawls
      ("pop", a2, 0.6), ("pop", a2 + 0.35, 0.6),
      *[("step", a2 + 0.3 + k * 0.3, 0.8) for k in range(int((a3 - a2 - 0.4) / 0.3))],        # adult walks
      ("pop", a3, 0.6), ("pop", a3 + 0.35, 0.6),
      *[(("clink" if k % 2 else "step"), a3 + 0.3 + k * 0.52, 0.5) for k in range(int((t_end - a3 - 0.4) / 0.52))],  # cane taps
      ("whoosh", t_end - 0.15, 0.6), ("pop", t_end, 0.8), ("pop", t_end + 0.2, 0.6),
      ("pop", st("Schreib's") + 0.4, 0.7), ("ding", st("Schreib's") + 2.0, 0.6)]
mix(os.path.join(HERE, "voice.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-16.0)
print("mix.wav", round(mv.END, 2), "s")
