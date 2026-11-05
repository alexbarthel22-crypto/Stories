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
function miniFan(x, y, s, k, sad) {
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
    ${sad ? `<path d="M-12 -98 Q0 -108 12 -98" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M-24 -140 l10 6 M24 -140 l-10 6" stroke="#111" stroke-width="4"/><path d="M22 -118 q4 10 0 14 q-4 -4 0 -14z" fill="#8EC9F2"/>`
          : `<path d="M-12 -104 Q0 -96 12 -104" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/>`}</g>`;
}

function crowd(t, x0, y0, cols, rows, dx, dy, s, sad) {
  let out = '';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const k = r * cols + c, bob = Math.sin(t * 6 + k) * 4;
    out += miniFan(x0 + c * dx + (r % 2) * dx / 2, y0 + r * dy + bob, s * (1 + r * 0.06), k, sad);
  }
  return out;
}

// Stuhlreihen (fuer "Klappstuehle fuer alle"); pop = wie viele schon sichtbar
function chairRows(t, x0, y0, cols, rows, dx, dy, s, t0, step) {
  let out = '';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const k = r * cols + c, p = pop(t, t0 + k * step, 0.2);
    if (p > 0) out += place(chair({}), x0 + c * dx + (r % 2) * dx * 0.5 - dx * 0.25, y0 + r * dy, s * (1 + r * 0.08) * p);
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
    const big = l[3], ly = y + 106 + i * 110 + (big ? 14 : 0), vy = y + 110 + i * 110 + (big ? 22 : 0);
    const age = t - times[i], hp = age < 0.6 ? Math.exp(-age * 6) : 0, sc = 1 + 0.55 * hp;
    const vx = x + 810;
    s += `<g opacity="${k}" transform="translate(${(1 - k) * 40} 0)">
      ${hp > 0.05 ? `<rect x="${x + 20}" y="${vy - (big ? 92 : 70)}" width="820" height="${big ? 118 : 92}" rx="14" fill="#FFD31A" opacity="${0.75 * hp}"/>` : ''}
      ${label(x + 50, ly, l[0], big ? 64 : 48, BROWN, 'start')}
      <g transform="translate(${vx} ${vy - 20}) scale(${sc}) translate(${-vx} ${-(vy - 20)})">
      <text x="${vx}" y="${vy}" text-anchor="end" ${FONT} font-size="${big ? 100 : 62}" fill="${l[2] || '#2FA84A'}" stroke="#fff" stroke-width="${big ? 6 : 0}" paint-order="stroke">${l[1]}</text></g></g>`;
  });
  return s;
}

// 80 Fans setzen sich nacheinander auf die Stuhlreihen (fallen von oben auf ihren Platz)
function seatedCrowd(t, x0, y0, cols, rows, dx, dy, s, t0, step, skip = []) {
  let out = '';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const k = r * cols + c, tt = t - (t0 + ((k * 37) % (rows * cols)) * step);
    if (tt <= 0 || skip.includes(k)) continue;
    const sc = s * (1 + r * 0.08), seatY = y0 + r * dy - 115 * sc, drop = Math.max(0, 1 - tt / 0.18);
    out += miniFan(x0 + c * dx + (r % 2) * dx * 0.5 - dx * 0.25, seatY - drop * 120 + 4 * sc * 10, sc * 2.2, k + 3);
  }
  return out;
}

// Trikot der Nr. 9 auf einem Buegel, mit Aermeln, Kragen, Seitenstreifen und Schatten
function jersey9(cx, cy, s, sway) {
  return `<g transform="translate(${cx} ${cy}) rotate(${sway}) scale(${s})">
    <path d="M0 -250 q0 -40 30 -40 q30 0 30 30" stroke="#9A9A9A" stroke-width="12" fill="none" stroke-linecap="round"/>
    <path d="M-170 -170 Q0 -215 170 -170 L180 -150 L-180 -150 Z" fill="#8A5A36" stroke="#111" stroke-width="8"/>
    <path d="M-80 -180 L-200 -140 L-260 -10 L-185 20 L-150 -40 L-150 230 Q0 250 150 230 L150 -40 L185 20 L260 -10 L200 -140 L80 -180 Q0 -110 -80 -180 Z"
      fill="#2F7FD8" stroke="#111" stroke-width="10" stroke-linejoin="round"/>
    <path d="M-150 -40 L-150 230 L-118 232 L-118 -60 Z M150 -40 L150 230 L118 232 L118 -60 Z" fill="#1F5FAE"/>
    <path d="M-133 -40 V228 M133 -40 V228" stroke="#FFD31A" stroke-width="10"/>
    <path d="M-262 -14 L-188 16" stroke="#FFD31A" stroke-width="16"/><path d="M262 -14 L188 16" stroke="#FFD31A" stroke-width="16"/>
    <path d="M-80 -180 Q0 -110 80 -180 L60 -184 Q0 -132 -60 -184 Z" fill="#FFD31A" stroke="#111" stroke-width="6"/>
    <path d="M-60 -140 Q-90 0 -70 200" stroke="#fff" stroke-width="14" fill="none" opacity=".18" stroke-linecap="round"/>
    <g transform="translate(-75 -95) scale(0.11) translate(-300 -300)">${LOGO}</g>
    <text x="0" y="150" text-anchor="middle" ${FONT} font-size="230" fill="#FFD31A" stroke="#111" stroke-width="12" paint-order="stroke">9</text>
    <text x="0" y="-60" text-anchor="middle" ${FONT} font-size="44" fill="#fff" stroke="#111" stroke-width="6" paint-order="stroke" letter-spacing="3">STURM</text>
  </g>`;
}

function speech(x, y, text, rot = 0, s = 1) {
  const w = text.length * 22 + 50;
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">
    <path d="M${-w / 2} -40 h${w} a20 20 0 0 1 20 20 v40 a20 20 0 0 1 -20 20 h${-w / 2 + 30} l-24 26 l-6 -26 h${-w / 2 + 0} a20 20 0 0 1 -20 -20 v-40 a20 20 0 0 1 20 -20z" fill="#fff" stroke="#3A2316" stroke-width="7"/>
    <text x="10" y="14" text-anchor="middle" ${FONT} font-size="40" fill="#3A2316">${text}</text></g>`;
}

function profilePic(x, y, i, r = 72) {
  const id = 'pp' + (UID++);
  return `<defs><clipPath id="${id}"><circle cx="${x}" cy="${y}" r="${r}"/></clipPath></defs>
    <circle cx="${x + 4}" cy="${y + 8}" r="${r + 8}" fill="#3A2316"/>
    <image href="${FAN_PICS[i]}" x="${x - r}" y="${y - r}" width="${2 * r}" height="${2 * r}" clip-path="url(#${id})"/>
    <circle cx="${x}" cy="${y}" r="${r}" fill="none" stroke="#fff" stroke-width="8"/><circle cx="${x}" cy="${y}" r="${r + 5}" fill="none" stroke="#3A2316" stroke-width="5"/>`;
}

function twoLineBadge(cx, cy, l1, l2, fs) {
  const w = Math.max(l1.length, l2.length) * fs * 0.6 + fs * 2.6, h = fs * 2.7;
  return `${box(cx - w / 2, cy - h / 2, w, h, 'orange', 8)}${ballIcon(cx - w / 2 + fs * 1.0, cy, fs * 0.55)}
    ${label(cx + fs * 0.6, cy - fs * 0.12, l1, fs, '#fff')}${label(cx + fs * 0.6, cy + fs * 1.0, l2, fs, '#fff')}`;
}
