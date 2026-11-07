"""TikTok-Folge: Heute ist Alex ... ein Linken-Wähler. Politische Satire über Klischee-Verhalten (Gegenstück: AfD-Wähler).
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#C0392B", top_style="hoodie", pants="#2B2F3A", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN LINKEN-WÄHLER.", "ein Linken-Wähler.", "ein Linken-Wähler!"
MOODS = dict(MOODS_BASE, plenum="ernst und gewichtig, dann trocken", demo="kämpferisch, dann trocken",
             chat="belehrend, dann trocken", party="eifrig, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"plenum": ["🧻", "😴", "🚩"], "demo": ["🪧", "📦", "🚩"], "chat": ["✊", "💸", "🚩"], "party": ["🎂", "🙉", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="LINKEN-", l2="WÄHLER", bg="#A8232F", color1="#FFFFFF", accent="#FFE14D",
             pill="#5A0E14", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("✊", "🪧", "📱", "🚩"))
INTRO_CFG = dict(icon="✊", bg="#A8232F", title_lines=["LINKEN-WÄHLER."],
                 house=dict(sky=("#D9534F", "#FFE1E1"), walls="#FFF2F2", roof="#5A0E14", door="#3A0A0E", lawn="#5DAA5E",
                            accent=("#E23B3B", "#2FA36B"), sun=True),
                 left=("🪧", "DEMO-SCHILD"), right=("📱", "PRO MAX"), door=("WG-PLENUM", "HEUTE 4 STD"),
                 neon=("EAT THE", "RICH ✊", "#FF5A5A"), signs=("Eigentum ist Diebstahl ✊", "Außer meins 🔒"),
                 fly=["✊", "🪧", "📦"], burst=["✊", "🪧", "📱", "📦", "🧻", "🥛", "📋", "🗣️"],
                 extras=[("✊", 34, 60, 12)])

SCENES = [
    dict(id="what", bg="#A8232F", clock=None, title="WAS IST EIN LINKEN-WÄHLER?", dark=True, lines=[
        ("Ein Linken-Wähler ist gegen Kapitalismus.", None),
        ("Das postet er von seinem brandneuen iPhone.", None),
    ], viz=dict(kind="bars", head="SEINE WERTE", rows=[("ANTI-KAPITAL", 1.0, "100 %", "#C0392B"), ("iPHONE", 1.0, "Pro Max", "#2B2F3A")],
                pills=[("✊", "Gegen Kapitalismus", "#C0392B"), ("📱", "Gepostet vom iPhone", "#2B2F3A")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Eigentum ist Diebstahl. Außer es ist meins.", None),
    ], viz=dict(kind="stage", box="#FFF2F2", head="✊ ALLES GEHÖRT ALLEN", head_col="#A8232F",
                items=[("🌍", 330, 680, 160, 0, "spin"), ("🎮", 720, 660, 120, 0, "bob"), ("🔒", 800, 780, 90, 0, "pulse")],
                tags=[("… AUSSER SEINE PS5 🔒", "#A8232F")], move="wobble", alex=("smug", "hips", None))),
    dict(id="plenum", bg="#D9A441", clock="09:00", title="WG-PLENUM", lines=[
        ("Neun Uhr. WG-Plenum. Thema: Wer kauft Klopapier?", None),
        ("Nach vier Stunden Diskussion gibt es ein Ergebnis: einen Arbeitskreis.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="📋 TAGESORDNUNG: 🧻", head_col="#A8642E",
                people=[(TOM, 820, "Tom", "neutral", 1)],
                items=[("🧻", 330, 660, 140, 0, "bob"), ("🗣️", 520, 640, 110, 0, "shake"), ("⏰", 330, 840, 90, 1, "spin"),
                       ("📋", 560, 840, 100, 1, "pulse")],
                tags=[None, ("4 STD → ARBEITSKREIS 📋", "#A8232F", 540, 980)], fx="anger", move="wobble",
                alex=("happy", "idle", None))),
    dict(id="demo", bg="#C0392B", clock="13:00", title="DIE DEMO", dark=True, lines=[
        ("Mittags auf der Demo ruft er: Eat the rich!", None),
        ("Danach bestellt er beim größten Onlinehändler der Welt. Mit Express-Lieferung.", None),
    ], viz=dict(kind="stage", box="#FFF2F2", head="🪧 DEMO", head_col="#A8232F",
                items=[("🪧", 330, 660, 160, 0, "shake"), ("📢", 520, 620, 100, 0, "pulse"), ("📦", 720, 760, 150, 1, "bob"),
                       ("🚚", 860, 860, 100, 1, "shake")],
                tags=[("EAT THE RICH ✊", "#A8232F", 330, 840), ("EXPRESS 📦", "#F2B233", 720, 980)], fx="shock",
                move="rumble", flash="#FFE14D", alex=("angry", "idle", "📱"))),
    dict(id="chat", bg="#36B5C2", clock="17:00", title="WG-CHAT", lines=[
        ("Siebzehn Uhr. Er erklärt im WG-Chat, wie man richtig gendert.", None),
        ("Dann leiht er sich von Tom zwanzig Euro. Für Bio-Hafermilch.", None),
    ], viz=dict(kind="chat", chat="🏠 WG Rote Zora", bar="#A8232F",
                msgs=[(0, "Alex", "Liebe Mitbewohner*innen ✊ kurze Info …", "#C0392B"),
                      (1, "Alex", "Kann mir wer 20 € leihen? Bio-Hafermilch 🥛", "#C0392B"),
                      (1, "Tom", "Umverteilung, oder was? 💀", "#3E7BDA")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="party", bg="#8E5BE0", clock="20:00", title="GEBURTSTAG", dark=True, lines=[
        ("Abends auf einem Geburtstag erklärt er allen die Welt.", None),
        ("Keiner hat gefragt. Er hört trotzdem nicht auf.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🎂 LENAS GEBURTSTAG", head_col="#7A3FA8",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("🎂", 620, 860, 100, 0, "bob"), ("🗣️", 330, 640, 140, 0, "shake"), ("😴", 820, 560, 80, 1, "fly")],
                tags=[None, ("KEINER HAT GEFRAGT 🙉", "#7A3FA8", 540, 980)], fx="anger", move="wobble",
                alex=("happy", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Linken-Wähler erkennst:", None),
        ("Er ist gegen Kapitalismus. Vom iPhone aus.", None),
        ("Für alles gibt es ein Plenum.", None),
        ("Eigentum ist Diebstahl. Außer seins.", None),
        ("Und er erklärt dir ungefragt die Welt.", None),
    ], viz=dict(kind="signs", items=[("Anti-Kapitalismus vom iPhone", "📱"), ("Plenum für alles", "📋"),
                                     ("Eigentum? Nur seins!", "🔒"), ("Erklärt ungefragt die Welt", "🗣️")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Linken-Wähler? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Linken-Wähler?", handle="@genosse_alex", icon="✊", col="#A8232F")),
]
