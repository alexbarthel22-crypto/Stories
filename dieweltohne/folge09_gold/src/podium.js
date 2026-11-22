// Siegerehrung in einer Halle. Der Sieger beißt auf seine Goldmedaille – und plötzlich ist sie silbern.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, envMap} from './lib.js';
import {GOLD, SILVER, glitter, updateGlitter} from './gold.js';
import {MEDAL_GONE} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.background = new THREE.Color('#0c0e14');
  scene.fog = new THREE.Fog('#0c0e14', 20, 60);
  scene.add(new THREE.HemisphereLight('#9fb4ff', '#202028', 0.35));
  const spot = new THREE.SpotLight('#fff4e0', 260, 30, 0.42, 0.5, 1.2); spot.position.set(0, 12, 8); spot.target.position.set(0, 1.2, 0); spot.castShadow = true; spot.shadow.mapSize.set(2048, 2048); scene.add(spot, spot.target);
  const rim = new THREE.SpotLight('#9fc0ff', 120, 30, 0.5, 0.6, 1.2); rim.position.set(-6, 9, -8); rim.target.position.set(0, 1.5, 0); scene.add(rim, rim.target);
  const key = new THREE.PointLight('#fff0dc', 8, 10, 1.5); key.position.set(1.0, 2.6, 2.6); scene.add(key);

  // Boden: blauer Hallenboden, Bühnenteppich
  mesh(new THREE.PlaneGeometry(80, 80), mat('#1d3a6a', {roughness: 0.5}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(10, 6), mat('#7a1424', {roughness: 0.95}), 0, 0.005, 0.5, scene).rotation.x = -Math.PI / 2;
  // Siegertreppchen
  const podM = mat('#f2f2f0', {roughness: 0.5});
  const numT = n => canvasTex(256, 256, (g) => { g.fillStyle = '#f2f2f0'; g.fillRect(0, 0, 256, 256); g.fillStyle = '#1d3a6a'; g.font = '900 170px sans-serif'; g.textAlign = 'center'; g.fillText(String(n), 128, 190); });
  const PODS = [[0, 0.8, 1], [-1.25, 0.55, 2], [1.25, 0.38, 3]];
  for (const [x, h, n] of PODS) {
    const front = new THREE.MeshStandardMaterial({map: numT(n), roughness: 0.5});
    mesh(new THREE.BoxGeometry(1.2, h, 1.0), [podM, podM, podM, podM, front, podM], x, h / 2, 0, scene);
  }
  // Rückwand mit Flaggen (erfundene Farben) und Anzeigetafel
  mesh(new THREE.PlaneGeometry(30, 12), mat('#121620', {roughness: 0.9}), 0, 6, -6, scene);
  const flagT = (a, b2, c) => canvasTex(300, 200, g => { g.fillStyle = a; g.fillRect(0, 0, 300, 67); g.fillStyle = b2; g.fillRect(0, 67, 300, 67); g.fillStyle = c; g.fillRect(0, 134, 300, 66); });
  const flags = [];
  [[0, 4.6, ['#2a63c9', '#f4f4f4', '#2a63c9']], [-2.4, 4.0, ['#1f8a4c', '#f2d23a', '#1f8a4c']], [2.4, 3.6, ['#c8202e', '#f4f4f4', '#c8202e']]].forEach(([x, y, c]) => {
    const f = mesh(new THREE.PlaneGeometry(1.5, 1.0, 12, 4), new THREE.MeshStandardMaterial({map: flagT(...c), roughness: 0.8, side: THREE.DoubleSide}), x, y, -5.0, scene); flags.push(f);
    mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.8, 6), mat('#999', {metalness: 0.8}), x - 0.8, y - 0.2, -5.0, scene); });
  const boardT = canvasTex(1024, 256, g => { g.fillStyle = '#05070c'; g.fillRect(0, 0, 1024, 256); g.fillStyle = '#ffd25a'; g.font = '800 80px sans-serif'; g.textAlign = 'center'; g.fillText('SIEGEREHRUNG', 512, 120); g.fillStyle = '#9fb4ff'; g.font = '600 50px sans-serif'; g.fillText('100 M · FINALE', 512, 200); });
  mesh(new THREE.PlaneGeometry(6, 1.5), new THREE.MeshBasicMaterial({map: boardT}), 0, 7.6, -5.9, scene);
  // Zuschauer: Ränge hinter der Kamera und seitlich (Instanzen)
  const crowdG = new THREE.CapsuleGeometry(0.22, 0.4, 3, 8);
  const crowd = new THREE.InstancedMesh(crowdG, new THREE.MeshStandardMaterial({roughness: 0.9}), 900);
  { const r = rng(5), m4 = new THREE.Matrix4(), c = new THREE.Color(); let n = 0;
    for (let row = 0; row < 10; row++) for (let i = 0; i < 90 && n < 900; i++) { const a = -1.25 + i / 90 * 2.5, R = 14 + row * 1.1;
      const x = Math.sin(a) * R, z = -Math.cos(a) * R * 0.55 - 2; if (z > -3) continue;
      m4.makeTranslation(x, 1 + row * 0.75, z); crowd.setMatrixAt(n, m4); c.setHSL(r(), 0.5, 0.35 + r() * 0.25); crowd.setColorAt(n, c); n++; }
    crowd.count = n; }
  scene.add(crowd);
  // Fotografen-Blitze (Lichtpunkte in den Rängen)
  const flashes = []; { const r = rng(9); for (let i = 0; i < 26; i++) { const a = -1.1 + r() * 2.2, R = 14 + r() * 8;
      const m = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 6), new THREE.MeshBasicMaterial({color: '#ffffff', transparent: true, opacity: 0})); m.position.set(Math.sin(a) * R, 1.6 + r() * 6, -Math.cos(a) * R * 0.55 - 2); scene.add(m); flashes.push({m, ph: r() * 10, f: 0.7 + r() * 1.5}); } }

  // Athleten
  const mk = (seed, top, skin, hair) => { const p = makePerson(seed, {top, pants: top, skin, hair, shoe: '#f2f2f2', height: 1.02}); scene.add(p); return p; };
  const a1 = mk(61, '#2a63c9', '#a8714f', '#111'), a2 = mk(66, '#1f8a4c', '#f1c7a5', '#5a3b22'), a3 = mk(68, '#c8202e', '#d9a47e', '#2a1d15');
  // Medaillen: Scheibe + Band
  const medal = (p, m) => { const g = new THREE.Group(); p.userData.torso.add(g);
    const band = mesh(new THREE.BoxGeometry(0.04, 0.26, 0.01), mat('#c8202e'), 0, 0.5, 0.13, g); band.rotation.x = -0.15;
    const disc = mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.008, 28), m, 0, 0.36, 0.145, g); disc.rotation.x = Math.PI / 2;
    return {g, disc}; };
  const m2 = medal(a2, SILVER), m3 = medal(a3, new THREE.MeshStandardMaterial({color: '#b0703a', metalness: 1, roughness: 0.3}));
  // Siegermedaille in der rechten Hand (zum Reinbeißen), Band hängt zum Hals
  const handMedal = new THREE.Group(); a1.userData.armR.userData.fore.add(handMedal); handMedal.position.set(0, -0.34, 0.03);
  const disc1 = mesh(new THREE.CylinderGeometry(0.065, 0.065, 0.01, 32), GOLD, 0, 0, 0, handMedal); disc1.rotation.x = Math.PI / 2;
  const disc1S = mesh(new THREE.CylinderGeometry(0.065, 0.065, 0.01, 32), SILVER, 0, 0, 0, handMedal); disc1S.rotation.x = Math.PI / 2;
  const rib = mesh(new THREE.BoxGeometry(0.035, 0.2, 0.008), mat('#c8202e'), 0, 0.12, -0.01, handMedal);
  const gl = glitter(400, 0.035); scene.add(gl);

  const camera = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.05, 200); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    const gone = T >= MEDAL_GONE;
    disc1.visible = !gone; disc1S.visible = gone;
    flags.forEach((f, i) => { const P = f.geometry.attributes.position; for (let k = 0; k < P.count; k++) { const x = P.getX(k); P.setZ(k, Math.sin(x * 3 + T * 3 + i) * 0.05 * (x + 0.75)); } P.needsUpdate = true; });
    flashes.forEach(fl => { const ph = (T * fl.f + fl.ph) % 1; fl.m.material.opacity = ph < 0.06 ? 1 : 0; });
    // Sieger: Medaille hoch – reinbeißen – Schreck
    a1.position.set(0, 0.8, 0); a1.rotation.set(0, 0, 0); posePerson(a1, {});
    const u = a1.userData;
    const bite = smooth(17.2, 17.9, T) * (1 - smooth(MEDAL_GONE + 0.5, MEDAL_GONE + 1.2, T)), look = smooth(MEDAL_GONE + 0.5, MEDAL_GONE + 1.2, T), show = smooth(21.0, 21.8, T);
    u.armL.rotation.z = lerp(-2.5, -0.2, smooth(17.0, 17.6, T)); u.armL.rotation.x = 0; u.armL.userData.fore.rotation.x = -0.2; // Jubel links
    const raise = smooth(17.0, 17.5, T);
    u.armR.rotation.x = lerp(-0.2, -1.25, raise) + lerp(0, -0.25, bite) + lerp(0, 0.25, look * (1 - show)) + lerp(0, -1.2, show);
    u.armR.rotation.z = lerp(0.1, -0.25, raise) + lerp(0, -0.2, bite) + 0.35 * show;
    u.armR.userData.fore.rotation.x = lerp(-0.3, -1.0, raise) + lerp(0, -0.75, bite) + lerp(0, 0.45, look * (1 - show)) + lerp(0, 0.6, show);
    u.head.rotation.x = 0.4 * look * (1 - show) + 0.12 * bite; u.head.rotation.y = -0.2 * bite + 0.35 * show;
    handMedal.rotation.set(-1.2 * look * (1 - show), 0, 0);
    // Zweiter und Dritter: schauen rüber, der Zweite vergleicht seine Medaille
    a2.position.set(-1.25, 0.55, 0); a2.rotation.set(0, 0.15, 0); posePerson(a2, {}); a3.position.set(1.25, 0.38, 0); a3.rotation.set(0, -0.15, 0); posePerson(a3, {});
    const cmp = smooth(MEDAL_GONE + 1.4, MEDAL_GONE + 2.2, T), grin = smooth(MEDAL_GONE + 2.8, MEDAL_GONE + 3.4, T);
    a2.userData.head.rotation.y = 0.6 * smooth(MEDAL_GONE + 0.6, MEDAL_GONE + 1.2, T); a2.userData.armR.rotation.x = -0.9 * cmp; a2.userData.armR.userData.fore.rotation.x = -0.8 * cmp;
    a2.userData.torso.rotation.x = Math.sin(T * 20) * 0.03 * grin;
    a3.userData.head.rotation.y = -0.55 * smooth(MEDAL_GONE + 0.8, MEDAL_GONE + 1.4, T); a3.userData.armL.rotation.x = -1.2 * grin; a3.userData.armL.userData.fore.rotation.x = -1.7 * grin; a3.userData.torso.rotation.x = 0.2 * grin + Math.sin(T * 22) * 0.04 * grin;
    a1.updateMatrixWorld(true);
    updateGlitter(gl, [disc1.getWorldPosition(new THREE.Vector3())], T - MEDAL_GONE, 0.9, 0.08, 0.15);
    // Kamera: frontal, fährt zum Sieger, Nahaufnahme der Medaille, dann wieder weiter
    const k1 = smooth(17, 18.2, T), k2 = smooth(21.0, 22.5, T);
    const near = V3(0.75, 2.35, 2.1), far = V3(0.3, 1.9, 7.4);
    const pos = far.clone().lerp(near, k1 * (1 - k2)).lerp(V3(0.4, 1.9, 7.6), k2);
    camera.position.set(pos.x + noise1(T, 1) * 0.01, pos.y, pos.z);
    const tgt = V3(0, 1.4, 0).lerp(V3(0.08, 2.3, 0), k1 * (1 - k2)).lerp(V3(0, 1.5, 0), k2);
    camera.lookAt(tgt); camera.updateProjectionMatrix();
  }};
}
