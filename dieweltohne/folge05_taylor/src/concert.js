// Stadionkonzert bei Nacht: 70.000 Fans, Bühne mit LED-Wand und Laufsteg.
// concert: Mikrofon fällt aus der Luft, die Bühne ist leer, die Band spielt weiter.
// stadium: Luftbild, die Menge drängt nach vorn, die Absperrung bricht.
// comeback: Rückkehr – gleißendes Licht in der Bühnenmitte (sie selbst ist nie zu sehen), Pyro, Feuerwerk, Konfetti, alle springen.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, skyDome, envMap, easeIn} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {MIC_DROP, SURGE, BARRIER, RETURN, JUMP} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const DECK = 2.0;

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#05060c');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.1;
  scene.fog = new THREE.Fog('#0b0b18', 60, 260);
  scene.add(skyDome('#020309', '#0c1030', '#241a3a', 500));
  const hemi = new THREE.HemisphereLight('#4a4c8a', '#100c14', 0.5); scene.add(hemi);
  const r = rng(5);

  // Rasen
  const grassT = canvasTex(512, 512, (g, w, h) => { for (let y = 0; y < h; y += 32) { g.fillStyle = (y / 32) % 2 ? '#1f4a26' : '#245429'; g.fillRect(0, y, w, 32); } });
  grassT.wrapS = grassT.wrapT = THREE.RepeatWrapping; grassT.repeat.set(4, 6);
  const field = mesh(new THREE.PlaneGeometry(90, 120), new THREE.MeshStandardMaterial({map: grassT, roughness: 1}), 0, 0, 38, scene); field.rotation.x = -Math.PI / 2;

  // Tribünen: geneigter Ring um das Feld, besetzt mit Punkten (Zuschauer) und Handylichtern
  const CX = 0, CZ = 38, RX = 46, RZ = 58;
  const ringPos = [], ringIdx = []; const NA = 120, NR = 12;
  for (let i = 0; i <= NA; i++) { const a = i / NA * Math.PI * 2; for (let j = 0; j <= NR; j++) { const k = j / NR, s = 1 + k * 0.55; ringPos.push(CX + Math.cos(a) * RX * s, 1.5 + k * 34, CZ + Math.sin(a) * RZ * s); } }
  for (let i = 0; i < NA; i++) for (let j = 0; j < NR; j++) { const a = i * (NR + 1) + j, b = a + NR + 1; ringIdx.push(a, b, a + 1, b, b + 1, a + 1); }
  const bowlG = new THREE.BufferGeometry(); bowlG.setAttribute('position', new THREE.Float32BufferAttribute(ringPos, 3)); bowlG.setIndex(ringIdx); bowlG.computeVertexNormals();
  scene.add(new THREE.Mesh(bowlG, new THREE.MeshStandardMaterial({color: '#23232c', roughness: 0.9, side: THREE.DoubleSide})));
  const roofG = new THREE.RingGeometry(1, 1, 120, 1); { const p = roofG.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), l = Math.hypot(x, y) || 1, outer = l > 0.99 && i % 2 === 1; const a = Math.atan2(y, x); const s = i < 121 ? 1.5 : 1.62; p.setXYZ(i, CX + Math.cos(a) * RX * s, 36 + (i < 121 ? 0 : 1.5), CZ + Math.sin(a) * RZ * s); } }
  const roof = new THREE.Mesh(roofG, new THREE.MeshStandardMaterial({color: '#15151c', side: THREE.DoubleSide})); scene.add(roof);
  const NS = 26000, seatG = new THREE.BufferGeometry(), seatP = new Float32Array(NS * 3), seatC = new Float32Array(NS * 3), seatBase = [];
  const fanCols = ['#e8e2d4', '#d94b6a', '#7b4fa0', '#3f6fb5', '#e2b23a', '#111', '#f2a0c8', '#5fc7e8'].map(c => new THREE.Color(c));
  for (let i = 0; i < NS; i++) { let a; do { a = r() * Math.PI * 2; } while (Math.sin(a) < -0.55 && Math.abs(Math.cos(a)) < 0.6); const k = 0.03 + r() * 0.92, s = 1 + k * 0.55;
    seatBase.push([CX + Math.cos(a) * RX * s, 1.5 + k * 34 + 0.5, CZ + Math.sin(a) * RZ * s, r()]); const c = fanCols[Math.floor(r() * fanCols.length)]; seatC.set([c.r * 0.5, c.g * 0.5, c.b * 0.5], i * 3); }
  seatG.setAttribute('position', new THREE.BufferAttribute(seatP, 3)); seatG.setAttribute('color', new THREE.BufferAttribute(seatC, 3));
  const seats = new THREE.Points(seatG, new THREE.PointsMaterial({size: 0.55, vertexColors: true})); seats.frustumCulled = false; scene.add(seats);
  const dotT = canvasTex(32, 32, (g, w) => { const gr = g.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.3, 'rgba(255,255,255,0.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });

  // Bühne
  const deckM = mat('#141418', {roughness: 0.4, metalness: 0.3});
  mesh(new THREE.BoxGeometry(40, DECK, 9), deckM, 0, DECK / 2, -4.5, scene);
  mesh(new THREE.BoxGeometry(4, DECK, 22), deckM, 0, DECK / 2, 11, scene);
  const bst = mesh(new THREE.CylinderGeometry(4.5, 4.5, DECK, 40), deckM, 0, DECK / 2, 25, scene);
  const edgeM = new THREE.MeshBasicMaterial({color: '#ff5fb8'});
  mesh(new THREE.BoxGeometry(40, 0.06, 0.06), edgeM, 0, DECK, 0, scene); for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(0.06, 0.06, 22), edgeM, s * 2, DECK, 11, scene);
  // LED-Wand und Seitenbildschirme
  const ledC = document.createElement('canvas'); ledC.width = 1024; ledC.height = 480; const ledT = new THREE.CanvasTexture(ledC); ledT.colorSpace = THREE.SRGBColorSpace;
  const led = mesh(new THREE.PlaneGeometry(28, 13), new THREE.MeshBasicMaterial({map: ledT, toneMapped: false}), 0, DECK + 7, -8.5, scene);
  const RT = new THREE.WebGLRenderTarget(512, 640); RT.texture.colorSpace = THREE.SRGBColorSpace;
  const sideM = new THREE.MeshBasicMaterial({map: RT.texture, toneMapped: false});
  const sides = [-1, 1].map(s => mesh(new THREE.PlaneGeometry(8, 10), sideM, s * 22, DECK + 9, -6, scene)); sides.forEach((m, i) => m.rotation.y = (i ? -1 : 1) * 0.25);
  const liveCam = new THREE.PerspectiveCamera(30, 0.8, 0.5, 200); liveCam.position.set(0, DECK + 1.6, 14); liveCam.lookAt(0, DECK + 1.4, 0);
  // Traversen
  const trussM = mat('#2a2a30', {metalness: 0.8, roughness: 0.4});
  for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(0.6, 22, 0.6), trussM, s * 19.5, 11, -7, scene);
  mesh(new THREE.BoxGeometry(40, 0.8, 0.8), trussM, 0, 20, -5, scene); mesh(new THREE.BoxGeometry(40, 0.6, 0.6), trussM, 0, 18, 0, scene);
  // Mikrofonständer, Mikrofon, Lichtkreis
  const stand = new THREE.Group(); stand.position.set(0, DECK, -0.8); scene.add(stand);
  mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.5, 8), mat('#888', {metalness: 0.9, roughness: 0.3}), 0, 0.75, 0, stand); mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.03, 20), mat('#222', {metalness: 0.7}), 0, 0.015, 0, stand);
  const mic = new THREE.Group(); scene.add(mic); mic.scale.setScalar(1.8);
  mesh(new THREE.CylinderGeometry(0.022, 0.016, 0.18, 12), mat('#d7c27a', {metalness: 0.9, roughness: 0.25}), 0, 0, 0, mic);
  mesh(new THREE.SphereGeometry(0.032, 12, 10), mat('#bbb', {metalness: 0.8, roughness: 0.5}), 0, 0.1, 0, mic);
  const poolT = canvasTex(128, 128, (g, w) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,0.95)'); gr.addColorStop(0.7, 'rgba(255,255,255,0.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const pool = mesh(new THREE.PlaneGeometry(3.2, 3.2), new THREE.MeshBasicMaterial({map: poolT, color: '#fff2e0', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false}), 0, DECK + 0.02, 0.6, scene); pool.rotation.x = -Math.PI / 2;
  const coneT = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0.8)'); gr.addColorStop(1, 'rgba(255,255,255,0.05)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const beam = (col, op) => { const c = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 24, 1, true), new THREE.MeshBasicMaterial({map: coneT, color: col, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide})); c.geometry.translate(0, -0.5, 0); scene.add(c); return c; };
  const aim = (c, from, to, rad) => { const d = to.clone().sub(from); c.position.copy(from); c.quaternion.setFromUnitVectors(V3(0, -1, 0), d.clone().normalize()); c.scale.set(rad, d.length(), rad); };
  const follow = beam('#fff4e2', 0.12); // Verfolger von der Tribüne
  const beams = []; for (let i = 0; i < 10; i++) beams.push({c: beam(['#ff5fb8', '#b46bff', '#5fc7e8', '#ffffff'][i % 4], 0.07), x: -18 + i * 4});
  const stageL = new THREE.SpotLight('#ffd9f0', 900, 60, 0.6, 0.5, 1.4); stageL.position.set(0, 18, 12); stageL.target.position.set(0, DECK, -3); scene.add(stageL, stageL.target);
  for (const x of [-12, -4, 4, 12]) { const pl = new THREE.PointLight('#ffd0f0', 60, 22, 1.3); pl.position.set(x, DECK + 4, 4); scene.add(pl); }
  const followL = new THREE.SpotLight('#fff4e2', 0, 120, 0.05, 0.4, 1.0); followL.position.set(0, 30, 95); followL.target.position.set(0, DECK, 0.6); scene.add(followL, followL.target);
  // Gleißender Lichtpunkt bei der Rückkehr (verdeckt die Bühnenmitte)
  const flareT = canvasTex(256, 256, (g, w) => { const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.12, 'rgba(255,248,235,1)'); gr.addColorStop(0.35, 'rgba(255,220,240,0.45)'); gr.addColorStop(1, 'rgba(255,200,240,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w);
    g.globalCompositeOperation = 'lighter'; g.fillStyle = 'rgba(255,240,255,0.5)'; g.fillRect(0, 124, w, 8); g.fillRect(124, 0, 8, w); });
  const flare = new THREE.Sprite(new THREE.SpriteMaterial({map: flareT, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false})); flare.position.set(0, DECK + 1.1, -0.6); flare.renderOrder = 20; scene.add(flare);

  // Band und Tänzer:innen
  const band = [[-12, -5, 0], [-8, -6.5, 1], [9, -5, 2], [12.5, -5.5, 3]].map(([x, z, k]) => { const p = makePerson(300 + k, {top: '#1b1b20', pants: '#111'}); p.position.set(x, DECK + (k === 1 ? 0.6 : 0), z); p.rotation.y = (x < 0 ? 0.3 : -0.3); scene.add(p); return {p, k}; });
  const drums = new THREE.Group(); drums.position.set(-8, DECK + 0.6, -5.6); scene.add(drums);
  mesh(new THREE.BoxGeometry(3, 0.6, 2.5), mat('#202024'), 0, -0.3, 0, drums); for (const [x, z, rr] of [[-0.6, 0.6, 0.3], [0.6, 0.6, 0.3], [0, 0.3, 0.4]]) mesh(new THREE.CylinderGeometry(rr, rr, 0.35, 20), mat('#c8102e', {metalness: 0.4}), x, 0.5, z, drums);
  const dancers = []; for (let i = 0; i < 8; i++) { const p = makePerson(400 + i, {top: '#e8c96a', pants: '#e8c96a', hair: ['#111', '#5a3b22', '#c9a35b'][i % 3], longHair: i % 2 === 0}); const x = (i - 3.5) * 2.2; p.position.set(x, DECK, -2.5 - (i % 2) * 1.2); scene.add(p); dancers.push({p, x, ph: i * 0.7}); }
  dancers.forEach(d => d.p.traverse(o => { if (o.isMesh && o.material.color && o.material.color.getHexString() === 'e8c96a') o.material = new THREE.MeshStandardMaterial({color: '#e8c96a', metalness: 0.9, roughness: 0.25}); }));

  // Menge im Innenraum (instanziert)
  const N = 9000, bodyI = new THREE.InstancedMesh(new THREE.CapsuleGeometry(0.21, 0.75, 3, 8), new THREE.MeshStandardMaterial({roughness: 0.8}), N);
  const headI = new THREE.InstancedMesh(new THREE.SphereGeometry(0.12, 10, 8), new THREE.MeshStandardMaterial({roughness: 0.7}), N);
  const fans = []; const skin = ['#f1c7a5', '#d9a47e', '#a8714f', '#7a4d33'].map(c => new THREE.Color(c)), hairC = ['#2a1d15', '#5a3b22', '#c9a35b', '#111'].map(c => new THREE.Color(c));
  while (fans.length < N) { const x = (r() - 0.5) * 66, z = 2.2 + r() * 70; if (Math.abs(x) < 3.2 && z < 28) continue; if (Math.hypot(x, z - 25) < 5.6) continue; if (z > 62 && Math.abs(x) > 26) continue; if (x > 2.6 && x < 8.0 && z > 10.4 && z < 16.5) continue;
    fans.push({x, z, ph: r() * 6, h: 0.9 + r() * 0.2, phone: r() < 0.35, lag: r()}); }
  const tc = new THREE.Color(); fans.forEach((f, i) => { bodyI.setColorAt(i, tc.copy(fanCols[i % fanCols.length]).multiplyScalar(0.8)); headI.setColorAt(i, r() < 0.6 ? hairC[i % 4] : skin[i % 4]); });
  bodyI.frustumCulled = headI.frustumCulled = false; scene.add(bodyI, headI);
  const phoneIdx = fans.map((f, i) => f.phone ? i : -1).filter(i => i >= 0);
  const phG = new THREE.BufferGeometry(), phP = new Float32Array(phoneIdx.length * 3); phG.setAttribute('position', new THREE.BufferAttribute(phP, 3));
  const phones = new THREE.Points(phG, new THREE.PointsMaterial({map: dotT, size: 0.5, color: '#eaf2ff', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})); phones.frustumCulled = false; scene.add(phones);
  const stG = new THREE.BufferGeometry(), stIdx = []; for (let i = 0; i < NS; i += 6) stIdx.push(i); const stP = new Float32Array(stIdx.length * 3); stG.setAttribute('position', new THREE.BufferAttribute(stP, 3));
  const stPhones = new THREE.Points(stG, new THREE.PointsMaterial({map: dotT, size: 0.9, color: '#eaf2ff', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})); stPhones.frustumCulled = false; scene.add(stPhones);
  // Absperrgitter vor der Bühne
  const barrier = []; for (let i = 0; i < 16; i++) { const g = new THREE.Group(); g.position.set(-15 + i * 2, 0, 1.3); scene.add(g); mesh(new THREE.BoxGeometry(1.95, 1.15, 0.08), mat('#9aa0a8', {metalness: 0.8, roughness: 0.35}), 0, 0.58, 0, g); barrier.push({g, k: r()}); }
  // Fans im Vordergrund (detailliert)
  const front = []; for (let i = 0; i < 14; i++) { const p = makePerson(600 + i, {longHair: i % 2 === 0}); const x = 3.0 + (i % 5) * 0.95 + (r() - 0.5) * 0.3, z = 10.9 + Math.floor(i / 5) * 0.8 + (r() - 0.5) * 0.3; p.position.set(x, 0, z); p.rotation.y = Math.PI + (r() - 0.5) * 0.4; scene.add(p); front.push({p, x, z, ph: r() * 6, up: i % 3 !== 0}); }

  // Pyro, Feuerwerk, Konfetti
  const fire = particles(1600, 'fire'); scene.add(fire); const smoke = particles(500, 'smoke'); scene.add(smoke);
  const NB = 14, PB = 160, fwG = new THREE.BufferGeometry(), fwP = new Float32Array(NB * PB * 3), fwC = new Float32Array(NB * PB * 3);
  fwG.setAttribute('position', new THREE.BufferAttribute(fwP, 3)); fwG.setAttribute('color', new THREE.BufferAttribute(fwC, 3));
  const fw = new THREE.Points(fwG, new THREE.PointsMaterial({map: dotT, size: 1.3, vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})); fw.frustumCulled = false; scene.add(fw);
  const bursts = Array.from({length: NB}, (_, k) => ({t0: RETURN + 0.6 + k * 0.6 + r() * 0.3, p: V3((r() - 0.5) * 50, 30 + r() * 25, -10 + r() * 20), col: new THREE.Color().setHSL(r(), 0.9, 0.65), dirs: Array.from({length: PB}, () => { const v = V3(r() - 0.5, r() - 0.5, r() - 0.5).normalize(); return [v, 0.8 + r() * 0.4]; })}));
  const NC = 2500, confI = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.09, 0.05), new THREE.MeshBasicMaterial({side: THREE.DoubleSide}), NC); confI.frustumCulled = false; scene.add(confI);
  const conf = Array.from({length: NC}, (_, i) => { confI.setColorAt(i, new THREE.Color().setHSL(r(), 0.85, 0.65)); return {x: (r() - 0.5) * 40, z: -2 + r() * 40, t0: RETURN + 0.4 + r() * 1.2, v: 1.0 + r() * 1.2, ph: r() * 6, y0: 22 + r() * 8}; });

  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s3 = V3(1, 1, 1), p3 = V3(0, 0, 0), e3 = new THREE.Euler();
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.1, 900);

  function drawLED(T, mode) {
    const g = ledC.getContext('2d'), w = 1024, h = 480;
    if (mode === 'show') { const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, '#ff5fb8'); gr.addColorStop(0.5, '#7b3fe0'); gr.addColorStop(1, '#3fc8ff'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      const rr = rng(3); for (let i = 0; i < 160; i++) { g.fillStyle = `rgba(255,255,255,${Math.abs(Math.sin(T * 3 + i))})`; g.beginPath(); g.arc(rr() * w, rr() * h, 1 + rr() * 4, 0, 7); g.fill(); } }
    else if (mode === 'empty') { g.fillStyle = '#05050a'; g.fillRect(0, 0, w, h); const rr = rng(Math.floor(T * 15)); for (let i = 0; i < 1500; i++) { const v = rr() * 60; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(rr() * w, rr() * h, 3, 3); }
      g.fillStyle = Math.sin(T * 5) > 0 ? '#ff4d6a' : '#ff8fa0'; g.font = '500 44px Plex'; g.textAlign = 'center'; g.fillText('KEIN SIGNAL', w / 2, h / 2 + 16); }
    else { const k = (T * 0.8) % 1; const gr = g.createRadialGradient(w / 2, h / 2, 10, w / 2, h / 2, w * 0.7); gr.addColorStop(0, '#ffffff'); gr.addColorStop(0.3, '#ffd1ec'); gr.addColorStop(1, '#ff5fb8'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      g.fillStyle = '#7b2a6a'; g.font = '500 120px Garamond'; g.textAlign = 'center'; g.fillText('WELCOME BACK', w / 2, h / 2 + 40); }
    ledT.needsUpdate = true;
  }

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.0;
    const id = shot.id, t = T - shot.t0, back = id === 'comeback';
    const surge = id === 'stadium' ? smooth(SURGE, SURGE + 4.5, T) : 0, brk = id === 'stadium' ? smooth(BARRIER, BARRIER + 0.8, T) : 0;
    const jump = back ? smooth(JUMP - 0.3, JUMP, T) : 0, flash = back ? smooth(RETURN, RETURN + 0.25, T) * (1 - 0.5 * smooth(RETURN + 1.5, RETURN + 4, T)) : 0;
    // LED / Seitenbildschirme
    drawLED(T, back && T > RETURN + 0.2 ? 'back' : 'empty');
    led.visible = false; sides.forEach(m => m.visible = false); flare.visible = false; renderer.setRenderTarget(RT); renderer.render(scene, liveCam); renderer.setRenderTarget(null); led.visible = true; sides.forEach(m => m.visible = true);
    // Licht
    stageL.intensity = back ? 900 + 1500 * flash : 700; stageL.color.set(back ? '#fff0f8' : '#d9c8ff');
    followL.intensity = (back ? 5000 * flash : 2500); pool.material.opacity = back ? 1 : 0.8;
    aim(follow, V3(0, 32, 95), V3(0, DECK, 0.6), 1.1); follow.material.opacity = back ? 0.12 + 0.15 * flash : 0.1;
    flare.visible = back && T > RETURN - 0.05; flare.scale.setScalar(4 + 14 * flash + Math.sin(T * 9) * 0.3); flare.material.opacity = clamp(flash * 1.2);
    beams.forEach((b, i) => { const sw = Math.sin(T * (back ? 1.6 : 0.5) + i) * 0.6; aim(b.c, V3(b.x, 19.5, -5), V3(b.x + Math.sin(sw) * 25, 90, 10 + Math.cos(sw + i) * 25), 5); b.c.material.opacity = back ? 0.09 : 0.05; });
    hemi.intensity = back ? 0.5 + 0.8 * flash : 0.5;
    // Mikrofon fällt (concert), liegt dann
    if (id === 'concert' && T < MIC_DROP) { const k = clamp((T - 24.0) / (MIC_DROP - 24.0)); mic.position.set(0.2, DECK + 1.45 - 1.4 * k * k, -0.4); mic.rotation.set(0, 0, 0.3 + k * 1.2); }
    else if (!back) { const d = T - MIC_DROP; const roll = id === 'concert' ? Math.min(d, 1.5) : 1.5; mic.position.set(0.2 + roll * 0.25, DECK + 0.03 + Math.abs(Math.sin(Math.min(d, 0.5) * 9)) * 0.12 * Math.exp(-d * 6), -0.4 + roll * 0.1); mic.rotation.set(0, roll * 1.5, Math.PI / 2); }
    else { mic.position.set(0, -5, 0); }
    // Band spielt weiter, Tänzer:innen halten an und schauen sich um
    band.forEach(({p, k}) => { posePerson(p, {}); const u = p.userData, b = T * 8 + k; u.armR.rotation.x = -0.9 + Math.sin(b) * 0.15; u.armL.rotation.x = -0.7; u.armL.userData.fore.rotation.x = -1.0; u.head.rotation.x = 0.1 * Math.abs(Math.sin(T * 4.3));
      if (k === 1) { u.armL.rotation.x = -1.1 + Math.abs(Math.sin(b)) * 0.4; u.armR.rotation.x = -1.1 + Math.abs(Math.cos(b)) * 0.4; } });
    dancers.forEach(d => { const p = d.p, u = p.userData; const dance = back ? 1 : 1 - smooth(24.6, 25.3, T); posePerson(p, {armsUp: (0.5 + 0.4 * Math.sin(T * 4.4 + d.ph)) * dance});
      p.position.y = DECK + 0.08 * Math.abs(Math.sin(T * 4.4 + d.ph)) * dance; p.rotation.y = 0;
      if (dance < 1) { u.head.rotation.y = Math.sin(T * 1.3 + d.ph) * 0.7 * (1 - dance); p.rotation.y = (d.x > 0 ? -1 : 1) * 0.6 * (1 - dance); if (d.ph > 2.5) { u.armL.rotation.x = -0.5; u.armL.userData.fore.rotation.x = -1.6; } } });
    // Menge
    const zMin = lerp(2.2, 0.6, brk);
    fans.forEach((f, i) => {
      let z = f.z, x = f.x, y = 0;
      if (surge > 0) { const dz = (f.z - 2.2); z = Math.max(zMin + (f.lag * 0.4), 2.2 + dz * lerp(1, 0.55, surge * (0.85 + f.lag * 0.15)) - 1.6 * brk * Math.exp(-dz * 0.1)); x = f.x * lerp(1, 0.92, surge) + noise1(T * 2 + f.ph, i) * 0.12 * surge; }
      if (back) y = jump * 0.38 * Math.abs(Math.sin((T - JUMP) * Math.PI * 2.1 + f.lag * 0.4)); else if (id === 'concert') y = 0;
      p3.set(x, y + 0.6 * f.h, z); s3.set(f.h, f.h, f.h); m4.compose(p3, q, s3); bodyI.setMatrixAt(i, m4);
      p3.set(x, y + 1.45 * f.h, z); m4.compose(p3, q, s3); headI.setMatrixAt(i, m4);
    });
    bodyI.instanceMatrix.needsUpdate = true; headI.instanceMatrix.needsUpdate = true;
    phoneIdx.forEach((fi, k) => { const m = bodyI; m.getMatrixAt(fi, m4); p3.setFromMatrixPosition(m4); const on = back || id === 'concert' ? 1 : 0.6; phP[k * 3] = p3.x + 0.15; phP[k * 3 + 1] = (on > 0.7 ? p3.y + 1.45 : p3.y + 0.6); phP[k * 3 + 2] = p3.z; });
    phG.attributes.position.needsUpdate = true; phones.material.opacity = id === 'stadium' ? 0.35 : 0.9;
    for (let i = 0; i < NS; i++) { const b = seatBase[i]; const yy = back ? jump * 0.3 * Math.abs(Math.sin((T - JUMP) * Math.PI * 2.1 + b[3])) : 0; seatP[i * 3] = b[0]; seatP[i * 3 + 1] = b[1] + yy; seatP[i * 3 + 2] = b[2]; }
    seatG.attributes.position.needsUpdate = true;
    stIdx.forEach((si, k) => { const b = seatBase[si]; const tw = (Math.sin(T * 2 + b[3] * 50) > -0.2) ? 1 : 0; stP[k * 3] = b[0]; stP[k * 3 + 1] = b[1] + 0.8 + (tw ? 0 : -50); stP[k * 3 + 2] = b[2]; });
    stG.attributes.position.needsUpdate = true;
    barrier.forEach(b => { const k = clamp((brk - b.k * 0.4) / 0.6); b.g.rotation.x = -1.45 * easeIn(k); b.g.position.z = 1.3 - 0.4 * k; });
    front.forEach(fp => { const p = fp.p, u = p.userData; posePerson(p, {holdUp: fp.up && !back ? 1 : 0});
      p.position.set(fp.x, back ? jump * 0.35 * Math.abs(Math.sin((T - JUMP) * Math.PI * 2.1 + fp.ph * 0.1)) : 0, fp.z);
      if (id === 'concert') { const conf2 = smooth(25.0, 26.0, T); if (!fp.up) { u.armL.rotation.x = -2.6 * conf2; u.armR.rotation.x = -2.6 * conf2; u.armL.userData.fore.rotation.x = -1.9 * conf2; u.armR.userData.fore.rotation.x = -1.9 * conf2; } u.head.rotation.y = Math.sin(T * 0.9 + fp.ph) * 0.4 * conf2; }
      if (back) { u.armL.rotation.z = -2.6 * jump; u.armR.rotation.z = 2.6 * jump; } });
    // Pyro / Feuerwerk / Konfetti
    const src = [];
    if (back) { for (let i = 0; i < 8; i++) { const x = -17 + i * 4.85; src.push({type: 'flame', pos: V3(x, DECK + 0.2, -0.3), r: 0.35, t0: RETURN + 0.3, t1: RETURN + 1.6, size: 2.6, rise: 9, power: 1.2});
        src.push({type: 'flame', pos: V3(x, DECK + 0.2, -0.3), r: 0.35, t0: JUMP + 2.0, t1: JUMP + 2.8, size: 2.6, rise: 9, power: 1.2}); } }
    updateParticles(fire, src, T); updateParticles(smoke, back ? [{type: 'smoke', pos: V3(0, DECK + 6, -2), r: 16, t0: RETURN + 0.5, size: 6, rise: 1.2, alpha: 0.18, col: [0.5, 0.45, 0.6], share: 1}] : [], T, V3(0.4, 0, 0.6));
    bursts.forEach((b, k) => { const age = T - b.t0; const on = back && age > 0 && age < 2.6; for (let j = 0; j < PB; j++) { const o = (k * PB + j) * 3; if (!on) { fwP[o + 1] = -999; continue; }
      const [d, v] = b.dirs[j]; const R = 14 * v * (1 - Math.exp(-age * 2.2)); fwP[o] = b.p.x + d.x * R; fwP[o + 1] = b.p.y + d.y * R - 2.2 * age * age; fwP[o + 2] = b.p.z + d.z * R;
      const f = clamp(1 - age / 2.6) * (0.6 + 0.4 * Math.sin(age * 30 + j)); fwC[o] = b.col.r * f; fwC[o + 1] = b.col.g * f; fwC[o + 2] = b.col.b * f; } });
    fwG.attributes.position.needsUpdate = true; fwG.attributes.color.needsUpdate = true;
    conf.forEach((c, i) => { const a = T - c.t0; if (!back || a < 0) { m4.makeScale(0, 0, 0); confI.setMatrixAt(i, m4); return; }
      const y = Math.max(0.05, c.y0 - a * c.v * 2.2); p3.set(c.x + Math.sin(a * 2 + c.ph) * 0.6, y, c.z + Math.cos(a * 1.7 + c.ph) * 0.4); e3.set(a * 5 + c.ph, a * 3, c.ph); q.setFromEuler(e3); s3.setScalar(y > 0.06 ? 1.6 : 1.2); m4.compose(p3, q, s3); confI.setMatrixAt(i, m4); });
    confI.instanceMatrix.needsUpdate = true; q.identity();
    // Kamera
    camera.fov = 50;
    if (id === 'concert') { const u = smooth(0, 8, t); camera.position.set(lerp(5.6, 4.8, u), lerp(2.7, 2.6, u), lerp(15.5, 13.6, u)); camera.lookAt(lerp(0.6, 0.0, u), lerp(4.0, 3.2, u), -1); }
    else if (id === 'stadium') { const u = smooth(0, 8, t), sh = noise1(T * 9, 2) * 0.15 * surge; camera.fov = 55; camera.position.set(lerp(38, 30, u) + sh, lerp(46, 38, u), lerp(92, 80, u)); camera.lookAt(lerp(2, 0, u), 0, lerp(26, 18, u)); }
    else { const u = smooth(0, 9, t), sh = (noise1(T * 14, 5) * 0.06 + noise1(T * 23, 7) * 0.04) * jump; camera.fov = 52; camera.position.set(lerp(5.5, 2.5, u) + sh, lerp(2.4, 11, u) + sh, lerp(26, 52, u)); camera.lookAt(0, lerp(6.5, 7, u), 0); }
    camera.updateProjectionMatrix();
  }};
}
