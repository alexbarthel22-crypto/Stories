"""Laura-Varianten: weniger US-Akzent, energischer und genervter."""
import json, urllib.request, urllib.error

LAURA = "FGY2WhTYpPnrIDTdsKH5"
TAGGED = ("[frustrated sigh] BOAH. Na super. Ganz toll! [annoyed] Ich bin auf 'ner einsamen Insel gestrandet. Nach 'nem RAVE! "
          "[angry] Mein Handy hat kein Netz, mein Schuh schwimmt im Meer – und die Krabbe guckt mich SCHON WIEDER so an! "
          "[exasperated] Okay. Ihr entscheidet ab jetzt, was ich mache. Schreibt's in die Kommentare! "
          "[mutters angrily] Aber ich hab jetzt schon keine Lust.")
PLAIN = ("Boah! Na super. Ganz toll! Ich bin auf 'ner einsamen Insel gestrandet. Nach 'nem Rave! "
         "Mein Handy hat kein Netz, mein Schuh schwimmt im Meer – und die Krabbe guckt mich SCHON WIEDER so an! "
         "Okay. Ihr entscheidet ab jetzt, was ich mache. Schreibt's in die Kommentare! "
         "Aber ich hab jetzt schon keine Lust.")
VARIANTS = [
    ("A_v3_kreativ", {"text": TAGGED, "model_id": "eleven_v3", "language_code": "de",
                      "voice_settings": {"stability": 0.0}}),
    ("B_v3_deutsch", {"text": "[native German speaker, no accent] " + TAGGED, "model_id": "eleven_v3",
                      "language_code": "de", "voice_settings": {"stability": 0.5}}),
    ("C_multilingual_v2", {"text": PLAIN, "model_id": "eleven_multilingual_v2",
                           "voice_settings": {"stability": 0.3, "similarity_boost": 0.6, "style": 0.8,
                                              "use_speaker_boost": True}}),
    ("D_turbo_deutsch", {"text": PLAIN, "model_id": "eleven_turbo_v2_5", "language_code": "de",
                         "voice_settings": {"stability": 0.3, "similarity_boost": 0.6, "style": 0.8}}),
]
for name, body in VARIANTS:
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{LAURA}?output_format=mp3_44100_128",
        json.dumps(body).encode(), {"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    try:
        audio = urllib.request.urlopen(req, timeout=180).read()
    except urllib.error.HTTPError as e:
        print(name, "FEHLER", e.code, e.read().decode()[:300]); continue
    open(f"Laura_{name}.mp3", "wb").write(audio); print(name, len(audio))
