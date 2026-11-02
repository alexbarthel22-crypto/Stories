"""Gemeinsame Zeichen-Bibliothek für die "Heute ist Alex ..."-Serie.

Alles wird mit pycairo auf 1080x1920 gezeichnet. Die Figur ALEX ist hier fest
definiert (ALEX_BASE), damit er in jeder Folge identisch aussieht – nur das
Outfit wechselt je nach Rolle.
"""
import math, random, re
import cairo

W, H, FPS = 1080, 1920, 30
FONT_HEAD = "Inter Display Black"
FONT_BOLD = "Inter Display ExtraBold"
FONT_EMOJI = "Noto Color Emoji"
INK = "#1C1B22"


# ----------------------------------------------------------------- Farben/Math
def rgb(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def shade(h, f):
    """f<1 dunkler, f>1 heller."""
    r, g, b, _ = rgb(h)
    if f < 1:
        r, g, b = r * f, g * f, b * f
    else:
        k = f - 1
        r, g, b = r + (1 - r) * k, g + (1 - g) * k, b + (1 - b) * k
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def src(c, h, a=1.0):
    c.set_source_rgba(*rgb(h, a))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x, s=1.9):
    x = clamp(x)
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def pop(t, t0, d=0.32):
    """Skalierung 0 -> 1 mit Überschwingen ab Zeitpunkt t0."""
    if t < t0:
        return 0.0
    return ease_out_back((t - t0) / d)


def fade(t, t0, d=0.2):
    return clamp((t - t0) / d)


# ----------------------------------------------------------------- Formen
def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def ellipse(c, x, y, rx, ry):
    c.save()
    c.translate(x, y)
    c.scale(rx, ry)
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def fill(c, color, a=1.0):
    src(c, color, a)
    c.fill()


def scaled(c, x, y, s, fn, rot=0.0):
    """Zeichnet fn() skaliert/rotiert um Punkt (x, y)."""
    if s <= 0.001:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.translate(-x, -y)
    fn()
    c.restore()


# ----------------------------------------------------------------- Text
_EMOJI_RE = re.compile(
    "([\U0001F000-\U0001FAFF☀-➿⬀-⯿←-⇿⌀-⏿〰〽㊗㊙]"
    "[️‍\U0001F3FB-\U0001F3FF]*)"
)


def _runs(s):
    out = []
    for part in _EMOJI_RE.split(s):
        if not part:
            continue
        out.append((part, bool(_EMOJI_RE.fullmatch(part))))
    return out


def _font(c, emoji, font, size):
    c.select_font_face(FONT_EMOJI if emoji else font)
    c.set_font_size(size * (0.92 if emoji else 1.0))


def text_width(c, s, size, font=FONT_HEAD):
    w = 0
    for part, emo in _runs(s):
        _font(c, emo, font, size)
        w += c.text_extents(part).x_advance
    return w


def text(c, s, x, y, size, color=INK, font=FONT_HEAD, anchor="c", alpha=1.0):
    """Einzeilig. y = Grundlinien-Mitte (vertikal zentriert auf Versalhöhe)."""
    if size < 0.5:
        return 0
    w = text_width(c, s, size, font)
    if anchor == "c":
        x0 = x - w / 2
    elif anchor == "r":
        x0 = x - w
    else:
        x0 = x
    yb = y + size * 0.36
    for part, emo in _runs(s):
        _font(c, emo, font, size)
        c.move_to(x0, yb + (size * 0.06 if emo else 0))
        src(c, color, alpha)
        c.show_text(part)
        x0 += c.text_extents(part).x_advance
    c.new_path()
    return w


def wrap(c, s, size, max_w, font=FONT_HEAD):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if text_width(c, t, size, font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def text_block(c, s, x, y, size, max_w, color=INK, font=FONT_HEAD, lh=1.15, anchor="c"):
    lines = wrap(c, s, size, max_w, font)
    n = len(lines)
    for i, ln in enumerate(lines):
        text(c, ln, x, y + (i - (n - 1) / 2) * size * lh, size, color, font, anchor)
    return n


def emoji(c, e, x, y, size, rot=0.0, alpha=1.0):
    if size < 0.5 or alpha <= 0.003:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.select_font_face(FONT_EMOJI)
    c.set_font_size(size)
    ext = c.text_extents(e)
    c.move_to(-ext.x_advance / 2, size * 0.36)
    if alpha < 1:
        c.push_group()
        c.show_text(e)
        c.pop_group_to_source()
        c.paint_with_alpha(alpha)
    else:
        c.show_text(e)
    c.new_path()
    c.restore()


# ----------------------------------------------------------------- Hintergrund
def background(c, color, t, rays=0.07, cx=W / 2, cy=1050, nrays=18, speed=0.04):
    fill_rect(c, color)
    if rays > 0:
        c.save()
        c.translate(cx, cy)
        c.rotate(t * speed)
        R = 2600
        for i in range(nrays):
            a0 = (2 * i) * math.pi / nrays
            a1 = (2 * i + 1) * math.pi / nrays
            c.move_to(0, 0)
            c.arc(0, 0, R, a0, a1)
            c.close_path()
        c.set_source_rgba(1, 1, 1, rays)
        c.fill()
        c.restore()
    # Vignette
    g = cairo.RadialGradient(cx, cy, 200, cx, cy, 1400)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.28)
    c.set_source(g)
    c.paint()


def fill_rect(c, color):
    src(c, color)
    c.paint()


def is_dark(color):
    r, g, b, _ = rgb(color)
    return (0.299 * r + 0.587 * g + 0.114 * b) < 0.45


# ----------------------------------------------------------------- UI-Elemente
def clock_pill(c, label, y=118, s=1.0):
    hour = int(label.split(":")[0])
    icon = "🌙" if hour >= 19 or hour < 6 else "☀️"
    def draw():
        w = 230
        rrect(c, W / 2 - w / 2, y - 31, w, 62, 31)
        src(c, "#000000", 0.72)
        c.fill()
        emoji(c, icon, W / 2 - 62, y, 32)
        text(c, label, W / 2 + 22, y, 36, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, y, s, draw)


def title(c, s_txt, y, color, s=1.0, size=70):
    def draw():
        text_block(c, s_txt, W / 2, y, size, 980, color, FONT_HEAD)
    scaled(c, W / 2, y, s, draw)


def caption(c, s_txt, t_since, y=1585):
    """Untertitel-Box wie im Referenzstil: weiß, dunkler Rand, leicht schräg."""
    if not s_txt:
        return
    s_txt = s_txt.upper()
    size = 50
    lines = wrap(c, s_txt, size, 820, FONT_HEAD)
    w = max(text_width(c, ln, size, FONT_HEAD) for ln in lines) + 56
    h = len(lines) * size * 1.12 + 34
    sc = 0.86 + 0.14 * ease_out_back(t_since / 0.14, 2.5)
    def draw():
        c.save()
        c.translate(W / 2, y)
        c.rotate(math.radians(-2.2))
        rrect(c, -w / 2 + 6, -h / 2 + 8, w, h, 16)
        src(c, "#000000", 0.25)
        c.fill()
        rrect(c, -w / 2, -h / 2, w, h, 16)
        fill(c, "#FFFFFF")
        rrect(c, -w / 2, -h / 2, w, h, 16)
        c.set_line_width(5)
        src(c, INK)
        c.stroke()
        for i, ln in enumerate(lines):
            text(c, ln, 0, (i - (len(lines) - 1) / 2) * size * 1.12, size, "#111111", FONT_HEAD)
        c.restore()
    scaled(c, W / 2, y, sc, draw)


def bubble(c, s_txt, x, y, s=1.0, tail=(0, 1), size=40, max_w=560, color="#FFFFFF",
           txt=INK, font=FONT_BOLD, border=True):
    """Sprechblase mit Mittelpunkt (x, y). tail = Richtung des Zipfels."""
    if s <= 0.001:
        return
    lines = wrap(c, s_txt, size, max_w, font)
    w = max(text_width(c, ln, size, font) for ln in lines) + 60
    h = len(lines) * size * 1.18 + 40
    def draw():
        tx, ty = tail
        bx, by = x + tx * w * 0.28, y + ty * h / 2
        for pas in (0, 1):
            c.new_path()
            rrect(c, x - w / 2, y - h / 2, w, h, 26)
            c.move_to(bx - 18, by - ty * 6)
            c.line_to(bx + tx * 30 + 6, by + ty * 34)
            c.line_to(bx + 18, by - ty * 6)
            c.close_path()
            if pas == 0:
                src(c, "#000000", 0.18)
                c.save(); c.translate(5, 7); c.fill(); c.restore()
                c.new_path()
                rrect(c, x - w / 2, y - h / 2, w, h, 26)
                c.move_to(bx - 18, by - ty * 6)
                c.line_to(bx + tx * 30 + 6, by + ty * 34)
                c.line_to(bx + 18, by - ty * 6)
                c.close_path()
                src(c, color)
                c.fill_preserve()
                if border:
                    c.set_line_width(4)
                    src(c, INK)
                    c.stroke()
        rrect(c, x - w / 2 + 3, y - h / 2 + 3, w - 6, h - 6, 24)
        src(c, color)
        c.fill()
        for i, ln in enumerate(lines):
            text(c, ln, x, y + (i - (len(lines) - 1) / 2) * size * 1.18, size, txt, font)
    scaled(c, x, y, s, draw)


def card(c, x, y, w, h, s=1.0, color="#FFFFFF", radius=26, border=True, shadow=True, rot=0.0):
    """Leere Karte, gibt nichts zurück. Inhalt danach mit scaled() zeichnen."""
    def draw():
        if shadow:
            rrect(c, x - w / 2 + 8, y - h / 2 + 12, w, h, radius)
            src(c, "#000000", 0.2)
            c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, radius)
        src(c, color)
        c.fill_preserve()
        if border:
            c.set_line_width(5)
            src(c, INK)
            c.stroke()
        else:
            c.new_path()
    scaled(c, x, y, s, draw, rot)


def name_tag(c, name, x, y, size=24):
    w = text_width(c, name, size, FONT_BOLD) + 22
    rrect(c, x - w / 2, y - size * 0.75, w, size * 1.5, 7)
    src(c, "#2A2A30", 0.9)
    c.fill()
    text(c, name, x, y, size, "#FFFFFF", FONT_BOLD)


def red_flag_stamp(c, x, y, s, label="RED FLAG", rot=-0.18):
    def draw():
        c.save(); c.translate(x, y); c.rotate(rot)
        w = text_width(c, label, 40, FONT_HEAD) + 110
        rrect(c, -w / 2, -38, w, 76, 14)
        fill(c, "#E23B3B")
        rrect(c, -w / 2 + 6, -32, w - 12, 64, 10)
        c.set_line_width(3); src(c, "#FFFFFF", 0.9); c.stroke()
        emoji(c, "🚩", -w / 2 + 44, 0, 40)
        text(c, label, 26, 0, 40, "#FFFFFF", FONT_HEAD)
        c.restore()
    scaled(c, x, y, s, draw)


def phone(c, x, y, w, h, s=1.0, screen="#FFFFFF", rot=0.0):
    """Smartphone-Rahmen; gibt Screen-Rechteck (x0, y0, w, h) zurück."""
    def draw():
        rrect(c, x - w / 2 + 10, y - h / 2 + 14, w, h, 56)
        src(c, "#000000", 0.25); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 56)
        fill(c, "#17171C")
        rrect(c, x - w / 2 + 16, y - h / 2 + 16, w - 32, h - 32, 42)
        fill(c, screen)
        rrect(c, x - 60, y - h / 2 + 30, 120, 26, 13)
        fill(c, "#17171C")
    scaled(c, x, y, s, draw, rot)
    return (x - w / 2 + 16, y - h / 2 + 16, w - 32, h - 32)


# ----------------------------------------------------------------- Figuren
# ALEX – fest definiert, gilt für ALLE Folgen. Nur "top/pants/shoes/extra" wechseln.
ALEX_BASE = dict(
    skin="#F6CDA8", hair="#EDB93F", hair_dark="#C98E25", hair_style="alex",
    glasses=True, freckles=True, eyes="#2F4F7A",
    top="#5B8DEF", top_style="tee", pants="#2F3B52", shoes="#FFFFFF",
)

OUTFIT_PICKME = dict(top="#EFE2C6", top_style="cardigan", inner="#FFFFFF",
                     pants="#9CC0E3", shoes="#FFFFFF", tote=True)


def alex(**kw):
    d = dict(ALEX_BASE)
    d.update(kw)
    return d


def person_spec(seed=0, girl=False, **kw):
    rnd = random.Random(seed)
    skins = ["#F6CDA8", "#E9B48A", "#C98B5E", "#8D5A3B", "#F1C27D"]
    hairs = ["#3B2A20", "#5A3A22", "#1E1A18", "#8A5A2B", "#C4472E", "#2B2B2B"]
    tops = ["#E5534B", "#3E7BDA", "#2FA36B", "#F2B233", "#8E5BE0", "#F07FB0", "#36B5C2", "#555A66"]
    d = dict(skin=rnd.choice(skins), hair=rnd.choice(hairs), hair_style=("long" if girl else "short"),
             glasses=False, freckles=False, eyes="#2A2A2A",
             top=rnd.choice(tops), top_style="tee", pants=rnd.choice(["#2F3B52", "#3C3C46", "#5B6B8A", "#7A5C45"]),
             shoes=rnd.choice(["#FFFFFF", "#222222", "#E9E2D0"]))
    d.update(kw)
    d.setdefault("hair_dark", shade(d["hair"], 0.75))
    if "hair" in kw and "hair_dark" not in kw:
        d["hair_dark"] = shade(d["hair"], 0.75)
    return d


def person(c, x, y, h, spec, t=0.0, expr="happy", pose="idle", prop=None, name=None,
           blink_seed=0, bob=True, look=0.0, flip=False):
    """Zeichnet eine Figur. (x, y) = Mitte zwischen den Füßen, h = Gesamthöhe in px."""
    k = h / 100.0
    by = (math.sin(t * 2 * math.pi * 0.7 + blink_seed) * 0.6) if bob else 0
    c.save()
    c.translate(x, y)
    c.scale(k * (-1 if flip else 1), k)
    sp = spec
    skin = sp["skin"]

    # Schatten
    ellipse(c, 0, 0, 20, 2.6)
    src(c, "#000000", 0.18); c.fill()

    # Beine
    for sx in (-1, 1):
        rrect(c, sx * 5.4 - 4.6, -27 + by * 0.3, 9.2, 25, 3.2)
        fill(c, sp["pants"])
    # Schuhe
    for sx in (-1, 1):
        ellipse(c, sx * 6.2, -2.6, 6.6, 3.3)
        fill(c, sp["shoes"])
        ellipse(c, sx * 6.2, -1.6, 6.6, 1.6)
        fill(c, shade(sp["shoes"], 0.85))

    c.translate(0, by)

    # Tote-Bag (hinter dem Arm, links)
    if sp.get("tote"):
        c.save()
        c.set_line_width(1.3); src(c, "#B8A27A")
        c.move_to(-12, -50); c.line_to(-31, -29); c.stroke()
        c.move_to(-9, -50); c.line_to(-22, -29); c.stroke()
        rrect(c, -35, -30, 16, 18, 1.5)
        fill(c, "#E9DCC0")
        src(c, "#5A4A30")
        c.select_font_face(FONT_HEAD); c.set_font_size(2.4)
        for i, ln in enumerate(["NOT LIKE", "OTHER", "GUYS"]):
            e = c.text_extents(ln)
            c.move_to(-27 - e.x_advance / 2, -24 + i * 3.4); c.show_text(ln)
        c.restore()

    # Oberkörper
    top = sp["top"]
    rrect(c, -15, -54, 30, 30, 7)
    fill(c, top)
    style = sp.get("top_style", "tee")
    if style == "cardigan":
        c.move_to(-3.5, -54); c.line_to(3.5, -54); c.line_to(2.5, -24); c.line_to(-2.5, -24); c.close_path()
        fill(c, sp.get("inner", "#FFFFFF"))
        for yy in (-46, -39, -32):
            c.arc(-4.6, yy, 0.9, 0, 2 * math.pi); fill(c, shade(top, 0.62))
        # Strickrippen unten
        rrect(c, -15, -27, 30, 3.2, 1.5); fill(c, shade(top, 0.9))
    elif style == "hoodie":
        rrect(c, -8, -38, 16, 9, 3); fill(c, shade(top, 0.85))
        c.move_to(-3, -53); c.line_to(-3.6, -45); c.set_line_width(0.8); src(c, "#FFFFFF"); c.stroke()
        c.move_to(3, -53); c.line_to(3.6, -45); c.stroke()
    elif style == "suit":
        c.move_to(-4, -54); c.line_to(4, -54); c.line_to(0, -40); c.close_path(); fill(c, "#FFFFFF")
        c.move_to(-1.3, -52); c.line_to(1.3, -52); c.line_to(0.8, -38); c.line_to(0, -36); c.line_to(-0.8, -38); c.close_path()
        fill(c, sp.get("tie", "#C0392B"))
    else:
        c.arc(0, -54, 4.6, 0, math.pi); fill(c, shade(top, 0.82))
    # Gürtel/Saum
    rrect(c, -15, -26, 30, 2.5, 1); fill(c, shade(sp["pants"], 0.8))

    # Arme
    arms = {"idle": (14, 14), "wave": (14, 155 + 18 * math.sin(t * 9)), "phone": (14, 150),
            "shrug": (115, 115), "up": (168, 168), "point": (14, 95), "hips": (35, 35),
            "guitar": (-55, -35), "cross": (-60, -60), "facepalm": (14, -150)}.get(pose, (14, 14))
    hand_pos = {}
    for side, ang in ((-1, arms[0]), (1, arms[1])):
        a = math.radians(ang)
        sx, sy = side * 14.2, -50.5
        dx, dy = side * math.sin(a), math.cos(a)
        L = 21
        c.save()
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_width(7.4)
        src(c, shade(top, 0.92))
        c.move_to(sx, sy); c.line_to(sx + dx * L, sy + dy * L); c.stroke()
        c.restore()
        hx, hy = sx + dx * (L + 2.5), sy + dy * (L + 2.5)
        c.arc(hx, hy, 3.9, 0, 2 * math.pi); fill(c, skin)
        hand_pos[side] = (hx, hy)

    # Hals
    rrect(c, -4.2, -58, 8.4, 6, 2); fill(c, shade(skin, 0.88))

    hs = sp.get("hair_style", "short")
    hair, hdark = sp["hair"], sp.get("hair_dark", shade(sp["hair"], 0.75))
    hy0 = -73
    # Haare hinten (lang)
    if hs in ("long", "bun"):
        rrect(c, -20.5, hy0 - 16, 41, 40, 14); fill(c, hdark)
    # Ohren
    for sx in (-1, 1):
        c.arc(sx * 17.6, hy0 + 1, 3.6, 0, 2 * math.pi); fill(c, shade(skin, 0.94))
    # Kopf
    ellipse(c, 0, hy0, 17.6, 18.6)
    fill(c, skin)

    # Gesicht
    blink = 1.0
    ph = (t + blink_seed * 1.37) % 3.7
    if ph < 0.12:
        blink = max(0.08, abs(ph - 0.06) / 0.06)
    ex = look * 1.6
    eye_y = hy0 + 1.5
    big = expr in ("puppy",)
    for sx in (-1, 1):
        c.save()
        c.translate(sx * 6.4 + ex, eye_y)
        c.scale(1, blink)
        r = 2.9 if big else 2.15
        c.arc(0, 0, r, 0, 2 * math.pi); fill(c, "#1A1A1A")
        if blink > 0.5:
            c.arc(0.8, -0.8, 0.85 if big else 0.6, 0, 2 * math.pi); fill(c, "#FFFFFF")
            if big:
                c.arc(-0.9, 0.9, 0.45, 0, 2 * math.pi); fill(c, "#FFFFFF")
        c.restore()
    # Augenbrauen
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(1.5)
    src(c, hdark if sp.get("glasses") else shade(hair, 0.8))
    for sx in (-1, 1):
        if expr == "angry":
            c.move_to(sx * 9.5, eye_y - 8.5); c.line_to(sx * 3.2, eye_y - 6.2)
        elif expr in ("sad", "puppy"):
            c.move_to(sx * 9.2, eye_y - 6.6); c.line_to(sx * 3.4, eye_y - 8.6)
        elif expr == "smug":
            c.move_to(sx * 9.2, eye_y - (8.8 if sx > 0 else 7.6)); c.line_to(sx * 3.6, eye_y - (8.0 if sx > 0 else 7.8))
        else:
            c.move_to(sx * 9.4, eye_y - 7.4); c.curve_to(sx * 7.5, eye_y - 9.0, sx * 5, eye_y - 9.0, sx * 3.4, eye_y - 7.8)
        c.stroke()
    # Wangen + Sommersprossen
    for sx in (-1, 1):
        ellipse(c, sx * 11.2, hy0 + 7.2, 3.2, 1.9)
        src(c, "#FF6F7D", 0.42 if expr != "angry" else 0.8); c.fill()
        if sp.get("freckles"):
            for (fx, fy) in ((9.0, 4.6), (11.2, 5.4), (10.0, 6.6), (12.6, 4.2)):
                c.arc(sx * fx, hy0 + fy, 0.42, 0, 2 * math.pi); src(c, "#B5764A", 0.85); c.fill()
    # Nase
    c.set_line_width(1.0); src(c, shade(skin, 0.78))
    c.move_to(-0.8, hy0 + 4.2); c.curve_to(0, hy0 + 5.6, 1.2, hy0 + 5.4, 1.4, hy0 + 4.4); c.stroke()
    # Mund
    my = hy0 + 10.0
    if expr in ("happy", "talk"):
        c.move_to(-5.2, my - 0.6)
        c.curve_to(-3.5, my + 5.2, 3.5, my + 5.2, 5.2, my - 0.6)
        c.close_path(); fill(c, "#7A2B2B")
        c.move_to(-4.4, my - 0.3); c.line_to(4.4, my - 0.3); c.line_to(3.8, my + 0.9); c.line_to(-3.8, my + 0.9); c.close_path()
        fill(c, "#FFFFFF")
        ellipse(c, 0, my + 2.9, 2.4, 1.0); fill(c, "#E86A7A")
    elif expr == "smug":
        c.set_line_width(1.5); src(c, "#7A2B2B")
        c.move_to(-4.2, my + 0.8); c.curve_to(-1, my + 2.4, 2.5, my + 1.8, 5.0, my - 1.6); c.stroke()
    elif expr in ("sad",):
        c.set_line_width(1.5); src(c, "#7A2B2B")
        c.move_to(-4, my + 2.6); c.curve_to(-2, my - 0.2, 2, my - 0.2, 4, my + 2.6); c.stroke()
    elif expr == "puppy":
        c.set_line_width(1.3); src(c, "#7A2B2B")
        c.move_to(-3.2, my + 1.6); c.curve_to(-1.6, my + 0.2, -0.4, my + 0.2, 0, my + 1.2)
        c.curve_to(0.4, my + 0.2, 1.6, my + 0.2, 3.2, my + 1.6); c.stroke()
    elif expr == "angry":
        rrect(c, -4.6, my - 0.4, 9.2, 3.6, 1.4); fill(c, "#7A2B2B")
        rrect(c, -4.0, my - 0.2, 8.0, 1.3, 0.6); fill(c, "#FFFFFF")
    elif expr == "shock":
        ellipse(c, 0, my + 1.4, 2.6, 3.2); fill(c, "#7A2B2B")
    elif expr == "cringe":
        rrect(c, -5, my - 0.6, 10, 3.8, 1.6); fill(c, "#FFFFFF")
        c.set_line_width(0.6); src(c, "#7A2B2B")
        rrect(c, -5, my - 0.6, 10, 3.8, 1.6); c.stroke()
        for xx in (-2.5, 0, 2.5):
            c.move_to(xx, my - 0.6); c.line_to(xx, my + 3.2); c.stroke()
    else:
        c.set_line_width(1.5); src(c, "#7A2B2B")
        c.move_to(-3, my + 0.8); c.line_to(3, my + 0.8); c.stroke()

    # Haare vorne
    if hs == "alex":
        # blonde Tolle mit Seitenscheitel und Locke nach rechts
        c.move_to(-17.9, hy0 + 1)
        c.curve_to(-19.5, hy0 - 10, -15, hy0 - 19, -7, hy0 - 21)
        c.curve_to(-3, hy0 - 27.5, 8, hy0 - 28, 14, hy0 - 23)
        c.curve_to(19.5, hy0 - 19.5, 20.5, hy0 - 11, 18.4, hy0 - 2)
        c.curve_to(17.2, hy0 - 6, 16.4, hy0 - 9, 14.2, hy0 - 11.2)
        c.curve_to(10, hy0 - 9.2, 4, hy0 - 10.8, 0.5, hy0 - 13.4)
        c.curve_to(-4, hy0 - 10.5, -10, hy0 - 10.4, -14.5, hy0 - 8.5)
        c.curve_to(-15.8, hy0 - 5.8, -16.6, hy0 - 2, -17.9, hy0 + 1)
        c.close_path()
        fill(c, hair)
        # Schattierung + Strähnen
        c.set_line_width(1.1); src(c, hdark)
        c.move_to(-9, hy0 - 19); c.curve_to(-4, hy0 - 22, 2, hy0 - 22, 7, hy0 - 18); c.stroke()
        c.move_to(-12, hy0 - 13.5); c.curve_to(-7, hy0 - 17, 0, hy0 - 17, 4, hy0 - 15); c.stroke()
        c.move_to(9, hy0 - 22.5); c.curve_to(13, hy0 - 21, 16, hy0 - 17, 16.6, hy0 - 12); c.stroke()
        c.set_line_width(1.6); src(c, "#FFFFFF", 0.45)
        c.move_to(-5, hy0 - 22.6); c.curve_to(-1, hy0 - 24.8, 4, hy0 - 25.0, 8, hy0 - 23.6); c.stroke()
    elif hs == "short":
        c.move_to(-18, hy0 - 1)
        c.curve_to(-19, hy0 - 16, -9, hy0 - 22, 0, hy0 - 21.5)
        c.curve_to(9, hy0 - 22, 19, hy0 - 16, 18, hy0 - 1)
        c.curve_to(16.5, hy0 - 8, 14, hy0 - 10, 10, hy0 - 10.5)
        c.curve_to(4, hy0 - 9, -4, hy0 - 12, -10, hy0 - 10.5)
        c.curve_to(-14, hy0 - 10, -16.5, hy0 - 8, -18, hy0 - 1)
        c.close_path(); fill(c, hair)
    elif hs == "cap":
        c.move_to(-18.5, hy0 - 4); c.curve_to(-18, hy0 - 22, 18, hy0 - 22, 18.5, hy0 - 4); c.close_path()
        fill(c, sp.get("cap", "#E5534B"))
        rrect(c, -2, hy0 - 8, 26, 4.5, 2); fill(c, shade(sp.get("cap", "#E5534B"), 0.8))
    elif hs in ("long", "bun"):
        c.move_to(-19, hy0 + 8)
        c.curve_to(-21, hy0 - 16, -8, hy0 - 22, 2, hy0 - 21)
        c.curve_to(14, hy0 - 21, 21, hy0 - 12, 19, hy0 + 8)
        c.curve_to(17, hy0 - 2, 15, hy0 - 8, 9, hy0 - 11)
        c.curve_to(3, hy0 - 9, -6, hy0 - 12, -12, hy0 - 9)
        c.curve_to(-16, hy0 - 6, -17.5, hy0, -19, hy0 + 8)
        c.close_path(); fill(c, hair)
        if hs == "bun":
            c.arc(0, hy0 - 23, 7, 0, 2 * math.pi); fill(c, hair)

    # Brille
    if sp.get("glasses"):
        c.set_line_width(1.25)
        src(c, "#2A2A2E")
        for sx in (-1, 1):
            c.new_sub_path(); c.arc(sx * 6.4, eye_y, 5.0, 0, 2 * math.pi)
        c.stroke()
        for sx in (-1, 1):
            c.new_sub_path(); c.arc(sx * 6.4, eye_y, 4.4, 0, 2 * math.pi)
        src(c, "#FFFFFF", 0.12); c.fill()
        src(c, "#2A2A2E")
        c.move_to(-1.6, eye_y - 0.6); c.curve_to(-0.6, eye_y - 1.8, 0.6, eye_y - 1.8, 1.6, eye_y - 0.6); c.stroke()
        c.move_to(-11.4, eye_y - 1); c.line_to(-17.2, eye_y - 2.2); c.stroke()
        c.move_to(11.4, eye_y - 1); c.line_to(17.2, eye_y - 2.2); c.stroke()

    # Requisite in der rechten Hand
    if prop:
        hx, hy = hand_pos[1]
        if pose == "phone":
            emoji(c, prop, hx + 1, hy - 6, 15, rot=-0.15)
        elif pose == "guitar":
            emoji(c, prop, 1, -36, 34, rot=0.0)
        else:
            emoji(c, prop, hx + 7, hy - 3, 15, rot=0.12)
    c.restore()

    if name:
        name_tag(c, name, x, y - h * 1.035 + by * k, size=max(16, int(h * 0.052)))


# ----------------------------------------------------------------- Partikel
def burst(c, t, t0, items, cx, cy, n=16, seed=3, dist=520, life=1.4, size=70):
    if t < t0 or t > t0 + life + 0.2:
        return
    rnd = random.Random(seed)
    u = (t - t0)
    for i in range(n):
        ang = (i / n) * 2 * math.pi + rnd.uniform(-0.2, 0.2)
        d = dist * rnd.uniform(0.6, 1.1) * ease_out_cubic(u / (life * 0.6))
        x = cx + math.cos(ang) * d
        y = cy + math.sin(ang) * d + 140 * (u / life) ** 2
        rot = rnd.uniform(-1, 1) * u * 3
        a = clamp(1 - (u - life * 0.6) / (life * 0.4))
        s = size * rnd.uniform(0.75, 1.2) * min(1, u / 0.12)
        emoji(c, items[i % len(items)], x, y, s, rot, a)


def sparkle_lines(c, t, t0, cx, cy, n=12, color="#FFFFFF", r0=120, r1=330, d=0.45):
    if t < t0 or t > t0 + d:
        return
    u = (t - t0) / d
    c.save()
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(14 * (1 - u))
    src(c, color, 1 - u)
    for i in range(n):
        a = i / n * 2 * math.pi
        ra = r0 + (r1 - r0) * ease_out_cubic(u)
        rb = ra + 70 * (1 - u)
        c.move_to(cx + math.cos(a) * ra, cy + math.sin(a) * ra)
        c.line_to(cx + math.cos(a) * rb, cy + math.sin(a) * rb)
    c.stroke()
    c.restore()
