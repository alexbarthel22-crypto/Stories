"""TikTok-Folge: Heute ist Alex ... delulu. Alltags-Comedy über Klischees (Jugendsprache: delulu = in einer Fantasiewelt).
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#C59BFF", top_style="hoodie", pants="#9CC0E3", shoes="#FFFFFF")
KELLNERIN = person_spec(33, girl=True, top="#6B4A2E", hair="#2B1A10", skin="#C98B5E")
ROLE, ROLE_TTS, ROLE_SAY = "DELULU.", "delulu.", "delulu!"
MOODS = dict(MOODS_BASE, star="verträumt und sicher, dann trocken", cafe="verliebt, dann trocken",
             chat="euphorisch, dann trocken", job="selbstbewusst, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"star": ["⭐", "💍", "🚩"], "cafe": ["☕", "⏰", "🚩"], "chat": ["📸", "💀", "🚩"], "job": ["👔", "🎓", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX…", l1="", l2="DELULU", bg="#9B6BE0", color1="#FFFFFF", accent="#FFE14D",
             pill="#4A2E78", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🦄", "🌈", "💍", "🚩"))
INTRO_CFG = dict(icon="🦄", bg="#9B6BE0", title_lines=["DELULU."],
                 house=dict(sky=("#C59BFF", "#FFE6FA"), walls="#FFF5FD", roof="#7A4FB8", door="#4A2E78", lawn="#5DAA5E",
                            accent=("#F07FB0", "#36B5C2"), sun=True),
                 left=("🦄", "TRAUMWELT"), right=("🌈", "REALITÄT?"), door=("SIE STEHT", "AUF MICH 💍"),
                 neon=("DELULU IS", "THE SOLULU", "#FF9BEA"), signs=("Sie hat gelächelt! 😍", "Das war für mich! ⭐"),
                 fly=["🦄", "🌈", "💍"], burst=["🦄", "🌈", "💍", "⭐", "💘", "☁️", "✨", "🫧"],
                 extras=[("🫧", -30, 100, 10), ("✨", 30, 100, 10)])

SCENES = [
    dict(id="what", bg="#9B6BE0", clock=None, title="WAS IST DELULU?", dark=True, lines=[
        ("Wer delulu ist, lebt in seiner eigenen Fantasiewelt.", None),
        ("Ein Lächeln? Für ihn heißt das: Hochzeit.", None),
    ], viz=dict(kind="bars", head="SEIN KOPF", rows=[("REALITÄT", 0.05, "…", "#555A66"), ("FANTASIE", 1.0, "100 %", "#C59BFF")],
                pills=[("😊", "Sie hat gelächelt …", "#F07FB0"), ("💍", "… er plant die Hochzeit", "#8E5BE0")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Delulu ist die Solulu.", None),
    ], viz=dict(kind="stage", box="#FFF5FD", head="🌈 TRAUMWELT", head_col="#9B6BE0",
                items=[("🦄", 330, 680, 180, 0, "bob"), ("🌈", 700, 640, 170, 0, "pulse"), ("☁️", 560, 840, 100, 0, "bob")],
                tags=[("DELULU IS THE SOLULU 🦄", "#9B6BE0")], move="wobble", alex=("happy", "hips", None))),
    dict(id="star", bg="#E0457B", clock="08:00", title="DER POPSTAR", dark=True, lines=[
        ("Acht Uhr. Ein Popstar postet ein Herz.", None),
        ("Er ist sich sicher: Das war für ihn. Er hat schon Namen für die Kinder.", None),
    ], viz=dict(kind="stage", box="#FFF0F6", head="📱 NEUER POST VOM STAR", head_col="#E0457B",
                items=[("⭐", 330, 640, 140, 0, "spin"), ("❤️", 520, 660, 140, 0, "pulse"), ("💍", 720, 640, 110, 1, "bob"),
                       ("👶", 700, 840, 90, 1, "bob"), ("👶", 820, 840, 90, 1, "bob")],
                tags=[None, ("„DAS WAR FÜR MICH!“ 💘", "#E0457B", 400, 980)], fx="love", move="wobble",
                alex=("happy", "idle", "📱"))),
    dict(id="cafe", bg="#C0392B", clock="12:00", title="IM CAFÉ", dark=True, lines=[
        ("Mittags sagt die Kellnerin: Schönen Tag noch.", None),
        ("Er wartet bis Ladenschluss auf sie. Sie hat ja eindeutig Interesse.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="☕ CAFÉ", head_col="#6B4A2E",
                people=[(KELLNERIN, 790, "Kellnerin", "neutral", 1)],
                items=[("☕", 330, 820, 100, 0, "bob"), ("💘", 520, 620, 110, 0, "pulse"), ("⏰", 330, 640, 110, 1, "spin")],
                tags=[None, ("WARTET BIS 20 UHR ⏰", "#E23B3B", 540, 980)], fx="shock", move="wobble",
                bubbles=["Schönen Tag noch! 😊", None], alex=("happy", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="16:00", title="DER CRUSH", lines=[
        ("Nachmittags antwortet sein Crush. Nach drei Tagen. Mit: ok.", None),
        ("Er schickt einen Screenshot an alle: Sie steht auf mich!", None),
    ], viz=dict(kind="chat", chat="💬 Mia 💘", bar="#25A366",
                msgs=[(0, "Mia", "ok", "#3E7BDA"),
                      (1, "Alex → Gruppe", "📸 SIE STEHT AUF MICH!!! 💍", "#8E5BE0"),
                      (1, "Tom", "Bro … das ist ein „ok“ 💀", "#3E7BDA")],
                fx="love", alex=("happy", "idle", "📱"))),
    dict(id="job", bg="#8E5BE0", clock="20:00", title="DIE BEWERBUNG", dark=True, lines=[
        ("Abends bewirbt er sich als Chef eines Weltkonzerns. Ohne Abschluss.", None),
        ("Er kauft schon mal einen Anzug für den ersten Arbeitstag.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="📄 BEWERBUNG: CEO", head_col="#7A3FA8",
                items=[("📄", 330, 680, 150, 0, "bob"), ("🎓", 540, 640, 100, 0, "shake"), ("❌", 540, 640, 70, 0, "pulse"),
                       ("👔", 760, 720, 160, 1, "pulse"), ("🏢", 760, 560, 80, 1, "bob")],
                tags=[("OHNE ABSCHLUSS 🎓❌", "#E23B3B", 400, 860), ("ANZUG GEKAUFT 👔", "#7A3FA8", 700, 980)],
                fx="shock", move="wobble", alex=("smug", "hips", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du erkennst, dass jemand delulu ist:", None),
        ("Ein Lächeln ist für ihn Liebe.", None),
        ("Jeder Promi-Post ist für ihn.", None),
        ("Ein ok ist ein Heiratsantrag.", None),
        ("Und er plant Dinge, die niemals passieren.", None),
    ], viz=dict(kind="signs", items=[("Lächeln = Liebe", "😊"), ("Promi-Posts sind für ihn", "⭐"),
                                     ("„ok“ = Heiratsantrag", "💍"), ("Plant das Unmögliche", "🌈")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch jemanden, der delulu ist? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch jemanden, der delulu ist?", handle="@delulu_alex", icon="🦄", col="#9B6BE0")),
]
