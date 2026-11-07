"""TikTok-Folge: Heute ist Alex ... ein Fremdgeher. Alltags-Comedy, jugendfrei.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#2B2F3A", top_style="hoodie", pants="#2F3B52", shoes="#FFFFFF")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN FREMDGEHER.", "ein Fremdgeher.", "ein Fremdgeher!"
MOODS = dict(MOODS_BASE, mama="verschwörerisch, dann trocken", ego="ehrlich, dann trocken", handy="flirtend, dann erschrocken", ausrede="unschuldig, dann trocken",
             kino="verschmitzt, dann trocken", check="nervös, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
INTRO_LEN = 3.3   # kürzere Pause nach der Verkündung
REACTIONS = {"mama": ["📞", "🤫", "🚩"], "ego": ["🪫", "❤️", "🚩"], "handy": ["😘", "😱", "🚩"], "ausrede": ["🦷", "🏊", "🚩"], "kino": ["🎬", "🍿", "🚩"], "check": ["📱", "👭", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="FREMD-", l2="GEHER", bg="#8C1C3A", color1="#FFFFFF", accent="#FFE14D",
             pill="#4A0E1E", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("📱", "🤫", "💔", "🚩"))
INTRO_CFG = dict(icon="💔", bg="#8C1C3A", title_lines=["FREMDGEHER."],
                 house=dict(sky=("#C93A5E", "#FFE1E8"), walls="#FFF0F3", roof="#5A1426", door="#3A0A18", lawn="#5DAA5E",
                            accent=("#E0457B", "#2B2F3A"), sun=True),
                 left=("📱", "DISPLAY UNTEN"), right=("🔒", "NEUER CODE"), door=("BITTE NICHT", "STÖREN 🤫"),
                 neon=("SCHATZ?", "WELCHE? 💔", "#FF5A7A"), signs=("Das ist meine Cousine 👭", "Akku war leer 🪫"),
                 fly=["💔", "📱", "🤫"], burst=["💔", "📱", "🤫", "🔒", "🌹", "😘", "🎬", "👭"],
                 extras=[("📱", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#8C1C3A", clock=None, title="WAS IST EIN FREMDGEHER?", dark=True, lines=[
        ("Ein Fremdgeher hat eine Freundin. Und nebenbei noch ein paar andere.", None),
        ("Und er denkt eher mit der Hose als mit dem Kopf.", None),
    ], viz=dict(kind="bars", head="WOMIT ER DENKT", rows=[("KOPF 🧠", 0.1, "10 %", "#555A66"), ("HOSE 👖", 0.9, "90 %", "#E0457B")],
                pills=[("📱", "Display: immer unten", "#2B2F3A"), ("🔒", "Code: geändert. Wieder.", "#E23B3B")])),
    dict(id="handy", bg="#36B5C2", clock="09:00", title="GUTEN MORGEN", lines=[
        ("Neun Uhr. Er schreibt drei Mädchen gleichzeitig: Guten Morgen, Schatz.", None),
        ("Bei einer vertippt er sich. Mit dem falschen Namen.", None),
    ], viz=dict(kind="messenger", switch=1,
                list=[(0, "Lena ❤️", "Du: Guten Morgen, Schatz 😘", "09:01", 0, "#46B39A"),
                      (0, "Mia", "Du: Guten Morgen, Schatz 😘", "09:01", 0, "#F07FB0"),
                      (0, "Jana", "Du: Guten Morgen, Schatz 😘", "09:02", 0, "#F2B233")],
                chat=dict(name="Lena ❤️", col="#46B39A", msgs=[(1, True, "Guten Morgen, Jana 😘", "09:03"),
                                                               (1, False, "Wer ist JANA??? 😡", "09:03")]),
                fx="shock", alex=("shock", "idle", "📱"))),
    dict(id="ausrede", bg="#C0392B", clock="13:00", title="DIE AUSREDE", dark=True, lines=[
        ("Mittags sagt er Lena: Ich bin beim Zahnarzt.", None),
        ("Dann sieht Lena ihn in Mias Story. Im Freibad.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="📱 MIAS STORY", head_col="#2B5C66",
                people=[(LENA, 790, "Lena", "neutral", 1)],
                items=[("🦷", 300, 640, 130, 0, "bob"), ("🏊", 400, 830, 120, 1, "shake"), ("☀️", 260, 830, 90, 1, "spin")],
                tags=[("„ZAHNARZT“ 🦷", "#3E7BDA", 300, 560), ("FREIBAD?! 🏊", "#E23B3B", 540, 980)], fx="anger",
                move="wobble", flash="#FF3B3B", alex=("shock", "idle", None))),
    dict(id="mama", bg="#3E7BDA", clock="15:00", title="MAMA RUFT AN", dark=True, lines=[
        ("Nachmittags ruft Mama an. Zum fünften Mal heute. Mama heißt eigentlich Jana.", None),
        ("Und damit keiner was merkt, hat er gleich drei Handys.", None),
    ], viz=dict(kind="stage", box="#EAF2FF", head="📞 EINGEHENDER ANRUF", head_col="#2B2F3A",
                items=[("📱", 330, 680, 170, 0, "shake"), ("👩", 520, 640, 100, 0, "bob"), ("📱", 620, 820, 110, 1, "bob"),
                       ("📱", 740, 820, 110, 1, "shake"), ("📱", 860, 820, 110, 1, "bob")],
                tags=[("„MAMA“ = JANA 🤫", "#E0457B", 400, 560), ("HANDY 1 · 2 · 3 📱", "#2B2F3A", 740, 980)],
                fx="shock", move="rumble", alex=("smug", "idle", "📱"))),
    dict(id="kino", bg="#5B6BC9", clock="18:00", title="IM KINO", dark=True, lines=[
        ("Achtzehn Uhr. Kino mit Mia.", None),
        ("Zwanzig Uhr. Gleicher Film. Mit Jana. Er tut überrascht vom Ende.", None),
    ], viz=dict(kind="stage", box="#1C1C22", head="🎬 KINO · SAAL 3", head_col="#E23B3B",
                items=[("🎬", 540, 620, 130, 0, "pulse"), ("🍿", 300, 820, 100, 0, "bob"), ("🍿", 780, 820, 100, 1, "bob"),
                       ("😮", 540, 830, 90, 1, "shake")],
                tags=[("18:00 MIT MIA 🎬", "#8E5BE0", 300, 960), ("20:00 MIT JANA 🎬", "#E0457B", 780, 960)],
                fx="shock", move="flicker", alex=("smug", "idle", "🍿"))),
    dict(id="ego", bg="#E07A2E", clock="21:00", title="DIE BESTÄTIGUNG", dark=True, lines=[
        ("Dabei hat er eigentlich kaum Selbstbewusstsein.", None),
        ("Er braucht jedes Herz und jedes Kompliment. Von möglichst vielen.", None),
    ], viz=dict(kind="stage", box="#FFF0E6", head="🪫 SELBSTBEWUSSTSEIN", head_col="#A8642E",
                items=[("🪫", 330, 680, 170, 0, "shake"), ("❤️", 600, 620, 90, 1, "fly"), ("❤️", 720, 680, 90, 1, "fly"),
                       ("💬", 840, 620, 90, 1, "pulse"), ("😍", 680, 820, 90, 1, "bob")],
                tags=[("NUR 5 % 🪫", "#E23B3B", 330, 860), ("MEHR LIKES! MEHR HERZEN! ❤️", "#E0457B", 600, 980)],
                fx="love", move="wobble", alex=("sad", "idle", "📱"))),
    dict(id="check", bg="#8E5BE0", clock="22:00", title="DER HANDY-CHECK", dark=True, lines=[
        ("Abends nimmt Lena sein Handy.", None),
        ("Er sagt: Das sind alles meine Cousinen. Alle zwölf.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="📱 KONTAKTE", head_col="#7A3FA8",
                people=[(LENA, 780, "Lena", "neutral", 1)],
                items=[("📱", 330, 660, 150, 0, "shake"), ("👭", 330, 860, 110, 1, "pulse")],
                tags=[None, ("12 „COUSINEN“ 👀", "#E23B3B", 400, 980)], fx="anger", move="rumble", flash="#FF3B3B",
                bubbles=[None, "Alles Cousinen! 😅"], alex=("smug", "shrug", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Fremdgeher erkennst:", None),
        ("Sein Handy liegt immer mit dem Display nach unten.", None),
        ("Frauen speichert er als Mama ein.", None),
        ("Er hat mehrere Handys.", None),
        ("Und er braucht ständig Bestätigung von anderen.", None),
    ], viz=dict(kind="signs", items=[("Handy: Display nach unten", "📱"), ("Frauen als „Mama“ gespeichert", "👩"),
                                     ("Mehrere Handys", "📲"), ("Braucht ständig Bestätigung", "❤️")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Fremdgeher? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Fremdgeher?", handle="@schatz_alex", icon="💔", col="#8C1C3A")),
]
