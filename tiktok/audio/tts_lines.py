import base64, json, os, sys, urllib.request
key = os.environ['GEMINI_API_KEY']
lines = json.load(open(sys.argv[1]))
out = sys.argv[2]
style = ('Lies im Stil eines jungen, schnellen TikTok-Creators vor (klares Hochdeutsch, zuegig, trocken-ironisch, '
         'kurze Kunstpause vor Pointen, zwischen den Zeilen eine Sekunde Pause) - und zwar genau diesen Text:\n')
body = {'contents': [{'parts': [{'text': style + '\n'.join(lines)}]}],
        'generationConfig': {'responseModalities': ['AUDIO'],
                             'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': 'Puck'}}}}}
req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent',
    data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
r = json.load(urllib.request.urlopen(req, timeout=600))
p = r['candidates'][0]['content']['parts'][0]['inlineData']
open(out, 'wb').write(base64.b64decode(p['data']))
print(p['mimeType'])
