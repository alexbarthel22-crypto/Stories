// Pichu (Pembroke Corgi): natuerliche Proportionen – kurzer Hals, kurze Beine, langer Koerper.
// Seitenansicht nach links, Fuesse bei y=705. Kein Halsband.
const CG = '#D9944C', CG2 = '#E8B077', CW = '#FFF8EC', CE = '#F2C2A8';

function corgi(o = {}) {
  const tw = o.wag || 0;
  const leg = (x, top, len, col) => `
      <rect x="${x}" y="${top}" width="40" height="${len}" rx="14" fill="${col}" stroke="${K}" stroke-width="7"/>
      <ellipse cx="${x + 16}" cy="${top + len - 4}" rx="28" ry="12" fill="${CW}" stroke="${K}" stroke-width="7"/>`;
  return `
  ${o.noShadow ? '' : '<ellipse cx="290" cy="702" rx="230" ry="16" fill="#000" opacity="0.3"/>'}
  <g transform="rotate(${tw * 12} 476 520)">
    <path d="M470 505 Q540 512 548 590 Q550 650 512 676 Q484 640 474 590 Z" fill="${CG}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M506 600 Q526 646 512 676 Q490 650 482 612 Z" fill="${CW}"/>
  </g>
  ${leg(166, 618, 82, '#EDE2D2')}
  ${leg(430, 618, 82, '#EDE2D2')}
  <path d="M132 500 Q142 462 214 460 L436 460 Q500 466 502 548 Q502 626 446 634 L190 638 Q124 632 122 572 Z" fill="${CG}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M240 480 Q340 468 440 482" stroke="${CG2}" stroke-width="12" fill="none" stroke-linecap="round" opacity=".8"/>
  <path d="M180 624 Q310 650 470 620 L456 634 Q310 660 186 640 Z" fill="${CW}"/>
  <path d="M430 620 Q456 584 494 584 Q498 616 466 632 Z" fill="${CW}" opacity=".9"/>
  <path d="M90 468 Q76 562 128 630 Q182 642 198 592 Q170 540 178 476 Q140 450 90 468 Z" fill="${CW}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  ${leg(130, 616, 86, CW)}
  ${leg(400, 616, 86, CW)}
  <path d="M86 500 Q80 446 112 418 L196 430 Q206 474 186 504 Z" fill="${CG}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M92 504 Q90 462 106 440 Q126 470 132 504 Z" fill="${CW}"/>
  <path d="M138 372 Q146 274 176 254 Q206 302 208 380 Z" fill="${CG}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M154 368 Q160 300 176 278 Q192 310 194 370 Z" fill="${CE}"/>
  <path d="M64 378 Q58 272 90 250 Q128 292 134 372 Z" fill="${CG}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M78 372 Q76 298 92 276 Q114 308 118 370 Z" fill="${CW}"/>
  <ellipse cx="128" cy="420" rx="84" ry="66" fill="${CG}" stroke="${K}" stroke-width="8"/>
  <path d="M116 360 Q124 398 112 440 L142 440 Q132 398 128 358 Z" fill="${CW}"/>
  <path d="M68 428 Q28 436 14 456 Q18 480 64 486 Q118 488 158 464 Q148 436 120 430 Q94 440 68 428 Z" fill="${CW}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <ellipse cx="20" cy="456" rx="17" ry="13" fill="#1A1A1A"/>
  <ellipse cx="16" cy="451" rx="5" ry="3" fill="#777"/>
  <path d="M48 478 Q78 490 104 478" stroke="${K}" stroke-width="6" fill="none" stroke-linecap="round"/>
  ${o.tongue === 0 ? '' : `<path d="M66 482 q4 32 22 28 q14 -4 6 -30z" fill="#F38BA0" stroke="${K}" stroke-width="5"/>`}
  ${o.blink ? `<path d="M74 404 h16 M148 400 h16" stroke="#1A1A1A" stroke-width="5" stroke-linecap="round"/>`
            : `<circle cx="82" cy="404" r="9" fill="#1A1A1A"/><circle cx="156" cy="400" r="9" fill="#1A1A1A"/>`}
  <ellipse cx="178" cy="448" rx="14" ry="8" fill="#F0A0A0" opacity=".7"/>`;
}

// ---------- Vereinskasse: Geldkassette mit Scheinen, Muenzen und Kaugummi ----------
function banknote(x, y, rot, val, s = 1) {
  const col = val === 100 ? ['#7CC47F', '#4E9A52'] : ['#F2A65A', '#C9762E'];
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">
    <rect x="-95" y="-50" width="190" height="100" rx="8" fill="${col[0]}" stroke="#3A2316" stroke-width="6"/>
    <rect x="-84" y="-39" width="168" height="78" rx="5" fill="none" stroke="${col[1]}" stroke-width="3"/>
    <circle cx="-42" cy="0" r="26" fill="${col[1]}" opacity=".45"/>
    <path d="M-60 0 h36 M-42 -18 v36" stroke="#fff" stroke-width="3" opacity=".5"/>
    <text x="48" y="-6" text-anchor="middle" ${FONT} font-size="40" fill="#3A2316">${val}</text>
    <text x="48" y="30" text-anchor="middle" ${FONT} font-size="26" fill="#3A2316">EURO</text>
    <text x="-74" y="-20" ${FONT} font-size="20" fill="#3A2316">€</text></g>`;
}

function coin(x, y, r, two) {
  return `<g transform="translate(${x} ${y})">
    <circle r="${r}" fill="${two ? '#D9D9D9' : '#E8C24A'}" stroke="#3A2316" stroke-width="${r / 6}"/>
    <circle r="${r * 0.62}" fill="${two ? '#E8C24A' : '#D9D9D9'}"/>
    <text y="${r * 0.32}" text-anchor="middle" ${FONT} font-size="${r * 0.9}" fill="#3A2316">${two ? '2' : '1'}</text></g>`;
}

function crownCap(x, y, s) {
  let pts = '';
  for (let i = 0; i < 42; i++) { const r = i % 2 ? 40 : 46, a = i / 42 * Math.PI * 2; pts += `${(Math.cos(a) * r).toFixed(1)},${(Math.sin(a) * r * 0.62).toFixed(1)} `; }
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <polygon points="${pts}" fill="#D9B13A" stroke="#3A2316" stroke-width="5" stroke-linejoin="round"/>
    <ellipse cx="0" cy="-3" rx="32" ry="19" fill="#E5483A" stroke="#3A2316" stroke-width="4"/>
    <ellipse cx="-10" cy="-9" rx="12" ry="5" fill="#fff" opacity=".55"/>
    <text x="0" y="5" text-anchor="middle" ${FONT} font-size="16" fill="#fff">BIER</text></g>`;
}

function cashBox(cx, cy, s, open, t = 0) {
  const lid = open ? `
    <path d="M-220 -40 L-250 -250 L250 -250 L220 -40 Z" fill="#245A39" stroke="#3A2316" stroke-width="10" stroke-linejoin="round"/>
    <path d="M-196 -60 L-220 -228 L220 -228 L196 -60 Z" fill="#1C4A2E"/>
    <rect x="-40" y="-262" width="80" height="22" rx="8" fill="#B8B8B8" stroke="#3A2316" stroke-width="6"/>` : '';
  const money = open ? `
    ${banknote(-110, -110, -14, 100)}${banknote(10, -128, 4, 100)}${banknote(120, -104, 16, 50)}
    ${banknote(-60, -70, -6, 50)}${banknote(70, -66, 8, 50)}
` : '';
  return `<g transform="translate(${cx} ${cy}) scale(${s})">
    ${lid}
    <rect x="-220" y="-50" width="440" height="40" rx="6" fill="#163B25" stroke="#3A2316" stroke-width="8"/>
    ${open ? [-150, -75, 0, 75].map((x, i) => `<rect x="${x - 30}" y="-46" width="60" height="32" fill="#0F2C1B"/>${coin(x, -36, 22, i % 2)}${coin(x + 8, -42, 20, (i + 1) % 2)}`).join('') : ''}
    ${money}
    <path d="M-230 -14 L230 -14 L218 190 Q216 206 200 206 L-200 206 Q-216 206 -218 190 Z" fill="#2E7A4C" stroke="#3A2316" stroke-width="10" stroke-linejoin="round"/>
    <path d="M-214 4 L214 4" stroke="#4FA06D" stroke-width="10" opacity=".7"/>
    ${[[-196, 20], [196, 20], [-190, 180], [190, 180]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="8" fill="#9FC9AE" stroke="#3A2316" stroke-width="3"/>`).join('')}
    <g transform="rotate(-3)"><rect x="-150" y="40" width="300" height="70" rx="6" fill="#FFF8EC" stroke="#3A2316" stroke-width="6"/>
      <text x="0" y="90" text-anchor="middle" ${FONT} font-size="40" fill="#3A2316">VEREINSKASSE</text></g>
    <rect x="-34" y="124" width="68" height="62" rx="10" fill="#E8C24A" stroke="#3A2316" stroke-width="6"/>
    <circle cx="0" cy="148" r="9" fill="#3A2316"/><path d="M-4 150 L-6 172 L6 172 L4 150Z" fill="#3A2316"/>
  </g>`;
}

// Frodo, der Frosch (Maskottchen): sitzend, Frontansicht, Fuesse bei y=705
const FG = '#6CC24A', FG2 = '#58A93A', FB = '#D8F5B0';
function frog(o = {}) {
  const bl = o.blink;
  const sq = o.squash || 0; // Huepf-Stauchung
  const eye = (cx) => `
    <circle cx="${cx}" cy="350" r="64" fill="${FG}" stroke="${K}" stroke-width="8"/>
    ${bl ? `<path d="M${cx - 30} 352 Q${cx} 372 ${cx + 30} 352" stroke="${K}" stroke-width="8" fill="none" stroke-linecap="round"/>`
         : `<circle cx="${cx}" cy="352" r="44" fill="#fff" stroke="${K}" stroke-width="6"/>
            <circle cx="${cx + 6}" cy="358" r="20" fill="#1A1A1A"/><circle cx="${cx + 13}" cy="350" r="7" fill="#fff"/>`}`;
  return `
  <ellipse cx="250" cy="702" rx="170" ry="18" fill="#000" opacity="0.3"/>
  <g transform="translate(250 705) scale(${1 + sq * 0.08} ${1 - sq * 0.08}) translate(-250 -705)">
    <ellipse cx="112" cy="640" rx="66" ry="50" fill="${FG2}" stroke="${K}" stroke-width="8"/>
    <ellipse cx="388" cy="640" rx="66" ry="50" fill="${FG2}" stroke="${K}" stroke-width="8"/>
    <ellipse cx="250" cy="590" rx="148" ry="112" fill="${FG}" stroke="${K}" stroke-width="8"/>
    <ellipse cx="250" cy="618" rx="96" ry="74" fill="${FB}"/>
    <path d="M200 600 q50 14 100 0 M210 636 q40 12 80 0" stroke="#B9E08E" stroke-width="6" fill="none" stroke-linecap="round"/>
    ${[170, 330].map(x => `<ellipse cx="${x}" cy="692" rx="52" ry="20" fill="${FG}" stroke="${K}" stroke-width="7"/>
      <circle cx="${x - 34}" cy="690" r="10" fill="${FG}" stroke="${K}" stroke-width="5"/><circle cx="${x}" cy="700" r="10" fill="${FG}" stroke="${K}" stroke-width="5"/><circle cx="${x + 34}" cy="690" r="10" fill="${FG}" stroke="${K}" stroke-width="5"/>`).join('')}
    <ellipse cx="250" cy="455" rx="172" ry="112" fill="${FG}" stroke="${K}" stroke-width="8"/>
    ${eye(162)}${eye(338)}
    <ellipse cx="146" cy="486" rx="26" ry="14" fill="#F59AAE" opacity=".8"/>
    <ellipse cx="354" cy="486" rx="26" ry="14" fill="#F59AAE" opacity=".8"/>
    <circle cx="230" cy="440" r="5" fill="${FG2}"/><circle cx="270" cy="440" r="5" fill="${FG2}"/>
    ${o.mouth ? `<path d="M196 476 Q250 470 304 476 Q290 524 250 526 Q210 524 196 476 Z" fill="#B23A48" stroke="${K}" stroke-width="7"/><path d="M226 512 Q250 498 274 512 Q250 524 226 512Z" fill="#F38BA0"/>`
              : `<path d="M180 474 Q250 532 320 474" stroke="${K}" stroke-width="9" fill="none" stroke-linecap="round"/>`}
  </g>`;
}
