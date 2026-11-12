const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{
 const [,, out, ...frames]=process.argv;
 const srv=spawn('python3',['-m','http.server','8765','--bind','127.0.0.1'],{cwd:__dirname,stdio:'ignore'});
 await new Promise(r=>setTimeout(r,800));
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>{console.error('PAGEERR',e.message);process.exit(1)});
 await p.goto('http://127.0.0.1:8765/page.html');const nf=await p.evaluate(()=>init());
 const shot=async f=>{await p.evaluate(f=>render(f),f);return p.screenshot({type:'jpeg',quality:90})};
 if(out.endsWith('.mp4')){
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','30','-i','-','-i',__dirname+'/mix.wav','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<nf;f++){const buf=await shot(f);if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(f%300==0)console.log('frame',f,'/',nf)}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));
 } else { for(const f of frames){require('fs').writeFileSync(`${out}/p${f}.jpg`,await shot(+f))} }
 await b.close();srv.kill();})();
