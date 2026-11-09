"""Viral cover for #9 (1080x1920): door camera Papa + phone message, no answer."""
import os, sys, importlib.util
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from fx3d import pill3d
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)


def cover():
    img = Image.new("RGB", (OUT_W, OUT_H), (8, 9, 20))
    mv.monitor_view(img, 0.4, stare=1.0, zoom=1.5)
    mv.phone_ui(img, 9.0, [("in", "Sitze noch im Zug. Mach NIEMANDEM auf!", 0)], battery=1, scale=0.5, cx=790, cy=1260)
    pill3d(img, 540, 290, "PAPA KLINGELT …", 60, bg="#fff6e6", rot=-2)
    pill3d(img, 540, 440, "PAPA SCHREIBT?!", 80, bg="#e2574c", fg="#ffffff", rot=2)
    pill3d(img, 330, 1400, "WEM GLAUBST DU?", 46, bg="#ffd34d", rot=-3)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
