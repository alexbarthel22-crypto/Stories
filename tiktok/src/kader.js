const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1600,height:1220},deviceScaleFactor:1});
await p.goto('file://'+__dirname+'/page.html'); await p.evaluate(()=>{render(0);return document.fonts.ready});
await p.evaluate(()=>{
 const r=document.getElementById('root'); r.setAttribute('viewBox','0 0 1600 1220'); r.setAttribute('width',1600); r.setAttribute('height',1220);
 const t=0.5, m=0; UID=0; PID=0;
 const list=[[vlad({}), '1','VLAD','TOR'],[opa({}),'4','OPA JÜRGEN','ABWEHR'],[teamPlayer(6,t),'3','IRO','ABWEHR'],[teamPlayer(1,t),'5','BULLDOZER','ABWEHR'],
  [teamPlayer(4,t),'6','HIPSTER','MITTELFELD'],[teamPlayer(0,t),'7','VOKUHILA','MITTELFELD'],[teamPlayer(3,t),'8','DER JÜNGSTE','MITTELFELD'],[teamPlayer(2,t),'10','SPIELMACHERIN','MITTELFELD'],
  [busguy({}),'9','BUS VERPASST','STURM'],[teamPlayer(5,t),'11','DER COOLE','STURM'],[teamPlayer(7,t),'14','TRÄUMER','STURM']];
 let s=`<rect width="1600" height="1220" fill="#3E6B32"/>`+badge(800,70,'KADER FC SCHLAMMLOCH',{kind:'pitch',fs:50});
 list.push([coach({}),'','CHEFTRAINER','ICH']); 
 list.forEach(([svg,n,name,pos],i)=>{const col=i%7,row=Math.floor(i/7);const x=118+col*227,y=row?1010:500;
   s+=place(svg,x,y,0.4)+label(x,y+50,name,28,'#fff')+label(x,y+84,(n?'#'+n+' · ':'')+pos,22,'#FFD31A');});
 s+=place(corgi({}),1480,990,0.3)+label(1480,1060,'CORGI',28,'#fff')+label(1480,1094,'MASKOTTCHEN',22,'#FFD31A');
 r.innerHTML=s;});
await p.screenshot({path:process.argv[2]});await b.close();})();
