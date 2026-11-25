# Sunken Pearl – Folge 1: Etage −201

**Beschreibung (TikTok):**
Shelly wohnt im Sunken Pearl – dem einzigen Wolkenkratzer der Welt, der nach UNTEN wächst. 200 Etagen tief ins Meer. 🐚🌊
Heute Nacht um 3:12 klopft es. Am Fenster. In 4.000 Metern Tiefe …
Soll Shelly die Perle öffnen? JA oder NEIN – schreib's in die Kommentare! 👇

#sunkenpearl #animation #3danimation #story #mystery #tiefsee #gruselig #shelly #fyp #fürdich

---

## Produktion
- 3D: Blender 5.3 (Cycles), komplett prozedural per Python gebaut (`src/`): Figur `shelly.py`, Sets `sets*.py`, Einstellungen `shots.py`
- Stimme: ElevenLabs, Stimme „Otto“ (eleven_multilingual_v2), Text in `src/script.txt`
- Musik: selbst synthetisiert (`src/mix.py`)
- Schrift: Anton (SIL Open Font License, `src/fonts/OFL_LICENSE.txt`)
- Geräusche (Freesound, alle CC0):
- plunge: "Dipping below water 2" von adviseme333 (freesound.org/s/679407, CC0)
- deepamb: "09 Stream, Dirty Sewer, Dark, Trickling, Burbling, Flowing, Underwater, Dive Deep 2 Freebie.wav" von hisoul (freesound.org/s/493076, CC0)
- whoosh: "Swoosh" von Shinplaster (freesound.org/s/264777, CC0)
- sonar: "Submarine sonar ping" von therealdeevee (freesound.org/s/653896, CC0)
- clock: "Foley_Object_Clock_Old_Tick_Sequence_Stereo" von Nox_Sound (freesound.org/s/790019, CC0)
- flicker: "Vintage Edison Bulb Flicker & Warm-Up Sound Effect" von hipoidogs (freesound.org/s/866662, CC0)
- hiss: "centraleverwarming .wav" von noisesounds (freesound.org/s/333449, CC0)
- crack: "break01.wav" von Johnny97 (freesound.org/s/566448, CC0)
- alarm: "Submarine submersion alarm_mono_wave.wav" von Guialgarve (freesound.org/s/480898, CC0)
- run: "Retro-Styled Footsteps - Metal" von MalikArsYasakani (freesound.org/s/845047, CC0)
- elev: "ship-interior-1.wav" von markkuyp (freesound.org/s/344379, CC0)
- ding: "Elevator Ping 02" von LilMati (freesound.org/s/514865, CC0)
- doors: "elevator doors opening" von ccovi (freesound.org/s/679014, CC0)
- cave: "Resonating Ambient Drone with Distant Shimmering Voices" von bassimat (freesound.org/s/875083, CC0)
- breath: "Man breathing regularly then faster" von exe2be (freesound.org/s/512741, CC0)
- growl: "DRAGON_ROAR.wav" von JoelAudio (freesound.org/s/85568, CC0)
- sting: "Sting/jumpscare" von hotpin7 (freesound.org/s/846789, CC0)
- heart: "RWHeart.wav" von bluejello13 (freesound.org/s/232481, CC0)
- riser: "Riser Hit sfx 119" von AudioPapkin (freesound.org/s/822419, CC0)
- bubbles: "SFX_UnderWater" von Perel (freesound.org/s/173439, CC0)
- drip: "WATR_DRIPPING FAUCET" von Patricio_San (freesound.org/s/807590, CC0)
- waves: "Ocean Noise - Surf" von amholma (freesound.org/s/372181, CC0)
- knock: "hit - glass - window 01.wav" von Anthousai (freesound.org/s/406261, CC0)
- groan: "squeak_01.wav" von joedeshon (freesound.org/s/339184, CC0)
- boom: "whoosh+boom.wav" von Capashen (freesound.org/s/118934, CC0)

## Neu rendern
```
python -m venv venv && venv/bin/pip install bpy numpy pillow
src/render_all.sh          # 26 Einstellungen -> frames/<shot>/
python3 src/mix.py         # Ton -> audio/final_mix.wav
src/assemble.sh            # Untertitel/Grading -> sunken_pearl.mp4
```
