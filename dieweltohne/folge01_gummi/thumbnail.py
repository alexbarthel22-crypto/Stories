# Erzeugt thumbnail.jpg (1080x1920) aus einem sauberen Einzelbild (src/still.js) mit großer Schrift.
# python3 thumbnail.py clean_2220.png
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
F = '/usr/share/fonts/opentype/inter/'
W, H = 1080, 1920
img = Image.open(sys.argv[1]).convert('RGB').resize((W, H))
img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.25)).enhance(1.12)
# Verläufe oben/unten für Lesbarkeit
ov = Image.new('L', (W, H), 0); d = ImageDraw.Draw(ov)
for y in range(H):
    a = 0
    if y < 900: a = int(215 * (1 - y / 900) ** 1.4)
    if y > 1250: a = max(a, int(200 * ((y - 1250) / 670) ** 1.3))
    d.line([(0, y), (W, y)], fill=a)
img = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), img, ov)
draw = ImageDraw.Draw(img)

def text(cx, y, s, font, fill, stroke=0, sc=(0, 0, 0), shadow=True):
    w = draw.textlength(s, font=font)
    x = cx - w / 2
    if shadow:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 6, y + 10), s, font=font, fill=(0, 0, 0, 200), stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
        img.paste(sh.filter(ImageFilter.GaussianBlur(12)), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
    draw.text((x, y), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=sc)

def fit(s, path, maxw, start):
    size = start
    while ImageFont.truetype(path, size).getlength(s) > maxw: size -= 4
    return ImageFont.truetype(path, size)

# Kicker-Pille
k = ImageFont.truetype(F + 'InterDisplay-Black.otf', 54); ks = 'WAS WÄRE, WENN …'
kw = draw.textlength(ks, font=k)
draw.rounded_rectangle([(W - kw) / 2 - 34, 300, (W + kw) / 2 + 34, 386], 43, fill=(229, 40, 34))
draw.text(((W - kw) / 2, 312), ks, font=k, fill='white')
# Hauptzeilen
text(W / 2, 420, '10 SEKUNDEN', fit('10 SEKUNDEN', F + 'InterDisplay-Black.otf', 900, 160), 'white', 6)
text(W / 2, 580, 'OHNE GUMMI', fit('OHNE GUMMI', F + 'InterDisplay-Black.otf', 980, 220), (255, 196, 0), 8)
# Stufenbalken unten (im 3:4-Ausschnitt des Profilrasters)
cols = ['#4cc76a', '#a5d34a', '#e8d13a', '#f3a531', '#f07a2a', '#e5482b', '#c4161c']
bw, gap, y0 = 112, 12, 1470
x0 = (W - (7 * bw + 6 * gap)) / 2
for i, c in enumerate(cols):
    draw.rounded_rectangle([x0 + i * (bw + gap), y0, x0 + i * (bw + gap) + bw, y0 + 26], 8, fill=c)
text(W / 2, 1516, 'STUFE 7/7: WELTUNTERGANG', fit('STUFE 7/7: WELTUNTERGANG', F + 'InterDisplay-Black.otf', 860, 64), 'white', 3)
img.save('thumbnail.jpg', quality=92)
img.crop((0, 240, W, 1680)).resize((540, 720)).save(sys.argv[2] if len(sys.argv) > 2 else '/dev/null', 'JPEG') if len(sys.argv) > 2 else None
