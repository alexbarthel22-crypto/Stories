"""Natural, emotional narration via Gemini TTS. Writes voice.wav + timing.json.

usage: GEMINI_API_KEY=... python3 tts_gemini.py script.txt out_dir [--voice Puck] [--model gemini-3.8-flash-tts]

Script lines: '#' = comment, '[PAUSE x]' = x seconds silence, '{emotion} text' = extra
delivery hint for that line (e.g. {amused}, {surprised}). Each line is generated
separately so scene timings stay exact; a shared style prompt keeps the voice consistent.
"""
import argparse, base64, json, os, re, sys, time, urllib.request, urllib.error
import numpy as np, soundfile as sf

SR = 24000
PROFILE = "Junger, sympathischer männlicher Erzähler (Mitte 20) eines deutschen TikTok-Rätselkanals."
NOTES = ("Natürlich, lebendig und emotional, wie ein echter Mensch, der seinen Followern ein Rätsel erzählt. "
         "Zügiges TikTok-Tempo, spannende Betonung, keine Füllwörter, nichts hinzufügen.")
HINTS = {
    "amused": "mit einem Lächeln in der Stimme, verschmitzt",
    "surprised": "neugierig und überrascht, als echte Frage an die Zuschauer",
    "excited": "begeistert",
    "tense": "spannend, etwas leiser und geheimnisvoll",
}


def synth(text, voice, model, hint=None, retries=7):
    notes = NOTES + (" Dieser Satz: " + HINTS.get(hint, hint) + "." if hint else "")
    prompt = f"# AUDIO PROFILE\n{PROFILE}\n## DIRECTOR'S NOTES\n{notes}\n## TRANSCRIPT\n{text}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(url, json.dumps(body).encode(), {
        "Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    for k in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            if "candidates" not in d:
                raise RuntimeError(f"Gemini blocked line ({d.get('promptFeedback')}) - rephrase it: {text}")
            part = d["candidates"][0]["content"]["parts"][0]["inlineData"]
            pcm = np.frombuffer(base64.b64decode(part["data"]), "<i2").astype(np.float32) / 32768
            time.sleep(float(os.environ.get("TTS_SPACING", "4")))  # stay under per-minute quota
            return pcm
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TimeoutError) as e:
            msg = e.read().decode()[:300] if isinstance(e, urllib.error.HTTPError) else repr(e)
            print(f"  retry {k + 1}: {msg}", file=sys.stderr)
            time.sleep(min(60, 8 * 2 ** k))
    raise RuntimeError("Gemini TTS failed for: " + text)


_ASR = None


def asr_text(a):
    """Transcribe with local Whisper (sherpa-onnx) if WHISPER_DIR is set, else None."""
    global _ASR
    wd = os.environ.get("WHISPER_DIR")
    if not wd:
        return None
    if _ASR is None:
        import sherpa_onnx
        _ASR = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=f"{wd}/small-encoder.int8.onnx", decoder=f"{wd}/small-decoder.int8.onnx",
            tokens=f"{wd}/small-tokens.txt", language="de", task="transcribe", num_threads=4)
    x = np.interp(np.arange(int(len(a) * 16000 / SR)) / 16000, np.arange(len(a)) / SR, a).astype(np.float32)
    s = _ASR.create_stream(); s.accept_waveform(16000, x); _ASR.decode_stream(s)
    return s.result.text


NUM = {"7": "sieben", "9": "neunten", "12": "zwölften", "18": "achtzehn", "3": "drei"}


def norm(s):
    s = s.lower().replace("ß", "ss")
    s = re.sub(r"(\d+)\.?", lambda m: NUM.get(m.group(1), m.group(1)), s)
    return re.findall(r"[a-zäöü]+", s)


def check(text, a):
    """Reject takes with added/missing words (Gemini sometimes improvises) or odd length."""
    words = len(text.split())
    dur = len(a) / SR
    if dur > words / 1.6 + 1.2 or dur < words / 5.5:
        return False, f"duration {dur:.1f}s for {words} words"
    heard = asr_text(a)
    if heard is None:
        return True, ""
    import difflib
    ref, hyp = norm(text), norm(heard)
    r = difflib.SequenceMatcher(None, ref, hyp).ratio()
    extra = len(hyp) - len(ref)
    ok = r >= 0.6 and extra <= 2
    return ok, f"asr '{heard}' ratio {r:.2f}"


def trim(a, thr=0.006):
    nz = np.where(np.abs(a) > thr)[0]
    if not len(nz):
        return a
    return a[max(nz[0] - int(SR * 0.02), 0):nz[-1] + int(SR * 0.08)]


def main(script, out_dir, voice, model, gap=0.08, cache_dir=None):
    cache_dir = cache_dir or os.path.join(out_dir, "cache", "tts")
    os.makedirs(cache_dir, exist_ok=True)
    chunks, timing, t = [], [], 0.0
    lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip() and not l.startswith("#")]
    for i, l in enumerate(lines):
        m = re.match(r"\[PAUSE ([\d.]+)\]", l)
        if m:
            d = float(m.group(1)); chunks.append(np.zeros(int(SR * d), np.float32))
            timing.append({"text": "PAUSE", "start": round(t, 3), "end": round(t + d, 3)}); t += d; continue
        hint = None
        m = re.match(r"\{(\w+)\}\s*(.*)", l)
        if m:
            hint, l = m.group(1), m.group(2)
        key = re.sub(r"\W+", "_", f"{model}_{voice}_{hint}_{l}")[:150]
        cp = os.path.join(cache_dir, key + ".wav")
        if os.path.exists(cp):
            a = sf.read(cp, dtype="float32")[0]
        else:
            print(f"[{i}] {l}")
            best = None
            for attempt in range(6):
                a = trim(synth(l, voice, model, hint))
                ok, why = check(l, a)
                print(f"   take {attempt + 1}: {'OK' if ok else 'REJECT'} {why}")
                if ok:
                    best = a
                    break
                time.sleep(4)
            if best is None:
                raise RuntimeError("no clean take for: " + l)
            a = best
            sf.write(cp, a, SR)
        a = a / (np.abs(a).max() + 1e-9) * 0.9
        g = gap + (0.12 if l[-1] in ".!?" else 0.0)
        timing.append({"text": l, "start": round(t, 3), "end": round(t + len(a) / SR, 3)})
        chunks += [a, np.zeros(int(SR * g), np.float32)]; t += len(a) / SR + g
    v = np.concatenate(chunks)
    sf.write(os.path.join(out_dir, "voice.wav"), v / np.abs(v).max() * 0.9, SR)
    json.dump(timing, open(os.path.join(out_dir, "timing.json"), "w"), ensure_ascii=False, indent=1)
    w = sum(len(x["text"].split()) for x in timing if x["text"] != "PAUSE")
    print(f"duration {t:.1f}s  words {w}  wpm {w / t * 60:.0f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("script"); ap.add_argument("out_dir")
    ap.add_argument("--voice", default="Puck"); ap.add_argument("--model", default="gemini-3.8-flash-tts")
    a = ap.parse_args()
    main(a.script, a.out_dir, a.voice, a.model)
