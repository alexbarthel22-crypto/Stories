// Die Stadt bei Nacht von oben: Viertel für Viertel geht das Licht aus (Stufe 5) – und um 2:13 Uhr wieder an (Stufe 7).
import * as THREE from 'three';
import {lerp, smooth, clamp, rng, noise1, canvasTex, envMap} from './lib.js';
import {CITY_OUT, POWER_BACK} from './timeline.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#03050b');
  scene.fog = new THREE.FogExp2('#0b0d16', 0.00036);
  const camera = new THREE.PerspectiveCamera(42, 1080 / 1920, 1, 9000);
  // Himmel: dunkles Blau, am Horizont Lichtglocke (verschwindet mit dem Strom)
  const skyC = document.createElement('canvas'); skyC.width = 16; skyC.height = 512; const sg = skyC.getContext('2d');
  const skyT = new THREE.CanvasTexture(skyC); skyT.colorSpace = THREE.SRGBColorSpace;
  const sky = new THREE.Mesh(new THREE.SphereGeometry(8000, 32, 16), new THREE.MeshBasicMaterial({map: skyT, side: THREE.BackSide, fog: false, depthWrite: false})); scene.add(sky);
  const drawSky = glow => { const g = sg.createLinearGradient(0, 0, 0, 512); g.addColorStop(0, '#02030a'); g.addColorStop(0.42, '#060a18'); g.addColorStop(0.5, `rgb(${20 + 70 * glow | 0},${18 + 40 * glow | 0},${30 + 30 * glow | 0})`); g.addColorStop(0.53, '#05070d'); g.addColorStop(1, '#020203'); sg.fillStyle = g; sg.fillRect(0, 0, 16, 512); skyT.needsUpdate = true; };
  // Sterne (erst sichtbar, wenn die Stadt dunkel ist)
  const sp = []; const qs = rng(5); for (let i = 0; i < 2500; i++) { const a = qs() * Math.PI * 2, e = 0.05 + Math.pow(qs(), 0.7) * 1.3; sp.push(Math.cos(a) * Math.cos(e) * 7000, Math.sin(e) * 7000, Math.sin(a) * Math.cos(e) * 7000); }
  const sgeo = new THREE.BufferGeometry(); sgeo.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3));
  const stars = new THREE.Points(sgeo, new THREE.PointsMaterial({color: '#cfd8ff', size: 1.6, sizeAttenuation: false, transparent: true, opacity: 0, fog: false})); scene.add(stars);
  scene.add(new THREE.HemisphereLight('#28324a', '#0a0a0c', 0.25));
  const moon = new THREE.DirectionalLight('#8fa6d6', 0.7); moon.position.set(-1, 2, -1); scene.add(moon);
  // Boden mit Straßenraster (dunkel) und Fluss
  const groundT = canvasTex(2048, 2048, g => { g.fillStyle = '#0c0d10'; g.fillRect(0, 0, 2048, 2048); g.fillStyle = '#16171b'; for (let i = 0; i < 2048; i += 32) { g.fillRect(i, 0, 4, 2048); g.fillRect(0, i, 2048, 4); } g.fillStyle = '#060a12'; g.beginPath(); g.moveTo(0, 1300); for (let x = 0; x <= 2048; x += 32) g.lineTo(x, 1300 + Math.sin(x * 0.003) * 160); for (let x = 2048; x >= 0; x -= 32) g.lineTo(x, 1390 + Math.sin(x * 0.003) * 160); g.fill(); });
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(8000, 8000), new THREE.MeshStandardMaterial({map: groundT, roughness: 0.9})); ground.rotation.x = -Math.PI / 2; scene.add(ground);
  // Fensterfassade (dunkel + Fenster, Emission = beleuchtete Fenster)
  const facade = (seed, warm) => { const q = rng(seed);
    const map = canvasTex(256, 512, g => { g.fillStyle = '#2e3139'; g.fillRect(0, 0, 256, 512); for (let y = 10; y < 512; y += 42) for (let x = 10; x < 256; x += 36) { g.fillStyle = '#0d0e11'; g.fillRect(x, y, 22, 26); } });
    const em = canvasTex(256, 512, g => { g.fillStyle = '#000'; g.fillRect(0, 0, 256, 512); for (let y = 10; y < 512; y += 42) for (let x = 10; x < 256; x += 36) if (q() < 0.42) { const c = q(); g.fillStyle = c < 0.6 ? (warm ? '#ffbe70' : '#ffd59a') : c < 0.85 ? '#bcd2ff' : '#ffe9c8'; g.globalAlpha = 0.45 + q() * 0.55; g.fillRect(x, y, 22, 26); g.globalAlpha = 1; } });
    return {map, em}; };
  const facs = [facade(1, 1), facade(2, 0), facade(3, 1)];
  // 14 Viertel als Ring-Sektoren um ein Umspannwerk; jedes Viertel = eigene InstancedMesh
  const D = []; const q = rng(77); const cell = 64;
  for (let d = 0; d < 14; d++) {
    const f = facs[d % 3]; const mat = new THREE.MeshStandardMaterial({map: f.map, emissive: '#ffffff', emissiveMap: f.em, emissiveIntensity: 1.4, roughness: 0.8});
    const roofM = new THREE.MeshStandardMaterial({color: '#15161a', roughness: 0.9});
    D.push({mat, list: [], lights: [], order: 0, roofM});
  }
  const geo = new THREE.BoxGeometry(1, 1, 1); geo.translate(0, 0.5, 0);
  const sector = (x, z) => { const a = Math.atan2(z - 600, x + 200), r = Math.hypot(x + 200, z - 600); return Math.min(13, Math.floor(((a + Math.PI) / (Math.PI * 2)) * 7) * 2 + (r > 1500 ? 1 : 0)); };
  for (let gx = -40; gx < 40; gx++) for (let gz = -60; gz < 30; gz++) {
    const x = gx * cell, z = gz * cell; if (Math.abs(z - (1300 - 1024) * 4 + Math.sin(x * 0.0007) * 640) < 200) continue; // Fluss
    const dist = Math.hypot(x, z + 800); if (q() < 0.12) continue;
    const n = q() < 0.5 ? 1 : 2; for (let k = 0; k < n; k++) {
      const w = 18 + q() * 26, dd = 18 + q() * 26, h = (dist < 1400 ? 40 + q() * 140 * Math.exp(-dist / 900) * 2 : 12 + q() * 30) * (q() < 0.05 ? 2.5 : 1);
      const px = x + (q() - 0.5) * (cell - w - 12), pz = z + (q() - 0.5) * (cell - dd - 12);
      D[sector(px, pz)].list.push([px, pz, w, dd, h]);
    }
  }
  const dummy = new THREE.Object3D();
  D.forEach(d => { const im = new THREE.InstancedMesh(geo, d.mat, d.list.length); d.list.forEach(([x, z, w, dd, h], i) => { dummy.position.set(x, 0, z); dummy.scale.set(w, h, dd); dummy.updateMatrix(); im.setMatrixAt(i, dummy.matrix); }); im.instanceMatrix.needsUpdate = true; scene.add(im); d.mesh = im; });
  // Straßenlaternen als Lichtpunkte pro Viertel
  const glowT = canvasTex(64, 64, g => { const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, 'rgba(255,220,160,1)'); r.addColorStop(0.2, 'rgba(255,170,80,0.6)'); r.addColorStop(1, 'rgba(255,140,40,0)'); g.fillStyle = r; g.fillRect(0, 0, 64, 64); });
  const lp = D.map(() => []);
  for (let gx = -40; gx < 40; gx++) for (let gz = -60; gz < 30; gz++) { const main = gx % 6 === 0 || gz % 6 === 0; for (let k = 0; k < (main ? 4 : 2); k++) { const along = q() < 0.5; const x = gx * cell - cell / 2 + (along ? q() * cell : 0) + (q() - 0.5) * 3, z = gz * cell - cell / 2 + (along ? 0 : q() * cell) + (q() - 0.5) * 3; if (q() < 0.7 || main) lp[sector(x, z)].push(x, 6, z); } }
  D.forEach((d, i) => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(lp[i], 3)); d.pts = new THREE.Points(g, new THREE.PointsMaterial({map: glowT, size: 16, color: '#ffb066', transparent: true, depthWrite: false, blending: THREE.AdditiveBlending})); scene.add(d.pts); });
  // Reihenfolge: vom Umspannwerk nach außen (aus), umgekehrt beim Einschalten
  const outOrder = [6, 7, 4, 5, 8, 9, 2, 3, 10, 11, 0, 1, 12, 13], inOrder = [0, 1, 12, 13, 10, 11, 2, 3, 8, 9, 4, 5, 6, 7];
  // Blitze in Umspannwerken (blau-weiß)
  const flash = new THREE.PointLight('#a8d8ff', 0, 1500, 1.2); scene.add(flash);
  const flashS = new THREE.Mesh(new THREE.SphereGeometry(18, 16, 12), new THREE.MeshBasicMaterial({color: '#dff2ff', transparent: true, opacity: 0, fog: false})); scene.add(flashS);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0; const back = shot.id === 'back';
    let litSum = 0;
    D.forEach((d, i) => {
      let on;
      if (!back) { const t0 = CITY_OUT + outOrder.indexOf(i) * 0.48; on = T < t0 ? 1 : T < t0 + 0.25 ? (Math.sin(T * 60 + i) > 0 ? 0.6 : 0.1) : 0; }
      else { const t0 = POWER_BACK + inOrder.indexOf(i) * 0.38; on = T < t0 ? 0 : T < t0 + 0.3 ? (Math.sin(T * 50 + i) > 0 ? 0.8 : 0.2) : 1; }
      d.mat.emissiveIntensity = 1.4 * on; d.pts.material.opacity = on; litSum += on;
    });
    const lit = litSum / D.length; drawSky(lit); stars.material.opacity = (1 - lit) * 0.9;
    // Umspannwerk-Blitze beim Ausfall
    const fl = !back ? [CITY_OUT - 0.1, CITY_OUT + 1.5, CITY_OUT + 3.4] : [POWER_BACK - 0.2];
    let fI = 0; fl.forEach((f, k) => { const e = T - f; if (e > 0 && e < 0.35) fI = Math.max(fI, Math.exp(-e * 10) * (0.6 + 0.4 * Math.sin(e * 90))); });
    flash.intensity = fI * 8e4; flashS.material.opacity = fI * 0.6; flash.position.set(-200, 60, 600); flashS.position.copy(flash.position);
    // Kamera: hoch über der Stadt, langsame Drift
    const k = back ? smooth(64, 72, T) : smooth(39, 47, T);
    const pos = back ? V(lerp(700, 450, k), lerp(520, 460, k), lerp(1900, 1650, k)) : V(lerp(-600, -350, k), lerp(560, 480, k), lerp(2000, 1750, k));
    pos.add(V(noise1(T * 0.3, 2) * 3, noise1(T * 0.3, 5) * 3, 0));
    camera.position.copy(pos); camera.lookAt(back ? V(-200, 0, -200) : V(-150, 0, -300)); camera.fov = 50; camera.updateProjectionMatrix();
    return {dof: null, exposure: 1.5, bloom: [0.9, 0.6, 0.55], grain: 0.06, vig: 0.42, ao: false};
  }};
}
