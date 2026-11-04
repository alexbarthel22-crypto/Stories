import base64, json, os, sys, urllib.request
key = os.environ['GEMINI_API_KEY']
lines = json.load(open(sys.argv[1]))
out = sys.argv[2]
style = ('WICHTIG: Sprich SCHNELL, rund 180 Woerter pro Minute, wie ein schneller TikTok-Voiceover. '
 'Sprich auf Deutsch wie ein junger TikTok-Creator, der seinen eigenen Fussballverein vorstellt: klares Hochdeutsch, schnelles Grundtempo, '
 'direkte Ansprache, nah am Mikrofon. Trockener, ironischer Deadpan-Humor. Vor Pointen eine kurze Kunstpause von etwa einer halben Sekunde, '
 'die Stimme dabei leicht resigniert absenken. "Und unsere Fans? Null." klingt traurig und ernuechtert; sprich "unsere" deutlich als "un-se-re", nicht "unserer". '
 'Zwischen den Zeilen jeweils eine volle Sekunde Stille lassen. '
 'Lies diese Regieanweisung NICHT vor. Sprich ausschliesslich den Text nach der Markierung TEXT:\n\nTEXT:\n')
body = {'contents': [{'parts': [{'text': style + '\n'.join(lines)}]}],
        'generationConfig': {'responseModalities': ['AUDIO'],
                             'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': 'Puck'}}}}}
req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent',
    data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
r = json.load(urllib.request.urlopen(req, timeout=600))
p = r['candidates'][0]['content']['parts'][0]['inlineData']
open(out, 'wb').write(base64.b64decode(p['data']))
print(p['mimeType'])
