"""Erzeugt die Sprecherspur (eine WAV pro Zeile).

Nutzung:
  python3 tools/tts.py <episode-ordner> gemini [voice]        # Google Gemini (GEMINI_API_KEY)
  python3 tools/tts.py <episode-ordner> <voice.onnx> [scale]  # lokale Piper-Stimme
Schreibt <episode>/build/tts/*.wav und <episode>/build/tts.json
"""
import sys, os, json, wave, io, time, base64, importlib.util, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
import numpy as np

ep_dir, backend = sys.argv[1], sys.argv[2]
arg3 = sys.argv[3] if len(sys.argv) > 3 else None

spec = importlib.util.spec_from_file_location("script", os.path.join(ep_dir, "script.py"))
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)
out = os.path.join(ep_dir, "build", "tts")
os.makedirs(out, exist_ok=True)
GEMINI = backend == "gemini"
MOODS = getattr(script, "MOODS", {})

GEMINI_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
VOICE = arg3 or "Puck"
PROFILE = """# AUDIO PROFILE: Der Erzähler
Ein junger deutscher TikTok-Storyteller, Mitte zwanzig, charmant, witzig und sehr ausdrucksstark.

### DIRECTOR'S NOTES
Stil: emotional und lebendig, echte Betonung, kleine Kunstpausen vor Pointen. Zitate von Alex mit verstellter, übertrieben gefühlvoller Stimme. Tempo: zügig wie auf TikTok.
Stimmung in diesem Satz: {mood}
Sprache: Deutsch, englische Begriffe englisch aussprechen.
Wichtig: Sprich ausschließlich den Text unter TRANSCRIPT, wortwörtlich, nichts hinzufügen oder weglassen.

#### TRANSCRIPT
{text}"""


def trim_save(a, sr, path):
    thr = int(np.abs(a).max() * 0.02) + 50
    nz = np.where(np.abs(a) > thr)[0]
    if len(nz):
        a = a[max(0, nz[0] - int(0.01 * sr)): nz[-1] + int(0.05 * sr)]
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(a.astype(np.int16).tobytes())
    return len(a) / sr


def gemini_tts(text, mood, path):
    body = {"contents": [{"parts": [{"text": PROFILE.format(mood=mood, text=text)}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    for attempt in range(6):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
            "Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            raw = base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            break
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TimeoutError) as e:
            print("  retry", attempt, text[:30], e)
            time.sleep(2 ** attempt * 2)
    else:
        raise RuntimeError("Gemini TTS fehlgeschlagen: " + text)
    if raw[:4] == b"RIFF":
        with wave.open(io.BytesIO(raw)) as w:
            sr = w.getframerate()
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    else:
        sr, a = 24000, np.frombuffer(raw, dtype=np.int16)
    return trim_save(a, sr, path)


if not GEMINI:
    from piper import PiperVoice, SynthesisConfig
    pv = PiperVoice.load(backend)
    LS = float(arg3) if arg3 else 0.9


def piper_tts(text, ls, path):
    with wave.open(path, "wb") as w:
        pv.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=ls, noise_scale=0.6, noise_w_scale=0.7))
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return trim_save(a, sr, path)


jobs = [("intro_pre", "Heute ist Alex ...", "Heute ist Alex ...", MOODS.get("intro_pre", "spannend")),
        ("intro_role", getattr(script, "ROLE_SAY", script.ROLE_TTS), script.ROLE_TTS, MOODS.get("intro_role", "laut"))]
for s in script.SCENES:
    for i, (cap, say) in enumerate(s["lines"]):
        jobs.append((f"{s['id']}_{i}", cap, say or cap, MOODS.get(s["id"], "lebendig")))


def run(job):
    key, gem_text, piper_text, mood = job
    p = f"{out}/{key}.wav"
    if GEMINI:
        return key, p, gemini_tts(gem_text, mood, p)
    return key, p, piper_tts(piper_text, LS, p)


# ONLY=key1,key2 -> nur diese Zeilen neu erzeugen, Rest aus vorhandener tts.json übernehmen
only = [k for k in os.environ.get("ONLY", "").split(",") if k]
res = {}
if only:
    old = json.load(open(os.path.join(ep_dir, "build", "tts.json")))
    res["intro_pre"] = (f"{out}/intro_pre.wav", old["intro"]["pre"])
    res["intro_role"] = (f"{out}/intro_role.wav", old["intro"]["role"])
    for s in old["scenes"]:
        for i, l in enumerate(s["lines"]):
            res[f"{s['id']}_{i}"] = (l["file"], l["dur"])
    jobs = [j for j in jobs if j[0] in only]
with ThreadPoolExecutor(6 if GEMINI else 1) as ex:
    res.update({k: (p, d) for k, p, d in ex.map(run, jobs)})

meta = {"backend": "gemini:" + VOICE if GEMINI else "piper",
        "intro": {"pre": res["intro_pre"][1], "role": res["intro_role"][1]}, "scenes": []}
for s in script.SCENES:
    meta["scenes"].append({"id": s["id"], "lines": [
        {"file": res[f"{s['id']}_{i}"][0], "dur": res[f"{s['id']}_{i}"][1], "caption": cap}
        for i, (cap, _) in enumerate(s["lines"])]})
json.dump(meta, open(os.path.join(ep_dir, "build", "tts.json"), "w"), indent=1, ensure_ascii=False)
tot = sum(l["dur"] for s in meta["scenes"] for l in s["lines"])
print("Sprechzeit Szenen: %.1fs  Intro: %.1f+%.1f" % (tot, meta["intro"]["pre"], meta["intro"]["role"]))
