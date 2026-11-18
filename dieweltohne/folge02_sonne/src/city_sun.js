// Innenstadt: mittags plötzlich dunkel, dann Blackout. Kreuzung mit Ampeln, Straßenbahn, Supermarkt, Krankenhaus.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, easeOut, noise1, canvasTex, tileTex, asphaltTex, makePerson, posePerson, makeCar} from './lib.js';
import {decorateBuilding, addStreetFurniture, LIT} from './city.js';
import {skyMaterial} from './beach.js';
import {makePhone, makeHands, updateScreen} from './phone.js';
import {particles, updateParticles, flicker} from './fx.js';
import {DARK, RETURN} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const SUN_DIR = V3(-0.35, 0.85, -0.4).normalize();
const CROSS = [-29, -15]; // Querstraße

// Fassade mit eigener Leuchtkarte für die Fenster
function facade(base, seed, floors, cols) {
  const r = rng(seed); const W = 256, H = 512;
  const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');
  const e = document.createElement('canvas'); e.width = W; e.height = H; const ge = e.getContext('2d'); ge.fillStyle = '#000'; ge.fillRect(0, 0, W, H);
  g.fillStyle = base; g.fillRect(0, 0, W, H);
  for (let i = 0; i < 1500; i++) { g.fillStyle = `rgba(0,0,0,${r() * 0.05})`; g.fillRect(r() * W, r() * H, 3, 3); }
  const fh = H / floors, cw = W / cols;
  for (let f = 0; f < floors - 1; f++) for (let k = 0; k < cols; k++) {
    const x = k * cw + cw * 0.22, y = f * fh + fh * 0.2, ww = cw * 0.56, hh = fh * 0.55;
    g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(x - 4, y - 4, ww + 8, hh + 8);
    const grd = g.createLinearGradient(x, y, x + ww, y + hh); grd.addColorStop(0, '#5a6b7c'); grd.addColorStop(1, '#2a333d'); g.fillStyle = grd; g.fillRect(x, y, ww, hh);
    g.fillStyle = 'rgba(255,255,255,0.18)'; g.fillRect(x + ww / 2 - 1.5, y, 3, hh); g.fillRect(x, y + hh * 0.4, ww, 3);
    g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(x - 6, y + hh + 4, ww + 12, 5);
    if (r() < 0.45) { const warm = r() < 0.8; ge.fillStyle = warm ? `hsl(38,80%,${45 + r() * 25}%)` : '#9fc0ff'; ge.fillRect(x, y, ww, hh); ge.fillStyle = 'rgba(0,0,0,0.5)'; ge.fillRect(x + ww / 2 - 1.5, y, 3, hh); }
  }
  g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(0, H - fh * 0.9, W, fh * 0.9);
  const map = new THREE.CanvasTexture(c), emis = new THREE.CanvasTexture(e); map.colorSpace = emis.colorSpace = THREE.SRGBColorSpace; map.anisotropy = 8;
  return {map, emis};
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), skyMaterial(SUN_DIR)); sky.renderOrder = -10; scene.add(sky);
  const envScene = new THREE.Scene(); envScene.background = new THREE.Color('#a9c6e6');
  const pm = new THREE.PMREMGenerator(renderer); const env = pm.fromScene(envScene, 0.02).texture; scene.environment = env;
  scene.fog = new THREE.Fog('#a9bfd6', 60, 420);
  const hemi = new THREE.HemisphereLight('#c8dcf2', '#5a5248', 1.0); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff3dc', 3.0); sun.position.copy(SUN_DIR).multiplyScalar(90); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -45, right: 45, top: 45, bottom: -45, near: 1, far: 220}); sun.shadow.bias = -0.0005;
  scene.add(sun, sun.target);
  const starLight = new THREE.HemisphereLight('#41557d', '#0b0b0d', 0); scene.add(starLight);

  // Straße, Querstraße, Gehwege
  const asp = asphaltTex(); asp.repeat.set(2, 60);
  const road = mesh(new THREE.PlaneGeometry(13, 420), new THREE.MeshStandardMaterial({map: asp, roughness: 0.85}), 0, 0, 0, scene); road.rotation.x = -Math.PI / 2; road.castShadow = false;
  const asp2 = asphaltTex(); asp2.repeat.set(60, 2);
  const road2 = mesh(new THREE.PlaneGeometry(420, 14), new THREE.MeshStandardMaterial({map: asp2, roughness: 0.85}), 0, 0.001, (CROSS[0] + CROSS[1]) / 2, scene); road2.rotation.x = -Math.PI / 2; road2.castShadow = false;
  const lineM = mat('#e8e8e2', {roughness: 0.5});
  for (let z = -210; z < 210; z += 9) { if (z > CROSS[0] - 3 && z < CROSS[1] + 3) continue; for (const x of [-3.2, 3.2]) { const l = mesh(new THREE.PlaneGeometry(0.15, 4), lineM, x, 0.004, z, scene); l.rotation.x = -Math.PI / 2; l.castShadow = false; } }
  // Straßenbahnschienen in der Mitte
  for (const x of [-0.72, 0.72]) { const rl = mesh(new THREE.BoxGeometry(0.07, 0.02, 420), mat('#9a9ea4', {metalness: 0.9, roughness: 0.3}), x, 0.01, 0, scene); rl.castShadow = false; }
  const tiles = tileTex(); tiles.repeat.set(3, 100);
  for (const s of [-1, 1]) for (const [z0, z1] of [[-210, CROSS[0]], [CROSS[1], 210]]) {
    const L = z1 - z0, zc = (z0 + z1) / 2;
    mesh(new THREE.BoxGeometry(5, 0.15, L), new THREE.MeshStandardMaterial({map: tiles, roughness: 0.6, color: '#c4c2bc'}), s * 9, 0.075, zc, scene);
    mesh(new THREE.BoxGeometry(0.25, 0.17, L), mat('#a4a49e', {roughness: 0.5}), s * 6.55, 0.085, zc, scene);
  }
  // Häuserzeilen (Lücke für die Querstraße)
  const r = rng(5); const winMats = [];
  const cols = ['#d8cbb2', '#c9b79c', '#e2d9c8', '#b9a48a', '#cfc2ad', '#a89a8a', '#d6c3a5', '#e0d2bc'];
  for (const s of [-1, 1]) {
    let z = -200;
    while (z < 200) {
      const w = 9 + r() * 7, h = 12 + r() * 16, d = 12;
      if (z + w > CROSS[0] - 1 && z < CROSS[1] + 1) { z = CROSS[1] + 1; continue; }
      const c = cols[Math.floor(r() * cols.length)];
      const {map, emis} = facade(c, Math.floor(r() * 1000), Math.round(h / 3.3), Math.round(w / 3));
      const fm = new THREE.MeshStandardMaterial({map, emissiveMap: emis, emissive: '#ffffff', emissiveIntensity: 0, roughness: 0.85}); winMats.push(fm);
      mesh(new THREE.BoxGeometry(d, h, w), [fm, fm, mat('#6d6a66'), mat(c), mat(c), mat(c)], s * (11.5 + d / 2), h / 2, z + w / 2, scene);
      decorateBuilding(scene, s, z, w, h, d, r);
      mesh(new THREE.BoxGeometry(d + 0.6, 0.5, w + 0.2), mat('#7d7368'), s * (11.5 + d / 2) - s * 0.3, h + 0.25, z + w / 2, scene);
      z += w;
    }
  }
  const city = addStreetFurniture(scene);
  // Weitere Stadtblöcke für das Luftbild (instanziert)
  const blockGeo = new THREE.BoxGeometry(1, 1, 1); blockGeo.translate(0, 0.5, 0);
  const blocks = new THREE.InstancedMesh(blockGeo, new THREE.MeshStandardMaterial({color: '#b8ad9c', roughness: 0.9}), 900); let bi = 0;
  const m4 = new THREE.Matrix4();
  for (let x = -330; x <= 330; x += 26) for (let z = -330; z <= 260; z += 26) {
    if (Math.abs(x) < 34 || (z > CROSS[0] - 16 && z < CROSS[1] + 2)) continue;
    for (let k = 0; k < 2 && bi < 900; k++) { const h = 10 + r() * 22; m4.compose(V3(x + (k ? 6 : -6), 0, z + (r() - 0.5) * 4), new THREE.Quaternion(), V3(11, h, 20)); blocks.setMatrixAt(bi++, m4); }
  }
  blocks.count = bi; blocks.castShadow = blocks.receiveShadow = true; scene.add(blocks);
  // Krankenhaus mit Notstrom (leuchtet)
  const hosp = new THREE.Group(); hosp.position.set(70, 0, -120); scene.add(hosp);
  const hw = facade('#e8e6e0', 9, 9, 10);
  const hmat = new THREE.MeshStandardMaterial({map: hw.map, emissiveMap: hw.emis, emissive: '#ffffff', emissiveIntensity: 0, roughness: 0.8}); winMats.push(hmat);
  mesh(new THREE.BoxGeometry(40, 30, 30), hmat, 0, 15, 0, hosp);
  const cross = canvasTex(128, 128, (g) => { g.fillStyle = '#fff'; g.fillRect(0, 0, 128, 128); g.fillStyle = '#d0021b'; g.fillRect(48, 12, 32, 104); g.fillRect(12, 48, 104, 32); });
  const crossM = new THREE.MeshStandardMaterial({map: cross, emissive: '#ffffff', emissiveMap: cross, emissiveIntensity: 2});
  const cm = mesh(new THREE.PlaneGeometry(6, 6), crossM, -20.1, 24, 0, hosp); cm.rotation.y = -Math.PI / 2;
  mesh(new THREE.CylinderGeometry(6, 6, 0.3, 24), mat('#3a3a3a'), 0, 30.2, 0, hosp);

  // Laternen (aus), Bäume, Ampeln
  for (let z = -180; z < 180; z += 18) for (const s of [-1, 1]) {
    if (z > CROSS[0] - 2 && z < CROSS[1] + 2) continue;
    mesh(new THREE.CylinderGeometry(0.06, 0.09, 5.5, 8), mat('#2c2f33', {metalness: 0.6, roughness: 0.4}), s * 7.0, 2.75, z, scene);
    mesh(new THREE.BoxGeometry(0.9, 0.1, 0.25), mat('#2c2f33'), s * 6.65, 5.45, z, scene);
    mesh(new THREE.BoxGeometry(0.5, 0.05, 0.2), mat('#d8d8d0'), s * 6.45, 5.38, z, scene);
    if ((z / 18) % 2 === 0) {
      mesh(new THREE.CylinderGeometry(0.12, 0.16, 3, 7), mat('#4a3a2c'), s * 10.2, 1.5, z + 9, scene);
      const c = mesh(new THREE.IcosahedronGeometry(1.8, 1), mat('#4f6d3a', {flatShading: true, roughness: 0.9}), s * 10.2, 4.2, z + 9, scene); c.scale.y = 1.2;
    }
  }
  // Oberleitung der Straßenbahn
  for (let z = -180; z < 180; z += 30) { mesh(new THREE.BoxGeometry(14, 0.06, 0.06), mat('#333'), 0, 6.2, z, scene); }
  for (const x of [-0.72, 0.72]) mesh(new THREE.BoxGeometry(0.02, 0.02, 400), mat('#333'), x * 0, 6.0, 0, scene);
  const signals = [];
  for (const [x, z, ry] of [[7.2, CROSS[1] + 0.8, 0], [-7.2, CROSS[0] - 0.8, Math.PI], [7.2, CROSS[0] - 0.8, Math.PI], [-7.2, CROSS[1] + 0.8, 0]]) {
    const g = new THREE.Group(); g.position.set(x, 0.15, z); g.rotation.y = ry; scene.add(g);
    mesh(new THREE.CylinderGeometry(0.07, 0.07, 3.6, 8), mat('#222'), 0, 1.8, 0, g);
    mesh(new THREE.BoxGeometry(0.38, 1.0, 0.3), mat('#1a1a1a'), 0, 3.3, 0.18, g);
    const lamps = [['#ff3b2f', 3.62], ['#ffb02e', 3.3], ['#3bdc6a', 2.98]].map(([c, y]) => mesh(new THREE.SphereGeometry(0.11, 12, 8), new THREE.MeshStandardMaterial({color: '#222', emissive: c, emissiveIntensity: 0}), 0, y, 0.34, g));
    signals.push(lamps);
  }

  // Straßenbahn
  const tram = new THREE.Group(); tram.position.set(0, 0, -6); scene.add(tram);
  const tramM = mat('#f2c230', {roughness: 0.4, metalness: 0.2}), white = mat('#f4f4f0', {roughness: 0.4});
  const tw = canvasTex(512, 64, (g, w, h) => { g.fillStyle = '#1b232c'; g.fillRect(0, 0, w, h); for (let i = 0; i < 12; i++) { g.fillStyle = '#2d3b4a'; g.fillRect(8 + i * 42, 6, 34, h - 12); } });
  const twM = new THREE.MeshStandardMaterial({map: tw, roughness: 0.1, metalness: 0.5, emissive: '#fff0cc', emissiveMap: tw, emissiveIntensity: 0});
  for (const [dz, L] of [[0, 9], [-9.3, 9], [9.3, 9]]) {
    mesh(new THREE.BoxGeometry(2.4, 1.0, L), tramM, 0, 0.75, dz, tram); mesh(new THREE.BoxGeometry(2.4, 1.2, L), white, 0, 1.85, dz, tram);
    for (const s of [-1, 1]) { const w = mesh(new THREE.PlaneGeometry(L - 0.4, 0.9), twM, s * 1.21, 1.95, dz, tram); w.rotation.y = s * Math.PI / 2; }
    mesh(new THREE.BoxGeometry(2.3, 0.2, L), mat('#bbb'), 0, 2.55, dz, tram);
  }
  mesh(new THREE.BoxGeometry(0.05, 1.4, 0.05), mat('#333'), 0, 3.3, 0, tram).rotation.z = 0.4;
  LIT.push(twM);

  // Autos: stehen im Dunkeln mit Licht. Unfall an der Kreuzung
  const cars = []; for (let i = 0; i < 26; i++) { const c = makeCar(i + 1, i === 25 ? {ambulance: true, color: '#f4f4f0'} : (i === 24 ? {color: '#2b4f9e'} : {})); scene.add(c); cars.push(c); }
  const carLights = cars.slice(0, 6).map(() => { const l = new THREE.SpotLight('#fff1d0', 0, 40, 0.5, 0.5, 1.4); scene.add(l, l.target); return l; });
  const blue = new THREE.PointLight('#2a6bff', 0, 30, 1.5); scene.add(blue);
  // Scherben auf der Kreuzung, Warnblinker der Unfallautos
  const shardG = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.06, 0.04), new THREE.MeshStandardMaterial({color: '#dfeaf2', roughness: 0.05, metalness: 0.8, side: THREE.DoubleSide}), 300);
  { const q = rng(44); for (let i = 0; i < 300; i++) { const a = q() * 6.28, d = Math.pow(q(), 0.6) * 4; m4.compose(V3(0.2 + Math.cos(a) * d, 0.012, -22 + Math.sin(a) * d * 0.7), new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI / 2, 0, q() * 6)), V3(1 + q(), 1 + q(), 1)); shardG.setMatrixAt(i, m4); } }
  scene.add(shardG); shardG.castShadow = false;
  const hazTex = canvasTex(64, 64, (g, w) => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,190,80,1)'); gr.addColorStop(1, 'rgba(255,140,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const haz = Array.from({length: 8}, () => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({map: hazTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})); sp.scale.setScalar(0.7); scene.add(sp); return sp; });
  const steamS = particles(300, 'smoke'); scene.add(steamS);
  // Menschen
  const people = []; for (let i = 0; i < 30; i++) { const p = makePerson(300 + i, {}); scene.add(p);
    const ph = mesh(new THREE.BoxGeometry(0.075, 0.15, 0.01), mat('#111'), 0, -0.33, 0.05, p.userData.armR.userData.fore);
    const glow = mesh(new THREE.PlaneGeometry(0.03, 0.03), new THREE.MeshBasicMaterial({color: '#ffffff'}), 0, 0.05, -0.008, ph); glow.rotation.y = Math.PI;
    people.push({p, ph, glow}); }
  const beamTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.12, 'rgba(255,255,255,0.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const beams = people.map(() => { const b = new THREE.Mesh(new THREE.ConeGeometry(0.9, 7, 18, 1, true), new THREE.MeshBasicMaterial({map: beamTex, color: '#dfe8ff', transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false})); b.geometry.translate(0, -3.5, 0); scene.add(b); return b; });
  const torches = [0, 1, 2, 3, 4].map(() => { const l = new THREE.SpotLight('#e6eeff', 0, 25, 0.42, 0.6, 1.5); scene.add(l, l.target); return l; });
  // Supermarkt mit Hinweis (Nachtszene)
  const sm = new THREE.Group(); sm.position.set(-11.45, 0.15, 30); scene.add(sm);
  const smSign = canvasTex(512, 96, (g, w, h) => { g.fillStyle = '#c8102e'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.font = '600 58px Plex'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('SUPERMARKT', w / 2, h / 2 + 3); });
  const ss = mesh(new THREE.PlaneGeometry(7, 1.3), new THREE.MeshStandardMaterial({map: smSign}), 0.05, 3.6, 0, sm); ss.rotation.y = Math.PI / 2;
  const note = canvasTex(256, 320, (g, w, h) => { g.fillStyle = '#f4f1e6'; g.fillRect(0, 0, w, h); g.fillStyle = '#1a1a1a'; g.font = '600 34px Plex'; g.textAlign = 'center'; ['KEIN STROM', 'KASSEN', 'AUSGEFALLEN', '', 'NUR BARGELD'].forEach((t, i) => g.fillText(t, w / 2, 60 + i * 50)); });
  const nm = mesh(new THREE.PlaneGeometry(0.8, 1.0), new THREE.MeshStandardMaterial({map: note, roughness: 0.9}), 0.08, 1.5, -1.6, sm); nm.rotation.y = Math.PI / 2;
  // Feuer (brennendes Auto in der Nacht) und Brände fürs Luftbild
  const fire = particles(2200, 'flame'); scene.add(fire); const smoke = particles(1200, 'smoke'); scene.add(smoke);
  const fireLight = new THREE.PointLight('#ff7a2a', 0, 30, 1.8); scene.add(fireLight);
  const FIRES = [V3(3.5, 0.6, 62), V3(-40, 8, -60), V3(90, 6, 20), V3(-110, 10, -150), V3(20, 4, -190), V3(150, 6, -40)];
  // Lichtpunkte (Taschenlampen) fürs Luftbild
  const dotsGeo = new THREE.BufferGeometry(); const dn = 260; const dp = new Float32Array(dn * 3); const dseed = [];
  for (let i = 0; i < dn; i++) { const x = (r() < 0.6 ? (r() < 0.5 ? -1 : 1) * (7.5 + r() * 3) : (r() - 0.5) * 12); const z = -180 + r() * 360; dseed.push([x, z, r() * 6, (r() - 0.5) * 1.2]); }
  dotsGeo.setAttribute('position', new THREE.BufferAttribute(dp, 3));
  const dots = new THREE.Points(dotsGeo, new THREE.PointsMaterial({color: '#e8f0ff', size: 3, sizeAttenuation: false, transparent: true, opacity: 0.9, fog: false})); dots.frustumCulled = false; scene.add(dots);

  // Kamera und Handy
  const camera = new THREE.PerspectiveCamera(48, 1080 / 1920, 0.03, 1500); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#2a2d33'); const hands = makeHands('#d9a47e', '#3a3f48');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig); rig.position.set(0.0, -0.075, -0.27); rig.rotation.set(-0.1, 0.0, 0.02);
  const torchBeam = new THREE.SpotLight('#eaf1ff', 0, 35, 0.38, 0.5, 1.4); camera.add(torchBeam); torchBeam.position.set(0.02, -0.05, -0.3); torchBeam.target.position.set(0.3, -1.4, -8); camera.add(torchBeam.target);
  function drawPhone(g, st, SW, SH) {
    g.fillStyle = '#0b0d12'; g.fillRect(0, 0, SW, SH);
    g.fillStyle = '#fff'; g.font = '500 24px Plex'; g.textAlign = 'left'; g.fillText('17:47', 40, 52);
    g.textAlign = 'right'; g.fillStyle = '#ff5a4f'; g.fillText('Kein Netz   9 %', SW - 40, 52);
    g.textAlign = 'center'; g.fillStyle = '#9aa3ad'; g.font = '500 30px Plex'; g.fillText(st.k < 0.5 ? 'Notruf wird gewählt …' : 'Anruf fehlgeschlagen', SW / 2, 300);
    g.fillStyle = '#fff'; g.font = '300 170px Garamond'; g.fillText('112', SW / 2, 500);
    g.fillStyle = st.k < 0.5 ? '#3bdc6a' : '#ff3b30'; g.beginPath(); g.arc(SW / 2, 1080, 78, 0, 7); g.fill();
    g.fillStyle = '#fff'; g.font = '500 26px Plex'; g.fillText(st.k < 0.5 ? '' : 'Kein Mobilfunknetz verfügbar', SW / 2, 820);
    if (st.k >= 0.5) { g.strokeStyle = '#fff'; g.lineWidth = 10; g.beginPath(); g.moveTo(SW / 2 - 30, 1050); g.lineTo(SW / 2 + 30, 1110); g.moveTo(SW / 2 + 30, 1050); g.lineTo(SW / 2 - 30, 1110); g.stroke(); }
    else { for (let i = 0; i < 3; i++) { g.fillStyle = `rgba(255,255,255,${0.3 + 0.7 * ((Math.floor(st.t * 3) % 3) === i)})`; g.beginPath(); g.arc(SW / 2 - 40 + i * 40, 360, 8, 0, 7); g.fill(); } }
  }
  const dust = (() => { const q = rng(15); return Array.from({length: 70}, () => [q() * 600, q() * 1300, 1 + q() * 2.5, q()]); })();
  function overlay(g) { for (const [x, y, s, v] of dust) { g.fillStyle = `rgba(255,255,255,${0.08 + v * 0.12})`; g.beginPath(); g.arc(x, y, s, 0, 7); g.fill(); } g.save(); g.globalAlpha = 0.12; g.strokeStyle = '#fff'; g.lineWidth = 30; g.beginPath(); g.moveTo(60, 900); g.quadraticCurveTo(300, 760, 540, 980); g.stroke(); g.restore(); }

  // Positionen
  const PARK = []; // Autos in den Spuren
  for (let i = 0; i < 26; i++) { const lane = [-4.8, -1.6, 1.6, 4.8][i % 4]; PARK.push([lane, (lane > 0 ? -1 : 1) * 0 + 10 + Math.floor(i / 4) * 9 * (i % 2 ? 1 : -1) + (i % 3), lane > 0 ? Math.PI : 0]); }
  const poses = people.map((_, i) => ({x: (i % 3 ? 1 : -1) * (7.6 + (i * 0.37 % 1) * 3.4), z: i < 12 ? -2 + i * 1.3 : -40 + ((i * 7.3) % 50), ry: (i * 1.7) % 6.28, d: (i * 0.61) % 1}));

  function setMode(T, id) {
    const day = id === 'back' ? (T >= RETURN ? 1 : 0) : 0;
    const power = id === 'street_dark' ? 1 : 0;           // mittags ist der Strom noch da, später nicht mehr
    const night = id === 'night' || id === 'aerial';
    sky.material.uniforms.day.value = day; sky.material.uniforms.stars.value = day ? 0 : (night ? 1 : 0.8);
    sun.intensity = 3.0 * day; hemi.intensity = 1.0 * day; scene.environmentIntensity = 0.6 * day + 0.01;
    starLight.intensity = day ? 0 : (id === 'aerial' ? 0.16 : night ? 0.07 : 0.05);
    scene.fog.color.set(day ? '#a9bfd6' : '#05070b'); scene.fog.near = day ? 60 : 30; scene.fog.far = day ? 420 : (id === 'aerial' ? 900 : 260);
    renderer.toneMappingExposure = day ? 1.0 : 1.5;
    LIT.forEach(m => { m.emissiveIntensity = power * 1.1; });
    winMats.forEach(m => { m.emissiveIntensity = m === hmat ? (night || id === 'back' ? 0.9 : 0.9) : power * 1.0; });
    crossM.emissiveIntensity = 1.5;
    city.skyline.forEach(m => m.color.set(day ? '#9aa6b3' : '#07090d'));
    blocks.material.color.set(day ? '#b8ad9c' : '#5d574f');
    return {day, power, night};
  }

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id; const {day, power, night} = setMode(T, id);
    // Autos parken / stehen
    cars.forEach((c, i) => { const [x, z, ry] = PARK[i]; c.position.set(x, 0, z); c.rotation.set(0, ry, 0); c.visible = !(id === 'back' && z > -45 && z < 2 && i > 3 && i !== 25); });
    // Unfall auf der Kreuzung (ab "back")
    if (id !== 'street_dark') {
      cars[0].position.set(-0.6, 0, -20.5); cars[0].rotation.y = 0.55; cars[1].position.set(1.6, 0, -23.4); cars[1].rotation.y = -1.45;
      cars[2].position.set(-4.6, 0, -18.5); cars[2].rotation.y = 0.25; cars[3].position.set(4.4, 0, -25.5); cars[3].rotation.y = Math.PI + 0.3;
      cars[1].userData.body.rotation.z = 0.04; cars[25].position.set(-4.8, 0, -3); cars[25].rotation.y = 0;
    }
    const crash = id !== 'street_dark';
    shardG.visible = crash; const blink = Math.sin(T * 9) > 0;
    haz.forEach((h, k) => { const c = cars[k >> 2]; const corner = V3((k & 1 ? 0.75 : -0.75), 0.75, (k & 2 ? 2.15 : -2.15)).applyAxisAngle(V3(0, 1, 0), c.rotation.y).add(c.position); h.position.copy(corner); h.visible = crash && blink; });
    if (crash) { cars[0].userData.body.rotation.set(0.02, 0, -0.03); cars[1].userData.body.rotation.set(0, 0, 0.05); }
    updateParticles(steamS, crash ? [{type: 'smoke', pos: V3(cars[0].position.x + Math.sin(cars[0].rotation.y) * 2, 0.9, cars[0].position.z + Math.cos(cars[0].rotation.y) * 2), r: 0.4, t0: -9, size: 1.1, rise: 0.7, col: [0.7, 0.7, 0.7], alpha: 0.18, share: 1}] : [{type: 'smoke', pos: V3(0, -99, 0), r: 1, t0: 99, share: 1}], T, V3(0.4, 0, 0.3));
    const ambBlue = id !== 'street_dark';
    cars[25].userData.blue.forEach((b, k) => b.material.emissiveIntensity = ambBlue ? 4 * Math.max(0, Math.sin(T * 12 + k * Math.PI)) : 0);
    blue.position.set(cars[25].position.x, 2.2, cars[25].position.z); blue.intensity = ambBlue ? 40 * Math.max(0, Math.sin(T * 12)) + 15 * Math.max(0, Math.sin(T * 12 + Math.PI)) : 0;
    // Scheinwerfer: die vordersten Autos richten Licht nach vorn
    carLights.forEach((l, k) => { const c = cars[[4, 5, 6, 7, 8, 9][k]]; const f = V3(0, 0, 1).applyAxisAngle(V3(0, 1, 0), c.rotation.y);
      l.position.copy(c.position).add(V3(0, 0.7, 0)).addScaledVector(f, 2.2); l.target.position.copy(l.position).addScaledVector(f, 10).add(V3(0, -0.8, 0)); l.intensity = day ? 0 : 60; });
    tram.visible = true; tram.position.z = id === 'street_dark' ? 40 : -44;
    signals.forEach((lamps, k) => lamps.forEach((m, j) => { m.material.emissiveIntensity = power ? (j === (k % 2 ? 0 : 2) ? 3 : 0) : 0; }));
  // Menschen
    let ti = 0;
    people.forEach((o, i) => {
      const q = poses[i]; const p = o.p; p.visible = true;
      let x = q.x, z = q.z, ry = q.ry;
      if (id === 'night') { z = 22 + (i % 10) * 1.2 + (i > 15 ? 6 : 0); x = -9.2 + (i % 3) * 0.9 + (i * 0.13 % 0.5); ry = -Math.PI / 2 + (i % 4 - 1.5) * 0.4; } // Menge vor dem Supermarkt
      p.position.set(x, 0.15, z); p.rotation.set(0, ry, 0);
      const torch = id === 'street_dark' ? smooth(24.5 + q.d * 3, 25 + q.d * 3, T) * (q.d < 0.7) : (night || (id === 'back' && T < RETURN)) ? (q.d < 0.55 ? 1 : 0) : 0;
      posePerson(p, {walk: 0, walkAmp: 0, look: Math.sin(T * 0.6 + i) * 0.4});
      if (id === 'street_dark' && q.d >= 0.7) p.userData.head.rotation.x = -0.45; // schaut nach oben
      if (torch > 0) { const u = p.userData; u.armR.rotation.x = -1.3 * torch; u.armR.userData.fore.rotation.x = -0.25; }
      if (id === 'back' && T >= RETURN) { const u = p.userData; const k = smooth(RETURN, RETURN + 0.4, T); u.armL.rotation.x = -2.5 * k; u.armL.rotation.z = 0.4 * k; u.armL.userData.fore.rotation.x = -1.6 * k; u.head.rotation.x = 0.2 * k; } // Hand vor die Augen
      o.glow.visible = torch > 0.5;
      const b = beams[i]; b.material.opacity = torch > 0.5 ? 0.06 : 0;
      if (torch > 0.5) {
        const wp = new THREE.Vector3(); o.ph.getWorldPosition(wp);
        const dir = V3(Math.sin(ry), -0.15 + 0.15 * Math.sin(T * 0.7 + i), Math.cos(ry)).normalize();
        b.position.copy(wp); b.quaternion.setFromUnitVectors(V3(0, -1, 0), dir);
        if (ti < torches.length && Math.hypot(wp.x - camera.position.x, wp.z - camera.position.z) < 30) { const l = torches[ti++]; l.position.copy(wp); l.target.position.copy(wp).addScaledVector(dir, 8); l.intensity = 25; }
      }
    });
    for (; ti < torches.length; ti++) torches[ti].intensity = 0;
    // Feuer
    const fx = [], sm = [];
    if (night) {
      FIRES.forEach((p, k) => { fx.push({type: 'flame', pos: p, r: k ? 2.5 : 0.9, t0: -9, size: k ? 2.6 : 1.6, rise: k ? 4 : 2.4, power: k ? 0.7 : 1, share: k ? 1 : 2}); sm.push({type: 'smoke', pos: p.clone().add(V3(0, k ? 4 : 1.5, 0)), r: k ? 4 : 1, t0: -9, size: k ? 10 : 3.5, rise: k ? 4 : 2.2, col: [0.05, 0.05, 0.055], alpha: 0.6, share: 1}); });
      cars[12].position.set(3.5, 0, 62); cars[12].rotation.y = 0.4;
    }
    updateParticles(fire, fx, T, V3(0.6, 0, 0.2)); updateParticles(smoke, sm, T, V3(1.2, 0, 0.3));
    fireLight.position.set(3.5, 2, 62); fireLight.intensity = night ? 45 * flicker(T) : 0;
    // Taschenlampen-Punkte (Luftbild)
    dots.visible = id === 'aerial';
    if (dots.visible) dseed.forEach(([x, z, ph, v], i) => { dp[i * 3] = x; dp[i * 3 + 1] = 1.3; dp[i * 3 + 2] = z + T * v + Math.sin(T * 2 + ph) * 0.3; });
    dotsGeo.attributes.position.needsUpdate = true;
    hosp.visible = true;

    // Kamera
    rig.visible = false; torchBeam.intensity = 0; camera.fov = 48;
    if (id === 'street_dark') {
      camera.position.set(9.3, 1.7, 18 - t * 0.5); camera.lookAt(2.0, 2.6, -25);
    } else if (id === 'back') {
      const u = smooth(0, 7.5, t);
      camera.position.set(lerp(8.4, 7.8, u), lerp(2.3, 2.1, u), lerp(-5, -8, u)); camera.lookAt(lerp(-1.5, 0, u), 0.9, -24);
      if (T >= RETURN) { const k = Math.exp(-(T - RETURN) * 2); camera.position.x += noise1(T * 8, 2) * 0.04 * k; }
    } else if (id === 'night') {
      if (t < 5) { // Handy-POV
        rig.visible = true; camera.fov = 52;
        camera.position.set(6.0 + noise1(T, 1) * 0.02, 1.62, 40 - t * 0.25); camera.lookAt(0.0, 1.3, 20);
        updateScreen(phone, [], {t: T, noDrops: true, k: smooth(1.8, 1.9, t), custom: drawPhone, overlay});
        torchBeam.intensity = 12;
      } else {
        const u = smooth(5, 12, t);
        camera.position.set(lerp(-3.5, -2.0, u), 1.7, lerp(42, 37, u)); camera.lookAt(-9.5, 1.6, 26);
      }
    } else { // aerial
      const u = smooth(0, 12, t);
      camera.fov = 50; camera.position.set(lerp(18, 26, u), lerp(42, 95, u), lerp(110, 150, u)); camera.lookAt(lerp(0, -10, u), lerp(0, 20, u), lerp(20, -200, u));
    }
    camera.updateProjectionMatrix();
    city.furniture.forEach(f => { f.visible = Math.hypot(f.position.x - camera.position.x, f.position.z - camera.position.z) > 6 || f.position.z > camera.position.z + 1; });
  }};
}
