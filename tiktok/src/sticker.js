// Animierter Sticker: Frodo tanzt. node sticker.js <ordner> -> transparente PNG-Frames
const {chromium} = require('playwright');
(async () => {
  const out = process.argv[2], N = 24;
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 600, height: 600}});
  await p.goto('file://' + __dirname + '/page.html');
  await p.evaluate(() => { render(0); return document.fonts.ready; });
  await p.addStyleTag({content: 'html,body{background:transparent!important}'});
  for (let i = 0; i < N; i++) {
    await p.evaluate(([i, N]) => {
      UID = 0; PID = 0;
      const ph = i / N, a = ph * Math.PI * 2;
      const sway = Math.sin(a) * 10;                          // Hueftschwung
      const hop = Math.abs(Math.sin(a * 2)) * 34;             // zwei Huepfer pro Takt
      const sq = Math.max(0, -Math.cos(a * 2)) * 0.9;         // Stauchen beim Landen
      const armL = Math.sin(a * 2) * 50, armR = -Math.sin(a * 2 + 1) * 50;
      const arm = (sx, ang, side) => {
        const len = 120, ex = sx + side * Math.cos(ang * Math.PI / 180) * len, ey = 560 - Math.sin(ang * Math.PI / 180) * len;
        return `<path d="M${sx} 560 L${ex} ${ey}" stroke="#111" stroke-width="46" stroke-linecap="round"/>
          <path d="M${sx} 560 L${ex} ${ey}" stroke="#6CC24A" stroke-width="32" stroke-linecap="round"/>
          <circle cx="${ex}" cy="${ey}" r="26" fill="#6CC24A" stroke="#111" stroke-width="7"/>
          <circle cx="${ex + side * 18}" cy="${ey - 18}" r="10" fill="#6CC24A" stroke="#111" stroke-width="5"/>
          <circle cx="${ex + side * 26}" cy="${ey}" r="10" fill="#6CC24A" stroke="#111" stroke-width="5"/>`;
      };
      const body = `${arm(140, 40 + armL, -1)}${arm(360, 40 + armR, 1)}${frog({mouth: true, squash: sq, blink: i === 15}).replace('<ellipse cx="250" cy="702" rx="170" ry="18" fill="#000" opacity="0.3"/>', '')}`;
      const frogG = `<g transform="translate(300 ${560 - hop}) rotate(${sway}) scale(0.74) translate(-250 -705)">${body}</g>`;
      let notes = '';
      for (let k = 0; k < 3; k++) {
        const q = (ph + k / 3) % 1, x = k % 2 ? 500 + q * 30 : 100 - q * 30, y = 280 - q * 170;
        notes += `<text x="${x}" y="${y}" text-anchor="middle" font-family="Lilita" font-size="${70 - q * 20}" fill="${['#FFD31A', '#F28A2E', '#2F7FD8'][k]}" stroke="#3A2316" stroke-width="7" paint-order="stroke" transform="translate(${x} ${y}) scale(${q < 0.8 ? 1 : (1 - q) * 5}) rotate(${Math.sin(q * 6) * 15}) translate(${-x} ${-y})">${k === 1 ? '♫' : '♪'}</text>`;
      }
      const shadow = `<ellipse cx="300" cy="528" rx="${110 - hop * 1.2}" ry="16" fill="#000" opacity="${0.22 - hop / 400}"/>`;
      const svg = document.getElementById('root');
      svg.setAttribute('viewBox', '0 0 600 600'); svg.setAttribute('width', 600); svg.setAttribute('height', 600);
      svg.innerHTML = `<defs><filter id="rand" x="-10%" y="-10%" width="120%" height="120%">
          <feMorphology in="SourceAlpha" operator="dilate" radius="10" result="d"/>
          <feFlood flood-color="#fff"/><feComposite in2="d" operator="in" result="w"/>
          <feMerge><feMergeNode in="w"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
        <g filter="url(#rand)">${frogG}</g><g filter="url(#rand)">${notes}</g>`;
    }, [i, N]);
    await p.screenshot({path: `${out}/s${String(i).padStart(2, '0')}.png`, omitBackground: true});
  }
  await b.close();
})();
