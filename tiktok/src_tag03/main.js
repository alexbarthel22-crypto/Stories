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


function chairTribune(t) {
  let s = chairRows(9, 95, 800, 10, 8, 99, 66, 0.17, 0, 0);
  s += seatedCrowd(99, 95, 800, 10, 8, 99, 66, 0.17, 0, 0, [74, 75, 76]);
  [0, 1, 2].forEach(i => { const x = 95 + (4 + i) * 99 + 0.5 * 99 - 99 * 0.25; s += place(fanFigure(Object.assign({blink: blinkAt(t, i)}, FIRST_FANS[i].o), true), x, 800 + 7 * 66, 0.17 * 1.56 * 0.62); });
  return s + tarp(t, 45, 1035, 610, 1310, 1);
}

const SCENES = {
  intro(t, d, m) {
    const k = clamp(t / d, 0, 1), e = k * k * (3 - 2 * k), z = 0.7 + 0.3 * e;
    const world = field(t, 900, {goal: false, touchY: 1210}) + `<g transform="translate(0 -100)">${chairTribune(t)}</g>` +
      place(coach({mouth: m, blink: blinkAt(t)}), 540, 1420, 0.72);
    return cam(z, 540, 1110 - 40 * e, world) +
      `<g transform="rotate(${t > 0.3 ? Math.sin((t - 0.3) * 40) * 6 * Math.exp(-(t - 0.3) * 7) : 0} 540 440)">${badge(540, 440, 'TAG 3', {kind: 'pitch', fs: 150, pad: 120})}</g>` +
      popG(t, 0.55, 540, 640, twoLineBadge(540, 640, 'ICH GRÜNDE EINEN', 'FUSSBALLVEREIN', 52)) + introBall(t);
  },
  fans3(t, d, m) {
    const t0 = capT(2), n = t < t0 ? 83 : Math.round(83 + 317 * easeOut(clamp((t - t0) / 1.0, 0, 1)));
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 820}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 420, 1640, 1.2) +
        place(frog({blink: blinkAt(t, .4), mouth: t > t0}), 860, 1660 - Math.abs(Math.sin(t * 7)) * 70, 0.5)) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'GESTERN: 83 FANS', {fs: 46})) +
      popG(t, t0, 540, 500, badge(540, 500, 'HEUTE', {kind: 'pitch', fs: 56})) +
      (t >= t0 ? bigText(540, 760, String(n), '#6BF06B', 240) : '') +
      popG(t, t0 + 1.0, 870, 640, `<g transform="translate(870 640)"><circle r="70" fill="#3A2316"/><circle r="62" fill="#58B044" stroke="#fff" stroke-width="7"/>
        <path d="M0 -40 L32 0 L14 0 L14 34 L-14 34 L-14 0 L-32 0 Z" fill="#fff" stroke="#3A2316" stroke-width="4" stroke-linejoin="round"/></g>` + badge(870, 750, '+317', {kind: 'pitch', fs: 44}));
  },
  striker(t, d, m) {
    const t1 = capT(2);
    if (t < t1) return cam(1.0, 540, 960, field(t, 1080, {goalX: 780})) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'TOP-KOMMENTAR GESTERN', {kind: 'red', fs: 46})) +
      popG(t, 0.25, 540, 600, tiktokComment(80, 460, t)) +
      popG(t, 0.8, 540, 900, jerseyNum(540, 1000, 0.55, Math.sin(t * 2) * 4, '9', 'STURM'));
    const tt = t - t1;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 780}) + place(lkz({blink: blinkAt(t)}), 540, 1660 - Math.abs(Math.sin(tt * 8)) * 20 * Math.exp(-tt * 2), 1.45)) +
      popG(tt, 0.0, 500, 600, nameCard(80, 520, '9', 'LEBERKAASZERFETZER', 'STURM · NEUZUGANG').replace('font-size="72"', 'font-size="46"')) +
      popG(tt, 0.3, 860, 470, `<g transform="rotate(12 860 470)">${badge(860, 470, 'NEU!', {kind: 'red', fs: 60})}</g>`);
  },
  money3(t, d, m) {
    const lines = [['408 FOLLOWER × 1 €', '+408 €'], ['214 KOMMENTARE × 2 €', '+428 €'], ['VEREINSKASSE', '836 €']];
    let coins = '';
    const t3 = capT(2);
    for (let i = 0; i < 18; i++) { const t0 = t3 + rnd(i + 900) * 1.2, k = (t - t0) / 0.9; if (k > 0 && k < 1) coins += coin(80 + rnd(i + 950) * 920, -60 + k * 1500, 34, i % 2); }
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(coach({mouth: m, wave: t > t3 ? Math.sin(t * 10) : 0, blink: blinkAt(t)}), 540, 1660, 1.05)) +
      popG(t, 0.0, 540, 340, calcBoard(t, 110, 290, lines, [capT(0), capT(1), t3]).replace('>836 €</text>', ' font-size="84">836 €</text>').replace('font-size="62" fill="#2FA84A" font-size="84">836', 'font-size="84" fill="#2FA84A">836')) +
      (t >= t3 ? `<path d="M150 ${290 + 106 + 110 + 36} H930" stroke="#3A2316" stroke-width="7"/>` : '') + coins;
  },
  ikea(t, d, m) {
    const tb = 0.9, build = easeOut(clamp((t - tb) / 0.6, 0, 1)), fill = clamp((t - tb - 0.6) / 1.4, 0, 1);
    let s = wholePitch(t) + (t >= tb ? bigStand(t, build, fill) : '');
    let box = '';
    if (t < tb) { const k = easeOut(clamp(t / 0.45, 0, 1)); box = flatpack(540, -300 + k * 1000, 1.0, (1 - k) * -25); }
    else if (t < tb + 0.25) box = `<circle cx="540" cy="700" r="${(t - tb) * 2400}" fill="#fff" opacity="${1 - (t - tb) / 0.25}"/>`;
    return cam(1.0, 540, 960, s) + box +
      popG(t, 0.0, 540, 1150, badge(540, 1150, 'FERTIG-TRIBÜNE', {kind: 'pitch', fs: 54})) +
      popG(t, capT(3), 540, 1280, badge(540, 1280, '500 PLÄTZE!', {kind: 'orange', fs: 54, rot: -2})) +
      popG(t, 2.2, 240, 960, badge(240, 960, 'MIT ULTRAS!', {kind: 'red', fs: 40, rot: -4}));
  },
  honor(t, d, m) {
    const z = 1 + 2.4 * easeOut(clamp(t / 0.7, 0, 1)), [cx, cy] = standSeatPos(1);
    let s = cam(z, cx, cy - 10, wholePitch(t) + bigStand(t, 1, 1));
    let tags = '';
    [0, 1, 2].forEach(i => { const [x, y] = standSeatPos(i); const sx = 540 + z * (x - cx), sy = 960 + z * (y - 10 - cy);
      tags += popG(t, 0.75 + i * 0.15, sx, sy - 260, profilePic(sx, sy - 300, i, 62) + handleTag(sx, sy - 200, FIRST_FANS[i].handle, 0.75)); });
    return s + tags + popG(t, 0.6, 540, 1250, badge(540, 1250, '★ EHRENPLÄTZE ★', {kind: 'orange', fs: 54}));
  },
  kasse3(t, d, m) {
    const lines = [['FERTIG-TRIBÜNE', '−836 €', '#E5483A']];
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + crate(780, 1290, 0.75) + cashBox(780, 1160, 0.62, 'empty') +
        place(coach({mouth: m, mood: 'sad', blink: blinkAt(t)}), 240, 1600, 0.95)) + moth(t, capT(1) + 0.1) +
      popG(t, 0.0, 540, 340, calcBoard(t, 110, 290, lines, [0.1])) +
      popG(t, capT(0), 540, 640, badge(540, 620, 'VEREINSKASSE', {fs: 46})) +
      popG(t, capT(1), 540, 800, bigText(540, 900, '0 €', '#FF4A4A', 250));
  },
  mud(t, d, m) {
    let s = field(t, 1000, {goalX: 600, noPost: true, puddles: [[160, 1400, 160, 30], [880, 1520, 180, 34]]}) + floatingGoal(t, 600, 1040, 1.0);
    s += place(coach({mouth: m, mood: 'sad', blink: blinkAt(t)}), 170, 1660, 0.75);
    return cam(1.0, 540, 960, s) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'PLATZ = SCHLAMMLOCH', {kind: 'red', fs: 52})) +
      popG(t, capT(3), 540, 520, badge(540, 520, 'DAS TOR SCHWIMMT WEG!', {kind: 'orange', fs: 46, rot: -3}));
  },
  platzwart(t, d, m) {
    const c3 = capT(3), pulse = 0.5 + 0.5 * Math.sin(t * 12);
    const tape = (y, r) => `<g transform="rotate(${r} 540 ${y})"><rect x="-100" y="${y - 38}" width="1280" height="76" fill="#FFD31A" stroke="#111" stroke-width="6"/>
      ${Array.from({length: 22}, (_, i) => `<path d="M${-100 + i * 64} ${y + 38} l38 -76 h30 l-38 76z" fill="#111"/>`).join('')}
      <rect x="250" y="${y - 30}" width="580" height="60" fill="#FFD31A"/><text x="540" y="${y + 18}" text-anchor="middle" ${FONT} font-size="48" fill="#111">DRINGEND GESUCHT</text></g>`;
    const tools = `<g transform="translate(540 860) rotate(${Math.sin(t * 2) * 5})">
      <path d="M0 -260 V220" stroke="#8A5A36" stroke-width="22" stroke-linecap="round"/>
      <path d="M-120 220 H120" stroke="#9A9A9A" stroke-width="20" stroke-linecap="round"/>
      ${Array.from({length: 9}, (_, i) => `<path d="M${-110 + i * 27.5} 220 v50" stroke="#9A9A9A" stroke-width="10" stroke-linecap="round"/>`).join('')}
      <g transform="translate(150 -40) rotate(20)"><path d="M0 -200 V100" stroke="#8A5A36" stroke-width="20" stroke-linecap="round"/><path d="M-60 100 Q0 260 60 100 Z" fill="#9A9A9A" stroke="#3A2316" stroke-width="8"/></g>
      <g transform="translate(-170 40) rotate(-15)"><path d="M0 -150 V120" stroke="#8A5A36" stroke-width="16" stroke-linecap="round"/><rect x="-60" y="110" width="120" height="70" rx="10" fill="#E5483A" stroke="#3A2316" stroke-width="7"/></g></g>`;
    const siren = (x) => `<g transform="translate(${x} 560)"><path d="M-40 30 Q-40 -40 0 -40 Q40 -40 40 30Z" fill="${pulse > 0.5 ? '#FF4A4A' : '#9E2A2A'}" stroke="#111" stroke-width="7"/>
      <rect x="-50" y="28" width="100" height="22" rx="6" fill="#555" stroke="#111" stroke-width="6"/>
      ${pulse > 0.5 ? `<path d="M-80 -30 l-40 -20 M80 -30 l40 -20 M0 -60 v-40" stroke="#FF4A4A" stroke-width="10" stroke-linecap="round"/>` : ''}</g>`;
    let letters = '';
    if (t >= c3) for (let i = 0; i < 9; i++) {
      const t0 = c3 + i * 0.16, k = (t - t0) / 0.7;
      if (k > 0 && k < 1) { const x0 = 100 + rnd(i + 30) * 880, x = x0 + (540 - x0) * k, y = 1700 - k * 600; letters += `<text x="${x}" y="${y}" text-anchor="middle" font-family="Noto Color Emoji" font-size="${80 - k * 30}" transform="rotate(${(1 - k) * 30} ${x} ${y})">✉️</text>`; }
    }
    const inbox = t >= c3 ? popG(t, c3, 540, 1130, `<g transform="translate(540 1130) scale(${1 + 0.06 * pulse}) translate(-540 -1130)">${box(200, 1060, 680, 140, 'red', 11)}
      ${label(540, 1150, 'BEWERBUNGEN 👇', 70, '#fff').replace('👇', '')}<text x="830" y="1158" text-anchor="middle" font-family="Noto Color Emoji" font-size="64">👇</text></g>`) : '';
    return cam(1.0, 540, 960, field(t, 1080, {goal: false}) + `<rect width="1080" height="1920" fill="#E5483A" opacity="${0.12 * pulse}"/>`) +
      tools + siren(170) + siren(910) + popG(t, 0.0, 540, 400, tape(400, -3)) +
      popG(t, capT(2), 540, 1000, `<g transform="rotate(4 540 1000)">${badge(540, 1000, 'PLATZWART', {kind: 'pitch', fs: 80})}</g>`) +
      inbox + letters + popG(t, c3 + 0.6, 540, 1270, badge(540, 1270, 'TOP-KOMMENTAR GEWINNT!', {kind: 'orange', fs: 44, rot: -2}));
  },
  opa(t, d, m) {
    let s = field(t, 960, {goal: false, touchY: 1320});
    s += place(rockingOpa(t), 520, 1300, 0.95);
    return cam(1.0, 540, 960, s) +
      popG(t, 0.0, 500, 440, nameCard(80, 360, '4', 'OPA JÜRGEN', 'ABWEHR · IN RENTE')) +
      popG(t, capT(2), 860, 640, `<g transform="rotate(10 860 640)">${badge(860, 640, 'RENTE!', {kind: 'red', fs: 60})}</g>`);
  },
  abwehr(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + `<path d="M540 0 L300 1100 L780 1100 Z" fill="#FFF3B0" opacity=".14"/>`) +
      jerseyNum(540, 860, 1.05, Math.sin(t * 2) * 5, '4', 'ABWEHR') +
      popG(t, 0.0, 540, 400, badge(540, 400, 'GESUCHT: VERTEIDIGER', {kind: 'pitch', fs: 52}));
  },
  news(t, d, m) {
    const k = clamp(t / 0.6, 0, 1), e = easeOut(k);
    const rot = (1 - e) * 720 - 4, sc = 0.05 + 0.95 * e;
    const shake = t > 0.6 && t < 1.0 ? Math.sin(t * 90) * 12 * (1 - (t - 0.6) / 0.4) : 0;
    const flash = t > 0.6 && t < 0.9 ? `<rect width="1080" height="1920" fill="#fff" opacity="${0.7 * (1 - (t - 0.6) / 0.3)}"/>` : '';
    const stamp = popG(t, capT(4), 820, 380, `<g transform="rotate(-14 820 380)"><rect x="640" y="320" width="360" height="120" rx="14" fill="#fff" fill-opacity=".85" stroke="#E5483A" stroke-width="12"/>
      <text x="820" y="405" text-anchor="middle" ${FONT} font-size="76" fill="#E5483A">EILMELDUNG</text></g>`.replace('font-size="76"', 'font-size="56"'));
    const rays = `<g opacity=".25">${Array.from({length: 12}, (_, i) => { const a = i * 30 + t * 20; return `<path d="M540 800 L${540 + Math.cos(a * Math.PI / 180) * 1400} ${800 + Math.sin(a * Math.PI / 180) * 1400} L${540 + Math.cos((a + 12) * Math.PI / 180) * 1400} ${800 + Math.sin((a + 12) * Math.PI / 180) * 1400}Z" fill="#FFD31A"/>`; }).join('')}</g>`;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 540})) + `<rect width="1080" height="1920" fill="#000" opacity=".45"/>` + rays +
      `<g transform="translate(${540 + shake} 800) rotate(${rot}) scale(${sc}) translate(-540 -800)">${newspaper(t)}</g>` + stamp + flash;
  },
  train(t, d, m) {
    let run = '';
    const runners = [vlad({blink: blinkAt(t)}), lkz({}), teamPlayer(1, t), teamPlayer(2, t), teamPlayer(0, t), teamPlayer(6, t), teamPlayer(4, t), teamPlayer(5, t)];
    runners.forEach((svg, k) => { const x = ((t * 230 + k * 190) % 1520) - 220; run += place(svg, x, 1180 - Math.abs(Math.sin(t * 10 + k)) * 14, 0.36); });
    const t2 = capT(2);
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + run + place(coach({mouth: m, blink: blinkAt(t)}), 220, 1680, 0.9)) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'HÄRTER TRAINIEREN!', {kind: 'red', fs: 56, rot: -2})) +
      (t >= t2 ? popG(t, t2, 540, 600, bigText(540, 640, 'NOCH 3 TAGE', '#FFD31A', 110)) : '') +
      popG(t, capT(4), 540, 820, `<g transform="translate(330 830) scale(0.42) translate(-300 -300)">${LOGO}</g>` + bigText(540, 860, 'VS', '#FFD31A', 100) + heuLogo(750, 830, 0.6));
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
  end3(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1700, 1.15)) +
      `<g transform="translate(510 500) scale(${1 + 0.025 * Math.sin(t * 6)}) translate(-510 -500)">${popG(t, 0.0, 510, 500, commentCard(70, 300, t, 'ICH WERDE ...'))}</g>` +
      popG(t, capT(1), 300, 790, badge(300, 790, 'PLATZWART?', {kind: 'pitch', fs: 44, rot: -3})) +
      popG(t, capT(2), 760, 790, badge(760, 790, 'VERTEIDIGER?', {kind: 'pitch', fs: 44, rot: 3})) +
      popG(t, capT(3), 540, 910, badge(540, 910, 'WAS VORM SPIEL KAUFEN?', {bg: '#FFD31A', fs: 44, rot: -1}));
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
  if (false) r = `<defs><mask id="tm"><rect width="1080" height="1920" fill="#fff"/><rect x="20" y="670" width="1040" height="640" fill="#000"/></mask></defs><g mask="url(#tm)">${r}</g>`;
  body += r;
  const cap = SEG.caps.find(c => t >= c.t0 && t < c.t1) || (t >= SEG.caps[SEG.caps.length - 1].t0 ? SEG.caps[SEG.caps.length - 1] : null);
  if (cap) body += caption(cap.text, cap.t0, t);
  if (si > 0) body += mudWipe(lt);
  document.getElementById('root').innerHTML = `<defs><linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2438"/><stop offset="1" stop-color="#46506A"/></linearGradient>
    <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient></defs>
    ${body}<rect width="1080" height="1920" fill="url(#vig)"/>`;
}
