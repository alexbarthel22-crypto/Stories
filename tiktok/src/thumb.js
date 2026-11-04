// Thumbnail-Vorlage fuer alle Folgen: node thumb.js <tag> <fans> <kasse_euro> <ausgabe.png>
// Gleiches Design jede Folge: grosser TAG-Kasten, Trainer gross, Fans (rot bei 0, sonst gruen), Vereinskasse gruen.
const {chromium} = require('playwright');
(async () => {
  const [,, tag, fans, kasse, out] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1080, height: 1920}});
  await p.goto('file://' + __dirname + '/page.html');
  await p.evaluate(() => { render(0); return document.fonts.ready; });
  await p.evaluate(([tag, fans, kasse]) => {
    UID = 0; PID = 0;
    const t = 0.3, f = +fans;
    let s = field(t, 1080, {goalX: 820});
    s += `<rect width="1080" height="1920" fill="#000" opacity=".18"/>`;
    // Lichtstrahlen hinter dem Trainer
    for (let i = 0; i < 7; i++) {
      const a = -54 + i * 18;
      s += `<path d="M540 1100 L${540 + Math.tan(a * Math.PI / 180) * 1100 - 70} 0 L${540 + Math.tan(a * Math.PI / 180) * 1100 + 70} 0 Z" fill="#FFF3B0" opacity=".10"/>`;
    }
    // Fussball liegt hinten links auf dem Platz
    s += `<ellipse cx="190" cy="1176" rx="46" ry="11" fill="#000" opacity=".3"/>${ballIcon(190, 1140, 40)}
      <path d="M152 1160 q20 10 40 4 q-8 12 -30 8z" fill="#6B4226"/>`;
    s += place(coach({mouth: 0.9}), 540, 1600, 1.45);
    s += rain(t, 110, 0.35);
    // TAG oben
    s += badge(540, 450, 'TAG ' + tag, {kind: 'pitch', fs: 200, pad: 110});
    s += badge(540, 632, 'FC SCHLAMMLOCH', {kind: 'orange', fs: 58});
    // Stat-Kaesten unten (oberhalb der Beschreibungszone)
    const fansCol = f === 0 ? 'red' : 'pitch';
    s += `<g transform="rotate(-4 300 1390)">${box(90, 1280, 420, 230, fansCol, 12)}
      ${label(300, 1360, 'FANS', 62, '#fff')}${label(300, 1478, String(f), 120, '#fff')}</g>`;
    s += `<g transform="rotate(3 775 1390)">${box(570, 1280, 420, 230, 'pitch', 12)}
      ${label(780, 1360, 'VEREINSKASSE', 50, '#fff')}${label(780, 1478, kasse + ' €', 104, '#fff')}</g>`;
    document.getElementById('root').innerHTML = `<defs><linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2438"/><stop offset="1" stop-color="#46506A"/></linearGradient></defs>${s}`;
  }, [tag, fans, kasse]);
  await p.screenshot({path: out});
  await b.close();
})();
