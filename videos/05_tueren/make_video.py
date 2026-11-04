"""Rätsel #5 – Die drei Türen im Kellergewölbe.

usage:  python3 make_video.py            -> renders video.mp4 (needs timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from animals import draw_tiger, draw_saber, draw_pirate_extras, draw_chainsaw, draw_parrot

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# ------------------------------------------------------------------ layout (world units = screen px, image 2x)
W, H = OUT_W, OUT_H
ZW = 2
WALL_BOTTOM = 1180                 # floor line
DOOR_X = (175, 470, 765)           # door centres (all left of TikTok's icon column)
DOOR_W, DOOR_RECT_TOP = 214, 880   # door width, top of the rectangular part (arch above)
TORCH_X = (322, 617, 912)
STONE, STONE_D, STONE_L = "#4a4250", "#3a3340", "#5d5464"
WOOD, WOOD_D = "#7a4f2e", "#5c3a22"
DU = Style(205, "#f1c19c", "#6b4423", "#e2574c", "#2f3a56", shoes="#ffffff", hair_style="quiff",
           accent="#9b2f27", under="#f4efe4", shoe_accent="#ffd34d")
SAWMAN = Style(205, "#e9b48f", "#3a3530", "#4a5a3a", "#3b3f4a", hair_style="short", beard=True, shoes="#22243a",
               accent="#2f3a26")
PIRATE = Style(205, "#c98c62", "#1d1712", "#8b2a2a", "#2f2a36", hair_style="short", beard=True, shoes="#22243a")


def door_poly(k, inset=0):
    cx = DOOR_X[k]
    w = DOOR_W / 2 - inset
    pts = [(cx - w, WALL_BOTTOM), (cx - w, DOOR_RECT_TOP)]
    for i in range(1, 16):
        a = math.pi - math.pi * i / 16
        pts.append((cx + math.cos(a) * w, DOOR_RECT_TOP - math.sin(a) * w))
    pts += [(cx + w, DOOR_RECT_TOP), (cx + w, WALL_BOTTOM)]
    return pts


# the world is larger than one screen: the opening shot shows the whole cellar, then zooms in
WX0, WY0, WX1, WY1 = -270, -480, 1350, 2400


def _paste_grad(img, x0, y0, x1, y1, stops):
    g = vgradient(int((x1 - x0) * ZW), int((y1 - y0) * ZW), stops)
    img.paste(g, (int((x0 - WX0) * ZW), int((y0 - WY0) * ZW)))


def draw_world():
    img = Image.new("RGB", (int((WX1 - WX0) * ZW), int((WY1 - WY0) * ZW)))
    _paste_grad(img, WX0, WY0, WX1, WALL_BOTTOM, [(0, "#16121b"), (0.35, "#241f2b"), (1, "#3d3546")])
    cv = Canvas(img, WX0, WY0, ZW)
    rng = np.random.default_rng(5)
    # stone blocks over the whole wall
    for row, y in enumerate(range(-60, WALL_BOTTOM, 64)):
        off = (row % 2) * 60
        for x in range(WX0 - 120 + off, WX1 + 120, 120):
            sh = rng.uniform(-0.06, 0.08)
            col = mix(hexc(STONE), (255, 255, 255), max(0, sh)) if sh > 0 else mix(hexc(STONE), (0, 0, 0), -sh)
            if y < 200:
                col = mix(col, (0, 0, 0), 0.35)
            cv.rect(x + 4, y + 4, x + 116, y + 60, fill=col, r=10)
    # vaulted ceiling: big arches and ribs
    for cx in (-280, 28, 323, 617, 912, 1210):
        cv.ellipse(cx - 330, -560, cx + 330, 520, fill=hexc("#1f1a25"))
    for cx in (-125, 175, 470, 765, 1060):
        cv.arc(cx - 300, -420, cx + 300, 560, 180, 360, hexc(STONE_L), 26)
    for x in (-125, 28, 322, 617, 912, 1210):
        cv.rect(x - 22, 150, x + 22, WALL_BOTTOM, fill=hexc(STONE_D))
        cv.rect(x - 30, 140, x + 30, 175, fill=hexc(STONE_L), r=6)
    # hanging chains
    for cx, ln in ((-60, 380), (1150, 300), (470, 120)):
        for k in range(int(ln / 22)):
            y = -300 + k * 22
            cv.ellipse(cx - 7, y, cx + 7, y + 26, outline=hexc("#6b707c"), width=4)
    # cobwebs in the corners of the big view and above the doors
    for (cx, cy, d, R) in ((WX0, -60, 1, 260), (WX1, -60, -1, 260), (0, 250, 1, 160), (W, 250, -1, 160)):
        for r in (R * 0.35, R * 0.65, R):
            cv.arc(cx - r, cy - r, cx + r, cy + r, 0 if d > 0 else 90, 90 if d > 0 else 180, (220, 220, 230, 90), 3)
        for a in (0.15, 0.6, 1.1, 1.45):
            cv.line([(cx, cy), (cx + d * math.cos(a) * R * 1.05, cy + math.sin(a) * R * 1.05)], (220, 220, 230, 90), 3,
                    cap=False)
    # left alcove: wine rack with dusty bottles
    rx0, rx1 = -245, 0
    cv.rect(rx0, 600, rx1, WALL_BOTTOM, fill=hexc(WOOD_D))
    for k in range(6):
        y = 640 + k * 90
        cv.rect(rx0, y + 70, rx1, y + 82, fill=hexc(WOOD))
        for j in range(5):
            bx = rx0 + 26 + j * 46
            cv.ellipse(bx - 18, y + 30, bx + 18, y + 68, fill=hexc(["#2f5a3a", "#5a1d2a", "#3a3d46"][(j + k) % 3]))
            cv.circle(bx, y + 49, 6, fill=hexc("#d9a441"))
    # right alcove: barrel pyramid + crates
    for (bx, by, r) in ((1130, WALL_BOTTOM - 70, 70), (1270, WALL_BOTTOM - 70, 70), (1200, WALL_BOTTOM - 200, 70)):
        cv.circle(bx, by, r, fill=hexc(WOOD))
        cv.circle(bx, by, r * 0.72, outline=hexc("#3a3d46"), width=8)
        cv.circle(bx, by, r * 0.3, fill=hexc(WOOD_D))
    for (x0, y0, w_) in ((1080, WALL_BOTTOM + 40, 120), (1210, WALL_BOTTOM + 10, 100)):
        cv.rect(x0, y0, x0 + w_, y0 + w_ * 0.8, fill=hexc("#9a6a3a"))
        cv.line([(x0, y0), (x0 + w_, y0 + w_ * 0.8)], hexc(WOOD_D), 6, cap=False)
        cv.line([(x0 + w_, y0), (x0, y0 + w_ * 0.8)], hexc(WOOD_D), 6, cap=False)
    # doors: stone arch frame, wooden leaf drawn per frame (opening)
    for k in range(3):
        cv.poly(door_poly(k, -26), fill=hexc(STONE_L))
        cv.poly(door_poly(k, -12), fill=hexc("#6d6374"))
        cv.poly(door_poly(k, 0), fill=hexc("#140f18"))
        cx = DOOR_X[k]
        cv.rect(cx - 34, DOOR_RECT_TOP - DOOR_W / 2 - 92, cx + 34, DOOR_RECT_TOP - DOOR_W / 2 - 34, fill=hexc("#b8902f"), r=8)
        cv.text(cx, DOOR_RECT_TOP - DOOR_W / 2 - 63, str(k + 1), 40, hexc("#2b1d14"))
    # floor (perspective flagstones), deeper towards the viewer
    _paste_grad(img, WX0, WALL_BOTTOM, WX1, WY1, [(0, "#4f4652"), (0.4, "#3a3340"), (1, "#1c1820")])
    cv = Canvas(img, WX0, WY0, ZW)
    y, step = WALL_BOTTOM, 26
    while y < WY1:
        cv.rect(WX0, y, WX1, y + 3, fill=hexc("#3a3340"))
        y += step
        step *= 1.22
    for k in range(-12, 13):
        cv.line([(W / 2 + k * 70, WALL_BOTTOM), (W / 2 + k * 330, WY1)], hexc("#3a3340"), 3, cap=False)
    cv.rect(WX0, WALL_BOTTOM - 6, WX1, WALL_BOTTOM + 6, fill=hexc(STONE_D))
    # puddle, old barrel, straw, bucket, broom
    cv.ellipse(600, 1330, 820, 1370, fill=(120, 140, 170, 60))
    cv.ellipse(-150, 1900, 150, 1960, fill=(120, 140, 170, 50))
    cv.ellipse(930, 1000, 1080, WALL_BOTTOM + 10, fill=hexc(WOOD_D))
    cv.rect(935, 1010, 1075, WALL_BOTTOM, fill=hexc(WOOD))
    for yy in (1040, 1140):
        cv.rect(930, yy - 8, 1080, yy + 8, fill=hexc("#3a3d46"))
    for _ in range(40):
        x, y = rng.uniform(WX0, WX1), rng.uniform(1500, WY1 - 50)
        a = rng.uniform(0, 3.14)
        cv.line([(x, y), (x + math.cos(a) * 26, y + math.sin(a) * 6)], hexc("#b89a5a"), 3, cap=False)
    cv.poly([(-200, 1650), (-120, 1650), (-130, 1740), (-190, 1740)], fill=hexc("#6b707c"))
    cv.arc(-205, 1610, -115, 1700, 180, 360, hexc("#3a3d46"), 5)
    cv.line([(1230, 1450), (1310, 1880)], hexc(WOOD), 10)
    cv.poly([(1290, 1860), (1340, 1860), (1350, 1960), (1270, 1960)], fill=hexc("#b89a5a"))
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
    vh = min(vh, WY1 - WY0)
    vw = vh * OUT_W / OUT_H
    cx = clamp(cx, WX0 + vw / 2, WX1 - vw / 2)
    cy = clamp(cy, WY0 + vh / 2, WY1 - vh / 2)
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    crop = world().crop((int(round((box[0] - WX0) * ZW)), int(round((box[1] - WY0) * ZW)),
                         int(round((box[2] - WX0) * ZW)), int(round((box[3] - WY0) * ZW))))
    cv = Canvas(crop, box[0], box[1], ZW)
    actors(cv)
    return crop.resize((OUT_W, OUT_H), Image.LANCZOS), (box, vh / OUT_H)


def w2s(x, y, view):
    box, k = view
    return (x - box[0]) / k, (y - box[1]) / k


FULL = (W / 2, H / 2, H)
BIG = (W / 2, (WY0 + WY1) / 2, WY1 - WY0)     # the whole cellar


def cam_door(k):
    return (DOOR_X[k], 1060, 860)


# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Du befindest", "Drei alte", "Hinter der ersten", "Hinter der zweiten", "Und hinter der dritten",
        "Durch welche", "PAUSE", "Kleiner Tipp", "Schreib deine", "Hier kommt", "Hinter Tür zwei",
        "Hinter Tür drei", "Aber Tür eins", "Denn Tiger", "Du kannst also", "Hättest", "Schreib's"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 2.6
XFADE = 0.25


def st(key):
    return S[K[key]]


# ------------------------------------------------------------------ props per frame
def cellar_life(cv, t):
    """small, slow details that make the big cellar feel alive"""
    # chandelier with flickering candles
    cx, cy = 540, -170
    cv.line([(cx, -480), (cx, cy)], hexc("#3a3d46"), 5, cap=False)
    cv.ellipse(cx - 150, cy - 18, cx + 150, cy + 18, outline=hexc("#6b707c"), width=8)
    for i in range(5):
        x = cx - 120 + i * 60
        cv.rect(x - 7, cy - 52, x + 7, cy - 12, fill=hexc("#efe6d2"))
        fl = 0.8 + 0.2 * math.sin(t * 12 + i * 1.7)
        cv.circle(x, cy - 66, 22 * fl, fill=(255, 190, 100, 40))
        cv.poly([(x - 6, cy - 54), (x + 6, cy - 54), (x + 2 * math.sin(t * 10 + i), cy - 54 - 20 * fl)], fill=hexc("#ffd07a"))
    # spider going up and down on its thread
    sy = -260 + 120 * (0.5 + 0.5 * math.sin(t * 0.9))
    cv.line([(1150, -480), (1150, sy)], (220, 220, 230, 140), 2, cap=False)
    cv.circle(1150, sy + 10, 12, fill=hexc("#1d1a24"))
    for k in range(4):
        for d in (-1, 1):
            cv.line([(1150, sy + 10), (1150 + d * 20, sy + 2 + k * 6), (1150 + d * 26, sy + 14 + k * 6)],
                    hexc("#1d1a24"), 3, cap=False)
    # water drop falling into the puddle
    ph = (t * 0.7) % 1
    dy = 230 + (1330 - 230) * ph ** 2
    if ph < 0.93:
        cv.ellipse(706, dy - 9, 714, dy + 6, fill=(170, 200, 235, 200))
    else:
        r = 10 + (ph - 0.93) * 700
        cv.ellipse(710 - r, 1345 - r * 0.25, 710 + r, 1345 + r * 0.25, outline=(170, 200, 235, 160), width=3)
    # a rat scurrying across the front floor now and then
    rp = (t % 9.0) / 9.0
    if rp < 0.35:
        rx = WX0 - 60 + (WX1 - WX0 + 120) * (rp / 0.35)
        ry = 1720 + 4 * math.sin(t * 30)
        cv.ellipse(rx - 34, ry - 18, rx + 34, ry + 14, fill=hexc("#5d5664"))
        cv.circle(rx + 34, ry - 6, 14, fill=hexc("#5d5664"))
        cv.circle(rx + 30, ry - 20, 7, fill=hexc("#e98aa0"))
        cv.circle(rx + 40, ry - 8, 2.5, fill=hexc("#ffffff"))
        cv.line([(rx - 34, ry), (rx - 80, ry - 10 + 8 * math.sin(t * 20))], hexc("#e98aa0"), 3)


def torches(cv, t):
    for i, x in enumerate(TORCH_X):
        y = 640
        fl = 0.8 + 0.2 * math.sin(t * 11 + i * 2) * math.sin(t * 7.3 + i)
        cv.circle(x, y - 40, 120 * fl, fill=(255, 170, 80, 26))
        cv.circle(x, y - 40, 70 * fl, fill=(255, 190, 100, 40))
        cv.rect(x - 7, y - 20, x + 7, y + 60, fill=hexc(WOOD_D))
        cv.rect(x - 16, y - 30, x + 16, y - 14, fill=hexc("#3a3d46"), r=4)
        h = 46 * fl
        cv.poly([(x - 16, y - 30), (x + 16, y - 30), (x + 4 * math.sin(t * 9 + i), y - 30 - h)], fill=hexc("#ff9a2e"))
        cv.poly([(x - 8, y - 30), (x + 8, y - 30), (x + 3 * math.sin(t * 13 + i), y - 30 - h * 0.6)], fill=hexc("#ffe07a"))


def draw_leaf(cv, k, opened):
    """wooden door leaf hinged on the RIGHT (so everything behind it stays visible), opening = narrowing"""
    cx = DOOR_X[k]
    pts = door_poly(k, 0)
    x1 = cx + DOOR_W / 2
    f = 1 - 0.9 * smooth(opened)
    leaf = [(x1 - (x1 - x) * f, y) for x, y in pts]
    shade = mix(hexc(WOOD), (0, 0, 0), 0.35 * smooth(opened))
    cv.poly(leaf, fill=shade)
    if f > 0.25:
        for i in range(1, 5):
            px = x1 - DOOR_W * i / 5 * f
            cv.line([(px, WALL_BOTTOM), (px, DOOR_RECT_TOP - 0.85 * math.sqrt(max(0, (DOOR_W / 2) ** 2 - ((x1 - DOOR_W * i / 5) - cx) ** 2)) + 6)],
                    hexc(WOOD_D), 4, cap=False)
    for yy in (DOOR_RECT_TOP + 40, WALL_BOTTOM - 70):
        cv.rect(x1 - (DOOR_W - 6) * f, yy - 9, x1 - 6 * f, yy + 9, fill=hexc("#2c2f38"))
        for rx in (x1 - (DOOR_W - 18) * f, x1 - 18 * f):
            cv.circle(rx, yy, 5, fill=hexc("#8a8f99"))
    if f > 0.4:
        hx = x1 - DOOR_W * 0.8 * f
        cv.circle(hx, (DOOR_RECT_TOP + WALL_BOTTOM) / 2, 14, outline=hexc("#b8902f"), width=5)


def outside(cv, k, t, starved=False):
    """what waits behind door k (drawn into the doorway, clipped) – animated"""
    cx = DOOR_X[k]
    x0, x1 = cx - DOOR_W / 2, cx + DOOR_W / 2
    top = DOOR_RECT_TOP - DOOR_W / 2
    cv.rect(x0, top, x1, WALL_BOTTOM - 140, fill=hexc("#9fd2f0"))
    cv.rect(x0, WALL_BOTTOM - 150, x1, WALL_BOTTOM - 120, fill=hexc("#cfe9f6"))
    cv.rect(x0, WALL_BOTTOM - 130, x1, WALL_BOTTOM, fill=hexc("#6fae5a"))
    cv.circle(cx + 60, DOOR_RECT_TOP - 50, 26, fill=hexc("#fff3c4"))
    for i in range(2):          # drifting clouds
        ccx = x0 - 60 + ((t * 18 + i * 140 + k * 50) % (DOOR_W + 120))
        ccy = top + 60 + i * 50
        cv.rect(ccx - 40, ccy - 10, ccx + 40, ccy + 12, fill=(255, 255, 255, 220), r=11)
        cv.circle(ccx - 8, ccy - 10, 16, fill=(255, 255, 255, 220))
    bx = x0 + ((t * 40 + k * 70) % (DOOR_W + 40)) - 20     # a bird far away
    by = top + 110 + 8 * math.sin(t * 2 + k)
    wing = 6 * math.sin(t * 14)
    cv.line([(bx - 10, by - wing), (bx, by), (bx + 10, by - wing)], hexc("#2b2140"), 3)
    for g in range(9):          # swaying grass
        gx = x0 + 12 + g * 24
        sw = 5 * math.sin(t * 2.2 + g)
        cv.line([(gx, WALL_BOTTOM - 4), (gx + sw, WALL_BOTTOM - 26)], hexc("#4f8a4c"), 4)
    gy = WALL_BOTTOM - 20
    if k == 0:
        if starved:
            draw_tiger(cv, cx - 28, gy + 8, 0.68, face=1, starved=True)
            draw_tiger(cv, cx + 30, gy - 34, 0.6, face=-1, starved=True)
            for i in range(4):  # flies circling
                a = t * 4 + i * 1.6
                fx, fy = cx + math.cos(a) * 46 + (i - 1.5) * 10, gy - 70 + math.sin(a * 1.3) * 18
                cv.circle(fx, fy, 3.5, fill=hexc("#22243a"))
                ww = 4 + 2 * math.sin(t * 40 + i)
                cv.ellipse(fx - ww, fy - 7, fx, fy - 2, fill=(255, 255, 255, 170))
                cv.ellipse(fx, fy - 7, fx + ww, fy - 2, fill=(255, 255, 255, 170))
        else:
            r = 0.5 + 0.5 * math.sin(t * 6)
            pace = 10 * math.sin(t * 1.6)
            draw_tiger(cv, cx - 34 - pace, gy - 30, 0.62, face=1, roar=r, phase=t * 6)
            draw_tiger(cv, cx + 28 + pace, gy, 0.72, face=-1, roar=1 - r, phase=t * 6 + 1)
    elif k == 1:
        rev = abs(math.sin(t * 3.0))
        sh = 3 * math.sin(t * 40) * rev
        hand = draw_person(cv, cx + 38 + sh, gy, SAWMAN, face=-1, h=300, reach=(cx - 20, gy - 170 + 10 * rev),
                           angry=True, lean=-6 * rev)
        draw_chainsaw(cv, hand, face=-1, s=0.62, t=t, running=True)
    else:
        sw = -1.1 + 0.6 * math.sin(t * 5)
        hand = draw_person(cv, cx + 34, gy, PIRATE, face=-1, h=300, reach=(cx - 40, gy - 250 - 20 * math.sin(t * 5)),
                           angry=True)
        draw_saber(cv, hand, face=-1, s=0.75, ang=sw)
        draw_pirate_extras(cv, cx + 34, gy, PIRATE, 300, face=-1)
        draw_parrot(cv, cx + 34 + 30, gy - 0.72 * 300 + 2, 0.8, t=t, face=-1)


def draw_doors(cv, t, opened, starved=False):
    """opened: list of 3 opening amounts (0..1)"""
    for k in range(3):
        if opened[k] > 0.02:
            layer = Image.new("RGBA", cv.img.size, (0, 0, 0, 0))
            lc = Canvas(layer, cv.ox, cv.oy, cv.s)
            outside(lc, k, t, starved=starved and k == 0)
            mask = Image.new("L", cv.img.size, 0)
            ImageDraw.Draw(mask).polygon([lc.p(x, y) for x, y in door_poly(k, 0)], fill=255)
            layer.putalpha(ImageChops.multiply(layer.split()[3], mask))
            cv.img.paste(layer, (0, 0), layer)
            cv.d = ImageDraw.Draw(cv.img, "RGBA")
            # daylight spilling into the cellar
            o = smooth(opened[k])
            cx = DOOR_X[k]
            cv.poly([(cx - DOOR_W / 2, WALL_BOTTOM), (cx + DOOR_W / 2, WALL_BOTTOM), (cx + DOOR_W * 0.9, WALL_BOTTOM + 260),
                     (cx - DOOR_W * 0.9, WALL_BOTTOM + 260)], fill=(255, 240, 200, int(50 * o)))
        draw_leaf(cv, k, opened[k])


def open_amount(t, t0, t1, ramp=0.45):
    return smooth(prog(t, t0, t0 + ramp)) * (1 - smooth(prog(t, t1 - ramp, t1)))


def fit_size(text, max_w, size):
    while font(size).getbbox(text)[2] + 70 > max_w and size > 24:
        size -= 2
    return size


def door_pills(frame, view, scale=1.0, hl=None):
    for k in range(3):
        sx, sy = w2s(DOOR_X[k], DOOR_RECT_TOP - DOOR_W / 2 - 150, view)
        bg = "#ffd34d" if hl == k else "#fff6e6"
        pill(frame, sx, sy, f"TÜR {k + 1}", 40, bg=bg, pad=(18, 9), scale=scale)


# ------------------------------------------------------------------ scenes
def scene_story(t):
    t0, t1, t2, t3, t4 = st("Du befindest"), st("Drei alte"), st("Hinter der ersten"), st("Hinter der zweiten"), \
        st("Und hinter der dritten")
    t5 = st("Durch welche")
    cam = keyframes(t, [(t0, BIG), (t0 + 0.25, BIG), (t1 - 0.15, (540, 1150, 1300)), (t1 + 0.55, FULL), (t2, FULL),
                        (t2 + 0.5, cam_door(0)), (t3 - 0.1, cam_door(0)), (t3 + 0.5, cam_door(1)), (t4 - 0.1, cam_door(1)),
                        (t4 + 0.5, cam_door(2)), (t5 - 0.4, cam_door(2)), (t5, FULL)])
    opened = [open_amount(t, t2 + 0.5, t3 - 0.1), open_amount(t, t3 + 0.5, t4 - 0.1), open_amount(t, t4 + 0.5, t5 - 0.2)]

    def actors(cv):
        cellar_life(cv, t)
        torches(cv, t)
        draw_doors(cv, t, opened)
        if t < t2 + 0.3:
            draw_person(cv, 540, 1440, DU, face=1 if int(t * 0.8) % 2 else -1, h=300,
                        bounce=abs(math.sin(t * 3)) * 3, blink=(t % 3.2) < 0.13)

    frame, view = render_world_frame(cam, actors)
    if t < t1:
        sx, sy = w2s(540, 1440 - 170, view)
        pill(frame, sx + 150, sy, "DU", 60, bg="#ffd34d", rot=3, scale=ease_out_back(prog(t, t0 + 0.3, t0 + 0.6)))

    if t1 <= t < t2 + 0.2:
        door_pills(frame, view, scale=ease_out_back(prog(t, t1 + 0.2, t1 + 0.55)))
        pill(frame, OUT_W / 2, 330, "3 TÜREN INS FREIE", 60, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, t1 + 0.4, t1 + 0.75)))
    karaoke_title(frame, t)
    for k, (ta, tb, lab) in enumerate(((t2, t3, "2 TIGER · 5 MONATE NICHTS GEFRESSEN"),
                                        (t3, t4, "BÖSER MANN MIT MOTORSÄGE"),
                                        (t4, t5, "EINÄUGIGER PIRAT MIT SÄBEL"))):
        if ta <= t < tb:
            pill(frame, OUT_W / 2, 330, f"TÜR {k + 1}", 64, bg="#ffd34d", rot=-2, scale=ease_out_back(prog(t, ta, ta + 0.3)))
            size = fit_size(lab, 740, 46)
            pill(frame, OUT_W / 2 - 20, 1400, lab, size, bg="#e2574c", fg="#ffffff",
                 scale=ease_out_back(prog(t, ta + 0.7, ta + 1.0)))
    return frame


TITLE_LINES = [(["DU", "BEFINDEST", "DICH"], "#fff6e6", -3), (["IN", "EINEM", "ALTEN"], "#ffd34d", 2),
               (["KELLERGEWÖLBE"], "#ffd34d", -2)]


def karaoke_title(frame, t):
    """whole first sentence visible from frame 0 (channel-style pills); the word being spoken pops up bigger"""
    t0, t1 = S[K["Du befindest"]], E[K["Du befindest"]]
    if t > t1 + 0.45:
        return
    words = [w for line, _, _ in TITLE_LINES for w in line]
    weights = [len(w) + 2 for w in words]
    tot = sum(weights)
    spans, acc = [], t0 + 0.02
    for wgt in weights:
        d_ = (t1 - t0 - 0.1) * wgt / tot
        spans.append((acc, acc + d_))
        acc += d_
    fade = 1 - prog(t, t1 + 0.1, t1 + 0.45)
    i = 0
    for li, (line, bg, rot) in enumerate(TITLE_LINES):
        base = 84 if li < 2 else 96
        gap = 0.28 * base
        while sum(font(base).getbbox(w)[2] for w in line) + gap * (len(line) - 1) > 600:
            base -= 2
            gap = 0.28 * base
        pops = []
        for j in range(len(line)):
            a_, b_ = spans[i + j]
            p = prog(t, a_ - 0.04, b_ + 0.1)
            pops.append(math.sin(math.pi * p) if 0 < p < 1 else 0.0)     # 0 -> 1 -> 0 while spoken
        sizes = [base * (1 + 0.32 * ease_out_back(min(1, pp * 1.4)) * (pp > 0)) if pp > 0 else base for pp in pops]
        widths = [font(int(sz)).getbbox(w)[2] for sz, w in zip(sizes, line)]
        tw = sum(widths) + gap * (len(line) - 1)
        if tw > 680:            # keep the popped line clear of TikTok's side areas
            k = 680 / tw
            sizes = [sz * k if pp > 0 else sz for sz, pp in zip(sizes, pops)]
            widths = [font(int(sz)).getbbox(w)[2] for sz, w in zip(sizes, line)]
            tw = sum(widths) + gap * (len(line) - 1)
        padx, pady = 34, 20
        hmax = max(sizes)
        Z = 2
        x0, y0 = 30, 30
        x1, y1 = x0 + tw + 2 * padx, y0 + base + 2 * pady
        PW, PH = int(x1 + 40), int(y0 + hmax + 2 * pady + 60)
        tile = Image.new("RGBA", (PW * Z, PH * Z), (0, 0, 0, 0))
        d = ImageDraw.Draw(tile)
        d.rounded_rectangle([(x0 + 8) * Z, (y0 + 12) * Z, (x1 + 8) * Z, (y1 + 12) * Z], radius=int((y1 - y0) / 3 * Z),
                            fill=(30, 20, 60, 90))
        d.rounded_rectangle([x0 * Z, y0 * Z, x1 * Z, y1 * Z], radius=int((y1 - y0) / 3 * Z), fill=hexc(bg))
        x = x0 + padx
        for j, w in enumerate(line):
            col = hexc("#c0392b") if pops[j] > 0.35 else hexc("#2b2140")
            d.text(((x + widths[j] / 2) * Z, (y0 + (y1 - y0) / 2) * Z), w, font=font(int(sizes[j] * Z)), fill=col,
                   anchor="mm")
            x += widths[j] + gap
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
        tile = tile.resize((max(1, tile.width // Z), max(1, tile.height // Z)), Image.LANCZOS)
        if fade < 1:
            tile.putalpha(tile.split()[3].point(lambda v: int(v * fade)))
        cy = 610 + li * 148
        px, py = int(OUT_W / 2 - tile.width / 2), int(cy - (y0 + (y1 - y0) / 2) - (tile.height - PH) / 2)
        frame.paste(tile, (px, py), tile)
        log_ui("title line " + str(li), px + 30, py + 30, px + tile.width - 30, py + tile.height - 30)
        i += len(line)


def door_icon(cv, x, y, s, n, open_=0.0):
    w, h = 110 * s, 190 * s
    cv.rect(x - w / 2 - 10 * s, y - h - 10 * s, x + w / 2 + 10 * s, y, fill=hexc(STONE_L), r=w / 2)
    cv.rect(x - w / 2, y - h, x + w / 2, y, fill=hexc(WOOD), r=w / 2 - 6 * s)
    for i in range(1, 4):
        cv.line([(x - w / 2 + w * i / 4, y - h + 20 * s), (x - w / 2 + w * i / 4, y)], hexc(WOOD_D), 3 * s, cap=False)
    cv.text(x, y - h * 0.62, str(n), 46 * s, hexc("#ffd34d"))


Q_FEET = 1150


def scene_question(t):
    t0, t_pause, t_tip, t_cm = st("Durch welche"), st("PAUSE"), st("Kleiner Tipp"), st("Schreib deine")
    img = vgradient(OUT_W, OUT_H, [(0, "#14213d"), (1, "#2b3f74")])
    cv = Canvas(img)
    rng = np.random.default_rng(1)
    for _ in range(70):
        x, y = rng.uniform(0, OUT_W), rng.uniform(0, OUT_H)
        tw = 0.5 + 0.5 * math.sin(t * 3 + x)
        cv.circle(x, y, 2 + 2 * tw, fill=(255, 255, 255, int(80 + 100 * tw)))
    s = 1.7
    cvs = Canvas(img, -(OUT_W / 2 - 250) / s, -Q_FEET / s, s)
    cvs.ellipse(-70, -8, 70, 12, fill=(0, 0, 0, 70))
    draw_person(cvs, 0, 0, DU, face=1, reach=(30, -178), blink=(t % 3.1) < 0.13)
    for k in range(3):
        door_icon(cv, OUT_W / 2 - 40 + k * 170, 1370, 1.1, k + 1)
    pill(img, OUT_W / 2 + 200, 860, "?", 110, bg="#ffd34d", rot=6, scale=ease_out_back(prog(t, t0 + 0.4, t0 + 0.7)))
    p = ease_out_back(prog(t, t0, t0 + 0.35))
    pill(img, OUT_W / 2, 360, "WELCHE TÜR", 92, bg="#fff6e6", scale=p, rot=-3)
    pill(img, OUT_W / 2, 515, "IST SICHER?", 100, bg="#ffd34d", scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)), rot=2)
    if t_pause - 0.2 < t < t_tip:
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            cv.circle(OUT_W / 2 - 180 + i * 70, 830 - i * 35, 20 + 10 * a, fill=(255, 255, 255, int(120 + 135 * a)))
    if t > t_tip:
        pill(img, OUT_W / 2, 670, "TIPP: DENK AN DIE ZEIT", 58, bg="#c5def5", rot=-2,
             scale=ease_out_back(prog(t, t_tip, t_tip + 0.35)))
    if t > t_cm:
        pill(img, OUT_W / 2, 1420, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff",
             scale=ease_out_back(prog(t, t_cm, t_cm + 0.35)))
    return img


def scene_solution(t):
    t0, a2, a3, a1, why, out = st("Hier kommt"), st("Hinter Tür zwei"), st("Hinter Tür drei"), st("Aber Tür eins"), \
        st("Denn Tiger"), st("Du kannst also")
    t_end = st("Hättest")
    cam = keyframes(t, [(t0, FULL), (a2, FULL), (a2 + 0.5, cam_door(1)), (a3 - 0.1, cam_door(1)), (a3 + 0.5, cam_door(2)),
                        (a1 - 0.1, cam_door(2)), (a1 + 0.5, cam_door(0)), (out - 0.1, cam_door(0)), (out + 0.6, FULL)])
    opened = [smooth(prog(t, why, why + 0.5)), open_amount(t, a2 + 0.5, a3 - 0.1), open_amount(t, a3 + 0.5, a1 - 0.2)]
    # you walk out through door 1 (getting smaller = further away)
    walk = prog(t, out + 0.6, t_end - 0.3)

    def actors(cv):
        cellar_life(cv, t)
        torches(cv, t)
        draw_doors(cv, t, opened, starved=True)
        if t >= out + 0.4:
            x = 540 + (DOOR_X[0] + 20 - 540) * smooth(walk)
            y = 1440 + (WALL_BOTTOM + 10 - 1440) * smooth(walk)
            hh = 300 * (1 - 0.35 * smooth(walk))
            if walk < 0.98:
                draw_person(cv, x, y, DU, face=-1, h=hh, phase=t * 10 if 0 < walk < 1 else None)

    frame, view = render_world_frame(cam, actors)
    if t < t0 + 1.4:
        pill(frame, OUT_W / 2, 330, "DIE LÖSUNG", 96, bg="#fff6e6", rot=-4,
             scale=ease_out_back(prog(t, t0, t0 + 0.35)) * (1 - prog(t, t0 + 1.1, t0 + 1.4)))
    if t0 + 1.0 < t < a2:
        door_pills(frame, view)
    if a2 <= t < a3:
        pill(frame, OUT_W / 2, 330, "TÜR 2: MOTORSÄGE", 64, bg="#fff6e6", rot=-2, scale=ease_out_back(prog(t, a2, a2 + 0.3)))
        check_icon(frame, OUT_W / 2, 1380, 70, ok=False, scale=ease_out_back(prog(t, a2 + 0.9, a2 + 1.2)))
    if a3 <= t < a1:
        pill(frame, OUT_W / 2, 330, "TÜR 3: SÄBEL", 64, bg="#fff6e6", rot=-2, scale=ease_out_back(prog(t, a3, a3 + 0.3)))
        check_icon(frame, OUT_W / 2, 1380, 70, ok=False, scale=ease_out_back(prog(t, a3 + 0.9, a3 + 1.2)))
    if a1 <= t < out:
        pill(frame, OUT_W / 2, 330, "TÜR 1 IST RICHTIG!", 64, bg="#37b26c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, a1, a1 + 0.3)))
    if why + 0.5 <= t < out + 0.6:
        pill(frame, OUT_W / 2, 1300, "5 MONATE OHNE FRESSEN", 46, bg="#fff6e6",
             scale=ease_out_back(prog(t, why + 0.6, why + 0.9)))
        pill(frame, OUT_W / 2 - 20, 1405, "= LÄNGST VERHUNGERT!", 46, bg="#e2574c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, why + 1.2, why + 1.5)))
    if t >= out:
        pill(frame, OUT_W / 2, 330, "ENTSPANNT INS FREIE", 60, bg="#37b26c", fg="#ffffff", rot=-2,
             scale=ease_out_back(prog(t, out, out + 0.35)))
        sx, sy = w2s(DOOR_X[0], DOOR_RECT_TOP - DOOR_W / 2 - 150, view)
        check_icon(frame, sx, sy, 50, scale=ease_out_back(prog(t, out + 0.6, out + 0.9)))
    return frame


def scene_outro(t):
    t0, t1 = st("Hättest"), st("Schreib's")

    def actors(cv):
        torches(cv, t)
        draw_doors(cv, t, [1.0, 0.0, 0.0], starved=True)
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
    cv.ellipse(OUT_W / 2 - 110, 1462, OUT_W / 2 + 110, 1488, fill=(0, 0, 0, 90))
    s = 1.3
    draw_person(Canvas(img, -(OUT_W / 2) / s, -1470 / s, s), 0, 0, DU, face=1, wave=t * 9, blink=(t % 3) < 0.12)
    return img


SCENES = [
    (0.0, scene_story),
    (st("Durch welche") - 0.05, scene_question),
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
