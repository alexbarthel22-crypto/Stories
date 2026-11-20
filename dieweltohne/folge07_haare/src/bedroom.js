// Jugendzimmer am Nachmittag. Selfie-Video mit der Frontkamera: Haare werfen, dann Glatze ohne Augenbrauen und Wimpern.
// Hinten auf dem Bett eine flauschige Katze, die zur Nacktkatze wird. Am Ende (final) sitzt sie am Boden: Haare zurück, Gehör weg.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeOut, envMap} from './lib.js';
import {makeHead, furCoat, strandMesh} from './furhair.js';
import {VANISH, RETURN} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#d8d0c8');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.35;
  scene.add(new THREE.HemisphereLight('#fff4ea', '#7a6a60', 0.9));
  const sun = new THREE.DirectionalLight('#ffe2b8', 2.6); sun.position.set(3.5, 3.2, 1.5); sun.target.position.set(0, 1, -1);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -3, right: 3, top: 3, bottom: -3, near: 0.5, far: 12}); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02;
  scene.add(sun, sun.target);
  const ring = new THREE.PointLight('#fff1e6', 1.6, 3, 1.5); ring.position.set(0.0, 1.55, 0.7); scene.add(ring); // Ringlicht hinter dem Handy
  const fairyL = new THREE.PointLight('#ffb070', 0.8, 3, 1.5); fairyL.position.set(-0.6, 2.0, -2.0); scene.add(fairyL);

  // Raum: 4 x 4 m
  const wallT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#e9d9d2'; g.fillRect(0, 0, w, h); const r = rng(4); for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '255,255,255' : '160,130,120'},${r() * 0.06})`; g.fillRect(r() * w, r() * h, 2, 2); } });
  const wallM = new THREE.MeshStandardMaterial({map: wallT, roughness: 0.95});
  mesh(new THREE.BoxGeometry(4, 2.7, 0.1), wallM, 0, 1.35, -2.4, scene).receiveShadow = true;
  mesh(new THREE.BoxGeometry(0.1, 2.7, 4), wallM, -2.0, 1.35, -0.4, scene);
  mesh(new THREE.BoxGeometry(0.1, 2.7, 4), wallM, 2.0, 1.35, -0.4, scene);
  mesh(new THREE.BoxGeometry(4, 2.7, 0.1), wallM, 0, 1.35, 1.6, scene);
  const floorT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#b48a62'; g.fillRect(0, 0, w, h); const r = rng(9); for (let y = 0; y < h; y += 40) { g.fillStyle = 'rgba(60,30,10,0.18)'; g.fillRect(0, y, w, 2); for (let i = 0; i < 30; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '255,230,200' : '70,40,20'},${r() * 0.1})`; g.fillRect(r() * w, y + r() * 38, 40 + r() * 120, 2); } } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(3, 3);
  const fl = mesh(new THREE.PlaneGeometry(4, 4), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.6}), 0, 0, -0.4, scene); fl.rotation.x = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(4, 4), mat('#f2ece6'), 0, 2.7, -0.4, scene).rotation.x = Math.PI / 2;
  // Fenster rechts mit Licht
  const winT = canvasTex(256, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#bfe0ff'); gr.addColorStop(1, '#fff3dc'); g.fillStyle = gr; g.fillRect(0, 0, w, h); g.fillStyle = '#e8e8e4'; g.fillRect(w / 2 - 4, 0, 8, h); g.fillRect(0, h / 2 - 4, w, 8); });
  const win = mesh(new THREE.PlaneGeometry(1.2, 1.3), new THREE.MeshBasicMaterial({map: winT}), 1.94, 1.5, -1.2, scene); win.rotation.y = -Math.PI / 2;
  // Poster, Lichterkette, Regal
  const poster = (seed, c1, c2, txt) => canvasTex(300, 420, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, c1); gr.addColorStop(1, c2); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(seed); for (let i = 0; i < 14; i++) { g.fillStyle = `rgba(255,255,255,${r() * 0.25})`; g.beginPath(); g.arc(r() * w, r() * h, 10 + r() * 40, 0, 7); g.fill(); }
    g.fillStyle = '#fff'; g.font = '600 38px Plex'; g.textAlign = 'center'; g.fillText(txt, w / 2, h - 40); });
  [[-0.9, 1.75, 'GOOD VIBES', '#ff8fb1', '#7a5cff', 2], [0.55, 1.85, 'TOKYO', '#2ec5c9', '#1b3a6b', 5], [1.25, 1.55, '☾ ✦', '#f6c26b', '#d0567a', 8]].forEach(([x, y, t, a, b, s]) =>
    mesh(new THREE.PlaneGeometry(0.5, 0.7), new THREE.MeshStandardMaterial({map: poster(s, a, b, t), roughness: 0.7}), x, y, -2.34, scene));
  const bulbM = new THREE.MeshStandardMaterial({color: '#ffd9a0', emissive: '#ffb050', emissiveIntensity: 2.5});
  for (let i = 0; i < 26; i++) { const x = -1.9 + i * 0.15; mesh(new THREE.SphereGeometry(0.018, 8, 6), bulbM, x, 2.25 - Math.sin(i / 25 * Math.PI) * 0.18 + (i % 2) * 0.02, -2.32, scene).castShadow = false; }
  // Bett links hinten mit Decke und Kissen
  const bed = new THREE.Group(); bed.position.set(-1.0, 0, -1.55); scene.add(bed);
  mesh(new RoundedBoxGeometry(1.5, 0.35, 1.9, 3, 0.05), mat('#cfc4b8'), 0, 0.2, 0, bed);
  mesh(new RoundedBoxGeometry(1.46, 0.14, 1.84, 4, 0.06), mat('#f4f1ec', {roughness: 0.95}), 0, 0.43, 0, bed);
  mesh(new RoundedBoxGeometry(1.48, 0.08, 1.2, 4, 0.04), mat('#a7c4e8', {roughness: 0.95}), 0, 0.52, 0.32, bed);
  mesh(new RoundedBoxGeometry(0.6, 0.14, 0.35, 4, 0.06), mat('#ffffff', {roughness: 0.95}), -0.35, 0.56, -0.7, bed);
  mesh(new RoundedBoxGeometry(0.5, 0.14, 0.3, 4, 0.06), mat('#f7b6c8', {roughness: 0.95}), 0.35, 0.57, -0.72, bed);
  // Schreibtisch rechts hinten mit Spiegel und Bürste
  mesh(new RoundedBoxGeometry(1.1, 0.05, 0.55, 2, 0.01), mat('#f4f1ec'), 1.3, 0.75, -2.0, scene);
  for (const [x, z] of [[0.8, -2.2], [1.8, -2.2], [0.8, -1.8], [1.8, -1.8]]) mesh(new THREE.BoxGeometry(0.04, 0.75, 0.04), mat('#d8d4ce'), x, 0.375, z, scene);
  mesh(new THREE.TorusGeometry(0.22, 0.02, 10, 40), mat('#d9b56a', {metalness: 0.8, roughness: 0.3}), 1.3, 1.08, -2.28, scene);
  mesh(new THREE.CircleGeometry(0.21, 40), new THREE.MeshStandardMaterial({color: '#cfd8e0', metalness: 0.95, roughness: 0.05}), 1.3, 1.08, -2.29, scene);
  // Pflanze
  mesh(new THREE.CylinderGeometry(0.1, 0.08, 0.2, 16), mat('#e6e1da'), 1.65, 0.88, -2.05, scene);
  for (let i = 0; i < 9; i++) { const l = mesh(new THREE.SphereGeometry(0.06, 8, 6), mat('#4f8a4a'), 1.65 + Math.sin(i * 2.4) * 0.08, 1.02 + (i % 3) * 0.05, -2.05 + Math.cos(i * 2.4) * 0.08, scene); l.scale.set(1, 0.4, 1.6); l.rotation.y = i; }

  // Katze auf dem Bett: flauschig (Fell) und als Nacktkatze
  const cat = new THREE.Group(); cat.position.set(-0.75, 0.56, -1.45); cat.rotation.y = 0.7; scene.add(cat);
  const fluffy = new THREE.Group(); cat.add(fluffy);
  const furBase = mat('#d98a3a', {roughness: 0.95});
  const cb = mesh(new THREE.SphereGeometry(0.16, 20, 16), furBase, 0, 0.13, 0, fluffy); cb.scale.set(0.95, 0.85, 1.25);
  const ch = mesh(new THREE.SphereGeometry(0.095, 20, 16), furBase, 0, 0.3, 0.16, fluffy); ch.scale.set(1.15, 1, 1);
  for (const s of [-1, 1]) { const e = mesh(new THREE.ConeGeometry(0.035, 0.07, 8), furBase, s * 0.06, 0.39, 0.15, fluffy); e.rotation.z = -s * 0.25; }
  fluffy.add(furCoat(2600, 3, {rx: 0.16, ry: 0.14, rz: 0.2, len: 0.045, width: 0.009, center: V3(0, 0.13, 0), dir: V3(0, -0.3, -1)}));
  fluffy.add(furCoat(1100, 4, {rx: 0.11, ry: 0.1, rz: 0.1, len: 0.03, width: 0.007, center: V3(0, 0.3, 0.16), dir: V3(0, -0.2, -0.6)}));
  const tailC = new THREE.CatmullRomCurve3([V3(0, 0.08, -0.2), V3(0.12, 0.05, -0.32), V3(0.25, 0.08, -0.3), V3(0.3, 0.14, -0.18)]);
  const tail = mesh(new THREE.TubeGeometry(tailC, 16, 0.045, 10, false), furBase, 0, 0, 0, fluffy);
  const eyeY = mat('#c9d64a', {roughness: 0.2}), pup = mat('#111');
  for (const g of [fluffy]) for (const s of [-1, 1]) { mesh(new THREE.SphereGeometry(0.018, 12, 10), eyeY, s * 0.04, 0.32, 0.245, g); mesh(new THREE.SphereGeometry(0.008, 8, 6), pup, s * 0.04, 0.32, 0.262, g).scale.set(0.5, 1.3, 0.5); }
  const naked = new THREE.Group(); cat.add(naked); naked.visible = false;
  const nk = mat('#d8a99a', {roughness: 0.6});
  const nb = mesh(new THREE.SphereGeometry(0.12, 20, 16), nk, 0, 0.11, 0, naked); nb.scale.set(0.85, 0.8, 1.3);
  const nh = mesh(new THREE.SphereGeometry(0.07, 20, 16), nk, 0, 0.27, 0.15, naked); nh.scale.set(1.05, 0.95, 1);
  for (const s of [-1, 1]) { const e = mesh(new THREE.ConeGeometry(0.045, 0.12, 10), nk, s * 0.055, 0.37, 0.13, naked); e.rotation.z = -s * 0.45;
    for (let w = 0; w < 3; w++) mesh(new THREE.TorusGeometry(0.06, 0.004, 4, 20, 1.2), mat('#c4907f'), s * 0.03, 0.29 + w * 0.012, 0.155, naked).rotation.set(0, 0, Math.PI / 2 + 0.4); }
  for (const s of [-1, 1]) { mesh(new THREE.SphereGeometry(0.022, 12, 10), eyeY, s * 0.035, 0.29, 0.21, naked); mesh(new THREE.SphereGeometry(0.01, 8, 6), pup, s * 0.035, 0.29, 0.23, naked).scale.set(0.6, 1.2, 0.5); }
  const nTail = mesh(new THREE.TubeGeometry(tailC, 16, 0.015, 8, false), nk, 0, 0, 0, naked);
  for (let w = 0; w < 6; w++) mesh(new THREE.TorusGeometry(0.1, 0.004, 4, 20, 1.6), mat('#c4907f'), 0, 0.12 + w * 0.02, -0.02 - w * 0.03, naked).rotation.set(0, Math.PI / 2, Math.PI / 2 - 0.8);
  for (const g of [fluffy, naked]) for (const [x, z] of [[-0.07, 0.12], [0.07, 0.12], [-0.08, -0.12], [0.08, -0.12]]) mesh(new THREE.CapsuleGeometry(0.025, 0.05, 4, 8), g === fluffy ? furBase : nk, x, 0.02, z, g);

  // Mädchen
  const girl = new THREE.Group(); scene.add(girl);
  const hoodM = mat('#b7a6e0', {roughness: 0.95});
  const torso = mesh(new THREE.CapsuleGeometry(0.17, 0.3, 6, 20), hoodM, 0, 1.12, -0.02, girl); torso.scale.set(1.15, 1, 0.68);
  const hood = mesh(new THREE.TorusGeometry(0.1, 0.035, 10, 24), hoodM, 0, 1.33, -0.05, girl); hood.rotation.x = Math.PI / 2 - 0.3;
  for (const s of [-1, 1]) mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.16, 6), mat('#ffffff'), s * 0.04, 1.24, 0.08, girl);
  const head = makeHead({seed: 11}); head.position.set(0, 1.53, 0); girl.add(head);
  const H = head.userData;
  // Arm, der in die Haare greift (links im Bild = rechter Arm des Mädchens ist -x)
  const skinM = H.sk;
  const sh = new THREE.Group(); sh.position.set(-0.2, 1.33, -0.02); girl.add(sh);
  mesh(new THREE.CapsuleGeometry(0.05, 0.22, 6, 12), hoodM, 0, -0.14, 0, sh);
  const fore = new THREE.Group(); fore.position.y = -0.28; sh.add(fore);
  mesh(new THREE.CapsuleGeometry(0.044, 0.2, 6, 12), hoodM, 0, -0.12, 0, fore);
  const hand = new THREE.Group(); hand.position.y = -0.27; fore.add(hand);
  mesh(new THREE.SphereGeometry(0.04, 16, 12), skinM, 0, 0, 0, hand).scale.set(1, 1.2, 0.55);
  for (let i = 0; i < 4; i++) { const f = mesh(new THREE.CapsuleGeometry(0.01, 0.045, 4, 8), skinM, -0.025 + i * 0.017, -0.06, 0, hand); f.rotation.x = 0.2; }
  // anderer Arm hält das Handy (zur Kamera hin)
  const sh2 = new THREE.Group(); sh2.position.set(0.2, 1.33, -0.02); girl.add(sh2);
  mesh(new THREE.CapsuleGeometry(0.05, 0.24, 6, 12), hoodM, 0, -0.14, 0, sh2);
  const fore2 = new THREE.Group(); fore2.position.y = -0.28; sh2.add(fore2);
  mesh(new THREE.CapsuleGeometry(0.044, 0.22, 6, 12), hoodM, 0, -0.13, 0, fore2);

  const camera = new THREE.PerspectiveCamera(62, 1080 / 1920, 0.02, 60);
  const eyeBase = H.eyes.map(e => e.scale.clone());
  return {scene, camera, update(shot, T) {
    const id = shot.id, t = T - shot.t0;
    const gone = T >= VANISH && T < RETURN;
    H.hairG.visible = !gone; H.brows.forEach(b => b.visible = !gone); H.lashes.forEach(l => l.visible = !gone);
    fluffy.visible = !gone; naked.visible = gone;
    // Pose
    let headY = 0, headX = 0, headZ = 0, flip = 0, armUp = 0, mouthO = 0, eyeW = 1, bodyX = 0, sway = 0;
    if (id === 'intro' || id === 'wait') {
      // Haare werfen bei 1.2 s und 6.5 s, dazwischen posen
      const f1 = Math.exp(-Math.pow((T - 1.4) / 0.35, 2)), f2 = Math.exp(-Math.pow((T - 6.6) / 0.35, 2));
      headY = 0.35 * Math.sin(T * 0.7) * 0.4 + (f1 - f2) * 0.35; headZ = (f1 + f2) * 0.12; flip = f1 + f2;
      armUp = 0.6 + 0.4 * Math.sin(T * 0.9); mouthO = 0.25 + 0.25 * Math.max(0, Math.sin(T * 2.2));
    } else if (id === 'selfie') {
      const shock = smooth(VANISH + 0.25, VANISH + 0.6, T);
      eyeW = 1 + shock * 0.35; mouthO = shock * 1.0 * (0.85 + 0.15 * Math.sin(T * 9));
      armUp = 1 + smooth(VANISH + 0.8, VANISH + 1.4, T) * 0.6; headY = noise1(T * 2, 3) * 0.08 * shock; headX = -0.08 * shock;
      sway = smooth(13.0, 16.0, T); // erster Schwindel
    } else if (id === 'final') {
      mouthO = 0.35 + 0.2 * Math.sin(T * 3.1); headY = 0.25 * Math.sin(t * 0.6); headZ = 0.12 * Math.sin(t * 0.45 + 1); headX = 0.1; armUp = 1.3; eyeW = 1.05;
    }
    head.rotation.set(headX, headY, headZ + sway * 0.15 * Math.sin(T * 1.7));
    H.hairG.rotation.set(0, -flip * 0.15, flip * 0.08);
    H.eyes.forEach((e, i) => e.scale.copy(eyeBase[i]).multiplyScalar(eyeW));
    H.lids.forEach(l => l.rotation.x = 0.55 - (eyeW - 1) * 1.2);
    // Blinzeln
    const bl = Math.max(0, 1 - Math.abs(((T * 0.37) % 1) - 0.5) * 40); H.lids.forEach(l => l.rotation.x += bl * 0.9 * (id === 'selfie' ? 0 : 1));
    H.mouth.scale.set(1.2, 0.1 + mouthO * 0.9, 0.5); H.lipL.position.y = -0.066 - mouthO * 0.012;
    sh.rotation.set(-1.4 * clamp(armUp), 0, -0.4 - 0.9 * clamp(armUp - 0.3)); fore.rotation.set(-1.2 * clamp(armUp), 0, 0);
    if (id === 'selfie' || id === 'final') { sh.rotation.set(-0.3, 0, -0.15); fore.rotation.set(-0.6, 0, 0); }
    sh2.rotation.set(-1.25, 0, 0.35); fore2.rotation.set(-0.5, 0, 0);
    // Katze zuckt
    cat.rotation.y = 0.7 + (gone ? noise1(T * 3, 5) * 0.12 : 0); cat.position.y = 0.56;
    // Kamera = Frontkamera des Handys in der ausgestreckten Hand
    camera.fov = 56;
    let cp = V3(0.1, 1.55, 0.72), look = V3(0, 1.45, 0);
    if (id === 'selfie' && T > 13.3) { // Handy schwenkt zur Katze
      const k = smooth(13.3, 14.3, T); cp = V3(lerp(0.1, -0.15, k), lerp(1.55, 1.2, k), lerp(0.72, -0.4, k)); look = V3(lerp(0, -0.75, k), lerp(1.48, 0.8, k), lerp(0, -1.45, k));
    }
    if (id === 'final') { cp = V3(0.1, 1.5 - 0.62, 0.66); look = V3(0, 1.45 - 0.62, 0); }
    girl.position.y = id === 'final' ? -0.62 : 0; // final: sitzt auf dem Boden
    girl.rotation.z = id === 'final' ? 0.06 * Math.sin(t * 0.5) : 0;
    const shake = (id === 'selfie' ? 0.006 + sway * 0.012 : 0.003) + (id === 'final' ? 0.006 : 0);
    camera.position.set(cp.x + noise1(T * 2.3, 1) * shake, cp.y + noise1(T * 2.1, 2) * shake, cp.z);
    camera.lookAt(look); camera.rotateZ((id === 'selfie' ? sway * 0.08 * Math.sin(T * 1.3) : 0) + noise1(T * 1.4, 7) * 0.01);
    if (id === 'final') camera.rotateZ(0.05 * Math.sin(t * 0.4));
    camera.updateProjectionMatrix();
  }};
}
