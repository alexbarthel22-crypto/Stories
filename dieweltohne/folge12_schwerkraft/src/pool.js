// Freibad. pool (Stufe 3): Arschbombe vom Zehner – ohne Schwerkraft kommt er nie unten an und treibt über die Liegewiese.
// drop_pool: Schwerkraft zurück – er landet im Planschbecken.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut, makePerson, posePerson, envMap, skyDome} from './lib.js';
import {addMouth, mouthOpen, brows, seat} from './people.js';
import {flail, blob, wobble} from './float.js';
import {waterBlobs, updateBlobs, splashFX} from './water.js';
import {rainSystem, updateRain} from './lib.js';
import {VANISH, RETURN, BOMB, POOL_LAND} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
export const PZ0 = -5.4, VZ = 3.0, VY = 0.5, H0 = 10.4; // Absprung: Kante z, Geschwindigkeit nach vorn/oben, Höhe Hüfte
const KID = V3(2.5, 0, 15.5); // Planschbecken

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.4;
  scene.add(skyDome('#3f8fe0', '#8cc4f2', '#e4f2fb', 300));
  scene.fog = new THREE.Fog('#d7ebf8', 60, 220);
  scene.add(new THREE.HemisphereLight('#dff0ff', '#6c8a4a', 1.0));
  const sun = new THREE.DirectionalLight('#fff3dc', 3.0); sun.position.set(-14, 30, 10); sun.target.position.set(0, 0, 4); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -22, right: 22, top: 22, bottom: -22, near: 1, far: 90}); scene.add(sun, sun.target);

  // Wiese
  const grassT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#5f9a3e'; g.fillRect(0, 0, w, h); const r = rng(6); for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${40 + r() * 60},${110 + r() * 70},${30 + r() * 40},0.5)`; g.fillRect(r() * w, r() * h, 2, 4); } });
  grassT.wrapS = grassT.wrapT = THREE.RepeatWrapping; grassT.repeat.set(30, 30);
  { const sh = new THREE.Shape([new THREE.Vector2(-150, -150), new THREE.Vector2(150, -150), new THREE.Vector2(150, 150), new THREE.Vector2(-150, 150)]);
    sh.holes.push(new THREE.Path([new THREE.Vector2(-7, -6), new THREE.Vector2(-7, 6), new THREE.Vector2(7, 6), new THREE.Vector2(7, -6)]));
    const gg = new THREE.ShapeGeometry(sh); const uv = gg.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) / 300, uv.getY(i) / 300);
    mesh(gg, new THREE.MeshStandardMaterial({map: grassT, roughness: 1}), 0, -0.01, 0, scene).rotation.x = -Math.PI / 2; }
  // Beckenumrandung (Platten), Becken 14 x 12 m (x -7..7, z -6..6), 4 m tief
  const tiles = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#e8e3d6'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(0,0,0,0.12)'; g.lineWidth = 2; for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * 64, 0); g.lineTo(i * 64, h); g.moveTo(0, i * 64); g.lineTo(w, i * 64); g.stroke(); } });
  tiles.wrapS = tiles.wrapT = THREE.RepeatWrapping; tiles.repeat.set(12, 12);
  const deckM = new THREE.MeshStandardMaterial({map: tiles, roughness: 0.8});
  const rail = mat('#c9ccd1', {metalness: 0.8, roughness: 0.3});
  for (const [x, z, w, d] of [[0, -8.5, 22, 5], [0, 8.5, 22, 5], [-9, 0, 4, 12], [9, 0, 4, 12]]) mesh(new THREE.BoxGeometry(w, 0.2, d), deckM, x, 0.0, z, scene);
  const DEPTH = 4.5;
  const blueT = canvasTex(512, 512, (g, w, h) => { const r = rng(12); const n = 16, c = w / n;
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) { const v = r() * 14 - 7; g.fillStyle = `rgb(${92 + v},${170 + v},${205 + v})`; g.fillRect(x * c, y * c, c, c); }
    g.strokeStyle = 'rgba(235,245,250,0.85)'; g.lineWidth = 3; for (let i = 0; i <= n; i++) { g.beginPath(); g.moveTo(i * c, 0); g.lineTo(i * c, h); g.moveTo(0, i * c); g.lineTo(w, i * c); g.stroke(); }
    g.fillStyle = 'rgba(20,40,60,0.12)'; for (let i = 0; i < 40; i++) { g.beginPath(); g.ellipse(r() * w, r() * h, 10 + r() * 40, 4 + r() * 12, r() * 3, 0, 7); g.fill(); } });
  blueT.wrapS = blueT.wrapT = THREE.RepeatWrapping; blueT.repeat.set(7, 6);
  const basinM = new THREE.MeshStandardMaterial({map: blueT, roughness: 0.25, metalness: 0.0, envMapIntensity: 1.2});
  mesh(new THREE.PlaneGeometry(14, 12), basinM, 0, -DEPTH, 0, scene).rotation.x = -Math.PI / 2;
  const laneT = canvasTex(64, 512, (g, w, h) => { g.fillStyle = '#1d3f73'; g.fillRect(24, 0, 16, h); g.fillRect(8, 20, 48, 12); g.fillRect(8, h - 32, 48, 12); });
  for (const x of [-3.5, 0, 3.5]) { const l = mesh(new THREE.PlaneGeometry(0.6, 11), new THREE.MeshStandardMaterial({map: laneT, transparent: true, roughness: 0.3}), x, -DEPTH + 0.01, 0, scene); l.rotation.x = -Math.PI / 2; }
  const wallT = blueT.clone(); wallT.repeat.set(7, 2.2); wallT.needsUpdate = true; const wallM = new THREE.MeshStandardMaterial({map: wallT, roughness: 0.25});
  for (const [x, z, ry, w] of [[0, -6, 0, 14], [0, 6, Math.PI, 14], [-7, 0, Math.PI / 2, 12], [7, 0, -Math.PI / 2, 12]]) { const m = mesh(new THREE.PlaneGeometry(w, DEPTH + 0.1), wallM, x, -DEPTH / 2, z, scene); m.rotation.y = ry; }
  // Überlaufrinne und Wasserlinie (nasser Rand, wo das Wasser stand)
  for (const [x, z, w, d] of [[0, -6.1, 14.4, 0.2], [0, 6.1, 14.4, 0.2], [-7.1, 0, 0.2, 12.2], [7.1, 0, 0.2, 12.2]]) mesh(new THREE.BoxGeometry(w, 0.06, d), mat('#5d6a70', {roughness: 0.4}), x, -0.05, z, scene);
  for (const s2 of [-1, 1]) { const ladder = new THREE.Group(); ladder.position.set(s2 * 6.2, 0, 5.9); scene.add(ladder); for (const dx of [-0.25, 0.25]) mesh(new THREE.TorusGeometry(0.35, 0.025, 6, 16, Math.PI), rail, dx, 0.0, -0.3, ladder).rotation.y = Math.PI / 2;
    for (let k = 1; k < 7; k++) mesh(new THREE.BoxGeometry(0.5, 0.03, 0.08), rail, 0, -k * 0.3, 0.05, ladder); }
  const causT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#2b9fd8'; g.fillRect(0, 0, w, h); const r = rng(2); g.strokeStyle = 'rgba(210,245,255,0.45)'; g.lineWidth = 3;
    for (let i = 0; i < 80; i++) { g.beginPath(); let x = r() * w, y = r() * h; g.moveTo(x, y); for (let k = 0; k < 5; k++) { x += (r() - 0.5) * 70; y += (r() - 0.5) * 70; g.lineTo(x, y); } g.stroke(); } });
  causT.wrapS = causT.wrapT = THREE.RepeatWrapping; causT.repeat.set(3, 3);
  // Das Wasser des Beckens: schwebt als tausende Kugeln (ab VANISH)
  const poolW = waterBlobs(renderer, 1100, {x0: -6.8, x1: 6.8, y0: -DEPTH + 0.2, y1: -0.2, z0: -5.8, z1: 5.8}, {seed: 5, vy0: 0.06, vy1: 0.42, rMin: 0.04, rMax: 0.45, bigShare: 0.04, rBig0: 0.6, rBig1: 1.5, vx: 0.12, vz: 0.12, delay: 0.8});
  scene.add(poolW);
  // Sprungturm (1, 3, 5, 10 m) am Kopfende
  const conc = mat('#d5d2cb', {roughness: 0.9});
  mesh(new THREE.BoxGeometry(3, 10.2, 1.6), conc, 0, 5.1, -8.2, scene);
  for (const [h, len] of [[3, 2.4], [5, 2.6], [10, 3.0]]) { mesh(new THREE.BoxGeometry(2.2, 0.25, len), conc, 0, h, -7.4 + len / 2 - 0.5, scene);
    for (const s of [-1, 1]) mesh(new THREE.CylinderGeometry(0.03, 0.03, len, 6), rail, s * 1.05, h + 1.0, -7.4 + len / 2 - 0.5, scene).rotation.x = Math.PI / 2; }
  const stripe = canvasTex(64, 8, (g, w, h) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? '#d33' : '#fff'; g.fillRect(i * 8, 0, 8, h); } });
  mesh(new THREE.BoxGeometry(2.21, 0.05, 0.25), new THREE.MeshStandardMaterial({map: stripe}), 0, 10.14, -5.0, scene);
  // Liegewiese: Handtücher, Schirme, Leute; Zaun; Planschbecken
  const r = rng(21); const towelC = ['#e94f6a', '#2f8fd6', '#f2c230', '#3fbf7f', '#9b59b6', '#ff8c42'];
  const lawn = [];
  for (let i = 0; i < 16; i++) { const x = lerp(-14, 14, r()), z = lerp(11, 22, r()); if (Math.hypot(x - KID.x, z - KID.z) < 3.4) continue;
    const t = mesh(new THREE.BoxGeometry(0.9, 0.02, 1.9), mat(towelC[i % 6]), x, 0.01, z, scene); t.rotation.y = r() * 0.6;
    if (i % 2 === 0) { const p = makePerson(900 + i * 7, {shortSleeve: true, top: towelC[(i + 2) % 6]}); addMouth(p); scene.add(p); lawn.push({p, x, z, ry: t.rotation.y, s: r() * 9}); }
    if (i % 4 === 1) { const u = new THREE.Group(); u.position.set(x + 1.2, 0, z); scene.add(u); mesh(new THREE.CylinderGeometry(0.025, 0.025, 2.2, 6), rail, 0, 1.1, 0, u); mesh(new THREE.ConeGeometry(1.3, 0.5, 10, 1, true), mat(towelC[(i + 1) % 6], {side: THREE.DoubleSide}), 0, 2.25, 0, u); } }
  const fenceM = mat('#3d6b3a', {roughness: 0.7});
  for (let x = -30; x <= 30; x += 2.5) mesh(new THREE.BoxGeometry(0.06, 2.0, 0.06), fenceM, x, 1.0, 26, scene);
  mesh(new THREE.BoxGeometry(60, 1.6, 0.02), new THREE.MeshStandardMaterial({color: '#3d6b3a', transparent: true, opacity: 0.35}), 0, 1.0, 26, scene);
  for (let i = 0; i < 12; i++) { const tr = new THREE.Group(); tr.position.set(lerp(-40, 40, r()), 0, lerp(30, 45, r())); scene.add(tr); mesh(new THREE.CylinderGeometry(0.25, 0.35, 3, 8), mat('#6b4a2b'), 0, 1.5, 0, tr); mesh(new THREE.SphereGeometry(2.6 + r() * 1.5, 12, 10), mat('#3f7a33', {roughness: 1}), 0, 4.6, 0, tr); }
  for (let i = 0; i < 10; i++) { const tr = new THREE.Group(); tr.position.set(i < 5 ? -24 - r() * 8 : 24 + r() * 8, 0, lerp(-25, 20, r())); scene.add(tr); mesh(new THREE.CylinderGeometry(0.25, 0.35, 3, 8), mat('#6b4a2b'), 0, 1.5, 0, tr); mesh(new THREE.SphereGeometry(2.6 + r() * 1.5, 12, 10), mat('#3f7a33', {roughness: 1}), 0, 4.6, 0, tr); }
  // Planschbecken (rund) mit Kindern
  const kp = new THREE.Group(); kp.position.copy(KID); scene.add(kp);
  mesh(new THREE.CylinderGeometry(2.2, 2.2, 0.45, 32, 1, true), mat('#3fa7d6', {side: THREE.DoubleSide}), 0, 0.22, 0, kp);
  mesh(new THREE.TorusGeometry(2.2, 0.12, 8, 40), mat('#f2c230'), 0, 0.45, 0, kp).rotation.x = Math.PI / 2;
  const kWater = mesh(new THREE.CircleGeometry(2.15, 32), new THREE.MeshPhysicalMaterial({map: causT, transparent: true, opacity: 0.85, roughness: 0.06, clearcoat: 1}), 0, 0.33, 0, kp); kWater.rotation.x = -Math.PI / 2; kWater.castShadow = false;
  const kidW = waterBlobs(renderer, 260, {x0: KID.x - 1.8, x1: KID.x + 1.8, y0: 0.06, y1: 0.32, z0: KID.z - 1.8, z1: KID.z + 1.8}, {seed: 9, vy0: 0.03, vy1: 0.14, rMin: 0.03, rMax: 0.22, bigShare: 0.03, rBig0: 0.35, rBig1: 0.7, delay: 0.5});
  scene.add(kidW);
  const kSplash = splashFX(scene, 1.0);
  const rain = rainSystem(2600, {x0: KID.x - 14, x1: KID.x + 14, y0: 0, y1: 16, z0: KID.z - 16, z1: KID.z + 10}, 0xd8ecf6, 0.9, 0.55); scene.add(rain);
  const kids = [0, 1, 2].map(i => { const p = makePerson(1500 + i * 9, {height: 0.62, shortSleeve: true, top: towelC[i + 2]}); addMouth(p); scene.add(p); return p; });
  // Schwimmer im großen Becken (nur Köpfe/Schultern), Wasserbälle aus Tropfen
  const swim = []; for (let i = 0; i < 7; i++) { const p = makePerson(1600 + i * 5, {shortSleeve: true}); addMouth(p); scene.add(p); swim.push({p, x: lerp(-5.5, 5.5, r()), z: lerp(-2, 5, r()), s: r() * 9}); }
  const beach = mesh(new THREE.SphereGeometry(0.3, 20, 14), new THREE.MeshStandardMaterial({map: canvasTex(256, 128, (g, w, h) => { const c = ['#e33', '#fff', '#2d7fd6', '#fff', '#f2c230', '#fff']; c.forEach((cc, i) => { g.fillStyle = cc; g.fillRect(i * w / 6, 0, w / 6 + 1, h); }); }), roughness: 0.4}), 3, 0.15, 1.5, scene);
  // Bademeister auf dem Hochstuhl
  const lg = makePerson(1777, {top: '#d33', pants: '#d33', shortSleeve: true, height: 1.05}); addMouth(lg); scene.add(lg);
  mesh(new THREE.BoxGeometry(0.6, 1.8, 0.6), mat('#ffffff'), 8.0, 0.9, 1.5, scene);
  // Er
  const pivot = new THREE.Group(); scene.add(pivot);
  const guy = makePerson(1208, {skin: '#e2b28c', top: '#e2b28c', pants: '#ff7a3d', hair: '#2a1d15', height: 1.0, shortSleeve: true}); addMouth(guy); pivot.add(guy); guy.position.y = -0.95;
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 400); scene.add(camera);
  const look = (p, tgt) => { const d = V3().subVectors(tgt, p.position); p.rotation.y = Math.atan2(d.x, d.z); };
  const bombPose = (u, k) => { u.legL.rotation.x = u.legR.rotation.x = -1.7 * k; u.legL.userData.knee.rotation.x = u.legR.userData.knee.rotation.x = 2.2 * k; u.pl.forEach((g, i) => { const l = i ? u.legR : u.legL; g.position.copy(l.position); g.rotation.copy(l.rotation); });
    u.armL.rotation.set(-1.3 * k, 0, 0.3 * k); u.armR.rotation.set(-1.3 * k, 0, -0.3 * k); u.armL.userData.fore.rotation.x = -1.2 * k; u.armR.userData.fore.rotation.x = -1.2 * k; u.torso.rotation.x = 0.4 * k; };
  const FALL0 = POOL_LAND - Math.sqrt(2 * (13.0 - 0.75) / 9.8);
  const top = V3(KID.x - 0.2, 13.0, KID.z);

  return {scene, camera, update(shot, T) {
    const drop = shot.id === 'drop_pool';
    const u = guy.userData; posePerson(guy, {}); guy.position.set(0, -0.95, 0); guy.rotation.set(0, 0, 0);
    if (!drop) {
      // Anlauf auf dem 10-m-Brett, Absprung bei BOMB
      if (T < BOMB) { const k = clamp((T - 24.0) / (BOMB - 24.0)); pivot.position.set(0, H0 - 0.15, lerp(-7.4, PZ0, k)); pivot.rotation.set(0, 0, 0); posePerson(guy, {walk: (T - 24) * 12, walkAmp: 1.2}); }
      else { const d = T - BOMB; pivot.position.set(0.05 * d, H0 + VY * d, PZ0 + VZ * d); pivot.rotation.set(0.55 * d, 0.2 * d, 0.1 * Math.sin(d));
        bombPose(u, smooth(0, 0.3, d)); if (d > 2.2) { const k = smooth(2.2, 3.0, d); bombPose(u, 1 - k); flail(guy, T, 3, k); }
        mouthOpen(guy, d > 2 ? 0.8 : 0.2); brows(guy, d > 1.5 ? 1 : 0.2, 0); }
    } else {
      const t = Math.max(0, T - FALL0); const y = Math.max(0.75, top.y - 4.9 * t * t);
      pivot.position.set(top.x, y, top.z); pivot.rotation.set(T < POOL_LAND ? 0.4 * Math.sin(T * 2) : 0, 0.6, 0);
      if (T < POOL_LAND) { flail(guy, T * 1.5, 3, 1); mouthOpen(guy, 0.9); brows(guy, 1, 0); }
      else { // sitzt im Planschbecken, Daumen hoch
        seat(guy, 0.35); guy.position.y = guy.position.y - 0.75 + 0.0; u.armR.rotation.set(-1.5 * smooth(POOL_LAND + 0.6, POOL_LAND + 1.0, T), 0, 0.3); u.armR.userData.fore.rotation.x = -1.2; mouthOpen(guy, 0.15); brows(guy, 0.6, 0); u.head.rotation.z = 0.15; }
    }
    // Wasser: steigt ab VANISH als Kugeln aus den Becken; im drop-Shot prasselt es zurück
    const dT = T - VANISH;
    if (!drop) { updateBlobs(poolW, dT, null); updateBlobs(kidW, dT, null); }
    else { const f = T - 60.9; updateBlobs(poolW, RETURN - VANISH, f, -DEPTH); updateBlobs(kidW, RETURN - VANISH, f, 0.05); }
    rain.visible = drop && T > 61.3 && T < 64; if (rain.visible) updateRain(rain, T, 16, 0.05);
    rain.material.opacity = 0.5 * smooth(61.3, 61.8, T) * (1 - smooth(63.3, 64, T));
    kSplash.update(drop ? T - POOL_LAND : -1, V3(KID.x - 0.2, 0.35, KID.z));
    if (!drop) { beach.position.set(3 + 0.1 * dT, 0.15 + 0.35 * dT, 1.5); beach.rotation.set(dT * 0.4, dT * 0.7, 0); } else beach.position.set(5, 0.15, 3);
    // Schwimmer: treiben mit dem Kopf über Wasser hoch
    swim.forEach(q => { const p = q.p; p.visible = !drop; posePerson(p, {}); p.position.set(q.x, -1.25 + 0.16 * dT, q.z); p.rotation.set(0.05 * dT * Math.sin(q.s), q.s, 0.04 * dT * Math.cos(q.s));
      if (!drop) { flail(p, T, q.s, 0.8); mouthOpen(p, 0.6); brows(p, 1, 0); p.userData.head.rotation.x = -0.4; } });
    // Leute auf der Wiese schauen hoch
    lawn.forEach((q, i) => { const p = q.p; posePerson(p, {}); seat(p, 0.32); p.position.set(q.x, p.position.y - 0.32, q.z); look(p, V3(pivot.position.x, 0, pivot.position.z));
      const pu = p.userData; pu.head.rotation.x = -0.7; mouthOpen(p, 0.5); brows(p, 1, 0); if (!drop && dT > 0) { p.position.y += 0.08 * dT; flail(p, T, q.s, 0.5); }
      if (i % 3 === 0) { pu.armR.rotation.x = -2.6; } });
    // Kinder im Planschbecken
    kids.forEach((p, i) => { posePerson(p, {}); seat(p, 0.4); const a = i * 2.1; p.position.set(KID.x + Math.cos(a) * 1.3, p.position.y - 0.25, KID.z + Math.sin(a) * 1.3); look(p, V3(KID.x, 0, KID.z));
      p.userData.head.rotation.x = drop ? -0.7 * (1 - smooth(POOL_LAND, POOL_LAND + 0.5, T)) : 0; mouthOpen(p, drop ? 0.8 : 0.3); brows(p, 1, 0);
      if (drop && T > POOL_LAND + 0.2) { p.userData.armL.rotation.z = -2.6; p.userData.armR.rotation.z = 2.6; } });
    // Bademeister
    posePerson(lg, {}); seat(lg, 1.8 + 0.45); lg.position.set(8.0, lg.position.y, 1.5); look(lg, V3(pivot.position.x, 0, pivot.position.z)); lg.userData.head.rotation.x = -0.6; lg.userData.armR.rotation.x = -2.0; mouthOpen(lg, 0.8); brows(lg, 1, 0);
    kWater.visible = drop && T > 61.6; kWater.position.y = 0.06 + 0.27 * smooth(61.6, 63.6, T) + (drop && T > POOL_LAND ? 0.04 * Math.sin((T - POOL_LAND) * 12) * Math.exp(-(T - POOL_LAND) * 2) : 0);
    causT.offset.set(T * 0.02, T * 0.013);

    // ---------- Kamera ----------
    let pos, lk; camera.fov = 50; camera.up.set(0, 1, 0);
    if (!drop) {
      if (T < BOMB + 0.6) { const k = smooth(24, BOMB + 0.6, T); pos = V3(lerp(5.5, 5.0, k), lerp(9.6, 10.6, k), lerp(-2.0, -1.0, k)); lk = V3(0, lerp(10.2, 6.5, k), lerp(-6.5, -2.0, k)); camera.fov = 56; }
      else if (T < 28.2) { const k = smooth(BOMB + 0.6, 28.2, T); pos = pivot.position.clone().add(V3(lerp(1.4, 1.8, k), lerp(2.0, 2.6, k), lerp(-1.8, -2.4, k))); lk = pivot.position.clone().add(V3(-0.3, -6, lerp(1.0, 2.5, k))); camera.fov = 62; }
      else { const k = smooth(28.2, 31, T); pos = V3(lerp(4.0, 4.6, k), 1.3, lerp(21.5, 23, k)); lk = V3(pivot.position.x * 0.6, lerp(7.2, 7.8, k), pivot.position.z); camera.fov = lerp(58, 62, k); }
    } else {
      const k = smooth(61, 64, T); pos = V3(KID.x + lerp(5.2, 4.6, k), lerp(1.6, 1.4, k), KID.z + lerp(4.0, 3.6, k)); lk = V3(KID.x, lerp(9.5, 0.8, smooth(61.0, POOL_LAND + 0.1, T)), KID.z); camera.fov = lerp(62, 48, smooth(POOL_LAND - 0.2, 64, T));
      if (T > POOL_LAND && T < POOL_LAND + 0.4) pos.add(V3(noise1(T * 12, 1) * 0.05, noise1(T * 12, 4) * 0.05, 0));
    }
    camera.position.copy(pos); camera.lookAt(lk); camera.updateProjectionMatrix();
  }};
}
