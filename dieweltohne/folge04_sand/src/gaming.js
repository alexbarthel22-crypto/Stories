// Gaming-Zimmer am Mittag, mitten im Match. Ohne Sand gibt es kein Glas und keine Siliziumchips:
// Monitorglas, Seitenscheibe des PCs und Fensterscheibe verschwinden, der Bildschirm stirbt, Lüfter und RGB gehen aus.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, easeOut, envMap} from './lib.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const GLASS_OFF = 17.15, SCREEN_DEAD = 17.8, CHIPS_OFF = 18.0, WINDOW_OFF = 17.1;
const RAGE = 19.5, HEADSET_OFF = 20.3, STAND = 21.5;
const RW = 2.4, ZB = -1.75, ZF = 2.6, RH = 2.6;

// Monitor: gebogene Fläche (Curved)
function curved(w, h, k) { const g = new THREE.PlaneGeometry(w, h, 40, 1); const p = g.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i); p.setZ(i, -x * x * k); } g.computeVertexNormals(); return g; }

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#0b0c10');
  const env = envMap(renderer); scene.environment = env; scene.environmentIntensity = 0.25;
  scene.add(new THREE.HemisphereLight('#cfd8ff', '#3a3030', 0.75));
  const winFill = new THREE.PointLight('#fff2dc', 4.5, 7, 1.2); winFill.position.set(-1.9, 1.7, 0.2); scene.add(winFill);
  const sun = new THREE.DirectionalLight('#fff1d8', 3.0); sun.position.set(-9, 5, 1.2); sun.target.position.set(0, 0.6, 0);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -4, right: 4, top: 4, bottom: -4, near: 1, far: 25}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.02;
  scene.add(sun, sun.target);
  const rgbA = new THREE.PointLight('#ff2bd6', 4, 6, 1.6); rgbA.position.set(-1.3, 2.3, -1.4);
  const rgbB = new THREE.PointLight('#22d3ff', 3, 5, 1.6); rgbB.position.set(1.4, 0.7, -1.4);
  const scrL = new THREE.PointLight('#7fb0ff', 2.5, 4, 1.5); scrL.position.set(0, 1.05, -1.0);
  scene.add(rgbA, rgbB, scrL);

  // Raum
  const wallM = mat('#2b2f3a', {roughness: 0.9}), floorT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#6b5440'; g.fillRect(0, 0, w, h); const r = rng(2);
    for (let y = 0; y < h; y += 32) { g.fillStyle = `rgba(0,0,0,${0.08 + r() * 0.08})`; g.fillRect(0, y, w, 2); for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '255,220,180' : '40,25,15'},${r() * 0.08})`; g.fillRect(r() * w, y + r() * 30, 30 + r() * 120, 2); } } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(3, 3);
  const fl = mesh(new THREE.PlaneGeometry(RW * 2, ZF - ZB), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.55}), 0, 0, (ZB + ZF) / 2, scene); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true;
  const rug = mesh(new THREE.CircleGeometry(1.1, 40), mat('#1d1f2b', {roughness: 1}), 0.2, 0.004, 0.2, scene); rug.rotation.x = -Math.PI / 2; rug.receiveShadow = true;
  mesh(new THREE.PlaneGeometry(RW * 2, ZF - ZB), mat('#20232c'), 0, RH, (ZB + ZF) / 2, scene).rotation.x = Math.PI / 2;
  mesh(new THREE.BoxGeometry(RW * 2, RH, 0.1), wallM, 0, RH / 2, ZB - 0.05, scene).receiveShadow = true;
  mesh(new THREE.BoxGeometry(0.1, RH, ZF - ZB), wallM, RW + 0.05, RH / 2, (ZB + ZF) / 2, scene).receiveShadow = true;
  mesh(new THREE.BoxGeometry(RW * 2, RH, 0.1), wallM, 0, RH / 2, ZF + 0.05, scene);
  // linke Wand mit Fenster (z -0.9..0.9, y 0.9..2.2)
  const wz0 = -0.9, wz1 = 0.9, wy0 = 0.9, wy1 = 2.2;
  const wl = (y0, y1, z0, z1) => { const m = mesh(new THREE.BoxGeometry(0.15, y1 - y0, z1 - z0), wallM, -RW - 0.07, (y0 + y1) / 2, (z0 + z1) / 2, scene); m.castShadow = m.receiveShadow = true; };
  wl(0, wy0, ZB, ZF); wl(wy1, RH, ZB, ZF); wl(wy0, wy1, ZB, wz0); wl(wy0, wy1, wz1, ZF);
  const frM = mat('#e8e8e4', {roughness: 0.5});
  for (const z of [wz0, 0, wz1]) mesh(new THREE.BoxGeometry(0.1, wy1 - wy0, 0.06), frM, -RW, (wy0 + wy1) / 2, z, scene).castShadow = true;
  for (const y of [wy0, wy1]) mesh(new THREE.BoxGeometry(0.1, 0.06, wz1 - wz0), frM, -RW, y, 0, scene);
  const winGlass = mesh(new THREE.PlaneGeometry(wz1 - wz0, wy1 - wy0), new THREE.MeshStandardMaterial({color: '#cfe6ff', transparent: true, opacity: 0.18, roughness: 0.02, metalness: 0.4}), -RW + 0.01, (wy0 + wy1) / 2, 0, scene); winGlass.rotation.y = Math.PI / 2;
  const outT = canvasTex(512, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#8fc1f0'); gr.addColorStop(1, '#e8f1f5'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(6); g.fillStyle = '#c9b9a3'; g.fillRect(40, 120, 200, 136); g.fillStyle = '#9fb2c4'; for (let x = 55; x < 230; x += 32) for (let y = 135; y < 250; y += 30) g.fillRect(x, y, 18, 16);
    for (let i = 0; i < 18; i++) { g.fillStyle = `rgb(${60 + r() * 30},${110 + r() * 50},${50 + r() * 30})`; g.beginPath(); g.arc(r() * w, 150 + r() * 80, 30 + r() * 50, 0, 7); g.fill(); } });
  const op = mesh(new THREE.PlaneGeometry(14, 7), new THREE.MeshBasicMaterial({map: outT}), -RW - 4, 1.6, 0, scene); op.rotation.y = Math.PI / 2;
  // Vorhänge (halb zu), wehen nach innen, sobald die Scheibe weg ist
  const curtM = new THREE.MeshStandardMaterial({color: '#3b3f6e', roughness: 0.95, side: THREE.DoubleSide});
  const curtains = [[-0.95, -0.25], [0.35, 1.0]].map(([z0, z1]) => { const g = new THREE.PlaneGeometry(z1 - z0, 2.15, 14, 24); const m = new THREE.Mesh(g, curtM); m.position.set(-RW + 0.12, 1.42, (z0 + z1) / 2); m.rotation.y = Math.PI / 2; m.castShadow = true; scene.add(m);
    m.userData.base = g.attributes.position.array.slice(); m.userData.w = z1 - z0; return m; });
  mesh(new THREE.CylinderGeometry(0.015, 0.015, 2.3, 8), mat('#888', {metalness: 0.8}), -RW + 0.12, 2.5, 0, scene).rotation.x = Math.PI / 2;

  // Poster
  const poster = (seed, title, c1, c2) => canvasTex(360, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, c1); gr.addColorStop(1, c2); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(seed); for (let i = 0; i < 9; i++) { g.fillStyle = `rgba(255,255,255,${0.06 + r() * 0.12})`; g.beginPath(); g.moveTo(r() * w, r() * h); g.lineTo(r() * w, r() * h); g.lineTo(r() * w, r() * h); g.fill(); }
    g.fillStyle = '#111'; g.beginPath(); g.ellipse(w / 2, h * 0.58, 70, 150, 0, 0, 7); g.fill(); g.beginPath(); g.arc(w / 2, h * 0.3, 48, 0, 7); g.fill();
    g.fillStyle = '#fff'; g.font = '600 46px Plex'; g.textAlign = 'center'; g.fillText(title, w / 2, h - 46); });
  for (const [x, t, s, a, b] of [[-1.55, 'LEVEL UP', 3, '#ff3d7f', '#4b1e9e'], [1.55, 'NO RESPAWN', 5, '#13c8b5', '#0d2a5e']]) mesh(new THREE.PlaneGeometry(0.62, 0.88), new THREE.MeshStandardMaterial({map: poster(s, t, a, b), roughness: 0.7}), x, 1.75, ZB + 0.01, scene);
  // Bett-Ecke rechts hinten
  mesh(new RoundedBoxGeometry(1.0, 0.45, 2.0, 3, 0.06), mat('#d6d2c8'), RW - 0.55, 0.23, 1.4, scene).receiveShadow = true;
  mesh(new RoundedBoxGeometry(1.02, 0.12, 1.5, 3, 0.05), mat('#2f5d8a', {roughness: 1}), RW - 0.55, 0.5, 1.6, scene);
  mesh(new RoundedBoxGeometry(0.6, 0.14, 0.35, 3, 0.06), mat('#f2f2ee'), RW - 0.55, 0.54, 0.6, scene);

  // Schreibtisch
  const deskM = mat('#17181c', {roughness: 0.4});
  const desk = mesh(new THREE.BoxGeometry(1.9, 0.04, 0.8), deskM, 0, 0.74, ZB + 0.42, scene); desk.castShadow = desk.receiveShadow = true;
  for (const x of [-0.9, 0.9]) mesh(new THREE.BoxGeometry(0.05, 0.72, 0.7), deskM, x, 0.36, ZB + 0.42, scene);
  const pad = mesh(new THREE.PlaneGeometry(1.2, 0.42), mat('#0e0f12', {roughness: 1}), 0.1, 0.762, ZB + 0.6, scene); pad.rotation.x = -Math.PI / 2; pad.receiveShadow = true;
  const rgbMats = []; // alle RGB-Elemente
  const rgb = (w, h, d, x, y, z, ph) => { const m = new THREE.MeshStandardMaterial({color: '#111', emissive: '#ff00ff', emissiveIntensity: 2.5}); m.userData.ph = ph; rgbMats.push(m); return mesh(new THREE.BoxGeometry(w, h, d), m, x, y, z, scene); };
  rgb(1.2, 0.004, 0.006, 0.1, 0.763, ZB + 0.39, 0); rgb(1.2, 0.004, 0.006, 0.1, 0.763, ZB + 0.81, 0.5); // Mauspad-Rand
  rgb(1.9, 0.01, 0.01, 0, 0.715, ZB + 0.82, 0.2);                                                          // Tischkante unten
  rgb(3.6, 0.02, 0.02, 0, RH - 0.05, ZB + 0.06, 0.7);                                                      // Lichtleiste oben
  const bias = mesh(new THREE.PlaneGeometry(1.6, 0.9), new THREE.MeshBasicMaterial({map: canvasTex(256, 128, (g, w, h) => { const gr = g.createRadialGradient(w / 2, h / 2, 5, w / 2, h / 2, w / 2); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }), color: '#8a3dff', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false}), 0, 1.15, ZB + 0.005, scene);
  // Tastatur mit RGB-Tasten
  const keyT = canvasTex(512, 160, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); for (let r = 0; r < 5; r++) for (let c = 0; c < 15; c++) { g.fillStyle = `hsl(${(c * 24 + r * 10) % 360},100%,60%)`; g.fillRect(6 + c * 33.5, 8 + r * 30, 27, 22); } });
  const keyM = new THREE.MeshStandardMaterial({color: '#1a1b1f', emissive: '#ffffff', emissiveMap: keyT, emissiveIntensity: 1.2, roughness: 0.5});
  const kb = mesh(new THREE.BoxGeometry(0.44, 0.025, 0.14), [mat('#111'), mat('#111'), keyM, mat('#111'), mat('#111'), mat('#111')], -0.05, 0.775, ZB + 0.66, scene); kb.rotation.y = 0.04; kb.castShadow = true;
  const mouse = mesh(new THREE.CapsuleGeometry(0.03, 0.05, 4, 10), mat('#141418', {roughness: 0.4}), 0.42, 0.775, ZB + 0.66, scene); mouse.rotation.x = Math.PI / 2; mouse.scale.set(1, 1, 0.5);
  rgb(0.004, 0.004, 0.06, 0.42, 0.79, ZB + 0.66, 0.3);
  const can = mesh(new THREE.CylinderGeometry(0.033, 0.033, 0.16, 20), mat('#16c26a', {metalness: 0.8, roughness: 0.3}), 0.72, 0.84, ZB + 0.42, scene); can.castShadow = true;

  // Curved-Monitor
  const SC = document.createElement('canvas'); SC.width = 1024; SC.height = 434; const scT = new THREE.CanvasTexture(SC); scT.colorSpace = THREE.SRGBColorSpace; scT.anisotropy = 8;
  const mon = new THREE.Group(); mon.position.set(0, 1.12, ZB + 0.22); scene.add(mon);
  const panel = new THREE.Group(); mon.add(panel);
  const screen = mesh(curved(1.22, 0.517, 0.22), new THREE.MeshBasicMaterial({map: scT, toneMapped: false}), 0, 0, 0, panel);
  const back = mesh(curved(1.26, 0.55, 0.22), mat('#0d0e11', {side: THREE.DoubleSide}), 0, 0, -0.025, panel); back.castShadow = true;
  const monGlass = mesh(curved(1.22, 0.517, 0.22), new THREE.MeshStandardMaterial({color: '#ffffff', transparent: true, opacity: 0.1, roughness: 0.02, metalness: 0.9, envMapIntensity: 2}), 0, 0, 0.006, panel);
  mesh(new THREE.BoxGeometry(0.06, 0.32, 0.04), mat('#202227', {metalness: 0.6}), 0, -0.33, -0.06, mon);
  mesh(new THREE.BoxGeometry(0.34, 0.012, 0.2), mat('#202227', {metalness: 0.6}), 0, -0.37, 0.0, mon);

  function drawGame(T) {
    const g = SC.getContext('2d'), w = SC.width, h = SC.height, sw = Math.sin(T * 1.3) * 14, r = rng(Math.floor(T * 20) + 3);
    const sky = g.createLinearGradient(0, 0, 0, h); sky.addColorStop(0, '#3b6fe0'); sky.addColorStop(0.55, '#f6a96b'); sky.addColorStop(1, '#f6d58b'); g.fillStyle = sky; g.fillRect(0, 0, w, h);
    g.fillStyle = 'rgba(160,60,255,0.45)'; g.fillRect(0, 0, 140 + Math.sin(T) * 10, h); // Sturmwand
    const hill = (col, base, amp, f, ph) => { g.fillStyle = col; g.beginPath(); g.moveTo(0, h); for (let x = 0; x <= w; x += 16) g.lineTo(x, base + Math.sin(x * f + ph + sw * 0.01) * amp); g.lineTo(w, h); g.fill(); };
    hill('#7a6bb5', 230, 30, 0.006, 1); hill('#4f8f5a', 280, 22, 0.011, 2); hill('#3c7a45', 320, 14, 0.02, 4);
    for (let i = 0; i < 7; i++) { const x = 140 + i * 125 + sw, y = 300 - (i % 3) * 18; g.fillStyle = ['#ff5d5d', '#ffd23f', '#3fc5ff', '#9b5dff'][i % 4]; g.fillRect(x, y - 60, 70, 60); g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(x + 70, y - 60, 14, 60); g.fillStyle = '#5a3a2a'; g.beginPath(); g.moveTo(x - 6, y - 60); g.lineTo(x + 42, y - 95); g.lineTo(x + 90, y - 60); g.fill(); }
    // Spielfigur von hinten
    const cx = w / 2 - 30, cy = h - 40; g.fillStyle = '#ff7a2f'; g.beginPath(); g.ellipse(cx, cy - 60, 40, 62, 0, 0, 7); g.fill(); g.fillStyle = '#2a2a38'; g.fillRect(cx - 28, cy - 100, 56, 56);
    g.fillStyle = '#f2c79c'; g.beginPath(); g.arc(cx, cy - 135, 24, 0, 7); g.fill(); g.fillStyle = '#ffde2e'; g.beginPath(); g.arc(cx, cy - 142, 25, Math.PI, 0); g.fill();
    g.fillStyle = '#333'; g.save(); g.translate(cx + 38, cy - 70); g.rotate(-0.3); g.fillRect(0, -8, 90, 16); g.restore();
    // HUD
    g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 3; g.beginPath(); g.moveTo(w / 2 - 14, h / 2 - 30); g.lineTo(w / 2 + 14, h / 2 - 30); g.moveTo(w / 2, h / 2 - 44); g.lineTo(w / 2, h / 2 - 16); g.stroke();
    g.fillStyle = 'rgba(0,0,0,0.45)'; g.beginPath(); g.arc(w - 80, 80, 60, 0, 7); g.fill(); g.strokeStyle = '#fff'; g.stroke(); g.fillStyle = '#ff3b3b'; g.beginPath(); g.arc(w - 70 + Math.sin(T) * 10, 70, 6, 0, 7); g.fill();
    g.fillStyle = '#fff'; g.font = '600 30px Plex'; g.textAlign = 'right'; g.fillText('#2 ÜBRIG', w - 160, 50); g.font = '500 22px Plex'; g.fillText('7 ELIMINIERUNGEN', w - 160, 82);
    g.textAlign = 'left'; g.fillStyle = 'rgba(0,0,0,0.45)'; g.fillRect(30, h - 70, 300, 44); g.fillStyle = '#3bdc6a'; g.fillRect(36, h - 52, 288 * 0.78, 20); g.fillStyle = '#3fa9ff'; g.fillRect(36, h - 64, 288 * 0.5, 8);
    g.fillStyle = '#fff'; g.font = '600 22px Plex'; g.fillText('78', 300, h - 34); g.textAlign = 'center'; g.font = '600 34px Plex'; g.fillText('24 | 120', w / 2 + 220, h - 30);
    g.textAlign = 'left'; g.font = '400 18px Plex'; g.fillStyle = 'rgba(255,255,255,0.9)'; ['xNova ⟶ Blitz42', 'du ⟶ Kaktus_7', 'Reaper ⟶ moonfox'].forEach((s, i) => g.fillText(s, 24, 34 + i * 26));
    // Zerfall: Glas weg, Schichten lösen sich, Pixelfehler
    if (T >= GLASS_OFF) {
      const k = clamp((T - GLASS_OFF) / (SCREEN_DEAD - GLASS_OFF));
      for (let i = 0; i < 30 * k + 6; i++) { const y = r() * h, hh = 4 + r() * 40; g.drawImage(SC, 0, y, w, hh, (r() - 0.5) * 120 * k, y, w, hh); }
      for (let i = 0; i < 25; i++) { g.fillStyle = ['#ff00ff', '#00ffff', '#ffffff', '#00ff66', '#000'][Math.floor(r() * 5)]; g.fillRect(r() * w, 0, 1 + r() * 4, h); }
      g.fillStyle = `rgba(0,0,0,${k * 0.9})`; g.fillRect(0, 0, w, h);
      if (r() < 0.35) { g.fillStyle = 'rgba(255,255,255,0.6)'; g.fillRect(0, 0, w, h); }
    }
    if (T >= SCREEN_DEAD) { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); const f = clamp(1 - (T - SCREEN_DEAD) / 0.3);
      for (let i = 0; i < 6; i++) { g.fillStyle = `rgba(255,255,255,${f * 0.8})`; g.fillRect(rng(i + 9)() * w, 0, 2, h); } }
    scT.needsUpdate = true;
  }

  // PC mit Glasseite (links auf dem Tisch), Lüfter, Grafikkarte
  const pc = new THREE.Group(); pc.position.set(-0.72, 0.76, ZB + 0.42); scene.add(pc);
  const PW = 0.22, PH = 0.48, PD = 0.46;
  const caseM = mat('#141518', {roughness: 0.45, metalness: 0.3});
  for (const [w, h, d, x, y, z] of [[PW, 0.01, PD, 0, PH, 0], [PW, 0.01, PD, 0, 0, 0], [0.01, PH, PD, -PW / 2, PH / 2, 0], [PW, PH, 0.01, 0, PH / 2, -PD / 2], [PW, PH, 0.01, 0, PH / 2, PD / 2]]) mesh(new THREE.BoxGeometry(w, h, d), caseM, x, y, z, pc).castShadow = true;
  mesh(new THREE.PlaneGeometry(PD - 0.02, PH - 0.02), mat('#1d1f24', {roughness: 0.8}), -PW / 2 + 0.012, PH / 2, 0, pc).rotation.y = Math.PI / 2; // Mainboard
  const sideGlass = mesh(new THREE.PlaneGeometry(PD, PH), new THREE.MeshStandardMaterial({color: '#9aa4b8', transparent: true, opacity: 0.22, roughness: 0.02, metalness: 0.8, envMapIntensity: 2}), PW / 2, PH / 2, 0, pc); sideGlass.rotation.y = Math.PI / 2;
  const fans = [];
  for (let i = 0; i < 3; i++) { const f = new THREE.Group(); f.position.set(0, 0.08 + i * 0.14, PD / 2 - 0.03); pc.add(f);
    const ringM = new THREE.MeshStandardMaterial({color: '#111', emissive: '#ff00ff', emissiveIntensity: 3}); ringM.userData.ph = i * 0.15; rgbMats.push(ringM);
    mesh(new THREE.TorusGeometry(0.058, 0.007, 8, 32), ringM, 0, 0, 0, f);
    const hub = new THREE.Group(); f.add(hub); mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.01, 16), mat('#222'), 0, 0, 0, hub).rotation.x = Math.PI / 2;
    for (let b = 0; b < 7; b++) { const bl = mesh(new THREE.BoxGeometry(0.012, 0.045, 0.003), new THREE.MeshStandardMaterial({color: '#e8e8f0', transparent: true, opacity: 0.85, emissive: '#ffffff', emissiveIntensity: 0.15}), 0, 0.03, 0, new THREE.Group()); const pv = bl.parent; pv.rotation.z = b / 7 * Math.PI * 2; bl.rotation.y = 0.5; hub.add(pv); }
    f.rotation.y = 0; fans.push(hub); }
  const gpu = mesh(new THREE.BoxGeometry(0.12, 0.045, 0.3), mat('#2a2c31', {metalness: 0.6, roughness: 0.35}), 0.0, 0.2, -0.03, pc); gpu.castShadow = true;
  { const m = new THREE.MeshStandardMaterial({color: '#111', emissive: '#00ffff', emissiveIntensity: 3}); m.userData.ph = 0.4; rgbMats.push(m); mesh(new THREE.BoxGeometry(0.004, 0.006, 0.26), m, 0.062, 0.215, -0.03, pc); }
  const cool = new THREE.Group(); cool.position.set(-0.05, 0.36, -0.06); pc.add(cool);
  { const m = new THREE.MeshStandardMaterial({color: '#111', emissive: '#ff00ff', emissiveIntensity: 3}); m.userData.ph = 0.6; rgbMats.push(m); mesh(new THREE.TorusGeometry(0.04, 0.006, 8, 28), m, 0.07, 0, 0, cool).rotation.y = Math.PI / 2; }
  mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.05, 20), mat('#3a3d44', {metalness: 0.8}), 0.04, 0, 0, cool).rotation.z = Math.PI / 2;
  for (let i = 0; i < 4; i++) mesh(new THREE.BoxGeometry(0.1, 0.012, 0.012), mat('#c9a14a', {metalness: 0.9, roughness: 0.3}), 0.02, 0.06 + i * 0.03, 0.1, pc); // RAM

  // Glitzern, wenn Glas zu nichts wird
  const glintT = canvasTex(64, 64, (g, w) => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,245,220,0.6)'); gr.addColorStop(1, 'rgba(255,240,200,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const glints = []; { const r = rng(17); const spots = [[0, 1.12, ZB + 0.23, 0.6, 0.25, 0], [-0.61, 0.99, ZB + 0.42, 0.01, 0.23, 0.22], [-RW + 0.02, 1.55, 0, 0.01, 0.65, 0.9]];
    for (let i = 0; i < 70; i++) { const s = spots[i % 3]; const sp = new THREE.Sprite(new THREE.SpriteMaterial({map: glintT, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false}));
      sp.userData = {p: V3(s[0] + (r() - 0.5) * 2 * s[3], s[1] + (r() - 0.5) * 2 * s[4], s[2] + (r() - 0.5) * 2 * s[5]), t0: (i % 3 === 2 ? WINDOW_OFF : GLASS_OFF) - 0.05 + r() * 0.2, sz: 0.01 + r() * 0.025, vy: -0.1 - r() * 0.3}; scene.add(sp); glints.push(sp); } }

  // Spieler: Gaming-Stuhl, Headset
  const chair = new THREE.Group(); chair.position.set(0, 0, ZB + 1.45); scene.add(chair);
  const chM = mat('#1b1c22', {roughness: 0.6}), chR = mat('#c8102e', {roughness: 0.6});
  mesh(new RoundedBoxGeometry(0.52, 0.09, 0.5, 3, 0.03), chM, 0, 0.5, 0, chair).castShadow = true;
  const backR = mesh(new RoundedBoxGeometry(0.5, 0.82, 0.09, 3, 0.04), chM, 0, 0.98, 0.26, chair); backR.castShadow = true; backR.rotation.x = 0.1;
  mesh(new THREE.BoxGeometry(0.08, 0.7, 0.095), chR, -0.16, 0.98, 0.26, chair).rotation.x = 0.1; mesh(new THREE.BoxGeometry(0.08, 0.7, 0.095), chR, 0.16, 0.98, 0.26, chair).rotation.x = 0.1;
  mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.4, 10), mat('#333', {metalness: 0.7}), 0, 0.27, 0, chair);
  for (let i = 0; i < 5; i++) { const a = i / 5 * Math.PI * 2; const l = mesh(new THREE.BoxGeometry(0.32, 0.03, 0.04), mat('#222'), Math.cos(a) * 0.15, 0.06, Math.sin(a) * 0.15, chair); l.rotation.y = -a; }
  const teen = makePerson(812, {height: 1.0, top: '#20232a', pants: '#3a3a40', hair: '#2a1d15', shortSleeve: false}); teen.rotation.y = Math.PI; scene.add(teen);
  teen.traverse(o => { if (o.isMesh) o.castShadow = true; });
  const headset = new THREE.Group(); scene.add(headset);
  const hsM = mat('#18191d', {roughness: 0.4}); const hb = mesh(new THREE.TorusGeometry(0.13, 0.014, 8, 24, Math.PI), hsM, 0, 0, 0, headset);
  for (const s of [-1, 1]) { mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.04, 20), hsM, s * 0.13, -0.01, 0, headset).rotation.z = Math.PI / 2;
    const m = new THREE.MeshStandardMaterial({color: '#111', emissive: '#00ffff', emissiveIntensity: 2.5}); m.userData.ph = 0.8; rgbMats.push(m); mesh(new THREE.TorusGeometry(0.04, 0.005, 6, 20), m, s * 0.152, -0.01, 0, headset).rotation.y = Math.PI / 2; }
  const mic = mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.16, 6), hsM, -0.15, -0.08, 0.06, headset); mic.rotation.x = 1.0;

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 80);
  const tmp = V3(0, 0, 0), tmp2 = V3(0, 0, 0);

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.05;
    drawGame(T);
    const gl = T < GLASS_OFF, chips = T < CHIPS_OFF;
    monGlass.visible = gl; sideGlass.visible = gl; winGlass.visible = T < WINDOW_OFF;
    // Display-Schichten sacken nach vorn, wenn das Glas fehlt
    const sag = easeOut(clamp((T - SCREEN_DEAD + 0.2) / 0.8)); panel.rotation.x = 0.22 * sag; panel.position.y = -0.03 * sag; panel.position.z = 0.03 * sag;
    // RGB
    rgbMats.forEach(m => { const hue = (T * 0.25 + m.userData.ph) % 1; m.emissive.setHSL(hue, 1, 0.55); m.emissiveIntensity = chips ? (m.emissiveIntensity > 0 ? m.emissiveIntensity : 2.5) : 0; if (!chips) m.emissiveIntensity = 0; else m.emissiveIntensity = 2.6; });
    keyM.emissiveIntensity = chips ? 1.2 : 0; bias.visible = chips; bias.material.color.setHSL((T * 0.25 + 0.7) % 1, 1, 0.5);
    rgbA.intensity = chips ? 4 : 0; rgbB.intensity = chips ? 3 : 0; rgbA.color.setHSL((T * 0.25) % 1, 1, 0.55); rgbB.color.setHSL((T * 0.25 + 0.5) % 1, 1, 0.55);
    scrL.intensity = T < GLASS_OFF ? 2.5 : (T < SCREEN_DEAD ? 2.5 * (rng(Math.floor(T * 20))() * 1.2) : 0);
    // Lüfter laufen aus
    const ang = T < CHIPS_OFF ? T * 40 : CHIPS_OFF * 40 + 40 * (1 - Math.exp(-(T - CHIPS_OFF) * 1.4)) / 1.4; fans.forEach((f, i) => f.rotation.z = ang + i);
    // Vorhänge wehen
    const blow = smooth(WINDOW_OFF, WINDOW_OFF + 0.5, T);
    curtains.forEach((c, ci) => { const p = c.geometry.attributes.position, b = c.userData.base;
      for (let i = 0; i < p.count; i++) { const x = b[i * 3], y = b[i * 3 + 1]; const v = clamp((1.075 - y) / 2.15); // 0 oben, 1 unten
        const fold = Math.sin(x * 22 + ci) * 0.03; const gust = blow * v * (0.45 + 0.25 * Math.sin(T * 3.1 + x * 4 + ci) + 0.12 * noise1(T * 2.2 + x * 3, ci + 1));
        p.setXYZ(i, x + Math.sin(T * 2 + y) * 0.03 * blow * v, y + gust * 0.25, fold + gust); }
      p.needsUpdate = true; c.geometry.computeVertexNormals(); });
    // Glitzern
    glints.forEach(s => { const d = T - s.userData.t0; s.visible = d > 0 && d < 0.6; if (!s.visible) return; const k = Math.sin(clamp(d / 0.6) * Math.PI);
      s.position.copy(s.userData.p).add(V3(0, s.userData.vy * d, 0)); s.scale.setScalar(s.userData.sz * (0.6 + k)); s.material.opacity = k * (0.6 + 0.4 * Math.sin(d * 60 + s.id)); });
    // Spieler
    const up = easeOut(clamp((T - STAND) / 0.6));
    chair.position.z = ZB + 1.45 + 0.35 * easeOut(clamp((T - STAND - 0.1) / 0.7)); chair.rotation.y = 0.25 * up;
    teen.position.set(0, lerp(-0.45, 0, up), ZB + 1.38 + 0.12 * up);
    posePerson(teen, {});
    const u = teen.userData, seat = 1 - up;
    for (const [k, lg] of [[0, u.legL], [1, u.legR]]) { lg.rotation.x = -1.5 * seat; lg.userData.knee.rotation.x = 1.5 * seat; u.pl[k].position.copy(lg.position); u.pl[k].rotation.copy(lg.rotation); u.pl[k].userData.low.visible = seat < 0.5; }
    const play = 1 - smooth(RAGE - 0.3, RAGE, T);
    // Spielhaltung: Hände an Tastatur und Maus, leichtes Zucken
    u.armL.rotation.x = -1.05; u.armL.rotation.z = 0.25; u.armL.userData.fore.rotation.x = -0.75;
    u.armR.rotation.x = -1.05 + Math.sin(T * 13) * 0.03 * play; u.armR.rotation.z = -0.25; u.armR.userData.fore.rotation.x = -0.7;
    u.torso.rotation.x = 0.12 * play; u.head.rotation.x = 0.1;
    // Schreck, dann Hände an den Kopf
    const shock = smooth(GLASS_OFF, GLASS_OFF + 0.25, T) * (1 - smooth(RAGE - 0.2, RAGE, T)); u.torso.rotation.x -= 0.2 * shock; u.head.rotation.x -= 0.15 * shock;
    const rage = smooth(RAGE, RAGE + 0.35, T) * (1 - smooth(HEADSET_OFF - 0.1, HEADSET_OFF + 0.1, T));
    if (rage > 0) { u.armL.rotation.x = lerp(u.armL.rotation.x, -2.8, rage); u.armL.rotation.z = lerp(0.25, -0.35, rage); u.armL.userData.fore.rotation.x = lerp(-0.75, -1.9, rage);
      u.armR.rotation.x = lerp(u.armR.rotation.x, -2.8, rage); u.armR.rotation.z = lerp(-0.25, 0.35, rage); u.armR.userData.fore.rotation.x = lerp(-0.7, -1.9, rage); u.head.rotation.x = lerp(0.1, -0.35, rage); u.torso.rotation.x = -0.15 * rage; }
    const pull = smooth(HEADSET_OFF - 0.1, HEADSET_OFF + 0.35, T) * (1 - smooth(HEADSET_OFF + 0.7, HEADSET_OFF + 1.1, T));
    if (pull > 0) { u.armR.rotation.x = lerp(-1.05, -3.0, pull); u.armR.rotation.z = lerp(-0.25, 0.6, pull); u.armR.userData.fore.rotation.x = lerp(-0.7, -0.6, pull); u.armL.rotation.x = lerp(-1.05, -0.4, pull); u.armL.userData.fore.rotation.x = -0.4; }
    if (T > HEADSET_OFF + 0.9) { const k = smooth(HEADSET_OFF + 0.9, STAND, T); u.armL.rotation.x = lerp(-1.05, -0.2, k); u.armR.rotation.x = lerp(-1.05, -0.2, k); u.armL.userData.fore.rotation.x = -0.3; u.armR.userData.fore.rotation.x = -0.3; u.armL.rotation.z = -0.15; u.armR.rotation.z = 0.15; }
    if (T > STAND) { u.head.rotation.x = -0.05 + 0.1 * Math.sin(T * 1.7); u.torso.rotation.y = 0.15 * Math.sin((T - STAND) * 1.2); u.armL.rotation.z = -0.35 - 0.2 * Math.sin(T * 2.4); u.armR.rotation.z = 0.35 + 0.2 * Math.sin(T * 2.4 + 1); u.armL.userData.fore.rotation.x = -1.2; u.armR.userData.fore.rotation.x = -1.2; }
    teen.updateMatrixWorld(true);
    // Headset: auf dem Kopf, dann in der rechten Hand, dann auf den Tisch geworfen
    u.head.getWorldPosition(tmp); const onHead = tmp.clone().add(V3(0, 0.1, 0));
    u.armR.userData.fore.getWorldPosition(tmp2); const hand = tmp2.clone().add(V3(0, 0.25 * pull, 0));
    if (T < HEADSET_OFF) { headset.position.copy(onHead); headset.rotation.set(0, 0, 0); }
    else if (T < HEADSET_OFF + 0.7) { const k = smooth(HEADSET_OFF, HEADSET_OFF + 0.35, T); headset.position.copy(onHead).lerp(hand, k); headset.rotation.set(-0.6 * k, 0, 0.5 * k); }
    else { const t = T - HEADSET_OFF - 0.7, p0 = hand, land = V3(0.35, 0.79, ZB + 0.55); const k = clamp(t / 0.45);
      headset.position.set(lerp(p0.x, land.x, k), lerp(p0.y, land.y, k) + Math.sin(k * Math.PI) * 0.2, lerp(p0.z, land.z, k)); headset.rotation.set(-0.6 - 2.2 * k, 0.4 * k, 0.5 + 1.2 * k); if (k >= 1) headset.rotation.set(-Math.PI / 2 + 0.1, 0.4, 0.2); }
    // Kamera: über die Schulter, langsame Fahrt
    const t = T - shot.t0, cu = smooth(0, 7, t), shake = T > GLASS_OFF && T < GLASS_OFF + 0.6 ? 0.004 : 0;
    camera.fov = 54; camera.position.set(lerp(1.05, 0.9, cu) + noise1(T * 12, 1) * shake, lerp(2.0, 1.92, cu), lerp(1.35, 1.0, cu)); camera.lookAt(lerp(-0.22, -0.18, cu), 0.92, ZB + 0.25);
    camera.updateProjectionMatrix();
  }};
}
