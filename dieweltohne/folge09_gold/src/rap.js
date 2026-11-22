// Parkdeck auf einem Hochhaus bei Sonnenuntergang: Musikvideo-Dreh. Der Rapper zeigt seine Kette – dann ist alles Gold weg.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, skyDome, easeOut, makePerson, posePerson, envMap, makeCar} from './lib.js';
import {makePhone, makeHands} from './phone.js';
import {bling, setBling, glitter, updateGlitter} from './gold.js';
import {VANISH, RETURN} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.55;
  scene.fog = new THREE.Fog('#d99a72', 80, 520);
  scene.add(skyDome('#24305e', '#c7684a', '#ffbf7a', 600));
  const hemi = new THREE.HemisphereLight('#ffd2b0', '#3a3440', 0.8); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#ffb070', 2.6); sun.position.set(-18, 9, -22); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 80}); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03; scene.add(sun);
  const fill = new THREE.PointLight('#ffffff', 6, 12, 1.5); fill.position.set(1.8, 2.0, 3.0); scene.add(fill); // Ringlicht

  // Parkdeck
  const deckT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#8d8a85'; g.fillRect(0, 0, w, h); const r = rng(4);
    for (let i = 0; i < 9000; i++) { const v = 110 + r() * 60; g.fillStyle = `rgba(${v},${v},${v - 4},0.3)`; g.fillRect(r() * w, r() * h, 2, 2); }
    for (let i = 0; i < 14; i++) { g.fillStyle = 'rgba(40,40,40,0.08)'; g.beginPath(); g.ellipse(r() * w, r() * h, 20 + r() * 70, 10 + r() * 30, r() * 3, 0, 7); g.fill(); } });
  deckT.wrapS = deckT.wrapT = THREE.RepeatWrapping; deckT.repeat.set(8, 8);
  mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({map: deckT, roughness: 0.85}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const lineM = mat('#f2efe6', {roughness: 0.7});
  for (let i = -6; i <= 6; i++) { const l = mesh(new THREE.PlaneGeometry(0.1, 5), lineM, i * 2.6 + 1.3, 0.004, -6, scene); l.rotation.x = -Math.PI / 2; l.receiveShadow = true; l.castShadow = false; }
  // Brüstung
  const wallM = mat('#9b9690', {roughness: 0.9});
  mesh(new THREE.BoxGeometry(60, 1.1, 0.3), wallM, 0, 0.55, -10, scene);
  for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(0.3, 1.1, 30), wallM, s * 14, 0.55, 2, scene);
  // Laternen
  const poleM = mat('#2b2f33', {metalness: 0.6});
  for (const [x, z] of [[-9, -8], [9, -8], [-12, 4]]) { mesh(new THREE.CylinderGeometry(0.06, 0.08, 5, 8), poleM, x, 2.5, z, scene); mesh(new THREE.BoxGeometry(0.7, 0.12, 0.25), poleM, x + 0.3, 5, z, scene); }
  // Skyline hinter dem Deck
  { const r = rng(31); for (let i = 0; i < 60; i++) { const x = -260 + r() * 520, z = -60 - r() * 260, w = 12 + r() * 22, h = 20 + r() * 90;
      mesh(new THREE.BoxGeometry(w, h, 14), new THREE.MeshStandardMaterial({map: facadeTex(['#8e8a96', '#a59c92', '#7c8796'][i % 3], i + 9, Math.round(h / 3.4), 5), roughness: 0.85}), x, h / 2 - 25, z, scene); } }
  // Auto und Ringlicht
  const car = makeCar(4, {color: '#4b2a7a'}); car.position.set(-3.0, 0, -3.4); car.rotation.y = 0.55; scene.add(car);
  const tri = new THREE.Group(); tri.position.set(1.8, 0, 3.0); scene.add(tri);
  for (let k = 0; k < 3; k++) { const leg = mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.7, 6), poleM, Math.cos(k * 2.1) * 0.25, 0.8, Math.sin(k * 2.1) * 0.25, tri); leg.rotation.set(Math.sin(k * 2.1) * 0.3, 0, -Math.cos(k * 2.1) * 0.3); }
  const ring = mesh(new THREE.TorusGeometry(0.28, 0.03, 8, 40), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#fff8ee', emissiveIntensity: 2.5}), 0, 1.75, 0, tri); ring.rotation.y = -0.5;
  // Lautsprecherbox
  mesh(new RoundedBoxGeometry(0.5, 0.8, 0.45, 2, 0.03), mat('#1d1f22'), 2.4, 0.4, -1.6, scene);
  mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.02, 20), mat('#333'), 2.4, 0.5, -1.36, scene).rotation.x = Math.PI / 2;

  // Rapper und Freunde
  const rapper = makePerson(41, {skin: '#7a4d33', hair: '#111', top: '#1b1b1f', pants: '#2b2f3a', shoe: '#f2f2f2', height: 1.0});
  scene.add(rapper); const b = bling(rapper);
  const fr = [makePerson(52, {skin: '#d9a47e', top: '#c23b6a', pants: '#1f2a44', hair: '#2a1d15'}), makePerson(57, {skin: '#f1c7a5', top: '#e8e2d4', pants: '#3a3a3a', hair: '#c9a35b', longHair: true})];
  fr.forEach(p => scene.add(p));
  const gl = glitter(700, 0.05); scene.add(gl);

  // Kamera und Handy (Intro)
  const camera = new THREE.PerspectiveCamera(45, 1080 / 1920, 0.02, 2000); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#1e2126'); const hands = makeHands('#e3b08e', '#3a3f48');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig);
  rig.position.set(0.02, -0.07, -0.29); rig.rotation.set(-0.08, 0.04, -0.03);
  const RT = new THREE.WebGLRenderTarget(432, 936); RT.texture.colorSpace = THREE.SRGBColorSpace;
  const phoneCam = new THREE.PerspectiveCamera(58, 432 / 936, 0.05, 2000);
  const uiC = document.createElement('canvas'); uiC.width = 432; uiC.height = 936; const uiT = new THREE.CanvasTexture(uiC); uiT.colorSpace = THREE.SRGBColorSpace;
  const pw = phone.userData.pw, phh = phone.userData.ph;
  mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: RT.texture, toneMapped: false}), 0, 0, 0.0052, phone);
  mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: uiT, transparent: true, toneMapped: false}), 0, 0, 0.0056, phone);
  phone.userData.scr.visible = false;

  const wp = o => o.getWorldPosition(new THREE.Vector3());
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id;
    const gone = T >= VANISH && T < RETURN;
    // Rapper: rappt in die Kamera, Kopfnicken im Takt (ca. 92 bpm)
    rapper.position.set(0, 0, 0); rapper.rotation.set(0, 0.08, 0); posePerson(rapper, {});
    const u = rapper.userData, beat = T * 1.53 * Math.PI * 2;
    const shock = smooth(VANISH + 0.15, VANISH + 0.7, T), what = smooth(VANISH + 2.6, VANISH + 3.3, T), sag = smooth(VANISH + 4.5, VANISH + 5.5, T);
    const groove = 1 - shock;
    u.hips.position.y = 0.92 + Math.abs(Math.sin(beat / 2)) * 0.03 * groove;
    u.head.rotation.x = Math.sin(beat) * 0.12 * groove + 0.5 * shock * (1 - what) + 0.15 * sag;
    u.torso.rotation.y = Math.sin(beat / 4) * 0.15 * groove;
    // Arme: Gesten, dann Hände an die Brust, dann "Was?"
    const gx = -1.1 + Math.sin(beat / 2) * 0.35, gz = 0.35 + Math.sin(beat / 2 + 1) * 0.15;
    u.armR.rotation.x = lerp(lerp(gx, -0.85, shock), -0.5, what); u.armR.rotation.z = lerp(lerp(gz, 0.55, shock), 0.95, what);
    u.armR.userData.fore.rotation.x = lerp(lerp(-1.2, -1.75, shock), -0.9, what);
    u.armL.rotation.x = lerp(lerp(-0.4 + Math.sin(beat / 2 + 2) * 0.2, -0.8, shock), -0.5, what); u.armL.rotation.z = lerp(lerp(-0.25, -0.5, shock), -0.95, what);
    u.armL.userData.fore.rotation.x = lerp(lerp(-0.9, -1.75, shock), -0.9, what);
    if (sag > 0) { u.armR.rotation.z = lerp(u.armR.rotation.z, 0.12, sag); u.armL.rotation.z = lerp(u.armL.rotation.z, -0.12, sag); u.armR.rotation.x = lerp(u.armR.rotation.x, -0.1, sag); u.armL.rotation.x = lerp(u.armL.rotation.x, -0.1, sag); u.armR.userData.fore.rotation.x = lerp(u.armR.userData.fore.rotation.x, -0.3, sag); u.armL.userData.fore.rotation.x = lerp(u.armL.userData.fore.rotation.x, -0.3, sag); }
    setBling(b, !gone);
    // Freunde: tanzen mit, dann lachen sie
    const laugh = smooth(VANISH + 1.2, VANISH + 1.8, T);
    [[-1.05, -1.5, 0.3], [1.05, -1.3, -0.35]].forEach(([x, z, ry], i) => { const p = fr[i]; p.position.set(x, 0, z); p.rotation.set(0, ry, 0); posePerson(p, {});
      const q = p.userData, sh = Math.sin(T * 21 + i) * 0.05 * laugh;
      q.hips.position.y = 0.92 + Math.abs(Math.sin(beat / 2 + i)) * 0.025 * (1 - laugh);
      q.head.rotation.x = Math.sin(beat + i) * 0.1 * (1 - laugh) - 0.2 * laugh;
      q.torso.rotation.x = (0.4 + sh) * laugh * (i ? 1 : 0.7);
      q.armL.rotation.x = -1.0 * laugh; q.armL.userData.fore.rotation.x = -1.4 * laugh; q.armR.rotation.x = lerp(-0.6 + Math.sin(beat / 2) * 0.3, -0.3, laugh); q.armR.rotation.z = 0.3 + 0.4 * laugh;
      if (i === 0) { q.armR.rotation.x = lerp(-0.6, -1.6, laugh); q.armR.userData.fore.rotation.x = -0.4; } }); // zeigt auf ihn
    // Glitzer beim Verschwinden
    updateGlitter(gl, b.items.slice(0, 12).map(wp).concat([wp(b.chain)]), T - VANISH, 1.0, 0.18, 0.25);

    // Kamera
    rig.visible = id === 'intro'; camera.fov = 45;
    if (id === 'intro') {
      camera.position.set(0.7 + noise1(T, 1) * 0.02, 1.55 + noise1(T, 3) * 0.01, 4.4); camera.lookAt(0.1, 1.25, 0);
      phoneCam.position.copy(camera.position).add(V3(-0.02, -0.08, -0.3)); phoneCam.lookAt(0, 1.25, 0); phoneCam.updateProjectionMatrix();
      rig.visible = false; gl.visible = false; renderer.setRenderTarget(RT); renderer.render(scene, phoneCam); renderer.setRenderTarget(null); rig.visible = true;
      const g = uiC.getContext('2d'); g.clearRect(0, 0, 432, 936); g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(0, 0, 432, 70); g.fillRect(0, 800, 432, 136);
      g.fillStyle = '#ff3b30'; g.beginPath(); g.arc(150, 38, 9, 0, 7); g.fill(); g.fillStyle = '#fff'; g.font = '500 22px Plex'; g.textAlign = 'left'; g.fillText(`REC 00:0${Math.floor(t + 4)}`, 166, 46);
      g.strokeStyle = '#fff'; g.lineWidth = 6; g.beginPath(); g.arc(216, 868, 36, 0, 7); g.stroke(); g.fillStyle = '#ff3b30'; g.beginPath(); g.roundRect(198, 850, 36, 36, 6); g.fill();
      uiT.needsUpdate = true;
    } else if (id === 'wait') {
      const k = smooth(3.5, 10, T);
      camera.position.set(lerp(1.5, 0.35, k) + noise1(T, 2) * 0.02, lerp(1.45, 1.55, k), lerp(5.6, 2.2, k)); camera.lookAt(0, lerp(1.25, 1.45, k), 0);
    } else { // rap
      const k = smooth(VANISH + 2.2, VANISH + 4.2, T);
      camera.position.set(lerp(0.3, 0.8, k) + noise1(T, 2) * 0.015, lerp(1.62, 1.6, k), lerp(2.0, 5.6, k)); camera.lookAt(0, lerp(1.58, 1.2, k), 0);
    }
    camera.updateProjectionMatrix();
  }};
}
