"""Grundlagen: Farben, Formen, Text, UI-Elemente (Chips, Sticker, Haken) – flacher Vektorstil."""
import math
import cairo

W, H = 1080, 1920
FONT = 'Inter Display Black'
FONT2 = 'Inter Display ExtraBold'


def hexc(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


C = {k: hexc(v) for k, v in dict(
    navy='#1D2A4D', navy2='#2B3A66', cream='#FFF7EA', ink='#1B2238', yellow='#FFC93C', yellow2='#F2B21B',
    green='#2DBE6C', green2='#22A45A', red='#E5484D', white='#FFFFFF', pink='#F28DB2', pink2='#E2669A',
    pink3='#FBC4D8', skin='#F7C9A4', skin2='#E9AE86', hair='#8A4A2B', hair2='#6E3820', pearl='#F4EFE7',
    pearl2='#E4DCCF', pearl3='#CFC5B5', gold='#D9A441', gold2='#B8862C', sky='#8FD3F4', sand='#F3D9A4',
    sand2='#E8C483', wood='#C98B5A', wood2='#A96E43', coral='#F07A5A', sea1='#3EC1D3', sea2='#1677A8',
    sea3='#0B3C6E', sea4='#061A3A', lamp='#FFE6A8', lightblue='#CFE9FF', grey='#8A93A6', shadow='#000000',
).items()}


def lerp(a, b, k):
    return a + (b - a) * k


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t, a, b):
    k = clamp((t - a) / (b - a)) if b != a else (1.0 if t >= b else 0.0)
    return k * k * (3 - 2 * k)


def ease_out(t, a, b):
    k = clamp((t - a) / (b - a))
    return 1 - (1 - k) ** 3


def back_out(t, a, b, s=1.9):
    k = clamp((t - a) / (b - a))
    k -= 1
    return k * k * ((s + 1) * k + s) + 1


def mixc(c1, c2, k):
    return tuple(lerp(a, b, k) for a, b in zip(c1, c2))


def alpha(c, a):
    return (c[0], c[1], c[2], c[3] * a)


def src(ctx, c):
    ctx.set_source_rgba(*c)


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def fill_rrect(ctx, x, y, w, h, r, c):
    rrect(ctx, x, y, w, h, r)
    src(ctx, c)
    ctx.fill()


def rect(ctx, x, y, w, h, c):
    ctx.rectangle(x, y, w, h)
    src(ctx, c)
    ctx.fill()


def circle(ctx, x, y, r, c):
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    src(ctx, c)
    ctx.fill()


def ellipse(ctx, x, y, rx, ry, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    src(ctx, c)
    ctx.fill()


def line(ctx, x1, y1, x2, y2, w, c, cap=cairo.LINE_CAP_ROUND):
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.set_line_width(w)
    ctx.set_line_cap(cap)
    src(ctx, c)
    ctx.stroke()


def poly(ctx, pts, c=None, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()
    if c is not None:
        src(ctx, c)
        ctx.fill()


def vgrad(ctx, x, y, w, h, stops):
    g = cairo.LinearGradient(0, y, 0, y + h)
    for o, c in stops:
        g.add_color_stop_rgba(o, *c)
    ctx.rectangle(x, y, w, h)
    ctx.set_source(g)
    ctx.fill()


# ---------------------------------------------------------------- Text
def text_size(ctx, s, size, font=FONT):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    return max(e.x_advance, e.x_bearing + e.width), size * 0.72


def text(ctx, s, x, y, size, c, font=FONT, align='c'):
    """y = vertikale Mitte der Großbuchstaben."""
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    w = e.x_advance
    xx = x - w / 2 if align == 'c' else (x if align == 'l' else x - w)
    ctx.move_to(xx - e.x_bearing * 0, y + size * 0.36)
    src(ctx, c)
    ctx.show_text(s)
    return w


# ---------------------------------------------------------------- Icons
def check_icon(ctx, x, y, r, bg=None, fg=None):
    circle(ctx, x, y, r, bg or C['green'])
    ctx.move_to(x - r * 0.45, y + r * 0.02)
    ctx.line_to(x - r * 0.12, y + r * 0.34)
    ctx.line_to(x + r * 0.48, y - r * 0.32)
    ctx.set_line_width(r * 0.26)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    src(ctx, fg or C['white'])
    ctx.stroke()


def tick_mark(ctx, x, y, s, c):
    ctx.move_to(x - s * 0.5, y)
    ctx.line_to(x - s * 0.15, y + s * 0.35)
    ctx.line_to(x + s * 0.5, y - s * 0.35)
    ctx.set_line_width(s * 0.28)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    src(ctx, c)
    ctx.stroke()


def cross_icon(ctx, x, y, r, c=None):
    c = c or C['red']
    for sx in (-1, 1):
        line(ctx, x - r * sx, y - r, x + r * sx, y + r, r * 0.45, c)


def clock_icon(ctx, x, y, r, hour):
    circle(ctx, x, y, r, C['white'])
    circle(ctx, x, y, r * 0.84, C['navy'])
    circle(ctx, x, y, r * 0.74, C['white'])
    for i in range(12):
        a = i / 12 * 2 * math.pi
        line(ctx, x + math.sin(a) * r * 0.58, y - math.cos(a) * r * 0.58, x + math.sin(a) * r * 0.66,
             y - math.cos(a) * r * 0.66, r * 0.06, C['navy'])
    ah = (hour % 12) / 12 * 2 * math.pi
    am = (hour % 1) * 2 * math.pi
    line(ctx, x, y, x + math.sin(ah) * r * 0.36, y - math.cos(ah) * r * 0.36, r * 0.13, C['navy'])
    line(ctx, x, y, x + math.sin(am) * r * 0.55, y - math.cos(am) * r * 0.55, r * 0.09, C['navy'])
    circle(ctx, x, y, r * 0.09, C['red'])


def sun_icon(ctx, x, y, r, c=None):
    c = c or C['yellow']
    for i in range(8):
        a = i / 8 * 2 * math.pi
        line(ctx, x + math.cos(a) * r * 1.25, y + math.sin(a) * r * 1.25, x + math.cos(a) * r * 1.65,
             y + math.sin(a) * r * 1.65, r * 0.28, c)
    circle(ctx, x, y, r, c)


def moon_icon(ctx, x, y, r, bg):
    circle(ctx, x, y, r, C['yellow'])
    circle(ctx, x + r * 0.45, y - r * 0.3, r * 0.82, bg)


def cloud_shape(ctx, x, y, s, c):
    for dx, dy, r in [(-0.55, 0.1, 0.42), (-0.1, -0.2, 0.55), (0.45, 0.0, 0.45), (0.0, 0.2, 0.42)]:
        circle(ctx, x + dx * s, y + dy * s, r * s, c)
    fill_rrect(ctx, x - 0.95 * s, y + 0.05 * s, 1.85 * s, 0.5 * s, 0.25 * s, c)


def rain_cloud_icon(ctx, x, y, s):
    cloud_shape(ctx, x, y, s, C['white'])
    for i, dx in enumerate((-0.45, 0.0, 0.45)):
        line(ctx, x + dx * s, y + 0.75 * s, x + dx * s - 0.12 * s, y + 1.05 * s, 0.12 * s, hexc('#4FA3E8'))


def bubble_dots(ctx, x, y, s, n, c):
    for i in range(n):
        circle(ctx, x + i * 0.9 * s, y - i * 0.75 * s, s * (0.28 + 0.1 * i), c)


# ---------------------------------------------------------------- UI-Bausteine
def pop(t, t0, dur=0.35):
    """Skalierung für Pop-in (0 vor t0, Overshoot, dann 1)."""
    if t < t0:
        return 0.0
    return max(0.0, back_out(t, t0, t0 + dur, 2.4))


UI_ON = [True]   # False: Text/Anzeigen weglassen (für Bewegungsunschärfe der Szene)
SAFE = (80, 260, 940, 1480)   # TikTok-Sicherheitsbereich: Text nur innerhalb


def sticker(ctx, s, x, y, size, style='cream', rot=0.0, sc=1.0, pad=None, alpha_=1.0, icon=None, world=False):
    """Aufkleber-Label (cream, yellow, white, blue, green, red, navy). (x, y) = Mitte."""
    if sc <= 0.001 or alpha_ <= 0.001 or (not world and not UI_ON[0]):
        return
    bg, fg = {
        'cream': (C['cream'], C['ink']), 'yellow': (C['yellow'], C['ink']), 'white': (C['white'], C['ink']),
        'blue': (C['lightblue'], C['ink']), 'green': (C['green'], C['white']), 'red': (C['red'], C['white']),
        'navy': (C['navy'], C['white']), 'pink': (C['pink'], C['white']),
    }[style]
    tw, th = text_size(ctx, s, size)
    px = pad if pad is not None else size * 0.42
    py = size * 0.34
    iw = 0
    if icon:
        iw = size * 1.15
    w, h = tw + px * 2 + iw, th + py * 2
    if not world:
        x0, y0, x1, y1 = SAFE
        fit = min(1.0, (x1 - x0) / (w * 1.06))
        size *= fit
        if fit < 1.0:
            return sticker(ctx, s, x, y, size, style, rot, sc, pad, alpha_, icon, world)
        sc = min(sc, (x1 - x0) / (w * 1.06))
        we, he = w * sc, h * sc
        x = min(max(x, x0 + we / 2 * 1.04), x1 - we / 2 * 1.04)
        y = min(max(y, y0 + he / 2 * 1.1), y1 - he / 2 * 1.1)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(rot))
    ctx.scale(sc, sc)
    ctx.push_group()
    fill_rrect(ctx, -w / 2 + size * 0.05, -h / 2 + size * 0.12, w, h, size * 0.28, alpha(C['shadow'], 0.28))
    fill_rrect(ctx, -w / 2, -h / 2, w, h, size * 0.28, bg)
    text(ctx, s, -w / 2 + px + tw / 2, 0, size, fg)
    if icon == 'check':
        tick_mark(ctx, w / 2 - px - size * 0.4, 0, size * 0.62, fg)
    elif icon == 'rain':
        rain_cloud_icon(ctx, w / 2 - px * 0.6 - size * 0.5, -size * 0.14, size * 0.5)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha_)
    ctx.restore()
    return w, h


def chip(ctx, x, y, h, draw_fn, w, sc=1.0, alpha_=1.0, border=True):
    """Dunkle Pill mit Inhalt; draw_fn(ctx) zeichnet relativ zur Mitte."""
    if not UI_ON[0]:
        return
    if sc <= 0.001:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.push_group()
    fill_rrect(ctx, -w / 2 + 3, -h / 2 + 6, w, h, h * 0.32, alpha(C['shadow'], 0.25))
    if border:
        fill_rrect(ctx, -w / 2 - 5, -h / 2 - 5, w + 10, h + 10, h * 0.36, C['white'])
    fill_rrect(ctx, -w / 2, -h / 2, w, h, h * 0.32, C['navy'])
    draw_fn(ctx)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha_)
    ctx.restore()


def clock_chip(ctx, x, y, hhmm, hour, kind, sc=1.0):
    def d(c):
        clock_icon(c, -118, 0, 34, hour)
        text(c, hhmm, 0, 0, 52, C['white'])
        if kind == 'sun':
            sun_icon(c, 118, 0, 15)
        elif kind == 'moon':
            moon_icon(c, 118, 0, 22, C['navy'])
        else:
            rain_cloud_icon(c, 118, -6, 26)
    chip(ctx, x, y, 92, d, 320, sc)


def floor_chip(ctx, x, y, label, direction, sc=1.0, ok=0.0):
    if not UI_ON[0]:
        return
    w = 120 + text_size(ctx, label, 56)[0]

    def d(c):
        if direction:
            cx = -w / 2 + 48
            if direction > 0:
                poly(c, [(cx - 17, 12), (cx + 17, 12), (cx, -16)], C['green'])
            else:
                poly(c, [(cx - 17, -12), (cx + 17, -12), (cx, 16)], C['green'])
        text(c, label, 26 if direction else 0, 0, 56, C['white'])
    chip(ctx, x, y, 92, d, w, sc)
    if ok > 0:
        ctx.save()
        ctx.translate(x + w / 2 + 34, y)
        ctx.scale(ok, ok)
        check_icon(ctx, 0, 0, 30)
        ctx.restore()


def check_row(ctx, x, y, s, size, sc):
    """Grüner Haken + Label (linksbündig an x)."""
    if not UI_ON[0]:
        return
    if sc <= 0.001:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    circle(ctx, 0, 0, size * 0.95, C['white'])
    check_icon(ctx, 0, 0, size * 0.78)
    tw, th = text_size(ctx, s, size)
    fill_rrect(ctx, size * 1.25 + 3, -th / 2 - size * 0.3 + 5, tw + size * 0.8, th + size * 0.6, size * 0.25,
               alpha(C['shadow'], 0.25))
    fill_rrect(ctx, size * 1.25, -th / 2 - size * 0.3, tw + size * 0.8, th + size * 0.6, size * 0.25, C['cream'])
    text(ctx, s, size * 1.25 + size * 0.4, 0, size, C['ink'], align='l')
    ctx.restore()


def qmark_bubble(ctx, x, y, r, sc=1.0, c=None):
    if not UI_ON[0]:
        return
    if sc <= 0.001:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    circle(ctx, 2, 5, r, alpha(C['shadow'], 0.2))
    circle(ctx, 0, 0, r, C['white'])
    circle(ctx, 0, 0, r * 0.86, c or C['yellow'])
    text(ctx, '?', 0, 0, r * 1.25, C['ink'])
    ctx.restore()
