// Außeneinsatz an einer Raumstation. Das Visier ist mit einer hauchdünnen Goldschicht bedampft – sie filtert das grelle Sonnenlicht.
// Ohne Gold: klares Glas, die Sonne blendet ungefiltert. Der Astronaut lässt los und treibt an seiner Sicherungsleine weg.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, envMap} from './lib.js';
import {GOLD, glitter, updateGlitter} from './gold.js';
import {VISOR_GONE, GLARE} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#000105');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.25;
  const SUN = V3(0.45, 0.55, 1).normalize();
  const sunL = new THREE.DirectionalLight('#fffaf0', 4.5); sunL.position.copy(SUN).multiplyScalar(30); sunL.castShadow = true; sunL.shadow.mapSize.set(2048, 2048);
  Object.assign(sunL.shadow.camera, {left: -8, right: 8, top: 8, bottom: -8, near: 1, far: 80}); scene.add(sunL);
  scene.add(new THREE.HemisphereLight('#7fa8ff', '#0a1020', 0.35)); // Erdlicht von unten
  // Sterne
  { const n = 3000, r = rng(3), P = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const v = V3(r() - 0.5, r() - 0.5, r() - 0.5).normalize().multiplyScalar(900); P.set([v.x, v.y, v.z], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); scene.add(new THREE.Points(g, new THREE.PointsMaterial({color: '#ffffff', size: 1.2, sizeAttenuation: false}))); }
  // Sonne
  const sunTex = canvasTex(256, 256, g => { const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.12, 'rgba(255,255,250,1)'); gr.addColorStop(0.3, 'rgba(255,240,200,0.35)'); gr.addColorStop(1, 'rgba(255,220,160,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); });
  const sunS = new THREE.Sprite(new THREE.SpriteMaterial({map: sunTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false})); sunS.scale.setScalar(160); sunS.position.copy(SUN).multiplyScalar(800); scene.add(sunS);
  // Erde
  const img = new Image(); img.src = '../tex/earth_day.jpg'; await img.decode();
  const et = new THREE.Texture(img); et.colorSpace = THREE.SRGBColorSpace; et.anisotropy = 8; et.needsUpdate = true;
  const earth = mesh(new THREE.SphereGeometry(2000, 128, 96), new THREE.MeshStandardMaterial({map: et, roughness: 0.9}), 0, -2130, -300, scene); earth.rotation.set(0.4, 2.2, 0.2); earth.castShadow = false;
  const atm = mesh(new THREE.SphereGeometry(2030, 96, 64), new THREE.MeshBasicMaterial({color: '#6fa8ff', transparent: true, opacity: 0.18, side: THREE.BackSide, depthWrite: false}), 0, -2130, -300, scene); atm.castShadow = false;

  // Station: Gitterträger, Module, Solarflügel
  const st = new THREE.Group(); scene.add(st);
  const trussM = mat('#c9cdd2', {metalness: 0.6, roughness: 0.4}), whiteM = mat('#e9ebee', {roughness: 0.6});
  for (let x = -16; x <= 16; x += 1.2) {
    for (const [y, z] of [[-0.6, -0.6], [0.6, -0.6], [-0.6, 0.6], [0.6, 0.6]]) mesh(new THREE.BoxGeometry(1.2, 0.06, 0.06), trussM, x, y - 0.9, z - 1.2, st);
    for (const [y, z] of [[-0.6, -0.6], [0.6, -0.6], [-0.6, 0.6], [0.6, 0.6]]) mesh(new THREE.BoxGeometry(0.05, 0.05, 0.05), trussM, x, y - 0.9, z - 1.2, st);
    const d = mesh(new THREE.BoxGeometry(0.04, 1.7, 0.04), trussM, x + 0.3, -0.9, -0.6, st); d.rotation.z = 0.78;
    const d2 = mesh(new THREE.BoxGeometry(0.04, 1.7, 0.04), trussM, x + 0.3, -0.9, -1.8, st); d2.rotation.z = -0.78;
  }
  const mod = mesh(new THREE.CylinderGeometry(2.1, 2.1, 9, 32), whiteM, 3, 1.6, -6, st); mod.rotation.z = Math.PI / 2;
  mesh(new THREE.CylinderGeometry(1.6, 1.6, 5, 32), whiteM, -6, 1.2, -7, st).rotation.x = Math.PI / 2;
  const solT = canvasTex(256, 512, g => { g.fillStyle = '#0f1d3a'; g.fillRect(0, 0, 256, 512); g.strokeStyle = '#3c5a8c'; g.lineWidth = 2; for (let x = 0; x < 256; x += 16) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, 512); g.stroke(); } for (let y = 0; y < 512; y += 24) { g.beginPath(); g.moveTo(0, y); g.lineTo(256, y); g.stroke(); } g.fillStyle = '#c7a24a'; g.fillRect(124, 0, 8, 512); });
  const solM = new THREE.MeshStandardMaterial({map: solT, metalness: 0.5, roughness: 0.3, side: THREE.DoubleSide});
  for (const sx of [-1, 1]) for (const k of [0, 1]) { const p = mesh(new THREE.PlaneGeometry(4.5, 26), solM, sx * (20 + k * 5.2), -0.9, -1.2, st); p.rotation.x = -Math.PI / 2 + 0.25; }
  // Handlauf (gelb) am Modul vorn
  const railM = mat('#e3b62a', {roughness: 0.5});
  const rail = mesh(new THREE.BoxGeometry(2.6, 0.04, 0.04), railM, 0, 0.05, -0.32, scene);
  for (const x of [-1.2, 1.2]) mesh(new THREE.BoxGeometry(0.04, 0.12, 0.04), railM, x, -0.02, -0.32, scene);
  mesh(new THREE.BoxGeometry(5, 0.25, 0.6), whiteM, 0, -0.18, -0.55, scene); // Kante, an der der Handlauf sitzt

  // Astronaut
  const suitM = mat('#f3f3f0', {roughness: 0.75}), greyM = mat('#9aa0a8', {roughness: 0.6}), stripeM = mat('#c8202e');
  const astro = new THREE.Group(); scene.add(astro);
  const body = new THREE.Group(); astro.add(body);
  mesh(new THREE.CapsuleGeometry(0.27, 0.42, 4, 12), suitM, 0, 0, 0, body).scale.set(1.05, 1, 0.85);
  mesh(new RoundedBoxGeometry(0.56, 0.72, 0.26, 3, 0.05), suitM, 0, 0.05, -0.33, body); // Rucksack
  mesh(new THREE.BoxGeometry(0.3, 0.16, 0.06), greyM, 0, 0.05, 0.25, body); // Bedienteil
  mesh(new THREE.CylinderGeometry(0.29, 0.29, 0.06, 20), stripeM, 0, 0.36, 0, body);
  const head = new THREE.Group(); head.position.set(0, 0.55, 0.02); body.add(head);
  mesh(new THREE.SphereGeometry(0.21, 24, 18, Math.PI * 0.82, Math.PI * 1.36), suitM, 0, 0, -0.01, head);
  const face = mesh(new THREE.SphereGeometry(0.11, 16, 12), mat('#d9a47e'), 0, -0.01, 0.05, head);
  for (const s of [-1, 1]) mesh(new THREE.SphereGeometry(0.013, 8, 6), mat('#1a1a1a'), s * 0.04, 0.01, 0.155, head);
  const visorGeo = new THREE.SphereGeometry(0.215, 28, 20, Math.PI * 0.05, Math.PI * 0.9, Math.PI * 0.16, Math.PI * 0.6);
  const visorGold = mesh(visorGeo, GOLD, 0, 0, 0, head); visorGold.castShadow = false;
  const visorClear = mesh(visorGeo, new THREE.MeshPhysicalMaterial({color: '#9fb4c8', transparent: true, opacity: 0.18, roughness: 0.02, metalness: 0, clearcoat: 1}), 0, 0, 0, head); visorClear.castShadow = false;
  mesh(new THREE.TorusGeometry(0.2, 0.02, 8, 30), greyM, 0, 0, 0.03, head).scale.set(1, 1.1, 1);
  const limb = (parent, x, y, len, r) => { const g = new THREE.Group(); g.position.set(x, y, 0); parent.add(g);
    mesh(new THREE.CapsuleGeometry(r, len, 4, 10), suitM, 0, -len / 2 - r, 0, g); const low = new THREE.Group(); low.position.y = -len - r * 1.6; g.add(low);
    mesh(new THREE.CapsuleGeometry(r * 0.9, len, 4, 10), suitM, 0, -len / 2 - r, 0, low); mesh(new THREE.SphereGeometry(r * 1.05, 10, 8), greyM, 0, -len - r * 1.7, 0, low); g.userData.low = low; return g; };
  const armL = limb(body, -0.36, 0.28, 0.22, 0.085), armR = limb(body, 0.36, 0.28, 0.22, 0.085);
  const legL = limb(body, -0.14, -0.4, 0.3, 0.1), legR = limb(body, 0.14, -0.4, 0.3, 0.1);
  // Sicherungsleine
  const tether = new THREE.Line(new THREE.BufferGeometry().setFromPoints(new Array(24).fill(0).map(() => V3())), new THREE.LineBasicMaterial({color: '#e8e2d0'})); tether.frustumCulled = false; scene.add(tether);
  const gl = glitter(400, 0.02); scene.add(gl);

  // Helmrand für die Innenansicht
  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.01, 6000); scene.add(camera);
  const rimG = new THREE.Group(); camera.add(rimG);
  const rimM = new THREE.MeshBasicMaterial({color: '#1b1d22'});
  const rimRing = mesh(new THREE.TorusGeometry(0.15, 0.035, 10, 40), rimM, 0, 0, -0.12, rimG); rimRing.scale.set(0.62, 1.05, 1);
  mesh(new THREE.PlaneGeometry(0.4, 0.06), rimM, 0, -0.14, -0.13, rimG);

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, gone = T >= VISOR_GONE;
    visorGold.visible = !gone; visorClear.visible = gone;
    // Haltung: arbeitet am Handlauf, dann Hand vors Visier, lässt los, treibt weg
    const flinch = smooth(GLARE, GLARE + 0.4, T), drift = smooth(27.6, 31, T), tumble = smooth(27.8, 31, T);
    astro.position.set(0.1 + drift * 0.6, 0.55 + drift * 1.4 + noise1(T * 0.3, 2) * 0.02, 0.35 + drift * 2.2);
    astro.rotation.set(-0.35 + tumble * 0.9, 0.1 + tumble * 0.5, tumble * 0.35);
    armR.rotation.set(lerp(-0.35, -2.4, flinch), 0, lerp(0.25, -0.55, flinch)); armR.userData.low.rotation.x = lerp(-0.3, -1.5, flinch);
    armL.rotation.set(lerp(-0.4, -0.3, drift) + Math.sin(T * 2) * 0.03, 0, lerp(-0.2, -1.0, drift)); armL.userData.low.rotation.x = lerp(-0.6, -0.2, drift);
    legL.rotation.set(0.25 + drift * 0.3, 0, -0.1 - drift * 0.4); legR.rotation.set(-0.1 + drift * 0.5, 0, 0.12 + drift * 0.3); legL.userData.low.rotation.x = 0.3; legR.userData.low.rotation.x = 0.5;
    head.rotation.x = lerp(0.25, -0.1, flinch);
    astro.updateMatrixWorld(true);
    // Leine vom Handlauf zur Hüfte (durchhängend, wird straff)
    const a = V3(1.2, 0.05, -0.32), b = body.localToWorld(V3(0.15, -0.25, 0.05)); const P = tether.geometry.attributes.position;
    for (let i = 0; i < 24; i++) { const k = i / 23; const p = a.clone().lerp(b, k); const sag = (1 - drift) * 0.25 * Math.sin(k * Math.PI); p.y -= sag; P.setXYZ(i, p.x, p.y, p.z); } P.needsUpdate = true;
    updateGlitter(gl, [visorGold.getWorldPosition(new THREE.Vector3())], T - VISOR_GONE, 0.9, 0.12, 0.1);
    // Kamera
    rimG.visible = false; camera.fov = 46; astro.visible = true;
    if (T < GLARE) { // außen, nah am Helm, Sonne spiegelt sich im Goldvisier
      const k = smooth(24, 26, T);
      camera.position.set(lerp(-1.1, -0.7, k), lerp(1.15, 1.05, k), lerp(2.1, 1.6, k)); camera.lookAt(0.1, 1.0, 0.35);
    } else if (T < 28.4) { // Innenansicht: Blick in die Sonne
      rimG.visible = true; camera.fov = 70; astro.visible = false;
      const hp = head.getWorldPosition(new THREE.Vector3()); camera.position.copy(hp).add(V3(0, 0.02, 0.06));
      const look = SUN.clone().multiplyScalar(800).add(V3(noise1(T * 3, 1) * 40, -90 + noise1(T * 2, 4) * 30, 0)).lerp(V3(hp.x, hp.y - 500, hp.z + 300), smooth(27.0, 28.4, T) * 0.4);
      camera.lookAt(look);
    } else { // weit: er treibt an der Leine von der Station weg
      const k = smooth(28.4, 31, T);
      camera.position.set(lerp(3.0, 3.6, k), lerp(1.9, 2.5, k), lerp(4.2, 5.4, k)); camera.lookAt(lerp(0.4, 0.8, k), lerp(0.9, 1.6, k), lerp(0.8, 1.8, k));
    }
    tether.visible = astro.visible;
    camera.updateProjectionMatrix();
  }};
}
