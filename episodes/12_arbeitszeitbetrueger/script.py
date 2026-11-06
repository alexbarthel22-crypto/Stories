"""TikTok Folge 5: Heute ist Alex ... ein Arbeitszeit-Betrüger. Büro-/Homeoffice-Comedy, keine echten Firmen.
Stimme exakt wie Pick-me-Boy: gemini-3.8-flash-tts, Puck, TTS_PROFILE="pickme", tighten 1.08.
"""
TTS_PROFILE = "pickme"
SAFE_MODE = "strict"
SAFE_TOP = 240
SAFE_LEFT = 100
EXTRAS = True
CAPTION_SIZE = 62
NAME_SCALE = 1.6
TITLE_SIZE = 92
BUBBLE_SCALE = 1.2
INTRO_SFX_GAIN = 3.4   # Reveal-Effekt
REVEAL_TAIL = (0.28, 0.0)   # Hintergrundstimme im Original-Reveal entfernt, Knall bleibt
INTRO_TICK_GAIN = 6.0  # Auswahl-Klicks extra laut
REACTIONS = {"stamp": ["⏰", "😴", "🚩"], "meeting": ["📵", "😴", "🚩"], "toilet": ["🚽", "📱", "🚩"],
             "mouse": ["🖱️", "💇", "🚩"], "mail": ["📧", "🌙", "🚩"]}

ROLE = "EIN ARBEITSZEIT-BETRÜGER."
ROLE_TTS = "ein Arbeitszeitbetrüger."
ROLE_SAY = "ein Arbeitszeitbetrüger!"

MOODS = {
    "intro_pre": "geheimnisvoll und spannend, ruhig und flüssig, ohne Stocken; den Namen Alex deutsch aussprechen (kurzes A wie in Alexander)",
    "intro_role": "völlig überrascht und amüsiert, wie ungläubig ausgerufen, zügig gesprochen",
    "what": "erklärend und amüsiert, die Pointe trocken",
    "motto": "verschmitzt und stolz, wie ein Lebensmotto",
    "stamp": "gut gelaunt, dann trocken",
    "meeting": "erst sachlich, dann flüsternd verschwörerisch, am Ende gespielt unschuldig",
    "toilet": "trocken und ungläubig amüsiert",
    "mouse": "spannend-geheimnisvoll, dann trocken",
    "mail": "beiläufig, dann frech stolz, 'Überstunden sammeln' verschmitzt",
    "signs": "energisch und zügig wie ein Countdown, jedes Anzeichen mit Nachdruck",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("EMOTIONAL ABHÄNGIG.", "🥺", "#7FA3D6", "#3E5C9A"),
    ("EIN GASLIGHTER.", "🌀", "#3F5A4A", "#4A2E6B"),
    ("EINE DORFMATRATZE.", "🏘️", "#5E8C3A", "#3F9A4A"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

THUMB = dict(head="HEUTE IST ALEX EIN…", l1="ARBEITSZEIT-", l2="BETRÜGER", bg="#2F6FA8", color1="#FFFFFF",
             accent="#FFD34D", pill="#173A5C", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True,
             emojis=("⏰", "🖱️", "😴", "🚩"))

SCENES = [
    dict(id="what", bg="#2F6FA8", clock=None, title="WAS IST EIN ARBEITSZEIT-BETRÜGER?", dark=True, lines=[
        ("Ein Arbeitszeitbetrüger ist acht Stunden bei der Arbeit.", None),
        ("Gearbeitet hat er davon ungefähr vierzig Minuten.", None),
    ]),
    dict(id="motto", bg="#2FA36B", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Hauptsache, der Status ist grün.", None),
    ]),
    dict(id="stamp", bg="#E9A23B", clock="06:00", title="EINSTEMPELN", lines=[
        ("Sechs Uhr. Alex stempelt pünktlich ein.", None),
        ("Und dann schläft er erst mal zwei Stunden. Status: rot. Beschäftigt.", None),
    ]),
    dict(id="meeting", bg="#5B6BC9", clock="10:00", title="TEAMS-MEETING", lines=[
        ("Zehn Uhr, Meeting. Kamera aus, Mikro aus.", None),
        ("In Wahrheit liegt er noch im Bett.", None),
        ("Der Chef fragt: Alex, was meinst du? Und Alex sagt: Sorry, ich hatte kurz Netzprobleme.", None),
    ]),
    dict(id="toilet", bg="#36B5C2", clock="12:00", title="DIE PAUSE", lines=[
        ("Mittags geht er aufs Klo. Für fünfundvierzig Minuten.", None),
        ("Mit Handy. Candy Crush, Level dreihundert.", None),
    ]),
    dict(id="mouse", bg="#8E5BE0", clock="15:00", title="DIE MAUS", dark=True, lines=[
        ("Nachmittags bewegt sich seine Maus von ganz allein.", None),
        ("Status: grün. Alex: beim Friseur.", None),
    ]),
    dict(id="mail", bg="#26345E", clock="16:00", title="FEIERABEND", dark=True, lines=[
        ("Um vier macht er Feierabend. Ausgestempelt wird aber erst um zehn. Überstunden sammeln.", None),
        ("Seine Mail an den Chef geht trotzdem erst um zehn Uhr abends raus. Zeitgesteuert.", None),
    ]),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Arbeitszeitbetrüger erkennst:", None),
        ("Sein Status ist immer grün.", None),
        ("Er hat ständig Netzprobleme.", None),
        ("Bei allem sagt er: Ich nehm das mal mit.", None),
        ("Und er ist die Hälfte der Arbeitszeit auf dem Klo oder rauchen.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Arbeitszeitbetrüger? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]

# Nur für die Stimme: "Aleks" geschrieben -> deutsches A statt englischem "Äläx"
GEMINI_LINE_TEXT = {"stamp_0": "Sechs Uhr. Aleks stempelt pünktlich ein.",
                    "mouse_1": "Status: grün. Aleks: beim Friseur.",
                    "meeting_2": "Der Chef fragt: Aleks, was meinst du? Und Aleks sagt: Sorry, ich hatte kurz Netzprobleme."}
_ALEX = "; den Namen deutsch aussprechen: A-leks mit offenem A wie in 'Alexander', niemals englisch 'Äläx'; kein Lachen"
GEMINI_LINE_MOOD = {"stamp_0": "gut gelaunt" + _ALEX,
                    "mouse_1": "trocken, kurze Pointe" + _ALEX,
                    "meeting_2": "erst den Chef ernst nachmachen, dann Alex gespielt unschuldig" + _ALEX}

# Verkündung und Aufzählung zügig
LINE_MAXPAUSE = {"what_1": 0.06}   # keine lange Kunstpause vor "40 Minuten"
LINE_TEMPO = {"what_1": 1.2, "intro_role": 1.22, "signs_0": 1.26, "signs_1": 1.28, "signs_2": 1.28, "signs_3": 1.28, "signs_4": 1.24}
