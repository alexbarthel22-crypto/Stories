// Tag 3 – neue Grafiken

// Neuer Stuermer Nr. 9: Leberkaaszerfetzer (Neuzugang)
function lkz(o = {}) {
  return player(Object.assign({
    jersey: '#2F7FD8', trim: '#FFD31A', num: '9', shorts: '#1F3E66', skin: '#F2C9A0', browCol: '#3A2416',
    hair: `<path d="M100 196 Q100 74 250 72 Q400 74 400 196 Q380 132 250 128 Q120 132 100 196Z" fill="#4A2E1C"/>`,
    hairOver: `<path d="M150 112 Q250 64 350 112" stroke="#4A2E1C" stroke-width="22" fill="none" stroke-linecap="round"/>`,
    face: `<path d="M150 268 Q250 330 350 268 Q340 340 250 356 Q160 340 150 268Z" fill="#6B4A32" opacity=".35"/>`,
    mood: 'talk', mouth: 0.7,
    front: `<g transform="translate(300 420)"><path d="M0 -26 L8 -8 L28 -8 L12 4 L18 24 L0 12 L-18 24 L-12 4 L-28 -8 L-8 -8Z" fill="#FFD31A" stroke="#111" stroke-width="5"/></g>`,
  }, o));
}

// TikTok-Kommentar-Nachbau
function tiktokComment(x, y, t) {
  const id = 'lk' + (UID++);
  return `<g transform="translate(${x} ${y})">
    <rect x="8" y="12" width="920" height="300" rx="30" fill="#000" opacity=".45"/>
    <rect x="0" y="0" width="920" height="300" rx="30" fill="#1E1E1E" stroke="#fff" stroke-width="5"/>
    <defs><clipPath id="${id}"><circle cx="100" cy="100" r="64"/></clipPath></defs>
    <image href="${LKZ_PIC}" x="36" y="36" width="128" height="128" clip-path="url(#${id})"/>
    <text x="200" y="82" font-family="Inter" font-weight="700" font-size="40" fill="#9A9A9A">Leberkaaszerfetzer</text>
    <text x="610" y="82" font-family="Noto Color Emoji" font-size="38">🐻🦣</text>
    <text x="200" y="150" font-family="Inter" font-weight="600" font-size="52" fill="#fff">bitte ich Stürmer</text>
    <text x="200" y="240" font-family="Inter" font-weight="700" font-size="34" fill="#8A8A8A">8 Std   Antworten</text>
    <g transform="translate(800 140) scale(${1 + 0.12 * Math.max(0, Math.sin(t * 9))})"><path d="M0 -14 c-22 -30 -64 -8 -46 24 l46 46 l46 -46 c18 -32 -24 -54 -46 -24z" fill="#FE2C55" stroke="#fff" stroke-width="4"/></g>
    <text x="800" y="250" text-anchor="middle" font-family="Inter" font-weight="800" font-size="34" fill="#fff">40</text></g>`;
}

// Flachpaket mit Bauanleitung-Charme
function flatpack(cx, cy, s, rot) {
  return `<g transform="translate(${cx} ${cy}) rotate(${rot}) scale(${s})">
    <rect x="-260" y="-150" width="520" height="300" rx="8" fill="#C8A26B" stroke="#3A2316" stroke-width="10"/>
    <path d="M-260 -60 H260" stroke="#A9824E" stroke-width="8"/><path d="M-40 -150 V150" stroke="#E6CB9A" stroke-width="30" opacity=".7"/>
    <text x="0" y="-80" text-anchor="middle" ${FONT} font-size="60" fill="#3A2316">TRIBÜNSTAD</text>
    <text x="0" y="0" text-anchor="middle" ${FONT} font-size="34" fill="#3A2316">500 PLÄTZE · SELBSTAUFBAU</text>
    <g transform="translate(-150 80)"><path d="M-40 -20 h60 v-30" stroke="#3A2316" stroke-width="12" fill="none" stroke-linecap="round"/></g>
    <g transform="translate(120 80)" fill="#3A2316"><circle cx="0" cy="-30" r="14"/><path d="M-16 -12 h32 l8 50 h-48z"/><circle cx="70" cy="-30" r="14"/><path d="M54 -12 h32 l8 50 h-48z"/></g>
  </g>`;
}

// Grosse Tribuene mit ~500 Fans, Dach, Ehrenplaetze vorne in der Mitte
const STAND = {x0: 40, cols: 24, dx: 42, rowTop: 330, rows: 21, dy: 19};
function bigStand(t, build, fill) {
  const {x0, cols, dx, rowTop, rows, dy} = STAND;
  const bottom = rowTop + rows * dy + 30, h = (bottom - 230) * build;
  let s = `<g transform="translate(0 ${bottom}) scale(1 ${Math.max(0.001, build)}) translate(0 ${-bottom})">
    <rect x="20" y="230" width="1040" height="${bottom - 230}" fill="#8C939C" stroke="#3A2316" stroke-width="8"/>`;
  for (let r = 0; r <= rows; r++) s += `<path d="M20 ${rowTop + r * dy + 8} H1060" stroke="#6F7680" stroke-width="5"/>`;
  s += `<path d="M0 230 L540 170 L1080 230 L1080 262 L0 262 Z" fill="#2F7FD8" stroke="#3A2316" stroke-width="8"/>
    <text x="540" y="252" text-anchor="middle" ${FONT} font-size="30" fill="#FFD31A" letter-spacing="3">SCHLAMMLOCH-ARENA</text>`;
  [60, 540, 1020].forEach(x => { s += `<rect x="${x - 8}" y="262" width="16" height="${bottom - 262}" fill="#5A6068"/>`; });
  s += `</g>`;
  if (build >= 1) {
    const total = rows * cols, n = Math.floor(total * fill);
    const honor = [(rows - 1) * cols + 11, (rows - 1) * cols + 12, (rows - 1) * cols + 13];
    let k = 0;
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const idx = r * cols + c, order = (idx * 131) % total;
      if (order >= n || honor.includes(idx)) continue;
      const sc = 0.2 + r * 0.004, x = x0 + c * dx + (r % 2) * dx / 2, y = rowTop + r * dy;
      s += miniFan(x, y + Math.sin(t * 7 + idx) * 1.5, sc, idx, false);
      k++;
    }
    // Ultra-Block (links): Fahnen schwenken
    for (let k = 0; k < 6; k++) {
      const fx = 90 + k * 52, fy = rowTop + 6 * dy + (k % 2) * 40, w = Math.sin(t * 6 + k) * 18;
      s += `<path d="M${fx} ${fy} V${fy - 70}" stroke="#3A2316" stroke-width="4"/>
        <path d="M${fx} ${fy - 70} q${30 + w * 0.3} ${-8 + w * 0.2} 60 ${w * 0.3} v32 q-30 ${8 - w * 0.2} -60 ${-w * 0.3}z" fill="${k % 2 ? '#FFD31A' : '#1F3FD8'}" stroke="#3A2316" stroke-width="3"/>`;
    }
    // Ultra-Banner an der Bruestung vorne
    s += `<rect x="40" y="${rowTop + rows * dy - 10}" width="430" height="100" fill="#3A2316"/>
      <image href="${ULTRA_FLAG}" x="46" y="${rowTop + rows * dy - 4}" width="418" height="88" preserveAspectRatio="none"/>`;
    // Ehrenplaetze: goldene Sitze, die drei ersten Fans
    honor.forEach((idx, i) => {
      const c = idx % cols, r = rows - 1, x = x0 + c * dx + (r % 2) * dx / 2, y = rowTop + r * dy;
      s += `<rect x="${x - 20}" y="${y + 2}" width="40" height="16" rx="4" fill="#FFD31A" stroke="#3A2316" stroke-width="3"/>`;
      s += place(fanFigure(Object.assign({blink: false}, FIRST_FANS[i].o), true), x, y + 16, 0.1);
    });
  }
  return s;
}
function standSeatPos(i) {
  const {x0, cols, dx, rowTop, rows, dy} = STAND, idx = (rows - 1) * cols + 11 + i, c = idx % cols, r = rows - 1;
  return [x0 + c * dx + (r % 2) * dx / 2, rowTop + r * dy];
}

// Ganzer Platz von der Seite (unter der Tribuene)
function wholePitch(t) {
  let s = sky(t) + `<rect x="-400" y="740" width="1880" height="1600" fill="#6B4A30"/>`;
  for (let i = 0; i < 18; i++) s += `<ellipse cx="${rnd(i + 40) * 1100}" cy="${800 + rnd(i + 50) * 900}" rx="${50 + rnd(i) * 80}" ry="${10 + rnd(i + 2) * 12}" fill="#4F8A3E" opacity=".8"/>`;
  s += `<g fill="none" stroke="#F0EDE0" stroke-width="7" opacity=".85"><path d="M60 780 L1020 780 L1080 1300 L0 1300 Z"/><path d="M540 780 V1300"/>
    <ellipse cx="540" cy="1020" rx="150" ry="70"/><path d="M60 880 L200 880 L205 1150 L30 1150"/><path d="M1020 880 L880 880 L875 1150 L1050 1150"/></g>`;
  s += goalPost(70, 1040, 0.55) + goalPost(1010, 1040, 0.55);
  [[260, 1180, 120, 22], [760, 1220, 160, 26], [480, 900, 110, 16]].forEach(p => { s += `<ellipse cx="${p[0]}" cy="${p[1]}" rx="${p[2]}" ry="${p[3]}" fill="#4A3828" stroke="#2C2018" stroke-width="5"/>`; });
  return s;
}

// Schwimmendes Tor in einem Schlammsee
// Tor steht auf seiner Torlinie (gx, gy) im Strafraum – der Strafraum ist ein Schlammsee, das Tor treibt langsam weg
function floatingGoal(t, gx, gy, sc) {
  const dx = t * 22, bob = Math.sin(t * 3) * 8 * sc, tilt = Math.sin(t * 2.2) * 4;
  let s = `<ellipse cx="${gx}" cy="${gy + 60 * sc}" rx="${300 * sc}" ry="${70 * sc}" fill="#4A3828" stroke="#2C2018" stroke-width="8"/>
    <ellipse cx="${gx - 120 * sc}" cy="${gy + 40 * sc}" rx="${170 * sc}" ry="${26 * sc}" fill="#7B8AA3" opacity=".3"/>`;
  s += `<g transform="translate(${dx} ${bob}) rotate(${tilt} ${gx} ${gy})">${goalPost(gx, gy + 8 * sc, 0.9 * sc / 0.9)}</g>`;
  s += `<path d="M${gx - 290 * sc} ${gy + 12 * sc} Q${gx} ${gy + 34 * sc} ${gx + 290 * sc} ${gy + 12 * sc} Q${gx + 270 * sc} ${gy + 110 * sc} ${gx} ${gy + 128 * sc} Q${gx - 270 * sc} ${gy + 110 * sc} ${gx - 290 * sc} ${gy + 12 * sc}Z" fill="#4A3828" opacity=".8"/>`;
  for (let k = 0; k < 4; k++) {
    const ph = (t * 0.9 + k / 4) % 1;
    s += `<ellipse cx="${gx + dx}" cy="${gy + 10 * sc + bob}" rx="${(170 + ph * 230) * sc}" ry="${(22 + ph * 40) * sc}" fill="none" stroke="#C9D3E3" stroke-width="4" opacity="${0.6 * (1 - ph)}"/>`;
  }
  return s;
}

// Schaukelstuhl mit Opa Juergen (sitzend, schaukelnd, Decke)
function rockingOpa(t) {
  const rock = Math.sin(t * 2.6) * 7;
  const id = 'op' + (UID++);
  const body = opa({blink: blinkAt(t, .3), mood: 'smile'});
  return `<g transform="rotate(${rock} 250 700)">
    <path d="M40 700 Q250 760 470 690" stroke="#6B4226" stroke-width="22" fill="none" stroke-linecap="round"/>
    <path d="M110 700 L140 560 M390 700 L360 560" stroke="#8A5A36" stroke-width="18"/>
    <rect x="96" y="250" width="40" height="330" rx="10" fill="#8A5A36" stroke="#3A2316" stroke-width="6" transform="rotate(-8 116 415)"/>
    <defs><clipPath id="${id}"><rect x="-200" y="-200" width="900" height="760"/></clipPath></defs>
    <g clip-path="url(#${id})">${body}</g>
    <rect x="130" y="540" width="250" height="40" rx="10" fill="#A8743F" stroke="#3A2316" stroke-width="7"/>
    <path d="M150 520 Q250 500 370 520 L380 640 Q250 660 140 640 Z" fill="#B83226" stroke="#3A2316" stroke-width="7"/>
    <path d="M180 520 V650 M230 512 V655 M280 512 V655 M330 516 V650 M144 560 H378 M146 600 H380" stroke="#FFD31A" stroke-width="5" opacity=".7"/>
    <rect x="190" y="640" width="40" height="46" fill="#1F3E66" stroke="#111" stroke-width="6"/><rect x="280" y="640" width="40" height="46" fill="#1F3E66" stroke="#111" stroke-width="6"/>
    <ellipse cx="206" cy="690" rx="32" ry="13" fill="#6B4226" stroke="#111" stroke-width="5"/><ellipse cx="296" cy="690" rx="32" ry="13" fill="#6B4226" stroke="#111" stroke-width="5"/>
  </g>
  <g transform="translate(460 600)"><rect x="-26" y="-30" width="52" height="60" rx="8" fill="#fff" stroke="#3A2316" stroke-width="6"/><path d="M26 -16 q22 0 22 16 q0 16 -22 16" stroke="#3A2316" stroke-width="6" fill="none"/>
    ${[0, 1].map(k => { const ph = (t * 0.8 + k * 0.5) % 1; return `<path d="M${-8 + k * 14} ${-40 - ph * 50} q8 -10 0 -20" stroke="#fff" stroke-width="5" fill="none" opacity="${1 - ph}"/>`; }).join('')}</g>`;
}

// Wappen der Konkurrenz (nachgezeichnet)
function ascheLogo(cx, cy, s) {
  return `<g transform="translate(${cx} ${cy}) scale(${s})">
    <defs><clipPath id="ash${UID}"><path d="M-160 -190 H160 V60 Q160 170 0 220 Q-160 170 -160 60Z"/></clipPath></defs>
    <path d="M-160 -190 H160 V60 Q160 170 0 220 Q-160 170 -160 60Z" fill="#F28A2E"/>
    <rect x="-55" y="-200" width="110" height="430" fill="#3A3A3A" clip-path="url(#ash${UID++})"/>
    <path d="M-160 -190 H160 V60 Q160 170 0 220 Q-160 170 -160 60Z" fill="none" stroke="#111" stroke-width="12"/>
    <text x="0" y="-110" text-anchor="middle" font-family="Inter" font-weight="900" font-size="54" fill="#fff">FC ASCHE</text>
    <circle cx="0" cy="10" r="62" fill="#fff" stroke="#111" stroke-width="9"/>
    <path d="M0 -18 L26 1 L16 30 L-16 30 L-26 1Z" fill="#3A3A3A"/>
    <text x="0" y="140" text-anchor="middle" font-family="Inter" font-weight="900" font-size="52" fill="#fff">2026</text></g>`;
}
function kuhLogo(cx, cy, s) {
  return `<g transform="translate(${cx} ${cy}) scale(${s})">
    <path d="M-160 -190 H160 V60 Q160 170 0 220 Q-160 170 -160 60Z" fill="#fff"/>
    <g fill="#2A2A3A"><ellipse cx="-90" cy="-110" rx="70" ry="55"/><ellipse cx="110" cy="-160" rx="50" ry="30"/><ellipse cx="110" cy="-10" rx="55" ry="70"/><ellipse cx="-40" cy="150" rx="60" ry="42"/></g>
    <path d="M-160 -190 H160 V60 Q160 170 0 220 Q-160 170 -160 60Z" fill="none" stroke="#111" stroke-width="12"/>
    <circle cx="0" cy="-20" r="80" fill="#FFD84A" stroke="#111" stroke-width="9"/>
    <text x="0" y="8" text-anchor="middle" font-family="Inter" font-weight="900" font-size="80" fill="#2A2A2A">SV</text></g>`;
}
function heuLogo(cx, cy, s) {
  return `<g transform="translate(${cx} ${cy}) scale(${s})">
      <path d="M-150 -170 H150 V30 Q150 150 0 200 Q-150 150 -150 30 Z" fill="#E8C24A" stroke="#3A2316" stroke-width="12"/>
      <path d="M-150 -170 H150 V-110 H-150 Z" fill="#6B8E23" stroke="#3A2316" stroke-width="8"/>
      <text x="0" y="-126" text-anchor="middle" ${FONT} font-size="40" fill="#fff">SC HEUBALLEN</text>
      <ellipse cx="0" cy="30" rx="105" ry="80" fill="#F2D06B" stroke="#3A2316" stroke-width="9"/>
      <ellipse cx="-55" cy="30" rx="30" ry="80" fill="#E0B84A" stroke="#3A2316" stroke-width="6"/>
      <path d="M-20 -40 Q30 -30 90 -10 M-15 0 Q40 10 100 20 M-15 50 Q40 60 95 70 M-20 90 Q30 98 80 100" stroke="#C99A2E" stroke-width="5" fill="none"/>
      <path d="M-55 -50 V110 M40 -48 V108" stroke="#B83226" stroke-width="7"/></g>`;
}

// Zeitungsartikel
function newspaper(t) {
  let lines = '';
  for (let i = 0; i < 9; i++) lines += `<rect x="${i % 2 ? 470 : 70}" y="${1040 + Math.floor(i / 2) * 34}" width="${330 - (i % 3) * 40}" height="14" rx="4" fill="#9C9284"/>`;
  return `<g>
    <rect x="58" y="300" width="964" height="1000" fill="#000" opacity=".35" transform="translate(12 16)"/>
    <rect x="58" y="300" width="964" height="1000" fill="#F2ECDD" stroke="#3A2316" stroke-width="8"/>
    <text x="540" y="400" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="78" fill="#1A1A1A">Kreisliga-Kurier</text>
    <path d="M90 425 H990 M90 437 H990" stroke="#1A1A1A" stroke-width="4"/>
    <text x="90" y="470" font-family="DejaVu Serif" font-size="26" fill="#444">Ausgabe Nr. 3 · Sport · 1,20 €</text>
    <text x="540" y="560" text-anchor="middle" ${FONT} font-size="74" fill="#1A1A1A">FC ASCHE SCHLÄGT</text>
    <text x="540" y="640" text-anchor="middle" ${FONT} font-size="74" fill="#1A1A1A">SV KUHWIESE!</text>
    <rect x="90" y="680" width="900" height="320" fill="#E2DACA" stroke="#3A2316" stroke-width="5"/>
    ${ascheLogo(260, 830, 0.62)}${kuhLogo(820, 830, 0.62)}
    <text x="540" y="880" text-anchor="middle" ${FONT} font-size="150" fill="#1A1A1A">1:0</text>
    ${lines}
    <text x="90" y="1260" font-family="DejaVu Serif" font-style="italic" font-size="28" fill="#555">„Der FC Schlammloch sollte sich warm anziehen.“</text></g>`;
}

function jerseyNum(cx, cy, s, sway, num, pos) {
  return jersey9(cx, cy, s, sway).replace('>9</text>', `>${num}</text>`).replace('>STURM</text>', `>${pos}</text>`);
}
