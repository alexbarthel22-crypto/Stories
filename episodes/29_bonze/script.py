"""TikTok-Folge: Heute ist Alex ... ein Bonze. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#1C1C22", top_style="tee", pants="#2B2F3A", shoes="#8A5A2B")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
BUTLER = person_spec(66, top="#1C1C22", hair="#888888")
KELLNER = person_spec(41, top="#FFFFFF", hair="#2B1A10")
ROLE, ROLE_TTS, ROLE_SAY = "EIN BONZE.", "ein Bonze.", "ein Bonze!"
MOODS = dict(MOODS_BASE, fruehstueck="snobistisch, dann trocken", park="angeberisch, dann trocken",
             chat="herablassend, dann trocken", essen="großkotzig, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"fruehstueck": ["🥐", "✨", "🚩"], "park": ["🏎️", "🅿️", "🚩"], "chat": ["🚲", "💀", "🚩"], "essen": ["💳", "🪙", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="BONZE", bg="#B8860B", color1="#FFFFFF", accent="#FFE14D",
             pill="#3A2A06", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("💰", "💎", "🏎️", "🚩"))
INTRO_CFG = dict(icon="💰", bg="#B8860B", title_lines=["BONZE."],
                 house=dict(sky=("#E5B53A", "#FFF6D6"), walls="#FFFFFF", roof="#1C1C22", door="#B8860B", lawn="#5DAA5E",
                            accent=("#E5A50A", "#1C1C22"), sun=True),
                 left=("💎", "TRESOR"), right=("🍾", "CHAMPAGNER"), door=("PRIVAT.", "NUR VIPS 💎"),
                 neon=("GELD", "SPIELT KEINE ROLLE", "#FFD24A"), signs=("War nicht teuer 💸", "Kauf's dir halt! 🛍️"),
                 fly=["💰", "💎", "💸"], burst=["💰", "💎", "💸", "🏎️", "🍾", "🛥️", "⌚", "🛍️"],
                 extras=[("⌚", -30, 52, 10), ("🕶️", 0, 92, 10)])

SCENES = [
    dict(id="what", bg="#B8860B", clock=None, title="WAS IST EIN BONZE?", dark=True, lines=[
        ("Ein Bonze hat viel Geld. Und das soll auch jeder sehen.", None),
        ("Sein Lieblingswort: teuer.", None),
    ], viz=dict(kind="bars", head="SEIN KONTO VS. SEINE BESCHEIDENHEIT", rows=[("GELD", 1.0, "viel", "#E5A50A"), ("DEMUT", 0.0, "0", "#555A66")],
                pills=[("⌚", "Uhr: teurer als dein Auto", "#8E5BE0"), ("🛥️", "Hobby: Yacht", "#3E7BDA")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Wer billig kauft, kauft zweimal. Ich kauf einfach alles.", None),
    ], viz=dict(kind="stage", box="#FFF6D6", head="🛍️ SHOPPING", head_col="#B8860B",
                items=[("🛍️", 300, 680, 150, 0, "bob"), ("🛍️", 460, 700, 130, 0, "bob"), ("💰", 720, 660, 170, 0, "pulse"),
                       ("💸", 600, 600, 80, 0, "fly")],
                tags=[("ALLES. KAUFEN. 💸", "#B8860B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="fruehstueck", bg="#D9A441", clock="09:00", title="FRÜHSTÜCK", lines=[
        ("Neun Uhr. Ein Croissant mit Blattgold.", None),
        ("Der Butler muss es ihm vorschneiden.", None),
    ], viz=dict(kind="stage", box="#FFFDF5", head="🥐 FRÜHSTÜCK À LA BONZE", head_col="#B8860B",
                people=[(BUTLER, 790, "Butler", "neutral", None)],
                items=[("🥐", 360, 700, 160, 0, "pulse"), ("✨", 300, 620, 70, 0, "spin"), ("✨", 440, 620, 70, 0, "spin"),
                       ("🔪", 560, 820, 90, 1, "shake"), ("🍾", 560, 640, 90, 0, "bob")],
                tags=[("BLATTGOLD ✨", "#B8860B", 360, 860), ("BUTLER SCHNEIDET 🔪", "#2B2F3A", 540, 980)], fx="party",
                move="wobble", flash="#FFE14D", alex=("smug", "idle", None))),
    dict(id="park", bg="#C0392B", clock="13:00", title="DER PARKPLATZ", dark=True, lines=[
        ("Mittags parkt er seinen Sportwagen. Quer über drei Parkplätze.", None),
        ("Und lässt den Motor laufen. Damit ihn auch alle hören.", None),
    ], viz=dict(kind="stage", box="#E6E6EA", floor="#8C8C96", head="🅿️ PARKPLATZ", head_col="#2B2F3A",
                items=[("🅿️", 260, 620, 90, 0, "bob"), ("🅿️", 540, 620, 90, 0, "bob"), ("🅿️", 820, 620, 90, 0, "bob"),
                       ("🏎️", 540, 820, 230, 0, "shake"), ("💨", 300, 880, 90, 1, "fly"), ("🔊", 800, 820, 90, 1, "pulse")],
                tags=[None, ("VROOOM!!! 🔊", "#E23B3B", 540, 980)], fx="anger", move="rumble",
                alex=("smug", "hips", "🔑"))),
    dict(id="chat", bg="#36B5C2", clock="17:00", title="DER CHAT", lines=[
        ("Siebzehn Uhr. Tom erzählt, dass er auf ein neues Fahrrad spart.", None),
        ("Er antwortet: Warum sparen? Kauf's dir doch einfach.", None),
    ], viz=dict(kind="chat", chat="💬 Tom", bar="#25A366",
                msgs=[(0, "Tom", "Spare grad auf ein neues Fahrrad 🚲", "#3E7BDA"),
                      (1, "Alex 💎", "Warum sparen? Kauf's dir einfach 🤷", "#B8860B"),
                      (1, "Tom", "… 💀", "#3E7BDA")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="essen", bg="#8E5BE0", clock="20:00", title="IM RESTAURANT", dark=True, lines=[
        ("Abends im Restaurant zahlt er mit seiner goldenen Kreditkarte.", None),
        ("Trinkgeld gibt er aber keins. Er sagt: Vom Verschenken wird man nicht reich.", None),
    ], viz=dict(kind="stage", box="#FFF6D6", head="🦞 STERNE-RESTAURANT", head_col="#7A3FA8",
                people=[(KELLNER, 800, "Kellner", "neutral", 1)],
                items=[("💳", 360, 660, 140, 0, "pulse"), ("🦞", 380, 860, 100, 0, "bob"), ("🍾", 520, 840, 90, 0, "bob"),
                       ("🪙", 560, 660, 90, 1, "shake")],
                tags=[("GOLD-KARTE 💳", "#B8860B", 360, 560), ("TRINKGELD: 0 € 🪙", "#E23B3B", 540, 980)], fx="anger",
                move="wobble", alex=("smug", "hips", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Bonzen erkennst:", None),
        ("Er erwähnt ständig, was etwas gekostet hat.", None),
        ("Er parkt auf drei Parkplätzen.", None),
        ("Sein Ratschlag: Kauf's dir doch einfach.", None),
        ("Und Trinkgeld gibt's nie.", None),
    ], viz=dict(kind="signs", items=[("Erwähnt ständig Preise", "💸"), ("Parkt auf 3 Plätzen", "🏎️"),
                                     ("„Kauf's dir halt!“", "🛍️"), ("Nie Trinkgeld", "🪙")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Bonzen? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Bonzen?", handle="@rich_alex", icon="💰", col="#B8860B")),
]
