"""Visuals für Folge 3 (Choleriker). Keine Gewalt gegen Menschen oder Tiere:
Wut wird nur über Comic-Effekte gezeigt (roter Kopf, Dampf, 💢, Wackeln).
"""
import math, random
from alexlib import *

# Outfit heute: Büro-Look mit Krawatte
AL = alex(top="#3C4A63", top_style="suit", tie="#D63A3A", pants="#2F3B52", shoes="#3A2A20")
FEET, AH = 1665, 470

INTRO = dict(icon="😡", bg="#D9534F", spec=AL, expr="angry", pose="cross", hand_prop=None,
             side_emoji="💢", burst=["💢", "😡", "💨", "🔥", "📢", "🍞", "🖨️", "🚗"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


def rage(c, t, x=W / 2, y=FEET - AH * 0.9, k=1.0):
    """Comic-Wut: Dampfwolken links/rechts vom Kopf + 💢."""
    for i, sx in enumerate((-1, 1)):
        u = (t * 1.6 + i * 0.5) % 1
        emoji(c, "💨", x + sx * (120 + u * 60) * k, y - u * 60 * k, 70 * k, rot=sx * 0.4, alpha=1 - u)
    emoji(c, "💢", x + 130 * k, y - 120 * k, 80 * k * (1 + 0.1 * math.sin(t * 14)))


def alex_bottom(c, S, expr="happy", pose="idle", prop=None, x=W / 2, h=AH, angry=False):
    shake = math.sin(S.t * 55) * 6 if angry else 0
    person(c, x + shake, FEET, h, AL, S.t, expr, pose, prop, name="Alex")
    if angry:
        rage(c, S.t, x, FEET - h * 0.9, h / AH)


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#E23B3B")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def red_flash(c, t, t0, d=0.25):
    if t0 <= t < t0 + d:
        c.save(); c.identity_matrix()
        c.set_source_rgba(1, 0.15, 0.1, 0.35 * (1 - (t - t0) / d)); c.paint()
        c.restore()


# ======================================================================= SZENEN
def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    # Wut-Meter: Nadel springt in Zeile 2 von 0 auf 100
    val = 0.05 if t < a1 else 0.05 + 0.95 * ease_out_back((t - S.at(1, 0.35)) / 0.35, 1.2) if t > S.at(1, 0.35) else 0.05
    def meter():
        cx, cy, R = W / 2, 900, 360
        card(c, cx, 760, 920, 560, 1)
        cols = ["#2FA36B", "#9BCB3C", "#F2B233", "#F07F4F", "#E23B3B"]
        for i, col in enumerate(cols):
            a0 = math.pi + i * math.pi / 5
            c.arc(cx, cy, R, a0, a0 + math.pi / 5)
            c.arc_negative(cx, cy, R - 80, a0 + math.pi / 5, a0)
            c.close_path(); fill(c, col)
        text(c, "0", cx - R + 40, cy + 45, 40, INK, FONT_HEAD)
        text(c, "100", cx + R - 50, cy + 45, 40, INK, FONT_HEAD)
        text(c, "WUT-O-METER", cx, 560, 48, INK, FONT_HEAD)
        ang = math.pi + clamp(val, 0, 1.08) * math.pi
        c.save(); c.translate(cx, cy); c.rotate(ang)
        c.move_to(0, -12); c.line_to(R - 70, 0); c.line_to(0, 12); c.close_path(); fill(c, INK)
        c.restore()
        c.arc(cx, cy, 26, 0, 2 * math.pi); fill(c, INK)
    shake = math.sin(t * 60) * 8 if t > S.at(1, 0.7) else 0
    scaled(c, W / 2 + shake, 760, s, meter)
    if t > S.at(1, 0.7):
        text(c, "⚠️ 1 SEKUNDE", W / 2, 1090, 56 * pop(t, S.at(1, 0.7)), "#FFFFFF", FONT_HEAD)
    red_flash(c, t, S.at(1, 0.7))
    angry = t > S.at(1, 0.6)
    alex_bottom(c, S, "angry" if angry else "happy", "cross" if angry else "idle", angry=angry)


def toaster(c, x, y, s):
    def d():
        rrect(c, x - 230, y - 150, 460, 300, 70)
        c.set_source(cairo.LinearGradient(0, y - 150, 0, y + 150)); fill(c, "#C9CED6")
        rrect(c, x - 230, y - 150, 460, 300, 70); c.set_line_width(6); src(c, INK); c.stroke()
        for dx in (-90, 90):
            rrect(c, x + dx - 70, y - 160, 140, 26, 13); fill(c, "#3A3A40")
        rrect(c, x + 200, y - 30, 70, 30, 10); fill(c, "#3A3A40")
    scaled(c, x, y, s, d)


def sc_toast(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    up = ease_out_back((t - S.at(0, 0.2)) / 0.4)
    # Toastscheiben (verbrannt) springen hoch
    for i, dx in enumerate((-90, 90)):
        y = 760 - 180 * up
        def tst(dx=dx, y=y):
            rrect(c, W / 2 + dx - 75, y - 90, 150, 170, 40); fill(c, "#3B2414")
            rrect(c, W / 2 + dx - 75, y - 90, 150, 170, 40); c.set_line_width(5); src(c, "#1E120A"); c.stroke()
            rrect(c, W / 2 + dx - 58, y - 72, 116, 134, 32); fill(c, "#2A180C")
        if t > S.at(0, 0.2):
            scaled(c, W / 2, 760, s, tst)
    toaster(c, W / 2, 820, s)
    if t > S.at(0, 0.3):
        for i in range(3):
            u = (t * 0.7 + i / 3) % 1
            emoji(c, "💨", W / 2 - 100 + i * 100, 520 - u * 150, 60, alpha=(1 - u) * 0.8)
    if t > a1:
        # Toaster schweigt: "..." Sprechblase
        bubble(c, "…", 820, 600, pop(t, a1 + 0.1), tail=(-0.5, 1), size=60, max_w=200)
    angry = t > S.at(0, 0.5)
    alex_bottom(c, S, "angry" if angry else "neutral", "cross" if angry else "idle", angry=angry)
    if t > S.at(0, 0.55):
        bubble(c, "Das ist doch nicht zu fassen!", 540, 1085, pop(t, S.at(0, 0.55)) * out_fade(t, a1 + 0.3),
               tail=(0, 1), size=40, max_w=640)
    red_flash(c, t, S.at(0, 0.55))


def sc_traffic(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def road():
        rrect(c, 60, 450, 960, 520, 30); fill(c, "#55585F")
        rrect(c, 60, 450, 960, 520, 30); c.set_line_width(6); src(c, INK); c.stroke()
        for i in range(6):
            rrect(c, 110 + i * 160, 705, 90, 14, 7); fill(c, "#F2F2F2")
        cars = ["🚙", "🚕", "🚐", "🚗", "🚌"]
        for i, e in enumerate(cars):
            emoji(c, e, 160 + i * 190, 590, 130)
            emoji(c, cars[(i + 2) % 5], 160 + i * 190, 850, 130)
        rrect(c, 300, 380, 480, 80, 18); fill(c, "#FFFFFF")
        rrect(c, 300, 380, 480, 80, 18); c.set_line_width(5); src(c, INK); c.stroke()
        text(c, "Tempo: 0 km/h", 540, 420, 40, INK, FONT_HEAD)
    scaled(c, W / 2, 700, s, road)
    # Hupen
    for k in range(4):
        th = S.at(0, 0.25 + 0.17 * k)
        if th <= t < th + 0.45:
            u = (t - th) / 0.45
            text(c, "HUUUP!", 300 + (k % 2) * 480, 1040 - (k % 2) * 30, 70 * (0.6 + 0.6 * ease_out_back(u)),
                 "#FFE14D", FONT_HEAD, alpha=1 - u * 0.6)
    if t >= a1:
        def ey():
            c.save(); c.translate(W / 2, 1040); c.rotate(-0.08)
            text(c, "EY!", 0, 6, 220, "#000000", FONT_HEAD, alpha=0.3)
            text(c, "EY!", 0, 0, 220, "#FFFFFF", FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 1040, pop(t, a1 + 0.15), ey)
        red_flash(c, t, a1 + 0.15)
    alex_bottom(c, S, "angry", "cross", angry=True)


def sc_office(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    if t < a1 + 0.2:
        o = out_fade(t, a1)
        def printer():
            emoji(c, "🖨️", W / 2, 680, 380)
            rrect(c, 300, 880, 480, 100, 16); fill(c, "#1F1F28")
            blink_on = int(t * 4) % 2 == 0
            text(c, "PAPIERSTAU", 540, 930, 52, "#FF4D4D" if blink_on else "#802020", FONT_HEAD)
        scaled(c, W / 2, 780, s * o, printer)
        bubble(c, "Warum passiert das immer mir?!", 540, 1085, pop(t, S.at(0, 0.45)) * o, tail=(0, 1), size=42, max_w=640)
        red_flash(c, t, S.at(0, 0.45))
    else:
        cs = pop(t, a1 + 0.05)
        def coworkers():
            for i, x in enumerate((200, 540, 880)):
                sp = person_spec(50 + i, girl=bool(i % 2))
                person(c, x, 940, 380, sp, t, "cringe", blink_seed=i, bob=False)
                rrect(c, x - 140, 760, 280, 190, 14); fill(c, "#2B2F3A")
                rrect(c, x - 140, 760, 280, 190, 14); c.set_line_width(5); src(c, INK); c.stroke()
                rrect(c, x - 125, 775, 250, 160, 8); fill(c, "#7FB3FF")
                for j in range(4):
                    u = ((t * 2 + j * 0.25 + i * 0.3) % 1)
                    rrect(c, x - 110, 790 + j * 35, 220 * (0.4 + 0.6 * u), 14, 7); fill(c, "#FFFFFF")
            rrect(c, 60, 940, 960, 40, 10); fill(c, "#B07A4F")
            text(c, "SEHR BESCHÄFTIGT 👀", W / 2, 560, 54, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 800, cs, coworkers)
    alex_bottom(c, S, "angry", "cross", angry=t > S.at(0, 0.4))


def sc_wifi(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    def browser():
        card(c, W / 2, 720, 900, 640, 1)
        rrect(c, 90, 400, 900, 90, 0); fill(c, "#E6E6EA")
        for i, col in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
            c.arc(140 + i * 45, 445, 14, 0, 2 * math.pi); fill(c, col)
        rrect(c, 290, 420, 660, 50, 25); fill(c, "#FFFFFF")
        text(c, "www.wichtige-seite.de", 320, 445, 28, "#555555", FONT_BOLD, anchor="l")
        # Lade-Kreis
        c.save(); c.translate(W / 2, 700); c.rotate(t * 6)
        c.set_line_width(22); c.set_line_cap(cairo.LINE_CAP_ROUND); src(c, "#3D8BFF")
        c.arc(0, 0, 110, 0, math.pi * 1.4); c.stroke()
        c.restore()
        secs = min(3.0, max(0, (t - S.at(0, 0.1))) * 1.0)
        text(c, f"Lädt … {secs:.1f} s", W / 2, 900, 48, INK, FONT_HEAD)
    scaled(c, W / 2, 720, s, browser)
    if t > S.at(0, 0.55):
        red_flag_stamp(c, W / 2, 620, pop(t, S.at(0, 0.55), 0.25), "PERSÖNLICHER ANGRIFF", rot=-0.15)
        red_flash(c, t, S.at(0, 0.55))
    angry = t > S.at(0, 0.5)
    alex_bottom(c, S, "angry" if angry else "neutral", "cross" if angry else "idle", "📱" if not angry else None, angry=angry)


def sc_market(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def store():
        for i, x in enumerate((280, 800)):
            rrect(c, x - 180, 700, 360, 160, 16); fill(c, "#D9DDE3")
            rrect(c, x - 180, 700, 360, 160, 16); c.set_line_width(5); src(c, INK); c.stroke()
            rrect(c, x - 70, 420, 140, 90, 14); fill(c, "#2FA36B" if (i == 1 and t > S.at(0, 0.15)) else "#888888")
            text(c, str(i + 1), x, 465, 60, "#FFFFFF", FONT_HEAD)
            c.set_line_width(6); src(c, "#555555"); c.move_to(x, 510); c.line_to(x, 700); c.stroke()
        # Schlange an Kasse 1
        for j in range(3):
            person(c, 180 + j * 70, 1000, 260, person_spec(60 + j, girl=bool(j % 2)), t, "neutral", bob=False)
        if t > S.at(0, 0.15):
            text(c, "KASSE 2 ÖFFNET!", 800, 600, 46, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, 700, s, store)
    # Jemand anderes ist schneller (Person mit Einkaufswagen gleitet zur Kasse 2)
    if t > a1 - 0.6:
        u = ease_in_out((t - (a1 - 0.6)) / 0.8)
        x = 1200 - u * 400
        person(c, x, 1010, 270, person_spec(77, girl=True, hair_style="bun", hair="#C9C9CF", glasses=True,
                                             top="#8E5BE0"), t, "happy", bob=False)
        emoji(c, "🛒", x - 120, 960, 110)
    if t > a1:
        text(c, "ZU SPÄT!", 330, 1110, 90 * pop(t, a1 + 0.3), "#FFE14D", FONT_HEAD)
        red_flash(c, t, a1 + 0.3)
    # Alex sprintet ins Bild
    if t < a1:
        ax = W / 2 + 140 * ease_out_cubic((t - S.at(0, 0.6)) / 0.5) if t > S.at(0, 0.6) else W / 2
        alex_bottom(c, S, "happy" if t < S.at(0, 0.6) else "shock", "point", x=ax)
        if t > S.at(0, 0.6):
            emoji(c, "💨", ax - 220, FEET - 120, 100, alpha=0.8)
    else:
        alex_bottom(c, S, "angry", "cross", x=W / 2 + 140, angry=True)


def sc_gaming(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    lost = t > S.at(0, 0.3)
    def tv():
        rrect(c, 110, 380, 860, 560, 30); fill(c, "#141418")
        rrect(c, 110, 380, 860, 560, 30); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 140, 410, 800, 500, 18); fill(c, "#5B1E2E" if lost else "#1E3A5B")
        if lost:
            text(c, "DEFEAT", W / 2, 620, 130, "#FF4D4D", FONT_HEAD)
            text(c, "0 : 12", W / 2, 760, 64, "#FFFFFF", FONT_HEAD)
        else:
            text(c, "FINALE RUNDE", W / 2, 640, 80, "#FFFFFF", FONT_HEAD)
        rrect(c, 480, 940, 120, 50, 8); fill(c, "#141418")
    scaled(c, W / 2, 660, s, tv)
    if lost:
        red_flash(c, t, S.at(0, 0.3))
        bubble(c, "Der hat doch gecheatet!", 540, 1085, pop(t, S.at(0, 0.5)) * out_fade(t, a1), tail=(0, 1), size=42)
    if t > a1:
        # Controller mit Schweißtropfen (wird nur angeschrien)
        cs = pop(t, a1 + 0.1)
        emoji(c, "🎮", 820, 1150, 140 * cs, rot=math.sin(t * 30) * 0.08)
        emoji(c, "💦", 900, 1080, 60 * cs)
        for k, w in enumerate(("!!!", "#@%!", "WARUM?!")):
            tk = S.at(1, 0.15 + 0.22 * k)
            if t > tk:
                text(c, w, 260 + k * 70, 1060 - k * 70, 54 * pop(t, tk), "#FFE14D", FONT_HEAD)
    alex_bottom(c, S, "angry" if lost else "smug", "cross" if lost else "idle", None if lost else "🎮", angry=lost)


def sc_sorry(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def counter():
        card(c, W / 2, 680, 800, 440, 1)
        text(c, "ENTSCHULDIGUNGEN", W / 2, 540, 50, INK, FONT_HEAD)
        text(c, "HEUTE", W / 2, 600, 40, "#777777", FONT_HEAD)
        n = 1 if t < a1 else min(12, 1 + int(11 * ease_out_cubic((t - a1) / 1.2)))
        text(c, str(n), W / 2, 740, 170, "#E23B3B", FONT_HEAD)
    scaled(c, W / 2, 680, s, counter)
    # Heiligenschein
    hy = FEET - AH * 1.12
    c.save(); c.translate(W / 2, hy); c.scale(1, 0.3)
    c.arc(0, 0, 90, 0, 2 * math.pi); c.restore()
    c.set_line_width(10); src(c, "#FFE14D", pop(t, S.at(0, 0.2)) * 0.95); c.stroke()
    alex_bottom(c, S, "puppy", "idle")
    bubble(c, "Sorry, war nicht so gemeint 😇", 540, 1020, pop(t, S.at(0, 0.3)), tail=(0, 1), size=44)


def sc_signs(c, S):
    t = S.t
    items = [("Roter Kopf", "🍅"), ("Lauter als nötig", "📢"), ("Kleinigkeit = Katastrophe", "🌋"), ("Danach war „nichts“", "😇")]
    for i, (lab, ic) in enumerate(items):
        y = 420 + i * 175
        row_card(c, W / 2, y, 900, 140, pop(t, S.at(i + 1, 0.0)), lab, ic, 44, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    last = t > S.at(4)
    alex_bottom(c, S, "puppy" if last else "angry", "idle" if last else "cross", angry=not last and t > S.at(1))


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du noch einen Choleriker?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 920, 150, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 50, 860, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#D9534F", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@der_mit_dem_roten_kopf"
            n = int(clamp((t - S.at(0, 0.55)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#5FA9B8", "#D9534F", "#F2B233", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        prev = [("🌹", "FOLGE 1", "#555A66"), ("🛋️", "FOLGE 2", "#555A66"), ("😡", "HEUTE ✅", "#2FA36B")]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 260 + cc * 280, 500 + r * 230
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 95, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 95, 0, 2 * math.pi); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
                if i < 3:
                    e, lab, col = prev[i]
                    emoji(c, e, x, y, 100)
                    rrect(c, x - 85, y + 70, 170, 46, 12); fill(c, col)
                    text(c, lab, x, y + 93, 26, "#FFFFFF", FONT_HEAD)
                else:
                    text(c, "?", x, y, 110, "#FFFFFF", FONT_HEAD)
            scaled(c, x, y, pop(t, a1 + 0.1 + i * 0.07), icon)
        ps = pop(t, S.at(1, 0.45))
        def pill():
            rrect(c, 170, 1040, 740, 96, 48); fill(c, "#E23B3B")
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1088, 42, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1088, ps * (1 + 0.04 * math.sin(t * 7)), pill)
    alex_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=sc_what, toast=sc_toast, traffic=sc_traffic, office=sc_office, wifi=sc_wifi,
                  market=sc_market, gaming=sc_gaming, sorry=sc_sorry, signs=sc_signs, outro=sc_outro)
