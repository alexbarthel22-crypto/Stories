import json,subprocess,numpy as np,wave,os
SR=44100; rng=np.random.default_rng(3)
def load(f,extra=''):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse'+extra,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).copy()
RADIO=',highpass=f=350,lowpass=f=3200,acrusher=bits=10:mix=0.3,volume=1.6,aecho=0.8:0.6:120:0.25'
S={s['id']:s for s in json.load(open('script.json'))}
# szenen: (bild, [(zeile oder ('sfx',name)), ...], extra-pause-nach)
PLAN=[('01',[('fx','boom'),('gap',0.25),'01','02'],0.4),
      ('02',['03'],0.5),
      ('03',[('gap',0.3),'04'],0.5),
      ('04',['05'],0.4),
      ('05',[('fx','drone'),('gap',0.6),'06','07'],0.2),
      ('06',['08'],0.5),
      ('07',['09'],0.6),
      ('08',[('fx','bigboom'),('gap',1.2),'10'],0.6),
      ('09',[('fx','zap'),('gap',0.4),'11','12'],0.4),
      ('10',[('fx','beep'),('gap',0.9),'13'],0.6),
      ('11',[('fx','zap'),('gap',0.3),'15'],0.8)]
def t_(d): return np.arange(int(d*SR))/SR
def lp(x,n): return np.convolve(x,np.ones(n)/n,'same')
def boom(d=2.5,big=1.0):
    t=t_(d); n=lp(rng.standard_normal(len(t)),int(60*big)); sub=np.sin(2*np.pi*(55-25*t)*t)
    crack=rng.standard_normal(len(t))*np.exp(-t*25)
    return ((n*6+sub*0.8)*np.exp(-t*(2.2/big))+crack*0.5)*0.55
def glass(d=1.2):
    t=t_(d); x=np.zeros(len(t))
    for _ in range(60):
        i=int(rng.uniform(0,0.8)*SR); f=rng.uniform(2500,7000); tt=t_(0.08)
        x[i:i+len(tt)]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*60)*rng.uniform(.05,.2)
    return x
def drone(d):
    t=t_(d); return (np.sign(np.sin(2*np.pi*180*t))*0.3+np.sin(2*np.pi*362*t))*0.04*(1+0.3*np.sin(2*np.pi*3*t))
def beep():
    out=[]; 
    for k in range(3): tt=t_(0.12); out+= [np.sin(2*np.pi*1800*tt)*0.25, np.zeros(int(0.08*SR))]
    tt=t_(0.6); out.append(np.sin(2*np.pi*900*tt)*0.3); return np.concatenate(out)
def zap(d=0.8):
    t=t_(d); return rng.standard_normal(len(t))*(0.5+0.5*np.sign(np.sin(2*np.pi*23*t)))*np.exp(-t*3)*0.18
def whoosh(d=0.5):
    t=t_(d); return lp(rng.standard_normal(len(t)),30)*np.sin(np.pi*t/d)*0.5
def steps(d):
    x=np.zeros(int(d*SR)); 
    for s in np.arange(0,d-0.1,0.28):
        tt=t_(0.09); i=int(s*SR); x[i:i+len(tt)]+=lp(rng.standard_normal(len(tt)),20)*np.exp(-tt*50)*0.6
    return x
FX={'boom':lambda:boom()+np.pad(glass(),(0,int(1.3*SR))) ,'bigboom':lambda:boom(4,1.8)*1.3,'drone':lambda:drone(2.0),'beep':beep,'zap':zap}
# layout
voice=[];sfx=[];subs=[];scenes=[];t=0.0;shakes=[];flashes=[]
for img,items,after in PLAN:
    st=t
    for it in items:
        if isinstance(it,tuple):
            if it[0]=='gap': t+=it[1]; continue
            a=FX[it[1]](); sfx.append((t,a))
            if it[1] in('boom','bigboom'): shakes.append((t,28 if it[1]=='boom' else 40)); flashes.append((t,0.18))
            if it[1]=='zap': flashes.append((t,0.08))
            continue
        s=S[it]; radio=s['who']=='ansage'
        a=load(f'vo/{it}.mp3',RADIO if radio else '')
        voice.append((t,a)); d=len(a)/SR
        subs.append((t,t+d,s['sub'],radio)); t+=d+0.25
    t+=after; scenes.append((img,st,t))
END=3.5; total=t+END
mix=np.zeros(int((total+1)*SR))
def put(t0,a,g=1.0):
    i=int(t0*SR); mix[i:i+len(a)]+=a[:len(mix)-i]*g
for t0,a in voice: put(t0,a,1.0)
for t0,a in sfx: put(t0,a,0.9)
# running steps in scene 06/07, drone hum under 05-07
for img,st,en in scenes:
    if img in('06','07'): put(st,steps(en-st),0.5)
    if img in('05','06','07'): put(st,drone(en-st),0.5)
    put(st,whoosh(),0.25)
# dark music bed: low pulse + pad + heartbeat at the end
tt=np.arange(len(mix))/SR
pad=(np.sin(2*np.pi*55*tt)+0.5*np.sin(2*np.pi*82.4*tt)+0.3*np.sin(2*np.pi*110*tt*1.003))*0.05
pulse=np.sin(2*np.pi*45*tt)*np.exp(-(tt%0.5)*12)*0.25
siren=np.sin(2*np.pi*(650+180*np.sin(2*np.pi*0.25*tt))*tt)*0.012
bed=pad+pulse+siren
s11=scenes[-1][1]; hb=(tt>s11)*np.sin(2*np.pi*50*tt)*(np.exp(-((tt-s11)%0.8)*18)+np.exp(-(((tt-s11)-0.22)%0.8)*18))*0.5
bed[tt>total-END+0.3]*=0; mix+=bed+hb*(tt<total-END+0.3)
mix=mix[:int(total*SR)]; mix/=max(1e-6,np.abs(mix).max())/0.95
w=wave.open('mix.wav','w');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype(np.int16).tobytes());w.close()
json.dump({'scenes':scenes,'subs':subs,'shakes':shakes,'flashes':flashes,'total':total},open('timeline.json','w'),ensure_ascii=False,indent=0)
print('dauer %.1f s'%total)
