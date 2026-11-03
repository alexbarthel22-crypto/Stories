"""TikTok cover (1080x1920). Key content stays inside the 3:4 profile-grid crop (y 240-1680)
and outside TikTok's UI safe zones. No spoiler: Alex is shown in story size."""
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
    cam = (1530, mv.yb(9) - 360, 1300)

    def actors(cv):
        info = mv.draw_cab(cv, 9.0, 1.0)
        draw_person(cv, mv.SX + 10, mv.yb(9), mv.ALEX, face=1)
        mv.draw_cab_doors(cv, info)
        speech_bubble(cv, mv.SX + 205, mv.yb(9) - 300, 52, "?")

    img, view = mv.render_world_frame(0, "dusk", cam, actors)
    # darken top/bottom for readable text
    shade = vgradient(OUT_W, OUT_H, [(0, "#0d1530"), (1, "#0d1530")])
    mask = vgradient(OUT_W, OUT_H, [(0, "#a0a0a0"), (0.22, "#606060"), (0.36, "#000000"), (0.86, "#000000"),
                                     (1, "#707070")]).convert("L")
    img = Image.composite(shade, img, mask)
    # floor display next to the cab
    sx, sy = mv.world_to_screen(mv.SX, mv.yb(9) - mv.CAB_H - 70, view)
    floor_display(img, sx, sy, "9", scale=0.9)
    pill(img, OUT_W / 2, 290, "RÄTSEL", 44, bg="#e2574c", fg="#ffffff", pad=(26, 12))
    l1, l2 = "WARUM FÄHRT ALEX", "NUR BIS ZUM 9. STOCK?"
    pill(img, OUT_W / 2, 420, l1, fit(l1, 960, 88), rot=-2)
    pill(img, OUT_W / 2, 570, l2, fit(l2, 960, 88), bg="#ffd34d", rot=1.5)
    l3 = "Er wohnt im 12.!"
    pill(img, OUT_W / 2, 725, l3, fit(l3, 860, 60), bg="#ffffff", rot=-2)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
