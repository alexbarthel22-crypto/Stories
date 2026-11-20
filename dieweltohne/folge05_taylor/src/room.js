// Jugendzimmer am Abend: Sie singt mit Kopfhörern in die Haarbürste. Dann ist jeder Song von Taylor Swift weg.
// Der kleine Bruder filmt. Am Ende: das Video geht viral (POV des Bruders mit Handy).
// Taylor Swift selbst ist nie zu sehen (nur Text auf Postern/Display).
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, easeOut, envMap} from './lib.js';
import {makePhone, makeHands, updateScreen} from './phone.js';
import {VANISH, RETURN} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const RW = 2.3, ZB = -2.0, ZF = 2.8, RH = 2.6;
const STOP_SING = 11.4, TAP = 12.0, BRO_IN = 12.4, BRO_FILM = 13.4, SEE = 14.3;

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#120f1a');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.22;
  scene.add(new THREE.HemisphereLight('#e7d9ff', '#3a2c2c', 0.55));
  const lamp = new THREE.PointLight('#ffcf9a', 7, 9, 1.4); lamp.position.set(-0.6, 2.3, 1.2); lamp.castShadow = true; lamp.shadow.mapSize.set(1024, 1024); lamp.shadow.bias = -0.002; scene.add(lamp);
  const pink = new THREE.PointLight('#ff5fb8', 3.5, 6, 1.6); pink.position.set(1.6, 2.2, -1.6); scene.add(pink);
  const blue = new THREE.PointLight('#5f86ff', 2.0, 6, 1.6); blue.position.set(-2.0, 0.6, -1.4); scene.add(blue);

  // Raum
  const wallM = mat('#c9b6dd', {roughness: 0.92}), wallM2 = mat('#b9a3d0', {roughness: 0.92});
  const floorT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#9c7a5a'; g.fillRect(0, 0, w, h); const r = rng(4);
    for (let y = 0; y < h; y += 32) { g.fillStyle = `rgba(0,0,0,${0.06 + r() * 0.08})`; g.fillRect(0, y, w, 2); for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '255,230,200' : '50,30,20'},${r() * 0.08})`; g.fillRect(r() * w, y + r() * 30, 30 + r() * 120, 2); } } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(3, 3);
  const fl = mesh(new THREE.PlaneGeometry(RW * 2, ZF - ZB), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.6}), 0, 0, (ZB + ZF) / 2, scene); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true;
  const rug = mesh(new THREE.CircleGeometry(1.0, 48), mat('#f2e6f7', {roughness: 1}), 0.2, 0.004, 0.2, scene); rug.rotation.x = -Math.PI / 2; rug.receiveShadow = true;
  mesh(new THREE.PlaneGeometry(RW * 2, ZF - ZB), mat('#e9e2ef'), 0, RH, (ZB + ZF) / 2, scene).rotation.x = Math.PI / 2;
  mesh(new THREE.BoxGeometry(0.1, RH, ZF - ZB), wallM2, -RW - 0.05, RH / 2, (ZB + ZF) / 2, scene).receiveShadow = true;
  mesh(new THREE.BoxGeometry(0.1, RH, ZF - ZB), wallM2, RW + 0.05, RH / 2, (ZB + ZF) / 2, scene).receiveShadow = true;
  mesh(new THREE.BoxGeometry(RW * 2, RH, 0.1), wallM, 0, RH / 2, ZF + 0.05, scene);
  // Rückwand mit Tür (x 1.15..2.05)
  const DX0 = 1.15, DX1 = 2.05, DH = 2.05;
  const wb = (x0, x1, y0, y1) => mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, 0.1), wallM, (x0 + x1) / 2, (y0 + y1) / 2, ZB - 0.05, scene).receiveShadow = true;
  wb(-RW, DX0, 0, RH); wb(DX1, RW, 0, RH); wb(DX0, DX1, DH, RH);
  const frameM = mat('#f4f1ea', {roughness: 0.5});
  for (const x of [DX0, DX1]) mesh(new THREE.BoxGeometry(0.06, DH, 0.14), frameM, x, DH / 2, ZB, scene);
  mesh(new THREE.BoxGeometry(DX1 - DX0 + 0.06, 0.06, 0.14), frameM, (DX0 + DX1) / 2, DH, ZB, scene);
  // Flur hinter der Tür (hell)
  mesh(new THREE.PlaneGeometry(3, 3), new THREE.MeshBasicMaterial({color: '#d8cbb8'}), 1.6, 1.3, ZB - 1.6, scene);
  const hallL = new THREE.PointLight('#ffe7c2', 3, 4, 1.5); hallL.position.set(1.6, 2.0, ZB - 0.8); scene.add(hallL);
  const door = new THREE.Group(); door.position.set(DX0 + 0.02, 0, ZB + 0.02); scene.add(door);
  mesh(new THREE.BoxGeometry(DX1 - DX0 - 0.04, DH - 0.02, 0.04), mat('#f7f5f0', {roughness: 0.5}), (DX1 - DX0) / 2, DH / 2, 0, door).castShadow = true;
  mesh(new THREE.SphereGeometry(0.03, 10, 8), mat('#c9c9c9', {metalness: 0.9, roughness: 0.3}), DX1 - DX0 - 0.12, 1.0, 0.05, door);

  // Poster (nur Schrift und Formen)
  const poster = (seed, lines, c1, c2) => canvasTex(360, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, c1); gr.addColorStop(1, c2); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(seed); for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(255,255,255,${0.2 + r() * 0.6})`; const x = r() * w, y = r() * h, s = 2 + r() * 6; g.beginPath(); for (let k = 0; k < 10; k++) { const a = k * Math.PI / 5, rr = k % 2 ? s * 0.4 : s; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.fill(); }
    g.fillStyle = '#fff'; g.textAlign = 'center'; lines.forEach(([txt, size, y]) => { g.font = `500 ${size}px Garamond`; g.fillText(txt, w / 2, y); }); });
  [[-1.55, 1.7, poster(3, [['THE', 40, 180], ['ERAS', 96, 270], ['TOUR', 70, 340]], '#7b3fa0', '#ff7aa8')], [-0.7, 1.85, poster(5, [['13', 220, 330]], '#1d3a6b', '#5fc7e8')], [0.35, 1.75, poster(9, [['Swiftie', 72, 260], ['forever', 44, 320]], '#e8b04a', '#d94b6a')]]
    .forEach(([x, y, tex]) => { const p = mesh(new THREE.PlaneGeometry(0.62, 0.88), new THREE.MeshStandardMaterial({map: tex, roughness: 0.7}), x, y, ZB + 0.01, scene); p.rotation.z = (x * 7 % 3 - 1) * 0.02; });
  // Lichterkette an der Rückwand
  const bulbs = []; for (let i = 0; i < 26; i++) { const x = -2.1 + i * 0.168, y = 2.35 - Math.sin(i / 25 * Math.PI) * 0.25 - (i % 2) * 0.02;
    const m = new THREE.MeshStandardMaterial({color: '#ffd9a0', emissive: '#ffb860', emissiveIntensity: 3}); bulbs.push(m); mesh(new THREE.SphereGeometry(0.018, 8, 6), m, x, y, ZB + 0.04, scene); }
  const cordPts = Array.from({length: 27}, (_, i) => V3(-2.1 + i * 0.168, 2.37 - Math.sin(i / 26 * Math.PI) * 0.25, ZB + 0.03));
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(cordPts), new THREE.LineBasicMaterial({color: '#222'})));
  // Bett an der linken Wand
  mesh(new RoundedBoxGeometry(1.1, 0.42, 2.1, 3, 0.06), mat('#efe9df'), -RW + 0.6, 0.21, 0.2, scene).receiveShadow = true;
  const duvet = mesh(new RoundedBoxGeometry(1.14, 0.14, 1.5, 3, 0.06), mat('#d98bb5', {roughness: 1}), -RW + 0.6, 0.48, 0.5, scene); duvet.receiveShadow = true; duvet.castShadow = true;
  mesh(new RoundedBoxGeometry(0.62, 0.15, 0.36, 3, 0.07), mat('#fff', {roughness: 1}), -RW + 0.6, 0.52, -0.6, scene);
  const plush = mesh(new THREE.SphereGeometry(0.13, 14, 10), mat('#c8a07a', {roughness: 1}), -RW + 0.85, 0.6, -0.55, scene); plush.scale.set(1, 0.9, 0.8);
  // Schreibtisch hinten rechts mit Lampe, Spiegel
  mesh(new THREE.BoxGeometry(0.6, 0.04, 1.2), mat('#f3f0ea'), RW - 0.32, 0.74, 0.3, scene).castShadow = true;
  for (const z of [-0.25, 0.85]) mesh(new THREE.BoxGeometry(0.56, 0.72, 0.04), mat('#f3f0ea'), RW - 0.32, 0.36, z, scene);
  mesh(new THREE.CylinderGeometry(0.12, 0.08, 0.16, 16, 1, true), new THREE.MeshStandardMaterial({color: '#fff3dc', emissive: '#ffcf8a', emissiveIntensity: 1.2, side: THREE.DoubleSide}), RW - 0.25, 1.14, -0.1, scene);
  mesh(new THREE.CylinderGeometry(0.01, 0.01, 0.38, 6), mat('#ccc', {metalness: 0.8}), RW - 0.25, 0.94, -0.1, scene);
  // Freundschaftsarmbänder auf dem Tisch
  const beadCols = ['#ff6fa8', '#ffd84a', '#5fd1ff', '#ffffff', '#a07bff', '#6fe08a'];
  for (let k = 0; k < 4; k++) for (let i = 0; i < 18; i++) { const a = i / 18 * Math.PI * 2; mesh(new THREE.SphereGeometry(0.009, 6, 5), mat(beadCols[(i + k) % 6], {roughness: 0.3}), RW - 0.4 + Math.cos(a) * 0.04, 0.765, 0.2 + k * 0.12 + Math.sin(a) * 0.04, scene); }

  // Sie: lange Haare, Kopfhörer, Haarbürste als Mikro
  const girl = makePerson(505, {height: 0.98, top: '#f2f2f2', pants: '#4a5f9a', hair: '#6b3f22', longHair: true, skin: '#e8b996'}); scene.add(girl);
  girl.traverse(o => { if (o.isMesh) o.castShadow = true; });
  const gu = girl.userData;
  const hpM = mat('#f7f7f7', {roughness: 0.35}), hpM2 = mat('#e7a3c2', {roughness: 0.5});
  const hp = new THREE.Group(); gu.head.add(hp); hp.position.y = 0.07;
  mesh(new THREE.TorusGeometry(0.14, 0.014, 8, 26, Math.PI), hpM, 0, 0, 0, hp);
  for (const s of [-1, 1]) { const c = mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.045, 22), hpM, s * 0.135, -0.02, 0, hp); c.rotation.z = Math.PI / 2; mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.05, 20), hpM2, s * 0.13, -0.02, 0, hp).rotation.z = Math.PI / 2; }
  const brush = new THREE.Group(); gu.armR.userData.fore.add(brush); brush.position.set(0, -0.3, 0.02);
  mesh(new THREE.CylinderGeometry(0.016, 0.02, 0.16, 10), mat('#ff7ab0', {roughness: 0.4}), 0, 0.02, 0, brush);
  const bh = mesh(new THREE.CapsuleGeometry(0.035, 0.05, 4, 10), mat('#ff7ab0', {roughness: 0.4}), 0, -0.1, 0, brush); bh.scale.set(1, 1, 0.55);
  // Armband am Handgelenk
  for (let i = 0; i < 14; i++) { const a = i / 14 * Math.PI * 2; mesh(new THREE.SphereGeometry(0.011, 6, 5), mat(beadCols[i % 6], {roughness: 0.3}), Math.cos(a) * 0.05, -0.25, Math.sin(a) * 0.05, gu.armL.userData.fore); }
  // Handy auf dem Bett (zeigt den Player)
  const bedPhone = makePhone(); bedPhone.userData.caseM.color.set('#b9a4ff'); bedPhone.position.set(-RW + 0.75, 0.56, 1.0); bedPhone.rotation.set(-Math.PI / 2, 0, 0.5); bedPhone.scale.setScalar(1.6); scene.add(bedPhone);

  // kleiner Bruder mit Handy
  const bro = makePerson(77, {height: 0.72, top: '#3fa36b', pants: '#2d3a55', hair: '#5a3b22'}); scene.add(bro);
  bro.traverse(o => { if (o.isMesh) o.castShadow = true; });
  const broPhone = makePhone(); broPhone.userData.caseM.color.set('#222'); broPhone.scale.setScalar(1.3); bro.userData.armR.userData.fore.add(broPhone); broPhone.position.set(0, -0.32, 0.04); broPhone.rotation.set(Math.PI / 2, Math.PI, 0);

  // Kamera, POV-Handy (Intro: ihr Player, Ende: Video des Bruders)
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 60); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#b9a4ff'); const hands = makeHands('#e8b996', '#f2f2f2');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig); rig.position.set(0.0, -0.05, -0.27); rig.rotation.set(-0.1, 0.0, 0.03);
  const RT = new THREE.WebGLRenderTarget(432, 936); RT.texture.colorSpace = THREE.SRGBColorSpace;
  const vidCam = new THREE.PerspectiveCamera(48, 432 / 936, 0.05, 60);
  const uiC = document.createElement('canvas'); uiC.width = 432; uiC.height = 936; const uiT = new THREE.CanvasTexture(uiC); uiT.colorSpace = THREE.SRGBColorSpace;
  const pw = phone.userData.pw, phh = phone.userData.ph;
  const live = mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: RT.texture, toneMapped: false}), 0, 0, 0.0052, phone);
  const ui = mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: uiT, transparent: true, toneMapped: false}), 0, 0, 0.0056, phone);

  // Musik-Player (ohne Bild der Künstlerin: nur Farbverlauf, Glitzer, Text)
  function player(g, st, SW, SH) {
    const {t, gone} = st;
    const gr = g.createLinearGradient(0, 0, 0, SH); gr.addColorStop(0, '#3a1f5c'); gr.addColorStop(1, '#0f0b1a'); g.fillStyle = gr; g.fillRect(0, 0, SW, SH);
    g.fillStyle = '#fff'; g.font = '500 24px Plex'; g.textAlign = 'left'; g.fillText('21:14', 40, 52); g.textAlign = 'right'; g.fillText('5G  63%', SW - 40, 52);
    // Cover: abstrakt
    const cx = 60, cy = 150, cs = SW - 120;
    if (!gone) { const cg = g.createLinearGradient(cx, cy, cx + cs, cy + cs); cg.addColorStop(0, '#ff7aa8'); cg.addColorStop(0.5, '#b56bff'); cg.addColorStop(1, '#5fc7e8'); g.fillStyle = cg; g.beginPath(); g.roundRect(cx, cy, cs, cs, 24); g.fill();
      const r = rng(11); for (let i = 0; i < 60; i++) { g.fillStyle = `rgba(255,255,255,${0.3 + 0.7 * Math.abs(Math.sin(t * 3 + i))})`; g.beginPath(); g.arc(cx + r() * cs, cy + r() * cs, 1 + r() * 4, 0, 7); g.fill(); }
      g.fillStyle = 'rgba(255,255,255,0.92)'; g.font = '500 64px Garamond'; g.textAlign = 'center'; g.fillText('✦', cx + cs / 2, cy + cs / 2 + 20); }
    else { g.fillStyle = '#2a2433'; g.beginPath(); g.roundRect(cx, cy, cs, cs, 24); g.fill(); g.fillStyle = '#6d6578'; g.font = '400 150px Garamond'; g.textAlign = 'center'; g.fillText('?', cx + cs / 2, cy + cs / 2 + 50); }
    g.textAlign = 'left'; g.fillStyle = '#fff'; g.font = '500 40px Plex';
    if (!gone) { g.fillText('Lieblingssong ♥', 60, cy + cs + 80); g.fillStyle = '#d9c9ff'; g.font = '400 32px Plex'; g.fillText('Taylor Swift', 60, cy + cs + 128); }
    else { g.fillText('Titel nicht verfügbar', 60, cy + cs + 80); g.fillStyle = '#ff6b6b'; g.font = '400 30px Plex'; g.fillText('Künstlerin nicht gefunden', 60, cy + cs + 128); }
    const py = cy + cs + 190, pr = gone ? 0 : clamp(0.38 + t * 0.01);
    g.fillStyle = 'rgba(255,255,255,0.25)'; g.fillRect(60, py, SW - 120, 8); g.fillStyle = '#fff'; g.fillRect(60, py, (SW - 120) * pr, 8); g.beginPath(); g.arc(60 + (SW - 120) * pr, py + 4, 12, 0, 7); g.fill();
    g.font = '400 22px Plex'; g.fillText(gone ? '0:00' : `1:${String(22 + Math.floor(t)).padStart(2, '0')}`, 60, py + 44); g.textAlign = 'right'; g.fillText(gone ? '0:00' : '3:51', SW - 60, py + 44);
    // Equalizer
    for (let i = 0; i < 24; i++) { const hgt = gone ? 3 : 10 + Math.abs(Math.sin(t * 7 + i * 1.7) * Math.sin(t * 3.1 + i)) * 90; g.fillStyle = gone ? '#555' : `hsl(${300 + i * 3},90%,70%)`; g.fillRect(60 + i * 20, py + 190 - hgt, 12, hgt); }
    g.textAlign = 'center'; g.fillStyle = '#fff'; g.font = '400 70px Plex'; g.fillText(gone ? '▶' : '❚❚', SW / 2, py + 300);
  }
  // Video des Bruders (Hochkant-Video-App mit Zahlen)
  function videoUI(g, t, views) {
    g.clearRect(0, 0, 432, 936);
    g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(0, 0, 432, 70); g.fillStyle = 'rgba(0,0,0,0.45)'; g.fillRect(0, 780, 432, 156);
    g.fillStyle = '#fff'; g.font = '500 20px Plex'; g.textAlign = 'center'; g.fillText('Folge ich   Für dich', 216, 46);
    g.textAlign = 'left'; g.font = '500 21px Plex'; g.fillText('@kleinerbruder', 22, 820); g.font = '400 18px Plex'; g.fillText('meine schwester als die musik weg war 💀', 22, 850); g.fillText('#swiftie #fail', 22, 878);
    const items = [['♥', views * 0.12], ['💬', views * 0.004], ['↗', views * 0.02]];
    items.forEach(([ic, n], i) => { const y = 470 + i * 110; g.textAlign = 'center'; g.font = '400 44px Plex'; g.fillStyle = i === 0 ? '#ff3b6b' : '#fff'; g.fillText(ic, 396, y);
      g.fillStyle = '#fff'; g.font = '500 18px Plex'; g.fillText(n >= 1e6 ? (n / 1e6).toFixed(1).replace('.', ',') + ' Mio.' : n >= 1e3 ? Math.round(n / 1e3) + ' Tsd.' : String(Math.round(n)), 396, y + 34); });
    g.fillStyle = 'rgba(255,255,255,0.3)'; g.fillRect(0, 930, 432, 6); g.fillStyle = '#fff'; g.fillRect(0, 930, 432 * ((t * 0.18) % 1), 6);
    uiT.needsUpdate = true;
  }

  // Pose helpers
  function singPose(p, T, amt = 1) { const u = p.userData; posePerson(p, {});
    const sway = Math.sin(T * 3.4), bob = Math.abs(Math.sin(T * 3.4));
    u.hips.position.y = 0.92 - 0.03 * bob * amt; u.torso.rotation.z = 0.08 * sway * amt; u.torso.rotation.x = -0.05 * amt; u.head.rotation.x = -0.25 * amt + 0.06 * bob; u.head.rotation.z = -0.1 * sway * amt;
    u.armR.rotation.x = lerp(-0.1, -1.0, amt); u.armR.rotation.z = lerp(0.08, -0.3, amt); u.armR.userData.fore.rotation.x = lerp(-0.25, -2.45, amt);
    u.armL.rotation.x = lerp(-0.1, -0.6 - 0.9 * Math.max(0, Math.sin(T * 1.7)), amt); u.armL.rotation.z = lerp(-0.08, -0.5 - 0.4 * Math.max(0, Math.sin(T * 1.7)), amt); u.armL.userData.fore.rotation.x = lerp(-0.25, -0.4, amt);
    u.legL.rotation.x = 0.05 * sway * amt; u.legR.rotation.x = -0.05 * sway * amt; u.legL.userData.knee.rotation.x = 0.08 * bob * amt; u.legR.userData.knee.rotation.x = 0.08 * bob * amt; }

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.05;
    const t = T - shot.t0, id = shot.id, gone = T >= VANISH && T < RETURN;
    bulbs.forEach((m, i) => m.emissiveIntensity = 2.4 + 0.6 * Math.sin(T * 2 + i));
    updateScreen(bedPhone, [], {t: T, noDrops: true, gone, custom: player});
    // Mädchen (im Intro ist das Handy ihr POV)
    girl.visible = id !== 'intro';
    girl.position.set(0.25, 0, -0.1); girl.rotation.set(0, 0.25, 0);
    if (id !== 'viral') {
      const sing = T < STOP_SING ? 1 : 1 - smooth(STOP_SING, STOP_SING + 0.5, T);
      singPose(girl, T < STOP_SING ? T : STOP_SING, Math.max(sing, 0.001));
      if (T >= STOP_SING) { // stutzt, tippt an den Kopfhörer, dreht sich zum Bruder um, erschrickt
        const tap = smooth(TAP, TAP + 0.3, T) * (1 - smooth(TAP + 1.2, TAP + 1.5, T));
        gu.armL.rotation.x = lerp(gu.armL.rotation.x, -2.6, tap); gu.armL.rotation.z = lerp(gu.armL.rotation.z, -0.6, tap); gu.armL.userData.fore.rotation.x = lerp(-0.25, -2.0, tap);
        gu.head.rotation.z = 0.15 * tap; gu.armR.rotation.x = lerp(-0.1, -0.7, smooth(STOP_SING, STOP_SING + 0.6, T)); gu.armR.userData.fore.rotation.x = -0.9;
        const turn = smooth(SEE, SEE + 0.5, T); girl.rotation.y = lerp(0.25, Math.PI - 0.45, turn); gu.head.rotation.y = 0.3 * turn;
        const shock = smooth(SEE + 0.4, SEE + 0.7, T); gu.torso.rotation.x = -0.12 * shock; gu.armL.rotation.x = lerp(gu.armL.rotation.x, -0.9, shock); gu.armL.rotation.z = lerp(gu.armL.rotation.z, -0.9, shock);
        const chase = smooth(SEE + 1.4, SEE + 2.2, T); gu.armR.rotation.x = lerp(gu.armR.rotation.x, -1.7, chase); gu.armR.userData.fore.rotation.x = lerp(-0.9, -0.2, chase); // zeigt mit der Bürste auf ihn
        if (chase > 0) { girl.position.x += 0.45 * chase; girl.position.z -= 0.6 * chase; }
      }
    } else { // sitzt auf dem Bett, Hände vors Gesicht
      girl.position.set(-RW + 0.8, 0, 0.35); girl.rotation.set(0, 1.25, 0); posePerson(girl, {});
      gu.hips.position.y = 0.5; for (const lg of [gu.legL, gu.legR]) { lg.rotation.x = -1.5; lg.userData.knee.rotation.x = 1.5; }
      gu.pl.forEach((g, i) => { const lg = i ? gu.legR : gu.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
      const rock = Math.sin(T * 2.2) * 0.06; gu.torso.rotation.x = 0.35 + rock; gu.head.rotation.x = 0.35;
      for (const [a, s] of [[gu.armL, -1], [gu.armR, 1]]) { a.rotation.x = -1.0; a.rotation.z = -s * 0.3; a.userData.fore.rotation.x = -2.5; }
    }
    // Bruder kommt rein und filmt
    const doorOpen = id === 'viral' ? 0 : smooth(BRO_IN - 0.4, BRO_IN + 0.2, T);
    door.rotation.y = 1.5 * doorOpen;
    bro.visible = id !== 'viral' && T > BRO_IN - 0.3;
    if (bro.visible) { const walk = smooth(BRO_IN, BRO_IN + 1.0, T); bro.position.set(1.62, 0, lerp(ZB - 0.9, ZB + 0.45, walk)); bro.rotation.y = -0.35;
      posePerson(bro, {walk: T * 9 * (walk < 1 ? 1 : 0), walkAmp: walk < 1 ? 0.8 : 0});
      const film = smooth(BRO_FILM - 0.4, BRO_FILM, T), laugh = T > SEE + 0.3 ? Math.abs(Math.sin(T * 14)) : 0;
      const bu = bro.userData; bu.armR.rotation.x = lerp(bu.armR.rotation.x, -1.6, film); bu.armR.userData.fore.rotation.x = lerp(-0.25, -0.5, film);
      bu.torso.rotation.x = 0.12 * laugh; bu.armL.rotation.x = -0.9 * (T > SEE + 0.3 ? 1 : 0); bu.armL.userData.fore.rotation.x = -1.4 * (T > SEE + 0.3 ? 1 : 0);
      const flee = smooth(SEE + 2.0, SEE + 2.6, T); bro.position.z -= 1.4 * flee; bro.rotation.y += Math.PI * smooth(SEE + 1.8, SEE + 2.1, T); }
    updateScreen(broPhone, [], {t: T, noDrops: true, custom: (g, st, SW, SH) => { g.fillStyle = '#26303d'; g.fillRect(0, 0, SW, SH); g.fillStyle = '#ff3b30'; g.beginPath(); g.arc(SW / 2, SH - 150, 50, 0, 7); g.fill(); }});

    // Kamera
    rig.visible = id === 'intro' || id === 'viral'; live.visible = ui.visible = id === 'viral'; phone.userData.scr.visible = id === 'intro';
    camera.fov = 50;
    if (id === 'intro') { // ihr Handy, dahinter das Zimmer
      camera.position.set(0.2 + Math.sin(t * 0.8) * 0.01, 1.42, 1.6); camera.lookAt(0.6, 1.0, -1.4);
      updateScreen(phone, [], {t: T, noDrops: true, gone: false, custom: player});
    } else if (id === 'wait') {
      const u = smooth(0, 6.5, t); camera.fov = 52; camera.position.set(lerp(0.9, 0.6, u), lerp(1.4, 1.35, u), lerp(2.65, 2.35, u)); camera.lookAt(lerp(0.3, 0.35, u), 1.0, -0.3);
    } else if (id === 'room_drop') {
      const u = smooth(0, 7, t); camera.fov = 54; camera.position.set(lerp(0.0, 0.1, u), 1.45, lerp(2.7, 2.5, u)); camera.lookAt(lerp(0.45, 0.8, smooth(2.0, 4.5, t)), 1.05, -1.0);
    } else { // viral: POV des Bruders, das Video läuft auf seinem Handy
      const u = smooth(0, 15, t);
      camera.position.set(lerp(1.6, 1.3, u), 1.2, lerp(2.2, 1.9, u)); camera.lookAt(-RW + 0.8, 0.75, 0.35);
      const views = Math.min(1e7, Math.pow(10, lerp(3.2, 7, smooth(2, 11, t))));
      // Video zeigt sie beim Singen (Pose kurz umstellen)
      const sv = {pos: girl.position.clone(), rot: girl.rotation.y}; girl.position.set(0.25, 0, -0.1); girl.rotation.set(0, 0.25, 0); singPose(girl, 6 + t, 1);
      bro.visible = false; rig.visible = false; girl.rotation.set(0, Math.PI - 0.6, 0); vidCam.position.set(1.62, 1.0, ZB + 0.45); vidCam.lookAt(0.25, 1.05, -0.1); vidCam.updateProjectionMatrix();
      renderer.setRenderTarget(RT); renderer.render(scene, vidCam); renderer.setRenderTarget(null); rig.visible = true;
      girl.position.copy(sv.pos); girl.rotation.set(0, sv.rot, 0);
      // zurück in die Sitzpose
      posePerson(girl, {}); gu.hips.position.y = 0.5; for (const lg of [gu.legL, gu.legR]) { lg.rotation.x = -1.5; lg.userData.knee.rotation.x = 1.5; }
      gu.pl.forEach((g, i) => { const lg = i ? gu.legR : gu.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
      const rock = Math.sin(T * 2.2) * 0.06; gu.torso.rotation.x = 0.35 + rock; gu.head.rotation.x = 0.35;
      for (const [a, s] of [[gu.armL, -1], [gu.armR, 1]]) { a.rotation.x = -1.0; a.rotation.z = -s * 0.3; a.userData.fore.rotation.x = -2.5; }
      videoUI(uiC.getContext('2d'), t, views);
      rig.position.set(0.035, -0.085, -0.3); rig.rotation.set(-0.05, -0.08, 0.04);
    }
    camera.updateProjectionMatrix();
  }};
}
