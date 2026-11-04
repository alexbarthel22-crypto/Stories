const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
(async()=>{
 const [,, out, from, to, step] = process.argv;
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>{console.error('PAGEERR',e.message);process.exit(1)});
 await p.goto('file://'+__dirname+'/page.html');
 const data=JSON.parse(fs.readFileSync(__dirname+'/data.json'));
 const nf=data.env.length;
 if(out.endsWith('.mp4')){
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','30','-i','-','-i',__dirname+'/mix.wav','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<nf;f++){await p.evaluate(f=>render(f),f);const buf=await p.screenshot({type:'jpeg',quality:92});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); if(f%300==0) console.log('frame',f,'/',nf);}
  ff.stdin.end(); await new Promise(r=>ff.on('close',r));
 } else {
  for(let f=+from;f<+to;f+=+step){await p.evaluate(f=>render(f),f);await p.screenshot({path:`${out}/f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:80});}
 }
 await b.close();})();
