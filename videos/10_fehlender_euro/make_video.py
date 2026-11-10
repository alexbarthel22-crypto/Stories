"""Rätsel #10 – Der fehlende Euro (Pizzeria Bella, Corgi Pepe). Eigene Geschichte zum klassischen Rätsel.

usage:  python3 make_video.py            -> renders video.mp4 (needs timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from fx3d import BCanvas, pill3d, burst, karaoke
from fx3d import pop_pill as _pop_pill
from people import Look, draw_char
from money import note_sprite, paste_sprite

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
Z = 2
INK = hexc("#1d1b33")
_T = [0.0]

LEA = Look("#f1c7a3", "#8b4a2b", "#ffd34d", "#34495e", "#ffffff", hair_style="long", top_style="tee", lashes=True,
           eyes="#3a7bd5")
TOM = Look("#8d5524", "#1b1b1b", "#3fa7f5", "#2d3436", "#ff6f91", hair_style="curly", top_style="hoodie", trim="#1f6fb0")
BEN = Look("#ffdbac", "#d4a373", "#37b26c", "#3b3b58", "#ffffff", hair_style="quiff", top_style="bomber", trim="#1f7a45",
           under="#ffffff", glasses=True)
CHEF = Look("#e0ac69", "#2d1e12", "#ffffff", "#2d3436", "#1d1b33", hair_style="short", top_style="tee", beard=True,
            eyes="#3b2a20")
WAITER = Look("#c68642", "#111111", "#1d1b33", "#1d1b33", "#1d1b33", hair_style="short", top_style="tee",
              eyes="#3b2a20")

# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Drei Freunde", "Lea, Tom", "Die Rechnung", "Dann merkt", "Er gibt", "Der Kellner", "Also hat", "Wo ist",
        "PAUSE", "Schreib's", "Hier kommt", "In den", "Dazu die", "Folg mir"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 0.7
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
    _pop_pill(img, t, t0, cx, cy, text, int(size * 1.12), **kw)


def shadow(cv, x, y, w):
    cv.ellipse(x - w, y - w * 0.12, x + w, y + w * 0.12, fill=(40, 20, 10, 70))


# ------------------------------------------------------------------ original characters & props
def corgi(cv, x, y, s=1.0, t=0.0, f=1, beg=0.0, wag=1.0):
    """original corgi: red-tan coat, white blaze/chest/paws, big upright ears, fluffy bum, wagging nub tail"""
    tan, tan_d, wh = hexc("#e2913f"), hexc("#c4742b"), hexc("#fff6ea")
    by = y - 52 * s - beg * 40 * s
    lift = beg * 0.6
    # tail (behind)
    tx = x - f * 92 * s
    w = math.sin(t * 14) * 14 * s * wag
    cv.ellipse(tx - 22 * s + w * 0.3, by - 34 * s + w, tx + 22 * s + w * 0.3, by + 4 * s + w, fill=tan)
    # back legs
    for dx in (-70, -50):
        cv.rect(x + f * dx * s - 10 * s, by + 10 * s, x + f * dx * s + 10 * s, y, fill=tan_d, r=8 * s)
        cv.ellipse(x + f * dx * s - 14 * s, y - 10 * s, x + f * dx * s + 14 * s, y + 2 * s, fill=wh)
    # body (long, low) – tilts up when begging
    cv.ellipse(x - 95 * s, by - 44 * s - lift * 30 * s, x + 75 * s, by + 34 * s, fill=tan)
    cv.ellipse(x - 92 * s, by - 30 * s, x - 30 * s, by + 34 * s, fill=wh if f < 0 else tan)        # fluffy bum
    cv.ellipse(x + f * 10 * s - 50 * s, by + 4 * s, x + f * 10 * s + 50 * s, by + 36 * s, fill=wh)   # belly
    # front legs
    for dx in (40, 58):
        if beg > 0.3:
            cv.line([(x + f * dx * s, by), (x + f * (dx + 22) * s, by - 30 * s)], tan, 18 * s)
            cv.circle(x + f * (dx + 24) * s, by - 32 * s, 11 * s, fill=wh)
        else:
            cv.rect(x + f * dx * s - 10 * s, by + 10 * s, x + f * dx * s + 10 * s, y, fill=tan, r=8 * s)
            cv.ellipse(x + f * dx * s - 14 * s, y - 10 * s, x + f * dx * s + 16 * s, y + 2 * s, fill=wh)
    # chest ruff + head
    hx, hy = x + f * 78 * s, by - 52 * s - lift * 44 * s + 3 * s * math.sin(t * 3)
    cv.ellipse(hx - f * 34 * s - 30 * s, hy + 10 * s, hx - f * 34 * s + 34 * s, hy + 78 * s, fill=wh)
    for side in (-1, 1):                       # big ears
        ex = hx + side * 26 * s - f * 6 * s
        cv.poly([(ex - 18 * s, hy - 26 * s), (ex + side * 6 * s, hy - 82 * s), (ex + 18 * s, hy - 26 * s)], fill=tan)
        cv.poly([(ex - 9 * s, hy - 30 * s), (ex + side * 4 * s, hy - 66 * s), (ex + 9 * s, hy - 30 * s)], fill=hexc("#f6b8a8"))
    cv.ellipse(hx - 46 * s, hy - 40 * s, hx + 46 * s, hy + 32 * s, fill=tan)
    cv.poly([(hx - 8 * s, hy - 40 * s), (hx + 8 * s, hy - 40 * s), (hx + f * 30 * s + 14 * s, hy + 24 * s),
             (hx + f * 30 * s - 14 * s, hy + 24 * s)], fill=wh)                                     # white blaze
    cv.ellipse(hx + f * 20 * s - 26 * s, hy + 2 * s, hx + f * 20 * s + 30 * s, hy + 36 * s, fill=wh)   # muzzle
    cv.circle(hx + f * 44 * s, hy + 10 * s, 7 * s, fill=INK)                                         # nose
    for side in (-1, 1):
        ex = hx + f * 6 * s + side * 17 * s
        cv.circle(ex, hy - 8 * s, 6.5 * s, fill=INK)
        cv.circle(ex + 2 * s, hy - 10 * s, 2.2 * s, fill=hexc("#ffffff"))
    if beg > 0.2 or wag > 0.5:                  # tongue
        cv.ellipse(hx + f * 22 * s - 8 * s, hy + 26 * s, hx + f * 22 * s + 8 * s, hy + 46 * s + 4 * s * math.sin(t * 9),
                   fill=hexc("#f07a8a"))
    cv.rect(hx - f * 30 * s - 26 * s, hy + 30 * s, hx - f * 30 * s + 26 * s, hy + 40 * s, fill=hexc("#e2574c"), r=4 * s)  # collar
    cv.circle(hx - f * 30 * s, hy + 46 * s, 6 * s, fill=hexc("#ffd34d"))


def chef_hat(cv, g, s=1.0):
    hx, hy, r = g["head"][0], g["head"][1], g["r"]
    cv.rect(hx - r * 0.95, hy - r * 1.15, hx + r * 0.95, hy - r * 0.7, fill=hexc("#ffffff"), r=r * 0.1)
    for dx in (-0.55, 0, 0.55):
        cv.circle(hx + dx * r, hy - r * 1.45, r * 0.55, fill=hexc("#ffffff"))
    cv.line([(hx - r * 0.95, hy - r * 0.78), (hx + r * 0.95, hy - r * 0.78)], hexc("#e5e5ee"), r * 0.08)


def mustache(cv, g):
    fx, ey, r = g["fx"], g["ey"], g["r"]
    cv.ellipse(fx - r * 0.42, ey + r * 0.34, fx + r * 0.02, ey + r * 0.52, fill=hexc("#2d1e12"))
    cv.ellipse(fx - r * 0.02, ey + r * 0.34, fx + r * 0.42, ey + r * 0.52, fill=hexc("#2d1e12"))


def apron(cv, g, h):
    x, hip = g["hip"]
    cv.rect(x - 0.075 * h, hip - 0.06 * h, x + 0.075 * h, hip + 0.18 * h, fill=hexc("#f4efe4"), r=0.01 * h)
    cv.rect(x - 0.075 * h, hip - 0.06 * h, x + 0.075 * h, hip - 0.04 * h, fill=hexc("#c0392b"))


def euro_coin(cv, x, y, r, val=1):
    """1 € coin: brass ring, silver centre (2 € the other way round)"""
    ring, core = (hexc("#d9a93a"), hexc("#c9ced8")) if val == 1 else (hexc("#c9ced8"), hexc("#d9a93a"))
    cv.circle(x, y, r, fill=ring)
    cv.circle(x, y, r * 0.66, fill=core)
    cv.circle(x, y, r, outline=_shade(ring, 0.3), width=max(1, r * 0.06))
    cv.text(x, y + r * 0.04, str(val), r * 0.8, INK)


from toolkit import _shade  # noqa: E402


# ------------------------------------------------------------------ backgrounds
FLOOR = 1440
TABLE_Y = 1170


def bg_pizzeria(img, cv):
    img.paste(vgradient(img.width, img.height, [(0, "#3a1f1a"), (1, "#5a2e22")]))
    for row, y in enumerate(range(0, 1300, 46)):                        # brick wall
        off = (row % 2) * 45
        for x in range(-90 + off, 1100, 90):
            c = ["#a8483a", "#b45444", "#9a4034", "#b9604e"][(x // 90 + row) % 4]
            cv.rect(x + 3, y + 3, x + 87, y + 43, fill=hexc(c), r=4)
    cv.rect(0, 1240, 1080, 1440, fill=hexc("#e9dcc6"))                  # wainscot
    for x in range(0, 1081, 60):
        cv.line([(x, 1240), (x, 1440)], (200, 180, 150, 255), 3, cap=False)
    for r_ in range(10):                                                # checkered floor
        for c_ in range(12):
            y0 = FLOOR + r_ * r_ * 6 + r_ * 18
            y1 = FLOOR + (r_ + 1) ** 2 * 6 + (r_ + 1) * 18
            if (r_ + c_) % 2 == 0:
                cv.rect(c_ * 90, y0, c_ * 90 + 90, y1, fill=hexc("#2a2a3a"))
            else:
                cv.rect(c_ * 90, y0, c_ * 90 + 90, y1, fill=hexc("#f0e8dc"))
    # wood-fired oven (right)
    cv.pieslice(700, 640, 1060, 1000, 180, 360, fill=hexc("#c8b8a0"))
    cv.rect(700, 820, 1060, 1180, fill=hexc("#c8b8a0"))
    cv.pieslice(790, 820, 970, 1000, 180, 360, fill=hexc("#1a0f0a"))
    cv.rect(790, 910, 970, 990, fill=hexc("#1a0f0a"))
    cv.rect(760, 990, 1000, 1010, fill=hexc("#8a7a66"))
    cv.rect(840, 560, 920, 660, fill=hexc("#8a7a66"))
    # menu chalkboard (left)
    cv.rect(60, 330, 420, 760, fill=hexc("#6b4a36"), r=10)
    cv.rect(80, 350, 400, 740, fill=hexc("#22352b"), r=6)
    cv.text(240, 400, "MENU", 40, hexc("#f4efe4"))
    for k, (n, p) in enumerate((("Margherita", "18"), ("Salami", "20"), ("Funghi", "19"), ("Tonno", "21"))):
        cv.text(110, 470 + k * 60, n, 26, hexc("#e9e2d0"), anchor="lm")
        cv.text(380, 470 + k * 60, p + " €", 26, hexc("#ffd34d"), anchor="rm")
    # shelf with bottles
    cv.rect(440, 520, 680, 540, fill=hexc("#6b4a36"))
    for k, c in enumerate(("#2f6b3a", "#c9a46a", "#7a1f3d", "#2f6b3a", "#e0b64a")):
        x = 460 + k * 46
        cv.rect(x, 440, x + 26, 520, fill=hexc(c), r=6)
        cv.rect(x + 8, 418, x + 18, 442, fill=hexc(c))
    # sign
    cv.rect(380, 160, 700, 250, fill=hexc("#1d1b33"), r=20)
    cv.text(540, 205, "Pizzeria Bella", 44, hexc("#ffd34d"))


def bg_board(img, cv):
    img.paste(vgradient(img.width, img.height, [(0, "#3a1f1a"), (1, "#5a2e22")]))
    cv.rect(40, 560, 1040, 1460, fill=hexc("#6b4a36"), r=20)
    cv.rect(66, 586, 1014, 1434, fill=hexc("#21452f"), r=10)
    rng = np.random.default_rng(4)
    for _ in range(50):
        x, y = rng.uniform(80, 1000), rng.uniform(600, 1420)
        cv.line([(x, y), (x + rng.uniform(-60, 60), y + rng.uniform(-6, 6))], (255, 255, 255, 16), 6)


BGS = {"pizzeria": bg_pizzeria, "board": bg_board}
_BG = {}


def bg(name):
    if name not in _BG:
        p = os.path.join(CACHE, f"bg_{name}.png")
        if not os.path.exists(p):
            im = Image.new("RGB", (OUT_W * Z, OUT_H * Z))
            BGS[name](im, BCanvas(im, 0, 0, Z))
            im.save(p)
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
    if actors:
        actors(BCanvas(crop, box[0], box[1], Z))
    return crop.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS), box


def drift(cam, t, a=1.0):
    cx, cy, vh = cam
    k = vh / OUT_H
    return (cx + a * k * 8 * math.sin(t * 0.45), cy + a * k * 5 * math.sin(t * 0.33 + 1), vh * (1 + 0.01 * math.sin(t * 0.55)))


def room_life(cv, t):
    for k in range(7):                                   # oven fire
        fl = 1 + 0.25 * math.sin(t * 13 + k * 1.7)
        x = 820 + k * 22
        cv.poly([(x - 16, 990), (x + 16, 990), (x + 4 * math.sin(t * 9 + k), 990 - 60 * fl)],
                fill=[(255, 120, 30, 230), (255, 190, 60, 230)][k % 2])
    cv.circle(880, 950, 120, fill=(255, 150, 60, 30))
    pts = [(x, 290 + 40 * math.sin(math.pi * x / 1080)) for x in range(-20, 1101, 40)]   # string lights
    cv.line(pts, hexc("#2b1d14"), 3, cap=False)
    for i, (x, y) in enumerate(pts[1::2]):
        on = 0.6 + 0.4 * math.sin(t * 3 + i)
        cv.circle(x, y + 10, 20, fill=(255, 210, 120, int(45 * on)))
        cv.circle(x, y + 10, 7, fill=(255, 230, 160, 255))


FR = [(LEA, 300, 1), (TOM, 520, 1), (BEN, 740, -1)]


def friends(cv, t, kw_each=None, table=True, pizza=True):
    for i, (look, x, f) in enumerate(FR):
        shadow(cv, x, FLOOR, 80)
        kw = dict(t=t + i * 1.3, mood="smile")
        if kw_each:
            kw.update(kw_each(i) or {})
        draw_char(cv, x, FLOOR, look, 420, f if i < 2 else -1, **kw)
    if table:
        cv.rect(230, TABLE_Y, 820, TABLE_Y + 26, fill=hexc("#ffffff"))
        for k in range(14):
            cv.rect(230 + k * 42, TABLE_Y, 251 + k * 42, TABLE_Y + 26, fill=hexc("#d63a3a"))
        cv.poly([(230, TABLE_Y + 26), (820, TABLE_Y + 26), (800, TABLE_Y + 120), (250, TABLE_Y + 120)], fill=hexc("#f4efe4"))
        for k in range(10):
            cv.poly([(250 + k * 55, TABLE_Y + 26), (278 + k * 55, TABLE_Y + 26), (276 + k * 55, TABLE_Y + 120),
                     (252 + k * 55, TABLE_Y + 120)], fill=hexc("#d63a3a"))
        cv.rect(500, TABLE_Y + 120, 540, FLOOR, fill=hexc("#5a3a2c"))
        cv.ellipse(420, FLOOR - 12, 620, FLOOR + 8, fill=hexc("#5a3a2c"))
        if pizza:
            cv.ellipse(440, TABLE_Y - 26, 640, TABLE_Y + 6, fill=hexc("#e8b25a"))
            cv.ellipse(452, TABLE_Y - 22, 628, TABLE_Y + 2, fill=hexc("#d64a2a"))
            for k in range(7):
                cv.circle(470 + k * 24, TABLE_Y - 10 + (k % 2) * 6, 7, fill=hexc("#b8262a"))


# ------------------------------------------------------------------ scenes
HOOK = [(["3", "FREUNDE"], "#fff6e6", "#2b2140", -3, 130),
        (["1", "PIZZA-RECHNUNG"], "#ffd34d", "#2b2140", 2, 112),
        (["1 €", "FEHLT!"], "#e2574c", "#ffffff", -2, 136)]


def hook_times():
    k = "Drei Freunde"

    def w(a, b=None):
        return (wt(k, a, 0.0), wt(k, b, 0.0) if b else wt(k, a, 1.0))
    return [w("Drei", "Freunde"), w("Freunde", "eine"), w("eine", "Pizza"), w("Pizza", "und"),
            w("ein Euro", "Euro"), (wt(k, "fehlt", 0.0), wt(k, "Euro", 1.0))]


def sc_hook(t):
    t0, t1 = st("Drei Freunde"), en("Drei Freunde")
    z = smooth(prog(t, 0, t1))
    cam = (540, 1150 - 110 * z, 1000 + 700 * z)

    def act(cv):
        room_life(cv, t)
        friends(cv, t, lambda i: dict(talk=0.4 if (int(t * 1.5) + i) % 3 == 0 else 0.0))
        corgi(cv, 560, FLOOR + 50, 1.0, t, 1, wag=1.0)
    img, _ = stage("pizzeria", cam, act)
    img = Image.blend(img, Image.new("RGB", img.size, (15, 10, 30)), 0.3)
    karaoke(img, t, HOOK, t0, t1, [430, 620, 820], pop_k=0.4, first_pop=False, stagger=0.06, times=hook_times())
    return img


def sc_intro(t):
    t0, t1 = st("Lea, Tom"), en("Lea, Tom")
    tc = wt("Lea, Tom", "Unterm", 0.0)
    cam = keyframes(t, [(t0, (520, 1080, 1700)), (tc - 0.2, (520, 1080, 1700)), (tc + 0.6, (560, 1360, 900))])

    def act(cv):
        room_life(cv, t)
        friends(cv, t, lambda i: dict(talk=0.6 if t < tc and i == int((t - t0) * 1.5) % 3 else 0.0,
                                      look=(0.0, 0.8) if t > tc else (0, 0)))
        corgi(cv, 560, FLOOR + 50, 1.0, t, 1, beg=smooth(prog(t, tc, tc + 0.5)), wag=1.0)
    img, _ = stage("pizzeria", drift(cam, t), act)
    for i, (n, x) in enumerate((("LEA", 300), ("TOM", 520), ("BEN", 740))):
        if t < tc:
            pop_pill(img, t, wt("Lea, Tom", n.capitalize(), 0.0), x, 330 + (i % 2) * 110, n, 56,
                     bg=["#ffd34d", "#3fa7f5", "#37b26c"][i], fg="#2b2140" if i == 0 else "#ffffff", rot=(-3, 2, -2)[i])
    if t >= tc:
        pop_pill(img, t, tc, 540, 330, "PEPE, DER CORGI", 62, bg="#e2913f", fg="#ffffff", rot=-2)
    return img


def sc_bill(t):
    t0 = st("Die Rechnung")
    tj = wt("Die Rechnung", "Jeder", 0.0)

    def act(cv):
        room_life(cv, t)
        friends(cv, t, lambda i: dict(arm_f=("ik", (540 + (i - 1) * 60, TABLE_Y - 40))) if t > tj + i * 0.25 else {})
        corgi(cv, 560, FLOOR + 50, 1.0, t, 1, wag=0.6)
        for i in range(3):
            if t > tj + i * 0.25:
                p = smooth(prog(t, tj + i * 0.25, tj + i * 0.25 + 0.5))
                paste_sprite(cv, note_sprite(20), 300 + i * 220 + (540 - 300 - i * 220) * p * 0.6, TABLE_Y - 60 - 30 * i,
                             150, rot=-0.2 + i * 0.2)
    img, _ = stage("pizzeria", drift((540, 1080, 1500), t), act)
    pop_pill(img, t, t0 + 0.1, 540, 330, "RECHNUNG: 60 €", 76, bg="#fff6e6", rot=-2)
    pop_pill(img, t, tj, 540, 480, "JEDER ZAHLT 20 €", 62, bg="#ffd34d", rot=2)
    return img


CHEF_X, WAITER_X = 380, 700


def counter_scene(t, chef_kw=None, waiter_kw=None, coins=None, cam=(540, 1100, 1400)):
    def act(cv):
        room_life(cv, t)
        shadow(cv, CHEF_X, FLOOR, 90)
        kw = dict(t=t, mood="smile")
        kw.update(chef_kw or {})
        g = draw_char(cv, CHEF_X, FLOOR, CHEF, 460, 1, **kw)
        chef_hat(cv, g)
        mustache(cv, g)
        shadow(cv, WAITER_X, FLOOR, 80)
        kw = dict(t=t + 2, mood="smile")
        kw.update(waiter_kw or {})
        g2 = draw_char(cv, WAITER_X, FLOOR, WAITER, 430, -1, **kw)
        apron(cv, g2, 430)
        cv.poly([(g2["neck"][0] - 12, g2["neck"][1] + 6), (g2["neck"][0], g2["neck"][1] + 13),
                 (g2["neck"][0] - 12, g2["neck"][1] + 20)], fill=hexc("#c0392b"))
        cv.poly([(g2["neck"][0] + 12, g2["neck"][1] + 6), (g2["neck"][0], g2["neck"][1] + 13),
                 (g2["neck"][0] + 12, g2["neck"][1] + 20)], fill=hexc("#c0392b"))
        if coins:
            coins(cv, g, g2)
        corgi(cv, 900, FLOOR + 40, 0.8, t, -1, wag=0.8)
    return stage("pizzeria", drift(cam, t), act)


def sc_chef(t):
    t0, ta = st("Dann merkt"), wt("Dann merkt", "Aktionstag", 0.0)

    def coins(cv, g, g2):
        if t > ta:
            a = ease_out_back(prog(t, ta, ta + 0.35))
            hx, hy = g["hand_f"]
            cv.rect(hx - 10, hy - 170 * a, hx + 170 * a, hy - 10, fill=hexc("#ffd34d"), r=10)
            if a > 0.6:
                cv.text(hx + 80, hy - 120, "AKTION", 26, INK)
                cv.text(hx + 80, hy - 70, "55 €", 40, hexc("#c0392b"))
    img, _ = counter_scene(t, chef_kw=dict(arm_f=("ik", (CHEF_X + 120, FLOOR - 330)), talk=0.6, mood="smile"), coins=coins)
    pop_pill(img, t, t0 + 0.1, 540, 330, "AKTIONSTAG!", 80, bg="#e2574c", fg="#ffffff", rot=-3)
    pop_pill(img, t, wt("Dann merkt", "nur", 0.0), 540, 480, "NUR 55 € STATT 60 €", 56, bg="#fff6e6", rot=2)
    return img


def sc_give(t):
    t0 = st("Er gibt")

    def coins(cv, g, g2):
        p = smooth(prog(t, t0 + 0.3, t0 + 1.2))
        a = g["hand_f"]
        b = g2["hand_f"]
        for k in range(5):
            x = a[0] + (b[0] - a[0]) * p + (k - 2) * 18
            y = a[1] + (b[1] - a[1]) * p - 60 * math.sin(math.pi * p) - k * 4
            euro_coin(cv, x, y, 18)
    img, _ = counter_scene(t, chef_kw=dict(arm_f=("ik", (CHEF_X + 170, FLOOR - 270)), hand_f="open"),
                           waiter_kw=dict(arm_f=("ik", (WAITER_X - 150, FLOOR - 270)), hand_f="open"), coins=coins)
    pop_pill(img, t, t0 + 0.1, 540, 330, "5 € ZURÜCK", 84, bg="#ffd34d", rot=-2)
    return img


def sc_waiter(t):
    t0, th, tg = st("Der Kellner"), wt("Der Kellner", "heimlich", 0.0), wt("Der Kellner", "gibt", 0.0)
    if t < tg:
        def coins(cv, g, g2):
            x, hip = g2["hip"]
            p = smooth(prog(t, th, th + 0.6))
            for k in range(2):
                euro_coin(cv, g2["hand_f"][0] + (x + 20 - g2["hand_f"][0]) * p, g2["hand_f"][1] + (hip + 30 - g2["hand_f"][1]) * p - k * 8,
                          16, 1)
        img, _ = counter_scene(t, waiter_kw=dict(arm_f=("ik", (WAITER_X - 10, FLOOR - 200)), look=(-0.9, 0.0), mood="smirk",
                                                 hand_f="fist"), coins=coins, cam=(WAITER_X - 60, 1150, 950))
        pop_pill(img, t, th, 540, 330, "2 € HEIMLICH", 80, bg="#1d1b33", fg="#ffd34d", rot=-3)
        return img

    def act(cv):
        room_life(cv, t)
        friends(cv, t, lambda i: dict(arm_f=("ik", (FR[i][1] + (60 if i < 2 else -60), TABLE_Y - 80)), hand_f="open"))
        for i in range(3):
            ta = tg + 0.2 + i * 0.25
            if t > ta:
                p = smooth(prog(t, ta, ta + 0.4))
                euro_coin(cv, FR[i][1] + (60 if i < 2 else -60), TABLE_Y - 120 - 80 * (1 - p), 20)
        corgi(cv, 560, FLOOR + 50, 1.0, t, 1, wag=1.0)
    img, _ = stage("pizzeria", drift((540, 1080, 1500), t), act)
    pop_pill(img, t, tg, 540, 330, "JEDER BEKOMMT 1 €", 66, bg="#ffd34d", rot=-2)
    return img


def board_scene(t, rows, title=None, title_t=0.0, title_bg="#fff6e6", circle=None):
    def act(cv):
        for i, (txt, ts, col) in enumerate(rows):
            a = prog(t, ts, ts + 0.3)
            if a > 0:
                n = max(1, int(len(txt) * prog(t, ts, ts + 0.5)))
                cv.text(540, 700 + i * 140, txt[:n], 84, col + (int(255 * a),))
        if circle and t > circle[1]:
            p = prog(t, circle[1], circle[1] + 0.5)
            x, y, w_, h_ = circle[0]
            cv.arc(x - w_, y - h_, x + w_, y + h_, -90, -90 + 360 * p, (255, 211, 77, 255), 8)
    img, _ = stage("board", (540, 960, 1920), act)
    if title:
        pop_pill(img, t, title_t, 540, 380, title, 72, bg=title_bg, rot=-2)
    return img


def sc_math(t):
    t0, te = st("Also hat"), en("Also hat")
    w19 = wt("Also hat", "neunzehn", 0.0)
    w57 = wt("Also hat", "siebenundfünfzig", 0.0)
    w59 = wt("Also hat", "neunundfünfzig", 0.0)
    rows = [("20 € − 1 € = 19 €", w19 - 0.6, (240, 240, 230)), ("3 × 19 € = 57 €", w57 - 0.6, (240, 240, 230)),
            ("57 € + 2 € = 59 €", w59 - 0.6, (255, 211, 77)), ("BEZAHLT: 60 €", w59 + 0.4, (255, 150, 140))]
    return board_scene(t, rows, "DIE RECHNUNG", t0 + 0.05)


def sc_question(t):
    t0, tp, tc = st("Wo ist"), st("PAUSE"), st("Schreib's")
    rows = [("57 € + 2 € = 59 €", -1, (255, 211, 77)), ("BEZAHLT: 60 €", -1, (255, 150, 140))]
    img = board_scene(t, rows)
    pop_pill(img, t, t0, 540, 340, "WO IST DER", 92, bg="#fff6e6", rot=-3)
    pop_pill(img, t, t0 + 0.25, 540, 490, "LETZTE EURO?", 96, bg="#ffd34d", rot=2)
    d = ImageDraw.Draw(img, "RGBA")
    if tp - 0.2 < t < tc:
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            r = 18 + 10 * a
            cx = OUT_W / 2 - 70 + i * 70
            d.ellipse([cx - r, 1300 - r, cx + r, 1300 + r], fill=(255, 255, 255, int(120 + 135 * a)))
    if t >= tc:
        pop_pill(img, t, tc, 540, 1320, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff")
    return img


def sc_solution(t):
    t0, ti, td = st("Hier kommt"), st("In den"), st("Dazu die")
    rows = [("57 € = 55 € + 2 €", wt("In den", "fünfundfünfzig", 0.0) - 0.3, (240, 240, 230)),
            ("(Chef)   (Kellner)", wt("In den", "Kellner", 0.0) - 0.3, (190, 220, 200)),
            ("57 € + 3 € = 60 €", wt("Dazu die", "drei", 0.0) - 0.2, (255, 211, 77)),
            ("✓ ES FEHLT NICHTS", wt("Dazu die", "fehlt", 0.0) - 0.3, (140, 240, 160))]
    title = "DIE LÖSUNG" if t < ti else None
    img = board_scene(t, rows, title, t0 + 0.05, "#fff6e6")
    if t >= ti:
        pop_pill(img, t, ti, 540, 380, "DIE +2 € SIND SCHON DRIN!", 54, bg="#e2574c", fg="#ffffff", rot=-2)
    return img


def sc_outro(t):
    t0 = st("Folg mir")

    def act(cv):
        room_life(cv, t)
        corgi(cv, 520, FLOOR + 60, 1.6, t, 1, beg=0.5 + 0.5 * math.sin(t * 2), wag=1.5)
    img, _ = stage("pizzeria", drift((540, 1200, 1300), t), act)
    img = Image.blend(img, Image.new("RGB", img.size, (15, 10, 30)), 0.25)
    pop_pill(img, t, t0, 540, 360, "HÄTTEST DU'S GEWUSST?", 60, bg="#fff6e6", rot=-2)
    followed = t > t0 + 1.0
    pill3d(img, 540, 520, "GEFOLGT  ✓" if followed else "+  FOLGEN", 74, bg="#37b26c" if followed else "#e2574c",
           fg="#ffffff", scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.5)))
    return img


SCENES = [(0.0, sc_hook), (st("Lea, Tom") - 0.05, sc_intro), (st("Die Rechnung") - 0.05, sc_bill),
          (st("Dann merkt") - 0.05, sc_chef), (st("Er gibt") - 0.05, sc_give), (st("Der Kellner") - 0.05, sc_waiter),
          (st("Also hat") - 0.05, sc_math), (st("Wo ist") - 0.05, sc_question), (st("Hier kommt") - 0.05, sc_solution),
          (st("Folg mir") - 0.05, sc_outro)]


def frame_at(t):
    _T[0] = t
    idx = max(i for i, (s0, _) in enumerate(SCENES) if t >= s0)
    img = SCENES[idx][1](t)
    if idx > 0:
        s0 = SCENES[idx][0]
        if t < s0 + XFADE:
            prev = SCENES[idx - 1][1](t)
            img = Image.blend(prev, img, smooth(prog(t, s0, s0 + XFADE)))
    if t > END - 0.4:
        img = Image.blend(img, Image.new("RGB", img.size, (20, 14, 36)), prog(t, END - 0.4, END))
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
