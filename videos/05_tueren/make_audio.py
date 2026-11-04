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
ev = [("bed", 0.0, 0.3, t5),                                # quiet torch crackle in the cellar
      ("bed", st("Hier kommt"), 0.3, t_end - st("Hier kommt")),
      *[("drip", x, 0.45) for x in (3.1, 12.8, 18.4, 35.5, 46.9)],
      ("pop", st("Drei alte") + 0.2, 0.6),
      # door 1: tigers roar
      ("growl", t2 + 0.8, 0.5), ("growl", t2 + 2.6, 0.42), ("pop", t2 + 0.7, 0.5),
      # door 2: chainsaw running
      ("chainsaw", t3 + 0.5, 0.42, t4 - t3 - 0.7), ("pop", t3 + 0.7, 0.5),
      # door 3: saber swishes + blade ring + parrot
      ("swish", t4 + 1.0, 0.6), ("shing", t4 + 1.15, 0.5), ("swish", t4 + 2.2, 0.55), ("shing", t4 + 2.35, 0.45),
      ("squawk", t4 + 1.7, 0.35), ("pop", t4 + 0.7, 0.5),
      ("whoosh", t5 - 0.15, 0.6), ("pop", t5, 0.8), ("pop", t5 + 0.2, 0.6),
      *[("tick", st("PAUSE") + 0.25 + k * 0.5, 0.9) for k in range(3)],
      ("pop", st("Kleiner Tipp"), 0.7), ("pop", st("Schreib deine"), 0.6),
      ("whoosh", st("Hier kommt") - 0.15, 0.6), ("pop", st("Hier kommt"), 0.8),
      ("chainsaw", a2 + 0.5, 0.35, 1.6), ("wrong", a2 + 0.9, 0.6),
      ("swish", a3 + 0.9, 0.5), ("shing", a3 + 1.05, 0.4), ("wrong", a3 + 0.9, 0.6),
      ("ding", a1, 0.8), ("pop", why + 0.6, 0.6), ("pop", why + 1.2, 0.7),
      ("tada", out, 0.7), *[("step", out + 0.6 + k * 0.28, 0.8) for k in range(int((t_end - out - 0.9) / 0.28))],
      ("whoosh", t_end - 0.15, 0.6), ("pop", t_end, 0.8), ("pop", st("Schreib's") + 0.4, 0.7),
      ("pop", st("Schreib's") + 2.0, 0.7)]
mix(os.path.join(HERE, "voice.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "grusel_keller.mp3"), music_db=-16.0)   # spooky track for this video
print("mix.wav", round(mv.END, 2), "s")
