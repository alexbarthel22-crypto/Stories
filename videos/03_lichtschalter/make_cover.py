"""TikTok cover (1080x1920) for riddle #3, spoiler-free, text inside the 3:4 grid crop and safe zones."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)


def fit(text, max_w, size):
    while font(size).getbbox(text)[2] + 70 > max_w and size > 30:
        size -= 2
    return size


def cover():
    def actors(cv):
        mv.draw_attic_light(cv, "hidden", 0)
        mv.draw_bulb_world(cv, "hidden", 0)
        mv.draw_world_switches(cv, [False, False, False])
        draw_person(cv, 380, mv.EG_Y, mv.NILS, face=-1, reach=(mv.SW_X[1], mv.SW_Y))

    img, view = mv.render_world_frame(mv.FULL, actors)
    sx, sy = mv.w2s(mv.BULB[0], mv.BULB[1] - 20, view)
    pill(img, sx, sy, "?", 120, bg="#ffd34d")
    pill(img, OUT_W / 2, 300, "RÄTSEL", 44, bg="#e2574c", fg="#ffffff", pad=(26, 12))
    l1, l2 = "3 SCHALTER, 1 LAMPE:", "WELCHER IST ES?"
    pill(img, OUT_W / 2 - 28, 900, l1, fit(l1, 860, 80), rot=-2)
    pill(img, OUT_W / 2 - 20, 1045, l2, fit(l2, 860, 84), bg="#ffd34d", rot=1.5)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
