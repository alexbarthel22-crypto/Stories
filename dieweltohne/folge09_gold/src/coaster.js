// Freizeitpark, Sturzachterbahn: Der Zug fährt den Lifthügel hoch und kippt über die Kante – dann fällt die Steuerung aus.
// Die Bremsen greifen (sie sind so gebaut, dass sie ohne Strom schließen): Der Zug hängt in 60 m Höhe senkrecht über dem Abgrund.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, skyDome, makePerson, posePerson, envMap} from './lib.js';
import {CHIP_DEAD, BRAKE} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.45;
  scene.fog = new THREE.Fog('#cfe0ee', 120, 700);
  scene.add(skyDome('#2f6fc2', '#86b6e4', '#e4eef4', 900));
  scene.add(new THREE.HemisphereLight('#e6f0ff', '#5d6a4a', 1.0));
  const sun = new THREE.DirectionalLight('#fff3dc', 2.6); sun.position.set(40, 90, 50); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -80, right: 80, top: 80, bottom: -80, near: 1, far: 300}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.05; scene.add(sun);
  // Boden: Wiese, Wege
  mesh(new THREE.PlaneGeometry(1600, 1600), mat('#6f9a4a', {roughness: 1}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const pathM = mat('#9a8e74', {roughness: 0.95});
  for (const [x, z, w, l, r] of [[0, 18, 8, 160, 0], [-30, -20, 6, 120, 1.2], [40, -10, 6, 100, -0.8]]) { const p = mesh(new THREE.PlaneGeometry(w, l), pathM, x, 0.02, z, scene); p.rotation.set(-Math.PI / 2, 0, r); p.castShadow = false; }
  // Strecke (Seitenansicht in der x-y-Ebene): Lift 45°, kurze Kuppe, senkrechter Fall
  const pts = [];
  for (let x = -62; x <= -6; x += 2) pts.push(V3(x, x + 64, 0));
  for (let a = 0; a <= 1; a += 0.1) { const ang = Math.PI * 0.75 - a * Math.PI * 0.25; pts.push(V3(-2 + Math.cos(ang) * 5.66 * 0.0 + lerp(-6, 0, a), lerp(58, 60, Math.sin(a * Math.PI / 2)), 0)); }
  for (let x = 0.5; x <= 4; x += 0.5) pts.push(V3(x, 60, 0));
  for (let a = 0.1; a <= 1.001; a += 0.1) { const ang = Math.PI / 2 - a * Math.PI / 2; pts.push(V3(4 + Math.cos(ang) * 6 - 0, 54 + Math.sin(ang) * 6, 0).add(V3(0, 0, 0))); }
  for (let y = 52; y >= 10; y -= 3) pts.push(V3(10, y, 0));
  for (let a = 0.1; a <= 1.001; a += 0.1) { const ang = Math.PI - a * Math.PI / 2; pts.push(V3(18 + Math.cos(ang) * 8, 10 - Math.sin(ang) * 8 + 0, 0)); }
  for (let x = 20; x <= 70; x += 5) pts.push(V3(x, 2, 0));
  const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
  const railM = mat('#e2342f', {metalness: 0.5, roughness: 0.35}), supM = mat('#d8d4cc', {metalness: 0.4, roughness: 0.5});
  const W = 1.5;
  for (const s of [-1, 1]) { const rp = curve.getSpacedPoints(400).map(p => p.clone().add(V3(0, 0, s * W))); mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(rp), 600, 0.14, 8), railM, 0, 0, 0, scene); }
  const spine = mesh(new THREE.TubeGeometry(curve, 600, 0.35, 8), railM, 0, -0.45, 0, scene);
  // Querträger und Stützen
  { const sp = curve.getSpacedPoints(160); sp.forEach((p, i) => { const tie = mesh(new THREE.BoxGeometry(0.15, 0.15, W * 2 + 0.3), supM, p.x, p.y - 0.25, p.z, scene); tie.castShadow = false;
      if (i % 6 === 0 && p.y > 4 && !(p.x > 6 && p.x < 14)) { const h = p.y - 0.6; mesh(new THREE.CylinderGeometry(0.45, 0.6, h, 10), supM, p.x, h / 2, 0, scene); } }); }
  mesh(new THREE.CylinderGeometry(0.5, 0.7, 54, 10), supM, 14, 27, -5, scene); mesh(new THREE.BoxGeometry(0.4, 0.4, 5), supM, 12, 46, -2.5, scene);
  // Zug: ein breiter Wagen mit zwei Reihen
  const train = new THREE.Group(); scene.add(train);
  const carM = mat('#1b2a4a', {metalness: 0.3, roughness: 0.4}), seatM = mat('#222', {roughness: 0.8}), barM = mat('#f2c230', {roughness: 0.5});
  mesh(new RoundedBoxGeometry(3.2, 0.6, W * 2 + 0.8, 3, 0.15), carM, 0, 0.6, 0, train);
  mesh(new THREE.BoxGeometry(0.2, 0.25, W * 2 + 0.9), mat('#e2342f'), 1.6, 0.85, 0, train);
  const riders = [];
  const COLS = ['#e2b23a', '#3f6fb5', '#d94b3d', '#2f8f6b', '#7b4fa0', '#e07a2f', '#24343f', '#c23b6a', '#4aa3c7', '#e8e2d4'];
  for (let row = 0; row < 2; row++) for (let i = 0; i < 5; i++) {
    const z = -1.8 + i * 0.9, x = 0.9 - row * 1.5;
    mesh(new RoundedBoxGeometry(0.6, 0.9, 0.7, 2, 0.1), seatM, x - 0.38, 1.2, z, train);
    const p = makePerson(200 + row * 10 + i, {top: COLS[(row * 5 + i) % 10]}); p.position.set(x - 0.2, 0.2, z); p.rotation.y = -Math.PI / 2; p.rotation.y = Math.PI / 2; train.add(p);
    const bar = mesh(new THREE.TorusGeometry(0.26, 0.05, 8, 16, Math.PI), barM, x + 0.05, 1.55, z, train); bar.rotation.set(0, Math.PI / 2, Math.PI / 2);
    riders.push(p);
  }
  // Riesenrad und Karussell mit Lichtern
  const wheel = new THREE.Group(); wheel.position.set(-55, 32, -60); scene.add(wheel);
  const bulbM = new THREE.MeshStandardMaterial({color: '#fff3c0', emissive: '#ffd36a', emissiveIntensity: 2.2});
  mesh(new THREE.TorusGeometry(28, 0.5, 8, 64), supM, 0, 0, 0, wheel);
  for (let i = 0; i < 24; i++) { const a = i / 24 * Math.PI * 2; const sp = mesh(new THREE.BoxGeometry(0.3, 28, 0.3), supM, Math.cos(a) * 14, Math.sin(a) * 14, 0, wheel); sp.rotation.z = a + Math.PI / 2;
    const gd = mesh(new RoundedBoxGeometry(2.2, 2.4, 2.2, 2, 0.3), mat(COLS[i % 10]), Math.cos(a) * 28, Math.sin(a) * 28 - 1.6, 0, wheel); gd.userData.gondola = true;
    for (let k = 0; k < 3; k++) mesh(new THREE.SphereGeometry(0.35, 8, 6), bulbM, Math.cos(a + k * 0.08) * 28.6, Math.sin(a + k * 0.08) * 28.6, 0.6, wheel); }
  for (const s of [-1, 1]) { const l = mesh(new THREE.BoxGeometry(0.8, 36, 0.8), supM, s * 9, 15, -60, scene); l.rotation.z = s * 0.28; l.position.y = 15; }
  const caro = new THREE.Group(); caro.position.set(30, 0, -30); scene.add(caro);
  mesh(new THREE.CylinderGeometry(9, 9, 0.8, 32), mat('#f2efe6'), 0, 0.4, 0, caro);
  const roof = mesh(new THREE.ConeGeometry(10, 4, 24), mat('#d94b3d'), 0, 7, 0, caro);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; mesh(new THREE.CylinderGeometry(0.08, 0.08, 4.6, 6), mat('#e8c64a', {metalness: 0.7}), Math.cos(a) * 7, 2.8, Math.sin(a) * 7, caro);
    mesh(new THREE.SphereGeometry(0.3, 8, 6), bulbM, Math.cos(a) * 9.6, 5.2, Math.sin(a) * 9.6, caro); }
  // Bäume, Buden, Besucher am Boden
  { const r = rng(4), trunk = mat('#5a4330'), leaf = mat('#4f7a3a', {roughness: 0.9});
    for (let i = 0; i < 60; i++) { const x = -150 + r() * 300, z = -150 + r() * 220; if (Math.abs(z) < 12 && x > -70 && x < 75) continue; mesh(new THREE.CylinderGeometry(0.3, 0.4, 4, 6), trunk, x, 2, z, scene); mesh(new THREE.IcosahedronGeometry(2.5 + r() * 1.5, 1), leaf, x, 5.5, z, scene); }
    for (let i = 0; i < 10; i++) { const x = -40 + i * 9, z = 26; mesh(new THREE.BoxGeometry(5, 3, 4), mat(COLS[i % 10]), x, 1.5, z, scene); mesh(new THREE.ConeGeometry(3.6, 1.6, 4), mat('#f2efe6'), x, 3.8, z, scene).rotation.y = Math.PI / 4; } }
  const visitors = []; for (let i = 0; i < 26; i++) { const p = makePerson(300 + i); const r = rng(i + 70); p.position.set(-30 + r() * 70, 0, 8 + r() * 14); p.rotation.y = Math.PI + (r() - 0.5); scene.add(p); visitors.push(p); }

  const L = curve.getLength();
  // Position des Zuges entlang der Strecke (u = 0..1 des Kurvenparameters über Bogenlänge)
  const sTop = (() => { let best = 0, d = 1e9; for (let i = 0; i <= 2000; i++) { const p = curve.getPointAt(i / 2000); const dd = Math.hypot(p.x - 9.4, p.y - 56.5); if (dd < d) { d = dd; best = i / 2000; } } return best; })();
  function placeTrain(u) { const p = curve.getPointAt(u), tg = curve.getTangentAt(u); train.position.copy(p).add(V3(0, 0.15, 0)); train.rotation.set(0, 0, Math.atan2(tg.y, tg.x)); }
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 3000); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    // Zug: Lift mit konstanter Geschwindigkeit, dann über die Kante bis zur Haltebremse
    const uStart = sTop - 14 / L, climb = smooth(31.0, 32.8, T), tip = smooth(32.6, BRAKE, T);
    const u = lerp(uStart, sTop - 2.5 / L, climb) + (2.5 / L) * tip;
    placeTrain(u + Math.sin(clamp((T - BRAKE) * 6) * Math.PI) * 0.0004 * (T > BRAKE));
    // Riesenrad dreht, bis die Steuerung stirbt; Lichter gehen aus
    const dead = T >= CHIP_DEAD;
    const ang = T < CHIP_DEAD ? T * 0.05 : CHIP_DEAD * 0.05 + (1 - Math.exp(-(T - CHIP_DEAD) * 2)) * 0.012;
    wheel.rotation.z = ang; wheel.children.forEach(c => { if (c.userData.gondola) c.rotation.z = -ang; });
    caro.rotation.y = T < CHIP_DEAD ? T * 0.6 : CHIP_DEAD * 0.6 + (1 - Math.exp(-(T - CHIP_DEAD) * 0.8)) * 0.6;
    bulbM.emissiveIntensity = dead ? 0 : 2.2;
    // Fahrgäste: Arme hoch, nach dem Halt Panik
    const panic = smooth(BRAKE + 0.6, BRAKE + 1.4, T);
    riders.forEach((p, i) => { posePerson(p, {}); const q = p.userData;
      q.legL.rotation.x = -1.45; q.legR.rotation.x = -1.45; q.legL.userData.knee.rotation.x = 1.4 + Math.sin(T * 9 + i) * 0.25 * panic; q.legR.userData.knee.rotation.x = 1.4 + Math.sin(T * 8 + i * 2) * 0.25 * panic;
      const up = T < 32.9 ? 1 : 1 - smooth(32.9, 33.4, T);
      q.armL.rotation.x = -2.8 * up - 0.6 * (1 - up) + Math.sin(T * 7 + i) * 0.4 * panic; q.armR.rotation.x = -2.8 * up - 0.6 * (1 - up) + Math.sin(T * 6 + i * 3) * 0.4 * panic;
      q.armL.userData.fore.rotation.x = -0.6 * (1 - up); q.armR.userData.fore.rotation.x = -0.6 * (1 - up);
      q.head.rotation.x = 0.4 * panic + Math.sin(T * 5 + i) * 0.1 * panic; });
    visitors.forEach((p, i) => { posePerson(p, {}); p.userData.head.rotation.x = -0.5 * smooth(CHIP_DEAD + 0.5, CHIP_DEAD + 1.5, T); if (i % 3 === 0) { const k = smooth(BRAKE + 1, BRAKE + 2, T); p.userData.armR.rotation.x = -2.4 * k; } });
    // Kamera
    camera.fov = 50;
    if (T < 34.2) { // weit von der Seite: wie hoch das ist
      const k = smooth(31, 34.2, T);
      camera.position.set(lerp(-22, -10, k), lerp(26, 34, k), lerp(44, 34, k)); camera.lookAt(lerp(-6, 4, k), lerp(46, 50, k), 0);
    } else if (T < 36.6) { // erste Reihe: Blick senkrecht nach unten
      train.updateMatrixWorld(true);
      const p = train.localToWorld(V3(1.25, 2.0, 1.35)), d = train.localToWorld(V3(5, -1.0, 2.2)).sub(p);
      camera.fov = 62; camera.position.copy(p).add(V3(noise1(T * 4, 1) * 0.02, 0, noise1(T * 4, 2) * 0.02)); camera.lookAt(p.clone().add(d.multiplyScalar(1)).add(V3(0, -3, 0)));
    } else { // nah von vorn-unten an den hängenden Wagen
      const k = smooth(36.6, 39, T);
      camera.position.set(lerp(20, 22, k), lerp(50, 47, k), lerp(16, 20, k)); camera.lookAt(7, 56, 0);
    }
    camera.updateProjectionMatrix();
  }};
}
