// TikTok-Story (Standbild 1080x1920): Trainer sitzt am Spielfeldrand und liest Kommentare am Handy.
// node story_handy.js <ausgabe.png>
const {chromium} = require('playwright');
(async () => {
  const out = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1080, height: 1920}});
  await p.goto('file://' + __dirname + '/page.html');
  await p.evaluate(() => { render(0); return document.fonts.ready; });
  await p.evaluate(() => {
    UID = 0; PID = 0;
    const t = 0.4, K = '#111';
    // Hintergrund: Schlammplatz mit Tor, vorne Grasstreifen hinter der Seitenlinie
    let s = field(t, 940, {goalX: 760});
    s += `<rect x="0" y="1230" width="1080" height="690" fill="#4A8038"/>`;
    for (let i = 0; i < 26; i++) {
      const x = rnd(i + 1300) * 1080, y = 1260 + rnd(i + 1400) * 640;
      s += `<path d="M${x} ${y} l7 -20 l7 20 l7 -16 l5 16" stroke="#356A2A" stroke-width="5" fill="none" stroke-linejoin="round"/>`;
    }
    s += `<path d="M0 1230 H1080" stroke="#F0EDE0" stroke-width="12"/>`;

    // Trainer sitzend: Beine/Schuhe und Arme aus der Standfigur entfernen, eigene Sitzpose zeichnen
    let c = coach({mood: 'smile', blink: false});
    c = c.replace(/<ellipse cx="250" cy="702"[^>]*\/>/, '')
         .replace(/<rect x="(200|264)" y="590"[^>]*\/>/g, '')
         .replace(/<ellipse cx="(208|292)" cy="690"[^>]*\/>/g, '')
         .replace(/<path d="M208 680[^>]*\/>/, '')
         .replace(/<path d="M175 385 L118 540"[^>]*\/>/g, '')
         .replace(/<circle cx="112" cy="556"[^>]*\/>/, '')
         .replace(/<path d="M325 385 L382 540"[^>]*\/>/g, '')
         .replace(/<circle cx="388" cy="556"[^>]*\/>/, '');
    const legs = `
      <rect x="186" y="560" width="52" height="70" rx="10" fill="#2A2A2E" stroke="${K}" stroke-width="7"/>
      <rect x="262" y="560" width="52" height="70" rx="10" fill="#2A2A2E" stroke="${K}" stroke-width="7"/>
      <rect x="190" y="620" width="40" height="70" fill="#2A2A2E" stroke="${K}" stroke-width="7"/>
      <rect x="270" y="620" width="40" height="70" fill="#2A2A2E" stroke="${K}" stroke-width="7"/>
      <ellipse cx="204" cy="694" rx="36" ry="15" fill="#1A1A1C" stroke="${K}" stroke-width="6"/>
      <ellipse cx="296" cy="694" rx="36" ry="15" fill="#1A1A1C" stroke="${K}" stroke-width="6"/>`;
    // Arme halten das Handy vor der Brust, Handy-Rueckseite zum Betrachter, Display leuchtet aufs Gesicht
    const arms = `
      <path d="M175 390 Q150 480 214 500" stroke="${K}" stroke-width="44" fill="none" stroke-linecap="round"/>
      <path d="M175 390 Q150 480 214 500" stroke="#2F7FD8" stroke-width="30" fill="none" stroke-linecap="round"/>
      <path d="M325 390 Q350 480 286 500" stroke="${K}" stroke-width="44" fill="none" stroke-linecap="round"/>
      <path d="M325 390 Q350 480 286 500" stroke="#2F7FD8" stroke-width="30" fill="none" stroke-linecap="round"/>
      <rect x="208" y="408" width="84" height="140" rx="14" fill="#22252B" stroke="${K}" stroke-width="7" transform="rotate(-4 250 478)"/>
      <circle cx="232" cy="432" r="9" fill="#444" stroke="${K}" stroke-width="3"/>
      <rect x="236" y="470" width="28" height="28" rx="6" fill="#FE2C55" opacity=".9"/>
      <circle cx="216" cy="500" r="22" fill="#F5D3AE" stroke="${K}" stroke-width="7"/>
      <circle cx="284" cy="500" r="22" fill="#F5D3AE" stroke="${K}" stroke-width="7"/>
      <ellipse cx="250" cy="300" rx="120" ry="70" fill="#BFE6FF" opacity=".22"/>`;
    const sitting = `<g transform="translate(250 0) scale(1.45 1) translate(-250 0)">${chair({})}</g>` + `<g transform="translate(0 0)">${legs}${c}${arms}</g>`;
    // Schirm in Vereinsfarben, am Stuhl befestigt
    const umbrella = `
      <path d="M330 600 L330 40" stroke="#555" stroke-width="10"/>
      <path d="M40 120 Q330 -120 620 120 Q560 90 500 120 Q440 88 380 120 Q330 92 280 120 Q220 88 160 120 Q100 90 40 120 Z" fill="#2F7FD8" stroke="${K}" stroke-width="9" stroke-linejoin="round"/>
      <path d="M330 40 Q260 70 280 120 M330 40 Q400 70 380 120 M330 40 Q150 60 160 120 M330 40 Q510 60 500 120" stroke="#FFD31A" stroke-width="7" fill="none"/>
      <circle cx="330" cy="34" r="12" fill="#FFD31A" stroke="${K}" stroke-width="5"/>`;
    s += place(umbrella + sitting, 470, 1700, 1.05);

    // Kommentar-Blasen und Herzen schweben vom Handy hoch
    const bubble = (x, y, sc, emoji) => `<g transform="translate(${x} ${y}) scale(${sc})">
      <path d="M-70 -46 h140 a24 24 0 0 1 24 24 v52 a24 24 0 0 1 -24 24 h-90 l-30 28 v-28 h-20 a24 24 0 0 1 -24 -24 v-52 a24 24 0 0 1 24 -24z" fill="#fff" stroke="#3A2316" stroke-width="7"/>
      <text x="0" y="24" text-anchor="middle" font-family="Noto Color Emoji" font-size="56">${emoji}</text></g>`;
    const heart = (x, y, sc) => `<path transform="translate(${x} ${y}) scale(${sc})" d="M0 -14 c-22 -30 -64 -8 -46 24 l46 46 l46 -46 c18 -32 -24 -54 -46 -24z" fill="#FE2C55" stroke="#3A2316" stroke-width="6"/>`;
    s += bubble(200, 1050, 1.1, '😂') + bubble(860, 1000, 1.0, '⚽') + bubble(150, 1330, 0.85, '🐸') + bubble(900, 1280, 0.9, '🔥');
    s += heart(330, 900, 0.9) + heart(760, 1160, 0.7) + heart(950, 820, 0.6);
    s += rain(t, 140, 0.4);

    // Text
    s += box(110, 300, 860, 330, 'white', 11);
    s += label(540, 405, 'ICH SCHAUE EURE', 74, BROWN) + label(540, 495, 'KOMMENTARE JETZT AN,', 70, BROWN) + `<text x="540" y="585" text-anchor="middle" ${FONT} font-size="66" fill="#E5483A" letter-spacing="1">BIS MORGEN NACHMITTAG!</text>`;
    s += badge(540, 720, '#FCSCHLAMMLOCH', {kind: 'orange', fs: 48, rot: -2});

    document.getElementById('root').innerHTML = `<defs><linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2438"/><stop offset="1" stop-color="#46506A"/></linearGradient>
      <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".4"/></radialGradient></defs>${s}<rect width="1080" height="1920" fill="url(#vig)"/>`;
  });
  await p.screenshot({path: out});
  await b.close();
})();
