import json, sys, urllib.request, urllib.parse, os
Q = {
 'pop': ('pop bubble ui', '[0.05 TO 1]'),
 'music': ('happy ukulele loop', '[20 TO 120]'),
 'steps': ('footsteps stairs', '[2 TO 20]'),
 'swoosh': ('swoosh transition', '[0.2 TO 1.5]'),
 'gull': ('seagulls beach', '[4 TO 40]'),
 'thinking': ('thinking music', '[5 TO 60]'),
}
os.makedirs('audio/fs', exist_ok=True)
credits = {}
for k, (q, dur) in Q.items():
    if sys.argv[1:] and k not in sys.argv[1:]: continue
    for lic in ['license:"Creative Commons 0"']:
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
