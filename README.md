# Stories – Rätsel-Videos für TikTok

Vertikale Erklärvideos (1080×1920, 30 fps) im flachen Vektor-Look mit natürlicher, emotionaler Erzählstimme (Gemini TTS, Stimme „Puck“).

| # | Thema | Datei | Länge |
|---|-------|-------|-------|
| 1 | Alex und der Aufzug | `videos/01_alex_aufzug/video.mp4` | 1:16 |
| 2 | Niklas, Wolf, Ziege und Kohlkopf | `videos/02_fluss/video.mp4` | 1:09 |
| 3 | Nils und die drei Lichtschalter | `videos/03_lichtschalter/video.mp4` | 1:00 |
| 4 | Dario und die zwei Eimer (4 Liter) | `videos/04_eimer/video.mp4` | 1:01 |
| 5 | Die drei Türen im Kellergewölbe | `videos/05_tueren/video.mp4` | 0:57 |

## Kanal-Standard (für jedes neue Video)
- Musik: immer `assets/music/raetsel_theme.mp3` (Lyria), 15 dB unter der Stimme
- Stimme: Gemini TTS, Stimme „Puck“, `gemini-3.1-flash-tts-preview`, Tempo 1.12
- Optik: flacher Vektor-Look, Blaue-Stunde-Skyline, Inter-ExtraBold-Pills, Fragen-Szene mit Denkpause, Outro „Hättest du's gewusst?“
- `safecheck.py` muss „OK“ melden; Cover (`make_cover.py`) + `description.txt` ohne Spoiler

## Aufbau
- `engine/toolkit.py` – Zeichen-Toolkit (Figuren, Kamera, Titel-Pills, Uhr, Etagenanzeige, Regen …)
- `engine/tts_gemini.py` – **Standard:** Gemini TTS (natürlich, emotional), eine Anfrage pro Zeile mit gemeinsamem Stil-Prompt, `{amused}`/`{surprised}` als Regieanweisung, automatische Whisper-Prüfung gegen erfundenen Text, Tempo-Faktor. Braucht `GEMINI_API_KEY` (optional `WHISPER_DIR` für die Prüfung).
- `engine/tts.py` – Offline-Fallback (Piper): Hauptstimme `de_DE-thorsten-high`, emotionale Zeilen (`{amused}`, `{surprised}`) mit `de_DE-thorsten_emotional-medium`, +2 Halbtöne (jünger). Korrigiert den ç-Laut („ich“, „-ig“) und hat ein Aussprache-Lexikon (`LEXICON`). Schreibt `voice.wav` + `timing.json`
- `engine/animals.py` – Wolf, Ziege, Kohlkopf, Boot, Glühbirne, Lichtschalter im Kanal-Stil
- `engine/audio.py` – Soundeffekte, Mix mit Ducking; Hintergrundmusik aus Datei (z. B. mit Google Lyria generiert, siehe `music.txt`) oder als prozeduraler Fallback
- `videos/<nr>_<name>/` – `script.txt` (Sprechtext, `[PAUSE x]` = Pause), `make_audio.py`, `make_video.py`

## Neu bauen
```bash
pip install numpy pillow soundfile   # + piper-tts / sherpa-onnx für Offline-TTS bzw. Prüfung
export GEMINI_API_KEY=...            # optional: WHISPER_DIR=<sherpa-onnx-whisper-small>
python3 engine/tts_gemini.py videos/01_alex_aufzug/script.txt videos/01_alex_aufzug \
  --voice Puck --model gemini-3.1-flash-tts-preview --tempo 1.12
cd videos/01_alex_aufzug && python3 make_audio.py && python3 make_video.py
```
TikTok-Sicherheitsbereiche prüfen: `python3 safecheck.py` (meldet jedes Textelement, das unter Suchleiste, Icon-Spalte oder Beschreibung läge; `--stills` erzeugt Kontrollbilder mit eingeblendeten Zonen).

Szenen-Timings werden automatisch aus `timing.json` übernommen – Text ändern, neu sprechen lassen, neu rendern.
