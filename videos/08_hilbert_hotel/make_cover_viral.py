"""Viral cover for #8 (1080x1920): booked-out endless hotel + infinite bus, no answer shown."""
import os, sys, importlib.util
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from fx3d import pill3d, burst
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)


def cover():
    t = 0.3

    def ex(cv):
        mv.bus(cv, 300, 1600, 0.9, t)
        mv.queue(cv, t, 1.0, x_start=760)
    img, _ = mv.street_scene(t, (540, 960, 1920), ex, people=False)
    img = mv.dim(img, 0.12)
    burst(img, 540, 470, 0.45, t, 170, 430)
    pill3d(img, 540, 290, "99% SCHEITERN", 52, bg="#e2574c", fg="#ffffff", rot=-2)
    pill3d(img, 540, 430, "HOTEL VOLL –", 96, bg="#fff6e6", rot=-3)
    pill3d(img, 540, 585, "+ ∞ GÄSTE?", 108, bg="#ffd34d", rot=2)
    pill3d(img, 540, 1390, "NUR 1 DURCHSAGE. WELCHE?", 46, bg="#a29bfe", fg="#ffffff", rot=-2)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
