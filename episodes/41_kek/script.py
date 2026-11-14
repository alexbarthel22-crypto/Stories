"""TikTok-Folge: Heute ist Alex ... ein Kek (Jugendsprache: peinlicher Möchtegern, der sich ständig blamiert).
Alltags-Comedy, Jugendliche 2026, nur Freunde/Bros. Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck), tighten 1.08 0.22 + match_level. Freigegeben vom Nutzer."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#F2C94C", top_style="hoodie", pants="#5C5C66", shoes="#FFFFFF")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
ROLE, ROLE_TTS, ROLE_SAY = "EIN KEK.", "ein Keck.", "ein Keck!"   # Stimme: „Keck“, sonst sagt sie „Keks“
INTRO_LEN = 3.3
MUSIC = "groove"
MUSIC_START = 0.0
MUSIC_DB = -15
MUSIC_DUCK_DB = -6
LOUDNESS = -11
LAYOUT = dict(feet=1732, ky=1.15, phone=1.06)
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.3 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
_BIG = dict(tag_size=52, head_size=54, item_scale=1.45, lively=True)
MOODS = dict(MOODS_BASE, handshake="cool, dann peinlich berührt", witz="unsicher, dann trocken",
             story="angeberisch, dann trocken", rizz="selbstsicher, dann trocken", sport="motiviert, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"handshake": ["🤝", "🤦", "🚩"], "witz": ["😂", "😐", "🚩"], "story": ["🏎️", "💀", "🚩"],
             "rizz": ["😏", "🙄", "🚩"], "sport": ["⚽", "😵", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="KEK", bg="#2FA36B", color1="#FFFFFF", accent="#FFE14D",
             pill="#1F5A28", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🤡", "🍪", "💀", "🚩"))
INTRO_CFG = dict(icon="🍪", bg="#2FA36B", title_lines=["KEK."], sign_x=(190, 890), sign_w=330, sign_size=40,
                 house=dict(sky=("#5BC08A", "#E3FFEC"), walls="#F2FFF6", roof="#1F5A28", door="#0E3A1A", lawn="#5DAA5E",
                            accent=("#F2C94C", "#E23B3B"), sun=True),
                 left=("🤡", "CRINGE-ECKE"), right=("😎", "„SO COOL“"), door=("ACHTUNG:", "STUFE! 🫣"),
                 neon=("SIGMA?", "EHER KEK 🍪", "#7CFF8A"), signs=("Sheesh, Bro! 😎", "Bin voll der Alpha 🐺"),
                 fly=["🍪", "🤡", "💀"], burst=["🍪", "🤡", "💀", "🤦", "😬", "🙈", "🫠", "😎"],
                 extras=[("🕶️", 0, 92, 10), ("🍪", 36, 40, 13)])

SCENES = [
    dict(id="what", bg="#2FA36B", clock=None, title="WAS IST EIN KEK?", dark=True, lines=[
        ("Ein Kek will unbedingt cool sein.", "Ein Keck will unbedingt cool sein."),
        ("Und blamiert sich dabei jedes Mal. Wirklich jedes Mal.", None),
    ], viz=dict(kind="bars", enter="zoom", head="WILL SEIN VS. IST", rows=[("COOL", 0.04, "0 %", "#555A66"), ("CRINGE", 1.0, "100 %", "#E23B3B")],
                pills=[("😎", "Selbstbild: Sigma", "#2B2F3A"), ("🤡", "Realität: Kek", "#E07A2E")])),
    dict(id="handshake", bg="#E07A2E", clock="07:45", title="DER HANDSHAKE", dark=True, lines=[
        ("Morgens will er mit Tom den coolen Bro-Handshake machen.", None),
        ("Tom geht vorbei. Alex klatscht der Lehrerin ab.", None),
    ], viz=dict(kind="stage", **_BIG, enter="slide_l", particles=["😬", "💀"], box="#FFF0E6", head="🏫 SCHULHOF", head_col="#A8642E",
                people=[(TOM, 820, "Tom", "neutral", None)],
                items=[("🤝", 270, 620, 110, 0, "shake"), ("✋", 430, 620, 100, 1, "pulse"), ("👩‍🏫", 600, 640, 110, 1, "bob")],
                tags=[("BRO-HANDSHAKE? 🤝", "#A8642E", 360, 800), ("HIGH FIVE MIT DER LEHRERIN 💀", "#E23B3B", 470, 990)],
                fx="shock", move="rumble", alex=("happy", "idle", None))),
    dict(id="story", bg="#2B2F4A", clock="10:00", title="DIE STORY", dark=True, lines=[
        ("In der Pause postet er eine Story: Neuer Wagen.", None),
        ("Im Hintergrund sieht man das Autohaus. Und den Verkäufer, der ihn rauswirft.", None),
    ], viz=dict(kind="stage", **_BIG, enter="drop", particles=["✨", "💸"], box="#EEF0FF", head="📸 STORY: „NEUER WAGEN 😎“", head_col="#3E4A9C",
                items=[("🏎️", 330, 650, 160, 0, "bob"), ("🏢", 640, 620, 100, 1, "bob"), ("🧑‍💼", 790, 640, 100, 1, "shake")],
                tags=[("„MEIN NEUER LAMBO“ 🏎️", "#3E4A9C", 360, 830), ("VERKÄUFER: „RAUS!“ 🚪", "#E23B3B", 470, 990)],
                fx="shock", move="bounce", alex=("smug", "idle", "📱"))),
    dict(id="witz", bg="#5B6BC9", clock="11:30", title="DER WITZ", dark=True, lines=[
        ("Tom erzählt einen Witz. Alex lacht am lautesten.", None),
        ("Dann fragt er: Und was war jetzt der Witz?", None),
    ], viz=dict(kind="stage", **_BIG, enter="flip", particles=["😂", "❓"], box="#EEF0FF", head="😂 DER WITZ", head_col="#3E4A9C",
                people=[(TOM, 820, "Tom", "happy", 1)],
                items=[("😂", 260, 620, 110, 0, "pulse"), ("🔊", 420, 620, 90, 0, "shake"), ("❓", 600, 620, 90, 1, "bob")],
                tags=[("LACHT AM LAUTESTEN 😂", "#3E4A9C", 380, 800), ("„WAS WAR DER WITZ?“ 🤨", "#E23B3B", 420, 990)],
                move="wobble", alex=("happy", "idle", None))),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Ich bin nicht peinlich. Die anderen verstehen mich nur nicht.", None),
    ], viz=dict(kind="stage", **_BIG, enter="spin", particles=["🤡"], box="#F2FFF6", head="😎 SELBSTBILD", head_col="#1F5A28",
                items=[("😎", 300, 680, 150, 0, "pulse"), ("➡️", 540, 680, 90, 0, "bob"), ("🤡", 780, 680, 150, 0, "shake")],
                tags=[("„DIE VERSTEHEN MICH NUR NICHT“", "#1F5A28", 540, 960)], move="chomp", alex=("smug", "hips", None))),
    dict(id="rizz", bg="#E0457B", clock="15:00", title="DER RIZZ", dark=True, lines=[
        ("Nachmittags will er Lena mit seinem Rizz beeindrucken.", None),
        ("Er lehnt sich cool an die Wand. Die Wand ist eine Tür.", None),
    ], viz=dict(kind="stage", **_BIG, enter="slide_r", particles=["💘", "💥"], box="#FFF0F6", head="😏 RIZZ-VERSUCH", head_col="#C2185B",
                people=[(LENA, 820, "Lena", "shock", 1)],
                items=[("😏", 270, 620, 110, 0, "pulse"), ("🚪", 440, 630, 110, 1, "shake"), ("💥", 600, 640, 90, 1, "pulse")],
                tags=[("COOL ANLEHNEN 😎", "#C2185B", 380, 790), ("DIE WAND WAR 'NE TÜR 💥", "#2B2F3A", 420, 990)],
                fx="shock", move="rumble", alex=("shock", "idle", None))),
    dict(id="sport", bg="#8E5BE0", clock="18:00", title="FUSSBALL", dark=True, lines=[
        ("Abends Fußball mit den Bros. Er kündigt seinen Fallrückzieher an.", None),
        ("Er trifft den Ball nicht. Aber Toms Kopf.", None),
    ], viz=dict(kind="stage", **_BIG, enter="rise", particles=["⚽", "⭐"], box="#F3EAFE", floor="#5DAA5E", head="⚽ BOLZPLATZ", head_col="#7A3FA8",
                people=[(TOM, 820, "Tom", "angry", 1)],
                items=[("⚽", 300, 620, 100, 0, "spin"), ("🦵", 450, 640, 100, 0, "shake"), ("💫", 700, 560, 90, 1, "spin")],
                tags=[("„FALLRÜCKZIEHER!“ 🦵", "#7A3FA8", 380, 790), ("TREFFER: TOMS KOPF 💫", "#E23B3B", 420, 990)],
                fx="shock", move="bounce", alex=("shock", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Kek erkennst:", "Woran du einen Keck erkennst:"),
        ("Sein Handshake endet bei der Lehrerin.", None),
        ("Er posert mit Autos, die ihm nicht gehören.", None),
        ("Er lacht über Witze, die er nicht versteht.", None),
        ("Und sein Rizz endet an einer Tür.", None),
    ], viz=dict(kind="signs", slide=True, items=[("Handshake mit der Lehrerin", "🤝"), ("Posert mit fremden Autos", "🏎️"),
                                                 ("Lacht, versteht's aber nicht", "😂"), ("Rizz endet an der Tür", "🚪")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Kek? Markier sie oder ihn!", "Kennst du auch einen Keck? Markier sie oder ihn!"),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Kek?", handle="@kek_alex", icon="🍪", col="#2FA36B")),
]

_ALEX = "; den Namen deutsch aussprechen: A-leks mit offenem A wie in 'Alexander', niemals englisch 'Äläx'"
GEMINI_LINE_TEXT = {"handshake_1": "Tom geht vorbei. Aleks klatscht der Lehrerin ab.",
                    "witz_0": "Tom erzählt einen Witz. Aleks lacht am lautesten."}
GEMINI_LINE_MOOD = {k: MOODS[k.split("_")[0]] + _ALEX for k in GEMINI_LINE_TEXT}
GEMINI_LINE_MOOD["signs_0"] = MOODS["signs"] + "; das letzte Wort heißt 'Keck' (wie das Adjektiv keck), niemals 'Keks', 'Geek' oder 'Kick'"
GEMINI_LINE_MOOD["intro_role"] = "völlig überrascht und amüsiert, flüssig und kurz ausgerufen: 'ein Keck!' (wie 'keck', ohne s, niemals 'Keks') – das Wort 'ein' unbedingt mitsprechen"
