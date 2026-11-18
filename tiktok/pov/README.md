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
| `sfx` | Geräusch aus `sfx/` abspielen | `"ping.wav"` oder `{"datei": "boom.wav", "ab": 0.3, "lautstaerke": 0.8}` |

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
| `atmo`, `atmo_lautstaerke` | Hintergrundrauschen (Wind/Stadt), `null` = aus |

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
