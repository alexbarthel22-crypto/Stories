"""TikTok-Folge: Heute ist Alex ... ein Bad Boy. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), erst nach Freigabe. Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#1C1C22", top_style="hoodie", pants="#2B2F3A", shoes="#1C1C22")
ROLE, ROLE_TTS, ROLE_SAY = "EIN BAD BOY.", "ein Bad Boy.", "ein Bad Boy!"
INTRO_LEN = 3.3
MOODS = dict(MOODS_BASE, kurs="cool, dann trocken", chat="lässig, dann trocken", roller="dramatisch cool, dann trocken",
             nacht="großspurig, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"kurs": ["⏰", "🪑", "🚩"], "chat": ["💬", "🙄", "🚩"], "roller": ["🛵", "🐢", "🚩"], "nacht": ["🌙", "📞", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="BAD", l2="BOY", bg="#1C1C22", color1="#FFFFFF", accent="#FFE14D",
             pill="#E23B3B", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🕶️", "🛵", "😎", "🚩"))
INTRO_CFG = dict(icon="😎", bg="#2B2F3A", title_lines=["BAD BOY."],
                 house=dict(sky=("#4A4F66", "#C9CDD8"), walls="#E6E8EE", roof="#1C1C22", door="#0A0A0E", lawn="#5DAA5E",
                            accent=("#E23B3B", "#1C1C22"), sun=True),
                 left=("🕶️", "AUCH NACHTS"), right=("🛵", "„MASCHINE“"), door=("BETRETEN", "AUF EIGENE GEFAHR"),
                 neon=("NO", "RULES 😎", "#FF4A4A"), signs=("Regeln? Nö 😎", "Bin um 22:30 zu Hause 🏠"),
                 fly=["😎", "🔥", "🕶️"], burst=["😎", "🕶️", "🛵", "🔥", "⛓️", "🖤", "💀", "🎸"],
                 extras=[("🕶️", 0, 92, 10), ("⛓️", 20, 50, 10)])

_BIG = dict(tag_size=48, head_size=50, item_scale=1.35)
SCENES = [
    dict(id="what", bg="#2B2F3A", clock=None, title="WAS IST EIN BAD BOY?", dark=True, lines=[
        ("Ein Bad Boy will gefährlich und geheimnisvoll wirken.", None),
        ("Lederjacke, Sonnenbrille, immer schlecht gelaunt. Auch wenn die Sonne scheint.", None),
    ], viz=dict(kind="bars", head="IMAGE VS. REALITÄT", rows=[("IMAGE", 1.0, "gefährlich", "#E23B3B"), ("REALITÄT", 0.12, "harmlos", "#555A66")],
                pills=[("🧥", "Lederjacke: auch im Sommer", "#2B2F3A"), ("🕶️", "Sonnenbrille: auch nachts", "#555A66")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Regeln sind für die anderen.", None),
    ], viz=dict(kind="stage", box="#E6E8EE", head="📜 REGELN", head_col="#1C1C22",
                items=[("📜", 330, 680, 160, 0, "shake"), ("🚫", 330, 680, 110, 0, "pulse"), ("😎", 740, 680, 170, 0, "bob")],
                tags=[("REGELN? NÖ 😎", "#E23B3B")], move="wobble", alex=("smug", "hips", None), **_BIG)),
    dict(id="kurs", bg="#D9A441", clock="08:00", title="IM KURS", lines=[
        ("Acht Uhr. Er kommt zu spät. Natürlich mit Absicht.", None),
        ("Dann setzt er sich in die letzte Reihe und kippelt mit dem Stuhl. Lebensgefährlich.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="📚 RAUM 204", head_col="#A8642E",
                items=[("⏰", 300, 650, 140, 0, "shake"), ("🚪", 520, 650, 130, 0, "bob"), ("🪑", 740, 760, 170, 1, "shake")],
                tags=[("10 MIN ZU SPÄT 😎", "#2B2F3A", 360, 870), ("KIPPELT!!! 🪑", "#E23B3B", 700, 980)], fx="shock",
                move="wobble", alex=("smug", "hips", None), **_BIG)),
    dict(id="chat", bg="#36B5C2", clock="13:00", title="DIE NACHRICHT", lines=[
        ("Mittags schreibt Lena ihm.", None),
        ("Er antwortet nach sechs Stunden. Mit: k. Bad Boys schreiben nicht viel.", None),
    ], viz=dict(kind="messenger", switch=0, list=[],
                chat=dict(name="Lena", col="#46B39A", msgs=[(0, False, "Hey, wie geht's dir? 😊", "13:00"),
                                                            (1, True, "k.", "19:04"),
                                                            (1, False, "… k?? 🙄", "19:05")]),
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="roller", bg="#C0392B", clock="17:00", title="SEINE MASCHINE", dark=True, lines=[
        ("Nachmittags fährt er mit seiner Maschine vor. Laut und gefährlich.", None),
        ("Es ist ein Roller. Mit fünfundzwanzig Sachen.", None),
    ], viz=dict(kind="stage", box="#E6E6EA", floor="#8C8C96", head="🏍️ VROOOM", head_col="#1C1C22",
                items=[("🔊", 280, 620, 110, 0, "shake"), ("🔥", 420, 620, 100, 0, "pulse"), ("🛵", 600, 780, 220, 1, "shake"),
                       ("💨", 380, 840, 100, 1, "fly"), ("🐢", 820, 860, 90, 1, "bob")],
                tags=[None, ("MAX. 25 KM/H 🐢", "#E23B3B", 600, 980)], fx="shock", move="rumble",
                alex=("smug", "hips", None), **_BIG)),
    dict(id="nacht", bg="#2B2F4A", clock="22:30", title="DIE NACHT", dark=True, lines=[
        ("Abends erzählt er allen: Ich mach heute die Nacht durch.", None),
        ("Um halb elf ruft Mama an. Er muss nach Hause.", None),
    ], viz=dict(kind="stage", box="#1C1C22", head="🌙 PARTY", head_col="#7A3FA8",
                items=[("🌙", 300, 640, 140, 0, "bob"), ("🎉", 480, 640, 110, 0, "spin"), ("📞", 720, 680, 150, 1, "shake"),
                       ("🏠", 840, 840, 110, 1, "bob")],
                tags=[("„NACHT DURCH!“ 🌙", "#7A3FA8", 380, 860), ("22:30 – MAMA 📞", "#E0457B", 640, 980)], fx="shock",
                move="wobble", flash="#FFFFFF", alex=("shock", "idle", "📱"), **_BIG)),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Bad Boy erkennst:", None),
        ("Lederjacke. Auch im Sommer.", None),
        ("Sonnenbrille. Auch nachts.", None),
        ("Er antwortet nur mit: k.", None),
        ("Und sein Motorrad ist ein Roller.", None),
    ], viz=dict(kind="signs", items=[("Lederjacke, auch im Sommer", "🧥"), ("Sonnenbrille, auch nachts", "🕶️"),
                                     ("Antwortet nur mit „k.“", "💬"), ("Motorrad = Roller", "🛵")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Bad Boy? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Bad Boy?", handle="@badboy_alex", icon="😎", col="#2B2F3A")),
]
