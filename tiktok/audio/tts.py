import base64, json, os, sys, urllib.request, wave
key = os.environ['GEMINI_API_KEY']
model = sys.argv[1] if len(sys.argv) > 1 else 'gemini-3.8-flash-tts'
segs = json.load(open('../tt/script.json'))
fix = {'Ein Korgi.': 'Ein Corgi.', 'Pitschu.': 'Pitschu.'}
lines = []
for s in segs:
    t = s['say']
    for a, b in fix.items(): t = t.replace(a, b)
    lines.append(t)
script = '\n'.join(lines)
style = ('WICHTIG: Sprich SCHNELL. Der gesamte Text muss in etwa 55 Sekunden gesprochen sein, also rund 180 Woerter pro Minute, wie ein schneller TikTok-Voiceover. '
 'Keine langen Pausen: zwischen Zeilen hoechstens 0,3 Sekunden, nur vor Pointen kurz 0,5 Sekunden. '
 'Sprich auf Deutsch wie ein junger TikTok-Creator, der seinen eigenen Fussballverein vorstellt: klares Hochdeutsch, '
 'schnelles Grundtempo, direkte Ansprache, nah am Mikrofon. '
 'Zwischen den Zeilen nur kurze Pausen von etwa 0,3 Sekunden. Wechsle spielerisch zwischen begeisterter Aufbruchstimmung und trockenem, '
 'ironischem Deadpan-Humor. Vor absurden Pointen (zum Beispiel "Mit Augenklappe.", "In Flip-Flops.", "Null.", "Und ein Kaugummi.") '
 'eine kurze Kunstpause von etwa einer halben Sekunde und die Stimme leicht resigniert absenken. '
 '"Und unsere Fans? Null." klingt traurig und ernuechtert. Bei "Deutscher Meister in der Bundesliga!" und "Folg jetzt" deutlich mehr Energie. '
 'Die letzte Zeile ist ein klarer Aufruf zum Kommentieren.\n\n')
body = {'contents': [{'parts': [{'text': style + script}]}],
        'generationConfig': {'responseModalities': ['AUDIO'],
                             'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': 'Puck'}}}}}
req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
    data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
try:
    r = json.load(urllib.request.urlopen(req, timeout=600))
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read().decode()[:600]); sys.exit(1)
p = r['candidates'][0]['content']['parts'][0]['inlineData']
pcm = base64.b64decode(p['data'])
print(p['mimeType'], len(pcm))
raw = pcm
open(sys.argv[2] if len(sys.argv) > 2 else 'out.wav', 'wb').write(raw)
print('ok')
sys.exit(0)
w = wave.open(sys.argv[2] if len(sys.argv) > 2 else 'gemini_full.wav', 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm); w.close()
print('dauer', len(pcm) / 2 / 24000)
