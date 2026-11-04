"""High-contrast 'challenge' cover for TikTok (1080x1920): big 3-word hook, close-up, curiosity gap, no spoiler."""
import os, sys, math, importlib.util
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
        mv.string_lights(cv, 1.0)
        mv.party_background(cv, 2.2)
        mv.draw_barrel(cv, 0)
        draw_person(cv, mv.DARIO_HOME, mv.FLOOR, mv.DARIO, face=-1, h=mv.PERSON_H["dario"], talk=1.0,
                    reach=(mv.DARIO_HOME - 160, mv.TABLE[2] - 60))   # pointing at the buckets
        mv.draw_table(cv)
        mv.draw_bucket(cv, "big", *mv.BUCKETS["big"]["home"], 0)
        mv.draw_bucket(cv, "small", *mv.BUCKETS["small"]["home"], 0)

    img, view = mv.render_world_frame((330, 1000, 1300), actors)
    # darken the top for the headline
    shade = vgradient(OUT_W, OUT_H, [(0, "#0b1026"), (1, "#0b1026")])
    mask = vgradient(OUT_W, OUT_H, [(0, "#c8c8c8"), (0.28, "#808080"), (0.4, "#000000"), (1, "#000000")]).convert("L")
    img = Image.composite(shade, img, mask)
    # headline: challenge hook
    pill(img, OUT_W / 2, 285, "NUR 2 EIMER", 44, bg="#e2574c", fg="#ffffff", pad=(26, 12), rot=-2)
    l1 = "SCHAFFST DU DAS?"
    pill(img, OUT_W / 2 - 20, 425, l1, fit(l1, 880, 96), bg="#ffd34d", rot=-2)
    l2 = "GENAU 4 LITER ABMESSEN"
    pill(img, OUT_W / 2 - 20, 570, l2, fit(l2, 860, 64), bg="#ffffff", rot=1.5)
    # bucket stickers + big question mark
    for n, lab in (("big", "5 L"), ("small", "3 L")):
        x, y = mv.BUCKETS[n]["home"]
        sx, sy = mv.w2s(x, y + 50, view)
        pill(img, sx, sy, lab, 60, bg="#ffd34d", pad=(22, 10))
    sx, sy = mv.w2s(205, mv.TABLE[2] - 230, view)
    pill(img, sx, sy, "= 4 L ?", 84, bg="#37b26c", fg="#ffffff", rot=-5)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
