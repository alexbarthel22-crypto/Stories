"""Viral cover for #7 (1080x1920): Leon vs. Mia, both offers, no answer."""
import os, sys, importlib.util, math
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from fx3d import BCanvas, pill3d, burst
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)


def cover():
    t = 0.0
    lay = Image.new("RGBA", (OUT_W * 2, OUT_H * 2), (0, 0, 0, 255))
    cv = BCanvas(lay, 0, 0, 2)
    cv.poly([(0, 0), (640, 0), (440, 1920), (0, 1920)], fill=hexc("#ffc93c"))
    cv.poly([(640, 0), (1080, 0), (1080, 1920), (440, 1920)], fill=hexc("#3cc9a4"))
    for i in range(18):
        a = i / 18 * 2 * math.pi
        cv.poly([(540, 1050), (540 + math.cos(a) * 1600, 1050 + math.sin(a) * 1600),
                 (540 + math.cos(a + 0.1) * 1600, 1050 + math.sin(a + 0.1) * 1600)], fill=(255, 255, 255, 22))
    cv.line([(640, 0), (440, 1920)], hexc("#ffffff"), 14)
    for i in range(10):
        mv.banknote(cv, 80 + (i * 97) % 380, 1150 + (i * 53) % 300, 0.8, i * 0.7)
    mv.leon(cv, 250, 1470, 450, 1, t=t, shades=True, chain=True, wave=1.0, talk=0.8)
    mv.mia(cv, 840, 1470, 450, -1, mood="smirk")
    img = lay.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)
    mv.option_card(img, 300, 780, 0.76, "million", t)
    mv.option_card(img, 770, 780, 0.76, "cent", t)
    burst(img, 540, 780, 0.6, t, 50, 150, (255, 255, 255), 12)
    pill3d(img, 540, 780, "VS", 70, bg="#1d1b33", fg="#ffd34d", rot=-6)
    pill3d(img, OUT_W / 2, 290, "99% WÄHLEN FALSCH", 52, bg="#e2574c", fg="#ffffff", rot=-2)
    pill3d(img, OUT_W / 2, 430, "WAS NIMMST DU?", 96, bg="#ffd34d", rot=-3, max_w=860)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
