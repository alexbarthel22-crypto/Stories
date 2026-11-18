// Umspannwerk und Kraftwerk: die Netzfrequenz fällt, Schalter lösen aus, Lichtbögen, dann geht alles aus
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, sparkSystem, updateSparks} from './lib.js';
import {skyMaterial} from './beach.js';
import {particles, updateParticles} from './fx.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const OFF = 4.4; // Abschaltung (s nach Beginn der Einstellung)
const ARCS = [[1.4, V3(-6, 6.5, -8)], [2.6, V3(5, 6.5, -14)], [3.5, V3(-2, 6.5, -20)], [4.25, V3(3, 6.5, -6)]];

function pylon(scene, x, z, h = 38) {
  const g = new THREE.Group(); g.position.set(x, 0, z); scene.add(g); const s = mat('#5d636b', {metalness: 0.7, roughness: 0.5});
  for (const [a, b] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const l = mesh(new THREE.BoxGeometry(0.3, h, 0.3), s, a * 2.2, h / 2, b * 2.2, g); l.rotation.z = -a * 0.06; l.rotation.x = b * 0.06; }
  for (const y of [h * 0.6, h * 0.78, h * 0.95]) mesh(new THREE.BoxGeometry(y > h * 0.9 ? 10 : 16, 0.35, 0.35), s, 0, y, 0, g);
  for (let y = 3; y < h; y += 4) { const c = mesh(new THREE.BoxGeometry(5, 0.12, 0.12), s, 0, y, 2.1, g); c.rotation.z = 0.7; const d = mesh(new THREE.BoxGeometry(5, 0.12, 0.12), s, 0, y, -2.1, g); d.rotation.z = -0.7; }
  return g;
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), skyMaterial()); sky.renderOrder = -10; scene.add(sky);
  sky.material.uniforms.day.value = 1; sky.material.uniforms.stars.value = 0;
  scene.fog = new THREE.Fog('#b4c6da', 120, 900);
  scene.add(new THREE.HemisphereLight('#c8dcf2', '#5a5248', 1.0));
  { const sl = new THREE.DirectionalLight('#fff3dc', 2.6); sl.position.set(-40, 80, 30); scene.add(sl); }
  mesh(new THREE.PlaneGeometry(2000, 2000), mat('#20201c', {roughness: 1}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(40, 50), mat('#55534e', {roughness: 0.95}), 0, 0.01, -12, scene).rotation.x = -Math.PI / 2; // Schotter
  // Schaltfeld: Trafos, Leistungsschalter, Sammelschienen
  const steel = mat('#9aa0a7', {metalness: 0.75, roughness: 0.35}), porc = mat('#7a3b2a', {roughness: 0.4});
  for (const [x, z] of [[-10, -4], [10, -4]]) { const g = new THREE.Group(); g.position.set(x, 0, z); scene.add(g);
    mesh(new THREE.BoxGeometry(6, 4.5, 4), mat('#6f7a6a', {roughness: 0.6}), 0, 2.25, 0, g);
    for (let k = 0; k < 8; k++) mesh(new THREE.BoxGeometry(0.15, 3.5, 3.6), mat('#5e685a'), -3.2 - k * 0.0, 2.2, 0, g).position.x = -3.1 + (k % 2) * 6.2;
    for (const dx of [-1.6, 0, 1.6]) { mesh(new THREE.CylinderGeometry(0.18, 0.28, 2.2, 10), porc, dx, 5.6, 0, g); } }
  const breakers = [];
  for (let row = 0; row < 3; row++) for (let i = -3; i <= 3; i++) { const x = i * 3, z = -10 - row * 6;
    mesh(new THREE.BoxGeometry(0.5, 3, 0.5), steel, x, 1.5, z, scene); mesh(new THREE.CylinderGeometry(0.15, 0.22, 2.4, 10), porc, x, 4.2, z, scene);
    const bar = mesh(new THREE.BoxGeometry(0.12, 1.6, 0.12), steel, x, 6.0, z, scene); breakers.push(bar); }
  for (const z of [-10, -16, -22]) mesh(new THREE.BoxGeometry(22, 0.12, 0.12), steel, 0, 7.0, z, scene);
  // Strahler auf Masten
  const floods = [[-14, 2], [14, 2], [0, -28]].map(([x, z]) => { mesh(new THREE.CylinderGeometry(0.1, 0.12, 12, 8), steel, x, 6, z, scene);
    const l = new THREE.SpotLight('#ffe8c4', 0, 60, 0.8, 0.5, 1.3); l.position.set(x, 11.8, z); l.target.position.set(x * 0.3, 0, -12); scene.add(l, l.target);
    const lamp = mesh(new THREE.BoxGeometry(0.7, 0.35, 0.3), new THREE.MeshStandardMaterial({color: '#222', emissive: '#ffe8c4', emissiveIntensity: 3}), x, 12, z, scene); return {l, lamp}; });
  // Freileitung zum Kraftwerk
  const pyl = [[-12, -60], [-30, -160], [-55, -270]].map(([x, z]) => pylon(scene, x, z));
  const wireM = new THREE.LineBasicMaterial({color: '#3a3f46'});
  for (const dx of [-7, 0, 7]) { const pts = []; const P = [V3(0, 7, -22), ...pyl.map(p => V3(p.position.x + dx, 36, p.position.z))];
    for (let i = 0; i < P.length - 1; i++) for (let k = 0; k <= 20; k++) { const u = k / 20; const p = P[i].clone().lerp(P[i + 1], u); p.y -= Math.sin(u * Math.PI) * 4; pts.push(p); }
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), wireM)); }
  // Kraftwerk mit Kühltürmen, Fenstern und Flugwarnlichtern
  const plant = new THREE.Group(); plant.position.set(-60, 0, -380); scene.add(plant);
  const winT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); const r = rng(3); for (let y = 8; y < h; y += 20) for (let x = 6; x < w; x += 16) if (r() < 0.55) { g.fillStyle = r() < 0.8 ? '#ffd79a' : '#cfe0ff'; g.fillRect(x, y, 9, 9); } });
  const hall = new THREE.MeshStandardMaterial({color: '#3a3c40', emissive: '#ffffff', emissiveMap: winT, emissiveIntensity: 1.3});
  mesh(new THREE.BoxGeometry(110, 45, 50), hall, 0, 22.5, 0, plant);
  const towerGeo = new THREE.CylinderGeometry(22, 32, 110, 32, 1, true); const tgm = mat('#6b6c6e', {roughness: 0.9, side: THREE.DoubleSide});
  for (const x of [-120, -60]) mesh(towerGeo, tgm, x, 55, -30, plant);
  mesh(new THREE.CylinderGeometry(3, 4.5, 170, 16), mat('#7a7b7d'), 60, 85, -10, plant);
  const aviation = []; for (const [x, y, z] of [[60, 171, -10], [-120, 111, -30], [-60, 111, -30], [60, 120, -10]]) aviation.push(mesh(new THREE.SphereGeometry(1.4, 8, 6), new THREE.MeshBasicMaterial({color: '#ff2a1a', fog: false}), x, y, z, plant));
  const steam = particles(10, 'smoke');
  const sparks = sparkSystem(1400, 0.14); sparks.material.size = 0.18; scene.add(sparks);
  const arcLight = new THREE.PointLight('#a8c8ff', 0, 90, 1.2); scene.add(arcLight);
  const arcFlash = new THREE.Mesh(new THREE.SphereGeometry(0.6, 12, 8), new THREE.MeshBasicMaterial({color: '#e6f0ff', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})); scene.add(arcFlash);
  const glowTex = canvasTex(128, 128, (g, w) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(220,235,255,1)'); gr.addColorStop(0.3, 'rgba(140,180,255,0.5)'); gr.addColorStop(1, 'rgba(100,150,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const arcGlow = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})); arcGlow.scale.setScalar(14); scene.add(arcGlow);
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.1, 2000);

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0; renderer.toneMappingExposure = 1.0;
    const on = t < OFF ? 1 : 0;
    floods.forEach(f => { f.l.intensity = on ? 110 * (1 - 0.15 * smooth(1, OFF, t) * (Math.sin(T * 30) > 0)) : 0; f.lamp.material.emissiveIntensity = on ? 3 : 0; });
    // Das Kraftwerk geht vom Netz: Fenster gehen zeilenweise aus
    hall.emissiveIntensity = 1.3 * (t < OFF - 0.6 ? 1 : (t < OFF + 0.6 ? (Math.sin(T * 40) > 0 ? 0.6 : 0.1) : 0));
    aviation.forEach((a, i) => { a.visible = Math.sin(T * 2.5 + i) > 0; }); // Flugwarnlichter laufen auf Batterie weiter
    breakers.forEach((b, i) => { const ti = 1.2 + (i % 7) * 0.45 + Math.floor(i / 7) * 0.2; b.rotation.z = t > ti ? -0.9 : 0; });
    // Lichtbögen
    let arcK = 0, ap = ARCS[0][1];
    const em = [];
    ARCS.forEach(([ta, p]) => { const a = t - ta; if (a > 0 && a < 0.35) { const k = Math.exp(-a * 9) * (0.6 + 0.4 * Math.sin(a * 140)); if (k > arcK) { arcK = k; ap = p; } } if (a > 0) em.push({pos: p, dir: V3(0, 0.4, 0.3), t0: ta, t1: ta + 0.18}); });
    updateSparks(sparks, em.length ? em : [{pos: V3(0, -50, 0), dir: V3(0, 1, 0), t0: -9, t1: -8}], t);
    arcLight.position.copy(ap); arcLight.intensity = 2500 * arcK; arcFlash.position.copy(ap); arcFlash.material.opacity = arcK; arcFlash.scale.setScalar(0.5 + arcK * 1.5);
    arcGlow.position.copy(ap); arcGlow.material.opacity = arcK; arcGlow.scale.setScalar(8 + arcK * 16);
    if (false) updateParticles(steam, [{type: 'smoke', pos: V3(-180, 112, -410), r: 34, t0: -20, size: 55, rise: 9, alpha: 0.22, col: [0.3, 0.32, 0.36], share: 1}, {type: 'smoke', pos: V3(-120, 112, -410), r: 34, t0: -20, size: 55, rise: 9, alpha: 0.22, col: [0.3, 0.32, 0.36], share: 1}], T, V3(3, 0, 0));
    const u = smooth(0, 6.5, t), sh = arcK * 0.15;
    camera.position.set(lerp(1.5, 0, u) + noise1(T * 9, 1) * sh, lerp(2.0, 2.6, u) + noise1(T * 9, 4) * sh, lerp(20, 14, u)); camera.lookAt(lerp(-10, -14, u), lerp(14, 18, u), -200);
    camera.updateProjectionMatrix();
  }};
}
