// Klassenzimmer, Mittag, Mathearbeit. Um 12:00 verschwindet die Mathe: Tafel, Uhr und Taschenrechner zeigen Unsinn, die Klasse jubelt.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, easeOut} from './lib.js';
import {makePhone, makeHands, updateScreen} from './phone.js';
import {VANISH} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const RW = 4.6, ZB = -4.4, ZF = 6.5, RH = 3.2; // Raum: x ±RW, Tafelwand bei ZB, Rückwand bei ZF
const JUMP = VANISH + 1.0;                     // Klasse springt auf
const THROW = VANISH + 1.6;                    // Blätter fliegen

// Zufallszeichen für den Glitch
const GL = '0123456789+−×÷=∞√∑∫πΔ≠≈%#?!§&@'.split('');
function scramble(txt, k, r) { return txt.split('').map(c => (c !== ' ' && r() < k) ? GL[Math.floor(r() * GL.length)] : c).join(''); }

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#cfe3f5');
  // Licht: Mittagssonne durch die Fenster links, Neonröhren, Himmelslicht
  scene.add(new THREE.HemisphereLight('#eaf2ff', '#8a7a64', 0.9));
  const sun = new THREE.DirectionalLight('#fff3dc', 3.2); sun.position.set(-14, 9, 3); sun.target.position.set(0, 0, 0);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 40}); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
  scene.add(sun, sun.target);
  for (const [x, z] of [[-1.5, -1], [1.5, -1], [-1.5, 3], [1.5, 3]]) { const l = new THREE.PointLight('#f4f8ff', 2.2, 9, 1.6); l.position.set(x, RH - 0.9, z); scene.add(l); }

  // Raum
  const floorT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#9c8f7a'; g.fillRect(0, 0, w, h); const r = rng(4);
    for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '60,50,40' : '230,220,200'},${r() * 0.07})`; g.fillRect(r() * w, r() * h, 2 + r() * 6, 2 + r() * 6); }
    g.strokeStyle = 'rgba(70,60,50,0.25)'; g.lineWidth = 2; for (let x = 0; x <= w; x += 128) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); g.beginPath(); g.moveTo(0, x); g.lineTo(w, x); g.stroke(); } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(5, 6);
  const floor = mesh(new THREE.PlaneGeometry(RW * 2, ZF - ZB), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.45}), 0, 0, (ZB + ZF) / 2, scene); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
  const wallM = mat('#e9e3d3', {roughness: 0.9}), lowM = mat('#c9b99a', {roughness: 0.8});
  const ceil = mesh(new THREE.PlaneGeometry(RW * 2, ZF - ZB), mat('#f2f0ea'), 0, RH, (ZB + ZF) / 2, scene); ceil.rotation.x = Math.PI / 2;
  mesh(new THREE.BoxGeometry(RW * 2, RH, 0.2), wallM, 0, RH / 2, ZB - 0.1, scene).receiveShadow = true;
  mesh(new THREE.BoxGeometry(RW * 2, RH, 0.2), wallM, 0, RH / 2, ZF + 0.1, scene);
  mesh(new THREE.BoxGeometry(0.2, RH, ZF - ZB), wallM, RW + 0.1, RH / 2, (ZB + ZF) / 2, scene).receiveShadow = true;
  mesh(new THREE.BoxGeometry(0.02, 1.0, ZF - ZB), lowM, RW - 0.01, 0.5, (ZB + ZF) / 2, scene); // Lackanstrich unten
  // Fensterwand links mit drei großen Fenstern (Wandstücke werfen Schatten)
  const winZ = [[-3.4, -1.2], [-0.4, 1.8], [2.6, 4.8]];
  const wl = (y0, y1, z0, z1) => { const m = mesh(new THREE.BoxGeometry(0.25, y1 - y0, z1 - z0), wallM, -RW - 0.12, (y0 + y1) / 2, (z0 + z1) / 2, scene); m.castShadow = true; m.receiveShadow = true; };
  wl(0, 0.9, ZB, ZF); wl(2.75, RH, ZB, ZF); let zp = ZB; for (const [a, b] of winZ) { wl(0.9, 2.75, zp, a); zp = b; } wl(0.9, 2.75, zp, ZF);
  const frameM = mat('#f4f4f2', {roughness: 0.5});
  for (const [a, b] of winZ) { for (const z of [a, (a + b) / 2, b]) mesh(new THREE.BoxGeometry(0.12, 1.85, 0.07), frameM, -RW, 1.825, z, scene).castShadow = true;
    mesh(new THREE.BoxGeometry(0.12, 0.07, b - a), frameM, -RW, 1.9, (a + b) / 2, scene).castShadow = true;
    mesh(new THREE.BoxGeometry(0.3, 0.05, b - a + 0.1), frameM, -RW + 0.1, 0.92, (a + b) / 2, scene); }
  // Lichtstrahlen (Staub in der Luft)
  const beamM = new THREE.MeshBasicMaterial({color: '#fff2d0', transparent: true, opacity: 0.05, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide});
  const sd = V3(14, -9, -3).normalize(), beams = [];
  for (const [a, b] of winZ) for (let k = 0; k < 3; k++) { const L = 7; const bm = mesh(new THREE.BoxGeometry(L, 1.6, (b - a) / 3 - 0.08), beamM, 0, 0, 0, scene);
    const c = V3(-RW, 1.85, a + (k + 0.5) * (b - a) / 3).addScaledVector(sd, L / 2); bm.position.copy(c); bm.quaternion.setFromUnitVectors(V3(1, 0, 0), sd); beams.push(bm); }
  // draußen: Himmel, Bäume, Nachbarschule
  const out = canvasTex(1024, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#7fb2e8'); gr.addColorStop(0.7, '#d5e7f6'); gr.addColorStop(1, '#e8eef0');
    g.fillStyle = gr; g.fillRect(0, 0, w, h); g.fillStyle = '#c9b8a0'; g.fillRect(120, 300, 420, 212); g.fillStyle = '#8fa7bf'; for (let x = 140; x < 520; x += 60) for (let y = 320; y < 500; y += 55) g.fillRect(x, y, 34, 30);
    const r = rng(8); for (let i = 0; i < 26; i++) { const x = r() * w, y = 300 + r() * 120, s = 40 + r() * 90; g.fillStyle = `rgb(${50 + r() * 30},${100 + r() * 50},${40 + r() * 30})`; g.beginPath(); g.arc(x, y, s, 0, 7); g.fill(); }
    g.fillStyle = '#5d7d3f'; g.fillRect(0, 440, w, 72); });
  const outM = new THREE.MeshBasicMaterial({map: out, fog: false}); const op = mesh(new THREE.PlaneGeometry(40, 20), outM, -RW - 8, 3, 1, scene); op.rotation.y = Math.PI / 2;

  // Tafel (Canvas, wird jedes Bild neu gezeichnet)
  const BC = document.createElement('canvas'); BC.width = 2048; BC.height = 768; const bt = new THREE.CanvasTexture(BC); bt.colorSpace = THREE.SRGBColorSpace; bt.anisotropy = 8;
  const board = mesh(new THREE.PlaneGeometry(5.2, 1.95), new THREE.MeshStandardMaterial({map: bt, roughness: 0.85}), -0.2, 1.75, ZB + 0.03, scene);
  mesh(new THREE.BoxGeometry(5.4, 2.12, 0.04), mat('#6b5843', {roughness: 0.6}), -0.2, 1.75, ZB + 0.005, scene);
  mesh(new THREE.BoxGeometry(5.3, 0.05, 0.12), mat('#7a6650'), -0.2, 0.75, ZB + 0.08, scene);
  for (const x of [-1.4, -1.1, 0.8]) mesh(new THREE.BoxGeometry(0.08, 0.015, 0.015), mat('#fafafa'), x, 0.785, ZB + 0.08, scene);
  const boardLines = [[0.06, 0.18, 'Mathearbeit · Klasse 9b', 78], [0.06, 0.36, 'x² − 5x + 6 = 0', 92], [0.06, 0.52, 'x₁ = 2   x₂ = 3', 84], [0.06, 0.72, 'a² + b² = c²', 92], [0.06, 0.9, 'sin 30° = 0,5', 80],
    [0.56, 0.36, 'f(x) = 2x + 3', 92], [0.56, 0.54, 'f(4) = 11', 84], [0.56, 0.74, 'π ≈ 3,14159', 92], [0.56, 0.9, '1 + 1 = 2', 92]];
  function drawBoard(T) {
    const g = BC.getContext('2d'), w = BC.width, h = BC.height;
    g.fillStyle = '#25392f'; g.fillRect(0, 0, w, h);
    const r0 = rng(5); for (let i = 0; i < 90; i++) { g.fillStyle = `rgba(255,255,255,${0.02 + r0() * 0.04})`; g.beginPath(); g.ellipse(r0() * w, r0() * h, 60 + r0() * 200, 20 + r0() * 50, r0(), 0, 7); g.fill(); } // Wischspuren
    const k = T < VANISH ? 0 : clamp(0.35 + (T - VANISH) * 0.25, 0, 0.95), r = rng(Math.floor(T * 12) * 7 + 1);
    // Lehrer schreibt die letzte Zeile während der Wartezeit
    boardLines.forEach(([x, y, txt, s], i) => {
      let t = txt; if (i === boardLines.length - 1 && T < VANISH) t = txt.slice(0, Math.max(0, Math.floor((T - 4) * 3)));
      if (k > 0) t = scramble(txt, k, r);
      g.save(); g.font = `italic 400 ${s}px Garamond`; g.fillStyle = 'rgba(245,245,238,0.93)';
      const dx = k > 0 ? (r() - 0.5) * 30 * k : 0, dy = k > 0 ? (r() - 0.5) * 24 * k : 0;
      g.translate(x * w + dx, y * h + dy); if (k > 0) g.rotate((r() - 0.5) * 0.15 * k);
      g.fillText(t, 0, 0); g.restore();
    });
    if (k > 0) { // neue, falsche Rechnungen tauchen auf
      g.font = 'italic 400 120px Garamond'; g.fillStyle = 'rgba(255,240,200,0.95)';
      if (T > VANISH + 0.6) g.fillText(`1 + 1 = ${GL[Math.floor(r() * 10)]}${r() < 0.5 ? GL[Math.floor(r() * GL.length)] : ''}`, 0.56 * w + (r() - 0.5) * 20, 0.9 * h);
      if (T > VANISH + 2) { g.font = 'italic 400 100px Garamond'; g.fillText('2 + 2 = ' + ['∞', '7', '−0', '?', '22', '√π'][Math.floor(r() * 6)], 0.3 * w, 0.62 * h); }
    }
    bt.needsUpdate = true;
  }
  // Wanduhr über der Tafel: 11:59:51 am Anfang, 12:00:00 bei VANISH, danach drehen die Zeiger durch
  const clock = new THREE.Group(); clock.position.set(3.4, 2.55, ZB + 0.05); scene.add(clock);
  mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.05, 40), mat('#f7f7f4'), 0, 0, 0, clock).rotation.x = Math.PI / 2;
  mesh(new THREE.TorusGeometry(0.24, 0.022, 8, 40), mat('#222'), 0, 0, 0.02, clock);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; mesh(new THREE.BoxGeometry(0.015, i % 3 ? 0.03 : 0.05, 0.005), mat('#111'), Math.sin(a) * 0.2, Math.cos(a) * 0.2, 0.03, clock).rotation.z = -a; }
  const hand = (len, wdt, col) => { const p = new THREE.Group(); p.position.z = 0.035; clock.add(p); mesh(new THREE.BoxGeometry(wdt, len, 0.006), mat(col), 0, len / 2 - 0.02, 0, p); return p; };
  const hH = hand(0.12, 0.022, '#111'), hM = hand(0.18, 0.014, '#111'), hS = hand(0.2, 0.006, '#c8102e');
  // Tische, Stühle, Schüler
  const deskM = mat('#d8c39a', {roughness: 0.55}), legM = mat('#4b5563', {metalness: 0.6, roughness: 0.4}), chairM = mat('#2f6aa5', {roughness: 0.6});
  const sheetT = canvasTex(256, 360, (g, w, h) => { g.fillStyle = '#fbfbf7'; g.fillRect(0, 0, w, h); g.fillStyle = '#222'; g.font = '600 20px Plex'; g.fillText('Mathearbeit', 20, 34);
    g.strokeStyle = 'rgba(80,120,200,0.35)'; for (let y = 60; y < h; y += 14) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
    g.fillStyle = '#1d3d8f'; g.font = 'italic 16px Garamond'; const r = rng(2); for (let y = 80; y < h - 20; y += 28) g.fillText(['x = 3', '2x+3', 'a²+b²', 'f(4)=11', '√16 = 4'][Math.floor(r() * 5)], 20 + r() * 60, y); });
  const sheetM = new THREE.MeshStandardMaterial({map: sheetT, roughness: 0.9, side: THREE.DoubleSide});
  const CC = document.createElement('canvas'); CC.width = 256; CC.height = 96; const calcT = new THREE.CanvasTexture(CC); calcT.colorSpace = THREE.SRGBColorSpace;
  const calcScreenM = new THREE.MeshStandardMaterial({map: calcT, emissive: '#ffffff', emissiveMap: calcT, emissiveIntensity: 0.25});
  const students = [], desks = [];
  const r = rng(21);
  for (let row = 0; row < 4; row++) for (const cx of [-2.7, 0, 2.7]) {
    const z = -1.9 + row * 1.75;
    const d = new THREE.Group(); d.position.set(cx, 0, z); scene.add(d); desks.push(d);
    const top = mesh(new THREE.BoxGeometry(1.5, 0.035, 0.6), deskM, 0, 0.74, 0, d); top.castShadow = top.receiveShadow = true;
    for (const [x, zz] of [[-0.7, -0.25], [0.7, -0.25], [-0.7, 0.25], [0.7, 0.25]]) mesh(new THREE.BoxGeometry(0.035, 0.74, 0.035), legM, x, 0.37, zz, d);
    for (const s of [-0.38, 0.38]) {
      const seed = row * 10 + Math.round(cx) + s * 3 + 40;
      // Stuhl
      const ch = new THREE.Group(); ch.position.set(s, 0, 0.55); d.add(ch);
      mesh(new THREE.BoxGeometry(0.42, 0.025, 0.4), chairM, 0, 0.45, 0, ch).castShadow = true;
      mesh(new THREE.BoxGeometry(0.42, 0.3, 0.025), chairM, 0, 0.72, 0.2, ch).castShadow = true;
      for (const [x, zz] of [[-0.18, -0.17], [0.18, -0.17], [-0.18, 0.17], [0.18, 0.17]]) mesh(new THREE.BoxGeometry(0.02, 0.45, 0.02), legM, x, 0.225, zz, ch);
      // Blatt, Taschenrechner, Stift
      const sh = mesh(new THREE.PlaneGeometry(0.21, 0.297), sheetM, s + (r() - 0.5) * 0.05, 0.759, -0.03, d); sh.rotation.x = -Math.PI / 2; sh.rotation.z = (r() - 0.5) * 0.3;
      const calc = new THREE.Group(); calc.position.set(s + (s > 0 ? 0.2 : -0.2), 0.765, -0.12); calc.rotation.y = (r() - 0.5) * 0.4; d.add(calc);
      mesh(new RoundedBoxGeometry(0.085, 0.015, 0.16, 2, 0.005), mat('#2b2d31', {roughness: 0.5}), 0, 0, 0, calc);
      const cs = mesh(new THREE.PlaneGeometry(0.07, 0.026), calcScreenM, 0, 0.0085, -0.05, calc); cs.rotation.x = -Math.PI / 2;
      for (let i = 0; i < 16; i++) mesh(new THREE.BoxGeometry(0.013, 0.006, 0.011), mat(i % 4 === 3 ? '#e07a2f' : '#8a8d93'), -0.027 + (i % 4) * 0.018, 0.009, -0.01 + Math.floor(i / 4) * 0.02, calc);
      mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.14, 6), mat(['#1d4ed8', '#111', '#c8102e'][Math.floor(r() * 3)]), s - 0.12, 0.762, 0.02, d).rotation.z = Math.PI / 2;
      // Schüler (sitzend, Rücken zur Kamera)
      const p = makePerson(seed, {height: 0.88 + r() * 0.12, longHair: r() < 0.45, shortSleeve: r() < 0.5});
      p.position.set(cx + s, 0, z + 0.5); p.rotation.y = Math.PI; if (row === 3 && cx > 1) continue; scene.add(p);
      p.traverse(o => { if (o.isMesh) o.castShadow = true; });
      students.push({p, ph: r() * 6, delay: r() * 0.7, cheer: r() < 0.85, armsAmt: 0.8 + r() * 0.2, look: (r() - 0.5) * 0.6});
    }
  }
  // fliegende Blätter (Instanzen)
  const NS = 34; const flying = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.21, 0.297), sheetM, NS); flying.castShadow = true; scene.add(flying);
  const fl = []; const rf = rng(77); for (let i = 0; i < NS; i++) { const s = students[i % students.length].p.position;
    fl.push({p0: V3(s.x + (rf() - 0.5) * 0.3, 1.5, s.z - 0.2), v: V3((rf() - 0.5) * 2.2, 3.2 + rf() * 2.6, (rf() - 0.5) * 2.2 - 0.6), t0: THROW + rf() * 2.2, spin: V3(rf() * 8, rf() * 8, rf() * 8), sw: rf() * 6}); }
  // Lehrerin an der Tafel
  const teacher = makePerson(3, {height: 1.06, top: '#7a4b3a', pants: '#2b2b30', hair: '#5a3b22', longHair: true}); teacher.position.set(1.0, 0, ZB + 0.55); scene.add(teacher);
  teacher.traverse(o => { if (o.isMesh) o.castShadow = true; });
  // Neonröhren
  for (const [x, z] of [[-1.5, -1], [1.5, -1], [-1.5, 3], [1.5, 3]]) mesh(new THREE.BoxGeometry(0.25, 0.06, 1.3), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#f4f8ff', emissiveIntensity: 1.2}), x, RH - 0.04, z, scene);
  // Schränke, Weltkarte, Poster an der rechten Wand
  mesh(new THREE.BoxGeometry(0.5, 1.1, 2.4), mat('#b9a17a'), RW - 0.26, 0.55, 4.5, scene);
  const poster = canvasTex(512, 360, (g, w, h) => { g.fillStyle = '#f5f1e6'; g.fillRect(0, 0, w, h); g.fillStyle = '#c8102e'; g.font = '600 40px Plex'; g.fillText('PYTHAGORAS', 30, 60);
    g.strokeStyle = '#1d3d8f'; g.lineWidth = 6; g.beginPath(); g.moveTo(80, 300); g.lineTo(380, 300); g.lineTo(80, 110); g.closePath(); g.stroke(); g.fillStyle = '#111'; g.font = 'italic 46px Garamond'; g.fillText('a² + b² = c²', 220, 200); });
  mesh(new THREE.PlaneGeometry(1.3, 0.92), new THREE.MeshStandardMaterial({map: poster}), RW - 0.02, 1.8, 1.0, scene).rotation.y = -Math.PI / 2;
  // Handy für den Einstieg (Taschenrechner-App)
  const phone = makePhone(); phone.userData.caseM.color.set('#1f2937'); const hands = makeHands('#e8bb98', '#3d4a5c'); const ph = new THREE.Group(); ph.add(phone, hands); scene.add(ph);
  const calcApp = (g, st, SW, SH) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, SW, SH);
    g.fillStyle = '#fff'; g.font = '500 24px Plex'; g.textAlign = 'left'; g.fillText('11:59', 40, 52); g.textAlign = 'right'; g.fillText('5G  71%', SW - 40, 52);
    const keys = [['AC', '+/−', '%', '÷'], ['7', '8', '9', '×'], ['4', '5', '6', '−'], ['1', '2', '3', '+'], ['0', '', ',', '=']];
    keys.forEach((row, j) => row.forEach((k, i) => { if (!k) return; const x = 75 + i * 150, y = 640 + j * 140, op = i === 3, fn = j === 0 && i < 3;
      const hit = (k === '1' && ((st.t > 0.6 && st.t < 0.8) || (st.t > 1.3 && st.t < 1.5))) || (k === '+' && st.t > 1.0 && st.t < 1.2) || (k === '=' && st.t > 1.8 && st.t < 2.0);
      g.fillStyle = hit ? '#fff' : (op ? '#ff9f0a' : (fn ? '#a5a5a5' : '#333')); g.beginPath(); if (k === '0') g.roundRect(15, y - 60, 270, 120, 60); else g.arc(x, y, 62, 0, 7); g.fill();
      g.fillStyle = fn || hit ? '#000' : '#fff'; g.font = '400 56px Plex'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(k, k === '0' ? 90 : x, y); }));
    g.textBaseline = 'alphabetic'; g.textAlign = 'right'; g.fillStyle = '#fff';
    const shown = st.t < 0.6 ? '0' : st.t < 1.0 ? '1' : st.t < 1.3 ? '1 +' : st.t < 1.8 ? '1 + 1' : '2';
    g.font = shown.length > 2 ? '300 130px Plex' : '300 190px Plex'; g.fillText(shown, SW - 40, 520);
    if (st.t >= 1.8) { g.font = '300 50px Plex'; g.fillStyle = '#8e8e93'; g.fillText('1 + 1 =', SW - 40, 330); }
  };
  const camera = new THREE.PerspectiveCamera(58, 1080 / 1920, 0.02, 200);

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.0;
    drawBoard(T);
    // Uhr
    const clockS = T < VANISH ? 11 * 3600 + 59 * 60 + 50 + T : 0;
    const sp = T < VANISH ? 0 : (T - VANISH);
    const sec = T < VANISH ? clockS % 60 : sp * 47 + noise1(T * 3, 2) * 20, mn = T < VANISH ? (clockS / 60) % 60 : -sp * 11 + 60, hr = T < VANISH ? (clockS / 3600) % 12 : sp * 3.3 + 12;
    hS.rotation.z = -sec / 60 * Math.PI * 2; hM.rotation.z = -mn / 60 * Math.PI * 2; hH.rotation.z = -hr / 12 * Math.PI * 2;
    // Taschenrechner-Anzeigen
    { const g = CC.getContext('2d'); g.fillStyle = '#a9b59a'; g.fillRect(0, 0, 256, 96); g.fillStyle = '#1d231a'; g.font = '400 64px Plex'; g.textAlign = 'right';
      const rr = rng(Math.floor(T * 15)); g.fillText(T < VANISH ? '2' : Array.from({length: 8}, () => GL[Math.floor(rr() * 16)]).join(''), 246, 74); calcT.needsUpdate = true; }
    // Schüler
    students.forEach((s, i) => {
      const u = s.p.userData;
      const up = s.cheer ? easeOut(clamp((T - JUMP - s.delay) / 0.45)) : 0;
      posePerson(s.p, {look: T < VANISH ? 0 : s.look * smooth(VANISH + 0.2, VANISH + 0.8, T)});
      const hop = up > 0.9 ? Math.abs(Math.sin((T - JUMP) * 7 + s.ph)) * 0.12 : 0;
      s.p.position.y = lerp(-0.47, 0, up) + hop;
      const seat = 1 - up;
      for (const [k, lg] of [[0, u.legL], [1, u.legR]]) { lg.rotation.x = -1.5 * seat; lg.userData.knee.rotation.x = 1.5 * seat; u.pl[k].position.copy(lg.position); u.pl[k].rotation.copy(lg.rotation); u.pl[k].userData.low.visible = seat < 0.5; }
      if (T < VANISH) { u.armL.rotation.x = -0.9; u.armR.rotation.x = -0.9 + 0.15 * Math.sin(T * 9 + s.ph) * (i % 3 === 0); u.armL.userData.fore.rotation.x = -0.6; u.armR.userData.fore.rotation.x = -0.6; u.torso.rotation.x = 0.18; u.head.rotation.x = 0.35; }
      else {
        const a = up * s.armsAmt; u.armL.rotation.z = -a * 2.6 - Math.sin(T * 9 + s.ph) * 0.25 * up; u.armR.rotation.z = a * 2.6 + Math.sin(T * 9 + s.ph + 1) * 0.25 * up;
        u.armL.rotation.x = lerp(-0.9, 0, up); u.armR.rotation.x = lerp(-0.9, 0, up);
        u.head.rotation.x = lerp(0.2, -0.25, up); u.torso.rotation.x = lerp(0.1, -0.08, up);
      }
    });
    // Lehrerin schreibt, dreht sich dann ungläubig um
    { posePerson(teacher, {}); const u = teacher.userData; const turn = smooth(VANISH + 0.3, VANISH + 1.3, T);
      teacher.rotation.y = lerp(Math.PI * 0.95, 0.15, turn) + Math.PI; teacher.position.x = lerp(1.0, 1.4, turn);
      if (turn < 1) { const w = 1 - turn; u.armR.rotation.x = -2.2 * w; u.armR.rotation.z = 0.4 * w + Math.sin(T * 6) * 0.08 * w; u.armR.userData.fore.rotation.x = -0.4 * w; }
      u.armL.rotation.z = -0.5 * turn; u.armL.userData.fore.rotation.x = -1.6 * turn; u.head.rotation.x = -0.1 * turn; }
    // fliegende Blätter
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
    fl.forEach((f, i) => {
      const t = T - f.t0;
      if (t < 0) { m4.makeScale(0, 0, 0); flying.setMatrixAt(i, m4); return; }
      const dr = 1.6; const vx = f.v.x * (1 - Math.exp(-dr * t)) / dr, vz = f.v.z * (1 - Math.exp(-dr * t)) / dr;
      let y = f.p0.y + f.v.y * (1 - Math.exp(-dr * t)) / dr - 1.2 * t; // Papier sinkt langsam
      y = Math.max(0.01, Math.min(RH - 0.1, y));
      const p = V3(f.p0.x + vx + Math.sin(t * 2 + f.sw) * 0.25, y, f.p0.z + vz);
      e.set(f.spin.x * t * 0.4 + f.sw, f.spin.y * t * 0.3, f.spin.z * t * 0.4); q.setFromEuler(e); m4.compose(p, q, V3(1, 1, 1)); flying.setMatrixAt(i, m4);
    });
    flying.instanceMatrix.needsUpdate = true;
    // Kamera
    ph.visible = shot.id === 'intro';
    if (shot.id === 'intro') {
      const t = T - shot.t0;
      camera.fov = 58; camera.position.set(2.7 + 0.38, 1.28 + noise1(T * 0.7, 1) * 0.004, -1.9 + 0.62); camera.lookAt(2.7 + 0.3, 0.6, -2.6);
      ph.position.set(2.7 + 0.36, 1.08, -1.9 + 0.32); ph.quaternion.copy(camera.quaternion); ph.rotateX(-0.1); ph.translateY(0.0);
      ph.position.y += noise1(T * 0.9, 3) * 0.002;
      updateScreen(phone, [], {t, custom: calcApp, noDrops: true});
      students.forEach(s => s.p.visible = Math.abs(s.p.position.x - 3.08) > 0.1 || Math.abs(s.p.position.z - (-1.4)) > 0.1);
    } else {
      students.forEach(s => s.p.visible = true);
      const t = T - 3.5, u = smooth(0, 13.5, t);
      const shake = T > JUMP ? 0.012 : 0;
      camera.fov = 62; camera.position.set(lerp(4.1, 3.7, u) + noise1(T * 2, 4) * shake, lerp(2.55, 2.4, u) + noise1(T * 2, 5) * shake, lerp(6.2, 5.0, u));
      camera.lookAt(lerp(-1.6, -1.2, u), lerp(0.85, 1.0, u), ZB + 0.6);
    }
    camera.updateProjectionMatrix();
  }};
}
