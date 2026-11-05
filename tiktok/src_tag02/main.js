// Tag 2 – Zeitachse und Szenen. DATA = {fps, segs:[{id,start,end,caps}], env, total}
function cam(z, cx, cy, inner) {
  return `<g transform="translate(540 960) scale(${z}) translate(${-cx} ${-cy})">${inner}</g>`;
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

const SCENES = {
  intro(t, d, m) {
    const k = clamp(t / d, 0, 1), e = k * k * (3 - 2 * k), z = 0.7 + 0.3 * e;
    return cam(z, 540, 1060 - 30 * e, field(t, 1060, {goalX: 790}) + [130, 215, 300].map((x, i) => place(seatedFan(i, t), x, 1092, 0.17)).join('') + place(coach({mouth: m, blink: blinkAt(t)}), 470, 1290, 0.6)) +
      `<g transform="rotate(${t > 0.3 ? Math.sin((t - 0.3) * 40) * 6 * Math.exp(-(t - 0.3) * 7) : 0} 540 440)">${badge(540, 440, 'TAG 2', {kind: 'pitch', fs: 150, pad: 120})}</g>` +
      popG(t, 0.55, 540, 640, twoLineBadge(540, 640, 'ICH GRÜNDE EINEN', 'FUSSBALLVEREIN', 52)) +
      introBall(t);
  },
  first3(t, d, m) {
    const z = 1.0 + 0.06 * t / d;
    let s = field(t, 960, {goal: false, touchY: 1265});
    [220, 540, 860].forEach((x, i) => { s += place(seatedFan(i, t), x, 1210, 0.82); });
    let tags = '';
    FIRST_FANS.forEach((f, i) => { const x = [220, 540, 860][i]; tags += popG(t, capT(i + 1), x, 500, profilePic(x, 440, i, 100) + handleTag(x, 600, f.handle, i === 1 ? 0.95 : 1.05)); });
    return cam(z, 540, 1000, s) + tags;
  },
  fans83(t, d, m) {
    const n = Math.round(83 * easeOut(clamp((t - 0.3) / 1.4, 0, 1)));
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 820}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 460, 1640, 1.2) + place(frog({blink: blinkAt(t, .4), mouth: t > 0.6 && t < 1.1}), 860, 1660 - Math.abs(Math.sin(t * 7)) * 70, 0.5)) +
      popG(t, 0.0, 540, 400, badge(540, 400, 'FANS', {kind: 'pitch', fs: 64})) +
      popG(t, 0.2, 540, 600, bigText(540, 660, String(n), '#6BF06B', 230));
  },
  problem(t, d, m) {
    let s = field(t, 960, {goal: false, touchY: 1150});
    [380, 540, 700].forEach((x, i) => { s += place(seatedFan(i, t), x, 1120, 0.42); });
    s += crowd(t, 70, 1330, 9, 4, 118, 105, 0.7, true);
    const bub = [[200, 1180, 'NASS!', -6, 0.5], [560, 1140, 'WILL SITZEN!', 4, 0.9], [880, 1200, 'MIR IST KALT!', -3, 1.3], [420, 1290, 'BUUUH!', 5, 1.7]];
    let bubbles = ''; bub.forEach(([x, y, txt, r, t0]) => { bubbles += popG(t, t0, x, y, speech(x, y, txt, r)); });
    return cam(1.0, 540, 960, s + bubbles) +
      popG(t, 0.1, 540, 420, badge(540, 420, 'TRIBÜNE: 3 PLÄTZE', {kind: 'red', fs: 54})) +
      popG(t, capT(2), 540, 560, badge(540, 560, 'FANS: 83', {kind: 'pitch', fs: 50, rot: -2}));
  },
  calc(t, d, m) {
    const lines = [['83 FOLLOWER × 1 €', '83 €'], ['24 KOMMENTARE × 2 €', '48 €'], ['VEREINSKASSE', '500 €']];
    const vx = 860 + Math.sin(t * 2.6) * 115, vflip = Math.cos(t * 2.6) < 0;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(vlad({blink: blinkAt(t)}), vx, 1124 - Math.abs(Math.sin(t * 10)) * 6, 0.3) + place(coach({mouth: m, blink: blinkAt(t)}), 540, 1660, 1.05)) +
      popG(t, 0.0, 540, 340, calcBoard(t, 110, 290, lines, [capT(0), capT(1), capT(2)]));
  },
  total(t, d, m) {
    let coins = '';
    for (let i = 0; i < 18; i++) { const t0 = rnd(i + 900) * 1.4, k = (t - t0) / 0.9; if (k > 0 && k < 1) coins += coin(80 + rnd(i + 950) * 920, -60 + k * 1500, 34, i % 2); }
    const lines = [['83 FOLLOWER × 1 €', '83 €'], ['24 KOMMENTARE × 2 €', '48 €'], ['VEREINSKASSE', '500 €']];
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1660, 1.05)) +
      calcBoard(9, 110, 290, lines, [0, 0, 0]) +
      `<path d="M150 760 H930" stroke="#3A2316" stroke-width="10"/>` +
      popG(t, 0.2, 540, 920, bigText(540, 1010, '= 631 €', '#6BF06B', 240)) + coins;
  },
  chairs(t, d, m) {
    let s = field(t, 720, {goal: false, touchY: 1310});
    s += chairRows(t, 95, 800, 10, 8, 99, 66, 0.17, 0.1, 0.018);
    return cam(1.0 + 0.04 * t / d, 540, 960, s) + popG(t, 0.0, 540, 360, badge(540, 360, 'KLAPPSTÜHLE FÜR ALLE', {kind: 'pitch', fs: 54}));
  },
  tarp(t, d, m) {
    let s = field(t, 720, {goal: false, touchY: 1310});
    s += chairRows(9, 95, 800, 10, 8, 99, 66, 0.17, 0, 0);
    s += seatedCrowd(t, 95, 800, 10, 8, 99, 66, 0.17, 0.35, 0.016, [74, 75, 76]);
    [0, 1, 2].forEach(i => { const x = 95 + (4 + i) * 99 + 0.5 * 99 - 99 * 0.25; s += place(fanFigure(Object.assign({blink: blinkAt(t, i)}, FIRST_FANS[i].o), true), x, 800 + 7 * 66, 0.17 * 1.56 * 0.62); });
    s += tarp(t, 45, 1035, 610, 1310, easeOut(clamp(t / 0.35, 0, 1)));
    return cam(1.0, 540, 960, s) +
      popG(t, 0.0, 540, 330, badge(540, 330, 'PLANE DRÜBER', {kind: 'pitch', fs: 56})) +
      popG(t, capT(2), 540, 470, badge(540, 470, 'KEINER WIRD NASS', {kind: 'orange', fs: 48, rot: -2}));
  },
  bus(t, d, m) {
    const x = 1500 - (t / d) * 2100;
    const id = 'win' + (UID++);
    const passenger = `<defs><clipPath id="${id}"><rect x="90" y="-300" width="120" height="120" rx="14"/></clipPath></defs>
      <g clip-path="url(#${id})">${place(busguy({mood: 'smile'}), 150, -82, 0.33)}</g>
      <g transform="translate(205 -250) rotate(${Math.sin(t * 12) * 20})"><circle r="16" fill="#E7C29C" stroke="#111" stroke-width="5"/></g>`;
    let s = field(t, 1000, {goal: false});
    s += `<rect x="-400" y="1080" width="1880" height="260" fill="#4E4E54"/><path d="M-400 1210 H1480" stroke="#F0EDE0" stroke-width="10" stroke-dasharray="70 50"/>`;
    s += busStop(120, 1090, 0.9) + cityBus(x, 1290, 1.05, t, passenger);
    return cam(1.0, 540, 960, s) + popG(t, 0.0, 540, 420, badge(540, 420, 'HEUTE MORGEN', {fs: 60}));
  },
  out(t, d, m) {
    // Nr. 9 wird dramatisch durchgestrichen: zwei rote Pinselstriche, Bildschuetteln, roter Blitz
    const k1 = clamp((t - 0.05) / 0.18, 0, 1), k2 = clamp((t - 0.25) / 0.18, 0, 1);
    const shake = t < 0.6 ? Math.sin(t * 90) * 14 * Math.exp(-t * 5) : 0;
    const L = 760;
    const strokes = `<g stroke-linecap="round" fill="none">
      <path d="M240 600 L840 1220" stroke="#111" stroke-width="64" stroke-dasharray="${L * 1.15}" stroke-dashoffset="${L * 1.15 * (1 - k1)}"/>
      <path d="M240 600 L840 1220" stroke="#E5483A" stroke-width="48" stroke-dasharray="${L * 1.15}" stroke-dashoffset="${L * 1.15 * (1 - k1)}"/>
      <path d="M840 600 L240 1220" stroke="#111" stroke-width="64" stroke-dasharray="${L * 1.15}" stroke-dashoffset="${L * 1.15 * (1 - k2)}"/>
      <path d="M840 600 L240 1220" stroke="#E5483A" stroke-width="48" stroke-dasharray="${L * 1.15}" stroke-dashoffset="${L * 1.15 * (1 - k2)}"/></g>`;
    const flash = t > 0.25 && t < 0.6 ? `<rect width="1080" height="1920" fill="#E5483A" opacity="${0.35 * (1 - (t - 0.25) / 0.35)}"/>` : '';
    return `<g transform="translate(${shake} 0)">` + cam(1.0, 540, 960, field(t, 1080, {goalX: 780}) +
        `<g opacity=".85">${place(busguy({mood: 'sad'}), 540, 1300, 1.0)}</g>`) +
      nameCard(80, 400, '9', '???', 'STÜRMER · BUS GENOMMEN') + strokes +
      popG(t, 0.45, 540, 1150, badge(540, 1150, 'RAUS!', {kind: 'red', fs: 90, rot: -8})) + `</g>` + flash;
  },
  search(t, d, m) {
    const sway = Math.sin(t * 2) * 5;
    const jersey = jersey9(540, 860, 1.05, sway);
    const beam = `<path d="M540 0 L300 1100 L780 1100 Z" fill="#FFF3B0" opacity=".14"/>`;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + beam) + jersey +
      popG(t, 0.0, 540, 400, badge(540, 400, 'GESUCHT: NR. 9', {kind: 'pitch', fs: 62})) +
      popG(t, capT(4), 540, 1150, badge(540, 1150, 'EINER VON EUCH!', {kind: 'orange', fs: 56, rot: -2}));
  },
  kasse0(t, d, m) {
    const lines = [['80 KLAPPSTÜHLE', '−500 €', '#E5483A'], ['PLANE', '−131 €', '#E5483A']];
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + crate(780, 1290, 0.75) + cashBox(780, 1160, 0.62, t >= capT(2) ? 'empty' : true) +
        place(coach({mouth: m, mood: t >= capT(2) ? 'sad' : 'talk', blink: blinkAt(t)}), 240, 1600, 0.95)) + moth(t, capT(3) + 0.1) +
      popG(t, 0.0, 540, 360, calcBoard(t, 110, 290, lines, [capT(0), capT(1)])) +
      popG(t, capT(2), 540, 700, badge(540, 680, 'VEREINSKASSE', {fs: 46})) +
      popG(t, capT(3), 540, 860, bigText(540, 965, '0 €', '#FF4A4A', 250));
  },
  rule(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    let coins = '';
    for (let i = 0; i < 12; i++) {
      const t0 = c[3] + 0.1 + i * 0.3, k = (t - t0) / 0.6, two = t0 >= c[4];
      if (k > 0 && k < 1) coins += coin(470 + rnd(i + 700) * 140, 560 + k * 340, two ? 36 : 30, two);
    }
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + crate(540, 1180, 0.95) + cashBox(540, 1015, 0.8, 'empty') + coins +
        place(coach({mouth: m, wave: t < c[3] ? Math.sin(t * 9) : 0, blink: blinkAt(t)}), 170, 1600, 0.85)) +
      (t < c[3] ? popG(t, c[0], 520, 400, badge(520, 400, 'WIR BRAUCHEN', {kind: 'red', fs: 60, rot: -2}))
                : popG(t, c[3], 520, 330, badge(520, 330, 'WIR BRAUCHEN DICH!', {kind: 'red', fs: 52, rot: -2}))) +
      (t >= c[0] && t < c[3] ? popG(t, c[0] + 0.1, 540, 700, `<g transform="translate(540 700) scale(${1 + 0.04 * Math.sin(t * 10)}) translate(-540 -700)">${bigText(540, 790, 'DICH!', '#FFD31A', 300)}</g>`) : '') +
      popG(t, c[3], 520, 470, badge(520, 470, '+1 € PRO FOLLOWER', {kind: 'pitch', fs: 46})) +
      popG(t, c[4], 520, 590, badge(520, 590, '+2 € PRO KOMMENTAR', {kind: 'orange', fs: 46, rot: -2}));
  },
  comment(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1680, 1.25)) +
      `<g transform="translate(510 500) scale(${1 + 0.025 * Math.sin(t * 6)}) translate(-510 -500)">${popG(t, 0.0, 510, 500, commentCard(70, 300, t, 'NR. 9 + KAUFEN: ...'))}</g>` +
      popG(t, 0.6, 520, 790, badge(520, 790, 'WER WIRD NR. 9?', {bg: '#FFD31A', fs: 50, rot: -2})) +
      popG(t, capT(2), 520, 920, badge(520, 920, 'WAS KAUFEN WIR?', {kind: 'pitch', fs: 50, rot: 2}));
  },
  sunday2(t, d, m) {
    const heu = `<g transform="translate(790 820)">
      <path d="M-150 -170 H150 V30 Q150 150 0 200 Q-150 150 -150 30 Z" fill="#E8C24A" stroke="#3A2316" stroke-width="12"/>
      <path d="M-150 -170 H150 V-110 H-150 Z" fill="#6B8E23" stroke="#3A2316" stroke-width="8"/>
      <text x="0" y="-126" text-anchor="middle" ${FONT} font-size="40" fill="#fff">SC HEUBALLEN</text>
      <ellipse cx="0" cy="30" rx="105" ry="80" fill="#F2D06B" stroke="#3A2316" stroke-width="9"/>
      <ellipse cx="-55" cy="30" rx="30" ry="80" fill="#E0B84A" stroke="#3A2316" stroke-width="6"/>
      <path d="M-20 -40 Q30 -30 90 -10 M-15 0 Q40 10 100 20 M-15 50 Q40 60 95 70 M-20 90 Q30 98 80 100" stroke="#C99A2E" stroke-width="5" fill="none"/>
      <path d="M-55 -50 V110 M40 -48 V108" stroke="#B83226" stroke-width="7"/></g>`;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 540}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1780, 0.8)) +
      popG(t, 0.0, 540, 340, badge(540, 340, 'SONNTAG · 1. SPIEL', {kind: 'pitch', fs: 58})) +
      popG(t, 0.25, 280, 820, `<g transform="translate(280 820) scale(0.6) translate(-300 -300)">${LOGO}</g>`) +
      popG(t, 0.5, 540, 820, bigText(540, 860, 'VS', '#FFD31A', 120)) +
      popG(t, 0.7, 790, 820, heu) +
      popG(t, capT(3), 540, 1110, badge(540, 1110, 'WIR BRAUCHEN EUCH!', {kind: 'red', fs: 54, rot: -2}));
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
  let r = rain(t, 150, 0.45);
  if (SEG.id === 'tarp') r = `<defs><mask id="tm"><rect width="1080" height="1920" fill="#fff"/><rect x="20" y="670" width="1040" height="640" fill="#000"/></mask></defs><g mask="url(#tm)">${r}</g>`;
  body += r;
  const cap = SEG.caps.find(c => t >= c.t0 && t < c.t1) || (t >= SEG.caps[SEG.caps.length - 1].t0 ? SEG.caps[SEG.caps.length - 1] : null);
  if (cap) body += caption(cap.text, cap.t0, t);
  if (si > 0) body += mudWipe(lt);
  document.getElementById('root').innerHTML = `<defs><linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2438"/><stop offset="1" stop-color="#46506A"/></linearGradient>
    <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient></defs>
    ${body}<rect width="1080" height="1920" fill="url(#vig)"/>`;
}
