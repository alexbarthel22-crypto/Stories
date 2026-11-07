"""TikTok-Folge: Heute ist Alex ... ein Catfish. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#3E7BDA", top_style="hoodie", pants="#5C5C66", shoes="#FFFFFF")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN CATFISH.", "ein Catfish.", "ein Catfish!"
MOODS = dict(MOODS_BASE, profil="stolz, dann trocken", chat="ausweichend, dann trocken", call="nervös, dann trocken",
             treffen="spannend, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"profil": ["🖼️", "🛋️", "🚩"], "chat": ["📞", "🎤", "🚩"], "call": ["📹", "🌅", "🚩"], "treffen": ["🕶️", "😳", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="CATFISH", bg="#1F6F8B", color1="#FFFFFF", accent="#FFE14D",
             pill="#0E3A4A", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🐟", "🎭", "📸", "🚩"))
INTRO_CFG = dict(icon="🐟", bg="#1F6F8B", title_lines=["CATFISH."],
                 house=dict(sky=("#36A2C2", "#DDF6FF"), walls="#EFFAFF", roof="#0E3A4A", door="#0A2A36", lawn="#5DAA5E",
                            accent=("#36B5C2", "#E0457B"), sun=True),
                 left=("🖼️", "FAKE-PROFIL"), right=("🎭", "FILTER"), door=("LEON, 19", "MODEL 🇮🇹"),
                 neon=("100 %", "ECHT 😇", "#5AD8FF"), signs=("Mikro kaputt 🎤", "Kamera auch 📷"),
                 fly=["🐟", "🎭", "📸"], burst=["🐟", "🎭", "📸", "🖼️", "🕶️", "📹", "🪄", "🇮🇹"],
                 extras=[("🕶️", 0, 92, 10), ("🐟", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#1F6F8B", clock=None, title="WAS IST EIN CATFISH?", dark=True, lines=[
        ("Ein Catfish gibt sich im Internet als jemand ganz anderes aus.", None),
        ("Auf dem Profilbild: ein Model. In echt: na ja.", None),
    ], viz=dict(kind="bars", head="PROFIL VS. REALITÄT", rows=[("PROFIL", 1.0, "Model 😍", "#E0457B"), ("ECHT", 0.08, "na ja", "#555A66")],
                pills=[("🖼️", "Profilbild: geklaut", "#E0457B"), ("🪄", "Filter: 14 Stück", "#8E5BE0")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Echt sein ist überbewertet. Filter nicht.", None),
    ], viz=dict(kind="stage", box="#EFFAFF", head="🪄 FILTER-STUDIO", head_col="#1F6F8B",
                items=[("🪄", 320, 660, 150, 0, "shake"), ("✨", 540, 620, 120, 0, "spin"), ("😎", 760, 700, 160, 0, "pulse")],
                tags=[("FILTER: 100 % ✨", "#1F6F8B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="profil", bg="#D9A441", clock="10:00", title="DAS PROFIL", lines=[
        ("Zehn Uhr. Neues Profil: Leon, neunzehn, Model aus Mailand.", None),
        ("In Wahrheit liegt er in Jogginghose auf dem Sofa.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="📱 NEUES PROFIL", head_col="#A8642E",
                items=[("🇮🇹", 300, 620, 110, 0, "bob"), ("🕶️", 450, 620, 100, 0, "bob"), ("🏙️", 620, 620, 110, 0, "bob"),
                       ("🛋️", 540, 840, 150, 1, "shake"), ("🍟", 720, 840, 80, 1, "bob")],
                tags=[("LEON, 19, MAILAND 🇮🇹", "#E0457B", 450, 750), ("REALITÄT: SOFA 🛋️", "#555A66", 540, 980)],
                fx="shock", move="wobble", flash="#FFFFFF", alex=("smug", "idle", "📱"))),
    dict(id="chat", bg="#36B5C2", clock="14:00", title="DER CHAT", lines=[
        ("Mittags schreibt Lena ihm. Sie will telefonieren.", None),
        ("Er schreibt: Mein Mikro ist kaputt. Seit drei Monaten.", None),
    ], viz=dict(kind="chat", chat="💬 Leon 🇮🇹📸", bar="#25A366",
                msgs=[(0, "Lena", "Lass mal telefonieren 📞😊", "#3E7BDA"),
                      (1, "Leon 🇮🇹", "Mikro kaputt 😔 seit 3 Monaten", "#E0457B"),
                      (1, "Lena", "Schon wieder? 🤨", "#3E7BDA")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="call", bg="#5B6BC9", clock="17:00", title="VIDEOCALL", dark=True, lines=[
        ("Siebzehn Uhr. Lena will einen Videocall.", None),
        ("Er schickt ihr stattdessen ein Foto. Von einem Sonnenuntergang.", None),
    ], viz=dict(kind="stage", box="#1C1C22", head="📹 VIDEOANRUF …", head_col="#2FA36B",
                items=[("📹", 330, 660, 150, 0, "shake"), ("🌅", 720, 720, 180, 1, "pulse"), ("❌", 330, 660, 90, 1, "pulse")],
                tags=[("ANRUF ABGELEHNT ❌", "#E23B3B", 330, 860), ("📸 SONNENUNTERGANG", "#F2B233", 720, 960)], fx="anger",
                move="flicker", alex=("shock", "idle", "📱"))),
    dict(id="treffen", bg="#8E5BE0", clock="20:00", title="DAS TREFFEN", dark=True, lines=[
        ("Abends wollen sie sich endlich treffen.", None),
        ("Er kommt nicht. Er sitzt zwei Tische weiter. Mit Sonnenbrille.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="☕ CAFÉ · 20 UHR", head_col="#7A3FA8",
                people=[(LENA, 300, "Lena", "neutral", 1)],
                items=[("🌹", 300, 860, 80, 0, "bob"), ("⏰", 440, 600, 80, 0, "shake"), ("🕶️", 780, 640, 120, 1, "bob"),
                       ("☕", 780, 840, 90, 1, "bob"), ("📰", 860, 760, 90, 1, "shake")],
                tags=[None, ("2 TISCHE WEITER 🕶️", "#7A3FA8", 760, 980)], fx="shock", move="wobble",
                alex=("smug", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Catfish erkennst:", None),
        ("Sein Profilbild sieht aus wie ein Model.", None),
        ("Sein Mikro ist immer kaputt.", None),
        ("Videocalls gibt es nie.", None),
        ("Und zum Treffen kommt er nie.", None),
    ], viz=dict(kind="signs", items=[("Profilbild = Model", "🖼️"), ("Mikro immer kaputt", "🎤"),
                                     ("Nie Videocall", "📹"), ("Kommt nie zum Treffen", "🕶️")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Catfish? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Catfish?", handle="@leon_model19", icon="🐟", col="#1F6F8B")),
]
