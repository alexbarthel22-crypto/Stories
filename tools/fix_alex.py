"""Prüft, ob der Name „Alex“ deutsch ausgesprochen wird, und erzeugt betroffene Zeilen neu.
Nutzung: python3 tools/fix_alex.py <episode-ordner> [max_runden=4]
Danach tighten.py erneut laufen lassen."""
import os, sys, json, base64, urllib.request, subprocess, time
ep = sys.argv[1]
rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 4
HERE = os.path.dirname(os.path.abspath(__file__))
Q = ("Hör genau auf den Namen 'Alex' in dieser Aufnahme. Wird er DEUTSCH ausgesprochen (kurzes helles a wie in "
     "'Alexander', [ˈalɛks]) oder ENGLISCH ([ˈælɪks], 'Äl-iks')? Antworte nur mit DEUTSCH oder ENGLISCH.")


def judge(f):
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(open(f, "rb").read()).decode()}},
                                    {"text": Q}]}]}
    for a in range(4):
        try:
            req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
                                         data=json.dumps(body).encode(), headers={"Content-Type": "application/json",
                                                                                  "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
            return "ENGLISCH" not in json.load(urllib.request.urlopen(req, timeout=120))["candidates"][0]["content"]["parts"][0]["text"].upper()
        except Exception:
            time.sleep(3 * (a + 1))
    return True


def alex_keys():
    meta = json.load(open(os.path.join(ep, "build", "tts.json")))
    keys = [("intro_pre", os.path.join(ep, "build/tts/intro_pre.wav"))]
    for s in meta["scenes"]:
        for i, l in enumerate(s["lines"]):
            if "Alex" in l["caption"]:
                keys.append((f"{s['id']}_{i}", l["file"]))
    return keys


changed = set()
for r in range(rounds + 1):
    bad = [k for k, f in alex_keys() if not judge(f)]
    print(f"Runde {r}: englisch ->", bad or "keine")
    if not bad or r == rounds:
        break
    for k in bad:
        orig = os.path.join(ep, "build/tts", k + ".orig.wav")
        if os.path.exists(orig):
            os.remove(orig)
    changed.update(bad)
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "tts.py"), ep, "gemini", "Puck"],
                   env={**os.environ, "ONLY": ",".join(bad)}, check=True, stdout=subprocess.DEVNULL)
print("neu erzeugt:", sorted(changed))
