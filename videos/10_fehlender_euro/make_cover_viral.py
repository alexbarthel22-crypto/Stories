"""Viral cover for #10 (1080x1920): pizzeria table, corgi, the wrong sum – no answer."""
import os, sys, importlib.util
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from fx3d import pill3d, burst
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)


def cover():
    t = 0.4

    def act(cv):
        mv.room_life(cv, t)
        mv.friends(cv, t, lambda i: dict(mood="o", look=(0, -0.4)))
        mv.corgi(cv, 600, mv.FLOOR + 60, 1.25, t, 1, beg=0.6, wag=1.0)
    img, _ = mv.stage("pizzeria", (540, 1080, 1500), act)
    img = Image.blend(img, Image.new("RGB", img.size, (15, 10, 30)), 0.2)
    burst(img, 540, 400, 0.4, t, 160, 420)
    pill3d(img, 540, 290, "99% RECHNEN FALSCH", 50, bg="#e2574c", fg="#ffffff", rot=-2)
    pill3d(img, 540, 430, "57 + 2 = 59 ?!", 100, bg="#ffd34d", rot=-3)
    pill3d(img, 540, 580, "WO IST DER 1 €?", 76, bg="#fff6e6", rot=2)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
