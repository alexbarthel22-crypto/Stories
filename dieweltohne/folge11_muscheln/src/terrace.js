// Stufe 3: Muschel-Restaurant, Terrasse in der Altstadt. Der Kellner trägt sechs schwere Töpfe Muscheln auf einem Tablett.
// Die Muscheln verschwinden, das Tablett wird schlagartig leicht – seine Arme schießen hoch, die Töpfe fliegen
// und landen kopfüber auf den Köpfen der Gäste (und zuletzt auf seinem eigenen).
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, tileTex, skyDome, easeOut, easeIn, makePerson, posePerson, envMap} from './lib.js';
import {seat, addMouth, mouthOpen, brows} from './people.js';
import {shellSwarm} from './shells.js';
import {TRAY, POT_HITS} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.add(skyDome('#6f9fd8', '#b6d0ea', '#eef2f4', 300));
  scene.fog = new THREE.Fog('#dfe6ec', 30, 160);
  const hemi = new THREE.HemisphereLight('#eaf2ff', '#5a5040', 0.8); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff1dc', 2.6); sun.position.set(6, 10, 7); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 40}); sun.shadow.bias = -0.0004; scene.add(sun, sun.target);
  // Kopfsteinpflaster
  const cobT = canvasTex(512, 512, (g, w, h) => { const r = rng(4); g.fillStyle = '#5b5650'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += 32) for (let x = (y / 32) % 2 * 16; x < w; x += 32) { const v = 120 + r() * 50; g.fillStyle = `rgb(${v},${v - 6},${v - 14})`; g.beginPath(); g.roundRect(x + 2, y + 2, 28, 28, 8); g.fill(); } });
  cobT.wrapS = cobT.wrapT = THREE.RepeatWrapping; cobT.repeat.set(14, 14);
  mesh(new THREE.PlaneGeometry(40, 40), new THREE.MeshStandardMaterial({map: cobT, roughness: 0.9}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  // Fassade mit Fenstern, Markise (rot-weiß gestreift)
  const facT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#e6d3b3'; g.fillRect(0, 0, w, h); const r = rng(2);
    for (let i = 0; i < 600; i++) { g.fillStyle = `rgba(90,60,30,${r() * 0.05})`; g.fillRect(r() * w, r() * h, 5, 5); }
    for (const x of [40, 200, 360]) for (const y of [40, 210]) { g.fillStyle = '#f4efe6'; g.fillRect(x - 6, y - 6, 112, 142); g.fillStyle = '#34414e'; g.fillRect(x, y, 100, 130); g.fillStyle = 'rgba(255,255,255,0.3)'; g.fillRect(x + 48, y, 4, 130); } });
  mesh(new THREE.BoxGeometry(10, 8, 0.3), new THREE.MeshStandardMaterial({map: facT, roughness: 0.9}), 0, 6.2, -3.2, scene);
  const shopT = canvasTex(512, 256, (g, w, h) => { g.fillStyle = '#2b1f18'; g.fillRect(0, 0, w, h); const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#ffd59a'); gr.addColorStop(1, '#b8743a'); g.fillStyle = gr; g.fillRect(20, 30, 220, 220); g.fillRect(272, 30, 220, 220);
    g.fillStyle = 'rgba(40,25,15,0.7)'; g.fillRect(126, 30, 6, 220); g.fillRect(378, 30, 6, 220); });
  mesh(new THREE.BoxGeometry(10, 2.4, 0.3), new THREE.MeshStandardMaterial({map: shopT, roughness: 0.6, emissive: '#ffffff', emissiveMap: shopT, emissiveIntensity: 0.25}), 0, 1.2, -3.2, scene);
  const awT = canvasTex(256, 64, (g, w, h) => { for (let i = 0; i < 16; i++) { g.fillStyle = i % 2 ? '#f4f0ea' : '#c4232f'; g.fillRect(i * 16, 0, 16, h); } });
  awT.wrapS = THREE.RepeatWrapping; awT.repeat.set(3, 1);
  const aw = mesh(new THREE.PlaneGeometry(10, 2.0), new THREE.MeshStandardMaterial({map: awT, roughness: 0.8, side: THREE.DoubleSide}), 0, 2.85, -2.35, scene); aw.rotation.x = -1.15;
  const valT = canvasTex(1024, 64, (g, w, h) => { g.fillStyle = '#c4232f'; g.fillRect(0, 0, w, h); g.fillStyle = '#f4f0ea'; g.font = 'italic 600 44px Garamond, serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('Moules · Frites · Moules · Frites', w / 2, h / 2 + 2); });
  mesh(new THREE.PlaneGeometry(10, 0.3), new THREE.MeshStandardMaterial({map: valT, roughness: 0.8}), 0, 2.32, -1.44, scene);
  // Blumenkästen
  for (const x of [-3.5, 3.5]) { mesh(new THREE.BoxGeometry(1.2, 0.4, 0.4), mat('#6b4a2c'), x, 0.2, -2.6, scene); for (let k = 0; k < 6; k++) mesh(new THREE.IcosahedronGeometry(0.16, 0), mat(k % 2 ? '#d8344a' : '#3f7a2a'), x - 0.5 + k * 0.2, 0.48, -2.6, scene); }
  // Tische, Stühle, Gäste
  const clothT = canvasTex(128, 128, (g, w, h) => { for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { g.fillStyle = (x + y) % 2 ? '#f6f2ea' : '#c62a35'; g.fillRect(x * 16, y * 16, 16, 16); } });
  const clothM = new THREE.MeshStandardMaterial({map: clothT, roughness: 0.85}), woodM = mat('#3a2a1e', {roughness: 0.6}), chairM = mat('#2b3d2f', {roughness: 0.5});
  const table = (x, z) => { mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.03, 28), clothM, x, 0.74, z, scene); mesh(new THREE.CylinderGeometry(0.04, 0.05, 0.72, 8), woodM, x, 0.36, z, scene);
    mesh(new THREE.CylinderGeometry(0.03, 0.025, 0.14, 10), new THREE.MeshPhysicalMaterial({color: '#f2c14a', roughness: 0.1, transparent: true, opacity: 0.8}), x + 0.15, 0.83, z + 0.1, scene);
    mesh(new THREE.ConeGeometry(0.05, 0.16, 10), mat('#f0e6d2'), x - 0.12, 0.83, z + 0.12, scene).rotation.x = Math.PI; };
  const chair = (x, z, ry) => { const c = new THREE.Group(); c.position.set(x, 0, z); c.rotation.y = ry; scene.add(c);
    mesh(new RoundedBoxGeometry(0.42, 0.04, 0.42, 2, 0.015), chairM, 0, 0.47, 0, c); mesh(new RoundedBoxGeometry(0.42, 0.45, 0.04, 2, 0.015), chairM, 0, 0.72, -0.2, c);
    for (const [a, b] of [[-0.18, -0.18], [0.18, -0.18], [-0.18, 0.18], [0.18, 0.18]]) mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.47, 6), chairM, a, 0.235, b, c); };
  table(-0.75, -0.55); table(0.85, -0.9); table(0.0, -2.0);
  // Gäste: [x, z, Blickrichtung]
  const GP = [[-1.2, -0.55, Math.PI / 2], [-0.3, -0.55, -Math.PI / 2], [0.4, -0.9, Math.PI / 2], [1.3, -0.9, -Math.PI / 2], [0.0, -1.55, Math.PI]];
  const guests = GP.map(([x, z, ry], i) => { chair(x - Math.sin(ry) * 0.05, z - Math.cos(ry) * 0.05, ry); const p = makePerson(1301 + i, {longHair: i % 2 === 1}); addMouth(p); scene.add(p); return p; });
  // Kellner, Tablett, sechs Töpfe
  const waiter = makePerson(1320, {skin: '#e2b28c', top: '#f7f7f4', pants: '#111', hair: '#2a1d15', height: 1.04}); addMouth(waiter); scene.add(waiter);
  mesh(new THREE.BoxGeometry(0.36, 0.55, 0.02), mat('#141414'), 0, 0.05, 0.14, waiter.userData.torso); // Schürze
  const tray = new THREE.Group(); scene.add(tray);
  mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.02, 32), mat('#c9ccd0', {metalness: 0.9, roughness: 0.3}), 0, 0, 0, tray);
  const potM = new THREE.MeshPhysicalMaterial({color: '#151517', roughness: 0.3, clearcoat: 0.8}), rimM = mat('#2a2a2e', {roughness: 0.4});
  const pots = []; const POTPOS = [[-0.22, -0.12], [0.0, -0.22], [0.22, -0.12], [-0.22, 0.13], [0.0, 0.22], [0.22, 0.13]];
  const potGeo = new THREE.CylinderGeometry(0.11, 0.095, 0.15, 24, 1, true); potGeo.translate(0, 0.075, 0);
  const swarm = shellSwarm(6 * 36, scene, {scale: 0.85});
  for (let i = 0; i < 6; i++) { const g = new THREE.Group(); scene.add(g);
    const side = mesh(potGeo, potM, 0, 0, 0, g); side.material.side = THREE.DoubleSide;
    mesh(new THREE.CircleGeometry(0.095, 24), potM, 0, 0.002, 0, g).rotation.x = -Math.PI / 2;
    mesh(new THREE.TorusGeometry(0.11, 0.008, 6, 24), rimM, 0, 0.15, 0, g).rotation.x = Math.PI / 2;
    for (const s of [-1, 1]) mesh(new THREE.TorusGeometry(0.025, 0.007, 6, 12, Math.PI), rimM, s * 0.12, 0.12, 0, g).rotation.set(0, s * Math.PI / 2, 0);
    pots.push(g); }
  const MS = []; { const r = rng(21); for (let i = 0; i < 6 * 36; i++) { const a = r() * 7, d = Math.sqrt(r()) * 0.085; MS.push([Math.cos(a) * d, 0.1 + r() * 0.07, Math.sin(a) * d, r() * 6, r() * 6, r() * 6]); } }
  // Flugbahnen: Start auf dem Tablett, Landung kopfüber auf Kopf (Gast 0..4, zuletzt Kellner)
  const camera = new THREE.PerspectiveCamera(45, 1080 / 1920, 0.05, 300); scene.add(camera);
  const tmp = V3(0, 0, 0);
  function headPos(p) { p.updateMatrixWorld(true); return p.userData.head.localToWorld(V3(0, 0.1, 0)); }

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    // Gäste sitzen, essen/plaudern; nach dem Treffer: Arme hoch, Kopf wackelt
    guests.forEach((p, i) => { const [x, z, ry] = GP[i]; p.position.set(x, 0, z); p.rotation.set(0, ry, 0); seat(p, 0.49); const u = p.userData;
      u.armL.rotation.x = -0.7; u.armR.rotation.x = -0.7; u.armL.userData.fore.rotation.x = -0.9; u.armR.userData.fore.rotation.x = -0.9; u.head.rotation.y = 0.25 * Math.sin(T * 1.3 + i); mouthOpen(p, 0.2 * Math.abs(Math.sin(T * 5 + i)));
      const look = smooth(TRAY + 0.3, TRAY + 0.6, T); u.head.rotation.x = -0.45 * look; u.head.rotation.y *= 1 - look; mouthOpen(p, lerp(0.2, 0.8, look)); brows(p, look, 0);
      const hit = POT_HITS[i], h = smooth(hit, hit + 0.15, T);
      if (h > 0) { const wob = Math.exp(-(T - hit) * 2.5); u.torso.rotation.x = 0.15 * Math.sin((T - hit) * 18) * wob; u.head.rotation.x = 0.2 * wob * Math.sin((T - hit) * 20);
        u.armL.rotation.x = lerp(-0.7, -2.4, h); u.armR.rotation.x = lerp(-0.7, -2.4, h); u.armL.rotation.z = -0.5 * h; u.armR.rotation.z = 0.5 * h; u.armL.userData.fore.rotation.x = u.armR.userData.fore.rotation.x = -0.6; mouthOpen(p, 0.9); } });
    // Kellner: läuft von rechts herein, bleibt stehen
    const walk = smooth(24.0, TRAY - 0.1, T); const wx = lerp(1.9, 0.15, walk);
    waiter.position.set(wx, 0, 0.55); waiter.rotation.set(0, -Math.PI / 2 + 0.6 * smooth(TRAY - 0.3, TRAY, T), 0);
    posePerson(waiter, {walk: T * 9, walkAmp: 1 - smooth(TRAY - 0.5, TRAY - 0.1, T)});
    const wu = waiter.userData, launch = smooth(TRAY, TRAY + 0.12, T), relax = smooth(TRAY + 0.5, TRAY + 1.0, T);
    wu.armR.rotation.x = -2.6 - 0.35 * launch * (1 - relax); wu.armR.rotation.z = 0.25; wu.armR.userData.fore.rotation.x = lerp(-0.6, -0.05, launch);
    wu.armL.rotation.x = lerp(-0.4, -2.8, launch * (1 - relax)); wu.armL.userData.fore.rotation.x = -0.4;
    mouthOpen(waiter, smooth(TRAY + 0.2, TRAY + 0.5, T)); brows(waiter, smooth(TRAY + 0.2, TRAY + 0.5, T), 0);
    const lastHit = POT_HITS[5];
    if (T > lastHit) { const k = T - lastHit; wu.torso.rotation.z = 0.12 * Math.sin(k * 12) * Math.exp(-k * 2); wu.head.rotation.x = 0.1 * Math.sin(k * 16) * Math.exp(-k * 2); wu.armL.rotation.x = -2.2; wu.armR.rotation.x = -2.2; mouthOpen(waiter, 0.9); }
    // Tablett: auf der rechten Hand, schießt hoch
    waiter.updateMatrixWorld(true);
    const handP = wu.armR.userData.fore.localToWorld(V3(0, -0.32, 0));
    const trayUp = T > TRAY ? Math.max(0, 2.6 * (T - TRAY) - 4.9 * Math.pow(T - TRAY, 2)) : 0;
    tray.position.copy(handP).add(V3(0, 0.04 + trayUp, 0)); tray.rotation.set(0.25 * smooth(TRAY, TRAY + 0.4, T), 0, -0.3 * smooth(TRAY, TRAY + 0.4, T));
    if (T > TRAY + 0.4) { const k = T - TRAY - 0.4; tray.position.copy(handP).add(V3(-0.3 * k, Math.max(-handP.y + 0.01, 0.04 + 0.5 - 4.9 * k * k), -0.7 * k)); tray.rotation.set(1.3 * clamp(k * 2), 0, -0.3 - 2 * clamp(k)); }
    // Töpfe
    const t0 = TRAY + 0.05;
    pots.forEach((g, i) => { const [px, pz] = POTPOS[i];
      const onTray = tray.localToWorld(V3(px, 0.012, pz));
      if (T < t0) { g.position.copy(onTray); g.rotation.set(tray.rotation.x, 0, tray.rotation.z); }
      else { const th = POT_HITS[i], target = i < 5 ? headPos(guests[i]) : headPos(waiter);
        const P0 = V3().copy(handP).add(V3(px, 0.05, pz)), P1 = target.clone().add(V3(0, 0.17, 0));
        if (T < th) { const d = th - t0, u = (T - t0) / d; const v = P1.clone().sub(P0).divideScalar(d); v.y += 4.9 * d;
          const dt = T - t0; g.position.set(P0.x + v.x * dt, P0.y + v.y * dt - 4.9 * dt * dt, P0.z + v.z * dt); g.rotation.set(Math.PI * easeOut(u) * (i % 2 ? 1 : -1) * 1, u * 2 * (i - 2.5), 0); }
        else { g.position.copy(P1); const k = T - th; g.rotation.set(Math.PI + 0.12 * Math.sin(k * 15) * Math.exp(-k * 3), 0, 0.1 * Math.sin(k * 11) * Math.exp(-k * 2)); }
      } });
    // Muscheln in den Töpfen (bis TRAY)
    for (let i = 0; i < 6 * 36; i++) { const pi = Math.floor(i / 36), m = MS[i];
      if (T >= TRAY) { swarm.hide(i); continue; }
      tmp.set(m[0], m[1], m[2]); pots[pi].updateMatrixWorld(true); pots[pi].localToWorld(tmp); swarm.set(i, tmp.x, tmp.y, tmp.z, m[3], m[4], m[5], 1); }
    swarm.commit();
    // Kamera: von der Straße, leicht schwenkend
    const k = smooth(24.6, 25.6, T), k2 = smooth(25.6, 31, T);
    camera.position.set(lerp(1.0, 0.35, k) - 0.15 * k2 + noise1(T, 2) * 0.01, lerp(2.3, 2.05, k), lerp(3.6, 6.0, k) + 0.3 * k2);
    camera.lookAt(lerp(0.55, 0.0, k), lerp(1.85, 1.35, k), lerp(0.4, -0.6, k));
    camera.fov = lerp(40, 48, k);  camera.updateProjectionMatrix();
  }};
}
