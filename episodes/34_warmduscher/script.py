"""TikTok-Folge: Heute ist Alex ... ein Warmduscher. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), erst nach Freigabe. Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#F2B6C8", top_style="hoodie", pants="#9CC0E3", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN WARMDUSCHER.", "ein Warmduscher.", "ein Warmduscher!"
INTRO_LEN = 3.3
MOODS = dict(MOODS_BASE, dusche="vorsichtig, dann trocken", chat="ängstlich, dann trocken",
             park="ungläubig, dann trocken", film="gruselig angespannt, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"dusche": ["🚿", "🥶", "🚩"], "chat": ["🌡️", "🙄", "🚩"], "park": ["🎠", "⛑️", "🚩"], "film": ["💡", "📞", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="WARM-", l2="DUSCHER", bg="#E0703A", color1="#FFFFFF", accent="#FFE14D",
             pill="#7A3414", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🚿", "🧸", "🥶", "🚩"))
INTRO_CFG = dict(icon="🚿", bg="#E0703A", title_lines=["WARMDUSCHER."],
                 house=dict(sky=("#F29A6A", "#FFE6D6"), walls="#FFF5EE", roof="#7A3414", door="#4A1E08", lawn="#5DAA5E",
                            accent=("#F2B6C8", "#7FD0FF"), sun=True),
                 left=("🚿", "NUR 42 °C"), right=("🧸", "KUSCHELTIER"), door=("VORSICHT:", "ZUGLUFT! 🌬️"),
                 neon=("SICHERHEIT", "ZUERST ⛑️", "#FF9A5A"), signs=("Ist das Wasser warm? 🌡️", "Zu gefährlich! ⛑️"),
                 fly=["🚿", "🧸", "⛑️"], burst=["🚿", "🧸", "⛑️", "🌡️", "🧣", "🥶", "🛟", "🫖"],
                 extras=[("🧣", 0, 72, 12), ("🧸", 34, 30, 14)])

_BIG = dict(tag_size=48, head_size=50, item_scale=1.35)
SCENES = [
    dict(id="what", bg="#E0703A", clock=None, title="WAS IST EIN WARMDUSCHER?", dark=True, lines=[
        ("Ein Warmduscher duscht nur warm. Und auch sonst ist ihm alles zu gefährlich.", None),
        ("Schon ein kalter Tropfen ist für ihn eine Mutprobe.", None),
    ], viz=dict(kind="bars", head="WASSER VS. MUT", rows=[("WASSER", 1.0, "42 °C", "#E07A2E"), ("MUT", 0.03, "0 %", "#555A66")],
                pills=[("🚿", "Dusche: exakt 42 °C", "#E07A2E"), ("🧊", "Kaltes Wasser? Niemals!", "#3E7BDA")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Lieber sicher als mutig.", None),
    ], viz=dict(kind="stage", box="#FFF5EE", head="⛑️ SICHERHEIT ZUERST", head_col="#7A3414",
                items=[("⛑️", 300, 680, 150, 0, "bob"), ("🛟", 540, 700, 150, 0, "spin"), ("🧸", 780, 690, 150, 0, "pulse")],
                tags=[("LIEBER SICHER 🛡️", "#7A3414")], move="wobble", alex=("happy", "hips", None), **_BIG)),
    dict(id="dusche", bg="#36B5C2", clock="07:00", title="DIE DUSCHE", lines=[
        ("Sieben Uhr. Er testet das Wasser. Zehn Minuten lang.", None),
        ("Ein Grad zu kalt? Dann wird heute nicht geduscht.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="🚿 BADEZIMMER", head_col="#2B5C66",
                items=[("🚿", 330, 660, 160, 0, "shake"), ("💧", 300, 820, 60, 0, "fly"), ("💧", 370, 840, 60, 0, "fly"),
                       ("🌡️", 620, 680, 130, 0, "pulse"), ("🥶", 800, 690, 130, 1, "shake")],
                tags=[("10 MIN TESTEN ⏱️", "#2B5C66", 400, 950), ("41,9 °C?! 😱", "#3E7BDA", 700, 560)], fx="shock",
                move="rumble", flash="#7FD0FF", alex=("shock", "idle", None), **_BIG)),
    dict(id="chat", bg="#2FA36B", clock="12:00", title="DAS FREIBAD", dark=True, lines=[
        ("Mittags fragt Tom: Kommst du mit ins Freibad?", None),
        ("Er fragt zuerst nach der Wassertemperatur. Dreiundzwanzig Grad? Viel zu kalt.", None),
    ], viz=dict(kind="messenger", switch=0,
                chat=dict(name="Tom", col="#36B5C2", msgs=[(0, False, "Kommst du mit ins Freibad? ☀️🏊", "12:01"),
                                                           (1, True, "Wie warm ist das Wasser? 🌡️", "12:02"),
                                                           (1, False, "23 Grad", "12:02"),
                                                           (1, True, "Viel zu kalt 🥶 Ich bleib daheim", "12:03")]),
                list=[], fx="shock", alex=("sad", "idle", "📱"))),
    dict(id="park", bg="#8E5BE0", clock="16:00", title="FREIZEITPARK", dark=True, lines=[
        ("Nachmittags im Freizeitpark. Die anderen fahren Achterbahn.", None),
        ("Er fährt Kinderkarussell. Mit Gurt und Helm.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🎡 FREIZEITPARK", head_col="#7A3FA8",
                items=[("🎢", 320, 650, 170, 0, "shake"), ("😱", 450, 600, 80, 0, "bob"), ("🎠", 720, 730, 190, 1, "spin"),
                       ("⛑️", 720, 600, 90, 1, "bob")],
                tags=[("ACHTERBAHN? NÖ 🎢", "#E23B3B", 330, 870), ("KARUSSELL + HELM ⛑️", "#7A3FA8", 640, 980)],
                fx="party", move="bounce", alex=("happy", "idle", None), **_BIG)),
    dict(id="film", bg="#2B2F4A", clock="21:00", title="HORRORFILM", dark=True, lines=[
        ("Abends Filmabend. Die anderen wollen einen Horrorfilm.", None),
        ("Er schaut ihn hinter einem Kissen. Mit Licht an. Und Mama am Telefon.", None),
    ], viz=dict(kind="stage", box="#1C1C22", head="🎬 FILMABEND", head_col="#E23B3B",
                items=[("👻", 330, 650, 160, 0, "shake"), ("🔪", 480, 620, 80, 0, "shake"), ("🛋️", 620, 840, 140, 1, "bob"),
                       ("💡", 800, 620, 110, 1, "pulse"), ("📞", 820, 820, 100, 1, "shake")],
                tags=[("LICHT AN 💡", "#F2B233", 760, 560), ("MAMA AM TELEFON 📞", "#E0457B", 540, 980)], fx="shock",
                move="flicker", flash="#FFFFFF", alex=("shock", "idle", "🧸"), **_BIG)),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Warmduscher erkennst:", None),
        ("Er duscht nur bei genau zweiundvierzig Grad.", None),
        ("Er fragt immer zuerst nach der Wassertemperatur.", None),
        ("Er fährt nur Kinderkarussell.", None),
        ("Und Horrorfilme gibt's nur mit Licht an.", None),
    ], viz=dict(kind="signs", items=[("Duscht nur bei 42 °C", "🚿"), ("Fragt nach der Wassertemperatur", "🌡️"),
                                     ("Fährt nur Kinderkarussell", "🎠"), ("Horrorfilm nur mit Licht an", "💡")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Warmduscher? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Warmduscher?", handle="@warmduscher_alex", icon="🚿", col="#E0703A")),
]
