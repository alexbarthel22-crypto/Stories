"""Folge 1 – Tonspur mit lokaler Piper-Stimme (Kerstin), komplett offline, kein Kontingent.
Erzeugt voice.wav, timeline.json (Satz-Zeiten für Untertitel) und envelope.json (Mundbewegung)."""
import json, subprocess, wave, sys
from pathlib import Path
import numpy as np

MODEL = sys.argv[1] if len(sys.argv) > 1 else "de-kerstin-low.onnx"
SR = 16000
LINES = [  # (Text für die Stimme, Untertitel, Sprechtempo, Lautstärke, Pause danach in s)
    ("Was glotzt du so?!", "WAS GLOTZT DU SO?!", 0.78, 2.6, 0.55),
    ("Bro, gestern war ich auf einem Reiv,", "Bro, gestern war ich auf einem Rave …", 0.86, 1.4, 0.1),
    ("und bin heute hier aufgewacht.", "… und bin heute HIER aufgewacht.", 0.88, 1.4, 0.35),
    ("Wer will mich hier hopps nehmen?!", "Wer will mich hier hopps nehmen?!", 0.84, 1.7, 0.45),
    ("Was soll der Mist?", "Was soll der Mist?!", 0.82, 1.6, 0.2),
    ("Hier ist ja gar nichts!", "Hier ist ja GAR NICHTS!", 0.85, 1.6, 0.55),
    ("Und das Beste:", "Und das Beste:", 0.95, 1.3, 0.3),
    ("Ausnahmslos alles, was ihr in die Kommentare schreibt,", "Ausnahmslos ALLES, was ihr in die Kommentare schreibt …", 0.86, 1.4, 0.1),
    ("wird mit mir und der Insel gemacht.", "… wird mit mir und der Insel gemacht.", 0.88, 1.4, 0.45),
    ("Das kann ja nur scheiße werden.", "Das kann ja nur sch🥚sse werden.", 0.9, 1.4, 0.4),
    ("Wow.", "Wow.", 1.5, 1.2, 0.6),
    ("Ja, dann kommentiert mal.", "Ja, dann kommentiert mal.", 0.92, 1.4, 0.3),
    ("Nur, egal was ihr macht.", "Nur … egal, was ihr macht.", 0.95, 1.3, 0.3),
]
START = 0.25
out, timeline, t = [np.zeros(int(START * SR), np.float32)], [], START
for i, (text, sub, speed, gain, pause) in enumerate(LINES):
    fn = f"_line{i}.wav"
    subprocess.run(["piper", "-m", MODEL, "-f", fn, "--length-scale", str(speed),
                    "--noise-scale", "0.75", "--noise-w-scale", "0.9"],
                   input=text.encode(), check=True, capture_output=True)
    with wave.open(fn) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if sr != SR:
        a = np.interp(np.linspace(0, len(a), int(len(a) * SR / sr), endpoint=False), np.arange(len(a)), a)
    # Stille am Rand abschneiden
    nz = np.where(np.abs(a) > 0.02)[0]
    a = a[max(nz[0] - 200, 0): nz[-1] + 400]
    a = np.tanh(a / max(np.abs(a).max(), 1e-6) * gain) * 0.9   # lauter + leicht „gepresst“
    dur = len(a) / SR
    timeline.append({"text": sub, "start": round(t, 3), "end": round(t + dur, 3)})
    out += [a.astype(np.float32), np.zeros(int(pause * SR), np.float32)]
    t += dur + pause
    Path(fn).unlink()
audio = np.concatenate(out)
with wave.open("voice.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((audio * 32767).astype(np.int16).tobytes())
FPS = 25
hop = SR // FPS
env = [float(np.sqrt(np.mean(audio[k:k + hop] ** 2))) for k in range(0, len(audio), hop)]
m = max(env)
json.dump([round(min(e / m * 1.6, 1.0), 3) for e in env], open("envelope.json", "w"))
json.dump({"duration": round(t, 3), "lines": timeline}, open("timeline.json", "w"), indent=1, ensure_ascii=False)
print("Sprechdauer", round(t, 2), "s")
