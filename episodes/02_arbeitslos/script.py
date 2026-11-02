"""Folge 2 (v2): Heute ist Alex ... arbeitslos – das volle Klischee, plus echte Fakten.

Fakten (Stand Nov. 2026, recherchiert):
- Arbeitslosengeld I: 60 % des pauschalierten Nettoentgelts (67 % mit Kind),
  unter 50 Jahren max. 12 Monate (bei 24 Monaten Versicherungszeit). Quelle: arbeitsagentur.de
- Grundsicherungsgeld (seit 1.7.2026, vorher Bürgergeld): Regelsatz Alleinstehende 563 €/Monat
  (2026 Nullrunde), Unterkunft + Heizung zusätzlich, sofern angemessen. Quellen: bundesregierung.de, bmas.de
- Nebenjob: Grundfreibetrag 100 €, darüber nur prozentuale Freibeträge.
Jede Zeile: (Untertitel-Text, TTS-Text oder None).
"""

ROLE = "ARBEITSLOS."
ROLE_TTS = "arbeitslos."
ROLE_SAY = "arbeitslos!"

MOODS = {
    "intro_pre": "spannend, aber zügig und kurz gesprochen, ohne lange Pause",
    "intro_role": "kurze, dramatische Enthüllung, halb mitleidig, halb lachend",
    "plan": "erst mitfühlend, dann amüsiert wie ein Modekommentator, der ein Outfit vorstellt",
    "money1": "klar und informativ wie ein Erklärvideo, aber locker",
    "money2": "informativ, die Zahlen deutlich betont, am Ende leicht ironisch",
    "morning": "verschlafen und gemütlich, trocken-witzig",
    "jobcenter": "erst sachlich-ernst, dann Alex' Witz übertrieben stolz, dann trocken und peinlich still",
    "tv": "wie ein dramatischer Fernsehsprecher, übertrieben spannend",
    "sidejob": "informativ wie ein Fun Fact, dann trocken-lustig",
    "family": "lieb, neugierig und locker",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

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

THUMB = dict(l1="ARBEITS", l2="LOS", bg="#5FA9B8", expr="smug", pose="idle", prop="beer",
             emojis=("📺", "💶", "🛋️", "🦗"))

# Running Gag: nach "Ich hab morgen frei!" zirpen Grillen
SFX = [("jobcenter", 1, 1.0, "crickets"), ("family", 1, 1.0, "crickets")]

SCENES = [
    dict(id="plan", bg="#5FA9B8", clock=None, title="JOB WEG", lines=[
        ("Alex hat seinen Job verloren. Firma pleite.", None),
        ("Heute das volle Klischee: Muskelshirt, Jogginghose, Bier in der Hand.", None),
    ]),
    dict(id="money1", bg="#2FA36B", clock=None, title="WAS ER BEKOMMT", lines=[
        ("Zuerst gibt's Arbeitslosengeld I: 60 Prozent vom letzten Netto.",
         "Zuerst gibt's Arbeitslosengeld eins: sechzig Prozent vom letzten Netto."),
        ("Bei 2.000 Euro netto: rund 1.200 Euro. Maximal zwölf Monate.",
         "Bei zweitausend Euro netto: rund zwölfhundert Euro. Maximal zwölf Monate."),
    ]),
    dict(id="money2", bg="#3E7BDA", clock=None, title="UND DANACH?", dark=True, lines=[
        ("Danach: Grundsicherungsgeld, früher Bürgergeld. 563 Euro im Monat.",
         "Danach: Grundsicherungsgeld, früher Bürgergeld. Fünfhundertdreiundsechzig Euro im Monat."),
        ("Plus angemessene Miete und Heizung. Macht rund 18,50 Euro am Tag.",
         "Plus angemessene Miete und Heizung. Macht rund achtzehn Euro fünfzig am Tag."),
    ]),
    dict(id="morning", bg="#F2C14E", clock="11:30", title="GUTEN MORGEN", lines=[
        ("Halb zwölf. Frühstück ist gleichzeitig Mittagessen.", None),
    ]),
    dict(id="jobcenter", bg="#8FA3B8", clock="12:30", title="JOBCENTER", lines=[
        ("Jobcenter-Termin. Wer ohne wichtigen Grund fehlt, dem kann das Geld gekürzt werden.", None),
        ("Alex: Ich hab morgen frei!", "Alex sagt stolz: Ich hab morgen frei!"),
        ("Niemand lacht.", None),
    ]),
    dict(id="tv", bg="#E07A5F", clock="14:00", title="FLIESENTISCH-TIME", lines=[
        ("Ab zwei: Fliesentisch, Chips und RTL.", None),
        ("Gerichtsshow. Am Ende war's der Nachbar.", None),
    ]),
    dict(id="sidejob", bg="#8E5BE0", clock="16:00", title="NEBENJOB?", dark=True, lines=[
        ("Fun Fact: Vom Nebenjob darf er die ersten 100 Euro behalten.",
         "Fun Fact: Vom Nebenjob darf er die ersten hundert Euro behalten."),
        ("Vom Rest nur ein Teil. Alex rechnet. Und macht ein Nickerchen.", None),
    ]),
    dict(id="family", bg="#E9A23B", clock="18:30", title="FAMILIENESSEN", lines=[
        ("Oma fragt: Und, was machst du gerade beruflich?", None),
        ("Alex: Ich hab morgen frei!", "Alex sagt stolz: Ich hab morgen frei!"),
        ("Wieder lacht niemand.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du noch jemanden, der gerade arbeitslos ist? Markier ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]

# Stille nach dem Gag (für das Grillenzirpen), in Sekunden
PAUSE_AFTER = {("jobcenter", 1): 1.3, ("family", 1): 1.3}
