"""TikTok-Folge: Heute ist Alex ... ein Golddigger. Alltags-Comedy, Alex hier klar erwachsen (Anfang 20, Uni/Café) wegen Sugar-Thema, nur Freunde/Bros.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), tighten 1.08 0.22 + match_level. Freigegeben vom Nutzer."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#1C1C22", top_style="tee", pants="#2F3B52", shoes="#FFFFFF", chain="#F2C94C")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
SOPHIE = person_spec(22, girl=True, top="#F2C94C", hair="#E8C77A", skin="#F1C9A8")
ROLE, ROLE_TTS, ROLE_SAY = "EIN GOLDDIGGER.", "ein Golddigger.", "ein Golddigger!"
INTRO_LEN = 3.3
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45)
MOODS = dict(MOODS_BASE, sugar="selbstbewusst wie eine Werbung, dann trocken", iphone="kalt und berechnend, dann trocken", insta="detektivisch, dann trocken",
             bro="schleimig, dann trocken", party="gierig, dann trocken", date="enttäuscht, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"sugar": ["💸", "👀", "🚩"], "iphone": ["📱", "💔", "🚩"], "insta": ["🔍", "🛥️", "🚩"], "bro": ["🏠", "🤝", "🚩"],
             "party": ["🎧", "💰", "🚩"], "date": ["🍔", "😐", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="GOLD-", l2="DIGGER", bg="#B8860B", color1="#FFFFFF", accent="#FFE14D",
             pill="#3A2A06", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("💰", "⛏️", "💎", "🚩"))
INTRO_CFG = dict(icon="⛏️", bg="#B8860B", title_lines=["GOLDDIGGER."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#E5B53A", "#FFF3C4"), walls="#FFF8E1", roof="#8A6206", door="#5A3E06", lawn="#5DAA5E",
                            accent=("#F2C94C", "#1C1C22"), sun=True),
                 left=("💎", "SUCHT REICH"), right=("⛏️", "AM GRABEN"), door=("NUR MIT", "PORSCHE 🏎️"),
                 neon=("LIEBE?", "NUR MIT KOHLE 💰", "#FFD24A"), signs=("Was fährt dein Vater? 🏎️", "Habt ihr 'nen Pool? 🏊"),
                 fly=["💰", "💎", "🪙"], burst=["⛏️", "💰", "💎", "🪙", "🏎️", "🛥️", "💳", "👑"],
                 extras=[("⛏️", 36, 40, 14), ("😎", 0, 104, 13)])

SCENES = [
    dict(id="what", bg="#B8860B", clock=None, title="WAS IST EIN GOLDDIGGER?", dark=True, lines=[
        ("Ein Golddigger sucht keine Liebe. Er sucht Kohle.", None),
        ("Die erste Frage beim Kennenlernen: Was arbeitet dein Vater?", None),
    ], viz=dict(kind="bars", enter="zoom", head="LIEBE VS. KONTOSTAND", rows=[("LIEBE", 0.03, "egal", "#555A66"), ("KONTO", 1.0, "alles", "#F2C94C")],
                pills=[("💰", "Interessiert an: Geld", "#B8860B"), ("❤️", "Gefühle: optional", "#E0457B")])),
    dict(id="sugar", bg="#E0457B", clock="07:00", title="DAS DATING-PROFIL", dark=True, lines=[
        ("Sein Dating-Profil: Alex, zweiundzwanzig. Sucht Sugar Mami oder Sugar Daddy.", "Sein Dating-Profil: Aleks, zweiundzwanzig. Sucht Sugar Mami oder Sugar Daddy."),
        ("Filter: Alter egal. Hauptsache Yacht.", None),
    ], viz=dict(kind="stage", **_BIG, enter="slide_r", box="#FFF0F6", head="💘 DATING-APP · FILTER", head_col="#C2185B",
                items=[("👵", 250, 620, 100, 0, "bob"), ("👴", 400, 620, 100, 0, "bob"), ("💳", 620, 620, 100, 0, "pulse"),
                       ("🛥️", 790, 620, 110, 1, "bob")],
                tags=[("SUCHT: SUGAR MAMI / DADDY 💸", "#C2185B", 540, 790), ("ALTER: EGAL · YACHT: PFLICHT 🛥️", "#2B2F3A", 540, 990)],
                fx="shock", move="bounce", alex=("smug", "idle", "📱"))),
    dict(id="iphone", bg="#C0392B", clock="08:00", title="DAS IPHONE", dark=True, lines=[
        ("Acht Uhr in der Uni. Lena kommt mit einem gebrauchten Handy.", None),
        ("Mittags ist Alex Single. Er sagt: Ich brauch jemanden mit Zukunft.", None),
    ], viz=dict(kind="stage", **_BIG, enter="drop", box="#FFF0F0", head="📱 LENAS NEUES HANDY", head_col="#C0392B",
                people=[(LENA, 820, "Lena", "happy", 1)],
                items=[("📱", 280, 620, 120, 0, "shake"), ("🏷️", 440, 620, 90, 0, "bob"), ("💔", 600, 640, 100, 1, "pulse")],
                tags=[("GEBRAUCHT 😬", "#2B2F3A", 360, 780), ("„ICH BRAUCH ZUKUNFT“", "#B8860B", 400, 990)],
                fx="shock", move="rumble", alex=("smug", "idle", None))),
    dict(id="insta", bg="#5B6BC9", clock="10:00", title="DIE RECHERCHE", dark=True, lines=[
        ("Bevor er jemanden anschreibt, checkt er ihr Insta.", None),
        ("Kein Urlaubsfoto mit Yacht? Kein Like.", None),
    ], viz=dict(kind="stage", **_BIG, enter="flip", box="#EEF0FF", head="🔍 INSTA-CHECK", head_col="#3E4A9C",
                items=[("🔍", 260, 620, 110, 0, "shake"), ("🏖️", 430, 620, 100, 0, "bob"), ("🛥️", 600, 620, 110, 0, "bob")],
                tags=[("YACHT? ✅ / ❌", "#3E4A9C", 540, 790), ("KEINE YACHT = KEIN LIKE", "#E23B3B", 540, 990)],
                move="wobble", alex=("smug", "idle", "📱"))),
    dict(id="bro", bg="#2FA36B", clock="14:00", title="DER NEUE BRO", dark=True, lines=[
        ("Nachmittags hat er plötzlich einen neuen besten Bro: Finn.", None),
        ("Finn hat einen Pool, eine PS5 und einen Vater mit Porsche.", None),
    ], viz=dict(kind="messenger", enter="slide_r", switch=1,
                list=[(0, "Bro Tom 🤝", "Bro? Wo bist du heute? 😢", "14:02", 3, "#36B5C2"),
                      (0, "Finn 💎", "Kannst gern rumkommen", "13:58", 0, "#F2C94C")],
                chat=dict(name="Finn 💎", col="#F2C94C", msgs=[(1, True, "Bro!!! Bester Mann 🤝👑", "14:05"),
                                                             (1, True, "Wann darf ich in euren Pool? 🏊🏎️", "14:05"),
                                                             (1, False, "Wir kennen uns seit gestern 😐", "14:06")]),
                alex=("happy", "idle", "📱"))),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Wahre Liebe hat einen Pool.", None),
    ], viz=dict(kind="stage", **_BIG, enter="spin", box="#FFF8E1", head="💘 WAHRE LIEBE", head_col="#B8860B",
                items=[("💘", 300, 680, 150, 0, "pulse"), ("➡️", 540, 680, 100, 0, "pulse"), ("🏊", 780, 680, 150, 0, "bob")],
                tags=[("LIEBE = POOL 🏊", "#B8860B", 540, 960)], move="chomp", alex=("smug", "hips", None))),
    dict(id="party", bg="#8E5BE0", clock="20:00", title="DIE PARTY", dark=True, lines=[
        ("Abends auf der Party redet er nur mit Sophie. Sie hat die teuersten Kopfhörer.", None),
        ("Dann erfährt er: Die sind nur geliehen. Er ist sofort weg.", None),
    ], viz=dict(kind="stage", **_BIG, enter="slide_l", box="#F3EAFE", head="🎉 HOUSEPARTY", head_col="#7A3FA8",
                people=[(SOPHIE, 820, "Sophie", "happy", 1)],
                items=[("🎧", 300, 620, 120, 0, "pulse"), ("💸", 470, 620, 90, 0, "spin"), ("🏃", 330, 860, 110, 1, "shake")],
                tags=[("NUR GELIEHEN 😐", "#2B2F3A", 380, 770), ("ALEX: WEG 💨", "#E23B3B", 470, 990)],
                fx="shock", move="bounce", alex=("smug", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Golddigger erkennst:", None),
        ("Er sucht Sugar Mamis und Sugar Daddys.", None),
        ("Gebrauchtes Handy? Schluss.", None),
        ("Sein bester Bro hat immer einen Pool.", None),
        ("Und seine erste Frage: Was arbeitet dein Vater?", None),
    ], viz=dict(kind="signs", slide=True, items=[("Sucht Sugar Mami/Daddy", "💸"), ("Gebrauchtes Handy = Schluss", "📱"),
                                                 ("Bester Bro hat einen Pool", "🏊"), ("„Was arbeitet dein Vater?“", "💰")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Golddigger? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Golddigger?", handle="@golddigger_alex", icon="⛏️", col="#B8860B")),
]
