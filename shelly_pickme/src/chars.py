"""Figuren: Shelly (klein, Muschel-Haarschmuck), Krabbe Karla, Seepferdchen Paul, Regenschirm."""
import math
import cairo
from draw import *

L1, L2 = 25.0, 23.0          # Oberarm, Unterarm
SH_Y = -97.0                  # Schulterhöhe (Füße bei y=0)


def ik(sx, sy, tx, ty, bend, L1=L1, L2=L2):
    dx, dy = tx - sx, ty - sy
    d = max(1e-3, min(math.hypot(dx, dy), L1 + L2 - 0.5))
    base = math.atan2(dy, dx)
    cosa = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
    a = math.acos(max(-1, min(1, cosa)))
    ang1 = base + a * bend
    ex, ey = sx + math.cos(ang1) * L1, sy + math.sin(ang1) * L1
    ang2 = math.atan2(ty - ey, tx - ex)
    hx, hy = ex + math.cos(ang2) * L2, ey + math.sin(ang2) * L2
    return (ex, ey), (hx, hy)


def umbrella(ctx, hx, hy, ang, state='closed', length=118, k_open=0.0, col=None):
    """Regenschirm: Griff an der Hand (hx, hy), Schaft Richtung ang (rad, 0 = nach rechts)."""
    col = col or hexc('#2F6FDB')
    col2 = mixc(col, C['navy'], 0.35)
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    tx, ty = hx + ux * length, hy + uy * length
    # Griff (J-Haken entgegen der Schaftrichtung)
    ctx.new_path()
    gx, gy = hx - ux * 6, hy - uy * 6
    ctx.move_to(hx + ux * 4, hy + uy * 4)
    ctx.line_to(gx, gy)
    ctx.set_line_width(5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, hexc('#7A4A2A'))
    ctx.stroke()
    ctx.new_sub_path()
    cxh, cyh = gx + px * 7, gy + py * 7
    a0 = math.atan2(gy - cyh, gx - cxh)
    ctx.arc(cxh, cyh, 7, a0, a0 + math.pi)
    ctx.set_line_width(5)
    src(ctx, hexc('#7A4A2A'))
    ctx.stroke()
    # Schaft
    line(ctx, hx, hy, tx, ty, 3.2, hexc('#3A3F4F'))
    if state == 'closed' and k_open < 0.01:
        # gefalteter Schirm: schlanke Tropfenform zwischen 30% und 92%
        a, b = 0.28, 0.93
        mx, my = hx + ux * length * a, hy + uy * length * a
        ex_, ey_ = hx + ux * length * b, hy + uy * length * b
        wid = 9
        ctx.move_to(mx, my)
        ctx.curve_to(mx + px * wid, my + py * wid, ex_ + px * wid * 0.6 - ux * 20, ey_ + py * wid * 0.6 - uy * 20, ex_, ey_)
        ctx.curve_to(ex_ - px * wid * 0.6 - ux * 20, ey_ - py * wid * 0.6 - uy * 20, mx - px * wid, my - py * wid, mx, my)
        src(ctx, col)
        ctx.fill()
        line(ctx, mx + ux * 30 + px * 2, my + uy * 30 + py * 2, ex_ - ux * 14, ey_ - uy * 14, 2, alpha(C['white'], 0.35))
        # Band
        bx, by = hx + ux * length * 0.55, hy + uy * length * 0.55
        line(ctx, bx - px * 8, by - py * 8, bx + px * 8, by + py * 8, 4, C['pink'])
        line(ctx, tx - ux * 6, ty - uy * 6, tx, ty, 3.5, hexc('#3A3F4F'))
        circle(ctx, tx, ty, 2.6, hexc('#3A3F4F'))
    else:
        # aufgespannter Schirm: Kuppel senkrecht zur Schaftachse am oberen Ende
        k = max(k_open, 0.0)
        R = 78 * (0.35 + 0.65 * k)
        top_x, top_y = tx, ty
        base_x, base_y = top_x - ux * R * 0.55 * (0.4 + 0.6 * k), top_y - uy * R * 0.55 * (0.4 + 0.6 * k)
        ctx.save()
        ctx.translate(top_x, top_y)
        ctx.rotate(ang + math.pi / 2)
        # Kuppel nach "oben" (lokal -y)
        ctx.move_to(-R, R * 0.55)
        ctx.curve_to(-R, -R * 0.35, R, -R * 0.35, R, R * 0.55)
        n = 4
        for i in range(n, 0, -1):
            x0 = -R + (2 * R) * i / n
            x1 = -R + (2 * R) * (i - 1) / n
            ctx.curve_to(x0 - (x0 - x1) * 0.25, R * 0.42, x1 + (x0 - x1) * 0.25, R * 0.42, x1, R * 0.55)
        ctx.close_path()
        src(ctx, col)
        ctx.fill()
        for i in range(1, n):
            x0 = -R + 2 * R * i / n
            ctx.move_to(0, -R * 0.08)
            ctx.curve_to(x0 * 0.6, -R * 0.05, x0 * 0.95, R * 0.25, x0, R * 0.55)
            ctx.set_line_width(2.2)
            src(ctx, col2)
            ctx.stroke()
        ctx.move_to(-R * 0.55, R * 0.05)
        ctx.curve_to(-R * 0.45, -R * 0.12, -R * 0.2, -R * 0.2, 0, -R * 0.2)
        ctx.set_line_width(4)
        src(ctx, alpha(C['white'], 0.3))
        ctx.stroke()
        circle(ctx, 0, -R * 0.26, 3.5, hexc('#3A3F4F'))
        ctx.restore()
    return tx, ty


def shelly(ctx, x, y, s=1.0, face=0.0, walk=None, arms=None, expr='smile', blink=0.0, look=(0, 0),
           umb=None, tiptoe=0.0, step=0.0, mirror=False, arm_len=1.0, shell=True, long_hair=False):
    """Shelly zeichnen. (x, y) = Fußpunkt.
    arms: dict mit 'L'/'R' -> Handziel relativ zum Fußpunkt (unskaliert) oder Schlüsselwort.
    umb: dict(state, ang, k_open, hand='R') -> Regenschirm in der Hand."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * (-1 if mirror else 1), s)
    bob = 0.0
    legL = legR = 0.0
    if walk is not None:
        legL = math.sin(walk) * 0.55
        legR = -legL
        bob = -abs(math.cos(walk)) * 3.5
    lift = -tiptoe * 7
    ctx.translate(0, bob + lift)
    fx = face * 7

    # Schatten
    ctx.save()
    ctx.translate(0, -bob - lift)
    ellipse(ctx, 0, 1, 26, 5, alpha(C['shadow'], 0.18))
    ctx.restore()

    if shell:
    # Muschel-Haarschmuck (hinter dem Kopf)
        cx, cy, R = -face * 3, -156, 46
        ctx.new_path()
        nsc = 9
        ctx.move_to(cx + math.cos(math.radians(195)) * R * 0.25, cy + 18)
        for i in range(nsc + 1):
            a = math.radians(195 + 150 * i / nsc)
            ctx.line_to(cx + math.cos(a) * R, cy + 12 + math.sin(a) * R)
            if i < nsc:
                am = math.radians(195 + 150 * (i + 0.5) / nsc)
                ctx.curve_to(cx + math.cos(am) * R * 1.12, cy + 12 + math.sin(am) * R * 1.12,
                             cx + math.cos(am) * R * 1.12, cy + 12 + math.sin(am) * R * 1.12,
                             cx + math.cos(a + math.radians(150 / nsc)) * R, cy + 12 + math.sin(a + math.radians(150 / nsc)) * R)
        ctx.line_to(cx + math.cos(math.radians(345)) * R * 0.25, cy + 18)
        ctx.close_path()
        src(ctx, C['pink3'])
        ctx.fill_preserve()
        ctx.set_line_width(2.5)
        src(ctx, C['pink2'])
        ctx.stroke()
        for i in range(1, nsc):
            a = math.radians(195 + 150 * i / nsc)
            line(ctx, cx, cy + 22, cx + math.cos(a) * R * 0.95, cy + 12 + math.sin(a) * R * 0.95, 2.2, alpha(C['pink2'], 0.8))

    # Haare hinten (Bob / lang)
    if long_hair:
        fill_rrect(ctx, -36 - face * 2, -166, 72, 100, 30, C['hair2'])
    fill_rrect(ctx, -33 - face * 2, -166, 66, 56, 24, C['hair2'])

    # Beine
    for side, lg in ((-1, legL), (1, legR)):
        hx_, hy_ = side * 7, -34
        fx_, fy_ = hx_ + math.sin(lg) * 22, hy_ + math.cos(lg) * 30
        line(ctx, hx_, hy_, fx_, fy_ - 2, 6.5, C['skin2'])
        ellipse(ctx, fx_ + face * 3 + side * 1.5, fy_ - 1.5, 8.5, 5, C['pink2'])
        if tiptoe > 0:
            pass
    # Kleid (A-Linie)
    ctx.new_path()
    ctx.move_to(-15, -96)
    ctx.line_to(15, -96)
    ctx.curve_to(17, -84, 16, -78, 17, -74)
    ctx.curve_to(26, -58, 33, -44, 36, -33)
    ctx.curve_to(20, -27, -20, -27, -36, -33)
    ctx.curve_to(-33, -44, -26, -58, -17, -74)
    ctx.curve_to(-16, -78, -17, -84, -15, -96)
    ctx.close_path()
    src(ctx, C['pink'])
    ctx.fill()
    # Rocksaum-Welle und Gürtel
    ctx.move_to(-36, -33)
    for i in range(6):
        x0 = -36 + 72 * i / 6
        ctx.curve_to(x0 + 3, -29, x0 + 9, -29, x0 + 12, -33)
    ctx.set_line_width(3)
    src(ctx, C['white'])
    ctx.stroke()
    fill_rrect(ctx, -17, -77, 34, 6, 3, C['pink2'])
    circle(ctx, 0, -74, 3.6, C['white'])

    # Arme
    def arm(side, target, layer):
        sx, sy = side * 15.5, SH_Y
        if target is None:
            target = (side * 21, -54)
        if isinstance(target, str):
            target = {'down': (side * 21, -54), 'hip': (side * 27, -72)}[target]
        bend = -side if target[1] > sy - 10 else side
        (ex, ey), (hx, hy) = ik(sx, sy, target[0], target[1], bend, L1 * arm_len, L2 * arm_len)
        line(ctx, sx, sy, ex, ey, 7, C['skin'])
        line(ctx, ex, ey, hx, hy, 6.5, C['skin'])
        circle(ctx, sx, sy + 1, 8.5, C['pink'])
        circle(ctx, hx, hy, 5.2, C['skin'])
        return hx, hy

    arms = arms or {}
    hands = {}
    # Hals
    rect(ctx, -4.5, -108, 9, 14, C['skin2'])
    # Kragen + Perlenkette
    ctx.move_to(-14, -97)
    ctx.curve_to(-8, -88, 8, -88, 14, -97)
    ctx.set_line_width(4)
    src(ctx, C['white'])
    ctx.stroke()
    for i in range(7):
        a = math.radians(200 + i * 20)
        circle(ctx, math.cos(a) * -9 * -1 * 0 + (-9 + i * 3), -94 + 3.2 * math.sin(math.radians(i * 30)), 1.9, C['white'])
    def raised(tg):
        return isinstance(tg, tuple) and tg[1] < SH_Y - 8
    late = []
    for side, key in ((-1, 'L'), (1, 'R')):
        if raised(arms.get(key)):
            late.append((side, key))
        else:
            hands[key] = arm(side, arms.get(key), 0)

    # Kopf
    hx0, hy0 = fx * 0.3, -136
    circle(ctx, hx0, hy0, 28, C['skin'])
    # Ohren
    if abs(face) < 0.6:
        circle(ctx, hx0 - 27, hy0 + 2, 5, C['skin2'])
        circle(ctx, hx0 + 27, hy0 + 2, 5, C['skin2'])
    # Gesicht
    ex0 = hx0 + fx + look[0] * 0.5
    ey0 = hy0 + 2 + look[1] * 0.5
    for side in (-1, 1):
        exx = ex0 + side * 10.5
        if blink > 0.5:
            ctx.move_to(exx - 5, ey0)
            ctx.curve_to(exx - 2, ey0 + 3, exx + 2, ey0 + 3, exx + 5, ey0)
            ctx.set_line_width(2.4)
            src(ctx, C['ink'])
            ctx.stroke()
        else:
            ellipse(ctx, exx, ey0, 4.6, 6.2, C['ink'])
            circle(ctx, exx + 1.6, ey0 - 2.2, 1.7, C['white'])
        # Wimpern
        line(ctx, exx + side * 4, ey0 - 5.5, exx + side * 7, ey0 - 8, 1.6, C['ink'])
    # Augenbrauen
    by = ey0 - 12 - (3 if expr in ('o', 'wow') else 0)
    for side in (-1, 1):
        lift_ = 3 if (expr == 'think' and side == 1) else 0
        inner = 2.5 if expr == 'strain' else -0.5
        ctx.move_to(ex0 + side * 5.5, by + 1 - inner - lift_)
        ctx.curve_to(ex0 + side * 9, by - 2.5 - lift_, ex0 + side * 12, by - 2.5 - lift_, ex0 + side * 15, by + 0.5 - lift_)
        ctx.set_line_width(2.4)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, C['hair2'])
        ctx.stroke()
    # Wangen
    ellipse(ctx, ex0 - 15, ey0 + 9, 5.5, 3.2, alpha(hexc('#F27B95'), 0.55))
    ellipse(ctx, ex0 + 15, ey0 + 9, 5.5, 3.2, alpha(hexc('#F27B95'), 0.55))
    # Mund
    mx, my = ex0, ey0 + 13
    if expr == 'smile':
        ctx.move_to(mx - 6, my - 1)
        ctx.curve_to(mx - 3, my + 4, mx + 3, my + 4, mx + 6, my - 1)
        ctx.set_line_width(2.4)
        src(ctx, hexc('#B2405E'))
        ctx.stroke()
    elif expr in ('open', 'wow'):
        ctx.move_to(mx - 7, my - 2)
        ctx.curve_to(mx - 5, my + 8, mx + 5, my + 8, mx + 7, my - 2)
        ctx.close_path()
        src(ctx, hexc('#B2405E'))
        ctx.fill()
    elif expr == 'o':
        ellipse(ctx, mx, my + 1, 3.6, 4.6, hexc('#B2405E'))
    elif expr == 'think':
        line(ctx, mx - 3, my + 1, mx + 5, my - 1, 2.4, hexc('#B2405E'))
    elif expr == 'strain':
        ctx.move_to(mx - 6, my + 2)
        ctx.curve_to(mx - 2, my - 1, mx + 2, my - 1, mx + 6, my + 2)
        ctx.set_line_width(2.4)
        src(ctx, hexc('#B2405E'))
        ctx.stroke()
    # Pony / Haare vorne
    ctx.new_path()
    ctx.arc(hx0, hy0, 29.5, math.radians(185), math.radians(355))
    ctx.curve_to(hx0 + 22, hy0 - 16, hx0 + 8 + fx, hy0 - 20, hx0 - 2 + fx, hy0 - 13)
    ctx.curve_to(hx0 - 10 + fx, hy0 - 19, hx0 - 22, hy0 - 15, hx0 - 29, hy0 - 3)
    ctx.close_path()
    src(ctx, C['hair'])
    ctx.fill()
    # Seitensträhnen
    for side in (-1, 1):
        ctx.move_to(hx0 + side * 29.5, hy0 - 4)
        ctx.curve_to(hx0 + side * 33, hy0 + 10, hx0 + side * 31, hy0 + 22, hx0 + side * 26, hy0 + 26)
        ctx.curve_to(hx0 + side * 24, hy0 + 14, hx0 + side * 26, hy0 + 4, hx0 + side * 24, hy0 - 4)
        ctx.close_path()
        src(ctx, C['hair'])
        ctx.fill()
    # Perle im Haar
    if shell:
        circle(ctx, hx0 + 18, hy0 - 22, 4.2, C['white'])
        circle(ctx, hx0 + 19.2, hy0 - 23.3, 1.4, alpha(C['pink3'], 0.9))

    for side, key in late:
        hands[key] = arm(side, arms.get(key), 0)
    # Regenschirm
    tip = None
    if umb:
        hh = hands[umb.get('hand', 'R')]
        tip = umbrella(ctx, hh[0], hh[1], umb['ang'], umb.get('state', 'closed'), umb.get('len', 118),
                       umb.get('k_open', 0.0))
        circle(ctx, hh[0], hh[1], 5.4, C['skin'])
    ctx.restore()
    # Weltkoordinaten der Hände / Schirmspitze
    m = -1 if mirror else 1
    out = {k: (x + v[0] * s * m, y + (v[1] + bob + lift) * s) for k, v in hands.items()}
    if tip:
        out['tip'] = (x + tip[0] * s * m, y + (tip[1] + bob + lift) * s)
    return out


def hand_target_world(x, y, s, wx, wy, mirror=False):
    m = -1 if mirror else 1
    return ((wx - x) / s * m, (wy - y) / s)


# ---------------------------------------------------------------- Nachbarn
def karla(ctx, x, y, s=1.0, t=0.0, wonder=0.0):
    """Krabbe Karla: rot, Stielaugen, große Scheren, Brille + Perlenkette."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 1, 52, 7, alpha(C['shadow'], 0.18))
    red, red2 = hexc('#E8553E'), hexc('#C43E2C')
    # Beine
    for side in (-1, 1):
        for i in range(3):
            bx = side * (22 + i * 9)
            k = math.sin(t * 6 + i) * 2
            ctx.move_to(bx, -30)
            ctx.line_to(bx + side * 16, -22 + k)
            ctx.line_to(bx + side * 20, 0)
            ctx.set_line_width(5)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            src(ctx, red2)
            ctx.stroke()
    # Körper
    ellipse(ctx, 0, -42, 46, 28, red)
    ellipse(ctx, -6, -50, 30, 12, alpha(C['white'], 0.18))
    # Scheren
    wave = math.sin(t * 3) * 0.15
    for side in (-1, 1):
        ax, ay = side * 40, -52
        ex, ey = side * 58, -82 - (10 * wonder if side == 1 else 0)
        line(ctx, ax, ay, ex, ey, 8, red2)
        ctx.save()
        ctx.translate(ex, ey - 10)
        ctx.rotate(side * (0.3 + wave))
        ellipse(ctx, 0, 0, 15, 19, red)
        poly(ctx, [(-4, -22), (5, -22), (0, -4)], C['white'] if False else hexc('#F7E7D8'))
        ctx.restore()
    # Stielaugen
    for side in (-1, 1):
        sx = side * 13
        line(ctx, sx, -64, sx + side * 3, -88, 5, red2)
        circle(ctx, sx + side * 3, -94, 10, C['white'])
        circle(ctx, sx + side * 3 + 1, -93 + (-2 if wonder else 0), 5, C['ink'])
        circle(ctx, sx + side * 3 + 2.5, -95, 1.6, C['white'])
    # Brille-Andeutung: kleine Schleife
    poly(ctx, [(-10, -72), (0, -67), (-10, -62)], C['pink'])
    poly(ctx, [(10, -72), (0, -67), (10, -62)], C['pink'])
    circle(ctx, 0, -67, 3.4, C['pink2'])
    # Mund
    if wonder > 0.5:
        ellipse(ctx, 0, -36, 4.5, 5.5, hexc('#6E1E14'))
    else:
        ctx.move_to(-7, -38)
        ctx.curve_to(-3, -33, 3, -33, 7, -38)
        ctx.set_line_width(2.6)
        src(ctx, hexc('#6E1E14'))
        ctx.stroke()
    # Perlenkette
    for i in range(7):
        circle(ctx, -15 + i * 5, -28 + abs(i - 3) * -1.2 + 2, 2.4, C['white'])
    ctx.restore()


def paul(ctx, x, y, s=1.0, t=0.0, wonder=0.0):
    """Seepferdchen Paul: gelb-orange, Ringelschwanz, Fliege, Rückenflosse."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    sway = math.sin(t * 2.2) * 2.5
    ctx.translate(0, sway - 6)
    ellipse(ctx, 0, 7 - sway, 30, 5, alpha(C['shadow'], 0.15))
    body, body2 = hexc('#FFB547'), hexc('#F08A24')
    # Schwanz (Spirale)
    ctx.new_path()
    ctx.move_to(4, -40)
    ctx.curve_to(16, -18, 16, -4, 2, -2)
    ctx.curve_to(-12, 0, -12, -16, -2, -16)
    ctx.curve_to(6, -16, 6, -8, 0, -8)
    ctx.set_line_width(9)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, body2)
    ctx.stroke()
    # Körper
    ctx.new_path()
    ctx.move_to(-6, -118)
    ctx.curve_to(-26, -100, -24, -70, -12, -52)
    ctx.curve_to(-6, -40, 2, -34, 8, -42)
    ctx.curve_to(18, -60, 16, -90, 8, -112)
    ctx.close_path()
    src(ctx, body)
    ctx.fill()
    # Bauchrillen
    for i in range(5):
        yy = -98 + i * 11
        ctx.move_to(-19 + i * 1.5, yy)
        ctx.curve_to(-12, yy + 3, -6, yy + 3, -2, yy + 1)
        ctx.set_line_width(2.2)
        src(ctx, alpha(body2, 0.8))
        ctx.stroke()
    # Rückenflosse
    ctx.move_to(12, -95)
    ctx.curve_to(28, -92 + sway, 28, -70 + sway, 14, -66)
    ctx.close_path()
    src(ctx, hexc('#FFD37E'))
    ctx.fill()
    # Kopf + Schnauze
    ellipse(ctx, -2, -124, 18, 16, body)
    ctx.move_to(-14, -128)
    ctx.line_to(-40, -123)
    ctx.curve_to(-44, -122, -44, -116, -40, -115)
    ctx.line_to(-14, -114)
    ctx.close_path()
    src(ctx, body)
    ctx.fill()
    # Krönchen
    poly(ctx, [(-6, -138), (-2, -150), (2, -140), (6, -151), (9, -137)], body2)
    # Auge
    circle(ctx, -4, -127, 7.5, C['white'])
    circle(ctx, -5, -127 - (1.5 if wonder else 0), 4, C['ink'])
    circle(ctx, -3.6, -128.6, 1.3, C['white'])
    # Fliege
    poly(ctx, [(-10, -110), (-2, -106), (-10, -101)], hexc('#3C6FD8'))
    poly(ctx, [(6, -110), (-2, -106), (6, -101)], hexc('#3C6FD8'))
    circle(ctx, -2, -106, 2.6, hexc('#2A50A8'))
    ctx.restore()


NEIGHBOR_LOOK = {
    'sophia': dict(hair='#2E2A33', hair2='#1E1B22', pink='#4FA3E8', pink2='#2F7FC4', skin='#E8B58F', skin2='#D49A72'),
    'laura': dict(hair='#E7B65A', hair2='#C9953A', pink='#7BC67E', pink2='#4FA65A', skin='#F7D2B5', skin2='#E8B595'),
}


def person(ctx, who, x, y, s=1.45, wonder=0.0, t=0.0, **kw):
    """Nachbarin (normal groß, ohne Muschel). Farben werden kurzfristig getauscht."""
    look = NEIGHBOR_LOOK[who]
    old = {k: C[k] for k in look}
    for k, v in look.items():
        C[k] = hexc(v)
    try:
        arms = {'R': (14, -116)} if wonder > 0.5 else None
        shelly(ctx, x, y, s, shell=False, long_hair=True, expr='o' if wonder > 0.5 else 'smile',
               arms=arms, look=(-5, 0), **kw)
    finally:
        C.update(old)
