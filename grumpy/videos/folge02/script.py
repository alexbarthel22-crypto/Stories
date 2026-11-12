"""Tag 2 – Drehbuch: Kommentare (Reihenfolge: Katastrophen zuerst) und Claras Text.
Felder: key, user, comment, pre (Sekunden Animation VOR Claras Satz), lines [(tag, gesprochen, Untertitel)]"""

SEGMENTS = [
    dict(key="intro", user=None, comment=None, pre=0.0, lines=[
        ("[angry]", "Ihr habt echt kommentiert?!", "IHR HABT ECHT KOMMENTIERT?!"),
        ("[annoyed]", "Wer macht denn bei so einem Scheiß mit?!", "Wer macht denn bei so einem Sch🥚ß mit?!"),
        ("[sighs]", "Na gut. Dann eben so.", "Na gut. Dann eben so."),
    ]),
    dict(key="vulkan", user="❤️🌹", comment="Ein Vulkanausbruch", pre=2.2, lines=[
        ("[sarcastic]", "Das fängt ja hier wieder richtig respektlos an.", "Das fängt ja hier wieder richtig RESPEKTLOS an."),
    ]),
    dict(key="tsunami", user="david🇬🇪", comment="ey ein tsunamie kommt jetzt", pre=1.9, lines=[
        ("[annoyed]", "Oha, was ein Tsunami.", "Oha, was ein TSUNAMI."),
        ("[sarcastic]", "Als hätte Regen nicht gereicht. Übertreib halt direkt.", "Als hätte Regen nicht gereicht. Übertreib halt direkt."),
    ]),
    dict(key="baum", user="Corny_Tech", comment="Der baum soll umfallen", pre=1.1, lines=[
        ("[deadpan]", "Der einzige Schatten hier. Danke.", "Der einzige Schatten hier. Danke."),
    ]),
    dict(key="zigaretten", user="¤LEMI.42¤", comment="500 Zigaretten fallen vom himmel", pre=1.5, lines=[
        ("[annoyed]", "Ich rauch nicht mal! Und jetzt sind die auch noch nass.", "Ich rauch nicht mal! Und jetzt sind die auch noch nass."),
    ]),
    dict(key="haus", user="Scoot.Nik459", comment="ein Haus damit du da leben kannst", pre=0.8, lines=[
        ("[surprised]", "Oh. Ein Haus. Das ist… tatsächlich nett.", "Oh. Ein Haus. Das ist … tatsächlich nett."),
    ]),
    dict(key="toilette", user="❤️🌹", comment="Eine Toilette", pre=0.7, lines=[
        ("[annoyed]", "Ich weiß nicht, wo ihr aufs Klo geht, aber das Klo wäre im Haus irgendwie besser gewesen.",
         "Ich weiß nicht, wo ihr aufs Klo geht, aber das Klo wäre im Haus irgendwie besser gewesen."),
        ("[sighs]", "Aber egal.", "Aber egal."),
    ]),
    dict(key="doener", user="Team_Fisch🐟", comment="ein dönerladen bauen", pre=0.8, lines=[
        ("[confused]", "Digga, wieso kostet der Döner fünf Euro?", "Digga, wieso kostet der Döner 5 €?"),
        ("[annoyed]", "Und wen bezahle ich? Da arbeitet doch gar keiner.", "Und wen bezahle ich? Da arbeitet doch gar KEINER."),
    ]),
    dict(key="angel", user="01_k61", comment="Wann nächster Part und bitte mach die angelstation", pre=0.7, lines=[
        ("", "Hier ist dein Part. Angelstation steht.", "Hier ist dein Part. Angelstation steht."),
    ]),
    dict(key="angeln", user="LHW_Oli", comment="Angeln", pre=1.0, lines=[
        ("[confused]", "Digga, warte mal, woher hab ich eigentlich die Angel?", "Digga, warte mal, woher hab ich eigentlich die ANGEL?"),
        ("[shrugs]", "Naja, egal.", "Naja, egal."),
        ("[surprised]", "Mein Schuh?!", "Mein SCHUH?!"),
    ]),
    dict(key="bob", user="《M》 ▸ Clara🖤", comment="Bob kann Fisch fangen 2x pro Tag morgens und abends.", pre=1.2, lines=[
        ("[sarcastic]", "Das ist Bob. Fängt zweimal am Tag Fisch. Mein neuer bester Freund.",
         "Das ist Bob. Fängt zweimal am Tag Fisch. Mein neuer bester Freund."),
    ]),
    dict(key="rucksack", user="joleen",
         comment=("Ich gebe dir einen Rucksack, damit du deine Sachen transportieren kannst. Dazu bekommst du eine Wasserflasche, "
                  "damit du Wasser aufbewahren kannst, eine Taschenlampe, damit du nachts sehen kannst, und einen Kompass, damit du "
                  "dich orientieren kannst. Außerdem gebe ich dir ein Zelt, das dich vor Regen schützt, ein Seil, um Dinge zu "
                  "befestigen, ein Erste-Hilfe-Set für kleine Verletzungen und Streichhölzer, um ein Feuer zu machen. Ein Messer "
                  "bekommst du auch, um Lebensmittel vorzubereiten und Materialien zu schneiden."),
         pre=0.8, lines=[
        ("[surprised]", "Wasser, Lampe, Kompass, Zelt, Seil, Erste Hilfe, Streichhölzer, Messer…",
         "Wasser, Lampe, Kompass, Zelt, Seil, Erste Hilfe, Streichhölzer, Messer …"),
        ("[impressed]", "Joleen, du bist die Einzige hier mit Verstand.", "Joleen, du bist die Einzige hier mit Verstand."),
    ]),
    dict(key="krabbe", user="Muchacho",
         comment="Trink erst mal etwas eine Kokosnuss vom Baum und dann töte die Krabbe und iss sie roh fals du es braten kannst tu es!",
         pre=0.5, lines=[
        ("[satisfied]", "Kokosnuss: gut.", "Kokosnuss: gut."),
        ("[annoyed]", "Aber die Krabbe? Nein. Die versteht mich als Einzige.", "Aber die Krabbe? NEIN. Die versteht mich als Einzige."),
    ]),
    dict(key="flugzeug", user="lyrics guy", comment="ein Flugzeug kommt und gibt sie essen", pre=2.0, lines=[
        ("[annoyed]", "Hätte mich ja gleich mitnehmen können.", "Hätte mich ja gleich MITNEHMEN können."),
        ("[sarcastic]", "Aber was weiß ich schon.", "Aber was weiß ich schon."),
    ]),
    dict(key="villa", user="Michyx🦦💦", comment="so ne rießen insel mit hafen und ner rießen villa", pre=2.4, lines=[
        ("[impressed]", "Okay… das ist ziemlich geil.", "Okay … das ist ziemlich geil."),
        ("[annoyed]", "Ich hasse, dass es mir gefällt.", "Ich hasse, dass es mir gefällt."),
    ]),
    dict(key="outro", user=None, comment=None, pre=0.4, lines=[
        ("[annoyed]", "Schreibt in die Kommentare, was mit mir und der Insel im nächsten Video passieren soll.",
         "Schreibt in die Kommentare, was mit mir und der Insel im nächsten Video passieren soll."),
        ("[serious]", "Und alles, was in den Kommentaren steht, passiert. Ausnahmslos.",
         "Und ALLES, was in den Kommentaren steht, passiert. Ausnahmslos."),
        ("[sighs]", "Ich hasse mein Leben.", "Ich hasse mein Leben."),
    ]),
]

# Soundeffekte relativ zum Beginn der Animation eines Segments: (segment, datei, offset)
SFX = [
    ("vulkan", "rumble", 0.0), ("vulkan", "boom", 1.0),
    ("tsunami", "wave", 0.0),
    ("baum", "thud", 0.75),
    ("zigaretten", "patter", 0.1),
    ("haus", "pop", 0.25), ("toilette", "pop", 0.2), ("doener", "pop", 0.25), ("angel", "pop", 0.2),
    ("angeln", "splash", 0.15),
    ("bob", "splash", 0.1),
    ("rucksack", "thud", 0.55),
    ("flugzeug", "plane", 0.0),
    ("villa", "magic", 0.0), ("villa", "rumble", 0.1),
]
