#!/usr/bin/env node
// Thumbnail aus einer Story: sauberes Standbild (ohne Untertitel) + großer Titel.
//   node tools/thumbnail.js <name> --bei 32.5 --titel "ER STAND|PLÖTZLICH|NEBEN MIR" --unter "TEIL 1" [--oben "18:30"]
//   "|" = Zeilenumbruch, *Wort* = rot hervorgehoben.  -> build/<name>/thumbnail.jpg
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const name = argv[0];
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i < 0 ? d : argv[i + 1]; };
const bei = +opt('bei', 5), titel = opt('titel', ''), unter = opt('unter', ''), oben = opt('oben', '');
const out = path.join(ROOT, 'build', name, opt('aus', 'thumbnail.jpg'));

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.wav': 'audio/wav' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(res);
});
const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const fmt = (s) => s.split('|').map((l) => esc(l).replace(/\*(.+?)\*/g, '<b>$1</b>')).join('<br>');

(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => { console.error('Fehler im Browser:', e.message); process.exit(1); });
  await page.goto(`http://127.0.0.1:${server.address().port}/engine/index.html?story=${encodeURIComponent(name)}&scale=1`);
  await page.waitForFunction(() => window.READY === true, null, { timeout: 120000 });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate((f) => window.render(f), Math.round(bei * 30));
  await page.evaluate(({ t, u, o }) => {
    document.getElementById('ui').style.display = 'none';
    const d = document.createElement('div');
    d.innerHTML = `<style>
      .th{position:fixed;inset:0;pointer-events:none;font-family:Inter,"Liberation Sans",sans-serif}
      .th .shade{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,transparent 35%,rgba(0,0,0,.55) 100%),linear-gradient(transparent 55%,rgba(0,0,0,.75))}
      .th .t{position:absolute;left:60px;right:60px;bottom:330px;color:#fff;font-weight:900;font-size:118px;line-height:1.02;letter-spacing:-1px;
        text-transform:uppercase;-webkit-text-stroke:10px #000;paint-order:stroke fill;text-shadow:0 8px 0 #000}
      .th .t b{color:#ffd400}
      .th .u{position:absolute;left:60px;bottom:230px;background:#e1251b;color:#fff;font-weight:900;font-size:54px;padding:10px 26px;letter-spacing:4px;border-radius:10px}
      .th .o{position:absolute;right:56px;top:120px;background:rgba(0,0,0,.7);color:#fff;font-weight:800;font-size:64px;padding:12px 28px;border-radius:14px;border:4px solid #e1251b}
    </style><div class="th"><div class="shade"></div><div class="t">${t}</div>${u ? `<div class="u">${u}</div>` : ''}${o ? `<div class="o">${o}</div>` : ''}</div>`;
    document.body.appendChild(d);
  }, { t: fmt(titel), u: esc(unter), o: esc(oben) });
  fs.writeFileSync(out, await page.screenshot({ type: 'jpeg', quality: 92 }));
  console.log(out);
  await browser.close(); server.close();
})();
