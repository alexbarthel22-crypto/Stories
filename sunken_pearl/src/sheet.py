import sys, glob, os
from PIL import Image, ImageDraw
names = sys.argv[2:]
out = sys.argv[1]
d = '/home/user/Stories/sunken_pearl/frames/preview'
rows = []
for n in names:
    fs = sorted(glob.glob(f'{d}/{n}_*.png'))
    rows.append((n, fs))
W, H = 270, 480
cols = max(len(f) for _, f in rows)
# zwei Shots pro Zeile
per = 2
nrow = (len(rows) + per - 1) // per
im = Image.new('RGB', (W * cols * per, H * nrow), (40, 40, 40))
dr = ImageDraw.Draw(im)
for i, (n, fs) in enumerate(rows):
    r, c = divmod(i, per)
    for j, f in enumerate(fs):
        im.paste(Image.open(f).convert('RGB'), ((c * cols + j) * W, r * H))
    dr.text(((c * cols) * W + 5, r * H + 5), n, fill=(255, 255, 0))
im.save(out)
