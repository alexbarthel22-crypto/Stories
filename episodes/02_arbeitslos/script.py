"""Folge 2: Heute ist Alex ... arbeitslos.

Jede Zeile: (Untertitel-Text, TTS-Text oder None).
"""

ROLE = "ARBEITSLOS."
ROLE_TTS = "arbeitslos."
ROLE_SAY = "arbeitslos!"

MOODS = {
    "intro_pre": "geheimnisvoll und spannend, wie vor einer großen Enthüllung, langgezogen",
    "intro_role": "dramatische Enthüllung, halb mitleidig, halb lachend",
    "plan": "motiviert und optimistisch, als würde gleich alles klappen",
    "alarm": "verschlafen und gemütlich, dann immer genervter beim Snooze",
    "breakfast": "verwirrt-philosophisch, trocken",
    "jobcenter": "ungläubig und genervt, die Beamtenstimme monoton und bürokratisch",
    "apply": "sarkastisch über absurde Stellenanzeigen, die Absage übertrieben höflich-kühl vorlesen",
    "family": "peinlich berührt; Oma neugierig und lieb, Alex nervös stotternd",
    "linkedin": "übertrieben businessmäßig motiviert, dann trocken die Übersetzung",
    "night": "flüsternd, dann plötzlich übermotiviert und euphorisch",
    "phases": "energisch wie ein Countdown, jede Phase mit Nachdruck, die letzte lachend",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

# Rollen, die im Intro durchgeschaltet werden (Text, Emoji, Oberteil, Hintergrund)
SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("EIN KOCH.", "🍳", "#F4F4F4", "#E3A23B"),
    ("EIN RENTNER.", "👓", "#8C6B4F", "#7C8A96"),
    ("EIN INFLUENCER.", "🤳", "#F07FB0", "#E26AA0"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

# Cover/Thumbnail
THUMB = dict(l1="ARBEITS", l2="LOS", bg="#5FA9B8", expr="sad", pose="shrug", prop=None,
             emojis=("📄", "☕", "💤", "📉"))

SCENES = [
    dict(id="plan", bg="#5FA9B8", clock=None, title="DER PLAN", lines=[
        ("Alex hat seinen Job verloren. Firma pleite.", None),
        ("Aber er hat einen Plan: früh aufstehen, Bewerbungen schreiben, Sport machen.", None),
    ]),
    dict(id="alarm", bg="#F2A65A", clock="07:00", title="DER WECKER", lines=[
        ("Sieben Uhr. Der Wecker klingelt. Alex denkt: Ich hab ja eh Zeit.", None),
        ("Snooze. Snooze. Snooze.", None),
    ]),
    dict(id="breakfast", bg="#F2C14E", clock="11:30", title="FRÜHSTÜCK?", lines=[
        ("Halb zwölf. Frühstück oder Mittagessen? Wer weiß das schon.", None),
    ]),
    dict(id="jobcenter", bg="#8FA3B8", clock="12:30", title="JOBCENTER", lines=[
        ("Dann sein Termin im Jobcenter. Seine Nummer: 247. Aufgerufen wird gerade: 12.",
         "Dann sein Termin im Jobcenter. Seine Nummer: zweihundertsiebenundvierzig. Aufgerufen wird gerade: zwölf."),
        ("Nach drei Stunden: Bitte bringen Sie nächstes Mal alle Unterlagen mit.", None),
    ]),
    dict(id="apply", bg="#6C8CE0", clock="15:00", title="BEWERBUNGEN", lines=[
        ("Nachmittags Bewerbungen. Gesucht: Junior mit zehn Jahren Berufserfahrung.", None),
        ("Die Antworten: Leider haben wir uns für einen anderen Kandidaten entschieden.", None),
    ]),
    dict(id="family", bg="#E07A5F", clock="18:30", title="FAMILIENESSEN", lines=[
        ("Beim Familienessen fragt Oma: Und, was machst du gerade beruflich?", None),
        ("Alex stottert: Ich bin gerade so in einer Findungsphase.", None),
    ]),
    dict(id="linkedin", bg="#3E7BDA", clock="20:00", title="LINKEDIN", dark=True, lines=[
        ("Auf LinkedIn postet er: Ich freue mich auf neue Herausforderungen!", None),
        ("Übersetzt: Bitte stellt mich ein.", None),
    ]),
    dict(id="night", bg="#26345E", clock="23:00", title="MITTERNACHTS-MOTIVATION", dark=True, lines=[
        ("Und um elf Uhr nachts plötzlich: Ab morgen ändere ich alles!", None),
    ]),
    dict(id="phases", bg="#D9534F", clock=None, title="DIE 4 PHASEN", lines=[
        ("Die vier Phasen der Arbeitslosigkeit:", None),
        ("Urlaubsgefühl.", None),
        ("Langeweile.", None),
        ("Panik.", None),
        ("Und plötzlich backst du Sauerteigbrot.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du noch jemanden, der gerade arbeitslos ist? Markier ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
