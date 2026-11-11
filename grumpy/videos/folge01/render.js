// Rendert alle SVG-Bilder eines Ordners zu JPEG (für ffmpeg).
// node render.js <svg-ordner> <jpg-ordner> [nur-diese,dateien]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [src, dst, only] = process.argv.slice(2);
  fs.mkdirSync(dst, { recursive: true });
  let files = fs.readdirSync(src).filter(f => f.endsWith('.svg')).sort();
  if (only) files = files.filter(f => only.split(',').includes(f));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.setContent('<html><body style="margin:0"><div id="s"></div></body></html>');
  for (const f of files) {
    const svg = fs.readFileSync(path.join(src, f), 'utf8');
    await p.evaluate(s => { document.getElementById('s').innerHTML = s; }, svg);
    await p.screenshot({ path: path.join(dst, f.replace('.svg', '.jpg')), type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
