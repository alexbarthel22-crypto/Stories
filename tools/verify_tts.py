"""Prüft die TTS-Dateien: Gemini transkribiert jede Zeile, Vergleich mit dem Drehbuch.
Nutzung: python3 tools/verify_tts.py <episode-ordner>"""
import os, sys, json, base64, urllib.request, difflib, re, time
from concurrent.futures import ThreadPoolExecutor
ep = sys.argv[1]
meta = json.load(open(os.path.join(ep, "build", "tts.json")))
items = [("intro_pre", os.path.join(ep, "build/tts/intro_pre.wav"), "Heute ist Alex ...")]
for s in meta["scenes"]:
    for l in s["lines"]:
        items.append((os.path.basename(l["file"])[:-4], l["file"], l["caption"]))

def norm(s):
    s = s.lower().replace("ß", "ss")
    s = re.sub(r"\b30\b", "dreissig", s); s = re.sub(r"\b10\b", "zehn", s)
    return re.sub(r"[^a-zäöü0-9 ]", " ", s).split()

def stt(item):
    key, f, ref = item
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(open(f, "rb").read()).decode()}},
                                    {"text": "Transkribiere diese deutsche Aufnahme exakt wörtlich. Nur der Text."}]}]}
    for a in range(5):
        try:
            req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
                data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
            txt = json.load(urllib.request.urlopen(req, timeout=120))["candidates"][0]["content"]["parts"][0]["text"].strip()
            break
        except Exception as e:
            time.sleep(3 * (a + 1))
    r = difflib.SequenceMatcher(None, norm(ref), norm(txt)).ratio()
    return key, r, txt

bad = 0
with ThreadPoolExecutor(4) as ex:
    for key, r, txt in ex.map(stt, items):
        flag = "OK " if r > 0.85 else "!! "
        bad += r <= 0.85
        print(f"{flag}{r:.2f} {key:10s} {txt}")
print("Abweichungen:", bad)
