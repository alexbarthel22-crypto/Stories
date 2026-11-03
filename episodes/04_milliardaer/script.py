"""Folge 4: Heute ist Alex ... Milliardär.
Eigene Szenen/Gags (keine Übernahme aus dem Referenzvideo).

Fakten/Rechnungen:
- 1 Milliarde = 1.000 Millionen.
- 1.000 € pro Tag: 1.000.000.000 / 1.000 / 365 ≈ 2.740 Jahre.
- Mindestlohn 2026: 13,90 €/h (MiLoV5). Vollzeit 40 h/Woche ≈ 2.409 €/Monat ≈ 28.900 €/Jahr brutto
  -> 1 Mrd. / 28.912 € ≈ 34.590 Jahre.
- Beispiel 3 % Zinsen: 30 Mio. €/Jahr ≈ 82.000 €/Tag.
"""

ROLE = "MILLIARDÄR."
ROLE_TTS = "Milliardär."
ROLE_SAY = "Milliardär!"

MOODS = {
    "intro_pre": "spannend, aber zügig und kurz gesprochen, ohne lange Pause",
    "intro_role": "kurz, laut, triumphierend wie bei einem Jackpot",
    "what": "staunend, die Zahl wirkungsvoll betont",
    "minwage": "ungläubig und leicht empört, die Zahl langsam und deutlich",
    "morning": "übertrieben motiviert wie ein Hustle-Influencer, am Ende trocken-ironisch",
    "selfmade": "erst stolz und angeberisch, dann trocken entlarvend",
    "jet": "übertrieben glamourös, die Pointe trocken",
    "cars": "angeberisch, die Pointe absurd-trocken",
    "interest": "informativ wie ein Fun Fact, am Ende fassungslos",
    "yacht": "gespielt nachdenklich-philosophisch, dann trocken",
    "signs": "energisch wie ein Countdown, jedes Anzeichen mit Nachdruck",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("ARBEITSLOS.", "🛋️", "#8A8F99", "#5FA9B8"),
    ("CHOLERIKER.", "😡", "#3C4A63", "#D9534F"),
    ("EIN INFLUENCER.", "🤳", "#F07FB0", "#E26AA0"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

THUMB = dict(l1="MILLI-", l2="ARDÄR", bg="#1F6B4A", expr="smug", pose="hips", prop=None,
             emojis=("💰", "🛥️", "💎", "🥂"))

SCENES = [
    dict(id="what", bg="#1F6B4A", clock=None, title="WIE VIEL IST 1 MILLIARDE?", dark=True, lines=[
        ("Eine Milliarde, das sind tausend Millionen.", None),
        ("Gibst du jeden Tag 1.000 Euro aus, bist du erst nach 2.700 Jahren pleite.",
         "Gibst du jeden Tag tausend Euro aus, bist du erst nach zweitausendsiebenhundert Jahren pleite."),
    ]),
    dict(id="minwage", bg="#E9A23B", clock=None, title="ZUM VERGLEICH", lines=[
        ("Mit Mindestlohn, 13,90 Euro die Stunde, müsstest du über 34.000 Jahre Vollzeit arbeiten.",
         "Mit Mindestlohn, dreizehn Euro neunzig die Stunde, müsstest du über vierunddreißigtausend Jahre Vollzeit arbeiten."),
    ]),
    dict(id="morning", bg="#F2A65A", clock="05:00", title="MORNING ROUTINE", lines=[
        ("Fünf Uhr. Eisbad, Meditation, grüner Smoothie.", None),
        ("Danach ein Podcast über Mindset. Moderiert von ihm selbst.", None),
    ]),
    dict(id="selfmade", bg="#6C8CE0", clock="09:00", title="SELFMADE", lines=[
        ("Alex sagt gern: Ich hab bei null angefangen.", None),
        ("Mit einem kleinen Startkredit. Von Papa. Eine Million.", None),
    ]),
    dict(id="jet", bg="#36B5C2", clock="12:00", title="MITTAGESSEN", lines=[
        ("Zum Mittagessen fliegt er nach Paris. Im Privatjet. Für ein Croissant.", None),
    ]),
    dict(id="interest", bg="#2FA36B", clock=None, title="FUN FACT", lines=[
        ("Bei drei Prozent Zinsen bringt eine Milliarde 30 Millionen im Jahr.",
         "Bei drei Prozent Zinsen bringt eine Milliarde dreißig Millionen im Jahr."),
        ("Das sind über 80.000 Euro. Pro Tag. Fürs Nichtstun.",
         "Das sind über achtzigtausend Euro. Pro Tag. Fürs Nichtstun."),
    ]),
    dict(id="yacht", bg="#26345E", clock="21:00", title="AUF DER JACHT", dark=True, lines=[
        ("Abends auf seiner Jacht sagt Alex nachdenklich: Geld macht nicht glücklich.", None),
        ("Dann lässt er sich Champagner per Hubschrauber liefern.", None),
    ]),
    dict(id="signs", bg="#8E5BE0", clock=None, title="DIE 4 ANZEICHEN", dark=True, lines=[
        ("Woran du einen Milliardär erkennst:", None),
        ("Er sagt: Geld ist mir egal.", None),
        ("Sein grauer Pulli kostet 3.000 Euro.", "Sein grauer Pulli kostet dreitausend Euro."),
        ("Er hat einen Podcast.", None),
        ("Und er nennt sich bescheiden.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du einen Milliardär? Markier ihn! Er soll mir Geld leihen.", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
