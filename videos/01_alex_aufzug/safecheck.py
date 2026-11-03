"""Checks all screen-space UI elements against TikTok safe zones; optional guide stills.

usage: python3 safecheck.py            -> report
       python3 safecheck.py --stills   -> also writes stills with safe-zone guides to ./stills_safe
"""
import os, sys
sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:]]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import toolkit as tk
import importlib.util
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
from PIL import ImageDraw

bad = {}
t = 0.0
stills = "--stills" in sys.argv
if stills:
    os.makedirs(os.path.join(HERE, "stills_safe"), exist_ok=True)
while t < mv.END:
    tk.UI_LOG.clear()
    img = mv.frame_at(t)
    for lab, x0, y0, x1, y1 in tk.UI_LOG:
        v = tk.safe_violation(x0, y0, x1, y1)
        if v:
            key = (lab, tuple(v))
            bad.setdefault(key, [t, t, (int(x0), int(y0), int(x1), int(y1))])[1] = t
    if stills and abs((t * 2) - round(t * 2)) < 1e-6:
        d = ImageDraw.Draw(img, "RGBA")
        red = (255, 0, 0, 70)
        d.rectangle([0, 0, 1080, tk.SAFE_TOP], fill=red)
        d.rectangle([0, tk.SAFE_BOTTOM, 1080, 1920], fill=red)
        d.rectangle([tk.SAFE_RIGHT, tk.SAFE_RIGHT_Y[0], 1080, tk.SAFE_RIGHT_Y[1]], fill=red)
        img.resize((270, 480)).save(os.path.join(HERE, "stills_safe", f"t{t:05.1f}.jpg"), quality=80)
    t = round(t + 0.1, 2)
if not bad:
    print("OK: no UI element enters a TikTok safe zone")
for (lab, v), (t0, t1, box) in sorted(bad.items(), key=lambda kv: kv[1][0]):
    print(f"{t0:5.1f}-{t1:5.1f}s  {'/'.join(v):12s} {lab:32s} box={box}")
