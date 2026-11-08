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
      `<g transform="rotate(${t > 0.3 ? Math.sin((t - 0.3) * 40) * 6 * Math.exp(-(t - 0.3) * 7) : 0} 540 440)">${badge(540, 440, 'TAG 5', {kind: 'pitch', fs: 150, pad: 120})}</g>` +
      twoLineBadge(540, 640, 'ICH GRÜNDE EINEN', 'FUSSBALLVEREIN', 52) +
      introBall(t);
  },
  fans5(t, d, m) {
    const t0 = capT(2), n = t < t0 ? 477 : Math.round(477 + 17 * easeOut(clamp((t - t0) / 0.7, 0, 1)));
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 820}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 420, 1640, 1.2)) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'GESTERN: 477 FANS', {fs: 46})) +
      popG(t, t0, 540, 500, badge(540, 500, 'HEUTE', {kind: 'pitch', fs: 56})) +
      (t >= t0 ? bigText(540, 760, String(n), '#6BF06B', 240) : '') +
      popG(t, t0 + 0.7, 800, 640, `<g transform="translate(800 640)"><circle r="70" fill="#3A2316"/><circle r="62" fill="#58B044" stroke="#fff" stroke-width="7"/>
        <path d="M0 -40 L32 0 L14 0 L14 34 L-14 34 L-14 0 L-32 0 Z" fill="#fff" stroke="#3A2316" stroke-width="4" stroke-linejoin="round"/></g>` + badge(800, 750, '+17', {kind: 'pitch', fs: 44})) + confetti(t, t0 + 0.7);
  },
  co13(t, d, m) {
    const t1 = capT(2);
    if (t < t1) return cam(1.0, 540, 960, field(t, 1080, {goalX: 780})) +
      popG(t, 0.0, 540, 380, badge(540, 380, 'TOP-KOMMENTAR', {kind: 'red', fs: 50})) +
      popG(t, 0.2, 520, 640, `<g transform="translate(70 520) scale(0.9) translate(-70 -520)">${commentReplica(70, 520, t, P13_PIC, '13', '🇦🇫', 'Kann ich co-Trainer sein bitte')}</g>`);
    const tt = t - t1;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 780}) + place(co13({blink: blinkAt(t)}), 540, 1660 - Math.abs(Math.sin(tt * 8)) * 20 * Math.exp(-tt * 2), 1.45)) +
      popG(tt, 0.0, 500, 600, nameCard(80, 520, '13', '„13“', 'CO-TRAINER · NEUZUGANG')) +
      popG(tt, 0.3, 760, 450, `<g transform="rotate(12 760 450)">${badge(760, 450, 'NEU!', {kind: 'red', fs: 60})}</g>`) + confetti(t, t1 + 0.1, 30);
  },
  matchday(t, d, m) {
    let ours = '', theirs = '';
    [vlad({}), denny({}), lkz({}), teamPlayer(2, t), teamPlayer(1, t)].forEach((svg, i) => { ours += place(svg, 80 + i * 90, 1560 + (i % 2) * 40, 0.36); });
    [0, 1, 2, 3, 4].forEach(i => { theirs += place(heu({num: String([1, 4, 7, 9, 10][i]), blink: blinkAt(t, i)}), 620 + i * 90, 1560 + (i % 2) * 40, 0.36, true); });
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 540}) + ours + theirs) +
      popG(t, 0.0, 540, 400, bigText(540, 440, 'SPIELTAG!', '#FFD31A', 140)) +
      popG(t, capT(2), 280, 820, `<g transform="translate(280 820) scale(0.55) translate(-300 -300)">${LOGO}</g>`) +
      popG(t, capT(3), 540, 820, bigText(540, 860, 'VS', '#fff', 120)) +
      popG(t, capT(3) + 0.15, 800, 820, heuLogo(800, 820, 0.75));
  },
  crowd(t, d, m) {
    const z = 1.25 + 0.15 * easeOut(clamp(t / d, 0, 1));
    return cam(z, 360, 600, wholePitch(t) + bigStand(t, 1, 1)) +
      popG(t, 0.0, 540, 1200, badge(540, 1200, 'AUSVERKAUFT!', {kind: 'red', fs: 64, rot: -3})) + confetti(t, 0.2, 40);
  },
  kickoff(t, d, m) {
    let s = field(t, 960, {goal: false}) + `<g fill="none" stroke="#F0EDE0" stroke-width="7"><ellipse cx="540" cy="1300" rx="300" ry="110"/><path d="M-400 1300 H1480"/></g>`;
    s += `<rect x="-400" y="1560" width="1880" height="400" fill="#4A8038"/><path d="M-400 1560 H1480" stroke="#F0EDE0" stroke-width="10"/>` + sleepyOpa(t, 860, 1780, 0.42, false) + place(frog({blink: blinkAt(t), mouth: true}), 140 + (t * 300) % 800, 1230 - Math.abs(Math.sin(t * 9)) * 50, 0.26) + place(lkz({}), 430, 1320, 0.5) + place(heu({num: '9'}), 650, 1300, 0.5, true) + `<g transform="translate(540 1300)">${ballIcon(0, 0, 26)}</g>`;
    return cam(1.0, 540, 960, s) + scoreBug(0, 0, "1'") + popG(t, 0.0, 540, 760, bigText(540, 800, 'ANPFIFF!', '#fff', 150)) + popG(t, 0.4, 540, 1000, badge(540, 1000, 'FRODO AUF DEM PLATZ!', {kind: 'orange', fs: 40, rot: -3}));
  },
  h1(t, d, m) {
    const tg = capT(1) + 0.4;
    return cam(1.0, 540, 960, shotScene(t, heu({num: '9', mood: 'smile'}), vlad({mood: 'sad', blink: blinkAt(t)}), tg - 0.6, tg, 300, false, 1)) +
      scoreBug(t < tg ? 0 : 0, t < tg ? 0 : 1, "23'") + goalFlash(t, tg, '0:1', '#FF5A4A');
  },
  eq1(t, d, m) {
    const tg = capT(1) + 0.3;
    return cam(1.0, 540, 960, shotScene(t, lkz({mood: 'talk', mouth: 1}), heuKeeper({mood: 'sad'}), tg - 0.6, tg, 820, false, -1)) +
      scoreBug(t < tg ? 0 : 1, 1, "38'") + goalFlash(t, tg, 'TOR!', '#6BF06B') + confetti(t, tg, 50);
  },
  half(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080, {goal: false}) + `<rect width="1080" height="1920" fill="#000" opacity=".25"/>` +
        sleepyOpa(t, 870, 1120, 0.35, false) + place(co13({mouth: 1, mood: 'talk', blink: blinkAt(t)}), 330, 1700, 1.0) + place(coach({mouth: m, blink: blinkAt(t)}), 760, 1700, 0.9)) +
      scoreBug(1, 1, 'HALBZEIT') + popG(t, capT(1), 540, 640, badge(540, 640, 'TAKTIK VON 13', {kind: 'pitch', fs: 54, rot: -2}));
  },
  h2(t, d, m) {
    const tg = capT(3) + 0.1;
    return cam(1.0, 540, 960, shotScene(t, heu({num: '10'}), vlad({mood: 'sad', blink: blinkAt(t)}), tg - 0.6, tg, 760, false, -1)) +
      scoreBug(1, t < tg ? 1 : 2, "61'") + goalFlash(t, tg, '1:2', '#FF5A4A');
  },
  pen(t, d, m) {
    const tg = capT(2) + 0.2;
    let s = shotScene(t, heu({num: '9'}), vlad({blink: blinkAt(t)}), tg - 0.5, tg, 330, true, -1);
    return cam(1.0, 540, 960, s + `<ellipse cx="540" cy="1520" rx="12" ry="6" fill="#fff"/>`) + scoreBug(1, 2, "74'") +
      popG(t, 0.0, 540, 560, badge(540, 560, 'ELFMETER!', {kind: 'red', fs: 60, rot: -2})) +
      popG(t, tg, 540, 700, badge(540, 700, 'GEHALTEN!', {kind: 'pitch', fs: 70, rot: 3})) +
      popG(t, capT(3), 540, 830, badge(540, 830, 'MIT EINEM AUGE!', {kind: 'orange', fs: 50, rot: -2})) + confetti(t, tg, 40);
  },
  eq2(t, d, m) {
    const ts = capT(1), tg = ts + 0.7;
    if (t < ts) {
      const k = easeOut(clamp(t / 0.6, 0, 1)), x = -100 + k * 600;
      const s = field(t, 1000, {goalX: 860}) + place(heu({num: '7'}), 640, 1300, 0.62, true) +
        `<g transform="rotate(-58 ${x} 1270)">${place(denny({}), x, 1270, 0.72)}</g>` +
        `<g transform="translate(${k > 0.9 ? 600 + (k - 0.9) * 3000 : 600} 1240)">${ballIcon(0, 0, 40)}</g>`;
      return cam(1.0, 540, 960, s) + scoreBug(1, 2, "83'") + popG(t, 0.2, 540, 600, badge(540, 600, 'GRÄTSCHE!', {kind: 'orange', fs: 64, rot: -3}));
    }
    return cam(1.0, 540, 960, shotScene(t, teamPlayer(2, t), heuKeeper({mood: 'sad'}), ts, tg, 300, false, 1)) +
      scoreBug(t < tg ? 1 : 2, 2, "84'") + goalFlash(t, tg, '2:2!', '#6BF06B') + confetti(t, tg, 50);
  },
  last(t, d, m) {
    const z = 1 + 0.25 * easeOut(clamp(t / d, 0, 1));
    const clock = `<g opacity="${Math.sin(t * 12) > -0.3 ? 1 : 0.3}">${badge(540, 560, "90.+3'", {kind: 'red', fs: 70})}</g>`;
    return `<g transform="translate(540 1300) scale(${z}) translate(-540 -1300)">` + cam(1.0, 540, 960, shotScene(t, lkz({mood: 'talk', mouth: 0.6}), heuKeeper({}), 99, 100, 540, false, 0)) + `</g>` +
      scoreBug(2, 2, "90.+3'") + clock + `<rect width="1080" height="1920" fill="#000" opacity="${0.25 * clamp(t / d, 0, 1)}"/>`;
  },
  win(t, d, m) {
    const tg = 0.15;
    let s = shotScene(t + 0.6, lkz({mood: 'talk', mouth: 1}), heuKeeper({mood: 'sad'}), 0, tg + 0.6, 820, false, -1);
    let jump = '';
    if (t > 1.0) { [vlad({}), denny({}), teamPlayer(2, t), co13({}), coach({mouth: 1})].forEach((svg, i) => { jump += place(svg, 120 + i * 210, 1880 - Math.abs(Math.sin(t * 9 + i)) * 80, 0.55); }); }
    return cam(1.0, 540, 960, s) + scoreBug(t < tg ? 2 : 3, 2, 'ABPFIFF') + goalFlash(t, tg, 'TOR!!!', '#6BF06B') +
      popG(t, capT(2), 540, 1050, badge(540, 1050, 'SIEG! 3:2', {kind: 'pitch', fs: 80, rot: -3})) + jump + confetti(t, tg, 70);
  },
  opa5(t, d, m) {
    const wake = t > capT(2) + 0.5;
    let s = field(t, 960, {goal: false, touchY: 1320});
    s += sleepyOpa(t, 520, 1300, 0.95, wake);
    return cam(1.0, 540, 960, s) + popG(t, 0.0, 500, 440, nameCard(80, 360, '4', 'OPA JÜRGEN', 'RENTNER · SCHLÄFT')) +
      popG(t, capT(2), 790, 600, `<g transform="rotate(10 790 600)">${badge(790, 600, 'ZZZ ...', {kind: 'red', fs: 52})}</g>`) +
      (wake ? popG(t, capT(2) + 0.5, 290, 600, badge(290, 600, 'WIE STEHT\'S?', {kind: 'pitch', fs: 48, rot: -3})) : '');
  },
  money5(t, d, m) {
    const lines = [['494 FANS × 5 €', '+2470 €'], ['31 KOMMENTARE × 2 €', '+62 €'], ['VEREINSKASSE', '2532 €', '#2FA84A', true]];
    const t3 = capT(5);
    let coins = '';
    for (let i = 0; i < 24; i++) { const t0 = capT(1) + rnd(i + 900) * 2.6, k = (t - t0) / 0.9; if (k > 0 && k < 1) coins += coin(80 + rnd(i + 950) * 860, -60 + k * 1500, 34, i % 2); }
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + crate(760, 1330, 0.7) + cashBox(760, 1210, 0.58, true) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 240, 1640, 0.95)) +
      popG(t, 0.0, 540, 340, calcBoard(t, 70, 290, lines, [capT(1), capT(2), t3])) + (t >= t3 ? `<path d="M110 ${290 + 106 + 110 + 30} H890" stroke="#3A2316" stroke-width="7"/>` : '') + coins + confetti(t, t3, 40);
  },
  vote(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start);
    const iconGrill = `<g transform="translate(0 30) scale(0.5)">${grill(0, 0, 1, t)}</g>`;
    const iconCab = `<g transform="translate(0 70) scale(0.3)">${bauwagen(0, 0, 1)}</g>`;
    return cam(1.0, 540, 960, field(t, 1080, {goal: false}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 540, 1720, 0.95)) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'WAS MACHEN WIR DAMIT?', {fs: 48})) +
      popG(t, c[2], 285, 740, `<g transform="translate(285 740) scale(1.25) translate(-285 -740)">${optionCard(285, 740, iconGrill, 'WÜRSTCHEN-', 'STAND', -5)}</g>`) +
      popG(t, c[3] - 0.3, 540, 720, bigText(530, 760, 'ODER', '#fff', 50)) +
      popG(t, c[3], 775, 740, `<g transform="translate(775 740) scale(1.25) translate(-775 -740)">${optionCard(775, 740, iconCab, 'SPIELER-', 'KABINE', 5)}</g>`) +
      (t >= c[4] ? `<g opacity="${Math.sin(t * 14) > -0.3 ? 1 : 0.3}">${badge(530, 1060, 'ABSTIMMEN IN DEN KOMMENTAREN 👇', {kind: 'red', fs: 36})}</g>` : '');
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
