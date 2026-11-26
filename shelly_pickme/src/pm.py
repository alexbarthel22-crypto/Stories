"""Shelly – Pick-Me-Girl. Kapitel mit Strahlen-Hintergrund, Info-Karte, Shelly und Untertiteln."""
import json, math, os, random, re, difflib
import cairo
from draw import *
from chars import shelly, person

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NEW = json.load(open(f'{ROOT}/audio/vo_words.json'))
VO_END = NEW[-1][2] + 0.3
END = VO_END + 1.6


def _norm(w):
    w = re.sub(r"[^\wäöüß']", '', w.lower()).replace('ß', 'ss')
    return {'7': 'sieben', 'hasse': 'hasse'}.get(w, w)


def TW(prefix, k=0, end=False, after=-1.0):
    hits = [w for w in NEW if _norm(w[0]) == prefix and w[1] > after]
    if len(hits) <= k:
        hits = [w for w in NEW if _norm(w[0]).startswith(prefix) and w[1] > after]
    return hits[k][2 if end else 1]


BL = [1.4, 4.1, 7.3, 10.9, 14.2, 18.8, 22.5, 26.1, 30.4, 34.9, 38.2, 42.6, 47.1, 51.3, 55.8, 59.0]


def blink(T):
    return 1.0 if any(0 <= T - b < 0.12 for b in BL) else 0.0


# ---------------------------------------------------------------- Kapitel
CH = [
    # key, start, Titel, Uhrzeit, Icon, Farbe1, Farbe2
    ('intro', 0.0, None, None, None, '#E95C9C', '#F27BB0'),
    ('was', TW('ein', 1) - 0.1, 'WAS IST EIN PICK-ME-GIRL?', None, None, '#7B5CD6', '#8E72E0'),
    ('morgen', TW('sieben') - 0.1, 'GUTEN MORGEN', '07:00', 'sun', '#F2A23C', '#F6B65E'),
    ('strand', TW('am', 1) - 0.1, 'AM STRAND', '10:00', 'sun', '#2BB3C6', '#4CC4D4'),
    ('mittag', TW('mittags') - 0.1, 'MITTAGSPAUSE', '12:00', 'sun', '#53B97A', '#6BC98E'),
    ('social', TW('in', 0) - 0.1, 'SOCIAL MEDIA', '15:00', 'sun', '#E86FA6', '#EE8DBA'),
    ('party', TW('abends') - 0.1, 'DIE STRANDPARTY', '19:00', 'moon', '#E5675B', '#EC8378'),
    ('chat', TW('jonas') - 0.35, 'DIE NACHRICHT', '21:00', 'moon', '#24345F', '#2F4274'),
    ('flags', TW('diesen') - 0.45, 'DIE 4 RED FLAGS', None, None, '#D9473F', '#E2615A'),
    ('outro', TW('kennst') - 0.1, None, None, None, '#2BB3C6', '#4CC4D4'),
]


def chapter(T):
    cur = CH[0]
    for c in CH:
        if T >= c[1]:
            cur = c
    return cur


# ---------------------------------------------------------------- Hintergrund
def sunburst(ctx, T, c1, c2):
    rect(ctx, 0, 0, W, H, hexc(c1))
    cx, cy = 540, 1150
    n = 22
    rot = T * 0.06
    for i in range(n):
        if i % 2:
            continue
        a0 = rot + i / n * 2 * math.pi
        a1 = rot + (i + 1) / n * 2 * math.pi
        poly(ctx, [(cx, cy), (cx + math.cos(a0) * 2600, cy + math.sin(a0) * 2600),
                   (cx + math.cos(a1) * 2600, cy + math.sin(a1) * 2600)], hexc(c2))
    g = cairo.RadialGradient(cx, cy, 200, cx, cy, 1400)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.12)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.18)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()
    # Meer-Vibe: Blasen + treibende Muscheln/Seesterne
    r = random.Random(7)
    for i in range(26):
        x = r.uniform(0, W)
        y = (r.uniform(0, H) - T * r.uniform(25, 60)) % (H + 100) - 50
        ctx.new_sub_path()
        ctx.arc(x + math.sin(T + i) * 8, y, r.uniform(5, 14), 0, 2 * math.pi)
        ctx.set_line_width(3)
        src(ctx, alpha(C['white'], 0.35))
        ctx.stroke()
    for i in range(7):
        x = r.uniform(40, W - 40)
        y = r.uniform(150, 1800)
        ctx.save()
        ctx.translate(x, y + math.sin(T * 1.3 + i) * 12)
        ctx.rotate(math.sin(T * 0.8 + i) * 0.3)
        if i % 2:
            shell_icon(ctx, 0, 0, r.uniform(0.9, 1.4), alpha(C['white'], 0.28))
        else:
            star_icon(ctx, 0, 0, r.uniform(16, 24), alpha(C['white'], 0.28))
        ctx.restore()
    # Wellen unten
    for k, (yy, a) in enumerate([(1760, 0.25), (1810, 0.35)]):
        ctx.move_to(0, H)
        for x in range(0, W + 41, 40):
            ctx.line_to(x, yy + math.sin(x / 90 + T * 2 + k) * 14)
        ctx.line_to(W, H)
        ctx.close_path()
        src(ctx, alpha(C['white'], a))
        ctx.fill()


def shell_icon(ctx, x, y, s, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 16)
    for i in range(9):
        a = math.radians(200 + i * 140 / 8)
        ctx.line_to(math.cos(a) * 26, math.sin(a) * 26 + 6)
    ctx.close_path()
    src(ctx, c)
    ctx.fill()
    for i in range(1, 8):
        a = math.radians(200 + i * 140 / 8)
        line(ctx, 0, 14, math.cos(a) * 22, math.sin(a) * 22 + 6, 2, alpha(C['ink'], 0.15))
    ctx.restore()


def star_icon(ctx, x, y, r, c, rot=0.0):
    pts = []
    for i in range(10):
        a = rot + i * math.pi / 5 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    poly(ctx, pts, c)


def heart(ctx, x, y, s, c):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 8)
    ctx.curve_to(-22, -6, -12, -24, 0, -12)
    ctx.curve_to(12, -24, 22, -6, 0, 8)
    src(ctx, c)
    ctx.fill()
    ctx.restore()


def sparkle(ctx, x, y, r, c):
    poly(ctx, [(x, y - r), (x + r * 0.25, y - r * 0.25), (x + r, y), (x + r * 0.25, y + r * 0.25), (x, y + r),
               (x - r * 0.25, y + r * 0.25), (x - r, y), (x - r * 0.25, y - r * 0.25)], c)


def red_flag(ctx, x, y, s):
    line(ctx, x, y, x, y - 44 * s, 4 * s, C['ink'])
    poly(ctx, [(x, y - 44 * s), (x + 30 * s, y - 36 * s), (x, y - 26 * s)], C['red'])


# ---------------------------------------------------------------- Kopf / Text
def outlined(ctx, s, x, y, size, fill, stroke=None, sw=None, align='c'):
    if not UI_ON[0]:
        return
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    xx = x - e.x_advance / 2 if align == 'c' else x
    ctx.move_to(xx, y + size * 0.36)
    ctx.text_path(s)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(sw or size * 0.2)
    src(ctx, stroke or C['ink'])
    ctx.stroke_preserve()
    src(ctx, fill)
    ctx.fill()


def header(ctx, T, ch):
    key, t0, title, clock, icon = ch[0], ch[1], ch[2], ch[3], ch[4]
    if clock:
        def d(c):
            if icon == 'sun':
                sun_icon(c, -62, 0, 11)
            else:
                moon_icon(c, -62, 0, 15, C['navy'])
            text(c, clock, 18, 0, 36, C['white'])
        chip(ctx, 540, 300, 62, d, 200, pop(T, t0, 0.3))
    if title:
        k = back_out(T, t0, t0 + 0.3, 1.8) if T >= t0 else 0
        ctx.save()
        ctx.translate(540, 385)
        ctx.scale(max(k, 0.01), max(k, 0.01))
        size = 62 if len(title) < 18 else 54
        outlined(ctx, title, 0, 0, size, C['white'])
        ctx.restore()


def card(ctx, T, t0, x0=170, y0=470, w=740, h=560, col=None):
    """Weiße Info-Karte: Pop-in, danach schwebt und wackelt sie leicht."""
    k = back_out(T, t0, t0 + 0.32, 1.7) if T >= t0 else 0.0
    if k <= 0.001:
        return 0.0
    ctx.save()
    cx, cy = x0 + w / 2, y0 + h / 2
    ctx.translate(cx, cy + math.sin(T * 1.7 + x0) * 7)
    ctx.rotate(math.sin(T * 1.2 + y0) * 0.012 + (1 - min(1, (T - t0) / 0.4)) * 0.08)
    ctx.scale(k, k)
    ctx.translate(-cx, -cy)
    fill_rrect(ctx, x0 + 8, y0 + 14, w, h, 30, alpha(C['shadow'], 0.22))
    fill_rrect(ctx, x0, y0, w, h, 30, col or C['white'])
    return k


def card_end(ctx):
    ctx.restore()


def bubble(ctx, T, t0, s, x, y, size=34, style='yellow', maxw=600, tail=None):
    """Sprechblase (kräftige Farbe + dunkler Rand, hebt sich vom Hintergrund ab)."""
    if not UI_ON[0] or T < t0:
        return
    k = back_out(T, t0, t0 + 0.28, 2.0)
    if k <= 0.001:
        return
    words = s.split()
    lines, cur = [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if text_size(ctx, t, size, FONT2)[0] > maxw and cur:
            lines.append(cur); cur = w_
        else:
            cur = t
    lines.append(cur)
    tw = max(text_size(ctx, l, size, FONT2)[0] for l in lines)
    lh = size * 1.25
    bw, bh = tw + size * 1.2, len(lines) * lh + size * 0.7
    bg, fg = {'white': (C['white'], C['ink']), 'blue': (hexc('#2F80ED'), C['white']), 'grey': (hexc('#E9EBF0'), C['ink']),
              'yellow': (C['yellow'], C['ink']), 'red': (C['red'], C['white'])}[style]
    border = style in ('yellow', 'red', 'white')
    ctx.save()
    ctx.translate(x, y + math.sin(T * 3 + x) * 3)
    ctx.scale(k, k)
    fill_rrect(ctx, -bw / 2 + 5, -bh / 2 + 9, bw, bh, size * 0.6, alpha(C['shadow'], 0.25))
    if tail:
        tx, ty = tail[0] - x, tail[1] - y
        if border:
            poly(ctx, [(-24, bh / 2 - 8), (24, bh / 2 - 8), (tx, ty + 6)], C['ink'])
        poly(ctx, [(-18, bh / 2 - 6), (18, bh / 2 - 6), (tx, ty)], bg)
    if border:
        fill_rrect(ctx, -bw / 2 - 5, -bh / 2 - 5, bw + 10, bh + 10, size * 0.6 + 5, C['ink'])
    fill_rrect(ctx, -bw / 2, -bh / 2, bw, bh, size * 0.6, bg)
    for i, l in enumerate(lines):
        text(ctx, l, 0, -bh / 2 + size * 0.35 + lh * (i + 0.5), size, fg, font=FONT2)
    ctx.restore()


def stamp(ctx, T, t0, s, x, y, size=44, rot=-12):
    if not UI_ON[0] or T < t0:
        return
    k = lerp(2.2, 1.0, 1 - (1 - clamp((T - t0) / 0.18)) ** 3)
    tw = text_size(ctx, s, size)[0]
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(rot))
    ctx.scale(k, k)
    rrect(ctx, -tw / 2 - 22, -size * 0.75, tw + 44, size * 1.5, 12)
    src(ctx, alpha(C['white'], 0.85))
    ctx.fill_preserve()
    ctx.set_line_width(7)
    src(ctx, C['red'])
    ctx.stroke()
    text(ctx, s, 0, 0, size, C['red'])
    ctx.restore()


# ---------------------------------------------------------------- Figuren-Extras
def boy(ctx, x, y, s, hair, shirt, skin='#F2C6A0', mood=0.0, style=0, look=0.0, body=True):
    """Junge als Brustbild mit Details (Haarschnitt, Ohren, Brauen, Kragen, Schattierung). y = Unterkante."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    sh = hexc(shirt)
    if body:
        fill_rrect(ctx, -36, -48, 72, 52, 24, sh)
        fill_rrect(ctx, -36, -48, 30, 52, 24, mixc(sh, C['white'], 0.12))
        poly(ctx, [(-12, -48), (0, -36), (12, -48)], mixc(sh, C['ink'], 0.25))
    rect(ctx, -7, -60, 14, 14, mixc(hexc(skin), C['ink'], 0.1))
    for ex in (-28, 28):
        circle(ctx, ex, -84, 6.5, mixc(hexc(skin), C['ink'], 0.06))
    circle(ctx, 0, -86, 28, hexc(skin))
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
    line(ctx, -14, -114, 4, -112, 3, alpha(C['white'], 0.35))
    for sx in (-10, 10):
        line(ctx, sx - 5, -97, sx + 5, -98 - (1.5 if mood > 0 else 0), 2.4, mixc(hc, C['ink'], 0.3))
        ellipse(ctx, sx + look * 3, -86, 3.6, 4.4, C['ink'])
        circle(ctx, sx + look * 3 + 1.2, -87.5, 1.2, C['white'])
    line(ctx, 0, -84, -2, -78, 2, alpha(C['ink'], 0.25))
    ellipse(ctx, -16, -76, 5, 3, alpha(hexc('#F27B95'), 0.35))
    ellipse(ctx, 16, -76, 5, 3, alpha(hexc('#F27B95'), 0.35))
    if mood > 0:
        ctx.move_to(-8, -71)
        ctx.curve_to(-3, -64, 3, -64, 8, -71)
    elif mood < 0:
        ctx.move_to(-7, -66)
        ctx.curve_to(-3, -71, 3, -71, 7, -66)
    else:
        ctx.move_to(-6, -69)
        ctx.line_to(6, -69)
    ctx.set_line_width(2.6)
    src(ctx, hexc('#8A3B3B'))
    ctx.stroke()
    ctx.restore()


def boy_full(ctx, x, y, s, hair, shirt, shorts='#2B3A66', style=0, arms_up=0.0, T=0.0):
    """Junge als ganze Figur (Füße bei y)."""
    skin = hexc('#F2C6A0')
    sh = hexc(shirt)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 1, 26, 5, alpha(C['shadow'], 0.18))
    for side in (-1, 1):
        line(ctx, side * 8, -40, side * 9, -6, 7, mixc(skin, C['ink'], 0.08))
        ellipse(ctx, side * 10, -4, 9, 5, C['white'])
        ellipse(ctx, side * 10, -2, 9, 3, hexc('#3A3F4F'))
    fill_rrect(ctx, -18, -56, 36, 22, 6, hexc(shorts))
    ctx.restore()
    # Kopf ohne eigenen Oberkörper
    boy(ctx, x, y - 54 * s, s * 0.95, hair, shirt, mood=1, style=style, body=False)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    fill_rrect(ctx, -19, -98, 38, 46, 12, sh)
    fill_rrect(ctx, -19, -98, 15, 46, 12, mixc(sh, C['white'], 0.12))
    poly(ctx, [(-8, -98), (0, -90), (8, -98)], mixc(sh, C['ink'], 0.25))
    for side in (-1, 1):
        sx, sy = side * 16, -92
        if arms_up > 0:
            tx, ty = side * 40, -150 + math.sin(T * 6 + side) * 4
        else:
            tx, ty = side * 23, -56
        ex, ey = (sx + tx) / 2 + side * 5, (sy + ty) / 2
        line(ctx, sx, sy, ex, ey, 6.5, skin)
        line(ctx, ex, ey, tx, ty, 6, skin)
        circle(ctx, sx, sy + 1, 7.5, sh)
        circle(ctx, tx, ty, 4.8, skin)
    ctx.restore()


BOYS = [('#4A3426', '#3FA7D6'), ('#E2B65A', '#E2574C'), ('#1F1B1B', '#F2A23C'), ('#8A4A2B', '#53B97A'), ('#C9C3BC', '#7B5CD6')]


def phone(ctx, x, y, s=1.0, ang=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    fill_rrect(ctx, -12, -22, 24, 44, 5, C['ink'])
    fill_rrect(ctx, -9, -18, 18, 34, 3, hexc('#7FD0F0'))
    ctx.restore()


def shelly_main(ctx, T, pose='idle', expr='smile', x=540, feet=1470, s=2.05, phone_on=False, name=True, look=(0, 0)):
    arms = None
    wv = math.sin(T * 8) * 10
    if pose == 'wave':
        arms = {'R': (32 + wv * 0.2, -140 + wv)}
    elif pose == 'pick':
        arms = {'R': (14, -168 + abs(math.sin(T * 9)) * 8)}
    elif pose == 'phone':
        arms = {'R': (16, -112)}
    elif pose == 'hip':
        arms = {'R': (27, -72), 'L': (-27, -72)}
    elif pose == 'shrug':
        arms = {'R': (40, -106), 'L': (-40, -106)}
    elif pose == 'cheer':
        arms = {'R': (30, -150 + wv), 'L': (-30, -150 - wv)}
    elif pose == 'hair':
        arms = {'R': (22, -150), 'L': (-27, -72)}
    bob = math.sin(T * 2.2) * 4
    out = shelly(ctx, x, feet + bob, s, arms=arms, expr=expr, blink=blink(T), look=look)
    if phone_on and 'R' in out:
        hx, hy = out['R']
        phone(ctx, hx + 6, hy - 22, s * 0.9, 0.15)
    if name and UI_ON[0]:
        fill_rrect(ctx, x - 52, feet - 455, 104, 36, 10, C['navy'])
        text(ctx, 'Shelly', x, feet - 437, 24, C['white'])
    return out


# ---------------------------------------------------------------- Kapitel-Inhalte
def sc_intro(ctx, T):
    """Thema sofort: riesiges PICK-ME-GIRL mit Blitz, Strahlen, Glitzerregen, Herzen."""
    # rotierende Lichtstrahlen + Glitzerregen
    r = random.Random(3)
    for i in range(40):
        x = r.uniform(0, W)
        y = (r.uniform(-200, H) + T * r.uniform(250, 450)) % (H + 200) - 100
        rot = T * r.uniform(-4, 4)
        kind = i % 4
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        if kind == 0:
            heart(ctx, 0, 0, r.uniform(1.0, 1.8), C['red'])
        elif kind == 1:
            sparkle(ctx, 0, 0, r.uniform(14, 26), C['yellow'])
        elif kind == 2:
            shell_icon(ctx, 0, 0, r.uniform(0.8, 1.2), C['pink3'])
        else:
            star_icon(ctx, 0, 0, r.uniform(12, 20), hexc('#FF8A5B'))
        ctx.restore()
    if T < 0.25:
        rect(ctx, 0, 0, W, H, alpha(C['white'], 0.7 * (1 - T / 0.25)))
    if UI_ON[0]:
        outlined(ctx, 'Heute ist Shelly', 540, 330, 54, C['white'], sw=10)
        # Riesiges Thema: Punch-in + Puls + Wackeln
        k = lerp(1.12, 1.0, 1 - (1 - clamp(T / 0.3)) ** 3)
        puls = 1 + 0.05 * math.sin(T * 7)
        ang = math.sin(T * 5) * 0.05 * max(0.3, 1 - T / 2)
        ctx.save()
        ctx.translate(540, 500)
        ctx.rotate(ang - 0.05)
        ctx.scale(k * puls, k * puls)
        tw = text_size(ctx, 'PICK-ME-GIRL', 118)[0]
        fill_rrect(ctx, -tw / 2 - 40 + 8, -95 + 12, tw + 80, 190, 40, alpha(C['shadow'], 0.3))
        fill_rrect(ctx, -tw / 2 - 40, -95, tw + 80, 190, 40, C['yellow'])
        rrect(ctx, -tw / 2 - 40, -95, tw + 80, 190, 40)
        ctx.set_line_width(8)
        src(ctx, C['ink'])
        ctx.stroke()
        text(ctx, 'PICK-ME-GIRL', 0, 0, 118, C['ink'])
        ctx.restore()
        # Funkelsterne um den Titel
        for i in range(6):
            a = T * 2 + i * math.pi / 3
            sparkle(ctx, 540 + math.cos(a) * 470, 500 + math.sin(a) * 140, 18 + 8 * math.sin(T * 6 + i), C['white'])
    shelly_main(ctx, T, 'hair', 'open', feet=1440, s=2.4)


def sc_was(ctx, T, ch):
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 190, 470, 700, 420)
    if k:
        text(ctx, 'DIE AUSWAHL', 540, 520, 30, C['ink'])
        happy = T > TW('ausgewählt')
        for i, (hc, sc) in enumerate(BOYS):
            bx = 270 + i * 135
            boy(ctx, bx, 760, 1.35, hc, sc, mood=1 if happy else 0)
            if happy and UI_ON[0]:
                heart(ctx, bx, 610 + math.sin(T * 5 + i) * 6, 0.9, C['red'])
        card_end(ctx)
    sticker(ctx, 'PICK ME!', 540, 960, 46, 'yellow', rot=-3, sc=pop(T, TW('ausgewählt')) if T < TW('lieblings') else 0)
    bubble(ctx, T, TW('lieblings') + 0.5, 'Ich bin nicht wie die anderen Mädchen.', 540, 975, 34, 'yellow', 640, tail=(540, 1040))
    pick = TW('jungs') - 0.1 <= T < TW('lieblings')
    shelly_main(ctx, T, 'pick' if pick else ('hair' if T >= TW('lieblings') else 'idle'),
                'open' if pick else 'smile')


def sc_morgen(ctx, T, ch):
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 330, 450, 420, 640, C['ink'])
    if k:
        fill_rrect(ctx, 348, 470, 384, 600, 20, C['white'])
        circle(ctx, 380, 500, 14, C['pink'])
        text(ctx, 'shelly.natural', 470, 500, 20, C['ink'], font=FONT2)
        # Foto: Sonnenaufgang am Meer + Selfie
        vgrad(ctx, 358, 525, 364, 330, [(0, hexc('#FFB45A')), (0.55, hexc('#FFD9A0')), (0.56, hexc('#3FB6D9')), (1, hexc('#2A8FBF'))])
        circle(ctx, 640, 700, 46, hexc('#FFF2B0'))
        ctx.save()
        rrect(ctx, 358, 525, 364, 330, 0)
        ctx.clip()
        shelly(ctx, 470, 1000, 1.55, expr='smile', look=(2, 0))
        ctx.restore()
        if T > TW('ungeschminkt'):
            text(ctx, 'ungeschminkt :)', 540, 885, 26, C['ink'], font=FONT2)
            text(ctx, '#natural #nomakeup', 540, 925, 22, hexc('#2F80ED'), font=FONT2)
        heart(ctx, 380, 985, 1.0, C['red'])
        text(ctx, '1.284', 440, 978, 22, C['ink'], font=FONT2)
        card_end(ctx)
    stamp(ctx, T, TW('stunde') - 0.1, '1 STUNDE MAKE-UP', 540, 780, 46, -10)
    shelly_main(ctx, T, 'phone', 'smile', phone_on=True)


def shell_necklace(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_sub_path()
    ctx.arc(0, -20, 60, math.radians(20), math.radians(160))
    ctx.set_line_width(4)
    src(ctx, C['gold2'])
    ctx.stroke()
    for i in range(7):
        a = math.radians(30 + i * 20)
        shell_icon(ctx, math.cos(a) * 60, -20 + math.sin(a) * 60, 0.45, [C['pink3'], C['cream'], hexc('#F9B6A0')][i % 3])
    ctx.restore()


def sc_strand(ctx, T, ch):
    """Sie lästert vor den Jungs über die anderen Mädchen."""
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 170, 470, 740, 400, hexc('#BFE8FF'))
    if k:
        rect(ctx, 170, 700, 740, 170, hexc('#F3D9A4'))
        rect(ctx, 170, 660, 740, 44, hexc('#3FB6D9'))
        for i in range(8):
            line(ctx, 190 + i * 90 + math.sin(T * 2 + i) * 8, 680, 230 + i * 90 + math.sin(T * 2 + i) * 8, 680, 4, alpha(C['white'], 0.6))
        circle(ctx, 820, 540, 40, hexc('#FFF2B0'))
        sad = T >= TW('oberflächlich') - 0.2
        # andere Mädchen links
        for i, who in enumerate(('sophia', 'laura')):
            person(ctx, who, 250 + i * 95, 860 + math.sin(T * 3 + i) * 2, 0.95, 1.0 if sad else 0.0, T)
        # Jungs rechts, lachen
        for i, (hc, sc_) in enumerate(BOYS[:3]):
            boy(ctx, 650 + i * 95, 870 + abs(math.sin(T * 4 + i)) * -6, 1.0, hc, sc_, mood=1, style=i % 3, look=-1)
        # Shelly flüstert in der Mitte
        shelly(ctx, 500, 865, 0.95, arms={'R': (14, -124)}, expr='smile', look=(4, 0), blink=blink(T))
        if T >= TW('lästert'):
            for j in range(3):
                kk = ((T - TW('lästert')) * 1.5 + j / 3) % 1
                ctx.save()
                ctx.translate(560 + kk * 90, 690 - kk * 50)
                text(ctx, 'bla', 0, 0, 22 + 8 * (1 - kk), alpha(C['ink'], 1 - kk))
                ctx.restore()
        if sad:
            cloud_shape(ctx, 300, 590 + math.sin(T * 2) * 4, 40, hexc('#8A93A6'))
            for j in range(4):
                yy = 630 + ((T * 160 + j * 30) % 80)
                line(ctx, 280 + j * 14, yy, 276 + j * 14, yy + 12, 3, hexc('#4FA3E8'))
        card_end(ctx)
    if TW('sind') - 0.25 <= T < TW('ich', 1) - 0.05:
        bubble(ctx, T, TW('sind') - 0.25, 'Die sind doch alle so oberflächlich.', 540, 935, 34, 'yellow', 640, tail=(540, 1010))
    elif T >= TW('ich', 1) - 0.05:
        bubble(ctx, T, TW('ich', 1) - 0.05, 'Ich bin eher so der Kumpel-Typ.', 540, 935, 34, 'yellow', 640, tail=(540, 1010))
    shelly_main(ctx, T, 'hip' if T < TW('ich', 1) else 'hair', 'smile')


def burger(ctx, x, y, s, T=0.0):
    """Detaillierter Fischburger: Sesambrötchen mit Glanz, Salat, Tomate, Käse, panierter Fisch, Soße, Dampf."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 132, 150, 16, alpha(C['shadow'], 0.18))
    # Teller
    ellipse(ctx, 0, 124, 150, 22, hexc('#FFFFFF'))
    ellipse(ctx, 0, 120, 130, 15, hexc('#EEF1F5'))
    # Unterteil Brötchen
    g = cairo.LinearGradient(0, 86, 0, 124)
    g.add_color_stop_rgba(0, *hexc('#E6A04A')); g.add_color_stop_rgba(1, *hexc('#C47A2C'))
    rrect(ctx, -112, 86, 224, 36, 18); ctx.set_source(g); ctx.fill()
    # Soße (Tropfen)
    rect(ctx, -108, 78, 216, 10, hexc('#FFF3D6'))
    for dx in (-70, -10, 55):
        ellipse(ctx, dx, 90, 7, 10, hexc('#FFF3D6'))
    # panierter Fisch
    g = cairo.LinearGradient(0, 44, 0, 82)
    g.add_color_stop_rgba(0, *hexc('#F5C266')); g.add_color_stop_rgba(1, *hexc('#D9922F'))
    rrect(ctx, -118, 44, 236, 38, 18); ctx.set_source(g); ctx.fill()
    r = random.Random(2)
    for i in range(40):
        circle(ctx, r.uniform(-110, 110), r.uniform(48, 78), r.uniform(1.2, 2.6), alpha(hexc('#B5701E'), 0.6))
    poly(ctx, [(118, 63), (152, 40), (146, 63), (152, 86)], hexc('#E7A54C'))
    # Käse mit Tropfen
    poly(ctx, [(-105, 38), (105, 38), (110, 48), (60, 48), (48, 66), (38, 48), (-30, 48), (-42, 62), (-52, 48), (-110, 48)], hexc('#FFCC33'))
    # Tomaten
    for dx in (-55, 15, 75):
        ellipse(ctx, dx, 32, 38, 9, hexc('#E5484D'))
        ellipse(ctx, dx, 30, 26, 5, hexc('#F07373'))
    # Salat (wellig)
    ctx.move_to(-122, 24)
    for i in range(13):
        xx = -122 + i * 20
        ctx.curve_to(xx + 5, 12, xx + 15, 34, xx + 20, 22)
    ctx.line_to(122, 16)
    ctx.line_to(-122, 16)
    ctx.close_path()
    src(ctx, hexc('#6BC98E'))
    ctx.fill()
    # Oberteil Brötchen mit Glanz
    g = cairo.LinearGradient(0, -70, 0, 20)
    g.add_color_stop_rgba(0, *hexc('#F2B45C')); g.add_color_stop_rgba(1, *hexc('#D48632'))
    ctx.new_sub_path()
    ctx.move_to(-118, 18)
    ctx.curve_to(-118, -62, 118, -62, 118, 18)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()
    ctx.move_to(-70, -24)
    ctx.curve_to(-50, -44, -10, -50, 20, -46)
    ctx.set_line_width(10)
    src(ctx, alpha(C['white'], 0.35))
    ctx.stroke()
    for i in range(16):
        a = r.uniform(-2.7, -0.4)
        rr = r.uniform(30, 95)
        ellipse(ctx, math.cos(a) * rr, 10 + math.sin(a) * rr * 0.6, 4, 2.4, hexc('#FFF6DC'))
    # Fähnchen-Spieß
    line(ctx, 0, -90, 0, -40, 3, hexc('#B98450'))
    poly(ctx, [(0, -90), (34, -82), (0, -74)], C['pink'])
    # Dampf
    for j in range(3):
        kk = ((T * 0.6 + j / 3) % 1)
        ctx.move_to(-40 + j * 40, -60 - kk * 60)
        ctx.curve_to(-50 + j * 40, -75 - kk * 60, -30 + j * 40, -85 - kk * 60, -40 + j * 40, -100 - kk * 60)
        ctx.set_line_width(5)
        src(ctx, alpha(C['white'], 0.7 * (1 - kk)))
        ctx.stroke()
    ctx.restore()


def salad(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_sub_path()
    ctx.arc(0, 0, 50, 0, math.pi)
    ctx.close_path()
    src(ctx, C['white'])
    ctx.fill()
    for i in range(5):
        circle(ctx, -32 + i * 16, -6 - (i % 2) * 6, 14, hexc('#6BC98E'))
    circle(ctx, 10, -12, 7, C['red'])
    ctx.restore()


def sc_mittag(ctx, T, ch):
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 190, 470, 700, 380)
    if k:
        rect(ctx, 210, 760, 660, 18, hexc('#C98B5A'))
        burger(ctx, 460, 610, 1.05, T)
        salad(ctx, 760, 720, 0.9)
        text(ctx, 'XXL FISCHBURGER', 470, 810, 22, C['ink'])
        text(ctx, 'SALAT', 760, 810, 22, C['ink'])
        if T >= TW('gegessen'):
            text(ctx, 'GEGESSEN:', 330, 545, 24, C['ink'])
            fill_rrect(ctx, 420, 532, 360, 26, 13, hexc('#E9EBF0'))
            kk = ease(T, TW('gegessen'), TW('gegessen') + 0.5)
            fill_rrect(ctx, 420, 532, max(26, 360 * 0.06 * kk + 20), 26, 13, C['red'])
            text(ctx, '2 BISSEN', 830, 545, 22, C['red'])
        card_end(ctx)
    if TW('ich', 2) - 0.1 <= T < TW('gegessen') + 0.6:
        bubble(ctx, T, TW('ich', 2) - 0.1, 'Ich esse nicht nur Salat wie andere Mädchen.', 540, 945, 34, 'yellow', 640, tail=(540, 1030))
    shelly_main(ctx, T, 'hip', 'open' if T < TW('gegessen') else 'think')


def sc_social(ctx, T, ch):
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 170, 470, 740, 430)
    if k:
        circle(ctx, 270, 570, 56, C['pink3'])
        ctx.save()
        ctx.new_sub_path()
        ctx.arc(270, 570, 52, 0, 2 * math.pi)
        ctx.clip()
        shelly(ctx, 270, 720, 0.95, expr='smile')
        ctx.restore()
        for i, (n, l) in enumerate([('312', 'Beiträge'), ('9.402', 'Follower'), ('88', 'Gefolgt')]):
            text(ctx, n, 450 + i * 150, 552, 28, C['ink'])
            text(ctx, l, 450 + i * 150, 586, 18, C['grey'], font=FONT2)
        text(ctx, '@shelly.nicht.wie.die.anderen', 230, 660, 24, C['ink'], font=FONT2, align='l')
        lines = [(TW('ich', 3) - 0.1, 'nur beste Freunde, keine Freundinnen'), (TW('mädchen', 3) - 0.1, 'Mädchen = nur Drama')]
        for i, (ta, l) in enumerate(lines):
            if T >= ta:
                yy = 715 + i * 52
                hl = ease(T, ta, ta + 0.3)
                tw = text_size(ctx, l, 24, FONT2)[0]
                fill_rrect(ctx, 250, yy - 20, (tw + 20) * hl, 40, 8, alpha(C['yellow'], 0.8))
                shell_icon(ctx, 232, yy + 2, 0.45, C['pink2'])
                text(ctx, l, 262, yy, 24, C['ink'], font=FONT2, align='l')
        fill_rrect(ctx, 230, 830, 620, 46, 12, hexc('#E9EBF0'))
        text(ctx, 'Nachricht senden', 540, 853, 22, C['ink'], font=FONT2)
        card_end(ctx)
    shelly_main(ctx, T, 'phone', 'smile', phone_on=True)


def volleyball(ctx, x, y, r):
    circle(ctx, x, y, r, C['white'])
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_line_width(2.5)
    src(ctx, C['ink'])
    ctx.stroke()
    for a in (0.3, 2.4, 4.4):
        ctx.new_sub_path()
        ctx.arc(x + math.cos(a) * r, y + math.sin(a) * r, r * 0.9, a + 2.3, a + 3.9)
        ctx.stroke()


def sc_party(ctx, T, ch):
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 170, 470, 740, 440, hexc('#FFE9C7'))
    if k:
        vgrad(ctx, 170, 470, 740, 190, [(0, hexc('#3B3A7A')), (1, hexc('#E87B6B'))])
        rect(ctx, 170, 660, 740, 250, hexc('#F3D9A4'))
        for i in range(7):
            yy = 500 + (i % 2) * 18
            circle(ctx, 210 + i * 110, yy, 9 + math.sin(T * 6 + i) * 1.5, [C['yellow'], C['pink'], hexc('#7FD0F0')][i % 3])
        line(ctx, 190, 495, 890, 515, 2, alpha(C['white'], 0.6))
        # Spielfeld in Perspektive (vorne breit, hinten schmal)
        poly(ctx, [(230, 880), (850, 880), (760, 720), (320, 720)], alpha(C['white'], 0.0))
        for (p, q) in [((230, 880), (320, 720)), ((850, 880), (760, 720)), ((320, 720), (760, 720)), ((230, 880), (850, 880))]:
            line(ctx, p[0], p[1], q[0], q[1], 3, alpha(C['white'], 0.85))
        # Netz quer zum Feld: vorderer Pfosten groß/unten, hinterer klein/oben
        fx, fb, ft = 528, 878, 640      # vorne: x, Fuß, Spitze
        bx_, bb, bt = 568, 722, 600     # hinten
        n_top_f, n_bot_f = ft + 8, ft + 78
        n_top_b, n_bot_b = bt + 6, bt + 54
        poly(ctx, [(fx, n_top_f), (bx_, n_top_b), (bx_, n_bot_b), (fx, n_bot_f)], alpha(C['white'], 0.25))
        for j in range(1, 8):
            u = j / 8
            line(ctx, lerp(fx, bx_, u), lerp(n_top_f, n_top_b, u), lerp(fx, bx_, u), lerp(n_bot_f, n_bot_b, u), 1.4, alpha(C['ink'], 0.55))
        for j in range(1, 6):
            v = j / 6
            line(ctx, fx, lerp(n_top_f, n_bot_f, v), bx_, lerp(n_top_b, n_bot_b, v), 1.4, alpha(C['ink'], 0.55))
        line(ctx, fx, n_top_f, bx_, n_top_b, 5, C['white'])
        line(ctx, fx, n_bot_f, bx_, n_bot_b, 2.5, C['white'])
        line(ctx, bx_, bb, bx_, bt, 5, C['ink'])
        line(ctx, fx, fb, fx, ft, 8, C['ink'])
        ellipse(ctx, fx, fb, 12, 4, alpha(C['shadow'], 0.3))
        ellipse(ctx, bx_, bb, 7, 2.5, alpha(C['shadow'], 0.3))
        # Shelly links auf dem Feld (springt zum Ball)
        jump = abs(math.sin(T * 2.4)) * 34
        shelly(ctx, 330, 860 - jump, 1.0, arms={'R': (24, -160), 'L': (-24, -160)}, expr='open', blink=blink(T))
        # Jungs rechts
        jb = abs(math.sin(T * 2.4 + 1.2)) * 22
        boy_full(ctx, 700, 862 - jb, 1.0, '#4A3426', '#3FA7D6', '#2B3A66', 0, 1.0, T)
        boy_full(ctx, 815, 866, 1.0, '#E2B65A', '#E2574C', '#3A6F4F', 1, 0.0, T)
        bx = 540 + math.sin(T * 2.4) * 190
        by = 590 - abs(math.cos(T * 2.4)) * 50
        volleyball(ctx, bx, by, 22)
        # Zuschauer unten (nur wenn alle zuschauen)
        if T >= TW('zuschauen') - 0.2:
            for i in range(6):
                hx = 210 + i * 120
                hy = 905 - abs(math.sin(T * 5 + i)) * 8
                boy(ctx, hx, hy, 0.6, BOYS[i % 5][0], BOYS[(i + 2) % 5][1], mood=1, style=i % 3, look=0)
        if T >= TW('als') - 0.1:
            person(ctx, 'laura', 215, 870, 1.05, 0.0, T, mirror=True)
        card_end(ctx)
    if T >= TW('sagt', 0) - 0.1:
        bubble(ctx, T, TW('sagt', 0) - 0.1, 'Das ist eher nichts für Mädchen.', 540, 975, 36, 'red', 620, tail=(540, 1040))
    shelly_main(ctx, T, 'cheer' if T < TW('als') else 'hip', 'open' if T < TW('als') else 'think')


def chat_msg(ctx, T, t0, msg, side, y, time_s, x0=336, x1=744, size=28, maxw=300):
    """Handy-Chat-Nachricht: eingehend links (grau), ausgehend rechts (blau), bündig am Rand, mit Ecke + Uhrzeit."""
    if T < t0:
        return
    k = back_out(T, t0, t0 + 0.22, 1.6)
    if k <= 0.001:
        return
    words = msg.split()
    lines, cur = [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if text_size(ctx, t, size, FONT2)[0] > maxw and cur:
            lines.append(cur); cur = w_
        else:
            cur = t
    lines.append(cur)
    tw = max(text_size(ctx, l, size, FONT2)[0] for l in lines)
    lh = size * 1.25
    bw, bh = tw + 34, len(lines) * lh + 34
    out = side == 'r'
    bg = hexc('#2F80ED') if out else hexc('#E9EBF0')
    fg = C['white'] if out else C['ink']
    bx = x1 - bw if out else x0
    ctx.save()
    ax = x1 if out else x0
    ctx.translate(ax, y + bh)
    ctx.scale(k, k)
    ctx.translate(-ax, -(y + bh))
    fill_rrect(ctx, bx, y, bw, bh, 20, bg)
    # Ecke unten an der Absenderseite
    if out:
        poly(ctx, [(x1 - 22, y + bh - 2), (x1 + 6, y + bh + 4), (x1 - 2, y + bh - 18)], bg)
    else:
        poly(ctx, [(x0 + 22, y + bh - 2), (x0 - 6, y + bh + 4), (x0 + 2, y + bh - 18)], bg)
    for i, l in enumerate(lines):
        text(ctx, l, bx + 17, y + 17 + lh * (i + 0.5), size, fg, font=FONT2, align='l')
    st = time_s + ('  ✓✓' if out else '')
    text(ctx, st, (x1 - 4) if out else (x0 + 4), y + bh + 18, 15, C['grey'], font=FONT2, align='r' if out else 'l')
    ctx.restore()


def sc_chat(ctx, T, ch):
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 300, 440, 480, 650, C['ink'])
    if k:
        fill_rrect(ctx, 316, 456, 448, 618, 22, hexc('#FFFFFF'))
        rect(ctx, 316, 456, 448, 84, hexc('#F4F5F8'))
        line(ctx, 316, 540, 764, 540, 1.5, hexc('#DADDE3'))
        text(ctx, '‹', 336, 498, 40, hexc('#2F80ED'), font=FONT2, align='l')
        circle(ctx, 392, 498, 24, hexc('#CFE9FF'))
        ctx.save()
        ctx.new_sub_path()
        ctx.arc(392, 498, 23, 0, 2 * math.pi)
        ctx.clip()
        boy(ctx, 392, 532, 0.5, '#4A3426', '#3FA7D6', mood=1)
        ctx.restore()
        text(ctx, 'Jonas', 428, 488, 26, C['ink'], align='l')
        text(ctx, 'online', 428, 514, 16, C['green'], font=FONT2, align='l')
        # Eingabezeile
        fill_rrect(ctx, 332, 1020, 360, 40, 20, hexc('#F1F2F5'))
        text(ctx, 'Nachricht', 350, 1040, 18, C['grey'], font=FONT2, align='l')
        circle(ctx, 724, 1040, 20, hexc('#2F80ED'))
        poly(ctx, [(716, 1031), (734, 1040), (716, 1049)], C['white'])
        chat_msg(ctx, T, TW('du', 0) - 0.15, 'Du bist echt cool', 'l', 570, '21:04')
        chat_msg(ctx, T, TW('weiss') - 0.15, 'Ich weiß.', 'r', 680, '21:05')
        chat_msg(ctx, T, TW('ich', 5) - 0.15, 'Ich bin halt nicht wie die anderen.', 'r', 770, '21:05')
        card_end(ctx)
    shelly_main(ctx, T, 'phone', 'smile', phone_on=True, x=720, feet=1480, s=1.9, name=False)


FLAGS = ['Macht andere Mädchen schlecht', 'Spielt eine Rolle für Jungs', 'Hasst Drama – macht Drama',
         'Braucht für alles Publikum']


def sc_flags(ctx, T, ch):
    _n = TW('punkten')
    times = [TW('sie', 0, after=_n) - 0.05, TW('sie', 1, after=_n) - 0.05, TW('sie', 2, after=_n) - 0.05, TW('braucht') - 0.3]
    for i, (ta, l) in enumerate(zip(times, FLAGS)):
        if T < ta:
            continue
        k = back_out(T, ta, ta + 0.3, 1.8)
        if k <= 0.001:
            continue
        y = 480 + i * 118
        ctx.save()
        ctx.translate(540, y)
        ctx.scale(k, k)
        fill_rrect(ctx, -355, -44, 720, 96, 22, alpha(C['shadow'], 0.2))
        fill_rrect(ctx, -360, -50, 720, 96, 22, C['white'])
        circle(ctx, -310, -2, 26, C['red'])
        text(ctx, str(i + 1), -310, -2, 30, C['white'])
        text(ctx, l, -268, -2, 32, C['ink'], font=FONT2, align='l')
        red_flag(ctx, 318, 20, 1.0)
        ctx.restore()
    shelly_main(ctx, T, 'shrug', 'think')
    # rote Fähnchen um Shelly
    for i in range(6):
        a = i / 6 * 2 * math.pi + T * 0.6
        red_flag(ctx, 540 + math.cos(a) * 260, 1250 + math.sin(a) * 90, 1.1)


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
    shell_icon(ctx, 0, -185, 1.1, C['white'])
    fill_rrect(ctx, -95, -305, 190, 58, 10, C['cream'])
    rrect(ctx, -95, -305, 190, 58, 10)
    ctx.set_line_width(4)
    src(ctx, C['gold2'])
    ctx.stroke()
    text(ctx, 'DEIN NAME', 0, -276, 30, C['ink'])
    line(ctx, 0, -247, 0, -236, 6, C['gold2'])
    ctx.restore()


def sc_outro(ctx, T, ch):
    t0 = ch[1]
    t_mus = TW('und', 0, after=TW('markier'))
    if T < t_mus - 0.05:
        sticker(ctx, 'KENNST DU EIN', 510, 470, 66, 'cream', rot=-3, sc=pop(T, t0 + 0.1))
        sticker(ctx, 'PICK-ME-GIRL?', 510, 585, 76, 'yellow', rot=2, sc=pop(T, TW('ein', 0, after=TW('kennst')) - 0.05))
        sticker(ctx, 'MARKIER SIE!', 510, 720, 64, 'red', rot=-2, sc=pop(T, TW('markier') - 0.05))
        shelly_main(ctx, T, 'wave', 'open')
        return
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
        if tap - 0.25 < T < tap + 0.4 and UI_ON[0]:
            kk = clamp((T - tap + 0.25) / 0.65)
            ctx.new_sub_path()
            ctx.arc(570, 690, 30 + 60 * kk, 0, 2 * math.pi)
            ctx.set_line_width(8)
            src(ctx, alpha(C['white'], 0.8 * (1 - kk)))
            ctx.stroke()
    sticker(ctx, 'HÜTTE MIT DEINEM NAMEN', 510, 820, 44, 'white', sc=pop(T, TW('hütte')))
    shelly_main(ctx, T, 'wave', 'open', x=380)


SCENES = {'intro': lambda c, T, ch: sc_intro(c, T), 'was': sc_was, 'morgen': sc_morgen, 'strand': sc_strand,
          'mittag': sc_mittag, 'social': sc_social, 'party': sc_party, 'chat': sc_chat, 'flags': sc_flags,
          'outro': sc_outro}


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
    disp = {'sieben': '7'}
    caps = []
    for t, (a, b) in zip(txt, tm):
        core = re.sub(r'[^\wäöüß]', '', t.lower())
        t2 = t.lower().replace(core, disp[core]) if core in disp else t
        caps.append((t2.upper(), a, b))
    chunks, cur = [], []
    for idx, (t, a, b) in enumerate(caps):
        cur.append(idx)
        if len(cur) >= 3 or t[-1] in '.,?!:' or (idx + 1 < len(caps) and caps[idx + 1][1] - b > 0.4):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return caps, chunks


CAPS, CAP_CHUNKS = _build_caps()


def subtitles(ctx, T, y=1425, size=44):
    if not UI_ON[0] or T < CH[1][1] - 0.05:
        return
    cur = None
    for ch in CAP_CHUNKS:
        if CAPS[ch[0]][1] - 0.06 <= T <= CAPS[ch[-1]][2] + 0.3:
            cur = ch
    if cur is None:
        return
    s = ' '.join(CAPS[i][0] for i in cur)
    tw = text_size(ctx, s, size)[0]
    k = max(0.05, back_out(T, CAPS[cur[0]][1] - 0.06, CAPS[cur[0]][1] + 0.12, 1.6))
    ctx.save()
    ctx.translate(540, y)
    ctx.rotate(math.radians(-1.5))
    ctx.scale(k, k)
    w, h = tw + size * 0.9, size * 1.45
    fill_rrect(ctx, -w / 2 + 4, -h / 2 + 7, w, h, 14, alpha(C['shadow'], 0.3))
    fill_rrect(ctx, -w / 2, -h / 2, w, h, 14, C['cream'])
    x = -tw / 2
    for i in cur:
        t = CAPS[i][0]
        on = CAPS[i][1] - 0.03 <= T < (CAPS[i + 1][1] - 0.03 if i + 1 < len(CAPS) else CAPS[i][2] + 0.3)
        wt = text_size(ctx, t, size)[0]
        text(ctx, t, x + wt / 2, 0, size, C['pink2'] if on else C['ink'])
        x += wt + text_size(ctx, ' ', size)[0]
    ctx.restore()


def frame(ctx, T):
    ch = chapter(T)
    sunburst(ctx, T, ch[5], ch[6])
    header(ctx, T, ch)
    SCENES[ch[0]](ctx, T, ch)
    subtitles(ctx, T)
    # kurzer Blitz beim Kapitelwechsel
    for c in CH[1:]:
        if 0 <= T - c[1] < 0.1:
            rect(ctx, 0, 0, W, H, alpha(C['white'], 0.5 * (1 - (T - c[1]) / 0.1)))
