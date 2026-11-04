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
from animals import draw_tiger, draw_pistol, draw_crutch, draw_saber, draw_pirate_extras

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
GUNMAN = Style(205, "#e9b48f", "#7a7a7a", "#5d6270", "#3b4a6b", hair_style="short", beard=True, shoes="#22243a")
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


def draw_world():
    img = Image.new("RGB", (W * ZW, H * ZW))
    img.paste(vgradient(W * ZW, WALL_BOTTOM * ZW, [(0, "#201b26"), (0.45, "#2f2836"), (1, "#3d3546")]), (0, 0))
    cv = Canvas(img, 0, 0, ZW)
    rng = np.random.default_rng(5)
    # stone blocks
    for row, y in enumerate(range(240, WALL_BOTTOM, 64)):
        off = (row % 2) * 60
        for x in range(-120 + off, W + 120, 120):
            sh = rng.uniform(-0.06, 0.08)
            col = mix(hexc(STONE), (255, 255, 255), max(0, sh)) if sh > 0 else mix(hexc(STONE), (0, 0, 0), -sh)
            cv.rect(x + 4, y + 4, x + 116, y + 60, fill=col, r=10)
    # vaulted ceiling (arches + ribs)
    for k, cx in enumerate((-60, 323, 617, 1140)):
        cv.ellipse(cx - 330, -260, cx + 330, 520, fill=hexc("#2a2430"))
    for cx in (175, 470, 765):
        cv.arc(cx - 300, -200, cx + 300, 560, 180, 360, hexc(STONE_L), 26)
    for x in (322, 617):
        cv.rect(x - 22, 150, x + 22, WALL_BOTTOM, fill=hexc(STONE_D))
        cv.rect(x - 30, 140, x + 30, 175, fill=hexc(STONE_L), r=6)
    # cobwebs
    for (cx, cy, d) in ((0, 250, 1), (W, 250, -1)):
        for r in (60, 110, 160):
            cv.arc(cx - r, cy - r, cx + r, cy + r, 0 if d > 0 else 90, 90 if d > 0 else 180, (220, 220, 230, 90), 3)
        for a in (0.15, 0.6, 1.1, 1.45):
            cv.line([(cx, cy), (cx + d * math.cos(a) * 170, cy + math.sin(a) * 170)], (220, 220, 230, 90), 3, cap=False)
    # doors: stone arch frame, wooden leaf drawn per frame (opening)
    for k in range(3):
        cv.poly(door_poly(k, -26), fill=hexc(STONE_L))
        cv.poly(door_poly(k, -12), fill=hexc("#6d6374"))
        cv.poly(door_poly(k, 0), fill=hexc("#140f18"))
        # number plaque
        cx = DOOR_X[k]
        cv.rect(cx - 34, DOOR_RECT_TOP - DOOR_W / 2 - 92, cx + 34, DOOR_RECT_TOP - DOOR_W / 2 - 34, fill=hexc("#b8902f"), r=8)
        cv.text(cx, DOOR_RECT_TOP - DOOR_W / 2 - 63, str(k + 1), 40, hexc("#2b1d14"))
    # floor (perspective flagstones)
    floor = vgradient(W * ZW, (H - WALL_BOTTOM) * ZW, [(0, "#4f4652"), (1, "#2a2430")])
    img.paste(floor, (0, WALL_BOTTOM * ZW))
    cv = Canvas(img, 0, 0, ZW)
    y, step = WALL_BOTTOM, 26
    while y < H:
        cv.rect(0, y, W, y + 3, fill=hexc("#3a3340"))
        y += step
        step *= 1.22
    for k in range(-8, 9):
        cv.line([(W / 2 + k * 70, WALL_BOTTOM), (W / 2 + k * 260, H)], hexc("#3a3340"), 3, cap=False)
    cv.rect(0, WALL_BOTTOM - 6, W, WALL_BOTTOM + 6, fill=hexc(STONE_D))
    # puddle + old barrel
    cv.ellipse(600, 1330, 820, 1370, fill=(120, 140, 170, 60))
    cv.ellipse(930, 1000, 1080, WALL_BOTTOM + 10, fill=hexc(WOOD_D))
    cv.rect(935, 1010, 1075, WALL_BOTTOM, fill=hexc(WOOD))
    for yy in (1040, 1140):
        cv.rect(930, yy - 8, 1080, yy + 8, fill=hexc("#3a3d46"))
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
    """wooden door leaf hinged on the left, opening = narrowing (perspective)"""
    cx = DOOR_X[k]
    pts = door_poly(k, 0)
    x0 = cx - DOOR_W / 2
    f = 1 - 0.86 * smooth(opened)
    leaf = [(x0 + (x - x0) * f, y + (0 if x == x0 else (y - WALL_BOTTOM) * 0.0)) for x, y in pts]
    shade = mix(hexc(WOOD), (0, 0, 0), 0.35 * smooth(opened))
    cv.poly(leaf, fill=shade)
    for i in range(1, 5):
        px = x0 + DOOR_W * i / 5 * f
        cv.line([(px, WALL_BOTTOM), (px, DOOR_RECT_TOP - math.sqrt(max(0, (DOOR_W / 2) ** 2 - (px - cx) ** 2)) * (1 if f > 0.95 else 0.9) + 4)],
                hexc(WOOD_D), 4, cap=False)
    for yy in (DOOR_RECT_TOP + 40, WALL_BOTTOM - 70):
        cv.rect(x0 + 6 * f, yy - 9, x0 + (DOOR_W - 6) * f, yy + 9, fill=hexc("#2c2f38"))
        for rx in (x0 + 18 * f, x0 + (DOOR_W - 18) * f):
            cv.circle(rx, yy, 5, fill=hexc("#8a8f99"))
    if f > 0.4:
        hx = x0 + DOOR_W * 0.8 * f
        cv.circle(hx, (DOOR_RECT_TOP + WALL_BOTTOM) / 2, 14, outline=hexc("#b8902f"), width=5)


def outside(cv, k, t, starved=False):
    """what waits behind door k (drawn into the doorway, clipped)"""
    cx = DOOR_X[k]
    sky = [(cx - DOOR_W / 2, DOOR_RECT_TOP - DOOR_W / 2), (cx + DOOR_W / 2, WALL_BOTTOM)]
    cv.rect(sky[0][0], sky[0][1], sky[1][0], WALL_BOTTOM - 140, fill=hexc("#9fd2f0"))
    cv.rect(sky[0][0], WALL_BOTTOM - 150, sky[1][0], WALL_BOTTOM - 120, fill=hexc("#cfe9f6"))
    cv.rect(sky[0][0], WALL_BOTTOM - 130, sky[1][0], WALL_BOTTOM, fill=hexc("#6fae5a"))
    cv.circle(cx + 60, DOOR_RECT_TOP - 50, 26, fill=hexc("#fff3c4"))
    gy = WALL_BOTTOM - 20
    if k == 0:
        if starved:
            draw_tiger(cv, cx - 28, gy + 8, 0.68, face=1, starved=True)
            draw_tiger(cv, cx + 30, gy - 34, 0.6, face=-1, starved=True)
        else:
            r = 0.5 + 0.5 * math.sin(t * 6)
            draw_tiger(cv, cx - 34, gy - 30, 0.62, face=1, roar=r)
            draw_tiger(cv, cx + 28, gy, 0.72, face=-1, roar=1 - r)
    elif k == 1:
        hand = draw_person(cv, cx + 30, gy, GUNMAN, face=-1, h=300, reach=(cx - 60, gy - 205),
                           bounce=abs(math.sin(t * 2)) * 2)
        draw_pistol(cv, hand, face=-1, s=1.0)
        draw_crutch(cv, (cx + 72, gy - 200), (cx + 95, gy), 1.0)
    else:
        sw = -0.9 + 0.35 * math.sin(t * 5)
        hand = draw_person(cv, cx + 20, gy, PIRATE, face=-1, h=300, reach=(cx - 50, gy - 240))
        draw_saber(cv, hand, face=-1, s=0.9, ang=sw)
        draw_pirate_extras(cv, cx + 20, gy, PIRATE, 300, face=-1)


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
    cam = keyframes(t, [(t0, (540, 1150, 1300)), (t1 - 0.1, (540, 1050, 1500)), (t1 + 0.5, FULL), (t2, FULL),
                        (t2 + 0.5, cam_door(0)), (t3 - 0.1, cam_door(0)), (t3 + 0.5, cam_door(1)), (t4 - 0.1, cam_door(1)),
                        (t4 + 0.5, cam_door(2)), (t5 - 0.4, cam_door(2)), (t5, FULL)])
    opened = [open_amount(t, t2 + 0.5, t3 - 0.1), open_amount(t, t3 + 0.5, t4 - 0.1), open_amount(t, t4 + 0.5, t5 - 0.2)]

    def actors(cv):
        torches(cv, t)
        draw_doors(cv, t, opened)
        if t < t2 + 0.3:
            draw_person(cv, 540, 1440, DU, face=1 if int(t * 0.8) % 2 else -1, h=300,
                        bounce=abs(math.sin(t * 3)) * 3, blink=(t % 3.2) < 0.13)

    frame, view = render_world_frame(cam, actors)
    if t < t1:
        sx, sy = w2s(540, 1440 - 360, view)
        pill(frame, sx, sy, "DU", 60, bg="#ffd34d", rot=3, scale=ease_out_back(prog(t, t0 + 0.3, t0 + 0.6)))
        pill(frame, OUT_W / 2, 330, "ALTES KELLERGEWÖLBE", 56, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, t0 + 0.6, t0 + 0.95)))
    if t1 <= t < t2 + 0.2:
        door_pills(frame, view, scale=ease_out_back(prog(t, t1 + 0.2, t1 + 0.55)))
        pill(frame, OUT_W / 2, 330, "3 TÜREN INS FREIE", 60, bg="#fff6e6", rot=-2,
             scale=ease_out_back(prog(t, t1 + 0.4, t1 + 0.75)))
    for k, (ta, tb, lab) in enumerate(((t2, t3, "2 TIGER · 5 MONATE NICHTS GEFRESSEN"),
                                        (t3, t4, "KRÜCKE + GELADENE PISTOLE"),
                                        (t4, t5, "EINÄUGIGER PIRAT MIT SÄBEL"))):
        if ta <= t < tb:
            pill(frame, OUT_W / 2, 330, f"TÜR {k + 1}", 64, bg="#ffd34d", rot=-2, scale=ease_out_back(prog(t, ta, ta + 0.3)))
            size = fit_size(lab, 740, 46)
            pill(frame, OUT_W / 2 - 20, 1400, lab, size, bg="#e2574c", fg="#ffffff",
                 scale=ease_out_back(prog(t, ta + 0.7, ta + 1.0)))
    return frame


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
        pill(frame, OUT_W / 2, 330, "TÜR 2: PISTOLE", 64, bg="#fff6e6", rot=-2, scale=ease_out_back(prog(t, a2, a2 + 0.3)))
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
