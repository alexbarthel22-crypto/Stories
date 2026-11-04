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

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# ------------------------------------------------------------------ layout (world units = screen px, image 2x)
W, H = OUT_W, OUT_H
ZW = 2
FLOOR = 1440
TABLE = (120, 620, 1185)            # x0, x1, top y
BARREL = (815, 975, 845)            # x0, x1, top y
TAP = (806, 1115)                   # tap outlet
FILL_SPOT = (722, FLOOR)            # bucket under the tap (bottom centre)
BUCKETS = {"big": dict(cap=5, bw=158, tw=228, h=262, home=(265, TABLE[2])),
           "small": dict(cap=3, bw=120, tw=172, h=198, home=(500, TABLE[2]))}
DRINK, DRINK_D = "#eef3f6", "#c9d6de"
ANTH, WOOD, WOOD_D = "#2c2f38", "#b9804f", "#94603a"

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
    cv.rect(0, 1200, W, FLOOR, fill=hexc("#33406e"))
    cv.rect(0, 1080, W, FLOOR, fill=(225, 235, 245, 70))
    cv.rect(0, 1072, W, 1084, fill=hexc(ANTH))
    for k in range(0, W, 180):
        cv.rect(k - 3, 1080, k + 3, FLOOR, fill=hexc("#454955"))
    deck = vgradient(W * ZW, (H - FLOOR) * ZW, [(0, "#b9804f"), (1, "#8a5a36")])
    img.paste(deck, (0, FLOOR * ZW))
    cv = Canvas(img, 0, 0, ZW)
    for k in range(FLOOR + 40, H, 60):
        cv.rect(0, k, W, k + 4, fill=hexc(WOOD_D))
    # planters
    for px in (40, 1010):
        cv.rect(px - 50, FLOOR - 110, px + 50, FLOOR, fill=hexc(ANTH), r=8)
        for a in range(7):
            cv.circle(px + (a - 3) * 14, FLOOR - 140 - (a % 3) * 26, 28, fill=hexc("#4f8a4c"))
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
CAM = (540, 1070, 1700)


# ------------------------------------------------------------------ props
def string_lights(cv, t):
    pts = [(x, 560 + 70 * math.sin(math.pi * x / W)) for x in range(-20, W + 40, 40)]
    cv.line(pts, hexc("#22243a"), 3, cap=False)
    for i, (x, y) in enumerate(pts[1::2]):
        on = 0.75 + 0.25 * math.sin(t * 3 + i)
        cv.circle(x, y + 14, 16, fill=(255, 214, 110, int(60 * on)))
        cv.circle(x, y + 12, 8, fill=hexc("#ffe4a0"))


def draw_barrel(cv, t, stream_to=None):
    x0, x1, top = BARREL
    cx = (x0 + x1) / 2
    cv.ellipse(x0 - 16, top + 20, x1 + 16, FLOOR + 10, fill=hexc("#a86f40"))
    cv.rect(x0 - 10, top + 30, x1 + 10, FLOOR - 10, fill=hexc(WOOD))
    for k in range(6):
        xx = x0 + 10 + k * (x1 - x0 - 20) / 5
        cv.rect(xx - 2, top + 30, xx + 2, FLOOR - 10, fill=hexc(WOOD_D))
    for yy in (top + 70, (top + FLOOR) / 2, FLOOR - 60):
        cv.rect(x0 - 14, yy - 10, x1 + 14, yy + 10, fill=hexc("#5d6270"), r=4)
    cv.ellipse(x0 - 10, top + 6, x1 + 10, top + 56, fill=hexc("#8a5a36"))
    cv.ellipse(x0 + 6, top + 14, x1 - 6, top + 48, fill=hexc(DRINK_D))
    # label (neutral, no brand logo)
    cv.rect(cx - 62, top + 150, cx + 62, top + 250, fill=hexc("#f7f7f7"), r=10)
    cv.text(cx, top + 186, "WHITE", 30, hexc("#22243a"))
    cv.text(cx, top + 222, "ENERGY", 18, hexc("#6b7380"))
    # tap
    cv.rect(TAP[0], TAP[1] - 24, x0, TAP[1] - 8, fill=hexc("#9aa1ab"))
    cv.rect(TAP[0] - 6, TAP[1] - 30, TAP[0] + 10, TAP[1], fill=hexc("#8a919c"), r=3)
    cv.rect(TAP[0] - 4, TAP[1] - 58, TAP[0] + 8, TAP[1] - 30, fill=hexc("#e2574c"), r=3)
    if stream_to is not None:
        cv.line([(TAP[0] + 2, TAP[1]), (TAP[0] + 2, stream_to)], (238, 243, 246, 230), 10, cap=False)


def draw_table(cv):
    x0, x1, top = TABLE
    cv.rect(x0, top, x1, top + 26, fill=hexc(WOOD), r=6)
    cv.rect(x0, top + 22, x1, top + 30, fill=hexc(WOOD_D))
    for lx in (x0 + 30, x1 - 44):
        cv.rect(lx, top + 26, lx + 14, FLOOR, fill=hexc(ANTH))
    for k, cx in enumerate((x0 + 40, x1 - 40)):   # cups for the friends
        cv.poly([(cx - 18, top - 46), (cx + 18, top - 46), (cx + 13, top), (cx - 13, top)], fill=hexc("#f2f2f2"))
        cv.rect(cx - 18, top - 50, cx + 18, top - 44, fill=hexc("#3f7fd9" if k else "#e2574c"))


def _rot(pts, ang, piv):
    c, s = math.cos(ang), math.sin(ang)
    return [(piv[0] + (x - piv[0]) * c - (y - piv[1]) * s, piv[1] + (x - piv[0]) * s + (y - piv[1]) * c) for x, y in pts]


def draw_bucket(cv, name, bx, by, liters, tilt=0.0):
    """transparent bucket, bottom centre (bx, by); tilt in radians (+ = pours to the right)"""
    b = BUCKETS[name]
    bw, tw, h = b["bw"], b["tw"], b["h"]
    piv = (bx + (tw / 2 if tilt >= 0 else -tw / 2), by - h)       # pour lip
    body = [(bx - tw / 2, by - h), (bx + tw / 2, by - h), (bx + bw / 2, by), (bx - bw / 2, by)]
    frac = clamp(liters / b["cap"], 0, 1)
    if frac > 0.002:
        ly = by - h * frac
        wl = bw + (tw - bw) * frac
        liquid = [(bx - wl / 2, ly), (bx + wl / 2, ly), (bx + bw / 2, by), (bx - bw / 2, by)]
        cv.poly(_rot(liquid, tilt, piv), fill=hexc(DRINK))
        cv.line(_rot([(bx - wl / 2 + 4, ly + 3), (bx + wl / 2 - 4, ly + 3)], tilt, piv), hexc(DRINK_D), 6, cap=False)
    cv.poly(_rot(body, tilt, piv), fill=(210, 230, 245, 70))
    cv.line(_rot(body + [body[0]], tilt, piv), hexc("#9fb3c8"), 5, joint="curve", cap=False)
    rim = _rot([(bx - tw / 2 - 6, by - h), (bx + tw / 2 + 6, by - h)], tilt, piv)
    cv.line(rim, hexc("#7f93a8"), 9)
    # handle
    hp = _rot([(bx - tw / 2 + 6 + k * (tw - 12) / 10, by - h - 46 * math.sin(math.pi * k / 10)) for k in range(11)],
              tilt, piv)
    cv.line(hp, hexc("#5d6270"), 5, cap=False)
    return _rot([(bx + (tw / 2 if tilt >= 0 else -tw / 2), by - h)], tilt, piv)[0]


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
                pos[src] = (home[0] + (spot[0] - home[0]) * q, home[1] + (spot[1] - home[1]) * q - math.sin(math.pi * q) * 80)
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
                pos[src] = (spot[0] + (home[0] - spot[0]) * q, spot[1] + (home[1] - spot[1]) * q - math.sin(math.pi * q) * 80)
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
                            home[1] + (lift[1] - home[1]) * q - math.sin(math.pi * q) * 120)
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
                                lift[1] + (home[1] - lift[1]) * q2 - math.sin(math.pi * q2) * 120)
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


def draw_scene(cv, t, solution=True, dario_face=1, cheer=0.0):
    string_lights(cv, t)
    # friends in the back
    draw_person(cv, 95, FLOOR - 30, FRIEND1, face=1, h=FRIEND1.h * 1.2, arms_up=cheer * abs(math.sin(t * 6)))
    draw_person(cv, 175, FLOOR - 60, FRIEND2, face=1, h=FRIEND2.h * 1.15, arms_up=cheer * abs(math.sin(t * 6 + 1)))
    if solution:
        pos, lv, tilt, streams, tap_to = bucket_states(t)
    else:
        pos = {n: BUCKETS[n]["home"] for n in BUCKETS}
        lv, tilt, streams, tap_to = {"big": 0, "small": 0}, {"big": 0, "small": 0}, [], None
    draw_barrel(cv, t, stream_to=tap_to)
    draw_person(cv, 680, FLOOR, DARIO, face=dario_face, wave=0, arms_up=cheer * abs(math.sin(t * 6 + 2)),
                h=DARIO.h * 1.25)
    draw_table(cv)
    lips = {}
    order = sorted(BUCKETS, key=lambda n: 1 if tilt[n] else 0)   # pouring bucket in front
    for n in order:
        lips[n] = draw_bucket(cv, n, pos[n][0], pos[n][1], lv[n], tilt[n])
    for src, target in streams:
        lip = lips[src]
        d = 1 if tilt[src] > 0 else -1
        cv.line([lip, (lip[0] + d * 12, lip[1] + 24), (lip[0] + d * 18, target[1] + 6)], (238, 243, 246, 235), 13)
    return pos, lv


# ------------------------------------------------------------------ overlays
def level_pills(img, view, pos, lv, scale=1.0, show=("big", "small")):
    for n in show:
        b = BUCKETS[n]
        x, y = pos[n]
        sx, sy = w2s(x, y + 52, view)
        bg = "#37b26c" if (abs(lv[n] - 4) < 0.04 and n == "big") else "#ffffff"
        fg = "#ffffff" if bg == "#37b26c" else "#22243a"
        pill(img, clamp(sx, 110, 850), min(sy, 1430), fmt_l(lv[n]), 44, bg=bg, fg=fg, pad=(22, 10), scale=scale)


def cap_labels(img, view, scale):
    for n in BUCKETS:
        x, y = BUCKETS[n]["home"]
        sx, sy = w2s(x, y - BUCKETS[n]["h"] - 110, view)
        pill(img, sx, sy, f"{BUCKETS[n]['cap']}-LITER-EIMER", 34, bg="#ffd34d", pad=(18, 9), scale=scale)


# ------------------------------------------------------------------ scenes
def scene_story(t):
    t0, t1, t2, t3 = st("Dario will"), st("Das Getränk"), st("Zum Abmessen"), st("Und die Eimer")
    cam = keyframes(t, [(t0, FULL), (t0 + 1.2, FULL), (t1, CAM)])

    def actors(cv):
        draw_scene(cv, t, solution=False, dario_face=1)

    frame, view = render_world_frame(cam, actors)
    if t < t1 + 0.2:
        out = 1 - prog(t, t1 - 0.1, t1 + 0.2)
        sx, sy = w2s(680, FLOOR - 330, view)
        pill(frame, sx, sy, "DARIO", 52, bg="#ffd34d", rot=3, scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.5)) * out)
        pill(frame, OUT_W / 2, 330, "ZIEL: GENAU 4 LITER", 60, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, t0 + 1.0, t0 + 1.35)) * out)
    if t1 <= t < t2 + 0.2:
        sx, sy = w2s((BARREL[0] + BARREL[1]) / 2, BARREL[2] - 60, view)
        pill(frame, min(sx, 820), sy, "DAS FASS", 48, bg="#fff6e6", rot=-3, scale=ease_out_back(prog(t, t1, t1 + 0.35)))
    if t2 <= t:
        cap_labels(frame, view, ease_out_back(prog(t, t2 + 0.6, t2 + 0.95)))
    if t3 <= t:
        pill(frame, OUT_W / 2, 330, "KEINE MARKIERUNGEN!", 58, bg="#e2574c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, t3 + 0.2, t3 + 0.55)))
    return frame


Q_FEET = 1150


def scene_question(t):
    t0, t_pause, t_tip, t_cm = st("Wie bekommt"), st("PAUSE"), st("Kleiner Tipp"), st("Schreib deine")
    img = vgradient(OUT_W, OUT_H, [(0, "#14213d"), (1, "#2b3f74")])
    cv = Canvas(img)
    rng = np.random.default_rng(1)
    for _ in range(70):
        x, y = rng.uniform(0, OUT_W), rng.uniform(0, OUT_H)
        tw = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv.circle(x, y, 2 + 2 * tw, fill=(255, 255, 255, int(80 + 100 * tw)))
    s = 1.9
    cvs = Canvas(img, -(OUT_W / 2 - 200) / s, -Q_FEET / s, s)
    cvs.ellipse(-70, -8, 70, 12, fill=(0, 0, 0, 70))
    draw_person(cvs, 0, 0, DARIO, face=1, reach=(30, -178))
    bx0, by0 = OUT_W / 2 + 10, 1340
    cb = Canvas(img, -bx0, -by0, 1.0)
    draw_bucket(cb, "big", 0, 0, 0)
    draw_bucket(cb, "small", 250, 0, 0)
    pill(img, bx0, by0 - 120, "5 L", 44, pad=(18, 8))
    pill(img, bx0 + 250, by0 - 95, "3 L", 44, pad=(18, 8))
    pill(img, OUT_W / 2 + 200, Q_FEET - 300, "4 L ?", 60, bg="#37b26c", fg="#ffffff", rot=4,
         scale=ease_out_back(prog(t, t0 + 0.4, t0 + 0.75)))
    p = ease_out_back(prog(t, t0, t0 + 0.35))
    pill(img, OUT_W / 2, 360, "WIE BEKOMMT ER", 84, bg="#fff6e6", scale=p, rot=-3)
    pill(img, OUT_W / 2, 515, "GENAU 4 LITER?", 88, bg="#ffd34d", scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)),
         rot=2)
    if t_pause - 0.2 < t < t_tip:
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            cv.circle(OUT_W / 2 - 80 + i * 70, Q_FEET - 440 - i * 35, 20 + 10 * a, fill=(255, 255, 255, int(120 + 135 * a)))
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
        draw_scene(cv, 0, solution=False, dario_face=1)
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
    cv = Canvas(img)
    cv.ellipse(OUT_W / 2 - 200, 1462, OUT_W / 2 + 200, 1488, fill=(0, 0, 0, 90))
    s = 1.3
    draw_person(Canvas(img, -(OUT_W / 2 - 80) / s, -1470 / s, s), 0, 0, DARIO, face=1, wave=t * 9)
    draw_bucket(Canvas(img, -(OUT_W / 2 + 130), -1470, 1.0), "big", 0, 0, 4)
    pill(img, OUT_W / 2 + 130, 1400, "4 L", 40, bg="#37b26c", fg="#ffffff", pad=(18, 8))
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
