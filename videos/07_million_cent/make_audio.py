"""Builds mix.wav = voice + channel theme music + sound effects (synced to timing.json)."""
import os, sys, importlib.util
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from audio import mix
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
st, en, wt = mv.st, mv.en, mv.wt

ev = [
    # hook: impact + both options
    ("impact", 0.0, 0.9), ("whoosh", 0.02, 0.5), ("kaching", wt("Eine Million", "Million") - 0.05, 0.5),
    ("pop", wt("Eine Million", "Cent") - 0.05, 0.6), ("tick", wt("Eine Million", "Sekunde"), 0.8),
    ("drum", wt("Eine Million", "Cent") + 0.1, 0.5),
    # rooftop: Leon & Mia
    ("whoosh", st("Leon muss") - 0.1, 0.5), ("pop", st("Leon muss") + 0.1, 0.6),
    ("kaching", st("Die Million"), 0.6), ("cheer", st("Die Million"), 0.25),
    ("pop", st("Ein Cent?"), 0.6), ("clink", st("Ein Cent?") + 0.3, 0.7), ("pop", st("Ein Cent?") + 0.7, 0.5),
    ("whoosh", st("Aber Mia"), 0.4), ("pop", st("Aber Mia") + 0.1, 0.6), ("sparkle", st("Aber Mia") + 0.5, 0.45),
    ("pop", st("Ich nehme"), 0.6), ("tick", st("Ich nehme") + 0.4, 0.7),
    ("pop", st("Viel Glück") + 0.2, 0.6), ("pop", wt("Viel Glück", "Eis", 0.0), 0.6),
    ("pop", st("Wetten") + 0.1, 0.6), ("clink", en("Wetten") - 0.6, 0.6), ("tada", en("Wetten") - 0.6, 0.6),
    # race start lights
    *[("beep", st("Und das Rennen") + k * (en("Und das Rennen") - st("Und das Rennen")) * 0.8 / 3, 0.9) for k in range(2)],
    ("beep_hi", st("Und das Rennen") + (en("Und das Rennen") - st("Und das Rennen")) * 0.8, 0.9),
    ("engine", st("Und das Rennen") + 0.2, 0.5, 1.4),
    # first seconds
    ("tick", st("Erste Sekunde"), 0.9), ("clink", st("Erste Sekunde") + 0.7, 0.8),
    ("tick", wt("Erste Sekunde", "Zweite", 0.0), 0.9), ("clink", wt("Erste Sekunde", "Zweite", 0.0) + 0.6, 0.8),
    # Leon laughs, celebrates
    *[("pop", st("Leon lacht") + 0.1 + k * 0.25, 0.4) for k in range(4)],
    ("sparkle", st("Und weil er") + 0.3, 0.5), ("whoosh", st("Und weil er") + 0.8, 0.4),
    # spending spree
    ("engine", st("Einen Sportwagen") - 0.2, 0.9, 1.6), ("kaching", en("Einen Sportwagen") - 0.5, 0.6),
    ("sparkle", st("Eine Diamant"), 0.6), ("shing", st("Eine Diamant") + 0.3, 0.4), ("kaching", en("Eine Diamant") - 0.5, 0.6),
    ("splash", st("Und eine Pool"), 0.7), ("cheer", st("Und eine Pool") + 0.2, 0.45), ("kaching", en("Und eine Pool") - 0.5, 0.6),
    *[("notify", wt("Und eine Pool", "ganze", 0.0) + k * 0.25, 0.5) for k in range(3)],
    ("cheer", st("Ich bin Millionär"), 0.6), ("tada", st("Ich bin Millionär"), 0.5),
    # Mia's counter, day and night
    ("whoosh", st("Während Leon") - 0.1, 0.5),
    *[("clink", st("Während Leon") + 0.3 + k * 0.42, 0.45) for k in range(int((en("Während Leon") - st("Während Leon")) / 0.42))],
    ("owl", wt("Während Leon", "Nacht", 0.0), 0.3), ("chirp", wt("Während Leon", "Tag", 0.0), 0.3),
    # six months later
    *[("swish", st("Sechs Monate") + k * 0.17, 0.35) for k in range(6)], ("engine", st("Sechs Monate") + 1.0, 0.6, 1.4),
    ("pop", st("Na, Mia"), 0.6), ("kaching", st("Na, Mia") + 0.2, 0.4), ("pop", wt("Na, Mia", "Gibst"), 0.5),
    ("pop", st("Am Ende") + 0.1, 0.6), ("pop", st("Am Ende") + 0.6, 0.6),
    # yacht
    ("notify", st("Trotzdem bucht") + 0.1, 0.6), ("click", st("Trotzdem bucht") + 1.0, 0.7), ("splash", st("Trotzdem bucht") + 0.7, 0.6),
    ("kaching", en("Trotzdem bucht") - 0.5, 0.6),
    # both sure, tight race
    ("whoosh", st("Denn beide"), 0.5), ("pop", st("Denn beide") + 0.4, 0.6), ("pop", st("Denn beide") + 0.7, 0.6),
    *[("heartbeat", st("Es wird knapp") + k * 0.62, 0.9) for k in range(int((en("Es wird knapp") - st("Es wird knapp")) / 0.62) + 1)],
    ("drum", wt("Es wird knapp", "Sehr"), 0.7),
    # new year's eve
    ("file", st("Dann kommt") - 0.05, 0.35, os.path.join(HERE, "..", "..", "assets", "sfx", "fireworks.mp3"),
     en("Dann kommt") - st("Dann kommt") + 0.4), ("pop", st("Dann kommt") + 0.1, 0.6),
    # reveal
    ("notify", st("Leon öffnet") + 0.3, 0.6), ("kaching", wt("Leon öffnet", "vierhundert", 0.0), 0.6),
    *[("ding", st("Trotz Sportwagen") + k * 0.35, 0.35) for k in range(4)],
    ("pop", st("Und du") + 0.1, 0.6), ("pop", wt("Und du", "Setz", 0.0), 0.6),
    # formula
    *[("tick", wt("Ein Cent pro", w, 0.0), 0.8) for w in ("Cent", "Sekunde", "ganzes", "Jahr")],
    ("riser", en("Ein Cent pro") - 1.0, 0.4), ("drum", en("Ein Cent pro") - 0.2, 0.6),
    # Leon counting
    *[("click", st("Leon fängt") + 0.3 + k * 0.45, 0.5) for k in range(int((en("Leon fängt") - st("Leon fängt")) / 0.45))],
    # final question + outro
    ("whoosh", st("Wie viel") - 0.1, 0.6), ("pop", st("Wie viel"), 0.7), ("drum", wt("Wie viel", "wer", 0.0), 0.6),
    ("pop", wt("Wie viel", "wer", 0.0), 0.6), ("pop", st("Schreib's"), 0.7), ("pop", st("Schreib's") + 0.3, 0.6),
    ("ding", st("Schreib's") + 1.3, 0.6)]

# shouted opener: first sentence a bit louder than the rest
v, sr = sf.read(os.path.join(HERE, "voice.wav"), dtype="float32")
g = np.full(len(v), 0.7, np.float32)
e0 = int(en("Eine Million") * sr)
g[:e0] = 1.0
g[e0:e0 + int(0.1 * sr)] = np.linspace(1.0, 0.7, len(g[e0:e0 + int(0.1 * sr)]))
v = np.tanh(v * g * 1.4) / np.tanh(1.4)
sf.write(os.path.join(HERE, "cache", "voice_boost.wav"), v, sr)
mix(os.path.join(HERE, "cache", "voice_boost.wav"), mv.END, ev, os.path.join(HERE, "mix.wav"),
    music_path=os.path.join(HERE, "..", "..", "assets", "music", "raetsel_theme.mp3"), music_db=-16.0)
print("mix.wav", round(mv.END, 2), "s")
