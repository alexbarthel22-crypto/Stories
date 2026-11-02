"""Strafft die Sprecherspur: kürzt lange Pausen innerhalb der Zeilen und beschleunigt
leicht (tonhöhenneutral via ffmpeg atempo). Originale bleiben als *.orig.wav erhalten.
Nutzung: python3 tools/tighten.py <episode-ordner> [tempo=1.08] [max_pause=0.22]"""
import sys, os, json, shutil, subprocess
import numpy as np, soundfile as sf
ep = sys.argv[1]
tempo = float(sys.argv[2]) if len(sys.argv) > 2 else 1.08
maxp = float(sys.argv[3]) if len(sys.argv) > 3 else 0.22
mp = os.path.join(ep, "build", "tts.json")
meta = json.load(open(mp))

def process(f):
    orig = f[:-4] + ".orig.wav"
    if not os.path.exists(orig):
        shutil.copy(f, orig)
    a, sr = sf.read(orig)
    hop = int(0.01 * sr)
    rms = np.array([np.sqrt((a[i:i + hop] ** 2).mean()) for i in range(0, len(a), hop)])
    quiet = rms < max(rms.max() * 0.025, 1e-4)
    keep = np.ones(len(a), bool)
    i = 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            n = j - i
            if n * 0.01 > maxp:
                cut0 = (i + int(maxp / 2 / 0.01)) * hop
                cut1 = (j - int(maxp / 2 / 0.01)) * hop
                keep[cut0:cut1] = False
            i = j
        else:
            i += 1
    b = a[keep]
    tmp = f[:-4] + ".tmp.wav"
    sf.write(tmp, b, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"atempo={tempo}", f], check=True)
    os.remove(tmp)
    return sf.info(f).duration

files = [os.path.join(ep, "build/tts/intro_pre.wav"), os.path.join(ep, "build/tts/intro_role.wav")]
meta["intro"]["pre"] = process(files[0])
meta["intro"]["role"] = process(files[1])
for s in meta["scenes"]:
    for l in s["lines"]:
        l["dur"] = process(l["file"])
json.dump(meta, open(mp, "w"), indent=1, ensure_ascii=False)
print("Sprechzeit Szenen: %.1fs" % sum(l["dur"] for s in meta["scenes"] for l in s["lines"]))
