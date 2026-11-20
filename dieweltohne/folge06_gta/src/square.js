// Stufe 5: Launch-Party auf dem Platz in der Innenstadt, 40.000 Fans vor einer Riesenleinwand.
// Das Bild wird schwarz, die Menge drängt nach vorn, die Leinwand kippt vom Gerüst.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, envMap, sparkSystem, updateSparks} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {drawChase, drawHome} from './living.js';
import {WALL_BLACK, WALL_FALL} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const PUSH = WALL_BLACK + 0.9, IMPACT = WALL_FALL + 0.9;

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#070a14'); scene.fog = new THREE.Fog('#0b0f1c', 30, 120);
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.15;
  const hemi = new THREE.HemisphereLight('#5065a0', '#1a1410', 0.35); scene.add(hemi);
  const wallL = new THREE.PointLight('#ff6fa0', 60, 40, 1.4); wallL.position.set(0, 6, -4); scene.add(wallL);
  const wash = new THREE.SpotLight('#ffffff', 0, 60, 0.5, 0.6, 1.2); wash.position.set(0, 14, 20); wash.target.position.set(0, 0, 4); scene.add(wash, wash.target);
  // Boden: Pflaster
  const pT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#4a4a4e'; g.fillRect(0, 0, w, h); const r = rng(2); for (let y = 0; y < h; y += 16) for (let x = (y / 16 % 2) * 8; x < w; x += 16) { g.fillStyle = `rgb(${70 + r() * 25},${70 + r() * 25},${74 + r() * 25})`; g.fillRect(x + 1, y + 1, 14, 14); } });
  pT.wrapS = pT.wrapT = THREE.RepeatWrapping; pT.repeat.set(30, 30);
  const gr = mesh(new THREE.PlaneGeometry(120, 120), new THREE.MeshStandardMaterial({map: pT, roughness: 0.8}), 0, 0, 0, scene); gr.rotation.x = -Math.PI / 2;
  // Häuser rund um den Platz
  const r0 = rng(5);
  for (let i = 0; i < 16; i++) { const side = i < 8 ? -1 : 1, k = i % 8, h = 14 + r0() * 16, w = 8 + r0() * 4;
    const b = mesh(new THREE.BoxGeometry(10, h, w), new THREE.MeshStandardMaterial({map: facadeTex(['#6a5a4a', '#5a5f6a', '#7a6a5a', '#4a5560'][k % 4], 40 + i, Math.round(h / 3.2), 4), emissive: '#ffd9a0', emissiveIntensity: 0.0}), side * 24, h / 2, -20 + k * 9, scene);
    b.material.emissiveMap = b.material.map; b.material.emissiveIntensity = 0.35; }
  for (let i = 0; i < 6; i++) { const h = 20 + r0() * 20; const b = mesh(new THREE.BoxGeometry(9, h, 8), new THREE.MeshStandardMaterial({map: facadeTex('#5a5f6a', 70 + i, Math.round(h / 3.2), 4), emissive: '#ffd9a0', emissiveIntensity: 0.35}), -25 + i * 10, h / 2, -26, scene); b.material.emissiveMap = b.material.map; }
  // Bühne, Traversen, Leinwand
  mesh(new THREE.BoxGeometry(20, 1.2, 6), mat('#15161a'), 0, 0.6, -5, scene);
  const truss = mat('#9aa0a8', {metalness: 0.8, roughness: 0.35});
  for (const x of [-9.5, 9.5]) for (const dx of [-0.3, 0.3]) for (const dz of [-0.3, 0.3]) mesh(new THREE.CylinderGeometry(0.05, 0.05, 13, 6), truss, x + dx, 6.5, -8 + dz, scene);
  for (const x of [-9.5, 9.5]) for (let y = 1; y < 13; y += 1) mesh(new THREE.BoxGeometry(0.6, 0.04, 0.04), truss, x, y, -7.7, scene).rotation.z = 0.7;
  for (const dz of [-0.3, 0.3]) for (const dy of [-0.3, 0.3]) mesh(new THREE.CylinderGeometry(0.05, 0.05, 19.6, 6), truss, 0, 12.8 + dy, -8 + dz, scene).rotation.z = Math.PI / 2;
  const LC = document.createElement('canvas'); LC.width = 1024; LC.height = 576; const lT = new THREE.CanvasTexture(LC); lT.colorSpace = THREE.SRGBColorSpace;
  const wall = new THREE.Group(); wall.position.set(0, 2.2, -7.8); scene.add(wall); // Drehpunkt: Unterkante
  mesh(new THREE.BoxGeometry(16.4, 9.4, 0.4), mat('#0b0b0c', {metalness: 0.5}), 0, 4.6, -0.22, wall);
  const screen = mesh(new THREE.PlaneGeometry(16, 9), new THREE.MeshBasicMaterial({map: lT, toneMapped: false}), 0, 4.6, 0.0, wall);
  // Lautsprechertürme
  for (const x of [-11.5, 11.5]) for (let i = 0; i < 4; i++) mesh(new RoundedBoxGeometry(1.4, 0.9, 1.0, 2, 0.05), mat('#111'), x, 1.6 + i * 0.95, -6.5, scene);
  // Scheinwerferkegel
  const beamM = new THREE.MeshBasicMaterial({color: '#9ad0ff', transparent: true, opacity: 0.12, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide});
  const beams = []; for (let i = 0; i < 6; i++) { const g = new THREE.ConeGeometry(2.2, 30, 20, 1, true); g.translate(0, -15, 0); const b = new THREE.Mesh(g, beamM.clone()); b.position.set(-8 + i * 3.2, 13, -7.5); scene.add(b); b.material.color.set(['#9ad0ff', '#ff6fd0', '#ffd36f'][i % 3]); beams.push(b); }
  // Menge: Instanzen (Körper, Kopf, Handylicht)
  const N = 1400, r = rng(8); const crowd = [];
  for (let i = 0; i < N; i++) { const z = -1.2 + Math.pow(r(), 0.8) * 30, x = (r() - 0.5) * (22 + z * 0.6); crowd.push({x, z, ph: r() * 6, hgt: 0.9 + r() * 0.2, phone: r() < 0.22, sp: 4 + r() * 2.5, push: 1 + r() * 1.5}); }
  const bodyI = new THREE.InstancedMesh(new THREE.CapsuleGeometry(0.22, 0.75, 3, 8), new THREE.MeshStandardMaterial({roughness: 0.8}), N);
  const headI = new THREE.InstancedMesh(new THREE.SphereGeometry(0.13, 10, 8), new THREE.MeshStandardMaterial({roughness: 0.7}), N);
  const phI = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.08, 0.14), new THREE.MeshBasicMaterial({color: '#e8f2ff', toneMapped: false}), N);
  const tops = ['#e2b23a', '#d94b3d', '#3f6fb5', '#2f8f6b', '#e8e2d4', '#7b4fa0', '#e07a2f', '#24343f', '#c23b6a', '#4aa3c7', '#222', '#555'], skins = ['#f1c7a5', '#d9a47e', '#a8714a', '#6b4429', '#e8b894'];
  const c = new THREE.Color(); crowd.forEach((p, i) => { bodyI.setColorAt(i, c.set(tops[i % tops.length])); headI.setColorAt(i, c.set(skins[(i * 7) % skins.length])); });
  [bodyI, headI, phI].forEach(m => { m.frustumCulled = false; }); scene.add(bodyI, headI, phI);
  // Einzelne LED-Module, die abbrechen und herunterfallen
  const modM = new THREE.MeshStandardMaterial({color: '#222', emissive: '#5a8cff', emissiveIntensity: 1.2});
  const mods = []; { const q = rng(14); for (let i = 0; i < 28; i++) { const m = mesh(new THREE.BoxGeometry(1.0, 1.0, 0.12), [mat('#111'), mat('#111'), mat('#111'), mat('#111'), modM, mat('#111')], 0, -9, 0, scene);
    mods.push({m, x: -7.5 + (i % 14) * 1.15 + q() * 0.2, y0: 2.6 + Math.floor(i / 14) * 1.0 + q() * 0.4, d: q() * 0.9, vx: (q() - 0.5) * 2, vz: 1.5 + q() * 3, rx: (q() - 0.5) * 8, rz: (q() - 0.5) * 6}); } }
  const dust = particles(900, 'smoke'); scene.add(dust); const sparks = sparkSystem(900, 0.08); scene.add(sparks);
  const confetti = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.06, 0.1), new THREE.MeshBasicMaterial({side: THREE.DoubleSide}), 500); confetti.frustumCulled = false; scene.add(confetti);
  { const cc = new THREE.Color(); for (let i = 0; i < 500; i++) confetti.setColorAt(i, cc.setHSL((i * 0.13) % 1, 0.9, 0.6)); }

  function drawWall(T) {
    const g = LC.getContext('2d'), w = 1024, h = 576;
    if (T < WALL_BLACK) { drawChase(g, w, h, T); g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(0, 0, w, 80); g.fillStyle = '#fff'; g.font = '600 46px Plex'; g.textAlign = 'center'; g.fillText('LAUNCH-PARTY · LIVE', w / 2, 56); }
    else if (T < WALL_BLACK + 0.6) { drawChase(g, w, h, WALL_BLACK); const q = rng(Math.floor(T * 30)); for (let i = 0; i < 50; i++) { g.fillStyle = ['#f0f', '#0ff', '#000', '#fff'][Math.floor(q() * 4)]; g.fillRect(q() * w, q() * h, q() * 500, 4 + q() * 40); }
      g.fillStyle = `rgba(0,0,0,${(T - WALL_BLACK) / 0.6})`; g.fillRect(0, 0, w, h); }
    else if (T < WALL_BLACK + 1.4) { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); }
    else { drawHome(g, w, h, T, 1); }
    if (T > WALL_FALL - 0.4) { const q = rng(Math.floor(T * 20) + 9); g.fillStyle = 'rgba(0,0,0,0.6)'; for (let i = 0; i < 30; i++) g.fillRect(Math.floor(q() * 16) * 64, Math.floor(q() * 9) * 64, 64, 64); }
    lT.needsUpdate = true;
  }

  const camera = new THREE.PerspectiveCamera(48, 1080 / 1920, 0.1, 300); scene.add(camera);
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), S = V3(1, 1, 1), P = V3(0, 0, 0);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    drawWall(T);
    const party = T < WALL_BLACK, black = T >= WALL_BLACK;
    wallL.intensity = party ? 60 : (T < WALL_BLACK + 1.4 ? 4 : 25); wallL.color.set(party ? '#ff6fa0' : '#5a8cff');
    if (T > IMPACT) wallL.intensity = 6;
    wash.intensity = T > WALL_BLACK + 1.0 ? 120 : 0; // Arbeitslicht geht an
    beams.forEach((b, i) => { b.visible = party; b.rotation.z = Math.sin(T * 0.9 + i) * 0.5; b.rotation.x = 0.3 + Math.sin(T * 0.7 + i * 2) * 0.25; });
    // Leinwand kippt nach vorn
    // Leinwand reißt oben ab und hängt schief nach vorn, Module fallen herunter
    let fk = 0; if (T > WALL_FALL) { const d = T - WALL_FALL; fk = d < 0.6 ? Math.pow(d / 0.6, 2) : 1 + Math.sin((d - 0.6) * 9) * Math.exp(-(d - 0.6) * 3) * 0.12; } else if (T > WALL_FALL - 0.8) fk = Math.sin((T - WALL_FALL + 0.8) * 20) * 0.01;
    wall.rotation.x = fk * 0.42; wall.rotation.z = fk * 0.06;
    mods.forEach(o => { const d = T - WALL_FALL - 0.35 - o.d; if (d < 0) { o.m.position.y = -9; return; }
      const fy = o.y0 - 4.9 * d * d, land = fy <= 0.06; const td = land ? Math.sqrt((o.y0 - 0.06) / 4.9) : d;
      o.m.position.set(o.x + o.vx * td, land ? 0.06 : fy, -7.4 + o.vz * td + (o.y0 > 3 ? 0 : 0)); o.m.rotation.set(land ? -Math.PI / 2 : o.rx * td, 0, land ? o.rz : o.rz * td);
      if (o.x > -10 && o.x < 10 && o.m.position.z < -2 && o.m.position.y < 1.3) o.m.position.y = Math.max(o.m.position.y, 1.26); });
    modM.emissiveIntensity = T > IMPACT + 0.5 ? 0.15 : 1.2;
    // Menge
    crowd.forEach((p, i) => {
      let x = p.x, z = p.z, y = 0;
      if (party) y = Math.max(0, Math.sin(T * 7.5 + p.ph)) * 0.18;
      if (T > PUSH) z -= Math.min(p.push, (T - PUSH) * 1.2) * clamp(1 - p.z / 30);
      if (T > WALL_FALL + 0.3) { const d = Math.min(T - WALL_FALL - 0.3, 3.5); z += d * p.sp * 0.55 * clamp(d * 1.5); x += Math.sign(p.x) * d * 0.5; y = Math.abs(Math.sin(T * 12 + p.ph)) * 0.08; }
      P.set(x, 0.62 * p.hgt + y, z); S.set(1, p.hgt, 1); M.compose(P, Q, S); bodyI.setMatrixAt(i, M);
      P.set(x, 1.4 * p.hgt + y, z); S.set(1, 1, 1); M.compose(P, Q, S); headI.setMatrixAt(i, M);
      const ph = p.phone && T < WALL_FALL + 0.3; P.set(x + 0.15, ph ? 1.85 * p.hgt + y : -9, z - 0.1); M.compose(P, Q, S); phI.setMatrixAt(i, M);
    });
    bodyI.instanceMatrix.needsUpdate = headI.instanceMatrix.needsUpdate = phI.instanceMatrix.needsUpdate = true;
    // Konfetti während der Party
    const cr = rng(3); for (let i = 0; i < 500; i++) { const x = (cr() - 0.5) * 26, z = cr() * 20, sp = 0.8 + cr(), y0 = 14 * cr(); const y = party ? ((y0 - T * sp) % 14 + 14) % 14 : -5;
      M.makeRotationFromEuler(new THREE.Euler(T * 3 + i, T * 2 + i * 0.5, 0)); M.setPosition(x + Math.sin(T + i) * 0.4, y, z); confetti.setMatrixAt(i, M); } confetti.instanceMatrix.needsUpdate = true;
    // Aufprall: Funken und Staub
    updateSparks(sparks, T > IMPACT - 0.1 ? [-6, -2, 2, 6].map(x => ({pos: V3(x, 2.4, -6.8), dir: V3(0, 2, 3), t0: WALL_FALL, t1: IMPACT + 0.8})) : [], T, 9.8);
    updateParticles(dust, T > IMPACT ? [{type: 'burstSmoke', pos: V3(0, 1.5, -4), r: 9, t0: IMPACT, size: 3.5, rise: 1.0, share: 1}] : [], T, V3(0.5, 0, 1));
    // Kamera auf dem Technikturm hinter der Menge
    const k = smooth(0, 9, t), sh = T > IMPACT && T < IMPACT + 1.2 ? 0.08 * (1 - (T - IMPACT) / 1.2) : 0.005;
    camera.position.set(3.5 + noise1(T * 3, 2) * sh, lerp(7.5, 8.5, k) + noise1(T * 3, 4) * sh, lerp(27, 24, k));
    camera.lookAt(0, lerp(5.5, 4.0, k), -6);
    camera.updateProjectionMatrix();
  }};
}
