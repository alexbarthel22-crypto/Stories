// Brücke über den Fluss. bus (Stufe 4): Der Schulbus fährt über eine Bodenwelle – ohne Schwerkraft hebt er ab und steigt weiter.
// drop_bus: Schwerkraft zurück – der Bus fällt neben der Brücke in den Fluss. city: Das große Beben – Risse, Rauch, roter Himmel.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut, makePerson, posePerson, envMap, skyDome, facadeTex, asphaltTex} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {seat, addMouth, mouthOpen, brows} from './people.js';
import {flail, blob} from './float.js';
import {VANISH, BUMP, BUS_SPLASH, CRASH, CRACK} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const DECK = 6.0, BX = -6.0, SPEED = 7.0;

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.4;
  const skyDay = skyDome('#3c86d8', '#93c4ee', '#eaf3f9', 380); scene.add(skyDay);
  const skyRed = skyDome('#2a0f0a', '#8a2d12', '#e0753a', 379); scene.add(skyRed);
  scene.fog = new THREE.Fog('#dce9f3', 80, 330);
  const hemi = new THREE.HemisphereLight('#e2efff', '#5d6f45', 1.0); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff2da', 3.0); sun.position.set(-30, 45, 25); sun.target.position.set(0, 0, 0); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -45, right: 45, top: 45, bottom: -45, near: 1, far: 140}); scene.add(sun, sun.target);
  const glow = new THREE.PointLight('#ff5a1a', 0, 120, 1.2); glow.position.set(30, 8, -40); scene.add(glow);

  // Fluss (entlang z), Ufer
  const waterT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#3f6f86'; g.fillRect(0, 0, w, h); const r = rng(3); g.strokeStyle = 'rgba(220,240,250,0.25)'; g.lineWidth = 2; for (let i = 0; i < 160; i++) { const x = r() * w, y = r() * h; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + 15, y - 4, x + 30 + r() * 30, y); g.stroke(); } });
  waterT.wrapS = waterT.wrapT = THREE.RepeatWrapping; waterT.repeat.set(4, 30);
  const water = mesh(new THREE.PlaneGeometry(34, 400), new THREE.MeshPhysicalMaterial({map: waterT, roughness: 0.1, clearcoat: 1}), 0, 0, 0, scene); water.rotation.x = -Math.PI / 2; water.castShadow = false;
  const grassT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#5b8f3c'; g.fillRect(0, 0, w, h); const r = rng(7); for (let i = 0; i < 4000; i++) { g.fillStyle = `rgba(${40 + r() * 50},${100 + r() * 60},${30 + r() * 30},0.5)`; g.fillRect(r() * w, r() * h, 2, 3); } });
  grassT.wrapS = grassT.wrapT = THREE.RepeatWrapping; grassT.repeat.set(20, 60);
  for (const s of [-1, 1]) {
    const bank = mesh(new THREE.BoxGeometry(160, DECK, 400), new THREE.MeshStandardMaterial({map: grassT, roughness: 1}), s * (17 + 80), DECK / 2 - 0.05, 0, scene);
    const slope = mesh(new THREE.PlaneGeometry(Math.hypot(4, DECK), 400), mat('#6b7a52', {roughness: 1}), s * 15, DECK / 2, 0, scene); slope.rotation.set(-Math.PI / 2, 0, 0); slope.rotation.y = s * Math.atan2(DECK, 4) * -1; slope.rotation.order = 'YXZ';
  }
  // Uferstraße und Häuser
  const r = rng(33); const houses = [];
  for (const s of [-1, 1]) for (let z = -120; z < 120; z += 11 + r() * 4) { if (Math.abs(z) < 9) continue;
    const h = 8 + r() * 10, w = 8 + r() * 3; const hs = new THREE.Group(); hs.position.set(s * (24 + r() * 3), DECK, z); scene.add(hs);
    mesh(new THREE.BoxGeometry(w, h, 9), new THREE.MeshStandardMaterial({map: facadeTex(['#e9dcc5', '#d9c3a3', '#c8d2d8', '#e4c9b6', '#f1e7d4'][Math.floor(r() * 5)], Math.floor(r() * 99), Math.round(h / 3), 3), roughness: 0.9}), 0, h / 2, 0, hs).rotation.y = s > 0 ? -Math.PI / 2 : Math.PI / 2;
    mesh(new THREE.ConeGeometry(6.4, 3, 4), mat('#9a4a36'), 0, h + 1.5, 0, hs).rotation.y = Math.PI / 4; houses.push(hs); }
  for (let i = 0; i < 26; i++) { const s = i % 2 ? 1 : -1; const t = new THREE.Group(); t.position.set(s * (18.5 + r() * 2), DECK, lerp(-110, 110, r())); if (Math.abs(t.position.z) < 8) continue; scene.add(t);
    mesh(new THREE.CylinderGeometry(0.2, 0.3, 2.6, 7), mat('#5b3f26'), 0, 1.3, 0, t); mesh(new THREE.SphereGeometry(2.2 + r(), 12, 10), mat('#4a8a3a', {roughness: 1}), 0, 3.8, 0, t); }
  // Brücke (entlang x), Fahrbahn 10 m breit
  const asp = asphaltTex(); asp.repeat.set(8, 1.5);
  const deck = new THREE.Group(); scene.add(deck);
  mesh(new THREE.BoxGeometry(90, 0.8, 10), new THREE.MeshStandardMaterial({map: asp, roughness: 0.9}), 0, DECK - 0.4, 0, deck);
  mesh(new THREE.BoxGeometry(90, 1.4, 9.4), mat('#b9b5ab'), 0, DECK - 1.5, 0, deck);
  for (const x of [-9, 0, 9]) mesh(new THREE.BoxGeometry(2, DECK - 1.5, 6), mat('#a9a59b'), x, (DECK - 1.5) / 2, 0, deck);
  const lineM = mat('#f2f2ee'); for (let x = -44; x < 44; x += 4) mesh(new THREE.BoxGeometry(2, 0.02, 0.15), lineM, x, DECK + 0.01, 0, deck);
  const railM = mat('#4a6b8a', {metalness: 0.6, roughness: 0.4});
  for (const s of [-1, 1]) { mesh(new THREE.BoxGeometry(90, 0.08, 0.08), railM, 0, DECK + 1.1, s * 4.9, deck); for (let x = -44; x <= 44; x += 2) mesh(new THREE.BoxGeometry(0.06, 1.1, 0.06), railM, x, DECK + 0.55, s * 4.9, deck); }
  const bump = mesh(new THREE.CylinderGeometry(0.6, 0.6, 9.6, 16, 1, false, 0, Math.PI), mat('#e0c13a', {roughness: 0.8}), BX, DECK - 0.42, 0, deck); bump.rotation.set(Math.PI / 2, 0, -Math.PI / 2); bump.scale.set(1, 1, 0.3);
  // Risse (für das Beben)
  const cracks = new THREE.Group(); deck.add(cracks); const crackM = mat('#1a0c08', {emissive: '#ff4a10', emissiveIntensity: 0});
  for (let i = 0; i < 14; i++) { const c = new THREE.Group(); c.position.set(lerp(-40, 40, r()), DECK + 0.02, lerp(-4.5, 4.5, r())); cracks.add(c); let x = 0, z = 0, a = r() * 6;
    for (let k = 0; k < 7; k++) { const L = 0.6 + r() * 1.4; a += (r() - 0.5) * 1.2; const m = mesh(new THREE.BoxGeometry(L, 0.05, 0.18 + r() * 0.25), crackM, x + Math.cos(a) * L / 2, 0, z + Math.sin(a) * L / 2, c); m.rotation.y = -a; x += Math.cos(a) * L; z += Math.sin(a) * L; } }
  for (let i = 0; i < 10; i++) { const c = mesh(new THREE.BoxGeometry(2 + r() * 6, 0.04, 0.3 + r() * 0.5), crackM, (r() < 0.5 ? -1 : 1) * (22 + r() * 20), DECK + 0.03, lerp(-60, 60, r()), cracks); c.rotation.y = r() * 3; }
  const smoke = particles(900, 'smoke'); scene.add(smoke);
  const fire = particles(500, 'flame'); scene.add(fire);
  const debris = []; for (let i = 0; i < 40; i++) { const m = mesh(new THREE.DodecahedronGeometry(0.15 + r() * 0.35, 0), mat('#8a8278'), 0, -50, 0, scene); debris.push({m, x: lerp(-30, 30, r()), z: (r() < 0.5 ? -1 : 1) * (20 + r() * 10), t0: CRACK - 1 + r() * 6, h: 10 + r() * 8}); }

  // Schulbus
  const bus = new THREE.Group(); scene.add(bus); const body = new THREE.Group(); bus.add(body);
  const busT = canvasTex(1024, 256, (g, w, h) => { g.fillStyle = '#f2c230'; g.fillRect(0, 0, w, h); g.fillStyle = '#20303c'; g.fillRect(40, 40, w - 140, 110); g.fillStyle = 'rgba(255,255,255,0.25)';
    for (let x = 40; x < w - 100; x += 92) { g.fillRect(x, 40, 4, 110); } g.fillStyle = '#ffffff'; g.fillRect(0, 170, w, 16); g.fillStyle = '#1a1a1a'; g.font = '900 44px sans-serif'; g.fillText('SCHULBUS', 60, 230); });
  const busM = new THREE.MeshStandardMaterial({map: busT, roughness: 0.45});
  mesh(new RoundedBoxGeometry(12, 3.0, 2.55, 3, 0.25), [busM, busM, mat('#f4f1e8'), mat('#2a2a2a'), busM, busM].map(m => m), 0, 1.9, 0, body);
  const frontT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#f2c230'; g.fillRect(0, 0, w, h); g.fillStyle = '#20303c'; g.fillRect(20, 20, w - 40, 120); g.fillStyle = '#111'; g.fillRect(40, 6, w - 80, 14); g.fillStyle = '#ffb000'; g.font = '900 13px sans-serif'; g.fillText('SCHULBUS', 95, 17); g.fillStyle = '#fff6d0'; g.fillRect(24, 200, 50, 24); g.fillRect(w - 74, 200, 50, 24); });
  mesh(new THREE.PlaneGeometry(2.4, 2.8), new THREE.MeshStandardMaterial({map: frontT, roughness: 0.4}), 6.02, 1.9, 0, body).rotation.y = Math.PI / 2;
  const wheels = []; for (const x of [-3.8, 3.8]) for (const z of [-1.15, 1.15]) { const w = mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.4, 20), mat('#151515', {roughness: 0.9}), x, 0.55, z, bus); w.rotation.x = Math.PI / 2; wheels.push(w); }
  const kidsIn = []; for (let i = 0; i < 8; i++) { const p = makePerson(2000 + i * 7, {height: 0.85, longHair: i % 3 === 0}); addMouth(p); body.add(p); kidsIn.push({p, x: -4.5 + i * 1.25, z: i % 2 ? 0.55 : -0.55, s: i * 1.3}); }
  const roofKids = [0, 1, 2, 3].map(i => { const p = makePerson(2100 + i * 9, {height: 0.85}); addMouth(p); scene.add(p); return p; });
  const splash = []; for (let i = 0; i < 260; i++) { const b = blob('#e4f4fa', 0.05 + r() * 0.14); b.material.transparent = true; b.material.opacity = 0.6; scene.add(b); const a = r() * 7, sp = 1 + r() * 7; splash.push({b, v: V3(Math.cos(a) * sp * 0.6, 6 + r() * 11, Math.sin(a) * sp * 0.6)}); }
  // Autos auf der Brücke (nur im Beben)
  const cars = [1, 2, 3].map(i => { const c = makeCarSimple(i); scene.add(c); return c; });
  function makeCarSimple(i) { const g = new THREE.Group(); mesh(new RoundedBoxGeometry(4.2, 1.2, 1.8, 2, 0.2), mat(['#c8102e', '#2b5fa8', '#e8e8e2'][i - 1], {roughness: 0.3, metalness: 0.2}), 0, 0.75, 0, g); mesh(new RoundedBoxGeometry(2.2, 0.7, 1.7, 2, 0.2), mat('#1a2430', {roughness: 0.1, metalness: 0.6}), -0.2, 1.55, 0, g); return g; }

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.1, 800); scene.add(camera);
  const busAt = T => { // Position und Lage des Busses in der Stufe 4
    if (T < BUMP) return {p: V3(BX + SPEED * (T - BUMP), DECK, 0), pitch: 0, roll: 0};
    const d = T - BUMP; return {p: V3(BX + SPEED * d, DECK + 1.25 * d, 0.35 * d), pitch: 0.07 * d + 0.05 * Math.sin(d * 3) * Math.exp(-d), roll: 0.03 * d}; };
  const HOVER = V3(10, DECK + 3.5, -16); const FALL0 = BUS_SPLASH - Math.sqrt(2 * (HOVER.y - 1.0) / 9.8);

  return {scene, camera, update(shot, T) {
    const city = shot.id === 'city', dropS = shot.id === 'drop_bus';
    skyDay.visible = !city; skyRed.visible = city; scene.fog.color.set(city ? '#6b3a22' : '#dce9f3'); scene.fog.near = city ? 30 : 80; scene.fog.far = city ? 220 : 330;
    hemi.color.set(city ? '#ffb48a' : '#e2efff'); hemi.intensity = city ? 0.6 : 1.0; sun.color.set(city ? '#ff9a5a' : '#fff2da'); sun.intensity = city ? 1.6 : 3.0;
    glow.intensity = city ? 900 * flicker(T, 2) : 0;
    waterT.offset.y = -T * 0.05;
    // ---- Bus ----
    let b;
    if (shot.id === 'bus') { b = busAt(T); bus.position.copy(b.p); bus.rotation.set(b.roll, 0, b.pitch); body.position.y = T < BUMP ? 0.03 * Math.sin(T * 9) : 0; }
    else if (dropS) { const t = Math.max(0, T - FALL0); const y = Math.max(-1.4, HOVER.y - 4.9 * t * t); bus.position.set(HOVER.x, y, HOVER.z); bus.rotation.set(0.12, 0.4, T < BUS_SPLASH ? 0.25 + 0.1 * t : 0.18);
      if (T > BUS_SPLASH) bus.position.y = -1.4 + 0.25 * Math.sin((T - BUS_SPLASH) * 5) * Math.exp(-(T - BUS_SPLASH) * 1.5); }
    else { bus.position.set(HOVER.x, -1.45 + 0.05 * Math.sin(T * 1.3), HOVER.z); bus.rotation.set(0.12, 0.4, 0.18); }
    wheels.forEach(w => { w.rotation.y = shot.id === 'bus' ? -T * SPEED / 0.55 : 0; });
    const floatIn = shot.id === 'bus' ? smooth(BUMP, BUMP + 0.8, T) : dropS && T < BUS_SPLASH ? 1 : 0;
    kidsIn.forEach((q, i) => { const p = q.p; posePerson(p, {}); seat(p, 0.95); p.position.x = q.x; p.position.z = q.z; p.position.y += 0.6 * floatIn + 0.25 * floatIn * Math.sin(T * 1.5 + q.s); p.rotation.set(0, Math.PI / 2 + (i % 2 ? 0.6 : -0.6) * floatIn, 0.3 * floatIn * Math.sin(q.s));
      if (floatIn > 0) { flail(p, T, q.s, floatIn); mouthOpen(p, 0.8); brows(p, 1, 0); } p.visible = !city; });
    roofKids.forEach((p, i) => { p.visible = city; if (!city) return; posePerson(p, {}); bus.updateMatrixWorld(true); const w = bus.localToWorld(V3(-3 + i * 2, 3.4, 0)); p.position.copy(w); p.rotation.set(0, 1.2 + i, 0);
      p.userData.armL.rotation.z = -2.4 + 0.3 * Math.sin(T * 4 + i); p.userData.armR.rotation.z = 2.4 - 0.3 * Math.sin(T * 4 + i); mouthOpen(p, 0.7); brows(p, 1, 0); });
    splash.forEach(s => { const t = T - BUS_SPLASH; s.b.visible = dropS && t > 0 && t < 2.2; if (!s.b.visible) return; s.b.position.set(HOVER.x + s.v.x * t, s.v.y * t - 4.9 * t * t, HOVER.z + s.v.z * t); if (s.b.position.y < -0.2) s.b.visible = false; });
    // ---- Beben ----
    const q = city ? 0.12 + 0.25 * smooth(CRACK - 0.3, CRACK + 0.3, T) * (1 - 0.6 * smooth(CRACK + 1.5, 80, T)) : 0;
    const shk = V3(noise1(T * 14, 1) * q, noise1(T * 14, 2) * q * 0.5, noise1(T * 14, 3) * q);
    deck.position.copy(city ? shk : V3()); bump.visible = true;
    houses.forEach((h, i) => { h.rotation.z = city ? 0.015 * Math.sin(T * 11 + i) * (q / 0.37) : 0; h.rotation.x = city ? 0.01 * Math.sin(T * 9 + i * 2) : 0; });
    crackM.emissiveIntensity = city ? 6 * smooth(CRACK, CRACK + 1.2, T) * flicker(T, 1) : 0;
    cracks.visible = city; cracks.children.forEach((c, i) => { c.scale.setScalar(city ? smooth(CRACK - 0.2 + (i % 5) * 0.15, CRACK + 0.8 + (i % 5) * 0.15, T) + 0.001 : 0.001); });
    if (city) updateParticles(smoke, [{pos: V3(28, DECK, -48), r: 7, t0: 60, type: 'smoke', size: 16, rise: 5, alpha: 0.6, col: [0.16, 0.12, 0.1]}, {pos: V3(48, DECK, -18), r: 6, t0: 60, type: 'smoke', size: 14, rise: 4, alpha: 0.55, col: [0.2, 0.14, 0.1]}, {pos: V3(-35, DECK, -40), r: 6, t0: 60, type: 'smoke', size: 14, rise: 4, alpha: 0.55, col: [0.18, 0.14, 0.12]}, {pos: V3(30, DECK, -60), r: 8, t0: 60, type: 'smoke', size: 18, rise: 5, alpha: 0.5, col: [0.2, 0.15, 0.12]},
      {pos: V3(-25, DECK, 50), r: 6, t0: 60, type: 'smoke', size: 14, rise: 4, alpha: 0.5, col: [0.22, 0.16, 0.12]}, {pos: V3(0, DECK, 0), r: 30, t0: CRACK, type: 'smoke', size: 3, rise: 1, alpha: 0.18, col: [0.55, 0.45, 0.38]}], T, V3(1.5, 0, 0.5));
    smoke.visible = city; fire.visible = city;
    if (city) updateParticles(fire, [{pos: V3(28, DECK + 2, -48), r: 4, t0: 60, type: 'flame', size: 6, power: 1.3}, {pos: V3(48, DECK + 2, -18), r: 3, t0: 60, type: 'flame', size: 5, power: 1.2}, {pos: V3(-35, DECK + 2, -40), r: 3, t0: 60, type: 'flame', size: 5, power: 1.2}, {pos: V3(30, DECK + 2, -60), r: 4, t0: 60, type: 'flame', size: 6, power: 1.2}, {pos: V3(-25, DECK + 2, 50), r: 3, t0: 60, type: 'flame', size: 5}], T);
    debris.forEach(d => { const t = T - d.t0; d.m.visible = city && t > 0 && t < 3; if (!d.m.visible) return; d.m.position.set(d.x, DECK + d.h - 4.9 * t * t, d.z); if (d.m.position.y < DECK) d.m.position.y = DECK + 0.1; d.m.rotation.set(t * 3, t * 2, 0); });
    cars.forEach((c, i) => { c.visible = city; c.position.set(6 + i * 9, DECK + 0.02 + Math.abs(shk.y) * 0.5, -2.4 + (i % 2) * 4.6).add(shk); c.rotation.set(0, i * 0.3, 0); });

    // ---------- Kamera ----------
    let pos, lk; camera.fov = 50; camera.up.set(0, 1, 0);
    if (shot.id === 'bus') {
      if (T < BUMP + 0.8) { const k = smooth(31, BUMP + 0.8, T); pos = V3(lerp(10, 8, k), DECK + 2.2, lerp(15, 13, k)); lk = V3().lerpVectors(bus.position, V3(BX, DECK + 1.5, 0), 0.5).add(V3(0, 1.0, 0)); camera.fov = 50; }
      else { const k = smooth(BUMP + 0.8, 39, T); pos = V3(lerp(BX - 4, BX - 8, k), DECK + 1.5, lerp(-3.5, -4.2, k)); lk = bus.position.clone().add(V3(0, 1.2, 0)); camera.fov = lerp(54, 46, k); }
      if (T > BUMP && T < BUMP + 0.4) pos.add(V3(0, noise1(T * 20, 1) * 0.08, 0));
    } else if (dropS) { const k = smooth(55, 58, T); pos = V3(lerp(-3, -4, k), DECK + 1.6, lerp(-4.2, -4.4, k)); lk = V3().lerpVectors(V3(HOVER.x, HOVER.y + 1.2, HOVER.z), V3(HOVER.x, 0.5, HOVER.z), smooth(FALL0, BUS_SPLASH + 0.4, T)); camera.fov = 48;
      if (T > BUS_SPLASH && T < BUS_SPLASH + 0.5) pos.add(V3(noise1(T * 14, 1) * 0.06, noise1(T * 14, 2) * 0.06, 0)); }
    else { const k = smooth(72, 80, T); pos = V3(lerp(-14, -10, k), DECK + lerp(2.2, 3.0, k), lerp(-3.0, -2.0, k)).add(shk.clone().multiplyScalar(0.35)); lk = V3(lerp(6, 10, k), DECK + lerp(1.5, 2.5, k), lerp(-6, -10, k)); camera.fov = lerp(60, 54, k); }
    camera.position.copy(pos); camera.lookAt(lk); camera.updateProjectionMatrix();
  }};
}
