import json, base64, urllib.request, sys
text = open(sys.argv[1]).read().replace('\n', ' ').strip()
voice = sys.argv[2]
body = {"text": text, "model_id": "eleven_multilingual_v2", "language_code": "de",
        "voice_settings": {"stability": 0.42, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True, "speed": 1.15}}
req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
    data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "xi-api-key": "dummy", "User-Agent": "curl/8.5"})
r = json.load(urllib.request.urlopen(req, timeout=300))
open(sys.argv[3] + '.mp3', 'wb').write(base64.b64decode(r['audio_base64']))
json.dump(r['alignment'], open(sys.argv[3] + '.json', 'w'))
a = r['alignment']; print('dur', a['character_end_times_seconds'][-1])
