"""TikTok cover (1080x1920) for riddle #5: challenge hook, three half-open doors, no spoiler."""
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
        mv.torches(cv, 0.3)
        mv.draw_doors(cv, 0.4, [0.55, 0.55, 0.55])
        draw_person(cv, 540, 1440, mv.DU, face=1, h=300)
        speech_bubble(cv, 640, 1080, 44, "?")

    img, view = mv.render_world_frame(mv.FULL, actors)
    shade = vgradient(OUT_W, OUT_H, [(0, "#0b0a12"), (1, "#0b0a12")])
    mask = vgradient(OUT_W, OUT_H, [(0, "#a0a0a0"), (0.2, "#606060"), (0.3, "#000000"), (1, "#000000")]).convert("L")
    img = Image.composite(shade, img, mask)
    pill(img, OUT_W / 2, 285, "NUR 1 TÜR IST SICHER", 44, bg="#e2574c", fg="#ffffff", pad=(26, 12), rot=-2)
    l1 = "WELCHE WÄHLST DU?"
    pill(img, OUT_W / 2 - 20, 425, l1, fit(l1, 880, 92), bg="#ffd34d", rot=-2)
    for k, lab in enumerate(("TIGER", "PISTOLE", "PIRAT")):
        sx, sy = mv.w2s(mv.DOOR_X[k], mv.DOOR_RECT_TOP - mv.DOOR_W / 2 - 150, view)
        pill(img, sx, sy, lab, 40, bg="#fff6e6", pad=(16, 9), rot=(-3, 2, -2)[k])
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
