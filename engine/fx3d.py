"""Shared 'channel look' overlays: extruded 3D text pills, karaoke title, burst, blend-correct canvas."""
import math
import numpy as np
from PIL import Image, ImageDraw
from toolkit import Canvas, font, hexc, log_ui, OUT_W, ease_out_back, prog, _shade


class BCanvas(Canvas):
    """Canvas that alpha-blends semi-transparent shapes on RGBA images (PIL would replace the pixels)"""

    def _blend(self, name, pts, pad, *a, **kw):
        col = kw.get("fill") if kw.get("fill") is not None else kw.get("outline")
        if col is None and len(a) and isinstance(a[-1], tuple):
            col = a[-1]
        if self.img.mode != "RGBA" or col is None or len(col) < 4 or col[3] >= 255:
            return getattr(Canvas, name)(self, *a, **kw)
        q = [self.p(*p) for p in pts]
        pd = pad * self.s + 3
        x0 = max(0, int(min(p[0] for p in q) - pd)); y0 = max(0, int(min(p[1] for p in q) - pd))
        x1 = min(self.img.width, int(max(p[0] for p in q) + pd) + 1)
        y1 = min(self.img.height, int(max(p[1] for p in q) + pd) + 1)
        if x1 <= x0 or y1 <= y0:
            return
        ov = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        getattr(Canvas, name)(Canvas(ov, self.ox + x0 / self.s, self.oy + y0 / self.s, self.s), *a, **kw)
        self.img.alpha_composite(ov, (x0, y0))

    def rect(self, x0, y0, x1, y1, **kw):
        self._blend("rect", [(x0, y0), (x1, y1)], kw.get("width", 1), x0, y0, x1, y1, **kw)

    def circle(self, x, y, r, **kw):
        self._blend("circle", [(x - r, y - r), (x + r, y + r)], kw.get("width", 1), x, y, r, **kw)

    def ellipse(self, x0, y0, x1, y1, **kw):
        self._blend("ellipse", [(x0, y0), (x1, y1)], kw.get("width", 1), x0, y0, x1, y1, **kw)

    def line(self, pts, fill, width=1, joint="curve", cap=True):
        self._blend("line", pts, width, pts, fill, width, joint, cap)

    def poly(self, pts, **kw):
        self._blend("poly", pts, kw.get("width", 1), pts, **kw)

    def pieslice(self, x0, y0, x1, y1, a0, a1, fill):
        self._blend("pieslice", [(x0, y0), (x1, y1)], 1, x0, y0, x1, y1, a0, a1, fill)

    def arc(self, x0, y0, x1, y1, a0, a1, fill, width=1):
        self._blend("arc", [(x0, y0), (x1, y1)], width, x0, y0, x1, y1, a0, a1, fill, width)


def pill_tile(words, base, bg, fg, pops=None, depth=12, Z=2, hl_col=None, pop_k=0.28):
    """extruded pill with words (spoken word: capsule highlight + colour); returns (tile at Z x, pill box at 1x)"""
    pops = pops or [0.0] * len(words)
    gap = 0.28 * base
    sizes = [base * (1 + pop_k * pp) for pp in pops]
    widths = [font(int(sz)).getbbox(w)[2] for sz, w in zip(sizes, words)]
    tw = sum(widths) + gap * (len(words) - 1)
    padx, pady = 0.42 * base, 0.24 * base
    x0, y0 = 30, 30
    grow = base * pop_k * max(pops) if pops else 0.0
    x1, y1 = x0 + tw + 2 * padx, y0 + base + grow + 2 * pady
    PW, PH = int(x1 + 40), int(y1 + depth + 50)
    tile = Image.new("RGBA", (PW * Z, PH * Z), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile, "RGBA")
    rad = int((y1 - y0) / 2.6 * Z)
    d.rounded_rectangle([(x0 + 10) * Z, (y0 + depth + 14) * Z, (x1 + 10) * Z, (y1 + depth + 14) * Z], radius=rad,
                        fill=(20, 12, 40, 90))
    side = _shade(hexc(bg), 0.42)
    for k in range(depth, 0, -1):
        d.rounded_rectangle([x0 * Z, (y0 + k) * Z, x1 * Z, (y1 + k) * Z], radius=rad, fill=side)
    d.rounded_rectangle([x0 * Z, y0 * Z, x1 * Z, y1 * Z], radius=rad, fill=hexc(bg), outline=hexc("#1d1b33"),
                        width=4 * Z)
    x = x0 + padx
    cy = (y0 + (y1 - y0) / 2) * Z
    for j, w in enumerate(words):
        cxw = (x + widths[j] / 2) * Z
        pp = pops[j]
        if pp > 0.05 and len(words) > 1:
            hl = hl_col or ((255, 255, 255) if bg == "#ffd34d" else (255, 211, 77))
            hh = ((y1 - y0) / 2 - 7) * Z
            hw = widths[j] / 2 * Z + hh * 0.55
            lx, rx = max(cxw - hw, (x0 + 7) * Z), min(cxw + hw, (x1 - 7) * Z)
            col = tuple(int(c0 + (c1 - c0) * min(1, pp * 1.6)) for c0, c1 in zip(hexc(bg), hl))
            d.rounded_rectangle([lx, cy - hh, rx, cy + hh], radius=int(hh), fill=col)
        col = (hexc("#ffe46b") if bg in ("#e2574c", "#1d1b33") else hexc("#d62828")) if pp > 0.3 else hexc(fg)
        jump = -base * 0.06 * Z * pp
        fnt = font(int(sizes[j] * Z))
        light = sum(col[:3]) > 600
        if light:      # extruded 3D text with a dark outline (no ghosting)
            for k in range(int(base * 0.06) + 1, 0, -1):
                d.text((cxw, cy + jump + k * Z), w, font=fnt, fill=hexc("#1d1b33"), anchor="mm",
                       stroke_width=int(2.5 * Z), stroke_fill=hexc("#1d1b33"))
            d.text((cxw, cy + jump), w, font=fnt, fill=col, anchor="mm", stroke_width=int(2.5 * Z),
                   stroke_fill=hexc("#1d1b33"))
        else:
            d.text((cxw, cy + jump), w, font=fnt, fill=col, anchor="mm",
                   stroke_width=int(2 * Z * pp), stroke_fill=hexc("#1d1b33"))
        x += widths[j] + gap
    return tile, (x0, y0, x1, y1)


def safe_half_width(cx, cy, half_h, overshoot=1.0):
    """largest half width a centred element at (cx, cy) may have to stay out of the TikTok zones"""
    right = 1040 if (cy + half_h < 760 or cy - half_h > 1480) else 930
    return min(cx - 50, right - cx) / overshoot


def _shine(tile, box, Z, p):
    """diagonal light sweep across the pill (p = 0..1), clipped to the pill"""
    if not (0 < p < 1):
        return tile
    x0, y0, x1, y1 = box
    band = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(band, "RGBA")
    w = (x1 - x0)
    cx = x0 - 0.3 * w + 1.6 * w * p
    d.polygon([((cx - 30) * Z, y1 * Z), ((cx + 10) * Z, y0 * Z), ((cx + 60) * Z, y0 * Z), ((cx + 20) * Z, y1 * Z)],
              fill=(255, 255, 255, 120))
    m = Image.new("L", tile.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([x0 * Z, y0 * Z, x1 * Z, y1 * Z], radius=int((y1 - y0) / 2.6 * Z), fill=255)
    band.putalpha(Image.fromarray((np.asarray(band.split()[3], np.uint16) * np.asarray(m, np.uint16) // 255).astype(np.uint8)))
    tile.alpha_composite(band)
    return tile


def pill3d(img, cx, cy, text, size, bg="#fff6e6", fg="#2b2140", rot=0.0, scale=1.0, depth=10, max_w=860,
           alpha=1.0, sx=1.0, sy=1.0, shine=None, overshoot=1.18):
    if scale <= 0.01 or alpha <= 0.01:
        return
    hw = safe_half_width(cx, cy, size * 0.9 * overshoot, overshoot)
    max_w = min(max_w, 2 * hw)
    while font(size).getbbox(text)[2] + 0.84 * size + 8 > max_w and size > 24:
        size -= 2
    tile, (x0, y0, x1, y1) = pill_tile([text], size, bg, fg, depth=depth)
    if shine is not None:
        tile = _shine(tile, (x0, y0, x1, y1), 2, shine)
    if rot:
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
    kx, ky = scale * sx / 2, scale * sy / 2
    tile = tile.resize((max(1, int(tile.width * kx)), max(1, int(tile.height * ky))), Image.LANCZOS)
    if alpha < 1:
        tile.putalpha(tile.split()[3].point(lambda v: int(v * alpha)))
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)
    if scale > 0.6 and alpha > 0.5:
        pw, ph = (x1 - x0) * scale * sx, (y1 - y0 + depth) * scale * sy
        log_ui("pill:" + text, cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2)


def elastic(p):
    if p <= 0:
        return 0.0
    if p >= 1:
        return 1.0
    return 1 + 2 ** (-10 * p) * math.sin((p * 10 - 0.75) * (2 * math.pi) / 3)


def pop_pill(img, t, t0, cx, cy, text, size, t1=None, burst_col=None, **kw):
    """modern pop-in: elastic scale, squash & stretch, light sweep, sparkle burst, gentle idle bob (+ pop-out at t1)"""
    if t < t0 or (t1 is not None and t > t1 + 0.2):
        return
    p = prog(t, t0, t0 + 0.55)
    sc = elastic(p)
    st_ = math.sin(math.pi * min(1.0, p * 1.6)) * (1 - p)
    sx, sy = 1 + 0.18 * st_, 1 - 0.15 * st_
    if t1 is not None:
        sc *= 1 - prog(t, t1, t1 + 0.2)
    cy2 = cy                                   # no idle wobble: boxes stand still after popping in
    rot = kw.pop("rot", 0.0)
    if p < 0.6:
        sparkle(img, cx, cy2, p / 0.6, size, burst_col)
    kw.setdefault("overshoot", 1.58)
    pill3d(img, cx, cy2, text, size, scale=sc, sx=sx, sy=sy, rot=rot, shine=prog(t, t0 + 0.12, t0 + 0.75), **kw)


def sparkle(img, cx, cy, p, size, col=None):
    """little star / dot burst around a popping element"""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    cols = [col or (255, 211, 77), (255, 255, 255), (255, 111, 174), (63, 167, 245)]
    a = int(255 * (1 - p))
    for i in range(12):
        ang = i / 12 * 2 * math.pi + 0.3
        r0 = size * 1.6 + size * 3.2 * p
        x, y = cx + math.cos(ang) * r0 * 1.5, cy + math.sin(ang) * r0 * 0.55
        rr = size * 0.09 * (1 - p * 0.6)
        c = cols[i % 4] + (a,)
        if i % 2:
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c)
        else:
            d.line([(x - rr * 1.8, y), (x + rr * 1.8, y)], fill=c, width=max(2, int(rr * 0.6)))
            d.line([(x, y - rr * 1.8), (x, y + rr * 1.8)], fill=c, width=max(2, int(rr * 0.6)))
    img.paste(lay, (0, 0), lay)


def burst(img, cx, cy, a, t, r0=170, r1=430, col=(255, 222, 90), n=18):
    if a <= 0.02:
        return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    for i in range(n):
        ang = i / n * 2 * math.pi + t * 0.8
        da = 0.06
        rr = r1 * (0.75 + 0.25 * ((i * 7) % 3) / 2)
        d.polygon([(cx + math.cos(ang - da) * r0, cy + math.sin(ang - da) * r0 * 0.6),
                   (cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * 0.6),
                   (cx + math.cos(ang + da) * r0, cy + math.sin(ang + da) * r0 * 0.6)], fill=col + (int(200 * a),))
    img.paste(lay, (0, 0), lay)


def karaoke(frame, t, lines, t0, t1, ys, first_pop=True, max_w=900, pop_k=0.28, stagger=0.0, times=None):
    """lines: [(words, bg, fg, rot, base)]; whole sentence visible; spoken word grows, jumps and lights up.
    stagger>0: lines pop in one after another at the very start (still all visible within `stagger*len` s)"""
    words = [w for line, *_ in lines for w in line]
    weights = [len(w) + 2 for w in words]
    tot = sum(weights)
    spans, acc = [], t0 + 0.02
    for wgt in weights:
        dd = (t1 - t0 - 0.06) * wgt / tot
        spans.append((acc, acc + dd))
        acc += dd
    if times:                       # explicit (start, end) per displayed word
        spans = list(times)
    fade = 1 - prog(t, t1 + 0.15, t1 + 0.5)
    if fade <= 0.01:
        return
    i = 0
    for li, (line, bg, fg, rot, base) in enumerate(lines):
        pops = []
        for j in range(len(line)):
            a_, b_ = spans[i + j]
            p = prog(t, a_ - 0.03, b_ + 0.08)
            pops.append(math.sin(math.pi * p) if 0 < p < 1 else 0.0)
        hw = safe_half_width(OUT_W / 2, ys[li], base * 0.9 * (1 + pop_k), 1.0)
        lim = min(max_w, 2 * hw)
        b = base
        while True:
            tile, box = pill_tile(line, b, bg, fg, pops, pop_k=pop_k)
            if box[2] - box[0] <= lim or b < 40:
                break
            b -= 3
        single = len(line) == 1
        sc = (1 + 0.12 * pops[0]) if single else 1.0
        tl = t0 + li * stagger
        p_in = prog(t, tl - (0.0 if stagger else 0.36), tl + 0.36) if (first_pop and li == 0) or stagger else 1.0
        sx = sy = 1.0
        if p_in < 1:
            sc *= max(0.05, elastic(p_in)) if stagger else 0.2 + 0.8 * ease_out_back(p_in)
            st_ = math.sin(math.pi * min(1.0, p_in * 1.6)) * (1 - p_in)
            sx, sy = 1 + 0.2 * st_, 1 - 0.16 * st_
        cap = lim / max(1.0, box[2] - box[0])
        if sc * sx > cap:
            sc *= cap / (sc * sx)
        if single:
            burst(frame, OUT_W / 2, ys[li], max(pops[0], 1 - prog(t, t0, t0 + 0.7)) * fade, t)
        tile = _shine(tile, box, 2, prog(t, tl + 0.1, tl + 0.7))
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
        tile = tile.resize((max(1, int(tile.width * sc * sx / 2)), max(1, int(tile.height * sc * sy / 2))), Image.LANCZOS)
        if fade < 1:
            tile.putalpha(tile.split()[3].point(lambda v: int(v * fade)))
        sh = 0
        yb = ys[li]
        px, py = int(OUT_W / 2 - tile.width / 2 + sh), int(yb - tile.height / 2)
        frame.paste(tile, (px, py), tile)
        if stagger and p_in < 0.6:
            sparkle(frame, OUT_W / 2, yb, p_in / 0.6, base * 0.8)
        bw, bh = (box[2] - box[0]) * sc * sx, (box[3] - box[1] + 12) * sc * sy
        if fade > 0.5 and sc > 0.6:
            log_ui("karaoke " + str(li), OUT_W / 2 - bw / 2 + sh, yb - bh / 2, OUT_W / 2 + bw / 2 + sh, yb + bh / 2)
        i += len(line)
