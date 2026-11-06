"""TikTok #7 – Eine Million sofort oder 1 Cent pro Sekunde ein Jahr lang? (Leon vs. Mia)

usage:  python3 make_video.py            -> renders video.mp4 (needs timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from toolkit import _shade
from fx3d import BCanvas, pill3d, pop_pill, burst, karaoke
from people import Look, draw_char, talk_arm
from money import note_sprite, coin_sprite, paste_sprite

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
Z = 2
INK = hexc("#1d1b33")

LEON = Look("#f1c7a3", "#f2c94c", "#ff7a2f", "#2b3550", "#ffffff", hair_style="quiff", top_style="bomber",
            under="#1d1b33", trim="#ffb703", shoe_trim="#ff7a2f", eyes="#3a7bd5")
MIA = Look("#a8714f", "#2a1b14", "#3cc9a4", "#34495e", "#ff6f91", hair_style="long", top_style="hoodie",
           trim="#2a9d8f", glasses=True, lashes=True, eyes="#4a2c1a")
GUESTS = [Look("#e0ac69", "#3b2a20", "#e84393", "#2d3436", "#ffffff", hair_style="ponytail", top_style="tee", lashes=True),
          Look("#8d5524", "#111111", "#00b894", "#2d3436", "#fdcb6e", hair_style="curly", top_style="hoodie"),
          Look("#ffdbac", "#c0392b", "#6c5ce7", "#2d3436", "#ffffff", hair_style="short", top_style="bomber",
               trim="#a29bfe")]
WALKERS = [Look("#f3d2b5", "#7b4a2a", "#e17055", "#3b3b58", "#f5f6fa", hair_style="bun", top_style="tee", lashes=True),
           Look("#c68642", "#1b1b1b", "#0984e3", "#2d3436", "#dfe6e9", hair_style="short", top_style="hoodie"),
           Look("#ffe0bd", "#d4a373", "#fdcb6e", "#6c5ce7", "#ffffff", hair_style="ponytail", top_style="tee", lashes=True),
           Look("#8d5524", "#2d1e12", "#00b894", "#34495e", "#ffeaa7", hair_style="curly", top_style="bomber",
                trim="#55efc4")]

# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Eine Million", "Leon muss", "Die Million", "Ein Cent?", "Aber Mia", "Ich nehme", "Viel Glück", "Wetten",
        "Und das Rennen", "Erste Sekunde", "Leon lacht", "Und weil er", "Einen Sportwagen", "Eine Diamant",
        "Und eine Pool", "Ich bin Millionär", "Während Leon", "Sechs Monate", "Na, Mia", "Am Ende", "Trotzdem bucht",
        "Denn beide", "Es wird knapp", "Dann kommt", "Leon öffnet", "Trotz Sportwagen", "Und du", "Ein Cent pro",
        "Leon fängt", "Wie viel", "Schreib's"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 0.8
XFADE = 0.22


def st(k):
    return S[K[k]]


def en(k):
    return E[K[k]]


def wt(key, word, frac=0.3):
    seg = next(x for x in TIM if x["text"].startswith(key))
    i = seg["text"].find(word)
    f = (i + len(word) * frac) / len(seg["text"])
    return seg["start"] + (seg["end"] - seg["start"]) * f


# ------------------------------------------------------------------ helpers
def money(v):
    return f"{v:,.0f}".replace(",", ".") + " €"


def head_geo(x, y, look, h, f=1, lean=0.0, bounce=0.0):
    h = h * 1.12
    r = 0.084 * h
    hy = y - bounce - 0.875 * h
    hx = x + f * 0.017 * h
    fx = hx + f * r * 0.3
    return dict(hx=hx, hy=hy, r=r, fx=fx, ey=hy + r * 0.05)


def _char_kw(h, f, t, kw):
    out = dict(t=t, talk=kw.get("talk", 0.0), bounce=kw.get("bounce", 0.0), blink=kw.get("blink"),
               mood=kw.get("mood", "smile"))
    if kw.get("lean"):
        out["lean"] = math.asin(clamp(kw["lean"] / (0.3 * h), -0.6, 0.6))
    if kw.get("phase") is not None:
        out["walk"] = kw["phase"]
    if kw.get("reach") is not None:
        out["arm_f"] = ("ik", kw["reach"])
    a = kw.get("arms_up", 0.0)
    if a:
        out["arm_f"] = ("ang", 0.25 + 2.45 * a, 0.25 + 0.1 * math.sin(t * 7))
        out["arm_b"] = ("ang", -(0.25 + 2.45 * a), -0.25 - 0.1 * math.sin(t * 7 + 1))
    if kw.get("wave"):
        w = kw["wave"]
        out["arm_f"] = ("ang", 2.45 + 0.2 * math.sin(w), 0.55 + 0.45 * math.sin(w))
    for k in ("arm_f", "arm_b", "look", "brows", "head_tilt", "squash", "hand_f", "hand_b", "point_f", "shrug",
              "glasses_dy", "breathe", "sway"):
        if k in kw:
            out[k] = kw[k]
    if out["talk"] > 0.05 and "arm_f" not in out and "walk" not in out:
        out["arm_f"] = talk_arm(t, 0.8, x_seed(h))
    return out


def x_seed(h):
    return (h * 0.37) % 6.28


def leon(cv, x, y, h=420, f=1, t=0.0, shades=False, chain=False, crown=0.0, **kw):
    g = draw_char(cv, x, y, LEON, h * 1.12, f, **_char_kw(h * 1.12, f, t, kw))
    r = g["r"]
    hx, hy = g["head"]
    if chain:
        nx, sy = g["neck"][0], g["sh_y"]
        pts = [(nx + f * 0.01 * h + math.sin(a) * 0.05 * h, sy + 0.02 * h + (1 - math.cos(a)) * 0.1 * h)
               for a in np.linspace(-1.1, 1.1, 14)]
        for p in pts:
            cv.circle(p[0], p[1], h * 0.009, fill=hexc("#ffd34d"))
        bx, by = nx + f * 0.01 * h, sy + 0.08 * h
        cv.poly([(bx, by - h * 0.022), (bx + h * 0.018, by), (bx, by + h * 0.027), (bx - h * 0.018, by)],
                fill=hexc("#bdf3ff"))
        if math.sin(t * 5) > 0.6:
            cv.line([(bx - h * 0.03, by - h * 0.03), (bx + h * 0.03, by + h * 0.03)], (255, 255, 255, 220), 2)
    if shades:
        for ex in (g["fx"] - r * 0.33, g["fx"] + r * 0.33):
            cv.rect(ex - r * 0.25, g["ey"] - r * 0.18, ex + r * 0.25, g["ey"] + r * 0.17, fill=hexc("#111522"), r=r * 0.09)
            cv.line([(ex - r * 0.15, g["ey"] - r * 0.08), (ex - r * 0.03, g["ey"] - r * 0.12)], (255, 255, 255, 170), r * 0.05)
        cv.line([(g["fx"] - r * 0.1, g["ey"] - r * 0.08), (g["fx"] + r * 0.1, g["ey"] - r * 0.08)], hexc("#111522"), r * 0.07)
        cv.line([(g["fx"] - f * r * 0.58, g["ey"] - r * 0.06), (hx - f * r * 0.68, g["ey"] - r * 0.1)], hexc("#111522"), r * 0.06)
    if crown > 0.02:
        cy = hy - r * 1.55 - (1 - crown) * r * 2
        cw = r * 0.75 * crown
        cv.poly([(hx - cw, cy + r * 0.35), (hx - cw, cy - r * 0.1), (hx - cw * 0.5, cy + r * 0.12),
                 (hx, cy - r * 0.3), (hx + cw * 0.5, cy + r * 0.12), (hx + cw, cy - r * 0.1),
                 (hx + cw, cy + r * 0.35)], fill=hexc("#ffd34d"))
        for k in (-1, 0, 1):
            cv.circle(hx + k * cw * 0.5, cy + r * 0.24, r * 0.07, fill=hexc("#e2574c" if k else "#3fa7f5"))
    g.update(hx=hx, hy=hy)
    return g["hand_f"], g


def mia(cv, x, y, h=420, f=-1, t=None, **kw):
    t = kw.pop("tt", t if t is not None else _T[0])
    g = draw_char(cv, x, y, MIA, h * 1.12, f, **_char_kw(h * 1.12, f, t, kw))
    g.update(hx=g["head"][0], hy=g["head"][1])
    return g["hand_f"], g


_T = [0.0]


def shadow(cv, x, y, w):
    cv.ellipse(x - w, y - w * 0.12, x + w, y + w * 0.12, fill=(20, 10, 30, 70))


def coin(cv, x, y, r, rot=0.0):
    """real-looking 1 euro cent (flips with rot)"""
    paste_sprite(cv, coin_sprite(), x, y, 2 * r, squash=math.cos(rot))


def banknote(cv, x, y, s, rot, value=None):
    """real-looking euro banknote"""
    if value is None:
        value = (100, 50, 200, 100)[int(abs(x * 7 + y * 3)) % 4]
    paste_sprite(cv, note_sprite(value), x, y, 130 * s, rot=rot)


def stopwatch(cv, x, y, r, t):
    cv.rect(x - r * 0.18, y - r * 1.32, x + r * 0.18, y - r * 1.08, fill=hexc("#e2574c"), r=r * 0.05)
    cv.circle(x, y, r * 1.08, fill=INK)
    cv.circle(x, y, r, fill=hexc("#ffffff"))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        cv.line([(x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82), (x + math.sin(a) * r * 0.92, y - math.cos(a) * r * 0.92)],
                INK, r * 0.05)
    a = t * 2 * math.pi
    cv.line([(x, y), (x + math.sin(a) * r * 0.78, y - math.cos(a) * r * 0.78)], hexc("#e2574c"), r * 0.07)
    cv.circle(x, y, r * 0.08, fill=INK)


def sports_car(cv, x, y, s=1.0, t=0.0, wheel=0.0, col="#ffc93c"):
    c = hexc(col)
    cd = _shade(c, 0.25)
    cv.ellipse(x - 330 * s, y - 16 * s, x + 330 * s, y + 22 * s, fill=(20, 10, 30, 80))
    cv.poly([(x - 320 * s, y - 40 * s), (x - 300 * s, y - 120 * s), (x - 120 * s, y - 150 * s), (x - 40 * s, y - 225 * s),
             (x + 120 * s, y - 230 * s), (x + 230 * s, y - 150 * s), (x + 320 * s, y - 120 * s), (x + 335 * s, y - 40 * s)],
            fill=c)
    cv.poly([(x - 20 * s, y - 210 * s), (x + 110 * s, y - 214 * s), (x + 195 * s, y - 150 * s), (x - 90 * s, y - 150 * s)],
            fill=hexc("#2b3a55"))
    cv.line([(x + 50 * s, y - 212 * s), (x + 50 * s, y - 150 * s)], c, 8 * s)
    cv.poly([(x - 60 * s, y - 205 * s), (x + 10 * s, y - 208 * s), (x - 40 * s, y - 158 * s)], fill=(255, 255, 255, 70))
    cv.rect(x - 320 * s, y - 70 * s, x + 335 * s, y - 40 * s, fill=cd)
    cv.line([(x - 280 * s, y - 105 * s), (x + 290 * s, y - 100 * s)], _shade(c, -0.3) if False else (255, 255, 255, 120), 5 * s)
    cv.rect(x + 300 * s, y - 115 * s, x + 336 * s, y - 95 * s, fill=hexc("#fff3b0"), r=6 * s)
    cv.rect(x - 322 * s, y - 112 * s, x - 296 * s, y - 94 * s, fill=hexc("#e2574c"), r=5 * s)
    for wx in (x - 190 * s, x + 200 * s):
        cv.circle(wx, y - 40 * s, 62 * s, fill=hexc("#1b1b24"))
        cv.circle(wx, y - 40 * s, 36 * s, fill=hexc("#c9ced8"))
        for k in range(5):
            a = wheel + k * 2 * math.pi / 5
            cv.line([(wx, y - 40 * s), (wx + math.cos(a) * 32 * s, y - 40 * s + math.sin(a) * 32 * s)], hexc("#8a90a0"),
                    7 * s)
        cv.circle(wx, y - 40 * s, 9 * s, fill=hexc("#555b6e"))


def piggy(cv, x, y, s=1.0, coins=0):
    pink, pd = hexc("#ff9fb7"), hexc("#f27a99")
    cv.ellipse(x - 90 * s, y - 120 * s, x + 90 * s, y, fill=pink)
    cv.circle(x + 80 * s, y - 70 * s, 30 * s, fill=pink)
    cv.ellipse(x + 92 * s, y - 84 * s, x + 122 * s, y - 56 * s, fill=pd)
    cv.circle(x + 102 * s, y - 70 * s, 4 * s, fill=INK)
    cv.circle(x + 112 * s, y - 70 * s, 4 * s, fill=INK)
    cv.circle(x + 60 * s, y - 92 * s, 6 * s, fill=INK)
    cv.poly([(x + 40 * s, y - 118 * s), (x + 70 * s, y - 150 * s), (x + 74 * s, y - 108 * s)], fill=pd)
    for lx in (-50, -15, 25, 55):
        cv.rect(x + lx * s, y - 20 * s, x + (lx + 22) * s, y + 14 * s, fill=pd, r=6 * s)
    cv.rect(x - 30 * s, y - 124 * s, x + 30 * s, y - 114 * s, fill=hexc("#7a3348"), r=4 * s)
    cv.ellipse(x - 60 * s, y - 100 * s, x - 10 * s, y - 70 * s, fill=(255, 255, 255, 90))


def phone(cv, x, y, s, screen_fn=None):
    cv.rect(x - 150 * s, y - 300 * s, x + 150 * s, y + 300 * s, fill=INK, r=40 * s)
    cv.rect(x - 136 * s, y - 286 * s, x + 136 * s, y + 286 * s, fill=hexc("#f6f7fb"), r=30 * s)
    cv.rect(x - 40 * s, y - 280 * s, x + 40 * s, y - 266 * s, fill=INK, r=7 * s)
    if screen_fn:
        screen_fn(cv, x, y, s)


def calendar(cv, x, y, s, top, big, col="#e2574c"):
    cv.rect(x - 160 * s, y - 170 * s, x + 170 * s, y + 190 * s, fill=(20, 10, 30, 70), r=30 * s)
    cv.rect(x - 170 * s, y - 180 * s, x + 160 * s, y + 180 * s, fill=hexc("#ffffff"), r=30 * s)
    cv.rect(x - 170 * s, y - 180 * s, x + 160 * s, y - 70 * s, fill=hexc(col), r=30 * s)
    cv.rect(x - 170 * s, y - 100 * s, x + 160 * s, y - 70 * s, fill=hexc(col))
    cv.text(x - 5 * s, y - 125 * s, top, 54 * s, hexc("#ffffff"))
    cv.text(x - 5 * s, y + 60 * s, big, 150 * s, INK)
    for k in (-1, 1):
        cv.rect(x - 5 * s + k * 90 * s - 10 * s, y - 210 * s, x - 5 * s + k * 90 * s + 10 * s, y - 150 * s, fill=hexc("#555b6e"),
                r=8 * s)


def confetti(cv, t, n=60, seed=3, area=(0, 0, 1080, 1500)):
    rng = np.random.default_rng(seed)
    cols = ["#ffd34d", "#e2574c", "#3cc9a4", "#6c5ce7", "#ff9fb7", "#3fa7f5"]
    for i in range(n):
        x0, sp, ph = rng.uniform(area[0], area[2]), rng.uniform(120, 260), rng.uniform(0, 10)
        y = area[1] + ((t * sp + ph * 200) % (area[3] - area[1]))
        x = x0 + 30 * math.sin(t * 2 + ph)
        a = t * 4 + ph
        cv.poly([(x + math.cos(a) * 10, y + math.sin(a) * 5), (x - math.sin(a) * 6, y + math.cos(a) * 10),
                 (x - math.cos(a) * 10, y - math.sin(a) * 5), (x + math.sin(a) * 6, y - math.cos(a) * 10)],
                fill=hexc(cols[i % len(cols)]))


# ------------------------------------------------------------------ static backgrounds (screen world 1080x1920, 2x)
def _bg(name, fn):
    p = os.path.join(CACHE, f"bg_{name}.png")
    if not os.path.exists(p):
        img = Image.new("RGB", (W * Z, H * Z) if False else (OUT_W * Z, OUT_H * Z), (0, 0, 0))
        fn(img, BCanvas(img, 0, 0, Z))
        img.save(p)
    return Image.open(p).convert("RGB")


def grad(img, stops):
    g = vgradient(img.width, img.height, stops)
    img.paste(g)


def skyline(cv, base, cols, seed, lit=0.5, h0=200, h1=620):
    rng = np.random.default_rng(seed)
    x = -40
    while x < 1120:
        w = rng.uniform(90, 170)
        hgt = rng.uniform(h0, h1)
        cv.rect(x, base - hgt, x + w, base, fill=hexc(cols[int(rng.integers(0, len(cols)))]))
        for wy in np.arange(base - hgt + 30, base - 20, 44):
            for wx in np.arange(x + 16, x + w - 20, 34):
                if rng.random() < lit:
                    cv.rect(wx, wy, wx + 16, wy + 22, fill=(255, 226, 140, 220))
        x += w + rng.uniform(4, 20)


def bg_roof(img, cv):
    grad(img, [(0, "#2b1d5c"), (0.35, "#8a3e7c"), (0.55, "#f2795a"), (0.66, "#ffc27a"), (1, "#ffc27a")])
    cv.circle(780, 1000, 120, fill=(255, 220, 150, 255))
    skyline(cv, 1190, ["#4a2c6b", "#5a3478", "#3d2560"], 2, 0.35, 200, 650)
    skyline(cv, 1190, ["#2e1b4a", "#26163f"], 5, 0.25, 80, 330)
    cv.rect(0, 1180, 1080, 1920, fill=hexc("#b48a78"))
    for k in range(10):                              # tiles in perspective
        y = 1180 + k * k * 9
        cv.line([(0, y), (1080, y)], (140, 100, 90, 255), 3, cap=False)
    for k in range(-8, 9):
        cv.line([(540 + k * 60, 1180), (540 + k * 220, 1920)], (140, 100, 90, 255), 3, cap=False)
    cv.rect(0, 1100, 1080, 1112, fill=hexc("#2e2a3a"))       # railing
    for x in range(0, 1081, 60):
        cv.rect(x, 1100, x + 8, 1185, fill=hexc("#2e2a3a"))
    cv.rect(0, 1175, 1080, 1190, fill=hexc("#2e2a3a"))
    for x in (60, 1000):                                      # plants
        cv.rect(x - 50, 1310, x + 50, 1420, fill=hexc("#c66b3d"), r=10)
        for a in range(7):
            ang = math.pi + a * math.pi / 6
            cv.line([(x, 1310), (x + math.cos(ang) * 90, 1310 + math.sin(ang) * 140)], hexc("#3f8a4c"), 18)


def bg_mia_room(img, cv):
    grad(img, [(0, "#d7f3ea"), (1, "#b5e2d3")])
    cv.rect(0, 1300, 1080, 1920, fill=hexc("#d9a46c"))
    for k in range(8):
        cv.line([(k * 150, 1300), (k * 150 - 80, 1920)], (190, 130, 80, 255), 4, cap=False)
    cv.rect(0, 1290, 1080, 1306, fill=hexc("#ffffff"))
    cv.rect(620, 380, 1020, 900, fill=hexc("#ffffff"), r=16)    # window frame (content drawn per frame)
    cv.rect(40, 420, 560, 720, fill=INK, r=24)                    # wall screen
    cv.rect(56, 436, 544, 704, fill=hexc("#10162b"), r=18)
    cv.rect(40, 1060, 600, 1090, fill=hexc("#8d5a3b"), r=8)       # desk
    cv.rect(70, 1090, 100, 1300, fill=hexc("#6e4429"))
    cv.rect(540, 1090, 570, 1300, fill=hexc("#6e4429"))
    cv.rect(130, 930, 350, 1060, fill=hexc("#3d4466"), r=10)      # laptop
    cv.rect(142, 942, 338, 1048, fill=hexc("#8fd3ff"), r=6)
    cv.rect(100, 1052, 380, 1066, fill=hexc("#555b6e"), r=6)
    for i, c in enumerate(["#e2574c", "#3fa7f5", "#ffd34d", "#6c5ce7", "#3cc9a4"]):   # books on shelf
        cv.rect(80 + i * 34, 250, 108 + i * 34, 380, fill=hexc(c), r=4)
    cv.rect(60, 380, 320, 394, fill=hexc("#8d5a3b"))
    cv.circle(840, 1180, 60, fill=hexc("#3f8a4c"))
    cv.rect(800, 1200, 880, 1300, fill=hexc("#c66b3d"), r=10)


def bg_loft(img, cv):
    grad(img, [(0, "#14112b"), (1, "#2a1f4d")])
    cv.rect(110, 260, 970, 1060, fill=hexc("#0b1430"), r=10)
    sky = vgradient(860 * Z, 800 * Z, [(0, "#0b1033"), (1, "#3a2a6e")])
    img.paste(sky, (110 * Z, 260 * Z))
    sub = BCanvas(img, 0, 0, Z)
    skyline(sub, 1060, ["#1b1f45", "#232a5a", "#1a1a3a"], 8, 0.4, 250, 650)
    for x in (110, 395, 685, 960):
        cv.rect(x, 260, x + 12, 1060, fill=hexc("#2e2a3a"))
    cv.rect(110, 650, 970, 662, fill=hexc("#2e2a3a"))
    cv.rect(0, 220, 1080, 236, fill=hexc("#ff4fa3"))              # neon strips
    cv.rect(0, 1068, 1080, 1078, fill=hexc("#38e1ff"))
    cv.rect(0, 1240, 1080, 1920, fill=hexc("#3b1f5e"))
    for k in range(6):
        cv.line([(0, 1240 + k * k * 14), (1080, 1240 + k * k * 14)], (90, 50, 130, 255), 3, cap=False)
    cv.rect(120, 1080, 960, 1250, fill=hexc("#d8a53a"), r=40)     # gold sofa
    cv.rect(90, 1140, 990, 1290, fill=hexc("#e8b84a"), r=40)
    cv.rect(0, 1300, 1080, 1306, fill=(255, 79, 163, 120))


def bg_street(img, cv):
    grad(img, [(0, "#7ec8f0"), (0.6, "#c9ecfb"), (1, "#c9ecfb")])
    cols = ["#f4a259", "#f6d6ad", "#8cc0de", "#e5989b", "#b5e48c"]
    x = -20
    for i in range(7):
        w = 220
        hgt = 520 + (i % 3) * 90
        cv.rect(x, 1180 - hgt, x + w, 1180, fill=hexc(cols[i % 5]))
        cv.poly([(x - 10, 1180 - hgt), (x + w / 2, 1180 - hgt - 80), (x + w + 10, 1180 - hgt)], fill=hexc("#c0392b"))
        for wy in range(int(1180 - hgt + 60), 1080, 120):
            for wx in (x + 40, x + 130):
                cv.rect(wx, wy, wx + 50, wy + 70, fill=hexc("#e9f6ff"))
                cv.rect(wx, wy, wx + 50, wy + 10, fill=hexc("#6c7a89"))
        cv.rect(x + 80, 1060, x + 140, 1180, fill=hexc("#6e4429"))
        x += w
    cv.rect(0, 1180, 1080, 1260, fill=hexc("#d6d6d6"))
    cv.rect(0, 1260, 1080, 1920, fill=hexc("#555b6e"))
    for k in range(6):
        cv.rect(k * 220 + 40, 1580, k * 220 + 160, 1596, fill=hexc("#ffffff"))
    for x in (160, 860):
        cv.rect(x - 8, 900, x + 8, 1180, fill=hexc("#6e4429"))
        cv.circle(x, 880, 90, fill=hexc("#5fae5a"))


def bg_showroom(img, cv):
    grad(img, [(0, "#0f2d3a"), (0.6, "#14505e"), (1, "#0f2d3a")])
    for k, x in enumerate((200, 540, 880)):
        cv.poly([(x - 30, 0), (x + 30, 0), (x + 260, 1500), (x - 260, 1500)], fill=(255, 255, 255, 22))
    cv.ellipse(60, 1300, 1020, 1560, fill=hexc("#1d6e7c"))
    cv.ellipse(120, 1320, 960, 1520, fill=hexc("#2a8c99"))


def bg_jeweler(img, cv):
    grad(img, [(0, "#2a0f3d"), (1, "#5b1f6e")])
    for x in range(0, 1080, 90):
        cv.rect(x, 0, x + 45, 1920, fill=(255, 255, 255, 10))
    cv.ellipse(140, 1350, 940, 1560, fill=hexc("#1b0a26"))
    cv.poly([(330, 1460), (750, 1460), (660, 1100), (420, 1100)], fill=hexc("#f1e6ef"))    # display bust
    cv.ellipse(330, 840, 750, 1160, fill=hexc("#f1e6ef"))
    cv.rect(470, 700, 610, 900, fill=hexc("#e6d6e3"), r=50)
    cv.ellipse(350, 860, 520, 1120, fill=(255, 255, 255, 120))


def bg_pool(img, cv):
    grad(img, [(0, "#0d1b4a"), (0.6, "#2b3d8f"), (1, "#2b3d8f")])
    cv.rect(0, 640, 1080, 1060, fill=hexc("#f3e7d3"))           # villa
    cv.rect(0, 610, 1080, 650, fill=hexc("#d8c7ab"))
    for x in (60, 330, 600, 870):
        cv.rect(x, 720, x + 160, 960, fill=hexc("#ffcf6b"))
        cv.rect(x + 76, 720, x + 84, 960, fill=hexc("#d8c7ab"))
    cv.rect(0, 1060, 1080, 1140, fill=hexc("#e9dcc6"))
    cv.rect(0, 1140, 1080, 1440, fill=hexc("#2fb7e8"))
    cv.rect(0, 1140, 1080, 1160, fill=hexc("#ffffff"))
    cv.rect(0, 1440, 1080, 1920, fill=hexc("#e9dcc6"))
    for x in (-20, 1040):
        cv.line([(x, 1060), (x + 30, 700), (x + 50, 520)], hexc("#7a4f2e"), 22)
        for a in range(7):
            ang = math.pi + a * math.pi / 6
            cv.line([(x + 50, 520), (x + 50 + math.cos(ang) * 170, 520 + math.sin(ang) * 70 + 70)], hexc("#3f8a4c"), 22)


def bg_sea(img, cv):
    grad(img, [(0, "#4fb3ff"), (0.5, "#bfe6ff"), (0.55, "#1f8fd6"), (1, "#0a4f8a")])
    cv.circle(820, 620, 110, fill=hexc("#fff3b0"))
    for k in range(14):
        y = 1080 + k * k * 5
        cv.line([(0, y), (1080, y)], (255, 255, 255, 60), 3, cap=False)
    cv.poly([(0, 1056), (260, 980), (420, 1056)], fill=hexc("#6aa36f"))


def bg_night(img, cv):
    grad(img, [(0, "#050816"), (0.7, "#1b1f4a"), (1, "#1b1f4a")])
    skyline(cv, 1500, ["#11142e", "#151a3a", "#0e1128"], 11, 0.45, 300, 800)
    cv.rect(0, 1500, 1080, 1920, fill=hexc("#0a0c1f"))


def bg_board(img, cv):
    grad(img, [(0, "#1f3b2c"), (1, "#173024")])
    cv.rect(30, 230, 1050, 1500, fill=hexc("#6e4429"), r=20)
    cv.rect(56, 256, 1024, 1474, fill=hexc("#21452f"), r=10)
    rng = np.random.default_rng(4)
    for _ in range(60):
        x, y = rng.uniform(70, 1010), rng.uniform(270, 1460)
        cv.line([(x, y), (x + rng.uniform(-60, 60), y + rng.uniform(-6, 6))], (255, 255, 255, 18), 6)


# ------------------------------------------------------------------ fairground (main set)
WHEEL = (800, 560, 300)
TRACK = lambda x: 800 + 110 * math.sin(x / 150 + 0.6) - 60 * math.sin(x / 61)


def bg_fair(img, cv):
    grad(img, [(0, "#17194f"), (0.22, "#4a2a84"), (0.42, "#c9467e"), (0.52, "#ff9d5c"), (0.57, "#ffc387"), (1, "#ffc387")])
    for i in range(40):
        rng = np.random.default_rng(i)
        cv.circle(rng.uniform(0, 1080), rng.uniform(40, 520), rng.uniform(1.5, 3), fill=(255, 255, 255, 160))
    skyline(cv, 1030, ["#3b2468", "#45297a", "#33205e"], 9, 0.35, 90, 300)
    # roller coaster lattice
    xs = list(range(-20, 1101, 10))
    for x in range(0, 1081, 54):
        y = TRACK(x)
        cv.line([(x, y), (x, 1040)], hexc("#3a2a6a"), 7, cap=False)
        cv.line([(x, y + 40), (x + 54, min(1040, TRACK(x + 54) + 140))], hexc("#3a2a6a"), 4, cap=False)
    cv.line([(x, TRACK(x)) for x in xs], hexc("#e2574c"), 12, cap=False)
    cv.line([(x, TRACK(x) + 14) for x in xs], hexc("#2b1d4f"), 6, cap=False)
    # Ferris wheel legs + hub
    wx, wy, R = WHEEL
    for dx in (-150, 150):
        cv.line([(wx, wy), (wx + dx, 1060)], hexc("#efe9ff"), 18)
        cv.line([(wx, wy), (wx + dx, 1060)], hexc("#b9b0d8"), 6)
    cv.line([(wx - 110, 920), (wx + 110, 920)], hexc("#efe9ff"), 10)
    # booths
    for i, (x0, x1, name, c1) in enumerate(((440, 640, "POPCORN", "#e2574c"), (660, 860, "LOSE", "#3fa7f5"),
                                           (880, 1100, "ZUCKERWATTE", "#ff6fae"))):
        cv.rect(x0, 960, x1, 1110, fill=hexc("#fff3dc"))
        cv.rect(x0, 1040, x1, 1110, fill=hexc(c1))
        cv.rect(x0 + 20, 980, x1 - 20, 1035, fill=hexc("#3d2a1e"))
        n = 6
        for k in range(n):
            xa, xb = x0 + (x1 - x0) * k / n, x0 + (x1 - x0) * (k + 1) / n
            cv.rect(xa, 900, xb, 965, fill=hexc(c1 if k % 2 == 0 else "#ffffff"))
            cv.pieslice(xa, 940, xb, 990, 0, 180, fill=hexc(c1 if k % 2 == 0 else "#ffffff"))
        cv.rect(x0 + 10, 860, x1 - 10, 902, fill=hexc("#ffd34d"), r=10)
        fs = 30
        while font(fs).getbbox(name)[2] > (x1 - x0) - 40:
            fs -= 2
        cv.text((x0 + x1) / 2, 881, name, fs, hexc("#2b2140"))
    # carousel roof + pole + platform
    cx = 210
    cv.rect(cx - 10, 760, cx + 10, 1080, fill=hexc("#ffd34d"))
    cv.ellipse(cx - 200, 1050, cx + 200, 1110, fill=hexc("#7a3f8f"))
    cv.ellipse(cx - 200, 1040, cx + 200, 1095, fill=hexc("#a45bbd"))
    for k in range(10):
        xa, xb = cx - 210 + 42 * k, cx - 210 + 42 * (k + 1)
        cv.poly([(cx, 700), (xa, 860), (xb, 860)], fill=hexc("#e2574c" if k % 2 == 0 else "#fff3dc"))
        cv.pieslice(xa, 840, xb, 885, 0, 180, fill=hexc("#e2574c" if k % 2 == 0 else "#fff3dc"))
    cv.circle(cx, 696, 14, fill=hexc("#ffd34d"))
    cv.line([(cx, 682), (cx, 640)], hexc("#2b2140"), 4)
    cv.poly([(cx, 640), (cx + 40, 652), (cx, 664)], fill=hexc("#3cc9a4"))
    # plaza ground
    cv.rect(0, 1110, 1080, 1920, fill=hexc("#b88e6a"))
    vg = vgradient(1080 * Z, 810 * Z, [(0, "#9c7656"), (1, "#d2a983")])
    img.paste(vg, (0, 1110 * Z))
    for row in range(16):
        y = 1120 + row * row * 3.3 + row * 14
        hgt = 10 + row * 2.2
        off = (row % 2) * 30
        for x in range(-60, 1140, 60 + row * 4):
            cv.ellipse(x + off, y, x + off + 46 + row * 4, y + hgt, fill=(120, 85, 60, 60))
    # lamp posts
    for x in (30, 1050):
        cv.rect(x - 8, 820, x + 8, 1330, fill=hexc("#2b2140"))
        cv.rect(x - 26, 800, x + 26, 830, fill=hexc("#2b2140"), r=8)


def fair_life(cv, t, crowd=True):
    wx, wy, R = WHEEL
    a0 = t * 0.22
    # wheel
    cv.circle(wx, wy, R, outline=hexc("#efe9ff"), width=10)
    cv.circle(wx, wy, R - 26, outline=hexc("#c9c1ea"), width=5)
    for k in range(16):
        a = a0 + k * math.pi / 8
        cv.line([(wx, wy), (wx + math.cos(a) * R, wy + math.sin(a) * R)], hexc("#d9d2f2"), 4, cap=False)
    for k in range(32):
        a = a0 + k * math.pi / 16
        on = 0.5 + 0.5 * math.sin(t * 5 + k * 0.9)
        cv.circle(wx + math.cos(a) * R, wy + math.sin(a) * R, 9, fill=(255, 226, 140, int(120 + 135 * on)))
    for k in range(8):
        a = a0 + k * math.pi / 4
        px, py = wx + math.cos(a) * R, wy + math.sin(a) * R
        sw = 0.08 * math.sin(t * 1.6 + k)
        gx = px + math.sin(sw) * 50
        cv.line([(px, py), (gx, py + 46)], hexc("#2b2140"), 4)
        col = hexc(["#e2574c", "#3fa7f5", "#ffd34d", "#3cc9a4", "#ff6fae", "#a29bfe", "#ff9f43", "#55efc4"][k])
        cv.rect(gx - 38, py + 40, gx + 38, py + 96, fill=col, r=16)
        cv.rect(gx - 30, py + 48, gx + 30, py + 68, fill=hexc("#2b2140"), r=6)
        cv.circle(gx - 10, py + 60, 7, fill=hexc("#f1c7a3"))
        cv.circle(gx + 12, py + 60, 7, fill=hexc("#8d5524"))
    cv.circle(wx, wy, 30, fill=hexc("#ffd34d"))
    cv.circle(wx, wy, 12, fill=hexc("#2b2140"))
    # coaster train
    for c in range(4):
        x = (t * 300) % 2000 - 400 - c * 70
        if -80 < x < 1160:
            y = TRACK(x)
            dx = TRACK(x + 5) - TRACK(x - 5)
            ang = math.atan2(dx, 10)
            cv.rect(x - 30, y - 42, x + 30, y - 6, fill=hexc("#ffd34d" if c else "#3fa7f5"), r=10)
            for k in (-1, 1):
                hx = x + k * 13
                cv.circle(hx, y - 52, 9, fill=hexc(["#f1c7a3", "#8d5524", "#ffe0bd"][c % 3]))
                up = abs(math.sin(t * 6 + c + k))
                cv.line([(hx, y - 48), (hx + k * 8, y - 70 - 12 * up)], hexc(["#e2574c", "#0984e3", "#00b894"][c % 3]), 5)
    # carousel horses + lights
    cx = 210
    for k in range(5):
        a = t * 1.1 + k * 2 * math.pi / 5
        depth = math.sin(a)
        if depth < -0.2:
            continue
        hx = cx + math.cos(a) * 160
        hy = 980 + 28 * math.sin(t * 3 + k)
        s = 0.8 + 0.25 * depth
        cv.line([(hx, 860), (hx, hy - 30 * s)], hexc("#ffd34d"), 5)
        col = hexc(["#ffffff", "#ffd9e6", "#e1f5ff", "#fff3c4", "#e8ddff"][k])
        cv.ellipse(hx - 44 * s, hy - 22 * s, hx + 44 * s, hy + 18 * s, fill=col)
        d = 1 if math.cos(a + math.pi / 2) > 0 else -1
        cv.line([(hx + d * 34 * s, hy - 6 * s), (hx + d * 50 * s, hy - 38 * s)], col, 18 * s)
        cv.ellipse(hx + d * 42 * s, hy - 52 * s, hx + d * 70 * s, hy - 32 * s, fill=col)
        cv.line([(hx + d * 36 * s, hy - 40 * s), (hx + d * 30 * s, hy - 20 * s)], hexc("#e2574c"), 6 * s)
        for lx in (-28, -14, 16, 30):
            cv.line([(hx + lx * s, hy + 10 * s), (hx + lx * s + d * 6 * s * math.sin(t * 6 + lx), hy + 40 * s)], col, 7 * s)
    for k in range(10):
        on = 0.5 + 0.5 * math.sin(t * 6 + k)
        cv.circle(cx - 190 + 42 * k, 862, 7, fill=(255, 236, 160, int(100 + 155 * on)))
    # booth + lamp glow
    for k, x in enumerate((30, 1050)):
        cv.circle(x, 815, 70, fill=(255, 210, 120, 40))
        cv.circle(x, 815, 16, fill=hexc("#fff3c0"))
    for i, x0 in enumerate((440, 660, 880)):
        for k in range(8):
            on = 0.5 + 0.5 * math.sin(t * 4 + k * 1.3 + i)
            cv.circle(x0 + 15 + k * 26, 855, 6, fill=(255, 230, 150, int(110 + 145 * on)))
    # bunting
    for row, (y0, sag) in enumerate(((240, 60), (180, 40))):
        pts = [(x, y0 + sag * math.sin(math.pi * x / 1080) + 4 * math.sin(t * 2 + x * 0.02 + row)) for x in range(-30, 1111, 40)]
        cv.line(pts, hexc("#2b2140"), 3, cap=False)
        for i, (x, y) in enumerate(pts[:-1]):
            col = hexc(["#e2574c", "#ffd34d", "#3fa7f5", "#3cc9a4", "#ff6fae"][(i + row) % 5])
            sw = 6 * math.sin(t * 3 + i)
            cv.poly([(x, y), (x + 34, y + 2), (x + 17 + sw, y + 44)], fill=col)
    # balloons drifting up
    for i in range(4):
        ph = (t * 0.09 + i * 0.27) % 1
        bx = 120 + i * 250 + 30 * math.sin(t + i)
        by = 1100 - ph * 1200
        col = hexc(["#e2574c", "#3fa7f5", "#ffd34d", "#ff6fae"][i])
        cv.line([(bx, by + 40), (bx + 6 * math.sin(t * 2 + i), by + 120)], (255, 255, 255, 160), 2)
        cv.ellipse(bx - 30, by - 38, bx + 30, by + 40, fill=col)
        cv.ellipse(bx - 16, by - 26, bx - 4, by - 6, fill=(255, 255, 255, 120))
    if crowd:
        for i, look in enumerate(WALKERS):
            d = 1 if i % 2 == 0 else -1
            sp = 70 + i * 12
            x = ((t * sp * d + i * 330) % 1500) - 210 if d > 0 else 1290 - ((t * sp + i * 330) % 1500)
            y = 1175 + (i % 2) * 34
            shadow(cv, x, y, 40)
            draw_char(cv, x, y, look, 250 + (i % 2) * 20, d, t=t + i, walk=t * 6.5 + i, talk=0.4 if i == 2 else 0.0)
            if i == 2:
                hx, hy = x + d * 30, y - 170
                cv.line([(hx, hy), (hx + 4 * math.sin(t * 2), hy - 140)], (255, 255, 255, 180), 2)
                cv.ellipse(hx - 26, hy - 205, hx + 26, hy - 135, fill=hexc("#ff6fae"))


def cat(cv, x, y, t):
    """sleeping cat with breathing body and swishing tail"""
    b = 1 + 0.04 * math.sin(t * 2.2)
    col, cd = hexc("#f4a259"), hexc("#d9823b")
    tail = [(x + 60, y - 10), (x + 110, y - 20 + 10 * math.sin(t * 2)), (x + 130 + 10 * math.sin(t * 2.5), y - 60)]
    cv.line(tail, col, 16)
    cv.ellipse(x - 70, y - 60 * b, x + 80, y + 4, fill=col)
    for k in range(3):
        cv.arc(x - 30 + k * 30, y - 58 * b, x + 10 + k * 30, y - 10, 200, 340, cd, 5)
    cv.circle(x - 70, y - 30, 34, fill=col)
    cv.poly([(x - 98, y - 52), (x - 92, y - 84), (x - 74, y - 60)], fill=col)
    cv.poly([(x - 66, y - 62), (x - 52, y - 88), (x - 44, y - 56)], fill=col)
    for ex in (-84, -62):
        cv.arc(x + ex - 8, y - 36, x + ex + 8, y - 26, 20, 160, hexc("#3d2a1e"), 3)
    z = (t * 0.7) % 1
    cv.text(x - 40 + 30 * z, y - 110 - 60 * z, "z", 30 + 16 * z, (90, 90, 140, int(255 * (1 - z))))


def room_life(cv, t):
    cat(cv, 380, 1290, t)
    a = 0.06 * math.sin(t * 1.4)
    for k in range(6):                          # swaying plant leaves
        ang = -math.pi / 2 + (k - 2.5) * 0.35 + a
        cv.line([(840, 1200), (840 + math.cos(ang) * 110, 1200 + math.sin(ang) * 110)], hexc("#3f8a4c"), 14)


def loft_life(cv, t):
    x = (t * 70) % 1200 - 60
    cv.line([(x - 40, 420), (x + 40, 410)], (220, 220, 240, 255), 6)
    if math.sin(t * 8) > 0:
        cv.circle(x + 40, 410, 6, fill=hexc("#ff4f4f"))
    for k in range(5):                          # car lights on the street far below
        cx = (t * (120 + k * 30) + k * 260) % 1000 + 120
        cv.circle(cx, 1040, 5, fill=hexc("#fff3b0" if k % 2 else "#ff5a5a"))


def street_life(cv, t):
    for i, look in enumerate(WALKERS[:2]):
        d = 1 if i == 0 else -1
        x = (t * 80 + i * 500) % 1400 - 160 if d > 0 else 1240 - (t * 80 + i * 500) % 1400
        draw_char(cv, x, 1215, look, 230, d, t=t + i, walk=t * 6.5 + i)
    for k in range(3):
        x = (t * 90 + k * 400) % 1300 - 100
        y = 300 + 40 * k + 10 * math.sin(t * 2 + k)
        w = 10 * math.sin(t * 10 + k)
        cv.line([(x - 16, y - w), (x, y), (x + 16, y - w)], hexc("#2b2140"), 4)


def sea_life(cv, t):
    for k in range(3):
        x = (t * 60 + k * 380) % 1300 - 100
        y = 420 + 50 * k + 14 * math.sin(t * 1.5 + k)
        w = 14 * math.sin(t * 6 + k)
        cv.line([(x - 26, y - w), (x, y), (x + 26, y - w)], hexc("#ffffff"), 6)
    for k in range(12):
        x = (k * 97 + t * 50) % 1080
        y = 1300 + (k * 41) % 400
        cv.arc(x - 30, y - 8, x + 30, y + 8, 200, 340, (255, 255, 255, 140), 4)


def bg_plain(stops):
    def fn(img, cv):
        grad(img, stops)
    return fn


BGS = {"fair": bg_fair, "roof": bg_roof, "mia": bg_mia_room, "loft": bg_loft, "street": bg_street, "show": bg_showroom,
       "jewel": bg_jeweler, "pool": bg_pool, "sea": bg_sea, "night": bg_night, "board": bg_board,
       "race": bg_plain([(0, "#101629"), (1, "#26305a")]), "cal": bg_plain([(0, "#ffb36b"), (1, "#ff7a59")]),
       "phone": bg_plain([(0, "#1a1440"), (1, "#3b2a7a")])}
_BG = {}


def bg(name):
    if name not in _BG:
        _BG[name] = _bg(name, BGS[name])
    return _BG[name]


def stage(name, cam, actors=None, t=0.0):
    """cam=(cx, cy, viewH) in screen-world coords; actors(cv) drawn in world coords at 2x"""
    cx, cy, vh = cam
    vh = min(vh, OUT_H)
    vw = vh * OUT_W / OUT_H
    cx = clamp(cx, vw / 2, OUT_W - vw / 2)
    cy = clamp(cy, vh / 2, OUT_H - vh / 2)
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    crop = bg(name).crop(tuple(int(round(v * Z)) for v in box)).convert("RGBA")
    cvs = BCanvas(crop, box[0], box[1], Z)
    life = {"loft": loft_life, "street": street_life, "sea": sea_life}.get(name)
    if life:
        life(cvs, _T[0])
    if actors:
        actors(cvs)
    return crop.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS), box


def drift(cam, t, a=1.0):
    cx, cy, vh = cam
    k = vh / OUT_H
    return (cx + a * k * 10 * math.sin(t * 0.5), cy + a * k * 6 * math.sin(t * 0.37 + 1), vh * (1 + 0.01 * math.sin(t * 0.6)))


def dim(img, a, col=(15, 10, 30)):
    return Image.blend(img, Image.new("RGB", img.size, col), a) if a > 0.01 else img


# ------------------------------------------------------------------ account display (screen space)
SPEND = [("Einen Sportwagen", 280000), ("Eine Diamant", 45000), ("Und eine Pool", 120000), ("Trotzdem bucht", 135000)]


def leon_money(t):
    v = 1000000
    for key, amt in SPEND:
        t0 = en(key) - 0.5
        v -= amt * smooth(prog(t, t0, t0 + 0.6))
    return v


def account(img, t, cx, cy, label, value_txt, col="#37b26c", scale=1.0, delta=None, delta_a=0.0):
    if scale <= 0.01:
        return
    w, h = 440, 150
    tile = Image.new("RGBA", ((w + 40) * Z, (h + 40) * Z), (0, 0, 0, 0))
    cv = BCanvas(tile, -20, -20, Z)
    cv.rect(6, 10, w + 6, h + 10, fill=(20, 12, 40, 110), r=34)
    cv.rect(0, 0, w, h, fill=INK, r=34)
    cv.rect(6, 6, w - 6, h - 6, outline=hexc(col), width=4, r=30)
    cv.text(w / 2, 36, label, 30, (200, 200, 220, 255))
    fs = 70
    while font(fs).getbbox(value_txt)[2] > w - 40:
        fs -= 2
    cv.text(w / 2, 96, value_txt, fs, hexc(col))
    tile = tile.resize((int(tile.width * scale / Z), int(tile.height * scale / Z)), Image.LANCZOS)
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)
    log_ui("account", cx - w / 2 * scale, cy - h / 2 * scale, cx + w / 2 * scale, cy + h / 2 * scale)
    if delta and delta_a > 0.01:
        pill3d(img, cx, cy + 115 * scale, delta, 44, bg="#e2574c", fg="#ffffff", rot=-3, scale=ease_out_back(delta_a),
               depth=6)


def leon_account(img, t, cx=540, cy=330, scale=1.0):
    v = leon_money(t)
    d, a = None, 0.0
    for key, amt in SPEND:
        t0 = st(key) + 0.3
        if t0 <= t < en(key) + 0.8:
            d, a = "-" + money(amt), prog(t, t0, t0 + 0.3) * (1 - prog(t, en(key) + 0.5, en(key) + 0.8))
    account(img, t, cx, cy, "KONTO · LEON", money(round(v / 1000) * 1000 if abs(v - round(v)) > 1 else v), scale=scale,
            delta=d, delta_a=a)


# ------------------------------------------------------------------ scenes
ROOF_L, ROOF_M, FEET = 320, 770, 1430


def roof_people(cv, t, leon_kw=None, mia_kw=None, h=430):
    shadow(cv, ROOF_L, FEET, 110)
    shadow(cv, ROOF_M, FEET, 110)
    lk = dict(t=t, blink=(t % 3.1) < 0.12)
    lk.update(leon_kw or {})
    mk = dict(blink=(t % 2.7) < 0.12)
    mk.update(mia_kw or {})
    a = leon(cv, ROOF_L, FEET, h, 1, **lk)
    b = mia(cv, ROOF_M, FEET, h, -1, **mk)
    return a, b


def string_lights(cv, t):
    for row, (y0, sag) in enumerate(((330, 90), (520, 70))):
        pts = [(x, y0 + sag * math.sin(math.pi * x / 1080)) for x in range(-20, 1101, 30)]
        cv.line(pts, hexc("#2e2a3a"), 3, cap=False)
        for i, (x, y) in enumerate(pts[1::3]):
            on = 0.6 + 0.4 * math.sin(t * 3 + i * 1.3 + row)
            cv.circle(x, y + 12, 26, fill=(255, 210, 120, int(50 * on)))
            cv.circle(x, y + 12, 9, fill=(255, 230, 160, 255))


def option_card(img, cx, cy, sc, kind, t):
    if sc <= 0.01:
        return
    w, h = 420, 470
    tile = Image.new("RGBA", ((w + 40) * Z, (h + 40) * Z), (0, 0, 0, 0))
    cv = BCanvas(tile, -20, -20, Z)
    col = "#37b26c" if kind == "million" else "#3fa7f5"
    cv.rect(10, 16, w + 10, h + 16, fill=(20, 12, 40, 120), r=40)
    for k in range(14, 0, -1):
        cv.rect(0, k, w, h + k, fill=_shade(hexc(col), 0.42), r=40)
    cv.rect(0, 0, w, h, fill=hexc(col), r=40)
    cv.rect(0, 0, w, h, outline=INK, width=5, r=40)
    if kind == "million":
        for i in range(5):
            banknote(cv, w / 2 - 40 + i * 20, 175 - i * 10, 2.2, -0.25 + i * 0.12, value=(200, 100, 100, 200, 100)[i])
        cv.text(w / 2, 320, "1.000.000 €", 66, hexc("#ffffff"))
        cv.rect(w / 2 - 120, 370, w / 2 + 120, 440, fill=hexc("#ffd34d"), r=30)
        cv.text(w / 2, 406, "SOFORT", 44, INK)
    else:
        coin(cv, w / 2 - 80, 160, 75, 0.35 * math.sin(t * 2))
        stopwatch(cv, w / 2 + 95, 175, 62, t * 0.8)
        cv.text(w / 2, 300, "1 CENT / SEK.", 56, hexc("#ffffff"))
        cv.rect(w / 2 - 140, 370, w / 2 + 140, 440, fill=hexc("#ffd34d"), r=30)
        cv.text(w / 2, 406, "1 JAHR LANG", 42, INK)
    tile = tile.resize((int(tile.width * sc / Z), int(tile.height * sc / Z)), Image.LANCZOS)
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)
    log_ui("card " + kind, cx - w / 2 * sc, cy - h / 2 * sc, cx + w / 2 * sc, cy + h / 2 * sc)


HOOK = [(["EINE", "MILLION", "EURO"], "#ffd34d", "#2b2140", -2, 100),
        (["SOFORT", "–", "ODER"], "#fff6e6", "#2b2140", 2, 96),
        (["1 CENT", "PRO", "SEKUNDE,"], "#fff6e6", "#2b2140", -2, 96),
        (["EIN", "GANZES", "JAHR", "LANG?"], "#e2574c", "#ffffff", 2, 96)]


def sc_hook(t):
    t0, t1 = st("Eine Million"), en("Eine Million")

    def act(cv):
        fair_life(cv, t)
    img, _ = stage("fair", drift((540, 1000, 1920), t), act)
    img = dim(img, 0.35)
    if t < 0.15:
        img = Image.blend(img, Image.new("RGB", img.size, (255, 250, 230)), 0.4 * (1 - t / 0.15))
    c1 = ease_out_back(prog(t, wt("Eine Million", "Million") - 0.1, wt("Eine Million", "Million") + 0.2))
    c2 = ease_out_back(prog(t, wt("Eine Million", "Cent") - 0.1, wt("Eine Million", "Cent") + 0.2))
    option_card(img, 318, 1200, 0.74 * c1, "million", t)
    option_card(img, 752, 1200, 0.74 * c2, "cent", t)
    if c2 > 0.3:
        vs = ease_out_back(prog(t, wt("Eine Million", "Cent") + 0.1, wt("Eine Million", "Cent") + 0.4))
        burst(img, 540, 1200, 0.6 * vs, t, 60, 170, (255, 255, 255), 12)
        pill3d(img, 535, 1200, "VS", 60, bg="#1d1b33", fg="#ffd34d", scale=vs, rot=-6)
    karaoke(img, t, HOOK, t0, t1, [380, 525, 670, 815], pop_k=0.55, first_pop=False)
    return img


def sc_roof(t):
    a1, a2, a3, a4, a5, a6, a7, a8 = (st(k) for k in ("Leon muss", "Die Million", "Ein Cent?", "Aber Mia", "Ich nehme",
                                                       "Viel Glück", "Wetten", "Und das Rennen"))
    cams = [(a1 - 0.3, (540, 1060, 1500)), (a1 + 0.5, (ROOF_L + 40, 1120, 1100)), (a3 + 0.8, (ROOF_L + 60, 1120, 1080)),
            (a4, (ROOF_L + 60, 1120, 1080)), (a4 + 0.5, (ROOF_M - 30, 1020, 800)), (a5 + 0.1, (ROOF_M - 30, 1020, 800)),
            (a5 + 0.5, (ROOF_M - 40, 1120, 1080)), (a6, (ROOF_M - 40, 1120, 1080)),
            (a6 + 0.5, (ROOF_L + 80, 1120, 1150)), (a7, (ROOF_L + 80, 1120, 1150)), (a7 + 0.5, (540, 1100, 1500))]
    cam = drift(keyframes(t, cams), t)
    eis_t = wt("Viel Glück", "Eis", 0.1)

    def act(cv):
        fair_life(cv, t)
        lk, mk = {}, {}
        if a2 <= t < a3:                         # "Die Million! Sofort!"
            lk = dict(arms_up=1.0, bounce=14 * abs(math.sin(t * 9)), talk=0.8)
        elif a3 <= t < a4:                       # "Ein Cent?" -> shrug, then hands in pockets
            H_ = 430 * 1.12
            if t < wt("Ein Cent?", "Dafür", 0.0):
                k = smooth(prog(t, a3, a3 + 0.35))
                lk = dict(talk=0.6, shrug=k, arm_f=("ang", 0.3 * k, 0.2 + 1.5 * k), arm_b=("ang", -0.3 * k, -(0.2 + 1.5 * k)),
                          hand_f="open", hand_b="open", mood="smirk", head_tilt=0.1)
            else:
                lk = dict(talk=0.6, arm_f=("ik", (ROOF_L + 0.06 * H_, FEET - 0.45 * H_)),
                          arm_b=("ik", (ROOF_L - 0.05 * H_, FEET - 0.45 * H_)), hand_f="pocket", hand_b="pocket",
                          lean=-10, mood="smirk")
        elif a6 <= t < a7:                       # laughing at Mia
            lk = dict(talk=1.0, blink=True, bounce=8 * abs(math.sin(t * 12)), reach=(ROOF_M - 80, FEET - 300))
        elif a7 <= t:                            # handshake
            p = smooth(prog(t, a7 + 0.3, a7 + 1.0))
            lk = dict(reach=(ROOF_L + (545 - ROOF_L) * p + 60 * (1 - p), FEET - 230))
            mk = dict(reach=(ROOF_M + (555 - ROOF_M) * p - 60 * (1 - p), FEET - 230))
        if a4 + 0.3 <= t < a5 + 0.2:             # adjusts her glasses at the frame (thumb + index)
            g = head_geo(ROOF_M, FEET, MIA, 430, -1)
            r_, fx_, ey_ = g["r"], g["fx"], g["ey"]
            up = smooth(prog(t, a4 + 0.3, a4 + 0.8)) * (1 - smooth(prog(t, a5 - 0.1, a5 + 0.2)))
            gd = 0.1 * smooth(prog(t, a4 + 0.75, a4 + 1.1))
            hx_ = fx_ - 1.05 * r_
            wrist = (hx_ * up + (ROOF_M - 60) * (1 - up), (ey_ + 1.15 * r_) * up + (FEET - 230) * (1 - up))
            mk = dict(arm_f=("ik", wrist), hand_f="pinch" if up > 0.7 else "relaxed",
                      point_f=("to", (fx_ - 0.62 * r_, ey_ - gd * r_)), glasses_dy=gd, mood="smirk", breathe=0.3, sway=0.2)
        if a5 <= t < a6:
            mk = dict(talk=0.4 + 0.4 * math.sin(t * 14))
        if t >= a1:
            roof_people(cv, t, lk, mk)
        if a4 + 1.1 <= t < a4 + 1.6:            # glint across the lenses
            g = head_geo(ROOF_M, FEET, MIA, 430, -1)
            p = prog(t, a4 + 1.1, a4 + 1.6)
            for ex in (g["fx"] - 0.33 * g["r"], g["fx"] + 0.33 * g["r"]):
                x0 = ex - 0.25 * g["r"] + 0.5 * g["r"] * p
                cv.line([(x0 - 0.06 * g["r"], g["ey"] + 0.12 * g["r"]), (x0 + 0.06 * g["r"], g["ey"] - 0.22 * g["r"])],
                        (255, 255, 255, int(230 * math.sin(math.pi * p))), 0.07 * g["r"])
        if a3 <= t < a4:                          # a lonely cent on the ground
            coin(cv, ROOF_L - 170, FEET - 26, 26, 0.35 * math.sin(t * 2))
        if a2 <= t < a3 + 0.05:                   # money rain
            for i in range(14):
                rng = np.random.default_rng(i)
                x = ROOF_L + rng.uniform(-260, 260)
                y = 700 + ((t - a2) * 380 + rng.uniform(0, 500)) % 800
                banknote(cv, x, y, 0.8, math.sin(t * 3 + i))

    img, box = stage("fair", cam, act, t)
    pop_pill(img, t, a1 + 0.1, 540, 330, "LEON", 70, t1=a2 - 0.1, bg="#ff7a2f", fg="#ffffff", rot=-3)
    pop_pill(img, t, a2, 540, 330, "DIE MILLION! SOFORT!", 64, t1=a3 - 0.1, bg="#ffd34d", rot=-2)
    pop_pill(img, t, a3, 540, 330, "1 CENT?!", 70, t1=a4 - 0.1, bg="#fff6e6", rot=2)
    pop_pill(img, t, a3 + 0.7, 540, 450, "NICHT MAL DEN FINGER!", 52, t1=a4 - 0.1, bg="#e2574c", fg="#ffffff", rot=-2)
    pop_pill(img, t, a4 + 0.1, 540, 330, "MIA", 70, t1=a5 - 0.1, bg="#3cc9a4", fg="#ffffff", rot=3)
    pop_pill(img, t, a5, 540, 330, "„ICH NEHME DIE SEKUNDEN.“", 52, t1=a6 - 0.1, bg="#fff6e6", rot=-2)
    pop_pill(img, t, a6 + 0.2, 540, 330, "„FRAU PROFESSORIN!“", 60, t1=a7 - 0.1, bg="#ffd34d", rot=2)
    if eis_t - 0.2 <= t < a7:
        pop_pill(img, t, eis_t - 0.1, 540, 455, "1 KUGEL EIS?", 52, bg="#ff9fb7", rot=-3)
    pop_pill(img, t, a7 + 0.1, 540, 330, "„WETTEN?“", 66, t1=en("Wetten") - 0.6, bg="#fff6e6", rot=-2)
    pop_pill(img, t, en("Wetten") - 0.6, 540, 330, "DIE WETTE GILT!", 72, bg="#37b26c", fg="#ffffff", rot=2)
    if en("Wetten") - 0.6 < t:
        burst(img, 540, 1060, 0.5 * (1 - prog(t, en("Wetten"), en("Wetten") + 0.4)), t, 40, 160, (255, 255, 255), 12)
    return img


def sc_race(t):
    t0 = st("Und das Rennen")
    img, _ = stage("race", (540, 960, 1920))
    d = BCanvas(Image.new("RGBA", (OUT_W * Z, OUT_H * Z), (0, 0, 0, 0)), 0, 0, Z)
    dur = en("Und das Rennen") - t0
    n_on = int(clamp((t - t0) / (dur * 0.8)) * 3 + 0.0001)
    x, y = 540, 980
    d.rect(x - 130, y - 420, x + 130, y + 420, fill=INK, r=60)
    for k in range(3):
        on = k < n_on or (k == 2 and t >= t0 + dur * 0.8)
        col = ["#e2574c", "#ffb703", "#37e07a"][k] if on else "#3a3a50"
        if on:
            d.circle(x, y - 270 + k * 270, 150, fill=hexc(col, 60) if False else tuple(hexc(col)) + (60,))
        d.circle(x, y - 270 + k * 270, 100, fill=hexc(col))
    im = d.img.resize((OUT_W, OUT_H), Image.LANCZOS)
    img.paste(im, (0, 0), im)
    pop_pill(img, t, t0, 540, 330, "DAS RENNEN BEGINNT!", 70, bg="#ffd34d", rot=-2)
    return img


def mia_window(cv, t, cycle=None):
    """window content: day/night cycle"""
    if cycle is None:
        night = 0.0
    else:
        night = 0.5 - 0.5 * math.cos(cycle * 2 * math.pi)
    top = mix(hexc("#6ec6ff"), hexc("#0b1033"), night)
    bot = mix(hexc("#d9f2ff"), hexc("#2a2f6e"), night)
    for k in range(10):
        cv.rect(636, 396 + k * 48.8, 1004, 396 + (k + 1) * 48.8 + 1, fill=mix(top, bot, k / 9))
    if cycle is not None:
        a = cycle * 2 * math.pi
        sx, sy = 820 + 160 * math.sin(a), 720 - 260 * math.cos(a) * 0.9
        if night < 0.5:
            cv.circle(sx, sy, 40, fill=hexc("#ffe27a"))
        else:
            mx, my = 820 - 160 * math.sin(a), 720 + 260 * math.cos(a) * 0.9
            cv.circle(mx, my, 34, fill=hexc("#f4f1d0"))
    else:
        cv.circle(900, 500, 40, fill=hexc("#ffe27a"))
    skyline(cv, 884, ["#8aa0c8"] if night < 0.5 else ["#1b1f45"], 3, 0.0 if night < 0.5 else 0.5, 60, 200)
    cv.rect(810, 380, 830, 900, fill=hexc("#ffffff"))
    cv.rect(620, 630, 1020, 650, fill=hexc("#ffffff"))


def mia_counter(cv, t, text, col="#37e07a"):
    cv.text(300, 480, "KONTO · MIA", 34, (190, 200, 230, 255))
    cv.text(300, 600, text, 92 if len(text) < 9 else 66, hexc(col))


def sc_mia_start(t):
    t0, t1 = st("Erste Sekunde"), en("Erste Sekunde")
    sec2 = wt("Erste Sekunde", "Zweite", 0.0)
    c = 0.01 if t < sec2 else 0.02

    def act(cv):
        mia_window(cv, t)
        room_life(cv, t)
        mia_counter(cv, t, f"0,0{1 if t < sec2 else 2} €")
        piggy(cv, 470, 1060, 0.9)
        for k, tc in enumerate((t0 + 0.3, sec2 + 0.2)):
            if t > tc:
                p = prog(t, tc, tc + 0.5)
                if p < 1:
                    coin(cv, 470, 860 + 90 * p * p, 20, t * 8)
        shadow(cv, 790, 1440, 100)
        mia(cv, 790, 1440, 420, -1, reach=(560, 1040), blink=(t % 2.6) < 0.12)
        stopwatch(cv, 900, 1180, 60, (t - t0) * 0.5)
    img, _ = stage("mia", drift((560, 940, 1650), t), act)
    pop_pill(img, t, t0, 540, 300, "SEKUNDE 1", 70, t1=sec2 - 0.1, bg="#fff6e6", rot=-2)
    pop_pill(img, t, sec2, 540, 300, "SEKUNDE 2", 70, bg="#fff6e6", rot=2)
    pop_pill(img, t, t0 + 0.4, 540, 1360, "+1 CENT", 60, t1=sec2 - 0.1, bg="#37b26c", fg="#ffffff", rot=-3)
    pop_pill(img, t, sec2 + 0.4, 540, 1360, "+1 CENT", 60, bg="#37b26c", fg="#ffffff", rot=3)
    return img


def sc_loft(t):
    t0, t1, t2 = st("Leon lacht"), st("Und weil er"), en("Und weil er")

    def act(cv):
        shadow(cv, 540, 1450, 120)
        if t < t1:
            leon(cv, 540, 1450, 470, 1, t=t, blink=True, talk=1.0, bounce=12 * abs(math.sin(t * 11)),
                 lean=10 * math.sin(t * 11), reach=(470, 1120))
        else:
            leon(cv, 540, 1450, 470, 1, t=t, arms_up=0.7, shades=t > t1 + 0.8, crown=smooth(prog(t, t1 + 0.3, t1 + 0.9)),
                 bounce=4 * abs(math.sin(t * 5)))
        if t < t1:
            for k in range(4):
                ph = (t * 1.6 + k / 4) % 1
                cv.text(540 + (-1) ** k * (180 + 40 * ph), 800 - ph * 200, "HA", 70, (255, 211, 77, int(255 * (1 - ph))))
    img, _ = stage("loft", drift((540, 1000, 1500), t), act)
    if t < t1:
        pop_pill(img, t, t0 + 0.1, 540, 330, "HAHAHA!", 80, bg="#ffd34d", rot=-3)
    else:
        leon_account(img, t)
        pop_pill(img, t, t1 + 0.6, 540, 520, "„SCHON GEWONNEN!“", 56, bg="#fff6e6", rot=2)
    return img


def sc_car(t):
    t0, t1 = st("Einen Sportwagen"), en("Einen Sportwagen")
    p = smooth(prog(t, t0 - 0.2, t0 + 0.9))
    cx = -400 + 920 * p

    def act(cv):
        sports_car(cv, cx, 1400, 1.25, t, wheel=-cx / 40)
        if p >= 0.99:
            for k in range(3):
                a = (t * 2 + k * 2.1) % 6.28
                cv.circle(400 + 260 * k, 1080 - 20 * math.sin(a), 6 + 6 * max(0, math.sin(a)), fill=(255, 255, 255, 200))
    img, _ = stage("show", drift((540, 1000, 1700), t), act)
    leon_account(img, t)
    pop_pill(img, t, t0 + 0.2, 540, 1600 - 1600 + 1550 - 1550 + 600, "SPORTWAGEN", 64, bg="#ffc93c", rot=-2)
    return img


def sc_jewel(t):
    t0, t1 = st("Eine Diamant"), en("Eine Diamant")
    p = ease_out_back(prog(t, t0, t0 + 0.4))

    def act(cv):
        cx, cy = 540, 1020
        for k in range(26):
            a = math.pi * (0.12 + 0.76 * k / 25)
            x, y = cx - math.cos(a) * 170 * p, cy - 120 + math.sin(a) * 210 * p
            cv.circle(x, y, 13 * p, fill=hexc("#ffd34d"))
            cv.circle(x - 3, y - 3, 5 * p, fill=hexc("#fff6c0"))
        d = 60 * p
        cv.poly([(cx, cy + 90), (cx + d, cy + 90 + d), (cx, cy + 90 + 2.2 * d), (cx - d, cy + 90 + d)], fill=hexc("#9ee8ff"))
        cv.poly([(cx, cy + 90), (cx + d, cy + 90 + d), (cx, cy + 90 + d * 0.9)], fill=hexc("#e8fbff"))
        for k in range(6):
            a = t * 1.5 + k
            s = max(0, math.sin(t * 4 + k * 1.7))
            x, y = cx + math.cos(a) * 260, cy + 60 + math.sin(a * 1.3) * 200
            cv.line([(x - 22 * s, y), (x + 22 * s, y)], (255, 255, 255, 230), 4)
            cv.line([(x, y - 22 * s), (x, y + 22 * s)], (255, 255, 255, 230), 4)
    img, _ = stage("jewel", drift((540, 1000, 1700), t), act)
    leon_account(img, t)
    pop_pill(img, t, t0 + 0.2, 540, 600, "DIAMANTKETTE", 64, bg="#bdf3ff", rot=2)
    return img


def sc_pool(t):
    t0, t1, t2 = st("Und eine Pool"), st("Ich bin Millionär"), en("Ich bin Millionär")
    town = wt("Und eine Pool", "ganze", 0.0)

    def act(cv):
        for i in range(5):                      # light beams
            a = -0.6 + i * 0.3 + 0.25 * math.sin(t * 1.5 + i)
            x0 = 120 + i * 210
            cv.poly([(x0, 620), (x0 + math.sin(a) * 900 - 60, -100), (x0 + math.sin(a) * 900 + 60, -100)],
                    fill=(255, 255, 255, 26))
        for i in range(3):                      # floaties
            x = 200 + i * 340 + 30 * math.sin(t + i)
            y = 1290 + 8 * math.sin(t * 2 + i)
            cv.ellipse(x - 80, y - 26, x + 80, y + 26, fill=hexc(["#ff9fb7", "#ffd34d", "#3cc9a4"][i]))
            cv.ellipse(x - 40, y - 12, x + 40, y + 12, fill=hexc("#2fb7e8"))
        for k in range(30):                     # water sparkle
            x = (k * 73 + t * 40) % 1080
            y = 1170 + (k * 37) % 250
            cv.rect(x, y, x + 30, y + 4, fill=(255, 255, 255, int(150 * max(0, math.sin(t * 3 + k)))))
        for i, sty in enumerate(GUESTS):        # dancing guests on the deck
            x = 180 + i * 360
            up = 0.6 + 0.4 * abs(math.sin(t * 6 + i))
            draw_char(cv, x, 1100, sty, 320, 1 if i < 1 else -1, t=t + i, arm_f=("ang", 0.3 + 2.3 * up, 0.3),
                      arm_b=("ang", -(0.3 + 2.3 * up), -0.3), bounce=10 * abs(math.sin(t * 6 + i)), mood="laugh")
        if t >= t1 - 0.3:
            shadow(cv, 540, 1600, 130)
            leon(cv, 540, 1600, 520, 1, t=t, arms_up=1.0, shades=True, chain=True, bounce=14 * abs(math.sin(t * 9)),
                 talk=0.9)
        confetti(cv, t, 70)
    cam = keyframes(t, [(t0, (540, 960, 1920)), (t1 - 0.3, (540, 960, 1920)), (t1 + 0.3, (540, 1150, 1500))])
    img, _ = stage("pool", drift(cam, t), act)
    if t < t1 - 0.2:
        leon_account(img, t)
        pop_pill(img, t, t0 + 0.2, 540, 600, "POOLPARTY", 70, bg="#ff9fb7", rot=-2)
        if t >= town:
            for i, (txt, x, y, r) in enumerate((("STADTGESPRÄCH!", 300, 860, -6), ("LEGENDÄR!", 760, 760, 5),
                                                ("#LEONSPARTY", 640, 1000, -3))):
                pop_pill(img, t, town + i * 0.25, x, y, txt, 44, bg="#ffffff", rot=r, depth=6)
    else:
        burst(img, 540, 380, 0.6, t)
        pop_pill(img, t, t1, 540, 380, "„ICH BIN MILLIONÄR, BABY!“", 54, bg="#ffd34d", rot=-3)
    return img


def sc_mia_counter(t):
    t0, t1 = st("Während Leon"), en("Während Leon")
    cyc = max(0.0, t - t0 - 1.0) * 0.8
    rng = np.random.default_rng(int(t * 30))
    digits = f"{int(rng.integers(0, 100)):02d}"

    def act(cv):
        mia_window(cv, t, cyc)
        room_life(cv, t)
        mia_counter(cv, t, f"???.???,{digits} €")
        cv.circle(470, 600, 0, fill=(0, 0, 0, 0))
        piggy(cv, 470, 1060, 0.9)
        for k in range(5):
            ph = (t * 2.4 + k / 5) % 1
            coin(cv, 470 + 10 * math.sin(k), 820 + 120 * ph * ph, 16, t * 10 + k)
        shadow(cv, 790, 1440, 100)
        mia(cv, 790, 1440, 420, -1, reach=(600, 1040), blink=(t % 2.6) < 0.12, lean=-6)
    img, _ = stage("mia", drift((560, 940, 1650), t), act)
    pop_pill(img, t, t0 + 0.2, 540, 300, "WÄHRENDDESSEN BEI MIA ...", 52, bg="#3cc9a4", fg="#ffffff", rot=-2)
    pop_pill(img, t, wt("Während Leon", "Tag"), 540, 1340, "TAG UND NACHT", 60, bg="#1d1b33", fg="#ffd34d", rot=2)
    return img


MONTHS = ["JAN", "FEB", "MÄR", "APR", "MAI", "JUN", "JUL"]


def sc_six(t):
    t0, t1, t2 = st("Sechs Monate"), st("Na, Mia"), en("Na, Mia")
    tc = t0 + 1.2
    if t < tc:
        img, _ = stage("cal", (540, 960, 1920))
        k = min(6, int(prog(t, t0, tc - 0.15) * 7))
        lay = Image.new("RGBA", (OUT_W * Z, OUT_H * Z), (0, 0, 0, 0))
        calendar(BCanvas(lay, 0, 0, Z), 540, 1000, 1.6, MONTHS[k], "1")
        lay = lay.resize((OUT_W, OUT_H), Image.LANCZOS)
        img.paste(lay, (0, 0), lay)
        pop_pill(img, t, t0, 540, 330, "6 MONATE SPÄTER", 72, bg="#fff6e6", rot=-2)
        return img
    p = smooth(prog(t, tc - 0.2, tc + 0.8))
    cx = -300 + 650 * p

    def act(cv):
        sports_car(cv, cx, 1470, 1.0, t, wheel=-cx / 32)
        if p > 0.95:
            shadow(cv, 300, 1470, 90)
            leon(cv, 300, 1470, 400, 1, t=t, shades=True, chain=True, reach=(520, 1230) if t > t1 else None,
                 talk=0.5 + 0.5 * math.sin(t * 13) if t > t1 else 0.0)
        mx = 1200 - 360 * smooth(prog(t, tc, tc + 1.0))
        shadow(cv, mx, 1470, 90)
        mia(cv, mx, 1470, 400, -1, phase=t * 9 if mx > 841 else None, blink=(t % 2.6) < 0.12)
    img, _ = stage("street", drift((560, 1150, 1450), t), act)
    if t >= t1:
        account(img, t, 540, 330, "KONTO · LEON", money(leon_money(t)), scale=ease_out_back(prog(t, t1, t1 + 0.3)))
        pop_pill(img, t, t1 + 0.2, 540, 520, "„NA, MIA?“", 60, bg="#ffd34d", rot=-3)
        pop_pill(img, t, wt("Na, Mia", "Gibst"), 540, 640, "„GIBST DU SCHON AUF?“", 50, bg="#fff6e6", rot=2)
    return img


def sc_last_day(t):
    t0 = st("Am Ende")

    def act(cv):
        shadow(cv, 600, 1470, 120)
        mia(cv, 600, 1470, 520, -1, blink=(t % 2.6) < 0.12, talk=0.3 + 0.3 * math.sin(t * 13))
    img, _ = stage("street", drift((620, 1150, 1050), t), act)
    pop_pill(img, t, t0 + 0.1, 540, 330, "AM ENDE ZÄHLT", 66, bg="#3cc9a4", fg="#ffffff", rot=-2)
    pop_pill(img, t, t0 + 0.6, 540, 460, "NUR DER LETZTE TAG", 60, bg="#fff6e6", rot=2)
    return img


def sc_yacht(t):
    t0, t1 = st("Trotzdem bucht"), en("Trotzdem bucht")
    yp = ease_out_back(prog(t, t0 + 0.6, t0 + 1.1))

    def act(cv):
        bob = 8 * math.sin(t * 2)
        x, y = 540, 1240 + bob
        if yp > 0.01:
            s = yp
            cv.poly([(x - 380 * s, y - 60 * s), (x + 400 * s, y - 60 * s), (x + 320 * s, y + 60 * s), (x - 320 * s, y + 60 * s)],
                    fill=hexc("#ffffff"))
            cv.rect(x - 380 * s, y - 20 * s, x + 380 * s, y - 4 * s, fill=hexc("#1f8fd6"))
            cv.poly([(x - 240 * s, y - 60 * s), (x - 200 * s, y - 160 * s), (x + 220 * s, y - 160 * s), (x + 280 * s, y - 60 * s)],
                    fill=hexc("#f4f6fb"))
            for k in range(5):
                cv.rect(x - 170 * s + k * 80 * s, y - 135 * s, x - 120 * s + k * 80 * s, y - 95 * s, fill=hexc("#2b3a55"),
                        r=8 * s)
            cv.poly([(x - 120 * s, y - 160 * s), (x - 80 * s, y - 230 * s), (x + 120 * s, y - 230 * s), (x + 160 * s, y - 160 * s)],
                    fill=hexc("#ffffff"))
            cv.ellipse(x - 420 * s, y + 50 * s, x + 420 * s, y + 80 * s, fill=(255, 255, 255, 120))
            leon(cv, x + 40 * s, y - 230 * s, 230 * s, 1, t=t, shades=True, chain=True, arms_up=0.8)

        def screen(cv2, px, py, s):
            cv2.text(px, py - 200 * s, "YACHT-URLAUB", 30 * s, INK)
            cv2.rect(px - 110 * s, py - 160 * s, px + 110 * s, py - 20 * s, fill=hexc("#bfe6ff"), r=16 * s)
            cv2.text(px, py - 90 * s, "⛵" if False else "135.000 €", 34 * s, INK)
            booked = t > t0 + 1.0
            cv2.rect(px - 110 * s, py + 20 * s, px + 110 * s, py + 90 * s, fill=hexc("#37b26c" if booked else "#ff7a2f"),
                     r=30 * s)
            cv2.text(px, py + 55 * s, "GEBUCHT ✓" if booked else "BUCHEN", 30 * s, hexc("#ffffff"))
        if t < t0 + 1.4:
            ps = ease_out_back(prog(t, t0, t0 + 0.3)) * (1 - prog(t, t0 + 1.1, t0 + 1.4))
            if ps > 0.01:
                phone(cv, 540, 960, 1.3 * ps, screen)
    img, _ = stage("sea", drift((540, 1000, 1700), t), act)
    leon_account(img, t)
    return img


def sc_both(t):
    t0 = st("Denn beide")
    img = Image.new("RGB", (OUT_W, OUT_H))
    lay = Image.new("RGBA", (OUT_W * Z, OUT_H * Z), (0, 0, 0, 255))
    cv = BCanvas(lay, 0, 0, Z)
    cv.poly([(0, 0), (700, 0), (380, 1920), (0, 1920)], fill=hexc("#ffc93c"))
    cv.poly([(700, 0), (1080, 0), (1080, 1920), (380, 1920)], fill=hexc("#3cc9a4"))
    for i in range(16):
        a = i / 16 * 2 * math.pi + t * 0.2
        cv.poly([(270, 1000), (270 + math.cos(a) * 1500, 1000 + math.sin(a) * 1500),
                 (270 + math.cos(a + 0.12) * 1500, 1000 + math.sin(a + 0.12) * 1500)], fill=(255, 255, 255, 18))
    cv.line([(700, 0), (380, 1920)], hexc("#ffffff"), 14)
    leon(cv, 270, 1450, 440, 1, t=t, shades=True, chain=True, blink=False, arms_up=0.4 + 0.1 * math.sin(t * 4))
    mia(cv, 810, 1450, 440, -1, blink=(t % 2.6) < 0.12, reach=(700, 1150))
    img = lay.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)
    pop_pill(img, t, t0 + 0.4, 270, 680, "GEWONNEN!", 48, bg="#ffffff", rot=-5, depth=6)
    pop_pill(img, t, t0 + 0.7, 790, 680, "GEWONNEN!", 48, bg="#ffffff", rot=5, depth=6)
    pop_pill(img, t, t0 + 0.1, 540, 330, "BEIDE SIND SICH SICHER", 56, bg="#fff6e6", rot=-2)
    return img


def sc_tight(t):
    t0 = st("Es wird knapp")
    img, _ = stage("race", (540, 960, 1920))
    lay = Image.new("RGBA", (OUT_W * Z, OUT_H * Z), (0, 0, 0, 0))
    cv = BCanvas(lay, 0, 0, Z)
    for k, (name, col, y) in enumerate((("LEON", "#ffc93c", 820), ("MIA", "#3cc9a4", 1100))):
        cv.text(540, y - 110, name, 60, hexc("#ffffff"))
        cv.rect(110, y - 50, 970, y + 50, fill=hexc("#2a2f55"), r=50)
        f = 0.82 + 0.06 * math.sin(t * 5 + k * 2.5)
        cv.rect(110, y - 50, 110 + 860 * f, y + 50, fill=hexc(col), r=50)
        cv.text(110 + 860 * f - 70, y, "???", 44, hexc("#ffffff"))
    cv.line([(930, 640), (930, 1220)], hexc("#ffffff"), 6)
    for j in range(12):
        cv.rect(918 + (j % 2) * 12, 640 + j * 48, 930 + (j % 2) * 12, 664 + j * 48, fill=INK)
    lay = lay.resize((OUT_W, OUT_H), Image.LANCZOS)
    img.paste(lay, (0, 0), lay)
    pulse = 1 + 0.05 * abs(math.sin(t * 7))
    pop_pill(img, t, t0 + 0.05, 540, 330, "KNAPP ...", 72, bg="#e2574c", fg="#ffffff", rot=-3)
    if t > wt("Es wird knapp", "Sehr"):
        pill3d(img, 540, 470, "SEHR KNAPP!", 72 , bg="#ffd34d", rot=3, scale=pulse * ease_out_back(prog(t, wt("Es wird knapp", "Sehr"), wt("Es wird knapp", "Sehr") + 0.3)))
    return img


def firework(cv, x, y, t, t0, col, n=22, R=220):
    p = (t - t0)
    if p < 0:
        return
    if p < 0.5:
        cv.circle(x, y + (1 - p / 0.5) * 600, 6, fill=hexc("#fff3c0"))
        return
    q = (p - 0.5) / 1.2
    if q > 1:
        return
    for i in range(n):
        a = i / n * 2 * math.pi
        r = R * (1 - (1 - q) ** 2)
        px, py = x + math.cos(a) * r, y + math.sin(a) * r + 80 * q * q
        cv.line([(x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75 + 80 * q * q), (px, py)],
                tuple(hexc(col)) + (int(255 * (1 - q)),), 6)


def sc_nye(t):
    t0 = st("Dann kommt")

    def act(cv):
        for k, (x, y, c, d) in enumerate(((250, 520, "#ffd34d", 0.0), (800, 420, "#ff6f91", 0.4), (560, 700, "#3cc9a4", 0.8),
                                           (180, 820, "#3fa7f5", 1.2), (880, 760, "#ffd34d", 1.5))):
            firework(cv, x, y, t, t0 + d, c)
        calendar(cv, 540, 1180, 1.5 * ease_out_back(prog(t, t0, t0 + 0.4)), "DEZ", "31")
    img, _ = stage("night", (540, 960, 1920), act)
    pop_pill(img, t, t0 + 0.1, 540, 330, "LETZTER TAG DES JAHRES", 56, bg="#fff6e6", rot=-2)
    return img


def sc_reveal(t):
    t0, t1, t2 = st("Leon öffnet"), st("Trotz Sportwagen"), en("Trotz Sportwagen")
    zoom = smooth(prog(t, t0 + 0.2, t0 + 1.0))

    def screen(cv, px, py, s):
        cv.text(px, py - 220 * s, "MEINE BANK", 30 * s, hexc("#6c5ce7"))
        cv.text(px, py - 170 * s, "KONTOSTAND", 24 * s, (120, 120, 140, 255))
        show = t > wt("Leon öffnet", "vierhundert", 0.0)
        cv.text(px, py - 110 * s, "420.000 €" if show else "· · ·", 52 * s, hexc("#37b26c"))
        for i, (n, v) in enumerate((("Auto", "-280.000"), ("Kette", "-45.000"), ("Party", "-120.000"),
                                    ("Yacht", "-135.000"))):
            yy = py - 30 * s + i * 60 * s
            cv.rect(px - 116 * s, yy - 24 * s, px + 116 * s, yy + 24 * s, fill=hexc("#eceef6"), r=12 * s)
            cv.text(px - 100 * s, yy, n, 20 * s, INK, anchor="lm")
            cv.text(px + 104 * s, yy, v, 20 * s, hexc("#e2574c"), anchor="rm")

    def act(cv):
        shadow(cv, 540, 1450, 120)
        if t < t1:
            leon(cv, 300, 1450, 460, 1, t=t, shades=False, chain=True, reach=(470, 1080))
            phone(cv, 520 + 20 * zoom, 1070 - 110 * zoom, 0.55 + 1.0 * zoom, screen)
        else:
            phone(cv, 540, 960, 1.55, screen)
            for i, (x, y) in enumerate(((180, 560), (900, 560), (180, 1380), (900, 1380))):
                a = ease_out_back(prog(t, t1 + i * 0.35, t1 + i * 0.35 + 0.3))
                if a > 0.01:
                    cv.circle(x, y, 95 * a, fill=hexc("#ffffff"))
                    if i == 0:
                        sports_car(cv, x, y + 40 * a, 0.22 * a, t)
                    elif i == 1:
                        for k in range(12):
                            aa = math.pi * (0.15 + 0.7 * k / 11)
                            cv.circle(x - math.cos(aa) * 45 * a, y - 30 * a + math.sin(aa) * 55 * a, 6 * a, fill=hexc("#ffd34d"))
                        cv.poly([(x, y + 30 * a), (x + 16 * a, y + 46 * a), (x, y + 64 * a), (x - 16 * a, y + 46 * a)],
                                fill=hexc("#9ee8ff"))
                    elif i == 2:
                        for k in range(3):
                            cv.circle(x - 40 * a + k * 40 * a, y - 10 * a, 22 * a, fill=hexc(["#ff9fb7", "#ffd34d", "#3cc9a4"][k]))
                        cv.text(x, y + 45 * a, "PARTY", 28 * a, INK)
                    else:
                        cv.poly([(x - 60 * a, y + 10 * a), (x + 66 * a, y + 10 * a), (x + 48 * a, y + 40 * a), (x - 44 * a, y + 40 * a)],
                                fill=hexc("#1f8fd6"))
                        cv.poly([(x - 30 * a, y + 10 * a), (x - 20 * a, y - 30 * a), (x + 34 * a, y - 30 * a), (x + 44 * a, y + 10 * a)],
                                fill=hexc("#9fb3c8"))
                    cv.circle(x + 60 * a, y - 60 * a, 26 * a, fill=hexc("#37b26c"))
                    cv.line([(x + 48 * a, y - 60 * a), (x + 58 * a, y - 50 * a), (x + 74 * a, y - 72 * a)], hexc("#ffffff"), 6 * a)
    img, _ = stage("loft" if t < t1 else "phone", drift((540, 1000, 1700 if t < t1 else 1920), t), act)
    if t < t1:
        pop_pill(img, t, t0 + 0.1, 540, 330, "LEON ÖFFNET SEIN KONTO", 54, bg="#ff7a2f", fg="#ffffff", rot=-2)
    else:
        pop_pill(img, t, t1, 540, 300, "TROTZDEM 420.000 €!", 62, bg="#37b26c", fg="#ffffff", rot=-2)
    return img


def sc_genius(t):
    t0, t1 = st("Und du"), en("Und du")
    sit = wt("Und du", "Setz", 0.0)
    cam = keyframes(t, [(t0, (ROOF_L + 80, 1120, 1150)), (sit - 0.2, (ROOF_L + 80, 1120, 1150)), (sit + 0.3, (ROOF_M - 60, 1110, 1050))])

    def act(cv):
        fair_life(cv, t)
        lk = dict(shades=True, chain=True, reach=(ROOF_M - 100, FEET - 300), talk=0.5 + 0.5 * math.sin(t * 12)) if t < sit \
            else dict(shades=True, chain=True)
        mk = dict(talk=0.4 + 0.4 * math.sin(t * 13), reach=(ROOF_L + 100, FEET - 220)) if t >= sit else {}
        roof_people(cv, t, lk, mk)
    img, _ = stage("fair", drift(cam, t), act)
    pop_pill(img, t, t0 + 0.1, 540, 330, "„UND DU, RECHENGENIE?“", 56, t1=sit - 0.1, bg="#ffd34d", rot=-2)
    pop_pill(img, t, sit, 540, 330, "„SETZ DICH LIEBER HIN.“", 56, bg="#3cc9a4", fg="#ffffff", rot=2)
    return img


def sc_formula(t):
    t0, t1 = st("Ein Cent pro"), en("Ein Cent pro")

    def act(cv):
        rows = [("1 CENT", t0), ("× 60 SEKUNDEN", wt("Ein Cent pro", "Sekunde")), ("× 60 MINUTEN", wt("Ein Cent pro", "Sekunde") + 0.35),
                ("× 24 STUNDEN", wt("Ein Cent pro", "ganzes", 0.0)), ("× 365 TAGE", wt("Ein Cent pro", "Jahr", 0.0)),
                ("= ???", t1 - 0.2)]
        for i, (txt, ts) in enumerate(rows):
            a = prog(t, ts, ts + 0.3)
            if a > 0:
                col = (255, 255, 255, int(235 * a)) if i < 5 else (255, 211, 77, int(255 * a))
                cv.text(540, 480 + i * 150, txt, 92 if i < 5 else 130, col)
        coin(cv, 200, 1330, 70, 0.35 * math.sin(t * 2))
        stopwatch(cv, 880, 1330, 80, t * 0.5)
    img, _ = stage("board", (540, 960, 1920), act)
    return img


def sc_count(t):
    t0, t1 = st("Leon fängt"), en("Leon fängt")

    def act(cv):
        shadow(cv, 540, 1450, 120)
        g = head_geo(540, 1450, LEON, 480, 1)
        H_ = 480 * 1.12
        n = int(max(0.0, t - t0) / 0.45)
        tap = 0.5 - 0.5 * math.cos(((t - t0) % 0.45) / 0.45 * 2 * math.pi)
        fh = (540 + 0.2 * H_, 1450 - 0.66 * H_)                 # open hand held up in front of the chest
        tip = (fh[0] + 0.02 * H_ - (n % 4) * 0.012 * H_, fh[1] - 0.06 * H_ + 0.02 * H_ * tap)
        leon(cv, 540, 1450, 480, 1, t=t, chain=True, arm_f=("ik", fh), hand_f="open",
             arm_b=("ik", (540 + 0.1 * H_, 1450 - 0.55 * H_ + 0.015 * H_ * tap)), hand_b="point", point_f=("to", tip),
             mood="worried", brows=0.6, look=(0.6, 0.8), head_tilt=0.08)
        for k, sym in enumerate(("+", "×", "?", "÷", "=", "?")):
            a = t * 0.9 + k * 1.05
            cv.text(540 + math.cos(a) * 260, g["hy"] - 40 + math.sin(a) * 120, sym, 80,
                    hexc(["#ffd34d", "#e2574c", "#3cc9a4", "#6c5ce7", "#ffffff", "#3fa7f5"][k]))
        dy = (t * 1.3) % 1
        cv.ellipse(g["hx"] - g["r"] * 1.05, g["hy"] - g["r"] * 0.2 + dy * 60, g["hx"] - g["r"] * 0.85,
                   g["hy"] + g["r"] * 0.1 + dy * 60, fill=hexc("#8fd3ff"))
    img, _ = stage("loft", drift((540, 1020, 1300), t), act)
    n = int(clamp((t - t0) / 0.45, 0, 9)) + 1
    pop_pill(img, t, t0 + 0.1, 540, 330, "FINGER FÜR FINGER ...", 58, bg="#ff7a2f", fg="#ffffff", rot=-2)
    pill3d(img, 540, 470, " ".join(str(i) for i in range(1, min(n, 6) + 1)) + (" ..." if n > 6 else ""), 52, bg="#fff6e6",
           rot=2, scale=ease_out_back(prog(t, t0 + 0.4, t0 + 0.7)))
    return img


def sc_final(t):
    t0, t1 = st("Wie viel"), st("Schreib's")
    lay = Image.new("RGBA", (OUT_W * Z, OUT_H * Z), (0, 0, 0, 255))
    cv = BCanvas(lay, 0, 0, Z)
    cv.rect(0, 0, 540, 1920, fill=hexc("#ffc93c"))
    cv.rect(540, 0, 1080, 1920, fill=hexc("#3cc9a4"))
    for i in range(16):
        a = i / 16 * 2 * math.pi + t * 0.25
        for cx in (270, 810):
            cv.poly([(cx, 1150), (cx + math.cos(a) * 1300, 1150 + math.sin(a) * 1300),
                     (cx + math.cos(a + 0.1) * 1300, 1150 + math.sin(a + 0.1) * 1300)], fill=(255, 255, 255, 14))
    cv.rect(532, 0, 548, 1920, fill=hexc("#ffffff"))
    leon(cv, 270, 1440, 400, 1, t=t, chain=True, shades=True)
    mia(cv, 810, 1440, 400, -1, blink=(t % 2.6) < 0.12)
    bob = 12 * math.sin(t * 3)
    cx = 540 + 200 * math.sin(t * 2.2)
    if t < t1:
        cv.poly([(cx - 70, 900 + bob), (cx - 70, 840 + bob), (cx - 35, 870 + bob), (cx, 820 + bob), (cx + 35, 870 + bob),
                 (cx + 70, 840 + bob), (cx + 70, 900 + bob)], fill=hexc("#ffd34d"))
    img = lay.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS)
    account(img, t, 270, 640, "LEON", "420.000 €", scale=0.9)
    rng = np.random.default_rng(int(t * 20))
    account(img, t, 810, 640, "MIA", "??? €", col="#ffd34d", scale=0.9)
    pop_pill(img, t, t0, 540, 300, "WIE VIEL HAT MIA?", 66, bg="#fff6e6", rot=-2)
    pop_pill(img, t, wt("Wie viel", "wer", 0.0), 540, 440, "WER GEWINNT?", 74, bg="#ffd34d", rot=2)
    if t > t1:
        pop_pill(img, t, t1, 540, 830, "SCHREIB'S IN DIE KOMMENTARE", 42, bg="#ffffff")
        followed = t > t1 + 1.3
        pill3d(img, 540, 950, "GEFOLGT  ✓" if followed else "+  FOLGEN", 64, bg="#37b26c" if followed else "#e2574c",
               fg="#ffffff", scale=ease_out_back(prog(t, t1 + 0.3, t1 + 0.6)) * (1 + (0 if followed else 0.05 * math.sin(t * 10))))
    return img


SCENES = [(0.0, sc_hook), (st("Leon muss") - 0.1, sc_roof), (st("Und das Rennen") - 0.05, sc_race),
          (st("Erste Sekunde") - 0.05, sc_mia_start), (st("Leon lacht") - 0.05, sc_loft),
          (st("Einen Sportwagen") - 0.05, sc_car), (st("Eine Diamant") - 0.05, sc_jewel),
          (st("Und eine Pool") - 0.05, sc_pool), (st("Während Leon") - 0.05, sc_mia_counter),
          (st("Sechs Monate") - 0.05, sc_six), (st("Am Ende") - 0.05, sc_last_day),
          (st("Trotzdem bucht") - 0.05, sc_yacht), (st("Denn beide") - 0.05, sc_both),
          (st("Es wird knapp") - 0.05, sc_tight), (st("Dann kommt") - 0.05, sc_nye),
          (st("Leon öffnet") - 0.05, sc_reveal), (st("Und du") - 0.05, sc_genius),
          (st("Ein Cent pro") - 0.05, sc_formula), (st("Leon fängt") - 0.05, sc_count),
          (st("Wie viel") - 0.05, sc_final)]


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
