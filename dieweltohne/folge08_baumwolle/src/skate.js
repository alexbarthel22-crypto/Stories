// Skatepark am Nachmittag. Der Kumpel springt über die Kicker-Rampe – mitten in der Luft verschwinden Jeans und Hoodie.
// Schluss (final): derselbe Park in der Dämmerung, über der Stadt stehen Rauchsäulen, Fasern und Asche treiben herab.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, skyDome, easeOut, posePerson, envMap, tileTex} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {makePhone, makeHands} from './phone.js';
import {cottonPerson, setCotton, flakes, updateFlakes, fluffTex} from './cotton.js';
import {VANISH, RETURN} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.35;
  scene.fog = new THREE.Fog('#c9d8e6', 60, 380);
  const skyDay = skyDome('#3f7cc4', '#8fbbe2', '#dfe9f0', 450), skyDusk = skyDome('#2a2440', '#9a4a3a', '#f08a3a', 450);
  scene.add(skyDay, skyDusk);
  const hemi = new THREE.HemisphereLight('#dfeaff', '#6a6458', 1.0); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff1d8', 2.8); sun.position.set(-20, 30, 14); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -20, right: 20, top: 20, bottom: -20, near: 1, far: 90}); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03; scene.add(sun);
  const glow = new THREE.PointLight('#ff6a2a', 0, 400, 1.2); glow.position.set(0, 30, -140); scene.add(glow);

  // Boden: heller Beton mit Fugen
  const conT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#b9b6ae'; g.fillRect(0, 0, w, h); const r = rng(2);
    for (let i = 0; i < 9000; i++) { const v = 150 + r() * 60; g.fillStyle = `rgba(${v},${v},${v - 6},0.35)`; g.fillRect(r() * w, r() * h, 2, 2); }
    g.strokeStyle = 'rgba(90,88,84,0.55)'; g.lineWidth = 3; for (let x = 0; x <= w; x += 128) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); g.beginPath(); g.moveTo(0, x); g.lineTo(w, x); g.stroke(); }
    for (let i = 0; i < 20; i++) { g.fillStyle = 'rgba(60,60,60,0.08)'; g.beginPath(); g.ellipse(r() * w, r() * h, 20 + r() * 60, 10 + r() * 30, r() * 3, 0, 7); g.fill(); } });
  conT.wrapS = conT.wrapT = THREE.RepeatWrapping; conT.repeat.set(10, 10);
  const conM = new THREE.MeshStandardMaterial({map: conT, roughness: 0.9});
  const ground = mesh(new THREE.PlaneGeometry(80, 80), conM, 0, 0, 0, scene); ground.rotation.x = -Math.PI / 2;
  const grass = mesh(new THREE.PlaneGeometry(900, 900), mat('#6f8a4a', {roughness: 1}), 0, -0.02, 0, scene); grass.rotation.x = -Math.PI / 2;
  // Fasern am Boden (nur im Schluss)
  const fluffM = new THREE.MeshStandardMaterial({map: fluffTex(8), roughness: 1, transparent: true, opacity: 0});
  const fluffG = mesh(new THREE.PlaneGeometry(80, 80), fluffM, 0, 0.015, 0, scene); fluffG.rotation.x = -Math.PI / 2; fluffG.castShadow = false;
  const tufts = new THREE.InstancedMesh(new THREE.SphereGeometry(0.3, 10, 8), mat('#f6f3ec', {roughness: 1}), 160); tufts.castShadow = true;
  { const r = rng(12), m4 = new THREE.Matrix4(); for (let i = 0; i < 160; i++) { const x = -30 + r() * 60, z = -22 + r() * 40, s = 0.4 + r() * 1.6;
      m4.compose(V3(x, 0, z), new THREE.Quaternion(), V3(s * 1.4, s * 0.45, s)); tufts.setMatrixAt(i, m4); } }
  scene.add(tufts);

  // Rampen
  const rampM = mat('#a8a49c', {roughness: 0.8}), steelM = mat('#7b8289', {metalness: 0.8, roughness: 0.35});
  const kick = new THREE.Shape(); kick.moveTo(0, 0); kick.lineTo(2.0, 0); kick.lineTo(2.0, 0.55); kick.quadraticCurveTo(1.0, 0.12, 0, 0);
  const kickG = new THREE.ExtrudeGeometry(kick, {depth: 1.8, bevelEnabled: false}); kickG.translate(-2.0, 0, -0.9);
  mesh(kickG, rampM, 0, 0, 0, scene);
  mesh(new THREE.CylinderGeometry(0.03, 0.03, 1.8, 8), steelM, 0, 0.55, 0, scene).rotation.x = Math.PI / 2;
  // Funbox und Quarterpipe im Hintergrund
  mesh(new THREE.BoxGeometry(4, 0.6, 2.4), rampM, 7, 0.3, -6, scene);
  mesh(new THREE.BoxGeometry(4, 0.05, 0.05), steelM, 7, 0.62, -5.2, scene);
  const qp = new THREE.Shape(); qp.moveTo(0, 0); qp.lineTo(2.6, 0); qp.lineTo(2.6, 2.2); qp.lineTo(2.4, 2.2); qp.quadraticCurveTo(2.4, 0.05, 0, 0);
  const qpG = new THREE.ExtrudeGeometry(qp, {depth: 9, bevelEnabled: false}); qpG.translate(0, 0, -4.5);
  const qpM = mesh(qpG, rampM, -16, 0, -6, scene); qpM.rotation.y = Math.PI;
  // Graffitiwand
  const graf = canvasTex(1024, 256, (g, w, h) => { g.fillStyle = '#8f8a82'; g.fillRect(0, 0, w, h); const r = rng(8);
    const cols = ['#ff4f7a', '#3ad1c4', '#ffd23f', '#8a5cff', '#ff8a2a', '#2f9e5a'];
    for (let i = 0; i < 14; i++) { g.fillStyle = cols[i % 6]; g.beginPath(); g.ellipse(r() * w, 60 + r() * 140, 40 + r() * 90, 25 + r() * 50, r() * 3, 0, 7); g.fill(); }
    g.font = '900 120px sans-serif'; g.lineWidth = 10; g.strokeStyle = '#1a1a1a'; g.fillStyle = '#fff'; g.save(); g.translate(120, 180); g.rotate(-0.08); g.strokeText('SKATE', 0, 0); g.fillText('SKATE', 0, 0); g.restore();
    g.fillStyle = '#ffd23f'; g.strokeText('ZONE', 600, 190); g.fillText('ZONE', 600, 190); });
  mesh(new THREE.BoxGeometry(26, 2.4, 0.3), new THREE.MeshStandardMaterial({map: graf, roughness: 0.9}), 0, 1.2, -12, scene);
  // Bäume
  const trunkM = mat('#5a4330'), leafM = mat('#4f7a3a', {roughness: 0.9});
  { const r = rng(21); for (let i = 0; i < 26; i++) { const a = r() * Math.PI * 2, d = 20 + r() * 18, x = Math.cos(a) * d, z = Math.sin(a) * d - 4; if (z > 14 && Math.abs(x) < 10) continue;
      mesh(new THREE.CylinderGeometry(0.15, 0.22, 3, 8), trunkM, x, 1.5, z, scene); mesh(new THREE.IcosahedronGeometry(1.8 + r(), 1), leafM, x, 3.8, z, scene); } }
  // Stadt am Horizont (Richtung -z)
  const city = [];
  { const r = rng(44); for (let i = 0; i < 46; i++) { const x = -200 + r() * 400, z = -110 - r() * 120, w = 10 + r() * 18, h = 14 + r() * 50;
      const b = mesh(new THREE.BoxGeometry(w, h, 12), new THREE.MeshStandardMaterial({map: facadeTex(['#a9a39a', '#9aa4ad', '#b8a68e'][i % 3], i + 3, Math.round(h / 3.4), 4), roughness: 0.9}), x, h / 2, z, scene); city.push(b); } }
  // Bänke und Leute am Rand
  const benchM = mat('#6b4b32');
  mesh(new THREE.BoxGeometry(2.4, 0.08, 0.5), benchM, 6, 0.46, 4.5, scene); mesh(new THREE.BoxGeometry(0.1, 0.45, 0.4), steelM, 5, 0.22, 4.5, scene); mesh(new THREE.BoxGeometry(0.1, 0.45, 0.4), steelM, 7, 0.22, 4.5, scene);

  // Skater
  const skater = cottonPerson(5, {hoodie: '#8b9098', top: '#c6ff3a', under: '#d8322f', skin: '#e1ad86', hair: '#2a1d15', shoe: '#1d1d1d'});
  scene.add(skater);
  const board = new THREE.Group(); scene.add(board);
  mesh(new RoundedBoxGeometry(0.8, 0.03, 0.22, 2, 0.012), mat('#2a2a2e'), 0, 0.085, 0, board);
  mesh(new THREE.BoxGeometry(0.78, 0.004, 0.2), mat('#e94f37'), 0, 0.068, 0, board);
  for (const x of [-0.27, 0.27]) for (const z of [-0.08, 0.08]) mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.035, 12), mat('#f2efe6'), x, 0.03, z, board).rotation.x = Math.PI / 2;
  // Freunde
  const fr1 = cottonPerson(12, {hoodie: '#24344f', top: '#ff6a3d', under: '#2f6fd1', skin: '#a8714f', hair: '#111'});
  const fr2 = cottonPerson(19, {top: '#f2f2f2', jeans: true, denim: '#2b3c5a', under: '#7a2fb5', skin: '#f1c7a5', hair: '#c9a35b', ponytail: true});
  scene.add(fr1, fr2);
  const extra = [cottonPerson(31, {hoodie: '#c23b6a', top: '#3a3a3a', under: '#222', skin: '#7a4d33'}), cottonPerson(33, {top: '#4aa3c7', under: '#e0457b', skin: '#f5d3b8'})];
  extra.forEach(p => scene.add(p));
  const smoke = particles(700, 'smoke'); scene.add(smoke);
  const fire = particles(300, 'flame'); scene.add(fire);
  const ash = flakes(900, [-30, 30, 0, 18, -30, 14], 0.16); scene.add(ash);

  // Kamera und Handy (Intro)
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 2000); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#2c2f36'); const hands = makeHands('#a8714f', '#24344f');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig);
  rig.position.set(0.02, -0.07, -0.29); rig.rotation.set(-0.1, 0.04, -0.03);
  const RT = new THREE.WebGLRenderTarget(432, 936); RT.texture.colorSpace = THREE.SRGBColorSpace;
  const phoneCam = new THREE.PerspectiveCamera(62, 432 / 936, 0.05, 2000);
  const uiC = document.createElement('canvas'); uiC.width = 432; uiC.height = 936; const uiT = new THREE.CanvasTexture(uiC); uiT.colorSpace = THREE.SRGBColorSpace;
  const pw = phone.userData.pw, phh = phone.userData.ph;
  mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: RT.texture, toneMapped: false}), 0, 0, 0.0052, phone);
  mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: uiT, transparent: true, toneMapped: false}), 0, 0, 0.0056, phone);
  phone.userData.scr.visible = false;

  // Fahrweg des Skaters: rollt entlang x auf den Kicker (Kante bei x=0) zu, springt ab bei JUMP
  const JUMP = 9.62, AIR = 0.95, X0 = -13;
  const SPEED = (0 - X0) / (JUMP - 3.0);
  function skaterAt(T) {
    // Rückgabe: x, y (Füße), Brettneigung, Pose
    if (T < 3.0) return {x: X0 - 0.3 + Math.sin(T * 1.3) * 0.15, y: 0, tilt: 0, push: (T % 1.2) / 1.2};
    if (T < JUMP - 0.9) { const x = X0 + SPEED * (T - 3.0); return {x, y: 0, tilt: 0, push: T < 5.5 ? ((T - 3) % 1.0) : -1}; }
    if (T < JUMP) { const x = X0 + SPEED * (T - 3.0); const k = clamp((x + 2.0) / 2.0); return {x, y: 0.55 * k * k, tilt: 0.55 * k, push: -1}; }
    const ta = T - JUMP;
    if (ta < AIR) { const x = SPEED * 0.8 * ta, y = 0.55 + 3.6 * ta - 0.5 * 9.81 * ta * ta * 0.98; return {x, y: Math.max(0, y), tilt: lerp(0.5, -0.1, ta / AIR), push: -1, air: ta / AIR}; }
    const tl = T - JUMP - AIR, x = SPEED * 0.8 * AIR + 3.2 * (1 - Math.exp(-tl * 0.9)); // rollt aus
    return {x, y: 0, tilt: 0, push: -1, land: tl};
  }

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id, fin = id === 'final';
    const gone = T >= VANISH && T < RETURN;
    skyDay.visible = !fin; skyDusk.visible = fin;
    scene.fog.color.set(fin ? '#7a5a4e' : '#c9d8e6'); scene.fog.near = fin ? 30 : 60; scene.fog.far = fin ? 260 : 380;
    sun.color.set(fin ? '#ff9a5a' : '#fff1d8'); sun.intensity = fin ? 1.2 : 2.8; sun.position.set(fin ? -60 : -20, fin ? 8 : 30, fin ? -20 : 14);
    hemi.intensity = fin ? 0.55 : 1.0; hemi.color.set(fin ? '#ffb48a' : '#dfeaff');
    glow.intensity = fin ? 9000 * flicker(T, 2) : 0;
    fluffM.opacity = fin ? 0.85 : 0; fluffG.visible = fin; tufts.visible = fin; ash.visible = fin;
    // Rauchsäulen und Feuerschein über der Stadt (nur Schluss)
    updateParticles(smoke, fin ? [[-60, -150], [10, -170], [70, -140], [-120, -190], [130, -200]].map(([x, z], i) => ({type: 'smoke', pos: V3(x, 10, z), r: 14, t0: 0, size: 38, rise: 9, col: [0.16, 0.13, 0.12], alpha: 0.7, share: 1})) : [], T + 20, V3(4, 0, 1));
    updateParticles(fire, fin ? [[-60, -150], [10, -170], [70, -140]].map(([x, z]) => ({type: 'flame', pos: V3(x, 4, z), r: 16, t0: 0, size: 14, rise: 8, power: 0.9, share: 1})) : [], T + 20);
    if (fin) updateFlakes(ash, T, 0.5, 1, [0.9, 0.3]);
    city.forEach(b => b.material.color.set(fin ? '#8a6e66' : '#ffffff'));

    // Skater
    const s = fin ? null : skaterAt(T);
    if (s) {
      const cr = s.push >= 0 ? 0 : 0.35; // in die Knie gehen
      skater.position.set(s.x, s.y, 0); skater.rotation.y = Math.PI / 2;
      posePerson(skater, {walk: 0, walkAmp: 0});
      const u = skater.userData;
      skater.rotation.set(0, 0.15, 0); // Skater-Stand: seitlich auf dem Brett, Gesicht zur Kamera
      u.hips.position.y = 0.92 - cr * 0.2 + 0.08;
      u.legL.rotation.z = -0.22; u.legR.rotation.z = 0.22; u.legL.rotation.x = cr * 0.5; u.legR.rotation.x = cr * 0.5; u.legL.userData.knee.rotation.x = cr * 0.9; u.legR.userData.knee.rotation.x = cr * 0.9;
      u.armL.rotation.z = -0.6; u.armR.rotation.z = 0.6;
      if (s.push >= 0 && s.push < 0.5 && T > 3) { u.legR.rotation.x = -0.5 * Math.sin(s.push * Math.PI * 2); u.legR.rotation.z = 0.05; }
      if (s.air != null) { const k = Math.sin(s.air * Math.PI); u.legL.rotation.x = -0.9 * k; u.legR.rotation.x = -0.9 * k; u.legL.userData.knee.rotation.x = 1.6 * k; u.legR.userData.knee.rotation.x = 1.6 * k; u.hips.position.y = 0.92 - 0.2 * k;
        u.armL.rotation.z = -1.3; u.armR.rotation.z = 1.3; }
      if (s.land != null) { // gelandet, merkt es, bleibt stehen und hält die Hände vor die Shorts
        const look = smooth(0.4, 1.0, s.land), cover = smooth(0.9, 1.5, s.land); if (s.land > 1.2) { u.legL.rotation.z = -0.06; u.legR.rotation.z = 0.06; u.legL.rotation.x = u.legR.rotation.x = 0; u.legL.userData.knee.rotation.x = u.legR.userData.knee.rotation.x = 0.1; u.hips.position.y = 0.92; skater.position.y = 0; }
        u.head.rotation.x = 0.55 * look; u.torso.rotation.x = 0.15 * look;
        u.armL.rotation.z = lerp(-0.6, -0.15, cover); u.armR.rotation.z = lerp(0.6, 0.15, cover); u.armL.rotation.x = -0.5 * cover; u.armR.rotation.x = -0.5 * cover;
        u.armL.userData.fore.rotation.x = -0.8 * cover; u.armR.userData.fore.rotation.x = -0.8 * cover;
        if (s.land > 2.5) { u.torso.rotation.y = 0.6 * smooth(2.5, 3.2, s.land); u.head.rotation.y = 0.5 * smooth(2.5, 3.2, s.land); }
      }
      setCotton(skater, !gone);
      board.position.set(s.x, s.y, 0); board.rotation.set(0, 0, s.tilt);
      if (s.land != null && s.land > 1.2) { const k = smooth(1.2, 2.4, s.land); board.position.x = s.x + 1.4 * k; board.rotation.z = 0; } // Brett rollt allein weiter
    } else { // Schluss: sitzt auf der Funbox, Brett daneben
      skater.position.set(2.9, 0, -6.4); skater.rotation.set(0, Math.PI - 0.3, 0); posePerson(skater, {});
      { const u = skater.userData; u.head.rotation.x = -0.3; u.armR.rotation.x = -0.4; u.armR.userData.fore.rotation.x = -1.2; }
      setCotton(skater, false);
      board.position.set(3.6, 0, -5.6); board.rotation.set(0, 0.5, 0);
    }
    // Freunde: fr1 filmt (Intro-POV-Position), fr2 lacht
    const laughK = smooth(VANISH + 0.8, VANISH + 1.6, T) * (fin ? 0 : 1);
    fr2.position.set(5.2, 0, -2.4); fr2.rotation.set(0, -1.2, 0); posePerson(fr2, {});
    { const u = fr2.userData; const sh = Math.sin(T * 22) * 0.05 * laughK; u.torso.rotation.x = 0.35 * laughK + sh; u.armL.rotation.x = -1.2 * laughK; u.armL.userData.fore.rotation.x = -1.6 * laughK; u.armR.rotation.z = 0.4 * laughK; }
    setCotton(fr2, !gone);
    fr1.position.set(-10.2, 0, 4.6); fr1.rotation.set(0, -2.6, 0); posePerson(fr1, {holdUp: 0.6});
    setCotton(fr1, !gone);
    fr1.visible = id !== 'intro';
    if (fin) { fr2.position.set(1.4, 0, -7.0); fr2.rotation.set(0, Math.PI, 0); posePerson(fr2, {}); fr2.userData.head.rotation.x = -0.35; fr2.userData.torso.rotation.x = 0; setCotton(fr2, false); fr1.visible = true; fr1.position.set(-0.4, 0, -6.6); fr1.rotation.set(0, Math.PI + 0.2, 0); posePerson(fr1, {}); fr1.userData.head.rotation.x = -0.3; setCotton(fr1, false); }
    extra[0].position.set(-6, 0, -8); extra[0].rotation.set(0, 0.4, 0); posePerson(extra[0], {walk: T * 4, walkAmp: 0.2}); setCotton(extra[0], !gone && !fin);
    extra[1].position.set(9, 0, -2.5); extra[1].rotation.set(0, -1.8, 0); posePerson(extra[1], {}); setCotton(extra[1], !gone && !fin);
    if (gone) { const k = smooth(VANISH + 1.0, VANISH + 1.8, T); extra[0].userData.armL.rotation.x = -2.4 * k; extra[1].userData.torso.rotation.x = 0.3 * k; }

    // Kamera
    rig.visible = id === 'intro'; camera.fov = 50;
    if (id === 'intro') {
      camera.position.set(-10.2 + noise1(T, 1) * 0.02, 1.6 + noise1(T, 3) * 0.01, 4.8); camera.lookAt(-12.6, 1.0, 0);
      const sx = skaterAt(T).x;
      phoneCam.position.copy(camera.position).add(V3(-0.03, -0.08, -0.3)); phoneCam.lookAt(sx, 1.0, 0); phoneCam.updateProjectionMatrix();
      rig.visible = false; renderer.setRenderTarget(RT); renderer.render(scene, phoneCam); renderer.setRenderTarget(null); rig.visible = true;
      const g = uiC.getContext('2d'); g.clearRect(0, 0, 432, 936); g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(0, 0, 432, 70); g.fillRect(0, 800, 432, 136);
      g.fillStyle = '#ff3b30'; g.beginPath(); g.arc(150, 38, 9, 0, 7); g.fill(); g.fillStyle = '#fff'; g.font = '500 22px Plex'; g.textAlign = 'left'; g.fillText(`REC 00:0${Math.floor(t + 2)}`, 166, 46);
      g.strokeStyle = '#fff'; g.lineWidth = 6; g.beginPath(); g.arc(216, 868, 36, 0, 7); g.stroke(); g.fillStyle = '#ff3b30'; g.beginPath(); g.roundRect(198, 850, 36, 36, 6); g.fill();
      uiT.needsUpdate = true;
    } else if (id === 'wait' || id === 'skate') {
      // seitliche Kamera, folgt dem Skater, beim Sprung tief und nah
      const sx = skaterAt(T).x, sy = skaterAt(T).y;
      const u = smooth(3.5, 9.4, T);
      const cx = lerp(-6, 1.2, u) + (id === 'skate' ? smooth(10.6, 13, T) * 2.2 : 0);
      camera.position.set(cx, lerp(1.4, 0.9, u), lerp(7.5, 5.2, u)); camera.lookAt(lerp(sx, sx * 0.6 + 1, smooth(9.0, 10.2, T)), 0.9 + sy * 0.5, 0);
    } else { // final
      const u = smooth(0, 10, t);
      camera.position.set(lerp(3.4, 3.0, u), lerp(2.7, 3.1, u), lerp(4.5, 3.2, u)); camera.lookAt(lerp(2.6, 2.2, u), lerp(3.0, 5.0, u), -60);
    }
    camera.updateProjectionMatrix();
  }};
}
