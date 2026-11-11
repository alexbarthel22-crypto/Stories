"""Erzeugt neue Stimmen per ElevenLabs Voice Design (funktioniert auch im Gratis-Konto).
Aufruf: python3 voice_design.py <kürzel> "<Beschreibung>" """
import base64, json, sys, urllib.request, urllib.error

TEXT = ("[sighs] Boah. Na super. Ganz toll. [sarcastic] Ich bin auf 'ner einsamen Insel gestrandet. Nach 'nem Rave. "
        "[annoyed] Mein Handy hat kein Netz, mein Schuh schwimmt im Meer... und die Krabbe guckt mich schon wieder so an. "
        "[sighs] Okay. Ihr entscheidet ab jetzt, was ich mache. Schreibt's in die Kommentare. "
        "[mutters] Aber ich hab jetzt schon keine Lust.")
tag, desc = sys.argv[1], sys.argv[2]
body = {"voice_description": desc, "text": TEXT, "model_id": "eleven_ttv_v3", "guidance_scale": 5}
req = urllib.request.Request("https://api.elevenlabs.io/v1/text-to-voice/design?output_format=mp3_44100_128",
                             json.dumps(body).encode(),
                             {"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
try:
    d = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e:
    print("FEHLER", e.code, e.read().decode()[:500]); sys.exit(1)
ids = {}
for k, p in enumerate(d["previews"], 1):
    fn = f"design_{tag}{k}.mp3"
    open(fn, "wb").write(base64.b64decode(p["audio_base_64"]))
    ids[fn] = p["generated_voice_id"]
    print(fn, p["generated_voice_id"])
json.dump(ids, open(f"design_{tag}_ids.json", "w"), indent=1)
