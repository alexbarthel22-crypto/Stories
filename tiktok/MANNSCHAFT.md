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
- **Maskottchen: Frodo, ein süßer Frosch** – grün, sitzend, große Glubschaugen oben auf dem Kopf, rosa Bäckchen, hellgrüner Bauch, breites Lächeln; hüpft gern; (Ersetzt den früheren Corgi.)

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

## Folge 1 (veröffentlicht)
- Datei: `tiktok/tag01_fc_schlammloch_frodo_v7.mp4` (0:52; Stadionkulisse in Szene 1; neue Lo-Fi-Musik; 2 € pro Video teilen statt pro Kommentar; Frodo statt Corgi, ohne Kronkorken; Intro: Weitwinkel auf Platz mit Tor, Kamera zoomt auf den Trainer, Fußball fliegt rein und trifft das „TAG 1“-Feld; Namenskarten direkt über den Figuren), Titelbild `tag01_thumbnail.png`, Beschreibung `tag01_beschreibung.md`
- Ablauf: Tag 1 → Verein gegründet → 1 Follow = 1 Tribünenplatz → Tribüne aus 3 Klappstühlen → Willkommen beim FC Schlammloch (Logo) → Platz = Schlammloch → Flutlicht = Taschenlampe am Mast (Akku 3 %) → Kreisliga, ganz unten → Vorstellung von Vlad (Tor), Opa Jürgen (Abwehr), Bus-Verpasser in Flip-Flops (Sturm), Frodo der Frosch (Maskottchen) → Ziel: Deutscher Meister → Sonntag 1. Spiel (ganzes Team) → Fans: 0 (traurig) → Folgen = Klappstuhl Nr. 1 → Vereinskasse 500 € → 1 € pro Follower, 2 € pro geteiltem Video → Was tun mit dem Geld? (Flutlicht kaufen / Vereinshaus mieten / was ganz anderes) → Top-Kommentar entscheidet
- Ohne Stadionjubel (die Variante mit Jubel, `gemini_v4`, wird nicht genutzt)

## Thumbnail-Vorlage (für jede Folge gleich)
- `node src/thumb.js <Tag> <Fans> <Kasse in €> <ausgabe.png>`, z. B. `node src/thumb.js 2 37 571 tag02_thumbnail.png`
- Großer Spielfeld-Kasten „TAG X“, darunter orange „⚽ FC SCHLAMMLOCH“, der Trainer groß und lachend, unten zwei Kästen: **FANS** (rot bei 0, sonst grün) und **VEREINSKASSE** (grün, Betrag in €)
- Alles Wichtige liegt im mittleren 3:4-Ausschnitt, der im TikTok-Profilraster sichtbar ist

## Stand nach Tag 1
- Liga: Kreisliga. Ziel: Deutscher Meister (Bundesliga)
- Tribüne: 3 Klappstühle (ohne Sitzkissen), Nr. 1–3, stehen außerhalb des Platzes
- Flutlicht: Taschenlampe auf einem Holzmast, außerhalb des Platzes
- Vereinskasse: 500 €
- Geld-Regel: Jeder Follower bringt 1 € in die Vereinskasse, jedes **Video teilen** 2 € (Box mit dem TikTok-Teilen-Icon `src/teilen_icon.jpg`). Kommentare bringen kein Geld mehr, der Top-Kommentar entscheidet aber weiterhin
- Fans: 0. Erstes Spiel: Sonntag
- Offene Frage an die Community: Flutlicht kaufen, Vereinshaus mieten oder etwas ganz anderes? Der Top-Kommentar entscheidet

## Videostil
- Format 1080×1920, 30 fps, maximal 59 s
- Dauerregen, Untertitel Wort für Wort (Schrift Lilita One, weiß mit brauner Kontur, Schlüsselwörter gelb)
- Boxen im Spielfeld-Look oder orange, dicke braune Kontur, harter Schatten
- Fußball immer im Stil des ⚽-Emojis
- Tor immer auf der Torlinie am Spielfeldrand, mit Fünfmeterraum, Strafraum und Elfmeterpunkt davor
- Oberste Text-Boxen beginnen frühestens bei y ≈ 280 (oberer TikTok-Sicherheitsbereich)
- Namenskarten und Info-Boxen sitzen nah am Geschehen (direkt über Kopf bzw. Objekt), nicht ganz oben am Bildrand
- Intro jeder Folge: Weitwinkel auf den Platz mit Tor und Strafraum, der Trainer steht darauf; die Kamera zoomt während der ersten Szene auf ihn. Ein Fußball fliegt von unten links ins Bild, trifft das „TAG X“-Feld beim Erscheinen und springt oben rechts raus (mit Aufprall-Geräusch)
- Untertitel bei y 1420 (unter den Mündern), TikTok-Sicherheitsbereiche: Inhalte zwischen y 240 und y 1450, rechts nicht über x 940

## Stimme
- Hintergrundmusik: eigene Komposition, lizenzfrei – **Lo-Fi-Hip-Hop** (`src/music2.py`, Hörprobe `audio/hintergrundmusik_lofi.wav`): 92 BPM, a-Moll, E-Piano-Akkorde Am7–Fmaj7–C–G, Boom-Bap-Drums, Bass, kurze Pfeif-Melodie als Hook, leichtes Vinyl-Knistern; wird unter der Stimme leiser. (Die frühere Marimba-Musik `src/music.py` wird nicht mehr genutzt.)
- Soundeffekte (leise gemischt): synthetisch in `src/sfx.py` (Szene 1: synthetische Großstadion-Kulisse `stadium()` nach dem Vorbild der Referenz – Grundteppich, Anschwellen zum Jubel, viel Hall, Fokus 1,5–5 kHz, Hörprobe `audio/stadion_intro_hoerprobe.wav`; Schlamm-Platscher bei Schnitten, Flackern beim Flutlicht; keine Platz- und Hupen-Sounds; Münzen, Kassenklingeln, Pfiff, Fanfare, trauriges Posaunen-„wah-wah“, Benachrichtigungs-Ding)
- Final: Gemini TTS (`gemini-3.8-flash-tts`), Stimme **Puck**
- Regie: schneller TikTok-Creator, trocken-ironisch, Kunstpausen vor Pointen, „Fans: null“ traurig, Ziel und Folgen-Aufruf mit Energie
- Ganzes Skript in **einem** Aufruf einsprechen, an den Pausen in Szenen schneiden, mit `atempo=0.85` auf das Referenztempo (ca. 150 Wörter pro Minute) bringen
- Stimmanalyse der Referenzvideos: `audio/analyse.json`
- Entwurfsstimme (kostenlos, offline): espeak-ng mit MBROLA `mb-de6`
