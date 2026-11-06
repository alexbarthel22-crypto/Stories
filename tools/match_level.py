"""Gleicht die Lautstärke jeder Sprachzeile einer Folge an eine Referenzfolge an (Median-RMS).
Nutzung: python3 tools/match_level.py <episode> [referenz=episodes/01_pick_me_boy]  (nach tighten, vor build)"""
import sys, glob, os
import numpy as np, soundfile as sf
ep = sys.argv[1]; ref = sys.argv[2] if len(sys.argv) > 2 else "episodes/01_pick_me_boy"
def rms_db(a): return 20 * np.log10(np.sqrt(np.mean(np.square(a))) + 1e-9)
def lines(e): return [f for f in glob.glob(f"{e}/build/tts/*.wav") if not f.endswith(".orig.wav") and "intro_pre" not in f]
target = float(np.median([rms_db(sf.read(f)[0]) for f in lines(ref)]))
print(f"Ziel {target:.1f} dB")
for f in sorted(lines(ep)):
    a, sr = sf.read(f); g = 10 ** ((target - rms_db(a)) / 20)
    b = a * g; pk = np.max(np.abs(b))
    if pk > 0.98: b *= 0.98 / pk
    sf.write(f, b, sr); print(os.path.basename(f), f"{rms_db(b):.1f} dB")
