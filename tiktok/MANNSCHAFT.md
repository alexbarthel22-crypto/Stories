# FC Schlammloch – feste Besetzung

Diese Figuren bleiben in allen Folgen gleich. Gezeichnet werden sie in `src/chars.js` und `src/team.js`, das Kaderbild ist `kader.png`.

| Nr. | Name | Position | Aussehen |
|---|---|---|---|
| 1 | **Vlad** | Tor | schwarze Haare, Augenklappe immer auf **seinem rechten Auge** (vom Betrachter aus links, auch beim Laufen nie spiegeln), grünes Torwarttrikot, Handschuhe |
| 4 | **Opa Jürgen** | Abwehr | Glatze mit weißen Haarresten, runde Brille, weißer Schnauzer, Gehstock, **kräftiger Körper mit Bierbauch** (breite Schultern, dicke Arme und Beine) |
| 3 | Iro *(Platzhalter-Name)* | Abwehr | grüner Irokese, Ohrring |
| 5 | Bulldozer *(Platzhalter-Name)* | Abwehr | Glatze, roter Vollbart |
| 6 | Hipster *(Platzhalter-Name)* | Mittelfeld | Dutt, eckige Brille |
| 7 | Vokuhila *(Platzhalter-Name)* | Mittelfeld | rotbrauner Vokuhila, rotes Stirnband |
| 8 | Der Jüngste *(Platzhalter-Name)* | Mittelfeld | rote Cap, Zahnspange |
| 10 | Spielmacherin *(Platzhalter-Name)* | Mittelfeld | braune Zöpfe mit pinken Haargummis |
| 9 | ~~Der, der den Bus verpasst hat~~ – **seit Tag 2 raus** (hat morgens den Bus genommen). Neue Nr. 9 wird ein Fan aus den Kommentaren | Sturm | blonde Strubbelhaare, verschlafene Augen, Rucksack, **Flip-Flops** |
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
- Datei: `tiktok/tag01_fc_schlammloch_frodo_v10.mp4` (0:52; Stadionjubel in Szene 1 aus Pixabay-Aufnahme; neue Lo-Fi-Musik; 2 € pro Video teilen statt pro Kommentar; Frodo statt Corgi, ohne Kronkorken; Intro: Weitwinkel auf Platz mit Tor, Kamera zoomt auf den Trainer, Fußball fliegt rein und trifft das „TAG 1“-Feld; Namenskarten direkt über den Figuren), Titelbild `tag01_thumbnail.png`, Beschreibung `tag01_beschreibung.md`
- Ablauf: Tag 1 → Verein gegründet → 1 Follow = 1 Tribünenplatz → Tribüne aus 3 Klappstühlen → Willkommen beim FC Schlammloch (Logo) → Platz = Schlammloch → Flutlicht = Taschenlampe am Mast (Akku 3 %) → Kreisliga, ganz unten → Vorstellung von Vlad (Tor), Opa Jürgen (Abwehr), Bus-Verpasser in Flip-Flops (Sturm), Frodo der Frosch (Maskottchen) → Ziel: Deutscher Meister → Sonntag 1. Spiel (ganzes Team) → Fans: 0 (traurig) → Folgen = Klappstuhl Nr. 1 → Vereinskasse 500 € → 1 € pro Follower, 2 € pro geteiltem Video → Was tun mit dem Geld? (Flutlicht kaufen / Vereinshaus mieten / was ganz anderes) → Top-Kommentar entscheidet
- Ohne Stadionjubel (die Variante mit Jubel, `gemini_v4`, wird nicht genutzt)

## Thumbnail-Vorlage (für jede Folge gleich)
- `node src/thumb.js <Tag> <Fans> <Kasse in €> <ausgabe.png> [+Zuwachs]`, z. B. `node src/thumb.js 2 83 0 tag02_thumbnail.png +83`
- Großer Spielfeld-Kasten „TAG X“, darunter orange „⚽ FC SCHLAMMLOCH“, der Trainer groß und lachend, unten zwei Kästen: **FANS** (rot bei 0, sonst grün) und **VEREINSKASSE** (grün, bei 0 € rot), optional grüner Pfeil nach oben mit Fan-Zuwachs (z. B. „+83“) am Fans-Kasten
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
- Intro jeder Folge: euphorisch gesprochen „Tag X! Ich gründe einen Fußballverein!“, darunter die orange Box „⚽ ICH GRÜNDE EINEN FUSSBALLVEREIN“ (Tag 1: „⚽ VEREIN GEGRÜNDET“). Weitwinkel auf den Platz mit Tor und Strafraum, der Trainer steht darauf; die Kamera zoomt während der ersten Szene auf ihn. Ein Fußball fliegt von unten links ins Bild, trifft das „TAG X“-Feld beim Erscheinen und springt oben rechts raus (mit Aufprall-Geräusch)
- Untertitel bei y 1420 (unter den Mündern), TikTok-Sicherheitsbereiche: Inhalte zwischen y 240 und y 1450, rechts nicht über x 940

## Stimme
- Hintergrundmusik: eigene Komposition, lizenzfrei – **Lo-Fi-Hip-Hop** (`src/music2.py`, Hörprobe `audio/hintergrundmusik_lofi.wav`): 92 BPM, a-Moll, E-Piano-Akkorde Am7–Fmaj7–C–G, Boom-Bap-Drums, Bass, kurze Pfeif-Melodie als Hook, leichtes Vinyl-Knistern; wird unter der Stimme leiser. (Die frühere Marimba-Musik `src/music.py` wird nicht mehr genutzt.)
- Soundeffekte (leise gemischt): synthetisch in `src/sfx.py` (Szene 1: Stadionjubel aus der Pixabay-Aufnahme „crowd-cheering-379666“ (Pixabay-Lizenz), Ausschnitt Sekunde 1,85–4,36 (sofort laut), startet mit dem Video und läuft nur in Szene 1, `audio/stadion_intro_jubel.wav`; Schlamm-Platscher bei Schnitten, Flackern beim Flutlicht; keine Platz- und Hupen-Sounds; Münzen, Kassenklingeln, Pfiff, Fanfare, trauriges Posaunen-„wah-wah“, Benachrichtigungs-Ding)
- Final: Gemini TTS (`gemini-3.8-flash-tts`), Stimme **Puck**
- Regie: schneller TikTok-Creator, trocken-ironisch, Kunstpausen vor Pointen, „Fans: null“ traurig, Ziel und Folgen-Aufruf mit Energie
- Ganzes Skript **immer in einem einzigen Aufruf** einsprechen (sonst klingen Szenen unterschiedlich), „Follower“ in der Sprache vermeiden (klingt amerikanisch) – stattdessen „neue Fans“; Stil-Satz: „Read in German like an energetic, fast, dry and ironic young TikTok creator, the same voice and mood for every line, with a one-second pause between lines:“; an den Pausen in Szenen schneiden, mit `atempo=0.85` auf das Referenztempo (ca. 150 Wörter pro Minute) bringen
- Stimmanalyse der Referenzvideos: `audio/analyse.json`
- Entwurfsstimme (kostenlos, offline): espeak-ng mit MBROLA `mb-de6`

## Folge 2 (Tag 2)
- Datei: `tiktok/tag02_fc_schlammloch_v8.mp4` (0:48; Jubel leiser; komplette Sprache in EINEM Gemini-Aufruf für eine einheitliche Stimme), Titelbild `tag02_thumbnail.png`, Beschreibung `tag02_beschreibung.md`, Code `src_tag02/`
- Die ersten drei Fans sitzen auf Klappstuhl 1–3 (Cartoon-Figuren mit Schal, keine echten Fotos):
  - Stuhl 1: **Eike** (@eikemzz) – rote Cap, graues Hoodie
  - Stuhl 2: **Tobi** (@tobiii1911) – braune Locken, oranges Hoodie
  - Stuhl 3: **Leo** (@leo.hro1) – graue Haare, grauer Schnauzer, schwarze Jacke
  - Gesprochen nur Vornamen („Unsere ersten drei Fans: Eike, Tobi und Leo!“), angezeigt mit ihren echten Profilbildern (aus dem Screenshot, `src_tag02/fanpics.js`) und Usernamen; sie sitzen hinter der Seitenlinie
- Fans: **83**
- Geld: 83 Follower × 1 € = 83 € + 24 Kommentare × 2 € = 48 € + 500 € = **631 €**. Ausgegeben: **80 Klappstühle = 500 €** (Reihen am Spielfeldrand) und eine blau-gelbe **Plane = 131 €** über der Tribüne. **Vereinskasse danach: 0 €**
- Die Nr. 9 hat morgens den Bus genommen und ist raus. Gesucht wird eine neue Nr. 9 aus der Community
- Regel ab Tag 2: **1 Follower = 1 €, 1 Kommentar = 2 €**
- Ablauf: TAG 2 (euphorisch gesprochen, Box „⚽ ICH GRÜNDE EINEN FUSSBALLVEREIN“) → 83 Fans (Frodo hüpft neben dem Trainer) → die ersten 3 Fans auf der Tribüne → Problem: nur 3 Plätze (traurige, nasse Menge buht – Buh-Chor aus Gemini-„Buuuh“ geschichtet, `src_tag02/buh_menge.wav` –, Sprechblasen „NASS!“, „WILL SITZEN!“, „MIR IST KALT!“, „BUUUH!“) → Rechnung (Vlad läuft im Tor hin und her) → 631 € → 80 Klappstühle in 8 Reihen → Plane drüber, 80 Fans setzen sich, Eike/Tobi/Leo klein vorne in der ersten Reihe → „Aber dann die Enttäuschung…“: Bus mit dem Stürmer Nr. 9 fährt weg → Nr. 9 wird dramatisch rot durchgestrichen, „RAUS!“ → „Also suchen wir einen neuen Stürmer mit der Nummer neun“ (hoffnungsvoll, Trikot am Bügel) → 80 Klappstühle −500 €, Plane −131 €, Kasse 0 € → „Wir brauchen dich, um die Vereinskasse zu füllen!“ + Geld-Regel (großes, mittiges „DICH!“) → Top-Kommentar: „Wer wird Nr. 9? Und was sollen wir vom Geld kaufen?“ → „Sonntag ist unser erstes Spiel gegen den SC Heuballen. Wir brauchen euch!“ (Wappen FC Schlammloch vs. SC Heuballen)

## Stand nach Tag 2
- Fans: 83 · Vereinskasse: 0 €
- Tribüne: viele Klappstühle am Spielfeldrand, darüber eine Plane; Stuhl 1–3 gehören @eikemzz, @tobiii1911, @leo.hro1
- Kader: 10 Spieler, die Nr. 9 ist frei
- Nächstes Spiel: **Sonntag, 1. Spiel gegen den SC Heuballen** (Gegner-Wappen: gelber Schild mit Heuballen, grüner Kopfbalken)
