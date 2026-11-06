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
    const world = field(t, 900, {goal: false, touchY: 1210}) + `<g transform="translate(0 -100)">${chairTribune(t)}</g>` +
      place(coach({mouth: m, blink: blinkAt(t)}), 540, 1420, 0.72) +
      place(frog({blink: blinkAt(t, .4)}), 760, 1430 - Math.abs(Math.sin(t * 7)) * 30, 0.2);
    return cam(z, 540, 1110 - 40 * e, world) +
      `<g transform="rotate(${t > 0.3 ? Math.sin((t - 0.3) * 40) * 6 * Math.exp(-(t - 0.3) * 7) : 0} 540 440)">${badge(540, 440, 'TAG 3', {kind: 'pitch', fs: 150, pad: 120})}</g>` +
      introBall(t);
  },
  fans3(t, d, m) {
    const t0 = capT(2), n = t < t0 ? 83 : Math.round(83 + 317 * easeOut(clamp((t - t0) / 1.0, 0, 1)));
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 820}) + place(coach({mouth: m, wave: Math.sin(t * 10), blink: blinkAt(t)}), 420, 1640, 1.2)) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'GESTERN: 83 FANS', {fs: 46})) +
      popG(t, t0, 540, 500, badge(540, 500, 'HEUTE', {kind: 'pitch', fs: 56})) +
      (t >= t0 ? bigText(540, 760, String(n), '#6BF06B', 240) : '') +
      popG(t, t0 + 1.0, 800, 640, `<g transform="translate(800 640)"><circle r="70" fill="#3A2316"/><circle r="62" fill="#58B044" stroke="#fff" stroke-width="7"/>
        <path d="M0 -40 L32 0 L14 0 L14 34 L-14 34 L-14 0 L-32 0 Z" fill="#fff" stroke="#3A2316" stroke-width="4" stroke-linejoin="round"/></g>` + badge(800, 750, '+317', {kind: 'pitch', fs: 44})) + confetti(t, t0 + 1.0);
  },
  striker(t, d, m) {
    const t1 = capT(2);
    if (t < t1) return cam(1.0, 540, 960, field(t, 1080, {goalX: 780})) +
      popG(t, 0.0, 540, 360, badge(540, 360, 'TOP-KOMMENTAR GESTERN', {kind: 'red', fs: 46})) +
      popG(t, 0.25, 520, 600, `<g transform="translate(70 460) scale(0.9) translate(-70 -460)">${tiktokComment(70, 460, t)}</g>`) +
      popG(t, 0.8, 540, 900, jerseyNum(540, 1000, 0.55, Math.sin(t * 2) * 4, '9', 'STURM'));
    const tt = t - t1;
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 780}) + place(lkz({blink: blinkAt(t)}), 540, 1660 - Math.abs(Math.sin(tt * 8)) * 20 * Math.exp(-tt * 2), 1.45)) +
      popG(tt, 0.0, 500, 600, nameCard(80, 520, '9', 'LEBERKAASZERFETZER', 'STURM · NEUZUGANG').replace('font-size="72"', 'font-size="46"')) +
      popG(tt, 0.3, 760, 450, `<g transform="rotate(12 760 450)">${badge(760, 450, 'NEU!', {kind: 'red', fs: 60})}</g>`);
  },
  money3(t, d, m) {
    const lines = [['408 FOLLOWER × 1 €', '+408 €'], ['214 KOMMENTARE × 2 €', '+428 €'], ['VEREINSKASSE', '836 €', '#2FA84A', true]];
    let coins = '';
    const t3 = capT(2);
    for (let i = 0; i < 18; i++) { const t0 = t3 + rnd(i + 900) * 1.2, k = (t - t0) / 0.9; if (k > 0 && k < 1) coins += coin(80 + rnd(i + 950) * 920, -60 + k * 1500, 34, i % 2); }
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + place(coach({mouth: m, wave: t > t3 ? Math.sin(t * 10) : 0, blink: blinkAt(t)}), 540, 1660, 1.05)) +
      popG(t, 0.0, 540, 340, calcBoard(t, 70, 290, lines, [capT(0), capT(1), t3])) +
      (t >= t3 ? `<path d="M110 ${290 + 106 + 110 + 30} H890" stroke="#3A2316" stroke-width="7"/>` : '') + coins + confetti(t, t3 + 0.3, 30);
  },
  ikea(t, d, m) {
    const tb = 0.9, build = easeOut(clamp((t - tb) / 0.6, 0, 1)), fill = clamp((t - tb - 0.6) / 1.4, 0, 1);
    let s = wholePitch(t) + (t >= tb ? bigStand(t, build, fill) : '');
    let box = '';
    if (t < tb) { const k = easeOut(clamp(t / 0.45, 0, 1)); box = flatpack(540, -300 + k * 1000, 1.0, (1 - k) * -25); }
    else if (t < tb + 0.25) box = `<circle cx="540" cy="700" r="${(t - tb) * 2400}" fill="#fff" opacity="${1 - (t - tb) / 0.25}"/>`;
    return cam(0.82, 540, 820, s) + box +
      popG(t, 0.0, 540, 1150, badge(540, 1150, 'FERTIG-TRIBÜNE', {kind: 'pitch', fs: 54})) +
      popG(t, capT(3), 540, 1280, badge(540, 1280, '500 PLÄTZE!', {kind: 'orange', fs: 54, rot: -2})) +
      popG(t, 2.2, 240, 960, badge(240, 960, 'MIT ULTRAS!', {kind: 'red', fs: 40, rot: -4}));
  },
  ultras(t, d, m) {
    const z = 1 + 1.2 * easeOut(clamp(t / 0.6, 0, 1)), cx = 280, cy = 700;
    const sx = x => 540 + z * (x - cx), sy = y => 960 + z * (y - cy);
    return cam(z, cx, cy, wholePitch(t) + bigStand(t, 1, 1)) +
      popG(t, 0.2, 540, 340, badge(540, 340, 'ULTRA-BLOCK', {kind: 'red', fs: 60, rot: -2})) +
      popG(t, capT(2), 540, 480, badge(540, 480, 'NEUES LOGO AUS TAG 1', {kind: 'pitch', fs: 42})) +
      popG(t, capT(3), 600, 640, profilePic(600, 640, 0, 95) + `<g transform="rotate(-4 600 780)">${badge(600, 780, 'DANKE, EIKE!', {kind: 'orange', fs: 50})}</g>`);
  },
  honor(t, d, m) {
    const z = 1 + 2.4 * easeOut(clamp(t / 0.7, 0, 1)), [cx, cy] = standSeatPos(1);
    let s = cam(z, cx, cy - 10, wholePitch(t) + bigStand(t, 1, 1));
    let tags = '';
    [0, 1, 2].forEach(i => { const [x, y] = standSeatPos(i); const sx = 540 + z * (x - cx), sy = 960 + z * (y - 10 - cy);
      tags += popG(t, 0.75 + i * 0.15, sx, sy - 260, profilePic(sx, sy - 300, i, 62) + handleTag(sx, sy - 200, FIRST_FANS[i].handle, 0.75)); });
    return s + tags + popG(t, 0.6, 540, 1250, badge(540, 1250, '★ EHRENPLÄTZE ★', {kind: 'orange', fs: 54})) + popG(t, capT(3), 540, 1110, badge(540, 1110, 'UNSERE ERSTEN FANS!', {kind: 'pitch', fs: 46, rot: -2})) + confetti(t, 0.7, 30);
  },
  kasse3(t, d, m) {
    const lines = [['FERTIG-TRIBÜNE', '-836 €', '#E5483A', true]];
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 300}) + crate(780, 1290, 0.75) + cashBox(780, 1160, 0.62, 'empty') +
        place(coach({mouth: m, mood: 'sad', blink: blinkAt(t)}), 240, 1600, 0.95)) + moth(t, capT(1) + 0.1) +
      popG(t, 0.0, 540, 340, calcBoard(t, 70, 290, lines, [0.1])) +
      popG(t, capT(0), 540, 640, badge(540, 620, 'VEREINSKASSE', {fs: 46})) +
      popG(t, capT(1), 540, 800, bigText(540, 900, '0 €', '#FF4A4A', 250));
  },
  mud(t, d, m) {
    let s = field(t, 1000, {goalX: 600, noPost: true, puddles: [[160, 1400, 160, 30], [880, 1520, 180, 34]]}) + floatingGoal(t, 600, 1040, 1.0);
    s += place(coach({mouth: m, mood: 'sad', blink: blinkAt(t)}), 170, 1660, 0.75);
    return cam(1.0, 540, 960, s) + (t >= capT(3) - 0.2 && t < capT(3) + 1.6 ? alarmLights(t) : '') +
      popG(t, 0.0, 540, 360, badge(540, 360, 'PLATZ = SCHLAMMLOCH', {kind: 'red', fs: 52})) +
      popG(t, capT(3), 540, 520, badge(540, 520, 'DAS TOR SCHWIMMT WEG!', {kind: 'orange', fs: 46, rot: -3}));
  },
  platzwart(t, d, m) {
    const c = SEG.caps.map(x => x.t0 - SEG.start), pulse = 0.5 + 0.5 * Math.sin(t * 10);
    const defs = `<defs>
      <linearGradient id="pwMetal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F6F8"/><stop offset=".45" stop-color="#A9B0B8"/><stop offset=".55" stop-color="#E2E6EA"/><stop offset="1" stop-color="#6C737B"/></linearGradient>
      <linearGradient id="pwWood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6B4226"/><stop offset=".4" stop-color="#B07A48"/><stop offset=".6" stop-color="#C98E58"/><stop offset="1" stop-color="#5A361E"/></linearGradient>
      <linearGradient id="pwGold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF3A8"/><stop offset=".5" stop-color="#FFD31A"/><stop offset="1" stop-color="#C98A12"/></linearGradient>
      <radialGradient id="pwSiren" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#FFE0E0"/><stop offset=".35" stop-color="#FF3B3B"/><stop offset="1" stop-color="#7A0E0E"/></radialGradient>
      <radialGradient id="pwGlow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FF4A4A" stop-opacity=".85"/><stop offset="1" stop-color="#FF4A4A" stop-opacity="0"/></radialGradient>
      <linearGradient id="pwBeam" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FFF6C8" stop-opacity=".55"/><stop offset="1" stop-color="#FFF6C8" stop-opacity="0"/></linearGradient>
      <linearGradient id="pwRed" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF7A6E"/><stop offset=".5" stop-color="#E5483A"/><stop offset="1" stop-color="#A3241A"/></linearGradient>
    </defs>`;
    // Suchscheinwerfer
    let beams = '';
    [[200, 1], [880, -1]].forEach(([x, dir]) => { const a = dir * (18 * Math.sin(t * 1.6)) - dir * 8;
      beams += `<g transform="rotate(${a} ${x} 1500)"><path d="M${x - 30} 1500 L${x - 260} 200 L${x + 260} 200 L${x + 30} 1500 Z" fill="url(#pwBeam)"/></g>`; });
    // 3D-Titel: gestapelte Ebenen
    const title3d = (txt, cx, cy, fs) => { let s = ''; for (let k = 12; k > 0; k--) s += `<text x="${cx + k * 1.5}" y="${cy + k * 2.2}" text-anchor="middle" ${FONT} font-size="${fs}" fill="${k > 10 ? '#1A0E06' : '#7A4A10'}">${txt}</text>`;
      return s + `<text x="${cx}" y="${cy}" text-anchor="middle" ${FONT} font-size="${fs}" fill="url(#pwGold)" stroke="#3A2316" stroke-width="5" paint-order="stroke">${txt}</text>`; };
    // drehendes 3D-Warnschild
    const ry = Math.cos(t * 2.4), face = ry >= 0;
    const sign = (x, y) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.06, Math.abs(ry))} 1)">
      <path d="M0 -80 L80 0 L0 80 L-80 0 Z" fill="${face ? '#FFD31A' : '#C99A12'}" stroke="#111" stroke-width="9"/>
      ${face ? `<path d="M0 -80 L80 0 L0 0 Z" fill="#fff" opacity=".18"/><text x="0" y="34" text-anchor="middle" ${FONT} font-size="100" fill="#111">!</text>` : ''}</g>`;
    // Sirene mit Glanz und Lichtkegel
    const siren = (x) => { const a = t * 400 % 360;
      return `<g transform="translate(${x} 640)"><circle r="${110 + 20 * pulse}" fill="url(#pwGlow)" opacity="${0.5 + 0.5 * pulse}"/>
        <g transform="rotate(${a})"><path d="M0 0 L-60 -380 L60 -380 Z" fill="#FF6A6A" opacity=".18"/></g>
        <rect x="-62" y="34" width="124" height="34" rx="8" fill="url(#pwMetal)" stroke="#111" stroke-width="6"/>
        <path d="M-50 36 Q-50 -56 0 -56 Q50 -56 50 36 Z" fill="url(#pwSiren)" stroke="#111" stroke-width="7"/>
        <ellipse cx="-16" cy="-26" rx="12" ry="20" fill="#fff" opacity=".6"/></g>`; };
    // hochwertige Werkzeuge: Rechen und Spaten gekreuzt, Schubkarre davor
    const tools = `<g transform="translate(540 870) scale(${0.6 + 0.01 * Math.sin(t * 3)})">
      <g transform="rotate(-24)">
        <rect x="-12" y="-330" width="24" height="560" rx="12" fill="url(#pwWood)" stroke="#3A2316" stroke-width="6"/>
        <rect x="-150" y="218" width="300" height="34" rx="10" fill="url(#pwMetal)" stroke="#3A2316" stroke-width="6"/>
        ${Array.from({length: 11}, (_, i) => `<path d="M${-140 + i * 28} 250 l0 52 l6 8" stroke="#6C737B" stroke-width="11" fill="none" stroke-linecap="round"/><path d="M${-142 + i * 28} 252 v40" stroke="#E2E6EA" stroke-width="4" stroke-linecap="round"/>`).join('')}</g>
      <g transform="rotate(24)">
        <rect x="-12" y="-330" width="24" height="420" rx="12" fill="url(#pwWood)" stroke="#3A2316" stroke-width="6"/>
        <path d="M-40 -330 h80 v-26 a40 40 0 0 0 -80 0z" fill="#2A2A2E" stroke="#111" stroke-width="6"/>
        <path d="M-80 90 L80 90 L70 250 Q0 320 -70 250 Z" fill="url(#pwMetal)" stroke="#3A2316" stroke-width="7"/>
        <path d="M-50 110 L-44 240" stroke="#fff" stroke-width="10" opacity=".5" stroke-linecap="round"/></g>
      <g transform="translate(0 250)">
        <path d="M-200 -60 L200 -60 L160 60 L-160 60 Z" fill="url(#pwRed)" stroke="#3A2316" stroke-width="8" stroke-linejoin="round"/>
        <path d="M-180 -48 L180 -48" stroke="#fff" stroke-width="8" opacity=".35"/>
        <ellipse cx="0" cy="-60" rx="200" ry="22" fill="#6B4A30" stroke="#3A2316" stroke-width="6"/>
        <circle cx="0" cy="110" r="46" fill="#2A2A2E" stroke="#111" stroke-width="8"/><circle cx="0" cy="110" r="16" fill="url(#pwMetal)"/>
        <path d="M-160 40 L-260 120 M160 40 L260 120" stroke="url(#pwWood)" stroke-width="20" stroke-linecap="round"/></g></g>`;
    // Bewerbungs-Umschlaege mit 3D-Flip
    let letters = '';
    if (t >= c[3]) for (let i = 0; i < 10; i++) {
      const t0 = c[3] + i * 0.14, k = (t - t0) / 0.75;
      if (k > 0 && k < 1) { const x0 = 80 + rnd(i + 30) * 920, x = x0 + (540 - x0) * k, y = 1750 - k * 530, fl = Math.cos(k * 8);
        letters += `<g transform="translate(${x} ${y}) rotate(${(1 - k) * 40 * (i % 2 ? 1 : -1)}) scale(${0.9 - k * 0.4} ${(0.9 - k * 0.4) * Math.max(0.15, Math.abs(fl))})">
          <rect x="-60" y="-40" width="120" height="80" rx="8" fill="${fl > 0 ? '#FFFFFF' : '#E8E2D6'}" stroke="#3A2316" stroke-width="6"/>
          ${fl > 0 ? `<path d="M-60 -40 L0 10 L60 -40" stroke="#3A2316" stroke-width="6" fill="none"/><circle cx="34" cy="16" r="10" fill="#E5483A"/>` : ''}</g>`; }
    }
    const inbox = t >= c[3] ? popG(t, c[3], 540, 1160, `<g transform="translate(540 1160) scale(${1 + 0.05 * pulse}) translate(-540 -1160)">
      <rect x="196" y="1104" width="700" height="130" rx="24" fill="#5E120C"/>
      <rect x="190" y="1090" width="700" height="130" rx="24" fill="url(#pwRed)" stroke="#3A2316" stroke-width="9"/>
      <rect x="206" y="1102" width="668" height="40" rx="16" fill="#fff" opacity=".18"/>
      ${label(510, 1180, 'BEWERBUNGEN', 72, '#fff')}<text x="820" y="${1186 + 10 * Math.abs(Math.sin(t * 6))}" text-anchor="middle" font-family="Noto Color Emoji" font-size="70">👇</text></g>`) : '';
    return defs + cam(1.0, 540, 960, field(t, 1080, {goal: false})) + `<rect width="1080" height="1920" fill="#000" opacity=".45"/>` + beams +
      `<rect width="1080" height="1920" fill="#E5483A" opacity="${0.10 * pulse}"/>` +
      siren(150) + siren(930) + popG(t, 0.0, 540, 360, title3d('DRINGEND', 540, 400, 130)) +
      popG(t, 0.15, 540, 470, title3d('GESUCHT!', 540, 520, 96)) + sign(150, 860) + sign(930, 860) +
      popG(t, c[1], 540, 870, tools) +
      popG(t, c[2], 540, 640, `<g transform="translate(540 640) scale(${1 + 0.05 * Math.abs(Math.sin(t * 6))}) rotate(-4) translate(-540 -640)">
        <rect x="150" y="560" width="780" height="160" rx="34" fill="#5E120C" transform="translate(10 14)"/>
        <rect x="150" y="560" width="780" height="160" rx="34" fill="url(#pwRed)" stroke="#fff" stroke-width="10"/>
        <rect x="170" y="574" width="740" height="46" rx="20" fill="#fff" opacity=".2"/>
        <text x="540" y="684" text-anchor="middle" ${FONT} font-size="124" fill="#fff" stroke="#5E120C" stroke-width="12" paint-order="stroke" letter-spacing="3">PLATZWART</text></g>`) +
      inbox + letters + (t >= c[5] ? `<g opacity="${Math.sin(t * 16) > -0.3 ? 1 : 0.25}" transform="translate(540 1330) scale(${1 + 0.06 * Math.abs(Math.sin(t * 8))}) translate(-540 -1330)">${badge(540, 1330, 'TOP-KOMMENTAR GEWINNT!', {kind: 'orange', fs: 50, rot: -2})}</g>` : '');
  },
  opa(t, d, m) {
    let s = field(t, 960, {goal: false, touchY: 1320});
    s += place(rockingOpa(t), 520, 1300, 0.95);
    return cam(1.0, 540, 960, s) +
      popG(t, 0.0, 500, 440, nameCard(80, 360, '4', 'OPA JÜRGEN', 'ABWEHR · IN RENTE')) +
      popG(t, capT(2), 740, 640, `<g transform="rotate(10 740 640)">${badge(740, 640, 'RENTE!', {kind: 'red', fs: 60})}</g>`);
  },
  abwehr(t, d, m) {
    return cam(1.0, 540, 960, field(t, 1080, {goalX: 860}) + `<path d="M540 0 L300 1100 L780 1100 Z" fill="#FFF3B0" opacity=".14"/>`) +
      jerseyNum(540, 860, 1.05, Math.sin(t * 2) * 5, '4', 'ABWEHR') +
      popG(t, 0.0, 540, 400, badge(540, 400, 'GESUCHT: VERTEIDIGER', {kind: 'pitch', fs: 52})) + bewerbungen(t, capT(3), 1220);
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
      (t >= t2 ? popG(t, t2, 540, 600, `<g opacity="${Math.sin(t * 14) > -0.4 ? 1 : 0.35}" transform="translate(540 600) scale(${1 + 0.07 * Math.abs(Math.sin(t * 7))}) translate(-540 -600)"><ellipse cx="540" cy="600" rx="${380 + 30 * Math.sin(t * 7)}" ry="110" fill="#FFD31A" opacity="${0.25 + 0.2 * Math.abs(Math.sin(t * 7))}"/>${bigText(540, 640, 'NOCH 3 TAGE', '#FFE45A', 110)}</g>`) : '') +
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
      popG(t, capT(1), 540, 780, badge(540, 780, 'PLATZWART?', {kind: 'pitch', fs: 44, rot: -3})) +
      popG(t, capT(2), 540, 880, badge(540, 880, 'VERTEIDIGER?', {kind: 'pitch', fs: 44, rot: 2})) +
      popG(t, capT(3), 540, 985, badge(540, 985, 'WAS VORM SPIEL KAUFEN?', {bg: '#FFD31A', fs: 44, rot: -1}));
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
