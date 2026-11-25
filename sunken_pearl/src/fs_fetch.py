import json, sys, urllib.request, urllib.parse, os
Q = {
 'waves': ('sea waves', '[3 TO 60]'),
 'plunge': ('underwater dive splash', '[1 TO 15]'),
 'deepamb': ('deep underwater ambience', '[20 TO 300]'),
 'whoosh': ('whoosh', '[1 TO 8]'),
 'sonar': ('sonar ping', '[1 TO 10]'),
 'clock': ('clock ticking', '[3 TO 30]'),
 'knock': ('knock glass', '[1 TO 10]'),
 'groan': ('metal creak', '[3 TO 30]'),
 'flicker': ('light flicker electrical buzz', '[1 TO 10]'),
 'hiss': ('steam pressure hiss', '[1 TO 10]'),
 'crack': ('glass crack', '[1 TO 10]'),
 'alarm': ('submarine alarm', '[2 TO 30]'),
 'run': ('running footsteps metal', '[2 TO 20]'),
 'elev': ('elevator moving hum', '[5 TO 60]'),
 'ding': ('elevator ding', '[0.5 TO 5]'),
 'doors': ('elevator doors opening', '[1 TO 10]'),
 'cave': ('ethereal drone ambient pad', '[15 TO 200]'),
 'breath': ('breathing deep', '[2 TO 20]'),
 'boom': ('boom impact deep', '[0.5 TO 8]'),
 'growl': ('growl', '[1 TO 10]'),
 'sting': ('horror sting impact', '[1 TO 10]'),
 'heart': ('heartbeat', '[3 TO 30]'),
 'riser': ('cinematic riser tension', '[2 TO 15]'),
 'bubbles': ('bubbles underwater', '[2 TO 20]'),
 'drip': ('water drip echo', '[1 TO 15]'),
}
os.makedirs('audio/fs', exist_ok=True)
credits = {}
for k, (q, dur) in Q.items():
    if sys.argv[1:] and k not in sys.argv[1:]: continue
    for lic in ['license:"Creative Commons 0"', '']:
        params = {'query': q, 'filter': f'duration:{dur} ' + lic, 'sort': 'downloads_desc',
                  'fields': 'id,name,duration,license,previews,username', 'page_size': 5}
        r = json.load(urllib.request.urlopen('https://freesound.org/apiv2/search/text/?' + urllib.parse.urlencode(params), timeout=60))
        if r['results']: break
    if not r['results']:
        print('NONE', k); continue
    it = r['results'][0]
    data = urllib.request.urlopen(it['previews']['preview-hq-mp3'], timeout=120).read()
    open(f'audio/fs/{k}.mp3', 'wb').write(data)
    credits[k] = {'name': it['name'], 'user': it['username'], 'id': it['id'], 'license': it['license'], 'dur': it['duration']}
    print(k, it['name'], it['username'], round(it['duration'], 1), it['license'].split('/')[-3:-1])
old = json.load(open('audio/fs/credits.json')) if os.path.exists('audio/fs/credits.json') else {}
old.update(credits)
json.dump(old, open('audio/fs/credits.json', 'w'), indent=1)
