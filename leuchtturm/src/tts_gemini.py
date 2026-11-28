"""Gemini-TTS: python tts_gemini.py script.txt voice outprefix"""
import json, base64, os, sys, urllib.request, subprocess
text = open(sys.argv[1]).read().strip()
voice = sys.argv[2]
prompt = (sys.argv[4] if len(sys.argv) > 4 else "Sprich auf Deutsch, lebendig, warm und emotional, wie ein junger freundlicher Erzähler, zügig: ") + text
body = {"contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
req = urllib.request.Request(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
r = json.load(urllib.request.urlopen(req, timeout=600))
part = r["candidates"][0]["content"]["parts"][0]["inlineData"]
pcm = base64.b64decode(part["data"])
rate = 24000
if "rate=" in part["mimeType"]:
    rate = int(part["mimeType"].split("rate=")[1].split(";")[0])
raw = sys.argv[3] + ".pcm"
open(raw, "wb").write(pcm)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", raw,
                sys.argv[3] + ".wav"], check=True)
os.remove(raw)
print("dur", len(pcm) / 2 / rate, part["mimeType"])
