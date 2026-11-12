import json,sys,urllib.request,os
V={'ich':'SOYHLrjzK2X1ezoPC6cr','sven':'TX3LPaxmHKxFdv7VOQHJ','lea':'EXAVITQu4vr4xnSDxMaL','ansage':'pNInz6obpgDQGcFmaJgB'}
model=sys.argv[1]; only=sys.argv[2:]
for s in json.load(open('script.json')):
    if only and s['id'] not in only: continue
    out=f"vo/{s['id']}.mp3"
    if os.path.exists(out) and not only: continue
    body={'text':s['say'],'model_id':model,'language_code':'de'}
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{V[s['who']]}?output_format=mp3_44100_128",data=json.dumps(body).encode(),headers={'Content-Type':'application/json','xi-api-key':'dummy'})
    try: open(out,'wb').write(urllib.request.urlopen(req,timeout=120).read()); print(s['id'],'ok')
    except urllib.error.HTTPError as e: print(s['id'],e.code,e.read().decode()[:300]); sys.exit(1)
