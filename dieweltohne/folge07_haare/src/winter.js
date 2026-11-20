// Bushaltestelle im Schnee, minus fünf Grad. Wolle ist Schafhaar: Pullover, Mützen und Schals verschwinden,
// übrig bleiben T-Shirts. Der flauschige Samojede wird zum nackten, zitternden Hund. Haare der Menschen sind auch weg.
// street_after (nach RETURN): Wolle und Haare sind zurück, aber niemand hält mehr das Gleichgewicht. Bus steht schräg, Warnblinker.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, skyDome, makePerson, posePerson, makeCar, rainSystem, updateRain, envMap} from './lib.js';
import {furCoat} from './furhair.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const WOOL_OFF = 17.15;

function knitTex(c) { return canvasTex(128, 128, (g, w, h) => { g.fillStyle = c; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 8) for (let x = 0; x < w; x += 8) {
  g.fillStyle = 'rgba(0,0,0,0.16)'; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 4, y + 8); g.lineTo(x + 8, y); g.lineTo(x + 4, y + 3); g.fill(); g.fillStyle = 'rgba(255,255,255,0.08)'; g.fillRect(x + 3, y + 1, 2, 5); } }); }

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#c9d3dc');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.45;
  scene.fog = new THREE.Fog('#c9d3dc', 18, 90);
  scene.add(skyDome('#9fb0c2', '#c9d3dc', '#e4e9ee', 300));
  scene.add(new THREE.HemisphereLight('#e8eef6', '#9aa4ae', 1.5));
  const sun = new THREE.DirectionalLight('#f4f2ee', 1.3); sun.position.set(-8, 14, 6); sun.target.position.set(0, 0, 0);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 60}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.03;
  scene.add(sun, sun.target);

  // Boden: verschneite Straße (x quer), Gehweg bei z<0
  const snowT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#eef2f6'; g.fillRect(0, 0, w, h); const r = rng(5); for (let i = 0; i < 6000; i++) { const v = 215 + r() * 40; g.fillStyle = `rgba(${v},${v + 3},${v + 8},0.5)`; g.fillRect(r() * w, r() * h, 3, 3); } });
  snowT.wrapS = snowT.wrapT = THREE.RepeatWrapping; snowT.repeat.set(10, 10);
  const snowM = new THREE.MeshStandardMaterial({map: snowT, roughness: 0.9, color: '#ffffff'});
  const ground = mesh(new THREE.PlaneGeometry(200, 200), snowM, 0, 0, 0, scene); ground.rotation.x = -Math.PI / 2;
  const roadT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#7d8086'; g.fillRect(0, 0, w, h); const r = rng(7); for (let i = 0; i < 9000; i++) { const v = 90 + r() * 120; g.fillStyle = `rgba(${v},${v},${v + 6},0.45)`; g.fillRect(r() * w, r() * h, 3, 3); }
    for (let i = 0; i < 8; i++) { g.fillStyle = 'rgba(70,72,78,0.6)'; g.fillRect(0, 60 + i * 55 + r() * 10, w, 14); } });
  roadT.wrapS = roadT.wrapT = THREE.RepeatWrapping; roadT.repeat.set(16, 1);
  const road = mesh(new THREE.PlaneGeometry(200, 8), new THREE.MeshStandardMaterial({map: roadT, roughness: 0.75}), 0, 0.01, 5, scene); road.rotation.x = -Math.PI / 2;
  // Schneewälle am Rand
  for (const z of [0.6, 9.4]) for (let x = -60; x < 60; x += 2.2) { const b = mesh(new THREE.SphereGeometry(1, 10, 8), snowM, x + Math.sin(x) * 0.5, 0, z, scene); b.scale.set(1.5, 0.35 + Math.abs(Math.sin(x * 1.7)) * 0.2, 0.55); }
  // Häuser hinter der Haltestelle und gegenüber
  const r = rng(12);
  for (const side of [-1, 1]) for (let x = -50; x < 50;) {
    const w = 7 + r() * 5, h = 9 + r() * 9, z = side < 0 ? -7 : 17;
    const cols = ['#c7b7a2', '#a9b8c4', '#d9cdb8', '#b9a08a', '#e0d8cc'];
    const ft = facadeTex(cols[Math.floor(r() * cols.length)], Math.floor(r() * 99), Math.round(h / 3), Math.round(w / 2.4));
    const b = mesh(new THREE.BoxGeometry(w - 0.2, h, 6), new THREE.MeshStandardMaterial({map: ft, roughness: 0.9}), x + w / 2, h / 2, z + side * 3, scene);
    mesh(new THREE.BoxGeometry(w, 0.4, 6.4), snowM, x + w / 2, h + 0.2, z + side * 3, scene); // Schnee auf dem Dach
    x += w;
  }
  // Bushaltestelle
  const stop = new THREE.Group(); stop.position.set(0, 0, -1.2); scene.add(stop);
  const steel = mat('#3a4048', {metalness: 0.7, roughness: 0.4});
  for (const x of [-2.2, 2.2]) for (const z of [-0.7, 0.7]) mesh(new THREE.BoxGeometry(0.08, 2.5, 0.08), steel, x, 1.25, z, stop);
  mesh(new THREE.BoxGeometry(4.7, 0.12, 1.7), steel, 0, 2.55, 0, stop);
  mesh(new THREE.BoxGeometry(4.7, 0.22, 1.7), snowM, 0, 2.72, 0, stop);
  const glassM = new THREE.MeshStandardMaterial({color: '#cfe0ea', transparent: true, opacity: 0.25, roughness: 0.05, metalness: 0.3});
  mesh(new THREE.BoxGeometry(4.4, 2.2, 0.02), glassM, 0, 1.3, -0.7, stop).castShadow = false;
  const adT = canvasTex(256, 400, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#ff5a7a'); gr.addColorStop(1, '#ffb35a'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.fillStyle = '#fff'; g.font = '600 40px Plex'; g.textAlign = 'center'; g.fillText('WINTER', w / 2, 90); g.fillText('SALE', w / 2, 140); g.font = '600 90px Plex'; g.fillText('-50%', w / 2, 300); });
  const ad = mesh(new THREE.BoxGeometry(1.1, 1.8, 0.1), new THREE.MeshStandardMaterial({map: adT, emissive: '#ffffff', emissiveMap: adT, emissiveIntensity: 0.35}), 2.2, 1.2, 0, stop); ad.rotation.y = Math.PI / 2;
  mesh(new RoundedBoxGeometry(2.4, 0.08, 0.4, 2, 0.02), mat('#8a6a4a'), -0.4, 0.48, -0.45, stop);
  const sign = new THREE.Group(); sign.position.set(-3.2, 0, 0.2); stop.add(sign);
  mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.8, 10), steel, 0, 1.4, 0, sign);
  const hT = canvasTex(128, 128, (g, w, h) => { g.fillStyle = '#ffd400'; g.beginPath(); g.arc(64, 64, 60, 0, 7); g.fill(); g.fillStyle = '#1b7a3a'; g.font = '700 80px Plex'; g.textAlign = 'center'; g.fillText('H', 64, 92); });
  mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.04, 24), new THREE.MeshStandardMaterial({map: hT}), 0, 2.9, 0, sign).rotation.x = Math.PI / 2;
  // Straßenlaterne
  const lampPost = mesh(new THREE.CylinderGeometry(0.06, 0.08, 5.5, 10), steel, 4.5, 2.75, -0.4, scene);
  // geparkte Autos mit Schnee
  [[-9, 2.0, 3], [9.5, 2.1, 5], [15, 7.9, 2]].forEach(([x, z, s]) => { const c = makeCar(s); c.position.set(x, 0, z); c.rotation.y = Math.PI / 2; scene.add(c); mesh(new THREE.BoxGeometry(1.5, 0.12, 2.0), snowM, 0, 1.47, 0, c); });
  // Bus (für street_after)
  const bus = new THREE.Group(); scene.add(bus);
  const busM = mat('#f2c230', {roughness: 0.4}), winM = mat('#1c2630', {roughness: 0.1, metalness: 0.6});
  mesh(new RoundedBoxGeometry(12, 3.0, 2.55, 4, 0.15), busM, 0, 1.75, 0, bus);
  mesh(new THREE.BoxGeometry(11.4, 1.1, 2.6), winM, 0, 2.25, 0, bus);
  mesh(new THREE.BoxGeometry(0.1, 1.4, 2.3), winM, 6.0, 2.0, 0, bus);
  mesh(new THREE.BoxGeometry(12.05, 0.25, 2.6), snowM, 0, 3.3, 0, bus);
  const hazM = new THREE.MeshStandardMaterial({color: '#ff9a1a', emissive: '#ff8a00', emissiveIntensity: 0});
  for (const x of [-6.02, 6.02]) for (const z of [-1.1, 1.1]) mesh(new THREE.BoxGeometry(0.06, 0.18, 0.25), hazM, x, 0.85, z, bus);
  for (const x of [-4, 4]) for (const z of [-1.28, 1.28]) { const w = mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.3, 18), mat('#151515'), x, 0.5, z, bus); w.rotation.x = Math.PI / 2; }
  bus.position.set(-9.0, 0, 4.4); bus.rotation.y = 0.22; bus.visible = false;
  // Schneefall
  const snow = rainSystem(2600, {x0: -12, x1: 14, y0: 0, y1: 9, z0: -4, z1: 14}, 0xffffff, 0.035, 0.9); scene.add(snow);

  // Menschen mit Wolle
  const woolCols = ['#b23a3a', '#2f5d8a', '#e8e0cf', '#3f7a52', '#7a4fa0', '#d98a2a', '#5a5f66'];
  const SPOTS = [[-1.6, -1.0, 0.2], [-0.6, -1.3, -0.1], [0.4, -0.9, 0.3], [1.3, -1.4, -0.4], [-2.6, -0.4, 0.5], [2.6, -0.2, -0.6], [0.0, -0.1, 0.1]];
  const people = SPOTS.map(([x, z, ry], i) => {
    const p = makePerson(40 + i, {top: ['#f2f2f2', '#9aa3ad', '#2b2b2b', '#e9d8c2'][i % 4], shortSleeve: true});
    p.position.set(x, 0, z); p.rotation.y = ry + 0.3; scene.add(p);
    const u = p.userData;
    const wm = new THREE.MeshStandardMaterial({map: knitTex(woolCols[i % woolCols.length]), roughness: 1});
    const wool = [];
    const sw = mesh(new THREE.CapsuleGeometry(0.19, 0.36, 4, 12), wm, 0, 0.3, 0, u.torso); sw.scale.set(1.15, 1.02, 0.8); wool.push(sw);
    for (const a of [u.armL, u.armR]) { wool.push(mesh(new THREE.CapsuleGeometry(0.066, 0.25, 4, 8), wm, 0, -0.16, 0, a)); wool.push(mesh(new THREE.CapsuleGeometry(0.058, 0.22, 4, 8), wm, 0, -0.13, 0, a.userData.fore)); }
    const hatM = new THREE.MeshStandardMaterial({map: knitTex(woolCols[(i + 3) % woolCols.length]), roughness: 1});
    if (i % 2 === 0) { const hat = mesh(new THREE.SphereGeometry(0.128, 14, 10, 0, Math.PI * 2, 0, Math.PI * 0.55), hatM, 0, 0.08, 0, u.head); wool.push(hat); wool.push(mesh(new THREE.SphereGeometry(0.045, 10, 8), hatM, 0, 0.215, 0, u.head)); }
    const scarf = mesh(new THREE.TorusGeometry(0.075, 0.035, 8, 18), hatM, 0, -0.07, 0, u.head); scarf.rotation.x = Math.PI / 2; wool.push(scarf);
    wool.push(mesh(new THREE.BoxGeometry(0.08, 0.3, 0.03), hatM, 0.04, -0.22, 0.11, u.head));
    return {p, wool, seed: i};
  });
  // Samojede (weiß, flauschig) und nackter Hund
  const dog = new THREE.Group(); dog.position.set(1.0, 0, 0.35); dog.rotation.y = -0.5; scene.add(dog);
  const fl = new THREE.Group(); dog.add(fl);
  const dW = mat('#f4f1ea', {roughness: 1});
  const db = mesh(new THREE.SphereGeometry(0.22, 18, 14), dW, 0, 0.42, 0, fl); db.scale.set(0.85, 0.85, 1.4);
  const dh = mesh(new THREE.SphereGeometry(0.14, 18, 14), dW, 0, 0.62, 0.32, fl);
  mesh(new THREE.CylinderGeometry(0.05, 0.07, 0.12, 10), dW, 0, 0.58, 0.45, fl).rotation.x = Math.PI / 2;
  mesh(new THREE.SphereGeometry(0.025, 8, 6), mat('#111'), 0, 0.59, 0.52, fl);
  for (const s of [-1, 1]) { mesh(new THREE.ConeGeometry(0.045, 0.1, 8), dW, s * 0.07, 0.75, 0.3, fl); mesh(new THREE.SphereGeometry(0.016, 8, 6), mat('#111'), s * 0.05, 0.66, 0.44, fl); }
  for (const [x, z] of [[-0.1, 0.18], [0.1, 0.18], [-0.1, -0.2], [0.1, -0.2]]) mesh(new THREE.CapsuleGeometry(0.045, 0.26, 4, 8), dW, x, 0.17, z, fl);
  fl.add(furCoat(3000, 7, {rx: 0.2, ry: 0.2, rz: 0.32, len: 0.06, width: 0.012, center: V3(0, 0.42, 0), cols: ['#ffffff', '#f2eee6', '#e6e1d6'], dir: V3(0, -0.3, -1)}));
  fl.add(furCoat(1200, 8, {rx: 0.14, ry: 0.13, rz: 0.14, len: 0.045, width: 0.01, center: V3(0, 0.62, 0.32), cols: ['#ffffff', '#f2eee6'], dir: V3(0, -0.2, -0.5)}));
  const tailD = mesh(new THREE.SphereGeometry(0.11, 12, 10), dW, 0, 0.62, -0.3, fl); tailD.scale.set(0.7, 0.7, 1.3);
  const nd = new THREE.Group(); dog.add(nd); nd.visible = false;
  const nM = mat('#e2b5a5', {roughness: 0.6});
  const nb = mesh(new THREE.SphereGeometry(0.14, 18, 14), nM, 0, 0.42, 0, nd); nb.scale.set(0.8, 0.85, 1.6);
  mesh(new THREE.SphereGeometry(0.1, 18, 14), nM, 0, 0.6, 0.28, nd);
  mesh(new THREE.CylinderGeometry(0.04, 0.06, 0.12, 10), nM, 0, 0.57, 0.39, nd).rotation.x = Math.PI / 2;
  mesh(new THREE.SphereGeometry(0.022, 8, 6), mat('#111'), 0, 0.58, 0.46, nd);
  for (const s of [-1, 1]) { mesh(new THREE.ConeGeometry(0.035, 0.09, 8), nM, s * 0.06, 0.71, 0.26, nd); mesh(new THREE.SphereGeometry(0.017, 8, 6), mat('#111'), s * 0.045, 0.63, 0.37, nd); }
  for (const [x, z] of [[-0.08, 0.16], [0.08, 0.16], [-0.08, -0.18], [0.08, -0.18]]) mesh(new THREE.CapsuleGeometry(0.03, 0.27, 4, 8), nM, x, 0.17, z, nd);
  mesh(new THREE.CapsuleGeometry(0.018, 0.22, 4, 8), nM, 0, 0.5, -0.32, nd).rotation.x = 0.9;

  const camera = new THREE.PerspectiveCamera(42, 1080 / 1920, 0.05, 400);
  return {scene, camera, update(shot, T) {
    const id = shot.id, t = T - shot.t0;
    updateRain(snow, T, 1.1, 0.25);
    const after = id === 'street_after';
    const woolGone = !after && T >= WOOL_OFF;
    people.forEach(({p, wool, seed}, i) => {
      wool.forEach(w => w.visible = !woolGone); p.userData.hair.visible = !woolGone;
      if (!after) {
        const k = smooth(WOOL_OFF + 0.2 + i * 0.07, WOOL_OFF + 0.8 + i * 0.07, T);
        posePerson(p, {look: Math.sin(T * 0.6 + i) * 0.2 * (1 - k)});
        const u = p.userData;
        if (k > 0) { // Arme um den Körper, zittern, hüpfen
          u.armL.rotation.set(-0.45 * k, 0, 0.3 * k); u.armR.rotation.set(-0.45 * k, 0, -0.3 * k);
          u.armL.userData.fore.rotation.set(-1.25 * k, 0.6 * k, 0); u.armR.userData.fore.rotation.set(-1.25 * k, -0.6 * k, 0);
          u.torso.rotation.x = 0.15 * k + Math.sin(T * 40 + i) * 0.015 * k;
          u.hips.position.y = 0.92 + Math.max(0, Math.sin(T * 7 + i * 1.3)) * 0.06 * k * (i % 3 === 0 ? 1 : 0.3);
          u.head.rotation.x = 0.2 * k; u.head.rotation.y = Math.sin(T * 2 + i) * 0.4 * k;
        }
        p.position.set(SPOTS[i][0], 0, SPOTS[i][1]); p.rotation.set(0, SPOTS[i][2] + 0.3, 0);
        // gegen Ende: erster Schwindel
        const wob = smooth(22.0, 24.0, T); p.rotation.z = Math.sin(T * 2.3 + i) * 0.07 * wob;
      } else {
        // Niemand steht: liegen, sitzen, am Mast festhalten
        const mode = i % 3;
        const tryUp = Math.max(0, Math.sin(t * 0.9 + i * 1.7));
        if (mode === 0) { posePerson(p, {fall: 1, fallDir: 1, slipSide: (i % 2 ? 1 : -1)}); p.position.set(SPOTS[i][0], 0, SPOTS[i][1] + 0.2); p.rotation.set(0, SPOTS[i][2] + 1.2 * i, 0); p.userData.head.rotation.y = Math.sin(t * 0.7 + i) * 0.5; }
        else if (mode === 1) { posePerson(p, {}); const u = p.userData; p.position.set(SPOTS[i][0], -0.5 + tryUp * 0.12, SPOTS[i][1]); p.rotation.set(0, SPOTS[i][2], Math.sin(t * 1.1 + i) * 0.25);
          u.legL.rotation.x = -1.4; u.legR.rotation.x = -1.3; u.legL.userData.knee.rotation.x = 1.6; u.legR.userData.knee.rotation.x = 1.7; u.armL.rotation.set(-0.3, 0, -0.9); u.armR.rotation.set(-0.3, 0, 0.9); u.torso.rotation.x = 0.3; u.head.rotation.x = 0.4; }
        else { posePerson(p, {}); const u = p.userData; p.position.set(SPOTS[i][0], 0, SPOTS[i][1]); p.rotation.set(Math.sin(t * 1.3 + i) * 0.12, SPOTS[i][2], Math.sin(t * 0.9 + i) * 0.22);
          u.armL.rotation.set(-0.4, 0, -1.2); u.armR.rotation.set(-0.4, 0, 1.2); u.legL.userData.knee.rotation.x = 0.5; u.legR.userData.knee.rotation.x = 0.4; u.torso.rotation.x = 0.35; u.head.rotation.x = 0.5; }
      }
    });
    fl.visible = !woolGone; nd.visible = woolGone;
    dog.position.y = 0; dog.rotation.set(0, -0.5 + (woolGone ? Math.sin(T * 30) * 0.03 : 0), after ? 1.4 : 0);
    if (after) dog.position.set(1.4, 0.18, 0.4); else dog.position.set(1.0, 0, 0.35);
    bus.visible = after; hazM.emissiveIntensity = after && Math.sin(T * 6) > 0 ? 3 : 0;
    // Kamera
    camera.fov = 42;
    if (!after) {
      camera.position.set(0.9 + t * 0.06 + noise1(T * 1.5, 2) * 0.03, 1.45 + noise1(T * 1.3, 3) * 0.02, 4.3 - t * 0.12); camera.lookAt(-0.1, 1.0, -1.0);
    } else {
      camera.position.set(4.2 - t * 0.15, 1.6 + noise1(T, 4) * 0.03, 4.6 - t * 0.06); camera.lookAt(-0.8 - t * 0.1, 0.5, -0.9);
    }
    camera.updateProjectionMatrix();
  }};
}
