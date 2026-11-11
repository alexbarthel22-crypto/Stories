"""TikTok-Folge: Heute ist Alex ... ein Looksmaxxer. Alltags-Comedy, Jugendliche 2026, nur Freunde/Bros.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), erst nach Freigabe. Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#2B2F3A", top_style="tee", pants="#5C5C66", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN LOOKSMAXXER.", "ein Looksmaxxer.", "ein Looksmaxxer!"
INTRO_LEN = 3.3
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45)
MOODS = dict(MOODS_BASE, tape="ernst wie ein Tutorial, dann trocken", foto="pedantisch, dann trocken",
             mewing="angestrengt, dann trocken", chat="selbstverliebt, dann trocken", lachen="todernst, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"tape": ["🩹", "😶", "🚩"], "foto": ["📸", "🙄", "🚩"], "mewing": ["👅", "🤐", "🚩"],
             "chat": ["📊", "💀", "🚩"], "lachen": ["😐", "😂", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="LOOKS-", l2="MAXXER", bg="#1F6F8B", color1="#FFFFFF", accent="#FFE14D",
             pill="#0E3A4A", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🗿", "🪞", "📐", "🚩"))
INTRO_CFG = dict(icon="🗿", bg="#1F6F8B", title_lines=["LOOKSMAXXER."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#36A2C2", "#DDF6FF"), walls="#EFFAFF", roof="#0E3A4A", door="#0A2A36", lawn="#5DAA5E",
                            accent=("#36B5C2", "#F2C94C"), sun=True),
                 left=("🪞", "SPIEGEL 24/7"), right=("📐", "KIEFER-WINKEL"), door=("NICHT LACHEN", "FALTEN! 😐"),
                 neon=("JAWLINE", "IS LIFE 🗿", "#5AD8FF"), signs=("Mewing läuft 🤐", "Bin heute 7/10 📊"),
                 fly=["🗿", "🪞", "📐"], burst=["🗿", "🪞", "📐", "🧴", "💆", "😐", "📊", "✨"],
                 extras=[("🪞", 36, 40, 14), ("🧴", -36, 40, 12)])

SCENES = [
    dict(id="what", bg="#1F6F8B", clock=None, title="WAS IST EIN LOOKSMAXXER?", dark=True, lines=[
        ("Ein Looksmaxxer will das Maximum aus seinem Gesicht rausholen.", None),
        ("Er hat eine Hautpflege-Routine mit zwölf Schritten. Hausaufgaben: null.", None),
    ], viz=dict(kind="bars", enter="flip", head="ROUTINE VS. SCHULE", rows=[("SKINCARE", 1.0, "12 Schritte", "#36B5C2"), ("SCHULE", 0.02, "0", "#555A66")],
                pills=[("🪞", "Spiegel-Zeit: 2 Std.", "#1F6F8B"), ("📐", "Kiefer: wird vermessen", "#E07A2E")])),
    dict(id="tape", bg="#5B6BC9", clock="06:00", title="DIE NACHT", dark=True, lines=[
        ("Er schläft mit Tape auf dem Mund. Für die Jawline.", None),
        ("Sein Bro übernachtet bei ihm und denkt, er wurde entführt.", None),
    ], viz=dict(kind="stage", **_BIG, enter="zoom", box="#2B2F4A", head="🌙 ÜBERNACHTUNG", head_col="#3E4A9C",
                items=[("🛏️", 300, 680, 150, 0, "bob"), ("🩹", 300, 600, 80, 0, "pulse"), ("😱", 640, 640, 120, 1, "shake"),
                       ("🚨", 800, 640, 90, 1, "pulse")],
                tags=[("TAPE = JAWLINE 🗿", "#3E4A9C", 330, 820), ("„BRO, WURDEST DU ENTFÜHRT?!“", "#E23B3B", 540, 990)],
                fx="shock", move="flicker", alex=("neutral", "idle", None))),
    dict(id="lachen", bg="#E07A2E", clock="07:30", title="NICHT LACHEN", dark=True, lines=[
        ("Tom erzählt den besten Witz des Jahres. Alle lachen.", None),
        ("Nur Alex nicht. Lachen gibt Falten. Bro.", None),
    ], viz=dict(kind="stage", **_BIG, enter="drop", box="#FFF0E6", head="😂 DER BESTE WITZ", head_col="#A8642E",
                people=[(TOM, 820, "Tom", "happy", None)],
                items=[("😂", 260, 620, 110, 0, "pulse"), ("🤣", 420, 620, 100, 0, "pulse"), ("😐", 610, 870, 100, 1, "bob")],
                tags=[("ALLE: 😂😂😂", "#2B2F3A", 330, 780), ("ALEX: 😐 (FALTEN!)", "#E23B3B", 360, 990)],
                fx="shock", move="bounce", alex=("neutral", "idle", None))),
    dict(id="foto", bg="#36B5C2", clock="12:00", title="DAS GRUPPENFOTO", lines=[
        ("Mittags Gruppenfoto mit den Bros.", None),
        ("Er braucht vierzig Versuche. Wegen dem richtigen Kieferwinkel.", None),
    ], viz=dict(kind="stage", **_BIG, enter="slide_l", box="#E8F7FF", head="📸 GRUPPENFOTO", head_col="#2B5C66",
                people=[(TOM, 820, "Tom", "neutral", 1)],
                items=[("📸", 260, 620, 110, 0, "shake"), ("📐", 430, 620, 100, 1, "spin"), ("🔁", 620, 870, 80, 1, "spin")],
                tags=[("VERSUCH 40 📸", "#2B5C66", 330, 780), ("„NOCH EINS, KIEFER WAR SCHIEF“", "#E23B3B", 470, 990)],
                fx="anger", move="wobble", alex=("smug", "idle", "📱"))),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Erst die Jawline, dann der Rest.", None),
    ], viz=dict(kind="stage", **_BIG, enter="spin", box="#EFFAFF", head="🗿 PRIORITÄTEN", head_col="#1F6F8B",
                items=[("🗿", 300, 680, 160, 0, "bob"), ("1️⃣", 540, 680, 100, 0, "pulse"), ("📚", 780, 680, 120, 0, "shake")],
                tags=[("JAWLINE > ALLES", "#1F6F8B", 540, 960)], move="chomp", alex=("smug", "hips", None))),
    dict(id="mewing", bg="#2FA36B", clock="15:00", title="MEWING", dark=True, lines=[
        ("Lena fragt ihn was. Er antwortet nicht.", None),
        ("Er ist gerade am Mewing. Zunge an den Gaumen. Seit drei Stunden.", None),
    ], viz=dict(kind="stage", **_BIG, enter="rise", box="#E8FFE0", head="🤐 MEWING-MODUS", head_col="#2E6B34",
                people=[(LENA, 820, "Lena", "neutral", 1)],
                items=[("❓", 640, 600, 90, 0, "bob"), ("🤐", 300, 640, 120, 1, "pulse"), ("⏱️", 450, 640, 90, 1, "spin")],
                tags=[("„HALLO??“", "#2B2F3A", 380, 790), ("MEWING SEIT 3 STD 🤐", "#2E6B34", 450, 990)],
                fx="anger", move="rumble", alex=("neutral", "idle", None))),
    dict(id="chat", bg="#8E5BE0", clock="21:00", title="DIE BEWERTUNG", dark=True, lines=[
        ("Abends bewertet er im Gruppenchat alle Bros. Mit Punkten von eins bis zehn.", None),
        ("Sich selbst gibt er eine neun. Die Bros geben ihm eine vier.", None),
    ], viz=dict(kind="messenger", enter="slide_r", switch=0, list=[],
                chat=dict(name="Die Bros 🍻", col="#3E7BDA", msgs=[(0, True, "📊 Rating: Tom 5/10, Finn 6/10", "21:00"),
                                                                 (0, True, "Ich: 9/10 🗿", "21:00"),
                                                                 (1, False, "Tom: Bro, du bist ne 4 💀", "21:01"),
                                                                 (1, False, "Finn: 3 😂", "21:01")]),
                alex=("angry", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Looksmaxxer erkennst:", None),
        ("Er lacht nie. Wegen der Falten.", None),
        ("Er schläft mit Tape auf dem Mund.", None),
        ("Er antwortet nicht, weil er mewt.", None),
        ("Und er bewertet alle mit Punkten.", None),
    ], viz=dict(kind="signs", slide=True, items=[("Lacht nie (Falten!)", "😐"), ("Schläft mit Mund-Tape", "🩹"),
                                                 ("Antwortet nicht – mewt", "🤐"), ("Bewertet alle 1–10", "📊")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Looksmaxxer? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Looksmaxxer?", handle="@looksmaxx_alex", icon="🗿", col="#1F6F8B")),
]
