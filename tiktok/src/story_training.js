// TikTok-Story (Standbild 1080x1920): Chaos-Training des FC Schlammloch. node story_training.js <ausgabe.png>
const {chromium} = require('playwright');
(async () => {
  const out = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1080, height: 1920}});
  await p.goto('file://' + __dirname + '/page.html');
  await p.evaluate(() => { render(0); return document.fonts.ready; });
  await p.evaluate(() => {
    UID = 0; PID = 0;
    const t = 0.6;
    const rot = (svg, x, y, deg) => `<g transform="rotate(${deg} ${x} ${y})">${svg}</g>`;
    const splash = (x, y, s = 1) => [[-40, -30, 14], [30, -45, 10], [55, -10, 8], [-60, 5, 9], [5, -60, 7]]
      .map(([dx, dy, r]) => `<circle cx="${x + dx * s}" cy="${y + dy * s}" r="${r * s}" fill="#5A3B22" stroke="#111" stroke-width="3"/>`).join('');
    const stars = (x, y) => [0, 1, 2].map(k => { const a = k * 2.1; return `<text x="${x + Math.cos(a) * 46}" y="${y + Math.sin(a) * 16}" text-anchor="middle" ${FONT} font-size="40" fill="#FFD31A" stroke="#3A2316" stroke-width="5" paint-order="stroke">★</text>`; }).join('')
      + `<ellipse cx="${x}" cy="${y}" rx="52" ry="18" fill="none" stroke="#FFD31A" stroke-width="4" stroke-dasharray="8 8"/>`;
    const motion = (x, y) => `<g stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".8"><path d="M${x - 70} ${y + 30} l-60 30"/><path d="M${x - 60} ${y + 55} l-50 25"/><path d="M${x - 80} ${y + 5} l-45 22"/></g>`;

    let s = field(t, 900, {goalX: 520, puddles: [[200, 1260, 210, 40], [760, 1180, 150, 26], [520, 1470, 220, 42], [120, 1420, 130, 22]]});
    // Ball schlaegt oben rechts ein, Vlad fliegt in die andere Ecke
    s += place(vlad({mood: 'sad'}), 330, 1010, 0.42).replace('<g transform="translate(330 1010)', '<g transform="translate(330 1010) rotate(-72)');
    s += splash(300, 1000, 0.8);
    s += motion(640, 830) + `<g transform="translate(640 830) rotate(30)">${ballIcon(0, 0, 30)}</g>`;
    // #5 und #3 zusammengestossen
    s += rot(place(teamPlayer(1, t), 690, 1240, 0.46), 690, 1180, 18) + rot(place(teamPlayer(6, t), 830, 1240, 0.46), 830, 1180, -18);
    s += stars(700, 1000) + stars(830, 1000);
    s += `<text x="765" y="935" text-anchor="middle" ${FONT} font-size="60" fill="#fff" stroke="#3A2316" stroke-width="10" paint-order="stroke">BONK</text>`;
    // Opa Juergen liegt in der Pfuetze, Gehstock fliegt weg
    s += rot(place(opa({mood: 'sad'}), 190, 1290, 0.5), 190, 1210, 82);
    s += `<path d="M70 1060 L140 1130" stroke="#7A4E2C" stroke-width="12" stroke-linecap="round"/>` + splash(220, 1230, 1.1);
    // Bus-Typ rutscht aus, ein Flip-Flop fliegt
    s += rot(place(busguy({mood: 'sad'}), 520, 1490, 0.5), 520, 1380, -32);
    s += `<g transform="translate(640 1230) rotate(-35)"><ellipse rx="34" ry="11" fill="#FF3FA4" stroke="#111" stroke-width="6"/><path d="M-10 -4 L4 -14 L16 -4" stroke="#FFD31A" stroke-width="6" fill="none"/></g>` + splash(560, 1470, 0.9);
    // Seitenrand vorne rechts mit dem Trainer (Facepalm, Klemmbrett)
    s += `<path d="M560 1920 L1080 1470 L1080 1920 Z" fill="#4A8038"/><path d="M560 1920 L1080 1470" stroke="#F0EDE0" stroke-width="12"/>`;
    const facepalm = `<path d="M325 385 L300 260" stroke="#111" stroke-width="44" stroke-linecap="round"/>
      <path d="M325 385 L300 260" stroke="#2F7FD8" stroke-width="30" stroke-linecap="round"/>
      <ellipse cx="290" cy="232" rx="40" ry="32" fill="#F5D3AE" stroke="#111" stroke-width="7"/>
      <path d="M262 214 h50 M262 232 h54 M266 250 h46" stroke="#D8AE88" stroke-width="5"/>
      <g transform="rotate(-12 110 520)"><rect x="60" y="470" width="110" height="140" rx="10" fill="#A8743F" stroke="#111" stroke-width="7"/>
      <rect x="74" y="490" width="82" height="108" fill="#fff"/><path d="M84 512 h56 M84 532 h40 M84 552 h56 M84 572 h30" stroke="#999" stroke-width="5"/>
      <rect x="96" y="460" width="38" height="20" rx="4" fill="#C9C9C9" stroke="#111" stroke-width="5"/></g>`;
    s += place(coach({mood: 'sad'}) + facepalm, 870, 1830, 0.78);
    s += rain(t, 150, 0.4);
    // Texte (Story-Sicherheitsbereich: oben ~250 px, unten ~260 px frei)
    s += badge(540, 330, 'TRAINING', {kind: 'pitch', fs: 110, pad: 80});
    s += badge(540, 470, 'LÄUFT BEI UNS.', {fs: 46, rot: -3});
    s += badge(540, 600, '▶ VIDEO 1 IST ONLINE', {kind: 'red', fs: 48, rot: 2});
    s += badge(300, 1560, '+1 € PRO FOLLOWER', {kind: 'pitch', fs: 40, rot: -2});
    s += badge(300, 1650, '+2 € PRO KOMMENTAR', {kind: 'orange', fs: 40, rot: 2});
    document.getElementById('root').innerHTML = `<defs><linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2438"/><stop offset="1" stop-color="#46506A"/></linearGradient>
      <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient></defs>${s}<rect width="1080" height="1920" fill="url(#vig)"/>`;
  });
  await p.screenshot({path: out});
  await b.close();
})();
