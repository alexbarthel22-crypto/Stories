"""TikTok-Folge: Heute ist Alex ... ein 31er (Petze, verpetzt jeden). Alltags-Comedy über Klischees.
Gesprochen: „Einunddreißiger“. Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), erst nach Freigabe. Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#8C96A8", top_style="hoodie", pants="#2F3B52", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN 31ER.", "ein Einunddreißiger.", "ein Einunddreißiger!"
INTRO_LEN = 3.3
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45)
MOODS = dict(MOODS_BASE, buero="petzend und wichtig, dann trocken", chat="unschuldig tuend, dann trocken",
             nachbar="empört und pflichtbewusst, dann trocken", spiel="beleidigt, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"buero": ["⏰", "📞", "🚩"], "chat": ["📸", "😱", "🚩"], "nachbar": ["🚗", "📞", "🚩"], "spiel": ["🎲", "🗣️", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="31ER", bg="#4A5568", color1="#FFFFFF", accent="#FFE14D",
             pill="#1C2230", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🐀", "📸", "🗣️", "🚩"))
INTRO_CFG = dict(icon="🐀", bg="#4A5568", title_lines=["31ER."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#7A869C", "#E6EAF2"), walls="#F2F4F8", roof="#1C2230", door="#2B2F3A", lawn="#5DAA5E",
                            accent=("#E23B3B", "#3E7BDA"), sun=True),
                 left=("👀", "ALLES GESEHEN"), right=("📞", "KURZWAHL CHEF"), door=("ICH SAG'S", "NUR MAL 🗣️"),
                 neon=("PETZE", "DES JAHRES 🏆", "#9FC3FF"), signs=("Ich sag's dem Chef! 🗣️", "Nur zur Info 🤓"),
                 fly=["🐀", "📸", "🗣️"], burst=["🐀", "📸", "🗣️", "📞", "👀", "📝", "🚨", "🤫"],
                 extras=[("📝", -34, 40, 12), ("📱", 34, 40, 13)])

SCENES = [
    dict(id="what", bg="#4A5568", clock=None, title="WAS IST EIN 31ER?", dark=True, lines=[
        ("Ein 31er verpetzt jeden. Wirklich jeden.", "Ein Einunddreißiger verpetzt jeden. Wirklich jeden."),
        ("Kaum passiert irgendwas, weiß es der Chef schon.", None),
    ], viz=dict(kind="bars", head="LOYALITÄT VS. PETZEN", rows=[("LOYALITÄT", 0.02, "0 %", "#555A66"), ("PETZEN", 1.0, "100 %", "#E23B3B")],
                pills=[("🗣️", "Geheimnis? Nicht bei ihm", "#E23B3B"), ("📸", "Screenshot? Schon verschickt", "#3E7BDA")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Wer petzt, gewinnt. Glaubt er.", None),
    ], viz=dict(kind="stage", **_BIG, box="#F2F4F8", head="🏆 PETZE DES JAHRES", head_col="#4A5568",
                items=[("🐀", 300, 680, 160, 0, "bob"), ("🏆", 540, 660, 150, 0, "pulse"), ("🗣️", 780, 680, 140, 0, "shake")],
                tags=[("WER PETZT, GEWINNT? 🤔", "#E23B3B", 540, 960)], move="wobble", alex=("smug", "hips", None))),
    dict(id="buero", bg="#D9A441", clock="08:00", title="IM BÜRO", lines=[
        ("Acht Uhr. Tom kommt fünf Minuten zu spät.", None),
        ("Der Chef weiß es schon, bevor Tom seine Jacke ausgezogen hat.", None),
    ], viz=dict(kind="stage", **_BIG, box="#FFF4E0", head="🏢 BÜRO", head_col="#A8642E",
                people=[(TOM, 820, "Tom", "neutral", 1)],
                items=[("⏰", 250, 600, 100, 0, "shake"), ("🧥", 430, 600, 95, 0, "bob"), ("📞", 620, 610, 95, 1, "shake")],
                tags=[("5 MIN ZU SPÄT ⏰", "#E07A2E", 400, 780), ("CHEF WEISS ES SCHON 📞", "#E23B3B", 390, 990)],
                fx="shock", move="rumble", alex=("smug", "idle", "📱"))),
    dict(id="chat", bg="#36B5C2", clock="12:00", title="DER SCREENSHOT", lines=[
        ("Mittags lästert Lena im Gruppenchat über den Chef.", None),
        ("Eine Minute später hat der Chef den Screenshot.", None),
    ], viz=dict(kind="messenger", switch=1,
                list=[(0, "Kollegen ☕", "Lena: Der Chef nervt heute 🙄", "12:01", 1, "#46B39A"),
                      (0, "Chef 👔", "Danke für die Info 👍", "Mo.", 0, "#2B2F3A"),
                      (0, "Mama ❤️", "Hast du gegessen?", "Di.", 0, "#E07A2E")],
                chat=dict(name="Chef 👔", col="#2B2F3A", msgs=[(1, True, "📸 [Screenshot: Lena]", "12:02"),
                                                             (1, True, "Nur zur Info 🤓", "12:02"),
                                                             (1, False, "Danke, Alex. 👍", "12:03")]),
                alex=("smug", "idle", "📱"))),
    dict(id="nachbar", bg="#C0392B", clock="17:00", title="DER NACHBAR", dark=True, lines=[
        ("Nachmittags parkt der Nachbar zwei Minuten im Halteverbot.", None),
        ("Alex hat schon Fotos gemacht. Und das Ordnungsamt angerufen.", None),
    ], viz=dict(kind="stage", **_BIG, box="#E6E6EA", floor="#8C8C96", head="🚫 HALTEVERBOT", head_col="#C0392B",
                items=[("🚗", 330, 830, 170, 0, "shake"), ("🚫", 190, 610, 85, 0, "pulse"), ("📸", 640, 640, 110, 1, "shake"),
                       ("📞", 800, 640, 100, 1, "shake")],
                tags=[("2 MIN ⏱️", "#2B2F3A", 430, 610), ("ORDNUNGSAMT KOMMT 🚨", "#E23B3B", 540, 990)],
                fx="shock", move="rumble", flash="#FF3B3B", alex=("smug", "idle", "📱"))),
    dict(id="spiel", bg="#8E5BE0", clock="20:00", title="SPIELEABEND", dark=True, lines=[
        ("Abends Spieleabend. Alex verliert.", None),
        ("Also verrät er allen, wer beim letzten Mal geschummelt hat. Und wer heimlich in Tom verliebt ist.", None),
    ], viz=dict(kind="stage", **_BIG, box="#F3EAFE", head="🎲 SPIELEABEND", head_col="#7A3FA8",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("🎲", 250, 610, 100, 0, "spin"), ("🃏", 250, 830, 100, 0, "bob"), ("🗣️", 450, 830, 110, 1, "shake"),
                       ("💘", 620, 830, 85, 1, "pulse")],
                tags=[("VERLOREN 😤", "#2B2F3A", 545, 615), ("ALLES AUSGEPLAUDERT 🗣️", "#E23B3B", 470, 990)],
                fx="shock", move="wobble", alex=("angry", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen 31er erkennst:", "Woran du einen Einunddreißiger erkennst:"),
        ("Er weiß alles. Und erzählt alles.", None),
        ("Screenshots gehen direkt an den Chef.", None),
        ("Das Ordnungsamt hat er auf Kurzwahl.", None),
        ("Und Geheimnisse hält er null Sekunden.", None),
    ], viz=dict(kind="signs", items=[("Weiß alles, erzählt alles", "🗣️"), ("Screenshots an den Chef", "📸"),
                                     ("Ordnungsamt auf Kurzwahl", "📞"), ("Geheimnis hält 0 Sekunden", "🤐")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen 31er? Markier sie oder ihn!", "Kennst du auch einen Einunddreißiger? Markier sie oder ihn!"),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen 31er?", handle="@petze_alex", icon="🐀", col="#4A5568")),
]
