// Stufe 1 – Klassenzimmer, Mathearbeit. Er spielt heimlich unter dem Tisch ein Insel-Spiel, in dem Muscheln das Geld sind.
// Als alle Muscheln der Welt verschwinden, fällt sein Konto auf 0 – er springt auf und schreit „NEIN!“ mitten in die Totenstille.
// Die ganze Klasse dreht sich um, die Lehrerin kommt und kassiert das Handy.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {seat, unseat, addMouth, mouthOpen, brows} from './people.js';
import {makePhone, updateScreen} from './phone.js';
import {VANISH, SCREAM, TURN, TAKE} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export const COUNT0 = 4807;
// Kontostand im Spiel: sammelt langsam, fällt beim Verschwinden auf 0
export function balance(T) {
  if (T < VANISH) return COUNT0 + Math.floor(clamp((T - 4.2) / 5.2) * 5);
  return Math.round((COUNT0 + 5) * (1 - smooth(VANISH, VANISH + 0.55, T)));
}

// Bildschirm: Insel-Spiel (türkises Meer, runde Insel, Strohhütten, Muschel-Palast, Muscheln am Strand)
function drawGame(g, st, SW, SH) {
  const {t, T} = st; const gone = smooth(VANISH, VANISH + 0.35, T), red = smooth(VANISH + 0.3, VANISH + 0.5, T);
  const bg = g.createLinearGradient(0, 0, SW * 0.4, SH); bg.addColorStop(0, '#14b3c2'); bg.addColorStop(1, '#07547a'); g.fillStyle = bg; g.fillRect(0, 0, SW, SH);
  // Wellen
  g.strokeStyle = 'rgba(255,255,255,0.18)'; g.lineWidth = 3;
  for (let i = 0; i < 14; i++) { const y = 140 + i * 85 + 10 * Math.sin(t * 1.5 + i); g.beginPath(); for (let x = 0; x <= SW; x += 20) g.lineTo(x, y + 6 * Math.sin(x * 0.03 + t * 2 + i)); g.stroke(); }
  const cx = SW / 2, cy = 690, R = 250;
  g.fillStyle = 'rgba(255,255,255,0.35)'; g.beginPath(); g.arc(cx, cy, R + 26, 0, 7); g.fill();
  g.fillStyle = '#f3dca0'; g.beginPath(); g.arc(cx, cy, R, 0, 7); g.fill();
  g.fillStyle = '#8fd16a'; g.beginPath(); g.arc(cx, cy, R - 32, 0, 7); g.fill();
  g.save(); g.beginPath(); g.arc(cx, cy, R - 32, 0, 7); g.clip();
  g.fillStyle = '#ecd59a'; for (let k = -4; k <= 4; k++) { g.fillRect(cx + k * 52 - 4, cy - R, 8, 2 * R); g.fillRect(cx - R, cy + k * 52 - 4, 2 * R, 8); }
  // Strohhütten
  const r = rng(8);
  for (let i = -4; i < 4; i++) for (let j = -4; j < 4; j++) for (let q = 0; q < 2; q++) {
    const x = cx + i * 52 + 14 + q * 22, y = cy + j * 52 + 26; if (Math.hypot(x - cx, y - cy) > R - 46 || Math.hypot(x - cx, y - cy) < 70) continue;
    g.fillStyle = '#c98a4a'; g.fillRect(x - 7, y - 2, 14, 10);
    g.fillStyle = r() < 0.5 ? '#e8b94a' : '#f0c75a'; g.beginPath(); g.moveTo(x - 11, y); g.lineTo(x, y - 14); g.lineTo(x + 11, y); g.closePath(); g.fill();
    g.strokeStyle = '#2a1b12'; g.lineWidth = 1.5; g.stroke(); }
  g.restore();
  // Platz und Palast mit Fächermuschel-Dach (das Dach ist eine Muschel – verschwindet mit)
  g.fillStyle = '#f6e7c2'; g.beginPath(); g.arc(cx, cy, 64, 0, 7); g.fill(); g.strokeStyle = '#2a1b12'; g.lineWidth = 3; g.stroke();
  g.fillStyle = '#fff3df'; g.fillRect(cx - 44, cy - 6, 88, 34); g.strokeRect(cx - 44, cy - 6, 88, 34);
  g.fillStyle = '#e8467c'; for (const s of [-1, 1]) { g.fillRect(cx + s * 50 - 7, cy - 26, 14, 54); g.strokeRect(cx + s * 50 - 7, cy - 26, 14, 54); }
  if (gone < 1) { g.save(); g.globalAlpha = 1 - gone; g.translate(cx, cy - 6); g.scale(1 + gone * 0.4, 1 + gone * 0.4);
    g.fillStyle = '#ff9ec0'; g.beginPath(); g.moveTo(-40, 0); g.arc(0, 0, 40, Math.PI, 0); g.closePath(); g.fill(); g.stroke();
    g.strokeStyle = '#ffd23f'; g.lineWidth = 2.5; for (let k = 1; k < 8; k++) { const a = Math.PI + k * Math.PI / 8; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(a) * 38, Math.sin(a) * 38); g.stroke(); }
    g.restore(); }
  // Muscheln am Strand (Sammelobjekte)
  const rs = rng(5);
  for (let i = 0; i < 26; i++) { const a = rs() * 7, d = R - 16 + rs() * 8, x = cx + Math.cos(a) * d, y = cy + Math.sin(a) * d, c = ['#ff8fb1', '#ffd23f', '#fff3df', '#ffb38a'][i % 4];
    const s = 1 - gone; if (s <= 0) continue; g.save(); g.translate(x, y - Math.sin(gone * 3) * 20); g.scale(s, s); g.fillStyle = c; g.beginPath(); g.moveTo(-7, 3); g.arc(0, 3, 7, Math.PI, 0); g.closePath(); g.fill(); g.strokeStyle = '#2a1b12'; g.lineWidth = 1.5; g.stroke(); g.restore(); }
  // Puff-Wölkchen beim Verschwinden
  if (gone > 0 && gone < 1) { g.fillStyle = `rgba(255,255,255,${0.7 * (1 - gone)})`; for (let i = 0; i < 26; i++) { const a = rs() * 7, d = R - 12; g.beginPath(); g.arc(cx + Math.cos(a) * d, cy + Math.sin(a) * d - gone * 30, 6 + gone * 14, 0, 7); g.fill(); } }
  // +1-Muschel beim Sammeln
  for (const tc of [4.6, 5.9, 7.1, 8.2, 9.2]) { const u = (T - tc) / 0.9; if (u < 0 || u > 1) continue; g.save(); g.globalAlpha = 1 - u; g.font = 'bold 40px sans-serif'; g.textAlign = 'center'; g.fillStyle = '#ffd23f'; g.strokeStyle = '#2a1b12'; g.lineWidth = 6;
    g.strokeText('+1 🐚', cx + 150, 470 - u * 90); g.fillText('+1 🐚', cx + 150, 470 - u * 90); g.restore(); }
  // Logo-Badge oben links (klein)
  g.save(); g.translate(24, 92); g.rotate(-0.03); g.fillStyle = '#2a1b12'; g.beginPath(); g.roundRect(4, 6, 300, 64, 20); g.fill(); g.fillStyle = '#ffd23f'; g.beginPath(); g.roundRect(0, 0, 300, 64, 20); g.fill(); g.strokeStyle = '#2a1b12'; g.lineWidth = 4; g.stroke();
  g.font = '30px sans-serif'; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillText('🐚', 14, 34); g.fillStyle = '#2a1b12'; g.font = '900 28px sans-serif'; g.fillText('MUSCHEL-TAL', 54, 35); g.restore();
  // Kontostand oben rechts
  const n = balance(T), txt = '🐚 ' + n.toLocaleString('de-DE');
  g.save(); const sh = red > 0 && T < VANISH + 1.5 ? 6 * Math.sin(T * 70) * (1 - smooth(VANISH + 0.8, VANISH + 1.5, T)) : 0; g.translate(SW - 24 + sh, 92);
  g.font = '900 34px sans-serif'; const w = g.measureText(txt).width + 44;
  g.fillStyle = '#2a1b12'; g.beginPath(); g.roundRect(-w + 4, 6, w, 64, 32); g.fill();
  g.fillStyle = red > 0 ? `rgb(${lerp(255, 229, red)},${lerp(248, 38, red)},${lerp(231, 59, red)})` : '#fff8e7'; g.beginPath(); g.roundRect(-w, 0, w, 64, 32); g.fill(); g.strokeStyle = '#2a1b12'; g.lineWidth = 4; g.stroke();
  g.fillStyle = red > 0.5 ? '#fff' : '#2a1b12'; g.textAlign = 'right'; g.textBaseline = 'middle'; g.fillText(txt, -22, 35); g.restore();
  // Knöpfe unten
  g.save(); g.textBaseline = 'middle'; g.textAlign = 'center';
  for (const [x, w, c, l] of [[150, 230, '#e8467c', '🛍️ Shop'], [430, 250, '#fff8e7', '🏝️ Insel']]) { g.fillStyle = '#2a1b12'; g.beginPath(); g.roundRect(x - w / 2 + 3, 1152, w, 70, 35); g.fill(); g.fillStyle = c; g.beginPath(); g.roundRect(x - w / 2, 1146, w, 70, 35); g.fill(); g.strokeStyle = '#2a1b12'; g.lineWidth = 4; g.stroke();
    g.fillStyle = c === '#e8467c' ? '#fff' : '#2a1b12'; g.font = '800 32px sans-serif'; g.fillText(l, x, 1182); }
  g.restore();
  // Hinweis nach dem Verschwinden
  if (red > 0) { const a = red; g.save(); g.globalAlpha = a; g.fillStyle = 'rgba(42,27,18,0.55)'; g.fillRect(0, 0, SW, SH);
    g.fillStyle = '#fff8e7'; g.beginPath(); g.roundRect(60, 520, SW - 120, 300, 36); g.fill(); g.strokeStyle = '#2a1b12'; g.lineWidth = 5; g.stroke();
    g.fillStyle = '#e8467c'; g.textAlign = 'center'; g.font = '900 120px sans-serif'; g.fillText('0 🐚', SW / 2, 680);
    g.fillStyle = '#2a1b12'; g.font = '800 34px sans-serif'; g.fillText('Alle Muscheln weg?!', SW / 2, 765); g.restore(); }
  // Statusleiste
  g.fillStyle = '#fff'; g.font = '500 24px sans-serif'; g.textAlign = 'left'; g.textBaseline = 'alphabetic'; g.fillText('10:14', 40, 50); g.textAlign = 'right'; g.fillText('5G  61%', SW - 40, 50);
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.55;
  scene.background = new THREE.Color('#dfe6ea');
  scene.add(new THREE.HemisphereLight('#f4f7ff', '#8a7a66', 1.1));
  const sun = new THREE.DirectionalLight('#fff2dc', 2.6); sun.position.set(-8, 6, 1); sun.target.position.set(0, 0, -0.5); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 25}); scene.add(sun, sun.target);
  const fill = new THREE.PointLight('#fff6ea', 6, 12, 1.4); fill.position.set(1.5, 2.8, 1.5); scene.add(fill);

  // Raum: x -4..4, z -5.4..4.4, Höhe 3.2. Tafel vorn (z = -5.4), Fenster links (x = -4)
  const floorT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#b9a98f'; g.fillRect(0, 0, w, h); const r = rng(4); for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(${90 + r() * 40},${80 + r() * 30},${60 + r() * 30},0.12)`; g.fillRect(r() * w, r() * h, 2 + r() * 6, 2 + r() * 6); }
    g.strokeStyle = 'rgba(0,0,0,0.12)'; for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * 128, 0); g.lineTo(i * 128, h); g.moveTo(0, i * 128); g.lineTo(w, i * 128); g.stroke(); } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(4, 5);
  mesh(new THREE.PlaneGeometry(8, 10), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.6}), 0, 0, -0.5, scene).rotation.x = -Math.PI / 2;
  const wallM = mat('#eef0e4', {roughness: 0.95}), wallLow = mat('#9fb8a8', {roughness: 0.9});
  mesh(new THREE.BoxGeometry(8, 3.2, 0.1), wallM, 0, 1.6, -5.45, scene);
  mesh(new THREE.BoxGeometry(8, 3.2, 0.1), wallM, 0, 1.6, 4.45, scene);
  mesh(new THREE.BoxGeometry(0.1, 3.2, 10), wallM, 4.05, 1.6, -0.5, scene);
  mesh(new THREE.BoxGeometry(8, 0.1, 10), mat('#f4f4f0'), 0, 3.25, -0.5, scene);
  for (const [x, z, w, d] of [[0, -5.38, 8, 0.02], [0, 4.38, 8, 0.02], [3.98, -0.5, 0.02, 10]]) mesh(new THREE.BoxGeometry(w, 1.0, d), wallLow, x, 0.5, z, scene);
  // Fensterwand links: Brüstung, Pfeiler, Sturz, Himmel/Bäume draußen
  mesh(new THREE.BoxGeometry(0.1, 0.9, 10), wallLow, -4.05, 0.45, -0.5, scene); mesh(new THREE.BoxGeometry(0.1, 0.5, 10), wallM, -4.05, 2.95, -0.5, scene);
  for (let z = -5.2; z <= 4.3; z += 2.35) mesh(new THREE.BoxGeometry(0.14, 1.8, 0.25), wallM, -4.05, 1.8, z, scene);
  const outT = canvasTex(1024, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#9cc7ef'); gr.addColorStop(1, '#e7f1f8'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(9); for (let i = 0; i < 40; i++) { g.fillStyle = `rgb(${60 + r() * 40},${120 + r() * 50},${60 + r() * 30})`; g.beginPath(); g.arc(r() * w, h * 0.75 + r() * 60, 30 + r() * 50, 0, 7); g.fill(); } });
  mesh(new THREE.PlaneGeometry(10, 2.4), new THREE.MeshBasicMaterial({map: outT}), -4.6, 1.8, -0.5, scene).rotation.y = Math.PI / 2;
  // Tafel mit Aufgaben
  const boardT = canvasTex(2048, 640, (g, w, h) => { g.fillStyle = '#2f4a3c'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(255,255,255,0.06)'; for (let i = 0; i < 60; i++) g.fillRect(Math.random() * w, Math.random() * h, 200, 30);
    g.fillStyle = 'rgba(245,245,235,0.92)'; g.font = 'italic 70px Garamond'; g.fillText('Klassenarbeit Nr. 2 – Mathe', 90, 120);
    g.font = '60px Garamond'; g.fillText('1)  f(x) = 3x² − 12x + 9   Nullstellen?', 90, 260); g.fillText('2)  Löse:  4(x − 2) = 2x + 6', 90, 370); g.fillText('3)  Bestimme den Scheitelpunkt.', 90, 480);
    g.font = 'italic 52px Garamond'; g.fillText('Handys aus!', 1600, 600); });
  mesh(new THREE.BoxGeometry(4.4, 1.38, 0.05), mat('#6b5a44'), 0, 1.75, -5.38, scene);
  mesh(new THREE.PlaneGeometry(4.3, 1.3), new THREE.MeshStandardMaterial({map: boardT, roughness: 0.9}), 0, 1.75, -5.35, scene);
  // Uhr
  const clockT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#fff'; g.beginPath(); g.arc(128, 128, 120, 0, 7); g.fill(); g.strokeStyle = '#222'; g.lineWidth = 10; g.stroke();
    for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; g.lineWidth = 6; g.beginPath(); g.moveTo(128 + Math.cos(a) * 95, 128 + Math.sin(a) * 95); g.lineTo(128 + Math.cos(a) * 110, 128 + Math.sin(a) * 110); g.stroke(); }
    g.lineWidth = 8; g.beginPath(); g.moveTo(128, 128); g.lineTo(128 + 50 * Math.cos(-2.6), 128 + 50 * Math.sin(-2.6)); g.stroke(); g.lineWidth = 5; g.beginPath(); g.moveTo(128, 128); g.lineTo(128 + 80 * Math.cos(-0.5), 128 + 80 * Math.sin(-0.5)); g.stroke(); });
  mesh(new THREE.CircleGeometry(0.2, 32), new THREE.MeshStandardMaterial({map: clockT, roughness: 0.5}), 2.9, 2.6, -5.38, scene);
  // Lehrerpult
  const deskWood = mat('#c9a978', {roughness: 0.6}), steel = mat('#5d6670', {metalness: 0.6, roughness: 0.45});
  const pult = new THREE.Group(); pult.position.set(1.8, 0, -4.3); scene.add(pult);
  mesh(new THREE.BoxGeometry(1.5, 0.05, 0.75), deskWood, 0, 0.76, 0, pult); mesh(new THREE.BoxGeometry(1.5, 0.6, 0.04), mat('#8a9aa8'), 0, 0.42, 0.3, pult);
  for (const x of [-0.7, 0.7]) mesh(new THREE.BoxGeometry(0.05, 0.74, 0.7), steel, x, 0.37, 0, pult);
  mesh(new THREE.BoxGeometry(0.25, 0.08, 0.32), mat('#e6e1d4'), -0.3, 0.82, 0, pult);

  // Schülertische (Zweiertische) und Schüler
  const sheetT = canvasTex(256, 360, (g, w, h) => { g.fillStyle = '#fbfaf5'; g.fillRect(0, 0, w, h); g.fillStyle = '#9aa'; for (let y = 40; y < h; y += 18) g.fillRect(16, y, w - 32, 1); g.fillStyle = '#2a3a6a'; g.font = '16px sans-serif'; for (let y = 60; y < 240; y += 36) g.fillText('x = ' + (y % 7) + ',5  …', 22, y); });
  const sheetM = new THREE.MeshStandardMaterial({map: sheetT, roughness: 0.9});
  const COLS = [-2.35, 0, 2.35], ROWS = [-2.6, -1.15, 0.3, 1.75];
  const students = []; const r = rng(31);
  const GX = -0.33, GZ = 0.3; // er: linker Platz am mittleren Tisch, dritte Reihe
  for (const zc of ROWS) for (const xc of COLS) {
    const t = new THREE.Group(); t.position.set(xc, 0, zc - 0.5); scene.add(t);
    mesh(new THREE.BoxGeometry(1.3, 0.04, 0.55), deskWood, 0, 0.74, 0, t);
    for (const x of [-0.6, 0.6]) { mesh(new THREE.BoxGeometry(0.04, 0.72, 0.04), steel, x, 0.36, 0.22, t); mesh(new THREE.BoxGeometry(0.04, 0.72, 0.04), steel, x, 0.36, -0.22, t); }
    for (const s of [-1, 1]) {
      const sx = xc + s * 0.33;
      const ch = new THREE.Group(); ch.position.set(sx, 0, zc + 0.05); scene.add(ch);
      mesh(new THREE.BoxGeometry(0.42, 0.03, 0.4), deskWood, 0, 0.45, 0, ch); mesh(new THREE.BoxGeometry(0.42, 0.32, 0.03), deskWood, 0, 0.78, 0.2, ch);
      for (const [x, z] of [[-0.18, -0.17], [0.18, -0.17], [-0.18, 0.17], [0.18, 0.17]]) mesh(new THREE.BoxGeometry(0.025, 0.45, 0.025), steel, x, 0.225, z, ch);
      mesh(new THREE.PlaneGeometry(0.21, 0.3), sheetM, s * 0.33, 0.762, 0.05, t).rotation.x = -Math.PI / 2;
      const isHim = Math.abs(sx - GX) < 0.01 && zc === GZ;
      if (isHim) continue;
      const p = makePerson(400 + students.length * 7, {height: 0.95 + r() * 0.08, longHair: r() < 0.45, ponytail: r() < 0.2}); addMouth(p); scene.add(p);
      students.push({p, x: sx, z: zc, ph: r() * 6, side: Math.sign(GX - sx) || 1, dz: GZ - zc});
    }
  }
  // Er (gleicher Look wie später im Zimmer, ohne Headset)
  const guy = makePerson(1101, {skin: '#e2b28c', top: '#ff7a3d', pants: '#22262e', hair: '#2a1d15', height: 1.0}); addMouth(guy); scene.add(guy);
  const phone = makePhone(); scene.add(phone); phone.userData.caseM.color.set('#e8467c'); Object.assign(phone.userData.scr.material, {color: new THREE.Color('#000'), clearcoat: 0.15, roughness: 0.35, envMapIntensity: 0.15, emissiveIntensity: 1.0});
  // Lehrerin (Brille, Strickjacke)
  const tea = makePerson(2207, {skin: '#f0c7a8', top: '#7a8f6a', pants: '#3a3f4a', hair: '#8a6a4a', height: 1.06, longHair: true}); addMouth(tea); scene.add(tea);
  for (const s of [-1, 1]) mesh(new THREE.TorusGeometry(0.026, 0.005, 6, 16), mat('#222'), s * 0.042, 0.08, 0.112, tea.userData.head);
  mesh(new THREE.BoxGeometry(0.03, 0.005, 0.005), mat('#222'), 0, 0.08, 0.115, tea.userData.head);

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 60); scene.add(camera);
  const hand = (p, side) => { p.updateMatrixWorld(true); const a = side < 0 ? p.userData.armL : p.userData.armR; return a.userData.fore.localToWorld(V3(0, -0.29, 0.0)); };

  return {scene, camera, update(shot, T) {
    // ---- Klasse: schreiben, dann zu ihm umdrehen ----
    const turn = smooth(TURN, TURN + 0.5, T);
    students.forEach((s, i) => { const p = s.p, u = p.userData;
      seat(p, 0.47); p.position.x = s.x; p.position.z = s.z + 0.05; p.rotation.set(0, Math.PI, 0);
      const wr = Math.sin(T * 7 + s.ph) * 0.06 * (1 - turn);
      u.armR.rotation.set(-0.95 + wr, 0, 0.1); u.armR.userData.fore.rotation.x = -0.75; u.armL.rotation.set(-0.85, 0, -0.15); u.armL.userData.fore.rotation.x = -0.9;
      u.head.rotation.set(0.42 * (1 - turn), 0, 0); u.torso.rotation.set(0.12 * (1 - turn), 0, 0);
      // umdrehen: nach links/rechts/hinten, je nachdem wo er sitzt
      const k = turn * smooth(0, 1, (T - TURN - (i % 5) * 0.05) * 3 + 0.0);
      const ang = Math.atan2(-(GX - s.x), -(GZ - s.z)); // Drehwinkel (Figur ist um π gedreht)
      u.torso.rotation.y = clamp(ang * 0.55, -1.2, 1.2) * k; u.head.rotation.y = clamp(ang * 0.45, -1.0, 1.0) * k; u.head.rotation.x -= 0.1 * k;
      mouthOpen(p, 0.55 * k); brows(p, k, 0);
      if (i % 3 === 0) { u.armL.rotation.x = lerp(u.armL.rotation.x, -1.9, k); u.armL.userData.fore.rotation.x = lerp(-0.9, -2.2, k); } // Hand vor den Mund
    });
    // ---- Er ----
    const g = guy, u = g.userData;
    const up = smooth(SCREAM - 0.05, SCREAM + 0.25, T), down = smooth(TAKE + 0.8, TAKE + 1.4, T);
    if (up <= 0 || down >= 1) {
      seat(g, 0.47); g.position.set(GX, g.position.y, GZ + 0.05); g.rotation.set(0, Math.PI, 0);
      // Hände im Schoß, Handy halten; Kopf runter
      u.armL.rotation.set(-0.3, 0, -0.28); u.armL.userData.fore.rotation.x = -1.15; u.armR.rotation.set(-0.3, 0, 0.28); u.armR.userData.fore.rotation.x = -1.15;
      u.head.rotation.set(0.62, 0, 0); u.torso.rotation.set(0.18, 0, 0); mouthOpen(g, 0); brows(g, 0, 0);
      if (T > VANISH && T < SCREAM) { brows(g, smooth(VANISH + 0.2, VANISH + 0.5, T), 0); mouthOpen(g, 0.4 * smooth(VANISH + 0.3, VANISH + 0.7, T)); u.torso.rotation.x = 0.18 + 0.03 * Math.sin(T * 40); }
      if (down >= 1) { u.head.rotation.set(0.75, 0, 0); u.torso.rotation.set(0.35, 0, 0); u.armL.rotation.set(-0.2, 0, -0.1); u.armR.rotation.set(-0.2, 0, 0.1); u.armL.userData.fore.rotation.x = -0.3; u.armR.userData.fore.rotation.x = -0.3; brows(g, 0.8, 0); mouthOpen(g, 0.1); }
    } else {
      // aufspringen, Arme hoch, schreien
      unseat(g); posePerson(g, {}); g.position.set(GX, 0.0 + 0.12 * Math.sin(clamp((T - SCREAM) / 0.35) * Math.PI) * (T < SCREAM + 0.4 ? 1 : 0), GZ + 0.25); g.rotation.set(0, Math.PI, 0);
      const sc = T < TURN + 0.6 ? 1 : 1 - smooth(TURN + 0.6, TURN + 1.2, T);
      u.armL.rotation.z = -2.5 * up * sc - 0.1; u.armR.rotation.z = 2.5 * up * sc + 0.1; u.armL.userData.fore.rotation.x = -0.3; u.armR.userData.fore.rotation.x = -0.3;
      u.head.rotation.x = -0.35 * up * sc; mouthOpen(g, sc > 0.5 ? 0.9 + 0.1 * Math.sin(T * 30) : 0.35); brows(g, 1, 0);
      // erstarrt; dann Handy abgeben
      const give = smooth(TAKE - 0.5, TAKE, T);
      if (sc < 1) { u.armR.rotation.x = -1.1 * give; u.armR.rotation.z = lerp(0.3, -0.1, give); u.armR.userData.fore.rotation.x = -0.4 * give; u.armL.rotation.z = -0.15; u.head.rotation.x = 0.25 * (1 - sc) + 0.15 * give; u.head.rotation.y = -0.5 * give; }
      if (T > TAKE) { u.armR.rotation.x = lerp(-1.1, -0.1, smooth(TAKE + 0.1, TAKE + 0.6, T)); }
      // Hinsetzen
      if (down > 0) { g.position.y -= 0.0; }
    }
    // ---- Lehrerin ----
    const tu = tea.userData; const W0 = V3(1.3, 0, -4.4), W1 = V3(-1.17, 0, -4.0), W2 = V3(-1.17, 0, GZ - 0.05);
    const walk = clamp((T - (TURN + 0.9)) / 1.6), p1 = clamp(walk / 0.3), p2 = clamp((walk - 0.3) / 0.7);
    if (T < TURN + 0.9) { tea.position.copy(W0); posePerson(tea, {}); tea.rotation.set(0, 0, 0); tu.armL.rotation.set(-0.6, 0, -0.5); tu.armR.rotation.set(-0.6, 0, 0.5); tu.armL.userData.fore.rotation.x = -1.7; tu.armR.userData.fore.rotation.x = -1.7; // Arme verschränkt
      tu.head.rotation.y = 0.25 * Math.sin(T * 0.6); const look = smooth(SCREAM + 0.2, TURN + 0.3, T); tu.head.rotation.y = lerp(tu.head.rotation.y, -0.45, look); brows(tea, 0, look); }
    else if (walk < 1) { const pos = walk < 0.3 ? V3().lerpVectors(W0, W1, easeOut(p1)) : V3().lerpVectors(W1, W2, p2); tea.position.copy(pos);
      posePerson(tea, {walk: T * 9, walkAmp: 0.9}); tea.rotation.set(0, walk < 0.3 ? -1.41 : 0, 0); brows(tea, 0, 1); }
    else { tea.position.copy(W2); posePerson(tea, {}); tea.rotation.set(0, 1.17, 0); brows(tea, 0, 1);
      const hold = smooth(TURN + 2.6, TURN + 3.0, T); tu.armR.rotation.x = -1.3 * hold; tu.armR.userData.fore.rotation.x = -0.2; tu.armR.rotation.z = 0.2;
      const pocket = smooth(TAKE + 0.5, TAKE + 1.1, T); tu.armR.rotation.x = lerp(tu.armR.rotation.x, -0.3, pocket); tu.head.rotation.x = 0.15; }
    // ---- Handy ----
    let ph;
    if (T < SCREAM) { ph = V3(GX + 0.01, 0.66 + 0.005 * Math.sin(T * 1.3), GZ - 0.13); phone.position.copy(ph); phone.rotation.set(-1.2, 0, 0.04 * Math.sin(T * 0.9)); }
    else if (T < TAKE) { ph = hand(guy, 1); phone.position.copy(ph).add(V3(0, 0.06, 0)); phone.rotation.set(-0.2, Math.PI, 0.3); }
    else { ph = hand(tea, 1); phone.position.copy(ph).add(V3(0, 0.05, 0)); phone.rotation.set(-0.3, -Math.PI / 2, 0); }
    updateScreen(phone, [], {t: T, T, custom: drawGame, noDrops: true});

    // ---- Kamera ----
    camera.fov = 50; let pos, tgt; u.torso.visible = true; camera.up.set(0, 1, 0);
    if (shot.id === 'intro') { const k = smooth(0, 3.5, T); pos = V3(lerp(3.3, 3.0, k), lerp(2.65, 2.5, k), lerp(-4.9, -4.5, k)); tgt = V3(-0.6, 0.85, 0.6); }
    else if (shot.id === 'wait' || T < VANISH + 1.0) { // aus seinen Augen aufs Handy (sein Kopf ist dafür ausgeblendet)
      const k = smooth(3.5, 9.6, T); const c = phone.position; guy.updateMatrixWorld(true);
      const eye = u.head.localToWorld(V3(0, 0.08, 0.06)); pos = V3().lerpVectors(eye, c, lerp(0.3, 0.55, k)); tgt = c.clone().add(V3(0, 0, -0.01)); camera.fov = lerp(52, 42, k); camera.up.set(0, 0.3, -1).normalize();
      if (shot.id === 'wait' && T < 5.2) { const e = 1 - smooth(3.5, 5.2, T); pos.add(V3(0.25 * e, 0.2 * e, 0.25 * e)); }
      if (T > VANISH) { const s = 0.004 * Math.sin(T * 60) * smooth(VANISH + 0.3, VANISH + 0.5, T); pos.x += s; }
      u.torso.visible = false;
    }
    else if (T < TURN) { // frontal: er springt auf
      pos = V3(GX + 0.1, 1.62, GZ - 1.35); tgt = V3(GX, 1.45, GZ + 0.25); const z = smooth(SCREAM + 0.15, SCREAM + 0.3, T); camera.fov = 42 - 18 * z;
      tgt.y = lerp(1.3, 1.62, z); pos.add(V3(noise1(T * 9, 2) * 0.01 * z, noise1(T * 9, 5) * 0.01 * z, 0)); }
    else if (T < TURN + 1.6) { // weit von vorn: alle drehen sich um
      const k = smooth(TURN, TURN + 1.6, T); pos = V3(lerp(1.9, 1.7, k), 1.75, -4.7 + 0.2 * k); tgt = V3(-0.4, 1.05, 0.1); camera.fov = lerp(48, 40, k); }
    else { // seitlich: Lehrerin kommt und kassiert das Handy
      const k = smooth(TURN + 1.6, 17, T); pos = V3(1.17, lerp(1.72, 1.66, k), lerp(-0.95, -0.8, k)); tgt = V3(lerp(-0.8, -0.72, k), 1.38, GZ + 0.3); camera.fov = lerp(46, 40, k); }
    camera.position.copy(pos); camera.lookAt(tgt); camera.updateProjectionMatrix();
  }};
}
