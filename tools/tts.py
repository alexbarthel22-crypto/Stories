"""Erzeugt die Sprecherspur (eine WAV pro Zeile) mit Piper (lokale deutsche Stimme).

Nutzung: python3 tools/tts.py <episode-ordner> <voice.onnx> [length_scale]
Schreibt <episode>/build/tts/*.wav und <episode>/build/tts.json
"""
import sys, os, json, wave, importlib.util
import numpy as np
from piper import PiperVoice, SynthesisConfig

ep_dir, model = sys.argv[1], sys.argv[2]
length_scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.9

spec = importlib.util.spec_from_file_location("script", os.path.join(ep_dir, "script.py"))
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

out = os.path.join(ep_dir, "build", "tts")
os.makedirs(out, exist_ok=True)
voice = PiperVoice.load(model)
cfg = SynthesisConfig(length_scale=length_scale, noise_scale=0.6, noise_w_scale=0.7)


def synth(text, path, ls=None):
    c = cfg if ls is None else SynthesisConfig(length_scale=ls, noise_scale=0.6, noise_w_scale=0.7)
    with wave.open(path, "wb") as w:
        voice.synthesize_wav(text, w, syn_config=c)
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    # Stille am Anfang/Ende abschneiden
    thr = 300
    nz = np.where(np.abs(a) > thr)[0]
    a = a[max(0, nz[0] - int(0.01 * sr)): nz[-1] + int(0.04 * sr)] if len(nz) else a
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(a.tobytes())
    return len(a) / sr


meta = {"intro": {}, "scenes": []}
meta["intro"]["pre"] = synth("Heute ist Alex ...", f"{out}/intro_pre.wav", length_scale * 1.0)
meta["intro"]["role"] = synth(script.ROLE_TTS, f"{out}/intro_role.wav", length_scale * 1.05)
for s in script.SCENES:
    lines = []
    for i, (cap, say) in enumerate(s["lines"]):
        p = f"{out}/{s['id']}_{i}.wav"
        d = synth(say or cap, p)
        lines.append({"file": p, "dur": d, "caption": cap})
    meta["scenes"].append({"id": s["id"], "lines": lines})

json.dump(meta, open(os.path.join(ep_dir, "build", "tts.json"), "w"), indent=1, ensure_ascii=False)
tot = sum(l["dur"] for s in meta["scenes"] for l in s["lines"])
print("Sprechzeit Szenen: %.1fs  Intro: %.1f+%.1f" % (tot, meta["intro"]["pre"], meta["intro"]["role"]))
