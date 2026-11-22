// Stufe 2: Erstes Date im Steakhaus. Der Kellner stellt den Teller ab und hebt die Silberglocke – der Teller ist leer.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, envMap} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {CLOCHE} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

function seat(p, seatY = 0.5) { // sitzt auf einem Stuhl, Blick in +z (lokal)
  const u = p.userData, h = u.h;
  posePerson(p, {}); p.position.y = seatY - 0.92 * h;
  u.legL.rotation.x = u.legR.rotation.x = -1.5; u.legL.userData.knee.rotation.x = u.legR.userData.knee.rotation.x = 1.45;
  u.pl.forEach((g, i) => { const lg = i ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
  u.pl.forEach(g => { g.userData.low.visible = false; });
  if (!u.shins) { u.shins = [u.legL, u.legR].map((lg, i) => mesh(new THREE.CapsuleGeometry(0.066, 0.3, 4, 8), u.pl[i].userData.low.material, 0, -0.2, 0, lg.userData.knee)); }
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.25;
  scene.background = new THREE.Color('#120c08');
  scene.fog = new THREE.Fog('#160e09', 9, 26);
  const hemi = new THREE.HemisphereLight('#ffcf9a', '#2a1a10', 0.35); scene.add(hemi);
  const key = new THREE.SpotLight('#ffd7a8', 26, 9, 0.7, 0.6, 1.5); key.position.set(0.3, 3.0, 0.2); key.target.position.set(0, 0.75, 0); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); scene.add(key, key.target);
  const candleL = new THREE.PointLight('#ffb35a', 2.2, 4, 1.7); candleL.position.set(-0.12, 0.98, 0.05); scene.add(candleL);
  // Raum: Holzboden, dunkle Wände mit Holzvertäfelung, Fenster mit Lichtern der Stadt
  const floorT = canvasTex(512, 512, (g, w, h) => { const r = rng(2); for (let i = 0; i < 16; i++) { const v = 70 + r() * 30; g.fillStyle = `rgb(${v + 30},${v + 8},${v - 20})`; g.fillRect(0, i * 32, w, 31); for (let k = 0; k < 40; k++) { g.fillStyle = `rgba(40,20,5,${r() * 0.15})`; g.fillRect(r() * w, i * 32 + r() * 30, 30 + r() * 80, 1.5); } } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(6, 6);
  mesh(new THREE.PlaneGeometry(30, 30), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.6}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const wallM = mat('#3a2418', {roughness: 0.85}), panelM = mat('#5a3622', {roughness: 0.6});
  mesh(new THREE.BoxGeometry(14, 4, 0.2), wallM, 0, 2, -3.6, scene); mesh(new THREE.BoxGeometry(14, 1.1, 0.24), panelM, 0, 0.55, -3.55, scene);
  mesh(new THREE.BoxGeometry(0.2, 4, 14), wallM, -4.5, 2, 0, scene); mesh(new THREE.BoxGeometry(0.24, 1.1, 14), panelM, -4.45, 0.55, 0, scene);
  // Fenster mit unscharfen Stadtlichtern
  const cityT = canvasTex(512, 384, (g, w, h) => { g.fillStyle = '#0b1020'; g.fillRect(0, 0, w, h); const r = rng(8);
    for (let i = 0; i < 140; i++) { const x = r() * w, y = h * 0.3 + r() * h * 0.7, rad = 4 + r() * 14; const gr = g.createRadialGradient(x, y, 0, x, y, rad); const c = r() < 0.6 ? '255,190,110' : '170,200,255'; gr.addColorStop(0, `rgba(${c},0.9)`); gr.addColorStop(1, `rgba(${c},0)`); g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2); } });
  for (const x of [-2.4, 1.6]) { mesh(new THREE.PlaneGeometry(2.6, 2.0), new THREE.MeshBasicMaterial({map: cityT}), x, 2.0, -3.48, scene); mesh(new THREE.BoxGeometry(2.8, 0.1, 0.1), panelM, x, 0.96, -3.45, scene); }
  // Pendelleuchten
  const lampM = new THREE.MeshStandardMaterial({color: '#2a1a0f', emissive: '#ffb060', emissiveIntensity: 1.6});
  for (const [x, z] of [[0, 0], [-2.8, -1.8], [2.8, -1.6], [-2.6, 2.2]]) { mesh(new THREE.CylinderGeometry(0.004, 0.004, 1.6, 4), mat('#111'), x, 3.2, z, scene); mesh(new THREE.ConeGeometry(0.18, 0.2, 16, 1, true), lampM, x, 2.35, z, scene); }
  // Tische
  const clothM = mat('#f3efe6', {roughness: 0.9}), woodM = mat('#4a2c1a', {roughness: 0.5});
  const table = (x, z, r = 0.55) => { const t = new THREE.Group(); t.position.set(x, 0, z); scene.add(t);
    mesh(new THREE.CylinderGeometry(r, r, 0.04, 32), clothM, 0, 0.76, 0, t); mesh(new THREE.CylinderGeometry(r + 0.01, r + 0.06, 0.22, 32, 1, true), clothM, 0, 0.64, 0, t);
    mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.6, 8), woodM, 0, 0.3, 0, t); return t; };
  const chair = (x, z, ry) => { const c = new THREE.Group(); c.position.set(x, 0, z); c.rotation.y = ry; scene.add(c);
    mesh(new RoundedBoxGeometry(0.45, 0.06, 0.45, 2, 0.02), woodM, 0, 0.47, 0, c); mesh(new RoundedBoxGeometry(0.45, 0.6, 0.05, 2, 0.02), woodM, 0, 0.78, -0.21, c);
    for (const [a, b] of [[-0.19, -0.19], [0.19, -0.19], [-0.19, 0.19], [0.19, 0.19]]) mesh(new THREE.BoxGeometry(0.04, 0.47, 0.04), woodM, a, 0.235, b, c); return c; };
  table(0, 0); chair(-0.75, 0, Math.PI / 2); chair(0.75, 0, -Math.PI / 2);
  for (const [x, z] of [[-2.8, -1.8], [2.8, -1.6], [-2.6, 2.2]]) { table(x, z); chair(x - 0.75, z, Math.PI / 2); chair(x + 0.75, z, -Math.PI / 2);
    mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.12, 8), mat('#f5f0e0'), x, 0.84, z, scene); const fl = new THREE.PointLight('#ffb35a', 0.8, 2.5, 1.8); fl.position.set(x, 0.95, z); scene.add(fl); }
  // Gedeck: Kerze, Weingläser, Besteck
  mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.16, 10), mat('#f5f0e0'), -0.12, 0.86, 0.05, scene);
  const flame = mesh(new THREE.SphereGeometry(0.014, 8, 6), new THREE.MeshBasicMaterial({color: '#ffd27a'}), -0.12, 0.955, 0.05, scene); flame.scale.y = 2;
  const glassM = new THREE.MeshPhysicalMaterial({color: '#ffffff', transparent: true, opacity: 0.25, roughness: 0.05});
  for (const s of [-1, 1]) { mesh(new THREE.CylinderGeometry(0.035, 0.03, 0.09, 12, 1, true), glassM, s * 0.28, 0.92, -0.18, scene); mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.1, 6), glassM, s * 0.28, 0.83, -0.18, scene);
    mesh(new THREE.CylinderGeometry(0.032, 0.03, 0.04, 12), mat('#5a0d1a', {roughness: 0.2}), s * 0.28, 0.9, -0.18, scene);
    mesh(new THREE.CylinderGeometry(0.13, 0.12, 0.015, 24), mat('#ffffff', {roughness: 0.3}), s * 0.32, 0.785, 0.02, scene); }
  const silverM = mat('#d8dadc', {metalness: 1, roughness: 0.2});
  // Teller mit Glocke (kommt mit dem Kellner)
  const plateG = new THREE.Group(); scene.add(plateG);
  mesh(new THREE.CylinderGeometry(0.16, 0.13, 0.02, 32), mat('#ffffff', {roughness: 0.25}), 0, 0, 0, plateG);
  for (let i = 0; i < 3; i++) mesh(new THREE.SphereGeometry(0.02, 8, 6), mat('#3f7a2a'), 0.08 - i * 0.03, 0.015, 0.06, plateG).scale.y = 0.5; // nur Garnitur
  mesh(new THREE.TorusGeometry(0.03, 0.006, 6, 16), mat('#c8102e'), -0.07, 0.012, -0.05, plateG).rotation.x = Math.PI / 2;
  const cloche = new THREE.Group(); plateG.add(cloche);
  mesh(new THREE.SphereGeometry(0.15, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), silverM, 0, 0.005, 0, cloche);
  mesh(new THREE.SphereGeometry(0.018, 10, 8), silverM, 0, 0.16, 0, cloche);
  // Gäste und Kellner
  const guy = makePerson(301, {skin: '#d9a47e', top: '#2a3442', pants: '#1f2a44', hair: '#2a1d15', height: 1.0});
  const girl = makePerson(307, {skin: '#f1c7a5', top: '#b3203a', pants: '#2a2a2a', hair: '#5a3b22', longHair: true, height: 0.96});
  const waiter = makePerson(311, {skin: '#e2b28c', top: '#f4f4f2', pants: '#111', hair: '#111', height: 1.02});
  mesh(new THREE.BoxGeometry(0.34, 0.5, 0.02), mat('#141414'), 0, 0.12, 0.15, waiter.userData.torso); // Schürze
  const others = [makePerson(321), makePerson(322, {longHair: true}), makePerson(323), makePerson(324, {longHair: true})];
  [guy, girl, waiter, ...others].forEach(p => scene.add(p));

  const camera = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.02, 100); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    flame.scale.set(1, 2 + 0.3 * Math.sin(T * 13), 1); candleL.intensity = 2.0 * flicker(T, 2);
    // Sitzende Gäste (Blick zueinander, Tisch in der Mitte)
    guy.position.set(-0.72, 0, 0); guy.rotation.set(0, Math.PI / 2, 0); seat(guy);
    girl.position.set(0.72, 0, 0); girl.rotation.set(0, -Math.PI / 2, 0); seat(girl);
    others.forEach((p, i) => { const [x, z] = [[-2.8, -1.8], [2.8, -1.6], [-2.6, 2.2], [2.8, -1.6]][i]; const s = i % 2 ? 1 : -1; p.position.set(x + s * 0.72, 0, z); p.rotation.set(0, -s * Math.PI / 2, 0); seat(p); p.position.x += (i === 3 ? 1.44 : 0);
      if (i === 3) p.rotation.y = -Math.PI / 2; p.userData.head.rotation.y = Math.sin(T * 0.7 + i) * 0.2; });
    const gu = guy.userData, gi = girl.userData;
    // Kellner: kommt von hinten, stellt ab (bis 18.6), hebt die Glocke (CLOCHE)
    const walkK = smooth(17.0, 18.4, T);
    const wp = V3(lerp(1.6, 0.1, walkK), 0, lerp(-2.6, -0.62, walkK));
    waiter.position.copy(wp); waiter.rotation.set(0, lerp(-0.6, 0, walkK), 0); posePerson(waiter, {walk: T * 8, walkAmp: 1 - walkK});
    const wu = waiter.userData; wu.armR.rotation.x = -1.2; wu.armR.userData.fore.rotation.x = -0.6;
    const set = smooth(18.2, 18.7, T), lift = smooth(CLOCHE, CLOCHE + 0.35, T), look = smooth(CLOCHE + 0.4, CLOCHE + 0.9, T);
    // Tellerposition: in der Hand des Kellners, dann vor dem Gast
    const hand = V3(wp.x + 0.25, 1.15, wp.z + 0.45);
    plateG.position.lerpVectors(hand, V3(-0.3, 0.795, 0.02), set);
    cloche.position.set(lift * 0.25, lift * 0.5, -lift * 0.35); cloche.rotation.x = 0.6 * lift;
    if (T > CLOCHE - 0.3) { wu.armR.rotation.x = lerp(-0.9, -1.6, lift); wu.armR.userData.fore.rotation.x = lerp(-0.9, -0.3, lift); }
    wu.torso.rotation.x = 0.25 * set * (1 - lift * 0.5) + 0.35 * look; wu.head.rotation.x = 0.3 + 0.3 * look; // schaut in die Glocke
    if (look > 0) { cloche.rotation.x = lerp(0.6, 1.3, look); }
    // Gast: freut sich, dann starrt er, dann Hand vors Gesicht
    const stare = smooth(CLOCHE + 0.2, CLOCHE + 0.6, T), face = smooth(CLOCHE + 2.6, CLOCHE + 3.2, T);
    gu.armR.rotation.x = -0.35; gu.armR.userData.fore.rotation.x = -1.1; gu.armL.rotation.x = -0.35; gu.armL.userData.fore.rotation.x = -1.1;
    gu.head.rotation.x = 0.35 * stare; gu.torso.rotation.x = 0.15 * stare;
    if (face > 0) { gu.armR.rotation.x = lerp(-0.35, -2.3, face); gu.armR.userData.fore.rotation.x = lerp(-1.1, -2.1, face); gu.head.rotation.x = lerp(0.35 * stare, 0.5, face); }
    // Date: lacht mit der Hand vor dem Mund
    const laugh = smooth(CLOCHE + 1.0, CLOCHE + 1.6, T);
    gi.armL.rotation.x = -0.75; gi.armL.userData.fore.rotation.x = -0.75; gi.armR.rotation.x = lerp(-0.75, -2.2, laugh); gi.armR.userData.fore.rotation.x = lerp(-0.75, -2.0, laugh);
    gi.torso.rotation.x = (0.12 + Math.sin(T * 18) * 0.04) * laugh; gi.head.rotation.x = 0.2 * laugh * Math.sin(T * 9);
    // Kamera: Totale -> nah auf den Teller -> Reaktion
    const k1 = smooth(18.4, CLOCHE, T), k2 = smooth(CLOCHE + 1.4, CLOCHE + 2.2, T);
    let pos = V3(lerp(0.1, -0.25, k1), lerp(1.45, 1.3, k1), lerp(2.6, 0.8, k1)), tgt = V3(lerp(0, -0.3, k1), lerp(0.98, 0.8, k1), lerp(-0.3, 0.0, k1));
    pos.lerp(V3(0.35, 1.3, 1.7), k2); tgt.lerp(V3(-0.3, 1.0, -0.1), k2);
    camera.position.copy(pos).add(V3(noise1(T, 2) * 0.008, noise1(T, 5) * 0.006, 0)); camera.lookAt(tgt);
    camera.fov = lerp(44, 36, k1 * (1 - k2)); camera.updateProjectionMatrix();
  }};
}
