"""TikTok-Folge: Heute ist Alex ... ein Doppelmoralist. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#555A66", top_style="tee", pants="#2F3B52", shoes="#FFFFFF")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894")
TOM = person_spec(12, top="#36B5C2", hair="#3B2A20")
ROLE, ROLE_TTS, ROLE_SAY = "EIN DOPPELMORALIST.", "ein Doppelmoralist.", "ein Doppelmoralist!"
MOODS = dict(MOODS_BASE, bus="empört, dann trocken", essen="belehrend, dann trocken", umwelt="engagiert, dann trocken",
             chat="eifersüchtig, die Pointe trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"bus": ["🔊", "📞", "🚩"], "essen": ["📱", "🙄", "🚩"], "umwelt": ["♻️", "🚗", "🚩"], "chat": ["❤️", "💀", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EIN…", l1="DOPPEL-", l2="MORALIST", bg="#3B4252", color1="#FFFFFF", accent="#FFE14D",
             pill="#1C1F26", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("⚖️", "🙊", "🤥", "🚩"))
INTRO_CFG = dict(icon="⚖️", bg="#3B4252", title_lines=["DOPPELMORALIST."],
                 house=dict(sky=("#6B7894", "#E6ECF5"), walls="#F2F4F8", roof="#2B2F3A", door="#1C1F26", lawn="#5DAA5E",
                            accent=("#E23B3B", "#2FA36B"), sun=True),
                 left=("📜", "REGELN"), right=("😎", "AUSNAHME"), door=("REGELN GELTEN", "FÜR EUCH ☝️"),
                 neon=("DU NICHT,", "ICH SCHON 😎", "#FF6A6A"), signs=("Handy weg beim Essen! ☝️", "*scrollt TikTok* 📱"),
                 fly=["⚖️", "☝️", "😎"], burst=["⚖️", "☝️", "😎", "📜", "🙊", "🤥", "🚗", "📱"],
                 extras=[("☝️", 34, 60, 12)])

SCENES = [
    dict(id="what", bg="#3B4252", clock=None, title="WAS IST EIN DOPPELMORALIST?", dark=True, lines=[
        ("Ein Doppelmoralist hat ganz strenge Regeln.", None),
        ("Aber die gelten nur für die anderen.", None),
    ], viz=dict(kind="bars", head="WER HÄLT SICH DRAN?", rows=[("IHR", 1.0, "100 %", "#2FA36B"), ("ER", 0.0, "0 %", "#E23B3B")],
                pills=[("📜", "Regeln: für alle", "#E23B3B"), ("😎", "Ausnahme: er selbst", "#2B2F3A")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Mach, was ich sage. Nicht, was ich mache.", None),
    ], viz=dict(kind="stage", box="#F2F4F8", head="⚖️ DIE WAAGE", head_col="#3B4252",
                items=[("⚖️", 540, 680, 220, 0, "shake"), ("☝️", 300, 640, 110, 0, "pulse"), ("😎", 780, 640, 110, 0, "bob")],
                tags=[("REDEN ≠ MACHEN", "#E23B3B")], move="wobble", alex=("smug", "hips", None))),
    dict(id="bus", bg="#D9A441", clock="08:00", title="IM BUS", lines=[
        ("Acht Uhr. Er beschwert sich über laute Musik im Bus.", None),
        ("Dann telefoniert er zwanzig Minuten. Auf Lautsprecher.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", floor="#8C8C96", head="🚌 LINIE 8", head_col="#A8642E",
                items=[("🎧", 760, 640, 110, 0, "shake"), ("🤫", 330, 640, 120, 0, "pulse"), ("📞", 330, 850, 110, 1, "shake"),
                       ("🔊", 480, 820, 100, 1, "pulse")],
                tags=[("„LEISER BITTE!“ ☝️", "#3E7BDA", 330, 560), ("LAUTSPRECHER 📢 20 MIN", "#E23B3B", 540, 980)],
                fx="anger", move="rumble", alex=("angry", "idle", "📱"))),
    dict(id="essen", bg="#2FA36B", clock="12:00", title="BEIM ESSEN", dark=True, lines=[
        ("Mittags erklärt er Tom, dass Handys beim Essen unhöflich sind.", None),
        ("Und scrollt dabei durch TikTok.", None),
    ], viz=dict(kind="stage", box="#E8FFE0", head="🍝 MITTAGESSEN", head_col="#2E6B34",
                people=[(TOM, 790, "Tom", "neutral", 1)],
                items=[("🍝", 430, 870, 100, 0, "bob"), ("☝️", 330, 640, 110, 0, "pulse"), ("📱", 330, 790, 100, 1, "shake")],
                tags=[("„HANDY WEG!“ ☝️", "#2E6B34", 330, 560), ("… SCROLLT 📱", "#E23B3B", 540, 980)], fx="anger",
                move="wobble", alex=("smug", "idle", "📱"))),
    dict(id="umwelt", bg="#5B6BC9", clock="16:00", title="UMWELTSCHUTZ", dark=True, lines=[
        ("Nachmittags hält er einen Vortrag über Umweltschutz.", None),
        ("Dann fährt er die dreihundert Meter zum Bäcker. Mit dem Auto.", None),
    ], viz=dict(kind="stage", box="#E8FFE0", floor="#8C8C96", head="🌍 RETTET DIE WELT", head_col="#2E6B34",
                items=[("🌍", 330, 650, 160, 0, "spin"), ("♻️", 560, 620, 100, 0, "pulse"), ("🚗", 640, 870, 160, 1, "shake"),
                       ("💨", 470, 880, 90, 1, "fly"), ("🥖", 860, 820, 80, 1, "bob")],
                tags=[None, ("300 M MIT AUTO 🚗", "#E23B3B", 640, 980)], fx="shock", move="wobble", flash="#FF3B3B",
                alex=("smug", "idle", None))),
    dict(id="chat", bg="#36B5C2", clock="20:00", title="EIFERSUCHT", lines=[
        ("Abends regt er sich auf, weil Lena einem Typen ein Like gegeben hat.", None),
        ("Er selbst hat heute schon dreißig fremde Selfies geliked.", None),
    ], viz=dict(kind="chat", chat="💬 Lena ❤️", bar="#25A366",
                msgs=[(0, "Alex", "Wer ist der Typ, den du geliked hast?! 😡", "#E23B3B"),
                      (1, "Lena", "Du hast heute 30 Selfies geliked 💀", "#3E7BDA"),
                      (1, "Alex", "Das ist was anderes!!", "#E23B3B")],
                fx="shock", alex=("angry", "idle", "📱"))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du einen Doppelmoralisten erkennst:", None),
        ("Seine Regeln gelten nur für andere.", None),
        ("Er beschwert sich über Lärm. Und ist selbst am lautesten.", None),
        ("Er predigt Umweltschutz. Und fährt jeden Meter mit dem Auto.", None),
        ("Und sein Lieblingssatz: Das ist was anderes!", None),
    ], viz=dict(kind="signs", items=[("Regeln nur für andere", "📜"), ("Meckert über Lärm, ist laut", "🔊"),
                                     ("Predigt Umwelt, fährt Auto", "🚗"), ("„Das ist was anderes!“", "🙊")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch einen Doppelmoralisten? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch einen Doppelmoralisten?", handle="@regeln_alex", icon="⚖️", col="#3B4252")),
]
