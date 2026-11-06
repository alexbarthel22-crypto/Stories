"""TikTok Folge 6: Heute ist Alex ... ein Schmarotzer. Alltags-Comedy, keine echten Personen.
Stimme exakt wie Pick-me-Boy: gemini-3.8-flash-tts, Puck, TTS_PROFILE="pickme", tighten 1.08 0.22 (Tempo + Lautstärke exakt wie Folge 1 Pick-me-Boy, keine LINE_TEMPO-Sonderwerte).
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
REACTIONS = {"hotspot": ["📶", "😤", "🚩"], "stream": ["📺", "🔑", "🚩"], "food": ["🥩", "💸", "🚩"],
             "party": ["🎂", "🥡", "🚩"]}

ROLE = "EIN SCHMAROTZER."
ROLE_TTS = "ein Schmarotzer."
ROLE_SAY = "ein Schmarotzer!"

MOODS = {
    "intro_pre": "geheimnisvoll und spannend, ruhig und flüssig, ohne Stocken; den Namen Alex deutsch aussprechen (kurzes A wie in Alexander)",
    "intro_role": "völlig überrascht und amüsiert, wie ungläubig ausgerufen, zügig gesprochen",
    "what": "erklärend und amüsiert, die Pointe trocken",
    "motto": "verschmitzt und stolz, wie eine Lebensweisheit, die Pointe trocken",
    "hotspot": "beiläufig, dann trocken und amüsiert, die Pointe mit Jana trocken",
    "stream": "ungläubig amüsiert, die Pointe trocken",
    "food": "erst genießerisch, dann trocken, am Ende frech",
    "party": "fröhlich, dann trocken, am Ende verschwörerisch leise und frech",
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
    ("EIN ARBEITSZEIT-BETRÜGER.", "⏰", "#2F6FA8", "#3E7BDA"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="SCHMAROTZER", bg="#D9762B", color1="#FFFFFF",
             accent="#FFE14D", pill="#5A2E0E", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True,
             emojis=("💸", "🍕", "🥡", "🚩"))

SCENES = [
    dict(id="what", bg="#D9762B", clock=None, title="WAS IST EIN SCHMAROTZER?", dark=True, lines=[
        ("Ein Schmarotzer lebt richtig gut. Bezahlen tun nur immer die anderen.", None),
        ("Seine Karte hat er leider immer vergessen. Und mit dem Handy bezahlen geht bei ihm komischerweise nie.", None),
    ]),
    dict(id="motto", bg="#2FA36B", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Teilen ist wichtig. Vor allem, wenn die anderen bezahlen.", None),
    ]),
    dict(id="hotspot", bg="#36B5C2", clock="08:00", title="DER HOTSPOT", lines=[
        ("Acht Uhr, in der Bahn. Sein Datenvolumen ist leer. Wie immer.", None),
        ("Also hängt er in Janas Hotspot und schaut Brainrot-Videos auf TikTok. Jana hat jetzt kein Datenvolumen mehr.", None),
    ]),
    dict(id="stream", bg="#5B6BC9", clock="11:00", title="SERIEN-MARATHON", dark=True, lines=[
        ("Elf Uhr. Serien gucken. Mit dem Account seiner Ex. Seit drei Jahren.", None),
        ("Sie hat das Passwort fünfmal geändert. Er hat es fünfmal erraten.", None),
    ]),
    dict(id="food", bg="#C0392B", clock="13:00", title="BEIM ESSEN", lines=[
        ("Mittags essen mit Freunden. Alex bestellt Steak, Vorspeise und drei Cocktails.", None),
        ("Die anderen nehmen Salat und Leitungswasser.", None),
        ("Und bei der Rechnung sagt er: Wir teilen einfach durch alle.", None),
    ]),
    dict(id="party", bg="#8E5BE0", clock="19:00", title="GEBURTSTAG", dark=True, lines=[
        ("Abends Geburtstag. Er kennt das Geburtstagskind nicht mal.", None),
        ("Aber nach Hause geht er mit drei vollen Tupperdosen.", None),
        ("Und heimlich nimmt er noch Svens Pflanze, das Bild und die Discokugel mit.", None),
    ]),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Schmarotzer erkennst:", None),
        ("Er hat nie seine Karte dabei. Und Handy-Bezahlen geht auch nie.", None),
        ("Er sagt immer: Ich geb's dir morgen wieder.", None),
        ("Er taucht immer pünktlich zum Essen auf. Und isst den anderen alles weg.", None),
        ("Und er hat immer Tupperdosen im Rucksack.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Schmarotzer? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]

# Nur für die Stimme: "Aleks" geschrieben -> deutsches A statt englischem "Äläx"
_ALEX = "; den Namen deutsch aussprechen: A-leks mit offenem A wie in 'Alexander', niemals englisch 'Äläx'; kein Lachen"
GEMINI_LINE_TEXT = {
    "food_0": "Mittags essen mit Freunden. Aleks bestellt Steak, Vorspeise und drei Cocktails.",
}
GEMINI_LINE_MOOD = {"food_0": "genießerisch" + _ALEX}

LINE_TEMPO = {}   # wie Pick-me-Boy: alle Zeilen 1.08
