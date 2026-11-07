"""TikTok-Folge: Heute ist Alex ... ein Scheinstudent. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), erst nach Freigabe. Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#3E5C9A", top_style="hoodie", pants="#5C5C66", shoes="#FFFFFF")
ERSTI = person_spec(19, girl=True, top="#F2B233", hair="#C98B4A", skin="#F1C9A8")
ROLE, ROLE_TTS, ROLE_SAY = "EIN SCHEINSTUDENT.", "ein Scheinstudent.", "ein Scheinstudent!"
MOODS = dict(MOODS_BASE, wecker="verschlafen, dann trocken", mensa="zufrieden, dann trocken",
             chat="ausweichend, dann trocken", party="feierlich, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"wecker": ["⏰", "😴", "🚩"], "mensa": ["🍝", "🗺️", "🚩"], "chat": ["👵", "⏳", "🚩"], "party": ["🎉", "👨‍🏫", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="SCHEIN-", l2="STUDENT", bg="#2E4A7A", color1="#FFFFFF", accent="#FFE14D",
             pill="#14243F", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🎓", "🎫", "😴", "🚩"))
INTRO_CFG = dict(icon="🎓", bg="#2E4A7A", title_lines=["SCHEINSTUDENT."],
                 house=dict(sky=("#5B7FC0", "#E1ECFF"), walls="#F2F6FC", roof="#14243F", door="#0A1428", lawn="#5DAA5E",
                            accent=("#3E7BDA", "#F2B233"), sun=True),
                 left=("🎫", "SEMESTERTICKET"), right=("😴", "VORLESUNG"), door=("23. SEMESTER", "BALD FERTIG 🎓"),
                 neon=("STUDENT?", "NUR RABATT 💸", "#7FB0FF"), signs=("Bin bald fertig! 🎓", "Studentenrabatt? 💸"),
                 fly=["🎓", "🎫", "💤"], burst=["🎓", "🎫", "😴", "📚", "🍝", "💸", "⏰", "🎉"],
                 extras=[("🎓", 0, 112, 14), ("🎫", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#2E4A7A", clock=None, title="WAS IST EIN SCHEINSTUDENT?", dark=True, lines=[
        ("Ein Scheinstudent ist an der Uni eingeschrieben. Aber nur auf dem Papier.", None),
        ("Er ist im dreiundzwanzigsten Semester. Und war noch nie in einer Vorlesung.", None),
    ], viz=dict(kind="bars", head="SEIN STUDIUM", rows=[("SEMESTER", 1.0, "23.", "#3E7BDA"), ("VORLESUNGEN", 0.02, "0", "#555A66")],
                pills=[("🎫", "Semesterticket: ✅", "#2FA36B"), ("📚", "Vorlesungen besucht: 0", "#E23B3B")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Studieren lohnt sich. Wegen der Rabatte.", None),
    ], viz=dict(kind="stage", box="#F2F6FC", head="🎓 STUDENTENRABATT", head_col="#2E4A7A",
                items=[("🎫", 280, 660, 130, 0, "bob"), ("🎵", 450, 640, 110, 0, "pulse"), ("🍔", 620, 660, 120, 0, "bob"),
                       ("💸", 790, 640, 110, 0, "fly")],
                tags=[("ALLES MIT RABATT 💸", "#2E4A7A")], move="wobble", alex=("smug", "hips", None))),
    dict(id="wecker", bg="#5B6BC9", clock="10:00", title="DER WECKER", dark=True, lines=[
        ("Zehn Uhr. Die Vorlesung hat vor zwei Stunden angefangen.", None),
        ("Er dreht sich um. Vorlesungen sind ja für Leute, die studieren.", None),
    ], viz=dict(kind="stage", box="#2B2F4A", head="🛏️ SCHLAFZIMMER", head_col="#3E5C9A",
                items=[("⏰", 300, 640, 140, 0, "shake"), ("🛏️", 620, 800, 220, 0, "bob"), ("😴", 700, 620, 100, 1, "fly"),
                       ("💤", 820, 600, 80, 1, "fly")],
                tags=[("VORLESUNG: 8:00 📚", "#E23B3B", 300, 820), ("SCHLÄFT WEITER 😴", "#3E5C9A", 620, 980)],
                fx="shock", move="rumble", alex=("sleepy", "idle", None))),
    dict(id="mensa", bg="#2FA36B", clock="12:00", title="IN DER MENSA", dark=True, lines=[
        ("Mittags ist er pünktlich in der Mensa. Zum Studentenpreis.", None),
        ("Das ist das einzige Gebäude der Uni, das er kennt.", None),
    ], viz=dict(kind="stage", box="#E8FFE0", head="🍝 MENSA", head_col="#2E6B34",
                items=[("🍝", 330, 680, 150, 0, "pulse"), ("💶", 520, 640, 90, 0, "bob"), ("🏫", 760, 640, 140, 1, "bob"),
                       ("🗺️", 760, 840, 90, 1, "shake")],
                tags=[("NUR 2,50 € 🎓", "#2E6B34", 330, 860), ("EINZIGES GEBÄUDE 🗺️", "#E23B3B", 640, 980)],
                fx="party", move="wobble", alex=("happy", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="15:00", title="OMA FRAGT", lines=[
        ("Nachmittags fragt Oma, wann er endlich fertig ist.", None),
        ("Er schreibt: Bald, Oma. Das schreibt er seit zehn Jahren.", None),
    ], viz=dict(kind="chat", chat="💬 Oma 👵", bar="#25A366",
                msgs=[(0, "Oma 👵", "Wann bist du denn fertig, Junge? 🎓", "#E07A2E"),
                      (1, "Alex", "Bald, Oma! 📚", "#3E5C9A"),
                      (1, "Oma 👵", "Das hast du 2016 auch gesagt 🤔", "#E07A2E")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="party", bg="#8E5BE0", clock="20:00", title="ERSTI-PARTY", dark=True, lines=[
        ("Abends Erstsemester-Party. Er ist dreiunddreißig.", None),
        ("Die Erstis halten ihn für den Professor.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🎉 ERSTI-PARTY", head_col="#7A3FA8",
                people=[(ERSTI, 800, "Ersti", "shock", None)],
                items=[("🎉", 300, 620, 110, 0, "spin"), ("🍺", 480, 660, 90, 0, "bob"), ("🎂", 330, 820, 90, 0, "bob"),
                       ("👨‍🏫", 560, 820, 120, 1, "pulse")],
                tags=[("33 JAHRE 🎂", "#7A3FA8", 330, 940), ("„HERR PROFESSOR?“ 👨‍🏫", "#E23B3B", 620, 980)],
                fx="party", move="bounce", alex=("happy", "idle", "🍺"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Scheinstudenten erkennst:", None),
        ("Er ist im dreiundzwanzigsten Semester.", None),
        ("Er kennt von der Uni nur die Mensa.", None),
        ("Sein Hauptfach: das Semesterticket.", None),
        ("Und fertig ist er immer: bald.", None),
    ], viz=dict(kind="signs", items=[("23. Semester", "🎓"), ("Kennt nur die Mensa", "🍝"),
                                     ("Hauptfach: Semesterticket", "🎫"), ("Fertig? „Bald!“", "⏳")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Scheinstudenten? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Scheinstudenten?", handle="@ewigerstudent", icon="🎓", col="#2E4A7A")),
]
