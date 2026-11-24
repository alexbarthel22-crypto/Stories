// Freibad. pool (Stufe 3): Arschbombe vom Zehner – ohne Schwerkraft kommt er nie unten an und treibt über die Liegewiese.
// drop_pool: Schwerkraft zurück – er landet im Planschbecken.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut, makePerson, posePerson, envMap, skyDome} from './lib.js';
import {addMouth, mouthOpen, brows, seat} from './people.js';
import {flail, blob, wobble} from './float.js';
import {VANISH, BOMB, POOL_LAND} from './timeline.js';
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
  mesh(new THREE.PlaneGeometry(300, 300), new THREE.MeshStandardMaterial({map: grassT, roughness: 1}), 0, -0.01, 0, scene).rotation.x = -Math.PI / 2;
  // Beckenumrandung (Platten), Becken 14 x 12 m (x -7..7, z -6..6), 4 m tief
  const tiles = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#e8e3d6'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(0,0,0,0.12)'; g.lineWidth = 2; for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * 64, 0); g.lineTo(i * 64, h); g.moveTo(0, i * 64); g.lineTo(w, i * 64); g.stroke(); } });
  tiles.wrapS = tiles.wrapT = THREE.RepeatWrapping; tiles.repeat.set(12, 12);
  const deckM = new THREE.MeshStandardMaterial({map: tiles, roughness: 0.8});
  for (const [x, z, w, d] of [[0, -8.5, 22, 5], [0, 8.5, 22, 5], [-9, 0, 4, 12], [9, 0, 4, 12]]) mesh(new THREE.BoxGeometry(w, 0.2, d), deckM, x, 0.0, z, scene);
  const blueT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#3fa7d6'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(255,255,255,0.25)'; g.lineWidth = 2; for (let i = 0; i <= 8; i++) { g.beginPath(); g.moveTo(i * 32, 0); g.lineTo(i * 32, h); g.moveTo(0, i * 32); g.lineTo(w, i * 32); g.stroke(); } });
  blueT.wrapS = blueT.wrapT = THREE.RepeatWrapping; blueT.repeat.set(6, 3);
  const basinM = new THREE.MeshStandardMaterial({map: blueT, roughness: 0.5});
  mesh(new THREE.PlaneGeometry(14, 12), basinM, 0, -2.0, 0, scene).rotation.x = -Math.PI / 2;
  for (const [x, z, ry, w] of [[0, -6, 0, 14], [0, 6, Math.PI, 14], [-7, 0, Math.PI / 2, 12], [7, 0, -Math.PI / 2, 12]]) { const m = mesh(new THREE.PlaneGeometry(w, 2.1), basinM, x, -0.95, z, scene); m.rotation.y = ry; }
  const causT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#2b9fd8'; g.fillRect(0, 0, w, h); const r = rng(2); g.strokeStyle = 'rgba(210,245,255,0.45)'; g.lineWidth = 3;
    for (let i = 0; i < 80; i++) { g.beginPath(); let x = r() * w, y = r() * h; g.moveTo(x, y); for (let k = 0; k < 5; k++) { x += (r() - 0.5) * 70; y += (r() - 0.5) * 70; g.lineTo(x, y); } g.stroke(); } });
  causT.wrapS = causT.wrapT = THREE.RepeatWrapping; causT.repeat.set(3, 3);
  const water = mesh(new THREE.PlaneGeometry(14, 12), new THREE.MeshPhysicalMaterial({map: causT, transparent: true, opacity: 0.82, roughness: 0.06, clearcoat: 1}), 0, -0.12, 0, scene); water.rotation.x = -Math.PI / 2; water.receiveShadow = true; water.castShadow = false;
  // Sprungturm (1, 3, 5, 10 m) am Kopfende
  const conc = mat('#d5d2cb', {roughness: 0.9}), rail = mat('#c9ccd1', {metalness: 0.8, roughness: 0.3});
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
  const kids = [0, 1, 2].map(i => { const p = makePerson(1500 + i * 9, {height: 0.62, shortSleeve: true, top: towelC[i + 2]}); addMouth(p); scene.add(p); return p; });
  // Schwimmer im großen Becken (nur Köpfe/Schultern), Wasserbälle aus Tropfen
  const swim = []; for (let i = 0; i < 7; i++) { const p = makePerson(1600 + i * 5, {shortSleeve: true}); addMouth(p); scene.add(p); swim.push({p, x: lerp(-5.5, 5.5, r()), z: lerp(-2, 5, r()), s: r() * 9}); }
  const drops = []; for (let i = 0; i < 46; i++) { const b = blob('#9fdcf7', 0.03 + r() * 0.08); b.material.transparent = true; b.material.opacity = 0.75; scene.add(b); drops.push({b, p: V3(lerp(-6, 6, r()), 0.0, lerp(-5, 5, r())), v: V3((r() - 0.5) * 0.3, 0.25 + r() * 0.6, (r() - 0.5) * 0.3), s: i}); }
  const beach = mesh(new THREE.SphereGeometry(0.3, 20, 14), new THREE.MeshStandardMaterial({map: canvasTex(256, 128, (g, w, h) => { const c = ['#e33', '#fff', '#2d7fd6', '#fff', '#f2c230', '#fff']; c.forEach((cc, i) => { g.fillStyle = cc; g.fillRect(i * w / 6, 0, w / 6 + 1, h); }); }), roughness: 0.4}), 3, 0.15, 1.5, scene);
  // Bademeister auf dem Hochstuhl
  const lg = makePerson(1777, {top: '#d33', pants: '#d33', shortSleeve: true, height: 1.05}); addMouth(lg); scene.add(lg);
  mesh(new THREE.BoxGeometry(0.6, 1.8, 0.6), mat('#ffffff'), 8.0, 0.9, 1.5, scene);
  // Er
  const pivot = new THREE.Group(); scene.add(pivot);
  const guy = makePerson(1208, {skin: '#e2b28c', top: '#e2b28c', pants: '#ff7a3d', hair: '#2a1d15', height: 1.0, shortSleeve: true}); addMouth(guy); pivot.add(guy); guy.position.y = -0.95;
  // Spritzer im Planschbecken
  const splash = []; for (let i = 0; i < 70; i++) { const b = blob('#bfe8fb', 0.03 + r() * 0.06); b.material.transparent = true; b.material.opacity = 0.85; scene.add(b); const a = r() * 7, s = 1.5 + r() * 4;
    splash.push({b, v: V3(Math.cos(a) * s * 0.6, 2 + r() * 6, Math.sin(a) * s * 0.6)}); }

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
    // Tropfen und Wasserball schweben (ab VANISH)
    const dT = T - VANISH;
    drops.forEach((d, i) => { d.b.visible = !drop; if (drop) return; const k = clamp(dT); d.b.position.copy(d.p).addScaledVector(d.v, dT * k); wobble(d.b, T, d.s); });
    if (!drop) { beach.position.set(3 + 0.1 * dT, 0.15 + 0.35 * dT, 1.5); beach.rotation.set(dT * 0.4, dT * 0.7, 0); } else beach.position.set(5, 0.15, 3);
    // Schwimmer: treiben mit dem Kopf über Wasser hoch
    swim.forEach(q => { const p = q.p; posePerson(p, {}); p.position.set(q.x, -1.25 + (drop ? 0 : 0.22 * dT), q.z); p.rotation.set(drop ? 0 : 0.1 * dT, q.s, 0);
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
    // Spritzer
    splash.forEach(s => { const t = T - POOL_LAND; s.b.visible = drop && t > 0 && t < 1.6; if (!s.b.visible) return; s.b.position.set(KID.x + s.v.x * t, 0.4 + s.v.y * t - 4.9 * t * t, KID.z + s.v.z * t); if (s.b.position.y < 0.3) s.b.visible = false; });
    kWater.position.y = 0.33 + (drop && T > POOL_LAND ? 0.05 * Math.sin((T - POOL_LAND) * 12) * Math.exp(-(T - POOL_LAND) * 2) : 0);
    causT.offset.set(T * 0.02, T * 0.013);

    // ---------- Kamera ----------
    let pos, lk; camera.fov = 50; camera.up.set(0, 1, 0);
    if (!drop) {
      if (T < BOMB + 0.6) { const k = smooth(24, BOMB + 0.6, T); pos = V3(lerp(5.5, 5.0, k), lerp(9.6, 10.6, k), lerp(-2.0, -1.0, k)); lk = V3(0, 10.6, lerp(-6.5, -4.4, k)); camera.fov = 52; }
      else if (T < 28.2) { const k = smooth(BOMB + 0.6, 28.2, T); pos = V3(lerp(-11, -12, k), lerp(7.5, 8.5, k), lerp(5.5, 9.0, k)); lk = pivot.position.clone().add(V3(0, -3.2, 0)); camera.fov = lerp(48, 52, k); }
      else { const k = smooth(28.2, 31, T); pos = V3(lerp(4.0, 4.6, k), 1.3, lerp(21.5, 23, k)); lk = V3(pivot.position.x * 0.6, lerp(7.2, 7.8, k), pivot.position.z); camera.fov = lerp(58, 62, k); }
    } else {
      const k = smooth(61, 64, T); pos = V3(KID.x + lerp(5.2, 4.6, k), lerp(1.6, 1.4, k), KID.z + lerp(4.0, 3.6, k)); lk = V3(KID.x, lerp(9.5, 0.8, smooth(61.0, POOL_LAND + 0.1, T)), KID.z); camera.fov = lerp(62, 48, smooth(POOL_LAND - 0.2, 64, T));
      if (T > POOL_LAND && T < POOL_LAND + 0.4) pos.add(V3(noise1(T * 12, 1) * 0.05, noise1(T * 12, 4) * 0.05, 0));
    }
    camera.position.copy(pos); camera.lookAt(lk); camera.updateProjectionMatrix();
  }};
}
