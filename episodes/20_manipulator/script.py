"""TikTok-Folge: Heute ist Alex ... ein Manipulator. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#4A2E6B", top_style="tee", pants="#2F3B52", shoes="#FFFFFF")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN MANIPULATOR.", "ein Manipulator.", "ein Manipulator!"
MOODS = dict(MOODS_BASE, referat="theatralisch seufzend, dann trocken", mittag="mitleidig gespielt, dann trocken",
             chat="gespielt traurig, dann trocken", streit="ungläubig, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"referat": ["😮‍💨", "📚", "🚩"], "mittag": ["🥺", "🍔", "🚩"], "chat": ["🥺", "🏃", "🚩"], "streit": ["🎂", "🙇", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="MANIPU-", l2="LATOR", bg="#4A2E6B", color1="#FFFFFF", accent="#FFE14D",
             pill="#2A1640", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🎻", "🧠", "🎣", "🚩"))
INTRO_CFG = dict(icon="🎻", bg="#4A2E6B", title_lines=["MANIPULATOR."],
                 house=dict(sky=("#7A4FB8", "#EEE1FF"), walls="#F6F0FF", roof="#2A1640", door="#1C0E2E", lawn="#5DAA5E",
                            accent=("#8E5BE0", "#F2B233"), sun=True),
                 left=("🎣", "KÖDER"), right=("🎻", "MITLEID"), door=("DEINE IDEE", "(MEINE) 🧠"),
                 neon=("DU WILLST", "DAS DOCH 😇", "#B98CFF"), signs=("Schon gut … 🥺", "War doch deine Idee 🧠"),
                 fly=["🥺", "🎻", "🧠"], burst=["🎻", "🧠", "🎣", "🥺", "🎭", "🕸️", "😇", "🪄"],
                 extras=[("🎻", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#4A2E6B", clock=None, title="WAS IST EIN MANIPULATOR?", dark=True, lines=[
        ("Ein Manipulator bringt dich dazu, Dinge zu tun, die du gar nicht willst.", None),
        ("Und am Ende denkst du, es war deine Idee.", None),
    ], viz=dict(kind="bars", head="WESSEN SCHULD?", rows=[("SEINE", 0.0, "0 %", "#555A66"), ("DEINE", 1.0, "100 %", "#E23B3B")],
                pills=[("🧠", "Deine Idee? Seine.", "#4A2E6B"), ("🎻", "Mitleid: auf Knopfdruck", "#E07A2E")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Ich frag nie. Ich warte, bis du's anbietest.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="🎣 DIE ANGEL", head_col="#2B5C66",
                items=[("🎣", 340, 640, 170, 0, "shake"), ("🐟", 720, 820, 130, 0, "bob"), ("🪝", 520, 760, 80, 0, "bob")],
                tags=[("DU BEISST AN 🎣", "#4A2E6B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="referat", bg="#D9A441", clock="08:00", title="DAS REFERAT", lines=[
        ("Acht Uhr. Er hat keine Lust auf das Referat.", None),
        ("Also seufzt er so lange, bis Tom anbietet, alles zu machen.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="📚 GRUPPENARBEIT", head_col="#A8642E",
                people=[(TOM, 790, "Tom", "neutral", 1)],
                items=[("📚", 330, 640, 130, 0, "bob"), ("😮‍💨", 300, 830, 100, 1, "pulse"), ("📝", 790, 560, 80, 1, "shake")],
                tags=[("SEUFZER × 37 😮‍💨", "#E07A2E", 330, 960), ("TOM MACHT ALLES 📚", "#3E7BDA", 760, 960)],
                fx="anger", move="wobble", alex=("sad", "idle", None))),
    dict(id="mittag", bg="#2FA36B", clock="12:00", title="MITTAGESSEN", dark=True, lines=[
        ("Mittags hat er Hunger. Aber kein Geld.", None),
        ("Er sagt: Ach, ich ess heute halt nichts. Lena kauft ihm sofort ein Menü.", None),
    ], viz=dict(kind="stage", box="#E8FFE0", head="🍔 FASTFOOD", head_col="#2E6B34",
                people=[(LENA, 790, "Lena", "sad", None)],
                items=[("🥺", 330, 640, 140, 0, "pulse"), ("🍔", 360, 860, 110, 1, "bob"), ("🍟", 480, 860, 90, 1, "bob"),
                       ("🥤", 600, 860, 90, 1, "bob")],
                tags=[None, ("😢 → 🍔 GRATIS", "#2E6B34", 480, 980)], move="wobble", alex=("sad", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="17:00", title="DIE ABSAGE", lines=[
        ("Siebzehn Uhr. Mia sagt ab.", None),
        ("Er schreibt: Kein Problem, ich bin eh immer allein. Zwei Minuten später steht sie vor der Tür.", None),
    ], viz=dict(kind="chat", chat="💬 Mia", bar="#25A366",
                msgs=[(0, "Mia", "Sorry, kann heute nicht 🙏", "#3E7BDA"),
                      (1, "Alex", "Kein Problem. Bin eh immer allein 🥺", "#4A2E6B"),
                      (1, "Mia", "Bin in 2 Min da!!! 🏃‍♀️", "#3E7BDA")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="streit", bg="#8E5BE0", clock="20:00", title="DER STREIT", dark=True, lines=[
        ("Abends gibt es Streit. Er hat Lenas Geburtstag vergessen.", None),
        ("Am Ende entschuldigt sich Lena. Bei ihm.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🎂 LENAS GEBURTSTAG", head_col="#7A3FA8",
                people=[(LENA, 780, "Lena", "angry", None)],
                items=[("🎂", 330, 650, 140, 0, "shake"), ("🔄", 520, 820, 110, 1, "spin"), ("🙇‍♀️", 780, 560, 80, 1, "pulse")],
                tags=[("VERGESSEN 🎂", "#E23B3B", 330, 800), ("LENA: „SORRY …“ 🙇‍♀️", "#7A3FA8", 540, 980)], fx="shock",
                move="wobble", flash="#FFE14D", alex=("smug", "hips", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Manipulator erkennst:", None),
        ("Er seufzt so lange, bis du es machst.", None),
        ("Er hat Mitleid auf Knopfdruck.", None),
        ("Seine Ideen werden plötzlich deine.", None),
        ("Und am Ende entschuldigst du dich.", None),
    ], viz=dict(kind="signs", items=[("Seufzt, bis du's machst", "😮‍💨"), ("Mitleid auf Knopfdruck", "🥺"),
                                     ("Seine Idee wird deine", "🧠"), ("Am Ende: DU sagst sorry", "🙇")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Manipulator? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Manipulator?", handle="@mitleid_alex", icon="🎻", col="#4A2E6B")),
]
