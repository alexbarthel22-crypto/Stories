"""TikTok-Folge: Heute ist Alex ... ein Fremdgeher. Alltags-Comedy, jugendfrei.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#2B2F3A", top_style="hoodie", pants="#2F3B52", shoes="#FFFFFF")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN FREMDGEHER.", "ein Fremdgeher.", "ein Fremdgeher!"
MOODS = dict(MOODS_BASE, handy="flirtend, dann erschrocken", ausrede="unschuldig, dann trocken",
             kino="verschmitzt, dann trocken", check="nervös, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"handy": ["😘", "😱", "🚩"], "ausrede": ["🦷", "🏊", "🚩"], "kino": ["🎬", "🍿", "🚩"], "check": ["📱", "👭", "🚩"]}
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
        ("Sein Handy liegt immer mit dem Display nach unten.", None),
    ], viz=dict(kind="bars", head="SEINE BEZIEHUNG", rows=[("FREUNDIN", 1.0, "1", "#E0457B"), ("„COUSINEN“", 1.0, "12", "#8E5BE0")],
                pills=[("📱", "Display: immer unten", "#2B2F3A"), ("🔒", "Code: geändert. Wieder.", "#E23B3B")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Was sie nicht weiß, macht sie nicht heiß.", None),
    ], viz=dict(kind="stage", box="#FFF0F3", head="🤫 PSST …", head_col="#8C1C3A",
                items=[("🤫", 540, 660, 200, 0, "pulse"), ("🙈", 280, 700, 120, 0, "shake"), ("🔥", 800, 700, 110, 0, "pulse")],
                tags=[("SIE WEISS NIX 🤫", "#8C1C3A")], move="wobble", alex=("smug", "hips", None))),
    dict(id="handy", bg="#36B5C2", clock="09:00", title="GUTEN MORGEN", lines=[
        ("Neun Uhr. Er schreibt drei Mädchen gleichzeitig: Guten Morgen, Schatz.", None),
        ("Bei einer vertippt er sich. Mit dem falschen Namen.", None),
    ], viz=dict(kind="chat", chat="💬 Chats (3)", bar="#25A366",
                msgs=[(0, "Alex → Lena", "Guten Morgen, Schatz 😘", "#E0457B"),
                      (0, "Alex → Mia", "Guten Morgen, Schatz 😘", "#E0457B"),
                      (1, "Lena", "Wer ist JANA??? 😡", "#3E7BDA")],
                fx="shock", alex=("shock", "idle", "📱"))),
    dict(id="ausrede", bg="#C0392B", clock="13:00", title="DIE AUSREDE", dark=True, lines=[
        ("Mittags sagt er Lena: Ich bin beim Zahnarzt.", None),
        ("Dann sieht Lena ihn in Mias Story. Im Freibad.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="📱 MIAS STORY", head_col="#2B5C66",
                people=[(LENA, 790, "Lena", "neutral", 1)],
                items=[("🦷", 300, 640, 130, 0, "bob"), ("🏊", 400, 830, 120, 1, "shake"), ("☀️", 260, 830, 90, 1, "spin")],
                tags=[("„ZAHNARZT“ 🦷", "#3E7BDA", 300, 560), ("FREIBAD?! 🏊", "#E23B3B", 540, 980)], fx="anger",
                move="wobble", flash="#FF3B3B", alex=("shock", "idle", None))),
    dict(id="kino", bg="#5B6BC9", clock="18:00", title="IM KINO", dark=True, lines=[
        ("Achtzehn Uhr. Kino mit Mia.", None),
        ("Zwanzig Uhr. Gleicher Film. Mit Jana. Er tut überrascht vom Ende.", None),
    ], viz=dict(kind="stage", box="#1C1C22", head="🎬 KINO · SAAL 3", head_col="#E23B3B",
                items=[("🎬", 540, 620, 130, 0, "pulse"), ("🍿", 300, 820, 100, 0, "bob"), ("🍿", 780, 820, 100, 1, "bob"),
                       ("😮", 540, 830, 90, 1, "shake")],
                tags=[("18:00 MIT MIA 🎬", "#8E5BE0", 300, 960), ("20:00 MIT JANA 🎬", "#E0457B", 780, 960)],
                fx="shock", move="flicker", alex=("smug", "idle", "🍿"))),
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
        ("Er ändert ständig seinen Code.", None),
        ("Er hat erstaunlich viele Cousinen.", None),
        ("Und er kennt jedes Film-Ende schon.", None),
    ], viz=dict(kind="signs", items=[("Handy: Display nach unten", "📱"), ("Ständig neuer Code", "🔒"),
                                     ("Sehr viele „Cousinen“", "👭"), ("Kennt jedes Film-Ende", "🎬")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Fremdgeher? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Fremdgeher?", handle="@schatz_alex", icon="💔", col="#8C1C3A")),
]
