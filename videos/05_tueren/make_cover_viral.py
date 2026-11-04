"""Viral-style cover for riddle #5 (1080x1920): challenge hook, all three dangers visible, no spoiler."""
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
        mv.cellar_life(cv, 1.2)
        mv.torches(cv, 0.3)
        mv.draw_doors(cv, 0.55, [0.85, 0.85, 0.85])
        draw_person(cv, 540, 1450, mv.DU, face=1, h=330, talk=1.0)
        speech_bubble(cv, 650, 1080, 48, "?")

    img, view = mv.render_world_frame((540, 1000, 1700), actors)
    shade = vgradient(OUT_W, OUT_H, [(0, "#0b0a12"), (1, "#0b0a12")])
    mask = vgradient(OUT_W, OUT_H, [(0, "#b0b0b0"), (0.2, "#707070"), (0.3, "#000000"), (1, "#000000")]).convert("L")
    img = Image.composite(shade, img, mask)
    pill(img, OUT_W / 2, 270, "NUR 1 TÜR IST SICHER", 46, bg="#e2574c", fg="#ffffff", pad=(26, 12), rot=-2)
    l1 = "WELCHE NIMMST DU?"
    pill(img, OUT_W / 2 - 20, 410, l1, fit(l1, 880, 96), bg="#ffd34d", rot=-2)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
