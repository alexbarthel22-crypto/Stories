"""TikTok-Folge: Heute ist Alex ... famegeil. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#E0457B", top_style="tee", pants="#2F3B52", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "FAMEGEIL.", "famegeil.", "famegeil!"
MOODS = dict(MOODS_BASE, live="aufgedreht, dann trocken", essen="gestresst, dann trocken", dm="hoffnungsvoll, dann trocken",
             tanz="begeistert, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"live": ["🔴", "👀", "🚩"], "essen": ["📸", "🥶", "🚩"], "dm": ["🙏", "👻", "🚩"], "tanz": ["🕺", "🚌", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX…", l1="", l2="FAMEGEIL", bg="#C2185B", color1="#FFFFFF", accent="#FFE14D",
             pill="#5A0B2B", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("📲", "⭐", "🔴", "🚩"))
INTRO_CFG = dict(icon="⭐", bg="#C2185B", title_lines=["FAMEGEIL."],
                 house=dict(sky=("#E0457B", "#FFE1EE"), walls="#FFF0F6", roof="#5A0B2B", door="#3A0718", lawn="#5DAA5E",
                            accent=("#E0457B", "#F2B233"), sun=True),
                 left=("🔴", "LIVE"), right=("💡", "RINGLICHT"), door=("FOLG MIR!", "@ALEX ⭐"),
                 neon=("FOLG", "MIR!!! 📲", "#FF6FB0"), signs=("Folg mir! 📲", "Glocke an! 🔔"),
                 fly=["⭐", "📲", "❤️"], burst=["⭐", "📲", "🔴", "💡", "📸", "🔔", "❤️", "📈"],
                 extras=[("📲", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#C2185B", clock=None, title="WAS IST FAMEGEIL?", dark=True, lines=[
        ("Wer famegeil ist, will um jeden Preis berühmt werden.", None),
        ("Und fast jeder Satz endet mit: Folg mir!", None),
    ], viz=dict(kind="bars", head="FOLLOWER VS. EGO", rows=[("FOLLOWER", 0.08, "312", "#555A66"), ("EGO", 1.0, "Superstar", "#E0457B")],
                pills=[("📲", "Lieblingssatz: Folg mir!", "#E0457B"), ("🔔", "Und: Glocke an!", "#F2B233")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Was nicht gepostet ist, ist nie passiert.", None),
    ], viz=dict(kind="stage", box="#FFF0F6", head="📸 POSTEN ODER STERBEN", head_col="#C2185B",
                items=[("📸", 540, 660, 200, 0, "pulse"), ("❤️", 300, 700, 100, 0, "fly"), ("⭐", 780, 700, 100, 0, "spin")],
                tags=[("NICHT GEPOSTET = NIE PASSIERT", "#C2185B")], move="wobble", alex=("smug", "hips", "📱"))),
    dict(id="live", bg="#36B5C2", clock="07:00", title="LIVE", lines=[
        ("Sieben Uhr. Er geht live. Beim Zähneputzen.", None),
        ("Zuschauer: zwei. Seine Mutter und ein Bot.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="🔴 LIVE · BAD", head_col="#E23B3B",
                items=[("🪥", 330, 660, 140, 0, "shake"), ("💡", 760, 620, 120, 0, "pulse"), ("👩", 640, 850, 90, 1, "bob"),
                       ("🤖", 800, 850, 90, 1, "bob")],
                tags=[("🔴 LIVE", "#E23B3B", 330, 560), ("👀 2 ZUSCHAUER", "#555A66", 720, 980)], fx="shock",
                move="wobble", alex=("happy", "idle", "📱"))),
    dict(id="essen", bg="#2FA36B", clock="12:00", title="IM RESTAURANT", dark=True, lines=[
        ("Mittags im Restaurant. Alle haben Hunger.", None),
        ("Er braucht vierzig Versuche für das perfekte Foto. Das Essen ist längst kalt.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="🍝 RESTAURANT", head_col="#2E6B34",
                people=[(TOM, 800, "Tom", "neutral", 1)],
                items=[("🍝", 400, 860, 110, 0, "bob"), ("📸", 380, 640, 120, 1, "shake"), ("🥶", 520, 840, 80, 1, "pulse")],
                tags=[None, ("VERSUCH 40 📸 · ESSEN KALT 🥶", "#E23B3B", 540, 980)], fx="anger", move="wobble",
                flash="#FFFFFF", alex=("smug", "idle", "📱"))),
    dict(id="dm", bg="#5B6BC9", clock="16:00", title="DIE DMS", dark=True, lines=[
        ("Nachmittags schreibt er großen Influencern.", None),
        ("Hey, folg mir, ich folg zurück! Antwort: keine.", None),
    ], viz=dict(kind="chat", chat="✉️ Nachrichten", bar="#C2185B",
                msgs=[(0, "Alex", "Hey!! Folg mir, ich folg zurück 🙏⭐", "#E0457B"),
                      (1, "Alex", "??? 🥺", "#E0457B"),
                      (1, "System", "Gesehen ✓✓", "#555A66")],
                fx="shock", alex=("sad", "idle", "📱"))),
    dict(id="tanz", bg="#8E5BE0", clock="19:00", title="DER TREND", dark=True, lines=[
        ("Abends tanzt er einen TikTok-Trend. Mitten auf der Straße.", None),
        ("Ein Bus hupt. Er postet es trotzdem.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", floor="#8C8C96", head="📈 TRENDING?!", head_col="#7A3FA8",
                items=[("🕺", 360, 720, 160, 0, "shake"), ("🎵", 520, 620, 80, 0, "fly"), ("🚌", 760, 860, 160, 1, "rumble"),
                       ("📣", 760, 680, 90, 1, "pulse")],
                tags=[None, ("HUP!!! 🚌 → GEPOSTET ✅", "#E23B3B", 540, 980)], fx="shock", move="rumble", flash="#FFE14D",
                alex=("happy", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du erkennst, dass jemand famegeil ist:", None),
        ("Er sagt ständig: Folg mir!", None),
        ("Er geht bei allem live.", None),
        ("Fürs Foto wird das Essen kalt.", None),
        ("Und er tanzt überall Trends.", None),
    ], viz=dict(kind="signs", items=[("Sagt ständig: Folg mir!", "📲"), ("Geht bei allem live", "🔴"),
                                     ("Essen kalt fürs Foto", "📸"), ("Tanzt überall Trends", "🕺")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch jemanden, der famegeil ist? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch jemanden, der famegeil ist?", handle="@folgmir_alex", icon="⭐", col="#C2185B")),
]
