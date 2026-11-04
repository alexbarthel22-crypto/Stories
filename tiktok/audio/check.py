import base64, json, os, sys, urllib.request
key = os.environ['GEMINI_API_KEY']
f = sys.argv[1]
parts = [{'inline_data': {'mime_type': 'audio/mp3', 'data': base64.b64encode(open(f, 'rb').read()).decode()}},
         {'text': 'Transkribiere diese deutsche Aufnahme woertlich. Antworte als JSON-Liste von Objekten {"start": Sekunden, "ende": Sekunden, "text": Satz}, ein Objekt pro Satz bzw. Frage.'}]
body = {'contents': [{'parts': parts}], 'generationConfig': {'responseMimeType': 'application/json'}}
req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent',
    data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
r = json.load(urllib.request.urlopen(req, timeout=300))
txt = r['candidates'][0]['content']['parts'][0]['text']
open(f + '.json', 'w').write(txt)
for x in json.loads(txt): print(x['start'], x['ende'], x['text'])
