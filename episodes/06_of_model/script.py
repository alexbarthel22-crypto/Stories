"""Folge (TikTok Folge 3): Heute ist Alex ... ein OF-Model – als Alexia.
Gesprochen/geschrieben wird nur "OF". Komplett jugendfrei: Humor über Business-Klischees.
Keine Zahlen/Gebühren – nur Klischees.
Stimme wie Pick-me-Boy: gemini-3.8-flash-tts, Puck. Fans: eigene männliche Gemini-Stimmen.
"""

from ep_base import (TTS_PROFILE, SAFE_MODE, SAFE_TOP, SAFE_LEFT, EXTRAS, CAPTION_SIZE, NAME_SCALE, TITLE_SIZE,
                     BUBBLE_SCALE, INTRO_SFX_GAIN, REVEAL_TAIL, INTRO_TICK_GAIN, SHUFFLE_BASE)
# Aufbau wie die neuen Folgen: kurze Pause nach der Verkündung, Untertitel + Tagesleiste tiefer, schneller gesprochen
INTRO_LEN = 3.3
CAPTION_Y = 1650
DAYBAR_Y = 1755
LINE_TEMPO = {k: 1.25 for k in ("signs_0", "signs_1", "signs_2", "signs_3", "signs_4", "outro_0", "outro_1")}
REACTIONS = {"morning": ["💄", "📸", "🚩"], "promo": ["🔗", "💸", "🚩"], "dms": ["💌", "🙄", "🚩"],
             "family": ["👵", "😅", "🚩"], "boss": ["💼", "🛏️", "🚩"]}

ROLE = "EIN OF-MODEL."
ROLE_TTS = "ein Oh-Eff-Model."
ROLE_SAY = "ein Oh-Eff-Model!"

# Aussprache für Gemini: OF (OnlyFans) = „Oh Eff“
GEMINI_REPLACE = {"OF-Model": "Oh-Eff-Model", "OF ": "Oh-Eff "}

MOODS = {
    "intro_pre": "spannend, aber zügig und kurz gesprochen, ohne lange Pause",
    "intro_role": "völlig überrascht und amüsiert, wie ungläubig ausgerufen, zügig gesprochen; OF wird 'Oh Eff' ausgesprochen",
    "what": "erklärend und amüsiert, die Verwandlung wie eine Vorher-nachher-Show",
    "morning": "ironisch wie ein Beauty-Tutorial, die Pointe trocken",
    "promo": "übertrieben werblich wie ein Influencer, dann trocken",
    "dms": "amüsiert, der Fan-Satz übertrieben schmalzig, die Pointe trocken",
    "family": "lieb und neugierig, dann peinlich ausweichend",
    "boss": "übertrieben businessmäßig motiviert, dann trocken entlarvend",
    "signs": "energisch wie ein Countdown, jedes Anzeichen mit Nachdruck",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = SHUFFLE_BASE

# Cover: Anordnung wie Pick-me-Boy, Farben zum Thema (Ringlicht-Pink/Lila, Gold)
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="OF-MODEL", bg="#B0307A", accent="#FFD84D",
             pill="#2B1030", pill_text="#FFFFFF", expr="smug", pose="phone", prop="📱",
             emojis=("💸", "💄", "📸", "💅"))

# Männliche Fan-Stimmen (nicht der Erzähler)
VOICE_OVERRIDE = {
    ("dms", 2): dict(voice="Charon", text="Ich hab dir Trinkgeld geschickt. Heiratest du mich?",
                     profile="Ein männlicher Fan, Mitte vierzig, tiefe Männerstimme, aufgeregt und hoffnungsvoll.",
                     mood="aufgeregt, naiv, voller Hoffnung"),
}

SCENES = [
    dict(id="what", bg="#B0307A", clock=None, title="WAS IST EIN OF-MODEL?", dark=True, lines=[
        ("Ein OF-Model verkauft exklusive Inhalte an zahlende Fans. Im Abo.",
         "Ein Oh-Eff-Model verkauft exklusive Inhalte an zahlende Fans. Im Abo."),
        ("Und dafür wird Alex heute zu Alexia: Perücke, Make-up, Minirock.", None),
    ]),
    dict(id="morning", bg="#F2A65A", clock="09:00", title="NATURAL LOOK", lines=[
        ("Neun Uhr. Der natürliche Look. Dauert nur zwei Stunden.", None),
        ("Ringlicht an. Ausschnitt richten. Dreihundert Fotos. Eins wird gepostet.", None),
    ]),
    dict(id="promo", bg="#8E5BE0", clock="13:00", title="LINK IN BIO", dark=True, lines=[
        ("Mittags Werbung auf allen Kanälen. Unter jedem Video: Link in Bio.", None),
    ]),
    dict(id="dms", bg="#36B5C2", clock="17:00", title="DIE NACHRICHTEN", lines=[
        ("Nachmittags: Hunderte Nachrichten von Fans.", None),
        ("Fan 1: Du bist die Einzige, die mich versteht.", None),
        ("Fan 2: Ich hab dir Trinkgeld geschickt. Heiratest du mich?", None),
        ("Alexia antwortet: Du auch, Babe. In Wahrheit hat Kevin geantwortet. Der bezahlte Chatter.", None),
    ]),
    dict(id="family", bg="#E9A23B", clock="19:00", title="FAMILIENESSEN", lines=[
        ("Oma fragt: Und, was machst du so beruflich?", None),
        ("Alexia: Ich bin Content Creatorin. Im Bereich Fitness.", None),
    ]),
    dict(id="boss", bg="#2B1030", clock="21:00", title="BOSS BABE", dark=True, lines=[
        ("Abends postet sie: Ich bin keine Influencerin. Ich bin Unternehmerin.", None),
        ("Ihr Büro: das Bett. Ihr ganzes Team: ein Ringlicht.", None),
    ]),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du ein OF-Model erkennst:", "Woran du ein Oh-Eff-Model erkennst:"),
        ("Link in Bio.", None),
        ("Nennt sich CEO.", None),
        ("Das Ringlicht ist immer dabei.", None),
        ("Und jeder Fan heißt Babe.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch jemanden, der damit starten sollte? Markier ihn oder sie!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
