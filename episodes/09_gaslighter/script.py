"""TikTok Folge 4: Heute ist Alex ... ein Gaslighter. (Aufbau wie Pick-me-Boy, kurz gehalten)
Ton: typische Sätze wiedererkennbar machen, nicht verharmlosen; ernster Satz am Ende.
Stimme exakt wie Pick-me-Boy: gemini-3.8-flash-tts, Puck, TTS_PROFILE="pickme", tighten 1.08.
"""

TTS_PROFILE = "pickme"

ROLE = "EIN GASLIGHTER."
ROLE_TTS = "ein Gaslighter."
ROLE_SAY = "ein Gaslighter!"

MOODS = {
    "intro_pre": "geheimnisvoll und spannend, ruhig und flüssig, ohne Stocken; den Namen Alex deutsch aussprechen (kurzes A wie in Alexander)",
    "intro_role": "dramatische Enthüllung, eher ernst als lustig",
    "what": "erklärend und klar; das Zitat von Alex kühl und überzeugt",
    "forgot": "ungläubig, das Zitat von Alex lässig und selbstsicher",
    "proof": "trocken und entlarvend",
    "joke": "erst locker, dann ernüchtert; das Zitat von Alex abwertend",
    "fight": "ruhig und kopfschüttelnd, die Pointe trocken",
    "signs": "energisch wie ein Countdown, jedes Anzeichen mit Nachdruck",
    "real": "ruhig, warm und ehrlich, ohne Ironie",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("EMOTIONAL ABHÄNGIG.", "🥺", "#7FA3D6", "#3E5C9A"),
    ("FRIEDRICH MERZ.", "🎙️", "#1F2A44", "#1F3A6B"),
    ("EIN INFLUENCER.", "🤳", "#F07FB0", "#E26AA0"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

# Cover: Anordnung wie Pick-me-Boy, Farben zum Thema (verwirrendes Lila, Gaslampen-Orange)
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="", l2="GASLIGHTER", bg="#4A2E6B", accent="#FFB547",
             pill="#1E1230", pill_text="#FFFFFF", expr="smug", pose="shrug", prop=None,
             emojis=("🌀", "🚩", "🤷", "🙄"))

SCENES = [
    dict(id="what", bg="#4A2E6B", clock=None, title="WAS IST GASLIGHTING?", dark=True, lines=[
        ("Gaslighting heißt: Jemand bringt dich dazu, an deiner eigenen Wahrnehmung zu zweifeln.", None),
        ("Alex' Lieblingssatz: Das hab ich nie gesagt.", None),
    ]),
    dict(id="forgot", bg="#4FA3C7", clock="08:00", title="VERGESSEN", lines=[
        ("Alex vergisst, Lena abzuholen. Seine Erklärung: Du hast doch gesagt, du nimmst den Bus.", None),
    ]),
    dict(id="proof", bg="#F2A65A", clock="12:00", title="DER BEWEIS", lines=[
        ("Lena zeigt ihm seine eigene Nachricht. Alex: Das hast du falsch verstanden.", None),
    ]),
    dict(id="joke", bg="#E06A6A", clock="19:00", title="DER WITZ", lines=[
        ("Abends macht er einen fiesen Witz über sie. Lena ist verletzt. Alex: Du bist einfach zu empfindlich.", None),
    ]),
    dict(id="fight", bg="#26345E", clock="22:00", title="DER STREIT", dark=True, lines=[
        ("Im Streit dreht er alles um. Am Ende entschuldigt sich Lena. Bei ihm.", None),
    ]),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Gaslighter erkennst:", None),
        ("Das hab ich nie gesagt.", None),
        ("Du bist zu empfindlich.", None),
        ("Du bildest dir das ein.", None),
        ("Und am Ende bist du schuld.", None),
    ]),
    dict(id="real", bg="#F7B2C9", clock=None, title="MAL ERNST", lines=[
        ("Und mal ernst: Vertrau deiner Wahrnehmung. Und rede mit Menschen, denen du vertraust.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du jemanden, der auch immer sagt: Das hab ich nie gesagt? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
