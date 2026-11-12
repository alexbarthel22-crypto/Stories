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



# ---------------------------------------------------------------- moderne 3D-Emojis (Fluent Emoji 3D, MIT)
import os as _os
_EMO_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "assets", "emoji")
_EMO_INDEX = {}
if _os.path.isdir(_EMO_DIR):
    for _f in _os.listdir(_EMO_DIR):
        if _f.endswith(".webp"):
            _k = _f[:-5]
            _EMO_INDEX[_k] = _f
            _EMO_INDEX.setdefault(_k.replace("-fe0f", ""), _f)
_EMO_CACHE = {}
_EMO_KEEP = []
USE_EMOJI_IMAGES = True


def _emo_key(cl):
    return "-".join(f"{ord(ch):x}" for ch in cl)


def _emo_surface(cl):
    if not USE_EMOJI_IMAGES:
        return None
    if cl in _EMO_CACHE:
        return _EMO_CACHE[cl]
    k = _emo_key(cl)
    f = _EMO_INDEX.get(k) or _EMO_INDEX.get(k.replace("-fe0f", "")) or _EMO_INDEX.get(k.replace("-fe0f", "") + "-fe0f")
    surf = None
    if f:
        from PIL import Image
        im = Image.open(_os.path.join(_EMO_DIR, f)).convert("RGBA")
        r, g, b, a = im.split()
        from PIL import ImageChops
        pre = Image.merge("RGBA", [ImageChops.multiply(ch, a) for ch in (b, g, r)] + [a])   # BGRA, vormultipliziert
        data = bytearray(pre.tobytes())
        surf = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, im.width, im.height, im.width * 4)
        _EMO_KEEP.append(data)
    _EMO_CACHE[cl] = surf
    return surf


def _clusters(s):
    out, i, n = [], 0, len(s)
    while i < n:
        j = i + 1
        if 0x1F1E6 <= ord(s[i]) <= 0x1F1FF and j < n and 0x1F1E6 <= ord(s[j]) <= 0x1F1FF:
            j += 1
        while j < n:
            o = ord(s[j])
            if o in (0xFE0F, 0x20E3) or 0x1F3FB <= o <= 0x1F3FF or 0xE0020 <= o <= 0xE007F:
                j += 1
            elif o == 0x200D and j + 1 < n:
                j += 2
            else:
                break
        out.append(s[i:j]); i = j
    return out


_EMO_SIZED = {}


def _emo_sized(cl, px):
    """Emoji in exakt der Pixelgröße (Lanczos + leichte Schärfung) – scharf statt weich skaliert."""
    key = (cl, px)
    if key in _EMO_SIZED:
        return _EMO_SIZED[key]
    from PIL import Image, ImageChops, ImageFilter
    k = _emo_key(cl)
    f = _EMO_INDEX.get(k) or _EMO_INDEX.get(k.replace("-fe0f", "")) or _EMO_INDEX.get(k.replace("-fe0f", "") + "-fe0f")
    im = Image.open(_os.path.join(_EMO_DIR, f)).convert("RGBA").resize((px, px), Image.LANCZOS)
    r, g, b, a = im.split()
    rgb = Image.merge("RGB", (r, g, b)).filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=2))
    r, g, b = rgb.split()
    pre = Image.merge("RGBA", [ImageChops.multiply(ch, a) for ch in (b, g, r)] + [a])
    data = bytearray(pre.tobytes())
    surf = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, px, px, px * 4)
    _EMO_KEEP.append(data)
    if len(_EMO_SIZED) > 4000:
        _EMO_SIZED.clear()
    _EMO_SIZED[key] = surf
    return surf


def _emo_draw(c, surf, cx, cy, size, rot=0.0, alpha=1.0, cl=None):
    d = size * 1.12
    dx, dy = c.user_to_device_distance(d, 0)
    px = int(round((dx * dx + dy * dy) ** 0.5 / 4.0)) * 4            # Zielgröße in Gerätepixeln (4er-Raster)
    c.save(); c.translate(cx, cy); c.rotate(rot)
    if cl is not None and 8 <= px <= 1024:
        ss = _emo_sized(cl, px)
        sc = d / px; c.scale(sc, sc)
        c.set_source_surface(ss, -px / 2, -px / 2)
        c.get_source().set_filter(cairo.FILTER_BEST)
    else:
        sc = d / surf.get_width(); c.scale(sc, sc)
        c.set_source_surface(surf, -surf.get_width() / 2, -surf.get_height() / 2)
        c.get_source().set_filter(cairo.FILTER_BEST)
    c.paint_with_alpha(alpha) if alpha < 1 else c.paint()
    c.restore()

def _runs(s):
    out = []
    for part in _EMOJI_RE.split(s):
        if not part:
            continue
        emo = bool(_EMOJI_RE.fullmatch(part))
        if out and emo and out[-1][1]:                      # ZWJ-Sequenzen (z. B. 🏳️‍🌈) zusammenhalten
            out[-1] = (out[-1][0] + part, True)
        else:
            out.append((part, emo))
    return out


def _font(c, emoji, font, size):
    c.select_font_face(FONT_EMOJI if emoji else font)
    c.set_font_size(size * (0.92 if emoji else 1.0))


def _emo_adv(c, cl, size, font):
    if _emo_surface(cl) is not None:
        return size * 1.08
    _font(c, True, font, size)
    return c.text_extents(cl).x_advance


def text_width(c, s, size, font=FONT_HEAD):
    w = 0
    for part, emo in _runs(s):
        if emo:
            w += sum(_emo_adv(c, cl, size, font) for cl in _clusters(part))
        else:
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
        if emo:
            for cl in _clusters(part):
                surf = _emo_surface(cl)
                if surf is not None:
                    _emo_draw(c, surf, x0 + size * 0.54, y, size * 0.95, alpha=alpha, cl=cl)
                    x0 += size * 1.08
                else:
                    _font(c, True, font, size)
                    c.move_to(x0, yb + size * 0.06); src(c, color, alpha); c.show_text(cl)
                    x0 += c.text_extents(cl).x_advance
            continue
        _font(c, emo, font, size)
        c.move_to(x0, yb)
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
    surf = _emo_surface(e)
    if surf is not None:
        _emo_draw(c, surf, x, y, size, rot, alpha, cl=e)
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


# TikTok-Safe-Zone: Inhalt (ohne Hintergrund) wird auf SAFE_SCALE um SAFE_PIVOT skaliert,
# damit oben nichts hinter den TikTok-Tabs/der Suchleiste verschwindet.
SAFE_SCALE, SAFE_PIVOT = 0.9, (W / 2, 1720)


# SAFE_MODE "strict": kompletter Inhalt in TikToks freier Zone
# (oben 160 px, unten ~470 px, rechts ~140 px, links ~60 px frei bei 1080x1920)
SAFE_MODE = "default"
STRICT = dict(scale=0.78, x0=500 - 540 * 0.78, y0=160 - 60 * 0.78)
SAFE_BOX = (60, 160, 940, 1500)   # x0, y0, x1, y1 der freien Zone (unten ~420 px für TikTok-Text)


def configure_strict(top=160, bottom=1500, left=60, right=940):
    """Freie Zone setzen; Inhalt (Design-Bereich y 60..1772) wird hineinskaliert und zentriert."""
    global SAFE_BOX
    sc_ = min((right - left) / 1080, (bottom - top) / (1772 - 60))
    STRICT.update(scale=sc_, x0=left + ((right - left) - 1080 * sc_) / 2, y0=top - 60 * sc_)
    SAFE_BOX = (left, top, right, bottom)
TITLE_SIZE = 72


def safe_zone(c):
    if SAFE_MODE == "strict":
        c.translate(STRICT["x0"], STRICT["y0"])
        c.scale(STRICT["scale"], STRICT["scale"])
        return
    px, py = SAFE_PIVOT
    c.translate(px, py)
    c.scale(SAFE_SCALE, SAFE_SCALE)
    c.translate(-px, -py)


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
    # längstes Einzelwort darf nicht breiter als die freie Fläche sein -> Größe anpassen
    widest = max(text_width(c, wd, size, FONT_HEAD) for wd in s_txt.split())
    if widest > 1000:
        size = size * 1000 / widest
    def draw():
        text_block(c, s_txt, W / 2, y, size, 1000, color, FONT_HEAD)
    scaled(c, W / 2, y, s, draw)


CAPTION_SIZE = 50
NAME_SCALE = 1.0
BUBBLE_SCALE = 1.0


def caption(c, s_txt, t_since, y=1585):
    """Untertitel-Box wie im Referenzstil: weiß, dunkler Rand, leicht schräg."""
    if not s_txt:
        return
    s_txt = s_txt.upper()
    size = CAPTION_SIZE
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
    size *= BUBBLE_SCALE; max_w *= BUBBLE_SCALE
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


def _head_path(c, sp, hy0):
    """Kopfform: rund (Standard) oder sp['jaw'] == 'square' = kantiges Gesicht mit breitem Kiefer."""
    if sp.get("jaw") == "square":
        c.move_to(-16.8, hy0 - 13)
        c.line_to(-14.5, hy0 - 18.6); c.line_to(14.5, hy0 - 18.6); c.line_to(16.8, hy0 - 13)
        c.line_to(18.2, hy0 + 11)
        c.line_to(15.5, hy0 + 17.5)
        c.line_to(7.5, hy0 + 20.2)
        c.line_to(-7.5, hy0 + 20.2)
        c.line_to(-15.5, hy0 + 17.5)
        c.line_to(-18.2, hy0 + 11)
        c.close_path()
    else:
        ellipse(c, 0, hy0, 17.6, 18.6)


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
    pants = skin if sp.get("bare_legs") else sp["pants"]
    for sx in (-1, 1):
        cx = sx * 5.3
        c.move_to(cx - 4.9, -27 + by * 0.3)
        c.line_to(cx + 4.9, -27 + by * 0.3)
        c.line_to(cx + 4.2, -5.5)
        c.line_to(cx - 4.2, -5.5)
        c.close_path()
        _fill_line(c, pants, -27, -5, 0.8)
        if not sp.get("bare_legs"):
            rrect(c, cx - 4.5, -7.6, 9.0, 2.6, 1.0)
            _fill_line(c, shade(pants, 0.9), -8, -5, 0.6)
    # Sneaker oder Pumps
    shoes = sp["shoes"]
    for sx in ((-1, 1) if not sp.get("heels") else ()):
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

    if sp.get("heels"):
        for sx in (-1, 1):
            cx = sx * 5.6
            c.move_to(cx - 3.2, -6.0); c.curve_to(cx - 3.4, -2.6, cx - 0.5, -1.4, cx + 4.2, -1.3)
            c.curve_to(cx + 4.6, -2.2, cx + 2.4, -3.6, cx + 1.8, -6.0); c.close_path()
            _fill_line(c, shoes, -6.5, -1, 0.6, 1.15, 0.88, 0.6)
            rrect(c, cx - 3.3, -2.4, 1.1, 2.4, 0.3); fill(c, shade(shoes, 0.6))
    c.translate(0, by)

    # lange Haare hinten (hinter dem Körper)
    if sp.get("hair_style") == "fem":
        hy0, hair = -73, sp["hair"]
        c.move_to(-21, hy0 + 30)
        c.curve_to(-26, hy0 + 14, -25, hy0 - 22, 0, hy0 - 22)
        c.curve_to(25, hy0 - 22, 26, hy0 + 14, 21, hy0 + 30)
        for k in range(6):
            x1 = 21 - (k + 1) * 7
            c.curve_to(21 - k * 7 - 2, hy0 + 33, x1 + 2, hy0 + 33, x1, hy0 + 30)
        c.close_path()
        _fill_line(c, shade(hair, 0.9), hy0 - 22, hy0 + 36, 0.9, 1.1, 0.85, 0.68)
        c.set_line_width(0.8); src(c, shade(hair, 0.72), 0.7)
        for sx in (-1, 1):
            c.move_to(sx * 20, hy0 + 2); c.curve_to(sx * 23, hy0 + 14, sx * 19, hy0 + 22, sx * 21, hy0 + 32); c.stroke()

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
    style = sp.get("top_style", "tee")
    def torso_path():
        if style == "dress":
            c.move_to(-5, -56.5)
            c.curve_to(-9.5, -56.2, -13.8, -55.4, -14.6, -50.5)
            c.curve_to(-14.4, -45, -11, -41, -10.4, -37.5)
            c.curve_to(-12.5, -30, -16.5, -22, -18, -15.5)
            c.curve_to(-6, -13.8, 6, -13.8, 18, -15.5)
            c.curve_to(16.5, -22, 12.5, -30, 10.4, -37.5)
            c.curve_to(11, -41, 14.4, -45, 14.6, -50.5)
            c.curve_to(13.8, -55.4, 9.5, -56.2, 5, -56.5)
            c.close_path()
            return
        c.move_to(-5, -56.5)
        c.curve_to(-10, -56.2, -14.5, -55.6, -15.8, -50.5)
        c.line_to(-15.4, -26.5)
        c.curve_to(-15.4, -24.6, -14.4, -24.2, -12.8, -24.2)
        c.line_to(12.8, -24.2)
        c.curve_to(14.4, -24.2, 15.4, -24.6, 15.4, -26.5)
        c.line_to(15.8, -50.5)
        c.curve_to(14.5, -55.6, 10, -56.2, 5, -56.5)
        c.close_path()
    if sp.get("skirt"):                                   # Minirock (unter dem Oberteil)
        sk = sp["skirt"]
        c.move_to(-14.2, -27.5); c.line_to(14.2, -27.5); c.line_to(17.2, -17.2)
        c.curve_to(6, -16.2, -6, -16.2, -17.2, -17.2); c.close_path()
        _fill_line(c, sk, -28, -16, 0.8)
        c.set_line_width(0.45); src(c, shade(sk, 0.75))
        for xx in (-8, -3, 3, 8):
            c.move_to(xx * 0.9, -24); c.line_to(xx * 1.15, -17.5)
        c.stroke()
    torso_path()
    _fill_line(c, top, -57, -24, 0.9)
    c.save(); torso_path(); c.clip()
    if style == "dress":
        # Herz-Ausschnitt, Taillenband, Falten
        c.move_to(-9.5, -58); c.curve_to(-7.5, -52, -3, -50.5, 0, -52.2)
        c.curve_to(3, -50.5, 7.5, -52, 9.5, -58); c.close_path()
        c.set_source(_grad(c, skin, -58, -50, 1.04, 0.92)); c.fill()
        c.set_line_width(0.7); src(c, shade(top, 0.6))
        c.move_to(-9.5, -57.5); c.curve_to(-7.5, -52, -3, -50.5, 0, -52.2)
        c.curve_to(3, -50.5, 7.5, -52, 9.5, -57.5); c.stroke()
        rrect(c, -12, -39, 24, 2.6, 1); fill(c, shade(top, 0.75))
        c.set_line_width(0.45); src(c, shade(top, 0.78))
        for xx in (-9, -4.5, 0, 4.5, 9):
            c.move_to(xx * 0.8, -36); c.line_to(xx * 1.5, -16)
        c.stroke()
    elif style == "cardigan":
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
    elif style == "tank":
        # Feinripp-Muskelshirt: Rippen, tiefe Armausschnitte, runder Halsausschnitt
        c.set_line_width(0.4); src(c, shade(top, 0.86))
        for xx in range(-15, 16):
            c.move_to(xx, -57); c.line_to(xx, -24)
        c.stroke()
        for sx in (-1, 1):
            c.move_to(sx * 17, -58); c.line_to(sx * 9.5, -58)
            c.curve_to(sx * 9.5, -51, sx * 11.5, -44, sx * 17, -42.5); c.close_path()
            c.set_source(_grad(c, skin, -58, -42, 1.04, 0.92)); c.fill()
            c.set_line_width(0.7); src(c, shade(top, 0.7))
            c.move_to(sx * 9.5, -58); c.curve_to(sx * 9.5, -51, sx * 11.5, -44, sx * 17, -42.5); c.stroke()
        c.arc(0, -57.5, 6.2, 0, math.pi); c.set_source(_grad(c, skin, -58, -51, 1.0, 0.9)); c.fill()
        c.set_line_width(0.7); src(c, shade(top, 0.7)); c.arc(0, -57.5, 6.2, 0, math.pi); c.stroke()
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

    # Halskette (optional)
    if sp.get("chain"):
        c.save()
        c.set_line_width(1.1); src(c, sp["chain"])
        c.move_to(-6.5, -56.2); c.curve_to(-5, -47.5, 5, -47.5, 6.5, -56.2); c.stroke()
        c.set_line_width(0.5); src(c, "#FFFFFF", 0.7)
        c.move_to(-5.8, -54.5); c.curve_to(-4.4, -48.6, -1, -48.2, 0, -48.2); c.stroke()
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
        bare = style in ("tank", "dress")
        sleeve = skin if bare else top
        pump = (sp["pump"] if isinstance(sp.get("pump"), (int, float)) and not isinstance(sp.get("pump"), bool) else 1.45) if sp.get("pump") else 1.0
        c.set_line_width((8.6 if not bare else 7.2) * pump); src(c, shade(sleeve, 0.62 if not bare else 0.72))
        c.move_to(sx, sy); c.line_to(ex_, ey_); c.stroke()
        c.set_line_width((7.0 if not bare else 5.8) * pump); c.set_source(_grad(c, sleeve, sy - 4, ey_ + 4, 1.06, 0.9))
        c.move_to(sx, sy); c.line_to(ex_, ey_); c.stroke()
        if not bare:
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
    if hs in ("long", "bun", "alex_long"):
        c.move_to(-20.5, hy0 + 22); c.curve_to(-24, hy0 + 2, -22, hy0 - 20, 0, hy0 - 20)
        c.curve_to(22, hy0 - 20, 24, hy0 + 2, 20.5, hy0 + 22); c.close_path()
        _fill_line(c, shade(hair, 0.93) if hs == "alex_long" else hdark, hy0 - 20, hy0 + 22, 0.8, 1.05, 0.9, 0.7)
    # Ohren
    for sx in (-1, 1):
        c.arc(sx * 17.4, hy0 + 1.5, 3.7, 0, 2 * math.pi)
        _fill_line(c, skin, hy0 - 2, hy0 + 5, 0.7, 1.0, 0.9, 0.72)
        c.arc(sx * 17.6, hy0 + 1.6, 1.6, 0, 2 * math.pi); src(c, shade(skin, 0.82)); c.fill()
        if sp.get("earrings"):
            c.arc(sx * 17.8, hy0 + 6.2, 1.5, 0, 2 * math.pi); src(c, sp["earrings"]); c.fill()
    # Kopf mit Verlauf
    _head_path(c, sp, hy0)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
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
    if expr == "sleepy":
        blink = 0.1
    lx = look * 1.2
    eye_y = hy0 + 1.6
    big = expr == "puppy"
    iris = sp.get("eyes", "#3B6EA8")
    mk = sp.get("makeup")
    if mk:
        for sx in (-1, 1):
            g = cairo.RadialGradient(sx * 6.6, eye_y - 2.6, 0.3, sx * 6.6, eye_y - 2.6, 5.2)
            g.add_color_stop_rgba(0, *rgb(mk.get("shadow", "#C8708E"), 0.7)); g.add_color_stop_rgba(1, *rgb(mk.get("shadow", "#C8708E"), 0))
            ellipse(c, sx * 6.6, eye_y - 2.4, 5.4, 3.4); c.set_source(g); c.fill()
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
        if mk:
            c.set_line_width(1.5); src(c, "#1A1214")
            c.arc(0, 0.2, rxs * 1.04, math.pi * 1.15, math.pi * 1.95); c.stroke()
            c.move_to(sx * rxs * 0.98, -0.6); c.line_to(sx * (rxs + 1.8), -2.2); c.line_to(sx * rxs * 0.9, -0.2); c.close_path()
            fill(c, "#1A1214")
        if sp.get("lashes"):
            c.set_line_width(0.6)
            for k, ang in enumerate((1.6, 1.78, 1.92)):
                a_ = math.pi * ang
                px, py = math.cos(a_) * rxs * 1.02 * sx, 0.2 + math.sin(a_) * rxs * 1.02
                c.move_to(px, py); c.line_to(px * 1.18 + sx * 0.5, py * 1.18 - 0.3)
            c.stroke()
        c.restore()
    # Augenbrauen (dicker, getapert)
    brow = sp.get("brow", shade(hair, 0.68) if hs in ("alex", "fem") else shade(hair, 0.85))
    c.set_line_width(1.7 if not mk else 1.05); src(c, brow)
    for sx in (-1, 1):
        if mk and expr not in ("angry", "sad", "puppy"):
            lift = -1.0 if (expr == "smug" and sx > 0) else 0
            c.move_to(sx * 3.2, eye_y - 7.6 + lift)
            c.curve_to(sx * 5.5, eye_y - 10.4 + lift, sx * 8.2, eye_y - 10.4 + lift, sx * 10.2, eye_y - 7.4 + lift)
        elif expr == "angry":
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
    lip = sp.get("lips", "#6E2430")
    if mk and expr in ("smug", "neutral"):
        up = 1.2 if expr == "smug" else 0
        c.move_to(-4.6, my + 0.6 - up * 0.3)
        c.curve_to(-3, my - 1.2, -1.4, my - 1.4, 0, my - 0.4)
        c.curve_to(1.4, my - 1.4, 3, my - 1.2, 4.6, my + 0.6 - up)
        c.curve_to(3, my + 3.4, -3, my + 3.4, -4.6, my + 0.6 - up * 0.3); c.close_path()
        c.set_source(_grad(c, lip, my - 1.4, my + 3.2, 1.15, 0.85)); c.fill()
        c.set_line_width(0.5); src(c, shade(lip, 0.6))
        c.move_to(-4.4, my + 0.6 - up * 0.3); c.curve_to(-1.5, my + 1.2, 1.5, my + 1.2, 4.4, my + 0.6 - up); c.stroke()
        ellipse(c, 1.0, my + 1.9, 1.4, 0.5); src(c, "#FFFFFF", 0.55); c.fill()
    elif expr in ("happy", "talk"):
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
    if hs == "bald":
        # Halbglatze: kahler Oberkopf mit Glanz, Haarkranz an Seiten/hinten (über den Ohren)
        c.save()
        _head_path(c, sp, hy0); c.clip()
        g = cairo.RadialGradient(-4, hy0 - 15, 0.5, -4, hy0 - 15, 9)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.55); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        ellipse(c, -4, hy0 - 14, 8, 4.5); c.set_source(g); c.fill()
        c.restore()
        for sx in (-1, 1):
            c.move_to(sx * 16.4, hy0 + 7)
            c.curve_to(sx * 19.2, hy0 + 6, sx * 19.9, hy0 + 1, sx * 19.5, hy0 - 3.5)
            c.curve_to(sx * 19.1, hy0 - 7, sx * 17.4, hy0 - 8.6, sx * 15.6, hy0 - 7.8)
            c.curve_to(sx * 16.6, hy0 - 5, sx * 16.6, hy0 - 1.5, sx * 15.8, hy0 + 1.5)
            c.curve_to(sx * 15.6, hy0 + 3.5, sx * 15.8, hy0 + 5.5, sx * 16.4, hy0 + 7)
            c.close_path()
            _fill_line(c, hair, hy0 - 9, hy0 + 7, 0.7, 1.15, 0.9, 0.7)
            c.set_line_width(0.45); src(c, shade(hair, 0.72))
            c.move_to(sx * 17.2, hy0 - 6.5); c.curve_to(sx * 18.6, hy0 - 3, sx * 18.4, hy0 + 1, sx * 17.6, hy0 + 4.5); c.stroke()
        # Stirnfalten
        c.set_line_width(0.45); src(c, shade(skin, 0.75), 0.7)
        for kk in range(2):
            fy = hy0 - 9.5 - kk * 2.2
            c.move_to(-5.5 + kk, fy); c.curve_to(-2, fy - 0.8, 2, fy - 0.8, 5.5 - kk, fy); c.stroke()
    # Haare vorne
    if hs == "fem":
        g = cairo.LinearGradient(0, hy0 - 24, 0, hy0 + 22)
        g.add_color_stop_rgba(0, *rgb(shade(hair, 1.3))); g.add_color_stop_rgba(0.45, *rgb(hair))
        g.add_color_stop_rgba(1, *rgb(shade(hair, 0.82)))
        c.move_to(-18.8, hy0 + 22)
        c.curve_to(-21.5, hy0 + 4, -21, hy0 - 16, -10, hy0 - 21.5)
        c.curve_to(-2, hy0 - 25, 14, hy0 - 23, 18.8, hy0 - 10)
        c.curve_to(21, hy0 - 2, 20.6, hy0 + 12, 19, hy0 + 22)
        c.curve_to(17.4, hy0 + 23, 15.6, hy0 + 21, 15.2, hy0 + 18)
        c.curve_to(16.4, hy0 + 8, 16.2, hy0 - 2, 14.4, hy0 - 6.5)
        c.curve_to(9, hy0 - 6.2, 0, hy0 - 9.5, -7.5, hy0 - 15.5)
        c.curve_to(-11.5, hy0 - 11, -14.6, hy0 - 4, -15.2, hy0 + 4)
        c.curve_to(-15.4, hy0 + 11, -15.4, hy0 + 17, -15.8, hy0 + 21)
        c.curve_to(-16.6, hy0 + 23, -18, hy0 + 23, -18.8, hy0 + 22)
        c.close_path()
        c.set_source(g); c.fill_preserve()
        c.set_line_width(0.9); src(c, shade(hdark, 0.72)); c.stroke()
        c.set_line_width(0.75); src(c, shade(hdark, 0.85), 0.8)
        for (a0, a1, a2, a3) in (((-6, -19), (2, -17), (9, -12), (14, -8)), ((-9, -17.5), (-2, -13), (6, -9.5), (13, -7)),
                                 ((-17, -6), (-18, 4), (-17, 12), (-17.5, 20)), ((17, -4), (18.4, 6), (17.5, 14), (17.5, 20))):
            c.move_to(a0[0], hy0 + a0[1]); c.curve_to(a1[0], hy0 + a1[1], a2[0], hy0 + a2[1], a3[0], hy0 + a3[1]); c.stroke()
        c.set_line_width(1.6); src(c, "#FFFFFF", 0.5)
        c.move_to(-4, hy0 - 21.5); c.curve_to(1, hy0 - 22.6, 7, hy0 - 21.5, 11, hy0 - 18.5); c.stroke()
    if hs in ("alex", "alex_long"):
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

    # Stirnband (Sport)
    if sp.get("headband"):
        hb = sp["headband"]
        c.save(); ellipse(c, 0, hy0, 18.9, 19.9); c.clip()
        rrect(c, -21, hy0 - 14.5, 42, 6.2, 1.5); _fill_line(c, hb, hy0 - 14.5, hy0 - 8.3, 0.7)
        rrect(c, -21, hy0 - 12.2, 42, 1.3, 0.5); src(c, "#FFFFFF", 0.85); c.fill()
        c.restore()

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
    if prop == "beer":
        hx, hy = hand_pos[1]
        c.save(); c.translate(hx + 1.5, hy - 2); c.rotate(0.1); c.scale(1.3, 1.3)
        c.move_to(-2.4, 6); c.line_to(-2.4, -3); c.curve_to(-2.4, -6, -1.1, -7, -1.1, -9)
        c.line_to(-1.1, -12.5); c.line_to(1.1, -12.5); c.line_to(1.1, -9)
        c.curve_to(1.1, -7, 2.4, -6, 2.4, -3); c.line_to(2.4, 6); c.close_path()
        _fill_line(c, "#7A4A12", -12, 6, 0.6, 1.2, 0.85, 0.6)
        rrect(c, -2.4, -2.5, 4.8, 4.5, 0.6); fill(c, "#F2E2B8")
        rrect(c, -1.3, -13.6, 2.6, 1.5, 0.4); fill(c, "#D9B23A")
        c.set_line_width(0.6); src(c, "#FFFFFF", 0.5); c.move_to(-1.6, 4.5); c.line_to(-1.6, -3); c.stroke()
        c.restore()
        c.arc(hx, hy, 3.7, 0, 2 * math.pi)
        _fill_line(c, skin, hy - 4, hy + 4, 0.6, 1.06, 0.92, 0.72)
    elif prop:
        hx, hy = hand_pos[1]
        if pose == "phone":
            emoji(c, prop, hx + 1, hy - 6, 15, rot=-0.15)
        elif pose == "guitar":
            emoji(c, prop, 1, -36, 34, rot=0.0)
        else:
            emoji(c, prop, hx + 7, hy - 3, 15, rot=0.12)
    c.restore()

    if name:
        name_tag(c, name, x, y - h * (1.055 + 0.02 * (NAME_SCALE - 1)) + by * k, size=max(16, int(h * 0.052 * NAME_SCALE)))



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


# ----------------------------------------------------------------- Intro (generisch)
def draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, cfg):
    """Auswahl-Intro wie im Referenzvideo. cfg: icon, bg, spec, expr, pose, hand_prop,
    side_emoji, burst (Liste Emojis)."""
    k = 0
    for i, tk in enumerate(ticks):
        if t >= tk:
            k = i
    revealed = t >= reveal_t
    if revealed:
        bg, top, txt = cfg["bg"], None, role_text
    else:
        txt, prop, top, bg = shuffle[k][0], shuffle[k][1], shuffle[k][2], shuffle[k][3]
    background(c, bg, t, rays=0.09, cy=1080, speed=0.25)
    c.save()
    safe_zone(c)
    text(c, "Heute ist Alex", W / 2, 112, 44, "#FFFFFF", FONT_BOLD)
    sc = pop(t, reveal_t, 0.4) if revealed else 1.0
    def ttl():
        c.save(); c.translate(0, 6)
        text(c, txt, W / 2, 196, 76, "#000000", FONT_HEAD, alpha=0.25)
        c.restore()
        text(c, txt, W / 2, 196, 76, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, 196, sc, ttl)
    icons = [s_[1] for s_ in shuffle] + [cfg["icon"]]
    cols = [s_[3] for s_ in shuffle] + [cfg["bg"]]
    sel = len(shuffle) if revealed else k
    last_tick = reveal_t if revealed else (ticks[k] if t >= ticks[0] else 0)
    slide = 1 - ease_out_cubic((t - last_tick) / 0.06)
    yb = 330
    rrect(c, -200, yb - 50, W + 400, 100, 0)
    src(c, "#000000", 0.55); c.fill()
    for j in range(-8, 9):
        idx = (sel + j) % len(icons)
        x = W / 2 + (j + slide) * 96
        c.arc(x, yb, 36, 0, 2 * math.pi); fill(c, shade(cols[idx], 0.85))
        c.arc(x, yb, 36, 0, 2 * math.pi); c.set_line_width(3); src(c, "#FFFFFF", 0.35); c.stroke()
        emoji(c, icons[idx], x, yb, 38)
    c.arc(W / 2, yb, 44, 0, 2 * math.pi)
    c.set_line_width(7); src(c, "#F7C948"); c.stroke()
    if revealed:
        spec, expr, pose = cfg["spec"], cfg.get("expr", "happy"), cfg.get("pose", "idle")
        s = 0.9 + 0.1 * ease_out_back((t - reveal_t) / 0.35)
        scaled(c, W / 2, 1520, s, lambda: person(c, W / 2, 1520, 780, spec, t, expr, pose, cfg.get("hand_prop")))
        emoji(c, cfg["side_emoji"], 830, 1080 + math.sin(t * 3) * 10, 120, rot=0.25)
        sparkle_lines(c, t, reveal_t, W / 2, 1000, n=14, r0=260, r1=560, d=0.55)
        burst(c, t, reveal_t, cfg["burst"], W / 2, 1000, n=18, seed=5, dist=620, life=1.6, size=86)
    else:
        spec = alex(top=top, top_style="hoodie", pants="#2F3B52")
        person(c, W / 2, 1520, 780, spec, t, "happy", "idle")
        emoji(c, prop, 870 + math.sin(t * 6) * 6, 1150, 110, rot=0.15)
    c.restore()
    if flash_start <= t < reveal_t + 0.3:
        a = clamp((t - flash_start) / 0.04) if t < reveal_t else 1 - ease_out_cubic((t - reveal_t) / 0.3)
        c.set_source_rgba(1, 1, 1, a)
        c.paint()
        if t < reveal_t:
            emoji(c, cfg["icon"], W / 2, 960, 130, rot=(t - flash_start) * 9)


# ----------------------------------------------------------------- Intro draußen vor dem Haus
ROLE_DETAILS = {
    "EIN ASTRONAUT.": ["🚀", "🪐", "🛰️", "⭐"], "EIN PICK ME BOY.": ["🌹", "📖", "🧋", "🎸"],
    "EIN GAMER.": ["🎮", "🕹️", "🎧", "🖥️"], "EMOTIONAL ABHÄNGIG.": ["📱", "🥺", "💔", "⏳"],
    "EIN GASLIGHTER.": ["🤷", "🌀", "🚩", "🕯️"], "EIN INFLUENCER.": ["🤳", "💄", "📸", "✨"],
    "EIN BAUARBEITER.": ["🔨", "🧱", "🚧", "👷"], "EIN DJ.": ["🎧", "💿", "🔊", "🪩"],
    "EIN PIRAT.": ["⚓", "🦜", "💰", "🏴"], "EIN LEHRER.": ["🍎", "📚", "✏️", "🔔"],
    "EIN POLIZIST.": ["🚨", "🚓", "🍩", "👮"], "EIN ROCKSTAR.": ["🎸", "🤘", "🎤", "⚡"],
    "EIN KOCH.": ["🍳", "🥘", "🧂", "🍝"], "EIN F-BOY.": ["📱", "💪", "🌙", "👻"],
    "EIN OF-MODEL.": ["📸", "💄", "💸", "💅"], "FRIEDRICH MERZ.": ["🎙️", "🛩️", "⛰️", "💼"],
}


def mix_col(a, b, u):
    ra, ga, ba, _ = rgb(a); rb, gb, bb, _ = rgb(b)
    return "#%02x%02x%02x" % (int((ra + (rb - ra) * u) * 255), int((ga + (gb - ga) * u) * 255), int((ba + (bb - ba) * u) * 255))


def garden_furniture(c, t, accent=("#3E7BDA", "#F2B233"), umbrella=True):
    a1, a2 = accent
    wood, dark = "#A87447", "#6B4A2E"
    def line(w=5):
        c.set_line_width(w); src(c, INK); c.stroke()
    # Fußmatte, Wandlaternen, Blumentöpfe an der Tür
    rrect(c, 470, 1255, 140, 16, 4); fill(c, shade(a1, 0.8))
    for x in (450, 630):
        rrect(c, x - 14, 1095, 28, 40, 6); fill(c, "#2B2B2B")
        rrect(c, x - 9, 1101, 18, 26, 4); src(c, "#FFE9A8", 0.7 + 0.3 * math.sin(t * 3 + x) ** 2); c.fill()
    for x in (430, 650):
        c.move_to(x - 26, 1205); c.line_to(x + 26, 1205); c.line_to(x + 18, 1262); c.line_to(x - 18, 1262); c.close_path(); fill(c, a2)
        c.move_to(x - 26, 1205); c.line_to(x + 26, 1205); c.line_to(x + 18, 1262); c.line_to(x - 18, 1262); c.close_path(); line(4)
        for dx, dy, r in ((0, -30, 26), (-18, -14, 18), (18, -14, 18)):
            c.arc(x + dx, 1205 + dy, r, 0, 2 * math.pi)
        fill(c, "#3F9A4A")
    # Vogelhaus am Baum
    c.move_to(90, 1010); c.line_to(130, 1045); c.line_to(50, 1045); c.close_path(); fill(c, a1)
    rrect(c, 58, 1045, 64, 54, 4); fill(c, a2); rrect(c, 58, 1045, 64, 54, 4); line(3)
    c.arc(90, 1070, 10, 0, 2 * math.pi); fill(c, INK)
    # Briefkasten am Zaun
    c.rectangle(684, 1330, 12, 110); fill(c, dark)
    rrect(c, 650, 1280, 80, 56, 18); fill(c, a1); rrect(c, 650, 1280, 80, 56, 18); line(4)
    c.rectangle(722, 1262, 6, 30); fill(c, "#E23B3B")
    # Bank links
    for x in (135, 315):
        c.rectangle(x, 1470, 14, 60); fill(c, dark)
    for i in range(3):
        rrect(c, 120, 1395 + i * 22, 220, 14, 4); fill(c, wood)
    rrect(c, 115, 1460, 230, 18, 5); fill(c, wood); rrect(c, 115, 1460, 230, 18, 5); line(3)
    rrect(c, 130, 1440, 90, 26, 10); fill(c, a1)
    rrect(c, 230, 1440, 90, 26, 10); fill(c, a2)
    # Picknicktisch (+ optional Sonnenschirm) rechts
    if umbrella:
        c.set_line_width(8); src(c, "#E8E8E8"); c.move_to(895, 1180); c.line_to(895, 1470); c.stroke()
        for i in range(6):
            x0 = 765 + i * 43.3
            c.move_to(895, 1160); c.line_to(x0, 1235); c.line_to(x0 + 43.3, 1235); c.close_path()
            src(c, a1 if i % 2 == 0 else "#FFFFFF"); c.fill()
        c.move_to(895, 1160); c.line_to(765, 1235); c.line_to(1025, 1235); c.close_path(); line(4)
    rrect(c, 790, 1455, 210, 18, 5); fill(c, wood); rrect(c, 790, 1455, 210, 18, 5); line(3)
    for x in (805, 970):
        c.move_to(x, 1473); c.line_to(x + 12, 1473); c.line_to(x + (24 if x < 900 else -12), 1540); c.line_to(x + (12 if x < 900 else -24), 1540); c.close_path()
        fill(c, dark)
    for x in (770, 1010):                                    # Hocker
        rrect(c, x - 22, 1490, 44, 12, 4); fill(c, a2); c.rectangle(x - 4, 1502, 8, 40); fill(c, dark)
    rrect(c, 860, 1425, 26, 30, 5); fill(c, "#FFFFFF")      # Becher
    c.arc(915, 1440, 14, 0, 2 * math.pi); fill(c, "#F2B233")   # Zitrone


def house_scene(c, t, sky=("#4E98E0", "#BFE3FF"), walls="#F2E3C8", roof="#B5523B", door="#7A4A2E", lawn="#5DBB63",
                accent=("#3E7BDA", "#F2B233"), umbrella=True, sun=True):
    g = cairo.LinearGradient(0, 0, 0, 1240)
    g.add_color_stop_rgb(0, *rgb(sky[0])[:3]); g.add_color_stop_rgb(1, *rgb(sky[1])[:3])
    c.rectangle(-400, -400, W + 800, 1640); c.set_source(g); c.fill()
    if sun:
        c.arc(900, 470, 70, 0, 2 * math.pi); src(c, "#FFE27A"); c.fill()
    else:
        c.arc(900, 470, 62, 0, 2 * math.pi); src(c, "#F2EBD9"); c.fill()
        c.arc(926, 452, 54, 0, 2 * math.pi); src(c, sky[0]); c.fill()
    for i, (x0, y0, s) in enumerate(((180, 470, 1.0), (760, 560, 0.8))):
        x = x0 + math.sin(t * 0.4 + i) * 20
        for dx, dy, r in ((0, 0, 40), (45, -15, 50), (95, 0, 38)):
            c.arc(x + dx * s, y0 + dy * s, r * s, 0, 2 * math.pi)
        src(c, "#FFFFFF", 0.9); c.fill()
    c.rectangle(-400, 1240, W + 800, 2400); src(c, lawn); c.fill()
    c.rectangle(-400, 1240, W + 800, 14); src(c, shade(lawn, 0.85)); c.fill()
    # Baum links, Busch rechts
    rrect(c, 70, 1000, 40, 260, 12); fill(c, "#7A4A2E")
    for dx, dy, r in ((0, 0, 95), (-60, 50, 70), (60, 50, 70)):
        c.arc(90 + dx, 950 + dy, r, 0, 2 * math.pi)
    src(c, "#3F9A4A"); c.fill()
    for dx in (0, 60):
        c.arc(960 + dx, 1250, 70, math.pi, 0); src(c, "#4CAB57"); c.fill()
    # Haus
    rrect(c, 220, 820, 640, 440, 6); fill(c, walls)
    rrect(c, 220, 820, 640, 440, 6); c.set_line_width(6); src(c, INK); c.stroke()
    c.rectangle(700, 600, 70, 160); fill(c, shade(roof, 0.8))
    c.move_to(540, 560); c.line_to(900, 840); c.line_to(180, 840); c.close_path(); fill(c, roof)
    c.move_to(540, 560); c.line_to(900, 840); c.line_to(180, 840); c.close_path(); c.set_line_width(6); src(c, INK); c.stroke()
    for x in (290, 670):
        rrect(c, x, 900, 120, 110, 8); fill(c, "#BFE6FF")
        rrect(c, x, 900, 120, 110, 8); c.set_line_width(5); src(c, INK); c.stroke()
        c.move_to(x + 60, 900); c.line_to(x + 60, 1010); c.move_to(x, 955); c.line_to(x + 120, 955); c.set_line_width(3); c.stroke()
    c.arc(540, 730, 42, 0, 2 * math.pi); fill(c, "#BFE6FF")
    c.arc(540, 730, 42, 0, 2 * math.pi); c.set_line_width(5); src(c, INK); c.stroke()
    rrect(c, 480, 1080, 120, 180, 10); fill(c, door)
    c.arc(580, 1175, 7, 0, 2 * math.pi); fill(c, "#F2C94C")
    # Weg + Zaun
    c.move_to(480, 1260); c.line_to(600, 1260); c.line_to(760, 2400); c.line_to(320, 2400); c.close_path(); src(c, "#D9CBB0"); c.fill()
    for x in list(range(-40, 400, 55)) + list(range(700, 1140, 55)):
        c.move_to(x, 1330); c.line_to(x + 18, 1305); c.line_to(x + 36, 1330); c.line_to(x + 36, 1420); c.line_to(x, 1420); c.close_path()
        fill(c, "#FFFFFF")
    for y in (1350, 1395):
        c.rectangle(-40, y, 440, 10); c.rectangle(700, y, 440, 10)
    fill(c, "#EDEDED")
    garden_furniture(c, t, accent, umbrella)


def draw_intro_house(c, t, shuffle, ticks, flash_start, reveal_t, role_text, cfg):
    """Auswahl-Intro draußen vor dem Haus. cfg wie draw_intro_generic, zusätzlich optional:
    house=dict(sky, walls, roof, door, lawn), decor(c, t, u), alex_extras(c, x, feet, h, t, u)."""
    k = 0
    for i, tk in enumerate(ticks):
        if t >= tk:
            k = i
    revealed = t >= reveal_t
    fill_rect(c, cfg.get("fill", cfg.get("house", {}).get("sky", ("#4E98E0",))[0] if revealed else "#4E98E0"))
    c.save()
    safe_zone(c)
    if revealed:
        u = ease_out_back((t - reveal_t) / 0.45)
        hcfg = cfg.get("house", {})
        if cfg.get("scene"):
            cfg["scene"](c, t, True, cfg["bg"])
        else:
            house_scene(c, t, umbrella=cfg.get("umbrella", True), **hcfg)
        if cfg.get("decor"):
            cfg["decor"](c, t, u)
        txt = role_text
    else:
        txt, icon, top, bg = shuffle[k]
        det = ROLE_DETAILS.get(txt, [icon] * 4)
        if cfg.get("scene"):
            cfg["scene"](c, t, False, bg)
        else:
            house_scene(c, t, sky=(mix_col("#4E98E0", bg, 0.55), mix_col("#BFE3FF", bg, 0.25)), umbrella=cfg.get("umbrella", True))
        bounce = 1 + 0.15 * max(0, 1 - (t - ticks[k]) / 0.08) if t >= ticks[0] else 1
        emoji(c, det[1], 228, 1395, 95 * bounce, rot=-0.15)
        emoji(c, det[2], 940, 1405, 85 * bounce, rot=0.15)
        emoji(c, det[3], 350, 955, 80)
        emoji(c, det[3 if len(det) < 5 else 4], 730, 955, 80)
        emoji(c, icon, 540, 730, 60)
    # Kopfzeile + Auswahl-Leiste
    head = "Heute ist Alex"
    if revealed and txt.split(" ", 1)[0] in ("EIN", "EINE"):
        head += " " + txt.split(" ", 1)[0].lower() + " …"
    text(c, head, c.device_to_user(W / 2, 0)[0] if revealed else W / 2, 112, 50 if revealed else 44, "#FFFFFF", FONT_HEAD if revealed else FONT_BOLD)
    if revealed:
        u_ = (t - reveal_t) / 0.5
        sc = ease_out_back(u_, 2.8) if u_ < 1 else 1 + 0.03 * math.sin((t - reveal_t) * 6)
        # Bildschirmmitte (nicht Mitte des Inhaltsbereichs) und maximale Breite bis zur rechten Sperrzone
        cx = c.device_to_user(W / 2, 0)[0]
        half = c.device_to_user(SAFE_BOX[2], 0)[0] - cx - 45
        words = txt.split(" ", 1)
        small, big_ = (words[0], words[1]) if len(words) == 2 and words[0] in ("EIN", "EINE") else ("", txt)
        lines = cfg.get("title_lines") or (big_.replace("-", "-\n", 1).split("\n") if "-" in big_ and len(big_) > 9 else [big_])
        sizes = [min(200, 200 * 2 * half / max(1, text_width(c, ln, 200, FONT_HEAD))) for ln in lines]
        bsize = min(sizes)
        def ttl():
            y = 175 + bsize * 0.5
            for ln in lines:
                c.select_font_face(FONT_HEAD); c.set_font_size(bsize)
                w_ = text_width(c, ln, bsize, FONT_HEAD)
                c.move_to(cx - w_ / 2 + 8, y + bsize * 0.36 + 10); c.text_path(ln); src(c, "#000000", 0.3); c.fill()
                c.move_to(cx - w_ / 2, y + bsize * 0.36); c.text_path(ln)
                c.set_line_width(bsize * 0.15); c.set_line_join(cairo.LINE_JOIN_ROUND); src(c, INK); c.stroke_preserve()
                src(c, "#FFE14D"); c.fill()
                y += bsize * 0.95
            ttl.bottom = y
        ty = 175 + bsize * 0.5
        scaled(c, cx, ty + bsize * 0.4, sc, ttl)
        title_bottom = c.user_to_device(0, getattr(ttl, "bottom", ty + bsize * 1.4) - bsize * 0.35)[1]
    else:
        title_bottom = None
        def ttl():
            c.save(); c.translate(0, 6); text(c, txt, W / 2, 196, 76, "#000000", FONT_HEAD, alpha=0.3); c.restore()
            text(c, txt, W / 2, 196, 76, "#FFFFFF", FONT_HEAD)
        ttl()
    icons = [s_[1] for s_ in shuffle] + [cfg["icon"]]
    cols = [s_[3] for s_ in shuffle] + [cfg["bg"]]
    sel = len(shuffle) if revealed else k
    last_tick = reveal_t if revealed else (ticks[k] if t >= ticks[0] else 0)
    slide = 1 - ease_out_cubic((t - last_tick) / 0.06)
    _, band_y = c.user_to_device(W / 2, 330)
    band_x, _ = c.user_to_device(W / 2, 330)
    # Alex
    fx, fy, hh = W / 2, 1640, 700
    if revealed:
        s = 0.9 + 0.1 * ease_out_back((t - reveal_t) / 0.35)
        def body():
            person(c, fx, fy, hh, cfg["spec"], t, cfg.get("expr", "happy"), cfg.get("pose", "idle"), cfg.get("hand_prop"))
            if cfg.get("alex_extras"):
                cfg["alex_extras"](c, fx, fy, hh, t, u)
        scaled(c, fx, fy, s, body)
        sparkle_lines(c, t, reveal_t, W / 2, 1150, n=14, r0=260, r1=560, d=0.55)
        burst(c, t, reveal_t, cfg["burst"], W / 2, 1150, n=18, seed=5, dist=620, life=1.6, size=86)
    else:
        txt_, icon, top, bg = shuffle[k]
        det = ROLE_DETAILS.get(txt_, [icon] * 4)
        person(c, fx, fy, hh, alex(top=top, top_style="hoodie", pants="#2F3B52"), t, "happy", "idle")
        emoji(c, det[0], fx + 190, fy - 300, 110, rot=0.15)
    c.restore()
    # Auswahl-Band über die volle Bildschirmbreite (darf rechts in den Sicherheitsbereich)
    # nach der Enthüllung: Band wird kleiner und rutscht nach unten (Platz für das große Thema)
    bu = ease_in_out((t - reveal_t) / 0.4) if revealed else 0.0
    bs = 1 - 0.45 * bu
    target = (title_bottom + 45) if title_bottom else band_y + 22
    yb = band_y + 22 + (max(band_y + 22, target) - band_y - 22) * bu
    rrect(c, 0, yb - 78 * bs, W, 156 * bs, 0); src(c, "#000000", 0.6); c.fill()
    step = 150 * bs
    for j in range(-7, 8):
        idx = (sel + j) % len(icons)
        x = band_x + (j + slide) * step
        c.arc(x, yb, 58 * bs, 0, 2 * math.pi); fill(c, shade(cols[idx], 0.85))
        c.arc(x, yb, 58 * bs, 0, 2 * math.pi); c.set_line_width(4 * bs); src(c, "#FFFFFF", 0.4); c.stroke()
        emoji(c, icons[idx], x, yb, 62 * bs)
    c.arc(band_x, yb, 68 * bs, 0, 2 * math.pi); c.set_line_width(10 * bs); src(c, "#F7C948"); c.stroke()
    if flash_start <= t < reveal_t + 0.3:
        a = clamp((t - flash_start) / 0.04) if t < reveal_t else 1 - ease_out_cubic((t - reveal_t) / 0.3)
        c.set_source_rgba(1, 1, 1, a); c.paint()
        if t < reveal_t:
            emoji(c, cfg["icon"], W / 2, 960, 130, rot=(t - flash_start) * 9)
