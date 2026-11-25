"""Nachbearbeitung: Upscale, Bloom, Partikel, Grading, Untertitel, Badge, HUD -> 1080x1920 PNGs."""
import json, math, os, sys, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = '/home/user/Stories/sunken_pearl'
FR = f'{ROOT}/frames'
OUT = f'{ROOT}/frames/post'
FPS = 24
W, H = 1080, 1920
CUTS = [0.0, 2.55, 8.0, 11.4, 15.2, 18.4, 20.3, 21.65, 23.0, 24.2, 26.9, 28.65, 30.45, 32.25, 34.6, 36.55, 39.1,
        42.85, 45.5, 48.15, 49.85, 53.9, 56.6, 60.8, 63.5, 65.4, 70.6]
NAMES = ['surf', 'under', 'descent', 'winext', 'cozy', 'clock', 'startle', 'door', 'windark', 'peer', 'nixie', 'flicker',
         'gauge', 'crack', 'run', 'capsule', 'liftup', 'display', 'face', 'doors', 'reveal', 'pearl', 'faceglow', 'reach',
         'eye', 'final']
UNDER = {'under', 'descent', 'winext', 'capsule', 'reveal', 'pearl', 'faceglow', 'reach', 'eye', 'final'}
FONT = f'{ROOT}/src/fonts/anton.woff'
YEL = (255, 204, 40)
RED = (255, 70, 55)


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


NUM = {'hundertsiebenundvierzig': '147', 'zweihunderteins': '201', 'zweihundert': '200', 'viertausend': '4.000',
       'drei': '3', 'zwölf': '12'}
KEY = {'sunken', 'pearl', 'wolkenkratzer', 'unten', '200', 'meer', '−147', 'still', '3:12', 'klopft', 'fenster',
       'nichts', '4.000', 'licht', 'druckmesser', 'riss', 'aufzug', 'runter', 'darf', '−201', 'perle', 'haus',
       'leuchtet', 'atmet', 'innen', 'öffnen', 'kommentare', 'tür', 'glas', 'wasser', 'nur'}
REDW = {'−201', 'riss', 'innen', 'darf', 'klopft'}


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
    if t < 2.6: return 0
    if t < 11.4:
        k = (t - 2.6) / 8.8
        k = k * k * (3 - 2 * k)
        return -round(147 * k)
    if t < 36.6: return -147
    if t < 44.3:
        k = (t - 36.6) / 7.7
        return -147 - round(53 * min(1, k ** 0.8))
    return -201


def badge(img, t):
    if t > 65.3: return
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    fl = floor_at(t)
    red = fl == -201
    blink = red and int(t * 4) % 2 == 0
    f = font(50)
    a = 'SUNKEN PEARL · '
    b = f'ETAGE {"−" if fl < 0 else ""}{abs(fl)}'
    wa, wb = dr.textlength(a, font=f), dr.textlength(b, font=f)
    x0, y0 = 70, 150
    app = min(1, t / 0.35)
    pad = 22
    box = (x0, y0, x0 + wa + wb + 2 * pad, y0 + 82)
    col = RED if red else YEL
    dr.rounded_rectangle(box, 10, fill=(10, 14, 20, int(200 * app)), outline=col + (int(255 * app),), width=5)
    dr.text((x0 + pad, y0 + 9), a, font=f, fill=(255, 255, 255, int(255 * app)))
    dr.text((x0 + pad + wa, y0 + 9), b, font=f, fill=(col if not blink else (255, 255, 255)) + (int(255 * app),))
    img.alpha_composite(layer)


def cta(img, t):
    t0 = 65.5
    if t < t0: return
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    k = min(1, (t - t0) / 0.3)
    f = font(int(150 + 30 * (1 - k)))
    txt = 'ÖFFNEN?'
    w = dr.textlength(txt, font=f)
    draw_outlined(dr, ((W - w) / 2, 250), txt, f, YEL + (int(255 * k),), 12)
    if t > 66.4:
        k2 = min(1, (t - 66.4) / 0.25)
        fb = font(80)
        for i, (lab, col) in enumerate((('JA', (46, 204, 113)), ('NEIN', (231, 76, 60)))):
            cx = W / 2 + (i * 2 - 1) * 210
            bw = 330
            yy = 470 + 30 * (1 - k2)
            dr.rounded_rectangle((cx - bw / 2, yy, cx + bw / 2, yy + 130), 65, fill=col + (int(235 * k2),), outline=(255, 255, 255, int(255 * k2)), width=6)
            lw = dr.textlength(lab, font=fb)
            dr.text((cx - lw / 2, yy + 14), lab, font=fb, fill=(255, 255, 255, int(255 * k2)), stroke_width=4, stroke_fill=(0, 0, 0, int(200 * k2)))
    if t > 68.6:
        k3 = min(1, (t - 68.6) / 0.3)
        f3 = font(70)
        s = 'TEIL 2 FOLGT …'
        w3 = dr.textlength(s, font=f3)
        draw_outlined(dr, ((W - w3) / 2, 1580), s, f3, (255, 255, 255, int(255 * k3)), 8)
    img.alpha_composite(layer)


# ------------------------------------------------------------ Bildeffekte
def particles(arr, name, t, tl):
    """Meeresschnee: weiche Punkte mit Parallaxe."""
    rg = np.random.default_rng(abs(hash(name)) % 2 ** 32)
    n = 140
    xs = rg.uniform(0, W, n); ys = rg.uniform(0, H, n); z = rg.uniform(0.2, 1.0, n)
    vx = rg.uniform(-6, 6, n); vy = rg.uniform(-18, -4, n)
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
    col = np.array([0.75, 0.9, 1.0], np.float32)
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
    si = max(i for i, c in enumerate(CUTS[:-1]) if c <= t + 1e-6)
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
    arr = grade(arr, name, t)
    arr = arr * vignette()
    # Korn
    rng = np.random.default_rng(g)
    arr = arr + rng.normal(0, 0.012, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1).astype(np.float32)
    # Ein-/Ausblenden + Blitz beim Riss / Auge
    fade = min(1, t / 0.4) * min(1, max(0, (70.6 - t) / 0.6))
    arr = arr * fade
    for tf, amt in ((32.3, 0.5), (63.55, 0.35), (44.33, 0.25)):
        if tf <= t < tf + 0.25:
            arr = arr + amt * (1 - (t - tf) / 0.25)
    img = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8)).convert('RGBA')
    badge(img, t)
    captions(img, t)
    cta(img, t)
    img.convert('RGB').save(f'{OUT}/p{g:04d}.png', compress_level=1)
    return True


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    a, b = int(sys.argv[1]), int(sys.argv[2])
    for g in range(a, b):
        if os.path.exists(f'{OUT}/p{g:04d}.png') and '--force' not in sys.argv:
            continue
        process(g)
