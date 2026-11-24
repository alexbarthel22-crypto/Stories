// Turnhalle. gym (Stufe 2): Sein erster Dunk – ohne Schwerkraft hört er nicht mehr auf zu steigen und knallt an die Hallendecke.
// drop_gym: Die Schwerkraft ist zurück. Die Klasse hat den Weichboden drunter geschoben – Bauchklatscher.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {addMouth, mouthOpen, brows} from './people.js';
import {flail} from './float.js';
import {VANISH, JUMP, BONK, GYM_LAND} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const CEIL = 7.0, RIM = 3.05, BZ = -6.1;
export const VY = 2.17; // m/s nach dem Absprung

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.background = new THREE.Color('#dfe3e6');
  scene.add(new THREE.HemisphereLight('#f4f7ff', '#a07a50', 1.05));
  const key = new THREE.DirectionalLight('#fff4e0', 2.2); key.position.set(6, 12, 6); key.target.position.set(0, 0, -3); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, {left: -10, right: 10, top: 10, bottom: -10, near: 1, far: 40}); scene.add(key, key.target);

  // Hallenboden mit Linien
  const floorT = canvasTex(2048, 1536, (g, w, h) => { const r = rng(5);
    for (let i = 0; i < 64; i++) { const v = 190 + r() * 25; g.fillStyle = `rgb(${v},${v * 0.78},${v * 0.52})`; g.fillRect(0, i * 24, w, 23); g.fillStyle = 'rgba(0,0,0,0.12)'; g.fillRect(0, i * 24 + 23, w, 1);
      for (let k = 0; k < 6; k++) g.fillRect(r() * w, i * 24, 1, 23); }
    g.strokeStyle = '#1f6fd1'; g.lineWidth = 8; g.strokeRect(80, 80, w - 160, h - 160); g.beginPath(); g.moveTo(w / 2, 80); g.lineTo(w / 2, h - 80); g.stroke(); g.beginPath(); g.arc(w / 2, h / 2, 140, 0, 7); g.stroke();
    g.strokeStyle = '#d33'; g.beginPath(); g.arc(80, h / 2, 520, -1.3, 1.3); g.stroke(); g.strokeRect(80, h / 2 - 190, 420, 380);
    g.strokeStyle = '#e8c21a'; g.lineWidth = 6; g.strokeRect(300, 260, w - 600, h - 520); });
  const floor = mesh(new THREE.PlaneGeometry(20, 15), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.35}), 0, 0, 0, scene); floor.rotation.x = -Math.PI / 2; floor.rotation.z = Math.PI / 2;
  const wallM = mat('#e6e2d6', {roughness: 0.95}), padM = mat('#2f5fa8', {roughness: 0.8});
  mesh(new THREE.BoxGeometry(15, CEIL, 0.2), wallM, 0, CEIL / 2, -10, scene); mesh(new THREE.BoxGeometry(15, CEIL, 0.2), wallM, 0, CEIL / 2, 10, scene);
  mesh(new THREE.BoxGeometry(0.2, CEIL, 20), wallM, -7.5, CEIL / 2, 0, scene); mesh(new THREE.BoxGeometry(0.2, CEIL, 20), wallM, 7.5, CEIL / 2, 0, scene);
  mesh(new THREE.BoxGeometry(15, 2, 0.05), padM, 0, 1, -9.88, scene); mesh(new THREE.BoxGeometry(0.05, 2, 20), padM, 7.38, 1, 0, scene); mesh(new THREE.BoxGeometry(0.05, 2, 20), padM, -7.38, 1, 0, scene);
  // Fensterband oben
  const winT = canvasTex(512, 64, (g, w, h) => { g.fillStyle = '#cfe4f7'; g.fillRect(0, 0, w, h); g.fillStyle = '#9db2c4'; for (let x = 0; x < w; x += 64) g.fillRect(x, 0, 5, h); });
  winT.wrapS = THREE.RepeatWrapping; winT.repeat.set(6, 1);
  for (const x of [-7.37, 7.37]) { const m = mesh(new THREE.PlaneGeometry(20, 1.4), new THREE.MeshBasicMaterial({map: winT}), x, 5.6, 0, scene); m.rotation.y = x < 0 ? Math.PI / 2 : -Math.PI / 2; }
  // Decke mit Stahlträgern und Lampen
  mesh(new THREE.BoxGeometry(15, 0.2, 20), mat('#cfd3d6', {roughness: 0.9}), 0, CEIL + 0.1, 0, scene);
  const steel = mat('#7d8790', {metalness: 0.6, roughness: 0.4});
  for (let z = -9; z <= 9; z += 3) mesh(new THREE.BoxGeometry(15, 0.45, 0.2), steel, 0, CEIL - 0.22, z, scene);
  const lampM = mat('#ffffff', {emissive: '#fffaf0', emissiveIntensity: 1.6});
  for (const x of [-4, 0, 4]) for (let z = -7.5; z <= 7.5; z += 3) { const l = mesh(new THREE.BoxGeometry(1.4, 0.08, 0.35), lampM, x, CEIL - 0.5, z, scene); l.castShadow = false; }
  // Sprossenwand und Bank
  for (let x = -6; x <= -2; x += 1) { for (let y = 0.3; y < 2.8; y += 0.28) mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.95, 8), mat('#d8b27a'), x, y, 9.82, scene).rotation.z = Math.PI / 2; mesh(new THREE.BoxGeometry(0.08, 2.9, 0.08), mat('#c49a62'), x - 0.5, 1.45, 9.82, scene); }
  mesh(new THREE.BoxGeometry(4, 0.06, 0.35), mat('#d8b27a'), 4, 0.42, -9.2, scene);
  // Korb
  const hoop = new THREE.Group(); scene.add(hoop);
  mesh(new THREE.BoxGeometry(1.8, 1.05, 0.05), new THREE.MeshPhysicalMaterial({color: '#ffffff', transparent: true, opacity: 0.55, roughness: 0.05}), 0, RIM + 0.5, BZ - 0.45, hoop);
  mesh(new THREE.BoxGeometry(0.6, 0.45, 0.06), mat('#ffffff', {roughness: 0.4}), 0, RIM + 0.28, BZ - 0.42, hoop);
  const rimM = mat('#e2541f', {metalness: 0.4, roughness: 0.4});
  const rim = mesh(new THREE.TorusGeometry(0.23, 0.012, 8, 32), rimM, 0, RIM, BZ, hoop); rim.rotation.x = Math.PI / 2;
  const netM = new THREE.MeshStandardMaterial({color: '#ffffff', wireframe: true, transparent: true, opacity: 0.8});
  mesh(new THREE.CylinderGeometry(0.23, 0.15, 0.42, 12, 3, true), netM, 0, RIM - 0.21, BZ, hoop);
  mesh(new THREE.BoxGeometry(0.15, 0.15, 3.2), steel, 0, RIM + 0.6, BZ - 2.1, hoop); mesh(new THREE.BoxGeometry(0.15, 2.2, 0.15), steel, 0, CEIL - 1.1, BZ - 3.6, hoop);
  // Weichboden (für die Landung)
  const matG = new THREE.Group(); scene.add(matG);
  mesh(new RoundedBoxGeometry(2.2, 0.45, 3.0, 3, 0.1), mat('#2c56b8', {roughness: 0.85}), 0, 0.225, 0, matG);
  // Ball
  const ballT = canvasTex(256, 128, (g, w, h) => { g.fillStyle = '#e0702a'; g.fillRect(0, 0, w, h); g.strokeStyle = '#2a1508'; g.lineWidth = 3; g.beginPath(); g.moveTo(0, h / 2); g.lineTo(w, h / 2); for (const x of [w / 4, w / 2, w * 3 / 4]) { g.moveTo(x, 0); g.lineTo(x, h); } g.stroke(); });
  const ball = mesh(new THREE.SphereGeometry(0.12, 24, 16), new THREE.MeshStandardMaterial({map: ballT, roughness: 0.7}), 0, 0, 0, scene);

  // Er (Sportsachen)
  const pivot = new THREE.Group(); scene.add(pivot);
  const guy = makePerson(1207, {skin: '#e2b28c', top: '#ff7a3d', pants: '#22262e', hair: '#2a1d15', height: 1.0, shortSleeve: true}); addMouth(guy); pivot.add(guy); guy.position.y = -0.95;
  // Klasse mit Handys, Sportlehrer
  const r = rng(12); const kids = [];
  const spots = [[-2.6, -2.2], [-3.2, -1.0], [-2.2, 0.2], [2.4, -2.0], [3.0, -0.6], [2.0, 0.6], [-1.0, 1.4], [0.9, 1.6], [-3.6, -3.4], [3.6, -3.2], [-0.2, 2.6], [1.8, 2.8]];
  spots.forEach(([x, z], i) => { const p = makePerson(700 + i * 13, {height: 0.95 + r() * 0.1, shortSleeve: true, longHair: r() < 0.45, ponytail: r() < 0.25}); addMouth(p); scene.add(p);
    const ph = mesh(new THREE.BoxGeometry(0.07, 0.14, 0.01), mat('#111', {roughness: 0.3}), 0, 0, 0, scene); kids.push({p, x, z, ph, s: r() * 9, film: i % 3 !== 2}); });
  const coach = makePerson(2301, {top: '#c8102e', pants: '#1f2a44', hair: '#5a3b22', height: 1.06}); addMouth(coach); scene.add(coach);
  const whistle = mesh(new THREE.BoxGeometry(0.05, 0.03, 0.03), mat('#e5b31b', {metalness: 0.5}), 0, -0.13, 0.1, coach.userData.head);

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 80); scene.add(camera);
  const look = (p, tgt) => { const d = V3().subVectors(tgt, p.position); p.rotation.y = Math.atan2(d.x, d.z); };
  const LAND = GYM_LAND, FALL0 = LAND - Math.sqrt((CEIL - 1.0 - 1.1) * 2 / 9.8); // Start des Falls (Bauch auf 1,1 m über dem Mattenrand)

  // Position seiner Mitte (Hüfte) über der Zeit
  function guyState(T) {
    const z0 = 2.2, zJ = BZ + 0.9;
    if (T < JUMP) { const k = clamp((T - 17.0) / (JUMP - 17.0)); return {pos: V3(0.1, 0.95, lerp(z0, zJ, k)), run: k < 1, phase: (T - 17) * 13, air: 0}; }
    const d = T - JUMP; const topY = CEIL - 1.0;
    let y = 0.95 + VY * d, bonk = 0;
    if (y > topY) { const dd = (y - topY) / VY; y = topY - 0.18 * (1 - Math.exp(-dd * 2.5)); bonk = dd; }
    return {pos: V3(0.1, y, zJ - 0.35 * Math.min(d, 2.5) - 0.05 * Math.max(0, d - 2.5)), run: false, air: d, bonk};
  }

  return {scene, camera, update(shot, T) {
    const drop = shot.id === 'drop_gym';
    const u = guy.userData;
    posePerson(guy, {}); guy.position.set(0, -0.95, 0); guy.rotation.set(0, 0, 0); u.body.rotation.set(0, 0, 0);
    let st;
    if (!drop) {
      st = guyState(T); pivot.position.copy(st.pos); pivot.rotation.set(0, Math.PI, 0);
      if (st.run) { posePerson(guy, {walk: st.phase, walkAmp: 1.4}); u.armR.rotation.x = -0.6; u.armR.userData.fore.rotation.x = -1.2; }
      else { // Absprung: Arm hoch zum Dunk, dann zappeln
        const k = smooth(0, 0.35, st.air); u.armR.rotation.x = -2.9 * k; u.armL.rotation.x = -2.2 * k; u.legL.rotation.x = -0.6 * k; u.legL.userData.knee.rotation.x = 1.2 * k;
        u.pl.forEach((g, i) => { const lg = i ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
        if (st.air > 0.9) { flail(guy, T, 5, smooth(0.9, 1.6, st.air)); pivot.rotation.z = 0.15 * Math.sin(T * 1.3) * smooth(0.9, 2, st.air); }
        if (st.bonk > 0) { pivot.rotation.x = -0.25 * Math.exp(-st.bonk * 2) * Math.sin(st.bonk * 14) - 0.12; u.head.rotation.x = -0.4; }
        mouthOpen(guy, st.air > 0.6 ? 0.8 : 0.3); brows(guy, st.air > 0.6 ? 1 : 0.3, 0);
      }
      matG.position.set(-4.5, 0, -7.5); matG.rotation.set(0, 0.3, 0); matG.scale.set(1, 1, 1);
    } else {
      // Fallen: Bauch nach unten, Arme und Beine gespreizt, Landung auf dem Weichboden
      const top = guyState(30).pos; const t = Math.max(0, T - FALL0);
      let y = Math.max(0.55, top.y - 0.18 - 4.9 * t * t);
      const land = clamp((T - LAND) / 0.6); const squash = land > 0 ? Math.sin(land * Math.PI) * Math.exp(-land * 2) : 0;
      pivot.position.set(top.x, y - squash * 0.18, top.z); pivot.rotation.set(T < FALL0 ? -0.12 : -Math.PI / 2 * smooth(FALL0, FALL0 + 0.5, T), Math.PI, 0);
      flail(guy, T * (T > LAND ? 0.2 : 1.6), 5, T > LAND ? 0.3 : 1); u.armL.rotation.z = -1.4; u.armR.rotation.z = 1.4;
      mouthOpen(guy, T > LAND + 0.3 ? 0.15 : 0.9); brows(guy, 1, 0);
      matG.position.set(top.x, 0, top.z); matG.rotation.set(0, 0, 0); matG.scale.set(1, 1 - squash * 0.45, 1);
    }
    // Ball: verlässt bei JUMP die Hand und fliegt schräg nach oben weiter
    if (!drop) { if (T < JUMP) { guy.updateMatrixWorld(true); ball.position.copy(u.armR.userData.fore.localToWorld(V3(0, -0.36, 0.05))); }
      else { const d = T - JUMP; const s = guyState(JUMP).pos; ball.position.set(s.x + 0.3 * d, s.y + 1.1 + 2.5 * d, s.z - 0.5 * d); if (ball.position.y > CEIL - 0.6) ball.position.y = CEIL - 0.6 - 0.1 * (ball.position.y - CEIL + 0.6); }
      ball.rotation.set(T * 4, T * 2, 0); }
    else ball.position.set(-1.6, 0.12, -3.2);
    // Klasse
    const tgt = pivot.position;
    kids.forEach((q, i) => { const p = q.p; posePerson(p, {}); p.position.set(q.x, 0, q.z); look(p, V3(tgt.x, 0, tgt.z));
      const pu = p.userData; const up = smooth(JUMP + 0.6, JUMP + 1.4, T) || drop ? 1 : 0;
      pu.head.rotation.x = -0.6 * up; mouthOpen(p, 0.3 + 0.3 * Math.max(0, Math.sin(T * 6 + q.s)) * up); brows(p, up, 0);
      if (q.film && (T > JUMP + 0.8 || drop)) { pu.armR.rotation.x = -2.3; pu.armR.userData.fore.rotation.x = -0.4; p.updateMatrixWorld(true); q.ph.visible = true; q.ph.position.copy(pu.armR.userData.fore.localToWorld(V3(0, -0.33, 0.04))); q.ph.lookAt(tgt); }
      else { q.ph.visible = false; if (drop && T > LAND + 0.2) { pu.armL.rotation.z = -2.6; pu.armR.rotation.z = 2.6; } }
      if (drop && T > LAND + 0.2 && q.film && i % 2) { pu.armL.rotation.z = -2.4; }
    });
    // Sportlehrer
    posePerson(coach, {}); coach.position.set(4.2, 0, 1.0); look(coach, V3(tgt.x, 0, tgt.z)); coach.userData.head.rotation.x = -0.5 * smooth(JUMP + 0.5, JUMP + 1.2, T); mouthOpen(coach, 0.6); brows(coach, 1, 0);
    coach.userData.armR.rotation.x = -1.9; coach.userData.armR.userData.fore.rotation.x = -1.3;

    // ---------- Kamera ----------
    camera.fov = 50; let pos, lk; camera.up.set(0, 1, 0);
    const sh = a => V3(noise1(T * 10, 1) * a, noise1(T * 10, 4) * a, 0);
    if (!drop) {
      if (T < JUMP + 0.5) { const k = smooth(17, JUMP + 0.5, T); pos = V3(lerp(1.6, 1.9, k), lerp(2.7, 2.0, k), lerp(5.4, 0.6, k)); lk = V3().lerpVectors(V3(0, 1.4, 0), V3(0, 2.6, BZ), k); camera.fov = 48; }
      else if (T < 21.2) { // von unten: er steigt am Korb vorbei bis zur Decke
        const k = smooth(JUMP + 0.5, 21.2, T); pos = V3(1.7, 1.1, BZ + 3.6); lk = V3(pivot.position.x, Math.min(pivot.position.y + 0.5, CEIL - 0.6), pivot.position.z); camera.fov = lerp(60, 54, k);
        if (T > BONK && T < BONK + 0.5) pos.add(sh(0.05 * (1 - (T - BONK) / 0.5))); }
      else { const k = smooth(21.2, 24, T); pos = V3(lerp(-1.4, -1.7, k), 1.5, lerp(BZ + 4.4, BZ + 4.9, k)); lk = V3(0, lerp(CEIL - 1.6, CEIL - 1.9, k), BZ - 0.2); camera.fov = lerp(48, 52, k); }
    } else {
      const k = smooth(58, 61, T); pos = V3(lerp(3.4, 3.0, k), lerp(0.9, 0.8, k), lerp(-2.0, -2.4, k)); lk = V3(0, lerp(3.4, 0.9, smooth(FALL0 - 0.1, LAND + 0.1, T)), BZ + 0.6); camera.fov = 58;
      if (T > LAND && T < LAND + 0.4) pos.add(sh(0.04 * (1 - (T - LAND) / 0.4)));
    }
    camera.position.copy(pos); camera.lookAt(lk); camera.updateProjectionMatrix();
  }};
}
