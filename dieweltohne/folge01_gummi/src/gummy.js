// Gummibärchen auf einer Hand: sie bleiben, weil sie aus Gelatine sind. Daneben ein Radiergummi, der verschwunden ist.
import {THREE, envMap, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex} from './lib.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

function bearGeometry() {
  const parts = [];
  const add = (g, x, y, z, sx = 1, sy = 1, sz = 1) => { g.scale(sx, sy, sz); g.translate(x, y, z); parts.push(g); };
  add(new THREE.SphereGeometry(0.5, 20, 16), 0, 0, 0, 1, 1.15, 0.75);           // Bauch
  add(new THREE.SphereGeometry(0.38, 20, 16), 0, 0.78, 0, 1.05, 0.95, 0.8);      // Kopf
  add(new THREE.SphereGeometry(0.13, 12, 10), -0.26, 1.08, 0, 1, 1, 0.7);         // Ohren
  add(new THREE.SphereGeometry(0.13, 12, 10), 0.26, 1.08, 0, 1, 1, 0.7);
  add(new THREE.SphereGeometry(0.16, 12, 10), 0, 0.68, 0.27, 1.1, 0.8, 0.8);      // Schnauze
  add(new THREE.SphereGeometry(0.17, 12, 10), -0.42, 0.25, 0.08, 1, 1.3, 0.8);    // Arme
  add(new THREE.SphereGeometry(0.17, 12, 10), 0.42, 0.25, 0.08, 1, 1.3, 0.8);
  add(new THREE.SphereGeometry(0.21, 12, 10), -0.25, -0.55, 0.1, 1, 1, 0.85);     // Beine
  add(new THREE.SphereGeometry(0.21, 12, 10), 0.25, -0.55, 0.1, 1, 1, 0.85);
  const g = mergeGeometries(parts.map(p => p.toNonIndexed())); g.computeVertexNormals(); return g;
}

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.environment = envMap(renderer); scene.environmentIntensity = 1.0;
  const r = rng(6);
  // warmer, unscharfer Hintergrund (Kinderzimmer am Fenster)
  const bg = canvasTex(512, 1024, (g, w, h) => {
    const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, '#5d6f86'); grd.addColorStop(0.5, '#b39b86'); grd.addColorStop(1, '#6a5446'); g.fillStyle = grd; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 40; i++) { const x = r() * w, y = r() * h * 0.6, rad = 15 + r() * 45; const rg = g.createRadialGradient(x, y, 0, x, y, rad); rg.addColorStop(0, 'rgba(255,230,190,0.45)'); rg.addColorStop(1, 'rgba(255,230,190,0)'); g.fillStyle = rg; g.fillRect(x - rad, y - rad, rad * 2, rad * 2); }
  });
  mesh(new THREE.PlaneGeometry(6, 12), new THREE.MeshBasicMaterial({map: bg}), 0, 0, -3, scene);
  scene.add(new THREE.HemisphereLight('#fff1e0', '#4a3a30', 1.2));
  const key = new THREE.DirectionalLight('#ffffff', 2.4); key.position.set(-1, 2, 1.5); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); scene.add(key);
  const rim = new THREE.DirectionalLight('#ffd9a8', 2.0); rim.position.set(1.5, 1, -2); scene.add(rim);
  // Hand (offene Handfläche)
  const skin = mat('#e9b893', {roughness: 0.55});
  const hand = new THREE.Group(); scene.add(hand);
  mesh(new RoundedBoxGeometry(0.9, 0.18, 0.95, 4, 0.08), skin, 0, -0.1, 0, hand);
  for (let i = 0; i < 4; i++) { const f = mesh(new THREE.CapsuleGeometry(0.09, 0.45, 6, 12), skin, -0.33 + i * 0.22, -0.06, -0.72 - (i === 1 || i === 2 ? 0.05 : 0), hand); f.rotation.x = Math.PI / 2 - 0.25; }
  const th = mesh(new THREE.CapsuleGeometry(0.1, 0.38, 6, 12), skin, 0.55, -0.02, 0.1, hand); th.rotation.set(Math.PI / 2, 0, -0.9);
  mesh(new THREE.CylinderGeometry(0.36, 0.4, 1.6, 20), mat('#3e5f8a', {roughness: 0.9}), 0, -0.15, 1.3, hand).rotation.x = Math.PI / 2;
  // Gummibärchen
  const geo = bearGeometry();
  const cols = ['#e3202f', '#f6c21b', '#3fae3b', '#ff8a1c', '#f4f1e8', '#d81f2a'];
  const bears = cols.map((c, i) => {
    const m = new THREE.MeshPhysicalMaterial({color: c, roughness: 0.18, transmission: 0.55, thickness: 0.6, ior: 1.45, clearcoat: 0.8, clearcoatRoughness: 0.15, attenuationColor: c, attenuationDistance: 0.5});
    const b = mesh(geo, m, 0, 0, 0, hand); b.scale.setScalar(0.17);
    b.position.set(-0.28 + (i % 3) * 0.26 + r() * 0.05, 0.08 + (i > 2 ? 0.05 : 0), -0.2 + Math.floor(i / 3) * 0.3);
    b.rotation.set(-Math.PI / 2 + 0.2, (r() - 0.5) * 0.8, (r() - 0.5) * 1.2); return b;
  });
  // Radiergummi daneben auf dem Fensterbrett: verschwindet
  const sill = mesh(new THREE.BoxGeometry(3, 0.1, 1), mat('#efe9df'), 0.2, -0.7, -0.9, scene);
  const eraser = mesh(new RoundedBoxGeometry(0.35, 0.12, 0.2, 2, 0.03), mat('#f08aa0', {roughness: 0.8}), 1.0, -0.59, -0.7, scene);
  const pencil = mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.9, 6), mat('#f3c31b'), 0.75, -0.62, -0.45, scene); pencil.rotation.z = Math.PI / 2; pencil.rotation.y = 0.4;
  const camera = new THREE.PerspectiveCamera(38, 1080 / 1920, 0.01, 50);

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    eraser.visible = false; // Gummi ist zu dieser Zeit weg
    hand.position.set(noise1(T, 1) * 0.01, noise1(T, 2) * 0.01, 0); hand.rotation.set(0.05, -0.15, 0.02);
    bears.forEach((b, i) => { b.position.y = 0.09 + Math.sin(T * 3 + i) * 0.003; });
    const k = smooth(0, 6, t);
    camera.position.set(lerp(0.55, 0.35, k), lerp(0.95, 0.8, k), lerp(1.05, 0.85, k)); camera.lookAt(0.0, 0.05, -0.08); camera.updateProjectionMatrix();
    void sill; void pencil; void clamp;
  }};
}
