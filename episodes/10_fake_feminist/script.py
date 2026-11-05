"""TikTok Folge 3: Heute ist Alex ... ein Fake-Feminist. (Aufbau wie Pick-me-Boy)
Humor über performativen 'Feminismus' – nicht über Feminismus selbst.
Layout: SAFE_MODE "strict" (TikTok-Sicherheitsbereiche komplett frei).
Stimme exakt wie Pick-me-Boy: gemini-3.8-flash-tts, Puck, TTS_PROFILE="pickme", tighten 1.08.
"""

TTS_PROFILE = "pickme"
SAFE_MODE = "strict"
CAPTION_SIZE = 62        # größere Untertitel
TITLE_SIZE = 92          # größere Überschriften
BUBBLE_SCALE = 1.2       # größere Sprechblasen
NAME_SCALE = 1.6         # größeres Namensschild
MUSIC = "marimba" # eigenes lizenzfreies Thema (fröhliche Marimba), mit Ducking unter der Stimme
INTRO_SFX_GAIN = 2.2   # Auswahl-Klicks + Reveal im Intro lauter
EXTRAS = True     # Red-Flag-Zähler, Tagesleiste, Reaktions-Emojis, Wisch-Übergänge
REACTIONS = {"post": ["📈", "🙄", "🚩"], "mansplain": ["🤦", "😂", "🚩"], "work": ["😤", "🙄", "🚩"],
             "home": ["🧽", "😂", "🚩"], "men": ["🤡", "🙄", "🚩"]}

ROLE = "EIN FAKE-FEMINIST."
ROLE_TTS = "ein Fake-Feminist."
ROLE_SAY = "ein Fake-Feminist!"

MOODS = {
    "intro_pre": "geheimnisvoll und spannend, ruhig und flüssig, ohne Stocken; den Namen Alex deutsch aussprechen (kurzes A wie in Alexander)",
    "intro_role": "triumphierende, laute Enthüllung mit einem Augenzwinkern",
    "what": "erklärend und amüsiert; das Zitat von Alex laut und stolz",
    "post": "übertrieben pathetisch wie ein Influencer, dann trocken",
    "mansplain": "amüsiert-ungläubig, das Zitat von Alex belehrend und selbstverliebt",
    "work": "trocken und entlarvend",
    "home": "erst stolz, dann trocken entlarvend",
    "men": "erst übertrieben empört und laut, dann trocken und entlarvend",
    "signs": "energisch wie ein Countdown, jedes Anzeichen mit Nachdruck",
    "outro": "freundlich, aufgedreht, direkt an die Zuschauer, auffordernd",
}

SHUFFLE = [
    ("EIN ASTRONAUT.", "🚀", "#E9EEF5", "#3B6FB6"),
    ("EIN PICK ME BOY.", "🌹", "#EFE2C6", "#EC7FAE"),
    ("EIN GAMER.", "🎮", "#6A3FC4", "#8E5BE0"),
    ("EMOTIONAL ABHÄNGIG.", "🥺", "#7FA3D6", "#3E5C9A"),
    ("EIN GASLIGHTER.", "🌀", "#3F5A4A", "#4A2E6B"),
    ("EIN INFLUENCER.", "🤳", "#F07FB0", "#E26AA0"),
    ("EIN BAUARBEITER.", "👷", "#F2A23A", "#C9852E"),
    ("EIN DJ.", "🎧", "#1E1E1E", "#2E3A8C"),
    ("EIN PIRAT.", "🏴", "#7A2E2E", "#3D8C7A"),
    ("EIN LEHRER.", "🍎", "#3E6B48", "#5FA36E"),
    ("EIN POLIZIST.", "👮", "#23406E", "#3B5BA8"),
    ("EIN ROCKSTAR.", "🎸", "#151515", "#5C5C66"),
]

# Cover: Anordnung wie Pick-me-Boy, Farben zum Thema (Lila + Pink, "Fake" in Gelb)
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="FAKE-", l2="FEMINIST", bg="#7A3FA8", color1="#FFE14D",
             accent="#FF7BC0", pill="#2A1240", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None,
             emojis=("🚩", "📢", "👕", "🙄"))

SCENES = [
    dict(id="what", bg="#7A3FA8", clock=None, title="WAS IST EIN FAKE-FEMINIST?", dark=True, lines=[
        ("Ein Fake-Feminist ist Feminist. Aber nur, wenn jemand zuschaut.", None),
        ("Sein Lieblingssatz: Ich bin der größte Feminist, den du kennst.", None),
    ]),
    dict(id="post", bg="#F07FB0", clock="09:00", title="DER POST", lines=[
        ("Morgens postet er ein Foto im Shirt: The future is female.", None),
        ("Die Likes zählt er öfter als seine Freunde.", None),
    ]),
    dict(id="mansplain", bg="#6C8CE0", clock="12:00", title="DIE ERKLÄRUNG", lines=[
        ("In der Mittagspause erklärt Alex seiner Kollegin, was Feminismus ist.", None),
        ("Sie ist Gleichstellungsbeauftragte.", None),
    ]),
    dict(id="work", bg="#2FA36B", clock="15:00", title="IM MEETING", lines=[
        ("Im Meeting hat Lea eine richtig gute Idee. Alex wiederholt sie lauter. Und bekommt das Lob.", None),
    ]),
    dict(id="home", bg="#E9A23B", clock="19:00", title="ZU HAUSE", lines=[
        ("Zu Hause sagt er stolz: Ich helfe ja im Haushalt.", None),
        ("Helfen. Als wäre es nicht auch seine Wohnung.", None),
    ]),
    dict(id="men", bg="#E06A6A", clock="21:00", title="ALLE MÄNNER?", lines=[
        ("Abends postet er: Männer sind das Problem. Alle Männer!", None),
        ("Und er selbst? Na ja, er ist ja anders.", None),
    ]),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Fake-Feministen erkennst:", None),
        ("Feminist nur online.", None),
        ("Erklärt Frauen den Feminismus.", None),
        ("Hilft im Haushalt, statt mitzumachen.", None),
        ("Gleichberechtigung nur, wenn's ihm nützt.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch so einen Fake-Feministen? Markier ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]
