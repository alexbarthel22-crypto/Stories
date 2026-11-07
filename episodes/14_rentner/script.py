"""TikTok-Folge: Heute ist Alex ... ein Rentner. Alltags-Comedy, liebevolle Klischees.
Stimme exakt wie Pick-me-Boy: gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level. (Vorschau: Ersatzstimme)"""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#B9A27A", top_style="cardigan", inner="#FFFFFF", pants="#6B6B70", shoes="#4A3B2A")
BAECKER = person_spec(21, top="#FFFFFF", hair="#3B2A20")
NACHBAR = person_spec(55, top="#3E7BDA", hair="#8A5A2B")
ROLE = "EIN RENTNER."
ROLE_TTS = "ein Rentner."
ROLE_SAY = "ein Rentner!"
MOODS = dict(MOODS_BASE, baecker="ruhig, dann trocken", fenster="empört und wichtig", kasse="genervt amüsiert",
             chat="liebevoll spöttisch, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"baecker": ["🥖", "🪙", "🚩"], "fenster": ["🚗", "📞", "🚩"], "kasse": ["🛒", "😤", "🚩"], "chat": ["🌹", "📢", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="RENTNER", bg="#8A7B5C", color1="#FFFFFF", accent="#FFE14D",
             pill="#4A3B2A", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("👴", "🥖", "🪙", "🚩"))
INTRO_CFG = dict(icon="👴", bg="#8A7B5C", title_lines=["RENTNER."],
                 house=dict(sky=("#C9B48A", "#FFF1D6"), walls="#FFF4E0", roof="#6B4A2E", door="#4A3B2A", lawn="#5DAA5E",
                            accent=("#B9A27A", "#3E7BDA"), sun=True),
                 left=("🪟", "FENSTERPLATZ"), right=("📺", "VOLKSMUSIK"), door=("BITTE KEINE", "WERBUNG!"),
                 neon=("FRÜHER", "WAR ALLES 👌", "#FFB13B"), signs=("Ruhezeit! 🤫", "Früher war alles besser 👴"),
                 fly=["🪙", "🥖", "💊"], burst=["👴", "🥖", "🪙", "💊", "📺", "🦯", "☕", "🌹"],
                 extras=[("👓", 0, 92, 10), ("🦯", 34, 30, 16)])

SCENES = [
    dict(id="what", bg="#8A7B5C", clock=None, title="WAS IST EIN RENTNER?", dark=True, lines=[
        ("Ein Rentner hat den ganzen Tag frei. Und trotzdem nie Zeit.", None),
        ("Sein Kalender ist voll: Arzt, Apotheke und nochmal Arzt.", None),
    ], viz=dict(kind="bars", head="FREIZEIT VS. ZEIT", rows=[("FREIZEIT", 1.0, "24/7", "#2FA36B"), ("ZEIT", 0.0, "0 Min", "#E23B3B")],
                pills=[("📅", "Mo–Fr: Arzt, Arzt, Arzt", "#3E7BDA"), ("💊", "Apotheke: Stammkunde", "#2FA36B")])),
    dict(id="motto", bg="#2FA36B", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Früher war alles besser. Sogar das Wetter.", None),
    ], viz=dict(kind="stage", box="#EAF6FF", head="FRÜHER  vs.  HEUTE", head_col="#8A7B5C",
                items=[("☀️", 300, 600, 150, 0, "spin"), ("🌧️", 780, 600, 150, 0, "shake"), ("👍", 300, 820, 90, 0, "pulse"),
                       ("👎", 780, 820, 90, 0, "pulse")],
                tags=[("SOGAR DAS WETTER ☁️", "#8A7B5C")], move="wobble", alex=("smug", "hips", None))),
    dict(id="baecker", bg="#D9A441", clock="06:00", title="BEIM BÄCKER", lines=[
        ("Sechs Uhr. Erster beim Bäcker. Er wartet schon, bevor die aufmachen.", None),
        ("Dann bezahlt er zwei Brötchen. In Ein-Cent-Stücken.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", floor="#E8C79A", head="🥐 BÄCKEREI · ÖFFNET 6:00", head_col="#A8642E",
                people=[(BAECKER, 780, "Bäcker", "neutral", 1)],
                items=[("🥖", 250, 600, 100, 0, "bob"), ("🥐", 400, 620, 90, 0, "bob"), ("⏰", 560, 560, 90, 0, "shake"),
                       ("🪙", 260, 900, 60, 1, "fly"), ("🪙", 360, 880, 60, 1, "fly"), ("🪙", 460, 900, 60, 1, "fly"),
                       ("🪙", 560, 880, 60, 1, "fly")],
                tags=[("5:42 SCHON DA 🕠", "#3E7BDA", 300, 760), ("1,20 € IN 1-CENT 🪙", "#E23B3B", 540, 980)],
                fx="anger", move="wobble", alex=("happy", "idle", "🥖"))),
    dict(id="fenster", bg="#5B6BC9", clock="10:00", title="AM FENSTER", dark=True, lines=[
        ("Zehn Uhr. Kissen aufs Fensterbrett. Er überwacht die Straße.", None),
        ("Ein Auto parkt zwei Zentimeter zu weit. Er ruft sofort das Ordnungsamt.", None),
    ], viz=dict(kind="stage", box="#CFE8FF", floor="#8C8C96", head="🪟 STRASSEN-ÜBERWACHUNG", head_col="#2B2F3A",
                items=[("🪟", 270, 610, 150, 0, "bob"), ("🔭", 430, 600, 90, 0, "shake"), ("🚗", 700, 900, 160, 1, "shake"),
                       ("📏", 860, 830, 80, 1, "pulse"), ("📞", 330, 860, 100, 1, "shake")],
                tags=[None, ("2 CM ZU WEIT! 🚨", "#E23B3B", 700, 760)], fx="shock", move="rumble", flash="#FF3B3B",
                alex=("angry", "idle", "📞"))),
    dict(id="kasse", bg="#C0392B", clock="14:00", title="AN DER KASSE", dark=True, lines=[
        ("Vierzehn Uhr. Supermarkt. Hinter ihm warten vierzehn Leute.", None),
        ("Und er erzählt der Kassiererin seine ganze Knie-OP.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="🛒 KASSE 1", head_col="#C0392B",
                people=[(NACHBAR, 760, "Kundin", "neutral", 1)],
                items=[("🛒", 250, 900, 120, 0, "bob"), ("🧍", 650, 700, 60, 0, "bob"), ("🧍", 720, 700, 60, 0, "bob"),
                       ("🧍", 790, 700, 60, 0, "bob"), ("🦵", 420, 640, 110, 1, "pulse"), ("🏥", 560, 600, 90, 1, "bob")],
                tags=[("SCHLANGE: 14 😤", "#E23B3B", 700, 560), ("KNIE-OP: 25 MIN 🦵", "#8A7B5C", 450, 980)],
                fx="anger", move="wobble", alex=("happy", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="18:00", title="FAMILIEN-CHAT", lines=[
        ("Achtzehn Uhr. Familien-Chat. Er schickt Guten-Abend-Bilder mit Glitzer.", None),
        ("Und schreibt alles in Großbuchstaben. Mit Unterschrift.", None),
    ], viz=dict(kind="chat", chat="👨‍👩‍👧 Familie 💕", bar="#25A366",
                msgs=[(0, "Opa Alex", "🌹✨ GUTEN ABEND IHR LIEBEN ✨🌹", "#E23B3B"),
                      (1, "Opa Alex", "WER HAT MEINEN SCHIRM? GRUSS, ALEX", "#E23B3B"),
                      (1, "Enkel Tom", "Opa, du musst nicht unterschreiben 😭", "#3E7BDA")],
                fx="party", alex=("happy", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Rentner erkennst:", None),
        ("Er steht um sechs beim Bäcker.", None),
        ("Er zahlt mit Kleingeld. Ganz langsam.", None),
        ("Er überwacht die Straße vom Fenster aus.", None),
        ("Und er schreibt alles in Großbuchstaben.", None),
    ], viz=dict(kind="signs", items=[("Um 6 Uhr beim Bäcker", "🥖"), ("Zahlt mit Kleingeld", "🪙"),
                                     ("Überwacht die Straße", "🪟"), ("SCHREIBT IN CAPS", "📢")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Rentner? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Rentner?", handle="@opa_alex", icon="👴", col="#8A7B5C")),
]
