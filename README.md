# Stories – Rätsel-Videos für TikTok

Vertikale Erklärvideos (1080×1920, 30 fps) im flachen Vektor-Look mit junger männlicher Erzählstimme.

| # | Thema | Datei | Länge |
|---|-------|-------|-------|
| 1 | Alex und der Aufzug | `videos/01_alex_aufzug/video.mp4` | 1:12 |

## Aufbau
- `engine/toolkit.py` – Zeichen-Toolkit (Figuren, Kamera, Titel-Pills, Uhr, Etagenanzeige, Regen …)
- `engine/tts.py` – Offline-Sprachausgabe (Piper): Hauptstimme `de_DE-thorsten-high`, emotionale Zeilen (`{amused}`, `{surprised}`) mit `de_DE-thorsten_emotional-medium`, +2 Halbtöne (jünger). Korrigiert den ç-Laut („ich“, „-ig“) und hat ein Aussprache-Lexikon (`LEXICON`). Schreibt `voice.wav` + `timing.json`
- `engine/audio.py` – generierte Hintergrundmusik, Soundeffekte, Mix mit Ducking
- `videos/<nr>_<name>/` – `script.txt` (Sprechtext, `[PAUSE x]` = Pause), `make_audio.py`, `make_video.py`

## Neu bauen
```bash
pip install piper-tts numpy pillow soundfile
# Stimmen: https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models (vits-piper-de_DE-thorsten-high, ...-thorsten_emotional-medium)
python3 engine/tts.py videos/01_alex_aufzug/script.txt videos/01_alex_aufzug \
  --model <pfad>/de_DE-thorsten-high.onnx --emo-model <pfad>/de_DE-thorsten_emotional-medium.onnx --length 0.85 --pitch 2
cd videos/01_alex_aufzug && python3 make_audio.py && python3 make_video.py
```
Szenen-Timings werden automatisch aus `timing.json` übernommen – Text ändern, neu sprechen lassen, neu rendern.
