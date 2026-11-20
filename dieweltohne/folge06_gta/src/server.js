// Stufe 4: Rechenzentrum. Millionen Konsolen fragen gleichzeitig nach ihrem Spiel. Die Server laufen heiß,
// ein Rack fängt Feuer, die Löschanlage flutet den Gang mit Löschgas.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, envMap, sparkSystem, updateSparks} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {OVERHEAT, FIRE, GAS} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const SURGE = 31.8;

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#06080c');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.25;
  const hemi = new THREE.HemisphereLight('#a8c4ff', '#202428', 0.5); scene.add(hemi);
  const strips = []; for (let z = 2; z > -26; z -= 4) { const l = new THREE.PointLight('#d8e6ff', 3, 7, 1.6); l.position.set(0, 3.0, z); scene.add(l); strips.push(l); }
  const reds = []; for (const z of [-4, -12, -20]) { const l = new THREE.PointLight('#ff2020', 0, 9, 1.4); l.position.set(0, 2.9, z); scene.add(l); reds.push(l); }
  const fireL = new THREE.PointLight('#ff7a20', 0, 8, 1.4); fireL.position.set(-1.0, 1.4, -10); scene.add(fireL);
  // Doppelboden mit Lochplatten
  const floorT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#9aa0a8'; g.fillRect(0, 0, w, h); g.strokeStyle = '#5a6068'; g.lineWidth = 4; g.strokeRect(0, 0, w, h);
    g.fillStyle = '#6a7078'; for (let y = 30; y < h - 20; y += 16) for (let x = 30; x < w - 20; x += 16) { g.beginPath(); g.arc(x, y, 3, 0, 7); g.fill(); } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(4, 46);
  const fl = mesh(new THREE.PlaneGeometry(2.4, 28), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.5, metalness: 0.3}), 0, 0, -12, scene); fl.rotation.x = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(12, 30), mat('#1a1d22'), 0, 3.4, -12, scene).rotation.x = Math.PI / 2;
  // Kabeltrassen
  for (const x of [-0.7, 0.7]) { mesh(new THREE.BoxGeometry(0.3, 0.05, 28), mat('#6a6e74', {metalness: 0.6, roughness: 0.5}), x * 1.3, 3.15, -12, scene);
    for (let i = 0; i < 6; i++) mesh(new THREE.CylinderGeometry(0.02, 0.02, 28, 6), mat(['#2a6bd1', '#e5b31b', '#d43a3a', '#2a2a2a'][i % 4]), x * 1.3 - 0.12 + i * 0.05, 3.2, -12, scene).rotation.x = Math.PI / 2; }
  // Löschdüsen
  const nozzles = []; for (let z = -2; z > -24; z -= 3.5) { mesh(new THREE.CylinderGeometry(0.04, 0.06, 0.15, 10), mat('#c8102e'), 0, 3.3, z, scene); nozzles.push(z); }
  // Racks: Türen mit Lochblech, LED-Raster als Canvas (pro Seite eine Textur)
  const rackT = canvasTex(128, 512, (g, w, h) => { g.fillStyle = '#16181c'; g.fillRect(0, 0, w, h); g.fillStyle = '#23262c'; for (let y = 6; y < h; y += 26) g.fillRect(6, y, w - 12, 20);
    g.fillStyle = '#0c0d10'; for (let y = 0; y < h; y += 4) for (let x = 0; x < w; x += 4) if ((x + y) % 8 === 0) g.fillRect(x, y, 2, 2); });
  const rackM = new THREE.MeshStandardMaterial({map: rackT, roughness: 0.6, metalness: 0.5});
  const LC = document.createElement('canvas'); LC.width = 512; LC.height = 128; const ledT = new THREE.CanvasTexture(LC); ledT.magFilter = THREE.NearestFilter;
  const ledM = new THREE.MeshBasicMaterial({map: ledT, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false});
  const racks = [];
  for (const s of [-1, 1]) for (let i = 0; i < 22; i++) {
    const z = 0.5 - i * 1.25, x = s * 1.5;
    const rk = mesh(new THREE.BoxGeometry(0.9, 2.2, 1.2), rackM, x, 1.1, z, scene);
    const leds = mesh(new THREE.PlaneGeometry(1.15, 2.1), ledM, x - s * 0.452, 1.1, z, scene); leds.rotation.y = -s * Math.PI / 2;
    leds.material = ledM.clone(); leds.material.map = ledT; leds.userData.off = i * 0.13 + (s > 0 ? 0.5 : 0);
    // Uniform-Offset über UV-Verschiebung: jedes Rack zeigt einen anderen Ausschnitt
    leds.material.map = ledT.clone(); leds.material.map.needsUpdate = true; leds.material.map.repeat.set(0.5, 1); leds.material.map.offset.set(((i * 37) % 10) / 20, 0); leds.material.map.wrapS = THREE.RepeatWrapping;
    racks.push({rk, leds, s, z, i});
    mesh(new THREE.BoxGeometry(0.92, 0.12, 1.22), mat('#0c0d10'), x, 2.26, z, scene);
  }
  // Monitorwand am Gangende: Anfragen pro Sekunde
  const MC = document.createElement('canvas'); MC.width = 1024; MC.height = 512; const monT = new THREE.CanvasTexture(MC); monT.colorSpace = THREE.SRGBColorSpace;
  mesh(new THREE.PlaneGeometry(2.6, 1.3), new THREE.MeshBasicMaterial({map: monT, toneMapped: false}), 0, 1.9, -27.2, scene);
  mesh(new THREE.BoxGeometry(2.8, 1.5, 0.1), mat('#111'), 0, 1.9, -27.3, scene);
  mesh(new THREE.BoxGeometry(6, 3.4, 0.2), mat('#1a1d22'), 0, 1.7, -27.5, scene);
  // Feuer, Rauch, Löschgas, Funken
  const fire = particles(900, 'flame'), smoke = particles(700, 'smoke'), gas = particles(1500, 'smoke'); scene.add(fire, smoke, gas);
  const sparks = sparkSystem(500, 0.03); scene.add(sparks);
  const FR = racks.find(r => r.s < 0 && r.i === 8);

  function drawLeds(T) {
    const g = LC.getContext('2d'); g.clearRect(0, 0, 512, 128);
    const hot = smooth(OVERHEAT - 1.0, OVERHEAT + 0.5, T), surge = T > SURGE ? 1 : 0;
    for (let y = 0; y < 128; y += 6) for (let x = 0; x < 512; x += 8) {
      const ph = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453, rnd = ph - Math.floor(ph);
      const speed = surge ? 30 : 4; const on = Math.sin(T * speed * (0.5 + rnd) + rnd * 40) > (surge ? -0.6 : 0.3);
      if (!on) continue;
      g.fillStyle = hot > rnd ? (rnd < 0.5 ? '#ff2a1a' : '#ffae1a') : (rnd < 0.7 ? '#36ff7a' : '#3aa8ff'); g.fillRect(x + 2, y + 2, 3, 2);
    }
    ledT.needsUpdate = true; racks.forEach(r => { r.leds.material.map.needsUpdate = true; });
  }
  function drawMon(T) {
    const g = MC.getContext('2d'), w = 1024, h = 512; g.fillStyle = '#05080e'; g.fillRect(0, 0, w, h);
    g.strokeStyle = 'rgba(80,140,255,0.2)'; g.lineWidth = 1; for (let x = 0; x < w; x += 64) { g.beginPath(); g.moveTo(x, 60); g.lineTo(x, h - 40); g.stroke(); } for (let y = 60; y < h - 40; y += 50) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
    const val = x => { const tt = T - (w - x) / 120; const base = 0.2 + 0.05 * Math.sin(tt * 3 + x * 0.05); return tt > SURGE ? Math.min(1.25, base + (tt - SURGE) * 0.6) : base; };
    g.strokeStyle = '#38d1ff'; g.lineWidth = 4; g.beginPath(); for (let x = 0; x < w; x += 4) { const y = h - 40 - val(x) * (h - 120); x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
    g.fillStyle = '#fff'; g.font = '600 34px Plex'; g.textAlign = 'left'; g.fillText('ANFRAGEN PRO SEKUNDE', 24, 44);
    const n = T > SURGE ? Math.min(24.5e6, (T - SURGE) * 9e6) : 31000 + Math.sin(T) * 900; g.textAlign = 'right'; g.fillStyle = T > OVERHEAT ? '#ff3a2a' : '#38d1ff';
    g.fillText(Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.'), w - 24, 44);
    if (T > OVERHEAT && Math.sin(T * 10) > 0) { g.fillStyle = 'rgba(255,30,30,0.85)'; g.fillRect(w / 2 - 300, h / 2 - 50, 600, 100); g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = '600 44px Plex'; g.fillText('ÜBERLASTUNG · KÜHLUNG AUSGEFALLEN', w / 2, h / 2 + 16); }
    monT.needsUpdate = true;
  }

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 200); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    drawLeds(T); drawMon(T);
    const alarm = T > OVERHEAT ? (Math.sin(T * 7) > 0 ? 1 : 0.1) : 0;
    reds.forEach((l, i) => { l.intensity = alarm * 18; });
    strips.forEach((l, i) => { l.intensity = T > OVERHEAT ? (T > FIRE ? 0.8 : 1.6) : 3; });
    // Feuer im Rack links (Funken zuerst)
    const fp = V3(-1.04, 1.3, FR.z);
    updateSparks(sparks, T > FIRE - 0.6 ? [{pos: fp.clone().add(V3(0, 0.4, 0)), dir: V3(1.2, 0.8, 0), t0: FIRE - 0.6, t1: shot.t1}] : [], T, 9.8);
    updateParticles(fire, T > FIRE ? [{type: 'flame', pos: fp, r: 0.3, t0: FIRE, size: 0.45, rise: 1.4, power: 0.6 * smooth(FIRE, FIRE + 0.6, T) * (1 - 0.6 * smooth(GAS + 0.5, GAS + 1.6, T)), share: 1}] : [], T, V3(0.3, 0, 0));
    updateParticles(smoke, T > FIRE ? [{type: 'smoke', pos: fp.clone().add(V3(0.3, 1.0, 0)), r: 0.5, t0: FIRE, size: 1.6, rise: 0.6, alpha: 0.7, share: 1}] : [], T, V3(0.4, 0, 0.3));
    updateParticles(gas, T > GAS ? nozzles.map(z => ({type: 'smoke', pos: V3(0, 2.9, z), r: 0.8, t0: GAS, size: 2.4, rise: -0.9, alpha: 0.45, col: [0.85, 0.88, 0.92], share: 1})) : [], T, V3(0, 0, 0));
    fireL.position.copy(fp).add(V3(0.5, 0.2, 0)); fireL.intensity = T > FIRE ? 14 * flicker(T, 3) * smooth(FIRE, FIRE + 0.5, T) : 0;
    // Kamera: fährt den Gang entlang, stoppt am Feuer
    const k = smooth(0, 4.8, t), stop = smooth(FIRE - 0.5, FIRE + 0.5, T);
    const z = lerp(3.0, -4.5, k) - stop * 0.4, shake = (T > OVERHEAT ? 0.01 : 0.003) + (T > FIRE && T < FIRE + 0.8 ? 0.02 : 0);
    camera.position.set(0.15 + noise1(T * 2, 3) * shake, 1.62 + noise1(T * 2.3, 5) * shake, z);
    camera.lookAt(lerp(0, -0.7, stop), lerp(1.5, 1.3, stop), z - 8);
    camera.updateProjectionMatrix();
  }};
}
