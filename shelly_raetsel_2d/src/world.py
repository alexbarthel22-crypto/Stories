"""Welt: Tiefseekratzer im Querschnitt (Treppenhaus | Aufzug | Wohnung), Meer, Strand mit Bahnhof."""
import math
import random
import cairo
from draw import *
from chars import karla, paul

FH = 420.0          # Etagenhöhe
SLAB = 30.0
X_ST0, X_ST1 = 0.0, 400.0       # Treppenhaus
X_SH0, X_SH1 = 400.0, 660.0     # Aufzugschacht
X_AP0, X_AP1 = 660.0, 1480.0    # Wohnung
X_L, X_R = -50.0, 1530.0        # Außenglas
DOOR_X0, DOOR_X1 = 700.0, 840.0
SEA_Y = 300.0                   # Unterkante Sandinsel / Beginn Meer im Querschnitt
CAB_W, CAB_H = 214.0, 330.0
CAB_X = (X_SH0 + X_SH1) / 2


def fy(n):
    """Fußboden-y von Etage n (0 = Strand, -200 = ganz unten)."""
    return 0.0 if n >= 0 else SEA_Y + (-n) * FH


class Cam:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def apply(self, ctx):
        ctx.translate(W / 2, H / 2)
        ctx.scale(self.z, self.z)
        ctx.translate(-self.x, -self.y)

    def scr(self, x, y):
        return W / 2 + (x - self.x) * self.z, H / 2 + (y - self.y) * self.z

    def bounds(self):
        hw, hh = W / 2 / self.z, H / 2 / self.z
        return self.x - hw, self.y - hh, self.x + hw, self.y + hh


# ---------------------------------------------------------------- Meer
def sea_col(y):
    d = clamp((y - SEA_Y) / (20 * FH))
    stops = [(0.0, C['sea1']), (0.15, hexc('#2A9EC4')), (0.5, C['sea2']), (1.0, C['sea3']), (1.01, C['sea4'])]
    for (o0, c0), (o1, c1) in zip(stops, stops[1:]):
        if d <= o1:
            return mixc(c0, c1, (d - o0) / (o1 - o0))
    return stops[-1][1]


def fish(ctx, x, y, s, c, flip):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    ellipse(ctx, 0, 0, 22, 12, c)
    poly(ctx, [(16, 0), (34, -12), (34, 12)], c)
    poly(ctx, [(-2, -10), (10, -18), (12, -8)], mixc(c, C['white'], 0.25))
    circle(ctx, -11, -3, 3.4, C['white'])
    circle(ctx, -12, -3, 1.8, C['ink'])
    ctx.restore()


FISH_COLS = [hexc('#FFB547'), hexc('#FF7A8A'), hexc('#7FE0D0'), hexc('#FFE070'), hexc('#B39DFF')]


def draw_sea(ctx, x0, y0, x1, y1, t, dark=0.0):
    yy0 = max(y0, SEA_Y)
    if yy0 >= y1:
        return
    n = 24
    hh = (y1 - yy0) / n
    for i in range(n):
        ya = yy0 + i * hh
        c = sea_col(ya + hh / 2)
        rect(ctx, x0, ya, x1 - x0, hh + 1, mixc(c, C['sea4'], dark))
    # Lichtstrahlen nahe der Oberfläche
    if yy0 < SEA_Y + 4000:
        ctx.save()
        for i in range(6):
            bx = -900 + i * 520 + math.sin(t * 0.4 + i) * 40
            g = cairo.LinearGradient(0, SEA_Y, 0, SEA_Y + 2400)
            g.add_color_stop_rgba(0, 1, 1, 1, 0.16 * (1 - dark))
            g.add_color_stop_rgba(1, 1, 1, 1, 0)
            ctx.move_to(bx, SEA_Y)
            ctx.line_to(bx + 160, SEA_Y)
            ctx.line_to(bx + 520, SEA_Y + 2400)
            ctx.line_to(bx + 250, SEA_Y + 2400)
            ctx.close_path()
            ctx.set_source(g)
            ctx.fill()
        ctx.restore()
    # Fische + Blasen (deterministisch je Rasterzelle)
    cell = 700
    for gx in range(int(x0 // cell) - 1, int(x1 // cell) + 2):
        for gy in range(int(yy0 // cell) - 1, int(y1 // cell) + 2):
            r = random.Random(gx * 7919 + gy * 104729)
            if r.random() < 0.55:
                sp = r.uniform(25, 60) * (1 if r.random() < 0.5 else -1)
                fx = gx * cell + ((r.uniform(0, cell) + sp * t) % (cell * 1.6)) - cell * 0.3
                fyy = gy * cell + r.uniform(80, cell - 80) + math.sin(t * 1.5 + gx) * 10
                if fyy > SEA_Y + 60:
                    col = mixc(r.choice(FISH_COLS), sea_col(fyy), 0.2 + 0.25 * clamp((fyy - SEA_Y) / 8400))
                    fish(ctx, fx, fyy, r.uniform(0.9, 1.5), col, sp > 0)
            for k in range(3):
                bx = gx * cell + r.uniform(0, cell)
                by = gy * cell + cell - ((t * r.uniform(50, 90) + r.uniform(0, cell)) % cell)
                if by > SEA_Y + 20:
                    ctx.new_sub_path()
                    ctx.arc(bx + math.sin(t * 2 + k) * 6, by, r.uniform(4, 9), 0, 2 * math.pi)
                    ctx.set_line_width(2.5)
                    src(ctx, alpha(C['white'], 0.35))
                    ctx.stroke()


def seaweed(ctx, x, y, h, t, c, seg=6):
    ctx.move_to(x, y)
    for i in range(1, seg + 1):
        k = i / seg
        ctx.line_to(x + math.sin(t * 1.6 + k * 3 + x) * 14 * k, y - h * k)
    ctx.set_line_width(10)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    src(ctx, c)
    ctx.stroke()


def shell_deco(ctx, x, y, s, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 0)
    for i in range(7):
        a = math.radians(200 + i * 140 / 6)
        ctx.line_to(math.cos(a) * 20, math.sin(a) * 20 + 2)
    ctx.close_path()
    src(ctx, c)
    ctx.fill()
    for i in range(1, 6):
        a = math.radians(200 + i * 140 / 6)
        line(ctx, 0, 0, math.cos(a) * 18, math.sin(a) * 18 + 2, 1.5, mixc(c, C['ink'], 0.2))
    ctx.restore()


def starfish(ctx, x, y, r, c, rot=0):
    pts = []
    for i in range(10):
        a = rot + i * math.pi / 5 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    poly(ctx, pts, c)
    circle(ctx, x, y, r * 0.2, mixc(c, C['white'], 0.3))


# ---------------------------------------------------------------- Etage
def plate(ctx, x, y, label, w=None, size=34):
    tw = text_size(ctx, label, size)[0]
    w = w or tw + 34
    fill_rrect(ctx, x - w / 2, y - 25, w, 50, 10, C['navy'])
    text(ctx, label, x, y, size, C['white'])


def lab(n):
    return '0' if n == 0 else f'−{abs(n)}'


def draw_stairs(ctx, n, y, hl=0.0):
    """Treppenhaus der Etage n (Fußboden y): Lauf 1 von links unten nach rechts zur Zwischenpodest, Lauf 2 zurück."""
    rect(ctx, X_ST0, y - FH + SLAB, X_ST1 - X_ST0, FH - SLAB, hexc('#EDE7DD'))
    # Bullauge zum Meer
    ox, oy = 200, y - FH * 0.62
    circle(ctx, ox, oy, 54, C['gold'])
    circle(ctx, ox, oy, 46, sea_col(y))
    ctx.new_sub_path()
    ctx.arc(ox - 10, oy - 10, 30, math.radians(200), math.radians(260))
    ctx.set_line_width(5)
    src(ctx, alpha(C['white'], 0.35))
    ctx.stroke()
    mid = y - FH / 2
    st = C['pearl3'] if hl <= 0 else mixc(C['pearl3'], C['yellow'], hl)
    st2 = C['white'] if hl <= 0 else mixc(C['white'], C['yellow'], hl * 0.7)
    for (xa, ya, xb, yb) in ((60, y, 340, mid), (340, mid, 60, y - FH)):
        nst = 9
        pts = [(xa, ya)]
        for i in range(nst):
            px = xa + (xb - xa) * (i + 1) / nst
            py0 = ya + (yb - ya) * i / nst
            py1 = ya + (yb - ya) * (i + 1) / nst
            pts += [(pts[-1][0], py1), (px, py1)]
        pts += [(xb, yb + 26), (xa, ya + 26)]
        poly(ctx, pts, st2)
        line(ctx, xa, ya + 26, xb, yb + 26, 8, st)
        # Geländer
        line(ctx, xa, ya - 70, xb, yb - 70, 5, C['gold'])
        for i in range(0, nst + 1, 3):
            px = xa + (xb - xa) * i / nst
            py = ya + (yb - ya) * i / nst
            line(ctx, px, py, px, py - 70, 3, C['gold2'])
    # Zwischenpodest
    rect(ctx, 330, mid, 70, 18, C['pearl2'])
    rect(ctx, 0, y - FH + SLAB, 70, 18, C['pearl2'])


def draw_shaft(ctx, n, y, door_l=0.0, door_r=0.0):
    rect(ctx, X_SH0, y - FH + SLAB, X_SH1 - X_SH0, FH - SLAB, hexc('#C9D6E3'))
    # Schiene/Seile
    for xx in (X_SH0 + 30, X_SH1 - 30):
        rect(ctx, xx - 4, y - FH, 8, FH, hexc('#A9B8C9'))
    # Wände mit Türöffnungen
    for xw, k in ((X_SH0, door_l), (X_SH1, door_r)):
        rect(ctx, xw - 9, y - FH + SLAB, 18, FH - SLAB - 300, C['pearl2'])
        # Schiebetür (Strich) – offen = nach oben eingefahren
        dh = 300 * (1 - k)
        rect(ctx, xw - 6, y - 300, 12, dh, C['gold'])
    # Leuchtanzeige über Schacht


def draw_apartment(ctx, n, y, t, light=1.0, door=0.0, who=None, tod='day'):
    x0, x1 = X_AP0, X_AP1
    top = y - FH + SLAB
    # Flur/Eingangsbereich + Wohnung (warmes Licht)
    wall = mixc(hexc('#F6DDBA'), hexc('#E9B98A'), 0.0)
    rect(ctx, x0, top, x1 - x0, FH - SLAB, wall)
    rect(ctx, x0, y - 22, x1 - x0, 22, hexc('#E2BE92'))
    # Tür
    dx0, dx1 = DOOR_X0, DOOR_X1
    rect(ctx, dx0 - 10, y - 310, dx1 - dx0 + 20, 310, C['gold'])
    rect(ctx, dx0, y - 300, dx1 - dx0, 300, hexc('#5B3A29'))
    # offene Tür = dunkle Öffnung + Türblatt schmal
    dw = (dx1 - dx0) * (1 - 0.82 * door)
    fill_rrect(ctx, dx0, y - 300, dw, 300, 0, C['coral'] if n != -20 else C['pink2'])
    for i in range(3):
        rect(ctx, dx0 + 14, y - 280 + i * 92, max(0, dw - 28), 74, alpha(C['white'], 0.12))
    if door < 0.5:
        circle(ctx, dx0 + dw - 20, y - 150, 6, C['gold'])
    circle(ctx, dx0 + dw / 2, y - 235, 18, C['gold'])
    circle(ctx, dx0 + dw / 2, y - 235, 13, sea_col(y))
    # Nummernschild über der Tür
    plate(ctx, (dx0 + dx1) / 2, y - 345, lab(n))
    # Wohnraum: großes Panoramafenster (Bullauge-Reihe) zum Meer
    wx0, wx1 = 900, 1440
    fill_rrect(ctx, wx0 - 12, top + 40, wx1 - wx0 + 24, 250, 34, C['gold'])
    ctx.save()
    rrect(ctx, wx0, top + 52, wx1 - wx0, 226, 26)
    ctx.clip()
    vgrad(ctx, wx0, top + 52, wx1 - wx0, 226, [(0, sea_col(y - 200)), (1, sea_col(y + 200))])
    r = random.Random(n * 31)
    for i in range(2):
        sp = r.uniform(30, 50)
        fx = wx0 + ((r.uniform(0, 540) + sp * t * (1 if i else -1)) % 640) - 50
        fish(ctx, fx, top + 110 + i * 90 + math.sin(t + i) * 8, 1.1, r.choice(FISH_COLS), i == 1)
    for i in range(4):
        seaweed(ctx, wx0 + 40 + i * 140 + r.uniform(-20, 20), top + 290, r.uniform(60, 120), t,
                mixc(hexc('#3FAE7A'), sea_col(y), 0.3))
    ctx.restore()
    line(ctx, (wx0 + wx1) / 2, top + 52, (wx0 + wx1) / 2, top + 278, 10, C['gold'])
    # Möbel: Sofa + Muschellampe + Pflanze
    fill_rrect(ctx, 1010, y - 110, 300, 90, 30, hexc('#7FC8C2'))
    fill_rrect(ctx, 990, y - 135, 60, 115, 26, hexc('#6BB5AF'))
    fill_rrect(ctx, 1270, y - 135, 60, 115, 26, hexc('#6BB5AF'))
    fill_rrect(ctx, 1040, y - 160, 240, 70, 26, hexc('#8FD5CF'))
    # Muschellampe
    line(ctx, 1390, y - 22, 1390, y - 190, 5, C['gold2'])
    shell_deco(ctx, 1390, y - 190, 2.2, C['lamp'])
    # Pflanze (Seetang im Topf)
    fill_rrect(ctx, 870, y - 80, 50, 58, 8, C['coral'])
    for i in range(3):
        seaweed(ctx, 885 + i * 10, y - 80, 70 + i * 15, t * 0.5, hexc('#4BB37F'), 4)
    # Nachbarn
    if who == 'karla':
        karla(ctx, 1170, y - 22, 1.25, t)
    elif who == 'paul':
        paul(ctx, 1170, y - 22, 1.35, t)


def draw_slab(ctx, y, x0=X_L, x1=X_R):
    rect(ctx, x0, y, x1 - x0, SLAB, C['pearl'])
    rect(ctx, x0, y + SLAB - 6, x1 - x0, 6, C['pearl3'])
    rect(ctx, x0, y, x1 - x0, 4, C['gold'])


def draw_floor(ctx, n, t, st):
    y = fy(n)
    draw_stairs(ctx, n, y, st.get('stair_hl', {}).get(n, 0.0))
    dl = st.get('door_l', {}).get(n, 0.0)
    dr = st.get('door_r', {}).get(n, 0.0)
    draw_shaft(ctx, n, y, dl, dr)
    draw_apartment(ctx, n, y, t, door=st.get('apt_door', {}).get(n, 0.0), who=st.get('who', {}).get(n))
    # Außenwände (Glas, Perlrahmen)
    for xw in (X_L, X_R - 50):
        rect(ctx, xw, y - FH + SLAB, 50, FH - SLAB, alpha(C['white'], 0.18))
        rect(ctx, xw + (0 if xw == X_L else 38), y - FH + SLAB, 12, FH - SLAB, C['pearl2'])
    draw_slab(ctx, y)


def draw_cabin(ctx, yfloor, k_open=0.0, inside=None, glow=0.0):
    x0 = CAB_X - CAB_W / 2
    y0 = yfloor - CAB_H
    fill_rrect(ctx, x0 - 8, y0 - 8, CAB_W + 16, CAB_H + 16, 14, C['gold'])
    rect(ctx, x0, y0, CAB_W, CAB_H, hexc('#FDF6EC'))
    vgrad(ctx, x0, y0, CAB_W, CAB_H, [(0, alpha(C['lamp'], 0.0)), (1, alpha(C['lamp'], 0.35))])
    # Bedienfeld
    fill_rrect(ctx, x0 + 14, yfloor - 250, 22, 200, 8, C['pearl3'])
    for i in range(21):
        circle(ctx, x0 + 25, yfloor - 240 + i * 9, 3.2, C['gold'] if i != glow else C['yellow'])
    rect(ctx, x0, yfloor - 10, CAB_W, 10, C['pearl3'])
    if inside:
        inside()
    # Glasfront mit Reflex
    ctx.move_to(x0 + 30, y0 + 20)
    ctx.line_to(x0 + 80, y0 + 20)
    ctx.line_to(x0 + 30, y0 + 120)
    ctx.close_path()
    src(ctx, alpha(C['white'], 0.25))
    ctx.fill()
    # Schiebetüren (seitlich zur Kamera als Rahmen)
    dw = CAB_W / 2 * (1 - k_open)
    if dw > 1:
        rect(ctx, x0, y0, dw, CAB_H, alpha(hexc('#D8C08A'), 0.3))
        rect(ctx, x0 + CAB_W - dw, y0, dw, CAB_H, alpha(hexc('#D8C08A'), 0.3))
        line(ctx, x0 + dw, y0, x0 + dw, y0 + CAB_H, 3, C['gold2'])
        line(ctx, x0 + CAB_W - dw, y0, x0 + CAB_W - dw, y0 + CAB_H, 3, C['gold2'])
    rect(ctx, x0 - 8, y0 - 22, CAB_W + 16, 16, C['gold2'])


# ---------------------------------------------------------------- Strand / Himmel (y < SEA_Y)
SKY = {
    'day': [(0, hexc('#5DB8F0')), (1, hexc('#BFE8FF'))],
    'eve': [(0, hexc('#3B3A7A')), (0.55, hexc('#E87B6B')), (1, hexc('#FFC27A'))],
    'rain': [(0, hexc('#5B6676')), (1, hexc('#98A3B2'))],
}


def palm(ctx, x, y, h, t, lean=0.15, dark=0.0):
    trunk = mixc(hexc('#B98450'), C['ink'], dark)
    leaf = mixc(hexc('#3DAA6A'), C['ink'], dark)
    tx, ty = x + h * lean, y - h
    ctx.move_to(x - 12, y)
    ctx.curve_to(x - 6, y - h * 0.5, tx - 10, ty + 40, tx - 6, ty)
    ctx.line_to(tx + 6, ty)
    ctx.curve_to(tx + 6, ty + 40, x + 6, y - h * 0.5, x + 12, y)
    ctx.close_path()
    src(ctx, trunk)
    ctx.fill()
    for i in range(6):
        a = math.radians(-170 + i * 36) + math.sin(t * 1.8 + i) * 0.06
        lx, ly = tx + math.cos(a) * 120, ty + math.sin(a) * 60 + 40
        ctx.move_to(tx, ty)
        ctx.curve_to(tx + math.cos(a) * 60, ty - 40 + math.sin(a) * 20, lx, ly - 30, lx, ly)
        ctx.curve_to(lx - math.cos(a) * 40, ly - 10, tx + math.cos(a) * 40, ty - 10, tx, ty)
        src(ctx, leaf)
        ctx.fill()
    for i in range(3):
        circle(ctx, tx - 8 + i * 9, ty + 8, 8, mixc(hexc('#7A5230'), C['ink'], dark))


def train(ctx, x, y, dark=0.0, door=0.0):
    """Strandbahn (2 Wagen), x = Nase links. Steht auf y."""
    body = mixc(C['white'], C['ink'], dark * 0.5)
    for k in range(2):
        cx0 = x + k * 520
        fill_rrect(ctx, cx0, y - 210, 500, 180, 60 if k == 0 else 30, body)
        rect(ctx, cx0 + 10, y - 82, 480, 16, C['pink'])
        rect(ctx, cx0 + 10, y - 62, 480, 6, C['gold'])
        for i in range(4):
            fill_rrect(ctx, cx0 + 70 + i * 105, y - 180, 80, 70, 16, mixc(hexc('#7FD0F0'), C['navy'], 0.15 + dark * 0.4))
        # Tür
        fill_rrect(ctx, cx0 + 230, y - 190, 70 - 60 * door, 150, 12, C['pink2'])
        for wx in (cx0 + 90, cx0 + 400):
            circle(ctx, wx, y - 22, 22, hexc('#3A3F4F'))
            circle(ctx, wx, y - 22, 9, C['pearl3'])
    fill_rrect(ctx, x - 10, y - 160, 70, 90, 40, mixc(hexc('#7FD0F0'), C['navy'], 0.2))
    text(ctx, 'STRANDBAHN', x + 640, y - 125, 30, C['pink2'])


def draw_beach(ctx, x0, y0, x1, y1, t, weather='day', train_x=1150, train_door=0.0, st_open=False, rainbow=0.0):
    if y0 > SEA_Y:
        return
    dark = {'day': 0.0, 'eve': 0.15, 'rain': 0.35}[weather]
    ytop = y0
    ctx.save()
    vgrad(ctx, x0, ytop, x1 - x0, SEA_Y - ytop, SKY[weather] if ytop < -1500 else SKY[weather])
    g = cairo.LinearGradient(0, -2600, 0, SEA_Y)
    for o, c in SKY[weather]:
        g.add_color_stop_rgba(o, *c)
    ctx.rectangle(x0, ytop, x1 - x0, SEA_Y - ytop)
    ctx.set_source(g)
    ctx.fill()
    # Sonne / Regenbogen / Wolken
    if weather == 'day':
        circle(ctx, 1150, -1100, 150, alpha(C['white'], 0.3))
        circle(ctx, 1150, -1100, 110, hexc('#FFF2B0'))
    elif weather == 'eve':
        circle(ctx, 1150, -190, 210, alpha(hexc('#FFD27A'), 0.35))
        circle(ctx, 1150, -190, 160, hexc('#FFB45A'))
        rect(ctx, x0, -150, x1 - x0, 150, alpha(hexc('#FFB45A'), 0.0))
    if rainbow > 0:
        cols = ['#FF5A5F', '#FF9F43', '#FFD93D', '#6BCB77', '#4D96FF', '#9B5DE5']
        for i, cc in enumerate(cols):
            ctx.new_sub_path()
            ctx.arc(700, -60, 1050 - i * 38, math.pi, 2 * math.pi)
            ctx.set_line_width(38)
            src(ctx, alpha(hexc(cc), 0.55 * rainbow))
            ctx.stroke()
    cl = C['white'] if weather != 'rain' else hexc('#6F7A8A')
    for i, (cx, cy, s) in enumerate([(-250, -1250, 120), (420, -1500, 90), (1500, -1350, 140), (900, -950, 70), (-600, -800, 80)]):
        cloud_shape(ctx, cx + (t * 12 * (1 + i * 0.3)) % 300, cy, s * (1.4 if weather == 'rain' else 1), alpha(cl, 0.95))
    # Meer am Horizont (hinter der Insel)
    rect(ctx, x0, -150, x1 - x0, 150, mixc(hexc('#3FB6D9'), C['navy'], dark))
    for i in range(int(x0 // 120), int(x1 // 120) + 1):
        xx = i * 120 + math.sin(t * 2 + i) * 15
        line(ctx, xx, -120 + (i % 3) * 35, xx + 50, -120 + (i % 3) * 35, 4, alpha(C['white'], 0.4))
    # Schiene + Bahn (hinter der Plattform)
    rect(ctx, x0, -40, x1 - x0, 14, hexc('#8A7B6A'))
    train(ctx, train_x, -40, dark, train_door)
    # Insel / Sand
    vgrad(ctx, x0, 0, x1 - x0, SEA_Y, [(0, mixc(C['sand'], C['ink'], dark * 0.5)), (0.25, mixc(C['sand2'], C['ink'], dark * 0.5)), (1, mixc(hexc('#B88E55'), C['ink'], dark * 0.5))])
    rr = random.Random(9)
    for i in range(60):
        sx = rr.uniform(-1500, 3000)
        if x0 - 20 < sx < x1 + 20:
            circle(ctx, sx, rr.uniform(90, SEA_Y - 20), rr.uniform(3, 7), alpha(hexc('#9C7442'), 0.5))
    # Schacht + Treppe durch den Sand
    rect(ctx, X_SH0 - 9, 0, X_SH1 - X_SH0 + 18, SEA_Y + 30, C['pearl2'])
    rect(ctx, X_SH0, 0, X_SH1 - X_SH0, SEA_Y + 30, hexc('#C9D6E3'))
    for xx in (X_SH0 + 30, X_SH1 - 30):
        rect(ctx, xx - 4, -20, 8, SEA_Y + 60, hexc('#A9B8C9'))
    rect(ctx, X_ST0 - 9, 0, X_ST1 - X_ST0 + 18, SEA_Y + 30, C['pearl2'])
    rect(ctx, X_ST0, 0, X_ST1 - X_ST0, SEA_Y + 30, hexc('#EDE7DD'))
    poly(ctx, [(60, SEA_Y + 30), (340, 0), (340, 26), (60, SEA_Y + 56)], C['white'])
    line(ctx, 60, SEA_Y - 40, 340, -70, 5, C['gold'])
    rect(ctx, x0, 0, x1 - x0, 10, mixc(C['sand2'], C['ink'], dark * 0.4))
    r = random.Random(5)
    for i in range(40):
        sx = r.uniform(-1500, 3000)
        if x0 - 50 < sx < x1 + 50:
            if r.random() < 0.5:
                shell_deco(ctx, sx, r.uniform(30, 70), r.uniform(0.8, 1.4), r.choice([C['pink3'], C['cream'], hexc('#F9B6A0')]))
            else:
                starfish(ctx, sx, r.uniform(30, 70), r.uniform(12, 20), r.choice([hexc('#FF8A5B'), hexc('#F25F7A')]), r.uniform(0, 1))
    # Palmen
    for px, ph in ((-260, 520), (-120, 380), (1280, 470), (1430, 560)):
        palm(ctx, px, 0, ph, t, 0.12 if px > 0 else -0.12, dark * 0.6)
    # Treppenausgang (kleines Häuschen)
    fill_rrect(ctx, X_ST0 + 20, -340, 270, 350, 40, C['pearl'])
    rect(ctx, X_ST0 + 20, -340, 270, 14, C['gold'])
    fill_rrect(ctx, X_ST0 + 85, -285, 140, 285, 20, hexc('#5B3A29') if not st_open else hexc('#2A1A12'))
    sticker(ctx, 'TREPPE', X_ST0 + 155, -312, 26, 'cream')
    # Glaskuppel über dem Aufzug (Station "Etage 0")
    cx = (X_SH0 + X_SH1) / 2
    ctx.save()
    ctx.translate(cx, 0)
    ctx.scale(1.0, 1.85)
    ctx.new_sub_path()
    ctx.arc(0, 0, 225, math.pi, 2 * math.pi)
    ctx.close_path()
    ctx.restore()
    src(ctx, alpha(hexc('#DFF4FF'), 0.55))
    ctx.fill_preserve()
    ctx.set_line_width(10)
    src(ctx, C['gold'])
    ctx.stroke()
    for a in (200, 240, 270, 300, 340):
        line(ctx, cx, 0, cx + math.cos(math.radians(a)) * 225, math.sin(math.radians(a)) * 225 * 1.85, 4, alpha(C['gold'], 0.7))
    circle(ctx, cx, -418, 18, C['white'])
    sticker(ctx, 'TIEFSEEKRATZER', cx, -500, 48, 'navy')
    # Schild
    plate(ctx, cx + 330, -60, 'STRAND · ETAGE 0', size=26)
    ctx.restore()


def rain(ctx, x0, y0, x1, y1, t, dens=1.0):
    r = random.Random(int(t * 30) % 7)
    n = int((x1 - x0) * (y1 - y0) / 9000 * dens)
    ctx.set_line_width(3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, alpha(hexc('#D8E6F5'), 0.65))
    for i in range(n):
        rx = r.uniform(x0, x1)
        ry = r.uniform(y0, y1)
        ctx.move_to(rx, ry)
        ctx.line_to(rx - 10, ry + 46)
    ctx.stroke()


def draw_view(ctx, cam, t, st):
    """Komplette Querschnitt-Ansicht. st: weather, cabin_y, cabin_open, door_l/door_r, who, ..."""
    x0, y0, x1, y1 = cam.bounds()
    ctx.save()
    cam.apply(ctx)
    draw_sea(ctx, x0 - 10, y0 - 10, x1 + 10, y1 + 10, t, st.get('sea_dark', 0.0))
    draw_beach(ctx, x0 - 10, y0 - 10, x1 + 10, y1 + 10, t, st.get('weather', 'day'), st.get('train_x', 1150),
               st.get('train_door', 0.0), st.get('st_open', False), st.get('rainbow', 0.0))
    # Etagen im Bild
    n_hi = min(-1, -int((y0 - SEA_Y) // FH) + 1)
    n_lo = max(-20, -int((y1 - SEA_Y) // FH) - 1)
    for n in range(n_lo, n_hi + 1):
        if n <= -1:
            draw_floor(ctx, n, t, st)
    # Grundplatte Etage 0 (Strand) – Kuppelboden
    if y0 < 60:
        draw_slab(ctx, 0, X_SH0 - 240, X_SH1 + 240)
    # Tiefsee-Boden unter -200
    yb = fy(-20)
    if y1 > yb:
        rect(ctx, x0 - 10, yb + SLAB, x1 - x0 + 20, y1 - yb, hexc('#C9A86A'))
        r = random.Random(3)
        for i in range(30):
            sx = r.uniform(-1200, 2700)
            shell_deco(ctx, sx, yb + 70 + r.uniform(0, 80), r.uniform(1, 1.8), r.choice([C['pink3'], C['cream']]))
    # Aufzugkabine + Figuren
    if 'cabin_y' in st:
        draw_cabin(ctx, st['cabin_y'], st.get('cabin_open', 0.0), st.get('in_cabin'), st.get('cabin_glow', -1))
    # Etagenschilder am Schacht immer sichtbar (über der Kabine)
    for n in range(n_lo, n_hi + 1):
        if n <= -1:
            plate(ctx, (X_SH0 + X_SH1) / 2, fy(n) - FH + SLAB + 30, lab(n), size=26)
    for fn in st.get('actors', []):
        fn(ctx)
    if st.get('weather') == 'rain' and y0 < 0:
        rain(ctx, x0, y0, x1, min(y1, 20), t)
    ctx.restore()
