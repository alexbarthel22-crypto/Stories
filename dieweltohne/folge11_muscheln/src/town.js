// Altstadt mit Marktplatz und Kirche aus Muschelkalk.
// church: Stufe 5 – der Kirchturm wird löchrig wie ein Käse, kippt und kracht auf die leere Häuserzeile.
// rain:   Stufe 6 – die Muscheln sind zurück und regnen vom Himmel.
// aerial: Stufe 7 – Luftbild: Ein Muschelberg begräbt die halbe Stadt.
// final:  Oben auf dem Berg taucht er auf – zuerst die Hand mit dem Handy, dann der Kopf – und jubelt.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, skyDome, easeOut, easeIn, makePerson, posePerson, makeCar, envMap} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {addMouth, mouthOpen, brows} from './people.js';
import {shellSwarm, heapTex} from './shells.js';
import {makePhone, updateScreen} from './phone.js';
import {HOLES, TILT, TOWER_HIT, RETURN, HAND_UP, HEAD_UP, GULP} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

// Material mit wachsenden Löchern (Objektkoordinaten, damit die Löcher beim Kippen mitwandern)
function holeMat(base, uniforms, scale = 0.9) {
  const m = base; m.side = THREE.DoubleSide;
  m.onBeforeCompile = sh => {
    sh.uniforms.uHoles = uniforms.uHoles;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vLP;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvLP = position;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
uniform float uHoles; varying vec3 vLP;
float h3(vec3 p){ p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
float vn(vec3 x){ vec3 i = floor(x); vec3 f = fract(x); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(h3(i), h3(i + vec3(1,0,0)), f.x), mix(h3(i + vec3(0,1,0)), h3(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(h3(i + vec3(0,0,1)), h3(i + vec3(1,0,1)), f.x), mix(h3(i + vec3(0,1,1)), h3(i + vec3(1,1,1)), f.x), f.y), f.z); }`)
      .replace('#include <map_fragment>', `#include <map_fragment>
float hn = vn(vLP * ${scale.toFixed(2)}) * 0.65 + vn(vLP * ${(scale * 2.7).toFixed(2)}) * 0.35;
if (hn < uHoles) discard;
if (hn < uHoles + 0.035) diffuseColor.rgb *= 0.35;`);
  };
  m.customProgramCacheKey = () => 'holes' + scale;
  return m;
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  const sky = skyDome('#5f8fcf', '#a9c6e6', '#e8eef2', 1500); scene.add(sky);
  scene.fog = new THREE.Fog('#d8e0e8', 120, 1100);
  const hemi = new THREE.HemisphereLight('#e6f0ff', '#5a5040', 0.85); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff0d8', 2.7); sun.position.set(40, 60, 30); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -45, right: 45, top: 45, bottom: -45, near: 1, far: 220}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.04; scene.add(sun, sun.target);
  // Boden: Kopfsteinpflaster
  const cobT = canvasTex(512, 512, (g, w, h) => { const r = rng(4); g.fillStyle = '#6b665e'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += 32) for (let x = (y / 32) % 2 * 16; x < w; x += 32) { const v = 125 + r() * 45; g.fillStyle = `rgb(${v},${v - 5},${v - 12})`; g.beginPath(); g.roundRect(x + 2, y + 2, 28, 28, 8); g.fill(); } });
  cobT.wrapS = cobT.wrapT = THREE.RepeatWrapping; cobT.repeat.set(220, 220);
  mesh(new THREE.PlaneGeometry(2400, 2400), new THREE.MeshStandardMaterial({map: cobT, roughness: 0.9}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  // Muschelkalk: gelbgraue Quader mit Muschelabdrücken
  const kalkT = canvasTex(512, 512, (g, w, h) => { const r = rng(7); g.fillStyle = '#cbbb98'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += 42) for (let x = (y / 42) % 2 * 40; x < w + 80; x += 80) { const v = r() * 20 - 10; g.fillStyle = `rgb(${200 + v},${186 + v},${150 + v})`; g.fillRect(x + 2, y + 2, 76, 38); }
    for (let i = 0; i < 700; i++) { const x = r() * w, y = r() * h, s = 1 + r() * 4; g.strokeStyle = `rgba(110,95,70,${0.25 + r() * 0.3})`; g.lineWidth = 1; g.beginPath(); g.arc(x, y, s, Math.PI, 0); g.stroke(); }
    for (let i = 0; i < 2000; i++) { g.fillStyle = `rgba(90,80,60,${r() * 0.12})`; g.fillRect(r() * w, r() * h, 2, 2); } });
  kalkT.wrapS = kalkT.wrapT = THREE.RepeatWrapping;
  const U = {uHoles: {value: -1}};
  const towT = kalkT.clone(); towT.needsUpdate = true; towT.repeat.set(2, 9); const naveT = kalkT.clone(); naveT.needsUpdate = true; naveT.repeat.set(6, 3);
  const towerM = holeMat(new THREE.MeshStandardMaterial({map: towT, roughness: 0.9}), U, 0.9);
  const naveM = holeMat(new THREE.MeshStandardMaterial({map: naveT, roughness: 0.9}), U, 0.7);
  const roofM = mat('#6b3a2c', {roughness: 0.8}), slateM = mat('#3e4249', {roughness: 0.7});
  // Kirche: Schiff + Turm (Turm kippt um seine rechte vordere Kante)
  const church = new THREE.Group(); church.position.set(0, 0, -11); scene.add(church);
  mesh(new THREE.BoxGeometry(11, 10, 22), naveM, 0, 5, -11, church);
  const nroof = new THREE.CylinderGeometry(6.6, 6.6, 22.4, 3, 1); nroof.rotateX(-Math.PI / 2);
  const nr = mesh(nroof, roofM, 0, 12.4, -11, church); nr.rotation.set(0, 0, 0); nr.scale.set(1.0, 0.75, 1); nr.rotation.x = 0; nr.rotation.z = Math.PI / 2 * 0;
  const pivot = new THREE.Group(); pivot.position.set(-2.5, 0, 2.5); church.add(pivot); // linke vordere Kante
  const tower = new THREE.Group(); tower.position.set(2.5, 0, -2.5); pivot.add(tower);
  mesh(new THREE.BoxGeometry(5, 26, 5, 10, 40, 10), towerM, 0, 13, 0, tower);
  // Schallöffnungen, Uhr, Spitzhelm
  const darkM = mat('#1e1a16', {roughness: 1});
  for (const [x, z, ry] of [[0, 2.52, 0], [2.52, 0, Math.PI / 2], [0, -2.52, 0], [-2.52, 0, Math.PI / 2]]) {
    const o = mesh(new THREE.PlaneGeometry(1.2, 2.4), darkM, x, 22, z, tower); o.rotation.y = ry;
    const clockT = canvasTex(128, 128, (g, w) => { g.fillStyle = '#f2eee2'; g.beginPath(); g.arc(64, 64, 60, 0, 7); g.fill(); g.strokeStyle = '#222'; g.lineWidth = 4; for (let k = 0; k < 12; k++) { const a = k / 12 * 7; g.beginPath(); g.moveTo(64 + Math.cos(a) * 46, 64 + Math.sin(a) * 46); g.lineTo(64 + Math.cos(a) * 56, 64 + Math.sin(a) * 56); g.stroke(); }
      g.lineWidth = 6; g.beginPath(); g.moveTo(64, 64); g.lineTo(64, 24); g.stroke(); g.beginPath(); g.moveTo(64, 64); g.lineTo(92, 70); g.stroke(); });
    const c = mesh(new THREE.CircleGeometry(1.0, 32), new THREE.MeshStandardMaterial({map: clockT, roughness: 0.5}), x * 1.004, 17.5, z * 1.004, tower); c.rotation.y = ry + (z < 0 || x < 0 ? Math.PI : 0); }
  const spire = mesh(new THREE.ConeGeometry(3.6, 11, 4), slateM, 0, 31.5, 0, tower); spire.rotation.y = Math.PI / 4;
  mesh(new THREE.CylinderGeometry(0.06, 0.06, 2, 6), mat('#c9a44a', {metalness: 1, roughness: 0.3}), 0, 38, 0, tower);
  const bell = mesh(new THREE.CylinderGeometry(0.35, 0.65, 1.0, 16, 1, true), mat('#8a6a2a', {metalness: 0.9, roughness: 0.35, side: THREE.DoubleSide}), 0, 22, 0, tower);
  // Häuser um den Platz (und weiter hinaus für das Luftbild)
  const houses = [];
  const roofG = new THREE.CylinderGeometry(1, 1, 1, 3, 1); roofG.rotateZ(Math.PI / 2); roofG.rotateX(-Math.PI / 2); // Prisma, First entlang x
  const facMs = []; for (let k = 0; k < 6; k++) facMs.push(new THREE.MeshStandardMaterial({map: facadeTex(['#e8d9c0', '#d9c3a3', '#cfd6dc', '#e6cfc5', '#c9b79a', '#efe6d4'][k], 11 + k, 5, 4), roughness: 0.9}));
  function house(x, z, w, d, h, ry, k) { const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; scene.add(g);
    mesh(new THREE.BoxGeometry(w, h, d), facMs[k % 6], 0, h / 2, 0, g); const r = mesh(roofG, k % 3 ? roofM : slateM, 0, h + d * 0.28, 0, g); r.scale.set(w * 1.02, d * 0.36, d * 0.6);
    houses.push(g); return g; }
  // Platzränder (Marktplatz ca. 40 x 40 m)
  { const r = rng(3); let k = 0;
    for (let x = -26; x <= 26; x += 8.6) { if (Math.abs(x) > 7) house(x, -18, 8.4, 10, 12 + r() * 5, 0, k++); house(x, 26, 8.4, 10, 12 + r() * 5, 0, k++); }
    for (let z = -12; z <= 22; z += 8.6) { house(-26, z, 8.4, 10, 12 + r() * 5, Math.PI / 2, k++); house(26, z, 8.4, 10, 12 + r() * 5, Math.PI / 2, k++); }
    // Stadt drumherum (für das Luftbild): Blöcke
    const far = new THREE.Group(); scene.add(far);
    for (let gx = -14; gx <= 14; gx++) for (let gz = -14; gz <= 14; gz++) { if (Math.abs(gx) <= 3 && Math.abs(gz) <= 3) continue; if (r() < 0.12) continue;
      const x = gx * 22 + (r() - 0.5) * 4, z = gz * 22 + (r() - 0.5) * 4; const h = 9 + r() * 10, w = 12 + r() * 6, d = 10 + r() * 5;
      const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = r() < 0.5 ? 0 : Math.PI / 2; far.add(g);
      mesh(new THREE.BoxGeometry(w, h, d), facMs[(gx * 7 + gz * 3 + 99) % 6], 0, h / 2, 0, g); const rf = mesh(roofG, r() < 0.6 ? roofM : slateM, 0, h + d * 0.28, 0, g); rf.scale.set(w * 1.02, d * 0.36, d * 0.6); }
    scene.userData.far = far; }
  // Marktstände
  const awnM = [mat('#c4232f'), mat('#2f6fb3'), mat('#2f8f5b')];
  for (let i = 0; i < 3; i++) { const s = new THREE.Group(); s.position.set(-19 + i * 6, 0, 9 + (i % 2) * 4); scene.add(s);
    mesh(new THREE.BoxGeometry(3, 0.9, 1.4), mat('#8a6a48'), 0, 0.45, 0, s); for (const x of [-1.4, 1.4]) mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.4, 6), mat('#666'), x, 1.2, 0.6, s);
    const a = mesh(new THREE.BoxGeometry(3.3, 0.06, 1.9), awnM[i % 3], 0, 2.45, 0.1, s); a.rotation.x = 0.15; }
  // Autos am Rand
  const cars = []; for (let i = 0; i < 5; i++) { const c = makeCar(i + 1); c.position.set(-16 + i * 6.5, 0, 20.5); c.rotation.y = Math.PI / 2; scene.add(c); cars.push(c); }
  // Menschen auf dem Platz
  const crowd = []; { const r = rng(5); for (let i = 0; i < 22; i++) { const p = makePerson(1500 + i, {longHair: r() < 0.5}); addMouth(p); scene.add(p);
    crowd.push({p, x: -14 + r() * 26, z: -4 + r() * 20, ry: r() * 6, sp: 2.5 + r() * 2, umb: i % 4 === 0}); } }
  crowd.forEach(c => { if (!c.umb) return; const u = new THREE.Group(); c.p.userData.armR.userData.fore.add(u); u.position.set(0, -0.3, 0);
    mesh(new THREE.CylinderGeometry(0.01, 0.01, 0.9, 6), mat('#222'), 0, 0.45, 0, u); const cnp = mesh(new THREE.ConeGeometry(0.55, 0.25, 12, 1, true), mat(['#d62a5a', '#2a6bd6', '#f2c21b'][c.x > 0 ? 0 : 1], {side: THREE.DoubleSide, roughness: 0.6}), 0, 0.95, 0, u); c.umbrella = u; });
  // Staub, Trümmer
  const dust = particles(700, 'smoke'); scene.add(dust);
  const chunks = new THREE.InstancedMesh(new RoundedBoxGeometry(1, 1, 1, 1, 0.1), new THREE.MeshStandardMaterial({map: kalkT, roughness: 0.9}), 160); chunks.castShadow = true; chunks.frustumCulled = false; scene.add(chunks);
  const CH = []; { const r = rng(44); for (let i = 0; i < 160; i++) CH.push({s: 0.4 + r() * 1.6, along: r() * 34, side: (r() - 0.5) * 6, vx: (r() - 0.5) * 8, vy: 2 + r() * 9, vz: (r() - 0.5) * 8, rx: r() * 6, ry: r() * 6}); }
  const rubble = new THREE.Group(); scene.add(rubble); { const r = rng(45); const rm = new THREE.MeshStandardMaterial({map: kalkT, roughness: 0.95});
    for (let i = 0; i < 60; i++) { const b = mesh(new RoundedBoxGeometry(1, 1, 1, 1, 0.12), rm, 0, 0, 0, rubble); const s = 0.6 + r() * 2.2; b.scale.set(s, s * 0.6, s * (0.8 + r())); b.position.set(-4 - r() * 22, s * 0.25, -9 + (r() - 0.5) * 7); b.rotation.set(r(), r() * 3, r()); } }
  // Muschelregen: fallende Muscheln + Bodenbelag
  const NR = 9000; const rain = shellSwarm(NR, scene, {scale: 2.4});
  const RR = []; { const r = rng(61); for (let i = 0; i < NR; i++) RR.push({x: (r() - 0.5) * 22, z: -2 + r() * 17, t0: RETURN + 0.3 + r() * 9.6, v: 14 + r() * 6, rx: r() * 6, ry: r() * 6, sp: (r() - 0.5) * 20, s: 0.8 + r() * 0.6}); }
  const groundT = heapTex(21, 1024, 6500); groundT.repeat.set(10, 10);
  const groundShells = mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({map: groundT, roughness: 0.75, transparent: true, opacity: 0, color: '#dcdce0'}), 0, 0.03, 4, scene); groundShells.rotation.x = -Math.PI / 2; groundShells.castShadow = false;
  // Muschelberg (Luftbild/Finale): Kegel mit unregelmäßigem Rand
  const mT = heapTex(33, 2048, 16000); mT.repeat.set(9, 9);
  const mGeo = new THREE.ConeGeometry(160, 95, 96, 30, true); { const p = mGeo.attributes.position; const r = rng(9);
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), a = Math.atan2(z, x), k = (95 / 2 - y) / 95;
      const wob = 1 + 0.08 * Math.sin(a * 5) + 0.05 * Math.sin(a * 11 + 1) + (r() - 0.5) * 0.02; const sag = Math.pow(k, 0.85);
      p.setXYZ(i, x * wob, y - (1 - sag) * 0 + 3 * Math.sin(a * 7) * k, z * wob); } mGeo.computeVertexNormals(); }
  // Weiche Kuppe statt Spitze
  const mountain = new THREE.Group(); mountain.position.set(120, 0, -150); scene.add(mountain);
  const cone = mesh(mGeo, new THREE.MeshStandardMaterial({map: mT, roughness: 0.75, color: '#d8d8dc'}), 0, 95 / 2 - 2, 0, mountain); cone.castShadow = true;
  const cap = mesh(new THREE.SphereGeometry(14, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({map: mT, roughness: 0.75, color: '#d8d8dc'}), 0, 85, 0, mountain); cap.scale.y = 0.45;
  const domeT = heapTex(41, 2048, 16000); domeT.repeat.set(14, 14);
  const domeG = new THREE.PlaneGeometry(60, 60, 120, 120); domeG.rotateX(-Math.PI / 2); { const p = domeG.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), d2 = x * x + z * z; p.setY(i, -0.035 * d2 + 0.02 * Math.sin(x * 3) * Math.cos(z * 2.6)); } domeG.computeVertexNormals(); }
  const dome = mesh(domeG, new THREE.MeshStandardMaterial({map: domeT, roughness: 0.7, color: '#d8d8dc'}), 120, 85 + 14 * 0.45, -150, scene); dome.castShadow = false;
  const topSwarm = shellSwarm(4500, scene, {scale: 2.4});
  { const r = rng(71); const top = V3(120, 85 + 14 * 0.45, -150); for (let i = 0; i < 4500; i++) { const a = r() * 7, d = Math.pow(r(), 0.7) * 4.5;
      const y = top.y - 0.035 * d * d + 0.03; topSwarm.set(i, top.x + Math.cos(a) * d, y, top.z + Math.sin(a) * d, (r() - 0.5), r() * 6, (r() - 0.5), 0.8 + r() * 0.6); } topSwarm.commit(); }
  // Der Streamer (gleicher Look wie im Zimmer) und seine Auster
  const guy = makePerson(1101, {skin: '#e2b28c', top: '#ff7a3d', pants: '#22262e', hair: '#2a1d15', height: 1.0}); addMouth(guy); scene.add(guy);
  mesh(new THREE.TorusGeometry(0.13, 0.014, 8, 24, Math.PI), mat('#111', {roughness: 0.4}), 0, 0.08, -0.005, guy.userData.head);
  for (const s of [-1, 1]) mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.03, 16), mat('#111'), s * 0.13, 0.05, 0, guy.userData.head).rotation.z = Math.PI / 2;
  const ph = makePhone(); scene.add(ph); ph.userData.caseM.color.set('#e8467c'); Object.assign(ph.userData.scr.material, {color: new THREE.Color('#000'), clearcoat: 0.15, roughness: 0.35, envMapIntensity: 0.15, emissiveIntensity: 1.0});
  // Handy-Bildschirm: Kontostand explodiert
  const rich = (g, st, SW, SH) => { const gr = g.createLinearGradient(0, 0, SW * 0.4, SH); gr.addColorStop(0, '#14b3c2'); gr.addColorStop(1, '#07547a'); g.fillStyle = gr; g.fillRect(0, 0, SW, SH);
    const k = smooth(85.9, 87.8, st.T), n = Math.floor(Math.pow(k, 3) * 999999999999);
    g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = '260px sans-serif'; g.fillText('🐚', SW / 2, 470);
    g.fillStyle = '#2a1b12'; g.beginPath(); g.roundRect(34, 716, SW - 60, 190, 60); g.fill(); g.fillStyle = '#fff8e7'; g.beginPath(); g.roundRect(30, 706, SW - 60, 190, 60); g.fill(); g.strokeStyle = '#2a1b12'; g.lineWidth = 8; g.stroke();
    g.fillStyle = '#e8467c'; g.font = '900 ' + (n > 1e8 ? 62 : 90) + 'px sans-serif'; g.fillText(n.toLocaleString('de-DE'), SW / 2, 803); };

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 3000); scene.add(camera);
  const o3 = new THREE.Object3D();
  return {scene, camera, update(shot, T) {
    const id = shot.id, t = T - shot.t0;
    // Löcher wachsen
    U.uHoles.value = T < HOLES ? -1 : 0.5 * Math.pow(smooth(HOLES, TILT + 0.3, T), 0.9);
    // Turm kippt nach rechts (um die z-Achse) und schlägt auf
    const fallU = clamp((T - TILT) / (TOWER_HIT - TILT)); const ang = (Math.PI / 2 - 0.08) * easeIn(fallU) + 0.06 * smooth(TILT - 0.6, TILT, T);
    pivot.rotation.z = ang; tower.visible = T < TOWER_HIT; bell.rotation.z = 0.5 * Math.sin(T * 6) * smooth(TILT - 0.8, TILT, T);
    rubble.visible = T >= TOWER_HIT;
    // Trümmerbrocken beim Aufprall
    for (let i = 0; i < 160; i++) { const c = CH[i], dt = T - TOWER_HIT;
      if (dt > 0 && dt < 4 && id !== 'aerial' && id !== 'final') { const x0 = -2.5 - c.along, y = Math.max(c.s * 0.3, 1 + c.vy * dt - 4.9 * dt * dt); o3.position.set(x0 + c.vx * Math.min(dt, 1.4), y, -8.5 + c.side + c.vz * Math.min(dt, 1.4)); o3.rotation.set(c.rx + dt * 3, c.ry + dt * 2, 0); o3.scale.setScalar(c.s); }
      else { o3.position.set(0, -99, 0); o3.scale.setScalar(0.0001); }
      o3.updateMatrix(); chunks.setMatrixAt(i, o3.matrix); } chunks.instanceMatrix.needsUpdate = true;
    // Staubwolke
    const dsrc = [];
    if (T > TOWER_HIT && (id === 'church' || id === 'rain')) for (let k = 0; k < 6; k++) dsrc.push({type: 'burstSmoke', pos: V3(-4 - k * 4.5, 1, -8.5), r: 10, t0: TOWER_HIT + k * 0.05, size: 9, rise: 0.6, col: [0.78, 0.72, 0.6], alpha: 0.6, share: 1});
    if (id === 'church' && T > HOLES) dsrc.push({type: 'smoke', pos: V3(0, 14, -11), r: 3, t0: HOLES, size: 3, rise: -0.8, col: [0.8, 0.75, 0.62], alpha: 0.25 * smooth(HOLES, TILT, T), share: 0.6});
    updateParticles(dust, dsrc, T, V3(0.8, 0, 0.3));
    // Menschen: erst bummeln, dann gaffen, dann rennen (nach links weg); im Regen: Arme über den Kopf, Schirme
    crowd.forEach((c, i) => { const p = c.p, u = p.userData; p.visible = id === 'church' || id === 'rain';
      if (id === 'church') { const run = smooth(TILT - 0.4, TILT + 0.4, T);
        const x = c.x + run * c.sp * Math.max(0, T - TILT + 0.4) * 1.2; p.position.set(x, 0, c.z); p.rotation.set(0, lerp(Math.PI + 0.3 * Math.sin(i), Math.PI / 2, run), 0);
        posePerson(p, {walk: T * (6 + run * 6), walkAmp: run, armsUp: 0.3 * run}); u.head.rotation.x = -0.4 * (1 - run) * smooth(HOLES, HOLES + 1, T); mouthOpen(p, 0.6 * smooth(HOLES + 0.5, HOLES + 1.5, T)); brows(p, smooth(HOLES, HOLES + 1, T), 0); }
      else if (id === 'rain') { p.position.set(-6 + (i % 6) * 2.4 + Math.sin(i) * 0.4, 0, 2 + Math.floor(i / 6) * 3.2); p.rotation.set(0, Math.sin(i * 3) * 0.8, 0);
        posePerson(p, {walk: T * 9 + i, walkAmp: 0.35}); const cov = smooth(RETURN + 0.4, RETURN + 1.0, T);
        if (!c.umb) { u.armL.rotation.x = -2.6 * cov; u.armR.rotation.x = -2.6 * cov; u.armL.rotation.z = 0.4 * cov; u.armR.rotation.z = -0.4 * cov; u.armL.userData.fore.rotation.x = u.armR.userData.fore.rotation.x = -1.4 * cov; }
        else { u.armR.rotation.x = -1.6; u.armR.userData.fore.rotation.x = -0.9; }
        u.head.rotation.x = -0.3 * cov; mouthOpen(p, 0.7); brows(p, 1, 0); }
      if (c.umbrella) c.umbrella.visible = id === 'rain'; });
    cars.forEach(c => { c.visible = id === 'church' || id === 'rain'; });
    // Muschelregen
    const raining = id === 'rain';
    for (let i = 0; i < NR; i++) { const d = RR[i], dt = T - d.t0;
      if (!raining || dt < 0) { rain.hide(i); continue; }
      const y = 30 - d.v * dt; if (y > 0.03) rain.set(i, d.x, y, d.z, d.rx + dt * d.sp, d.ry, dt * d.sp * 0.5, d.s); else rain.set(i, d.x, 0.04, d.z, 0.1, d.ry, 0.1, d.s); }
    rain.commit(); rain.visible = raining;
    groundShells.visible = raining; groundShells.material.opacity = 0.95 * smooth(RETURN + 1.5, 57.5, T);
    // Luftbild / Finale
    const big = id === 'aerial'; mountain.visible = big; dome.visible = id === 'final'; topSwarm.visible = id === 'final'; scene.userData.far.visible = id !== 'final' || true;
    guy.visible = id === 'final'; ph.visible = id === 'final';
    if (id === 'final') { const top = V3(120, 85 + 14 * 0.45, -150); const u = guy.userData;
      const hand = smooth(HAND_UP, HAND_UP + 0.5, T), head = smooth(HEAD_UP, HEAD_UP + 0.6, T);
      guy.position.set(top.x, top.y - 1.78 + 0.1 * hand + 0.4 * head, top.z + 0.3); guy.rotation.set(0, 0.25, 0); posePerson(guy, {}); brows(guy, 1, 0);
      u.armR.rotation.x = -2.9; u.armR.rotation.z = 0.15 * Math.sin(T * 9) * (1 - head); u.armR.userData.fore.rotation.x = -0.1; u.armL.rotation.x = -0.2; mouthOpen(guy, 0.2);
      // Er hält das Handy in die Kamera (der Kontostand explodiert) und jubelt
      const look = smooth(86.4, 87.0, T), cheer = smooth(GULP - 0.2, GULP + 0.3, T);
      u.armR.rotation.x = lerp(-2.9, -1.6, look) - 1.2 * cheer; u.armR.userData.fore.rotation.x = lerp(-0.1, -1.1, look) + 0.9 * cheer; u.armR.rotation.z = 0.15 * Math.sin(T * 9) * (1 - head) + 0.8 * cheer;
      u.head.rotation.x = 0.2 * look * (1 - cheer) - 0.25 * cheer; mouthOpen(guy, T > 87.2 ? 0.55 + 0.4 * cheer + 0.1 * Math.sin(T * 20) * cheer : 0.25); brows(guy, 1, 0);
      if (cheer > 0) { u.armL.rotation.x = -0.4; u.armL.rotation.z = -2.3 * cheer; u.armL.userData.fore.rotation.x = -0.4; }
      guy.position.y += 0.06 * cheer * Math.abs(Math.sin(T * 9));
      guy.updateMatrixWorld(true); const hr = u.armR.userData.fore.localToWorld(V3(0, -0.33, 0.03));
      ph.position.copy(hr); ph.scale.setScalar(1.6); ph.rotation.set(0.1, 0.35 - 0.1 * look, 0);
      if (cheer > 0) ph.rotation.set(0, 0.25, 0.3 * Math.sin(T * 9));
      updateScreen(ph, [], {t: T, T, custom: rich, noDrops: true});
    }
    // ---- Kamera ----
    camera.fov = 50; scene.fog.near = 120; scene.fog.far = 1100;
    if (id === 'church') { const k = smooth(39, 48, T), up = smooth(39, 41, T), f = smooth(TILT, TOWER_HIT + 0.4, T);
      camera.position.set(lerp(10, 13, k), lerp(1.8, 2.3, k), lerp(14, 19, k)); camera.lookAt(lerp(0, -12, f), lerp(9, 17, up) - 12 * f, -9);
      const sh = T > TOWER_HIT && T < TOWER_HIT + 1.2 ? 0.25 * (1 - (T - TOWER_HIT) / 1.2) : 0; camera.position.x += noise1(T * 8, 1) * sh; camera.position.y += noise1(T * 8, 2) * sh; }
    else if (id === 'rain') { const k = smooth(48, 58, T), up = smooth(54.5, 57.5, T);
      camera.position.set(lerp(1.5, 0.5, k), 1.6, lerp(16, 13.5, k)); camera.lookAt(lerp(-1, 0, k), lerp(1.5, 1.5, k) + 14 * up, lerp(4, 2, k) - 4 * up); }
    else if (id === 'aerial') { const k = smooth(78, 84, T);
      camera.position.set(lerp(-160, -60, k), lerp(70, 150, k), lerp(160, 150, k)); camera.lookAt(lerp(40, 100, k), lerp(30, 40, k), lerp(-90, -150, k)); }
    else { const top = V3(120, 85 + 14 * 0.45, -150); const k = smooth(84, 90, T);
      camera.position.set(top.x + lerp(0.5, 0.8, k), top.y + lerp(0.3, 0.45, k), top.z + lerp(1.9, 2.4, k)); camera.lookAt(top.x, top.y + 0.2 + 0.45 * smooth(HEAD_UP, HEAD_UP + 0.6, T), top.z); }
    camera.updateProjectionMatrix();
  }};
}
