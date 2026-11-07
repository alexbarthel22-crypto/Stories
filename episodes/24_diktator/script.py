"""TikTok-Folge: Heute ist Alex ... ein Diktator. Alltags-Comedy: der WG-Diktator.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#3F4A2E", top_style="tee", pants="#2B2F3A", shoes="#1C1C22")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN DIKTATOR.", "ein Diktator.", "ein Diktator!"
MOODS = dict(MOODS_BASE, morgen="militärisch streng, dann trocken", wahl="feierlich, dann trocken",
             chat="herrisch, dann trocken", abend="pompös, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"morgen": ["📜", "😤", "🚩"], "wahl": ["🗳️", "🙄", "🚩"], "chat": ["📢", "🚫", "🚩"], "abend": ["📺", "🗿", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="DIKTATOR", bg="#5A2A1E", color1="#FFFFFF", accent="#FFE14D",
             pill="#2E140E", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("👑", "📜", "📢", "🚩"))
INTRO_CFG = dict(icon="📜", bg="#5A2A1E", title_lines=["DIKTATOR."],
                 house=dict(sky=("#8A4A3A", "#F5E1D6"), walls="#F5EEE6", roof="#3F4A2E", door="#2B2F3A", lawn="#5DAA5E",
                            accent=("#C0392B", "#F2B233"), sun=True),
                 left=("🗿", "SEINE STATUE"), right=("📢", "DURCHSAGE"), door=("WG-REGELN:", "ICH ENTSCHEIDE"),
                 neon=("ABSTIMMUNG?", "NEIN. 🚫", "#FF6A3A"), signs=("Ich entscheide! 📜", "Widerstand zwecklos 🚫"),
                 fly=["📜", "👑", "📢"], burst=["📜", "👑", "📢", "🗿", "🚫", "🎖️", "🏰", "🗳️"],
                 extras=[("🎖️", -14, 70, 10), ("👑", 0, 112, 14)])

SCENES = [
    dict(id="what", bg="#5A2A1E", clock=None, title="WAS IST EIN DIKTATOR?", dark=True, lines=[
        ("Ein Diktator bestimmt alles. Alleine.", None),
        ("In seiner WG hat er sich selbst zum Chef ernannt. Gefragt hat er niemanden.", None),
    ], viz=dict(kind="bars", head="WER BESTIMMT IN DER WG?", rows=[("ALEX", 1.0, "100 %", "#C0392B"), ("DIE ANDEREN", 0.0, "0 %", "#555A66")],
                pills=[("👑", "Chef: Alex (selbst ernannt)", "#C0392B"), ("🗳️", "Abstimmung: nie", "#2B2F3A")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Demokratie ist super. Solange ich gewinne.", None),
    ], viz=dict(kind="stage", box="#F5EEE6", head="📜 VERFASSUNG DER WG", head_col="#5A2A1E",
                items=[("📜", 330, 680, 170, 0, "bob"), ("🏆", 760, 660, 150, 0, "pulse"), ("🗳️", 560, 840, 90, 0, "shake")],
                tags=[("GEWINNER: IMMER ALEX 🏆", "#C0392B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="morgen", bg="#D9A441", clock="07:00", title="DIE NEUEN REGELN", lines=[
        ("Sieben Uhr. Er hängt die neuen WG-Regeln an den Kühlschrank.", None),
        ("Regel eins: Die Fernbedienung gehört Alex. Regel zwei: Siehe Regel eins.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="📜 WG-GESETZ NR. 47", head_col="#5A2A1E",
                people=[(TOM, 800, "Tom", "neutral", 1)],
                items=[("🧊", 330, 700, 160, 0, "bob"), ("📜", 330, 660, 110, 0, "shake"), ("📺", 560, 620, 90, 1, "bob"),
                       ("🎮", 560, 780, 90, 1, "pulse")],
                tags=[None, ("REGEL 2: SIEHE REGEL 1", "#C0392B", 540, 980)], fx="anger", move="wobble",
                alex=("smug", "hips", None))),
    dict(id="wahl", bg="#5B6BC9", clock="12:00", title="DIE ABSTIMMUNG", dark=True, lines=[
        ("Mittags gibt's eine Abstimmung: Was wird gekocht?", None),
        ("Drei Stimmen für Pasta, eine für Pizza. Gewonnen hat: Pizza.", None),
    ], viz=dict(kind="stage", box="#EEF0F4", head="🗳️ WAHL: MITTAGESSEN", head_col="#2B2F3A",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("🍝", 300, 640, 110, 0, "bob"), ("🍕", 560, 640, 110, 0, "bob"), ("🗳️", 430, 820, 110, 0, "shake")],
                tags=[("🍝 3 : 1 🍕", "#3E7BDA", 430, 760), ("SIEGER: 🍕 (ALEX)", "#C0392B", 540, 980)], fx="shock",
                move="wobble", flash="#FFE14D", alex=("smug", "hips", None))),
    dict(id="chat", bg="#36B5C2", clock="17:00", title="DER WG-CHAT", lines=[
        ("Siebzehn Uhr. Im WG-Chat dürfen nur noch Admins schreiben.", None),
        ("Der einzige Admin: Alex. Er schickt eine Durchsage nach der anderen.", None),
    ], viz=dict(kind="chat", chat="🏰 WG Alexanderplatz", bar="#5A2A1E",
                msgs=[(0, "System", "Nur Admins dürfen schreiben 🔒", "#555A66"),
                      (1, "Alex 👑", "📢 DURCHSAGE: Bad putzt heute Tom.", "#C0392B"),
                      (1, "Alex 👑", "📢 DURCHSAGE: Widerspruch verboten.", "#C0392B")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="abend", bg="#8E5BE0", clock="20:00", title="DAS DENKMAL", dark=True, lines=[
        ("Abends stellt er eine Statue von sich ins Wohnzimmer.", None),
        ("Lena wollte da eigentlich das Sofa hinstellen.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🏛️ WOHNZIMMER", head_col="#7A3FA8",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("🗿", 420, 700, 220, 0, "pulse"), ("✨", 300, 580, 70, 0, "spin"), ("✨", 540, 580, 70, 0, "spin"),
                       ("🛋️", 660, 880, 110, 1, "shake")],
                tags=[None, ("UND DAS SOFA?! 🛋️", "#E23B3B", 540, 980)], fx="anger", move="wobble",
                alex=("happy", "hips", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Diktator erkennst:", None),
        ("Er hat sich selbst zum Chef ernannt.", None),
        ("Abstimmungen gewinnt immer er.", None),
        ("Im Gruppenchat darf nur er schreiben.", None),
        ("Und im Wohnzimmer steht seine Statue.", None),
    ], viz=dict(kind="signs", items=[("Selbst ernannter Chef", "👑"), ("Gewinnt jede Abstimmung", "🗳️"),
                                     ("Nur er darf schreiben", "📢"), ("Statue im Wohnzimmer", "🗿")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Diktator? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Diktator?", handle="@chef_alex", icon="📜", col="#5A2A1E")),
]
