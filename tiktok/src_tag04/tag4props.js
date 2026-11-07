// Tag 4 – neue Figuren und Gelaende

// Luca, Platzwart: olivgruene Latzhose, orange Muetze, Gummistiefel
function luca(o = {}) {
  return player(Object.assign({
    jersey: '#6B7A3A', trim: '#6B7A3A', num: '', shorts: '#55622C', socks: '#2E7D32', shoe: '#2E7D32', skin: '#F2C9A0', browCol: '#3A2416',
    hair: `<path d="M104 170 Q120 66 250 66 Q380 66 396 170 Z" fill="#F28A2E"/>`,
    hairOver: `<path d="M100 172 Q250 140 400 172 L398 200 Q250 168 102 200 Z" fill="#D9701E" stroke="#111" stroke-width="7"/>
      <circle cx="250" cy="62" r="20" fill="#F28A2E" stroke="#111" stroke-width="6"/>`,
    front: `<path d="M200 362 L206 470 M300 362 L294 470" stroke="#3E4A1C" stroke-width="14"/>
      <rect x="206" y="430" width="88" height="70" rx="8" fill="#55622C" stroke="#111" stroke-width="6"/>
      <path d="M226 452 h48" stroke="#F28A2E" stroke-width="7"/>`,
    mood: 'smile',
  }, o));
}

// Denny, Verteidiger Nr. 4: lange dunkle Haare mit Zopf, rotes Schweissband
function denny(o = {}) {
  return player(Object.assign({
    jersey: '#2F7FD8', trim: '#FFD31A', num: '4', shorts: '#1F3E66', skin: '#E9B98F', browCol: '#1C1410',
    hair: `<path d="M100 220 Q100 70 250 68 Q400 70 400 220 Q380 140 250 136 Q120 140 100 220Z" fill="#1C1410"/>`,
    behind: `<path d="M330 300 Q420 380 380 470" stroke="#1C1410" stroke-width="40" fill="none" stroke-linecap="round"/>`,
    hairOver: `<rect x="108" y="146" width="284" height="26" rx="8" fill="#E5483A" stroke="#111" stroke-width="6"/>`,
    mood: 'talk', mouth: 0.4,
  }, o));
}

// TikTok-Kommentar-Nachbau (allgemein)
function commentReplica(x, y, t, pic, name, emoji, text) {
  const id = 'cr' + (UID++);
  return `<g transform="translate(${x} ${y})">
    <rect x="8" y="12" width="860" height="250" rx="30" fill="#000" opacity=".45"/>
    <rect x="0" y="0" width="860" height="250" rx="30" fill="#1E1E1E" stroke="#fff" stroke-width="5"/>
    <defs><clipPath id="${id}"><circle cx="100" cy="100" r="64"/></clipPath></defs>
    <image href="${pic}" x="36" y="36" width="128" height="128" clip-path="url(#${id})"/>
    <text x="200" y="82" font-family="Inter" font-weight="700" font-size="40" fill="#9A9A9A">${name}</text>
    <text x="${210 + name.length * 22}" y="82" font-family="Noto Color Emoji" font-size="36">${emoji}</text>
    <text x="200" y="152" font-family="Inter" font-weight="600" font-size="48" fill="#fff">${text}</text>
    <text x="200" y="212" font-family="Inter" font-weight="700" font-size="30" fill="#8A8A8A">Antworten</text>
    <g transform="translate(780 120) scale(${1 + 0.12 * Math.max(0, Math.sin(t * 9))})"><path d="M0 -14 c-22 -30 -64 -8 -46 24 l46 46 l46 -46 c18 -32 -24 -54 -46 -24z" fill="#FE2C55" stroke="#fff" stroke-width="4"/></g></g>`;
}

// Schlammpumpe mit Schlauch
function mudPump(x, y, s, t, on) {
  const vib = on ? Math.sin(t * 60) * 2 : 0;
  return `<g transform="translate(${x + vib} ${y}) scale(${s})">
    <rect x="-130" y="-120" width="260" height="150" rx="18" fill="#E5483A" stroke="#3A2316" stroke-width="9"/>
    <rect x="-110" y="-104" width="220" height="30" rx="10" fill="#fff" opacity=".22"/>
    <circle cx="-60" cy="-40" r="38" fill="#9AA0A8" stroke="#3A2316" stroke-width="7"/><circle cx="-60" cy="-40" r="14" fill="#3A2316"/>
    <rect x="10" y="-70" width="90" height="56" rx="8" fill="#2A2A2E" stroke="#3A2316" stroke-width="6"/>
    <text x="55" y="-32" text-anchor="middle" ${FONT} font-size="26" fill="#FFD31A">PUMP</text>
    <circle cx="-90" cy="44" r="26" fill="#2A2A2E" stroke="#111" stroke-width="6"/><circle cx="90" cy="44" r="26" fill="#2A2A2E" stroke="#111" stroke-width="6"/>
    ${on ? [0, 1, 2].map(k => { const ph = (t * 1.5 + k / 3) % 1; return `<circle cx="${-100 + ph * -40}" cy="${-140 - ph * 90}" r="${10 + ph * 18}" fill="#9AA0A8" opacity="${0.6 * (1 - ph)}"/>`; }).join('') : ''}
  </g>`;
}

// Vereinsgelaende-Elemente
function bauwagen(x, y, s) {
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <rect x="-260" y="-260" width="520" height="230" rx="30" fill="#2F7FD8" stroke="#3A2316" stroke-width="10"/>
    <path d="M-260 -230 Q0 -320 260 -230" fill="#1F5FAE" stroke="#3A2316" stroke-width="10"/>
    <rect x="-200" y="-210" width="110" height="80" rx="8" fill="#BFE0F2" stroke="#3A2316" stroke-width="7"/>
    <rect x="80" y="-210" width="100" height="180" rx="6" fill="#8A5A36" stroke="#3A2316" stroke-width="7"/><circle cx="160" cy="-120" r="8" fill="#FFD31A"/>
    <rect x="-60" y="-200" width="120" height="44" rx="6" fill="#FFF8EC" stroke="#3A2316" stroke-width="5"/>
    <text x="0" y="-168" text-anchor="middle" ${FONT} font-size="30" fill="#3A2316">KABINE</text>
    <circle cx="-150" cy="-20" r="42" fill="#2A2A2E" stroke="#111" stroke-width="8"/><circle cx="150" cy="-20" r="42" fill="#2A2A2E" stroke="#111" stroke-width="8"/>
    <path d="M-300 -60 L-260 -60" stroke="#3A2316" stroke-width="12"/>
    <path d="M-120 -260 v-40 h20" stroke="#9AA0A8" stroke-width="10" fill="none"/></g>`;
}
function grill(x, y, s, t) {
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <path d="M-60 0 L-80 120 M60 0 L80 120 M0 0 V120" stroke="#3A3A3A" stroke-width="10"/>
    <path d="M-120 -60 Q0 60 120 -60 Z" fill="#2A2A2E" stroke="#111" stroke-width="8"/>
    <rect x="-120" y="-70" width="240" height="14" rx="5" fill="#9AA0A8" stroke="#111" stroke-width="5"/>
    ${[-70, -20, 30, 80].map(sx => `<rect x="${sx - 22}" y="-92" width="54" height="20" rx="10" fill="#B8572E" stroke="#3A2316" stroke-width="4"/>`).join('')}
    ${[0, 1, 2].map(k => { const ph = (t * 0.8 + k / 3) % 1; return `<circle cx="${-30 + k * 30 + Math.sin(ph * 6) * 15}" cy="${-110 - ph * 220}" r="${16 + ph * 26}" fill="#C9C9C9" opacity="${0.55 * (1 - ph)}"/>`; }).join('')}
    <rect x="-90" y="-240" width="180" height="56" rx="8" fill="#FFF8EC" stroke="#3A2316" stroke-width="5" transform="rotate(-6)"/>
    <text x="0" y="-202" text-anchor="middle" ${FONT} font-size="30" fill="#E5483A" transform="rotate(-6)">WURST 2 €</text></g>`;
}
function pappeTafel(x, y, s) {
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <path d="M-150 0 V120 M150 0 V120" stroke="#8A5A36" stroke-width="16"/>
    <path d="M-200 -150 L200 -158 L196 10 L-196 14 Z" fill="#C8A26B" stroke="#3A2316" stroke-width="8"/>
    <text x="-110" y="-90" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="38" fill="#3A2316">HEIM</text>
    <text x="110" y="-92" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="38" fill="#3A2316">GAST</text>
    <text x="0" y="-20" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="96" fill="#3A2316">0 : 0</text>
    <path d="M-180 -140 l30 10" stroke="#A9824E" stroke-width="6"/></g>`;
}
function flagPole(x, y, s, t) {
  const w = Math.sin(t * 4);
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <rect x="-8" y="-520" width="16" height="520" fill="#9AA0A8" stroke="#3A2316" stroke-width="5"/>
    <circle cx="0" cy="-526" r="14" fill="#FFD31A" stroke="#3A2316" stroke-width="5"/>
    <path d="M8 -500 Q${100 + w * 10} ${-520 + w * 14} 220 -500 L220 -360 Q${100 + w * 10} ${-380 + w * 14} 8 -360 Z" fill="#2F7FD8" stroke="#3A2316" stroke-width="6"/>
    <g transform="translate(114 -430) scale(0.17) translate(-300 -300)">${LOGO}</g></g>`;
}
