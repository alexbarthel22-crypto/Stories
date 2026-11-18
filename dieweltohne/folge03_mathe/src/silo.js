// Raketensilo auf einer Waldlichtung: der Deckel gleitet auf, Dampf schießt heraus, die Rakete steigt auf.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex} from './lib.js';
import {skyMaterial} from './beach.js';
import {particles, updateParticles, flicker} from './fx.js';
import {IGNITION, LIFTOFF} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const SUN_DIR = V3(0.75, 0.3, 0.45).normalize();
const L = 22;              // Raketenlänge
const LIFT2 = 80.5;        // zweite Rakete im Hintergrund
const P2 = V3(-600, 0, -620);

// Höhe der Raketenunterkante über Grund (negativ: noch im Schacht)
function rise(T, t0) { const t = T - t0; if (t <= 0) return -L - 0.5; return -L - 0.5 + 0.5 * (4 + 1.4 * t) * t * t; }

function missile(scale = 1) {
  const g = new THREE.Group();
  const white = mat('#e9e9e4', {roughness: 0.45, metalness: 0.1}), dark = mat('#2b2d30', {roughness: 0.6}), grey = mat('#a7aaae', {roughness: 0.5, metalness: 0.3});
  mesh(new THREE.CylinderGeometry(1.0, 1.0, L * 0.72, 32), white, 0, L * 0.36, 0, g);
  for (const y of [L * 0.3, L * 0.58]) mesh(new THREE.CylinderGeometry(1.02, 1.02, 0.35, 32), dark, 0, y, 0, g);
  mesh(new THREE.CylinderGeometry(0.85, 1.0, L * 0.12, 32), grey, 0, L * 0.78, 0, g);
  mesh(new THREE.ConeGeometry(0.85, L * 0.16, 32), white, 0, L * 0.92, 0, g);
  mesh(new THREE.CylinderGeometry(0.75, 0.95, 0.9, 24), dark, 0, -0.3, 0, g); // Düse
  const tag = canvasTex(256, 64, (c, w, h) => { c.fillStyle = '#e9e9e4'; c.fillRect(0, 0, w, h); c.fillStyle = '#1a1a1a'; c.font = '600 34px Plex'; c.fillText('Б-17', 70, 44); });
  const tg = mesh(new THREE.PlaneGeometry(1.2, 0.3), new THREE.MeshStandardMaterial({map: tag}), 0, L * 0.5, 1.01, g);
  g.scale.setScalar(scale); return g;
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(1500, 48, 24), skyMaterial(SUN_DIR)); sky.renderOrder = -10; scene.add(sky);
  sky.material.uniforms.day.value = 1; sky.material.uniforms.stars.value = 0;
  scene.fog = new THREE.Fog('#8a96a3', 150, 1400);
  const hemi = new THREE.HemisphereLight('#aab6c4', '#3a3a2c', 0.9); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#ffe2bd', 1.6); sun.position.copy(SUN_DIR).multiplyScalar(200); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -60, right: 60, top: 60, bottom: -60, near: 1, far: 500}); scene.add(sun, sun.target);
  // Boden, Lichtung, Wald
  const grassT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#4a5a33'; g.fillRect(0, 0, w, h); const r = rng(3); for (let i = 0; i < 6000; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '30,40,20' : '120,130,80'},${r() * 0.25})`; g.fillRect(r() * w, r() * h, 2 + r() * 4, 2 + r() * 4); } });
  grassT.wrapS = grassT.wrapT = THREE.RepeatWrapping; grassT.repeat.set(120, 120);
  const ground = mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.MeshStandardMaterial({map: grassT, roughness: 1}), 0, 0, 0, scene); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true;
  const conc = mat('#8f8d87', {roughness: 0.9}), concD = mat('#6b6964', {roughness: 0.9});
  mesh(new THREE.BoxGeometry(34, 0.4, 30), conc, 0, 0.2, 0, scene).receiveShadow = true;
  // Schacht: Ring und dunkles Loch
  const ring = mesh(new THREE.CylinderGeometry(4.2, 4.4, 1.2, 40, 1, true), concD, 0, 0.6, 0, scene); ring.material.side = THREE.DoubleSide;
  mesh(new THREE.RingGeometry(3.2, 4.3, 40), concD, 0, 1.21, 0, scene).rotation.x = -Math.PI / 2;
  const hole = mesh(new THREE.CircleGeometry(3.25, 40), new THREE.MeshBasicMaterial({color: '#050505'}), 0, 1.0, 0, scene); hole.rotation.x = -Math.PI / 2;
  // Schienen und Deckel
  for (const z of [-4, 4]) mesh(new THREE.BoxGeometry(26, 0.3, 0.5), mat('#55575a', {metalness: 0.7, roughness: 0.4}), 9, 0.55, z, scene);
  const lid = new THREE.Group(); scene.add(lid);
  const lm = mesh(new THREE.BoxGeometry(10, 1.6, 10), mat('#7e7b74', {roughness: 0.8}), 0, 1.6, 0, lid); lm.castShadow = true; lm.receiveShadow = true;
  mesh(new THREE.BoxGeometry(10.2, 0.25, 10.2), mat('#5b5955'), 0, 2.45, 0, lid);
  for (const z of [-3.5, 0, 3.5]) mesh(new THREE.BoxGeometry(9.6, 0.15, 0.4), mat('#c9a227'), 0, 2.6, z, lid);
  // Zaun, Masten, Wachhaus, Antennen
  const fenceM = mat('#6f7276', {metalness: 0.6}), r = rng(41);
  for (let a = 0; a < 360; a += 4) { const x = Math.cos(a * Math.PI / 180) * 26, z = Math.sin(a * Math.PI / 180) * 24; mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.6, 6), fenceM, x, 1.3, z, scene); }
  const fenceNet = mesh(new THREE.CylinderGeometry(26, 26, 2.4, 90, 1, true), new THREE.MeshStandardMaterial({color: '#7a7d80', transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false}), 0, 1.3, 0, scene); fenceNet.scale.z = 24 / 26;
  mesh(new THREE.BoxGeometry(4, 3, 3), mat('#7c8270'), -14, 1.5, 12, scene);
  for (const [x, z] of [[-12, -10], [12, 11]]) { mesh(new THREE.CylinderGeometry(0.08, 0.1, 9, 8), fenceM, x, 4.5, z, scene); mesh(new THREE.BoxGeometry(0.6, 0.3, 0.3), mat('#222'), x, 9, z, scene); }
  // Wald (instanziert): Nadelbäume um die Lichtung
  const treeG = new THREE.ConeGeometry(1, 1, 7); treeG.translate(0, 0.5, 0);
  const trees = new THREE.InstancedMesh(treeG, mat('#22331f', {roughness: 0.95, flatShading: true}), 5000);
  const trunks = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.25, 0.3, 1, 5), mat('#3a2a1d'), 5000);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(); let ti = 0;
  while (ti < 5000) { const x = (r() - 0.5) * 1600, z = (r() - 0.5) * 1600 - 200; const d = Math.hypot(x / 1.1, z);
    if (d < 46 || Math.hypot(x - 50, z - 38) < 30) continue; // Lichtung und Kamerastandort frei
    const h = 12 + r() * 14; m4.compose(V3(x, 1.5, z), q, V3(h * 0.2, h, h * 0.2)); trees.setMatrixAt(ti, m4); m4.compose(V3(x, 1, z), q, V3(1, 2, 1)); trunks.setMatrixAt(ti, m4); ti++; }
  trees.castShadow = true; scene.add(trees, trunks);
  // Raketen
  const m1 = missile(); scene.add(m1);
  const m2 = missile(1.2); m2.position.copy(P2); scene.add(m2);
  // Feuerstrahl: heller Kern als Kegel, Flammen- und Rauchpartikel
  const flameTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,240,190,0.95)'); gr.addColorStop(0.6, 'rgba(255,150,50,0.6)'); gr.addColorStop(1, 'rgba(255,80,20,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const plume = (len, rad) => { const geo = new THREE.ConeGeometry(rad, len, 24, 1, true); geo.translate(0, -len / 2, 0);
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({map: flameTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, toneMapped: false})); return m; };
  const core1 = plume(26, 1.5), core2 = plume(30, 1.9); scene.add(core1, core2);
  const glowTex = canvasTex(128, 128, (g, w) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,250,230,1)'); gr.addColorStop(0.3, 'rgba(255,200,120,0.6)'); gr.addColorStop(1, 'rgba(255,120,40,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const glow1 = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false})); scene.add(glow1);
  const glow2 = glow1.clone(); glow2.material = glow1.material.clone(); scene.add(glow2);
  const fireL = new THREE.PointLight('#ffb060', 0, 300, 2); scene.add(fireL);
  const fire = particles(1600, 'flame'); scene.add(fire);
  const smoke = particles(2600, 'smoke'); scene.add(smoke);
  // Rauchsäule als weicher, aufgeblähter Schlauch (wächst mit der Rakete)
  const puffT = canvasTex(256, 512, (g, w, h) => { g.clearRect(0, 0, w, h); const r2 = rng(19);
    g.fillStyle = 'rgba(190,190,186,0.55)'; g.fillRect(0, 0, w, h); for (let i = 0; i < 420; i++) { const x = r2() * w, y = r2() * h, rad = 16 + r2() * 40; const v = 140 + r2() * 90;
      const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, `rgba(${v},${v},${v - 4},0.8)`); gr.addColorStop(1, `rgba(${v},${v},${v - 4},0)`); g.fillStyle = gr; g.fillRect(0, 0, w, h); } });
  puffT.wrapS = puffT.wrapT = THREE.RepeatWrapping;
  const colGeo = new THREE.CylinderGeometry(1, 1, 1, 28, 24, true); colGeo.translate(0, 0.5, 0);
  { const P = colGeo.attributes.position; for (let i = 0; i < P.count; i++) { const y = P.getY(i); const k = 1 + 1.6 * Math.pow(1 - y, 2.5); P.setX(i, P.getX(i) * k); P.setZ(i, P.getZ(i) * k); } colGeo.computeVertexNormals(); }
  const colM = new THREE.MeshStandardMaterial({color: '#d6d5d0', map: puffT, alphaMap: puffT, transparent: true, depthWrite: false, side: THREE.DoubleSide, roughness: 1});
  const column = new THREE.Mesh(colGeo, colM); scene.add(column);
  const column2 = new THREE.Mesh(colGeo, colM.clone()); scene.add(column2);
  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.5, 4000);
  const CAM = V3(50, 2.0, 38);

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.0;
    lid.position.x = 12 * smooth(76.0, 77.0, T) + noise1(T * 30, 4) * 0.03 * (T > 76 && T < 77);
    // Rakete 1
    const y1 = rise(T, LIFTOFF); m1.position.set(0, y1 + 0.3, 0); m1.visible = y1 > -L - 0.4 && T > 76;
    const ign = T >= IGNITION, out = y1 > 0.5;
    const nozzle = V3(0, Math.max(y1, 0.8), 0);
    core1.visible = ign && T > LIFTOFF - 0.4; core1.position.copy(nozzle); core1.scale.set(1, 0.6 + 0.4 * flicker(T, 1) + smooth(LIFTOFF, LIFTOFF + 2, T) * 0.6, 1);
    glow1.visible = ign; glow1.position.copy(nozzle).add(V3(0, -2, 0)); glow1.scale.setScalar((out ? 24 : 8 + 8 * smooth(IGNITION, LIFTOFF, T)) * (0.85 + 0.15 * flicker(T, 2)));
    glow1.material.opacity = ign ? 0.9 : 0;
    fireL.position.copy(nozzle).add(V3(4, 2, 4)); fireL.intensity = ign ? (out ? 3500 : 900 + 2000 * smooth(IGNITION, LIFTOFF, T)) * flicker(T, 3) : 0;
    // Rakete 2 im Hintergrund
    const y2 = rise(T, LIFT2) * 1.2; m2.position.set(P2.x, y2 + 0.3, P2.z); m2.visible = y2 > 0;
    const n2 = V3(P2.x, Math.max(y2, 1), P2.z);
    core2.visible = T > LIFT2 - 0.3; core2.position.copy(n2); glow2.visible = core2.visible; glow2.position.copy(n2); glow2.scale.setScalar(45 * flicker(T, 5)); glow2.material.opacity = 0.9;
    // Rauchsäulen
    column.visible = out; if (out) { const h = Math.max(1, y1 - 1); column.scale.set(1.6 + h * 0.006, h, 1.6 + h * 0.006); column.position.set(0, 0, 0); puffT.offset.y = -T * 0.05; puffT.repeat.set(2, 1 + h / 60); }
    column2.visible = y2 > 1; if (y2 > 1) { const h = y2 - 1; column2.scale.set(2.5 + h * 0.008, h, 2.5 + h * 0.008); column2.position.set(P2.x, 0, P2.z); }
    // Flammen und Rauch
    const fl = [], sm = [];
    if (ign) {
      fl.push({type: 'flame', pos: out ? nozzle.clone().add(V3(0, -3, 0)) : V3(0, 1.5, 0), r: out ? 1.4 : 3.0, t0: IGNITION, size: out ? 5 : 4, rise: out ? -14 : 5, power: 1, share: 2});
      sm.push({type: 'smoke', pos: V3(0, 2, 0), r: 3.5, t0: IGNITION, size: 9, rise: 4.5, col: [0.72, 0.72, 0.71], alpha: 0.75, share: 3});           // Dampf aus dem Schacht
      sm.push({type: 'smoke', pos: V3(0, 1.5, 0), r: 22, t0: LIFTOFF - 0.3, size: 16, rise: 1.2, col: [0.62, 0.61, 0.59], alpha: 0.7, share: 3});       // Bodenwolke
      // Rauchsäule entlang der Bahn
      for (const h of [20, 45, 75, 110, 150, 200, 260, 330, 410, 500, 600, 720, 850]) { let tp = LIFTOFF; while (rise(tp, LIFTOFF) < h && tp < LIFTOFF + 30) tp += 0.05;
        sm.push({type: 'smoke', pos: V3(0, h, 0), r: 2.5 + h * 0.02, t0: tp, size: 11 + h * 0.05, rise: -1.5, col: [0.66, 0.66, 0.66], alpha: 0.6, share: 1.5}); }
    }
    if (T > LIFT2 - 0.3) { for (const h of [5, 40, 100, 200]) { let tp = LIFT2; while (rise(tp, LIFT2) * 1.2 < h && tp < LIFT2 + 30) tp += 0.05;
      sm.push({type: 'smoke', pos: V3(P2.x, h, P2.z), r: 6 + h * 0.03, t0: tp, size: 22 + h * 0.08, rise: 1, col: [0.62, 0.62, 0.63], alpha: 0.6, share: 1}); } }
    updateParticles(fire, fl.length ? fl : [{type: 'flame', pos: V3(0, -99, 0), r: 1, t0: 999}], T, V3(0, 0, 0));
    updateParticles(smoke, sm.length ? sm : [{type: 'smoke', pos: V3(0, -99, 0), r: 1, t0: 999}], T, V3(2.5, 0, 0.8));
    // Kamera: am Waldrand, folgt der Rakete nach oben, starkes Wackeln bei Zündung und Start
    const shk = (T > IGNITION ? 0.25 * Math.exp(-(T - IGNITION) * 1.5) : 0) + (T > LIFTOFF ? 0.5 * Math.exp(-(T - LIFTOFF) * 0.9) + 0.06 : 0) + (T > 76 && T < 77 ? 0.03 : 0);
    const look = Math.max(8, Math.min(y1 + L * 0.6, 900));
    camera.position.copy(CAM).add(V3(noise1(T * 17, 1) * shk, noise1(T * 19, 2) * shk, noise1(T * 15, 3) * shk));
    camera.position.addScaledVector(V3(-0.8, 0, -0.6), smooth(76, 84, T) * 6);
    camera.lookAt(0, look * 0.8 + 6, 0);
    camera.fov = lerp(40, 46, smooth(LIFTOFF, LIFTOFF + 3, T)); camera.updateProjectionMatrix();
  }};
}
