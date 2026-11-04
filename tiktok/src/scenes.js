// Szenen, Hintergruende, UI-Elemente. Leinwand 1080x1920.
const W = 1080, H = 1920;
const FONT = `font-family="Lilita"`;

// ---------- Helfer ----------
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const easeOut = x => 1 - Math.pow(1 - clamp(x, 0, 1), 3);
function backOut(x) { x = clamp(x, 0, 1); const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); }
function pop(t, t0, dur = 0.28) { return t < t0 ? 0 : backOut((t - t0) / dur); }
function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

// ---------- Hintergrund ----------
function sky(t) {
  let clouds = '';
  for (let i = 0; i < 6; i++) {
    const x = ((rnd(i) * 1600 + t * (8 + i * 3)) % 1700) - 300, y = 120 + rnd(i + 9) * 520;
    clouds += `<ellipse cx="${x}" cy="${y}" rx="${260 + rnd(i + 3) * 160}" ry="${50 + rnd(i + 5) * 30}" fill="#232A3E" opacity="0.55"/>`;
  }
  return `<rect x="-400" y="-400" width="${W + 800}" height="${H + 800}" fill="url(#skyG)"/>${clouds}`;
}

function treeline(y) {
  let s = '';
  for (let i = -2; i < 16; i++) {
    const x = i * 90 + rnd(i) * 40, r = 60 + rnd(i + 30) * 40;
    s += `<rect x="${x - 7}" y="${y - 30}" width="14" height="50" fill="#2A2420"/><circle cx="${x}" cy="${y - r * 0.9}" r="${r}" fill="#2C4A36" stroke="#1B2E22" stroke-width="6"/>`;
  }
  return s;
}

function goalPost(x, y, s = 1) {
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <path d="M-160 0 V-150 H160 V0" fill="none" stroke="#111" stroke-width="16"/>
    <path d="M-160 0 V-150 H160 V0" fill="none" stroke="#F3F3F3" stroke-width="9"/>
    <g stroke="#fff" stroke-width="2" opacity=".35">${Array.from({length: 9}, (_, i) => `<path d="M${-140 + i * 35} -146 V0"/>`).join('')}
    <path d="M-156 -100 H156 M-156 -50 H156"/></g></g>`;
}

function field(t, hz = 1060, o = {}) {
  let s = sky(t) + treeline(hz + 6);
  s += `<rect x="-400" y="${hz}" width="${W + 800}" height="${H - hz + 400}" fill="#3F6B32"/>`;
  // Schlamm ueberall
  s += `<path d="M-400 ${hz + 30} Q200 ${hz - 10} 600 ${hz + 40} Q900 ${hz + 10} 1480 ${hz + 30} L1480 ${H + 400} L-400 ${H + 400}Z" fill="#6B4A30"/>`;
  for (let i = 0; i < 14; i++) {
    const x = rnd(i + 40) * 1300 - 100, y = hz + 60 + rnd(i + 50) * (H - hz);
    s += `<ellipse cx="${x}" cy="${y}" rx="${50 + rnd(i) * 80}" ry="${12 + rnd(i + 2) * 12}" fill="#4F8A3E" opacity=".8"/>`;
  }
  if (o.goal !== false) {
    // Tor steht auf der Torlinie, davor Fuenfmeterraum, Strafraum, Elfmeterpunkt und Teilkreis
    const gx = o.goalX || 760, gy = hz + 40;
    s += `<g fill="none" stroke="#F0EDE0" stroke-width="7" stroke-linejoin="round" opacity=".85">
      <path d="M-400 ${gy} H1480"/>
      <path d="M${gx - 200} ${gy} L${gx - 214} ${gy + 46} L${gx + 214} ${gy + 46} L${gx + 200} ${gy}"/>
      <path d="M${gx - 340} ${gy} L${gx - 380} ${gy + 130} L${gx + 380} ${gy + 130} L${gx + 340} ${gy}"/>
      <path d="M${gx - 100} ${gy + 130} Q${gx} ${gy + 175} ${gx + 100} ${gy + 130}"/></g>
      <ellipse cx="${gx}" cy="${gy + 92}" rx="9" ry="5" fill="#F0EDE0" opacity=".85"/>`;
    s += goalPost(gx, gy, 0.9);
  } else if (!o.touchY) s += `<path d="M-400 ${hz + 70} H1480" stroke="#E8E2D0" stroke-width="7" opacity=".45"/>`;
  // Pfuetzen mit Regenringen
  const puddles = o.puddles || [[180, hz + 260, 170, 30], [820, hz + 330, 200, 34], [520, hz + 600, 260, 46], [120, hz + 760, 200, 40], [900, hz + 700, 150, 30]];
  puddles.forEach((p, i) => {
    s += `<ellipse cx="${p[0]}" cy="${p[1]}" rx="${p[2]}" ry="${p[3]}" fill="#4A3828" stroke="#2C2018" stroke-width="6"/>
          <ellipse cx="${p[0] - p[2] * 0.2}" cy="${p[1] - p[3] * 0.2}" rx="${p[2] * 0.45}" ry="${p[3] * 0.3}" fill="#7B8AA3" opacity=".35"/>`;
    for (let k = 0; k < 2; k++) {
      const ph = ((t * 1.4 + rnd(i * 7 + k) * 3) % 1);
      const rx = p[0] + (rnd(i * 3 + k) - 0.5) * p[2], ry = p[1] + (rnd(i * 5 + k) - 0.5) * p[3] * 0.8;
      s += `<ellipse cx="${rx}" cy="${ry}" rx="${8 + ph * 40}" ry="${2 + ph * 9}" fill="none" stroke="#C9D3E3" stroke-width="3" opacity="${0.6 * (1 - ph)}"/>`;
    }
  });
  if (o.touchY) {
    s += `<rect x="-400" y="${hz}" width="${W + 800}" height="${o.touchY - hz}" fill="#4A8038"/>`;
    for (let i = 0; i < 18; i++) {
      const x = rnd(i + 900) * 1300 - 100, y = hz + 10 + rnd(i + 950) * (o.touchY - hz - 20);
      s += `<path d="M${x} ${y} l6 -18 l6 18 l6 -14 l4 14" stroke="#356A2A" stroke-width="5" fill="none" stroke-linejoin="round"/>`;
    }
    s += `<path d="M-400 ${o.touchY} H1480" stroke="#F0EDE0" stroke-width="11"/>`;
  }
  return s;
}

function rain(t, n = 150, op = 0.5) {
  let s = '';
  for (let i = 0; i < n; i++) {
    const sp = 1500 + rnd(i) * 900, len = 40 + rnd(i + 1) * 50;
    const x0 = rnd(i + 2) * (W + 300);
    const y = ((rnd(i + 3) * (H + 200) + t * sp) % (H + 200)) - 100;
    const x = x0 - (y + 100) * 0.12;
    s += `<path d="M${x.toFixed(1)} ${y.toFixed(1)} l${(-len * 0.12).toFixed(1)} ${len.toFixed(1)}"/>`;
  }
  return `<g stroke="#D6E2F2" stroke-width="3" stroke-linecap="round" opacity="${op}">${s}</g>`;
}

// ---------- Requisiten ----------
function flashMast(x, base, top, t, flick) {
  const on = flick ? (Math.sin(t * 37) + Math.sin(t * 13.3) > -0.6 ? 1 : 0.15) : 1;
  return `
  <path d="M${x + 30} ${top + 40} L${x + 520} ${base + 40} L${x - 300} ${base + 40} Z" fill="#FFF6B0" opacity="${0.22 * on}"/>
  <rect x="${x - 14}" y="${top}" width="28" height="${base - top}" fill="#7A5232" stroke="#111" stroke-width="7"/>
  <rect x="${x - 18}" y="${top + 160}" width="36" height="26" fill="#B8B8B8" stroke="#111" stroke-width="5"/>
  <rect x="${x - 18}" y="${top + 420}" width="36" height="26" fill="#B8B8B8" stroke="#111" stroke-width="5"/>
  <g transform="translate(${x} ${top}) rotate(28)">
    <rect x="-22" y="-80" width="44" height="100" rx="8" fill="#2A2A2E" stroke="#111" stroke-width="7"/>
    <path d="M-34 20 L34 20 L28 60 L-28 60 Z" fill="#FFD31A" stroke="#111" stroke-width="7" stroke-linejoin="round"/>
    <ellipse cx="0" cy="60" rx="26" ry="9" fill="${on > 0.5 ? '#FFFBE0' : '#888'}" stroke="#111" stroke-width="5"/>
    <rect x="-8" y="-50" width="16" height="22" rx="4" fill="#E8432E" stroke="#111" stroke-width="4"/>
  </g>
  <rect x="${x - 26}" y="${top + 10}" width="52" height="22" fill="#B8B8B8" stroke="#111" stroke-width="5" transform="rotate(-8 ${x} ${top + 20})"/>`;
}

function trophy(cx, cy, s) {
  return `<g transform="translate(${cx} ${cy}) scale(${s})">
    <path d="M-120 -160 H120 Q120 -10 0 20 Q-120 -10 -120 -160Z" fill="#FFC81A" stroke="#111" stroke-width="10"/>
    <path d="M-120 -130 Q-200 -130 -180 -70 Q-160 -20 -100 -40" fill="none" stroke="#111" stroke-width="22"/>
    <path d="M-120 -130 Q-200 -130 -180 -70 Q-160 -20 -100 -40" fill="none" stroke="#FFC81A" stroke-width="10"/>
    <path d="M120 -130 Q200 -130 180 -70 Q160 -20 100 -40" fill="none" stroke="#111" stroke-width="22"/>
    <path d="M120 -130 Q200 -130 180 -70 Q160 -20 100 -40" fill="none" stroke="#FFC81A" stroke-width="10"/>
    <rect x="-24" y="18" width="48" height="60" fill="#FFC81A" stroke="#111" stroke-width="10"/>
    <rect x="-90" y="76" width="180" height="44" rx="8" fill="#8A5A36" stroke="#111" stroke-width="10"/>
    <path d="M-70 -140 Q-80 -60 -30 -20" stroke="#FFF2A8" stroke-width="12" fill="none" stroke-linecap="round"/>
  </g>`;
}


function crate(cx, cy, s) {
  return `<g transform="translate(${cx} ${cy}) scale(${s})">
    <rect x="-210" y="0" width="420" height="200" fill="#A8743F" stroke="#111" stroke-width="10"/>
    <path d="M-210 66 H210 M-210 133 H210" stroke="#111" stroke-width="7"/>
    <path d="M-200 10 L200 190" stroke="#8A5A30" stroke-width="12"/></g>`;
}

function busStop(x, base, s) {
  return `<g transform="translate(${x} ${base}) scale(${s})">
    <rect x="-10" y="-520" width="20" height="520" fill="#9A9A9A" stroke="#111" stroke-width="6"/>
    <circle cx="0" cy="-520" r="70" fill="#FFD31A" stroke="#2FB34A" stroke-width="14"/><circle cx="0" cy="-520" r="77" fill="none" stroke="#111" stroke-width="6"/>
    <text x="0" y="-492" text-anchor="middle" ${FONT} font-size="80" fill="#2FB34A">H</text>
</g>`;
}

// ---------- UI ----------



function profileCard(x, y, fans, followed) {
  return `<g transform="translate(${x} ${y})">
    <rect x="8" y="10" width="860" height="330" rx="34" fill="#000" opacity=".6"/>
    <rect x="0" y="0" width="860" height="330" rx="34" fill="#16181F" stroke="#fff" stroke-width="6"/>
    <text x="50" y="96" ${FONT} font-size="66" fill="#fff">FC Schlammloch</text>
    <text x="52" y="150" font-family="Inter" font-weight="700" font-size="36" fill="#9AA0AE">Tag 1 · Kreisliga</text>
    <text x="52" y="222" ${FONT} font-size="54" fill="${fans ? '#5BE35B' : '#FF4A4A'}">${fans}</text>
    <text x="${fans > 9 ? 130 : 100}" y="222" ${FONT} font-size="44" fill="#fff">Fans</text>
    <rect x="50" y="248" width="420" height="64" rx="16" fill="${followed ? '#3A3D48' : '#FE2C55'}"/>
    <text x="260" y="292" text-anchor="middle" ${FONT} font-size="38" fill="#fff">${followed ? 'Gefolgt ✓' : 'Folgen'}</text>
    <g transform="translate(720 160) scale(0.38) translate(-300 -300)">${LOGO}</g></g>`;
}

function commentCard(x, y) {
  return `<g transform="translate(${x} ${y})">
    <rect x="8" y="10" width="900" height="250" rx="34" fill="#000" opacity=".5"/>
    <rect x="0" y="0" width="900" height="250" rx="34" fill="#fff" stroke="#111" stroke-width="7"/>
    <circle cx="90" cy="92" r="50" fill="#C9CED8" stroke="#111" stroke-width="5"/>
    <circle cx="90" cy="78" r="18" fill="#fff"/><path d="M58 126 Q90 90 122 126" fill="#fff"/>
    <text x="164" y="80" font-family="Inter" font-weight="700" font-size="38" fill="#888">dein Name</text>
    <rect x="380" y="46" width="250" height="48" rx="14" fill="#FE2C55"/>
    <text x="505" y="81" text-anchor="middle" ${FONT} font-size="30" fill="#fff">Top-Kommentar</text>
    <text x="164" y="160" ${FONT} font-size="64" fill="#111">deine Idee?</text>
    <text x="164" y="220" font-family="Inter" font-weight="700" font-size="32" fill="#999">♥ 0 · Antworten</text>
    <path d="M820 70 c-20 -26 -56 -6 -40 20 l40 40 l40 -40 c16 -26 -20 -46 -40 -20z" fill="#FE2C55"/></g>`;
}

const ICON_BOOT = `<path d="M-70 -70 L-10 -70 L-6 0 Q40 6 70 30 Q80 60 50 60 L-70 60Z" fill="#222" stroke="#111" stroke-width="8" stroke-linejoin="round"/>
  <path d="M-50 70 v14 M-10 70 v14 M30 70 v14" stroke="#111" stroke-width="10" stroke-linecap="round"/><path d="M-60 -20 H-10 M-60 10 H0" stroke="#FFD31A" stroke-width="8"/>`;
const ICON_HOUSE = `<path d="M-90 -10 L0 -90 L90 -10Z" fill="#E8432E" stroke="#111" stroke-width="8" stroke-linejoin="round"/>
  <rect x="-70" y="-10" width="140" height="100" fill="#F3D9A4" stroke="#111" stroke-width="8"/>
  <rect x="-22" y="30" width="44" height="60" fill="#8A5A36" stroke="#111" stroke-width="6"/><rect x="34" y="10" width="28" height="28" fill="#9FC9EE" stroke="#111" stroke-width="5"/>`;
const ICON_Q = `<circle cx="0" cy="0" r="86" fill="#FFD31A" stroke="#111" stroke-width="8"/><text x="0" y="44" text-anchor="middle" ${FONT} font-size="130" fill="#111">?</text>`;

// Untertitel: Woerter mit * gruen, mit ! rot
