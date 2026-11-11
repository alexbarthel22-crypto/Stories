"""Erzeugt Stimmproben (Google Cloud TTS, Chirp 3 HD) – kein Gemini-Kontingent."""
import base64, json, os, urllib.request

TEXT = ("Na super. Ganz toll. Ich bin auf einer einsamen Insel gestrandet. Nach einem Rave! "
        "Mein Handy hat kein Netz, mein Schuh schwimmt im Meer … und die Krabbe guckt mich schon wieder so an. "
        "Okay. Ihr entscheidet ab jetzt, was ich mache. Schreibt's in die Kommentare. "
        "Aber ich hab jetzt schon keine Lust.")
VOICES = ["Achernar", "Aoede", "Autonoe", "Callirrhoe", "Despina", "Erinome", "Gacrux",
          "Kore", "Laomedeia", "Leda", "Pulcherrima", "Sulafat", "Vindemiatrix", "Zephyr"]
URL = "https://texttospeech.googleapis.com/v1/text:synthesize?key=" + os.environ["GOOGLE_TTS_API_KEY"]

for i, v in enumerate(VOICES, 1):
    body = {"input": {"text": TEXT},
            "voice": {"languageCode": "de-DE", "name": f"de-DE-Chirp3-HD-{v}"},
            "audioConfig": {"audioEncoding": "MP3"}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    audio = base64.b64decode(json.load(urllib.request.urlopen(req))["audioContent"])
    fn = f"{i:02d}_{v}.mp3"
    open(fn, "wb").write(audio)
    print(fn, len(audio))
