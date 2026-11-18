// Regennasse Stadtstraße und alle Einstellungen, die dort spielen
import {THREE, envMap, mat, mesh, rng, clamp, smooth, lerp, easeOut, noise1, canvasTex, facadeTex, asphaltTex, tileTex, skyDome,
  makePerson, posePerson, makeCar, carNoRubber, sparkSystem, updateSparks, rainSystem, updateRain, splashSystem, updateSplash} from './lib.js';
import {Reflector} from 'three/addons/objects/Reflector.js';
import {makePhone, makeHands, makeDrops, updateScreen} from './phone.js';
import {VANISH, RETURN} from './timeline.js';
import {particles, updateParticles, flicker} from './fx.js';

const LANES = [-4.8, -1.6, 1.6, 4.8];
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export function buildStreet(renderer) {
  const scene = new THREE.Scene(); scene.environment = envMap(renderer); scene.environmentIntensity = 0.55;
  scene.fog = new THREE.Fog('#8d97a3', 25, 190);
  const sky = skyDome('#5f6b7a', '#9aa4b0', '#b8bec4'); scene.add(sky);
  const hemi = new THREE.HemisphereLight('#c5d0dc', '#3b3a38', 1.5); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff1dd', 1.4); sun.position.set(-30, 50, 20); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -40, right: 40, top: 40, bottom: -40, near: 1, far: 150}); sun.shadow.bias = -0.0005;
  scene.add(sun); scene.add(sun.target);

  // Spiegelnde Straße unter halbtransparentem Asphalt = nasse Fahrbahn
  const refl = new Reflector(new THREE.PlaneGeometry(13, 420), {textureWidth: 540, textureHeight: 960, color: 0x8a8f96});
  refl.rotation.x = -Math.PI / 2; refl.position.y = -0.002; scene.add(refl);
  const asp = asphaltTex(); asp.repeat.set(2, 60);
  const road = mesh(new THREE.PlaneGeometry(13, 420), new THREE.MeshStandardMaterial({map: asp, transparent: true, opacity: 0.78, roughness: 0.35, metalness: 0.1}), 0, 0, 0, scene);
  road.rotation.x = -Math.PI / 2; road.castShadow = false;
  // Fahrbahnmarkierung
  const lineM = new THREE.MeshStandardMaterial({color: '#e8e8e2', roughness: 0.5, transparent: true, opacity: 0.85});
  for (let z = -210; z < 210; z += 9) for (const x of [-3.2, 3.2]) { const l = mesh(new THREE.PlaneGeometry(0.15, 4), lineM, x, 0.004, z, scene); l.rotation.x = -Math.PI / 2; l.castShadow = false; }
  for (const x of [-0.08, 0.08]) { const l = mesh(new THREE.PlaneGeometry(0.1, 420), new THREE.MeshStandardMaterial({color: '#e9c43a', roughness: 0.5, transparent: true, opacity: 0.8}), x, 0.004, 0, scene); l.rotation.x = -Math.PI / 2; }
  // Pfützen
  const r = rng(5);
  for (let i = 0; i < 26; i++) { const p = mesh(new THREE.CircleGeometry(1, 24), new THREE.MeshStandardMaterial({color: '#20262d', roughness: 0.02, metalness: 0.6, transparent: true, opacity: 0.55}), (r() - 0.5) * 11, 0.003, (r() - 0.5) * 120, scene); p.rotation.x = -Math.PI / 2; p.scale.set(0.8 + r() * 2, 0.5 + r() * 1.2, 1); }
  // Gehwege und Bordstein
  const tiles = tileTex(); tiles.repeat.set(3, 100);
  for (const s of [-1, 1]) {
    mesh(new THREE.BoxGeometry(5, 0.15, 420), new THREE.MeshStandardMaterial({map: tiles, roughness: 0.45, metalness: 0.05, color: '#b5b5b0'}), s * 9, 0.075, 0, scene);
    mesh(new THREE.BoxGeometry(0.25, 0.17, 420), mat('#a4a49e', {roughness: 0.5}), s * 6.55, 0.085, 0, scene);
  }
  // Häuserzeilen
  const cols = ['#d8cbb2', '#c9b79c', '#e2d9c8', '#b9a48a', '#cfc2ad', '#a89a8a', '#d6c3a5', '#e0d2bc'];
  for (const s of [-1, 1]) {
    let z = -200;
    while (z < 200) {
      const w = 9 + r() * 7, h = 12 + r() * 16, d = 12;
      const c = cols[Math.floor(r() * cols.length)];
      const tex = facadeTex(c, Math.floor(r() * 1000), Math.round(h / 3.3), Math.round(w / 3));
      const b = mesh(new THREE.BoxGeometry(d, h, w), [mat(c), mat(c), mat('#6d6a66'), mat(c), new THREE.MeshStandardMaterial({map: tex, roughness: 0.85}), new THREE.MeshStandardMaterial({map: tex, roughness: 0.85})], s * (11.5 + d / 2), h / 2, z + w / 2, scene);
      b.rotation.y = s > 0 ? -Math.PI / 2 : Math.PI / 2; b.rotation.y = 0;
      // Fassade zur Straße: Box-Seite +x/-x bekommt Textur
      b.material = s > 0 ? [new THREE.MeshStandardMaterial({map: tex}), new THREE.MeshStandardMaterial({map: tex, roughness: 0.85}), mat('#6d6a66'), mat(c), mat(c), mat(c)]
        : [new THREE.MeshStandardMaterial({map: tex}), new THREE.MeshStandardMaterial({map: tex, roughness: 0.85}), mat('#6d6a66'), mat(c), mat(c), mat(c)];
      // Dachkante
      mesh(new THREE.BoxGeometry(d + 0.6, 0.5, w + 0.2), mat('#7d7368'), s * (11.5 + d / 2) - s * 0.3, h + 0.25, z + w / 2, scene);
      // Ladenmarkise
      if (r() < 0.5) { const a = mesh(new THREE.BoxGeometry(1.4, 0.08, w * 0.6), mat(['#2f6b4f', '#8c2f2f', '#2f4f8c', '#c9852b'][Math.floor(r() * 4)]), s * 11.0, 3.2, z + w / 2, scene); a.rotation.z = s * 0.25; }
      z += w;
    }
  }
  // Laternen und Bäume
  for (let z = -180; z < 180; z += 18) for (const s of [-1, 1]) {
    mesh(new THREE.CylinderGeometry(0.06, 0.09, 5.5, 8), mat('#2c2f33', {metalness: 0.6, roughness: 0.4}), s * 7.0, 2.75, z, scene);
    mesh(new THREE.BoxGeometry(0.9, 0.1, 0.25), mat('#2c2f33'), s * 6.65, 5.45, z, scene);
    mesh(new THREE.BoxGeometry(0.5, 0.05, 0.2), mat('#fff3d6', {emissive: '#ffe2a8', emissiveIntensity: 2.2}), s * 6.45, 5.38, z, scene);
    if ((z / 18) % 2 === 0) {
      mesh(new THREE.CylinderGeometry(0.12, 0.16, 3, 7), mat('#4a3a2c'), s * 10.2, 1.5, z + 9, scene);
      const c = mesh(new THREE.IcosahedronGeometry(1.8, 1), mat('#4f6d3a', {flatShading: true, roughness: 0.9}), s * 10.2, 4.2, z + 9, scene); c.scale.y = 1.2;
    }
  }
  // Ampel
  mesh(new THREE.CylinderGeometry(0.07, 0.07, 3.6, 8), mat('#222'), 7.0, 1.8, -12, scene);
  mesh(new THREE.BoxGeometry(0.35, 0.95, 0.3), mat('#1a1a1a'), 7.0, 3.3, -12, scene);
  mesh(new THREE.SphereGeometry(0.1, 10, 8), mat('#ff3b2f', {emissive: '#ff2a1a', emissiveIntensity: 2}), 7.0, 3.6, -11.84, scene);
  // Bushaltestelle (für die Hosen-Szene)
  const shelter = new THREE.Group(); shelter.position.set(9.6, 0.15, 30); scene.add(shelter);
  mesh(new THREE.BoxGeometry(1.8, 0.08, 5), mat('#3d4650', {metalness: 0.5}), 0, 2.5, 0, shelter);
  const glassM = new THREE.MeshPhysicalMaterial({color: '#cfe3ee', roughness: 0.05, transmission: 0.0, transparent: true, opacity: 0.18});
  mesh(new THREE.BoxGeometry(0.04, 2.4, 5), glassM, 0.85, 1.25, 0, shelter);
  for (const z of [-2.45, 2.45]) mesh(new THREE.BoxGeometry(0.08, 2.5, 0.08), mat('#3d4650', {metalness: 0.5}), 0.85, 1.25, z, shelter);
  mesh(new THREE.BoxGeometry(0.5, 0.06, 2.4), mat('#70553a'), 0.55, 0.5, 0, shelter);

  // Regen, Einschläge
  const rain = rainSystem(9000, {x0: -14, x1: 14, y0: 0, y1: 14, z0: -40, z1: 50});
  scene.add(rain);
  const rainFar = rainSystem(5000, {x0: -30, x1: 30, y0: 0, y1: 50, z0: -160, z1: -40}, 0x9aa4b0, 1.4, 0.3); scene.add(rainFar);
  const splash = splashSystem(700, {x0: -6.5, x1: 6.5, z0: -40, z1: 40}); scene.add(splash);
  const splash2 = splashSystem(300, {x0: 6.7, x1: 11.4, z0: -10, z1: 40, y: 0.162}); scene.add(splash2);

  // Akteure
  const cars = []; for (let i = 0; i < 34; i++) { const c = makeCar(i + 1, i === 33 || i === 32 ? {ambulance: true, color: '#f4f4f0'} : {}); scene.add(c); cars.push(c); }
  const people = []; for (let i = 0; i < 16; i++) { const p = makePerson(i + 3, {shoe: i === 0 ? '#2b2b2e' : undefined, sole: i === 0 ? '#e9dcc3' : undefined, ponytail: i === 11, longHair: i === 11, shortSleeve: false, pants: i === 6 ? '#5a6b7c' : undefined}); scene.add(p); people.push(p); }
  // Regenschirm
  const umbrella = new THREE.Group();
  mesh(new THREE.ConeGeometry(0.75, 0.32, 10, 1, true), mat('#1f3b6e', {side: THREE.DoubleSide, roughness: 0.6}), 0, 0.9, 0, umbrella);
  mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.95, 6), mat('#222'), 0, 0.45, 0, umbrella);
  scene.add(umbrella);
  // Luftballons
  const balloons = [];
  const bc = ['#e8323c', '#2f7de1', '#f2c230'];
  for (let i = 0; i < 3; i++) {
    const b = new THREE.Group();
    const ball = mesh(new THREE.SphereGeometry(0.17, 20, 16), new THREE.MeshPhysicalMaterial({color: bc[i], roughness: 0.15, clearcoat: 1, transparent: true}), 0, 0, 0, b); ball.scale.y = 1.18;
    mesh(new THREE.ConeGeometry(0.025, 0.04, 8), mat(bc[i]), 0, -0.21, 0, b).rotation.x = Math.PI;
    const string = new THREE.Line(new THREE.BufferGeometry().setFromPoints([V3(0, 0, 0), V3(0, -1, 0)]), new THREE.LineBasicMaterial({color: '#eeeeee'}));
    scene.add(string); b.userData = {ball, string}; scene.add(b); balloons.push(b);
  }
  const puff = mesh(new THREE.SphereGeometry(0.2, 16, 12), new THREE.MeshBasicMaterial({color: '#ffffff', transparent: true, opacity: 0, depthWrite: false}), 0, 0, 0, scene);
  const puffs = [puff, puff.clone(), puff.clone()]; puffs.forEach(p => { p.material = p.material.clone(); scene.add(p); });
  // Reifen, die nach der Rückkehr auf der Straße liegen
  const looseTires = [];
  for (let i = 0; i < 16; i++) { const t = mesh(new THREE.TorusGeometry(0.24, 0.1, 10, 24), mat('#141414', {roughness: 0.9}), 0, 0, 0, scene); t.scale.set(1, 1, 1.9); looseTires.push(t); }
  // Funken
  const sparks = sparkSystem(2600, 0.09); scene.add(sparks);
  const glassBits = sparkSystem(300, 0.05); glassBits.material.color = new THREE.Color('#ffffff'); glassBits.material.blending = THREE.NormalBlending; scene.add(glassBits);
  // Blaulicht
  const blueLight = new THREE.PointLight('#3a6bff', 0, 30); scene.add(blueLight);

  // Feuer, Rauch, Feuerlicht
  const fire = particles(2600, 'flame'); scene.add(fire);
  const smoke = particles(1300, 'smoke'); scene.add(smoke);
  const fireLights = [0, 1, 2].map(() => { const l = new THREE.PointLight('#ff7a2a', 0, 40, 1.6); scene.add(l); return l; });
  // Gasanschluss an der Hauswand (für die Gas-Szene)
  const gas = new THREE.Group(); gas.position.set(11.35, 0.15, 62); scene.add(gas);
  const yellow = mat('#e6b422', {roughness: 0.5, metalness: 0.3});
  mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.2, 12), yellow, -0.15, 0.45, 0, gas);
  const elbow = mesh(new THREE.TorusGeometry(0.1, 0.05, 10, 16, Math.PI / 2), yellow, -0.05, 1.05, 0, gas); elbow.rotation.z = Math.PI / 2;
  mesh(new THREE.BoxGeometry(0.35, 0.5, 0.45), mat('#d8d4c8', {roughness: 0.6}), -0.2, 1.4, 0.0, gas);
  mesh(new THREE.BoxGeometry(0.02, 0.18, 0.25), mat('#222', {roughness: 0.2}), -0.38, 1.45, 0, gas);
  const gasket = mesh(new THREE.TorusGeometry(0.058, 0.014, 8, 20), mat('#111', {roughness: 0.95}), -0.15, 0.62, 0, gas); gasket.rotation.x = Math.PI / 2;
  const manhole = mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.03, 20), mat('#2d2d2d', {metalness: 0.7, roughness: 0.5}), 10.0, 0.16, 61.0, scene);
  // Fensterscheiben, die bei der Explosion zerspringen
  const shards = sparkSystem(900, 0.06); shards.material.blending = THREE.NormalBlending; shards.material.vertexColors = false; shards.material.color = new THREE.Color('#dfe9f2'); shards.material.needsUpdate = true; scene.add(shards);

  // Handy vor der Kamera (Intro)
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 600); scene.add(camera);
  const phone = makePhone(); const hands = makeHands();
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig);
  rig.position.set(0.03, -0.075, -0.4); rig.rotation.set(-0.1, -0.06, 0.04);
  const drops = makeDrops(11, 140);

  const S = {scene, camera, sun, sky, hemi, fire, smoke, fireLights, gasket, manhole, shards, cars, people, umbrella, balloons, puffs, looseTires, sparks, glassBits, rain, rainFar, splash, splash2, blueLight, rig, phone, drops};
  return {scene, camera, update: (shot, T) => updateStreet(S, shot, T)};
}

// ---------------------------------------------------------------
function hide(S) { S.cars.forEach(c => { c.visible = false; c.rotation.set(0, 0, 0); c.userData.body.position.set(0, 0, 0); c.userData.body.rotation.set(0, 0, 0); carNoRubber(c, 0); c.userData.wheels.forEach(w => { w.w.rotation.set(0, 0, 0); w.spin.rotation.set(0, 0, 0); w.wires.children.forEach(t => t.position.y = 0); }); });
  S.people.forEach(p => { p.visible = false; p.rotation.set(0, 0, 0); p.userData.soles.forEach(s => s.visible = true); p.userData.pants.visible = true; const pt = p.userData.ponytail; if (pt) { pt.userData.band.visible = true; pt.userData.loose.visible = false; } p.userData.pl.forEach(g => g.visible = true); });
  S.umbrella.visible = false; S.balloons.forEach(b => { b.visible = false; b.userData.string.visible = false; }); S.puffs.forEach(p => p.material.opacity = 0);
  S.looseTires.forEach(t => t.visible = false); S.rig.visible = false; S.blueLight.intensity = 0;
}
function mood(S, kind) {
  const night = kind === 'fire';
  S.sky.material.color.set(night ? '#3b2a26' : '#ffffff');
  S.scene.fog.color.set(night ? '#2b211d' : '#8d97a3'); S.scene.fog.near = night ? 15 : 25; S.scene.fog.far = night ? 150 : 190;
  S.hemi.intensity = night ? 0.35 : 1.5; S.sun.intensity = night ? 0.12 : 1.4;
  S.fireLights.forEach(l => l.intensity = 0);
}
function shake(cam, t, amp = 0.012, seed = 1) { cam.position.x += noise1(t, seed) * amp; cam.position.y += noise1(t, seed + 5) * amp; cam.rotation.z += noise1(t * 0.7, seed + 9) * amp * 0.5; }
function look(cam, p, t) { cam.position.copy(p); cam.lookAt(t); }

// Fahrt eines Autos: vor dem Verschwinden konstante Geschwindigkeit, danach Rutschen auf Felgen
function slideZ(z0, v, tv, a, t) {
  if (t < tv) return z0 + v * t;
  const s = Math.min(t - tv, Math.abs(v) / a); return z0 + v * tv + v * s - Math.sign(v) * 0.5 * a * s * s;
}
function slideV(v, tv, a, t) { if (t < tv) return v; return Math.sign(v) * Math.max(0, Math.abs(v) - a * (t - tv)); }
function placeCar(c, x, z, dir, t, tv, gone, spinDist) {
  c.visible = true; c.position.set(x, 0, z); c.rotation.y = dir > 0 ? 0 : Math.PI;
  const s = t - tv;
  const drop = gone ? -0.12 - Math.exp(-s * 9) * Math.sin(s * 30) * 0.04 * (s > 0) : 0;
  c.userData.body.position.y = s > 0 && gone ? lerp(0, drop, clamp(s / 0.08)) : 0;
  c.userData.wheels.forEach(w => { w.w.position.y = 0.34 + (gone && s > 0 ? lerp(0, -0.12, clamp(s / 0.08)) : 0); w.spin.rotation.x = spinDist; });
  carNoRubber(c, gone ? clamp(s / 0.12) : 0, 1);
}
function wheelEmitters(getCar, tv, t1, dirSign) {
  // Funken an den Kontaktpunkten der Hinterräder
  const out = [];
  for (const wx of [-0.82, 0.82]) for (const wz of [1.32, -1.3]) out.push({
    pos: tb => { const c = getCar(tb); return V3(c.x + wx * c.dir, 0.05, c.z + wz * c.dir); },
    dir: V3(0, 0.6, -dirSign * 0.8), t0: tv, t1});
  return out;
}

function updateStreet(S, shot, T) {
  hide(S);
  const cam = S.camera; cam.fov = 50; S.sparks.material.size = 0.09; cam.rotation.set(0, 0, 0);
  const t = T - shot.t0; // lokale Zeit
  updateRain(S.rain, T); updateRain(S.rainFar, T, 16); updateSplash(S.splash, T); updateSplash(S.splash2, T);
  let emitters = [], glass = [], fx = [], shardsE = [];
  mood(S, shot.id === 'back' || shot.id === 'later' ? 'fire' : 'day');
  const tvG = VANISH - shot.t0; // Zeitpunkt des Verschwindens in lokaler Zeit (falls in dieser Einstellung)

  // Verkehr mit 4 Spuren, z-Position abhängig von der Zeit
  const traffic = (tv, n = 14, base = 0, decel = 6, stopNear = 0) => {
    const list = [];
    for (let i = 0; i < n; i++) {
      const lane = i % 4, x = LANES[lane], dir = lane >= 2 ? 1 : -1, v = dir * (11 + (i * 7 % 5));
      const z0 = base + (lane >= 2 ? -1 : 1) * (8 + Math.floor(i / 4) * 17 + (i * 13 % 7)) + stopNear * dir;
      const c = S.cars[i];
      const get = tb => ({x, dir, z: slideZ(z0, v, tv, decel, tb)});
      const z = get(t).z;
      placeCar(c, x, z, dir, t, tv, t >= tv, (z - z0) / 0.34 * dir * (t < tv ? 1 : 0.15));
      list.push({c, get, x, dir, v, z0});
    }
    return list;
  };

  switch (shot.id) {
    case 'intro': {
      traffic(99, 10, 0);
      look(cam, V3(8.4, 1.62, 6), V3(1.5, 1.3, -18)); shake(cam, T, 0.006, 2);
      S.rig.visible = true;
      updateScreen(S.phone, S.drops, {t: T, notify: smooth(1.2, 1.6, t), wet: 1});
      S.phone.userData.caseM.opacity = 1; S.phone.userData.cg.visible = true;
      for (let i = 0; i < 4; i++) { const p = S.people[i]; p.visible = true; p.position.set(8.6 + (i % 2) * 1.4, 0.15, -6 - i * 5 + t * 1.2 * (i % 2 ? 1 : -1) * 0.5); p.rotation.y = i % 2 ? 0 : Math.PI; posePerson(p, {walk: T * 5 + i}); }
      break;
    }
    case 'cars_wide': {
      const tv = -0.01; const L = traffic(tv, 14, 0, 3.2);
      L.forEach(o => { emitters.push(...wheelEmitters(o.get, tv, tv + Math.abs(o.v) / 3.2, o.dir)); });
      look(cam, V3(7.6 + t * 0.05, 1.05, 14 - t * 0.4), V3(1.8, 0.9, -8)); shake(cam, T, 0.008, 3);
      break;
    }
    case 'cars_wheel': {
      // Kamera fährt neben dem rechten Vorderrad eines rutschenden Autos mit
      const c = S.cars[0]; const v = 7 - t * 1.4; const z = 20 - (7 * t - 0.7 * t * t);
      placeCar(c, 4.8, z, -1, t, -1, true, 0); c.userData.body.position.y = -0.12 + Math.sin(T * 40) * 0.006;
      c.userData.body.rotation.z = Math.sin(T * 23) * 0.004;
      const wl = clamp(1 - t / 2.2);
      c.userData.wheels.forEach((w, k) => { w.wireM.opacity = 1; w.wires.children.forEach((r, j) => { r.position.y = -easeOut(clamp((t - 0.5 - j * 0.25 - k * 0.1) / 0.9)) * 0.25; r.rotation.z = (j - 2) * 0.2 * clamp(t - 0.5); r.visible = r.position.y > -0.24; }); });
      c.updateMatrixWorld(true);
      const wp = c.userData.wheels.map(w => { const v = V3(); w.w.getWorldPosition(v); return v; });
      wp.forEach(p => emitters.push({pos: () => V3(p.x, 0.04, p.z), dir: V3(Math.sign(p.x - 4.8) * 0.4, 0.7, 1), t0: -1, t1: 9}));
      const front = wp.reduce((a, b) => (b.z < a.z && b.x < 4.8 ? b : a), wp.find(p => p.x < 4.8));
      // weitere Autos im Hintergrund
      for (let i = 1; i < 6; i++) { const cc = S.cars[i]; placeCar(cc, LANES[i % 4], z - 10 - i * 9, i % 4 >= 2 ? 1 : -1, t, -1, true, 0); }
      look(cam, V3(front.x - 1.9, 0.2, front.z + 0.7), V3(front.x, 0.22, front.z - 0.1)); cam.fov = 40; S.sparks.material.size = 0.035; shake(cam, T * 2, 0.008, 6);
      void v; void wl;
      break;
    }
    case 'cars_crash': {
      // hinteres Auto rutscht ungebremst in das stehende vordere
      const a = S.cars[0], b = S.cars[1];
      const ti = 0.9;
      const zb = t < ti ? 6 - 9 * t : 6 - 9 * ti - Math.min(1.6, (t - ti) * 2.2 - (t - ti) ** 2 * 0.6);
      const za = t < ti ? -2.2 : -2.2 - Math.min(2.4, (t - ti) * 4.5 - (t - ti) ** 2 * 1.6);
      placeCar(b, 1.6, zb + 0, -1, 1, 0, true, 0); placeCar(a, 1.6, za - 4.7, -1, 1, 0, true, 0);
      if (t > ti) { const k = Math.exp(-(t - ti) * 6); a.userData.body.rotation.x = -0.05 * k * Math.sin((t - ti) * 25); b.userData.body.rotation.x = 0.07 * k * Math.sin((t - ti) * 25); b.userData.body.rotation.y = 0.04 * clamp((t - ti) * 3); }
      emitters.push({pos: () => V3(1.6 - 0.82, 0.04, (t < ti ? 6 - 9 * t : zb) - 1.32), dir: V3(-0.2, 0.7, 1), t0: -1, t1: ti + 0.15});
      emitters.push({pos: () => V3(1.6 + 0.82, 0.04, (t < ti ? 6 - 9 * t : zb) - 1.32), dir: V3(0.2, 0.7, 1), t0: -1, t1: ti + 0.15});
      glass.push({pos: V3(1.6, 0.8, za - 4.7 + 2.1), dir: V3(0, 0.6, 0.4), t0: ti, t1: ti + 0.12});
      for (let i = 2; i < 9; i++) placeCar(S.cars[i], LANES[i % 4], -14 - i * 8 + (i % 3) * 3, i % 4 >= 2 ? 1 : -1, 1, 0, true, 0);
      S.cars[5].rotation.y += 0.3; S.cars[7].rotation.y -= 0.25;
      look(cam, V3(6.4, 1.35, 3.5), V3(1.3, 0.7, -4)); cam.fov = 46; shake(cam, T, 0.008, 7);
      if (t > ti && t < ti + 0.35) shake(cam, T * 8, 0.025, 8);
      break;
    }
    case 'soles': {
      const tv = 0.9;
      // Fußgänger auf dem Gehweg, gehen auf die Kamera zu
      const N = 6;
      for (let i = 0; i < N; i++) {
        const p = S.people[i]; p.visible = true;
        const x = 7.6 + (i % 3) * 1.2 + (i * 0.37 % 0.4), z0 = 7 - i * 2.3 - (i % 2) * 1.1;
        const fallT = 3.0 + i * 0.32 + (i % 2) * 0.25;
        const walkT = Math.min(t, fallT + 0.3);
        p.position.set(x, 0.15, z0 + walkT * 1.25); p.rotation.y = 0;
        const f = clamp((t - fallT) / 0.8);
        posePerson(p, {walk: walkT * 5.2 + i, fall: f, slipSide: (i % 2 ? 1 : -1)});
        p.userData.soles.forEach(s => s.visible = t < tv);
        if (i === 1) { // mit Regenschirm
          S.umbrella.visible = true; const hand = V3(); p.userData.armR.userData.fore.getWorldPosition(hand);
          p.updateMatrixWorld(true); p.userData.armR.userData.fore.getWorldPosition(hand);
          const fly = clamp((t - fallT - 0.2) / 1.2);
          S.umbrella.position.set(hand.x + fly * 1.2, hand.y - 0.3 + 0.2 + fly * 1.5 - fly * fly * 2.2, hand.z + fly * 1.0);
          S.umbrella.rotation.set(fly * 1.4, 0, -fly * 0.8);
        }
      }
      if (t < 2.4) { // tief bei den Schuhen
        const p = S.people[0]; p.updateMatrixWorld(true);
        look(cam, V3(p.position.x - 1.1, 0.42, p.position.z + 0.7), V3(p.position.x, 0.12, p.position.z + 0.05)); cam.fov = 40;
      } else {
        look(cam, V3(8.3, 1.4, 15.5), V3(8.8, 0.5, 4)); cam.fov = 48;
      }
      shake(cam, T, 0.006, 9);
      traffic(-1, 8, 0, 6); S.cars.slice(0, 8).forEach(c => { c.userData.body.position.y = -0.12; });
      break;
    }
    case 'pants': {
      // Wartende an der Bushaltestelle
      const tv = 0.7; const xs = [8.2, 8.9, 9.6, 8.5, 9.3], zs = [28, 29.3, 30.6, 31.8, 27.2];
      for (let i = 0; i < 5; i++) {
        const p = S.people[5 + i]; p.visible = true; p.position.set(xs[i], 0.15, zs[i]); p.rotation.y = -Math.PI / 2 + (i - 2) * 0.25;
        const jeans = i === 2; // Jeans mit Gürtel: bleibt oben
        const d = jeans ? 0 : easeOut(clamp((t - tv - i * 0.12) / 0.7));
        posePerson(p, {walk: 0, walkAmp: 0, pantsDrop: d, look: Math.sin(t * 2 + i) * 0.3 * clamp(t - 1.6)});
        p.userData.pants.children[1].visible = jeans || t < tv; // Bund weg
      }
      look(cam, V3(5.3, 1.35, 30.2), V3(9.0, 0.95, 29.6)); cam.fov = 48; shake(cam, T, 0.006, 10);
      cam.position.x -= t * 0.1;
      traffic(-1, 6, 30, 6); S.cars.slice(0, 6).forEach(c => { c.userData.body.position.y = -0.12; });
      break;
    }
    case 'balloons': {
      const tv = VANISH - shot.t0;
      const kid = S.people[10]; kid.visible = true; kid.scale.setScalar(0.62); kid.position.set(8.4, 0.15, 14); kid.rotation.y = -Math.PI / 2 - 0.3;
      posePerson(kid, {holdUp: 1 - smooth(tv + 0.6, tv + 1.4, t) * 0.6, look: 0}); kid.updateMatrixWorld(true);
      const hand = V3(); kid.userData.armR.userData.fore.getWorldPosition(hand); hand.y -= 0.17;
      S.balloons.forEach((b, i) => {
        const top = V3(hand.x - 0.3 + i * 0.3 + Math.sin(T * 1.3 + i) * 0.04, hand.y + 0.9 + (i % 2) * 0.18, hand.z + Math.cos(T + i) * 0.05);
        const gone = t >= tv + i * 0.05;
        b.visible = !gone; b.position.copy(top);
        const st = b.userData.string; st.visible = true;
        const fallen = clamp((t - tv) / 0.7);
        const end = gone ? V3(top.x, lerp(top.y - 0.2, hand.y - 0.9, easeOut(fallen)), top.z) : V3(top.x, top.y - 0.2, top.z);
        st.geometry.setFromPoints([hand, end]);
        const pf = S.puffs[i]; const k = clamp((t - tv - i * 0.05) / 0.35);
        pf.position.copy(top); pf.scale.setScalar(0.9 + k * 2.2); pf.material.opacity = k > 0 && k < 1 ? (1 - k) * 0.35 : 0;
      });
      const wom = S.people[11]; wom.visible = true; wom.position.set(9.8, 0.15, 12.6); wom.rotation.y = -Math.PI / 2 + 0.9;
      posePerson(wom, {look: -0.6});
      const pt = wom.userData.ponytail; const hairGone = t >= 3.5;
      pt.userData.band.visible = !hairGone; pt.userData.loose.visible = hairGone; pt.children[1].visible = !hairGone;
      // Kamera: erst Kind, dann Frau
      const k = smooth(2.5, 3.2, t);
      look(cam, V3(lerp(5.4, 8.6, k), lerp(1.1, 1.72, k), lerp(15.2, 11.3, k)), V3(lerp(8.4, 9.8, k), lerp(1.55, 1.62, k), lerp(14, 12.6, k)));
      cam.fov = lerp(55, 36, k); shake(cam, T, 0.005, 11);
      traffic(-1, 6, 14, 6); S.cars.slice(0, 6).forEach(c => { c.userData.body.position.y = -0.12; });
      break;
    }
    case 'last': {
      traffic(-1, 14, 0, 6); S.cars.slice(0, 14).forEach(c => { c.userData.body.position.y = -0.12; });
      S.cars[3].rotation.y += 0.35; S.cars[6].rotation.y -= 0.2;
      for (let i = 0; i < 5; i++) { const p = S.people[i]; p.visible = true; p.position.set(7.8 + (i % 3) * 1.3, 0.15, 4 - i * 2.6); posePerson(p, {fall: 1, slipSide: i % 2 ? 1 : -1}); p.userData.soles.forEach(s => s.visible = false); }
      look(cam, V3(9.6 - t * 0.2, 2.4, 16 - t * 0.8), V3(2, 0.6, -6)); cam.fov = 46; shake(cam, T, 0.005, 12);
      break;
    }
    case 'back': {
      // Gummi kehrt zurück: Reifen erscheinen dort, wo die Autos beim Verschwinden waren
      for (let i = 0; i < 4; i++) {
        const lane = i, x = LANES[lane], dir = lane >= 2 ? 1 : -1;
        const c = S.cars[i]; const zc = (dir > 0 ? 8 : -8) + dir * 2; // Auto steht hier
        placeCar(c, x, zc, dir, 1, 0, true, 0);
        if (i === 1) c.rotation.y += 0.2;
        for (let w = 0; w < 4; w++) {
          const tr = S.looseTires[i * 4 + w]; tr.visible = t >= 0.05;
          const wx = [-0.82, 0.82, -0.82, 0.82][w], wz = [1.32, 1.32, -1.3, -1.3][w];
          const zt = zc - dir * 14 + wz * dir; // 14 m weiter hinten
          const roll = clamp(t / 2.8); const fall = smooth(1.8, 3.0, t + w * 0.15);
          tr.position.set(x + wx * dir + roll * 0.6 * Math.sign(wx) + Math.sin(w) * 0.2, lerp(0.34, 0.1, fall), zt + dir * easeOut(roll) * (1.5 + w * 0.3));
          tr.rotation.set(0, Math.PI / 2, 0); tr.rotateOnAxis(V3(1, 0, 0), 0); tr.rotation.x = 0;
          tr.rotation.y = Math.PI / 2 + Math.sin(w * 2) * 0.3 * roll; tr.rotation.z = 0; tr.rotateX(fall * Math.PI / 2 * (w % 2 ? 1 : -1));
          tr.scale.set(1, 1, 1.9);
        }
      }
      for (let i = 4; i < 12; i++) placeCar(S.cars[i], LANES[i % 4], (i % 4 >= 2 ? 1 : -1) * (26 + i * 5), i % 4 >= 2 ? 1 : -1, 1, 0, true, 0);
      look(cam, V3(6.2, 2.0 + t * 0.1, 30 - t * 0.5), V3(2.5, 0.6, 12)); cam.fov = 50; shake(cam, T, 0.004, 13);
      S.cars[1].userData.body.rotation.z = 0.08;
      fx.push({type: 'flame', pos: V3(-1.6, 0.8, -10), r: 1.6, t0: -5, size: 1.4, power: 1, share: 3},
        {type: 'flame', pos: V3(4.8, 0.7, 10), r: 1.3, t0: -5, size: 1.2, share: 2},
        {type: 'flame', pos: V3(11.6, 3.5, -2), r: 2.5, t0: -5, size: 1.8, share: 3}, {type: 'flame', pos: V3(11.6, 7.2, -4), r: 2.0, t0: -5, size: 1.5, share: 2},
        {type: 'flame', pos: V3(-11.6, 4, -30), r: 3, t0: -5, size: 2.2, share: 3},
        {type: 'smoke', pos: V3(-1.6, 2, -10), r: 1.5, t0: -9, size: 4, rise: 2.5, share: 2}, {type: 'smoke', pos: V3(11, 8, -3), r: 3, t0: -9, size: 6, rise: 2.2, share: 3},
        {type: 'smoke', pos: V3(-11, 6, -30), r: 3, t0: -9, size: 8, rise: 2.5, share: 3});
      S.fireLights[0].position.set(-1.6, 2, -10); S.fireLights[1].position.set(10.5, 4, -2); S.fireLights[2].position.set(4.8, 2, 10);
      S.fireLights.forEach((l, i) => l.intensity = 90 * flicker(T, i));
      for (let i = 0; i < 4; i++) { const p = S.people[i]; p.visible = true; p.position.set(8 + i * 0.9, 0.15, 6 + i * 3); posePerson(p, {fall: 1, slipSide: 1}); }
      break;
    }
    case 'gas': {
      const ig = 4.2; // Zündung
      S.gasket.visible = false;
      // Gas strömt aus der Verbindung und dem Schacht (sichtbar als flimmernde Schwaden)
      if (t < ig + 0.1) fx.push({type: 'smoke', pos: V3(11.15, 0.75, 62), r: 0.25, t0: -3, size: 0.9, rise: 0.5, col: [0.75, 0.8, 0.85], alpha: 0.18, share: 2},
        {type: 'smoke', pos: V3(10.0, 0.25, 61), r: 0.4, t0: -3, size: 1.4, rise: 0.4, col: [0.75, 0.8, 0.85], alpha: 0.15, share: 2});
      // Auto rutscht auf Felgen heran, Funken fliegen
      const c = S.cars[0]; const zc = t => 92 - 9.5 * t + 0.4 * t * t;
      placeCar(c, 4.8, zc(t), -1, 1, 0, true, 0);
      emitters.push(...wheelEmitters(tb => ({x: 4.8, dir: -1, z: zc(tb)}), -1, 9, -1));
      for (let i = 1; i < 7; i++) placeCar(S.cars[i], LANES[i % 3], 66 + i * 8, i % 3 >= 2 ? 1 : -1, 1, 0, true, 0);
      for (let i = 0; i < 4; i++) { const p = S.people[i]; p.visible = true; p.position.set(8.0 + i * 0.7, 0.15, 50 - i * 2.2); p.rotation.y = Math.PI * 0.1; posePerson(p, {walk: 0, walkAmp: 0, look: 0.6, fall: t > ig + 0.15 ? clamp((t - ig - 0.15) / 0.7) : 0, slipSide: i % 2 ? 1 : -1}); }
      if (t >= ig) {
        fx.push({type: 'burst', pos: V3(10.4, 1.0, 62), r: 9, t0: ig, size: 6, rise: 2.5, power: 1.4, share: 5},
          {type: 'burstSmoke', pos: V3(10.4, 2, 62), r: 10, t0: ig + 0.2, size: 8, rise: 1.5, share: 3},
          {type: 'flame', pos: V3(10.8, 1.2, 62), r: 1.5, t0: ig + 0.6, size: 2.2, share: 3}, {type: 'flame', pos: V3(11.6, 4.5, 62), r: 2.5, t0: ig + 0.8, size: 2.0, share: 2},
          {type: 'smoke', pos: V3(11, 5, 62), r: 2, t0: ig + 1, size: 7, rise: 3, share: 2});
        shardsE.push({pos: V3(11.5, 4.5, 62), dir: V3(-1.4, 0.4, 0), t0: ig + 0.05, t1: ig + 0.25});
        const k = t - ig; S.fireLights[0].position.set(10, 3, 62); S.fireLights[0].intensity = (k < 0.6 ? 2500 * (1 - k / 0.6) + 200 : 200) * flicker(T, 1);
        S.fireLights[1].position.set(8, 6, 66); S.fireLights[1].intensity = k < 0.4 ? 1200 * (1 - k / 0.4) : 0;
      }
      if (t < 1.6) { look(cam, V3(10.1, 0.95, 63.3), V3(11.15, 0.65, 62)); cam.fov = 40; }
      else { look(cam, V3(6.6, 1.7, 40), V3(8.6, 2.0, 62)); cam.fov = 46; }
      shake(cam, T, 0.006, 21); if (t > ig && t < ig + 1.2) shake(cam, T * 9, 0.09 * (1 - (t - ig) / 1.2), 22);
      break;
    }
    case 'later': {
      // Luftbild: alles steht, Krankenwagen blinken
      for (let i = 0; i < 34; i++) {
        const lane = i % 4, c = S.cars[i], dir = lane >= 2 ? 1 : -1;
        const z = -60 + Math.floor(i / 4) * 12.5 + (i * 37 % 5) - (lane % 2) * 4;
        placeCar(c, LANES[lane] + Math.sin(i * 3.1) * 0.5, z, dir, 1, 0, true, 0); c.rotation.y += Math.sin(i * 1.7) * 0.25;
        if (c.userData.blue) { const on = Math.floor(T * 6) % 2; c.userData.blue[0].material.emissiveIntensity = on ? 5 : 0; c.userData.blue[1].material.emissiveIntensity = on ? 0 : 5; }
      }
      S.cars[32].position.set(-1.6, 0, -6); S.cars[33].position.set(4.8, 0, 12);
      [[-1.6, -40], [4.8, -18], [1.6, 4], [-4.8, 20]].forEach(([x, z], i) => fx.push({type: 'flame', pos: V3(x, 0.8, z), r: 1.6, t0: -5, size: 2.2, share: 2}, {type: 'smoke', pos: V3(x, 3, z), r: 2, t0: -9, size: 9, rise: 3, share: 2}));
      [[11.6, -25, 5], [-11.6, 8, 8], [11.6, 40, 4]].forEach(([x, z, y]) => fx.push({type: 'flame', pos: V3(x, y, z), r: 3.5, t0: -5, size: 3.5, share: 3}, {type: 'smoke', pos: V3(x, y + 4, z), r: 3, t0: -9, size: 14, rise: 3, share: 3}));
      S.fireLights[0].position.set(11, 6, -25); S.fireLights[1].position.set(-11, 9, 8); S.fireLights[2].position.set(0, 3, -18);
      S.fireLights.forEach((l, i) => l.intensity = 300 * flicker(T, i));
      S.blueLight.position.set(-1.6, 3, -6); S.blueLight.intensity = Math.floor(T * 6) % 2 ? 60 : 0;
      for (let i = 0; i < 10; i++) { const p = S.people[i]; p.visible = true; p.position.set(7.5 + (i % 3) * 1.2, 0.15, -30 + i * 6); p.rotation.y = i * 1.3; posePerson(p, {walk: 0, walkAmp: 0, look: Math.sin(T + i) * 0.4}); }
      look(cam, V3(14 - t * 0.5, 34 - t * 0.6, 30 - t * 1.0), V3(0, 0, -12 - t * 0.6)); cam.fov = 46;
      break;
    }
  }
  S.fire.visible = fx.some(f => f.type === 'flame' || f.type === 'burst'); S.smoke.visible = fx.some(f => f.type === 'smoke' || f.type === 'burstSmoke'); S.shards.visible = shardsE.length > 0; S.sparks.visible = emitters.length > 0; S.glassBits.visible = glass.length > 0;
  S.fireLights.forEach(l => l.visible = l.intensity > 0); S.blueLight.visible = S.blueLight.intensity > 0;
  updateSparks(S.sparks, emitters, t);
  updateParticles(S.fire, fx.filter(f => f.type === 'flame' || f.type === 'burst'), t);
  updateParticles(S.smoke, fx.filter(f => f.type === 'smoke' || f.type === 'burstSmoke'), t);
  updateSparks(S.shards, shardsE, t, 9.8);
  S.gasket.visible = shot.id !== 'gas';
  updateSparks(S.glassBits, glass, t, 9.8);
  cam.updateProjectionMatrix();
}
