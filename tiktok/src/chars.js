// Figuren im Stil des Avatars. Lokales Koordinatensystem 500x740, Fuesse bei y=705.
const K = '#111';
let UID = 0;

function place(svg, x, footY, s, flip) {
  const fx = flip ? -1 : 1;
  return `<g transform="translate(${x} ${footY}) scale(${s * fx} ${s}) translate(-250 -705)">${svg}</g>`;
}

function mouthSvg(m, mood, cx = 250, y = 300) {
  if (mood === 'sad') {
    return `<path d="M${cx - 32} ${y + 28} Q${cx} ${y + 2} ${cx + 32} ${y + 28}" stroke="${K}" stroke-width="9" fill="none" stroke-linecap="round"/>`;
  }
  if (mood === 'smile') {
    return `<path d="M${cx - 34} ${y + 6} Q${cx} ${y + 34} ${cx + 34} ${y + 6}" stroke="${K}" stroke-width="9" fill="none" stroke-linecap="round"/>`;
  }
  const h = 14 + 30 * m;
  return `<path d="M${cx - 35} ${y} Q${cx} ${y - 2} ${cx + 35} ${y} Q${cx + 31} ${y + h} ${cx} ${y + h + 2} Q${cx - 31} ${y + h} ${cx - 35} ${y} Z" fill="#8E1E1E" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M${cx - 16} ${y + h - 6} Q${cx} ${y + h - 18} ${cx + 16} ${y + h - 6} Q${cx} ${y + h + 1} ${cx - 16} ${y + h - 6} Z" fill="#F38BA0"/>`;
}

function eyesSvg(o) {
  const blink = o.blink ? 0.12 : 1;
  const px = o.look || 0;
  let s = '';
  for (const ex of [195, 305]) {
    s += `<g transform="translate(${ex} 215) scale(1 ${blink}) translate(${-ex} -215)">
      <circle cx="${ex}" cy="215" r="36" fill="#fff" stroke="${K}" stroke-width="8"/>
      <circle cx="${ex + 3 + px}" cy="217" r="12" fill="${K}"/></g>`;
  }
  return s;
}

function browsSvg(mood, col) {
  if (mood === 'sad') {
    return `<path d="M168 172 Q195 160 222 150" stroke="${col}" stroke-width="11" fill="none" stroke-linecap="round"/>
            <path d="M278 150 Q305 160 332 172" stroke="${col}" stroke-width="11" fill="none" stroke-linecap="round"/>`;
  }
  return `<path d="M168 168 Q195 152 222 166" stroke="${col}" stroke-width="11" fill="none" stroke-linecap="round"/>
          <path d="M278 166 Q305 152 332 168" stroke="${col}" stroke-width="11" fill="none" stroke-linecap="round"/>`;
}

// ---------- Cheftrainer (der Avatar) ----------
function coach(o = {}) {
  const id = 'c' + (UID++);
  const m = o.mouth || 0, mood = o.mood || 'talk';
  const armR = o.wave
    ? `<path d="M325 385 L398 ${300 - o.wave * 20}" stroke="${K}" stroke-width="44" stroke-linecap="round"/>
       <path d="M325 385 L398 ${300 - o.wave * 20}" stroke="#2F7FD8" stroke-width="30" stroke-linecap="round"/>
       <circle cx="402" cy="${288 - o.wave * 20}" r="22" fill="#F5D3AE" stroke="${K}" stroke-width="7"/>`
    : `<path d="M325 385 L382 540" stroke="${K}" stroke-width="44" stroke-linecap="round"/>
       <path d="M325 385 L382 540" stroke="#2F7FD8" stroke-width="30" stroke-linecap="round"/>
       <circle cx="388" cy="556" r="22" fill="#F5D3AE" stroke="${K}" stroke-width="7"/>`;
  return `
  <ellipse cx="250" cy="702" rx="140" ry="20" fill="#000" opacity="0.3"/>
  <rect x="200" y="590" width="36" height="96" fill="#2A2A2E" stroke="${K}" stroke-width="7"/>
  <rect x="264" y="590" width="36" height="96" fill="#2A2A2E" stroke="${K}" stroke-width="7"/>
  <ellipse cx="208" cy="690" rx="34" ry="15" fill="#1A1A1C" stroke="${K}" stroke-width="6"/>
  <ellipse cx="292" cy="690" rx="34" ry="15" fill="#1A1A1C" stroke="${K}" stroke-width="6"/>
  <path d="M208 680 q10 -10 22 -2 q4 10 -8 10z M282 682 q10 -8 18 0 q2 8 -8 8z" fill="#6B4226"/>
  <path d="M175 385 L118 540" stroke="${K}" stroke-width="44" stroke-linecap="round"/>
  <path d="M175 385 L118 540" stroke="#2F7FD8" stroke-width="30" stroke-linecap="round"/>
  <circle cx="112" cy="556" r="22" fill="#F5D3AE" stroke="${K}" stroke-width="7"/>
  ${armR}
  <path d="M175 360 L325 360 Q340 362 340 380 L346 600 L154 600 L160 380 Q160 362 175 360 Z" fill="#2F7FD8" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M250 360 V600" stroke="${K}" stroke-width="7"/>
  <rect x="157" y="462" width="186" height="18" fill="#1F3E66" stroke="${K}" stroke-width="6"/>
  <rect x="172" y="336" width="156" height="40" rx="18" fill="#1F3E66" stroke="${K}" stroke-width="8"/>
  <path d="M206 340 V372 M232 338 V374 M268 338 V374 M294 340 V372" stroke="#2F7FD8" stroke-width="9"/>
  <rect x="280" y="392" width="34" height="56" rx="6" fill="#2F7FD8" stroke="${K}" stroke-width="6"/>
  <path d="M284 408 H310 M284 424 H310" stroke="${K}" stroke-width="5"/>
  <path d="M212 372 Q214 420 232 466" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/>
  <rect x="216" y="462" width="34" height="22" rx="7" fill="#fff" stroke="${K}" stroke-width="5"/>
  <path d="M190 560 q10 -8 18 0 q2 10 -8 10 q-10 0 -10 -10z M300 540 q8 -6 14 0 q2 8 -6 8z" fill="#6B4226" stroke="${K}" stroke-width="3"/>
  <defs><clipPath id="${id}"><circle cx="250" cy="225" r="140"/></clipPath></defs>
  <circle cx="112" cy="235" r="24" fill="#F5D3AE" stroke="${K}" stroke-width="7"/>
  <circle cx="388" cy="235" r="24" fill="#F5D3AE" stroke="${K}" stroke-width="7"/>
  <circle cx="250" cy="225" r="140" fill="#F5D3AE"/>
  <g clip-path="url(#${id})">
    <path d="M100 215 Q100 70 250 70 Q400 70 400 215 Q392 165 335 150 Q265 172 195 138 Q130 158 100 215 Z" fill="#2B1D16"/>
    <path d="M110 240 Q122 330 180 352 Q250 382 320 352 Q378 330 390 240 Q380 300 330 310 Q300 292 250 292 Q200 292 170 310 Q120 300 110 240 Z" fill="#3A2A20"/>
  </g>
  <circle cx="250" cy="225" r="140" fill="none" stroke="${K}" stroke-width="8"/>
  ${browsSvg(mood, '#2B1D16')}
  ${eyesSvg(o)}
  <ellipse cx="148" cy="270" rx="22" ry="12" fill="#F0A0A0" opacity="0.7"/>
  <ellipse cx="352" cy="270" rx="22" ry="12" fill="#F0A0A0" opacity="0.7"/>
  ${mouthSvg(m, mood, 250, 300)}`;
}

// ---------- Generischer Spieler ----------
function player(o) {
  const id = 'p' + (UID++);
  const skin = o.skin || '#F5D3AE';
  const jersey = o.jersey || '#2F7FD8', trim = o.trim || '#FFD31A';
  const handR = o.gloves ? `<circle cx="386" cy="520" r="30" fill="#F2F2F2" stroke="${K}" stroke-width="7"/><path d="M366 506 h40" stroke="#E8432E" stroke-width="8"/>`
                         : `<circle cx="384" cy="516" r="22" fill="${skin}" stroke="${K}" stroke-width="7"/>`;
  const handL = o.gloves ? `<circle cx="114" cy="520" r="30" fill="#F2F2F2" stroke="${K}" stroke-width="7"/><path d="M94 506 h40" stroke="#E8432E" stroke-width="8"/>`
                         : `<circle cx="116" cy="516" r="22" fill="${skin}" stroke="${K}" stroke-width="7"/>`;
  const feet = o.flipflops
    ? `<ellipse cx="212" cy="696" rx="34" ry="10" fill="#FF3FA4" stroke="${K}" stroke-width="6"/>
       <ellipse cx="290" cy="696" rx="34" ry="10" fill="#FF3FA4" stroke="${K}" stroke-width="6"/>
       <ellipse cx="212" cy="684" rx="26" ry="12" fill="${skin}" stroke="${K}" stroke-width="6"/>
       <ellipse cx="290" cy="684" rx="26" ry="12" fill="${skin}" stroke="${K}" stroke-width="6"/>
       <path d="M200 690 L214 676 L226 690 M278 690 L292 676 L304 690" stroke="#FFD31A" stroke-width="6" fill="none" stroke-linecap="round"/>`
    : `<ellipse cx="208" cy="690" rx="34" ry="15" fill="${o.shoe || '#1A1A1C'}" stroke="${K}" stroke-width="6"/>
       <ellipse cx="292" cy="690" rx="34" ry="15" fill="${o.shoe || '#1A1A1C'}" stroke="${K}" stroke-width="6"/>`;
  const legs = o.flipflops
    ? `<rect x="198" y="580" width="30" height="104" fill="${skin}" stroke="${K}" stroke-width="7"/>
       <rect x="272" y="580" width="30" height="104" fill="${skin}" stroke="${K}" stroke-width="7"/>`
    : `<rect x="198" y="580" width="30" height="40" fill="${skin}" stroke="${K}" stroke-width="7"/>
       <rect x="272" y="580" width="30" height="40" fill="${skin}" stroke="${K}" stroke-width="7"/>
       <rect x="196" y="616" width="34" height="70" fill="${o.socks || '#fff'}" stroke="${K}" stroke-width="7"/>
       <rect x="270" y="616" width="34" height="70" fill="${o.socks || '#fff'}" stroke="${K}" stroke-width="7"/>`;
  return `
  <ellipse cx="250" cy="702" rx="130" ry="18" fill="#000" opacity="0.3"/>
  ${legs}${feet}
  ${o.behind || ''}
  <path d="M178 380 L124 500" stroke="${K}" stroke-width="40" stroke-linecap="round"/>
  <path d="M178 380 L124 500" stroke="${skin}" stroke-width="26" stroke-linecap="round"/>
  <path d="M322 380 L376 500" stroke="${K}" stroke-width="40" stroke-linecap="round"/>
  <path d="M322 380 L376 500" stroke="${skin}" stroke-width="26" stroke-linecap="round"/>
  <path d="M180 360 L150 420 L176 432" stroke="${K}" stroke-width="8" fill="${jersey}" stroke-linejoin="round"/>
  <path d="M320 360 L350 420 L324 432" stroke="${K}" stroke-width="8" fill="${jersey}" stroke-linejoin="round"/>
  ${handL}${handR}
  <path d="M182 358 L318 358 L332 540 L168 540 Z" fill="${jersey}" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M214 358 Q250 392 286 358" fill="${trim}" stroke="${K}" stroke-width="6"/>
  <rect x="166" y="530" width="168" height="58" rx="6" fill="${o.shorts || '#1F3E66'}" stroke="${K}" stroke-width="7"/>
  <path d="M250 548 V588" stroke="${K}" stroke-width="6"/>
  <text x="250" y="500" text-anchor="middle" font-family="Lilita" font-size="90" fill="${trim}" stroke="${K}" stroke-width="7" paint-order="stroke">${o.num || ''}</text>
  ${o.front || ''}
  <defs><clipPath id="${id}"><circle cx="250" cy="225" r="140"/></clipPath></defs>
  <circle cx="112" cy="235" r="24" fill="${skin}" stroke="${K}" stroke-width="7"/>
  <circle cx="388" cy="235" r="24" fill="${skin}" stroke="${K}" stroke-width="7"/>
  <circle cx="250" cy="225" r="140" fill="${skin}"/>
  <g clip-path="url(#${id})">${o.hair || ''}</g>
  <circle cx="250" cy="225" r="140" fill="none" stroke="${K}" stroke-width="8"/>
  ${o.hairOver || ''}
  ${o.noBrows ? '' : browsSvg(o.mood, o.browCol || '#2B1D16')}
  ${o.eyes || eyesSvg(o)}
  <ellipse cx="148" cy="270" rx="22" ry="12" fill="#F0A0A0" opacity="0.7"/>
  <ellipse cx="352" cy="270" rx="22" ry="12" fill="#F0A0A0" opacity="0.7"/>
  ${o.face || ''}
  ${mouthSvg(o.mouth || 0, o.mood || 'smile', 250, o.mouthY || 300)}
  ${o.top || ''}`;
}

// Vlad: Torwart mit Augenklappe
function vlad(o = {}) {
  const blink = o.blink ? 0.12 : 1;
  return player(Object.assign({
    jersey: '#2FB34A', trim: '#111', num: '1', shorts: '#111', socks: '#2FB34A', gloves: true, browCol: '#111',
    hair: `<path d="M100 200 Q110 72 250 72 Q390 72 400 200 Q360 120 250 128 Q150 120 100 200 Z" fill="#141414"/>
           <path d="M120 260 Q140 330 250 352 Q360 330 380 260 L380 400 L120 400Z" fill="#9A8A80" opacity="0.35"/>`,
    eyes: `<g transform="translate(305 215) scale(1 ${blink}) translate(-305 -215)">
             <circle cx="305" cy="215" r="36" fill="#fff" stroke="${K}" stroke-width="8"/>
             <circle cx="300" cy="217" r="12" fill="${K}"/></g>
           <path d="M112 150 L260 196" stroke="${K}" stroke-width="9"/>
           <path d="M150 250 L388 120" stroke="${K}" stroke-width="0"/>
           <path d="M158 196 Q195 170 232 196 L226 248 Q195 262 164 248 Z" fill="#111" stroke="${K}" stroke-width="6"/>
           <path d="M232 196 L372 120" stroke="${K}" stroke-width="8"/>`,
    mood: o.mood || 'smile',
  }, o));
}

// Opa Juergen: Verteidiger, 79
function opa(o = {}) {
  return player(Object.assign({
    jersey: '#2F7FD8', trim: '#FFD31A', num: '4', shorts: '#1F3E66', socks: '#fff', skin: '#F2CCA6', browCol: '#E8E8E8',
    hair: `<path d="M100 260 Q100 160 140 150 Q150 200 130 260Z" fill="#EDEDED"/><path d="M400 260 Q400 160 360 150 Q350 200 370 260Z" fill="#EDEDED"/>
           <path d="M200 120 q20 -10 40 0 M260 110 q20 -8 36 4" stroke="#D8B48E" stroke-width="5" fill="none"/>`,
    hairOver: `<path d="M240 86 q-6 -26 10 -32 q4 18 -10 32z" fill="#EDEDED" stroke="${K}" stroke-width="5"/>`,
    face: `<g fill="none">
             <circle cx="195" cy="215" r="48" stroke="${K}" stroke-width="10"/><circle cx="305" cy="215" r="48" stroke="${K}" stroke-width="10"/>
             <path d="M243 210 Q250 202 257 210" stroke="${K}" stroke-width="9"/></g>
           <path d="M200 292 Q225 268 250 286 Q275 268 300 292 Q300 318 270 310 Q250 300 230 310 Q200 318 200 292Z" fill="#F4F4F4" stroke="${K}" stroke-width="6"/>
           <path d="M150 175 q10 -6 20 0 M330 175 q10 -6 20 0" stroke="#C99E7C" stroke-width="4" fill="none"/>`,
    mouthY: 322, mood: o.mood || 'smile',
    front: `<path d="M120 500 L96 700" stroke="#7A4E2C" stroke-width="16" stroke-linecap="round"/><path d="M120 500 L96 700" stroke="${K}" stroke-width="4" opacity=".4"/>`,
  }, o));
}

// Der Typ, der den Bus verpasst hat
function busguy(o = {}) {
  const lid = `<path d="M159 205 Q195 175 231 205 Z" fill="#E7C29C" stroke="${K}" stroke-width="7"/><path d="M269 205 Q305 175 341 205 Z" fill="#E7C29C" stroke="${K}" stroke-width="7"/>`;
  return player(Object.assign({
    jersey: '#2F7FD8', trim: '#FFD31A', num: '9', shorts: '#1F3E66', flipflops: true, skin: '#E7C29C', browCol: '#C9862E',
    hair: `<path d="M100 200 Q96 70 250 66 Q404 70 400 200 Q380 140 340 150 Q320 110 280 140 Q250 100 220 140 Q180 110 160 150 Q120 140 100 200Z" fill="#E0A23A"/>`,
    hairOver: `<path d="M200 90 l-10 -36 l30 26 l10 -40 l18 40 l24 -34 l2 40 l30 -22 l-14 36" fill="#E0A23A" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>`,
    face: lid,
    behind: `<rect x="150" y="360" width="200" height="170" rx="30" fill="#E8432E" stroke="${K}" stroke-width="8"/>`,
    front: `<path d="M196 362 L196 470 M304 362 L304 470" stroke="#B82A1C" stroke-width="14"/>`,
    mood: o.mood || 'smile',
  }, o));
}


// Klappstuhl, Fuesse bei y=705
function chair(o = {}) {
  return `
  <ellipse cx="250" cy="702" rx="110" ry="14" fill="#000" opacity="0.3"/>
  <path d="M170 380 L170 600 M330 380 L330 600" stroke="${K}" stroke-width="20" stroke-linecap="round"/>
  <path d="M170 380 L170 600 M330 380 L330 600" stroke="#8C9196" stroke-width="10" stroke-linecap="round"/>
  <rect x="160" y="380" width="180" height="90" rx="12" fill="#C9682E" stroke="${K}" stroke-width="8"/>
  <path d="M176 410 H324 M176 440 H324" stroke="#A9531F" stroke-width="5"/>
  <path d="M180 610 L330 700 M320 610 L170 700" stroke="${K}" stroke-width="20" stroke-linecap="round"/>
  <path d="M180 610 L330 700 M320 610 L170 700" stroke="#8C9196" stroke-width="10" stroke-linecap="round"/>
  <path d="M150 590 L350 590 L340 620 L160 620Z" fill="#C9682E" stroke="${K}" stroke-width="8" stroke-linejoin="round"/>
  <path d="M160 566 Q250 548 340 566 Q352 580 344 596 Q250 606 156 596 Q148 580 160 566Z" fill="#2F7FD8" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
  <path d="M170 590 Q250 598 330 590" stroke="#FFD31A" stroke-width="5" fill="none" stroke-dasharray="10 7"/>
  <circle cx="250" cy="576" r="6" fill="#1F3E66"/>
  ${o.num ? `<circle cx="250" cy="425" r="30" fill="#FFD31A" stroke="${K}" stroke-width="6"/><text x="250" y="440" text-anchor="middle" font-family="Lilita" font-size="40" fill="#111">${o.num}</text>` : ''}
  ${o.mud ? `<path d="M200 600 q14 -10 24 0 q4 12 -10 12 q-14 0 -14 -12z M290 470 q8 -6 14 0 q2 8 -6 8z" fill="#6B4226"/>` : ''}`;
}

// Gestrichelter Platzhalter-Fan
function ghost(o = {}) {
  return `<g fill="rgba(255,255,255,0.12)" stroke="#fff" stroke-width="9" stroke-dasharray="22 16">
    <circle cx="250" cy="370" r="70"/><rect x="170" y="450" width="160" height="150" rx="40"/></g>
    <text x="250" y="398" text-anchor="middle" font-family="Lilita" font-size="80" fill="#fff">?</text>`;
}
