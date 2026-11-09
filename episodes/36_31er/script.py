"""TikTok-Folge: Heute ist Alex ... ein 31er (Petze, verpetzt jeden). Alltags-Comedy über Klischees.
Gesprochen: „Einunddreißiger“. Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), erst nach Freigabe. Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#8C96A8", top_style="hoodie", pants="#2F3B52", shoes="#FFFFFF")   # Schüler, 2026
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN 31ER.", "ein Einunddreißiger.", "ein Einunddreißiger!"
INTRO_LEN = 3.3
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45)
MOODS = dict(MOODS_BASE, standort="verschwörerisch, dann trocken", ki="streberhaft wichtig, dann trocken",
             chat="unschuldig tuend, dann trocken", spiel="beleidigt, dann trocken", ex="schleimig und überheblich, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"standort": ["📍", "😱", "🚩"], "ki": ["🤖", "🙋", "🚩"], "chat": ["📸", "😱", "🚩"], "spiel": ["🎮", "🗣️", "🚩"], "ex": ["😏", "💀", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="31ER", bg="#4A5568", color1="#FFFFFF", accent="#FFE14D",
             pill="#1C2230", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🐀", "📸", "🗣️", "🚩"))
INTRO_CFG = dict(icon="🐀", bg="#4A5568", title_lines=["31ER."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#7A869C", "#E6EAF2"), walls="#F2F4F8", roof="#1C2230", door="#2B2F3A", lawn="#5DAA5E",
                            accent=("#E23B3B", "#3E7BDA"), sun=True),
                 left=("👀", "ALLES GESEHEN"), right=("📸", "SCREENSHOTS"), door=("ICH SAG'S", "NUR MAL 🗣️"),
                 neon=("PETZE", "DES JAHRES 🏆", "#9FC3FF"), signs=("Ich sag's der Lehrerin! 🗣️", "Nur zur Info 🤓"),
                 fly=["🐀", "📸", "🗣️"], burst=["🐀", "📸", "🗣️", "📞", "👀", "📝", "🚨", "🤫"],
                 extras=[("📝", -34, 40, 12), ("📱", 34, 40, 13)])

SCENES = [
    dict(id="what", bg="#4A5568", clock=None, title="WAS IST EIN 31ER?", dark=True, lines=[
        ("Ein 31er verpetzt jeden. Wirklich jeden.", "Ein Einunddreißiger verpetzt jeden. Wirklich jeden."),
        ("Kaum passiert irgendwas, wissen es Lehrer und Eltern schon.", None),
    ], viz=dict(kind="bars", enter="flip", head="LOYALITÄT VS. PETZEN", rows=[("LOYALITÄT", 0.02, "0 %", "#555A66"), ("PETZEN", 1.0, "100 %", "#E23B3B")],
                pills=[("🗣️", "Geheimnis? Nicht bei ihm", "#E23B3B"), ("📸", "Screenshot? Schon verschickt", "#3E7BDA")])),
    dict(id="standort", bg="#E07A2E", clock="07:00", title="DER STANDORT", dark=True, lines=[
        ("Sieben Uhr. Sein Bro Tom schreibt seiner Mama: Bin schon in der Schule.", None),
        ("Alex schickt ihr Toms Live-Standort. Tom liegt noch im Bett.", None),
    ], viz=dict(kind="stage", **_BIG, enter="drop", box="#FFF0E6", head="📍 LIVE-STANDORT: TOM", head_col="#A8642E",
                items=[("🏫", 260, 620, 110, 0, "bob"), ("💬", 440, 620, 90, 0, "pulse"), ("🗺️", 700, 640, 130, 1, "bob"),
                       ("📍", 700, 600, 80, 1, "pulse"), ("🛏️", 720, 860, 105, 1, "shake")],
                tags=[("„BIN SCHON IN DER SCHULE“", "#2B2F3A", 470, 745), ("TOM: NOCH IM BETT 🛏️", "#E23B3B", 470, 990)],
                fx="shock", move="bounce", flash="#FFE14D", alex=("smug", "idle", "📱"))),
    dict(id="ki", bg="#D9A441", clock="08:00", title="DIE HAUSAUFGABE", lines=[
        ("Acht Uhr, Mathe. Tom hat die Hausaufgaben von der KI machen lassen.", None),
        ("Alex meldet sich sofort: Frau Müller, mein Bro hat das mit KI gemacht!", None),
    ], viz=dict(kind="stage", **dict(_BIG, tag_size=42), enter="slide_l", box="#FFF4E0", head="📚 MATHE · 8A", head_col="#2E6B34",
                people=[(TOM, 820, "Tom", "neutral", 1)],
                items=[("🤖", 260, 620, 110, 0, "bob"), ("📄", 420, 630, 100, 0, "bob"), ("🙋", 560, 870, 100, 1, "shake")],
                tags=[("HAUSAUFGABE: 100 % KI 🤖", "#3E7BDA", 380, 740), ("„MEIN BRO HAT KI BENUTZT!“ 🗣️", "#E23B3B", 400, 990)],
                fx="anger", move="rumble", alex=("smug", "idle", None))),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Wer petzt, gewinnt. Glaubt er.", None),
    ], viz=dict(kind="stage", **_BIG, enter="spin", box="#F2F4F8", head="🏆 PETZE DES JAHRES", head_col="#4A5568",
                items=[("🐀", 300, 680, 160, 0, "bob"), ("🏆", 540, 660, 150, 0, "pulse"), ("🗣️", 780, 680, 140, 0, "shake")],
                tags=[("WER PETZT, GEWINNT? 🤔", "#E23B3B", 540, 960)], move="chomp", alex=("smug", "hips", None))),
    dict(id="chat", bg="#36B5C2", clock="11:00", title="DER KLASSENCHAT", lines=[
        ("In der Pause lästert Lena im Klassenchat über die Mathelehrerin.", None),
        ("Zwei Minuten später hat die Lehrerin den Screenshot.", None),
    ], viz=dict(kind="messenger", enter="slide_r", switch=1,
                list=[(0, "Klasse 8a 📚", "Lena: Die Müller nervt heute 🙄", "11:01", 4, "#46B39A"),
                      (0, "Frau Müller 👩‍🏫", "Danke für die Info 👍", "Mo.", 0, "#2B2F3A"),
                      (0, "Bro Tom 🤝", "Bro, sag nix der Müller 🙏", "11:00", 1, "#36B5C2")],
                chat=dict(name="Frau Müller 👩‍🏫", col="#2B2F3A", msgs=[(1, True, "📸 [Screenshot: Lena]", "11:02"),
                                                                     (1, True, "Nur zur Info 🤓", "11:02"),
                                                                     (1, False, "Danke, Alex. 👍", "11:03")]),
                alex=("smug", "idle", "📱"))),
    dict(id="spiel", bg="#8E5BE0", clock="19:00", title="ZOCKEN", dark=True, lines=[
        ("Abends zockt er mit seinen Bros. Alex verliert.", None),
        ("Also verrät er allen, wer heimlich in Tom verliebt ist.", None),
    ], viz=dict(kind="stage", **_BIG, enter="zoom", box="#F3EAFE", head="🎮 ONLINE-RUNDE", head_col="#7A3FA8",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("🎮", 250, 610, 100, 0, "shake"), ("💀", 250, 830, 90, 0, "bob"), ("🗣️", 450, 830, 110, 1, "shake"),
                       ("💘", 620, 830, 85, 1, "pulse")],
                tags=[("VERLOREN 😤", "#2B2F3A", 545, 615), ("ALLES AUSGEPLAUDERT 🗣️", "#E23B3B", 470, 990)],
                fx="shock", move="flicker", alex=("angry", "idle", None))),
    dict(id="ex", bg="#C2185B", clock="21:00", title="DIE EX VOM BRO", dark=True, lines=[
        ("Abends trennt sich sein Bro Tom von Lena.", None),
        ("Zehn Minuten später schreibt Alex ihr: Tom war eh ein schlechter Typ. Ich bin viel besser.", None),
    ], viz=dict(kind="messenger", enter="rise", switch=1,
                list=[(0, "Bro Tom 🤝", "Bro, Lena hat Schluss gemacht 💔", "20:51", 2, "#36B5C2"),
                      (0, "Lena", "zuletzt online 20:50", "", 0, "#46B39A"),
                      (0, "Die Bros 🍻", "Tom: ich brauch euch heute 😔", "20:52", 5, "#3E7BDA")],
                chat=dict(name="Lena", col="#46B39A", msgs=[(1, True, "Hey Lena 😏 hab gehört, du bist wieder single", "21:01"),
                                                          (1, True, "Ehrlich, Tom war voll der schlechte Typ 🙄", "21:01"),
                                                          (1, True, "Ich wär viel besser für dich 😎💪", "21:02"),
                                                          (1, False, "Ihr seid doch Bros?! 💀", "21:03")]),
                alex=("smug", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen 31er erkennst:", "Woran du einen Einunddreißiger erkennst:"),
        ("Er schickt Live-Standorte an Mamas.", None),
        ("Screenshots gehen direkt an die Lehrer.", None),
        ("Geheimnisse hält er null Sekunden.", None),
        ("Und kaum ist sein Bro getrennt, macht er dessen Ex an.", None),
    ], viz=dict(kind="signs", slide=True, items=[("Live-Standort an Mamas", "📍"), ("Screenshots an die Lehrer", "📸"),
                                                 ("Geheimnis hält 0 Sekunden", "🤐"), ("Macht die Ex vom Bro an", "💔")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen 31er? Markier sie oder ihn!", "Kennst du auch einen Einunddreißiger? Markier sie oder ihn!"),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen 31er?", handle="@petze_alex", icon="🐀", col="#4A5568")),
]
