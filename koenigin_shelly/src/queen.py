"""Königin Shelly und der letzte Satz – Paradoxon-Rätsel im Retro-Stil (Muschelpalast)."""
import json, math, os, random, re
import cairo
from draw import *
from chars import shelly
import retro
from retro import P, SLAB, TYPE, ZILLA
from figs import man

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


def card(ctx, *a, **k):
    ctx.save()
    ctx.identity_matrix()
    retro.paper_card(ctx, *a, **k)
    ctx.restore()


# ---------------------------------------------------------------- Palast
FLOOR = 1500
QUEEN_ROBE = dict(pink=hexc('#B3242A'), pink2=hexc('#8C1C22'))


def palace(ctx, T):
    # Wand: Korallenstein
    rect(ctx, 0, 0, W, FLOOR, hexc('#B86A5A'))
    r = random.Random(1)
    for row in range(0, FLOOR // 46 + 1):
        off = 40 if row % 2 else 0
        for col in range(-1, W // 80 + 2):
            x = col * 80 + off
            y = row * 46
            fill_rrect(ctx, x + 3, y + 3, 74, 40, 4, mixc(hexc('#C77B68'), hexc('#A85E50'), r.random() * 0.6))
    # Rundfenster aufs Meer
    for wx in (180, 900):
        circle(ctx, wx, 360, 120, P['gold'])
        g = cairo.LinearGradient(0, 240, 0, 480)
        g.add_color_stop_rgba(0, *hexc('#7FC8F0'))
        g.add_color_stop_rgba(0.55, *hexc('#BFE8FF'))
        g.add_color_stop_rgba(0.56, *hexc('#3FB6D9'))
        g.add_color_stop_rgba(1, *hexc('#2A8FBF'))
        ctx.new_sub_path()
        ctx.arc(wx, 360, 104, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
        for i in range(4):
            line(ctx, wx - 60 + i * 30 + math.sin(T * 2 + i) * 6, 400 + (i % 2) * 20, wx - 40 + i * 30, 400 + (i % 2) * 20, 3, alpha(C['white'], 0.5))
        line(ctx, wx - 104, 360, wx + 104, 360, 6, P['gold'])
        line(ctx, wx, 256, wx, 464, 6, P['gold'])
    # Banner mit Muschel
    for bx in (60, 360, 680, 980):
        if 300 < bx < 760:
            continue
        poly(ctx, [(bx - 50, 520), (bx + 50, 520), (bx + 50, 880), (bx, 840), (bx - 50, 880)], hexc('#2B4A7A'))
        rect(ctx, bx - 56, 512, 112, 12, P['gold'])
        shellmark(ctx, bx, 640, 1.2, P['gold2'])
    # Laternen
    for lx in (120, 960):
        lamp(ctx, lx, 1180, T)
    # Boden: Muschelfliesen + Teppich
    rect(ctx, 0, FLOOR - 400, W, 1400, hexc('#E3D3B0'))
    for i in range(14):
        for j in range(26):
            x = i * 90 - 40 + (j % 2) * 45
            y = FLOOR - 400 + j * 52
            poly(ctx, [(x, y), (x + 45, y + 26), (x, y + 52), (x - 45, y + 26)], hexc('#D8C49A') if (i + j) % 2 else hexc('#EADBB8'))
    poly(ctx, [(430, FLOOR - 400), (650, FLOOR - 400), (900, FLOOR + 1000), (180, FLOOR + 1000)], P['carpet'])
    for i in range(9):
        y = FLOOR - 360 + i * 140
        shellmark(ctx, 540, y, 0.8 + i * 0.12, P['gold'])
    rect(ctx, 0, FLOOR, W, H - FLOOR, alpha(C['ink'], 0.0))


def shellmark(ctx, x, y, s, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 12)
    for i in range(9):
        a = math.radians(200 + i * 140 / 8)
        ctx.line_to(math.cos(a) * 26, math.sin(a) * 26 + 4)
    ctx.close_path()
    src(ctx, c)
    ctx.fill()
    for i in range(1, 8):
        a = math.radians(200 + i * 140 / 8)
        line(ctx, 0, 10, math.cos(a) * 22, math.sin(a) * 22 + 4, 1.5, alpha(C['ink'], 0.25))
    ctx.restore()


def lamp(ctx, x, y, T):
    g = cairo.RadialGradient(x, y - 260, 5, x, y - 260, 200)
    fl = 0.85 + 0.15 * math.sin(T * 9 + x)
    g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.55 * fl)
    g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
    ctx.arc(x, y - 260, 200, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    line(ctx, x, y, x, y - 220, 10, hexc('#3A2A20'))
    poly(ctx, [(x - 50, y - 220), (x + 50, y - 220), (x + 30, y - 190), (x - 30, y - 190)], hexc('#3A2A20'))
    for k in range(3):
        a = T * 10 + k * 2
        ctx.move_to(x - 30 + k * 30, y - 222)
        ctx.curve_to(x - 34 + k * 30, y - 260 - 10 * math.sin(a), x - 20 + k * 30, y - 270, x - 26 + k * 30, y - 300 - 12 * math.sin(a + 1))
        ctx.curve_to(x - 10 + k * 30, y - 270, x - 16 + k * 30, y - 250, x - 18 + k * 30, y - 222)
        src(ctx, hexc('#FFB45A') if k != 1 else hexc('#FFE08A'))
        ctx.fill()


def throne(ctx, x, y):
    """Riesiger Muschelthron (x = Mitte, y = Sitzfläche)."""
    ctx.save()
    ctx.translate(x, y)
    n = 11
    R = 330
    ctx.move_to(0, 80)
    for i in range(n + 1):
        a = math.radians(195 + 150 * i / n)
        ctx.line_to(math.cos(a) * R, math.sin(a) * R * 1.05)
        if i < n:
            am = math.radians(195 + 150 * (i + 0.5) / n)
            ctx.curve_to(math.cos(am) * R * 1.1, math.sin(am) * R * 1.15, math.cos(am) * R * 1.1, math.sin(am) * R * 1.15,
                         math.cos(a + math.radians(150 / n)) * R, math.sin(a + math.radians(150 / n)) * R * 1.05)
    ctx.close_path()
    src(ctx, hexc('#F7C9D6'))
    ctx.fill_preserve()
    ctx.set_line_width(8)
    src(ctx, P['gold'])
    ctx.stroke()
    for i in range(1, n):
        a = math.radians(195 + 150 * i / n)
        line(ctx, 0, 60, math.cos(a) * R * 0.96, math.sin(a) * R, 4, alpha(hexc('#E28AA6'), 0.9))
    circle(ctx, 0, -R * 1.05 - 10, 22, C['white'])
    circle(ctx, 6, -R * 1.05 - 16, 6, alpha(C['pink3'], 0.8))
    fill_rrect(ctx, -170, 40, 340, 70, 20, P['carpet'])
    rect(ctx, -170, 100, 340, 20, P['gold'])
    for sx in (-200, 200):
        fill_rrect(ctx, sx - 40, -20, 80, 140, 20, P['carpet2'])
        circle(ctx, sx, -30, 22, P['gold'])
    rect(ctx, -230, 120, 460, 40, P['gold'])
    for i in range(4):
        rect(ctx, -250 + i * 0, 160 + i * 36, 500, 36, P['carpet'] if i % 2 == 0 else P['carpet2'])
    ctx.restore()


def crown(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    poly(ctx, [(-30, 0), (-34, -34), (-18, -16), (0, -42), (18, -16), (34, -34), (30, 0)], P['gold2'])
    rect(ctx, -30, -6, 60, 10, P['gold'])
    for dx, c in ((-18, P['red']), (0, hexc('#3FB6D9')), (18, P['red'])):
        circle(ctx, dx, -1, 4, c)
    circle(ctx, 0, -44, 5, C['white'])
    ctx.restore()


def queen(ctx, T, x, y, s=1.35, pose='idle', expr='smile', look=(0, 0)):
    wv = math.sin(T * 7) * 6
    arms = {'idle': {'R': (27, -72), 'L': (-27, -72)}, 'point': {'R': (60, -118), 'L': (-27, -72)},
            'shrug': {'R': (40, -106), 'L': (-40, -106)}, 'think': {'R': (8, -112), 'L': (-27, -72)},
            'wave': {'R': (32, -140 + wv), 'L': (-27, -72)}, 'present': {'R': (46, -96), 'L': (-46, -96)}}[pose]
    old = {k: C[k] for k in QUEEN_ROBE}
    C.update(QUEEN_ROBE)
    try:
        out = shelly(ctx, x, y, s, arms=arms, expr=expr, blink=blink(T), look=look)
    finally:
        C.update(old)
    # Hermelin-Kragen + Krone
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    fill_rrect(ctx, -24, -100, 48, 13, 6, C['white'])
    for i in range(5):
        circle(ctx, -16 + i * 8, -93, 1.6, C['ink'])
    ctx.restore()
    crown(ctx, x, y - 190 * s, s * 0.9)
    # Zepter in der linken Hand
    if 'L' in out:
        hx, hy = out['L']
        line(ctx, hx, hy + 20, hx + 6, hy - 70 * s, 6, P['gold'])
        circle(ctx, hx + 6, hy - 76 * s, 12, hexc('#3FB6D9'))
    return out


def guard(ctx, x, y, s, T, face=1):
    """Krabben-Wache: Mensch mit Krabbenhelm und Dreizack."""
    man(ctx, x, y, s, 'officer', face=face, T=T)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * face, s)
    ellipse(ctx, 2, -150, 30, 14, hexc('#E8553E'))
    for sx in (-14, 14):
        line(ctx, sx, -158, sx + 3, -176, 4, hexc('#C43E2C'))
        circle(ctx, sx + 3, -180, 6, C['white'])
        circle(ctx, sx + 4, -180, 3, C['ink'])
    line(ctx, -26, -50, -26, -230, 6, hexc('#6E4630'))
    poly(ctx, [(-40, -230), (-12, -230), (-12, -246), (-18, -238), (-26, -256), (-34, -238), (-40, -246)], P['gold2'])
    ctx.restore()


def prisoner(ctx, x, y, s, T, expr=1, free=False):
    man(ctx, x, y, s, 'bert', face=-1, T=T, smile=expr, wave=1.0 if free else 0.0)
    if not free:
        # Seil um die Handgelenke (jugendfreundlich: Tau)
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(-s, s)
        for i in range(3):
            ellipse(ctx, 0, -60 + i * 6, 26, 5, hexc('#C9A86A'))
        ctx.restore()


def court(ctx, T):
    """Hofstaat links/rechts (kleine Figuren hinter Brüstung)."""
    r = random.Random(4)
    for side, xs in ((-1, (40, 110, 180)), (1, (900, 970, 1040))):
        for i, x in enumerate(xs):
            retro.figure(ctx, x, FLOOR - 300, 1.0, 20 + i + (0 if side < 0 else 5), 'travel', face=-side * 0.5)
        rect(ctx, xs[0] - 50, FLOOR - 330, 240, 90, P['carpet2'])
        rect(ctx, xs[0] - 50, FLOOR - 334, 240, 10, P['gold'])
        for k in range(3):
            shellmark(ctx, xs[0] + 20 + k * 70, FLOOR - 285, 0.6, P['gold2'])


def hall(ctx, T, zoom=1.0, cy=1100, queen_pose='idle', queen_expr='smile', pris_expr=1, free=False, pris_x=540, actors=()):
    ctx.save()
    ctx.translate(540, cy)
    ctx.scale(zoom, zoom)
    ctx.translate(-540, -1100)
    palace(ctx, T)
    throne(ctx, 540, 900)
    queen(ctx, T, 540, 1010, 1.85, queen_pose, queen_expr)
    court(ctx, T)
    guard(ctx, 250, FLOOR + 230, 2.2, T, 1)
    guard(ctx, 830, FLOOR + 230, 2.2, T, -1)
    prisoner(ctx, pris_x, FLOOR + 330, 2.5, T, pris_expr, free)
    for a in actors:
        a(ctx)
    ctx.restore()


# ---------------------------------------------------------------- Icons für die zwei Strafen
def icon_kerker(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    fill_rrect(ctx, -50, -60, 100, 110, 8, hexc('#5A5A66'))
    rect(ctx, -40, -50, 80, 90, hexc('#2B2B33'))
    for i in range(5):
        line(ctx, -32 + i * 16, -50, -32 + i * 16, 40, 5, hexc('#9AA0AE'))
    line(ctx, -40, -10, 40, -10, 5, hexc('#9AA0AE'))
    shellmark(ctx, 0, -62, 0.6, C['pink3'])
    ctx.restore()


def icon_island(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 30, 60, 16, hexc('#3FB6D9'))
    ellipse(ctx, 0, 22, 40, 12, hexc('#F3D9A4'))
    line(ctx, -4, 20, 6, -40, 5, hexc('#A9744A'))
    for a in range(5):
        aa = math.radians(-160 + a * 35)
        line(ctx, 6, -40, 6 + math.cos(aa) * 32, -40 + math.sin(aa) * 14 + 10, 5, hexc('#3DAA6A'))
    ctx.restore()


def rule_cards(ctx, T, t1, t2, x1=290, x2=790, y=380, mark1=None, mark2=None):
    for (tt, x, title, icon, word, rot, mark) in ((t1, x1, 'WENN WAHR', icon_kerker, 'KERKER', -3, mark1),
                                                   (t2, x2, 'WENN GELOGEN', icon_island, 'INSEL', 3, mark2)):
        if T < tt or not UI_ON[0]:
            continue
        k = back_out(T, tt, tt + 0.3, 1.8)
        ctx.save()
        ctx.identity_matrix()
        ctx.translate(x, y)
        ctx.rotate(math.radians(rot + math.sin(T * 1.3 + x) * 0.5))
        ctx.scale(k, k)
        fill_rrect(ctx, -170 + 8, -150 + 12, 340, 300, 6, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -170, -150, 340, 300, 6, P['paper'])
        text(ctx, title, 0, -118, 26, P['ink'], font=TYPE)
        icon(ctx, 0, -10, 1.3)
        text(ctx, word, 0, 100, 46, P['red'], font=SLAB)
        if mark:
            mt, ok = mark
            if T >= mt:
                kk = back_out(T, mt, mt + 0.25, 2.0)
                ctx.save()
                ctx.translate(110, -120)
                ctx.scale(kk, kk)
                if ok:
                    check_icon(ctx, 0, 0, 32)
                else:
                    circle(ctx, 0, 0, 32, C['white'])
                    cross_icon(ctx, 0, 0, 15)
                ctx.restore()
        ctx.restore()


def scroll(ctx, T, t0, s, sub, x=540, y=380, crack=0.0, seal=0.0):
    if T < t0 or not UI_ON[0]:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    ctx.save()
    ctx.identity_matrix()
    ctx.translate(x, y)
    ctx.scale(k, k)
    w, h = 640, 190
    fill_rrect(ctx, -w / 2 + 8, -h / 2 + 12, w, h, 10, alpha(C['shadow'], 0.35))
    fill_rrect(ctx, -w / 2, -h / 2, w, h, 10, hexc('#F1E2BE'))
    for sx in (-1, 1):
        fill_rrect(ctx, sx * w / 2 - 18, -h / 2 - 10, 36, h + 20, 18, hexc('#D9C08A'))
    text(ctx, s, 0, -20, 74, P['red'], font=SLAB)
    text(ctx, sub, 0, 50, 30, P['ink'], font=TYPE)
    if crack > 0:
        ctx.move_to(-20, -h / 2)
        pts = [(0, -60), (-18, -30), (8, 0), (-10, 30), (12, h / 2)]
        m = int(len(pts) * crack)
        for p in pts[:max(1, m)]:
            ctx.line_to(*p)
        ctx.set_line_width(5)
        src(ctx, C['ink'])
        ctx.stroke()
    if seal > 0:
        ctx.save()
        ctx.translate(w / 2 - 70, h / 2 - 30)
        ctx.scale(seal, seal)
        circle(ctx, 0, 0, 34, P['red'])
        shellmark(ctx, 0, 4, 0.8, mixc(P['red'], C['white'], 0.35))
        ctx.restore()
    ctx.restore()


def speech(ctx, T, t0, lines, x, y, tail, tag=None):
    """Zettel-Sprechblase mit Zitat; tag = ('WAHR'/'FALSCH', t)."""
    if T < t0 or not UI_ON[0]:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    ctx.save()
    ctx.identity_matrix()
    ctx.translate(x, y)
    ctx.scale(k, k)
    w, h = 560, 70 + 70 * len(lines)
    poly(ctx, [(-30, h / 2 - 4), (30, h / 2 - 4), (tail[0] - x, tail[1] - y)], P['paper'])
    fill_rrect(ctx, -w / 2 + 8, -h / 2 + 12, w, h, 6, alpha(C['shadow'], 0.3))
    fill_rrect(ctx, -w / 2, -h / 2, w, h, 6, P['paper'])
    for i, (s_, col) in enumerate(lines):
        text(ctx, s_, 0, -h / 2 + 60 + i * 70, 54, col, font=SLAB)
    if tag:
        word, tt, ok = tag
        if T >= tt:
            kk = back_out(T, tt, tt + 0.25, 2.0)
            ctx.save()
            ctx.translate(120, h / 2 - 6)
            ctx.rotate(-0.08)
            ctx.scale(kk, kk)
            col = C['green'] if ok else P['red']
            tw = text_size(ctx, word, 36, SLAB)[0]
            rrect(ctx, -tw / 2 - 16, -28, tw + 32, 56, 8)
            src(ctx, P['paper'])
            ctx.fill_preserve()
            ctx.set_line_width(5)
            src(ctx, col)
            ctx.stroke()
            text(ctx, word, 0, 0, 36, col, font=SLAB)
            ctx.restore()
    ctx.restore()


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
    line(ctx, 0, -4, 0, 90, 3, hexc('#E3C58A'))
    ctx.restore()


def loop_card(ctx, T, t0, x=540, y=760):
    """Paradoxon: Satz in einem Kreis aus zwei Pfeilen (wahr -> falsch -> wahr …)."""
    if T < t0 or not UI_ON[0]:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    ctx.save()
    ctx.identity_matrix()
    ctx.translate(x, y)
    ctx.scale(k, k)
    fill_rrect(ctx, -260 + 8, -300 + 12, 520, 600, 6, alpha(C['shadow'], 0.35))
    fill_rrect(ctx, -260, -300, 520, 600, 6, P['paper'])
    text(ctx, 'PARADOXON', 0, -240, 64, P['ink'], font=SLAB)
    rot = T * 1.5
    for i, col in enumerate((C['green'], P['red'])):
        a0 = rot + i * math.pi
        ctx.new_sub_path()
        ctx.arc(0, 40, 170, a0, a0 + math.pi * 0.85)
        ctx.set_line_width(26)
        src(ctx, col)
        ctx.stroke()
        a1 = a0 + math.pi * 0.85
        ex, ey = math.cos(a1) * 170, 40 + math.sin(a1) * 170
        tx, ty = -math.sin(a1), math.cos(a1)
        poly(ctx, [(ex + tx * 30, ey + ty * 30), (ex - ty * 26 * -1 + math.cos(a1) * 26, ey + math.sin(a1) * 26),
                   (ex - math.cos(a1) * 26, ey - math.sin(a1) * 26)], col)
    text(ctx, '„ICH WERDE AUF', 0, 10, 30, P['ink'], font=SLAB)
    text(ctx, 'DIE INSEL', 0, 50, 30, P['red'], font=SLAB)
    text(ctx, 'VERBANNT.“', 0, 90, 30, P['red'], font=SLAB)
    ctx.restore()


# ---------------------------------------------------------------- Szenen
def sc_hook(ctx, T, t0):
    z = lerp(1.6, 1.15, ease(T, 0, 3.0))
    hall(ctx, T, z, 1250, 'point', 'smile')
    card(ctx, T, nw('einzigen') - 0.1, [('NUR', 30, TYPE, P['ink']), ('EIN EINZIGER SATZ', 58, SLAB, P['red'])], 540, 420, -2)


def sc_caught(ctx, T, t0):
    z = lerp(1.0, 1.1, ease(T, t0, t0 + 4))
    hall(ctx, T, z, 1100, 'idle', 'smile', pris_expr=0)
    scroll(ctx, T, nw('erwischt') - 0.3, 'ERWISCHT!', 'MUSCHELBERT, DER SCHMUGGLER', 540, 380, seal=pop(T, nw('erwischt') + 0.2))
    if UI_ON[0]:
        sticker(ctx, 'KÖNIGIN SHELLY', 540, 640, 40, 'yellow', rot=-2, sc=pop(T, nw('königin', 1) - 0.05))


def sc_rules(ctx, T, t0):
    hall(ctx, T, 1.0, 1100, 'point', 'smile', pris_expr=0)
    rule_cards(ctx, T, nw('wahrheit') - 0.2, nw('lügter') - 0.2)
    if T >= nw('kerker') - 0.1:
        card(ctx, T, nw('kerker') - 0.1, [('KERKER ODER INSEL?', 50, SLAB, P['ink']), ('FREIHEIT WEG', 34, TYPE, P['red'])], 540, 700, 2)


def sc_word(ctx, T, t0):
    hall(ctx, T, 1.08, 1100, 'present', 'smile', pris_expr=0)
    scroll(ctx, T, t0 + 0.05, 'WORT', 'DER KÖNIGIN', 540, 380, seal=pop(T, nw('wort') + 0.2))
    if T >= nw('minute') - 0.4:
        hourglass(ctx, 900, 820, clamp((T - nw('minute') + 0.4) / 6), pop(T, nw('minute') - 0.4))
    if T >= nw('fragen') - 0.2:
        card(ctx, T, nw('fragen') - 0.2, [('KEINE FRAGEN', 40, SLAB, P['ink']), ('KEIN TRICK', 40, SLAB, P['ink']),
                                          ('1 SATZ', 66, SLAB, P['red'])], 300, 760, -3)


def sc_says(ctx, T, t0):
    free = T >= nw('freilassen') - 0.4
    hall(ctx, T, 1.0, 1100, 'shrug' if free else 'idle', 'o' if free else 'smile', pris_expr=1)
    speech(ctx, T, t0 + 0.2, [('„ … “', P['ink'])], 760, 1000, (620, 1420))
    if T >= nw('freilassen') - 0.4:
        card(ctx, T, nw('freilassen') - 0.4, [('UND SIE MUSS IHN', 34, TYPE, P['ink']), ('FREILASSEN!', 66, SLAB, P['red'])], 540, 400, -2)


def sc_question(ctx, T, t0):
    hall(ctx, T, 1.0, 1100, 'think', 'think', pris_expr=1)
    card(ctx, T, t0 + 0.05, [('ALSO,', 30, TYPE, P['ink']), ('WAS HAT ER', 60, SLAB, P['ink']), ('GESAGT?', 72, SLAB, P['red'])], 540, 420, -2)
    if T >= nw('schreib') - 0.05:
        card(ctx, T, nw('schreib') - 0.05, [('IN DIE KOMMENTARE!', 34, SLAB, P['red'])], 540, 660, 2)
    if T >= GAP_AT:
        hourglass(ctx, 880, 900, clamp((T - GAP_AT) / GAP), pop(T, GAP_AT))


Q_LINES = [('„ICH WERDE AUF', P['ink']), ('DIE INSEL', P['red']), ('VERBANNT.“', P['red'])]


def sc_answer(ctx, T, t0):
    hall(ctx, T, 1.0, 1100, 'idle', 'smile', pris_expr=1)
    if T < TW('sein') - 0.1:
        card(ctx, T, t0 + 0.05, [('DIE LÖSUNG', 76, SLAB, P['ink'])], 540, 420, -2)
    speech(ctx, T, TW('ich', 0, after=nw('lösung')) - 0.2, Q_LINES, 600, 470, (620, 1420))


def sc_trap(ctx, T, t0):
    z = lerp(1.0, 1.5, ease(T, t0, t0 + 1.2))
    hall(ctx, T, z, 1150, 'shrug', 'o', pris_expr=1)
    speech(ctx, T, -1, Q_LINES, 600, 380, (640, 900))
    card(ctx, T, t0 + 0.2, [('DIE KÖNIGIN', 40, SLAB, P['ink']), ('IN DER FALLE', 60, SLAB, P['red'])], 540, 1460, 2)


def sc_case1(ctx, T, t0):
    """Insel -> Satz wahr -> hätte Kerker sein müssen."""
    def act(c):
        k = ease(T, t0 + 0.2, t0 + 1.0)
        icon_island(c, lerp(540, 860, k), 1550, 2.6 * k + 0.01)
    hall(ctx, T, 1.0, 1100, 'point', 'o', pris_expr=1, actors=[act])
    speech(ctx, T, -1, Q_LINES, 600, 380, (620, 1420), tag=('WAHR', TW('wahr', 0, after=nw('verbannt', 2)) - 0.1, True))
    rule_cards(ctx, T, TW('dann') - 0.2, 1e9, 290, 790, 860, mark1=(TW('kerker', 0, after=nw('dann')) - 0.1, False))


def sc_case2(ctx, T, t0):
    def act(c):
        k = ease(T, t0 + 0.2, t0 + 1.0)
        icon_kerker(c, lerp(540, 220, k), 1560, 2.6 * k + 0.01)
    hall(ctx, T, 1.0, 1100, 'point', 'o', pris_expr=1, actors=[act])
    speech(ctx, T, -1, Q_LINES, 600, 380, (620, 1420), tag=('FALSCH', TW('falsch') - 0.1, False))
    rule_cards(ctx, T, 1e9, TW('dann', 1) - 0.2, 290, 790, 860, mark2=(TW('insel', 0, after=nw('dann', 1)) - 0.1, False))


def sc_word_broken(ctx, T, t0):
    hall(ctx, T, 1.0, 1100, 'shrug', 'o', pris_expr=1)
    t_br = TW('brechen') - 0.2
    scroll(ctx, T, t0 + 0.05, 'WORT', 'DER KÖNIGIN', 540, 380, crack=ease(T, t_br, t_br + 0.5))
    card(ctx, T, t0 + 0.2, [('KEINE STRAFE', 50, SLAB, P['ink']), ('PASST ZUR REGEL', 40, SLAB, P['red'])], 540, 650, 2)


def sc_free(ctx, T, t0):
    hall(ctx, T, 1.0, 1100, 'wave', 'open', pris_expr=1, free=T >= TW('frei') - 0.3)
    scroll(ctx, T, t0 + 0.05, 'WORT', 'DER KÖNIGIN', 540, 380, seal=pop(T, TW('frei') - 0.2))
    if T >= TW('frei') - 0.2:
        card(ctx, T, TW('frei') - 0.2, [('FREI!', 90, SLAB, hexc('#2F8A4A'))], 540, 650, 3)


def sc_paradox(ctx, T, t0):
    hall(ctx, T, 1.0, 1100, 'think', 'think', pris_expr=1)
    loop_card(ctx, T, t0 + 0.05, 540, 760)
    if T >= TW('widerspricht') - 0.3:
        card(ctx, T, TW('widerspricht') - 0.3, [('EIN SATZ, DER SICH', 30, TYPE, P['ink']), ('SELBST WIDERSPRICHT', 44, SLAB, P['red'])], 540, 1200, 2)


def sc_you(ctx, T, t0):
    hall(ctx, T, 1.0, 1100, 'point', 'smile', pris_expr=1)
    card(ctx, T, t0 + 0.05, [('UND DU,', 30, TYPE, P['ink']), ('WAS HÄTTEST', 58, SLAB, P['ink']), ('DU GESAGT?', 66, SLAB, P['red'])], 540, 420, -2)
    if T >= TW('schreib', 0, after=nw('gefunden')) - 0.1:
        card(ctx, T, TW('schreib', 0, after=nw('gefunden')) - 0.1, [('IN DIE KOMMENTARE!', 34, SLAB, P['red'])], 540, 660, 2)


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
    hall(ctx, T, 1.0, 1100, 'wave', 'open', pris_expr=1, free=True)
    card(ctx, T, TW('muscheltal') - 0.5, [('WOHNST DU SCHON IN', 34, TYPE, P['ink']), ('MUSCHELTAL?', 80, SLAB, P['ink'])], 540, 420, -2)
    tf = TW('folge') - 0.05
    tap = TW('namen') + 0.3
    if UI_ON[0] and T >= tf:
        k = back_out(T, tf, tf + 0.3, 2.0)
        ctx.save()
        ctx.translate(540, 650)
        ctx.scale(max(k, 0.01), max(k, 0.01))
        on = T >= tap
        fill_rrect(ctx, -170 + 6, -50 + 10, 340, 100, 14, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -170, -50, 340, 100, 14, C['green'] if on else P['red'])
        text(ctx, 'GEFOLGT' if on else 'FOLGEN', -24 if on else 0, 0, 48, C['white'], font=SLAB)
        if on:
            tick_mark(ctx, 120, 0, 34, C['white'])
        ctx.restore()
    hut(ctx, T, TW('hütte') - 0.2, 850, 1000)


# ---------------------------------------------------------------- Zeitleiste
SC = [
    ('hook', 0.0, sc_hook),
    ('caught', nw('muschelbert') - 0.1, sc_caught),
    ('rules', nw('sagt') - 0.1, sc_rules),
    ('word', nw('königin', 2) - 0.1, sc_word),
    ('says', nw('muschelbert', 1) - 0.1, sc_says),
    ('question', nw('was') - 0.1, sc_question),
    ('answer', TW('hier') - 0.1, sc_answer),
    ('trap', TW('und', 0, after=nw('verbannt', 1) + 0.1) - 0.1, sc_trap),
    ('case1', TW('wenn') - 0.1, sc_case1),
    ('case2', TW('wenn', 1) - 0.1, sc_case2),
    ('broken', TW('keine', 1) - 0.1, sc_word_broken),
    ('free', TW('königin', 5) - 0.1, sc_free),
    ('paradox', TW('so', 0, after=nw('frei')) - 0.1, sc_paradox),
    ('you', TW('und', 0, after=nw('widerspricht')) - 0.1, sc_you),
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
