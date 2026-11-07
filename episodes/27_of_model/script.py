"""TikTok-Folge (neu im aktuellen Layout): Heute ist Alex ... ein OF-Model. Komplett jugendfrei, nur Klischees.
Gesprochen wird "O-Eff". Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#00AFF0", top_style="tee", pants="#2F3B52", shoes="#FFFFFF")
OPA = person_spec(55, top="#B9A27A", hair="#DDDDDD")
ROLE, ROLE_TTS, ROLE_SAY = "EIN OF-MODEL.", "ein O-Eff-Model.", "ein O-Eff-Model!"
MOODS = dict(MOODS_BASE, shooting="übertrieben professionell, dann trocken", dms="aufgeregt, dann trocken",
             werbung="werblich, dann trocken", familie="lieb, dann peinlich ausweichend")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"shooting": ["💡", "🌶️", "🚩"], "dms": ["🤖", "👵", "🚩"], "werbung": ["🔗", "🥖", "🚩"], "familie": ["👴", "😅", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="OF-", l2="MODEL", bg="#0088C2", color1="#FFFFFF", accent="#FFE14D",
             pill="#004466", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🔗", "💡", "📸", "🚩"))
INTRO_CFG = dict(icon="🔗", bg="#0088C2", title_lines=["OF-MODEL."],
                 house=dict(sky=("#36B5E8", "#E1F6FF"), walls="#F0FAFF", roof="#004466", door="#002A40", lawn="#5DAA5E",
                            accent=("#00AFF0", "#E0457B"), sun=True),
                 left=("💡", "RINGLICHT"), right=("📸", "STUDIO (BAD)"), door=("LINK", "IN BIO 🔗"),
                 neon=("ABO?", "LINK IN BIO", "#4FD2FF"), signs=("Link in Bio 🔗", "Abonnier mich! 💸"),
                 fly=["🔗", "💸", "📸"], burst=["🔗", "💡", "📸", "💸", "🌶️", "🍳", "🤖", "⭐"],
                 extras=[("🔗", 34, 60, 12)])

SCENES = [
    dict(id="what", bg="#0088C2", clock=None, title="WAS IST EIN OF-MODEL?", dark=True, lines=[
        ("Ein OF-Model verkauft exklusive Inhalte im Internet.", "Ein O-Eff-Model verkauft exklusive Inhalte im Internet."),
        ("Bei Alex heißt exklusiv: Fotos von seinem Frühstück.", None),
    ], viz=dict(kind="bars", head="SEIN ACCOUNT", rows=[("FANS", 0.05, "3 (Bots)", "#555A66"), ("SELBSTBILD", 1.0, "Superstar", "#00AFF0")],
                pills=[("🔗", "Link in Bio!", "#00AFF0"), ("🍳", "Exklusiv: Rührei", "#F2B233")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Wer nicht abonniert, verpasst was. Sagt er.", None),
    ], viz=dict(kind="stage", box="#F0FAFF", head="🔗 ABONNIEREN?", head_col="#0088C2",
                items=[("🔗", 330, 680, 170, 0, "pulse"), ("💸", 720, 660, 140, 0, "fly"), ("🍳", 560, 840, 90, 0, "bob")],
                tags=[("VERPASST: RÜHREI 🍳", "#0088C2")], move="wobble", alex=("smug", "hips", "📱"))),
    dict(id="shooting", bg="#D9A441", clock="09:00", title="DAS SHOOTING", lines=[
        ("Neun Uhr. Fotoshooting mit Ringlicht. Im Badezimmer.", None),
        ("Der heißeste Inhalt heute: eine scharfe Chilischote.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="📸 STUDIO (BAD)", head_col="#2B5C66",
                items=[("💡", 330, 660, 160, 0, "pulse"), ("🛁", 720, 840, 130, 0, "bob"), ("🌶️", 660, 640, 140, 1, "shake"),
                       ("🔥", 800, 620, 80, 1, "pulse")],
                tags=[None, ("SPICY CONTENT 🌶️", "#E23B3B", 540, 980)], fx="shock", move="wobble", flash="#FFFFFF",
                alex=("smug", "hips", "📱"))),
    dict(id="dms", bg="#36B5C2", clock="13:00", title="DIE NACHRICHTEN", lines=[
        ("Mittags checkt er seine Nachrichten. Vierzig neue!", None),
        ("Neununddreißig davon sind Bots. Eine ist von seiner Oma: Junge, iss was.", None),
    ], viz=dict(kind="chat", chat="✉️ 40 neue Nachrichten", bar="#0088C2",
                msgs=[(0, "Bot_4821", "Gewinnspiel!!! Klick hier 🎁", "#555A66"),
                      (1, "Bot_4822", "Gewinnspiel!!! Klick hier 🎁", "#555A66"),
                      (1, "Oma 👵", "Junge, iss was 🍲", "#E07A2E")],
                fx="party", alex=("happy", "idle", "📱"))),
    dict(id="werbung", bg="#5B6BC9", clock="17:00", title="WERBUNG", dark=True, lines=[
        ("Siebzehn Uhr. Er macht Werbung für sich. Überall.", None),
        ("Sogar beim Bäcker hängt er einen Zettel auf: Link in Bio.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="🥐 BÄCKEREI", head_col="#A8642E",
                items=[("🥖", 300, 640, 110, 0, "bob"), ("🥐", 430, 640, 100, 0, "bob"), ("📌", 720, 640, 90, 1, "shake"),
                       ("📄", 720, 760, 150, 1, "pulse")],
                tags=[None, ("LINK IN BIO 🔗", "#00AFF0", 720, 980)], fx="shock", move="wobble",
                alex=("smug", "idle", None))),
    dict(id="familie", bg="#8E5BE0", clock="20:00", title="FAMILIENESSEN", dark=True, lines=[
        ("Abends beim Familienessen fragt Opa, was er beruflich macht.", None),
        ("Er sagt: Content Creator. Im Bereich Frühstück.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🍽️ SONNTAGSESSEN", head_col="#7A3FA8",
                people=[(OPA, 800, "Opa", "neutral", 1)],
                items=[("🍗", 420, 860, 90, 0, "bob"), ("🥔", 540, 860, 80, 0, "bob"), ("😅", 330, 640, 130, 1, "shake"),
                       ("🍳", 480, 640, 90, 1, "pulse")],
                tags=[None, ("„CONTENT CREATOR“ 🍳", "#7A3FA8", 540, 980)], fx="shock", move="wobble",
                alex=("smug", "shrug", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du ein OF-Model erkennst:", "Woran du ein O-Eff-Model erkennst:"),
        ("Er sagt ständig: Link in Bio.", None),
        ("Er hat ein Ringlicht im Badezimmer.", None),
        ("Seine Fans sind Bots. Und seine Oma.", None),
        ("Und beruflich ist er Content Creator.", None),
    ], viz=dict(kind="signs", items=[("„Link in Bio“ überall", "🔗"), ("Ringlicht im Bad", "💡"),
                                     ("Fans: Bots + Oma", "🤖"), ("Beruf: Content Creator", "📸")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch ein OF-Model? Markier sie oder ihn!", "Kennst du auch ein O-Eff-Model? Markier sie oder ihn!"),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch ein OF-Model?", handle="@linkinbio_alex", icon="🔗", col="#0088C2")),
]
