// Einzelbilder ohne HUD in voller Qualität (für Thumbnails).
// node src/still.js ordner frame1 frame2 ...
const {chromium} = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
(async () => {
  const [, , out, ...frames] = process.argv;
  const types = {'.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.jpg': 'image/jpeg', '.png': 'image/png'};
  const srv = http.createServer((req, res) => {
    const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, {'Content-Type': types[path.extname(p)] || 'application/octet-stream'}); fs.createReadStream(p).pipe(res);
  });
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport: {width: 1080, height: 1920}});
  await p.goto(`http://127.0.0.1:${srv.address().port}/folge10_fleisch/src/page.html${process.env.ONLY ? '?only=' + process.env.ONLY : ''}`);
  await p.waitForFunction(() => window.READY === true, null, {timeout: 120000});
  fs.mkdirSync(out, {recursive: true});
  for (const f of frames) {
    await p.evaluate(f => { window.render(f); document.querySelectorAll('canvas')[1].style.visibility = 'hidden'; }, +f);
    fs.writeFileSync(`${out}/clean_${f}.png`, await p.screenshot({type: 'png'}));
  }
  await b.close(); srv.close();
})();
