# Stories – Rätsel-Videos für TikTok

Vertikale Erklärvideos (1080×1920, 30 fps) im flachen Vektor-Look mit weiblicher Erzählstimme.

| # | Thema | Datei | Länge |
|---|-------|-------|-------|
| 1 | Alex und der Aufzug | `videos/01_alex_aufzug/video.mp4` | 1:19 |

## Aufbau
- `engine/toolkit.py` – Zeichen-Toolkit (Figuren, Kamera, Titel-Pills, Uhr, Etagenanzeige, Regen …)
- `engine/tts.py` – Offline-Sprachausgabe (Piper, Stimme `de_DE-kerstin-low`), schreibt `voice.wav` + `timing.json`
- `engine/audio.py` – generierte Hintergrundmusik, Soundeffekte, Mix mit Ducking
- `videos/<nr>_<name>/` – `script.txt` (Sprechtext, `[PAUSE x]` = Pause), `make_audio.py`, `make_video.py`

## Neu bauen
```bash
pip install piper-tts numpy pillow soundfile
python3 engine/tts.py videos/01_alex_aufzug/script.txt <pfad>/de_DE-kerstin-low.onnx videos/01_alex_aufzug 0.83
cd videos/01_alex_aufzug && python3 make_audio.py && python3 make_video.py
```
Szenen-Timings werden automatisch aus `timing.json` übernommen – Text ändern, neu sprechen lassen, neu rendern.
