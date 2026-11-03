"""Rätsel #1 – Alex und der Aufzug.

usage:  python3 make_video.py            -> renders video.mp4 (needs voice.wav + timing.json)
        python3 make_video.py --stills   -> writes preview stills to ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# ------------------------------------------------------------------ world layout
W, H = 3600, 6600
FH = 400                    # floor height
GROUND = 6000               # street level (bottom of ground floor)
FLOORS = 12
SX = 1300                   # elevator shaft centre x
SHAFT = (1150, 1450)
STAIRS = (1450, 1750)
APT = (1750, 2700)
HORIZON = 3500
CAB_W, CAB_H = 240, 330
ALEX_DOOR_X = 1850
PASTELS = ["#f6c6c8", "#fbe3a2", "#d9cdf3", "#bfe8d6", "#fcd2b0", "#c5def5"]
DOORS = ["#e2574c", "#2f8f83", "#f0a03c", "#4a6fd1", "#8b5cc7", "#2f8f83"]


def yb(n):
    """y of the floor surface of floor n (0 = Erdgeschoss)."""
    return GROUND - n * FH


ALEX = Style(150, "#f1c19c", "#3b2418", "#e8a33a", "#2c3e66", shoes="#ffffff", hair_style="quiff",
             leg=0.31, torso=0.31, arm=0.30, width=0.17, accent="#2d2a3a", under="#ffffff",
             shoe_accent="#e2574c")
ELISA = Style(250, "#f6d2b8", "#e9b949", "#7d5bd0", "#2f3350", hair_style="long", under="#f3eefc", shoes="#2f3350")
PAUL = Style(258, "#8d5a3b", "#1f1a24", "#d9534a", "#46618f", hair_style="short", glasses=True, beard=True,
             shoes="#f2f2f2")


def sky(variant):
    if variant == "day":
        stops = [(0, "#4f9fe0"), (0.45, "#a9d4f2"), (0.62, "#e8f3fa"), (1, "#e8f3fa")]
    elif variant == "rain":
        stops = [(0, "#4b5160"), (0.55, "#8e95a3"), (1, "#9aa1ae")]
    else:  # blue hour
        stops = [(0, "#14213d"), (0.25, "#2b3f74"), (0.45, "#6a6aa8"), (0.56, "#f08a5d"), (0.62, "#ffc178"),
                 (1, "#ffc178")]
    return vgradient(W, H, stops)


ANTH, ANTH_L = "#2c2f38", "#454955"
WOOD, WOOD_D = "#b9804f", "#94603a"
WHITE, SLAB = "#f3f1ec", "#dcd8d0"


def glass_interior(cv, x0, y0, x1, y1, variant, rng):
    if variant == "day":
        top, bot = hexc("#cfe2ef"), hexc("#eaf2f8")
    elif variant == "rain":
        top, bot = hexc("#9fa8b4"), hexc("#c4cad2")
    else:
        top, bot = hexc("#ffd28f"), hexc("#f39b62")
    steps = 8
    for i in range(steps):
        cv.rect(x0, y0 + (y1 - y0) * i / steps, x1, y0 + (y1 - y0) * (i + 1) / steps + 1, fill=mix(top, bot, i / steps))
    sil = (40, 30, 50, 55) if variant != "day" else (60, 80, 100, 45)
    # furniture silhouettes: sofa / lamp / plant / shelf
    k = rng.integers(0, 3)
    if k == 0:
        cv.rect(x0 + 40, y1 - 90, x0 + 230, y1 - 20, fill=sil, r=18)
        cv.line([(x1 - 70, y1 - 20), (x1 - 70, y0 + 80)], sil, 6)
        cv.pieslice(x1 - 110, y0 + 50, x1 - 30, y0 + 120, 180, 360, fill=sil)
    elif k == 1:
        for j in range(3):
            cv.rect(x0 + 50, y0 + 70 + j * 60, x0 + 200, y0 + 78 + j * 60, fill=sil)
        cv.rect(x1 - 120, y1 - 70, x1 - 70, y1 - 20, fill=sil, r=6)
        for a in range(5):
            cv.circle(x1 - 95 + (a - 2) * 16, y1 - 95 - (a % 2) * 22, 24, fill=sil)
    else:
        cv.rect(x0 + 60, y1 - 110, x0 + 210, y1 - 95, fill=sil)
        cv.rect(x0 + 70, y1 - 95, x0 + 80, y1 - 20, fill=sil)
        cv.rect(x0 + 190, y1 - 95, x0 + 200, y1 - 20, fill=sil)
        cv.circle(x0 + 135, y0 + 60, 26, fill=(255, 255, 230, 120) if variant != "day" else sil)
    # reflection
    cv.poly([(x0 + 30, y1), (x0 + 120, y0), (x0 + 170, y0), (x0 + 80, y1)], fill=(255, 255, 255, 45))


def draw_world(variant):
    img = sky(variant)
    cv = Canvas(img)
    rng = np.random.default_rng(5)
    night = variant == "dusk"
    if variant == "day":
        cv.circle(3050, 1300, 150, fill=hexc("#fff7d6"))
    elif variant == "dusk":
        cv.circle(700, 3700, 230, fill=hexc("#ffe0a0"))
    # soft flat clouds
    for cx, cy, s in [(450, 1000, 1.1), (3100, 1700, 0.9), (650, 2500, 0.8), (3000, 2900, 1.0)]:
        col = (255, 255, 255, 200) if variant == "day" else (255, 214, 190, 90) if night else (110, 116, 130, 230)
        cv.rect(cx - 220 * s, cy - 30 * s, cx + 220 * s, cy + 30 * s, fill=col, r=30 * s)
        cv.rect(cx - 120 * s, cy - 75 * s, cx + 90 * s, cy + 10 * s, fill=col, r=45 * s)

    # ---- skyline: two layers of modern towers
    far = hexc("#8fb3d3") if variant == "day" else hexc("#46507e") if night else hexc("#6d7381")
    near = hexc("#5f86ad") if variant == "day" else hexc("#2a3157") if night else hexc("#545a68")
    for layer, col, base_top in ((0, far, 3000), (1, near, 3600)):
        x = -100 + layer * 120
        while x < W:
            w = rng.integers(170, 330)
            top = base_top + rng.integers(-700, 600)
            if 1050 < x + w and x < 2780:      # keep the area behind our tower clear
                x += w + 40
                continue
            cv.rect(x, top, x + w, GROUND, fill=col)
            if rng.random() < 0.4:  # stepped crown / antenna
                cv.rect(x + w * 0.25, top - 90, x + w * 0.75, top, fill=col)
                cv.rect(x + w * 0.48, top - 230, x + w * 0.52, top - 90, fill=col)
            wc = mix(col, (255, 255, 255), 0.18) if variant != "dusk" else None
            for wy in range(int(top) + 40, GROUND - 40, 70 if layer else 90):
                if night:
                    for wx in range(int(x) + 25, int(x + w) - 30, 48):
                        if rng.random() < 0.45:
                            cv.rect(wx, wy, wx + 26, wy + 34, fill=hexc("#ffd58a") if rng.random() < 0.7 else
                                    mix(col, (255, 255, 255), 0.2))
                else:
                    cv.rect(x + 20, wy, x + w - 20, wy + 10, fill=wc)
            x += w + rng.integers(20, 90)

    top_y = yb(FLOORS) - FH
    ink = hexc("#22243a")
    anth, anth_l = hexc(ANTH), hexc(ANTH_L)
    wood, wood_d = hexc(WOOD), hexc(WOOD_D)
    white, slab = hexc(WHITE), hexc(SLAB)

    # ---- stair core behind glass
    cv.rect(STAIRS[0], top_y, STAIRS[1], GROUND, fill=hexc("#e6e3dd"))
    for n in range(FLOORS):
        a = (STAIRS[0] + 20, yb(n))
        m = (STAIRS[1] - 20, yb(n) - FH / 2)
        b = (STAIRS[0] + 20, yb(n + 1))
        for p0, p1 in ((a, m), (m, b)):
            cv.poly([p0, p1, (p1[0], p1[1] + 34), (p0[0], p0[1] + 34)], fill=hexc("#c9c5bc"))
            steps = 10
            for s_ in range(steps):
                f0, f1 = s_ / steps, (s_ + 1) / steps
                x0_, y0_ = p0[0] + (p1[0] - p0[0]) * f0, p0[1] + (p1[1] - p0[1]) * f0
                x1_, y1_ = p0[0] + (p1[0] - p0[0]) * f1, p0[1] + (p1[1] - p0[1]) * f1
                cv.line([(x0_, y0_), (x0_, y1_), (x1_, y1_)], hexc("#b4afa5"), 5, cap=False)
            cv.line([(p0[0], p0[1] - 90), (p1[0], p1[1] - 90)], anth, 8)
            for k in range(7):
                ff = (k + 0.5) / 7
                px, py = p0[0] + (p1[0] - p0[0]) * ff, p0[1] + (p1[1] - p0[1]) * ff
                cv.line([(px, py - 90), (px, py)], anth_l, 3, cap=False)
        cv.rect(m[0] - 50, m[1], m[0] + 25, m[1] + 28, fill=hexc("#c9c5bc"))
    # curtain wall: mullions + reflections
    for k in range(STAIRS[0], STAIRS[1] + 1, 100):
        cv.rect(k - 5, top_y, k + 5, GROUND, fill=anth)
    cv.rect(STAIRS[0], top_y, STAIRS[1], GROUND, fill=(170, 205, 230, 38) if variant != "dusk" else (120, 140, 200, 30))
    for k in range(14):
        yy = top_y + k * 380
        cv.poly([(STAIRS[0], yy + 300), (STAIRS[0] + 120, yy), (STAIRS[0] + 170, yy), (STAIRS[0] + 50, yy + 300)],
                fill=(255, 255, 255, 40))

    # ---- apartments with exterior walkway
    for n in range(FLOORS + 1):
        y1, y0 = yb(n), yb(n) - FH
        if n == 0:
            cv.rect(APT[0], y0, APT[1], y1, fill=white)
            glass_interior(cv, APT[0] + 30, y0 + 140, APT[1] - 30, y1, variant, rng)
            for k in range(7):
                xx = APT[0] + 30 + k * (APT[1] - APT[0] - 60) / 6
                cv.rect(xx - 7, y0 + 140, xx + 7, y1, fill=anth)
            cv.rect(APT[0] + 30, y0 + 132, APT[1] - 30, y0 + 146, fill=anth)
            cv.rect(APT[0] - 40, y0 + 90, APT[1] + 40, y0 + 122, fill=wood)      # wooden canopy
            cv.rect(APT[0] - 40, y0 + 118, APT[1] + 40, y0 + 126, fill=wood_d)
            cv.rect(APT[0] + 40, y0 + 20, APT[0] + 120, y0 + 76, fill=anth, r=8)
            cv.text(APT[0] + 80, y0 + 49, "E", 40, hexc("#ffffff"))
            for px in (APT[0] + 360, APT[1] - 120):                           # planters with grasses
                cv.rect(px - 60, y1 - 70, px + 60, y1, fill=anth_l, r=6)
                for g in range(9):
                    cv.line([(px - 40 + g * 10, y1 - 70), (px - 55 + g * 14, y1 - 140 - (g % 3) * 15)],
                            hexc("#6f9a5a"), 6)
            continue
        cv.rect(APT[0], y0, APT[1], y1, fill=white)
        # wood cladding next to Alex's door
        cv.rect(APT[0], y0 + 26, APT[0] + 30, y1, fill=wood)
        # door A (Alex's)
        dcol = wood if n != FLOORS else hexc("#d9653b")
        cv.rect(ALEX_DOOR_X - 62, y1 - 300, ALEX_DOOR_X + 62, y1, fill=anth)
        cv.rect(ALEX_DOOR_X - 52, y1 - 290, ALEX_DOOR_X + 52, y1, fill=dcol)
        for g in range(4):
            cv.rect(ALEX_DOOR_X - 40 + g * 26, y1 - 280, ALEX_DOOR_X - 37 + g * 26, y1 - 10, fill=_dk(dcol))
        cv.rect(ALEX_DOOR_X + 30, y1 - 170, ALEX_DOOR_X + 36, y1 - 110, fill=hexc("#d8dbe0"))
        # floor plate
        cv.rect(APT[0] + 50, y0 + 40, APT[0] + 140, y0 + 100, fill=anth, r=10)
        cv.text(APT[0] + 95, y0 + 71, str(n), 40, hexc("#ffffff"))
        # big window
        wx0, wx1 = 1980, 2380
        cv.rect(wx0 - 10, y0 + 40, wx1 + 10, y1, fill=anth)
        glass_interior(cv, wx0, y0 + 50, wx1, y1, variant, rng)
        cv.rect((wx0 + wx1) / 2 - 5, y0 + 50, (wx0 + wx1) / 2 + 5, y1, fill=anth)
        # door B
        bx = 2470
        cv.rect(bx - 62, y1 - 300, bx + 62, y1, fill=anth)
        cv.rect(bx - 52, y1 - 290, bx + 52, y1, fill=hexc("#5d6270"))
        cv.rect(bx - 40, y1 - 280, bx + 40, y1 - 160, fill=(200, 220, 235, 120))
        # wood louvres at the end
        for k in range(8):
            cv.rect(2560 + k * 18, y0 + 26, 2570 + k * 18, y1, fill=wood if k % 2 == 0 else wood_d)
        # ceiling downlights
        for lx in (1920, 2430):
            cv.rect(lx - 18, y0 + 26, lx + 18, y0 + 34, fill=hexc("#fff3d0"))
        # frosted glass balustrade
        cv.rect(APT[0], y1 - 118, APT[1], y1, fill=(235, 242, 248, 85))
        cv.rect(APT[0], y1 - 124, APT[1], y1 - 116, fill=anth)
        for k in range(0, APT[1] - APT[0] + 1, 240):
            cv.rect(APT[0] + k - 3, y1 - 118, APT[0] + k + 3, y1, fill=anth_l)
    # ---- slabs
    for n in range(FLOORS + 1):
        cv.rect(SHAFT[0] - 20, yb(n), APT[1] + 30, yb(n) + 26, fill=white)
        cv.rect(SHAFT[0] - 20, yb(n) + 22, APT[1] + 30, yb(n) + 30, fill=slab)
    # ---- glass elevator shaft
    cv.rect(SHAFT[0], top_y - 260, SHAFT[1], GROUND, fill=(200, 225, 245, 45) if variant != "dusk" else
            (150, 170, 220, 40))
    cv.rect(SHAFT[0], top_y - 260, SHAFT[0] + 14, GROUND, fill=anth)
    cv.rect(SHAFT[1] - 14, top_y - 260, SHAFT[1], GROUND, fill=anth)
    for n in range(FLOORS + 1):
        cv.rect(SHAFT[0], yb(n) - 5, SHAFT[1], yb(n) + 5, fill=anth)
    for k in range(13):
        yy = top_y + k * 420
        cv.poly([(SHAFT[0] + 20, yy + 260), (SHAFT[0] + 120, yy), (SHAFT[0] + 150, yy), (SHAFT[0] + 50, yy + 260)],
                fill=(255, 255, 255, 35))
    # ---- roof: parapet, glass railing, solar panels, planters, machine room
    cv.rect(SHAFT[0] - 30, top_y - 24, APT[1] + 40, top_y + 6, fill=white)
    cv.rect(STAIRS[0], top_y - 130, APT[1] + 30, top_y - 24, fill=(235, 242, 248, 80))
    cv.rect(STAIRS[0], top_y - 136, APT[1] + 30, top_y - 128, fill=anth)
    for k in range(4):
        px = 1900 + k * 170
        cv.poly([(px, top_y - 30), (px + 140, top_y - 30), (px + 110, top_y - 120), (px - 10, top_y - 120)],
                fill=hexc("#253a6b"))
        for j in range(1, 3):
            cv.line([(px + j * 47 - 4 * j, top_y - 30), (px + j * 40 - 10, top_y - 120)], hexc("#5170a8"), 3, cap=False)
    for px in (1560, 2600):
        cv.rect(px - 50, top_y - 80, px + 50, top_y - 24, fill=anth_l, r=6)
        cv.circle(px, top_y - 170, 80, fill=hexc("#5e9a5a") if variant != "rain" else hexc("#6a7f6a"))
        cv.circle(px - 40, top_y - 140, 55, fill=hexc("#4f8a4c") if variant != "rain" else hexc("#5f735f"))
        cv.rect(px - 6, top_y - 110, px + 6, top_y - 80, fill=wood_d)
    cv.rect(SHAFT[0] - 20, top_y - 300, SHAFT[1] + 20, top_y - 24, fill=anth)
    for k in range(5):
        cv.rect(SHAFT[0] + 10 + k * 56, top_y - 260, SHAFT[0] + 46 + k * 56, top_y - 70, fill=anth_l)
    # ---- street level: pavers, trees, lamps, road
    cv.rect(0, GROUND, W, GROUND + 230, fill=hexc("#d9d6d0") if variant != "rain" else hexc("#a9abb0"))
    for k in range(0, W, 120):
        cv.rect(k, GROUND, k + 4, GROUND + 230, fill=hexc("#c7c3bb") if variant != "rain" else hexc("#9a9ca2"))
    cv.rect(0, GROUND + 105, W, GROUND + 110, fill=hexc("#c7c3bb") if variant != "rain" else hexc("#9a9ca2"))
    cv.rect(0, GROUND + 215, W, GROUND + 240, fill=hexc("#b8b4ab"))
    cv.rect(0, GROUND + 240, W, H, fill=hexc("#3b3f4a") if variant != "rain" else hexc("#353841"))
    for x in range(0, W, 300):
        cv.rect(x + 40, GROUND + 390, x + 200, GROUND + 408, fill=hexc("#ffffff"))
    tree = hexc("#5e9a5a") if variant != "rain" else hexc("#617061")
    for tx in (350, 850, 3000, 3420):
        cv.rect(tx - 10, GROUND - 260, tx + 10, GROUND, fill=wood_d)
        cv.circle(tx, GROUND - 330, 120, fill=tree)
        cv.circle(tx + 60, GROUND - 280, 80, fill=_dk(tree, 0.12))
    for lx in (600, 3200):
        cv.rect(lx - 6, GROUND - 520, lx + 6, GROUND, fill=anth)
        cv.rect(lx - 6, GROUND - 520, lx + 70, GROUND - 508, fill=anth)
        cv.rect(lx + 40, GROUND - 510, lx + 80, GROUND - 498, fill=hexc("#fff3c4"))
    if variant == "rain":
        img = ImageEnhance.Color(img).enhance(0.55)
        img = ImageEnhance.Brightness(img).enhance(0.85)
        arr = np.asarray(img).astype(np.float32) * np.array([0.95, 0.98, 1.06])
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return img


def _dk(c, f=0.2):
    return mix(c, (20, 16, 30), f)


WORLDS = {}


def world(variant):
    if variant not in WORLDS:
        p = os.path.join(CACHE, f"world_{variant}.png")
        if not os.path.exists(p):
            draw_world(variant).save(p)
        WORLDS[variant] = Image.open(p).convert("RGB")
    return WORLDS[variant]


# ------------------------------------------------------------------ elevator cab (world)

def draw_cab(cv, floor_f, door=0.0, rain=False):
    yb_ = GROUND - floor_f * FH
    x0, x1 = SX - CAB_W / 2, SX + CAB_W / 2
    y0 = yb_ - CAB_H
    anth = hexc(ANTH)
    cv.line([(SX, yb(FLOORS) - FH - 40), (SX, y0)], hexc("#555a66"), 5, cap=False)
    cv.rect(x0 - 12, y0 - 12, x1 + 12, yb_ + 6, fill=anth, r=8)
    back = hexc("#e9e4dc") if not rain else hexc("#b9b9b9")
    cv.rect(x0, y0, x1, yb_, fill=back)
    cv.rect(x0 + 40, y0 + 40, x1 - 40, yb_ - 40, fill=hexc(WOOD) if not rain else hexc("#8f8070"))
    for g in range(5):
        cv.rect(x0 + 60 + g * 32, y0 + 40, x0 + 63 + g * 32, yb_ - 40, fill=hexc(WOOD_D))
    cv.rect(x0 + 20, y0 + 12, x1 - 20, y0 + 22, fill=hexc("#fff6dc"), r=4)
    cv.rect(x0 + 14, y0 + 90, x0 + 38, y0 + 210, fill=hexc("#c9ced6"), r=6)
    for k in range(7):
        cv.circle(x0 + 26, y0 + 104 + k * 16, 5, fill=anth)
    cv.rect(x0, yb_ - 140, x1, yb_ - 132, fill=hexc("#c9ced6"))
    return (x0, y0, x1, yb_, door, anth)


def draw_cab_doors(cv, info):
    x0, y0, x1, y1, door, frame = info
    half = (x1 - x0) / 2
    off = half * door
    col = (190, 215, 235, 70)
    cv.rect(x0 - off, y0, x0 + half - off, y1, fill=col)
    cv.rect(x0 + half + off, y0, x1 + off, y1, fill=col)
    cv.rect(x0 - 12, y0 - 12, x0, y1 + 6, fill=frame)
    cv.rect(x1, y0 - 12, x1 + 12, y1 + 6, fill=frame)
    if door < 0.95:
        cv.line([(x0 + half - off, y0), (x0 + half - off, y1)], hexc(ANTH_L), 4, cap=False)
        cv.line([(x0 + half + off, y0), (x0 + half + off, y1)], hexc(ANTH_L), 4, cap=False)
    cv.rect(x0 - 12, y1 - 6, x1 + 12, y1 + 8, fill=frame)


# ------------------------------------------------------------------ timing

TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Das hier ist Alex", "Alex wohnt", "Jeden Morgen", "Bis hierhin", "Aber jeden Abend",
        "Alex steigt in den Aufzug", "Dort steigt", "Seine Nachbarn", "Denn Alex", "Eines Tages",
        "Alex kommt nach Hause", "Am nächsten Tag", "Und Alex steigt", "Warum macht", "PAUSE", "Kleiner Tipp",
        "Schreib deine", "Hier kommt", "Alex ist klein", "Nach unten", "Aber nach oben", "Und bei Regen",
        "Da hat Alex", "Mit der Spitze", "Hättest", "Schreib's"]
S, E = anchors(TIM, KEYS)
END = E[-1] + 2.6
XFADE = 0.25


def stair_path(t0, n0, n1, speed=0.62):
    """keys for Alex walking up the zigzag stairs from floor n0 to n1 starting at t0."""
    keys = []
    t = t0
    for n in range(n0, n1):
        a = (STAIRS[0] + 20, yb(n))
        m = (STAIRS[1] - 20, yb(n) - FH / 2)
        keys += [(t, *a), (t + speed, *m)]
        t += speed
        t += speed
    keys.append((t, STAIRS[0] + 20, yb(n1)))
    return keys, t


# ------------------------------------------------------------------ scene rendering

def render_world_frame(t, variant, cam, actors):
    """cam=(cx, cy, viewH). actors: callable(cv) drawing into world coords."""
    cx, cy, vh = cam
    vw = vh * OUT_W / OUT_H
    cx = clamp(cx, vw / 2, W - vw / 2)
    cy = clamp(cy, vh / 2, H - vh / 2)
    box = (int(cx - vw / 2), int(cy - vh / 2), int(cx + vw / 2), int(cy + vh / 2))
    crop = world(variant).crop(box)
    cv = Canvas(crop, box[0], box[1], 1.0)
    actors(cv)
    frame = crop.resize((OUT_W, OUT_H), Image.BILINEAR if vh > OUT_H else Image.BICUBIC)
    return frame, (box, vh / OUT_H)


def world_to_screen(x, y, view):
    box, k = view
    return (x - box[0]) / k, (y - box[1]) / k


def walk_phase(t, moving, speed=11):
    return t * speed if moving else None


def actor_alex(cv, t, keys, umbrella=None, face_default=1, **kw):
    x, y, moving, dx = path_pos(t, keys)
    face = 1 if dx > 0 else (-1 if dx < 0 else face_default)
    bounce = abs(math.sin(t * 11)) * 6 if moving else 0
    draw_person(cv, x, y, ALEX, phase=walk_phase(t, moving), face=face, umbrella=umbrella, bounce=bounce, **kw)
    return x, y


# --- scene A: intro ------------------------------------------------------------

def scene_intro(t):
    t_wide = S[1] + 0.8
    cam = keyframes(t, [(0, (1900, yb(12) - 170, 1150)), (t_wide - 0.1, (1900, yb(12) - 170, 1150)),
                        (t_wide + 1.2, (1925, 3300, 6500))])

    def actors(cv):
        draw_cab_doors(cv, draw_cab(cv, 0.0))
        draw_person(cv, ALEX_DOOR_X + 130, yb(12), ALEX, wave=t * 9 if t < t_wide else 0, face=-1)

    frame, view = render_world_frame(t, "dusk", cam, actors)
    # name tag
    sx, sy = world_to_screen(ALEX_DOOR_X + 130, yb(12) - 220, view)
    pop = ease_out_back(prog(t, 0.15, 0.55)) * (1 - prog(t, t_wide - 0.2, t_wide + 0.2))
    pill(frame, sx, sy - 40, "ALEX", 70, scale=pop, rot=4)
    # highlight floor 12 on wide shot
    if t > t_wide + 0.7:
        bx, by = world_to_screen(APT[0] + 95, yb(12) - FH + 70, view)
        pulse = 1 + 0.12 * math.sin(t * 8)
        pill(frame, bx + 150, by, "12. STOCK", 56, bg="#ffd34d",
             scale=ease_out_back(prog(t, t_wide + 0.7, t_wide + 1.0)) * pulse, rot=-3)
    return frame


# --- scene B: morning -----------------------------------------------------------

def scene_morning(t):
    t0 = S[2]
    t_ride0, t_ride1 = t0 + 1.9, t0 + 3.6
    keys = [(t0, ALEX_DOOR_X, yb(12)), (t0 + 0.2, ALEX_DOOR_X, yb(12)), (t0 + 1.4, SX + 10, yb(12)),
            (t_ride1 + 0.25, SX + 10, yb(0)), (t_ride1 + 1.6, SX + 700, yb(0))]

    def cab_floor(tt):
        return keyframes(tt, [(t_ride0, 12.0), (t_ride1, 0.0)])

    def door(tt):
        if tt < t_ride0:
            return 1 - prog(tt, t0 + 1.45, t_ride0)
        return prog(tt, t_ride1, t_ride1 + 0.25)

    fl = cab_floor(t)
    cy = GROUND - fl * FH - 170
    cam = keyframes(t, [(t0, (1600, yb(12) - 170, 1250)), (t_ride0, (1500, yb(12) - 170, 1250)),
                        (t_ride0 + 0.4, (1500, yb(10) - 170, 1700)), (t_ride1 - 0.3, (1500, yb(1) - 170, 1700)),
                        (t_ride1 + 0.1, (1650, yb(0) - 220, 1300)), (t_ride1 + 1.6, (1900, yb(0) - 220, 1300))])

    def actors(cv):
        info = draw_cab(cv, fl, door(t))
        x, y, moving, dx = path_pos(t, keys)
        if abs(x - (SX + 10)) < 1:  # inside the cab: ride with it
            y = GROUND - fl * FH
            moving = moving and dx != 0
        face = 1 if dx > 0 else -1 if dx < 0 else 1
        draw_person(cv, x, y, ALEX, phase=walk_phase(t, moving and not (t_ride0 <= t <= t_ride1)), face=face)
        draw_cab_doors(cv, info)
        # path line (green) while descending
        if t_ride0 < t:
            cv.line([(SX - 160, yb(12) - 20), (SX - 160, max(GROUND - fl * FH - 20, yb(12) - 20))],
                    hexc("#37b26c"), 18)
            cv.poly([(SX - 190, GROUND - fl * FH - 40), (SX - 130, GROUND - fl * FH - 40),
                     (SX - 160, GROUND - fl * FH + 10)], fill=hexc("#37b26c"))

    frame, view = render_world_frame(t, "day", cam, actors)
    clock_badge(frame, OUT_W / 2, 190, 7, 0, "07:00", scale=ease_out_back(prog(t, t0, t0 + 0.4)))
    if t_ride0 < t < t_ride1 + 0.6:
        floor_display(frame, OUT_W / 2, 400, "E" if fl < 0.5 else str(int(round(fl))), arrow=-1)
    if t > S[3] - 0.1:
        check_icon(frame, OUT_W / 2, OUT_H / 2 - 100, 120, scale=ease_out_back(prog(t, S[3] - 0.1, S[3] + 0.25)))
        pill(frame, OUT_W / 2, OUT_H / 2 + 110, "GANZ NORMAL", 64, scale=ease_out_back(prog(t, S[3], S[3] + 0.35)))
    return frame


# --- scene C: evening ------------------------------------------------------------

def scene_evening(t):
    t0 = S[4]
    t_in = S[5]
    t_ride0, t_ride1 = t_in + 0.4, t_in + 2.4
    t_exit = S[6]
    skeys, t_top = stair_path(t_exit + 0.6, 9, 12, speed=0.45)
    keys = [(t0, SX + 900, yb(0)), (t0 + 0.3, SX + 900, yb(0)), (t_in + 0.2, SX + 10, yb(0)),
            (t_ride1 + 0.3, SX + 10, yb(9)), (t_exit + 0.6, STAIRS[0] + 20, yb(9))] + skeys + \
           [(t_top + 0.8, ALEX_DOOR_X, yb(12))]

    def cab_floor(tt):
        return keyframes(tt, [(t_ride0, 0.0), (t_ride1, 9.0)])

    def door(tt):
        if tt < t_ride0:
            return 1 - prog(tt, t_in + 0.15, t_ride0)
        return prog(tt, t_ride1, t_ride1 + 0.3)

    fl = cab_floor(t)
    x, y, moving, dx = path_pos(t, keys)
    if abs(x - (SX + 10)) < 1:  # inside the cab: ride with it
        y = GROUND - fl * FH
        moving = moving and dx != 0
    if t < t_ride0:
        cam = keyframes(t, [(t0, (1900, yb(0) - 220, 1350)), (t_in + 0.2, (1550, yb(0) - 220, 1350))])
    elif t < t_exit:
        cam = keyframes(t, [(t_ride0, (1550, yb(0) - 220, 1350)), (t_ride0 + 0.4, (1500, yb(1) - 200, 1800)),
                            (t_ride1, (1500, yb(9) - 200, 1700)), (t_exit, (1520, yb(9) - 200, 1500))])
    else:
        cam = keyframes(t, [(t_exit, (1520, yb(9) - 200, 1500)), (t_exit + 0.8, (1650, y - 180, 1600))])
        cam = (cam[0], keyframes(t, [(t_exit, yb(9) - 200), (t_exit + 0.6, yb(9) - 200), (t_top, yb(12) - 200)]),
               cam[2])

    def actors(cv):
        info = draw_cab(cv, fl, door(t))
        face = 1 if dx > 0 else -1 if dx < 0 else 1
        draw_person(cv, x, y, ALEX, phase=walk_phase(t, moving and not (t_ride0 <= t <= t_ride1)), face=face,
                    bounce=abs(math.sin(t * 11)) * 5 if moving else 0)
        draw_cab_doors(cv, info)
        if t > t_ride0:
            top = max(GROUND - fl * FH, yb(9))
            cv.line([(SX - 160, yb(0) - 20), (SX - 160, top - 20)], hexc("#37b26c"), 18)
            cv.poly([(SX - 190, top - 10), (SX - 130, top - 10), (SX - 160, top - 60)], fill=hexc("#37b26c"))
        if t > t_exit + 0.4:  # dotted stair route
            pts = []
            for n in range(9, 12):
                pts += [(STAIRS[0] + 20, yb(n) - 30), (STAIRS[1] - 20, yb(n) - FH / 2 - 30)]
            pts.append((STAIRS[0] + 20, yb(12) - 30))
            reveal = prog(t, t_exit + 0.4, t_exit + 0.9)
            if reveal > 0:
                cv.line(pts[:max(2, int(len(pts) * reveal))], (255, 211, 77, 200), 12)

    frame, view = render_world_frame(t, "dusk", cam, actors)
    clock_badge(frame, OUT_W / 2, 190, 18, 0, "18:00", scale=ease_out_back(prog(t, t0, t0 + 0.4)), night=True)
    if t0 + 1.2 < t < t_in:
        sx, sy = world_to_screen(x, y - 260, view)
        pill(frame, sx, sy, "?", 90, bg="#ffd34d", scale=ease_out_back(prog(t, t0 + 1.2, t0 + 1.6)))
    if t_ride0 < t < t_exit + 0.4:
        floor_display(frame, OUT_W / 2, 400, "E" if fl < 0.5 else str(int(round(fl))), arrow=1 if t < t_ride1 else 0)
    if t_ride1 < t < t_exit + 0.6:
        check_icon(frame, OUT_W / 2 + 190, 400, 60, scale=ease_out_back(prog(t, t_ride1, t_ride1 + 0.3)), ok=True)
    if t > t_exit + 0.6:
        steps = clamp((t - (t_exit + 0.6)) / (t_top - t_exit - 0.6) * 3, 0, 3)
        n = 9 + int(steps)
        pill(frame, OUT_W / 2, 400, f"{min(n, 12)}. STOCK  ·  ZU FUSS", 56, bg="#fff6e6")
        pill(frame, OUT_W / 2, OUT_H - 330, "3 STOCKWERKE", 70, bg="#ffd34d", rot=-3,
             scale=ease_out_back(prog(t, t_exit + 0.3, t_exit + 0.7)))
    return frame


# --- scene D: neighbours -------------------------------------------------------------

def scene_neighbours(t):
    t0 = S[7]
    t1 = S[8]
    cam = keyframes(t, [(t0, (2150, yb(12) - 100, 1500)), (t0 + 1.2, (2200, yb(11) - 60, 1900)),
                        (t1, (2150, yb(12) - 160, 1500))])

    def actors(cv):
        # Elisa on 12th floor at her door, Paul on 11th floor
        draw_person(cv, 2400, yb(12), ELISA, face=-1)
        draw_person(cv, 2300, yb(11), PAUL, face=-1)
        if t < t1:
            draw_person(cv, ALEX_DOOR_X + 20, yb(12), ALEX, face=1)
        else:  # Alex jumps / stretches
            j = abs(math.sin((t - t1) * 6))
            draw_person(cv, ALEX_DOOR_X + 20, yb(12), ALEX, face=1, bounce=j * 50, arms_up=j)
        for k, (bx, by, tt) in enumerate([(2470, yb(12) - 330, t0 + 0.6), (2400, yb(11) - 340, t0 + 1.0)]):
            p = ease_out_back(prog(t, tt, tt + 0.3))
            if p > 0.01:
                speech_bubble(cv, bx, by, 55 * p, "?")

    frame, view = render_world_frame(t, "dusk", cam, actors)
    for nm, wx, wy, ts in (("ELISA", 2400, yb(12) - 150, t0 + 0.3), ("PAUL", 2300, yb(11) - 150, t0 + 0.6)):
        sx, sy = world_to_screen(wx - 190, wy, view)
        pill(frame, sx, sy, nm, 40, pad=(20, 10), scale=ease_out_back(prog(t, ts, ts + 0.3)))
    items = [("GESUND", S[8] + 0.5), ("SPORTLICH", S[8] + 1.2), ("TREPPEN? KEIN PROBLEM", S[8] + 2.3)]
    for i, (txt, ts) in enumerate(items):
        sc = ease_out_back(prog(t, ts, ts + 0.3))
        if sc > 0.01:
            y = 330 + i * 150
            check_icon(frame, 150, y, 50, scale=sc)
            pill(frame, 215, y, txt, 52, scale=sc, shadow=True, pad=(26, 14), anchor="l")
    return frame


def pill_left(frame, x, y, txt, size, scale):
    pill(frame, x, y, txt, size, scale=scale)


# --- scene E: rain ---------------------------------------------------------------------

def scene_rain(t):
    t0 = S[9]
    t_in = S[10]
    t_ride0, t_ride1 = t_in + 1.1, t_in + 3.4
    keys = [(t0, SX + 1000, yb(0)), (t_in + 0.9, SX + 10, yb(0)), (t_ride1 + 0.3, SX + 10, yb(12)),
            (t_ride1 + 1.6, ALEX_DOOR_X, yb(12))]

    fl = keyframes(t, [(t_ride0, 0.0), (t_ride1, 12.0)])
    door = (1 - prog(t, t_in + 0.9, t_ride0)) if t < t_ride0 else prog(t, t_ride1, t_ride1 + 0.3)
    x, y, moving, dx = path_pos(t, keys)
    if abs(x - (SX + 10)) < 1:  # inside the cab: ride with it
        y = GROUND - fl * FH
        moving = moving and dx != 0
    if t < t_ride0:
        cam = keyframes(t, [(t0, (2100, yb(0) - 260, 1500)), (t_in + 0.8, (1600, yb(0) - 240, 1350))])
    else:
        cam = keyframes(t, [(t_ride0, (1600, yb(0) - 240, 1350)), (t_ride0 + 0.5, (1500, yb(2) - 200, 1900)),
                            (t_ride1, (1500, yb(12) - 200, 1800)), (t_ride1 + 1.6, (1650, yb(12) - 200, 1400))])
    umb = "open" if x > SX + 160 and t < t_ride0 else "closed"

    def actors(cv):
        info = draw_cab(cv, fl, door, rain=True)
        face = 1 if dx > 0 else -1 if dx < 0 else 1
        draw_person(cv, x, y, ALEX, phase=walk_phase(t, moving and not (t_ride0 <= t <= t_ride1)), face=face,
                    umbrella=umb, bounce=abs(math.sin(t * 11)) * 5 if moving else 0)
        draw_cab_doors(cv, info)
        if t > t_ride0:
            top = GROUND - fl * FH
            cv.line([(SX - 160, yb(0) - 20), (SX - 160, top - 20)], hexc("#37b26c"), 18)
            cv.poly([(SX - 190, top - 10), (SX - 130, top - 10), (SX - 160, top - 60)], fill=hexc("#37b26c"))

    frame, view = render_world_frame(t, "rain", cam, actors)
    rain(frame, t)
    if t < t_in + 1.0:
        pill(frame, OUT_W / 2, 220, "REGEN!", 80, bg="#c5def5", rot=-4, scale=ease_out_back(prog(t, t0, t0 + 0.4)))
    if t_ride0 < t:
        floor_display(frame, OUT_W / 2, 330, "E" if fl < 0.5 else str(int(round(fl))), arrow=1 if t < t_ride1 else 0)
    if t > t_ride1:
        check_icon(frame, OUT_W / 2 + 190, 330, 60, scale=ease_out_back(prog(t, t_ride1, t_ride1 + 0.3)))
        pill(frame, OUT_W / 2, 520, "DIREKT IN DEN 12. STOCK", 54, bg="#ffd34d",
             scale=ease_out_back(prog(t, t_ride1 + 0.1, t_ride1 + 0.45)))
    return frame


# --- scene F: next sunny day -----------------------------------------------------------

def scene_sunny(t):
    t0 = S[11]
    t1 = S[12]
    t_ride0, t_ride1 = t1 - 0.6, t1 + 1.2
    keys = [(t0, SX + 10, yb(0)), (t_ride1 + 0.2, SX + 10, yb(9)), (t_ride1 + 1.3, STAIRS[0] + 20, yb(9))] + \
        stair_path(t_ride1 + 1.3, 9, 10, speed=0.45)[0]
    fl = keyframes(t, [(t_ride0, 0.0), (t_ride1, 9.0)])
    door = 0.0 if t < t_ride1 else prog(t, t_ride1, t_ride1 + 0.3)
    x, y, moving, dx = path_pos(t, keys)
    if abs(x - (SX + 10)) < 1:  # inside the cab: ride with it
        y = GROUND - fl * FH
        moving = moving and dx != 0
    cam = keyframes(t, [(t0, (1925, 3400, 6500)), (t1 - 0.7, (1925, 3400, 6500)),
                        (t_ride1 - 0.2, (1520, yb(9) - 200, 1500))])

    def actors(cv):
        info = draw_cab(cv, fl, door)
        face = 1 if dx > 0 else -1 if dx < 0 else 1
        draw_person(cv, x, y, ALEX, phase=walk_phase(t, moving and t > t_ride1), face=face)
        draw_cab_doors(cv, info)
        if t < t1 - 0.4:  # rainbow
            for i, c in enumerate(["#e2574c", "#f0a03c", "#ffd34d", "#37b26c", "#3f7fd9", "#8b5cc7"]):
                r = 1500 - i * 40
                cv.arc(1925 - r, HORIZON - r * 0.9, 1925 + r, HORIZON + r * 0.9, 180, 360, hexc(c, 150), 40)

    frame, view = render_world_frame(t, "day", cam, actors)
    clock_badge(frame, OUT_W / 2, 190, 18, 0, "18:00", scale=ease_out_back(prog(t, t0, t0 + 0.4)))
    if t > t_ride0:
        floor_display(frame, OUT_W / 2, 400, "E" if fl < 0.5 else str(int(round(fl))), arrow=1 if t < t_ride1 else 0)
    if t > t_ride1:
        pill(frame, OUT_W / 2, OUT_H - 330, "WIEDER NUR BIS 9", 66, bg="#ffd34d", rot=-3,
             scale=ease_out_back(prog(t, t_ride1, t_ride1 + 0.35)))
    return frame


# --- scene G: question + hint + call to comment --------------------------------------------

def scene_question(t):
    t0 = S[13]
    t_tip = S[15]
    t_cm = S[16]
    img = vgradient(OUT_W, OUT_H, [(0, "#14213d"), (1, "#2b3f74")])
    cv = Canvas(img)
    # stars
    rng = np.random.default_rng(1)
    for _ in range(70):
        x, y = rng.uniform(0, OUT_W), rng.uniform(0, OUT_H)
        tw = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv.circle(x, y, 2 + 2 * tw, fill=(255, 255, 255, int(80 + 100 * tw)))
    # Alex thinking in the centre
    s = 2.6
    cv_s = Canvas(img, -OUT_W / 2 / s, -(OUT_H * 0.70) / s, s)
    cv_s.ellipse(-60, -8, 60, 12, fill=(0, 0, 0, 70))
    draw_person(cv_s, 0, 0, ALEX, face=1, reach=(28, -125))
    # big question
    p = ease_out_back(prog(t, t0, t0 + 0.35))
    pill(img, OUT_W / 2, 420, "WARUM MACHT", 92, bg="#fff6e6", scale=p, rot=-3)
    pill(img, OUT_W / 2, 580, "ALEX DAS?", 110, bg="#ffd34d", scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)), rot=2)
    # thinking dots during pause
    if S[14] - 0.2 < t < t_tip:
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            cv.circle(OUT_W / 2 + 120 + i * 70, OUT_H * 0.70 - 560 - i * 35, 20 + 10 * a, fill=(255, 255, 255, int(120 + 135 * a)))
    if t > t_tip:
        sc = ease_out_back(prog(t, t_tip, t_tip + 0.35))
        pill(img, OUT_W / 2, 800, "TIPP: REGEN", 84, bg="#c5def5", fg="#2b2140", scale=sc, rot=-2)
        # little cloud icon
        if sc > 0.3:
            c = Canvas(img, -(OUT_W / 2 + 330), -800, 1.0)
            for dx_, dy_, r in [(-40, 0, 40), (0, -25, 52), (45, 0, 40)]:
                c.circle(dx_, dy_, r * sc, fill=hexc("#ffffff"))
            for k in range(3):
                yy = 50 + ((t * 300 + k * 40) % 90)
                c.line([(-35 + k * 35, yy), (-45 + k * 35, yy + 26)], hexc("#7fb7ff"), 7)
    if t > t_cm:
        sc = ease_out_back(prog(t, t_cm, t_cm + 0.35))
        pill(img, OUT_W / 2, OUT_H - 260, "SCHREIB'S IN DIE KOMMENTARE", 50, bg="#ffffff", scale=sc)
        cc = Canvas(img, -(OUT_W / 2), -(OUT_H - 420), 1.0)
        if sc > 0.2:
            cc.rect(-80 * sc, -55 * sc, 80 * sc, 45 * sc, fill=hexc("#ffd34d"), r=30 * sc)
            cc.poly([(-30 * sc, 40 * sc), (-55 * sc, 85 * sc), (5 * sc, 40 * sc)], fill=hexc("#ffd34d"))
            for k in range(3):
                cc.circle((-40 + k * 40) * sc, -5 * sc, 11 * sc, fill=hexc("#2b2140"))
    return img


# --- scene H: solution in the elevator --------------------------------------------------------

PANEL_X = 250
BTN_BOTTOM = 1390
BTN_STEP = 43


def btn_y(idx):
    return BTN_BOTTOM - idx * BTN_STEP


def draw_interior(cv, lit=None, glow=0.0, reach_ok=None):
    ink = hexc("#22243a")
    anth = hexc(ANTH)
    # lobby wall (light concrete panels) + floor tiles
    cv.rect(0, 0, OUT_W, OUT_H, fill=hexc("#e7e4df"))
    for k in range(0, OUT_W, 270):
        cv.rect(k, 0, k + 3, 1560, fill=hexc("#d6d2cb"))
    for k in range(0, 1560, 390):
        cv.rect(0, k, OUT_W, k + 3, fill=hexc("#d6d2cb"))
    cv.rect(0, 1560, OUT_W, OUT_H, fill=hexc("#bdb8b0"))
    for k in range(-400, OUT_W + 400, 180):
        cv.line([(k, 1560), (k - 260, OUT_H)], hexc("#aaa59c"), 4, cap=False)
    cv.rect(0, 1700, OUT_W, 1705, fill=hexc("#aaa59c"))
    # cab: anthracite portal, brushed steel sides, wood back wall
    cv.rect(90, 270, 990, 1570, fill=anth, r=10)
    cv.rect(125, 305, 955, 1540, fill=hexc("#c3c8cf"))
    for k in range(0, 830, 14):
        cv.rect(125 + k, 305, 127 + k, 1540, fill=hexc("#b5bac2") if (k // 14) % 3 else hexc("#d0d4da"))
    cv.rect(420, 330, 935, 1500, fill=hexc(WOOD))
    for k in range(9):
        cv.rect(450 + k * 55, 330, 455 + k * 55, 1500, fill=hexc(WOOD_D))
    cv.rect(380, 318, 900, 334, fill=hexc("#fff6dc"), r=6)
    cv.rect(125, 1500, 955, 1540, fill=hexc("#3a3d46"))
    cv.rect(560, 1160, 935, 1176, fill=hexc("#e2e5ea"), r=8)
    cv.rect(580, 1176, 590, 1205, fill=hexc("#e2e5ea"))
    # button panel (brushed steel)
    cv.rect(PANEL_X - 62, btn_y(12) - 62, PANEL_X + 62, BTN_BOTTOM + 62, fill=hexc("#dfe3e8"), r=18)
    cv.rect(PANEL_X - 62, btn_y(12) - 62, PANEL_X + 62, BTN_BOTTOM + 62, outline=hexc("#9aa1ab"), width=3, r=18)
    for idx in range(13):
        y = btn_y(idx)
        label = "E" if idx == 0 else str(idx)
        on = lit is not None and idx == lit
        r = 20
        if on and glow > 0:
            cv.circle(PANEL_X, y, r + 16 * glow, fill=hexc("#ffd34d", int(130 * glow)))
        out_of_reach = reach_ok is not None and idx > reach_ok
        fill = hexc("#ffd34d") if on else (hexc("#8a8f99") if out_of_reach else anth)
        cv.circle(PANEL_X, y, r, fill=fill, outline=hexc("#ffffff") if not on else hexc("#ffb800"), width=3)
        cv.text(PANEL_X, y + 1, label, 21, ink if on else hexc("#ffffff"))


def scene_solution(t):
    t0 = S[17]
    t_small = S[18]
    t_down = S[19]
    t_up = S[20]
    t_rain = S[21]
    t_umb = S[22]
    t_press = S[23]
    t_end = S[24]
    img = Image.new("RGB", (OUT_W, OUT_H))
    cv = Canvas(img)
    alex_h = 430
    ax, ay = 380, 1500
    lit, glow, reach, umb, reach_ok = None, 0.0, None, None, None
    if t_down <= t < t_up:
        lp = prog(t, t_down + 1.6, t_down + 2.4)
        reach = (PANEL_X + 14, btn_y(0)) if lp > 0 else None
        if lp >= 1:
            lit, glow = 0, 0.6 + 0.4 * math.sin(t * 8)
    elif t_up <= t < t_umb:
        p = prog(t, t_up + 0.3, t_up + 1.5)
        target_idx = 1 + p * 11
        reach = (PANEL_X + 18, btn_y(target_idx))
        reach_ok = 9 if t > t_up + 1.5 else None
        if t > t_up + 1.6:
            reach = (PANEL_X + 18, btn_y(9))
            lit, glow = 9, 0.6 + 0.4 * math.sin(t * 8)
        if t >= t_rain:
            reach = None
    elif t >= t_umb:
        umb = "closed"
        if t > t_press - 0.4:
            p = prog(t, t_press - 0.4, t_press + 1.2)
            umb = "pointer"
            # aim the umbrella tip from low buttons up to button 12
            sh = (ax - 0.10 * alex_h, ay - 0.72 * alex_h + 0.075 * alex_h * 0.4)
            tgt_idx = 6 + 6 * smooth(p)
            tx, ty = PANEL_X + 14, btn_y(tgt_idx)
            dx_, dy_ = tx - sh[0], ty - sh[1]
            dd = math.hypot(dx_, dy_)
            hl = max(40, dd - 0.62 * alex_h)
            reach = (sh[0] + dx_ / dd * hl, sh[1] + dy_ / dd * hl)
            if p >= 1:
                lit, glow = 12, 0.6 + 0.4 * math.sin(t * 8)
    draw_interior(cv, lit, glow, reach_ok)
    # reach zone
    if t_up + 1.5 < t < t_rain:
        zone_top = btn_y(9) - 26
        cv.rect(PANEL_X - 90, zone_top, PANEL_X + 90, BTN_BOTTOM + 30, outline=hexc("#37b26c"), width=8, r=20)
        for idx in (10, 11, 12):
            cv.line([(PANEL_X - 26, btn_y(idx) - 14), (PANEL_X + 26, btn_y(idx) + 14)], hexc("#e2574c"), 6)
    # comparison silhouette during "kleinwüchsig"
    if t_small - 0.1 < t < t_down:
        a = prog(t, t_small - 0.1, t_small + 0.3) * (1 - prog(t, t_down - 0.3, t_down))
        ghost = Style(720, "#ffffff", "#ffffff", "#ffffff", "#ffffff", hair_style="short")
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gl = Canvas(layer)
        draw_person(gl, 760, 1500, ghost, face=-1)
        alpha = layer.split()[3].point(lambda v: int(v * 0.35 * a))
        layer.putalpha(alpha)
        img.paste(layer, (0, 0), layer)
        # height lines
        cv.line([(380, 1500 - alex_h - 20), (900, 1500 - alex_h - 20)], hexc("#ffd34d", int(255 * a)), 6)
    face = -1
    hand = draw_person(cv, ax, ay, ALEX, face=face, reach=reach, umbrella=umb, h=alex_h, arm_scale=1.3)
    if t > t_umb and t < t_press:
        sc = ease_out_back(prog(t, t_umb, t_umb + 0.35))
        pill(img, 760, 900, "REGENSCHIRM!", 56, bg="#c5def5", scale=sc, rot=3)
    # banners
    if t < t_small + 0.2:
        sc = ease_out_back(prog(t, t0, t0 + 0.35)) * (1 - prog(t, t_small - 0.1, t_small + 0.2))
        pill(img, OUT_W / 2, 180, "DIE LÖSUNG", 96, bg="#fff6e6", rot=-4, scale=sc)
    if t_small <= t < t_down:
        pill(img, OUT_W / 2, 180, "ALEX IST KLEINWÜCHSIG", 60, bg="#ffd34d", rot=-2,
             scale=ease_out_back(prog(t, t_small, t_small + 0.35)))
    if t_down <= t < t_up:
        pill(img, OUT_W / 2, 180, "RUNTER: KNOPF E  ✓", 62, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, t_down, t_down + 0.35)))
    if t_up <= t < t_rain:
        pill(img, OUT_W / 2, 180, "HOCH: NUR BIS 9", 66, bg="#fff6e6", rot=2,
             scale=ease_out_back(prog(t, t_up, t_up + 0.35)))
    if t_rain <= t < t_end:
        pill(img, OUT_W / 2, 180, "UND BEI REGEN?", 70, bg="#c5def5", rot=-2,
             scale=ease_out_back(prog(t, t_rain, t_rain + 0.35)))
    if t >= t_press + 0.8 and t < t_end:
        check_icon(img, PANEL_X - 110, btn_y(12) - 60, 50, scale=ease_out_back(prog(t, t_press + 0.8, t_press + 1.1)))
        pill(img, 680, 900, "12. STOCK  ✓", 64, bg="#ffd34d", scale=ease_out_back(prog(t, t_press + 1.0, t_press + 1.35)))
    if t_rain <= t < t_umb:
        rain_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        rain(rain_layer, t, density=120, color=(90, 120, 180, 120))
        img.paste(rain_layer, (0, 0), rain_layer)
    return img


# --- scene I: outro --------------------------------------------------------------------------

def scene_outro(t):
    t0 = S[24]
    t1 = S[25]
    img = world(  # use the wide dusk shot as backdrop
        "dusk").crop((0, 400, W, 400 + int(W * OUT_H / OUT_W))).resize((OUT_W, OUT_H), Image.BILINEAR)
    img = ImageEnhance.Brightness(img).enhance(0.55)
    pill(img, OUT_W / 2, 520, "HÄTTEST DU'S", 96, bg="#fff6e6", rot=-3, scale=ease_out_back(prog(t, t0, t0 + 0.35)))
    pill(img, OUT_W / 2, 690, "GEWUSST?", 110, bg="#ffd34d", rot=2, scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)))
    if t > t1:
        pill(img, OUT_W / 2, 960, "SCHREIB'S IN DIE KOMMENTARE", 48, bg="#ffffff",
             scale=ease_out_back(prog(t, t1, t1 + 0.35)))
        followed = t > t1 + 2.0
        txt = "GEFOLGT  ✓" if followed else "+  FOLGEN"
        bg = "#37b26c" if followed else "#e2574c"
        pulse = 1 + (0.06 * math.sin(t * 10) if not followed else 0)
        pill(img, OUT_W / 2, 1130, txt, 72, bg=bg, fg="#ffffff", scale=ease_out_back(prog(t, t1 + 0.4, t1 + 0.75)) * pulse)
        pill(img, OUT_W / 2, 1290, "MORGEN: NEUES RÄTSEL", 48, bg="#fff6e6",
             scale=ease_out_back(prog(t, t1 + 1.0, t1 + 1.35)))
    s = 2.0
    cvs = Canvas(img, -(OUT_W / 2) / s, -(OUT_H - 90) / s, s)
    draw_person(cvs, 0, 0, ALEX, face=1, wave=t * 9)
    return img


SCENES = [
    (0.0, scene_intro),
    (S[2] - 0.05, scene_morning),
    (S[4] - 0.05, scene_evening),
    (S[7] - 0.05, scene_neighbours),
    (S[9] - 0.05, scene_rain),
    (S[11] - 0.05, scene_sunny),
    (S[13] - 0.05, scene_question),
    (S[17] - 0.05, scene_solution),
    (S[24] - 0.05, scene_outro),
]


def frame_at(t):
    idx = max(i for i, (st, _) in enumerate(SCENES) if t >= st)
    img = SCENES[idx][1](t)
    if idx > 0:
        st = SCENES[idx][0]
        if t < st + XFADE:  # crossfade from previous scene
            prev = SCENES[idx - 1][1](t)
            img = Image.blend(prev, img, smooth(prog(t, st, st + XFADE)))
    if t > END - 0.6:
        img = Image.blend(img, Image.new("RGB", img.size, (20, 14, 36)), prog(t, END - 0.6, END))
    return img


# ------------------------------------------------------------------ output

def render_chunk(args):
    i0, i1, path = args
    for v in ("day", "dusk", "rain"):
        world(v)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame_at(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return path


def render(out="video.mp4", workers=4):
    for v in ("day", "dusk", "rain"):
        world(v)
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
        ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]] or [0.5, 3.8, 7, 10.3, 13, 16, 20, 23, 27,
                                                                               30.5, 34, 37.5, 40.5, 42.5, 47, 50,
                                                                               53, 55.5, 60, 64, 67, 71, 75, 78]
        for t in ts:
            frame_at(t).save(os.path.join(HERE, "stills", f"t{t:05.1f}.jpg"), quality=85)
    else:
        render()
