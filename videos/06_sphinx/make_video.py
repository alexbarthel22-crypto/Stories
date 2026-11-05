"""Rätsel #6 – Das Rätsel der Sphinx (Morgen vier, Mittag zwei, Abend drei Beine).

usage:  python3 make_video.py            -> renders video.mp4 (needs timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from animals import draw_baby, draw_cane

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# ------------------------------------------------------------------ world (bigger than one screen)
W, H = OUT_W, OUT_H
ZW = 2
WX0, WY0, WX1, WY1 = -270, -480, 1350, 2400
HORIZON = 1060
PATH_Y = 1440                    # where people walk (feet), above TikTok's caption area
SAND, SAND_D, SAND_L = "#e3b067", "#c48a45", "#f2cf8e"
STONE, STONE_D = "#d9a35e", "#b07a3c"
GOLD, LAPIS = "#e0b64a", "#2f5aa8"

ADULT = Style(205, "#c98c62", "#1d1712", "#2f8f83", "#e9e0cc", hair_style="quiff", shoes="#7a4f2e",
              accent="#1f5f57", under="#f4efe4")
OLD = Style(205, "#e9b48f", "#e6e6e6", "#7a5c3a", "#4a4a5a", hair_style="short", beard=True, glasses=True,
            shoes="#3a2c22", accent="#5a4228")

# sky palettes: (top, middle, horizon), sun colour, landscape tint (rgba)
PALETTES = {
    "golden":  (("#3d4f9a", "#e8916a", "#ffd08a"), "#ffe2a0", (255, 170, 90, 22)),
    "morning": (("#7d9fdc", "#f4aab0", "#ffe0b0"), "#fff0c8", (255, 190, 200, 28)),
    "noon":    (("#2f86d6", "#7ec4ee", "#dff2fb"), "#fffbe6", (255, 255, 255, 0)),
    "evening": (("#241a4a", "#b34f6a", "#ff9a4a"), "#ffb36b", (110, 50, 140, 60)),
}


def _pal_mix(a, b, f):
    (sa, suna, ta), (sb, sunb, tb) = PALETTES[a], PALETTES[b]
    stops = tuple(mix(hexc(x), hexc(y), f) for x, y in zip(sa, sb))
    sun = mix(hexc(suna), hexc(sunb), f)
    tint = tuple(int(round(p + (q - p) * f)) for p, q in zip(ta, tb))
    return stops, sun, tint


def _grad(img_w, img_h, stops):
    ys = np.linspace(0, 1, img_h)
    pos = [s[0] for s in stops]
    rgb = np.array([s[1] for s in stops], float)
    col = np.stack([np.interp(ys, pos, rgb[:, c]) for c in range(3)], 1)
    return Image.fromarray(np.repeat(col[:, None, :], img_w, axis=1).astype(np.uint8), "RGB")


def draw_pyramid(cv, apex, x0, x1, base):
    split = x0 + (x1 - x0) * 0.62
    cv.poly([apex, (x0, base), (split, base)], fill=hexc("#ecc681"))
    cv.poly([apex, (split, base), (x1, base)], fill=hexc("#b9874a"))
    for k in range(1, 9):     # stone courses
        y = apex[1] + (base - apex[1]) * k / 9
        f = (y - apex[1]) / (base - apex[1])
        xl, xr = apex[0] + (x0 - apex[0]) * f, apex[0] + (x1 - apex[0]) * f
        xs = apex[0] + (split - apex[0]) * f
        cv.line([(xl, y), (xs, y)], hexc("#d8ad68"), 2, cap=False)
        cv.line([(xs, y), (xr, y)], hexc("#a6763d"), 2, cap=False)
    cv.poly([apex, (apex[0] - (apex[0] - x0) * 0.08, apex[1] + (base - apex[1]) * 0.08),
             (apex[0] + (x1 - apex[0]) * 0.08, apex[1] + (base - apex[1]) * 0.08)], fill=hexc(GOLD))   # golden capstone


def draw_sphinx(cv):
    OL = hexc("#6e4524")
    BODY, BODY_D, BODY_L = hexc("#c4823f"), hexc("#a3672f"), hexc("#d99a55")
    # plinth
    cv.rect(-80, 1240, 680, 1336, fill=hexc("#b98447"), outline=OL, width=4)
    for x in range(-80, 680, 95):
        cv.rect(x, 1240, x + 4, 1336, fill=hexc("#94622f"))
    cv.rect(-80, 1286, 680, 1291, fill=hexc("#94622f"))
    cv.rect(-95, 1226, 695, 1246, fill=hexc("#d9a866"), outline=OL, width=4)
    # lion body in profile (facing right)
    cv.line([(-30, 1190), (-110, 1150), (-120, 1100), (-95, 1080)], OL, 26)          # tail
    cv.line([(-30, 1190), (-110, 1150), (-120, 1100), (-95, 1080)], BODY_D, 16)
    cv.ellipse(-70, 1070, 260, 1232, fill=BODY, outline=OL, width=4)                 # haunch
    cv.rect(40, 1095, 480, 1230, fill=BODY, outline=OL, width=4, r=50)               # back + belly
    cv.ellipse(-60, 1120, 200, 1232, fill=BODY_D, outline=OL, width=4)               # folded hind leg
    cv.rect(60, 1196, 250, 1230, fill=BODY_D, outline=OL, width=4, r=16)             # hind paw
    cv.rect(70, 1102, 400, 1118, fill=BODY_L, r=8)                                   # light on the back
    for k in range(4):                                                               # ribs/muscle lines
        cv.arc(180 + k * 50, 1120, 230 + k * 50, 1200, 200, 300, OL, 3)
    cv.rect(360, 1040, 540, 1230, fill=BODY, outline=OL, width=4, r=40)              # chest
    for k, dy in enumerate((0, 20)):                                                 # stretched front legs
        x1 = 690 - k * 26
        cv.rect(420 - k * 20, 1180 + dy, x1, 1214 + dy, fill=BODY_D if k == 0 else BODY, outline=OL, width=4, r=16)
        for j in range(3):
            cv.line([(x1 - 34 + j * 11, 1186 + dy), (x1 - 34 + j * 11, 1208 + dy)], OL, 3, cap=False)
    # nemes headdress: dome + lappets down to the shoulders, gold/blue stripes
    hx, hy = 470, 985
    cv.poly([(hx - 74, hy - 70), (hx + 74, hy - 70), (hx + 112, hy + 110), (hx + 112, hy + 150),
             (hx - 112, hy + 150), (hx - 112, hy + 110)], fill=hexc(GOLD), outline=OL, width=4)
    for k in range(7):                                                               # stripes on the lappets
        y = hy - 40 + k * 26
        f = (y - (hy - 70)) / 180
        xo = 74 + (112 - 74) * min(1, f)
        cv.line([(hx - xo + 4, y), (hx - 50, y)], hexc(LAPIS), 11, cap=False)
        cv.line([(hx + 50, y), (hx + xo - 4, y)], hexc(LAPIS), 11, cap=False)
    cv.pieslice(hx - 78, hy - 150, hx + 78, hy - 10, 180, 360, fill=hexc(GOLD))
    cv.arc(hx - 78, hy - 150, hx + 78, hy - 10, 180, 360, OL, 4)
    for k in range(1, 4):
        cv.arc(hx - 78 + k * 6, hy - 150 + k * 12, hx + 78 - k * 6, hy - 10, 200, 340, hexc(LAPIS), 9)
    # face
    cv.ellipse(hx - 54, hy - 84, hx + 54, hy + 66, fill=hexc("#dca765"), outline=OL, width=4)
    cv.rect(hx - 64, hy - 88, hx + 64, hy - 72, fill=hexc(LAPIS), outline=OL, width=3, r=6)   # headband
    cv.poly([(hx - 7, hy - 104), (hx + 7, hy - 104), (hx + 10, hy - 76), (hx - 10, hy - 76)], fill=hexc(GOLD),
            outline=OL, width=3)                                                                 # uraeus
    cv.circle(hx, hy - 108, 8, fill=hexc(GOLD), outline=OL, width=3)
    for ex in (hx - 23, hx + 23):
        cv.line([(ex - 17, hy - 30), (ex + 15, hy - 33)], hexc("#3a2a1e"), 6)            # brows
        cv.ellipse(ex - 14, hy - 20, ex + 14, hy - 5, fill=hexc("#ffffff"))
        cv.circle(ex + 1, hy - 12, 6, fill=hexc("#22243a"))
        tail = ex + 24 if ex > hx else ex - 24
        cv.line([(ex - 14 if ex > hx else ex + 14, hy - 12), (tail, hy - 16)], hexc("#22243a"), 4, cap=False)  # kohl
    cv.poly([(hx - 6, hy - 6), (hx + 6, hy - 6), (hx + 12, hy + 20), (hx - 12, hy + 20)], fill=hexc("#c58f4f"))
    cv.ellipse(hx - 20, hy + 30, hx + 20, hy + 42, fill=hexc("#9c5634"))
    # ceremonial beard
    cv.rect(hx - 13, hy + 62, hx + 13, hy + 118, fill=hexc(GOLD), outline=OL, width=3, r=6)
    for k in range(4):
        cv.rect(hx - 11, hy + 70 + k * 12, hx + 11, hy + 75 + k * 12, fill=hexc(LAPIS))


def draw_column(cv, x, top, bottom, w=110):
    cv.rect(x - w / 2, top + 60, x + w / 2, bottom, fill=hexc("#e2c08a"))
    cv.rect(x - w / 2, top + 60, x - w / 2 + 18, bottom, fill=hexc("#c9a36a"))
    cv.poly([(x - w * 0.75, top + 60), (x + w * 0.75, top + 60), (x + w * 0.55, top), (x - w * 0.55, top)], fill=hexc("#cfa35e"))
    for k in range(3):                       # painted bands
        y = top + 120 + k * 22
        cv.rect(x - w / 2, y, x + w / 2, y + 10, fill=hexc([LAPIS, "#c0392b", GOLD][k]))
    rng = np.random.default_rng(abs(int(x)))
    for r in range(8):                       # hieroglyphs
        y = top + 210 + r * 70
        kind = int(rng.integers(0, 4))
        cx = x + (r % 2) * 10 - 5
        col = hexc("#6b4a28")
        if kind == 0:
            cv.ellipse(cx - 16, y - 10, cx + 16, y + 10, outline=col, width=4)
            cv.circle(cx, y, 4, fill=col)
        elif kind == 1:
            cv.line([(cx - 16, y + 10), (cx, y - 14), (cx + 16, y + 10)], col, 4)
        elif kind == 2:
            cv.line([(cx - 14, y), (cx + 14, y)], col, 4)
            cv.line([(cx, y - 14), (cx, y + 14)], col, 4)
        else:
            cv.circle(cx, y - 6, 8, outline=col, width=4)
            cv.line([(cx, y + 2), (cx, y + 16)], col, 4)
    cv.rect(x - w * 0.6, bottom - 20, x + w * 0.6, bottom, fill=hexc("#c9a36a"))


def draw_world():
    """landscape without the sky (transparent sky, drawn per frame by time of day)"""
    img = Image.new("RGBA", (int((WX1 - WX0) * ZW), int((WY1 - WY0) * ZW)), (0, 0, 0, 0))
    cv = Canvas(img, WX0, WY0, ZW)
    rng = np.random.default_rng(6)
    # far dunes
    pts = [(x, HORIZON - 30 - 30 * math.sin(x / 210) - 14 * math.sin(x / 70)) for x in range(WX0, WX1 + 20, 20)]
    cv.poly(pts + [(WX1, HORIZON + 80), (WX0, HORIZON + 80)], fill=hexc("#dba862"))
    # pyramids
    draw_pyramid(cv, (1230, 860), 1100, 1360, HORIZON)
    draw_pyramid(cv, (1010, 760), 820, 1200, HORIZON)
    draw_pyramid(cv, (640, 590), 290, 990, HORIZON)
    # ground
    cv.rect(WX0, HORIZON, WX1, WY1, fill=hexc(SAND))
    for k in range(6):
        y = HORIZON + 40 + k * 70
        pts = [(x, y + 16 * math.sin(x / (120 + k * 30) + k)) for x in range(WX0, WX1 + 20, 20)]
        cv.line(pts, hexc("#d6a159"), 6, cap=False)
    # Nile with reeds and palms
    cv.poly([(WX0, HORIZON + 30), (760, HORIZON + 34), (820, HORIZON + 62), (WX0, HORIZON + 70)], fill=hexc("#3f87c2"))
    for _ in range(25):
        x = rng.uniform(WX0, 760)
        cv.rect(x, HORIZON + 44 + rng.uniform(0, 14), x + rng.uniform(20, 60), HORIZON + 47 + rng.uniform(0, 14),
                fill=(255, 255, 255, 110))
    # obelisk
    cv.poly([(985, 1180), (1015, 1180), (1010, 900), (990, 900)], fill=hexc("#e2bd7c"))
    cv.poly([(990, 900), (1010, 900), (1000, 870)], fill=hexc(GOLD))
    cv.poly([(1000, 1180), (1015, 1180), (1010, 900), (1000, 900)], fill=hexc("#c49a5c"))
    back = img
    img = Image.new("RGBA", back.size, (0, 0, 0, 0))
    cv = Canvas(img, WX0, WY0, ZW)
    # temple columns at the far sides (visible in the wide shot)
    for x in (-120, 1200):
        draw_column(cv, x, 300, 1500, 130)
    cv.rect(-270, 270, 10, 310, fill=hexc("#cfa35e"))
    cv.rect(1070, 270, 1350, 310, fill=hexc("#cfa35e"))
    # sphinx
    draw_sphinx(cv)
    # foreground: path, stones, scattered rocks
    pts = [(x, PATH_Y - 30 + 10 * math.sin(x / 160)) for x in range(WX0, WX1 + 20, 20)]
    cv.poly(pts + [(WX1, PATH_Y + 60), (WX0, PATH_Y + 60)], fill=hexc(SAND_L))
    for x in range(-240, 1340, 110):
        cv.ellipse(x, PATH_Y + 40 + (x % 3) * 6, x + 80, PATH_Y + 66 + (x % 3) * 6, fill=hexc("#e5be7c"))
    for _ in range(40):
        x, y = rng.uniform(WX0, WX1), rng.uniform(PATH_Y + 90, WY1 - 40)
        r = rng.uniform(8, 26)
        cv.ellipse(x - r, y - r * 0.6, x + r, y + r * 0.6, fill=hexc("#c48a45"))
        cv.ellipse(x - r * 0.7, y - r * 0.6, x + r * 0.5, y + r * 0.1, fill=hexc("#d9a35e"))
    # stone tablet with hieroglyphs (foreground right)
    cv.rect(1060, 1560, 1250, 1840, fill=hexc("#cfa35e"), r=20)
    for r_ in range(4):
        for c_ in range(3):
            x, y = 1095 + c_ * 55, 1610 + r_ * 55
            cv.circle(x, y, 10, outline=hexc("#6b4a28"), width=4)
    return back, img


_WORLD = None


def world():
    global _WORLD
    if _WORLD is None:
        p1, p2 = os.path.join(CACHE, "world_back.png"), os.path.join(CACHE, "world_front.png")
        if not os.path.exists(p2):
            bk, fr = draw_world()
            bk.save(p1)
            fr.save(p2)
        _WORLD = (Image.open(p1).convert("RGBA"), Image.open(p2).convert("RGBA"))
    return _WORLD


def render_world_frame(cam, actors, pal, t):
    """cam=(cx, cy, viewH); pal=(stops, sun, tint) for the current time of day"""
    cx, cy, vh = cam
    vh = min(vh, WY1 - WY0)
    vw = vh * OUT_W / OUT_H
    cx = clamp(cx, WX0 + vw / 2, WX1 - vw / 2)
    cy = clamp(cy, WY0 + vh / 2, WY1 - vh / 2)
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    pb = (int(round((box[0] - WX0) * ZW)), int(round((box[1] - WY0) * ZW)),
          int(round((box[2] - WX0) * ZW)), int(round((box[3] - WY0) * ZW)))
    stops, sun, tint = pal
    # sky: gradient from the top of the world to the horizon
    sky_h = int((HORIZON - WY0) * ZW)
    g = _grad(1, sky_h, [(0, stops[0]), (0.55, stops[1]), (1.0, stops[2])])
    col = np.asarray(g)[:, 0, :]
    rows = np.clip(np.arange(pb[1], pb[3]), 0, sky_h - 1)
    sky = np.repeat(col[rows][:, None, :], pb[2] - pb[0], axis=1)
    crop = Image.fromarray(sky.astype(np.uint8), "RGB")
    cv = Canvas(crop, box[0], box[1], ZW)
    sky_actors(cv, t, sun)
    back, front = world()
    land = back.crop(pb)
    crop.paste(land, (0, 0), land)
    cv = Canvas(crop, box[0], box[1], ZW)
    back_actors(cv, t)
    land = front.crop(pb)
    crop.paste(land, (0, 0), land)
    if tint[3] > 0:
        ov = Image.new("RGB", crop.size, tint[:3])
        crop = Image.blend(crop, ov, tint[3] / 255)
        cv = Canvas(crop, box[0], box[1], ZW)
    actors(cv)
    return crop.resize((OUT_W, OUT_H), Image.LANCZOS), (box, vh / OUT_H)


def w2s(x, y, view):
    box, k = view
    return (x - box[0]) / k, (y - box[1]) / k


FULL = (W / 2, H / 2, H)
BIG = (540, 1080, 2300)
CAM_SPHINX = (430, 1080, 1250)
CAM_FACE = (470, 1000, 900)
CAM_PATH = (520, 1180, 1350)


# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["WARTE", "Im alten", "Wer vorbei", "Was geht", "PAUSE", "Kleiner Tipp", "Schreib deine", "Hier kommt",
        "Es ist der", "Am Morgen", "Am Mittag", "Und am Abend", "Hättest", "Schreib's"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 2.4
XFADE = 0.25


def st(key):
    return S[K[key]]


def en(key):
    return E[K[key]]


def word_time(key, word, frac=0.5):
    seg = next(x for x in TIM if x["text"].startswith(key))
    i = seg["text"].find(word)
    f = (i + len(word) * frac) / len(seg["text"])
    return seg["start"] + (seg["end"] - seg["start"]) * f


T_MORNING = word_time("Was geht", "Morgen", 0.2)
T_NOON = word_time("Was geht", "Mittag", 0.2)
T_EVENING = word_time("Was geht", "Abend", 0.2)


def palette_at(t):
    keys = [(0.0, "golden"), (T_MORNING - 0.3, "golden"), (T_MORNING + 0.3, "morning"), (T_NOON - 0.3, "morning"),
            (T_NOON + 0.3, "noon"), (T_EVENING - 0.3, "noon"), (T_EVENING + 0.3, "evening"), (st("PAUSE"), "evening"),
            (st("Hier kommt"), "golden"), (st("Am Morgen") - 0.2, "golden"), (st("Am Morgen") + 0.4, "morning"),
            (st("Am Mittag") - 0.2, "morning"), (st("Am Mittag") + 0.4, "noon"), (st("Und am Abend") - 0.2, "noon"),
            (st("Und am Abend") + 0.4, "evening"), (st("Hättest") - 0.1, "evening"), (st("Hättest") + 0.4, "golden")]
    if t <= keys[0][0]:
        return _pal_mix(keys[0][1], keys[0][1], 0)
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t <= t1:
            return _pal_mix(a, b, smooth(prog(t, t0, t1)))
    return _pal_mix(keys[-1][1], keys[-1][1], 0)


def sun_pos(t):
    """sun travels with the time of day (morning low left, noon high, evening low right)"""
    if st("Was geht") <= t < st("PAUSE") + 0.3:
        tt = prog(t, T_MORNING - 0.3, T_EVENING + 0.3)
    elif st("Am Morgen") - 0.3 <= t < st("Hättest"):
        tt = prog(t, st("Am Morgen") - 0.2, st("Und am Abend") + 0.4)
    else:
        return (900, 760)
    x = 80 + 900 * tt
    y = 980 - 700 * math.sin(math.pi * tt)
    return (x, y)


# ------------------------------------------------------------------ animated details
def sky_actors(cv, t, sun):
    sx, sy = sun_pos(t)
    for k in range(5, 0, -1):
        cv.circle(sx, sy, 60 + k * 26, fill=sun + (14,))
    cv.circle(sx, sy, 62, fill=sun)
    for i, (cx, cy, s) in enumerate(((150, 260, 0.8), (700, 420, 0.6), (1100, 200, 0.7))):   # drifting clouds
        x = (cx + t * 12 * (1 + i * 0.3)) % 1900 - 400
        col = (255, 245, 235, 150)
        cv.rect(x - 160 * s, cy - 24 * s, x + 160 * s, cy + 24 * s, fill=col, r=24 * s)
        cv.rect(x - 80 * s, cy - 60 * s, x + 70 * s, cy + 10 * s, fill=col, r=36 * s)
    for i in range(3):                                                                     # ibis birds
        x = (i * 380 + t * 55) % 1800 - 300
        y = 520 + i * 60 + 12 * math.sin(t * 1.5 + i)
        w = 14 * math.sin(t * 9 + i)
        cv.line([(x - 18, y - w), (x, y), (x + 18, y - w)], hexc("#2b2140"), 4)


def back_actors(cv, t):
    # camel caravan along the far dunes
    for i in range(4):
        x = 1300 - ((t * 22 + i * 60) % 1700)
        y = HORIZON - 34 + 3 * math.sin(t * 4 + i)
        col = hexc("#8a5a36")
        cv.ellipse(x - 26, y - 34, x + 26, y - 8, fill=col)
        cv.circle(x - 6, y - 36, 12, fill=col)
        cv.line([(x - 24, y - 22), (x - 40, y - 46), (x - 46, y - 44)], col, 7)
        for lx in (x - 16, x - 4, x + 8, x + 18):
            cv.line([(lx, y - 10), (lx + 3 * math.sin(t * 6 + lx), y + 12)], col, 4)
    # palms by the Nile (swaying)
    for px, hgt in ((80, 210), (170, 170), (700, 190), (770, 150)):
        base = HORIZON + 40
        top = (px + 10 * math.sin(t * 1.3 + px), base - hgt)
        cv.line([(px, base), (px + 4, base - hgt * 0.5), top], hexc("#7a4f2e"), 10)
        for a in range(6):
            ang = math.pi + a * math.pi / 5 + 0.08 * math.sin(t * 2 + a)
            cv.line([top, (top[0] + math.cos(ang) * 90, top[1] + math.sin(ang) * 40 + 30)], hexc("#3f8a4c"), 12)


def ground_actors(cv, t):
    # blowing sand
    for i in range(30):
        x = (i * 97 + t * 160) % 1700 - 300
        y = PATH_Y - 60 + (i * 53) % 260 + 8 * math.sin(t * 3 + i)
        cv.circle(x, y, 2.5, fill=(255, 235, 190, 150))


def sphinx_eyes(cv, glow, t):
    if glow <= 0.01:
        return
    hx, hy = 470, 985
    p = 0.75 + 0.25 * math.sin(t * 8)
    for ex in (hx - 22, hx + 22):
        for k in range(4, 0, -1):
            cv.circle(ex + 2, hy - 11, (8 + k * 9) * p, fill=(255, 220, 90, int(45 * glow)))
        cv.ellipse(ex - 13, hy - 18, ex + 13, hy - 4, fill=(255, 236, 140, int(255 * glow)))


# ------------------------------------------------------------------ overlays
def karaoke_pills(frame, t, lines, seg_key, cy0, dy, max_w=660, shake_words=()):
    """whole sentence visible from frame 0; the spoken word pops, turns red and glows"""
    t0, t1 = S[K[seg_key]], E[K[seg_key]]
    words = [w for line, _, _, _ in lines for w in line]
    weights = [len(w) + 2 for w in words]
    tot = sum(weights)
    spans, acc = [], t0 + 0.02
    for wgt in weights:
        d_ = (t1 - t0 - 0.06) * wgt / tot
        spans.append((acc, acc + d_))
        acc += d_
    fade = 1 - prog(t, t1 + 0.15, t1 + 0.5)
    if fade <= 0.01:
        return
    i = 0
    for li, (line, bg, fg, rot) in enumerate(lines):
        base = 92 if li else 120
        gap = 0.28 * base
        while sum(font(base).getbbox(w)[2] for w in line) + gap * (len(line) - 1) > max_w - 90:
            base -= 2
            gap = 0.28 * base
        pops = []
        for j in range(len(line)):
            a_, b_ = spans[i + j]
            p = prog(t, a_ - 0.03, b_ + 0.08)
            pops.append(math.sin(math.pi * p) if 0 < p < 1 else 0.0)
        sizes = [base * (1 + 0.3 * pp) for pp in pops]
        widths = [font(int(sz)).getbbox(w)[2] for sz, w in zip(sizes, line)]
        tw = sum(widths) + gap * (len(line) - 1)
        if tw > max_w - 70:
            k = (max_w - 70) / tw
            sizes = [sz * k if pp > 0 else sz for sz, pp in zip(sizes, pops)]
            widths = [font(int(sz)).getbbox(w)[2] for sz, w in zip(sizes, line)]
            tw = sum(widths) + gap * (len(line) - 1)
        padx, pady, Z = 34, 20, 2
        x0, y0 = 40, 40
        x1, y1 = x0 + tw + 2 * padx, y0 + base + 2 * pady
        PW, PH = int(x1 + 50), int(y1 + 60)
        tile = Image.new("RGBA", (PW * Z, PH * Z), (0, 0, 0, 0))
        d = ImageDraw.Draw(tile)
        d.rounded_rectangle([(x0 + 8) * Z, (y0 + 12) * Z, (x1 + 8) * Z, (y1 + 12) * Z], radius=int((y1 - y0) / 3 * Z),
                            fill=(30, 20, 60, 110))
        d.rounded_rectangle([x0 * Z, y0 * Z, x1 * Z, y1 * Z], radius=int((y1 - y0) / 3 * Z), fill=hexc(bg),
                            outline=hexc("#1d1b33"), width=5 * Z)
        x = x0 + padx
        for j, w in enumerate(line):
            cxw, cyw = (x + widths[j] / 2) * Z, (y0 + (y1 - y0) / 2) * Z
            if pops[j] > 0.05:      # highlighter box behind the spoken word
                hl = {"#e2574c": (120, 16, 16), "#ffd34d": (255, 255, 255)}.get(bg, (255, 211, 77))
                hw, hh = widths[j] / 2 + 12, sizes[j] * 0.62
                k_ = min(1, pops[j] * 1.6)
                hl = tuple(int(c0 + (c1 - c0) * k_) for c0, c1 in zip(hexc(bg), hl))
                d.rounded_rectangle([cxw - hw * Z, cyw - hh * Z, cxw + hw * Z, cyw + hh * Z], radius=int(14 * Z),
                                    fill=hl)
            col = hexc("#d62828") if pops[j] > 0.3 and bg != "#e2574c" else hexc(fg)
            if pops[j] > 0.3 and bg == "#e2574c":
                col = hexc("#ffe46b")
            d.text((cxw, cyw), w, font=font(int(sizes[j] * Z)), fill=col, anchor="mm",
                   stroke_width=int(2 * Z * pops[j]), stroke_fill=hexc("#1d1b33"))
            x += widths[j] + gap
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
        tile = tile.resize((max(1, tile.width // Z), max(1, tile.height // Z)), Image.LANCZOS)
        if fade < 1:
            tile.putalpha(tile.split()[3].point(lambda v: int(v * fade)))
        shake = 0
        if any(w in shake_words for w in line) and pops[0] > 0.05:
            shake = 10 * math.sin(t * 75) * pops[0]
        cy = cy0 + li * dy
        px = int(OUT_W / 2 - tile.width / 2 + shake)
        py = int(cy - tile.height / 2)
        frame.paste(tile, (px, py), tile)
        log_ui("karaoke " + str(li), px + 40, py + 40, px + tile.width - 40, py + tile.height - 40)
        i += len(line)


INTRO_LINES = [(["WARTE!"], "#e2574c", "#ffffff", -3), (["DIESES", "RÄTSEL", "KANN"], "#fff6e6", "#2b2140", 2),
               (["NIEMAND", "LÖSEN!"], "#ffd34d", "#2b2140", -2)]


def legs_pill(frame, t, ts, y, label, n, bg):
    sc = ease_out_back(prog(t, ts, ts + 0.3))
    pill(frame, OUT_W / 2, y, f"{label}:  {n} BEINE", 54, bg=bg, scale=sc, rot=(-2 if n != 2 else 2),
         border="#1d1b33")


# ------------------------------------------------------------------ scenes
def scene_story(t):
    t0, t1, t2, t3 = st("WARTE"), st("Im alten"), st("Wer vorbei"), st("Was geht")
    t_end = st("PAUSE")
    cam = keyframes(t, [(t0, BIG), (t1 - 0.1, BIG), (t1 + 1.6, CAM_SPHINX), (t2 - 0.1, CAM_SPHINX),
                        (t2 + 1.0, (450, 1030, 1050)), (t3, (450, 1030, 1050)), (t3 + 0.8, CAM_FACE)])
    glow = smooth(prog(t, t3 - 0.2, t3 + 0.4))
    pal = palette_at(t)

    def actors(cv):
        ground_actors(cv, t)
        sphinx_eyes(cv, glow, t)

    frame, view = render_world_frame(cam, actors, pal, t)
    if t < t1 + 0.6:       # darken behind the opening text
        dark = 0.38 * (1 - prog(t, t1, t1 + 0.6))
        frame = Image.blend(frame, Image.new("RGB", frame.size, (15, 10, 30)), dark)
        if t < 0.18:       # impact flash on "WARTE!"
            frame = Image.blend(frame, Image.new("RGB", frame.size, (255, 250, 230)), 0.35 * (1 - t / 0.18))
    karaoke_pills(frame, t, INTRO_LINES, "WARTE", 760, 175, shake_words=("WARTE!",))
    if t1 + 0.3 <= t < t2 + 0.2:
        pill(frame, OUT_W / 2, 330, "ALTES ÄGYPTEN", 64, bg="#ffd34d", rot=-2, border="#1d1b33",
             scale=ease_out_back(prog(t, t1 + 0.3, t1 + 0.65)))
        sx, sy = w2s(470, 830, view)
        pill(frame, clamp(sx, 200, 820), max(sy, 470), "DIE SPHINX", 48, bg="#fff6e6", border="#1d1b33",
             scale=ease_out_back(prog(t, t1 + 1.2, t1 + 1.5)))
    if t2 <= t < t3:
        pill(frame, OUT_W / 2, 330, "NUR WER DAS RÄTSEL LÖST,", 46, bg="#fff6e6", border="#1d1b33", rot=-2,
             scale=ease_out_back(prog(t, t2, t2 + 0.3)))
        pill(frame, OUT_W / 2, 440, "DARF VORBEI", 64, bg="#e2574c", fg="#ffffff", border="#1d1b33", rot=2,
             scale=ease_out_back(prog(t, t2 + 0.25, t2 + 0.55)))
    if t3 <= t:
        legs_pill(frame, t, T_MORNING - 0.1, 1180, "MORGEN", 4, "#ffd9a0")
        legs_pill(frame, t, T_NOON - 0.1, 1300, "MITTAG", 2, "#fff6e6")
        legs_pill(frame, t, T_EVENING - 0.1, 1420, "ABEND", 3, "#f4aab0")
        pill(frame, OUT_W / 2, 330, "WAS IST DAS?", 70, bg="#ffd34d", border="#1d1b33", rot=-2,
             scale=ease_out_back(prog(t, t3, t3 + 0.35)))
    return frame


Q_Y = 860


def sun_icon(cv, x, y, kind, s=1.0):
    if kind == "moon":
        cv.circle(x, y, 34 * s, fill=hexc("#ffe3a0"))
        cv.circle(x + 14 * s, y - 10 * s, 30 * s, fill=hexc("#1c2b4f"))
        return
    col = hexc("#ffd34d") if kind == "sun" else hexc("#ffb36b")
    for i in range(10):
        a = i / 10 * 2 * math.pi
        cv.line([(x + math.cos(a) * 42 * s, y + math.sin(a) * 42 * s), (x + math.cos(a) * 56 * s, y + math.sin(a) * 56 * s)],
                col, 6 * s)
    cv.circle(x, y, 32 * s, fill=col)
    if kind == "rise":
        cv.rect(x - 70 * s, y + 4 * s, x + 70 * s, y + 70 * s, fill=hexc("#1c2b4f"))


def scene_question(t):
    t0, t_pause, t_tip, t_cm = st("Was geht"), st("PAUSE"), st("Kleiner Tipp"), st("Schreib deine")
    img = vgradient(OUT_W, OUT_H, [(0, "#14213d"), (1, "#2b3f74")])
    cv = Canvas(img)
    rng = np.random.default_rng(1)
    for _ in range(70):
        x, y = rng.uniform(0, OUT_W), rng.uniform(0, OUT_H)
        tw = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv.circle(x, y, 2 + 2 * tw, fill=(255, 255, 255, int(80 + 100 * tw)))
    for k, (kind, lab, n) in enumerate((("rise", "MORGEN", 4), ("sun", "MITTAG", 2), ("moon", "ABEND", 3))):
        x = 230 + k * 300
        sun_icon(cv, x, Q_Y + 60, kind, 1.2)
        pill(img, x, Q_Y + 190, lab, 40, bg="#fff6e6", pad=(18, 9))
        pill(img, x, Q_Y + 300, str(n), 96, bg="#ffd34d", pad=(30, 8), rot=(-4, 3, -3)[k])
    pill(img, OUT_W / 2, 360, "WAS GEHT AUF", 84, bg="#fff6e6", rot=-3, scale=ease_out_back(prog(t, t0, t0 + 0.35)))
    pill(img, OUT_W / 2, 510, "4, 2 UND 3 BEINEN?", 76, bg="#ffd34d", rot=2,
         scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)))
    if t_pause - 0.2 < t < t_tip:
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            cv.circle(OUT_W / 2 - 70 + i * 70, 700, 18 + 10 * a, fill=(255, 255, 255, int(120 + 135 * a)))
    if t > t_tip:
        pill(img, OUT_W / 2, 680, "TIPP: EIN GANZES LEBEN", 56, bg="#c5def5", rot=-2,
             scale=ease_out_back(prog(t, t_tip, t_tip + 0.35)))
    if t > t_cm:
        pill(img, OUT_W / 2, 1420, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff",
             scale=ease_out_back(prog(t, t_cm, t_cm + 0.35)))
    return img


def scene_solution(t):
    t0, tm, a1, a2, a3, t_end = st("Hier kommt"), st("Es ist der"), st("Am Morgen"), st("Am Mittag"), \
        st("Und am Abend"), st("Hättest")
    cam = keyframes(t, [(t0, FULL), (tm, FULL), (a1, CAM_PATH)])
    pal = palette_at(t)

    def actors(cv):
        ground_actors(cv, t)
        if tm <= t < a1:      # the human, standing proud
            draw_person(cv, 760, PATH_Y, ADULT, face=-1, h=300, wave=t * 8, blink=(t % 3) < 0.12)
        if a1 <= t < a2 + 0.2:
            p = prog(t, a1, a2)
            draw_baby(cv, 150 + 640 * p, PATH_Y, 1.6, phase=t * 9)
        if a2 <= t < a3 + 0.2:
            p = prog(t, a2, a3)
            draw_person(cv, 150 + 700 * p, PATH_Y, ADULT, face=1, h=300, phase=t * 10, blink=(t % 3) < 0.12)
        if a3 <= t < t_end + 0.3:
            p = prog(t, a3, t_end)
            x = 150 + 520 * p
            hand = draw_person(cv, x, PATH_Y, OLD, face=1, h=285, lean=16, phase=t * 6,
                               reach=(x + 70, PATH_Y - 120))
            draw_cane(cv, hand, (x + 82 + 6 * math.sin(t * 6), PATH_Y))

    frame, view = render_world_frame(cam, actors, pal, t)
    if t < t0 + 1.3:
        pill(frame, OUT_W / 2, 330, "DIE LÖSUNG", 96, bg="#fff6e6", rot=-4, border="#1d1b33",
             scale=ease_out_back(prog(t, t0, t0 + 0.35)) * (1 - prog(t, t0 + 1.0, t0 + 1.3)))
    if tm <= t < a1:
        pill(frame, OUT_W / 2, 400, "DER MENSCH!", 110, bg="#37b26c", fg="#ffffff", border="#1d1b33", rot=-3,
             scale=ease_out_back(prog(t, tm, tm + 0.35)))
    for (ta, tb, lab, sub, bg) in ((a1, a2, "MORGEN = BABY", "4 BEINE", "#ffd9a0"),
                                   (a2, a3, "MITTAG = ERWACHSEN", "2 BEINE", "#fff6e6"),
                                   (a3, t_end, "ABEND = IM ALTER", "2 BEINE + STOCK = 3", "#f4aab0")):
        if ta <= t < tb:
            pill(frame, OUT_W / 2, 330, lab, 60, bg=bg, border="#1d1b33", rot=-2, scale=ease_out_back(prog(t, ta, ta + 0.3)))
            pill(frame, OUT_W / 2, 450, sub, 70, bg="#ffd34d", border="#1d1b33", rot=2,
                 scale=ease_out_back(prog(t, ta + 0.35, ta + 0.65)))
    return frame


def scene_outro(t):
    t0, t1 = st("Hättest"), st("Schreib's")
    pal = palette_at(t)

    def actors(cv):
        ground_actors(cv, t)
        draw_baby(cv, 230, PATH_Y, 1.5, phase=t * 6)
        draw_person(cv, 520, PATH_Y, ADULT, face=1, h=300, wave=t * 8)
        hand = draw_person(cv, 790, PATH_Y, OLD, face=-1, h=285, lean=-16, reach=(730, PATH_Y - 120))
        draw_cane(cv, hand, (718, PATH_Y))

    img, _ = render_world_frame(FULL, actors, pal, t)
    img = ImageEnhance.Brightness(img).enhance(0.6)
    pill(img, OUT_W / 2, 520, "HÄTTEST DU'S", 96, bg="#fff6e6", rot=-3, border="#1d1b33",
         scale=ease_out_back(prog(t, t0, t0 + 0.35)))
    pill(img, OUT_W / 2, 690, "GEWUSST?", 110, bg="#ffd34d", rot=2, border="#1d1b33",
         scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)))
    if t > t1:
        pill(img, OUT_W / 2, 840, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff", border="#1d1b33",
             scale=ease_out_back(prog(t, t1, t1 + 0.35)))
        followed = t > t1 + 2.0
        txt = "GEFOLGT  ✓" if followed else "+  FOLGEN"
        bg = "#37b26c" if followed else "#e2574c"
        pulse = 1 + (0.06 * math.sin(t * 10) if not followed else 0)
        pill(img, OUT_W / 2, 965, txt, 72, bg=bg, fg="#ffffff", border="#ffffff",
             scale=ease_out_back(prog(t, t1 + 0.4, t1 + 0.75)) * pulse)
        pill(img, OUT_W / 2, 1085, "MORGEN: NEUES RÄTSEL", 48, bg="#fff6e6", border="#1d1b33",
             scale=ease_out_back(prog(t, t1 + 1.0, t1 + 1.35)))
    return img


SCENES = [
    (0.0, scene_story),
    (st("PAUSE") - 0.05, scene_question),
    (st("Hier kommt") - 0.05, scene_solution),
    (st("Hättest") - 0.05, scene_outro),
]


def frame_at(t):
    idx = max(i for i, (s0, _) in enumerate(SCENES) if t >= s0)
    img = SCENES[idx][1](t)
    if idx > 0:
        s0 = SCENES[idx][0]
        if t < s0 + XFADE:
            prev = SCENES[idx - 1][1](t)
            img = Image.blend(prev, img, smooth(prog(t, s0, s0 + XFADE)))
    if t > END - 0.6:
        img = Image.blend(img, Image.new("RGB", img.size, (20, 14, 36)), prog(t, END - 0.6, END))
    return img


def render_chunk(args):
    i0, i1, path = args
    world()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame_at(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return path


def render(out="video.mp4", workers=4):
    world()
    n = int(END * FPS)
    step = math.ceil(n / workers)
    chunks = [(i, min(n, i + step), os.path.join(CACHE, f"chunk{k}.mp4")) for k, i in enumerate(range(0, n, step))]
    with Pool(workers) as pool:
        paths = pool.map(render_chunk, chunks)
    lst = os.path.join(CACHE, "chunks.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in paths)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    os.path.join(CACHE, "silent.mp4")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(CACHE, "silent.mp4"),
                    "-i", os.path.join(HERE, "mix.wav"), "-c:v", "copy", "-af", "loudnorm=I=-14:LRA=11:TP=-1.5",
                    "-ar", "44100", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-shortest", os.path.join(HERE, out)], check=True)


if __name__ == "__main__":
    if "--stills" in sys.argv:
        os.makedirs(os.path.join(HERE, "stills"), exist_ok=True)
        for t in [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]]:
            frame_at(t).save(os.path.join(HERE, "stills", f"t{t:05.1f}.jpg"), quality=85)
    else:
        render()
