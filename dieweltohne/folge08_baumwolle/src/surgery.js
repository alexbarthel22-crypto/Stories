// Operationssaal: Die Chirurgin drückt eine Kompresse auf die Wunde. Kompressen, Tupfer und Mullbinden lösen sich auf.
// Ein roter Fleck breitet sich auf dem (synthetischen) Abdecktuch aus, der Monitor schlägt Alarm. Keine Wunde im Bild.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeOut, posePerson, envMap, tileTex, makePerson} from './lib.js';
import {MONITOR_ALARM} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const GAUZE_GONE = 40.1;

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.background = new THREE.Color('#1a2a2a');
  const hemi = new THREE.HemisphereLight('#e6fff8', '#3a4a48', 0.55); scene.add(hemi);
  const op = new THREE.SpotLight('#ffffff', 45, 10, 0.45, 0.5, 1.2); op.position.set(0, 2.6, 0); op.target.position.set(0, 0.9, 0); op.castShadow = true; op.shadow.mapSize.set(2048, 2048); scene.add(op, op.target);
  const fillL = new THREE.PointLight('#cfeee8', 6, 12, 1.5); fillL.position.set(2, 2.6, 2); scene.add(fillL);
  const alarmL = new THREE.PointLight('#ff2020', 0, 8, 1.5); alarmL.position.set(1.4, 2.0, -1.2); scene.add(alarmL);

  // Raum
  const floorT = tileTex('#9fb7b2', '#95ada8'); floorT.repeat.set(5, 5);
  mesh(new THREE.PlaneGeometry(9, 9), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.35}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const wallM = mat('#7fa39c', {roughness: 0.6});
  for (const [x, z, ry] of [[0, -4, 0], [-4, 0, Math.PI / 2], [4, 0, -Math.PI / 2]]) { const w = mesh(new THREE.PlaneGeometry(9, 3.2), wallM, x, 1.6, z, scene); w.rotation.y = ry; }
  mesh(new THREE.PlaneGeometry(9, 9), mat('#dfe8e6'), 0, 3.2, 0, scene).rotation.x = Math.PI / 2;
  // OP-Leuchte
  const lampArm = mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.6, 8), mat('#d0d6da', {metalness: 0.6}), 0, 2.9, 0, scene);
  const lamp = mesh(new THREE.CylinderGeometry(0.45, 0.35, 0.14, 32), mat('#e6eaee', {metalness: 0.4, roughness: 0.3}), 0, 2.55, 0, scene);
  for (let i = 0; i < 7; i++) { const a = i / 7 * Math.PI * 2; mesh(new THREE.CircleGeometry(0.08, 16), new THREE.MeshBasicMaterial({color: '#fffdf2'}), Math.cos(a) * 0.24 * (i ? 1 : 0), 2.477, Math.sin(a) * 0.24 * (i ? 1 : 0), scene).rotation.x = Math.PI / 2; }
  // OP-Tisch mit Patient unter grünem Tuch
  const steel = mat('#c3c9ce', {metalness: 0.85, roughness: 0.3});
  mesh(new THREE.BoxGeometry(0.6, 0.75, 0.5), steel, 0, 0.375, 0, scene);
  mesh(new THREE.BoxGeometry(0.7, 0.08, 2.1), mat('#2b2f33'), 0, 0.8, 0, scene);
  const drapeM = mat('#2f7a6a', {roughness: 0.85});
  const drape = mesh(new RoundedBoxGeometry(0.95, 0.26, 2.2, 3, 0.1), drapeM, 0, 0.95, 0, scene);
  const head = mesh(new THREE.SphereGeometry(0.11, 16, 12), mat('#e4b896'), 0, 1.0, -1.05, scene);
  const cap = mesh(new THREE.SphereGeometry(0.115, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.55), mat('#4d8fc0'), 0, 1.0, -1.07, scene); cap.rotation.x = -0.6;
  // Sichtschutz (Narkosebügel)
  const bar = mesh(new THREE.TorusGeometry(0.5, 0.015, 6, 24, Math.PI), steel, 0, 0.95, -0.75, scene);
  const screenD = mesh(new THREE.PlaneGeometry(1.0, 0.5), mat('#2f7a6a', {side: THREE.DoubleSide}), 0, 1.2, -0.75, scene);
  // OP-Feld: Öffnung im Tuch (nur angedeutet, dunkel) und Blutfleck, der sich ausbreitet
  const field = mesh(new THREE.CircleGeometry(0.09, 24), mat('#5a2a2a', {roughness: 0.4}), 0.05, 1.082, 0.1, scene); field.rotation.x = -Math.PI / 2;
  const stainT = canvasTex(256, 256, (g, w, h) => { const r = rng(3); for (let i = 0; i < 26; i++) { const x = 128 + (r() - 0.5) * 90, y = 128 + (r() - 0.5) * 90, rad = 20 + r() * 50;
    const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, 'rgba(120,14,18,0.9)'); gr.addColorStop(0.7, 'rgba(120,14,18,0.6)'); gr.addColorStop(1, 'rgba(120,14,18,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); } });
  const stain = mesh(new THREE.PlaneGeometry(0.9, 0.9), new THREE.MeshStandardMaterial({map: stainT, color: '#8a1414', transparent: true, roughness: 0.35, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2}), 0.05, 1.083, 0.1, scene); stain.rotation.x = -Math.PI / 2; stain.castShadow = false;
  // Instrumententisch mit Kompressen und Mullbinden
  const tray = new THREE.Group(); tray.position.set(0.95, 0, 0.7); scene.add(tray);
  mesh(new THREE.BoxGeometry(0.7, 0.03, 0.45), steel, 0, 1.0, 0, tray);
  mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.0, 8), steel, 0, 0.5, 0, tray);
  const gauzeM = mat('#f7f6f1', {roughness: 1});
  const gauze = [];
  for (let i = 0; i < 4; i++) for (let k = 0; k < 5; k++) gauze.push(mesh(new THREE.BoxGeometry(0.1, 0.006, 0.1), gauzeM, -0.22, 1.02 + k * 0.007, -0.12 + i * 0.0, tray));
  for (let i = 0; i < 3; i++) { const b = mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.08, 16), gauzeM, -0.02 + i * 0.09, 1.05, 0.1, tray); b.rotation.z = Math.PI / 2; gauze.push(b); }
  for (let i = 0; i < 6; i++) { const ins = mesh(new THREE.BoxGeometry(0.18, 0.008, 0.015), steel, 0.12, 1.02, -0.14 + i * 0.05, tray); ins.rotation.y = 0.1 * i; }
  // Monitor
  const monC = document.createElement('canvas'); monC.width = 512; monC.height = 340; const monT = new THREE.CanvasTexture(monC); monT.colorSpace = THREE.SRGBColorSpace;
  const mon = new THREE.Group(); mon.position.set(-1.1, 1.75, -1.1); mon.rotation.y = 0.6; scene.add(mon);
  mesh(new RoundedBoxGeometry(0.62, 0.44, 0.08, 2, 0.02), mat('#d8dde2'), 0, 0, 0, mon);
  mesh(new THREE.PlaneGeometry(0.56, 0.37), new THREE.MeshBasicMaterial({map: monT, toneMapped: false}), 0, 0, 0.041, mon);
  mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.4, 8), steel, 0, -0.9, -0.05, mon);
  // Personal: Chirurgin, Assistent, Pflegekraft (Kittel aus Kunstfaser, bleiben)
  const mk = (seed, x, z, ry, col) => { const p = makePerson(seed, {top: col, pants: col, shortSleeve: false, hair: '#4d8fc0'}); p.position.set(x, 0, z); p.rotation.y = ry; scene.add(p);
    const mask = mesh(new THREE.BoxGeometry(0.16, 0.08, 0.03), mat('#9fd0e8'), 0, 0.03, 0.11, p.userData.head); return p; };
  const surgeon = mk(301, -0.62, 0.15, Math.PI / 2, '#3b6f8f'), assist = mk(305, 0.62, -0.2, -Math.PI / 2, '#3b6f8f'), nurse = mk(309, 1.8, -1.4, -2.2, '#5a8fa8');
  const compress = mesh(new THREE.BoxGeometry(0.1, 0.008, 0.1), gauzeM, 0, -0.32, 0.03, surgeon.userData.armR.userData.fore);
  const fibers = (() => { const g = new THREE.BufferGeometry(); const n = 400, P = new Float32Array(n * 3); g.setAttribute('position', new THREE.BufferAttribute(P, 3));
    const pts = new THREE.Points(g, new THREE.PointsMaterial({color: '#ffffff', size: 0.012, transparent: true, depthWrite: false})); pts.frustumCulled = false; scene.add(pts); return pts; })();

  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.03, 60);
  function drawMon(T) {
    const g = monC.getContext('2d'), al = T > MONITOR_ALARM, k = smooth(MONITOR_ALARM, 46.5, T);
    g.fillStyle = '#05080a'; g.fillRect(0, 0, 512, 340);
    const hr = 78 + 64 * k, bp = Math.round(118 - 52 * k);
    g.strokeStyle = '#3cff6a'; g.lineWidth = 3; g.beginPath();
    for (let x = 0; x < 360; x++) { const tt = T - (360 - x) / 140, ph = (tt * hr / 60) % 1; let y = 70;
      if (ph < 0.04) y -= 40 * Math.sin(ph / 0.04 * Math.PI); else if (ph < 0.07) y += 18 * Math.sin((ph - 0.04) / 0.03 * Math.PI); else if (ph > 0.3 && ph < 0.42) y -= 10 * Math.sin((ph - 0.3) / 0.12 * Math.PI);
      x ? g.lineTo(10 + x, y) : g.moveTo(10, y); }
    g.stroke();
    g.strokeStyle = '#ff4a4a'; g.beginPath(); for (let x = 0; x < 360; x++) { const tt = T - (360 - x) / 140, ph = (tt * hr / 60) % 1; const y = 175 - (1 - k * 0.6) * 30 * Math.exp(-ph * 5) * (ph < 0.6 ? 1 : 0.3); x ? g.lineTo(10 + x, y) : g.moveTo(10, y); } g.stroke();
    g.font = '700 54px Plex'; g.fillStyle = '#3cff6a'; g.fillText(String(Math.round(hr)), 390, 80);
    g.fillStyle = '#ff4a4a'; g.font = '700 40px Plex'; g.fillText(`${bp}/${Math.round(bp * 0.62)}`, 372, 185);
    g.fillStyle = '#4ac8ff'; g.fillText('SpO2 ' + Math.round(98 - 7 * k), 30, 280);
    if (al && Math.sin(T * 10) > -0.2) { g.fillStyle = '#ff2020'; g.fillRect(0, 300, 512, 40); g.fillStyle = '#fff'; g.font = '700 30px Plex'; g.fillText('ALARM  BLUTDRUCK', 120, 330); }
    monT.needsUpdate = true;
  }

  return {scene, camera, update(shot, T) {
    const gone = T >= GAUZE_GONE;
    gauze.forEach(m => m.visible = !gone); compress.visible = !gone;
    const bleed = smooth(GAUZE_GONE + 0.3, 46.8, T);
    stain.scale.setScalar(0.08 + 0.55 * Math.pow(bleed, 0.7)); stain.material.opacity = bleed > 0 ? 0.95 : 0;
    // Fasern stieben beim Verschwinden kurz auf
    { const P = fibers.geometry.attributes.position.array, d = T - GAUZE_GONE, r = rng(5);
      for (let i = 0; i < 400; i++) { const src = i < 250 ? V3(0.95 - 0.22, 1.05, 0.58) : V3(0.05, 1.1, 0.1); const vx = (r() - 0.5) * 0.6, vy = r() * 0.5, vz = (r() - 0.5) * 0.6;
        const ok = d > 0 && d < 1.4; P[i * 3] = ok ? src.x + vx * d : 0; P[i * 3 + 1] = ok ? src.y + vy * d - 0.1 * d * d : -9; P[i * 3 + 2] = ok ? src.z + vz * d : 0; }
      fibers.geometry.attributes.position.needsUpdate = true; fibers.material.opacity = clamp(1 - d / 1.4); }
    drawMon(T);
    const al = T > MONITOR_ALARM ? 1 : 0;
    alarmL.intensity = al * (Math.sin(T * 10) > -0.2 ? 8 : 0);
    // Chirurgin: drückt mit rechter Hand, sucht dann nach neuen Kompressen
    posePerson(surgeon, {}); { const u = surgeon.userData; u.armR.rotation.x = -1.0; u.armR.userData.fore.rotation.x = -0.9; u.armL.rotation.x = -0.9; u.armL.userData.fore.rotation.x = -0.8; u.torso.rotation.x = 0.3; u.head.rotation.x = 0.5;
      const look = smooth(GAUZE_GONE + 0.4, GAUZE_GONE + 1.0, T); u.head.rotation.y = -0.7 * look * (1 - smooth(43, 43.6, T)); u.armL.rotation.z = -0.4 * look; }
    posePerson(assist, {}); { const u = assist.userData; const reach = smooth(GAUZE_GONE + 1.2, GAUZE_GONE + 2.0, T); u.armL.rotation.x = -1.0; u.armR.rotation.x = lerp(-1.0, -1.3, reach); u.armL.userData.fore.rotation.x = -0.9; u.armR.userData.fore.rotation.x = -0.9; u.torso.rotation.x = 0.25; u.head.rotation.x = 0.4;
      u.torso.rotation.y = -0.8 * reach; }
    // Pflegekraft: öffnet einen Schrank, findet nichts, eilt zum Tisch
    const run = smooth(43.0, 45.2, T);
    nurse.position.set(lerp(2.0, 1.0, run), 0, lerp(-1.8, -0.9, run)); nurse.rotation.y = -1.0 - 0.5 * run; posePerson(nurse, {walk: T * 9, walkAmp: run > 0 && run < 1 ? 1 : 0});
    { const u = nurse.userData; const k = smooth(GAUZE_GONE + 0.2, GAUZE_GONE + 0.7, T) * (1 - run); u.armL.rotation.x = -1.4 * k; u.armR.rotation.x = -1.4 * k; }
    // Kamera: schräg von oben, langsam heran
    const u = smooth(39, 47, T);
    camera.position.set(lerp(1.6, 1.2, u), lerp(2.35, 2.1, u), lerp(2.2, 1.55, u)); camera.lookAt(lerp(0.0, 0.05, u), lerp(1.0, 1.05, u), lerp(-0.1, 0.05, u));
    camera.updateProjectionMatrix();
  }};
}
