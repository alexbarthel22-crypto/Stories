"""Viral-style cover for riddle #4 (1080x1920): same 'ZIEL / GENAU 4 LITER' stamp as the first frame,
glowing 5 L / 3 L buckets, fireworks, no spoiler. Text inside the 3:4 grid crop and TikTok safe zones."""
import os, sys, math, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
spec = importlib.util.spec_from_file_location("mv", os.path.join(HERE, "make_video.py"))
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)
pill = mv.pill            # high-contrast party style


def cover():
    T = 1.15              # a moment with big fireworks in the sky

    def actors(cv):
        mv.big_fireworks(cv, T)
        mv.string_lights(cv, T)
        mv.party_background(cv, T)
        mv.draw_barrel(cv, 0)
        draw_person(cv, mv.DARIO_HOME, mv.FLOOR, mv.DARIO, face=-1, h=mv.PERSON_H["dario"], talk=1.0,
                    reach=(mv.DARIO_HOME - 160, mv.TABLE[2] - 60))
        mv.draw_table(cv)
        for n in ("big", "small"):
            bx, by = mv.BUCKETS[n]["home"]
            b = mv.BUCKETS[n]
            for k in range(5, 0, -1):
                cv.circle(bx, by - b["h"] * 0.6, b["tw"] * (0.45 + 0.22 * k), fill=(255, 211, 77, 34))
            sc = 1.35
            sub = Canvas(cv.img, bx - (bx - cv.ox) / sc, by - (by - cv.oy) / sc, cv.s * sc)
            mv.draw_bucket(sub, n, bx, by, 0)

    img, view = mv.render_world_frame(mv.CAM, actors)
    pill(img, OUT_W / 2, 285, "ZIEL", 50, bg="#e2574c", fg="#ffffff", pad=(26, 10), rot=-4)
    pill(img, OUT_W / 2, 415, "GENAU 4 LITER", 96, bg="#ffd34d", rot=2, pad=(36, 16))
    pill(img, OUT_W / 2, 560, "NUR MIT 5 L + 3 L EIMER", 50, bg="#ffffff", rot=-2)
    for n, lab in (("big", "5 L"), ("small", "3 L")):
        x, y = mv.BUCKETS[n]["home"]
        sx, sy = mv.w2s(x, y + 50, view)
        pill(img, sx, sy, lab, 58, bg="#ffd34d", pad=(22, 10))
    sx, sy = mv.w2s(mv.DARIO_HOME + 170, mv.FLOOR - mv.PERSON_H["dario"] * 0.82, view)
    pill(img, min(sx, 800), sy, "?", 110, bg="#37b26c", fg="#ffffff", rot=8)
    return img


if __name__ == "__main__":
    UI_LOG.clear()
    img = cover()
    for lab, *box in UI_LOG:
        v = safe_violation(*box)
        print(("SAFE-ZONE " + "/".join(v)) if v else "ok", lab, [int(b) for b in box])
    img.save(os.path.join(HERE, "cover.png"))
    img.save(os.path.join(HERE, "cover.jpg"), quality=92)
