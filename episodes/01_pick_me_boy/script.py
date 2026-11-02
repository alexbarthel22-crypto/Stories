"""Folge 1: Heute ist Alex ... ein Pick-me-Boy.

Jede Zeile: (Untertitel-Text, TTS-Text). Ist der TTS-Text None, wird der
Untertitel-Text gesprochen. Der TTS-Text enthält Lautschrift-Tricks, damit die
deutsche Stimme englische Wörter richtig ausspricht.
"""

ROLE = "EIN PICK ME BOY."
ROLE_TTS = "ein Pickmibeu."   # nur für die lokale Piper-Stimme
ROLE_SAY = "ein Pick-me-Boy!"   # Gemini spricht Englisch korrekt

# Stimmung je Szene (Regieanweisung für die Gemini-Stimme)
MOODS = {
    "intro_pre": "geheimnisvoll und spannend, wie vor einer großen Enthüllung, langgezogen",
    "intro_role": "triumphierende, laute Enthüllung mit einem Augenzwinkern",
    "what": "erklärend, amüsiert; das Zitat von Alex übertrieben selbstverliebt",
    "morning": "spöttisch-dramatisch, das traurige Zitat theatralisch-melancholisch",
    "train": "verschwörerisch flüsternd-amüsiert, die Pointe trocken",
    "lunch": "ungläubig, leicht genervt, das Zitat von Alex arrogant",
    "insta": "sarkastisch; die Kommentare übertrieben schmalzig vorlesen",
    "date": "romantisch-kitschig aufgebaut, dann trocken und entlarvend; Song-Teil peinlich berührt",
    "texts": "immer hektischer und überdrehter, dann trocken die Pointe",
    "reject": "erst mitfühlend, dann schockiert über Alex' Wut, am Ende ernst und klar",
    "flags": "energisch wie ein Countdown, jede Red Flag mit Nachdruck",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

# Rollen, die im Intro durchgeschaltet werden (Text, Emoji, Oberteil, Hintergrund)
SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN GYM-BRO.", "🏋", "#2B2B2B", "#D2453D"),
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

SCENES = [
    dict(id="what", bg="#7B5CD6", clock=None, title="WAS IST EIN PICK ME BOY?", lines=[
        ("Ein Pick-me-Boy will vor allem eins: von Mädchen ausgewählt werden.",
         "Ein Pickmibeu will vor allem eins: von Mädchen ausgewählt werden."),
        ("Sein Lieblingssatz: Ich bin nicht wie die anderen Jungs.", None),
    ]),
    dict(id="morning", bg="#F2A65A", clock="07:00", title="GUTEN MORGEN", lines=[
        ("Sieben Uhr. Alex wacht auf und postet sofort ein Foto.", None),
        ("Sonnenaufgang in Schwarz-Weiß, dazu ein trauriges Zitat.", None),
    ]),
    dict(id="train", bg="#4FA3C7", clock="08:30", title="IN DER BAHN", lines=[
        ("In der Bahn liest Alex ein Buch. Aber so, dass jedes Mädchen das Cover sieht.",
         "In der Bahn liest Alex ein Buch. Aber so, dass jedes Mädchen das Kawwer sieht."),
        ("Gelesen hat er nur den Klappentext.", None),
    ]),
    dict(id="lunch", bg="#6CC08B", clock="12:00", title="MITTAGSPAUSE", lines=[
        ("Mittags erzählt er: Ich hab nur Freundinnen. Jungs sind mir zu oberflächlich.", None),
        ("Er macht andere Jungs schlecht, damit er selbst besser dasteht.", None),
    ]),
    dict(id="insta", bg="#E98AB8", clock="15:00", title="SOCIAL MEDIA", lines=[
        ("In seiner Bio steht: Ich respektiere Frauen.", None),
        ("Unter Fotos von Mädchen kommentiert er: Ich würde dich nie so behandeln wie er.", None),
    ]),
    dict(id="date", bg="#E06A6A", clock="19:00", title="DAS DATE", lines=[
        ("Abends hat Alex ein Date mit Lena.", "Abends hat Alex ein Deit mit Lena."),
        ("Nach zehn Minuten sagt er: Du bist nicht wie die anderen Mädchen.", None),
        ("Klingt süß, macht aber alle anderen Mädchen schlecht.", None),
        ("Dann holt er die Gitarre raus. Mit einem Song über sie. Nach einem Date.",
         "Dann holt er die Gitarre raus. Mit einem Song über sie. Nach einem Deit."),
    ]),
    dict(id="texts", bg="#26345E", clock="21:00", title="DIE NACHRICHTEN", dark=True, lines=[
        ("Noch am selben Abend: dreißig Nachrichten. Ich glaub, ich hab mich verliebt.", None),
        ("Das nennt man Lovebombing.", "Das nennt man Läff-Bomming."),
    ]),
    dict(id="reject", bg="#3A2A5C", clock="22:00", title="DIE ANTWORT", dark=True, lines=[
        ("Lena schreibt: Ich sehe dich eher als Kumpel.", None),
        ("Und plötzlich ist der nette Alex weg: Typisch. Frauen wollen eh nur Bad Boys.",
         "Und plötzlich ist der nette Alex weg: Typisch. Frauen wollen eh nur Bädbeuss."),
        ("Denn er war nie einfach nett. Er wollte eine Belohnung dafür.", None),
    ]),
    dict(id="flags", bg="#D9534F", clock=None, title="DIE 4 RED FLAGS", lines=[
        ("Die nervigsten Red Flags:", "Die nervigsten Räd Fläggs:"),
        ("Er macht andere Jungs schlecht.", None),
        ("Er macht andere Mädchen schlecht.", None),
        ("Er ist nur nett mit Hintergedanken.", None),
        ("Und er braucht für alles Publikum.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du noch einen Pick-me-Boy? Markier ihn!",
         "Kennst du noch einen Pickmibeu? Markier ihn!"),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
