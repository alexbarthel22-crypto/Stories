// Rendert das Video Bild für Bild mit Playwright und gibt es an ffmpeg weiter.
// node render.js out.mp4            -> komplettes Video (ohne Ton: video_stumm.mp4)
// node render.js ordner 0 2700 30   -> Einzelbilder zur Kontrolle
const {chromium} = require('playwright');
const {spawn} = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..'); // dieweltohne/
const FPS = 30, TOTAL = 90 * FPS;

function serve() {
  const types = {'.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.jpg': 'image/jpeg', '.png': 'image/png', '.json': 'application/json'};
  const srv = http.createServer((req, res) => {
    const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, {'Content-Type': types[path.extname(p)] || 'application/octet-stream'});
    fs.createReadStream(p).pipe(res);
  });
  return new Promise(r => srv.listen(0, '127.0.0.1', () => r(srv)));
}

(async () => {
  const [, , out, from = 0, to = TOTAL, step = 1] = process.argv;
  const srv = await serve();
  const url = `http://127.0.0.1:${srv.address().port}/folge10_fleisch/src/page.html${process.env.ONLY ? '?only=' + process.env.ONLY : ''}`;
  const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport: {width: 1080, height: 1920}});
  p.on('pageerror', e => { console.error('PAGEERR', e.message); process.exit(1); });
  p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('CONSOLE', m.text()); });
  await p.goto(url);
  await p.waitForFunction(() => window.READY === true, null, {timeout: 120000});
  const shot = async f => { await p.evaluate(f => window.render(f), f); return p.screenshot({type: 'jpeg', quality: 93}); };
  if (out.endsWith('.mp4')) {
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], {stdio: ['pipe', 'inherit', 'inherit']});
    const t0 = Date.now();
    for (let f = +from; f < +to; f++) {
      const buf = await shot(f);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 150 === 0) console.log('frame', f, '/', to, Math.round((Date.now() - t0) / 1000) + 's');
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  } else {
    fs.mkdirSync(out, {recursive: true});
    for (let f = +from; f < +to; f += +step) fs.writeFileSync(`${out}/f${String(f).padStart(5, '0')}.jpg`, await shot(f));
  }
  await b.close(); srv.close();
})();
