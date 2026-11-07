"""TikTok-Folge: Heute ist Alex ... ein AfD-Wähler. Politische Satire über Klischee-Verhalten (Gegenstück: Linken-Wähler).
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#3E7BDA", top_style="tee", pants="#5C5C66", shoes="#FFFFFF")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN AFD-WÄHLER.", "ein A-eff-De-Wähler.", "ein A-eff-De-Wähler!"
MOODS = dict(MOODS_BASE, zeitung="empört, dann trocken", imbiss="schimpfend, dann trocken und ironisch",
             chat="aufgeregt, dann trocken", abend="empört, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"zeitung": ["📰", "😡", "🚩"], "imbiss": ["🥙", "🙃", "🚩"], "chat": ["‼️", "🔎", "🚩"], "abend": ["📺", "📝", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="AFD-", l2="WÄHLER", bg="#1F5FA8", color1="#FFFFFF", accent="#FFE14D",
             pill="#0E2E54", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("📢", "📰", "‼️", "🚩"))
INTRO_CFG = dict(icon="📢", bg="#1F5FA8", title_lines=["AFD-WÄHLER."],
                 house=dict(sky=("#4A86D0", "#E1EEFF"), walls="#F2F6FC", roof="#0E2E54", door="#0A1E36", lawn="#5DAA5E",
                            accent=("#3E7BDA", "#E23B3B"), sun=True),
                 left=("📰", "NUR TITEL"), right=("📺", "AUFREGER"), door=("FRÜHER WAR", "ALLES BESSER"),
                 neon=("MAN DARF", "JA NIX 📢", "#5AA8FF"), signs=("Man darf ja nix sagen! 📢", "Früher war alles besser 🕰️"),
                 fly=["📢", "‼️", "📰"], burst=["📢", "‼️", "📰", "🕰️", "😡", "📺", "📝", "🔊"],
                 extras=[("📰", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#1F5FA8", clock=None, title="WAS IST EIN AFD-WÄHLER?", dark=True, lines=[
        ("Ein AfD-Wähler findet, dass früher alles besser war.", "Ein A-eff-De-Wähler findet, dass früher alles besser war."),
        ("Und dass man ja gar nichts mehr sagen darf. Sagt er. Den ganzen Tag. Laut.", None),
    ], viz=dict(kind="bars", head="SEIN TAG", rows=[("MECKERN", 1.0, "24/7", "#E23B3B"), ("LÖSUNGEN", 0.02, "0", "#555A66")],
                pills=[("📢", "„Man darf ja nix sagen!“", "#3E7BDA"), ("🔊", "(sagt er. laut. ständig.)", "#555A66")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Das wird man ja wohl noch sagen dürfen.", None),
    ], viz=dict(kind="stage", box="#F2F6FC", head="📢 MEINUNG", head_col="#1F5FA8",
                items=[("📢", 330, 680, 180, 0, "shake"), ("🗣️", 740, 680, 160, 0, "pulse")],
                tags=[("SAGT ER. JEDEN TAG. 📢", "#1F5FA8")], move="rumble", alex=("angry", "hips", None))),
    dict(id="zeitung", bg="#D9A441", clock="08:00", title="DIE ZEITUNG", lines=[
        ("Acht Uhr. Er liest die Nachrichten. Nur die Überschriften.", None),
        ("Danach ist er sofort empört. Über alles.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="📰 FRÜHSTÜCK", head_col="#A8642E",
                items=[("📰", 330, 680, 170, 0, "bob"), ("☕", 560, 820, 90, 0, "bob"), ("😡", 760, 660, 150, 1, "shake")],
                tags=[("NUR ÜBERSCHRIFTEN 📰", "#3E7BDA", 330, 860), ("EMPÖRT: 100 % 😡", "#E23B3B", 700, 980)],
                fx="anger", move="wobble", flash="#FF3B3B", alex=("angry", "idle", None))),
    dict(id="imbiss", bg="#C0392B", clock="12:00", title="MITTAGSPAUSE", dark=True, lines=[
        ("Mittags schimpft er über Multikulti.", None),
        ("Danach holt er sich seinen Stammdöner. Mit allem und scharf.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="🥙 IMBISS · SEIT 2009", head_col="#C0392B",
                items=[("😤", 330, 660, 140, 0, "shake"), ("🥙", 640, 720, 170, 1, "pulse"), ("🌶️", 800, 640, 80, 1, "bob")],
                tags=[None, ("STAMMKUNDE SEIT 15 JAHREN 🥙", "#2FA36B", 540, 980)], fx="shock", move="wobble",
                alex=("happy", "idle", "🥙"))),
    dict(id="chat", bg="#36B5C2", clock="16:00", title="FAMILIEN-CHAT", lines=[
        ("Nachmittags teilt er im Familien-Chat einen Kettenbrief.", None),
        ("Seine Nichte schickt den Faktencheck. Er schreibt: Das sagen die alle!", None),
    ], viz=dict(kind="chat", chat="👨‍👩‍👧 Familie", bar="#25A366",
                msgs=[(0, "Onkel Alex", "‼️ TEILEN BEVOR ES GELÖSCHT WIRD ‼️", "#1F5FA8"),
                      (1, "Nichte Lena", "Faktencheck: stimmt nicht 🔎", "#2FA36B"),
                      (1, "Onkel Alex", "Das sagen die alle!! 😡", "#1F5FA8")],
                fx="shock", alex=("angry", "idle", "📱"))),
    dict(id="abend", bg="#8E5BE0", clock="20:00", title="DIE WERBUNG", dark=True, lines=[
        ("Abends sieht er in der Werbung ein Gendersternchen.", None),
        ("Er schreibt eine Beschwerde. Drei Seiten. Mit vielen Ausrufezeichen.", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="📺 WERBEPAUSE", head_col="#7A3FA8",
                items=[("📺", 330, 660, 170, 0, "bob"), ("✳️", 330, 650, 70, 0, "pulse"), ("📝", 700, 680, 140, 1, "shake"),
                       ("❗", 840, 600, 80, 1, "pulse"), ("❗", 880, 700, 80, 1, "pulse")],
                tags=[None, ("BESCHWERDE: 3 SEITEN ‼️", "#E23B3B", 540, 980)], fx="shock", move="rumble",
                alex=("angry", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen AfD-Wähler erkennst:", "Woran du einen A-eff-De-Wähler erkennst:"),
        ("Früher war alles besser.", None),
        ("Man darf nichts mehr sagen. Sagt er laut.", None),
        ("Er teilt jeden Kettenbrief.", None),
        ("Und ein Gendersternchen ruiniert seinen Tag.", None),
    ], viz=dict(kind="signs", items=[("Früher war alles besser", "🕰️"), ("„Darf nix sagen“ – laut", "📢"),
                                     ("Teilt jeden Kettenbrief", "‼️"), ("Sternchen ruiniert den Tag", "✳️")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen AfD-Wähler? Markier sie oder ihn!", "Kennst du auch einen A-eff-De-Wähler? Markier sie oder ihn!"),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen AfD-Wähler?", handle="@frueher_alex", icon="📢", col="#1F5FA8")),
]
