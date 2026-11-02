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
    glasses=False, freckles=True, eyes="#3B7BC8",
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


def _grad(c, color, y0, y1, top=1.12, bottom=0.9, x0=0, x1=0):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    g.add_color_stop_rgba(0, *rgb(shade(color, top)))
    g.add_color_stop_rgba(1, *rgb(shade(color, bottom)))
    return g


def _fill_line(c, color, y0, y1, lw=0.9, top=1.1, bottom=0.88, line=0.66):
    """Füllt den aktuellen Pfad mit Verlauf und zieht eine farbige Kontur."""
    c.set_source(_grad(c, color, y0, y1, top, bottom))
    c.fill_preserve()
    c.set_line_width(lw)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    src(c, shade(color, line))
    c.stroke()


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
    skin_line = shade(skin, 0.7)
    c.set_line_cap(cairo.LINE_CAP_ROUND)

    # Bodenschatten
    g = cairo.RadialGradient(0, 0, 2, 0, 0, 22)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.28)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.save(); c.scale(1, 0.16); c.arc(0, 0, 22, 0, 2 * math.pi); c.restore()
    c.set_source(g); c.fill()

    # Beine (leicht konisch) + Hosensaum
    pants = sp["pants"]
    for sx in (-1, 1):
        cx = sx * 5.3
        c.move_to(cx - 4.9, -27 + by * 0.3)
        c.line_to(cx + 4.9, -27 + by * 0.3)
        c.line_to(cx + 4.2, -5.5)
        c.line_to(cx - 4.2, -5.5)
        c.close_path()
        _fill_line(c, pants, -27, -5, 0.8)
        rrect(c, cx - 4.5, -7.6, 9.0, 2.6, 1.0)
        _fill_line(c, shade(pants, 0.9), -8, -5, 0.6)
    # Sneaker
    shoes = sp["shoes"]
    for sx in (-1, 1):
        cx = sx * 6.0
        c.move_to(cx - 5.4 * (1 if sx > 0 else 1.25), -1.8)
        c.curve_to(cx - 5.6, -6.6, cx + 1, -7.4, cx + 3.2, -5.4)
        c.curve_to(cx + 6.4, -4.6, cx + 7.4 * (1 if sx > 0 else 0.8), -3.2, cx + 7.0 * (1 if sx > 0 else 0.8), -1.8)
        c.close_path()
        _fill_line(c, shoes, -7, -1, 0.7, 1.05, 0.9, 0.6)
        rrect(c, cx - 6.4, -2.6, 13.4, 2.4, 1.1)
        _fill_line(c, "#F4F4F4" if is_dark(shoes) else shade(shoes, 0.86), -3, 0, 0.6, 1.0, 0.9, 0.6)
        c.set_line_width(0.5); src(c, shade(shoes, 0.6))
        for i in range(3):
            c.move_to(cx - 1.6 + i * 1.3, -6.2 + i * 0.25); c.line_to(cx - 0.4 + i * 1.3, -5.0 + i * 0.25)
        c.stroke()

    c.translate(0, by)

    # Tote-Bag (hinter dem Arm, links)
    if sp.get("tote"):
        c.save()
        c.set_line_width(1.2); src(c, "#B39A6C")
        c.move_to(-12, -50); c.curve_to(-20, -44, -27, -36, -31, -29); c.stroke()
        c.move_to(-9, -50); c.curve_to(-14, -42, -19, -34, -22, -29); c.stroke()
        rrect(c, -35, -30, 16, 18.5, 1.8)
        _fill_line(c, "#EDE1C6", -30, -11, 0.7, 1.05, 0.92, 0.65)
        src(c, "#5A4A30")
        c.select_font_face(FONT_HEAD); c.set_font_size(2.4)
        for i, ln in enumerate(["NOT LIKE", "OTHER", "GUYS"]):
            e = c.text_extents(ln)
            c.move_to(-27 - e.x_advance / 2, -24 + i * 3.4); c.show_text(ln)
        c.new_path()
        c.restore()

    # Oberkörper mit runden Schultern
    top = sp["top"]
    def torso_path():
        c.move_to(-5, -56.5)
        c.curve_to(-10, -56.2, -14.5, -55.6, -15.8, -50.5)
        c.line_to(-15.4, -26.5)
        c.curve_to(-15.4, -24.6, -14.4, -24.2, -12.8, -24.2)
        c.line_to(12.8, -24.2)
        c.curve_to(14.4, -24.2, 15.4, -24.6, 15.4, -26.5)
        c.line_to(15.8, -50.5)
        c.curve_to(14.5, -55.6, 10, -56.2, 5, -56.5)
        c.close_path()
    torso_path()
    _fill_line(c, top, -57, -24, 0.9)
    style = sp.get("top_style", "tee")
    c.save(); torso_path(); c.clip()
    if style == "cardigan":
        c.move_to(-4.2, -57); c.line_to(4.2, -57); c.line_to(1.6, -24); c.line_to(-1.6, -24); c.close_path()
        c.set_source(_grad(c, sp.get("inner", "#FFFFFF"), -57, -24, 1.0, 0.92)); c.fill()
        c.set_line_width(0.6); src(c, shade(top, 0.7))
        c.move_to(-4.2, -57); c.line_to(-1.6, -24); c.move_to(4.2, -57); c.line_to(1.6, -24); c.stroke()
        for yy in (-46, -39, -32):
            c.arc(-3.9, yy, 0.85, 0, 2 * math.pi); fill(c, shade(top, 0.55))
        for xx in range(-14, 15, 2):
            c.move_to(xx, -27.6); c.line_to(xx, -24.2)
        c.set_line_width(0.35); src(c, shade(top, 0.78)); c.stroke()
        rrect(c, -11.5, -37, 6, 5, 1); src(c, shade(top, 0.82)); c.stroke()
    elif style == "hoodie":
        rrect(c, -8.5, -37.5, 17, 9.5, 3.2); _fill_line(c, shade(top, 0.9), -38, -28, 0.6)
        c.arc(0, -56, 7, 0, math.pi); src(c, shade(top, 0.82)); c.fill()
        c.set_line_width(0.75); src(c, "#FFFFFF", 0.9)
        c.move_to(-2.8, -51.5); c.line_to(-3.3, -44.5); c.move_to(2.8, -51.5); c.line_to(3.3, -44.5); c.stroke()
    elif style == "suit":
        c.move_to(-4, -57); c.line_to(4, -57); c.line_to(0, -40); c.close_path(); fill(c, "#FFFFFF")
        c.move_to(-1.3, -54); c.line_to(1.3, -54); c.line_to(0.8, -40); c.line_to(0, -38); c.line_to(-0.8, -40); c.close_path()
        fill(c, sp.get("tie", "#C0392B"))
    else:
        c.arc(0, -56.5, 5, 0, math.pi); src(c, shade(top, 0.8)); c.fill()
    # weicher Seitenschatten
    g = cairo.LinearGradient(-16, 0, 16, 0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.0); g.add_color_stop_rgba(0.75, 0, 0, 0, 0.0); g.add_color_stop_rgba(1, 0, 0, 0, 0.14)
    c.set_source(g); c.paint()
    c.restore()

    # Arme (Ärmel mit Kontur, Bündchen, Hand)
    arms = {"idle": (12, 12), "wave": (14, 155 + 18 * math.sin(t * 9)), "phone": (12, 150),
            "shrug": (115, 115), "up": (168, 168), "point": (12, 95), "hips": (35, 35),
            "guitar": (-55, -35), "cross": (-60, -60), "facepalm": (12, -150)}.get(pose, (12, 12))
    hand_pos = {}
    for side, ang in ((-1, arms[0]), (1, arms[1])):
        a = math.radians(ang)
        sx, sy = side * 13.6, -51.2
        dx, dy = side * math.sin(a), math.cos(a)
        L = 20.5
        ex_, ey_ = sx + dx * L, sy + dy * L
        c.set_line_width(8.6); src(c, shade(top, 0.62))
        c.move_to(sx, sy); c.line_to(ex_, ey_); c.stroke()
        c.set_line_width(7.0); c.set_source(_grad(c, top, sy - 4, ey_ + 4, 1.06, 0.88))
        c.move_to(sx, sy); c.line_to(ex_, ey_); c.stroke()
        # Bündchen
        c.set_line_width(7.4); src(c, shade(top, 0.82))
        c.move_to(sx + dx * (L - 0.6), sy + dy * (L - 0.6)); c.line_to(ex_ + dx * 0.4, ey_ + dy * 0.4); c.stroke()
        hx, hy = sx + dx * (L + 2.6), sy + dy * (L + 2.6)
        c.arc(hx, hy, 3.7, 0, 2 * math.pi)
        _fill_line(c, skin, hy - 4, hy + 4, 0.6, 1.06, 0.92, 0.72)
        hand_pos[side] = (hx, hy)

    # Hals mit Schatten
    rrect(c, -4.2, -60, 8.4, 6.5, 2)
    _fill_line(c, shade(skin, 0.9), -60, -54, 0.5, 0.95, 0.85, 0.72)

    hs = sp.get("hair_style", "short")
    hair, hdark = sp["hair"], sp.get("hair_dark", shade(sp["hair"], 0.75))
    hy0 = -73
    if hs in ("long", "bun"):
        c.move_to(-20.5, hy0 + 22); c.curve_to(-24, hy0 + 2, -22, hy0 - 20, 0, hy0 - 20)
        c.curve_to(22, hy0 - 20, 24, hy0 + 2, 20.5, hy0 + 22); c.close_path()
        _fill_line(c, hdark, hy0 - 20, hy0 + 22, 0.8, 1.05, 0.9, 0.7)
    # Ohren
    for sx in (-1, 1):
        c.arc(sx * 17.4, hy0 + 1.5, 3.7, 0, 2 * math.pi)
        _fill_line(c, skin, hy0 - 2, hy0 + 5, 0.7, 1.0, 0.9, 0.72)
        c.arc(sx * 17.6, hy0 + 1.6, 1.6, 0, 2 * math.pi); src(c, shade(skin, 0.82)); c.fill()
    # Kopf mit Verlauf
    ellipse(c, 0, hy0, 17.6, 18.6)
    g = cairo.RadialGradient(-5, hy0 - 7, 3, 0, hy0, 21)
    g.add_color_stop_rgba(0, *rgb(shade(skin, 1.08)))
    g.add_color_stop_rgba(1, *rgb(shade(skin, 0.9)))
    c.set_source(g); c.fill_preserve()
    c.set_line_width(0.9); src(c, skin_line); c.stroke()
    # Kinn-/Halsschatten
    ellipse(c, 0, hy0 + 17, 7, 1.4); src(c, shade(skin, 0.8), 0.5); c.fill()

    # Augen
    blink = 1.0
    ph = (t + blink_seed * 1.37) % 3.7
    if ph < 0.12:
        blink = max(0.08, abs(ph - 0.06) / 0.06)
    lx = look * 1.2
    eye_y = hy0 + 1.6
    big = expr == "puppy"
    iris = sp.get("eyes", "#3B6EA8")
    for sx in (-1, 1):
        ex0 = sx * 6.4
        if blink < 0.35:
            c.set_line_width(1.1); src(c, "#2A1E1A")
            c.move_to(ex0 - 3, eye_y + 0.3); c.curve_to(ex0 - 1, eye_y + 1.6, ex0 + 1, eye_y + 1.6, ex0 + 3, eye_y + 0.3); c.stroke()
            continue
        c.save(); c.translate(ex0, eye_y); c.scale(1, blink)
        rxs, rys = (3.6, 4.0) if big else (3.1, 3.5)
        ellipse(c, 0, 0, rxs, rys); fill(c, "#FFFFFF")
        ir = 2.7 if big else 2.25
        c.arc(lx, 0.3, ir, 0, 2 * math.pi)
        g = cairo.RadialGradient(lx, 0.8, 0.3, lx, 0.3, ir)
        g.add_color_stop_rgba(0, *rgb(shade(iris, 1.3))); g.add_color_stop_rgba(1, *rgb(shade(iris, 0.75)))
        c.set_source(g); c.fill()
        c.arc(lx, 0.3, ir * 0.48, 0, 2 * math.pi); fill(c, "#141018")
        c.arc(lx + 0.8, -0.6, 0.75 if not big else 1.0, 0, 2 * math.pi); fill(c, "#FFFFFF")
        if big:
            c.arc(lx - 0.9, 1.2, 0.5, 0, 2 * math.pi); fill(c, "#FFFFFF")
        # Oberlid
        c.set_line_width(1.0); src(c, "#2A1E1A")
        c.arc(0, 0.2, rxs * 1.02, math.pi * 1.08, math.pi * 1.92); c.stroke()
        c.restore()
    # Augenbrauen (dicker, getapert)
    brow = sp.get("brow", shade(hair, 0.68) if hs == "alex" else shade(hair, 0.85))
    c.set_line_width(1.7); src(c, brow)
    for sx in (-1, 1):
        if expr == "angry":
            c.move_to(sx * 10, eye_y - 9); c.line_to(sx * 3.4, eye_y - 6.4)
        elif expr in ("sad", "puppy"):
            c.move_to(sx * 9.6, eye_y - 6.8); c.line_to(sx * 3.4, eye_y - 9.0)
        elif expr == "smug":
            yy = -1.2 if sx > 0 else 0
            c.move_to(sx * 9.8, eye_y - 7.6 + yy); c.curve_to(sx * 7.6, eye_y - 9.4 + yy, sx * 5, eye_y - 9.2 + yy, sx * 3.4, eye_y - 8.0 + yy)
        else:
            c.move_to(sx * 9.8, eye_y - 7.4); c.curve_to(sx * 7.6, eye_y - 9.4, sx * 5, eye_y - 9.4, sx * 3.4, eye_y - 8.2)
        c.stroke()
    # Wangen + Sommersprossen
    for sx in (-1, 1):
        g = cairo.RadialGradient(sx * 11, hy0 + 7.6, 0.2, sx * 11, hy0 + 7.6, 3.8)
        g.add_color_stop_rgba(0, 1, 0.42, 0.5, 0.55 if expr != "angry" else 0.95)
        g.add_color_stop_rgba(1, 1, 0.42, 0.5, 0)
        c.arc(sx * 11, hy0 + 7.6, 3.8, 0, 2 * math.pi); c.set_source(g); c.fill()
        if sp.get("freckles"):
            for (fx, fy) in ((8.6, 5.2), (10.8, 5.9), (9.6, 7.0), (12.4, 4.9), (7.4, 6.5)):
                c.arc(sx * fx, hy0 + fy, 0.38, 0, 2 * math.pi); src(c, "#B0703F", 0.8); c.fill()
    # Nase
    c.set_line_width(0.95); src(c, shade(skin, 0.72))
    c.move_to(-1.0, hy0 + 4.6); c.curve_to(-0.2, hy0 + 6.2, 1.3, hy0 + 6.0, 1.5, hy0 + 4.8); c.stroke()
    # Mund
    my = hy0 + 10.2
    lip = "#6E2430"
    if expr in ("happy", "talk"):
        c.move_to(-5.4, my - 0.8)
        c.curve_to(-3.6, my + 5.6, 3.6, my + 5.6, 5.4, my - 0.8)
        c.curve_to(2, my + 0.2, -2, my + 0.2, -5.4, my - 0.8); c.close_path()
        fill(c, lip)
        c.save(); c.move_to(-5.4, my - 0.8); c.curve_to(-3.6, my + 5.6, 3.6, my + 5.6, 5.4, my - 0.8)
        c.curve_to(2, my + 0.2, -2, my + 0.2, -5.4, my - 0.8); c.close_path(); c.clip()
        rrect(c, -5, my - 1.2, 10, 2.3, 0.8); fill(c, "#FFFFFF")
        ellipse(c, 0, my + 3.6, 2.8, 1.4); fill(c, "#E86A7A")
        c.restore()
        c.set_line_width(0.6); src(c, shade(skin, 0.68))
        c.arc(-5.9, my - 0.6, 0.9, math.pi * 0.6, math.pi * 1.2); c.stroke()
        c.arc(5.9, my - 0.6, 0.9, -math.pi * 0.2, math.pi * 0.4); c.stroke()
    elif expr == "smug":
        c.set_line_width(1.4); src(c, lip)
        c.move_to(-4.4, my + 0.6); c.curve_to(-1, my + 2.6, 2.6, my + 2.0, 5.2, my - 1.8); c.stroke()
        c.set_line_width(0.6); src(c, shade(skin, 0.7))
        c.arc(5.9, my - 1.6, 0.9, -math.pi * 0.1, math.pi * 0.5); c.stroke()
    elif expr == "sad":
        c.set_line_width(1.4); src(c, lip)
        c.move_to(-4, my + 2.6); c.curve_to(-2, my - 0.2, 2, my - 0.2, 4, my + 2.6); c.stroke()
    elif expr == "puppy":
        c.set_line_width(1.25); src(c, lip)
        c.move_to(-3.2, my + 1.6); c.curve_to(-1.6, my + 0.2, -0.4, my + 0.2, 0, my + 1.2)
        c.curve_to(0.4, my + 0.2, 1.6, my + 0.2, 3.2, my + 1.6); c.stroke()
    elif expr == "angry":
        rrect(c, -4.8, my - 0.4, 9.6, 3.8, 1.5); fill(c, lip)
        rrect(c, -4.2, my - 0.2, 8.4, 1.4, 0.6); fill(c, "#FFFFFF")
    elif expr == "shock":
        ellipse(c, 0, my + 1.4, 2.7, 3.3); fill(c, lip)
        ellipse(c, 0, my + 3.0, 1.6, 1.0); fill(c, "#E86A7A")
    elif expr == "cringe":
        rrect(c, -5.2, my - 0.6, 10.4, 3.8, 1.6); fill(c, "#FFFFFF")
        c.set_line_width(0.6); src(c, lip)
        rrect(c, -5.2, my - 0.6, 10.4, 3.8, 1.6); c.stroke()
        for xx in (-2.6, 0, 2.6):
            c.move_to(xx, my - 0.6); c.line_to(xx, my + 3.2)
        c.stroke()
    else:
        c.set_line_width(1.4); src(c, lip)
        c.move_to(-3, my + 0.8); c.curve_to(-1, my + 1.4, 1, my + 1.4, 3, my + 0.8); c.stroke()

    # Haare vorne
    if hs == "alex":
        # Schatten der Tolle auf der Stirn
        c.save()
        ellipse(c, 0, hy0, 17.2, 18.2); c.clip()
        g = cairo.LinearGradient(0, hy0 - 12, 0, hy0 - 5)
        g.add_color_stop_rgba(0, *rgb(shade(skin, 0.72), 0.45))
        g.add_color_stop_rgba(1, *rgb(shade(skin, 0.72), 0.0))
        c.rectangle(-18, hy0 - 12, 36, 7); c.set_source(g); c.fill()
        c.restore()
        # gestylte blonde Tolle (Texture-Quiff) mit Seitenscheitel
        c.move_to(-18.2, hy0 + 1.5)
        c.curve_to(-20.6, hy0 - 8, -19.4, hy0 - 16.5, -14.8, hy0 - 20.5)
        c.curve_to(-12.5, hy0 - 24.6, -9.2, hy0 - 25.6, -7.4, hy0 - 24.0)
        c.curve_to(-5.8, hy0 - 28.2, -0.8, hy0 - 29.6, 2.4, hy0 - 27.4)
        c.curve_to(5.4, hy0 - 30.0, 11.6, hy0 - 28.8, 13.8, hy0 - 24.8)
        c.curve_to(18.6, hy0 - 23.0, 21.0, hy0 - 16.0, 19.4, hy0 - 9.0)
        c.curve_to(19.6, hy0 - 5.0, 19.0, hy0 - 1.5, 18.2, hy0 + 1.5)
        c.curve_to(17.4, hy0 - 3.5, 16.6, hy0 - 6.8, 15.2, hy0 - 9.4)
        c.curve_to(12.0, hy0 - 8.2, 8.0, hy0 - 9.4, 5.6, hy0 - 11.8)
        c.curve_to(2.0, hy0 - 9.6, -3.4, hy0 - 10.2, -6.2, hy0 - 12.6)
        c.curve_to(-9.4, hy0 - 10.4, -13.2, hy0 - 9.6, -15.0, hy0 - 7.0)
        c.curve_to(-16.0, hy0 - 4.6, -16.8, hy0 - 1.6, -18.2, hy0 + 1.5)
        c.close_path()
        g = cairo.LinearGradient(0, hy0 - 29, 0, hy0)
        g.add_color_stop_rgba(0, *rgb(shade(hair, 1.32)))
        g.add_color_stop_rgba(0.45, *rgb(hair))
        g.add_color_stop_rgba(1, *rgb(hdark))
        c.set_source(g); c.fill_preserve()
        c.set_line_width(0.95); src(c, shade(hdark, 0.72)); c.stroke()
        # Strähnen
        c.set_line_width(0.8); src(c, shade(hdark, 0.85), 0.85)
        for path in (((-13.5, -12.5), (-11, -19), (-6, -22.6), (-1.5, -23.8)),
                     ((-8.5, -13.2), (-5, -19), (1, -22.6), (7, -23.6)),
                     ((-1, -12.6), (3, -18), (9, -21.4), (15.5, -19.6)),
                     ((7.2, -11.4), (11, -14.6), (15.4, -15.4), (18.4, -12.2))):
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = path
            c.move_to(x0, hy0 - y0 * -1 if False else hy0 + y0)
            c.curve_to(x1, hy0 + y1, x2, hy0 + y2, x3, hy0 + y3)
            c.stroke()
        # Glanz
        c.set_line_width(1.5); src(c, "#FFFFFF", 0.55)
        c.move_to(-5.2, hy0 - 23.4); c.curve_to(-2.4, hy0 - 26.0, 1.6, hy0 - 26.4, 4.4, hy0 - 25.2); c.stroke()
        c.set_line_width(1.0); src(c, "#FFFFFF", 0.35)
        c.move_to(8.6, hy0 - 25.6); c.curve_to(11.2, hy0 - 25.4, 13.4, hy0 - 24.0, 14.6, hy0 - 22.2); c.stroke()
    elif hs == "short":
        c.move_to(-18.2, hy0 - 0.5)
        c.curve_to(-19.4, hy0 - 16, -9, hy0 - 22.5, 0, hy0 - 22)
        c.curve_to(9, hy0 - 22.5, 19.4, hy0 - 16, 18.2, hy0 - 0.5)
        c.curve_to(16.6, hy0 - 8, 14, hy0 - 10, 10, hy0 - 10.6)
        c.curve_to(4, hy0 - 9, -4, hy0 - 12, -10, hy0 - 10.6)
        c.curve_to(-14, hy0 - 10, -16.6, hy0 - 8, -18.2, hy0 - 0.5)
        c.close_path(); _fill_line(c, hair, hy0 - 22, hy0, 0.8, 1.18, 0.9, 0.7)
    elif hs == "cap":
        c.move_to(-18.5, hy0 - 4); c.curve_to(-18, hy0 - 22, 18, hy0 - 22, 18.5, hy0 - 4); c.close_path()
        _fill_line(c, sp.get("cap", "#E5534B"), hy0 - 22, hy0 - 4, 0.8)
        rrect(c, -2, hy0 - 8, 26, 4.5, 2); _fill_line(c, shade(sp.get("cap", "#E5534B"), 0.8), hy0 - 8, hy0 - 3, 0.6)
    elif hs in ("long", "bun"):
        c.move_to(-19.2, hy0 + 9)
        c.curve_to(-21.4, hy0 - 16, -8, hy0 - 22.4, 2, hy0 - 21.4)
        c.curve_to(14, hy0 - 21.4, 21.4, hy0 - 12, 19.2, hy0 + 9)
        c.curve_to(17, hy0 - 2, 15, hy0 - 8, 9, hy0 - 11)
        c.curve_to(3, hy0 - 9, -6, hy0 - 12, -12, hy0 - 9)
        c.curve_to(-16, hy0 - 6, -17.6, hy0, -19.2, hy0 + 9)
        c.close_path(); _fill_line(c, hair, hy0 - 22, hy0 + 9, 0.8, 1.2, 0.9, 0.7)
        c.set_line_width(1.0); src(c, "#FFFFFF", 0.25)
        c.move_to(-8, hy0 - 18); c.curve_to(-3, hy0 - 20.4, 4, hy0 - 20.4, 9, hy0 - 18.4); c.stroke()
        if hs == "bun":
            c.arc(0, hy0 - 24, 7, 0, 2 * math.pi); _fill_line(c, hair, hy0 - 31, hy0 - 17, 0.8, 1.2, 0.9, 0.7)

    # Brille (moderne, leicht eckig-runde Fassung)
    if sp.get("glasses"):
        fr = sp.get("frame", "#26242B")
        for sx in (-1, 1):
            rrect(c, sx * 6.4 - 5.4, eye_y - 4.6, 10.8, 9.4, 4.2)
            src(c, "#FFFFFF", 0.14); c.fill_preserve()
            c.set_line_width(1.1); src(c, fr); c.stroke()
            c.set_line_width(0.7); src(c, "#FFFFFF", 0.5)
            c.move_to(sx * 6.4 - 3.2, eye_y - 3.0); c.line_to(sx * 6.4 - 1.6, eye_y - 3.6); c.stroke()
        c.set_line_width(1.15); src(c, fr)
        c.move_to(-1.0, eye_y - 1.4); c.curve_to(-0.4, eye_y - 2.4, 0.4, eye_y - 2.4, 1.0, eye_y - 1.4); c.stroke()
        c.move_to(-11.8, eye_y - 2.2); c.line_to(-17.0, eye_y - 3.0); c.stroke()
        c.move_to(11.8, eye_y - 2.2); c.line_to(17.0, eye_y - 3.0); c.stroke()

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
        name_tag(c, name, x, y - h * 1.055 + by * k, size=max(16, int(h * 0.052)))



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
