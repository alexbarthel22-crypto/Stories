"""Vier Freunde, vier Muschelhüte – Logikrätsel im Retro-Stil (Strandtreppe in Muscheltal)."""
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
POS = {1: (170, 1000), 2: (410, 1180), 3: (640, 1360), 4: (940, 1520)}
HAT = {1: BLUE, 2: PINK, 3: BLUE, 4: PINK}
NAME = {1: 'MUSCHELBERT', 2: 'SHELLY', 3: 'SOPHIA', 4: 'LAURA'}
S = 1.55


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


def draw_person(ctx, i, T, hat_q=None, expr='smile', arms=None):
    x, y = POS[i]
    q = hat_q.get(i, 0.0) if hat_q else 0.0
    if i == 1:
        man(ctx, x, y, S * 1.05, 'bert', face=1, T=T, cap_on=False, arm=arms)
        shell_hat(ctx, x + 2 * S, y - 150 * S * 1.05, S, HAT[i], q)
    else:
        who = {2: 'shelly', 3: 'sophia', 4: 'laura'}[i]
        girl(ctx, who, x, y, S, T, expr, {'R': arms} if arms else None)
        shell_hat(ctx, x + 4 * S, y - 162 * S, S * 1.05, HAT[i], q)
    # Nummer
    circle(ctx, x - 60, y - 120, 22, C['white'])
    circle(ctx, x - 60, y - 120, 18, C['navy'])
    text(ctx, str(i), x - 60, y - 120, 22, C['white'], font=SLAB)


# ---------------------------------------------------------------- Kulisse
def scene_bg(ctx, T, tod='eve'):
    g = cairo.LinearGradient(0, -200, 0, 1000)
    stops = [(0, hexc('#5B4A9A')), (0.55, hexc('#D97BA0')), (1, hexc('#FFC27A'))]
    for o, c in stops:
        g.add_color_stop_rgba(o, *c)
    ctx.rectangle(0, -200, W, 1200)
    ctx.set_source(g)
    ctx.fill()
    circle(ctx, 820, 900, 140, alpha(hexc('#FFE08A'), 0.45))
    circle(ctx, 820, 900, 100, hexc('#FFB45A'))
    for i, (cx, cy, s_) in enumerate([(160, 260, 60), (520, 180, 44), (900, 360, 54)]):
        cloud_shape(ctx, cx + (T * 8 * (1 + i * 0.3)) % 140, cy, s_, alpha(C['white'], 0.7))
    # Muscheltal-Silhouette (Hütten + Leuchtturm)
    for i, (hx, hw, hh) in enumerate([(40, 90, 110), (150, 120, 150), (300, 100, 120), (560, 110, 160), (980, 120, 140)]):
        rect(ctx, hx, 960 - hh, hw, hh, alpha(hexc('#7A5A9A'), 0.6))
        poly(ctx, [(hx - 10, 960 - hh), (hx + hw / 2, 960 - hh - 50), (hx + hw + 10, 960 - hh)], alpha(hexc('#7A5A9A'), 0.6))
    rect(ctx, 700, 640, 50, 320, alpha(hexc('#7A5A9A'), 0.6))
    poly(ctx, [(690, 640), (760, 640), (725, 590)], alpha(hexc('#7A5A9A'), 0.6))
    # Meer
    vgrad(ctx, 0, 960, W, 160, [(0, hexc('#6A5AA0')), (1, hexc('#4A6AA8'))])
    for i in range(16):
        xx = (i * 80 + T * 20) % (W + 80) - 40
        line(ctx, xx, 990 + (i % 3) * 40, xx + 40, 990 + (i % 3) * 40, 3, alpha(C['white'], 0.4))
    # Sand unten
    rect(ctx, 0, 1120, W, H - 1120, hexc('#E9C88E'))


def stairs(ctx):
    # Treppenkörper (Sandstein) von oben links nach unten rechts
    steps = []
    x, y = -40, 1000
    for i in range(9):
        steps.append((x, y))
        x += 80
        y += 60
    poly(ctx, [(-40, 1000)] + [(sx + 80, sy) for sx, sy in steps] + [(steps[-1][0] + 80, H), (-40, H)], hexc('#D8B47A'))
    for sx, sy in steps:
        rect(ctx, sx, sy, 80, 14, hexc('#F0D5A0'))
        rect(ctx, sx + 78, sy, 6, 60, hexc('#B8935A'))
    for yy in range(1040, H, 46):
        line(ctx, -40, yy, 760, yy, 2, alpha(hexc('#B8935A'), 0.4))
    # Geländer
    ctx.move_to(-40, 870)
    ctx.line_to(720, 1410)
    ctx.set_line_width(8)
    src(ctx, hexc('#2F8A86'))
    ctx.stroke()
    for i in range(10):
        px = -20 + i * 80
        py = 870 + (px + 40) * (540 / 760)
        line(ctx, px, py, px, py + 130, 5, hexc('#2F8A86'))
    # Boden unten rechts
    rect(ctx, 680, 1520, 400, 400, hexc('#E3C58A'))


def wall(ctx):
    x0, x1 = 740, 830
    rect(ctx, x0, 620, x1 - x0, 920, hexc('#C9824E'))
    r = random.Random(2)
    for row in range(0, 920 // 34 + 1):
        off = 22 if row % 2 else 0
        for col in range(-1, 3):
            bx = x0 + col * 44 + off
            by = 620 + row * 34
            fill_rrect(ctx, max(x0, bx + 2), by + 2, min(40, x1 - max(x0, bx + 2)), 30, 3, mixc(hexc('#D99460'), hexc('#B56E3E'), r.random() * 0.6))
    rect(ctx, x0 - 10, 600, x1 - x0 + 20, 26, hexc('#E8D2A8'))
    for i in range(6):
        seaweed_v(ctx, x0 + 10 + i * 14, 640 + i * 60)


def seaweed_v(ctx, x, y):
    ctx.move_to(x, y)
    ctx.curve_to(x - 10, y + 30, x + 10, y + 60, x - 4, y + 90)
    ctx.set_line_width(5)
    src(ctx, hexc('#3DAA6A'))
    ctx.stroke()
    ellipse(ctx, x - 6, y + 40, 8, 4, hexc('#3DAA6A'))


def setup(ctx, T, hat_q=None, expr=None, arms=None):
    scene_bg(ctx, T)
    stairs(ctx)
    for i in (1, 2, 3):
        draw_person(ctx, i, T, hat_q, (expr or {}).get(i, 'smile'), (arms or {}).get(i))
    wall(ctx)
    draw_person(ctx, 4, T, hat_q, (expr or {}).get(4, 'smile'), (arms or {}).get(4))


def head(i):
    x, y = POS[i]
    return (x + 14, y - 135 * S) if i != 1 else (x + 22, y - 128 * S * 1.05)


def hat_pt(i):
    x, y = POS[i]
    return (x, y - 185 * S)


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
        sticker(ctx, 'NR. 4 DAHINTER', 900, 1080, 34, 'yellow', rot=3, sc=pop(T, nw('dahinter') - 0.1))
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
            sticker(ctx, 'ROSA', POS[2][0] + 90, POS[2][1] - 290, 34, 'pink', rot=-3, sc=pop(T, nw('rosa', 1) - 0.2))
        if T >= nw('blau', 1) - 0.2:
            sticker(ctx, 'BLAU', POS[3][0] + 90, POS[3][1] - 290, 34, 'blue', rot=3, sc=pop(T, nw('blau', 1) - 0.2))
        eye_badge(ctx, POS[1][0] - 60, POS[1][1] - 300, pop(T, t1))
        card(ctx, T, t0 + 0.05, [('NR. 1 SIEHT', 50, SLAB, P['ink'])], 540, 330, -2)
    else:
        sight(ctx, head(2), hat_pt(3), ease(T, t_s, t_s + 0.5))
        eye_badge(ctx, POS[2][0] - 70, POS[2][1] - 310, pop(T, t_s))
        if T >= t_so:
            sight(ctx, head(3), (735, head(3)[1]), ease(T, t_so, t_so + 0.4), False)
            eye_badge(ctx, POS[3][0] - 70, POS[3][1] - 310, pop(T, t_so), False)
        if T >= t_l:
            eye_badge(ctx, POS[4][0], POS[4][1] - 330, pop(T, t_l), False)
        card(ctx, T, t_s, [('WER SIEHT WAS?', 50, SLAB, P['ink'])], 540, 330, -2)


def sc_rules(ctx, T, t0):
    setup(ctx, T)
    rules_card(ctx, T, t0 + 0.05, 540, 360)
    if T >= nw('nur', 1) - 0.1:
        card(ctx, T, nw('nur', 1) - 0.1, [('NUR WENN', 34, TYPE, P['ink']), ('100 % SICHER', 56, SLAB, hexc('#2F8A4A'))], 540, 790, 2)


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
            eye_badge(ctx, POS[3][0] - 70, POS[3][1] - 310, pop(T, t_blind), False)
            eye_badge(ctx, POS[4][0], POS[4][1] - 330, pop(T, t_blind + 0.2), False)
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
            ctx.translate(POS[1][0] + 90, POS[1][1] - 270)
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
        ctx.translate(POS[2][0] + 160, POS[2][1] - 300)
        ctx.scale(kk, kk)
        fill_rrect(ctx, -110, -46, 220, 92, 18, P['paper'])
        shell_hat(ctx, -60, 10, 0.6, PINK)
        text(ctx, 'ROSA!', 30, 0, 40, P['red'], font=SLAB)
        ctx.restore()
        check_icon(ctx, POS[2][0] + 290, POS[2][1] - 340, 28 * pop(T, t_pink + 0.2))


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
    hut(ctx, T, TW('hütte') - 0.2, 900, 900)


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
    ctx.save()
    ctx.translate(0, 180)
    cur[2](ctx, T, cur[1])
    ctx.restore()
    for s_ in SC[1:]:
        if 0 <= T - s_[1] < 0.08:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.3 * (1 - (T - s_[1]) / 0.08)))
