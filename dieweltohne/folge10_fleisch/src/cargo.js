// Stufe 3: Ein vierstrahliger Frachtjet startet in der Abenddämmerung, beladen mit Kühlfleisch.
// Die Fracht ist weg, der Schwerpunkt verschoben: Beim Abheben schießt die Nase hoch, das Heck schleift funkensprühend über die Piste,
// die Maschine steigt viel zu steil, Überziehwarnung, die Nase kippt ab – knapp über dem Boden fängt sie sich.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, asphaltTex, skyDome, easeIn, easeOut, envMap, sparkSystem, updateSparks} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {ROTATE, TAILSTRIKE, STALL} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

function makeJet() {
  const g = new THREE.Group();          // Ursprung: Aufstandspunkt des Hauptfahrwerks
  const body = new THREE.Group(); g.add(body);
  const white = mat('#e9ecef', {roughness: 0.45, metalness: 0.2}), grey = mat('#9aa1a8', {roughness: 0.5, metalness: 0.4}), dark = mat('#2a2e33', {roughness: 0.6}), blue = mat('#1f4e8c', {roughness: 0.5});
  const Y = 4.6; // Rumpfmitte über dem Boden
  const fus = mesh(new THREE.CylinderGeometry(3.2, 3.2, 46, 24), white, 4, Y, 0, body); fus.rotation.z = Math.PI / 2;
  const nose = mesh(new THREE.SphereGeometry(3.2, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), white, 27, Y, 0, body); nose.rotation.z = -Math.PI / 2; nose.scale.set(1, 2.0, 1);
  const hump = mesh(new THREE.CapsuleGeometry(1.9, 10, 6, 16), white, 22, Y + 2.6, 0, body); hump.rotation.z = Math.PI / 2; // Oberdeck
  const tail = mesh(new THREE.CylinderGeometry(3.2, 0.7, 16, 24), white, -27, Y + 0.9, 0, body); tail.rotation.z = Math.PI / 2 - 0.11;
  mesh(new THREE.BoxGeometry(46, 0.5, 6.42), blue, 4, Y - 0.6, 0, body); // Zierstreifen
  // Cockpitfenster
  for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(1.6, 0.5, 0.2), dark, 31.0, Y + 1.5, s * 1.0, body).rotation.y = s * 0.5;
  // Flügel (gepfeilt), Triebwerke
  for (const s of [-1, 1]) {
    const w = new THREE.Shape(); w.moveTo(0, 0); w.lineTo(-14, s * 30); w.lineTo(-18.5, s * 30); w.lineTo(-11, 0); w.closePath();
    const wg = new THREE.ExtrudeGeometry(w, {depth: 0.6, bevelEnabled: false}); wg.rotateX(Math.PI / 2);
    const wing = mesh(wg, grey, 10, Y - 1.4, 0, body);
    for (const d of [10, 20]) { const ex = 10 - d * 14 / 30 - 2, ez = s * d;
      const eng = mesh(new THREE.CylinderGeometry(1.25, 1.1, 5.2, 18), white, ex, Y - 3.1, ez, body); eng.rotation.z = Math.PI / 2;
      mesh(new THREE.CircleGeometry(1.05, 18), dark, ex + 2.61, Y - 3.1, ez, body).rotation.y = Math.PI / 2;
      mesh(new THREE.BoxGeometry(3, 1.2, 0.3), grey, ex + 0.5, Y - 2.1, ez, body); }
  }
  // Leitwerk
  const fin = new THREE.Shape(); fin.moveTo(0, 0); fin.lineTo(-7, 11); fin.lineTo(-11, 11); fin.lineTo(-10, 0); fin.closePath();
  const fg = new THREE.ExtrudeGeometry(fin, {depth: 0.5, bevelEnabled: false}); mesh(fg, blue, -24, Y + 2.2, -0.25, body);
  for (const s of [-1, 1]) { const hs = new THREE.Shape(); hs.moveTo(0, 0); hs.lineTo(-5, s * 11); hs.lineTo(-8, s * 11); hs.lineTo(-7, 0); hs.closePath();
    const hg = new THREE.ExtrudeGeometry(hs, {depth: 0.4, bevelEnabled: false}); hg.rotateX(Math.PI / 2); mesh(hg, grey, -26, Y + 1.6, 0, body); }
  // Fahrwerk
  const gear = new THREE.Group(); body.add(gear);
  for (const [x, z] of [[0, -2.2], [0, 2.2], [-2.5, -1.2], [-2.5, 1.2], [28, 0]]) { mesh(new THREE.CylinderGeometry(0.18, 0.18, Y - 1.6, 8), grey, x, (Y - 1.6) / 2 + 0.7, z, gear);
    for (const dz of [-0.45, 0.45]) mesh(new THREE.CylinderGeometry(0.7, 0.7, 0.5, 16), dark, x, 0.7, z + dz, gear).rotation.x = Math.PI / 2; }
  // Lichter
  const strobeM = new THREE.MeshBasicMaterial({color: '#ffffff'}), redM = new THREE.MeshBasicMaterial({color: '#ff2a2a'}), greenM = new THREE.MeshBasicMaterial({color: '#2aff6a'});
  const strobes = [mesh(new THREE.SphereGeometry(0.25, 8, 6), strobeM, -4.5, Y - 1.4, -30, body), mesh(new THREE.SphereGeometry(0.25, 8, 6), strobeM, -4.5, Y - 1.4, 30, body)];
  mesh(new THREE.SphereGeometry(0.22, 8, 6), redM, -4.4, Y - 1.4, -30.2, body); mesh(new THREE.SphereGeometry(0.22, 8, 6), greenM, -4.4, Y - 1.4, 30.2, body);
  const beacon = mesh(new THREE.SphereGeometry(0.3, 8, 6), redM, 6, Y + 3.3, 0, body);
  const landL = new THREE.SpotLight('#fff6e0', 120, 300, 0.25, 0.5, 1.2); landL.position.set(26, Y - 2, 0); landL.target.position.set(80, -8, 0); body.add(landL, landL.target);
  g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  g.userData = {body, gear, strobes, beacon, tailPt: V3(-34, Y - 1.8, 0)};
  return g;
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.35;
  scene.fog = new THREE.Fog('#4a4f6a', 300, 2600);
  scene.add(skyDome('#141a3a', '#6a5a86', '#f09a62', 3000));
  const hemi = new THREE.HemisphereLight('#a8b0d8', '#2a2a30', 0.7); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#ffb27a', 1.6); sun.position.set(-400, 120, 200); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -80, right: 80, top: 80, bottom: -80, near: 1, far: 1500}); sun.shadow.bias = -0.0005; scene.add(sun, sun.target);
  // Gras, Piste mit Markierungen und Randbefeuerung
  mesh(new THREE.PlaneGeometry(8000, 8000), mat('#3d4a2e', {roughness: 1}), 0, -0.05, 0, scene).rotation.x = -Math.PI / 2;
  const asT = asphaltTex(); asT.repeat.set(120, 3);
  const rw = mesh(new THREE.PlaneGeometry(4000, 60), new THREE.MeshStandardMaterial({map: asT, roughness: 0.9, color: '#9a9a9a'}), 800, 0, 0, scene); rw.rotation.x = -Math.PI / 2; rw.castShadow = false;
  const lineM = new THREE.MeshStandardMaterial({color: '#f0f0ea', roughness: 0.8, polygonOffset: true, polygonOffsetFactor: -1});
  for (let x = -1000; x < 2800; x += 50) { const l = mesh(new THREE.PlaneGeometry(30, 0.9), lineM, x, 0.01, 0, scene); l.rotation.x = -Math.PI / 2; l.castShadow = false; }
  for (const z of [-28, 28]) { const l = mesh(new THREE.PlaneGeometry(3800, 0.9), lineM, 800, 0.01, z, scene); l.rotation.x = -Math.PI / 2; l.castShadow = false; }
  const NL = 160, edge = new THREE.InstancedMesh(new THREE.SphereGeometry(0.35, 6, 4), new THREE.MeshBasicMaterial({color: '#fff1c8'}), NL * 2); const m4 = new THREE.Matrix4();
  for (let i = 0; i < NL; i++) for (const [k, z] of [[0, -31], [1, 31]]) { m4.makeTranslation(-1000 + i * 25, 0.4, z); edge.setMatrixAt(i * 2 + k, m4); } scene.add(edge);
  // Terminal und Hangars in der Ferne, mit Lichtern
  const r = rng(12); const winT = canvasTex(256, 64, (g, w, h) => { g.fillStyle = '#2a2c34'; g.fillRect(0, 0, w, h); for (let i = 0; i < 40; i++) { g.fillStyle = r() < 0.7 ? '#ffd79a' : '#3a3e48'; g.fillRect(4 + i * 6.3, 20, 4, 18); } });
  for (let i = 0; i < 8; i++) mesh(new THREE.BoxGeometry(120, 18 + r() * 10, 40), new THREE.MeshStandardMaterial({map: winT, roughness: 0.8, emissive: '#ffffff', emissiveMap: winT, emissiveIntensity: 0.5}), -600 + i * 160, 12, -260 - r() * 60, scene);
  for (let i = 0; i < 3; i++) mesh(new THREE.CylinderGeometry(4, 6, 60, 10), mat('#7a7e88'), -300 + i * 900, 30, -330, scene);
  // Jet
  const jet = makeJet(); scene.add(jet);
  const sparks = sparkSystem(1400, 0.6); scene.add(sparks);
  const smoke = particles(500, 'smoke'); scene.add(smoke);
  const heat = particles(300, 'smoke'); scene.add(heat);
  const camera = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.5, 6000); scene.add(camera);

  // Flugbahn: x(T), Höhe, Nickwinkel
  const X0 = -230, V = 70;
  const state = T => {
    const x = X0 + V * (T - 24) + 1.2 * Math.max(0, T - 24) ** 2;
    const rot = smooth(ROTATE, ROTATE + 0.55, T);                        // Nase schießt hoch
    const lift = clamp((T - (TAILSTRIKE + 0.5)) / 3.0);
    let pitch = 0.27 * rot; let y = 0;
    if (T > TAILSTRIKE + 0.5) { y = 60 * easeIn(clamp((T - TAILSTRIKE - 0.5) / 2.0)) * (T < STALL + 0.4 ? 1 : 1) ; pitch = lerp(0.27, 0.42, smooth(TAILSTRIKE + 0.5, STALL, T)); }
    const drop = smooth(STALL + 0.3, STALL + 1.3, T), recover = smooth(STALL + 1.6, 30.6, T);
    if (T > STALL + 0.3) { pitch = lerp(lerp(0.42, -0.16, drop), 0.06, recover); y = 60 * Math.min(1, easeIn(clamp((T - TAILSTRIKE - 0.5) / 2.0))) - 34 * smooth(STALL + 0.4, STALL + 2.2, T) + 18 * recover; }
    return {x, y: Math.max(0, y), pitch, lift};
  };

  return {scene, camera, update(shot, T) {
    const s = state(T);
    jet.position.set(s.x, s.y, 0); jet.rotation.set(0, 0, s.pitch);
    const u = jet.userData; u.gear.visible = true;
    u.strobes.forEach(m => m.visible = (T * 1.1) % 1 < 0.08); u.beacon.visible = (T * 1.3) % 1 < 0.5;
    // Funken am Heck, solange es über die Piste schleift
    const scrape = T > TAILSTRIKE && T < TAILSTRIKE + 0.75;
    updateSparks(sparks, [{pos: born => { const sb = state(born); return V3(sb.x - 34 * Math.cos(sb.pitch), 0.3, 0); }, dir: V3(-1, 0.6, 0), t0: TAILSTRIKE, t1: TAILSTRIKE + 0.75}], T, 9.8);
    updateParticles(smoke, T > TAILSTRIKE ? [{type: 'smoke', pos: V3(state(TAILSTRIKE + 0.2).x - 34, 0.5, 0), r: 6, t0: TAILSTRIKE, t1: TAILSTRIKE + 0.8, size: 6, rise: 1.2, col: [0.55, 0.55, 0.58], alpha: 0.5, share: 1}] : [], T, V3(-4, 0, 1));
    // Kamera: 24–27.8 an der Pistenkante, schwenkt mit; danach Blick von hinten auf den steilen Steigflug
    if (T < 27.8) {
      camera.position.set(-50 + noise1(T, 3) * 0.3, 2.2, 62); const look = V3(s.x - 6, s.y + 6, 0); camera.lookAt(look);
      camera.fov = lerp(34, 40, smooth(24, 26.5, T));
    } else {
      const k = smooth(27.8, 31, T);
      camera.position.set(s.x - 160 + noise1(T, 2) * 0.6, 14 + s.y * 0.35, 90); camera.lookAt(s.x + 10, s.y * 0.9 + 4, 0); camera.fov = 34;
    }
    if (scrape) { camera.position.y += Math.sin(T * 70) * 0.08; }
    camera.updateProjectionMatrix();
  }};
}
