"""Folge 1 – Tonspur mit ElevenLabs-Stimme „Laura“ (Variante A oder D) inkl. exakter Wortzeiten.
Aufruf: python3 audio_elevenlabs.py A|D
Erzeugt voice.wav, timeline.json (Zeilen + Wortzeiten) und envelope.json (Mundbewegung).
Die API-Antwort wird in _cache_<Variante>.json gespeichert, damit Neu-Rendern kein Kontingent kostet.
Der API-Schlüssel wird vom Proxy der Umgebung eingesetzt."""
import base64, json, subprocess, sys, urllib.request, wave
from pathlib import Path
import numpy as np

LAURA = "FGY2WhTYpPnrIDTdsKH5"
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "A"
HERE = Path(__file__).parent

# (Regieanweisung für v3, gesprochener Text, Untertitel)
LINES = [
    ("[shouting angrily]", "WAS GLOTZT DU SO?!", "WAS GLOTZT DU SO?!"),
    ("[annoyed]", "Bro, gestern war ich auf einem Rave", "Bro, gestern war ich auf einem Rave …"),
    ("", "und bin heute hier aufgewacht.", "… und bin heute HIER aufgewacht."),
    ("[frustrated]", "Wer will mich hier hopps nehmen?!", "Wer will mich hier hopps nehmen?!"),
    ("[angry]", "Was soll der Mist?", "Was soll der Mist?!"),
    ("", "Hier ist ja gar nichts!", "Hier ist ja GAR NICHTS!"),
    ("[sarcastic]", "Und das Beste:", "Und das Beste:"),
    ("", "Ausnahmslos alles, was ihr in die Kommentare schreibt,", "Ausnahmslos ALLES, was ihr in die Kommentare schreibt …"),
    ("", "wird mit mir und der Insel gemacht.", "… wird mit mir und der Insel gemacht."),
    ("[annoyed]", "Das kann ja nur scheiße werden.", "Das kann ja nur sch🥚sse werden."),
    ("[deadpan]", "Wow.", "Wow."),
    ("[sighs]", "Ja, dann kommentiert mal.", "Ja, dann kommentiert mal."),
    ("", "Mir egal, was ihr macht.", "Mir egal, was ihr macht."),
    ("[dismissive]", "Juckt mich nicht.", "Juckt mich nicht."),
]
SETTINGS = {
    "A": {"model_id": "eleven_v3", "language_code": "de", "voice_settings": {"stability": 0.0}, "tags": True},
    "D": {"model_id": "eleven_turbo_v2_5", "language_code": "de",
          "voice_settings": {"stability": 0.3, "similarity_boost": 0.6, "style": 0.8}, "tags": False},
}[VARIANT]

# Volltext zusammensetzen und Zeichenpositionen jeder Zeile merken
full, spans = "", []
for tag, spoken, _ in LINES:
    if full:
        full += " "
    if SETTINGS["tags"] and tag:
        full += tag + " "
    spans.append((len(full), len(full) + len(spoken)))
    full += spoken

cache = HERE / f"_cache_{VARIANT}.json"
if cache.exists() and json.loads(cache.read_text()).get("text") == full:
    resp = json.loads(cache.read_text())
else:
    body = {k: v for k, v in SETTINGS.items() if k != "tags"}
    body["text"] = full
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{LAURA}/with-timestamps",
                                 json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    resp = json.load(urllib.request.urlopen(req, timeout=300))
    resp["text"] = full
    cache.write_text(json.dumps(resp))

al = resp["alignment"]
chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
assert "".join(chars) == full, "Alignment passt nicht zum Text"

LEAD = 0.25  # Stille am Anfang
mp3 = HERE / f"_voice_{VARIANT}.mp3"
mp3.write_bytes(base64.b64decode(resp["audio_base64"]))
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-af", f"adelay={int(LEAD*1000)},aresample=16000",
                "-ac", "1", str(HERE / "voice.wav")], check=True)
mp3.unlink()

timeline = []
for (a, b), (_, spoken, sub) in zip(spans, LINES):
    words, i = [], a
    while i < b:
        if full[i] == " ":
            i += 1; continue
        j = i
        while j < b and full[j] != " ":
            j += 1
        words.append({"w": full[i:j], "start": round(st[i] + LEAD, 3), "end": round(en[j - 1] + LEAD, 3)})
        i = j
    timeline.append({"text": sub, "start": words[0]["start"], "end": words[-1]["end"], "words": words})

with wave.open(str(HERE / "voice.wav")) as w:
    sr = w.getframerate()
    audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
FPS = 25
hop = sr // FPS
env = [float(np.sqrt(np.mean(audio[k:k + hop] ** 2))) for k in range(0, len(audio), hop)]
m = max(env)
json.dump([round(min(e / m * 1.6, 1.0), 3) for e in env], open(HERE / "envelope.json", "w"))
dur = round(len(audio) / sr + 0.2, 3)
json.dump({"duration": dur, "lines": timeline}, open(HERE / "timeline.json", "w"), indent=1, ensure_ascii=False)
print(f"Laura {VARIANT}: {dur} s")
