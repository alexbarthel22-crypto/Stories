"""TikTok-Folge: Heute ist Alex ... ein Korinthenkacker. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#7A8A99", top_style="cardigan", inner="#FFFFFF", pants="#2F3B52", shoes="#4A3B2A")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN KORINTHENKACKER.", "ein Korinthenkacker.", "ein Korinthenkacker!"
MOODS = dict(MOODS_BASE, treppe="pedantisch, dann trocken", rechnung="kleinlich genau, dann trocken",
             chat="belehrend, dann trocken", spiele="monoton vorlesend, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"treppe": ["📏", "📄", "🚩"], "rechnung": ["🧮", "🪙", "🚩"], "chat": ["✏️", "💀", "🚩"], "spiele": ["📖", "😴", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="KORINTHEN-", l2="KACKER", bg="#5E6B78", color1="#FFFFFF", accent="#FFE14D",
             pill="#2B333B", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🔍", "📏", "✏️", "🚩"))
INTRO_CFG = dict(icon="🔍", bg="#5E6B78", title_lines=["KORINTHENKACKER."],
                 house=dict(sky=("#8A9AAB", "#EEF2F6"), walls="#F7F9FB", roof="#2B333B", door="#1C2228", lawn="#5DAA5E",
                            accent=("#3E7BDA", "#E23B3B"), sun=True),
                 left=("📏", "NACHGEMESSEN"), right=("📋", "HAUSORDNUNG"), door=("BITTE SCHUHE", "EXAKT 90° ➡️"),
                 neon=("FAST", "= FALSCH ❌", "#9FC3FF"), signs=("Eigentlich heißt es … ☝️", "Da fehlt ein Komma ✏️"),
                 fly=["🔍", "📏", "✏️"], burst=["🔍", "📏", "✏️", "📋", "🧮", "§", "📐", "☝️"],
                 extras=[("🔍", 34, 40, 14)])

SCENES = [
    dict(id="what", bg="#5E6B78", clock=None, title="WAS IST EIN KORINTHENKACKER?", dark=True, lines=[
        ("Ein Korinthenkacker nimmt alles ganz genau. Wirklich alles.", None),
        ("Machst du einen Fehler, findet er ihn. Sofort.", None),
    ], viz=dict(kind="bars", head="SEIN ALLTAG", rows=[("REGELN", 1.0, "alle", "#3E7BDA"), ("SPASS", 0.02, "0", "#555A66")],
                pills=[("🔍", "Lupe: immer dabei", "#3E7BDA"), ("✏️", "Rotstift: gespitzt", "#E23B3B")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Fast richtig ist auch falsch.", None),
    ], viz=dict(kind="stage", box="#F7F9FB", head="📐 PRÜFUNG", head_col="#5E6B78",
                items=[("📏", 330, 680, 170, 0, "shake"), ("✅", 640, 640, 100, 0, "bob"), ("❌", 800, 640, 120, 0, "pulse")],
                tags=[("99 % = DURCHGEFALLEN ❌", "#E23B3B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="treppe", bg="#D9A441", clock="08:00", title="IM TREPPENHAUS", lines=[
        ("Acht Uhr. Er misst nach, ob die Fußmatte vom Nachbarn zwei Zentimeter übersteht.", None),
        ("Dann hängt er einen Zettel auf. Mit Paragraphen.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", floor="#C9B48A", head="🏢 TREPPENHAUS", head_col="#A8642E",
                items=[("🚪", 330, 640, 150, 0, "bob"), ("📏", 520, 880, 110, 0, "shake"), ("📄", 720, 660, 140, 1, "pulse"),
                       ("☝️", 860, 600, 80, 1, "bob")],
                tags=[("+2 CM ÜBERSTAND 📏", "#E23B3B", 400, 980), ("§ 14 HAUSORDNUNG", "#2B333B", 720, 820)], fx="anger",
                move="wobble", alex=("angry", "idle", None))),
    dict(id="rechnung", bg="#2FA36B", clock="12:00", title="DIE RECHNUNG", dark=True, lines=[
        ("Mittags teilen sie die Rechnung. Er rechnet alles auf den Cent genau aus.", None),
        ("Tom schuldet ihm noch drei Cent. Für ein Stück Brot.", None),
    ], viz=dict(kind="stage", box="#E8FFE0", head="🧾 RECHNUNG", head_col="#2E6B34",
                people=[(TOM, 800, "Tom", "neutral", 1)],
                items=[("🧾", 300, 660, 140, 0, "bob"), ("🧮", 480, 680, 120, 0, "shake"), ("🍞", 420, 860, 90, 1, "bob"),
                       ("🪙", 560, 860, 80, 1, "pulse")],
                tags=[None, ("TOM SCHULDET: 0,03 € 🪙", "#E23B3B", 540, 980)], fx="anger", move="wobble",
                alex=("smug", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="16:00", title="DER CHAT", lines=[
        ("Nachmittags schreibt Lena: Treffen uns um acht bei mir.", None),
        ("Er antwortet: Es heißt zwanzig Uhr. Und da fehlt ein Komma.", None),
    ], viz=dict(kind="chat", chat="🍕 Pizzaabend", bar="#25A366",
                msgs=[(0, "Lena", "treffen uns um 8 bei mir 🍕", "#3E7BDA"),
                      (1, "Alex", "*um 20:00 Uhr. Und da fehlt ein Komma.", "#555A66"),
                      (1, "Lena", "Du bist ausgeladen 💀", "#3E7BDA")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="spiele", bg="#8E5BE0", clock="20:00", title="SPIELEABEND", dark=True, lines=[
        ("Abends Spieleabend. Er liest vorher die komplette Anleitung vor.", None),
        ("Vierzig Seiten. Als er fertig ist, sind alle gegangen.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🎲 SPIELEABEND", head_col="#7A3FA8",
                items=[("📖", 330, 680, 170, 0, "bob"), ("🎲", 620, 640, 90, 0, "spin"), ("😴", 760, 640, 90, 0, "fly"),
                       ("🚪", 760, 820, 130, 1, "shake")],
                tags=[("40 SEITEN 📖", "#7A3FA8", 330, 860), ("ALLE WEG 🚪", "#E23B3B", 760, 980)], fx="shock",
                move="wobble", alex=("happy", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Korinthenkacker erkennst:", None),
        ("Er misst alles nach.", None),
        ("Er rechnet auf den Cent genau.", None),
        ("Er korrigiert jede Nachricht.", None),
        ("Und er liest jede Anleitung komplett vor.", None),
    ], viz=dict(kind="signs", items=[("Misst alles nach", "📏"), ("Rechnet auf den Cent", "🪙"),
                                     ("Korrigiert jede Nachricht", "✏️"), ("Liest jede Anleitung vor", "📖")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Korinthenkacker? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Korinthenkacker?", handle="@genau_alex", icon="🔍", col="#5E6B78")),
]
