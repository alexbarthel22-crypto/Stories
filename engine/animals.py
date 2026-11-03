"""Flat-vector animals and props in the channel style (world coordinates, feet/ground at y)."""
import math
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
