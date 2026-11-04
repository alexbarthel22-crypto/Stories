// Text-Stil: Boxen im Spielfeld-Look bzw. orange Unterboxen, dicke dunkelbraune Kontur,
// harter Schatten nach unten, runde fette Schrift (Lilita One).
const BROWN = '#3A2316';
const NAVY = BROWN;
const KIND = {
  pitch: {fill: '#58B044', fg: '#fff'},
  orange: {fill: '#F28A2E', fg: '#fff'},
  red: {fill: '#E5483A', fg: '#fff'},
  pink: {fill: '#F25C9E', fg: '#fff'},
  blue: {fill: '#2F7FD8', fg: '#fff'},
  white: {fill: '#FFF8EC', fg: BROWN},
};
const BG2KIND = {'#2F7FD8': 'pitch', '#FFD31A': 'orange', '#E8432E': 'red', '#FF3FA4': 'pink', '#FF7EB6': 'pink'};

function popG(t, t0, cx, cy, inner) {
  if (t < t0) return '';
  const k = clamp((t - t0) / 0.3, 0, 1);
  const s = 0.4 + 0.6 * backOut(k);
  return `<g opacity="${clamp(k * 4, 0, 1)}" transform="translate(${cx} ${cy}) scale(${s}) translate(${-cx} ${-cy})">${inner}</g>`;
}

let PID = 0;
function pitchFill(x, y, w, h, r) {
  const id = 'pf' + (PID++);
  let st = '';
  const n = Math.max(6, Math.round(w / 70));
  for (let i = 0; i < n; i += 2) st += `<rect x="${x + i * w / n}" y="${y}" width="${w / n}" height="${h}" fill="#4CA13A"/>`;
  return `<defs><clipPath id="${id}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}"/></clipPath></defs>
    <g clip-path="url(#${id})"><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#5DB549"/>${st}
    <path d="M${x + w / 2} ${y} V${y + h}" stroke="#fff" stroke-opacity=".45" stroke-width="5"/>
    <circle cx="${x + w / 2}" cy="${y + h / 2}" r="${h * 0.3}" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="5"/></g>`;
}

function ballIcon(cx, cy, r) {
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#fff" stroke="${BROWN}" stroke-width="${r / 6}"/>
    <path d="M${cx} ${cy - r * 0.35} L${cx + r * 0.33} ${cy - r * 0.1} L${cx + r * 0.2} ${cy + r * 0.3} L${cx - r * 0.2} ${cy + r * 0.3} L${cx - r * 0.33} ${cy - r * 0.1}Z" fill="${BROWN}"/>
    <path d="M${cx} ${cy - r * 0.35} V${cy - r} M${cx + r * 0.33} ${cy - r * 0.1} L${cx + r * 0.95} ${cy - r * 0.3} M${cx - r * 0.33} ${cy - r * 0.1} L${cx - r * 0.95} ${cy - r * 0.3} M${cx + r * 0.2} ${cy + r * 0.3} L${cx + r * 0.55} ${cy + r * 0.8} M${cx - r * 0.2} ${cy + r * 0.3} L${cx - r * 0.55} ${cy + r * 0.8}" stroke="${BROWN}" stroke-width="${r / 10}"/>`;
}

function textW(text, fs) { return text.length * fs * 0.56; }

function box(x, y, w, h, kind, sw = 9) {
  const K2 = KIND[kind] || KIND.white, r = Math.min(h * 0.2, 34);
  return `<rect x="${x}" y="${y + sw * 1.4}" width="${w}" height="${h}" rx="${r}" fill="${BROWN}"/>
    ${kind === 'pitch' ? pitchFill(x, y, w, h, r) : `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${K2.fill}"/>`}
    <rect x="${x + sw * 0.9}" y="${y + sw * 0.9}" width="${w - sw * 1.8}" height="${h - sw * 1.8}" rx="${Math.max(r - sw, 4)}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="${sw * 0.5}"/>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="none" stroke="${BROWN}" stroke-width="${sw}"/>`;
}

function label(x, y, text, fs, fg, anchor = 'middle') {
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" ${FONT} font-size="${fs}" fill="${fg}" stroke="${BROWN}" stroke-width="${fg === BROWN ? 0 : fs / 6.5}" paint-order="stroke" stroke-linejoin="round" letter-spacing="1">${text}</text>`;
}

function badge(cx, cy, text, o = {}) {
  let fs = (o.fs || 64) * 1.3;
  const pad0 = o.pad || fs * 0.55;
  fs = Math.min(fs, (860 - 2 * pad0) / (text.length * 0.56 + (o.ball ? 1.1 : 0)));
  const pad = o.pad || fs * 0.55;
  const kind = o.kind || BG2KIND[o.bg] || 'white';
  const icon = o.ball ? fs * 1.1 : 0;
  const w = textW(text, fs) + pad * 2 + icon, h = fs * 1.45;
  const fg = KIND[kind].fg;
  const sw = Math.max(6, fs / 8);
  return `<g transform="rotate(${o.rot || 0} ${cx} ${cy})">${box(cx - w / 2, cy - h / 2, w, h, kind, sw)}
    ${o.ball ? ballIcon(cx - w / 2 + pad + fs * 0.4, cy, fs * 0.42) : ''}
    ${label(cx + icon / 2, cy + fs * 0.35, text, fs, fg)}</g>`;
}

function bigText(cx, cy, text, col, fs) {
  const st = `text-anchor="middle" ${FONT} font-size="${fs}" stroke-linejoin="round" letter-spacing="2"`;
  return `<text x="${cx}" y="${cy + fs / 12}" ${st} fill="${BROWN}" stroke="${BROWN}" stroke-width="${fs / 5.5}">${text}</text>
    <text x="${cx}" y="${cy}" ${st} fill="${col}" stroke="${BROWN}" stroke-width="${fs / 6.5}" paint-order="stroke">${text}</text>`;
}

function nameCard(x, y, num, name, sub, numBg) {
  const w = 800, h = 170;
  return `<g transform="translate(${x} ${y})">${box(0, 0, w, h, 'white', 10)}
    ${box(24, 22, 126, 126, 'pitch', 8)}
    ${label(87, 112, num, 84, '#fff')}
    ${label(180, 92, name, 72, BROWN, 'start')}
    <rect x="178" y="106" width="${textW(sub, 34) + 34}" height="50" rx="12" fill="#F28A2E" stroke="${BROWN}" stroke-width="6"/>
    ${label(195, 142, sub, 34, '#fff', 'start')}</g>`;
}

function optionCard(cx, cy, icon, l1, l2, rot) {
  const w = 255, h = 330, x = cx - w / 2, y = cy - h / 2;
  return `<g transform="rotate(${rot} ${cx} ${cy})">${box(x, y, w, h, 'white', 9)}
    ${box(x, y, w, 70, 'pitch', 9)}${ballIcon(cx, y + 35, 20)}
    <g transform="translate(${cx} ${cy - 10}) scale(.72)">${icon}</g>
    ${label(cx, cy + 105, l1, 38, BROWN)}${label(cx, cy + 147, l2, 38, BROWN)}</g>`;
}

// Untertitel: * = gelb, ! = rot; weiss mit dicker brauner Kontur
function caption(text, t0, t) {
  if (!text) return '';
  const k = clamp((t - t0) / 0.15, 0, 1);
  const s = 0.8 + 0.2 * backOut(k);
  const words = text.split(' ').map(w => {
    let col = '#fff';
    if (w.startsWith('*')) { col = '#FFD31A'; w = w.slice(1); }
    if (w.startsWith('!')) { col = '#FF5A4A'; w = w.slice(1); }
    return [w, col];
  });
  const len = text.replace(/[*!]/g, '').length;
  const fs = Math.min(112, 880 / (Math.max(len, 6) * 0.56));
  const cx = 510, cy = 1290;
  const plain = words.map(([w]) => w).join(' ');
  const main = words.map(([w, c]) => `<tspan fill="${c}">${w}</tspan>`).join(' ');
  const st = `text-anchor="middle" ${FONT} font-size="${fs}" stroke-linejoin="round" letter-spacing="1.5"`;
  return `<g transform="translate(${cx} ${cy}) scale(${s}) translate(${-cx} ${-cy})">
    <text x="${cx}" y="${cy + fs / 11}" ${st} fill="${BROWN}" stroke="${BROWN}" stroke-width="${fs / 4.6}">${plain}</text>
    <text x="${cx}" y="${cy}" ${st} stroke="${BROWN}" stroke-width="${fs / 5.2}" paint-order="stroke">${main}</text></g>`;
}

// Schlamm-Splash als Szenenuebergang
function mudWipe(lt) {
  const d = 0.2;
  if (lt >= d) return '';
  const k = 1 - easeOut(lt / d);
  let s = '';
  for (let i = 0; i < 9; i++) {
    const x = rnd(i + 200) * 1080, y = rnd(i + 300) * 1920, r = (380 + rnd(i + 400) * 300) * k;
    s += `<circle cx="${x}" cy="${y}" r="${r}" fill="${i % 2 ? '#5A3B22' : '#6B4A30'}"/>`;
  }
  return s;
}
