# Bilder kostenlos in Videoclips verwandeln

So geht's:
1. Lade das Bild (`img/NN.png`) bei einem kostenlosen Bild-zu-Video-Dienst hoch.
2. Füge den Prompt ein und wähle das Format **9:16**.
3. Lade den Clip herunter und schick ihn mir als `NN.mp4`. Ich setze Ton, Untertitel und Wackeln automatisch drüber.

Kostenlose Dienste (Stand: meine Kenntnis, Limits ändern sich):
- **Meta AI** (meta.ai → Bild hochladen → „Animate“): gratis, kurze Clips
- **Grok Imagine** (grok.com / X-App): gratis-Kontingent pro Tag
- **Kling AI** (klingai.com): tägliche Gratis-Credits, ca. 1–3 Clips pro Tag
- **Hailuo / MiniMax** (hailuoai.video): Gratis-Credits für neue Konten

Tipp: Clips mit 5 s reichen überall. Ist ein Clip länger als die Szene, schneide ich ihn; ist er kürzer, friert das letzte Bild ein.

| Szene | Länge | Prompt (Englisch funktioniert am besten) |
|---|---|---|
| 01 | 3 s | First-person POV, window glass explodes inward toward the camera, orange fireball outside, the boy in red hoodie dives to the floor, camera shakes violently, cartoon style |
| 02 | 5 s | First-person POV lying on the floor, camera slowly lifts, the boy crouches and peeks out the broken window, bus burning outside with flickering flames and smoke, cartoon style |
| 03 | 6 s | First-person POV walking slowly down a dark street, smoke columns rise and drift, distant fire flickers, headlights of military trucks move in the distance, handheld camera, cartoon style |
| 04 | 7 s | The boy grabs the viewer's arm and whispers urgently, subtle head movements, flickering orange light on his face, handheld camera, cartoon style |
| 05 | 5 s | A black drone hovers around the corner toward the camera, red laser beam scanning across the viewer, propellers spinning, fire flickering, cartoon style |
| 06 | 3 s | Fast first-person POV sprint through the alley, strong camera bob, the boy runs ahead and looks back, flames flicker, cartoon style |
| 07 | 4 s | First-person POV climbing up the fire escape ladder, hands grabbing rungs one after another, drone with red eye rising from below, cartoon style |
| 08 | 5 s | The fuel tanker truck on the street below explodes in a giant fireball, shockwave, smoke billows up, the boy flinches, camera shakes, cartoon style |
| 09 | 7 s | The girl in the gas mask steps forward out of the shadow, the electric stun baton crackles with blue sparks, the boy raises his hands, cartoon style |
| 10 | 4 s | The girl holds the scanner over the viewer's wrist, the device lights up and blinks red, sparks, cartoon style |
| 11 | 6 s | The girl slowly raises the crackling stun baton toward the camera, gas mask lenses reflect fire, slow push-in, tense, cartoon style |

Die Bilder liegen in `tiktok/stadt01/img/`. Fertige Clips kommen in `tiktok/stadt01/clips/` (Dateiname = Szenennummer, z. B. `05.mp4`). Danach: `python3 video.py`.
