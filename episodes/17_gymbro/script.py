"""TikTok-Folge: Heute ist Alex ... ein Gymbro. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), tighten 1.08 0.22 + match_level wie Folge 1. Freigegeben vom Nutzer."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#1C1C22", top_style="tank", pants="#555A66", shoes="#39FF6A", pump=2.0, headband="#E23B3B")   # übertrieben sportlich   # sportlich: Tanktop, dicke Arme
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN GYMBRO.", "ein Gymbro.", "ein Gymbro!"
MOODS = dict(MOODS_BASE, katze="todernst wie ein Fakt, dann trocken", morgen="motiviert, dann trocken", gym="ungläubig amüsiert", mittag="pedantisch, dann trocken",
             chat="stolz, dann trocken")
SHUFFLE = SHUFFLE_BASE
INTRO_LEN = 3.3
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45)
GEMINI_LINE_MOOD = {"morgen_1": "ironisch und augenzwinkernd; 'Für die Gains' übertrieben bedeutungsvoll und spöttisch gesprochen"}
REACTIONS = {"katze": ["🐈", "😱", "🚩"], "morgen": ["🥚", "🤢", "🚩"], "gym": ["🏋️", "📱", "🚩"], "mittag": ["⚖️", "🍰", "🚩"], "chat": ["💪", "🍕", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="GYMBRO", bg="#E8742B", color1="#FFFFFF", accent="#FFE14D",
             pill="#7A3414", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("💪", "🥤", "🏋️", "🚩"))
INTRO_CFG = dict(icon="💪", bg="#E8742B", title_lines=["GYMBRO."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#F29A5A", "#FFE8D6"), walls="#F5F5F7", roof="#2B2F3A", door="#1C1C22", lawn="#5DAA5E",
                            accent=("#E8742B", "#2B2F3A"), sun=True),
                 left=("🏋️", "HOME-GYM"), right=("🥤", "SHAKE-BAR"), door=("NO PAIN", "NO GAIN 💪"),
                 neon=("PROTEIN", "💪 24/7", "#FF5A5A"), signs=("Leg Day? Nö 🦵", "Bro, Protein? 🥤"),
                 fly=["💪", "🥤", "🥚"], burst=["💪", "🏋️", "🥤", "🥚", "🍗", "🔥", "📸", "⚖️"],
                 extras=[("🥤", 36, 30, 14)])

SCENES = [
    dict(id="what", bg="#E8742B", clock=None, title="WAS IST EIN GYMBRO?", dark=True, lines=[
        ("Ein Gymbro wohnt praktisch im Fitnessstudio.", None),
        ("Und jedes Gespräch endet irgendwann bei Protein.", None),
    ], viz=dict(kind="bars", head="SEIN SPEISEPLAN", rows=[("PROTEIN", 1.0, "300 g", "#E23B3B"), ("GEMÜSE", 0.03, "1 Erbse", "#2FA36B")],
                pills=[("🏋️", "Zuhause: Fitnessstudio", "#2B2F3A"), ("🥤", "Thema: Protein. Immer.", "#3E7BDA")])),
    dict(id="katze", bg="#8E5BE0", clock=None, title="DIE KATZE", dark=True, lines=[
        ("Laut ihm hat eine Katze sechshundert Gramm Eiweiß.", None),
        ("Deshalb verstecken seine Freunde ihre Katze, wenn er zu Besuch kommt. Damit er sie nicht isst.", None),
    ], viz=dict(kind="stage", **_BIG, box="#F3EAFE", head="🧮 PROTEIN-RECHNER", head_col="#7A3FA8",
                people=[(LENA, 820, "Lena", "shock", None)],
                items=[("🐈", 260, 600, 120, 0, "bob"), ("💪", 470, 590, 80, 0, "pulse"), ("📦", 470, 880, 100, 1, "shake"),
                       ("🐾", 610, 900, 60, 1, "bob")],
                tags=[("🐈 = 600 g EIWEISS", "#E8742B", 290, 760), ("KATZE IN SICHERHEIT 🫣", "#7A3FA8", 420, 990)],
                fx="shock", move="rumble", alex=("smug", "hips", None))),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Arme trainieren. Jeden Tag. Bald sieht er aus wie ein Dreieck. Leg Day? Kenn ich nicht.", None),
    ], viz=dict(kind="stage", **_BIG, box="#F5F5F7", head="📅 TRAININGSPLAN", head_col="#2B2F3A",
                items=[("💪", 320, 650, 170, 0, "pulse"), ("✅", 320, 840, 90, 0, "bob"), ("🦵", 760, 650, 150, 0, "shake"),
                       ("❌", 760, 840, 100, 0, "pulse"), ("🔻", 540, 700, 120, 0, "pulse")],
                tags=[("LEG DAY: GESCHWÄNZT 🦵", "#E23B3B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="morgen", bg="#D9A441", clock="05:00", title="FRÜHSTÜCK", lines=[
        ("Fünf Uhr. Zwölf rohe Eier. Aus einem Glas.", None),
        ("Danach ein Shake. Und ein Haufen Supplements. Für die Gains.", None),
    ], viz=dict(kind="stage", **_BIG, box="#FFF4E0", head="🍳 FRÜHSTÜCK", head_col="#A8642E",
                items=[("🥚", 260, 620, 80, 0, "bob"), ("🥚", 360, 620, 80, 0, "bob"), ("🥚", 460, 620, 80, 0, "bob"),
                       ("🥛", 260, 820, 120, 0, "shake"), ("🥤", 620, 640, 110, 1, "pulse"), ("💊", 760, 620, 70, 1, "spin"),
                       ("💊", 860, 680, 70, 1, "spin"), ("🧴", 780, 780, 80, 1, "bob"), ("💊", 900, 820, 60, 1, "spin")],
                tags=[("12 EIER 🥚", "#E07A2E", 560, 800), ("„FÜR DIE GAINS“ 💊", "#3E7BDA", 540, 990)], fx="shock",
                move="wobble", flash="#FFFFFF", alex=("happy", "idle", "🥤"))),
    dict(id="gym", bg="#5B6BC9", clock="09:00", title="IM GYM", dark=True, lines=[
        ("Neun Uhr. Er belegt drei Geräte gleichzeitig.", None),
        ("Und filmt jeden einzelnen Satz für TikTok.", None),
    ], viz=dict(kind="stage", **_BIG, box="#EEF0F4", floor="#8C8C96", head="🏋️ FITNESSSTUDIO", head_col="#2B2F3A",
                people=[(TOM, 840, "Tom", "neutral", 0)],
                items=[("🏋️", 230, 700, 110, 0, "shake"), ("🚴", 420, 700, 110, 0, "bob"), ("🧺", 610, 700, 90, 0, "bob"),
                       ("📱", 420, 880, 100, 1, "shake"), ("🔴", 500, 830, 40, 1, "pulse")],
                tags=[("3 GERÄTE BELEGT 😤", "#E23B3B", 420, 560), ("● REC", "#E23B3B", 420, 980)], fx="anger",
                move="rumble", alex=("smug", "hips", "📱"))),
    dict(id="mittag", bg="#2FA36B", clock="13:00", title="MITTAGESSEN", dark=True, lines=[
        ("Mittags Reis mit Hähnchen. Abgewogen auf das Gramm.", None),
        ("Lena bietet ihm Kuchen an. Er hält ihr einen Vortrag über Makros.", None),
    ], viz=dict(kind="stage", **_BIG, box="#E8FFE0", head="🍽️ MEAL PREP", head_col="#2E6B34",
                people=[(LENA, 790, "Lena", "happy", 1)],
                items=[("⚖️", 300, 760, 140, 0, "bob"), ("🍚", 250, 620, 80, 0, "bob"), ("🍗", 350, 620, 80, 0, "bob"),
                       ("🍰", 680, 840, 90, 1, "bob"), ("📊", 520, 620, 110, 1, "shake")],
                tags=[("200,0 g ⚖️", "#2E6B34", 300, 900), ("MAKROS!!! 📊", "#E23B3B", 540, 980)], fx="anger",
                move="wobble", alex=("smug", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="20:00", title="GRUPPENCHAT", lines=[
        ("Abends im Gruppenchat. Er schickt ein Spiegel-Selfie. Oberkörperfrei.", None),
        ("Die Frage war eigentlich, wer Pizza will.", None),
    ], viz=dict(kind="messenger", switch=0, list=[],
                chat=dict(name="Freitagabend 🍕", col="#E8742B", msgs=[(0, False, "Tom: Wer will heute Pizza? 🍕", "19:58"),
                                                                       (0, True, "📸 [Spiegel-Selfie oben ohne] 💪🔥", "20:01"),
                                                                       (1, False, "Tom: Bro. Die Frage war PIZZA 💀", "20:02")]),
                alex=("smug", "hips", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Gymbro erkennst:", None),
        ("Er redet nur über Protein.", None),
        ("Er filmt jedes Training.", None),
        ("Er wiegt sein Essen ab.", None),
        ("Und er schwänzt den Leg Day.", None),
    ], viz=dict(kind="signs", items=[("Redet nur über Protein", "🥤"), ("Filmt jedes Training", "📱"),
                                     ("Wiegt sein Essen ab", "⚖️"), ("Schwänzt den Leg Day", "🦵")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Gymbro? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Gymbro?", handle="@gymbro_alex", icon="💪", col="#C0392B")),
]
