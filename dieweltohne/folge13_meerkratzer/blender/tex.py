# Erzeugt die Bild-Texturen für die Blender-Fassung (Bedienfeld, Pizzakarton). Systempython mit PIL.
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.join(os.path.dirname(__file__), 'tex')
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
SANSB = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
def F(p, s): return ImageFont.truetype(p, s)

def panel(pressed):
    W, H = 1024, 2560
    im = Image.new('RGB', (W, H), (160, 165, 168)); g = ImageDraw.Draw(im)
    r = random.Random(3)
    for y in range(H):  # gebürsteter Stahl
        v = 150 + int(18 * r.random()); g.line([(0, y), (W, y)], fill=(v, v + 4, v + 6))
    im = im.filter(ImageFilter.GaussianBlur(0.6)); g = ImageDraw.Draw(im)
    g.rounded_rectangle([80, 80, W - 80, 320], 20, fill=(18, 22, 24))
    g.text((W // 2, 200), ('▼  0' if pressed else '0'), font=F(MONO, 130), fill=(255, 170, 60), anchor='mm')
    def btn(x, y, label, lit):
        g.ellipse([x - 84, y - 84, x + 84, y + 84], fill=(96, 102, 106))
        g.ellipse([x - 70, y - 70, x + 70, y + 70], fill=(255, 196, 110) if lit else (205, 209, 211))
        g.ellipse([x - 52, y - 52, x + 52, y + 52], fill=(255, 226, 170) if lit else (226, 229, 230))
        if label: g.text((x, y + 130), label, font=F(MONO, 58), fill=(40, 44, 47), anchor='mm')
    labels = ['0', '−1', '−2', '−3', '−4', '−5', '−6', '−7']
    for i, l in enumerate(labels): btn(720 if i % 2 else 304, 500 + (i // 2) * 280, l, False)
    for k in range(3): g.ellipse([W // 2 - 12, 1590 + k * 50 - 12, W // 2 + 12, 1590 + k * 50 + 12], fill=(40, 44, 47))
    btn(304, 1880, '−3.638', False); btn(720, 1880, '−3.639', False)
    btn(W // 2, 2240, '', pressed)
    # Klebeband
    tape = Image.new('RGBA', (820, 156), (232, 206, 92, 140 if pressed else 242)); tg = ImageDraw.Draw(tape)
    tg.text((410, 80), 'NICHT DRÜCKEN', font=F(MONO, 70), fill=(26, 26, 26, 255), anchor='mm')
    for x in range(0, 820, 7): tg.line([(x, 0), (x + 3, 6)], fill=(200, 175, 70, 255)); tg.line([(x, 150), (x + 3, 156)], fill=(200, 175, 70, 255))
    tape = tape.rotate(7, expand=True, resample=Image.BICUBIC)
    im.paste(tape, (W // 2 - tape.width // 2, 2240 - tape.height // 2), tape)
    g = ImageDraw.Draw(im); g.text((W // 2, 2430), '−3.640', font=F(MONO, 58), fill=(40, 44, 47), anchor='mm')
    im.save(os.path.join(D, 'panel_on.png' if pressed else 'panel_off.png'))
    # Leuchtmaske (nur Anzeige + gedrückter Knopf)
    m = Image.new('L', (W, H), 0); mg = ImageDraw.Draw(m)
    mg.text((W // 2, 200), ('▼  0' if pressed else '0'), font=F(MONO, 130), fill=255, anchor='mm')
    if pressed: mg.ellipse([W // 2 - 84, 2240 - 84, W // 2 + 84, 2240 + 84], fill=200)
    m.filter(ImageFilter.GaussianBlur(2)).save(os.path.join(D, 'panel_on_emit.png' if pressed else 'panel_off_emit.png'))

def pizza():
    W = 1024; im = Image.new('RGB', (W, W), (236, 228, 208)); g = ImageDraw.Draw(im); r = random.Random(5)
    for i in range(30000): x, y = r.random() * W, r.random() * W; v = 220 + int(r.random() * 25); g.point((x, y), fill=(v, v - 8, v - 26))
    g.rectangle([48, 48, W - 48, W - 48], outline=(190, 40, 32), width=26)
    g.text((W // 2, W // 2 - 70), 'PIZZA', font=F(SANSB, 230), fill=(190, 40, 32), anchor='mm')
    g.text((W // 2, W // 2 + 130), 'HEISS & FRISCH', font=F(SANSB, 84), fill=(44, 120, 56), anchor='mm')
    for i in range(7):  # Fettflecken
        x, y, s = 120 + i * 120 + r.random() * 30, 820 + r.random() * 70, 18 + r.random() * 22
        g.ellipse([x - s, y - s * 0.8, x + s, y + s * 0.8], fill=(205, 180, 140))
    im.filter(ImageFilter.GaussianBlur(0.8)).save(os.path.join(D, 'pizza.png'))

panel(False); panel(True); pizza()
print('ok')
