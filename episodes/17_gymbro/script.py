"""TikTok-Folge: Heute ist Alex ... ein Gymbro. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#2B2F3A", top_style="tee", pants="#5C5C66", shoes="#FFFFFF")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN GYMBRO.", "ein Gymbro.", "ein Gymbro!"
MOODS = dict(MOODS_BASE, morgen="motiviert, dann trocken", gym="ungläubig amüsiert", mittag="pedantisch, dann trocken",
             chat="stolz, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"morgen": ["🥚", "🤢", "🚩"], "gym": ["🏋️", "📱", "🚩"], "mittag": ["⚖️", "🍰", "🚩"], "chat": ["💪", "🍕", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="GYMBRO", bg="#C0392B", color1="#FFFFFF", accent="#FFE14D",
             pill="#5A1A14", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("💪", "🥤", "🏋️", "🚩"))
INTRO_CFG = dict(icon="💪", bg="#C0392B", title_lines=["GYMBRO."],
                 house=dict(sky=("#E5534B", "#FFE1D6"), walls="#F5F5F7", roof="#2B2F3A", door="#1C1C22", lawn="#5DAA5E",
                            accent=("#E23B3B", "#2B2F3A"), sun=True),
                 left=("🏋️", "HOME-GYM"), right=("🥤", "SHAKE-BAR"), door=("NO PAIN", "NO GAIN 💪"),
                 neon=("PROTEIN", "💪 24/7", "#FF5A5A"), signs=("Beintag? Nö 🦵", "Bro, Protein? 🥤"),
                 fly=["💪", "🥤", "🥚"], burst=["💪", "🏋️", "🥤", "🥚", "🍗", "🔥", "📸", "⚖️"],
                 extras=[("🥤", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#C0392B", clock=None, title="WAS IST EIN GYMBRO?", dark=True, lines=[
        ("Ein Gymbro wohnt praktisch im Fitnessstudio.", None),
        ("Und jedes Gespräch endet irgendwann bei Protein.", None),
    ], viz=dict(kind="bars", head="SEIN SPEISEPLAN", rows=[("PROTEIN", 1.0, "300 g", "#E23B3B"), ("GEMÜSE", 0.03, "1 Erbse", "#2FA36B")],
                pills=[("🏋️", "Zuhause: Fitnessstudio", "#2B2F3A"), ("🥤", "Thema: Protein. Immer.", "#3E7BDA")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Brusttag nie auslassen. Beintag? Kenn ich nicht.", None),
    ], viz=dict(kind="stage", box="#F5F5F7", head="📅 TRAININGSPLAN", head_col="#2B2F3A",
                items=[("💪", 320, 650, 170, 0, "pulse"), ("✅", 320, 840, 90, 0, "bob"), ("🦵", 760, 650, 150, 0, "shake"),
                       ("❌", 760, 840, 100, 0, "pulse")],
                tags=[("BEINTAG: GESCHWÄNZT 🦵", "#E23B3B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="morgen", bg="#D9A441", clock="05:00", title="FRÜHSTÜCK", lines=[
        ("Fünf Uhr. Zwölf rohe Eier. Aus einem Glas.", None),
        ("Danach ein Shake. Und noch ein Shake. Zur Sicherheit.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="🍳 FRÜHSTÜCK", head_col="#A8642E",
                items=[("🥚", 260, 620, 80, 0, "bob"), ("🥚", 360, 620, 80, 0, "bob"), ("🥚", 460, 620, 80, 0, "bob"),
                       ("🥛", 360, 820, 130, 0, "shake"), ("🥤", 680, 760, 120, 1, "pulse"), ("🥤", 840, 760, 120, 1, "pulse")],
                tags=[("12 EIER 🥚", "#E07A2E", 360, 960), ("SHAKE × 2 🥤", "#3E7BDA", 760, 960)], fx="shock",
                move="wobble", flash="#FFFFFF", alex=("happy", "idle", "🥤"))),
    dict(id="gym", bg="#5B6BC9", clock="09:00", title="IM GYM", dark=True, lines=[
        ("Neun Uhr. Er belegt drei Geräte gleichzeitig.", None),
        ("Und filmt jeden einzelnen Satz für TikTok.", None),
    ], viz=dict(kind="stage", box="#EEF0F4", floor="#8C8C96", head="🏋️ FITNESSSTUDIO", head_col="#2B2F3A",
                people=[(TOM, 840, "Tom", "neutral", 0)],
                items=[("🏋️", 230, 700, 110, 0, "shake"), ("🚴", 420, 700, 110, 0, "bob"), ("🧺", 610, 700, 90, 0, "bob"),
                       ("📱", 420, 880, 100, 1, "shake"), ("🔴", 500, 830, 40, 1, "pulse")],
                tags=[("3 GERÄTE BELEGT 😤", "#E23B3B", 420, 560), ("● REC", "#E23B3B", 420, 980)], fx="anger",
                move="rumble", alex=("smug", "hips", "📱"))),
    dict(id="mittag", bg="#2FA36B", clock="13:00", title="MITTAGESSEN", dark=True, lines=[
        ("Mittags Reis mit Hähnchen. Abgewogen auf das Gramm.", None),
        ("Lena bietet ihm Kuchen an. Er hält ihr einen Vortrag über Makros.", None),
    ], viz=dict(kind="stage", box="#E8FFE0", head="🍽️ MEAL PREP", head_col="#2E6B34",
                people=[(LENA, 790, "Lena", "happy", 1)],
                items=[("⚖️", 300, 760, 140, 0, "bob"), ("🍚", 250, 620, 80, 0, "bob"), ("🍗", 350, 620, 80, 0, "bob"),
                       ("🍰", 680, 840, 90, 1, "bob"), ("📊", 520, 620, 110, 1, "shake")],
                tags=[("200,0 g ⚖️", "#2E6B34", 300, 900), ("MAKROS!!! 📊", "#E23B3B", 540, 980)], fx="anger",
                move="wobble", alex=("smug", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="20:00", title="GRUPPENCHAT", lines=[
        ("Abends im Gruppenchat. Er schickt ein Spiegel-Selfie. Oberkörperfrei.", None),
        ("Die Frage war eigentlich, wer Pizza will.", None),
    ], viz=dict(kind="chat", chat="🍕 Freitagabend", bar="#25A366",
                msgs=[(0, "Tom", "Wer will heute Pizza? 🍕", "#3E7BDA"),
                      (0, "Alex", "📸 *Pump-Selfie* 💪🔥 #gains", "#E23B3B"),
                      (1, "Tom", "Bro. Die Frage war PIZZA 💀", "#3E7BDA")],
                fx="shock", alex=("smug", "hips", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Gymbro erkennst:", None),
        ("Er redet nur über Protein.", None),
        ("Er filmt jedes Training.", None),
        ("Er wiegt sein Essen ab.", None),
        ("Und er schwänzt den Beintag.", None),
    ], viz=dict(kind="signs", items=[("Redet nur über Protein", "🥤"), ("Filmt jedes Training", "📱"),
                                     ("Wiegt sein Essen ab", "⚖️"), ("Schwänzt den Beintag", "🦵")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Gymbro? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Gymbro?", handle="@gymbro_alex", icon="💪", col="#C0392B")),
]
