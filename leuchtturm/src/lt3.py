"""Shelly im Leuchtturm – Rapunzel-Fassung: Zopf statt Seil, Gewitter, Meerhexe auf dem Mantarochen."""
import json, math, os, random
import cairo
from draw import *
from chars import shelly
import retro
from retro import P, SLAB, TYPE
import lt2
from lt2 import (Cam, cam_path, landscape, tower, braid, loop, ring, measure, glow_ring, big_x, scissors, hourglass, hut,
                 halfw, M, TOPY, ROOM_H, BALY, RINGX, RING_TOP, BAL_RING, LOOPY, WIDE)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = json.load(open(f'{ROOT}/audio/vo_words.json'))
GAP_AT = next(w[2] for w in NEW if w[0].lower().startswith('hörst')) + 0.1
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


def HAIR():
    return C['hair']


# ---------------------------------------------------------------- Drama: Blitze, Wackeln, Regen
FLASHES = [0.05, 12.1, 22.9, 54.3, G(98.2)]


def flash(T):
    f = 0.0
    for t in FLASHES:
        if t <= T < t + 0.9:
            d = T - t
            f = max(f, math.exp(-d * 6) + (0.6 * math.exp(-(d - 0.18) * 9) if d > 0.18 else 0))
    return min(f, 1.0)


def shaken(cam, T):
    f = flash(T)
    if f <= 0.01:
        return cam
    return Cam(cam.x + math.sin(T * 61) * 16 * f / cam.z, cam.y + math.cos(T * 53) * 12 * f / cam.z, cam.z)


def bolt(ctx, x, y0, y1, seed, a):
    r = random.Random(seed)
    pts = [(x, y0)]
    n = 9
    for i in range(1, n + 1):
        pts.append((x + r.uniform(-90, 90), lerp(y0, y1, i / n)))
    for w, c in ((26, alpha(hexc('#B9A8FF'), 0.35 * a)), (9, alpha(C['white'], a))):
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.set_line_width(w)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        src(ctx, c)
        ctx.stroke()


def storm_clouds(ctx, cam, T):
    x0, y0, x1, y1 = cam.bounds()
    for i in range(7):
        cx = -1500 + i * 520 + (T * 14) % 520
        cy = TOPY - 900 + (i % 3) * 140
        if x0 - 500 < cx < x1 + 500 and cy < y1 + 300:
            for dx, dy, r in ((-160, 30, 170), (0, -30, 220), (180, 20, 180), (60, 80, 160)):
                circle(ctx, cx + dx, cy + dy, r, alpha(hexc('#151A3C'), 0.8))
            for dx, dy, r in ((-100, -10, 120), (90, -60, 120)):
                circle(ctx, cx + dx, cy + dy, r, alpha(hexc('#2A3166'), 0.6))


def rain(ctx, T, a=1.0):
    if a <= 0 or not UI_ON[0]:
        return
    r = random.Random(3)
    ctx.set_line_width(3)
    for i in range(140):
        sp = r.uniform(1500, 2200)
        x = (r.uniform(0, W + 300) - (T * sp * 0.3)) % (W + 300) - 100
        y = (r.uniform(0, H) + T * sp) % (H + 200) - 100
        ctx.move_to(x, y)
        ctx.line_to(x - 14, y + 46)
        src(ctx, alpha(hexc('#C9D4FF'), 0.22 * a))
        ctx.stroke()


def world(ctx, cam, T, tod='night', fg=(), bricks=0.0, storm=1.0, bg_fg=()):
    cam = shaken(cam, T)
    f = flash(T)
    ctx.save()
    cam.apply(ctx)
    landscape(ctx, cam, T, tod)
    if tod == 'night' and storm > 0:
        storm_clouds(ctx, cam, T)
        if f > 0.25:
            bolt(ctx, -520 + (int(T) % 3) * 300, TOPY - 900, -320, int(T * 3), f)
    for b in bg_fg:
        b(ctx)
    tower(ctx, T, tod, bricks)
    for g in fg:
        g(ctx)
    ctx.restore()
    if tod == 'night':
        rain(ctx, T, storm)
    if f > 0.01:
        rect(ctx, 0, 0, W, H, alpha(hexc('#E8E4FF'), 0.55 * f))


# ---------------------------------------------------------------- Zopf
def hair_braid(ctx, pts, w=14):
    braid(ctx, pts, col=HAIR(), w=w)


def hair_coil(ctx, x, y, s=1.0, k=1.0):
    if k <= 0.02:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    n = max(1, int(round(5 * k)))
    for i in range(n):
        ellipse(ctx, 0, -i * 10, 58 - i * 6, 16, HAIR())
        ellipse(ctx, 0, -i * 10 - 2, 48 - i * 6, 10, C['hair2'])
        for j in range(7):
            a = j / 7 * math.pi * 2
            line(ctx, math.cos(a) * (53 - i * 6), -i * 10 + math.sin(a) * 13, math.cos(a + 0.3) * (53 - i * 6),
                 -i * 10 + math.sin(a + 0.3) * 13 - 3, 3, alpha(C['hair2'], 0.9))
    ctx.restore()


def head_back(x, y, s):
    return (x - 28 * s, y - 128 * s)


def shelly_braided(c, T, x, y, s, expr='smile', arms=None, face=0.4, to=None, look=(0, 0)):
    """Shelly mit Zopf, der vom Hinterkopf über den Boden zu 'to' (Liste Punkte) läuft."""
    hx, hy = head_back(x, y, s)
    pts = [(hx, hy), (x - 46 * s, y - 70 * s), (x - 58 * s, y - 8)]
    if to:
        pts += to
    hair_braid(c, pts, w=13 * s / 0.95)
    shelly(c, x, y, s, expr=expr, blink=blink(T), arms=arms, face=face, look=look)


# ---------------------------------------------------------------- Meerhexe auf dem Mantarochen
def witch(ctx, x, y, s, T, face=1, angry=False, trail=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * face, s)
    fl = math.sin(T * 5.5)
    # Glitzerspur
    if trail:
        r = random.Random(1)
        for i in range(16):
            ph = (T * 1.6 + i / 16) % 1.0
            px = -150 - ph * 520 + r.uniform(-20, 20)
            py = math.sin(i * 1.7 + T * 2) * 30 + ph * 40 + r.uniform(-25, 25)
            a = (1 - ph) * 0.9
            sz = (1 - ph) * r.uniform(6, 12)
            ctx.save()
            ctx.translate(px, py)
            ctx.rotate(T * 3 + i)
            poly(ctx, [(0, -sz * 2), (sz * 0.5, -sz * 0.5), (sz * 2, 0), (sz * 0.5, sz * 0.5), (0, sz * 2), (-sz * 0.5, sz * 0.5),
                       (-sz * 2, 0), (-sz * 0.5, -sz * 0.5)], alpha(hexc('#B6FFCF') if i % 2 else hexc('#E3B6FF'), a))
            ctx.restore()
    # Aura
    g = cairo.RadialGradient(0, -40, 10, 0, -40, 260)
    g.add_color_stop_rgba(0, 0.6, 0.3, 0.9, 0.35)
    g.add_color_stop_rgba(1, 0.6, 0.3, 0.9, 0)
    ctx.arc(0, -40, 260, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    # Schwanz
    ctx.move_to(-80, 4)
    for i in range(1, 13):
        ctx.line_to(-80 - i * 22, 4 + math.sin(T * 7 - i * 0.6) * (4 + i * 1.6))
    ctx.set_line_width(5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, hexc('#2A3566'))
    ctx.stroke()
    manta_dark, manta, belly = hexc('#26305E'), hexc('#3C4C8C'), hexc('#D9E2F5')
    tt = -105 - 65 * fl          # obere Flügelspitze
    tb = 85 + 65 * fl           # untere Flügelspitze
    tx = -40 + 12 * abs(fl)

    def outline():
        ctx.move_to(128, 0)
        ctx.curve_to(90, -30, 40, tt * 0.7, tx, tt)
        ctx.curve_to(tx - 10, tt * 0.55, -60, -20, -96, -2)
        ctx.curve_to(-60, 22, tx - 10, tb * 0.55, tx, tb)
        ctx.curve_to(40, tb * 0.7, 90, 30, 128, 0)
        ctx.close_path()
    # Schatten-/Unterseite (heller Bauch blitzt beim Flügelschlag auf)
    outline()
    src(ctx, manta)
    ctx.fill()
    ctx.move_to(110, 6)
    ctx.curve_to(70, 30, 30, tb * 0.7, tx, tb)
    ctx.curve_to(tx - 6, tb * 0.6, -40, 30, -80, 6)
    ctx.close_path()
    src(ctx, alpha(belly, 0.18 + 0.18 * max(0, -fl)))
    ctx.fill()
    ctx.move_to(110, -6)
    ctx.curve_to(70, -30, 30, tt * 0.7, tx, tt)
    ctx.curve_to(tx - 6, tt * 0.6, -40, -26, -80, -6)
    ctx.close_path()
    src(ctx, manta_dark)
    ctx.fill()
    outline()
    ctx.set_line_width(3)
    src(ctx, hexc('#1C244A'))
    ctx.stroke()
    # Rückenlinie + Flecken
    ellipse(ctx, 20, 0, 90, 10, alpha(C['white'], 0.12))
    for sx, sy in ((10, 0.45), (-14, 0.6), (30, 0.3)):
        circle(ctx, sx, tb * sy, 6, alpha(C['white'], 0.3))
        circle(ctx, sx, tt * sy, 5, alpha(C['white'], 0.15))
    # Kopfflossen + Auge
    for sy in (-1, 1):
        ctx.move_to(118, sy * 6)
        ctx.curve_to(150, sy * 10, 162, sy * 28, 142, sy * 34)
        ctx.curve_to(136, sy * 22, 126, sy * 16, 112, sy * 14)
        src(ctx, manta_dark)
        ctx.fill()
    circle(ctx, 104, -10, 6, C['white'])
    circle(ctx, 106, -10, 3, C['ink'])
    # Hexe (sitzt oben auf dem Rochen)
    ctx.save()
    ctx.translate(0, -6)
    witch_rider(ctx, T, angry)
    ctx.restore()
    ctx.restore()


def witch_rider(ctx, T, angry):
    w = math.sin(T * 6)
    # Umhang (flattert nach hinten)
    pts = [(-8, -86)]
    for i in range(7):
        pts.append((-30 - i * 26, -80 + i * 9 + math.sin(T * 9 - i * 0.8) * (5 + i * 2.5)))
    pts += [(-200, -6 + math.sin(T * 9 - 6) * 18), (-20, -18)]
    poly(ctx, pts, hexc('#3B1F5E'))
    poly(ctx, [(-12, -60)] + [(p[0] * 0.8, p[1] * 0.8 + 10) for p in pts[3:-1]] + [(-20, -20)], alpha(hexc('#7A2E8E'), 0.8))
    # Haare (Seetang)
    for i in range(6):
        ctx.move_to(-10, -118 + i * 5)
        x0, y0 = -10, -118 + i * 5
        for j in range(1, 7):
            ctx.line_to(x0 - j * 22, y0 + j * 4 + math.sin(T * 8 - j * 0.9 + i) * (2 + j * 1.8))
        ctx.set_line_width(7 - i * 0.6)
        src(ctx, hexc('#2F7A4A') if i % 2 else hexc('#3FA060'))
        ctx.stroke()
    # Körper
    poly(ctx, [(-26, -20), (26, -20), (14, -88), (-14, -88)], hexc('#2E1A47'))
    # Arm mit Zauberstab
    arm = -64 + w * 6 if not angry else -110 + math.sin(T * 20) * 8
    line(ctx, 6, -74, 46, arm, 9, hexc('#2E1A47'))
    circle(ctx, 48, arm, 8, hexc('#9BD6A0'))
    if not angry:
        line(ctx, 48, arm, 96, arm - 30, 5, hexc('#6E4630'))
        gl = 0.6 + 0.4 * math.sin(T * 10)
        circle(ctx, 98, arm - 32, 20 * gl, alpha(hexc('#B6FFCF'), 0.5))
        circle(ctx, 98, arm - 32, 7, hexc('#E8FFF0'))
    # Kopf
    circle(ctx, 0, -110, 26, hexc('#9BD6A0'))
    poly(ctx, [(18, -114), (46, -100), (20, -100)], hexc('#86C48C'))
    circle(ctx, 30, -100, 3, hexc('#5A8A5E'))
    eye = hexc('#FFE14A') if not angry else hexc('#FF4A4A')
    ellipse(ctx, 10, -118, 7, 5, eye)
    circle(ctx, 12, -118, 2.6, C['ink'])
    line(ctx, 0, -130, 20, -124 if not angry else -120, 4, hexc('#1E3A24'))
    ctx.move_to(2, -96)
    ctx.curve_to(10, -88 if not angry else -98, 18, -88 if not angry else -98, 24, -94)
    ctx.set_line_width(3.5)
    src(ctx, hexc('#4A1A2A'))
    ctx.stroke()
    if not angry:
        poly(ctx, [(10, -93), (14, -93), (12, -88)], C['white'])
    # Hut mit wippender Spitze
    ellipse(ctx, 0, -132, 54, 10, hexc('#2E1A47'))
    tip = (-46 + w * 10, -226 + w * 6)
    ctx.move_to(-30, -134)
    ctx.curve_to(-26, -180, -10, -196, tip[0], tip[1])
    ctx.curve_to(-6, -200, 22, -170, 30, -134)
    ctx.close_path()
    src(ctx, hexc('#2E1A47'))
    ctx.fill()
    rect(ctx, -30, -146, 60, 10, hexc('#7A2E8E'))
    rect(ctx, -6, -148, 12, 14, P['gold'])


# ---------------------------------------------------------------- Bausteine
def room_cam(z=2.6, x=-10, y=None):
    return Cam(x, TOPY - 150 if y is None else y, z)


WIN_OUT = [(150, TOPY - 64), (208, TOPY - 64), (216, TOPY + 30)]


def red_vignette(ctx, a):
    if a <= 0:
        return
    g = cairo.RadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1100)
    g.add_color_stop_rgba(0, 0.8, 0.1, 0.1, 0)
    g.add_color_stop_rgba(1, 0.8, 0.1, 0.1, 0.55 * a)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()


# ---------------------------------------------------------------- Szenen
def sc_hook(ctx, T):
    cam = cam_path(T, [(0.0, 70, TOPY - 150, 2.4), (2.6, 70, TOPY - 150, 2.4), (3.6, 80, TOPY + 260, 1.0), (5.0, *WIDE)])
    k = ease(T, 5.4, 7.0)

    def fg(c):
        to = [(70, TOPY - 30), (120, TOPY - 40)] + WIN_OUT[:2]
        if k > 0:
            hair_braid(c, [(208, TOPY - 64), (216, TOPY + 30), (216, TOPY + 30 + (90 * M - 60) * k)], 22)
        hair_coil(c, 100, TOPY - 26, 0.9, 1 - k)
        shelly_braided(c, T, 30, TOPY - 26, 0.95, 'o' if T < 3 else 'smile', {'R': (40, -150)} if T < 3 else None, 0.6, to)
        measure(c, -420, 0, TOPY, '120 M', k=ease(T, 3.3, 4.3))
        if k >= 1:
            measure(c, 470, TOPY, TOPY + 90 * M, '90 M', HAIR(), fs=72)
            c.set_dash([18, 14])
            line(c, 216, TOPY + 90 * M, 216, lerp(TOPY + 90 * M, -20, ease(T, 7.0, 7.6)), 8, P['red'])
            c.set_dash([])
    world(ctx, cam, T, 'night', [fg])
    if T < 3.3:
        card(ctx, T, 0.15, [('GEFANGEN!', 96, SLAB, P['red'])], 540, 330, -3)
    else:
        card(ctx, T, 3.3, [('120 M HOCH', 64, SLAB, P['ink'])], 540, 300, -2)
    if 5.4 <= T < 8.8:
        card(ctx, T, 5.4, [('ZOPF: 90 M', 60, SLAB, hexc('#8A5A2E'))], 540, 480, 2)
    if T >= 7.3:
        card(ctx, T, 7.3, [('NIEMAND KOMMT', 56, SLAB, P['red'])], 540, 480 if T < 8.8 else 1540, 2)
    if T >= 8.78:
        card(ctx, T, 8.78, [('TROTZDEM', 34, TYPE, P['ink']), ('UNTEN AM STRAND!', 52, SLAB, hexc('#2F8A4A'))], 540, 470, 2)
        kk = back_out(T, 9.5, 9.9, 1.8)
        lt2.inset(ctx, 760, 1180, 200, Cam(-160, -90, 1.6), T, 'dawn',
                  [lambda c: shelly(c, -160, 40, 1.2, arms={'R': (30, -150 + math.sin(T * 8) * 10), 'L': (-30, -150)}, expr='open', blink=blink(T))], k=kk)


def sc_witch(ctx, T):
    t0 = 11.8
    cam = cam_path(T, [(t0, 0, TOPY - 40, 0.9), (13.9, 0, TOPY - 40, 0.9), (14.5, 0, -400, 1.0), (15.4, 0, -400, 1.0),
                       (16.2, 60, TOPY - 60, 0.85), (19.2, 60, TOPY - 60, 0.85), (20.6, 0, TOPY - 60, 0.85)])

    def fg(c):
        expr = 'o' if T < 19.3 else ('think' if T < 20.8 else 'o')
        shelly_braided(c, T, 0, TOPY - 26, 0.95, expr, None, 0.5, [(40, TOPY - 30), (90, TOPY - 30)])
        hair_coil(c, 100, TOPY - 26, 0.9)
        if T < 19.3:
            if T < 14.0:
                # stürzt aus dem Himmel heran
                kk = ease(T, t0, 13.4)
                wx, wy, ws = lerp(-900, -300, kk), lerp(TOPY - 700, TOPY - 230, kk), lerp(1.0, 1.7, kk)
                witch(c, wx + math.sin(T * 2) * 30, wy + math.sin(T * 3) * 20, ws, T, 1)
            else:
                a = (T - 14.0) * 1.1 - math.pi * 0.85
                wx = math.cos(a) * 470
                wy = TOPY - 160 + math.sin(a) * 150
                if math.sin(a) < 0:
                    witch(c, wx, wy, 1.7, T, -1 if math.cos(a) > 0 else 1)
        else:
            kk = ease(T, 19.3, 21.0)
            witch(c, lerp(300, 1500, kk), lerp(TOPY - 200, TOPY - 1100, kk), 1.7 * (1 - 0.6 * kk), T, 1)
        if 14.1 <= T < 15.6:
            glow_ring(c, 0, -110, ease(T, 14.2, 14.6), 130, P['red'])
            big_x(c, 0, -110, 2.0, pop(T, 14.6))

    def bg(c):
        # Hexe hinter dem Turm (Kreisbahn, hintere Hälfte)
        if 14.0 <= T < 19.3:
            a = (T - 14.0) * 1.1 - math.pi * 0.85
            if math.sin(a) >= 0:
                witch(c, math.cos(a) * 470, TOPY - 160 + math.sin(a) * 150, 1.25, T, -1 if math.cos(a) > 0 else 1, trail=False)
    bricks = ease(T, 22.9, 24.1)
    world(ctx, cam, T, 'night', [fg], bricks, bg_fg=[bg])
    if T < 14.0:
        card(ctx, T, 12.1, [('DIE BÖSE', 36, TYPE, P['ink']), ('MEERHEXE', 76, SLAB, hexc('#6A2E8E'))], 540, 300, -2)
    elif T < 15.7:
        card(ctx, T, 14.0, [('KEINE TÜR!', 70, SLAB, P['red'])], 540, 300, 2)
    elif T < 19.3:
        card(ctx, T, 15.7, [('NUR PER', 34, TYPE, P['ink']), ('MANTAROCHEN', 64, SLAB, hexc('#3C4C8C'))], 540, 300, -2)
        kk = back_out(T, 16.2, 16.6, 1.8)
        if kk > 0:
            ctx.save()
            ctx.translate(780, 1420)
            ctx.scale(kk, kk)
            circle(ctx, 6, 10, 230, alpha(C['shadow'], 0.35))
            circle(ctx, 0, 0, 230, C['white'])
            ctx.new_sub_path()
            ctx.arc(0, 0, 220, 0, 2 * math.pi)
            ctx.clip()
            vgrad(ctx, -230, -230, 460, 460, [(0, hexc('#1A2150')), (1, hexc('#4B4A92'))])
            for i in range(14):
                yy = ((T * 400 + i * 90) % 520) - 260
                line(ctx, -230 + (i * 37) % 460, yy, -170 + (i * 37) % 460, yy + 4, 3, alpha(C['white'], 0.3))
            witch(ctx, 30, 70 + math.sin(T * 3) * 10, 0.68, T, 1, trail=True)
            ctx.restore()
    else:
        if T < 20.86:
            card(ctx, T, 19.3, [('HEUTE NACHT:', 32, TYPE, P['ink']), ('HEXE WEG', 64, SLAB, P['ink'])], 540, 300, -2)
        else:
            card(ctx, T, 20.86, [('BEI SONNENAUFGANG:', 30, TYPE, P['ink']), ('FENSTER FÜR', 50, SLAB, P['ink']),
                                 ('IMMER ZU!', 70, SLAB, P['red'])], 540, 330, 2)


def sc_rings(ctx, T):
    cam = cam_path(T, [(24.7, 160, TOPY + 40, 1.7), (27.0, 200, TOPY + 40, 1.7), (28.9, 190, BALY - 40, 1.3), (32.3, 190, BALY - 40, 1.3)])

    def fg(c):
        shelly_braided(c, T, 0, TOPY - 26, 0.95, 'smile', None, 0.5, [(40, TOPY - 30), (90, TOPY - 30)])
        hair_coil(c, 100, TOPY - 26, 0.9)
        glow_ring(c, RINGX, RING_TOP, ease(T, 26.6, 27.0), 34)
        measure(c, 430, RING_TOP, BALY, '60 M', k=ease(T, 28.2, 29.4), fs=60)
        glow_ring(c, BAL_RING[0], BAL_RING[1] + 14, ease(T, 30.1, 30.5), 34)
        glow_ring(c, BAL_RING[0], BAL_RING[1] + 14, ease(T, 31.4, 31.8), 50)
    world(ctx, cam, T, 'night', [fg], storm=0.6)
    card(ctx, T, 24.75, [('SCHAU GENAU HIN', 54, SLAB, P['ink'])], 540, 300, -2)
    if T >= 26.6:
        card(ctx, T, 26.6, [('EISENRING', 52, SLAB, P['ink']), ('UNTER DEM FENSTER', 30, TYPE, P['red'])], 540, 1500, 2)


def sc_hair(ctx, T):
    t0 = 32.2

    def fg(c):
        hair_coil(c, 90, TOPY - 26, 1.25)
        scissors(c, -110, TOPY - 112, 0.6, 0.2 + 0.15 * math.sin(T * 5))
        shelly_braided(c, T, -20, TOPY - 26, 0.95, 'open', {'R': (40, -96)}, 0.5, [(30, TOPY - 30), (60, TOPY - 30)])
        glow_ring(c, 90, TOPY - 60, ease(T, 32.7, 33.1), 80)
        glow_ring(c, -100, TOPY - 116, ease(T, 35.9, 36.3), 46)
    world(ctx, room_cam(2.4), T, 'night', [fg], storm=0.4)
    card(ctx, T, t0 + 0.1, [('ZOPF: 90 M', 60, SLAB, hexc('#8A5A2E')), ('STARK WIE SEETANG', 36, SLAB, hexc('#2F8A4A'))], 540, 300, -2)
    if T >= 35.9:
        card(ctx, T, 35.9, [('+ SCHERE', 58, SLAB, P['red'])], 540, 1560, 3)


def sc_idea1(ctx, T):
    t0 = 36.5
    cam = cam_path(T, [(t0, 140, TOPY + 300, 1.0), (40.0, 140, TOPY + 300, 1.0), (41.0, 140, BALY - 80, 1.0), (43.8, 140, BALY - 80, 1.0),
                       (45.0, 180, -500, 1.25)])
    tie = ease(T, 38.4, 39.3)
    yb = RING_TOP + 90 * M * tie
    k = ease(T, 39.8, 40.8)
    sy = lerp(RING_TOP + 140, BALY - 6, k)

    def fg(c):
        hair_braid(c, [(RINGX, RING_TOP), (RINGX, yb)], 16)
        if T < 39.8:
            shelly(c, 20, TOPY - 26, 0.95, expr='open', blink=blink(T), face=0.5)
        elif k < 1:
            lt2.hang(c, T, RINGX, sy + 100, 0.62, expr='o')
        else:
            shelly(c, 210, BALY, 0.62, expr='o' if T > 44 else 'think', blink=blink(T), face=0.3)
        if T >= 41.3:
            glow_ring(c, RINGX, RING_TOP, ease(T, 41.3, 41.7), 50, P['red'])
            big_x(c, RINGX + 80, RING_TOP + 10, 1.6, pop(T, 41.7))
        measure(c, 470, BALY, 0, '60 M', P['red'], ease(T, 44.2, 45.0), fs=90)
    world(ctx, cam, T, 'night', [fg], storm=0.7)
    card(ctx, T, t0 + 0.05, [('IDEE 1', 30, TYPE, P['ink']), ('ABSCHNEIDEN +', 46, SLAB, P['ink']), ('OBEN FESTBINDEN', 46, SLAB, P['ink'])],
         540, 300, -2)
    if T >= 41.3:
        card(ctx, T, 41.3, [('ZOPF HÄNGT OBEN FEST!', 40, SLAB, P['red'])], 540, 1560, 2)
    red_vignette(ctx, ease(T, 44.2, 44.8) * (0.7 + 0.3 * math.sin(T * 8)))


def sc_idea2(ctx, T):
    t0 = 45.6
    cam = cam_path(T, [(t0, 160, TOPY + 300, 1.0), (50.0, 160, TOPY + 300, 1.0), (51.6, 150, -1500, 0.85)])
    kk = ease(T, 46.9, 48.0)
    kd = ease(T, 50.5, 51.7)
    L = lerp(90, 45, kd) * M

    def fg(c):
        if T < 50.5:
            hair_braid(c, [(RINGX - 12, RING_TOP), (RINGX - 12, RING_TOP + 90 * M * kk)], 16)
        else:
            hair_braid(c, [(RINGX - 12, RING_TOP + L), (RINGX - 12, RING_TOP), (RINGX + 12, RING_TOP), (RINGX + 12, RING_TOP + L)], 16)
            if kd >= 1:
                measure(c, 470, RING_TOP, RING_TOP + 45 * M, '45 M', HAIR(), fs=60)
                k3 = ease(T, 53.6, 54.3)
                if k3 > 0:
                    gy0, gy1 = RING_TOP + 45 * M, BALY
                    c.set_dash([16, 12])
                    line(c, RINGX, gy0, RINGX, lerp(gy0, gy1, k3), 8, P['red'])
                    c.set_dash([])
                    if k3 >= 1:
                        fill_rrect(c, RINGX + 30, (gy0 + gy1) / 2 - 50, 230, 100, 10, P['red'])
                        text(c, '15 M', RINGX + 145, (gy0 + gy1) / 2, 64, C['white'], font=SLAB)
        shelly(c, 20, TOPY - 26, 0.95, expr='think', blink=blink(T), face=0.5)
    world(ctx, cam, T, 'night', [fg], storm=0.7)
    card(ctx, T, t0 + 0.05, [('IDEE 2', 30, TYPE, P['ink']), ('DOPPELT DURCH DEN RING', 44, SLAB, P['ink'])], 540, 300, -2)
    if T >= 54.0:
        card(ctx, T, 54.0, [('15 M FEHLEN!', 64, SLAB, P['red'])], 540, 1580, 2)
    red_vignette(ctx, ease(T, 54.0, 54.5))


def sc_time(ctx, T):
    t0 = 55.3
    cam = cam_path(T, [(t0, 0, TOPY - 40, 1.1), (56.8, 0, TOPY - 40, 0.9)])

    def fg(c):
        shelly(c, 0, TOPY - 26, 0.95, expr='o', blink=blink(T), face=0.5, arms={'R': (30, -150), 'L': (-30, -150)})
        witch(c, 1400 + math.sin(T) * 40, TOPY - 900, 0.25, T, -1, trail=False)
    world(ctx, cam, T, 'night', [fg])
    card(ctx, T, t0 + 0.05, [('DIE ZEIT LÄUFT!', 70, SLAB, P['red'])], 540, 300, -2)
    hourglass(ctx, 860, 1420, ease(T, t0, 57.0), pop(T, t0 + 0.1))
    red_vignette(ctx, 0.5 + 0.5 * math.sin(T * 7))


def sc_dawn(ctx, T):
    cam = cam_path(T, [(56.9, *WIDE), (58.6, -60, -260, 1.6), (70, -60, -260, 1.6)])

    def fg(c):
        shelly(c, -180, 40, 1.15, arms={'R': (30, -150 + math.sin(T * 8) * 10), 'L': (-30, -150)}, expr='open', blink=blink(T))
    world(ctx, cam, T, 'dawn', [fg])
    if T < 61.6:
        card(ctx, T, 57.0, [('BEI SONNENAUFGANG', 44, SLAB, P['ink']), ('UNTEN AM STRAND', 50, SLAB, hexc('#2F8A4A'))], 540, 300, -2)
        if T >= 59.8:
            card(ctx, T, 59.8, [('OHNE KRATZER', 48, SLAB, P['red'])], 540, 500, 2)
    else:
        card(ctx, T, 61.6, [('WIE HAT SIE', 56, SLAB, P['ink']), ('DAS GESCHAFFT?', 60, SLAB, P['red'])], 540, 300, -2)
    if T >= 63.1:
        card(ctx, T, 63.1, [('IN DIE KOMMENTARE!', 36, SLAB, P['red'])], 540, 500, 2)
    if T >= GAP_AT:
        hourglass(ctx, 860, 800, clamp((T - GAP_AT) / GAP), pop(T, GAP_AT))


def sc_cut(ctx, T):
    t0 = G(66.2)
    t_snip = G(67.72)
    t_two = G(68.82)

    def fg(c):
        yy = TOPY - 60
        x = -150
        if T < t_snip + 0.2:
            shelly_braided(c, T, x, TOPY - 26, 0.95, 'open', None, 0.4, [(-80, TOPY - 30), (-40, yy + 30)])
            hair_braid(c, [(-40, yy + 30), (170, yy + 30)], 14)
            hx, hy = head_back(x, TOPY - 26, 0.95)
            scissors(c, hx - 10, hy + 40, 0.7, 0.15 + 0.3 * abs(math.sin(T * 12)))
        elif T < t_two:
            shelly(c, x, TOPY - 26, 0.95, expr='open', blink=blink(T), face=0.4)
            hair_braid(c, [(-120, yy), (170, yy)], 14)
            scissors(c, lerp(170, -60, ease(T, t_snip + 0.3, t_two)), yy, 0.7, 0.15 + 0.3 * abs(math.sin(T * 12)))
        else:
            shelly(c, x, TOPY - 26, 0.95, expr='smile', blink=blink(T), face=0.4, arms={'R': (40, -96)})
            k = ease(T, t_two, t_two + 0.35)
            hair_braid(c, [(-120, yy + 10 * k), (-60, yy + 10 * k)], 14)
            hair_braid(c, [(-40, yy - 10 * k), (170, yy - 10 * k)], 14)
            if T >= G(70.48):
                fill_rrect(c, -150, yy + 26, 90, 40, 8, P['paper'])
                text(c, '30 M', -105, yy + 46, 26, P['ink'], font=SLAB)
            if T >= G(72.18):
                fill_rrect(c, 20, yy - 70, 110, 40, 8, P['paper'])
                text(c, '60 M', 75, yy - 50, 26, P['red'], font=SLAB)
    world(ctx, room_cam(2.6), T, 'night', [fg], storm=0.3)
    if T < t_snip:
        card(ctx, T, t0 + 0.05, [('DIE LÖSUNG', 80, SLAB, P['ink'])], 540, 300, -2)
    else:
        card(ctx, T, t_snip, [('ZOPF AB …', 44, SLAB, P['ink']), ('UND IN 2 TEILE!', 60, SLAB, P['red'])], 540, 300, -2)


def sc_setup(ctx, T):
    t0 = G(73.24)
    cam = cam_path(T, [(t0, 180, TOPY + 220, 1.25), (G(77.8), 190, TOPY + 320, 1.05), (G(82.3), 150, -1450, 0.8)])
    ks = ease(T, G(74.2), G(75.3))
    kl = ease(T, G(78.9), G(81.8))

    def fg(c):
        hair_braid(c, [(RINGX, RING_TOP), (RINGX, RING_TOP + (LOOPY - RING_TOP) * ks)], 16)
        if ks >= 1 and T >= G(76.2):
            loop(c, RINGX, LOOPY)
            glow_ring(c, RINGX, LOOPY + 12, ease(T, G(76.6), G(77.0)) * (1 - ease(T, G(77.8), G(78.2))), 40)
        if kl > 0:
            Lh = 30 * M * kl
            braid(c, [(RINGX - 14, LOOPY + 26 + Lh), (RINGX - 14, LOOPY + 26), (RINGX + 14, LOOPY + 26), (RINGX + 14, LOOPY + 26 + Lh)],
                  col=C['hair2'], w=16)
        if T >= G(82.38):
            measure(c, 470, RING_TOP, LOOPY, '30 M', HAIR(), fs=60)
            measure(c, 470, LOOPY + 26, BALY, '30 M', C['hair2'], fs=60)
        shelly(c, 20, TOPY - 26, 0.95, expr='smile', blink=blink(T), face=0.5)
    world(ctx, cam, T, 'night', [fg], storm=0.5)
    if T < G(77.8):
        card(ctx, T, t0 + 0.05, [('KURZER ZOPF OBEN', 46, SLAB, P['ink']), ('+ SCHLAUFE', 42, SLAB, hexc('#2F8A4A'))], 540, 290, -2)
    else:
        card(ctx, T, G(77.8), [('LANGER ZOPF', 46, SLAB, P['ink']), ('DURCH DIE SCHLAUFE', 40, SLAB, hexc('#2F8A4A'))], 540, 290, -2)
        if G(80.9) <= T < G(82.3):
            k = back_out(T, G(80.9), G(81.25), 1.8)
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
    if T >= G(85.0):
        card(ctx, T, G(85.0), [('GENAU BIS ZUM BALKON', 40, SLAB, P['red'])], 540, 1600, 2)


def rig(c):
    hair_braid(c, [(RINGX, RING_TOP), (RINGX, LOOPY)], 16)
    loop(c, RINGX, LOOPY)


def long_doubled(c):
    braid(c, [(RINGX - 14, BALY - 4), (RINGX - 14, LOOPY + 26), (RINGX + 14, LOOPY + 26), (RINGX + 14, BALY - 4)], col=C['hair2'], w=16)


def sc_climb(ctx, T):
    t0 = G(86.44)
    t_l = G(88.94)
    t_b = G(91.3)
    if T < t_l:
        y = lerp(RING_TOP + 160, LOOPY + 20, ease(T, t0 + 0.2, t_l))
        xr = RINGX
    else:
        y = lerp(LOOPY + 170, BALY, ease(T, t_l, t_b))
        xr = RINGX - 14
    cam = Cam(220, y - 160, 1.25)

    def fg(c):
        rig(c)
        long_doubled(c)
        if T < t_b:
            lt2.hang(c, T, xr, y + 120, 0.75)
        else:
            shelly(c, 220, BALY, 0.75, expr='open', blink=blink(T), face=0.3)
    world(ctx, cam, T, 'night', [fg], storm=0.5)
    if T < t_l:
        card(ctx, T, t0 + 0.05, [('KURZER ZOPF', 50, SLAB, P['ink']), ('BIS ZUR SCHLAUFE', 34, TYPE, P['red'])], 540, 290, -2)
    else:
        card(ctx, T, t_l, [('DOPPELTER ZOPF', 50, SLAB, P['ink']), ('BIS ZUM BALKON', 34, TYPE, P['red'])], 540, 290, -2)
    lt2.inset(ctx, 820, 1540, 190, Cam(150, -1300, 0.36), T, 'night',
              [lambda c: (hair_braid(c, [(RINGX, RING_TOP), (RINGX, LOOPY)], 16), loop(c, RINGX, LOOPY), long_doubled(c),
                          circle(c, xr, y, 30, P['red']))], k=back_out(T, t0 + 0.4, t0 + 0.8, 1.8))


def sc_pull(ctx, T):
    t0 = G(92.08)
    tp = G(93.40)
    k = ease(T, tp, G(97.2))
    cam = cam_path(T, [(t0, 230, BALY - 260, 1.2), (tp, 230, BALY - 260, 1.2), (G(94.8), 240, -1650, 0.8)])

    def fg(c):
        rig(c)
        if k < 0.02:
            long_doubled(c)
        else:
            up = 30 * M * k * 2
            Lfree = 30 * M - up
            if Lfree > 0:
                braid(c, [(RINGX - 14, LOOPY + 26 + Lfree), (RINGX - 14, LOOPY + 26), (RINGX + 14, LOOPY + 26), (RINGX + 14, BALY - 4)],
                      col=C['hair2'], w=16)
            else:
                fall = min(30 * M, -Lfree)
                braid(c, [(RINGX + 14, LOOPY + 26 + fall), (RINGX + 14, BALY - 4)], col=C['hair2'], w=16)
        if k > 0.95:
            hair_coil(c, 250, BALY, 0.7)
        shelly(c, 230, BALY, 0.75, arms={'R': (18, -150)} if k < 0.95 else {'R': (34, -100)}, expr='open', blink=blink(T), face=0.3)
    world(ctx, cam, T, 'night', [fg], storm=0.5)
    card(ctx, T, t0 + 0.05, [('EIN ENDE LOSLASSEN', 44, SLAB, P['ink']), ('AM ANDEREN ZIEHEN', 44, SLAB, hexc('#2F8A4A'))], 540, 290, -2)
    if T >= G(96.5):
        card(ctx, T, G(96.5), [('LANGER ZOPF', 40, SLAB, P['ink']), ('ZURÜCK!', 66, SLAB, hexc('#2F8A4A'))], 540, 1600, 2)


def sc_escape(ctx, T):
    t0 = G(98.04)
    t_tie = G(100.4)
    t_cl = G(102.0)
    tf = G(104.5)
    t_find = G(105.28)
    k = ease(T, t_cl, tf - 0.15)
    y = lerp(BALY + 150, 40, k)
    tod = 'night' if T < tf - 0.4 else 'dawn'
    if T < t_tie:
        cam = cam_path(T, [(t0, 230, BALY - 260, 1.0), (t0 + 0.8, 500, BALY - 500, 0.6)])
    elif T < tf:
        cam = Cam(lerp(220, 60, k), lerp(BALY - 100, -380, k), lerp(1.1, 1.0, k))
    else:
        cam = cam_path(T, [(tf, 0, -600, 0.85), (t_find, 0, -600, 0.85), (t_find + 1.2, 0, -900, 0.62)])
    # Hexe kommt näher
    if T < tf:
        kw = ease(T, t0, tf)
        wx, wy, ws = lerp(1800, 900, kw), lerp(TOPY - 1000, TOPY - 500, kw), lerp(0.4, 0.9, kw)
        angry = False
    else:
        kw = ease(T, tf, t_find + 0.4)
        wx, wy, ws = lerp(900, 330, kw), lerp(TOPY - 500, TOPY - 140, kw), lerp(0.9, 1.3, kw)
        angry = T >= t_find + 0.4

    def bg(c):
        pass

    def fg(c):
        rig(c)
        if T >= t_tie:
            hair_braid(c, [(BAL_RING[0], BAL_RING[1] + 28), (BAL_RING[0], BAL_RING[1] + 28 + 60 * M * ease(T, t_tie, t_tie + 0.8))], 16)
        else:
            hair_coil(c, 250, BALY, 0.7)
        if T < t_cl:
            shelly(c, 230, BALY, 0.75, expr='o', blink=blink(T), face=0.3, arms={'R': (34, -100)})
        elif T < tf:
            lt2.hang(c, T, BAL_RING[0], y, 0.75, expr='o')
        else:
            shelly(c, -260, 40, 1.15, arms={'R': (30, -150 + math.sin(T * 8) * 10), 'L': (-30, -150 - math.sin(T * 8) * 10)},
                   expr='open', blink=blink(T))
    world(ctx, cam, T, tod, [fg], storm=1.0, bg_fg=[bg])
    if T < tf:
        kw = ease(T, t0, tf)
        witch(ctx, lerp(1000, 800, kw), lerp(620, 760, kw) + math.sin(T * 3) * 14, lerp(0.5, 1.0, kw), T, -1)
    elif T >= t_find - 0.3:
        lt2.inset(ctx, 720, 820, 250, Cam(250, TOPY - 170, 0.85), T, 'dawn',
                  [lambda c: witch(c, lerp(800, 400, ease(T, t_find - 0.3, t_find + 0.5)), TOPY - 150 + math.sin(T * 3) * 10, 1.0, T, -1,
                                   angry=T >= t_find + 0.5)], k=back_out(T, t_find - 0.3, t_find + 0.1, 1.8))
    if T < t_tie:
        card(ctx, T, t0 + 0.05, [('AM HORIZONT:', 34, TYPE, P['ink']), ('DIE HEXE!', 80, SLAB, P['red'])], 540, 300, -2)
    elif T < tf:
        card(ctx, T, t_tie, [('AM BALKON FESTBINDEN', 40, SLAB, P['ink']), ('60 M RUNTER', 56, SLAB, hexc('#2F8A4A'))], 540, 290, -2)
        red_vignette(ctx, 0.35 + 0.25 * math.sin(T * 8))
    else:
        card(ctx, T, tf, [('FREI!', 130, SLAB, hexc('#2F8A4A'))], 540, 330, 3)
        if T >= t_find:
            card(ctx, T, t_find, [('LEERER TURM!', 60, SLAB, hexc('#6A2E8E'))], 540, 1180, -2)


def sc_you(ctx, T):
    cam = Cam(-60, -260, 1.6)

    def fg(c):
        hair_coil(c, 60, 40, 1.4)
        shelly(c, -180, 40, 1.15, arms={'R': (46, -112)}, expr='smile', blink=blink(T))
    world(ctx, cam, T, 'dawn', [fg])
    card(ctx, T, G(107.86), [('HÄTTEST DU DEINEN', 42, SLAB, P['ink']), ('ZOPF GETEILT?', 66, SLAB, P['red'])], 540, 300, -2)
    if T >= G(111.08):
        card(ctx, T, G(111.08), [('IN DIE KOMMENTARE!', 36, SLAB, P['red'])], 540, 520, 2)


def sc_outro(ctx, T):
    cam = Cam(-60, -260, 1.6)

    def fg(c):
        shelly(c, -180, 40, 1.15, arms={'R': (32, -140 + math.sin(T * 8) * 10)}, expr='open', blink=blink(T))
    world(ctx, cam, T, 'dawn', [fg])
    card(ctx, T, G(112.9), [('WOHNST DU SCHON IN', 34, TYPE, P['ink']), ('MUSCHELTAL?', 80, SLAB, P['ink'])], 540, 300, -2)
    tf = G(114.98)
    tap = G(117.28) + 0.6
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
    hut(ctx, T, G(116.0), 800, 1350)


SC = [(0.0, sc_hook), (11.8, sc_witch), (24.68, sc_rings), (32.2, sc_hair), (36.5, sc_idea1), (45.6, sc_idea2), (55.3, sc_time),
      (56.9, sc_dawn), (G(66.15), sc_cut), (G(73.2), sc_setup), (G(86.4), sc_climb), (G(92.0), sc_pull), (G(98.0), sc_escape),
      (G(107.8), sc_you), (G(112.1), sc_outro)]


def frame(ctx, T):
    cur = SC[0]
    for s_ in SC:
        if T >= s_[0]:
            cur = s_
    cur[1](ctx, T)
    for s_ in SC[1:]:
        if 0 <= T - s_[0] < 0.08:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.25 * (1 - (T - s_[0]) / 0.08)))
