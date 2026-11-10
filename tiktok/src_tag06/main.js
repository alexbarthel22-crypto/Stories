// Tag 2 – Zeitachse und Szenen. DATA = {fps, segs:[{id,start,end,caps}], env, total}
let LT = 0, LD = 1, NOPUD = false;
function cam(z, cx, cy, inner) {
  const zz = z * (1 + 0.05 * clamp(LT / LD, 0, 1)), rr = Math.sin(LT * 1.3) * 0.6;
  return `<g transform="translate(540 960) rotate(${rr}) scale(${zz}) translate(${-cx} ${-cy})">${inner}</g>`;
}
function blinkAt(t, off = 0) { return ((t + off) % 3.3) < 0.12; }

// Ball fliegt zu Beginn von unten links ins Bild, trifft bei t=0.3 das TAG-Feld und springt oben rechts raus
function introBall(t) {
  if (t > 0.8) return '';
  let x, y, r;
  if (t <= 0.3) { const k = t / 0.3; x = -120 + k * 900; y = 1250 - Math.sin(k * Math.PI / 2) * 950; r = 95 - k * 25; }
  else { const k = (t - 0.3) / 0.5; x = 780 + k * 520; y = 300 - k * 560 + k * k * 120; r = 70; }
  return `<g transform="translate(${x} ${y}) rotate(${t * 900})">${ballIcon(0, 0, r)}</g>`;
}
const capT = i => SEG.caps[Math.min(i, SEG.caps.length - 1)].t0 - SEG.start;

function moth(t, t0) {
  if (t < t0) return '';
  const k = t - t0, x = 560 + Math.sin(k * 5) * 60 + k * 80, y = 860 - k * 260, w = Math.sin(k * 30) * 0.5 + 0.6;
  return `<g transform="translate(${x} ${y})"><ellipse cx="-16" cy="0" rx="${18 * w}" ry="12" fill="#C8B9A0" stroke="#111" stroke-width="4"/>
    <ellipse cx="16" cy="0" rx="${18 * w}" ry="12" fill="#C8B9A0" stroke="#111" stroke-width="4"/><ellipse rx="5" ry="12" fill="#6B5A44"/></g>`;
}


function chairTribune(t) {
  let s = chairRows(9, 95, 800, 10, 8, 99, 66, 0.17, 0, 0);
  s += seatedCrowd(99, 95, 800, 10, 8, 99, 66, 0.17, 0, 0, [74, 75, 76]);
  [0, 1, 2].forEach(i => { const x = 95 + (4 + i) * 99 + 0.5 * 99 - 99 * 0.25; s += place(fanFigure(Object.assign({blink: blinkAt(t, i)}, FIRST_FANS[i].o), true), x, 800 + 7 * 66, 0.17 * 1.56 * 0.62); });
  return s + tarp(t, 45, 1035, 610, 1310, 1);
}

function confetti(t, t0, n = 46) {
  if (t < t0) return '';
  const k = t - t0, cols = ['#FFD31A', '#2F7FD8', '#E5483A', '#58B044', '#FF7EB6', '#fff'];
  let s = '';
  for (let i = 0; i < n; i++) {
    const x = rnd(i + 1200) * 1080 + Math.sin(k * 3 + i) * 30, y = -50 + (k * (500 + rnd(i + 1300) * 500)) - rnd(i + 1400) * 300;
    if (y < -60 || y > 1960) continue;
    s += `<rect x="${x}" y="${y}" width="16" height="26" rx="3" fill="${cols[i % 6]}" stroke="#3A2316" stroke-width="2" transform="rotate(${k * 300 + i * 40} ${x} ${y})"/>`;
  }
  return s;
}

// Bewerbungs-Box mit fliegenden Umschlaegen (wiederverwendbar)
function bewerbungen(t, t0, y) {
  if (t < t0) return '';
  const pulse = 0.5 + 0.5 * Math.sin(t * 10);
  let letters = '';
  for (let i = 0; i < 8; i++) { const k = (t - t0 - i * 0.12) / 0.7;
    if (k > 0 && k < 1) { const x0 = 80 + rnd(i + 60) * 900, x = x0 + (540 - x0) * k, yy = 1800 - k * (1800 - y), fl = Math.cos(k * 8);
      letters += `<g transform="translate(${x} ${yy}) rotate(${(1 - k) * 35 * (i % 2 ? 1 : -1)}) scale(${0.85 - k * 0.35} ${(0.85 - k * 0.35) * Math.max(0.15, Math.abs(fl))})"><rect x="-60" y="-40" width="120" height="80" rx="8" fill="#fff" stroke="#3A2316" stroke-width="6"/>${fl > 0 ? '<path d="M-60 -40 L0 10 L60 -40" stroke="#3A2316" stroke-width="6" fill="none"/><circle cx="34" cy="16" r="10" fill="#E5483A"/>' : ''}</g>`; } }
  return popG(t, t0, 540, y, `<g transform="translate(540 ${y}) scale(${1 + 0.05 * pulse}) translate(-540 ${-y})">${box(170, y - 65, 740, 130, 'red', 10)}
    ${label(500, y + 25, 'BEWERBUNGEN', 72, '#fff')}<text x="830" y="${y + 30 + 10 * Math.abs(Math.sin(t * 6))}" text-anchor="middle" font-family="Noto Color Emoji" font-size="68">👇</text></g>`) + letters;
}


// ---------- Tag 5: Spieltag ----------
function sleepyOpa(t, x, y, s, awake) {
  let z = '';
  if (!awake) for (let k = 0; k < 3; k++) { const ph = (t * 0.6 + k / 3) % 1; z += `<text x="${x + 60 * s + ph * 80 * s}" y="${y - 520 * s - ph * 160 * s}" ${FONT} font-size="${(40 + ph * 30) * s * 2}" fill="#fff" opacity="${1 - ph}" stroke="#3A2316" stroke-width="4" paint-order="stroke">Z</text>`; }
  const body = rockingOpa(t).replace(/<circle cx="(195|305)" cy="215" r="36" fill="#fff" stroke="#111" stroke-width="8"\/>/g, awake ? '$&' : '<path d="M$1 215 m-28 0 q28 18 56 0" stroke="#111" stroke-width="8" fill="none"/>');
  return place(body, x, y, s) + z;
}
function heu(o = {}) {
  return player(Object.assign({jersey: '#E8C24A', trim: '#6B8E23', num: '7', shorts: '#6B8E23', socks: '#E8C24A', skin: '#F2C9A0', browCol: '#8A6A2A',
    hair: `<path d="M100 200 Q100 74 250 72 Q400 74 400 200 Q380 132 250 128 Q120 132 100 200Z" fill="#E8C870"/>`,
    hairOver: `<path d="M150 96 l-14 -40 M200 80 l-6 -44 M250 76 l0 -46 M300 80 l6 -44 M350 96 l14 -40" stroke="#C9A040" stroke-width="10" stroke-linecap="round"/>`,
    mood: 'smile'}, o));
}
function heuKeeper(o = {}) { return heu(Object.assign({jersey: '#E5483A', trim: '#fff', num: '1', socks: '#E5483A', gloves: true}, o)); }
function co13(o = {}) {
  return player(Object.assign({jersey: '#2A2A2E', trim: '#2F7FD8', num: '13', shorts: '#2A2A2E', socks: '#2A2A2E', skin: '#E2B48C', browCol: '#111',
    hair: `<path d="M104 170 Q120 66 250 66 Q380 66 396 170 Z" fill="#2F7FD8"/>`,
    hairOver: `<path d="M110 168 Q60 168 40 186 L250 186 Z" fill="#2F7FD8" stroke="#111" stroke-width="7" stroke-linejoin="round"/>
      <text x="250" y="140" text-anchor="middle" ${FONT} font-size="54" fill="#FFD31A">13</text>`,
    front: `<path d="M214 360 Q250 420 286 360" stroke="#E5483A" stroke-width="5" fill="none"/><rect x="236" y="410" width="30" height="16" rx="6" fill="#C0C6CC" stroke="#111" stroke-width="4"/>
      <g transform="translate(380 470) rotate(12)"><rect x="-50" y="-66" width="100" height="132" rx="10" fill="#A8743F" stroke="#111" stroke-width="6"/><rect x="-38" y="-50" width="76" height="104" fill="#fff"/>
      <circle cx="-14" cy="-20" r="8" fill="none" stroke="#2F7FD8" stroke-width="4"/><path d="M8 -28 l14 14 M22 -28 l-14 14" stroke="#E5483A" stroke-width="4"/></g>`,
    mood: 'smile'}, o));
}
function scoreBug(us, them, lbl) {
  return `<g>${box(150, 250, 780, 130, 'white', 9)}
    <g transform="translate(225 315) scale(0.17) translate(-300 -300)">${LOGO}</g>
    ${label(540, 345, `${us} : ${them}`, 84, BROWN)}
    ${heuLogo(855, 315, 0.25)}
    <rect x="430" y="384" width="220" height="44" rx="12" fill="#3A2316"/>${label(540, 416, lbl, 28, '#fff')}</g>`;
}
function goalLines(gx, gy) {
  return `<g fill="none" stroke="#F0EDE0" stroke-width="7" opacity=".85"><path d="M-400 ${gy} H1480"/><path d="M${gx - 520} ${gy} L${gx - 560} ${gy + 180} L${gx + 560} ${gy + 180} L${gx + 520} ${gy}"/><path d="M${gx - 240} ${gy} L${gx - 250} ${gy + 70} L${gx + 250} ${gy + 70} L${gx + 240} ${gy}"/></g>`;
}
function netShake(gx, gy, t, t0) {
  if (t < t0 || t > t0 + 0.6) return '';
  const a = Math.sin((t - t0) * 40) * 10 * (1 - (t - t0) / 0.6);
  return `<g stroke="#fff" stroke-width="4" opacity=".7">${Array.from({length: 7}, (_, i) => `<path d="M${gx - 300 + i * 100 + a} ${gy - 360} Q${gx - 300 + i * 100 - a} ${gy - 180} ${gx - 300 + i * 100 + a} ${gy - 10}" fill="none"/>`).join('')}</g>`;
}
// Torszene: shooter vorne, Keeper im Tor; tg = Zeit des Treffers, endX = Zielpunkt, saved = gehalten
function shotScene(t, shooter, keeper, tShot, tg, endX, saved, keeperDir) {
  const gx = 540, gy = 1330;
  const k = clamp((t - tShot) / (tg - tShot), 0, 1);
  const bx = 470 + (endX - 470) * k, by = 1700 - (1700 - (gy - 200)) * k - Math.sin(k * Math.PI) * 120;
  const dive = clamp((t - tShot - 0.15) / 0.35, 0, 1);
  const kx = gx + keeperDir * 220 * dive;
  let s = field(LT, 900, {goal: false}) + goalLines(gx, gy) + goalPost(gx, gy, 2.6) + netShake(gx, gy, t, saved ? 99 : tg);
  s += `<g transform="rotate(${keeperDir * 70 * dive} ${kx} ${gy - 120})">${place(keeper, kx, gy, 0.48)}</g>`;
  if (!(saved && t > tg)) s += `<g transform="translate(${bx} ${by}) rotate(${t * 700})">${ballIcon(0, 0, 32)}</g>`;
  else s += `<g transform="translate(${kx + keeperDir * 60} ${gy - 220})">${ballIcon(0, 0, 32)}</g>`;
  s += place(shooter, 360, 1760, 0.8);
  return s;
}
function goalFlash(t, tg, txt, col) {
  if (t < tg) return '';
  const k = t - tg;
  return (k < 0.25 ? `<rect width="1080" height="1920" fill="#fff" opacity="${0.8 * (1 - k / 0.25)}"/>` : '') +
    popG(t, tg, 540, 760, `<g transform="rotate(-6 540 760)">${bigText(540, 820, txt, col, 190)}</g>`);
}
const SCENES = {
  intro(t, d, m) {
    const k = clamp(t / d, 0, 1), e = k * k * (3 - 2 * k), z = 0.7 + 0.3 * e;
    const world = field(t, 900, {goal: false, touchY: 1210}) + `<g transform="translate(0 450)">${bigStand(t, 1, 1)}</g>` +
      place(coach({mouth: m, blink: blinkAt(t)}), 540, 1420, 0.72) +
      place(frog({blink: blinkAt(t, .4)}), 760, 1430 - Math.abs(Math.sin(t * 7)) * 30, 0.2);
    return cam(z, 540, 1110 - 40 * e, world) +
      `<g transform="rotate(${t > 0.3 ? Math.sin((t - 0.3) * 40) * 6 * Math.exp(-(t - 0.3) * 7) : 0} 540 440)">${badge(540, 440, 'TAG 6', {kind: 'pitch', fs: 150, pad: 120})}</g>` +
      twoLineBadge(540, 640, 'ICH GRÜNDE EINEN', 'FUSSBALLVEREIN', 52) +
      introBall(t);
  },
  fans6(t, d, m) {
    const t0 = capT(2), n = t < t0 ? 494 : Math.round(494 + 19 * easeOut(clamp((t - t0) / 0.7, 0, 1)));
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 820}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 420, 1640, 1.2)) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'GESTERN: 494 FANS', {fs: 46})) +
      popG(t, t0, 540, 500, badge(540, 500, 'HEUTE', {kind: 'pitch', fs: 56})) +
      (t >= t0 ? bigText(540, 760, String(n), '#6BF06B', 240) : '') +
      popG(t, t0 + 0.7, 800, 640, `<g transform="translate(800 640)"><circle r="70" fill="#3A2316"/><circle r="62" fill="#58B044" stroke="#fff" stroke-width="7"/>
        <path d="M0 -40 L32 0 L14 0 L14 34 L-14 34 L-14 0 L-32 0 Z" fill="#fff" stroke="#3A2316" stroke-width="4" stroke-linejoin="round"/></g>` + badge(800, 750, '+19', {kind: 'pitch', fs: 44})) + confetti(t, t0 + 0.7);
  },
  voteres(t, d, m) {
    const k = easeOut(clamp((t - capT(1)) / 0.5, 0, 1));
    const iconGrill = `<g transform="translate(0 30) scale(0.5)">${grill(0, 0, 1, t)}</g>`;
    const iconCab = `<g transform="translate(0 70) scale(0.3)">${bauwagen(0, 0, 1)}</g>`;
    const winner = t >= capT(1);
    return cam(1.0, 540, 960, field(t, 1080, {goal: false})) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'ABSTIMMUNG', {kind: 'orange', fs: 60})) +
      `<g opacity="${winner ? 0.35 : 1}" transform="translate(285 760) scale(${winner ? 1.25 - 0.25 * k : 1.25}) translate(-285 -760)">${optionCard(285, 760, iconGrill, 'WÜRSTCHEN-', 'STAND', -5)}</g>` +
      `<g transform="translate(775 760) scale(${1.25 + 0.2 * k}) translate(-775 -760)">${optionCard(775, 760, iconCab, 'SPIELER-', 'KABINE', 5)}</g>` +
      (winner ? popG(t, capT(2), 775, 1040, badge(775, 1040, 'GEWINNER!', {kind: 'pitch', fs: 52, rot: -4})) + confetti(t, capT(2), 50) : '');
  },
  money6(t, d, m) {
    const lines = [['19 FOLLOWER × 1 €', '+19 €'], ['24 KOMMENTARE × 2 €', '+48 €'], ['ALTE KASSE', '+2532 €'], ['VEREINSKASSE', '2599 €', '#2FA84A', true]];
    const t4 = capT(4);
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(coach({mouth: m, wave: t > t4 ? Math.sin(t * 10) : 0, blink: blinkAt(t)}), 540, 1680, 1.0)) +
      popG(t, 0.0, 540, 340, calcBoard(t, 70, 260, lines, [capT(0), capT(1), capT(2), t4])) +
      (t >= t4 ? `<path d="M110 ${260 + 106 + 220 + 30} H890" stroke="#3A2316" stroke-width="7"/>` : '') + confetti(t, t4, 30);
  },
  buy(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080, {goal: false}) + cabin(560, 1300, 0.95, 1, t) + place(coach({mouth: m, blink: blinkAt(t)}), 170, 1680, 0.8)) +
      popG(t, capT(0), 600, 520, priceTag(600, 560, 1.15, t, 'SPIELERKABINE', '-1500 €')) +
      popG(t, capT(2), 540, 860, badge(540, 860, 'KASSE: 1099 €', {kind: 'pitch', fs: 56, rot: -2}));
  },
  build(t, d, m) {
    const b = clamp(t / (capT(2) + 0.1), 0, 1);
    let s = field(t, 1080, {goal: false}) + cabin(560, 1300, 0.95, b, t);
    s += place(luca({blink: blinkAt(t)}), 160, 1700 - Math.abs(Math.sin(t * 8)) * 20, 0.75);
    s += place(lkz({}), 900, 1720 - Math.abs(Math.sin(t * 8 + 1)) * 20, 0.65, true);
    s += place(frog({blink: blinkAt(t)}), 560, 1760 - Math.abs(Math.sin(t * 7)) * 40, 0.3);
    const hammer = `<g transform="translate(260 1420) rotate(${-30 + 50 * Math.abs(Math.sin(t * 10))})"><rect x="-8" y="-120" width="16" height="130" rx="6" fill="#8A5A36" stroke="#3A2316" stroke-width="5"/><rect x="-40" y="-150" width="80" height="40" rx="6" fill="#6C737B" stroke="#3A2316" stroke-width="5"/></g>`;
    return cam(1.0, 540, 960, s + hammer) + popG(t, 0.0, 540, 360, badge(540, 360, 'AUFBAU!', {kind: 'pitch', fs: 70, rot: -2})) +
      popG(t, capT(3), 540, 760, `<g>${box(260, 680, 560, 180, 'red', 10)}${screw(380, 760, 1.6, -20)}${label(600, 800, 'FEHLT!', 80, '#fff')}</g>`);
  },
  inside(t, d, m) {
    let s = `<rect width="1080" height="1920" fill="#D9D2C2"/><rect y="1380" width="1080" height="540" fill="#A8743F"/>
      ${Array.from({length: 10}, (_, i) => `<path d="M${i * 120} 1380 V1920" stroke="#8A5A36" stroke-width="5"/>`).join('')}
      <path d="M0 1380 H1080" stroke="#3A2316" stroke-width="10"/>`;
    const names = [['VLAD', '#2FB34A'], ['DENNY', '#2F7FD8'], ['LEBERKAAS', '#2F7FD8'], ['NICO', '#2F7FD8'], ['LUCA', '#6B7A3A']];
    names.forEach(([n, c], i) => { if (t >= capT(1) + i * 0.15) s += locker(140 + i * 160, 1380, n, c); });
    if (t >= capT(2)) s += `<g transform="translate(950 1380)"><rect x="-90" y="-560" width="180" height="560" fill="#BFE0F2" stroke="#3A2316" stroke-width="7" opacity=".85"/>
      <path d="M-40 -540 h80 v30 h-80z" fill="#9AA0A8" stroke="#3A2316" stroke-width="5"/>
      ${Array.from({length: 10}, (_, i) => { const ph = (t * 2 + i / 10) % 1; return `<path d="M${-30 + (i % 5) * 15} ${-500 + ph * 460} v24" stroke="#5AA9E6" stroke-width="5" stroke-linecap="round"/>`; }).join('')}</g>`;
    if (t >= capT(4)) s += `<g transform="translate(540 1520)"><ellipse rx="160" ry="40" fill="#E5483A" stroke="#3A2316" stroke-width="7"/><text y="10" text-anchor="middle" ${FONT} font-size="30" fill="#fff">FRODO</text></g>` + place(frog({blink: blinkAt(t), mouth: true}), 540, 1520 - Math.abs(Math.sin(t * 6)) * 30, 0.32);
    return cam(1.0, 540, 960, s) + popG(t, 0.0, 540, 400, badge(540, 400, 'IN DER KABINE', {kind: 'orange', fs: 60}));
  },
  nico(t, d, m) {
    const t1 = capT(2);
    if (t < t1) return cam(1.0, 540, 960, field(t, 1080, {goalX: 780})) +
      popG(t, 0.0, 540, 380, badge(540, 380, 'NEUZUGANG', {kind: 'red', fs: 56})) +
      popG(t, 0.2, 520, 640, `<g transform="translate(70 520) scale(0.9) translate(-70 -520)">${commentReplica(70, 520, t, NICO_PIC, 'Nico', '', 'Bitte kann ich rechter flügel')}</g>`);
    const tt = t - t1;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 780}) + place(nico({blink: blinkAt(t)}), 540, 1660 - Math.abs(Math.sin(tt * 8)) * 20 * Math.exp(-tt * 2), 1.45)) +
      popG(tt, 0.0, 500, 600, nameCard(80, 520, '17', 'NICO', 'RECHTER FLÜGEL · NEU')) +
      popG(tt, 0.3, 760, 450, `<g transform="rotate(12 760 450)">${badge(760, 450, 'NEU!', {kind: 'red', fs: 60})}</g>`) + confetti(t, t1 + 0.1, 30);
  },
  denny6(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 780}) + place(denny({blink: blinkAt(t), mood: 'talk', mouth: 0.6}), 540, 1700, 1.2)) +
      popG(t, 0.2, 520, 560, `<g transform="translate(70 440) scale(0.9) translate(-70 -440)">${commentReplica(70, 440, t, DENNY_PIC, 'Denny', '🇰🇿🛡️🪄', 'kann ich bitte kürzere haare haben')}</g>`);
  },
  vote6(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    const card = (cx, rot, svg, l1, l2) => `<g transform="rotate(${rot} ${cx} 760)">${box(cx - 170, 520, 340, 480, 'white', 10)}
      <defs><clipPath id="vc${cx}"><rect x="${cx - 160}" y="530" width="320" height="360" rx="20"/></clipPath></defs>
      <g clip-path="url(#vc${cx})"><rect x="${cx - 160}" y="530" width="320" height="360" fill="#BFE0F2"/>${place(svg, cx, 1000, 0.62)}</g>
      ${label(cx, 950, l1, 52, BROWN)}</g>`;
    return cam(1.0, 540, 960, field(t, 1080, {goal: false})) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'DENNYS FRISUR?', {kind: 'orange', fs: 60})) +
      popG(t, c[1], 260, 760, card(260, -4, dennyShort({}), 'KÜRZER', '')) +
      popG(t, c[2] - 0.2, 530, 780, bigText(530, 800, 'ODER', '#fff', 52)) +
      popG(t, c[2], 800, 760, card(800, 4, dennyLong({}), 'LÄNGER', '')) +
      (t >= c[3] ? `<g opacity="${Math.sin(t * 14) > -0.3 ? 1 : 0.3}">${badge(530, 1110, 'ABSTIMMEN IN DEN KOMMENTAREN 👇', {kind: 'red', fs: 36})}</g>` : '');
  },
  rule3(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    let coins = '';
    for (let i = 0; i < 10; i++) { const t0 = c[0] + 0.1 + i * 0.3, k = (t - t0) / 0.6, two = t0 >= c[1]; if (k > 0 && k < 1) coins += coin(470 + rnd(i + 700) * 140, 560 + k * 340, two ? 36 : 30, two); }
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + crate(540, 1180, 0.95) + cashBox(540, 1015, 0.8, 'empty') + coins +
        place(coach({mouth: m, blink: blinkAt(t)}), 170, 1600, 0.85)) +
      popG(t, c[0], 520, 400, badge(520, 400, '+1 € PRO FOLLOWER', {kind: 'pitch', fs: 50})) +
      popG(t, c[1], 520, 530, badge(520, 530, '+2 € PRO KOMMENTAR', {kind: 'orange', fs: 50, rot: -2}));
  },
};

let SEG = null;
function render(f) {
  UID = 0; PID = 0;
  const t = f / DATA.fps;
  let si = DATA.segs.findIndex(s => t < s.end);
  if (si < 0) si = DATA.segs.length - 1;
  SEG = DATA.segs[si];
  const lt = t - SEG.start, d = SEG.end - SEG.start;
  const m = DATA.env[Math.min(f, DATA.env.length - 1)] || 0;
  LT = lt; LD = d; NOPUD = true;
  let body = SCENES[SEG.id](lt, d, m);
  let r = rain(t, 150, 0.45);
  if (false) r = `<defs><mask id="tm"><rect width="1080" height="1920" fill="#fff"/><rect x="20" y="670" width="1040" height="640" fill="#000"/></mask></defs><g mask="url(#tm)">${r}</g>`;
  body += r;
  const cap = SEG.caps.find(c => t >= c.t0 && t < c.t1) || (t >= SEG.caps[SEG.caps.length - 1].t0 ? SEG.caps[SEG.caps.length - 1] : null);
  if (cap) body += caption(cap.text, cap.t0, t);
  if (si > 0) body += mudWipe(lt);
  document.getElementById('root').innerHTML = `<defs><linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2438"/><stop offset="1" stop-color="#46506A"/></linearGradient>
    <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient></defs>
    ${body}<rect width="1080" height="1920" fill="url(#vig)"/>`;
}
