// Zeitachse und Szenen-Komposition. DATA = {fps, segs:[{id,start,dur,end,caps:[{text,t0,t1}]}], env:[...], total}
function cam(z, cx, cy, inner) {
  return `<g transform="translate(540 960) scale(${z}) translate(${-cx} ${-cy})">${inner}</g>`;
}
function blinkAt(t, off = 0) { return ((t + off) % 3.3) < 0.12; }

function teamLine(t, base, s, m) {
  return place(vlad({blink: blinkAt(t, .4)}), 170, base, s) +
         place(opa({blink: blinkAt(t, 1.1)}), 360, base, s) +
         place(busguy({blink: blinkAt(t, 2)}), 730, base, s) +
         place(coach({mouth: m, blink: blinkAt(t)}), 545, base + 10, s * 1.08) +
         place(corgi({wag: Math.sin(t * 14), blink: blinkAt(t, 1.7)}), 930, base, s * 0.8);
}

const SCENES = {
  intro(t, d, m) {
    const z = 1 + 0.35 * easeOut(t / d);
    return cam(z, 540, 1180, field(t) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1290, 0.6)) +
      popG(t, 0.05, 540, 330, badge(540, 330, 'TAG 1', {bg: '#3FBF4F', fg: '#fff', fs: 130, r: 26, rot: -3})) +
      popG(t, 0.7, 540, 490, badge(540, 490, 'VEREIN GEGRÜNDET', {bg: '#FFD31A', fs: 46}));
  },
  follow(t, d, m) {
    const z = 1.05 + 0.08 * (t / d);
    return cam(z, 540, 1100, field(t, 1060, {goalX: 860}) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1480, 1.3)) +
      popG(t, 0.6, 540, 300, badge(540, 300, '1 FOLLOW = 1 KLAPPSTUHL', {bg: '#3FBF4F', fg: '#fff', fs: 54}));
  },
  chairs(t, d, m) {
    const z = 1.15 - 0.1 * easeOut(t / d);
    let c = '';
    [[300, 0.15], [540, 0.45], [780, 0.75]].forEach(([x, t0], i) => {
      const s = pop(t, t0);
      if (s > 0) c += place(chair({mud: i === 1}), x, 1360, 1.0 * s);
    });
    return cam(z, 540, 1100, field(t, 1040, {goal: false}) + c) +
      popG(t, 0.0, 540, 560, badge(540, 560, 'TRIBÜNE', {fs: 80})) +
      popG(t, 0.9, 540, 700, badge(540, 700, '3 KLAPPSTÜHLE', {bg: '#FFD31A', fs: 50, rot: 2}));
  },
  welcome(t, d, m) {
    const ls = backOut(t / 0.35);
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1560, 1.05)) +
      popG(t, 0.0, 540, 170, badge(540, 170, 'WILLKOMMEN', {bg: '#3FBF4F', fg: '#fff', fs: 60})) +
      `<g transform="translate(540 580) scale(${0.95 * ls}) rotate(${Math.sin(t * 3) * 3}) translate(-300 -300)">${LOGO}</g>`;
  },
  field(t, d, m) {
    const px = 380 + 320 * (t / d);
    const pud = [[160, 1240, 220, 40], [700, 1180, 260, 36], [460, 1420, 320, 60], [960, 1460, 220, 46], [120, 1640, 260, 50], [760, 1760, 300, 60], [380, 1900, 280, 50]];
    let splat = '';
    for (let i = 0; i < 10; i++) splat += `<ellipse cx="${rnd(i + 70) * 1100}" cy="${1150 + rnd(i + 80) * 800}" rx="${20 + rnd(i) * 20}" ry="8" fill="#4A3828"/>`;
    return cam(1.15, px, 1150, field(t, 900, {puddles: pud, goalX: 640}) + splat +
        `<g transform="translate(${600} ${1520}) rotate(${t * 40})"><circle r="40" fill="#fff" stroke="#111" stroke-width="8"/><path d="M0 -16 L15 -5 L9 13 L-9 13 L-15 -5Z" fill="#111"/><path d="M-40 4 Q-10 40 36 14 Q40 2 40 0 Q0 30 -40 4Z" fill="#6B4226"/></g>`) +
      popG(t, 0.1, 540, 300, badge(540, 300, 'UNSER PLATZ', {fs: 70})) +
      popG(t, 1.2, 540, 430, badge(540, 430, 'WASSERSTAND: HOCH', {bg: '#E8432E', fg: '#fff', fs: 44, rot: -2}));
  },
  light(t, d, m) {
    const z = 1.0 + 0.06 * (t / d);
    return cam(z, 540, 960, field(t, 1080, {goalX: 780}) + flashMast(250, 1350, 360, t, true)) +
      popG(t, 0.5, 720, 560, badge(720, 560, '1 TASCHENLAMPE', {bg: '#FFD31A', fs: 52, rot: -3})) +
      popG(t, 1.4, 720, 690, badge(720, 690, 'AKKU: 3 %', {bg: '#E8432E', fg: '#fff', fs: 42, rot: 2}));
  },
  league(t, d, m) {
    return cam(1.0 + 0.05 * t / d, 540, 960, field(t, 1080) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1660, 1.4)) +
      popG(t, 0.1, 540, 250, badge(540, 250, 'KREISLIGA', {fs: 84})) +
      popG(t, 0.8, 540, 390, badge(540, 390, 'GANZ UNTEN', {bg: '#E8432E', fg: '#fff', fs: 40}));
  },
  vlad(t, d, m) {
    const b = Math.sin(t * 4) * 6;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 540}) + place(vlad({blink: blinkAt(t, .5)}), 540, 1660 + b, 1.55)) +
      popG(t, 0.1, 540, 310, nameCard(124, 200, '1', 'VLAD', 'TOR · AUGENKLAPPE', '#3FBF4F'));
  },
  opa(t, d, m) {
    const b = Math.sin(t * 2) * 4;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(opa({blink: blinkAt(t, .9)}), 540, 1660 + b, 1.55)) +
      popG(t, 0.1, 540, 310, nameCard(124, 200, '4', 'OPA JÜRGEN', 'ABWEHR · 79 JAHRE'));
  },
  bus(t, d, m) {
    const ff = SEG.caps[SEG.caps.length - 1].t0 - SEG.start;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + busStop(900, 1560, 1.1) + place(busguy({blink: blinkAt(t, .2)}), 450, 1660, 1.45)) +
      popG(t, 0.1, 540, 310, nameCard(124, 200, '9', '???', 'STURM · BUS VERPASST')) +
      popG(t, ff, 300, 1610, badge(300, 1610, 'FLIP-FLOPS', {bg: '#FF3FA4', fg: '#fff', fs: 46, rot: -6}));
  },
  pichu(t, d, m) {
    const hop = Math.abs(Math.sin(t * 6)) * 24;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 820}) + place(corgi({wag: Math.sin(t * 16), blink: blinkAt(t, .3)}), 600, 1640 - hop, 1.7)) +
      popG(t, 0.1, 540, 310, nameCard(124, 200, '★', 'PICHU', 'MASKOTTCHEN · CORGI', '#FFD31A')) +
      popG(t, 1.0, 540, 500, badge(540, 500, 'SPRICH: PITSCHU', {bg: '#2F7FD8', fg: '#fff', fs: 40, rot: 2}));
  },
  goal(t, d, m) {
    let beams = '';
    for (let i = 0; i < 5; i++) {
      const a = -40 + i * 20 + Math.sin(t * 1.5 + i) * 6;
      beams += `<path d="M540 1100 L${540 + Math.tan(a * Math.PI / 180) * 1100 - 90} 0 L${540 + Math.tan(a * Math.PI / 180) * 1100 + 90} 0 Z" fill="#FFF3B0" opacity=".12"/>`;
    }
    let stars = '';
    for (let i = 0; i < 7; i++) {
      const a = (i / 7) * Math.PI * 2 + t * 0.8;
      stars += `<text x="${540 + Math.cos(a) * 270}" y="${640 + Math.sin(a) * 120}" text-anchor="middle" ${FONT} font-size="54" fill="#FFD31A" stroke="#111" stroke-width="5" paint-order="stroke">★</text>`;
    }
    return cam(1.0, 540, 960, field(t, 1080, {goal: false}) + beams + teamLine(t, 1500, 0.56, m)) +
      popG(t, 0.0, 540, 210, bigText(540, 230, 'UNSER ZIEL:', '#fff', 64)) +
      popG(t, 0.6, 540, 640, trophy(540, 640, 1.25 + 0.03 * Math.sin(t * 5)) + stars) +
      popG(t, 1.0, 540, 360, bigText(540, 370, 'DEUTSCHER MEISTER', '#FFD31A', 84));
  },
  sunday(t, d, m) {
    return cam(1.0 + 0.06 * t / d, 540, 1200, field(t, 1080, {goalX: 860}) + teamLine(t, 1560, 0.68, m)) +
      popG(t, 0.0, 540, 260, bigText(540, 280, 'SONNTAG:', '#fff', 80)) +
      popG(t, 0.6, 540, 460, bigText(540, 500, '1. SPIEL', '#FFD31A', 190));
  },
  fans(t, d, m) {
    let c = '';
    [300, 540, 780].forEach(x => c += place(chair({}), x, 1240, 0.62));
    const z = 1.0 + 0.1 * easeOut(t / d);
    return cam(z, 540, 1150, field(t, 1040, {goal: false}) + c + place(coach({mouth: m * 0.6, mood: 'sad', blink: blinkAt(t)}), 860, 1560, 0.85)) +
      popG(t, 0.1, 540, 250, badge(540, 250, 'FANS', {fs: 60})) +
      popG(t, 0.9, 540, 470, bigText(540, 540, '0', '#FF4A4A', 260)) +
      popG(t, 2.0, 300, 1020, badge(300, 1020, 'LEER', {bg: '#E8432E', fg: '#fff', fs: 50, rot: -5}));
  },
  seat(t, d, m) {
    const fol = t > 1.0;
    let c = '';
    [300, 540, 780].forEach((x, i) => c += place(chair({num: i === 0 ? '1' : ''}), x, 1340, 0.9));
    const gs = pop(t, 1.3);
    if (gs > 0) c += place(ghost(), 300, 1160, 0.9 * gs);
    const tap = t > 0.6 && t < 1.1 ? `<circle cx="${110 + 260}" cy="${190 + 280}" r="${30 + (t - 0.6) * 90}" fill="#fff" opacity="${0.5 - (t - 0.6)}"/>` : '';
    return cam(1.0, 540, 960, field(t, 1080, {goal: false}) + c) +
      popG(t, 0.0, 540, 360, profileCard(110, 190, fol ? 1 : 0, fol)) + tap +
      popG(t, 1.6, 540, 700, badge(540, 700, 'KLAPPSTUHL NR. 001', {bg: '#3FBF4F', fg: '#fff', fs: 52, rot: -2}));
  },
  money(t, d, m) {
    const kg = SEG.caps[SEG.caps.length - 1].t0 - SEG.start;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + crate(690, 1330, 0.95) + cashBox(690, 1240, 1.0, t > 0.4) +
        place(coach({mouth: m, blink: blinkAt(t)}), 250, 1560, 0.95)) +
      popG(t, 0.0, 540, 230, badge(540, 230, 'VEREINSKASSE', {fs: 60})) +
      popG(t, 0.9, 540, 420, bigText(540, 470, '500 €', '#6BF06B', 190)) +
      popG(t, kg, 540, 620, badge(540, 620, '+ 1 KAUGUMMI', {bg: '#FF7EB6', fs: 54, rot: 3}));
  },
  options(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1680, 1.15)) +
      popG(t, c[0], 200, 560, optionCard(200, 560, ICON_BOOT, 'STÜRMER', 'KAUFEN?', -6)) +
      popG(t, c[1], 540, 540, optionCard(540, 540, ICON_HOUSE, 'VEREINSHAUS', 'MIETEN?', 0)) +
      popG(t, c[2], 880, 560, optionCard(880, 560, ICON_Q, 'WAS GANZ', 'ANDERES?', 6));
  },
  comment(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1680, 1.25)) +
      popG(t, 0.0, 540, 400, commentCard(90, 280)) +
      popG(t, 0.6, 540, 660, badge(540, 660, 'DU ENTSCHEIDEST!', {bg: '#FFD31A', fs: 52, rot: -2}));
  },
};

let SEG = null;
function render(f) {
  UID = 0;
  const t = f / DATA.fps;
  let si = DATA.segs.findIndex(s => t < s.end);
  if (si < 0) si = DATA.segs.length - 1;
  SEG = DATA.segs[si];
  const lt = t - SEG.start, d = SEG.end - SEG.start;
  const m = DATA.env[Math.min(f, DATA.env.length - 1)] || 0;
  let body = SCENES[SEG.id](lt, d, m);
  const heavy = SEG.id === 'fans' ? 230 : 150;
  body += rain(t, heavy, 0.45);
  const cap = SEG.caps.find(c => t >= c.t0 && t < c.t1) || (t >= SEG.caps[SEG.caps.length - 1].t0 ? SEG.caps[SEG.caps.length - 1] : null);
  if (cap) body += caption(cap.text, cap.t0, t);
  // leichter Blitz-Schnitt
  if (lt < 0.06 && si > 0) body += `<rect width="1080" height="1920" fill="#fff" opacity="${0.25 * (1 - lt / 0.06)}"/>`;
  document.getElementById('root').innerHTML = `<defs><linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2438"/><stop offset="1" stop-color="#46506A"/></linearGradient>
    <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient></defs>
    ${body}<rect width="1080" height="1920" fill="url(#vig)"/>`;
}
