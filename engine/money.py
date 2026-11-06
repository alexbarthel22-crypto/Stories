"""Realistic-looking (but clearly illustrated) euro banknotes and the 1-cent coin as cached sprites."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from toolkit import font

_CACHE = {}
NOTE_COLS = {100: ((96, 168, 112), (176, 214, 168), (40, 104, 60)),     # green
             50: ((226, 140, 64), (246, 200, 150), (150, 80, 30)),      # orange
             200: ((214, 176, 80), (240, 222, 160), (140, 104, 30)),    # yellow-brown
             20: ((70, 110, 190), (170, 196, 236), (30, 60, 130))}      # blue


def _grad(w, h, c0, c1, horizontal=True):
    t = np.linspace(0, 1, w if horizontal else h)
    cols = np.array([np.array(c0) * (1 - x) + np.array(c1) * x for x in t])
    if horizontal:
        a = np.repeat(cols[None, :, :], h, axis=0)
    else:
        a = np.repeat(cols[:, None, :], w, axis=1)
    return Image.fromarray(a.astype(np.uint8), "RGB")


def note_sprite(value=100, W=720):
    key = ("note", value, W)
    if key in _CACHE:
        return _CACHE[key]
    H = int(W * 0.53)
    base, light, dark = NOTE_COLS[value]
    img = _grad(W, H, light, base).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # guilloche lines
    for k in range(0, H, 6):
        d.arc([-W * 0.3, k - H, W * 0.9, k + H * 0.9], 270, 360, fill=dark + (40,), width=1)
    for k in range(18):
        d.ellipse([W * 0.2 + k * 6, H * 0.15 + k * 3, W * 0.62 - k * 6, H * 0.9 - k * 3], outline=dark + (35,), width=1)
    # architectural arch window (motif)
    ax, ay, aw, ah = W * 0.3, H * 0.2, W * 0.26, H * 0.62
    d.rectangle([ax, ay + aw / 2, ax + aw, ay + ah], fill=light + (200,), outline=dark + (200,), width=3)
    d.pieslice([ax, ay, ax + aw, ay + aw], 180, 360, fill=light + (200,), outline=dark + (200,), width=3)
    for k in range(1, 4):
        xx = ax + aw * k / 4
        d.line([(xx, ay + aw / 2), (xx, ay + ah)], fill=dark + (150,), width=2)
    d.line([(ax, ay + ah * 0.62), (ax + aw, ay + ah * 0.62)], fill=dark + (150,), width=2)
    # EU flag with 12 stars
    fx, fy, fw, fh = W * 0.04, H * 0.07, W * 0.14, H * 0.18
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(30, 60, 160, 255))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        sx, sy = fx + fw / 2 + math.cos(a) * fh * 0.33, fy + fh / 2 + math.sin(a) * fh * 0.33
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 214, 0, 255))
    # hologram stripe
    st = _grad(int(W * 0.07), H, (200, 210, 225), (240, 240, 250), horizontal=False).convert("RGBA")
    sd = ImageDraw.Draw(st, "RGBA")
    for k in range(0, H, 22):
        sd.ellipse([4, k, int(W * 0.07) - 4, k + 18], outline=(150, 160, 190, 200), width=2)
    img.paste(st, (int(W * 0.6), 0))
    # value numerals
    d.text((W * 0.04, H * 0.3), str(value), font=font(int(H * 0.16)), fill=dark + (255,))
    d.text((W * 0.975, H * 0.95), str(value), font=font(int(H * (0.3 if value < 100 else 0.24))), fill=dark + (255,), anchor="rb")
    d.text((W * 0.3, H * 0.93), "EURO", font=font(int(H * 0.09)), fill=dark + (230,), anchor="lb")
    d.text((W * 0.97, H * 0.06), "EYPΩ", font=font(int(H * 0.07)), fill=dark + (200,), anchor="rt")
    # small serial number
    d.text((W * 0.04, H * 0.93), "EA4721938", font=font(int(H * 0.05), bold=False), fill=(150, 40, 40, 220), anchor="lb")
    d.rectangle([0, 0, W - 1, H - 1], outline=dark + (180,), width=3)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], radius=10, fill=255)
    img.putalpha(mask)
    _CACHE[key] = img
    return img


def coin_sprite(D=400):
    """1 euro cent, common side: big 1, 'EURO CENT', globe, 12 stars, copper with rim"""
    key = ("coin", D)
    if key in _CACHE:
        return _CACHE[key]
    S = D
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:S, 0:S]
    r = np.hypot(xx - S / 2, yy - S / 2) / (S / 2)
    light = np.clip(0.75 + 0.35 * ((S / 2 - xx) + (S / 2 - yy)) / S, 0.5, 1.2)
    base = np.array([196, 112, 62], float)
    rgb = base[None, None, :] * light[..., None]
    rim = (r > 0.86) & (r <= 1.0)
    rgb[rim] = np.array([168, 92, 48]) * light[rim][:, None] * 1.05
    amask = (r <= 1.0).astype(np.uint8) * 255
    img = Image.fromarray(np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), amask]), "RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    c = S / 2
    d.ellipse([S * 0.07, S * 0.07, S * 0.93, S * 0.93], outline=(120, 60, 30, 200), width=max(2, S // 80))
    emb_d, emb_l = (110, 52, 26, 255), (240, 178, 130, 200)
    # globe (right half)
    gx, gy, gr = c + S * 0.14, c - S * 0.02, S * 0.27
    for k in range(-3, 4):
        d.arc([gx - gr * abs(k) / 3.2, gy - gr, gx + gr * abs(k) / 3.2, gy + gr], 270 if k < 0 else 90, 90 if k < 0 else 270,
              fill=emb_d, width=max(2, S // 120))
    for k in range(-2, 3):
        yk = gy + k * gr * 0.36
        hw = math.sqrt(max(0, gr * gr - (yk - gy) ** 2))
        d.line([(gx - hw, yk), (gx + hw, yk)], fill=emb_d, width=max(2, S // 120))
    # big 1 with highlight (embossed look)
    d.text((c - S * 0.16 - 2, c - S * 0.06 - 2), "1", font=font(int(S * 0.42)), fill=emb_l, anchor="mm")
    d.text((c - S * 0.16, c - S * 0.06), "1", font=font(int(S * 0.42)), fill=emb_d, anchor="mm")
    d.text((c - S * 0.16, c + S * 0.2), "EURO", font=font(int(S * 0.075)), fill=emb_d, anchor="mm")
    d.text((c - S * 0.16, c + S * 0.28), "CENT", font=font(int(S * 0.075)), fill=emb_d, anchor="mm")
    # 12 stars in the outer ring
    for k in range(12):
        a = -math.pi / 2 + k / 12 * 2 * math.pi
        sx, sy = c + math.cos(a) * S * 0.39, c + math.sin(a) * S * 0.39
        pts = []
        for j in range(10):
            rr = S * (0.024 if j % 2 == 0 else 0.01)
            aa = -math.pi / 2 + j * math.pi / 5
            pts.append((sx + math.cos(aa) * rr, sy + math.sin(aa) * rr))
        d.polygon(pts, fill=emb_d)
    # shine
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).arc([S * 0.08, S * 0.08, S * 0.92, S * 0.92], 190, 260, fill=(255, 225, 195, 160), width=max(3, S // 40))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(S / 30)))
    img.putalpha(Image.fromarray(amask))
    _CACHE[key] = img
    return img


def paste_sprite(cv, sprite, x, y, w_world, rot=0.0, squash=1.0):
    """paste sprite centred at world (x, y), width w_world, rotated (radians), horizontally squashed (coin flip)"""
    w = max(2, int(w_world * cv.s))
    h = max(2, int(w * sprite.height / sprite.width))
    sw = max(1, int(w * max(0.06, abs(squash))))
    im = sprite.resize((sw, h), Image.LANCZOS)
    if abs(squash) < 0.999:      # coin edge
        edge = Image.new("RGBA", (sw + max(2, int(w * 0.05 * (1 - abs(squash)))), h), (0, 0, 0, 0))
        ImageDraw.Draw(edge).ellipse([0, 0, edge.width - 1, h - 1], fill=(130, 66, 34, 255))
        edge.alpha_composite(im, (0, 0))
        im = edge
    if rot:
        im = im.rotate(math.degrees(-rot), resample=Image.BICUBIC, expand=True)
    px, py = cv.p(x, y)
    pos = (int(px - im.width / 2), int(py - im.height / 2))
    if cv.img.mode == "RGBA":
        x0, y0 = max(0, pos[0]), max(0, pos[1])
        crop = im.crop((x0 - pos[0], y0 - pos[1], min(im.width, cv.img.width - pos[0]), min(im.height, cv.img.height - pos[1])))
        if crop.width > 0 and crop.height > 0:
            cv.img.alpha_composite(crop, (x0, y0))
    else:
        cv.img.paste(im, pos, im)
