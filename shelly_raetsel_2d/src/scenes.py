"""Zeitleiste des Rätselvideos (Endzeit in Sekunden, 30 fps)."""
import math
import random
import cairo
from draw import *
from chars import shelly, karla, paul, umbrella, SH_Y
from world import *

# Pausen in der Sprachspur: (Originalzeit, Länge)
GAPS = [(48.9, 0.9), (54.7, 0.5)]
VO_END = 74.68


def g(t):
    return t + sum(d for at, d in GAPS if t >= at)


END = g(VO_END) + 2.0

# ---------------------------------------------------------------- Hilfen
FLOOR_CABX = CAB_X


def path_x(t, keys):
    """keys: [(t, x), ...] -> x(t), Gehphase und Richtung."""
    if t <= keys[0][0]:
        return keys[0][1], None, 0
    for (ta, xa), (tb, xb) in zip(keys, keys[1:]):
        if t <= tb:
            k = (t - ta) / (tb - ta) if tb > ta else 1
            x = xa + (xb - xa) * k
            moving = abs(xb - xa) > 1
            return x, (x * 0.075 if moving else None), (1 if xb > xa else -1) if moving else 0
    return keys[-1][1], None, 0


def ride(t, t0, t1, n0, n1):
    k = ease(t, t0, t1)
    return lerp(n0, n1, k)


def cab_y_of(nf):
    """Kabinenboden-y für (gebrochene) Etage nf."""
    if nf >= -1:
        return lerp(fy(-1), 0.0, clamp(nf + 1))
    return SEA_Y + (-nf) * FH


def flabel(nf, final=None):
    n = int(round(nf))
    return lab(n)


def blink_at(t, times):
    return 1.0 if any(0 <= t - b < 0.12 for b in times) else 0.0


BL = [0.9, 3.7, 6.1, 9.3, 12.2, 15.4, 18.8, 23.1, 27.6, 31.9, 36.0, 40.2, 44.7, 49.6, 53.3, 58.4, 62.9, 67.0, 72.3, 76.4]


def chips(ctx, T, clock=None, floor=None):
    if clock:
        hhmm, hour, kind, t0 = clock
        clock_chip(ctx, 330, 175, hhmm, hour, kind, pop(T, t0))
    if floor:
        label, direction, t0, ok = floor
        floor_chip(ctx, 230 + 0, 300, label, direction, pop(T, t0), ok)


def vignette(ctx, a=0.22):
    g_ = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75)
    g_.add_color_stop_rgba(0, 0, 0, 0, 0)
    g_.add_color_stop_rgba(1, 0, 0, 0, a)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g_)
    ctx.fill()


def green_track(ctx, cam, y_from, y_to, x=None):
    x = x or X_SH0 + 18
    ctx.save()
    cam.apply(ctx)
    line(ctx, x, y_from, x, y_to, 9, C['green'])
    d = -1 if y_to < y_from else 1
    poly(ctx, [(x - 20, y_to - d * 4), (x + 20, y_to - d * 4), (x, y_to + d * 30)], C['green'])
    ctx.restore()


# ---------------------------------------------------------------- Außenansicht
EXT_ROWS = 20
EXT_ROW_H = 120
EXT_TOP = 260


def ext_row_y(n):
    return EXT_TOP + (-n - 1) * EXT_ROW_H + EXT_ROW_H


def exterior(ctx, cy, z, T, weather='day', hl=0.0, sh=None):
    cam = Cam(540, cy, z)
    x0, y0, x1, y1 = cam.bounds()
    ctx.save()
    cam.apply(ctx)
    dark = {'day': 0, 'eve': 0.25, 'night': 0.5}[weather]
    sky = {'day': [(0, hexc('#5DB8F0')), (1, hexc('#BFE8FF'))],
           'eve': [(0, hexc('#2E2F6B')), (0.6, hexc('#E07A6E')), (1, hexc('#FFC27A'))],
           'night': [(0, hexc('#0E1638')), (1, hexc('#2C3A72'))]}[weather]
    g_ = cairo.LinearGradient(0, -1400, 0, 0)
    for o, c in sky:
        g_.add_color_stop_rgba(o, *c)
    ctx.rectangle(x0, y0, x1 - x0, -y0 + 10)
    ctx.set_source(g_)
    ctx.fill()
    if weather == 'day':
        circle(ctx, 860, -900, 110, alpha(C['white'], 0.3))
        circle(ctx, 860, -900, 80, hexc('#FFF2B0'))
    elif weather == 'eve':
        circle(ctx, 820, -120, 170, alpha(hexc('#FFD27A'), 0.35))
        circle(ctx, 820, -120, 120, hexc('#FFB45A'))
    for i, (cx_, cy_, s_) in enumerate([(160, -1000, 80), (640, -1250, 60), (980, -700, 70)]):
        cloud_shape(ctx, cx_ + (T * 10 * (1 + i * .3)) % 200, cy_, s_, alpha(C['white'], 0.9 - dark * 0.6))
    # Meer
    sea_bottom = ext_row_y(-20) + 160
    n = 30
    for i in range(n):
        ya = i * sea_bottom / n
        k = i / n
        c = mixc(mixc(C['sea1'], C['sea3'], k), C['sea4'], dark * 0.6 + k * 0.2)
        rect(ctx, x0, ya, x1 - x0, sea_bottom / n + 1, c)
    for i in range(-6, 16):
        xx = i * 90 + math.sin(T * 2 + i) * 12
        line(ctx, xx, 18 + (i % 2) * 10, xx + 40, 18 + (i % 2) * 10, 4, alpha(C['white'], 0.5))
    # Lichtstrahlen
    for i in range(5):
        bx = -200 + i * 300 + math.sin(T * 0.5 + i) * 30
        g2 = cairo.LinearGradient(0, 0, 0, 1800)
        g2.add_color_stop_rgba(0, 1, 1, 1, 0.14 * (1 - dark))
        g2.add_color_stop_rgba(1, 1, 1, 1, 0)
        poly(ctx, [(bx, 0), (bx + 90, 0), (bx + 330, 1800), (bx + 160, 1800)])
        ctx.set_source(g2)
        ctx.fill()
    # Meeresboden
    rect(ctx, x0, sea_bottom - 40, x1 - x0, y1 - sea_bottom + 60, hexc('#C9A86A'))
    r = random.Random(4)
    for i in range(14):
        seaweed(ctx, r.uniform(-100, 1180), sea_bottom - 30, r.uniform(120, 260), T, hexc('#3FAE7A'), 6)
    for i in range(18):
        sx = r.uniform(-100, 1180)
        if r.random() < 0.5:
            shell_deco(ctx, sx, sea_bottom + r.uniform(0, 80), r.uniform(1.2, 2.2), r.choice([C['pink3'], C['cream'], hexc('#F9B6A0')]))
        else:
            starfish(ctx, sx, sea_bottom + r.uniform(0, 80), r.uniform(16, 26), r.choice([hexc('#FF8A5B'), hexc('#F25F7A')]), r.uniform(0, 1))
    # Koralle
    for cx_ in (90, 960):
        for j in range(5):
            a = math.radians(-150 + j * 30)
            line(ctx, cx_, sea_bottom, cx_ + math.cos(a) * 110, sea_bottom + math.sin(a) * 140, 18, hexc('#FF7A8A'))
    # Fische
    for i in range(9):
        rr = random.Random(i * 13)
        sp = rr.uniform(30, 70) * (1 if i % 2 else -1)
        fx = (rr.uniform(0, 1400) + sp * T) % 1400 - 160
        fish(ctx, fx, 300 + i * 290 + math.sin(T + i) * 10, rr.uniform(1.4, 2.0), rr.choice(FISH_COLS), sp > 0)
    # Turm
    tx0, tx1 = 330, 750
    rect(ctx, tx0 - 14, 40, tx1 - tx0 + 28, sea_bottom - 40, C['gold'])
    rect(ctx, tx0, 40, tx1 - tx0, sea_bottom - 40, C['pearl'])
    for n_ in range(-1, -21, -1):
        yr = ext_row_y(n_)
        rect(ctx, tx0, yr - 6, tx1 - tx0, 8, C['pearl3'])
        lit = hexc('#FFE3A3')
        for i in range(3):
            fill_rrect(ctx, tx0 + 30 + i * 125, yr - EXT_ROW_H + 26, 105, EXT_ROW_H - 46, 14, lit)
        if n_ == -20 and hl > 0:
            rrect(ctx, tx0 - 30, yr - EXT_ROW_H + 6, tx1 - tx0 + 60, EXT_ROW_H - 4, 18)
            ctx.set_line_width(10)
            src(ctx, alpha(C['yellow'], hl))
            ctx.stroke()
        if n_ in (-1, -10, -20):
            plate(ctx, tx0 - 80, yr - EXT_ROW_H / 2, lab(n_), size=30)
    # Insel mit Kuppel und Palmen
    ctx.move_to(60, 40)
    ctx.curve_to(200, -40, 880, -40, 1020, 40)
    ctx.close_path()
    src(ctx, C['sand'])
    ctx.fill()
    palm(ctx, 170, 8, 320, T, -0.1, dark * 0.5)
    palm(ctx, 930, 8, 360, T, 0.1, dark * 0.5)
    ctx.new_sub_path()
    ctx.arc(540, -20, 150, math.pi, 2 * math.pi)
    ctx.close_path()
    src(ctx, alpha(hexc('#DFF4FF'), 0.7))
    ctx.fill_preserve()
    ctx.set_line_width(8)
    src(ctx, C['gold'])
    ctx.stroke()
    circle(ctx, 540, -175, 12, C['white'])
    if sh:
        sh(ctx)
    ctx.restore()
    return cam


# ---------------------------------------------------------------- Szenen
def sc_intro(ctx, T):
    """0 – Ganz unten: Shelly in ihrer Wohnung auf −20."""
    y = fy(-20)
    z = lerp(1.25, 1.36, ease(T, 0, 2.1))
    cam = Cam(1060, y - 330, z)
    wave = math.sin(T * 9) * 14

    def act(c):
        shelly(c, 1160, y - 2, 1.0, arms={'R': (34 + wave * 0.3, -140 + wave)}, expr='open' if T > 0.3 else 'smile',
               blink=blink_at(T, BL))
    draw_view(ctx, cam, T, {'actors': [act], 'cabin_y': fy(-20)})
    sx, sy = cam.scr(1160, y - 245)
    sticker(ctx, 'SHELLY', sx, sy, 52, 'cream', rot=-4, sc=pop(T, 0.25))


def sc_exterior(ctx, T, t0):
    k = ease(T, t0 + 0.1, t0 + 2.5)
    cy = lerp(-250, ext_row_y(-20) - 520, k)
    cam = exterior(ctx, cy, 1.0, T, 'day', hl=ease(T, g(3.88), g(4.1)))
    sx, sy = cam.scr(540, ext_row_y(-20) - 260)
    sticker(ctx, 'ETAGE −20', 540, 1220, 76, 'yellow', rot=-3, sc=pop(T, g(3.88)))
    sticker(ctx, 'UNTER DEM MEER', 540, 1360, 56, 'cream', rot=2, sc=pop(T, g(4.98)))


def walk_out_apartment(T, t_start, t_door, t_cab, t_in):
    """Gemeinsamer Weg: Wohnzimmer -> Tür -> Kabine (−20)."""
    keys = [(t_start, 1150), (t_door, 780), (t_cab, CAB_X + 10)]
    return path_x(T, keys)


def sc_morning(ctx, T, umb=False, label_t=None, clock=('07:00', 7.0, 'sun')):
    """Wohnung −20 -> Kabine -> Fahrt nach oben (Start)."""
    y = fy(-20)
    t0 = T0 = label_t
    ts = clock_t = T0
    # Zeitplan relativ
    a, b, c_, d = ts + 0.3, ts + 1.4, ts + 2.4, ts + 2.7
    x, ph, dr = path_x(T, [(a, 1150), (b, 790), (c_, CAB_X + 6)])
    door = ease(T, a + 0.6, a + 0.9) * (1 - ease(T, c_, c_ + 0.3))
    cab_open = ease(T, b, b + 0.3) * (1 - ease(T, d + 0.2, d + 0.5))
    shaft_r = cab_open
    cam = Cam(lerp(860, 700, ease(T, b - 0.2, c_)), y - 300, 1.1)

    def act(cx):
        if x > X_SH1 - 20:
            draw_sh(cx)

    def draw_sh(cx):
        u = {'ang': math.radians(78), 'state': 'closed'} if umb else None
        shelly(cx, x, y - 2 if x > X_SH1 - 20 else y - 10, 1.0, face=dr * 0.8, walk=ph, mirror=dr < 0,
               arms={'R': (24, -58)} if umb else None, umb=u, blink=blink_at(T, BL))

    def inside():
        if x <= X_SH1 - 20:
            draw_sh(ctx)
    st = {'actors': [act], 'cabin_y': fy(-20), 'cabin_open': cab_open, 'in_cabin': inside,
          'door_r': {-20: shaft_r}, 'apt_door': {-20: door}}
    draw_view(ctx, cam, T, st)
    return cam


def sc_ride(ctx, T, n0, n1, t0, t1, cam_x=620, z=0.9, umb=False, open_at=None, expr='smile', track=True,
            exit_left=None, label=None):
    """Kabine fährt von n0 nach n1, Kamera folgt."""
    nf = ride(T, t0, t1, n0, n1)
    cy = cab_y_of(nf)
    cam = Cam(cam_x, cy - 200, z)
    k_open = ease(T, open_at, open_at + 0.3) if open_at else 0.0
    xs = CAB_X + 6
    ph = None
    mirror = False
    if exit_left and T > exit_left:
        xs, ph, dr = path_x(T, [(exit_left, CAB_X + 6), (exit_left + 0.9, 250)])
        mirror = True

    def draw_sh(cx):
        u = {'ang': math.radians(78), 'state': 'closed'} if umb else None
        shelly(cx, xs, cy - 10 if xs > X_SH0 - 10 else cy - 2, 1.0, walk=ph, mirror=mirror, expr=expr,
               arms={'R': (24, -58)} if umb else None, umb=u, blink=blink_at(T, BL), face=-0.8 if mirror else 0)

    def inside():
        if xs > X_SH0 - 10:
            draw_sh(ctx)

    def act(cx):
        if xs <= X_SH0 - 10:
            draw_sh(cx)
    n_here = int(round(nf))
    st = {'cabin_y': cy, 'cabin_open': k_open, 'in_cabin': inside, 'actors': [act],
          'door_l': {n_here: k_open if exit_left else 0.0}}
    draw_view(ctx, cam, T, st)
    if track and T > t0:
        green_track(ctx, cam, cab_y_of(n0) - 20, cy - 20)
    return cam, nf


def stair_pos(f, n_start):
    """Position auf der Treppe nach f Etagen Aufstieg ab n_start (Fußpunkt, Richtung)."""
    n = n_start + math.floor(f)
    k = f - math.floor(f)
    y = fy(n)
    mid = y - FH / 2
    if k < 0.5:
        u = k / 0.5
        return lerp(60, 340, u), lerp(y, mid, u), 1
    u = (k - 0.5) / 0.5
    return lerp(340, 60, u), lerp(mid, y - FH, u), -1


def sc_climb(ctx, T, t0, t1, n_start, floors, cam_z=0.95, who=None, cam_fixed=None, expr='smile'):
    k = ease(T, t0, t1) if cam_fixed is None else clamp((T - t0) / (t1 - t0))
    f = floors * k
    x, y, dr = stair_pos(f, n_start)
    if cam_fixed:
        cam = cam_fixed
    else:
        cam = Cam(420, y - 200, cam_z)

    def act(cx):
        shelly(cx, x, y, 1.0, walk=T * 14, mirror=dr < 0, face=dr * 0.8, expr=expr, blink=blink_at(T, BL))
    st = {'actors': [act], 'who': who or {}}
    draw_view(ctx, cam, T, st)
    return cam, n_start + f


def neighbors_actors(T, y_k, y_p, wonder):
    def act(cx):
        karla(cx, 1000, y_k - 2, 1.05, T, wonder)
        paul(cx, 1010, y_p - 2, 1.15, T, wonder)
    return act


def sc_beach(ctx, T, weather, cam, actors=(), st_open=False, rainbow=0.0, train_door=0.0, train_x=860):
    st = {'weather': weather, 'actors': list(actors), 'cabin_y': 0.0, 'st_open': st_open, 'rainbow': rainbow,
          'train_x': train_x, 'train_door': train_door}
    draw_view(ctx, cam, T, st)


# ---------------------------------------------------------------- Lösungs-Nahaufnahme
SOL_FEET = 1650
SOL_S = 3.2
SOL_X = 520
PAN_X = 308
ARM = 1.35


def btn_y(i):
    """i = 0 (Etage 0) … 20 (Etage −20)."""
    return 882 + i * 28.5


def solution(ctx, T):
    # Hintergrund: Flur
    rect(ctx, 0, 0, W, H, hexc('#EDE6DA'))
    rect(ctx, 0, 1700, W, 220, hexc('#C9BFB0'))
    for i in range(8):
        line(ctx, i * 160 - 40, 1700, i * 160 - 120, 1920, 3, alpha(C['ink'], 0.08))
    # Kabine
    fx0, fy0, fx1, fy1 = 120, 520, 960, 1710
    fill_rrect(ctx, fx0 - 26, fy0 - 26, fx1 - fx0 + 52, fy1 - fy0 + 52, 20, C['navy'])
    vgrad(ctx, fx0, fy0, fx1 - fx0, fy1 - fy0, [(0, hexc('#FBF5EA')), (1, hexc('#EADFCB'))])
    # Türen rechts (Perlmutt/Gold)
    rect(ctx, 560, fy0 + 30, 380, fy1 - fy0 - 30, hexc('#E7C27D'))
    for i in range(9):
        line(ctx, 580 + i * 40, fy0 + 40, 580 + i * 40, fy1 - 10, 4, alpha(C['gold2'], 0.5))
    line(ctx, 750, fy0 + 30, 750, fy1, 4, C['gold2'])
    # Handlauf
    line(ctx, 560, 1300, 940, 1300, 12, C['gold2'])
    # Muschel-Deko an der Wand
    shell_deco(ctx, 420, 640, 2.0, alpha(C['pink3'], 0.9))
    # Bedienfeld
    fill_rrect(ctx, PAN_X - 70, btn_y(0) - 60, 140, btn_y(20) - btn_y(0) + 120, 22, hexc('#D9CFC0'))
    fill_rrect(ctx, PAN_X - 60, btn_y(0) - 50, 120, btn_y(20) - btn_y(0) + 100, 18, hexc('#F7F2EA'))
    return fx0, fy0, fx1, fy1


def panel_buttons(ctx, T, lit, reach_box=0.0, crosses=0.0, top_ok=0.0):
    for i in range(21):
        y = btn_y(i)
        on = lit.get(i, 0.0)
        circle(ctx, PAN_X + 18, y, 11, C['gold2'])
        circle(ctx, PAN_X + 18, y, 8.5, mixc(C['pearl'], C['yellow'], on))
        if on > 0:
            circle(ctx, PAN_X + 18, y, 22, alpha(C['yellow'], 0.35 * on))
        text(ctx, lab(-i), PAN_X - 16, y, 18, C['ink'], font=FONT2)
    if reach_box > 0:
        y0, y1 = btn_y(10) - 22, btn_y(20) + 22
        rrect(ctx, PAN_X - 46, y0, 92, (y1 - y0) * reach_box, 14)
        ctx.set_line_width(6)
        src(ctx, C['green'])
        ctx.stroke()
    if crosses > 0:
        for i in range(0, 10):
            k = clamp(crosses * 10 - (9 - i))
            if k > 0:
                ctx.save()
                ctx.translate(PAN_X + 18, btn_y(i))
                ctx.scale(k, k)
                cross_icon(ctx, 0, 0, 7)
                ctx.restore()


def solution_scene(ctx, T):
    solution(ctx, T)
    tA = g(54.77)
    t_klein = g(55.89)
    t_down = g(56.91)
    t_press20 = g(60.31)
    t_up = g(61.71)
    t_reach = g(62.75)
    t_10 = g(64.23)
    t_rain = g(65.10)
    t_umb = g(66.87)
    t_raise = g(67.91)
    t_press0 = g(68.97)
    t_strand = g(69.79)
    lit = {}
    # Arm/Pose
    tip_target = None
    tiptoe = 0.0
    expr = 'smile'
    arm_tgt = None
    umb = None
    look = (0, 0)

    def to_local(wx, wy, lift=0.0):
        return ((SOL_X - wx) / SOL_S, (wy - SOL_FEET) / SOL_S + lift)

    rest = (24, -46)
    # 1) Knopf −20 drücken
    p20 = (PAN_X + 24, btn_y(20))
    if t_down <= T < t_up:
        k = ease(T, t_press20 - 0.6, t_press20) * (1 - ease(T, t_press20 + 0.7, t_up))
        tg = to_local(*p20)
        arm_tgt = (lerp(rest[0], tg[0], k), lerp(rest[1], tg[1], k))
        look = (-6, 6 * k)
        if T >= t_press20:
            lit[20] = ease(T, t_press20, t_press20 + 0.1)
    # 2) Hoch: nur bis −10
    if t_up <= T < t_umb:
        k = ease(T, t_reach - 0.3, t_10)
        tiptoe = k
        p10 = (PAN_X + 24, btn_y(10))
        tg = to_local(p10[0], p10[1], 7 * k)
        arm_tgt = (lerp(rest[0], tg[0], k), lerp(rest[1], tg[1], k))
        expr = 'strain' if k > 0.5 else 'smile'
        look = (-6, -8 * k)
        if T >= t_10:
            lit[10] = ease(T, t_10, t_10 + 0.1)
        if T > t_rain:
            kk = 1 - ease(T, t_rain, t_rain + 0.5)
            arm_tgt = (lerp(rest[0], arm_tgt[0], kk), lerp(rest[1], arm_tgt[1], kk))
            tiptoe *= kk
            expr = 'think'
    # 3) Regenschirm
    if T >= t_umb:
        appear = ease(T, t_umb, t_umb + 0.25)
        kr = ease(T, t_raise, t_press0 - 0.1)
        top = (PAN_X + 24, btn_y(0))
        # Griffposition: entlang der Linie Spitze -> Schulter
        L = 118 * SOL_S
        shx, shy = SOL_X - 15.5 * SOL_S, SOL_FEET + SH_Y * SOL_S
        dx, dy = shx - top[0], shy - top[1]
        dd = math.hypot(dx, dy)
        hx_r, hy_r = top[0] + dx / dd * L, top[1] + dy / dd * L
        hold = (SOL_X - 24 * SOL_S, SOL_FEET - 46 * SOL_S)
        hx, hy = lerp(hold[0], hx_r, kr), lerp(hold[1], hy_r, kr)
        ang_w = lerp(math.radians(-118), math.atan2(top[1] - hy_r, top[0] - hx_r), kr)
        tg = to_local(hx, hy)
        arm_tgt = tg
        umb = {'ang': math.pi - ang_w, 'state': 'closed', 'scale': appear}
        expr = 'open' if T > t_press0 else 'smile'
        look = (-6, -10 * kr)
        if T >= t_press0:
            lit[0] = ease(T, t_press0, t_press0 + 0.1)
        lit[10] = 0
    if T < t_umb:
        lit.setdefault(10, lit.get(10, 0))
    panel_buttons(ctx, T, lit, reach_box=ease(T, t_10 + 0.1, t_10 + 0.5) if t_10 < T < t_umb else 0.0,
                  crosses=ease(T, t_10 + 0.5, t_10 + 1.1) if t_10 < T < t_umb else 0.0)
    arms = {'R': arm_tgt or rest, 'L': (-24, -46)}
    if umb and umb['scale'] < 1:
        ctx.push_group()
        out = shelly(ctx, SOL_X, SOL_FEET, SOL_S, mirror=True, arms=arms, umb=umb, tiptoe=tiptoe, expr=expr,
                     look=look, blink=blink_at(T, BL), face=-0.4, arm_len=ARM)
        ctx.pop_group_to_source()
        ctx.paint()
    else:
        shelly(ctx, SOL_X, SOL_FEET, SOL_S, mirror=True, arms=arms, umb=umb, tiptoe=tiptoe, expr=expr, look=look,
               blink=blink_at(T, BL), face=-0.4, arm_len=ARM)
    # Regen-Andeutung hinter dem Glas (nur Stimmung)
    # Sticker
    top_y = 300
    if tA <= T < t_klein:
        sticker(ctx, 'DIE LÖSUNG', 540, top_y, 70, 'cream', rot=-3, sc=pop(T, tA))
    elif t_klein <= T < t_down:
        sticker(ctx, 'SHELLY IST SEHR KLEIN', 540, top_y, 60, 'yellow', rot=-2, sc=pop(T, t_klein))
    elif t_down <= T < t_up:
        sticker(ctx, 'RUNTER: KNOPF −20', 520, top_y, 58, 'cream', rot=-2, sc=pop(T, t_down), icon='check')
    elif t_up <= T < t_rain:
        sticker(ctx, 'HOCH: NUR BIS −10', 540, top_y, 60, 'cream', rot=2, sc=pop(T, t_up))
    elif T >= t_rain:
        sticker(ctx, 'UND BEI REGEN?', 540, top_y, 62, 'blue', rot=-2, sc=pop(T, t_rain), icon='rain')
    if t_umb <= T:
        sticker(ctx, 'REGENSCHIRM!', 760, 1480, 54, 'yellow', rot=4, sc=pop(T, t_umb + 0.1))
    if T >= t_press0:
        ctx.save()
        ctx.translate(PAN_X + 18 - 80, btn_y(0))
        k = back_out(T, t_press0, t_press0 + 0.35)
        ctx.scale(k, k)
        check_icon(ctx, 0, 0, 30)
        ctx.restore()
        sticker(ctx, 'ETAGE 0 · STRAND', 600, 430, 52, 'green', rot=-2, sc=pop(T, t_strand), icon='check')


# ---------------------------------------------------------------- Fragekarte
def question_bg(ctx, T):
    vgrad(ctx, 0, 0, W, H, [(0, hexc('#0E2A55')), (0.7, hexc('#123C73')), (1, hexc('#0A1F44'))])
    r = random.Random(11)
    for i in range(60):
        x = r.uniform(0, W)
        y = (r.uniform(0, H) - T * r.uniform(20, 60)) % H
        ctx.new_sub_path()
        ctx.arc(x, y, r.uniform(2, 7), 0, 2 * math.pi)
        ctx.set_line_width(2)
        src(ctx, alpha(C['white'], 0.25))
        ctx.stroke()
    for i in range(6):
        rr = random.Random(i * 5)
        sp = rr.uniform(20, 40) * (1 if i % 2 else -1)
        fish(ctx, (rr.uniform(0, 1300) + sp * T) % 1300 - 110, 500 + i * 190, 1.6, alpha(C['white'], 0.12), sp > 0)
    # Sandboden
    ctx.move_to(0, 1560)
    ctx.curve_to(300, 1520, 780, 1600, W, 1540)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    src(ctx, hexc('#2C4A73'))
    ctx.fill()
    for i in range(5):
        seaweed(ctx, 60 + i * 240 + (i % 2) * 60, 1600, 140 + (i % 3) * 50, T, alpha(hexc('#2E8F6A'), 0.7), 5)


def question_scene(ctx, T):
    t0 = g(47.35)
    question_bg(ctx, T)
    k_dots = [pop(T, t0 + 0.9 + i * 0.25) for i in range(3)]
    shelly(ctx, 540, 1540, 3.4, arms={'R': (8, -112)}, expr='think', look=(4, -6), blink=blink_at(T, BL))
    for i, kd in enumerate(k_dots):
        if kd > 0:
            circle(ctx, 680 + i * 60, 820 - i * 55, (14 + i * 7) * kd, alpha(C['white'], 0.9))
    sticker(ctx, 'WARUM MACHT', 520, 330, 74, 'cream', rot=-3, sc=pop(T, t0))
    sticker(ctx, 'SHELLY DAS?', 560, 450, 80, 'yellow', rot=2, sc=pop(T, g(48.05)))
    sticker(ctx, 'TIPP: REGEN', 540, 580, 58, 'blue', rot=-2, sc=pop(T, g(49.52)), icon='rain')
    tc = g(51.93)
    k = pop(T, tc)
    if k > 0:
        ctx.save()
        ctx.translate(820, 1640)
        ctx.scale(k, k)
        fill_rrect(ctx, -60, -40, 120, 80, 22, C['yellow'])
        poly(ctx, [(-20, 36), (10, 36), (-28, 64)], C['yellow'])
        for i in range(3):
            circle(ctx, -28 + i * 28, 0, 8, C['ink'])
        ctx.restore()
    sticker(ctx, "SCHREIB'S IN DIE KOMMENTARE", 540, 1760, 40, 'white', sc=pop(T, tc + 0.15))


# ---------------------------------------------------------------- Endkarte
def end_scene(ctx, T):
    t0 = g(70.64)
    wave = math.sin(T * 9) * 14

    def sh(c):
        shelly(c, 380, -2, 1.5, arms={'R': (34 + wave * 0.3, -140 + wave)}, expr='open', blink=blink_at(T, BL))
    cy = lerp(160, 300, ease(T, t0, END))
    exterior(ctx, cy, 0.82, T, 'eve', sh=sh)
    vignette(ctx, 0.25)
    sticker(ctx, "HÄTTEST DU'S", 540, 300, 78, 'cream', rot=-3, sc=pop(T, t0))
    sticker(ctx, 'GEWUSST?', 540, 420, 90, 'yellow', rot=2, sc=pop(T, g(71.10)))
    sticker(ctx, "SCHREIB'S IN DIE KOMMENTARE", 540, 540, 38, 'white', sc=pop(T, g(71.60)))
    tf = g(72.99)
    tap = tf + 0.75
    if T >= tf:
        if T < tap:
            sticker(ctx, '+ FOLGEN', 540, 650, 54, 'red', sc=pop(T, tf))
        else:
            sticker(ctx, 'GEFOLGT', 540, 650, 54, 'green', sc=lerp(0.9, 1.0, back_out(T, tap, tap + 0.3)), icon='check')
        # Tipp-Kreis
        if tap - 0.25 < T < tap + 0.4:
            k = clamp((T - tap + 0.25) / 0.65)
            ctx.new_sub_path()
            ctx.arc(600, 660, 30 + 60 * k, 0, 2 * math.pi)
            ctx.set_line_width(8)
            src(ctx, alpha(C['white'], 0.8 * (1 - k)))
            ctx.stroke()
            circle(ctx, 600, 660, 26 * (1 - k * 0.5), alpha(C['white'], 0.6 * (1 - k)))
    sticker(ctx, 'MORGEN: NEUES RÄTSEL', 540, 760, 40, 'cream', sc=pop(T, g(73.78)))


# ---------------------------------------------------------------- Hauptzeitleiste
def frame(ctx, T):
    # 1 Intro
    if T < g(2.08):
        sc_intro(ctx, T)
        return
    # 2 Außenansicht
    if T < g(6.26):
        sc_exterior(ctx, T, g(2.08))
        return
    # 3 Morgen: Wohnung -> Aufzug (07:00)
    if T < g(10.95):
        t0 = g(6.26)
        if T < t0 + 3.2:
            sc_morning(ctx, T, label_t=t0)
            chips(ctx, T, clock=('07:00', 7.0, 'sun', t0 + 0.1))
            if T > t0 + 2.6:
                chips(ctx, T, floor=('−20', 1, t0 + 2.6, 0))
        else:
            cam, nf = sc_ride(ctx, T, -20, -17, t0 + 3.2, t0 + 4.8, track=True)
            chips(ctx, T, clock=('07:00', 7.0, 'sun', -1), floor=(flabel(nf), 1, -1, 0))
        return
    # 4 Strand mit Zug (eigentlich das Ziel)
    if T < g(13.86):
        t0 = g(10.95)
        cam = Cam(lerp(940, 1010, ease(T, t0, t0 + 2.8)), -260, 0.95)
        sc_beach(ctx, T, 'day', cam, train_door=ease(T, t0 + 0.3, t0 + 0.8))
        chips(ctx, T, clock=('07:00', 7.0, 'sun', -1))
        sx, sy = cam.scr(1120, -330)
        sticker(ctx, 'ZUG ZUR ARBEIT', sx, sy, 50, 'yellow', rot=-3, sc=pop(T, g(12.57)))
        return
    # 5 Aber... etwas Seltsames: Kabine Nahaufnahme
    if T < g(16.17):
        t0 = g(13.86)
        y = fy(-20)
        cam = Cam(CAB_X, y - 170, lerp(1.5, 1.65, ease(T, t0, g(16.17))))

        def inside():
            shelly(ctx, CAB_X + 6, y - 10, 1.0, expr='smile', blink=blink_at(T, BL), look=(0, -4))
        draw_view(ctx, cam, T, {'cabin_y': y, 'in_cabin': inside})
        sx, sy = cam.scr(CAB_X + 6, y - 245)
        qmark_bubble(ctx, sx + 40, sy - 20, 70, pop(T, g(14.85)))
        chips(ctx, T, clock=('07:00', 7.0, 'sun', -1), floor=('−20', 1, -1, 0))
        return
    # 6 Fahrt nur bis −10
    if T < g(19.33):
        t0 = g(16.17)
        cam, nf = sc_ride(ctx, T, -20, -10, t0 + 0.4, g(18.7), open_at=g(19.0))
        ok = ease(T, g(18.81), g(18.81) + 0.2)
        chips(ctx, T, clock=('07:00', 7.0, 'sun', -1), floor=(flabel(nf), 1, -1, ok))
        return
    # 7 Aussteigen + Treppe (−10 -> −6)
    if T < g(22.93):
        t0 = g(19.33)
        if T < t0 + 1.1:
            cam, nf = sc_ride(ctx, T, -10, -10, 0, 0.1, open_at=t0 - 0.4, exit_left=t0 + 0.1, track=False)
            chips(ctx, T, floor=('−10', 1, -1, 1))
        else:
            cam, f = sc_climb(ctx, T, t0 + 1.1, g(22.9), -10, 4.0)
            chips(ctx, T, floor=(flabel(math.floor(f + 0.25)), 1, -1, 0))
        sticker(ctx, '−10 · AB HIER ZU FUSS', 540, 430, 46, 'cream', rot=-2, sc=pop(T, t0 + 0.6))
        sticker(ctx, '10 ETAGEN', 540, 1500, 64, 'yellow', rot=3, sc=pop(T, g(21.26)))
        return
    # 8 Nachbarn wundern sich (−6 -> −4)
    if T < g(26.47):
        t0 = g(22.93)
        camf = Cam(700, fy(-5) - 60, 0.86)
        wonder = 1.0 if T > g(25.57) else 0.0
        cam, f = sc_climb(ctx, T, t0, g(26.47), -6, 2.0, cam_fixed=camf,
                          who={})
        # Nachbarn zusätzlich zeichnen
        ctx.save()
        camf.apply(ctx)
        karla(ctx, 1150, fy(-5) - 22, 1.15, T, wonder)
        paul(ctx, 1150, fy(-4) - 22, 1.25, T, wonder)
        ctx.restore()
        kx, ky = camf.scr(1150, fy(-5) - 200)
        px, py = camf.scr(1150, fy(-4) - 220)
        sticker(ctx, 'KARLA', kx, ky, 40, 'cream', rot=-3, sc=pop(T, g(24.02)))
        sticker(ctx, 'PAUL', px, py, 40, 'cream', rot=3, sc=pop(T, g(25.11)))
        qmark_bubble(ctx, kx + 120, ky - 40, 40, pop(T, g(25.57)))
        qmark_bubble(ctx, px + 110, py - 40, 40, pop(T, g(25.75)))
        chips(ctx, T, floor=(flabel(math.floor(f + 0.25)), 1, -1, 0))
        return
    # 9 Oben angekommen: Checkliste
    if T < g(30.81):
        t0 = g(26.47)
        cam = Cam(520, -330, 0.86)
        x, ph, dr = path_x(T, [(t0 + 0.2, 155), (t0 + 1.2, 330)])
        cheer = T > t0 + 1.2
        wv = math.sin(T * 8) * 8

        def act(cx):
            shelly(cx, x, 0, 1.15, walk=ph, face=0.8 if ph else 0,
                   arms={'R': (30, -150 + wv), 'L': (-30, -150 - wv)} if cheer else None,
                   expr='open' if cheer else 'smile', blink=blink_at(T, BL))
        sc_beach(ctx, T, 'day', cam, actors=[act], st_open=True)
        check_row(ctx, 110, 260, 'GESUND', 44, pop(T, g(27.20)))
        check_row(ctx, 110, 370, 'SPORTLICH', 44, pop(T, g(27.69)))
        check_row(ctx, 110, 480, 'TREPPEN? KEIN PROBLEM', 44, pop(T, g(29.83)))
        return
    # 10 Abends: Strand -> Aufzug runter bis −20
    if T < g(35.23):
        t0 = g(30.81)
        if T < t0 + 1.9:
            cam = Cam(640, -300, 0.86)
            x, ph, dr = path_x(T, [(t0 + 0.2, 1050), (t0 + 1.4, CAB_X + 6)])
            k_open = 1 - ease(T, t0 + 1.5, t0 + 1.8)

            def inside():
                if x < X_SH1 - 30:
                    shelly(ctx, x, -10, 1.0, walk=ph, mirror=dr < 0, face=-0.8 if ph else 0, blink=blink_at(T, BL))

            def act(cx):
                if x >= X_SH1 - 30:
                    shelly(cx, x, 0, 1.0, walk=ph, mirror=dr < 0, face=-0.8 if ph else 0, blink=blink_at(T, BL))
            draw_view(ctx, cam, T, {'weather': 'eve', 'cabin_y': 0.0, 'cabin_open': k_open, 'in_cabin': inside,
                                    'actors': [act]})
            chips(ctx, T, clock=('18:00', 18.0, 'moon', t0 + 0.05))
        else:
            cam, nf = sc_ride(ctx, T, 0, -20, t0 + 2.0, g(34.2), z=0.9)
            ok = ease(T, g(34.2), g(34.4))
            chips(ctx, T, clock=('18:00', 18.0, 'moon', -1), floor=(flabel(nf), -1, t0 + 1.9, ok))
            sticker(ctx, 'GANZ NORMAL', 540, 1500, 60, 'cream', rot=-2, sc=pop(T, g(33.41)), icon='check')
        return
    # 11 Regen am Strand
    if T < g(37.87):
        t0 = g(35.23)
        cam = Cam(lerp(560, 640, ease(T, t0, g(37.87))), -420, 0.72)
        sc_beach(ctx, T, 'rain', cam)
        vignette(ctx, 0.3)
        chips(ctx, T, clock=('07:00', 7.0, 'rain', t0 + 0.05))
        sticker(ctx, 'REGEN!', 540, 820, 96, 'blue', rot=-4, sc=pop(T, g(35.93)), icon='rain')
        return
    # 12 Mit Regenschirm direkt bis ganz oben
    if T < g(42.32):
        t0 = g(37.87)
        if T < t0 + 2.0:
            sc_morning(ctx, T, umb=True, label_t=t0 - 0.6)
            chips(ctx, T, clock=('07:00', 7.0, 'rain', -1))
            sticker(ctx, 'REGENSCHIRM', 540, 1450, 54, 'yellow', rot=3, sc=pop(T, g(38.59)))
        elif T < g(41.75):
            cam, nf = sc_ride(ctx, T, -20, 0, t0 + 2.1, g(41.66), umb=True, z=0.9)
            ok = ease(T, g(41.66), g(41.66) + 0.2)
            chips(ctx, T, clock=('07:00', 7.0, 'rain', -1), floor=(flabel(nf), 1, t0 + 2.0, ok))
            sticker(ctx, 'DIREKT BIS GANZ OBEN', 540, 1500, 52, 'yellow', rot=-2, sc=pop(T, g(40.73)), icon='check')
        else:
            tt = g(41.75)
            cam = Cam(620, -280, 0.86)
            x, ph, dr = path_x(T, [(tt + 0.1, CAB_X + 6), (tt + 0.55, X_SH1 + 70)])
            ko = ease(T, tt + 0.1, tt + 0.5)

            def act(cx):
                shelly(cx, x, 0, 1.0, walk=ph, face=0.8 if ph else 0, arms={'R': (16, -108)},
                       umb={'ang': math.radians(-90), 'state': 'open', 'k_open': ko, 'len': 120}, blink=blink_at(T, BL))
            draw_view(ctx, cam, T, {'weather': 'rain', 'cabin_y': 0.0, 'cabin_open': 1.0, 'actors': [act]})
            chips(ctx, T, clock=('07:00', 7.0, 'rain', -1), floor=('0', 1, -1, 1))
        return
    # 13 Nächster Tag: Sonne + Regenbogen
    if T < g(44.43):
        t0 = g(42.32)
        cam = Cam(620, lerp(-700, -520, ease(T, t0, g(44.43))), 0.62)
        sc_beach(ctx, T, 'day', cam, rainbow=ease(T, t0 + 0.2, t0 + 1.0))
        chips(ctx, T, clock=('07:00', 7.0, 'sun', t0 + 0.05))
        return
    # 14 Wieder nur bis −10
    if T < g(47.35):
        t0 = g(44.43)
        if T < g(46.95):
            cam, nf = sc_ride(ctx, T, -20, -10, t0 + 0.2, g(46.4), open_at=g(46.6), exit_left=g(46.75))
            ok = ease(T, g(46.49), g(46.49) + 0.2)
            chips(ctx, T, clock=('07:00', 7.0, 'sun', -1), floor=(flabel(nf), 1, t0, ok))
        else:
            cam, nf = sc_ride(ctx, T, -10, -10, 0, 0.1, open_at=0.0, exit_left=g(46.75), track=False)
            chips(ctx, T, clock=('07:00', 7.0, 'sun', -1), floor=('−10', 1, -1, 1))
        sticker(ctx, 'WIEDER NUR BIS −10', 540, 1500, 56, 'yellow', rot=-2, sc=pop(T, g(45.78)))
        return
    # 15 Frage
    if T < g(54.77):
        question_scene(ctx, T)
        return
    # 16 Lösung
    if T < g(70.64):
        solution_scene(ctx, T)
        return
    # 17 Ende
    end_scene(ctx, T)
