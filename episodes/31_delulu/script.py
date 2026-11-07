"""TikTok-Folge: Heute ist Alex ... delulu. Alltags-Comedy über Klischees (Jugendsprache: delulu = in einer Fantasiewelt).
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), tighten 1.08 0.22 + match_level wie Folge 1. Freigegeben vom Nutzer."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#C59BFF", top_style="hoodie", pants="#9CC0E3", shoes="#FFFFFF")
AL_ANZUG = alex(top="#2B2F3A", top_style="suit", inner="#FFFFFF", pants="#2B2F3A", shoes="#1C1C22")
KELLNERIN = person_spec(33, girl=True, top="#6B4A2E", hair="#2B1A10", skin="#C98B5E")
ROLE, ROLE_TTS, ROLE_SAY = "DELULU.", "delulu.", "delulu!"
MOODS = dict(MOODS_BASE, star="verträumt und sicher, dann trocken", cafe="verliebt, dann trocken",
             chat="euphorisch, dann trocken", job="selbstbewusst, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
INTRO_LEN = 3.3
LINE_MAXPAUSE = {"star_1": 0.12}
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)   # Alex tiefer, Animationsbox größer
CAPTION_Y = 1650   # Untertitel etwas tiefer (bleibt im Sicherheitsbereich)
DAYBAR_Y = 1755   # Tagesleiste unter Alex, noch im Sicherheitsbereich
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45)
REACTIONS = {"star": ["🤳", "💍", "🚩"], "cafe": ["☕", "⏰", "🚩"], "chat": ["📸", "💀", "🚩"], "job": ["👔", "🎓", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX…", l1="", l2="DELULU", bg="#F06FA8", color1="#FFFFFF", accent="#FFE14D",
             pill="#8C1C54", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🦄", "🌈", "💍", "🚩"))
INTRO_CFG = dict(icon="🦄", bg="#F06FA8", title_lines=["DELULU."], rose_glasses=True, glasses_y=74,
                 sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#F48FC0", "#FFE6F2"), walls="#FFF5FA", roof="#C2185B", door="#7A1F48", lawn="#5DAA5E",
                            accent=("#F07FB0", "#36B5C2"), sun=True),
                 left=("🦄", "TRAUMWELT"), right=("🌈", "REALITÄT?"), door=("SIE STEHT", "AUF MICH 💍"),
                 neon=("DELULU IS", "THE SOLULU", "#FF9BEA"), signs=("Sie hat gelächelt! 😍", "Sie steht safe auf mich! 💍"),
                 fly=["🦄", "🌈", "💍"], burst=["🦄", "🌈", "💍", "⭐", "💘", "☁️", "✨", "🫧"],
                 extras=[("🫧", -32, 108, 10), ("✨", 32, 108, 10)])

SCENES = [
    dict(id="what", bg="#9B6BE0", clock=None, title="WAS IST DELULU?", dark=True, lines=[
        ("Wer delulu ist, lebt in seiner eigenen Fantasiewelt.", None),
        ("Ein Lächeln? Für ihn heißt das: Hochzeit.", None),
    ], viz=dict(kind="bars", head="SEIN KOPF", rows=[("REALITÄT", 0.05, "…", "#555A66"), ("FANTASIE", 1.0, "100 %", "#C59BFF")],
                pills=[("😊", "Sie hat gelächelt …", "#F07FB0"), ("💍", "… er plant die Hochzeit", "#8E5BE0")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Delulu ist die Solulu.", None),
    ], viz=dict(kind="stage", **_BIG, box="#FFF5FD", head="🌈 TRAUMWELT", head_col="#9B6BE0",
                items=[("🦄", 330, 680, 180, 0, "bob"), ("🌈", 700, 640, 170, 0, "pulse"), ("☁️", 560, 840, 100, 0, "bob")],
                tags=[("DELULU IS THE SOLULU 🦄", "#9B6BE0")], move="wobble", alex=("happy", "hips", None))),
    dict(id="star", bg="#E0457B", clock="08:00", title="DIE INFLUENCERIN", dark=True, lines=[
        ("Acht Uhr. Seine Lieblings-Influencerin postet ein Herz.", None),
        ("Er ist sich sicher: Das war für ihn. Er hat schon Namen für die Kinder.", None),
    ], viz=dict(kind="stage", **_BIG, box="#FFF0F6", head="📱 NEUER POST VON @LILLY", head_col="#E0457B",
                items=[("🤳", 230, 640, 120, 0, "bob"), ("❤️", 420, 650, 130, 0, "pulse"), ("💍", 300, 840, 90, 1, "bob"),
                       ("👶", 450, 850, 80, 1, "bob"), ("👶", 560, 850, 80, 1, "bob")],
                panels=[dict(line=0, at=0.3, x=765, y=690, w=400, title="📩 DMs an @lilly",
                             rows=["Hey 😍 ✓", "Hallo?? 🥺 ✓", "Hast du mein Herz gesehen? ✓", "Lilly??? ✓"],
                             foot="147 gesendet · 0 Antworten")],
                tags=[None, ("„DAS WAR FÜR MICH!“ 💘", "#E0457B", 400, 980)], fx="love", move="wobble",
                alex=("happy", "idle", "📱"))),
    dict(id="cafe", bg="#C0392B", clock="12:00", title="IM CAFÉ", dark=True, lines=[
        ("Mittags sagt die Kellnerin: Schönen Tag noch.", None),
        ("Er wartet bis Ladenschluss auf sie. Sie hat ja eindeutig Interesse.", None),
    ], viz=dict(kind="stage", **_BIG, box="#FFF4E0", head="☕ CAFÉ", head_col="#6B4A2E",
                people=[(KELLNERIN, 790, "Kellnerin", "neutral", 1)],
                items=[("☕", 290, 860, 100, 0, "bob"), ("💘", 330, 610, 100, 0, "pulse"), ("⏰", 450, 860, 100, 1, "spin")],
                tags=[None, ("WARTET BIS 20 UHR ⏰", "#E23B3B", 540, 980)], fx="shock", move="wobble",
                bubbles=[("Schönen Tag noch! 😊", 545, 700, (1, 0.25), 30, 200), None], alex=("happy", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="16:00", title="DER CRUSH", lines=[
        ("Nachmittags antwortet sein Crush. Nach drei Tagen. Mit: ok.", None),
        ("Er schickt einen Screenshot an alle: Sie steht auf mich!", None),
    ], viz=dict(kind="messenger", switch=1,
                list=[(0, "Mia 💖💘💕😍", "ok", "16:02", 1, "#F07FB0"),
                      (0, "Papa 👨", "Hast du wieder daneben gepinkelt?!?!!??", "15:58", 3, "#555A66"),
                      (0, "Die Jungs 🍻", "Tom: wer kommt heute?", "15:40", 0, "#3E7BDA"),
                      (0, "Mama ❤️", "Hast du gegessen?", "Di.", 0, "#E07A2E")],
                chat=dict(name="Die Jungs 🍻", col="#3E7BDA", msgs=[(1, True, "📸 [Screenshot von Mia]", "16:03"),
                                                                  (1, True, "SIE STEHT SAFE AUF MICH!!! 💍", "16:03"),
                                                                  (1, False, "Bro … das ist ein „ok“ 💀", "16:04"),
                                                                  (1, False, "Bro, die ist doch lesbisch??? 🏳️‍🌈", "16:04")]),
                alex=("happy", "idle", "📱"))),
    dict(id="job", bg="#8E5BE0", clock="20:00", title="DIE BEWERBUNG", dark=True, lines=[
        ("Abends bewirbt er sich als Chef eines Weltkonzerns. Ohne Abschluss.", None),
        ("Er kauft schon mal einen Anzug für den ersten Arbeitstag.", None),
    ], viz=dict(kind="stage", **_BIG, box="#F3EAFE", head="📄 BEWERBUNG: CEO", head_col="#7A3FA8",
                items=[("📄", 330, 680, 150, 0, "bob"), ("🎓", 540, 640, 100, 0, "shake"), ("❌", 540, 640, 70, 0, "pulse"),
                       ("👔", 760, 720, 160, 1, "pulse"), ("🏢", 760, 560, 80, 1, "bob")],
                tags=[("OHNE ABSCHLUSS 🎓❌", "#E23B3B", 400, 860), ("ANZUG GEKAUFT 👔", "#7A3FA8", 700, 980)],
                fx="shock", move="wobble", alex=("smug", "hips", None), alex_swap=(1, 0.35, AL_ANZUG, "happy"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du erkennst, dass jemand delulu ist:", None),
        ("Ein ok ist für ihn ein Heiratsantrag.", None),
        ("Jeder Post seiner Lieblings-Influencerin ist für ihn.", None),
        ("Sie lächelt? Dann liebt sie ihn.", None),
        ("Und er plant Dinge, die niemals passieren.", None),
    ], viz=dict(kind="signs", items=[("„ok“ = Heiratsantrag", "💍"), ("Influencerin-Posts = für ihn", "🤳"),
                                     ("Sie lächelt = sie liebt mich", "😊"), ("Plant das Unmögliche", "🌈")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch jemanden, der delulu ist? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch jemanden, der delulu ist?", handle="@delulu_alex", icon="🦄", col="#9B6BE0")),
]

GEMINI_LINE_MOOD = {"star_1": "verträumt und überzeugt, zügig und flüssig; 'Das war für ihn' in einem Atemzug ohne jede Pause und ohne Dehnung, ganz normal gesprochen, dann trocken",
                    "intro_role": "völlig überrascht und amüsiert, flüssig in einem Zug ohne Stottern oder Wiederholung ausgerufen"}
