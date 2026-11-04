# Heute ist Alex … – TikTok-Serie

Deutsche Kurzvideos (9:16, 1080×1920, max. 1:30). Hauptfigur **Alex** schlüpft jeden Tag in eine neue Rolle.

## Folgen
| # | Thema | Datei | Länge |
|---|-------|-------|-------|
| 1 | Pick-me-Boy | `episodes/01_pick_me_boy/01_pick_me_boy.mp4` | 1:27 |
| 2 | Arbeitslos | `episodes/02_arbeitslos/02_arbeitslos.mp4` | 1:19 |
| 3 | Choleriker | `episodes/03_choleriker/03_choleriker.mp4` | 1:20 |
| 4 | Milliardär | `episodes/04_milliardaer/04_milliardaer.mp4` | 1:16 |
| 5 | F-Boy | `episodes/05_fboy/05_fboy.mp4` | 1:18 |
| 6 | OF-Model (Alexia) | `episodes/06_of_model/06_of_model.mp4` | 1:16 |
| 7 | Emotional abhängig (TikTok Folge 2) | `episodes/07_emotional_abhaengig/07_emotional_abhaengig.mp4` | 1:12 |
| 8 | Friedrich Merz, Parodie (TikTok Folge 3) | `episodes/08_merz/08_merz.mp4` | 1:11 |

## Alex – fester Look (gilt für alle Folgen)
Definiert in `tools/alexlib.py` → `ALEX_BASE`. **Nicht ändern**, nur das Outfit wechselt pro Rolle.
- blonde Tolle mit Seitenscheitel (Locke nach rechts)
- runde schwarze Brille, Sommersprossen, rosa Wangen
- heller Hautton

## Aufbau jeder Folge
1. **Intro (≈3,7 s):** Auswahl-Leiste wie im Referenzvideo: 12 Rollen werden durchgeschaltet,
   mit den **Original-Tick-Sounds im Original-Rhythmus** (2-2-2-2-3-3-3-4-4-5-6 Frames),
   dann weißer Blitz und Reveal mit dem **Original-Burst-Sound** (`assets/sfx/`).
2. Tagesablauf mit Uhrzeiten, Illustration oben, Alex unten, Untertitel-Box.
3. Outro: Markier-Aufruf + „Was soll Alex morgen sein? Schreib's in die Kommentare.“

## Neue Folge bauen
```bash
pip install piper-tts pycairo scipy soundfile numpy
# Stimme: de_DE-thorsten-high.onnx (+ .json) lokal ablegen
cp -r episodes/01_pick_me_boy episodes/02_neu   # script.py + scenes.py anpassen
python3 tools/tts.py episodes/02_neu /pfad/de_DE-thorsten-high.onnx 0.9
python3 tools/build.py episodes/02_neu --stills 2,10,30   # Vorschau-Bilder
python3 tools/build.py episodes/02_neu                    # fertiges MP4
```
Sound-Effekte neu extrahieren: `python3 tools/extract_sfx.py referenz.wav assets/sfx`

## Feste Regeln für neue Folgen
- Schluss immer: „Kennst du jemanden, der …? Markier sie oder ihn!“ + „Und was soll Alex morgen sein? Schreib's in die Kommentare.“
- Raster am Ende zeigt die tatsächlich veröffentlichten TikTok-Folgen (Folge 1 = Pick-me-Boy).
- Stimme: gemini-3.8-flash-tts, Puck (wie Pick-me-Boy), nicht auf andere Modelle ausweichen.
