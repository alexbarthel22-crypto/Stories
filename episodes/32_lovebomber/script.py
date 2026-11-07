"""TikTok-Folge: Heute ist Alex ... ein Lovebomber. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#E0457B", top_style="tee", pants="#2F3B52", shoes="#FFFFFF")
MIA = person_spec(14, girl=True, top="#F2B233", hair="#5A3A22", skin="#F1C9A8")
ROLE, ROLE_TTS, ROLE_SAY = "EIN LOVEBOMBER.", "ein Lovebomber.", "ein Lovebomber!"
MOODS = dict(MOODS_BASE, date="schwärmerisch, dann trocken", chat="übertrieben verliebt, dann trocken",
             geschenke="überschwänglich, dann trocken", woche3="kühl, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"date": ["💘", "🏠", "🚩"], "chat": ["😍", "😳", "🚩"], "geschenke": ["🌹", "✍️", "🚩"], "woche3": ["👻", "💣", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="LOVE-", l2="BOMBER", bg="#C2185B", color1="#FFFFFF", accent="#FFE14D",
             pill="#5A0B2B", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("💣", "❤️", "👻", "🚩"))
INTRO_CFG = dict(icon="💣", bg="#C2185B", title_lines=["LOVEBOMBER."],
                 house=dict(sky=("#F07FB0", "#FFE6F0"), walls="#FFF5F9", roof="#7A1F48", door="#4A0E2A", lawn="#5DAA5E",
                            accent=("#E0457B", "#F2B233"), sun=True),
                 left=("🌹", "100 ROSEN"), right=("💣", "LIEBESBOMBE"), door=("DU BIST", "DIE EINE 💘"),
                 neon=("FOREVER", "(3 WOCHEN)", "#FF6FB0"), signs=("Du bist mein Leben 😍", "… gelesen ✓✓"),
                 fly=["❤️", "💣", "🌹"], burst=["💣", "❤️", "🌹", "🧸", "💍", "💌", "👻", "😍"],
                 extras=[("🌹", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#C2185B", clock=None, title="WAS IST EIN LOVEBOMBER?", dark=True, lines=[
        ("Ein Lovebomber überschüttet dich am Anfang mit Liebe.", None),
        ("Und nach drei Wochen ist alles plötzlich wieder weg.", None),
    ], viz=dict(kind="bars", head="SEINE LIEBE", rows=[("WOCHE 1", 1.0, "1000 %", "#E0457B"), ("WOCHE 3", 0.02, "weg", "#555A66")],
                pills=[("💐", "Woche 1: Rosen & Herzen", "#E0457B"), ("👻", "Woche 3: Gelesen.", "#555A66")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Viel hilft viel. Zumindest am Anfang.", None),
    ], viz=dict(kind="stage", box="#FFF5F9", head="💣 LIEBESBOMBE", head_col="#C2185B",
                items=[("💣", 330, 680, 180, 0, "shake"), ("❤️", 600, 620, 90, 0, "fly"), ("❤️", 720, 680, 90, 0, "fly"),
                       ("❤️", 820, 620, 90, 0, "fly")],
                tags=[("VIEL HILFT VIEL 💥", "#C2185B")], fx="love", move="rumble", alex=("happy", "hips", None))),
    dict(id="date", bg="#E07A2E", clock="12:00", title="DAS ERSTE DATE", dark=True, lines=[
        ("Erstes Date. Nach zehn Minuten sagt er: Ich glaub, du bist die Eine.", None),
        ("Nach einer Stunde zeigt er ihr schon Wohnungen. Für sie beide.", None),
    ], viz=dict(kind="stage", box="#FFF0E6", head="🕯️ DATE NR. 1", head_col="#A8642E",
                people=[(MIA, 800, "Mia", "happy", 1)],
                items=[("💘", 330, 640, 140, 0, "pulse"), ("🍝", 520, 860, 80, 0, "bob"), ("🏠", 360, 820, 120, 1, "bob"),
                       ("💍", 520, 640, 90, 1, "spin")],
                tags=[("10 MIN: „DIE EINE“ 💘", "#E0457B", 360, 560), ("WOHNUNGSSUCHE 🏠", "#A8642E", 540, 980)],
                fx="love", move="wobble", alex=("happy", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="15:00", title="100 NACHRICHTEN", lines=[
        ("Danach: hundert Nachrichten. In einer Stunde.", None),
        ("Du bist mein Leben, schreibt er. Sie kennen sich seit gestern.", None),
    ], viz=dict(kind="chat", chat="💬 Mia 💕 (100)", bar="#E0457B",
                msgs=[(0, "Alex", "Prinzessin 👑💕 vermisse dich schon", "#E0457B"),
                      (1, "Alex", "Du bist mein LEBEN 😍😍😍", "#E0457B"),
                      (1, "Mia", "Wir kennen uns seit gestern 😳", "#3E7BDA")],
                fx="love", alex=("happy", "idle", "📱"))),
    dict(id="geschenke", bg="#8E5BE0", clock="18:00", title="WOCHE EINS", dark=True, lines=[
        ("Woche eins: Rosen, Teddybär, Kette. Und ein Tattoo mit ihrem Namen.", None),
        ("Ihren Nachnamen kennt er noch nicht.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🎁 GESCHENKE-FLUT", head_col="#7A3FA8",
                items=[("🌹", 260, 640, 110, 0, "bob"), ("🧸", 420, 650, 120, 0, "bob"), ("📿", 580, 640, 100, 0, "spin"),
                       ("✍️", 760, 660, 120, 0, "shake"), ("🤷", 540, 850, 110, 1, "pulse")],
                tags=[("TATTOO: „MIA“ ✍️", "#E0457B", 700, 820), ("NACHNAME? 🤷", "#555A66", 540, 980)], fx="party",
                move="wobble", flash="#FFE14D", alex=("happy", "idle", "🌹"))),
    dict(id="woche3", bg="#3B3F58", clock="21:00", title="WOCHE DREI", dark=True, lines=[
        ("Woche drei. Mia schreibt: Hey, alles okay?", None),
        ("Antwort: Gelesen. Er lovebombt schon die Nächste.", None),
    ], viz=dict(kind="stage", box="#E6E6EA", head="📱 MIA: „HEY, ALLES OK?“", head_col="#3B3F58",
                people=[(MIA, 800, "Mia", "sad", None)],
                items=[("📱", 330, 660, 150, 0, "bob"), ("👻", 330, 840, 110, 1, "fly"), ("💣", 560, 640, 110, 1, "shake"),
                       ("🌹", 560, 820, 80, 1, "bob")],
                tags=[("GELESEN ✓✓", "#555A66", 330, 560), ("NÄCHSTES ZIEL 💣", "#E23B3B", 540, 980)], fx="shock",
                move="wobble", alex=("smug", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Lovebomber erkennst:", None),
        ("Nach zehn Minuten bist du die Eine.", None),
        ("Er schickt hundert Nachrichten am Tag.", None),
        ("In Woche eins gibt's Geschenke ohne Ende.", None),
        ("Und in Woche drei: Funkstille.", None),
    ], viz=dict(kind="signs", items=[("„Die Eine“ nach 10 Min", "💘"), ("100 Nachrichten am Tag", "📱"),
                                     ("Geschenke-Flut in Woche 1", "🎁"), ("Woche 3: Funkstille", "👻")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Lovebomber? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Lovebomber?", handle="@lovebomb_alex", icon="💣", col="#C2185B")),
]
