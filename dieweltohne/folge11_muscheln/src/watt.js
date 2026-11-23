// Stufe 4: Wattwanderung. Die Gruppe steht auf einer Miesmuschelbank – dem einzigen festen Boden weit und breit.
// Die Bank verschwindet, alle plumpsen in den Schlick und versinken bis zum Bauch. Eine Möwe landet auf dem Kopf
// des Wattführers, von hinten kommt die Flut, ganz hinten ein Rettungshubschrauber.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, skyDome, easeOut, easeIn, makePerson, posePerson, envMap} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {addMouth, mouthOpen, brows} from './people.js';
import {shellSwarm, heapTex} from './shells.js';
import {SINK} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.6;
  scene.add(skyDome('#7d9cc4', '#c3d3e2', '#eef1f2', 600));
  scene.fog = new THREE.Fog('#dfe6ea', 40, 420);
  const hemi = new THREE.HemisphereLight('#eef4ff', '#5a5448', 0.9); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff3e0', 2.2); sun.position.set(-8, 12, 6); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 40}); sun.shadow.bias = -0.0004; scene.add(sun, sun.target);
  // Schlick: nasser, glänzender Boden mit Rippeln und Prielen
  const mudT = canvasTex(1024, 1024, (g, w, h) => { const r = rng(6); g.fillStyle = '#5e574c'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += 6) { g.strokeStyle = `rgba(${r() < 0.5 ? '40,36,30' : '120,112,100'},${0.15 + r() * 0.2})`; g.lineWidth = 2; g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= w; x += 32) g.lineTo(x, y + Math.sin(x * 0.05 + y * 0.3) * 3); g.stroke(); }
    for (let i = 0; i < 40; i++) { g.fillStyle = 'rgba(160,175,190,0.25)'; g.beginPath(); g.ellipse(r() * w, r() * h, 20 + r() * 90, 8 + r() * 30, r() * 3, 0, 7); g.fill(); }
    for (let i = 0; i < 900; i++) { g.fillStyle = 'rgba(30,26,20,0.5)'; g.beginPath(); g.arc(r() * w, r() * h, 1 + r() * 2, 0, 7); g.fill(); } });
  mudT.wrapS = mudT.wrapT = THREE.RepeatWrapping; mudT.repeat.set(40, 40);
  const mud = mesh(new THREE.PlaneGeometry(800, 800), new THREE.MeshStandardMaterial({map: mudT, roughness: 0.28, metalness: 0.05, color: '#bdb6aa'}), 0, 0, 0, scene); mud.rotation.x = -Math.PI / 2;
  // Fernes Meer am Horizont und die Flut, die von hinten kommt
  const seaM = new THREE.MeshStandardMaterial({color: '#6f8fa8', roughness: 0.15, metalness: 0.2, transparent: true, opacity: 0.92});
  const sea = mesh(new THREE.PlaneGeometry(900, 400), seaM, 0, 0.02, -420, scene); sea.rotation.x = -Math.PI / 2;
  const tide = new THREE.Group(); scene.add(tide);
  const tideW = mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshStandardMaterial({color: '#7f9db2', roughness: 0.1, metalness: 0.25, transparent: true, opacity: 0.8}), 0, 0, -100, tide); tideW.rotation.x = -Math.PI / 2;
  const foamT = canvasTex(512, 32, (g, w, h) => { const r = rng(3); for (let i = 0; i < 300; i++) { g.fillStyle = `rgba(255,255,255,${0.3 + r() * 0.6})`; g.beginPath(); g.ellipse(r() * w, h / 2 + (r() - 0.5) * 14, 3 + r() * 10, 2 + r() * 4, 0, 0, 7); g.fill(); } });
  foamT.wrapS = THREE.RepeatWrapping; foamT.repeat.set(40, 1);
  const foam = mesh(new THREE.PlaneGeometry(200, 0.8), new THREE.MeshBasicMaterial({map: foamT, transparent: true, depthWrite: false}), 0, 0.005, 0, tide); foam.rotation.x = -Math.PI / 2;
  // Pricken (Wegmarkierung: Birkenzweige im Watt)
  { const r = rng(8); for (let i = 0; i < 16; i++) { const z = -6 - i * 9, x = -3 + Math.sin(i * 0.7) * 4; const st = mesh(new THREE.CylinderGeometry(0.03, 0.04, 2.2, 5), mat('#4a3a2a'), x, 1.0, z, scene); st.rotation.z = (r() - 0.5) * 0.2;
      for (let k = 0; k < 4; k++) { const b = mesh(new THREE.CylinderGeometry(0.005, 0.012, 0.6, 4), mat('#5a4a36'), x, 2.0, z, scene); b.rotation.set((r() - 0.5) * 1.2, 0, (r() - 0.5) * 1.2); } } }
  // Muschelbank: Hügel + viele Miesmuscheln
  const hT = heapTex(12, 1024, 7000); hT.repeat.set(3, 3);
  const bankGeo = new THREE.CircleGeometry(3.2, 64, 0, Math.PI * 2); bankGeo.rotateX(-Math.PI / 2);
  { const p = bankGeo.attributes.position; const r = rng(4); for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), d = Math.hypot(x, z) / 3.2; p.setY(i, 0.26 * Math.pow(Math.max(0, 1 - d * d), 0.6) + (r() - 0.5) * 0.02 * (1 - d)); } bankGeo.computeVertexNormals(); }
  const bank = mesh(bankGeo, new THREE.MeshStandardMaterial({map: hT, roughness: 0.4, color: '#c9c9d0'}), 0, 0, 0, scene);
  const NM = 2400; const swarm = shellSwarm(NM, scene, {scale: 1.2});
  { const r = rng(15); for (let i = 0; i < NM; i++) { const a = r() * 7, d = Math.sqrt(r()) * 3.0, x = Math.cos(a) * d, z = Math.sin(a) * d, dd = d / 3.2;
      const y = 0.26 * Math.pow(Math.max(0, 1 - dd * dd), 0.6) + 0.01; swarm.set(i, x, y, z, (r() - 0.5) * 0.8, r() * 6, (r() - 0.5) * 0.8, 0.8 + r() * 0.5); } swarm.commit(); }
  // Gruppe: Wattführer (gelbe Jacke) + 5 Wanderer in bunten Regenjacken, Gummistiefel
  const JACK = ['#f2c21b', '#e2412f', '#2f7fd2', '#2ea56a', '#f07ab0', '#7a5ac8'];
  const POS = [[0.2, 0.75], [-0.9, -0.1], [0.95, -0.2], [-0.4, -1.0], [0.55, -1.15], [-1.35, -0.95]];
  const people = POS.map(([x, z], i) => { const p = makePerson(1401 + i, {top: JACK[i], pants: i % 2 ? '#2d3a55' : '#3a3a3a', shoe: i % 2 ? '#2c6b3a' : '#e8c21a', sole: '#222', longHair: i === 2 || i === 4, height: i === 5 ? 0.82 : 1.0});
    addMouth(p); scene.add(p); return p; });
  // Kapuze/Mütze für den Führer
  mesh(new THREE.SphereGeometry(0.13, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2), mat('#f2c21b', {roughness: 0.6}), 0, 0.1, -0.01, people[0].userData.head);
  // Möwe
  const gull = new THREE.Group(); scene.add(gull);
  mesh(new THREE.CapsuleGeometry(0.07, 0.18, 4, 10), mat('#f4f4f2'), 0, 0, 0, gull).rotation.x = Math.PI / 2;
  mesh(new THREE.SphereGeometry(0.06, 10, 8), mat('#f4f4f2'), 0, 0.06, 0.13, gull);
  mesh(new THREE.ConeGeometry(0.018, 0.08, 6), mat('#f0b21a'), 0, 0.05, 0.22, gull).rotation.x = Math.PI / 2;
  for (const s of [-1, 1]) mesh(new THREE.SphereGeometry(0.01, 6, 4), mat('#111'), s * 0.035, 0.08, 0.17, gull);
  const wings = [-1, 1].map(s => { const w = new THREE.Group(); w.position.set(s * 0.05, 0.03, 0); gull.add(w); const f = mesh(new THREE.BoxGeometry(0.32, 0.01, 0.14), mat('#b9c0c8'), s * 0.16, 0, 0, w); mesh(new THREE.BoxGeometry(0.06, 0.012, 0.13), mat('#222'), s * 0.3, 0, 0, w); return w; });
  for (const s of [-1, 1]) mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.08, 4), mat('#f0b21a'), s * 0.03, -0.09, 0.0, gull);
  // Rettungshubschrauber (fern)
  const heli = new THREE.Group(); scene.add(heli);
  mesh(new THREE.CapsuleGeometry(0.9, 2.0, 4, 10), mat('#e8e8e6'), 0, 0, 0, heli).rotation.z = Math.PI / 2;
  mesh(new THREE.BoxGeometry(2.6, 0.3, 0.3), mat('#d62a2a'), 2.2, 0.3, 0, heli);
  const rotor = mesh(new THREE.BoxGeometry(6, 0.05, 0.25), mat('#333'), 0, 1.0, 0, heli);
  // Schlammspritzer
  const drops = new THREE.InstancedMesh(new THREE.SphereGeometry(0.028, 8, 6), new THREE.MeshStandardMaterial({color: '#4a4237', roughness: 0.3}), 300); drops.frustumCulled = false; scene.add(drops);
  const DR = []; { const r = rng(31); for (let i = 0; i < 300; i++) { const pi = i % 6, a = r() * 7; DR.push({pi, ox: Math.cos(a) * 0.25, oz: Math.sin(a) * 0.25, vx: Math.cos(a) * (0.6 + r()), vz: Math.sin(a) * (0.6 + r()), vy: 1.4 + r() * 2.2, t0: SINK + 0.18 + r() * 0.5, s: 0.5 + r()}); } }
  const o3 = new THREE.Object3D();

  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.05, 900); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const gone = T >= SINK; bank.visible = !gone; swarm.visible = !gone;
    const drop = clamp((T - SINK) / 0.22), sink = smooth(SINK + 0.15, SINK + 1.7, T);
    people.forEach((p, i) => { const [x, z] = POS[i]; const u = p.userData; const bx = x / 3.2, bz = z / 3.2;
      const yb = 0.26 * Math.pow(Math.max(0, 1 - (bx * bx + bz * bz)), 0.6);
      const d = sink * (i === 5 ? 0.7 : 0.85 + 0.05 * (i % 2)) + 0.04 * Math.sin((T - SINK) * 6 + i) * sink * Math.exp(-(T - SINK - 1.5) * 0.8) * (T > SINK + 1.5);
      p.position.set(x, gone ? lerp(yb, 0, easeIn(drop)) - d : yb, z); p.rotation.set(0, (i === 0 ? 0.35 : Math.sin(i * 1.9) * 0.4), 0);
      posePerson(p, {}); brows(p, 0, 0);
      if (!gone) { // Führer erklärt, Gruppe hört zu
        if (i === 0) { u.armR.rotation.x = -1.0 - 0.3 * Math.sin(T * 3); u.armR.rotation.z = 0.4; mouthOpen(p, 0.3 * Math.abs(Math.sin(T * 7))); } else { u.head.rotation.y = Math.sin(T * 0.8 + i) * 0.15; mouthOpen(p, 0); }
      } else { const panic = smooth(SINK, SINK + 0.4, T);
        u.armL.rotation.z = -panic * (1.8 + 0.5 * Math.sin(T * 6 + i)); u.armR.rotation.z = panic * (1.8 + 0.5 * Math.sin(T * 6 + i + 1)); u.armL.userData.fore.rotation.x = u.armR.userData.fore.rotation.x = -0.6;
        u.torso.rotation.x = 0.1 * Math.sin(T * 4 + i); mouthOpen(p, 0.5 + 0.4 * Math.abs(Math.sin(T * 5 + i))); brows(p, 1, 0);
        // Ziehen am Bein (einer versucht es)
        if (i === 3) { u.torso.rotation.x = 0.35 + 0.15 * Math.sin(T * 8); }
        if (i === 0 && T > 35.4) { u.armL.rotation.z = -0.3; u.armR.rotation.z = 0.3; u.head.rotation.x = -0.15; mouthOpen(p, 0.2); brows(p, 0.2, 0.8); } // genervt mit Möwe
      } });
    // Möwe: fliegt ab 34.3 heran, landet 35.3 auf dem Kopf des Führers
    const g0 = people[0]; g0.updateMatrixWorld(true); const head = g0.userData.head.localToWorld(V3(0, 0.2, 0));
    const fl = smooth(34.3, 35.3, T);
    if (T < 34.3) { gull.position.set(-6, 5, -4); gull.visible = false; }
    else { gull.visible = true; const start = V3(-5, 4.2, -3); gull.position.lerpVectors(start, head, easeOut(fl)); gull.position.y += Math.sin(fl * Math.PI) * 0.6; gull.rotation.set(0, Math.atan2(head.x - start.x, head.z - start.z) * (1 - fl) + Math.PI * fl * 0.9, 0); }
    const flap = fl < 1 ? Math.sin(T * 22) * 0.9 : (T < 35.8 ? Math.sin(T * 22) * 0.6 * (1 - smooth(35.3, 35.8, T)) : 0.05);
    wings[0].rotation.z = flap; wings[1].rotation.z = -flap;
    // Flut: Front kommt von hinten (z sinkt auf die Gruppe zu)
    const tz = lerp(-70, -4.5, smooth(33.5, 39, T)); tide.position.set(0, 0.012 + 0.03 * smooth(36, 39, T), tz); foamT.offset.x = T * 0.05;
    // Hubschrauber fern
    heli.position.set(lerp(-45, -10, smooth(35.5, 39, T)), 8, -42); rotor.rotation.y = T * 40; heli.visible = T > 35.5;
    // Schlammspritzer beim Einsinken
    DR.forEach((d, i) => { const dt = T - d.t0, [x, z] = POS[d.pi]; const y = 0.05 + d.vy * dt - 4.9 * dt * dt;
      if (dt > 0 && y > 0) { o3.position.set(x + d.ox + d.vx * dt, y, z + d.oz + d.vz * dt); o3.scale.set(d.s, d.s * 1.3, d.s); } else { o3.position.set(0, -99, 0); o3.scale.setScalar(0.0001); }
      o3.updateMatrix(); drops.setMatrixAt(i, o3.matrix); }); drops.instanceMatrix.needsUpdate = true;
    // Kamera
    let pos, tgt;
    const a = smooth(SINK + 0.2, SINK + 1.0, T), b = smooth(36.0, 39, T);
    pos = V3(lerp(0.4, 0.5, a), lerp(1.5, 0.9, a), lerp(6.2, 4.6, a)); tgt = V3(0, lerp(1.1, 0.5, a), 0);
    pos.lerp(V3(1.2, 4.2, 8.5), b); tgt.lerp(V3(-1, 0.2, -6), b);
    const sh = T > SINK && T < SINK + 0.5 ? 0.02 * (1 - (T - SINK) / 0.5) : 0;
    camera.position.copy(pos).add(V3(noise1(T * 6, 1) * sh, noise1(T * 6, 3) * sh, 0)); camera.lookAt(tgt);
    camera.fov = 46; camera.updateProjectionMatrix();
  }};
}
