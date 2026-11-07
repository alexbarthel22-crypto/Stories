"""TikTok-Folge: Heute ist Alex ... eine Drama Queen. Alltags-Comedy über Klischees.
Stimme exakt wie Pick-me-Boy (gemini-3.8-flash-tts, Puck, tighten 1.08 0.22, match_level). Vorschau: Ersatzstimme."""
from ep_base import *
from alexlib import alex, person_spec

AL = alex(top="#E0457B", top_style="hoodie", pants="#2F3B52", shoes="#FFFFFF")
BARISTA = person_spec(33, girl=True, top="#6B4A2E", hair="#2B1A10", skin="#C98B5E")
ROLE, ROLE_TTS, ROLE_SAY = "EINE DRAMA QUEEN.", "eine Drama Queen.", "eine Drama Queen!"
MOODS = dict(MOODS_BASE, morgen="übertrieben dramatisch, dann trocken", cafe="empört, dann trocken",
             chat="hysterisch übertrieben, dann trocken", abend="theatralisch traurig, dann trocken")
SHUFFLE = SHUFFLE_BASE
REACTIONS = {"morgen": ["🪫", "😭", "🚩"], "cafe": ["☕", "⭐", "🚩"], "chat": ["😱", "🚪", "🚩"], "abend": ["🌧️", "💔", "🚩"]}
THUMB = dict(head="HEUTE IST ALEX EINE…", l1="DRAMA", l2="QUEEN", bg="#B0306A", color1="#FFFFFF", accent="#FFE14D",
             pill="#5A1436", pill_text="#FFFFFF", expr="smug", pose="hips", prop=None, extras=True, emojis=("🎭", "😭", "👑", "🚩"))
INTRO_CFG = dict(icon="🎭", bg="#B0306A", title_lines=["DRAMA QUEEN."],
                 house=dict(sky=("#E0457B", "#FFE1EE"), walls="#FFF0F6", roof="#7A1F48", door="#5A1436", lawn="#5DAA5E",
                            accent=("#E0457B", "#8E5BE0"), sun=True),
                 left=("🎭", "BÜHNE"), right=("😭", "TRÄNEN"), door=("ACHTUNG:", "DRAMA! 🎭"),
                 neon=("DRAMA", "24/7 🎭", "#FF6FB0"), signs=("Schlimmster Tag ever 😭", "Keiner versteht mich 💔"),
                 fly=["😭", "🎭", "💔"], burst=["🎭", "😭", "💔", "👑", "🌧️", "📱", "😱", "🥀"],
                 extras=[("👑", 0, 112, 14), ("🥀", 34, 30, 14)])

SCENES = [
    dict(id="what", bg="#B0306A", clock=None, title="WAS IST EINE DRAMA QUEEN?", dark=True, lines=[
        ("Eine Drama Queen macht aus jeder Mücke einen Elefanten.", None),
        ("Ein kleines Problem? Für ihn ist das der Weltuntergang.", None),
    ], viz=dict(kind="bars", head="DRAMA-PEGEL", rows=[("DRAMA", 1.0, "100 %", "#E0457B"), ("RUHE", 0.0, "0 Min", "#555A66")],
                pills=[("🦟", "Problem: winzig", "#555A66"), ("🐘", "Reaktion: riesig", "#E0457B")])),
    dict(id="motto", bg="#2F6FA8", clock=None, title="SEIN MOTTO", dark=True, lines=[
        ("Sein Motto: Wenn schon leiden, dann vor Publikum.", None),
    ], viz=dict(kind="stage", box="#2B1A2E", head="🎭 DIE BÜHNE", head_col="#B0306A",
                items=[("🎭", 540, 650, 190, 0, "pulse"), ("🔦", 260, 600, 100, 0, "shake"), ("🔦", 820, 600, 100, 0, "shake"),
                       ("👀", 300, 860, 90, 0, "bob"), ("👀", 540, 880, 90, 0, "bob"), ("👀", 780, 860, 90, 0, "bob")],
                tags=[("PUBLIKUM: ALLE 👀", "#B0306A", 540, 760)], move="wobble", alex=("sad", "idle", None))),
    dict(id="morgen", bg="#36B5C2", clock="07:00", title="DER MORGEN", lines=[
        ("Sieben Uhr. Sein Akku ist auf neunzehn Prozent.", None),
        ("Er schreibt in seine Story: Schlimmster Tag meines Lebens.", None),
    ], viz=dict(kind="stage", box="#E8F7FF", head="📱 STORY", head_col="#2B5C66",
                items=[("🪫", 320, 680, 170, 0, "shake"), ("📱", 740, 700, 160, 1, "bob"), ("😭", 740, 860, 90, 1, "pulse")],
                tags=[("19 % 😱", "#E23B3B", 320, 860), ("„SCHLIMMSTER TAG“ 😭", "#E0457B", 600, 980)], fx="shock",
                move="rumble", flash="#FF3B3B", alex=("sad", "idle", "📱"))),
    dict(id="cafe", bg="#C0392B", clock="12:00", title="IM CAFÉ", dark=True, lines=[
        ("Mittags im Café. Sein Kaffee kommt mit Kuhmilch statt Hafermilch.", None),
        ("Er weint, will den Chef sprechen und schreibt eine Ein-Stern-Bewertung.", None),
    ], viz=dict(kind="stage", box="#FFF4E0", head="☕ CAFÉ", head_col="#6B4A2E",
                people=[(BARISTA, 780, "Barista", "neutral", 1)],
                items=[("☕", 330, 640, 130, 0, "shake"), ("🥛", 470, 640, 90, 0, "bob"), ("😭", 330, 820, 90, 1, "pulse")],
                tags=[None, ("⭐ 1 VON 5 STERNEN", "#E23B3B", 540, 980)], fx="anger", move="wobble", flash="#FF3B3B",
                bubbles=[None, "Ich will den CHEF! 😭"], alex=("angry", "idle", None))),
    dict(id="chat", bg="#5B6BC9", clock="16:00", title="GRUPPENCHAT", dark=True, lines=[
        ("Sechzehn Uhr. Tom antwortet nur mit: ok.", None),
        ("Er schreibt: Ok? Was hab ich dir getan?! Und verlässt die Gruppe.", None),
    ], viz=dict(kind="chat", chat="👥 Die Clique", bar="#25A366",
                msgs=[(0, "Tom", "ok", "#3E7BDA"),
                      (1, "Alex", "OK??? WAS HAB ICH DIR GETAN?! 😭😭", "#E0457B"),
                      (1, "System", "Alex hat die Gruppe verlassen 🚪", "#555A66")],
                fx="shock", alex=("sad", "idle", "📱"))),
    dict(id="abend", bg="#8E5BE0", clock="21:00", title="DER POST", dark=True, lines=[
        ("Abends postet er ein trauriges Selfie mit Regen-Filter.", None),
        ("Darunter: Manche Menschen ändern sich halt. Keiner weiß, wer gemeint ist.", None),
    ], viz=dict(kind="stage", box="#3B3F58", head="📸 NEUER POST", head_col="#7A3FA8",
                items=[("🌧️", 300, 600, 130, 0, "bob"), ("🌧️", 780, 600, 130, 0, "bob"), ("📸", 540, 700, 150, 0, "pulse"),
                       ("💔", 760, 860, 90, 1, "pulse"), ("🤷", 320, 860, 90, 1, "shake")],
                tags=[("REGEN-FILTER 🌧️", "#555A66", 540, 560), ("WER IST GEMEINT?! 🤷", "#E0457B", 540, 980)],
                fx="shock", move="wobble", alex=("sad", "idle", None))),
    dict(id="signs", bg="#D9534F", clock=None, title="DIE 4 ANZEICHEN", lines=[
        ("Woran du eine Drama Queen erkennst:", None),
        ("Weltuntergang bei neunzehn Prozent Akku.", None),
        ("Für jedes Problem gibt's eine Story.", None),
        ("Er verlässt Gruppen dramatisch.", None),
        ("Und er postet traurige Selfies mit Regen-Filter.", None),
    ], viz=dict(kind="signs", items=[("Weltuntergang bei 19 %", "🪫"), ("Story für jedes Problem", "📱"),
                                     ("Verlässt Gruppen dramatisch", "🚪"), ("Selfies mit Regen-Filter", "🌧️")])),
    dict(id="outro", bg="#7B4FA8", clock=None, title=None, lines=[
        ("Kennst du auch eine Drama Queen? Markier sie oder ihn!", None),
        ("Und was soll Alex morgen sein? Schreib's in die Kommentare.", None),
    ], viz=dict(kind="outro", q="Kennst du auch eine Drama Queen?", handle="@drama_alex", icon="🎭", col="#B0306A")),
]
