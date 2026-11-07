"""TikTok-Folge: Heute ist Alex ... ein Lackaffe. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#FFFFFF", top_style="tee", pants="#E8E2D6", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN LACKAFFE.", "ein Lackaffe.", "ein Lackaffe!"
MOODS = dict(MOODS_BASE, bad="eitel, dann trocken", stadt="cool, dann trocken", fussball="ungläubig, dann trocken",
             chat="lässig, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"bad": ["🧴", "🌬️", "🚩"], "stadt": ["🕶️", "🏷️", "🚩"], "fussball": ["⚽", "👟", "🚩"], "chat": ["💇", "⏰", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="LACKAFFE", bg="#2B9AA8", color1="#FFFFFF", accent="#FFE14D",
             pill="#0E4A54", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("💇", "🕶️", "👟", "🚩"))
INTRO_CFG = dict(icon="💇", bg="#2B9AA8", title_lines=["LACKAFFE."],
                 house=dict(sky=("#4FC3D0", "#E0FAFF"), walls="#FFFFFF", roof="#0E4A54", door="#0A2E36", lawn="#5DAA5E",
                            accent=("#36B5C2", "#E5A50A"), sun=True),
                 left=("🪞", "SPIEGEL 1"), right=("🪞", "SPIEGEL 2"), door=("BITTE NICHT", "ANFASSEN 💇"),
                 neon=("STYLE", "> ALLES ✨", "#5AE8FF"), signs=("Nicht die Haare! 💇", "Achtung, Sneaker! 👟"),
                 fly=["✨", "💇", "🕶️"], burst=["💇", "🕶️", "👟", "🧴", "✨", "🪞", "🏷️", "👔"],
                 extras=[("🕶️", 0, 92, 10), ("✨", 30, 100, 10)])

SCENES = [
    dict(id="what", bg="#2B9AA8", clock=None, title="WAS IST EIN LACKAFFE?", dark=True, lines=[
        ("Ein Lackaffe achtet nur auf sein Äußeres.", None),
        ("Jede Spiegelung ist für ihn ein Spiegel. Sogar Autofenster.", None),
    ], viz=dict(kind="bars", head="AUSSEN VS. INNEN", rows=[("AUSSEHEN", 1.0, "100 %", "#36B5C2"), ("INHALT", 0.04, "…", "#555A66")],
                pills=[("💇", "Styling: 2 Stunden", "#E5A50A"), ("🚗", "Autofenster = Spiegel", "#3E7BDA")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Lieber zu spät und schick als pünktlich und normal.", None),
    ], viz=dict(kind="stage", box="#E0FAFF", head="✨ STYLE-CHECK", head_col="#2B9AA8",
                items=[("👔", 300, 680, 140, 0, "bob"), ("🕶️", 540, 640, 130, 0, "pulse"), ("⏰", 780, 680, 130, 0, "shake")],
                tags=[("SCHICK > PÜNKTLICH ⏰", "#2B9AA8")], move="wobble", alex=("smug", "hips", None))),
    dict(id="bad", bg="#D9A441", clock="07:00", title="IM BAD", lines=[
        ("Sieben Uhr. Eine ganze Tube Haargel. Für eine einzige Frisur.", None),
        ("Bei Wind geht er heute nicht mehr raus.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="🪞 STYLING", head_col="#2B5C66",
                items=[("🧴", 330, 680, 160, 0, "shake"), ("💇", 560, 640, 120, 0, "pulse"), ("🌬️", 780, 760, 140, 1, "shake"),
                       ("🚫", 780, 760, 80, 1, "pulse")],
                tags=[("1 TUBE GEL 🧴", "#2B9AA8", 330, 860), ("WIND = HAUSARREST 🌬️", "#E23B3B", 640, 980)], fx="shock",
                move="wobble", flash="#FFFFFF", alex=("smug", "idle", None))),
    dict(id="stadt", bg="#5B6BC9", clock="11:00", title="IN DER STADT", dark=True, lines=[
        ("Mittags in der Stadt: Sonnenbrille. Auch drinnen im Kaufhaus.", None),
        ("Und auf jedem Teil ist das Markenlogo. Riesig.", None),
    ], viz=dict(kind="stage", box="#F5F5F7", head="🛍️ KAUFHAUS (DRINNEN)", head_col="#2B2F3A",
                items=[("🕶️", 330, 660, 160, 0, "pulse"), ("💡", 560, 600, 80, 0, "bob"), ("👕", 700, 760, 150, 1, "bob"),
                       ("🏷️", 840, 640, 100, 1, "shake")],
                tags=[("DRINNEN?! 🕶️", "#E23B3B", 330, 820), ("LOGO XXL 🏷️", "#2B9AA8", 700, 980)], fx="shock",
                move="wobble", alex=("smug", "hips", None))),
    dict(id="fussball", bg="#2FA36B", clock="15:00", title="FUSSBALL", dark=True, lines=[
        ("Nachmittags spielen die Jungs Fußball.", None),
        ("Er spielt nicht mit. Seine weißen Sneaker könnten dreckig werden.", None),
    ], viz=dict(kind="stage", box="#E8FFE0", floor="#5DAA5E", head="⚽ BOLZPLATZ", head_col="#2E6B34",
                people=[(TOM, 800, "Tom", "happy", 1)],
                items=[("⚽", 540, 760, 100, 0, "spin"), ("🥅", 300, 680, 140, 0, "bob"), ("👟", 420, 880, 110, 1, "pulse"),
                       ("✨", 500, 840, 60, 1, "spin")],
                tags=[None, ("SNEAKER: SAUBER ✨👟", "#2B9AA8", 540, 980)], fx="anger", move="wobble",
                alex=("smug", "shrug", None))),
    dict(id="chat", bg="#36B5C2", clock="20:00", title="DAS WARTEN", lines=[
        ("Abends fragt Mia: Kommst du? Wir warten.", None),
        ("Er schreibt: Fünf Minuten, noch die Haare. Das schrieb er vor einer Stunde.", None),
    ], viz=dict(kind="chat", chat="💬 Mia", bar="#25A366",
                msgs=[(0, "Mia", "Kommst du? Wir warten 😤", "#3E7BDA"),
                      (1, "Alex", "5 Min! Noch die Haare 💇", "#2B9AA8"),
                      (1, "Mia", "Das hast du vor 1 Std. geschrieben 💀", "#3E7BDA")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Lackaffen erkennst:", None),
        ("Haargel kauft er im Großpack.", None),
        ("Er trägt Sonnenbrille. Auch drinnen.", None),
        ("Das Logo muss immer riesig sein.", None),
        ("Und seine Schuhe dürfen nie dreckig werden.", None),
    ], viz=dict(kind="signs", items=[("Haargel im Großpack", "🧴"), ("Sonnenbrille drinnen", "🕶️"),
                                     ("Logo immer XXL", "🏷️"), ("Schuhe nie dreckig", "👟")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Lackaffen? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Lackaffen?", handle="@style_alex", icon="💇", col="#2B9AA8")),
]
