"""Neufassung: Vier Freunde, vier Muschelhüte – Logikrätsel im Retro-Stil (Strandtreppe in Muscheltal)."""
import json, math, os, random, re
import cairo
from draw import *
from chars import shelly, NEIGHBOR_LOOK
import retro
from retro import P, SLAB, TYPE, ZILLA
from figs import man

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = json.load(open(f'{ROOT}/audio/vo_words.json'))


def _norm(w):
    w = re.sub(r"[^\wäöüß']", '', w.lower()).replace('ß', 'ss')
    return {'sofia': 'sophia', 'sofias': 'sophias', 'lamra': 'laura'}.get(w, w)


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


PINK, BLUE = hexc('#F28DB2'), hexc('#4FA3E8')


def shell_hat(ctx, x, y, s, col, q=0.0):
    """Muschelhut, Unterkante bei (x, y). q>0: Fragezeichen-Variante (unbekannte Farbe)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    c = mixc(col, hexc('#B9BFCF'), q)
    n = 7
    R = 42
    ctx.move_to(0, 6)
    for i in range(n + 1):
        a = math.radians(200 + 140 * i / n)
        ctx.line_to(math.cos(a) * R, math.sin(a) * R * 0.9)
        if i < n:
            am = math.radians(200 + 140 * (i + 0.5) / n)
            ctx.curve_to(math.cos(am) * R * 1.12, math.sin(am) * R, math.cos(am) * R * 1.12, math.sin(am) * R,
                         math.cos(a + math.radians(140 / n)) * R, math.sin(a + math.radians(140 / n)) * R * 0.9)
    ctx.close_path()
    src(ctx, c)
    ctx.fill_preserve()
    ctx.set_line_width(3)
    src(ctx, mixc(c, C['ink'], 0.3))
    ctx.stroke()
    for i in range(1, n):
        a = math.radians(200 + 140 * i / n)
        line(ctx, 0, 4, math.cos(a) * R * 0.92, math.sin(a) * R * 0.85, 2, alpha(mixc(c, C['ink'], 0.3), 0.8))
    ellipse(ctx, 0, 6, 46, 8, mixc(c, C['ink'], 0.2))
    if q > 0.5:
        text(ctx, '?', 0, -18, 34, C['white'], font=SLAB)
    ctx.restore()


# ---------------------------------------------------------------- Figuren
# ---------------------------------------------------------------- Bühne in Weltkoordinaten (Boden y = 0)
NST, RUN, RISE = 10, 66, 52
XT, YT = 280, -NST * RISE          # Oberkante Plattform
PIL0, PIL1, PILT = 1080, 1190, -980


def step_top(i):
    return YT + (i + 1) * RISE


def step_x(i):
    return XT + i * RUN + RUN / 2


POS = {1: (170, YT), 2: (step_x(2), step_top(2)), 3: (1010, 0), 4: (1310, 0)}
HAT = {1: BLUE, 2: PINK, 3: BLUE, 4: PINK}
NAME = {1: 'MUSCHELBERT', 2: 'SHELLY', 3: 'SOPHIA', 4: 'LAURA'}
S = 1.5


class Cam:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def apply(self, ctx):
        ctx.translate(W / 2, H / 2)
        ctx.scale(self.z, self.z)
        ctx.translate(-self.x, -self.y)


WIDE = (790, -190, 0.72)
CAM = [Cam(*WIDE)]


def cam_path(T, keys):
    if T <= keys[0][0]:
        return Cam(*keys[0][1:])
    for a, b in zip(keys, keys[1:]):
        if T <= b[0]:
            k = ease(T, a[0], b[0])
            z = math.exp(lerp(math.log(a[3]), math.log(b[3]), k))
            return Cam(lerp(a[1], b[1], k), lerp(a[2], b[2], k), z)
    return Cam(*keys[-1][1:])


def scr(x, y):
    c = CAM[0]
    return (W / 2 + (x - c.x) * c.z, H / 2 + (y - c.y) * c.z)


def girl(ctx, who, x, y, s, T, expr='smile', arms=None, look=(4, 0)):
    if who == 'shelly':
        shelly(ctx, x, y, s, shell=False, expr=expr, blink=blink(T), arms=arms, face=0.7, look=look)
        return
    pal = NEIGHBOR_LOOK[who]
    old = {k: C[k] for k in pal}
    for k, v in pal.items():
        C[k] = hexc(v)
    try:
        shelly(ctx, x, y, s, shell=False, long_hair=True, expr=expr, blink=blink(T, 0.4), arms=arms, face=0.7, look=look)
    finally:
        C.update(old)


def shadow(ctx, x, y, w=46):
    ellipse(ctx, x + 4, y, w, 9, alpha(C['shadow'], 0.28))


def draw_person(ctx, i, T, hat_q=None, expr='smile', arms=None):
    x, y = POS[i]
    q = hat_q.get(i, 0.0) if hat_q else 0.0
    shadow(ctx, x, y, 34 * S)
    if i == 1:
        man(ctx, x, y, S * 1.05, 'bert', face=1, T=T, cap_on=False, arm=arms)
        shell_hat(ctx, x + 2 * S, y - 150 * S * 1.05, S, HAT[i], q)
    else:
        who = {2: 'shelly', 3: 'sophia', 4: 'laura'}[i]
        girl(ctx, who, x, y, S, T, expr, {'R': arms} if arms else None)
        shell_hat(ctx, x + 4 * S, y - 162 * S, S * 1.05, HAT[i], q)
    bx, by = x - 44 * S, y - 82 * S
    circle(ctx, bx, by, 24, C['white'])
    circle(ctx, bx, by, 20, hexc('#2B2F4A'))
    text(ctx, str(i), bx, by + 1, 26, C['white'], font=SLAB)


# ---------------------------------------------------------------- Kulisse
def scene_bg(ctx, T):
    c = CAM[0]
    hw, hh = W / 2 / c.z + 20, H / 2 / c.z + 20
    x0, y0, x1, y1 = c.x - hw, c.y - hh, c.x + hw, c.y + hh
    g = cairo.LinearGradient(0, -1900, 0, -250)
    for o, col in ((0, '#4E3F95'), (0.45, '#8A66B8'), (0.78, '#E28AA8'), (1, '#FFC27A')):
        g.add_color_stop_rgba(o, *hexc(col))
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.translate((c.x - WIDE[0]) * 0.45, (c.y - WIDE[1]) * 0.2)   # Parallaxe
    circle(ctx, 930, -560, 170, alpha(hexc('#FFE08A'), 0.35))
    circle(ctx, 930, -560, 110, hexc('#FFB45A'))
    for i, (cx, cy, s_) in enumerate([(-80, -1500, 90), (500, -1700, 70), (1150, -1350, 80), (250, -1150, 60)]):
        cloud_shape(ctx, cx + (T * 9 * (1 + i * 0.3)) % 160, cy, s_, alpha(C['white'], 0.55))
    far, near = alpha(hexc('#B49AD8'), 0.75), hexc('#9E86CC')
    # Muscheltal-Skyline: Muschelturm, Leuchtturm, Hütten
    for hx, hw_, hh_ in ((-300, 160, 380), (-120, 120, 300), (420, 140, 420), (640, 110, 340), (1300, 150, 360), (1480, 130, 300)):
        rect(ctx, hx, -330 - hh_, hw_, hh_, far)
        for wy in range(int(-330 - hh_ + 40), -360, 60):
            for wx in range(int(hx + 22), int(hx + hw_ - 30), 44):
                rect(ctx, wx, wy, 20, 28, alpha(hexc('#FFE6B0'), 0.45))
    ctx.move_to(130, -330)
    ctx.line_to(150, -1050)
    ctx.curve_to(190, -1180, 290, -1180, 330, -1050)
    ctx.line_to(350, -330)
    ctx.close_path()
    src(ctx, far)
    ctx.fill()
    for k in range(6):
        line(ctx, 240, -1120, 160 + k * 34, -1000, 4, alpha(hexc('#8A70BA'), 0.8))
    rect(ctx, 820, -1000, 70, 670, near)
    rect(ctx, 806, -1060, 98, 60, alpha(hexc('#FFE6B0'), 0.8))
    poly(ctx, [(796, -1060), (914, -1060), (855, -1130)], near)
    for hx in range(-500, 1800, 150):
        hh_ = 120 + (hx * 7) % 90
        rect(ctx, hx, -330 - hh_, 110, hh_, near)
        poly(ctx, [(hx - 12, -330 - hh_), (hx + 55, -330 - hh_ - 60), (hx + 122, -330 - hh_)], near)
        rect(ctx, hx + 40, -330 - hh_ + 40, 30, 36, alpha(hexc('#FFE6B0'), 0.6))
    ctx.restore()
    vgrad(ctx, x0, -330, x1 - x0, 340, [(0, hexc('#8C7AC0')), (1, hexc('#5E6AB0'))])
    for i in range(30):
        xx = (i * 97 + T * 22) % 2400 - 700
        yy = -300 + (i % 5) * 60
        line(ctx, xx, yy, xx + 50, yy, 4, alpha(C['white'], 0.35))
    return x0, y0, x1, y1


def bricks(ctx, x0, y0, x1, y1, bw, bh, c1, c2, seed=1):
    r = random.Random(seed)
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    row = 0
    y = y0
    while y < y1:
        off = bw / 2 if row % 2 else 0
        x = x0 - off
        while x < x1:
            fill_rrect(ctx, x + 2, y + 2, bw - 4, bh - 4, 3, mixc(c1, c2, r.random() * 0.7))
            x += bw
        y += bh
        row += 1
    ctx.restore()


def stage(ctx, T, b):
    x0, y0, x1, y1 = b
    # Haus links (gelb) mit Laterne
    rect(ctx, -600, -1700, 640, 1700 + YT, hexc('#F2D27A'))
    rect(ctx, 20, -1700, 20, 1700 + YT, hexc('#D9B45E'))
    for wy in (-1500, -1150):
        fill_rrect(ctx, -300, wy, 150, 220, 70, hexc('#6E7896'))
        fill_rrect(ctx, -290, wy + 10, 130, 200, 62, hexc('#FFE6A8'))
    line(ctx, 40, -900, 110, -900, 6, C['ink'])
    line(ctx, 100, -900, 100, -880, 4, C['ink'])
    fill_rrect(ctx, 84, -880, 32, 46, 6, C['ink'])
    rect(ctx, 90, -874, 20, 32, hexc('#FFE08A'))
    circle(ctx, 100, -858, 40, alpha(hexc('#FFE08A'), 0.25))
    # Plattform-Block + Treppe (Sandstein)
    stone, stone2, top = hexc('#D8B47A'), hexc('#C29A60'), hexc('#F0D5A0')
    pts = [(x0 - 20, YT), (XT, YT)]
    for i in range(NST):
        pts.append((XT + i * RUN, step_top(i)))
        pts.append((XT + (i + 1) * RUN, step_top(i)))
    pts += [(XT + NST * RUN, 0), (XT + NST * RUN, 260), (x0 - 20, 260)]
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    ctx.save()
    ctx.clip_preserve()
    src(ctx, stone)
    ctx.fill()
    bricks(ctx, x0 - 20, YT, XT + NST * RUN, 260, 90, 44, stone, stone2, 3)
    ctx.restore()
    rect(ctx, x0 - 20, YT - 6, XT - x0 + 20, 16, top)
    for i in range(NST):
        sx, sy = XT + i * RUN, step_top(i)
        rect(ctx, sx - 2, sy - 6, RUN + 4, 14, top)
        rect(ctx, sx - 2, sy + 8, RUN + 4, 5, alpha(stone2, 0.8))
    # Promenade + Kaimauer
    rect(ctx, XT + NST * RUN - 4, -8, x1 - XT - NST * RUN + 30, 18, top)
    rect(ctx, XT + NST * RUN - 4, 10, x1 - XT - NST * RUN + 30, 250, stone)
    bricks(ctx, XT + NST * RUN - 4, 10, x1 + 30, 260, 90, 44, stone, stone2, 5)
    rect(ctx, x0 - 20, 260, x1 - x0 + 40, 30, hexc('#B8935A'))
    vgrad(ctx, x0 - 20, 290, x1 - x0 + 40, y1 - 290 + 20, [(0, hexc('#EBCB92')), (1, hexc('#DDB777'))])
    r = random.Random(7)
    for i in range(30):
        sx, sy = r.uniform(-300, 1600), r.uniform(320, 700)
        ellipse(ctx, sx, sy, 12, 7, r.choice([C['pink3'], C['cream'], hexc('#F9B6A0')]))


def railing(ctx):
    teal = hexc('#2F8A86')
    hgt = 150
    # Plattform
    line(ctx, 60, YT - hgt, XT, YT - hgt, 8, teal)
    for px in (60, 160, XT):
        line(ctx, px, YT, px, YT - hgt, 6, teal)
    # Treppe
    xa, ya = XT, YT - hgt
    xb, yb = XT + NST * RUN, -hgt + 10
    line(ctx, xa, ya, xb, yb, 8, teal)
    line(ctx, xb, yb, xb + 30, yb, 8, teal)
    for i in range(0, NST + 1, 2):
        px = XT + i * RUN
        py = step_top(min(i, NST - 1))
        line(ctx, px + 4, py, px + 4, lerp(ya, yb, i / NST), 5, teal)
    for i in range(1, NST):
        px = XT + i * RUN + 4
        line(ctx, px, lerp(ya, yb, i / NST) + 50, px + RUN, lerp(ya, yb, (i + 1) / NST) + 50, 4, alpha(teal, 0.7))


def pillar(ctx, T):
    bricks(ctx, PIL0, PILT, PIL1, 0, 50, 30, hexc('#E39A68'), hexc('#B5643A'), 11)
    rect(ctx, PIL1 - 22, PILT, 22, -PILT, alpha(C['shadow'], 0.18))
    rect(ctx, PIL0 - 12, PILT - 30, PIL1 - PIL0 + 24, 34, hexc('#F0E0C0'))
    rect(ctx, PIL0 - 12, PILT + 4, PIL1 - PIL0 + 24, 8, hexc('#C9B48E'))
    for vx, vy, n in ((PIL0 + 6, PILT + 10, 8), (PIL1 - 6, PILT + 30, 5)):
        for j in range(n):
            yy = vy + j * 50
            xx = vx + math.sin(j * 1.3 + T) * 6
            line(ctx, xx, yy, vx + math.sin((j + 1) * 1.3 + T) * 6, yy + 50, 4, hexc('#3B8A4A'))
            for d in (-1, 1):
                ellipse(ctx, xx + d * 14, yy + 20, 13, 8, hexc('#4FAE5E') if d > 0 else hexc('#3B8A4A'))


def tree(ctx, T):
    x = 1440
    poly(ctx, [(x - 46, -80), (x + 46, -80), (x + 34, 0), (x - 34, 0)], hexc('#D9744A'))
    rect(ctx, x - 52, -92, 104, 18, hexc('#E88A5A'))
    line(ctx, x, -92, x, -230, 10, hexc('#8A5A3A'))
    for dx, dy, r in ((0, -300, 90), (-60, -250, 60), (60, -250, 60)):
        circle(ctx, x + dx, dy, r, hexc('#4FAE5E'))
    for dx, dy in ((-40, -320), (30, -280), (60, -330), (-60, -240), (10, -220)):
        ellipse(ctx, x + dx, dy + math.sin(T * 2 + dx) * 2, 12, 14, hexc('#F7D84A'))


def bushes(ctx, b):
    x0, y0, x1, y1 = b
    for cx, cy, r in ((x0 + 40, 300, 120), (x0 + 160, 330, 90), (x1 - 60, 310, 130), (x1 - 190, 340, 90)):
        circle(ctx, cx, cy, r, hexc('#3B9A5A'))
        circle(ctx, cx - r * 0.3, cy - r * 0.3, r * 0.5, alpha(hexc('#6FCB7A'), 0.6))
    for cx, cy in ((x0 + 90, 230), (x1 - 120, 230)):
        circle(ctx, cx, cy, 12, hexc('#F28DB2'))


def setup(ctx, T, hat_q=None, expr=None, arms=None):
    ctx.save()
    CAM[0].apply(ctx)
    b = scene_bg(ctx, T)
    stage(ctx, T, b)
    for i in (1, 2, 3):
        draw_person(ctx, i, T, hat_q, (expr or {}).get(i, 'smile'), (arms or {}).get(i))
    railing(ctx)
    pillar(ctx, T)
    tree(ctx, T)
    draw_person(ctx, 4, T, hat_q, (expr or {}).get(4, 'smile'), (arms or {}).get(4))
    bushes(ctx, b)
    ctx.restore()


def head(i):
    x, y = POS[i]
    return scr(x + 14, y - 128 * S) if i != 1 else scr(x + 22, y - 122 * S)


def hat_pt(i):
    x, y = POS[i]
    return scr(x, y - 178 * S)


def above(i, dx=0, dy=0):
    x, y = POS[i]
    return scr(x + dx * S * 0.8, y - 190 * S + dy)


def sight(ctx, a, b, k, ok=True):
    if k <= 0:
        return
    x0, y0 = a
    x1, y1 = b
    xe, ye = lerp(x0, x1, k), lerp(y0, y1, k)
    ctx.move_to(x0, y0)
    ctx.line_to(xe, ye)
    ctx.set_dash([14, 10])
    ctx.set_line_width(5)
    src(ctx, C['white'] if ok else P['red'])
    ctx.stroke()
    ctx.set_dash([])
    if k >= 1:
        circle(ctx, x1, y1, 10, C['white'] if ok else P['red'])


def eye_badge(ctx, x, y, k, ok=True):
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    circle(ctx, 0, 0, 30, C['white'])
    ellipse(ctx, 0, 0, 22, 12, C['ink'])
    ellipse(ctx, 0, 0, 18, 9, C['white'])
    circle(ctx, 0, 0, 6, C['ink'])
    if not ok:
        line(ctx, -22, 22, 22, -22, 6, P['red'])
    ctx.restore()


def hat_card(ctx, T, t0, x=540, y=360):
    if T < t0 or not UI_ON[0]:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(-2))
    ctx.scale(k, k)
    fill_rrect(ctx, -300 + 8, -110 + 12, 600, 220, 6, alpha(C['shadow'], 0.35))
    fill_rrect(ctx, -300, -110, 600, 220, 6, P['paper'])
    for i, (col, lab) in enumerate(((PINK, '2 × ROSA'), (BLUE, '2 × BLAU'))):
        cx = -150 + i * 300
        if T >= t0 + i * 0.6:
            shell_hat(ctx, cx - 40, 10, 1.0, col)
            shell_hat(ctx, cx + 40, 10, 1.0, col)
            text(ctx, lab, cx, 70, 36, P['ink'], font=SLAB)
    ctx.restore()


def rules_card(ctx, T, t0, x=540, y=360):
    if T < t0 or not UI_ON[0]:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(-2))
    ctx.scale(k, k)
    fill_rrect(ctx, -320 + 8, -120 + 12, 640, 240, 6, alpha(C['shadow'], 0.35))
    fill_rrect(ctx, -320, -120, 640, 240, 6, P['paper'])
    labels = ['UMDREHEN', 'BEWEGEN', 'ZEICHEN']
    times = [TW('umdrehen') - 0.1, TW('bewegen') - 0.1, TW('zeichen') - 0.1]
    for i, (lab, tt) in enumerate(zip(labels, times)):
        cx = -200 + i * 200
        if T >= tt:
            circle(ctx, cx, -20, 50, hexc('#E8E0CC'))
            if i == 0:
                ctx.new_sub_path(); ctx.arc(cx, -20, 26, 0.5, 5.5); ctx.set_line_width(7); src(ctx, P['ink']); ctx.stroke()
                poly(ctx, [(cx + 22, -34), (cx + 34, -16), (cx + 12, -14)], P['ink'])
            elif i == 1:
                for d in (-1, 1):
                    ellipse(ctx, cx + d * 12, -20 + d * 8, 9, 14, P['ink'])
            else:
                fill_rrect(ctx, cx - 14, -44, 28, 46, 10, P['ink'])
                for j in range(3):
                    fill_rrect(ctx, cx - 16 + j * 10, -52, 8, 20, 4, P['ink'])
            text(ctx, lab, cx, 60, 26, P['ink'], font=SLAB)
            if T >= TW('verboten') - 0.1:
                line(ctx, cx - 44, -64, cx + 44, 24, 8, P['red'])
    ctx.restore()


def thought(ctx, T, t0, x, y, draw, w=460, h=230, tail=None):
    if T < t0 or not UI_ON[0]:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    for dx, dy, r in ((-w * 0.3, 0, h * 0.5), (0, -h * 0.15, h * 0.58), (w * 0.3, 0, h * 0.5), (0, h * 0.18, h * 0.5)):
        circle(ctx, dx, dy, r, C['white'])
    draw(ctx)
    ctx.restore()
    if tail:
        tx, ty = tail
        for j, f in enumerate((0.35, 0.65)):
            circle(ctx, lerp(x, tx, f + 0.15), lerp(y + h * 0.45, ty, f + 0.15), (16 - j * 6) * k, C['white'])


# ---------------------------------------------------------------- Szenen
def sc_hook(ctx, T, t0):
    setup(ctx, T, hat_q={i: 1.0 for i in range(1, 5)})
    if UI_ON[0]:
        for i in range(1, 5):
            kk = pop(T, 1.0 + i * 0.12)
            if kk > 0:
                ctx.save()
                hx, hy = hat_pt(i)
                ctx.translate(hx + 50, hy - 40)
                ctx.scale(kk, kk)
                circle(ctx, 0, 0, 24, C['yellow'])
                text(ctx, '?', 0, 0, 30, C['ink'], font=SLAB)
                ctx.restore()
    card(ctx, T, 0.0, [('4 FREUNDE', 52, SLAB, P['ink']), ('4 MUSCHELHÜTE', 60, SLAB, P['red'])], 540, 330, -2)
    if T >= nw('wer') - 0.1:
        card(ctx, T, nw('wer') - 0.1, [('WER KENNT', 40, SLAB, P['ink']), ('SEINE FARBE?', 50, SLAB, P['red'])], 540, 560, 2)


def sc_setup(ctx, T, t0):
    setup(ctx, T)
    card(ctx, T, t0 + 0.05, [('STRANDTREPPE', 44, SLAB, P['ink']), ('+ SANDSTEINMAUER', 36, TYPE, P['red'])], 540, 330, -2)
    if T >= nw('dahinter') - 0.1:
        sticker(ctx, 'NR. 4 DAHINTER', *above(4, -40, -90), 34, 'yellow', rot=3, sc=pop(T, nw('dahinter') - 0.1))
    hat_card(ctx, T, nw('gibt') - 0.1, 540, 560)


def sc_view(ctx, T, t0):
    setup(ctx, T)
    t1 = nw('sieht') - 0.2
    t_s = nw('sieht', 1) - 0.2
    t_so = nw('sieht', 2) - 0.2
    t_l = nw('sieht', 3) - 0.2
    if T < t_s:
        sight(ctx, head(1), hat_pt(2), ease(T, t1, t1 + 0.5))
        sight(ctx, head(1), hat_pt(3), ease(T, t1 + 0.3, t1 + 0.8))
        if T >= nw('rosa', 1) - 0.2:
            sticker(ctx, 'ROSA', *above(2, 90, -40), 34, 'pink', rot=-3, sc=pop(T, nw('rosa', 1) - 0.2))
        if T >= nw('blau', 1) - 0.2:
            sticker(ctx, 'BLAU', *above(3, 90, -40), 34, 'blue', rot=3, sc=pop(T, nw('blau', 1) - 0.2))
        eye_badge(ctx, *above(1, -40, -50), pop(T, t1))
        card(ctx, T, t0 + 0.05, [('NR. 1 SIEHT', 50, SLAB, P['ink'])], 540, 330, -2)
    else:
        sight(ctx, head(2), hat_pt(3), ease(T, t_s, t_s + 0.5))
        eye_badge(ctx, *above(2, -50, -50), pop(T, t_s))
        if T >= t_so:
            sight(ctx, head(3), (scr(PIL0, 0)[0], head(3)[1]), ease(T, t_so, t_so + 0.4), False)
            eye_badge(ctx, *above(3, -50, -50), pop(T, t_so), False)
        if T >= t_l:
            eye_badge(ctx, *above(4, 0, -60), pop(T, t_l), False)
        card(ctx, T, t_s, [('WER SIEHT WAS?', 50, SLAB, P['ink'])], 540, 330, -2)


def sc_rules(ctx, T, t0):
    setup(ctx, T)
    rules_card(ctx, T, t0 + 0.05, 540, 360)
    if T >= nw('nur', 1) - 0.1:
        card(ctx, T, nw('nur', 1) - 0.1, [('NUR WENN', 34, TYPE, P['ink']), ('100 % SICHER', 56, SLAB, hexc('#2F8A4A'))], 540, 620, 2)


def hourglass(ctx, x, y, k, sc):
    if sc <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    rect(ctx, -60, -110, 120, 14, P['wood2'])
    rect(ctx, -60, 96, 120, 14, P['wood2'])
    poly(ctx, [(-48, -96), (48, -96), (6, 0), (48, 96), (-48, 96), (-6, 0)], alpha(hexc('#DFF4FF'), 0.85))
    top = 1 - k
    poly(ctx, [(-40 * top, -90 + 80 * (1 - top)), (40 * top, -90 + 80 * (1 - top)), (4, -6), (-4, -6)], hexc('#E3C58A'))
    poly(ctx, [(-44, 92), (44, 92), (44 * k * 0.6, 92 - 60 * k), (-44 * k * 0.6, 92 - 60 * k)], hexc('#E3C58A'))
    ctx.restore()


def sc_question(ctx, T, t0):
    setup(ctx, T, expr={1: 'think', 2: 'think', 3: 'think', 4: 'think'})
    card(ctx, T, t0 + 0.05, [('ALSO,', 30, TYPE, P['ink']), ('WER IST ES?', 76, SLAB, P['red'])], 540, 360, -2)
    if T >= nw('schreibt') - 0.1:
        card(ctx, T, nw('schreibt') - 0.1, [("SCHREIB'S IN DIE", 32, SLAB, P['ink']), ('KOMMENTARE', 50, SLAB, P['red'])], 540, 580, 2)
    if T >= GAP_AT:
        hourglass(ctx, 900, 760, clamp((T - GAP_AT) / GAP), pop(T, GAP_AT))


def mini_hats(ctx, cols, x, y, s=0.8, gap=90, labels=None):
    for i, c in enumerate(cols):
        if c is None:
            text(ctx, '?', x + i * gap, y - 20, 50, P['ink'], font=SLAB)
        else:
            shell_hat(ctx, x + i * gap, y, s, c)
        if labels:
            circle(ctx, x + i * gap, y + 34, 16, C['navy'])
            text(ctx, labels[i], x + i * gap, y + 34, 18, C['white'], font=SLAB)


def sc_solution(ctx, T, t0):
    t_name = TW('shelly', 0, after=nw('lösung')) - 0.1
    t_blind = TW('sophia', 0, after=nw('lösung')) - 0.1
    t_b = TW('bleibt') - 0.1
    t_if = TW('während') - 0.1
    t_real = TW('aber', 0, after=nw('während')) - 0.1
    t_silent = TW('schweigt') - 0.2
    ex = {1: 'think' if t_if <= T < t_silent else 'smile'}
    arms = {}
    if T >= t_silent:
        ex[1] = 'smile'
    setup(ctx, T, expr=ex, arms=arms)
    if T < t_b:
        card(ctx, T, t0 + 0.05, [('DIE LÖSUNG', 60, SLAB, P['ink'])], 540, 330, -2)
        if T >= t_name:
            card(ctx, T, t_name, [('NUMMER 2:', 36, TYPE, P['ink']), ('SHELLY', 70, SLAB, P['red'])], 540, 560, 2)
        if T >= t_blind:
            eye_badge(ctx, *above(3, -50, -50), pop(T, t_blind), False)
            eye_badge(ctx, *above(4, 0, -60), pop(T, t_blind + 0.2), False)
        return
    sight(ctx, head(1), hat_pt(2), 1.0)
    sight(ctx, head(1), hat_pt(3), 1.0)
    if T < t_real:
        def d(c):
            text(c, 'ANGENOMMEN:', 0, -80, 26, P['ink'], font=SLAB)
            mini_hats(c, [BLUE if T >= TW('meiner') - 0.1 else None, PINK, PINK], -110, 10, 0.85, 110, ['1', '2', '3'])
            if T >= TW('nur', 0, after=nw('ja') - 1) - 0.1:
                text(c, 'NUR 2 × ROSA', 0, 82, 26, P['red'], font=SLAB)
        thought(ctx, T, t_if, 520, 470, d, 520, 250, tail=head(1))
        if T >= t_b:
            sticker(ctx, 'BLEIBT NR. 1', 200, 700, 36, 'yellow', rot=-3, sc=pop(T, t_b))
    elif T < t_silent:
        def d(c):
            text(c, 'ER SIEHT:', 0, -80, 26, P['ink'], font=SLAB)
            mini_hats(c, [None, PINK, BLUE], -110, 10, 0.85, 110, ['1', '2', '3'])
            text(c, 'BEIDES MÖGLICH', 0, 82, 26, P['red'], font=SLAB)
        thought(ctx, T, t_real, 520, 470, d, 520, 250, tail=head(1))
    else:
        # Schweigen-Blase
        if UI_ON[0]:
            kk = pop(T, t_silent)
            ctx.save()
            ctx.translate(*above(1, 80, -20))
            ctx.scale(kk, kk)
            fill_rrect(ctx, -60, -36, 120, 72, 20, C['white'])
            for i in range(3):
                circle(ctx, -28 + i * 28, 0, 8, P['ink'])
            ctx.restore()
        card(ctx, T, t_silent, [('NR. 1 SCHWEIGT …', 48, SLAB, P['ink'])], 540, 330, -2)


def sc_shelly(ctx, T, t0):
    t_diff = TW('verschieden') - 0.3
    t_blue = TW('sophias', 1) - 0.1
    t_pink = TW('rosa', 0, after=nw('meiner', 1) - 0.5) - 0.2
    sure = T >= t_pink
    setup(ctx, T, expr={2: 'open' if sure else 'think'}, arms={2: (40, -150 + math.sin(T * 8) * 8)} if sure else None)
    sight(ctx, head(2), hat_pt(3), 1.0)

    def d(c):
        text(c, 'NR. 1 SCHWEIGT', 0, -84, 26, P['ink'], font=SLAB)
        if T >= t_diff:
            shell_hat(c, -70, 0, 0.85, PINK if sure else hexc('#B9BFCF'), 0.0 if sure else 1.0)
            text(c, '≠', 0, -14, 60, P['red'], font=SLAB)
            shell_hat(c, 70, 0, 0.85, BLUE if T >= t_blue else hexc('#B9BFCF'), 0.0 if T >= t_blue else 1.0)
            circle(c, -70, 40, 16, C['navy']); text(c, '2', -70, 40, 18, C['white'], font=SLAB)
            circle(c, 70, 40, 16, C['navy']); text(c, '3', 70, 40, 18, C['white'], font=SLAB)
    thought(ctx, T, t0 + 0.1, 560, 470, d, 520, 250, tail=head(2))
    if sure and UI_ON[0]:
        kk = pop(T, t_pink)
        ctx.save()
        ctx.translate(*above(2, 150, -40))
        ctx.scale(kk, kk)
        fill_rrect(ctx, -110, -46, 220, 92, 18, P['paper'])
        shell_hat(ctx, -60, 10, 0.6, PINK)
        text(ctx, 'ROSA!', 30, 0, 40, P['red'], font=SLAB)
        ctx.restore()
        check_icon(ctx, *above(2, 270, -80), 28 * pop(T, t_pink + 0.2))


def sc_end(ctx, T, t0):
    setup(ctx, T)
    card(ctx, T, t0 + 0.05, [('WARUM VERRÄT', 50, SLAB, P['ink']), ('SEIN SCHWEIGEN', 50, SLAB, P['ink']), ('DIE LÖSUNG?', 56, SLAB, P['red'])], 540, 400, -2)


def hut(ctx, T, t0, x, y):
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
    setup(ctx, T, arms={2: (32, -140 + math.sin(T * 8) * 10)})
    card(ctx, T, TW('wohnst') - 0.05, [('WOHNST DU SCHON IN', 34, TYPE, P['ink']), ('MUSCHELTAL?', 80, SLAB, P['ink'])], 540, 360, -2)
    tf = TW('folge') - 0.05
    tap = TW('namen') + 0.3
    if UI_ON[0] and T >= tf:
        k = back_out(T, tf, tf + 0.3, 2.0)
        ctx.save()
        ctx.translate(540, 590)
        ctx.scale(max(k, 0.01), max(k, 0.01))
        on = T >= tap
        fill_rrect(ctx, -170 + 6, -50 + 10, 340, 100, 14, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -170, -50, 340, 100, 14, C['green'] if on else P['red'])
        text(ctx, 'GEFOLGT' if on else 'FOLGEN', -24 if on else 0, 0, 48, C['white'], font=SLAB)
        if on:
            tick_mark(ctx, 120, 0, 34, C['white'])
        ctx.restore()
    hut(ctx, T, TW('hütte') - 0.2, 560, 1420)


def cam_at(T):
    w = WIDE
    k = [(0.0, 330, -560, 1.35), (1.6, 330, -560, 1.35), (3.0, *w),
         (nw('dahinter') - 0.2, *w), (nw('dahinter') + 0.5, 1240, -230, 1.1), (nw('gibt') - 0.1, 1240, -230, 1.1), (nw('gibt') + 0.6, *w),
         (nw('muschelbert') - 0.1, *w), (nw('muschelbert') + 0.6, 600, -300, 0.9), (nw('sieht', 1) - 0.4, 600, -300, 0.9),
         (nw('sieht', 1) + 0.2, 640, -300, 1.0), (nw('sieht', 2) - 0.4, 640, -300, 1.0), (nw('sieht', 2) + 0.2, 1030, -200, 1.2),
         (nw('sieht', 3) - 0.5, 1030, -200, 1.2), (nw('sieht', 3) + 0.1, 1260, -200, 1.2), (nw('umdrehen') - 0.3, 1260, -200, 1.2),
         (nw('umdrehen') + 0.4, *w),
         (TW('bleibt') - 0.2, *w), (TW('bleibt') + 0.5, 640, -260, 0.82), (TW('schweigt') - 0.3, 640, -260, 0.82),
         (TW('schweigt') + 0.3, 300, -620, 1.3), (TW('shelly', 0, after=nw('schweigt')) - 0.2, 300, -620, 1.3),
         (TW('shelly', 0, after=nw('schweigt')) + 0.5, 700, -300, 0.95), (TW('hast') - 0.3, 700, -300, 0.95), (TW('hast') + 0.4, *w)]
    return cam_path(T, k)


SC = [
    ('hook', 0.0, sc_hook),
    ('setup', nw('drei') - 0.1, sc_setup),
    ('view', nw('muschelbert') - 0.1, sc_view),
    ('rules', nw('umdrehen') - 0.1, sc_rules),
    ('question', nw('also') - 0.1, sc_question),
    ('solution', TW('hier') - 0.1, sc_solution),
    ('shelly', TW('shelly', 0, after=nw('schweigt')) - 0.1, sc_shelly),
    ('end', TW('hast') - 0.1, sc_end),
    ('outro', TW('und', 0, after=nw('kommentare', 1)) - 0.1, sc_outro),
]


def frame(ctx, T):
    cur = SC[0]
    for s_ in SC:
        if T >= s_[1]:
            cur = s_
    CAM[0] = cam_at(T)
    cur[2](ctx, T, cur[1])
    for s_ in SC[1:]:
        if 0 <= T - s_[1] < 0.08:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.3 * (1 - (T - s_[1]) / 0.08)))
