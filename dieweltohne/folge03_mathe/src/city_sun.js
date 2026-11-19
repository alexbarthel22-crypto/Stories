// Innenstadt am Mittag, während Mathe fehlt: Bildschirme zeigen Unsinn, alle Ampeln grün, Unfall auf der Kreuzung, Banking-App.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, easeOut, noise1, canvasTex, tileTex, asphaltTex, makePerson, posePerson, makeCar} from './lib.js';
import {decorateBuilding, addStreetFurniture, LIT} from './city.js';
import {skyMaterial} from './beach.js';
import {makePhone, makeHands, updateScreen} from './phone.js';
import {particles, updateParticles, flicker} from './fx.js';
import {VANISH, RETURN} from './timeline.js';
import {sparkSystem, updateSparks} from './lib.js';
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

  // LED-Werbetafel an der Hauswand links und digitale Straßenuhr
  const GLC = '0123456789+−×÷=∞√∑∫πΔ≠≈%#?!§&@'.split('');
  const ledC = document.createElement('canvas'); ledC.width = 640; ledC.height = 384; const ledT = new THREE.CanvasTexture(ledC); ledT.colorSpace = THREE.SRGBColorSpace;
  const ledM = new THREE.MeshStandardMaterial({color: '#000', emissive: '#ffffff', emissiveMap: ledT, emissiveIntensity: 2.2, roughness: 0.4});
  const led = mesh(new THREE.PlaneGeometry(7, 4.2), ledM, -9.95, 7.5, -4, scene); led.rotation.y = Math.PI / 2;
  mesh(new THREE.BoxGeometry(1.5, 4.5, 7.3), mat('#1c1d20'), -10.72, 7.5, -4, scene);
  const clkC = document.createElement('canvas'); clkC.width = 256; clkC.height = 128; const clkT = new THREE.CanvasTexture(clkC); clkT.colorSpace = THREE.SRGBColorSpace;
  const clkM = new THREE.MeshStandardMaterial({color: '#000', emissive: '#ffffff', emissiveMap: clkT, emissiveIntensity: 1.4});
  const clk = new THREE.Group(); clk.position.set(-7.6, 0.15, 6); scene.add(clk);
  mesh(new THREE.CylinderGeometry(0.08, 0.1, 3.4, 10), mat('#2c2f33', {metalness: 0.6}), 0, 1.7, 0, clk);
  mesh(new THREE.BoxGeometry(1.5, 0.8, 0.25), mat('#2c2f33', {metalness: 0.6}), 0, 3.7, 0, clk);
  for (const s of [1, -1]) { const f = mesh(new THREE.PlaneGeometry(1.36, 0.66), clkM, 0, 3.7, s * 0.13, clk); if (s < 0) f.rotation.y = Math.PI; }
  function drawLED(T, gl) {
    const g = ledC.getContext('2d'), w = 640, h = 384, r = rng(Math.floor(T * 20) + 9);
    if (!gl) { const grd = g.createLinearGradient(0, 0, w, h); grd.addColorStop(0, '#ff3d6e'); grd.addColorStop(1, '#ffb02e'); g.fillStyle = grd; g.fillRect(0, 0, w, h);
      g.fillStyle = '#fff'; g.font = '600 64px Plex'; g.textAlign = 'center'; g.fillText('SOMMER SALE', w / 2, 150); g.font = '600 150px Plex'; g.fillText('−50 %', w / 2, 300); }
    else { g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 40; i++) { g.fillStyle = `hsl(${r() * 360},100%,${40 + r() * 30}%)`; g.fillRect(0, r() * h, w, 2 + r() * 30); }
      g.fillStyle = '#fff'; g.font = '600 90px Plex'; g.textAlign = 'center'; g.fillText(Array.from({length: 6}, () => GLC[Math.floor(r() * GLC.length)]).join(''), w / 2 + (r() - 0.5) * 60, 160 + r() * 120);
      if (r() < 0.08) { g.fillStyle = '#fff'; g.fillRect(0, 0, w, h); } }
    ledT.needsUpdate = true;
    const c = clkC.getContext('2d'); c.fillStyle = '#050505'; c.fillRect(0, 0, 256, 128); c.fillStyle = '#ff6a2a'; c.font = '500 58px Plex'; c.textAlign = 'center';
    c.fillText(gl ? `${GLC[Math.floor(r() * 30)]}${GLC[Math.floor(r() * 30)]}:${GLC[Math.floor(r() * 10)]}${GLC[Math.floor(r() * 30)]}` : '12:00', 128, 62); c.font = '500 34px Plex'; c.fillText(gl ? `${Math.floor(r() * 900 - 400)} °C` : '31 °C', 128, 108); clkT.needsUpdate = true;
  }
  const sparks = sparkSystem(500, 0.12); scene.add(sparks);
  const glass = sparkSystem(400, 0.07); scene.add(glass);

  // Kamera und Handy
  const camera = new THREE.PerspectiveCamera(48, 1080 / 1920, 0.03, 1500); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#2a2d33'); const hands = makeHands('#d9a47e', '#3a3f48');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig); rig.position.set(0.0, -0.06, -0.26); rig.rotation.set(-0.08, 0.0, 0.02);
  const BANK = 24, MIN_AT = BANK + 2.6; // Banking-App: Kontostand kippt
  function bankApp(g, st, SW, SH) {
    const t = st.T, r = rng(Math.floor(t * 18) + 3);
    g.fillStyle = '#f3f5f9'; g.fillRect(0, 0, SW, SH);
    g.fillStyle = '#0b3d91'; g.fillRect(0, 0, SW, 330);
    g.fillStyle = '#fff'; g.font = '500 24px Plex'; g.textAlign = 'left'; g.fillText('12:00', 40, 52); g.textAlign = 'right'; g.fillText('5G  64%', SW - 40, 52);
    g.textAlign = 'left'; g.font = '500 30px Plex'; g.fillText('Meine Bank', 40, 130); g.font = '400 26px Plex'; g.globalAlpha = 0.8; g.fillText('Girokonto · DE41 •••• 2207', 40, 190); g.globalAlpha = 1;
    g.font = '400 24px Plex'; g.fillText('Kontostand', 40, 250);
    let bal, col = '#fff';
    if (t < BANK + 1.0) bal = '2.341,57 €';
    else if (t < MIN_AT) bal = Array.from({length: 9}, (_, i) => i === 5 ? ',' : GLC[Math.floor(r() * 10)]).join('') + ' €';
    else { bal = '−2.147.483.648,00 €'; col = '#ff5a4f'; }
    g.fillStyle = col; g.font = bal.length > 14 ? '600 46px Plex' : '600 64px Plex'; g.fillText(bal, 40, 310);
    g.fillStyle = '#111'; g.font = '500 28px Plex'; g.fillText('Umsätze', 40, 410);
    const rows = [['REWE Markt', '−23,80'], ['Gehalt', '+2.140,00'], ['Netflix', '−13,99'], ['Miete', '−780,00'], ['Bäckerei', '−4,20'], ['Tankstelle', '−61,37'], ['Spotify', '−10,99']];
    rows.forEach(([n, v], i) => { const y = 480 + i * 105; g.fillStyle = '#fff'; g.fillRect(24, y - 50, SW - 48, 92);
      g.fillStyle = '#222'; g.font = '400 27px Plex'; g.fillText(n, 50, y); let vv = v;
      if (t >= BANK + 1.0) vv = (r() < 0.5 ? '−' : '+') + Array.from({length: 3 + Math.floor(r() * 5)}, () => GLC[Math.floor(r() * 10)]).join('') + ',' + Math.floor(r() * 99);
      g.textAlign = 'right'; g.fillStyle = vv[0] === '+' ? '#16834a' : '#c0392b'; g.fillText(vv + ' €', SW - 50, y); g.textAlign = 'left';
      g.fillStyle = '#888'; g.font = '400 20px Plex'; g.fillText('18.11.', 50, y + 30); });
    if (t >= MIN_AT) { const a = clamp((t - MIN_AT) / 0.3); g.globalAlpha = a; g.fillStyle = 'rgba(20,20,24,0.92)'; g.beginPath(); g.roundRect(40, 820, SW - 80, 250, 30); g.fill();
      g.fillStyle = '#ff5a4f'; g.font = '600 32px Plex'; g.textAlign = 'center'; g.fillText('Konto gesperrt', SW / 2, 900); g.fillStyle = '#fff'; g.font = '400 25px Plex';
      g.fillText('Überziehung festgestellt.', SW / 2, 960); g.fillText('Bitte wende dich an deine Filiale.', SW / 2, 1000); g.globalAlpha = 1; g.textAlign = 'left'; }
    if (st.gl) for (let i = 0; i < 6; i++) { const y = r() * SH; g.drawImage(g.canvas, 0, y, SW, 20, (r() - 0.5) * 40, y, SW, 20); }
  }

  // Positionen
  const PARK = []; // parkende / stehende Autos am Rand und in der Gegenspur
  for (let i = 0; i < 26; i++) { const lane = [-4.8, 4.8][i % 2]; PARK.push([lane, (i % 4 < 2 ? 1 : -1) * (32 + Math.floor(i / 4) * 7.5) + (i % 3), lane > 0 ? Math.PI : 0]); }
  const poses = people.map((_, i) => ({x: (i % 3 ? 1 : -1) * (7.6 + (i * 0.37 % 1) * 3.4), z: i < 16 ? -6 + i * 1.5 : 30 - ((i * 7.3) % 70), ry: (i * 1.7) % 6.28, d: (i * 0.61) % 1}));
  // Unfall: A fährt auf der Hauptstraße Richtung -z, B kommt aus der Querstraße (+x) und rammt A
  const TI = 28.0, PI_ = V3(1.6, 0, -20.5), VA = 14, VB = 15;
  function crashPose(T) {
    const a = {}, b = {};
    if (T < TI) { const d = TI - T; a.x = PI_.x; a.z = PI_.z + VA * d; a.ry = Math.PI; b.x = PI_.x - 3.1 - VB * d; b.z = PI_.z; b.ry = Math.PI / 2; a.roll = 0; b.roll = 0; }
    else { const t = T - TI, k = 2.2, s = (1 - Math.exp(-k * t)) / k; a.x = PI_.x + 7.5 * s * 0.9; a.z = PI_.z - 7 * s; a.ry = Math.PI + 1.7 * s;
      b.x = PI_.x - 3.1 + 7.5 * s; b.z = PI_.z - 6.4 * s; b.ry = Math.PI / 2 - 0.8 * s; a.roll = 0.12 * Math.exp(-t * 5) * Math.sin(t * 25); b.roll = 0.05 * Math.exp(-t * 4); }
    return {a, b};
  }

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id, gl = T >= VANISH && T < RETURN;
    sky.material.uniforms.day.value = 1; sky.material.uniforms.stars.value = 0;
    sun.intensity = 3.0; hemi.intensity = 1.0; scene.environmentIntensity = 0.6; starLight.intensity = 0;
    scene.fog.color.set('#a9bfd6'); scene.fog.near = 60; scene.fog.far = 420; renderer.toneMappingExposure = 1.0;
    LIT.forEach(m => { m.emissiveIntensity = 0; }); winMats.forEach(m => { m.emissiveIntensity = 0; }); crossM.emissiveIntensity = 1.2;
    city.skyline.forEach(m => m.color.set('#9aa6b3')); blocks.material.color.set('#b8ad9c');
    drawLED(T, gl);
    sm.visible = false; dots.visible = false; fireLight.intensity = 0; updateParticles(fire, [], T); updateParticles(smoke, [], T);
    // Autos
    cars.forEach((c, i) => { const [x, z, ry] = PARK[i]; c.position.set(x, 0, z); c.rotation.set(0, ry, 0); c.userData.body.rotation.set(0, 0, 0); c.visible = true; });
    const {a, b} = crashPose(T);
    cars[0].position.set(a.x, 0, a.z); cars[0].rotation.y = a.ry; cars[0].userData.body.rotation.z = a.roll;
    cars[1].position.set(b.x, 0, b.z); cars[1].rotation.y = b.ry; cars[1].userData.body.rotation.z = b.roll;
    // Gegenverkehr: knapp vorbei
    cars[2].position.set(-1.6, 0, -60 + 15 * (T - 24)); cars[2].rotation.y = 0;
    cars[3].position.set(-40 + 13 * (T - 24) - (T > 27 ? 0 : 0), 0, -26.2); cars[3].rotation.y = Math.PI / 2; // zweites Auto aus der Querstraße
    if (T > 28.6) { const tt = T - 28.6; const s = (1 - Math.exp(-3 * tt)) / 3; cars[3].position.x = -40 + 13 * 4.6 + 13 * s; } // bremst
    cars[25].position.set(-4.8, 0, 60); cars[25].userData.blue.forEach(bb => bb.material.emissiveIntensity = 0); blue.intensity = 0;
    const crash = id === 'crossing' && T > TI;
    shardG.visible = crash; const blink = Math.sin(T * 9) > 0;
    haz.forEach((h, k) => { const c = cars[k >> 2]; const corner = V3((k & 1 ? 0.75 : -0.75), 0.75, (k & 2 ? 2.15 : -2.15)).applyAxisAngle(V3(0, 1, 0), c.rotation.y).add(c.position); h.position.copy(corner); h.visible = crash && blink && T > TI + 1.2; });
    updateParticles(steamS, crash ? [{type: 'smoke', pos: V3(cars[1].position.x + 2, 0.9, cars[1].position.z), r: 0.4, t0: TI + 0.3, size: 1.1, rise: 0.7, col: [0.75, 0.75, 0.75], alpha: 0.2, share: 1}] : [], T, V3(0.4, 0, 0.3));
    const ip = V3(PI_.x - 0.9, 0.8, PI_.z);
    updateSparks(sparks, [{pos: ip, dir: V3(0.6, 0.3, -0.5), t0: TI, t1: TI + 0.15}], id === 'crossing' ? T : -99);
    updateSparks(glass, [{pos: ip.clone().add(V3(0, 0.3, 0)), dir: V3(0.7, 0.5, -0.4), t0: TI, t1: TI + 0.25}], id === 'crossing' ? T : -99);
    glass.geometry.attributes.color.array.forEach((v, k, arr) => { if (k % 3 === 2) arr[k] = arr[k - 2]; }); glass.geometry.attributes.color.needsUpdate = true;
    carLights.forEach(l => l.intensity = 0);
    tram.visible = true; tram.position.z = 60;
    // Ampeln: in der Stadt flackern sie wirr, an der Kreuzung zeigen alle Grün
    const rr = rng(Math.floor(T * 6) + 11);
    signals.forEach((lamps, k) => lamps.forEach((m, j) => {
      let on; if (!gl) on = j === (k % 2 ? 0 : 2); else if (id === 'crossing') on = j === 2; else on = rr() < 0.4;
      m.material.emissiveIntensity = on ? 3.2 : 0; }));
    // Menschen mit Handys
    people.forEach((o, i) => {
      const q = poses[i]; const p = o.p; p.visible = true;
      let x = q.x, z = q.z, ry = q.ry;
      if (id === 'crossing') { z = -9 - (i % 8) * 0.9; x = i % 3 ? -(7.6 + (i % 4) * 0.8) : 11.2 + (i % 2) * 0.7; ry = i % 3 ? Math.PI * 0.75 : -Math.PI * 0.8; }
      p.position.set(x, 0.15, z); p.rotation.set(0, ry, 0);
      if (id === 'street' && Math.hypot(x - 8.6, z - (16 - t * 0.5)) < 3.5) p.visible = false;
      posePerson(p, {walk: 0, walkAmp: 0, look: Math.sin(T * 0.6 + i) * 0.3});
      const u = p.userData;
      const hold = q.d < 0.75 ? 1 : 0;
      if (hold) { u.armR.rotation.x = -1.1; u.armR.userData.fore.rotation.x = -0.9; u.head.rotation.x = 0.35; }
      if (id === 'crossing' && T > TI) { const k = smooth(TI + 0.1 + q.d * 0.4, TI + 0.5 + q.d * 0.4, T); u.armL.rotation.x = -2.0 * k; u.armL.userData.fore.rotation.x = -1.4 * k; u.head.rotation.x = 0; u.torso.rotation.y = 0; }
      o.glow.visible = hold === 1;
      o.glow.material.color.setHSL(gl ? rr() : 0.6, gl ? 1 : 0.1, gl ? 0.5 + rr() * 0.4 : 0.92);
      beams[i].material.opacity = 0;
    });
    torches.forEach(l => l.intensity = 0);
    // Kamera
    rig.visible = false; camera.fov = 48;
    if (id === 'street') {
      camera.position.set(8.6, 1.75, 16 - t * 0.5); camera.lookAt(-8, 5.2, -4 - t * 0.3);
    } else if (id === 'crossing') {
      const sh = T > TI ? 0.03 * Math.exp(-(T - TI) * 3) : 0;
      camera.fov = 52; camera.position.set(7.6 + noise1(T * 14, 1) * sh, 1.95 + noise1(T * 14, 2) * sh, -10.5 - t * 0.12); camera.lookAt(-0.5, 1.1, -23);
    } else { // bank: Handy-POV auf dem Gehweg
      rig.visible = true; camera.fov = 52; rig.position.set(0.02, -0.035, -0.3); rig.scale.setScalar(0.8);
      camera.position.set(8.8 + noise1(T * 0.8, 1) * 0.02, 1.62, 12 - t * 0.12); camera.lookAt(1.0, 1.0, -10);
      updateScreen(phone, [], {t: T, T, gl, noDrops: true, custom: bankApp});
    }
    camera.updateProjectionMatrix();
    city.furniture.forEach(f => { f.visible = Math.hypot(f.position.x - camera.position.x, f.position.z - camera.position.z) > 6 || f.position.z > camera.position.z + 1; });
  }};
}
