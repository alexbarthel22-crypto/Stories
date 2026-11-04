// Cooler Sticker fuer Jugendliche: Frodo mit Sonnenbrille, Snapback, Goldkette, Floss-Dance.
// node sticker_cool.js <ordner>  -> 32 transparente PNG-Frames (2 s Loop bei 16 fps)
const {chromium} = require('playwright');
(async () => {
  const out = process.argv[2], N = 32;
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 600, height: 600}});
  await p.goto('file://' + __dirname + '/page.html');
  await p.evaluate(() => { render(0); return document.fonts.ready; });
  await p.addStyleTag({content: 'html,body{background:transparent!important}'});
  for (let i = 0; i < N; i++) {
    await p.evaluate(([i, N]) => {
      UID = 0; PID = 0;
      const ph = i / N, a = ph * Math.PI * 2;
      const beat = Math.abs(Math.sin(a * 2));                  // 4 Beats pro Loop
      const lean = Math.sin(a * 2) * 9;                        // Oberkoerper pendelt
      const bounce = beat * 22;
      const sq = Math.max(0, -Math.cos(a * 4)) * 0.6;
      const swing = Math.sin(a * 2);                           // Floss: Arme schwingen gemeinsam
      const K = '#111', G = '#6CC24A';
      const arm = (sx, side) => {
        const ex = sx + swing * 150 + side * 30, ey = 650 - Math.abs(swing) * 20;
        return `<path d="M${sx} 560 Q${(sx + ex) / 2} ${620} ${ex} ${ey}" stroke="${K}" stroke-width="46" fill="none" stroke-linecap="round"/>
          <path d="M${sx} 560 Q${(sx + ex) / 2} ${620} ${ex} ${ey}" stroke="${G}" stroke-width="32" fill="none" stroke-linecap="round"/>
          <circle cx="${ex}" cy="${ey}" r="26" fill="${G}" stroke="${K}" stroke-width="7"/>`;
      };
      // Accessoires in Frosch-Koordinaten
      const shades = `
        <path d="M96 330 Q162 316 222 330 L214 378 Q162 404 110 378 Z" fill="#141414" stroke="${K}" stroke-width="7"/>
        <path d="M278 330 Q338 316 404 330 L390 378 Q338 404 286 378 Z" fill="#141414" stroke="${K}" stroke-width="7"/>
        <path d="M222 338 Q250 326 278 338" stroke="${K}" stroke-width="10" fill="none"/>
        <path d="M80 336 L98 334 M404 334 L420 336" stroke="${K}" stroke-width="9"/>
        <path d="M120 340 L150 340 L128 368 Z M302 340 L332 340 L310 368 Z" fill="#fff" opacity="${0.35 + 0.4 * beat}"/>`;
      const cap = `
        <path d="M128 352 Q132 214 250 208 Q368 214 372 352 Q250 330 128 352 Z" fill="#2F7FD8" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
        <path d="M250 210 L250 338 M190 222 Q176 280 182 344 M310 222 Q324 280 318 344" stroke="#1F5FAE" stroke-width="5" fill="none"/>
        <path d="M200 346 Q250 296 300 346" fill="#14213D" stroke="${K}" stroke-width="6"/>
        <rect x="234" y="322" width="32" height="16" rx="4" fill="#FFD31A" stroke="${K}" stroke-width="4"/>
        <circle cx="250" cy="210" r="9" fill="#FFD31A" stroke="${K}" stroke-width="4"/>
        <path d="M150 262 Q200 236 236 236" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" opacity=".35"/>`;
      const grin = `<path d="M180 470 Q250 520 330 462" stroke="${K}" stroke-width="10" fill="none" stroke-linecap="round"/>
        <path d="M318 456 l20 -8" stroke="${K}" stroke-width="9" stroke-linecap="round"/>`;
      const chain = `<path d="M150 548 Q250 610 350 548" stroke="#C99A1A" stroke-width="16" fill="none" stroke-dasharray="14 6" stroke-linecap="round"/>
        <path d="M150 548 Q250 610 350 548" stroke="#FFD84A" stroke-width="8" fill="none" stroke-dasharray="14 6" stroke-linecap="round"/>
        <g transform="rotate(${-lean * 1.5} 250 584)"><circle cx="250" cy="612" r="34" fill="#FFD84A" stroke="${K}" stroke-width="6"/>
        <text x="250" y="626" text-anchor="middle" font-family="Noto Color Emoji" font-size="38">⚽</text></g>`;
      let frogSvg = frog({squash: sq}).replace('<ellipse cx="250" cy="702" rx="170" ry="18" fill="#000" opacity="0.3"/>', '');
      // Standard-Mund entfernen, eigenes Grinsen drueber
      frogSvg = frogSvg.replace(/<path d="M180 474 Q250 532 320 474"[^>]*\/>/, '');
      const body = `${arm(150, -1)}${frogSvg}${chain}${grin}${cap}${shades}${arm(350, 1)}`;
      const head = `<g transform="translate(300 ${560 - bounce}) rotate(${lean}) scale(0.72) translate(-250 -705)">${body}</g>`;
      // Bass-Wellen und Neon-Funken
      let fx = '';
      for (let k = 0; k < 2; k++) {
        const q = (ph * 2 + k / 2) % 1;
        fx += `<circle cx="300" cy="330" r="${150 + q * 140}" fill="none" stroke="${k ? '#FF3FA4' : '#2EE6D6'}" stroke-width="${7 * (1 - q)}" opacity="${0.75 * (1 - q)}"/>`;
      }
      const spark = (x, y, s, c) => `<path d="M${x} ${y - 30 * s} L${x + 8 * s} ${y - 8 * s} L${x + 30 * s} ${y} L${x + 8 * s} ${y + 8 * s} L${x} ${y + 30 * s} L${x - 8 * s} ${y + 8 * s} L${x - 30 * s} ${y} L${x - 8 * s} ${y - 8 * s} Z" fill="${c}" stroke="#111" stroke-width="5"/>`;
      const sp = [[110, 160, '#FFD31A', 0], [500, 140, '#2EE6D6', 0.33], [520, 420, '#FF3FA4', 0.66], [80, 440, '#FFD31A', 0.5]];
      let sparks = '';
      sp.forEach(([x, y, c, o]) => { const s = Math.max(0, Math.sin((ph + o) * Math.PI * 4)); if (s > 0.05) sparks += spark(x, y, s * 1.1, c); });
      const svg = document.getElementById('root');
      svg.setAttribute('viewBox', '0 0 600 600'); svg.setAttribute('width', 600); svg.setAttribute('height', 600);
      svg.innerHTML = `<defs><filter id="rand" x="-10%" y="-10%" width="120%" height="120%">
          <feMorphology in="SourceAlpha" operator="dilate" radius="10" result="d"/>
          <feFlood flood-color="#fff"/><feComposite in2="d" operator="in" result="w"/>
          <feMerge><feMergeNode in="w"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
        ${fx}<g filter="url(#rand)">${head}</g><g filter="url(#rand)">${sparks}</g>`;
    }, [i, N]);
    await p.screenshot({path: `${out}/c${String(i).padStart(2, '0')}.png`, omitBackground: true});
  }
  await b.close();
})();
