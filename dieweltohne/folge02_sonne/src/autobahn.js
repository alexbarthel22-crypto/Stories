// Autobahn mittags in plötzlicher Dunkelheit: 130 km/h, einer bremst, Auffahrunfälle
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, asphaltTex, makeCar, sparkSystem, updateSparks} from './lib.js';
import {skyMaterial} from './beach.js';
import {particles, updateParticles} from './fx.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const LANES = [-4.6, -1.1, 2.4]; // eigene Fahrtrichtung (nach -z), x = Fahrstreifenmitte
const DT = 1 / 240, DUR = 8.2;

// Vorab berechnete Fahrphysik: Bremsen, Auffahren, Ausweichen
function simulate() {
  // [Spur, Start-z, Tempo m/s, Bremsbeginn s, Verzögerung m/s², Ausweichen]
  const defs = [
    [1, 0, 36, 4.55, 9.5, 0],      // 0: Kamerawagen
    [1, -38, 36, 3.0, 10, 0],      // 1: bremst zuerst (sieht im Dunkeln etwas)
    [1, -16, 36, 3.9, 7, 0],       // 2: reagiert zu spät -> fährt auf 1 auf
    [0, -28, 37, 3.6, 8, 0],       // 3: linke Spur
    [0, -6, 37, 4.2, 8, 1.6],      // 4: weicht nach rechts aus -> trifft 2
    [2, -22, 31, 3.5, 6, 0],       // 5: rechte Spur (Lkw-Tempo)
    [2, -55, 31, 3.2, 6, 0],
    [0, -70, 37, 3.3, 9, 0],
    [1, -80, 36, 3.1, 9, 0],
  ];
  const cars = defs.map(([ln, z, v, tb, dec, sw]) => ({x: LANES[ln], z, v, tb, dec, sw, yaw: 0, yv: 0, hit: -1, brake: 0}));
  const crashes = []; const frames = [];
  for (let s = 0, t = 0; t <= DUR; s++, t = s * DT) {
    for (const c of cars) {
      if (t >= c.tb) { c.v = Math.max(0, c.v - c.dec * DT); c.brake = 1; }
      if (c.sw && t > c.tb - 0.2) c.x += Math.min(c.sw, 3) * DT * (t < c.tb + 0.8 ? 1.4 : 0);
      c.z -= c.v * DT; c.yaw += c.yv * DT; c.yv *= Math.exp(-2.2 * DT);
    }
    // Kollisionen gleicher Spur (Abstand Fahrzeugmitte < 4.4 m, seitlich < 1.9 m)
    for (let i = 0; i < cars.length; i++) for (let j = 0; j < cars.length; j++) {
      if (i === j) continue; const a = cars[i], b = cars[j]; // b fährt auf a auf (b hinter a: b.z > a.z)
      if (b.z > a.z && b.z - a.z < 4.4 && Math.abs(a.x - b.x) < 1.9 && b.v > a.v + 0.5) {
        const dv = b.v - a.v; a.v += dv * 0.55; b.v -= dv * 0.75; a.yv += (a.x < b.x ? 1 : -1) * dv * 0.12; b.yv -= (a.x < b.x ? 1 : -1) * dv * 0.08;
        b.z = a.z + 4.4; crashes.push({t, pos: V3((a.x + b.x) / 2, 0.8, a.z + 2.2), dv});
      }
    }
    if (s % 8 === 0) frames.push(cars.map(c => [c.x, c.z, c.yaw, c.brake, c.v]));
  }
  return {frames, crashes, n: cars.length};
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), skyMaterial()); sky.renderOrder = -10; scene.add(sky);
  sky.material.uniforms.day.value = 0; sky.material.uniforms.stars.value = 0.9;
  scene.fog = new THREE.Fog('#020305', 40, 320);
  scene.add(new THREE.HemisphereLight('#3d4f75', '#08080a', 0.06));
  // Fahrbahn: zwei Richtungsfahrbahnen mit Mittelleitplanke
  const asp = asphaltTex(); asp.repeat.set(3, 140);
  for (const cx of [-1.1, -15]) { const rd = mesh(new THREE.PlaneGeometry(12.5, 1400), new THREE.MeshStandardMaterial({map: asp, roughness: 0.8}), cx, 0, -500, scene); rd.rotation.x = -Math.PI / 2; rd.castShadow = false; }
  const lineM = mat('#e9e9e2', {roughness: 0.5});
  for (let z = 100; z > -1100; z -= 12) for (const x of [-2.85, 0.65, -16.75, -13.25]) { const l = mesh(new THREE.PlaneGeometry(0.15, 6), lineM, x, 0.005, z, scene); l.rotation.x = -Math.PI / 2; l.castShadow = false; }
  for (const x of [-6.9, 4.7, -8.2, -21.2]) { const l = mesh(new THREE.PlaneGeometry(0.25, 1400), lineM, x, 0.005, -500, scene); l.rotation.x = -Math.PI / 2; l.castShadow = false; }
  // Leitplanken und Leitpfosten mit Reflektoren
  const rail = mat('#a9adb2', {metalness: 0.85, roughness: 0.35});
  for (const x of [-7.6, 5.6]) { mesh(new THREE.BoxGeometry(0.06, 0.32, 1400), rail, x, 0.62, -500, scene); for (let z = 100; z > -1100; z -= 4) mesh(new THREE.BoxGeometry(0.12, 0.7, 0.12), mat('#7d8288', {metalness: 0.6}), x + (x < 0 ? -0.1 : 0.1), 0.35, z, scene); }
  const reflM = mat('#ffffff', {emissive: '#fff4e0', emissiveIntensity: 0.6}), reflO = mat('#ff9a2a', {emissive: '#ff8a1a', emissiveIntensity: 0.8});
  for (let z = 100; z > -1100; z -= 50) { mesh(new THREE.BoxGeometry(0.12, 1.0, 0.12), mat('#f2f2ee'), 7.0, 0.5, z, scene); mesh(new THREE.BoxGeometry(0.13, 0.12, 0.05), reflM, 7.0, 0.85, z + 0.07, scene); mesh(new THREE.BoxGeometry(0.13, 0.12, 0.05), reflO, 7.0, 0.85, z - 0.07, scene); }
  // Schilderbrücke
  const gantry = new THREE.Group(); gantry.position.set(0, 0, -150); scene.add(gantry);
  for (const x of [-22, 7.5]) mesh(new THREE.BoxGeometry(0.4, 7.5, 0.4), mat('#8a8f95', {metalness: 0.6}), x, 3.75, 0, gantry);
  mesh(new THREE.BoxGeometry(30, 0.6, 0.6), mat('#8a8f95', {metalness: 0.6}), -7.25, 7.3, 0, gantry);
  const signT = canvasTex(512, 256, (g, w, h) => { g.fillStyle = '#1f5fae'; g.fillRect(0, 0, w, h); g.strokeStyle = '#fff'; g.lineWidth = 8; g.strokeRect(10, 10, w - 20, h - 20);
    g.fillStyle = '#fff'; g.font = '600 64px Plex'; g.fillText('Hannover', 40, 110); g.fillText('Kassel', 40, 200); g.fillStyle = '#fff'; g.fillRect(360, 60, 110, 70); g.fillStyle = '#1f5fae'; g.font = '700 54px Plex'; g.fillText('A7', 375, 117); });
  const sgn = mesh(new THREE.PlaneGeometry(8, 4), new THREE.MeshStandardMaterial({map: signT, emissive: '#ffffff', emissiveMap: signT, emissiveIntensity: 0.08}), -1.1, 9.2, 0.35, gantry);
  // Böschung, Bäume als Silhouetten
  const r = rng(12);
  for (let i = 0; i < 160; i++) { const s = r() < 0.5 ? -1 : 1, x = s > 0 ? 12 + r() * 30 : -30 - r() * 30, z = 100 - r() * 1100; const h = 6 + r() * 8;
    mesh(new THREE.ConeGeometry(1.6 + r(), h, 7), mat('#0e1410', {roughness: 1}), x, h / 2, z, scene); }
  mesh(new THREE.PlaneGeometry(400, 1400), mat('#0c100c', {roughness: 1}), 0, -0.02, -500, scene).rotation.x = -Math.PI / 2;

  // Autos mit eigenen Brems- und Scheinwerfern
  const sim = simulate();
  const cars = Array.from({length: sim.n}, (_, i) => { const c = makeCar(40 + i, {color: ['#3a3a3d', '#c8102e', '#2b5fa8', '#8a9099', '#2a2b2e', '#d9d4c7', '#6fa3c9', '#3a6b4a', '#e5b31b'][i], long: i === 5 || i === 6 ? 6.5 : 4.2}); scene.add(c);
    const tails = [], heads = [];
    c.traverse(o => { if (o.isMesh && o.material.emissive && o.material.color.getHexString() === 'ff2a1a') { o.material = o.material.clone(); tails.push(o.material); }
      if (o.isMesh && o.material.emissive && o.material.color.getHexString() === 'fff6d8') heads.push(o); });
    c.userData.tails = tails; return c; });
  // Gegenverkehr
  const oncoming = Array.from({length: 8}, (_, i) => { const c = makeCar(60 + i); c.rotation.y = Math.PI; scene.add(c); return c; });
  const heads = [0, 1, 2, 3, 4].map(() => { const l = new THREE.SpotLight('#fff2d6', 0, 120, 0.42, 0.45, 1.2); l.castShadow = false; scene.add(l, l.target); return l; });
  const onHeads = [0, 1].map(() => { const l = new THREE.SpotLight('#fff2d6', 0, 80, 0.45, 0.5, 1.3); scene.add(l, l.target); return l; });
  const sparks = sparkSystem(1600, 0.1); scene.add(sparks);
  const glass = sparkSystem(400, 0.05); glass.material.blending = THREE.NormalBlending; glass.material.vertexColors = false; glass.material.color = new THREE.Color('#cfe0f0'); glass.material.needsUpdate = true; scene.add(glass);
  const smoke = particles(600, 'smoke'); scene.add(smoke);
  const camera = new THREE.PerspectiveCamera(55, 1080 / 1920, 0.05, 1500); scene.add(camera);
  const dash = new THREE.Group(); camera.add(dash); dash.position.set(0, -0.62, -0.9);
  mesh(new THREE.BoxGeometry(2.4, 0.3, 0.6), mat('#0b0b0c', {roughness: 0.6}), 0, 0, 0, dash);
  const wheel = mesh(new THREE.TorusGeometry(0.19, 0.025, 10, 32), mat('#121214', {roughness: 0.5}), -0.02, 0.2, 0.25, dash); wheel.rotation.x = -0.4;
  const gauge = mesh(new THREE.PlaneGeometry(0.07, 0.022), new THREE.MeshBasicMaterial({color: '#c8641a'}), -0.02, 0.17, 0.05, dash);
  mesh(new THREE.BoxGeometry(0.04, 0.9, 0.04), mat('#0b0b0c'), -0.62, 0.5, -0.05, dash).rotation.z = -0.45;
  mesh(new THREE.BoxGeometry(0.04, 0.9, 0.04), mat('#0b0b0c'), 0.62, 0.5, -0.05, dash).rotation.z = 0.45;

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0; renderer.toneMappingExposure = 1.15;
    const fi = Math.min(sim.frames.length - 1, Math.floor(t / (8 * DT))), F = sim.frames[fi];
    cars.forEach((c, i) => { const [x, z, yaw, br, v] = F[i]; c.position.set(x, 0, z); c.rotation.set(0, Math.PI + yaw, 0);
      c.userData.tails.forEach(m => { m.emissiveIntensity = br ? 4 : 1.0; });
      c.userData.wheels.forEach(w => { w.spin.rotation.x -= 0; });
      c.userData.body.rotation.x = br && v > 1 ? -0.025 : 0; c.visible = i > 0 || true; });
    oncoming.forEach((c, i) => { c.position.set(-15 + [-3, 1.5][i % 2], 0, -900 + ((i * 140 + t * 36) % 1000)); });
    // Scheinwerferkegel
    heads.forEach((l, k) => { const c = cars[k]; const f = V3(0, 0, -1).applyAxisAngle(V3(0, 1, 0), c.rotation.y - Math.PI);
      l.position.copy(c.position).add(V3(0, 0.75, 0)).addScaledVector(f, 2.3); l.target.position.copy(l.position).addScaledVector(f, 30).add(V3(0, -1.6, 0)); l.intensity = k === 0 ? 150 : 45; });
    let near = oncoming.filter(c => Math.abs(c.position.z - cars[0].position.z) < 120).slice(0, 2);
    onHeads.forEach((l, k) => { const c = near[k]; if (!c) { l.intensity = 0; return; } l.position.copy(c.position).add(V3(0, 0.75, -2.3 * -1)); l.target.position.copy(l.position).add(V3(0, -1.5, 25)); l.intensity = 160; });
    // Unfallfolgen
    const em = [], sm = []; let sh = 0;
    sim.crashes.filter(c => c.dv > 2).forEach((c, k) => { if (t >= c.t) { const a = t - c.t; if (a < 0.7) em.push({pos: c.pos, dir: V3((k % 2 ? 1 : -1) * 0.6, 0.6, 0.4), t0: c.t, t1: c.t + 0.25});
      sm.push({type: 'smoke', pos: c.pos, r: 1.2, t0: c.t, size: 1.4, rise: 1.2, alpha: 0.35, share: 1}); if (Math.hypot(c.pos.x - camera.position.x, c.pos.z - camera.position.z) < 40) sh = Math.max(sh, 0.12 * Math.exp(-a * 3)); } });
    updateSparks(sparks, em.length ? em : [{pos: V3(0, -50, 0), dir: V3(0, 1, 0), t0: -9, t1: -8}], t);
    updateSparks(glass, em.length ? em.map(e => ({...e, dir: V3(e.dir.x, 0.3, -0.3)})) : [{pos: V3(0, -50, 0), dir: V3(0, 1, 0), t0: -9, t1: -8}], t, 6);
    updateParticles(smoke, sm.length ? sm : [{type: 'smoke', pos: V3(0, -99, 0), r: 1, t0: 99, share: 1}], t, V3(0.5, 0, 0.2));
    // Kamera: hinter dem eigenen Wagen, leicht erhöht. Beim Bremsen nickt sie nach vorn
    const c0 = cars[0]; const [, , , br0, v0] = F[0];
    const pitch = br0 && v0 > 0.5 ? 1 : 0;
    c0.visible = false; camera.position.set(c0.position.x - 0.35, 1.25 - pitch * 0.12, c0.position.z - 0.3);
    camera.position.x += noise1(T * 9, 2) * (0.02 + sh); camera.position.y += noise1(T * 11, 5) * (0.015 + sh);
    camera.lookAt(c0.position.x - 0.3, 0.9 - pitch * 2.5, c0.position.z - 45);
    camera.fov = 55; camera.updateProjectionMatrix();
  }};
}
