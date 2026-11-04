"""TikTok cover (1080x1920) for riddle #4, spoiler-free, text inside the 3:4 grid crop and safe zones."""
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
        mv.draw_scene(cv, 0, solution=False, dario_face=-1)

    img, view = mv.render_world_frame((540, 1000, 1700), actors)
    for n, lab in (("big", "5 L"), ("small", "3 L")):
        x, y = mv.BUCKETS[n]["home"]
        sx, sy = mv.w2s(x, y - mv.BUCKETS[n]["h"] / 2, view)
        pill(img, sx, sy, lab, 56, pad=(20, 10))
    sx, sy = mv.w2s(680, mv.FLOOR - 360, view)
    pill(img, sx, sy, "4 L ?", 64, bg="#37b26c", fg="#ffffff", rot=4)
    pill(img, OUT_W / 2, 300, "RÄTSEL", 44, bg="#e2574c", fg="#ffffff", pad=(26, 12))
    l1, l2 = "NUR 5 L + 3 L EIMER:", "WIE MISST ER 4 LITER AB?"
    pill(img, OUT_W / 2 - 25, 430, l1, fit(l1, 860, 80), rot=-2)
    pill(img, OUT_W / 2 - 25, 580, l2, fit(l2, 860, 80), bg="#ffd34d", rot=1.5)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
