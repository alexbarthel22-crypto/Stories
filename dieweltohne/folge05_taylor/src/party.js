// Schulparty in der Turnhalle: DJ-Pult, Discokugel, 300 Leute tanzen zu Taylor Swift.
// Ab PARTY_STOP ist der Song weg: Stille, alle erstarren, einer tanzt noch kurz allein weiter, dann gehen die Ersten.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, envMap} from './lib.js';
import {PARTY_STOP} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#07060c');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.12;
  scene.fog = new THREE.FogExp2('#120c1c', 0.035);
  const hemi = new THREE.HemisphereLight('#6a5aa8', '#1a1020', 0.6); scene.add(hemi);
  // Halle 24 x 16 m
  const floorT = canvasTex(1024, 1024, (g, w, h) => { g.fillStyle = '#b07a45'; g.fillRect(0, 0, w, h); const r = rng(8);
    for (let x = 0; x < w; x += 24) { g.fillStyle = `rgba(0,0,0,${0.05 + r() * 0.08})`; g.fillRect(x, 0, 2, h); for (let i = 0; i < 20; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '255,220,170' : '60,30,10'},${r() * 0.1})`; g.fillRect(x + 2, r() * h, 20, 40 + r() * 140); } }
    g.strokeStyle = '#e8e8e8'; g.lineWidth = 6; g.strokeRect(60, 60, w - 120, h - 120); g.beginPath(); g.arc(w / 2, h / 2, 140, 0, 7); g.stroke(); g.beginPath(); g.moveTo(w / 2, 60); g.lineTo(w / 2, h - 60); g.stroke();
    g.strokeStyle = '#2f7fd0'; g.beginPath(); g.arc(w / 2, 60, 260, 0, Math.PI); g.stroke(); g.beginPath(); g.arc(w / 2, h - 60, 260, Math.PI, 0); g.stroke(); });
  const fl = mesh(new THREE.PlaneGeometry(16, 24), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.35, metalness: 0.05}), 0, 0, 0, scene); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true;
  const wallM = mat('#4b4a58', {roughness: 0.9});
  for (const [w, x, z, ry] of [[16, 0, -12, 0], [16, 0, 12, Math.PI], [24, -8, 0, Math.PI / 2], [24, 8, 0, -Math.PI / 2]]) { const m = mesh(new THREE.PlaneGeometry(w, 9), wallM, x, 4.5, z, scene); m.rotation.y = ry; }
  mesh(new THREE.PlaneGeometry(16, 24), mat('#1c1b22'), 0, 9, 0, scene).rotation.x = Math.PI / 2;
  // Basketballkorb hinten, Sprossenwand
  mesh(new THREE.BoxGeometry(1.8, 1.05, 0.05), mat('#f2f2f2'), 0, 3.6, -11.6, scene); mesh(new THREE.TorusGeometry(0.23, 0.02, 8, 24), mat('#e8541f', {metalness: 0.5}), 0, 3.05, -11.3, scene).rotation.x = Math.PI / 2;
  for (let i = 0; i < 10; i++) { mesh(new THREE.BoxGeometry(0.06, 3, 0.06), mat('#c4955e'), -7.9, 1.5, -6 + i * 0.5, scene); }
  // Banner
  const banT = canvasTex(1024, 192, (g, w, h) => { g.fillStyle = '#16122a'; g.fillRect(0, 0, w, h); g.fillStyle = '#ff5fb8'; g.font = '500 110px Garamond'; g.textAlign = 'center'; g.fillText('WINTERBALL ✦ 2026', w / 2, 135); });
  mesh(new THREE.PlaneGeometry(7, 1.3), new THREE.MeshStandardMaterial({map: banT, emissive: '#ffffff', emissiveMap: banT, emissiveIntensity: 0.7}), 0, 6.2, -11.9, scene);

  // DJ-Pult vorn (Kamera schaut über die Schulter des DJs in die Menge)
  const djz = 6.5;
  mesh(new RoundedBoxGeometry(3.2, 1.05, 0.9, 3, 0.04), mat('#151519', {roughness: 0.5}), 0, 0.52, djz, scene).castShadow = true;
  const ledT = canvasTex(512, 64, (g, w, h) => { for (let x = 0; x < w; x += 8) { g.fillStyle = `hsl(${x / w * 360},100%,60%)`; g.fillRect(x, 0, 6, h); } });
  const ledM = new THREE.MeshBasicMaterial({map: ledT}); const led = mesh(new THREE.PlaneGeometry(3.1, 0.18), ledM, 0, 0.85, djz - 0.46, scene); led.rotation.y = Math.PI;
  const lapC = document.createElement('canvas'); lapC.width = 512; lapC.height = 320; const lapT = new THREE.CanvasTexture(lapC); lapT.colorSpace = THREE.SRGBColorSpace;
  const lap = new THREE.Group(); lap.position.set(0.3, 1.06, djz + 0.05); scene.add(lap);
  mesh(new THREE.BoxGeometry(0.5, 0.02, 0.34), mat('#c9ccd2', {metalness: 0.8, roughness: 0.3}), 0, 0, 0, lap);
  const scrn = new THREE.Group(); scrn.position.set(0, 0.01, -0.17); scrn.rotation.x = 0.25; lap.add(scrn);
  mesh(new THREE.BoxGeometry(0.5, 0.33, 0.012), mat('#c9ccd2', {metalness: 0.8, roughness: 0.3}), 0, 0.165, 0, scrn);
  const lsc = mesh(new THREE.PlaneGeometry(0.47, 0.3), new THREE.MeshBasicMaterial({map: lapT, toneMapped: false}), 0, 0.165, 0.007, scrn); lsc.rotation.y = 0;
  // Laptop-Bildschirm zeigt zum DJ (+z): Ebene umdrehen
  scrn.rotation.y = Math.PI; scrn.position.z = 0.17; scrn.rotation.x = -0.25;
  for (const x of [-0.9, -0.45]) { mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.04, 28), mat('#222', {metalness: 0.5}), x, 1.07, djz, scene); }
  for (const s of [-1, 1]) { const sp = mesh(new RoundedBoxGeometry(0.8, 1.9, 0.7, 2, 0.04), mat('#101012', {roughness: 0.7}), s * 2.4, 0.95, djz - 0.2, scene); sp.castShadow = true;
    for (const [y, r] of [[1.4, 0.2], [0.65, 0.3]]) mesh(new THREE.CircleGeometry(r, 28), mat('#2a2a2e', {roughness: 0.4}), s * 2.4, y, djz - 0.56, scene).rotation.y = Math.PI; }
  const dj = makePerson(41, {height: 1.05, top: '#111', pants: '#222', hair: '#111'}); dj.position.set(0, 0, djz + 0.75); dj.rotation.y = Math.PI; scene.add(dj);
  const djHp = new THREE.Group(); dj.userData.head.add(djHp); djHp.position.y = 0.07; mesh(new THREE.TorusGeometry(0.14, 0.014, 8, 26, Math.PI), mat('#222'), 0, 0, 0, djHp);
  for (const s of [-1, 1]) mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.05, 20), mat('#222'), s * 0.135, -0.02, 0, djHp).rotation.z = Math.PI / 2;

  // Menge
  const r = rng(23); const crowd = [];
  for (let i = 0; i < 70; i++) { let x, z; do { x = (r() - 0.5) * 11; z = -9 + r() * 13.5; } while (Math.abs(x) < 1.6 && z > 3.2);
    const p = makePerson(200 + i, {height: 0.92 + r() * 0.12, longHair: r() < 0.5}); p.position.set(x, 0, z); p.rotation.y = (r() - 0.5) * 0.8; scene.add(p);
    crowd.push({p, x, z, ph: r() * 6, style: Math.floor(r() * 3), leave: PARTY_STOP + 2.2 + r() * 4, ry: p.rotation.y}); }
  const lone = crowd.reduce((a, c) => (Math.abs(c.x - 1.2) + Math.abs(c.z - 1.0) < Math.abs(a.x - 1.2) + Math.abs(a.z - 1.0) ? c : a)); lone.p.position.set(1.0, 0, 1.0); lone.x = 1.0; lone.z = 1.0; lone.leave = 99;

  // Lichter: bewegte Spots (Kegel), Discokugel mit Lichtpunkten
  const spots = [], cones = [];
  const coneT = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const cols = ['#ff3fb4', '#3fc8ff', '#b46bff', '#ffd23f', '#3fff9b', '#ff6a3f'];
  for (let i = 0; i < 6; i++) { const sl = new THREE.SpotLight(cols[i], 60, 30, 0.22, 0.5, 1.2); sl.position.set(-6 + i * 2.4, 8.5, -2 + (i % 2) * 4); scene.add(sl, sl.target); spots.push(sl);
    const cone = new THREE.Mesh(new THREE.ConeGeometry(1.6, 9, 24, 1, true), new THREE.MeshBasicMaterial({map: coneT, color: cols[i], transparent: true, opacity: 0.16, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide}));
    cone.geometry.translate(0, -4.5, 0); scene.add(cone); cones.push(cone); }
  const ball = mesh(new THREE.IcosahedronGeometry(0.45, 2), new THREE.MeshStandardMaterial({color: '#ddd', metalness: 1, roughness: 0.15, flatShading: true, envMapIntensity: 3}), 0, 6.5, -2, scene);
  const dotT = canvasTex(32, 32, (g, w) => { const gr = g.createRadialGradient(16, 16, 0, 16, 16, 16); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const ND = 260, dg = new THREE.BufferGeometry(), dp = new Float32Array(ND * 3), dirs = [];
  for (let i = 0; i < ND; i++) { const a = r() * Math.PI * 2, e = -0.1 - r() * 1.2; dirs.push([a, e]); }
  dg.setAttribute('position', new THREE.BufferAttribute(dp, 3));
  const dots = new THREE.Points(dg, new THREE.PointsMaterial({map: dotT, size: 0.18, color: '#fff7e6', transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false})); scene.add(dots);
  const front = new THREE.PointLight('#ff8fd0', 40, 14, 1.2); front.position.set(0, 3, 4.5); scene.add(front);
  const work = new THREE.PointLight('#ffffff', 0, 30, 1.0); work.position.set(0, 8, 0); scene.add(work); // Hallenlicht geht an (später)

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 80);
  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.1;
    const t = T - shot.t0, on = T < PARTY_STOP, beat = T * 2.1 * Math.PI, sil = smooth(PARTY_STOP, PARTY_STOP + 0.4, T);
    const lightsOn = smooth(PARTY_STOP + 3.6, PARTY_STOP + 4.4, T); // Hausmeister macht das Hallenlicht an
    work.intensity = 120 * lightsOn; front.intensity = 40 * (1 - 0.5 * sil) * (1 - lightsOn) + 10; hemi.intensity = 0.6 + 1.2 * lightsOn;
    // Spots
    spots.forEach((sl, i) => { const sp = on ? T : PARTY_STOP + (T - PARTY_STOP) * 0.15; const tx = Math.sin(sp * 0.9 + i) * 5, tz = -3 + Math.cos(sp * 0.7 + i * 2) * 4.5;
      sl.target.position.set(tx, 0, tz); sl.intensity = 60 * (1 - 0.65 * sil) * (1 - lightsOn);
      const c = cones[i]; c.position.copy(sl.position); const dir = V3(tx, 0, tz).sub(sl.position).normalize(); c.quaternion.setFromUnitVectors(V3(0, -1, 0), dir); c.material.opacity = 0.16 * (1 - 0.65 * sil) * (1 - lightsOn); });
    ball.rotation.y = T * 0.6;
    for (let i = 0; i < ND; i++) { const [a, e] = dirs[i]; const aa = a + T * 0.6, d = 9; dp[i * 3] = ball.position.x + Math.cos(aa) * Math.cos(e) * d; dp[i * 3 + 1] = Math.max(0.05, ball.position.y + Math.sin(e) * d); dp[i * 3 + 2] = ball.position.z + Math.sin(aa) * Math.cos(e) * d; }
    dg.attributes.position.needsUpdate = true; dots.material.opacity = 0.9 * (1 - lightsOn);
    ledM.color.setScalar(on ? 1 : 0.25 + 0.75 * (Math.sin(T * 6) > 0 ? 1 : 0) * (1 - sil));
    // Menge
    crowd.forEach(c => { const p = c.p, u = p.userData; const lone1 = c === lone;
      const dance = lone1 ? (T < PARTY_STOP + 1.6 ? 1 : 1 - smooth(PARTY_STOP + 1.6, PARTY_STOP + 1.9, T)) : 1 - sil;
      const b = beat + c.ph, bob = Math.abs(Math.sin(b));
      const lv = smooth(c.leave, c.leave + 0.6, T), walkT = Math.max(0, T - c.leave);
      p.position.set(c.x, 0.06 * bob * dance * (c.style === 2 ? 2 : 1), c.z - walkT * 1.1 * lv); p.rotation.y = lerp(c.ry, Math.PI - (c.x > 0 ? 0.3 : -0.3), lv) + (dance > 0 ? Math.sin(b * 0.5) * 0.2 * dance : 0);
      posePerson(p, {walk: walkT * 8, walkAmp: lv * 0.8, armsUp: c.style === 0 ? (0.4 + 0.5 * bob) * dance : 0});
      if (c.style === 1 && dance > 0) { u.armL.rotation.x = -1.2 * dance; u.armR.rotation.x = -1.2 * dance; u.armL.userData.fore.rotation.x = -1.4 * dance; u.armR.userData.fore.rotation.x = -1.4 * dance; u.torso.rotation.z = Math.sin(b) * 0.15 * dance; }
      if (c.style === 2 && dance > 0) { u.armR.rotation.x = -2.8 * dance; u.armR.userData.fore.rotation.x = -0.3; u.hips.position.y = 0.92 - 0.06 * bob * dance; }
      u.head.rotation.x = -0.1 * bob * dance + (1 - dance) * 0.05;
      if (!lone1 && sil > 0 && lv < 1) { u.head.rotation.y = 0.35 * Math.sin(c.ph * 3) * sil; if (c.ph > 3) { u.armL.rotation.z = -0.5 * sil; u.armR.rotation.z = 0.5 * sil; u.armL.rotation.x = -0.6 * sil; u.armR.rotation.x = -0.6 * sil; } } // ratlos: Hände hoch
      if (lone1 && T > PARTY_STOP + 1.9) { u.head.rotation.y = 0.6 * Math.sin((T - PARTY_STOP - 1.9) * 3) * Math.exp(-(T - PARTY_STOP - 1.9)); u.armL.rotation.z = -0.15; u.armR.rotation.z = 0.15; } });
    // DJ
    const du = dj.userData; posePerson(dj, {});
    du.armL.rotation.x = -0.8; du.armL.userData.fore.rotation.x = -0.6; du.armR.rotation.x = -0.8; du.armR.userData.fore.rotation.x = -0.6;
    du.head.rotation.x = 0.25 + 0.06 * Math.abs(Math.sin(beat)) * (1 - sil); du.torso.rotation.x = 0.05 * Math.abs(Math.sin(beat)) * (1 - sil);
    const shrug = smooth(PARTY_STOP + 1.0, PARTY_STOP + 1.4, T); if (shrug > 0) { du.armL.rotation.x = lerp(-0.8, -0.3, shrug); du.armR.rotation.x = lerp(-0.8, -0.3, shrug); du.armL.rotation.z = -0.9 * shrug; du.armR.rotation.z = 0.9 * shrug; du.armL.userData.fore.rotation.x = -1.3 * shrug; du.armR.userData.fore.rotation.x = -1.3 * shrug; du.head.rotation.x = -0.05; }
    // Laptop
    { const g = lapC.getContext('2d'), w = 512, h = 320; g.fillStyle = '#101218'; g.fillRect(0, 0, w, h);
      g.fillStyle = '#fff'; g.font = '500 22px Plex'; g.fillText(on ? '▶ Taylor Swift – Lieblingssong' : '■ Titel nicht gefunden', 20, 40);
      for (let x = 0; x < w - 40; x += 3) { const a = on ? Math.abs(Math.sin(x * 0.07 + T * 8) * Math.sin(x * 0.013 + T)) * 70 + 4 : 1; g.fillStyle = on ? '#3fc8ff' : '#444'; g.fillRect(20 + x, 150 - a, 2, a * 2); }
      if (!on && Math.sin(T * 8) > 0) { g.fillStyle = '#ff4d4d'; g.font = '500 30px Plex'; g.fillText('FEHLER: DATEI LEER', 20, 270); }
      lapT.needsUpdate = true; }
    // Kamera: über die Schulter des DJs
    const u = smooth(0, 7, t), sh = noise1(T * 1.5, 4) * 0.03;
    camera.fov = 50; camera.position.set(lerp(-1.0, -0.75, u) + sh, lerp(1.95, 1.85, u), lerp(8.3, 7.6, u)); camera.lookAt(lerp(0.0, 0.55, u), 1.05, 0);
    camera.updateProjectionMatrix();
  }};
}
