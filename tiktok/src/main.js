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
      popG(t, 0.05, 540, 330, badge(540, 330, 'TAG 1', {kind: 'pitch', fs: 150, pad: 120})) +
      popG(t, 0.7, 540, 490, badge(540, 490, 'VEREIN GEGRÜNDET', {bg: '#FFD31A', fs: 52, ball: true}));
  },
  follow(t, d, m) {
    const z = 1.05 + 0.08 * (t / d);
    return cam(z, 540, 1100, field(t, 1060, {goalX: 860}) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1480, 1.3)) +
      popG(t, 0.6, 520, 320, badge(520, 320, '1 FOLLOW = 1 TRIBÜNENPLATZ', {bg: '#2F7FD8', fg: '#fff', fs: 42}));
  },
  chairs(t, d, m) {
    const z = 1.15 - 0.1 * easeOut(t / d);
    let c = '';
    [[300, 0.15], [540, 0.45], [780, 0.75]].forEach(([x, t0], i) => {
      const s = pop(t, t0);
      if (s > 0) c += place(chair({mud: i === 1}), x, 1215, 1.0 * s);
    });
    return cam(z, 540, 1100, field(t, 1040, {goal: false, touchY: 1250}) + c) +
      popG(t, 0.0, 540, 400, badge(540, 400, 'TRIBÜNE', {fs: 80})) +
      popG(t, 0.9, 540, 540, badge(540, 540, '3 KLAPPSTÜHLE', {bg: '#FFD31A', fs: 50, rot: 2}));
  },
  welcome(t, d, m) {
    const ls = backOut(t / 0.35);
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1560, 1.05)) +
      popG(t, 0.0, 520, 280, badge(520, 280, 'WILLKOMMEN', {bg: '#2F7FD8', fg: '#fff', fs: 60})) +
      `<g transform="translate(520 660) scale(${0.85 * ls}) rotate(${Math.sin(t * 3) * 3}) translate(-300 -300)">${LOGO}</g>`;
  },
  field(t, d, m) {
    const px = 380 + 320 * (t / d);
    const pud = [[160, 1240, 220, 40], [700, 1180, 260, 36], [460, 1420, 320, 60], [960, 1460, 220, 46], [120, 1640, 260, 50], [760, 1760, 300, 60], [380, 1900, 280, 50]];
    let splat = '';
    for (let i = 0; i < 10; i++) splat += `<ellipse cx="${rnd(i + 70) * 1100}" cy="${1150 + rnd(i + 80) * 800}" rx="${20 + rnd(i) * 20}" ry="8" fill="#4A3828"/>`;
    return cam(1.15, px, 1150, field(t, 900, {puddles: pud, goalX: 640}) + splat +
        `<g transform="translate(600 1520) rotate(${t * 40})">${ballIcon(0, 0, 44)}<path d="M-30 18 q16 10 34 4 q-6 14 -24 10z M10 -30 q10 -4 14 4 q-4 6 -12 2z" fill="#6B4226"/></g>`) +
      popG(t, 0.1, 540, 300, badge(540, 300, 'UNSER PLATZ', {fs: 70}));;
  },
  light(t, d, m) {
    const z = 1.0 + 0.06 * (t / d);
    return cam(z, 540, 960, field(t, 1080, {goal: false, touchY: 1260}) + flashMast(230, 1225, 330, t, true)) +
      popG(t, 0.5, 640, 560, badge(640, 560, '1 TASCHENLAMPE', {bg: '#FFD31A', fs: 52, rot: -3})) +
      popG(t, 1.4, 640, 690, badge(640, 690, 'AKKU: 3 %', {bg: '#E8432E', fg: '#fff', fs: 42, rot: 2}));
  },
  league(t, d, m) {
    return cam(1.0 + 0.05 * t / d, 540, 960, field(t, 1080) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1660, 1.4)) +
      popG(t, 0.1, 520, 300, badge(520, 300, 'KREISLIGA', {fs: 84})) +
      popG(t, 0.8, 520, 440, badge(520, 440, 'GANZ UNTEN', {bg: '#E8432E', fg: '#fff', fs: 40}));
  },
  vlad(t, d, m) {
    const b = Math.sin(t * 4) * 6;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 540}) + place(vlad({blink: blinkAt(t, .5)}), 540, 1660 + b, 1.55)) +
      popG(t, 0.1, 500, 320, nameCard(80, 240, '1', 'VLAD', 'TOR · AUGENKLAPPE', '#2F7FD8'));
  },
  opa(t, d, m) {
    const b = Math.sin(t * 2) * 4;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(opa({blink: blinkAt(t, .9)}), 540, 1660 + b, 1.55)) +
      popG(t, 0.1, 500, 320, nameCard(80, 240, '4', 'OPA JÜRGEN', 'ABWEHR · 79 JAHRE'));
  },
  bus(t, d, m) {
    const ff = SEG.caps[SEG.caps.length - 1].t0 - SEG.start;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + busStop(900, 1560, 1.1) + place(busguy({blink: blinkAt(t, .2)}), 450, 1660, 1.45)) +
      popG(t, 0.1, 500, 320, nameCard(80, 240, '9', '???', 'STURM · BUS VERPASST')) +
      popG(t, ff, 300, 1450, badge(300, 1450, 'FLIP-FLOPS', {bg: '#FF3FA4', fg: '#fff', fs: 46, rot: -6}));
  },
  pichu(t, d, m) {
    const hop = Math.abs(Math.sin(t * 6)) * 16;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 820}) + place(corgi({wag: Math.sin(t * 16), blink: blinkAt(t, .3)}), 560, 1250 - hop, 1.35)) +
      popG(t, 0.1, 500, 320, nameCard(80, 240, '★', 'PICHU', 'MASKOTTCHEN · CORGI', '#FFD31A'));
  },
  goal(t, d, m) {
    let beams = '';
    for (let i = 0; i < 5; i++) {
      const a = -40 + i * 20 + Math.sin(t * 1.5 + i) * 6;
      beams += `<path d="M520 900 L${520 + Math.tan(a * Math.PI / 180) * 900 - 90} 0 L${520 + Math.tan(a * Math.PI / 180) * 900 + 90} 0 Z" fill="#FFF3B0" opacity=".12"/>`;
    }
    let stars = '';
    for (let i = 0; i < 7; i++) {
      const a = (i / 7) * Math.PI * 2 + t * 0.8;
      stars += `<text x="${520 + Math.cos(a) * 180}" y="${540 + Math.sin(a) * 70}" text-anchor="middle" ${FONT} font-size="48" fill="#FFD31A" stroke="#14213D" stroke-width="5" paint-order="stroke">★</text>`;
    }
    return cam(1.0, 540, 960, field(t, 880, {goal: false}) + beams + fullTeam(t, 960, 1090, 0.44, m, false)) +
      popG(t, 0.0, 520, 250, bigText(520, 270, 'UNSER ZIEL:', '#fff', 58)) +
      popG(t, 0.6, 520, 520, trophy(520, 530, 0.72 + 0.02 * Math.sin(t * 5)) + stars) +
      popG(t, 1.0, 520, 350, bigText(520, 360, 'DEUTSCHER MEISTER', '#FFD31A', 78));
  },
  sunday(t, d, m) {
    return cam(1.0, 540, 960, field(t, 880, {goalX: 860}) + fullTeam(t, 960, 1090, 0.44, m, false)) +
      popG(t, 0.0, 520, 300, bigText(520, 320, 'SONNTAG:', '#fff', 80)) +
      popG(t, 0.6, 520, 500, bigText(520, 540, '1. SPIEL', '#FFD31A', 180));
  },
  fans(t, d, m) {
    let c = '';
    [300, 540, 780].forEach(x => c += place(chair({}), x, 1240, 0.62));
    const z = 1.0 + 0.1 * easeOut(t / d);
    return cam(z, 540, 1150, field(t, 1040, {goal: false, touchY: 1265}) + c + place(coach({mouth: m * 0.6, mood: 'sad', blink: blinkAt(t)}), 860, 1560, 0.85)) +
      popG(t, 0.1, 520, 300, badge(520, 300, 'FANS', {fs: 60})) +
      popG(t, 0.9, 520, 500, bigText(520, 570, '0', '#FF4A4A', 260)) +
      popG(t, 2.0, 300, 1020, badge(300, 1020, 'LEER', {bg: '#E8432E', fg: '#fff', fs: 50, rot: -5}));
  },
  seat(t, d, m) {
    const fol = t > 1.0;
    let c = '';
    [300, 540, 780].forEach((x, i) => c += place(chair({num: String(i + 1)}), x, 1250, 0.9));
    [300, 540, 780].forEach((x, i) => { const gs = pop(t, 1.3 + i * 0.25); if (gs > 0) c += place(ghost(), x, 1070, 0.9 * gs); });
    const tap = t > 0.6 && t < 1.1 ? `<circle cx="${90 + 260}" cy="${240 + 280}" r="${30 + (t - 0.6) * 90}" fill="#fff" opacity="${0.5 - (t - 0.6)}"/>` : '';
    return cam(1.0, 540, 960, field(t, 1080, {goal: false, touchY: 1280}) + c) +
      popG(t, 0.0, 540, 360, profileCard(90, 240, fol ? 1 : 0, fol)) + tap +
      popG(t, 2.1, 520, 630, badge(520, 630, 'KLAPPSTUHL NR. 001', {bg: '#2F7FD8', fg: '#fff', fs: 52, rot: -2}));
  },
  money(t, d, m) {
    const kg = SEG.caps[SEG.caps.length - 1].t0 - SEG.start;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + crate(690, 1180, 0.95) + cashBox(690, 1015, 0.8, t > 0.4) +
        place(coach({mouth: m, blink: blinkAt(t)}), 250, 1560, 0.95)) +
      popG(t, 0.0, 520, 300, badge(520, 300, 'VEREINSKASSE', {fs: 60})) +
      popG(t, 0.9, 520, 450, bigText(520, 500, '500 €', '#6BF06B', 170)) +
      popG(t, kg, 520, 620, badge(520, 620, '+ 1 KAUGUMMI', {bg: '#FF7EB6', fs: 54, rot: 3}));
  },
  rule(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    let coins = '';
    for (let i = 0; i < 14; i++) {
      const t0 = c[0] + 0.15 + i * 0.36, k = (t - t0) / 0.6;
      const two = t0 >= c[3];
      if (k > 0 && k < 1) coins += coin(470 + rnd(i + 700) * 140, 520 + k * 380, two ? 36 : 30, two);
    }
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + crate(540, 1180, 0.95) + cashBox(540, 1015, 0.8, true) + coins +
        place(coach({mouth: m, blink: blinkAt(t)}), 170, 1600, 0.85)) +
      popG(t, c[0], 520, 300, badge(520, 300, '+1 € PRO FOLLOWER', {kind: 'pitch', fs: 52})) +
      popG(t, c[3], 520, 440, badge(520, 440, '+2 € PRO KOMMENTAR', {kind: 'orange', fs: 52, rot: -2}));
  },
  options(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1680, 1.15)) +
      popG(t, 0.0, 520, 300, badge(520, 300, 'WAS TUN MIT DEM GELD?', {fs: 52})) +
      popG(t, c[2], 190, 640, optionCard(190, 640, ICON_BOOT, 'STÜRMER', 'KAUFEN?', -6)) +
      popG(t, c[3], 480, 620, optionCard(480, 620, ICON_HOUSE, 'VEREINSHAUS', 'MIETEN?', 0)) +
      popG(t, c[4], 770, 640, optionCard(770, 640, ICON_Q, 'WAS GANZ', 'ANDERES?', 6));
  },
  comment(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1680, 1.25)) +
      popG(t, 0.0, 510, 420, commentCard(70, 300)) +
      popG(t, 0.6, 520, 700, badge(520, 700, 'DU ENTSCHEIDEST!', {bg: '#FFD31A', fs: 52, rot: -2}));
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
  let body = SCENES[SEG.id](lt, d, m);
  const heavy = SEG.id === 'fans' ? 230 : 150;
  body += rain(t, heavy, 0.45);
  const cap = SEG.caps.find(c => t >= c.t0 && t < c.t1) || (t >= SEG.caps[SEG.caps.length - 1].t0 ? SEG.caps[SEG.caps.length - 1] : null);
  if (cap) body += caption(cap.text, cap.t0, t);
  // leichter Blitz-Schnitt
  if (si > 0) body += mudWipe(lt);
  document.getElementById('root').innerHTML = `<defs><linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2438"/><stop offset="1" stop-color="#46506A"/></linearGradient>
    <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient></defs>
    ${body}<rect width="1080" height="1920" fill="url(#vig)"/>`;
}
