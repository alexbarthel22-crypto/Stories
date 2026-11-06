"""Viral-style cover for riddle #6 (1080x1920): close-up of the Sphinx with glowing eyes at dusk, no spoiler."""
import os, sys, importlib.util
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)


def cover():
    t = 1.3
    pal = mv._pal_mix("evening", "night", 0.35)

    def main(cv, box):
        mv.sphinx_eyes(cv, 1.0, 0.25)
        mv.sphinx_eyes(cv, 1.0, 0.25)
        mv.sand_wind(cv, t)

    img, _ = mv.render_scene((470, 945, 1000), t, pal, {"far": mv.far_actors(t), "mid": mv.mid_actors(t),
                                                         "main": main, "fg": mv.fg_actors(t, 1.0)})
    shade = Image.new("RGB", img.size, (12, 8, 30))
    mask = vgradient(OUT_W, OUT_H, [(0, "#c8c8c8"), (0.24, "#707070"), (0.36, "#000000"), (0.62, "#000000"),
                                    (0.8, "#909090"), (1, "#c8c8c8")]).convert("L")
    img = Image.composite(shade, img, mask)
    mv.burst(img, OUT_W / 2, 430, 0.55, 0.4, 200, 470)
    mv.pill3d(img, OUT_W / 2, 290, "NUR 1% LÖST ES", 56, bg="#e2574c", fg="#ffffff", rot=-2)
    mv.pill3d(img, OUT_W / 2, 440, "DAS RÄTSEL", 104, bg="#ffd34d", rot=-3, max_w=860)
    mv.pill3d(img, OUT_W / 2, 590, "DER SPHINX", 104, bg="#fff6e6", rot=2, max_w=860)
    for k, (kind, n) in enumerate((("rise", "4"), ("sun", "2"), ("moon", "3"))):
        x = 270 + k * 270
        mv.sun_icon(img, x, 1275, kind, 0.5, 0.9)
        mv.pill3d(img, x, 1405, n + " BEINE", 46, bg="#ffd34d" if k != 1 else "#fff6e6", rot=(-3, 2, -2)[k], depth=8)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
