"""Rendern: python render.py preview t1 t2 ...  |  python render.py full [start end]"""
import sys, os, cairo
import numpy as np
from PIL import Image
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mb as scenes
from draw import W, H

FPS = 30
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frames')


_yy, _xx = np.mgrid[0:1920, 0:1080]
VIG = (1 - 0.28 * (((_xx - 540) / 760.0) ** 2 + ((_yy - 960) / 1250.0) ** 2))[:, :, None].clip(0.6, 1)
SUB = 5            # Zwischenbilder pro Frame (Bewegungsunschärfe der Szene)
SHUTTER = 0.5      # Anteil der Framedauer
import draw as _draw


def _one(T, ui=True):
    _draw.UI_ON[0] = ui
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    c.set_antialias(cairo.ANTIALIAS_BEST)
    scenes.frame(c, T)
    s.flush()
    _draw.UI_ON[0] = True
    return np.frombuffer(s.get_data(), np.uint8).reshape(H, s.get_stride() // 4, 4)[:, :W, :3].astype(np.float32)


def render(T, path):
    full = _one(T, ui=True)
    mid = _one(T, ui=False)
    probe = _one(T + SHUTTER / FPS, ui=False)
    if np.abs(probe - mid).mean() < 1.5:
        img = full
    else:
        n = 14
        acc = np.zeros_like(mid)
        for k in range(n):
            dt = (k / (n - 1) - 0.5) * SHUTTER / FPS
            acc += _one(max(0.0, T + dt), ui=False)
        blur = acc / n
        m = (np.abs(full - mid).max(axis=2, keepdims=True) / 24.0).clip(0, 1)
        img = blur * (1 - m) + full * m
    img = img * VIG + np.random.default_rng(int(T * 1000)).normal(0, 4.5, (H, W, 1))
    img = (img + 0.5).clip(0, 255).astype(np.uint8)[:, :, ::-1]
    Image.fromarray(img).save(path, compress_level=1)


def job(i):
    p = os.path.join(OUT, f'f{i:05d}.png')
    if not os.path.exists(p):
        render(i / FPS, p)
    return i


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preview':
        from PIL import Image
        ts = [float(x) for x in sys.argv[2:]]
        ims = []
        for T in ts:
            p = f'/tmp/claude-0/-home-user-Stories/6cbad5e7-e7ab-5124-85a4-0dd8cbe1a969/scratchpad/pv_{T:.2f}.png'
            render(T, p)
            ims.append(Image.open(p).convert('RGB').resize((270, 480)))
        cols = min(7, len(ims))
        rows = (len(ims) + cols - 1) // cols
        sh = Image.new('RGB', (270 * cols, 480 * rows))
        for k, im in enumerate(ims):
            sh.paste(im, ((k % cols) * 270, (k // cols) * 480))
        sh.save('/tmp/claude-0/-home-user-Stories/6cbad5e7-e7ab-5124-85a4-0dd8cbe1a969/scratchpad/pv_sheet.jpg', quality=88)
        print('ok', scenes.END)
    else:
        os.makedirs(OUT, exist_ok=True)
        n = int(round(scenes.END * FPS))
        a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        b = int(sys.argv[3]) if len(sys.argv) > 3 else n
        with Pool(os.cpu_count()) as p:
            for k, i in enumerate(p.imap_unordered(job, range(a, b), chunksize=4)):
                if k % 200 == 0:
                    print('frame', k, flush=True)
        print('DONE', n)
