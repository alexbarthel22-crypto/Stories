"""Builds mix.wav = voice + channel theme music + sound effects (synced to timing.json)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
from toolkit import anchors

T = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Niklas steht", "Er muss alle", "Das Problem", "Und es gibt", "Bleiben Wolf", "Bleiben Ziege", "Wie bringt",
        "PAUSE", "Kleiner Tipp", "Schreib deine", "Hier kommt", "Zuerst bringt", "Dann fährt er allein",
        "Jetzt holt", "Aber Achtung", "Also nimmt", "Er setzt", "Wolf und Kohl warten", "Dann fährt er wieder",
        "Zum Schluss", "Und alle drei", "Hättest", "Schreib's"]
S, _ = anchors(T, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
st = lambda k: S[K[k]]
END = T[-1]["end"] + 2.6
t0, t1 = st("Niklas steht"), st("Er muss alle")
ev = [*[("pop", t0 + 0.3 + k * (t1 - t0 - 0.6) / 4, 0.6) for k in range(4)],   # name tags
      ("pop", t1 + 0.7, 0.6), ("pop", st("Das Problem") + 0.5, 0.6), ("pop", st("Und es gibt"), 0.7),
      ("pop", st("Bleiben Wolf") + 0.1, 0.7), ("pop", st("Bleiben Ziege") + 0.1, 0.7),
      ("pop", st("Wie bringt"), 0.8), ("pop", st("Wie bringt") + 0.2, 0.6),
      *[("tick", st("PAUSE") + 0.25 + k * 0.5, 0.9) for k in range(3)],
      ("pop", st("Kleiner Tipp"), 0.7), ("pop", st("Schreib deine"), 0.6), ("pop", st("Hier kommt"), 0.8),
      *[("pop", st(k) + 0.1, 0.45) for k in ("Zuerst bringt", "Dann fährt er allein", "Jetzt holt", "Also nimmt",
                                            "Er setzt", "Dann fährt er wieder", "Zum Schluss")],
      ("pop", st("Aber Achtung"), 0.8), ("pop", st("Wolf und Kohl warten"), 0.7),
      ("ding", st("Und alle drei"), 0.8),
      ("pop", st("Hättest"), 0.8), ("pop", st("Schreib's") + 0.4, 0.7), ("pop", st("Schreib's") + 2.0, 0.7)]
# channel theme music (Google Lyria), same track in every video
mix(os.path.join(HERE, "voice.wav"), END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-15.0)
print("mix.wav", round(END, 2), "s")
