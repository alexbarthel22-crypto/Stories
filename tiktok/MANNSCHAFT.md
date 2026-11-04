# FC Schlammloch – feste Besetzung

Diese Figuren bleiben in allen Folgen gleich. Gezeichnet werden sie in `src/chars.js` und `src/team.js`, das Kaderbild ist `kader.png`.

| Nr. | Name | Position | Aussehen |
|---|---|---|---|
| 1 | **Vlad** | Tor | schwarze Haare, Augenklappe (links), grünes Torwarttrikot, Handschuhe |
| 4 | **Opa Jürgen** | Abwehr | Glatze mit weißen Haarresten, runde Brille, weißer Schnauzer, Gehstock, **kräftiger Körper mit Bierbauch** (breite Schultern, dicke Arme und Beine) |
| 3 | Iro *(Platzhalter-Name)* | Abwehr | grüner Irokese, Ohrring |
| 5 | Bulldozer *(Platzhalter-Name)* | Abwehr | Glatze, roter Vollbart |
| 6 | Hipster *(Platzhalter-Name)* | Mittelfeld | Dutt, eckige Brille |
| 7 | Vokuhila *(Platzhalter-Name)* | Mittelfeld | rotbrauner Vokuhila, rotes Stirnband |
| 8 | Der Jüngste *(Platzhalter-Name)* | Mittelfeld | rote Cap, Zahnspange |
| 10 | Spielmacherin *(Platzhalter-Name)* | Mittelfeld | braune Zöpfe mit pinken Haargummis |
| 9 | **Der, der den Bus verpasst hat** (Name noch offen) | Sturm | blonde Strubbelhaare, verschlafene Augen, Rucksack, **Flip-Flops** |
| 11 | Der Coole *(Platzhalter-Name)* | Sturm | Afro, Sonnenbrille |
| 14 | Träumer *(Platzhalter-Name)* | Sturm | Locken, blaue Kopfhörer |

- **Cheftrainer (Ich-Erzähler):** dunkle Haare mit Seitenscheitel, kurzer Vollbart, blaue Parka-Jacke
- **Pichu (gesprochen „Pitschu“), Maskottchen:** Pembroke Corgi, rotgold mit weißer Brust, Schnauze, Blesse und Beinen, große Stehohren, langer Körper, kurzer Hals, kurze Beine, buschiger Schwanz, **kein Halsband**

Vereinsfarben: Blau `#2F7FD8`, Gelb `#FFD31A`. Trikots blau mit gelber Nummer, Torwart grün.

## Umgebung (Schauplatz aller Videos)
- **Wetter/Zeit:** Dauerregen, dunkler Abendhimmel (Dunkelblau bis Graublau), ziehende dunkle Wolken, Regenringe in Pfützen
- **Hintergrund:** dichte Baumreihe in Dunkelgrün am Horizont
- **Spielfeld:** ein einziges Schlammloch – brauner Matsch mit vereinzelten Grasflecken und vielen Pfützen
- **Tor:** weißes Tor mit Netz, steht immer auf der Torlinie, davor Fünfmeterraum, Strafraum, Elfmeterpunkt und Teilkreis
- **Spielfeldrand:** Grasstreifen hinter einer weißen Seitenlinie. Dort stehen die Tribüne und das Flutlicht
- **Tribüne:** 3 orange Holz-Klappstühle mit Metallgestell, nummeriert 1–3, ohne Kissen
- **Flutlicht:** Holzmast mit Klebeband-Schellen, oben eine schwarz-gelbe Taschenlampe, flackernd (Akku 3 %)
- **Vereinskasse:** grüne Geldkassette mit Nieten, gelbem Schloss und Etikett „VEREINSKASSE“, steht auf einer Holzkiste
- **Bushaltestelle:** Mast mit gelb-grünem H-Schild (gehört zum Stürmer #9)

## Stand nach Tag 1
- Liga: Kreisliga. Ziel: Deutscher Meister (Bundesliga)
- Tribüne: 3 Klappstühle (ohne Sitzkissen), Nr. 1–3, stehen außerhalb des Platzes
- Flutlicht: Taschenlampe auf einem Holzmast, außerhalb des Platzes
- Vereinskasse: 500 € und ein Kaugummi
- Geld-Regel: Jeder Follower bringt 1 € in die Vereinskasse, jeder Kommentar 2 €
- Fans: 0. Erstes Spiel: Sonntag
- Offene Frage an die Community: Flutlicht kaufen, Vereinshaus mieten oder etwas ganz anderes? Der Top-Kommentar entscheidet

## Videostil
- Format 1080×1920, 30 fps, maximal 59 s
- Dauerregen, Untertitel Wort für Wort (Schrift Lilita One, weiß mit brauner Kontur, Schlüsselwörter gelb)
- Boxen im Spielfeld-Look oder orange, dicke braune Kontur, harter Schatten
- Fußball immer im Stil des ⚽-Emojis
- Tor immer auf der Torlinie am Spielfeldrand, mit Fünfmeterraum, Strafraum und Elfmeterpunkt davor
- TikTok-Sicherheitsbereiche: Inhalte zwischen y 240 und y 1300, rechts nicht über x 940

## Stimme
- Final: Gemini TTS (`gemini-3.8-flash-tts`), Stimme **Puck**
- Regie: schneller TikTok-Creator, trocken-ironisch, Kunstpausen vor Pointen, „Fans: null“ traurig, Ziel und Folgen-Aufruf mit Energie
- Ganzes Skript in **einem** Aufruf einsprechen, an den Pausen in Szenen schneiden, mit `atempo=0.85` auf das Referenztempo (ca. 150 Wörter pro Minute) bringen
- Stimmanalyse der Referenzvideos: `audio/analyse.json`
- Entwurfsstimme (kostenlos, offline): espeak-ng mit MBROLA `mb-de6`
