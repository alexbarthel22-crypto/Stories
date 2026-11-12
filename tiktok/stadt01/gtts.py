import base64,json,os,sys,urllib.request,subprocess
voice=sys.argv[1]
for item in sys.argv[2:]:
    id,style,text=item.split('|')
    body={'contents':[{'parts':[{'text':text}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':voice}}}}}
    req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':os.environ['GEMINI_API_KEY']})
    r=json.load(urllib.request.urlopen(req,timeout=300)); pcm=base64.b64decode(r['candidates'][0]['content']['parts'][0]['inlineData']['data'])
    subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar','24000','-ac','1','-i','-','-ar','44100','-b:a','128k',f'vo/{id}.mp3'],input=pcm); print(id,'ok')
