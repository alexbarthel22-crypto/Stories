"""Rätsel #6 – Das Rätsel der Sphinx (Morgen vier, Mittag zwei, Abend drei Beine).

2.5D look: four parallax depth layers (far / mid / main / foreground) with baked volume shading,
time-of-day sky with god rays and stars, heat haze, bloom, depth-of-field blur and camera drift.

usage:  python3 make_video.py            -> renders video.mp4 (needs timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from toolkit import _shade
from animals import draw_baby, draw_cane

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

W, H = OUT_W, OUT_H
WX0, WY0, WX1, WY1 = -420, -520, 1520, 2560
HORIZON = 1060
PATH_Y = 1440
REF = (540.0, 1000.0, 1920.0)            # camera where all layers line up exactly
GOLD, LAPIS = "#e0b64a", "#2f5aa8"

ADULT = Style(205, "#c98c62", "#1d1712", "#2f8f83", "#e9e0cc", hair_style="quiff", shoes="#7a4f2e",
              accent="#1f5f57", under="#f4efe4")
OLD = Style(205, "#e9b48f", "#e6e6e6", "#7a5c3a", "#4a4a5a", hair_style="short", beard=True, glasses=True,
            shoes="#3a2c22", accent="#5a4228")

# sky stops (top, middle, horizon), sun colour, landscape tint rgba, star amount
PALETTES = {
    "golden":  (("#3d4f9a", "#e8916a", "#ffd08a"), "#ffe2a0", (255, 170, 90, 22), 0.0),
    "morning": (("#7d9fdc", "#f4aab0", "#ffe0b0"), "#fff0c8", (255, 190, 200, 26), 0.0),
    "noon":    (("#2f86d6", "#7ec4ee", "#dff2fb"), "#fffbe6", (255, 255, 255, 0), 0.0),
    "evening": (("#1d1640", "#a8476a", "#ff9a4a"), "#ffb36b", (110, 50, 140, 58), 0.45),
    "night":   (("#060a24", "#141c48", "#2e3566"), "#f4f1d0", (30, 40, 110, 120), 1.0),
}


def _pal_mix(a, b, f):
    (sa, suna, ta, na), (sb, sunb, tb, nb) = PALETTES[a], PALETTES[b]
    stops = tuple(mix(hexc(x), hexc(y), f) for x, y in zip(sa, sb))
    sun = mix(hexc(suna), hexc(sunb), f)
    tint = tuple(int(round(p + (q - p) * f)) for p, q in zip(ta, tb))
    return stops, sun, tint, na + (nb - na) * f


class BCanvas(Canvas):
    """Canvas that alpha-blends semi-transparent shapes on RGBA images (PIL would replace the pixels)"""

    def _blend(self, name, pts, pad, *a, **kw):
        col = kw.get("fill") if kw.get("fill") is not None else kw.get("outline")
        if col is None and len(a) and isinstance(a[-1], tuple):
            col = a[-1]
        if self.img.mode != "RGBA" or col is None or len(col) < 4 or col[3] >= 255:
            return getattr(Canvas, name)(self, *a, **kw)
        q = [self.p(*p) for p in pts]
        pd = pad * self.s + 3
        x0 = max(0, int(min(p[0] for p in q) - pd)); y0 = max(0, int(min(p[1] for p in q) - pd))
        x1 = min(self.img.width, int(max(p[0] for p in q) + pd) + 1)
        y1 = min(self.img.height, int(max(p[1] for p in q) + pd) + 1)
        if x1 <= x0 or y1 <= y0:
            return
        ov = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        getattr(Canvas, name)(Canvas(ov, self.ox + x0 / self.s, self.oy + y0 / self.s, self.s), *a, **kw)
        self.img.alpha_composite(ov, (x0, y0))

    def rect(self, x0, y0, x1, y1, **kw):
        self._blend("rect", [(x0, y0), (x1, y1)], kw.get("width", 1), x0, y0, x1, y1, **kw)

    def circle(self, x, y, r, **kw):
        self._blend("circle", [(x - r, y - r), (x + r, y + r)], kw.get("width", 1), x, y, r, **kw)

    def ellipse(self, x0, y0, x1, y1, **kw):
        self._blend("ellipse", [(x0, y0), (x1, y1)], kw.get("width", 1), x0, y0, x1, y1, **kw)

    def line(self, pts, fill, width=1, joint="curve", cap=True):
        self._blend("line", pts, width, pts, fill, width, joint, cap)

    def poly(self, pts, **kw):
        self._blend("poly", pts, kw.get("width", 1), pts, **kw)

    def pieslice(self, x0, y0, x1, y1, a0, a1, fill):
        self._blend("pieslice", [(x0, y0), (x1, y1)], 1, x0, y0, x1, y1, a0, a1, fill)

    def arc(self, x0, y0, x1, y1, a0, a1, fill, width=1):
        self._blend("arc", [(x0, y0), (x1, y1)], width, x0, y0, x1, y1, a0, a1, fill, width)


# ------------------------------------------------------------------ volume shading (baked "3D")
def fblur(a, sigma):
    """float gaussian approximation (3 box blurs, no 8-bit banding)"""
    r = max(1, int(sigma * 0.9))
    for ax in (0, 1):
        for _ in range(3):
            pad = [(0, 0), (0, 0)]
            pad[ax] = (r + 1, r)
            c = np.cumsum(np.pad(a, pad, mode="edge"), axis=ax, dtype=np.float64)
            a = ((np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) -
                  np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)).astype(np.float32)
    return a


def shaded_part(bbox, draw_fn, z, soft=16, k=1.4, ao=0.28, light=(-0.55, -0.83), spec=0.0):
    """draws a part on its own layer and lights it like a rounded 3D body (height = blurred alpha)"""
    x0, y0, x1, y1 = bbox
    im = Image.new("RGBA", (int((x1 - x0) * z), int((y1 - y0) * z)), (0, 0, 0, 0))
    draw_fn(BCanvas(im, x0, y0, z))
    h = fblur(np.asarray(im.split()[3], np.float32) / 255, soft * z)
    gy, gx = np.gradient(h)
    sh = -(gx * light[0] + gy * light[1]) * soft * z * k
    f = 1 + np.clip(sh, -0.45, 0.45)
    f *= 1 - ao * np.clip(1 - h * 1.6, 0, 1)
    rgb = np.asarray(im, np.float32).copy()
    rgb[..., :3] *= f[..., None]
    if spec:
        hl = np.clip(sh - 0.25, 0, 1) * spec * 255
        rgb[..., :3] += hl[..., None]
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGBA")
    return im, (x0, y0)


def paste_part(layer_img, z, part):
    im, (x0, y0) = part
    layer_img.alpha_composite(im, (int(round((x0 - WX0) * z)), int(round((y0 - WY0) * z))))


def vgrad_poly(cv, pts, c_top, c_bot, y0, y1):
    """polygon filled with a vertical gradient"""
    mask = Image.new("L", cv.img.size, 0)
    ImageDraw.Draw(mask).polygon([cv.p(*p) for p in pts], fill=255)
    a, b = cv.p(0, y0)[1], cv.p(0, y1)[1]
    ys = np.clip((np.arange(cv.img.size[1]) - a) / max(1, b - a), 0, 1)
    g = np.zeros((cv.img.size[1], 1, 3), np.float32)
    for c in range(3):
        g[:, 0, c] = c_top[c] + (c_bot[c] - c_top[c]) * ys
    grad = Image.fromarray(np.repeat(g, cv.img.size[0], axis=1).astype(np.uint8), "RGB").convert("RGBA")
    cv.img.paste(grad, (0, 0), mask)


# ------------------------------------------------------------------ layer: FAR (pyramids, dunes)
def draw_pyramid(cv, apex, x0, x1, base, seed):
    split = x0 + (x1 - x0) * 0.62
    vgrad_poly(cv, [apex, (x0, base), (split, base)], hexc("#fbe2a6"), hexc("#d9a862"), apex[1], base)
    vgrad_poly(cv, [apex, (split, base), (x1, base)], hexc("#c99350"), hexc("#94622f"), apex[1], base)
    rng = np.random.default_rng(seed)
    n = 14
    for k in range(1, n):
        y = apex[1] + (base - apex[1]) * k / n
        f = (y - apex[1]) / (base - apex[1])
        xl, xr = apex[0] + (x0 - apex[0]) * f, apex[0] + (x1 - apex[0]) * f
        xs = apex[0] + (split - apex[0]) * f
        cv.line([(xl, y), (xs, y)], (150, 100, 50, 90), 2, cap=False)
        cv.line([(xs, y), (xr, y)], (70, 40, 20, 90), 2, cap=False)
        for _ in range(int(6 * f) + 1):      # block joints
            xx = rng.uniform(xl + 6, xr - 6)
            yy0 = y - (base - apex[1]) / n
            cv.line([(xx, yy0 + 2), (xx, y - 2)], (90, 55, 25, 70), 2, cap=False)
    for _ in range(60):                      # weathering speckles
        f = rng.uniform(0.15, 1)
        y = apex[1] + (base - apex[1]) * f
        xl, xr = apex[0] + (x0 - apex[0]) * f, apex[0] + (x1 - apex[0]) * f
        cv.circle(rng.uniform(xl + 8, xr - 8), y, rng.uniform(2, 5), fill=(90, 55, 25, 60))
    cap = 0.085
    cv.poly([apex, (apex[0] - (apex[0] - x0) * cap, apex[1] + (base - apex[1]) * cap),
             (apex[0] + (split - apex[0]) * cap, apex[1] + (base - apex[1]) * cap)], fill=hexc("#ffe27a"))
    cv.poly([apex, (apex[0] + (split - apex[0]) * cap, apex[1] + (base - apex[1]) * cap),
             (apex[0] + (x1 - apex[0]) * cap, apex[1] + (base - apex[1]) * cap)], fill=hexc("#c99a2e"))
    cv.ellipse(x0 - 30, base - 14, x1 + 40, base + 16, fill=(110, 70, 30, 70))   # contact shadow


def new_layer(z):
    img = Image.new("RGBA", (int((WX1 - WX0) * z), int((WY1 - WY0) * z)), (0, 0, 0, 0))
    return img, BCanvas(img, WX0, WY0, z)


def draw_far(z):
    img, cv = new_layer(z)
    pts = [(x, HORIZON - 70 - 40 * math.sin(x / 260 + 1) - 16 * math.sin(x / 90)) for x in range(WX0, WX1 + 20, 20)]
    vgrad_poly(cv, pts + [(WX1, HORIZON + 120), (WX0, HORIZON + 120)], hexc("#e9b978"), hexc("#d29a55"), HORIZON - 130,
               HORIZON)
    draw_pyramid(cv, (1300, 870), 1170, 1440, HORIZON + 8, 3)
    draw_pyramid(cv, (1040, 770), 850, 1230, HORIZON + 8, 2)
    draw_pyramid(cv, (640, 590), 290, 990, HORIZON + 10, 1)
    draw_pyramid(cv, (-210, 900), -330, -70, HORIZON + 8, 4)
    pts = [(x, HORIZON - 22 - 14 * math.sin(x / 150) - 6 * math.sin(x / 47)) for x in range(WX0, WX1 + 20, 20)]
    vgrad_poly(cv, pts + [(WX1, HORIZON + 120), (WX0, HORIZON + 120)], hexc("#e7b46d"), hexc("#d9a35e"), HORIZON - 40,
               HORIZON + 40)
    return img.filter(ImageFilter.GaussianBlur(0.9 * z))


# ------------------------------------------------------------------ layer: MID (ground, Nile, obelisks, ruins)
def draw_obelisk(cv, x, top, base):
    vgrad_poly(cv, [(x - 18, base), (x, base), (x, top + 30), (x - 12, top + 30)], hexc("#f0cf91"), hexc("#d6aa66"),
               top, base)
    vgrad_poly(cv, [(x, base), (x + 18, base), (x + 12, top + 30), (x, top + 30)], hexc("#c49a5c"), hexc("#a3793f"),
               top, base)
    cv.poly([(x - 12, top + 30), (x, top + 30), (x, top)], fill=hexc("#ffe27a"))
    cv.poly([(x, top + 30), (x + 12, top + 30), (x, top)], fill=hexc("#c99a2e"))
    for k in range(6):
        y = top + 60 + k * 34
        cv.line([(x - 9, y), (x - 3, y + 10)], (110, 70, 35, 160), 2)
        cv.circle(x - 7, y + 20, 3, fill=(110, 70, 35, 160))
    cv.ellipse(x - 40, base - 8, x + 60, base + 10, fill=(110, 70, 30, 80))


def draw_mid(z):
    img, cv = new_layer(z)
    vgrad_poly(cv, [(WX0, HORIZON), (WX1, HORIZON), (WX1, WY1), (WX0, WY1)], hexc("#d9a35e"), hexc("#f0c27c"), HORIZON,
               1500)
    rng = np.random.default_rng(7)
    for k in range(9):
        y = HORIZON + 26 + k * k * 9
        pts = [(x, y + (5 + k * 2) * math.sin(x / (90 + k * 25) + k * 1.7)) for x in range(WX0, WX1 + 20, 20)]
        cv.line(pts, (190, 130, 70, 70), 3 + k * 0.6, cap=False)
    pts_top = [(x, HORIZON + 40 + 6 * math.sin(x / 140)) for x in range(WX0, WX1 + 20, 20)]
    pts_bot = [(x, HORIZON + 86 + 8 * math.sin(x / 120 + 1)) for x in range(WX1, WX0 - 20, -20)]
    cv.poly([(x, y - 6) for x, y in pts_top] + [(x, y + 8) for x, y in pts_bot], fill=hexc("#5e9a4c"))
    vgrad_poly(cv, pts_top + pts_bot, hexc("#2d6fae"), hexc("#4f9ad4"), HORIZON + 40, HORIZON + 90)
    for _ in range(90):
        x = rng.uniform(WX0, WX1)
        y = HORIZON + (38 if rng.random() < 0.5 else 92) + rng.uniform(-3, 3)
        cv.line([(x, y), (x + rng.uniform(-4, 4), y - rng.uniform(10, 26))], hexc("#4f8a3c"), 3)
    draw_obelisk(cv, 1010, 880, 1190)
    draw_obelisk(cv, 1090, 940, 1190)
    for x, hgt in ((1180, 210), (1260, 140), (1340, 240), (1420, 90)):     # temple ruins
        cv.rect(x - 22, 1200 - hgt, x + 22, 1200, fill=hexc("#e8c48a"))
        cv.rect(x + 6, 1200 - hgt, x + 22, 1200, fill=hexc("#c79d62"))
        cv.rect(x - 30, 1200 - hgt - 12, x + 30, 1200 - hgt, fill=hexc("#d8b071"))
    cv.ellipse(1140, 1188, 1460, 1214, fill=(110, 70, 30, 80))
    return img


# ------------------------------------------------------------------ layer: MAIN (sphinx, plinth, near ground)
SPHINX_BBOX = (-200, 780, 760, 1360)
GLYPHS = [(x, 1290) for x in range(-30, 650, 85)]


def draw_glyph(cv, x, y, kind, col):
    if kind == 0:
        cv.ellipse(x - 18, y - 11, x + 18, y + 11, outline=col, width=4)
        cv.circle(x, y, 5, fill=col)
    elif kind == 1:
        cv.line([(x - 16, y + 12), (x, y - 14), (x + 16, y + 12)], col, 4)
    elif kind == 2:
        cv.circle(x, y - 6, 9, outline=col, width=4)
        cv.line([(x, y + 3), (x, y + 18)], col, 4)
        cv.line([(x - 9, y + 8), (x + 9, y + 8)], col, 4)
    else:
        cv.line([(x - 16, y - 8), (x - 4, y + 10), (x + 6, y - 6), (x + 16, y + 10)], col, 4)


def sphinx_parts(z):
    BODY, BODY_D = hexc("#c98a45"), hexc("#a96d33")
    bb = SPHINX_BBOX
    hx, hy = 470, 985
    parts = [shaded_part(bb, lambda cv: cv.line([(-30, 1190), (-110, 1150), (-125, 1100), (-95, 1078)], BODY_D, 18),
                         z, soft=5)]

    def body(cv):
        cv.ellipse(-70, 1066, 270, 1232, fill=BODY)
        cv.rect(40, 1092, 480, 1230, fill=BODY, r=56)
    parts.append(shaded_part(bb, body, z, soft=30, k=1.6))
    parts.append(shaded_part(bb, lambda cv: cv.ellipse(-60, 1120, 200, 1232, fill=BODY_D), z, soft=16))
    parts.append(shaded_part(bb, lambda cv: cv.rect(60, 1192, 260, 1230, fill=BODY_D, r=17), z, soft=8))
    parts.append(shaded_part(bb, lambda cv: cv.rect(360, 1036, 545, 1230, fill=BODY, r=44), z, soft=24))
    parts.append(shaded_part(bb, lambda cv: cv.rect(420, 1178, 700, 1214, fill=BODY_D, r=17), z, soft=8))
    parts.append(shaded_part(bb, lambda cv: cv.rect(400, 1196, 676, 1232, fill=BODY, r=17), z, soft=8, spec=0.4))

    def nemes(cv):
        cv.poly([(hx - 76, hy - 70), (hx + 76, hy - 70), (hx + 114, hy + 110), (hx + 114, hy + 150),
                 (hx - 114, hy + 150), (hx - 114, hy + 110)], fill=hexc(GOLD))
        cv.pieslice(hx - 80, hy - 152, hx + 80, hy - 8, 180, 360, fill=hexc(GOLD))
        for k in range(7):
            y = hy - 40 + k * 26
            f = (y - (hy - 70)) / 180
            xo = 76 + (114 - 76) * min(1, f)
            cv.line([(hx - xo + 2, y), (hx - 50, y)], hexc(LAPIS), 11, cap=False)
            cv.line([(hx + 50, y), (hx + xo - 2, y)], hexc(LAPIS), 11, cap=False)
        for k in range(1, 4):
            cv.arc(hx - 80 + k * 6, hy - 152 + k * 12, hx + 80 - k * 6, hy - 8, 200, 340, hexc(LAPIS), 9)
    parts.append(shaded_part(bb, nemes, z, soft=22, k=1.5, spec=0.5))
    parts.append(shaded_part(bb, lambda cv: cv.ellipse(hx - 54, hy - 84, hx + 54, hy + 66, fill=hexc("#dca765")), z,
                             soft=20, k=1.6, spec=0.35))

    def details(cv):
        cv.rect(hx - 64, hy - 88, hx + 64, hy - 72, fill=hexc(LAPIS), r=6)
        cv.poly([(hx - 7, hy - 104), (hx + 7, hy - 104), (hx + 10, hy - 76), (hx - 10, hy - 76)], fill=hexc(GOLD))
        cv.circle(hx, hy - 108, 8, fill=hexc(GOLD))
        for ex in (hx - 23, hx + 23):
            cv.line([(ex - 17, hy - 30), (ex + 15, hy - 33)], hexc("#3a2a1e"), 6)
            cv.ellipse(ex - 14, hy - 20, ex + 14, hy - 5, fill=hexc("#f6efe2"))
            cv.circle(ex + 1, hy - 12, 6, fill=hexc("#22243a"))
            cv.circle(ex + 3, hy - 14, 2, fill=hexc("#ffffff"))
            tail = ex + 24 if ex > hx else ex - 24
            cv.line([(ex - 14 if ex > hx else ex + 14, hy - 12), (tail, hy - 16)], hexc("#22243a"), 4, cap=False)
        cv.poly([(hx - 6, hy - 6), (hx + 6, hy - 6), (hx + 12, hy + 20), (hx - 12, hy + 20)], fill=hexc("#c58f4f"))
        cv.ellipse(hx - 20, hy + 30, hx + 20, hy + 42, fill=hexc("#9c5634"))
        cv.rect(hx - 13, hy + 62, hx + 13, hy + 118, fill=hexc(GOLD), r=6)
        for k in range(4):
            cv.rect(hx - 11, hy + 70 + k * 12, hx + 11, hy + 75 + k * 12, fill=hexc(LAPIS))
        for k in range(4):
            cv.arc(180 + k * 50, 1118, 230 + k * 50, 1200, 200, 300, (110, 69, 36, 150), 3)
        for dy, x1 in ((0, 700), (18, 676)):
            for j in range(3):
                cv.line([(x1 - 34 + j * 11, 1184 + dy), (x1 - 34 + j * 11, 1208 + dy)], (110, 69, 36, 200), 3, cap=False)
        for k in range(14):
            rng = np.random.default_rng(k)
            x, y = rng.uniform(0, 470), rng.uniform(1100, 1220)
            cv.line([(x, y), (x + rng.uniform(-14, 14), y + rng.uniform(6, 18))], (110, 69, 36, 110), 2)
    parts.append(shaded_part(bb, details, z, soft=2, k=0.6, ao=0.0))
    return parts


def draw_main(z):
    img, cv = new_layer(z)
    lip = [(x, 1286 + 14 * math.sin(x / 210 + 0.6) + 6 * math.sin(x / 63)) for x in range(WX0, WX1 + 20, 20)]
    vgrad_poly(cv, lip + [(WX1, WY1), (WX0, WY1)], hexc("#efc581"), hexc("#e2ae66"), 1280, 2100)
    cv.line(lip, (255, 236, 196, 170), 5, cap=False)
    sh, scv = new_layer(z)
    scv.poly([(-90, 1336), (700, 1336), (900, 1400), (-40, 1400)], fill=(90, 50, 25, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14 * z)))
    # plinth as a 3D block
    vgrad_poly(cv, [(-90, 1246), (690, 1246), (690, 1338), (-90, 1338)], hexc("#c48d4e"), hexc("#a26c34"), 1246, 1338)
    cv.poly([(-90, 1246), (-70, 1226), (710, 1226), (690, 1246)], fill=hexc("#e0b06e"))
    cv.poly([(690, 1246), (710, 1226), (710, 1318), (690, 1338)], fill=hexc("#8e5d2c"))
    for x in range(-90, 690, 98):
        cv.line([(x, 1248), (x, 1336)], (110, 69, 36, 140), 3, cap=False)
    cv.line([(-90, 1268), (690, 1268)], (110, 69, 36, 110), 2, cap=False)
    for i, (x, y) in enumerate(GLYPHS):
        draw_glyph(cv, x + 40, y + 6, i % 4, (110, 69, 36, 210))
    for part in sphinx_parts(z):
        paste_part(img, z, part)
    pts = [(x, PATH_Y - 34 + 10 * math.sin(x / 160)) for x in range(WX0, WX1 + 20, 20)]
    vgrad_poly(cv, pts + [(WX1, PATH_Y + 64), (WX0, PATH_Y + 64)], hexc("#f7dca4"), hexc("#efcb8a"), PATH_Y - 40,
               PATH_Y + 64)
    for x in range(-400, 1520, 105):
        y = PATH_Y + 44 + (x % 3) * 6
        cv.ellipse(x, y, x + 78, y + 24, fill=hexc("#dcb06d"))
        cv.ellipse(x + 6, y - 2, x + 70, y + 14, fill=hexc("#ebc786"))
    rng = np.random.default_rng(6)
    for _ in range(70):
        x, y = rng.uniform(WX0, WX1), rng.uniform(PATH_Y + 100, WY1 - 40)
        r = rng.uniform(6, 22) * (0.6 + (y - PATH_Y) / 900)
        cv.ellipse(x - r * 1.2, y + r * 0.2, x + r * 1.4, y + r * 0.8, fill=(120, 75, 35, 70))
        cv.ellipse(x - r, y - r * 0.6, x + r, y + r * 0.6, fill=hexc("#c48a45"))
        cv.ellipse(x - r * 0.7, y - r * 0.6, x + r * 0.5, y + r * 0.1, fill=hexc("#dfac68"))
    return img


# ------------------------------------------------------------------ layer: FOREGROUND (columns, big rocks)
COLS = (-170, 1250)


def draw_fg(z):
    img, cv = new_layer(z)
    for cx in COLS:
        w, top, bot = 150, 250, 1900
        n = 30
        for i in range(n):                         # cylindrical shading
            a = -math.pi / 2 + math.pi * (i + 0.5) / n
            lit = 0.55 + 0.45 * max(0, math.cos(a + 0.6))
            c = tuple(int(v * lit) for v in hexc("#f0cd92"))
            x0 = cx - w / 2 + w * i / n
            cv.rect(x0, top + 70, x0 + w / n + 1, bot, fill=c)
        for k in range(4):
            y = top + 140 + k * 26
            for i in range(n):
                a = -math.pi / 2 + math.pi * (i + 0.5) / n
                lit = 0.55 + 0.45 * max(0, math.cos(a + 0.6))
                c = tuple(int(v * lit) for v in hexc([LAPIS, "#c0392b", GOLD, "#3f8a4c"][k]))
                x0 = cx - w / 2 + w * i / n
                cv.rect(x0, y, x0 + w / n + 1, y + 12, fill=c)
        cv.poly([(cx - w * 0.8, top + 70), (cx + w * 0.8, top + 70), (cx + w * 0.62, top), (cx - w * 0.62, top)],
                fill=hexc("#d6a862"))
        for k in range(-3, 4):
            cv.line([(cx + k * w * 0.2, top + 68), (cx + k * w * 0.14, top + 4)], (130, 85, 40, 140), 4)
        for r in range(9):
            draw_glyph(cv, cx + (r % 2) * 14 - 7, top + 280 + r * 92, r % 4, (110, 69, 36, 200))
        tx = cx + (w / 2 + 16 if cx < 540 else -w / 2 - 16)
        cv.rect(tx - 8, 760, tx + 8, 840, fill=hexc("#5a3a20"))
        cv.poly([(tx - 22, 740), (tx + 22, 740), (tx + 10, 770), (tx - 10, 770)], fill=hexc("#8a5a2c"))
    cv.rect(-420, 200, 20, 252, fill=hexc("#d8b071"))
    cv.rect(1060, 200, 1520, 252, fill=hexc("#d8b071"))
    for x0 in (-420, 1060):                            # lintel with winged sun
        cx = x0 + 220
        cv.line([(cx - 120, 226), (cx - 20, 226)], hexc(LAPIS), 10)
        cv.line([(cx + 20, 226), (cx + 120, 226)], hexc(LAPIS), 10)
        cv.circle(cx, 226, 18, fill=hexc(GOLD))
    for x, y, r in ((-150, 2000, 160), (60, 2120, 120), (1150, 2050, 170), (920, 2160, 110)):
        cv.ellipse(x - r * 1.2, y - r * 0.55, x + r * 1.2, y + r * 0.6, fill=hexc("#b07a3c"))
        cv.ellipse(x - r, y - r * 0.6, x + r * 0.8, y + r * 0.2, fill=hexc("#cf9b55"))
    return img.filter(ImageFilter.GaussianBlur(2.2 * z))


LAYERS = [("far", 0.45, 1, draw_far), ("mid", 0.78, 2, draw_mid), ("main", 1.0, 2, draw_main), ("fg", 1.35, 1, draw_fg)]
_L = {}


def layer(name):
    if name not in _L:
        nm, f, z, fn = next(x for x in LAYERS if x[0] == name)
        p = os.path.join(CACHE, f"layer_{name}.png")
        if not os.path.exists(p):
            fn(z).save(p)
        _L[name] = Image.open(p).convert("RGBA")
    return _L[name]


def layer_box(cam, f):
    cx, cy, vh = cam
    lx = REF[0] + (cx - REF[0]) * f
    ly = REF[1] + (cy - REF[1]) * f
    lv = min(REF[2] + (vh - REF[2]) * f, WY1 - WY0)
    lw = lv * OUT_W / OUT_H
    lx = clamp(lx, WX0 + lw / 2, WX1 - lw / 2)
    ly = clamp(ly, WY0 + lv / 2, WY1 - lv / 2)
    return (lx - lw / 2, ly - lv / 2, lx + lw / 2, ly + lv / 2)


def w2s(x, y, box):
    k = (box[3] - box[1]) / OUT_H
    return (x - box[0]) / k, (y - box[1]) / k


_VIG = None


def post_fx(frame):
    global _VIG
    small = frame.resize((OUT_W // 8, OUT_H // 8), Image.BILINEAR)
    bright = small.point(lambda v: max(0, v - 205) * 3)
    bloom = bright.filter(ImageFilter.GaussianBlur(5)).resize(frame.size, Image.BILINEAR)
    frame = ImageChops.add(frame, bloom.point(lambda v: int(v * 0.3)))
    frame = ImageEnhance.Color(frame).enhance(1.08)
    frame = ImageEnhance.Contrast(frame).enhance(1.04)
    if _VIG is None:
        _VIG = Image.fromarray((vignette(frame, 0.32)[..., 0] * 255).astype(np.uint8), "L")
    return Image.composite(frame, Image.new("RGB", frame.size, (20, 10, 30)), _VIG)


def render_scene(cam, t, pal, actors=None, haze=True):
    """actors: dict layer_name -> fn(cv, box) drawing animated things on that depth layer"""
    actors = actors or {}
    stops, sun, tint, stars = pal
    sb = layer_box(cam, 0.2)                     # sky at half resolution, parallax 0.2
    sw, shh = OUT_W // 2, OUT_H // 2
    ys = sb[1] + (np.arange(shh) + 0.5) * (sb[3] - sb[1]) / shh
    u = np.clip((ys - (WY0 + 300)) / (HORIZON - (WY0 + 300)), 0, 1)
    col = np.stack([np.interp(u, [0, 0.55, 1], [stops[0][c], stops[1][c], stops[2][c]]) for c in range(3)], 1)
    sky = Image.fromarray(np.repeat(col[:, None, :], sw, axis=1).astype(np.uint8), "RGB").convert("RGBA")
    sky_actors(BCanvas(sky, sb[0], sb[1], shh / (sb[3] - sb[1])), t, sun, stars)
    frame = sky.resize((OUT_W, OUT_H), Image.BILINEAR)
    boxes = {}
    for name, f, z, _ in LAYERS:
        box = layer_box(cam, f)
        boxes[name] = box
        pb = (int(round((box[0] - WX0) * z)), int(round((box[1] - WY0) * z)),
              int(round((box[2] - WX0) * z)), int(round((box[3] - WY0) * z)))
        crop = layer(name).crop(pb)
        if name in actors:
            actors[name](BCanvas(crop, box[0], box[1], z), box)
        im = crop.resize((OUT_W, OUT_H), Image.BILINEAR if z == 1 else Image.LANCZOS)
        if name == "far":                        # aerial perspective
            hz = Image.new("RGBA", im.size, tuple(stops[2]) + (255,))
            hz.putalpha(im.split()[3].point(lambda v: int(v * 0.28)))
            im.alpha_composite(hz)
        frame.alpha_composite(im)
    frame = frame.convert("RGB")
    if tint[3] > 0:
        frame = Image.blend(frame, Image.new("RGB", frame.size, tint[:3]), tint[3] / 255)
    if haze:                                     # heat shimmer around the horizon
        hy = int(w2s(0, HORIZON, boxes["mid"])[1])
        a = np.asarray(frame).copy()
        for y in range(max(0, hy - 70), min(OUT_H, hy + 40)):
            s = int(round(2.4 * math.sin(y * 0.21 + t * 7) * (1 - abs(y - hy) / 70)))
            if s:
                a[y] = np.roll(a[y], s, axis=0)
        frame = Image.fromarray(a)
    return post_fx(frame), boxes


# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["WARTE", "Im alten", "Wer vorbei", "Was geht", "PAUSE", "Kleiner Tipp", "Schreib deine", "Hier kommt",
        "Es ist der", "Am Morgen", "Am Mittag", "Und am Abend", "Hättest", "Schreib's"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 2.4
XFADE = 0.3


def st(key):
    return S[K[key]]


def en(key):
    return E[K[key]]


def word_time(key, word, frac=0.5):
    seg = next(x for x in TIM if x["text"].startswith(key))
    i = seg["text"].find(word)
    f = (i + len(word) * frac) / len(seg["text"])
    return seg["start"] + (seg["end"] - seg["start"]) * f


T_MORNING = word_time("Was geht", "Morgen", 0.2)
T_NOON = word_time("Was geht", "Mittag", 0.2)
T_EVENING = word_time("Was geht", "Abend", 0.2)


def palette_at(t):
    keys = [(0.0, "golden"), (T_MORNING - 0.3, "golden"), (T_MORNING + 0.3, "morning"), (T_NOON - 0.3, "morning"),
            (T_NOON + 0.3, "noon"), (T_EVENING - 0.3, "noon"), (T_EVENING + 0.3, "evening"), (st("PAUSE"), "evening"),
            (st("PAUSE") + 0.6, "night"), (st("Hier kommt") - 0.2, "night"),
            (st("Hier kommt") + 0.5, "golden"), (st("Am Morgen") - 0.2, "golden"), (st("Am Morgen") + 0.5, "morning"),
            (st("Am Mittag") - 0.2, "morning"), (st("Am Mittag") + 0.5, "noon"), (st("Und am Abend") - 0.2, "noon"),
            (st("Und am Abend") + 0.5, "evening"), (st("Hättest") - 0.1, "evening"), (st("Hättest") + 0.5, "golden")]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t <= t1:
            return _pal_mix(a, b, smooth(prog(t, t0, t1)))
    return _pal_mix(keys[-1][1], keys[-1][1], 0)


def sun_pos(t):
    """sun travels with the time of day (morning low left, noon high, evening low right)"""
    if st("Was geht") <= t < st("PAUSE"):
        tt = prog(t, T_MORNING - 0.3, T_EVENING + 0.3)
    elif st("Am Morgen") - 0.3 <= t < st("Hättest"):
        tt = prog(t, st("Am Morgen") - 0.2, st("Und am Abend") + 0.5)
    elif st("PAUSE") <= t < st("Hier kommt"):
        return (180, 420)                       # moon
    else:
        return (930, 720)
    return (60 + 960 * tt, 1000 - 720 * math.sin(math.pi * tt))


def shake(t):
    a = 16 * math.exp(-t * 6) if t < 0.8 else 0.0
    tr = st("Was geht")
    if tr - 0.2 < t < tr + 1.4:
        a += 7 * math.sin(math.pi * prog(t, tr - 0.2, tr + 1.4))
    return (a * math.sin(t * 71), a * math.cos(t * 59))


def drift(cam, t, amp=1.0):
    """slow handheld drift + breathing zoom so the parallax is always alive"""
    cx, cy, vh = cam
    sx, sy = shake(t)
    k = vh / 1920
    return (cx + amp * k * (14 * math.sin(t * 0.43) + 6 * math.sin(t * 1.1)) + sx * k,
            cy + amp * k * (8 * math.sin(t * 0.31 + 1)) + sy * k,
            vh * (1 + 0.012 * math.sin(t * 0.5)))


# ------------------------------------------------------------------ animated details per layer
_R = np.random.default_rng(42)
_STARS = [(_R.uniform(WX0, WX1), _R.uniform(WY0 + 150, HORIZON - 200), _R.uniform(1.2, 3.2)) for _ in range(140)]


def sky_actors(cv, t, sun, stars):
    if stars > 0.02:
        for i, (x, y, r) in enumerate(_STARS):
            tw = 0.6 + 0.4 * math.sin(t * 3 + i * 1.7)
            cv.circle(x, y, r * 1.2, fill=(255, 250, 230, int(220 * stars * tw)))
    sx, sy = sun_pos(t)
    night = stars > 0.7
    if not night:                                # god rays
        for i in range(12):
            a = i / 12 * 2 * math.pi + t * 0.05
            da = 0.07 + 0.03 * math.sin(t + i)
            L = 1400
            cv.poly([(sx, sy), (sx + math.cos(a - da) * L, sy + math.sin(a - da) * L),
                     (sx + math.cos(a + da) * L, sy + math.sin(a + da) * L)],
                    fill=tuple(sun) + (int(16 + 8 * math.sin(t * 0.7 + i)),))
    for k in range(6, 0, -1):
        cv.circle(sx, sy, 60 + k * 22, fill=tuple(sun) + (9,))
    if night:
        cv.circle(sx, sy, 58, fill=hexc("#f4f1d0"))
        for dx, dy, r in ((-18, -10, 10), (14, 12, 8), (6, -24, 6)):
            cv.circle(sx + dx, sy + dy, r, fill=hexc("#dcd6b0"))
    else:
        cv.circle(sx, sy, 64, fill=tuple(sun))
        cv.circle(sx - 14, sy - 14, 40, fill=tuple(min(255, c + 20) for c in sun))
    for i, (cx, cy, s) in enumerate(((150, 160, 0.9), (720, 330, 0.7), (1150, 120, 0.8), (-200, 380, 0.6))):
        x = (cx + t * 14 * (1 + i * 0.3)) % 2100 - 450
        top = (255, 248, 240, int(200 * (1 - stars * 0.7)))
        bot = (230, 200, 200, int(190 * (1 - stars * 0.7)))
        cv.rect(x - 170 * s, cy - 10 * s, x + 170 * s, cy + 34 * s, fill=bot, r=24 * s)
        for dx, dy, r in ((-90, 0, 50), (-20, -30, 70), (60, -6, 56), (120, 10, 40)):
            cv.circle(x + dx * s, cy + dy * s + 8 * s, r * s, fill=bot)
            cv.circle(x + dx * s, cy + dy * s, r * s * 0.95, fill=top)


def far_actors(t):
    def fn(cv, box):
        for i in range(5):                     # camel caravan with riders on the far dune ridge
            x = 1500 - ((t * 26 + i * 70) % 2100)
            y = HORIZON - 70 - 40 * math.sin(x / 260 + 1) - 16 * math.sin(x / 90) + 4 + 2 * math.sin(t * 5 + i)
            col = (110, 70, 40, 255)
            cv.ellipse(x - 22, y - 30, x + 22, y - 8, fill=col)
            cv.circle(x - 4, y - 32, 9, fill=col)
            cv.line([(x - 20, y - 20), (x - 34, y - 40), (x - 40, y - 38)], col, 6)
            for lx in (x - 14, x - 3, x + 8, x + 16):
                cv.line([(lx, y - 10), (lx + 3 * math.sin(t * 7 + lx), y + 10)], col, 3)
            if i % 2 == 0:
                cv.line([(x - 2, y - 40), (x - 2, y - 56)], (60, 40, 70, 255), 6)
                cv.circle(x - 2, y - 60, 5, fill=(240, 230, 220, 255))
        bx = 140 + (t * 9) % 260               # workers dragging a stone block
        by = HORIZON + 4
        cv.rect(bx, by - 22, bx + 34, by, fill=(225, 190, 130, 255))
        for k in range(4):
            wx = bx - 24 - k * 16
            lean = 4 * math.sin(t * 6 + k)
            cv.line([(wx, by), (wx + 4 + lean, by - 20)], (90, 60, 40, 255), 4)
            cv.circle(wx + 5 + lean, by - 24, 4, fill=(90, 60, 40, 255))
        cv.line([(bx, by - 12), (bx - 80, by - 18)], (90, 60, 40, 200), 2)
        for i in range(7):                     # bird flock in V formation
            j = i - 3
            x = (t * 60 + 200) % 2300 - 500 - abs(j) * 26
            y = 430 + j * 18 + 8 * math.sin(t * 1.3)
            w = 9 * math.sin(t * 10 + i)
            cv.line([(x - 12, y - w), (x, y), (x + 12, y - w)], (45, 35, 70, 230), 3)
        a = t * 0.6                            # circling falcon
        fx, fy = 860 + 160 * math.cos(a), 520 + 50 * math.sin(a)
        w = 6 * math.sin(t * 4)
        cv.line([(fx - 26, fy - w), (fx, fy + 4), (fx + 26, fy - w)], (60, 40, 40, 255), 4)
        g = max(0, math.sin(t * 1.7)) ** 8     # capstone glint
        if g > 0.05:
            for ang in (0, math.pi / 2):
                cv.line([(640 - 30 * g * math.cos(ang), 600 - 30 * g * math.sin(ang)),
                         (640 + 30 * g * math.cos(ang), 600 + 30 * g * math.sin(ang))], (255, 255, 230, int(255 * g)), 3)
    return fn


def mid_actors(t):
    def fn(cv, box):
        for i in range(50):                    # water sparkle
            x = (i * 53 + t * 30) % 1940 + WX0
            y = HORIZON + 50 + (i * 17) % 34
            a = max(0, math.sin(t * 3 + i * 2.3))
            cv.rect(x, y, x + 18 + (i % 3) * 8, y + 2.5, fill=(255, 255, 255, int(170 * a)))
        for i, (x0, sp, s) in enumerate(((-300, 18, 1.0), (900, -12, 0.75))):     # feluccas
            x = (x0 + t * sp - WX0) % 2100 + WX0
            y = HORIZON + 66 + 2 * math.sin(t * 2 + i)
            cv.poly([(x - 40 * s, y - 8 * s), (x + 44 * s, y - 8 * s), (x + 30 * s, y + 6 * s), (x - 28 * s, y + 6 * s)],
                    fill=hexc("#6b4126"))
            cv.line([(x, y - 8 * s), (x + 2 * s, y - 92 * s)], hexc("#4a2c18"), 4 * s)
            sw = 4 * math.sin(t * 1.4 + i)
            cv.poly([(x + 2 * s, y - 90 * s), (x - 38 * s + sw, y - 14 * s), (x + 30 * s + sw, y - 16 * s)],
                    fill=hexc("#f6efe2"))
            cv.poly([(x + 2 * s, y - 90 * s), (x + 30 * s + sw, y - 16 * s), (x + 8 * s, y - 16 * s)],
                    fill=hexc("#d9cfbd"))
            cv.ellipse(x - 50 * s, y + 4 * s, x + 54 * s, y + 10 * s, fill=(255, 255, 255, 80))
        c = (t % 9) / 9                        # crocodile surfacing now and then
        if 0.2 < c < 0.6:
            a = math.sin(math.pi * (c - 0.2) / 0.4)
            x = 300 + c * 80
            cv.ellipse(x - 30, HORIZON + 70, x + 30, HORIZON + 78, fill=(50, 90, 50, int(220 * a)))
            for dx in (-10, 8):
                cv.circle(x + dx, HORIZON + 69, 4, fill=(60, 100, 60, int(255 * a)))
        for px, hgt in ((40, 230), (130, 180), (760, 210), (840, 160), (1240, 200), (-300, 220)):   # palms
            base = HORIZON + 44
            top = (px + 8 * math.sin(t * 1.3 + px), base - hgt)
            cv.line([(px, base), (px + 6, base - hgt * 0.5), top], hexc("#6b4126"), 11)
            for k in range(6):
                yy = base - hgt * (0.15 + k * 0.14)
                cv.line([(px - 6, yy), (px + 8, yy - 6)], hexc("#4f301b"), 3)
            for a in range(7):
                ang = math.pi + a * math.pi / 6 + 0.1 * math.sin(t * 2 + a + px)
                tip = (top[0] + math.cos(ang) * 100, top[1] + math.sin(ang) * 46 + 36)
                mid = ((top[0] + tip[0]) / 2, (top[1] + tip[1]) / 2 - 18)
                cv.line([top, mid, tip], hexc("#2f7340"), 13)
                cv.line([top, mid, tip], hexc("#4ea05c"), 6)
            for d in (-8, 4, 14):
                cv.circle(top[0] + d, top[1] + 10, 6, fill=hexc("#a3541e"))
    return fn


def dust_falling(cv, t, t0):
    if not (t0 < t < t0 + 2.6):
        return
    for i in range(36):
        rng = np.random.default_rng(i)
        x = rng.uniform(380, 560)
        d = t - t0 - rng.uniform(0, 1.2)
        if d < 0 or d > 1.6:
            continue
        y = 900 + rng.uniform(0, 140) + 260 * d * d
        if y > 1240:
            continue
        cv.circle(x + 10 * math.sin(d * 4 + i), y, rng.uniform(2, 4), fill=(240, 210, 160, int(220 * (1 - d / 1.6))))


def sphinx_eyes(cv, glow, t):
    if glow <= 0.01:
        return
    hx, hy = 470, 985
    p = 0.75 + 0.25 * math.sin(t * 8)
    for ex in (hx - 23, hx + 23):
        for k in range(3, 0, -1):
            cv.circle(ex + 1, hy - 12, (8 + k * 8) * p, fill=(255, 220, 90, int(80 * glow)))
        cv.ellipse(ex - 14, hy - 20, ex + 14, hy - 5, fill=(255, 240, 150, int(255 * glow)))
    for i, (x, y) in enumerate(GLYPHS):        # glyphs on the plinth light up one after another
        a = glow * clamp((t - st("Was geht") - i * 0.18) * 2)
        if a > 0.02:
            for k in range(3, 0, -1):
                cv.circle(x + 40, y + 6, 10 + k * 5, fill=(255, 210, 90, int(16 * a)))
            draw_glyph(cv, x + 40, y + 6, i % 4, (255, 236, 150, int(255 * a)))


def sand_wind(cv, t, y0=PATH_Y - 120, n=40, big=False):
    for i in range(n):
        x = (i * 97 + t * (180 + (i % 5) * 30)) % 2000 + WX0
        y = y0 + (i * 53) % 300 + 10 * math.sin(t * 3 + i)
        cv.circle(x, y, (4 if big else 2.2) + (i % 3), fill=(255, 235, 190, 140))
    for k in range(3):                         # wind streaks
        x = (k * 700 + t * 420) % 2400 + WX0
        y = y0 + 60 + k * 70
        cv.line([(x, y), (x + 140, y - 6), (x + 260, y)], (255, 240, 210, 70), 3)


def scarab(cv, t):
    x = 760 - (t * 22) % 900
    y = 1342 + 2 * math.sin(t * 9)
    cv.ellipse(x - 12, y - 10, x + 12, y + 4, fill=hexc("#1f5d6b"))
    cv.ellipse(x - 8, y - 9, x + 2, y - 3, fill=(140, 220, 230, 180))
    cv.circle(x - 13, y - 3, 5, fill=hexc("#16424c"))
    for k in range(3):
        dx = -6 + k * 7
        cv.line([(x + dx, y + 2), (x + dx + 4 * math.sin(t * 20 + k), y + 7)], hexc("#16424c"), 2)


def torches(cv, t, k=1.0):
    for cx in COLS:
        tx = cx + (75 + 16 if cx < 540 else -75 - 16)
        for r in range(5, 0, -1):
            cv.circle(tx, 712, 26 + r * 22 * k, fill=(255, 170, 60, int(16 * k)))
        for j in range(3):
            fl = 1 + 0.25 * math.sin(t * 17 + j * 2.1 + cx)
            hh = (70 - j * 18) * fl
            ww = 24 - j * 6
            col = [(255, 120, 30, 240), (255, 190, 60, 240), (255, 245, 180, 250)][j]
            cv.poly([(tx - ww, 742), (tx + ww, 742), (tx + 4 * math.sin(t * 11 + j), 742 - hh)], fill=col)


def fg_actors(t, torch=1.0):
    def fn(cv, box):
        torches(cv, t, torch)
        sand_wind(cv, t, y0=1500, n=18, big=True)
    return fn


def char_shadow(cv, x, w=70):
    cv.ellipse(x - w, PATH_Y - 10, x + w, PATH_Y + 12, fill=(90, 50, 25, 90))


def poof(cv, x, t, t0, dur=0.6):
    p = prog(t, t0 - dur / 2, t0 + dur / 2)
    if not 0 < p < 1:
        return
    a = math.sin(math.pi * p)
    for i in range(22):
        ang = i / 22 * 2 * math.pi + p * 5
        r = 40 + 120 * p
        cv.circle(x + math.cos(ang) * r, PATH_Y - 150 + math.sin(ang) * r * 0.9, 16 + 10 * a,
                  fill=(255, 236, 190, int(200 * a)))
    for k in range(8):
        ang = k / 8 * 2 * math.pi + p * 2
        cv.line([(x + math.cos(ang) * 30, PATH_Y - 150 + math.sin(ang) * 30),
                 (x + math.cos(ang) * (90 + 90 * p), PATH_Y - 150 + math.sin(ang) * (90 + 90 * p))],
                (255, 250, 210, int(230 * a)), 5)


# ------------------------------------------------------------------ 3D text pills
def _pill_tile(words, base, bg, fg, pops=None, depth=12, Z=2):
    """extruded glossy pill with words; returns (tile at Z x, unrotated) and the pill box in 1x tile coords"""
    pops = pops or [0.0] * len(words)
    gap = 0.28 * base
    sizes = [base * (1 + 0.28 * pp) for pp in pops]
    widths = [font(int(sz)).getbbox(w)[2] for sz, w in zip(sizes, words)]
    tw = sum(widths) + gap * (len(words) - 1)
    padx, pady = 0.42 * base, 0.24 * base
    x0, y0 = 30, 30
    x1, y1 = x0 + tw + 2 * padx, y0 + base + 2 * pady
    PW, PH = int(x1 + 40), int(y1 + depth + 50)
    tile = Image.new("RGBA", (PW * Z, PH * Z), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile, "RGBA")
    rad = int((y1 - y0) / 2.6 * Z)
    d.rounded_rectangle([(x0 + 10) * Z, (y0 + depth + 14) * Z, (x1 + 10) * Z, (y1 + depth + 14) * Z], radius=rad,
                        fill=(20, 12, 40, 90))
    side = _shade(hexc(bg), 0.42)
    for k in range(depth, 0, -1):            # extrusion
        d.rounded_rectangle([x0 * Z, (y0 + k) * Z, x1 * Z, (y1 + k) * Z], radius=rad, fill=side)
    d.rounded_rectangle([x0 * Z, y0 * Z, x1 * Z, y1 * Z], radius=rad, fill=hexc(bg), outline=hexc("#1d1b33"),
                        width=4 * Z)
    d.rounded_rectangle([(x0 + 10) * Z, (y0 + 6) * Z, (x1 - 10) * Z, (y0 + (y1 - y0) * 0.42) * Z], radius=rad,
                        fill=(255, 255, 255, 55))   # gloss
    x = x0 + padx
    cy = (y0 + (y1 - y0) / 2) * Z
    for j, w in enumerate(words):
        cxw = (x + widths[j] / 2) * Z
        pp = pops[j]
        if pp > 0.05 and len(words) > 1:     # capsule highlight that stays inside the round pill
            hl = (255, 255, 255) if bg == "#ffd34d" else (255, 211, 77)
            hh = ((y1 - y0) / 2 - 7) * Z
            hw = widths[j] / 2 * Z + hh * 0.55
            lx, rx = max(cxw - hw, (x0 + 7) * Z), min(cxw + hw, (x1 - 7) * Z)
            col = tuple(int(c0 + (c1 - c0) * min(1, pp * 1.6)) for c0, c1 in zip(hexc(bg), hl))
            d.rounded_rectangle([lx, cy - hh, rx, cy + hh], radius=int(hh), fill=col)
        col = (hexc("#ffe46b") if bg == "#e2574c" else hexc("#d62828")) if pp > 0.3 else hexc(fg)
        d.text((cxw + 3 * Z, cy + 4 * Z), w, font=font(int(sizes[j] * Z)), fill=(0, 0, 0, 60), anchor="mm")
        d.text((cxw, cy), w, font=font(int(sizes[j] * Z)), fill=col, anchor="mm",
               stroke_width=int(2 * Z * pp), stroke_fill=hexc("#1d1b33"))
        x += widths[j] + gap
    return tile, (x0, y0, x1, y1)


def pill3d(img, cx, cy, text, size, bg="#fff6e6", fg="#2b2140", rot=0.0, scale=1.0, depth=10, max_w=860):
    if scale <= 0.01:
        return
    while font(size).getbbox(text)[2] + 0.84 * size > max_w and size > 24:
        size -= 2
    tile, (x0, y0, x1, y1) = _pill_tile([text], size, bg, fg, depth=depth)
    if rot:
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
    k = scale / 2
    tile = tile.resize((max(1, int(tile.width * k)), max(1, int(tile.height * k))), Image.LANCZOS)
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)
    if scale > 0.6:
        pw, ph = (x1 - x0) * scale, (y1 - y0 + depth) * scale
        log_ui("pill:" + text, cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2)


def burst(img, cx, cy, a, t, r0=170, r1=430, col=(255, 222, 90)):
    if a <= 0.02:
        return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    n = 18
    for i in range(n):
        ang = i / n * 2 * math.pi + t * 0.8
        da = 0.06
        rr = r1 * (0.75 + 0.25 * ((i * 7) % 3) / 2)
        d.polygon([(cx + math.cos(ang - da) * r0, cy + math.sin(ang - da) * r0 * 0.6),
                   (cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * 0.6),
                   (cx + math.cos(ang + da) * r0, cy + math.sin(ang + da) * r0 * 0.6)], fill=col + (int(200 * a),))
    img.paste(lay, (0, 0), lay)


def karaoke(frame, t, lines, seg_key, ys):
    """whole sentence visible from frame 0; the spoken word grows, changes colour and gets a highlight"""
    t0, t1 = S[K[seg_key]], E[K[seg_key]]
    words = [w for line, *_ in lines for w in line]
    weights = [len(w) + 2 for w in words]
    tot = sum(weights)
    spans, acc = [], t0 + 0.02
    for wgt in weights:
        dd = (t1 - t0 - 0.06) * wgt / tot
        spans.append((acc, acc + dd))
        acc += dd
    fade = 1 - prog(t, t1 + 0.15, t1 + 0.5)
    if fade <= 0.01:
        return
    i = 0
    for li, (line, bg, fg, rot, base) in enumerate(lines):
        pops = []
        for j in range(len(line)):
            a_, b_ = spans[i + j]
            p = prog(t, a_ - 0.03, b_ + 0.08)
            pops.append(math.sin(math.pi * p) if 0 < p < 1 else 0.0)
        b = base
        while True:
            tile, box = _pill_tile(line, b, bg, fg, pops)
            if box[2] - box[0] <= 780 or b < 40:
                break
            b -= 3
        single = len(line) == 1
        sc = (1 + 0.12 * pops[0]) if single else 1.0
        if li == 0 and t < 0.35:             # slam-in of WARTE at the very start
            sc *= 1 + 0.22 * (1 - ease_out_back(prog(t, 0, 0.35)))
        if single:
            burst(frame, OUT_W / 2, ys[li], max(pops[0], 1 - prog(t, 0.0, 0.7)) * fade, t)
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
        k = sc / 2
        tile = tile.resize((max(1, int(tile.width * k)), max(1, int(tile.height * k))), Image.LANCZOS)
        if fade < 1:
            tile.putalpha(tile.split()[3].point(lambda v: int(v * fade)))
        sh = 12 * math.sin(t * 75) * pops[0] if single and pops[0] > 0.05 else 0
        px, py = int(OUT_W / 2 - tile.width / 2 + sh), int(ys[li] - tile.height / 2)
        frame.paste(tile, (px, py), tile)
        bw, bh = (box[2] - box[0]) * sc, (box[3] - box[1] + 12) * sc
        if fade > 0.5:
            log_ui("karaoke " + str(li), OUT_W / 2 - bw / 2 + sh, ys[li] - bh / 2, OUT_W / 2 + bw / 2 + sh, ys[li] + bh / 2)
        i += len(line)


INTRO_LINES = [(["WARTE!"], "#e2574c", "#ffffff", -3, 172),
               (["DIESES", "RÄTSEL", "KANN"], "#fff6e6", "#2b2140", 2, 92),
               (["NIEMAND", "LÖSEN!"], "#ffd34d", "#2b2140", -2, 104)]


def legs_pill(frame, t, ts, y, label, n, bg, rot):
    if t < ts:
        return
    pill3d(frame, OUT_W / 2, y, f"{label}:  {n} BEINE", 58, bg=bg, scale=ease_out_back(prog(t, ts, ts + 0.3)), rot=rot)


# ------------------------------------------------------------------ scenes
BIG = (540, 1090, 2300)
CAM_SPHINX = (430, 1070, 1250)
CAM_FACE = (470, 1010, 880)


def scene_story(t):
    t0, t1, t2, t3 = st("WARTE"), st("Im alten"), st("Wer vorbei"), st("Was geht")
    big = (BIG[0], BIG[1], BIG[2] - 120 * prog(t, 0, t1))
    cam = keyframes(t, [(t0, big), (t1 - 0.05, (540, 1090, 2180)), (t1 + 1.8, CAM_SPHINX), (t2 - 0.1, (440, 1070, 1180)),
                        (t2 + 1.1, (450, 1040, 1040)), (t3, (455, 1035, 1000)), (t3 + 0.9, CAM_FACE),
                        (st("PAUSE"), (470, 1020, 820))])
    cam = drift(cam, t)
    glow = smooth(prog(t, t3 - 0.2, t3 + 0.4))

    def main(cv, box):
        sphinx_eyes(cv, glow, t)
        dust_falling(cv, t, t3 - 0.1)
        scarab(cv, t)
        sand_wind(cv, t)

    frame, boxes = render_scene(cam, t, palette_at(t), {"far": far_actors(t), "mid": mid_actors(t), "main": main,
                                                        "fg": fg_actors(t, 0.6)})
    if t < t1 + 0.6:       # darken behind the opening text + impact flash
        frame = Image.blend(frame, Image.new("RGB", frame.size, (15, 10, 30)), 0.32 * (1 - prog(t, t1, t1 + 0.6)))
        if t < 0.22:
            frame = Image.blend(frame, Image.new("RGB", frame.size, (255, 250, 230)), 0.45 * (1 - t / 0.22))
    karaoke(frame, t, INTRO_LINES, "WARTE", [590, 860, 1010])
    if t1 + 0.3 <= t < t2 + 0.2:
        pill3d(frame, OUT_W / 2, 330, "ALTES ÄGYPTEN", 68, bg="#ffd34d", rot=-2,
               scale=ease_out_back(prog(t, t1 + 0.3, t1 + 0.65)))
        sx, sy = w2s(470, 820, boxes["main"])
        pill3d(frame, clamp(sx, 220, 800), clamp(sy, 480, 1300), "DIE SPHINX", 50, bg="#fff6e6",
               scale=ease_out_back(prog(t, t1 + 1.3, t1 + 1.6)))
    if t2 <= t < t3:
        pill3d(frame, OUT_W / 2, 320, "NUR WER DAS RÄTSEL LÖST,", 48, bg="#fff6e6", rot=-2,
               scale=ease_out_back(prog(t, t2, t2 + 0.3)))
        pill3d(frame, OUT_W / 2, 440, "DARF VORBEI", 68, bg="#e2574c", fg="#ffffff", rot=2,
               scale=ease_out_back(prog(t, t2 + 0.25, t2 + 0.55)))
    if t3 <= t:
        pill3d(frame, OUT_W / 2, 330, "WAS IST DAS?", 74, bg="#ffd34d", rot=-2,
               scale=ease_out_back(prog(t, t3, t3 + 0.35)))
        legs_pill(frame, t, T_MORNING - 0.1, 1110, "MORGEN", 4, "#ffd9a0", -2)
        legs_pill(frame, t, T_NOON - 0.1, 1240, "MITTAG", 2, "#fff6e6", 2)
        legs_pill(frame, t, T_EVENING - 0.1, 1370, "ABEND", 3, "#f4aab0", -2)
    return frame


Q_Y = 860


def sun_icon(img, x, y, kind, t, s=1.2):
    S2 = 2
    sz = int(300 * s)
    lay = Image.new("RGBA", (sz * S2, sz * S2), (0, 0, 0, 0))
    cv = BCanvas(lay, -150, -150, s * S2)
    glow = (255, 210, 90) if kind != "moon" else (210, 220, 255)
    for k in range(5, 0, -1):
        cv.circle(0, 0, 40 + k * 14, fill=glow + (22,))
    if kind == "moon":
        cv.circle(0, 0, 44, fill=hexc("#f4f1d0"))
        cv.circle(-12, -10, 26, fill=hexc("#fffbe8"))
        cv.circle(24, -16, 40, fill=(0, 0, 0, 0))
        m = Image.new("L", lay.size, 0)
        ImageDraw.Draw(m).ellipse([(150 - 16) * s * S2, (150 - 58) * s * S2, (150 + 64) * s * S2, (150 + 24) * s * S2],
                                  fill=255)
        al = ImageChops.subtract(lay.split()[3], m)
        glow_l = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        gcv = BCanvas(glow_l, -150, -150, s * S2)
        for k in range(5, 0, -1):
            gcv.circle(0, 0, 40 + k * 14, fill=glow + (18,))
        lay.putalpha(al)
        glow_l.alpha_composite(lay)
        lay = glow_l
    else:
        col = hexc("#ffd34d") if kind == "sun" else hexc("#ffb36b")
        for i in range(12):
            a = i / 12 * 2 * math.pi + t * 0.8
            L = 66 + 8 * math.sin(t * 4 + i)
            cv.poly([(math.cos(a - 0.13) * 46, math.sin(a - 0.13) * 46), (math.cos(a) * L, math.sin(a) * L),
                     (math.cos(a + 0.13) * 46, math.sin(a + 0.13) * 46)], fill=col)
        cv.circle(0, 0, 42, fill=col)
        cv.circle(-12, -12, 22, fill=tuple(min(255, c + 30) for c in col))
        if kind == "rise":               # half sun over the horizon line
            ImageDraw.Draw(lay).rectangle([0, int((150 + 12) * s * S2), lay.width, lay.height], fill=(0, 0, 0, 0))
            cv.line([(-90, 12), (90, 12)], hexc("#ffe2a0"), 6)
    lay = lay.resize((sz, sz), Image.LANCZOS)
    img.paste(lay, (int(x - sz / 2), int(y - sz / 2)), lay)


def scene_question(t):
    t0, t_pause, t_tip, t_cm = st("Was geht"), st("PAUSE"), st("Kleiner Tipp"), st("Schreib deine")
    p = prog(t, t_pause, st("Hier kommt"))
    cam = drift((450 + 30 * p, 1040, 1500 - 200 * p), t)

    def main(cv, box):
        sphinx_eyes(cv, 0.8, t)
        sand_wind(cv, t)

    img, _ = render_scene(cam, t, palette_at(t), {"far": far_actors(t), "mid": mid_actors(t), "main": main,
                                                  "fg": fg_actors(t, 1.0)}, haze=False)
    img = Image.blend(img, Image.new("RGB", img.size, (10, 14, 40)), 0.42)
    for k, (kind, lab, n) in enumerate((("rise", "MORGEN", 4), ("sun", "MITTAG", 2), ("moon", "ABEND", 3))):
        x = 230 + k * 300
        bob = 8 * math.sin(t * 2.2 + k)
        sun_icon(img, x, Q_Y + 50 + bob, kind, t)
        pill3d(img, x, Q_Y + 200, lab, 40, bg="#fff6e6", depth=6)
        pill3d(img, x, Q_Y + 320 + bob * 0.5, str(n), 100, bg="#ffd34d", rot=(-4, 3, -3)[k], depth=12)
    pill3d(img, OUT_W / 2, 360, "WAS GEHT AUF", 86, bg="#fff6e6", rot=-3, scale=ease_out_back(prog(t, t0, t0 + 0.35)))
    pill3d(img, OUT_W / 2, 510, "4, 2 UND 3 BEINEN?", 78, bg="#ffd34d", rot=2,
           scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)))
    if t_pause - 0.2 < t < t_tip:
        d = ImageDraw.Draw(img, "RGBA")
        for i in range(3):
            ph = (t * 3 - i * 0.35) % 2
            a = clamp(1 - abs(ph - 0.5) * 2) if ph < 1 else 0
            r = 18 + 10 * a
            cx = OUT_W / 2 - 70 + i * 70
            d.ellipse([cx - r, 690 - r, cx + r, 690 + r], fill=(255, 255, 255, int(120 + 135 * a)))
    if t > t_tip:
        pill3d(img, OUT_W / 2, 680, "TIPP: DU KENNST ES GUT!", 58, bg="#c5def5", rot=-2,
               scale=ease_out_back(prog(t, t_tip, t_tip + 0.35)))
    if t > t_cm:
        pill3d(img, OUT_W / 2, 1420, "SCHREIB'S IN DIE KOMMENTARE", 42, bg="#ffffff",
               scale=ease_out_back(prog(t, t_cm, t_cm + 0.35)))
    return img


def life_x(t):
    a1, a2, a3, te = st("Am Morgen"), st("Am Mittag"), st("Und am Abend"), st("Hättest")
    if t < a2:
        return 0 + 200 * prog(t, a1, a2)
    if t < a3:
        return 200 + 380 * prog(t, a2, a3)
    return 580 + 200 * prog(t, a3, te)


def scene_solution(t):
    t0, tm, a1, a2, a3, t_end = st("Hier kommt"), st("Es ist der"), st("Am Morgen"), st("Am Mittag"), \
        st("Und am Abend"), st("Hättest")
    reveal = (540, 1080, 1800)
    xs = (life_x(t - 0.35) + life_x(t) + life_x(t + 0.35)) / 3
    track = (clamp(xs + 120, 300, 740), 1110, 1450)
    if t < a1:
        cam = keyframes(t, [(t0, (470, 1040, 1100)), (tm, reveal)])
    else:
        f = smooth(prog(t, a1, a1 + 0.9))
        cam = tuple(p + (q - p) * f for p, q in zip(reveal, track))
    cam = drift(cam, t, 0.6)

    def main(cv, box):
        scarab(cv, t)
        sand_wind(cv, t)
        if tm <= t < a1 + 0.3:      # the human in all three ages
            pops = [ease_out_back(prog(t, tm + k * 0.25, tm + k * 0.25 + 0.35)) for k in range(3)]
            hide = 1 - prog(t, a1, a1 + 0.3)
            if pops[0] * hide > 0.05:
                char_shadow(cv, 300, 80)
                draw_baby(cv, 300, PATH_Y, 1.6 * pops[0] * hide, phase=t * 6)
            if pops[1] * hide > 0.05:
                char_shadow(cv, 540)
                draw_person(cv, 540, PATH_Y, ADULT, face=1, h=300 * pops[1] * hide, wave=t * 8, blink=(t % 3) < 0.12)
            if pops[2] * hide > 0.05:
                char_shadow(cv, 790)
                hand = draw_person(cv, 790, PATH_Y, OLD, face=-1, h=285 * pops[2] * hide, lean=-16,
                                   reach=(730, PATH_Y - 120 * pops[2] * hide))
                draw_cane(cv, hand, (718, PATH_Y))
            poof(cv, 540, t, a1 + 0.1, 0.5)
        if a1 <= t < t_end + 0.3:
            x = life_x(t)
            if t < a2 + 0.05:
                char_shadow(cv, x, 85)
                draw_baby(cv, x, PATH_Y, 1.6, phase=t * 9)
                for k in range(3):       # little sand puffs behind
                    q = (t * 3 + k / 3) % 1
                    cv.circle(x - 90 - q * 40, PATH_Y - 10 - q * 20, 8 + q * 10, fill=(255, 236, 196, int(150 * (1 - q))))
            elif t < a3 + 0.05:
                char_shadow(cv, x)
                draw_person(cv, x, PATH_Y, ADULT, face=1, h=300, phase=t * 10, blink=(t % 3) < 0.12)
            else:
                char_shadow(cv, x + 20)
                hand = draw_person(cv, x, PATH_Y, OLD, face=1, h=285, lean=16, phase=t * 5,
                                   bounce=3 * abs(math.sin(t * 3)), reach=(x + 72, PATH_Y - 120))
                draw_cane(cv, hand, (x + 84 + 8 * math.sin(t * 3.0), PATH_Y - 6 * abs(math.sin(t * 3.0))))
            poof(cv, life_x(a2), t, a2, 0.5)
            poof(cv, life_x(a3), t, a3, 0.5)

    frame, boxes = render_scene(cam, t, palette_at(t), {"far": far_actors(t), "mid": mid_actors(t), "main": main,
                                                        "fg": fg_actors(t, 0.6)})
    if t < t0 + 1.3:
        pill3d(frame, OUT_W / 2, 330, "DIE LÖSUNG", 100, bg="#fff6e6", rot=-4,
               scale=ease_out_back(prog(t, t0, t0 + 0.35)) * (1 - prog(t, t0 + 1.0, t0 + 1.3)))
    if tm <= t < a1:
        burst(frame, OUT_W / 2, 400, 0.8 * (1 - prog(t, a1 - 0.4, a1)), t, 160, 380, (120, 230, 150))
        pill3d(frame, OUT_W / 2, 400, "DER MENSCH!", 116, bg="#37b26c", fg="#ffffff", rot=-3,
               scale=ease_out_back(prog(t, tm, tm + 0.35)))
    for (ta, tb, lab, sub, bg) in ((a1, a2, "MORGEN = BABY", "4 BEINE", "#ffd9a0"),
                                   (a2, a3, "MITTAG = ERWACHSEN", "2 BEINE", "#fff6e6"),
                                   (a3, t_end, "ABEND = IM ALTER", "2 BEINE + STOCK = 3", "#f4aab0")):
        if ta <= t < tb:
            pill3d(frame, OUT_W / 2, 330, lab, 62, bg=bg, rot=-2, scale=ease_out_back(prog(t, ta, ta + 0.3)))
            pill3d(frame, OUT_W / 2, 455, sub, 72, bg="#ffd34d", rot=2,
                   scale=ease_out_back(prog(t, ta + 0.35, ta + 0.65)))
    return frame


def scene_outro(t):
    t0, t1 = st("Hättest"), st("Schreib's")
    cam = drift((540, 1040, 1750 + 60 * prog(t, t0, END)), t, 0.6)

    def main(cv, box):
        sand_wind(cv, t)
        char_shadow(cv, 250, 85)
        draw_baby(cv, 250, PATH_Y, 1.5, phase=t * 6)
        char_shadow(cv, 530)
        draw_person(cv, 530, PATH_Y, ADULT, face=1, h=300, wave=t * 8)
        char_shadow(cv, 800)
        hand = draw_person(cv, 800, PATH_Y, OLD, face=-1, h=285, lean=-16, reach=(740, PATH_Y - 120))
        draw_cane(cv, hand, (728, PATH_Y))

    img, _ = render_scene(cam, t, palette_at(t), {"far": far_actors(t), "mid": mid_actors(t), "main": main,
                                                  "fg": fg_actors(t, 0.8)})
    img = ImageEnhance.Brightness(img).enhance(0.62)
    pill3d(img, OUT_W / 2, 520, "HÄTTEST DU'S", 98, bg="#fff6e6", rot=-3, scale=ease_out_back(prog(t, t0, t0 + 0.35)))
    pill3d(img, OUT_W / 2, 690, "GEWUSST?", 98, bg="#ffd34d", rot=2, scale=ease_out_back(prog(t, t0 + 0.2, t0 + 0.55)))
    if t > t1:
        pill3d(img, OUT_W / 2, 845, "SCHREIB'S IN DIE KOMMENTARE", 42, bg="#ffffff",
               scale=ease_out_back(prog(t, t1, t1 + 0.35)))
        followed = t > t1 + 2.0
        txt = "GEFOLGT  ✓" if followed else "+  FOLGEN"
        bg = "#37b26c" if followed else "#e2574c"
        pulse = 1 + (0.06 * math.sin(t * 10) if not followed else 0)
        pill3d(img, OUT_W / 2, 975, txt, 74, bg=bg, fg="#ffffff", scale=ease_out_back(prog(t, t1 + 0.4, t1 + 0.75)) * pulse)
        pill3d(img, OUT_W / 2, 1100, "MORGEN: NEUES RÄTSEL", 50, bg="#fff6e6",
               scale=ease_out_back(prog(t, t1 + 1.0, t1 + 1.35)))
    return img


SCENES = [
    (0.0, scene_story),
    (st("PAUSE") - 0.05, scene_question),
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
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame_at(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return path


def render(out="video.mp4", workers=4):
    for name, *_ in LAYERS:
        layer(name)
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
