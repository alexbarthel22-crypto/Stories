// Tag 2: Fans, Mini-Fans, Plane, Bus, Rechentafel
// Die ersten drei Fans (Cartoon-Figuren, keine echten Fotos), sitzend auf Klappstuehlen.
const FIRST_FANS = [
  {handle: '@eikemzz', o: {jersey: '#9AA3AE', trim: '#2F7FD8', skin: '#F2CBA4', browCol: '#3A2A20',
    hair: `<path d="M104 180 Q120 70 250 70 Q380 70 396 180 Z" fill="#E5483A"/>`,
    hairOver: `<path d="M110 176 L390 176" stroke="#111" stroke-width="7"/><rect x="226" y="160" width="48" height="18" rx="4" fill="#B83226" stroke="#111" stroke-width="4"/>`}},
  {handle: '@tobiii1911', o: {jersey: '#F28A2E', trim: '#FFD31A', skin: '#E7B98E', browCol: '#5A3416',
    hair: `<path d="M100 210 Q100 70 250 70 Q400 70 400 210 Q370 150 250 150 Q130 150 100 210Z" fill="#6B4226"/>`,
    hairOver: `<path d="M120 100 q20 -30 50 -10 q20 -30 50 -6 q30 -26 60 -2 q30 -22 54 6 q30 -6 40 20" fill="none" stroke="#6B4226" stroke-width="28" stroke-linecap="round"/>`}},
  {handle: '@leo.hro1', o: {jersey: '#2A2A2E', trim: '#FFD31A', skin: '#F2CCA6', browCol: '#9A9A9A',
    hair: `<path d="M100 200 Q104 96 250 92 Q396 96 400 200 Q380 150 250 146 Q120 150 100 200Z" fill="#A8A8A8"/>`,
    face: `<path d="M196 292 Q222 274 250 288 Q278 274 304 292 Q300 312 272 306 Q250 298 228 306 Q200 312 196 292Z" fill="#8A8A8A" stroke="#111" stroke-width="5"/>`, mouthY: 318}},
];

function scarf() {
  return `<path d="M188 352 Q250 392 312 352 L318 378 Q250 418 182 378 Z" fill="#2F7FD8" stroke="#111" stroke-width="6"/>
    <path d="M206 366 v24 M232 374 v24 M268 374 v24 M294 366 v24" stroke="#FFD31A" stroke-width="9"/>
    <rect x="274" y="384" width="30" height="80" rx="6" fill="#2F7FD8" stroke="#111" stroke-width="6"/>
    <path d="M278 410 h22 M278 436 h22" stroke="#FFD31A" stroke-width="9"/>`;
}

// Fan im Hoodie mit Vereinsschal; sitzend = Beine abgeschnitten, angewinkelte Beine darunter
function fanFigure(o, sitting) {
  const base = Object.assign({num: '', shorts: '#2B3A55', socks: '#2B3A55', mood: 'smile', front: scarf()}, o);
  const svg = player(base);
  if (!sitting) return svg;
  const id = 'sc' + (UID++);
  return `<defs><clipPath id="${id}"><rect x="-200" y="-200" width="900" height="760"/></clipPath></defs>
    <g clip-path="url(#${id})">${svg}</g>
    <rect x="188" y="540" width="50" height="60" rx="10" fill="#2B3A55" stroke="#111" stroke-width="7"/>
    <rect x="262" y="540" width="50" height="60" rx="10" fill="#2B3A55" stroke="#111" stroke-width="7"/>
    <rect x="192" y="590" width="40" height="96" fill="#2B3A55" stroke="#111" stroke-width="7"/>
    <rect x="268" y="590" width="40" height="96" fill="#2B3A55" stroke="#111" stroke-width="7"/>
    <ellipse cx="206" cy="692" rx="36" ry="15" fill="#F2F2F2" stroke="#111" stroke-width="6"/>
    <ellipse cx="294" cy="692" rx="36" ry="15" fill="#F2F2F2" stroke="#111" stroke-width="6"/>`;
}

function seatedFan(i, t, withChair = true) {
  const f = FIRST_FANS[i];
  return (withChair ? `<g transform="translate(250 0) scale(1.45 1) translate(-250 0)">${chair({num: String(i + 1)})}</g>` : '')
    + fanFigure(Object.assign({blink: blinkAt(t, i * 0.7)}, f.o), true);
}

function handleTag(x, y, text, s = 1) {
  return `<g transform="translate(${x} ${y}) scale(${s})">${box(-text.length * 13 - 26, -34, text.length * 26 + 52, 68, 'white', 6)}
    ${label(0, 14, text, 38, BROWN)}</g>`;
}

// Kleiner stehender Fan (fuer die Menge der 83)
function miniFan(x, y, s, k) {
  const shirts = ['#E5483A', '#2F7FD8', '#F28A2E', '#58B044', '#9AA3AE', '#7B3FE4', '#FFD31A', '#2A2A2E'];
  const skins = ['#F5D3AE', '#E7B98E', '#C98E62', '#8D5A3B', '#F2CCA6'];
  const hairs = ['#2B1D16', '#6B4226', '#E0A23A', '#111', '#A8A8A8', '#B5651D'];
  const sh = shirts[k % shirts.length], sk = skins[(k * 3) % skins.length], hr = hairs[(k * 5) % hairs.length];
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <rect x="-22" y="-10" width="16" height="50" fill="#2B3A55" stroke="#111" stroke-width="5"/>
    <rect x="6" y="-10" width="16" height="50" fill="#2B3A55" stroke="#111" stroke-width="5"/>
    <path d="M-34 -80 Q0 -96 34 -80 L38 -6 L-38 -6 Z" fill="${sh}" stroke="#111" stroke-width="6" stroke-linejoin="round"/>
    <path d="M-30 -84 Q0 -66 30 -84" stroke="#2F7FD8" stroke-width="12" fill="none"/>
    <circle cx="0" cy="-124" r="40" fill="${sk}" stroke="#111" stroke-width="6"/>
    <path d="M-40 -130 Q-38 -168 0 -168 Q38 -168 40 -130 Q20 -148 0 -146 Q-20 -148 -40 -130Z" fill="${hr}"/>
    <circle cx="-14" cy="-124" r="6" fill="#111"/><circle cx="14" cy="-124" r="6" fill="#111"/>
    <path d="M-12 -104 Q0 -96 12 -104" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/></g>`;
}

function crowd(t, x0, y0, cols, rows, dx, dy, s) {
  let out = '';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const k = r * cols + c, bob = Math.sin(t * 6 + k) * 4;
    out += miniFan(x0 + c * dx + (r % 2) * dx / 2, y0 + r * dy + bob, s * (1 + r * 0.06), k);
  }
  return out;
}

// Stuhlreihen (fuer "Klappstuehle fuer alle"); pop = wie viele schon sichtbar
function chairRows(t, x0, y0, cols, rows, dx, dy, s, t0, step) {
  let out = '';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const k = r * cols + c, p = pop(t, t0 + k * step, 0.2);
    if (p > 0) out += place(chair({}), x0 + c * dx, y0 + r * dy, s * (1 + r * 0.08) * p);
  }
  return out;
}

// Plane ueber der Tribuene: blau-gelb, an vier Stangen, Regentropfen perlen ab
function tarp(t, x0, x1, top, base, drop) {
  const sag = 26, y = top - (1 - drop) * 300;
  return `<g>
    <path d="M${x0} ${y} L${x0} ${base}" stroke="#7A5232" stroke-width="16"/><path d="M${x1} ${y} L${x1} ${base}" stroke="#7A5232" stroke-width="16"/>
    <path d="M${x0 - 30} ${y} Q${(x0 + x1) / 2} ${y + sag} ${x1 + 30} ${y} L${x1 + 10} ${y + 60} Q${(x0 + x1) / 2} ${y + 60 + sag} ${x0 - 10} ${y + 60} Z" fill="#2F7FD8" stroke="#111" stroke-width="9" stroke-linejoin="round"/>
    ${Array.from({length: 7}, (_, i) => { const xx = x0 + (x1 - x0) * (i + 0.5) / 7; return `<path d="M${xx - 30} ${y + 8 + sag * 0.6} L${xx + 30} ${y + 8 + sag * 0.6}" stroke="#FFD31A" stroke-width="10"/>`; }).join('')}
    ${Array.from({length: 6}, (_, i) => { const ph = (t * 2.2 + i * 0.17) % 1; const xx = x0 + (x1 - x0) * (i + 0.5) / 6; return `<circle cx="${xx + (i % 2 ? 1 : -1) * ph * 60}" cy="${y + sag - 10 - Math.sin(ph * Math.PI) * 40}" r="7" fill="#D6E2F2" opacity="${1 - ph}"/>`; }).join('')}
  </g>`;
}

// Stadtbus mit Fenster, in dem der Nr.-9-Stuerer winkt
function cityBus(x, base, s, t, passenger) {
  const wheel = (cx) => `<g transform="translate(${cx} 0) rotate(${-t * 400})"><circle r="48" fill="#222" stroke="#111" stroke-width="8"/><circle r="18" fill="#9A9A9A"/><path d="M-18 0 H18 M0 -18 V18" stroke="#555" stroke-width="5"/></g>`;
  return `<g transform="translate(${x} ${base}) scale(${s})">
    <rect x="-380" y="-330" width="760" height="290" rx="36" fill="#FFD31A" stroke="#111" stroke-width="10"/>
    <rect x="-380" y="-120" width="760" height="40" fill="#2F7FD8" stroke="#111" stroke-width="6"/>
    ${[-300, -150, 0, 150].map(wx => `<rect x="${wx - 60}" y="-300" width="120" height="120" rx="14" fill="#BFE0F2" stroke="#111" stroke-width="7"/>`).join('')}
    ${passenger || ''}
    <rect x="260" y="-300" width="100" height="220" rx="10" fill="#9EC6DA" stroke="#111" stroke-width="7"/>
    <rect x="-370" y="-360" width="300" height="40" rx="8" fill="#111"/><text x="-220" y="-330" text-anchor="middle" ${FONT} font-size="30" fill="#FFB020">9 · STADT</text>
    <g transform="translate(0 -40)">${wheel(-230)}${wheel(230)}</g>
    <circle cx="372" cy="-90" r="14" fill="#FFF3B0" stroke="#111" stroke-width="5"/>
  </g>`;
}

// Rechentafel: Zeilen erscheinen nacheinander
function calcBoard(t, x, y, lines, times) {
  let s = box(x, y, 860, 120 + lines.length * 110, 'white', 11);
  lines.forEach((l, i) => {
    if (t < times[i]) return;
    const k = clamp((t - times[i]) / 0.2, 0, 1);
    s += `<g opacity="${k}" transform="translate(${(1 - k) * 40} 0)">
      ${label(x + 50, y + 106 + i * 110, l[0], 48, BROWN, 'start')}
      <text x="${x + 810}" y="${y + 110 + i * 110}" text-anchor="end" ${FONT} font-size="62" fill="${l[2] || '#2FA84A'}">${l[1]}</text></g>`;
  });
  return s;
}
