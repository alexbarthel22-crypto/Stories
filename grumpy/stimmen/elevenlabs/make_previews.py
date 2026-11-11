"""Stimmproben mit ElevenLabs (Modell eleven_v3, mit Audio-Tags für Seufzer/Tonfall).
Der API-Schlüssel wird vom Proxy der Umgebung eingesetzt (Header xi-api-key)."""
import json, sys, urllib.request, urllib.error

TEXT = ("[sighs] Boah. Na super. Ganz toll. [sarcastic] Ich bin auf 'ner einsamen Insel gestrandet. Nach 'nem Rave. "
        "[annoyed] Mein Handy hat kein Netz, mein Schuh schwimmt im Meer... und die Krabbe guckt mich schon wieder so an. "
        "[sighs] Okay. Ihr entscheidet ab jetzt, was ich mache. Schreibt's in die Kommentare. "
        "[mutters] Aber ich hab jetzt schon keine Lust.")
VOICES = [  # Standardstimmen (im Gratis-Konto per API nutzbar)
    ("Laura", "FGY2WhTYpPnrIDTdsKH5"),
    ("Jessica", "cgSgspJ2msm6clMCkdW9"),
    ("Sarah", "EXAVITQu4vr4xnSDxMaL"),
    ("Lily", "pFZP5JQG7iQjIQuC4Bku"),
    ("Matilda", "XrExE9yKIg1WjnnlVkGX"),
    ("Bella", "hpp4J3VqNfWAUOO0d1Us"),
]
only = sys.argv[1:]
for i, (name, vid) in enumerate(VOICES, 1):
    if only and name not in only:
        continue
    body = {"text": TEXT, "model_id": "eleven_v3", "language_code": "de"}
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
        json.dumps(body).encode(),
        {"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    try:
        audio = urllib.request.urlopen(req, timeout=180).read()
    except urllib.error.HTTPError as e:
        print(name, "FEHLER", e.code, e.read().decode()[:400]); continue
    fn = f"{i:02d}_{name}.mp3"
    open(fn, "wb").write(audio)
    print(fn, len(audio))
