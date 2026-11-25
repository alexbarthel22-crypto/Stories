"""Nachbearbeitung: Upscale, Bloom, Partikel, Grading, Untertitel, Badge, HUD -> 1080x1920 PNGs."""
import json, math, os, sys, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = '/home/user/Stories/sunken_pearl_raetsel'
FR = f'{ROOT}/frames'
OUT = f'{ROOT}/frames/post'
FPS = 24
W, H = 1080, 1920
CUTS = [0.0, 5.05, 8.45, 10.35, 13.25, 16.35, 20.6, 22.45, 26.8, 31.35, 34.7, 38.1, 44.0, 49.6, 52.4]
NAMES = ['hook', 'deep', 'small', 'morning', 'station', 'rainlift', 'raintrain', 'sunlift', 'stairs', 'why', 'count',
         'reach', 'umbrella', 'end']
UNDER = {'deep'}
HALL = set()
RAINOUT = {'raintrain', 'end'}
RAINSET = {'rainlift', 'raintrain', 'umbrella', 'end'}
SUNSET = {'station', 'sunlift', 'stairs'}
END = 52.4
FONT = f'{ROOT}/src/fonts/anton.woff'
YEL = (255, 204, 40)
RED = (255, 120, 170)


def font(sz):
    return ImageFont.truetype(FONT, sz)


# ------------------------------------------------------------ Untertitel aus Alignment
def words():
    a = json.load(open(f'{ROOT}/audio/vo_otto.json'))
    ch, st, en = a['characters'], a['character_start_times_seconds'], a['character_end_times_seconds']
    out, w, t0, t1 = [], '', 0, 0
    for c, s, e in zip(ch, st, en):
        if c == ' ':
            if w: out.append([w, t0 + 0.05, t1 + 0.05])
            w = ''; continue
        if not w: t0 = s
        w += c; t1 = e
    if w: out.append([w, t0 + 0.05, t1 + 0.05])
    return [x for x in out if x[0] != '…']


NUM = {'zweihundert': '200', 'hundert': '100', 'drei': '3', 'zwei': '2', 'eins': '1'}
KEY = {'rätsel', 'sunken', 'pearl', 'unten', '−200', 'zug', 'arbeit', 'bahnhof', 'oben', 'meer', 'regnet', 'aufzug',
       'sonne', 'scheint', '−100', 'laufen', '100', 'fuß', 'kommentare', 'lösung', 'knopf', 'obersten', 'hand',
       'regenschirm', 'gewusst', '3', '2', '1', 'zug.'}
REDW = {'klein', 'warum', 'regenschirm', 'obersten'}


def tokens():
    ws = words()
    out = []
    i = 0
    while i < len(ws):
        w, a, b = ws[i]
        core = re.sub(r'[^\wäöüß]', '', w.lower())
        punct = re.sub(r'^[\wäöüßÄÖÜ]+', '', w)
        if core == 'minus' and i + 1 < len(ws):
            n2 = re.sub(r'[^\wäöüß]', '', ws[i + 1][0].lower())
            p2 = re.sub(r'^[\wäöüßÄÖÜ]+', '', ws[i + 1][0])
            out.append(['−' + NUM.get(n2, n2), a, ws[i + 1][2], p2]); i += 2; continue
        if core == 'drei' and i + 2 < len(ws) and ws[i + 1][0].lower() == 'uhr':
            p3 = re.sub(r'^[\wäöüßÄÖÜ]+', '', ws[i + 2][0])
            out.append(['3:12', a, ws[i + 2][2], p3.replace(',', '')]); i += 3; continue
        if core in NUM:
            out.append([NUM[core], a, b, punct]); i += 1; continue
        out.append([w.rstrip('.,:?!'), a, b, punct]); i += 1
    return out


def groups():
    tk = tokens()
    gs, cur = [], []
    for t in tk:
        cur.append(t)
        n = sum(len(x[0]) for x in cur)
        if t[3] in ('.', ',', ':', '?', '!', '?', '…') or len(cur) >= 3 or n > 14:
            gs.append(cur); cur = []
    if cur: gs.append(cur)
    res = []
    for k, g in enumerate(gs):
        start = g[0][1]
        end = gs[k + 1][0][1] if k + 1 < len(gs) else g[-1][2] + 1.0
        end = min(end, g[-1][2] + 0.9)
        res.append((start, end, g))
    return res


GROUPS = groups()


def draw_outlined(dr, xy, txt, f, fill, stroke=10):
    x, y = xy
    dr.text((x + 5, y + 7), txt, font=f, fill=(0, 0, 0, 150), stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
    dr.text((x, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))


def captions(img, t):
    g = None
    for s, e, words_ in GROUPS:
        if s - 0.02 <= t < e:
            g = words_; break
    if not g: return
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    base = 92
    f = font(base)
    txts = [w[0].upper() for w in g]
    widths = [dr.textlength(x, font=f) for x in txts]
    gap = 26
    total = sum(widths) + gap * (len(txts) - 1)
    if total > W - 120:
        sc = (W - 120) / total
        f = font(int(base * sc)); widths = [dr.textlength(x, font=f) for x in txts]; gap = int(gap * sc)
        total = sum(widths) + gap * (len(txts) - 1)
    x = (W - total) / 2
    y = int(H * 0.64)
    for (w, a, b, p), txt, wd in zip(g, txts, widths):
        if t < a - 0.03:
            x += wd + gap; continue
        k = min(1.0, (t - a + 0.03) / 0.12)
        sc = 1.0 + 0.25 * (1 - k) ** 2
        low = w.lower().replace('?', '')
        col = RED if low in REDW else (YEL if low in KEY else (255, 255, 255))
        if sc > 1.01:
            f2 = font(int(f.size * sc))
            w2 = dr.textlength(txt, font=f2)
            draw_outlined(dr, (x - (w2 - wd) / 2, y - (f2.size - f.size) * 0.6), txt, f2, col)
        else:
            draw_outlined(dr, (x, y), txt, f, col)
        x += wd + gap
    img.alpha_composite(layer)


def floor_at(t):
    def ramp(t, t0, t1, a, b):
        k = min(1, max(0, (t - t0) / (t1 - t0))); k = k * k * (3 - 2 * k)
        return round(a + (b - a) * k)
    if t < 5.05: return 0
    if t < 8.45: return ramp(t, 5.3, 8.2, 0, -200)
    if t < 13.25: return -200
    if t < 16.35: return 0
    if t < 20.6: return ramp(t, 16.6, 20.3, -200, 0)
    if t < 22.45: return 0
    if t < 26.8: return ramp(t, 22.6, 25.9, -200, -100)
    if t < 29.4: return -100
    return -99


def badge(img, t):
    if t > 31.35: return
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    fl = floor_at(t)
    secret = False
    f = font(50)
    a = 'SUNKEN PEARL · '
    b = f'ETAGE {"−" if fl < 0 else ""}{abs(fl)}'
    wa, wb = dr.textlength(a, font=f), dr.textlength(b, font=f)
    x0, y0 = 70, 150
    app = min(1, t / 0.35)
    pad = 22
    box = (x0, y0, x0 + wa + wb + 2 * pad, y0 + 82)
    col = RED if secret else YEL
    glow = 0.5 + 0.5 * math.sin(t * 5) if secret else 1.0
    dr.rounded_rectangle(box, 10, fill=(14, 10, 20, int(200 * app)), outline=col + (int(255 * app),), width=5)
    dr.text((x0 + pad, y0 + 9), a, font=f, fill=(255, 255, 255, int(255 * app)))
    c2 = tuple(int(c * (0.75 + 0.25 * glow) + 255 * 0.25 * (1 - glow)) for c in col)
    dr.text((x0 + pad + wa, y0 + 9), b, font=f, fill=c2 + (int(255 * app),))
    img.alpha_composite(layer)


def centered(dr, txt, f, y, col, stroke=12):
    w = dr.textlength(txt, font=f)
    draw_outlined(dr, ((W - w) / 2, y), txt, f, col, stroke)


def overlays(img, t):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    # Titel: RÄTSEL
    if t < 2.4:
        k = min(1, t / 0.25)
        out = min(1, max(0, (2.4 - t) / 0.25))
        a = int(255 * min(k, out))
        f = font(int(200 + 50 * (1 - k) ** 2))
        centered(dr, 'RÄTSEL', f, 330, YEL + (a,), 14)
    # Warum? -> großes Fragezeichen
    if 31.35 <= t < 34.7:
        k = min(1, (t - 31.35) / 0.2)
        sc = 1 + 0.06 * math.sin((t - 31.35) * 7)
        f = font(int(420 * sc * (0.6 + 0.4 * k)))
        centered(dr, '?', f, 180, RED + (int(255 * k),), 16)
    # Countdown
    for tn, n in ((36.0, '3'), (36.52, '2'), (37.11, '1')):
        nxt = {'3': 36.52, '2': 37.11, '1': 38.1}[n]
        if tn <= t < nxt:
            k = min(1, (t - tn) / 0.12)
            f = font(int(520 + 200 * (1 - k) ** 2))
            centered(dr, n, f, 260, YEL + (255,), 18)
    if 34.7 <= t < 36.0:
        centered(dr, 'DEINE ANTWORT?', font(110), 330, (255, 255, 255, 255), 12)
        centered(dr, '↓ KOMMENTARE ↓' if False else 'IN DIE KOMMENTARE', font(80), 470, YEL + (255,), 10)
    # Lösung
    if 38.1 <= t < 44.0:
        k = min(1, (t - 38.1) / 0.25)
        f = font(int(150 + 40 * (1 - k) ** 2))
        centered(dr, 'LÖSUNG', f, 270, (90, 230, 140, int(255 * k)), 14)
    # Ende
    if t >= 50.9:
        k = min(1, (t - 50.9) / 0.3)
        centered(dr, 'FOLGE FÜR', font(int(100 + 20 * (1 - k))), 260, (255, 255, 255, int(255 * k)), 12)
        centered(dr, 'MEHR RÄTSEL!', font(int(130 + 24 * (1 - k))), 380, YEL + (int(255 * k),), 12)
    img.alpha_composite(layer)


def weather_chip(img, t, name):
    if t > 31.35: 
        if name not in ('umbrella', 'end'): return
    if name not in RAINSET and name not in SUNSET: return
    rain = name in RAINSET
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    f = font(50)
    txt = 'REGEN' if rain else 'SONNE'
    x0, y0 = 70, 250 if t < 31.35 else 150
    w = dr.textlength(txt, font=f)
    col = (120, 190, 255) if rain else (255, 200, 60)
    dr.rounded_rectangle((x0, y0, x0 + w + 130, y0 + 82), 10, fill=(14, 10, 20, 200), outline=col + (255,), width=5)
    cx, cy = x0 + 50, y0 + 41
    if rain:
        dr.ellipse((cx - 26, cy - 22, cx + 4, cy + 4), fill=(225, 230, 240, 255))
        dr.ellipse((cx - 8, cy - 28, cx + 26, cy + 4), fill=(225, 230, 240, 255))
        dr.rectangle((cx - 16, cy - 6, cx + 18, cy + 4), fill=(225, 230, 240, 255))
        for dx in (-14, 0, 14):
            dr.line((cx + dx, cy + 12, cx + dx - 5, cy + 26), fill=col + (255,), width=5)
    else:
        dr.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=col + (255,))
        for k in range(8):
            a = k * math.pi / 4
            dr.line((cx + 20 * math.cos(a), cy + 20 * math.sin(a), cx + 29 * math.cos(a), cy + 29 * math.sin(a)), fill=col + (255,), width=5)
    dr.text((x0 + 100, y0 + 9), txt, font=f, fill=col + (255,))
    img.alpha_composite(layer)


def rain(arr, t, g):
    rg = np.random.default_rng(7)
    n = 260
    xs = rg.uniform(-200, W + 200, n); ys = rg.uniform(0, H, n); z = rg.uniform(0.3, 1.0, n)
    layer = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(layer)
    for i in range(n):
        sp = 2600 * z[i]
        y = (ys[i] + sp * t) % (H + 200) - 100
        x = xs[i] - 0.18 * (y - ys[i])
        L = 40 + 70 * z[i]
        dr.line((x, y, x - 0.18 * L, y + L), fill=int(60 + 120 * z[i]), width=max(1, int(3 * z[i])))
    layer = layer.filter(ImageFilter.GaussianBlur(1.0))
    m = np.asarray(layer, np.float32)[..., None] / 255.0
    return arr * 0.82 * np.array([0.92, 0.97, 1.05], np.float32) + m * np.array([0.75, 0.82, 0.9], np.float32) * 0.6


# ------------------------------------------------------------ Bildeffekte
def particles(arr, name, t, tl, col=(0.75, 0.9, 1.0), rise=1.0):
    """Meeresschnee: weiche Punkte mit Parallaxe."""
    rg = np.random.default_rng(abs(hash(name)) % 2 ** 32)
    n = 140
    xs = rg.uniform(0, W, n); ys = rg.uniform(0, H, n); z = rg.uniform(0.2, 1.0, n)
    vx = rg.uniform(-6, 6, n); vy = rg.uniform(-18, -4, n) * rise
    ph = rg.uniform(0, 6.28, n)
    layer = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(layer)
    for i in range(n):
        x = (xs[i] + vx[i] * tl * z[i] + 8 * math.sin(tl * 0.8 + ph[i])) % W
        y = (ys[i] + vy[i] * tl * z[i] * 3) % H
        r = 1.2 + 3.8 * z[i] ** 2
        a = int(40 + 110 * z[i])
        dr.ellipse((x - r, y - r, x + r, y + r), fill=a)
    layer = layer.filter(ImageFilter.GaussianBlur(1.6))
    m = np.asarray(layer, np.float32)[..., None] / 255.0
    col = np.array(col, np.float32)
    return arr + m * col * 0.55


def grade(arr, name, t):
    # Bloom
    small = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    s = np.asarray(small, np.float32) / 255
    lum = s.mean(2, keepdims=True)
    hi = np.clip((lum - 0.62) / 0.38, 0, 1) * s
    b1 = Image.fromarray((hi * 255).astype(np.uint8))
    bl = np.asarray(b1.filter(ImageFilter.GaussianBlur(10)), np.float32) / 255 * 0.9 + \
         np.asarray(b1.filter(ImageFilter.GaussianBlur(30)), np.float32) / 255 * 0.7
    bl = np.asarray(Image.fromarray(np.clip(bl * 255, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    arr = arr + bl * 0.55
    # Grading: Schatten kühl, Lichter warm, leichtes S
    l = arr.mean(2, keepdims=True)
    arr = arr + (0.025 * (1 - l) ** 3) * np.array([-0.4, 0.15, 0.5], np.float32) + 0.02 * l ** 2 * np.array([0.5, 0.2, -0.3], np.float32)
    arr = np.clip(arr, 0, 1)
    arr = arr * arr * (3 - 2 * arr) * 0.35 + arr * 0.65
    # Vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    return arr


_vig = None


def vignette():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 * 0.8 + ((yy - H / 2) / (H / 2)) ** 2)
        _vig = (1 - 0.42 * np.clip(d - 0.45, 0, 1) ** 1.6)[..., None].astype(np.float32)
    return _vig


def process(g):
    t = g / FPS
    si = max(i for i, c in enumerate(CUTS[:-1]) if round(c * FPS) <= g)
    si = min(si, len(NAMES) - 1)
    name = NAMES[si]
    tl = t - CUTS[si]
    src = f'{FR}/{name}/f{g:04d}.png'
    if not os.path.exists(src):
        return False
    im = Image.open(src).convert('RGB').resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(2, 60, 2))
    arr = np.asarray(im, np.float32) / 255
    if name in UNDER:
        arr = particles(arr, name, t, tl)
    if name in RAINOUT:
        arr = rain(arr, t, g)
    elif name in HALL:
        arr = particles(arr, name, t, tl, (1.0, 0.85, 0.6), -0.3)
    arr = grade(arr, name, t)
    arr = arr * vignette()
    # Korn
    rng = np.random.default_rng(g)
    arr = arr + rng.normal(0, 0.012, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1).astype(np.float32)
    # Ein-/Ausblenden + Blitz beim Riss / Auge
    fade = min(1, t / 0.4) * min(1, max(0, (END - t) / 0.6))
    arr = arr * fade
    for tf, amt in ((38.1, 0.4), (47.95, 0.3), (43.25, 0.15)):
        if tf <= t < tf + 0.25:
            arr = arr + amt * (1 - (t - tf) / 0.25)
    img = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8)).convert('RGBA')
    badge(img, t)
    captions(img, t)
    weather_chip(img, t, name)
    overlays(img, t)
    img.convert('RGB').save(f'{OUT}/p{g:04d}.png', compress_level=1)
    return True


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    a, b = int(sys.argv[1]), int(sys.argv[2])
    for g in range(a, b):
        if os.path.exists(f'{OUT}/p{g:04d}.png') and '--force' not in sys.argv:
            continue
        if not process(g):
            print('MISSING', g)
