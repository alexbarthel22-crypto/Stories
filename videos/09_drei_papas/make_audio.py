"""Builds mix.wav = voice + thriller music (Lyria, thriller_haus.mp3) + sound effects (synced to timing.json)."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
st, en, wt = mv.st, mv.en, mv.wt
ev = [
    ("rain", 0.0, 0.45, st("Das Licht")), ("rain", st("Das Licht"), 0.3, mv.END - st("Das Licht")),
    ("rumble", 0.15, 0.7, 2.0), ("tick", 0.6, 0.6), ("tick", 1.6, 0.6), ("tick", 2.6, 0.6), ("pop", wt("Es ist 23", "allein", 0.0), 0.5),
    ("doorbell", st("Es klingelt") + 0.05, 0.8), ("click", wt("Es klingelt", "Bildschirm", 0.0), 0.5),
    ("buzz", st("Im selben") + 0.2, 0.9), ("notify", st("„Sitze"), 0.5),
    ("heartbeat", wt("Du schaust", "blinzelt", 0.0), 0.8), ("heartbeat", wt("Du schaust", "blinzelt", 0.0) + 0.8, 0.8),
    # shower noise only while the bathroom door is on screen
    ("shower", st("Und tatsächlich") + 0.7, 0.9, st("Du schreibst") - st("Und tatsächlich") - 0.7),
    ("shower", st("Plötzlich"), 0.9, wt("Plötzlich", "still", 0.0) - st("Plötzlich") + 0.1),
    *[("click", st("Du schreibst") + 0.4 + k * 0.17, 0.25) for k in range(int((en("Du schreibst") - st("Du schreibst") - 0.8) / 0.17))],
    ("notify", st("Die Antwort") + 0.3, 0.5), ("ding", st("Die Antwort") + 0.9, 0.4),
    ("pop", st("Durch die") + 0.1, 0.5), ("squawk", wt("„Kapitän", "Papagei", 0.0), 0.35), ("ding", st("Das stimmt") + 0.1, 0.4),
    ("ding", st("Das stimmt") + 0.4, 0.4),
    ("rumble", st("Plötzlich") - 0.2, 0.6, 2.0),
    *[("step", wt("Plötzlich", "Schritte", 0.0) + k * 0.55, 0.9) for k in range(int((en("„Wer ist") - wt("Plötzlich", "Schritte", 0.0)) / 0.55))],
    ("lights_out", wt("Das Licht", "aus", 0.2), 0.9), ("beep", wt("Das Licht", "Prozent", 0.0), 0.4),
    ("buzz", st("Eine letzte") + 0.5, 0.8), ("lights_out", en("Eine letzte") + 0.1, 0.5),
    ("knock", st("Draußen klopft") + 0.1, 0.9), ("knock", st("Draußen klopft") + 1.1, 0.8),
    *[("step", wt("Draußen klopft", "Schritte", 0.0) + k * 0.5, 1.0) for k in range(5)],
    *[("heartbeat", st("Da flüstert") + k * 0.75, 0.7) for k in range(int((en("Da flüstert") - st("Da flüstert")) / 0.75))],
    ("impact", st("Drei Papas"), 0.6), ("pop", st("Drei Papas") + 0.15, 0.5), ("pop", st("Drei Papas") + 0.4, 0.5),
    ("pop", st("Drei Papas") + 0.65, 0.5), ("whoosh", st("Wem glaubst") - 0.1, 0.5), ("pop", wt("Wem glaubst", "folg", 0.0), 0.6)]
mix(os.path.join(HERE, "voice.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "thriller_haus.mp3"), music_db=-10.5, duck=0.55)
print("mix.wav", round(mv.END, 2), "s")
