import json, sys, urllib.request, os
S = {
 'waves': ("Calm night ocean waves gently lapping against a metal platform, distant buoy bell, soft wind", 4),
 'plunge': ("Camera plunges underwater: splash then muffled deep underwater whoosh with bubbles", 3),
 'deepamb': ("Deep ocean underwater ambience, low muffled rumble, distant whale-like metal groans, eerie", 22),
 'descend': ("Fast deep underwater descent whoosh, pressure rumble, sonar ping", 4),
 'clock': ("Antique wall clock ticking loudly in a silent room, close up", 3),
 'knock': ("Three slow heavy knocks on thick glass porthole, muffled underwater, ominous", 2.5),
 'groan': ("Deep metal hull groaning and creaking under water pressure, submarine", 5),
 'flicker': ("Electric light bulb flickering and buzzing, power surge, crackle", 2.5),
 'hiss': ("Pressure gauge needle dropping, high pressure hiss from pipe, metal strain", 2.5),
 'crack': ("Thick glass window cracking and splintering slowly under pressure, water dripping", 3),
 'alarm': ("Old submarine emergency alarm klaxon, repeating, metallic corridor reverb", 6),
 'run': ("Fast running footsteps on metal grating corridor with water puddles splashing", 3),
 'elev': ("Old brass elevator descending, mechanical hum, cable rattling, low drone", 10),
 'glitch': ("Elevator ding bell distorted and glitching, eerie wrong note", 2),
 'doors': ("Heavy elevator doors sliding open slowly, then vast cavern reverb whoosh", 3),
 'cave': ("Vast underwater cave ambience, ethereal shimmering tones, distant deep hum", 12),
 'breath': ("Giant creature slow deep breathing, low resonant pulse, inhale exhale", 5),
 'innerknock': ("Three very heavy deep knocks from inside a giant hollow object, booming resonance", 3),
 'eyeopen': ("Giant eye opening, wet organic slow squelch with deep monster growl rumble", 3),
 'sting': ("Horror cinematic sting, deep impact boom with rising dissonant strings, cliffhanger", 5),
}
only = sys.argv[1:]
for k, (txt, d) in S.items():
    if only and k not in only: continue
    fn = f'audio/sfx/{k}.mp3'
    if os.path.exists(fn): continue
    body = {"text": txt, "duration_seconds": d, "prompt_influence": 0.5}
    req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "xi-api-key": "dummy", "User-Agent": "curl/8.5"})
    try:
        open(fn, 'wb').write(urllib.request.urlopen(req, timeout=300).read()); print('ok', k)
    except urllib.error.HTTPError as e:
        print('ERR', k, e.code, e.read()[:200])
