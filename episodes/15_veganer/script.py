"""TikTok-Folge: Heute ist Alex ... ein Veganer. Alltags-Comedy über Klischees, nicht gegen vegane Ernährung.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#6FB86A", top_style="hoodie", pants="#C9B48A", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN VEGANER.", "ein Veganer.", "ein Veganer!"
MOODS = dict(MOODS_BASE, fruehstueck="begeistert, dann trocken", mensa="belehrend, dann trocken",
             markt="erst konzentriert, dann laut schockiert", grill="fröhlich, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"fruehstueck": ["🥑", "📸", "🚩"], "mensa": ["💧", "🙄", "🚩"], "markt": ["🔍", "😱", "🚩"], "grill": ["🔥", "🌭", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="VEGANER", bg="#3F9A4A", color1="#FFFFFF", accent="#FFE14D",
             pill="#1F5A28", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🌱", "🥑", "📢", "🚩"))
INTRO_CFG = dict(icon="🌱", bg="#3F9A4A", title_lines=["VEGANER."],
                 house=dict(sky=("#7FCB7A", "#E8FFE0"), walls="#F2FFF0", roof="#2E6B34", door="#1F5A28", lawn="#5DAA5E",
                            accent=("#6FB86A", "#F2B233"), sun=True),
                 left=("🥑", "AVOCADO"), right=("🌱", "PLANT-BASED"), door=("HIER WIRD", "VEGAN GEKOCHT"),
                 neon=("100 %", "VEGAN 🌱", "#7CFF8A"), signs=("Ich bin übrigens vegan 🌱", "Hast du mal Tofu? 🥢"),
                 fly=["🌱", "🥑", "🥕"], burst=["🌱", "🥑", "🥕", "🥦", "🌽", "🍆", "🥬", "📢"],
                 extras=[("🌱", -26, 60, 12), ("🥑", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#3F9A4A", clock=None, title="WAS IST EIN VEGANER?", dark=True, lines=[
        ("Ein Veganer isst keine tierischen Produkte.", None),
        ("Und das weißt du, bevor du überhaupt Hallo sagen kannst.", None),
    ], viz=dict(kind="bars", head="SEIN ERSTER SATZ", rows=[("TOFU", 1.0, "täglich", "#2FA36B"), ("FLEISCH", 0.0, "0 g", "#E23B3B")],
                pills=[("👋", "Hallo? Ich bin vegan!", "#2FA36B"), ("📢", "Hab ich schon erwähnt …?", "#E07A2E")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Wenn ich schon vegan bin, soll es auch die ganze Welt wissen.", None),
    ], viz=dict(kind="stage", box="#E8FFE0", head="📢 AN ALLE:", head_col="#2E6B34",
                items=[("🌍", 540, 690, 220, 0, "spin"), ("📢", 280, 640, 120, 0, "shake"), ("🌱", 800, 640, 110, 0, "pulse")],
                tags=[("DIE GANZE WELT 🌍", "#2E6B34")], move="wobble", alex=("smug", "hips", None))),
    dict(id="fruehstueck", bg="#D9A441", clock="08:00", title="FRÜHSTÜCK", lines=[
        ("Acht Uhr. Hafer-Latte und Avocado-Toast.", None),
        ("Bevor er isst, postet er das Foto. Mit siebzehn Hashtags.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", floor="#E8C79A", head="☕ BRUNCH-TIME", head_col="#A8642E",
                items=[("☕", 300, 640, 110, 0, "bob"), ("🥑", 540, 620, 120, 0, "pulse"), ("🍞", 760, 640, 110, 0, "bob"),
                       ("📸", 540, 860, 110, 1, "shake")],
                tags=[None, ("#vegan #plantbased #… ×17", "#2FA36B", 540, 980)], fx="party", move="wobble", flash="#FFFFFF",
                alex=("happy", "idle", "📱"))),
    dict(id="mensa", bg="#5B6BC9", clock="12:00", title="IN DER MENSA", dark=True, lines=[
        ("Mittags in der Mensa. Er rechnet Tom vor, wie viel Wasser sein Schnitzel verbraucht hat.", None),
        ("Tom isst einfach weiter.", None),
    ], viz=dict(kind="stage", box="#EEF0F4", head="🍽️ MENSA", head_col="#2B2F3A",
                people=[(TOM, 770, "Tom", "neutral", None)],
                items=[("📊", 300, 620, 130, 0, "shake"), ("💧", 450, 640, 90, 0, "fly"), ("🍖", 770, 880, 100, 1, "bob")],
                tags=[("15.000 L WASSER 💧", "#3E7BDA", 330, 820), ("TOM ISST WEITER 😋", "#2FA36B", 700, 560)],
                move="wobble", alex=("angry", "idle", None))),
    dict(id="markt", bg="#C0392B", clock="16:00", title="IM SUPERMARKT", dark=True, lines=[
        ("Sechzehn Uhr. Supermarkt. Er liest jede Zutatenliste. Laut.", None),
        ("Bei den Gummibärchen schreit er durch den ganzen Laden: Gelatine!", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="🛒 SUPERMARKT", head_col="#C0392B",
                items=[("🛒", 260, 880, 130, 0, "bob"), ("🔍", 420, 640, 110, 0, "shake"), ("📋", 620, 640, 110, 0, "bob"),
                       ("🐻", 760, 820, 120, 1, "shake")],
                tags=[None, ("GELATINE!!! 😱", "#E23B3B", 540, 980)], fx="shock", move="rumble", flash="#FF3B3B",
                alex=("angry", "idle", None))),
    dict(id="grill", bg="#E07A2E", clock="20:00", title="GRILLABEND", dark=True, lines=[
        ("Abends Grillabend. Er bringt seine eigenen Tofu-Würstchen mit.", None),
        ("Und verlangt einen eigenen Grill. Damit nichts Fleisch berührt.", None),
    ], viz=dict(kind="stage", box="#FFE9D6", floor="#5DAA5E", head="🔥 GRILLABEND", head_col="#A8642E",
                people=[(TOM, 780, "Tom", "neutral", 1)],
                items=[("🔥", 320, 760, 130, 0, "pulse"), ("🌭", 320, 640, 90, 0, "bob"), ("🍢", 540, 640, 100, 0, "bob"),
                       ("🔥", 560, 860, 120, 1, "pulse")],
                tags=[("TOFU-WÜRSTCHEN 🌱", "#2FA36B", 360, 560), ("EIGENER GRILL!", "#E23B3B", 560, 980)], fx="anger",
                move="wobble", alex=("smug", "hips", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Veganer erkennst:", None),
        ("Er sagt es dir in den ersten zehn Sekunden.", None),
        ("Er postet jedes Essen.", None),
        ("Er liest Zutatenlisten laut vor.", None),
        ("Und er bringt immer sein eigenes Essen mit.", None),
    ], viz=dict(kind="signs", items=[("Sagt es in 10 Sekunden", "🗣️"), ("Postet jedes Essen", "📸"),
                                     ("Liest Zutaten laut vor", "🔍"), ("Bringt eigenes Essen mit", "🥡")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Veganer? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Veganer?", handle="@tofu_alex", icon="🌱", col="#3F9A4A")),
]
