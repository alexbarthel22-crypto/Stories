"""TikTok Folge 3: Heute ist Alex ... Friedrich Merz (Parodie, jugendgerecht, unpolitisch).
Belegte Fakten: Bundeskanzler; geboren in Brilon (Sauerland); Hobbypilot mit eigenem Flugzeug;
2018 Selbsteinordnung "gehobene Mittelschicht" bei rund 1 Mio. € Jahreseinkommen.
Netz-Gag: Vergleich mit Mr. Burns (Simpsons). Bewusst weggelassen: beleidigende Memes, Parteipolitik.
Stimme exakt wie Pick-me-Boy: gemini-3.8-flash-tts, Puck, TTS_PROFILE="pickme", tighten 1.08.
"""

TTS_PROFILE = "pickme"

ROLE = "FRIEDRICH MERZ."
ROLE_TTS = "Friedrich Merz."
ROLE_SAY = "Friedrich Merz!"

MOODS = {
    # Intro-Stimmungen 1:1 wie in Folge 1 (Pick-me-Boy)
    "intro_pre": "geheimnisvoll und spannend, wie vor einer großen Enthüllung, langgezogen",
    "intro_role": "triumphierende, laute Enthüllung mit einem Augenzwinkern",
    "what": "erklärend und amüsiert, wie eine Vorstellung mit Augenzwinkern",
    "sauerland": "gemütlich und heimatverbunden, dann amüsiert-ironisch",
    "jet": "übertrieben glamourös, die Pointe trocken",
    "mittel": "erst gespielt bescheiden, dann ungläubig und trocken",
    "speech": "übertrieben feierlich und langsam, dann trocken amüsiert",
    "burns": "verschwörerisch amüsiert, das 'Ausgezeichnet' gespielt fies und genüsslich",
    "signs": "energisch wie ein Countdown, jedes Anzeichen mit Nachdruck",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("EMOTIONAL ABHÄNGIG.", "🥺", "#7FA3D6", "#3E5C9A"),
    ("EIN KOCH.", "🍳", "#F4F4F4", "#E3A23B"),
    ("EIN INFLUENCER.", "🤳", "#F07FB0", "#E26AA0"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

# Cover: Anordnung wie Pick-me-Boy, Farben zum Thema (Kanzler-Blau, Gold)
THUMB = dict(head="HEUTE IST ALEX…", l1="FRIEDRICH", l2="MERZ", bg="#1F3A6B", color1="#FFFFFF",
             accent="#F7C948", pill="#0E1A33", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None,
             emojis=("🛩️", "🎙️", "⛰️", "📏"))

SCENES = [
    dict(id="what", bg="#1F3A6B", clock=None, title="WER IST FRIEDRICH MERZ?", dark=True, lines=[
        ("Friedrich Merz ist Bundeskanzler. Und heute spielt Alex ihn. Als Parodie, versteht sich.", None),
        ("Erkennungszeichen: Brille, Anzug, und ganz, ganz groß.", None),
    ]),
    dict(id="sauerland", bg="#6CC08B", clock="06:00", title="IM SAUERLAND", lines=[
        ("Sechs Uhr im Sauerland. Da kommt er her, aus Brilon.", None),
        ("Und egal, worüber Kanzler-Alex redet: Am Ende landet er irgendwie im Sauerland.", None),
    ]),
    dict(id="jet", bg="#4FA3C7", clock="08:00", title="ZUR ARBEIT", lines=[
        ("Andere nehmen den Bus. Kanzler-Alex fliegt selbst. Er ist nämlich Hobbypilot mit eigenem Flugzeug.", None),
        ("Ziel heute: der Bäcker um die Ecke.", None),
    ]),
    dict(id="mittel", bg="#E9A23B", clock="12:00", title="MITTELSCHICHT", lines=[
        ("Mittags sagt er: Ich gehöre zur gehobenen Mittelschicht.", None),
        ("Das hat Merz wirklich mal gesagt. Bei rund einer Million Euro im Jahr.", None),
    ]),
    dict(id="speech", bg="#8E5BE0", clock="15:00", title="DIE REDE", dark=True, lines=[
        ("Nachmittags hält er eine Rede. Sehr lang. Sehr ernst.", None),
        ("Nach zehn Minuten schlafen alle. Außer ihm.", None),
    ]),
    dict(id="burns", bg="#26345E", clock="20:00", title="IM INTERNET", dark=True, lines=[
        ("Im Netz wird Merz oft mit Mister Burns von den Simpsons verglichen.", None),
        ("Alex übt schon mal: Ausgezeichnet.", None),
    ]),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du Kanzler-Alex erkennst:", None),
        ("Er ist größer als alle.", None),
        ("Er fliegt selbst.", None),
        ("Alles führt ins Sauerland.", None),
        ("Und keine Rede ist kurz.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du jemanden, der auch so gern lange Reden hält? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
