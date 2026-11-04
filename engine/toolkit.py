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

# TikTok UI safe zones for 1080x1920 (search bar on top, icon column right, caption/comments bottom)
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, SAFE_LEFT = 220, 1480, 940, 40
SAFE_RIGHT_Y = (760, 1480)
UI_LOG = []          # (label, x0, y0, x1, y1) of every screen-space UI element drawn


def log_ui(label, x0, y0, x1, y1):
    UI_LOG.append((label, x0, y0, x1, y1))


def safe_violation(x0, y0, x1, y1):
    v = []
    if y0 < SAFE_TOP:
        v.append("top")
    if y1 > SAFE_BOTTOM:
        v.append("bottom")
    if x1 > SAFE_RIGHT and y1 > SAFE_RIGHT_Y[0] and y0 < SAFE_RIGHT_Y[1]:
        v.append("right")
    if x0 < SAFE_LEFT:
        v.append("left")
    return v


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
        self.d.ellipse([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=fill, outline=outline,
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
        self.d.pieslice([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], a0, a1, fill=fill)

    def arc(self, x0, y0, x1, y1, a0, a1, fill, width=1):
        a, b = self.p(x0, y0), self.p(x1, y1)
        self.d.arc([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], a0, a1, fill=fill,
                   width=self.w(width))

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
    """Character look. Proportions are fractions of the total height h."""

    def __init__(self, h, skin, hair, top, pants, shoes="#ffffff", hair_style="short",
                 head=None, glasses=False, accent=None, under="#ffffff", leg=0.45, torso=0.30,
                 arm=0.36, width=0.13, beard=False, sole="#f4f4f4", shoe_accent=None, brows=None):
        self.h, self.skin, self.hair, self.top = h, skin, hair, top
        self.pants, self.shoes, self.hair_style = pants, shoes, hair_style
        self.glasses, self.accent, self.under = glasses, accent, under
        self.leg, self.torso, self.arm, self.width = leg, torso, arm, width
        self.head = head if head else (1 - leg - torso - 0.03) / 2
        self.beard, self.sole, self.shoe_accent = beard, sole, shoe_accent
        self.brows = brows or hair


def _shade(c, f):
    return mix(c, (20, 16, 40), f)


def draw_person(cv, x, y, st, phase=None, face=1, reach=None, umbrella=None, bounce=0.0,
                wave=0.0, h=None, arms_up=0.0, arm_scale=1.0, lean=0.0, blink=False, talk=0.0, cup=None):
    """Flat-vector person (3/4 view) standing with feet at (x, y).

    phase: walk-cycle phase in radians (None = standing)
    reach: (tx, ty) world point the front hand reaches towards
    umbrella: None | 'open' | 'closed' | 'pointer' (closed, extends from reaching hand)
    lean: shift of the upper body in px (sway); blink: eyes closed; talk: 0..1 mouth opening;
    cup: colour of a drink glass held in the front hand (None = no glass).
    returns the front hand position (umbrella tip for 'closed'/'pointer').
    """
    h = h or st.h
    x = x + lean
    y = y - bounce
    f = face
    ink = hexc("#22243a")
    skin = hexc(st.skin)
    skin_d = _shade(skin, 0.18)
    top = hexc(st.top)
    top_d = _shade(top, 0.22)
    pants = hexc(st.pants)
    pants_d = _shade(pants, 0.25)
    hair = hexc(st.hair)

    leg_len = st.leg * h
    hip_y = y - leg_len
    sh_y = hip_y - st.torso * h
    head_r = st.head * h
    head_y = sh_y - 0.03 * h - head_r * 0.92
    tw = st.width * h
    lw = max(0.085 * h, tw * 0.62)
    arm_len = st.arm * h * arm_scale
    aw = lw * 0.78
    sw = math.sin(phase) if phase is not None else 0.0

    # ---------- arms (back first)
    sx_b = x - f * tw * 0.72
    ab = -sw * 0.45 if phase is not None else 0.10 * f
    if arms_up:
        ab = -f * (math.pi * 0.85 * arms_up)
    hb = (sx_b + math.sin(ab) * arm_len, sh_y + aw * 0.5 + math.cos(ab) * arm_len)
    cv.line([(sx_b, sh_y + aw * 0.5), hb], top_d, aw)
    cv.circle(hb[0], hb[1], aw * 0.52, fill=skin_d)

    # ---------- legs + sneakers
    for sgn, back in ((-1, True), (1, False)):
        a = sgn * sw * 0.42
        hx = x - lean + sgn * tw * 0.32 * (0.6 if back else 1)
        fx, fy = hx + math.sin(a) * leg_len, hip_y + math.cos(a) * leg_len
        col = pants_d if back else pants
        cv.line([(hx, hip_y), (fx, fy - lw * 0.45)], col, lw)
        # cuff
        cv.line([(fx - lw * 0.48, fy - lw * 0.55), (fx + lw * 0.48, fy - lw * 0.55)], _shade(col, 0.15), lw * 0.18,
                cap=False)
        # sneaker: upper + sole
        L = lw * 1.25
        x0, x1 = (fx - L * 0.45, fx + L) if f > 0 else (fx - L, fx + L * 0.45)
        shoe = hexc(st.shoes) if not back else _shade(hexc(st.shoes), 0.12)
        cv.rect(x0, fy - lw * 0.62, x1, fy - lw * 0.05, fill=shoe, r=lw * 0.32)
        cv.rect(x0 - lw * 0.04, fy - lw * 0.18, x1 + lw * 0.04, fy + lw * 0.05, fill=hexc(st.sole), r=lw * 0.08)
        if st.shoe_accent:
            cx_ = (x0 + x1) / 2
            cv.line([(cx_ - lw * 0.25, fy - lw * 0.3), (cx_ + lw * 0.25, fy - lw * 0.45)], hexc(st.shoe_accent),
                    lw * 0.14)

    # ---------- torso: jacket over shirt
    hip_w = tw * 0.92
    cv.poly([(x - tw, sh_y + tw * 0.25), (x + tw, sh_y + tw * 0.25), (x + hip_w, hip_y + 0.03 * h),
             (x - hip_w, hip_y + 0.03 * h)], fill=top)
    cv.circle(x - tw + tw * 0.25, sh_y + tw * 0.25, tw * 0.25, fill=top)
    cv.circle(x + tw - tw * 0.25, sh_y + tw * 0.25, tw * 0.25, fill=top)
    cv.rect(x - tw * 0.75, sh_y, x + tw * 0.75, sh_y + tw * 0.4, fill=top, r=tw * 0.2)
    # shirt visible in the open jacket (shifted to the facing side)
    cx_ = x + f * tw * 0.18
    cv.poly([(cx_ - tw * 0.26, sh_y + tw * 0.05), (cx_ + tw * 0.26, sh_y + tw * 0.05),
             (cx_ + tw * 0.22, hip_y - 0.01 * h), (cx_ - tw * 0.22, hip_y - 0.01 * h)], fill=hexc(st.under))
    # jacket shading on the back side + hem band
    cv.poly([(x - f * tw, sh_y + tw * 0.25), (x - f * tw * 0.55, sh_y + tw * 0.25),
             (x - f * hip_w * 0.6, hip_y + 0.03 * h), (x - f * hip_w, hip_y + 0.03 * h)], fill=top_d)
    if st.accent:
        cv.rect(x - hip_w, hip_y - 0.02 * h, x + hip_w, hip_y + 0.035 * h, fill=hexc(st.accent), r=0.012 * h)
    # belt / waist
    cv.rect(x - hip_w * 0.95, hip_y + 0.02 * h, x + hip_w * 0.95, hip_y + 0.05 * h, fill=pants_d, r=0.01 * h)

    # ---------- neck + head
    cv.rect(x - head_r * 0.28, sh_y - 0.05 * h, x + head_r * 0.28, sh_y + tw * 0.15, fill=skin_d, r=head_r * 0.1)
    hx = x + f * head_r * 0.08
    if st.hair_style == "long":   # hair behind the head
        cv.rect(hx - head_r * 1.08, head_y - head_r * 0.5, hx + head_r * 1.08, head_y + head_r * 1.45,
                fill=_shade(hair, 0.1), r=head_r * 0.7)
    has_hair = st.hair_style in ("quiff", "short", "long")
    # ear (back side)
    ear_x = hx - f * head_r * 0.9
    cv.ellipse(ear_x - head_r * 0.2, head_y - head_r * 0.08, ear_x + head_r * 0.2, head_y + head_r * 0.36, fill=skin_d)
    # hair mass (skull), then the face on top of it -> curved hairline
    if has_hair:
        cv.ellipse(hx - head_r * 1.0, head_y - head_r * 1.1, hx + head_r * 1.0, head_y + head_r * 0.62, fill=hair)
        cv.ellipse(ear_x - head_r * 0.2, head_y - head_r * 0.08, ear_x + head_r * 0.2, head_y + head_r * 0.36,
                   fill=skin_d)
    fcx = hx + f * head_r * 0.12
    top_face = head_y - (head_r * 0.62 if has_hair else head_r)
    cv.ellipse(fcx - head_r * 0.86, top_face, fcx + head_r * 0.9, head_y + head_r * 1.02, fill=skin)
    # jaw/chin to the facing side
    cv.ellipse(fcx + f * head_r * 0.05 - head_r * 0.68, head_y + head_r * 0.05, fcx + f * head_r * 0.05 + head_r * 0.72,
               head_y + head_r * 1.06, fill=skin)
    if st.beard:
        cv.pieslice(fcx - head_r * 0.82, head_y - head_r * 0.3, fcx + head_r * 0.86, head_y + head_r * 1.12, 15, 165,
                    fill=hair + (60,))
    if st.hair_style == "quiff":
        # swept-up fringe over the forehead, towards the facing side
        cv.poly([(hx - f * head_r * 0.75, head_y - head_r * 0.7), (hx - f * head_r * 0.2, head_y - head_r * 1.28),
                 (hx + f * head_r * 0.55, head_y - head_r * 1.36), (hx + f * head_r * 1.02, head_y - head_r * 1.0),
                 (hx + f * head_r * 0.92, head_y - head_r * 0.62), (hx + f * head_r * 0.35, head_y - head_r * 0.78),
                 (hx - f * head_r * 0.15, head_y - head_r * 0.6)], fill=hair)
        hl = mix(hair, (255, 255, 255), 0.22)
        cv.line([(hx - f * head_r * 0.25, head_y - head_r * 1.1), (hx + f * head_r * 0.55, head_y - head_r * 1.2)],
                hl, head_r * 0.07)
        cv.line([(hx - f * head_r * 0.05, head_y - head_r * 0.95), (hx + f * head_r * 0.7, head_y - head_r * 1.02)],
                hl, head_r * 0.05)
    elif st.hair_style == "long":
        cv.pieslice(fcx - head_r * 0.95, head_y - head_r * 1.0, fcx + head_r * 0.95, head_y + head_r * 0.1,
                    200 if f > 0 else 240, 300 if f > 0 else 340, fill=hair)
    # face features (shifted to the facing side)
    fx_ = hx + f * head_r * 0.32
    eye_y = head_y + head_r * 0.02
    for k, ex in enumerate((fx_ - head_r * 0.30, fx_ + head_r * 0.30)):
        sc = 0.85 if (k == 0) == (f > 0) else 1.0   # far eye a bit smaller
        if blink:
            cv.arc(ex - head_r * 0.15 * sc, eye_y - head_r * 0.1, ex + head_r * 0.15 * sc, eye_y + head_r * 0.12, 20, 160,
                   ink, head_r * 0.06)
        else:
            cv.ellipse(ex - head_r * 0.15 * sc, eye_y - head_r * 0.19, ex + head_r * 0.15 * sc, eye_y + head_r * 0.17,
                       fill=hexc("#ffffff"))
            cv.circle(ex + f * head_r * 0.04, eye_y + head_r * 0.01, head_r * 0.10 * sc, fill=ink)
            cv.circle(ex + f * head_r * 0.07, eye_y - head_r * 0.04, head_r * 0.035, fill=hexc("#ffffff"))
        cv.line([(ex - head_r * 0.16, eye_y - head_r * 0.32), (ex + head_r * 0.14, eye_y - head_r * 0.36)],
                hexc(st.brows), head_r * 0.08)
        if st.glasses:
            cv.circle(ex, eye_y, head_r * 0.26, outline=ink, width=head_r * 0.06)
    if st.glasses:
        cv.line([(fx_ - head_r * 0.05, eye_y), (fx_ + head_r * 0.05, eye_y)], ink, head_r * 0.06)
    # nose + mouth + cheek
    cv.ellipse(fx_ + f * head_r * 0.06 - head_r * 0.1, eye_y + head_r * 0.2, fx_ + f * head_r * 0.06 + head_r * 0.12,
               eye_y + head_r * 0.38, fill=skin_d)
    mo = clamp(talk) * head_r * 0.14
    cv.pieslice(fx_ - head_r * 0.24, eye_y + head_r * 0.44 - mo * 0.3, fx_ + head_r * 0.28, eye_y + head_r * 0.76 + mo, 0,
                180, fill=hexc("#8a3b3b"))
    cv.pieslice(fx_ - head_r * 0.18, eye_y + head_r * 0.45, fx_ + head_r * 0.22, eye_y + head_r * 0.58, 0, 180,
                fill=hexc("#ffffff"))
    cv.circle(fx_ - f * head_r * 0.52, eye_y + head_r * 0.34, head_r * 0.13, fill=hexc("#ff8a7a", 70))

    # ---------- front arm
    sx_f = x + f * tw * 0.72
    shoulder = (sx_f, sh_y + aw * 0.5)
    if reach is not None:
        dx, dy = reach[0] - shoulder[0], reach[1] - shoulder[1]
        dist = math.hypot(dx, dy) or 1
        L = min(dist, arm_len * 1.05)
        hand = (shoulder[0] + dx / dist * L, shoulder[1] + dy / dist * L)
    else:
        af = sw * 0.45 if phase is not None else -0.10 * f
        if wave:
            af = f * (2.4 + 0.35 * math.sin(wave))
        if arms_up:
            af = f * math.pi * 0.85 * arms_up
        hand = (sx_f + math.sin(af) * arm_len, shoulder[1] + math.cos(af) * arm_len)

    hand_tip = hand
    if umbrella == "open":
        tip_top = (hand[0], head_y - head_r * 2.3)
        cv.line([hand, tip_top], ink, 0.02 * h)
        cr = 0.42 * h
        canopy, canopy2 = hexc("#2f6fd6"), hexc("#ffcf3f")
        cv.pieslice(tip_top[0] - cr, tip_top[1] - cr * 0.55, tip_top[0] + cr, tip_top[1] + cr * 0.55, 180, 360,
                    fill=canopy)
        for i in range(4):
            xx = tip_top[0] - cr + (2 * cr) * (i + 0.5) / 4
            cv.pieslice(xx - cr / 4, tip_top[1] - cr * 0.12, xx + cr / 4, tip_top[1] + cr * 0.12, 0, 180,
                        fill=canopy if i % 2 == 0 else canopy2)
        cv.pieslice(tip_top[0] - cr * 0.33, tip_top[1] - cr * 0.55, tip_top[0] + cr * 0.33, tip_top[1] + cr * 0.55,
                    180, 360, fill=canopy2)
        cv.circle(tip_top[0], tip_top[1] - cr * 0.56, 0.02 * h, fill=ink)
    elif umbrella in ("closed", "pointer"):
        if umbrella == "pointer" and reach is not None:
            dx, dy = hand[0] - shoulder[0], hand[1] - shoulder[1]
            dd = math.hypot(dx, dy) or 1
            ux, uy = dx / dd, dy / dd
        else:
            ux, uy = f * 0.25, 0.97
        L = 0.62 * h
        tip = (hand[0] + ux * L, hand[1] + uy * L)
        back = (hand[0] - ux * 0.08 * h, hand[1] - uy * 0.08 * h)
        nx, ny = -uy, ux
        mid = (hand[0] + ux * L * 0.35, hand[1] + uy * L * 0.35)
        cv.poly([(mid[0] + nx * 0.05 * h, mid[1] + ny * 0.05 * h), (tip[0] - ux * 0.12 * h, tip[1] - uy * 0.12 * h),
                 (mid[0] - nx * 0.05 * h, mid[1] - ny * 0.05 * h), (hand[0], hand[1])], fill=hexc("#2f6fd6"))
        cv.line([back, tip], ink, 0.018 * h)
        cv.arc(back[0] - 0.06 * h, back[1] - 0.03 * h, back[0] + 0.02 * h, back[1] + 0.07 * h, 90, 270, ink, 0.02 * h)
        hand_tip = tip

    cv.line([shoulder, hand], top, aw)
    if st.accent:  # cuff
        dx, dy = hand[0] - shoulder[0], hand[1] - shoulder[1]
        dd = math.hypot(dx, dy) or 1
        c0 = (hand[0] - dx / dd * aw * 0.9, hand[1] - dy / dd * aw * 0.9)
        cv.line([c0, (hand[0] - dx / dd * aw * 0.45, hand[1] - dy / dd * aw * 0.45)], hexc(st.accent), aw, cap=False)
    cv.circle(hand[0], hand[1], aw * 0.56, fill=skin)
    if cup:   # drink glass in the hand
        gh, gw = 0.09 * h, 0.035 * h
        cx, cy = hand[0] + f * aw * 0.2, hand[1]
        cv.poly([(cx - gw, cy - gh * 0.75), (cx + gw, cy - gh * 0.75), (cx + gw * 0.75, cy + gh * 0.25),
                 (cx - gw * 0.75, cy + gh * 0.25)], fill=(230, 240, 248, 170))
        cv.poly([(cx - gw * 0.9, cy - gh * 0.35), (cx + gw * 0.9, cy - gh * 0.35), (cx + gw * 0.72, cy + gh * 0.22),
                 (cx - gw * 0.72, cy + gh * 0.22)], fill=hexc(cup))
        cv.circle(cx + gw * 0.7, cy - gh * 0.75, gw * 0.45, fill=hexc("#f0a03c"))
        cv.circle(hand[0], hand[1], aw * 0.5, fill=skin)
    return hand_tip


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
    if scale > 0.6:
        m = pad_s * scale
        log_ui("pill:" + text, x + m, cy - tile.height / 2 + m, x + tile.width - m, cy + tile.height / 2 - m)


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
    if scale > 0.6:
        log_ui("clock:"+label+"", cx - tile.width / 2, cy - tile.height / 2, cx + tile.width / 2, cy + tile.height / 2)


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
    if scale > 0.6:
        log_ui("floor:"+text+"", cx - tile.width / 2, cy - tile.height / 2, cx + tile.width / 2, cy + tile.height / 2)


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
    if scale > 0.6:
        log_ui("check", cx - tile.width / 2, cy - tile.height / 2, cx + tile.width / 2, cy + tile.height / 2)


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


def anchors(timing, keys):
    """Map script-line prefixes to (starts, ends). Lines missing from timing collapse onto the next
    present line, so scene code keeps working when a line is removed from the script."""
    S, E = [None] * len(keys), [None] * len(keys)
    for i, k in enumerate(keys):
        for x in timing:
            if x["text"].startswith(k):
                S[i], E[i] = x["start"], x["end"]
                break
    nxt = timing[-1]["end"]
    for i in range(len(keys) - 1, -1, -1):
        if S[i] is None:
            S[i] = E[i] = nxt
        nxt = S[i]
    return S, E
