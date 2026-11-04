"""Flat-vector animals and props in the channel style (world coordinates, feet/ground at y)."""
import math
import numpy as np
from toolkit import hexc, mix

INK = hexc("#22243a")


def _dk(c, f=0.2):
    return mix(c, (20, 16, 30), f)


def _legs(cv, xs, y_top, y, col, w, phase):
    for i, lx in enumerate(xs):
        sw = math.sin(phase + (math.pi if i % 2 else 0)) * 0.35 if phase is not None else 0
        fx = lx + math.sin(sw) * (y - y_top)
        cv.line([(lx, y_top), (fx, y - w * 0.3)], col, w)
        cv.rect(fx - w * 0.55, y - w * 0.55, fx + w * 0.6, y, fill=INK, r=w * 0.2)


def draw_wolf(cv, x, y, s=1.0, face=1, phase=None, mood=0.0):
    """Grey wolf, ~170*s long. mood>0 leans the head down (hungry look)."""
    f = face
    fur, fur_d, belly = hexc("#8d93a3"), hexc("#666c7c"), hexc("#dfe1e7")
    L, Hb = 170 * s, 72 * s           # body length, body height
    by = y - 62 * s                    # body centre y
    # tail
    cv.poly([(x - f * L * 0.42, by - Hb * 0.15), (x - f * L * 0.78, by - Hb * 0.55), (x - f * L * 0.82, by - Hb * 0.25),
             (x - f * L * 0.62, by + Hb * 0.1)], fill=fur_d)
    cv.poly([(x - f * L * 0.74, by - Hb * 0.45), (x - f * L * 0.84, by - Hb * 0.6), (x - f * L * 0.8, by - Hb * 0.32)],
            fill=belly)
    # back legs (far)
    _legs(cv, [x - f * L * 0.28, x + f * L * 0.22], by + Hb * 0.1, y, fur_d, 16 * s, phase)
    # body
    cv.ellipse(x - L * 0.47, by - Hb * 0.5, x + L * 0.47, by + Hb * 0.5, fill=fur)
    cv.ellipse(x - L * 0.3, by, x + L * 0.3, by + Hb * 0.52, fill=belly)
    # front legs (near)
    _legs(cv, [x - f * L * 0.34, x + f * L * 0.3], by + Hb * 0.15, y, fur, 17 * s, None if phase is None else phase + 1)
    # neck + head
    hx, hy = x + f * L * 0.48, by - Hb * 0.55 + mood * 25 * s
    cv.poly([(x + f * L * 0.25, by - Hb * 0.4), (hx - f * 10 * s, hy - 18 * s), (hx + f * 6 * s, hy + 26 * s),
             (x + f * L * 0.38, by + Hb * 0.2)], fill=fur)
    cv.circle(hx, hy, 30 * s, fill=fur)
    # ears
    for dx in (-14, 8):
        ex = hx + f * dx * s
        cv.poly([(ex - 11 * s, hy - 20 * s), (ex + 2 * s, hy - 52 * s), (ex + 13 * s, hy - 18 * s)], fill=fur_d)
        cv.poly([(ex - 5 * s, hy - 22 * s), (ex + 2 * s, hy - 40 * s), (ex + 7 * s, hy - 21 * s)], fill=hexc("#d9a0a0"))
    # snout
    cv.poly([(hx + f * 8 * s, hy - 12 * s), (hx + f * 54 * s, hy + 4 * s), (hx + f * 52 * s, hy + 16 * s),
             (hx + f * 6 * s, hy + 22 * s)], fill=belly)
    cv.circle(hx + f * 52 * s, hy + 6 * s, 7 * s, fill=INK)
    cv.line([(hx + f * 18 * s, hy + 18 * s), (hx + f * 44 * s, hy + 15 * s)], INK, 3 * s)
    # eye + brow (a bit sly)
    cv.ellipse(hx + f * 6 * s, hy - 12 * s, hx + f * 20 * s, hy - 1 * s, fill=hexc("#ffd34d"))
    cv.circle(hx + f * 14 * s, hy - 6 * s, 3.5 * s, fill=INK)
    cv.line([(hx + f * 2 * s, hy - 18 * s), (hx + f * 22 * s, hy - 13 * s)], INK, 4 * s)
    # cheek fluff
    cv.poly([(hx - f * 22 * s, hy + 4 * s), (hx - f * 34 * s, hy + 22 * s), (hx - f * 12 * s, hy + 18 * s)], fill=belly)


def draw_goat(cv, x, y, s=1.0, face=1, phase=None, chew=0.0):
    """White goat with horns and beard, ~140*s long."""
    f = face
    fur, fur_d = hexc("#f4f1ea"), hexc("#d3cdbf")
    horn = hexc("#b89b6a")
    L, Hb = 140 * s, 64 * s
    by = y - 66 * s
    cv.poly([(x - f * L * 0.46, by - Hb * 0.3), (x - f * L * 0.62, by - Hb * 0.7), (x - f * L * 0.5, by - Hb * 0.1)],
            fill=fur_d)                                                    # tail
    _legs(cv, [x - f * L * 0.3, x + f * L * 0.2], by + Hb * 0.1, y, fur_d, 13 * s, phase)
    cv.ellipse(x - L * 0.5, by - Hb * 0.5, x + L * 0.5, by + Hb * 0.5, fill=fur)
    cv.ellipse(x - L * 0.12, by - Hb * 0.38, x + L * 0.3, by + Hb * 0.05, fill=hexc("#ffffff"))
    _legs(cv, [x - f * L * 0.36, x + f * L * 0.3], by + Hb * 0.15, y, fur, 14 * s, None if phase is None else phase + 1)
    # neck + head
    hx, hy = x + f * L * 0.5, by - Hb * 0.85
    cv.poly([(x + f * L * 0.25, by - Hb * 0.3), (hx - f * 8 * s, hy - 10 * s), (hx + f * 10 * s, hy + 18 * s),
             (x + f * L * 0.42, by + Hb * 0.2)], fill=fur)
    cv.ellipse(hx - 22 * s, hy - 22 * s, hx + 22 * s, hy + 24 * s, fill=fur)
    cv.poly([(hx, hy - 6 * s), (hx + f * 36 * s, hy + 14 * s), (hx + f * 30 * s, hy + 30 * s), (hx - f * 4 * s, hy + 22 * s)],
            fill=fur)                                                    # muzzle
    cv.circle(hx + f * 33 * s, hy + 18 * s, 4 * s, fill=INK)
    # horns: curved back from the top of the head
    for k, dxk in enumerate((0, 9)):
        pts = [(hx - f * (2 + dxk) * s, hy - 16 * s), (hx - f * (7 + dxk) * s, hy - 32 * s),
               (hx - f * (19 + dxk) * s, hy - 41 * s), (hx - f * (32 + dxk) * s, hy - 35 * s)]
        cv.line(pts, horn if k else _dk(horn, 0.12), 7 * s)
    # ear
    cv.poly([(hx - f * 10 * s, hy - 8 * s), (hx - f * 42 * s, hy + 2 * s), (hx - f * 12 * s, hy + 6 * s)], fill=fur_d)
    # eye
    cv.ellipse(hx + f * 4 * s, hy - 8 * s, hx + f * 16 * s, hy + 2 * s, fill=hexc("#ffffff"))
    cv.rect(hx + f * 7 * s - 3 * s, hy - 5 * s, hx + f * 7 * s + 5 * s, hy - 1 * s, fill=INK)
    # beard
    cv.poly([(hx + f * 12 * s, hy + 26 * s), (hx + f * 24 * s, hy + 26 * s), (hx + f * 16 * s, hy + 50 * s + chew * 4 * s)],
            fill=fur_d)


def draw_cabbage(cv, x, y, s=1.0, bite=0.0):
    """Cabbage head sitting on the ground at (x, y)."""
    r = 42 * s
    cy = y - r * 0.95
    g1, g2, g3 = hexc("#5a9e45"), hexc("#7bbf5a"), hexc("#b5e08a")
    for a in range(7):
        ang = math.pi * (0.95 + a * 0.18)
        cv.ellipse(x + math.cos(ang) * r * 0.75 - r * 0.55, cy + math.sin(ang) * r * 0.5 - r * 0.42,
                   x + math.cos(ang) * r * 0.75 + r * 0.55, cy + math.sin(ang) * r * 0.5 + r * 0.6, fill=g1)
    cv.circle(x, cy, r * 0.92, fill=g2)
    cv.circle(x + r * 0.08, cy - r * 0.12, r * 0.6, fill=g3)
    for a in (-0.6, 0.0, 0.6):
        cv.arc(x - r * 0.8 + a * r, cy - r * 0.5, x + r * 0.5 + a * r, cy + r * 0.9, 200, 300, g1, 3 * s)
    cv.ellipse(x - r * 0.95, y - r * 0.32, x + r * 0.95, y + r * 0.08, fill=g1)
    if bite > 0:
        cv.circle(x + r * 0.75, cy - r * 0.3, r * 0.35 * bite, fill=hexc("#000000", 0))


BOAT_W, BOAT_D = 330, 78


def draw_boat_back(cv, x, wy, t=0.0):
    """inner back wall of the boat (drawn before passengers)"""
    yb = wy + math.sin(t * 2.4) * 4
    cv.poly([(x - BOAT_W / 2 + 14, yb - BOAT_D + 6), (x + BOAT_W / 2 - 14, yb - BOAT_D + 6),
             (x + BOAT_W / 2 - 40, yb - 8), (x - BOAT_W / 2 + 40, yb - 8)], fill=hexc("#94603a"))
    return yb - 14          # floor level for passengers


def draw_boat_front(cv, x, wy, t=0.0, oar=None):
    """hull (front), drawn after passengers so their legs disappear behind it"""
    yb = wy + math.sin(t * 2.4) * 4
    wood, wood_d, rim = hexc("#c08a55"), hexc("#94603a"), hexc("#6e4528")
    hull = [(x - BOAT_W / 2, yb - BOAT_D + 20), (x + BOAT_W / 2, yb - BOAT_D + 20), (x + BOAT_W / 2 - 46, yb + 22),
            (x - BOAT_W / 2 + 46, yb + 22)]
    cv.poly(hull, fill=wood)
    for k in range(1, 3):
        yy = yb - BOAT_D + 20 + k * (BOAT_D + 2) / 3
        inset = 46 * k / 3
        cv.line([(x - BOAT_W / 2 + inset + 4, yy), (x + BOAT_W / 2 - inset - 4, yy)], wood_d, 4, cap=False)
    cv.rect(x - BOAT_W / 2 - 8, yb - BOAT_D + 12, x + BOAT_W / 2 + 8, yb - BOAT_D + 26, fill=rim, r=6)
    if oar is not None:     # oar angle in radians, pivot at the rim
        px, py = x + 20, yb - BOAT_D + 18
        ex, ey = px + math.cos(oar) * 190, py + math.sin(oar) * 190
        cv.line([(px, py), (ex, ey)], hexc("#e3c79a"), 9)
        cv.ellipse(ex - 16, ey - 9, ex + 16, ey + 9, fill=hexc("#e3c79a"))
        cv.circle(px, py, 8, fill=rim)


def draw_bulb(cv, x, y, s=1.0, state="off", t=0.0):
    """hanging light bulb, glass centre at (x, y). state: on | warm | cold | off"""
    r = 26 * s
    if state == "on":
        for k in range(6, 0, -1):
            cv.circle(x, y, r * (1 + k * 0.7), fill=(255, 214, 110, 16 + 6 * (6 - k)))
        for a in range(10):
            ang = a / 10 * 2 * math.pi + t * 0.4
            cv.line([(x + math.cos(ang) * r * 1.6, y + math.sin(ang) * r * 1.6),
                     (x + math.cos(ang) * r * 2.3, y + math.sin(ang) * r * 2.3)], hexc("#ffd34d"), 5 * s)
        glass, fil = hexc("#fff3b0"), hexc("#ff9f1c")
    elif state == "warm":
        for k in range(3, 0, -1):
            cv.circle(x, y, r * (1 + k * 0.35), fill=(255, 120, 60, 22))
        glass, fil = hexc("#ffd2b0"), hexc("#e8663b")
        for k in range(3):   # heat waves
            xx = x - r * 0.9 + k * r * 0.9
            pts = [(xx + 5 * s * math.sin((yy + t * 120) / (7 * s)), y - r * 1.4 - yy)
                   for yy in np.linspace(0, 34 * s, 9)]
            cv.line(pts, hexc("#ff7a3d", 200), 4 * s, cap=False)
    elif state == "cold":
        glass, fil = hexc("#dfeaf5"), hexc("#8a96a8")
    else:
        glass, fil = hexc("#e9edf2"), hexc("#8a96a8")
    cv.circle(x, y, r, fill=glass, outline=hexc("#9aa3b0"), width=2.5 * s)
    cv.rect(x - r * 0.42, y - r * 1.55, x + r * 0.42, y - r * 0.75, fill=glass)
    cv.line([(x - r * 0.3, y + r * 0.1), (x - r * 0.12, y - r * 0.35), (x + r * 0.12, y + r * 0.1),
             (x + r * 0.3, y - r * 0.35)], fil, 3 * s, cap=False)
    cv.rect(x - r * 0.5, y - r * 2.15, x + r * 0.5, y - r * 1.45, fill=hexc("#8f97a3"), r=3 * s)
    for k in range(3):
        cv.rect(x - r * 0.5, y - r * 2.0 + k * r * 0.2, x + r * 0.5, y - r * 1.93 + k * r * 0.2, fill=hexc("#6b7380"))
    cv.circle(x - r * 0.38, y - r * 0.3, r * 0.18, fill=(255, 255, 255, 170))


def draw_switch(cv, x, y, s=1.0, on=False, label=None, highlight=False):
    """single rocker switch centred at (x, y)"""
    w, h = 46 * s, 64 * s
    if highlight:
        cv.rect(x - w * 0.75, y - h * 0.75, x + w * 0.75, y + h * 0.75, fill=hexc("#ffd34d", 150), r=12 * s)
    cv.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=hexc("#ffffff"), outline=hexc("#c9ced6"), width=2 * s,
            r=7 * s)
    top = hexc("#e9edf2") if on else hexc("#ffffff")
    if on:
        cv.rect(x - w * 0.36, y - h * 0.38, x + w * 0.36, y + h * 0.05, fill=hexc("#d9dee5"), r=5 * s)
        cv.rect(x - w * 0.36, y + h * 0.05, x + w * 0.36, y + h * 0.38, fill=top, r=5 * s)
    else:
        cv.rect(x - w * 0.36, y - h * 0.38, x + w * 0.36, y - h * 0.05, fill=top, r=5 * s)
        cv.rect(x - w * 0.36, y - h * 0.05, x + w * 0.36, y + h * 0.38, fill=hexc("#d9dee5"), r=5 * s)
    cv.circle(x, y - h * 0.22, 4 * s, fill=hexc("#37b26c") if on else hexc("#b8bec8"))
    if label:
        cv.text(x, y - h * 0.85, label, 22 * s, INK)


def draw_tiger(cv, x, y, s=1.0, face=1, phase=None, roar=0.0, starved=False):
    """cartoon tiger, ~190*s long. roar 0..1 opens the mouth; starved = lying flat, grey, X eyes"""
    f = face
    if starved:
        fur, fur_d, belly, stripe = hexc("#b9a89a"), hexc("#9a8a7e"), hexc("#e6dfd6"), hexc("#7d7068")
    else:
        fur, fur_d, belly, stripe = hexc("#f08a2c"), hexc("#d46f1a"), hexc("#fbe6c8"), hexc("#2b1d14")
    L, Hb = 190 * s, 74 * s
    if starved:       # lying on its side
        by = y - 30 * s
        cv.ellipse(x - L * 0.5, by - Hb * 0.38, x + L * 0.5, by + Hb * 0.38, fill=fur)
        for k in range(5):
            xx = x - L * 0.3 + k * L * 0.14
            cv.line([(xx, by - Hb * 0.36), (xx + 8 * s, by - Hb * 0.05)], stripe, 7 * s, cap=False)
        for k in range(4):   # legs sticking out
            lx = x - L * 0.25 + k * L * 0.16
            cv.line([(lx, by + Hb * 0.2), (lx + 14 * s, by + Hb * 0.62)], fur_d, 13 * s)
        cv.poly([(x - f * L * 0.48, by), (x - f * L * 0.85, by + 10 * s), (x - f * L * 0.84, by + 20 * s),
                 (x - f * L * 0.48, by + 12 * s)], fill=fur_d)
        hx, hy = x + f * L * 0.55, by + 2 * s
        cv.circle(hx, hy, 34 * s, fill=fur)
        for dx in (-18, 16):
            cv.circle(hx + dx * s, hy - 28 * s, 10 * s, fill=fur_d)
        cv.ellipse(hx + f * 4 * s - 20 * s, hy + 2 * s, hx + f * 4 * s + 20 * s, hy + 26 * s, fill=belly)
        for ex in (hx - 12 * s, hx + 12 * s):     # X eyes
            cv.line([(ex - 6 * s, hy - 14 * s), (ex + 6 * s, hy - 2 * s)], INK, 4 * s)
            cv.line([(ex - 6 * s, hy - 2 * s), (ex + 6 * s, hy - 14 * s)], INK, 4 * s)
        cv.circle(hx + f * 4 * s, hy + 8 * s, 5 * s, fill=INK)
        cv.line([(hx + f * 4 * s, hy + 16 * s), (hx + f * 14 * s, hy + 24 * s)], hexc("#e98aa0"), 6 * s)  # tongue
        return
    by = y - 70 * s
    # tail
    cv.line([(x - f * L * 0.45, by - Hb * 0.1), (x - f * L * 0.7, by - Hb * 0.5), (x - f * L * 0.82, by - Hb * 0.9)],
            fur, 12 * s)
    cv.circle(x - f * L * 0.82, by - Hb * 0.9, 8 * s, fill=stripe)
    _legs(cv, [x - f * L * 0.3, x + f * L * 0.2], by + Hb * 0.1, y, fur_d, 20 * s, phase)
    cv.ellipse(x - L * 0.5, by - Hb * 0.5, x + L * 0.5, by + Hb * 0.5, fill=fur)
    cv.ellipse(x - L * 0.32, by + Hb * 0.02, x + L * 0.3, by + Hb * 0.5, fill=belly)
    for k in range(5):
        xx = x - L * 0.32 + k * L * 0.15
        cv.poly([(xx - 7 * s, by - Hb * 0.48), (xx + 7 * s, by - Hb * 0.48), (xx + 2 * s, by - Hb * 0.02)], fill=stripe)
    _legs(cv, [x - f * L * 0.36, x + f * L * 0.3], by + Hb * 0.15, y, fur, 21 * s, None if phase is None else phase + 1)
    # head
    hx, hy = x + f * L * 0.5, by - Hb * 0.55
    cv.circle(hx, hy, 40 * s, fill=fur)
    for dx in (-24, 20):
        cv.circle(hx + dx * s, hy - 34 * s, 12 * s, fill=fur)
        cv.circle(hx + dx * s, hy - 34 * s, 6 * s, fill=belly)
    for k in (-1, 1):
        cv.poly([(hx + k * 10 * s, hy - 40 * s), (hx + k * 4 * s, hy - 40 * s), (hx + k * 7 * s, hy - 24 * s)], fill=stripe)
    cv.ellipse(hx + f * 10 * s - 26 * s, hy + 2 * s, hx + f * 10 * s + 26 * s, hy + 30 * s, fill=belly)
    # angry eyes + brows
    for ex in (hx + f * 2 * s - 12 * s, hx + f * 2 * s + 14 * s):
        cv.ellipse(ex - 7 * s, hy - 12 * s, ex + 7 * s, hy, fill=hexc("#ffe46b"))
        cv.circle(ex + f * 2 * s, hy - 6 * s, 3.5 * s, fill=INK)
    cv.line([(hx + f * 2 * s - 22 * s, hy - 22 * s), (hx + f * 2 * s - 4 * s, hy - 14 * s)], INK, 4 * s)
    cv.line([(hx + f * 2 * s + 24 * s, hy - 22 * s), (hx + f * 2 * s + 6 * s, hy - 14 * s)], INK, 4 * s)
    cv.circle(hx + f * 12 * s, hy + 8 * s, 6 * s, fill=hexc("#e98aa0"))
    mo = 6 + 18 * roar
    cv.ellipse(hx + f * 12 * s - 16 * s, hy + 14 * s, hx + f * 12 * s + 16 * s, hy + (14 + mo) * s, fill=hexc("#6b1d1d"))
    for k in (-1, 1):   # fangs
        fx_ = hx + f * 12 * s + k * 8 * s
        cv.poly([(fx_ - 4 * s, hy + 14 * s), (fx_ + 4 * s, hy + 14 * s), (fx_, hy + (22 + roar * 6) * s)],
                fill=hexc("#ffffff"))
    for k in (-1, 1):   # whiskers
        cv.line([(hx + f * 22 * s, hy + 12 * s + k * 4 * s), (hx + f * 48 * s, hy + 8 * s + k * 10 * s)], INK, 2 * s)


def draw_pistol(cv, hand, face=1, s=1.0):
    """cartoon pistol held in the hand, pointing forward"""
    hx, hy = hand
    f = face
    cv.rect(min(hx, hx + f * 62 * s), hy - 18 * s, max(hx, hx + f * 62 * s), hy - 4 * s, fill=hexc("#3a3d46"), r=3 * s)
    cv.rect(min(hx - f * 6 * s, hx + f * 14 * s), hy - 18 * s, max(hx - f * 6 * s, hx + f * 14 * s), hy + 22 * s,
            fill=hexc("#2a2c33"), r=4 * s)
    cv.rect(min(hx + f * 50 * s, hx + f * 62 * s), hy - 22 * s, max(hx + f * 50 * s, hx + f * 62 * s), hy - 18 * s,
            fill=hexc("#2a2c33"))


def draw_crutch(cv, top, bottom, s=1.0):
    cv.line([top, bottom], hexc("#c9ced6"), 9 * s, cap=False)
    cv.line([(top[0] - 20 * s, top[1]), (top[0] + 20 * s, top[1])], hexc("#5d6270"), 12 * s)
    mid = (top[0] + (bottom[0] - top[0]) * 0.35, top[1] + (bottom[1] - top[1]) * 0.35)
    cv.line([(mid[0] - 10 * s, mid[1]), (mid[0] + 10 * s, mid[1])], hexc("#5d6270"), 8 * s)
    cv.rect(bottom[0] - 8 * s, bottom[1] - 10 * s, bottom[0] + 8 * s, bottom[1], fill=hexc("#22243a"), r=3 * s)


def draw_saber(cv, hand, face=1, s=1.0, ang=-1.0):
    """curved pirate saber; ang = blade direction (radians, 0 = forward)"""
    f = face
    hx, hy = hand
    pts = []
    for k in range(9):
        q = k / 8
        a = ang + 0.5 * q * q
        pts.append((hx + f * math.cos(a) * 150 * s * q, hy + math.sin(a) * 150 * s * q - 30 * s * math.sin(math.pi * q) * 0))
    cv.line(pts, hexc("#dfe5ec"), 12 * s)
    cv.line(pts, hexc("#ffffff"), 3 * s, cap=False)
    cv.arc(hx - 20 * s, hy - 14 * s, hx + 20 * s, hy + 18 * s, 0, 360, hexc("#d9a441"), 5 * s)


def draw_pirate_extras(cv, x, y, st, h, face=1):
    """tricorn hat + eye patch for a person drawn with draw_person at (x, y)"""
    f = face
    head_r = st.head * h
    sh_y = y - (st.leg + st.torso) * h
    head_y = sh_y - 0.03 * h - head_r * 0.92
    hx = x + f * head_r * 0.08
    cv.poly([(hx - head_r * 1.5, head_y - head_r * 0.55), (hx + head_r * 1.5, head_y - head_r * 0.55),
             (hx + head_r * 0.9, head_y - head_r * 1.55), (hx, head_y - head_r * 1.2), (hx - head_r * 0.9, head_y - head_r * 1.55)],
            fill=hexc("#1d1a24"))
    cv.line([(hx - head_r * 1.4, head_y - head_r * 0.62), (hx + head_r * 1.4, head_y - head_r * 0.62)], hexc("#d9a441"),
            head_r * 0.12)
    cv.circle(hx, head_y - head_r * 1.0, head_r * 0.2, fill=hexc("#f4f1ea"))
    fx_ = hx + f * head_r * 0.32
    ex = fx_ + f * head_r * 0.30
    eye_y = head_y + head_r * 0.02
    cv.line([(hx - head_r * 0.9, head_y - head_r * 0.45), (ex + f * head_r * 0.2, eye_y - head_r * 0.1)],
            hexc("#1d1a24"), head_r * 0.07)
    cv.ellipse(ex - head_r * 0.2, eye_y - head_r * 0.2, ex + head_r * 0.2, eye_y + head_r * 0.2, fill=hexc("#1d1a24"))
