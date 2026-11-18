// Küche: Dichtungen in Wasserleitungen und an der Waschmaschine verschwinden
import {THREE, envMap, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, tileTex} from './lib.js';

const dropTex = canvasTex(64, 64, (g, w) => { const r = g.createRadialGradient(28, 28, 2, 32, 32, 30); r.addColorStop(0, 'rgba(255,255,255,0.95)'); r.addColorStop(0.4, 'rgba(190,220,245,0.7)'); r.addColorStop(1, 'rgba(150,200,240,0)'); g.fillStyle = r; g.fillRect(0, 0, w, w); });
function waterSystem(n, size) {
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  const p = new THREE.Points(geo, new THREE.PointsMaterial({size, map: dropTex, transparent: true, depthWrite: false, color: '#dbeeff'}));
  p.frustumCulled = false; p.userData.n = n; return p;
}
// Strahl aus einer Leitung: emitters [{pos, dir, speed, spread, t0}]
function updateWater(sys, emitters, t, floorY) {
  const P = sys.geometry.attributes.position.array, n = sys.userData.n, per = Math.floor(n / emitters.length); let i = 0;
  emitters.forEach((e, ei) => {
    const r = rng(ei * 17 + 3);
    for (let k = 0; k < per; k++, i++) {
      const life = 0.5 + r() * 0.5, off = r() * life; const a = ((t + off) % life);
      const born = t - a; const ok = born >= e.t0;
      const sp = e.speed * (0.8 + r() * 0.4);
      const dx = e.dir.x + (r() - 0.5) * e.spread, dy = e.dir.y + (r() - 0.5) * e.spread, dz = e.dir.z + (r() - 0.5) * e.spread;
      let y = e.pos.y + dy * sp * a - 4.9 * a * a; const x = e.pos.x + dx * sp * a, z = e.pos.z + dz * sp * a;
      if (y < floorY) y = floorY + 0.005;
      P[i * 3] = ok ? x : 0; P[i * 3 + 1] = ok ? y : -99; P[i * 3 + 2] = ok ? z : 0;
    }
  });
  for (; i < n; i++) P[i * 3 + 1] = -99;
  sys.geometry.attributes.position.needsUpdate = true;
}

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.environment = envMap(renderer); scene.environmentIntensity = 0.35;
  scene.background = new THREE.Color('#6d6a64');
  scene.add(new THREE.HemisphereLight('#fff4e2', '#6b5a48', 0.55));
  const lamp = new THREE.PointLight('#ffd7a3', 9, 8); lamp.position.set(0.5, 2.6, 1.2); lamp.castShadow = true; scene.add(lamp);
  const win = new THREE.DirectionalLight('#cfdcef', 1.0); win.position.set(-3, 3, 2); scene.add(win);
  // Raum
  const ft = tileTex('#8c8274', '#7d7366'); ft.repeat.set(4, 4);
  const floor = mesh(new THREE.PlaneGeometry(6, 6), new THREE.MeshStandardMaterial({map: ft, roughness: 0.4}), 0, 0, 0, scene); floor.rotation.x = -Math.PI / 2;
  const wt = tileTex('#9fb3ad', '#93a8a1'); wt.repeat.set(6, 3);
  mesh(new THREE.PlaneGeometry(6, 3), new THREE.MeshStandardMaterial({map: wt, roughness: 0.3}), 0, 1.5, -0.62, scene);
  const sideWall = mesh(new THREE.PlaneGeometry(6, 3), mat('#b9ad98'), -1.6, 1.5, 1, scene); sideWall.rotation.y = Math.PI / 2;
  // Fenster mit Regen
  const winTex = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#7f8c9b'; g.fillRect(0, 0, w, h); for (let i = 0; i < 300; i++) { g.fillStyle = 'rgba(230,240,255,0.5)'; g.fillRect(Math.random() * w, Math.random() * h, 2, 6 + Math.random() * 8); } });
  mesh(new THREE.PlaneGeometry(0.9, 1.0), new THREE.MeshBasicMaterial({map: winTex}), -1.59, 1.75, 0.2, scene).rotation.y = Math.PI / 2;
  // Unterschrank (Türen offen) mit Spüle
  const wood = mat('#a9825a', {roughness: 0.6});
  mesh(new THREE.BoxGeometry(1.6, 0.04, 0.62), mat('#5a5048', {roughness: 0.3}), 0, 0.9, -0.3, scene); // Arbeitsplatte
  mesh(new THREE.BoxGeometry(1.6, 0.86, 0.04), wood, 0, 0.45, -0.6, scene);
  for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(0.04, 0.86, 0.6), wood, s * 0.78, 0.45, -0.3, scene);
  for (const s of [-1, 1]) { const d = mesh(new THREE.BoxGeometry(0.02, 0.8, 0.38), wood, s * 0.97, 0.45, 0.12, scene); d.rotation.y = s * 0.5; }
  const bowl = mesh(new THREE.BoxGeometry(0.6, 0.2, 0.4), mat('#c7cbd0', {metalness: 0.9, roughness: 0.2}), -0.1, 0.8, -0.32, scene);
  // Rohre: Siphon und Zuleitungen mit Gummidichtungen
  const chrome = mat('#d6d9de', {metalness: 1, roughness: 0.15});
  const rubber = mat('#151515', {roughness: 0.95});
  const pipes = new THREE.Group(); scene.add(pipes);
  mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.3, 16), chrome, -0.1, 0.55, -0.32, pipes);
  const trap = mesh(new THREE.TorusGeometry(0.07, 0.025, 12, 24, Math.PI), chrome, -0.03, 0.4, -0.32, pipes); trap.rotation.z = Math.PI;
  mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.12, 16), chrome, 0.04, 0.46, -0.32, pipes);
  const outP = mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.36, 16), chrome, 0.2, 0.52, -0.42, pipes); outP.rotation.z = Math.PI / 2; outP.position.set(0.22, 0.52, -0.32);
  const hot = mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.5, 10), mat('#c8763a', {metalness: 0.9, roughness: 0.3}), 0.45, 0.45, -0.55, pipes);
  const cold = mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.5, 10), chrome, 0.55, 0.45, -0.55, pipes);
  for (const [x, c] of [[0.45, '#c33'], [0.55, '#36c']]) { mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.05, 12), chrome, x, 0.32, -0.55, pipes); mesh(new THREE.BoxGeometry(0.06, 0.012, 0.012), mat(c), x, 0.35, -0.53, pipes); }
  const seals = [];
  for (const [x, y, z, rot] of [[-0.1, 0.4 + 0.0, -0.32, 0], [0.04, 0.52, -0.32, 0], [0.06, 0.52, -0.32, 1], [0.45, 0.28, -0.55, 0], [0.55, 0.28, -0.55, 0]]) {
    const s = mesh(new THREE.TorusGeometry(0.03, 0.009, 8, 20), rubber, x, y, z, pipes); s.rotation.x = Math.PI / 2; if (rot) s.rotation.set(0, Math.PI / 2, 0); seals.push(s);
  }
  // Waschmaschine rechts
  const wm = new THREE.Group(); wm.position.set(1.25, 0, -0.25); scene.add(wm);
  mesh(new RoundedBoxGeometry(0.6, 0.85, 0.6, 3, 0.03), mat('#f6f6f4', {roughness: 0.35}), 0, 0.425, 0, wm);
  mesh(new THREE.BoxGeometry(0.56, 0.1, 0.01), mat('#dcdcdc'), 0, 0.77, 0.3, wm);
  mesh(new THREE.CircleGeometry(0.03, 16), mat('#333'), 0.18, 0.77, 0.306, wm);
  const ringM = mat('#c9ccd1', {metalness: 0.8, roughness: 0.25});
  const ring = mesh(new THREE.TorusGeometry(0.2, 0.025, 10, 32), ringM, 0, 0.4, 0.33, wm);
  const gasket = mesh(new THREE.TorusGeometry(0.175, 0.022, 10, 32), mat('#585c61', {roughness: 0.9}), 0, 0.4, 0.315, wm);
  const door = mesh(new THREE.CircleGeometry(0.18, 32), new THREE.MeshPhysicalMaterial({color: '#7fa4c8', roughness: 0.05, transparent: true, opacity: 0.55, metalness: 0.1}), 0, 0.4, 0.34, wm);
  const drum = mesh(new THREE.CircleGeometry(0.17, 32), mat('#3c6a92', {roughness: 0.3}), 0, 0.4, 0.31, wm);
  // Wasser auf dem Boden
  const pool = mesh(new THREE.CircleGeometry(1, 48), new THREE.MeshStandardMaterial({color: '#9ec4e0', roughness: 0.03, metalness: 0.3, transparent: true, opacity: 0.55}), 0.5, 0.003, 0.2, scene);
  pool.rotation.x = -Math.PI / 2; pool.receiveShadow = false;
  const water = waterSystem(5000, 0.022); scene.add(water);
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.01, 50);

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, tv = 0.5;
    seals.forEach((s, i) => s.visible = t < tv + i * 0.02);
    const gone = t >= tv + 2.6; gasket.visible = !gone;
    const em = [
      {pos: new THREE.Vector3(-0.1, 0.4, -0.29), dir: new THREE.Vector3(0.2, 0.3, 1), speed: 2.2, spread: 0.6, t0: tv},
      {pos: new THREE.Vector3(0.06, 0.52, -0.29), dir: new THREE.Vector3(0.4, 0.6, 1), speed: 3, spread: 0.4, t0: tv},
      {pos: new THREE.Vector3(0.45, 0.28, -0.52), dir: new THREE.Vector3(-0.3, 0.9, 1), speed: 4.5, spread: 0.25, t0: tv},
      {pos: new THREE.Vector3(0.55, 0.28, -0.52), dir: new THREE.Vector3(0.4, 1, 1), speed: 4.2, spread: 0.25, t0: tv},
      {pos: new THREE.Vector3(1.25, 0.24, 0.1), dir: new THREE.Vector3(0, -0.2, 1), speed: 2.2, spread: 0.9, t0: tv + 2.6},
      {pos: new THREE.Vector3(1.25, 0.5, 0.1), dir: new THREE.Vector3(0, 0.2, 1), speed: 1.6, spread: 1.4, t0: tv + 2.6},
    ];
    updateWater(water, em, t, 0.005 + smooth(tv, 7, t) * 0.02);
    drum.position.z = 0.31; door.rotation.y = gone ? smooth(tv + 2.6, tv + 3.4, t) * -0.25 : 0;
    const flood = smooth(tv, 6.5, t); pool.scale.setScalar(0.1 + flood * 2.4); pool.position.y = 0.003 + flood * 0.02; pool.visible = t > tv;
    if (t < 3.0) { // Nahaufnahme Rohre
      camera.position.set(0.35 + t * 0.03, 0.62, 0.55); camera.lookAt(0.2, 0.42, -0.42); camera.fov = 45;
    } else {
      const k = smooth(3.0, 7, t);
      camera.position.set(lerp(1.0, 0.7, k), lerp(1.0, 1.3, k), lerp(1.7, 2.3, k)); camera.lookAt(0.75, 0.38, -0.2); camera.fov = 50;
    }
    camera.position.x += noise1(T, 3) * 0.006; camera.position.y += noise1(T, 6) * 0.006;
    camera.updateProjectionMatrix(); void bowl; void ring; void hot; void cold;
  }};
}
