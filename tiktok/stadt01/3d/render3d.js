const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
(async()=>{
 const [,, out, ...frames]=process.argv;const root=__dirname+'/..';
 const srv=spawn('python3',['-m','http.server','8766','--bind','127.0.0.1'],{cwd:root,stdio:'ignore'});await new Promise(r=>setTimeout(r,800));
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:720,height:1280},deviceScaleFactor:1.5});
 p.on('pageerror',e=>{console.error('PAGEERR',e.message);process.exit(1)});p.on('console',m=>{if(m.type()=='error')console.error('CONSOLE',m.text())});
 await p.goto('http://127.0.0.1:8766/3d/index.html');await p.waitForFunction(()=>window.ready);const nf=await p.evaluate(()=>init());
 const shot=async f=>{await p.evaluate(f=>render(f),f);return p.screenshot({type:'jpeg',quality:90})};
 if(out.endsWith('.mp4')){
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','30','-i','-','-i',root+'/mix.wav','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  const t0=Date.now();for(let f=0;f<nf;f++){const buf=await shot(f);if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(f%150==0)console.log('frame',f,'/',nf,((Date.now()-t0)/1000|0)+'s')}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));
 } else { for(const f of frames){fs.writeFileSync(`${out}/p${String(f).padStart(5,'0')}.jpg`,await shot(+f))} }
 await b.close();srv.kill();})();
