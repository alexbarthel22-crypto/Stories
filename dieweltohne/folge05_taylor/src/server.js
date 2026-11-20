// Rechenzentrum: Gang zwischen Serverschränken. Milliarden Suchanfragen „Wo ist Taylor?“:
// LEDs von Blau über Gelb zu Rot, Alarm mit Rundumleuchten (OVERLOAD), ein Schrank sprüht Funken und raucht (SPARK),
// dann fällt der Strom aus: nur noch rotes Notlicht und Löschnebel.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, sparkSystem, updateSparks, envMap} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {OVERLOAD, SPARK} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const BLACKOUT = 46.4;

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#05070a');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.15;
  scene.fog = new THREE.Fog('#0a0f16', 8, 40);
  const hemi = new THREE.HemisphereLight('#9fc4ff', '#141820', 0.35); scene.add(hemi);
  // Boden: Doppelboden-Platten (Lochplatten im Mittelgang)
  const tileT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#c9ccd1'; g.fillRect(0, 0, w, h); g.strokeStyle = '#8d9096'; g.lineWidth = 4; g.strokeRect(2, 2, w - 4, h - 4);
    g.fillStyle = '#6d7076'; for (let y = 24; y < h - 16; y += 16) for (let x = 24; x < w - 16; x += 16) { g.beginPath(); g.arc(x, y, 3, 0, 7); g.fill(); } });
  tileT.wrapS = tileT.wrapT = THREE.RepeatWrapping; tileT.repeat.set(10, 40);
  const fl = mesh(new THREE.PlaneGeometry(6, 24), new THREE.MeshStandardMaterial({map: tileT, roughness: 0.5, metalness: 0.3}), 0, 0, -10, scene); fl.rotation.x = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(12, 24), mat('#22252b'), 0, 3.2, -10, scene).rotation.x = Math.PI / 2;
  // Kabeltrassen an der Decke
  for (const x of [-0.8, 0.8]) mesh(new THREE.BoxGeometry(0.35, 0.08, 24), mat('#e3b23a', {metalness: 0.4}), x, 2.9, -10, scene);
  // Deckenlampen (Lichtbänder)
  const lampM = new THREE.MeshStandardMaterial({color: '#fff', emissive: '#e8f2ff', emissiveIntensity: 2.2});
  const lights = []; for (let i = 0; i < 6; i++) { mesh(new THREE.BoxGeometry(0.25, 0.04, 2.2), lampM, 0, 3.15, 1 - i * 4, scene); const l = new THREE.PointLight('#e8f2ff', 9, 7, 1.5); l.position.set(0, 2.9, 1 - i * 4); scene.add(l); lights.push(l); }
  // Serverschränke: gemeinsame animierte Front-Textur
  const FC = document.createElement('canvas'); FC.width = 256; FC.height = 1024; const FT = new THREE.CanvasTexture(FC); FT.colorSpace = THREE.SRGBColorSpace;
  const frontM = new THREE.MeshStandardMaterial({map: FT, emissive: '#ffffff', emissiveMap: FT, emissiveIntensity: 1.0, roughness: 0.4, metalness: 0.5});
  const bodyM = mat('#15171b', {metalness: 0.6, roughness: 0.4});
  const racks = []; const r = rng(3);
  for (const s of [-1, 1]) for (let i = 0; i < 18; i++) { const z = 2 - i * 0.65; const g = new THREE.Group(); g.position.set(s * 1.5, 0, z); scene.add(g);
    mesh(new THREE.BoxGeometry(0.6, 2.2, 0.62), bodyM, s * 0.3, 1.1, 0, g);
    const f = mesh(new THREE.PlaneGeometry(0.58, 2.1), frontM, -s * 0.005, 1.1, 0, g); f.rotation.y = -s * Math.PI / 2;
    // Seitenteile: Tür-Rahmen
    mesh(new THREE.BoxGeometry(0.03, 2.2, 0.03), mat('#2a2d33', {metalness: 0.7}), -s * 0.01, 1.1, 0.3, g);
    racks.push({g, s, z, i}); }
  function drawFronts(T) { const g = FC.getContext('2d'), w = 256, h = 1024; g.fillStyle = '#0d0e11'; g.fillRect(0, 0, w, h);
    const load = smooth(40, OVERLOAD, T), dead = T > BLACKOUT;
    for (let u = 0; u < 42; u++) { const y = 8 + u * 24; g.fillStyle = '#1c1e23'; g.fillRect(6, y, w - 12, 21); g.fillStyle = '#26292f'; for (let x = 20; x < 160; x += 9) g.fillRect(x, y + 4, 5, 13);
      const rr = rng(u * 13 + Math.floor(T * (8 + 30 * load)));
      for (let k = 0; k < 6; k++) { const on = rr() < 0.55 + load * 0.4; if (dead || !on) continue;
        const c = load < 0.35 ? '#3fa9ff' : load < 0.75 ? (rr() < load ? '#ffb02e' : '#3fa9ff') : (rr() < 0.85 ? '#ff3b30' : '#ffb02e'); g.fillStyle = c; g.fillRect(170 + k * 12, y + 8, 7, 6); } }
    FT.needsUpdate = true; }
  // Rundumleuchten (Alarm)
  const beacons = [-1, 1].map((s, i) => { const b = new THREE.Group(); b.position.set(s * 1.75, 2.32, -5 - i * 4); scene.add(b);
    mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.14, 16), new THREE.MeshStandardMaterial({color: '#ff2a1a', emissive: '#ff2a1a', emissiveIntensity: 0, transparent: true, opacity: 0.9}), 0, 0, 0, b);
    const sl = new THREE.SpotLight('#ff2a1a', 0, 14, 0.5, 0.4, 1.2); sl.position.set(0, 0, 0); b.add(sl); sl.target.position.set(1, -0.6, 0); b.add(sl.target); b.userData.sl = sl; b.userData.m = b.children[0].material; return b; });
  // Display am Gangende: Last-Anzeige
  const DC = document.createElement('canvas'); DC.width = 512; DC.height = 288; const DT = new THREE.CanvasTexture(DC); DT.colorSpace = THREE.SRGBColorSpace;
  const disp = mesh(new THREE.PlaneGeometry(1.6, 0.9), new THREE.MeshBasicMaterial({map: DT, toneMapped: false}), 0, 2.1, -9.6, scene);
  mesh(new THREE.PlaneGeometry(4, 3.2), mat('#2b2f36'), 0, 1.6, -9.7, scene);
  // Funken und Rauch aus einem Schrank
  const sparks = sparkSystem(900, 0.05); scene.add(sparks);
  const smoke = particles(700, 'smoke'); scene.add(smoke); const fire = particles(300, 'fire'); scene.add(fire);
  const hot = racks.find(k => k.s === 1 && k.i === 5);
  const fireL = new THREE.PointLight('#ff7a2a', 0, 6, 1.5); fireL.position.set(1.15, 1.4, hot.z); scene.add(fireL);

  const camera = new THREE.PerspectiveCamera(56, 1080 / 1920, 0.05, 80);
  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.05;
    const t = T - shot.t0, alarm = T > OVERLOAD, dead = T > BLACKOUT;
    drawFronts(T); frontM.emissiveIntensity = dead ? 0.05 : 1.0;
    lights.forEach(l => l.intensity = dead ? 0 : 9 * (T > SPARK ? (Math.sin(T * 40) > 0.3 ? 1 : 0.3) : 1)); lampM.emissiveIntensity = dead ? 0 : 2.2;
    hemi.intensity = dead ? 0.08 : 0.35;
    beacons.forEach((b, i) => { b.rotation.y = T * 7 + i; b.userData.sl.intensity = alarm ? (dead ? 80 : 40) : 0; b.userData.m.emissiveIntensity = alarm ? 3 : 0; });
    // Display
    { const g = DC.getContext('2d'), w = 512, h = 288; g.fillStyle = '#0b0d12'; g.fillRect(0, 0, w, h); if (!dead) {
      const load = Math.min(100, 38 + 70 * smooth(40, OVERLOAD + 0.5, T));
      g.fillStyle = '#9fb3c8'; g.font = '500 22px Plex'; g.fillText('SUCHANFRAGEN: „wo ist taylor“', 20, 40);
      g.fillStyle = load > 90 ? '#ff3b30' : load > 70 ? '#ffb02e' : '#3fa9ff'; g.font = '500 92px Plex'; g.fillText(Math.round(load) + ' %', 20, 150);
      g.fillStyle = '#9fb3c8'; g.font = '500 22px Plex'; g.fillText('AUSLASTUNG', 20, 190); g.fillText('TEMPERATUR ' + Math.round(24 + 40 * smooth(41, SPARK, T)) + ' °C', 20, 230);
      if (alarm && Math.sin(T * 10) > 0) { g.fillStyle = '#ff3b30'; g.font = '500 34px Plex'; g.fillText('⚠ ÜBERLASTUNG', 20, 275); } }
      DT.needsUpdate = true; }
    // Funken, Feuer, Rauch
    const hp = V3(1.2, 1.5, hot.z);
    updateSparks(sparks, T > SPARK ? [{pos: hp, dir: V3(-1, 0.4, 0), t0: SPARK, t1: SPARK + 0.6}, {pos: V3(1.2, 1.0, hot.z - 0.3), dir: V3(-1, 0.2, 0.2), t0: SPARK + 0.9, t1: SPARK + 1.4}, {pos: V3(1.2, 1.8, hot.z + 0.2), dir: V3(-1, 0.3, -0.1), t0: SPARK + 1.9, t1: SPARK + 2.4}] : [], T);
    updateParticles(fire, T > SPARK + 0.4 ? [{type: 'flame', pos: V3(1.15, 1.3, hot.z), r: 0.18, t0: SPARK + 0.4, size: 0.35, rise: 1.0, power: 0.9}] : [], T, V3(-0.3, 0, 0));
    updateParticles(smoke, T > SPARK + 0.2 ? [{type: 'smoke', pos: V3(1.0, 1.6, hot.z), r: 0.3, t0: SPARK + 0.2, size: 1.1, rise: 0.7, alpha: 0.5, col: [0.2, 0.2, 0.22], share: 2}, {type: 'smoke', pos: V3(0, 2.9, -2), r: 2.5, t0: BLACKOUT, size: 2.4, rise: -0.4, alpha: 0.4, col: [0.75, 0.78, 0.82], share: 1}] : [], T, V3(-0.4, 0, 0.3));
    fireL.intensity = T > SPARK ? 6 * flicker(T, 2) * (T < SPARK + 0.4 ? (Math.sin(T * 60) > 0 ? 1 : 0.2) : 1) : 0;
    // Kamera: Fahrt den Gang entlang, am Ende Blick auf den brennenden Schrank
    const u = smooth(0, 8, t), sh = alarm ? noise1(T * 5, 2) * 0.01 : 0;
    camera.position.set(lerp(-0.35, 0.15, u) + sh, lerp(1.55, 1.45, u), lerp(3.2, -0.2, u));
    camera.lookAt(lerp(0.1, 0.8, smooth(4.5, 7.5, t)), lerp(1.5, 1.4, u), lerp(-8, hot.z, smooth(4.5, 7.5, t)));
    camera.updateProjectionMatrix();
  }};
}
