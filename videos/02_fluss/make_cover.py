"""TikTok cover (1080x1920) for riddle #2, spoiler-free, text inside the 3:4 grid crop and safe zones."""
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
        mv.draw_scene(cv, 0, solution=False, niklas_in_boat=False)
        draw_person(cv, mv.NIKLAS_BANK_X, mv.FAR_Y, mv.NIKLAS, face=-1, h=mv.NIKLAS.h * mv.SCALE["L"])
        speech_bubble(cv, mv.NIKLAS_BANK_X + 75, mv.FAR_Y - 215, 30, "?")

    img, view = mv.render_world_frame((400, 650, 1300), actors)
    shade = vgradient(OUT_W, OUT_H, [(0, "#0d1530"), (1, "#0d1530")])
    mask = vgradient(OUT_W, OUT_H, [(0, "#909090"), (0.3, "#606060"), (0.45, "#000000"), (1, "#000000")]).convert("L")
    img = Image.composite(shade, img, mask)
    pill(img, OUT_W / 2, 290, "RÄTSEL", 44, bg="#e2574c", fg="#ffffff", pad=(26, 12))
    l1, l2 = "WOLF, ZIEGE, KOHL:", "WIE KOMMEN ALLE RÜBER?"
    pill(img, OUT_W / 2, 420, l1, fit(l1, 960, 84), rot=-2)
    pill(img, OUT_W / 2, 570, l2, fit(l2, 960, 84), bg="#ffd34d", rot=1.5)
    l3 = "Im Boot nur 1 Platz!"
    pill(img, OUT_W / 2 - 60, 1400, l3, fit(l3, 760, 60), bg="#ffffff", rot=-2)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
