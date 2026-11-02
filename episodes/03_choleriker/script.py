"""Folge 3: Heute ist Alex ... Choleriker.
Keine Gewalt gegen Menschen oder Tiere – Alex regt sich nur über Dinge und Situationen auf.
Jede Zeile: (Untertitel-Text, TTS-Text oder None).
"""

ROLE = "CHOLERIKER."
ROLE_TTS = "Choleriker."
ROLE_SAY = "Choleriker!"

MOODS = {
    "intro_pre": "spannend, aber zügig und kurz gesprochen, ohne lange Pause",
    "intro_role": "kurz, laut und explosiv wie ein Wutausbruch",
    "what": "erklärend, dann immer schneller und lauter bis zur Explosion",
    "toast": "erst ruhig, dann Alex' Zitat laut und empört, am Ende trocken",
    "traffic": "genervt und ungeduldig, das 'Ey!' laut gerufen",
    "office": "Alex' Zitat schreiend und verzweifelt, danach flüsternd-amüsiert über die Kollegen",
    "wifi": "dramatisch übertrieben, als wäre es eine Katastrophe",
    "market": "spannend wie ein Sportkommentator, dann enttäuscht",
    "gaming": "erst siegessicher, dann wütend, am Ende mitleidig-amüsiert",
    "sorry": "plötzlich ganz sanft und lieb, dann trocken und ironisch",
    "signs": "energisch wie ein Countdown, jedes Anzeichen mit Nachdruck",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("ARBEITSLOS.", "🛋️", "#8A8F99", "#5FA9B8"),
    ("EIN RENTNER.", "👓", "#8C6B4F", "#7C8A96"),
    ("EIN INFLUENCER.", "🤳", "#F07FB0", "#E26AA0"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

THUMB = dict(l1="CHOLE-", l2="RIKER", bg="#D9534F", expr="angry", pose="cross", prop=None,
             emojis=("💢", "💨", "🔥", "😤"))

SCENES = [
    dict(id="what", bg="#D9534F", clock=None, title="WAS IST EIN CHOLERIKER?", lines=[
        ("Ein Choleriker explodiert schneller, als du Entschuldigung sagen kannst.", None),
        ("Von null auf hundert. In einer Sekunde.", None),
    ]),
    dict(id="toast", bg="#F2A65A", clock="07:00", title="DER TOASTER", lines=[
        ("Sieben Uhr. Der Toast ist zu dunkel. Alex: Das ist doch nicht zu fassen!", None),
        ("Der Toaster sagt nichts. Das macht es nur schlimmer.", None),
    ]),
    dict(id="traffic", bg="#8FA3B8", clock="08:00", title="IM STAU", lines=[
        ("Im Stau hupt er, obwohl seit zehn Minuten niemand fährt.", None),
        ("Sein Lieblingswort: Ey!", None),
    ]),
    dict(id="office", bg="#6C8CE0", clock="10:00", title="IM BÜRO", lines=[
        ("Papierstau im Drucker. Alex: Warum passiert das immer mir?!", None),
        ("Seine Kollegen tun plötzlich alle sehr beschäftigt.", None),
    ]),
    dict(id="wifi", bg="#36B5C2", clock="13:00", title="DAS WLAN", lines=[
        ("Eine Seite lädt drei Sekunden zu lang. Für Alex: ein persönlicher Angriff.", None),
    ]),
    dict(id="market", bg="#2FA36B", clock="17:00", title="SUPERMARKT", lines=[
        ("An der Kasse: Kasse zwei macht auf! Alex sprintet los.", None),
        ("Jemand anderes ist schneller. Alex kocht.", None),
    ]),
    dict(id="gaming", bg="#5B3FA8", clock="20:00", title="GAMING", dark=True, lines=[
        ("Abends verliert er eine Runde. Alex: Der hat doch gecheatet!", None),
        ("Sein Controller muss sich einiges anhören.", None),
    ]),
    dict(id="sorry", bg="#F07FB0", clock="20:05", title="FÜNF MINUTEN SPÄTER", lines=[
        ("Fünf Minuten später: Sorry, war nicht so gemeint.", None),
        ("Das sagt er ungefähr zwölf Mal am Tag.", None),
    ]),
    dict(id="signs", bg="#C0392B", clock=None, title="DIE 4 ANZEICHEN", dark=True, lines=[
        ("Woran du einen Choleriker erkennst:", None),
        ("Roter Kopf.", None),
        ("Lauter als nötig.", None),
        ("Kleinigkeiten werden zur Katastrophe.", None),
        ("Und danach war angeblich nichts.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du noch einen Choleriker? Markier ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
