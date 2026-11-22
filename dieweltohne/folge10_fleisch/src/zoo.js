// Stufe 4: Fütterung im Zoo. Der Pfleger greift in den Eimer – leer. Fünf hungrige Löwen kommen ans Gitter,
// der Löwe springt dagegen, beim zweiten Mal reißt das Gitterfeld aus der Verankerung und kippt nach außen.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, skyDome, easeIn, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {makeLion, poseLion} from './lion.js';
import {BUCKET, FENCE_HIT, FENCE_BREAK} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.fog = new THREE.Fog('#d9d2c0', 40, 260);
  scene.add(skyDome('#6f98c9', '#b9cde0', '#efe7d6', 600));
  const hemi = new THREE.HemisphereLight('#eaf2ff', '#7a6a4a', 0.8); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff0d0', 2.6); sun.position.set(-20, 30, 18); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -25, right: 25, top: 25, bottom: -25, near: 1, far: 120}); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03; scene.add(sun, sun.target);
  // Boden: Sand im Gehege, Pflasterweg außen
  const sandT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#cdb184'; g.fillRect(0, 0, w, h); const r = rng(3); for (let i = 0; i < 20000; i++) { const v = r(); g.fillStyle = v < 0.5 ? 'rgba(120,95,60,0.25)' : 'rgba(240,225,190,0.25)'; g.fillRect(r() * w, r() * h, 2, 2); } });
  sandT.wrapS = sandT.wrapT = THREE.RepeatWrapping; sandT.repeat.set(10, 10);
  mesh(new THREE.PlaneGeometry(200, 120), new THREE.MeshStandardMaterial({map: sandT, roughness: 1}), 0, 0, -60, scene).rotation.x = -Math.PI / 2;
  const pathT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#9a948a'; g.fillRect(0, 0, w, h); const r = rng(5); for (let y = 0; y < h; y += 32) for (let x = (y / 32 % 2) * 16; x < w; x += 32) { const v = 140 + r() * 30; g.fillStyle = `rgb(${v},${v - 5},${v - 12})`; g.fillRect(x + 1, y + 1, 30, 30); } });
  pathT.wrapS = pathT.wrapT = THREE.RepeatWrapping; pathT.repeat.set(40, 10);
  mesh(new THREE.PlaneGeometry(200, 60), new THREE.MeshStandardMaterial({map: pathT, roughness: 0.9}), 0, 0.005, 30, scene).rotation.x = -Math.PI / 2;
  // Felsen, toter Baum, Hintergrundbäume
  const rockM = mat('#9c8a72', {roughness: 1}); { const r = rng(8);
    for (let i = 0; i < 14; i++) { const rk = mesh(new THREE.DodecahedronGeometry(1 + r() * 2.5, 1), rockM, -18 + r() * 36, 0.4, -9 - r() * 16, scene); rk.scale.set(1.3, 0.6 + r() * 0.4, 1); rk.rotation.y = r() * 3; }
    mesh(new THREE.DodecahedronGeometry(3.2, 1), rockM, 6.5, 1.0, -8, scene).scale.set(1.5, 0.7, 1.1);
    const trunkM = mat('#6a5a4a', {roughness: 1}); const tr = mesh(new THREE.CylinderGeometry(0.25, 0.45, 6, 8), trunkM, -7, 3, -11, scene); tr.rotation.z = 0.15;
    for (let k = 0; k < 4; k++) { const b = mesh(new THREE.CylinderGeometry(0.08, 0.16, 3, 6), trunkM, -7 + (k - 1.5) * 0.8, 5 + k * 0.3, -11, scene); b.rotation.z = (k - 1.5) * 0.6; }
    const leafM = mat('#4a7a34', {roughness: 1}); for (let i = 0; i < 40; i++) { const x = -60 + r() * 120, z = -35 - r() * 40; mesh(new THREE.CylinderGeometry(0.3, 0.4, 5, 6), trunkM, x, 2.5, z, scene); mesh(new THREE.IcosahedronGeometry(3 + r() * 2, 1), leafM, x, 6 + r() * 2, z, scene); } }
  // Gitterzaun entlang z = 0, mit Pfosten; das Feld vor dem Pfleger (x -2.2..2.2) ist ein eigenes Teil
  const meshT = canvasTex(256, 256, (g, w, h) => { g.clearRect(0, 0, w, h); g.strokeStyle = '#3a3e42'; g.lineWidth = 5; for (let i = 0; i <= 8; i++) { g.beginPath(); g.moveTo(i * 32, 0); g.lineTo(i * 32, h); g.stroke(); g.beginPath(); g.moveTo(0, i * 32); g.lineTo(w, i * 32); g.stroke(); } });
  meshT.wrapS = meshT.wrapT = THREE.RepeatWrapping;
  const fenceMat = (rx, ry) => { const t = meshT.clone(); t.repeat.set(rx, ry); t.needsUpdate = true; return new THREE.MeshStandardMaterial({map: t, alphaTest: 0.5, transparent: false, side: THREE.DoubleSide, metalness: 0.6, roughness: 0.5}); };
  const postM = mat('#33373b', {metalness: 0.7, roughness: 0.4}), H = 4.5;
  for (const [x0, x1] of [[-30, -2.2], [2.2, 30]]) { const w = x1 - x0; const f = mesh(new THREE.PlaneGeometry(w, H), fenceMat(w * 2.2, H * 2.2), (x0 + x1) / 2, H / 2, 0, scene); f.castShadow = false; }
  for (let x = -30; x <= 30; x += 4.4) mesh(new THREE.BoxGeometry(0.16, H + 0.3, 0.16), postM, x + (x === -30 ? 0 : 0), (H + 0.3) / 2, 0, scene);
  const panel = new THREE.Group(); panel.position.set(0, 0, 0.02); scene.add(panel); // Drehpunkt unten
  const pm = mesh(new THREE.PlaneGeometry(4.4, H), fenceMat(4.4 * 2.2, H * 2.2), 0, H / 2, 0, panel); pm.castShadow = false;
  mesh(new THREE.BoxGeometry(4.4, 0.08, 0.08), postM, 0, H, 0, panel); mesh(new THREE.BoxGeometry(4.4, 0.08, 0.08), postM, 0, 0.05, 0, panel);
  // Futterluke/Plattform für den Pfleger, Besuchergeländer
  mesh(new THREE.BoxGeometry(5, 0.3, 2.4), mat('#8a8278'), 0, 0.15, 1.6, scene);
  const railM = mat('#4a4f55', {metalness: 0.5});
  mesh(new THREE.BoxGeometry(30, 0.06, 0.06), railM, 0, 1.0, 5.2, scene); for (let x = -15; x <= 15; x += 2) mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.0, 6), railM, x, 0.5, 5.2, scene);
  // Schild
  const signT = canvasTex(512, 160, (g, w, h) => { g.fillStyle = '#2e4a2a'; g.fillRect(0, 0, w, h); g.fillStyle = '#f2ead6'; g.font = 'bold 64px sans-serif'; g.textAlign = 'center'; g.fillText('LÖWEN', w / 2, 75); g.font = '34px sans-serif'; g.fillText('Fütterung 15:00 Uhr', w / 2, 130); });
  mesh(new THREE.PlaneGeometry(2.2, 0.7), new THREE.MeshStandardMaterial({map: signT}), -5, 1.6, 5.25, scene);
  mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.6, 6), railM, -5, 0.8, 5.2, scene);
  // Pfleger mit Eimer
  const keeper = makePerson(501, {skin: '#d9a47e', top: '#4f6b3a', pants: '#4f6b3a', hair: '#5a3b22', height: 1.0});
  scene.add(keeper);
  const bucket = new THREE.Group(); scene.add(bucket);
  mesh(new THREE.CylinderGeometry(0.2, 0.16, 0.36, 16, 1, true), new THREE.MeshStandardMaterial({color: '#e8e4dc', side: THREE.DoubleSide, roughness: 0.6}), 0, 0, 0, bucket);
  mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.01, 16), mat('#d8d4cc'), 0, -0.17, 0, bucket);
  const handle = mesh(new THREE.TorusGeometry(0.19, 0.008, 4, 16, Math.PI), mat('#666'), 0, 0.18, 0, bucket);
  // Besucher
  const visitors = []; { const r = rng(41); for (let i = 0; i < 9; i++) { const p = makePerson(520 + i, {height: i % 3 === 0 ? 0.8 : 1.0}); p.position.set(-9 + i * 2.1 + r() * 0.8, 0, 5.9 + r() * 1.2); scene.add(p); visitors.push({p, ry: Math.PI + (r() - 0.5) * 0.4}); } }
  // Löwen
  const lions = [makeLion(11, {male: true, scale: 1.05}), makeLion(12, {male: false}), makeLion(13, {male: false}), makeLion(14, {male: false}), makeLion(15, {male: false, scale: 0.95})];
  lions.forEach(l => scene.add(l));
  const START = [[1.5, -6.5, 0.6], [-4.5, -7.5, 1.2], [-1.0, -10.5, -0.4], [4.5, -11, 2.4], [-7.5, -6, 0.9]];
  const AT = [[0.2, -1.6], [-2.6, -1.4], [2.8, -1.5], [-4.6, -1.9], [4.6, -2.2]]; // Plätze am Gitter
  const dust = particles(500, 'smoke'); scene.add(dust);

  const camera = new THREE.PerspectiveCamera(45, 1080 / 1920, 0.05, 1000); scene.add(camera);
  return {scene, camera, update(shot, T) {
    // Pfleger: hält den Eimer, greift hinein (BUCKET), schaut hinein, dreht den Eimer um, weicht zurück, rennt
    const look = smooth(BUCKET, BUCKET + 0.5, T), tip = smooth(BUCKET + 1.2, BUCKET + 1.8, T), back = smooth(FENCE_HIT - 0.2, FENCE_HIT + 0.6, T), run = smooth(FENCE_BREAK - 0.3, FENCE_BREAK + 0.3, T);
    const kp = V3(0.6, 0.3, lerp(1.3, 2.4, back)); kp.z += run * (T - FENCE_BREAK + 0.3) * 4.5; kp.x += run * (T - FENCE_BREAK + 0.3) * 1.5;
    keeper.position.copy(kp); keeper.rotation.set(0, run > 0.5 ? 0.4 : Math.PI, 0); posePerson(keeper, {walk: T * (run > 0 ? 14 : 6), walkAmp: run > 0 ? 1.2 : back * (1 - smooth(FENCE_HIT + 0.6, FENCE_HIT + 0.8, T))});
    const ku = keeper.userData; ku.armL.rotation.x = -0.6; ku.armL.userData.fore.rotation.x = -0.9; ku.head.rotation.x = 0.4 * look * (1 - back);
    ku.armR.rotation.x = lerp(-0.2, -1.0, look); ku.armR.userData.fore.rotation.x = -0.6 * look;
    const dropB = smooth(FENCE_HIT, FENCE_HIT + 0.35, T);
    const handW = V3(kp.x - 0.27, 0.3 + 0.75, kp.z - 0.25);
    if (dropB < 1 && run === 0) { bucket.position.copy(handW); bucket.position.y -= 0.6 * easeIn(dropB); bucket.rotation.set(-1.4 * tip * (1 - dropB), 0, 0); }
    else { bucket.position.set(0.3, 0.45, 1.6); bucket.rotation.set(0, 0, Math.PI / 2); }
    // Besucher: schauen, weichen zurück, rennen weg
    visitors.forEach(({p, ry}, i) => { const flee = smooth(FENCE_BREAK + 0.1 + i * 0.05, FENCE_BREAK + 0.6 + i * 0.05, T);
      p.position.z = 5.9 + (i % 3) * 0.4 + flee * (T - FENCE_BREAK) * 4; p.rotation.y = flee > 0.4 ? ry + Math.PI : ry; posePerson(p, {walk: T * 13 + i, walkAmp: flee, armsUp: smooth(FENCE_HIT, FENCE_HIT + 0.3, T) * (1 - flee) * 0.3}); });
    // Gitterfeld: vibriert beim Aufprall, kippt bei FENCE_BREAK nach außen
    const hitV = (T > FENCE_HIT && T < FENCE_HIT + 0.8 ? Math.sin((T - FENCE_HIT) * 50) * Math.exp(-(T - FENCE_HIT) * 5) : 0) + (T > FENCE_BREAK - 1.0 && T < FENCE_BREAK ? Math.sin((T - FENCE_BREAK + 1) * 50) * Math.exp(-(T - FENCE_BREAK + 1) * 4) : 0);
    const fall = easeIn(clamp((T - FENCE_BREAK) / 0.55));
    panel.rotation.x = hitV * 0.06 + fall * (Math.PI / 2 - 0.05); panel.position.z = 0.02 + hitV * 0.1;
    updateParticles(dust, T > FENCE_BREAK + 0.4 ? [{type: 'burstSmoke', pos: V3(0, 0.3, 2.4), r: 3, t0: FENCE_BREAK + 0.45, size: 2.2, rise: 0.4}] : [], T);
    // Löwen
    lions.forEach((l, i) => {
      const [sx, sz, sry] = START[i], [ax, az] = AT[i];
      const wake = smooth(BUCKET + 0.3 + i * 0.15, BUCKET + 0.8 + i * 0.15, T), go = clamp((T - (BUCKET + 1.0 + i * 0.25)) / 2.2);
      const pos = V3(lerp(sx, ax, easeOut(go)), 0, lerp(sz, az, easeOut(go)));
      let ry = go > 0 && go < 1 ? Math.atan2(ax - sx, az - sz) : (go >= 1 ? Math.PI * 0 + (i - 2) * 0.1 : sry);
      if (go >= 1) ry = 0 + Math.sin(T * 1.3 + i) * 0.25; // Blick zum Gitter (+z)
      const pace = go >= 1 ? Math.sin(T * 0.9 + i * 2) * 0.8 : 0; pos.x += pace;
      let o = {gait: T * 7 + i, walk: go > 0 && go < 1 ? 1 : Math.abs(Math.cos(T * 0.9 + i * 2)) * 0.6 * (go >= 1 ? 1 : 0), lie: 1 - wake, lookUp: 0.3 * wake, roar: 0, t: T, tailWag: wake};
      if (i === 0) { // der Löwe springt zweimal gegen das Gitter
        const j1 = clamp((T - (FENCE_HIT - 0.45)) / 0.9), j2 = clamp((T - (FENCE_BREAK - 1.45)) / 0.9);
        const j = j1 > 0 && j1 < 1 ? j1 : (j2 > 0 && j2 < 1 ? j2 : 0);
        if (j > 0) { pos.x = ax; pos.z = lerp(az - 1.5, -0.95, Math.sin(j * Math.PI * 0.5)) - (j > 0.6 ? (j - 0.6) * 2 : 0); pos.y = Math.sin(j * Math.PI) * 1.4; ry = 0; o = {leap: 0.35 + j * 0.3, roar: 1, t: T}; }
        if (T > FENCE_BREAK + 0.5) { const k = clamp((T - FENCE_BREAK - 0.5) / 1.4); pos.set(ax, 0.04 + 0.1 * Math.sin(k * Math.PI), lerp(az, 2.6, k)); ry = 0; o = {gait: T * 8, walk: 1, run: 0.3, t: T, roar: k > 0.6 ? 1 : 0}; }
        else if (T > FENCE_BREAK - 0.45 && j === 0) { o.roar = 1; }
        if (T > FENCE_HIT + 0.45 && T < FENCE_BREAK - 1.45) o.roar = smooth(FENCE_HIT + 0.5, FENCE_HIT + 0.8, T) * (1 - smooth(FENCE_HIT + 1.6, FENCE_HIT + 1.9, T));
      } else if (T > FENCE_BREAK + 0.8 && i < 3) { const k = clamp((T - FENCE_BREAK - 0.8 - i * 0.25) / 1.6); pos.lerp(V3(i === 1 ? -1.2 : 1.2, 0, 2.5), k); ry = lerp(ry, 0, k); o = {gait: T * 8 + i, walk: k > 0 && k < 1 ? 1 : 0.4, run: 0.2, t: T}; }
      poseLion(l, o); l.position.copy(pos); l.rotation.set(0, ry, 0);
    });
    // Kamera: hinter dem Pfleger durchs Gitter, dann seitlich auf den Ausbruch
    const k = smooth(FENCE_HIT + 0.9, FENCE_BREAK - 0.3, T);
    let pos = V3(lerp(2.8, 7.5, k), lerp(2.0, 1.5, k), lerp(4.6, 6.2, k)), tgt = V3(lerp(-0.4, 0.2, k), lerp(0.9, 1.1, k), lerp(-3.0, 0.4, k));
    if (T > FENCE_BREAK) { const sh = Math.exp(-(T - FENCE_BREAK - 0.5) * 3) * (T > FENCE_BREAK + 0.5 ? 0.05 : 0); pos.x += Math.sin(T * 61) * sh; pos.y += Math.cos(T * 53) * sh; }
    camera.position.copy(pos).add(V3(noise1(T, 3) * 0.02, noise1(T, 6) * 0.015, 0)); camera.lookAt(tgt); camera.fov = 48; camera.updateProjectionMatrix();
  }};
}
