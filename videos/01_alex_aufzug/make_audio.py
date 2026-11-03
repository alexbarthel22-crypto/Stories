"""Builds mix.wav = voice + background music + sound effects (synced to timing.json)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix

from toolkit import anchors
T = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Das hier ist Alex", "Alex wohnt", "Jeden Morgen", "Bis hierhin", "Aber jeden Abend",
        "Alex steigt in den Aufzug", "Dort steigt", "Seine Nachbarn", "Denn Alex", "Eines Tages",
        "Alex kommt nach Hause", "Am nächsten Tag", "Und Alex steigt", "Warum macht", "PAUSE", "Kleiner Tipp",
        "Schreib deine", "Hier kommt", "Alex ist klein", "Nach unten", "Aber nach oben", "Und bei Regen",
        "Da hat Alex", "Mit der Spitze", "Hättest", "Schreib's"]
S, _ = anchors(T, KEYS)
END = T[-1]["end"] + 2.6
ev = [
    ("pop", 0.2, 0.7),                                  # name tag
    ("ding", S[2] + 3.6, 0.8),                          # morning: arrives at E
    ("pop", S[3] - 0.1, 0.7),                           # ganz normal
    ("ding", S[5] + 2.4, 0.8),                          # evening: arrives at 9
    ("rain", S[9] - 0.2, 0.25, S[11] - S[9] + 0.2),      # rain scene
    ("ding", S[10] + 3.4, 0.8),                         # rain: arrives at 12
    ("ding", S[12] + 1.2, 0.8),                         # sunny: 9 again
    ("pop", S[13], 0.8), ("pop", S[13] + 0.2, 0.6),     # WARUM?
    *[("tick", S[14] + 0.25 + k * 0.5, 0.9) for k in range(3)],   # thinking pause
    ("pop", S[15], 0.7), ("pop", S[16], 0.6),
    ("pop", S[17], 0.8),
    ("pop", S[19] + 2.4, 0.6), ("pop", S[20] + 1.6, 0.6),
    ("pop", S[22], 0.7), ("ding", S[23] + 1.2, 0.8),
    ("pop", S[24], 0.8), ("pop", S[25] + 0.4, 0.7), ("pop", S[25] + 2.0, 0.7),
]
# Background music: instrumental track generated with Google Lyria (lyria-3.5), see music.txt
mix(os.path.join(HERE, "voice.wav"), END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "music.mp3"), music_db=-15.0)
print("mix.wav", round(END, 2), "s")
