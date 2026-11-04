"""Builds mix.wav = voice + channel theme music + sound effects (synced to timing.json)."""
import json, os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
st = mv.st
t2, t3, t4, t5 = st("Hinter der ersten"), st("Hinter der zweiten"), st("Und hinter der dritten"), st("Durch welche")
a2, a3, a1, why, out, t_end = st("Hinter Tür zwei"), st("Hinter Tür drei"), st("Aber Tür eins"), st("Denn Tiger"), \
    st("Du kannst also"), st("Hättest")
ev = [("bed", 0.0, 0.35, t5),                               # torch crackle in the cellar (story)
      ("bed", st("Hier kommt"), 0.35, t_end - st("Hier kommt")),
      *[("drip", x, 0.5) for x in (1.3, 6.2, 12.8, 18.4, 35.5, 46.9)],
      ("pop", st("Du befindest") + 0.3, 0.6), ("pop", st("Drei alte") + 0.2, 0.6),
      # door 1: creak + tiger roars
      ("creak", t2 + 0.45, 0.55), ("growl", t2 + 1.0, 0.55), ("growl", t2 + 2.6, 0.45), ("pop", t2 + 0.7, 0.5),
      ("creak", t3 - 0.55, 0.4),
      # door 2: creak + pistol click
      ("creak", t3 + 0.45, 0.55), ("click", t3 + 1.3, 1.0), ("click", t3 + 1.42, 0.8), ("pop", t3 + 0.7, 0.5),
      ("creak", t4 - 0.55, 0.4),
      # door 3: creak + saber swishes
      ("creak", t4 + 0.45, 0.55), ("swish", t4 + 1.2, 0.6), ("swish", t4 + 1.85, 0.6), ("swish", t4 + 3.1, 0.5),
      ("pop", t4 + 0.7, 0.5), ("creak", t5 - 0.65, 0.4),
      ("whoosh", t5 - 0.15, 0.6), ("pop", t5, 0.8), ("pop", t5 + 0.2, 0.6),
      *[("tick", st("PAUSE") + 0.25 + k * 0.5, 0.9) for k in range(3)],
      ("pop", st("Kleiner Tipp"), 0.7), ("pop", st("Schreib deine"), 0.6),
      ("whoosh", st("Hier kommt") - 0.15, 0.6), ("pop", st("Hier kommt"), 0.8),
      ("creak", a2 + 0.45, 0.5), ("click", a2 + 1.0, 0.9), ("buzzer", a2 + 0.9, 0.6), ("creak", a3 - 0.55, 0.35),
      ("creak", a3 + 0.45, 0.5), ("swish", a3 + 1.1, 0.55), ("buzzer", a3 + 0.9, 0.6), ("creak", a1 - 0.65, 0.35),
      ("ding", a1, 0.8), ("creak", why, 0.55), ("pop", why + 0.6, 0.6), ("pop", why + 1.2, 0.7),
      ("tada", out, 0.7), *[("step", out + 0.6 + k * 0.28, 0.8) for k in range(int((t_end - out - 0.9) / 0.28))],
      ("whoosh", t_end - 0.15, 0.6), ("pop", t_end, 0.8), ("pop", st("Schreib's") + 0.4, 0.7),
      ("pop", st("Schreib's") + 2.0, 0.7)]
mix(os.path.join(HERE, "voice.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-15.0)
print("mix.wav", round(mv.END, 2), "s")
