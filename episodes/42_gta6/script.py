"""TikTok-Folge: Heute ist Alex ... im GTA VI Fieber. Alltags-Comedy über einen Fan, keine Spielgrafik/Logos nachgebaut.
Gesprochen: „G T A Sechs“. Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), erst nach Freigabe. Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#F07FB0", top_style="tee", pants="#36B5C2", shoes="#FFFFFF")   # Miami-Look
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "IM GTA VI FIEBER.", "im G T A Sechs Fieber.", "im G T A Sechs Fieber!"
INTRO_LEN = 3.3
MUSIC = "groove"
MUSIC_START = 0.0
MUSIC_DB = -15
MUSIC_DUCK_DB = -6
LOUDNESS = -11
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45, lively=True)
MOODS = dict(MOODS_BASE, trailer="hochkonzentriert wie ein Detektiv, dann trocken", sparen="stolz, dann trocken",
             date="verträumt, dann trocken", krank="hustend gespielt, dann trocken", chat="aufgeregt, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"trailer": ["🔍", "🤯", "🚩"], "sparen": ["🐷", "💸", "🚩"], "date": ["🌴", "🙄", "🚩"],
             "krank": ["🤒", "🎮", "🚩"], "chat": ["⏳", "💀", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX…", l1="IM GTA VI", l2="FIEBER", bg="#E0457B", color1="#FFFFFF", accent="#FFE14D",
             pill="#5A0B2B", pill_text="#FFFFFF", expr="happy", pose="hips", prop=None, extras=True, emojis=("🎮", "🌴", "🔥", "🚩"))
INTRO_CFG = dict(icon="🎮", bg="#E0457B", title_lines=["IM GTA VI", "FIEBER."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#FF8A5B", "#FFD6E8"), walls="#FFF0F6", roof="#36B5C2", door="#1F6F8B", lawn="#5DAA5E",
                            accent=("#F07FB0", "#36B5C2"), sun=True),
                 left=("🎮", "GAMING-ZIMMER"), right=("🌴", "MIAMI-VIBES"), door=("NICHT STÖREN:", "TRAILER LÄUFT 🔁"),
                 neon=("NOCH", "X TAGE ⏳", "#FF6FB0"), signs=("Release-Day = Feiertag 🎉", "Trailer zum 300. Mal 🔁"),
                 fly=["🎮", "🌴", "🔥"], burst=["🎮", "🌴", "🔥", "🕹️", "⏳", "🤯", "🏎️", "💸"],
                 extras=[("🕶️", 0, 92, 10), ("🎮", 36, 40, 14)])

SCENES = [
    dict(id="what", bg="#E0457B", clock=None, title="GTA VI FIEBER?", dark=True, lines=[
        ("Alex hat nur noch ein Thema: GTA VI.", "Aleks hat nur noch ein Thema: G T A Sechs."),
        ("Er zählt die Tage bis zum Release. Auf die Sekunde genau.", None),
    ], viz=dict(kind="bars", enter="zoom", head="SEINE GESPRÄCHSTHEMEN", rows=[("GTA VI", 1.0, "100 %", "#E0457B"), ("REST", 0.02, "0 %", "#555A66")],
                pills=[("⏳", "Countdown: läuft 24/7", "#36B5C2"), ("🎮", "Gedanken: nur ein Spiel", "#2B2F3A")])),
    dict(id="trailer", bg="#2B2F4A", clock="02:00", title="DER TRAILER", dark=True, lines=[
        ("Zwei Uhr nachts. Er schaut den Trailer zum dreihundertsten Mal. Bild für Bild.", None),
        ("Er hat eine Theorie: Die Wolke in Sekunde zwölf ist ein Hinweis.", None),
    ], viz=dict(kind="stage", **_BIG, enter="zoom", particles=["🔍", "❓"], box="#1C1C22", head="▶️ TRAILER · 300. MAL", head_col="#E0457B",
                items=[("📺", 280, 640, 140, 0, "bob"), ("🔍", 450, 620, 100, 0, "shake"), ("☁️", 700, 620, 110, 1, "pulse"),
                       ("🧠", 700, 820, 90, 1, "spin")],
                tags=[("BILD FÜR BILD 🔁", "#E0457B", 360, 830), ("„DIE WOLKE IST EIN HINWEIS!“", "#F2B233", 540, 990)],
                fx="shock", move="flicker", alex=("shock", "idle", None))),
    dict(id="krank", bg="#2FA36B", clock="07:00", title="DER PLAN", dark=True, lines=[
        ("Er plant schon jetzt: Am Release-Tag ist er krank. Seit zwei Jahren.", None),
        ("Er übt jeden Morgen seinen Husten. Sein Bro sagt: Bro, das klingt wie ein Seehund.", None),
    ], viz=dict(kind="stage", **_BIG, enter="drop", particles=["🤧", "📅"], box="#E8FFE0", head="📅 RELEASE-TAG", head_col="#2E6B34",
                people=[(TOM, 820, "Tom", "happy", 1)],
                items=[("📅", 270, 620, 110, 0, "bob"), ("🤒", 440, 620, 100, 0, "shake"), ("🦭", 620, 620, 90, 1, "pulse")],
                tags=[("KRANKMELDUNG STEHT 🤒", "#2E6B34", 340, 790), ("„KLINGT WIE 'N SEEHUND“ 🦭", "#E23B3B", 360, 990)],
                fx="shock", move="rumble", alex=("sleepy", "idle", None))),
    dict(id="sparen", bg="#F2B233", clock="12:00", title="DAS SPARSCHWEIN", lines=[
        ("Mittags isst er nur Toast. Er spart für die Konsole.", None),
        ("Und für die Special Edition. Und für den Controller in Pink.", None),
    ], viz=dict(kind="stage", **_BIG, enter="slide_l", particles=["🪙", "💸"], box="#FFF8E1", head="🐷 SPARPLAN", head_col="#A8642E",
                items=[("🍞", 270, 620, 100, 0, "bob"), ("🐷", 450, 640, 130, 0, "pulse"), ("🎮", 680, 620, 100, 1, "spin"),
                       ("💿", 820, 640, 90, 1, "spin")],
                tags=[("MITTAGESSEN: TOAST 🍞", "#A8642E", 360, 820), ("SPECIAL EDITION + PINKER CONTROLLER", "#E0457B", 540, 990)],
                move="bounce", alex=("happy", "idle", None))),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Erst GTA VI, dann leb ich wieder.", "Sein Motto: Erst G T A Sechs, dann leb ich wieder."),
    ], viz=dict(kind="stage", **_BIG, enter="spin", particles=["⏳"], box="#FFF0F6", head="⏳ LEBEN: PAUSIERT", head_col="#E0457B",
                items=[("⏸️", 300, 680, 140, 0, "pulse"), ("➡️", 540, 680, 90, 0, "bob"), ("🎮", 780, 680, 150, 0, "shake")],
                tags=[("ERST DAS SPIEL, DANN DAS LEBEN", "#E0457B", 540, 960)], move="chomp", alex=("smug", "hips", None))),
    dict(id="date", bg="#36B5C2", clock="18:00", title="DAS DATE", lines=[
        ("Abends Date mit Lena. Er erzählt ihr eine Stunde lang von der Spielkarte.", None),
        ("Lena fragt, ob er sie überhaupt mag. Er sagt: Du erinnerst mich an den Strand im Trailer.", None),
    ], viz=dict(kind="stage", **_BIG, enter="slide_r", particles=["🌴", "💤"], box="#E8F7FF", head="🍦 DATE AM SEE", head_col="#1F6F8B",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("🗺️", 280, 620, 110, 0, "shake"), ("⏱️", 440, 620, 90, 0, "spin"), ("🏖️", 620, 620, 90, 1, "pulse")],
                tags=[("60 MIN: DIE SPIELKARTE 🗺️", "#1F6F8B", 360, 780), ("„WIE DER STRAND IM TRAILER“ 🏖️", "#E23B3B", 470, 990)],
                fx="anger", move="wobble", alex=("happy", "idle", None))),
    dict(id="chat", bg="#8E5BE0", clock="23:00", title="DIE BROS", dark=True, lines=[
        ("Nachts schreibt er in den Bro-Chat: Nur noch dreihundertzwölf Tage!", None),
        ("Tom antwortet: Bro, das hast du heute schon elf Mal geschrieben.", None),
    ], viz=dict(kind="messenger", enter="rise", switch=0, list=[],
                chat=dict(name="Die Bros 🎮", col="#3E7BDA", msgs=[(0, True, "NUR NOCH 312 TAGE 🤯🔥", "23:00"),
                                                                 (0, True, "Habt ihr den Trailer gesehen??", "23:00"),
                                                                 (1, False, "Tom: Bro, das schreibst du heute zum 11. Mal 💀", "23:01")]),
                alex=("happy", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du erkennst, dass jemand im GTA VI Fieber ist:", "Woran du erkennst, dass jemand im G T A Sechs Fieber ist:"),
        ("Er analysiert jede Wolke im Trailer.", None),
        ("Seine Krankmeldung steht schon.", None),
        ("Er isst nur Toast. Für die Special Edition.", None),
        ("Und er zählt die Tage. Jeden Tag elf Mal.", None),
    ], viz=dict(kind="signs", slide=True, items=[("Analysiert jede Wolke", "🔍"), ("Krankmeldung steht schon", "🤒"),
                                                 ("Isst nur Toast – spart", "🍞"), ("Countdown 11× am Tag", "⏳")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch jemanden im GTA VI Fieber? Markier sie oder ihn!", "Kennst du auch jemanden im G T A Sechs Fieber? Markier sie oder ihn!"),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch jemanden im GTA VI Fieber?", handle="@gta6_alex", icon="🎮", col="#E0457B")),
]
