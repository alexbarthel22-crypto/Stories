// Tag 6 – Spielerkabine, Nico, Denny-Frisuren
function nico(o = {}) {
  return player(Object.assign({
    jersey: '#2F7FD8', trim: '#FFD31A', num: '17', shorts: '#1F3E66', skin: '#C98E62', browCol: '#1A1410',
    hair: `<path d="M100 200 Q100 70 250 66 Q400 70 400 200 Q370 140 250 140 Q130 140 100 200Z" fill="#1A1410"/>`,
    hairOver: `<g fill="#1A1410" stroke="#111" stroke-width="5">${[130, 170, 210, 250, 290, 330, 370].map((x, i) => `<circle cx="${x}" cy="${92 - (i % 2) * 18}" r="32"/>`).join('')}</g>
      <circle cx="388" cy="262" r="8" fill="#FFD31A" stroke="#111" stroke-width="4"/>`,
    front: `<path d="M196 362 Q250 420 304 362" stroke="#FFD31A" stroke-width="5" fill="none"/><circle cx="250" cy="420" r="12" fill="#FFD31A" stroke="#111" stroke-width="4"/>`,
    mood: 'smile',
  }, o));
}
function dennyShort(o = {}) {
  return player(Object.assign({
    jersey: '#2F7FD8', trim: '#FFD31A', num: '4', shorts: '#1F3E66', skin: '#E9B98F', browCol: '#1C1410',
    hair: `<path d="M104 176 Q112 74 250 72 Q388 74 396 176 Q370 128 250 124 Q130 128 104 176Z" fill="#1C1410"/>`,
    hairOver: `<rect x="108" y="146" width="284" height="26" rx="8" fill="#E5483A" stroke="#111" stroke-width="6"/>`,
    mood: 'smile',
  }, o));
}
function dennyLong(o = {}) {
  return player(Object.assign({
    jersey: '#2F7FD8', trim: '#FFD31A', num: '4', shorts: '#1F3E66', skin: '#E9B98F', browCol: '#1C1410',
    hair: `<path d="M100 230 Q100 70 250 68 Q400 70 400 230 Q380 140 250 136 Q120 140 100 230Z" fill="#1C1410"/>`,
    behind: `<path d="M120 200 Q60 420 130 560 L370 560 Q440 420 380 200 Z" fill="#1C1410" stroke="#111" stroke-width="7"/>`,
    hairOver: `<rect x="108" y="146" width="284" height="26" rx="8" fill="#E5483A" stroke="#111" stroke-width="6"/>`,
    mood: 'smile',
  }, o));
}

// Spielerkabine (Bauanhaenger), build 0..1 baut Teile nacheinander auf
function cabin(x, y, s, build, t) {
  const p = k => clamp((build - k) / 0.18, 0, 1), pg = (k, svg) => p(k) <= 0 ? '' : `<g opacity="${p(k)}" transform="translate(0 ${(1 - p(k)) * -120})">${svg}</g>`;
  return `<g transform="translate(${x} ${y}) scale(${s})">
    ${pg(0.0, `<circle cx="-220" cy="-20" r="48" fill="#2A2A2E" stroke="#111" stroke-width="9"/><circle cx="220" cy="-20" r="48" fill="#2A2A2E" stroke="#111" stroke-width="9"/><path d="M-420 -60 L-340 -60" stroke="#3A2316" stroke-width="14"/>`)}
    ${pg(0.15, `<rect x="-340" y="-330" width="680" height="300" rx="20" fill="#E9EEF2" stroke="#3A2316" stroke-width="11"/><path d="M-340 -100 H340" stroke="#2F7FD8" stroke-width="30"/><path d="M-340 -70 H340" stroke="#FFD31A" stroke-width="12"/>`)}
    ${pg(0.35, `<path d="M-370 -330 L370 -330 L340 -380 L-340 -380 Z" fill="#2F7FD8" stroke="#3A2316" stroke-width="10" stroke-linejoin="round"/>`)}
    ${pg(0.5, `<rect x="160" y="-290" width="130" height="250" rx="8" fill="#8A5A36" stroke="#3A2316" stroke-width="8"/><circle cx="270" cy="-160" r="10" fill="#FFD31A"/>`)}
    ${pg(0.62, `<rect x="-300" y="-290" width="150" height="110" rx="10" fill="#BFE0F2" stroke="#3A2316" stroke-width="8"/><rect x="-120" y="-290" width="150" height="110" rx="10" fill="#BFE0F2" stroke="#3A2316" stroke-width="8"/>`)}
    ${pg(0.78, `<rect x="-300" y="-170" width="430" height="56" rx="10" fill="#FFF8EC" stroke="#3A2316" stroke-width="6"/><text x="-85" y="-130" text-anchor="middle" ${FONT} font-size="38" fill="#3A2316">SPIELERKABINE</text>
      <g transform="translate(-30 -360) scale(0.14) translate(-300 -300)">${LOGO}</g>`)}
  </g>`;
}
function screw(x, y, s, rot) {
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})"><rect x="-8" y="-10" width="16" height="70" rx="4" fill="#9AA0A8" stroke="#3A2316" stroke-width="5"/>
    <path d="M-8 6 h16 M-8 20 h16 M-8 34 h16" stroke="#3A2316" stroke-width="3"/><rect x="-22" y="-26" width="44" height="18" rx="5" fill="#C0C6CC" stroke="#3A2316" stroke-width="5"/></g>`;
}
function locker(x, y, name, col) {
  return `<g transform="translate(${x} ${y})"><rect x="-70" y="-300" width="140" height="300" rx="8" fill="${col}" stroke="#3A2316" stroke-width="7"/>
    ${[0, 1, 2].map(k => `<path d="M-40 ${-270 + k * 16} h80" stroke="#3A2316" stroke-width="5" opacity=".6"/>`).join('')}
    <rect x="-56" y="-200" width="112" height="40" rx="6" fill="#FFF8EC" stroke="#3A2316" stroke-width="4"/>
    <text x="0" y="-171" text-anchor="middle" ${FONT} font-size="${name.length > 7 ? 18 : 26}" fill="#3A2316">${name}</text>
    <circle cx="48" cy="-120" r="8" fill="#FFD31A" stroke="#3A2316" stroke-width="3"/></g>`;
}
