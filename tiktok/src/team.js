// Pichu (Pembroke Corgi nach Fotos): rotgold, weisse Brust/Beine/Schnauze/Blesse,
// langer Koerper, kurze Beine, grosse Stehohren, buschiger Schwanz. Seitenansicht nach links, Fuesse y=705.
const CG = '#D9944C', CG2 = '#E8B077', CW = '#FFF8EC', CE = '#F2C2A8';

function corgi(o = {}) {
  const tw = o.wag || 0;
  const eyeR = o.blink ? 3 : 19;
  const mud = o.mud ? `<g fill="#5A3B22" opacity=".9">
      <path d="M200 470 q30 -20 60 0 q10 24 -24 28 q-36 0 -36 -28z"/><path d="M330 520 q20 -14 40 0 q6 18 -18 18 q-24 0 -22 -18z"/>
      <path d="M120 560 q14 -10 28 0 q4 14 -14 14 q-16 0 -14 -14z"/><path d="M280 590 q18 -8 30 4 q2 12 -14 10z"/>
      <circle cx="70" cy="330" r="10"/><circle cx="150" cy="390" r="12"/></g>` : '';
  const legKick = o.kick || 0;
  const leg = (x, top, len, col, dx) => `<g transform="rotate(${dx} ${x + 19} ${top})">
      <rect x="${x}" y="${top}" width="38" height="${len}" rx="14" fill="${col}" stroke="${K}" stroke-width="7"/>
      <ellipse cx="${x + 16}" cy="${top + len - 4}" rx="27" ry="13" fill="${CW}" stroke="${K}" stroke-width="7"/></g>`;
  return `
  ${o.noShadow ? '' : '<ellipse cx="260" cy="702" rx="200" ry="16" fill="#000" opacity="0.3"/>'}
  <g transform="rotate(${tw * 14} 420 500)">
    <path d="M405 490 Q480 500 490 590 Q494 660 456 690 Q426 650 414 590 Z" fill="${CG}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M450 600 Q470 650 456 690 Q432 660 424 610 Z" fill="${CW}"/>
  </g>
  ${leg(150, 590, 108, '#EDE2D2', -legKick)}
  ${leg(372, 590, 108, '#EDE2D2', legKick)}
  <path d="M110 470 Q120 420 200 418 L370 418 Q448 424 450 520 Q450 604 392 612 L176 618 Q104 612 104 540 Z" fill="${CG}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M220 438 Q300 426 390 440" stroke="${CG2}" stroke-width="12" fill="none" stroke-linecap="round" opacity=".8"/>
  <path d="M160 604 Q270 630 420 598 L404 612 Q280 640 170 618 Z" fill="${CW}"/>
  <path d="M370 600 Q400 560 440 560 Q446 600 410 612 Z" fill="${CW}" opacity=".9"/>
  <path d="M74 420 Q52 520 110 600 Q166 618 182 566 Q146 520 152 440 Q120 410 74 420 Z" fill="${CW}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  ${leg(116, 588, 112, CW, legKick * 0.8)}
  ${leg(352, 588, 112, CW, -legKick * 0.8)}
  <path d="M62 470 Q50 380 100 330 L170 330 Q190 400 160 460 Z" fill="${CG}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M70 470 Q66 410 92 380 Q110 420 120 470 Z" fill="${CW}"/>
  <g>
    <path d="M128 300 Q138 200 168 182 Q196 230 196 312 Z" fill="${CG}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
    <path d="M144 296 Q152 228 168 206 Q182 240 182 300 Z" fill="${CE}"/>
    <path d="M58 306 Q52 200 82 178 Q118 220 124 300 Z" fill="${CG}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
    <path d="M72 300 Q70 226 84 204 Q106 236 110 298 Z" fill="${CW}"/>
  </g>
  <ellipse cx="118" cy="352" rx="84" ry="70" fill="${CG}" stroke="${K}" stroke-width="8"/>
  <path d="M106 290 Q114 330 102 372 L132 372 Q122 330 118 288 Z" fill="${CW}"/>
  <path d="M60 360 Q20 368 6 388 Q10 412 56 418 Q110 420 150 396 Q140 368 112 362 Q86 372 60 360 Z" fill="${CW}" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <ellipse cx="12" cy="388" rx="17" ry="13" fill="#1A1A1A"/>
  <ellipse cx="8" cy="383" rx="5" ry="3" fill="#777"/>
  ${o.tongue === 0 ? `<path d="M40 412 Q70 420 96 410" stroke="${K}" stroke-width="6" fill="none" stroke-linecap="round"/>`
                   : `<path d="M40 410 Q70 422 96 410" stroke="${K}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M58 414 q4 34 22 30 q14 -4 6 -32z" fill="#F38BA0" stroke="${K}" stroke-width="5"/>`}
  <circle cx="74" cy="336" r="${eyeR}" fill="#fff" stroke="${K}" stroke-width="6"/>
  <circle cx="148" cy="332" r="${eyeR}" fill="#fff" stroke="${K}" stroke-width="6"/>
  ${o.blink ? '' : `<circle cx="70" cy="339" r="10" fill="#5A3416"/><circle cx="144" cy="335" r="10" fill="#5A3416"/><circle cx="67" cy="335" r="3" fill="#fff"/><circle cx="141" cy="331" r="3" fill="#fff"/>`}
  <ellipse cx="170" cy="380" rx="14" ry="8" fill="#F0A0A0" opacity=".7"/>
  <path d="M62 440 Q110 470 170 446 L174 470 Q112 496 58 466 Z" fill="#2F7FD8" stroke="${K}" stroke-width="6"/>
  <path d="M90 454 v22 M130 456 v22" stroke="#FFD31A" stroke-width="9"/>
  ${mud}`;
}

// Pichu waelzt sich im Schlamm (auf dem Ruecken, Beine strampeln)
function corgiRoll(t) {
  const rot = 180 + Math.sin(t * 7) * 22;
  let spl = '';
  for (let i = 0; i < 8; i++) {
    const ph = (t * 1.6 + rnd(i + 500)) % 1;
    const a = -Math.PI * (0.15 + 0.7 * rnd(i + 600));
    const x = 260 + Math.cos(a) * 260 * ph, y = 690 + Math.sin(a) * 300 * ph + 400 * ph * ph;
    spl += `<circle cx="${x}" cy="${y}" r="${14 * (1 - ph) + 4}" fill="#5A3B22" stroke="${K}" stroke-width="3"/>`;
  }
  return `<ellipse cx="260" cy="700" rx="300" ry="46" fill="#4A3020" stroke="#2C1C12" stroke-width="7"/>
    <g transform="translate(0 -160) rotate(${rot} 260 520)">${corgi({noShadow: true, mud: true, kick: Math.sin(t * 16) * 22, wag: Math.sin(t * 12)})}</g>${spl}`;
}

// ---------- Die restlichen 8 Spieler ----------
const HAIR = {
  mullet: c => `<path d="M100 210 Q100 70 250 70 Q400 70 400 210 Q380 140 250 140 Q120 140 100 210Z" fill="${c}"/>`,
  mulletBack: c => `<path d="M100 220 Q80 330 130 360 L150 250Z M400 220 Q420 330 370 360 L350 250Z" fill="${c}" stroke="${K}" stroke-width="6"/>`,
  bald: () => ``,
  pig: c => `<path d="M100 220 Q100 68 250 68 Q400 68 400 220 Q330 120 250 150 Q170 120 100 220Z" fill="${c}"/>`,
  cap: c => `<path d="M104 170 Q120 66 250 66 Q380 66 396 170 Z" fill="${c}"/>`,
  bun: c => `<path d="M100 200 Q100 74 250 74 Q400 74 400 200 Q330 128 250 136 Q170 128 100 200Z" fill="${c}"/>`,
  afro: c => ``,
  mohawk: c => `<path d="M215 70 L285 70 L282 150 L218 150Z" fill="${c}"/>`,
  curly: c => `<path d="M100 210 Q100 70 250 70 Q400 70 400 210 Q370 150 250 150 Q130 150 100 210Z" fill="${c}"/>`,
};

function roster() {
  return [
    // #7 der Lange mit Vokuhila und Stirnband
    {num: '7', skin: '#F5D3AE', hair: HAIR.mullet('#B5651D'), behind: HAIR.mulletBack('#B5651D'),
     hairOver: `<rect x="112" y="130" width="276" height="26" rx="8" fill="#E8432E" stroke="${K}" stroke-width="6" transform="rotate(-4 250 143)"/>`},
    // #5 der Bulldozer: Glatze, roter Vollbart
    {num: '5', skin: '#F0C49C', hair: `<path d="M110 250 Q122 340 180 356 Q250 384 320 356 Q378 340 390 250 Q380 310 330 318 Q250 296 170 318 Q120 310 110 250Z" fill="#C0501E"/>`,
     hairOver: `<path d="M190 100 q20 -12 40 -4" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" opacity=".6"/>`, mood: 'talk', mouth: .4},
    // #10 die Spielmacherin mit Zoepfen
    {num: '10', skin: '#E9B98F', hair: HAIR.pig('#3A2416'),
     behind: `<circle cx="96" cy="300" r="40" fill="#3A2416" stroke="${K}" stroke-width="7"/><circle cx="404" cy="300" r="40" fill="#3A2416" stroke="${K}" stroke-width="7"/>`,
     hairOver: `<circle cx="112" cy="250" r="12" fill="#FF3FA4" stroke="${K}" stroke-width="4"/><circle cx="388" cy="250" r="12" fill="#FF3FA4" stroke="${K}" stroke-width="4"/>`},
    // #8 der Juengste: Cap und Zahnspange
    {num: '8', skin: '#F5D3AE', hair: HAIR.cap('#E8432E'), mood: 'talk', mouth: .6,
     hairOver: `<path d="M110 168 Q60 168 40 186 L250 186 Z" fill="#E8432E" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>`,
     face: `<path d="M222 312 H278" stroke="#B8B8B8" stroke-width="6"/>`},
    // #6 der Hipster: Dutt, Brille
    {num: '6', skin: '#C98E62', hair: HAIR.bun('#1C1C1C'),
     hairOver: `<circle cx="250" cy="74" r="36" fill="#1C1C1C" stroke="${K}" stroke-width="7"/>`,
     face: `<g fill="none" stroke="${K}" stroke-width="9"><rect x="150" y="180" width="92" height="72" rx="14"/><rect x="258" y="180" width="92" height="72" rx="14"/><path d="M242 206 h16"/></g>`},
    // #11 der Coole: Afro und Sonnenbrille
    {num: '11', skin: '#8D5A3B', hair: '', browCol: '#111',
     behindHead: `<circle cx="250" cy="150" r="170" fill="#1E1410" stroke="${K}" stroke-width="8"/>`,
     eyes: `<path d="M150 192 H350 L340 232 Q300 256 260 232 L250 214 L240 232 Q200 256 160 232 Z" fill="#111" stroke="${K}" stroke-width="5"/><path d="M175 205 l20 -8 M285 205 l20 -8" stroke="#fff" stroke-width="5" opacity=".6"/>`, noBrows: true},
    // #3 der Punk: gruener Irokese
    {num: '3', skin: '#F5D3AE', hair: HAIR.mohawk('#4BD44B'),
     hairOver: `<path d="M220 90 L230 20 L250 80 L262 14 L274 80 L292 30 L284 96" fill="#4BD44B" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>`,
     face: `<circle cx="388" cy="262" r="8" fill="none" stroke="#C0C0C0" stroke-width="5"/>`},
    // #14 der Traeumer: Locken und Kopfhoerer
    {num: '14', skin: '#E6B48A', hair: HAIR.curly('#7A4A22'),
     hairOver: `<path d="M120 90 q20 -30 50 -10 q20 -30 50 -6 q30 -26 60 -2 q30 -22 54 6 q30 -6 40 20" fill="none" stroke="#7A4A22" stroke-width="30" stroke-linecap="round"/>
       <path d="M96 240 Q80 60 250 50 Q420 60 404 240" fill="none" stroke="${K}" stroke-width="16"/>
       <rect x="70" y="200" width="54" height="84" rx="20" fill="#2F7FD8" stroke="${K}" stroke-width="7"/><rect x="376" y="200" width="54" height="84" rx="20" fill="#2F7FD8" stroke="${K}" stroke-width="7"/>`},
  ];
}

function teamPlayer(i, t) {
  const r = roster()[i];
  const o = Object.assign({mood: 'smile', blink: blinkAt(t, i * 0.37)}, r);
  return (r.behindHead || '') + player(o);
}

// 11 Spieler + Trainer + Pichu: zwei Reihen
function fullTeam(t, baseBack, baseFront, s, m, rolling) {
  let back = '', front = '';
  const backRow = [[0, 140], [1, 290], [2, 440], [3, 590], [4, 740], [5, 890]];
  backRow.forEach(([i, x]) => back += place(teamPlayer(i, t), x, baseBack, s * 0.92));
  const fr = [
    [vlad({blink: blinkAt(t, .4)}), 110], [opa({blink: blinkAt(t, 1.1)}), 250],
    [teamPlayer(6, t), 390], [busguy({blink: blinkAt(t, 2)}), 790], [teamPlayer(7, t), 910]];
  fr.forEach(([svg, x]) => front += place(svg, x, baseFront, s));
  front += place(coach({mouth: m, blink: blinkAt(t)}), 590, baseFront + 6, s * 1.1);
  const dog = rolling ? place(corgiRoll(t), 500, baseFront + 130, 0.5)
                      : place(corgi({wag: Math.sin(t * 14), blink: blinkAt(t, 1.7)}), 520, baseFront + 120, 0.4);
  return back + front + dog;
}
