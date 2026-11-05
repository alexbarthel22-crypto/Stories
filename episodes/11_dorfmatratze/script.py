"""TikTok Folge 4: Heute ist Alex ... eine Dorfmatratze. (ähnlich F-Boy, Dorf: jeder kennt jeden)
Nicht explizit; Outro markiert Dörfer/Leute, nicht 'Dorfmatratzen' (keine Bloßstellung).
Stimme exakt wie Pick-me-Boy: gemini-3.8-flash-tts, Puck, TTS_PROFILE="pickme", tighten 1.08.
"""
TTS_PROFILE = "pickme"
SAFE_MODE = "strict"
SAFE_TOP = 240
SAFE_LEFT = 100
EXTRAS = True
CAPTION_SIZE = 62
NAME_SCALE = 1.6
TITLE_SIZE = 92
BUBBLE_SCALE = 1.2
INTRO_SFX_GAIN = 3.4   # Reveal-Effekt
REVEAL_CUT = 0.3       # Reveal nur bis 0,3 s: danach leise Stimme aus dem Originalclip
INTRO_TICK_GAIN = 6.0  # Auswahl-Klicks während die Leiste läuft, extra laut
REACTIONS = {"bakery": ["🥐", "😬", "🚩"], "bus": ["🚌", "💀", "🚩"], "group": ["👀", "📢", "🚩"],
             "fest": ["💃", "😠", "🚩"], "night": ["👵", "👀", "🚩"]}

ROLE = "EINE DORFMATRATZE."
ROLE_TTS = "eine Dorfmatratze."
ROLE_SAY = "eine Dorfmatratze!"

MOODS = {
    "intro_pre": "geheimnisvoll und spannend, ruhig und flüssig, ohne Stocken; den Namen Alex deutsch aussprechen (kurzes A wie in Alexander)",
    "intro_role": "völlig überrascht und laut lachend amüsiert, wie ungläubig ausgerufen: Was?! Echt jetzt?",
    "what": "erklärend und amüsiert, die Pointe trocken",
    "motto": "amüsiert und verschmitzt, 'rammeln' frech betont, die Pointe 'bei drei auf dem Baum' schnell und lachend",
    "bakery": "peinlich berührt und amüsiert, die letzte Pointe verschwörerisch geflüstert und dann frech",
    "bus": "ungläubig amüsiert, die Pointe trocken",
    "group": "verschwörerisch wie Dorftratsch, dann trocken",
    "fest": "erst feierlich, dann peinlich berührt",
    "night": "flüsternd-spannend, dann trocken",
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

THUMB = dict(head="HEUTE IST ALEX EINE…", l1="DORF-", l2="MATRATZE", bg="#5E8C3A", color1="#FFFFFF",
             accent="#FFD34D", pill="#2E4A1C", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True,
             emojis=("🏘️", "👵", "💔", "🚩"))

SCENES = [
    dict(id="what", bg="#5E8C3A", clock=None, title="WAS IST EINE DORFMATRATZE?", dark=True, lines=[
        ("Eine Dorfmatratze hatte schon was mit fast jedem im Dorf.", None),
        ("Und in Wentorf bei Hamburg weiß das natürlich jeder. Da wird die Auswahl schnell klein.", None),
    ]),
    dict(id="motto", bg="#3F9A4A", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Alles rammeln, was nicht bei drei auf dem Baum ist.", None),
    ]),
    dict(id="bakery", bg="#E9A23B", clock="07:00", title="BEIM BÄCKER", lines=[
        ("Sieben Uhr beim Bäcker. Hinter der Theke: seine Ex.", None),
        ("Daneben ihre Mutter. Sie sagt nichts. Sie guckt nur.", None),
        ("Was die Ex nicht weiß: Mit ihrer Mutter hatte Alex auch schon was.", None),
    ]),
    dict(id="bus", bg="#4FA3C7", clock="08:00", title="IM BUS", lines=[
        ("Im Bus sitzen drei seiner Exen.", None),
        ("Und der Busfahrer ist der Onkel von einer.", None),
        ("Und mit dem hatte Alex auch schon was!", None),
    ]),
    dict(id="group", bg="#2FA36B", clock="15:00", title="DORF-WHATSAPP", lines=[
        ("Nachmittags in der Dorf-WhatsApp-Gruppe: Oma Hilde hat ihn gestern gesehen.", None),
        ("Mit wem, weiß jetzt das ganze Dorf.", None),
    ]),
    dict(id="fest", bg="#C0392B", clock="21:00", title="SCHÜTZENFEST", lines=[
        ("Abends Schützenfest. Alex tanzt mit Jana.", None),
        ("Lena und Sophie gucken böse. Alle drei sind Cousinen.", None),
    ]),
    dict(id="night", bg="#26345E", clock="23:30", title="DER HEIMWEG", dark=True, lines=[
        ("Auf dem Heimweg wackelt eine Gardine.", None),
        ("Morgen früh weiß es wieder jeder.", None),
    ]),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du eine Dorfmatratze erkennst:", None),
        ("Seine Exen haben eine eigene WhatsApp-Gruppe.", None),
        ("Auf jedem Fest muss er jemandem ausweichen.", None),
        ("Er datet schon im Nachbardorf.", None),
        ("Und er rammelt alles, was Beine hat.", None),
    ]),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch eine Dorfmatratze? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ]),
]

# Nur für die Stimme: "Aleks" geschrieben -> deutsches A statt englischem "Äläx"
GEMINI_LINE_TEXT = {"bakery_2": "Was die Ex nicht weiß: Mit ihrer Mutter hatte Aleks auch schon was."}
GEMINI_LINE_MOOD = {"bakery_2": "verschwörerisch geflüstert, dann trocken; den Namen deutsch aussprechen: A-leks mit offenem A wie in 'Alexander', niemals englisch 'Äläx'; kein Lachen, kein Kichern"}

# Bäcker etwas kürzer, Aufzählung schneller
LINE_TEMPO = {"bakery_0": 1.14, "bakery_1": 1.16, "bakery_2": 1.12,
              "signs_0": 1.22, "signs_1": 1.25, "signs_2": 1.25, "signs_3": 1.25, "signs_4": 1.2}
