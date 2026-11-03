"""Rätsel #3 – Nils und die drei Lichtschalter.

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
from animals import draw_bulb, draw_switch

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# ------------------------------------------------------------------ layout (world units = screen px, image 2x)
W, H = OUT_W, OUT_H
ZW = 2
HOUSE = (80, 1000)                 # outer walls
EG_Y, OG_Y, DG_Y = 1440, 1110, 790  # floor levels (Erdgeschoss, Obergeschoss, Dachgeschoss)
EAVE_Y, PEAK = 640, (540, 300)
STAIR = (770, 975)
SW_X, SW_Y = (175, 232, 289), 1250  # light switches on the ground floor wall
BULB = (520, 590)
ANTH, WOOD, WOOD_D = "#2c2f38", "#b9804f", "#94603a"

NILS = Style(205, "#e9b48f", "#2b1d14", "#d9653b", "#2f3a56", shoes="#ffffff", hair_style="short", glasses=True,
             accent="#7a3420", under="#f4efe4", shoe_accent="#ffd34d")


def roof_y(x):
    """inner roof line (sloped) at x"""
    if x < PEAK[0]:
        return EAVE_Y - (x - HOUSE[0]) / (PEAK[0] - HOUSE[0]) * (EAVE_Y - PEAK[1])
    return EAVE_Y - (HOUSE[1] - x) / (HOUSE[1] - PEAK[0]) * (EAVE_Y - PEAK[1])


def draw_world():
    img = Image.new("RGB", (W * ZW, H * ZW))
    img.paste(vgradient(W * ZW, 1500 * ZW, [(0, "#14213d"), (0.3, "#2b3f74"), (0.55, "#6a6aa8"), (0.75, "#f08a5d"),
                                            (0.9, "#ffc178"), (1, "#ffc178")]), (0, 0))
    cv = Canvas(img, 0, 0, ZW)
    rng = np.random.default_rng(11)
    cv.circle(170, 1000, 80, fill=hexc("#ffe0a0"))
    for cx, cy, s in [(180, 260, 0.6), (900, 420, 0.5)]:
        col = (255, 214, 190, 90)
        cv.rect(cx - 220 * s, cy - 30 * s, cx + 220 * s, cy + 30 * s, fill=col, r=30 * s)
        cv.rect(cx - 120 * s, cy - 75 * s, cx + 90 * s, cy + 10 * s, fill=col, r=45 * s)
    far, near = hexc("#46507e"), hexc("#2a3157")
    for layer, col, base in ((0, far, 900), (1, near, 1050)):
        x = -40 + layer * 50
        while x < W:
            w = int(rng.integers(60, 130))
            top = base + int(rng.integers(-260, 120))
            cv.rect(x, top, x + w, EG_Y, fill=col)
            for wy in range(top + 16, EG_Y - 10, 26 if layer else 32):
                for wx in range(int(x) + 9, int(x + w) - 12, 19):
                    if rng.random() < 0.42:
                        cv.rect(wx, wy, wx + 10, wy + 14, fill=hexc("#ffd58a") if rng.random() < 0.7 else
                                mix(col, (255, 255, 255), 0.2))
            x += w + int(rng.integers(8, 34))
    # garden + street
    cv.rect(0, EG_Y, W, H, fill=hexc("#5f9a52"))
    cv.rect(0, EG_Y + 150, W, H, fill=hexc("#d9d6d0"))
    for k in range(0, W, 110):
        cv.rect(k, EG_Y + 150, k + 4, EG_Y + 330, fill=hexc("#c7c3bb"))
    cv.rect(0, EG_Y + 330, W, H, fill=hexc("#3b3f4a"))
    for x in range(0, W, 220):
        cv.rect(x + 30, EG_Y + 400, x + 150, EG_Y + 412, fill=hexc("#ffffff"))
    for _ in range(60):
        x, y = rng.uniform(0, W), rng.uniform(EG_Y + 20, EG_Y + 140)
        cv.line([(x, y), (x - 5, y - 16)], hexc("#6fae5a"), 4)

    anth, white = hexc(ANTH), hexc("#f3f1ec")
    # roof (dark tiles) + attic interior (wood)
    cv.poly([(HOUSE[0] - 40, EAVE_Y + 10), PEAK, (HOUSE[1] + 40, EAVE_Y + 10)], fill=anth)
    cv.poly([(HOUSE[0] - 40, EAVE_Y + 10), (PEAK[0], PEAK[1] - 26), (HOUSE[1] + 40, EAVE_Y + 10)], fill=hexc("#454955"))
    cv.poly([(HOUSE[0] + 22, EAVE_Y + 18), (PEAK[0], PEAK[1] + 30), (HOUSE[1] - 22, EAVE_Y + 18),
             (HOUSE[1] - 22, DG_Y), (HOUSE[0] + 22, DG_Y)], fill=hexc("#e2c49a"))
    for k in range(-6, 7):   # rafters
        x = PEAK[0] + k * 72
        cv.line([(x, max(roof_y(x) + 30, PEAK[1] + 30)), (x, DG_Y)], hexc("#d2b083"), 10, cap=False)
    cv.line([(HOUSE[0] + 40, 700), (HOUSE[1] - 40, 700)], hexc(WOOD), 16, cap=False)   # collar beam
    # attic props: boxes, round window
    for bx, bw, bh in ((150, 110, 80), (250, 80, 60), (860, 100, 70)):
        cv.rect(bx, DG_Y - bh, bx + bw, DG_Y, fill=hexc("#c9955e"))
        cv.rect(bx, DG_Y - bh, bx + bw, DG_Y - bh + 12, fill=hexc("#b07f4b"))
    cv.circle(PEAK[0], 420, 34, fill=hexc("#33406e"), outline=anth, width=8)
    # OG: office/bedroom
    cv.rect(HOUSE[0], DG_Y, HOUSE[1], OG_Y, fill=hexc("#e9eef3"))
    cv.rect(160, DG_Y + 70, 420, DG_Y + 230, fill=anth)
    cv.rect(170, DG_Y + 80, 410, DG_Y + 220, fill=hexc("#33406e"))
    for k in range(6):
        cv.rect(180 + k * 38, DG_Y + 160 - (k % 3) * 40, 196 + k * 38, DG_Y + 220, fill=hexc("#ffd58a"))
    cv.rect(286, DG_Y + 80, 294, DG_Y + 220, fill=anth)
    cv.rect(470, OG_Y - 120, 700, OG_Y - 104, fill=hexc(WOOD))          # desk
    cv.rect(480, OG_Y - 104, 490, OG_Y, fill=hexc(WOOD_D))
    cv.rect(680, OG_Y - 104, 690, OG_Y, fill=hexc(WOOD_D))
    cv.rect(560, OG_Y - 200, 650, OG_Y - 124, fill=anth, r=6)
    cv.rect(568, OG_Y - 192, 642, OG_Y - 134, fill=hexc("#6a8fd0"))
    cv.rect(110, OG_Y - 140, 150, OG_Y, fill=hexc("#d9653b"), r=8)
    for a in range(5):
        cv.circle(130 + (a - 2) * 14, OG_Y - 165 - (a % 2) * 18, 24, fill=hexc("#4f8a4c"))
    # EG: hallway with switches, door, coat rack, plant
    cv.rect(HOUSE[0], OG_Y, HOUSE[1], EG_Y, fill=hexc("#f6f1e8"))
    cv.rect(HOUSE[0], EG_Y - 60, HOUSE[1], EG_Y, fill=hexc("#ece4d6"))
    cv.rect(HOUSE[0] + 22, OG_Y + 60, HOUSE[0] + 36, EG_Y, fill=hexc(WOOD))
    cv.rect(540, EG_Y - 270, 680, EG_Y, fill=anth)
    cv.rect(552, EG_Y - 258, 668, EG_Y, fill=hexc(WOOD))
    for k in range(4):
        cv.rect(565 + k * 28, EG_Y - 246, 568 + k * 28, EG_Y - 10, fill=hexc(WOOD_D))
    cv.circle(650, EG_Y - 130, 6, fill=hexc("#d8dbe0"))
    cv.rect(445, EG_Y - 80, 505, EG_Y, fill=hexc("#d9653b"), r=8)          # plant
    for a in range(7):
        cv.circle(475 + (a - 3) * 13, EG_Y - 110 - (a % 3) * 22, 22, fill=hexc("#4f8a4c"))
    cv.rect(SW_X[0] - 40, SW_Y - 48, SW_X[2] + 40, SW_Y + 48, fill=hexc("#ffffff"), r=10)
    # stairs (zigzag, like video #1) on the right
    for (y0, y1) in ((EG_Y, OG_Y), (OG_Y, DG_Y)):
        a, m, b = (STAIR[0] + 10, y0), (STAIR[1] - 10, (y0 + y1) / 2), (STAIR[0] + 10, y1)
        for p0, p1 in ((a, m), (m, b)):
            cv.poly([p0, p1, (p1[0], p1[1] + 26), (p0[0], p0[1] + 26)], fill=hexc("#c9c5bc"))
            for s_ in range(8):
                f0, f1 = s_ / 8, (s_ + 1) / 8
                x0_, y0_ = p0[0] + (p1[0] - p0[0]) * f0, p0[1] + (p1[1] - p0[1]) * f0
                x1_, y1_ = p0[0] + (p1[0] - p0[0]) * f1, p0[1] + (p1[1] - p0[1]) * f1
                cv.line([(x0_, y0_), (x0_, y1_), (x1_, y1_)], hexc("#b4afa5"), 4, cap=False)
            cv.line([(p0[0], p0[1] - 80), (p1[0], p1[1] - 80)], anth, 6)
    # floor slabs + outer walls
    for y in (OG_Y, DG_Y):
        cv.rect(HOUSE[0], y - 4, HOUSE[1], y + 22, fill=white)
        cv.rect(HOUSE[0], y + 18, HOUSE[1], y + 24, fill=hexc("#dcd8d0"))
    cv.rect(HOUSE[0] - 10, EG_Y - 2, HOUSE[1] + 10, EG_Y + 26, fill=white)
    for x0 in (HOUSE[0] - 10, HOUSE[1] - 12):
        cv.rect(x0, EAVE_Y + 10, x0 + 22, EG_Y + 26, fill=white)
    # floor plates
    for y, lab in ((OG_Y + 26, "EG"), (DG_Y + 26, "OG"), (EAVE_Y + 40, "DG")):
        cv.rect(HOUSE[1] - 100, y + 10, HOUSE[1] - 34, y + 54, fill=anth, r=8)
        cv.text(HOUSE[1] - 67, y + 32, lab, 26, hexc("#ffffff"))
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
CAM_EG = (420, 1200, 1050)
CAM_DG = (560, 700, 1000)

# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Nils steht", "Einer davon", "Von unten", "Er darf die", "Aber er darf", "Wie findet", "PAUSE",
        "Kleiner Tipp", "Schreib deine", "Hier kommt", "Nils schaltet", "Dann schaltet", "Jetzt schaltet",
        "Leuchtet", "Ist sie aus, aber", "Denn sie", "Und ist sie", "Hättest", "Schreib's"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 2.6
XFADE = 0.25


def st(key):
    return S[K[key]]


def en(key):
    return E[K[key]]


# ------------------------------------------------------------------ actors
def draw_attic_light(cv, state, t):
    """darken the attic when the bulb is off, glow when on"""
    poly = [(HOUSE[0] + 22, EAVE_Y + 18), (PEAK[0], PEAK[1] + 30), (HOUSE[1] - 22, EAVE_Y + 18),
            (HOUSE[1] - 22, DG_Y), (HOUSE[0] + 22, DG_Y)]
    if state == "on":
        cv.poly(poly, fill=(255, 220, 140, 40))
    else:
        cv.poly(poly, fill=(14, 20, 50, 120 if state != "hidden" else 165))


def draw_bulb_world(cv, state, t):
    cv.line([(BULB[0], PEAK[1] + 40), (BULB[0], BULB[1] - 56)], hexc("#2c2f38"), 4, cap=False)
    draw_bulb(cv, BULB[0], BULB[1], 1.0, state if state != "hidden" else "off", t)


def draw_world_switches(cv, states):
    for k, x in enumerate(SW_X):
        draw_switch(cv, x, SW_Y, 0.85, on=states[k], label=str(k + 1))


def switch_panel(img, cx, cy, states, highlight=None, scale=1.0):
    """big switch panel overlay (screen space)"""
    if scale <= 0.01:
        return
    Z = 2
    w, h = 470, 230
    tile = Image.new("RGBA", (w * Z, h * Z), (0, 0, 0, 0))
    cv = Canvas(tile, 0, 0, Z)
    cv.rect(10, 16, w - 4, h - 2, fill=(30, 20, 60, 90), r=30)
    cv.rect(4, 4, w - 12, h - 14, fill=hexc("#f7f5f0"), r=30)
    for k in range(3):
        draw_switch(cv, 90 + k * 140, 130, 1.6, on=states[k], label=str(k + 1), highlight=(highlight == k))
    tile = tile.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    x0, y0 = int(cx - tile.width / 2), int(cy - tile.height / 2)
    img.paste(tile, (x0, y0), tile)
    log_ui("switch panel", x0, y0, x0 + tile.width, y0 + tile.height)


def case_row(img, cy, state, text, scale=1.0, bg="#fff6e6"):
    """result row: bulb icon + text"""
    if scale <= 0.01:
        return
    pill(img, OUT_W / 2 + 35, cy, text, 40, bg=bg, scale=scale, pad=(28, 16))
    c = Canvas(img, -(OUT_W / 2 - 290) / scale, -cy / scale - 10, scale)
    c.circle(0, 0, 52, fill=hexc("#22243a"))
    draw_bulb(Canvas(img, -(OUT_W / 2 - 290), -(cy + 12), 1.0), 0, 0, 0.9, state, 0.0)


def stair_keys(t0, dur):
    """Nils from the switches up both flights into the attic within dur seconds"""
    pts = [(380, EG_Y), (STAIR[0] + 10, EG_Y), (STAIR[1] - 10, (EG_Y + OG_Y) / 2), (STAIR[0] + 10, OG_Y),
           (STAIR[1] - 10, (OG_Y + DG_Y) / 2), (STAIR[0] + 10, DG_Y), (610, DG_Y)]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    tot = sum(seg)
    keys, t = [(t0, *pts[0])], t0
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        t += dur * L / tot
        keys.append((t, *b))
    return keys


# ------------------------------------------------------------------ scenes
def scene_story(t):
    t0, t1, t2, t3, t4 = st("Nils steht"), st("Einer davon"), st("Von unten"), st("Er darf die"), st("Aber er darf")
    cam = keyframes(t, [(t0, CAM_EG), (t1 - 0.05, CAM_EG), (t1 + 0.9, FULL), (t3 - 0.05, FULL), (t3 + 0.5, CAM_EG),
                        (t4 - 0.05, CAM_EG), (t4 + 0.6, FULL)])
    flick = [False, False, False]
    if t3 < t < t4:   # playing with the switches
        k = int((t - t3) * 3)
        flick = [(k + i) % 3 == 0 for i in range(3)]
    bulb_state = "on" if (t1 + 0.4 < t < t2) else "hidden" if t >= t2 else "off"

    def actors(cv):
        draw_attic_light(cv, bulb_state, t)
        draw_bulb_world(cv, bulb_state, t)
        draw_world_switches(cv, flick)
        reach = (SW_X[1], SW_Y) if t3 < t < t4 else None
        draw_person(cv, 380, EG_Y, NILS, face=-1 if t < t2 or t3 < t < t4 else 1, reach=reach)
        if t4 + 0.4 < t:   # dotted route up the stairs, once
            p = prog(t, t4 + 0.4, t4 + 1.4)
            keys = stair_keys(0, 1)
            n = int(30 * p)
            for k in range(n):
                x, y, _, _ = path_pos(k / 30, keys)
                cv.circle(x, y - 40, 7, fill=hexc("#ffd34d"))

    frame, view = render_world_frame(cam, actors)
    if t < t1:
        sx, sy = w2s(380, EG_Y - 260, view)
        pill(frame, sx, sy, "NILS", 56, bg="#ffd34d", rot=3, scale=ease_out_back(prog(t, t0 + 0.3, t0 + 0.6)))
        switch_panel(frame, OUT_W / 2, 560, [False] * 3, scale=ease_out_back(prog(t, t0 + 1.4, t0 + 1.8)))
    if t1 < t < t2 + 0.3:
        sx, sy = w2s(BULB[0], BULB[1] + 90, view)
        pill(frame, sx, sy, "GLÜHBIRNE IM DACHGESCHOSS", 40, bg="#fff6e6", scale=ease_out_back(prog(t, t1 + 0.5, t1 + 0.8)))
    if t2 <= t < t3:
        sx, sy = w2s(BULB[0], BULB[1] - 30, view)
        pill(frame, sx, sy, "?", 110, bg="#ffd34d", scale=ease_out_back(prog(t, t2 + 0.2, t2 + 0.5)))
        pill(frame, OUT_W / 2, 330, "VON UNTEN NICHT SICHTBAR", 52, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, t2 + 0.4, t2 + 0.75)))
    if t3 <= t < t4:
        switch_panel(frame, OUT_W / 2, 520, flick, scale=ease_out_back(prog(t, t3, t3 + 0.35)))
        pill(frame, OUT_W / 2, 330, "SCHALTEN: SO OFT ER WILL", 52, bg="#37b26c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, t3 + 0.2, t3 + 0.55)))
    if t4 <= t:
        pill(frame, OUT_W / 2, 330, "NUR 1× NACH OBEN!", 64, bg="#e2574c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, t4 + 0.3, t4 + 0.65)))
    return frame


Q_FEET = 1150


def scene_question(t):
    t0, t_pause, t_tip, t_cm = st("Wie findet"), st("PAUSE"), st("Kleiner Tipp"), st("Schreib deine")
    img = vgradient(OUT_W, OUT_H, [(0, "#14213d"), (1, "#2b3f74")])
    cv = Canvas(img)
    rng = np.random.default_rng(1)
    for _ in range(70):
        x, y = rng.uniform(0, OUT_W), rng.uniform(0, OUT_H)
        tw = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv.circle(x, y, 2 + 2 * tw, fill=(255, 255, 255, int(80 + 100 * tw)))
    s = 1.9
    cvs = Canvas(img, -(OUT_W / 2 - 170) / s, -Q_FEET / s, s)
    cvs.ellipse(-70, -8, 70, 12, fill=(0, 0, 0, 70))
    draw_person(cvs, 0, 0, NILS, face=1, reach=(30, -172))
    draw_bulb(Canvas(img), OUT_W / 2 + 180, 860, 2.2, "off", t)
    switch_panel(img, OUT_W / 2, 1330, [False] * 3, scale=0.9)
    p = ease_out_back(prog(t, t0, t0 + 0.35))
    pill(img, OUT_W / 2, 360, "WELCHER SCHALTER", 76, bg="#fff6e6", scale=p, rot=-3)
    pill(img, OUT_W / 2, 515, "IST DER RICHTIGE?", 82, bg="#ffd34d", scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)),
         rot=2)
    if t_pause - 0.2 < t < t_tip:
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            cv.circle(OUT_W / 2 - 50 + i * 70, Q_FEET - 440 - i * 35, 20 + 10 * a, fill=(255, 255, 255, int(120 + 135 * a)))
    if t > t_tip:
        pill(img, OUT_W / 2, 670, "TIPP: NICHT NUR LICHT …", 60, bg="#c5def5", rot=-2,
             scale=ease_out_back(prog(t, t_tip, t_tip + 0.35)))
    if t > t_cm:
        pill(img, OUT_W / 2, 1190, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff",
             scale=ease_out_back(prog(t, t_cm, t_cm + 0.35)))
    return img


def scene_solution(t):
    t0 = st("Hier kommt")
    a1, a2, a3 = st("Nils schaltet"), st("Dann schaltet"), st("Jetzt schaltet")
    c1, c2, c3, c4 = st("Leuchtet"), st("Ist sie aus, aber"), st("Denn sie"), st("Und ist sie")
    climb0 = a3 + 0.9
    climb_dur = clamp(c1 - climb0 - 0.15, 1.6, 3.2)
    keys = stair_keys(climb0, climb_dur)
    states = [False, False, False]
    hl = None
    if a1 + 0.3 <= t < a2 + 0.3:
        states, hl = [True, False, False], 0
    elif a2 + 0.3 <= t < a3 + 0.3:
        states, hl = [False, False, False], 0
    elif t >= a3 + 0.3:
        states, hl = [False, True, False], 1
    # which outcome we are showing upstairs
    if t < c1:
        bulb = "hidden"
    elif t < c2:
        bulb = "on"
    elif t < c4:
        bulb = "warm"
    else:
        bulb = "cold"
    if t < climb0 - 0.2:
        cam = CAM_EG
    elif t < c1:
        cam = keyframes(t, [(climb0 - 0.2, CAM_EG), (climb0 + 0.6, FULL), (c1 - 0.5, FULL), (c1, CAM_DG)])
    else:
        cam = CAM_DG

    def actors(cv):
        draw_attic_light(cv, bulb, t)
        draw_bulb_world(cv, bulb, t)
        draw_world_switches(cv, states)
        x, y, moving, dx = path_pos(t, keys)
        face = -1 if t < climb0 else (1 if dx > 0 else -1 if dx < 0 else -1)
        reach = None
        if t < climb0 and (a1 + 0.1 < t < a1 + 0.6 or a2 + 0.1 < t < a2 + 0.6 or a3 + 0.1 < t < a3 + 0.6):
            k = 0 if t < a3 else 1
            reach = (SW_X[k], SW_Y)
        if t >= c2 and bulb in ("warm", "cold"):   # touch the bulb
            reach = (BULB[0] + 22, BULB[1] + 12)
        draw_person(cv, x, y, NILS, face=face, phase=t * 11 if moving else None, reach=reach)

    frame, view = render_world_frame(cam, actors)
    if t < t0 + 1.4:
        pill(frame, OUT_W / 2, 330, "DIE LÖSUNG", 96, bg="#fff6e6", rot=-4,
             scale=ease_out_back(prog(t, t0, t0 + 0.35)) * (1 - prog(t, t0 + 1.1, t0 + 1.4)))
    if a1 <= t < climb0 + 0.3:
        switch_panel(frame, OUT_W / 2, 560, states, highlight=hl, scale=ease_out_back(prog(t, a1, a1 + 0.35)))
    if a1 + 0.4 <= t < a2:
        p = prog(t, a1 + 0.4, a2 - 0.2)
        mins = int(p * 5)
        clock_badge(frame, OUT_W / 2, 330, 18, int(p * 300) % 60 + 0, f"+{max(1, mins)} MIN",
                    scale=ease_out_back(prog(t, a1 + 0.4, a1 + 0.7)))
    if a2 <= t < a3:
        pill(frame, OUT_W / 2, 330, "SCHALTER 1 WIEDER AUS", 54, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, a2 + 0.2, a2 + 0.5)))
    if a3 <= t < c1:
        pill(frame, OUT_W / 2, 330, "SCHALTER 2 AN – UND HOCH!", 52, bg="#ffd34d", rot=-2,
             scale=ease_out_back(prog(t, a3 + 0.2, a3 + 0.5)))
    if c1 <= t:
        pill(frame, OUT_W / 2, 300, "IM DACHGESCHOSS …", 56, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, c1, c1 + 0.3)))
        case_row(frame, 1215, "on", "LEUCHTET  →  SCHALTER 2", scale=ease_out_back(prog(t, c1 + 0.4, c1 + 0.75)),
                 bg="#ffd34d")
    if c2 <= t:
        case_row(frame, 1320, "warm", "AUS + WARM  →  SCHALTER 1", scale=ease_out_back(prog(t, c2 + 0.6, c2 + 0.95)),
                 bg="#ffcfb0")
    if c3 <= t < c4:
        pill(frame, OUT_W / 2, 430, "SIE HAT JA MINUTEN GEBRANNT!", 46, bg="#e8663b", fg="#ffffff", rot=2,
             scale=ease_out_back(prog(t, c3, c3 + 0.35)))
    if c4 <= t:
        case_row(frame, 1425, "cold", "AUS + KALT  →  SCHALTER 3", scale=ease_out_back(prog(t, c4 + 0.5, c4 + 0.85)),
                 bg="#c5def5")
    return frame


def scene_outro(t):
    t0, t1 = st("Hättest"), st("Schreib's")
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
    cv.ellipse(OUT_W / 2 - 200, 1462, OUT_W / 2 + 200, 1488, fill=(0, 0, 0, 90))
    s = 1.3
    draw_person(Canvas(img, -(OUT_W / 2 - 80) / s, -1470 / s, s), 0, 0, NILS, face=1, wave=t * 9)
    draw_bulb(cv, OUT_W / 2 + 130, 1250, 1.6, "on", t)
    return img


SCENES = [
    (0.0, scene_story),
    (st("Wie findet") - 0.05, scene_question),
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
