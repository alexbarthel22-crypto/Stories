"""Hotel Sandkorn – Shellys Rätsel nach Hilberts Hotel. Stil wie das Sunken-Pearl-Rätsel (2D, Sticker, Chips, Untertitel)."""
import json, math, os, random, re, difflib
import cairo
from draw import *
from chars import shelly
from world import fish, palm, boat, shell_deco, starfish

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = json.load(open(f'{ROOT}/audio/vo_words.json'))


def _norm(w):
    w = re.sub(r"[^\wäöüß']", '', w.lower()).replace('ß', 'ss')
    return {'1': 'eins', '2': 'zwei', '3': 'drei', '4': 'vier', '6': 'sechs'}.get(w, w)


def nw(prefix, k=0, after=-1.0, end=False):
    hits = [w for w in NEW if _norm(w[0]) == prefix and w[1] > after]
    if len(hits) <= k:
        hits = [w for w in NEW if _norm(w[0]).startswith(prefix) and w[1] > after]
    return hits[k][2 if end else 1]


# Pause nach der Frage (Zeit zum Nachdenken)
GAP_AT = nw('kommentare', 0, end=True) + 0.1
GAP = 1.4
VO_END = NEW[-1][2] + 0.3


def gn(t):
    return t + (GAP if t >= GAP_AT else 0.0)


def TW(prefix, k=0, after=-1.0, end=False):
    return gn(nw(prefix, k, after, end))


END = gn(VO_END) + 1.6
BL = [1.3, 4.2, 7.9, 11.6, 15.1, 19.4, 23.8, 27.2, 31.7, 35.5, 39.9, 44.1, 48.6, 52.2, 56.9, 60.3]


def blink(T):
    return 1.0 if any(0 <= T - b < 0.12 for b in BL) else 0.0


# ---------------------------------------------------------------- Figuren
PALETTES = [
    dict(hair='#2E2A33', hair2='#1E1B22', pink='#4FA3E8', pink2='#2F7FC4', skin='#E8B58F', skin2='#D49A72'),
    dict(hair='#E7B65A', hair2='#C9953A', pink='#7BC67E', pink2='#4FA65A', skin='#F7D2B5', skin2='#E8B595'),
    dict(hair='#B5482E', hair2='#8E3520', pink='#F2A23C', pink2='#D4841E', skin='#F7D2B5', skin2='#E8B595'),
    dict(hair='#4A3426', hair2='#2E1F16', pink='#9B6FE0', pink2='#7B4FC0', skin='#C98E66', skin2='#A9714C'),
]
BOYS = [('#4A3426', '#3FA7D6', '#2B3A66'), ('#E2B65A', '#E2574C', '#3A6F4F'), ('#1F1B1B', '#F2A23C', '#2B3A66'),
        ('#8A4A2B', '#53B97A', '#5B3A29'), ('#C9C3BC', '#7B5CD6', '#2B3A66')]


def boy_head(ctx, x, y, s, hair, shirt, style=0, mood=1):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    skin = hexc('#F2C6A0')
    rect(ctx, -7, -60, 14, 14, mixc(skin, C['ink'], 0.1))
    for ex in (-28, 28):
        circle(ctx, ex, -84, 6.5, mixc(skin, C['ink'], 0.06))
    circle(ctx, 0, -86, 28, skin)
    hc = hexc(hair)
    ctx.new_path()
    if style == 0:
        ctx.arc(0, -88, 30, math.radians(180), math.radians(360))
        ctx.curve_to(26, -98, 10, -106, -4, -100)
        ctx.curve_to(-14, -106, -26, -100, -30, -88)
    elif style == 1:
        for i in range(7):
            a = math.radians(190 + i * 26)
            ctx.line_to(math.cos(a) * 36, -90 + math.sin(a) * 30)
            a2 = math.radians(203 + i * 26)
            ctx.line_to(math.cos(a2) * 26, -90 + math.sin(a2) * 22)
    else:
        ctx.arc(0, -90, 31, math.radians(170), math.radians(370))
        ctx.curve_to(20, -96, -20, -96, -31, -86)
    ctx.close_path()
    src(ctx, hc)
    ctx.fill()
    for sx in (-10, 10):
        line(ctx, sx - 5, -97, sx + 5, -98, 2.4, mixc(hc, C['ink'], 0.3))
        ellipse(ctx, sx, -86, 3.6, 4.4, C['ink'])
        circle(ctx, sx + 1.2, -87.5, 1.2, C['white'])
    ellipse(ctx, -16, -76, 5, 3, alpha(hexc('#F27B95'), 0.35))
    ellipse(ctx, 16, -76, 5, 3, alpha(hexc('#F27B95'), 0.35))
    ctx.move_to(-8, -71)
    ctx.curve_to(-3, -64, 3, -64, 8, -71)
    ctx.set_line_width(2.6)
    src(ctx, hexc('#8A3B3B'))
    ctx.stroke()
    ctx.restore()


def boy_full(ctx, x, y, s, hair, shirt, shorts, style=0, walk=None, suitcase=False):
    skin = hexc('#F2C6A0')
    sh = hexc(shirt)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 1, 26, 5, alpha(C['shadow'], 0.18))
    lg = math.sin(walk) * 0.5 if walk is not None else 0.0
    for side, l in ((-1, lg), (1, -lg)):
        fx_, fy_ = side * 8 + math.sin(l) * 18, -6
        line(ctx, side * 8, -40, fx_, fy_, 7, mixc(skin, C['ink'], 0.08))
        ellipse(ctx, fx_ + 2, -3, 9, 5, hexc('#3A3F4F'))
    fill_rrect(ctx, -18, -56, 36, 22, 6, hexc(shorts))
    ctx.restore()
    boy_head(ctx, x, y - 54 * s, s * 0.95, hair, shirt, style)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    fill_rrect(ctx, -19, -98, 38, 46, 12, sh)
    fill_rrect(ctx, -19, -98, 15, 46, 12, mixc(sh, C['white'], 0.12))
    for side in (-1, 1):
        sx, sy = side * 16, -92
        tx, ty = side * 23, -56
        line(ctx, sx, sy, tx, ty, 6.5, skin)
        circle(ctx, sx, sy + 1, 7.5, sh)
        circle(ctx, tx, ty, 4.8, skin)
    if suitcase:
        fill_rrect(ctx, 22, -62, 30, 38, 5, hexc('#B5482E'))
        line(ctx, 30, -62, 30, -70, 3, C['ink'])
        line(ctx, 44, -62, 44, -70, 3, C['ink'])
        line(ctx, 30, -70, 44, -70, 3, C['ink'])
    ctx.restore()


def guest(ctx, x, y, s, seed, walk=None, mirror=False, suitcase=False):
    """Gast: abwechselnd Frau (Kleid) oder Mann (Shirt + Shorts)."""
    if seed % 2 == 0:
        pal = PALETTES[(seed // 2) % len(PALETTES)]
        old = {k: C[k] for k in pal}
        for k, v in pal.items():
            C[k] = hexc(v)
        try:
            shelly(ctx, x, y, s, shell=False, long_hair=True, walk=walk, mirror=mirror, face=0.8 if walk is not None else 0,
                   blink=1.0 if (seed * 7 % 23) == 0 else 0.0)
        finally:
            C.update(old)
    else:
        h, sh, sho = BOYS[(seed // 2) % len(BOYS)]
        boy_full(ctx, x, y, s * 1.05, h, sh, sho, seed % 3, walk, suitcase)


# ---------------------------------------------------------------- Kulisse Nachtstrand
def night_sky(ctx, T, y_hor=900):
    vgrad(ctx, 0, 0, W, y_hor, [(0, hexc('#0E1638')), (0.7, hexc('#23306A')), (1, hexc('#3A4A8A'))])
    r = random.Random(1)
    for i in range(90):
        x, y = r.uniform(0, W), r.uniform(0, y_hor - 80)
        tw = 0.5 + 0.5 * math.sin(T * r.uniform(1, 3) + i)
        circle(ctx, x, y, r.uniform(1.2, 2.8), alpha(C['white'], 0.35 + 0.5 * tw))
    circle(ctx, 860, 250, 70, alpha(hexc('#FFF6D6'), 0.18))
    circle(ctx, 860, 250, 52, hexc('#FFF2C2'))
    circle(ctx, 878, 240, 46, hexc('#22306A'))


def sea_band(ctx, T, y0, y1):
    vgrad(ctx, 0, y0, W, y1 - y0, [(0, hexc('#1C3E78')), (1, hexc('#2A5C9A'))])
    for i in range(14):
        xx = (i * 90 + T * 20) % (W + 100) - 50
        yy = y0 + 18 + (i % 4) * (y1 - y0 - 30) / 4
        line(ctx, xx, yy, xx + 46, yy, 3, alpha(C['white'], 0.3))
    # Mondglitzern
    for i in range(8):
        yy = y0 + 10 + i * (y1 - y0) / 9
        line(ctx, 860 - 30 + math.sin(T * 2 + i) * 10, yy, 860 + 30 + math.sin(T * 2 + i) * 10, yy, 3, alpha(hexc('#FFF2C2'), 0.35))


def sand(ctx, y0, y1):
    vgrad(ctx, 0, y0, W, y1 - y0, [(0, hexc('#C9A86A')), (1, hexc('#B08A50'))])
    r = random.Random(4)
    for i in range(40):
        shell_deco(ctx, r.uniform(0, W), r.uniform(y0 + 20, y1 - 10), r.uniform(0.8, 1.4), alpha(r.choice([C['pink3'], C['cream']]), 0.85))


def lantern(ctx, x, y, T):
    line(ctx, x, y, x, y - 170, 6, hexc('#3A3F4F'))
    g = cairo.RadialGradient(x, y - 178, 2, x, y - 178, 90)
    g.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.55)
    g.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
    ctx.arc(x, y - 178, 90, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    circle(ctx, x, y - 178, 14, hexc('#FFE6A8'))


# ---------------------------------------------------------------- Hotel-Fassade (Perspektive bis zum Horizont)
VX, VY = 1040, 830          # Fluchtpunkt rechts am Horizont


def room_rect(n, x0=60, base=1330, h=420, w=300, k=0.3):
    """Zimmer n (ab 1) in Fluchtperspektive: links groß, rechts zum Horizont hin klein."""
    f0 = 1.0 / (1 + k * (n - 1))
    f1 = 1.0 / (1 + k * n)
    xa = VX + (x0 - VX) * f0
    xb = VX + (x0 - VX) * f1
    ya_b = VY + (base - VY) * f0
    yb_b = VY + (base - VY) * f1
    return xa, xb, ya_b, yb_b, f0, f1, h, w


def facade(ctx, T, sign='HOTEL SANDKORN', belegt=1.0, guests=True, n_max=60, x0=60, sign_k=1.0, glow_rooms=None):
    base, top_h = 1330, 500
    # Dachkante und Sockel als durchgehende Flucht
    for n in range(n_max, 0, -1):
        xa, xb, ya, yb, f0, f1, h, w = room_rect(n, x0)
        ha, hb = top_h * f0, top_h * f1
        # Wand
        poly(ctx, [(xa, ya), (xb, yb), (xb, yb - hb), (xa, ya - ha)], hexc('#F2D7A6') if n % 2 else hexc('#EBCB94'))
        # Dach
        poly(ctx, [(xa, ya - ha), (xb, yb - hb), (xb, yb - hb - 60 * f1), (xa - 10 * f0, ya - ha - 70 * f0)], C['pink2'])
        line(ctx, xa, ya - ha, xb, yb - hb, max(1, 6 * f0), C['white'])
        if f0 < 0.04:
            continue
        # Tür mit Nummer
        def P(u, v):  # u: 0..1 entlang Zimmer, v: Höhe über Boden (Pixel bei f=1)
            ff = f0 + (f1 - f0) * u
            return (xa + (xb - xa) * u, (ya + (yb - ya) * u) - v * ff)
        d0, d1 = 0.18, 0.48
        poly(ctx, [P(d0, 0), P(d1, 0), P(d1, 250), P(d0, 250)], hexc('#5B3A29'))
        poly(ctx, [P(d0 + 0.02, 0), P(d1 - 0.02, 0), P(d1 - 0.02, 236), P(d0 + 0.02, 236)], hexc('#7FC8C2'))
        # Fenster (beleuchtet, Gast-Silhouette)
        w0, w1 = 0.58, 0.9
        lit = hexc('#FFE3A3')
        poly(ctx, [P(w0, 120), P(w1, 120), P(w1, 290), P(w0, 290)], hexc('#5B3A29'))
        poly(ctx, [P(w0 + 0.02, 130), P(w1 - 0.02, 130), P(w1 - 0.02, 280), P(w0 + 0.02, 280)], lit)
        if guests and f0 > 0.08:
            cx_, cy_ = P((w0 + w1) / 2, 150)
            circle(ctx, cx_, cy_ - 48 * f0, 22 * f0, alpha(hexc('#5B3A29'), 0.55))
            fill_rrect(ctx, cx_ - 28 * f0, cy_ - 30 * f0, 56 * f0, 40 * f0, 14 * f0, alpha(hexc('#5B3A29'), 0.55))
        # Nummernschild
        px, py = P((d0 + d1) / 2, 300)
        sz = 30 * f0
        if sz > 6:
            fill_rrect(ctx, px - 30 * f0, py - 20 * f0, 60 * f0, 40 * f0, 8 * f0, C['navy'])
            text(ctx, str(n), px, py, sz, C['white'])
        # BELEGT-Schildchen
        if belegt > 0 and f0 > 0.1:
            bx, by = P((d0 + d1) / 2, 205)
            fill_rrect(ctx, bx - 52 * f0, by - 14 * f0, 104 * f0, 28 * f0, 6 * f0, alpha(C['red'], belegt))
            text(ctx, 'BELEGT', bx, by, 18 * f0, alpha(C['white'], belegt))
        if glow_rooms and n in glow_rooms:
            poly(ctx, [P(0.02, 0), P(0.98, 0), P(0.98, 400), P(0.02, 400)], alpha(C['yellow'], 0.0))
    # Schild über dem ersten Zimmer
    xa, xb, ya, yb, f0, f1, h, w = room_rect(1, x0)
    sx = 330
    if sign_k > 0.01:
        ctx.save()
        ctx.translate(sx, ya - top_h - 120)
        ctx.scale(sign_k, sign_k)
        fill_rrect(ctx, -190, -48, 380, 96, 20, C['navy'])
        rrect(ctx, -190, -48, 380, 96, 20)
        ctx.set_line_width(6)
        src(ctx, C['gold'])
        ctx.stroke()
        text(ctx, sign, 0, 0, 44 if len(sign) < 15 else 40, hexc('#FFE6A8'))
        ctx.restore()


def neon_belegt(ctx, x, y, T, on=1.0):
    flick = 1.0 if (T * 7) % 5 > 0.4 else 0.4
    g = on * flick
    fill_rrect(ctx, x - 120, y - 40, 240, 80, 16, alpha(hexc('#2A0E14'), 0.9))
    for k_, a in ((10, 0.15), (6, 0.3)):
        rrect(ctx, x - 120 - k_, y - 40 - k_, 240 + 2 * k_, 80 + 2 * k_, 20)
        ctx.set_line_width(4)
        src(ctx, alpha(hexc('#FF4D6A'), a * g))
        ctx.stroke()
    text(ctx, 'BELEGT', x, y, 46, mixc(hexc('#5A2030'), hexc('#FF7A8F'), g))


# ---------------------------------------------------------------- Gang mit Zimmern (Seitenansicht, für die Lösung)
DOOR_SP = 190.0


def door_x(n, cam_x):
    return 160 + (n - 1) * DOOR_SP - cam_x


def corridor(ctx, T, cam_x, status=None, n_show=(1, 12), y_floor=1180, plates=True):
    """Außengang (Boardwalk) mit Zimmertüren. status[n] in {'belegt', 'frei', 'gerade', None}."""
    status = status or {}
    rect(ctx, 0, 560, W, y_floor - 560, hexc('#F2D7A6'))
    for i in range(-2, 14):
        x = (i * 105 - cam_x * 0.5) % (W + 105) - 105
        line(ctx, x, 560, x, y_floor, 2, alpha(hexc('#C9A86A'), 0.4))
    rect(ctx, 0, 540, W, 30, C['pink2'])
    rect(ctx, 0, 530, W, 12, C['white'])
    # Boardwalk
    rect(ctx, 0, y_floor, W, 120, hexc('#A9744A'))
    for i in range(-1, 14):
        x = (i * 90 - cam_x) % (W + 90) - 90
        line(ctx, x, y_floor, x, y_floor + 120, 3, hexc('#8E6238'))
    rect(ctx, 0, y_floor, W, 10, hexc('#C98B5A'))
    sand(ctx, y_floor + 120, H)
    n0, n1 = n_show
    for n in range(n0, n1 + 1):
        x = door_x(n, cam_x)
        if x < -150 or x > W + 150:
            continue
        stt = status.get(n)
        fill_rrect(ctx, x - 70, y_floor - 300, 140, 300, 12, hexc('#5B3A29'))
        fill_rrect(ctx, x - 60, y_floor - 290, 120, 290, 8, hexc('#7FC8C2') if stt != 'frei' else hexc('#BFF0D2'))
        circle(ctx, x + 40, y_floor - 140, 6, C['gold'])
        # Lampe
        circle(ctx, x - 100, y_floor - 330, 10, hexc('#FFE6A8'))
        if plates:
            col = C['navy']
            if stt == 'gerade':
                col = hexc('#2F80ED')
            if stt == 'frei':
                col = C['green']
            fill_rrect(ctx, x - 44, y_floor - 362, 88, 50, 10, col)
            text(ctx, str(n), x, y_floor - 337, 34, C['white'])
        if stt == 'frei':
            fill_rrect(ctx, x - 50, y_floor - 230, 100, 34, 8, C['green'])
            text(ctx, 'FREI', x, y_floor - 213, 22, C['white'])
        elif stt in ('belegt', 'gerade'):
            fill_rrect(ctx, x - 56, y_floor - 230, 112, 34, 8, C['red'])
            text(ctx, 'BELEGT', x, y_floor - 213, 20, C['white'])


def arc_arrow(ctx, x0, x1, y, h, k, col=None):
    """Roter Bogenpfeil von x0 nach x1 (k = Fortschritt 0..1)."""
    if k <= 0:
        return
    col = col or C['red']
    n = 40
    m = max(2, int(n * k))
    pts = []
    for i in range(m + 1):
        u = i / n
        pts.append((lerp(x0, x1, u), y - math.sin(math.pi * u) * h))
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_line_width(7)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, col)
    ctx.stroke()
    if k > 0.97:
        ex, ey = pts[-1]
        poly(ctx, [(ex - 16, ey - 18), (ex + 16, ey - 18), (ex, ey + 6)], col)


# ---------------------------------------------------------------- Texte / UI
def outlined(ctx, s, x, y, size, fill, stroke=None, sw=None):
    if not UI_ON[0]:
        return
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    ctx.move_to(x - e.x_advance / 2, y + size * 0.36)
    ctx.text_path(s)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(sw or size * 0.2)
    src(ctx, stroke or C['ink'])
    ctx.stroke_preserve()
    src(ctx, fill)
    ctx.fill()


def paper_card(ctx, T, t0, lines, x=510, y=560, rot=-2.0):
    """Zettel-Karte (wie im Original): kleine Zeile oben, große Zeile(n), optionale rote Zeile."""
    if not UI_ON[0] or T < t0:
        return
    k = back_out(T, t0, t0 + 0.3, 1.8)
    if k <= 0.001:
        return
    ws = [text_size(ctx, s, sz)[0] for s, sz, _ in lines]
    w = min(860, max(ws) + 90)
    h = sum(sz * 1.25 for _, sz, _ in lines) + 60
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(rot + math.sin(T * 1.5) * 0.6))
    ctx.scale(k, k)
    fill_rrect(ctx, -w / 2 + 8, -h / 2 + 12, w, h, 10, alpha(C['shadow'], 0.35))
    fill_rrect(ctx, -w / 2, -h / 2, w, h, 10, hexc('#F3EBDD'))
    yy = -h / 2 + 30
    for s, sz, col in lines:
        text(ctx, s, 0, yy + sz * 0.55, sz, col)
        yy += sz * 1.25
    ctx.restore()


def clock(ctx, T, t0, hhmm='20:00', kind='moon'):
    clock_chip(ctx, 270, 335, hhmm, 20.0, kind, pop(T, t0))


# ---------------------------------------------------------------- Untertitel
def _build_caps():
    txt = [t for t in open(os.path.join(ROOT, 'src', 'script.txt')).read().split() if re.search(r'\w', t)]
    sn = [_norm(t) for t in txt]
    wn = [_norm(w[0]) for w in NEW]
    tm = [None] * len(txt)
    for blk in difflib.SequenceMatcher(None, sn, wn, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            tm[blk.a + k] = (NEW[blk.b + k][1], NEW[blk.b + k][2])
    i = 0
    while i < len(tm):
        if tm[i] is None:
            j = i
            while j < len(tm) and tm[j] is None:
                j += 1
            a = tm[i - 1][1] if i else 0.0
            b = tm[j][0] if j < len(tm) else VO_END
            for k in range(j - i):
                tm[i + k] = (a + (b - a) * k / (j - i), a + (b - a) * (k + 1) / (j - i))
            i = j
        i += 1
    disp = {'eins': '1', 'zwei': '2', 'drei': '3', 'vier': '4', 'sechs': '6'}
    caps = []
    for t, (a, b) in zip(txt, tm):
        core = re.sub(r'[^\wäöüß]', '', t.lower())
        t2 = t.lower().replace(core, disp[core]) if core in disp and 'zimmer' not in core else t
        caps.append((t2.upper(), gn(a), gn(b)))
    chunks, cur = [], []
    for idx, (t, a, b) in enumerate(caps):
        cur.append(idx)
        if len(cur) >= 3 or t[-1] in '.,?!:' or (idx + 1 < len(caps) and caps[idx + 1][1] - b > 0.4):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return caps, chunks


CAPS, CAP_CHUNKS = _build_caps()


def subtitles(ctx, T, y=1420, size=66, start=0.0):
    if not UI_ON[0] or T < start:
        return
    cur = None
    for ch in CAP_CHUNKS:
        if CAPS[ch[0]][1] - 0.06 <= T <= CAPS[ch[-1]][2] + 0.3:
            cur = ch
    if cur is None:
        return
    k = max(0.05, back_out(T, CAPS[cur[0]][1] - 0.06, CAPS[cur[0]][1] + 0.14, 1.6))
    toks = [CAPS[i][0] for i in cur]
    gap = size * 0.32
    ws = [text_size(ctx, t, size)[0] for t in toks]
    lines, line_, cw = [], [], 0
    for i, w in zip(cur, ws):
        if line_ and cw + gap + w > 820:
            lines.append((line_, cw)); line_, cw = [], 0
        cw = cw + (gap if line_ else 0) + w
        line_.append((i, w))
    lines.append((line_, cw))
    lh = size * 1.12
    ctx.save()
    ctx.translate(510, y)
    ctx.scale(k, k)
    yy = -(len(lines) - 1) * lh / 2
    for items, lw in lines:
        x = -lw / 2
        for i, w in items:
            on = CAPS[i][1] - 0.03 <= T < (CAPS[i + 1][1] - 0.03 if i + 1 < len(CAPS) else CAPS[i][2] + 0.3)
            outlined(ctx, CAPS[i][0], x + w / 2, yy, size, C['yellow'] if on else C['white'])
            x += w + gap
        yy += lh
    ctx.restore()


# ---------------------------------------------------------------- Szenen
def shelly_owner(ctx, T, x, y, s=1.35, pose='idle', expr='smile', tag=True, mirror=False):
    wv = math.sin(T * 8) * 10
    arms = {'idle': None, 'wave': {'R': (32 + wv * 0.2, -140 + wv)}, 'point': {'R': (46, -108)},
            'megaphone': {'R': (20, -118)}, 'cheer': {'R': (30, -150 + wv), 'L': (-30, -150 - wv)},
            'shrug': {'R': (40, -106), 'L': (-40, -106)}}[pose]
    out = shelly(ctx, x, y, s, arms=arms, expr=expr, blink=blink(T), mirror=mirror)
    if pose == 'megaphone':
        hx, hy = out['R']
        d = -1 if mirror else 1
        poly(ctx, [(hx, hy - 10), (hx + d * 70, hy - 34), (hx + d * 70, hy + 30), (hx, hy + 8)], C['red'])
        fill_rrect(ctx, hx - 10 if d > 0 else hx - 4, hy - 12, 14, 24, 4, C['ink'])
    if tag and UI_ON[0]:
        fill_rrect(ctx, x - 70, y - 290 * s / 1.35, 140, 40, 10, C['navy'])
        text(ctx, 'CHEFIN', x, y - 290 * s / 1.35 + 20, 24, C['yellow'])
    return out


def sc_hook(ctx, T):
    """Einstieg: ausgebuchtes Hotel, Neon BELEGT, Wörter knallen rein."""
    night_sky(ctx, T, 820)
    sea_band(ctx, T, 760, 900)
    sand(ctx, 900, H)
    z = lerp(1.25, 1.0, 1 - (1 - clamp(T / 0.5)) ** 3)
    ctx.save()
    ctx.translate(540, 1100)
    ctx.scale(z, z)
    ctx.translate(-540, -1100)
    facade(ctx, T, belegt=1.0)
    neon_belegt(ctx, 760, 640, T)
    palm(ctx, 60, 1300, 420, T, -0.1, 0.4)
    ctx.restore()
    if T < 0.22:
        rect(ctx, 0, 0, W, H, alpha(C['white'], 0.7 * (1 - T / 0.22)))
    # große Wort-Slams
    groups = [(['AUSGEBUCHT!'], nw('ausgebucht') - 0.05), (['UND', 'TROTZDEM'], nw('und', 0) - 0.05),
              (['∞', 'NEUE GÄSTE?'], nw('unendlich', 0) - 0.05)]
    cur = None
    for g_, t0 in groups:
        if T >= min(t0, 0.0 if g_ == groups[0][0] else t0):
            cur = (g_, t0)
    if cur is None:
        cur = groups[0]
    words, t0 = cur
    t0 = max(0.0, t0) if words != groups[0][0] else 0.0
    k = lerp(2.2, 1.0, 1 - (1 - clamp((T - t0) / 0.18)) ** 3)
    ctx.save()
    ctx.translate(510, 470)
    ctx.rotate(math.sin(T * 9) * 0.03 * max(0, 1 - (T - t0) / 0.6) - 0.04)
    ctx.scale(k, k)
    for i, w_ in enumerate(words):
        sz = 150 if w_ == '∞' else (104 if len(w_) < 12 else 84)
        outlined(ctx, w_, 0, (i - (len(words) - 1) / 2) * 120, sz, C['yellow'] if i == len(words) - 1 else C['white'])
    ctx.restore()
    shelly_owner(ctx, T, 760, 1290, 1.35, 'shrug' if T > nw('unendlich', 0) else 'idle', 'o' if T > nw('unendlich', 0) else 'smile', tag=False)


def sc_owner(ctx, T, t0):
    night_sky(ctx, T, 820)
    sea_band(ctx, T, 760, 900)
    sand(ctx, 900, H)
    facade(ctx, T, belegt=0.0, sign_k=max(0.01, back_out(T, nw('hotel', 1) - 0.1, nw('hotel', 1) + 0.2, 2.0)))
    lantern(ctx, 70, 1330, T)
    shelly_owner(ctx, T, 620, 1300, 1.45, 'wave', 'open')
    sticker(ctx, 'SHELLY', 620, 820, 54, 'cream', rot=-3, sc=pop(T, t0 + 0.05))


def sc_sand(ctx, T, t0):
    """Sandkörner ohne Ende -> ∞ Zimmer."""
    vgrad(ctx, 0, 0, W, H, [(0, hexc('#E3C58A')), (1, hexc('#C9A86A'))])
    r = random.Random(9)
    z = lerp(1.0, 1.6, ease(T, t0, t0 + 3.5))
    ctx.save()
    ctx.translate(540, 960)
    ctx.scale(z, z)
    ctx.translate(-540, -960)
    for i in range(900):
        x, y = r.uniform(-200, W + 200), r.uniform(-200, H + 200)
        rr = r.uniform(3, 10)
        ellipse(ctx, x, y, rr, rr * 0.8, r.choice([hexc('#F2D7A6'), hexc('#D9B676'), hexc('#B98E52'), hexc('#FFF0CC')]))
    for i in range(10):
        shell_deco(ctx, r.uniform(0, W), r.uniform(0, H), r.uniform(1.2, 2.2), r.choice([C['pink3'], C['cream']]))
    ctx.restore()
    sticker(ctx, 'SO VIELE ZIMMER', 510, 600, 66, 'cream', rot=-3, sc=pop(T, nw('viele', 1) - 0.1))
    sticker(ctx, 'WIE SANDKÖRNER', 510, 720, 66, 'yellow', rot=2, sc=pop(T, nw('sandkörner') - 0.05))
    kk = pop(T, nw('unendlich', 1) - 0.05)
    if kk > 0 and UI_ON[0]:
        ctx.save()
        ctx.translate(510, 1000)
        ctx.scale(kk, kk)
        circle(ctx, 0, 0, 150, alpha(C['navy'], 0.92))
        outlined(ctx, '∞', 0, -10, 220, C['yellow'], sw=20)
        ctx.restore()
        sticker(ctx, 'UNENDLICH VIELE', 510, 1210, 56, 'navy', sc=kk)


def sc_endless(ctx, T, t0):
    """Zimmer 1, 2, 3 … ohne Ende: Kamera rauscht an der Fassade entlang zum Horizont."""
    night_sky(ctx, T, 820)
    sea_band(ctx, T, 760, 900)
    sand(ctx, 900, H)
    k = ease(T, nw('drei') - 0.1, nw('ende') + 0.6)
    x0 = lerp(60, -2600, k ** 1.4)
    facade(ctx, T, belegt=0.0, x0=x0, n_max=90)
    for i, (w_, t_) in enumerate([('1', nw('eins')), ('2', nw('zwei')), ('3', nw('drei'))]):
        sticker(ctx, w_, 280 + i * 230, 520, 96, 'yellow', rot=(-4, 3, -2)[i], sc=pop(T, t_ - 0.05) * (1 - ease(T, nw('ende') - 0.1, nw('ende') + 0.2)))
    sticker(ctx, '… OHNE ENDE', 510, 560, 84, 'cream', rot=-2, sc=pop(T, nw('ende') - 0.15))


def sc_full(ctx, T, t0):
    night_sky(ctx, T, 820)
    sea_band(ctx, T, 760, 900)
    sand(ctx, 900, H)
    facade(ctx, T, belegt=ease(T, nw('belegt') - 0.3, nw('belegt')))
    neon_belegt(ctx, 760, 640, T, ease(T, nw('belegt') - 0.2, nw('belegt')))
    clock(ctx, T, t0 + 0.1)
    shelly_owner(ctx, T, 760, 1300, 1.35, 'idle', 'smile')
    sticker(ctx, 'ALLE ZIMMER BELEGT', 510, 560, 58, 'red', rot=-2, sc=pop(T, nw('belegt')))


def sc_ferry(ctx, T, t0):
    """Fähre legt an, endlose Schlange von Gästen bis zum Horizont."""
    night_sky(ctx, T, 760)
    sea_band(ctx, T, 700, 1120)
    sand(ctx, 1120, H)
    kx = ease(T, t0, t0 + 1.6)
    bx = lerp(1150, 520, kx)
    # Steg
    rect(ctx, 0, 1080, 700, 40, hexc('#A9744A'))
    for i in range(8):
        rect(ctx, 20 + i * 90, 1100, 14, 60, hexc('#8E6238'))
    boat(ctx, bx, 1080, T, 0.25)
    # Gäste-Schlange: aus der Fähre bis zum Horizont (perspektivisch)
    if T >= nw('mit', 0, after=t0) - 0.2:
        kk = ease(T, nw('mit', 0, after=t0) - 0.2, nw('gästen') + 0.5)
        n = int(60 * kk) + 1
        for i in range(n, 0, -1):
            f = 1.0 / (1 + 0.32 * i)
            # Schlange führt vom Steg (vorne links) zur Fähre und weiter aufs Meer hinaus zum Horizont
            x = lerp(980, 200, f)
            y = lerp(760, 1500, f)
            guest(ctx, x, y, 1.4 * f, i, walk=T * 8 + i, mirror=True, suitcase=(i % 3 == 0))
    clock(ctx, T, -1)
    sticker(ctx, 'FÄHRE', 300, 600, 54, 'cream', rot=-3, sc=pop(T, nw('fähre') - 0.05))
    kinf = pop(T, nw('unendlich', 2) - 0.05)
    sticker(ctx, '∞ GÄSTE', 600, 470, 80, 'yellow', rot=3, sc=kinf)


def sc_want(ctx, T, t0):
    """Alle wollen ein Zimmer: Schlange vor dem vollen Hotel, Schlüssel-Symbole."""
    night_sky(ctx, T, 820)
    sea_band(ctx, T, 760, 900)
    sand(ctx, 900, H)
    facade(ctx, T, belegt=1.0)
    neon_belegt(ctx, 760, 640, T)
    for i in range(14, 0, -1):
        f = 1.0 / (1 + 0.22 * i)
        x = lerp(1060, 150, f)
        y = lerp(980, 1480, f)
        guest(ctx, x, y, 1.25 * f, i + 3, suitcase=(i % 2 == 0))
        if UI_ON[0] and i < 9:
            kx, ky = x, y - 230 * f
            kk = pop(T, t0 + 0.08 * i)
            if kk > 0:
                ctx.save()
                ctx.translate(kx, ky + math.sin(T * 4 + i) * 6)
                ctx.scale(kk * f * 1.6, kk * f * 1.6)
                circle(ctx, -12, 0, 12, C['gold'])
                circle(ctx, -12, 0, 5, C['navy'])
                rect(ctx, -2, -4, 34, 8, C['gold'])
                rect(ctx, 22, 4, 6, 10, C['gold'])
                ctx.restore()
    clock(ctx, T, -1)
    sticker(ctx, '1 ZIMMER PRO GAST', 510, 520, 60, 'cream', rot=-2, sc=pop(T, nw('eins', 1) - 0.1))
    sticker(ctx, 'NIEMAND BLEIBT DRAUSSEN', 510, 640, 48, 'yellow', rot=2, sc=pop(T, nw('niemand') - 0.1))


def sc_instruction(ctx, T, t0):
    """Shelly mit Megafon: nur EINE Anweisung. Welche?"""
    night_sky(ctx, T, 820)
    sea_band(ctx, T, 760, 900)
    sand(ctx, 900, H)
    facade(ctx, T, belegt=1.0)
    neon_belegt(ctx, 760, 640, T)
    for i in range(8, 0, -1):
        f = 1.0 / (1 + 0.25 * i)
        guest(ctx, lerp(1060, 300, f) + 120, lerp(980, 1460, f), 1.15 * f, i + 5)
    shelly_owner(ctx, T, 330, 1320, 1.45, 'megaphone', 'open', tag=False)
    if UI_ON[0] and T >= nw('anweisung') - 0.2:
        for j in range(3):
            kk = ((T - nw('anweisung')) * 1.2 + j / 3) % 1
            ctx.new_sub_path()
            ctx.arc(470, 1110, 40 + 120 * kk, -0.6, 0.6)
            ctx.set_line_width(6)
            src(ctx, alpha(C['white'], 1 - kk))
            ctx.stroke()
    paper_card(ctx, T, nw('nur', 0, after=t0) - 0.05, [('NUR EINE ANWEISUNG:', 30, C['ink']), ('WELCHE?', 92, C['ink'])], 510, 560)


def sc_question(ctx, T, t0):
    """Frage + Denkpause."""
    sc_instruction(ctx, T, t0 - 10)
    paper_card(ctx, T, t0 - 0.05, [('NUR EINE ANWEISUNG:', 30, C['ink']), ('WELCHE?', 92, C['ink']),
                                     ('DEINE ANTWORT IN DIE KOMMENTARE', 28, C['red'])], 510, 600)
    if UI_ON[0]:
        kk = pop(T, nw('schreibe') - 0.05)
        if kk > 0:
            ctx.save()
            ctx.translate(820, 820)
            ctx.scale(kk, kk)
            fill_rrect(ctx, -60, -40, 120, 80, 22, C['yellow'])
            poly(ctx, [(-20, 36), (10, 36), (-28, 64)], C['yellow'])
            for i in range(3):
                circle(ctx, -28 + i * 28, 0, 8, C['ink'])
            ctx.restore()
    # Denkpause: tickende Uhr / Countdown
    tp = GAP_AT
    if T >= tp and UI_ON[0]:
        k = clamp((T - tp) / GAP)
        cx_, cy_ = 510, 960
        circle(ctx, cx_, cy_, 70, alpha(C['navy'], 0.9))
        ctx.new_sub_path()
        ctx.arc(cx_, cy_, 58, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k)
        ctx.set_line_width(12)
        src(ctx, C['yellow'])
        ctx.stroke()
        text(ctx, '?', cx_, cy_, 80, C['white'])


SOL_CAM = 0.0


def sc_solution(ctx, T, t0):
    """Zimmernummer × 2: Bogenpfeile, gerade belegt, ungerade frei, Fährgäste ziehen ein."""
    night_sky(ctx, T, 560)
    t_z1 = TW('geht') - 0.4
    t_2 = TW('vier') - 0.5
    t_3 = TW('sechs') - 0.5
    t_rest = TW('weiter') - 0.2
    t_even = TW('geraden') - 0.2
    t_free = TW('frei') - 0.3
    t_new = TW('jeden') - 0.3
    cam = lerp(0, 520, ease(T, t_rest, t_rest + 1.2))
    # Status
    status = {}
    for n in range(1, 16):
        status[n] = 'belegt'
    if T >= t_free:
        for n in range(1, 16, 2):
            status[n] = 'frei'
        for n in range(2, 16, 2):
            status[n] = 'gerade'
    elif T >= t_even:
        for n in range(2, 16, 2):
            status[n] = 'gerade'
    if T >= t_new + 1.0:
        for n in range(1, 16, 2):
            status[n] = 'belegt'
    corridor(ctx, T, cam, status, (1, 15))
    # Gäste: alter Gast von Zimmer n steht vor seiner Tür und läuft nach 2n
    starts = {1: t_z1, 2: t_2, 3: t_3}
    for n in range(1, 8):
        ts = starts.get(n, t_rest + (n - 4) * 0.12)
        k = ease(T, ts, ts + 0.9)
        xa, xb = door_x(n, cam), door_x(2 * n, cam)
        x = lerp(xa, xb, k)
        hop = math.sin(math.pi * k) * 40
        walking = 0 < k < 1
        guest(ctx, x, 1175 - hop, 1.2, n * 2, walk=T * 10 if walking else None)
        if T >= ts - 0.1 and T < t_even + 0.3:
            arc_arrow(ctx, xa, xb, 830, 120 + 30 * n, ease(T, ts - 0.1, ts + 0.5))
    # Neue Gäste von der Fähre ziehen in die ungeraden Zimmer
    if T >= t_new:
        for j, n in enumerate(range(1, 16, 2)):
            ts = t_new + j * 0.12
            k = ease(T, ts, ts + 1.0)
            x = lerp(door_x(n, cam) - 260, door_x(n, cam), k)
            if k > 0:
                guest(ctx, x, 1290, 1.0, 101 + j * 2 + 1, walk=T * 10 if k < 1 else None, suitcase=True)
    # Karten
    paper_card(ctx, T, TW('jeder') - 0.1, [('SHELLYS ANWEISUNG:', 30, C['ink']), ('ZIMMERNUMMER × 2', 76, C['red'])], 510, 360)
    if T >= t_free and T < t_new + 1.0:
        sticker(ctx, 'UNGERADE ZIMMER: FREI!', 510, 1290, 56, 'green', rot=-2, sc=pop(T, t_free), icon='check')
    elif T >= t_even and T < t_free:
        sticker(ctx, 'ALTE GÄSTE: GERADE ZIMMER', 510, 1290, 48, 'blue', rot=2, sc=pop(T, t_even))
    if T >= t_new:
        sticker(ctx, '∞ FREIE ZIMMER FÜR ∞ GÄSTE', 510, 1290, 46, 'yellow', rot=-2, sc=pop(T, TW('davon') - 0.1) if T < t_new else 1.0)


def sc_still_full(ctx, T, t0):
    night_sky(ctx, T, 820)
    sea_band(ctx, T, 760, 900)
    sand(ctx, 900, H)
    t_h = TW('hilbert') - 0.2
    sk = 1.0
    sign = 'HOTEL SANDKORN'
    if T >= t_h:
        sign = "HILBERTS HOTEL"
        sk = max(0.01, back_out(T, t_h, t_h + 0.3, 2.0))
    facade(ctx, T, sign=sign, belegt=1.0, sign_k=sk)
    neon_belegt(ctx, 760, 640, T)
    shelly_owner(ctx, T, 760, 1300, 1.35, 'cheer', 'open')
    if T < t_h:
        sticker(ctx, 'IMMER NOCH AUSGEBUCHT', 510, 540, 56, 'red', rot=-2, sc=pop(T, TW('ausgebucht', 1) - 0.1))
    else:
        paper_card(ctx, T, t_h, [('MATHEMATIKER NENNEN DAS', 30, C['ink']), ('HILBERTS HOTEL', 76, C['navy'])], 510, 540)


def sc_ferries(ctx, T, t0):
    night_sky(ctx, T, 700)
    sea_band(ctx, T, 660, 1300)
    sand(ctx, 1300, H)
    for i in range(40, 0, -1):
        f = 1.0 / (1 + 0.45 * i)
        x = lerp(820, 300, f) + math.sin(i * 1.7) * 140 * f
        y = lerp(690, 1290, f)
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(f, f)
        boat(ctx, -280, 0, T + i, 0.25)
        ctx.restore()
    paper_card(ctx, T, TW('was', 0, after=nw('hilbert')) - 0.1,
               [('UND UNENDLICH', 64, C['ink']), ('VIELE FÄHREN?', 64, C['ink']), ('IN DIE KOMMENTARE', 28, C['red'])], 510, 520)


def beach_hut(ctx, x, y, k):
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
    fill_rrect(ctx, -95, -305, 190, 58, 10, C['cream'])
    text(ctx, 'DEIN NAME', 0, -276, 30, C['ink'])
    line(ctx, 0, -247, 0, -236, 6, C['gold2'])
    ctx.restore()


def sc_outro(ctx, T, t0):
    night_sky(ctx, T, 820)
    sea_band(ctx, T, 760, 900)
    sand(ctx, 900, H)
    sticker(ctx, 'WOHNST DU SCHON IN', 510, 430, 56, 'cream', rot=-2, sc=pop(T, TW('wohnst') - 0.05))
    sticker(ctx, 'MUSCHELTAL?', 510, 540, 84, 'yellow', rot=2, sc=pop(T, TW('muscheltal') - 0.05))
    kh = back_out(T, TW('hütte') - 0.2, TW('hütte') + 0.15, 2.0) if T >= TW('hütte') - 0.2 else 0.0
    beach_hut(ctx, 790, 1240, kh)
    tf = TW('folge') - 0.05
    tap = TW('namen') + 0.3
    if T >= tf:
        if T < tap:
            sticker(ctx, '+ FOLGEN', 510, 680, 60, 'red', sc=pop(T, tf))
        else:
            sticker(ctx, 'GEFOLGT', 510, 680, 60, 'green', sc=lerp(0.9, 1.0, back_out(T, tap, tap + 0.3)), icon='check')
    sticker(ctx, 'HÜTTE MIT DEINEM NAMEN', 510, 820, 44, 'white', sc=pop(T, TW('hütte')))
    shelly_owner(ctx, T, 380, 1300, 1.45, 'wave', 'open', tag=False)


# ---------------------------------------------------------------- Zeitleiste
SC = [
    ('hook', 0.0, None),
    ('owner', nw('shelly', 0) - 0.1, sc_owner),
    ('sand', nw('es', 0) - 0.1, sc_sand),
    ('endless', nw('zimmer', 1) - 0.1, sc_endless),
    ('full', nw('heute') - 0.25, sc_full),
    ('ferry', nw('da') - 0.1, sc_ferry),
    ('want', nw('und', 0, after=nw('gästen')) - 0.1, sc_want),
    ('instr', nw('shelly', 1) - 0.1, sc_instruction),
    ('question', nw('welche') - 0.1, sc_question),
    ('solution', TW('hier') - 0.1, sc_solution),
    ('still', TW('und', 0, after=nw('fähre', 1)) - 0.1, sc_still_full),
    ('ferries', TW('und', 0, after=nw('hilbert') + 0.3) - 0.1, sc_ferries),
    ('outro', TW('und', 0, after=nw('kommentare', 1) + 0.1) - 0.1, sc_outro),
]


def frame(ctx, T):
    cur = SC[0]
    for s_ in SC:
        if T >= s_[1]:
            cur = s_
    if cur[0] == 'hook':
        sc_hook(ctx, T)
    else:
        cur[2](ctx, T, cur[1])
    if cur[0] == 'solution' and T < TW('jeder') - 0.1 and UI_ON[0]:
        sticker(ctx, 'DIE LÖSUNG', 510, 560, 80, 'green', rot=-3, sc=pop(T, cur[1] + 0.05))
    subtitles(ctx, T, start=SC[1][1])
    for s_ in SC[1:]:
        if 0 <= T - s_[1] < 0.08:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.35 * (1 - (T - s_[1]) / 0.08)))
