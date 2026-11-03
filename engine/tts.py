"""Offline German TTS (Piper). Writes voice.wav + timing.json.

usage: python3 tts.py script.txt model.onnx out_dir [length_scale]
Lines starting with '#' are ignored, '[PAUSE x]' inserts x seconds of silence.
"""
import sys, json, re, numpy as np, soundfile as sf
from piper import PiperVoice, SynthesisConfig

def main(script, model, out_dir, length_scale=0.78, gap=0.10):
    voice = PiperVoice.load(model, config_path=model + ".json")
    sr = voice.config.sample_rate
    cfg = SynthesisConfig(length_scale=length_scale, noise_scale=0.6, noise_w_scale=0.7)
    chunks, timing, t = [], [], 0.0
    lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip() and not l.startswith("#")]
    for l in lines:
        m = re.match(r"\[PAUSE ([\d.]+)\]", l)
        if m:
            d = float(m.group(1)); chunks.append(np.zeros(int(sr*d), np.float32))
            timing.append({"text": "PAUSE", "start": round(t, 3), "end": round(t+d, 3)}); t += d; continue
        a = np.concatenate([c.audio_float_array for c in voice.synthesize(l, syn_config=cfg)]).astype(np.float32)
        nz = np.where(np.abs(a) > 0.01)[0]
        a = a[max(nz[0]-160, 0):nz[-1]+320]
        g = gap + (0.16 if l[-1] in ".!?" else 0.0)
        timing.append({"text": l, "start": round(t, 3), "end": round(t+len(a)/sr, 3)})
        chunks += [a, np.zeros(int(sr*g), np.float32)]; t += len(a)/sr + g
    v = np.concatenate(chunks); v = v / np.abs(v).max() * 0.9
    sf.write(f"{out_dir}/voice.wav", v, sr)
    json.dump(timing, open(f"{out_dir}/timing.json", "w"), ensure_ascii=False, indent=1)
    w = sum(len(x["text"].split()) for x in timing if x["text"] != "PAUSE")
    print(f"duration {t:.1f}s  words {w}  wpm {w/t*60:.0f}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 0.78)
