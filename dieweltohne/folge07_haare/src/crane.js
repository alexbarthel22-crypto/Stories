// Baustelle in der Abenddämmerung. Turmdrehkran, 80 m hoch, 12 t Stahlträger am Haken.
// Der Kranführer verliert das Gleichgewicht und fällt auf den Steuerhebel: Der Kran dreht durch, die Last pendelt in die
// Glasfassade des Nachbarhochhauses, dann knickt der Ausleger ab und der Kran stürzt auf die Straße.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, skyDome, easeIn, makeCar, envMap} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {SWING, CRANE_HIT, CRANE_FALL} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const MH = 80; // Masthöhe

function latticeTex(c) { return canvasTex(64, 256, (g, w, h) => { g.clearRect(0, 0, w, h); g.strokeStyle = c; g.lineWidth = 5; g.strokeRect(3, 0, w - 6, h);
  for (let y = 0; y < h; y += 64) { g.beginPath(); g.moveTo(3, y); g.lineTo(w - 3, y + 32); g.lineTo(3, y + 64); g.stroke(); g.beginPath(); g.moveTo(3, y); g.lineTo(w - 3, y); g.stroke(); } }); }

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.25;
  scene.fog = new THREE.Fog('#2c3048', 120, 700);
  scene.add(skyDome('#0e1430', '#3a3d6a', '#d0806a', 900));
  scene.add(new THREE.HemisphereLight('#7f86b8', '#201a22', 0.8));
  const moon = new THREE.DirectionalLight('#ffb48a', 1.4); moon.position.set(-80, 40, -120); moon.target.position.set(0, 30, 0);
  moon.castShadow = true; moon.shadow.mapSize.set(2048, 2048); Object.assign(moon.shadow.camera, {left: -90, right: 90, top: 90, bottom: -90, near: 1, far: 400}); moon.shadow.bias = -0.0006; moon.shadow.normalBias = 0.05;
  scene.add(moon, moon.target);
  const flood = new THREE.SpotLight('#fff1d0', 2500, 160, 0.5, 0.5, 1.5); flood.position.set(20, 30, 40); flood.target.position.set(0, 30, 0); scene.add(flood, flood.target);

  const ground = mesh(new THREE.PlaneGeometry(1200, 1200), mat('#2a2b2e', {roughness: 0.95}), 0, 0, 0, scene); ground.rotation.x = -Math.PI / 2;
  // Straße vorne
  const road = mesh(new THREE.PlaneGeometry(400, 16), mat('#202125', {roughness: 0.8}), 0, 0.02, 40, scene); road.rotation.x = -Math.PI / 2;
  for (let x = -190; x < 190; x += 8) mesh(new THREE.PlaneGeometry(3, 0.2), new THREE.MeshBasicMaterial({color: '#bdbdb0'}), x, 0.03, 40, scene).rotation.x = -Math.PI / 2;
  // Skyline mit Lichtern
  const r = rng(8);
  for (let i = 0; i < 90; i++) { const a = Math.PI * (1.05 + r() * 0.9), d = 160 + r() * 380, w = 14 + r() * 24, h = 30 + r() * 120; // nur hinter dem Kran
    const ft = facadeTex(['#3a3f50', '#2e3444', '#454a5c'][i % 3], i, Math.round(h / 4), 5);
    mesh(new THREE.BoxGeometry(w, h, w), new THREE.MeshStandardMaterial({map: ft, emissive: '#ffffff', emissiveMap: ft, emissiveIntensity: 0.55, roughness: 0.8}), Math.cos(a) * d, h / 2, Math.sin(a) * d - 60, scene); }
  // Rohbau (Hochhaus im Bau) rechts vom Kran
  const conc = mat('#8e8b86', {roughness: 0.95});
  const shell = new THREE.Group(); shell.position.set(26, 0, -10); scene.add(shell);
  for (let f = 0; f < 18; f++) { mesh(new THREE.BoxGeometry(26, 0.4, 22), conc, 0, f * 3.6 + 3.6, 0, shell);
    for (const [x, z] of [[-12, -10], [12, -10], [-12, 10], [12, 10], [0, -10], [0, 10], [-12, 0], [12, 0]]) mesh(new THREE.BoxGeometry(0.6, 3.6, 0.6), conc, x, f * 3.6 + 1.8, z, shell); }
  mesh(new THREE.BoxGeometry(7, 70, 7), conc, 0, 35, 0, shell);
  // Glasturm links (wird getroffen)
  const glassT = canvasTex(256, 1024, (g, w, h) => { g.fillStyle = '#1a2a40'; g.fillRect(0, 0, w, h); const rr = rng(3);
    for (let y = 0; y < h; y += 16) for (let x = 0; x < w; x += 32) { const lit = rr() < 0.4; g.fillStyle = lit ? `rgba(255,${200 + rr() * 40},${140 + rr() * 60},0.95)` : `rgba(60,90,130,${0.4 + rr() * 0.3})`; g.fillRect(x + 2, y + 2, 28, 12); } });
  const tower = mesh(new THREE.BoxGeometry(36.5, 62, 40), new THREE.MeshStandardMaterial({map: glassT, emissive: '#ffffff', emissiveMap: glassT, emissiveIntensity: 0.6, metalness: 0.6, roughness: 0.15}), -51.75, 31, -10, scene);
  const hole = mesh(new THREE.CircleGeometry(4.5, 20), new THREE.MeshBasicMaterial({color: '#05060a'}), -33.4, 44, -2, scene); hole.rotation.y = Math.PI / 2; hole.visible = false;
  // Bauzaun, Container, Autos
  for (let x = -30; x < 50; x += 3.2) mesh(new THREE.BoxGeometry(3.0, 2, 0.06), mat('#c9c2b0'), x, 1, 30, scene);
  [[10, 22, 0], [16, 22, 0]].forEach(([x, z]) => mesh(new THREE.BoxGeometry(6, 2.6, 2.4), mat('#c85a2a'), x, 1.3, z, scene));
  const cars = [[-20, 37, 1], [-6, 43, 3], [8, 37, 2], [30, 43, 5], [44, 37, 4]].map(([x, z, s], i) => { const c = makeCar(s); c.position.set(x, 0, z); c.rotation.y = i % 2 ? -Math.PI / 2 : Math.PI / 2; scene.add(c); return c; });

  // Kran
  const yellow = new THREE.MeshStandardMaterial({map: latticeTex('#f2b51c'), transparent: true, alphaTest: 0.3, side: THREE.DoubleSide, roughness: 0.6, metalness: 0.3});
  const crane = new THREE.Group(); scene.add(crane); // Drehpunkt am Mastfuß (für den Sturz)
  mesh(new THREE.BoxGeometry(8, 1.5, 8), conc, 0, 0.75, 0, scene);
  const mast = new THREE.Mesh(new THREE.BoxGeometry(2.2, MH, 2.2), yellow); mast.position.y = MH / 2; crane.add(mast);
  const top = new THREE.Group(); top.position.y = MH; crane.add(top); // dreht sich (Schwenkwerk)
  const jibT = yellow.clone(); jibT.map = latticeTex('#f2b51c'); jibT.map.wrapS = THREE.RepeatWrapping; jibT.map.repeat.set(1, 1);
  const jib = new THREE.Mesh(new THREE.BoxGeometry(60, 2.0, 2.0), yellow); jib.position.set(30, 1.5, 0); top.add(jib);
  const cjib = new THREE.Mesh(new THREE.BoxGeometry(18, 1.6, 2.6), yellow); cjib.position.set(-9, 1.4, 0); top.add(cjib);
  for (let k = 0; k < 4; k++) mesh(new THREE.BoxGeometry(1.6, 3, 2.4), conc, -14 - k * 1.7, 0, 0, top);
  const apex = new THREE.Mesh(new THREE.BoxGeometry(1.6, 9, 1.6), yellow); apex.position.set(0, 6, 0); top.add(apex);
  const tieM = new THREE.LineBasicMaterial({color: '#888'});
  top.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([V3(58, 2.4, 0), V3(0, 10.5, 0), V3(-17, 1.6, 0)]), tieM));
  const cab = mesh(new RoundedBoxGeometry(2.6, 2.6, 2.4, 2, 0.15), mat('#e8e6e0'), 2.6, -0.9, 1.8, top);
  const cabWin = mesh(new THREE.PlaneGeometry(2.2, 1.6), new THREE.MeshStandardMaterial({color: '#ffe8b0', emissive: '#ffcf80', emissiveIntensity: 1.2}), 3.92, -0.6, 1.8, top); cabWin.rotation.y = Math.PI / 2;
  const opr = mesh(new THREE.SphereGeometry(0.28, 12, 10), mat('#202020'), 3.3, -0.3, 1.8, top); // Silhouette Kopf
  const oprB = mesh(new THREE.CapsuleGeometry(0.35, 0.6, 4, 8), mat('#202020'), 3.3, -1.2, 1.8, top);
  const warn = mesh(new THREE.SphereGeometry(0.4, 10, 8), new THREE.MeshBasicMaterial({color: '#ff2a1a'}), 0, 10.6, 0, top);
  const warn2 = mesh(new THREE.SphereGeometry(0.4, 10, 8), new THREE.MeshBasicMaterial({color: '#ff2a1a'}), 59.5, 2.6, 0, top);
  // Laufkatze, Seil, Last (Pendel)
  const trolley = mesh(new THREE.BoxGeometry(2.2, 0.8, 2.4), mat('#333'), 42, 0.1, 0, top);
  const ropeGeo = new THREE.BufferGeometry().setFromPoints([V3(0, 0, 0), V3(0, -1, 0)]); const rope = new THREE.Line(ropeGeo, new THREE.LineBasicMaterial({color: '#cfcfcf'})); scene.add(rope);
  const load = new THREE.Group(); scene.add(load);
  for (let k = 0; k < 5; k++) mesh(new THREE.BoxGeometry(12, 0.5, 0.35), mat('#6a4a3a', {metalness: 0.6, roughness: 0.5}), 0, -2.2 - (k % 2) * 0.5, (k - 2) * 0.4, load);
  mesh(new THREE.BoxGeometry(0.8, 0.8, 0.8), mat('#e2b21c'), 0, -0.4, 0, load);
  const RL = 36; // Seillänge
  // Glassplitter, Staub, Funken
  const NS = 900, shards = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.5, 0.7), new THREE.MeshStandardMaterial({color: '#bcd8f0', metalness: 0.9, roughness: 0.05, side: THREE.DoubleSide, emissive: '#3a5070', emissiveIntensity: 0.4}), NS); shards.frustumCulled = false; scene.add(shards);
  const rs = rng(4), SH = []; for (let i = 0; i < NS; i++) SH.push({vx: 2 + rs() * 9, vy: (rs() - 0.3) * 8, vz: (rs() - 0.5) * 10, s: rs() * 9, ox: (rs() - 0.5) * 6, oy: (rs() - 0.5) * 6});
  const dust = particles(700, 'smoke'); scene.add(dust);
  const fire = particles(300, 'flame'); scene.add(fire);
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = V3(0, 0, 0), S1 = V3(1, 1, 1), Z = new THREE.Matrix4().makeScale(0, 0, 0);

  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.5, 2000);
  // Schwenkwinkel und Pendel (vorberechnet, deterministisch)
  const DT = 1 / 120, sim = []; { let ang = 1.86, w = 0.04, th = 0, om = 0, ph = 0, pom = 0;
    for (let T = 46; T <= 56.01; T += DT) {
      const drive = T > SWING ? 0.32 : 0.04; w += (drive - w) * DT * (T > SWING ? 0.9 : 3); ang += w * DT;
      // Pendel in Schwenkrichtung (tangential) angeregt durch Winkelbeschleunigung
      const acc = (T > SWING ? 0.9 * (0.32 - w) : 0) * 42; om += (-9.8 / RL * Math.sin(th) - acc / RL - 0.02 * om) * DT; th += om * DT;
      pom += (-9.8 / RL * Math.sin(ph) + (w * w * 42) / RL * Math.cos(ph) * 0.5 - 0.02 * pom) * DT; ph += pom * DT; // nach außen getragen
      sim.push([ang, th, ph]); } }
  const at = T => sim[Math.max(0, Math.min(sim.length - 1, Math.round((T - 46) / DT)))];

  let hitPos = null;
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    let [ang, th, ph] = at(Math.min(T, CRANE_HIT));
    if (T > CRANE_HIT) { const d = T - CRANE_HIT; ang += 0.05 * (1 - Math.exp(-d * 4)); th *= Math.exp(-d * 3); }
    // Kran kippt ab CRANE_FALL nach vorne (Richtung Straße, +z)
    const fall = easeIn(clamp((T - CRANE_FALL) / 2.6));
    crane.rotation.set(fall * 1.45, 0, fall * 0.12);
    top.rotation.set(0, ang, 0);
    jib.rotation.z = -fall * 0.35; // Ausleger knickt
    // Bediener sackt zusammen
    const slump = smooth(SWING - 0.6, SWING, T); opr.position.set(3.3 - slump * 0.3, -0.3 - slump * 0.9, 1.8); oprB.rotation.z = slump * 0.9;
    warn.visible = warn2.visible = Math.sin(T * 5) > 0;
    // Last am Seil
    crane.updateMatrixWorld(true);
    const tw = trolley.getWorldPosition(V3(0, 0, 0));
    const tang = V3(-Math.sin(ang), 0, -Math.cos(ang)).applyAxisAngle(V3(0, 1, 0), 0); // tangential zur Schwenkrichtung
    const radial = V3(Math.cos(ang), 0, -Math.sin(ang));
    let lp = tw.clone().add(V3(0, -RL * Math.cos(th) * Math.cos(ph), 0)).add(tang.clone().multiplyScalar(RL * Math.sin(th))).add(radial.clone().multiplyScalar(RL * Math.sin(ph)));
    if (lp.z > -30 && lp.z < 10 && lp.y < 62) lp.x = Math.max(lp.x, -32.8);
    if (!hitPos && T >= CRANE_HIT) { hitPos = lp.clone(); hitPos.x = -33.4; hole.position.set(-33.45, hitPos.y, hitPos.z); }
    if (fall > 0) { const d = T - CRANE_FALL; lp.y = Math.max(1.5, lp.y - 4.9 * d * d * 0.6); }
    load.position.copy(lp); load.rotation.set(0, -ang + th * 0.5, th * 0.3);
    const pa = rope.geometry.attributes.position; pa.setXYZ(0, tw.x, tw.y, tw.z); pa.setXYZ(1, lp.x, lp.y, lp.z); pa.needsUpdate = true;
    // Treffer in der Glasfassade
    hole.visible = T > CRANE_HIT; const hp = hitPos || V3(-33.4, 44, -20);
    for (let i = 0; i < NS; i++) { const s = SH[i], d = T - CRANE_HIT; if (d < 0) { shards.setMatrixAt(i, Z); continue; }
      const y = hp.y + s.oy + s.vy * d - 4.9 * d * d; if (y < 0.05) { M.compose(P.set(hp.x + s.vx * Math.min(d, 3) + 0, 0.05, hp.z + s.vz * Math.min(d, 3)), Q.setFromEuler(E.set(-Math.PI / 2, 0, s.s)), S1.set(1, 1, 1)); shards.setMatrixAt(i, M); continue; }
      M.compose(P.set(hp.x + s.vx * d, y, hp.z + s.vz * d), Q.setFromEuler(E.set(d * s.s, d * s.s * 0.7, s.s)), S1.set(1, 1, 1)); shards.setMatrixAt(i, M); }
    shards.instanceMatrix.needsUpdate = true;
    // Staub und Feuer beim Aufschlag
    const land = CRANE_FALL + 2.6;
    updateParticles(dust, [
      ...(T > CRANE_HIT ? [{type: 'burstSmoke', pos: hp, r: 8, t0: CRANE_HIT, size: 7, rise: 1, share: 0.3}] : []),
      ...(T > land ? [{type: 'burstSmoke', pos: V3(5, 2, 62), r: 30, t0: land, size: 16, rise: 2, share: 0.7}] : [])], T, V3(1, 0, 0.5));
    updateParticles(fire, T > land ? [{type: 'burst', pos: V3(0, 2, 55), r: 10, t0: land, size: 6, power: 1.2, share: 1}] : [], T);
    // Kamera: Straße gegenüber, Teleblick nach oben; schwenkt mit dem Sturz
    camera.fov = 46;
    const sh = smooth(land, land + 0.15, T) * (1 - smooth(land + 1.0, land + 2.2, T)) + smooth(CRANE_HIT, CRANE_HIT + 0.1, T) * (1 - smooth(CRANE_HIT + 0.4, CRANE_HIT + 0.9, T)) * 0.4;
    camera.position.set(30 - t * 0.6 + noise1(T * 13, 1) * 0.5 * sh, 3.5 + noise1(T * 11, 2) * 0.4 * sh, 125 - t * 1.2);
    const lk = V3(lerp(-6, 0, smooth(CRANE_FALL, land, T)), lerp(52, 18, smooth(CRANE_FALL + 0.4, land + 0.5, T)), lerp(-4, 20, smooth(CRANE_FALL, land, T)));
    camera.lookAt(lk);
    camera.updateProjectionMatrix();
  }};
}
