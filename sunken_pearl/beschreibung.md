# Sunken Pearl – Folge 1: Etage −201

**Beschreibung (TikTok):**
Shelly wohnt im Sunken Pearl – dem luxuriösesten Wolkenkratzer der Welt. Er wächst nicht nach oben, sondern 200 Etagen tief ins Meer. 🐚✨🌊
Marmor, Kristall, Gold … und statt Skyline ein leuchtendes Korallenriff.
Dann liegt eine Einladung vor ihrer Tür: „Etage −201. Mitternacht.“ Aber der Turm hat nur 200 Etagen …
Was ist in der Perle? Schreib's in die Kommentare! 👇

#sunkenpearl #animation #3danimation #story #luxury #underwater #mermaidcore #shelly #fyp #fürdich

---

## Produktion
- 3D: Blender 5.3 (Cycles), komplett prozedural per Python gebaut (`src/`): Figur `shelly.py`, Sets `sets_lux.py`, Einstellungen `shots.py`
- Stimme: ElevenLabs, Stimme „Otto“ (eleven_multilingual_v2), Text in `src/script.txt`
- Musik: selbst synthetisiert (`src/mix.py`)
- Schrift: Anton (SIL Open Font License, `src/fonts/OFL_LICENSE.txt`)
- Geräusche (Freesound, alle CC0):
- plunge: "Dipping below water 2" von adviseme333 (freesound.org/s/679407, CC0)
- deepamb: "09 Stream, Dirty Sewer, Dark, Trickling, Burbling, Flowing, Underwater, Dive Deep 2 Freebie.wav" von hisoul (freesound.org/s/493076, CC0)
- whoosh: "Swoosh" von Shinplaster (freesound.org/s/264777, CC0)
- elev: "ship-interior-1.wav" von markkuyp (freesound.org/s/344379, CC0)
- ding: "Elevator Ping 02" von LilMati (freesound.org/s/514865, CC0)
- doors: "elevator doors opening" von ccovi (freesound.org/s/679014, CC0)
- cave: "Resonating Ambient Drone with Distant Shimmering Voices" von bassimat (freesound.org/s/875083, CC0)
- riser: "Riser Hit sfx 119" von AudioPapkin (freesound.org/s/822419, CC0)
- bubbles: "SFX_UnderWater" von Perel (freesound.org/s/173439, CC0)
- waves: "Ocean Noise - Surf" von amholma (freesound.org/s/372181, CC0)
- boom: "whoosh+boom.wav" von Capashen (freesound.org/s/118934, CC0)
- chime: "GLEAM-GLOW-SFX-CHIME.wav" von newagesoup (freesound.org/s/351408, CC0)
- harp: "Good answer harp glissando.wav" von oggraphics (freesound.org/s/610703, CC0)
- paper: "MONTECOT_Mélissa_2015_2016_candy_paper.wav" von iut_Paris8 (freesound.org/s/345035, CC0)
- clink: "Glass Ding / Toast with champagne glasses" von Breviceps (freesound.org/s/458408, CC0)
- shimmer: "Magic Shimmer Swell" von Qvantor (freesound.org/s/880769, CC0)
- reveal: "Treasure Chest Reveal" von Qvantor (freesound.org/s/878615, CC0)

## Neu rendern
```
python -m venv venv && venv/bin/pip install bpy numpy pillow
src/render_all.sh          # 23 Einstellungen -> frames/v2/<shot>/
python3 src/mix.py         # Ton -> audio/final_mix.wav
src/assemble.sh            # Untertitel/Grading -> sunken_pearl.mp4
```
