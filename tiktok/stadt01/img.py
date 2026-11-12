import base64,json,os,sys,urllib.request
STYLE=("Hand-drawn 2D cartoon comic illustration, bold clean black outlines, flat cel shading, slightly muted colors, "
 "extreme first-person POV shot through a strong fisheye wide-angle lens (curved horizon and walls), vertical 9:16 frame. "
 "The viewer's own arms/hands in dark grey hoodie sleeves may appear at the bottom edge. Night-time, city in blackout, orange fire light and smoke. "
 "Absolutely no text, no letters, no captions, no watermark. ")
SVEN="Sven: a German teenage boy, 17, short messy dark-brown hair, red hoodie, jeans, cartoon style. "
LEA="Lea: a teenage girl, 18, black hooded jacket, black gas mask covering her face, dark ponytail, fingerless gloves, cartoon style. "
S={
'01':SVEN+"Inside a dark small apartment living room. The window directly next to the viewer is exploding inward: glass shards flying toward the camera, a huge orange fireball outside. Sven ducks and dives toward the floor, mouth open shouting.",
'02':SVEN+"Viewer lies on the floor among broken glass, looking toward the shattered window. Sven crouches below the window frame. Through the window: a dark street, a city bus burning, all buildings without electricity.",
'03':"Viewer stands on a dark empty city street at night. A tall pole with a loudspeaker horn in the foreground. Smoke columns rising behind dark apartment blocks, distant military trucks with headlights, a burning car.",
'04':SVEN+"Close-up: Sven grabs the viewer's arm with his hand, leaning in, whispering urgently, scared serious eyes. Dark street behind, orange glow.",
'05':"A dark street corner. A black quadcopter surveillance drone floats around the corner at eye level, pointing a bright red scanning laser beam straight into the viewer's face. Sinister.",
'06':SVEN+"Viewer sprints through a narrow back alley with trash bins, motion blur, viewer's hands pumping at the bottom edge. Sven runs ahead looking back over his shoulder, terrified.",
'07':"Viewer climbs a metal fire escape ladder on a brick building, both hands gripping the rungs at the bottom of the frame, looking down: a black drone with a red glowing eye rises below in the alley.",
'08':SVEN+"On a flat rooftop at night, viewer looks down over the edge onto a wide street where a fuel tanker truck explodes in a gigantic orange fireball with black smoke. Sven stands beside, lit orange, shocked.",
'09':LEA+SVEN+"On the rooftop. Lea steps out of the shadow holding a crackling blue electric stun baton raised toward the viewer, threatening pose. Sven in the background raises his hands. Tense, non-violent cartoon.",
'10':LEA+"Close-up: Lea's gloved hand grips the viewer's forearm (dark grey sleeve) and holds a small handheld scanner device over the wrist, the device glows bright red. Rooftop at night.",
'11':LEA+"Close-up: Lea holds the crackling blue electric stun baton toward the camera, gas mask lenses reflecting orange fire, dramatic red rim light, tense cartoon cliffhanger moment.",
}
REF={'04':'02','06':'02','08':'02','09':'02','10':'09','11':'09'}
model='gemini-3.1-flash-image'
for k in (sys.argv[1:] or S):
    out=f'img/{k}.png'
    if os.path.exists(out) and not sys.argv[1:]: continue
    parts=[{'text':STYLE+S[k]}]
    if k in REF: parts=[{'text':'Keep the characters and art style consistent with this reference image:'},{'inline_data':{'mime_type':'image/png','data':base64.b64encode(open(f'img/{REF[k]}.png','rb').read()).decode()}}]+parts
    body={'contents':[{'parts':parts}],'generationConfig':{'responseModalities':['IMAGE'],'imageConfig':{'aspectRatio':'9:16'}}}
    req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':os.environ['GEMINI_API_KEY']})
    try: r=json.load(urllib.request.urlopen(req,timeout=300))
    except urllib.error.HTTPError as e: print(k,e.code,e.read().decode()[:300]); continue
    d=[p['inlineData']['data'] for p in r['candidates'][0].get('content',{}).get('parts',[]) if 'inlineData' in p]#['data'] for p in r['candidates'][0]['content']['parts'] if 'inlineData' in p]
    if d: open(out,'wb').write(base64.b64decode(d[0])); print(k,'ok')
    else: print(k,'no image',str(r)[:300])
