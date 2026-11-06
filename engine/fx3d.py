"""Shared 'channel look' overlays: extruded 3D text pills, karaoke title, burst, blend-correct canvas."""
import math
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
    x1, y1 = x0 + tw + 2 * padx, y0 + base + 2 * pady
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
        jump = -base * 0.08 * Z * pp
        d.text((cxw + 3 * Z, cy + 4 * Z + jump), w, font=font(int(sizes[j] * Z)), fill=(0, 0, 0, 60), anchor="mm")
        d.text((cxw, cy + jump), w, font=font(int(sizes[j] * Z)), fill=col, anchor="mm",
               stroke_width=int(2 * Z * pp), stroke_fill=hexc("#1d1b33"))
        x += widths[j] + gap
    return tile, (x0, y0, x1, y1)


def pill3d(img, cx, cy, text, size, bg="#fff6e6", fg="#2b2140", rot=0.0, scale=1.0, depth=10, max_w=860,
           alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    while font(size).getbbox(text)[2] + 0.84 * size > max_w and size > 24:
        size -= 2
    tile, (x0, y0, x1, y1) = pill_tile([text], size, bg, fg, depth=depth)
    if rot:
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
    k = scale / 2
    tile = tile.resize((max(1, int(tile.width * k)), max(1, int(tile.height * k))), Image.LANCZOS)
    if alpha < 1:
        tile.putalpha(tile.split()[3].point(lambda v: int(v * alpha)))
    img.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)
    if scale > 0.6 and alpha > 0.5:
        pw, ph = (x1 - x0) * scale, (y1 - y0 + depth) * scale
        log_ui("pill:" + text, cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2)


def pop_pill(img, t, t0, cx, cy, text, size, t1=None, **kw):
    """pill that pops in at t0 (and pops out at t1)"""
    if t < t0 or (t1 is not None and t > t1 + 0.2):
        return
    sc = ease_out_back(prog(t, t0, t0 + 0.3))
    if t1 is not None:
        sc *= 1 - prog(t, t1, t1 + 0.2)
    pill3d(img, cx, cy, text, size, scale=sc, **kw)


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


def karaoke(frame, t, lines, t0, t1, ys, first_pop=True, max_w=780, pop_k=0.28):
    """lines: [(words, bg, fg, rot, base)]; whole sentence visible from frame 0; spoken word pops + highlight"""
    words = [w for line, *_ in lines for w in line]
    weights = [len(w) + 2 for w in words]
    tot = sum(weights)
    spans, acc = [], t0 + 0.02
    for wgt in weights:
        dd = (t1 - t0 - 0.06) * wgt / tot
        spans.append((acc, acc + dd))
        acc += dd
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
        b = base
        while True:
            tile, box = pill_tile(line, b, bg, fg, pops, pop_k=pop_k)
            if box[2] - box[0] <= max_w or b < 40:
                break
            b -= 3
        single = len(line) == 1
        sc = (1 + 0.12 * pops[0]) if single else 1.0
        if li == 0 and first_pop:
            sc *= 0.2 + 0.8 * ease_out_back(prog(t, t0, t0 + 0.36))
        if single:
            burst(frame, OUT_W / 2, ys[li], max(pops[0], 1 - prog(t, t0, t0 + 0.7)) * fade, t)
        tile = tile.rotate(rot, resample=Image.BICUBIC, expand=True)
        k = sc / 2
        tile = tile.resize((max(1, int(tile.width * k)), max(1, int(tile.height * k))), Image.LANCZOS)
        if fade < 1:
            tile.putalpha(tile.split()[3].point(lambda v: int(v * fade)))
        sh = 12 * math.sin(t * 75) * pops[0] if single and pops[0] > 0.05 else 0
        px, py = int(OUT_W / 2 - tile.width / 2 + sh), int(ys[li] - tile.height / 2)
        frame.paste(tile, (px, py), tile)
        bw, bh = (box[2] - box[0]) * sc, (box[3] - box[1] + 12) * sc
        if fade > 0.5:
            log_ui("karaoke " + str(li), OUT_W / 2 - bw / 2 + sh, ys[li] - bh / 2, OUT_W / 2 + bw / 2 + sh, ys[li] + bh / 2)
        i += len(line)
