// Erdbebenwarte bei Nacht: Trommel-Seismograf, Weltkarte mit Messpunkten, Wasserglas, Hängelampe.
// seismo: Fans weltweit auf der Straße, der Zeiger schlägt immer weiter aus (NEEDLE).
// quake: nach der Rückkehr springen alle vor Freude – der Zeiger schlägt an, die Schreibfeder bricht ab (SNAP), alles wackelt.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, envMap} from './lib.js';
import {NEEDLE, RETURN, JUMP, SNAP} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const REV = 1.6; // Sekunden pro Trommelumdrehung
const CITIES = [[52.5, 13.4], [48.9, 2.35], [51.5, -0.1], [40.7, -74], [34.05, -118.2], [41.9, -87.6], [47.6, -122.3], [19.4, -99.1], [-23.5, -46.6], [-34.6, -58.4], [35.7, 139.7], [37.5, 127], [31.2, 121.5], [1.35, 103.8], [-33.9, 151.2], [-37.8, 145], [19.1, 72.9], [25.2, 55.3], [55.75, 37.6], [59.3, 18.1], [41.0, 28.98], [30.0, 31.2], [-26.2, 28.0], [6.5, 3.4], [43.65, -79.4], [49.3, -123.1], [45.5, -73.6], [40.4, -3.7], [45.46, 9.19], [53.3, -6.26], [14.6, 121], [-6.2, 106.8], [13.75, 100.5], [39.9, 116.4], [22.3, 114.2], [-41.3, 174.8], [64.1, -21.9], [60.2, 24.9], [50.1, 14.4], [52.2, 21.0]];

// Ausschlag der Feder (0..1+) über die Zeit
function amp(t) {
  let a = 0.03 + 0.02 * Math.sin(t * 7);
  a += 0.25 * smooth(48.5, NEEDLE, t) + 0.35 * smooth(NEEDLE, 56.4, t);
  a *= 1 - 0.8 * smooth(56.4, 56.9, t) * (1 - smooth(RETURN + 0.3, JUMP, t)); // kurze Stille vor der Rückkehr
  a += 1.2 * smooth(JUMP - 0.5, JUMP + 2, t);
  return a;
}
function wig(t) { return Math.sin(t * 41) * 0.5 + Math.sin(t * 67 + 1) * 0.3 + Math.sin(t * 13 + 2) * 0.2; }

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#06070b');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.18;
  const hemi = new THREE.HemisphereLight('#8ea2c8', '#191510', 0.35); scene.add(hemi);
  // Raum
  const wallM = mat('#3a3e46', {roughness: 0.95});
  const floor = mesh(new THREE.PlaneGeometry(10, 10), mat('#2d2a27', {roughness: 0.8}), 0, 0, 0, scene); floor.rotation.x = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(10, 3.2), wallM, 0, 1.6, -2.2, scene); const lw = mesh(new THREE.PlaneGeometry(10, 3.2), wallM, -3, 1.6, 0, scene); lw.rotation.y = Math.PI / 2;
  mesh(new THREE.PlaneGeometry(10, 10), mat('#24262b'), 0, 3.0, 0, scene).rotation.x = Math.PI / 2;
  // Tisch
  const deskM = mat('#6b5440', {roughness: 0.6});
  const desk = mesh(new THREE.BoxGeometry(2.6, 0.06, 1.0), deskM, 0, 0.78, -1.3, scene); desk.receiveShadow = true;
  for (const x of [-1.2, 1.2]) for (const z of [-1.7, -0.9]) mesh(new THREE.BoxGeometry(0.06, 0.76, 0.06), deskM, x, 0.38, z, scene);
  // Monitore mit Weltkarte
  const img = new Image(); img.src = '../tex/earth_night.jpg'; await img.decode();
  const MC = document.createElement('canvas'); MC.width = 1024; MC.height = 512; const MT = new THREE.CanvasTexture(MC); MT.colorSpace = THREE.SRGBColorSpace;
  const monM = new THREE.MeshBasicMaterial({map: MT, toneMapped: false});
  const mons = [];
  for (const [x, ry] of [[-0.75, 0.18], [0.75, -0.18]]) { const g = new THREE.Group(); g.position.set(x, 1.35, -1.65); g.rotation.y = ry; scene.add(g);
    mesh(new THREE.BoxGeometry(1.42, 0.82, 0.05), mat('#111'), 0, 0, -0.03, g); const s = mesh(new THREE.PlaneGeometry(1.36, 0.76), monM, 0, 0, 0.001, g);
    if (x > 0) { s.geometry = new THREE.PlaneGeometry(1.36, 0.76); const uv = s.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setX(i, uv.getX(i) * 0.5 + 0.5); }
    else { const uv = s.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setX(i, uv.getX(i) * 0.5); }
    mesh(new THREE.BoxGeometry(0.06, 0.4, 0.06), mat('#222'), 0, -0.55, -0.05, g); mons.push(g); }
  const monL = new THREE.PointLight('#7fa6ff', 3, 4, 1.5); monL.position.set(0, 1.4, -1.0); scene.add(monL);
  // Seismograf: Sockel, Trommel mit Papier, Feder
  const sg = new THREE.Group(); sg.position.set(0.15, 0.81, -1.05); scene.add(sg);
  mesh(new RoundedBoxGeometry(0.9, 0.08, 0.42, 2, 0.02), mat('#1d2a3a', {metalness: 0.5, roughness: 0.4}), 0, 0.04, 0, sg);
  for (const x of [-0.38, 0.38]) mesh(new THREE.BoxGeometry(0.03, 0.26, 0.05), mat('#9aa0a8', {metalness: 0.8, roughness: 0.3}), x, 0.17, 0, sg);
  const PC = document.createElement('canvas'); PC.width = 2048; PC.height = 512; const PT = new THREE.CanvasTexture(PC); PT.colorSpace = THREE.SRGBColorSpace; PT.anisotropy = 8;
  const drum = new THREE.Group(); drum.position.set(0, 0.28, 0); sg.add(drum);
  const drumMesh = mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.7, 64, 1, true), new THREE.MeshStandardMaterial({map: PT, roughness: 0.8}), 0, 0, 0, drum); drumMesh.rotation.z = Math.PI / 2;
  for (const x of [-0.35, 0.35]) { const c = mesh(new THREE.CircleGeometry(0.11, 40), mat('#c9ccd1', {metalness: 0.8, roughness: 0.3}), x, 0, 0, drum); c.rotation.y = x > 0 ? Math.PI / 2 : -Math.PI / 2; }
  mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.8, 8), mat('#bbb', {metalness: 0.9}), 0, 0, 0, drum).rotation.z = Math.PI / 2;
  // Federarm: Drehpunkt hinten oben, Spitze vorn auf der Trommel
  const arm = new THREE.Group(); arm.position.set(0, 0.43, -0.25); sg.add(arm);
  const armRod = mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.25, 6), mat('#d8d8d8', {metalness: 0.9, roughness: 0.2}), 0, 0, 0.125, arm); armRod.rotation.x = Math.PI / 2;
  const pen = mesh(new THREE.ConeGeometry(0.008, 0.04, 8), mat('#b0201a'), 0, -0.02, 0.25, arm); pen.rotation.x = Math.PI;
  mesh(new THREE.BoxGeometry(0.06, 0.06, 0.06), mat('#333', {metalness: 0.6}), 0, 0, 0, arm);
  const armPivot = new THREE.Group(); arm.add(armPivot);
  const tipFly = new THREE.Group(); scene.add(tipFly); const tipRod = mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.2, 6), mat('#d8d8d8', {metalness: 0.9}), 0, 0, 0, tipFly); tipRod.rotation.x = Math.PI / 2; mesh(new THREE.ConeGeometry(0.008, 0.04, 8), mat('#b0201a'), 0, 0, 0.1, tipFly).rotation.x = Math.PI / 2;
  // Wasserglas mit Wellen
  const glass = mesh(new THREE.CylinderGeometry(0.04, 0.035, 0.12, 24, 1, true), new THREE.MeshPhysicalMaterial({color: '#dfefff', transparent: true, opacity: 0.25, roughness: 0.05, metalness: 0, side: THREE.DoubleSide}), -0.55, 0.87, -0.95, scene);
  const WC = document.createElement('canvas'); WC.width = WC.height = 128; const WT = new THREE.CanvasTexture(WC);
  const water = mesh(new THREE.CircleGeometry(0.038, 28), new THREE.MeshStandardMaterial({color: '#9cc6e8', map: WT, transparent: true, opacity: 0.85, roughness: 0.05, metalness: 0.2}), -0.55, 0.9, -0.95, scene); water.rotation.x = -Math.PI / 2;
  // Bücherregal links, Bücher fallen
  const shelf = new THREE.Group(); shelf.position.set(-2.85, 0, -0.6); scene.add(shelf);
  for (let k = 0; k < 4; k++) mesh(new THREE.BoxGeometry(0.3, 0.03, 1.2), mat('#5a4636'), 0, 0.5 + k * 0.5, 0, shelf);
  const books = []; { const r = rng(6); for (let k = 0; k < 4; k++) for (let i = 0; i < 9; i++) { const h = 0.22 + r() * 0.12; const b = mesh(new THREE.BoxGeometry(0.2, h, 0.05), mat(['#8a2f2a', '#2f4f7a', '#c9a35b', '#2f6b4a', '#d8d2c4'][Math.floor(r() * 5)]), 0.02, 0.515 + k * 0.5 + h / 2, -0.5 + i * 0.12, shelf); books.push({b, y0: b.position.y, z0: b.position.z, k: r(), lvl: k}); } }
  // Hängelampe
  const lamp = new THREE.Group(); lamp.position.set(0.1, 3.0, -1.0); scene.add(lamp);
  mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.9, 6), mat('#111'), 0, -0.45, 0, lamp);
  mesh(new THREE.ConeGeometry(0.22, 0.2, 28, 1, true), new THREE.MeshStandardMaterial({color: '#2a5a3a', side: THREE.DoubleSide, metalness: 0.4, roughness: 0.4}), 0, -0.98, 0, lamp);
  const bulb = mesh(new THREE.SphereGeometry(0.05, 12, 10), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#ffdcaa', emissiveIntensity: 3}), 0, -1.02, 0, lamp);
  const lampL = new THREE.SpotLight('#ffdcaa', 14, 6, 0.9, 0.5, 1.3); lampL.position.set(0, -1.0, 0); lamp.add(lampL); lampL.target.position.set(0, -3, 0); lamp.add(lampL.target);
  lampL.castShadow = true; lampL.shadow.mapSize.set(1024, 1024); lampL.shadow.bias = -0.001;
  // Fenster mit Stadtlichtern
  const winT = canvasTex(512, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#05070f'); gr.addColorStop(1, '#1c1f38'); g.fillStyle = gr; g.fillRect(0, 0, w, h); const r = rng(9); for (let i = 0; i < 300; i++) { g.fillStyle = `rgba(255,${200 + r() * 55},${120 + r() * 80},${0.4 + r() * 0.6})`; g.fillRect(r() * w, 150 + r() * 106, 2, 2); } });
  const win = mesh(new THREE.PlaneGeometry(1.6, 0.9), new THREE.MeshBasicMaterial({map: winT}), 1.9, 2.0, -2.19, scene);
  // Seismologin
  const sci = makePerson(902, {top: '#6b7a8a', pants: '#2d3a55', hair: '#2a1d15', longHair: true}); scene.add(sci);

  function drawPaper(T) {
    const g = PC.getContext('2d'), w = 2048, h = 512; g.fillStyle = '#cfc6b2'; g.fillRect(0, 0, w, h);
    g.strokeStyle = 'rgba(80,110,160,0.18)'; g.lineWidth = 1; for (let x = 0; x < w; x += 64) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }
    const t0 = Math.max(40, T - REV * 22); const rowH = 22;
    g.strokeStyle = '#0a0a14'; g.lineWidth = 6;
    let prev = null;
    for (let ts = t0; ts <= T; ts += 0.012) {
      const rev = (ts - 40) / REV, u = (rev % 1) * w, row = Math.floor(rev);
      const yc = 120 + (row % 14) * rowH; if (T > SNAP && ts > SNAP) break;
      const y = yc + clamp(amp(ts) * wig(ts), -1.4, 1.4) * 80 * Math.min(1, amp(ts) * 3);
      if (prev && u > prev[0] && row === prev[2]) { g.beginPath(); g.moveTo(prev[0], prev[1]); g.lineTo(u, y); g.stroke(); }
      prev = [u, y, row];
    }
    PT.needsUpdate = true; return prev;
  }
  function drawMap(T, id) {
    const g = MC.getContext('2d'), w = 1024, h = 512; g.drawImage(img, 0, 0, w, h); g.fillStyle = 'rgba(5,10,30,0.45)'; g.fillRect(0, 0, w, h);
    const k = id === 'quake' ? 1 : smooth(48.2, 55, T);
    CITIES.forEach(([la, lo], i) => { const on = i / CITIES.length < k * 1.05; if (!on) return; const x = (lo + 180) / 360 * w, y = (90 - la) / 180 * h;
      const pulse = (T * 1.4 + i * 0.13) % 1, big = id === 'quake' ? 1.8 : 1;
      g.strokeStyle = `rgba(255,${id === 'quake' ? 200 : 70},${id === 'quake' ? 60 : 50},${1 - pulse})`; g.lineWidth = 3; g.beginPath(); g.arc(x, y, (6 + pulse * 30) * big, 0, 7); g.stroke();
      g.fillStyle = id === 'quake' ? '#ffd23f' : '#ff3b30'; g.beginPath(); g.arc(x, y, 5 * big, 0, 7); g.fill(); });
    g.fillStyle = 'rgba(0,0,0,0.6)'; g.fillRect(0, 0, w, 54); g.fillStyle = '#fff'; g.font = '500 26px Plex';
    g.fillText(id === 'quake' ? 'ERSCHÜTTERUNGEN WELTWEIT · ALLE STATIONEN' : 'MESSSTATIONEN MIT AUSSCHLAG: ' + Math.round(CITIES.length * k * 12), 16, 36);
    if (Math.sin(T * 8) > 0) { g.fillStyle = '#ff3b30'; g.fillText('● ALARM', w - 160, 36); }
    MT.needsUpdate = true;
  }

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 60);
  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.05;
    const id = shot.id, t = T - shot.t0, quake = id === 'quake';
    const shake = quake ? 0.6 + 0.4 * Math.sin(T * 0.7) * 0 + 0.5 * smooth(SNAP - 0.4, SNAP, T) : smooth(NEEDLE, 56.4, T) * 0.25 * (1 - smooth(56.4, 56.9, T));
    drawPaper(T); drawMap(T, id);
    drum.rotation.x = -((T - 40) / REV) * Math.PI * 2;
    // Feder: Ausschlag entlang der Trommelachse, folgt der Zeile (helix)
    const rev = (T - 40) / REV, row = Math.floor(rev) % 14; const defl = clamp(amp(T) * wig(T), -1.4, 1.4) * Math.min(1, amp(T) * 3);
    const across = -0.35 + ((120 + row * 22) / 512) * 0.7 + defl * 80 / 512 * 0.7; // u-Richtung = Trommelachse
    arm.rotation.y = Math.atan2(across, 0.25) * -1;
    const snapped = quake && T > SNAP;
    armRod.visible = pen.visible = !snapped; tipFly.visible = snapped;
    if (snapped) { const a = T - SNAP; tipFly.position.set(0.15 + 0.6 * a, Math.max(0.82, 0.81 + 0.5 + 2.2 * a - 4.9 * a * a), -1.05 + 0.9 * a); tipFly.rotation.set(a * 9, a * 6, 0); }
    // Wasser
    { const g = WC.getContext('2d'); g.fillStyle = '#7fb0d8'; g.fillRect(0, 0, 128, 128); const s = quake ? 1 : clamp(shake * 3);
      for (let i = 0; i < 5; i++) { const ph = ((T * (1.5 + s * 3) + i / 5) % 1); g.strokeStyle = `rgba(255,255,255,${(1 - ph) * (0.15 + 0.6 * s)})`; g.lineWidth = 3; g.beginPath(); g.arc(64, 64, ph * 64, 0, 7); g.stroke(); } WT.needsUpdate = true; }
    glass.position.x = -0.55 + (quake ? noise1(T * 20, 3) * 0.01 : 0); water.position.x = glass.position.x;
    // Lampe pendelt
    lamp.rotation.z = Math.sin(T * 2.2) * (0.02 + 0.25 * (quake ? 1 : shake)); lamp.rotation.x = Math.cos(T * 1.9) * (0.01 + 0.15 * (quake ? 1 : shake * 0.5));
    // Bücher kippen und fallen (quake)
    books.forEach(bk => { if (!quake) { bk.b.position.set(0.02, bk.y0, bk.z0); bk.b.rotation.set(0, 0, 0); return; } const d = T - (66.8 + bk.k * 4);
      if (d < 0) { bk.b.position.set(0.02 + noise1(T * 25, bk.k * 10) * 0.004, bk.y0, bk.z0); bk.b.rotation.set(noise1(T * 22, bk.k * 7) * 0.05, 0, 0); return; }
      if (bk.k > 0.5) { const fall = Math.min(d, Math.sqrt(2 * bk.y0 / 9.8)); bk.b.position.set(0.02 + 0.6 * fall, Math.max(0.03, bk.y0 - 4.9 * fall * fall), bk.z0); bk.b.rotation.set(0, 0, -Math.min(1.5, fall * 4)); }
      else bk.b.rotation.set(0, 0, -Math.min(0.5, d * 2)); });
    monL.intensity = 3 + (Math.sin(T * 8) > 0 ? 1.5 : 0);
    // Seismologin
    posePerson(sci, {}); const su = sci.userData;
    if (!quake) { const back = smooth(NEEDLE + 0.5, NEEDLE + 1.5, T); sci.position.set(lerp(-0.7, -1.1, back), 0, lerp(-0.45, 0.1, back)); sci.rotation.y = Math.PI - 0.5;
      su.torso.rotation.x = lerp(0.45, 0.05, back); su.armL.rotation.x = lerp(-0.9, -0.3, back); su.armR.rotation.x = lerp(-0.9, -2.5, smooth(NEEDLE + 1.6, NEEDLE + 2.2, T)); su.armR.userData.fore.rotation.x = lerp(-0.4, -1.9, smooth(NEEDLE + 1.6, NEEDLE + 2.2, T)); su.head.rotation.x = 0.4 * (1 - back); }
    else { sci.position.set(-0.4, 0, -0.35); sci.rotation.y = Math.PI - 0.2; su.torso.rotation.x = 0.3; su.armL.rotation.x = -1.2; su.armR.rotation.x = -1.2; su.armL.userData.fore.rotation.x = -0.3; su.armR.userData.fore.rotation.x = -0.3; su.head.rotation.x = 0.2 + noise1(T * 9, 2) * 0.05; }
    // Kamera
    const sh = (quake ? 0.012 + 0.03 * smooth(SNAP - 0.4, SNAP, T) * Math.exp(-(T - SNAP) * 0.6 * (T > SNAP)) : shake * 0.006);
    const nx = noise1(T * 23, 1) * sh, ny = noise1(T * 29, 2) * sh;
    camera.fov = 48;
    if (!quake) { const u = smooth(0, 9, t); camera.position.set(lerp(0.62, 0.5, u) + nx, lerp(1.25, 1.42, u) + ny, lerp(-0.4, 0.45, u)); camera.lookAt(lerp(0.12, -0.1, u), lerp(1.08, 1.2, u), lerp(-1.05, -1.4, u)); }
    else { const u = smooth(0, 9, t); camera.position.set(lerp(0.9, 0.5, u) + nx * 2, lerp(1.6, 1.55, u) + ny * 2, lerp(1.6, 1.2, u)); camera.lookAt(lerp(-0.2, 0.0, u), 1.15, -1.3); }
    camera.updateProjectionMatrix();
  }};
}
