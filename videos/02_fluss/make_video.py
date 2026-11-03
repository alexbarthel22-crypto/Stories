"""Rätsel #2 – Niklas, Wolf, Ziege und Kohlkopf.

usage:  python3 make_video.py            -> renders video.mp4 (needs voice.wav + timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from animals import draw_wolf, draw_goat, draw_cabbage, draw_boat_back, draw_boat_front, BOAT_W

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# ------------------------------------------------------------------ world layout
# Portrait layout: start bank in the back (top), river across, goal bank in front (bottom).
# World units = screen pixels (1080x1920); the world image is rendered at 2x for crisp zooms.
W, H = OUT_W, OUT_H
ZW = 2                         # world image supersampling
FAR_Y, NEAR_Y = 865, 1440      # ground line of start / goal bank
WATER = (905, 1262)            # river top / bottom edge
BOAT_X = 765
BOAT_WY = {"L": 965, "R": 1225}   # boat waterline at start (L) / goal (R)
SCALE = {"L": 0.8, "R": 1.0}
SLOTS = {"L": {"wolf": 150, "goat": 330, "cabbage": 480},
         "R": {"cabbage": 190, "goat": 360, "wolf": 565}}
NIKLAS_BANK_X = 615
ITEM_S = 0.95
ANTH, WOOD, WOOD_D = "#2c2f38", "#b9804f", "#94603a"

NIKLAS = Style(205, "#f3c9a6", "#b8642e", "#3f8f6b", "#2f3a56", shoes="#ffffff", hair_style="quiff",
               accent="#24493a", under="#f4efe4", shoe_accent="#3f7fd9")


def bank_y(side):
    return FAR_Y if side == "L" else NEAR_Y


# ------------------------------------------------------------------ world
def draw_world():
    img = Image.new("RGB", (W * ZW, H * ZW))
    sky = vgradient(W * ZW, 700 * ZW, [(0, "#14213d"), (0.35, "#2b3f74"), (0.7, "#6a6aa8"), (0.9, "#f08a5d"),
                                       (1, "#ffc178")])
    img.paste(sky, (0, 0))
    cv = Canvas(img, 0, 0, ZW)
    rng = np.random.default_rng(7)
    cv.circle(860, 600, 90, fill=hexc("#ffe0a0"))
    for cx, cy, s in [(230, 250, 0.7), (840, 380, 0.6)]:
        col = (255, 214, 190, 90)
        cv.rect(cx - 220 * s, cy - 30 * s, cx + 220 * s, cy + 30 * s, fill=col, r=30 * s)
        cv.rect(cx - 120 * s, cy - 75 * s, cx + 90 * s, cy + 10 * s, fill=col, r=45 * s)
    # skyline on the far side (same style as video #1)
    far, near = hexc("#46507e"), hexc("#2a3157")
    for layer, col, base in ((0, far, 420), (1, near, 520)):
        x = -40 + layer * 50
        while x < W:
            w = int(rng.integers(60, 130))
            top = base + int(rng.integers(-170, 90))
            cv.rect(x, top, x + w, 700, fill=col)
            if rng.random() < 0.35:
                cv.rect(x + w * 0.3, top - 34, x + w * 0.7, top, fill=col)
            for wy in range(top + 16, 690, 26 if layer else 32):
                for wx in range(int(x) + 9, int(x + w) - 12, 19):
                    if rng.random() < 0.42:
                        cv.rect(wx, wy, wx + 10, wy + 14, fill=hexc("#ffd58a") if rng.random() < 0.7 else
                                mix(col, (255, 255, 255), 0.2))
            x += w + int(rng.integers(8, 34))
    # start bank (back)
    cv.rect(0, 690, W, WATER[0] + 10, fill=hexc("#4f8a4c"))
    cv.rect(0, 690, W, 720, fill=hexc("#447a42"))
    for tx, r in ((40, 70), (250, 55), (980, 80), (1060, 60)):
        cv.rect(tx - 7, 700 - r * 1.6, tx + 7, 720, fill=hexc(WOOD_D))
        cv.circle(tx, 700 - r * 1.8, r, fill=hexc("#3f7a40"))
    for _ in range(40):
        x, y = rng.uniform(0, W), rng.uniform(730, WATER[0] - 10)
        cv.line([(x, y), (x - 4, y - 12)], hexc("#5f9a52"), 3)
    # river
    river = vgradient(W * ZW, (WATER[1] - WATER[0]) * ZW, [(0, "#2f5f9a"), (1, "#3d78b8")])
    img.paste(river, (0, WATER[0] * ZW))
    cv = Canvas(img, 0, 0, ZW)
    cv.rect(0, WATER[0], W, WATER[0] + 12, fill=hexc("#3b2f26"))      # far bank edge
    # goal bank (front)
    front = vgradient(W * ZW, (H - WATER[1]) * ZW, [(0, "#5f9a52"), (0.35, "#558c49"), (1, "#3f6e3a")])
    img.paste(front, (0, WATER[1] * ZW))
    cv = Canvas(img, 0, 0, ZW)
    cv.rect(0, WATER[1] - 6, W, WATER[1] + 14, fill=hexc("#6b8f4a"))
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(WATER[1] + 30, H)
        cv.line([(x, y), (x - 6, y - 20)], hexc("#6fae5a"), 4)
    for _ in range(18):
        x, y = rng.uniform(20, W - 20), rng.uniform(1520, H - 40)
        col = hexc(["#ffd34d", "#f6f1ea", "#e98aa0"][int(rng.integers(0, 3))])
        for a in range(5):
            cv.circle(x + 8 * math.cos(a * 1.256), y + 8 * math.sin(a * 1.256), 6, fill=col)
        cv.circle(x, y, 4, fill=hexc("#f0a03c"))
    # jetties at the boat docks
    for wy, sc, top in ((BOAT_WY["L"], 0.8, WATER[0] - 6), (BOAT_WY["R"], 1.0, WATER[1] - 4)):
        x0, x1 = BOAT_X + 175 * sc, BOAT_X + 290 * sc
        cv.rect(x0, top - 8, x1, top + 10, fill=hexc(WOOD), r=4)
        for k in range(int(x0) + 8, int(x1), 18):
            cv.rect(k, top - 8, k + 2, top + 10, fill=hexc(WOOD_D))
    # reeds
    for rx, ry in ((40, WATER[0] + 8), (980, WATER[0] + 8), (60, WATER[1] + 4), (1000, WATER[1] + 4)):
        for k in range(6):
            cv.line([(rx + k * 7, ry), (rx + k * 7 - 8 + k * 3, ry - 50 - (k % 3) * 14)], hexc("#6f9a5a"), 4)
    return img


_WORLD = None


def world():
    global _WORLD
    if _WORLD is None:
        p = os.path.join(CACHE, "world.png")
        if not os.path.exists(p):
            draw_world().save(p)
        _WORLD = Image.open(p).convert("RGB")
    return _WORLD


def render_world_frame(cam, actors):
    cx, cy, vh = cam
    vh = min(vh, H)
    vw = vh * OUT_W / OUT_H
    cx = clamp(cx, vw / 2, W - vw / 2)
    cy = clamp(cy, vh / 2, H - vh / 2)
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    crop = world().crop(tuple(int(round(v * ZW)) for v in box))
    cv = Canvas(crop, box[0], box[1], ZW)
    actors(cv)
    return crop.resize((OUT_W, OUT_H), Image.LANCZOS), (box, vh / OUT_H)


def w2s(x, y, view):
    box, k = view
    return (x - box[0]) / k, (y - box[1]) / k


FULL = (W / 2, H / 2, H)


# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Niklas steht", "Er muss alle", "Das Problem", "Und es gibt", "Bleiben Wolf", "Bleiben Ziege", "Wie bringt",
        "PAUSE", "Kleiner Tipp", "Schreib deine", "Hier kommt", "Zuerst bringt", "Dann fährt er allein",
        "Jetzt holt", "Aber Achtung", "Also nimmt", "Er setzt", "Wolf und Kohl warten", "Dann fährt er wieder",
        "Zum Schluss", "Und alle drei", "Hättest", "Schreib's"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 2.6
XFADE = 0.25


def st(key):
    return S[K[key]]


# ------------------------------------------------------------------ solution trips
TRIP_KEYS = [("Zuerst bringt", "goat", "ZIEGE  →"), ("Dann fährt er allein", None, "ALLEIN  ←"),
             ("Jetzt holt", "cabbage", "KOHL  →"), ("Also nimmt", "goat", "ZIEGE  ←"),
             ("Er setzt", "wolf", "WOLF  →"), ("Dann fährt er wieder", None, "ALLEIN  ←"),
             ("Zum Schluss", "goat", "ZIEGE  →")]


def build_trips():
    trips = []
    side = "L"
    for i, (key, cargo, label) in enumerate(TRIP_KEYS):
        t0 = st(key) + 0.1
        nxt = st(TRIP_KEYS[i + 1][0]) if i + 1 < len(TRIP_KEYS) else st("Und alle drei")
        # "Er setzt die Ziege ab ..." : give the goat-unload of the previous trip time first
        dur = clamp(nxt - t0 - 0.15, 1.6, 2.8)
        dest = "R" if side == "L" else "L"
        trips.append(dict(t0=t0, t1=t0 + dur, cargo=cargo, frm=side, to=dest, label=label, n=i + 1))
        side = dest
    return trips


TRIPS = build_trips()
LOAD, UNLOAD = 0.45, 0.45


def boat_pos(t):
    """0 = docked at start bank (back), 1 = docked at goal bank (front)"""
    p = 0.0
    for tr in TRIPS:
        if t < tr["t0"] + LOAD:
            return p
        a, b = (0.0, 1.0) if tr["frm"] == "L" else (1.0, 0.0)
        if t < tr["t1"] - UNLOAD:
            return a + (b - a) * smooth(prog(t, tr["t0"] + LOAD, tr["t1"] - UNLOAD))
        p = b
    return p


def boat_geom(t, solution=True):
    p = boat_pos(t) if solution else 0.0
    wy = BOAT_WY["L"] + (BOAT_WY["R"] - BOAT_WY["L"]) * p
    sc = SCALE["L"] + (SCALE["R"] - SCALE["L"]) * p
    return BOAT_X, wy, sc


def boat_moving(t):
    return any(tr["t0"] + LOAD < t < tr["t1"] - UNLOAD for tr in TRIPS)


def hop(p, a, b, height=90):
    """position along a hop from a to b (p in 0..1)"""
    p = smooth(p)
    return a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p - math.sin(math.pi * p) * height


def item_state(name, t, solution=True):
    """returns (x, y, scale, where) with where in L / R / boat / hop"""
    side = "L"
    if solution:
        for tr in TRIPS:
            if tr["cargo"] != name:
                continue
            if t < tr["t0"]:
                break
            bx, wy, bsc = boat_geom(t)
            seat = (bx + 62 * bsc, wy - 12 * bsc)
            src = (SLOTS[tr["frm"]][name], bank_y(tr["frm"]))
            dst = (SLOTS[tr["to"]][name], bank_y(tr["to"]))
            if t < tr["t0"] + LOAD:
                x, y = hop(prog(t, tr["t0"], tr["t0"] + LOAD), src, seat)
                return x, y, SCALE[tr["frm"]] * ITEM_S, "hop"
            if t < tr["t1"] - UNLOAD:
                return seat[0], seat[1], bsc * ITEM_S * 0.92, "boat"
            if t < tr["t1"]:
                x, y = hop(prog(t, tr["t1"] - UNLOAD, tr["t1"]), seat, dst)
                return x, y, SCALE[tr["to"]] * ITEM_S, "hop"
            side = tr["to"]
    return SLOTS[side][name], bank_y(side), SCALE[side] * ITEM_S, side


def side_of(name, t):
    return item_state(name, t)[3]


def draw_item(cv, name, x, y, sc, t, face=1, mood=0.0):
    if name == "wolf":
        draw_wolf(cv, x, y, sc, face=face, mood=mood)
    elif name == "goat":
        draw_goat(cv, x, y, sc, face=face)
    else:
        draw_cabbage(cv, x, y, sc * 1.2)


def draw_water(cv, t):
    for k in range(6):
        y = WATER[0] + 40 + k * 55
        amp = 3 + k
        pts = [(x, y + amp * math.sin(x / (30 + k * 6) + t * 2.0 + k)) for x in range(0, W + 20, 16)]
        cv.line(pts, (255, 255, 255, 60 + k * 12), 3 + k * 0.6, cap=False)


def draw_scene(cv, t, solution, niklas_in_boat, mood=0.0):
    """back bank -> water -> boat -> front bank (painter's order)"""
    draw_water(cv, t)
    st_ = {n: item_state(n, t, solution) for n in ("wolf", "goat", "cabbage")}
    for n, (x, y, sc, wh) in st_.items():
        if wh == "L":
            draw_item(cv, n, x, y, sc, t, face=1, mood=mood if n == "wolf" else 0)
    bx, wy, bsc = boat_geom(t, solution)
    moving = solution and boat_moving(t)
    # boat (scaled canvas around the boat)
    sub = Canvas(cv.img, cv.ox / bsc + bx - bx / bsc, cv.oy / bsc + wy - wy / bsc, cv.s * bsc)
    floor = draw_boat_back(sub, bx, wy, t)
    if niklas_in_boat:
        nx = bx - 78
        row = math.sin(t * 6) if moving else 0
        draw_person(sub, nx, floor + 6, NIKLAS, face=1,
                    reach=(nx + 80, floor - 105 + row * 22) if moving else None)
    for n, (x, y, sc, wh) in st_.items():
        if wh == "boat":
            draw_item(sub, n, bx + 62, floor + 4, ITEM_S * 0.92, t, face=1)
    oar = math.radians(118 + 22 * math.sin(t * 6)) if (niklas_in_boat and moving) else None
    draw_boat_front(sub, bx, wy, t, oar=oar)
    for n, (x, y, sc, wh) in st_.items():
        if wh == "hop":
            draw_item(cv, n, x, y, sc, t, face=1)
        elif wh == "R":
            draw_item(cv, n, x, y, sc, t, face=1)


# ------------------------------------------------------------------ overlay helpers
def rule_card(img, cy, a, b, scale=1.0, ok=False, label=None):
    """card:  [icon a] + [icon b]  (x)  with a label underneath"""
    if scale <= 0.01:
        return
    Z = 2
    w, h = 640, 210
    tile = Image.new("RGBA", (w * Z, h * Z), (0, 0, 0, 0))
    cv = Canvas(tile, 0, 0, Z)
    cv.rect(10, 16, w - 4, h - 2, fill=(30, 20, 60, 90), r=36)
    cv.rect(4, 4, w - 12, h - 14, fill=hexc("#dfe7f2"), r=36)
    for k, (name, cx) in enumerate(((a, 140), (b, 370))):
        sc = 0.78
        ic = Canvas(tile, -cx / sc + 0, -170 / sc, Z * sc)
        draw_item(ic, name, 0, 0, 1.0, 0, face=1 if k == 0 else -1)
    cv.text(255, 110, "+", 80, hexc("#2b2140"))
    tile = tile.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    x0, y0 = int(OUT_W / 2 - tile.width / 2), int(cy - tile.height / 2)
    img.paste(tile, (x0, y0), tile)
    log_ui("card", x0, y0, x0 + tile.width, y0 + tile.height)
    check_icon(img, x0 + tile.width - 95 * scale, cy - 5 * scale, 58 * scale, ok=ok)
    if label:
        pill(img, OUT_W / 2, cy + 130 * scale, label, 44, bg="#e2574c" if not ok else "#37b26c", fg="#ffffff",
             scale=scale, pad=(24, 12))


def group_x(side):
    xs = list(SLOTS[side].values())
    return sum(xs) / len(xs)


# ------------------------------------------------------------------ scenes
def scene_story(t):
    t0 = st("Niklas steht")
    t1, t2, t3, t4, t5 = st("Er muss alle"), st("Das Problem"), st("Und es gibt"), st("Bleiben Wolf"), st("Bleiben Ziege")
    close_l = (420, 780, 1200)
    boat_cam = (700, 860, 1000)
    cam = keyframes(t, [(t0, close_l), (t1 - 0.1, close_l), (t1 + 0.9, FULL), (t2 - 0.05, FULL),
                        (t2 + 0.6, boat_cam), (t3 - 0.05, boat_cam), (t3 + 0.6, FULL)])
    mood = smooth(prog(t, t4 + 0.4, t4 + 1.2)) * (1 - smooth(prog(t, t5, t5 + 0.5)))

    def actors(cv):
        draw_scene(cv, t, solution=False, niklas_in_boat=False, mood=mood)
        wave = t * 9 if t < t0 + 1.0 else 0
        draw_person(cv, NIKLAS_BANK_X, FAR_Y, NIKLAS, face=-1, wave=wave, h=NIKLAS.h * SCALE["L"])
        if t1 + 0.5 < t < t2:   # dotted route across the river
            p = prog(t, t1 + 0.5, t1 + 1.3)
            for k in range(12):
                f = k / 11
                if f > p:
                    break
                cv.circle(BOAT_X - 120 + 30 * math.sin(f * math.pi), WATER[0] + 30 + f * (WATER[1] - WATER[0] - 60),
                          9, fill=hexc("#ffd34d"))

    frame, view = render_world_frame(cam, actors)
    if t < t1 + 0.2:
        out = 1 - prog(t, t1 - 0.1, t1 + 0.2)
        items = (("NIKLAS", NIKLAS_BANK_X, FAR_Y - 205), ("WOLF", SLOTS["L"]["wolf"], FAR_Y - 140),
                 ("ZIEGE", SLOTS["L"]["goat"], FAR_Y - 150), ("KOHL", SLOTS["L"]["cabbage"], FAR_Y - 100))
        for k, (nm, wx, wy) in enumerate(items):
            ts = t0 + 0.3 + k * (t1 - t0 - 0.6) / 4
            sx, sy = w2s(wx, wy, view)
            pill(frame, clamp(sx, 150, 790), sy, nm, 46, pad=(22, 10), rot=(-3 if k % 2 else 3),
                 scale=ease_out_back(prog(t, ts, ts + 0.3)) * out, bg="#ffd34d" if k == 0 else "#fff6e6")
    if t1 + 0.7 < t < t2 + 0.1:
        sc = ease_out_back(prog(t, t1 + 0.7, t1 + 1.0))
        sx, sy = w2s(group_x("L"), 610, view)
        pill(frame, sx, sy, "START", 50, scale=sc)
        sx, sy = w2s(group_x("R"), 1330, view)
        pill(frame, sx, sy, "ZIEL", 54, bg="#37b26c", fg="#ffffff", scale=sc)
    if t2 + 0.5 < t < t3:
        pill(frame, OUT_W / 2, 420, "IM BOOT: NIKLAS + 1", 60, bg="#ffd34d", rot=-2,
             scale=ease_out_back(prog(t, t2 + 0.5, t2 + 0.85)))
    if t3 < t:
        pill(frame, OUT_W / 2, 330, "2 REGELN", 70, bg="#fff6e6", rot=-3, scale=ease_out_back(prog(t, t3, t3 + 0.35)))
    if t4 < t:
        rule_card(frame, 1000, "wolf", "goat", scale=ease_out_back(prog(t, t4 + 0.1, t4 + 0.45)), label="WOLF FRISST ZIEGE")
    if t5 < t:
        rule_card(frame, 1265, "goat", "cabbage", scale=ease_out_back(prog(t, t5 + 0.1, t5 + 0.45)),
                  label="ZIEGE FRISST KOHL")
    return frame


Q_FEET = 1150


def scene_question(t):
    t0 = st("Wie bringt")
    t_pause = st("PAUSE")
    t_tip = st("Kleiner Tipp")
    t_cm = st("Schreib deine")
    img = vgradient(OUT_W, OUT_H, [(0, "#14213d"), (1, "#2b3f74")])
    cv = Canvas(img)
    rng = np.random.default_rng(1)
    for _ in range(70):
        x, y = rng.uniform(0, OUT_W), rng.uniform(0, OUT_H)
        tw = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv.circle(x, y, 2 + 2 * tw, fill=(255, 255, 255, int(80 + 100 * tw)))
    s = 1.9
    cvs = Canvas(img, -(OUT_W / 2) / s, -Q_FEET / s, s)
    cvs.ellipse(-70, -8, 70, 12, fill=(0, 0, 0, 70))
    draw_person(cvs, 0, 0, NIKLAS, face=1, reach=(30, -172))
    for k, name in enumerate(("wolf", "goat", "cabbage")):
        x, y, sc = 230 + k * 310, 1400, 1.0
        c2 = Canvas(img, -x / sc, -y / sc, sc)
        c2.ellipse(-90, -6, 90, 14, fill=(0, 0, 0, 70))
        draw_item(c2, name, 0, 0, 0.9, t, face=1)
    p = ease_out_back(prog(t, t0, t0 + 0.35))
    pill(img, OUT_W / 2, 360, "WIE KOMMEN", 92, bg="#fff6e6", scale=p, rot=-3)
    pill(img, OUT_W / 2, 515, "ALLE RÜBER?", 104, bg="#ffd34d", scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)), rot=2)
    if t_pause - 0.2 < t < t_tip:
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            cv.circle(OUT_W / 2 + 120 + i * 70, Q_FEET - 440 - i * 35, 20 + 10 * a,
                      fill=(255, 255, 255, int(120 + 135 * a)))
    if t > t_tip:
        sc = ease_out_back(prog(t, t_tip, t_tip + 0.35))
        pill(img, OUT_W / 2, 680, "TIPP: EIN SCHRITT ZURÜCK", 60, bg="#c5def5", scale=sc, rot=-2)
    if t > t_cm:
        sc = ease_out_back(prog(t, t_cm, t_cm + 0.35))
        pill(img, OUT_W / 2, 1255, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff", scale=sc)
    return img


def scene_solution(t):
    t0 = st("Hier kommt")
    t_warn = st("Aber Achtung")
    t_ok = st("Wolf und Kohl warten")
    t_done = st("Und alle drei")

    def actors(cv):
        draw_scene(cv, t, solution=True, niklas_in_boat=True)

    frame, view = render_world_frame(FULL, actors)
    if t < t0 + 1.6:
        pill(frame, OUT_W / 2, 360, "DIE LÖSUNG", 96, bg="#fff6e6", rot=-4,
             scale=ease_out_back(prog(t, t0, t0 + 0.35)) * (1 - prog(t, t0 + 1.3, t0 + 1.6)))
    cur = None
    for tr in TRIPS:
        if tr["t0"] - 0.05 <= t:
            cur = tr
    if cur and t0 + 1.6 < t < t_done:
        pill(frame, OUT_W / 2, 330, f"SCHRITT {cur['n']}/7:  {cur['label']}", 56, bg="#ffd34d", rot=-1.5)
    # rule check above the bank Niklas just left
    for tr in TRIPS:
        if tr["t0"] + LOAD < t < tr["t1"] - UNLOAD:
            left = [n for n in ("wolf", "goat", "cabbage") if side_of(n, t) == tr["frm"]]
            if len(left) >= 2:
                y = 640 if tr["frm"] == "L" else 1290
                check_icon(frame, group_x(tr["frm"]), y, 44, ok=True)
    if t_warn <= t < st("Also nimmt") + 0.4:
        check_icon(frame, (SLOTS["R"]["goat"] + SLOTS["R"]["cabbage"]) / 2, 1290, 50, ok=False,
                   scale=ease_out_back(prog(t, t_warn, t_warn + 0.3)))
        pill(frame, OUT_W / 2, 470, "ZIEGE + KOHL ALLEIN?  NEIN!", 50, bg="#e2574c", fg="#ffffff",
             scale=ease_out_back(prog(t, t_warn + 0.1, t_warn + 0.4)))
    if t_ok <= t < st("Dann fährt er wieder"):
        pill(frame, OUT_W / 2, 470, "WOLF + KOHL:  KEIN PROBLEM", 50, bg="#37b26c", fg="#ffffff",
             scale=ease_out_back(prog(t, t_ok, t_ok + 0.35)))
    if t >= t_done:
        pill(frame, OUT_W / 2, 330, "ALLE DREI SIND DRÜBEN!", 62, bg="#37b26c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, t_done, t_done + 0.35)))
        check_icon(frame, group_x("R"), 1290, 60, scale=ease_out_back(prog(t, t_done + 0.2, t_done + 0.5)))
    return frame


def scene_outro(t):
    t0 = st("Hättest")
    t1 = st("Schreib's")
    img = world().resize((OUT_W, OUT_H), Image.BILINEAR)
    img = ImageEnhance.Brightness(img).enhance(0.55)
    pill(img, OUT_W / 2, 520, "HÄTTEST DU'S", 96, bg="#fff6e6", rot=-3, scale=ease_out_back(prog(t, t0, t0 + 0.35)))
    pill(img, OUT_W / 2, 690, "GEWUSST?", 110, bg="#ffd34d", rot=2, scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)))
    if t > t1:
        pill(img, OUT_W / 2, 840, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff",
             scale=ease_out_back(prog(t, t1, t1 + 0.35)))
        followed = t > t1 + 2.0
        txt = "GEFOLGT  ✓" if followed else "+  FOLGEN"
        bg = "#37b26c" if followed else "#e2574c"
        pulse = 1 + (0.06 * math.sin(t * 10) if not followed else 0)
        pill(img, OUT_W / 2, 965, txt, 72, bg=bg, fg="#ffffff", scale=ease_out_back(prog(t, t1 + 0.4, t1 + 0.75)) * pulse)
        pill(img, OUT_W / 2, 1085, "MORGEN: NEUES RÄTSEL", 48, bg="#fff6e6",
             scale=ease_out_back(prog(t, t1 + 1.0, t1 + 1.35)))
    cv = Canvas(img)
    cv.ellipse(OUT_W / 2 - 330, 1462, OUT_W / 2 + 330, 1488, fill=(0, 0, 0, 90))
    draw_person(cv, 230, 1470, NIKLAS, face=1, wave=t * 9)
    for k, name in enumerate(("wolf", "goat", "cabbage")):
        draw_item(cv, name, 430 + k * 165, 1470, 0.75, t, face=-1)
    return img


SCENES = [
    (0.0, scene_story),
    (st("Wie bringt") - 0.05, scene_question),
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
