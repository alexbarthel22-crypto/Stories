import json,subprocess,os,textwrap
T=json.load(open('timeline.json')); FONT='/usr/share/fonts/opentype/inter/Inter-Black.otf'
os.makedirs('subs',exist_ok=True)
inp=[];fl=[]
RUN={'06':14,'07':8}
for i,(img,st,en) in enumerate(T['scenes']):
    d=en-st; clip=f'clips/{img}.mp4'; isclip=os.path.exists(clip)
    inp+=(['-i',clip] if isclip else ['-loop','1','-framerate','30','-t',f'{d:.3f}','-i',f'img/{img}.png'])
    sx=[];sy=[]
    for t0,A in T['shakes']:
        if st-0.01<=t0<en:
            l=t0-st; sx.append(f"{A}*exp(-(t-{l:.3f})*5)*sin(47*(t-{l:.3f}))*gte(t,{l:.3f})"); sy.append(f"{A}*exp(-(t-{l:.3f})*5)*cos(39*(t-{l:.3f}))*gte(t,{l:.3f})")
    if img in RUN: sx.append(f"{RUN[img]}*sin(t*11)"); sy.append(f"{RUN[img]*1.5}*abs(sin(t*11))")
    sx.append("6*sin(t*1.3)"); sy.append("5*sin(t*1.7)")
    dx=40 if i%2 else -40
    X=f"(iw-1080)/2+{dx}*t/{d:.3f}+"+"+".join(sx); Y=f"(ih-1920)/2-30*t/{d:.3f}+"+"+".join(sy)
    pre=f"fps=30,tpad=stop_mode=clone:stop_duration=20,trim=duration={d:.3f},setpts=PTS-STARTPTS,scale=1420:2524:force_original_aspect_ratio=increase," if isclip else "scale=1420:-2,"
    fl.append(f"[{i}:v]{pre}crop=1080:1920:'{X}':'{Y}',setsar=1,fps=30,format=yuv420p[s{i}]")
n=len(T['scenes'])
fl.append("".join(f"[s{i}]" for i in range(n))+f"concat=n={n}:v=1:a=0[cat]")
end=T['scenes'][-1][2]
chain="[cat]tpad=stop_mode=add:stop_duration=%.2f:color=black,vignette=PI/4.5,eq=contrast=1.06:saturation=1.1"%(T['total']-end)
for t0,d in T['flashes']: chain+=f",eq=brightness=0.45:enable='between(t,{t0:.2f},{t0+d:.2f})'"
for k,(a,b,txt,radio) in enumerate(T['subs']):
    lines=textwrap.wrap(txt,22); col='0xFFE14D' if radio else 'white'
    for j,ln in enumerate(lines):
        p=f'subs/{k}_{j}.txt'; open(p,'w').write(ln)
        chain+=f",drawtext=fontfile={FONT}:textfile={p}:fontsize=62:fontcolor={col}:borderw=7:bordercolor=black:x=(w-text_w)/2:y=h*0.64+{j*80}:enable='between(t,{a:.2f},{b+0.15:.2f})'"
open("subs/end1.txt","w").write("TEIL 2 MORGEN"); open("subs/end2.txt","w").write("Glaubt ihr Lea?"); open("subs/end3.txt","w").write("Schreibt es in die Kommentare")
chain+=f",drawtext=fontfile={FONT}:textfile=subs/end1.txt:fontsize=96:fontcolor=0xFF3B30:borderw=6:bordercolor=black:x=(w-text_w)/2:y=h*0.42:enable='gte(t,{end+0.2:.2f})'"
chain+=f",drawtext=fontfile={FONT}:textfile=subs/end2.txt:fontsize=60:fontcolor=white:x=(w-text_w)/2:y=h*0.52:enable='gte(t,{end+0.8:.2f})'"
chain+=f",drawtext=fontfile={FONT}:textfile=subs/end3.txt:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h*0.57:enable='gte(t,{end+0.8:.2f})'[v]"
fl.append(chain)
cmd=['ffmpeg','-y','-v','error']+inp+['-i','mix.wav','-filter_complex',";".join(fl),'-map','[v]','-map',f'{n}:a','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',f"{T['total']:.2f}",'-movflags','+faststart','../stadt01_teil1.mp4']
r=subprocess.run(cmd); print('rc',r.returncode)
