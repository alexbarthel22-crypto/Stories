// Eigener Grafikstil FC Schlammloch: schraege Klebeband-Badges in Vereinsfarben,
// Navy-Konturen mit versetztem Schatten, Untertitel mit gelben Schluesselwoertern.
const NAVY = '#14213D';

function popG(t, t0, cx, cy, inner) {
  if (t < t0) return '';
  const e = backOut((t - t0) / 0.32), lin = clamp((t - t0) / 0.32, 0, 1);
  const s = 0.6 + 0.4 * e, dy = -70 * (1 - easeOut(lin)), rot = -7 * (1 - easeOut(lin));
  return `<g opacity="${clamp(lin * 3, 0, 1)}" transform="translate(${cx} ${cy + dy}) rotate(${rot}) scale(${s}) translate(${-cx} ${-cy})">${inner}</g>`;
}

function badge(cx, cy, text, o = {}) {
  const fs = o.fs || 64, pad = o.pad || 40;
  const w = text.length * fs * 0.66 + pad * 2, h = fs * 1.45;
  const bg = o.bg || '#FFFFFF', fg = o.fg || NAVY;
  return `<g transform="rotate(${o.rot || 0} ${cx} ${cy})"><g transform="translate(${cx} ${cy}) skewX(-10)">
    <rect x="${-w / 2 + 10}" y="${-h / 2 + 12}" width="${w}" height="${h}" rx="10" fill="${NAVY}"/>
    <rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="10" fill="${bg}" stroke="${NAVY}" stroke-width="7"/>
    <rect x="${-w / 2 + 11}" y="${-h / 2 + 11}" width="${w - 22}" height="${h - 22}" rx="5" fill="none" stroke="${fg}" stroke-opacity=".35" stroke-width="3" stroke-dasharray="12 9"/>
    </g><text x="${cx}" y="${cy + fs * 0.36}" text-anchor="middle" ${FONT} font-size="${fs}" fill="${fg}" letter-spacing="1.5">${text}</text></g>`;
}

function bigText(cx, cy, text, col, fs) {
  const st = `text-anchor="middle" ${FONT} font-size="${fs}" stroke-linejoin="round" letter-spacing="2"`;
  return `<g transform="translate(${cx} ${cy}) skewX(-6) translate(${-cx} ${-cy})">
    <text x="${cx + fs / 14}" y="${cy + fs / 11}" ${st} fill="${NAVY}" stroke="${NAVY}" stroke-width="${fs / 6}">${text}</text>
    <text x="${cx}" y="${cy}" ${st} fill="${col}" stroke="${NAVY}" stroke-width="${fs / 7}" paint-order="stroke">${text}</text></g>`;
}

function nameCard(x, y, num, name, sub, numBg = '#FFD31A') {
  return `<g transform="translate(${x} ${y})">
    <g transform="skewX(-8)">
      <rect x="14" y="14" width="800" height="170" rx="18" fill="#000" opacity=".45"/>
      <rect x="0" y="0" width="800" height="170" rx="18" fill="${NAVY}" stroke="#fff" stroke-width="6"/>
      <rect x="0" y="0" width="34" height="170" rx="10" fill="#2F7FD8"/>
      <rect x="34" y="128" width="766" height="10" fill="#FFD31A"/>
    </g>
    <circle cx="120" cy="80" r="66" fill="${numBg}" stroke="#fff" stroke-width="7"/>
    <text x="120" y="108" text-anchor="middle" ${FONT} font-size="78" fill="${NAVY}">${num}</text>
    <text x="214" y="88" ${FONT} font-size="70" fill="#fff" letter-spacing="1">${name}</text>
    <text x="216" y="122" ${FONT} font-size="30" fill="#FFD31A" letter-spacing="2">${sub}</text></g>`;
}

function optionCard(cx, cy, icon, l1, l2, rot) {
  return `<g transform="rotate(${rot} ${cx} ${cy}) translate(${cx} ${cy}) scale(0.85) translate(${-cx} ${-cy})">
    <rect x="${cx - 150 + 12}" y="${cy - 190 + 14}" width="300" height="380" rx="20" fill="${NAVY}"/>
    <rect x="${cx - 150}" y="${cy - 190}" width="300" height="380" rx="20" fill="#fff" stroke="${NAVY}" stroke-width="8"/>
    <rect x="${cx - 150}" y="${cy - 190}" width="300" height="56" rx="20" fill="#2F7FD8" stroke="${NAVY}" stroke-width="8"/>
    <rect x="${cx - 50}" y="${cy - 212}" width="100" height="36" fill="#FFD31A" opacity=".85" transform="rotate(-4 ${cx} ${cy - 194})"/>
    <g transform="translate(${cx} ${cy - 40}) scale(.9)">${icon}</g>
    <text x="${cx}" y="${cy + 110}" text-anchor="middle" ${FONT} font-size="40" fill="${NAVY}">${l1}</text>
    <text x="${cx}" y="${cy + 158}" text-anchor="middle" ${FONT} font-size="40" fill="${NAVY}">${l2}</text></g>`;
}

// Untertitel: * = gelb, ! = rot
function caption(text, t0, t) {
  if (!text) return '';
  const k = clamp((t - t0) / 0.16, 0, 1);
  const s = 0.82 + 0.18 * backOut(k);
  const words = text.split(' ').map(w => {
    let col = '#fff';
    if (w.startsWith('*')) { col = '#FFD31A'; w = w.slice(1); }
    if (w.startsWith('!')) { col = '#FF5A4A'; w = w.slice(1); }
    return [w, col];
  });
  const len = text.replace(/[*!]/g, '').length;
  const fs = Math.min(100, 900 / (Math.max(len, 6) * 0.74));
  const cx = 510, cy = 1290;
  const sh = words.map(([w]) => w).join(' ');
  const main = words.map(([w, c]) => `<tspan fill="${c}">${w}</tspan>`).join(' ');
  const st = `text-anchor="middle" ${FONT} font-size="${fs}" stroke-linejoin="round" letter-spacing="1"`;
  return `<g transform="translate(${cx} ${cy}) skewX(-6) scale(${s}) translate(${-cx} ${-cy})">
    <text x="${cx + 7}" y="${cy + 10}" ${st} fill="${NAVY}" stroke="${NAVY}" stroke-width="${fs / 5}">${sh}</text>
    <text x="${cx}" y="${cy}" ${st} stroke="${NAVY}" stroke-width="${fs / 5.5}" paint-order="stroke">${main}</text></g>`;
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
