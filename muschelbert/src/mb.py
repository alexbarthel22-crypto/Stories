"""Muschelbert, der Schmuggler – Rätsel im Retro-Stil an der Strandgrenze."""
import json, math, os, random, re
import cairo
from draw import *
from chars import shelly
import retro
from retro import P, SLAB, TYPE, ZILLA

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = json.load(open(f'{ROOT}/audio/vo_words.json'))


def _norm(w):
    w = re.sub(r"[^\wäöüß']", '', w.lower()).replace('ß', 'ss')
    return {'20': 'zwanzig', '7000': 'siebentausend'}.get(w, w)


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


def paper_card(ctx, *a, **k):
    ctx.save()
    ctx.identity_matrix()
    retro.paper_card(ctx, *a, **k)
    ctx.restore()


# ---------------------------------------------------------------- Figuren
def man(ctx, x, y, s, kind='bert', walk=None, face=1, wave=0.0, gray=0.0, smile=1, T=0.0, sit=False, arm=None):
    """kind: bert (Matrosenhemd, rote Kappe mit Muschel, Schnurrbart) | officer (Zolluniform, Mütze)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * face, s)
    skin = hexc('#F2C6A0')
    if kind == 'bert':
        shirt, pants, cap = C['white'], hexc('#2B4A7A'), hexc('#C8322E')
        hair = hexc('#6E3820')
    else:
        shirt, pants, cap = hexc('#2A3A6A'), hexc('#22305A'), hexc('#22305A')
        hair = mixc(hexc('#3A2A20'), hexc('#D8D8D8'), gray)
    ellipse(ctx, 0, 0, 26, 5, alpha(C['shadow'], 0.22))
    lg = math.sin(walk) * 0.45 if walk is not None else 0.0
    if not sit:
        for side, l in ((-1, lg), (1, -lg)):
            fx = side * 7 + math.sin(l) * 18
            line(ctx, side * 7, -46, fx, -5, 11, pants)
            ellipse(ctx, fx + 4, -3, 11, 5, hexc('#2B2B33'))
    # Oberkörper
    ctx.save()
    rrect(ctx, -19, -102, 38, 60, 12)
    ctx.clip()
    rect(ctx, -19, -102, 38, 60, shirt)
    if kind == 'bert':
        for i in range(6):
            rect(ctx, -19, -96 + i * 10, 38, 4, hexc('#2B4A7A'))
    else:
        line(ctx, 0, -100, 0, -44, 2, alpha(C['white'], 0.3))
        for i in range(3):
            circle(ctx, 0, -88 + i * 13, 2.2, P['gold'])
        star = [(10 + 5 * math.cos(a), -84 + 5 * math.sin(a)) for a in [i * math.pi * 2 / 5 - math.pi / 2 for i in range(5)]]
        circle(ctx, 10, -84, 5, P['gold'])
    rect(ctx, 8, -102, 11, 60, alpha(C['ink'], 0.08))
    ctx.restore()
    if kind == 'officer':
        rect(ctx, -19, -50, 38, 6, hexc('#1A1A22'))
        rect(ctx, -3, -50, 6, 6, P['gold'])
    # Arme
    for side in (-1, 1):
        sx, sy = side * 16, -96
        if side == 1 and wave > 0:
            tx, ty = 26, -150 + math.sin(T * 10) * 8
        elif side == 1 and arm is not None:
            tx, ty = arm
        else:
            tx, ty = side * 22, -54 + (math.sin(walk + side) * 4 if walk is not None else 0)
        line(ctx, sx, sy, tx, ty, 9, shirt if kind == 'officer' else hexc('#2B4A7A'))
        circle(ctx, tx, ty + 2, 5, skin)
    # Kopf
    rect(ctx, -4, -110, 8, 10, mixc(skin, C['ink'], 0.12))
    circle(ctx, 2, -128, 20, skin)
    circle(ctx, 20, -126, 4, mixc(skin, C['ink'], 0.08))
    ellipse(ctx, 22, -124, 6, 5, skin)  # Nase
    circle(ctx, 22, -124, 5, mixc(skin, hexc('#E07A6A'), 0.35))
    ellipse(ctx, 10, -134, 2.4, 3.2, C['ink'])
    line(ctx, 6, -141, 13, -142, 2, mixc(hair, C['ink'], 0.2))
    # Schnurrbart
    ctx.move_to(8, -118)
    ctx.curve_to(14, -121, 22, -121, 28, -117)
    ctx.curve_to(22, -113, 14, -113, 8, -118)
    src(ctx, hair if kind == 'officer' else hexc('#6E3820'))
    ctx.fill()
    if smile:
        ctx.move_to(10, -110)
        ctx.curve_to(14, -106, 18, -106, 22, -110)
        ctx.set_line_width(1.8)
        src(ctx, hexc('#8A3B3B'))
        ctx.stroke()
    ctx.new_path()
    ctx.arc(2, -130, 21, math.radians(150), math.radians(260))
    ctx.line_to(-6, -128)
    ctx.close_path()
    src(ctx, hair)
    ctx.fill()
    # Kopfbedeckung
    if kind == 'bert':
        ctx.new_sub_path()
        ctx.arc(2, -136, 21, math.pi, 2 * math.pi)
        ctx.close_path()
        src(ctx, cap)
        ctx.fill()
        fill_rrect(ctx, 6, -140, 30, 7, 3, mixc(cap, C['ink'], 0.25))
        ctx.save()
        ctx.translate(0, -148)
        ctx.scale(0.35, 0.35)
        ctx.move_to(0, 10)
        for i in range(7):
            a = math.radians(200 + i * 140 / 6)
            ctx.line_to(math.cos(a) * 22, math.sin(a) * 22 + 4)
        ctx.close_path()
        src(ctx, C['pink3'])
        ctx.fill()
        ctx.restore()
    else:
        rect(ctx, -18, -152, 40, 16, cap)
        poly(ctx, [(-22, -152), (26, -152), (20, -162), (-16, -162)], cap)
        fill_rrect(ctx, 4, -140, 28, 6, 3, hexc('#111122'))
        circle(ctx, 2, -146, 4, P['gold'])
    ctx.restore()


def bicycle(ctx, x, y, s, T=0.0, moving=False, col=None, sacks=2, glow=0.0, rider=None):
    """Fahrrad nach rechts, Bodenlinie y. rider(ctx) zeichnet Fahrer in lokalen Koordinaten."""
    col = col or hexc('#C8322E')
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if glow > 0:
        g = cairo.RadialGradient(0, -60, 10, 0, -60, 160)
        g.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.7 * glow)
        g.add_color_stop_rgba(1, 1, 0.95, 0.6, 0)
        ctx.arc(0, -60, 160, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
    ellipse(ctx, 0, 0, 90, 6, alpha(C['shadow'], 0.2))
    rot = T * 8 if moving else 0.0
    for wx in (-55, 55):
        ctx.new_sub_path()
        ctx.arc(wx, -32, 30, 0, 2 * math.pi)
        ctx.set_line_width(6)
        src(ctx, hexc('#2B2B33'))
        ctx.stroke()
        for i in range(6):
            a = rot + i * math.pi / 3
            line(ctx, wx, -32, wx + math.cos(a) * 27, -32 + math.sin(a) * 27, 1.5, alpha(C['ink'], 0.6))
        circle(ctx, wx, -32, 4, P['gold'])
    pts = [(-55, -32), (-10, -32), (35, -82), (-20, -82)]
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0), (3, 1)):
        line(ctx, pts[a][0], pts[a][1], pts[b][0], pts[b][1], 6, col)
    line(ctx, 35, -82, 55, -32, 6, col)
    line(ctx, 32, -82, 40, -100, 5, hexc('#2B2B33'))
    line(ctx, 30, -100, 52, -100, 5, hexc('#2B2B33'))
    line(ctx, -20, -82, -24, -94, 5, hexc('#2B2B33'))
    fill_rrect(ctx, -38, -100, 30, 8, 4, hexc('#2B2B33'))
    # Gepäckträger + Sandsäcke
    line(ctx, -58, -70, -20, -70, 4, hexc('#2B2B33'))
    if sacks >= 1:
        sack(ctx, -48, -72, 1.0)
    if sacks >= 2:
        sack(ctx, 64, -84, 0.9)
    if rider:
        rider(ctx)
    ctx.restore()


def sack(ctx, x, y, s=1.0, label=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-26, 0)
    ctx.curve_to(-30, -30, -18, -48, -8, -50)
    ctx.line_to(8, -50)
    ctx.curve_to(18, -48, 30, -30, 26, 0)
    ctx.close_path()
    src(ctx, hexc('#C9A86A'))
    ctx.fill()
    line(ctx, -10, -50, 10, -50, 5, hexc('#8E6238'))
    if label:
        text(ctx, 'SAND', 0, -22, 11, hexc('#5A3824'), font=SLAB)
    ctx.restore()


def booth(ctx, x, y, T, flag=True):
    """Zollhäuschen (x = Mitte, y = Boden)."""
    rect(ctx, x - 130, y - 330, 260, 330, hexc('#F4F1EA'))
    for i in range(12):
        line(ctx, x - 130, y - 320 + i * 27, x + 130, y - 320 + i * 27, 2, alpha(hexc('#C9C3BC'), 0.6))
    poly(ctx, [(x - 160, y - 330), (x + 160, y - 330), (x + 140, y - 370), (x - 140, y - 370)], hexc('#2B4A7A'))
    fill_rrect(ctx, x - 110, y - 430, 220, 64, 6, C['white'])
    rrect(ctx, x - 110, y - 430, 220, 64, 6)
    ctx.set_line_width(5)
    src(ctx, hexc('#2B4A7A'))
    ctx.stroke()
    text(ctx, 'ZOLL', x, y - 398, 46, hexc('#2B4A7A'), font=SLAB)
    fill_rrect(ctx, x - 100, y - 280, 110, 110, 4, hexc('#2B4A7A'))
    rect(ctx, x - 92, y - 272, 94, 94, hexc('#9FC6E8'))
    line(ctx, x - 45, y - 272, x - 45, y - 178, 4, hexc('#2B4A7A'))
    line(ctx, x - 92, y - 225, x + 2, y - 225, 4, hexc('#2B4A7A'))
    rect(ctx, x + 30, y - 240, 70, 240, hexc('#2B4A7A'))
    circle(ctx, x + 88, y - 120, 5, P['gold'])
    if flag:
        line(ctx, x + 170, y, x + 170, y - 520, 5, hexc('#8A93A6'))
        wv = math.sin(T * 4) * 6
        ctx.move_to(x + 172, y - 515)
        ctx.curve_to(x + 210, y - 525 + wv, x + 240, y - 505 - wv, x + 272, y - 512)
        ctx.line_to(x + 272, y - 452)
        ctx.curve_to(x + 240, y - 445 - wv, x + 210, y - 465 + wv, x + 172, y - 455)
        ctx.close_path()
        src(ctx, hexc('#3FB6D9'))
        ctx.fill()
        ctx.save()
        ctx.translate(x + 222, y - 482)
        ctx.scale(0.7, 0.7)
        ctx.move_to(0, 10)
        for i in range(7):
            a = math.radians(200 + i * 140 / 6)
            ctx.line_to(math.cos(a) * 24, math.sin(a) * 24 + 4)
        ctx.close_path()
        src(ctx, C['white'])
        ctx.fill()
        ctx.restore()


def barrier(ctx, x, y, up=0.0):
    rect(ctx, x - 12, y - 120, 24, 120, hexc('#3A3F4F'))
    ang = -up * math.pi / 2.4
    ctx.save()
    ctx.translate(x, y - 100)
    ctx.rotate(ang)
    for i in range(8):
        rect(ctx, i * 40, -9, 40, 18, P['red'] if i % 2 == 0 else C['white'])
    ctx.restore()


def table(ctx, x, y, sand=0.0):
    rect(ctx, x - 150, y - 110, 300, 18, P['wood2'])
    rect(ctx, x - 140, y - 92, 14, 92, P['wood3'])
    rect(ctx, x + 126, y - 92, 14, 92, P['wood3'])
    if sand > 0:
        for i, dx in enumerate((-70, 60)):
            h = 50 * sand
            ctx.move_to(x + dx - 70, y - 110)
            ctx.curve_to(x + dx - 40, y - 110 - h, x + dx + 40, y - 110 - h, x + dx + 70, y - 110)
            ctx.close_path()
            src(ctx, hexc('#E3C58A'))
            ctx.fill()


def beach_bg(ctx, T, tod='day', road_y=1320):
    sky = {'day': [(0, hexc('#5DB8F0')), (1, hexc('#CFEFFF'))], 'eve': [(0, hexc('#3B3A7A')), (0.6, hexc('#D97BA0')), (1, hexc('#F7B47A'))],
           'morning': [(0, hexc('#7FC8F0')), (1, hexc('#FFE3B0'))]}[tod]
    g = cairo.LinearGradient(0, 0, 0, 900)
    for o, c in sky:
        g.add_color_stop_rgba(o, *c)
    ctx.rectangle(0, 0, W, 900)
    ctx.set_source(g)
    ctx.fill()
    if tod == 'eve':
        circle(ctx, 820, 760, 110, alpha(hexc('#FFD27A'), 0.4))
        circle(ctx, 820, 760, 80, hexc('#FFB45A'))
    else:
        circle(ctx, 860, 260, 90, alpha(C['white'], 0.35))
        circle(ctx, 860, 260, 64, hexc('#FFF2B0'))
    for i, (cx, cy, s_) in enumerate([(160, 220, 60), (520, 160, 44), (980, 420, 50)]):
        cloud_shape(ctx, cx + (T * 8 * (1 + i * 0.3)) % 140, cy, s_, alpha(C['white'], 0.9 if tod != 'eve' else 0.5))
    # Meer
    vgrad(ctx, 0, 800, W, 220, [(0, hexc('#3FB6D9') if tod != 'eve' else hexc('#5B5A9A')), (1, hexc('#2A8FBF') if tod != 'eve' else hexc('#3B4A80'))])
    for i in range(16):
        xx = (i * 80 + T * 25) % (W + 80) - 40
        line(ctx, xx, 830 + (i % 4) * 45, xx + 40, 830 + (i % 4) * 45, 3, alpha(C['white'], 0.45))
    # Strand
    ctx.move_to(0, 1020)
    ctx.curve_to(300, 990, 700, 1040, W, 1000)
    ctx.line_to(W, road_y)
    ctx.line_to(0, road_y)
    ctx.close_path()
    src(ctx, hexc('#F3D9A4') if tod != 'eve' else hexc('#D9B98A'))
    ctx.fill()
    r = random.Random(3)
    for i in range(14):
        sx, sy = r.uniform(0, W), r.uniform(1060, road_y - 30)
        retro_shell(ctx, sx, sy, r.uniform(0.6, 1.0), r.choice([C['pink3'], C['cream'], hexc('#F9B6A0')]))
    # Palmen
    for px, ph, lean in ((70, 520, -0.08), (1010, 460, 0.1)):
        palm(ctx, px, road_y - 40, ph, T, lean)
    # Straße / Promenade
    rect(ctx, 0, road_y, W, 170, hexc('#4A4A55'))
    for i in range(-1, 9):
        xx = (i * 160) % (W + 160)
        rect(ctx, xx, road_y + 80, 90, 10, hexc('#F2C35A'))
    rect(ctx, 0, road_y - 8, W, 10, hexc('#C9C3BC'))
    rect(ctx, 0, road_y + 170, W, 16, hexc('#C9C3BC'))
    # Dünen + Strandgras vorne
    vgrad(ctx, 0, road_y + 186, W, H - road_y - 186, [(0, hexc('#F3D9A4')), (1, hexc('#E3C58A'))])
    for i in range(18):
        gx = i * 64 + 20
        for k in range(4):
            line(ctx, gx, road_y + 260, gx - 12 + k * 8, road_y + 210 - k * 6 + math.sin(T * 2 + i) * 3, 3, hexc('#7DBA86'))
    # Holzzaun
    for i in range(0, W, 90):
        rect(ctx, i, road_y + 300, 12, 70, P['wood2'])
    rect(ctx, 0, road_y + 316, W, 8, P['wood2'])
    rect(ctx, 0, road_y + 346, W, 8, P['wood2'])
    if tod == 'eve':
        rect(ctx, 0, 0, W, H, alpha(hexc('#2A1E5A'), 0.12))


def retro_shell(ctx, x, y, s, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 8)
    for i in range(7):
        a = math.radians(200 + i * 140 / 6)
        ctx.line_to(math.cos(a) * 16, math.sin(a) * 16 + 3)
    ctx.close_path()
    src(ctx, c)
    ctx.fill()
    ctx.restore()


def palm(ctx, x, y, h, T, lean=0.1):
    tx, ty = x + h * lean, y - h
    ctx.move_to(x - 14, y)
    ctx.curve_to(x - 6, y - h * 0.5, tx - 10, ty + 40, tx - 6, ty)
    ctx.line_to(tx + 6, ty)
    ctx.curve_to(tx + 6, ty + 40, x + 6, y - h * 0.5, x + 14, y)
    ctx.close_path()
    src(ctx, hexc('#A9744A'))
    ctx.fill()
    for i in range(7):
        a = math.radians(-175 + i * 30) + math.sin(T * 1.6 + i) * 0.05
        lx, ly = tx + math.cos(a) * 150, ty + math.sin(a) * 70 + 50
        ctx.move_to(tx, ty)
        ctx.curve_to(tx + math.cos(a) * 70, ty - 50 + math.sin(a) * 20, lx, ly - 30, lx, ly)
        ctx.curve_to(lx - math.cos(a) * 40, ly - 10, tx + math.cos(a) * 50, ty - 10, tx, ty)
        src(ctx, hexc('#3DAA6A'))
        ctx.fill()


ROAD = 1320


def border_scene(ctx, T, tod='day', sand=0.0, bar_up=0.0, officer_gray=0.0, officer_kw=None, extra=None):
    beach_bg(ctx, T, tod, ROAD)
    booth(ctx, 720, ROAD - 2, T)
    table(ctx, 340, ROAD - 2, sand)
    barrier(ctx, 560, ROAD + 40, bar_up)
    if extra:
        extra(ctx)
    kw = dict(face=-1, gray=officer_gray, T=T)
    kw.update(officer_kw or {})
    man(ctx, 560, ROAD + 30, 1.9, 'officer', **kw)


def counter_card(ctx, T, t0, day, year, x=540, y=440):
    if T < t0:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    ctx.save()
    ctx.identity_matrix()
    ctx.translate(x, y)
    ctx.rotate(math.radians(-2))
    ctx.scale(k, k)
    fill_rrect(ctx, -230 + 8, -90 + 12, 460, 180, 6, alpha(C['shadow'], 0.35))
    fill_rrect(ctx, -230, -90, 460, 180, 6, P['paper'])
    fill_rrect(ctx, -200, -60, 150, 120, 8, C['white'])
    rect(ctx, -200, -60, 150, 34, P['red'])
    text(ctx, 'TAG', -125, -43, 20, C['white'], font=SLAB)
    text(ctx, str(day), -125, 15, 56, P['ink'], font=SLAB)
    text(ctx, 'JAHR', 90, -40, 30, P['ink'], font=SLAB)
    text(ctx, str(year), 90, 20, 70, P['red'], font=SLAB)
    ctx.restore()


# ---------------------------------------------------------------- Szenen
def bert_on_bike(ctx, T, x, y=None, s=1.5, moving=True, col=None, sacks=2, glow=0.0, wave=0.0):
    y = ROAD + 40 if y is None else y

    def rider(c):
        man(c, -10, -55, 0.95, 'bert', face=1, T=T, sit=True, arm=(30, -70), wave=wave)
    bicycle(ctx, x, y, s, T, moving, col, sacks, glow, rider)


def sc_intro(ctx, T, t0):
    k = ease(T, 0.2, 3.0)
    border_scene(ctx, T, 'day')
    bert_on_bike(ctx, T, lerp(-200, 250, k), moving=k < 1)
    paper_card(ctx, T, 0.0, [('SEIT', 30, TYPE, P['ink']), ('20 JAHREN', 64, SLAB, P['red'])], 540, 420, -3)
    if UI_ON[0]:
        sticker(ctx, 'ZÖLLNER', 560, 900, 40, 'navy', rot=2, sc=pop(T, nw('zöllner') - 0.05))
        sticker(ctx, 'MUSCHELBERT', 230, 1000, 40, 'cream', rot=-3, sc=pop(T, nw('muschelbert') - 0.05))
    if T >= nw('nie') - 0.1 and UI_ON[0]:
        kk = pop(T, nw('nie') - 0.1)
        ctx.save()
        ctx.translate(380, 1150)
        ctx.scale(kk, kk)
        circle(ctx, 0, 0, 40, C['white'])
        cross_icon(ctx, 0, 0, 18)
        ctx.restore()
    if T >= nw('millionär') - 0.2:
        paper_card(ctx, T, nw('millionär') - 0.2, [('MILLIONÄR!', 76, SLAB, hexc('#2F8A4A'))], 540, 620, 3)
        money_bag(ctx, 160, 1270, back_out(T, nw('millionär') - 0.1, nw('millionär') + 0.3, 2.0))


def money_bag(ctx, x, y, k):
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    ctx.move_to(-60, 0)
    ctx.curve_to(-80, -70, -40, -110, -20, -120)
    ctx.line_to(20, -120)
    ctx.curve_to(40, -110, 80, -70, 60, 0)
    ctx.close_path()
    src(ctx, hexc('#C9A86A'))
    ctx.fill()
    line(ctx, -22, -120, 22, -120, 8, hexc('#8E6238'))
    text(ctx, '€', 0, -50, 60, hexc('#2F8A4A'), font=SLAB)
    for i in range(5):
        ellipse(ctx, -50 + i * 26, 8, 16, 6, P['gold2'])
    ctx.restore()


def sc_morning(ctx, T, t0):
    k = ease(T, t0 + 0.1, nw('grenze') + 0.2)
    border_scene(ctx, T, 'morning')
    bert_on_bike(ctx, T, lerp(-200, 240, k), moving=k < 1)
    paper_card(ctx, T, t0 + 0.05, [('JEDEN MORGEN', 60, SLAB, P['ink'])], 540, 420, -2)
    if T >= nw('säcke') - 0.2 and UI_ON[0]:
        for i, (sx, sy) in enumerate(((128, 1250), (296, 1232))):
            kk = pop(T, nw('säcke') - 0.2 + i * 0.15)
            if kk > 0:
                ctx.save()
                ctx.translate(sx, sy - 120)
                ctx.scale(kk, kk)
                circle(ctx, 0, 0, 26, C['white'])
                text(ctx, str(i + 1), 0, 0, 30, P['ink'], font=SLAB)
                ctx.restore()
        paper_card(ctx, T, nw('sand') - 0.1, [('2 SÄCKE', 52, SLAB, P['ink']), ('SAND', 70, SLAB, hexc('#B8862C'))], 540, 640, 2)


def magnifier(ctx, x, y, r, k, cross=0.0, T=0.0):
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    line(ctx, r * 0.7, r * 0.7, r * 1.4, r * 1.4, 22, hexc('#6E4630'))
    circle(ctx, 0, 0, r + 12, hexc('#3A3F4F'))
    ctx.save()
    ctx.new_sub_path()
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.clip()
    rect(ctx, -r, -r, 2 * r, 2 * r, hexc('#E3C58A'))
    rnd = random.Random(int(T * 2))
    for i in range(220):
        ellipse(ctx, rnd.uniform(-r, r), rnd.uniform(-r, r), rnd.uniform(4, 10), rnd.uniform(3, 8),
                rnd.choice([hexc('#F2D7A6'), hexc('#D9B676'), hexc('#B98E52'), hexc('#FFF0CC')]))
    ctx.restore()
    ctx.new_sub_path()
    ctx.arc(-r * 0.3, -r * 0.3, r * 0.6, math.radians(200), math.radians(260))
    ctx.set_line_width(10)
    src(ctx, alpha(C['white'], 0.5))
    ctx.stroke()
    if cross > 0:
        ctx.save()
        ctx.scale(cross, cross)
        cross_icon(ctx, 0, 0, r * 0.45, P['red'])
        ctx.restore()
    ctx.restore()


def sc_check(ctx, T, t0):
    t_empty = nw('säcke', 1) - 0.4
    t_lupe = nw('lupe') - 0.6
    t_n = nw('nichts') - 0.1
    sand_k = ease(T, t_empty, t_empty + 0.8)
    ctx.save()
    ctx.translate(540, 1100)
    ctx.scale(1.25, 1.25)
    ctx.translate(-540, -1100)
    border_scene(ctx, T, 'morning', sand=sand_k, officer_kw={'arm': (-30, -80) if T < t_lupe else (-40, -110), 'face': -1})
    bert_on_bike(ctx, T, 200, moving=False, sacks=0 if T > t_empty else 2)
    ctx.restore()
    if T >= t_lupe:
        magnifier(ctx, 400, 760, 210, back_out(T, t_lupe, t_lupe + 0.35, 1.6), cross=pop(T, t_n), T=T)
    if T >= nw('nur', 0, after=t_n) - 0.1:
        paper_card(ctx, T, nw('nur', 0, after=t_n) - 0.1, [('NUR SAND.', 70, SLAB, P['ink'])], 620, 420, 3)


def sc_evening(ctx, T, t0):
    k = ease(T, t0, nw('abschied') + 0.4)
    border_scene(ctx, T, 'eve', sand=1.0, officer_kw={'wave': 1.0 if T > nw('winkt') - 0.2 else 0.0, 'face': 1})
    x = lerp(1180, 330, k)
    man(ctx, x, ROAD + 50, 1.9, 'bert', walk=T * 8 if k < 1 else None, face=-1, wave=1.0 if T > nw('winkt') - 0.2 else 0.0, T=T)
    paper_card(ctx, T, t0 + 0.05, [('JEDEN ABEND', 50, SLAB, P['ink']), ('ZU FUSS ZURÜCK', 36, TYPE, P['red'])], 540, 420, -2)


def sc_years(ctx, T, t0):
    t1 = nw('reicher') + 0.6
    k = clamp((T - t0) / (t1 - t0))
    tod = 'day' if int(k * 20) % 2 == 0 else 'eve'
    border_scene(ctx, T, tod, sand=1.0, officer_gray=k)
    day = 1 + int(k * 364)
    year = 1 + int(k ** 1.3 * 19.99)
    xb = (T * 1500) % 1500 - 200
    bert_on_bike(ctx, T, xb, moving=True, s=1.3)
    money_bag(ctx, 160, ROAD + 10, 0.5 + 1.2 * k)
    counter_card(ctx, T, t0 + 0.05, day, year, 540, 430)
    if T >= nw('grau') - 0.2:
        sticker(ctx, 'GRAU', 560, 880, 40, 'white', rot=3, sc=pop(T, nw('grau') - 0.2))
    if T >= nw('reicher') - 0.2:
        sticker(ctx, 'IMMER REICHER', 240, 1050, 40, 'green', rot=-3, sc=pop(T, nw('reicher') - 0.2))


def sc_question(ctx, T, t0):
    border_scene(ctx, T, 'day', sand=1.0, officer_gray=1.0)
    # Denkblase des Zöllners: Muschelbert auf Goldmünzen
    if UI_ON[0]:
        kk = pop(T, t0 + 0.2)
        if kk > 0:
            ctx.save()
            ctx.translate(380, 760)
            ctx.scale(kk, kk)
            for dx, dy, r in ((-90, 10, 90), (0, -30, 110), (100, 0, 95), (10, 60, 90)):
                circle(ctx, dx, dy, r, C['white'])
            for i in range(8):
                ellipse(ctx, -80 + i * 22, 70, 20, 8, P['gold2'])
            man(ctx, 0, 70, 0.9, 'bert', face=1, wave=1.0, T=T)
            text(ctx, '€€€', 90, -40, 36, hexc('#2F8A4A'), font=SLAB)
            ctx.restore()
            for j, (cx, cy, r) in enumerate(((470, 950, 18), (500, 1010, 12))):
                circle(ctx, cx, cy, r * kk, C['white'])
    paper_card(ctx, T, t0 + 0.05, [('WIE WURDE ER', 50, SLAB, P['ink']), ('SO REICH?', 64, SLAB, P['red'])], 540, 360, -2)
    if T >= nw('schreib') - 0.05:
        paper_card(ctx, T, nw('schreib') - 0.05, [("SCHREIB'S IN DIE", 34, SLAB, P['ink']), ('KOMMENTARE', 50, SLAB, P['red'])], 760, 560, 3)
    if T >= GAP_AT:
        hourglass(ctx, 900, 1000, clamp((T - GAP_AT) / GAP), pop(T, GAP_AT))


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
    line(ctx, 0, -4, 0, 90, 3, hexc('#E3C58A'))
    ctx.restore()


def bunting(ctx, T, y=560):
    for i in range(14):
        x = i * 80 + 20
        poly(ctx, [(x, y + math.sin(x / 200) * 20), (x + 60, y + math.sin((x + 60) / 200) * 20), (x + 30, y + 50 + math.sin(x / 200) * 20)],
             [P['red'], hexc('#3FB6D9'), P['gold2'], C['white']][i % 4])
    line(ctx, 0, y, W, y + 10, 2, C['ink'])


def sc_retire(ctx, T, t0):
    border_scene(ctx, T, 'day', sand=1.0, officer_gray=1.0)
    bunting(ctx, T, 600)
    bert_on_bike(ctx, T, 220, moving=False)
    if T < t0 + 2.0:
        r = random.Random(int(T * 10))
        for i in range(30):
            k = (T - t0) / 2.0
            circle(ctx, r.uniform(0, W), r.uniform(500, 1400) * k + 400 * (1 - k), 6, r.choice([P['red'], P['gold2'], hexc('#3FB6D9'), C['pink']]))
    paper_card(ctx, T, t0 + 0.05, [('DIE LÖSUNG …', 60, SLAB, P['ink'])], 540, 360, -2)
    if T >= TW('pensionierung') - 0.2:
        sticker(ctx, 'GUTEN RUHESTAND!', 720, 700, 40, 'red', rot=-2, sc=pop(T, TW('pensionierung') - 0.2))
    if T >= TW('was', 0, after=nw('endlich')) - 0.1:
        paper_card(ctx, T, TW('was', 0, after=nw('endlich')) - 0.1, [('WAS HAST DU', 46, SLAB, P['ink']), ('GESCHMUGGELT?!', 54, SLAB, P['red'])], 600, 880, 2)


BIKE_COLS = [hexc('#C8322E'), hexc('#2F80ED'), hexc('#3FAE6A'), hexc('#F2A23C'), hexc('#9B6FE0'), hexc('#E86FA6')]


def sc_bikes(ctx, T, t0):
    beach_bg(ctx, T, 'day', ROAD)
    t_f = TW('fahrräder') - 0.2
    glow = ease(T, t_f, t_f + 0.4)
    ci = int(max(0, T - TW('jeden', 0, after=nw('fahrräder'))) / 0.45) % len(BIKE_COLS)
    bert_on_bike(ctx, T, 520, y=ROAD + 60, s=2.6, moving=False, col=BIKE_COLS[ci], glow=glow, sacks=2)
    if T >= TW('fahrräder') - 0.2:
        paper_card(ctx, T, t_f, [('FAHRRÄDER!', 80, SLAB, P['red'])], 540, 380, -3)
    if T >= TW('jeden', 0, after=nw('fahrräder')) - 0.1:
        paper_card(ctx, T, TW('jeden', 0, after=nw('fahrräder')) - 0.1, [('JEDEN MORGEN EIN', 32, TYPE, P['ink']), ('NEUES RAD', 56, SLAB, P['ink'])], 540, 600, 2)
        if UI_ON[0]:
            sticker(ctx, 'NEU!', 640, 1180, 44, 'green', rot=-8, sc=pop(T, TW('nagelneues') - 0.1))


def sc_distraction(ctx, T, t0):
    border_scene(ctx, T, 'day', sand=1.0, officer_gray=1.0, officer_kw={'arm': (-40, -110), 'face': -1})
    bert_on_bike(ctx, T, 220, moving=False)
    retro_stamp(ctx, T, TW('ablenkung') - 0.1, 'ABLENKUNG', 420, 880)
    t_c = TW('zwanzig', 0, after=nw('beschäftigen')) - 0.1
    if T >= t_c:
        ctx.save()
        ctx.identity_matrix()
        k = back_out(T, t_c, t_c + 0.3, 1.8)
        ctx.translate(560, 430)
        ctx.rotate(math.radians(-2))
        ctx.scale(k, k)
        fill_rrect(ctx, -250 + 8, -130 + 12, 500, 260, 6, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -250, -130, 500, 260, 6, P['paper'])
        text(ctx, '20 JAHRE GEPRÜFT:', 0, -90, 30, P['ink'], font=SLAB)
        sack(ctx, -170, 0, 0.9, False)
        text(ctx, 'SAND', -40, -20, 40, P['ink'], font=SLAB, align='l')
        ctx.save()
        ctx.translate(-150, 80)
        ctx.scale(0.5, 0.5)
        bicycle(ctx, 0, 30, 1.0, 0, False, P['red'], 0)
        ctx.restore()
        text(ctx, 'FAHRRAD', -40, 60, 40, P['ink'], font=SLAB, align='l')
        if T >= TW('sand', 3) - 0.1:
            check_icon(ctx, 170, -20, 26)
        if T >= TW('nie', 1) - 0.1:
            text(ctx, 'NIE!', 190, 60, 46, P['red'], font=SLAB)
        ctx.restore()


def retro_stamp(ctx, T, t0, s, x, y, size=70, rot=-12):
    if T < t0:
        return
    k = lerp(2.2, 1.0, 1 - (1 - clamp((T - t0) / 0.18)) ** 3)
    tw = text_size(ctx, s, size, SLAB)[0]
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(rot))
    ctx.scale(k, k)
    rrect(ctx, -tw / 2 - 24, -size * 0.75, tw + 48, size * 1.5, 12)
    src(ctx, alpha(P['paper'], 0.9))
    ctx.fill_preserve()
    ctx.set_line_width(8)
    src(ctx, P['red'])
    ctx.stroke()
    text(ctx, s, 0, 0, size, P['red'], font=SLAB)
    ctx.restore()


def bike_shop(ctx, x, y, T):
    rect(ctx, x - 230, y - 360, 460, 360, hexc('#F3D9C0'))
    poly(ctx, [(x - 260, y - 360), (x + 260, y - 360), (x + 230, y - 430), (x - 230, y - 430)], hexc('#E07A4A'))
    fill_rrect(ctx, x - 190, y - 340, 380, 60, 6, C['white'])
    text(ctx, 'FAHRRÄDER', x, y - 310, 40, P['red'], font=SLAB)
    for i in range(7):
        poly(ctx, [(x - 200 + i * 60, y - 270), (x - 140 + i * 60, y - 270), (x - 140 + i * 60, y - 240), (x - 200 + i * 60, y - 240)],
             P['red'] if i % 2 == 0 else C['white'])
    rect(ctx, x - 190, y - 230, 200, 170, hexc('#9FC6E8'))
    rect(ctx, x + 60, y - 230, 110, 230, hexc('#2B4A7A'))


def sc_sell(ctx, T, t0):
    beach_bg(ctx, T, 'day' if T < TW('abends', 0) - 0.2 else 'eve', ROAD)
    bike_shop(ctx, 640, ROAD - 2, T)
    t_s = TW('jedes', 0, after=nw('drüben')) - 0.3
    t_back = TW('abends', 0) - 0.2
    if T < t_back:
        k = ease(T, t0, t_s)
        if T < t_s + 0.6:
            bicycle(ctx, lerp(-100, 360, k), ROAD + 40, 1.5, T, k < 1, hexc('#2F80ED'), 0)
        man(ctx, lerp(-100, 300, k) if T < t_s else 300, ROAD + 50, 1.9, 'bert', face=1, walk=T * 8 if k < 1 else None, T=T)
        # Shelly als Händlerin mit Geld
        shelly(ctx, 560, ROAD + 50, 1.35, arms={'R': (34, -110)} if T > t_s else None, expr='open', blink=blink(T))
        if T >= t_s + 0.6:
            bicycle(ctx, 820, ROAD + 40, 1.3, T, False, hexc('#2F80ED'), 0)
            sticker(ctx, 'VERKAUFT!', 820, 1060, 40, 'green', rot=-4, sc=pop(T, t_s + 0.6))
            if UI_ON[0]:
                for i in range(4):
                    yy = 1060 - ((T * 200 + i * 60) % 240)
                    text(ctx, '€', 340 + i * 20, yy, 40, hexc('#2F8A4A'), font=SLAB)
        paper_card(ctx, T, t0 + 0.05, [('DRÜBEN:', 30, TYPE, P['ink']), ('JEDES RAD VERKAUFT', 50, SLAB, P['ink'])], 540, 420, -2)
    else:
        k = ease(T, t_back, t_back + 2.0)
        man(ctx, lerp(560, -150, k), ROAD + 50, 1.9, 'bert', face=-1, walk=T * 8, T=T)
        paper_card(ctx, T, t_back, [('ABENDS ZU FUSS', 56, SLAB, P['ink'])], 540, 420, -2)
        if T >= TW('ohne') - 0.1:
            paper_card(ctx, T, TW('ohne') - 0.1, [('OHNE FAHRRAD', 60, SLAB, P['red'])], 540, 600, 2)


def sc_math(ctx, T, t0):
    beach_bg(ctx, T, 'eve', ROAD)
    # Fahrradberg
    k = ease(T, t0 + 0.3, TW('fahrräder', 1) + 0.2)
    n = int(140 * k)
    r = random.Random(7)
    for i in range(n):
        bx = 540 + r.gauss(0, 140) * (0.6 + 0.4 * (i / 140))
        by = ROAD + 40 - abs(r.gauss(0, 1)) * 80 * (i / 140) * 4
        ctx.save()
        ctx.translate(bx, by)
        ctx.rotate(r.uniform(-0.8, 0.8))
        bicycle(ctx, 0, 0, 0.55, 0, False, r.choice(BIKE_COLS), 0)
        ctx.restore()
    # fallende Räder
    if k < 1:
        for i in range(6):
            yy = ((T * 900 + i * 230) % 900) + 300
            ctx.save()
            ctx.translate(300 + i * 90, yy)
            ctx.rotate(T * 3 + i)
            bicycle(ctx, 0, 0, 0.5, 0, False, BIKE_COLS[i], 0)
            ctx.restore()
    lines = [('1 RAD × 365 TAGE', 44, SLAB, P['ink'])]
    if T >= TW('zwanzig', 0, after=nw('pro')) - 0.1:
        lines.append(('× 20 JAHRE', 44, SLAB, P['ink']))
    if T >= TW('siebentausend') - 0.1:
        lines = [('ÜBER', 30, TYPE, P['ink']), ('7.000', 100, SLAB, P['red']), ('FAHRRÄDER', 50, SLAB, P['ink'])]
    paper_card(ctx, T, t0 + 0.05, lines, 540, 440, -2)


def sc_hint(ctx, T, t0):
    border_scene(ctx, T, 'eve', sand=1.0, officer_gray=1.0)
    k = ease(T, t0, t0 + 2.5)
    man(ctx, lerp(1100, 700, k), ROAD + 50, 1.9, 'bert', face=-1, walk=T * 8 if k < 1 else None, T=T, wave=1.0 if k >= 1 else 0)
    if UI_ON[0]:
        sticker(ctx, 'ZU FUSS', 840, 1450, 40, 'red', rot=-3, sc=pop(T, t0 + 0.6))
    paper_card(ctx, T, t0 + 0.05, [('WARUM GING ER', 46, SLAB, P['ink']), ('ABENDS ZU FUSS?', 54, SLAB, P['red'])], 540, 400, -2)
    if T >= TW('schreib', 1) - 0.1:
        paper_card(ctx, T, TW('schreib', 1) - 0.1, [("SCHREIB'S IN DIE KOMMENTARE", 30, SLAB, P['ink'])], 540, 600, 2)


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
    beach_bg(ctx, T, 'eve', ROAD)
    man(ctx, 300, ROAD + 50, 1.9, 'bert', face=1, wave=1.0, T=T)
    paper_card(ctx, T, TW('wohnst') - 0.05, [('WOHNST DU SCHON IN', 34, TYPE, P['ink']), ('MUSCHELTAL?', 80, SLAB, P['ink'])], 540, 460, -2)
    tf = TW('folge') - 0.05
    tap = TW('namen') + 0.3
    if UI_ON[0] and T >= tf:
        k = back_out(T, tf, tf + 0.3, 2.0)
        ctx.save()
        ctx.translate(540, 700)
        ctx.scale(max(k, 0.01), max(k, 0.01))
        on = T >= tap
        fill_rrect(ctx, -170 + 6, -50 + 10, 340, 100, 14, alpha(C['shadow'], 0.35))
        fill_rrect(ctx, -170, -50, 340, 100, 14, C['green'] if on else P['red'])
        text(ctx, 'GEFOLGT' if on else 'FOLGEN', -24 if on else 0, 0, 48, C['white'], font=SLAB)
        if on:
            tick_mark(ctx, 120, 0, 34, C['white'])
        ctx.restore()
    hut_card(ctx, T, TW('hütte') - 0.2, 790, ROAD - 10)


# ---------------------------------------------------------------- Zeitleiste
SC = [
    ('intro', 0.0, sc_intro),
    ('morning', nw('jeden', 1) - 0.1, sc_morning),
    ('check', nw('der', 0, after=nw('sand') - 0.1) - 0.1, sc_check),
    ('evening', nw('und', 0, after=nw('nur', 0, after=nw('nichts'))) - 0.1, sc_evening),
    ('years', nw('so') - 0.1, sc_years),
    ('question', nw('also') - 0.1, sc_question),
    ('retire', TW('hier') - 0.1, sc_retire),
    ('bikes', TW('muschelbert', 0, after=nw('geschmuggelt')) - 0.1, sc_bikes),
    ('distract', TW('der', 0, after=nw('nagelneues')) - 0.1, sc_distraction),
    ('sell', TW('drüben') - 0.1, sc_sell),
    ('math', TW('ein', 0, after=nw('ohne')) - 0.1, sc_math),
    ('hint', TW('hast', 0, after=nw('siebentausend')) - 0.1, sc_hint),
    ('outro', TW('und', 0, after=nw('kommentare', 1) - 0.2) - 0.1, sc_outro),
]


def frame(ctx, T):
    cur = SC[0]
    for s_ in SC:
        if T >= s_[1]:
            cur = s_
    z = 1.22
    ctx.save()
    ctx.translate(540, 1540)
    ctx.scale(z, z)
    ctx.translate(-520, -ROAD)
    cur[2](ctx, T, cur[1])
    ctx.restore()
    for s_ in SC[1:]:
        if 0 <= T - s_[1] < 0.08:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.3 * (1 - (T - s_[1]) / 0.08)))
