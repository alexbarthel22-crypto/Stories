"""Visuals: Alex ist heute ein Schmarotzer (TikTok Folge 6). Alltags-Humor: immer zahlen die anderen."""
import math, random
from alexlib import *

# Outfit: grüner Hoodie, graue Jogginghose – lässig, alles irgendwie geliehen
AL = alex(top="#4E9A6A", top_style="hoodie", pants="#5C5C66", shoes="#FFFFFF")
FEET, AH = 1690, 560
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
JANA = person_spec(31, girl=True, top="#F2B233", hair="#C98B4A", skin="#F1C9A8")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
MIA = person_spec(14, girl=True, top="#F07FB0", hair="#5A3A22", skin="#F1C9A8")
SVEN = person_spec(77, top="#3E7BDA", hair="#8A5A2B")


# ---------------------------------------------------------------- Intro: Haus
def _sign(c, x, y, txt, col, rot, size=40, w=330, post=70, hh=130):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.set_line_width(10); src(c, "#5A3E2A"); c.move_to(0, 40); c.line_to(0, 40 + post); c.stroke()
    rrect(c, -w / 2, -hh + 45, w, hh, 12); fill(c, col)
    rrect(c, -w / 2, -hh + 45, w, hh, 12); c.set_line_width(5); src(c, INK); c.stroke()
    text_block(c, txt, 0, 45 - hh / 2, size, w - 26, INK, FONT_HEAD)
    c.restore()




def intro_decor(c, t, u):
    s_ = clamp(u)
    # Fenster links: offener Kühlschrank (fremd), Licht flackert
    rrect(c, 294, 904, 112, 102, 6); src(c, "#E8F7FF", s_); c.fill()
    rrect(c, 312, 914, 76, 84, 6); fill(c, "#FFFFFF")
    rrect(c, 312, 914, 76, 84, 6); c.set_line_width(3); src(c, INK); c.stroke()
    emoji(c, "🍕", 350, 945, 44 * s_)
    rrect(c, 316, 974, 68, 18, 4); fill(c, "#FFE14D")
    text(c, "GRATIS", 350, 983, 12, INK, FONT_HEAD)
    # Fenster rechts: fremdes WLAN mit Signal-Wellen
    rrect(c, 670, 900, 120, 110, 8); src(c, "#FFF4D6", s_); c.fill()
    for i in range(3):
        k = ((t * 1.5 + i / 3) % 1)
        c.arc(730, 990, 20 + 50 * k, math.pi * 1.25, math.pi * 1.75); c.set_line_width(6); src(c, "#3E7BDA", (1 - k) * s_); c.stroke()
    text(c, "NACHBAR", 730, 920, 16, INK, FONT_HEAD)
    # Türschild
    def door_sign():
        rrect(c, 465, 1100, 150, 56, 10); fill(c, "#FFFFFF")
        rrect(c, 465, 1100, 150, 56, 10); c.set_line_width(3); src(c, INK); c.stroke()
        text(c, "GIBT'S", 540, 1118, 18, INK, FONT_HEAD)
        text(c, "WAS ZU ESSEN?", 540, 1140, 14, INK, FONT_HEAD)
    scaled(c, 540, 1128, s_, door_sign)
    # Neon "GRATIS"
    def neon():
        glow = 0.7 + 0.3 * (1 if int(t * 3) % 4 else 0.2)
        rrect(c, 232, 1070, 196, 80, 18); src(c, "#1C1C22", 0.92); c.fill()
        rrect(c, 232, 1070, 196, 80, 18); c.set_line_width(5); src(c, "#FFB13B", glow); c.stroke()
        text(c, "GRATIS?", 330, 1094, 30, "#FFD28A", FONT_HEAD, alpha=glow)
        text(c, "🆓 IMMER", 330, 1128, 24, "#FFD28A", FONT_HEAD, alpha=glow)
    scaled(c, 330, 1110, s_, neon)
    _sign(c, 230, 1640, "Zahlst du? 💸", "#FFFFFF", -0.1, 54, 420, 60, 170)
    _sign(c, 850, 1640, "Ich zahl's morgen 🤞", "#FFE1B8", 0.08, 50, 420, 60, 170)
    for i in range(5):
        u2 = (t * 0.35 + i / 5) % 1
        emoji(c, "💸" if i % 2 else "🍕", 120 + i * 210, 1250 - u2 * 160, 46, alpha=0.8 * (1 - u2))


def alex_extras(c, x, feet, h, t, u):
    """Leere Hosentasche rausgezogen, Tupperdose in der Hand."""
    k = h / 100.0
    c.save(); c.translate(x - 14 * k, feet - 40 * k); c.rotate(0.15)
    rrect(c, -4 * k, 0, 8 * k, 9 * k, 2 * k); fill(c, "#FFFFFF")
    rrect(c, -4 * k, 0, 8 * k, 9 * k, 2 * k); c.set_line_width(0.5 * k); src(c, INK); c.stroke()
    c.restore()
    emoji(c, "🦋", x - 22 * k + math.sin(t * 3) * 3 * k, feet - 30 * k - (t * 6 % 10) * k * 0.6, 7 * k, alpha=0.9)
    emoji(c, "🥡", x + 36 * k, feet - 30 * k, 13 * k, rot=0.1)


INTRO = dict(icon="🥡", bg="#D9762B", spec=AL, expr="smug", pose="hips", hand_prop=None,
             house=dict(sky=("#F29A4A", "#FFE1B8"), walls="#FFF1DE", roof="#8A4A1E", door="#5A2E0E", lawn="#5DAA5E",
                        accent=("#E07A2E", "#2FA36B"), sun=True),
             umbrella=False, title_lines=["SCHMAROTZER."], fill="#6FB7E8", decor=intro_decor,
             alex_extras=alex_extras, burst=["💸", "🍕", "🥡", "🍺", "🎂", "🔑", "🥩", "🤞"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_house(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


# ---------------------------------------------------------------- Helfer
def alex_bottom(c, S, expr="smug", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Alex")


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#D9762B")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def tag(c, x, y, txt, col="#E23B3B", s=1.0):
    def d():
        w = text_width(c, txt, 30, FONT_HEAD) + 36
        rrect(c, x - w / 2, y - 26, w, 52, 14); fill(c, col)
        text(c, txt, x, y, 30, "#FFFFFF", FONT_HEAD)
    scaled(c, x, y, s, d)


def chat_msg(c, who, msg, x0, w, y, s, col):
    if s <= 0:
        return 0
    lines = wrap(c, msg, 28, w - 150, FONT_BOLD)
    bw = max(text_width(c, ln, 28, FONT_BOLD) for ln in lines) + 44
    bh = len(lines) * 35 + 62
    def d():
        rrect(c, x0 + 24, y, bw, bh, 22); fill(c, "#E6E6EA")
        text(c, who, x0 + 46, y + 24, 22, col, FONT_HEAD, anchor="l")
        for i, ln in enumerate(lines):
            text(c, ln, x0 + 46, y + 56 + i * 35, 28, INK, FONT_BOLD, anchor="l")
    scaled(c, x0 + 24, y, s, d)
    return bh


def box_fx(c, t, t0, x, y, w, h, kind="anger"):
    """Effekte um eine Szenen-Box: anger (rot pulsierend, 💢, Dampf), love (Herzen), shock (Blitze), party (Konfetti)."""
    if t < t0:
        return
    u = t - t0
    a = clamp(u / 0.25)
    if kind == "anger":
        pulse = 0.5 + 0.5 * math.sin(u * 12)
        for i in range(3):
            rrect(c, x - w / 2 - 10 - i * 9, y - h / 2 - 10 - i * 9, w + 20 + i * 18, h + 20 + i * 18, 30 + i * 9)
            c.set_line_width(7); src(c, "#FF3B3B", a * (0.55 - 0.15 * i) * (0.6 + 0.4 * pulse)); c.stroke()
        for (dx, dy) in ((-0.48, -0.48), (0.48, -0.5), (0.5, 0.45)):
            emoji(c, "💢", x + dx * w, y + dy * h, 70 * a * (1 + 0.15 * pulse))
        for i in range(2):
            uu = (u * 0.9 + i * 0.5) % 1
            emoji(c, "💨", x + w * 0.42, y - h * 0.5 - uu * 90, 60, rot=-0.4, alpha=a * (1 - uu))
            emoji(c, "💨", x - w * 0.42, y - h * 0.5 - uu * 90, 60, rot=0.4, alpha=a * (1 - uu))
    elif kind == "love":
        for i in range(8):
            ang = i / 8 * 2 * math.pi + u * 0.8
            rr = 1 + 0.06 * math.sin(u * 6 + i)
            emoji(c, "💘" if i % 2 else "💕", x + math.cos(ang) * w * 0.55 * rr, y + math.sin(ang) * h * 0.6 * rr, 54 * a)
    elif kind == "shock":
        for i in range(10):
            ang = i / 10 * 2 * math.pi
            r0 = max(w, h) * 0.5 + 20; r1 = r0 + 40 + 20 * math.sin(u * 20 + i)
            c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND); src(c, "#FFE14D", a)
            c.move_to(x + math.cos(ang) * r0 * w / max(w, h), y + math.sin(ang) * r0 * h / max(w, h))
            c.line_to(x + math.cos(ang) * r1 * w / max(w, h), y + math.sin(ang) * r1 * h / max(w, h)); c.stroke()
        emoji(c, "😱", x + w * 0.45, y - h * 0.5, 70 * a)
    elif kind == "party":
        rnd = random.Random(9)
        for i in range(18):
            px = x + rnd.uniform(-0.55, 0.55) * w
            py = y - h * 0.55 + ((u * rnd.uniform(120, 220) + rnd.uniform(0, h)) % (h * 1.1))
            c.save(); c.translate(px, py); c.rotate(u * 3 + i)
            rrect(c, -7, -12, 14, 24, 3); src(c, rnd.choice(["#F7C948", "#FF5CA8", "#36B5C2", "#2FA36B"]), a); c.fill()
            c.restore()


def status_dot(c, x, y, r, col="#2FD16B", t=0.0, pulse=True):
    if pulse:
        g = 0.5 + 0.5 * math.sin(t * 5)
        c.arc(x, y, r * (1.3 + 0.25 * g), 0, 2 * math.pi); src(c, col, 0.25); c.fill()
    c.arc(x, y, r, 0, 2 * math.pi); fill(c, col)
    c.arc(x, y, r, 0, 2 * math.pi); c.set_line_width(max(2, r * 0.18)); src(c, "#FFFFFF"); c.stroke()


def clock_face(c, x, y, r, hours, minutes):
    c.arc(x, y, r, 0, 2 * math.pi); fill(c, "#FFFFFF")
    c.arc(x, y, r, 0, 2 * math.pi); c.set_line_width(r * 0.08); src(c, INK); c.stroke()
    for i in range(12):
        a = i / 12 * 2 * math.pi
        c.move_to(x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82); c.line_to(x + math.sin(a) * r * 0.92, y - math.cos(a) * r * 0.92)
    c.set_line_width(r * 0.05); c.stroke()
    ah = (hours % 12 + minutes / 60) / 12 * 2 * math.pi; am = minutes / 60 * 2 * math.pi
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x, y); c.line_to(x + math.sin(ah) * r * 0.5, y - math.cos(ah) * r * 0.5); c.set_line_width(r * 0.1); c.stroke()
    c.move_to(x, y); c.line_to(x + math.sin(am) * r * 0.75, y - math.cos(am) * r * 0.75); c.set_line_width(r * 0.06); c.stroke()
    c.arc(x, y, r * 0.07, 0, 2 * math.pi); c.fill()


# ---------------------------------------------------------------- Szenen
def box_move(c, cx, cy, t, kind, t0=0.0):
    """Bewegung der großen Box (vorher c.save(), danach c.restore()).
    wobble: sanftes Wackeln · rumble: Bahn-Vibration · bounce: Party-Beat · shake: hartes Rütteln ab t0 · chomp: Puls"""
    dx = dy = rot = 0.0; sc = 1.0
    if kind == "wobble":
        rot = 0.018 * math.sin(t * 3.2); sc = 1 + 0.012 * math.sin(t * 2.1)
    elif kind == "rumble":
        dx = 3 * math.sin(t * 37); dy = 4 * math.sin(t * 23) * abs(math.sin(t * 1.7))
    elif kind == "bounce":
        b = abs(math.sin(t * math.pi * 2.0)); sc = 1 + 0.025 * b; rot = 0.02 * math.sin(t * math.pi)
    elif kind == "chomp":
        sc = 1 + 0.03 * max(0, math.sin(t * 9)); rot = 0.012 * math.sin(t * 4.5)
    elif kind == "flicker":
        dx = (4 if int(t * 14) % 7 == 0 else 0)
    if kind == "shake" or (t0 and t > t0):
        u = t - t0
        if 0 <= u < 0.6:
            amp = 14 * (1 - u / 0.6); dx += amp * math.sin(u * 70); rot += 0.025 * (1 - u / 0.6) * math.sin(u * 55)
    c.translate(cx + dx, cy + dy); c.rotate(rot); c.scale(sc, sc); c.translate(-cx, -cy)


def box_flash(c, x, y, w, h, t, t0, col="#FFFFFF", d=0.35):
    """Kurzes Aufblitzen über der Box."""
    if t0 <= t < t0 + d:
        a = 0.75 * (1 - (t - t0) / d)
        rrect(c, x - w / 2, y - h / 2, w, h, 30); src(c, col, a); c.fill()


def money_rain(c, t, t0, x, y, w, n=10):
    if t < t0:
        return
    for i in range(n):
        rr = random.Random(90 + i)
        uu = ((t - t0) * rr.uniform(0.4, 0.7) + rr.random()) % 1
        emoji(c, "💸", x + rr.uniform(-w / 2, w / 2) + math.sin(uu * 7 + i) * 20, y - 60 + uu * 300, 48, rot=uu * 3, alpha=1 - uu)


def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def card_():
        card(c, W / 2, 720, 980, 660, 1)
        text(c, "WER HAT BEZAHLT?", W / 2, 445, 46, INK, FONT_HEAD)
        k = clamp((t - S.at(0, 0.3)) / 1.6)
        rows = [("ALEX", 0.0, "#E23B3B"), ("FREUNDE", 1.0, "#2FA36B")]
        for i, (nm, f, col) in enumerate(rows):
            y = 540 + i * 120
            text(c, nm, 140, y + 40, 40, INK, FONT_HEAD, anchor="l")
            rrect(c, 380, y, 560, 80, 14); fill(c, "#EEF0F4")
            if f > 0:
                rrect(c, 380, y, max(1, 560 * f * k), 80, 14); fill(c, col)
            val = f"{int(237 * f * k)} €" if f > 0 else "0,00 €"
            text(c, val, 660, y + 40, 42, INK if f == 0 else "#FFFFFF", FONT_HEAD)
        if t > a1:
            def wal():
                for i, (ic, lab, col) in enumerate((("💳", "Karte: vergessen", "#E23B3B"),
                                                    ("📱", "Handy-Pay: geht „nie“", "#D9762B"))):
                    yy = 870 + i * 82
                    pl = 1 + 0.04 * math.sin(t * 6 + i * 1.5)
                    def pill_(yy=yy, ic=ic, lab=lab, col=col, i=i):
                        rrect(c, 120, yy - 34, 840, 68, 34); fill(c, col)
                        rrect(c, 120, yy - 34, 840, 68, 34); c.set_line_width(4); src(c, INK); c.stroke()
                        emoji(c, ic, 175, yy, 52, rot=math.sin(t * 4 + i) * 0.2)
                        text(c, lab, 225, yy, 40, "#FFFFFF", FONT_HEAD, anchor="l")
                    scaled(c, W / 2, yy, pl, pill_)
            scaled(c, W / 2, 910, pop(t, a1 + 0.1), wal)
    c.save(); box_move(c, W / 2, 700, t, "wobble", a1)
    scaled(c, W / 2, 700, s, card_)
    box_flash(c, W / 2, 700, 980, 620, t, a1, "#FFE14D")
    c.restore()
    money_rain(c, t, S.at(0, 0.6), 760, 600, 340, 6)
    alex_bottom(c, S, "smug", "hips")


def sc_motto(c, S):
    t = S.t
    d0 = S.at(0, 0.0)
    s = pop(t, d0)
    span = max(1.2, S.S.durs[0] * 0.8)
    gone = int(7 * clamp((t - d0 - 0.4) / span))
    def pizza():
        card(c, W / 2, 700, 960, 640, 1)
        # Quittung oben: wer hat bezahlt
        rrect(c, 140, 405, 800, 70, 14); fill(c, "#2FA36B")
        text(c, "🧾 BEZAHLT: TOM & MIA – 24 €", W / 2, 440, 38, "#FFFFFF", FONT_HEAD)
        cx, cy, r = W / 2, 690, 190
        c.arc(cx, cy + 12, r + 18, 0, 2 * math.pi); fill(c, "#E0E0E6")
        for i in range(8):
            a0 = i / 8 * 2 * math.pi - math.pi / 2
            uu = clamp((t - d0 - 0.4 - span * i / 7) / 0.5) if i < gone + 1 and i < 7 else 0
            if i < gone:
                uu = max(uu, 1.0)
            dy = 560 * ease_in_out(uu)                            # Stück fliegt runter zu Alex
            if uu >= 1:
                continue
            c.save(); c.translate(0, dy)
            c.move_to(cx, cy); c.arc(cx, cy, r, a0, a0 + 2 * math.pi / 8); c.close_path()
            fill(c, "#F2B233"); c.move_to(cx, cy); c.arc(cx, cy, r, a0, a0 + 2 * math.pi / 8); c.close_path()
            c.set_line_width(5); src(c, "#C9852E"); c.stroke()
            am = a0 + math.pi / 8
            for rr in (0.45, 0.75):
                c.arc(cx + math.cos(am) * r * rr, cy + math.sin(am) * r * rr, 16, 0, 2 * math.pi); fill(c, "#C0392B")
            c.restore()
        # Tom & Mia links/rechts mit Zählern
        for x, sp, nm in ((215, TOM, "Tom"), (865, MIA, "Mia")):
            person(c, x, 990, 300, sp, t, "angry" if gone >= 4 else "neutral", bob=False, name=nm, blink_seed=x)
        tag(c, 215, 560, "zahlt 12 € 💸", "#555A66", s=1)
        tag(c, 865, 560, "zahlt 12 € 💸", "#555A66", s=1)
        tag(c, cx, 935, f"ALEX ISST: {gone}/8 🍕 · ZAHLT: 0 €", "#E23B3B", s=1)
    c.save(); box_move(c, W / 2, 700, t, "chomp" if gone else "wobble", d0 + 0.4 + span * 4 / 7)
    scaled(c, W / 2, 700, s, pizza)
    c.restore()
    if gone >= 4:
        box_fx(c, t, d0 + 0.4 + span * 4 / 7, W / 2, 700, 960, 640, "anger")
    alex_bottom(c, S, "happy", "hips", "🍕" if gone else None)
    if t > d0 + 0.6:
        bubble(c, "Danke fürs Teilen! 😋", 830, 1190, pop(t, d0 + 0.6), tail=(-0.5, 1), size=38, max_w=320)


def sc_hotspot(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def bahn():
        rrect(c, 70, 390, 940, 640, 30); fill(c, "#DDEFF3")
        rrect(c, 70, 390, 940, 640, 30); c.set_line_width(6); src(c, INK); c.stroke()
        # Bahnfenster mit vorbeiziehender Landschaft
        for i in range(3):
            x = 120 + i * 300
            rrect(c, x, 420, 240, 120, 16); fill(c, "#9FD8F0")
            for k in range(3):
                tx = x + ((k * 110 - t * 260) % 300) - 30
                if x < tx < x + 230:
                    emoji(c, "🌳", tx, 500, 46)
            rrect(c, x, 420, 240, 120, 16); c.set_line_width(5); src(c, INK); c.stroke()
        text(c, "🚆 S-BAHN", 540, 575, 30, "#2B5C66", FONT_HEAD)
    t_leer = a1 + 0.3 + max(1.0, S.S.durs[1] * 0.6)
    c.save(); box_move(c, W / 2, 710, t, "rumble", t_leer)
    scaled(c, W / 2, 710, s, bahn)
    # Alex' Handy (links)
    x0, y0, w, h = phone(c, 300, 790, 300, 440, pop(t, S.at(0, 0.2)), screen="#FFFFFF" if t < a1 else "#111114",
                         rot=-0.05)
    if t < a1:
        text(c, "Datenvolumen", 300, y0 + 90, 30, INK, FONT_HEAD)
        k = clamp((t - S.at(0, 0.4)) / 1.0)
        rrect(c, x0 + 25, y0 + 125, w - 50, 40, 12); fill(c, "#EEF0F4")
        rrect(c, x0 + 25, y0 + 125, max(2, (w - 50) * 0.3 * (1 - k)), 40, 12); fill(c, "#E23B3B")
        text(c, "0 MB 🪫" if k >= 1 else f"{int(300 * (1 - k))} MB", 300, y0 + 215, 46, "#E23B3B", FONT_HEAD)
        text(c, "WIE IMMER", 300, y0 + 285, 30, "#555A66", FONT_HEAD, alpha=k)
    else:
        text(c, "📶 Janas iPhone ✅", 300, y0 + 60, 24, "#2FD16B", FONT_HEAD)
        text(c, "TikTok · HD", 300, y0 + 110, 32, "#FFFFFF", FONT_HEAD)
        for i in range(5):
            uu = (t * 0.8 + i / 5) % 1
            emoji(c, "❤️", x0 + w - 40, y0 + h - 40 - uu * 200, 30, alpha=1 - uu)
        emoji(c, "🕺", 290, y0 + 220 + math.sin(t * 8) * 10, 90, rot=math.sin(t * 6) * 0.2)
    # Jana (rechts) mit ihrem Handy
    jana_expr = "angry" if t > a1 + S.S.durs[1] * 0.6 else "neutral"
    person(c, 770, 1030, 420, JANA, t, jana_expr, bob=False, name="Jana", blink_seed=7)
    if t > a1:
        k = clamp((t - a1 - 0.3) / max(1.0, S.S.durs[1] * 0.6))
        def jp():
            rrect(c, 640, 425, 260, 150, 18); fill(c, "#FFFFFF")
            rrect(c, 640, 425, 260, 150, 18); c.set_line_width(4); src(c, INK); c.stroke()
            text(c, "Janas Datenvolumen", 770, 455, 22, INK, FONT_HEAD)
            rrect(c, 660, 480, 220, 30, 10); fill(c, "#EEF0F4")
            rrect(c, 660, 480, max(2, 220 * (1 - k)), 30, 10); fill(c, "#2FD16B" if k < 0.7 else "#E23B3B")
            text(c, f"{10 * (1 - k):.1f} GB" if k < 1 else "0 GB – LEER 😭", 770, 545, 30,
                 "#E23B3B" if k > 0.7 else INK, FONT_HEAD)
        scaled(c, 770, 500, pop(t, a1 + 0.1), jp, rot=0.04)
        # Daten fließen von Jana zu Alex
        for i in range(6):
            uu = (t * 1.2 + i / 6) % 1
            emoji(c, "📶", 640 - uu * 250, 700 + math.sin(uu * 6) * 30, 40, alpha=(1 - uu) * (1 - k * 0.5))
        if k >= 1:
            box_flash(c, W / 2, 710, 940, 640, t, t_leer, "#FF3B3B")
    c.restore()
    if t > a1 and t > t_leer:
        box_fx(c, t, t_leer, W / 2, 710, 940, 640, "anger")
    alex_bottom(c, S, "smug" if t > a1 else "neutral", "idle")


def sc_stream(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def tv():
        rrect(c, 80, 390, 920, 560, 26); fill(c, "#141418")
        rrect(c, 80, 390, 920, 560, 26); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 470, 950, 140, 50, 6); fill(c, "#333333")
        if t < a1:
            text(c, "Wer schaut gerade?", W / 2, 460, 46, "#FFFFFF", FONT_HEAD)
            profs = [("Jana", "#E5534B", "🙂"), ("Jana 2", "#3E7BDA", "😊"), ("Alex 😎", "#2FA36B", "🍿")]
            for i, (nm, col, e) in enumerate(profs):
                x = 260 + i * 280
                hl = 1 + (0.08 * math.sin(t * 6) if i == 2 else 0)
                def pf(x=x, col=col, e=e, nm=nm, i=i):
                    rrect(c, x - 100, 520, 200, 200, 20); fill(c, col)
                    emoji(c, e, x, 620, 100)
                    if i == 2:
                        rrect(c, x - 100, 520, 200, 200, 20); c.set_line_width(8); src(c, "#FFFFFF"); c.stroke()
                    text(c, nm, x, 760, 34, "#FFFFFF", FONT_HEAD)
                scaled(c, x, 620, hl, pf)
            tag(c, 820, 840, "SEIT 3 JAHREN 📅", "#E23B3B", s=pop(t, S.at(0, 0.6)))
        else:
            text(c, "Passwort geändert", 300, 470, 40, "#FFFFFF", FONT_HEAD)
            text(c, "Erraten", 780, 470, 40, "#FFFFFF", FONT_HEAD)
            k = clamp((t - a1 - 0.2) / max(0.8, S.S.durs[1] * 0.8))
            n = min(5, int(5 * k) + 1)
            for i in range(5):
                on = i < n
                emoji(c, "🔒" if on else "▫️", 140 + i * 80, 560, 60, alpha=1 if on else 0.3)
                emoji(c, "🔓" if on else "▫️", 620 + i * 80, 560, 60, alpha=1 if on else 0.3,
                      rot=(math.sin(t * 12) * 0.2 if on and i == n - 1 else 0))
            text(c, f"{n}×", 300, 680, 110, "#E5534B", FONT_HEAD)
            text(c, f"{n}×", 780, 680, 110, "#2FD16B", FONT_HEAD)
            pw = ["jana123", "Jana1234!", "JanaNeu99", "N1ch7Al3x", "AlexRaus!!"][n - 1]
            rrect(c, 260, 800, 560, 90, 16); fill(c, "#2A2A33")
            text(c, "🔑 " + pw, W / 2, 845, 42, "#FFE14D", FONT_HEAD)
    kk = clamp((t - a1 - 0.2) / max(0.8, S.S.durs[1] * 0.8)) if t > a1 else -1
    t_pw = a1 + 0.2 + (min(4, int(5 * kk)) / 5) * max(0.8, S.S.durs[1] * 0.8) if t > a1 else 0
    c.save(); box_move(c, W / 2, 680, t, "flicker", t_pw)
    scaled(c, W / 2, 680, s, tv)
    if t > a1:
        box_flash(c, W / 2, 680, 920, 560, t, t_pw, "#FFE14D", 0.25)
    c.restore()
    if t < a1:
        for i in range(4):
            rr = random.Random(i); uu = (t * 0.5 + rr.random()) % 1
            emoji(c, "🍿", 160 + rr.uniform(0, 760), 1050 - uu * 80, 44, alpha=1 - uu)
    alex_bottom(c, S, "happy" if t < a1 else "smug", "idle", "🍿" if t < a1 else None)


def sc_food(c, S):
    t, a1, a2 = S.t, S.at(1), S.at(2)
    s = pop(t, S.at(0, 0.0))
    def table():
        rrect(c, 70, 390, 940, 640, 30); fill(c, "#FFF4E0")
        rrect(c, 70, 390, 940, 640, 30); c.set_line_width(6); src(c, INK); c.stroke()
        # Freunde hinten
        for i, (sp, nm) in enumerate(((LENA, "Lena"), (TOM, "Tom"), (MIA, "Mia"))):
            person(c, 230 + i * 310, 980, 420, sp, t, "angry" if t > a2 + 0.4 else "neutral", bob=False, name=nm, blink_seed=i)
        rrect(c, 90, 790, 900, 220, 20); fill(c, "#B07A4F")
        rrect(c, 90, 790, 900, 220, 20); c.set_line_width(5); src(c, INK); c.stroke()
        if t > a1:                                            # die anderen: Salat + Wasser
            for i in range(3):
                emoji(c, "🥗", 200 + i * 310, 850, 60); emoji(c, "🚰", 280 + i * 310, 850, 44)
        if t > a2:
            def bill():
                rrect(c, 300, 430, 480, 300, 16); fill(c, "#FFFFFF")
                rrect(c, 300, 430, 480, 300, 16); c.set_line_width(5); src(c, INK); c.stroke()
                text(c, "RECHNUNG 🧾", W / 2, 475, 40, INK, FONT_HEAD)
                text(c, "Alex: 148,90 €", W / 2, 540, 36, "#C0392B", FONT_HEAD)
                text(c, "Rest: 3 × 9,50 €", W / 2, 590, 32, "#555A66", FONT_BOLD)
                c.move_to(330, 625); c.line_to(750, 625); c.set_line_width(3); src(c, INK); c.stroke()
                text(c, "÷ 4 = je 44,35 € 😇", W / 2, 675, 40, "#2E7D4F", FONT_HEAD)
            scaled(c, W / 2, 580, pop(t, a2 + 0.2), bill, rot=math.sin(t * 2) * 0.02)
    c.save(); box_move(c, W / 2, 710, t, "wobble", a2 + 0.2)
    scaled(c, W / 2, 710, s, table)
    box_flash(c, W / 2, 710, 940, 640, t, a2 + 0.2, "#FFFFFF")
    c.restore()
    # Alex' Bestellung wächst auf dem Tisch (vorne)
    items = [("🥩", 0.15), ("🍤", 0.35), ("🍹", 0.55), ("🍹", 0.7), ("🍹", 0.85)]
    for i, (e, f) in enumerate(items):
        if t > S.at(0, f):
            emoji(c, e, 230 + i * 150, 950 + math.sin(t * 4 + i) * 6, 80 * pop(t, S.at(0, f)))
    if t > a2 + 0.4:
        box_fx(c, t, a2 + 0.4, W / 2, 710, 940, 640, "anger")
    alex_bottom(c, S, "smug" if t > a2 else "happy", "idle")


def sc_party(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def room():
        rrect(c, 70, 390, 940, 640, 30); fill(c, "#F3EAFE")
        rrect(c, 70, 390, 940, 640, 30); c.set_line_width(6); src(c, INK); c.stroke()
        for i in range(12):                                   # Wimpelkette
            x = 100 + i * 75
            c.move_to(x, 420); c.line_to(x + 37, 470); c.line_to(x + 75, 420); c.close_path()
            src(c, ["#E5534B", "#F2B233", "#2FA36B", "#3E7BDA"][i % 4]); c.fill()
        text(c, "HAPPY BIRTHDAY, SVEN! 🎉", W / 2, 520, 44, "#7A3FA8", FONT_HEAD)
        for i, x in enumerate((140, 940)):
            emoji(c, "🎈", x, 640 + math.sin(t * 2 + i) * 15, 90)
        person(c, 300, 960, 360, SVEN, t, "happy", "wave", bob=False, name="Sven", blink_seed=4)
        rrect(c, 470, 800, 480, 200, 16); fill(c, "#FFFFFF")
        rrect(c, 470, 800, 480, 200, 16); c.set_line_width(5); src(c, INK); c.stroke()
        text(c, "BUFFET", 710, 830, 30, INK, FONT_HEAD)
        k = clamp((t - a1 - 0.2) / 1.5) if t > a1 else 0
        food = ["🍗", "🥗", "🍝", "🎂", "🥨", "🍰"]
        for i, e in enumerate(food):
            if i < int(6 * (1 - k) + 0.999):
                emoji(c, e, 530 + i * 75, 920, 60)
    c.save(); box_move(c, W / 2, 710, t, "bounce", a1 + 0.3)
    scaled(c, W / 2, 710, s, room)
    box_flash(c, W / 2, 710, 940, 640, t, a1 + 0.3, "#FFE14D")
    c.restore()
    if t > S.at(0, 0.4):
        tag(c, 300, 1060, "WER IST SVEN? 🤷", "#7A3FA8", s=pop(t, S.at(0, 0.4)))
    box_fx(c, t, 0.2, W / 2, 710, 940, 640, "party")
    alex_bottom(c, S, "happy", "idle")
    if t > a1:                                                # Tupperdosen stapeln sich
        for i in range(3):
            ti = a1 + 0.3 + i * 0.35
            if t > ti:
                def box(i=i):
                    y = 1390 - i * 70
                    rrect(c, 700, y, 190, 66, 12); src(c, "#BDE7FF", 0.9); c.fill()
                    rrect(c, 700, y, 190, 66, 12); c.set_line_width(4); src(c, INK); c.stroke()
                    rrect(c, 694, y - 10, 202, 18, 8); fill(c, "#3E7BDA")
                    emoji(c, ["🍗", "🍝", "🍰"][i], 795, y + 36, 40)
                scaled(c, 795, 1420 - i * 70, pop(t, ti), box)
        tag(c, 795, 1150, "3 DOSEN 🥡", "#E23B3B", s=pop(t, a1 + 1.4))


def sc_signs(c, S):
    t = S.t
    items = [("Nie Karte & Handy-Pay dabei", "💳"), ("„Ich geb's dir morgen wieder“", "🤞"),
             ("Zum Essen da – isst alles weg", "🍽️"), ("Tupperdosen im Rucksack", "🥡")]
    for i, (lab, ic) in enumerate(items):
        y = 400 + i * 175
        row_card(c, W / 2, y, 1000, 160, pop(t, S.at(i + 1, 0.0)), lab, ic, 40, num=i + 1, rot=(-0.02 if i % 2 else 0.02) + 0.012 * math.sin(t * 3 + i))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1150 + math.sin(t * 3 + i) * 12, 90 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    alex_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du auch einen Schmarotzer?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 1000, 220, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 52, 940, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tg():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#D9762B", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@schnorrer"
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tg, rot=math.sin(t * 4) * 0.02)
    if t >= a1:
        colors = ["#EC7FAE", "#3E5C9A", "#4A2E6B", "#5E8C3A", "#2F6FA8", "#D9762B", "#36B5C2", "#F07F4F", "#555A66"]
        prev = [("🌹", "FOLGE 1"), ("🥺", "FOLGE 2"), ("🌀", "FOLGE 3"), ("🏘️", "FOLGE 4"), ("⏰", "FOLGE 5"), ("🥡", "HEUTE ✅")]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 250 + cc * 290, 445 + r * 192
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 88, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 88, 0, 2 * math.pi); c.set_line_width(7); src(c, "#FFFFFF"); c.stroke()
                if i < len(prev):
                    e, lab = prev[i]
                    emoji(c, e, x, y, 90)
                    rrect(c, x - 88, y + 58, 176, 48, 12); fill(c, "#2FA36B" if i == len(prev) - 1 else "#555A66")
                    text(c, lab, x, y + 82, 30, "#FFFFFF", FONT_HEAD)
                else:
                    text(c, "?", x, y, 100, "#FFFFFF", FONT_HEAD)
            scaled(c, x, y, pop(t, a1 + 0.1 + i * 0.07), icon)
        ps = pop(t, S.at(1, 0.45))
        def pill():
            rrect(c, 40, 950, 1000, 126, 63); fill(c, "#E23B3B")
            rrect(c, 40, 950, 1000, 126, 63); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1013, 52, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1013, ps * (1 + 0.05 * math.sin(t * 7)), pill)
    alex_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=sc_what, motto=sc_motto, hotspot=sc_hotspot, stream=sc_stream, food=sc_food, party=sc_party,
                  signs=sc_signs, outro=sc_outro)
