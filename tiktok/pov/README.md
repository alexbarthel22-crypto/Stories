# POV-Stories im Comic-Stil

Mit diesem Werkzeug machst du Hochformat-Videos (1080×1920) aus der Ego-Perspektive:
- **Fischauge:** Die Kamera hat ein extremes Fischauge und dreht sich wie ein Kopf, der sich umschaut.
- **Comic-Look:** 3D-Szenen mit flachen Farben und dicken schwarzen Umrissen.
- **Ego-Körper:** Unten im Bild sind die eigenen Arme, Hände und das Handy zu sehen.
- **Figuren:** große runde Augen und Mundbewegung passend zur Stimme.
- **Einblendungen:** Ort und Uhrzeit oben links, Untertitel und Benachrichtigungen.

Du schreibst nur eine **Story-Datei (JSON)**. Den Rest erledigen die Skripte:
Stimmen erzeugen, Timing berechnen, Lippensynchronisation, Ton mischen und das Video rendern.

## Schnellstart

```bash
cd tiktok/pov
npm install                                   # einmalig (lädt three.js)
python3 tools/prep.py stories/beispiel.json   # Stimmen + Timing + Ton
node tools/render.js beispiel --bilder 1,5,10 # 3 Standbilder zur Kontrolle
node tools/render.js beispiel --entwurf       # schnelles Entwurfsvideo (halbe Auflösung)
node tools/render.js beispiel                 # finales Video -> build/beispiel/beispiel.mp4
```

Voraussetzungen: Node, Python 3 mit numpy, ffmpeg, Playwright mit Chromium.
Für die Stimmen brauchst du `GEMINI_API_KEY` (wie bei den FC-Schlammloch-Folgen).
ElevenLabs geht auch, siehe unten.
`python3 tools/prep.py … --ohne-stimmen` arbeitet ohne Stimmen und schätzt das Timing nur.

Das Rendern dauert hier in der Cloud ohne Grafikkarte etwa 1–2 Sekunden pro Frame,
also etwa 10–20 Minuten für 20 Sekunden Video. Auf einem Rechner mit Grafikkarte geht es viel schneller.

## Eine Story schreiben

Lege eine Datei `stories/<name>.json` an. Am einfachsten kopierst du `stories/beispiel.json`.

```json
{
  "set": "aussicht",
  "himmel": "abend",
  "fov": 140,
  "blick": "stadt",
  "cast": {
    "ich": { "pos": [0, -1.5], "pose": "aufstuetzen", "oberteil": "#4f7a3a", "stimme": "gemini:Fenrir" },
    "mia": { "pos": [-1.6, -1.95], "stimme": "gemini:Leda", "frisur": "bob", "haare": "#b98a4e",
             "oberteil": "#8b2525", "hose": "#1e2433", "brille": true }
  },
  "beats": [
    { "ort": ["LICHTENBERG-HÖHE", "Aussichtspunkt · Freitag, 18:12"], "blick": "stadt", "dauer": 2.5 },
    { "blick": "mia", "wer": "mia", "sagt": "Ich muss dir was sagen.", "wie": "zögernd, ernst" },
    { "wer": "ich", "sagt": "Jetzt? Hier oben?", "ort": null }
  ]
}
```

Eine Story besteht aus **Beats**, die nacheinander ablaufen. Ein Beat dauert so lange wie sein Satz
plus eine kurze Pause. Ohne Satz dauert er `dauer` Sekunden.

### Felder eines Beats

| Feld | Bedeutung | Beispiel |
|---|---|---|
| `wer` + `sagt` | Wer spricht was. Erzeugt Stimme, Untertitel und Mundbewegung. | `"wer": "mia", "sagt": "Hör auf."` |
| `wie` | Sprechweise für die Stimme | `"wie": "flüsternd, ängstlich"` |
| `dauer` | Mindestdauer des Beats in Sekunden | `2.5` |
| `pause` / `pause_vor` | Pause nach bzw. vor dem Satz | `0.6` |
| `blick` | Wohin die Kamera schaut: Figur, benannter Punkt oder `[Grad links/rechts, Grad hoch/runter]` | `"mia"`, `"stadt"`, `[0, -30]` |
| `drehung` | Wie lange die Kopfdrehung dauert (s) | `1.2` |
| `schnitt` | Harter Schnitt statt Drehung | `true` |
| `pose` | Körperhaltung pro Figur (siehe Liste) | `{"mia": "zeigen", "ich": "handy"}` |
| `stimmung` | Augenbrauen: `angst`, `wuetend` oder `null` | `{"mia": "angst"}` |
| `schaut` | Wohin eine Figur sich dreht (Standard: zu dir) | `{"mia": "skyline"}` |
| `laufen` | Figur läuft zu Position `[x, z]` (in Metern) | `{"ich": [0, 4], "mia": [2, 3]}` |
| `handy` | Bildschirminhalt des Handys | siehe unten |
| `ort` | Ort/Zeit oben links, `null` blendet aus | `["BERLIN", "Kreuzberg · 23:40"]` |
| `meldung` | Benachrichtigungskarte oben | `{"titel": "Mama", "text": "Anruf fehlgeschlagen", "icon": "📞", "dauer": 3}` |
| `text` | Freier Untertitel ohne Stimme (z. B. Geräusch) | `"text": "*Explosion*"` |
| `blende` | Schwarzblende (Dauer in s) | `0.8` |
| `sfx` | Geräusch aus `sfx/` abspielen (auch Liste) | `"ping.wav"` oder `{"datei": "sirene_fern.wav", "ab": 0.3, "lautstaerke": 0.5, "dauer": 4}` |
| `telefon` | Satz klingt wie durchs Handy | `true` |
| `atmo` | Lautstärke einer Atmo-Spur ab diesem Beat ändern (weich) | `{"voegel.wav": 0, "atmo_stadt.wav": 0.05}` |
| `musik` | Musik ab diesem Beat (Kreuzblende), `null` = aus | `{"datei": "gen/musik_2_spannung.mp3", "lautstaerke": 0.24, "einblenden": 2}` |
| `zoom` | Fischauge enger/weiter stellen (Grad), `0` = zurück | `"zoom": 78, "zoom_dauer": 1.4, "zoom_ab": 0.5` |
| `schuetteln` | Kamera erschüttern (Stärke) | `0.6` |
| `schwarz` | Schwarzbild für diesen Beat (z. B. Abspann mit `text`) | `true` |
| `effekt` | Spezialeffekte des Sets, z. B. Stromausfall in Wellen (Dauer s) | `{"stromausfall": 3.5}` |

**Handy-Bildschirme** (`"handy": {...}`; damit es sichtbar ist, braucht „ich“ die Pose `handy`):
- `{"typ": "anruf", "name": "Mama", "status": "Anruf wird aufgebaut"}`: ausgehender Anruf
- `{"typ": "eingehend", "name": "Lukas"}`: eingehender Anruf
- `{"typ": "alarm", "titel": "NOTFALL-\nALARM", "text": "Sofort Schutz suchen."}`
- `{"typ": "nachricht", "name": "Unbekannt", "text": ["Hallo?", "> Wer ist da?"]}`: Zeilen mit `>` sind eigene Nachrichten
- `null` oder `{"typ": "aus"}`

### Posen

- **Ich (Ego-Arme):** `runter`, `aufstuetzen`, `vor`, `zeigen`, `handy`, `handy_beide`, `abwehr`
- **Andere Figuren:** `idle`, `erklaeren`, `zeigen`, `winken`, `achselzucken`, `arme_verschraenkt`, `handy`, `aufstuetzen`, `haende_hoch`

### Figuren gestalten (`cast`)

| Feld | Werte |
|---|---|
| `pos` | Startposition `[x, z]` in Metern |
| `frisur` | `bob`, `kurz`, `lang`, `zopf`, `none` |
| `haare`, `haut`, `oberteil`, `hose`, `schuhe`, `augen` | Farben als `#rrggbb` |
| `brille` | `true` / `false` |
| `stimme` | `gemini:<Name>` (z. B. Leda, Fenrir, Puck, Kore, Charon, Aoede) oder `elevenlabs:<Name>` |
| `regie` | Standard-Sprechweise der Figur |
| `farbe` | Untertitelfarbe (Standard: Gelb für andere, Weiß für „ich“) |
| `tempo` | Sprechtempo, z. B. `1.15` |
| `mantel` | langer Mantel (`true`) |
| `details` | `none` = keine schwarzen Knopf-Striche auf dem Oberteil |

### Story-Einstellungen

| Feld | Bedeutung |
|---|---|
| `set` | Kulisse, aktuell `aussicht` (Aussichtspunkt über einer Großstadt plus Straße mit Reihenhäusern) |
| `himmel` | `abend` (Sonnenuntergang), `tag`, `daemmerung` |
| `fov` | Fischauge-Stärke in Grad (130 = weniger, 155 = extrem) |
| `blick` | Blickrichtung beim Start |
| `wackeln` | Handkamera-Wackeln (0 = aus, 1 = normal, 2 = stark) |
| `ort_klein` | `true` = kleine Ortsangabe (Stil „16:49 / VILLA · SALON“) |
| `untertitel_y` | Höhe der Untertitel (0 = oben, 1 = unten; Standard 0.6) |
| `atmo_spuren` | Durchlaufende Umgebungsgeräusche | `[{"datei": "atmo_wind.wav", "lautstaerke": 0.3}, …]` |
| `max_pause` | Lange Sprechpausen in Sätzen werden auf diesen Wert gekürzt (s, Standard 0.45) |
| `ducking` | Wie stark die Musik unter Sprache leiser wird (0–1, Standard 0.6) |
| `stimme_lautstaerke` | Gesamtlautstärke der Stimmen |

### Benannte Blickpunkte im Set `aussicht`

`stadt`, `skyline`, `abhang`, `strasse`, `haeuser`, `links`, `rechts`, `boden`, `himmel`.
Eigene Punkte legst du in der Story an: `"spots": {"auto": [150, -10]}`.

Koordinaten: Die Mauer zur Stadt liegt bei z = −2.35. Die Straße verläuft parallel bei z = 3.6…11,
die Reihenhäuser stehen ab z = 14. Die x-Achse läuft entlang der Mauer.

## Wie der Stil entsteht (zum Anpassen)

| Datei | Inhalt |
|---|---|
| `engine/toon.js` | Cel-Shading mit 3 Farbstufen, Tusche-Umrisse (Linienstärke `uW`), handgemalte Texturen (Flecken, Risse, Laub) |
| `engine/fisheye.js` | Fischauge über Cubemap: zuerst wird die Welt in alle Richtungen gerendert, dann verzerrt |
| `engine/sky.js` | Himmelsfarben, Wolken, Sonne und Licht pro Stimmung |
| `engine/chars.js` | Figuren, Posen, Augen- und Mundtexturen |
| `engine/pov.js` | eigene Arme, Hände, Beine und Handy |
| `engine/overlay.js` + `engine/index.html` | Untertitel, Ortsangabe und Meldungen (Schrift, Farben, Position) |
| `engine/sets/aussicht.js` | die Kulisse |

Für ein neues Set (z. B. Wohnung, Auto, Straße) kopierst du `sets/aussicht.js`,
baust die Kulisse aus Boxen, Zylindern und Texturen und trägst sie in `sets/index.js` ein.

Tipps für den Look des Originals:
- Figuren 1–2 m vor die Kamera stellen.
- Oft zwischen Gesicht, Umgebung und Handy hin- und herschauen.
- Kurze Sätze schreiben und wichtige Momente mit einer `meldung` oder einem Handy-Bildschirm zeigen.

## Ton: Geräusche, Atmo, Musik

`python3 tools/sfx_synth.py` erzeugt die Geräuschbibliothek in `sfx/`. Alles ist per Synthese erzeugt
und deshalb frei verwendbar:

| Datei | Inhalt |
|---|---|
| `atmo_wind.wav`, `atmo_stadt.wav`, `voegel.wav` | nahtlose Schleifen für `atmo_spuren` |
| `auto_vorbei.wav` | Auto fährt vorbei (Doppler, links → rechts) |
| `vibration.wav`, `klingelton.wav`, `anruf_ende.wav`, `ping.wav` | Handy |
| `sirene_fern.wav` | Martinshorn in der Ferne |
| `hubschrauber_fern.wav` | Hubschrauber in der Ferne |
| `stromausfall.wav` | dumpfer Schlag + absackendes Brummen |
| `herzschlag.wav`, `riser.wav`, `drone.wav` | Spannung |

Musik liegt in `sfx/gen/` (mit Lyria erzeugt, über `../audio/lyria.py "<Prompt>" <datei.mp3>`).
Die Musik wird unter Sprache automatisch leiser (Ducking).

Stimmen werden aufbereitet (Low-Cut, sanfter Kompressor). Lange Pausen werden gekürzt.
Erzeugt Gemini einen Satz falsch, erzeugst du ihn gezielt neu:
`python3 tools/prep.py stories/<name>.json --neu "Anfang des Satzes"`.
Tipp: Uhrzeiten als „achtzehn Uhr dreißig“ schreiben. Bei „halb sieben“ hat Gemini mehrfach „halb acht“ gesprochen.

## Stories

- `stories/beispiel.json`: kurzer Test (20 s)
- `stories/jens_1830.json`: **„Jens – 18:30“** (ca. 92 s). Jens trifft am Aussichtspunkt einen Fremden im grauen Mantel.
  Der sagt voraus, dass um halb sieben die Lichter ausgehen. Dann folgen ein abgebrochener Anruf seines Bruders Tobi
  und eine Nachricht von „Unbekannt“. Um 18:30 erlischt die ganze Stadt, und Tobi steht plötzlich hinter Jens.
- `stories/jens_1830_teil2.json`: **„Jens – 18:30 · Teil 2“** (ca. 77 s, Set `gasse`). Flucht im Gewitterregen in die Färbergasse.
  Tobi trägt ein Funkgerät und verrät Jens. Agenten mit Taschenlampen kommen, ein Hubschrauber kreist, ein Transporter versperrt die Einfahrt,
  eine Katze erschreckt ihn. Eine grüne Tür knarrt auf. Im Hinterzimmer mit Kerzen und Pinnwand steht sein totgeglaubter Vater. Dann hämmert es an der Tür.
- `stories/jens_1830_teil3.json`: **„Jens – 18:30 · Teil 3“** (ca. 91 s, Set `ubahn`). Flucht durch eine Falltür in den stillgelegten U-Bahnhof Färberplatz.
  Der Vater erzählt vom Umspannwerk. Ratten huschen vorbei, und trotz „Kein Netz“ kommt eine Nachricht. Doch der Vater hat gar kein Handy.
  Die Verfolger kommen die Leiter herunter, ein Geisterzug fährt ein. In der Tür steht der Fremde aus Teil 1 mit dem Handy: „Steig ein, Jens.“
- `stories/jens_1830_teil4.json`: **„Jens – 18:30 · Teil 4“** (ca. 80 s, Set `zug`). Jens fährt mit, der Vater rennt schreiend am Bahnsteig mit.
  Der Fremde heißt Martin Krause und sagt: Hinter dem Stromausfall steckt der Vater. Er zeigt ein Überwachungsvideo aus dem Umspannwerk.
  Dann kommen die Notbremse, Schläge aufs Dach und eine Nachricht von Tobi („ER = dein Vater“), und der Vater steht im nächsten Wagen.
- `stories/jens_1830_teil5.json`: **„Jens – 18:30 · Teil 5“** (ca. 82 s, Set `umspannwerk`). Jens geht mit dem Vater ins Umspannwerk Nord.
  Der Vater sagt, Krause wolle um Mitternacht das ganze Netz übernehmen. Zwei Schlüssel müssen gleichzeitig gedreht werden.
  Krause kommt mit seinen Leuten, es folgen Countdown, Knall und das Licht der Stadt. Dann sagt Krause: „Danke, Jens. Genau das wollte ich.“
- `stories/jens_1830_teil6.json`: **„Jens – 18:30 · Teil 6 (Finale)“** (ca. 91 s, Set `leitwarte`). Die Schlüssel haben Krauses Programm freigeschaltet.
  Jens schleicht in die Leitwarte. Tobi lenkt Krause am Fenster ab, Jens schlägt den NOT-AUS ein, und alles fährt herunter.
  Die Polizei kommt, Krause wird abgeführt. Am Morgen versöhnen sich Jens, Tobi und der Vater. Mama schreibt: Frühstück ist fertig. ENDE.
- `stories/mutprobe_1.json`: **„Die Mutprobe · Teil 1“** (ca. 90 s, Set `schule`, neue Serie für Jugendliche). Mia und Ben machen nachts einen Livestream in der Schule.
  Die Bewegungsmelder gehen von allein an, die Kamera folgt ihnen, Spind 47 mit Mias durchgestrichenem Foto öffnet sich. Um Mitternacht schrillt die Schulglocke, Ben verschwindet, der Lautsprecher flüstert.
  Im Bio-Raum schreibt sich die Kreide von selbst, das Skelett dreht den Kopf. Ben schreibt, er stehe draußen am Tor. Doch „Ben“ steht in der Tür, mit schwarzen Augen.
- `stories/mutprobe_2.json`: **„Die Mutprobe · Teil 2“** (ca. 89 s, Set `turnhalle`). Mia flieht in die Turnhalle und telefoniert mit dem echten Ben.
  Die Strahler gehen an, die Anzeigetafel zeigt „MIA IST DRAN“, ein Basketball springt heran. Auf der Tribüne nimmt „Ben“ die Maske ab: Es ist Noah,
  den die Clique letztes Jahr bei einer Mutprobe im Geräteraum eingesperrt hat. Das Rolltor geht auf, der echte Ben stürmt herein. Am Ende steht auf der Tafel: „MONTAG 1. STUNDE: BEN“.
- `stories/mutprobe_3.json`: **„Die Mutprobe · Teil 3“** (ca. 77 s, Set `klassenzimmer`, Tageslicht). Montag, 1. Stunde: Noah kommt als neuer Mitschüler.
  Das Smartboard startet das Video von damals, alle Handys vibrieren, ein Countdown läuft. Mia ruft „STOPP!“ und gesteht vor der Klasse. Ben gibt zu, dass die Idee von ihm war.
  Noah: „Mehr wollte ich nie hören.“ Dann schreibt der Schulgeist: „Aber Noah war nie der Schulgeist.“

## Neu: Felder für mehr Spannung und Details

| Feld (Beat) | Wirkung |
|---|---|
| `handy: {typ:"nachricht", text:[…], nach_und_nach: 1.2, neu_ab: 2}` | Nachrichten erscheinen nacheinander (mit „schreibt …“); `neu_ab` = so viele sind schon da |
| `handy: {…, tippen: "Wer bist du?"}` | Tastatur + Text wird Buchstabe für Buchstabe getippt (`sfx: tippen.wav`) |
| `handy: {…, uhr: "18:27"}` | Uhrzeit auf dem Handy |
| `ende: true` / `"Text"`, `ende_unter` | große Abspann-Karte („FORTSETZUNG FOLGT“), bleibt bis zum Schluss (mit `schwarz: true`) |
| `auto: {spur: 1\|2, ab, farbe, tempo}` | Auto fährt zur Zeit `ab` am Spieler vorbei, Geräusch wird automatisch passend gelegt |
| `effekt: {flackern: s}` | Laternen flackern (`sfx: summen.wav`) |
| `effekt: {hubschrauber: {ab, dauer, von:[x,y,z], nach:[x,y,z]}}` | Hubschrauber mit Suchscheinwerfer |
| `laufen: {"name": {nach:[x,z], zeit, ab}}` | eigene Laufzeit/Startzeit pro Figur (`zeit: 0.01` = teleportieren) |
| `hintergrund: [{wer, sagt, wie, ab, lautstaerke, funk}]` | Sätze nebenbei (ohne Untertitel, ohne Einfluss aufs Timing); `funk: true` = Funkgerät |
| `funk: true` (Satz) | Stimme klingt wie Funkgerät |

Cast-Optionen: `typ: "transporter"` (Fahrzeug, fährt über `laufen`), `taschenlampe: true` (sichtbar in Pose `leuchten`),
`handy_bild` (was auf dem Handy einer Figur zu sehen ist), `schaut` (Startblick). Neue Posen: `leuchten`, `rennen`, `haende_tasche`;
POV: `rennen`. Story: `nacht` (wie dunkel es nach dem Stromausfall wird), `handy_fov` (Zoom beim Blick aufs Handy, Standard 96).
Beim Blick aufs Handy zoomt das Bild automatisch heran; die Hand hält das Gerät von hinten, der Bildschirm bleibt frei.

Neue Geräusche: `tippen, gesendet, stich, braam, summen, jogger, transporter, tueren, glocke, rennen, atem_schwer,
atmo_laub, zug_fern, funk_knacken, hund_fern` · Musik: `gen/musik_4_flucht.mp3`, `gen/musik_5_lauern.mp3`.
In der Szene laufen automatisch: Vogelschwarm, Herbstlaub im Wind, Flugzeug mit Blinklicht, Fensterlichter, die beim Stromausfall ausgehen.

## Set `gasse` (Teil 2): Altstadtgasse bei Nacht, Gewitter und Regen

Himmel `"himmel": "nacht"`. Die Gasse läuft entlang Z, die Einfahrt liegt bei z ≈ +14, das Ende bei z ≈ −30. Die grüne Tür ist rechts (x = 2.6, z −2.2 … −1.0), dahinter das Hinterzimmer (x 2.9 … 8.2).
Blickpunkte: `gasse, ende, einfahrt, tuer, links, rechts, tonnen, himmel, fenster, boden, zimmer, pinnwand`.

Automatisch zu sehen:
- Regenstreifen und Spritzer in den Pfützen, Wasser aus den Fallrohren, Dampf aus dem Gully
- schaukelnde Wäsche und ein schwingendes „Café Mond“-Schild
- flackernde Kerzenfenster mit Spiegelung auf dem nassen Pflaster, eine Nachbarin als Silhouette im Fenster
- tote Lichterkette, Graffiti, Plakate, Fahrrad, Mülltonnen mit Katze, Flaschenkiste
- Auto mit Warnblinker an der Einfahrt
- im Zimmer: Pinnwand mit Fotos und roten Fäden, Kerzen, eine Uhr mit laufendem Sekundenzeiger, Bücherregal, Radio

| Feld | Wirkung |
|---|---|
| `effekt: {blitz: s \| [s, …]}` | Blitz: Himmel und Szene leuchten auf, Blitz am Himmel (`sfx: donner_nah.wav`) |
| `effekt: {katze: s}` | Katze springt von der Tonne, Deckel klappert (`sfx: tonne_katze.wav`) |
| `effekt: {tuer_auf: s}`, `effekt: {tuer_zu: s}` | grüne Tür knarrt auf (`knarren.wav`) bzw. knallt zu (`tuer_knall.wav`) |
| `hall: 0.7` (Beat, Satz oder Story) | Raumhall auf der Stimme (Nachhallzeit in s) |
| `gedaempft: true` (Satz/Hintergrund) | Stimme klingt wie durch eine Tür |
| `handy: {…, tropfen: true}` | Regentropfen auf dem Display |

Cast: `funkgeraet: true` (Funkgerät an der Brust, rote LED blinkt bei Funksprüchen), `kerze: true` (Pose `kerze`, Kerze wirft warmes Licht aufs Gesicht),
`schirm: "#farbe"` (Regenschirm, Pose `schirm`). Neue Posen: `funken`, `kerze`, `schirm`, `flehen`.

Neue Geräusche:
- Atmo: `atmo_regen`, `atmo_tropfen` (Tropfen und Regenrinne), `atmo_drinnen` (gedämpfter Regen im Raum)
- Effekte: `donner_nah, donner_fern, rennen_nass, stiefel_nass, tonne_katze, knarren, tuer_knall, klopfen, ticken, heli_nah, autoalarm_fern`
- erzeugen: `python3 tools/sfx_synth.py teil2`

Musik: `gen/musik_6_regen.mp3` (kalt, pulsierend) und `gen/musik_7_enthuellung.mp3` (Spieluhr, Streicher).
Thumbnail: `node tools/thumbnail.js <name> --bei <s> --titel "Zeile|*gelb*|Zeile" --unter "TEIL 2"`.

## Set `ubahn` (Teil 3): stillgelegter U-Bahnhof, nur Notbeleuchtung

Der Bahnsteig liegt bei x −4.5 … 1.6, das Gleis bei x ≈ 3.75 (eine Stufe tiefer). Der Bahnsteig reicht von z = +32 (Wartungsleiter und Schacht) bis z = −45 (Tunnel). Die Säulen stehen bei x = −1.
Blickpunkte: `bahnsteig, tunnel, leiter, schacht, gleis, wand, schild, uhr, boden, zug, decke`.

Automatisch zu sehen:
- Fliesen mit Schmutzspuren, Stahlsäulen mit Nieten, rote Notlampen (echtes Licht), eine Neonröhre, die immer wieder aufzuckt
- Notausgang-Schild, Bahnhofsuhr (steht auf 18:30), Bahnhofsschilder, Plakate von 1978–81, Liniennetz, Kiosk, Fahrkartenautomat, Bänke
- Zeitungen am Boden, Spinnweben, lose Kabel
- Tropfen von der Decke mit Ringen in Pfützen, Staub in der Luft, Ratten an der Wand
- Signal am Tunnel (springt auf Grün, wenn der Zug kommt)

| Feld | Wirkung |
|---|---|
| `effekt: {zug: {ab, dauer, von, nach}}` | Zug (2 Wagen, beleuchtet, Scheinwerfer) fährt ein; `von`/`nach` = z der Zugmitte. Mitfahrende Figur: `faehrt: true` und `laufen` mit gleicher Zeit (z + 4.5 = Tür) |
| `effekt: {zug_tueren: s}` | Türen gleiten auf (`zug_tueren.wav`) |
| `effekt: {ratten: s}` | Rattenrudel huscht über den Bahnsteig (`ratten.wav`) |
| `effekt: {flackern: s}` | Notlicht, Neonröhre und Zuglicht flackern |
| `effekt: {luke: s}` | Luke oben im Schacht geht auf, Licht fällt herein (`falltuer.wav`) |
| `handy: {…, netz: "Kein Netz"}` | Text oben rechts in der Statusleiste |

Cast: `licht: true` (Taschenlampe ist eine echte Lichtquelle), `faehrt: true` (Figur fährt mit, ohne Laufanimation).

Neue Geräusche:
- Atmo: `atmo_tunnel, atmo_tropfen_hall, neon_summen`
- Effekte: `tuer_aufbrechen, leiter, falltuer, schritte_hall, rennen_hall, ratten, hund_hall, zug_kommt, zug_tueren`
- erzeugen: `python3 tools/sfx_synth.py teil3`

Musik: `gen/musik_8_tunnel.mp3`, `gen/musik_9_zug.mp3`.

## Set `zug` (Teil 4): im fahrenden Geisterzug

Der Wagen steht still (x −1.35 … 1.35, z −7.5 … 7.5), die Welt draußen zieht vorbei: am Anfang der Bahnsteig auf der +X-Seite, danach Tunnel und Lampen.
Blickpunkte: `gegenueber, tuer, fenster, vorne, hinten, decke, boden, durchgang, plan`.

Automatisch zu sehen:
- Sitzbänke, Haltestangen, schaukelnde Griffe, Liniennetz „Linie 0“ bis zum Umspannwerk Nord, alte Werbung, Kratzer in den Scheiben, Notbremse
- eine Zeitung („Ingenieur tot – Unfall im Werk?“) und eine Flasche, die beim Anfahren und Bremsen rollt
- Tunnellampen, deren Licht durch den Wagen wandert
- dahinter der nächste Wagen mit rotem Notlicht

| Feld | Wirkung |
|---|---|
| `effekt: {fahrt: {ab, v, dauer}}` | Geschwindigkeit v (m/s) ansteuern; `v: 0` = bremsen (`zug_anfahrt.wav`, `notbremse.wav`) |
| `effekt: {licht_aus: s}` | Hauptlicht aus, rotes Notlicht |
| `effekt: {dach: [s, …]}` | Schläge aufs Dach, Delle in der Decke wächst (`dach_schlag.wav`) |
| `effekt: {durchgang: s}` | Verbindungstür nach vorne gleitet auf |
| `effekt: {flackern: s}` | Licht flackert |
| `handy: {typ: "video", name, text, laenge}` | Überwachungsvideo spielt auf dem Handy ab |

Cast: Pose `sitzen`, `gegenlauf: true` (die Figur schaut entgegen ihrer Bewegung, z. B. wenn sie neben dem Zug herrennt).
Neue Geräusche: `atmo_zug_innen, zug_anfahrt, notbremse, dach_schlag, schaben` (`python3 tools/sfx_synth.py teil4`). Musik: `gen/musik_10_fahrt.mp3`, `gen/musik_11_dach.mp3`.

## Set `umspannwerk` (Teil 5): Umspannwerk Nord bei Nacht

Der Weg verläuft entlang Z: das Tor bei z = +20, die Leitwarte bei z = −25. Der Schaltschrank mit Schlüssel A/B steht bei x = 2.2, z = −8. Die Stadt liegt links (−X) hinter dem Zaun.
Blickpunkte: `weg, warte, tor, stadt, schrank, trafo, himmel, links, rechts, boden`.

Automatisch zu sehen:
- Transformatoren mit Kühlrippen, Isolatoren und Typenschild, Stahlportale mit durchhängenden Leitungen, ferne Strommasten
- Zaun mit Stacheldraht und Warnschildern, Flutlichtmasten mit Motten, Bodennebel, Pfützen
- Leitwarte mit Bildschirmen (Netz Nord/Süd/Wasser/Kliniken), ab und zu ein Funkenüberschlag

| Feld | Wirkung |
|---|---|
| `effekt: {countdown: s}` | Countdown im Schaltschrank und in der Leitwarte springt auf s und zählt herunter |
| `effekt: {funken: s}` | Überschlag an einem Isolator (`funken.wav`) |
| `effekt: {flutlicht: s}` | alle Flutlichter an, das Tor schwingt auf (`flutlicht.wav`, `tor.wav`) |
| `effekt: {schluessel: s}` | beide Schlüssel drehen sich, Anzeige: GELÖSCHT (`schluessel.wav`) |
| `effekt: {knall: s}` | riesiger Überschlag: Blitz, Funkenregen, alles dunkel (`knall.wav`) |
| `effekt: {licht_an: s}` | die Stadt leuchtet wellenartig wieder auf (`stadt_an.wav`) |

Neue Geräusche: `atmo_brummen, schritte_kies, funken, tor, flutlicht, schluessel, knall, stadt_an` (`python3 tools/sfx_synth.py teil5`). Musik: `gen/musik_12_werk.mp3`, `gen/musik_13_finale.mp3`.

## Set `leitwarte` (Finale): Leitwarte des Umspannwerks

Der Raum reicht von x −8 … 8 und z −6 … 6. Vorne (−Z) liegt das Panoramafenster zum Hof, links die Netz-Schalttafel, rechts die Tür (z = 3.5) und die Serverschränke, hinten der NOT-AUS (x = −4).
Blickpunkte: `fenster, pult, tafel, tuer, notaus, server, decke, boden, stadt`.

Automatisch zu sehen:
- Schalttafel mit dem Stadtnetz (Linien werden mit der Übernahme rot), Hauptpult mit Fortschrittsbalken und Code
- Röhrenmonitore, Bürostühle, Tassen, rotes Telefon, Wanduhr mit laufendem Sekundenzeiger
- Serverschränke mit blinkenden LEDs, Feuerlöscher, Notausgang-Schild
- draußen der Hof mit Flutlicht, Trafos und Zaun, dahinter die beleuchtete Stadt

| Feld | Wirkung |
|---|---|
| `effekt: {uebernahme: {ab, von, bis, dauer}}` | Übernahme-Fortschritt (%) auf Pult und Schalttafel |
| `effekt: {notaus: s}` | Glas splittert, alles fährt herunter, rotes Notlicht (`glas_splitter.wav`, `notaus_aus.wav`) |
| `effekt: {polizei: s}` | Streifenwagen im Hof, Blaulicht flackert durch das Fenster (`sirenen_nah.wav`) |
| `effekt: {morgen: {ab, dauer}}` | Sonnenaufgang: Himmel und Raum werden hell, Tafel zeigt „NETZ STABIL“ |

Neue Geräusche: `tastatur, atmo_luefter, fenster_klopfen, glas_splitter, notaus_aus, sirenen_nah` (`python3 tools/sfx_synth.py teil6`). Musik: `gen/musik_14_warte.mp3`, `gen/musik_15_morgen.mp3`.

## Set `schule` (Die Mutprobe): Schulflur bei Nacht + Bio-Raum

Der Flur reicht von x −2.2 … 2.2 und z +10 … −22. Links stehen die Spinde (Spind 47 bei z ≈ −2.25), rechts die Fenster (Mondlicht), die Tür 10b (z = 5) und der Bio-Raum (Tür z = −16, Raum x 2.2 … 9).
Blickpunkte: `gang, zurueck, spinde, fenster, kamera, decke, boden, biotuer, tafel, skelett, aquarium, uhr`.

Automatisch zu sehen:
- Spinde mit Aufklebern, Schwarzes Brett mit Flyern, Pokalvitrine, Kinderbilder, Trinkbrunnen, Feuerlöscher
- Wanduhr (23:57 →), Notausgang, Banner, Schulhof mit Bäumen und Turnhalle vor den Fenstern
- im Bio-Raum: Tafel mit Mitose-Notizen, Poster, Mikroskope, Skelett, Aquarium mit Fischen und Blasen

| Feld | Wirkung |
|---|---|
| `effekt: {lichter: {ab, von, nach, tempo}}` | Bewegungsmelder: Deckenlampen gehen von z `von` bis `nach` nacheinander an (`bewegungsmelder.wav`) |
| `effekt: {dunkel: s}` | alle Lichter aus |
| `effekt: {kamera: s}` | Überwachungskamera folgt dem Spieler, rote LED (`kamera_servo.wav`) |
| `effekt: {spind: s}` | Spind 47 schwingt auf, darin ein Foto (`spind_knarren.wav`) |
| `effekt: {klingel: s}` | Schulglocke (`schulglocke.wav`) |
| `effekt: {kreide: {ab, dauer, text}}` | Text schreibt sich an die Tafel (`kreide.wav`) |
| `effekt: {skelett: s}` | Skelett dreht den Kopf, hebt den Arm (`knochen.wav`) |
| `handy: {typ: "live", name, zuschauer: [von, bis], kommentare: [[user, text], …], tempo, schon, figur, szene}` | Livestream mit Zuschauerzahl, Kommentaren und Herzen |

Cast: `augen: "leer"` (komplett schwarze Augen). Neue Geräusche: `atmo_schule, bewegungsmelder, kamera_servo, spind_knarren, schulglocke, lautsprecher_knacken, kreide, knochen`
(`python3 tools/sfx_synth.py mutprobe`). Musik: `gen/musik_16_schule.mp3`, `gen/musik_17_flucht.mp3`.

## Set `turnhalle` (Die Mutprobe 2): Schulturnhalle bei Nacht

Die Halle reicht von x −12 … 12 und z −18 … 18. Der Eingang liegt bei z = +18, die Tribüne links (Stufen y 0.6/1.2/1.8/2.4 bei x −8.45/−9.35/−10.25/−11.15).
Rechts sind Sprossenwand, Geräteraum (Rolltor z −6 … −2) und Notausgang mit Kette, vorne Anzeigetafel und Korb.
Blickpunkte: `halle, tribuene, anzeige, korb, geraeteraum, eingang, decke, boden, seile`.

| Feld | Wirkung |
|---|---|
| `effekt: {strahler: {ab, tempo}}` | Hallenstrahler Reihe für Reihe an (`strahler.wav`) |
| `effekt: {dunkel: s}`, `effekt: {blitz: s}` | alles aus / kurzes Flackern |
| `effekt: {anzeige: {ab, text, rot}}` (auch Liste) | LED-Anzeigetafel, lange Texte laufen durch (`anzeige_piep.wav`) |
| `effekt: {ball: s}` | Basketball springt aus dem Dunkeln heran (`basketball.wav`) |
| `effekt: {rolltor: s}` | Rolltor des Geräteraums fährt hoch (`rolltor.wav`) |
| `hoehe: {name: y}` (Beat) / `y` (Cast) | Figur steht erhöht, z. B. auf der Tribüne |

Musik: `gen/musik_18_halle.mp3`, `gen/musik_19_reue.mp3`. Geräusche erzeugen: `python3 tools/sfx_synth.py mutprobe2`.

## Set `klassenzimmer` (Die Mutprobe 3): Klasse 10b am Morgen

Der Raum reicht von x −5 … 5 und z −6 … 6. Vorne stehen Smartboard und Lehrerpult, links ist die Fensterfront mit Sonne, rechts die Tür (z −4.5).
Tische stehen in den Spalten x −3/−0.5/2 und Reihen z −2.2/−0.4/1.4/3.2, die Stühle bei (x ± 0.35, z + 0.55). Sitzende Figuren: Pose `sitzen`, `schaut: [0, 0]`, `blickhoehe: 0.95`.
Blickpunkte: `tafel, tuer, fenster, klasse, decke, boden, pult, hinten`.

| Feld | Wirkung |
|---|---|
| `effekt: {tafel: {ab, modus, von, text}}` | Smartboard: `aus`, `video` (Nachtsicht-Video), `countdown` (von), `pause`, `geloescht`, `text` |
| `effekt: {handys: s}` | alle Handys auf den Tischen leuchten und vibrieren |
| `effekt: {klingel: s}` | Lautsprecher wackelt (Ton: `schulgong.wav`) |

Neue Geräusche: `schulgong, tuer_auf, murmeln, smartboard_an, handys_vibrieren, atmo_klasse` (`python3 tools/sfx_synth.py mutprobe3`). Musik: `gen/musik_20_klasse.mp3`, `gen/musik_21_wahrheit.mp3`.
