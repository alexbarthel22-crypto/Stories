// Testbild: node tools/peek.js out.jpg frame [js-vorher] (ONLY=set)
const {chromium} = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
(async () => {
  const [, , out, frame = 0, js = ''] = process.argv;
  const types = {'.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.jpg': 'image/jpeg', '.png': 'image/png', '.json': 'application/json'};
  const srv = http.createServer((req, res) => { const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, {'Content-Type': types[path.extname(p)] || 'application/octet-stream'}); fs.createReadStream(p).pipe(res); });
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const b = await chromium.launch({args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport: {width: 1080, height: 1920}});
  p.on('pageerror', e => console.error('PAGEERR', e.message)); p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('CONSOLE', m.text().slice(0, 400)); });
  await p.goto(`http://127.0.0.1:${srv.address().port}/folge06_gta/src/page.html${process.env.ONLY ? '?only=' + process.env.ONLY : ''}`);
  await p.waitForFunction(() => window.READY === true, null, {timeout: 180000});
  const frames = String(frame).split(',');
  for (const f of frames) {
    const t0 = Date.now();
    await p.evaluate(([f, js]) => { eval(js); window.render(+f); }, [f, js]);
    const o = frames.length > 1 ? out.replace(/(\.\w+)$/, `_${f}$1`) : out;
    fs.writeFileSync(o, await p.screenshot({type: o.endsWith('.png') ? 'png' : 'jpeg', quality: o.endsWith('.png') ? undefined : 90}));
    console.log(o, (Date.now() - t0) + 'ms');
  }
  await b.close(); srv.close();
})();
