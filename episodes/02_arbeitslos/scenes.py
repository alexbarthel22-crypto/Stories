"""Visuals für Folge 2 v2 (Arbeitslos – volles Klischee + echte Fakten).
S.t = Zeit in der Szene, S.at(i, f) = Startzeit von Zeile i (+ Anteil f ihrer Dauer).
"""
import math, random
from alexlib import *

# Klischee-Outfit: Feinripp-Muskelshirt, graue Jogginghose, Badelatschen-Blau
AL = alex(top="#F4F4F2", top_style="tank", pants="#8A8F99", shoes="#2E5E9E")
FEET, AH = 1665, 470
OMA = person_spec(5, girl=True, hair_style="bun", hair="#C9C9CF", skin="#F1C9A8", top="#8E5BE0",
                  pants="#4A4A5A", shoes="#5A3A2A", glasses=True)
MAMA = person_spec(6, girl=True, hair="#7A4A2A", top="#2FA36B", skin="#F1C9A8")
OPA = person_spec(9, hair="#DADADF", top="#7A5C45", skin="#F1C9A8", glasses=True)
BERATERIN = person_spec(8, girl=True, hair="#3B2A20", top="#3C3C46", top_style="suit", tie="#3E7BDA",
                        glasses=True, skin="#E9B48A")

INTRO = dict(icon="🛋️", bg="#5FA9B8", spec=AL, expr="smug", pose="idle", hand_prop="beer",
             side_emoji="📺", burst=["💶", "📺", "🛋️", "🦗", "🥨", "📄", "⏰", "🧾"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


def alex_bottom(c, S, expr="happy", pose="idle", prop="beer", x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Alex")


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def row_card(c, x, y, w, h, s, label, icon=None, size=40, check=False, rot=0.0, color="#FFFFFF"):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, color)
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if check:
            emoji(c, "✅", x - w / 2 + 65, y, 52)
            lx = x - w / 2 + 115
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def silence(c, t, t0, x=W / 2, y=980):
    """Running Gag: niemand lacht – Grille + Stille-Schild."""
    if t < t0:
        return
    s = pop(t, t0)
    emoji(c, "🦗", x - 170, y + math.sin(t * 9) * 6, 120 * s)
    def tag():
        rrect(c, x - 60, y - 50, 300, 100, 20); fill(c, "#1F1F28")
        text(c, "*STILLE*", x + 90, y, 46, "#FFFFFF", FONT_HEAD)
    scaled(c, x + 90, y, s, tag, rot=-0.05)


def bar(c, x, y, w, h, frac, col, label, value):
    rrect(c, x, y, w, h, h / 2); fill(c, "#EDEDF0")
    if frac > 0.01:
        rrect(c, x, y, max(h, w * frac), h, h / 2); fill(c, col)
    text(c, label, x, y - 34, 34, "#444444", FONT_BOLD, anchor="l")
    text(c, value, x + w, y - 34, 40, INK, FONT_HEAD, anchor="r")


# ======================================================================= SZENEN
def sc_plan(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        s = pop(t, S.at(0, 0.0)) * out_fade(t, a1)
        def letter():
            c.save(); c.translate(W / 2, 720); c.rotate(-0.04)
            rrect(c, -330 + 10, -400 + 14, 660, 800, 18); src(c, "#000000", 0.2); c.fill()
            rrect(c, -330, -400, 660, 800, 18); fill(c, "#FFFFFF")
            rrect(c, -330, -400, 660, 800, 18); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, "KÜNDIGUNG", 0, -300, 70, INK, FONT_HEAD)
            text(c, "Sehr geehrter Herr Alex,", -270, -200, 30, "#333333", FONT_BOLD, anchor="l")
            for i in range(6):
                rrect(c, -270, -140 + i * 50, 540 - (i % 3) * 90, 14, 7); fill(c, "#DADADA")
            c.restore()
        scaled(c, W / 2, 720, s, letter)
        red_flag_stamp(c, W / 2, 900, pop(t, S.at(0, 0.5), 0.25), "FIRMA PLEITE", rot=-0.18)
        alex_bottom(c, S, "sad" if t > S.at(0, 0.4) else "shock", prop=None)
    if t >= a1:
        s = pop(t, a1 + 0.05)
        card(c, W / 2, 470, 760, 120, s, color="#1F1F28")
        scaled(c, W / 2, 470, s, lambda: text(c, "OUTFIT-CHECK 👀", W / 2, 470, 56, "#FFFFFF", FONT_HEAD))
        items = [("Feinripp-Muskelshirt", "🎽", 0.3), ("Jogginghose", "👖", 0.5), ("Bier in der Hand", "🍺", 0.7)]
        for i, (lab, ic, f) in enumerate(items):
            row_card(c, W / 2, 650 + i * 160, 900, 130, pop(t, S.at(1, f)), lab, ic, 44, check=True,
                     rot=(0.015 if i % 2 else -0.015))
        alex_bottom(c, S, "smug", "idle")


def sc_money1(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def panel():
        card(c, W / 2, 720, 920, 680, 1)
        text(c, "ARBEITSLOSENGELD I", W / 2, 450, 54, INK, FONT_HEAD)
        grow = ease_out_cubic((t - S.at(0, 0.5)) / 0.8)
        bar(c, 150, 600, 780, 60, 1.0, "#8A8F99", "Letztes Netto", "2.000 €")
        bar(c, 150, 760, 780, 60, 0.6 * grow, "#2FA36B", "Arbeitslosengeld", f"≈ {int(1200 * grow):,} €".replace(",", "."))
        if t > S.at(0, 0.5):
            rrect(c, 150 + 780 * 0.6 - 70, 840, 140, 60, 30); fill(c, "#2FA36B")
            text(c, "60 %", 150 + 780 * 0.6, 870, 36, "#FFFFFF", FONT_HEAD)
        text(c, "mit Kind: 67 %", W / 2, 960, 30, "#777777", FONT_BOLD)
    scaled(c, W / 2, 720, s, panel)
    if t >= a1:
        def cal():
            c.save(); c.translate(850, 1120); c.rotate(0.08)
            rrect(c, -150, -95, 300, 190, 22); fill(c, "#FFFFFF")
            rrect(c, -150, -95, 300, 190, 22); c.set_line_width(5); src(c, INK); c.stroke()
            rrect(c, -150, -95, 300, 55, 22); fill(c, "#E23B3B")
            text(c, "MAXIMAL", 0, -67, 30, "#FFFFFF", FONT_HEAD)
            text(c, "12 MONATE", 0, 20, 48, INK, FONT_HEAD)
            text(c, "(unter 50 Jahren)", 0, 66, 22, "#777777", FONT_BOLD)
            c.restore()
        scaled(c, 850, 1120, pop(t, S.at(1, 0.5)), cal)
    alex_bottom(c, S, "happy", "idle")


def sc_money2(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def panel():
        card(c, W / 2, 620, 920, 480, 1)
        text(c, "GRUNDSICHERUNGSGELD", W / 2, 440, 50, INK, FONT_HEAD)
        text(c, "(früher Bürgergeld)", W / 2, 495, 32, "#777777", FONT_BOLD)
        n = int(563 * ease_out_cubic((t - S.at(0, 0.55)) / 0.7)) if t > S.at(0, 0.55) else 0
        if t > S.at(0, 0.55):
            text(c, f"{n} €", W / 2, 640, 170, "#2FA36B", FONT_HEAD)
        text(c, "pro Monat · Alleinstehend · 2026", W / 2, 770, 30, "#555555", FONT_BOLD)
    scaled(c, W / 2, 620, s, panel)
    if t >= a1:
        row_card(c, W / 2, 960, 900, 110, pop(t, a1 + 0.05), "+ angemessene Miete & Heizung", "🏠", 38)
        def day():
            c.save(); c.translate(W / 2, 1110); c.rotate(-0.04)
            rrect(c, -300, -55, 600, 110, 55); fill(c, "#F7C948")
            rrect(c, -300, -55, 600, 110, 55); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, "≈ 18,50 € / TAG 🪙", 0, 0, 50, INK, FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 1110, pop(t, S.at(1, 0.6)), day)
    alex_bottom(c, S, "neutral" if t < a1 else "shock", "idle")


def sc_morning(c, S):
    t = S.t
    for i, (x, e, lab, f) in enumerate(((290, "🥣", "FRÜHSTÜCK", 0.2), (790, "🍝", "MITTAG", 0.45))):
        s = pop(t, S.at(0, f))
        def d(x=x, e=e, lab=lab):
            card(c, x, 700, 420, 460, 1)
            emoji(c, e, x, 650, 220)
            text(c, lab, x, 860, 46, INK, FONT_HEAD)
        scaled(c, x, 700, s, d, rot=(-0.04 if i == 0 else 0.04))
    text(c, "=", W / 2, 700, 140 * pop(t, S.at(0, 0.6)), "#FFFFFF", FONT_HEAD)
    alex_bottom(c, S, "sleepy" if t < S.at(0, 0.5) else "happy", "idle", "☕")


def sc_jobcenter(c, S):
    t, a1, a2 = S.t, S.at(1), S.at(2)
    s = pop(t, S.at(0, 0.0))
    def desk():
        person(c, 300, 1000, 380, BERATERIN, t, "neutral" if t < a1 + 0.8 else "cringe", bob=False, name="Beraterin")
        rrect(c, 90, 880, 460, 110, 12); fill(c, "#B07A4F")
        rrect(c, 90, 880, 460, 110, 12); c.set_line_width(5); src(c, INK); c.stroke()
        emoji(c, "🗂️", 470, 855, 70)
    scaled(c, 300, 900, s, desk)
    if t < a1 + 0.2:
        def warn():
            c.save(); c.translate(760, 560); c.rotate(0.05)
            rrect(c, -230, -150, 460, 300, 22); fill(c, "#FFFFFF")
            rrect(c, -230, -150, 460, 300, 22); c.set_line_width(5); src(c, INK); c.stroke()
            emoji(c, "⚠️", 0, -80, 70)
            text(c, "TERMIN VERPASST?", 0, 0, 36, INK, FONT_HEAD)
            text(c, "Kürzung möglich", 0, 60, 36, "#E23B3B", FONT_HEAD)
            c.restore()
        scaled(c, 760, 560, pop(t, S.at(0, 0.3)) * out_fade(t, a1), warn)
    if a1 <= t < a2 + 0.2:
        bubble(c, "Ich hab morgen frei! 😎", 760, 1060, pop(t, a1 + 0.05) * out_fade(t, a2), tail=(-0.3, 1), size=44, max_w=440)
    silence(c, t, S.at(1, 1.0) + 0.2, x=700, y=600)
    alex_bottom(c, S, "smug" if t < a2 else "neutral", "idle", x=760)


def tv(c, x, y, s, t, mode):
    def d():
        rrect(c, x - 300, y - 230, 600, 440, 40); fill(c, "#6B4A2E")
        rrect(c, x - 300, y - 230, 600, 440, 40); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, x - 260, y - 195, 430, 370, 60); fill(c, "#1E2A2A")
        c.save(); rrect(c, x - 260, y - 195, 430, 370, 60); c.clip()
        if mode == 0:
            src(c, "#2E4B6B"); c.paint()
            emoji(c, "⚖️", x - 45, y - 40, 150)
            text(c, "GERICHTSSHOW", x - 45, y + 110, 40, "#FFFFFF", FONT_HEAD)
        else:
            src(c, "#6B2E2E"); c.paint()
            emoji(c, "😱", x - 45, y - 50, 150)
            text(c, "DER NACHBAR!", x - 45, y + 110, 42, "#FFE14D", FONT_HEAD)
        # Röhrenfernseher-Streifen
        for i in range(0, 370, 8):
            c.rectangle(x - 260, y - 195 + i + (t * 40) % 8, 430, 2)
        src(c, "#000000", 0.18); c.fill()
        c.restore()
        for i in range(2):
            c.arc(x + 235, y - 120 + i * 80, 22, 0, 2 * math.pi); fill(c, "#2B2B2B")
        rrect(c, x - 70, y + 210, 140, 30, 8); fill(c, "#3A2A1E")
        rrect(c, x - 250, y - 200, 60, 40, 8); fill(c, "#E23B3B")
        text(c, "LIVE", x - 220, y - 180, 22, "#FFFFFF", FONT_HEAD)
    scaled(c, x, y, s, d)


def fliesentisch(c, x, y, s):
    def d():
        rrect(c, x - 300, y - 40, 600, 80, 10); fill(c, "#E8DCC0")
        c.save(); rrect(c, x - 300, y - 40, 600, 80, 10); c.clip()
        for i in range(-300, 300, 50):
            for j in range(-40, 40, 40):
                c.rectangle(x + i + 3, y + j + 3, 44, 34)
                src(c, "#D9C59A" if ((i // 50 + j // 40) % 2) else "#EFE3C8"); c.fill()
        c.restore()
        rrect(c, x - 300, y - 40, 600, 80, 10); c.set_line_width(5); src(c, INK); c.stroke()
        rrect(c, x - 320, y + 40, 640, 26, 6); fill(c, "#6B4A2E")
        for dx in (-280, 260):
            rrect(c, x + dx, y + 66, 22, 90, 4); fill(c, "#6B4A2E")
        emoji(c, "🥔", x - 180, y - 60, 70)
        emoji(c, "🥨", x - 80, y - 60, 70)
        rrect(c, x + 120, y - 75, 110, 36, 10); fill(c, "#2B2B2B")
        for k in range(3):
            c.arc(x + 145 + k * 30, y - 57, 7, 0, 2 * math.pi); fill(c, "#E23B3B" if k == 0 else "#888888")
        text(c, "FLIESENTISCH", x, y + 120, 34, "#FFFFFF", FONT_HEAD)
    scaled(c, x, y, s, d)


def sc_tv(c, S):
    t, a1 = S.t, S.at(1)
    tv(c, W / 2, 620, pop(t, S.at(0, 0.0)), t, 0 if t < a1 + 0.4 else 1)
    fliesentisch(c, W / 2, 970, pop(t, S.at(0, 0.3)))
    alex_bottom(c, S, "happy" if t < a1 + 0.4 else "shock", "idle")


def sc_sidejob(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def panel():
        card(c, W / 2, 650, 920, 520, 1)
        text(c, "NEBENJOB 💼", W / 2, 460, 56, INK, FONT_HEAD)
        text(c, "Erste 100 €", 160, 580, 44, INK, FONT_HEAD, anchor="l")
        text(c, "darf er behalten ✅", 920, 580, 38, "#2FA36B", FONT_HEAD, anchor="r")
        if t > a1:
            text(c, "Alles darüber", 160, 690, 44, INK, FONT_HEAD, anchor="l")
            text(c, "nur ein Teil 📉", 920, 690, 38, "#E23B3B", FONT_HEAD, anchor="r")
        if t > S.at(1, 0.35):
            emoji(c, "🧮", W / 2, 820, 100, rot=math.sin(t * 8) * 0.1)
    scaled(c, W / 2, 650, s, panel)
    nap = t > S.at(1, 0.65)
    if nap:
        for i in range(3):
            u = (t * 0.5 + i / 3) % 1
            emoji(c, "💤", 660 + u * 80, 1230 - u * 180, 60 + i * 8, alpha=1 - u)
    alex_bottom(c, S, "sleepy" if nap else "neutral", "idle")


def sc_family(c, S):
    t, a1, a2 = S.t, S.at(1), S.at(2)
    s = pop(t, S.at(0, 0.0))
    def table():
        for x, sp, nm in ((260, MAMA, None), (540, OMA, "Oma"), (820, OPA, "Opa")):
            ex = "happy" if t < a1 + 0.8 else "neutral"
            person(c, x, 1000, 420, sp, t, ex, blink_seed=x % 7, name=nm)
        rrect(c, 90, 860, 900, 60, 16); fill(c, "#B07A4F")
        rrect(c, 90, 860, 900, 60, 16); c.set_line_width(5); src(c, INK); c.stroke()
        for x, e in ((260, "🍗"), (540, "🥔"), (820, "🥗")):
            emoji(c, e, x, 840, 70)
    scaled(c, W / 2, 800, s, table)
    if t < a1 + 0.1:
        bubble(c, "Und, was machst du gerade beruflich? 😊", 540, 450, pop(t, S.at(0, 0.3)) * out_fade(t, a1),
               tail=(0, 1), size=40, max_w=640)
    elif t < a2 + 0.2:
        bubble(c, "Ich hab morgen frei! 😎", 540, 1080, pop(t, a1 + 0.05) * out_fade(t, a2), tail=(0, 1), size=44)
    silence(c, t, S.at(1, 1.0) + 0.2, x=540, y=470)
    alex_bottom(c, S, "smug" if t < a2 else "neutral", "idle")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du jemanden, der gerade arbeitslos ist?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 920, 170, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 48, 840, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#5FA9B8", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@hat_morgen_frei"
            n = int(clamp((t - S.at(0, 0.55)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 210, 950, 44, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#5FA9B8", "#2FA36B", "#F2B233", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 260 + cc * 280, 500 + r * 230
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 95, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 95, 0, 2 * math.pi); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
                if i < 2:
                    emoji(c, ["🌹", "🛋️"][i], x, y, 100)
                    lab, col = (["GESTERN", "HEUTE ✅"][i], ["#555A66", "#2FA36B"][i])
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


SCENE_DRAW = dict(plan=sc_plan, money1=sc_money1, money2=sc_money2, morning=sc_morning, jobcenter=sc_jobcenter,
                  tv=sc_tv, sidejob=sc_sidejob, family=sc_family, outro=sc_outro)
