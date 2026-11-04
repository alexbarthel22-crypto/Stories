import base64, json, os, sys, urllib.request
key = os.environ['GEMINI_API_KEY']
prompt = sys.argv[1]; out = sys.argv[2]
body = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseModalities': ['AUDIO']}}
req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/lyria-3-clip-preview:generateContent',
    data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
try:
    r = json.load(urllib.request.urlopen(req, timeout=600))
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read().decode()[:800]); sys.exit(1)
for p in r['candidates'][0]['content']['parts']:
    if 'inlineData' in p:
        open(out, 'wb').write(base64.b64decode(p['inlineData']['data'])); print(p['inlineData']['mimeType'])
    elif 'text' in p: print('TEXT:', p['text'][:300])
