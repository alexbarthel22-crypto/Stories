"""Story #9 – Drei Papas (Mystery in der Du-Form, Kommentar-Frage am Ende).

usage:  python3 make_video.py            -> renders video.mp4 (needs timing.json + mix.wav)
        python3 make_video.py --stills t1 t2 ...  -> preview stills in ./stills
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from toolkit import *  # noqa
from toolkit import _shade
from fx3d import BCanvas, pill3d, burst
from fx3d import pop_pill as _pop_pill
from people import Look, draw_char

CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
Z = 2
INK = hexc("#1d1b33")
_T = [0.0]

DU = Look("#e9b48f", "#5a3a22", "#4a6fa5", "#2d3436", "#f5f6fa", hair_style="short", top_style="hoodie",
          trim="#3b5a88", eyes="#3b2a20")
LINA = Look("#f3d2b5", "#c58b4a", "#ff8fb1", "#6c5ce7", "#ffd34d", hair_style="ponytail", top_style="tee",
            lashes=True, eyes="#3a7bd5")
PAPA = Look("#e0ac69", "#2d1e12", "#2f5d50", "#3b3b58", "#5a3a22", hair_style="short", top_style="bomber",
            trim="#1e4038", under="#d9d2c5", glasses=True, beard=True, eyes="#3b2a20")

# ------------------------------------------------------------------ timing
TIM = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
KEYS = ["Es ist 23", "Es klingelt", "„Mach schnell", "Im selben", "„Sitze", "Du schaust", "Dann zupft", "Und tatsächlich",
        "Du schreibst", "Die Antwort", "Durch die", "„Kapitän", "Das stimmt", "Plötzlich", "„Wer ist", "Das Licht",
        "Eine letzte", "Draußen klopft", "Da flüstert", "Drei Papas", "Wem glaubst"]
S, E = anchors(TIM, KEYS)
K = {k: i for i, k in enumerate(KEYS)}
END = E[-1] + 0.8
XFADE = 0.22


def st(k):
    return S[K[k]]


def en(k):
    return E[K[k]]


def wt(key, word, frac=0.3):
    seg = next(x for x in TIM if x["text"].startswith(key))
    i = seg["text"].find(word)
    f = (i + len(word) * frac) / len(seg["text"])
    return seg["start"] + (seg["end"] - seg["start"]) * f


def pop_pill(img, t, t0, cx, cy, text, size, **kw):
    _pop_pill(img, t, t0, cx, cy, text, int(size * 1.12), **kw)


def ftext(cv, x, y, txt, size, max_w, col, anchor="mm"):
    if size < 6:
        return
    while font(int(size)).getbbox(txt)[2] > max_w and size > 8:
        size *= 0.95
    cv.text(x, y, txt, size, col, anchor=anchor)


def shadow(cv, x, y, w):
    cv.ellipse(x - w, y - w * 0.12, x + w, y + w * 0.12, fill=(5, 5, 15, 90))


# ------------------------------------------------------------------ the house (screen world, cached 2x)
FLOOR = 1440
DOOR = (70, 820, 330, FLOOR)            # front door
MON = (370, 960, 540, 1080)             # intercom monitor on the wall
WIN = (390, 470, 610, 760)              # window with rain
BATH = (700, 300, 880, 610)             # bathroom door at the top of the stairs
CLOCK = (200, 680, 62)


def bg_house(img, cv):
    img.paste(vgradient(img.width, img.height, [(0, "#141834"), (0.75, "#1d2246"), (1, "#121530")]))
    for x in range(0, 1081, 90):                      # wallpaper stripes
        cv.rect(x, 0, x + 40, FLOOR, fill=(255, 255, 255, 8))
    cv.rect(0, FLOOR, 1080, 1920, fill=hexc("#2a2033"))
    for k in range(10):
        cv.line([(k * 130, FLOOR), (k * 130 - 90, 1920)], (60, 45, 70, 255), 4, cap=False)
    cv.rect(0, FLOOR - 14, 1080, FLOOR, fill=hexc("#3a3050"))
    # front door with frosted glass
    x0, y0, x1, y1 = DOOR
    cv.rect(x0 - 14, y0 - 14, x1 + 14, y1, fill=hexc("#3b2a24"))
    cv.rect(x0, y0, x1, y1, fill=hexc("#5a3a2c"))
    cv.rect(x0 + 40, y0 + 50, x1 - 40, y0 + 300, fill=hexc("#2b3a5c"), r=10)
    for k in range(5):
        cv.line([(x0 + 50 + k * 40, y0 + 60), (x0 + 70 + k * 40, y0 + 290)], (255, 255, 255, 18), 6)
    cv.circle(x1 - 34, y0 + 360, 10, fill=hexc("#c9a46a"))
    cv.rect(x1 - 44, y0 + 380, x1 - 24, y0 + 400, fill=hexc("#1d1b33"), r=4)
    # intercom
    x0, y0, x1, y1 = MON
    cv.rect(x0 - 10, y0 - 10, x1 + 10, y1 + 40, fill=hexc("#d9d5e6"), r=12)
    cv.rect(x0, y0, x1, y1, fill=hexc("#0b0d1a"), r=6)
    cv.circle((x0 + x1) / 2, y1 + 20, 9, fill=hexc("#8a8aa8"))
    # window frame
    x0, y0, x1, y1 = WIN
    cv.rect(x0 - 14, y0 - 14, x1 + 14, y1 + 20, fill=hexc("#d9d5e6"))
    cv.rect(x0, y0, x1, y1, fill=hexc("#0a0d22"))
    # clock
    cx, cy, r = CLOCK
    cv.circle(cx, cy, r + 8, fill=hexc("#c9a46a"))
    cv.circle(cx, cy, r, fill=hexc("#f4efe4"))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        cv.circle(cx + math.sin(a) * r * 0.8, cy - math.cos(a) * r * 0.8, 3.5, fill=INK)
    # staircase to the bathroom
    for k in range(10):
        y = FLOOR - k * 84
        x = 1080 - k * 44
        cv.rect(x - 250, y - 84, 1080, y, fill=hexc("#4a3428"))
        cv.rect(x - 250, y - 84, 1080, y - 70, fill=hexc("#6b4a36"))
    cv.rect(640, BATH[3], 1080, BATH[3] + 40, fill=hexc("#4a3428"))
    for k in range(10):
        x = 860 - k * 44
        y = FLOOR - 84 * k - 150
        cv.line([(x, y), (x, y + 130)], hexc("#d9d5e6"), 6)
    cv.line([(900, FLOOR - 150), (470, FLOOR - 840 - 150)], hexc("#d9d5e6"), 10)
    # bathroom door (light from inside drawn per frame)
    x0, y0, x1, y1 = BATH
    cv.rect(x0 - 12, y0 - 12, x1 + 12, y1, fill=hexc("#3b2a24"))
    cv.rect(x0, y0, x1, y1, fill=hexc("#6b4a36"))
    cv.circle(x0 + 26, (y0 + y1) / 2, 8, fill=hexc("#c9a46a"))
    # sofa + lamp
    cv.rect(560, 1250, 860, 1440, fill=hexc("#5a4a7a"), r=30)
    cv.rect(540, 1300, 880, 1440, fill=hexc("#6b5a8f"), r=30)
    cv.line([(990, FLOOR - 10), (990, 1230)], hexc("#8a8aa8"), 6) if False else None
    # family photo
    cv.rect(640, 780, 780, 900, fill=hexc("#c9a46a"))
    cv.rect(652, 792, 768, 888, fill=hexc("#b9d6f2"))
    for k, c in enumerate(("#2d1e12", "#c58b4a", "#5a3a22")):
        cv.circle(680 + k * 30, 830, 12, fill=hexc(c))
        cv.rect(670 + k * 30, 844, 690 + k * 30, 880, fill=hexc(["#2f5d50", "#ff8fb1", "#4a6fa5"][k]))


_BG = {}


def bg():
    if "h" not in _BG:
        p = os.path.join(CACHE, "bg_house.png")
        if not os.path.exists(p):
            img = Image.new("RGB", (OUT_W * Z, OUT_H * Z))
            bg_house(img, BCanvas(img, 0, 0, Z))
            img.save(p)
        _BG["h"] = Image.open(p).convert("RGB")
    return _BG["h"]


def stage(cam, actors=None):
    cx, cy, vh = cam
    vh = min(vh, OUT_H)
    vw = vh * OUT_W / OUT_H
    cx = clamp(cx, vw / 2, OUT_W - vw / 2)
    cy = clamp(cy, vh / 2, OUT_H - vh / 2)
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    crop = bg().crop(tuple(int(round(v * Z)) for v in box)).convert("RGBA")
    if actors:
        actors(BCanvas(crop, box[0], box[1], Z))
    return crop.convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS), box


def w2s(x, y, box):
    k = (box[3] - box[1]) / OUT_H
    return (x - box[0]) / k, (y - box[1]) / k


def drift(cam, t, a=1.0):
    cx, cy, vh = cam
    k = vh / OUT_H
    return (cx + a * k * 8 * math.sin(t * 0.45), cy + a * k * 5 * math.sin(t * 0.33 + 1), vh * (1 + 0.012 * math.sin(t * 0.55)))


LIGHTNING = [0.15, 9.7]


def flash(t):
    a = 0.0
    for t0 in LIGHTNING + [st("Plötzlich") - 0.2]:
        d = t - t0
        if 0 <= d < 0.35:
            a = max(a, (1 - d / 0.35) * (0.6 if (d * 20) % 2 < 1 else 0.3))
    return a


def house_life(cv, t, light_on=True, shower=True, bath_open=0.0):
    x0, y0, x1, y1 = WIN
    fl = flash(t)
    if fl > 0:
        cv.rect(x0, y0, x1, y1, fill=(200, 210, 255, int(255 * fl)))
        cv.line([(x0 + 140, y0), (x0 + 110, y0 + 90), (x0 + 150, y0 + 120), (x0 + 100, y1)], (255, 255, 255, int(255 * fl)), 5)
    for i in range(26):                      # rain on the window
        rx = x0 + (i * 37) % (x1 - x0)
        ry = y0 + ((t * 600 + i * 97) % (y1 - y0))
        cv.line([(rx, ry), (rx - 6, ry + 26)], (150, 170, 230, 150), 2)
    for i in range(8):
        dx = x0 + 20 + (i * 53) % (x1 - x0 - 40)
        dy = y0 + ((t * 40 + i * 70) % (y1 - y0))
        cv.circle(dx, dy, 4, fill=(190, 210, 255, 120))
    # clock 23:41 (minute hand creeps)
    cx, cy, r = CLOCK
    m = 41 + (t / 60)
    ah = (11 + m / 60) / 12 * 2 * math.pi
    am = m / 60 * 2 * math.pi
    cv.line([(cx, cy), (cx + math.sin(ah) * r * 0.5, cy - math.cos(ah) * r * 0.5)], INK, 7)
    cv.line([(cx, cy), (cx + math.sin(am) * r * 0.8, cy - math.cos(am) * r * 0.8)], hexc("#e2574c"), 4)
    cv.circle(cx, cy, 6, fill=INK)
    # bathroom: light under the door + steam while the shower runs
    bx0, by0, bx1, by1 = BATH
    if shower:                                   # only the light under the bathroom door
        cv.rect(bx0, by1 - 8, bx1, by1, fill=(255, 236, 170, 230))
    if bath_open > 0:
        cv.rect(bx0, by0, bx0 + (bx1 - bx0) * bath_open, by1, fill=hexc("#05060f"))
    # monitor glow when the bell rang
    if light_on:
        cv.circle(990, 1150, 0, fill=(0, 0, 0, 0))


def darkness(img, a, holes=()):
    """darken the frame; holes = [(x, y, r)] in screen space stay lit (phone glow, flashlights)"""
    if a <= 0.01:
        return img
    m = Image.new("L", img.size, int(255 * a))
    d = ImageDraw.Draw(m)
    for x, y, r in holes:
        d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    m = m.filter(ImageFilter.GaussianBlur(60))
    return Image.composite(Image.new("RGB", img.size, (3, 3, 10)), img, m)


# ------------------------------------------------------------------ props in screen space
def phone_ui(img, t, msgs, battery=82, vibrate=0.0, typing=None, dead=0.0, scale=1.0, cx=540, cy=1000):
    """messenger screen. msgs = [(side 'in'/'out', text, t_appear)]"""
    W2, H2 = 560, 1080
    tile = Image.new("RGBA", ((W2 + 40) * Z, (H2 + 40) * Z), (0, 0, 0, 0))
    cv = BCanvas(tile, -20, -20, Z)
    cv.rect(0, 0, W2, H2, fill=hexc("#0e0f18"), r=70)
    cv.rect(14, 14, W2 - 14, H2 - 14, fill=hexc("#f2f3f8"), r=58)
    cv.rect(14, 14, W2 - 14, 210, fill=hexc("#2f5d50"), r=58)
    cv.rect(14, 150, W2 - 14, 210, fill=hexc("#2f5d50"))
    cv.rect(W2 / 2 - 70, 30, W2 / 2 + 70, 56, fill=hexc("#0e0f18"), r=13)
    cv.circle(90, 150, 40, fill=hexc("#d9d2c5"))
    cv.text(90, 152, "P", 44, hexc("#2f5d50"))
    cv.text(150, 135, "Papa", 44, hexc("#ffffff"), anchor="lm")
    cv.text(150, 178, "online", 26, (200, 235, 220, 255), anchor="lm")
    bc = hexc("#e2574c") if battery <= 5 else hexc("#ffffff")
    cv.rect(W2 - 110, 70, W2 - 50, 98, outline=hexc("#ffffff"), width=3, r=6)
    cv.rect(W2 - 106, 74, W2 - 106 + 52 * battery / 100, 94, fill=bc, r=4)
    cv.text(W2 - 120, 84, f"{battery}%", 22, bc, anchor="rm")
    y = 260
    for side, text, ta in msgs:
        if t < ta:
            continue
        a = ease_out_back(prog(t, ta, ta + 0.3))
        words, lines, cur = text.split(), [], ""
        for w in words:
            if font(30).getbbox(cur + " " + w)[2] > 330:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        bh = 30 + 42 * len(lines)
        bw = max(font(30).getbbox(l)[2] for l in lines) + 50
        if side == "in":
            bx0 = 40
        else:
            bx0 = W2 - 40 - bw
        col = hexc("#ffffff") if side == "in" else hexc("#d4f5c9")
        cv.rect(bx0, y, bx0 + bw * a, y + bh * a, fill=col, r=26)
        if a > 0.8:
            for k, l in enumerate(lines):
                cv.text(bx0 + 25, y + 36 + k * 42, l, 30, INK, anchor="lm")
            cv.text(bx0 + bw - 20, y + bh - 14, "23:4" + str(2 + int(ta) % 8), 18, (120, 120, 140, 255), anchor="rm")
        y += bh + 30
    if typing is not None and t >= typing[0]:
        txt = typing[1][:int(len(typing[1]) * prog(t, typing[0], typing[0] + typing[2]))]
        cv.rect(30, H2 - 130, W2 - 30, H2 - 50, fill=hexc("#ffffff"), r=40)
        ftext(cv, 60, H2 - 90, txt + ("|" if int(t * 3) % 2 else ""), 26, W2 - 120, INK, anchor="lm")
    if dead > 0.01:
        cv.rect(14, 14, W2 - 14, H2 - 14, fill=(5, 5, 10, int(255 * dead)), r=58)
    if scale < 0.02:
        return
    tile = tile.resize((int(tile.width * scale / Z), int(tile.height * scale / Z)), Image.LANCZOS)
    sh = 10 * vibrate * math.sin(t * 90)
    img.paste(tile, (int(cx - tile.width / 2 + sh), int(cy - tile.height / 2)), tile)


def monitor_view(img, t, stare=0.0, talk=0.0, zoom=1.0):
    """full-screen door camera: Papa in the rain, slightly fish-eyed and grainy"""
    W2, H2 = 760, 1100
    tile = Image.new("RGBA", (W2 * Z, H2 * Z), (0, 0, 0, 0))
    cv = BCanvas(tile, 0, 0, Z)
    cv.rect(0, 0, W2, H2, fill=hexc("#0f1a24"), r=40)
    cv.rect(20, 20, W2 - 20, H2 - 20, fill=hexc("#22333f"), r=30)
    for k in range(6):
        cv.rect(20, 20 + k * 200, W2 - 20, 120 + k * 200, fill=(255, 255, 255, 6))
    h = 1350 * zoom
    g = draw_char(cv, W2 / 2 - 30, 300 + h * 0.86, PAPA, h, 1, t=t, blink=False, talk=talk, mood="smirk",
                  breathe=0.3, sway=0.2)
    if stare > 0.01:                          # unblinking stare: eyes stay wide, slow zoom handled by caller
        for ex in (g["fx"] - g["r"] * 0.33, g["fx"] + g["r"] * 0.33):
            cv.circle(ex, g["ey"], g["r"] * 0.22, outline=(255, 255, 255, int(120 * stare)), width=3)
    for i in range(70):                       # rain
        rx = (i * 61) % W2
        ry = (t * 900 + i * 131) % H2
        cv.line([(rx, ry), (rx - 10, ry + 46)], (170, 190, 230, 120), 3)
    for k in range(0, H2, 6):                 # scanlines
        cv.rect(20, k, W2 - 20, k + 2, fill=(0, 0, 0, 30))
    cv.circle(60, 60, 12, fill=hexc("#e2574c") if int(t * 2) % 2 else hexc("#6a2020"))
    cv.text(84, 60, "REC  23:41", 26, hexc("#ffffff"), anchor="lm")
    cv.text(W2 - 40, H2 - 50, "HAUSTÜR", 26, (200, 210, 230, 255), anchor="rm")
    m = Image.new("L", tile.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, tile.width, tile.height], radius=80, fill=255)
    tile.putalpha(m)
    tile = tile.resize((W2, H2), Image.LANCZOS)
    img.paste(tile, (int(530 - W2 / 2), int(1010 - H2 / 2)), tile)


# ------------------------------------------------------------------ scenes
DU_X, LINA_X = 560, 740


def people(cv, t, du_kw=None, lina_kw=None, du_h=440, lina_h=300, lina=True):
    shadow(cv, DU_X, FLOOR, 90)
    kw = dict(t=t, mood="worried")
    kw.update(du_kw or {})
    draw_char(cv, DU_X, FLOOR, DU, du_h, -1, **kw)
    if lina:
        shadow(cv, LINA_X, FLOOR, 60)
        kw = dict(t=t + 3, mood="smile")
        kw.update(lina_kw or {})
        g = draw_char(cv, LINA_X, FLOOR, LINA, lina_h, -1, **kw)
        bx, by = g["hand_b"]                  # plush bunny in her hand
        cv.ellipse(bx - 18, by - 10, bx + 18, by + 34, fill=hexc("#efe6f5"))
        cv.circle(bx, by - 18, 15, fill=hexc("#efe6f5"))
        cv.ellipse(bx - 12, by - 60, bx - 2, by - 24, fill=hexc("#efe6f5"))
        cv.ellipse(bx + 2, by - 60, bx + 12, by - 24, fill=hexc("#efe6f5"))


def phone_in_hand():
    return dict(arm_f=("ik", (DU_X - 0.14 * 440, FLOOR - 0.62 * 440)), hand_f="fist")


def sc_intro(t):
    t0, t1 = st("Es ist 23"), st("Es klingelt")
    cam = keyframes(t, [(0, (CLOCK[0] + 60, CLOCK[1] + 80, 700)), (wt("Es ist 23", "Du bist", 0.0), (CLOCK[0] + 60, CLOCK[1] + 80, 700)),
                        (wt("Es ist 23", "Du bist", 0.0) + 1.0, (620, 1060, 1300))])

    def act(cv):
        house_life(cv, t)
        people(cv, t, du_kw=dict(mood="smile"), lina_kw=dict(mood="smile"))
    img, _ = stage(drift(cam, t), act)
    img = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), flash(t) * 0.5)
    pop_pill(img, t, t0 + 0.05, 540, 330, "23:41 UHR", 92, bg="#1d1b33", fg="#ffd34d", rot=-2)
    pop_pill(img, t, wt("Es ist 23", "allein", 0.0), 540, 480, "ALLEIN MIT LINA", 62, bg="#fff6e6", rot=2)
    return img


def sc_bell(t):
    t0, t1, t2 = st("Es klingelt"), st("„Mach schnell"), en("„Mach schnell")
    tv = wt("Es klingelt", "Bildschirm", 0.0)
    if t < tv:
        cam = keyframes(t, [(t0, (620, 1060, 1300)), (tv, (MON[0] + 85, MON[1] + 60, 700))])

        def act(cv):
            house_life(cv, t)
            x0, y0, x1, y1 = MON
            cv.rect(x0, y0, x1, y1, fill=(80, 120, 160, 255))
            people(cv, t, du_kw=dict(look=(-0.8, -0.2), mood="o"))
        img, _ = stage(drift(cam, t), act)
        pop_pill(img, t, t0 + 0.05, 540, 330, "DING – DONG", 80, bg="#ffd34d", rot=-3)
        return img
    img = Image.new("RGB", (OUT_W, OUT_H), (8, 9, 20))
    monitor_view(img, t, talk=0.8 if t1 <= t < t2 else 0.0)
    pop_pill(img, t, tv, 540, 330, "PAPA STEHT VOR DER TÜR", 52, bg="#fff6e6", rot=-2, t1=t1 - 0.1)
    if t >= t1:
        pop_pill(img, t, t1 + 0.05, 540, 330, "„MACH SCHNELL AUF!“", 60, bg="#ffd34d", rot=-2)
        pop_pill(img, t, wt("„Mach schnell", "Schlüssel", 0.0), 540, 1680 - 1680 + 1420, "SCHLÜSSEL VERGESSEN", 46,
                 bg="#fff6e6", rot=2)
    return img


def sc_phone(t):
    t0, t1 = st("Im selben"), st("„Sitze")
    msgs = [("in", "Sitze noch im Zug. Bin in 2 Std. da. Mach NIEMANDEM auf!", t1)]
    img, _ = stage((DU_X - 80, 1080, 1000), lambda cv: (house_life(cv, t), people(cv, t, du_kw=phone_in_hand(), lina=False)))
    img = darkness(img, 0.5)
    phone_ui(img, t, msgs, battery=12, vibrate=1.0 if t0 <= t < t0 + 1.0 else 0.0, scale=ease_out_back(prog(t, t0, t0 + 0.35)),
             cy=1010)
    pop_pill(img, t, t0 + 0.1, 540, 330, "PAPA SCHREIBT …", 66, bg="#2f5d50", fg="#ffffff", rot=-2)
    return img


def sc_stare(t):
    t0 = st("Du schaust")
    z = 1 + 0.9 * smooth(prog(t, t0, en("Du schaust")))
    img = Image.new("RGB", (OUT_W, OUT_H), (8, 9, 20))
    monitor_view(img, t, stare=prog(t, wt("Du schaust", "blinzelt", 0.0), wt("Du schaust", "blinzelt", 0.0) + 0.4), zoom=z)
    pop_pill(img, t, wt("Du schaust", "lächelt", 0.0), 540, 330, "ER LÄCHELT …", 64, bg="#fff6e6", rot=-2)
    pop_pill(img, t, wt("Du schaust", "blinzelt", 0.0), 540, 470, "UND BLINZELT NICHT", 56, bg="#e2574c", fg="#ffffff", rot=2)
    return img


def sc_lina(t):
    t0, t1 = st("Dann zupft"), st("Und tatsächlich")
    tq = wt("Dann zupft", "Warum", 0.0)
    if t < t1:
        def act(cv):
            house_life(cv, t)
            g = draw_char(cv, DU_X, FLOOR, DU, 440, -1, t=t, mood="worried", look=(0.6, 0.2))
            shadow(cv, LINA_X - 40, FLOOR, 60)
            tug = 6 * math.sin(t * 9) if t < tq else 0
            draw_char(cv, LINA_X - 40, FLOOR, LINA, 300, -1, t=t + 3, arm_f=("ik", (DU_X + 50 + tug, FLOOR - 230)),
                      talk=0.7 if t >= tq else 0.0, mood="smile", look=(0.3, -0.8))
        img, _ = stage(drift((650, 1170, 900), t), act)
        pop_pill(img, t, tq, 540, 330, "„PAPA IST DOCH", 60, bg="#ff8fb1", fg="#ffffff", rot=-2)
        pop_pill(img, t, wt("Dann zupft", "oben", 0.0), 540, 470, "OBEN IM BAD!“", 70, bg="#fff6e6", rot=2)
        return img
    return sc_shower(t)


def sc_shower(t):
    t0 = st("Und tatsächlich")
    cam = keyframes(t, [(t0, (650, 1170, 900)), (t0 + 1.4, (790, 520, 760))])

    def act(cv):
        house_life(cv, t)
        people(cv, t, du_kw=dict(look=(0.8, -1.0), mood="o"), lina_kw=dict(look=(0.8, -1.0)))
    img, _ = stage(drift(cam, t), act)
    pop_pill(img, t, t0 + 0.2, 540, 330, "DIE DUSCHE LÄUFT …", 64, bg="#bfe6ff", rot=-2)
    pop_pill(img, t, wt("Und tatsächlich", "Seit", 0.0), 540, 470, "SEIT ÜBER 1 STUNDE", 52, bg="#fff6e6", rot=2)
    return img


Q_TEXT = "Was hast du mir früher vor dem Einschlafen erzählt?"
A_TEXT = "Die Geschichten von Kapitän Krümel, dem Piraten ohne Schiff."


def sc_ask(t):
    t0, t1 = st("Du schreibst"), st("Die Antwort")
    msgs = [("in", "Sitze noch im Zug. Bin in 2 Std. da. Mach NIEMANDEM auf!", -1),
            ("out", Q_TEXT, en("Du schreibst") - 0.3), ("in", A_TEXT, t1 + 0.3)]
    img = Image.new("RGB", (OUT_W, OUT_H), (10, 11, 24))
    phone_ui(img, t, msgs, battery=9, typing=(t0, Q_TEXT, en("Du schreibst") - t0 - 0.4) if t < en("Du schreibst") - 0.3 else None)
    if t >= t1 + 0.6:
        pop_pill(img, t, t1 + 0.6, 540, 330, "✓  STIMMT!", 72, bg="#37b26c", fg="#ffffff", rot=-2)
    else:
        pop_pill(img, t, t0 + 0.1, 540, 330, "DIE KONTROLLFRAGE", 60, bg="#fff6e6", rot=-2)
    return img


def silhouette(cv, x, y, h, a=255, laugh=0.0, t=0.0):
    col = (8, 10, 20, a)
    cv.rect(x - 0.13 * h, y - 0.8 * h, x + 0.13 * h, y, fill=col, r=0.08 * h)
    cv.circle(x, y - 0.88 * h + 4 * laugh * math.sin(t * 20), 0.1 * h, fill=col)


def sc_door(t):
    t0, t1, t2 = st("Durch die"), st("„Kapitän"), st("Das stimmt")
    cam = keyframes(t, [(t0, (330, 1100, 1100))])

    def act(cv):
        house_life(cv, t)
        x0, y0, x1, y1 = DOOR
        lit = 0.6 + 0.4 * math.sin(t * 2)
        cv.rect(x0 + 40, y0 + 50, x1 - 40, y0 + 300, fill=(60, 80, 120, 255))
        silhouette(cv, (x0 + x1) / 2, y0 + 520, 520, 200, laugh=1.0 if t >= t1 else 0.0, t=t)
        cv.rect(x0 + 40, y0 + 300, x1 - 40, y1, fill=hexc("#5a3a2c"))
        cv.circle(x1 - 34, y0 + 360, 10, fill=hexc("#c9a46a"))
        shadow(cv, 450, FLOOR, 90)
        draw_char(cv, 450, FLOOR, DU, 440, -1, t=t, mood="worried", talk=0.6 if t < t1 else 0.0,
                  arm_f=("ik", (x1 + 20, y0 + 380)), hand_f="relaxed")
    img, box = stage(drift(cam, t), act)
    pop_pill(img, t, t0 + 0.1, 540, 330, "DIESELBE FRAGE", 70, bg="#fff6e6", rot=-2, t1=t1 - 0.1)
    if t >= t1:
        pop_pill(img, t, t1 + 0.1, 540, 330, "„KAPITÄN KRÜMEL …", 60, bg="#ffd34d", rot=-2)
        pop_pill(img, t, wt("„Kapitän", "Papagei", 0.0), 540, 470, "PAPAGEI SPRICHT RÜCKWÄRTS“", 46, bg="#fff6e6", rot=2)
        if t > wt("„Kapitän", "rückwärts", 0.0):
            pop_pill(img, t, wt("„Kapitän", "rückwärts", 0.0), 760, 1350, "!OLLAH", 48, bg="#3cc9a4", fg="#ffffff", rot=6)
    return img


def sc_both(t):
    t0 = st("Das stimmt")
    img = Image.new("RGB", (OUT_W, OUT_H), (10, 11, 24))
    lay = Image.new("RGBA", (OUT_W * Z, OUT_H * Z), (0, 0, 0, 0))
    cv = BCanvas(lay, 0, 0, Z)
    for k, (x, label) in enumerate(((290, "HANDY"), (700, "TÜR"))):
        a = ease_out_back(prog(t, t0 + 0.1 + k * 0.3, t0 + 0.4 + k * 0.3))
        cv.rect(x - 170, 760, x + 170, 1260, fill=hexc("#22253f"), r=40)
        if k == 0:
            cv.rect(x - 80, 830, x + 80, 1110, fill=hexc("#f2f3f8"), r=24)
            cv.rect(x - 80, 830, x + 80, 880, fill=hexc("#2f5d50"), r=24)
        else:
            cv.rect(x - 90, 820, x + 90, 1120, fill=hexc("#5a3a2c"), r=8)
            silhouette(cv, x, 1000, 200, 220)
        cv.text(x, 1190, label, 46, hexc("#ffffff"))
        if a > 0.01:
            cv.circle(x + 120, 800, 56 * a, fill=hexc("#37b26c"))
            cv.line([(x + 95, 800), (x + 115, 822), (x + 150, 780)], hexc("#ffffff"), 12 * a)
    lay = lay.resize((OUT_W, OUT_H), Image.LANCZOS)
    img.paste(lay, (0, 0), lay)
    pop_pill(img, t, t0 + 0.1, 540, 360, "BEIDE WISSEN ES.", 76, bg="#e2574c", fg="#ffffff", rot=-2)
    return img


def sc_steps(t):
    t0, t1 = st("Plötzlich"), st("„Wer ist")
    open_ = smooth(prog(t, wt("Plötzlich", "Schritte", 0.0) - 0.4, wt("Plötzlich", "Schritte", 0.0) + 0.3))
    cam = keyframes(t, [(t0, (790, 560, 820)), (t1, (760, 760, 1150))])

    def act(cv):
        house_life(cv, t, shower=t < wt("Plötzlich", "still", 0.0), bath_open=open_)
        if t > wt("Plötzlich", "Schritte", 0.0):          # a shadow on the wall grows down the stairs
            p = prog(t, wt("Plötzlich", "Schritte", 0.0), en("„Wer ist") + 0.5)
            x, y = 820 - 240 * p, BATH[3] + 330 * p
            silhouette(cv, x, y, 380 + 120 * p, 150)
    img, _ = stage(drift(cam, t), act)
    img = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), flash(t) * 0.5)
    if t < t1:
        pop_pill(img, t, wt("Plötzlich", "still", 0.0), 540, 330, "DIE DUSCHE IST AUS.", 60, bg="#fff6e6", rot=-2)
        pop_pill(img, t, wt("Plötzlich", "Schritte", 0.0), 540, 470, "SCHRITTE …", 66, bg="#e2574c", fg="#ffffff", rot=2)
    else:
        pop_pill(img, t, t1 + 0.05, 540, 330, "„WER IST DA AN DER TÜR?", 52, bg="#fff6e6", rot=-2)
        pop_pill(img, t, wt("„Wer ist", "Mach", 0.0), 540, 470, "MACH BLOSS NICHT AUF!“", 56, bg="#e2574c", fg="#ffffff", rot=2)
    return img


def sc_dark(t):
    t0, t1, t2 = st("Das Licht"), st("Eine letzte"), en("Eine letzte")
    off = wt("Das Licht", "aus", 0.3)
    msgs = [("out", Q_TEXT, -1), ("in", A_TEXT, -1), ("in", "Der im Haus ist nicht ich.", t1 + 0.5)]
    if t < off:
        img, _ = stage((620, 1060, 1300), lambda cv: (house_life(cv, t), people(cv, t, du_kw=dict(mood="o"))))
        pop_pill(img, t, t0 + 0.05, 540, 330, "DAS LICHT GEHT AUS", 60, bg="#fff6e6", rot=-2)
        return img
    img = Image.new("RGB", (OUT_W, OUT_H), (3, 3, 10))
    glow = Image.new("RGB", img.size, (40, 60, 70))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([140, 380, 940, 1640], fill=150)
    img = Image.composite(glow, img, m.filter(ImageFilter.GaussianBlur(120)))
    phone_ui(img, t, msgs, battery=1, dead=prog(t, t2 + 0.1, t2 + 0.5), vibrate=1.0 if t1 + 0.5 <= t < t1 + 1.2 else 0.0)
    if t < t1:
        pop_pill(img, t, off, 540, 330, "AKKU: 1 %", 80, bg="#e2574c", fg="#ffffff", rot=-2)
    else:
        pop_pill(img, t, t1 + 0.5, 540, 330, "„DER IM HAUS", 66, bg="#fff6e6", rot=-2)
        pop_pill(img, t, t1 + 0.8, 540, 470, "IST NICHT ICH.“", 72, bg="#e2574c", fg="#ffffff", rot=2)
    return img


def sc_knock(t):
    t0, t1 = st("Draußen klopft"), st("Da flüstert")
    tk = t0 + 0.1
    shake = 8 * math.sin(t * 60) * max(0.0, 1 - ((t - tk) % 1.0) / 0.35) if t > tk else 0

    def act(cv):
        house_life(cv, t, shower=False, bath_open=1.0)
        x0, y0, x1, y1 = DOOR
        bx = x0 + 120 + 60 * math.sin(t * 1.7)
        cv.circle(bx, y0 + 170, 70, fill=(255, 250, 220, 120))          # flashlight through the glass
        p = prog(t, t0, en("Draußen klopft") + 0.6)
        silhouette(cv, 820 - 150 * p, FLOOR - 200 + 140 * p, 520, 210)
    img, _ = stage((540 + shake, 1060, 1500), act)
    img = darkness(img, 0.62, holes=[(110 + 160, 820 - 60, 160)])
    pop_pill(img, t, t0 + 0.1, 290, 330, "KLOPF KLOPF", 54, bg="#fff6e6", rot=-4)
    pop_pill(img, t, wt("Draußen klopft", "Schritte", 0.0), 790, 470, "SCHRITTE", 54, bg="#e2574c", fg="#ffffff", rot=4)
    return img


def sc_whisper(t):
    t0 = st("Da flüstert")

    def act(cv):
        house_life(cv, t, shower=False, bath_open=1.0)
        shadow(cv, LINA_X - 80, FLOOR, 60)
        draw_char(cv, LINA_X - 80, FLOOR, LINA, 300, -1, t=t, talk=0.45, mood="worried", look=(0.2, -0.6), brows=0.5)
    img, box = stage((LINA_X - 100, 1210, 620), act)
    img = darkness(img, 0.55, holes=[(560, 1000, 380)])
    pop_pill(img, t, wt("Da flüstert", "Ich hab", 0.0), 540, 330, "„ICH HAB SCHON JEMANDEN", 48, bg="#ff8fb1", fg="#ffffff", rot=-2)
    pop_pill(img, t, wt("Da flüstert", "reingelassen", 0.0), 540, 470, "REINGELASSEN …“", 66, bg="#fff6e6", rot=2)
    return img


def icon_card(cv, x, y, kind, a, t):
    cv.rect(x - 125, y - 170, x + 125, y + 170, fill=hexc("#22253f"), r=36)
    if kind == "door":
        cv.rect(x - 70, y - 130, x + 70, y + 110, fill=hexc("#5a3a2c"), r=8)
        cv.rect(x - 46, y - 104, x + 46, y - 10, fill=hexc("#2b3a5c"), r=6)
        silhouette(cv, x, y + 40, 150, 220)
    elif kind == "phone":
        cv.rect(x - 60, y - 120, x + 60, y + 110, fill=hexc("#f2f3f8"), r=20)
        cv.rect(x - 60, y - 120, x + 60, y - 70, fill=hexc("#2f5d50"), r=20)
        cv.text(x, y - 95, "Papa", 26, hexc("#ffffff"))
    else:
        for k in range(5):
            cv.rect(x - 110 + k * 44, y + 110 - k * 44, x + 120, y + 110 - (k - 1) * 44, fill=hexc("#4a3428"))
        silhouette(cv, x + 40, y - 40, 170, 230)
    cv.text(x, y + 140, "?", 60, hexc("#ffd34d"))


def sc_three(t):
    t0, t1 = st("Drei Papas"), st("Wem glaubst")
    img = Image.new("RGB", (OUT_W, OUT_H), (10, 11, 24))
    lay = Image.new("RGBA", (OUT_W * Z, OUT_H * Z), (0, 0, 0, 0))
    cv = BCanvas(lay, 0, 0, Z)
    labels = (("door", "TÜR"), ("phone", "HANDY"), ("stairs", "TREPPE"))
    for k, (kind, lab) in enumerate(labels):
        x = 175 + k * 290
        a = ease_out_back(prog(t, t0 + 0.1 + k * 0.25, t0 + 0.4 + k * 0.25))
        if a > 0.02:
            icon_card(cv, x, 950, kind, a, t)
    lay = lay.resize((OUT_W, OUT_H), Image.LANCZOS)
    img.paste(lay, (0, 0), lay)
    for k, (kind, lab) in enumerate(labels):
        pop_pill(img, t, t0 + 0.15 + k * 0.25, 175 + k * 290, 1210, lab, 38, bg="#fff6e6", depth=6)
    if t < t1:
        pop_pill(img, t, t0 + 0.05, 540, 360, "3 PAPAS", 100, bg="#ffd34d", rot=-3)
        pop_pill(img, t, wt("Drei Papas", "Nur", 0.0), 540, 530, "NUR 1 IST ECHT", 72, bg="#e2574c", fg="#ffffff", rot=2)
    else:
        pop_pill(img, t, t1, 540, 360, "WEM GLAUBST DU?", 84, bg="#ffd34d", rot=-3)
        pop_pill(img, t, wt("Wem glaubst", "Tür", 0.0), 540, 530, "TÜR · HANDY · TREPPE", 56, bg="#fff6e6", rot=2)
        tc = wt("Wem glaubst", "Schreib", 0.0)
        if t > tc:
            pop_pill(img, t, tc, 540, 1370, "SCHREIB'S IN DIE KOMMENTARE", 40, bg="#ffffff")
        tf = wt("Wem glaubst", "folg", 0.0)
        if t > tf:
            followed = t > tf + 1.2
            pill3d(img, 540, 690, "GEFOLGT  ✓" if followed else "+ FOLGEN FÜR TEIL 2", 54,
                   bg="#37b26c" if followed else "#e2574c", fg="#ffffff", scale=ease_out_back(prog(t, tf, tf + 0.3)))
    return img


SCENES = [(0.0, sc_intro), (st("Es klingelt") - 0.05, sc_bell), (st("Im selben") - 0.05, sc_phone),
          (st("Du schaust") - 0.05, sc_stare), (st("Dann zupft") - 0.05, sc_lina), (st("Du schreibst") - 0.05, sc_ask),
          (st("Durch die") - 0.05, sc_door), (st("Das stimmt") - 0.05, sc_both), (st("Plötzlich") - 0.05, sc_steps),
          (st("Das Licht") - 0.05, sc_dark), (st("Draußen klopft") - 0.05, sc_knock), (st("Da flüstert") - 0.05, sc_whisper),
          (st("Drei Papas") - 0.05, sc_three)]


def frame_at(t):
    _T[0] = t
    idx = max(i for i, (s0, _) in enumerate(SCENES) if t >= s0)
    img = SCENES[idx][1](t)
    if idx > 0:
        s0 = SCENES[idx][0]
        if t < s0 + XFADE:
            prev = SCENES[idx - 1][1](t)
            img = Image.blend(prev, img, smooth(prog(t, s0, s0 + XFADE)))
    if t > END - 0.5:
        img = Image.blend(img, Image.new("RGB", img.size, (8, 6, 16)), prog(t, END - 0.5, END))
    return img


def render_chunk(args):
    i0, i1, path = args
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame_at(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return path


def render(out="video.mp4", workers=4):
    bg()
    n = int(END * FPS)
    step = math.ceil(n / (workers * 3))
    chunks = [(i, min(n, i + step), os.path.join(CACHE, f"chunk{k:02d}.mp4")) for k, i in enumerate(range(0, n, step))]
    with Pool(workers) as pool:
        paths = pool.map(render_chunk, chunks, chunksize=1)
    lst = os.path.join(CACHE, "chunks.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in paths)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    os.path.join(CACHE, "silent.mp4")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(CACHE, "silent.mp4"),
                    "-i", os.path.join(HERE, "mix.wav"), "-c:v", "copy", "-af", "loudnorm=I=-14:LRA=11:TP=-1.5",
                    "-ar", "44100", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-shortest", os.path.join(HERE, out)], check=True)


if __name__ == "__main__":
    if "--stills" in sys.argv:
        os.makedirs(os.path.join(HERE, "stills"), exist_ok=True)
        for t in [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]]:
            frame_at(t).save(os.path.join(HERE, "stills", f"t{t:05.1f}.jpg"), quality=85)
    else:
        render()
