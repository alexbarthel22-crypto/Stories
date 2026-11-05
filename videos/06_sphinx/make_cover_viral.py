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

    def main(cv, box):
        mv.sphinx_eyes(cv, 1.0, 0.2)
        mv.sand_wind(cv, t)

    img, _ = mv.render_scene((470, 1050, 1150), t, pal, {"far": mv.far_actors(t), "mid": mv.mid_actors(t),
                                                         "main": main, "fg": mv.fg_actors(t, 1.0)})
    shade = vgradient(OUT_W, OUT_H, [(0, "#120c22"), (1, "#120c22")])
    mask = vgradient(OUT_W, OUT_H, [(0, "#b4b4b4"), (0.22, "#707070"), (0.33, "#000000"), (1, "#000000")]).convert("L")
    img = Image.composite(shade, img, mask)
    mv.pill3d(img, OUT_W / 2, 280, "99% SCHEITERN HIER", 50, bg="#e2574c", fg="#ffffff", rot=-2)
    l1 = "DAS RÄTSEL DER SPHINX"
    mv.pill3d(img, OUT_W / 2, 420, l1, 84, bg="#ffd34d", rot=-2, max_w=860)
    mv.pill3d(img, OUT_W / 2, 1380, "4 → 2 → 3 BEINE ?", 66, bg="#fff6e6", rot=2)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
