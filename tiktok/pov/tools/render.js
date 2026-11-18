#!/usr/bin/env node
// Rendert eine vorbereitete Story zu MP4 (oder einzelne Vorschaubilder).
//   node tools/render.js <name>                      -> build/<name>/<name>.mp4
//   node tools/render.js <name> --entwurf            -> halbe Auflösung, schnell
//   node tools/render.js <name> --bilder 0,2.5,7     -> Standbilder bei Sekunde 0 / 2.5 / 7
//   node tools/render.js <name> --von 4 --bis 9      -> nur Ausschnitt
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const name = argv[0];
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i < 0 ? d : argv[i + 1] === undefined || argv[i + 1].startsWith('--') ? true : argv[i + 1]; };
const draft = !!opt('entwurf', false);
const scale = draft ? 0.5 : +opt('scale', 1);
const outDir = path.join(ROOT, 'build', name);

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.wav': 'audio/wav' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(res);
});

(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => { console.error('Fehler im Browser:', e.message); process.exit(1); });
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error('[browser]', m.text()); });
  await page.goto(`http://127.0.0.1:${port}/engine/index.html?story=${encodeURIComponent(name)}&scale=${scale}${opt('flach', false) ? '&flat=' + opt('flach') : ''}`);
  await page.waitForFunction(() => window.READY === true, null, { timeout: 120000 });
  await page.evaluate(() => document.fonts.ready);
  const fps = 30, total = await page.evaluate(() => window.TOTAL_FRAMES);
  const shot = async (f) => { await page.evaluate((f) => window.render(f), f); return page.screenshot({ type: 'jpeg', quality: 93 }); };

  const bilder = opt('bilder', null);
  if (bilder) {
    fs.mkdirSync(path.join(outDir, 'vorschau'), { recursive: true });
    for (const s of String(bilder).split(',')) {
      const f = Math.round(+s * fps), fn = path.join(outDir, 'vorschau', `t${(+s).toFixed(1)}.jpg`);
      fs.writeFileSync(fn, await shot(f)); console.log(fn);
    }
  } else {
    const f0 = Math.round(+opt('von', 0) * fps), f1 = Math.min(total, Math.round(+opt('bis', 1e9) * fps));
    const out = path.join(outDir, opt('aus', `${name}${draft ? '_entwurf' : ''}.mp4`));
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-ss', String(f0 / fps), '-i', path.join(outDir, 'mix.wav'),
      '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
      '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let f = f0; f < f1; f++) {
      const buf = await shot(f);
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if ((f - f0) % 60 === 0) { const el = (Date.now() - t0) / 1000, per = el / (f - f0 + 1); console.log(`Frame ${f}/${f1}  (${per.toFixed(2)} s/Frame, noch ~${Math.round(per * (f1 - f) / 60)} min)`); }
    }
    ff.stdin.end(); await new Promise((r) => ff.on('close', r));
    console.log('Fertig:', out);
  }
  await browser.close(); server.close();
})();
