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
    ('intro', 0.0, None, None, None, '#F27BB0', '#F59BC4'),
    ('was', TW('ein', 1) - 0.1, 'WAS IST EIN PICK-ME-GIRL?', None, None, '#7B5CD6', '#8E72E0'),
    ('morgen', TW('sieben') - 0.1, 'GUTEN MORGEN', '07:00', 'sun', '#F2A23C', '#F6B65E'),
    ('strand', TW('am', 1) - 0.1, 'AM STRAND', '10:00', 'sun', '#2BB3C6', '#4CC4D4'),
    ('mittag', TW('mittags') - 0.1, 'MITTAGSPAUSE', '12:00', 'sun', '#53B97A', '#6BC98E'),
    ('social', TW('in', 0) - 0.1, 'SOCIAL MEDIA', '15:00', 'sun', '#E86FA6', '#EE8DBA'),
    ('party', TW('abends') - 0.1, 'DIE STRANDPARTY', '19:00', 'moon', '#E5675B', '#EC8378'),
    ('chat', TW('junge') - 0.35, 'DIE NACHRICHT', '21:00', 'moon', '#24345F', '#2F4274'),
    ('flags', TW('nervigsten') - 0.25, 'DIE 4 RED FLAGS', None, None, '#D9473F', '#E2615A'),
    ('outro', TW('kennst') - 0.1, None, None, None, '#8E5CD6', '#A274E0'),
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
    """Weiße Info-Karte mit Pop-in. Gibt Skalierung zurück (für Inhalte)."""
    k = back_out(T, t0, t0 + 0.32, 1.7) if T >= t0 else 0.0
    if k <= 0.001:
        return 0.0
    ctx.save()
    cx, cy = x0 + w / 2, y0 + h / 2
    ctx.translate(cx, cy)
    ctx.scale(k, k)
    ctx.translate(-cx, -cy)
    fill_rrect(ctx, x0 + 8, y0 + 14, w, h, 30, alpha(C['shadow'], 0.22))
    fill_rrect(ctx, x0, y0, w, h, 30, col or C['white'])
    return k


def card_end(ctx):
    ctx.restore()


def bubble(ctx, T, t0, s, x, y, size=34, style='white', maxw=600, tail=None):
    """Sprechblase mit Umbruch. tail = (x, y) Spitze."""
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
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    fill_rrect(ctx, -bw / 2 + 4, -bh / 2 + 7, bw, bh, size * 0.6, alpha(C['shadow'], 0.2))
    if tail:
        tx, ty = tail[0] - x, tail[1] - y
        poly(ctx, [(-18, bh / 2 - 6), (18, bh / 2 - 6), (tx, ty)], bg)
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
def boy(ctx, x, y, s, hair, shirt, skin='#F2C6A0', mood=0.0):
    """Junge als Brustbild (Kopf + Schultern), y = Unterkante."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    fill_rrect(ctx, -34, -46, 68, 50, 22, hexc(shirt))
    rect(ctx, -6, -58, 12, 14, hexc(skin))
    circle(ctx, 0, -84, 28, hexc(skin))
    ctx.new_path()
    ctx.arc(0, -86, 29.5, math.radians(185), math.radians(355))
    ctx.close_path()
    src(ctx, hexc(hair))
    ctx.fill()
    for sx in (-10, 10):
        circle(ctx, sx, -82, 3.6, C['ink'])
    if mood > 0:
        ctx.move_to(-7, -71)
        ctx.curve_to(-3, -66, 3, -66, 7, -71)
    else:
        ctx.move_to(-6, -70)
        ctx.line_to(6, -70)
    ctx.set_line_width(2.4)
    src(ctx, hexc('#8A3B3B'))
    ctx.stroke()
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
    flip = TW('ein', 0) - 0.08
    pre = T < flip
    if UI_ON[0]:
        outlined(ctx, 'Heute ist Shelly', 540, 300, 40, C['white'], sw=8)
        k = back_out(T, flip, flip + 0.3, 2.2) if not pre else 1.0
        ctx.save()
        ctx.translate(540, 390)
        ctx.scale(max(0.01, k), max(0.01, k))
        outlined(ctx, 'EINE MEERJUNGFRAU.' if pre else 'EIN PICK-ME-GIRL.', 0, 0, 70 if not pre else 60, C['white'] if pre else C['yellow'])
        ctx.restore()
    # fliegende Deko nach dem Wechsel
    if not pre:
        r = random.Random(3)
        for i in range(16):
            a = r.uniform(0, 2 * math.pi)
            sp = r.uniform(350, 700)
            dt = T - flip
            d = sp * (1 - math.exp(-dt * 2.2))
            x = 540 + math.cos(a) * d
            y = 1000 + math.sin(a) * d * 0.9 + 60 * dt
            kind = i % 4
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(dt * r.uniform(-3, 3))
            if kind == 0:
                heart(ctx, 0, 0, 1.6, C['red'])
            elif kind == 1:
                shell_icon(ctx, 0, 0, 1.2, C['pink3'])
            elif kind == 2:
                sparkle(ctx, 0, 0, 22, C['yellow'])
            else:
                star_icon(ctx, 0, 0, 20, hexc('#FF8A5B'))
            ctx.restore()
    shelly_main(ctx, T, 'wave' if pre else 'hair', 'smile' if pre else 'open', feet=1420, s=2.4)
    if T < flip + 0.12 and T > flip - 0.02:
        rect(ctx, 0, 0, W, H, alpha(C['white'], 0.9))


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
    bubble(ctx, T, TW('lieblings') + 0.5, 'Ich bin nicht wie die anderen Mädchen.', 540, 915, 34, 'white', 560, tail=(540, 980))
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
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 190, 470, 700, 330)
    if k:
        shell_necklace(ctx, 380, 640, 1.6)
        for i, (sx, sy) in enumerate([(640, 590), (700, 660), (610, 690), (760, 600), (680, 560)]):
            sparkle(ctx, sx, sy, 22 - i * 2, C['yellow'])
        text(ctx, 'MUSCHELKETTEN', 380, 760, 22, C['ink'])
        text(ctx, 'GLITZER', 680, 760, 22, C['ink'])
        if T > TW('hasse') + 0.2:
            kk = clamp((T - TW('hasse') - 0.2) / 0.25)
            for cx_ in (380, 680):
                line(ctx, cx_ - 90 * kk, 560, cx_ + 90 * kk, 560 + 180 * kk, 14, C['red'])
                line(ctx, cx_ + 90 * kk, 560, cx_ - 90 * kk, 560 + 180 * kk, 14, C['red'])
        card_end(ctx)
    if T < TW('ich', 2) - 0.05:
        bubble(ctx, T, TW('hasse') - 0.2, 'Ich hasse Muschelketten und Glitzer.', 540, 840, 34, 'white', 600, tail=(540, 930))
    elif T < TW('dabei') - 0.05:
        bubble(ctx, T, TW('ich', 2), 'Ich bin eher so der Kumpel-Typ.', 540, 840, 34, 'white', 600, tail=(540, 930))
    if T >= TW('muschel', 1) - 0.1 and UI_ON[0]:
        # Pfeil auf die Muschel im Haar
        ta = TW('muschel', 1) - 0.1
        kk = ease(T, ta, ta + 0.3)
        hx, hy = 540, 1470 - 165 * 2.05
        line(ctx, 800, 900, lerp(800, hx + 110, kk), lerp(900, hy - 10, kk), 10, C['yellow'])
        if kk > 0.95:
            poly(ctx, [(hx + 96, hy - 30), (hx + 122, hy + 8), (hx + 84, hy + 6)], C['yellow'])
        sticker(ctx, 'MUSCHEL IM HAAR', 760, 860, 40, 'yellow', rot=4, sc=pop(T, ta + 0.2))
    shelly_main(ctx, T, 'hip' if T < TW('dabei') else 'shrug', 'smile' if T < TW('dabei') else 'think')


def burger(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 52, 120, 14, alpha(C['shadow'], 0.15))
    ctx.new_sub_path()
    ctx.arc(0, 30, 110, math.pi, 2 * math.pi)
    ctx.close_path()
    src(ctx, hexc('#E7A54C'))
    ctx.fill()
    for i in range(7):
        ellipse(ctx, -70 + i * 23, -30 - abs(3 - i) * 6, 4, 2.5, C['cream'])
    rect(ctx, -115, 30, 230, 14, hexc('#6BC98E'))
    # Fisch
    fill_rrect(ctx, -112, 44, 224, 30, 14, hexc('#F2C46B'))
    poly(ctx, [(112, 59), (150, 36), (150, 82)], hexc('#F2C46B'))
    rect(ctx, -108, 74, 216, 10, hexc('#F7E07A'))
    fill_rrect(ctx, -110, 84, 220, 36, 16, hexc('#E7A54C'))
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
        burger(ctx, 470, 640, 1.25)
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
    if TW('ich', 3) - 0.1 <= T < TW('gegessen') + 0.6:
        bubble(ctx, T, TW('ich', 3) - 0.1, 'Ich esse nicht nur Salat wie andere Mädchen.', 540, 880, 34, 'white', 620, tail=(540, 970))
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
        lines = [(TW('ich', 4) - 0.1, 'nur beste Freunde, keine Freundinnen'), (TW('mädchen', 2) - 0.1, 'Mädchen = nur Drama')]
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
    k = card(ctx, T, t0 + 0.1, 190, 470, 700, 420, hexc('#FFE9C7'))
    if k:
        vgrad(ctx, 190, 470, 700, 200, [(0, hexc('#3B3A7A')), (1, hexc('#E87B6B'))])
        rect(ctx, 190, 670, 700, 220, hexc('#F3D9A4'))
        for i in range(6):
            circle(ctx, 240 + i * 120, 500 + (i % 2) * 20, 9, [C['yellow'], C['pink'], hexc('#7FD0F0')][i % 3])
        line(ctx, 210, 500, 870, 520, 2, alpha(C['white'], 0.6))
        # Netz
        line(ctx, 540, 640, 540, 860, 6, C['ink'])
        for j in range(5):
            line(ctx, 540, 650 + j * 14, 540, 650 + j * 14, 1, C['ink'])
        fill_rrect(ctx, 535, 640, 10, 80, 3, C['white'])
        boy(ctx, 690, 860, 1.3, '#4A3426', '#3FA7D6', mood=1)
        boy(ctx, 800, 860, 1.3, '#E2B65A', '#E2574C', mood=1)
        bx = 540 + math.sin(T * 2.4) * 160
        by = 600 - abs(math.cos(T * 2.4)) * 60
        volleyball(ctx, bx, by, 22)
        if T >= TW('zuschauen') - 0.1:
            fill_rrect(ctx, 220, 490, 210, 50, 25, alpha(C['ink'], 0.8))
            for e in (0, 1):
                ellipse(ctx, 252 + e * 26, 515, 10, 7, C['white'])
                circle(ctx, 254 + e * 26, 516, 4, C['ink'])
            n = min(48, int((T - TW('zuschauen')) * 60) + 3)
            text(ctx, f'{n} SCHAUEN ZU', 350, 515, 20, C['white'])
        if T >= TW('als') - 0.1:
            person(ctx, 'laura', 300, 880, 1.15, 0.0, T)
        card_end(ctx)
    if T >= TW('sagt', 1) - 0.1:
        bubble(ctx, T, TW('sagt', 1) - 0.1, 'Das ist eher nichts für Mädchen.', 540, 900, 36, 'red', 620, tail=(540, 980))
    shelly_main(ctx, T, 'cheer' if T < TW('als') else 'hip', 'open' if T < TW('als') else 'think')


def sc_chat(ctx, T, ch):
    t0 = ch[1]
    k = card(ctx, T, t0 + 0.1, 300, 440, 480, 650, C['ink'])
    if k:
        fill_rrect(ctx, 316, 456, 448, 618, 22, C['white'])
        rect(ctx, 316, 456, 448, 70, hexc('#F4F5F8'))
        boy(ctx, 360, 520, 0.55, '#4A3426', '#3FA7D6', mood=1)
        text(ctx, 'Jonas', 400, 492, 26, C['ink'], align='l')
        card_end(ctx)
    if k:
        bubble(ctx, T, TW('du', 0) - 0.15, 'Du bist echt cool', 470, 610, 30, 'grey', 300)
        bubble(ctx, T, TW('weiss') - 0.15, 'Ich weiß.', 640, 720, 30, 'blue', 300)
        bubble(ctx, T, TW('ich', 6) - 0.15, 'Ich bin halt nicht wie die anderen.', 560, 830, 30, 'blue', 340)
    shelly_main(ctx, T, 'phone', 'smile', phone_on=True, x=720, feet=1480, s=1.9)


FLAGS = ['Macht andere Mädchen schlecht', 'Spielt eine Rolle für Jungs', 'Hasst Drama – macht Drama',
         'Braucht für alles Publikum']


def sc_flags(ctx, T, ch):
    _n = TW('nervigsten')
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


def sc_outro(ctx, T, ch):
    t0 = ch[1]
    sticker(ctx, 'KENNST DU EIN', 510, 470, 66, 'cream', rot=-3, sc=pop(T, t0 + 0.1))
    sticker(ctx, 'PICK-ME-GIRL?', 510, 585, 76, 'yellow', rot=2, sc=pop(T, TW('pick', 0, after=TW('kennst')) - 0.1))
    sticker(ctx, 'MARKIER SIE!', 510, 720, 64, 'red', rot=-2, sc=pop(T, TW('markier') - 0.05))
    sticker(ctx, 'WAS SOLL SHELLY MORGEN SEIN?', 510, 860, 40, 'white', sc=pop(T, TW('was') - 0.05))
    if UI_ON[0] and T >= TW('was'):
        kk = max(0.01, pop(T, TW('was') + 0.2))
        ctx.save()
        ctx.translate(820, 960)
        ctx.scale(kk, kk)
        fill_rrect(ctx, -60, -40, 120, 80, 22, C['yellow'])
        poly(ctx, [(-20, 36), (10, 36), (-28, 64)], C['yellow'])
        for i in range(3):
            circle(ctx, -28 + i * 28, 0, 8, C['ink'])
        ctx.restore()
    shelly_main(ctx, T, 'wave', 'open')


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
