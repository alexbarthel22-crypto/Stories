"""Shelly und der Leuchtturm – hochwertige Neufassung (Kamerafahrten, Turmzimmer, Lupen-Einblendungen)."""
import json, math, os, random, re
import cairo
from draw import *
from chars import shelly
import retro
from retro import P, SLAB, TYPE

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = json.load(open(f'{ROOT}/audio/vo_words.json'))
GAP_AT = 61.48 + 0.4
GAP = 2.0
VO_END = NEW[-1][2] + 0.3


def G(t):
    return t + (GAP if t >= GAP_AT else 0.0)


END = G(VO_END) + 1.6
blink = retro.blink


def card(ctx, *a, **k):
    ctx.save()
    ctx.identity_matrix()
    retro.paper_card(ctx, *a, **k)
    ctx.restore()


# ---------------------------------------------------------------- Geometrie (1 m = 16 px, Boden y = 0)
M = 16.0
TOPY = -120 * M            # Oberkante Turmschaft = Boden des Turmzimmers
ROOM_H = 300
BALY = -60 * M             # Balkonboden
RINGX = 300                # x des oberen Rings / Seil
RING_TOP = TOPY + 26       # Seilansatz oben
BAL_RING = (236, BALY - 46)
LOOPY = RING_TOP + 30 * M  # Schlaufe am kurzen Stück


def halfw(y):
    return lerp(150, 112, clamp(-y / -TOPY))


class Cam:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def apply(self, ctx):
        ctx.translate(W / 2, H / 2)
        ctx.scale(self.z, self.z)
        ctx.translate(-self.x, -self.y)

    def bounds(self):
        hw, hh = W / 2 / self.z, H / 2 / self.z
        return self.x - hw, self.y - hh, self.x + hw, self.y + hh


def cam_path(T, keys):
    """keys: [(t, x, y, z)] – weich interpoliert (Zoom logarithmisch)."""
    if T <= keys[0][0]:
        return Cam(*keys[0][1:])
    for a, b in zip(keys, keys[1:]):
        if T <= b[0]:
            k = ease(T, a[0], b[0])
            z = math.exp(lerp(math.log(a[3]), math.log(b[3]), k))
            return Cam(lerp(a[1], b[1], k), lerp(a[2], b[2], k), z)
    return Cam(*keys[-1][1:])


# ---------------------------------------------------------------- Landschaft
SKY = {'night': [(0, '#141A45'), (0.6, '#2E3577'), (1, '#4B4A92')],
       'dusk': [(0, '#2E3577'), (0.55, '#8E6AB0'), (1, '#F2A0A0')],
       'dawn': [(0, '#5B6AB8'), (0.55, '#E7A0B8'), (1, '#FFD39A')]}


def landscape(ctx, cam, T, tod):
    x0, y0, x1, y1 = cam.bounds()
    g = cairo.LinearGradient(0, TOPY - 900, 0, -300)
    for o, c in SKY[tod]:
        g.add_color_stop_rgba(o, *hexc(c))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()
    r = random.Random(4)
    if tod != 'dawn':
        for i in range(260):
            sx, sy = r.uniform(-1800, 1800), r.uniform(TOPY - 1400, -600)
            if x0 < sx < x1 and y0 < sy < y1:
                a = 0.45 + 0.45 * math.sin(T * r.uniform(1, 3) + i)
                circle(ctx, sx, sy, r.uniform(1.6, 3.2), alpha(C['white'], a))
        circle(ctx, 620, TOPY - 520, 120, alpha(hexc('#FFF6D6'), 0.15))
        circle(ctx, 620, TOPY - 520, 70, hexc('#FFF4CC'))
    else:
        circle(ctx, -520, -520, 260, alpha(hexc('#FFE3A0'), 0.35))
        circle(ctx, -520, -520, 170, hexc('#FFC46A'))
    for i, (cx, cy, s) in enumerate([(-900, -2300, 140), (700, -1900, 170), (-500, -1450, 120), (900, -1100, 110), (-300, -2900, 150)]):
        cloud_shape(ctx, cx + (T * 10 * (1 + 0.2 * i)) % 300, cy, s, alpha(hexc('#F7C6D4') if tod != 'night' else hexc('#6A6FB0'), 0.75))
    # ferne Inseln mit Muscheltal-Hütten
    hz = -300
    for ix, iw, ih, col in ((-1100, 700, 120, '#3B4C8A'), (500, 900, 160, '#34437E'), (-200, 500, 80, '#43559A')):
        ctx.move_to(ix, hz)
        ctx.curve_to(ix + iw * 0.2, hz - ih, ix + iw * 0.8, hz - ih, ix + iw, hz)
        ctx.close_path()
        src(ctx, hexc(col) if tod != 'dawn' else mixc(hexc(col), hexc('#E7A0B8'), 0.35))
        ctx.fill()
    for i in range(7):
        hx = 700 + i * 70
        rect(ctx, hx, hz - 130 + abs(3 - i) * 12, 40, 34, hexc('#FFE6A8') if tod == 'night' else hexc('#F7EFD9'))
        poly(ctx, [(hx - 6, hz - 130 + abs(3 - i) * 12), (hx + 20, hz - 154 + abs(3 - i) * 12), (hx + 46, hz - 130 + abs(3 - i) * 12)], hexc('#C8322E'))
    # Meer
    sea = {'night': ('#24306A', '#1A2350'), 'dusk': ('#4A4F98', '#2E3577'), 'dawn': ('#6E8FD0', '#4E70B8')}[tod]
    vgrad(ctx, x0 - 10, hz, x1 - x0 + 20, 300, [(0, hexc(sea[0])), (1, hexc(sea[1]))])
    for i in range(int(x0 // 120) - 1, int(x1 // 120) + 2):
        xx = i * 120 + math.sin(T * 1.8 + i) * 18
        yy = hz + 30 + (i % 5) * 50
        line(ctx, xx, yy, xx + 60, yy, 4, alpha(C['white'], 0.3))
    # Strand + Dünen
    sand = {'night': '#C9A985', 'dusk': '#D9B48A', 'dawn': '#F3D9A4'}[tod]
    ctx.move_to(x0 - 10, 10)
    ctx.curve_to(-400, -30, 400, 20, x1 + 10, -20)
    ctx.line_to(x1 + 10, y1 + 10)
    ctx.line_to(x0 - 10, y1 + 10)
    ctx.close_path()
    src(ctx, hexc(sand))
    ctx.fill()
    ctx.move_to(x0 - 10, 220)
    ctx.curve_to(-300, 160, 300, 260, x1 + 10, 180)
    ctx.line_to(x1 + 10, y1 + 10)
    ctx.line_to(x0 - 10, y1 + 10)
    ctx.close_path()
    src(ctx, mixc(hexc(sand), hexc('#8E6A4A'), 0.12))
    ctx.fill()
    for gx in range(-900, 1000, 70):
        for k in range(4):
            line(ctx, gx, 200, gx - 12 + k * 8, 150 - k * 6 + math.sin(T * 2 + gx) * 3, 4, hexc('#6E9A5A') if tod != 'night' else hexc('#4F6F4A'))
    r = random.Random(9)
    for i in range(40):
        sx, sy = r.uniform(-900, 900), r.uniform(20, 140)
        shell_small(ctx, sx, sy, r.uniform(0.8, 1.3), r.choice([C['pink3'], C['cream'], hexc('#F9B6A0')]))
    for px, ph, lean in ((-560, 520, -0.1), (640, 470, 0.12)):
        palm(ctx, px, 20, ph, T, lean, tod)


def shell_small(ctx, x, y, s, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 8)
    for j in range(7):
        a = math.radians(200 + j * 140 / 6)
        ctx.line_to(math.cos(a) * 14, math.sin(a) * 14 + 3)
    ctx.close_path()
    src(ctx, c)
    ctx.fill()
    ctx.restore()


def palm(ctx, x, y, h, T, lean, tod):
    dark = 0.35 if tod == 'night' else 0.0
    tx, ty = x + h * lean, y - h
    ctx.move_to(x - 16, y)
    ctx.curve_to(x - 8, y - h * 0.5, tx - 12, ty + 40, tx - 8, ty)
    ctx.line_to(tx + 8, ty)
    ctx.curve_to(tx + 8, ty + 40, x + 8, y - h * 0.5, x + 16, y)
    ctx.close_path()
    src(ctx, mixc(hexc('#A9744A'), C['ink'], dark))
    ctx.fill()
    for i in range(8):
        a = math.radians(-178 + i * 27) + math.sin(T * 1.4 + i) * 0.05
        lx, ly = tx + math.cos(a) * 180, ty + math.sin(a) * 80 + 60
        ctx.move_to(tx, ty)
        ctx.curve_to(tx + math.cos(a) * 80, ty - 55 + math.sin(a) * 20, lx, ly - 30, lx, ly)
        ctx.curve_to(lx - math.cos(a) * 50, ly - 10, tx + math.cos(a) * 60, ty - 10, tx, ty)
        src(ctx, mixc(hexc('#3DAA6A'), C['ink'], dark))
        ctx.fill()


# ---------------------------------------------------------------- Leuchtturm
def stone_band(ctx, ya, yb, col):
    wa, wb = halfw(ya), halfw(yb)
    poly(ctx, [(-wa, ya), (wa, ya), (wb, yb), (-wb, yb)], col)


def tower(ctx, T, tod, bricks=0.0, room_lit=True):
    n = 12
    for i in range(n):
        ya, yb = TOPY * i / n, TOPY * (i + 1) / n
        stone_band(ctx, ya, yb, hexc('#EFE8DA') if i % 2 == 0 else hexc('#C8322E'))
    # Schattierung + Lichtkante
    ctx.move_to(halfw(0) * 0.35, 0)
    ctx.line_to(halfw(0), 0)
    ctx.line_to(halfw(TOPY), TOPY)
    ctx.line_to(halfw(TOPY) * 0.35, TOPY)
    ctx.close_path()
    src(ctx, alpha(C['ink'], 0.13))
    ctx.fill()
    ctx.move_to(-halfw(0), 0)
    ctx.line_to(-halfw(0) * 0.8, 0)
    ctx.line_to(-halfw(TOPY) * 0.8, TOPY)
    ctx.line_to(-halfw(TOPY), TOPY)
    ctx.close_path()
    src(ctx, alpha(C['white'], 0.12))
    ctx.fill()
    for h_ in (14, 32, 50, 78, 96):
        y = -h_ * M
        fill_rrect(ctx, -14, y - 44, 28, 56, 14, hexc('#2B3170'))
    rect(ctx, -halfw(0) - 20, -24, 2 * halfw(0) + 40, 24, hexc('#8E8A80'))
    # Balkon (60 m)
    bx0 = halfw(BALY) - 6
    rect(ctx, bx0, BALY, 150, 18, hexc('#7A7F90'))
    poly(ctx, [(bx0, BALY + 18), (bx0 + 150, BALY + 18), (bx0 + 110, BALY + 60), (bx0 + 10, BALY + 60)], hexc('#5A5E70'))
    for i in range(7):
        line(ctx, bx0 + 8 + i * 22, BALY, bx0 + 8 + i * 22, BALY - 64, 5, hexc('#4A4F5E'))
    line(ctx, bx0, BALY - 64, bx0 + 150, BALY - 64, 7, hexc('#4A4F5E'))
    ring(ctx, *BAL_RING)
    # Turmzimmer (Aufschnitt)
    rx0, rx1 = -200, 200
    ry0 = TOPY - ROOM_H
    rect(ctx, rx0 - 20, TOPY - 6, rx1 - rx0 + 40, 30, hexc('#8E8A80'))
    rect(ctx, rx0, ry0, rx1 - rx0, ROOM_H, hexc('#F2E3C2') if room_lit else hexc('#B8A88A'))
    for i in range(0, ROOM_H, 30):
        line(ctx, rx0, ry0 + i, rx1, ry0 + i, 2, alpha(hexc('#D9C49A'), 0.6))
    rect(ctx, rx0, TOPY - 26, rx1 - rx0, 26, hexc('#8E5A3A'))
    for i in range(8):
        line(ctx, rx0 + i * 50, TOPY - 26, rx0 + i * 50, TOPY, 2, hexc('#6E4630'))
    # Fensterbogen rechts
    fill_rrect(ctx, 120, ry0 + 60, 80, 190, 40, hexc('#6E7896'))
    fill_rrect(ctx, 130, ry0 + 70, 60, 172, 30, sky_col(tod))
    if bricks > 0:
        nb = int(8 * bricks)
        for b in range(nb):
            for c in range(2):
                fill_rrect(ctx, 132 + c * 28 + (b % 2) * 6, ry0 + 222 - b * 20, 26, 18, 2, hexc('#9A938A'))
    rect(ctx, 112, ry0 + 236, 100, 16, hexc('#BDB5A6'))
    # Tisch, Laterne, Kerze, Bild
    rect(ctx, -170, TOPY - 106, 120, 14, P['wood2'])
    rect(ctx, -160, TOPY - 92, 10, 66, P['wood3'])
    rect(ctx, -70, TOPY - 92, 10, 66, P['wood3'])
    rect(ctx, -126, TOPY - 140, 12, 34, C['white'])
    ctx.move_to(-120, TOPY - 140)
    ctx.curve_to(-128, TOPY - 156, -116, TOPY - 166, -120, TOPY - 176)
    ctx.curve_to(-110, TOPY - 160, -112, TOPY - 150, -120, TOPY - 140)
    src(ctx, hexc('#FFC24A'))
    ctx.fill()
    line(ctx, -20, ry0, -20, ry0 + 60, 3, hexc('#3A3F4F'))
    fill_rrect(ctx, -36, ry0 + 60, 32, 52, 6, hexc('#3A3F4F'))
    rect(ctx, -30, ry0 + 66, 20, 38, hexc('#FFE6A8'))
    for k in range(5):
        line(ctx, -180 + k * 14, ry0 + 50, -180 + k * 14, ry0 + 90, 3, alpha(hexc('#6E4630'), 0.7))
    line(ctx, -186, ry0 + 64, -122, ry0 + 80, 3, alpha(hexc('#6E4630'), 0.7))
    # Dach + Laterne darüber
    poly(ctx, [(rx0 - 40, ry0), (rx1 + 40, ry0), (rx1, ry0 - 40), (rx0, ry0 - 40)], hexc('#2E3A6E'))
    fill_rrect(ctx, -90, ry0 - 200, 180, 160, 10, hexc('#3A3F4F'))
    rect(ctx, -76, ry0 - 186, 152, 132, hexc('#FFE6A8') if tod != 'dawn' else hexc('#F7EFD9'))
    for i in range(1, 4):
        line(ctx, -76 + i * 38, ry0 - 186, -76 + i * 38, ry0 - 54, 4, hexc('#3A3F4F'))
    poly(ctx, [(-120, ry0 - 200), (120, ry0 - 200), (0, ry0 - 320)], hexc('#C8322E'))
    circle(ctx, 0, ry0 - 328, 14, P['gold'])
    if tod == 'night':
        a = T * 0.9
        ca = math.cos(a)
        if abs(ca) > 0.08:
            ctx.save()
            ctx.translate(0, ry0 - 120)
            ctx.scale(ca, 1)
            g = cairo.LinearGradient(0, 0, 2000, 0)
            g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.4)
            g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
            poly(ctx, [(0, -50), (2000, -300), (2000, 300), (0, 50)])
            ctx.set_source(g)
            ctx.fill()
            ctx.restore()
    # oberer Ring (Halterung)
    rect(ctx, halfw(TOPY), RING_TOP - 18, RINGX - halfw(TOPY) - 12, 10, hexc('#4A4F5E'))
    ring(ctx, RINGX, RING_TOP - 14)


def sky_col(tod):
    return {'night': hexc('#1A2150'), 'dusk': hexc('#6A5AA0'), 'dawn': hexc('#F2B0B8')}[tod]


def ring(ctx, x, y):
    ctx.new_sub_path()
    ctx.arc(x, y + 14, 14, 0, 2 * math.pi)
    ctx.set_line_width(7)
    src(ctx, hexc('#3A3F4F'))
    ctx.stroke()


def braid(ctx, pts, col=None, w=11):
    """Geflochtenes Seetang-Seil entlang eines Polygonzugs."""
    col = col or hexc('#3F9A5E')
    dark = mixc(col, C['ink'], 0.35)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    src(ctx, col)
    ctx.stroke()
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        if L < 1:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L
        px, py = -uy, ux
        n = int(L / (w * 0.9))
        for i in range(n):
            cx, cy = ax + ux * (i + 0.5) * w * 0.9, ay + uy * (i + 0.5) * w * 0.9
            sgn = 1 if i % 2 else -1
            line(ctx, cx - px * w * 0.45 * sgn, cy - py * w * 0.45 * sgn, cx + px * w * 0.45 * sgn + ux * w * 0.5,
                 cy + py * w * 0.45 * sgn + uy * w * 0.5, w * 0.22, dark)


def coil(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for i in range(5):
        ellipse(ctx, 0, -i * 9, 54 - i * 5, 15, hexc('#3F9A5E'))
        ellipse(ctx, 0, -i * 9 - 2, 44 - i * 5, 9, hexc('#2A6A40'))
    ctx.restore()


def loop(ctx, x, y, r=12):
    ctx.new_sub_path()
    ctx.arc(x, y + r, r, 0, 2 * math.pi)
    ctx.set_line_width(8)
    src(ctx, hexc('#3F9A5E'))
    ctx.stroke()


def hang(ctx, T, x, y, s=0.62, expr='smile', sway=True):
    """Shelly am Seil (Fußpunkt y), Hände über dem Kopf am Seil bei x."""
    k = math.sin(T * 7) * 5 if sway else 0
    shelly(ctx, x - 6 * s, y, s, arms={'R': (6, -175 + k), 'L': (2, -160 - k)}, expr=expr, blink=blink(T), face=0.3)


def witch(ctx, x, y, s, T, face=1):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * face, s)
    ww = math.sin(T * 5) * 16
    ctx.move_to(-150, ww)
    ctx.curve_to(-70, -36, 70, -36, 150, ww)
    ctx.curve_to(70, 26, -70, 26, -150, ww)
    src(ctx, hexc('#3A4A80'))
    ctx.fill()
    ellipse(ctx, 0, -6, 60, 10, alpha(C['white'], 0.12))
    line(ctx, -140, 0, -260, 26, 6, hexc('#3A4A80'))
    for sx in (60, 90):
        circle(ctx, sx, -10, 5, C['white'])
    poly(ctx, [(-24, -10), (24, -10), (14, -86), (-14, -86)], hexc('#2E1A47'))
    circle(ctx, 0, -106, 25, hexc('#9BD6A0'))
    ellipse(ctx, 18, -102, 10, 7, hexc('#8AC690'))
    poly(ctx, [(-40, -122), (40, -122), (8, -206), (-4, -196)], hexc('#2E1A47'))
    rect(ctx, -46, -128, 92, 12, hexc('#2E1A47'))
    circle(ctx, 8, -110, 4, C['ink'])
    ctx.move_to(4, -92)
    ctx.curve_to(10, -88, 16, -88, 20, -94)
    ctx.set_line_width(3)
    src(ctx, hexc('#5A2030'))
    ctx.stroke()
    for i in range(6):
        line(ctx, -24 + i * 3, -116, -36 + i * 2, -60, 4, hexc('#3F9A5E'))
    ctx.restore()


def world(ctx, cam, T, tod='night', fg=(), bricks=0.0):
    ctx.save()
    cam.apply(ctx)
    landscape(ctx, cam, T, tod)
    tower(ctx, T, tod, bricks)
    for f in fg:
        f(ctx)
    ctx.restore()


def inset(ctx, x, y, r, cam, T, tod, fg=(), border=None, k=1.0):
    """Runde Lupen-Einblendung mit eigener Kamera (Bildschirmkoordinaten)."""
    if k <= 0.001:
        return
    ctx.save()
    ctx.identity_matrix()
    ctx.translate(x, y)
    ctx.scale(k, k)
    circle(ctx, 6, 10, r + 10, alpha(C['shadow'], 0.35))
    circle(ctx, 0, 0, r + 10, border or C['white'])
    ctx.new_sub_path()
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.clip()
    ctx.translate(-x, -y)
    ctx.translate(x - W / 2, y - H / 2)
    world(ctx, cam, T, tod, fg)
    ctx.restore()


def measure(ctx, x, ya, yb, label, col=None, k=1.0, lw=9, fs=72):
    if k <= 0:
        return
    col = col or hexc('#F2C35A')
    yk = lerp(ya, yb, k)
    line(ctx, x, ya, x, yk, lw, col)
    line(ctx, x - 18, ya, x + 18, ya, lw, col)
    if k >= 1:
        line(ctx, x - 18, yb, x + 18, yb, lw, col)
        tw = text_size(ctx, label, fs, SLAB)[0]
        fill_rrect(ctx, x - tw / 2 - 16, (ya + yb) / 2 - fs * 0.7, tw + 32, fs * 1.4, 10, P['paper'])
        text(ctx, label, x, (ya + yb) / 2, fs, P['red'], font=SLAB)


def glow_ring(ctx, x, y, k, r=40, col=None):
    if k <= 0:
        return
    ctx.new_sub_path()
    ctx.arc(x, y, r * (0.6 + 0.4 * k) + 6 * math.sin(k * 10), 0, 2 * math.pi)
    ctx.set_line_width(7)
    src(ctx, alpha(col or C['yellow'], k))
    ctx.stroke()


def big_x(ctx, x, y, s, k):
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * k, s * k)
    circle(ctx, 0, 0, 36, C['white'])
    cross_icon(ctx, 0, 0, 16)
    ctx.restore()


def shelly_room(c, T, x=40, expr='smile', arms=None, face=0.4):
    shelly(c, x, TOPY - 26, 0.95, expr=expr, blink=blink(T), arms=arms, face=face)


WIDE = (0, -1160, 0.66)


# ---------------------------------------------------------------- Szenen
def sc_hook(ctx, T):
    cam = cam_path(T, [(0.0, 20, TOPY - 140, 2.2), (2.6, 80, TOPY + 200, 1.0), (4.4, *WIDE)])

    def fg(c):
        coil(c, 100, TOPY - 26, 0.9)
        shelly_room(c, T, 20, 'o' if T > 3.6 else 'smile', {'R': (34, -120 + math.sin(T * 8) * 10)} if T < 3.6 else None)
        measure(c, -420, 0, TOPY, '120 M', k=ease(T, 1.2, 2.2))
        if T >= 4.5:
            kk = ease(T, 4.5, 5.6)
            braid(c, [(RINGX, RING_TOP), (RINGX, RING_TOP + 90 * M * kk)])
            measure(c, 470, RING_TOP, RING_TOP + 90 * M * kk, '90 M', hexc('#7DE0A0'), 1.0 if kk >= 1 else kk)
    world(ctx, cam, T, 'night', [fg])
    if T >= 5.9:
        card(ctx, T, 5.9, [('KEIN RETTER', 60, SLAB, P['red'])], 540, 300, -3)
    if T >= 7.7:
        card(ctx, T, 7.7, [('TROTZDEM', 34, TYPE, P['ink']), ('UNTEN AM STRAND!', 52, SLAB, hexc('#2F8A4A'))], 540, 470, 2)
        k = back_out(T, 8.6, 9.0, 1.8) if T >= 8.6 else 0
        inset(ctx, 760, 1460, 210, Cam(-160, -90, 1.6), T, 'dawn',
              [lambda c: shelly(c, -160, 40, 1.2, arms={'R': (30, -150 + math.sin(T * 8) * 10), 'L': (-30, -150)}, expr='open', blink=blink(T))], k=k)


def sc_witch(ctx, T):
    t0 = 10.6
    cam = cam_path(T, [(t0, 0, TOPY - 60, 1.0), (14.2, 0, TOPY - 60, 1.0), (14.7, 0, -420, 1.1), (15.4, 0, -420, 1.1), (16.2, 0, TOPY - 60, 0.95)])

    def fg(c):
        shelly_room(c, T, 20, 'think' if T < 17.8 else 'o')
        if T < 17.6:
            a = (T - t0) * 0.9
            witch(c, math.cos(a) * 560, TOPY - 120 + math.sin(a) * 160, 1.15, T, 1 if math.sin(a) > 0 else -1)
        else:
            k = ease(T, 17.6, 19.2)
            witch(c, lerp(560, 1700, k), lerp(TOPY - 100, TOPY - 900, k), 1.15 * (1 - 0.5 * k), T, 1)
        if 14.3 <= T < 16.0:
            glow_ring(c, 0, -110, ease(T, 14.5, 14.9), 120, P['red'])
    bricks = ease(T, 21.3, 22.2)
    world(ctx, cam, T, 'night', [fg], bricks)
    if T < 17.8:
        card(ctx, T, 10.8, [('DIE MEERHEXE', 58, SLAB, P['ink'])], 540, 300, -2)
        if T >= 14.3:
            card(ctx, T, 14.4, [('KEINE TÜR!', 58, SLAB, P['red'])], 540, 1520, 2)
    else:
        card(ctx, T, 17.8, [('HEUTE NACHT:', 32, TYPE, P['ink']), ('HEXE WEG', 60, SLAB, P['ink'])], 540, 300, -2)
        if T >= 19.8:
            card(ctx, T, 19.8, [('MORGEN FRÜH:', 30, TYPE, P['ink']), ('FENSTER ZU!', 60, SLAB, P['red'])], 540, 1520, 2)


def sc_rings(ctx, T):
    cam = cam_path(T, [(22.6, 160, TOPY + 40, 1.7), (25.6, 200, TOPY + 40, 1.7), (27.4, 190, BALY - 40, 1.3), (29.9, 190, BALY - 40, 1.3)])

    def fg(c):
        shelly_room(c, T, 20)
        glow_ring(c, RINGX, RING_TOP, ease(T, 24.9, 25.3), 34)
        measure(c, 430, RING_TOP, BALY, '60 M', k=ease(T, 26.0, 27.4), fs=60)
        glow_ring(c, BAL_RING[0], BAL_RING[1] + 14, ease(T, 29.1, 29.5), 34)
    world(ctx, cam, T, 'night', [fg])
    card(ctx, T, 22.7, [('SCHAU GENAU HIN', 50, SLAB, P['ink'])], 540, 300, -2)
    if T >= 25.1:
        card(ctx, T, 25.1, [('EISENRING', 52, SLAB, P['ink']), ('UNTER DEM FENSTER', 30, TYPE, P['red'])], 540, 1500, 2)


def room_close(ctx, T, fg):
    cam = Cam(-10, TOPY - 150, 2.6)
    world(ctx, cam, T, 'night', [fg])


def scissors(ctx, x, y, s, o=0.3):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for sg in (1, -1):
        ctx.save()
        ctx.rotate(sg * o)
        poly(ctx, [(0, -4), (70, -1), (70, 1), (0, 4)], hexc('#C9CCD8'))
        ctx.new_sub_path()
        ctx.arc(-18, sg * 8, 12, 0, 2 * math.pi)
        ctx.set_line_width(6)
        src(ctx, P['red'])
        ctx.stroke()
        ctx.restore()
    circle(ctx, 0, 0, 4, C['ink'])
    ctx.restore()


def sc_rope(ctx, T):
    def fg(c):
        coil(c, 90, TOPY - 26, 1.1)
        scissors(c, -110, TOPY - 112, 0.6, 0.2 + 0.15 * math.sin(T * 5))
        shelly_room(c, T, -30, 'open', {'R': (40, -96)})
        glow_ring(c, 90, TOPY - 60, ease(T, 30.9, 31.3), 70)
        glow_ring(c, -100, TOPY - 116, ease(T, 34.5, 34.9), 46)
    room_close(ctx, T, fg)
    card(ctx, T, 30.9, [('SEIL AUS SEETANG', 48, SLAB, P['ink']), ('90 M · SUPERSTARK', 40, SLAB, hexc('#2F8A4A'))], 540, 300, -2)
    if T >= 34.5:
        card(ctx, T, 34.5, [('+ SCHERE', 54, SLAB, P['red'])], 540, 1560, 3)


def sc_idea1(ctx, T):
    t0 = 35.4
    cam = cam_path(T, [(t0, 140, TOPY + 300, 1.0), (37.6, 140, TOPY + 300, 1.0), (39.0, 120, BALY - 60, 1.0), (41.0, *WIDE)])
    tie = ease(T, 36.6, 37.4)
    yb = RING_TOP + 90 * M * tie
    k = ease(T, 37.9, 38.9)
    sy = lerp(RING_TOP + 140, BALY - 6, k)

    def fg(c):
        braid(c, [(RINGX, RING_TOP), (RINGX, yb)])
        if T >= 37.6:
            if k < 1:
                hang(c, T, RINGX, sy + 100, 0.62, sway=True)
            else:
                shelly(c, 210, BALY, 0.62, expr='think', blink=blink(T), face=0.3)
        if T >= 40.0:
            glow_ring(c, RINGX, RING_TOP, ease(T, 40.0, 40.4), 50, P['red'])
            big_x(c, RINGX + 80, RING_TOP + 10, 1.6, pop(T, 40.4))
        measure(c, 470, BALY, 0, '60 M', P['red'], ease(T, 41.6, 42.6), fs=90)
    world(ctx, cam, T, 'night', [fg])
    card(ctx, T, t0 + 0.05, [('IDEE 1', 30, TYPE, P['ink']), ('OBEN FESTBINDEN', 52, SLAB, P['ink'])], 540, 280, -2)
    if T >= 40.0:
        card(ctx, T, 40.0, [('SEIL HÄNGT OBEN FEST!', 40, SLAB, P['red'])], 540, 1580, 2)


def sc_idea2(ctx, T):
    t0 = 44.1
    cam = cam_path(T, [(t0, 160, TOPY + 300, 1.0), (47.6, 160, TOPY + 300, 1.0), (49.4, 150, -1500, 0.85)])
    kk = ease(T, 45.4, 46.4)
    kd = ease(T, 48.4, 49.6)
    L = lerp(90, 45, kd) * M

    def fg(c):
        if T < 48.4:
            braid(c, [(RINGX - 12, RING_TOP), (RINGX - 12, RING_TOP + 90 * M * kk)])
        else:
            braid(c, [(RINGX - 12, RING_TOP + L), (RINGX - 12, RING_TOP), (RINGX + 12, RING_TOP), (RINGX + 12, RING_TOP + L)])
            if kd >= 1:
                measure(c, 470, RING_TOP, RING_TOP + 45 * M, '45 M', hexc('#7DE0A0'), fs=60)
                k3 = ease(T, 51.3, 52.0)
                if k3 > 0:
                    gy0, gy1 = RING_TOP + 45 * M, BALY
                    ctx_dash = c
                    ctx_dash.set_dash([16, 12])
                    line(c, RINGX, gy0, RINGX, lerp(gy0, gy1, k3), 8, P['red'])
                    c.set_dash([])
                    if k3 >= 1:
                        fill_rrect(c, RINGX + 30, (gy0 + gy1) / 2 - 44, 200, 88, 10, P['red'])
                        text(c, '15 M', RINGX + 130, (gy0 + gy1) / 2, 54, C['white'], font=SLAB)
        shelly_room(c, T, 20, 'think')
    world(ctx, cam, T, 'night', [fg])
    card(ctx, T, t0 + 0.05, [('IDEE 2', 30, TYPE, P['ink']), ('DOPPELT DURCH DEN RING', 44, SLAB, P['ink'])], 540, 280, -2)
    if T >= 52.0:
        card(ctx, T, 52.0, [('15 M FEHLEN!', 58, SLAB, P['red'])], 540, 1600, 2)


def hourglass(ctx, x, y, k, sc):
    if sc <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    rect(ctx, -60, -110, 120, 14, P['wood2'])
    rect(ctx, -60, 96, 120, 14, P['wood2'])
    poly(ctx, [(-48, -96), (48, -96), (6, 0), (48, 96), (-48, 96), (-6, 0)], alpha(hexc('#DFF4FF'), 0.85))
    top = 1 - k
    poly(ctx, [(-40 * top, -90 + 80 * (1 - top)), (40 * top, -90 + 80 * (1 - top)), (4, -6), (-4, -6)], hexc('#E3C58A'))
    poly(ctx, [(-44, 92), (44, 92), (44 * k * 0.6, 92 - 60 * k), (-44 * k * 0.6, 92 - 60 * k)], hexc('#E3C58A'))
    ctx.restore()


def sc_dawn(ctx, T):
    cam = cam_path(T, [(53.4, *WIDE), (55.4, -60, -260, 1.6), (62.2, -60, -260, 1.6)])

    def fg(c):
        shelly(c, -180, 40, 1.15, arms={'R': (30, -150 + math.sin(T * 8) * 10), 'L': (-30, -150)}, expr='open', blink=blink(T))
    world(ctx, cam, T, 'dawn', [fg])
    if T < 58.0:
        card(ctx, T, 53.5, [('BEI SONNENAUFGANG', 44, SLAB, P['ink']), ('UNTEN AM STRAND', 50, SLAB, hexc('#2F8A4A'))], 540, 300, -2)
    else:
        card(ctx, T, 58.0, [('WIE HAT SIE', 56, SLAB, P['ink']), ('DAS GESCHAFFT?', 60, SLAB, P['red'])], 540, 300, -2)
    if T >= 59.2:
        card(ctx, T, 59.2, [('IN DIE KOMMENTARE!', 36, SLAB, P['red'])], 540, 500, 2)
    if T >= GAP_AT:
        hourglass(ctx, 860, 800, clamp((T - GAP_AT) / GAP), pop(T, GAP_AT))


def sc_cut(ctx, T):
    t0 = G(62.22)
    tc = G(63.56)

    def fg(c):
        yy = TOPY - 60
        if T < tc + 0.25:
            braid(c, [(-170, yy), (170, yy)], w=14)
            scissors(c, lerp(150, -60, ease(T, t0, tc)), yy, 0.7, 0.15 + 0.3 * abs(math.sin(T * 12)))
        else:
            k = ease(T, tc + 0.25, tc + 0.6)
            braid(c, [(-170, yy + 10 * k), (-60, yy + 10 * k)], w=14)
            braid(c, [(-40, yy - 10 * k), (170, yy - 10 * k)], w=14)
            if T >= G(65.5):
                fill_rrect(c, -160, yy + 26, 90, 40, 8, P['paper'])
                text(c, '30 M', -115, yy + 46, 26, P['ink'], font=SLAB)
            if T >= G(67.08):
                fill_rrect(c, 20, yy - 70, 110, 40, 8, P['paper'])
                text(c, '60 M', 75, yy - 50, 26, P['red'], font=SLAB)
        shelly_room(c, T, -150, 'open', {'R': (40, -96)})
    room_close(ctx, T, fg)
    if T < G(63.28):
        card(ctx, T, t0 + 0.05, [('DIE LÖSUNG', 76, SLAB, P['ink'])], 540, 300, -2)
    else:
        card(ctx, T, G(63.28), [('IN 2 STÜCKE', 70, SLAB, P['red'])], 540, 300, -2)


def sc_setup(ctx, T):
    t0 = G(68.26)
    cam = cam_path(T, [(t0, 180, TOPY + 220, 1.25), (G(72.6), 190, TOPY + 320, 1.05), (G(77.2), 150, -1450, 0.8)])
    ks = ease(T, G(69.6), G(70.6))
    kl = ease(T, G(73.6), G(76.6))

    def fg(c):
        braid(c, [(RINGX, RING_TOP), (RINGX, RING_TOP + (LOOPY - RING_TOP) * ks)])
        if ks >= 1 and T >= G(71.6):
            loop(c, RINGX, LOOPY)
            glow_ring(c, RINGX, LOOPY + 12, ease(T, G(71.8), G(72.2)) * (1 - ease(T, G(73.0), G(73.4))), 40)
        if kl > 0:
            Lh = 30 * M * kl
            braid(c, [(RINGX - 14, LOOPY + 26 + Lh), (RINGX - 14, LOOPY + 26), (RINGX + 14, LOOPY + 26), (RINGX + 14, LOOPY + 26 + Lh)],
                  col=hexc('#62BF7A'))
        if T >= G(77.22):
            measure(c, 470, RING_TOP, LOOPY, '30 M', hexc('#7DE0A0'), fs=60)
            measure(c, 470, LOOPY + 26, BALY, '30 M', hexc('#B9F0C0'), fs=60)
        shelly_room(c, T, 20, 'smile')
    world(ctx, cam, T, 'night', [fg])
    if T < G(72.92):
        card(ctx, T, t0 + 0.05, [('KURZES STÜCK OBEN', 44, SLAB, P['ink']), ('+ SCHLAUFE', 40, SLAB, hexc('#2F8A4A'))], 540, 280, -2)
    else:
        card(ctx, T, G(72.92), [('LANGES STÜCK', 44, SLAB, P['ink']), ('DURCH DIE SCHLAUFE', 40, SLAB, hexc('#2F8A4A'))], 540, 280, -2)
        if T >= G(75.26) and T < G(77.2):
            k = back_out(T, G(75.26), G(75.6), 1.8)
            ctx.save()
            ctx.translate(820, 1500)
            ctx.scale(k, k)
            circle(ctx, 0, 0, 120, P['paper'])
            ellipse(ctx, 0, 30, 90, 40, hexc('#C8322E'))
            for i in range(3):
                circle(ctx, -40 + i * 40, 10, 8, C['white'])
            line(ctx, -60, -40, 60, 20, 6, C['ink'])
            line(ctx, -60, 20, 60, -40, 6, C['ink'])
            ctx.restore()
    if T >= G(79.62):
        card(ctx, T, G(79.62), [('GENAU BIS ZUM BALKON', 40, SLAB, P['red'])], 540, 1600, 2)


def rig(c):
    braid(c, [(RINGX, RING_TOP), (RINGX, LOOPY)])
    loop(c, RINGX, LOOPY)


def sc_climb(ctx, T):
    t0 = G(80.9)
    t_l = G(83.52)
    t_b = G(85.9)
    if T < t_l:
        y = lerp(RING_TOP + 160, LOOPY + 20, ease(T, t0 + 0.2, t_l))
        xr = RINGX
    else:
        y = lerp(LOOPY + 170, BALY, ease(T, t_l, t_b))
        xr = RINGX - 14
    cam = Cam(220, y - 160, 1.25)

    def fg(c):
        rig(c)
        braid(c, [(RINGX - 14, BALY - 4), (RINGX - 14, LOOPY + 26), (RINGX + 14, LOOPY + 26), (RINGX + 14, BALY - 4)], col=hexc('#62BF7A'))
        if T < t_b:
            hang(c, T, xr, y + 120, 0.75)
        else:
            shelly(c, 220, BALY, 0.75, expr='open', blink=blink(T), face=0.3)
    world(ctx, cam, T, 'night', [fg])
    if T < t_l:
        card(ctx, T, t0 + 0.05, [('KURZES STÜCK', 50, SLAB, P['ink']), ('BIS ZUR SCHLAUFE', 34, TYPE, P['red'])], 540, 280, -2)
    else:
        card(ctx, T, t_l, [('DOPPELTES STÜCK', 50, SLAB, P['ink']), ('BIS ZUM BALKON', 34, TYPE, P['red'])], 540, 280, -2)
    inset(ctx, 820, 1540, 190, Cam(150, -1300, 0.36), T, 'night',
          [rig, lambda c: braid(c, [(RINGX - 14, BALY - 4), (RINGX - 14, LOOPY + 26), (RINGX + 14, LOOPY + 26), (RINGX + 14, BALY - 4)], col=hexc('#62BF7A')),
           lambda c: circle(c, xr, y, 30, P['red'])], k=back_out(T, t0 + 0.4, t0 + 0.8, 1.8))


def sc_pull(ctx, T):
    t0 = G(86.36)
    tp = G(87.74)
    k = ease(T, tp, G(90.9))
    cam = cam_path(T, [(t0, 230, BALY - 260, 1.2), (tp, 230, BALY - 260, 1.2), (G(89.0), 240, -1650, 0.8)])

    def fg(c):
        rig(c)
        if k < 0.02:
            braid(c, [(RINGX - 14, BALY - 4), (RINGX - 14, LOOPY + 26), (RINGX + 14, LOOPY + 26), (RINGX + 14, BALY - 4)], col=hexc('#62BF7A'))
        else:
            # freies Ende läuft hoch, über die Schlaufe und auf der anderen Seite herunter
            up = 30 * M * k * 2
            Lfree = 30 * M - up
            if Lfree > 0:
                braid(c, [(RINGX - 14, LOOPY + 26 + Lfree), (RINGX - 14, LOOPY + 26), (RINGX + 14, LOOPY + 26), (RINGX + 14, BALY - 4)], col=hexc('#62BF7A'))
            else:
                fall = min(30 * M, -Lfree)
                braid(c, [(RINGX + 14, LOOPY + 26 + fall), (RINGX + 14, BALY - 4)], col=hexc('#62BF7A'))
        if k > 0.95:
            coil(c, 250, BALY, 0.7)
        shelly(c, 230, BALY, 0.75, arms={'R': (18, -150)} if k < 0.95 else {'R': (34, -100)}, expr='open', blink=blink(T), face=0.3)
    world(ctx, cam, T, 'night', [fg])
    card(ctx, T, t0 + 0.05, [('EIN ENDE LOSLASSEN', 44, SLAB, P['ink']), ('AM ANDEREN ZIEHEN', 44, SLAB, hexc('#2F8A4A'))], 540, 280, -2)
    if T >= G(90.6):
        card(ctx, T, G(90.6), [('LANGES STÜCK', 40, SLAB, P['ink']), ('ZURÜCK!', 66, SLAB, hexc('#2F8A4A'))], 540, 1600, 2)


def sc_down(ctx, T):
    t0 = G(91.58)
    tf = G(95.4)
    k = ease(T, G(93.1), tf - 0.2)
    y = lerp(BALY + 150, 40, k)
    tod = 'night' if T < tf - 0.6 else 'dawn'
    cam = Cam(lerp(220, 60, k), lerp(BALY - 100, -380, k), lerp(1.2, 1.1, k))

    def fg(c):
        rig(c)
        braid(c, [(BAL_RING[0], BAL_RING[1] + 28), (BAL_RING[0], BAL_RING[1] + 28 + 60 * M)], col=hexc('#62BF7A'))
        if T < tf:
            hang(c, T, BAL_RING[0], y, 0.75)
        else:
            shelly(c, 60, 40, 1.15, arms={'R': (30, -150 + math.sin(T * 8) * 10), 'L': (-30, -150 - math.sin(T * 8) * 10)},
                   expr='open', blink=blink(T))
    world(ctx, cam, T, tod, [fg])
    card(ctx, T, t0 + 0.05, [('AM BALKON FESTBINDEN', 40, SLAB, P['ink']), ('60 M RUNTER', 54, SLAB, hexc('#2F8A4A'))], 540, 280, -2)
    if T >= tf:
        card(ctx, T, tf, [('FREI!', 120, SLAB, hexc('#2F8A4A'))], 540, 560, 3)


def sc_you(ctx, T):
    cam = Cam(-60, -260, 1.6)

    def fg(c):
        coil(c, 60, 40, 1.4)
        shelly(c, -180, 40, 1.15, arms={'R': (46, -112)}, expr='smile', blink=blink(T))
    world(ctx, cam, T, 'dawn', [fg])
    card(ctx, T, G(96.28), [('HÄTTEST DU DAS SEIL', 44, SLAB, P['ink']), ('GETEILT?', 76, SLAB, P['red'])], 540, 300, -2)
    if T >= G(99.16):
        card(ctx, T, G(99.16), [('IN DIE KOMMENTARE!', 36, SLAB, P['red'])], 540, 520, 2)


def hut(ctx, T, t0, x, y):
    if T < t0:
        return
    k = back_out(T, t0, t0 + 0.35, 2.0)
    if k <= 0.001:
        return
    ctx.save()
    ctx.identity_matrix()
    ctx.translate(x, y)
    ctx.scale(k, k)
    rect(ctx, -95, -150, 190, 150, hexc('#E9B77A'))
    for i in range(6):
        line(ctx, -95, -128 + i * 24, 95, -128 + i * 24, 3, alpha(hexc('#B8864E'), 0.7))
    poly(ctx, [(-125, -140), (0, -235), (125, -140)], C['pink2'])
    poly(ctx, [(-105, -146), (0, -222), (105, -146)], C['pink'])
    fill_rrect(ctx, -30, -100, 60, 100, 10, hexc('#7FC8C2'))
    fill_rrect(ctx, -95, -305, 190, 58, 6, P['paper'])
    text(ctx, 'DEIN NAME', 0, -276, 30, P['ink'], font=SLAB)
    line(ctx, 0, -247, 0, -236, 6, P['gold'])
    ctx.restore()


def sc_outro(ctx, T):
    cam = Cam(-60, -260, 1.6)

    def fg(c):
        shelly(c, -180, 40, 1.15, arms={'R': (32, -140 + math.sin(T * 8) * 10)}, expr='open', blink=blink(T))
    world(ctx, cam, T, 'dawn', [fg])
    card(ctx, T, G(101.4), [('WOHNST DU SCHON IN', 34, TYPE, P['ink']), ('MUSCHELTAL?', 80, SLAB, P['ink'])], 540, 300, -2)
    tf = G(103.7)
    tap = G(104.9) + 0.6
    if UI_ON[0] and T >= tf:
        k = back_out(T, tf, tf + 0.3, 2.0)
        ctx.save()
        ctx.translate(540, 530)
        ctx.scale(max(k, 0.01), max(k, 0.01))
        on = T >= tap
        fill_rrect(ctx, -170 + 6, -50 + 10, 340, 100, 14, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -170, -50, 340, 100, 14, C['green'] if on else P['red'])
        text(ctx, 'GEFOLGT' if on else 'FOLGEN', -24 if on else 0, 0, 48, C['white'], font=SLAB)
        if on:
            tick_mark(ctx, 120, 0, 34, C['white'])
        ctx.restore()
    hut(ctx, T, G(104.6), 800, 1350)


SC = [(0.0, sc_hook), (10.6, sc_witch), (22.6, sc_rings), (30.1, sc_rope), (35.4, sc_idea1), (44.1, sc_idea2), (53.4, sc_dawn),
      (G(62.2), sc_cut), (G(68.2), sc_setup), (G(80.85), sc_climb), (G(86.3), sc_pull), (G(91.5), sc_down), (G(96.2), sc_you),
      (G(100.6), sc_outro)]


def frame(ctx, T):
    cur = SC[0]
    for s_ in SC:
        if T >= s_[0]:
            cur = s_
    cur[1](ctx, T)
    for s_ in SC[1:]:
        if 0 <= T - s_[0] < 0.08:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.25 * (1 - (T - s_[0]) / 0.08)))
