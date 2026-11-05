"""Rätsel #4 – Dario und die zwei Eimer (genau 4 Liter abmessen).

usage:  python3 make_video.py            -> renders video.mp4 (needs timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
import toolkit as _tk
from animals import draw_citrus_slice, draw_apple_cube, draw_ice_cube, draw_orange_wedge

# High-contrast text boxes for the colourful party scene: light boxes become dark navy with a yellow
# frame, yellow boxes get a dark frame, green/red boxes a white frame. The question scene (dark
# background) keeps the normal channel style.
_PARTY_STYLE = {"on": True}
_NAVY = "#1d1b33"


def pill(img, cx, cy, text, size=64, fg="#2b2140", bg="#fff6e6", **kw):
    if _PARTY_STYLE["on"] and "border" not in kw:
        if bg in ("#fff6e6", "#ffffff"):
            bg, fg, kw["border"] = _NAVY, "#ffffff", "#ffd34d"
        elif bg == "#c5def5":
            bg, fg, kw["border"] = _NAVY, "#9fd2ff", "#9fd2ff"
        elif bg == "#ffd34d":
            kw["border"] = _NAVY
        else:
            kw["border"] = "#ffffff"
    return _tk.pill(img, cx, cy, text, size, fg=fg, bg=bg, **kw)



CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# ------------------------------------------------------------------ layout (world units = screen px, image 2x)
W, H = OUT_W, OUT_H
ZW = 2
M = 400                             # pixels per metre (real proportions)
FLOOR = 1460
TABLE = (30, 400, FLOOR - 0.75 * M)  # 75 cm table
BARREL = (682, 890, FLOOR - 0.42 * M - 0.72 * M)   # barrel (72 cm) on a 42 cm stand
STAND_TOP = FLOOR - 0.42 * M
TAP = (640, STAND_TOP - 40)         # tap outlet
STOOL_TOP = TAP[1] + 40 + 0.21 * M
FILL_SPOT = (TAP[0] + 2, STOOL_TOP)  # small bucket under the tap (bottom centre)
BUCKETS = {"big": dict(cap=5, bw=0.23 * M, tw=0.30 * M, h=0.26 * M, home=(115, TABLE[2]), straws=3),
           "small": dict(cap=3, bw=0.19 * M, tw=0.245 * M, h=0.21 * M, home=(295, TABLE[2]), straws=2)}
DRINK, DRINK_D = "#a3162f", "#7a0f22"
STREAM = (170, 28, 52, 235)
ANTH, WOOD, WOOD_D = "#2c2f38", "#b9804f", "#94603a"
DECK_DEPTH = 170
RAIL_TOP = FLOOR - DECK_DEPTH - 0.9 * M
PERSON_H = {"dario": 1.78 * M, "friend1": 1.66 * M * 0.86, "friend2": 1.74 * M * 0.86}

DARIO = Style(215, "#c98c62", "#1d1712", "#3f7fd9", "#2f3a56", shoes="#ffffff", hair_style="quiff",
              accent="#1f4f9a", under="#f4efe4", shoe_accent="#e2574c", beard=True)
FRIEND1 = Style(205, "#f6d2b8", "#e9b949", "#7d5bd0", "#2f3350", hair_style="long", under="#f3eefc", shoes="#2f3350")
FRIEND2 = Style(212, "#8d5a3b", "#1f1a24", "#e8a33a", "#46618f", hair_style="short", glasses=True, shoes="#f2f2f2")


def draw_world():
    img = Image.new("RGB", (W * ZW, H * ZW))
    img.paste(vgradient(W * ZW, 1200 * ZW, [(0, "#14213d"), (0.3, "#2b3f74"), (0.6, "#6a6aa8"), (0.82, "#f08a5d"),
                                            (1, "#ffc178")]), (0, 0))
    cv = Canvas(img, 0, 0, ZW)
    rng = np.random.default_rng(21)
    cv.circle(860, 980, 85, fill=hexc("#ffe0a0"))
    for cx, cy, s in [(200, 300, 0.6), (880, 470, 0.5)]:
        col = (255, 214, 190, 90)
        cv.rect(cx - 220 * s, cy - 30 * s, cx + 220 * s, cy + 30 * s, fill=col, r=30 * s)
        cv.rect(cx - 120 * s, cy - 75 * s, cx + 90 * s, cy + 10 * s, fill=col, r=45 * s)
    far, near = hexc("#46507e"), hexc("#2a3157")
    for layer, col, base in ((0, far, 700), (1, near, 860)):
        x = -40 + layer * 50
        while x < W:
            w = int(rng.integers(60, 140))
            top = base + int(rng.integers(-260, 120))
            cv.rect(x, top, x + w, 1200, fill=col)
            if rng.random() < 0.3:
                cv.rect(x + w * 0.45, top - 70, x + w * 0.55, top, fill=col)
            for wy in range(top + 16, 1190, 26 if layer else 32):
                for wx in range(int(x) + 9, int(x + w) - 12, 19):
                    if rng.random() < 0.42:
                        cv.rect(wx, wy, wx + 10, wy + 14, fill=hexc("#ffd58a") if rng.random() < 0.7 else
                                mix(col, (255, 255, 255), 0.2))
            x += w + int(rng.integers(8, 34))
    # terrace: glass railing, deck
    back = FLOOR - DECK_DEPTH                     # where the deck meets the railing (further back)
    rail = RAIL_TOP
    cv.rect(0, 1200, W, back, fill=hexc("#33406e"))
    cv.rect(0, rail, W, back, fill=(225, 235, 245, 70))
    cv.rect(0, rail - 8, W, rail + 4, fill=hexc(ANTH))
    for k in range(0, W, 160):
        cv.rect(k - 3, rail, k + 3, back, fill=hexc("#454955"))
    deck = vgradient(W * ZW, int(H - back) * ZW, [(0, "#9a6a42"), (DECK_DEPTH / (H - back), "#b9804f"), (1, "#8a5a36")])
    img.paste(deck, (0, int(back * ZW)))
    cv = Canvas(img, 0, 0, ZW)
    k = back + 14
    while k < H:      # planks get wider towards the front (perspective)
        cv.rect(0, k, W, k + 3, fill=hexc(WOOD_D))
        k += 18 if k < FLOOR else 60
    # planters
    # bunting (pennant garland) across the terrace
    cols = ["#e2574c", "#ffd34d", "#37b26c", "#3f7fd9", "#f08a5d", "#9b6fd1"]
    for row, (y0, sag) in enumerate(((540, 60), (610, 45))):
        pts = [(x, y0 + sag * math.sin(math.pi * x / W)) for x in range(-40, W + 60, 60)]
        cv.line(pts, hexc("#22243a"), 3, cap=False)
        for i, (x, y) in enumerate(pts[:-1]):
            cv.poly([(x + 4, y + 2), (x + 52, y + 4), (x + 28, y + 46)], fill=hexc(cols[(i + row * 2) % 6]))
    # speaker box
    cv.rect(960, FLOOR - 250, 1060, FLOOR, fill=hexc("#22243a"), r=10)
    for cy_, r_ in ((FLOOR - 190, 26), (FLOOR - 90, 40)):
        cv.circle(1010, cy_, r_, fill=hexc("#454955"))
        cv.circle(1010, cy_, r_ * 0.45, fill=hexc("#2c2f38"))
    for px in (40,):
        cv.rect(px - 50, FLOOR - 160, px + 50, FLOOR, fill=hexc(ANTH), r=8)
        for a in range(7):
            cv.circle(px + (a - 3) * 16, FLOOR - 200 - (a % 3) * 34, 36, fill=hexc("#4f8a4c"))
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
CAM = (480, 1068, 1707)


# ------------------------------------------------------------------ props
def string_lights(cv, t):
    pts = [(x, 420 + 70 * math.sin(math.pi * x / W)) for x in range(-20, W + 40, 40)]
    cv.line(pts, hexc("#22243a"), 3, cap=False)
    for i, (x, y) in enumerate(pts[1::2]):
        on = 0.75 + 0.25 * math.sin(t * 3 + i)
        cv.circle(x, y + 14, 16, fill=(255, 214, 110, int(60 * on)))
        cv.circle(x, y + 12, 8, fill=hexc("#ffe4a0"))


def draw_barrel(cv, t, stream_to=None):
    x0, x1, top = BARREL
    cx = (x0 + x1) / 2
    bot = STAND_TOP
    # stand
    cv.rect(x0 + 10, bot - 10, x1 - 10, bot + 12, fill=hexc(ANTH), r=4)
    for lx in (x0 + 24, x1 - 40):
        cv.rect(lx, bot, lx + 16, FLOOR, fill=hexc(ANTH))
    cv.line([(x0 + 32, FLOOR - 40), (x1 - 32, bot + 30)], hexc("#454955"), 8)
    # barrel body (bulging)
    cv.ellipse(x0 - 18, top + 12, x1 + 18, bot + 6, fill=hexc("#a86f40"))
    cv.rect(x0 - 6, top + 24, x1 + 6, bot - 8, fill=hexc(WOOD))
    for k in range(7):
        xx = x0 + 12 + k * (x1 - x0 - 24) / 6
        cv.rect(xx - 2, top + 24, xx + 2, bot - 8, fill=hexc(WOOD_D))
    for yy in (top + 50, (top + bot) / 2, bot - 44):
        cv.rect(x0 - 12, yy - 9, x1 + 12, yy + 9, fill=hexc("#5d6270"), r=4)
    cv.ellipse(x0 - 4, top, x1 + 4, top + 46, fill=hexc("#8a5a36"))
    cv.ellipse(x0 + 12, top + 8, x1 - 12, top + 38, fill=hexc(DRINK_D))
    # label
    lx = cx - 20                     # label kept left of TikTok's icon column
    cv.rect(lx - 56, top + 112, lx + 56, top + 190, fill=hexc("#f7f1e6"), r=10)
    cv.text(lx, top + 140, "SANGRIA", 23, hexc(DRINK_D))
    for k, kind in enumerate(("orange", "lemon", "orange")):
        draw_citrus_slice(cv, lx - 24 + k * 24, top + 168, 9, kind, flat=1.0, rot=k)
    # tap (brass) with lever
    opened = stream_to is not None
    ty = TAP[1]
    cv.rect(TAP[0] - 8, ty - 40, x0 + 6, ty - 22, fill=hexc("#c9a24a"), r=5)
    cv.rect(TAP[0] - 12, ty - 44, TAP[0] + 16, ty - 4, fill=hexc("#b8902f"), r=6)
    cv.rect(TAP[0] - 6, ty - 8, TAP[0] + 10, ty + 4, fill=hexc("#8f6f22"), r=3)
    ang = math.radians(-60 if opened else 0)
    lx, ly = TAP[0] + 2, ty - 44
    cv.line([(lx, ly), (lx + math.sin(ang) * 56, ly - math.cos(ang) * 56)], hexc("#22243a"), 10)
    cv.circle(lx + math.sin(ang) * 56, ly - math.cos(ang) * 56, 9, fill=hexc("#e2574c"))
    if opened:
        cv.line([(TAP[0] + 2, ty + 2), (TAP[0] + 2, stream_to)], STREAM, 9, cap=False)
    # stool under the tap
    cv.rect(FILL_SPOT[0] - 62, STOOL_TOP, FILL_SPOT[0] + 62, STOOL_TOP + 16, fill=hexc(WOOD), r=4)
    for lx in (FILL_SPOT[0] - 52, FILL_SPOT[0] + 40):
        cv.rect(lx, STOOL_TOP + 16, lx + 12, FLOOR, fill=hexc(WOOD_D))


def draw_table(cv):
    x0, x1, top = TABLE
    cv.rect(x0, top, x1, top + 22, fill=hexc(WOOD), r=6)
    cv.rect(x0, top + 18, x1, top + 26, fill=hexc(WOOD_D))
    for lx in (x0 + 24, x1 - 38):
        cv.rect(lx, top + 22, lx + 14, FLOOR, fill=hexc(ANTH))
    for k, cx in enumerate((x0 + 30, x1 - 30)):   # glasses for the friends (12 cm)
        gh = 0.12 * M
        cv.poly([(cx - 17, top - gh), (cx + 17, top - gh), (cx + 13, top), (cx - 13, top)], fill=(230, 240, 248, 140))
        cv.poly([(cx - 15, top - gh * 0.6), (cx + 15, top - gh * 0.6), (cx + 13, top - 2), (cx - 13, top - 2)],
                fill=hexc(DRINK))
        draw_orange_wedge(cv, cx + 12, top - gh * 0.9, 11)


def _rot(pts, ang, piv):
    c, s = math.cos(ang), math.sin(ang)
    return [(piv[0] + (x - piv[0]) * c - (y - piv[1]) * s, piv[1] + (x - piv[0]) * s + (y - piv[1]) * c) for x, y in pts]


STRAW_COLS = ("#ff6b6b", "#ffd34d", "#3f7fd9", "#37b26c")
# fruit pieces inside the sangria: (kind, u = -0.5..0.5 across, v = height fraction, size, rotation)
FRUIT = {"big": [("orange", -0.18, 0.22, 15, 0.2), ("apple", 0.22, 0.12, 9, 0.4), ("lemon", 0.2, 0.48, 12, 0.6),
                 ("apple", -0.25, 0.55, 8, -0.3), ("ice", 0.02, 0.7, 10, 0.25), ("orange", -0.08, 0.78, 13, 1.0)],
         "small": [("orange", 0.12, 0.25, 12, 0.3), ("apple", -0.2, 0.18, 7, 0.7), ("lemon", -0.12, 0.6, 10, 0.1),
                   ("ice", 0.18, 0.66, 8, -0.2)]}
FLOAT = {"big": [("orange", -0.2, 17, 0.4), ("lemon", 0.22, 14, 0.9)], "small": [("orange", 0.12, 14, 0.2)]}


def draw_bucket(cv, name, bx, by, liters, tilt=0.0):
    """transparent bucket, bottom centre (bx, by); tilt in radians (+ = pours to the right)"""
    b = BUCKETS[name]
    bw, tw, h = b["bw"], b["tw"], b["h"]
    piv = (bx + (tw / 2 if tilt >= 0 else -tw / 2), by - h)       # pour lip
    R = lambda pts: _rot(pts, tilt, piv)
    body = [(bx - tw / 2, by - h), (bx + tw / 2, by - h), (bx + bw / 2, by), (bx - bw / 2, by)]
    frac = clamp(liters / b["cap"], 0, 1)
    # straws (behind the front wall)
    for k in range(b["straws"]):
        sx = bx - bw * 0.25 + k * bw * 0.5 / max(1, b["straws"] - 1)
        lean = (-0.35 + k * 0.3)
        top = (sx + lean * h * 0.9, by - h * 1.45)
        cv.line(R([(sx, by - 6), top]), hexc(STRAW_COLS[(k + (name == "small")) % 4]), 7, cap=False)
        cv.line(R([(top[0] - lean * 18, top[1] + 18), top]), hexc("#ffffff"), 7, cap=False)
    if frac > 0.002:
        ly = by - h * frac
        wl = bw + (tw - bw) * frac
        W_at = lambda v: bw + (tw - bw) * v          # inner width at height fraction v
        # liquid with depth gradient (darker towards the bottom)
        bands = 6
        for i in range(bands):
            v0, v1 = frac * i / bands, frac * (i + 1) / bands
            col = mix(hexc("#5e0a1e"), hexc("#b21d38"), (i + 1) / bands)
            y0, y1 = by - h * v0, by - h * v1
            cv.poly(R([(bx - W_at(v1) / 2, y1), (bx + W_at(v1) / 2, y1), (bx + W_at(v0) / 2, y0 + 0.5),
                       (bx - W_at(v0) / 2, y0 + 0.5)]), fill=col)
        # fruit sunk in the drink (only where the drink already reaches)
        for (kind, u, v, sz, rot) in FRUIT[name]:
            if v + sz / h * 0.9 > frac:
                continue
            fx, fy = bx + u * W_at(v), by - h * v
            p = R([(fx, fy)])[0]
            if kind == "apple":
                draw_apple_cube(cv, p[0], p[1], sz * 0.55, rot + tilt)
            elif kind == "ice":
                draw_ice_cube(cv, p[0], p[1], sz * 0.6, rot + tilt)
            else:
                draw_citrus_slice(cv, p[0], p[1], sz, kind, flat=1.0, rot=rot)
        # tiny rising bubbles
        for i in range(4):
            u = -0.3 + i * 0.2
            vv = (0.15 + i * 0.21) % 1 * frac
            p = R([(bx + u * W_at(vv), by - h * vv)])[0]
            cv.circle(p[0], p[1], 2.2, fill=(255, 220, 225, 150))
        # shiny surface + side highlight
        cv.line(R([(bx - wl / 2 + 3, ly + 2), (bx + wl / 2 - 3, ly + 2)]), hexc("#d4485f"), 5, cap=False)
        cv.line(R([(bx - wl / 2 + 8, ly + 8), (bx - bw / 2 + 8, by - 6)]), (255, 255, 255, 60), 5, cap=False)
        # slices floating on top, seen at an angle
        if frac > 0.15:
            for (kind, u, sz, rot) in FLOAT[name]:
                p = R([(bx + u * wl, ly + 2)])[0]
                draw_citrus_slice(cv, p[0], p[1], sz, kind, flat=0.42, rot=rot)
    cv.poly(R(body), fill=(210, 230, 245, 32))
    cv.line(R(body + [body[0]]), hexc("#9fb3c8"), 4, joint="curve", cap=False)
    cv.line(R([(bx - tw / 2 - 4, by - h), (bx + tw / 2 + 4, by - h)]), hexc("#7f93a8"), 7)
    hp = R([(bx - tw / 2 + 5 + k * (tw - 10) / 10, by - h - 0.33 * tw * math.sin(math.pi * k / 10)) for k in range(11)])
    cv.line(hp, hexc("#5d6270"), 4, cap=False)
    return R([(bx + (tw / 2 if tilt >= 0 else -tw / 2), by - h)])[0]


# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Dario will", "Das Getränk", "Zum Abmessen", "Und die Eimer", "Wie bekommt", "PAUSE", "Kleiner Tipp",
        "Schreib deine", "Hier kommt", "Dario füllt", "Dann füllt", "Da nur noch", "Jetzt kippt", "Und gießt",
        "Zum Schluss", "Eins plus drei", "Hättest", "Schreib's"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 2.6
XFADE = 0.25


def st(key):
    return S[K[key]]


def build_actions():
    """(t0, t1, kind, src, dst, amount) – kinds: fill, pour, empty"""
    acts = []

    def span(key, nxt, parts):
        a, b = st(key) + 0.05, st(nxt) - 0.1
        d = (b - a) / parts
        return [(a + i * d, a + (i + 1) * d) for i in range(parts)]

    (f1, p1) = span("Dario füllt", "Dann füllt", 2)
    acts += [(*f1, "fill", "small", None, 3), (*p1, "pour", "small", "big", 3)]
    (f2, p2) = span("Dann füllt", "Da nur noch", 2)
    acts += [(*f2, "fill", "small", None, 3), (*p2, "pour", "small", "big", 2)]
    (e1,) = span("Jetzt kippt", "Und gießt", 1)
    acts += [(*e1, "empty", "big", None, 5)]
    (p3,) = span("Und gießt", "Zum Schluss", 1)
    acts += [(*p3, "pour", "small", "big", 1)]
    (f3, p4) = span("Zum Schluss", "Eins plus drei", 2)
    acts += [(*f3, "fill", "small", None, 3), (*p4, "pour", "small", "big", 3)]
    return acts


ACTIONS = build_actions()


def bucket_states(t):
    """returns per bucket dict(x, y, liters, tilt), plus stream info"""
    lv = {"big": 0.0, "small": 0.0}
    pos = {n: BUCKETS[n]["home"] for n in BUCKETS}
    tilt = {n: 0.0 for n in BUCKETS}
    streams = []
    tap_to = None
    for (t0, t1, kind, src, dst, amt) in ACTIONS:
        if t < t0:
            break
        p = prog(t, t0, t1)
        home = BUCKETS[src]["home"]
        if kind == "fill":
            spot = FILL_SPOT
            if p < 0.25:
                q = smooth(p / 0.25)
                pos[src] = (home[0] + (spot[0] - home[0]) * q, home[1] + (spot[1] - home[1]) * q - math.sin(math.pi * q) * 40)
            elif p < 0.78:
                pos[src] = spot
                q = (p - 0.25) / 0.53
                lv[src] = amt * smooth(q)
                tap_to = spot[1] - BUCKETS[src]["h"] * lv[src] / BUCKETS[src]["cap"] + 4
                if t >= t1:
                    tap_to = None
            else:
                lv[src] = amt
                q = smooth((p - 0.78) / 0.22)
                pos[src] = (spot[0] + (home[0] - spot[0]) * q, spot[1] + (home[1] - spot[1]) * q - math.sin(math.pi * q) * 40)
            if t >= t1:
                lv[src], pos[src] = amt, home
        else:
            sb = BUCKETS[src]
            if kind == "pour":
                db = BUCKETS[dst]
                dtop_y = pos[dst][1] - db["h"]
                direction = 1 if home[0] < pos[dst][0] else -1
                lip = (pos[dst][0] - direction * (db["tw"] / 2 - 26), dtop_y - 34)
                target_top = (pos[dst][0], dtop_y + 10)
            else:   # empty into the barrel (to the right)
                cx = (BARREL[0] + BARREL[1]) / 2
                direction = 1
                lip = (cx - 30, BARREL[2] - 26)
                target_top = (cx, BARREL[2] + 30)
            lift = (lip[0] - direction * sb["tw"] / 2, lip[1] + sb["h"])
            src_start = lv[src]
            dst_start = lv[dst] if dst else 0
            if p < 0.22:
                q = smooth(p / 0.22)
                pos[src] = (home[0] + (lift[0] - home[0]) * q,
                            home[1] + (lift[1] - home[1]) * q - math.sin(math.pi * q) * 60)
            else:
                pos[src] = lift
                tq = smooth(prog(p, 0.22, 0.34)) * (1 - smooth(prog(p, 0.78, 0.88)))
                tilt[src] = direction * 1.6 * tq
                q = smooth(prog(p, 0.34, 0.76))
                lv[src] = src_start - amt * q
                if dst:
                    lv[dst] = dst_start + amt * q
                if 0.34 <= p < 0.78:
                    streams.append((src, target_top))
                if p >= 0.88:
                    q2 = smooth((p - 0.88) / 0.12)
                    pos[src] = (lift[0] + (home[0] - lift[0]) * q2,
                                lift[1] + (home[1] - lift[1]) * q2 - math.sin(math.pi * q2) * 60)
            if t >= t1:
                pos[src], tilt[src] = home, 0.0
                lv[src] = src_start - amt
                if dst:
                    lv[dst] = dst_start + amt
    return pos, lv, tilt, streams, tap_to


def fmt_l(v):
    v = max(0.0, v)
    if abs(v - round(v)) < 0.04:
        return f"{int(round(v))} L"
    return f"{v:.1f} L".replace(".", ",")


BPM = 104
BEAT = BPM / 60


def beat_bob(t, amp, ph=0.0):
    return abs(math.sin(math.pi * BEAT * t + ph)) * amp


def blinking(t, seed):
    period = 3.1 + seed * 0.7
    return ((t + seed * 1.37) % period) < 0.13


GUEST_STYLES = [Style(200, "#c9a58c", "#3a3348", "#5a5f8a", "#2f3350", hair_style="short"),
                Style(200, "#8a6a5a", "#2a2230", "#7a5a8a", "#3a3350", hair_style="long"),
                Style(200, "#d9b49a", "#5a4a3a", "#4a7a7a", "#2f3a46", hair_style="quiff")]


def party_background(cv, t, finale=0.0):
    """subtle background motion: fireworks, balloons, dancing guests, speaker pulse"""
    # small, faint fireworks in the sky
    for k in range(3):
        period = 6.0
        tt = (t + k * 2.1) % period
        if tt < 1.4:
            rng = np.random.default_rng(int((t + k * 2.1) // period) * 7 + k)
            fx, fy = rng.uniform(150, 900), rng.uniform(170, 380)
            col = [(255, 211, 77), (240, 138, 93), (159, 210, 240), (200, 170, 255)][int(rng.integers(0, 4))]
            r = 25 + tt * 70
            a = int(110 * (1 - tt / 1.4))
            for i in range(12):
                ang = i / 12 * 2 * math.pi
                cv.line([(fx + math.cos(ang) * r * 0.55, fy + math.sin(ang) * r * 0.55 + tt * 12),
                         (fx + math.cos(ang) * r, fy + math.sin(ang) * r + tt * 18)], col + (a,), 3, cap=False)
    # balloon clusters tied to the railing
    rail = RAIL_TOP
    for bx0, cols in ((70, ("#e2574c", "#ffd34d", "#3f7fd9")), (1000, ("#37b26c", "#e98aa0", "#ffd34d"))):
        for i, c in enumerate(cols):
            ox = (i - 1) * 34 + 6 * math.sin(t * 0.9 + i)
            oy = -170 - (i % 2) * 50 + 5 * math.sin(t * 1.3 + i * 2)
            bxx, byy = bx0 + ox, rail + oy
            cv.line([(bx0, rail), (bxx, byy + 36)], (240, 240, 240, 160), 2, cap=False)
            cv.ellipse(bxx - 28, byy - 34, bxx + 28, byy + 34, fill=hexc(c))
            cv.ellipse(bxx - 14, byy - 22, bxx - 4, byy - 6, fill=(255, 255, 255, 90))
    # dancing guests further back (smaller, muted, slow)
    for i, (gx, st_) in enumerate(((455, GUEST_STYLES[0]), (640, GUEST_STYLES[1]), (595, GUEST_STYLES[2]))):
        gh = 1.7 * M * 0.62
        draw_person(cv, gx, FLOOR - 120, st_, face=1 if i % 2 else -1, h=gh,
                    bounce=beat_bob(t, 6, i), lean=8 * math.sin(t * 1.7 + i),
                    arms_up=0.15 + 0.25 * abs(math.sin(math.pi * BEAT * t / 2 + i)) + finale * 0.5)
    cv.rect(0, FLOOR - 160, W, FLOOR - 100, fill=(51, 64, 110, 0))
    # speaker pulse
    p = beat_bob(t, 1.0)
    cv.circle(1010, FLOOR - 90, 18 + 6 * p, fill=hexc("#5d6270"))


# big opening fireworks (first ~2.7 s): (launch time, x, burst y, colour)
INTRO_FIREWORKS = [(0.05, 300, 380, (255, 211, 77)), (0.40, 780, 320, (255, 105, 120)),
                   (0.75, 540, 460, (110, 200, 255)), (1.10, 200, 300, (200, 150, 255)),
                   (1.40, 860, 430, (110, 235, 160)), (1.70, 600, 290, (255, 165, 80))]
FW_LAUNCH, FW_BURST = 0.35, 1.0


def big_fireworks(cv, t):
    for (t0, fx, fy, col) in INTRO_FIREWORKS:
        tt = t - t0
        if tt < 0 or tt > FW_LAUNCH + FW_BURST:
            continue
        if tt < FW_LAUNCH:     # rising rocket with trail
            q = tt / FW_LAUNCH
            y = 980 + (fy - 980) * (1 - (1 - q) ** 2)
            cv.line([(fx, y + 70), (fx, y)], col + (160,), 5, cap=False)
            cv.circle(fx, y, 7, fill=(255, 250, 230, 230))
            continue
        q = (tt - FW_LAUNCH) / FW_BURST           # explosion
        r = 50 + 270 * (1 - (1 - q) ** 3)
        a = int(250 * (1 - q) ** 1.2)
        if q < 0.12:
            cv.circle(fx, fy, 60 * (1 - q / 0.12) + 20, fill=(255, 255, 240, int(170 * (1 - q / 0.12))))
        for ring, (n_, rf, wid) in enumerate(((36, 1.0, 7), (24, 0.6, 5))):
          for i in range(n_):
            ang = i / n_ * 2 * math.pi + (i % 2) * 0.06 + ring * 0.13
            rr = r * rf * (0.82 + 0.18 * ((i * 7) % 5) / 4)
            drop = 70 * q * q
            x1, y1 = fx + math.cos(ang) * rr, fy + math.sin(ang) * rr + drop
            x0, y0 = fx + math.cos(ang) * rr * 0.7, fy + math.sin(ang) * rr * 0.7 + drop * 0.7
            c_ = col if ring == 0 else (255, 245, 220)
            cv.line([(x0, y0), (x1, y1)], c_ + (a,), wid, cap=False)
            if q > 0.3 and (i + int(t * 20)) % 3 == 0:   # twinkling sparks
                cv.circle(x1, y1 + 10, 5, fill=(255, 250, 220, a))
        cv.circle(fx, fy, 220 * q + 40, fill=col + (int(40 * (1 - q)),))


def confetti(cv, t, t0):
    if t < t0:
        return
    rng = np.random.default_rng(12)
    n = 70
    xs, sp, ph = rng.uniform(0, W, n), rng.uniform(380, 620, n), rng.uniform(0, 6.28, n)
    cols = ["#e2574c", "#ffd34d", "#37b26c", "#3f7fd9", "#f08a5d", "#9b6fd1"]
    for i in range(n):
        y = -40 + (t - t0) * sp[i]
        if y > FLOOR:
            continue
        x = xs[i] + 30 * math.sin((t - t0) * 3 + ph[i])
        a = (t - t0) * 6 + ph[i]
        cv.poly([(x + math.cos(a) * 12, y + math.sin(a) * 5), (x - math.sin(a) * 6, y + math.cos(a) * 9),
                 (x - math.cos(a) * 12, y - math.sin(a) * 5), (x + math.sin(a) * 6, y - math.cos(a) * 9)],
                fill=hexc(cols[i % 6]))


DARIO_HOME = 515


def dario_track():
    """Dario walks to the bucket he works with: (time, x, y) keys"""
    keys = [(0.0, DARIO_HOME, FLOOR)]
    for (t0, t1, kind, src, dst, amt) in ACTIONS:
        tx = 535 if kind == "fill" else (430 if kind == "pour" else 560)
        keys += [(t0, keys[-1][1], FLOOR), (t0 + min(0.6, (t1 - t0) * 0.2), tx, FLOOR), (t1, tx, FLOOR)]
    keys += [(ACTIONS[-1][1] + 0.7, DARIO_HOME, FLOOR)]
    return keys


DARIO_KEYS = dario_track()


def draw_friends(cv, t, cheer):
    # friend 2 (left) talks, friend 1 (right) listens; both hold sangria and toast now and then
    for i, (x, st_, face, hk) in enumerate(((120, FRIEND2, 1, "friend2"), (300, FRIEND1, -1, "friend1"))):
        h = PERSON_H[hk]
        sh_y = FLOOR - (st_.leg + st_.torso) * h
        toast = smooth(prog((t + i * 0.3) % 7.0, 5.2, 5.7)) * (1 - smooth(prog((t + i * 0.3) % 7.0, 6.3, 6.8)))
        sip = smooth(prog((t + i * 2.5) % 9.0, 3.0, 3.5)) * (1 - smooth(prog((t + i * 2.5) % 9.0, 4.2, 4.7)))
        hx = x + face * (40 + 30 * toast) + (-face * 10 * sip)
        hy = sh_y + 95 - 120 * toast - 70 * sip
        talk = (0.5 + 0.5 * math.sin(t * 13)) if (i == 0 and (t % 5.0) < 2.4) else 0.0
        reach = None if cheer > 0.05 else (hx, hy)
        draw_person(cv, x, FLOOR, st_, face=face, h=h, bounce=beat_bob(t, 4, i * 0.8),
                    lean=5 * math.sin(t * 1.1 + i * 1.7), blink=blinking(t, i + 1), talk=talk, cup=DRINK,
                    reach=reach, arms_up=cheer * (0.6 + 0.4 * abs(math.sin(t * 6 + i))))


def draw_scene(cv, t, solution=True, dario_face=1, cheer=0.0, intro=False):
    if intro:
        big_fireworks(cv, t)
    string_lights(cv, t)
    party_background(cv, t, cheer)
    draw_friends(cv, t, cheer)
    if solution:
        pos, lv, tilt, streams, tap_to = bucket_states(t)
    else:
        pos = {n: BUCKETS[n]["home"] for n in BUCKETS}
        lv, tilt, streams, tap_to = {"big": 0, "small": 0}, {"big": 0, "small": 0}, [], None
    draw_barrel(cv, t, stream_to=tap_to)
    # Dario: walks to the bucket he handles and grabs its handle
    if solution:
        dx_, dy_, moving, ddx = path_pos(t, DARIO_KEYS)
    else:
        dx_, moving, ddx = DARIO_HOME, False, 0
    reach, face = None, dario_face
    active = [a for a in ACTIONS if a[0] <= t < a[1]] if solution else []
    if active and cheer < 0.05:
        src = active[0][3]
        b = BUCKETS[src]
        bx, by = pos[src]
        reach = (bx + (b["tw"] * 0.25 if bx > dx_ else -b["tw"] * 0.25) * 0, by - b["h"] - 0.2 * b["tw"])
        face = 1 if bx > dx_ else -1
    elif moving:
        face = 1 if ddx > 0 else -1
    draw_person(cv, dx_, FLOOR, DARIO, face=face, h=PERSON_H["dario"], phase=t * 9 if moving else None,
                bounce=0 if moving else beat_bob(t, 4, 2), lean=0 if reach else 4 * math.sin(t * 0.9),
                blink=blinking(t, 0), reach=reach, arm_scale=1.15,
                arms_up=cheer * (0.6 + 0.4 * abs(math.sin(t * 6 + 2))))
    draw_table(cv)
    lips = {}
    order = sorted(BUCKETS, key=lambda n: 1 if tilt[n] else 0)   # pouring bucket in front
    for n in order:
        lips[n] = draw_bucket(cv, n, pos[n][0], pos[n][1], lv[n], tilt[n])
    for src, target in streams:
        lip = lips[src]
        d = 1 if tilt[src] > 0 else -1
        cv.line([lip, (lip[0] + d * 10, lip[1] + 18), (lip[0] + d * 14, target[1] + 6)], STREAM, 9)
    if solution:
        confetti(cv, t, st("Eins plus drei") + 0.1)
    return pos, lv


# ------------------------------------------------------------------ overlays
def level_pills(img, view, pos, lv, scale=1.0, show=("big", "small")):
    for n in show:
        b = BUCKETS[n]
        x, y = pos[n]
        hx, hy = b["home"]
        if abs(y - hy) > 15 and abs(y - FILL_SPOT[1]) > 15:     # lifted: label beside the bucket
            sx, sy = w2s(x - b["tw"] / 2 - 70, y - b["h"] * 0.5, view)
        else:
            sx, sy = w2s(x, y + 45, view)
        bg = "#37b26c" if (abs(lv[n] - 4) < 0.04 and n == "big") else "#ffffff"
        fg = "#ffffff" if bg == "#37b26c" else "#22243a"
        pill(img, clamp(sx, 125, 840), min(sy, 1430), fmt_l(lv[n]), 44, bg=bg, fg=fg, pad=(22, 10), scale=scale)


def cap_labels(img, view, scale):
    for n in BUCKETS:
        x, y = BUCKETS[n]["home"]
        sx, sy = w2s(x, y - BUCKETS[n]["h"] * 1.5 - 60, view)
        pill(img, sx, sy, f"{BUCKETS[n]['cap']} L", 50, bg="#ffd34d", pad=(20, 10), scale=scale)


# ------------------------------------------------------------------ scenes
def scene_story(t):
    t0, t1, t2, t3 = st("Dario will"), st("Das Getränk"), st("Zum Abmessen"), st("Und die Eimer")
    cam = keyframes(t, [(t0, FULL), (t0 + 1.2, FULL), (t1, CAM)])

    def actors(cv):
        draw_scene(cv, t, solution=False, dario_face=1, intro=t < 3.2)

    frame, view = render_world_frame(cam, actors)
    if t < t1 + 0.2:
        out = 1 - prog(t, t1 - 0.1, t1 + 0.2)
        sx, sy = w2s(515, FLOOR - PERSON_H['dario'] - 60, view)
        pill(frame, sx, sy, "DARIO", 52, bg="#ffd34d", rot=3, scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.5)) * out)
        pill(frame, OUT_W / 2, 330, "ZIEL: GENAU 4 LITER", 60, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, t0 + 1.0, t0 + 1.35)) * out)
    if t1 <= t < t2 + 0.2:
        sx, sy = w2s((BARREL[0] + BARREL[1]) / 2, BARREL[2] - 60, view)
        pill(frame, min(sx, 760), sy, "DAS FASS", 48, bg="#fff6e6", rot=-3, scale=ease_out_back(prog(t, t1, t1 + 0.35)))
    if t2 <= t:
        cap_labels(frame, view, ease_out_back(prog(t, t2 + 0.6, t2 + 0.95)))
    if t3 <= t:
        pill(frame, OUT_W / 2, 330, "KEINE MARKIERUNGEN!", 58, bg="#e2574c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, t3 + 0.2, t3 + 0.55)))
    return frame


Q_FEET = 1150


def scene_question(t):
    _PARTY_STYLE["on"] = False
    try:
        return _scene_question(t)
    finally:
        _PARTY_STYLE["on"] = True


def _scene_question(t):
    t0, t_pause, t_tip, t_cm = st("Wie bekommt"), st("PAUSE"), st("Kleiner Tipp"), st("Schreib deine")
    img = vgradient(OUT_W, OUT_H, [(0, "#14213d"), (1, "#2b3f74")])
    cv = Canvas(img)
    rng = np.random.default_rng(1)
    for _ in range(70):
        x, y = rng.uniform(0, OUT_W), rng.uniform(0, OUT_H)
        tw = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv.circle(x, y, 2 + 2 * tw, fill=(255, 255, 255, int(80 + 100 * tw)))
    # the two buckets, big and alone (no person next to them -> no wrong proportions)
    sc, bx0, by0 = 2.6, OUT_W / 2 - 170, 1290
    cb = Canvas(img, -bx0 / sc, -by0 / sc, sc)
    cb.rect(-130, 0, 260, 10, fill=hexc(WOOD), r=4)
    draw_bucket(cb, "big", 0, 0, 0)
    draw_bucket(cb, "small", 150, 0, 0)
    pill(img, bx0, by0 - 160, "5 L", 52, pad=(20, 10))
    pill(img, bx0 + 150 * sc, by0 - 125, "3 L", 52, pad=(20, 10))
    pill(img, OUT_W / 2 + 230, 900, "4 L ?", 64, bg="#37b26c", fg="#ffffff", rot=4,
         scale=ease_out_back(prog(t, t0 + 0.4, t0 + 0.75)))
    p = ease_out_back(prog(t, t0, t0 + 0.35))
    pill(img, OUT_W / 2, 360, "WIE BEKOMMT ER", 84, bg="#fff6e6", scale=p, rot=-3)
    pill(img, OUT_W / 2, 515, "GENAU 4 LITER?", 88, bg="#ffd34d", scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)),
         rot=2)
    if t_pause - 0.2 < t < t_tip:
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            cv.circle(OUT_W / 2 - 220 + i * 70, 880 - i * 35, 20 + 10 * a, fill=(255, 255, 255, int(120 + 135 * a)))
    if t > t_tip:
        pill(img, OUT_W / 2, 670, "TIPP: WAS BLEIBT ÜBRIG?", 58, bg="#c5def5", rot=-2,
             scale=ease_out_back(prog(t, t_tip, t_tip + 0.35)))
    if t > t_cm:
        pill(img, OUT_W / 2, 1420, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff",
             scale=ease_out_back(prog(t, t_cm, t_cm + 0.35)))
    return img


STEP_LABELS = [("Dario füllt", "KLEIN FÜLLEN → IN GROSS"), ("Dann füllt", "NOCHMAL → GROSS VOLL"),
               ("Da nur noch", "1 LITER BLEIBT ÜBRIG"), ("Jetzt kippt", "GROSS ZURÜCK INS FASS"),
               ("Und gießt", "1 LITER IN DEN GROSSEN"), ("Zum Schluss", "+ 3 LITER DAZU")]


def scene_solution(t):
    t0, t_done = st("Hier kommt"), st("Eins plus drei")
    cheer = smooth(prog(t, t_done, t_done + 0.4))

    def actors(cv):
        actors.res = draw_scene(cv, t, solution=True, dario_face=-1, cheer=cheer)

    frame, view = render_world_frame(CAM, actors)
    pos, lv = actors.res
    level_pills(frame, view, pos, lv)
    if t < t0 + 1.4:
        pill(frame, OUT_W / 2, 330, "DIE LÖSUNG", 96, bg="#fff6e6", rot=-4,
             scale=ease_out_back(prog(t, t0, t0 + 0.35)) * (1 - prog(t, t0 + 1.1, t0 + 1.4)))
    cur = None
    for i, (key, lab) in enumerate(STEP_LABELS):
        if st(key) - 0.05 <= t:
            cur = (i + 1, lab)
    if cur and t0 + 1.4 < t < t_done:
        pill(frame, OUT_W / 2, 330, f"SCHRITT {cur[0]}/6:  {cur[1]}", 44, bg="#ffd34d", rot=-1.5)
    if st("Da nur noch") + 0.3 <= t < st("Jetzt kippt"):
        sx, sy = w2s(pos["small"][0], pos["small"][1] - BUCKETS["small"]["h"] - 80, view)
        pill(frame, sx, sy, "1 LITER!", 54, bg="#37b26c", fg="#ffffff", rot=-3,
             scale=ease_out_back(prog(t, st("Da nur noch") + 0.3, st("Da nur noch") + 0.6)))
    if t >= t_done:
        pill(frame, OUT_W / 2, 330, "1 + 3 = GENAU 4 LITER!", 62, bg="#37b26c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, t_done, t_done + 0.35)))
        sx, sy = w2s(pos["big"][0], pos["big"][1] - BUCKETS["big"]["h"] - 90, view)
        check_icon(frame, sx, sy, 60, scale=ease_out_back(prog(t, t_done + 0.2, t_done + 0.5)))
    return frame


def scene_outro(t):
    t0, t1 = st("Hättest"), st("Schreib's")

    def actors(cv):
        draw_scene(cv, t, solution=False, dario_face=1, cheer=0.6)
    img, _ = render_world_frame(FULL, actors)
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
    return img


SCENES = [
    (0.0, scene_story),
    (st("Wie bekommt") - 0.05, scene_question),
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
