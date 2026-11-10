"""Builds mix.wav = voice + channel theme music + sound effects (synced to timing.json)."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
st, en, wt = mv.st, mv.en, mv.wt
tj, th, tg = wt("Die Rechnung", "Jeder", 0.0), wt("Der Kellner", "heimlich", 0.0), wt("Der Kellner", "gibt", 0.0)
ev = [("impact", 0.0, 0.6), ("pop", 0.1, 0.5), ("pop", 0.6, 0.5), ("pop", 1.2, 0.5),
      *[("pop", wt("Lea, Tom", n, 0.0), 0.5) for n in ("Lea", "Tom", "Ben")],
      ("squawk", wt("Lea, Tom", "Unterm", 0.0) + 0.2, 0.0),
      ("chirp", wt("Lea, Tom", "Unterm", 0.0) + 0.3, 0.25), ("pop", wt("Lea, Tom", "Unterm", 0.0), 0.5),
      ("pop", st("Die Rechnung") + 0.1, 0.6), *[("swish", tj + i * 0.25, 0.4) for i in range(3)], ("kaching", tj + 0.8, 0.5),
      ("ding", st("Dann merkt"), 0.5), ("sparkle", wt("Dann merkt", "Aktionstag", 0.0), 0.5),
      *[("clink", st("Er gibt") + 0.4 + k * 0.12, 0.45) for k in range(5)],
      ("whoosh", th - 0.1, 0.4), ("clink", th + 0.5, 0.5), *[("clink", tg + 0.3 + i * 0.25, 0.5) for i in range(3)],
      ("pop", st("Also hat"), 0.5), *[("click", wt("Also hat", w, 0.0) - 0.6 + k * 0.07, 0.25) for w in ("neunzehn", "siebenundfünfzig", "neunundfünfzig") for k in range(6)],
      ("buzzer", wt("Also hat", "neunundfünfzig", 0.0) + 0.5, 0.3),
      ("whoosh", st("Wo ist") - 0.1, 0.5), ("pop", st("Wo ist"), 0.6), ("drum", st("Wo ist") + 0.25, 0.5),
      *[("tick", st("PAUSE") + 0.2 + k * 0.45, 0.9) for k in range(3)], ("pop", st("Schreib's"), 0.6),
      ("riser", st("Hier kommt") - 0.9, 0.35), ("pop", st("Hier kommt"), 0.6), ("ding", st("In den") + 0.2, 0.5),
      ("tada", wt("Dazu die", "sechzig", 0.0), 0.7), ("pop", st("Folg mir"), 0.6), ("ding", st("Folg mir") + 1.0, 0.5)]
ev = [e for e in ev if e[2] > 0]
mix(os.path.join(HERE, "voice.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-13.5)
print("mix.wav", round(mv.END, 2), "s")
