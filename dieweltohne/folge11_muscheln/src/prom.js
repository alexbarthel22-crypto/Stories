// Stufe 2: Abiball, Gruppenfoto auf der Treppe vor der Schule. Die Hemdknöpfe sind aus Perlmutt –
// sie verschwinden, alle Hemden springen auf (darunter bunte Unterhemden), die Fliegen fallen, die Perlenketten sind weg.
// Genau dann blitzt die Kamera: Das Foto friert ein.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, skyDome, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {addMouth, mouthOpen, brows} from './people.js';
import {shellMats} from './shells.js';
import {POP, FLASH} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

function underTex(kind) {
  return canvasTex(256, 256, (g, w, h) => {
    const base = {duck: '#ffe14a', heart: '#ff7fb0', stripe: '#4aa3ff', dino: '#7ee26a', star: '#b48cff'}[kind]; g.fillStyle = base; g.fillRect(0, 0, w, h);
    g.fillStyle = 'rgba(255,255,255,0.9)';
    if (kind === 'stripe') { for (let y = 0; y < h; y += 32) { g.fillStyle = 'rgba(255,255,255,0.85)'; g.fillRect(0, y, w, 14); } }
    else { g.font = 'bold 70px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = '#222';
      const sym = {duck: '🦆', heart: '♥', dino: '🦖', star: '★'}[kind]; for (let i = 0; i < 6; i++) g.fillText(sym, 50 + (i % 3) * 78, 70 + Math.floor(i / 3) * 110); }
  });
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.4;
  scene.add(skyDome('#1c2a52', '#4a4f86', '#c98a72', 300));
  scene.fog = new THREE.Fog('#3a3a5a', 30, 120);
  const hemi = new THREE.HemisphereLight('#aab6ff', '#3a2a2a', 0.5); scene.add(hemi);
  const key = new THREE.SpotLight('#ffe2bd', 40, 20, 0.6, 0.6, 1.4); key.position.set(2.5, 4.5, 6); key.target.position.set(0, 1.2, 0); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); scene.add(key, key.target);
  const fill = new THREE.PointLight('#ffcf9a', 6, 12, 1.5); fill.position.set(-2.5, 2.5, 3); scene.add(fill);
  const flashL = new THREE.PointLight('#ffffff', 0, 14, 1.2); flashL.position.set(-0.62, 1.7, 3.4); scene.add(flashL);
  // Boden, Treppe, Schulfassade
  mesh(new THREE.PlaneGeometry(80, 80), mat('#6b6660', {roughness: 0.9}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const stepM = mat('#b8b2a6', {roughness: 0.85});
  for (let i = 0; i < 3; i++) mesh(new THREE.BoxGeometry(6, 0.18 * (i + 1), 0.5), stepM, 0, 0.09 * (i + 1), -0.25 - i * 0.5, scene);
  mesh(new THREE.BoxGeometry(6, 0.54, 3), stepM, 0, 0.27, -3.0, scene);
  const facT = canvasTex(512, 256, (g, w, h) => { g.fillStyle = '#d8cbb4'; g.fillRect(0, 0, w, h); const r = rng(3);
    for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(0,0,0,${r() * 0.05})`; g.fillRect(r() * w, r() * h, 4, 4); }
    for (const x of [30, 150, 290, 410]) { const gr = g.createLinearGradient(0, 40, 0, 150); gr.addColorStop(0, '#ffd88a'); gr.addColorStop(1, '#e49a4a'); g.fillStyle = gr; g.fillRect(x, 40, 72, 110); g.fillStyle = 'rgba(80,50,30,0.6)'; g.fillRect(x + 34, 40, 4, 110); g.fillRect(x, 90, 72, 4); } });
  mesh(new THREE.BoxGeometry(12, 6, 0.4), new THREE.MeshStandardMaterial({map: facT, roughness: 0.9, emissive: '#ffffff', emissiveMap: facT, emissiveIntensity: 0.18}), 0, 3.0, -2.2, scene);
  // Tür (offen, warmes Licht)
  mesh(new THREE.PlaneGeometry(1.6, 2.3), new THREE.MeshBasicMaterial({color: '#ffcf8a'}), 0, 1.69, -1.99, scene);
  // Banner
  const banT = canvasTex(1024, 200, (g, w, h) => { g.fillStyle = '#16213f'; g.fillRect(0, 0, w, h); g.strokeStyle = '#e8c76a'; g.lineWidth = 8; g.strokeRect(10, 10, w - 20, h - 20);
    g.fillStyle = '#f3d98a'; g.font = 'italic 600 110px Garamond, serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('Abiball 2026', w / 2, h / 2 + 6); });
  mesh(new THREE.PlaneGeometry(2.6, 0.5), new THREE.MeshStandardMaterial({map: banT, roughness: 0.7, emissive: '#ffffff', emissiveMap: banT, emissiveIntensity: 0.3}), 0, 3.25, -1.97, scene);
  // Ballonbogen
  { const r = rng(9); const cols = ['#f3d98a', '#ffffff', '#e8c76a', '#f6f1e6'].map(c => new THREE.MeshPhysicalMaterial({color: c, roughness: 0.2, clearcoat: 1}));
    const bg = new THREE.SphereGeometry(0.16, 16, 12);
    for (let i = 0; i < 70; i++) { const a = Math.PI * i / 69, R = 2.05 + r() * 0.12; const b = mesh(bg, cols[i % 4], Math.cos(a) * R * 1.15, 0.5 + Math.sin(a) * R * 1.35, -1.6 + (r() - 0.5) * 0.3, scene); b.scale.set(1, 1.15, 1); b.scale.multiplyScalar(0.8 + r() * 0.45); } }
  // Lichterketten
  const bulbM = new THREE.MeshBasicMaterial({color: '#ffe6a8'});
  for (let k = 0; k < 2; k++) for (let i = 0; i < 26; i++) { const x = -4 + i * 0.32; mesh(new THREE.SphereGeometry(0.025, 6, 4), bulbM, x, 4.6 - k * 0.5 - 0.35 * Math.sin(i / 25 * Math.PI), -1.9, scene); }
  // Schüler: 5 Jungs in weißen Hemden, 4 Mädchen im Kleid
  const M = shellMats();
  const kinds = ['duck', 'heart', 'stripe', 'dino', 'star'];
  const guys = [], girls = [];
  const SKINS = ['#f1c7a5', '#d9a47e', '#a8714f', '#e2b28c', '#7a4d33', '#f5d3b8', '#d9a47e', '#f1c7a5', '#a8714f'];
  const spots = [[-0.62, 0, 0.35], [0, 0, 0.35], [0.62, 0, 0.35], [-0.31, 0.36, -0.75], [0.31, 0.36, -0.75], // Jungs
    [-0.95, 0.36, -0.75], [0.95, 0.36, -0.75], [-0.5, 0.54, -1.25], [0.5, 0.54, -1.25]]; // Mädchen
  for (let i = 0; i < 5; i++) {
    const p = makePerson(1201 + i, {skin: SKINS[i], top: '#f7f7f4', pants: '#15161c', shoe: '#111', sole: '#111', height: 1.0 + (i % 3) * 0.03});
    const u = p.userData; addMouth(p);
    const cap = u.torso.children[0]; cap.material = new THREE.MeshStandardMaterial({map: underTex(kinds[i]), roughness: 0.8});
    // Hemdhälften (Scharnier an der Seite), Knöpfe aus Perlmutt, Fliege
    u.flaps = [-1, 1].map(s => { const piv = new THREE.Group(); piv.position.set(s * 0.19, 0.3, 0.09); u.torso.add(piv);
      const f = mesh(new RoundedBoxGeometry(0.2, 0.56, 0.03, 2, 0.012), mat('#f7f7f4', {roughness: 0.7}), -s * 0.1, 0, 0.035, piv);
      if (s > 0) for (let k = 0; k < 5; k++) { const b = mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.006, 12), M.nacre, -0.19, 0.2 - k * 0.1, 0.053, piv); b.rotation.x = Math.PI / 2; (u.buttons = u.buttons || []).push(b); }
      return piv; });
    const bow = new THREE.Group(); bow.position.set(0, 0.59, 0.12); u.torso.add(bow);
    for (const s of [-1, 1]) mesh(new THREE.ConeGeometry(0.03, 0.06, 8), mat('#111'), s * 0.03, 0, 0, bow).rotation.z = s * Math.PI / 2;
    mesh(new THREE.SphereGeometry(0.013, 8, 6), mat('#111'), 0, 0, 0, bow); u.bow = bow;
    const [x, y, z] = spots[i]; p.position.set(x, y, z); scene.add(p); guys.push(p);
  }
  const DRESS = ['#b3203a', '#1f6fb3', '#2f8f6b', '#7b4fa0'];
  for (let i = 0; i < 4; i++) {
    const p = makePerson(1221 + i, {skin: SKINS[5 + i], top: DRESS[i], pants: DRESS[i], longHair: true, height: 0.95 + (i % 2) * 0.03});
    const u = p.userData; addMouth(p);
    const skirt = mesh(new THREE.ConeGeometry(0.33, 0.95, 20, 1, true), mat(DRESS[i], {roughness: 0.55, side: THREE.DoubleSide}), 0, -0.42, 0, u.hips); skirt.castShadow = true;
    // Perlenkette
    u.pearls = []; for (let k = 0; k < 15; k++) { const a = Math.PI * (0.15 + 0.7 * k / 14); const b = mesh(new THREE.SphereGeometry(0.011, 10, 8), M.pearl, Math.cos(a) * 0.1, 0.62 - Math.sin(a) * 0.08, 0.075 + Math.sin(a) * 0.04, u.torso); u.pearls.push(b); }
    const [x, y, z] = spots[5 + i]; p.position.set(x, y, z); scene.add(p); girls.push(p);
  }
  // Fotograf im Vordergrund (von hinten), Kamera auf Stativ
  const photog = makePerson(1250, {top: '#2a2a30', pants: '#3a3a3a', hair: '#b8b8b8', height: 1.02}); scene.add(photog);
  const cam3 = new THREE.Group(); scene.add(cam3); cam3.position.set(-0.62, 0, 3.45);
  for (let k = 0; k < 3; k++) { const l = mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.55, 6), mat('#222'), 0, 0.75, 0, cam3); l.rotation.set(0.25 * Math.cos(k * 2.1), 0, 0.25 * Math.sin(k * 2.1)); }
  mesh(new RoundedBoxGeometry(0.16, 0.11, 0.09, 2, 0.02), mat('#1a1a1a', {roughness: 0.4}), 0, 1.58, 0, cam3);
  mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.08, 16), mat('#111', {roughness: 0.2}), 0, 1.58, -0.08, cam3).rotation.x = Math.PI / 2;
  const flashBox = mesh(new THREE.BoxGeometry(0.07, 0.05, 0.05), new THREE.MeshStandardMaterial({color: '#222', emissive: '#ffffff', emissiveIntensity: 0}), 0, 1.69, -0.01, cam3);

  const camera = new THREE.PerspectiveCamera(42, 1080 / 1920, 0.05, 400); scene.add(camera);
  return {scene, camera, update(shot, T) {
    // Eingefroren: Pose bleibt beim Blitz stehen (bis 23.4)
    const Tp = T > FLASH + 0.05 && T < 23.4 ? FLASH + 0.05 : T;
    const pop = smooth(POP, POP + 0.12, Tp), over = Math.sin(clamp((Tp - POP) / 0.5) * Math.PI) * Math.exp(-(Tp - POP) * 3) * (Tp > POP);
    guys.forEach((p, i) => { const u = p.userData; const [x, y, z] = spots[i];
      posePerson(p, {}); p.position.set(x, y, z); p.rotation.y = -x * 0.15; brows(p, 0, 0);
      const ang = 1.25 + 0.25 * Math.sin(i * 1.7);
      u.flaps.forEach((f, k) => { const s = k ? 1 : -1; f.rotation.y = s * (ang * pop + 0.35 * over); });
      u.buttons.forEach(b => { b.visible = Tp < POP; });
      // Fliege fällt
      const fall = clamp((Tp - POP - 0.05 * i) / 0.45); u.bow.position.set(0, 0.59 - (fall > 0 ? 4.9 * Math.pow(fall * 0.45, 2) * 2.5 : 0), 0.12 + fall * 0.05); u.bow.rotation.z = fall * 4 * (i % 2 ? 1 : -1); u.bow.visible = u.bow.position.y > -0.5;
      // Reaktion: runter schauen, Hände auf die Brust, peinlich
      const look = smooth(POP + 0.25, POP + 0.6, Tp), cover = smooth(POP + 0.7 + i * 0.12, POP + 1.3 + i * 0.12, Tp);
      u.head.rotation.x = 0.45 * look * (1 - 0.6 * cover); brows(p, look, 0); mouthOpen(p, 0.15 + 0.6 * look);
      u.armL.rotation.x = lerp(0, -0.55, cover); u.armR.rotation.x = lerp(0, -0.55, cover); u.armL.rotation.z = lerp(-0.08, 0.35, cover); u.armR.rotation.z = lerp(0.08, -0.35, cover);
      u.armL.userData.fore.rotation.x = lerp(-0.25, -1.75, cover); u.armR.userData.fore.rotation.x = lerp(-0.25, -1.75, cover);
      if (i === 1) { u.armL.rotation.z = lerp(-0.08, -2.3, look); u.armR.rotation.z = lerp(0.08, 2.3, look); u.armL.rotation.x = u.armR.rotation.x = 0; } // einer jubelt einfach
      if (Tp < POP) mouthOpen(p, 0.35); // "Cheese"
    });
    girls.forEach((p, i) => { const u = p.userData; const [x, y, z] = spots[5 + i];
      posePerson(p, {}); p.position.set(x, y, z); p.rotation.y = -x * 0.15; u.pearls.forEach(b => { b.visible = Tp < POP; });
      const laugh = smooth(POP + 0.35 + i * 0.1, POP + 0.8 + i * 0.1, Tp);
      u.armR.rotation.x = lerp(0, -2.4, laugh); u.armR.userData.fore.rotation.x = lerp(-0.25, -1.6, laugh); u.armR.rotation.z = lerp(0.08, -0.3, laugh);
      u.torso.rotation.x = laugh * (0.18 + 0.05 * Math.sin(Tp * 17 + i)); mouthOpen(p, Tp < POP ? 0.35 : 0.8 * laugh); brows(p, laugh, 0);
      if (i === 2) { u.armL.rotation.x = lerp(0, -0.6, laugh); u.armL.userData.fore.rotation.x = -1.8 * laugh; } });
    // Fotograf
    photog.position.set(-0.85, 0, 3.75); photog.rotation.y = Math.PI; posePerson(photog, {});
    const pu = photog.userData; pu.armR.rotation.x = -1.6; pu.armR.userData.fore.rotation.x = -0.4; pu.armL.rotation.x = -1.3; pu.armL.userData.fore.rotation.x = -0.9;
    if (Tp > POP + 0.3) { pu.head.rotation.y = 0.3 * Math.sin(clamp((Tp - POP - 0.3) / 1.2) * Math.PI); }
    const fl = T - FLASH; flashL.intensity = fl > 0 && fl < 0.25 ? 120 * (1 - fl / 0.25) : 0; flashBox.material.emissiveIntensity = flashL.intensity > 0 ? 6 : 0;
    // Kamera: hinter dem Fotografen, leichter Schwenk; im Foto langsam näher
    const k = smooth(17, FLASH, T), z = smooth(FLASH, 23.4, T);
    camera.position.set(lerp(0.2, 0.05, k) + noise1(T, 3) * 0.01, lerp(1.5, 1.45, k), lerp(5.4, 5.0, k) - 0.9 * z);
    camera.lookAt(0, lerp(1.2, 1.22, k) + 0.08 * z, -0.4);
    camera.fov = 40; camera.updateProjectionMatrix();
  }};
}
