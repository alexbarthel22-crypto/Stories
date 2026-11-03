"""Folge 5: Heute ist Alex ... ein F-Boy.  (Aufbau wie Folge 1 / Pick-me-Boy)
Gesprochen wird nur "F-Boy" (Eff-Boy) – das ausgeschriebene Wort kommt nicht vor.
Stimme: gemini-2.5-pro-preview-tts, Puck, tighten 1.08 (3.8-Modell war am Tageslimit).
"""

ROLE = "EIN F-BOY."
ROLE_TTS = "ein Eff-Boy."
ROLE_SAY = "ein Eff-Boy!"

MOODS = {
    "intro_pre": "spannend, aber zügig und kurz gesprochen, ohne lange Pause",
    "intro_role": "triumphierende, laute Enthüllung mit einem Augenzwinkern",
    "what": "erklärend, amüsiert; das Zitat von Alex lässig und überheblich",
    "seen": "trocken und genervt, die Pointe ironisch",
    "gym": "lässig, amüsiert und deutlich",
    "date": "erst amüsiert, dann entlarvend; das Zitat lässig-ausweichend",
    "chats": "verschwörerisch und amüsiert",
    "snap": "ruhig, amüsiert und deutlich, nicht flüstern",
    "crumbs": "erst überrascht, dann trocken erklärend",
    "flags": "energisch wie ein Countdown, jede Red Flag mit Nachdruck",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("ARBEITSLOS.", "🛋️", "#8A8F99", "#5FA9B8"),
    ("CHOLERIKER.", "😡", "#3C4A63", "#D9534F"),
    ("MILLIARDÄR.", "💰", "#9AA0A8", "#1F6B4A"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

THUMB = dict(l1="F-BOY", l2="ALARM", bg="#2B2D5E", expr="smug", pose="phone", prop="📱",
             emojis=("🚩", "👻", "🌙", "💪"))

SCENES = [
    dict(id="what", bg="#2B2D5E", clock=None, title="WAS IST EIN F-BOY?", dark=True, lines=[
        ("Ein F-Boy will keine Beziehung. Aber trotzdem alles, was dazugehört.",
         "Ein Eff-Boy will keine Beziehung. Aber trotzdem alles, was dazugehört."),
        ("Sein Lieblingssatz: Ich will mich gerade auf nichts festlegen.", None),
    ]),
    dict(id="seen", bg="#F2A65A", clock="10:00", title="GELESEN", lines=[
        ("Zehn Uhr. Deine Nachricht hat er um sieben gelesen.", None),
        ("Antwort? Vielleicht heute Nacht.", None),
    ]),
    dict(id="gym", bg="#4FA3C7", clock="17:00", title="IM GYM", lines=[
        ("Im Gym: Spiegel-Selfie. Muskeln anspannen. Bildunterschrift: Grind never stops.", None),
    ]),
    dict(id="date", bg="#E06A6A", clock="20:00", title="DAS DATE", lines=[
        ("Beim Date redet er nur über sich. Und schaut ständig aufs Handy.", None),
        ("Fragst du, was ihr seid: Lass uns das nicht labeln.", None),
    ]),
    dict(id="chats", bg="#6CC08B", clock="22:00", title="5 CHATS", lines=[
        ("Danach hat er fünf Chats gleichzeitig offen. Jeder beginnt mit: Hey du.", None),
    ]),
    dict(id="snap", bg="#1E1F3A", clock="23:30", title="DER NACHT-SNAP", dark=True, lines=[
        ("Halb zwölf nachts kommt der Snap. Jawline von unten, schlechtes Licht.", None),
        ("Dazu der Text: Bist du wach?", None),
    ]),
    dict(id="crumbs", bg="#8E5BE0", clock=None, title="EINE WOCHE SPÄTER", dark=True, lines=[
        ("Du meldest dich nicht mehr. Sofort schreibt er: Vermiss dich.", None),
        ("Danach wieder Funkstille. Das nennt man Breadcrumbing.", None),
    ]),
    dict(id="flags", bg="#D9534F", clock=None, title="DIE 4 RED FLAGS", lines=[
        ("Die nervigsten Red Flags:", "Die nervigsten Räd Fläggs:"),
        ("Er schreibt nur nachts.", None),
        ("Er will nichts Festes, aber alles.", None),
        ("Er antwortet tagelang nicht.", None),
        ("Und er meldet sich, sobald du ihn vergisst.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du einen F-Boy? Markier ihn!", "Kennst du einen Eff-Boy? Markier ihn!"),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
