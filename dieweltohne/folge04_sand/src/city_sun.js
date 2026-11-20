// Innenstadt nach der Rückkehr des Sands: Glas, Beton und Chips sind nur noch Sand. Häuser zerfließen zu Sandhaufen, Luftbild der Wüstenstadt, Handy zerrinnt in der Hand.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, easeOut, noise1, canvasTex, tileTex, asphaltTex, makePerson, posePerson, makeCar} from './lib.js';
import {decorateBuilding, addStreetFurniture, LIT} from './city.js';
import {skyMaterial} from './beach.js';
import {makePhone, makeHands, updateScreen} from './phone.js';
import {particles, updateParticles, flicker} from './fx.js';
import {VANISH, RETURN, CRUMBLE} from './timeline.js';
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
    g.fillStyle = '#17130f'; g.fillRect(x, y, ww, hh); g.fillStyle = 'rgba(210,180,130,0.5)'; g.fillRect(x, y + hh - 6, ww, 6); // leere Fensterlöcher, Sand auf der Brüstung
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
  const r = rng(5); const winMats = []; const bldgs = [];
  const cols = ['#d8cbb2', '#c9b79c', '#e2d9c8', '#b9a48a', '#cfc2ad', '#a89a8a', '#d6c3a5', '#e0d2bc'];
  for (const s of [-1, 1]) {
    let z = -200;
    while (z < 200) {
      const w = 9 + r() * 7, h = 12 + r() * 16, d = 12;
      if (z + w > CROSS[0] - 1 && z < CROSS[1] + 1) { z = CROSS[1] + 1; continue; }
      const c = cols[Math.floor(r() * cols.length)];
      const {map, emis} = facade(c, Math.floor(r() * 1000), Math.round(h / 3.3), Math.round(w / 3));
      const fm = new THREE.MeshStandardMaterial({map, emissiveMap: emis, emissive: '#ffffff', emissiveIntensity: 0, roughness: 0.85}); winMats.push(fm);
      const n0 = scene.children.length;
      const bm = mesh(new THREE.BoxGeometry(d, h, w), [fm, fm, mat('#6d6a66'), mat(c), mat(c), mat(c)], s * (11.5 + d / 2), h / 2, z + w / 2, scene);
      bm.geometry.translate(0, h / 2, 0); bm.position.y = 0;
      decorateBuilding(scene, s, z, w, h, d, r);
      mesh(new THREE.BoxGeometry(d + 0.6, 0.5, w + 0.2), mat('#7d7368'), s * (11.5 + d / 2) - s * 0.3, h + 0.25, z + w / 2, scene);
      bldgs.push({bm, deco: scene.children.slice(n0 + 1), s, z, w, h, d, delay: r() * 1.6});
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

  // Sandhaufen: wachsen dort, wo Häuser standen
  const sandT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#d2b582'; g.fillRect(0, 0, w, h); const q = rng(3); for (let i = 0; i < 6000; i++) { g.fillStyle = `rgba(${q() < 0.5 ? '120,95,60' : '250,235,200'},${q() * 0.25})`; g.fillRect(q() * w, q() * h, 1 + q() * 2, 1 + q() * 2); } });
  sandT.wrapS = sandT.wrapT = THREE.RepeatWrapping; sandT.repeat.set(3, 3);
  const sandM = new THREE.MeshStandardMaterial({map: sandT, roughness: 1, color: '#e6cf9f'});
  // Schüttkegel: gerade Flanken, oben leicht gerundet, unten flach auslaufend
  const prof = []; for (let i = 0; i <= 16; i++) { const rr = i / 16; prof.push(new THREE.Vector2(rr, Math.max(0, Math.pow(1 - rr, 1.35) * (1 - 0.25 * Math.exp(-rr * 12)) + 0.02 * Math.sin(rr * 9)))); }
  prof.reverse(); const heapGeo = new THREE.LatheGeometry(prof, 36); heapGeo.computeVertexNormals();
  bldgs.forEach(b => { b.heap = mesh(heapGeo, sandM, b.bm.position.x - b.s * 1.5, 0, b.z + b.w / 2, scene); b.heap.scale.set(0.01, 0.01, 0.01); b.heap.castShadow = b.heap.receiveShadow = true;
    // Bewehrungsstahl und Stahlträger bleiben stehen
    const rq = rng(Math.floor(b.z * 13 + b.s * 7) + 999); b.rebar = new THREE.Group(); scene.add(b.rebar);
    for (let k = 0; k < 14; k++) { const L = b.h * (0.25 + rq() * 0.5); const bar = mesh(new THREE.CylinderGeometry(0.03, 0.03, L, 5), mat('#4a3426', {metalness: 0.6, roughness: 0.7}), b.bm.position.x + (rq() - 0.5) * b.d * 0.7, L / 2, b.z + rq() * b.w, b.rebar); bar.rotation.set((rq() - 0.5) * 0.5, 0, (rq() - 0.5) * 0.5); }
    b.rebar.visible = false; });
  const blockHeaps = new THREE.InstancedMesh(heapGeo, sandM, 900); blockHeaps.count = blocks.count; blockHeaps.castShadow = blockHeaps.receiveShadow = true; scene.add(blockHeaps);
  { const m = new THREE.Matrix4(), p = new THREE.Vector3(), q = new THREE.Quaternion(), sc = new THREE.Vector3();
    for (let i = 0; i < blocks.count; i++) { blocks.getMatrixAt(i, m); m.decompose(p, q, sc); m.compose(p, q, V3(sc.x * 0.75, sc.y * 0.3, sc.z * 0.7)); blockHeaps.setMatrixAt(i, m); } }
  const sandify = sys => { Object.assign(sys.material, {blending: THREE.NormalBlending, vertexColors: false, depthWrite: true, alphaTest: 0.4}); sys.material.color.set('#cfb07a'); sys.material.needsUpdate = true; return sys; };
  const desert = mesh(new THREE.PlaneGeometry(1600, 1600), new THREE.MeshStandardMaterial({map: sandT, roughness: 1, color: '#d9c091'}), 0, -0.03, -100, scene); desert.rotation.x = -Math.PI / 2; desert.receiveShadow = true;
  sandT.repeat.set(3, 3);
  // Düne über der Straße (nur Schlusseinstellung): Die Straße endet im Sand
  const driftGeo = new THREE.PlaneGeometry(90, 260, 90, 130); driftGeo.rotateX(-Math.PI / 2);
  { const pa = driftGeo.attributes.position; for (let i = 0; i < pa.count; i++) { const x = pa.getX(i), z = pa.getZ(i) - 130;
      const rise = THREE.MathUtils.smoothstep(-z, 0, 20); const edge = 1 - THREE.MathUtils.smoothstep(Math.abs(x), 30, 45);
      const h = rise * (5.5 + 1.8 * Math.sin(z * 0.11 + x * 0.07) + 0.8 * Math.sin(x * 0.23 - z * 0.05)) * edge;
      pa.setXYZ(i, x, h - 0.2 * (1 - rise), z); } driftGeo.computeVertexNormals(); }
  const drift = new THREE.Mesh(driftGeo, new THREE.MeshStandardMaterial({map: sandT, roughness: 1, color: '#c8a46c'})); drift.position.set(0, 0, -24); drift.receiveShadow = true; drift.castShadow = true; scene.add(drift);
  const ledBox = scene.children.find(o => o.isMesh && Math.abs(o.position.x + 10.72) < 0.01 && Math.abs(o.position.y - 7.5) < 0.01);
  const pour = sandify(sparkSystem(2600, 0.16)); scene.add(pour); // Sandströme aus den Fensterlöchern
  const haze = particles(500, 'smoke'); scene.add(haze);
  // Handy zerrinnt: Gehäuse bleibt, Glas und Chip werden Sand
  const grainsS = sandify(sparkSystem(1500, 0.004)); camera.add(grainsS);

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id;
    sky.material.uniforms.day.value = 1; sky.material.uniforms.stars.value = 0;
    sun.intensity = 2.6; hemi.intensity = 1.0; scene.environmentIntensity = 0.5; starLight.intensity = 0; renderer.toneMappingExposure = 1.0;
    LIT.forEach(m => { m.emissiveIntensity = 0; }); winMats.forEach(m => { m.emissiveIntensity = 0; }); crossM.emissiveIntensity = 0;
    const dustK = smooth(CRUMBLE, CRUMBLE + 3, T);
    scene.fog.color.set('#cdb48c'); scene.fog.near = lerp(60, 15, dustK); scene.fog.far = lerp(420, id === 'aerial' ? 700 : 240, dustK);
    city.skyline.forEach(m => { m.color.set('#cdb48c'); }); city.skyline.forEach(m => { if (m.transparent !== undefined) m.visible = id === 'sandcity'; });
    sm.visible = false; dots.visible = false; fireLight.intensity = 0; updateParticles(fire, [], T); updateParticles(smoke, [], T);
    led.visible = false; clk.visible = false; shardG.visible = false; haz.forEach(h => h.visible = false); updateParticles(steamS, [], T);
    updateSparks(sparks, [], -99); updateSparks(glass, [], -99);
    // Häuser zerfließen ab CRUMBLE zu Sand (gestaffelt)
    bldgs.forEach(b => { const k = smooth(CRUMBLE + b.delay, CRUMBLE + b.delay + 2.2, T);
      b.bm.scale.y = Math.max(0.001, 1 - k); b.bm.visible = k < 0.999; b.deco.forEach(o => o.visible = k < 0.15);
      const hh = b.h * 0.42 * Math.pow(k, 0.8); b.heap.scale.set(b.d * 0.55 + b.d * 0.3 * k, Math.max(0.01, hh), b.w * 0.62); b.rebar.visible = k > 0.5; });
    desert.visible = id === 'aerial'; drift.visible = id === 'hand'; if (ledBox) ledBox.visible = false;
    blocks.visible = id !== 'aerial'; blockHeaps.visible = id === 'aerial' || dustK > 0.9;
    hosp.visible = false;
    // Sand rieselt aus den Fensterlöchern (Häuser in Kameranähe)
    const em = [];
    bldgs.forEach(b => { if (Math.abs(b.z + b.w / 2 - camera.position.z) < 60 && T > CRUMBLE + b.delay - 0.5 && T < CRUMBLE + b.delay + 2.0) for (let f = 1; f < 4; f++) em.push({pos: V3(b.s * 11.4, b.h * (1 - smooth(CRUMBLE + b.delay, CRUMBLE + b.delay + 2.2, T)) * f / 4, b.z + b.w / 2), dir: V3(-b.s * 0.4, 0, 0), t0: CRUMBLE + b.delay - 0.5, t1: CRUMBLE + b.delay + 2.0}); });
    updateSparks(pour, em.slice(0, 26), id === 'sandcity' ? T : -99, 9.8);
    updateParticles(haze, dustK > 0 ? [{type: 'smoke', pos: V3(0, 3, camera.position.z - 30), r: 30, t0: CRUMBLE, size: 14, rise: 1.2, col: [0.78, 0.68, 0.52], alpha: 0.18 * dustK, share: 1}] : [], T, V3(1.5, 0, 0.5));
    // Autos stehen, Straßenbahn steht
    cars.forEach((c, i) => { const [x, z, ry] = PARK[i]; c.position.set(x, 0, z); c.rotation.set(0, ry, 0); c.visible = true; c.userData.body.rotation.set(0, 0, 0); });
    cars[25].userData.blue.forEach(bb => bb.material.emissiveIntensity = 0); blue.intensity = 0; carLights.forEach(l => l.intensity = 0);
    tram.visible = true; tram.position.z = -20;
    signals.forEach(lamps => lamps.forEach(m => m.material.emissiveIntensity = 0));
    // Menschen: schauen hoch, halten sich dann Arm vor Mund und Nase
    people.forEach((o, i) => { const q = poses[i]; const p = o.p; p.visible = true;
      p.position.set(q.x, 0.15, q.z); p.rotation.set(0, q.ry, 0); posePerson(p, {look: Math.sin(T * 0.5 + i) * 0.3});
      const u = p.userData, cough = smooth(CRUMBLE + 1 + q.d, CRUMBLE + 1.6 + q.d, T);
      u.head.rotation.x = -0.4 * (1 - cough); u.armL.rotation.x = -2.0 * cough; u.armL.userData.fore.rotation.x = -1.8 * cough;
      o.glow.visible = false; beams[i].material.opacity = 0; });
    torches.forEach(l => l.intensity = 0);
    // Kamera
    rig.visible = false; grainsS.visible = false; camera.fov = 50;
    if (id === 'sandcity') {
      camera.position.set(5.0 + noise1(T * 3, 1) * 0.02, 1.7, 26 - t * 0.5); camera.lookAt(-11, lerp(9, 4, smooth(57, 66, T)), 2 - t * 0.5);
    } else if (id === 'aerial') {
      const u = smooth(0, 12, t);
      camera.position.set(lerp(18, 30, u), lerp(38, 110, u), lerp(70, 140, u)); camera.lookAt(lerp(0, -10, u), 0, lerp(-10, -180, u));
    } else { // hand: Handy zerrinnt in der Hand
      rig.visible = true; grainsS.visible = false; camera.fov = 52;
      const lift = smooth(5, 9.0, t);
      camera.position.set(6.5, 1.62, 10 - t * 0.1); camera.lookAt(lerp(4, 2, lift), lerp(0.6, 2.2, lift), lerp(4, -40, lift));
      const k = smooth(1.0, 6.5, t);
      rig.scale.setScalar(0.8);
      updateScreen(phone, [], {t: T, noDrops: true, custom: (g, st, SW, SH) => { // Display ist Sand und rinnt nach unten weg
        g.fillStyle = '#2a2622'; g.fillRect(0, 0, SW, SH); g.fillStyle = '#3a342c'; for (let y = 80; y < SH; y += 140) g.fillRect(40, y, SW - 80, 60); // Innenleben
        const top = SH * k; const q = rng(7); g.fillStyle = '#cdb07c'; g.fillRect(0, top, SW, SH - top);
        for (let i = 0; i < 2500; i++) { const y = top + q() * (SH - top); g.fillStyle = `rgba(${q() < 0.5 ? '120,95,60' : '250,235,200'},${q() * 0.5})`; g.fillRect(q() * SW, y, 3, 3); } }});
      rig.position.set(0.0, -0.06 - lift * 0.06, -0.3); rig.rotation.set(-0.15 - lift * 0.3, 0, 0.03);
      updateSparks(grainsS, [{pos: V3(0, -0.11 - lift * 0.06, -0.27), dir: V3(0, -0.2, 0), t0: 0.6, t1: 5.5}], t, 0.6);
    }
    camera.updateProjectionMatrix();
    if (id === 'hand') city.furniture.forEach(f => { f.visible = f.position.z < -24 ? false : (Math.hypot(f.position.x - 6.5, f.position.z - 10) > 15 || f.position.z > 11); }); // fest, kein Flackern
    else city.furniture.forEach(f => { f.visible = Math.hypot(f.position.x - camera.position.x, f.position.z - camera.position.z) > 6 || f.position.z > camera.position.z + 1; });
  }};
}
