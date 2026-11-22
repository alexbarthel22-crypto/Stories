// Stufe 5: Abends in der Innenstadt neben dem Zoo. Löwen laufen die Straße herunter, Menschen rennen,
// eine Straßenbahn macht eine Notbremsung, Leute klettern aufs Wartehäuschen, ein Löwe springt auf ein Autodach und brüllt.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, asphaltTex, tileTex, skyDome, easeIn, easeOut, makePerson, posePerson, envMap, makeCar, sparkSystem, updateSparks} from './lib.js';
import {makeLion, poseLion} from './lion.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.45;
  scene.fog = new THREE.Fog('#c79a7e', 60, 340);
  scene.add(skyDome('#2c3566', '#c0725a', '#f3b27c', 800));
  const hemi = new THREE.HemisphereLight('#ffd6b8', '#3a3440', 0.85); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#ffb37a', 2.2); sun.position.set(-40, 26, -60); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -40, right: 40, top: 40, bottom: -40, near: 1, far: 220}); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.04; scene.add(sun, sun.target);
  // Straße entlang z, Gehwege, Schienen
  const asT = asphaltTex(); asT.repeat.set(4, 60);
  mesh(new THREE.PlaneGeometry(16, 600), new THREE.MeshStandardMaterial({map: asT, roughness: 0.92}), 0, 0, -150, scene).rotation.x = -Math.PI / 2;
  const swT = tileTex('#aaa49a', '#9e988f'); swT.repeat.set(3, 120);
  for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(6, 0.15, 600), new THREE.MeshStandardMaterial({map: swT, roughness: 0.9}), s * 11, 0.075, -150, scene).castShadow = false;
  const railM = mat('#8e9398', {metalness: 0.9, roughness: 0.3});
  for (const x of [-0.72, 0.72]) mesh(new THREE.BoxGeometry(0.08, 0.04, 600), railM, x, 0.02, -150, scene).castShadow = false;
  const lineM = new THREE.MeshStandardMaterial({color: '#e8e6de', roughness: 0.8, polygonOffset: true, polygonOffsetFactor: -1});
  for (const x of [-3.4, 3.4]) for (let z = 40; z > -340; z -= 9) { const l = mesh(new THREE.PlaneGeometry(0.15, 4.5), lineM, x, 0.008, z, scene); l.rotation.x = -Math.PI / 2; l.castShadow = false; }
  // Häuser beidseitig, Zoo-Eingang links hinten
  { const r = rng(21); const cols = ['#c9b39a', '#b4bcc4', '#d6c6ae', '#a89a8c', '#c2a894', '#e0d4c0'];
    for (const s of [-1, 1]) for (let z = 30, i = 0; z > -320; i++) { const w = 12 + r() * 10, h = 14 + r() * 16;
      if (!(s < 0 && z < -60 && z > -100)) mesh(new THREE.BoxGeometry(10, h, w - 0.4), new THREE.MeshStandardMaterial({map: facadeTex(cols[i % 6], i * 7 + (s > 0 ? 3 : 0), Math.round(h / 3.3), 4), roughness: 0.85}), s * 19, h / 2, z - w / 2, scene);
      z -= w; } }
  const gateM = mat('#3a5a32'); mesh(new THREE.BoxGeometry(0.8, 6, 0.8), gateM, -14.5, 3, -62, scene); mesh(new THREE.BoxGeometry(0.8, 6, 0.8), gateM, -14.5, 3, -98, scene);
  const zooSign = canvasTex(512, 128, (g, w, h) => { g.fillStyle = '#3a5a32'; g.fillRect(0, 0, w, h); g.fillStyle = '#f2ead6'; g.font = 'bold 84px sans-serif'; g.textAlign = 'center'; g.fillText('ZOO', w / 2, 98); });
  const zs = mesh(new THREE.BoxGeometry(0.3, 2.4, 36), [mat('#3a5a32'), mat('#3a5a32'), mat('#3a5a32'), mat('#3a5a32'), new THREE.MeshStandardMaterial({map: zooSign}), new THREE.MeshStandardMaterial({map: zooSign})], -14.5, 6.6, -80, scene);
  zs.material[0] = new THREE.MeshStandardMaterial({map: zooSign}); zs.material[1] = zs.material[0];
  { const leafM = mat('#3f6e2c'), trunkM = mat('#5a4030'); const r = rng(5); for (let i = 0; i < 12; i++) { const z = -64 - i * 3; mesh(new THREE.CylinderGeometry(0.25, 0.3, 4, 6), trunkM, -18 - r() * 6, 2, z, scene); mesh(new THREE.IcosahedronGeometry(2.6, 1), leafM, -18 - r() * 6, 5.5, z, scene); } }
  // Laternen
  const poleM = mat('#2b2f33', {metalness: 0.6}); const lampM = new THREE.MeshStandardMaterial({color: '#fff1c8', emissive: '#ffd890', emissiveIntensity: 1.5});
  for (let z = 20; z > -200; z -= 22) for (const s of [-1, 1]) { mesh(new THREE.CylinderGeometry(0.07, 0.09, 6, 8), poleM, s * 8.6, 3, z, scene); mesh(new THREE.BoxGeometry(0.8, 0.14, 0.3), lampM, s * 8.2, 6, z, scene); }
  // Wartehäuschen rechts
  const shelter = new THREE.Group(); shelter.position.set(9.6, 0.15, -6); scene.add(shelter);
  const glassM = new THREE.MeshPhysicalMaterial({color: '#cfe0ea', transparent: true, opacity: 0.3, roughness: 0.05, depthWrite: false});
  mesh(new THREE.BoxGeometry(1.6, 0.08, 4.4), mat('#5a6068', {metalness: 0.5}), 0, 2.5, 0, shelter);
  for (const [x, z] of [[-0.7, -2.1], [0.7, -2.1], [-0.7, 2.1], [0.7, 2.1]]) mesh(new THREE.BoxGeometry(0.07, 2.5, 0.07), mat('#5a6068', {metalness: 0.5}), x, 1.25, z, shelter);
  mesh(new THREE.PlaneGeometry(4.2, 2.2), glassM, 0.75, 1.3, 0, shelter).rotation.y = Math.PI / 2;
  // Straßenbahn (kommt von hinten, Notbremsung)
  const tram = new THREE.Group(); scene.add(tram);
  { const tramM = mat('#c8202a', {roughness: 0.4, metalness: 0.2}), white = mat('#f2f2ee', {roughness: 0.4}), twM = new THREE.MeshStandardMaterial({color: '#1d2630', roughness: 0.1, metalness: 0.5, emissive: '#ffe0a8', emissiveIntensity: 0.25});
    for (const dz of [0, -9.6, -19.2]) { mesh(new THREE.BoxGeometry(2.4, 1.0, 9.2), tramM, 0, 0.8, dz, tram); mesh(new THREE.BoxGeometry(2.4, 1.3, 9.2), white, 0, 1.95, dz, tram); mesh(new THREE.BoxGeometry(2.3, 0.3, 9.0), white, 0, 2.75, dz, tram);
      for (const s of [-1, 1]) { const w = mesh(new THREE.PlaneGeometry(8.6, 0.95), twM, s * 1.21, 2.0, dz, tram); w.rotation.y = s * Math.PI / 2; } }
    mesh(new THREE.PlaneGeometry(2.0, 1.1), twM, 0, 2.05, 4.61, tram);
    const hl = new THREE.MeshStandardMaterial({color: '#fff', emissive: '#fff4d0', emissiveIntensity: 2.5}); for (const s of [-1, 1]) mesh(new THREE.CircleGeometry(0.14, 12), hl, s * 0.8, 0.75, 4.61, tram);
    mesh(new THREE.BoxGeometry(0.05, 1.6, 0.05), mat('#222'), 0, 3.7, 0, tram).rotation.x = 0.6; }
  const sparks = sparkSystem(900, 0.18); scene.add(sparks);
  // Autos: stehen am Rand, eins mitten auf der Fahrbahn (Löwe springt drauf)
  const cars = []; { const spots = [[-6, 10, 0], [-6, 22, 0], [6, -18, Math.PI], [-6, -26, 0], [6, -40, Math.PI], [-6, -52, 0], [6, 14, Math.PI]];
    spots.forEach(([x, z, ry], i) => { const c = makeCar(i + 3); c.position.set(x, 0, z); c.rotation.y = ry; scene.add(c); cars.push(c); }); }
  const hero = makeCar(2, {color: '#2b5fa8'}); hero.position.set(3.2, 0, 4); hero.rotation.y = Math.PI + 0.15; scene.add(hero);
  // Menschen
  const people = []; { const r = rng(61); for (let i = 0; i < 26; i++) { const p = makePerson(700 + i); const side = r() < 0.5 ? -1 : 1;
      const x = side * (9 + r() * 3), z = 10 - r() * 60; scene.add(p); people.push({p, x, z, side, ph: r() * 6, dly: r() * 0.9, sp: 4.5 + r() * 2}); } }
  const climbers = [makePerson(801, {top: '#e2b23a'}), makePerson(802, {top: '#4aa3c7', longHair: true})]; climbers.forEach(p => scene.add(p));
  // Löwen
  const lions = [makeLion(21, {male: true, scale: 1.05}), makeLion(22, {male: false}), makeLion(23, {male: false}), makeLion(24, {male: false, scale: 0.95})];
  lions.forEach(l => scene.add(l));
  const LP = [[0, 0], [-3.5, -5], [3.0, -8], [-1.0, -12]];

  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.05, 1500); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const t = T - 39;
    // Löwen laufen aus dem Zoo die Straße herunter (Richtung +z, auf die Kamera zu)
    lions.forEach((l, i) => { const [ox, oz] = LP[i]; let z = -58 + oz + 7.0 * t + Math.max(0, t - 1) * 0.8 * t, x = ox + Math.sin(t * 0.7 + i) * 0.8;
      let ry = 0, o = {gait: T * 11 + i, walk: 1, run: 1, t: T};
      if (i === 0) { // der große Löwe: rennt bis zum Auto, springt aufs Dach (45.6), brüllt
        const jT = 45.4; z = Math.min(z, 0.2);
        if (T > jT - 1.4) { const k = clamp((T - (jT - 1.4)) / 1.4); x = lerp(x, 3.2, k); }
        if (T > jT) { const j = clamp((T - jT) / 0.6); x = 3.2; z = lerp(0.2, 4.0, j); const y = Math.sin(j * Math.PI) * 1.0 + 1.45 * easeOut(j); l.position.set(x, y, z); o = j < 1 ? {leap: j, t: T} : {roar: smooth(46.3, 46.6, T) * (1 - smooth(47.6, 47.9, T)), lookUp: 0.2, t: T}; poseLion(l, o); l.rotation.set(0, 0, 0); return; }
      }
      if (i > 0 && T > 44) z = Math.min(z, -2 - i * 2.5); // bleiben hinter dem Auto
      if (i > 0 && z >= -2 - i * 2.5) { o = {gait: T * 6 + i, walk: 0.6, run: 0, t: T, roar: i === 2 ? smooth(45.0, 45.3, T) * (1 - smooth(46.0, 46.3, T)) : 0}; ry = (i - 2) * 0.4; }
      l.position.set(x, 0, z); l.rotation.set(0, ry, 0); poseLion(l, o);
    });
    // Straßenbahn: fährt Richtung Kamera, Vollbremsung ab 42.2, steht bei 44.0 (Funken an den Rädern)
    const tz = (() => { const v0 = 9; if (T < 42.2) return -40 + v0 * (T - 39); const b = clamp((T - 42.2) / 1.8); return -40 + v0 * 3.2 + v0 * 1.8 * (b - b * b / 2); })();
    tram.position.set(0, 0, tz); tram.rotation.x = T > 42.2 && T < 44.3 ? 0.01 * Math.sin((T - 42.2) * 9) : 0;
    updateSparks(sparks, T > 42.2 && T < 44.0 ? [-1, 1].flatMap(s => [0, -9.6].map(dz => ({pos: born => V3(s * 0.72, 0.1, (born < 42.2 ? -40 + 9 * (born - 39) : -40 + 28.8 + 16.2 * (clamp((born - 42.2) / 1.8) - clamp((born - 42.2) / 1.8) ** 2 / 2)) + dz + 3), dir: V3(s * 0.4, 0.5, -1), t0: 42.2, t1: 44.0}))) : [], T, 9.8);
    // Menschen: bummeln, dann rennen sie zur Seite bzw. nach vorn weg
    people.forEach(({p, x, z, side, ph, dly, sp}, i) => { const alarm = 40.4 + dly + Math.max(0, (-z) * 0.02);
      if (T < alarm) { p.position.set(x, 0.15, z + (i % 2 ? 1 : -1) * 0.6 * (T - 39)); p.rotation.set(0, i % 2 ? 0 : Math.PI, 0); posePerson(p, {walk: T * 5 + ph, walkAmp: 0.6}); return; }
      const k = T - alarm; p.position.set(x + side * Math.min(2.5, k * 1.5), 0.15, z + (i % 2 ? 1 : -1) * 0.6 * (alarm - 39) + k * sp); p.rotation.set(0, side * 0.3, 0);
      posePerson(p, {walk: T * 14 + ph, walkAmp: 1.3, armsUp: 0.15}); });
    // zwei klettern aufs Wartehäuschen (43.0 – 45.0)
    climbers.forEach((p, i) => { const k = smooth(42.8 + i * 0.4, 44.6 + i * 0.4, T); p.position.set(9.6 + (i ? 0.25 : -0.25), 0.15 + 2.42 * easeOut(k), -6.8 + i * 1.4); p.rotation.set(0, -Math.PI / 2, 0); posePerson(p, {walk: T * 10, walkAmp: k < 1 ? 0.8 : 0});
      if (k > 0 && k < 1) { p.userData.armL.rotation.x = p.userData.armR.rotation.x = -2.8; }
      if (k >= 1) { p.userData.armL.rotation.z = -0.5; p.userData.armR.rotation.z = 0.5; p.userData.head.rotation.x = 0.4; } });
    // Kamera: 39–42.2 hohe Totale die Straße hinunter; 42.2–45 Bahn bremst (seitlich); 45–48 tief vor dem Auto, Löwe brüllt
    if (T < 42.2) { const k = smooth(39, 42.2, T); camera.position.set(lerp(2, 1.2, k), lerp(6, 4.2, k), 16); camera.lookAt(0, lerp(1.5, 1.2, k), lerp(-60, -30, k)); camera.fov = 40; }
    else if (T < 45.0) { const k = smooth(42.2, 45, T); camera.position.set(-8.6, 1.7, lerp(1, 4, k)); camera.lookAt(lerp(0, 2, k), 1.5, lerp(-10, -8, k)); camera.fov = 52; }
    else { camera.position.set(1.2 + noise1(T, 4) * 0.03, 0.9, 11.5); camera.lookAt(2.8, 2.2, 3.5); camera.fov = 50;
      if (T > 45.95 && T < 46.5) { const sh = 0.06 * (1 - (T - 45.95) / 0.55); camera.position.x += Math.sin(T * 60) * sh; camera.position.y += Math.cos(T * 47) * sh; } }
    hero.userData.body.rotation.z = T > 45.95 && T < 46.8 ? 0.03 * Math.sin((T - 45.95) * 25) * Math.exp(-(T - 45.95) * 4) : 0;
    camera.updateProjectionMatrix();
  }};
}
