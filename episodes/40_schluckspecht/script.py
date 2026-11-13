"""TikTok-Folge: Heute ist Alex ... ein Schluckspecht. Alex hier klar erwachsen (Anfang 20, WG/Kneipe) wegen Alkohol-Thema.
Alltags-Comedy, nur Freunde/Bros, kein Verherrlichen. Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), tighten 1.08 0.22 + match_level. Freigegeben vom Nutzer."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#3E5C9A", top_style="hoodie", pants="#2F3B52", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN SCHLUCKSPECHT.", "ein Schluckspecht.", "ein Schluckspecht!"
INTRO_LEN = 3.3
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45)
MOODS = dict(MOODS_BASE, rest="verkatert, dann trocken", pfand="stolz, dann trocken", party="unschuldig tuend, dann trocken",
             nureins="gemütlich, dann trocken", chat="gerührt und übertrieben emotional, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"rest": ["🪟", "🤢", "🚩"], "pfand": ["♻️", "🪙", "🚩"], "party": ["🥂", "😳", "🚩"], "nureins": ["🍺", "⏰", "🚩"], "chat": ["🥹", "💀", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="SCHLUCK-", l2="SPECHT", bg="#C98E25", color1="#FFFFFF", accent="#FFE14D",
             pill="#5A3E06", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🍺", "🐦", "🥂", "🚩"))
INTRO_CFG = dict(icon="🍺", bg="#C98E25", title_lines=["SCHLUCKSPECHT."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#E5A84A", "#FFF0D6"), walls="#FFF6E6", roof="#7A4A1E", door="#4A2A10", lawn="#5DAA5E",
                            accent=("#F2C94C", "#7A4A1E"), sun=True),
                 left=("🍺", "STAMMTISCH"), right=("♻️", "PFAND-LAGER"), door=("NUR NOCH", "EINS 🍺"),
                 neon=("PROST", "24/7 🍻", "#FFC85A"), signs=("Nur noch eins! 🍺", "Wasser? Langweilig 💧"),
                 fly=["🍺", "🥂", "🫧"], burst=["🍺", "🍻", "🥂", "🐦", "🫧", "♻️", "🪙", "🎉"],
                 extras=[("🍺", 36, 40, 14), ("🐦", -36, 70, 11)])

SCENES = [
    dict(id="what", bg="#C98E25", clock=None, title="WAS IST EIN SCHLUCKSPECHT?", dark=True, lines=[
        ("Ein Schluckspecht trinkt alles, was nicht bei drei leer ist.", None),
        ("Sein Lieblingssatz: Nur noch eins. Gemeint sind zwölf.", None),
    ], viz=dict(kind="bars", enter="drop", head="GEPLANT VS. GETRUNKEN", rows=[("GEPLANT", 0.08, "1", "#2FA36B"), ("GETRUNKEN", 1.0, "12", "#E07A2E")],
                pills=[("🍺", "„Nur noch eins“", "#E07A2E"), ("💧", "Wasser: kennt er nicht", "#3E7BDA")])),
    dict(id="rest", bg="#5B6BC9", clock="08:00", title="RESTALKOHOL", dark=True, lines=[
        ("Acht Uhr, Berufsschule. Er kommt mit Restalkohol in den Unterricht.", None),
        ("Der Lehrer reißt sofort alle Fenster auf. Sein Bro sagt: Bro, du riechst wie eine Kneipe.", None),
    ], viz=dict(kind="stage", **_BIG, enter="drop", box="#EEF0FF", head="📚 BERUFSSCHULE · 1. STUNDE", head_col="#3E4A9C",
                people=[(TOM, 820, "Tom", "neutral", 1)],
                items=[("😵‍💫", 270, 620, 110, 0, "shake"), ("🍺", 430, 620, 80, 0, "bob"), ("🪟", 600, 620, 90, 1, "pulse"),
                       ("💨", 600, 760, 70, 1, "fly")],
                tags=[("RESTALKOHOL 🍺", "#3E4A9C", 360, 760), ("„DU RIECHST WIE 'NE KNEIPE“", "#E23B3B", 430, 990)],
                fx="shock", move="rumble", alex=("sleepy", "idle", None))),
    dict(id="pfand", bg="#2FA36B", clock="10:00", title="PFANDAUTOMAT", dark=True, lines=[
        ("Zehn Uhr. Er bringt seine Pfandflaschen weg. Mit dem Einkaufswagen.", None),
        ("Hinter ihm die Schlange: zwanzig Leute. Der Automat: voll.", None),
    ], viz=dict(kind="stage", **_BIG, enter="slide_l", box="#E8FFE0", head="♻️ PFANDAUTOMAT", head_col="#2E6B34",
                items=[("🛒", 280, 640, 130, 0, "shake"), ("🍾", 440, 620, 90, 0, "bob"), ("🍾", 520, 640, 90, 0, "bob"),
                       ("🧍", 650, 860, 70, 1, "bob"), ("🧍", 740, 860, 70, 1, "bob"), ("🧍", 830, 860, 70, 1, "bob")],
                tags=[("87 FLASCHEN ♻️", "#2E6B34", 360, 800), ("AUTOMAT: VOLL 🚫", "#E23B3B", 400, 990)],
                fx="shock", move="rumble", alex=("happy", "idle", None))),
    dict(id="party", bg="#8E5BE0", clock="18:00", title="DIE GLÄSER", dark=True, lines=[
        ("Abends Geburtstag bei Lena. Wer kurz auf Toilette geht, findet sein Glas leer.", None),
        ("Alex sagt: Ich dachte, das braucht keiner mehr.", None),
    ], viz=dict(kind="stage", **_BIG, enter="zoom", box="#F3EAFE", head="🎂 LENAS GEBURTSTAG", head_col="#7A3FA8",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("🥂", 260, 620, 100, 0, "bob"), ("🍷", 400, 620, 100, 0, "bob"), ("🚾", 580, 620, 90, 0, "pulse"),
                       ("🫗", 620, 870, 90, 1, "shake")],
                tags=[("ALLE GLÄSER: LEER 🫗", "#7A3FA8", 340, 790), ("„BRAUCHT DOCH KEINER“ 🤷", "#E23B3B", 380, 990)],
                fx="anger", move="bounce", alex=("smug", "idle", None))),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Wasser ist zum Duschen da.", None),
    ], viz=dict(kind="stage", **_BIG, enter="spin", box="#FFF6E6", head="💧 WASSER?", head_col="#3E7BDA",
                items=[("🚿", 300, 680, 150, 0, "bob"), ("✅", 300, 860, 80, 0, "pulse"), ("🥛", 760, 680, 130, 0, "shake"),
                       ("❌", 760, 860, 90, 0, "pulse")],
                tags=[("WASSER = NUR ZUM DUSCHEN", "#3E7BDA", 540, 990)], move="chomp", alex=("smug", "hips", None))),
    dict(id="nureins", bg="#7A4A1E", clock="22:00", title="NUR NOCH EINS", dark=True, lines=[
        ("Zweiundzwanzig Uhr in der Kneipe. Er sagt zu Tom: Nur noch eins.", None),
        ("Drei Uhr nachts. Der Wirt stellt schon die Stühle hoch.", None),
    ], viz=dict(kind="stage", **_BIG, enter="flip", box="#FFF0E0", head="🍺 STAMMKNEIPE", head_col="#7A4A1E",
                people=[(TOM, 820, "Tom", "sleepy", 1)],
                items=[("🍺", 280, 620, 110, 0, "bob"), ("🕙", 450, 620, 90, 0, "spin"), ("🪑", 600, 860, 90, 1, "shake")],
                tags=[("22:00 „NUR NOCH EINS“", "#7A4A1E", 360, 780), ("03:00 – STÜHLE HOCH 🪑", "#E23B3B", 360, 990)],
                fx="shock", move="wobble", alex=("happy", "idle", "🍺"))),
    dict(id="chat", bg="#36B5C2", clock="23:59", title="DER GRUPPENCHAT", lines=[
        ("Auf dem Heimweg schreibt er in den Gruppenchat.", None),
        ("Bros, ich lieb euch so sehr. Vierzehn Sprachnachrichten. Jede fünf Minuten.", None),
    ], viz=dict(kind="messenger", enter="rise", switch=0, list=[],
                chat=dict(name="Die Bros 🍻", col="#3E7BDA", msgs=[(0, True, "Brooos ich lieb euch so sehr 🥹🍻❤️", "23:58"),
                                                                 (1, True, "🎤 Sprachnachricht · 5:02", "23:59"),
                                                                 (1, True, "🎤 Sprachnachricht · 4:58 (13 weitere)", "23:59"),
                                                                 (1, False, "Tom: Bro, geh schlafen 💀", "23:59")]),
                alex=("happy", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Schluckspecht erkennst:", None),
        ("Morgens sitzt er mit Restalkohol im Unterricht.", None),
        ("Sein Nur noch eins dauert bis drei Uhr.", None),
        ("Volle Gläser sind bei ihm nie sicher.", None),
        ("Und nachts kommen Sprachnachrichten voller Liebe.", None),
    ], viz=dict(kind="signs", slide=True, items=[("Restalkohol im Unterricht", "😵‍💫"), ("„Nur noch eins“ = 3 Uhr", "🍺"),
                                                 ("Kein Glas ist sicher", "🥂"), ("Nachts Liebes-Sprachis", "🎤")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Schluckspecht? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Schluckspecht?", handle="@schluckspecht_alex", icon="🍺", col="#C98E25")),
]
