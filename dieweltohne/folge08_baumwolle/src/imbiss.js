// Imbiss. cash: Ein Jugendlicher bezahlt mit einem Zwanziger – der Schein und alle Scheine in der Kasse lösen sich auf, die Münzen bleiben.
// kitchen: Der Koch trägt eine Pfanne mit heißem Fett mit Topflappen. Die Topflappen verschwinden, die Pfanne fällt, das Fett entzündet sich am Gasherd.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut, posePerson, envMap, tileTex} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {cottonPerson, setCotton, noteTex} from './cotton.js';
import {NOTE_GONE, MITT_GONE, POT_DROP, FLARE} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.45;
  scene.background = new THREE.Color('#1c1a18');
  const hemi = new THREE.HemisphereLight('#fff4e0', '#5a4a3a', 0.7); scene.add(hemi);
  const lamps = [];
  for (const [x, z] of [[-2, 0], [2, 0], [0, -3.2]]) { const l = new THREE.PointLight('#ffe7c2', 14, 12, 1.6); l.position.set(x, 2.7, z); scene.add(l); lamps.push(l); }
  const key = new THREE.DirectionalLight('#fff1dc', 1.2); key.position.set(3, 6, 5); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, {left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 20}); key.shadow.bias = -0.0005; scene.add(key);
  const fireL = new THREE.PointLight('#ff7a2a', 0, 14, 1.4); fireL.position.set(-1.6, 1.4, -3.0); scene.add(fireL);

  // Raum: Gastraum vorn (z > 0), Theke bei z=0, Küche hinten (z < 0)
  const floorT = tileTex('#b9b2a6', '#a9a296'); floorT.repeat.set(6, 6);
  mesh(new THREE.PlaneGeometry(10, 12), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.6}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const wallT = tileTex('#efece4', '#e6e2d8'); wallT.repeat.set(5, 2);
  const wallM = new THREE.MeshStandardMaterial({map: wallT, roughness: 0.5});
  mesh(new THREE.PlaneGeometry(10, 3), wallM, 0, 1.5, -4.8, scene);
  const sideL = mesh(new THREE.PlaneGeometry(12, 3), wallM, -4.2, 1.5, 0, scene); sideL.rotation.y = Math.PI / 2;
  const sideR = mesh(new THREE.PlaneGeometry(12, 3), wallM, 4.2, 1.5, 0, scene); sideR.rotation.y = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(10, 12), mat('#e8e4dc'), 0, 3, 0, scene).rotation.x = Math.PI / 2;
  // Theke mit Glasvitrine
  const steel = mat('#b9bec4', {metalness: 0.85, roughness: 0.3});
  mesh(new THREE.BoxGeometry(6, 1.0, 0.8), mat('#7a3b2a', {roughness: 0.6}), 0, 0.5, 0, scene);
  mesh(new THREE.BoxGeometry(6.1, 0.05, 0.9), steel, 0, 1.02, 0, scene);
  const glassM = new THREE.MeshPhysicalMaterial({color: '#dfeef2', transparent: true, opacity: 0.25, roughness: 0.05, metalness: 0});
  mesh(new THREE.BoxGeometry(2.4, 0.4, 0.04), glassM, 1.6, 1.25, 0.38, scene).rotation.x = -0.35;
  // Salate in der Vitrine
  const sal = ['#d33a2b', '#3f8f3a', '#f2e6c2', '#8a3fa0', '#e0b13a'];
  sal.forEach((c, i) => mesh(new THREE.BoxGeometry(0.4, 0.08, 0.3), mat(c, {roughness: 0.8}), 0.75 + i * 0.42, 1.08, 0.1, scene));
  // Kasse
  const reg = new THREE.Group(); reg.position.set(-1.6, 1.05, 0.05); scene.add(reg);
  mesh(new RoundedBoxGeometry(0.42, 0.1, 0.36, 2, 0.02), mat('#2b2d31'), 0, 0.05, 0, reg);
  const screen = mesh(new RoundedBoxGeometry(0.3, 0.2, 0.03, 2, 0.01), mat('#202226'), 0, 0.28, -0.08, reg); screen.rotation.x = -0.3;
  const scrT = canvasTex(256, 160, (g, w, h) => { g.fillStyle = '#0d2a3a'; g.fillRect(0, 0, w, h); g.fillStyle = '#7fe3ff'; g.font = '700 34px Plex'; g.fillText('DÖNER  6,50', 12, 60); g.fillText('COLA   2,50', 12, 100); g.fillStyle = '#fff'; g.fillText('SUMME  9,00', 12, 145); });
  mesh(new THREE.PlaneGeometry(0.27, 0.17), new THREE.MeshBasicMaterial({map: scrT, toneMapped: false}), 0, 0, 0.017, screen);
  // Schublade (geöffnet zum Gastraum) mit Scheinen und Münzen
  const drawer = new THREE.Group(); drawer.position.set(0, -0.02, 0.32); reg.add(drawer);
  mesh(new THREE.BoxGeometry(0.4, 0.06, 0.3), mat('#1e1f22'), 0, 0, 0, drawer);
  const noteM = new THREE.MeshStandardMaterial({map: noteTex('eur'), roughness: 0.8});
  const drawerNotes = [];
  for (let i = 0; i < 4; i++) for (let k = 0; k < 6; k++) { const n = mesh(new THREE.BoxGeometry(0.075, 0.002, 0.13), noteM, -0.15 + i * 0.08, 0.032 + k * 0.003, -0.05, drawer); n.rotation.y = (k - 3) * 0.03; drawerNotes.push(n); }
  const coinM = mat('#c9a44a', {metalness: 0.9, roughness: 0.35});
  for (let i = 0; i < 5; i++) for (let k = 0; k < 4; k++) mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.002, 14), coinM, -0.16 + i * 0.08, 0.032 + k * 0.0022, 0.09, drawer);
  // Dönerspieß und Grill
  const spit = new THREE.Group(); spit.position.set(2.4, 1.05, -1.3); scene.add(spit);
  const meatT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#8a4a22'; g.fillRect(0, 0, w, h); const r = rng(4); for (let i = 0; i < 1200; i++) { g.fillStyle = r() < 0.5 ? 'rgba(60,25,8,0.5)' : 'rgba(190,120,60,0.5)'; g.fillRect(r() * w, r() * h, 6, 3); } });
  const cone = mesh(new THREE.CylinderGeometry(0.22, 0.14, 0.75, 20), new THREE.MeshStandardMaterial({map: meatT, roughness: 0.7}), 0, 0.5, 0, spit);
  mesh(new THREE.CylinderGeometry(0.01, 0.01, 1.1, 6), steel, 0, 0.5, 0, spit);
  mesh(new THREE.BoxGeometry(0.15, 0.9, 0.5), mat('#2b2b2b'), 0.42, 0.5, 0, spit);
  mesh(new THREE.PlaneGeometry(0.1, 0.7), new THREE.MeshBasicMaterial({color: '#ff5a1a'}), 0.34, 0.5, 0, spit).rotation.y = -Math.PI / 2;
  // Menütafel
  const menuT = canvasTex(1024, 300, (g, w, h) => { g.fillStyle = '#1b1b1b'; g.fillRect(0, 0, w, h); g.fillStyle = '#ffd23f'; g.font = '900 64px sans-serif'; g.fillText('IMBISS AM ECK', 30, 80);
    g.fillStyle = '#fff'; g.font = '500 44px Plex'; [['Döner', '6,50'], ['Dürüm', '7,50'], ['Pommes', '3,50'], ['Falafel', '6,00']].forEach(([a, b], i) => { g.fillText(a, 40 + (i % 2) * 500, 160 + Math.floor(i / 2) * 70); g.fillText(b + ' €', 330 + (i % 2) * 500, 160 + Math.floor(i / 2) * 70); }); });
  mesh(new THREE.PlaneGeometry(3.4, 1.0), new THREE.MeshBasicMaterial({map: menuT, toneMapped: false}), 0, 2.45, -4.78, scene);
  // Küche: Gasherd links hinten, Abzugshaube, Fritteuse
  const stove = new THREE.Group(); stove.position.set(-1.6, 0, -3.9); scene.add(stove);
  mesh(new THREE.BoxGeometry(1.6, 0.9, 0.8), steel, 0, 0.45, 0, stove);
  mesh(new THREE.BoxGeometry(1.6, 0.04, 0.8), mat('#222'), 0, 0.92, 0, stove);
  const burners = [];
  for (const [x, z] of [[-0.4, -0.15], [0.4, -0.15], [-0.4, 0.2], [0.4, 0.2]]) {
    mesh(new THREE.CylinderGeometry(0.11, 0.12, 0.03, 16), mat('#111'), x, 0.95, z, stove);
    const f = mesh(new THREE.TorusGeometry(0.08, 0.018, 6, 20), new THREE.MeshBasicMaterial({color: '#4aa8ff', transparent: true, opacity: 0.85}), x, 0.975, z, stove); f.rotation.x = Math.PI / 2; f.castShadow = false; burners.push(f);
  }
  mesh(new THREE.BoxGeometry(1.9, 0.5, 1.0), steel, 0, 2.5, 0, stove);
  const fryer = mesh(new THREE.BoxGeometry(0.7, 0.95, 0.7), steel, 0.95, 0.475, -3.9, scene);
  mesh(new THREE.BoxGeometry(0.55, 0.02, 0.5), mat('#c79a3a', {roughness: 0.2}), 0.95, 0.94, -3.9, scene);
  // Arbeitsplatte rechts mit Geschirrtuch
  mesh(new THREE.BoxGeometry(2.2, 0.9, 0.8), steel, 2.6, 0.45, -3.9, scene);
  const towel = mesh(new THREE.BoxGeometry(0.4, 0.01, 0.3), mat('#e8e2d4', {roughness: 1}), 2.2, 0.91, -3.8, scene);
  const towelStripe = mesh(new THREE.BoxGeometry(0.4, 0.012, 0.05), mat('#c0392b'), 2.2, 0.91, -3.7, scene);
  // Regal mit Brötchen
  for (let i = 0; i < 6; i++) mesh(new THREE.SphereGeometry(0.1, 10, 8), mat('#d9a35a'), 2.0 + i * 0.22, 1.65, -4.6, scene).scale.set(1.4, 0.6, 1);
  mesh(new THREE.BoxGeometry(1.6, 0.03, 0.35), steel, 2.55, 1.58, -4.6, scene);

  // Personen
  const cashier = cottonPerson(41, {top: '#2b2b2b', under: '#3b5bd9', skin: '#a8714f', hair: '#111', denim: '#2a2f3a'});
  const apron = mesh(new THREE.BoxGeometry(0.42, 0.75, 0.04), mat('#f2efe8', {roughness: 1}), 0, 0.05, 0.14, cashier.userData.hips); cashier.userData.cotton.cot.push(apron);
  scene.add(cashier);
  const cust = cottonPerson(52, {hoodie: '#e2b23a', top: '#1d1d1d', under: '#2fa36b', skin: '#f1c7a5', hair: '#5a3b22'});
  scene.add(cust);
  const noteHand = mesh(new THREE.BoxGeometry(0.075, 0.002, 0.13), noteM, 0, -0.33, 0.04, cust.userData.armR.userData.fore); noteHand.rotation.x = 1.2;
  const cust2 = cottonPerson(57, {top: '#4aa3c7', under: '#e94f6a', skin: '#7a4d33', hair: '#111', ponytail: true}); scene.add(cust2);
  const cook = cottonPerson(63, {top: '#f2f2f2', under: '#2b2b2b', skin: '#d9a47e', hair: '#2a1d15', denim: '#3a3a3a'});
  const capron = mesh(new THREE.BoxGeometry(0.42, 0.8, 0.04), mat('#f4f1ea', {roughness: 1}), 0, 0.02, 0.14, cook.userData.hips); cook.userData.cotton.cot.push(capron);
  const capronTop = mesh(new THREE.BoxGeometry(0.3, 0.3, 0.04), mat('#f4f1ea', {roughness: 1}), 0, 0.42, 0.13, cook.userData.torso); cook.userData.cotton.cot.push(capronTop);
  scene.add(cook);
  // Pfanne mit Fett, Topflappen
  const pan = new THREE.Group(); scene.add(pan);
  const panBody = mesh(new THREE.CylinderGeometry(0.2, 0.17, 0.08, 24, 1, true), mat('#3a3a3c', {metalness: 0.7, roughness: 0.4, side: THREE.DoubleSide}), 0, 0, 0, pan);
  mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.01, 24), mat('#3a3a3c', {metalness: 0.7, roughness: 0.4}), 0, -0.04, 0, pan);
  const oil = mesh(new THREE.CylinderGeometry(0.19, 0.19, 0.01, 24), new THREE.MeshStandardMaterial({color: '#d9a23a', roughness: 0.1, metalness: 0.2, emissive: '#5a3a08'}), 0, 0.015, 0, pan);
  const handles = [];
  for (const s of [-1, 1]) { const h = mesh(new THREE.BoxGeometry(0.09, 0.03, 0.05), mat('#3a3a3c', {metalness: 0.7}), s * 0.25, 0.02, 0, pan); handles.push(h); }
  const mitts = [-1, 1].map(s => { const m = mesh(new RoundedBoxGeometry(0.13, 0.06, 0.13, 2, 0.02), mat('#d84a3a', {roughness: 1}), s * 0.25, 0.03, 0, pan); return m; });
  const spill = mesh(new THREE.CircleGeometry(1, 32), new THREE.MeshStandardMaterial({color: '#c79a3a', roughness: 0.05, transparent: true, opacity: 0.85}), -1.6, 0.012, -3.2, scene); spill.rotation.x = -Math.PI / 2; spill.castShadow = false;
  const fire = particles(900, 'flame'); scene.add(fire);
  const smoke = particles(500, 'smoke'); scene.add(smoke);
  const puff = particles(120, 'smoke'); scene.add(puff);

  const camera = new THREE.PerspectiveCamera(48, 1080 / 1920, 0.03, 100);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id;
    const noteGone = T >= NOTE_GONE, mittGone = T >= MITT_GONE;
    // Kasse
    drawerNotes.forEach(n => n.visible = !noteGone);
    noteHand.visible = !noteGone;
    cashier.position.set(-1.6, 0, -0.75); cashier.rotation.set(0, 0, 0); posePerson(cashier, {});
    { const u = cashier.userData; const reach = smooth(17.2, 18.2, T) * (1 - smooth(19.3, 20.0, T));
      u.armR.rotation.x = -1.2 * reach; u.armR.userData.fore.rotation.x = -0.5 * reach; u.armL.rotation.x = -0.6; u.armL.userData.fore.rotation.x = -0.9;
      const shock = smooth(18.9, 19.4, T); u.head.rotation.x = 0.35 * shock; u.armL.rotation.z = -0.5 * shock; u.armR.rotation.z = 0.5 * shock;
      if (T > 21) { u.head.rotation.x = 0; u.head.rotation.y = 0.4 * Math.sin((T - 21) * 3); } }
    setCotton(cashier, !noteGone);
    cust.position.set(-1.55, 0, 0.8); cust.rotation.set(0, Math.PI, 0); posePerson(cust, {});
    { const u = cust.userData; const give = smooth(17.0, 17.9, T) * (1 - smooth(19.6, 20.3, T));
      u.armR.rotation.x = -1.35 * give; u.armR.userData.fore.rotation.x = -0.3 * give;
      const look = smooth(18.9, 19.5, T); u.head.rotation.x = 0.5 * look * (T < 20.6 ? 1 : 0) ; if (T > 20.6) { u.head.rotation.x = 0.55; u.armL.rotation.x = -0.6; u.armR.rotation.x = -0.6; u.armL.userData.fore.rotation.x = -0.9; u.armR.userData.fore.rotation.x = -0.9; } }
    setCotton(cust, !noteGone);
    cust2.position.set(0.6, 0, 1.5); cust2.rotation.set(0, Math.PI - 0.3, 0); posePerson(cust2, {});
    { const u = cust2.userData; const k = smooth(19.4, 20.0, T); u.armL.rotation.x = -2.0 * k; u.armL.userData.fore.rotation.x = -1.5 * k; u.torso.rotation.x = -0.15 * k; }
    setCotton(cust2, !noteGone);
    cashier.visible = cust.visible = cust2.visible = id === 'cash';
    // Küche: Koch trägt die Pfanne von der Fritteuse zum Herd
    const walk = smooth(24.0, 25.4, T);
    let cx = lerp(0.5, -1.25, walk), cz = -3.15;
    cook.position.set(cx, 0, cz); cook.rotation.set(0, -Math.PI / 2 + 0.25, 0); posePerson(cook, {walk: T < 25.4 ? T * 7 : 0, walkAmp: T < 25.4 ? 0.5 : 0});
    const u = cook.userData;
    const hold = T < POT_DROP ? 1 : 0;
    u.armL.rotation.x = -1.1; u.armR.rotation.x = -1.1; u.armL.userData.fore.rotation.x = -0.4; u.armR.userData.fore.rotation.x = -0.4; u.armL.rotation.z = 0.25; u.armR.rotation.z = -0.25;
    const ouch = smooth(MITT_GONE + 0.05, MITT_GONE + 0.3, T);
    if (!hold) { const back = smooth(POT_DROP, POT_DROP + 0.5, T); const away = smooth(FLARE, FLARE + 0.5, T);
      u.armL.rotation.x = lerp(-1.1, -2.6, away); u.armR.rotation.x = lerp(-1.1, -2.6, away); u.armL.rotation.z = -0.6 * away; u.armR.rotation.z = 0.6 * away;
      u.torso.rotation.x = -0.3 * away; cook.position.x = cx + 1.2 * easeOut(clamp((T - FLARE) / 0.9)); cook.position.z = cz + 0.5 * easeOut(clamp((T - FLARE) / 0.9));
      cook.rotation.y = -Math.PI / 2 + 0.25 + 1.2 * away; }
    else if (ouch > 0) { u.armL.userData.fore.rotation.x = -0.4 - 0.3 * Math.sin(T * 40) * ouch; }
    setCotton(cook, !mittGone);
    cook.visible = id === 'kitchen';
    // Pfanne: in den Händen vor dem Bauch, dann fällt sie, kippt und das Fett spritzt
    const hand = V3(cook.position.x - 0.55 * Math.cos(cook.rotation.y), 1.0, cook.position.z + 0.55 * Math.sin(cook.rotation.y));
    if (T < POT_DROP) { pan.position.set(cx - 0.5, 1.02 + noise1(T * 4, 2) * 0.01 - (ouch > 0 ? 0.03 * Math.sin(T * 50) * ouch : 0), cz); pan.rotation.set(0, 0, 0); }
    else { const d = T - POT_DROP; const fall = Math.min(1.02 - 0.95, 0.5 * 9.81 * d * d); // fällt auf die Herdkante, kippt nach vorn
      pan.position.set(cx - 0.5 - 0.1 * clamp(d / 0.2), 1.02 - fall - (d > 0.12 ? Math.min(0.9, 0.5 * 9.81 * (d - 0.12) ** 2) : 0), cz - 0.25 * clamp(d / 0.3));
      pan.rotation.set(-1.6 * easeOut(clamp(d / 0.35)), 0, 0.5 * clamp(d / 0.35)); pan.position.y = Math.max(0.04, pan.position.y); }
    oil.visible = T < POT_DROP + 0.15;
    mitts.forEach(m => m.visible = !mittGone);
    towel.visible = towelStripe.visible = !mittGone;
    spill.visible = T > POT_DROP + 0.15; spill.scale.setScalar(lerp(0.05, 0.9, easeOut(clamp((T - POT_DROP - 0.15) / 0.6))));
    // Feuer: Stichflamme am Herd, dann brennt der Herd und die Lache
    const fk = T > FLARE ? 1 : 0;
    const flareK = Math.exp(-(T - FLARE) * 1.6) * fk;
    const srcs = [];
    if (fk) {
      srcs.push({type: 'flame', pos: V3(-1.6, 1.0, -3.85), r: 0.7 + 0.5 * flareK, t0: FLARE, size: 0.55 + 0.8 * flareK, rise: 2.4 + 3 * flareK, power: 1, share: 3});
      srcs.push({type: 'flame', pos: V3(-1.6, 0.08, -3.2), r: 0.6 * smooth(FLARE, FLARE + 1.5, T) + 0.1, t0: FLARE + 0.1, size: 0.45, rise: 1.6, power: 0.9, share: 2});
      srcs.push({type: 'burst', pos: V3(-1.6, 1.1, -3.6), r: 1.6, t0: FLARE, size: 1.2, rise: 2.5, power: 1, share: 1.5});
    }
    updateParticles(fire, id === 'kitchen' ? srcs : [], T, V3(0.1, 0, 0.1));
    updateParticles(smoke, id === 'kitchen' && fk ? [{type: 'smoke', pos: V3(-1.6, 2.2, -3.8), r: 0.8, t0: FLARE + 0.3, size: 1.4, rise: 0.4, alpha: 0.6, share: 1}] : [], T, V3(0.4, 0, 0.6));
    updateParticles(puff, [], T);
    fireL.intensity = fk ? (30 + 120 * flareK) * flicker(T, 3) : 0;
    burners.forEach(b => b.material.opacity = 0.75 + 0.15 * Math.sin(T * 30));
    spit.rotation.y = T * 0.6;
    // Kamera
    camera.fov = 48;
    if (id === 'cash') { // über die Schulter des Kunden auf Hand, Schein und Kasse
      const u2 = smooth(17, 24, T);
      camera.position.set(lerp(-0.55, -0.7, u2), lerp(1.95, 1.85, u2), lerp(1.45, 1.35, u2)); camera.lookAt(-1.65, 1.02, 0.15);
    } else { // Küche von der Seite
      const sh = fk ? 0.03 * Math.exp(-(T - FLARE) * 2) : 0;
      camera.position.set(1.6 + noise1(T * 15, 1) * sh, 1.55 + noise1(T * 15, 2) * sh, -0.6 - smooth(24, 31, T) * 0.4); camera.lookAt(-1.0, 1.0, -3.6);
    }
    camera.updateProjectionMatrix();
  }};
}
