"""Builds mix.wav = voice + channel theme music + sound effects (synced to timing.json)."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
st, en, wt = mv.st, mv.en, mv.wt
ts = mv.jump_times()
ev = [
    ("impact", 0.0, 0.8), ("ding", 0.05, 0.5), ("whoosh", 0.02, 0.4),
    ("riser", st("Das Hotel"), 0.4, ), ("whoosh", st("Das Hotel") + 0.1, 0.5),
    *[("pop", wt("Das Hotel", w, 0.0), 0.6) for w in ("eins", "zwei", "drei")], ("sparkle", wt("Das Hotel", "Ende", 0.0) - 0.4, 0.5),
    *[("click", st("Und heute") + 0.2 + k * 0.08, 0.35) for k in range(12)], ("buzzer", st("Und heute") + 0.3, 0.25),
    ("engine", st("Da hält") - 0.2, 0.7, 1.6), ("beep", st("Da hält") + 1.3, 0.6), ("beep", st("Da hält") + 1.5, 0.6),
    *[("step", st("Da hält") + 1.6 + k * 0.28, 0.6) for k in range(int((st("Der Hotelchef") - st("Da hält") - 1.8) / 0.28))],
    ("pop", st("Jeder will") + 0.1, 0.6),
    ("ding", st("Der Hotelchef"), 0.6), ("notify", wt("Der Hotelchef", "Durchsage", 0.0), 0.4),
    ("whoosh", st("Welche") - 0.15, 0.6), ("pop", st("Welche"), 0.7), ("drum", st("Welche") + 0.25, 0.5),
    *[("tick", st("PAUSE") + 0.25 + k * 0.5, 0.9) for k in range(3)],
    ("pop", st("Schreib deine"), 0.6),
    ("riser", st("Hier kommt") - 1.0, 0.4), ("whoosh", st("Hier kommt") - 0.15, 0.6), ("pop", st("Hier kommt"), 0.8),
    ("beep_hi", st("Die Durchsage") - 0.1, 0.3), ("tada", wt("Die Durchsage", "Nummer", 0.5), 0.7),
    *[("swish", ts[n], 0.5) for n in range(1, 11)], *[("pop", ts[n] + 0.85, 0.4) for n in range(1, 6)],
    ("ding", st("Jetzt wohnen") + 0.1, 0.5), ("sparkle", st("Und alle"), 0.6), ("tada", st("Und alle") + 0.2, 0.5),
    *[("step", st("Eins für") + k * 0.26, 0.6) for k in range(int((st("Dieses Rätsel") - st("Eins für")) / 0.26))],
    ("gong", st("Dieses Rätsel"), 0.4), ("pop", st("Dieses Rätsel") + 0.1, 0.6), ("pop", st("Dieses Rätsel") + 0.35, 0.6),
    ("engine", st("Und was") - 0.2, 0.6, 1.4), ("beep", st("Und was") + 1.0, 0.5),
    ("pop", st("Schreib's"), 0.7), ("pop", st("Schreib's") + 0.3, 0.6), ("ding", st("Schreib's") + 1.4, 0.6)]
mix(os.path.join(HERE, "voice.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-16.0)
print("mix.wav", round(mv.END, 2), "s")
