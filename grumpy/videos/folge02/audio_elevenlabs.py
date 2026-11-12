"""Tag 2 – Tonspur mit Laura (ElevenLabs v3, eine Aufnahme für alles -> gleiche Stimme) + exakte Wortzeiten.
Ablauf: Volltext synthetisieren -> Stille am Anfang weg -> Pausen kürzen -> leicht schneller ->
vor jedem Kommentar Platz für dessen Animation einfügen. Ergebnis: voice.wav, timeline.json, envelope.json.
Die API-Antwort wird gecacht (_cache.json), Neu-Rendern kostet kein Kontingent."""
import base64, json, subprocess, urllib.request, wave
from pathlib import Path
import numpy as np
from script import SEGMENTS, SFX

HERE = Path(__file__).parent
LAURA = "FGY2WhTYpPnrIDTdsKH5"
TEMPO = 1.15          # etwas zügiger, damit das Video bei ~70 s bleibt
MAX_GAP = 0.36        # Pause zwischen zwei Sätzen
SR = 16000

def build_text(segments, offset_seg=0):
    text, spans = "", []
    for si, seg in enumerate(segments):
        for li, (tag, spoken, _) in enumerate(seg["lines"]):
            if text:
                text += " "
            if tag:
                text += tag + " "
            spans.append((len(text), len(text) + len(spoken), si + offset_seg, li))
            text += spoken
    return text, spans


def tts(text):
    """ElevenLabs v3 (Streaming mit Zeitstempeln). Ergebnis wird pro Text gecacht."""
    import hashlib
    cache = HERE / f"_cache_{hashlib.md5(text.encode()).hexdigest()[:10]}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    old = HERE / "_cache.json"      # erste Aufnahme (ganzes Skript) wiederverwenden, wenn der Text darin vorkommt
    if old.exists() and json.loads(old.read_text())["text"].startswith(text):
        return json.loads(old.read_text())
    body = {"text": text, "model_id": "eleven_v3", "language_code": "de", "voice_settings": {"stability": 0.0}}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{LAURA}/stream/with-timestamps",
                                 json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    audio_b, chars, starts, ends = b"", [], [], []
    with urllib.request.urlopen(req, timeout=600) as r:
        for raw_line in r:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            d = json.loads(raw_line)
            if d.get("audio_base64"):
                audio_b += base64.b64decode(d["audio_base64"])
            a = d.get("alignment") or {}
            if a.get("characters"):
                chars += a["characters"]; starts += a["character_start_times_seconds"]; ends += a["character_end_times_seconds"]
    resp = {"text": text, "audio_base64": base64.b64encode(audio_b).decode(),
            "alignment": {"characters": chars, "character_start_times_seconds": starts, "character_end_times_seconds": ends}}
    cache.write_text(json.dumps(resp))
    return resp


def decode(resp):
    mp3 = HERE / "_raw.mp3"; raw = HERE / "_raw.wav"
    mp3.write_bytes(base64.b64decode(resp["audio_base64"]))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(SR), str(raw)], check=True)
    with wave.open(str(raw)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    mp3.unlink(); raw.unlink()
    return x


# Pro Szene: unveränderte Sätze aus vorhandenen Aufnahmen herausschneiden, geänderte Szenen einzeln neu vertonen
def recordings():
    for f in sorted(HERE.glob("_cache*.json")):
        d = json.loads(f.read_text())
        yield d


RECS = list(recordings())
_decoded = {}


def piece_for(si):
    """Audio + Zeichenzeiten für Szene si. Sucht den Text in vorhandenen Aufnahmen, sonst neue Aufnahme."""
    text, sp = build_text([SEGMENTS[si]], offset_seg=si)
    first_char = sp[0][0]
    for d in RECS:
        k = d["text"].find(text)
        if k < 0:
            continue
        al = d["alignment"]
        t0 = al["character_start_times_seconds"][k + first_char] - 0.05
        t1 = al["character_end_times_seconds"][k + len(text) - 1] + 0.15
        key = id(d)
        if key not in _decoded:
            _decoded[key] = decode(d)
        x = _decoded[key][max(int(t0 * SR), 0): int(t1 * SR)]
        st_ = [v - t0 for v in al["character_start_times_seconds"][k:k + len(text)]]
        en_ = [v - t0 for v in al["character_end_times_seconds"][k:k + len(text)]]
        return text, sp, x, st_, en_
    d = tts(text)
    x = decode(d)
    al = d["alignment"]
    t0 = max(al["character_start_times_seconds"][first_char] - 0.05, 0)
    t1 = al["character_end_times_seconds"][-1] + 0.15
    return (text, sp, x[int(t0 * SR): int(t1 * SR)],
            [v - t0 for v in al["character_start_times_seconds"]], [v - t0 for v in al["character_end_times_seconds"]])


full, spans, st, en, parts, pos = "", [], [], [], [], 0.0
for si in range(len(SEGMENTS)):
    text, sp, x, st_, en_ = piece_for(si)
    if full:
        full += " "; st.append(0.0); en.append(0.0)
        parts.append(np.zeros(int(0.3 * SR), np.float32)); pos += 0.3
    base_i = len(full)
    spans += [(a + base_i, b + base_i, s_, l_) for a, b, s_, l_ in sp]
    full += text
    st += [v + pos for v in st_]; en += [v + pos for v in en_]
    parts.append(x.astype(np.float32)); pos += len(x) / SR
audio = np.concatenate(parts)
assert len(st) == len(full)

# Zeilen mit Wortzeiten
lines = []
for a, b, si, li in spans:
    words, i = [], a
    while i < b:
        if full[i] == " ":
            i += 1; continue
        j = i
        while j < b and full[j] != " ":
            j += 1
        words.append({"w": full[i:j], "start": st[i], "end": en[j - 1]})
        i = j
    lines.append({"seg": si, "idx": li, "text": SEGMENTS[si]["lines"][li][2],
                  "start": words[0]["start"], "end": words[-1]["end"], "words": words})


def shift(from_line, dt):
    for ln in lines[from_line:]:
        ln["start"] += dt; ln["end"] += dt
        for wd in ln["words"]:
            wd["start"] += dt; wd["end"] += dt


# 1) Anfang bündig
head = max(lines[0]["start"] - 0.03, 0)
audio = audio[int(head * SR):]; shift(0, -head)

# 2) Pausen zwischen Sätzen kürzen (von hinten nach vorne schneiden)
for i in range(len(lines) - 2, -1, -1):
    gap = lines[i + 1]["start"] - lines[i]["end"]
    if gap > MAX_GAP:
        cut = gap - MAX_GAP
        a = int((lines[i]["end"] + 0.04) * SR)     # direkt nach dem Satzende schneiden
        audio = np.concatenate([audio[:a], audio[a + int(cut * SR):]])
        shift(i + 1, -cut)

# 3) Tempo (gleiche Tonhöhe)
tin, tout = HERE / "_t_in.wav", HERE / "_t_out.wav"
with wave.open(str(tin), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tin), "-af", f"atempo={TEMPO}", str(tout)], check=True)
with wave.open(str(tout)) as w:
    audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
tin.unlink(); tout.unlink()
for ln in lines:
    ln["start"] /= TEMPO; ln["end"] /= TEMPO
    for wd in ln["words"]:
        wd["start"] /= TEMPO; wd["end"] /= TEMPO

# 4) Platz für die Animation vor jedem Kommentar einfügen
segs = []
for si, seg in enumerate(SEGMENTS):
    first = next(k for k, ln in enumerate(lines) if ln["seg"] == si)
    if seg["pre"] > 0:
        # Pause direkt NACH dem vorigen Satz einfügen (nicht vor dem neuen Wort -> kein Gestotter)
        at = lines[first - 1]["end"] + 0.04 if first > 0 else max(lines[first]["start"] - 0.05, 0)
        audio = np.concatenate([audio[:int(at * SR)], np.zeros(int(seg["pre"] * SR), np.float32), audio[int(at * SR):]])
        shift(first, seg["pre"])
    last = max(k for k, ln in enumerate(lines) if ln["seg"] == si)
    segs.append({"key": seg["key"], "user": seg["user"], "comment": seg["comment"],
                 "event": round(lines[first]["start"] - seg["pre"], 3),
                 "speak": round(lines[first]["start"], 3), "end": round(lines[last]["end"], 3)})

for ln in lines:
    ln["start"] = round(ln["start"], 3); ln["end"] = round(ln["end"], 3)
    for wd in ln["words"]:
        wd["start"] = round(wd["start"], 3); wd["end"] = round(wd["end"], 3)

ev = {s["key"]: s["event"] for s in segs}
sfx = [{"file": f"../../sounds/sfx/{name}.wav", "from": 0, "to": 9, "at": round(ev[k] + off, 3)} for k, name, off in SFX]

with wave.open(str(HERE / "voice.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
hop = SR // 25
env = [float(np.sqrt(np.mean(audio[k:k + hop] ** 2))) for k in range(0, len(audio), hop)]
m = max(env)
json.dump([round(min(e / m * 1.6, 1.0), 3) for e in env], open(HERE / "envelope.json", "w"))
dur = round(len(audio) / SR + 0.3, 3)
json.dump({"duration": dur, "lines": lines, "segments": segs, "sfx": sfx},
          open(HERE / "timeline.json", "w"), indent=1, ensure_ascii=False)
print("Tag 2:", dur, "s")
