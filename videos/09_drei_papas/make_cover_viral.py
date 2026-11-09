"""Viral cover for #9 (1080x1920): the three Papas (door, phone, stairs) in the dark house, no answer."""
import os, sys, importlib.util
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from fx3d import pill3d, burst, BCanvas
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)


def cover():
    t = 0.5
    img, _ = mv.stage((560, 1100, 1500), lambda cv: (mv.house_life(cv, t, shower=True),
                                                    mv.people(cv, t, du_kw=dict(mood="o", look=(-0.6, -0.6)),
                                                              lina_kw=dict(mood="worried"))))
    img = mv.darkness(img, 0.72, holes=[(560, 1350, 330)])
    lay = Image.new("RGBA", (OUT_W * 2, OUT_H * 2), (0, 0, 0, 0))
    cv = BCanvas(lay, 0, 0, 2)
    for k, kind in enumerate(("door", "phone", "stairs")):
        mv.icon_card(cv, 205 + k * 290, 820, kind, 1.0, t)
    lay = lay.resize((OUT_W, OUT_H), Image.LANCZOS)
    img.paste(lay, (0, 0), lay)
    for k, lab in enumerate(("TÜR", "HANDY", "TREPPE")):
        pill3d(img, 205 + k * 290, 1070, lab, 40, bg="#fff6e6", depth=6)
    burst(img, 540, 360, 0.35, t, 150, 380, (226, 87, 76))
    pill3d(img, 540, 335, "3 PAPAS", 110, bg="#ffd34d", rot=-3)
    pill3d(img, 540, 500, "NUR 1 IST ECHT", 72, bg="#e2574c", fg="#ffffff", rot=2)
    pill3d(img, 540, 1240, "WEM GLAUBST DU?", 66, bg="#fff6e6", rot=-2)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
