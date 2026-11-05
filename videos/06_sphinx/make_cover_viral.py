"""Viral-style cover for riddle #6 (1080x1920): Sphinx with glowing eyes + the riddle hook, no spoiler."""
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
    t = 1.0
    pal = mv._pal_mix("evening", "golden", 0.45)

    def actors(cv):
        mv.ground_actors(cv, t)
        mv.sphinx_eyes(cv, 1.0, 0.2)

    img, view = mv.render_world_frame((470, 1060, 1150), actors, pal, t)
    shade = vgradient(OUT_W, OUT_H, [(0, "#120c22"), (1, "#120c22")])
    mask = vgradient(OUT_W, OUT_H, [(0, "#b4b4b4"), (0.22, "#707070"), (0.33, "#000000"), (1, "#000000")]).convert("L")
    img = Image.composite(shade, img, mask)
    pill(img, OUT_W / 2, 270, "99% SCHEITERN HIER", 48, bg="#e2574c", fg="#ffffff", pad=(26, 12), rot=-2)
    l1 = "DAS RÄTSEL DER SPHINX"
    pill(img, OUT_W / 2 - 10, 410, l1, fit(l1, 900, 84), bg="#ffd34d", rot=-2)
    pill(img, OUT_W / 2, 1380, "4 → 2 → 3 BEINE ?", 64, bg="#fff6e6", rot=2, border="#1d1b33")
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
