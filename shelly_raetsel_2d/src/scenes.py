"""Zeitleiste des Rätselvideos (Endzeit in Sekunden, 30 fps)."""
import math
import random
import cairo
from draw import *
from chars import shelly, karla, paul, person, umbrella, SH_Y
from world import *

# Zeitachse: Szenen sind in der alten Skript-Zeitbasis geschrieben (old_words.json).
# Sie werden per Wortabgleich auf die aktuelle Stimme (vo_words.json) abgebildet, plus eingefügte Pausen.
import json as _json, os as _os, re as _re, difflib as _dl
_A = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'audio')
_NUM = {'20': 'zwanzig', '10': 'zehn', '7': 'sieben'}


def _norm(w):
    w = _re.sub(r"[^\wäöüß']", '', w.lower())
    w = _NUM.get(w, w)
    if w.startswith(('shel', 'schel')):
        w = 'shelly'
    return w


OLD = _json.load(open(f'{_A}/old_words.json'))
NEW = _json.load(open(f'{_A}/vo_words.json'))
_io = next(i for i, w in enumerate(OLD) if w[0] == 'Warum')
_in = next(i for i, w in enumerate(NEW) if w[0] == 'Warum')
_o = [_norm(w[0]) for w in OLD[_io:]]
_n = [_norm(w[0]) for w in NEW[_in:]]
ANCH = [(0.0, 0.0)]
for blk in _dl.SequenceMatcher(None, _o, _n, autojunk=False).get_matching_blocks():
    for k in range(blk.size):
        a_, b_ = OLD[_io + blk.a + k][1], NEW[_in + blk.b + k][1]
        if a_ > ANCH[-1][0] + 0.05 and b_ > ANCH[-1][1] + 0.05:
            ANCH.append((a_, b_))
VO_END = NEW[-1][2] + 0.3
ANCH.append((74.68, VO_END))


def nw(prefix, k=0, end=False):
    """Zeit (Stimme, ohne Pausen) des k-ten Worts, das mit prefix beginnt."""
    hits = [w for w in NEW if _norm(w[0]).startswith(prefix)]
    return hits[k][2 if end else 1]


GAPS = [([w for w in NEW if w[0].endswith('das?')][0][2] + 0.1, 0.9),
        ([w for w in NEW if w[0].startswith('hörst')][0][2] + 0.1, 0.5)]


def gn(tn):
    return tn + sum(d for at, d in GAPS if tn >= at)


def g(t):
    for (a0, b0), (a1, b1) in zip(ANCH, ANCH[1:]):
        if t <= a1:
            return gn(b0 + (b1 - b0) * (t - a0) / (a1 - a0))
    return gn(ANCH[-1][1] + t - ANCH[-1][0])


def TW(prefix, k=0, end=False):
    return gn(nw(prefix, k, end))


T_DANN = gn(nw('dann'))
END = gn(VO_END) + 2.0

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


def y_to_floor(y):
    if y <= fy(-1):
        return -clamp(y / fy(-1))
    return -((y - SEA_Y) / FH)


def ease_sine(t, a, b):
    k = clamp((t - a) / (b - a)) if b > a else 1.0
    return 0.5 - 0.5 * math.cos(math.pi * k)


def flabel(nf, final=None):
    n = int(round(nf))
    return lab(n)


def blink_at(t, times):
    return 1.0 if any(0 <= t - b < 0.12 for b in times) else 0.0


BL = [0.9, 3.7, 6.1, 9.3, 12.2, 15.4, 18.8, 23.1, 27.6, 31.9, 36.0, 40.2, 44.7, 49.6, 53.3, 58.4, 62.9, 67.0, 72.3, 76.4]


def chips(ctx, T, clock=None, floor=None):
    if clock:
        hhmm, hour, kind, t0 = clock
        clock_chip(ctx, 270, 335, hhmm, hour, kind, pop(T, t0))
    if floor:
        label, direction, t0, ok = floor
        floor_chip(ctx, 210, 455, label, direction, pop(T, t0), ok)


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


def exterior(ctx, cy, z, T, weather='day', hl=0.0, sh=None, hut=None, sign=1.0):
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
    # Turm im Querschnitt: Treppenhaus | Aufzug | Wohnungen
    tx0, tx1 = 170, 910
    sx0, sx1 = 330, 470          # Aufzugschacht
    rect(ctx, tx0 - 16, 30, tx1 - tx0 + 32, sea_bottom - 30, C['gold'])
    rect(ctx, tx0, 30, tx1 - tx0, sea_bottom - 30, C['pearl'])
    for n_ in range(-1, -21, -1):
        yr = ext_row_y(n_)
        ytop = yr - EXT_ROW_H + 10
        # Treppenhaus
        rect(ctx, tx0 + 8, ytop, sx0 - tx0 - 16, EXT_ROW_H - 10, hexc('#EDE7DD'))
        if n_ % 2:
            line(ctx, tx0 + 18, yr - 4, sx0 - 18, ytop + 6, 7, C['white'])
        else:
            line(ctx, sx0 - 18, yr - 4, tx0 + 18, ytop + 6, 7, C['white'])
        # Schacht
        rect(ctx, sx0, ytop - 10, sx1 - sx0, EXT_ROW_H, hexc('#C9D6E3'))
        # Wohnung
        rect(ctx, sx1 + 10, ytop, tx1 - sx1 - 18, EXT_ROW_H - 10, hexc('#F6DDBA'))
        fill_rrect(ctx, sx1 + 30, yr - 82, 44, 76, 8, C['pink2'] if n_ == -20 else C['coral'])
        for i in range(2):
            wx = sx1 + 110 + i * 160
            fill_rrect(ctx, wx - 6, ytop + 10, 146, EXT_ROW_H - 34, 16, C['gold'])
            fill_rrect(ctx, wx, ytop + 16, 134, EXT_ROW_H - 46, 12, mixc(C['sea1'], C['sea3'], (-n_) / 20))
        rect(ctx, tx0, yr - 4, tx1 - tx0, 10, C['pearl3'])
        if n_ == -20 and hl > 0:
            rrect(ctx, tx0 - 24, ytop - 14, tx1 - tx0 + 48, EXT_ROW_H + 10, 18)
            ctx.set_line_width(12)
            src(ctx, alpha(C['yellow'], hl))
            ctx.stroke()
    for x_ in (sx0 + 22, sx1 - 22):
        line(ctx, x_, 20, x_, sea_bottom - 20, 4, hexc('#A9B8C9'), cap=cairo.LINE_CAP_BUTT)
    # Kabine fährt auf und ab
    cab_n = -1 - 19 * (0.5 - 0.5 * math.cos(T * 0.9))
    cy_ = EXT_TOP + (-cab_n) * EXT_ROW_H
    fill_rrect(ctx, sx0 + 14, cy_ - 98, sx1 - sx0 - 28, 92, 8, C['gold'])
    rect(ctx, sx0 + 22, cy_ - 90, sx1 - sx0 - 44, 78, hexc('#FDF6EC'))
    # Name am Gebäude
    sticker(ctx, 'SUNKEN PEARL', (tx0 + tx1) / 2, 130, 58, 'navy', sc=sign, world=True)
    # Etagenschilder links
    for n_ in (-1, -10, -20):
        plate(ctx, tx0 - 75, ext_row_y(n_) - EXT_ROW_H / 2, lab(n_), size=32)
    # Insel mit Kuppel und Palmen
    ctx.move_to(60, 40)
    ctx.curve_to(200, -40, 880, -40, 1020, 40)
    ctx.close_path()
    src(ctx, C['sand'])
    ctx.fill()
    palm(ctx, 170, 8, 320, T, -0.1, dark * 0.5)
    palm(ctx, 930, 8, 360, T, 0.1, dark * 0.5)
    ctx.save()
    ctx.translate(400, 10)
    ctx.scale(1, 1.6)
    ctx.new_sub_path()
    ctx.arc(0, 0, 130, math.pi, 2 * math.pi)
    ctx.close_path()
    ctx.restore()
    src(ctx, alpha(hexc('#DFF4FF'), 0.7))
    ctx.fill_preserve()
    ctx.set_line_width(8)
    src(ctx, C['gold'])
    ctx.stroke()
    circle(ctx, 400, -205, 12, C['white'])
    plate(ctx, 400 - 220, -10, '0', size=32)
    if hut:
        hut(ctx)
    if sh:
        sh(ctx)
    ctx.restore()
    return cam


# ---------------------------------------------------------------- Szenen
def sc_intro(ctx, T, t0=0.0):
    """Shelly in ihrer Wohnung auf −20."""
    y = fy(-20)
    z = lerp(1.25, 1.36, ease(T, t0, t0 + 2.1))
    cam = Cam(1060, y - 330, z)
    wave = math.sin(T * 9) * 14

    def act(c):
        shelly(c, 1160, y - 2, 1.0, arms={'R': (34 + wave * 0.3, -140 + wave)}, expr='open' if T > 0.3 else 'smile',
               blink=blink_at(T, BL))
    draw_view(ctx, cam, T, {'actors': [act], 'cabin_y': fy(-20)})
    sx, sy = cam.scr(1160, y - 245)
    sticker(ctx, 'SHELLY', sx, sy, 52, 'cream', rot=-4, sc=pop(T, t0 + 0.2))


INTRO_TXT = ['SHELLY', 'WOHNT', 'IM', '20.', 'UNTERGESCHOSS', 'EINES', 'HOCHHAUSES', 'UNTER', 'WASSER,', 'DEM',
             'SUNKEN', 'PEARL.']


def karaoke(ctx, T, toks, times, cx, cy, size, maxw, appear=0.0):
    """Ganzer Satz sofort lesbar; das gerade gesprochene Wort leuchtet gelb auf."""
    if not UI_ON[0]:
        return
    gap = size * 0.42
    padx, pady = size * 0.22, size * 0.16
    ws = [text_size(ctx, t, size)[0] for t in toks]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(ws):
        bw = w + 2 * padx
        if cur and cw + gap + bw > maxw:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (gap if cur else 0) + bw
        cur.append(i)
    lines.append((cur, cw))
    lh = size * 0.72 + 2 * pady + size * 0.22
    total_h = len(lines) * lh
    k = 1.0
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(k, k)
    pw = max(l[1] for l in lines) + size * 0.7
    ph = total_h + size * 0.45
    fill_rrect(ctx, -pw / 2 + 6, -ph / 2 + 10, pw, ph, size * 0.4, alpha(C['shadow'], 0.3))
    fill_rrect(ctx, -pw / 2, -ph / 2, pw, ph, size * 0.4, alpha(C['navy'], 0.92))
    y = -total_h / 2 + lh / 2
    for idxs, lw in lines:
        x = -lw / 2
        for i in idxs:
            bw = ws[i] + 2 * padx
            t0 = times[i][0]
            t1 = times[i + 1][0] if i + 1 < len(times) else times[i][1] + 0.4
            on = clamp((T - t0) / 0.06) * (1 - clamp((T - t1) / 0.12))
            done = T >= t1
            sc_ = 1 + 0.08 * on
            ctx.save()
            ctx.translate(x + bw / 2, y)
            ctx.scale(sc_, sc_)
            if on > 0.01:
                fill_rrect(ctx, -bw / 2, -(size * 0.72 + 2 * pady) / 2, bw, size * 0.72 + 2 * pady, size * 0.2,
                           alpha(C['yellow'], on))
            fg = mixc(C['white'], C['ink'], on)
            if not done and on < 0.01 and T < t0:
                fg = alpha(C['white'], 0.92)
            text(ctx, toks[i], 0, 0, size, fg)
            ctx.restore()
            x += bw + gap
        y += lh
    ctx.restore()


def sc_overview(ctx, T):
    """Explosiver Einstieg: Blitz, Zoom-Punch, Wackeln, RÄTSEL-Stempel, ganzer Satz mit Wort-Highlight."""
    t_end = TW('jeden')
    punch = back_out(T, 0.0, 0.55, 1.4)
    z = lerp(1.6, 0.56, punch) + 0.02 * ease(T, 0.6, t_end)
    shake = max(0.0, 1 - T / 0.45)
    ox = math.sin(T * 90) * 18 * shake
    oy = math.cos(T * 77) * 14 * shake
    t20 = TW('zwanzig')
    ctx.save()
    ctx.translate(ox, oy)
    exterior(ctx, lerp(2300, 1200, punch), z, T, 'day', hl=ease(T, t20, t20 + 0.2),
             sign=max(1.0, 1 + 0.35 * math.sin(math.pi * clamp((T - TW('sunken')) / 0.5))))
    ctx.restore()
    vignette(ctx, 0.3)
    # Blitz (unter den Texten, damit der Satz sofort lesbar ist)
    if T < 0.25:
        rect(ctx, 0, 0, W, H, alpha(C['white'], 0.8 * (1 - T / 0.25)))
    # Strahlen-Burst hinter dem Stempel
    kb = clamp(T / 0.5)
    if kb < 1:
        ctx.save()
        ctx.translate(510, 560)
        for i in range(16):
            a_ = i / 16 * 2 * math.pi + T
            r0, r1 = 120 + 500 * kb, 220 + 900 * kb
            line(ctx, math.cos(a_) * r0, math.sin(a_) * r0, math.cos(a_) * r1, math.sin(a_) * r1, 16 * (1 - kb),
                 alpha(C['yellow'], 0.9 * (1 - kb)))
        ctx.restore()
    rot = -4 + 2 * math.sin(T * 3)
    sticker(ctx, 'RÄTSEL', 510, 560, 120, 'yellow', rot=rot, sc=lerp(2.2, 1.0, back_out(T, 0.0, 0.4, 2.5)) if T < 0.4 else 1.0 + 0.04 * math.sin(T * 6))
    times = [(w[1] + 0.0, w[2]) for w in NEW[:len(INTRO_TXT)]]
    times = [(gn(a), gn(b)) for a, b in times]
    karaoke(ctx, T, INTRO_TXT, times, 510, 1120, 60, 800, appear=0.0)


def sc_exterior(ctx, T, t0):
    k = ease(T, t0, T_MINUS)
    z = lerp(0.575, 1.05, k)
    cy = lerp(1200, ext_row_y(-20) - 360, k)
    cam = exterior(ctx, cy, z, T, 'day', hl=ease(T, T_MINUS, T_MINUS + 0.2))
    sticker(ctx, 'ETAGE −20', 540, 1500, 84, 'yellow', rot=-3, sc=pop(T, T_MINUS))


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
        shelly(cx, x, y - 2 if x > X_SH1 - 20 else y - 10, 1.0, face=0.8 if dr else 0, walk=ph, mirror=dr < 0,
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
    k = ease_sine(T, t0, t1)
    cy = lerp(cab_y_of(n0), cab_y_of(n1), k)
    nf = y_to_floor(cy)
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
               arms={'R': (24, -58)} if umb else None, umb=u, blink=blink_at(T, BL), face=0.8 if mirror else 0)

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
        shelly(cx, x, y, 1.0, walk=T * 14, mirror=dr < 0, face=0.8, expr=expr, blink=blink_at(T, BL))
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
                     look=look, blink=blink_at(T, BL), face=0.4, arm_len=ARM)
        ctx.pop_group_to_source()
        ctx.paint()
    else:
        shelly(ctx, SOL_X, SOL_FEET, SOL_S, mirror=True, arms=arms, umb=umb, tiptoe=tiptoe, expr=expr, look=look,
               blink=blink_at(T, BL), face=0.4, arm_len=ARM)
    # Regen-Andeutung hinter dem Glas (nur Stimmung)
    # Sticker
    top_y = 340
    if tA <= T < t_klein:
        sticker(ctx, 'DIE LÖSUNG', 540, top_y, 70, 'cream', rot=-3, sc=pop(T, tA))
    elif t_klein <= T < t_down:
        sticker(ctx, 'SHELLY IST KLEINWÜCHSIG', 540, top_y, 60, 'yellow', rot=-2, sc=pop(T, t_klein))
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
    shelly(ctx, 510, 1330, 3.0, arms={'R': (8, -112)}, expr='think', look=(4, -6), blink=blink_at(T, BL))
    for i, kd in enumerate(k_dots):
        if kd > 0:
            circle(ctx, 640 + i * 55, 760 - i * 50, (14 + i * 7) * kd, alpha(C['white'], 0.9))
    sticker(ctx, 'WARUM MACHT', 490, 350, 74, 'cream', rot=-3, sc=pop(T, t0))
    sticker(ctx, 'SHELLY DAS?', 530, 470, 80, 'yellow', rot=2, sc=pop(T, g(48.05)))
    sticker(ctx, 'TIPP: REGEN', 510, 595, 58, 'blue', rot=-2, sc=pop(T, g(49.52)), icon='rain')
    tc = g(51.93)
    k = pop(T, tc)
    if k > 0:
        ctx.save()
        ctx.translate(800, 1300)
        ctx.scale(k, k)
        fill_rrect(ctx, -60, -40, 120, 80, 22, C['yellow'])
        poly(ctx, [(-20, 36), (10, 36), (-28, 64)], C['yellow'])
        for i in range(3):
            circle(ctx, -28 + i * 28, 0, 8, C['ink'])
        ctx.restore()
    sticker(ctx, "SCHREIB'S IN DIE KOMMENTARE", 510, 1430, 40, 'white', sc=pop(T, tc + 0.15))


# ---------------------------------------------------------------- Endkarte
def beach_hut(ctx, x, y, k):
    """Strandhütte mit Namensschild (k = Einblend-Skalierung)."""
    if k <= 0.001:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    ellipse(ctx, 0, 0, 120, 12, alpha(C['shadow'], 0.2))
    rect(ctx, -95, -150, 190, 150, hexc('#E9B77A'))
    for i in range(6):
        line(ctx, -95, -128 + i * 24, 95, -128 + i * 24, 3, alpha(hexc('#B8864E'), 0.7))
    poly(ctx, [(-125, -140), (0, -235), (125, -140)], C['pink2'])
    poly(ctx, [(-105, -146), (0, -222), (105, -146)], C['pink'])
    fill_rrect(ctx, -30, -100, 60, 100, 10, hexc('#7FC8C2'))
    shell_deco(ctx, 0, -180, 1.4, C['white'])
    fill_rrect(ctx, -90, -300, 180, 56, 10, C['cream'])
    rrect(ctx, -90, -300, 180, 56, 10)
    ctx.set_line_width(4)
    src(ctx, C['gold2'])
    ctx.stroke()
    text(ctx, 'DEIN NAME', 0, -272, 30, C['ink'])
    line(ctx, 0, -244, 0, -235, 6, C['gold2'])
    ctx.restore()


def end_scene(ctx, T):
    t0 = g(70.64)
    t_du = TW('willst') - 0.15
    t_folg = T_DANN
    wave = math.sin(T * 9) * 14
    khut = back_out(T, t_du + 0.9, t_du + 1.3) if T > t_du + 0.9 else 0.0

    def sh(c):
        shelly(c, 560, -2, 1.5, arms={'R': (34 + wave * 0.3, -140 + wave)}, expr='open', blink=blink_at(T, BL))

    def hut(c):
        beach_hut(c, 880, 10, khut)
    cy = lerp(40, 100, ease(T, t0, END))
    exterior(ctx, cy, 0.82, T, 'eve', sh=sh, hut=hut)
    vignette(ctx, 0.25)
    if T < t_du:
        sticker(ctx, "HÄTTEST DU'S", 510, 340, 78, 'cream', rot=-3, sc=pop(T, t0))
        sticker(ctx, 'GEWUSST?', 510, 460, 90, 'yellow', rot=2, sc=pop(T, g(71.10)))
        sticker(ctx, "SCHREIB'S IN DIE KOMMENTARE", 510, 575, 40, 'white', sc=pop(T, g(71.60)))
    else:
        sticker(ctx, 'DU WILLST MITSPIELEN?', 510, 335, 66, 'cream', rot=-2, sc=pop(T, t_du))
        sticker(ctx, 'DEINE EIGENE HÜTTE', 510, 445, 62, 'yellow', rot=2, sc=pop(T, t_du + 0.6))
        sticker(ctx, 'MIT DEINEM NAMEN!', 510, 545, 56, 'yellow', rot=-1, sc=pop(T, t_du + 0.9))
        tap = t_folg + 0.7
        if T >= t_folg:
            if T < tap:
                sticker(ctx, '+ FOLGEN', 400, 660, 58, 'red', sc=pop(T, t_folg))
            else:
                sticker(ctx, 'GEFOLGT', 400, 660, 58, 'green', sc=lerp(0.9, 1.0, back_out(T, tap, tap + 0.3)), icon='check')
            if tap - 0.25 < T < tap + 0.4:
                k = clamp((T - tap + 0.25) / 0.65)
                ctx.new_sub_path()
                ctx.arc(460, 670, 30 + 60 * k, 0, 2 * math.pi)
                ctx.set_line_width(8)
                src(ctx, alpha(C['white'], 0.8 * (1 - k)))
                ctx.stroke()
                circle(ctx, 460, 670, 26 * (1 - k * 0.5), alpha(C['white'], 0.6 * (1 - k)))


# ---------------------------------------------------------------- Hauptzeitleiste
def frame(ctx, T):
    # 1 Gesamtansicht
    if T < TW('jeden'):
        sc_overview(ctx, T)
        return
    # 2 Abends: mit dem Boot zurück, Aufzug runter, in die Wohnung (ganz normal)
    t_eve = TW('jeden')
    t_ride = TW('boot') + 0.2
    t_home = TW('geht') + 0.1
    t_aber = TW('aber')
    if T < t_ride:
        t0 = t_eve
        cam = Cam(700, -300, 0.86)
        x, ph, dr = path_x(T, [(t0 + 0.2, 930), (t_ride - 0.7, CAB_X + 6)])
        k_open = 1 - ease(T, t_ride - 0.6, t_ride - 0.3)

        def inside():
            if x < X_SH1 - 30:
                shelly(ctx, x, -10, 1.0, walk=ph, mirror=dr < 0, face=0.8 if ph else 0, blink=blink_at(T, BL))

        def act(cx):
            if x >= X_SH1 - 30:
                shelly(cx, x, 0, 1.0, walk=ph, mirror=dr < 0, face=0.8 if ph else 0, blink=blink_at(T, BL))
        draw_view(ctx, cam, T, {'weather': 'eve', 'cabin_y': 0.0, 'cabin_open': k_open, 'in_cabin': inside,
                                'actors': [act], 'train_x': 1000})
        chips(ctx, T, clock=('18:00', 18.0, 'moon', t0 + 0.05))
        sx, sy = cam.scr(x, -260)
        sticker(ctx, 'SHELLY', sx, sy, 48, 'cream', rot=-3, sc=pop(T, t0 + 0.4))
        return
    if T < t_home:
        cam, nf = sc_ride(ctx, T, 0, -20, t_ride + 0.1, t_home - 0.25, z=0.9, open_at=t_home - 0.15)
        ok = ease(T, t_home - 0.25, t_home - 0.05)
        chips(ctx, T, clock=('18:00', 18.0, 'moon', -1), floor=(flabel(nf), -1, t_ride, ok))
        return
    if T < t_aber:
        sc_home(ctx, T, t_home)
        chips(ctx, T, clock=('18:00', 18.0, 'moon', -1), floor=('−20', -1, -1, 1))
        sticker(ctx, 'GANZ NORMAL', 510, 1400, 64, 'cream', rot=-2, sc=pop(T, TW('ganz')), icon='check')
        return
    # 3 Morgens: etwas Seltsames
    t_ride2 = TW('shelly', 1)
    if T < t_ride2:
        cam = sc_morning(ctx, T, label_t=t_aber - 0.1)
        chips(ctx, T, clock=('07:00', 7.0, 'sun', TW('morgen')))
        sx, sy = cam.scr(CAB_X + 6, fy(-20) - 250)
        qmark_bubble(ctx, sx + 40, sy - 10, 60, pop(T, TW('seltsam')))
        return
    t_dort = TW('dort')
    if T < t_dort:
        t10 = TW('zehnte')
        cam, nf = sc_ride(ctx, T, -20, -10, t_ride2 + 0.3, t10, open_at=t_dort - 0.5)
        ok = ease(T, t10, t10 + 0.2)
        chips(ctx, T, clock=('07:00', 7.0, 'sun', -1), floor=(flabel(nf), 1, -1, ok))
        return
    t_ihre = TW('nachbar') - 0.2
    if T < t_ihre:
        t0 = t_dort
        if T < t0 + 1.0:
            cam, nf = sc_ride(ctx, T, -10, -10, 0, 0.1, open_at=t0 - 0.6, exit_left=t0 + 0.05, track=False)
            chips(ctx, T, floor=('−10', 1, -1, 1))
        else:
            cam, f = sc_climb(ctx, T, t0 + 1.0, t_ihre, -10, 4.0)
            chips(ctx, T, floor=(flabel(math.floor(f + 0.25)), 1, -1, 0))
        sticker(ctx, 'AB −10 ZU FUSS', 560, 580, 50, 'cream', rot=-2, sc=pop(T, t0 + 0.4))
        sticker(ctx, '10 STOCKWERKE', 510, 1400, 64, 'yellow', rot=3, sc=pop(T, TW('letzten')))
        return
    t_denn = TW('denn')
    if T < t_denn:
        t0 = t_ihre
        camf = Cam(700, fy(-5) - 60, 0.86)
        wonder = 1.0 if T > TW('wundern') else 0.0
        cam, f = sc_climb(ctx, T, t0, t_denn, -6, 2.0, cam_fixed=camf, who={})
        ctx.save()
        camf.apply(ctx)
        person(ctx, 'sophia', 1150, fy(-5) - 22, 1.5, wonder, T, blink=blink_at(T, BL), mirror=True)
        person(ctx, 'laura', 1150, fy(-4) - 22, 1.5, wonder, T, blink=blink_at(T - 0.4, BL), mirror=True)
        ctx.restore()
        kx, ky = camf.scr(1150, fy(-5) - 330)
        px, py = camf.scr(1150, fy(-4) - 330)
        sticker(ctx, 'SOPHIA', kx, ky, 40, 'cream', rot=-3, sc=pop(T, TW('soph')))
        sticker(ctx, 'LAURA', px, py, 40, 'cream', rot=3, sc=pop(T, TW('laura')))
        qmark_bubble(ctx, kx + 120, ky - 40, 40, pop(T, TW('wundern')))
        qmark_bubble(ctx, px + 110, py - 40, 40, pop(T, TW('wundern') + 0.18))
        chips(ctx, T, floor=(flabel(math.floor(f + 0.25)), 1, -1, 0))
        return
    t_eines = TW('eines')
    if T < t_eines:
        t0 = t_denn
        cam = Cam(520, -330, 0.86)
        x, ph, dr = path_x(T, [(t0 + 0.2, 155), (t0 + 1.2, 330)])
        cheer = T > t0 + 1.2
        wv = math.sin(T * 8) * 8

        def act(cx):
            shelly(cx, x, 0, 1.15, walk=ph, face=0.8 if ph else 0,
                   arms={'R': (30, -150 + wv), 'L': (-30, -150 - wv)} if cheer else None,
                   expr='open' if cheer else 'smile', blink=blink_at(T, BL))
        sc_beach(ctx, T, 'day', cam, actors=[act], st_open=True)
        check_row(ctx, 110, 330, 'GESUND', 44, pop(T, TW('gesund')))
        check_row(ctx, 110, 440, 'SPORTLICH', 44, pop(T, TW('sportlich')))
        check_row(ctx, 110, 550, 'TREPPENSTEIGEN? KEIN PROBLEM', 40, pop(T, TW('probleme')))
        return
    # 4 Regen
    t_rain2 = TW('shelly', 3)
    if T < t_rain2:
        t0 = t_eines
        cam = Cam(lerp(560, 640, ease(T, t0, t_rain2)), -420, 0.72)
        sc_beach(ctx, T, 'rain', cam)
        vignette(ctx, 0.3)
        chips(ctx, T, clock=('07:00', 7.0, 'rain', t0 + 0.05))
        sticker(ctx, 'REGEN!', 510, 620, 96, 'blue', rot=-4, sc=pop(T, TW('regnet')), icon='rain')
        return
    t_am = TW('am', 0) if any(_norm(w[0]) == 'am' for w in NEW) else TW('nächsten') - 0.2
    t_top = TW('oben', 0) + 0.1
    if T < t_am:
        t0 = t_rain2
        if T < t0 + 0.9:
            sc_morning(ctx, T, umb=True, label_t=t0 - 1.7)
            chips(ctx, T, clock=('07:00', 7.0, 'rain', -1))
            sticker(ctx, 'REGENSCHIRM', 510, 1400, 54, 'yellow', rot=3, sc=pop(T, t0 + 0.1))
        elif T < t_top + 0.1:
            cam, nf = sc_ride(ctx, T, -20, 0, t0 + 0.95, t_top, umb=True, z=0.9)
            ok = ease(T, t_top, t_top + 0.2)
            chips(ctx, T, clock=('07:00', 7.0, 'rain', -1), floor=(flabel(nf), 1, t0 + 0.9, ok))
            sticker(ctx, 'DIREKT BIS GANZ OBEN', 510, 1400, 52, 'yellow', rot=-2, sc=pop(T, TW('direkt')), icon='check')
        else:
            tt = t_top + 0.1
            cam = Cam(620, -280, 0.86)
            x, ph, dr = path_x(T, [(tt + 0.1, CAB_X + 6), (tt + 0.55, X_SH1 + 70)])
            ko = ease(T, tt + 0.1, tt + 0.5)

            def act(cx):
                shelly(cx, x, 0, 1.0, walk=ph, face=0.8 if ph else 0, arms={'R': (16, -108)},
                       umb={'ang': math.radians(-90), 'state': 'open', 'k_open': ko, 'len': 120}, blink=blink_at(T, BL))
            draw_view(ctx, cam, T, {'weather': 'rain', 'cabin_y': 0.0, 'cabin_open': 1.0, 'actors': [act]})
            chips(ctx, T, clock=('07:00', 7.0, 'rain', -1), floor=('0', 1, -1, 1))
        return
    # 5 Nächster Tag: Sonne
    t_und = gn(next(w[1] for w in NEW if _norm(w[0]) == 'und' and w[1] > nw('sonne')))
    if T < t_und:
        t0 = t_am
        cam = Cam(620, lerp(-700, -520, ease(T, t0, t_und)), 0.62)
        sc_beach(ctx, T, 'day', cam, rainbow=ease(T, t0 + 0.2, t0 + 1.0))
        chips(ctx, T, clock=('07:00', 7.0, 'sun', t0 + 0.05))
        return
    t_warum = TW('warum')
    if T < t_warum:
        t0 = t_und
        t10 = TW('zehnten')
        t_ex = t10 + 0.5
        if T < t_ex + 0.2:
            cam, nf = sc_ride(ctx, T, -20, -10, t0 + 0.2, t10, open_at=t10 + 0.15, exit_left=t_ex)
            ok = ease(T, t10, t10 + 0.2)
            chips(ctx, T, clock=('07:00', 7.0, 'sun', -1), floor=(flabel(nf), 1, t0, ok))
        else:
            cam, nf = sc_ride(ctx, T, -10, -10, 0, 0.1, open_at=0.0, exit_left=t_ex, track=False)
            chips(ctx, T, clock=('07:00', 7.0, 'sun', -1), floor=('−10', 1, -1, 1))
        sticker(ctx, 'WIEDER NUR BIS −10', 510, 1400, 56, 'yellow', rot=-2, sc=pop(T, t10))
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
