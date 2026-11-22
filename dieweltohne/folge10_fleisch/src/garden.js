// Reihenhaus-Garten am Samstagnachmittag: Papa grillt. Stufe 1: Würstchen und Steaks verschwinden vom Rost.
// suburb: Luftbild der Siedlung – das Fleisch ist zurück, aus jedem Garten steigt Grillrauch, drei Löwen laufen die Straße entlang.
// back / lion / final: Papa grillt wieder, ein Löwe steht am Zaun, springt hinüber, alle flüchten ins Haus, der Löwe frisst die Würstchen.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, asphaltTex, tileTex, skyDome, easeIn, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {makePhone, makeHands} from './phone.js';
import {makeLion, poseLion} from './lion.js';
import {VANISH, RETURN, LION_JUMP, DOOR_SLAM} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

function grassTex(seed, base = '#5f8f3a') {
  const r = rng(seed);
  const t = canvasTex(512, 512, (g, w, h) => { g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 26000; i++) { const v = r(); g.fillStyle = v < 0.5 ? `rgba(40,80,25,${0.25 + r() * 0.3})` : `rgba(150,190,90,${0.15 + r() * 0.25})`; g.fillRect(r() * w, r() * h, 1.5, 3 + r() * 3); }
    for (let i = 0; i < 20; i++) { g.fillStyle = 'rgba(30,60,20,0.08)'; g.beginPath(); g.ellipse(r() * w, r() * h, 30 + r() * 80, 20 + r() * 50, r() * 3, 0, 7); g.fill(); } });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
function woodTex(seed, base = '#a77b4f') {
  const r = rng(seed);
  return canvasTex(128, 512, (g, w, h) => { g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 60; i++) { g.strokeStyle = `rgba(60,35,15,${0.08 + r() * 0.15})`; g.lineWidth = 1 + r() * 2; g.beginPath(); const x = r() * w; g.moveTo(x, 0); g.bezierCurveTo(x + (r() - 0.5) * 20, h / 3, x + (r() - 0.5) * 20, 2 * h / 3, x + (r() - 0.5) * 10, h); g.stroke(); } });
}
function tree(scene, x, z, s, r, leafM, trunkM) {
  mesh(new THREE.CylinderGeometry(0.12 * s, 0.18 * s, 2.4 * s, 8), trunkM, x, 1.2 * s, z, scene);
  const n = 3 + Math.floor(r() * 3);
  for (let i = 0; i < n; i++) { const b = mesh(new THREE.IcosahedronGeometry((1.1 + r() * 0.6) * s, 1), leafM, x + (r() - 0.5) * 1.4 * s, (2.8 + r() * 1.4) * s, z + (r() - 0.5) * 1.4 * s, scene); b.scale.y = 0.85; }
}
function makeDog() { // kleiner Hund: Löwen-Skelett ohne Mähne, kurz und gefleckt
  const d = makeLion(3, {male: false, scale: 0.42, fur: '#b7834a', light: '#f0e6d6'});
  const u = d.userData; for (const s of [-1, 1]) { const e = mesh(new THREE.SphereGeometry(0.09, 8, 6), mat('#6b4423'), s * 0.17, 0.08, -0.02, u.head); e.scale.set(0.5, 1.4, 0.8); e.rotation.z = s * 0.4; }
  return d;
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.55;
  scene.fog = new THREE.Fog('#d8dfe6', 120, 900);
  scene.add(skyDome('#5f8fcf', '#a9c6e6', '#e8eef2', 1500));
  const hemi = new THREE.HemisphereLight('#e6f0ff', '#4a5a30', 0.85); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff0d8', 2.7); sun.position.set(30, 40, 22); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -22, right: 22, top: 22, bottom: -22, near: 1, far: 140}); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03; scene.add(sun, sun.target);

  // Boden: Straße/Gehweg überall, Rasen in den Gärten
  const asT = asphaltTex(); asT.repeat.set(60, 60);
  mesh(new THREE.PlaneGeometry(1600, 1600), new THREE.MeshStandardMaterial({map: asT, roughness: 0.95}), 0, -0.02, 0, scene).rotation.x = -Math.PI / 2;
  const gT = grassTex(5); gT.repeat.set(5, 5); const lawnM = new THREE.MeshStandardMaterial({map: gT, roughness: 1});
  const gTf = grassTex(6, '#5a8636'); gTf.repeat.set(3, 3); const lawnFarM = new THREE.MeshStandardMaterial({map: gTf, roughness: 1});
  const terT = tileTex('#b9b2a6', '#aaa397'); terT.repeat.set(4, 2); const terM = new THREE.MeshStandardMaterial({map: terT, roughness: 0.9});
  const wallMs = ['#e9e2d6', '#d9c6a8', '#c9d2d8', '#e3d3c3', '#bfae9a'].map(c => mat(c, {roughness: 0.9})), roofM = mat('#7a3b2c', {roughness: 0.85}), roof2 = mat('#4a4a50', {roughness: 0.85});
  const winM = new THREE.MeshStandardMaterial({color: '#28323c', roughness: 0.15, metalness: 0.3});
  const fenceT = woodTex(3); const fenceM = new THREE.MeshStandardMaterial({map: fenceT, roughness: 0.85});
  const leafM = mat('#3f6e2c', {roughness: 0.95}), leaf2 = mat('#4f7f32', {roughness: 0.95}), trunkM = mat('#5a4030', {roughness: 0.95});
  const hedgeM = mat('#35622a', {roughness: 1});

  // Siedlung: Reihen von Grundstücken 20 x 18 m, Straßen dazwischen. Unser Grundstück: x -8..8, z -11..8, Haus hinten
  const LOT_W = 20, LOT_D = 30; const lots = []; // Gartenmitten (für Grillrauch)
  const houseGeo = new THREE.BoxGeometry(12, 6, 8), prism = new THREE.CylinderGeometry(4.85, 4.85, 12.6, 3); prism.rotateZ(Math.PI / 2); prism.rotateX(-Math.PI / 2);
  { const r = rng(17);
    for (let ix = -7; ix <= 7; ix++) for (let iz = -6; iz <= 6; iz++) {
      const cx = ix * LOT_W, cz = iz * (LOT_D + 8) + (ix % 2 ? 0 : 0);
      const own = ix === 0 && iz === 0;
      // Rasen
      const lawn = mesh(new THREE.PlaneGeometry(LOT_W - 2, LOT_D - 2), own ? lawnM : lawnFarM, cx, 0.005, cz, scene); lawn.rotation.x = -Math.PI / 2; lawn.castShadow = false;
      lots.push(V3(cx + (r() - 0.5) * 6, 0.9, cz + 4 + r() * 4));
      if (own) continue;
      // Haus (hinten im Grundstück), Dach
      const h = mesh(houseGeo, wallMs[Math.floor(r() * 5)], cx, 3, cz - 10, scene);
      const rm = r() < 0.6 ? roofM : roof2; const rf = mesh(prism, rm, cx, 6 + 0.5 * 4.85 * 0.4, cz - 10, scene); rf.scale.set(1, 0.4, 1);
      mesh(new THREE.BoxGeometry(2.0, 1.5, 0.05), winM, cx - 3, 4.4, cz - 5.97, scene); mesh(new THREE.BoxGeometry(2.0, 1.5, 0.05), winM, cx + 3, 4.4, cz - 5.97, scene);
      mesh(new THREE.BoxGeometry(3.0, 2.2, 0.05), winM, cx + 1, 1.2, cz - 5.97, scene);
      // Hecke als Grundstücksgrenze, ein Baum
      mesh(new THREE.BoxGeometry(0.8, 1.6, LOT_D - 4), hedgeM, cx - LOT_W / 2 + 0.6, 0.8, cz, scene);
      if (r() < 0.55) tree(scene, cx + (r() - 0.5) * 12, cz + 6 + r() * 5, 0.8 + r() * 0.5, r, r() < 0.5 ? leafM : leaf2, trunkM);
    } }

  // Unser Haus: Rückseite mit Terrassentür (Glas), Terrasse
  const ownWall = mat('#ece4d4', {roughness: 0.9});
  const hb = new THREE.Group(); scene.add(hb);
  mesh(new THREE.BoxGeometry(5.2, 6, 0.3), ownWall, -3.4, 3, -7, hb); mesh(new THREE.BoxGeometry(3.0, 6, 0.3), ownWall, 4.5, 3, -7, hb);
  mesh(new THREE.BoxGeometry(3.6, 3.6, 0.3), ownWall, 1.2, 4.2, -7, hb);
  mesh(new THREE.BoxGeometry(12, 3, 7.6), ownWall, 0, 4.5, -10.95, hb);   // Obergeschoss
  const inWall = mat('#efe6d8', {roughness: 0.9});
  mesh(new THREE.BoxGeometry(0.3, 3, 7.6), inWall, -6, 1.5, -10.95, hb); mesh(new THREE.BoxGeometry(0.3, 3, 7.6), inWall, 6, 1.5, -10.95, hb); mesh(new THREE.BoxGeometry(12, 3, 0.3), inWall, 0, 1.5, -14.6, hb); // Erdgeschoss innen offen
  mesh(new THREE.CylinderGeometry(4.85, 4.85, 12.6, 3).rotateZ(Math.PI / 2).rotateX(-Math.PI / 2), roofM, 0, 6 + 0.97, -10.95, hb).scale.set(1, 0.4, 0.92);
  mesh(new THREE.BoxGeometry(1.8, 1.3, 0.05), winM, -3.2, 4.4, -6.83, hb); mesh(new THREE.BoxGeometry(1.8, 1.3, 0.05), winM, 4.4, 4.4, -6.83, hb);
  // Terrassentür: Rahmen + Glas (halbtransparent), Innenraum dahinter
  const frameM = mat('#f4f4f2', {roughness: 0.5});
  for (const x of [-0.6, 3.0]) mesh(new THREE.BoxGeometry(0.08, 2.4, 0.12), frameM, x, 1.2, -6.9, hb);
  mesh(new THREE.BoxGeometry(3.7, 0.1, 0.12), frameM, 1.2, 2.4, -6.9, hb);
  const glassM = new THREE.MeshPhysicalMaterial({color: '#cfe3ea', transparent: true, opacity: 0.18, roughness: 0.05, metalness: 0, depthWrite: false});
  const glass = mesh(new THREE.PlaneGeometry(3.6, 2.35), glassM, 1.2, 1.2, -6.88, hb); glass.castShadow = false;
  mesh(new THREE.BoxGeometry(11.4, 0.05, 6), mat('#b08a64', {roughness: 0.7}), 0, 0.02, -10.2, hb); // Holzboden innen
  mesh(new THREE.BoxGeometry(2.4, 0.8, 0.9), mat('#59606b'), -2.8, 0.42, -12.8, hb); // Sofa
  const indoorL = new THREE.PointLight('#ffe7c4', 4, 10, 1.6); indoorL.position.set(1, 2.6, -10); scene.add(indoorL);
  const ter = mesh(new THREE.BoxGeometry(12, 0.1, 3.4), terM, 0, 0.05, -5.15, scene); ter.castShadow = false;
  // Zaun um den Garten (Latten), Hecke dahinter
  const picket = new THREE.BoxGeometry(0.09, 1.25, 0.025);
  const fence = new THREE.Group(); scene.add(fence);
  for (let x = -8; x <= 8.01; x += 0.16) mesh(picket, fenceM, x, 0.62, 8, fence);
  for (const s of [-1, 1]) for (let z = -3.4; z <= 8.01; z += 0.16) { const p = mesh(picket, fenceM, s * 8, 0.62, z, fence); p.rotation.y = Math.PI / 2; }
  for (const y of [0.3, 1.0]) { mesh(new THREE.BoxGeometry(16, 0.07, 0.04), fenceM, 0, y, 7.97, fence); for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(0.04, 0.07, 11.4), fenceM, s * 7.97, y, 2.3, fence); }
  // Straße hinter dem Zaun (z 9..15), gegenüber Hecken
  tree(scene, -5.5, 5.5, 1.1, rng(4), leafM, trunkM); tree(scene, 6.2, -1.5, 0.9, rng(9), leaf2, trunkM);
  mesh(new THREE.BoxGeometry(16, 1.8, 0.9), hedgeM, 0, 0.9, 16.5, scene);

  // Gartentisch mit Geschirr, Salat, Ketchup
  const tableM = mat('#f2f0ea', {roughness: 0.6});
  mesh(new THREE.BoxGeometry(2.2, 0.06, 1.0), tableM, -3.0, 0.76, -4.6, scene);
  for (const [x, z] of [[-4, -5], [-2, -5], [-4, -4.2], [-2, -4.2]]) mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.76, 6), tableM, x, 0.38, z, scene);
  for (let i = 0; i < 4; i++) mesh(new THREE.CylinderGeometry(0.13, 0.11, 0.02, 20), mat('#ffffff', {roughness: 0.3}), -3.8 + i * 0.55, 0.8, -4.35 - (i % 2) * 0.5, scene);
  mesh(new THREE.SphereGeometry(0.2, 14, 8, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), mat('#e8e8e8'), -3, 0.99, -4.6, scene).rotation.x = Math.PI;
  mesh(new THREE.SphereGeometry(0.17, 10, 8), mat('#5ea03a'), -3, 0.92, -4.6, scene).scale.y = 0.5;
  mesh(new THREE.CylinderGeometry(0.035, 0.04, 0.2, 10), mat('#c81e1e', {roughness: 0.4}), -2.4, 0.89, -4.5, scene);
  // Gasgrill
  const grill = new THREE.Group(); grill.position.set(1.8, 0, -2.6); scene.add(grill);
  const steelM = mat('#2a2d31', {metalness: 0.7, roughness: 0.35}), steel2 = mat('#8d939a', {metalness: 0.85, roughness: 0.3});
  mesh(new THREE.BoxGeometry(1.2, 0.8, 0.6), steelM, 0, 0.45, 0, grill);
  mesh(new THREE.BoxGeometry(1.22, 0.12, 0.62), steel2, 0, 0.9, 0, grill);
  const lid = new THREE.Group(); lid.position.set(0, 0.96, -0.31); grill.add(lid);
  mesh(new THREE.CylinderGeometry(0.31, 0.31, 1.2, 16, 1, false, 0, Math.PI), steelM, 0, 0, 0.0, lid).rotation.set(0, 0, Math.PI / 2);
  lid.rotation.x = -1.35; // offen
  mesh(new THREE.BoxGeometry(0.5, 0.05, 0.6), steel2, 0.86, 0.9, 0, grill); // Ablage
  const glowM = new THREE.MeshStandardMaterial({color: '#2a1408', emissive: '#ff5a1a', emissiveIntensity: 0.8});
  mesh(new THREE.PlaneGeometry(1.1, 0.52), glowM, 0, 0.955, 0, grill).rotation.x = -Math.PI / 2;
  for (let i = 0; i < 12; i++) mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.54, 4), steel2, -0.5 + i * 0.09, 0.97, 0, grill).rotation.x = Math.PI / 2;
  // Fleisch auf dem Rost: 8 Würstchen, 3 Steaks; Platte mit Würstchen auf der Ablage
  const sausM = new THREE.MeshStandardMaterial({color: '#a2502a', roughness: 0.45}), steakM = new THREE.MeshStandardMaterial({color: '#6e3320', roughness: 0.7});
  const meat = new THREE.Group(); grill.add(meat);
  const sausGeo = new THREE.CapsuleGeometry(0.028, 0.16, 4, 10);
  for (let i = 0; i < 8; i++) { const s = mesh(sausGeo, sausM, -0.45 + (i % 4) * 0.1, 1.0, -0.15 + Math.floor(i / 4) * 0.12, meat); s.rotation.x = Math.PI / 2; s.rotation.y = (i % 3 - 1) * 0.08; }
  for (let i = 0; i < 3; i++) { const s = mesh(new THREE.CylinderGeometry(0.11, 0.12, 0.03, 10), steakM, 0.12 + i * 0.15, 0.995, 0.05 - (i % 2) * 0.12, meat); s.scale.set(1.15, 1, 0.8); }
  const platter = new THREE.Group(); platter.position.set(0.86, 0.94, 0); grill.add(platter);
  mesh(new THREE.CylinderGeometry(0.2, 0.18, 0.02, 20), mat('#f6f6f6', {roughness: 0.3}), 0, 0, 0, platter);
  const platMeat = new THREE.Group(); platter.add(platMeat);
  for (let i = 0; i < 6; i++) { const s = mesh(sausGeo, sausM, -0.1 + (i % 3) * 0.08, 0.035 + Math.floor(i / 3) * 0.04, -0.03 + Math.floor(i / 3) * 0.04, platMeat); s.rotation.x = Math.PI / 2; }
  const grillSmoke = particles(260, 'smoke'); scene.add(grillSmoke);
  const puff = particles(160, 'smoke'); scene.add(puff);
  const farSmoke = particles(3000, 'smoke'); scene.add(farSmoke);

  // Familie
  const dad = makePerson(71, {skin: '#e2b28c', top: '#3e6f9e', pants: '#4a4f57', hair: '#5a3b22', shortSleeve: true, height: 1.04});
  const apron = mesh(new THREE.BoxGeometry(0.36, 0.62, 0.02), mat('#ece7dc', {roughness: 0.9}), 0, 0.24, 0.15, dad.userData.torso);
  const tongs = new THREE.Group(); dad.userData.armR.userData.fore.add(tongs); tongs.position.set(0, -0.31, 0.02);
  for (const s of [-1, 1]) { const a = mesh(new THREE.BoxGeometry(0.012, 0.35, 0.02), steel2, s * 0.012, -0.17, 0.0, tongs); a.rotation.z = s * 0.04; }
  const mom = makePerson(83, {skin: '#f1c7a5', top: '#d9a6b8', pants: '#2d3a55', hair: '#8a5a2b', longHair: true});
  const kid1 = makePerson(91, {skin: '#e2b28c', top: '#f0c43a', pants: '#2b4d3a', hair: '#2a1d15', height: 0.82, shortSleeve: true});
  const kid2 = makePerson(97, {skin: '#e2b28c', top: '#e8e2d4', pants: '#3a3a3a', hair: '#c9a35b', height: 0.9, longHair: true});
  [dad, mom, kid1, kid2].forEach(p => scene.add(p));
  const dog = makeDog(); scene.add(dog);
  // Löwen: einer kommt in den Garten, drei laufen im Luftbild durch die Siedlung
  const lionG = makeLion(1, {male: true}); scene.add(lionG);
  const runners = [makeLion(2, {male: true}), makeLion(5, {male: false}), makeLion(6, {male: false})]; runners.forEach(l => scene.add(l));

  // Kamera und Handy (Intro)
  const camera = new THREE.PerspectiveCamera(45, 1080 / 1920, 0.02, 3000); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#2f6d5a'); const hands = makeHands('#d9a47e', '#5a6b7a');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig);
  rig.position.set(0.02, -0.07, -0.29); rig.rotation.set(-0.08, 0.04, -0.03);
  const RT = new THREE.WebGLRenderTarget(432, 936); RT.texture.colorSpace = THREE.SRGBColorSpace;
  const phoneCam = new THREE.PerspectiveCamera(58, 432 / 936, 0.05, 2000);
  const uiC = document.createElement('canvas'); uiC.width = 432; uiC.height = 936; const uiT = new THREE.CanvasTexture(uiC); uiT.colorSpace = THREE.SRGBColorSpace;
  const pw = phone.userData.pw, phh = phone.userData.ph;
  mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: RT.texture, toneMapped: false}), 0, 0, 0.0052, phone);
  mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: uiT, transparent: true, toneMapped: false}), 0, 0, 0.0056, phone);
  phone.userData.scr.visible = false;

  const GP = V3(1.8, 0, -2.6); // Grill
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id;
    const gone = T >= VANISH && T < RETURN;
    const late = T >= 58; // nach der Rückkehr im Garten
    // Licht: Nachmittag; Schatten um den Garten (Luftbild: großer Ausschnitt)
    const aerial = id === 'suburb';
    sun.shadow.camera.left = sun.shadow.camera.bottom = aerial ? -140 : -22; sun.shadow.camera.right = sun.shadow.camera.top = aerial ? 140 : 22; sun.shadow.camera.far = aerial ? 400 : 140; sun.shadow.camera.updateProjectionMatrix();
    sun.position.set(30, 40, 22); sun.target.position.set(0, 0, 0);
    if (aerial) { sun.position.set(90, 120, 66); }

    // Fleisch auf dem Grill: weg zwischen VANISH und RETURN; in lion/final vom Löwen gefressen
    meat.visible = !gone; platMeat.visible = !gone;
    const eaten = smooth(81, 89, T);
    platter.position.set(0.86, 0.94, 0);
    if (id === 'final') { platter.position.set(-1.95, 0.03, 0.95); platter.position.y = 0.03; platMeat.visible = true; platMeat.children.forEach((m, i) => { m.visible = i / platMeat.children.length >= eaten; }); }
    if (id === 'lion' && T > 76.5) platMeat.visible = false;
    // Grillrauch (immer leicht, mit Fleisch stärker)
    updateParticles(grillSmoke, aerial ? [] : [{type: 'smoke', pos: V3(GP.x - 0.1, 1.05, GP.z), r: 0.4, t0: -10, size: 0.7, rise: 0.8, col: [0.82, 0.82, 0.84], alpha: gone ? 0.12 : 0.32, share: 1}], T, V3(0.25, 0, 0.35));
    updateParticles(puff, T > VANISH - 0.05 && T < VANISH + 3 ? [{type: 'burstSmoke', pos: V3(GP.x - 0.15, 1.0, GP.z), r: 0.6, t0: VANISH, size: 0.35, rise: 0.5}] : [], T);
    // Luftbild: Grillrauch in allen Gärten ab RETURN
    if (aerial) { const src = []; lots.forEach((p, i) => { src.push({type: 'smoke', pos: p, r: 1.5, t0: RETURN + 0.2 + (i % 13) * 0.25, size: 9, rise: 3.0, col: [0.9, 0.9, 0.92], alpha: 0.6, share: 1}); });
      updateParticles(farSmoke, src, T, V3(2.5, 0, 1.5)); } else updateParticles(farSmoke, [], T);
    farSmoke.visible = aerial;

    // Papa am Grill (steht hinter dem Grill, Blick zum Garten +z)
    dad.position.set(GP.x, 0, GP.z - 0.75); dad.rotation.set(0, 0, 0); posePerson(dad, {});
    const du = dad.userData, flip = Math.sin(T * 2.2);
    du.armR.rotation.x = -0.9 + flip * 0.12; du.armR.rotation.z = 0.15; du.armR.userData.fore.rotation.x = -0.75; du.head.rotation.x = 0.45;
    du.armL.rotation.x = -0.3; du.armL.rotation.z = -0.15;
    tongs.rotation.x = -0.4; tongs.children.forEach((c, i) => c.rotation.z = (i ? 1 : -1) * (0.04 + 0.04 * Math.max(0, Math.sin(T * 6))));
    if (id === 'bbq') { const grab = smooth(VANISH + 0.1, VANISH + 0.5, T), stare = smooth(VANISH + 1.2, VANISH + 1.8, T), shrug = smooth(VANISH + 3.8, VANISH + 4.6, T);
      tongs.children.forEach((c, i) => c.rotation.z = (i ? 1 : -1) * 0.02 * (1 - grab)); // greift ins Leere
      du.armR.rotation.x = lerp(-0.9, -0.6, stare); du.head.rotation.x = lerp(0.45, 0.6, stare) - 0.5 * shrug; du.torso.rotation.x = 0.1 * stare;
      du.armL.rotation.z = lerp(-0.15, -0.9, shrug); du.armR.rotation.z = lerp(0.15, 0.9, shrug); du.armL.userData.fore.rotation.x = -1.2 * shrug; }
    // Mama und Kinder am Tisch / im Garten
    mom.position.set(-3.6, 0, -3.7); mom.rotation.set(0, 2.6, 0); posePerson(mom, {}); mom.userData.armR.rotation.x = -0.6; mom.userData.armR.userData.fore.rotation.x = -1.2;
    kid1.position.set(-1.9, 0, -2.2); kid1.rotation.set(0, 1.9, 0); posePerson(kid1, {}); kid2.position.set(-1.3, 0, -3.3); kid2.rotation.set(0, 2.2, 0); posePerson(kid2, {});
    const laugh = id === 'bbq' ? smooth(VANISH + 1.4, VANISH + 2.0, T) : 0;
    [kid1, kid2].forEach((k, i) => { const q = k.userData; q.torso.rotation.x = (0.35 + Math.sin(T * 20 + i) * 0.05) * laugh; q.armL.rotation.x = -1.0 * laugh; q.armL.userData.fore.rotation.x = -1.4 * laugh;
      if (i === 0) { q.armR.rotation.x = lerp(-0.2, -1.5, laugh); } });
    // Hund: sitzt vor dem Grill, wedelt; bbq: schnüffelt, legt den Kopf schief
    dog.position.set(GP.x - 0.2, 0, GP.z + 1.0); dog.rotation.set(0, Math.PI, 0);
    { const sn = id === 'bbq' ? smooth(VANISH + 0.6, VANISH + 1.2, T) : 0, tilt = id === 'bbq' ? smooth(VANISH + 3.0, VANISH + 3.6, T) : 0;
      poseLion(dog, {crouch: 0.5 * (1 - sn), lookUp: 0.9 - 0.4 * sn, tailWag: 1 - tilt, t: T}); dog.userData.head.rotation.z = 0.45 * tilt + 0.05 * Math.sin(T * 9) * sn; }

    // Löwe im Garten (back/lion/final)
    lionG.visible = late || id === 'suburb'; runners.forEach(l => l.visible = aerial);
    let lp = V3(3.4, 0, 9.2), ly = Math.PI; // hinter dem Zaun, Blick in den Garten
    if (late) {
      const L = lionG.userData;
      if (T < LION_JUMP - 0.8) { // steht am Zaun, schnuppert, brüllt
        const arrive = smooth(59, 62.5, T); lp = V3(lerp(-6, 3.4, arrive), 0, 9.6); ly = lerp(Math.PI / 2, Math.PI * 0.92, smooth(61.5, 63, T));
        poseLion(lionG, {gait: T * 6, walk: 1 - smooth(62, 62.6, T), look: Math.sin(T * 0.8) * 0.2, lookUp: 0.2, roar: smooth(66.0, 66.3, T) * (1 - smooth(67.4, 67.9, T)), t: T, tailWag: 0.4});
      } else if (T < LION_JUMP + 0.9) { // Sprung über den Zaun
        const k = clamp((T - (LION_JUMP - 0.3)) / 1.0); const crouch = smooth(LION_JUMP - 0.8, LION_JUMP - 0.3, T) * (1 - smooth(LION_JUMP - 0.3, LION_JUMP - 0.15, T));
        lp = V3(3.4, Math.sin(k * Math.PI) * 1.7, lerp(9.6, 5.6, k)); ly = Math.PI;
        poseLion(lionG, {crouch, leap: k > 0 && k < 1 ? k : 0, t: T});
      } else if (T < 80) { // läuft zum Grill, stellt sich auf die Hinterbeine an die Ablage
        const k = smooth(LION_JUMP + 0.9, 76.0, T); lp = V3(lerp(3.4, GP.x + 0.9, k), 0, lerp(5.6, GP.z + 1.4, k)); ly = Math.PI + lerp(0, 0.35, k);
        poseLion(lionG, {gait: T * 9, walk: 1 - smooth(75.6, 76.0, T), run: 0.6, roar: smooth(73.0, 73.3, T) * (1 - smooth(74.2, 74.6, T)), t: T, tailWag: 0.8});
        if (T > 76.0) { L.neck.rotation.x = 0.5 * smooth(76.0, 76.6, T); L.head.rotation.x = -0.3 * smooth(76.0, 76.6, T) + 0.1 * Math.sin(T * 6); } // schnuppert am Grill
      } else { // final: liegt vor dem Grill und frisst
        lp = V3(-1.0, 0, -1.7); ly = Math.PI / 2 - 0.15; poseLion(lionG, {lie: 1, eat: 1, t: T, tailWag: 0.6});
      }
      lionG.position.copy(lp); lionG.rotation.set(0, ly, 0);
    }
    if (aerial) { // drei Löwen laufen die Straße hinter den Gärten entlang auf unser Grundstück zu
      const k = smooth(RETURN + 3.5, 58, T);
      runners.forEach((l, i) => { const x = lerp(-150 - i * 9, -30 - i * 6, k); l.position.set(x, 0, 12.5 + (i - 1) * 1.6); l.rotation.set(0, Math.PI / 2, 0); poseLion(l, {gait: T * 11 + i, walk: T > RETURN + 3.4 ? 1 : 0, run: 1, t: T}); l.visible = T > RETURN + 3.4; });
      lionG.visible = false;
    }
    // Familie flüchtet (lion) und steht hinter der Glastür (final)
    if (late) {
      const turn = smooth(62.6, 63.4, T);
      du.head.rotation.x = lerp(du.head.rotation.x, 0.0, turn); dad.rotation.y = lerp(0, 0.35, turn);
      const flee = smooth(LION_JUMP - 0.2, DOOR_SLAM - 0.6, T);
      const run = p => { const a = p.position.clone(), b = V3(1.2 + (p === dad ? 0.4 : (p === mom ? -0.6 : p === kid1 ? 0 : 0.9)), 0, -8.4); return [a, b]; };
      [dad, mom, kid1, kid2].forEach((p, i) => { if (T < LION_JUMP - 0.2 + i * 0.15) return; const [a, b] = run(p); const k = clamp((T - (LION_JUMP - 0.2 + i * 0.15)) / (2.6 + i * 0.2));
        p.position.lerpVectors(a, b, easeIn(k) * 0.4 + k * 0.6); p.rotation.y = Math.atan2(b.x - a.x, b.z - a.z); posePerson(p, {walk: T * 13 + i, walkAmp: 1.3 * (1 - smooth(0.95, 1, k))});
        if (p === dad && k >= 1) { p.position.set(1.0, 0, -8.6); } });
      const ddog = smooth(LION_JUMP - 0.6, LION_JUMP + 1.2, T); if (ddog > 0) { dog.position.lerpVectors(V3(GP.x - 0.2, 0, GP.z + 1.0), V3(0.4, 0, -8.6), ddog); dog.rotation.y = Math.PI * 1.1; poseLion(dog, {gait: T * 16, walk: ddog < 1 ? 1 : 0, run: 1, t: T}); }
      if (id === 'final') { // Papa steht hinter der Glastür und schaut raus, Zange noch in der Hand
        dad.position.set(0.3, 0, -7.7); dad.rotation.set(0, 0.25, 0); posePerson(dad, {}); du.armR.rotation.x = -0.2; du.armR.userData.fore.rotation.x = -0.5; du.head.rotation.x = 0.15;
        du.armL.rotation.x = -1.9; du.armL.rotation.z = -0.1; du.armL.userData.fore.rotation.x = -0.6; // Hand an der Scheibe
        mom.position.set(-0.6, 0, -8.6); mom.rotation.set(0, 0.2, 0); posePerson(mom, {}); mom.userData.armR.rotation.x = -1.5; mom.userData.armR.userData.fore.rotation.x = -1.6;
        kid1.position.set(2.7, 0, -7.6); kid1.rotation.set(0, -0.2, 0); posePerson(kid1, {}); kid2.position.set(-1.4, 0, -9.0); kid2.rotation.set(0, 0, 0); posePerson(kid2, {});
        dog.position.set(2.2, 0, -9.4); dog.rotation.set(0, 0.2, 0); poseLion(dog, {lie: 1, t: T}); }
    }
    hb.visible = true;

    // Kamera
    rig.visible = id === 'intro'; camera.fov = 45; let shake = 0;
    if (id === 'intro') {
      camera.position.set(-0.4 + noise1(T, 1) * 0.02, 1.55 + noise1(T, 3) * 0.01, 4.2); camera.lookAt(GP.x - 0.4, 1.2, GP.z);
      phoneCam.position.copy(camera.position).add(V3(-0.02, -0.08, -0.3)); phoneCam.lookAt(GP.x - 0.2, 1.15, GP.z); phoneCam.updateProjectionMatrix();
      rig.visible = false; renderer.setRenderTarget(RT); renderer.render(scene, phoneCam); renderer.setRenderTarget(null); rig.visible = true;
      const g = uiC.getContext('2d'); g.clearRect(0, 0, 432, 936); g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(0, 0, 432, 70); g.fillRect(0, 800, 432, 136);
      g.fillStyle = '#ff3b30'; g.beginPath(); g.arc(150, 38, 9, 0, 7); g.fill(); g.fillStyle = '#fff'; g.font = '500 22px Plex'; g.textAlign = 'left'; g.fillText(`REC 00:0${Math.floor(t + 2)}`, 166, 46);
      g.strokeStyle = '#fff'; g.lineWidth = 6; g.beginPath(); g.arc(216, 868, 36, 0, 7); g.stroke(); g.fillStyle = '#ff3b30'; g.beginPath(); g.roundRect(198, 850, 36, 36, 6); g.fill();
      uiT.needsUpdate = true;
    } else if (id === 'wait') {
      const k = smooth(3.5, 10, T);
      camera.position.set(lerp(-0.6, 1.4, k) + noise1(T, 2) * 0.02, lerp(1.75, 1.7, k), lerp(5.0, 0.4, k)); camera.lookAt(GP.x - 0.2, lerp(1.25, 1.05, k), GP.z);
    } else if (id === 'bbq') {
      const k = smooth(VANISH + 2.4, VANISH + 3.8, T); // erst nah auf den Rost, dann halbtotale mit Hund und Kindern
      camera.position.set(lerp(GP.x - 0.3, 0.2, k) + noise1(T, 2) * 0.01, lerp(1.45, 1.65, k), lerp(GP.z + 1.9, 3.4, k)); camera.lookAt(lerp(GP.x - 0.15, 0.6, k), lerp(1.1, 1.0, k), lerp(GP.z - 0.3, -2.2, k));
      camera.fov = lerp(42, 46, k);
    } else if (id === 'suburb') {
      const k = smooth(48, 58, T);
      camera.position.set(lerp(-70, -22, k), lerp(70, 5, k), lerp(70, 24, k)); camera.lookAt(lerp(-50, -36, k), lerp(0, 0.8, k), lerp(0, 12, k)); camera.fov = 50;
    } else if (id === 'back') { // über Papas Schulter Richtung Zaun
      const k = smooth(62.6, 64.2, T);
      camera.position.set(lerp(4.4, 4.0, k) + noise1(T, 4) * 0.01, 1.6, lerp(-4.6, -4.2, k)); camera.lookAt(lerp(GP.x - 0.1, 3.3, k), lerp(1.1, 1.0, k), lerp(GP.z, 8.5, k)); camera.fov = lerp(46, 30, k);
    } else if (id === 'lion') { // seitliche Totale: Sprung über den Zaun, Flucht ins Haus
      const k = smooth(74, 79, T);
      camera.position.set(lerp(-6.5, -4.5, k), lerp(2.3, 1.6, k), lerp(4.5, 1.8, k)); camera.lookAt(lerp(1.6, GP.x + 0.6, k), lerp(1.0, 0.9, k), lerp(0.5, GP.z + 0.8, k)); camera.fov = 50;
      if (T > LION_JUMP + 0.65 && T < LION_JUMP + 1.2) shake = 0.02 * (1 - (T - LION_JUMP - 0.65) / 0.55);
    } else { // final: aus dem Haus durch die Glastür
      const k = smooth(80, 90, T);
      camera.position.set(lerp(1.9, 2.0, k), 1.5, lerp(-10.4, -9.9, k)); camera.lookAt(lerp(0.3, 0.2, k), 0.7, lerp(-2.2, -1.8, k)); camera.fov = 50;
    }
    if (shake) { camera.position.x += Math.sin(T * 60) * shake; camera.position.y += Math.cos(T * 47) * shake; }
    camera.updateProjectionMatrix();
  }};
}
