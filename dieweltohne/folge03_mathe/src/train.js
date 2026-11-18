// Eingleisige Strecke auf dem Land, Mittag. Das Stellwerk rechnet nicht mehr: beide Signale zeigen Grün, zwei Züge prallen frontal aufeinander.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, sparkSystem, updateSparks} from './lib.js';
import {skyMaterial} from './beach.js';
import {particles, updateParticles} from './fx.js';
import {TRAIN_HIT} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const SUN_DIR = V3(-0.3, 0.8, 0.45).normalize();
const L = 26, GAP = 0.9, NC = 5, V = 24; // Wagenlänge, Abstand, Wagen pro Zug, Geschwindigkeit m/s (~86 km/h)

// ICE-ähnlicher Wagen. dir = +1: Front zeigt nach +x. lead: Triebkopf mit Nase
function makeCar(lead, seed) {
  const g = new THREE.Group(); const body = new THREE.Group(); g.add(body);
  const white = mat('#eef0f2', {roughness: 0.35, metalness: 0.15}), red = mat('#c8102e', {roughness: 0.4}), glass = mat('#1d2630', {roughness: 0.08, metalness: 0.6}), dark = mat('#2a2c30', {roughness: 0.7}), grey = mat('#9aa0a6', {metalness: 0.6, roughness: 0.4});
  const len = lead ? L - 6 : L;
  // Wagenkasten (Mittelpunkt bei x=0, Front bei +L/2)
  const cx = lead ? -3 : 0;
  mesh(new THREE.BoxGeometry(len, 3.0, 2.9), white, cx, 2.35, 0, body).castShadow = true;
  { const rg = new THREE.CylinderGeometry(1.45, 1.45, len, 20, 1, false, 0, Math.PI); rg.rotateZ(Math.PI / 2); rg.rotateX(-Math.PI / 2); const r = mesh(rg, white, cx, 3.85, 0, body); r.scale.y = 0.25; r.castShadow = true; }
  mesh(new THREE.BoxGeometry(len - 0.4, 0.75, 2.94), glass, cx, 2.95, 0, body);           // Fensterband
  mesh(new THREE.BoxGeometry(len, 0.22, 2.94), red, cx, 1.7, 0, body);                    // roter Streifen
  for (let x = -len / 2 + 1.5; x < len / 2 - 1; x += 2.2) for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(0.12, 0.8, 0.02), white, cx + x, 2.95, s * 1.48, body); // Fensterstege
  mesh(new THREE.BoxGeometry(len, 0.4, 2.7), dark, cx, 0.75, 0, body);                     // Schürze
  for (const bx of [-len / 2 + 3, len / 2 - 3]) { const b = mesh(new THREE.BoxGeometry(3.2, 0.7, 2.2), dark, cx + bx, 0.55, 0, body); b.castShadow = true;
    for (const wx of [-0.9, 0.9]) for (const s of [-1, 1]) mesh(new THREE.CylinderGeometry(0.46, 0.46, 0.12, 14), grey, cx + bx + wx, 0.46, s * 0.75, body).rotation.x = Math.PI / 2; }
  // Dachaufbauten
  for (let k = 0; k < 3; k++) mesh(new THREE.BoxGeometry(2.4, 0.3, 1.4), mat('#c9ccd0'), cx - len / 3 + k * len / 3, 4.0, 0, body);
  if (seed % 2 === 0 || lead) { const pg = new THREE.Group(); pg.position.set(cx + (lead ? -6 : 5), 4.1, 0); body.add(pg);
    const a1 = mesh(new THREE.BoxGeometry(1.9, 0.06, 0.06), grey, 0.8, 0.55, 0, pg); a1.rotation.z = 0.55; const a2 = mesh(new THREE.BoxGeometry(1.9, 0.06, 0.06), grey, 0.8, 1.35, 0, pg); a2.rotation.z = -0.3;
    mesh(new THREE.BoxGeometry(0.25, 0.05, 1.8), grey, 1.6, 1.62, 0, pg); }
  if (lead) { // Nase: verjüngter Keil
    const ng = new THREE.BoxGeometry(6, 3.6, 2.9, 8, 4, 4); const p = ng.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i) + 3, u = x / 6; // 0..1 nach vorn
      const y = p.getY(i) + 1.8; const ny = y * (1 - 0.55 * u * u) - 0.0; p.setY(i, ny - 1.8 + 0.0); p.setZ(i, p.getZ(i) * (1 - 0.35 * u * u)); p.setX(i, x - 3); }
    ng.computeVertexNormals();
    const nose = mesh(ng, white, L / 2 - 3, 2.65, 0, body); nose.castShadow = true;
    const wg = new THREE.BoxGeometry(2.2, 0.9, 2.4); const ws = mesh(wg, glass, L / 2 - 3.6, 3.5, 0, body); ws.rotation.z = -0.5; // Frontscheibe
    mesh(new THREE.BoxGeometry(5.5, 0.22, 2.6), red, L / 2 - 3.1, 1.7, 0, body).scale.z = 0.95;
    for (const s of [-1, 1]) mesh(new THREE.SphereGeometry(0.16, 10, 8), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#fff8e0', emissiveIntensity: 2}), L / 2 - 0.5, 1.6, s * 0.75, body);
    body.userData.nose = nose;
  }
  g.userData = {body};
  return g;
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(1500, 48, 24), skyMaterial(SUN_DIR)); sky.renderOrder = -10; scene.add(sky);
  scene.fog = new THREE.Fog('#b9cde0', 180, 1400);
  scene.add(new THREE.HemisphereLight('#cfe1f5', '#6b6248', 1.0));
  const sun = new THREE.DirectionalLight('#fff3dc', 3.0); sun.position.copy(SUN_DIR).multiplyScalar(150); sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096); Object.assign(sun.shadow.camera, {left: -110, right: 110, top: 110, bottom: -110, near: 1, far: 400}); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.05;
  scene.add(sun, sun.target);
  { const e = new THREE.Scene(); e.background = new THREE.Color('#a9c6e6'); const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(e, 0.02).texture; scene.environmentIntensity = 0.5; }
  // Felder
  const fieldT = canvasTex(1024, 1024, (g, w, h) => { const r = rng(3); const cols = ['#7f9a3e', '#a8a24c', '#6e8a36', '#c9b45e', '#5f7d30', '#91a845'];
    for (let y = 0; y < h; y += 128) for (let x = 0; x < w; x += 170) { g.fillStyle = cols[Math.floor(r() * cols.length)]; g.fillRect(x, y, 170, 128);
      g.strokeStyle = 'rgba(0,0,0,0.07)'; for (let k = 0; k < 128; k += 5) { g.beginPath(); g.moveTo(x, y + k); g.lineTo(x + 170, y + k); g.stroke(); } }
    for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '40,50,20' : '220,210,150'},${r() * 0.08})`; g.fillRect(r() * w, r() * h, 3, 3); } });
  fieldT.wrapS = fieldT.wrapT = THREE.RepeatWrapping; fieldT.repeat.set(5, 5); fieldT.anisotropy = 8;
  const ground = mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshStandardMaterial({map: fieldT, roughness: 1}), 0, 0, 0, scene); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true;
  // Bahndamm: Schotter, Schwellen, Schienen
  const ballT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#7d756a'; g.fillRect(0, 0, w, h); const r = rng(6); for (let i = 0; i < 4000; i++) { const v = 70 + r() * 90; g.fillStyle = `rgb(${v},${v * 0.95},${v * 0.88})`; g.fillRect(r() * w, r() * h, 2 + r() * 3, 2 + r() * 3); } });
  ballT.wrapS = ballT.wrapT = THREE.RepeatWrapping; ballT.repeat.set(400, 2);
  const bed = new THREE.BoxGeometry(1600, 0.6, 5.5); { const p = bed.attributes.position; for (let i = 0; i < p.count; i++) if (p.getY(i) > 0) p.setZ(i, p.getZ(i) * 0.6); bed.computeVertexNormals(); }
  const ballast = mesh(bed, new THREE.MeshStandardMaterial({map: ballT, roughness: 1}), 0, 0.3, 0, scene); ballast.receiveShadow = true;
  const NS = 2400; const sleepers = new THREE.InstancedMesh(new THREE.BoxGeometry(0.26, 0.16, 2.6), mat('#8e8a83', {roughness: 0.9}), NS);
  const m4 = new THREE.Matrix4(); for (let i = 0; i < NS; i++) { m4.makeTranslation(-720 + i * 0.6, 0.66, 0); sleepers.setMatrixAt(i, m4); } sleepers.receiveShadow = true; scene.add(sleepers);
  for (const s of [-0.72, 0.72]) mesh(new THREE.BoxGeometry(1600, 0.16, 0.08), mat('#8d8f93', {metalness: 0.9, roughness: 0.3}), 0, 0.82, s, scene);
  // Oberleitung
  const mastM = mat('#7c8288', {metalness: 0.6, roughness: 0.5}); const masts = [];
  for (let x = -600; x <= 600; x += 55) { const g = new THREE.Group(); g.position.set(x, 0, -3.6); scene.add(g);
    mesh(new THREE.BoxGeometry(0.35, 8.2, 0.35), mastM, 0, 4.1, 0, g).castShadow = true; mesh(new THREE.BoxGeometry(0.12, 0.12, 4.2), mastM, 0, 7.4, 1.9, g); mesh(new THREE.BoxGeometry(0.1, 0.1, 3.8), mastM, 0, 6.3, 1.8, g).rotation.x = 0.28;
    masts.push(g); }
  const wireM = new THREE.LineBasicMaterial({color: '#3b3f44'});
  for (const y of [5.6, 6.9]) { const pts = []; for (let x = -600; x <= 600; x += 5) pts.push(V3(x, y - (y > 6 ? Math.pow(Math.sin(((x + 600) % 55) / 55 * Math.PI), 1) * 0.6 : 0), 0)); scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), wireM)); }
  // Signale (Ks): beide zeigen Grün
  const sigs = []; for (const [x, ry] of [[-38, 0], [42, Math.PI]]) { const g = new THREE.Group(); g.position.set(x, 0, ry ? -3.4 : 3.4); g.rotation.y = ry; g.scale.setScalar(1.4); scene.add(g);
    mesh(new THREE.CylinderGeometry(0.1, 0.12, 5, 8), mat('#5a5f66'), 0, 2.5, 0, g); mesh(new THREE.BoxGeometry(0.2, 1.4, 0.8), mat('#151515'), -0.12, 5.3, 0, g);
    mesh(new THREE.BoxGeometry(0.05, 0.4, 0.4), mat('#f2f2f2'), -0.1, 4.25, 0, g); // Mastschild
    const lamp = mesh(new THREE.SphereGeometry(0.15, 12, 8), new THREE.MeshStandardMaterial({color: '#111', emissive: '#3bdc6a', emissiveIntensity: 4}), -0.25, 5.5, 0, g); sigs.push(lamp); }
  // Stellwerk (Backstein) und Feldweg-Bahnübergang
  { const g = new THREE.Group(); g.position.set(60, 0, -22); scene.add(g); const brick = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#8f4a36'; c.fillRect(0, 0, w, h); c.strokeStyle = 'rgba(230,220,200,0.45)'; for (let y = 0; y < h; y += 10) { c.beginPath(); c.moveTo(0, y); c.lineTo(w, y); c.stroke(); for (let x = (y / 10) % 2 * 12; x < w; x += 24) { c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 10); c.stroke(); } } });
    mesh(new THREE.BoxGeometry(9, 7, 6), new THREE.MeshStandardMaterial({map: brick, roughness: 0.9}), 0, 3.5, 0, g).castShadow = true;
    mesh(new THREE.BoxGeometry(9.2, 1.4, 6.2), mat('#2a3138', {roughness: 0.2, metalness: 0.4}), 0, 5.6, 0, g);
    const roof = mesh(new THREE.ConeGeometry(6, 2.6, 4), mat('#5a2e24'), 0, 8.3, 0, g); roof.rotation.y = Math.PI / 4; roof.scale.set(1.15, 1, 0.8); }
  // Wald und Baumreihen
  const treeG = new THREE.IcosahedronGeometry(1, 1), trunkG = new THREE.CylinderGeometry(0.25, 0.35, 1, 6);
  const leaves = new THREE.InstancedMesh(treeG, mat('#3f5c2a', {flatShading: true, roughness: 0.9}), 1400), trunks = new THREE.InstancedMesh(trunkG, mat('#4a3a2c'), 1400);
  const rt = rng(19); let ti = 0; const q = new THREE.Quaternion();
  const addTree = (x, z, s) => { if (ti >= 1400) return; m4.compose(V3(x, s * 1.6, z), q, V3(s * 0.4, s * 3.2, s * 0.4)); trunks.setMatrixAt(ti, m4); m4.compose(V3(x, s * 4.2, z), q, V3(s * 1.9, s * 2.6, s * 1.9)); leaves.setMatrixAt(ti, m4); ti++; };
  for (let i = 0; i < 900; i++) { const x = -700 + rt() * 1400, z = -70 - rt() * 140 - Math.sin(x * 0.01) * 30; addTree(x, z, 2.2 + rt() * 1.6); }
  for (let i = 0; i < 300; i++) { const x = -700 + rt() * 1400, z = 140 + rt() * 200; addTree(x, z, 2 + rt() * 1.5); }
  for (let x = -400; x < 400; x += 14 + rt() * 10) addTree(x, -24 - rt() * 4, 1.6 + rt());
  leaves.count = trunks.count = ti; leaves.castShadow = trunks.castShadow = true; scene.add(leaves, trunks);
  // Hügel in der Ferne
  for (let i = 0; i < 14; i++) { const h = mesh(new THREE.SphereGeometry(1, 24, 12), mat('#6f8a55', {roughness: 1}), -900 + i * 140, -60, -700 - (i % 3) * 120, scene); h.scale.set(220, 140, 120); }
  // Windräder
  for (const [x, z] of [[-260, -420], [-160, -470], [180, -440]]) { const g = new THREE.Group(); g.position.set(x, 0, z); scene.add(g); mesh(new THREE.CylinderGeometry(1.4, 2.4, 100, 12), mat('#e2e4e6'), 0, 50, 0, g);
    const hub = new THREE.Group(); hub.position.set(0, 100, 3); g.add(hub); g.userData.hub = hub; for (let k = 0; k < 3; k++) { const pv = new THREE.Group(); pv.rotation.z = k * 2.094; hub.add(pv); mesh(new THREE.BoxGeometry(2.2, 48, 0.6), mat('#eceef0'), 0, 24, 0, pv); } masts.push(g); }
  const turbs = scene.children.filter(c => c.userData && c.userData.hub);

  // Züge: A kommt von -x (Front +x), B kommt von +x (Front -x)
  const trains = [0, 1].map(k => Array.from({length: NC}, (_, i) => { const c = makeCar(i === 0, i + k * 7); c.traverse(o => { if (o.isMesh) o.castShadow = true; }); scene.add(c); return c; }));
  // Effekte
  const sparks = sparkSystem(1600, 0.25); scene.add(sparks);
  const glass = sparkSystem(800, 0.12); scene.add(glass);
  const wireSparks = sparkSystem(500, 0.2); scene.add(wireSparks);
  const dust = particles(1800, 'smoke'); scene.add(dust);
  const flashL = new THREE.PointLight('#ffd9a0', 0, 60, 1.5); scene.add(flashL);
  const camera = new THREE.PerspectiveCamera(42, 1080 / 1920, 0.5, 4000);

  // Kette der Wagen nach dem Aufprall: Knickwinkel so gewählt, dass die Verkürzung dem Nachschieben entspricht
  const W = [[0.35, 1.0, 0.75, 0.45, 0.2], [0.55, 0.85, 0.6, 0.35, 0.15]];
  function chain(k, T) {
    const dir = k ? -1 : 1, t = T - TRAIN_HIT, out = [];
    if (t <= 0) { const f = -dir * V * (TRAIN_HIT - T) - dir * 0.3; for (let i = 0; i < NC; i++) out.push({x: f - dir * (L / 2 + i * (L + GAP)), z: 0, yaw: 0, y: 0, pitch: 0, roll: 0}); return out; }
    const kk = 0.85, D = V * (1 - Math.exp(-kk * t)) / kk;                 // so weit schiebt der Zug noch nach
    const crush = 4.5 * (1 - Math.exp(-6 * t));                             // Nasen werden zusammengedrückt
    const need = Math.max(0, D - crush);
    let lo = 0, hi = 1.3; for (let it = 0; it < 30; it++) { const m = (lo + hi) / 2; let s = 0; W[k].forEach(w => s += (L + GAP) * (1 - Math.cos(w * m))); if (s > need) hi = m; else lo = m; }
    const phi = lo;
    let fx = -dir * 0.3 + dir * crush * 0.4, fz = 0; // Front bleibt fast am Aufprallpunkt, Nasen schieben sich ineinander
    for (let i = 0; i < NC; i++) {
      const yaw = (i % 2 ? -1 : 1) * (k ? -1 : 1) * W[k][i] * phi;
      const hx = Math.cos(yaw) * dir, hz = Math.sin(yaw);
      const cxp = fx - hx * L / 2, czp = fz - hz * L / 2;
      const lift = i === 0 ? (k ? 1.8 : -0.2) * smooth(0, 0.6, t) : 0; // Triebkopf A steigt auf B auf
      out.push({x: cxp, z: czp, yaw: k ? Math.PI - yaw : yaw, y: lift + (i < 2 ? 0.25 * smooth(0, 1, t) : 0), pitch: i === 0 ? (k ? 0.12 : -0.05) * smooth(0, 0.6, t) : 0, roll: Math.min(0.35, Math.abs(yaw) * 0.6) * Math.sign(yaw) * smooth(0.2, 2.0, t) * (i % 2 ? 1 : -1)});
      fx = cxp - hx * (L / 2 + GAP); fz = czp - hz * (L / 2 + GAP);
    }
    return out;
  }

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.0;
    const t = T - shot.t0, tt = T - TRAIN_HIT;
    trains.forEach((cars, k) => { const ch = chain(k, T); cars.forEach((c, i) => { const s = ch[i];
      c.position.set(s.x, s.y, s.z); c.rotation.order = 'YXZ'; c.rotation.set(s.roll, -s.yaw, s.pitch);
      if (c.userData.body.userData.nose) c.userData.body.userData.nose.scale.x = 1 - 0.55 * smooth(0, 0.15, tt); }); });
    sigs.forEach(l => l.material.emissiveIntensity = 4);
    turbs.forEach((g, i) => g.userData.hub.rotation.z = T * 0.5 + i);
    // Aufprall: Funken, Glas, Staub, Fahrdraht
    const P = V3(0, 3.2, 0);
    updateSparks(sparks, [{pos: P, dir: V3(0, 0.8, 1), t0: TRAIN_HIT, t1: TRAIN_HIT + 0.35}, {pos: P, dir: V3(0, 0.8, -1), t0: TRAIN_HIT, t1: TRAIN_HIT + 0.35}, {pos: V3(0, 1, 0), dir: V3(0, 0.3, 1), t0: TRAIN_HIT + 0.1, t1: TRAIN_HIT + 1.6}], T);
    updateSparks(glass, [{pos: P.clone().add(V3(0, 0.6, 0)), dir: V3(0.2, 1, 0.8), t0: TRAIN_HIT, t1: TRAIN_HIT + 0.2}], T);
    { const C = glass.geometry.attributes.color.array; for (let i = 0; i < C.length; i += 3) { C[i + 1] = C[i]; C[i + 2] = C[i]; } glass.geometry.attributes.color.needsUpdate = true; }
    updateSparks(wireSparks, [{pos: V3(-3, 5.6, 0), dir: V3(0, -0.5, 0.3), t0: TRAIN_HIT + 0.15, t1: TRAIN_HIT + 2.2}, {pos: V3(4, 5.6, 0), dir: V3(0, -0.5, -0.3), t0: TRAIN_HIT + 0.4, t1: TRAIN_HIT + 1.5}], T);
    const src = [];
    if (tt > 0) {
      src.push({type: 'smoke', pos: V3(0, 2.0, 0), r: 9, t0: TRAIN_HIT, size: 11, rise: 2.2, col: [0.72, 0.64, 0.52], alpha: 0.6, share: 3});
      trains.forEach(cars => cars.slice(0, 4).forEach((c, i) => src.push({type: 'smoke', pos: V3(c.position.x, 0.8, c.position.z), r: 6, t0: TRAIN_HIT + 0.1 + i * 0.25, size: 6, rise: 1.0, col: [0.62, 0.55, 0.44], alpha: 0.5, share: 1})));
    }
    updateParticles(dust, src, T, V3(2.5, 0, 1.2));
    flashL.position.copy(P); flashL.intensity = tt > 0 && tt < 0.4 ? 3000 * (1 - tt / 0.4) : 0;
    // Kamera: hoch über dem Feld, die Strecke läuft schräg durchs Bild; fährt langsam heran
    const u = smooth(0, 7, t), sh = tt > 0 ? 0.35 * Math.exp(-tt * 3) : 0;
    camera.position.set(lerp(75, 52, u) + noise1(T * 13, 1) * sh, lerp(46, 26, u) + noise1(T * 13, 2) * sh, lerp(70, 44, u));
    camera.lookAt(lerp(-10, -2, u), lerp(-13, -7, u), lerp(-4, -2, u));
    camera.updateProjectionMatrix();
  }};
}
