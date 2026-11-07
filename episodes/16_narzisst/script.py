"""TikTok-Folge: Heute ist Alex ... ein Narzisst. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#E5A50A", top_style="tee", pants="#2F3B52", shoes="#FFFFFF")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
MIA = person_spec(14, girl=True, top="#F07FB0", hair="#5A3A22", skin="#F1C9A8")
ROLE, ROLE_TTS, ROLE_SAY = "EIN NARZISST.", "ein Narzisst.", "ein Narzisst!"
MOODS = dict(MOODS_BASE, bad="selbstverliebt, dann trocken", mittag="erst ernst, dann trocken und unglaublich",
             post="stolz, dann trocken", date="genervt amüsiert, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"bad": ["🪞", "📸", "🚩"], "mittag": ["🏥", "🤧", "🚩"], "post": ["💬", "💀", "🚩"], "date": ["🍷", "🙄", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="NARZISST", bg="#B8860B", color1="#FFFFFF", accent="#FFE14D",
             pill="#5A3E06", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🪞", "👑", "✨", "🚩"))
INTRO_CFG = dict(icon="🪞", bg="#B8860B", title_lines=["NARZISST."],
                 house=dict(sky=("#F2C84B", "#FFF6D6"), walls="#FFF8E6", roof="#8A6206", door="#5A3E06", lawn="#5DAA5E",
                            accent=("#E5A50A", "#E0457B"), sun=True),
                 left=("🪞", "SPIEGEL"), right=("🖼️", "ICH"), door=("ICH. ICH.", "UND ICH."),
                 neon=("KING", "👑 = ICH", "#FFD24A"), signs=("Genug von mir … 🙄", "Was hältst DU von mir? 👑"),
                 fly=["✨", "👑", "🪞"], burst=["🪞", "👑", "✨", "📸", "💅", "🏆", "😎", "💎"],
                 extras=[("👑", 0, 112, 14), ("🪞", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#B8860B", clock=None, title="WAS IST EIN NARZISST?", dark=True, lines=[
        ("Ein Narzisst liebt nur eine einzige Person. Sich selbst.", None),
        ("Und jedes Gespräch mit ihm dreht sich nur um ihn.", None),
    ], viz=dict(kind="bars", head="WORUM GEHT'S IM GESPRÄCH?", rows=[("ER", 1.0, "100 %", "#E5A50A"), ("DU", 0.03, "0 %", "#555A66")],
                pills=[("🎤", "Lieblingsthema: Ich", "#E5A50A"), ("🙉", "Zuhören: ausgeschaltet", "#E23B3B")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Ich bin nicht arrogant. Ich bin einfach besser.", None),
    ], viz=dict(kind="stage", box="#FFF8E6", head="👑 EINFACH BESSER", head_col="#B8860B",
                items=[("👑", 540, 640, 200, 0, "pulse"), ("🏆", 280, 700, 120, 0, "bob"), ("✨", 800, 640, 110, 0, "spin"),
                       ("💎", 760, 840, 90, 0, "bob")],
                tags=[("PLATZ 1: ICH 🥇", "#B8860B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="bad", bg="#36B5C2", clock="07:00", title="IM BAD", lines=[
        ("Sieben Uhr. Eine Stunde vor dem Spiegel.", None),
        ("Er macht zweihundert Selfies. Und findet jedes einzelne perfekt.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="🪞 SPIEGEL-ZEIT", head_col="#2B5C66",
                items=[("🪞", 540, 680, 230, 0, "pulse"), ("⏰", 260, 600, 90, 0, "shake"), ("📸", 300, 860, 90, 1, "shake"),
                       ("📸", 800, 860, 90, 1, "shake"), ("✨", 820, 600, 90, 1, "spin")],
                tags=[("60 MIN ⏰", "#3E7BDA", 260, 720), ("200 SELFIES · ALLE 10/10 ✨", "#E0457B", 540, 980)],
                fx="love", move="wobble", flash="#FFFFFF", alex=("happy", "idle", "📱"))),
    dict(id="mittag", bg="#C0392B", clock="12:00", title="MITTAGESSEN", dark=True, lines=[
        ("Mittags mit Lena. Sie erzählt, dass ihr Opa im Krankenhaus liegt.", None),
        ("Er sagt: Krass. Ich hatte letzte Woche Schnupfen.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="🍝 MITTAGESSEN", head_col="#C0392B",
                people=[(LENA, 760, "Lena", "sad", 1)],
                items=[("🏥", 760, 580, 90, 0, "bob"), ("🍝", 420, 880, 90, 0, "bob"), ("🤧", 320, 640, 120, 1, "shake")],
                tags=[None, ("THEMA GEKLAUT 🎤", "#E23B3B", 400, 800)], fx="anger", move="wobble", flash="#FF3B3B",
                alex=("smug", "idle", None))),
    dict(id="post", bg="#5B6BC9", clock="17:00", title="SELFIE-POST", dark=True, lines=[
        ("Siebzehn Uhr. Er postet ein Selfie.", None),
        ("Und schreibt den ersten Kommentar selbst: Wow, wer ist dieser Mann?", None),
    ], viz=dict(kind="chat", chat="📸 alex.official", bar="#E0457B",
                msgs=[(0, "alex.official", "📸 *neues Selfie* #king #perfekt", "#E5A50A"),
                      (1, "alex.official", "Wow, wer ist dieser Mann?? 😍🔥", "#E5A50A"),
                      (1, "Lena", "Du hast das grad selbst kommentiert 💀", "#3E7BDA")],
                fx="shock", alex=("smug", "idle", "📱"))),
    dict(id="date", bg="#8E5BE0", clock="20:00", title="DAS DATE", dark=True, lines=[
        ("Abends ein Date. Er redet zwei Stunden nur über sich.", None),
        ("Dann sagt er: Genug von mir. Was hältst du von mir?", None),
    ], viz=dict(kind="stage", box="#F3EAFE", head="🕯️ DATE-NIGHT", head_col="#7A3FA8",
                people=[(MIA, 770, "Mia", "neutral", 1)],
                items=[("🍷", 540, 860, 90, 0, "bob"), ("🕯️", 420, 860, 70, 0, "pulse"), ("🗣️", 300, 640, 120, 0, "shake"),
                       ("😴", 770, 560, 70, 0, "fly")],
                tags=[("2 STUNDEN ÜBER SICH 🗣️", "#7A3FA8", 400, 980)], fx="anger", move="wobble",
                bubbles=[None, "Was hältst du von mir? 😏"], alex=("smug", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Narzissten erkennst:", None),
        ("Jedes Gespräch dreht sich um ihn.", None),
        ("Sein bester Freund ist der Spiegel.", None),
        ("Er kommentiert seine eigenen Posts.", None),
        ("Und er kann einfach nicht zuhören.", None),
    ], viz=dict(kind="signs", items=[("Jedes Gespräch über ihn", "🎤"), ("Bester Freund: Spiegel", "🪞"),
                                     ("Kommentiert sich selbst", "💬"), ("Kann nicht zuhören", "🙉")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Narzissten? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Narzissten?", handle="@king_alex", icon="🪞", col="#B8860B")),
]
