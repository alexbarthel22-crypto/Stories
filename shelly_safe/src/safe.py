"""Shelly und der Schuh im Safe – Rätsel im Retro-Stil (Hotel Sandkorn, Muschelpass)."""
import json, math, os, random, re
import cairo
from draw import *
from chars import shelly
import retro
from retro import P, SLAB, TYPE, ZILLA, figure, Cam, hotel_facade, GROUND


def paper_card(ctx, *a, **k):
    ctx.save()
    ctx.identity_matrix()
    retro.paper_card(ctx, *a, **k)
    ctx.restore()


def calendar(ctx, *a, **k):
    ctx.save()
    ctx.identity_matrix()
    retro.calendar(ctx, *a, **k)
    ctx.restore()

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = json.load(open(f'{ROOT}/audio/vo_words.json'))


def _norm(w):
    return re.sub(r"[^\wäöüß']", '', w.lower()).replace('ß', 'ss')


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


# ---------------------------------------------------------------- Shelly-Varianten
UNIFORM = dict(pink=hexc('#24315F'), pink2=hexc('#182246'))


def shelly_x(ctx, T, x, y, s, uniform=False, **kw):
    if uniform:
        old = {k: C[k] for k in UNIFORM}
        C.update(UNIFORM)
    try:
        out = shelly(ctx, x, y, s, blink=blink(T), **kw)
    finally:
        if uniform:
            C.update(old)
    if uniform:
        # rotes Halstuch + Käppi
        m = -1 if kw.get('mirror') else 1
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(s * m, s)
        poly(ctx, [(-10, -97), (10, -97), (4, -84), (-4, -84)], P['red'])
        poly(ctx, [(2, -90), (12, -76), (6, -74)], P['red'])
        fill_rrect(ctx, -22, -176, 40, 14, 4, hexc('#24315F'))
        rect(ctx, -22, -166, 44, 5, hexc('#182246'))
        rect(ctx, -22, -172, 40, 3, P['gold'])
        circle(ctx, -2, -170, 3, P['gold'])
        for i in range(3):
            circle(ctx, 0, -70 + i * 10, 1.8, P['gold'])
        ctx.restore()
    return out


def shoe(ctx, x, y, s=1.0, ang=0.0, col=None):
    """Pinker Pumps, Sohle unten bei y."""
    col = col or C['pink2']
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ellipse(ctx, 0, 2, 34, 5, alpha(C['shadow'], 0.2))
    ctx.move_to(-30, 0)
    ctx.curve_to(-30, -18, -10, -20, 0, -14)
    ctx.curve_to(10, -10, 24, -10, 30, -2)
    ctx.line_to(30, 0)
    ctx.close_path()
    src(ctx, col)
    ctx.fill()
    rect(ctx, -30, -2, 8, 2, C['ink'])
    poly(ctx, [(-30, 0), (-24, 0), (-26, 12), (-29, 12)], C['ink'])
    ellipse(ctx, -14, -12, 8, 3, alpha(C['white'], 0.35))
    ctx.restore()


def muschelpass(ctx, x, y, s=1.0, ang=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    fill_rrect(ctx, -32, -44, 64, 88, 6, hexc('#1E3F7A'))
    rect(ctx, -32, -44, 8, 88, hexc('#16305E'))
    sh = 0
    ctx.move_to(0, 4)
    for i in range(7):
        a = math.radians(200 + i * 140 / 6)
        ctx.line_to(math.cos(a) * 18, math.sin(a) * 18 + 4)
    ctx.close_path()
    src(ctx, P['gold2'])
    ctx.fill()
    text(ctx, 'MUSCHEL', 4, 22, 9, P['gold2'], font=SLAB)
    text(ctx, 'PASS', 4, 33, 9, P['gold2'], font=SLAB)
    ctx.restore()


def papers(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for i in range(3):
        fill_rrect(ctx, -30 + i * 6, -40 - i * 4, 60, 80, 3, mixc(C['white'], P['cream2'], 0.2 * i))
        for j in range(5):
            line(ctx, -22 + i * 6, -28 - i * 4 + j * 11, 18 + i * 6, -28 - i * 4 + j * 11, 2, alpha(P['ink'], 0.3))
    circle(ctx, 18 + 12, 26 - 8, 9, P['red'])
    ctx.restore()


FRIEND = dict(hair=hexc('#C2562E'), hair2=hexc('#9A3F1F'), pink=hexc('#7D8B5A'), pink2=hexc('#5E6B40'),
              skin=hexc('#F7D2B5'), skin2=hexc('#E8B595'))


def friend(ctx, T, x, y, s):
    old = {k: C[k] for k in FRIEND}
    C.update(FRIEND)
    try:
        shelly(ctx, x, y, s, shell=False, long_hair=True, expr='o' if T > nw('seltsam') else 'smile',
               blink=blink(T, 0.4), arms={'R': (14, -116)} if T > nw('seltsam') else None)
    finally:
        C.update(old)


# ---------------------------------------------------------------- Zimmer (Seitenansicht)
def room(ctx, T, tod='eve', home=False):
    """Hotelzimmer: Tapete, Fenster mit Vorhängen, Lampe, Bild, Bett, Schreibtisch mit Safe-Platz."""
    wall = P['teal'] if not home else hexc('#F2C6CF')
    wall2 = P['teal2'] if not home else hexc('#E8B0BD')
    rect(ctx, 0, 0, W, 260, P['wood3'] if not home else hexc('#F7EFE8'))
    rect(ctx, 0, 250, W, 14, P['cream'])
    rect(ctx, 0, 264, W, 1000, wall)
    for i in range(0, W, 34):
        line(ctx, i, 264, i, 1250, 3, wall2)
    rect(ctx, 0, 1250, W, 200, P['wood'] if not home else hexc('#FFFFFF'))
    rect(ctx, 0, 1246, W, 12, P['wood2'] if not home else hexc('#E8B0BD'))
    # Boden
    rect(ctx, 0, 1450, W, H - 1450, hexc('#E3D3B0') if not home else hexc('#D9B27A'))
    for yy in range(1470, H, 60):
        for xx in range(-30 + (yy // 60 % 2) * 40, W, 80):
            poly(ctx, [(xx, yy - 8), (xx + 8, yy), (xx, yy + 8), (xx - 8, yy)], alpha(hexc('#C9B48A'), 0.6))
    # Fenster
    wx0, wy0, ww, wh = 60, 420, 420, 600
    fill_rrect(ctx, wx0 - 16, wy0 - 16, ww + 32, wh + 32, 6, P['cream'])
    sky = {'eve': [(0, hexc('#3B3A7A')), (0.6, hexc('#C97BA0')), (1, hexc('#F2A97A'))],
           'night': [(0, hexc('#0E1438')), (1, hexc('#2B3170'))],
           'morning': [(0, hexc('#8FC8F0')), (0.7, hexc('#F7E3B0')), (1, hexc('#FFD27A'))]}[tod]
    g = cairo.LinearGradient(0, wy0, 0, wy0 + wh)
    for o, c in sky:
        g.add_color_stop_rgba(o, *c)
    ctx.rectangle(wx0, wy0, ww, wh)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.rectangle(wx0, wy0, ww, wh)
    ctx.clip()
    if tod == 'night':
        r = random.Random(3)
        for i in range(30):
            circle(ctx, r.uniform(wx0, wx0 + ww), r.uniform(wy0, wy0 + 300), r.uniform(1.5, 3), alpha(C['white'], 0.7))
        circle(ctx, wx0 + 300, wy0 + 120, 40, hexc('#FFF2C2'))
    elif tod == 'morning':
        circle(ctx, wx0 + 280, wy0 + 360, 60, hexc('#FFF2B0'))
    else:
        circle(ctx, wx0 + 280, wy0 + 420, 70, hexc('#FFB45A'))
    if home:
        rect(ctx, wx0, wy0 + 420, ww, 180, hexc('#7DBA86'))
        for i in range(10):
            line(ctx, wx0 + i * 44, wy0 + 440, wx0 + i * 44, wy0 + 520, 6, C['white'])
        line(ctx, wx0, wy0 + 460, wx0 + ww, wy0 + 460, 6, C['white'])
    else:
        seac = {'eve': hexc('#5B5A9A'), 'night': hexc('#1C2A5C'), 'morning': hexc('#5AB7D9')}[tod]
        rect(ctx, wx0, wy0 + 440, ww, 160, seac)
        for i in range(6):
            line(ctx, wx0 + 20 + i * 70 + math.sin(T + i) * 6, wy0 + 470 + (i % 3) * 30, wx0 + 60 + i * 70, wy0 + 470 + (i % 3) * 30, 3, alpha(C['white'], 0.4))
        # Palme
        line(ctx, wx0 + 90, wy0 + 600, wx0 + 110, wy0 + 380, 10, hexc('#5A3824'))
        for a in range(6):
            aa = math.radians(-170 + a * 32)
            line(ctx, wx0 + 110, wy0 + 380, wx0 + 110 + math.cos(aa) * 90, wy0 + 380 + math.sin(aa) * 40 + 30, 8, hexc('#2F6E4A'))
    ctx.restore()
    line(ctx, wx0 + ww / 2, wy0, wx0 + ww / 2, wy0 + wh, 8, P['cream'])
    line(ctx, wx0, wy0 + wh * 0.45, wx0 + ww, wy0 + wh * 0.45, 8, P['cream'])
    # Vorhänge (gold)
    cur = hexc('#D9A441') if not home else hexc('#9ED6B0')
    for side in (0, 1):
        cx = wx0 - 30 if side == 0 else wx0 + ww + 30
        d = 1 if side == 0 else -1
        ctx.move_to(cx, wy0 - 40)
        ctx.line_to(cx + d * 90, wy0 - 40)
        ctx.curve_to(cx + d * 60, wy0 + 200, cx + d * 110, wy0 + 420, cx + d * 70, wy0 + wh + 60)
        ctx.line_to(cx, wy0 + wh + 60)
        ctx.close_path()
        src(ctx, cur)
        ctx.fill()
        for k in range(3):
            line(ctx, cx + d * (20 + k * 20), wy0 - 30, cx + d * (16 + k * 22), wy0 + wh + 40, 2, alpha(C['ink'], 0.15))
    rect(ctx, wx0 - 60, wy0 - 52, ww + 120, 14, P['wood3'])
    # Wandlampe
    lx, ly = 600, 520
    g = cairo.RadialGradient(lx, ly, 5, lx, ly, 240)
    g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.5 if tod != 'morning' else 0.2)
    g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
    ctx.arc(lx, ly, 240, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    poly(ctx, [(lx - 30, ly + 20), (lx + 30, ly + 20), (lx + 18, ly - 30), (lx - 18, ly - 30)], P['cream'])
    rect(ctx, lx - 4, ly + 20, 8, 30, P['gold'])
    # Bild mit Muschel
    fill_rrect(ctx, 760, 420, 220, 170, 4, P['gold'])
    rect(ctx, 774, 434, 192, 142, hexc('#F3E7CC') if not home else hexc('#CFE9FF'))
    ctx.save()
    ctx.translate(870, 520)
    ctx.scale(2.2, 2.2)
    ctx.move_to(0, 10)
    for i in range(9):
        a = math.radians(200 + i * 140 / 8)
        ctx.line_to(math.cos(a) * 26, math.sin(a) * 26 + 4)
    ctx.close_path()
    src(ctx, C['pink3'])
    ctx.fill()
    ctx.restore()
    if tod == 'night':
        rect(ctx, 0, 0, W, H, alpha(hexc('#0B0E2A'), 0.35))


def bed(ctx, x=600, y=1470, home=False):
    fill_rrect(ctx, x + 380, y - 420, 60, 420, 10, P['wood3'])
    rect(ctx, x, y - 170, 440, 120, C['white'])
    fill_rrect(ctx, x + 300, y - 230, 120, 70, 30, C['white'])
    rect(ctx, x, y - 160, 330, 110, P['teal3'] if not home else hexc('#7DBA86'))
    rect(ctx, x, y - 160, 330, 16, mixc(P['teal3'] if not home else hexc('#7DBA86'), C['white'], 0.3))
    rect(ctx, x - 10, y - 60, 460, 40, P['wood2'])
    rect(ctx, x, y - 20, 20, 20, P['wood3'])
    rect(ctx, x + 420, y - 20, 20, 20, P['wood3'])


def desk(ctx, x=120, y=1470):
    rect(ctx, x, y - 230, 360, 26, P['wood2'])
    rect(ctx, x + 10, y - 204, 340, 70, P['wood'])
    circle(ctx, x + 180, y - 170, 6, P['gold'])
    rect(ctx, x + 20, y - 134, 18, 134, P['wood3'])
    rect(ctx, x + 322, y - 134, 18, 134, P['wood3'])


def safe(ctx, x, y, s=1.0, open_k=0.0, state='locked', inside=()):
    """Tresor (x = Mitte, y = Unterkante). open_k 0..1 Tür auf. inside: Liste von Zeichenfunktionen (lokal)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    w, h = 220, 170
    fill_rrect(ctx, -w / 2 - 6, -h - 6, w + 12, h + 12, 14, hexc('#4A5068'))
    fill_rrect(ctx, -w / 2, -h, w, h, 12, hexc('#6B7390'))
    # Innenraum
    rect(ctx, -w / 2 + 16, -h + 16, w - 32, h - 32, hexc('#1E2230'))
    ctx.save()
    ctx.rectangle(-w / 2 + 16, -h + 16, w - 32, h - 32)
    ctx.clip()
    for fn in inside:
        fn(ctx)
    ctx.restore()
    # Tür (links angeschlagen, klappt nach links auf)
    dw = (w - 20) * (1 - open_k)
    if dw > 2:
        g = cairo.LinearGradient(-w / 2 + 10, 0, -w / 2 + 10 + dw, 0)
        g.add_color_stop_rgba(0, *hexc('#7E87A6'))
        g.add_color_stop_rgba(1, *hexc('#5C6480'))
        rrect(ctx, -w / 2 + 10, -h + 10, dw, h - 20, 10)
        ctx.set_source(g)
        ctx.fill()
        if open_k < 0.3:
            fill_rrect(ctx, -w / 2 + 26, -h + 26, 110, 34, 4, hexc('#101418'))
            col = P['red'] if state == 'locked' else C['green']
            text(ctx, 'GESPERRT' if state == 'locked' else 'OFFEN', -w / 2 + 81, -h + 43, 15, col, font=SLAB)
            for i in range(3):
                for j in range(3):
                    fill_rrect(ctx, -w / 2 + 30 + j * 34, -h + 74 + i * 26, 26, 18, 3, hexc('#C9CCD8'))
            circle(ctx, w / 2 - 50, -h / 2, 24, hexc('#C9CCD8'))
            circle(ctx, w / 2 - 50, -h / 2, 18, hexc('#7E87A6'))
            line(ctx, w / 2 - 50, -h / 2, w / 2 - 50, -h / 2 - 16, 5, hexc('#C9CCD8'))
            circle(ctx, w / 2 - 22, -h + 30, 5, P['red'] if state == 'locked' else C['green'])
    ctx.restore()


def check_badge(ctx, x, y, k):
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    check_icon(ctx, 0, 0, 34)
    ctx.restore()


def cross_badge(ctx, x, y, k):
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    circle(ctx, 0, 0, 30, C['white'])
    cross_icon(ctx, 0, 0, 14)
    ctx.restore()


# ---------------------------------------------------------------- Szenen
def sc_arrive(ctx, T, t0):
    cam = Cam(540, -560, 0.8)
    k = ease(T, t0, t0 + 2.4)
    x = lerp(-120, 470, k)
    ctx.save()
    cam.apply(ctx)
    hotel_facade(ctx, cam, T, belegt=0.0)
    shelly_x(ctx, T, x, GROUND + 40, 1.25, walk=T * 9 if k < 1 else None, face=0.8 if k < 1 else 0)
    fill_rrect(ctx, x - 90, GROUND - 40, 46, 70, 8, hexc('#3F6E9E'))
    line(ctx, x - 67, GROUND - 40, x - 67, GROUND - 70, 4, C['ink'])
    ctx.restore()
    paper_card(ctx, T, nw('sandkorn') - 0.1, [('ZUM BEISPIEL IM', 28, TYPE, P['ink']), ('HOTEL SANDKORN', 60, SLAB, P['ink'])], 540, 560, -2)


def sc_ritual_intro(ctx, T, t0):
    """Jedes Mal: ein Schuh in den Safe, nie der andere."""
    room(ctx, T, 'eve')
    bed(ctx)
    desk(ctx)
    t_safe = nw('zimmersafe') - 0.3
    ko = 1 - ease(T, t_safe + 0.6, t_safe + 1.0)
    safe(ctx, 300, 1240, 1.0, ko, 'locked' if ko < 0.2 else 'open',
         inside=[lambda c: shoe(c, 0, 50, 1.4)] if T > t_safe else [])
    shoe(ctx, 560, 1470, 1.6)
    shelly_x(ctx, T, 470, 1480, 1.9, arms={'R': (40, -110)} if T < t_safe + 0.5 else None, shoes=(True, False), mirror=True)
    if T < t_safe + 0.3:
        shoe(ctx, 390, 1250, 1.3, -0.2)
    paper_card(ctx, T, nw('zimmersafe') - 0.2, [('1 SCHUH', 60, SLAB, P['ink']), ('EINGESCHLOSSEN', 34, TYPE, P['red'])], 540, 300 + 60, -3)
    if T >= nw('nie') - 0.1:
        cross_badge(ctx, 560, 1360, pop(T, nw('nie') - 0.1))


def sc_evening(ctx, T, t0):
    """Jeden Abend zieht sie die Schuhe aus."""
    room(ctx, T, 'night')
    bed(ctx)
    desk(ctx)
    safe(ctx, 300, 1240, 1.0, 0.0, 'open')
    t_off = nw('aus') - 0.3
    off = T > t_off
    shelly_x(ctx, T, 560, 1480, 1.9, expr='smile', shoes=(not off, not off), mirror=False)
    if off:
        k = ease(T, t_off, t_off + 0.4)
        shoe(ctx, lerp(540, 470, k), 1480, 1.6)
        shoe(ctx, lerp(580, 660, k), 1480, 1.6)
    paper_card(ctx, T, t0 + 0.1, [('JEDEN ABEND', 50, SLAB, P['ink'])], 540, 360, -2)
    if T >= nw('ritual') - 0.2:
        paper_card(ctx, T, nw('ritual') - 0.2, [('EIN SELTSAMES', 30, TYPE, P['ink']), ('RITUAL', 72, SLAB, P['red'])], 540, 560, 2)


def sc_split(ctx, T, t0):
    """Einen Schuh neben das Bett, den anderen in den Safe -> abschließen."""
    room(ctx, T, 'night')
    bed(ctx)
    desk(ctx)
    t_bed = nw('bett') - 0.2
    t_safe = nw('safe', 0) - 0.4
    t_lock = nw('ab', 0, after=nw('schliesst', 1) - 0.1) - 0.1
    k_walk = ease(T, t_bed + 0.3, t_safe)
    x = lerp(620, 420, k_walk)
    ko = ease(T, t_safe - 0.2, t_safe + 0.1) * (1 - ease(T, t_lock - 0.2, t_lock + 0.1))
    state = 'locked' if T >= t_lock else 'open'
    inside = [lambda c: shoe(c, 0, 50, 1.4)] if T > t_safe + 0.2 else []
    safe(ctx, 300, 1240, 1.0, ko, state, inside)
    shoe(ctx, 600, 1480, 1.6)
    if T >= t_bed:
        check_badge(ctx, 600, 1380, pop(T, t_bed))
    out = shelly_x(ctx, T, x, 1480, 1.9, walk=T * 9 if 0 < k_walk < 1 else None, mirror=True, face=0.8 if 0 < k_walk < 1 else 0,
                   shoes=(False, False), arms={'R': (34, -100)} if T < t_safe + 0.3 else None)
    if T < t_safe + 0.25:
        hx, hy = out['R']
        shoe(ctx, hx - 10, hy + 20, 1.3, 0.3)
    if T >= t_lock:
        paper_card(ctx, T, t_lock, [('ABGESCHLOSSEN', 54, SLAB, P['red'])], 540, 380, -2)


def sc_morning(ctx, T, t0):
    room(ctx, T, 'morning')
    bed(ctx)
    desk(ctx)
    t_out = nw('heraus') - 0.4
    ko = ease(T, t0 + 0.3, t0 + 0.7)
    safe(ctx, 300, 1240, 1.0, ko, 'open', [lambda c: shoe(c, 0, 50, 1.4)] if T < t_out else [])
    got = T >= t_out
    shelly_x(ctx, T, 430, 1480, 1.9, mirror=True, shoes=(got, True), expr='smile', arms={'R': (34, -100)} if t_out - 0.4 < T < t_out + 0.4 else None)
    paper_card(ctx, T, t0 + 0.1, [('AM NÄCHSTEN MORGEN', 44, SLAB, P['ink'])], 540, 360, -2)


def corridor_side(ctx, T):
    rect(ctx, 0, 0, W, 260, P['wood3'])
    rect(ctx, 0, 250, W, 14, P['cream'])
    rect(ctx, 0, 264, W, 1000, P['teal'])
    for i in range(0, W, 34):
        line(ctx, i, 264, i, 1250, 3, P['teal2'])
    rect(ctx, 0, 1250, W, 200, P['wood'])
    rect(ctx, 0, 1246, W, 12, P['wood2'])
    rect(ctx, 0, 1450, W, H - 1450, hexc('#E3D3B0'))
    # Tür 207
    rect(ctx, 120, 760, 340, 700, P['wood3'])
    rect(ctx, 140, 780, 300, 680, hexc('#C98B4A'))
    for (a, b) in ((820, 1080), (1120, 1420)):
        rrect(ctx, 170, a, 240, b - a, 6)
        ctx.set_line_width(4)
        src(ctx, mixc(hexc('#C98B4A'), C['ink'], 0.25))
        ctx.stroke()
    fill_rrect(ctx, 220, 840, 140, 60, 6, hexc('#2A1E16'))
    text(ctx, '207', 290, 870, 40, P['gold2'], font=ZILLA)
    circle(ctx, 410, 1130, 10, P['gold'])
    # Schrank
    rect(ctx, 600, 700, 420, 760, P['wood3'])
    rect(ctx, 620, 720, 190, 720, P['wood2'])
    rect(ctx, 830, 720, 170, 720, P['wood2'])
    circle(ctx, 800, 1080, 8, P['gold'])
    circle(ctx, 840, 1080, 8, P['gold'])


def sc_friend(ctx, T, t0):
    corridor_side(ctx, T)
    friend(ctx, T, 330, 1520, 1.95)
    shelly_x(ctx, T, 760, 1520, 1.9, mirror=True, expr='smile')
    t_seltsam = nw('seltsam') - 0.2
    if UI_ON[0] and T >= t_seltsam:
        k = pop(T, t_seltsam)
        ctx.save()
        ctx.translate(380, 980)
        ctx.scale(k, k)
        fill_rrect(ctx, -90, -60, 180, 120, 26, C['white'])
        poly(ctx, [(-10, 56), (20, 56), (-20, 90)], C['white'])
        shoe(ctx, -20, 20, 1.1)
        text(ctx, '?', 50, -6, 70, P['red'], font=SLAB)
        ctx.restore()
    paper_card(ctx, T, nw('rätselhafter') - 0.3, [('NOCH', 30, TYPE, P['ink']), ('RÄTSELHAFTER', 56, SLAB, P['ink'])], 540, 400, 2)


def sc_home(ctx, T, t0):
    room(ctx, T, 'morning', home=True)
    bed(ctx, home=True)
    # Katze auf dem Bett
    cx, cy = 760, 1300
    ellipse(ctx, cx, cy, 60, 26, hexc('#F2A23C'))
    circle(ctx, cx - 56, cy - 18, 22, hexc('#F2A23C'))
    poly(ctx, [(cx - 72, cy - 34), (cx - 66, cy - 54), (cx - 56, cy - 36)], hexc('#F2A23C'))
    poly(ctx, [(cx - 52, cy - 36), (cx - 44, cy - 54), (cx - 38, cy - 32)], hexc('#F2A23C'))
    line(ctx, cx + 56, cy, cx + 90, cy - 30 + math.sin(T * 3) * 8, 8, hexc('#F2A23C'))
    for i in range(3):
        line(ctx, cx - 20 + i * 20, cy - 20, cx - 16 + i * 20, cy + 20, 4, alpha(hexc('#C9781E'), 0.6))
    shoe(ctx, 520, 1480, 1.6)
    shoe(ctx, 600, 1480, 1.6)
    check_badge(ctx, 560, 1380, pop(T, nw('nie', 1) - 0.1))
    paper_card(ctx, T, t0 + 0.05, [('ZU HAUSE: NIE', 54, SLAB, P['ink'])], 540, 380, -2)
    if T >= nw('nur', 0, after=t0) - 0.1:
        paper_card(ctx, T, nw('nur', 0, after=t0) - 0.1, [('NUR', 40, TYPE, P['ink']), ('IM HOTEL', 66, SLAB, P['red'])], 540, 560, 2)


def sc_question(ctx, T, t0):
    room(ctx, T, 'night')
    desk(ctx, 360, 1560)
    safe(ctx, 540, 1330, 1.6, 0.0, 'locked')
    paper_card(ctx, T, t0 + 0.05, [('WARUM?', 100, SLAB, P['red'])], 540, 420, -3)
    if T >= nw('schreib') - 0.05:
        paper_card(ctx, T, nw('schreib') - 0.05, [("SCHREIB'S IN DIE", 34, SLAB, P['ink']), ('KOMMENTARE', 50, SLAB, P['red'])], 540, 650, 2)
    if T >= GAP_AT:
        calendar(ctx, T, GAP_AT + 0.05, 820, 940)


def puff(ctx, x, y, k):
    if k <= 0 or k >= 1:
        return
    r = random.Random(2)
    for i in range(14):
        a = r.uniform(0, 2 * math.pi)
        d = r.uniform(20, 160) * (0.4 + k)
        rr = r.uniform(50, 110) * (1 - 0.4 * k)
        circle(ctx, x + math.cos(a) * d, y + math.sin(a) * d * 1.3, rr, alpha(C['white'], 0.9 * (1 - k)))


def sc_answer(ctx, T, t0):
    """Die Antwort: Puff -> Flugbegleiterin."""
    corridor_side(ctx, T)
    t_f = TW('flugbegl') - 0.2
    uni = T >= t_f + 0.25
    friend(ctx, T, 330, 1520, 1.95)
    shelly_x(ctx, T, 760, 1520, 1.9, mirror=True, expr='open' if uni else 'smile', uniform=uni)
    puff(ctx, 760, 1200, clamp((T - t_f) / 0.7))
    if T < t_f:
        paper_card(ctx, T, t0 + 0.05, [('DIE ANTWORT', 70, SLAB, P['ink'])], 540, 400, -3)
    else:
        paper_card(ctx, T, t_f + 0.15, [('FLUG-', 64, SLAB, P['red']), ('BEGLEITERIN', 64, SLAB, P['red'])], 540, 420, -3)


def sc_plane(ctx, T, t0):
    rect(ctx, 0, 0, W, H, hexc('#F3EFE8'))
    rect(ctx, 0, 0, W, 200, hexc('#E3DED4'))
    for i in range(6):
        rect(ctx, 40 + i * 180, 120, 120, 24, hexc('#D2CCC0'))
    rect(ctx, 0, 820, W, 24, P['red'])
    for i in range(4):
        cx = 140 + i * 270
        fill_rrect(ctx, cx - 50, 420, 100, 170, 50, hexc('#CFC8BA'))
        fill_rrect(ctx, cx - 38, 432, 76, 146, 38, hexc('#FFE3A3'))
        g = cairo.LinearGradient(0, 432, 0, 578)
        g.add_color_stop_rgba(0, 1, 0.7, 0.35, 0.8)
        g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0.3)
        rrect(ctx, cx - 38, 432, 76, 146, 38)
        ctx.set_source(g)
        ctx.fill()
    rect(ctx, 0, 1520, W, 400, hexc('#C9CCD8'))
    rect(ctx, 0, 1560, W, 60, hexc('#24315F'))
    # Sitze + Passagiere
    for i, cx in enumerate((150, 920)):
        figure(ctx, cx + 20, 1500, 2.2, 30 + i, 'travel', face=1 if i == 0 else -1)
        fill_rrect(ctx, cx - 70, 1060, 110, 300, 26, hexc('#2F5FB0'))
        fill_rrect(ctx, cx - 80, 1300, 170, 70, 16, hexc('#2F5FB0'))
        rect(ctx, cx - 60, 1370, 14, 140, hexc('#5A5A66'))
        rect(ctx, cx + 50, 1370, 14, 140, hexc('#5A5A66'))
    # Trolley
    tx = lerp(700, 640, ease(T, t0, t0 + 2))
    fill_rrect(ctx, tx - 70, 1180, 140, 300, 10, hexc('#D8DCE6'))
    for j in range(4):
        rect(ctx, tx - 60, 1200 + j * 70, 120, 50, hexc('#B9BFCF'))
    circle(ctx, tx - 50, 1490, 12, C['ink'])
    circle(ctx, tx + 50, 1490, 12, C['ink'])
    shelly_x(ctx, T, 470, 1520, 1.9, uniform=True, arms={'R': (40, -96)}, expr='open')
    paper_card(ctx, T, t0 + 0.05, [('BERUFLICH', 34, TYPE, P['ink']), ('STÄNDIG UNTERWEGS', 50, SLAB, P['ink'])], 540, 360, -2)


def safe_closeup(ctx, T, ko, state, items):
    room(ctx, T, 'night')
    rect(ctx, 0, 1450, W, H - 1450, hexc('#E3D3B0'))
    rect(ctx, 80, 1380, 920, 40, P['wood2'])
    rect(ctx, 100, 1420, 880, 120, P['wood'])
    safe(ctx, 540, 1380, 3.4, ko, state, items)


def sc_pass(ctx, T, t0):
    t_pass = nw('muschelpass') - 0.2
    t_pap = nw('papiere') - 0.2
    t_close = nw('safe', 1) - 0.1
    ko = ease(T, t0, t0 + 0.4) * (1 - ease(T, t_close + 0.4, t_close + 0.8))
    items = []
    if T >= t_pass:
        kk = ease(T, t_pass, t_pass + 0.4)
        items.append(lambda c, kk=kk: muschelpass(c, lerp(200, -40, kk), lerp(-160, 30, kk), 1.0, 0.1))
    if T >= t_pap:
        kk = ease(T, t_pap, t_pap + 0.4)
        items.append(lambda c, kk=kk: papers(c, lerp(200, 40, kk), lerp(-160, 20, kk), 0.8))
    safe_closeup(ctx, T, ko, 'locked' if T > t_close + 0.8 else 'open', items)
    paper_card(ctx, T, t_pass, [('MUSCHELPASS', 60, SLAB, P['ink']), ('+ WICHTIGE PAPIERE', 32, TYPE, P['red'])], 540, 400, -2)


def sc_forget(ctx, T, t0):
    room(ctx, T, 'morning')
    bed(ctx)
    desk(ctx)
    safe(ctx, 300, 1240, 1.0, 0.0, 'locked')
    # Röntgenblick: Papiere im Safe
    if UI_ON[0]:
        g = 0.6 + 0.4 * math.sin(T * 6)
        rrect(ctx, 190, 1050, 220, 190, 16)
        ctx.set_line_width(6)
        src(ctx, alpha(C['yellow'], g))
        ctx.stroke()
    muschelpass(ctx, 270, 1160, 0.9)
    papers(ctx, 340, 1160, 0.7)
    k = ease(T, nw('abreisen') - 0.6, nw('vergessen') + 0.3)
    x = lerp(560, 1150, k)
    shelly_x(ctx, T, x, 1480, 1.9, uniform=True, walk=T * 9 if 0 < k < 1 else None, face=0.8 if 0 < k < 1 else 0)
    fill_rrect(ctx, x + 30, 1380, 70, 100, 10, hexc('#3F6E9E'))
    line(ctx, x + 65, 1380, x + 65, 1330, 5, C['ink'])
    paper_card(ctx, T, nw('vergesslich') - 0.2, [('ZIEMLICH', 30, TYPE, P['ink']), ('VERGESSLICH', 64, SLAB, P['red'])], 540, 380, -2)
    if T >= nw('vergessen') - 0.2:
        cross_badge(ctx, 300, 980, pop(T, nw('vergessen') - 0.2))


def sc_solve(ctx, T, t0):
    """Zurückspulen, dann: ohne zweiten Schuh kann sie nicht los -> Safe auf -> Schuh + Muschelpass."""
    t_rew = t0
    t_door = TW('weil') - 0.2
    t_open = TW('öffnen') - 0.6
    t_take = TW('nimmt') - 0.2
    room(ctx, T, 'morning')
    bed(ctx)
    desk(ctx)
    if T < t_door:
        # Rückspulen: Safe mit Schuh + Pass
        safe(ctx, 300, 1240, 1.0, 0.0, 'locked')
        shoe(ctx, 300, 1160, 1.1)
        muschelpass(ctx, 250, 1160, 0.8)
        shelly_x(ctx, T, lerp(900, 520, ease(T, t0, t_door)), 1480, 1.9, uniform=True, mirror=True, shoes=(True, False))
        if UI_ON[0]:
            for i in range(10):
                yy = (i * 190 + T * 2400) % H
                rect(ctx, 0, yy, W, 6, alpha(C['white'], 0.2))
            for j in range(2):
                poly(ctx, [(110 + j * 40, 300), (150 + j * 40, 272), (150 + j * 40, 328)], C['white'])
            text(ctx, 'REW', 260, 300, 54, C['white'], font=SLAB)
        return
    if T < t_open:
        # an der Tür: nur ein Schuh -> geht nicht
        k = ease(T, t_door, t_door + 0.8)
        safe(ctx, 300, 1240, 1.0, 0.0, 'locked')
        shelly_x(ctx, T, lerp(690, 760, k), 1480, 1.9, uniform=True, shoes=(True, False), expr='o')
        cross_badge(ctx, 775, 1530, pop(T, t_door + 0.4))
        paper_card(ctx, T, TW('beide') - 0.1, [('BEIDE SCHUHE!', 70, SLAB, P['red'])], 540, 380, -2)
        return
    ko = ease(T, t_open, t_open + 0.4)
    items = []
    if T < t_take + 0.5:
        items.append(lambda c: shoe(c, -20, 50, 1.4))
    if T < t_take + 0.9:
        items.append(lambda c: muschelpass(c, 50, 20, 1.0))
    safe(ctx, 300, 1240, 1.0, ko, 'open', items)
    got = T >= t_take + 0.5
    out = shelly_x(ctx, T, 470, 1480, 1.9, uniform=True, mirror=True, shoes=(True, got),
                   arms={'R': (34, -100)} if t_take - 0.2 < T < t_take + 1.0 else None, expr='open' if got else 'smile')
    if T >= t_take + 0.9:
        hx, hy = out['R'] if 'R' in out else (430, 1290)
        muschelpass(ctx, 360, 1320, 1.0, -0.2)
        check_badge(ctx, 360, 1220, pop(T, t_take + 0.9))
    if T >= t_open:
        paper_card(ctx, T, t_open, [('SAFE AUF =', 34, TYPE, P['ink']), ('MUSCHELPASS DABEI', 52, SLAB, P['ink'])], 540, 380, -2)


def sc_end(ctx, T, t0):
    corridor_side(ctx, T)
    shelly_x(ctx, T, 760, 1520, 1.9, mirror=True, uniform=True, arms={'R': (34, -140 + math.sin(T * 8) * 10)}, expr='open')
    fill_rrect(ctx, 600, 1420, 80, 110, 10, hexc('#3F6E9E'))
    paper_card(ctx, T, t0 + 0.05, [("HAST DU'S", 60, SLAB, P['ink']), ('GEWUSST?', 74, SLAB, P['red'])], 540, 420, -3)
    if T >= TW('gewusst', end=True) + 0.4:
        paper_card(ctx, T, TW('gewusst', end=True) + 0.4, [("SCHREIB'S IN DIE KOMMENTARE", 30, SLAB, P['ink'])], 540, 650, 2)


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
    ctx.save()
    cam.apply(ctx)
    hotel_facade(ctx, cam, T, belegt=0.0)
    shelly_x(ctx, T, 330, GROUND + 40, 1.2, arms={'R': (34, -140 + math.sin(T * 8) * 10)}, expr='open')
    ctx.restore()
    paper_card(ctx, T, TW('wohnst') - 0.05, [('WOHNST DU SCHON IN', 34, TYPE, P['ink']), ('MUSCHELTAL?', 80, SLAB, P['ink'])], 540, 520, -2)
    tf = TW('folge') - 0.05
    tap = TW('namen') + 0.3
    if UI_ON[0] and T >= tf:
        k = back_out(T, tf, tf + 0.3, 2.0)
        ctx.save()
        ctx.translate(540, 760)
        ctx.scale(max(k, 0.01), max(k, 0.01))
        on = T >= tap
        fill_rrect(ctx, -170 + 6, -50 + 10, 340, 100, 14, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -170, -50, 340, 100, 14, C['green'] if on else P['red'])
        text(ctx, 'GEFOLGT' if on else 'FOLGEN', -24 if on else 0, 0, 48, C['white'], font=SLAB)
        if on:
            tick_mark(ctx, 120, 0, 34, C['white'])
        ctx.restore()
    hut_card(ctx, T, TW('hütte') - 0.2, 800, 1240)


# ---------------------------------------------------------------- Zeitleiste
SC = [
    ('arrive', 0.0, sc_arrive),
    ('ritual', nw('und', 0) - 0.1, sc_ritual_intro),
    ('evening', nw('jeden') - 0.1, sc_evening),
    ('split', nw('einen', 1) - 0.1, sc_split),
    ('morning', nw('am', 0) - 0.1, sc_morning),
    ('friend', nw('ihre', 1) - 0.1, sc_friend),
    ('home', nw('zu', 0, after=nw('rätselhafter')) - 0.1, sc_home),
    ('question', nw('also', 0) - 0.1, sc_question),
    ('answer', TW('hier') - 0.1, sc_answer),
    ('plane', TW('sie', 0, after=nw('lösung', 1) + 1.2) - 0.1, sc_plane),
    ('pass', TW('im', 0, after=nw('unterwegs')) - 0.1, sc_pass),
    ('forget', TW('aber', 0, after=nw('unterwegs')) - 0.1, sc_forget),
    ('solve', TW('und', 0, after=nw('vergessen')) - 0.1, sc_solve),
    ('end', TW('hast') - 0.1, sc_end),
    ('outro', TW('und', 0, after=nw('kommentare', 1) + 0.1) - 0.1, sc_outro),
]


ROOM_ZOOM = {'ritual': 1.4, 'evening': 1.4, 'split': 1.4, 'morning': 1.4, 'forget': 1.3, 'solve': 1.4,
             'friend': 1.25, 'answer': 1.25, 'end': 1.25, 'home': 1.3}


def frame(ctx, T):
    cur = SC[0]
    for s_ in SC:
        if T >= s_[1]:
            cur = s_
    if cur[0] in ROOM_ZOOM:
        z = ROOM_ZOOM[cur[0]]
        ctx.save()
        ctx.translate(540, 1300)
        ctx.scale(z, z)
        ctx.translate(-540, -1300)
        cur[2](ctx, T, cur[1])
        ctx.restore()
    else:
        cur[2](ctx, T, cur[1])
    for s_ in SC[1:]:
        if 0 <= T - s_[1] < 0.08:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.3 * (1 - (T - s_[1]) / 0.08)))
