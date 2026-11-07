"""Rätsel #8 – Hilberts Hotel: voll belegt, unendlich viele neue Gäste, eine Durchsage (Zimmernummer x 2).

usage:  python3 make_video.py            -> renders video.mp4 (needs timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from toolkit import _shade
from fx3d import BCanvas, pill3d, burst, karaoke
from fx3d import pop_pill as _pop_pill
from people import Look, draw_char, talk_arm

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
Z = 2
INK = hexc("#1d1b33")
_T = [0.0]

CHEF = Look("#e9b48f", "#6b5a4e", "#4b2a7a", "#2a2140", "#1d1b33", hair_style="short", top_style="bomber",
            under="#ffffff", trim="#e0b64a", eyes="#3b2a20", beard=True)
_rng = np.random.default_rng(8)
_SK = ["#f1c7a3", "#e0ac69", "#c68642", "#8d5524", "#ffdbac", "#a8714f"]
_HR = ["#2a1b14", "#7b4a2a", "#d4a373", "#111111", "#c0392b", "#f2c94c", "#555555"]
_TP = ["#e2574c", "#3fa7f5", "#3cc9a4", "#ffd34d", "#a29bfe", "#ff9f43", "#ff6fae", "#55efc4", "#6c5ce7", "#00b894"]
_HS = ["short", "long", "ponytail", "curly", "bun", "quiff"]
_TS = ["tee", "hoodie", "bomber"]


def rand_look(i):
    r = np.random.default_rng(100 + i)
    return Look(_SK[r.integers(0, 6)], _HR[r.integers(0, 7)], _TP[r.integers(0, 10)], ["#2d3436", "#34495e", "#3b3b58", "#6c5ce7"][r.integers(0, 4)],
                ["#ffffff", "#ffd34d", "#ff6f91", "#1d1b33"][r.integers(0, 4)], hair_style=_HS[r.integers(0, 6)],
                top_style=_TS[r.integers(0, 3)], lashes=bool(r.integers(0, 2)), glasses=bool(r.integers(0, 4) == 0))


OLD = [rand_look(i) for i in range(1, 21)]
NEW = [rand_look(100 + i) for i in range(1, 40)]

# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Dieses Hotel ist", "Das Hotel", "Und heute", "Da hält", "Jeder will", "Der Hotelchef", "Welche", "PAUSE",
        "Schreib deine", "Hier kommt", "Die Durchsage", "Zimmer eins", "Jetzt wohnen", "Und alle",
        "Eins für", "Dieses Rätsel", "Und was", "Schreib's"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 0.8
XFADE = 0.22


def st(k):
    return S[K[k]]


def en(k):
    return E[K[k]]


def wt(key, word, frac=0.3, nth=0):
    seg = next(x for x in TIM if x["text"].startswith(key))
    i = -1
    for _ in range(nth + 1):
        i = seg["text"].find(word, i + 1)
    f = (i + len(word) * frac) / len(seg["text"])
    return seg["start"] + (seg["end"] - seg["start"]) * f


def pop_pill(img, t, t0, cx, cy, text, size, **kw):
    _pop_pill(img, t, t0, cx, cy, text, int(size * 1.15), **kw)


# ------------------------------------------------------------------ helpers
def grad(img, stops):
    img.paste(vgradient(img.width, img.height, stops))


def shadow(cv, x, y, w):
    cv.ellipse(x - w, y - w * 0.12, x + w, y + w * 0.12, fill=(20, 10, 30, 80))


def ftext(cv, x, y, txt, size, max_w, col, anchor="mm"):
    if size < 6:
        return
    while font(int(size)).getbbox(txt)[2] > max_w and size > 8:
        size *= 0.95
    cv.text(x, y, txt, size, col, anchor=anchor)


def skyline(cv, base, cols, seed, lit=0.5, h0=200, h1=620, x0=-40, x1=1120):
    rng = np.random.default_rng(seed)
    x = x0
    while x < x1:
        w = rng.uniform(90, 170)
        hgt = rng.uniform(h0, h1)
        cv.rect(x, base - hgt, x + w, base, fill=hexc(cols[int(rng.integers(0, len(cols)))]))
        for wy in np.arange(base - hgt + 30, base - 20, 44):
            for wx in np.arange(x + 16, x + w - 20, 34):
                if rng.random() < lit:
                    cv.rect(wx, wy, wx + 16, wy + 22, fill=(255, 226, 140, 220))
        x += w + rng.uniform(4, 20)


def suitcase(cv, x, y, s, col):
    cv.rect(x - 26 * s, y - 52 * s, x + 26 * s, y, fill=hexc(col), r=8 * s)
    cv.rect(x - 26 * s, y - 30 * s, x + 26 * s, y - 24 * s, fill=_shade(hexc(col), 0.3))
    cv.arc(x - 12 * s, y - 66 * s, x + 12 * s, y - 46 * s, 180, 360, INK, 4 * s)
    cv.circle(x - 16 * s, y + 2 * s, 4 * s, fill=INK)
    cv.circle(x + 16 * s, y + 2 * s, 4 * s, fill=INK)


def guest(cv, x, y, look, h, f=1, t=0.0, case=False, **kw):
    g = draw_char(cv, x, y, look, h, f, t=t, **kw)
    if case:
        suitcase(cv, x + f * 0.17 * h, y, h / 240, _TP[int(x * 7) % 10])
    return g


# ------------------------------------------------------------------ backgrounds (screen world, cached 2x)
HOTEL_X0, HOTEL_X1, GROUND = 250, 830, 1290


def bg_street(img, cv):
    grad(img, [(0, "#0d1033"), (0.35, "#2a2a6e"), (0.62, "#6a3d8f"), (0.7, "#c76b8f"), (1, "#c76b8f")])
    rng = np.random.default_rng(3)
    for _ in range(70):
        cv.circle(rng.uniform(0, 1080), rng.uniform(0, 900), rng.uniform(1.5, 3), fill=(255, 255, 255, 170))
    cv.circle(900, 330, 70, fill=hexc("#fff3d0"))
    cv.circle(880, 315, 18, fill=hexc("#ece0bd"))
    skyline(cv, GROUND, ["#24205a", "#2c2668", "#1f1b4d"], 5, 0.45, 300, 900)
    # hotel tower (top continues beyond the frame)
    cv.rect(HOTEL_X0, -20, HOTEL_X1, GROUND, fill=hexc("#e8c9a0"))
    cv.rect(HOTEL_X1 - 70, -20, HOTEL_X1, GROUND, fill=hexc("#c9a47a"))
    for fl, y in enumerate(range(GROUND - 300, -150, -130)):
        cv.rect(HOTEL_X0 - 10, y + 104, HOTEL_X1 + 10, y + 116, fill=hexc("#b89066"))
        for k in range(4):
            x = HOTEL_X0 + 50 + k * 132
            cv.rect(x, y, x + 84, y + 96, fill=hexc("#8b5a3c"), r=8)
            cv.rect(x + 6, y + 6, x + 78, y + 90, fill=hexc("#ffd88a"), r=6)
            cv.rect(x + 6, y + 6, x + 22, y + 90, fill=hexc("#c0392b"))
            cv.rect(x + 62, y + 6, x + 78, y + 90, fill=hexc("#c0392b"))
            cv.rect(x + 22, y - 18, x + 62, y - 2, fill=hexc("#3b2a20"), r=4)
            cv.text(x + 42, y - 10, str(fl * 4 + k + 1), 14, hexc("#ffe7a8"))
    # entrance
    cv.rect(HOTEL_X0 + 140, GROUND - 230, HOTEL_X1 - 140, GROUND, fill=hexc("#3b2a20"))
    cv.rect(HOTEL_X0 + 160, GROUND - 210, HOTEL_X1 - 160, GROUND, fill=hexc("#ffcf6b"))
    cv.line([(540, GROUND - 210), (540, GROUND)], hexc("#c99a3c"), 6)
    for k in range(9):                        # striped canopy
        xa = HOTEL_X0 + 110 + k * 40
        cv.rect(xa, GROUND - 290, xa + 40, GROUND - 240, fill=hexc("#2a9d8f" if k % 2 == 0 else "#f4efe4"))
        cv.pieslice(xa, GROUND - 262, xa + 40, GROUND - 222, 0, 180, fill=hexc("#2a9d8f" if k % 2 == 0 else "#f4efe4"))
    cv.poly([(470, GROUND), (610, GROUND), (680, GROUND + 60), (400, GROUND + 60)], fill=hexc("#b3263a"))   # carpet
    cv.rect(0, GROUND, 1080, GROUND + 60, fill=hexc("#8d8aa8"))
    cv.rect(0, GROUND + 60, 1080, 1920, fill=hexc("#3a3858"))
    for k in range(6):
        cv.rect(k * 220 + 30, 1560, k * 220 + 150, 1574, fill=hexc("#e6e3f0"))
    cv.rect(0, 1760, 1080, 1920, fill=hexc("#8d8aa8"))
    for x in (90, 990):                        # street lamps
        cv.rect(x - 6, GROUND - 330, x + 6, GROUND, fill=hexc("#1d1b33"))
        cv.rect(x - 24, GROUND - 350, x + 24, GROUND - 326, fill=hexc("#1d1b33"), r=6)
    cv.rect(HOTEL_X0 + 20, GROUND - 400, HOTEL_X1 - 20, GROUND - 320, fill=hexc("#1d1b33"), r=16)   # sign board


def bg_hall(img, cv):
    grad(img, [(0, "#1a1440"), (1, "#2b2160")])
    cv.rect(0, 760, 1080, 1260, fill=hexc("#2f6f73"))                       # wallpaper
    for x in range(0, 1081, 36):
        cv.rect(x, 760, x + 14, 1260, fill=hexc("#347c80"))
    for x in range(18, 1081, 72):
        for y in range(800, 1260, 72):
            cv.poly([(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)], fill=hexc("#e0b64a"))
    cv.rect(0, 740, 1080, 770, fill=hexc("#c9a46a"))
    cv.rect(0, 1240, 1080, 1270, fill=hexc("#8b5a3c"))
    cv.rect(0, 1270, 1080, 1520, fill=hexc("#7a1f3d"))                       # carpet
    for x in range(-40, 1100, 120):
        cv.poly([(x, 1395), (x + 40, 1360), (x + 80, 1395), (x + 40, 1430)], fill=hexc("#e0b64a"))
    cv.rect(0, 1290, 1080, 1300, fill=hexc("#e0b64a"))
    cv.rect(0, 1490, 1080, 1500, fill=hexc("#e0b64a"))
    cv.rect(0, 1520, 1080, 1920, fill=hexc("#1a1440"))
    cv.rect(0, 560, 1080, 740, fill=hexc("#241c52"))
    for x in range(60, 1080, 196):                                           # ceiling lamps
        cv.line([(x, 560), (x, 640)], hexc("#c9a46a"), 4)
        cv.pieslice(x - 34, 620, x + 34, 680, 180, 360, fill=hexc("#e0b64a"))


def bg_plain(stops):
    def fn(img, cv):
        grad(img, stops)
    return fn


BGS = {"street": bg_street, "hall": bg_hall, "night": bg_plain([(0, "#0d1033"), (0.6, "#2a2a6e"), (1, "#6a3d8f")])}
_BG = {}


def bg(name):
    if name not in _BG:
        p = os.path.join(CACHE, f"bg_{name}.png")
        if not os.path.exists(p):
            img = Image.new("RGB", (OUT_W * Z, OUT_H * Z))
            BGS[name](img, BCanvas(img, 0, 0, Z))
            img.save(p)
        _BG[name] = Image.open(p).convert("RGB")
    return _BG[name]


def stage(name, cam, actors=None):
    cx, cy, vh = cam
    vh = min(vh, OUT_H)
    vw = vh * OUT_W / OUT_H
    cx = clamp(cx, vw / 2, OUT_W - vw / 2)
    cy = clamp(cy, vh / 2, OUT_H - vh / 2)
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    crop = bg(name).crop(tuple(int(round(v * Z)) for v in box)).convert("RGBA")
    cvs = BCanvas(crop, box[0], box[1], Z)
    if actors:
        actors(cvs)
    return crop.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS), box


def drift(cam, t, a=1.0):
    cx, cy, vh = cam
    k = vh / OUT_H
    return (cx + a * k * 10 * math.sin(t * 0.5), cy + a * k * 6 * math.sin(t * 0.37 + 1), vh * (1 + 0.01 * math.sin(t * 0.6)))


def dim(img, a, col=(15, 10, 30)):
    return Image.blend(img, Image.new("RGB", img.size, col), a) if a > 0.01 else img


# ------------------------------------------------------------------ animated street life
def neon(cv, t, booked=True):
    flick = 1.0 if (t * 7) % 5 > 0.4 else 0.35
    cv.text(540, GROUND - 360, "HOTEL UNENDLICHKEIT", 44, (255, 214, 120, int(255 * flick)))
    cv.circle(540, GROUND - 470, 0, fill=(0, 0, 0, 0))
    # big infinity sign
    pts = [(540 + 70 * math.cos(a) / (1 + math.sin(a) ** 2), GROUND - 470 + 70 * math.sin(a) * math.cos(a) / (1 + math.sin(a) ** 2))
           for a in np.linspace(0, 2 * math.pi, 60)]
    cv.line(pts, (255, 111, 174, 90), 26, cap=False)
    cv.line(pts, hexc("#ff6fae"), 10, cap=False)
    if booked:
        on = (t * 2) % 1 < 0.7
        x0, y0 = HOTEL_X1 - 220, GROUND - 210
        cv.rect(x0 - 8, y0 - 8, x0 + 228, y0 + 68, fill=(226, 87, 76, 70 if on else 20), r=14)
        cv.rect(x0, y0, x0 + 220, y0 + 60, fill=hexc("#1d1b33"), r=10)
        cv.text(x0 + 110, y0 + 30, "AUSGEBUCHT", 30, hexc("#ff5a4f") if on else hexc("#5a2a3a"))


def windows_life(cv, t):
    for fl, y in enumerate(range(GROUND - 300, -150, -130)):
        for k in range(4):
            x = HOTEL_X0 + 50 + k * 132
            i = fl * 4 + k
            ph = math.sin(t * 1.3 + i * 1.7)
            hx = x + 42 + 16 * ph
            cv.circle(hx, y + 52, 12, fill=(80, 40, 60, 180))
            cv.rect(hx - 14, y + 64, hx + 14, y + 90, fill=(80, 40, 60, 180), r=6)
            if (i * 3 + int(t * 0.8)) % 7 == 0:
                cv.line([(hx + 12, y + 70), (hx + 26, y + 46 + 6 * math.sin(t * 9))], (80, 40, 60, 180), 7)


def passersby(cv, t, n=3):
    for i in range(n):
        d = 1 if i % 2 == 0 else -1
        x = ((t * 75 + i * 420) % 1400) - 160 if d > 0 else 1240 - ((t * 75 + i * 420) % 1400)
        shadow(cv, x, GROUND + 40, 34)
        guest(cv, x, GROUND + 40, NEW[30 + i], 230, d, t=t + i, walk=t * 6.5 + i)


def street_scene(t, cam, extra=None, booked=True, people=True):
    def act(cv):
        windows_life(cv, t)
        neon(cv, t, booked)
        for k, x in enumerate((90, 990)):
            cv.circle(x, GROUND - 338, 60, fill=(255, 220, 140, 45))
        if people:
            passersby(cv, t)
        if extra:
            extra(cv)
    return stage("street", drift(cam, t), act)


# ------------------------------------------------------------------ corridor with numbered doors
DOOR_X0, DOOR_DX, DOOR_W, DOOR_TOP, FLOOR = 100, 104, 76, 1050, 1262


def door_x(n, off=0.0):
    return DOOR_X0 + (n - 1) * DOOR_DX - off


def door(cv, n, off, state="closed", glow=0.0, t=0.0):
    x = door_x(n, off)
    if x < -100 or x > 1180:
        return
    cv.rect(x - DOOR_W / 2 - 8, DOOR_TOP - 8, x + DOOR_W / 2 + 8, FLOOR, fill=hexc("#5a3a20"))
    if state == "open" or state == "free":
        cv.rect(x - DOOR_W / 2, DOOR_TOP, x + DOOR_W / 2, FLOOR, fill=hexc("#ffd88a" if state == "open" else "#c9ffd9"))
        cv.poly([(x - DOOR_W / 2, DOOR_TOP), (x - DOOR_W / 2 - 22, DOOR_TOP + 10), (x - DOOR_W / 2 - 22, FLOOR - 6),
                 (x - DOOR_W / 2, FLOOR)], fill=hexc("#8b5a3c"))
    else:
        cv.rect(x - DOOR_W / 2, DOOR_TOP, x + DOOR_W / 2, FLOOR, fill=hexc("#8b5a3c"))
        cv.rect(x - DOOR_W / 2 + 10, DOOR_TOP + 14, x + DOOR_W / 2 - 10, DOOR_TOP + 90, fill=hexc("#7a4e33"), r=4)
        cv.rect(x - DOOR_W / 2 + 10, DOOR_TOP + 110, x + DOOR_W / 2 - 10, FLOOR - 16, fill=hexc("#7a4e33"), r=4)
        cv.circle(x + DOOR_W / 2 - 14, DOOR_TOP + 110, 5, fill=hexc("#e0b64a"))
    if glow > 0.01:
        col = (90, 255, 150) if state == "free" else (255, 214, 120)
        for k in range(3, 0, -1):
            cv.rect(x - DOOR_W / 2 - 8 * k, DOOR_TOP - 8 * k, x + DOOR_W / 2 + 8 * k, FLOOR, fill=col + (int(30 * glow),), r=10)
    cv.rect(x - 30, DOOR_TOP - 70, x + 30, DOOR_TOP - 22, fill=hexc("#e0b64a"), r=8)
    cv.rect(x - 26, DOOR_TOP - 66, x + 26, DOOR_TOP - 26, fill=hexc("#1d1b33"), r=6)
    cv.text(x, DOOR_TOP - 46, str(n), 30, hexc("#ffe7a8"))
    if state == "free" and glow > 0.3:
        cv.rect(x - 34, DOOR_TOP + 60, x + 34, DOOR_TOP + 94, fill=hexc("#37b26c"), r=8)
        cv.text(x, DOOR_TOP + 77, "FREI", 20, hexc("#ffffff"))


def arc_arrow(cv, x0, x1, y, p, col=(255, 90, 80)):
    """dashed arc from x0 to x1, drawn up to fraction p"""
    if p <= 0:
        return
    h = 60 + abs(x1 - x0) * 0.35
    pts = []
    for k in range(int(40 * p) + 1):
        q = k / 40
        pts.append((x0 + (x1 - x0) * q, y - h * math.sin(math.pi * q)))
    for k in range(0, len(pts) - 1, 2):
        cv.line([pts[k], pts[k + 1]], col + (255,), 7)
    if p > 0.95:
        ex, ey = pts[-1]
        cv.poly([(ex, ey + 6), (ex - 16, ey - 18), (ex + 14, ey - 16)], fill=col + (255,))


# ------------------------------------------------------------------ scenes
HOOK = [(["HOTEL", "VOLL –"], "#fff6e6", "#2b2140", -3, 150),
        (["TROTZDEM", "PASSEN"], "#ffd34d", "#2b2140", 2, 132),
        (["∞ VIELE", "GÄSTE", "REIN!"], "#e2574c", "#ffffff", -2, 128)]


def hook_times():
    k = "Dieses Hotel ist"

    def w(word, nxt=None):
        a = wt(k, word, 0.0)
        b = wt(k, nxt, 0.0) if nxt else wt(k, word, 1.0)
        return (a, b)
    return [w("Hotel", "ist"), w("voll", "und"), w("trotzdem", "passen"), w("passen", "noch"),
            (wt(k, "unendlich", 0.0), wt(k, "Gäste", 0.0)), w("Gäste", "rein"), w("rein")]


def sc_hook(t):
    t0, t1 = st("Dieses Hotel ist"), en("Dieses Hotel ist")
    img, _ = street_scene(t, (540, 960, 1920))
    img = dim(img, 0.38)
    if t < 0.15:
        img = Image.blend(img, Image.new("RGB", img.size, (255, 250, 230)), 0.4 * (1 - t / 0.15))
    karaoke(img, t, HOOK, t0, t1, [560, 780, 990], pop_k=0.4, first_pop=False, stagger=0.06, times=hook_times())
    return img


def sc_tower(t):
    """endless climb up the hotel: floors keep coming, room numbers keep growing"""
    t0, t1 = st("Das Hotel"), en("Das Hotel")
    p = prog(t, t0, t1)
    speed = 1.0 + 9 * p * p                        # accelerate
    scroll = (t - t0) * 260 * speed
    img = Image.new("RGBA", (OUT_W * Z, OUT_H * Z))
    cv = BCanvas(img, 0, 0, Z)
    sky = vgradient(OUT_W * Z, OUT_H * Z, [(0, "#05081f"), (0.6, "#1b1f55"), (1, "#3a2a7a")])
    img.paste(sky)
    for k in range(60):
        rng = np.random.default_rng(k)
        y = (rng.uniform(0, 1920) + scroll * 0.2) % 1920
        cv.circle(rng.uniform(0, 1080), y, rng.uniform(1.5, 3), fill=(255, 255, 255, 180))
    for k in range(3):                             # clouds rushing by
        y = (k * 700 + scroll * 0.6) % 2400 - 300
        x = 120 + k * 340
        for dx, r in ((-80, 60), (0, 80), (90, 60)):
            cv.circle(x + dx, y, r, fill=(220, 210, 255, 90))
    x0, x1 = 300, 780
    cv.rect(x0, 0, x1, 1920, fill=hexc("#e8c9a0"))
    cv.rect(x1 - 60, 0, x1, 1920, fill=hexc("#c9a47a"))
    fh = 210
    base_floor = int(scroll // fh)
    for j in range(-1, 11):
        fl = base_floor + j
        y = 1920 - ((j + 1) * fh - (scroll % fh)) - 40
        cv.rect(x0 - 12, y + 170, x1 + 12, y + 186, fill=hexc("#b89066"))
        for k in range(2):
            wx = x0 + 70 + k * 200
            cv.rect(wx, y + 20, wx + 140, y + 160, fill=hexc("#8b5a3c"), r=10)
            cv.rect(wx + 8, y + 28, wx + 132, y + 152, fill=hexc("#ffd88a"), r=8)
            cv.rect(wx + 8, y + 28, wx + 30, y + 152, fill=hexc("#c0392b"))
            cv.rect(wx + 110, y + 28, wx + 132, y + 152, fill=hexc("#c0392b"))
            n = max(1, fl * 2 + k + 1)
            cv.rect(wx + 30, y - 18, wx + 110, y + 14, fill=hexc("#1d1b33"), r=6)
            ftext(cv, wx + 70, y - 2, str(n), 26, 74, hexc("#ffe7a8"))
            hx = wx + 70 + 20 * math.sin(t * 1.4 + n)
            cv.circle(hx, y + 92, 18, fill=(80, 40, 60, 170))
            cv.rect(hx - 20, y + 110, hx + 20, y + 152, fill=(80, 40, 60, 170), r=8)
    img = img.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)
    pop_pill(img, t, t0 + 0.1, 540, 330, "UNENDLICH VIELE ZIMMER", 58, bg="#ffd34d", rot=-2)
    if t > wt("Das Hotel", "eins", 0.0):
        for k, (w, x) in enumerate((("eins", 300), ("zwei", 540), ("drei", 780))):
            pop_pill(img, t, wt("Das Hotel", w, 0.0), x, 470, str(k + 1), 64, bg="#fff6e6", rot=(-4, 3, -3)[k])
    if t > wt("Das Hotel", "Ende", 0.0) - 0.4:
        pop_pill(img, t, wt("Das Hotel", "Ende", 0.0) - 0.4, 540, 1300, "… ∞", 90, bg="#ff6fae", fg="#ffffff", rot=2)
    return img


def sc_booked(t):
    t0 = st("Und heute")
    cam = keyframes(t, [(t0, (540, 700, 1300)), (en("Und heute"), (540, 900, 1500))])

    def ex(cv):
        for fl, y in enumerate(range(GROUND - 300, -150, -130)):
            for k in range(4):
                x = HOTEL_X0 + 50 + k * 132
                ts = t0 + 0.2 + ((fl * 4 + k) % 12) * 0.08
                if t > ts:
                    a = ease_out_back(prog(t, ts, ts + 0.25))
                    if a < 0.1:
                        continue
                    cv.rect(x + 8, y + 36, x + 76, y + 60, fill=hexc("#e2574c"), r=6)
                    ftext(cv, x + 42, y + 48, "BELEGT", 15 * a, 60, hexc("#ffffff"))
    img, _ = street_scene(t, cam, ex, people=False)
    pop_pill(img, t, t0 + 0.1, 540, 330, "ALLE ZIMMER BELEGT", 62, bg="#e2574c", fg="#ffffff", rot=-2)
    return img


def bus(cv, x, y, s, t):
    cv.rect(x - 300 * s, y - 230 * s, x + 300 * s, y - 40 * s, fill=hexc("#ffcf3f"), r=40 * s)
    cv.rect(x - 300 * s, y - 100 * s, x + 300 * s, y - 70 * s, fill=hexc("#ff9f1c"))
    for k in range(6):
        wx = x - 270 * s + k * 86 * s
        cv.rect(wx, y - 210 * s, wx + 70 * s, y - 130 * s, fill=hexc("#2b3a55"), r=10 * s)
        cv.circle(wx + 35 * s, y - 150 * s + 4 * s * math.sin(t * 8 + k), 16 * s, fill=hexc(_SK[k % 6]))
    cv.rect(x + 240 * s, y - 210 * s, x + 296 * s, y - 50 * s, fill=hexc("#2b3a55"), r=10 * s)
    cv.text(x - 40 * s, y - 85 * s, "∞ EXPRESS", 30 * s, hexc("#1d1b33"))
    for wx in (x - 190 * s, x + 190 * s):
        cv.circle(wx, y - 40 * s, 46 * s, fill=hexc("#1b1b24"))
        cv.circle(wx, y - 40 * s, 24 * s, fill=hexc("#c9ced8"))
    cv.rect(x + 290 * s, y - 120 * s, x + 306 * s, y - 96 * s, fill=hexc("#fff3b0"), r=4 * s)


def queue(cv, t, n_vis=1.0, x_start=700):
    """endless queue of new guests stretching to the vanishing point"""
    items = []
    for k in range(60):
        s = 1 / (1 + k * 0.22)
        x = x_start + (1060 - x_start) * (1 - s) * 1.1 + 40 * (1 - s)
        y = GROUND + 40 - (1 - s) * 70
        items.append((k, s, x, y))
    for k, s, x, y in reversed(items):
        if k / 60 > n_vis:
            continue
        h = 230 * s
        if h < 18:
            cv.rect(x - 3 * s * 10, y - h, x + 3 * s * 10, y, fill=hexc(_TP[k % 10]))
            continue
        guest(cv, x, y, NEW[k % len(NEW)], h, -1, t=t + k, case=h > 60)


def sc_bus(t):
    t0, t1 = st("Da hält"), st("Der Hotelchef")
    tj = st("Jeder will")
    p = smooth(prog(t, t0 - 0.2, t0 + 1.4))
    bx = -400 + 820 * p

    def ex(cv):
        if t < tj + 0.3:
            bus(cv, bx, 1530, 1.0, t)
        nv = prog(t, t0 + 1.2, tj + 0.5)
        queue(cv, t, nv)
    cam = keyframes(t, [(t0, (540, 1200, 1400)), (tj, (620, 1100, 1250))])
    img, _ = street_scene(t, cam, ex, people=False)
    pop_pill(img, t, t0 + 0.2, 540, 330, "EIN BUS VOLLER GÄSTE", 58, bg="#ffcf3f", rot=-2, t1=tj - 0.1)
    pop_pill(img, t, t0 + 1.3, 540, 460, "∞ NEUE GÄSTE", 70, bg="#ff6fae", fg="#ffffff", rot=2, t1=tj - 0.1)
    if t >= tj:
        pop_pill(img, t, tj + 0.1, 540, 330, "JEDER WILL EIN ZIMMER", 58, bg="#fff6e6", rot=-2)
    return img


def mic(cv, hand, s):
    cv.line([hand, (hand[0] + 10 * s, hand[1] - 40 * s)], hexc("#1d1b33"), 10 * s)
    cv.circle(hand[0] + 12 * s, hand[1] - 52 * s, 16 * s, fill=hexc("#555b6e"))
    cv.circle(hand[0] + 8 * s, hand[1] - 56 * s, 6 * s, fill=hexc("#8a90a0"))


def chef(cv, x, y, h, t, talk=0.0, with_mic=True, **kw):
    H = h
    if with_mic:
        hx, hy = x + 0.17 * H, y - 0.74 * H
        g = draw_char(cv, x, y, CHEF, H, 1, t=t, arm_f=("ik", (hx, hy)), hand_f="fist", talk=talk,
                      arm_b=("ang", -0.2, 0.25), **kw)
        mic(cv, g["hand_f"], H / 500)
    else:
        g = draw_char(cv, x, y, CHEF, H, 1, t=t, talk=talk, **kw)
    nx, ny = g["neck"]
    cv.poly([(nx - 14, ny + 4), (nx, ny + 12), (nx - 14, ny + 20)], fill=hexc("#e2574c"))     # bow tie
    cv.poly([(nx + 14, ny + 4), (nx, ny + 12), (nx + 14, ny + 20)], fill=hexc("#e2574c"))
    cv.circle(nx, ny + 12, 5, fill=hexc("#b3263a"))
    return g


def waves(cv, x, y, t, n=3):
    for k in range(n):
        ph = ((t * 1.6) + k / n) % 1
        r = 40 + 120 * ph
        cv.arc(x - r, y - r, x + r, y + r, -45, 45, (255, 255, 255, int(220 * (1 - ph))), 8)


def sc_chef(t):
    t0 = st("Der Hotelchef")

    def ex(cv):
        shadow(cv, 290, 1420, 120)
        g = chef(cv, 290, 1420, 560, t, talk=0.0, mood="smirk")
        waves(cv, g["hand_f"][0] + 30, g["hand_f"][1] - 60, t)
    img, _ = street_scene(t, (420, 1080, 1250), ex, people=False)
    pop_pill(img, t, t0 + 0.1, 540, 330, "DER HOTELCHEF", 64, bg="#a29bfe", fg="#ffffff", rot=-2)
    pop_pill(img, t, wt("Der Hotelchef", "einzige", 0.0), 540, 470, "NUR 1 DURCHSAGE!", 66, bg="#ffd34d", rot=2)
    return img


def corridor(t, cam=(540, 960, 1920), actors=None, off=0.0, states=None, glows=None):
    def act(cv):
        for x in range(60, 1080, 196):
            cv.pieslice(x - 80, 640, x + 80, 820, 60, 120, fill=(255, 220, 140, 40))
        for n in range(1, 13):
            door(cv, n, off, (states or {}).get(n, "open"), (glows or {}).get(n, 0.0), t)
        if actors:
            actors(cv)
    return stage("hall", drift(cam, t, 0.5), act)


def sc_question(t):
    t0, tp, tc = st("Welche"), st("PAUSE"), st("Schreib deine")
    ttip = tc

    def act(cv):
        for n in range(1, 11):
            guest(cv, door_x(n), FLOOR, OLD[n - 1], 170, 1 if n % 2 else -1, t=t + n)
    img, _ = corridor(t, actors=act)
    img = dim(img, 0.55, (12, 10, 40))
    pop_pill(img, t, t0, 540, 360, "WELCHE", 96, bg="#fff6e6", rot=-3)
    pop_pill(img, t, t0 + 0.25, 540, 520, "DURCHSAGE?", 100, bg="#ffd34d", rot=2)
    if tp - 0.2 < t < ttip:
        from PIL import ImageDraw
        d = ImageDraw.Draw(img, "RGBA")
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            r = 18 + 10 * a
            cx = OUT_W / 2 - 70 + i * 70
            d.ellipse([cx - r, 700 - r, cx + r, 700 + r], fill=(255, 255, 255, int(120 + 135 * a)))
    if t > tc:
        pop_pill(img, t, tc, 540, 1420, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff")
    return img


def sc_solution_chef(t):
    t0, td, te = st("Hier kommt"), st("Die Durchsage"), en("Die Durchsage")

    def ex(cv):
        shadow(cv, 290, 1420, 120)
        g = chef(cv, 290, 1420, 560, t, talk=0.8 if t > td else 0.0, mood="smile")
        if t > td:
            waves(cv, g["hand_f"][0] + 30, g["hand_f"][1] - 60, t)
    img, _ = street_scene(t, (420, 1080, 1250), ex, people=False)
    if t < td:
        pop_pill(img, t, t0, 540, 360, "DIE LÖSUNG", 100, bg="#fff6e6", rot=-4)
    else:
        pop_pill(img, t, td + 0.1, 540, 330, "„ZIEHT ALLE UM IN DIE", 50, bg="#fff6e6", rot=-2)
        pop_pill(img, t, wt("Die Durchsage", "doppelten", 0.0), 540, 460, "DOPPELTE NUMMER!“", 62, bg="#ffd34d", rot=2)
        if t > wt("Die Durchsage", "Nummer", 0.5):
            pop_pill(img, t, wt("Die Durchsage", "Nummer", 0.5), 540, 610, "ZIMMER × 2", 88, bg="#e2574c", fg="#ffffff",
                     rot=-3)
    return img


def jump_times():
    """start time of each guest's move n -> 2n"""
    ts = {1: wt("Zimmer eins", "eins", 0.0), 2: wt("Zimmer eins", "zwei", 0.0, 0),
          3: wt("Zimmer eins", "drei", 0.0)}
    so = wt("Zimmer eins", "so weiter", 0.0)
    for n in range(4, 11):
        ts[n] = so - 0.3 + (n - 4) * 0.12
    return ts


def guest_pos(n, t, ts):
    """old guest n: x position, airborne amount"""
    t0 = ts[n]
    p = smooth(prog(t, t0, t0 + 0.9))
    x0, x1 = door_x(n), door_x(2 * n)
    x = x0 + (x1 - x0) * p
    h = 60 + abs(x1 - x0) * 0.35
    return x, math.sin(math.pi * p) * h, p


def old_guests(cv, t, ts, arrows=True, show_new=0.0, glow_even=0.0):
    for n in range(1, 11):
        x, air, p = guest_pos(n, t, ts)
        if arrows and t > ts[n] - 0.1 and n <= 5:
            arc_arrow(cv, door_x(n), door_x(2 * n), DOOR_TOP - 90, prog(t, ts[n] - 0.1, ts[n] + 0.5))
        y = FLOOR - air
        if x > 1200:
            continue
        kw = dict(arm_f=("ang", 2.6, 0.2), arm_b=("ang", -2.6, -0.2), mood="laugh") if 0.05 < p < 0.95 else {}
        guest(cv, x, y, OLD[n - 1], 170, 1 if (p < 1 and p > 0) or n % 2 else -1, t=t + n,
              walk=(t * 8 + n) if 0.05 < p < 0.95 else None, **kw)


def sc_moves(t):
    t0, tg, tu, te, tr = st("Zimmer eins"), st("Jetzt wohnen"), st("Und alle"), st("Eins für"), st("Dieses Rätsel")
    ts = jump_times()
    glow_odd = smooth(prog(t, tu, tu + 0.6))
    glow_even = smooth(prog(t, tg, tg + 0.5)) * (1 - glow_odd)
    states = {n: ("free" if (n % 2 == 1 and t > tu) else "open") for n in range(1, 13)}
    glows = {n: (glow_odd if n % 2 == 1 else glow_even) for n in range(1, 13)}
    off = 0.0

    def act(cv):
        old_guests(cv, t, ts, arrows=t < tg + 0.5)
        if t > te:                                   # new bus guests walk into the free odd rooms
            for j, n in enumerate((1, 3, 5, 7, 9, 11)):
                ta = te + j * 0.22
                p = smooth(prog(t, ta, ta + 1.2))
                x = -80 + (door_x(n) + 80) * p
                guest(cv, x, FLOOR, NEW[j], 170, 1, t=t + j, walk=t * 7 + j if p < 1 else None, case=True)
    img, _ = corridor(t, actors=act, off=off, states=states, glows=glows)
    if t < tg:
        pop_pill(img, t, t0 + 0.1, 540, 330, "ZIMMER × 2", 80, bg="#e2574c", fg="#ffffff", rot=-2)
        for k, (n, w) in enumerate(((1, "eins"), (2, "zwei"), (3, "drei"))):
            if t > ts[n]:
                pop_pill(img, t, ts[n], 220 + k * 320, 470, f"{n} → {2 * n}", 54, bg="#fff6e6", rot=(-3, 2, -2)[k])
    elif t < tu:
        pop_pill(img, t, tg + 0.1, 540, 330, "ALTE GÄSTE: GERADE ZIMMER", 50, bg="#ffd34d", rot=-2)
        pop_pill(img, t, tg + 0.5, 540, 460, "2 · 4 · 6 · 8 · 10 …", 56, bg="#fff6e6", rot=2)
    elif t < te:
        pop_pill(img, t, tu + 0.1, 540, 330, "UNGERADE ZIMMER: FREI!", 52, bg="#37b26c", fg="#ffffff", rot=-2)
        pop_pill(img, t, wt("Und alle", "unendlich", 0.0), 540, 460, "1 · 3 · 5 · 7 · 9 … ∞", 56, bg="#fff6e6", rot=2)
    else:
        pop_pill(img, t, te + 0.1, 540, 330, "PLATZ FÜR ALLE NEUEN!", 56, bg="#37b26c", fg="#ffffff", rot=-2)
    return img


def sc_name(t):
    t0 = st("Dieses Rätsel")
    img, _ = street_scene(t, (540, 980, 1500), people=False, booked=True)
    img = dim(img, 0.3)
    burst(img, 540, 760, 0.5, t, 180, 460)
    pop_pill(img, t, t0 + 0.1, 540, 620, "HILBERTS", 104, bg="#ffd34d", rot=-3)
    pop_pill(img, t, t0 + 0.35, 540, 790, "HOTEL", 120, bg="#fff6e6", rot=2)
    pop_pill(img, t, wt("Dieses Rätsel", "Gedanken", 0.0), 540, 960, "MATHE-GEDANKENEXPERIMENT", 42, bg="#a29bfe",
             fg="#ffffff", rot=-2)
    return img


def sc_buses(t):
    t0, t1 = st("Und was"), st("Schreib's")

    def ex(cv):
        for k in range(14, -1, -1):
            s = 1 / (1 + k * 0.35)
            x = 560 + 520 * (1 - s) + ((t - t0) * 120 * s) % 30
            y = 1560 - (1 - s) * 260
            if k == 0:
                x = -360 + 860 * smooth(prog(t, t0 - 0.2, t0 + 1.0))
            bus(cv, x, y, 0.75 * s, t + k)
    img, _ = street_scene(t, (540, 1150, 1500), ex, people=False)
    if t < t1:
        pop_pill(img, t, t0 + 0.1, 540, 330, "UND WENN UNENDLICH", 56, bg="#fff6e6", rot=-2)
        pop_pill(img, t, wt("Und was", "Busse", 0.0), 540, 470, "VIELE BUSSE KOMMEN?", 64, bg="#ff6fae", fg="#ffffff",
                 rot=2)
    else:
        img = dim(img, 0.35)
        pop_pill(img, t, t1, 540, 520, "SCHREIB'S IN DIE KOMMENTARE", 42, bg="#ffffff")
        followed = t > t1 + 1.4
        pill3d(img, 540, 650, "GEFOLGT  ✓" if followed else "+  FOLGEN", 72, bg="#37b26c" if followed else "#e2574c",
               fg="#ffffff", scale=ease_out_back(prog(t, t1 + 0.3, t1 + 0.6)) * (1 + (0 if followed else 0.05 * math.sin(t * 10))))
        pop_pill(img, t, t1 + 0.8, 540, 790, "JEDEN TAG EIN RÄTSEL", 48, bg="#ffd34d", rot=-2)
    return img


SCENES = [(0.0, sc_hook), (st("Das Hotel") - 0.1, sc_tower), (st("Und heute") - 0.05, sc_booked),
          (st("Da hält") - 0.05, sc_bus), (st("Der Hotelchef") - 0.05, sc_chef), (st("Welche") - 0.05, sc_question),
          (st("Hier kommt") - 0.05, sc_solution_chef), (st("Zimmer eins") - 0.05, sc_moves),
          (st("Dieses Rätsel") - 0.05, sc_name), (st("Und was") - 0.05, sc_buses)]


def frame_at(t):
    _T[0] = t
    idx = max(i for i, (s0, _) in enumerate(SCENES) if t >= s0)
    img = SCENES[idx][1](t)
    if idx > 0:
        s0 = SCENES[idx][0]
        if t < s0 + XFADE:
            prev = SCENES[idx - 1][1](t)
            img = Image.blend(prev, img, smooth(prog(t, s0, s0 + XFADE)))
    if t > END - 0.5:
        img = Image.blend(img, Image.new("RGB", img.size, (20, 14, 36)), prog(t, END - 0.5, END))
    return img


def render_chunk(args):
    i0, i1, path = args
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame_at(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return path


def render(out="video.mp4", workers=4):
    for n in BGS:
        bg(n)
    n = int(END * FPS)
    step = math.ceil(n / (workers * 3))
    chunks = [(i, min(n, i + step), os.path.join(CACHE, f"chunk{k:02d}.mp4")) for k, i in enumerate(range(0, n, step))]
    with Pool(workers) as pool:
        paths = pool.map(render_chunk, chunks, chunksize=1)
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
