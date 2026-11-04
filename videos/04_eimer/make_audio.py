"""Builds mix.wav = voice + channel theme music + sound effects (synced to timing.json)."""
import json, os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
st = mv.st
ev = [("pop", st("Dario will") + 0.2, 0.6), ("pop", st("Dario will") + 1.0, 0.6), ("pop", st("Das Getränk"), 0.6),
      ("pop", st("Zum Abmessen") + 0.6, 0.6), ("pop", st("Und die Eimer") + 0.2, 0.7),
      ("pop", st("Wie bekommt"), 0.8), ("pop", st("Wie bekommt") + 0.2, 0.6),
      *[("tick", st("PAUSE") + 0.25 + k * 0.5, 0.9) for k in range(3)],
      ("pop", st("Kleiner Tipp"), 0.7), ("pop", st("Schreib deine"), 0.6), ("pop", st("Hier kommt"), 0.8),
      ("pop", st("Da nur noch") + 0.3, 0.7), ("ding", st("Eins plus drei"), 0.8),
      ("pop", st("Hättest"), 0.8), ("pop", st("Schreib's") + 0.4, 0.7), ("pop", st("Schreib's") + 2.0, 0.7)]
for (t0, t1, kind, src, dst, amt) in mv.ACTIONS:
    if kind == "fill":
        a, b = t0 + (t1 - t0) * 0.25, t0 + (t1 - t0) * 0.78
        ev += [("click", a - 0.05, 1.0), ("click", b, 0.9)]          # tap lever open / close
    else:
        a, b = t0 + (t1 - t0) * 0.34, t0 + (t1 - t0) * 0.76
        ev.append(("whoosh", t0, 0.35))                               # bucket lifted
    ev += [("rain", a, 0.35, b - a), ("glug", a + 0.05, 0.8), ("clink", t1 - 0.05, 0.8)]
# transitions + finale
ev += [("whoosh", st("Wie bekommt") - 0.15, 0.6), ("whoosh", st("Hier kommt") - 0.15, 0.6),
       ("whoosh", st("Hättest") - 0.15, 0.6), ("tada", st("Eins plus drei") + 0.1, 0.9)]
ev = [e for e in ev if not (e[0] == "ding" and abs(e[1] - st("Eins plus drei")) < 0.01)]
# opening fireworks: clearly quieter than the voice (sfx are mixed at 0.6x on top of these gains)
for (t0, fx, fy, col) in mv.INTRO_FIREWORKS:
    ev += [("fw_launch", t0, 0.11), ("fw_boom", t0 + mv.FW_LAUNCH, 0.21), ("fw_crackle", t0 + mv.FW_LAUNCH + 0.12, 0.15)]
mix(os.path.join(HERE, "voice.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-15.0)
print("mix.wav", round(mv.END, 2), "s")
