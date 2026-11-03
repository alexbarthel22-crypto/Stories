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


ALEX = Style(150, "#f2c4a0", "#5a3a26", "#f0803c", "#2f3a6b", hair_style="curly", head=0.2, accent="#ffd34d")
ELISA = Style(250, "#f6d2b8", "#f3c95a", "#9b6fd1", "#3b3b5c", hair_style="long")
PAUL = Style(258, "#8d5a3b", "#1f1a24", "#e2574c", "#4a6fa5", hair_style="short", glasses=True)


def sky(variant):
    if variant == "day":
        stops = [(0, "#5aa7e0"), (0.35, "#9fd2f0"), (0.52, "#ffe2c2"), (0.53, "#4f8fc4"), (1, "#3f73a8")]
    elif variant == "rain":
        stops = [(0, "#4d5263"), (0.5, "#8b91a0"), (0.53, "#5d6577"), (1, "#4a5163")]
    else:
        stops = [(0, "#3a2c78"), (0.22, "#6b4fa6"), (0.40, "#d983b4"), (0.52, "#fbbf78"), (0.53, "#5b4c9e"),
                 (1, "#463b86")]
    return vgradient(W, H, stops)


def draw_world(variant):
    img = sky(variant)
    cv = Canvas(img)
    rng = np.random.default_rng(3)
    dusk = variant != "day"
    # sun + clouds
    if variant == "day":
        cv.circle(3000, 1500, 170, fill=hexc("#fff3c4"))
    elif variant == "dusk":
        cv.circle(560, HORIZON - 40, 210, fill=hexc("#ffd98a"))
    for cx, cy, s in [(500, 900, 1.2), (3050, 1250, 1.0), (700, 2300, 0.8), (2950, 2600, 1.1), (300, 3000, 0.7)]:
        col = hexc("#ffffff") if variant == "day" else hexc("#f6b5c6") if variant == "dusk" else hexc("#6d7384")
        for dx, dy, r in [(-110, 10, 70), (-30, -30, 95), (70, -10, 80), (150, 20, 55)]:
            cv.circle(cx + dx * s, cy + dy * s, r * s, fill=col)
        cv.rect(cx - 180 * s, cy + 10 * s, cx + 205 * s, cy + 75 * s, fill=col, r=30 * s)
    # mountains
    mcol = hexc("#4c3d93") if dusk else hexc("#6f8fbf")
    if variant == "rain":
        mcol = hexc("#555b6c")
    cv.poly([(0, HORIZON), (300, HORIZON - 380), (650, HORIZON - 160), (900, HORIZON)], fill=mcol)
    cv.poly([(2600, HORIZON), (3100, HORIZON - 520), (3350, HORIZON - 420), (3600, HORIZON - 600), (3600, HORIZON)],
            fill=mcol)
    # sea glints
    for i in range(60):
        x, y = rng.uniform(0, W), rng.uniform(HORIZON + 40, GROUND - 200)
        cv.rect(x, y, x + rng.uniform(60, 200), y + 8, fill=(255, 255, 255, 40))
    # city silhouettes
    city = hexc("#3b2f74") if dusk else hexc("#5a79a8")
    city2 = hexc("#4d3f8c") if dusk else hexc("#7a97c2")
    if variant == "rain":
        city, city2 = hexc("#4a4f5e"), hexc("#5a6070")
    for x0, x1, top, c in [(0, 380, 3800, city2), (320, 760, 3300, city), (720, 1100, 4100, city2),
                           (2760, 3100, 3600, city), (3050, 3450, 3100, city2), (3380, 3600, 3900, city)]:
        cv.rect(x0, top, x1, GROUND, fill=c)
        for wy in range(int(top) + 50, GROUND - 60, 90):
            for wx in range(int(x0) + 40, int(x1) - 40, 70):
                if rng.random() < 0.55:
                    lit = hexc("#ffcf6e") if (dusk and rng.random() < 0.6) else mix(c, (255, 255, 255), 0.25)
                    cv.rect(wx, wy, wx + 34, wy + 46, fill=lit)

    # ---- building
    cream, cream_d = hexc("#f5efe6"), hexc("#e2d8c8")
    teal, teal_d = hexc("#2f9c8f"), hexc("#21766c")
    ink = hexc("#2b2140")
    top_y = yb(FLOORS) - FH
    # stairs column wall
    cv.rect(STAIRS[0], top_y, STAIRS[1], GROUND, fill=cream)
    # facade dot pattern on stair wall
    for n in range(FLOORS + 1):
        for i in range(3):
            for j in range(3):
                cv.circle(STAIRS[0] + 190 + i * 32, yb(n) - FH + 80 + j * 32, 10, fill=cream_d)
    # apartments
    for n in range(FLOORS + 1):
        y1, y0 = yb(n), yb(n) - FH
        if n == 0:
            cv.rect(APT[0], y0, APT[1], y1, fill=hexc("#f5efe6"))
            # lobby glass front
            cv.rect(APT[0] + 40, y0 + 120, APT[1] - 40, y1, fill=hexc("#2f9c8f"))
            for k in range(6):
                xx = APT[0] + 40 + k * (APT[1] - APT[0] - 80) / 5
                cv.rect(xx - 10, y0 + 120, xx + 10, y1, fill=hexc("#d9a441"))
            cv.rect(APT[0] + 40, y0 + 110, APT[1] - 40, y0 + 130, fill=hexc("#d9a441"))
            # awning
            for k in range(12):
                xx = APT[0] + 20 + k * 76
                cv.rect(xx, y0 + 20, xx + 76, y0 + 95, fill=hexc("#2f9c8f") if k % 2 == 0 else hexc("#ffffff"))
                cv.pieslice(xx, y0 + 60, xx + 76, y0 + 130, 0, 180,
                            fill=hexc("#2f9c8f") if k % 2 == 0 else hexc("#ffffff"))
            # mailboxes
            for i in range(4):
                for j in range(3):
                    cv.rect(APT[0] + 520 + i * 60, y0 + 190 + j * 46, APT[0] + 570 + i * 60, y0 + 228 + j * 46,
                            fill=hexc("#e6c36a"))
            cv.rect(APT[0] + 30, y0 + 150, APT[0] + 120, y0 + 210, fill=hexc("#d9a441"), r=10)
            cv.text(APT[0] + 75, y0 + 181, "E", 44, ink)
            continue
        wall = hexc(PASTELS[n % len(PASTELS)])
        cv.rect(APT[0], y0, APT[1], y1, fill=wall)
        # door A (Alex's on floor 12)
        dcol = hexc(DOORS[n % len(DOORS)]) if n != FLOORS else hexc("#ffcf3f")
        cv.rect(ALEX_DOOR_X - 55, y1 - 285, ALEX_DOOR_X + 55, y1, fill=mix(dcol, (0, 0, 0), 0.25), r=8)
        cv.rect(ALEX_DOOR_X - 45, y1 - 275, ALEX_DOOR_X + 45, y1, fill=dcol, r=6)
        cv.circle(ALEX_DOOR_X + 25, y1 - 140, 8, fill=ink)
        # window with shutters
        wx0, wx1 = 2020, 2260
        cv.rect(wx0, y1 - 300, wx1, y1 - 60, fill=hexc("#ffffff"))
        cv.rect(wx0 + 14, y1 - 286, wx1 - 14, y1 - 74, fill=mix(hexc("#f29ab0"), hexc("#7e66c9"), 0.3))
        cv.poly([(wx0 + 14, y1 - 200), (wx0 + 120, y1 - 286), (wx0 + 170, y1 - 286), (wx0 + 14, y1 - 150)],
                fill=(255, 255, 255, 70))
        for sx0 in (wx0 - 80, wx1 + 10):
            cv.rect(sx0, y1 - 300, sx0 + 70, y1 - 60, fill=hexc("#ffffff"))
            for k in range(9):
                cv.rect(sx0 + 8, y1 - 290 + k * 26, sx0 + 62, y1 - 280 + k * 26, fill=cream_d)
        # door B
        bx = 2470
        dcol2 = hexc(DOORS[(n + 3) % len(DOORS)])
        cv.rect(bx - 55, y1 - 285, bx + 55, y1, fill=mix(dcol2, (0, 0, 0), 0.25), r=8)
        cv.rect(bx - 45, y1 - 275, bx + 45, y1, fill=dcol2, r=6)
        cv.circle(bx - 25, y1 - 140, 8, fill=ink)
        # lamp + plants
        cv.circle(2340, y1 - 330, 14, fill=hexc("#fff3c4"))
        if n % 3 == 1:
            cv.rect(2600, y1 - 130, 2660, y1 - 60, fill=hexc("#d9774a"), r=8)
            for a in range(5):
                cv.circle(2630 + (a - 2) * 18, y1 - 150 - (a % 2) * 20, 26, fill=hexc("#3e9a5a"))
        # floor badge
        cv.rect(APT[0] + 20, y0 + 26, APT[0] + 120, y0 + 92, fill=hexc("#d9a441"), r=12)
        cv.text(APT[0] + 70, y0 + 60, str(n), 44, ink)
        # balcony rail
        cv.rect(APT[0], y1 - 120, APT[1], y1, fill=(255, 255, 255, 55))
        cv.rect(APT[0], y1 - 128, APT[1], y1 - 112, fill=teal)
        for k in range(0, APT[1] - APT[0] + 1, 95):
            cv.rect(APT[0] + k - 5, y1 - 120, APT[0] + k + 5, y1, fill=teal)
    # stairs: zigzag flights between floors
    for n in range(FLOORS):
        a = (STAIRS[0] + 20, yb(n))
        m = (STAIRS[1] - 20, yb(n) - FH / 2)
        b = (STAIRS[0] + 20, yb(n + 1))
        for p0, p1 in ((a, m), (m, b)):
            cv.poly([p0, p1, (p1[0], p1[1] + 28), (p0[0], p0[1] + 28)], fill=cream_d)
            steps = 9
            for s in range(steps):
                f0, f1 = s / steps, (s + 1) / steps
                x0_, y0_ = p0[0] + (p1[0] - p0[0]) * f0, p0[1] + (p1[1] - p0[1]) * f0
                x1_, y1_ = p0[0] + (p1[0] - p0[0]) * f1, p0[1] + (p1[1] - p0[1]) * f1
                cv.line([(x0_, y0_), (x0_, y1_), (x1_, y1_)], hexc("#cfc3b0"), 6, cap=False)
            cv.line([(p0[0], p0[1] - 95), (p1[0], p1[1] - 95)], teal, 14)
            for k in range(5):
                f = (k + 0.5) / 5
                px, py = p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f
                cv.line([(px, py - 95), (px, py)], teal_d, 6, cap=False)
        cv.rect(m[0] - 40, m[1], m[0] + 25, m[1] + 22, fill=cream_d)
    # floor slabs
    for n in range(FLOORS + 1):
        cv.rect(SHAFT[0] - 20, yb(n), APT[1] + 20, yb(n) + 26, fill=cream)
        cv.rect(SHAFT[0] - 20, yb(n) + 22, APT[1] + 20, yb(n) + 30, fill=cream_d)
    # shaft frame
    cv.rect(SHAFT[0], top_y - 260, SHAFT[0] + 22, GROUND, fill=hexc("#ffffff"))
    cv.rect(SHAFT[1] - 22, top_y - 260, SHAFT[1], GROUND, fill=hexc("#ffffff"))
    for n in range(FLOORS + 1):
        cv.rect(SHAFT[0], yb(n) - 8, SHAFT[1], yb(n) + 8, fill=hexc("#ffffff"))
    # roof
    cv.rect(SHAFT[0] - 30, top_y - 20, APT[1] + 30, top_y + 10, fill=cream)
    cv.rect(STAIRS[0], top_y - 110, APT[1], top_y - 96, fill=teal)
    for k in range(STAIRS[0], APT[1] + 1, 60):
        cv.rect(k - 4, top_y - 110, k + 4, top_y - 20, fill=teal)
    cv.rect(SHAFT[0] - 20, top_y - 300, SHAFT[1] + 20, top_y - 20, fill=cream)   # machine room
    for k in range(4):
        cv.rect(SHAFT[0] + 30 + k * 62, top_y - 250, SHAFT[0] + 62 + k * 62, top_y - 120, fill=cream_d, r=12)
    cv.rect(SHAFT[0] - 40, top_y - 320, SHAFT[1] + 40, top_y - 296, fill=teal)
    for px in (2150, 2500):  # palms
        cv.rect(px - 12, top_y - 380, px + 12, top_y - 20, fill=hexc("#8a5a3c"))
        for a in range(6):
            ang = math.pi + a * math.pi / 5
            cv.line([(px, top_y - 380), (px + math.cos(ang) * 150, top_y - 380 + math.sin(ang) * 80 + 60)],
                    hexc("#2f8a5a"), 34)
    for k in range(10):
        cv.circle(1820 + k * 44, top_y - 140 - (k % 3) * 18, 26, fill=hexc("#e05a8a") if k % 2 else hexc("#3e9a5a"))
    # street
    cv.rect(0, GROUND, W, GROUND + 230, fill=hexc("#ffffff"))
    wave = hexc("#8a7cc8") if variant != "rain" else hexc("#7d8294")
    for row in range(3):
        pts = [(x, GROUND + 50 + row * 60 + 18 * math.sin(x / 45)) for x in range(0, W + 20, 20)]
        cv.line(pts, wave, 20, cap=False)
    cv.rect(0, GROUND + 230, W, H, fill=hexc("#4a4458") if variant != "rain" else hexc("#3f4250"))
    for x in range(0, W, 300):
        cv.rect(x + 40, GROUND + 380, x + 200, GROUND + 400, fill=hexc("#ffffff"))
    # lobby entrance opening near shaft (walkway from street)
    if variant == "rain":
        img = ImageEnhance.Color(img).enhance(0.45)
        img = ImageEnhance.Brightness(img).enhance(0.82)
        arr = np.asarray(img).astype(np.float32)
        arr = arr * np.array([0.95, 0.98, 1.06])
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return img


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
    cv.line([(SX, yb(FLOORS) - FH - 40), (SX, y0)], hexc("#555066"), 6, cap=False)
    gold = hexc("#d9a441") if not rain else hexc("#a99266")
    cv.rect(x0 - 14, y0 - 14, x1 + 14, yb_ + 6, fill=gold, r=10)
    back = hexc("#22857a") if not rain else hexc("#4b6d6a")
    cv.rect(x0, y0, x1, yb_, fill=back)
    cv.rect(x0 + 30, y0 + 16, x1 - 30, y0 + 30, fill=hexc("#fff3c4"), r=6)
    cv.rect(x0 + 18, y0 + 70, x0 + 46, y0 + 200, fill=hexc("#e9e4ec"), r=8)
    for k in range(7):
        cv.circle(x0 + 32, y0 + 85 + k * 17, 5, fill=hexc("#8a8396"))
    return (x0, y0, x1, yb_, door, gold)


def draw_cab_doors(cv, info):
    x0, y0, x1, y1, door, gold = info
    half = (x1 - x0) / 2
    off = half * door
    col = (60, 180, 165, 120)
    cv.rect(x0 - off, y0, x0 + half - off, y1, fill=col)
    cv.rect(x0 + half + off, y0, x1 + off, y1, fill=col)
    cv.rect(x0 - 14, y0 - 14, x0, y1 + 6, fill=gold)
    cv.rect(x1, y0 - 14, x1 + 14, y1 + 6, fill=gold)
    if door < 0.95:
        cv.line([(x0 + half - off, y0), (x0 + half - off, y1)], hexc("#1b5f57"), 4, cap=False)
        cv.line([(x0 + half + off, y0), (x0 + half + off, y1)], hexc("#1b5f57"), 4, cap=False)
    cv.rect(x0 - 14, y1 - 6, x1 + 14, y1 + 8, fill=gold)


# ------------------------------------------------------------------ timing

TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
S = [x["start"] for x in TIM]
E = [x["end"] for x in TIM]
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
    t_wide = S[1]
    cam = keyframes(t, [(0, (1900, yb(12) - 170, 1150)), (t_wide - 0.1, (1900, yb(12) - 170, 1150)),
                        (t_wide + 1.6, (1925, 3300, 6500))])

    def actors(cv):
        draw_cab_doors(cv, draw_cab(cv, 0.0))
        draw_person(cv, ALEX_DOOR_X + 130, yb(12), ALEX, wave=t * 9 if t < t_wide else 0, face=-1)

    frame, view = render_world_frame(t, "dusk", cam, actors)
    # name tag
    sx, sy = world_to_screen(ALEX_DOOR_X + 130, yb(12) - 220, view)
    pop = ease_out_back(prog(t, 0.15, 0.55)) * (1 - prog(t, t_wide - 0.2, t_wide + 0.2))
    pill(frame, sx, sy - 40, "ALEX", 70, scale=pop, rot=4)
    # highlight floor 12 on wide shot
    if t > t_wide + 1.0:
        bx, by = world_to_screen(APT[0] + 70, yb(12) - FH + 60, view)
        pulse = 1 + 0.12 * math.sin(t * 8)
        pill(frame, bx + 150, by, "12. STOCK", 56, bg="#ffd34d",
             scale=ease_out_back(prog(t, t_wide + 1.0, t_wide + 1.4)) * pulse, rot=-3)
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

    frame, view = render_world_frame(t, "dusk", cam, actors)
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
    img = vgradient(OUT_W, OUT_H, [(0, "#2b2140"), (1, "#3a2c78")])
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
    ink = hexc("#2b2140")
    # outside wall
    cv.rect(0, 0, OUT_W, OUT_H, fill=hexc("#f5efe6"))
    cv.rect(0, 1560, OUT_W, OUT_H, fill=hexc("#8a7cc8"))
    for row in range(4):
        pts = [(x, 1610 + row * 70 + 16 * math.sin(x / 40)) for x in range(0, OUT_W + 20, 20)]
        cv.line(pts, hexc("#ffffff"), 18, cap=False)
    # cab frame
    cv.rect(100, 280, 980, 1560, fill=hexc("#d9a441"), r=24)
    cv.rect(130, 310, 950, 1540, fill=hexc("#22857a"))
    for k in range(3):
        cv.rect(470 + k * 160, 360, 590 + k * 160, 1500, fill=hexc("#2a958a"), r=16)
    cv.rect(400, 330, 700, 360, fill=hexc("#fff3c4"), r=12)
    cv.rect(130, 1500, 950, 1540, fill=hexc("#1c6e65"))
    # handrail
    cv.rect(560, 1170, 940, 1188, fill=hexc("#d9a441"), r=8)
    # panel
    cv.rect(PANEL_X - 60, btn_y(12) - 60, PANEL_X + 60, BTN_BOTTOM + 60, fill=hexc("#e9e4ec"), r=30)
    for idx in range(13):
        y = btn_y(idx)
        label = "E" if idx == 0 else str(idx)
        on = lit is not None and idx == lit
        r = 20
        if on and glow > 0:
            cv.circle(PANEL_X, y, r + 16 * glow, fill=hexc("#ffd34d", int(120 * glow)))
        out_of_reach = reach_ok is not None and idx > reach_ok
        fill = hexc("#ffd34d") if on else (hexc("#d6cfdc") if out_of_reach else hexc("#ffffff"))
        cv.circle(PANEL_X, y, r, fill=fill, outline=hexc("#8a8396"), width=3)
        cv.text(PANEL_X, y + 1, label, 22, ink)


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
