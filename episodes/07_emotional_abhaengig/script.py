"""TikTok Folge 4: Heute ist Alex ... emotional abhängig.  (Aufbau wie Pick-me-Boy)
Stimme exakt wie Pick-me-Boy: gemini-3.8-flash-tts, Puck, tighten 1.08.
Ton: nachvollziehbar-lustig, nicht herablassend; kurzer ernster Satz am Ende.
"""

ROLE = "EMOTIONAL ABHÄNGIG."
ROLE_TTS = "emotional abhängig."
ROLE_SAY = "emotional abhängig!"

MOODS = {
    "intro_pre": "spannend, aber zügig und kurz gesprochen, ohne lange Pause",
    "intro_role": "dramatische Enthüllung, halb mitfühlend, halb amüsiert",
    "what": "erklärend und mitfühlend-amüsiert, das Zitat von Alex klammernd und weinerlich",
    "morning": "amüsiert, die Analyse übertrieben dramatisch wie ein Detektiv",
    "online": "zunehmend nervös und hektisch, die Pointe trocken",
    "friends": "trocken und leicht mitleidig",
    "party": "immer hektischer, die Nachrichten klammernd, die Pointe trocken",
    "google": "verzweifelt-dramatisch, dann trocken",
    "signs": "energisch wie ein Countdown, jedes Anzeichen mit Nachdruck",
    "real": "ruhig, warm und ehrlich, ohne Ironie",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("EIN F-BOY.", "😏", "#1C1C22", "#2B2D5E"),
    ("EIN KOCH.", "🍳", "#F4F4F4", "#E3A23B"),
    ("EIN OF-MODEL.", "📸", "#E8457A", "#B0307A"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

# Cover: Anordnung wie Pick-me-Boy, Farben zum Thema (melancholisches Blau, warmes Rosa)
THUMB = dict(head="HEUTE IST ALEX…", l1="EMOTIONAL", l2="ABHÄNGIG", bg="#3E5C9A", color1="#FFFFFF",
             accent="#FF9EC4", pill="#1E2A4A", pill_text="#FFFFFF", expr="puppy", pose="phone", prop="📱",
             emojis=("🥺", "💬", "⏳", "💔"))

SCENES = [
    dict(id="what", bg="#3E5C9A", clock=None, title="WAS HEISST EMOTIONAL ABHÄNGIG?", dark=True, lines=[
        ("Emotional abhängig heißt: Deine Laune hängt komplett an einer anderen Person.", None),
        ("Alex' Lieblingssatz: Ohne dich bin ich nichts.", None),
    ]),
    dict(id="morning", bg="#F2A65A", clock="07:00", title="GUTEN MORGEN", lines=[
        ("Sieben Uhr. Sophie schreibt: ok. Nicht okay. Nur ok.", None),
        ("Alex analysiert eine Stunde lang: Ist sie sauer? Hab ich was falsch gemacht?", None),
    ]),
    dict(id="online", bg="#6C8CE0", clock="12:00", title="ZULETZT ONLINE", lines=[
        ("Mittags: Sophie war vor zwei Minuten online. Aber sie hat nicht geantwortet.", None),
        ("Alex schickt: Fragezeichen. Dann noch eins. Dann: Alles gut?", None),
    ]),
    dict(id="friends", bg="#6CC08B", clock="16:00", title="FREUNDE", lines=[
        ("Seine Kumpels fragen: Kommst du mit zum Fußball?", None),
        ("Alex sagt ab. Vielleicht meldet sie sich ja.", None),
    ]),
    dict(id="party", bg="#E06A6A", clock="20:00", title="SIE IST UNTERWEGS", lines=[
        ("Abends ist Sophie mit ihren Freundinnen unterwegs.", None),
        ("Alex schreibt zwanzig Nachrichten. Hast du Spaß? Ohne mich? Denkst du an mich?", None),
    ]),
    dict(id="google", bg="#26345E", clock="23:00", title="NACHTS", dark=True, lines=[
        ("Elf Uhr nachts googelt Alex: Wie lange darf eine Antwort dauern?", None),
        ("Dann starrt er auf den Chat. Bis da endlich steht: schreibt.", None),
    ]),
    dict(id="signs", bg="#8E5BE0", clock=None, title="DIE 4 ANZEICHEN", dark=True, lines=[
        ("Woran du emotionale Abhängigkeit erkennst:", None),
        ("Dein Tag hängt an einer Antwort.", None),
        ("Du sagst Freunde und Hobbys ab.", None),
        ("Ohne Bestätigung geht gar nichts.", None),
        ("Und Alleinsein fühlt sich an wie Panik.", None),
    ]),
    dict(id="real", bg="#F7B2C9", clock=None, title="MAL ERNST", lines=[
        ("Und mal ernst: Rede mit deinen Freunden. Du bist auch allein wertvoll.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du jemanden, der gerade emotional abhängig ist, aber auch alleine wertvoll ist? Markier ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
