"""Builds mix.wav = voice + channel theme music + sound effects (synced to timing.json)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
from toolkit import anchors

T = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Nils steht", "Einer davon", "Von unten", "Er darf die", "Aber er darf", "Wie findet", "PAUSE",
        "Kleiner Tipp", "Schreib deine", "Hier kommt", "Nils schaltet", "Dann schaltet", "Jetzt schaltet",
        "Leuchtet", "Ist sie aus, aber", "Denn sie", "Und ist sie", "Hättest", "Schreib's"]
S, _ = anchors(T, KEYS)
st = lambda k: S[KEYS.index(k)]
END = T[-1]["end"] + 2.6
t3, t4 = st("Er darf die"), st("Aber er darf")
ev = [("pop", st("Nils steht") + 0.3, 0.6), ("pop", st("Nils steht") + 1.4, 0.5), ("pop", st("Einer davon") + 0.5, 0.6),
      ("pop", st("Von unten") + 0.2, 0.7),
      *[("click", t3 + k / 3, 0.9) for k in range(int((t4 - t3) * 3))],      # playing with the switches
      ("pop", st("Aber er darf") + 0.3, 0.7),
      ("pop", st("Wie findet"), 0.8), ("pop", st("Wie findet") + 0.2, 0.6),
      *[("tick", st("PAUSE") + 0.25 + k * 0.5, 0.9) for k in range(3)],
      ("pop", st("Kleiner Tipp"), 0.7), ("pop", st("Schreib deine"), 0.6), ("pop", st("Hier kommt"), 0.8),
      ("click", st("Nils schaltet") + 0.3, 1.0), *[("tick", st("Nils schaltet") + 0.6 + k * 0.4, 0.6) for k in range(5)],
      ("click", st("Dann schaltet") + 0.3, 1.0), ("click", st("Jetzt schaltet") + 0.3, 1.0),
      ("pop", st("Leuchtet") + 0.4, 0.7), ("pop", st("Ist sie aus, aber") + 0.6, 0.7), ("pop", st("Denn sie"), 0.6),
      ("pop", st("Und ist sie") + 0.5, 0.7), ("ding", st("Und ist sie") + 0.9, 0.6),
      ("pop", st("Hättest"), 0.8), ("pop", st("Schreib's") + 0.4, 0.7), ("pop", st("Schreib's") + 2.0, 0.7)]
mix(os.path.join(HERE, "voice.wav"), END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-15.0)
print("mix.wav", round(END, 2), "s")
