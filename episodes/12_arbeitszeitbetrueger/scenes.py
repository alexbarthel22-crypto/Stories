"""Visuals: Alex ist heute ein Arbeitszeit-Betrüger (TikTok Folge 5). Büro-/Homeoffice-Humor."""
import math, random
from alexlib import *

# Outfit: Büro-Casual – grauer Hoodie, dunkle Chino, Firmenausweis am Band
AL = alex(top="#6B7A90", top_style="hoodie", pants="#2B2F3A", shoes="#FFFFFF")
FEET, AH = 1690, 560
CHEF = person_spec(56, hair="#6B6B6B", top="#2B2F3A", top_style="suit", skin="#E9B48A")
JANA = person_spec(31, girl=True, top="#F2B233", hair="#C98B4A", skin="#F1C9A8")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")


# ---------------------------------------------------------------- Intro: Homeoffice-Haus
def _sign(c, x, y, txt, col, rot, size=40, w=330, post=70):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.set_line_width(10); src(c, "#5A3E2A"); c.move_to(0, 40); c.line_to(0, 40 + post); c.stroke()
    hh = 130
    rrect(c, -w / 2, -hh + 45, w, hh, 12); fill(c, col)
    rrect(c, -w / 2, -hh + 45, w, hh, 12); c.set_line_width(5); src(c, INK); c.stroke()
    text_block(c, txt, 0, 45 - hh / 2, size, w - 26, INK, FONT_HEAD)
    c.restore()



def intro_decor(c, t, u):
    s_ = clamp(u)
    # Fenster links: Laptop leuchtet, Status grün, keiner da (💤)
    rrect(c, 294, 904, 112, 102, 6); src(c, "#7FD0FF", (0.55 + 0.2 * math.sin(t * 2)) * s_); c.fill()
    rrect(c, 312, 930, 76, 48, 4); fill(c, "#1C1C22")
    c.arc(372, 942, 8, 0, 2 * math.pi); src(c, "#2FD16B", s_); c.fill()
    emoji(c, "💤", 350, 885, 40 * s_)
    # Fenster rechts: Uhr dreht sich viel zu schnell
    rrect(c, 670, 900, 120, 110, 8); src(c, "#FFF4D6", s_); c.fill()
    cx, cy = 730, 955
    c.arc(cx, cy, 40, 0, 2 * math.pi); fill(c, "#FFFFFF")
    c.arc(cx, cy, 40, 0, 2 * math.pi); c.set_line_width(4); src(c, INK); c.stroke()
    for ang, ln, lw in ((t * 6, 30, 4), (t * 0.6, 20, 6)):
        c.move_to(cx, cy); c.line_to(cx + math.sin(ang) * ln, cy - math.cos(ang) * ln)
        c.set_line_width(lw); src(c, INK); c.stroke()
    # Türschild "Bin im Meeting"
    def door_sign():
        rrect(c, 470, 1100, 140, 56, 10); fill(c, "#FFFFFF")
        rrect(c, 470, 1100, 140, 56, 10); c.set_line_width(3); src(c, INK); c.stroke()
        text(c, "BIN IM", 540, 1118, 18, INK, FONT_HEAD)
        text(c, "MEETING 🎧", 540, 1140, 16, INK, FONT_HEAD)
    scaled(c, 540, 1128, s_, door_sign)
    # Neon "ONLINE 🟢"
    def neon():
        glow = 0.7 + 0.3 * (1 if int(t * 3) % 4 else 0.2)
        rrect(c, 232, 1070, 196, 80, 18); src(c, "#1C1C22", 0.92); c.fill()
        rrect(c, 232, 1070, 196, 80, 18); c.set_line_width(5); src(c, "#2FD16B", glow); c.stroke()
        text(c, "ONLINE", 330, 1094, 30, "#9FFFC0", FONT_HEAD, alpha=glow)
        text(c, "🟢 24/7", 330, 1128, 26, "#9FFFC0", FONT_HEAD, alpha=glow)
    scaled(c, 330, 1110, s_, neon)
    # Schilder vorne
    _sign(c, 200, 1650, "Kamera aus 📷", "#FFFFFF", -0.1, 42, 340)
    _sign(c, 880, 1650, "Status: grün 🟢", "#B8F0C8", 0.08, 42, 340)
    # fliegende Uhren / Zzz
    for i in range(5):
        u2 = (t * 0.35 + i / 5) % 1
        emoji(c, "⏰" if i % 2 else "💤", 120 + i * 210, 1250 - u2 * 160, 46, alpha=0.8 * (1 - u2))


def alex_extras(c, x, feet, h, t, u):
    """Firmenausweis am Band, Kaffeetasse, müde Zzz."""
    k = h / 100.0
    c.set_line_width(1.1 * k); src(c, "#E23B3B")
    c.move_to(x - 6 * k, feet - 60 * k); c.line_to(x, feet - 44 * k); c.line_to(x + 6 * k, feet - 60 * k); c.stroke()
    rrect(c, x - 5 * k, feet - 45 * k, 10 * k, 13 * k, 1.5 * k); fill(c, "#FFFFFF")
    rrect(c, x - 5 * k, feet - 45 * k, 10 * k, 13 * k, 1.5 * k); c.set_line_width(0.5 * k); src(c, INK); c.stroke()
    c.arc(x, feet - 40.5 * k, 2.2 * k, 0, 2 * math.pi); src(c, "#EDB93F"); c.fill()
    rrect(c, x - 3.5 * k, feet - 37 * k, 7 * k, 1.2 * k, 0.5 * k); src(c, "#555A66"); c.fill()
    emoji(c, "☕", x + 36 * k, feet - 30 * k, 12 * k, rot=0.1)
    emoji(c, "💤", x + 26 * k, feet - 100 * k + math.sin(t * 2) * 2 * k, 11 * k)


INTRO = dict(icon="⏰", bg="#2F6FA8", spec=AL, expr="smug", pose="hips", hand_prop=None,
             house=dict(sky=("#3E7BDA", "#BFE3FF"), walls="#E6ECF5", roof="#2F4A6B", door="#2B2F3A", lawn="#5DAA5E",
                        accent=("#3E7BDA", "#F2B233"), sun=True),
             umbrella=False, title_lines=["ARBEITSZEIT-", "BETRÜGER."], fill="#6FB7E8", decor=intro_decor,
             alex_extras=alex_extras, burst=["⏰", "💤", "🟢", "☕", "🖱️", "📵", "😴", "💻"])


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
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#2F6FA8")
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


# ---------------------------------------------------------------- Szenen
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


def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def card_():
        card(c, W / 2, 700, 980, 620, 1)
        text(c, "ANWESEND", 140, 470, 44, INK, FONT_HEAD, anchor="l")
        k = clamp((t - S.at(0, 0.2)) / 1.4)
        for i in range(8):
            x = 140 + i * 102
            rrect(c, x, 510, 92, 110, 14); fill(c, "#E6ECF5")
            if i < int(8 * k + 0.999) and k > 0:
                rrect(c, x, 510, 92, 110, 14); fill(c, "#3E7BDA")
                text(c, f"{i + 1}h", x + 46, 565, 34, "#FFFFFF", FONT_HEAD)
        text(c, "8 STUNDEN ✅", W / 2, 680, 50, "#3E7BDA", FONT_HEAD)
        if t > a1:
            text(c, "GEARBEITET", 140, 790, 44, INK, FONT_HEAD, anchor="l")
            rrect(c, 140, 830, 800, 110, 14); fill(c, "#E6ECF5")
            kk = clamp((t - a1 - 0.2) / 0.6)
            rrect(c, 140, 830, max(1, 66 * kk), 110, 14); fill(c, "#2FA36B")
            text(c, "40 MIN 😅", 560, 885, 50, "#E23B3B", FONT_HEAD)
    scaled(c, W / 2, 700, s, card_)
    if t > a1 + 0.5:
        box_fx(c, t, a1 + 0.5, W / 2, 700, 980, 620, "shock")
    alex_bottom(c, S, "smug", "hips", x=W / 2)


def sc_motto(c, S):
    t = S.t
    d0 = S.at(0, 0.0)
    s = pop(t, d0)
    def prof():
        card(c, W / 2, 700, 900, 600, 1)
        c.arc(W / 2, 640, 170, 0, 2 * math.pi); fill(c, "#3E7BDA")
        text(c, "A", W / 2, 640, 170, "#FFFFFF", FONT_HEAD)
        status_dot(c, W / 2 + 125, 640 + 120, 46, t=t)
        rrect(c, W / 2 - 220, 850, 440, 90, 45); fill(c, "#E8FBEF")
        status_dot(c, W / 2 - 170, 895, 20, pulse=False)
        text(c, "Verfügbar", W / 2 + 25, 895, 46, "#1E7A44", FONT_HEAD)
    scaled(c, W / 2, 700, s, prof)
    box_fx(c, t, d0 + 0.4, W / 2, 700, 900, 600, "party")
    alex_bottom(c, S, "smug", "hips")
    if t > d0 + 0.6:
        bubble(c, "🟢 = fleißig 😏", 820, 1190, pop(t, d0 + 0.6), tail=(-0.5, 1), size=40, max_w=320)


def sc_stamp(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    stamped = t > S.at(0, 0.5)
    def machine():
        card(c, W / 2, 700, 980, 620, 1)
        # Stempeluhr
        rrect(c, 130, 420, 380, 540, 30); fill(c, "#555A66")
        rrect(c, 130, 420, 380, 540, 30); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 165, 460, 310, 120, 14); fill(c, "#10261A")
        text(c, "08:00", 320, 520, 80, "#4DFF88", FONT_HEAD)
        clock_face(c, 320, 720, 95, 8, 0)
        rrect(c, 230, 850, 180, 22, 8); fill(c, "#1C1C22")
        dy = 0 if stamped else -60 * (1 - clamp((t - S.at(0, 0.1)) / 0.4))
        rrect(c, 260, 800 + dy, 120, 70, 8); fill(c, "#FFFFFF")
        rrect(c, 260, 800 + dy, 120, 70, 8); c.set_line_width(3); src(c, INK); c.stroke()
        text(c, "ALEX", 320, 835 + dy, 26, INK, FONT_HEAD)
        if stamped:
            text(c, "PIEP ✅", 320, 925, 40, "#4DFF88", FONT_HEAD)
        # Frühstück rechts
        if t > a1:
            k = clamp((t - a1) / 1.6)
            clock_face(c, 760, 560, 110, 8 + k, 60 * k)
            rrect(c, 580, 720, 360, 120, 18); fill(c, "#C98E5A")
            for i, e in enumerate(("🥐", "☕", "🍳", "🥯")):
                emoji(c, e, 625 + i * 90, 770, 66)
            tag(c, 760, 900, "1 STUNDE 🍽️", "#E23B3B", s=pop(t, a1 + 0.4))
    scaled(c, W / 2, 700, s, machine)
    if t > a1:
        box_fx(c, t, a1 + 0.2, 760, 700, 400, 540, "party")
    alex_bottom(c, S, "happy" if t < a1 else "smug", "idle", "☕" if t > a1 else None)


def sc_meeting(c, S):
    t, a1, a2 = S.t, S.at(1), S.at(2)
    s = pop(t, S.at(0, 0.0))
    talk = t > a2 and t < a2 + S.S.durs[2] * 0.5
    def laptop():
        rrect(c, 90, 380, 900, 620, 30); fill(c, "#1C1C22")
        rrect(c, 90, 380, 900, 620, 30); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 115, 400, 850, 60, 12); fill(c, "#3B3F8F")
        text(c, "Weekly Meeting · 12 Teilnehmer", 140, 430, 30, "#FFFFFF", FONT_BOLD, anchor="l")
        tiles = [(115, 480, "Chef", CHEF), (545, 480, "Jana", JANA), (115, 730, "Tom", TOM), (545, 730, "Alex", None)]
        for x, y, nm, sp in tiles:
            c.save(); rrect(c, x, y, 420, 235, 14); c.clip()
            fill(c, "#2E3140" if sp is None else "#DCE6F5")
            if sp is not None:
                person(c, x + 210, y + 470, 520, sp, t, ("talk" if talk and nm == "Chef" else "neutral"), bob=False,
                       blink_seed=len(nm))
            else:
                c.arc(x + 210, y + 105, 62, 0, 2 * math.pi); fill(c, "#3E7BDA")
                text(c, "A", x + 210, y + 105, 70, "#FFFFFF", FONT_HEAD)
                text(c, "📷🚫  🎤🚫", x + 210, y + 200, 34, "#FFFFFF", FONT_HEAD)
            c.restore()
            if talk and nm == "Chef":
                rrect(c, x, y, 420, 235, 14); c.set_line_width(6); src(c, "#2FD16B"); c.stroke()
            rrect(c, x + 12, y + 190, text_width(c, nm, 26, FONT_HEAD) + 24, 36, 8); src(c, "#000000", 0.55); c.fill()
            text(c, nm, x + 24, y + 208, 26, "#FFFFFF", FONT_HEAD, anchor="l")
    scaled(c, W / 2, 690, s, laptop)
    if t > a2:
        bubble(c, "Alex, was meinst du?", 330, 470, pop(t, a2 + 0.1), tail=(0, 1), size=36, max_w=420)
    if t < a1:
        alex_bottom(c, S, "neutral", "idle")
        return
    # In Wahrheit: Alex liegt im Bett (Kopf auf dem Kissen, links)
    awake = t > a2 + S.S.durs[2] * 0.35
    def bed():
        rrect(c, 110, 1200, 860, 330, 30); fill(c, "#8A6A55")
        rrect(c, 110, 1200, 860, 330, 30); c.set_line_width(5); src(c, INK); c.stroke()
        rrect(c, 130, 1230, 240, 150, 40); fill(c, "#FFFFFF")
        c.save(); c.translate(255, 1305); c.rotate(-math.pi / 2)
        person(c, 0, 520, 600, AL, t, "shock" if awake else "sleepy", "idle", bob=False)
        c.restore()
        rrect(c, 400, 1240, 550, 230, 40); fill(c, "#5B8DEF")
        rrect(c, 400, 1240, 550, 230, 40); c.set_line_width(5); src(c, INK); c.stroke()
        for i in range(4):
            c.arc(480 + i * 130, 1350, 26, 0, 2 * math.pi); src(c, "#FFFFFF", 0.35); c.fill()
        rrect(c, 600, 1195, 170, 100, 10); fill(c, "#1C1C22")
        rrect(c, 610, 1205, 150, 70, 6); fill(c, "#DCE6F5")
    scaled(c, W / 2, 1360, pop(t, a1), bed)
    tag(c, 260, 1110, "IN WAHRHEIT 🛏️", "#7A3FA8", s=pop(t, a1 + 0.2))
    if not awake:
        for i in range(3):
            uu = (t * 0.6 + i / 3) % 1
            emoji(c, "💤", 330 + uu * 120, 1200 - uu * 140, 50 + 20 * uu, alpha=1 - uu)
    else:
        bubble(c, "Sorry… Netzprobleme 📶", 720, 1100, pop(t, a2 + S.S.durs[2] * 0.4), tail=(-0.6, 1), size=36, max_w=400)


def sc_toilet(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def stall():
        card(c, W / 2, 700, 980, 620, 1, color="#EAF6F8")
        rrect(c, 120, 420, 400, 560, 16); fill(c, "#9CC7D1")
        rrect(c, 120, 420, 400, 560, 16); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 250, 450, 140, 70, 10); fill(c, "#FFFFFF")
        text(c, "WC 🚽", 320, 485, 32, INK, FONT_HEAD)
        rrect(c, 420, 680, 70, 40, 8); fill(c, "#E23B3B")
        text(c, "BESETZT", 320, 620, 36, "#E23B3B", FONT_HEAD)
        mins = int(25 * clamp((t - S.at(0, 0.3)) / max(0.8, S.S.durs[0] * 0.8)))
        rrect(c, 170, 760, 300, 120, 16); fill(c, "#10261A")
        text(c, f"{mins:02d}:00", 320, 820, 72, "#FF6B6B", FONT_HEAD)
        text(c, "MINUTEN", 320, 920, 34, INK, FONT_HEAD)
        if t > a1:
            x0, y0, w, h = phone(c, 760, 700, 340, 560, pop(t, a1), screen="#3B1E6B")
            if pop(t, a1) > 0.6:
                rnd = random.Random(5)
                for r in range(4):
                    for cc in range(4):
                        emoji(c, rnd.choice(["🍬", "💎", "🍭", "⭐"]), x0 + 50 + cc * 70, y0 + 170 + r * 70, 52)
                text(c, "LEVEL", 760, y0 + 70, 40, "#FFE14D", FONT_HEAD)
                text(c, "300 🎉", 760, y0 + 120, 56, "#FFE14D", FONT_HEAD)
    scaled(c, W / 2, 700, s, stall)
    if t > a1:
        box_fx(c, t, a1 + 0.3, 760, 700, 340, 560, "party")
    alex_bottom(c, S, "smug", "phone", "📱")


def sc_mouse(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def desk():
        rrect(c, 70, 380, 940, 660, 30); fill(c, "#E9E0F7")
        rrect(c, 70, 380, 940, 660, 30); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 220, 420, 640, 380, 20); fill(c, "#1C1C22")
        rrect(c, 240, 440, 600, 330, 10); fill(c, "#F4F7FB")
        rrect(c, 240, 440, 600, 54, 10); fill(c, "#3B3F8F")
        text(c, "Alex  ·  Verfügbar", 270, 467, 30, "#FFFFFF", FONT_BOLD, anchor="l")
        status_dot(c, 800, 467, 16, pulse=False)
        jx = math.sin(t * 7) * 110
        jy = math.sin(t * 11) * 50
        c.save(); c.translate(540 + jx, 630 + jy)
        c.move_to(0, 0); c.line_to(0, 44); c.line_to(12, 33); c.line_to(22, 54); c.line_to(30, 50); c.line_to(20, 30); c.line_to(36, 30); c.close_path()
        fill(c, "#FFFFFF"); c.move_to(0, 0); c.line_to(0, 44); c.line_to(12, 33); c.line_to(22, 54); c.line_to(30, 50); c.line_to(20, 30); c.line_to(36, 30); c.close_path()
        c.set_line_width(3); src(c, INK); c.stroke(); c.restore()
        rrect(c, 510, 800, 60, 60, 4); fill(c, "#555A66")
        rrect(c, 120, 880, 840, 40, 8); fill(c, "#B07A4F")
        mx = 700 + math.sin(t * 7) * 30
        c.save(); c.translate(mx, 860); ellipse(c, 0, 0, 34, 22); fill(c, "#FFFFFF")
        ellipse(c, 0, 0, 34, 22); c.set_line_width(3); src(c, INK); c.stroke(); c.restore()
    scaled(c, W / 2, 710, s, desk)
    if t < a1 + 0.5:
        tag(c, 760, 1000, "MAUS-WACKLER 🖱️", "#7A3FA8", s=pop(t, S.at(0, 0.6)) * out_fade(t, a1 + 0.3))
    if t > a1:
        tag(c, 260, 1000, "STATUS: 🟢", "#2FA36B", s=pop(t, a1 + 0.1))
        tag(c, 690, 1000, "ALEX: BEIM FRISEUR 💇", "#E23B3B", s=pop(t, a1 + 0.6))
        alex_bottom(c, S, "happy", "idle")
        # Friseur-Umhang mit Kragen
        c.move_to(W / 2 - 70, 1345); c.curve_to(W / 2 - 150, 1420, W / 2 - 190, 1520, W / 2 - 200, 1580)
        c.line_to(W / 2 + 200, 1580); c.curve_to(W / 2 + 190, 1520, W / 2 + 150, 1420, W / 2 + 70, 1345); c.close_path()
        src(c, "#F07FB0", 0.95); c.fill_preserve(); c.set_line_width(4); src(c, INK); c.stroke()
        rrect(c, W / 2 - 75, 1335, 150, 26, 12); fill(c, "#FFFFFF")
        for i in range(6):
            rnd = random.Random(i); uu = (t * 0.8 + rnd.random()) % 1
            c.arc(W / 2 + rnd.uniform(-120, 120), 1360 + uu * 200, 4, 0, 2 * math.pi); src(c, "#EDB93F", 1 - uu); c.fill()
        emoji(c, "✂️", 700, 1190 + math.sin(t * 7) * 10, 70, rot=math.sin(t * 14) * 0.3)
    else:
        alex_bottom(c, S, "smug", "hips")


def sc_mail(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    night = t > a1 + S.S.durs[1] * 0.45
    def mail():
        card(c, W / 2, 700, 940, 620, 1)
        rrect(c, 85, 395, 910, 80, 14); fill(c, "#3E7BDA")
        text(c, "✉️ Neue E-Mail", 120, 435, 36, "#FFFFFF", FONT_HEAD, anchor="l")
        rows = [("An:", "Chef"), ("Betreff:", "Hab noch kurz drübergeschaut 💪")]
        for i, (k_, v) in enumerate(rows):
            text(c, k_, 120, 525 + i * 70, 32, "#555A66", FONT_BOLD, anchor="l")
            text(c, v, 290, 525 + i * 70, 32, INK, FONT_HEAD, anchor="l")
        c.move_to(110, 640); c.line_to(970, 640); c.set_line_width(2); src(c, "#D0D6E0"); c.stroke()
        if t > a1:
            rrect(c, 120, 680, 840, 110, 20); fill(c, "#FFF4D6")
            rrect(c, 120, 680, 840, 110, 20); c.set_line_width(4); src(c, "#F2B233"); c.stroke()
            text(c, "⏰ Senden planen: 22:00 Uhr", W / 2, 735, 44, INK, FONT_HEAD)
        if night:
            rrect(c, 120, 830, 840, 110, 20); fill(c, "#E8FBEF")
            text(c, "✅ Gesendet um 22:00", W / 2, 885, 46, "#1E7A44", FONT_HEAD)
    scaled(c, W / 2, 700, s, mail)
    if night:
        emoji(c, "🌙", 900, 1120, 90 * pop(t, a1 + S.S.durs[1] * 0.45))
        bubble(c, "Wow, so fleißig! 👏", 290, 1110, pop(t, a1 + S.S.durs[1] * 0.6), tail=(0.5, 1), size=36, max_w=380)
        box_fx(c, t, a1 + S.S.durs[1] * 0.45, W / 2, 700, 940, 620, "shock")
    if t < a1:
        alex_bottom(c, S, "happy", "wave")
        tag(c, W / 2, 940, "16:00 FEIERABEND 🏃", "#2FA36B", s=pop(t, S.at(0, 0.3)))
    else:
        alex_bottom(c, S, "smug", "hips")


def sc_signs(c, S):
    t = S.t
    items = [("Status immer grün", "🟢"), ("Ständig Netzprobleme", "📶"),
             ("„Ich nehm das mal mit“", "📝"), ("Tippt nur, wenn der Chef guckt", "⌨️")]
    for i, (lab, ic) in enumerate(items):
        y = 400 + i * 175
        row_card(c, W / 2, y, 1000, 160, pop(t, S.at(i + 1, 0.0)), lab, ic, 40, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1150 + math.sin(t * 3 + i) * 12, 90 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    alex_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du auch einen Arbeitszeit-Betrüger?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 1000, 220, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 52, 940, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tg():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#2F6FA8", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@kollege"
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tg, rot=math.sin(t * 4) * 0.02)
    if t >= a1:
        colors = ["#EC7FAE", "#3E5C9A", "#4A2E6B", "#5E8C3A", "#2F6FA8", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        prev = [("🌹", "FOLGE 1"), ("🥺", "FOLGE 2"), ("🌀", "FOLGE 3"), ("🏘️", "FOLGE 4"), ("⏰", "HEUTE ✅")]
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


SCENE_DRAW = dict(what=sc_what, motto=sc_motto, stamp=sc_stamp, meeting=sc_meeting, toilet=sc_toilet, mouse=sc_mouse,
                  mail=sc_mail, signs=sc_signs, outro=sc_outro)
