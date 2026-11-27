"""Hotel Sandkorn – detaillierter Retro-Look (nach Referenz): Flur-Kamerafahrt, Grandhotel-Fassade, Seitenflur-Lösung."""
import json, math, os, random, re
import cairo
from draw import *
from chars import shelly

SLAB = 'Alfa Slab One'
TYPE = 'Special Elite'
ZILLA = 'Zilla Slab'
BL = [1.3, 4.2, 7.9, 11.6, 15.1, 19.4, 23.8, 27.2, 31.7, 35.5, 39.9, 44.1, 48.6, 52.2, 56.9, 60.3, 63.1, 66.4]


def blink(T, off=0.0):
    return 1.0 if any(0 <= T - b - off < 0.12 for b in BL) else 0.0


# ---------------------------------------------------------------- Palette
P = {k: hexc(v) for k, v in dict(
    carpet='#B0262C', carpet2='#8C1C22', gold='#D9A441', gold2='#E9BE5A', teal='#2C7A77', teal2='#256866',
    teal3='#3A8C88', wood='#5A3824', wood2='#6E4630', wood3='#432818', door='#6B4129', door2='#57331F',
    cream='#EADFC3', cream2='#CDBF9E', dark='#17110D', night='#1B2048', night2='#2B3170', city='#2A305F',
    city2='#343B75', win='#F2C35A', stone='#D8C6A2', stone2='#C3AE89', stone3='#B09A74', curtain='#B3242A',
    lit='#F7D27A', paper='#EFE6D2', ink='#2A2320', red='#B8262B', street='#2B2B33', walk='#5A5A66',
    water='#1F2E5C', water2='#2B3F78',
).items()}


# ---------------------------------------------------------------- Figuren (Gäste im Pyjama / Reisende)
SKIN = [hexc('#F2C6A0'), hexc('#E2A97E'), hexc('#C98E66'), hexc('#8D5B3E')]
HAIR = [hexc('#3A2A20'), hexc('#E2B65A'), hexc('#1F1B1B'), hexc('#B5482E'), hexc('#C9C3BC'), hexc('#6E3820')]
PJ = [(hexc('#E8EEF7'), hexc('#7FA7D8')), (hexc('#F6E3EA'), hexc('#D884A2')), (hexc('#EAF4E6'), hexc('#7DBA86')),
      (hexc('#F7EFD9'), hexc('#D9A441')), (hexc('#EDE6F7'), hexc('#9C7FD6'))]
COATS = [hexc('#3F6E9E'), hexc('#B5482E'), hexc('#4F7D5A'), hexc('#8E5C9E'), hexc('#C98B3A'), hexc('#5A5A66')]


def figure(ctx, x, y, s, seed, kind='pajama', walk=None, face=0.0, cap=None, suitcase=False, arm_up=0.0):
    """Detaillierte Figur, Füße bei (x, y). kind: pajama | travel."""
    r = random.Random(seed * 7919)
    skin = SKIN[r.randrange(4)]
    hair = HAIR[r.randrange(len(HAIR))]
    female = r.random() < 0.5
    tall = r.uniform(0.92, 1.08)
    cap = (r.random() < 0.35) if cap is None else cap
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * tall, s * tall)
    ellipse(ctx, 0, 0, 24, 4.5, alpha(C['shadow'], 0.22))
    lg = math.sin(walk) * 0.45 if walk is not None else 0.0
    if kind == 'pajama':
        base, stripe = PJ[r.randrange(len(PJ))]
    else:
        base, stripe = COATS[r.randrange(len(COATS))], None
    # Beine / Hose
    for side, l in ((-1, lg), (1, -lg)):
        hx, hy = side * 7, -46
        fx, fy = hx + math.sin(l) * 16, -4
        line(ctx, hx, hy, fx, fy, 10, mixc(base, C['ink'], 0.08) if kind == 'pajama' else hexc('#3A3F4F'))
        if kind == 'pajama' and stripe:
            line(ctx, hx + 2, hy, fx + 2, fy, 2, alpha(stripe, 0.8))
        ellipse(ctx, fx + 3 * (1 if face >= 0 else -1), -3, 9, 4.5, hexc('#7A4A3A') if kind == 'pajama' else hexc('#2B2B33'))
    # Oberkörper
    ctx.save()
    rrect(ctx, -17, -98, 34, 56, 12)
    ctx.clip()
    rect(ctx, -17, -98, 34, 56, base)
    if kind == 'pajama':
        for i in range(-3, 4):
            line(ctx, i * 8, -100, i * 8, -40, 2.5, alpha(stripe, 0.85))
    else:
        rect(ctx, -17, -98, 34, 6, mixc(base, C['white'], 0.25))
        line(ctx, 0, -92, 0, -44, 2, alpha(C['ink'], 0.25))
    rect(ctx, 6, -98, 11, 56, alpha(C['ink'], 0.1))
    ctx.restore()
    # Kragen / Knöpfe
    poly(ctx, [(-8, -98), (0, -88), (8, -98)], mixc(base, C['white'], 0.5))
    for k_ in range(3):
        circle(ctx, 0, -80 + k_ * 11, 1.6, alpha(C['ink'], 0.4))
    # Arme
    for side in (-1, 1):
        sx, sy = side * 15, -94
        if side == 1 and arm_up > 0:
            tx, ty = side * 22, -150
        else:
            tx, ty = side * 21, -52 + (math.sin(walk + side) * 4 if walk is not None else 0)
        line(ctx, sx, sy, tx, ty, 8, base)
        if kind == 'pajama':
            line(ctx, sx, sy, tx, ty, 1.6, alpha(stripe, 0.7))
        circle(ctx, tx, ty + 2, 4.5, skin)
    # Kopf
    rect(ctx, -4, -106, 8, 10, mixc(skin, C['ink'], 0.12))
    hx0 = face * 3
    if female:
        fill_rrect(ctx, -20 + hx0, -138, 40, 40, 16, mixc(hair, C['ink'], 0.15))
    circle(ctx, hx0, -122, 18, skin)
    circle(ctx, hx0 - 18, -120, 4, mixc(skin, C['ink'], 0.08))
    circle(ctx, hx0 + 18, -120, 4, mixc(skin, C['ink'], 0.08))
    ctx.new_path()
    ctx.arc(hx0, -124, 19, math.radians(185), math.radians(355))
    ctx.curve_to(hx0 + 12, -132, hx0 - 4, -136, hx0 - 18, -126)
    ctx.close_path()
    src(ctx, hair)
    ctx.fill()
    ex = hx0 + face * 4
    for sx in (-6, 6):
        ellipse(ctx, ex + sx, -121, 2.2, 3, C['ink'])
    line(ctx, ex - 1, -117, ex + 1, -114, 1.5, alpha(C['ink'], 0.35))
    ctx.move_to(ex - 4, -111)
    ctx.curve_to(ex - 1, -108, ex + 1, -108, ex + 4, -111)
    ctx.set_line_width(1.6)
    src(ctx, hexc('#8A3B3B'))
    ctx.stroke()
    ellipse(ctx, ex - 10, -114, 3.5, 2, alpha(hexc('#F27B95'), 0.35))
    ellipse(ctx, ex + 10, -114, 3.5, 2, alpha(hexc('#F27B95'), 0.35))
    if kind == 'pajama' and cap:
        poly(ctx, [(hx0 - 19, -130), (hx0 + 19, -130), (hx0 + 28, -150), (hx0 + 4, -146)], stripe)
        circle(ctx, hx0 + 30, -150, 5, C['white'])
    if kind == 'travel' and r.random() < 0.5:
        ellipse(ctx, hx0, -139, 26, 5, mixc(base, C['ink'], 0.3))
        fill_rrect(ctx, hx0 - 14, -156, 28, 18, 6, mixc(base, C['ink'], 0.3))
    if suitcase:
        fill_rrect(ctx, 22, -58, 28, 36, 5, hexc('#8E4A2A'))
        rect(ctx, 22, -44, 28, 4, P['gold'])
        line(ctx, 30, -58, 30, -64, 3, C['ink'])
        line(ctx, 42, -58, 42, -64, 3, C['ink'])
        line(ctx, 30, -64, 42, -64, 3, C['ink'])
    ctx.restore()


def shelly_boss(ctx, T, x, y, s, pose='idle', expr='smile', mirror=False):
    wv = math.sin(T * 8) * 10
    arms = {'idle': None, 'wave': {'R': (32 + wv * 0.2, -140 + wv)}, 'point': {'R': (46, -112)},
            'megaphone': {'R': (20, -118)}, 'cheer': {'R': (30, -150 + wv), 'L': (-30, -150 - wv)},
            'present': {'R': (44, -96), 'L': (-27, -72)}}[pose]
    out = shelly(ctx, x, y, s, arms=arms, expr=expr, blink=blink(T), mirror=mirror)
    if pose == 'megaphone':
        hx, hy = out['R']
        d = -1 if mirror else 1
        poly(ctx, [(hx, hy - 10 * s / 1.3), (hx + d * 64 * s / 1.3, hy - 30 * s / 1.3), (hx + d * 64 * s / 1.3, hy + 26 * s / 1.3),
                   (hx, hy + 8 * s / 1.3)], P['red'])
    return out


# ---------------------------------------------------------------- Karten / Texte (Retro-Papier)
def paper_card(ctx, T, t0, lines, x=540, y=620, rot=-2.0, w_min=0):
    """lines: [(text, size, font, color)]"""
    if not UI_ON[0] or T < t0:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    if k <= 0.001:
        return
    ws = [text_size(ctx, s_, sz, f)[0] for s_, sz, f, _ in lines]
    w = min(880, max(max(ws) + 100, w_min))
    h = sum(sz * 1.22 for _, sz, _, _ in lines) + 70
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(rot + math.sin(T * 1.3) * 0.5))
    ctx.scale(k, k)
    fill_rrect(ctx, -w / 2 + 10, -h / 2 + 16, w, h, 4, alpha(C['shadow'], 0.4))
    g = cairo.LinearGradient(0, -h / 2, 0, h / 2)
    g.add_color_stop_rgba(0, *P['paper'])
    g.add_color_stop_rgba(1, *mixc(P['paper'], P['cream2'], 0.5))
    rrect(ctx, -w / 2, -h / 2, w, h, 4)
    ctx.set_source(g)
    ctx.fill()
    r = random.Random(3)
    for i in range(60):
        circle(ctx, r.uniform(-w / 2, w / 2), r.uniform(-h / 2, h / 2), r.uniform(0.6, 1.8), alpha(P['cream2'], 0.5))
    yy = -h / 2 + 38
    for s_, sz, f, col in lines:
        text(ctx, s_, 0, yy + sz * 0.5, sz, col, font=f)
        yy += sz * 1.22
    ctx.restore()


def calendar(ctx, T, t0, x=540, y=900):
    """'Rätsel des Tages' – Abreißkalender, Tage blättern."""
    if not UI_ON[0] or T < t0:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    day = 1 + min(6, int(max(0, T - t0 - 0.4) / 0.22))
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(-3))
    ctx.scale(k, k)
    fill_rrect(ctx, -150 + 8, -170 + 14, 300, 340, 10, alpha(C['shadow'], 0.4))
    fill_rrect(ctx, -150, -170, 300, 340, 10, C['white'])
    rect(ctx, -150, -170, 300, 64, P['red'])
    for i in range(6):
        circle(ctx, -110 + i * 44, -170, 9, C['ink'])
    text(ctx, 'RÄTSEL DES TAGES', 0, -82, 22, C['ink'], font=TYPE)
    text(ctx, '?', 0, 10, 150, P['red'], font=SLAB)
    text(ctx, f'TAG {day}', 0, 130, 34, C['ink'], font=ZILLA)
    ctx.restore()


# ---------------------------------------------------------------- Szene A: Flur in Zentralperspektive (Kamerafahrt)
F_CX, F_CY, F_F = 540.0, 900.0, 620.0


def proj(X, Y, Z, cz):
    d = max(0.05, Z - cz)
    return F_CX + X * F_F / d, F_CY - Y * F_F / d, F_F / d


def fog(col, d):
    k = clamp((d - 2) / 30.0) ** 0.8
    return mixc(col, P['dark'], k)


def quad(ctx, pts, col):
    poly(ctx, pts, col)


def corridor_3d(ctx, T, cz, numbers, belegt_z=None, guests=()):
    rect(ctx, 0, 0, W, H, P['dark'])
    zmax = cz + 34
    z0 = math.floor(cz)
    seg = 0.5
    zs = []
    z = zmax
    while z > cz + 0.2:
        zs.append(z)
        z -= seg
    for za in zs:
        zb = max(cz + 0.2, za - seg)
        d = (za + zb) / 2 - cz
        # Boden (Holz außen, Teppich innen)
        for (xa, xb, col) in ((-1.0, -0.9, P['wood3']), (0.9, 1.0, P['wood3']), (-0.9, 0.9, P['carpet'])):
            a, b = proj(xa, -1, za, cz), proj(xb, -1, za, cz)
            c, e = proj(xb, -1, zb, cz), proj(xa, -1, zb, cz)
            quad(ctx, [(a[0], a[1]), (b[0], b[1]), (c[0], c[1]), (e[0], e[1])], fog(col, d))
        # Decke
        a, b = proj(-1, 1.3, za, cz), proj(1, 1.3, za, cz)
        c, e = proj(1, 1.3, zb, cz), proj(-1, 1.3, zb, cz)
        quad(ctx, [(a[0], a[1]), (b[0], b[1]), (c[0], c[1]), (e[0], e[1])], fog(P['cream'] if int(za * 2) % 2 else mixc(P['cream'], P['cream2'], 0.3), d))
        # Wände
        for X in (-1.0, 1.0):
            for (ya, yb, col) in ((-1, -0.35, P['wood']), (-0.35, -0.28, P['wood2']), (-0.28, 1.3, P['teal'])):
                a, b = proj(X, ya, za, cz), proj(X, yb, za, cz)
                c, e = proj(X, yb, zb, cz), proj(X, ya, zb, cz)
                quad(ctx, [(a[0], a[1]), (b[0], b[1]), (c[0], c[1]), (e[0], e[1])], fog(col, d))
            # Tapetenstreifen
            for zz in (za, za - 0.25):
                if zz <= cz + 0.2:
                    continue
                a, b = proj(X, -0.28, zz, cz), proj(X, 1.3, zz, cz)
                line(ctx, a[0], a[1], b[0], b[1], max(1, 3 * b[2] / 120), fog(P['teal2'], zz - cz), cap=cairo.LINE_CAP_BUTT)
        # Teppich-Goldlinien
        for X in (-0.78, 0.78):
            a, b = proj(X, -1, za, cz), proj(X, -1, zb, cz)
            line(ctx, a[0], a[1], b[0], b[1], max(1, 0.03 * b[2]), fog(P['gold'], d), cap=cairo.LINE_CAP_BUTT)
    # Rauten auf dem Teppich + Lampen + Türen (von hinten nach vorne)
    items = []
    k0 = int(cz // 2.4) - 1
    for k in range(k0, k0 + 16):
        zc = k * 2.4 + 1.2
        if cz + 0.75 < zc < zmax:
            items.append((zc, 'diamond', k))
    k0 = int(cz // 3.0) - 1
    for k in range(k0, k0 + 13):
        zc = k * 3.0 + 0.5
        if cz + 0.3 < zc < zmax:
            items.append((zc, 'lamp', k))
    for k in range(int(cz // 1.6) - 1, int(cz // 1.6) + 24):
        side = -1 if k % 2 == 0 else 1
        zc = k * 1.6 + (0.0 if side < 0 else 0.8)
        if cz + 0.6 < zc < zmax:
            items.append((zc, 'door', k))
    for g_ in guests:
        items.append(g_)
    if belegt_z and cz + 0.4 < belegt_z < zmax:
        items.append((belegt_z, 'belegt', 0))
    items.sort(key=lambda it: -it[0])
    for it in items:
        zc, kind, k = it[0], it[1], it[2]
        d = zc - cz
        if kind == 'diamond':
            pts = [proj(0, -1, zc - 0.45, cz), proj(0.28, -1, zc, cz), proj(0, -1, zc + 0.45, cz), proj(-0.28, -1, zc, cz)]
            quad(ctx, [(p[0], p[1]) for p in pts], fog(P['gold'], d))
        elif kind == 'lamp':
            a, b = proj(0, 1.3, zc, cz), proj(0, 1.08, zc, cz)
            line(ctx, a[0], a[1], b[0], b[1], max(1, b[2] * 0.012), fog(P['wood3'], d))
            ellipse(ctx, b[0], b[1], 0.2 * b[2], 0.05 * b[2], fog(P['gold'], d))
            g = cairo.RadialGradient(b[0], b[1] + 0.1 * b[2], 1, b[0], b[1] + 0.1 * b[2], 0.9 * b[2])
            g.add_color_stop_rgba(0, 1, 0.92, 0.7, 0.25 * (1 - clamp(d / 30)))
            g.add_color_stop_rgba(1, 1, 0.92, 0.7, 0)
            ctx.arc(b[0], b[1] + 0.1 * b[2], 0.9 * b[2], 0, 2 * math.pi)
            ctx.set_source(g)
            ctx.fill()
        elif kind == 'door':
            side = -1 if k % 2 == 0 else 1
            X = side * 0.999
            za_, zb_ = zc - 0.32, zc + 0.32
            corners = lambda y0, y1, z0_, z1_: [proj(X, y0, z0_, cz), proj(X, y1, z0_, cz), proj(X, y1, z1_, cz), proj(X, y0, z1_, cz)]
            fr = corners(-1, 0.72, za_ - 0.05, zb_ + 0.05)
            quad(ctx, [(p[0], p[1]) for p in fr], fog(P['wood3'], d))
            dr = corners(-1, 0.66, za_, zb_)
            quad(ctx, [(p[0], p[1]) for p in dr], fog(P['door'], d))
            for (y0, y1) in ((-0.85, -0.2), (-0.05, 0.55)):
                pn = corners(y0, y1, za_ + 0.08, zb_ - 0.08)
                quad(ctx, [(p[0], p[1]) for p in pn], fog(P['door2'], d))
            kn = proj(X, -0.2, zb_ - 0.08 if side < 0 else za_ + 0.08, cz)
            circle(ctx, kn[0], kn[1], max(1, 0.03 * kn[2]), fog(P['gold'], d))
            # Nummernschild
            pl = corners(0.82, 1.05, zc - 0.2, zc + 0.2)
            quad(ctx, [(p[0], p[1]) for p in pl], fog(P['gold2'], d))
            c_ = proj(X, 0.935, zc, cz)
            num = numbers(k)
            sz = 0.17 * c_[2]
            if sz > 5:
                tw = text_size(ctx, num, sz, ZILLA)[0]
                maxw = abs(pl[2][0] - pl[0][0]) * 0.9
                if tw > maxw and maxw > 4:
                    sz *= maxw / tw
                text(ctx, num, c_[0], c_[1], sz, fog(P['ink'], d), font=ZILLA)
            # Wandleuchte neben der Tür
            sc = proj(X, 0.25, zb_ + 0.35, cz)
            fill_rrect(ctx, sc[0] - 0.05 * sc[2], sc[1] - 0.1 * sc[2], 0.1 * sc[2], 0.16 * sc[2], 0.02 * sc[2], fog(P['cream'], d))
            g = cairo.RadialGradient(sc[0], sc[1], 1, sc[0], sc[1], 0.5 * sc[2])
            g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.35 * (1 - clamp(d / 25)))
            g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
            ctx.arc(sc[0], sc[1], 0.5 * sc[2], 0, 2 * math.pi)
            ctx.set_source(g)
            ctx.fill()
        elif kind == 'belegt':
            a = proj(0, 0.95, zc, cz)
            w_, h_ = 0.9 * a[2], 0.22 * a[2]
            line(ctx, a[0] - w_ * 0.35, a[1] - h_ / 2, a[0] - w_ * 0.35, proj(0, 1.3, zc, cz)[1], 2, C['ink'])
            line(ctx, a[0] + w_ * 0.35, a[1] - h_ / 2, a[0] + w_ * 0.35, proj(0, 1.3, zc, cz)[1], 2, C['ink'])
            fill_rrect(ctx, a[0] - w_ / 2, a[1] - h_ / 2, w_, h_, 0.03 * a[2], hexc('#3A1A1A'))
            fl = 1.0 if (T * 6) % 4 > 0.3 else 0.5
            for k_, al in ((0.04, 0.2), (0.02, 0.35)):
                rrect(ctx, a[0] - w_ / 2 - k_ * a[2], a[1] - h_ / 2 - k_ * a[2], w_ + 2 * k_ * a[2], h_ + 2 * k_ * a[2], 0.05 * a[2])
                ctx.set_line_width(3)
                src(ctx, alpha(hexc('#FF4D5A'), al * fl))
                ctx.stroke()
            text(ctx, 'BELEGT', a[0], a[1], 0.15 * a[2], mixc(hexc('#6A2028'), hexc('#FF7A86'), fl), font=SLAB)
        elif kind == 'guest':
            side, seed = it[3], it[4]
            X = side * 0.78
            p = proj(X, -1, zc, cz)
            figure(ctx, p[0], p[1], p[2] / 200, seed, 'pajama', face=-side * 0.6)
    # Vignette in die Tiefe
    g = cairo.RadialGradient(F_CX, F_CY, 10, F_CX, F_CY, 140)
    g.add_color_stop_rgba(0, 0.05, 0.03, 0.02, 0.95)
    g.add_color_stop_rgba(1, 0.05, 0.03, 0.02, 0)
    ctx.arc(F_CX, F_CY, 140, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()


def door_numbers(k):
    seq = [3, 5, 8, 12, 21, 34, 57, 99, 100, 250, 999, 4096, 99999, 999999, 99999999, 999999999]
    if k < 0:
        return str(k + 3)
    return f'{seq[min(k, len(seq) - 1)]:,}'.replace(',', ' ')


def sc_corridor(ctx, T):
    t_end = SC[1][1]
    k = clamp(T / t_end)
    cz = 30 * (k ** 1.6) + 4 * k
    guests = [(4.0, 'guest', 0, 1, 3), (8.8, 'guest', 0, -1, 8), (14.2, 'guest', 0, 1, 11), (20.5, 'guest', 0, -1, 4),
              (26.0, 'guest', 0, 1, 21)]
    corridor_3d(ctx, T, cz, door_numbers, belegt_z=11.5, guests=guests)


# ---------------------------------------------------------------- Szene B: Grandhotel-Fassade
HX0, HX1 = 200.0, 880.0   # Hotelbreite
FLOOR_H = 250.0
LOBBY_H = 420.0
GROUND = 0.0             # Fassaden-Welt: y=0 Straßenniveau, negative y = nach oben


def floor_y(f):
    """Unterkante von Etage f (1 = erste Etage über der Lobby)."""
    return GROUND - LOBBY_H - (f - 1) * FLOOR_H


def city_bg(ctx, cam, T, x0, y0, x1, y1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *hexc('#0F1433'))
    g.add_color_stop_rgba(1, *P['night2'])
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()
    r = random.Random(2)
    for i in range(120):
        sx, sy = r.uniform(-2000, 3000), r.uniform(-30000, -800)
        if x0 < sx < x1 and y0 < sy < y1:
            circle(ctx, sx, sy, r.uniform(1.5, 3.2) / cam.z, alpha(C['white'], 0.5 + 0.4 * math.sin(T * 2 + i)))
    # Nachbarhäuser
    r = random.Random(5)
    for side, xs in ((-1, [-700, -420, -120]), (1, [900, 1180, 1460])):
        for j, bx in enumerate(xs):
            bw = r.uniform(260, 320)
            bh = r.uniform(1500, 2600)
            col = P['city'] if j % 2 else P['city2']
            rect(ctx, bx, GROUND - bh, bw, bh, col)
            rect(ctx, bx, GROUND - bh, bw, 18, mixc(col, C['white'], 0.08))
            for wy in range(int(GROUND - bh + 60), int(GROUND - 80), 90):
                for wx in range(int(bx + 25), int(bx + bw - 40), 62):
                    on = r.random() < 0.55
                    rect(ctx, wx, wy, 34, 48, P['win'] if on else mixc(col, C['ink'], 0.25))


def window_unit(ctx, x, y, w, h, n, T, guest_seed=None, lit=True):
    """Fenster mit Rahmen, roten Vorhängen, Licht, Gast-Silhouette, Balkongitter, Nummernschild."""
    fill_rrect(ctx, x - 8, y - 8, w + 16, h + 16, 6, P['stone3'])
    rect(ctx, x, y, w, h, P['lit'] if lit else hexc('#3A3A5A'))
    if lit:
        g = cairo.RadialGradient(x + w / 2, y + h * 0.4, 5, x + w / 2, y + h * 0.4, h)
        g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.6)
        g.add_color_stop_rgba(1, 0.95, 0.7, 0.35, 0.0)
        ctx.rectangle(x, y, w, h)
        ctx.set_source(g)
        ctx.fill()
    if guest_seed is not None and lit:
        ctx.save()
        ctx.rectangle(x, y, w, h)
        ctx.clip()
        figure(ctx, x + w / 2 + ((guest_seed % 3) - 1) * w * 0.12, y + h + 30, h / 150, guest_seed, 'pajama')
        ctx.restore()
    # Vorhänge
    for side in (0, 1):
        cx = x if side == 0 else x + w
        d = 1 if side == 0 else -1
        ctx.move_to(cx, y)
        ctx.curve_to(cx + d * w * 0.32, y + h * 0.3, cx + d * w * 0.18, y + h * 0.7, cx + d * w * 0.28, y + h)
        ctx.line_to(cx, y + h)
        ctx.close_path()
        src(ctx, P['curtain'])
        ctx.fill()
        line(ctx, cx + d * w * 0.1, y + 6, cx + d * w * 0.14, y + h - 6, 2, alpha(C['ink'], 0.2))
    rect(ctx, x - 6, y - 4, w + 12, 10, mixc(P['curtain'], C['ink'], 0.2))
    # Fensterkreuz
    line(ctx, x + w / 2, y, x + w / 2, y + h, 3, alpha(P['stone3'], 0.9))
    # Balkongitter
    rect(ctx, x - 14, y + h + 4, w + 28, 8, C['ink'])
    for i in range(9):
        xx = x - 10 + i * (w + 20) / 8
        line(ctx, xx, y + h + 8, xx, y + h + 34, 2.5, C['ink'])
    rect(ctx, x - 14, y + h + 32, w + 28, 6, C['ink'])
    # Nummernschild
    fill_rrect(ctx, x + w / 2 - 22, y + h + 42, 44, 26, 3, P['gold2'])
    text(ctx, str(n), x + w / 2, y + h + 55, 18 if n < 100 else 14, P['ink'], font=ZILLA)


def hotel_facade(ctx, cam, T, sign='HOTEL SANDKORN', belegt=1.0, all_lit=True, guests_in=True, sign_k=1.0):
    x0, y0, x1, y1 = cam.bounds()
    city_bg(ctx, cam, T, x0, y0, x1, y1)
    # Turm (beliebig hoch)
    top = max(y0 - 200, -200000)
    rect(ctx, HX0 - 20, top, HX1 - HX0 + 40, GROUND - top, P['stone2'])
    rect(ctx, HX0, top, HX1 - HX0, GROUND - top, P['stone'])
    for xx in (HX0 + 10, HX1 - 30):
        rect(ctx, xx, top, 20, GROUND - top - LOBBY_H, P['stone2'])
    f_lo = max(1, int((GROUND - LOBBY_H - y1) / FLOOR_H))
    f_hi = int((GROUND - LOBBY_H - y0) / FLOOR_H) + 2
    if cam.z < 0.12:
        # sehr weit weg: nur Lichterraster
        step = max(1, int(0.05 / cam.z))
        for f in range(f_lo, f_hi, step):
            yy = floor_y(f) - FLOOR_H * 0.6
            for i in range(3):
                rect(ctx, HX0 + 70 + i * 210, yy, 140, FLOOR_H * 0.5 * step, P['lit'])
        return
    for f in range(f_lo, f_hi):
        yb = floor_y(f)
        rect(ctx, HX0 - 6, yb - 10, HX1 - HX0 + 12, 12, P['stone3'])
        for i in range(3):
            n = (f - 1) * 3 + i + 1
            r = random.Random(n * 31)
            gs = n if (guests_in and r.random() < 0.55) else None
            lit = all_lit or r.random() < 0.6
            window_unit(ctx, HX0 + 75 + i * 205, yb - FLOOR_H + 30, 130, 150, n, T, gs, lit)
    # Lobby
    ly = GROUND - LOBBY_H
    rect(ctx, HX0, ly, HX1 - HX0, LOBBY_H, P['stone2'])
    rect(ctx, HX0 - 20, ly - 30, HX1 - HX0 + 40, 36, P['stone3'])
    # Schild
    if sign_k > 0.01:
        ctx.save()
        ctx.translate((HX0 + HX1) / 2, ly + 40)
        ctx.scale(sign_k, sign_k)
        fill_rrect(ctx, -250, -44, 500, 88, 6, hexc('#1E1A16'))
        rrect(ctx, -250, -44, 500, 88, 6)
        ctx.set_line_width(5)
        src(ctx, P['gold'])
        ctx.stroke()
        text(ctx, sign, 0, 0, 46, P['gold2'], font=ZILLA)
        ctx.restore()
    # Schaufenster
    for xx in (HX0 + 30, HX1 - 190):
        rect(ctx, xx, ly + 140, 160, 220, P['lit'])
        g = cairo.LinearGradient(0, ly + 140, 0, ly + 360)
        g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.6)
        g.add_color_stop_rgba(1, 0.9, 0.6, 0.3, 0.2)
        ctx.rectangle(xx, ly + 140, 160, 220)
        ctx.set_source(g)
        ctx.fill()
        circle(ctx, xx + 80, ly + 330, 34, hexc('#4F7D5A'))
        rect(ctx, xx + 66, ly + 330, 28, 30, hexc('#8E4A2A'))
        rect(ctx, xx, ly + 140, 160, 10, P['gold'])
    # Markise
    ax0, ax1, ay = (HX0 + HX1) / 2 - 150, (HX0 + HX1) / 2 + 150, ly + 105
    for i in range(10):
        col = P['red'] if i % 2 == 0 else C['white']
        poly(ctx, [(ax0 + i * 30, ay), (ax0 + (i + 1) * 30, ay), (ax0 + (i + 1) * 30 + 4, ay + 50), (ax0 + i * 30 + 4, ay + 50)], col)
    for i in range(10):
        ctx.new_sub_path()
        ctx.arc(ax0 + i * 30 + 17, ay + 50, 15, 0, math.pi)
        src(ctx, P['red'] if i % 2 == 0 else C['white'])
        ctx.fill()
    # Goldene Tür
    dx0, dx1 = (HX0 + HX1) / 2 - 110, (HX0 + HX1) / 2 + 110
    rect(ctx, dx0 - 12, ly + 160, dx1 - dx0 + 24, LOBBY_H - 160, P['wood3'])
    g = cairo.LinearGradient(dx0, 0, dx1, 0)
    g.add_color_stop_rgba(0, *P['gold']); g.add_color_stop_rgba(0.5, *P['gold2']); g.add_color_stop_rgba(1, *P['gold'])
    ctx.rectangle(dx0, ly + 170, dx1 - dx0, LOBBY_H - 170)
    ctx.set_source(g)
    ctx.fill()
    line(ctx, (dx0 + dx1) / 2, ly + 170, (dx0 + dx1) / 2, GROUND, 4, mixc(P['gold'], C['ink'], 0.3))
    for xx in (dx0 + 20, (dx0 + dx1) / 2 + 20):
        rect(ctx, xx, ly + 200, 70, 150, alpha(C['white'], 0.25))
    # BELEGT-Neon
    if belegt > 0:
        bx, by = HX1 - 110, ly + 95
        fl = belegt * (1.0 if (T * 6) % 4 > 0.3 else 0.5)
        fill_rrect(ctx, bx - 70, by - 22, 140, 44, 6, hexc('#2A0E12'))
        rrect(ctx, bx - 76, by - 28, 152, 56, 10)
        ctx.set_line_width(4)
        src(ctx, alpha(hexc('#FF4D5A'), 0.35 * fl))
        ctx.stroke()
        text(ctx, 'BELEGT', bx, by, 28, mixc(hexc('#5A2028'), hexc('#FF7A86'), fl), font=SLAB)
    # Roter Teppich, Gehweg, Straße, Kai + Wasser
    poly(ctx, [(dx0 - 10, GROUND), (dx1 + 10, GROUND), (dx1 + 40, GROUND + 70), (dx0 - 40, GROUND + 70)], P['carpet'])
    rect(ctx, x0, GROUND, x1 - x0, 70, P['walk'])
    for i in range(int(x0 // 120), int(x1 // 120) + 2):
        line(ctx, i * 120, GROUND, i * 120 - 20, GROUND + 70, 2, alpha(C['ink'], 0.25))
    poly(ctx, [(dx0 - 10, GROUND), (dx1 + 10, GROUND), (dx1 + 40, GROUND + 70), (dx0 - 40, GROUND + 70)], P['carpet'])
    rect(ctx, x0, GROUND + 70, x1 - x0, 16, P['stone3'])
    rect(ctx, x0, GROUND + 86, x1 - x0, 200, P['street'])
    for i in range(int(x0 // 200), int(x1 // 200) + 2):
        rect(ctx, i * 200 + 40, GROUND + 180, 100, 8, alpha(C['white'], 0.6))
    rect(ctx, x0, GROUND + 286, x1 - x0, 24, P['stone3'])
    g = cairo.LinearGradient(0, GROUND + 310, 0, GROUND + 900)
    g.add_color_stop_rgba(0, *P['water2']); g.add_color_stop_rgba(1, *P['water'])
    ctx.rectangle(x0, GROUND + 310, x1 - x0, 900)
    ctx.set_source(g)
    ctx.fill()
    for i in range(int(x0 // 140), int(x1 // 140) + 2):
        xx = i * 140 + math.sin(T * 2 + i) * 14
        line(ctx, xx, GROUND + 350 + (i % 3) * 40, xx + 60, GROUND + 350 + (i % 3) * 40, 3, alpha(C['white'], 0.25))
    # Laternen
    for lx in (HX0 - 120, HX1 + 120):
        line(ctx, lx, GROUND + 60, lx, GROUND - 330, 8, hexc('#1E1A16'))
        g = cairo.RadialGradient(lx, GROUND - 345, 4, lx, GROUND - 345, 160)
        g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.5)
        g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        ctx.arc(lx, GROUND - 345, 160, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
        circle(ctx, lx, GROUND - 345, 18, hexc('#FFE6A8'))


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

    def scr(self, x, y):
        return W / 2 + (x - self.x) * self.z, H / 2 + (y - self.y) * self.z


def draw_facade_scene(ctx, cam, T, actors=(), **kw):
    ctx.save()
    cam.apply(ctx)
    hotel_facade(ctx, cam, T, **kw)
    for a in actors:
        a(ctx)
    ctx.restore()


def ferry_long(ctx, x, y, T, length=6000):
    """Sehr lange Fähre (Bug bei x, Wasserlinie y), läuft nach rechts aus dem Bild."""
    bob = math.sin(T * 2) * 4
    y += bob
    rect(ctx, x + 40, y - 120, length, 120, C['white'])
    ctx.move_to(x + 40, y - 120)
    ctx.curve_to(x - 20, y - 110, x - 10, y - 20, x + 40, y)
    ctx.close_path()
    src(ctx, C['white'])
    ctx.fill()
    rect(ctx, x, y - 52, length + 40, 18, P['red'])
    rect(ctx, x + 10, y - 30, length + 40, 8, P['gold'])
    rect(ctx, x + 120, y - 200, length, 80, hexc('#EDE6D6'))
    for i in range(int(length // 70)):
        wx = x + 150 + i * 70
        fill_rrect(ctx, wx, y - 185, 44, 46, 8, P['lit'])
        circle(ctx, wx + 22, y - 85, 13, hexc('#9FC6E8'))
    for i in range(0, int(length // 900) + 1):
        cx = x + 400 + i * 900
        rect(ctx, cx, y - 290, 60, 90, P['red'])
        rect(ctx, cx, y - 290, 60, 14, C['ink'])
        for j in range(3):
            kk = (T * 0.5 + j / 3) % 1
            circle(ctx, cx + 30 + kk * 40, y - 300 - kk * 120, 18 + 20 * kk, alpha(hexc('#C9C3BC'), 0.5 * (1 - kk)))


def sc_owner(ctx, T, t0):
    """Shelly vor ihrem Hotel, Kamera fährt an die Fassade."""
    k = ease(T, t0, t0 + 1.4)
    cam = Cam(540, lerp(-520, -400, k), lerp(1.05, 1.25, k))

    def act(c):
        shelly_boss(c, T, 380, GROUND + 40, 1.15, 'wave', 'open')
        figure(c, 760, GROUND + 40, 1.1, 77, 'travel', suitcase=True)
    draw_facade_scene(ctx, cam, T, [act], belegt=0.0)
    if UI_ON[0]:
        sx, sy = cam.scr(380, GROUND - 230)
        sticker(ctx, 'SHELLY', sx, sy, 46, 'cream', rot=-3, sc=pop(T, t0 + 0.1))
        if T > nw('sandkorn') - 0.1:
            sticker(ctx, 'DIE CHEFIN', sx, sy + 70, 36, 'yellow', rot=2, sc=pop(T, nw('sandkorn') - 0.1))


def sc_rooms(ctx, T, t0):
    """So viele Zimmer wie Sandkörner: Kamera schießt die Fassade hoch, dann weit raus – unendlicher Turm."""
    t_up = nw('viele', 1) - 0.2
    t_out = nw('unendlich', 1) - 0.4
    if T < t_out:
        k = ease(T, t0, t_out)
        y = lerp(-900, -9000, k ** 1.5)
        cam = Cam(540, y, 0.9)
    else:
        k = ease(T, t_out, t_out + 1.6)
        z = math.exp(lerp(math.log(0.9), math.log(0.025), k))
        cam = Cam(540, lerp(-9000, -36000, k), z)
    draw_facade_scene(ctx, cam, T, [], belegt=0.0)
    # Wolken um den Turm
    if cam.z < 0.4 and UI_ON[0] or cam.z < 0.4:
        r = random.Random(4)
        for i in range(10):
            cx_, cy_ = r.uniform(-50, 1130), r.uniform(150, 1100)
            cloud_shape(ctx, cx_ + math.sin(T * 0.3 + i) * 20, cy_, r.uniform(40, 80), alpha(hexc('#3A4380'), 0.85 * (1 - cam.z / 0.4)))
    paper_card(ctx, T, nw('sandkörner') - 0.1, [('SO VIELE ZIMMER WIE', 30, TYPE, P['ink']), ('SANDKÖRNER', 64, SLAB, P['ink'])], 540, 560, -2)
    if T >= nw('unendlich', 1) - 0.1:
        paper_card(ctx, T, nw('unendlich', 1) - 0.1, [('∞', 120, SLAB, P['red']), ('UNENDLICH VIELE', 40, SLAB, P['ink'])], 540, 1180, 2)


def sc_numbers(ctx, T, t0):
    """Zimmer 1, 2, 3 … ohne Ende: von unten nach oben rauschen."""
    k = ease(T, nw('drei') - 0.2, nw('ende') + 0.8)
    y = lerp(-650, -60000, k ** 2.2)
    cam = Cam(540, y, 1.0)
    draw_facade_scene(ctx, cam, T, [], belegt=0.0, all_lit=False)
    for i, (w_, t_) in enumerate([('1', nw('eins')), ('2', nw('zwei')), ('3', nw('drei'))]):
        if UI_ON[0] and T >= t_ - 0.05 and T < nw('ende') - 0.1:
            kk = pop(T, t_ - 0.05)
            ctx.save()
            ctx.translate(320 + i * 220, 600)
            ctx.scale(kk, kk)
            fill_rrect(ctx, -60, -60, 120, 120, 10, P['gold2'])
            text(ctx, w_, 0, 0, 90, P['ink'], font=ZILLA)
            ctx.restore()
    paper_card(ctx, T, nw('ende') - 0.15, [('… OHNE ENDE', 70, SLAB, P['ink'])], 540, 600, -2)


def sc_full(ctx, T, t0):
    k = ease(T, t0, t0 + 2.0)
    cam = Cam(540, lerp(-1100, -700, k), lerp(0.62, 0.72, k))

    def act(c):
        shelly_boss(c, T, 330, GROUND + 40, 1.15, 'present', 'smile')
    draw_facade_scene(ctx, cam, T, [act], belegt=ease(T, nw('belegt') - 0.3, nw('belegt')))
    paper_card(ctx, T, nw('belegt') - 0.05, [('HEUTE ABEND:', 30, TYPE, P['ink']), ('ALLES BELEGT', 66, SLAB, P['red'])], 540, 560, -2)


def sc_ferry(ctx, T, t0):
    """Riesenlange Fähre legt am Kai an, Gäste steigen aus und stellen sich an."""
    cam = Cam(540, 120, 0.72)
    kx = ease(T, t0, t0 + 2.0)
    fx = lerp(1400, 80, kx)

    def act(c):
        ferry_long(c, fx, GROUND + 520, T)
        shelly_boss(c, T, 300, GROUND + 40, 1.0, 'idle', 'o' if T > nw('unendlich', 2) else 'smile')
        if T >= nw('mit', 0, after=t0) - 0.3:
            kk = ease(T, nw('mit', 0, after=t0) - 0.3, nw('gästen') + 1.0)
            n = int(30 * kk)
            for i in range(n, 0, -1):
                gx = 1500 - (n - i) * 0 + i * 70 - 900 * kk
                figure(c, 470 + i * 62, GROUND + 60, 0.95, 100 + i, 'travel', walk=T * 9 + i, face=-1, suitcase=(i % 2 == 0))
    draw_facade_scene(ctx, cam, T, [act], belegt=1.0)
    paper_card(ctx, T, nw('unendlich', 2) - 0.1, [('EINE FÄHRE MIT', 30, TYPE, P['ink']), ('∞ GÄSTEN', 70, SLAB, P['red'])], 540, 520, 2)


def key_icon(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_sub_path()
    ctx.arc(0, -18, 11, 0, 2 * math.pi)
    ctx.set_line_width(5)
    src(ctx, P['gold2'])
    ctx.stroke()
    line(ctx, 0, -7, 0, 22, 5, P['gold2'])
    line(ctx, 0, 12, 8, 12, 4, P['gold2'])
    line(ctx, 0, 19, 7, 19, 4, P['gold2'])
    ctx.restore()


def sc_queue(ctx, T, t0):
    """Alle wollen ein Zimmer: Schlange auf dem Gehweg, Schlüssel über den Köpfen."""
    k = ease(T, t0, t0 + 3.5)
    cam = Cam(lerp(560, 1700, k), -120, 0.62)

    def act(c):
        ferry_long(c, -400, GROUND + 520, T)
        shelly_boss(c, T, 300, GROUND + 40, 1.0, 'idle', 'smile')
        for i in range(40, 0, -1):
            gx = 470 + i * 64
            figure(c, gx, GROUND + 60, 0.95, 100 + i, 'travel', face=-1, suitcase=(i % 2 == 0))
            if UI_ON[0]:
                kk = pop(T, t0 + 0.25 + i * 0.05)
                if kk > 0:
                    key_icon(c, gx, GROUND - 120 + math.sin(T * 4 + i) * 5, 1.3 * kk)
    draw_facade_scene(ctx, cam, T, [act], belegt=1.0)
    paper_card(ctx, T, nw('eins', 1) - 0.1, [('1 ZIMMER PRO GAST', 56, SLAB, P['ink']),
                                             ('NIEMAND BLEIBT DRAUSSEN', 30, TYPE, P['red'])], 540, 520, -2)


def sc_instruction(ctx, T, t0, card_t=None):
    cam = Cam(560, -360, 1.0)

    def act(c):
        shelly_boss(c, T, 420, GROUND + 40, 1.3, 'megaphone', 'open')
        for i in range(6, 0, -1):
            figure(c, 600 + i * 80, GROUND + 60, 1.05, 100 + i, 'travel', face=-1, suitcase=(i % 2 == 0))
    draw_facade_scene(ctx, cam, T, [act], belegt=1.0)
    if UI_ON[0] and T >= nw('anweisung') - 0.2:
        for j in range(3):
            kk = ((T - nw('anweisung')) * 1.2 + j / 3) % 1
            ctx.new_sub_path()
            ctx.arc(560, 1190, 40 + 120 * kk, -0.7, 0.7)
            ctx.set_line_width(6)
            src(ctx, alpha(C['white'], 1 - kk))
            ctx.stroke()
    lines = [('NUR EINE ANWEISUNG:', 30, TYPE, P['ink']), ('WELCHE?', 100, SLAB, P['ink'])]
    if T >= nw('schreibe') - 0.05:
        lines.append(('DEINE ANTWORT IN DIE KOMMENTARE', 26, TYPE, P['red']))
    paper_card(ctx, T, card_t or nw('welche') - 0.1, lines, 540, 600, -2)


def sc_think(ctx, T, t0):
    sc_instruction(ctx, T, t0 - 10, card_t=-1)
    calendar(ctx, T, GAP_AT + 0.05, 540, 1060)


# ---------------------------------------------------------------- Szene C: Seitenflur (Lösung)
SF_H = 560.0           # Höhe einer Etage im Seitenschnitt
SF_DOOR = 230.0        # Türabstand


def side_floor(ctx, y_top, x0, x1, n_first, cam_x, status, T):
    """Eine Etage im Schnitt: Decke, Tapete mit Leuchten, Türen mit Nummern, Teppich mit Rauten."""
    y_wall = y_top + 60
    y_floor = y_top + SF_H - 120
    rect(ctx, x0, y_top, x1 - x0, 60, P['wood3'])
    for i in range(int(x0 // 40), int(x1 // 40) + 1):
        rect(ctx, i * 40, y_top + 8, 20, 44, mixc(P['wood3'], C['white'], 0.05))
    rect(ctx, x0, y_wall, x1 - x0, y_floor - y_wall, P['teal'])
    for i in range(int(x0 // 24), int(x1 // 24) + 1):
        line(ctx, i * 24, y_wall, i * 24, y_floor - 90, 3, P['teal2'])
    rect(ctx, x0, y_wall, x1 - x0, 14, P['cream'])
    rect(ctx, x0, y_floor - 90, x1 - x0, 90, P['wood'])
    rect(ctx, x0, y_floor - 92, x1 - x0, 8, P['wood2'])
    # Teppich
    rect(ctx, x0, y_floor, x1 - x0, 120, P['carpet'])
    rect(ctx, x0, y_floor + 6, x1 - x0, 5, P['gold'])
    rect(ctx, x0, y_floor + 109, x1 - x0, 5, P['gold'])
    for i in range(int(x0 // 80), int(x1 // 80) + 1):
        cx = i * 80 + 40
        poly(ctx, [(cx, y_floor + 38), (cx + 18, y_floor + 60), (cx, y_floor + 82), (cx - 18, y_floor + 60)], P['carpet2'])
        poly(ctx, [(cx, y_floor + 48), (cx + 9, y_floor + 60), (cx, y_floor + 72), (cx - 9, y_floor + 60)], P['gold'])
    # Türen
    for j in range(-1, 12):
        n = n_first + j
        if n < 1:
            continue
        dx = j * SF_DOOR + 400 - cam_x
        if dx < x0 - 200 or dx > x1 + 200:
            continue
        st = status.get(n)
        rect(ctx, dx - 62, y_floor - 270, 124, 270, P['wood3'])
        rect(ctx, dx - 54, y_floor - 262, 108, 262, P['door'] if st != 'open' else hexc('#F2D08A'))
        if st != 'open':
            for (a, b) in ((-240, -150), (-130, -20)):
                rrect(ctx, dx - 40, y_floor + a, 80, b - a, 4)
                ctx.set_line_width(3)
                src(ctx, P['door2'])
                ctx.stroke()
            circle(ctx, dx + 38, y_floor - 130, 5, P['gold'])
        fill_rrect(ctx, dx - 34, y_floor - 320, 68, 36, 4, P['gold2'])
        text(ctx, str(n), dx, y_floor - 302, 26, P['ink'], font=ZILLA)
        # Wandleuchte
        lx = dx + SF_DOOR / 2
        g = cairo.RadialGradient(lx, y_floor - 250, 2, lx, y_floor - 250, 110)
        g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.35)
        g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        ctx.arc(lx, y_floor - 250, 110, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
        poly(ctx, [(lx - 16, y_floor - 236), (lx + 16, y_floor - 236), (lx + 9, y_floor - 268), (lx - 9, y_floor - 268)], P['cream'])
        rect(ctx, lx - 3, y_floor - 236, 6, 20, P['gold'])
        if st == 'free':
            fill_rrect(ctx, dx - 22, y_floor - 175, 44, 70, 5, P['red'])
            circle(ctx, dx, y_floor - 166, 5, C['white'])
            ctx.save()
            ctx.translate(dx, y_floor - 132)
            ctx.rotate(-math.pi / 2)
            text(ctx, 'FREI', 0, 0, 16, C['white'], font=SLAB)
            ctx.restore()
    return y_floor


def arc(ctx, xa, xb, y, h, k, col=None, w=7):
    if k <= 0:
        return
    col = col or P['red']
    n = 40
    m = max(2, int(n * k))
    ctx.move_to(xa, y)
    for i in range(1, m + 1):
        u = i / n
        ctx.line_to(lerp(xa, xb, u), y - math.sin(math.pi * u) * h)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, col)
    ctx.stroke()
    if k > 0.97:
        poly(ctx, [(xb - 15, y - 20), (xb + 15, y - 20), (xb, y + 4)], col)


def sc_solution(ctx, T, t0):
    t_card = TW('jeder') - 0.1
    t1, t2, t3 = TW('geht') - 0.4, TW('vier') - 0.5, TW('sechs') - 0.5
    t_rest = TW('weiter') - 0.2
    t_even = TW('geraden') - 0.2
    t_free = TW('frei') - 0.3
    t_new = TW('jeden') - 0.3
    # Kamera: erst nah (eine Etage), dann Zoom-out auf viele Etagen
    zk = ease(T, t_rest, t_rest + 1.6)
    z = lerp(1.45, 0.42, zk)
    rect(ctx, 0, 0, W, H, P['dark'])
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H / 2 - lerp(0, 0, zk))
    cam_x = lerp(0, 160, ease(T, t1, t3 + 0.8))
    floors = 7
    x0, x1 = -W / z, W + W / z
    base_top = 700
    for fi in range(-(floors // 2), floors // 2 + 1):
        y_top = base_top + fi * SF_H
        n_first = 1 + fi * 10 if fi != 0 else 1
        if fi != 0:
            n_first = 100 + fi * 37
        status = {}
        moved = T >= t_even
        for n in range(max(1, n_first - 1), n_first + 12):
            if T >= t_free:
                status[n] = 'free' if n % 2 else None
            if T >= t_new + 1.2:
                status[n] = None
        y_floor = side_floor(ctx, y_top, x0, x1, n_first, cam_x, status, T)
        # Gäste
        for j in range(0, 11):
            n = n_first + j
            if fi == 0:
                ts = {1: t1, 2: t2, 3: t3}.get(n, t_rest + (n - 4) * 0.1)
            else:
                ts = t_rest + 0.3 + j * 0.08 + abs(fi) * 0.05
            k = ease(T, ts, ts + 0.9)
            xa = j * SF_DOOR + 400 - cam_x
            xb = (2 * n - n_first) * SF_DOOR + 400 - cam_x
            x = lerp(xa, xb, k)
            hop = math.sin(math.pi * k) * 30
            figure(ctx, x + 10, y_floor + 20 - hop, 1.35, n * 3 + fi, 'pajama', walk=T * 10 if 0 < k < 1 else None, face=1 if 0 < k < 1 else 0)
            if ts - 0.1 <= T < t_even + 0.4:
                arc(ctx, xa, xb, y_floor - 340, 90 + 25 * min(n, 6), ease(T, ts - 0.1, ts + 0.5))
        # neue Gäste in ungerade Türen
        if T >= t_new:
            for j in range(0, 11):
                n = n_first + j
                if n % 2 == 0:
                    continue
                ts = t_new + j * 0.06 + abs(fi) * 0.04
                k = ease(T, ts, ts + 0.9)
                if k <= 0:
                    continue
                dx = j * SF_DOOR + 400 - cam_x
                figure(ctx, lerp(dx - 180, dx - 20, k), y_floor + 70, 1.25, 500 + n, 'travel', walk=T * 10 if k < 1 else None,
                       face=1, suitcase=True)
    # Shelly links mit Ansage (nur nah)
    if zk < 0.5:
        shelly_boss(ctx, T, 235, base_top + SF_H - 100, 1.15, 'megaphone', 'open', mirror=False)
    ctx.restore()
    paper_card(ctx, T, t_card, [('SHELLYS ANWEISUNG:', 28, TYPE, P['ink']), ('ZIMMERNUMMER', 52, SLAB, P['ink']),
                                ('× 2', 90, SLAB, P['red'])], 540, 330 + 70, -2)
    if T >= t_even and T < t_free:
        paper_card(ctx, T, t_even, [('ALTE GÄSTE:', 28, TYPE, P['ink']), ('GERADE ZIMMER', 58, SLAB, P['ink'])], 540, 1330, 2)
    elif T >= t_free and T < t_new:
        paper_card(ctx, T, t_free, [('UNGERADE ZIMMER:', 28, TYPE, P['ink']), ('FREI!', 80, SLAB, P['red'])], 540, 1330, 2)
    elif T >= t_new:
        paper_card(ctx, T, t_new, [('∞ FREIE ZIMMER', 52, SLAB, P['ink']), ('FÜR ∞ NEUE GÄSTE', 34, TYPE, P['red'])], 540, 1330, 2)


def sc_still(ctx, T, t0):
    t_h = TW('hilbert') - 0.2
    k = ease(T, t0, t0 + 3)
    cam = Cam(540, lerp(-900, -760, k), 0.68)
    sign, sk = 'HOTEL SANDKORN', 1.0
    if T >= t_h:
        sign = 'HILBERTS HOTEL'
        sk = max(0.01, back_out(T, t_h, t_h + 0.3, 2.0))

    def act(c):
        shelly_boss(c, T, 330, GROUND + 40, 1.15, 'cheer', 'open')
    draw_facade_scene(ctx, cam, T, [act], belegt=1.0, sign=sign, sign_k=sk)
    if T < t_h:
        paper_card(ctx, T, TW('ausgebucht', 1) - 0.1, [('UND AM ENDE:', 28, TYPE, P['ink']), ('IMMER NOCH', 50, SLAB, P['ink']),
                                                     ('AUSGEBUCHT', 64, SLAB, P['red'])], 540, 560, -2)
    else:
        paper_card(ctx, T, t_h, [('DIE REGEL DER CHEFIN', 28, TYPE, P['ink']), ('n → 2n', 96, SLAB, P['ink']),
                                 ('HILBERTS HOTEL', 34, TYPE, P['red'])], 540, 560, -2)


def sc_ferries(ctx, T, t0):
    cam = Cam(540, 0, 0.55)

    def act(c):
        for i in range(9, -1, -1):
            f = 1.0 / (1 + 0.35 * i)
            c.save()
            c.translate(540, GROUND + 330)
            c.scale(f, f)
            ferry_long(c, -900 + i * 260, 120 + 420 * (1 - (1 - f) * 1.0) - 260 * (1 - f), T + i, 2600)
            c.restore()
    draw_facade_scene(ctx, cam, T, [act], belegt=1.0)
    rect(ctx, 0, 0, W, H, alpha(hexc('#0B0E24'), 0.15))
    paper_card(ctx, T, TW('was', 0, after=nw('hilbert')) - 0.1,
               [('UND UNENDLICH', 62, SLAB, P['ink']), ('VIELE FÄHREN?', 62, SLAB, P['ink']), ('IN DIE KOMMENTARE', 28, TYPE, P['red'])], 540, 560, -2)


def hut_card(ctx, T, t0, x, y):
    if T < t0:
        return
    k = back_out(T, t0, t0 + 0.35, 2.0)
    if k <= 0.001:
        return
    ctx.save()
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
    cam = Cam(540, -700, 0.62)

    def act(c):
        shelly_boss(c, T, 330, GROUND + 40, 1.2, 'wave', 'open')
    draw_facade_scene(ctx, cam, T, [act], belegt=1.0)
    paper_card(ctx, T, TW('wohnst') - 0.05, [('WOHNST DU SCHON IN', 34, TYPE, P['ink']), ('MUSCHELTAL?', 80, SLAB, P['ink'])], 540, 520, -2)
    tf = TW('folge') - 0.05
    tap = TW('namen') + 0.3
    if UI_ON[0] and T >= tf:
        k = back_out(T, tf, tf + 0.3, 2.0)
        ctx.save()
        ctx.translate(540, 760)
        ctx.scale(k, k)
        on = T >= tap
        fill_rrect(ctx, -170 + 6, -50 + 10, 340, 100, 14, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -170, -50, 340, 100, 14, C['green'] if on else P['red'])
        text(ctx, 'GEFOLGT' if on else 'FOLGEN', -24 if on else 0, 0, 48, C['white'], font=SLAB)
        if on:
            tick_mark(ctx, 120, 0, 34, C['white'])
        ctx.restore()
    hut_card(ctx, T, TW('hütte') - 0.2, 800, 1240)


