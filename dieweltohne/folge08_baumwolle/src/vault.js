// Tresorraum einer Zentralbank: Paletten voller gebündelter Geldscheine. Die Scheine lösen sich auf – zurück bleiben
// leere Folienhüllen, Banderolen aus Papier fallen zu Boden. Alarm, rotes Licht.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeOut, easeIn, posePerson, envMap, tileTex} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {cottonPerson, setCotton, noteTex, flakes, updateFlakes} from './cotton.js';
import {VAULT_ALARM} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const GONE0 = 31.55; // Welle: von vorn nach hinten

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.4;
  scene.background = new THREE.Color('#121416');
  scene.fog = new THREE.Fog('#141618', 18, 48);
  const hemi = new THREE.HemisphereLight('#e8f0ff', '#3a3c40', 0.6); scene.add(hemi);
  const ceilL = [];
  for (let z = 2; z > -30; z -= 6) { const l = new THREE.PointLight('#eaf2ff', 18, 14, 1.5); l.position.set(0, 3.6, z); scene.add(l); ceilL.push(l);
    mesh(new THREE.BoxGeometry(0.3, 0.05, 2.4), new THREE.MeshBasicMaterial({color: '#f4f8ff'}), 0, 3.95, z, scene); }
  const alarmL = [V3(-3.5, 3.6, -4), V3(3.5, 3.6, -14), V3(-3.5, 3.6, -24)].map(p => { const l = new THREE.SpotLight('#ff1a1a', 0, 20, 0.6, 0.4, 1); l.position.copy(p); scene.add(l, l.target); return l; });
  const beacons = alarmL.map(l => mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.2, 14), new THREE.MeshStandardMaterial({color: '#661010', emissive: '#ff1a1a', emissiveIntensity: 0}), l.position.x, l.position.y + 0.25, l.position.z, scene));

  // Raum
  const floorT = tileTex('#5c6066', '#55595f'); floorT.repeat.set(4, 16);
  mesh(new THREE.PlaneGeometry(9, 40), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.45, metalness: 0.2}), 0, 0, -12, scene).rotation.x = -Math.PI / 2;
  const wallM = mat('#6e737a', {roughness: 0.6, metalness: 0.3});
  for (const s of [-1, 1]) { const w = mesh(new THREE.PlaneGeometry(40, 4.2), wallM, s * 4.5, 2.1, -12, scene); w.rotation.y = -s * Math.PI / 2; }
  mesh(new THREE.PlaneGeometry(9, 40), mat('#3b3f45'), 0, 4.2, -12, scene).rotation.x = Math.PI / 2;
  mesh(new THREE.PlaneGeometry(9, 4.2), wallM, 0, 2.1, -32, scene);
  // Tresortür (offen) am Anfang, rechts
  const door = new THREE.Group(); door.position.set(3.9, 2.0, 4.5); scene.add(door);
  const steelM = mat('#9aa1a8', {metalness: 0.9, roughness: 0.25});
  const disc = mesh(new THREE.CylinderGeometry(1.9, 1.9, 0.7, 48), steelM, 0, 0, 0, door); disc.rotation.z = Math.PI / 2;
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; const b = mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.4, 12), steelM, 0.45, Math.cos(a) * 1.55, Math.sin(a) * 1.55, door); b.rotation.z = Math.PI / 2; }
  const wheel = mesh(new THREE.TorusGeometry(0.5, 0.05, 8, 32), steelM, 0.42, 0, 0, door); wheel.rotation.y = Math.PI / 2;
  door.rotation.y = -0.9;

  // Gitterregale und Paletten mit Geldbündeln
  const rackM = mat('#3a4048', {metalness: 0.7, roughness: 0.4});
  const eurM = new THREE.MeshStandardMaterial({map: noteTex('eur'), roughness: 0.85});
  const usdM = new THREE.MeshStandardMaterial({map: noteTex('usd'), roughness: 0.85});
  const bandM = mat('#f2efe6', {roughness: 0.9});
  const wrapM = new THREE.MeshPhysicalMaterial({color: '#e6f0f6', transparent: true, opacity: 0.22, roughness: 0.15, side: THREE.DoubleSide, depthWrite: false});
  const pallets = []; const r = rng(7);
  const bundleGeo = new THREE.BoxGeometry(0.17, 0.11, 0.08);
  for (const side of [-1, 1]) for (let i = 0; i < 6; i++) for (let lvl = 0; lvl < 3; lvl++) {
    const z = 0.5 - i * 4.8, x = side * 3.2, y = 0.12 + lvl * 1.25;
    if (lvl === 0) { // Regalständer
      for (const dz of [-1.9, 1.9]) for (const dx of [-0.6, 0.6]) mesh(new THREE.BoxGeometry(0.06, 3.9, 0.06), rackM, x + dx, 1.95, z + dz, scene);
    }
    mesh(new THREE.BoxGeometry(1.3, 0.05, 4.0), rackM, x, y - 0.03, z, scene);
    for (const dz of [-1.0, 1.0]) {
      const g = new THREE.Group(); g.position.set(x, y, z + dz); scene.add(g);
      mesh(new THREE.BoxGeometry(1.1, 0.1, 1.6), mat('#8a6a44'), 0, 0.05, 0, g); // Holzpalette
      // Bündel (Instanzen): 6 x 18 x 6
      const usd = r() < 0.35;
      const inst = new THREE.InstancedMesh(bundleGeo, usd ? usdM : eurM, 6 * 9 * 6); const m4 = new THREE.Matrix4();
      let n = 0; for (let a = 0; a < 6; a++) for (let b = 0; b < 9; b++) for (let c = 0; c < 6; c++) { m4.makeTranslation(-0.45 + a * 0.18, 0.16 + c * 0.115, -0.72 + b * 0.18); inst.setMatrixAt(n++, m4); }
      inst.castShadow = true; inst.receiveShadow = true; g.add(inst);
      const bands = new THREE.InstancedMesh(new THREE.BoxGeometry(0.03, 0.112, 0.082), bandM, 6 * 9 * 6); n = 0;
      for (let a = 0; a < 6; a++) for (let b = 0; b < 9; b++) for (let c = 0; c < 6; c++) { m4.makeTranslation(-0.45 + a * 0.18, 0.16 + c * 0.115, -0.72 + b * 0.18); bands.setMatrixAt(n++, m4); }
      g.add(bands);
      const wrap = mesh(new THREE.BoxGeometry(1.12, 0.72, 1.66), wrapM, 0, 0.46, 0, g); wrap.castShadow = false;
      pallets.push({g, inst, bands, wrap, z: z + dz, delay: Math.max(0, -(z + dz)) * 0.012 + r() * 0.04});
    }
  }
  // Zählmaschine mit Tisch vorn links
  const table = mesh(new THREE.BoxGeometry(1.6, 0.06, 0.8), steelM, -1.6, 0.9, -3.6, scene);
  mesh(new THREE.BoxGeometry(1.5, 0.88, 0.7), mat('#2b2f35'), -1.6, 0.44, -3.6, scene);
  const counter = mesh(new RoundedBoxGeometry(0.4, 0.3, 0.35, 2, 0.03), mat('#d8dde2'), -1.8, 1.08, -3.6, scene);
  const loose = [];
  for (let i = 0; i < 18; i++) { const n = mesh(new THREE.BoxGeometry(0.17, 0.003, 0.08), eurM, -1.2 + (i % 3) * 0.05, 0.935 + i * 0.0035, -3.65 + (i % 2) * 0.02, scene); n.rotation.y = (i % 5) * 0.1; loose.push(n); }
  // Personal
  const guard = cottonPerson(71, {top: '#1f2a44', jeans: false, pants: '#1a2233', skin: '#d9a47e', hair: '#111'});
  const clerk = cottonPerson(73, {top: '#e8e2d4', jeans: false, pants: '#3a3a3a', skin: '#f1c7a5', hair: '#8a5a2b', ponytail: true});
  scene.add(guard, clerk);
  const dust = flakes(1500, [-3.8, 3.8, 0, 3.6, -28, 3], 0.05); scene.add(dust);
  const puffs = particles(900, 'smoke'); scene.add(puffs);

  const camera = new THREE.PerspectiveCamera(52, 1080 / 1920, 0.05, 120);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    // Verschwinden: Welle von vorn nach hinten
    const srcs = [];
    pallets.forEach(p => { const tg = GONE0 + p.delay; const gone = T >= tg;
      p.inst.visible = !gone;
      
      const sag = smooth(tg, tg + 0.8, T); p.wrap.scale.set(1 + 0.04 * sag, lerp(1, 0.18, easeOut(sag)), 1 + 0.04 * sag); p.wrap.position.y = lerp(0.46, 0.17, easeOut(sag));
      p.bands.scale.y = lerp(1, 0.12, easeIn(sag)); // Banderolen (Papier aus Holz) bleiben und fallen zusammen
      if (T > tg - 0.1 && T < tg + 2.2 && srcs.length < 14) srcs.push({type: 'burstSmoke', pos: V3(p.g.position.x, p.g.position.y + 0.4, p.z), r: 0.9, t0: tg, size: 0.5, rise: 0.25, share: 1}); });
    updateParticles(puffs, srcs, T, V3(0.05, 0, 0.1));
    // weiße Fasern statt grauer Rauch: Farbe der Partikel aufhellen
    { const C = puffs.geometry.attributes.aColor.array; for (let i = 0; i < C.length; i += 4) { if (C[i + 3] > 0) { C[i] = 0.95; C[i + 1] = 0.94; C[i + 2] = 0.9; C[i + 3] *= 0.8; } } }
    loose.forEach(n => n.visible = T < GONE0);
    dust.visible = T > GONE0; updateFlakes(dust, T, 0.12, smooth(GONE0, GONE0 + 1.0, T) * (1 - smooth(36, 39, T) * 0.6), [0.05, 0.1]);
    // Alarm
    const al = T > VAULT_ALARM ? 1 : 0;
    alarmL.forEach((l, i) => { const a = T * 6 + i; l.intensity = al * 60; l.target.position.set(l.position.x + Math.cos(a) * 3, 0, l.position.z + Math.sin(a) * 3); beacons[i].material.emissiveIntensity = al * (1.5 + Math.sin(T * 12) * 1); });
    ceilL.forEach(l => l.intensity = al ? 7 : 18);
    hemi.intensity = al ? 0.35 : 0.6;
    // Personal
    guard.position.set(1.4, 0, -6 + smooth(32.5, 36, T) * 3.0); guard.rotation.set(0, (T > 32.5 ? 0.3 : -1.4), 0); posePerson(guard, {walk: T > 32.5 && T < 36 ? T * 9 : 0, walkAmp: T > 32.5 && T < 36 ? 1.2 : 0});
    { const u = guard.userData; const k = smooth(31.7, 32.2, T); u.head.rotation.y = -0.6 * k * (T < 32.5 ? 1 : 0); u.armR.rotation.x = T > 32.5 ? -1.6 : u.armR.rotation.x; }
    setCotton(guard, true);
    clerk.position.set(-1.6, 0, -4.35); clerk.rotation.set(0, 0, 0); posePerson(clerk, {});
    { const u = clerk.userData; const k = smooth(31.6, 32.0, T); u.armL.rotation.x = lerp(-0.9, -2.3, k); u.armR.rotation.x = lerp(-0.9, -2.3, k); u.armL.userData.fore.rotation.x = lerp(-0.6, -1.4, k); u.armR.userData.fore.rotation.x = lerp(-0.6, -1.4, k);
      u.torso.rotation.x = -0.15 * k; u.head.rotation.y = 0.5 * smooth(32.6, 33.2, T); }
    setCotton(clerk, true);
    // Kamera: langsame Fahrt durch den Gang
    const u = smooth(31, 39, T);
    camera.position.set(lerp(-1.0, -0.6, u), lerp(1.9, 1.7, u), lerp(3.2, 0.4, u)); camera.lookAt(lerp(-3.0, -2.6, u), lerp(1.0, 1.2, u), lerp(-3.5, -7, u));
    camera.updateProjectionMatrix();
  }};
}
