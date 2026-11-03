"""Small flat-vector 2D toolkit for vertical (1080x1920) riddle videos.

World images are drawn once in "world units"; each frame crops a camera
window from the world, draws moving objects into the crop, and scales it to
the output size. Screen-space overlays (titles, clocks, icons) come last.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_W, OUT_H, FPS = 1080, 1920, 30
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
_font_cache = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_SEMI, size)
    return _font_cache[key]


def hexc(h, a=None):
    h = h.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return c + (a,) if a is not None else c


def mix(c1, c2, f):
    return tuple(int(round(a + (b - a) * f)) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- easing

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t, a, b):
    """0..1 progress of t through [a, b]."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def keyframes(t, keys, ease=smooth):
    """keys: list of (time, value or tuple). Eased piecewise interpolation."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            f = ease(prog(t, t0, t1))
            if isinstance(v0, tuple):
                return tuple(a + (b - a) * f for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * f
    return keys[-1][1]


def path_pos(t, keys):
    """Linear movement along (time, x, y) keys. Returns (x, y, moving, dx)."""
    if t <= keys[0][0]:
        return keys[0][1], keys[0][2], False, 0
    for (t0, x0, y0), (t1, x1, y1) in zip(keys, keys[1:]):
        if t <= t1:
            f = prog(t, t0, t1)
            moving = (x0, y0) != (x1, y1)
            return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, moving, x1 - x0
    return keys[-1][1], keys[-1][2], False, 0


# ---------------------------------------------------------------- canvas

class Canvas:
    """ImageDraw wrapper that takes world coordinates (offset + scale)."""

    def __init__(self, img, ox=0.0, oy=0.0, s=1.0):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, x, y):
        return ((x - self.ox) * self.s, (y - self.oy) * self.s)

    def w(self, v):
        return max(1, int(round(v * self.s)))

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1, r=0):
        a, b = self.p(x0, y0), self.p(x1, y1)
        box = [min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])]
        if r:
            self.d.rounded_rectangle(box, radius=r * self.s, fill=fill, outline=outline,
                                     width=self.w(width) if outline else 0)
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=self.w(width) if outline else 0)

    def circle(self, x, y, r, fill=None, outline=None, width=1):
        cx, cy = self.p(x, y)
        rr = r * self.s
        self.d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=fill, outline=outline,
                       width=self.w(width) if outline else 0)

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        a, b = self.p(x0, y0), self.p(x1, y1)
        self.d.ellipse([a[0], a[1], b[0], b[1]], fill=fill, outline=outline,
                       width=self.w(width) if outline else 0)

    def line(self, pts, fill, width=1, joint="curve", cap=True):
        q = [self.p(*pt) for pt in pts]
        wd = self.w(width)
        self.d.line(q, fill=fill, width=wd, joint=joint)
        if cap and wd > 3:
            for x, y in (q[0], q[-1]):
                self.d.ellipse([x - wd / 2, y - wd / 2, x + wd / 2, y + wd / 2], fill=fill)

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon([self.p(*pt) for pt in pts], fill=fill, outline=outline,
                       width=self.w(width) if outline else 0)

    def pieslice(self, x0, y0, x1, y1, a0, a1, fill):
        a, b = self.p(x0, y0), self.p(x1, y1)
        self.d.pieslice([a[0], a[1], b[0], b[1]], a0, a1, fill=fill)

    def arc(self, x0, y0, x1, y1, a0, a1, fill, width=1):
        a, b = self.p(x0, y0), self.p(x1, y1)
        self.d.arc([a[0], a[1], b[0], b[1]], a0, a1, fill=fill, width=self.w(width))

    def text(self, x, y, s, size, fill, anchor="mm", bold=True):
        self.d.text(self.p(x, y), s, font=font(max(6, int(size * self.s)), bold), fill=fill, anchor=anchor)


def vgradient(w, h, stops):
    """stops: list of (pos 0..1, '#rrggbb'). Returns RGB Image."""
    ys = np.linspace(0, 1, h)
    cols = np.zeros((h, 3))
    pos = [s[0] for s in stops]
    rgb = np.array([hexc(s[1]) for s in stops], float)
    for c in range(3):
        cols[:, c] = np.interp(ys, pos, rgb[:, c])
    arr = np.repeat(cols[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


# ---------------------------------------------------------------- people

class Style:
    def __init__(self, h, skin, hair, top, pants, shoes="#ffffff", hair_style="short",
                 head=0.16, glasses=False, accent=None):
        self.h, self.skin, self.hair, self.top = h, skin, hair, top
        self.pants, self.shoes, self.hair_style = pants, shoes, hair_style
        self.head, self.glasses, self.accent = head, glasses, accent


def draw_person(cv, x, y, st, phase=None, face=1, reach=None, umbrella=None, bounce=0.0,
                wave=0.0, h=None, arms_up=0.0, arm_scale=1.0):
    """Flat cartoon person standing with feet at (x, y).

    phase: walk-cycle phase in radians (None = standing)
    reach: (tx, ty) world point the front hand reaches towards
    umbrella: None | 'open' | 'closed' | 'pointer' (closed, extends from reaching hand)
    returns hand position of the front arm.
    """
    h = h or st.h
    y = y - bounce
    ink = hexc("#2b2140")
    skin = hexc(st.skin)
    leg_len = 0.40 * h
    hip_y = y - leg_len
    sh_y = y - 0.72 * h
    head_r = st.head * h
    head_y = sh_y - head_r * 0.95
    lw = 0.10 * h

    # legs
    sw = math.sin(phase) if phase is not None else 0.0
    for sgn, shade in ((-1, 0.82), (1, 1.0)):
        a = sgn * sw * 0.45
        fx, fy = x + math.sin(a) * leg_len, hip_y + math.cos(a) * leg_len
        col = mix(hexc(st.pants), (0, 0, 0), 1 - shade)
        cv.line([(x + sgn * lw * 0.25, hip_y), (fx, fy - lw * 0.3)], col, lw)
        cv.ellipse(fx - lw * 0.55 + face * lw * 0.25, fy - lw * 0.55, fx + lw * 0.65 + face * lw * 0.25, fy + lw * 0.1,
                   fill=hexc(st.shoes), outline=ink, width=0.012 * h)

    # back arm
    arm_len = 0.36 * h * arm_scale
    aw = 0.075 * h
    sx_b = x - face * 0.10 * h
    ab = -sw * 0.5 if phase is not None else 0.12 * face
    if arms_up:
        ab = -face * (math.pi * 0.85 * arms_up)
    hb = (sx_b + math.sin(ab) * arm_len, sh_y + math.cos(ab) * arm_len)
    cv.line([(sx_b, sh_y + aw * 0.4), hb], mix(hexc(st.top), (0, 0, 0), 0.15), aw)
    cv.circle(hb[0], hb[1], aw * 0.55, fill=skin)

    # torso
    tw = 0.20 * h
    cv.rect(x - tw, sh_y - 0.02 * h, x + tw, hip_y + 0.05 * h, fill=hexc(st.top), r=0.07 * h)
    if st.accent:
        cv.rect(x - tw * 0.15, sh_y + 0.02 * h, x + tw * 0.15, hip_y, fill=hexc(st.accent), r=0.02 * h)
    cv.rect(x - tw, hip_y - 0.02 * h, x + tw, hip_y + 0.07 * h, fill=hexc(st.pants), r=0.03 * h)

    # head + hair
    hx = x + face * 0.02 * h
    if st.hair_style == "long":
        cv.rect(hx - head_r * 1.1, head_y - head_r * 0.6, hx + head_r * 1.1, head_y + head_r * 1.6,
                fill=hexc(st.hair), r=head_r * 0.6)
    cv.circle(hx, head_y, head_r, fill=skin)
    hair = hexc(st.hair)
    if st.hair_style == "curly":
        for i in range(7):
            a = math.pi * (1.05 + i * 0.15)
            cv.circle(hx + math.cos(a) * head_r * 0.85, head_y + math.sin(a) * head_r * 0.85, head_r * 0.42, fill=hair)
    elif st.hair_style in ("short", "long"):
        cv.pieslice(hx - head_r * 1.05, head_y - head_r * 1.12, hx + head_r * 1.05, head_y + head_r * 0.9,
                    180, 360, fill=hair)
        cv.circle(hx - face * head_r * 0.8, head_y - head_r * 0.05, head_r * 0.32, fill=hair)
    elif st.hair_style == "cap":
        cv.pieslice(hx - head_r * 1.05, head_y - head_r * 1.15, hx + head_r * 1.05, head_y + head_r * 0.9,
                    180, 360, fill=hair)
        cv.rect(hx, head_y - head_r * 0.25, hx + face * head_r * 1.5, head_y - head_r * 0.05, fill=hair, r=head_r * 0.1)
    # face
    ex = hx + face * head_r * 0.38
    cv.circle(ex - head_r * 0.22, head_y - head_r * 0.05, head_r * 0.11, fill=ink)
    cv.circle(ex + head_r * 0.22, head_y - head_r * 0.05, head_r * 0.11, fill=ink)
    if st.glasses:
        for gx in (ex - head_r * 0.22, ex + head_r * 0.22):
            cv.circle(gx, head_y - head_r * 0.05, head_r * 0.24, outline=ink, width=head_r * 0.07)
    cv.arc(ex - head_r * 0.3, head_y + head_r * 0.05, ex + head_r * 0.3, head_y + head_r * 0.5, 20, 160, ink,
           head_r * 0.08)
    cv.circle(ex + face * head_r * 0.5, head_y + head_r * 0.25, head_r * 0.13, fill=hexc("#f49a8f", 160))

    # front arm
    sx_f = x + face * 0.10 * h
    shoulder = (sx_f, sh_y + aw * 0.4)
    if reach is not None:
        dx, dy = reach[0] - shoulder[0], reach[1] - shoulder[1]
        dist = math.hypot(dx, dy) or 1
        L = min(dist, arm_len * 1.05)
        hand = (shoulder[0] + dx / dist * L, shoulder[1] + dy / dist * L)
    else:
        af = sw * 0.5 if phase is not None else -0.12 * face
        if wave:
            af = face * (2.4 + 0.35 * math.sin(wave))
        if arms_up:
            af = face * math.pi * 0.85 * arms_up
        hand = (sx_f + math.sin(af) * arm_len, shoulder[1] + math.cos(af) * arm_len)

    if umbrella == "open":
        top = (hand[0], head_y - head_r * 2.6)
        cv.line([hand, top], ink, 0.02 * h)
        cr = 0.42 * h
        cv.pieslice(top[0] - cr, top[1] - cr * 0.55, top[0] + cr, top[1] + cr * 0.55, 180, 360, fill=hexc("#3f7fd9"))
        for i in range(4):
            xx = top[0] - cr + (2 * cr) * (i + 0.5) / 4
            cv.pieslice(xx - cr / 4, top[1] - cr * 0.12, xx + cr / 4, top[1] + cr * 0.12, 0, 180, fill=hexc("#3f7fd9"))
        cv.pieslice(top[0] - cr * 0.35, top[1] - cr * 0.55, top[0] + cr * 0.35, top[1] + cr * 0.55, 180, 360,
                    fill=hexc("#ffd34d"))
        cv.circle(top[0], top[1] - cr * 0.56, 0.02 * h, fill=ink)
    elif umbrella in ("closed", "pointer"):
        if umbrella == "pointer" and reach is not None:
            dx, dy = hand[0] - shoulder[0], hand[1] - shoulder[1]
            dd = math.hypot(dx, dy) or 1
            ux, uy = dx / dd, dy / dd
        else:
            ux, uy = face * 0.25, 0.97
        L = 0.62 * h
        tip = (hand[0] + ux * L, hand[1] + uy * L)
        back = (hand[0] - ux * 0.08 * h, hand[1] - uy * 0.08 * h)
        nx, ny = -uy, ux
        mid = (hand[0] + ux * L * 0.35, hand[1] + uy * L * 0.35)
        cv.poly([(mid[0] + nx * 0.05 * h, mid[1] + ny * 0.05 * h), (tip[0] - ux * 0.12 * h, tip[1] - uy * 0.12 * h),
                 (mid[0] - nx * 0.05 * h, mid[1] - ny * 0.05 * h), (hand[0], hand[1])], fill=hexc("#3f7fd9"))
        cv.line([back, tip], ink, 0.018 * h)
        cv.arc(back[0] - 0.06 * h, back[1] - 0.03 * h, back[0] + 0.02 * h, back[1] + 0.07 * h, 90, 270, ink, 0.02 * h)
        hand_tip = tip
    else:
        hand_tip = hand

    cv.line([shoulder, hand], hexc(st.top), aw)
    cv.circle(hand[0], hand[1], aw * 0.6, fill=skin)
    return hand_tip if umbrella in ("closed", "pointer") else hand


# ---------------------------------------------------------------- overlays (screen space)

def pill(img, cx, cy, text, size=64, fg="#2b2140", bg="#fff6e6", pad=(34, 18), scale=1.0, rot=0.0,
         shadow=True, border=None, anchor="m"):
    if scale <= 0.01:
        return
    f = font(size)
    tw = f.getbbox(text)
    w, h = tw[2] - tw[0] + pad[0] * 2, size + pad[1] * 2
    pad_s = 30
    tile = Image.new("RGBA", (w + pad_s * 2, h + pad_s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    if shadow:
        d.rounded_rectangle([pad_s + 8, pad_s + 12, pad_s + w + 8, pad_s + h + 12], radius=h // 3, fill=(30, 20, 60, 90))
    d.rounded_rectangle([pad_s, pad_s, pad_s + w, pad_s + h], radius=h // 3, fill=hexc(bg),
                        outline=hexc(border) if border else None, width=6 if border else 0)
    d.text((pad_s + w / 2, pad_s + h / 2), text, font=f, fill=hexc(fg), anchor="mm")
    if rot:
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
    if scale != 1.0:
        tile = tile.resize((max(1, int(tile.width * scale)), max(1, int(tile.height * scale))), Image.BICUBIC)
    x = cx - pad_s * scale if anchor == "l" else cx - tile.width / 2
    img.paste(tile, (int(x), int(cy - tile.height / 2)), tile)


def clock_badge(img, cx, cy, hour, minute, label, scale=1.0, night=False):
    if scale <= 0.01:
        return
    S = 2
    w, h = 520, 170
    tile = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    cv = Canvas(tile, 0, 0, S)
    cv.rect(10, 14, w - 6, h - 4, fill=(30, 20, 60, 90), r=70)
    cv.rect(4, 4, w - 12, h - 14, fill=hexc("#2b2140"), r=70)
    ccx, ccy, r = 82, (h - 10) / 2, 58
    cv.circle(ccx, ccy, r, fill=hexc("#fff6e6"))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        cv.circle(ccx + math.sin(a) * r * 0.8, ccy - math.cos(a) * r * 0.8, 4, fill=hexc("#2b2140"))
    ah = (hour % 12 + minute / 60) / 12 * 2 * math.pi
    am = minute / 60 * 2 * math.pi
    cv.line([(ccx, ccy), (ccx + math.sin(ah) * r * 0.5, ccy - math.cos(ah) * r * 0.5)], hexc("#2b2140"), 9)
    cv.line([(ccx, ccy), (ccx + math.sin(am) * r * 0.75, ccy - math.cos(am) * r * 0.75)], hexc("#e2574c"), 6)
    cv.circle(ccx, ccy, 7, fill=hexc("#2b2140"))
    cv.text(165, ccy + 2, label, 78, hexc("#ffd34d"), anchor="lm")
    icon_x = w - 70
    if night:
        cv.circle(icon_x, ccy, 34, fill=hexc("#ffd34d"))
        cv.circle(icon_x + 16, ccy - 12, 30, fill=hexc("#2b2140"))
    else:
        for i in range(8):
            a = i / 8 * 2 * math.pi
            cv.line([(icon_x + math.cos(a) * 34, ccy + math.sin(a) * 34),
                     (icon_x + math.cos(a) * 46, ccy + math.sin(a) * 46)], hexc("#ffd34d"), 7)
        cv.circle(icon_x, ccy, 26, fill=hexc("#ffd34d"))
    tile = tile.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)


def floor_display(img, cx, cy, text, scale=1.0, arrow=0):
    if scale <= 0.01:
        return
    S = 2
    w, h = 300, 150
    tile = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    cv = Canvas(tile, 0, 0, S)
    cv.rect(10, 14, w - 6, h - 4, fill=(30, 20, 60, 90), r=30)
    cv.rect(4, 4, w - 12, h - 14, fill=hexc("#2b2140"), r=30)
    cv.rect(16, 16, w - 24, h - 26, outline=hexc("#d9a441"), width=5, r=22)
    cv.text(w / 2 + (18 if arrow else 0) - 4, h / 2 - 4, text, 84, hexc("#ffd34d"))
    if arrow:
        ax, ay = 62, h / 2 - 5
        col = hexc("#6fe08a")
        if arrow > 0:
            cv.poly([(ax - 22, ay + 12), (ax + 22, ay + 12), (ax, ay - 20)], fill=col)
        else:
            cv.poly([(ax - 22, ay - 12), (ax + 22, ay - 12), (ax, ay + 20)], fill=col)
    tile = tile.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)


def check_icon(img, cx, cy, r, scale=1.0, ok=True):
    if scale <= 0.01:
        return
    S = 3
    size = int(r * 2 + 20)
    tile = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0))
    cv = Canvas(tile, 0, 0, S)
    c = size / 2
    cv.circle(c + 3, c + 5, r, fill=(30, 20, 60, 80))
    cv.circle(c, c, r, fill=hexc("#ffffff"))
    cv.circle(c, c, r * 0.84, fill=hexc("#37b26c" if ok else "#e2574c"))
    if ok:
        cv.line([(c - r * 0.38, c + r * 0.02), (c - r * 0.1, c + r * 0.3), (c + r * 0.42, c - r * 0.3)],
                hexc("#ffffff"), r * 0.18, joint="curve")
    else:
        cv.line([(c - r * 0.3, c - r * 0.3), (c + r * 0.3, c + r * 0.3)], hexc("#ffffff"), r * 0.18)
        cv.line([(c - r * 0.3, c + r * 0.3), (c + r * 0.3, c - r * 0.3)], hexc("#ffffff"), r * 0.18)
    tile = tile.resize((max(1, int(size * scale)), max(1, int(size * scale))), Image.LANCZOS)
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)


def speech_bubble(cv, x, y, r, text, fill="#ffffff", fg="#2b2140"):
    cv.poly([(x - r * 0.3, y + r * 0.7), (x - r * 0.7, y + r * 1.45), (x + r * 0.15, y + r * 0.85)], fill=hexc(fill))
    cv.circle(x, y, r, fill=hexc(fill), outline=hexc("#2b2140"), width=r * 0.06)
    cv.text(x, y + r * 0.05, text, r * 1.25, hexc(fg))


def rain(img, t, density=260, color=(225, 232, 245, 150), speed=2600, seed=7):
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(seed)
    xs = rng.uniform(-200, OUT_W + 200, density)
    ys = rng.uniform(0, OUT_H + 400, density)
    ln = rng.uniform(40, 90, density)
    sp = rng.uniform(0.8, 1.2, density)
    for x, y0, l, s in zip(xs, ys, ln, sp):
        y = (y0 + t * speed * s) % (OUT_H + 400) - 200
        xx = x - (y + 200) * 0.18
        d.line([(xx, y), (xx - l * 0.18, y + l)], fill=color, width=4)


def vignette(img, strength=0.25):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    m = 1 - strength * np.clip(r - 0.6, 0, 1)
    return m[..., None]
