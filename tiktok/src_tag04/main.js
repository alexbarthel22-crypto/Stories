// Tag 2 – Zeitachse und Szenen. DATA = {fps, segs:[{id,start,end,caps}], env, total}
let LT = 0, LD = 1;
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

const SCENES = {
  intro(t, d, m) {
    const k = clamp(t / d, 0, 1), e = k * k * (3 - 2 * k), z = 0.7 + 0.3 * e;
    const world = field(t, 900, {goal: false, touchY: 1210}) + `<g transform="translate(0 450)">${bigStand(t, 1, 1)}</g>` +
      place(coach({mouth: m, blink: blinkAt(t)}), 540, 1420, 0.72) +
      place(frog({blink: blinkAt(t, .4)}), 760, 1430 - Math.abs(Math.sin(t * 7)) * 30, 0.2);
    return cam(z, 540, 1110 - 40 * e, world) +
      `<g transform="rotate(${t > 0.3 ? Math.sin((t - 0.3) * 40) * 6 * Math.exp(-(t - 0.3) * 7) : 0} 540 440)">${badge(540, 440, 'TAG 4', {kind: 'pitch', fs: 150, pad: 120})}</g>` +
      twoLineBadge(540, 640, 'ICH GRÜNDE EINEN', 'FUSSBALLVEREIN', 52) +
      introBall(t);
  },
  fans4(t, d, m) {
    const t0 = capT(2), n = t < t0 ? 428 : Math.round(428 + 50 * easeOut(clamp((t - t0) / 0.8, 0, 1)));
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 820}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 420, 1640, 1.2)) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'GESTERN: 428 FANS', {fs: 46})) +
      popG(t, t0, 540, 500, badge(540, 500, 'HEUTE', {kind: 'pitch', fs: 56})) +
      (t >= t0 ? bigText(540, 760, String(n), '#6BF06B', 240) : '') +
      popG(t, t0 + 0.8, 800, 640, `<g transform="translate(800 640)"><circle r="70" fill="#3A2316"/><circle r="62" fill="#58B044" stroke="#fff" stroke-width="7"/>
        <path d="M0 -40 L32 0 L14 0 L14 34 L-14 34 L-14 0 L-32 0 Z" fill="#fff" stroke="#3A2316" stroke-width="4" stroke-linejoin="round"/></g>` + badge(800, 750, '+50', {kind: 'pitch', fs: 44})) + confetti(t, t0 + 0.8);
  },
  luca(t, d, m) {
    const t1 = capT(2);
    if (t < t1) return cam(1.0, 540, 960, field(t, 1080, {goalX: 780})) +
      popG(t, 0.0, 540, 380, badge(540, 380, 'TOP-KOMMENTAR', {kind: 'red', fs: 50})) +
      popG(t, 0.2, 520, 640, `<g transform="translate(70 520) scale(0.9) translate(-70 -520)">${commentReplica(70, 520, t, LUCA_PIC, 'luca', '🦈', 'ich will Platzwart liekt bitte')}</g>`);
    const tt = t - t1;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 780}) + place(luca({blink: blinkAt(t)}), 540, 1660 - Math.abs(Math.sin(tt * 8)) * 20 * Math.exp(-tt * 2), 1.45)) +
      popG(tt, 0.0, 500, 600, nameCard(80, 520, '🧹', 'LUCA', 'PLATZWART · NEUZUGANG').replace('font-size="84" fill="#fff">🧹', 'font-size="60" fill="#fff" font-family="Noto Color Emoji">🧹')) +
      popG(tt, 0.3, 760, 450, `<g transform="rotate(12 760 450)">${badge(760, 450, 'NEU!', {kind: 'red', fs: 60})}</g>`) + confetti(t, t1 + 0.1, 30);
  },
  denny(t, d, m) {
    const t1 = capT(3);
    if (t < t1) return cam(1.0, 540, 960, field(t, 1080, {goalX: 780})) +
      popG(t, 0.0, 540, 380, badge(540, 380, 'TOP-KOMMENTAR', {kind: 'red', fs: 50})) +
      popG(t, 0.2, 520, 640, `<g transform="translate(70 520) scale(0.9) translate(-70 -520)">${commentReplica(70, 520, t, DENNY_PIC, 'Denny', '🇰🇿🛡️🪄', 'kann ich verteidiger')}</g>`) +
      popG(t, capT(2), 540, 1050, jerseyNum(540, 1100, 0.5, Math.sin(t * 2) * 4, '4', 'ABWEHR'));
    const tt = t - t1;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 780}) + place(denny({blink: blinkAt(t)}), 540, 1660 - Math.abs(Math.sin(tt * 8)) * 20 * Math.exp(-tt * 2), 1.45)) +
      popG(tt, 0.0, 500, 600, nameCard(80, 520, '4', 'DENNY', 'ABWEHR · NEUZUGANG')) +
      popG(tt, 0.3, 760, 450, `<g transform="rotate(12 760 450)">${badge(760, 450, 'NEU!', {kind: 'red', fs: 60})}</g>`) + confetti(t, t1 + 0.1, 30);
  },
  money4(t, d, m) {
    const lines = [['50 FOLLOWER × 1 €', '+50 €'], ['40 KOMMENTARE × 2 €', '+80 €'], ['VEREINSKASSE', '130 €', '#2FA84A', true]];
    const t3 = capT(2);
    let coins = '';
    for (let i = 0; i < 14; i++) { const t0 = t3 + rnd(i + 900) * 1.0, k = (t - t0) / 0.9; if (k > 0 && k < 1) coins += coin(80 + rnd(i + 950) * 860, -60 + k * 1500, 34, i % 2); }
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(coach({mouth: m, wave: t > t3 ? Math.sin(t * 10) : 0, blink: blinkAt(t)}), 540, 1660, 1.05)) +
      popG(t, 0.0, 540, 340, calcBoard(t, 70, 290, lines, [capT(0), capT(1), t3])) +
      (t >= t3 ? `<path d="M110 ${290 + 106 + 110 + 30} H890" stroke="#3A2316" stroke-width="7"/>` : '') + coins;
  },
  pump(t, d, m) {
    const k = easeOut(clamp(t / 0.5, 0, 1));
    const lines = [['SCHLAMMPUMPE', '-130 €', '#E5483A', true]];
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + place(coach({mouth: m, blink: blinkAt(t)}), 220, 1640, 0.9)) +
      mudPump(640, -200 + k * 1300, 1.3, t, false) + (t > 0.5 && t < 0.8 ? `<circle cx="640" cy="1150" r="${(t - 0.5) * 900}" fill="none" stroke="#fff" stroke-width="10" opacity="${1 - (t - 0.5) / 0.3}"/>` : '') +
      popG(t, capT(0), 540, 340, calcBoard(t, 70, 290, lines, [capT(1)])) +
      popG(t, capT(3), 540, 760, bigText(540, 840, '0 €', '#FF4A4A', 200));
  },
  pumpwork(t, d, m) {
    const k = clamp(t / d, 0, 1), lake = 1 - easeOut(clamp((t - 0.3) / (d * 0.7), 0, 1));
    const gx = 600, gy = 1040, dx = 160 * lake, bob = Math.sin(t * 3) * 8 * lake;
    let s = field(t, 1000, {goalX: gx, noPost: true, puddles: [[160, 1400, 120 * lake + 20, 20], [880, 1520, 140 * lake + 20, 24]]});
    if (lake > 0.05) s += `<ellipse cx="${gx}" cy="${gy + 60}" rx="${300 * lake}" ry="${70 * lake}" fill="#4A3828" stroke="#2C2018" stroke-width="8"/>`;
    s += goalPost(gx + dx, gy + 8 + bob, 0.9);
    s += `<path d="M${880} 1380 Q${760} ${1300} ${gx + 40} ${gy + 70}" stroke="#2A2A2E" stroke-width="22" fill="none"/>` + mudPump(880, 1420, 0.7, t, true);
    s += place(luca({blink: blinkAt(t)}), 330, 1560, 0.85);
    let drops = '';
    for (let i = 0; i < 6; i++) { const ph = (t * 1.4 + i / 6) % 1; drops += `<circle cx="${980 + ph * 60}" cy="${1300 - Math.sin(ph * Math.PI) * 120 + ph * 160}" r="${12 - ph * 6}" fill="#6B4A30"/>`; }
    return cam(1.0, 540, 960, s + drops) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'PLATZWART IM EINSATZ', {kind: 'pitch', fs: 50})) +
      (t >= capT(3) ? popG(t, capT(3), 540, 520, badge(540, 520, 'TOR ZURÜCK!', {kind: 'orange', fs: 60, rot: -3})) + confetti(t, capT(3), 30) : '');
  },
  tour(t, d, m) {
    const pan = easeOut(clamp(t / d, 0, 1)), wx = -pan * 1100;
    let world = `<g transform="translate(${wx} 0)"><rect x="-400" y="-400" width="3000" height="2800" fill="url(#skyG)"/>` + sky(t) + `<g transform="translate(1100 0)">${sky(t + 7)}</g>` + `<rect x="0" y="1080" width="2400" height="900" fill="#4A8038"/>` + treeline(1086) +
      `<g transform="translate(1080 0)">${treeline(1086)}</g>` +
      `<rect x="0" y="1180" width="2400" height="740" fill="#6B4A30"/>` + `<path d="M0 1180 H2400" stroke="#F0EDE0" stroke-width="10"/>` +
      flagPole(160, 1150, 0.9, t) + bauwagen(560, 1170, 1.0) + grill(1180, 1120, 1.0, t) + pappeTafel(1720, 1060, 1.0) +
      place(luca({blink: blinkAt(t)}), 1420, 1180, 0.5) + place(frog({blink: blinkAt(t, .4)}), 2000, 1180 - Math.abs(Math.sin(t * 7)) * 40, 0.3) + `</g>`;
    const lbl = (i, txt, x) => popG(t, capT(i), x, 520, badge(x, 520, txt, {kind: 'pitch', fs: 48, rot: -2}));
    return world + popG(t, 0.0, 540, 340, badge(540, 340, 'UNSER VEREINSGELÄNDE', {kind: 'orange', fs: 50})) +
      (t >= capT(1) && t < capT(3) ? lbl(1, 'BAUWAGEN = KABINE', 540) : '') +
      (t >= capT(3) && t < capT(4) ? lbl(3, 'WÜRSTCHENGRILL', 540) : '') +
      (t >= capT(4) ? lbl(4, 'ANZEIGETAFEL (PAPPE)', 540) : '');
  },
  train1(t, d, m) {
    const ph = (t * 0.9) % 1, side = Math.floor(t * 0.9) % 2 ? 1 : -1;
    const bx = 540 + side * 240 * ph, by = 1500 - ph * 420;
    const vx = 540 + side * 200 * clamp((ph - 0.35) / 0.4, 0, 1), dive = clamp((ph - 0.35) / 0.3, 0, 1) * 70 * side;
    let s = field(t, 1000, {goalX: 540}) + `<g transform="rotate(${dive} ${vx} 1200)">${place(vlad({blink: blinkAt(t)}), vx, 1250, 0.55)}</g>`;
    if (ph < 0.85) s += `<g transform="translate(${bx} ${by}) rotate(${t * 600})">${ballIcon(0, 0, 38)}</g>`;
    return cam(1.0, 540, 960, s) + popG(t, 0.0, 540, 360, badge(540, 360, 'TRAINING!', {kind: 'red', fs: 76, rot: -2})) +
      (ph > 0.6 ? popG(t, Math.floor(t * 0.9) / 0.9 + 0.67, 540, 560, badge(540, 560, 'GEHALTEN!', {kind: 'pitch', fs: 54, rot: 3})) : '');
  },
  train2(t, d, m) {
    const ph = clamp((t - 0.4) / 1.2, 0, 1), miss = t >= capT(2) - 0.6;
    const bx = 540 + ph * (miss ? 520 : 60), by = 1500 - ph * (miss ? 900 : 380);
    let s = field(t, 1000, {goalX: 540}) + place(vlad({blink: blinkAt(t)}), 540, 1060, 0.4) +
      place(lkz({blink: blinkAt(t)}), 380, 1650 - (t < 0.5 ? 0 : 0), 1.0);
    s += `<g transform="translate(${bx} ${by}) rotate(${t * 700})">${ballIcon(0, 0, 40)}</g>`;
    return cam(1.0, 540, 960, s) +
      popG(t, capT(1), 760, 520, badge(760, 520, 'TOR?', {kind: 'pitch', fs: 56})) +
      popG(t, capT(2), 540, 660, badge(540, 660, '… MANCHMAL', {kind: 'red', fs: 54, rot: -4}));
  },
  train3(t, d, m) {
    const k = (t * 0.7) % 1, x = -200 + k * 1500;
    let cones = '';
    [250, 450, 650, 850].forEach((cx, i) => { const hit = x > cx; cones += `<g transform="translate(${cx} 1480) rotate(${hit ? 80 : 0})"><path d="M-30 0 L0 -70 L30 0 Z" fill="#F28A2E" stroke="#111" stroke-width="5"/><path d="M-18 -26 h36" stroke="#fff" stroke-width="8"/></g>`; });
    let clods = '';
    for (let i = 0; i < 8; i++) { const ph = (t * 2 + i / 8) % 1; clods += `<circle cx="${x - 120 - ph * 200}" cy="${1480 - Math.sin(ph * Math.PI) * 150}" r="${10 + rnd(i) * 10}" fill="#6B4A30" stroke="#3A2316" stroke-width="3"/>`; }
    const s = field(t, 1000, {goalX: 860}) + cones + clods + `<g transform="rotate(-72 ${x} 1440)">${place(denny({blink: blinkAt(t)}), x, 1480, 0.55)}</g>`;
    return cam(1.0, 540, 960, s) + popG(t, 0.0, 540, 360, badge(540, 360, 'GRÄTSCHE!', {kind: 'orange', fs: 70, rot: -3}));
  },
  count2(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1680, 0.9)) +
      `<g opacity="${Math.sin(t * 14) > -0.4 ? 1 : 0.35}" transform="translate(540 520) scale(${1 + 0.07 * Math.abs(Math.sin(t * 7))}) translate(-540 -520)"><ellipse cx="540" cy="520" rx="${380 + 30 * Math.sin(t * 7)}" ry="110" fill="#FFD31A" opacity="${0.25 + 0.2 * Math.abs(Math.sin(t * 7))}"/>${bigText(540, 560, 'MORGEN!', '#FFE45A', 140)}</g>` +
      popG(t, capT(2), 540, 820, `<g transform="translate(330 830) scale(0.42) translate(-300 -300)">${LOGO}</g>` + bigText(540, 860, 'VS', '#FFD31A', 100) + heuLogo(750, 830, 0.6));
  },
  heroes(t, d, m) {
    const list = [[FAN_PICS[0], '@eikemzz'], [FAN_PICS[1], '@tobiii1911'], [FAN_PICS[2], '@leo.hro1'], [LKZ_PIC, 'Leberkaaszerfetzer'], [LUCA_PIC, 'luca'], [DENNY_PIC, 'Denny']];
    const times = [capT(3), capT(3) + 0.35, capT(3) + 0.7, capT(4), capT(5), capT(5) + 0.4];
    let g = '';
    list.forEach(([pic, name], i) => { const x = 230 + (i % 3) * 300, y = 640 + Math.floor(i / 3) * 330;
      const id = 'hp' + i;
      g += popG(t, times[i], x, y, `<defs><clipPath id="${id}"><circle cx="${x}" cy="${y}" r="100"/></clipPath></defs>
        <circle cx="${x + 5}" cy="${y + 9}" r="112" fill="#3A2316"/><circle cx="${x}" cy="${y}" r="110" fill="url(#pwGold2)" stroke="#3A2316" stroke-width="6"/>
        <image href="${pic}" x="${x - 100}" y="${y - 100}" width="200" height="200" clip-path="url(#${id})"/>
        <text x="${x + 78}" y="${y - 70}" text-anchor="middle" font-family="Noto Color Emoji" font-size="54">⭐</text>` + handleTag(x, y + 150, name, name.length > 12 ? 0.6 : 0.8)); });
    const defs = `<defs><linearGradient id="pwGold2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF3A8"/><stop offset=".5" stop-color="#FFD31A"/><stop offset="1" stop-color="#C98A12"/></linearGradient></defs>`;
    return defs + cam(1.0, 540, 960, field(t, 1080, {goal: false})) + `<rect width="1080" height="1920" fill="#000" opacity=".35"/>` +
      `<g opacity=".25">${Array.from({length: 12}, (_, i) => { const a = i * 30 + t * 15; return `<path d="M540 800 L${540 + Math.cos(a * Math.PI / 180) * 1400} ${800 + Math.sin(a * Math.PI / 180) * 1400} L${540 + Math.cos((a + 12) * Math.PI / 180) * 1400} ${800 + Math.sin((a + 12) * Math.PI / 180) * 1400}Z" fill="#FFD31A"/>`; }).join('')}</g>` +
      popG(t, 0.0, 540, 360, badge(540, 360, 'UNSERE HELDEN', {kind: 'orange', fs: 64, rot: -2})) + g + confetti(t, capT(3), 40);
  },
  cotrainer(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    const board = `<g transform="translate(540 820) rotate(${Math.sin(t * 2) * 4})">
      <rect x="-150" y="-200" width="300" height="400" rx="20" fill="#A8743F" stroke="#3A2316" stroke-width="10"/>
      <rect x="-120" y="-160" width="240" height="330" fill="#fff"/>
      <rect x="-60" y="-220" width="120" height="50" rx="10" fill="#9AA0A8" stroke="#3A2316" stroke-width="7"/>
      <g stroke="#2F7FD8" stroke-width="7" fill="none"><circle cx="-50" cy="-80" r="18"/><circle cx="40" cy="-30" r="18"/><circle cx="-30" cy="40" r="18"/></g>
      <g stroke="#E5483A" stroke-width="8"><path d="M30 -100 l24 24 M54 -100 l-24 24 M60 60 l24 24 M84 60 l-24 24"/></g>
      <path d="M-50 -60 Q0 -40 30 -36 M40 -12 Q20 20 -20 34" stroke="#3A2316" stroke-width="5" fill="none" stroke-dasharray="10 8"/>
      <g transform="translate(150 140) rotate(-20)"><rect x="-50" y="-22" width="90" height="44" rx="20" fill="#C0C6CC" stroke="#3A2316" stroke-width="6"/><circle cx="40" cy="0" r="26" fill="#C0C6CC" stroke="#3A2316" stroke-width="6"/><path d="M-50 0 Q-110 40 -150 -10" stroke="#E5483A" stroke-width="7" fill="none"/></g></g>`;
    return cam(1.0, 540, 960, field(t, 1080, {goal: false})) + `<rect width="1080" height="1920" fill="#000" opacity=".3"/>` +
      popG(t, 0.0, 540, 380, badge(540, 380, 'GESUCHT: CO-TRAINER', {kind: 'pitch', fs: 56})) + popG(t, 0.2, 540, 820, board) +
      bewerbungen(t, c[3], 1180) +
      (t >= c[3] + 0.4 ? `<g opacity="${Math.sin(t * 16) > -0.3 ? 1 : 0.25}">${badge(540, 1290, 'TOP-KOMMENTAR GEWINNT!', {kind: 'orange', fs: 44, rot: -2})}</g>` : '');
  },
  allin(t, d, m) {
    const z = 1.6, cx = 540, cy = 600;
    return cam(z, cx, cy, wholePitch(t) + bigStand(t, 1, 1)) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1700, 1.0) +
      popG(t, capT(1), 540, 420, bigText(540, 470, 'ALLES GEBEN!', '#FFD31A', 120)) +
      popG(t, capT(3), 540, 620, badge(540, 620, 'WIR BRAUCHEN JEDEN FAN!', {kind: 'red', fs: 50, rot: -2})) + confetti(t, capT(1), 50);
  },
  goal5k(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    const grow = easeOut(clamp((t - c[2]) / 1.2, 0, 1));
    let s = field(t, 1000, {goalX: 540});
    let rasen = '';
    if (t >= c[2]) {
      const w = 1080 * grow;
      rasen = `<defs><clipPath id="rz"><rect x="0" y="1000" width="${w}" height="920"/></clipPath></defs><g clip-path="url(#rz)"><rect x="0" y="1000" width="1080" height="920" fill="#3FA34D"/>
        ${Array.from({length: 9}, (_, i) => `<rect x="${i * 120}" y="1000" width="60" height="920" fill="#4DB85C"/>`).join('')}
        <g fill="none" stroke="#fff" stroke-width="8" opacity=".9"><path d="M-400 1040 H1480"/><path d="M340 1040 L320 1170 L760 1170 L740 1040"/></g>
        ${goalPost(540, 1040, 0.9)}</g>
        <g transform="translate(${w} 1300)"><ellipse cx="0" cy="0" rx="40" ry="300" fill="#2E7D32" stroke="#1B4D1F" stroke-width="8"/></g>`;
    }
    const prog = 0;
    const bar = `<g>${box(90, 1150, 900, 120, 'white', 9)}<rect x="120" y="1180" width="840" height="60" rx="30" fill="#E2DACA" stroke="#3A2316" stroke-width="5"/>
      <rect x="120" y="1180" width="${Math.max(30, 840 * prog)}" height="60" rx="30" fill="#58B044"/>
      ${label(540, 1228, '0 € / 5000 €', 46, '#3A2316')}</g>`;
    return cam(1.0, 540, 960, s + rasen) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'UNSER ZIEL:', {kind: 'orange', fs: 54})) +
      popG(t, c[2], 540, 500, bigText(540, 540, 'STADIONRASEN', '#6BF06B', 110)) +
      popG(t, c[3], 540, 1210, bar) +
      popG(t, c[4], 300, 700, badge(300, 700, '5000 FANS', {kind: 'pitch', fs: 48, rot: -3})) +
      popG(t, c[5], 540, 790, bigText(540, 800, 'ODER', '#fff', 60)) +
      popG(t, c[5], 760, 700, badge(760, 700, '2500 KOMMENTARE', {kind: 'red', fs: 38, rot: 3}));
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
  end4(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1700, 1.15)) +
      `<g transform="translate(510 500) scale(${1 + 0.025 * Math.sin(t * 6)}) translate(-510 -500)">${popG(t, 0.0, 510, 500, commentCard(70, 300, t, 'ICH WERDE ...'))}</g>` +
      popG(t, capT(1), 540, 830, badge(540, 830, 'WER WIRD CO-TRAINER?', {bg: '#FFD31A', fs: 48, rot: -2}));
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
  LT = lt; LD = d;
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
