"""TikTok-Folge: Heute ist Alex ... ein Lustmolch. Jugendfreie Alltags-Comedy: flirtet mit allem und jedem, nur Cringe.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), erst nach Freigabe. Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#C2185B", top_style="tee", pants="#2F3B52", shoes="#FFFFFF", chain="#F2C94C")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
MIA = person_spec(14, girl=True, top="#F07FB0", hair="#5A3A22", skin="#F1C9A8")
ROLE, ROLE_TTS, ROLE_SAY = "EIN LUSTMOLCH.", "ein Lustmolch.", "ein Lustmolch!"
INTRO_LEN = 3.3
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45)
MOODS = dict(MOODS_BASE, navi="schleimig flirtend, dann trocken", lehrerin="ungläubig, dann trocken",
             bro="empört, dann trocken", gym="selbstverliebt, dann trocken", zwinker="übertrieben verführerisch, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"navi": ["🗺️", "😳", "🚩"], "lehrerin": ["👩‍🏫", "💀", "🚩"], "bro": ["💬", "🙄", "🚩"],
             "gym": ["🏋️", "😬", "🚩"], "zwinker": ["😉", "🤨", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="LUST-", l2="MOLCH", bg="#7B2FBE", color1="#FFFFFF", accent="#FFE14D",
             pill="#3A1260", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🦎", "😏", "💋", "🚩"))
INTRO_CFG = dict(icon="🦎", bg="#7B2FBE", title_lines=["LUSTMOLCH."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#A66BE0", "#F1E1FF"), walls="#FBF5FF", roof="#3A1260", door="#2A0C46", lawn="#5DAA5E",
                            accent=("#E0457B", "#F2B233"), sun=True),
                 left=("😏", "HEY DU"), right=("💋", "KUSS-MUND"), door=("NA, DU?", "😉"),
                 neon=("FLIRTEN", "MIT ALLEM 😏", "#C59BFF"), signs=("Na, Süße? 😏", "Bist du WLAN? 📶"),
                 fly=["😏", "💋", "🦎"], burst=["🦎", "😏", "💋", "😉", "🌹", "💘", "👀", "🔥"],
                 extras=[("🌹", 36, 40, 13)])

SCENES = [
    dict(id="what", bg="#7B2FBE", clock=None, title="WAS IST EIN LUSTMOLCH?", dark=True, lines=[
        ("Ein Lustmolch flirtet mit allem, was nicht bei drei auf dem Baum ist.", None),
        ("Und er hält jeden seiner Sprüche für unwiderstehlich.", None),
    ], viz=dict(kind="bars", enter="zoom", head="FLIRT VS. ERFOLG", rows=[("FLIRTS", 1.0, "247 heute", "#E0457B"), ("ERFOLG", 0.02, "0", "#555A66")],
                pills=[("😏", "Ziel: alle", "#E0457B"), ("🙈", "Cringe-Level: unendlich", "#2B2F3A")])),
    dict(id="navi", bg="#E0457B", clock="08:00", title="DAS NAVI", dark=True, lines=[
        ("Acht Uhr, in der Bahn. Er flirtet mit der Navi-Stimme auf seinem Handy.", None),
        ("Sie sagt: Bitte wenden. Er sagt: Für dich wende ich alles, Baby.", None),
    ], viz=dict(kind="stage", **_BIG, enter="drop", box="#FFF0F6", head="🗺️ NAVI-STIMME", head_col="#C2185B",
                items=[("📱", 280, 640, 120, 0, "shake"), ("🗺️", 460, 640, 100, 0, "bob"),
                       ("😘", 720, 650, 110, 1, "pulse")],
                tags=[("„BITTE WENDEN“", "#2B2F3A", 400, 800), ("„FÜR DICH WENDE ICH ALLES“ 😏", "#E0457B", 540, 990)],
                move="bounce", alex=("smug", "idle", "📱"))),
    dict(id="bro", bg="#36B5C2", clock="10:00", title="DER BRO", lines=[
        ("In der Pause zeigt sein Bro Tom ihm ein Foto von seiner neuen Freundin.", None),
        ("Alex schreibt ihr sofort auf Insta: Na, Süße? Was macht so jemand wie du mit Tom?", None),
    ], viz=dict(kind="messenger", enter="slide_r", switch=1,
                list=[(0, "Bro Tom 🤝", "📸 Das ist Mia 😍 meine Freundin", "09:58", 1, "#36B5C2"),
                      (0, "Die Bros 🍻", "Tom: Bro, Finger weg 😤", "10:05", 3, "#3E7BDA")],
                chat=dict(name="mia.xo ✨", col="#F07FB0", msgs=[(1, True, "Na, Süße? 😏", "10:01"),
                                                              (1, True, "Was macht so jemand wie du mit Tom? 🌹", "10:01"),
                                                              (1, False, "Ich zeig das Tom 💀", "10:02")]),
                alex=("smug", "idle", "📱"))),
    dict(id="lehrerin", bg="#D9A441", clock="11:00", title="DIE REFERENDARIN", lines=[
        ("Elf Uhr. Neue Referendarin in Bio.", None),
        ("Er meldet sich: Frau Weber, Sie sind die schönste Zelle im ganzen Organismus.", None),
    ], viz=dict(kind="stage", **dict(_BIG, tag_size=44), enter="slide_l", box="#E8FFE0", head="🧬 BIO · 9B", head_col="#2E6B34",
                people=[(MIA, 820, "Fr. Weber", "shock", None)],
                items=[("🦠", 260, 620, 100, 0, "spin"), ("🔬", 420, 630, 100, 0, "bob"), ("🙋", 620, 870, 90, 1, "shake")],
                tags=[("„DIE SCHÖNSTE ZELLE“ 💘", "#E0457B", 340, 780), ("NACHSITZEN 📝", "#2B2F3A", 330, 990)],
                fx="shock", move="rumble", alex=("smug", "idle", None))),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Ein Korb ist auch nur eine Einladung.", None),
    ], viz=dict(kind="stage", **_BIG, enter="spin", box="#F1E1FF", head="🧺 KORB = EINLADUNG", head_col="#7B2FBE",
                items=[("🧺", 300, 680, 160, 0, "bob"), ("➡️", 540, 680, 100, 0, "pulse"), ("💌", 780, 680, 150, 0, "shake")],
                tags=[("247 KÖRBE, 0 AUFGEGEBEN 💪", "#E0457B", 540, 960)], move="chomp", alex=("smug", "hips", None))),
    dict(id="gym", bg="#E8742B", clock="17:00", title="IM GYM", dark=True, lines=[
        ("Nachmittags im Gym. Er stöhnt bei jeder Wiederholung extra laut.", None),
        ("Damit Lena am Laufband auch ja hinschaut. Sie macht die Musik lauter.", None),
    ], viz=dict(kind="stage", **_BIG, enter="rise", box="#FFF0E6", floor="#8C8C96", head="🏋️ FITNESSSTUDIO", head_col="#A8642E",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("🏋️", 280, 640, 120, 0, "shake"), ("🔊", 460, 620, 90, 0, "pulse"), ("🎧", 660, 640, 90, 1, "bob")],
                tags=[("„UUUH! AAAH!“ 💪", "#E8742B", 360, 800), ("MUSIK: 100 % 🎧", "#2B2F3A", 470, 990)],
                fx="shock", move="rumble", alex=("smug", "idle", None))),
    dict(id="zwinker", bg="#8E5BE0", clock="20:00", title="DER ZWINKER", dark=True, lines=[
        ("Abends auf der Party zwinkert er jedem Mädchen zu.", None),
        ("Eins fragt, ob er was im Auge hat. Er sagt: Ja, dich.", None),
    ], viz=dict(kind="stage", **_BIG, enter="flip", box="#F3EAFE", head="🎉 HOUSEPARTY", head_col="#7A3FA8",
                people=[(MIA, 820, "Mia", "neutral", 1)],
                items=[("😉", 280, 640, 130, 0, "pulse"), ("😉", 460, 640, 100, 0, "pulse"),
                       ("🤨", 620, 600, 80, 1, "bob")],
                tags=[("ZWINKERT 37× 😉", "#7A3FA8", 360, 820), ("„JA, DICH.“ 😏", "#E0457B", 470, 990)],
                move="flicker", alex=("smug", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Lustmolch erkennst:", None),
        ("Er flirtet sogar mit dem Navi.", None),
        ("Er schreibt die Freundin vom Bro an.", None),
        ("Er stöhnt im Gym extra laut.", None),
        ("Und ein Korb ist für ihn eine Einladung.", None),
    ], viz=dict(kind="signs", slide=True, items=[("Flirtet sogar mit dem Navi", "🗺️"), ("Schreibt die Freundin vom Bro an", "💬"),
                                                 ("Stöhnt im Gym extra laut", "🏋️"), ("Korb = Einladung", "🧺")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Lustmolch? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Lustmolch?", handle="@lustmolch_alex", icon="🦎", col="#7B2FBE")),
]
