"""Offline German TTS (Piper). Writes voice.wav + timing.json.

usage: python3 tts.py script.txt out_dir --model main.onnx [--emo-model thorsten_emotional.onnx]
                      [--speaker NAME] [--length 0.85] [--pitch 1.5]

Script lines: '#' = comment, '[PAUSE x]' = x seconds silence,
'{emotion} text' = speak this line with the emotion model's speaker (e.g. amused, surprised).
"""
import sys, json, re, subprocess, tempfile, os, unicodedata
import numpy as np, soundfile as sf
from piper import PiperVoice, SynthesisConfig

# words espeak-ng gets wrong -> IPA (stress marks allowed)
LEXICON = {
    "kleinwüchsig": "klˈaɪnˌvyːksɪç",
}


def make_phonemizer(voice):
    orig = voice.phonemize

    def phonemize(text):
        out = []
        words = {w.lower(): w for w in re.findall(r"\w+", text)}
        for sent in orig(text):
            s = unicodedata.normalize("NFC", "".join(sent))   # 'c'+U+0327 -> 'ç'
            for word, ipa in LEXICON.items():
                if word in words:
                    wrong = unicodedata.normalize("NFC", "".join(sum(orig(word), [])).strip(".!?, "))
                    s = s.replace(wrong, ipa)
            out.append([p for p in s if p in voice.config.phoneme_id_map])
        return out

    voice.phonemize = phonemize


def pitch_shift(a, sr, semitones):
    if not semitones:
        return a
    with tempfile.TemporaryDirectory() as d:
        i, o = os.path.join(d, "i.wav"), os.path.join(d, "o.wav")
        sf.write(i, a, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", i, "-af",
                        f"rubberband=pitch={2 ** (semitones / 12):.5f}:formant=preserved", o], check=True)
        return sf.read(o, dtype="float32")[0]


def load(model):
    v = PiperVoice.load(model, config_path=model + ".json")
    make_phonemizer(v)
    return v


def main(script, out_dir, model, emo_model=None, speaker=None, length_scale=0.85, semitones=0.0, gap=0.10):
    main_voice = load(model)
    emo_voice = load(emo_model) if emo_model else main_voice
    sr = main_voice.config.sample_rate
    chunks, timing, t = [], [], 0.0
    lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip() and not l.startswith("#")]
    for l in lines:
        m = re.match(r"\[PAUSE ([\d.]+)\]", l)
        if m:
            d = float(m.group(1)); chunks.append(np.zeros(int(sr*d), np.float32))
            timing.append({"text": "PAUSE", "start": round(t, 3), "end": round(t+d, 3)}); t += d; continue
        voice, emo = main_voice, speaker
        m = re.match(r"\{(\w+)\}\s*(.*)", l)
        if m:
            voice, emo, l = emo_voice, m.group(1), m.group(2)
        spk_map = voice.config.speaker_id_map or {}
        cfg = SynthesisConfig(length_scale=length_scale, noise_scale=0.667, noise_w_scale=0.8,
                              speaker_id=spk_map.get(emo) if spk_map else None)
        a = np.concatenate([c.audio_float_array for c in voice.synthesize(l, syn_config=cfg)]).astype(np.float32)
        nz = np.where(np.abs(a) > 0.004)[0]
        a = a[max(nz[0]-int(sr*0.01), 0):nz[-1]+int(sr*0.09)]
        a = a / (np.abs(a).max() + 1e-9) * 0.9   # even loudness across emotions
        g = gap + (0.16 if l[-1] in ".!?" else 0.0)
        timing.append({"text": l, "start": round(t, 3), "end": round(t+len(a)/sr, 3)})
        chunks += [a, np.zeros(int(sr*g), np.float32)]; t += len(a)/sr + g
    v = np.concatenate(chunks)
    v = pitch_shift(v, sr, semitones)
    v = v / np.abs(v).max() * 0.9
    sf.write(f"{out_dir}/voice.wav", v, sr)
    json.dump(timing, open(f"{out_dir}/timing.json", "w"), ensure_ascii=False, indent=1)
    w = sum(len(x["text"].split()) for x in timing if x["text"] != "PAUSE")
    print(f"duration {t:.1f}s  words {w}  wpm {w/t*60:.0f}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("script"); ap.add_argument("out_dir")
    ap.add_argument("--model", required=True); ap.add_argument("--emo-model")
    ap.add_argument("--speaker"); ap.add_argument("--length", type=float, default=0.85)
    ap.add_argument("--pitch", type=float, default=0.0)
    a = ap.parse_args()
    main(a.script, a.out_dir, a.model, a.emo_model, a.speaker, a.length, a.pitch)
