"""Shelly und der Leuchtturm – Seil-Rätsel im Retro-Stil (Muscheltal)."""
import json, math, os, random, re
import cairo
from draw import *
from chars import shelly
import retro
from retro import P, SLAB, TYPE, ZILLA

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = json.load(open(f'{ROOT}/audio/vo_words.json'))


def _norm(w):
    w = re.sub(r"[^\wäöüß']", '', w.lower()).replace('ß', 'ss')
    return {'120': 'hundertzwanzig', '90': 'neunzig', '60': 'sechzig', '45': 'fünfundvierzig', '15': 'fünfzehn',
            '30': 'dreissig', 'shelley': 'shelly'}.get(w, w)


def nw(prefix, k=0, after=-1.0, end=False):
    hits = [w for w in NEW if _norm(w[0]) == prefix and w[1] > after]
    if len(hits) <= k:
        hits = [w for w in NEW if _norm(w[0]).startswith(prefix) and w[1] > after]
    return hits[k][2 if end else 1]


GAP_AT = nw('hörst', 0, end=True) + 0.1
GAP = 2.0
VO_END = NEW[-1][2] + 0.3


def gn(t):
    return t + (GAP if t >= GAP_AT else 0.0)


def TW(prefix, k=0, after=-1.0, end=False):
    return gn(nw(prefix, k, after, end))


END = gn(VO_END) + 1.6
blink = retro.blink


def card(ctx, *a, **k):
    ctx.save()
    ctx.identity_matrix()
    retro.paper_card(ctx, *a, **k)
    ctx.restore()


# ---------------------------------------------------------------- Welt (1 m = 20 px, Boden y = 0)
M = 20.0
TOP = -120 * M
BAL = -60 * M
RX = 700.0          # x der Ringe / des Seils


def ym(m):
    """Höhe in Metern -> Welt-y."""
    return -m * M


def tower_halfw(y):
    k = clamp(-y / -TOP)
    return lerp(170, 110, k)


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


def sky(ctx, cam, T, tod):
    x0, y0, x1, y1 = cam.bounds()
    stops = {'night': [(0, hexc('#0E1438')), (1, hexc('#3B3A7A'))],
             'dawn': [(0, hexc('#3B3A7A')), (0.6, hexc('#E07A8A')), (1, hexc('#FFC27A'))]}[tod]
    g = cairo.LinearGradient(0, TOP - 600, 0, 0)
    for o, c in stops:
        g.add_color_stop_rgba(o, *c)
    ctx.rectangle(x0, y0, x1 - x0, min(y1, 0) - y0 + 2)
    ctx.set_source(g)
    ctx.fill()
    r = random.Random(2)
    for i in range(160):
        sx, sy = r.uniform(-1400, 2400), r.uniform(TOP - 900, -300)
        if x0 < sx < x1 and y0 < sy < y1:
            a = 0.4 + 0.5 * math.sin(T * 2 + i) if tod == 'night' else 0.2
            circle(ctx, sx, sy, r.uniform(2, 4) / max(cam.z, 0.3), alpha(C['white'], a))
    if tod == 'night':
        circle(ctx, 1000, TOP - 300, 90, hexc('#FFF2C2'))
        circle(ctx, 1030, TOP - 320, 80, hexc('#1A2150'))
    else:
        circle(ctx, 900, -60, 220, alpha(hexc('#FFD27A'), 0.4))
        circle(ctx, 900, -60, 160, hexc('#FFB45A'))
    for i, (cx, cy, s) in enumerate([(-200, -1900, 120), (1100, -1500, 140), (200, -900, 100), (1300, -2600, 120)]):
        cloud_shape(ctx, cx + (T * 15) % 200, cy, s, alpha(hexc('#5A5E9A') if tod == 'night' else C['white'], 0.8))


def ground(ctx, cam, T, tod):
    x0, y0, x1, y1 = cam.bounds()
    if y1 < -400:
        return
    # Meer
    sea = hexc('#1C2A5C') if tod == 'night' else hexc('#3B7FB0')
    rect(ctx, x0, -380, x1 - x0, 380, sea)
    for i in range(int(x0 // 140), int(x1 // 140) + 2):
        xx = i * 140 + math.sin(T * 2 + i) * 20
        line(ctx, xx, -340 + (i % 4) * 80, xx + 70, -340 + (i % 4) * 80, 6, alpha(C['white'], 0.35))
    # Strand
    ctx.move_to(x0, 0)
    ctx.curve_to(x0 + 300, -40, x1 - 300, 20, x1, -20)
    ctx.line_to(x1, y1 + 10)
    ctx.line_to(x0, y1 + 10)
    ctx.close_path()
    src(ctx, hexc('#D9B98A') if tod == 'night' else hexc('#F3D9A4'))
    ctx.fill()
    r = random.Random(3)
    for i in range(30):
        sx, sy = r.uniform(-800, 1900), r.uniform(20, 600)
        if x0 < sx < x1:
            ctx.save()
            ctx.translate(sx, sy)
            ctx.scale(1.4, 1.4)
            ctx.move_to(0, 8)
            for j in range(7):
                a = math.radians(200 + j * 140 / 6)
                ctx.line_to(math.cos(a) * 16, math.sin(a) * 16 + 3)
            ctx.close_path()
            src(ctx, r.choice([C['pink3'], C['cream'], hexc('#F9B6A0')]))
            ctx.fill()
            ctx.restore()
    for px in (-160, 1250):
        retro_palm(ctx, px, 30, 520, T)


def retro_palm(ctx, x, y, h, T):
    tx, ty = x + h * 0.1, y - h
    ctx.move_to(x - 18, y)
    ctx.curve_to(x - 8, y - h * 0.5, tx - 12, ty + 40, tx - 8, ty)
    ctx.line_to(tx + 8, ty)
    ctx.curve_to(tx + 8, ty + 40, x + 8, y - h * 0.5, x + 18, y)
    ctx.close_path()
    src(ctx, hexc('#A9744A'))
    ctx.fill()
    for i in range(7):
        a = math.radians(-175 + i * 30) + math.sin(T * 1.6 + i) * 0.05
        lx, ly = tx + math.cos(a) * 190, ty + math.sin(a) * 90 + 60
        ctx.move_to(tx, ty)
        ctx.curve_to(tx + math.cos(a) * 90, ty - 60 + math.sin(a) * 20, lx, ly - 30, lx, ly)
        ctx.curve_to(lx - math.cos(a) * 50, ly - 10, tx + math.cos(a) * 60, ty - 10, tx, ty)
        src(ctx, hexc('#3DAA6A'))
        ctx.fill()


def tower(ctx, T, tod, window_bricked=0.0, beam=True):
    # Rumpf mit roten/weißen Bändern
    n = 12
    for i in range(n):
        ya, yb = TOP * i / n, TOP * (i + 1) / n
        wa, wb = tower_halfw(ya), tower_halfw(yb)
        col = hexc('#E9E2D4') if i % 2 == 0 else hexc('#C8322E')
        poly(ctx, [(540 - wa, ya), (540 + wa, ya), (540 + wb, yb), (540 - wb, yb)], col)
    # Schattierung rechts
    poly(ctx, [(540 + 60, 0), (540 + tower_halfw(0), 0), (540 + tower_halfw(TOP), TOP), (540 + 30, TOP)], alpha(C['ink'], 0.12))
    # kleine Fenster
    for h_ in (20, 45, 80, 100):
        y = ym(h_)
        fill_rrect(ctx, 520, y - 40, 40, 70, 20, hexc('#2B3170'))
    # Laterne
    rect(ctx, 400, TOP - 30, 280, 36, hexc('#3A3F4F'))
    for i in range(9):
        line(ctx, 410 + i * 32, TOP - 30, 410 + i * 32, TOP - 18, 4, hexc('#3A3F4F'))
    fill_rrect(ctx, 440, TOP - 230, 200, 200, 10, hexc('#3A3F4F'))
    rect(ctx, 455, TOP - 215, 170, 170, hexc('#FFE6A8') if tod == 'night' else hexc('#F7EFD9'))
    poly(ctx, [(420, TOP - 230), (660, TOP - 230), (540, TOP - 330)], P['red'])
    circle(ctx, 540, TOP - 340, 14, P['gold'])
    if beam and tod == 'night':
        a = T * 0.8
        for sgn in (1, -1):
            if abs(math.cos(a)) < 0.06:
                continue
            ctx.save()
            ctx.translate(540, TOP - 130)
            ctx.scale(sgn * abs(math.cos(a)) + 0.0001, 1)
            g = cairo.LinearGradient(0, 0, 1800, 0)
            g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.45)
            g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
            poly(ctx, [(0, -40), (1800, -260), (1800, 260), (0, 40)])
            ctx.set_source(g)
            ctx.fill()
            ctx.restore()
    # Fenster der Gefangenen (unter der Laterne)
    wy = TOP + 120
    fill_rrect(ctx, 470, wy - 110, 140, 160, 60, hexc('#3A3F4F'))
    rect(ctx, 480, wy - 100, 120, 140, hexc('#FFE6A8'))
    if window_bricked > 0:
        nrows = int(7 * window_bricked)
        for rr in range(nrows):
            for cc in range(4):
                fill_rrect(ctx, 480 + cc * 30 + (rr % 2) * 10, wy + 40 - (rr + 1) * 20, 28, 18, 2, hexc('#8E8A80'))
    # Ring oben (Halterung nach rechts)
    ring(ctx, RX, ym(119.5))
    line(ctx, 540 + tower_halfw(ym(119.5)), ym(119.5) - 6, RX - 14, ym(119.5) - 6, 8, hexc('#3A3F4F'))
    # Balkon auf 60 m
    bx0 = 540 + tower_halfw(BAL) - 10
    rect(ctx, bx0, BAL, 230, 22, hexc('#5A5E70'))
    for i in range(9):
        line(ctx, bx0 + 10 + i * 26, BAL, bx0 + 10 + i * 26, BAL - 70, 4, hexc('#3A3F4F'))
    line(ctx, bx0, BAL - 70, bx0 + 230, BAL - 70, 6, hexc('#3A3F4F'))
    ring(ctx, RX + 60, BAL + 34)


def ring(ctx, x, y):
    ctx.new_sub_path()
    ctx.arc(x, y + 16, 16, 0, 2 * math.pi)
    ctx.set_line_width(7)
    src(ctx, hexc('#4A4F5E'))
    ctx.stroke()


def rope(ctx, pts, col=None, w=20):
    col = col or hexc('#4FB06A')
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    src(ctx, col)
    ctx.stroke_preserve()
    ctx.set_line_width(w * 0.35)
    ctx.set_dash([10, 10])
    src(ctx, alpha(hexc('#2A6A40'), 0.9))
    ctx.stroke()
    ctx.set_dash([])


def coil(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for i in range(4):
        ellipse(ctx, 0, -i * 10, 50 - i * 4, 16, hexc('#3E8C5A'))
        ellipse(ctx, 0, -i * 10 - 2, 40 - i * 4, 10, hexc('#2A6A40'))
    ctx.restore()


def climber(ctx, T, x, y, s=1.0, climbing=True, expr='smile'):
    """Shelly am Seil (Hände oben)."""
    k = math.sin(T * 8) * 6 if climbing else 0
    shelly(ctx, x - 20 * s, y + 170 * s, s, arms={'R': (20, -150 + k), 'L': (14, -140 - k)}, expr=expr, blink=blink(T), face=0.4)


def witch(ctx, x, y, s, T):
    """Meerhexe auf einem Rochen."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ww = math.sin(T * 5) * 18
    ctx.move_to(-160, ww)
    ctx.curve_to(-80, -30, 80, -30, 160, ww)
    ctx.curve_to(80, 30, -80, 30, -160, ww)
    src(ctx, hexc('#3A4A80'))
    ctx.fill()
    line(ctx, 140, 0, 260, 30, 6, hexc('#3A4A80'))
    for sx in (-20, 20):
        circle(ctx, sx, -10, 5, C['white'])
    # Hexe
    poly(ctx, [(-30, -10), (30, -10), (16, -90), (-16, -90)], hexc('#2E1A47'))
    circle(ctx, 0, -110, 26, hexc('#9BD6A0'))
    poly(ctx, [(-40, -126), (40, -126), (6, -210), (-4, -200)], hexc('#2E1A47'))
    rect(ctx, -48, -132, 96, 12, hexc('#2E1A47'))
    for sx in (-9, 9):
        circle(ctx, sx, -112, 4, C['ink'])
    line(ctx, -8, -96, 8, -98, 3, hexc('#5A2030'))
    for i in range(6):
        line(ctx, -28 + i * 4, -120, -40 + i * 2, -70, 4, hexc('#3E8C5A'))
    ctx.restore()


def world(ctx, cam, T, tod='night', extra=(), bricked=0.0):
    ctx.save()
    cam.apply(ctx)
    sky(ctx, cam, T, tod)
    ground(ctx, cam, T, tod)
    tower(ctx, T, tod, bricked)
    for e in extra:
        e(ctx)
    ctx.restore()


def measure(ctx, x, ya, yb, label, col=None, k=1.0):
    """Maßpfeil in Weltkoordinaten."""
    if k <= 0:
        return
    col = col or C['yellow']
    yb2 = lerp(ya, yb, k)
    line(ctx, x, ya, x, yb2, 8, col)
    line(ctx, x - 24, ya, x + 24, ya, 8, col)
    if k >= 1:
        line(ctx, x - 24, yb, x + 24, yb, 8, col)
        ctx.save()
        ctx.translate(x - 40, (ya + yb) / 2)
        ctx.rotate(-math.pi / 2)
        tw = text_size(ctx, label, 70, SLAB)[0]
        fill_rrect(ctx, -tw / 2 - 20, -50, tw + 40, 100, 12, P['paper'])
        text(ctx, label, 0, 0, 70, P['ink'], font=SLAB)
        ctx.restore()


def big_x(ctx, x, y, s, k):
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * k, s * k)
    circle(ctx, 0, 0, 40, C['white'])
    cross_icon(ctx, 0, 0, 18)
    ctx.restore()


# ---------------------------------------------------------------- Szenen
CAM_FULL = Cam(560, -1250, 0.62)


def sc_hook(ctx, T, t0):
    k = ease(T, 0, 2.0)
    cam = Cam(lerp(560, 560, k), lerp(TOP + 200, -1250, k), lerp(1.4, 0.62, k))

    def ex(c):
        shelly(c, 540, TOP + 160, 1.0, arms={'R': (34, -140 + math.sin(T * 8) * 10)}, expr='o', blink=blink(T))
        measure(c, 220, 0, TOP, '120 M', k=ease(T, nw('hundertzwanzig') - 0.2, nw('hundertzwanzig') + 0.4))
        if T >= nw('neunzig') - 0.2:
            kk = ease(T, nw('neunzig') - 0.2, nw('neunzig') + 0.5)
            rope(c, [(RX, ym(119.5) + 30), (RX, ym(119.5) + 30 + 90 * M * kk)])
            measure(c, 900, ym(119.5), ym(119.5) + 90 * M * kk, '90 M', hexc('#7DE0A0'), 1.0 if kk >= 1 else kk)
    world(ctx, cam, T, 'night', [ex])
    if T >= nw('niemand') - 0.2:
        card(ctx, T, nw('niemand') - 0.2, [('KEIN RETTER', 60, SLAB, P['red'])], 540, 380, -3)
    if T >= nw('trotzdem') - 0.1:
        card(ctx, T, nw('trotzdem') - 0.1, [('TROTZDEM', 36, TYPE, P['ink']), ('UNTEN AM STRAND!', 52, SLAB, P['ink'])], 540, 560, 2)


def sc_witch(ctx, T, t0):
    cam = Cam(560, TOP + 500, 0.75)
    t_away = nw('heute') - 0.2

    def ex(c):
        shelly(c, 540, TOP + 160, 1.0, expr='think' if T < t_away else 'o', blink=blink(T))
        if T < t_away:
            a = (T - t0) * 1.2
            witch(c, 540 + math.cos(a) * 520, TOP + 200 + math.sin(a) * 140, 1.3, T)
        else:
            k = ease(T, t_away, t_away + 1.5)
            witch(c, lerp(900, 1900, k), lerp(TOP + 200, TOP - 600, k), 1.3 * (1 - 0.6 * k), T)
    world(ctx, cam, T, 'night', [ex], bricked=ease(T, nw('maurt') - 0.3, nw('maurt') + 0.8) * (1 - ease(T, nw('maurt') + 1.0, nw('maurt') + 1.3)))
    if T < t_away:
        card(ctx, T, nw('meerhexe') - 0.1, [('DIE MEERHEXE', 56, SLAB, P['ink'])], 540, 380, -2)
        if T >= nw('tür') - 0.2:
            card(ctx, T, nw('tür') - 0.2, [('KEINE TÜR', 56, SLAB, P['red'])], 540, 1480, 2)
    else:
        card(ctx, T, t_away + 0.05, [('HEUTE NACHT:', 34, TYPE, P['ink']), ('HEXE WEG', 60, SLAB, P['ink'])], 540, 380, -2)
        if T >= nw('morgen') - 0.1:
            card(ctx, T, nw('morgen') - 0.1, [('MORGEN FRÜH:', 30, TYPE, P['ink']), ('FENSTER ZU!', 60, SLAB, P['red'])], 540, 1480, 2)


def sc_rings(ctx, T, t0):
    t_bal = nw('sechzig') - 0.3
    k = ease(T, t_bal - 0.2, t_bal + 1.4)
    cam = Cam(620, lerp(TOP + 200, -1650, k), lerp(1.1, 0.75, k))

    def ex(c):
        shelly(c, 540, TOP + 160, 1.0, expr='smile', blink=blink(T))
        if T >= nw('eisenring') - 0.2:
            kk = pop(T, nw('eisenring') - 0.2)
            c.save(); c.translate(RX, ym(119.5) + 16); c.scale(kk, kk)
            c.new_sub_path(); c.arc(0, 0, 50, 0, 2 * math.pi); c.set_line_width(8); src(c, C['yellow']); c.stroke(); c.restore()
        measure(c, 940, ym(119.5), BAL, '60 M', k=ease(T, t_bal, t_bal + 1.0))
        if T >= nw('eisenring', 1) - 0.2:
            kk = pop(T, nw('eisenring', 1) - 0.2)
            c.save(); c.translate(RX + 60, BAL + 50); c.scale(kk, kk)
            c.new_sub_path(); c.arc(0, 0, 50, 0, 2 * math.pi); c.set_line_width(8); src(c, C['yellow']); c.stroke(); c.restore()
    world(ctx, cam, T, 'night', [ex])
    card(ctx, T, t0 + 0.05, [('SCHAU GENAU HIN', 50, SLAB, P['ink'])], 540, 380, -2)
    if T >= nw('balkon') - 0.2:
        card(ctx, T, nw('balkon') - 0.2, [('BALKON', 56, SLAB, P['ink']), ('MIT RING', 34, TYPE, P['red'])], 540, 1480, 2)


def room_bg(ctx, T):
    rect(ctx, 0, 0, W, H, hexc('#E9E2D4'))
    for i in range(0, H, 60):
        line(ctx, 0, i, W, i, 2, alpha(hexc('#C9BFAE'), 0.6))
    fill_rrect(ctx, 240, 300, 600, 700, 280, hexc('#3A3F4F'))
    fill_rrect(ctx, 270, 330, 540, 640, 260, hexc('#1A2150'))
    r = random.Random(3)
    for i in range(40):
        circle(ctx, r.uniform(320, 760), r.uniform(380, 900), r.uniform(1.5, 3), alpha(C['white'], 0.7))
    circle(ctx, 640, 520, 50, hexc('#FFF2C2'))
    rect(ctx, 0, 1400, W, 520, P['wood'])
    for i in range(0, W, 120):
        line(ctx, i, 1400, i, H, 3, P['wood3'])
    g = cairo.RadialGradient(860, 900, 10, 860, 900, 500)
    g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.35)
    g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()


def scissors(ctx, x, y, s, open_=0.3):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for sg in (1, -1):
        ctx.save()
        ctx.rotate(sg * open_)
        line(ctx, 0, 0, 90, 0, 8, hexc('#B9BFCF'))
        ctx.new_sub_path()
        ctx.arc(-22, sg * 10, 16, 0, 2 * math.pi)
        ctx.set_line_width(7)
        src(ctx, P['red'])
        ctx.stroke()
        ctx.restore()
    circle(ctx, 0, 0, 5, C['ink'])
    ctx.restore()


def sc_rope(ctx, T, t0):
    room_bg(ctx, T)
    coil(ctx, 540, 1440, 3.0)
    scissors(ctx, 820, 1400, 1.6, 0.25 + 0.15 * math.sin(T * 4))
    shelly(ctx, 300, 1520, 2.4, arms={'R': (34, -100)}, expr='open', blink=blink(T))
    card(ctx, T, nw('seil', 1) - 0.2, [('SEIL AUS SEETANG', 50, SLAB, P['ink']), ('90 M', 80, SLAB, hexc('#2F8A4A'))], 540, 380, -2)
    if T >= nw('schere') - 0.2:
        card(ctx, T, nw('schere') - 0.2, [('+ SCHERE', 50, SLAB, P['red'])], 760, 1150, 4)


def sc_idea1(ctx, T, t0):
    t_bal = nw('balkon', 1) - 0.6
    t_stuck = nw('aber', 1) - 0.1
    cam = CAM_FULL
    top_y = ym(119.5) + 30
    bot = top_y + 90 * M

    def ex(c):
        kk = ease(T, t0 + 0.2, t0 + 1.2)
        rope(c, [(RX, top_y), (RX, top_y + (bot - top_y) * kk)])
        k = ease(T, t_bal - 0.4, t_bal + 0.8)
        cy = lerp(TOP + 160, BAL - 40, k)
        if T > t0 + 0.6:
            climber(c, T, RX, cy - 170, 1.0, 0 < k < 1)
        if T >= t_stuck:
            measure(c, 980, BAL, 0, '60 M', P['red'], ease(T, nw('unter', 1) - 0.2, nw('unter', 1) + 0.6))
            big_x(c, RX, top_y + 40, 2.5, pop(T, t_stuck + 0.3))
    world(ctx, cam, T, 'night', [ex])
    card(ctx, T, t0 + 0.05, [('IDEE 1:', 30, TYPE, P['ink']), ('OBEN FESTBINDEN', 52, SLAB, P['ink'])], 540, 260, -2)
    if T >= t_stuck:
        card(ctx, T, t_stuck, [('SEIL HÄNGT OBEN FEST', 40, SLAB, P['red'])], 540, 1700, 2)


def sc_idea2(ctx, T, t0):
    cam = CAM_FULL
    top_y = ym(119.5) + 30
    t_d = nw('doppelt') - 0.2
    L = (90 if T < t_d else 45) * M

    def ex(c):
        kk = ease(T, t0 + 0.2, t0 + 1.2)
        if T < t_d:
            rope(c, [(RX - 12, top_y), (RX - 12, top_y + L * kk)])
        else:
            k2 = ease(T, t_d, t_d + 0.6)
            Lk = lerp(90, 45, k2) * M
            rope(c, [(RX - 14, top_y + Lk), (RX - 14, top_y), (RX + 14, top_y), (RX + 14, top_y + Lk)])
            if k2 >= 1:
                measure(c, 960, top_y, top_y + 45 * M, '45 M', hexc('#7DE0A0'))
                gap_y0, gap_y1 = top_y + 45 * M, BAL
                k3 = ease(T, nw('fehlen') - 0.4, nw('fehlen') + 0.3)
                if k3 > 0:
                    line(c, RX, gap_y0, RX, lerp(gap_y0, gap_y1, k3), 10, P['red'])
                    if k3 >= 1:
                        fill_rrect(c, RX + 40, (gap_y0 + gap_y1) / 2 - 60, 260, 120, 12, P['red'])
                        text(c, '15 M', RX + 170, (gap_y0 + gap_y1) / 2, 70, C['white'], font=SLAB)
        shelly(c, 540, TOP + 160, 1.0, expr='think', blink=blink(T))
    world(ctx, cam, T, 'night', [ex])
    card(ctx, T, t0 + 0.05, [('IDEE 2:', 30, TYPE, P['ink']), ('DURCH DEN RING', 52, SLAB, P['ink'])], 540, 260, -2)
    if T >= nw('fehlen') - 0.2:
        card(ctx, T, nw('fehlen') - 0.2, [('15 M FEHLEN!', 56, SLAB, P['red'])], 540, 1700, 2)


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


def sc_dawn(ctx, T, t0):
    cam = Cam(560, -700, 1.0)

    def ex(c):
        shelly(c, 760, 60, 1.6, arms={'R': (30, -150 + math.sin(T * 8) * 10), 'L': (-30, -150)}, expr='open', blink=blink(T))
    world(ctx, cam, T, 'dawn', [ex])
    if T < nw('wie') - 0.1:
        card(ctx, T, t0 + 0.05, [('BEI SONNENAUFGANG', 44, SLAB, P['ink']), ('UNTEN AM STRAND', 50, SLAB, hexc('#2F8A4A'))], 540, 380, -2)
    else:
        card(ctx, T, nw('wie') - 0.1, [('WIE HAT SIE', 56, SLAB, P['ink']), ('DAS GESCHAFFT?', 60, SLAB, P['red'])], 540, 380, -2)
    if T >= nw('schreibt') - 0.1:
        card(ctx, T, nw('schreibt') - 0.1, [('IN DIE KOMMENTARE!', 36, SLAB, P['red'])], 540, 600, 2)
    if T >= GAP_AT:
        hourglass(ctx, 860, 900, clamp((T - GAP_AT) / GAP), pop(T, GAP_AT))


def sc_cut(ctx, T, t0):
    room_bg(ctx, T)
    t_cut = TW('schneidet') - 0.1
    if T < t_cut + 0.3:
        rope(ctx, [(120, 1300), (960, 1300)], w=22)
        scissors(ctx, lerp(900, 400, ease(T, t0, t_cut)), 1300, 2.2, 0.2 + 0.3 * abs(math.sin(T * 10)))
    else:
        k = ease(T, t_cut + 0.3, t_cut + 0.8)
        rope(ctx, [(120, 1300), (400 - 30 * k, 1300 + 40 * k)], w=22)
        rope(ctx, [(400 + 30 * k, 1300 - 40 * k), (960, 1300 - 40 * k)], w=22)
        if T >= TW('kurzes') - 0.1:
            fill_rrect(ctx, 150, 1360, 220, 90, 10, P['paper'])
            text(ctx, '30 M', 260, 1405, 56, P['ink'], font=SLAB)
        if T >= TW('langes') - 0.1:
            fill_rrect(ctx, 560, 1300, 260, 90, 10, P['paper'])
            text(ctx, '60 M', 690, 1345, 56, P['red'], font=SLAB)
    shelly(ctx, 840, 1700, 2.2, arms={'R': (34, -100)}, expr='open', blink=blink(T))
    if T < TW('shelly', 0, after=nw('lösung') - 0.5) - 0.1:
        card(ctx, T, t0 + 0.05, [('DIE LÖSUNG', 76, SLAB, P['ink'])], 540, 380, -2)
    else:
        card(ctx, T, TW('schneidet') - 0.2, [('2 STÜCKE', 70, SLAB, P['red'])], 540, 380, -2)


# Lösungsgeometrie
TOPR = ym(119.5) + 30          # Ring oben
LOOP = TOPR + 30 * M           # Schlaufe am Ende des kurzen Stücks
BALR = BAL + 50                # Balkonring


def loop_at(c, y):
    c.new_sub_path()
    c.arc(RX, y + 18, 20, 0, 2 * math.pi)
    c.set_line_width(10)
    src(c, hexc('#3E8C5A'))
    c.stroke()


def sc_setup(ctx, T, t0):
    """Kurzes Stück oben + Schlaufe, langes Stück durch die Schlaufe (doppelt bis zum Balkon)."""
    t_thread = TW('lange') - 0.1
    k_short = ease(T, t0 + 0.2, t0 + 1.2)
    k_long = ease(T, t_thread + 0.3, TW('schuh') + 0.4)
    z = 0.62 if T < t_thread else 0.62
    cam = CAM_FULL

    def ex(c):
        rope(c, [(RX, TOPR), (RX, TOPR + (LOOP - TOPR) * k_short)])
        if k_short >= 1 and T >= TW('schlaufe') - 0.2:
            loop_at(c, LOOP)
            if T < t_thread:
                c.new_sub_path(); c.arc(RX, LOOP + 18, 60, 0, 2 * math.pi); c.set_line_width(8); src(c, C['yellow']); c.stroke()
        if k_long > 0:
            Lh = 30 * M * k_long
            rope(c, [(RX - 16, LOOP + 36 + Lh), (RX - 16, LOOP + 36), (RX + 16, LOOP + 36), (RX + 16, LOOP + 36 + Lh)], col=hexc('#6FBF7A'))
        if T >= TW('beide') - 0.2:
            measure(c, 960, TOPR, LOOP, '30', hexc('#7DE0A0'))
            measure(c, 960, LOOP + 36, BAL, '30', hexc('#B9F0C0'))
        shelly(c, 540, TOP + 160, 1.0, expr='smile', blink=blink(T))
    world(ctx, cam, T, 'night', [ex])
    if T < t_thread:
        card(ctx, T, t0 + 0.05, [('KURZES STÜCK OBEN', 44, SLAB, P['ink']), ('+ SCHLAUFE', 40, SLAB, hexc('#2F8A4A'))], 540, 260, -2)
    else:
        card(ctx, T, t_thread, [('LANGES STÜCK', 44, SLAB, P['ink']), ('DURCH DIE SCHLAUFE', 40, SLAB, hexc('#2F8A4A'))], 540, 260, -2)
    if T >= TW('genau') - 0.2:
        card(ctx, T, TW('genau') - 0.2, [('GENAU BIS ZUM BALKON', 40, SLAB, P['red'])], 540, 1700, 2)


def sc_climb(ctx, T, t0):
    t_loop = TW('dann', 0, after=nw('schlaufe', 2)) - 0.2
    t_bal = TW('balkon', 0, after=nw('doppelten')) + 0.1
    if T < t_loop:
        y = lerp(TOP + 160, LOOP, ease(T, t0 + 0.2, t_loop))
    else:
        y = lerp(LOOP, BAL - 30, ease(T, t_loop, t_bal))
    cam = Cam(620, y - 100, 1.0)

    def ex(c):
        rope(c, [(RX, TOPR), (RX, LOOP)])
        loop_at(c, LOOP)
        rope(c, [(RX - 16, BAL - 10), (RX - 16, LOOP + 36), (RX + 16, LOOP + 36), (RX + 16, BAL - 10)], col=hexc('#6FBF7A'))
        climber(c, T, RX, y - 170, 1.0, True)
    world(ctx, cam, T, 'night', [ex])
    if T < t_loop:
        card(ctx, T, t0 + 0.05, [('KURZES STÜCK', 50, SLAB, P['ink']), ('BIS ZUR SCHLAUFE', 36, TYPE, P['red'])], 540, 300, -2)
    else:
        card(ctx, T, t_loop, [('DOPPELTES STÜCK', 50, SLAB, P['ink']), ('BIS ZUM BALKON', 36, TYPE, P['red'])], 540, 300, -2)


def sc_pull(ctx, T, t0):
    t_pull = TW('zieht') - 0.2
    k = ease(T, t_pull, TW('hände') + 0.2)
    cam = Cam(640, -1700, 0.75)

    def ex(c):
        rope(c, [(RX, TOPR), (RX, LOOP)])
        loop_at(c, LOOP)
        if k < 0.05:
            rope(c, [(RX - 16, BAL - 10), (RX - 16, LOOP + 36), (RX + 16, LOOP + 36), (RX + 16, BAL - 10)], col=hexc('#6FBF7A'))
        elif k < 0.98:
            # das freie Ende rutscht hoch durch die Schlaufe, Shelly zieht das andere herunter
            top_end = LOOP + 36 - 30 * M * (1 - k) * 0 + 30 * M * k
            rope(c, [(RX + 16, min(top_end, BAL - 10)), (RX + 16, BAL - 10)], col=hexc('#6FBF7A'))
            if top_end < BAL - 10:
                rope(c, [(RX - 16, LOOP + 36), (RX - 16, LOOP + 36 + 30 * M * (1 - k))], col=hexc('#6FBF7A'))
        if k > 0.9:
            coil(c, RX + 120, BAL - 6, 1.2)
        shelly(c, RX + 120, BAL + 10, 1.1, arms={'R': (20, -150), 'L': (14, -140)} if k < 0.9 else {'R': (30, -96)}, expr='open', blink=blink(T))
    world(ctx, cam, T, 'night', [ex])
    card(ctx, T, t0 + 0.05, [('EIN ENDE LOSLASSEN,', 40, SLAB, P['ink']), ('AM ANDEREN ZIEHEN', 40, SLAB, hexc('#2F8A4A'))], 540, 300, -2)
    if T >= TW('hände') - 0.2:
        card(ctx, T, TW('hände') - 0.2, [('LANGES STÜCK', 40, SLAB, P['ink']), ('ZURÜCK!', 66, SLAB, hexc('#2F8A4A'))], 540, 1650, 2)


def sc_down(ctx, T, t0):
    t_free = TW('frei') - 0.2
    k = ease(T, TW('klettert', 0, after=nw('bindet', 1)) - 0.1, t_free)
    y = lerp(BAL + 40, -170, k)
    tod = 'night' if T < t_free - 0.3 else 'dawn'
    cam = Cam(620, lerp(-1500, -700, k), lerp(0.75, 1.0, k))

    def ex(c):
        rope(c, [(RX, TOPR), (RX, LOOP)])
        loop_at(c, LOOP)
        rope(c, [(RX + 60, BALR), (RX + 60, BALR + 60 * M)], col=hexc('#6FBF7A'))
        if T < t_free:
            climber(c, T, RX + 60, y, 1.0, True)
        else:
            shelly(c, RX - 120, 60, 1.6, arms={'R': (30, -150 + math.sin(T * 8) * 10), 'L': (-30, -150)}, expr='open', blink=blink(T))
    world(ctx, cam, T, tod, [ex])
    card(ctx, T, t0 + 0.05, [('AM BALKON FESTBINDEN', 40, SLAB, P['ink']), ('60 M RUNTER', 50, SLAB, hexc('#2F8A4A'))], 540, 300, -2)
    if T >= t_free:
        card(ctx, T, t_free, [('FREI!', 110, SLAB, hexc('#2F8A4A'))], 540, 600, 3)


def sc_you(ctx, T, t0):
    cam = Cam(560, -700, 1.0)

    def ex(c):
        shelly(c, 760, 60, 1.6, arms={'R': (46, -112)}, expr='smile', blink=blink(T))
        coil(c, 540, 60, 1.6)
    world(ctx, cam, T, 'dawn', [ex])
    card(ctx, T, t0 + 0.05, [('HÄTTEST DU DAS SEIL', 44, SLAB, P['ink']), ('GETEILT?', 70, SLAB, P['red'])], 540, 380, -2)
    if T >= TW('kommentare', 1) - 0.4:
        card(ctx, T, TW('kommentare', 1) - 0.4, [('IN DIE KOMMENTARE!', 36, SLAB, P['red'])], 540, 600, 2)


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


def sc_outro(ctx, T, t0):
    cam = Cam(560, -700, 1.0)

    def ex(c):
        shelly(c, 760, 60, 1.6, arms={'R': (32, -140 + math.sin(T * 8) * 10)}, expr='open', blink=blink(T))
    world(ctx, cam, T, 'dawn', [ex])
    card(ctx, T, TW('muscheltal') - 0.5, [('WOHNST DU SCHON IN', 34, TYPE, P['ink']), ('MUSCHELTAL?', 80, SLAB, P['ink'])], 540, 380, -2)
    tf = TW('folge') - 0.05
    tap = TW('namen') + 0.3
    if UI_ON[0] and T >= tf:
        k = back_out(T, tf, tf + 0.3, 2.0)
        ctx.save()
        ctx.translate(540, 610)
        ctx.scale(max(k, 0.01), max(k, 0.01))
        on = T >= tap
        fill_rrect(ctx, -170 + 6, -50 + 10, 340, 100, 14, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -170, -50, 340, 100, 14, C['green'] if on else P['red'])
        text(ctx, 'GEFOLGT' if on else 'FOLGEN', -24 if on else 0, 0, 48, C['white'], font=SLAB)
        if on:
            tick_mark(ctx, 120, 0, 34, C['white'])
        ctx.restore()
    hut(ctx, T, TW('hütte') - 0.2, 300, 1500)


SC = [
    ('hook', 0.0, sc_hook),
    ('witch', nw('die', 0) - 0.1, sc_witch),
    ('rings', nw('schau') - 0.1, sc_rings),
    ('rope', nw('shelly', 2) - 0.1, sc_rope),
    ('idea1', nw('erste') - 0.1, sc_idea1),
    ('idea2', nw('zweite') - 0.1, sc_idea2),
    ('dawn', nw('bei') - 0.1, sc_dawn),
    ('cut', TW('hier') - 0.1, sc_cut),
    ('setup', TW('das', 0, after=nw('sechzig', 2)) - 0.1, sc_setup),
    ('climb', TW('sie', 0, after=nw('balkon', 4)) - 0.1, sc_climb),
    ('pull', TW('dort') - 0.1, sc_pull),
    ('down', TW('sie', 0, after=nw('hände')) - 0.1, sc_down),
    ('you', TW('hättest') - 0.1, sc_you),
    ('outro', TW('und', 0, after=nw('kommentare', 1)) - 0.1, sc_outro),
]


def frame(ctx, T):
    cur = SC[0]
    for s_ in SC:
        if T >= s_[1]:
            cur = s_
    cur[2](ctx, T, cur[1])
    for s_ in SC[1:]:
        if 0 <= T - s_[1] < 0.08:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.3 * (1 - (T - s_[1]) / 0.08)))
