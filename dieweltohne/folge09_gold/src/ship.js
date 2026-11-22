// Hafeneinfahrt bei Nacht. Ein Containerschiff fährt auf eine Fachwerkbrücke zu – dann Blackout an Bord: Licht weg, Ruder weg.
// Es treibt gegen den Pfeiler, die Brücke stürzt ins Wasser (wie 2024 in Baltimore nach einem Stromausfall).
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, skyDome, envMap, easeIn} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {BLACKOUT, SHIP_HIT, SPAN_FALL} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const PIER = 70, DECK = 52;

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.12;
  scene.fog = new THREE.Fog('#1d2a44', 300, 1600);
  scene.add(skyDome('#0a1630', '#27406e', '#6a5a7a', 1800));
  scene.add(new THREE.HemisphereLight('#7f9fd0', '#101622', 0.9));
  const moon = new THREE.DirectionalLight('#b8ccff', 1.3); moon.position.set(-200, 300, -400); scene.add(moon);
  // Sterne
  { const n = 1200, r = rng(8), P = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const a = r() * Math.PI * 2, e = 0.08 + r() * 1.3; P.set([Math.cos(a) * Math.cos(e) * 1600, Math.sin(e) * 1600, Math.sin(a) * Math.cos(e) * 1600], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); scene.add(new THREE.Points(g, new THREE.PointsMaterial({color: '#cfd8ff', size: 1.3, sizeAttenuation: false, fog: false}))); }
  // Wasser
  const waterM = new THREE.MeshStandardMaterial({color: '#16283c', roughness: 0.25, metalness: 0.3});
  mesh(new THREE.PlaneGeometry(6000, 6000), waterM, 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  // Ufer mit Stadtlichtern hinter der Brücke
  const shoreM = mat('#11151c', {roughness: 1});
  mesh(new THREE.BoxGeometry(3000, 8, 400), shoreM, 0, 3, -700, scene);
  { const r = rng(12); for (let i = 0; i < 80; i++) { const x = -1200 + r() * 2400, h = 20 + r() * 90, w = 20 + r() * 40;
      const t = facadeTex('#1a1d24', i + 40, Math.round(h / 4), 6); const m = new THREE.MeshStandardMaterial({map: t, emissive: '#ffcf8a', emissiveMap: t, emissiveIntensity: 0.6, roughness: 0.9});
      mesh(new THREE.BoxGeometry(w, h, 30), m, x, h / 2 + 6, -620 - r() * 200, scene); } }
  // Brücke: drei Felder; das Hauptfeld und das rechte Feld können einstürzen
  const steelM = mat('#3d4a57', {metalness: 0.6, roughness: 0.5}), conM = mat('#6a6c70', {roughness: 0.9});
  const lampM = new THREE.MeshStandardMaterial({color: '#ffd08a', emissive: '#ffb050', emissiveIntensity: 3});
  const spans = [];
  const span = (x0, x1, arch) => { const g = new THREE.Group(); g.position.set(x0, DECK, 0); scene.add(g); const L = x1 - x0;
    mesh(new THREE.BoxGeometry(L, 2.2, 22), conM, L / 2, 0, 0, g);
    for (const z of [-10.5, 10.5]) {
      const top = x => arch ? 8 + 22 * Math.sin(Math.PI * x / L) : 10;
      for (let x = 0; x < L; x += 10) { const h0 = top(x), h1 = top(x + 10);
        const tc = mesh(new THREE.BoxGeometry(10.4, 1.2, 1.2), steelM, x + 5, (h0 + h1) / 2, z, g); tc.rotation.z = Math.atan2(h1 - h0, 10);
        mesh(new THREE.BoxGeometry(0.8, h0, 0.8), steelM, x, h0 / 2, z, g);
        const d = mesh(new THREE.BoxGeometry(0.6, Math.hypot(10, h1), 0.6), steelM, x + 5, h1 / 2, z, g); d.rotation.z = Math.atan2(10, h1) * (x % 20 ? 1 : -1);
        if (x % 20 === 0) mesh(new THREE.SphereGeometry(0.6, 6, 4), lampM, x + 5, 3, z * 0.95, g); }
      mesh(new THREE.BoxGeometry(L, 1.2, 1.2), steelM, L / 2, 1.6, z, g); }
    for (let x = 0; x < L; x += 20) mesh(new THREE.BoxGeometry(1, 1, 22), steelM, x, arch ? 8 + 22 * Math.sin(Math.PI * x / L) : 10, 0, g);
    g.userData = {x0, L}; spans.push(g); return g; };
  span(-320, -PIER, false); const main = span(-PIER, PIER, true); const right = span(PIER, 320, false);
  // Pfeiler
  const piers = [];
  for (const x of [-PIER, PIER, -320, 320]) { const g = new THREE.Group(); g.position.set(x, 0, 0); scene.add(g);
    mesh(new THREE.BoxGeometry(8, DECK - 1, 18), conM, 0, (DECK - 1) / 2, 0, g); mesh(new THREE.CylinderGeometry(9, 11, 6, 16), conM, 0, 2, 0, g); piers.push(g); }
  // Autos auf der Brücke (Scheinwerferpunkte)
  const carM = new THREE.MeshStandardMaterial({color: '#fff', emissive: '#fff3d6', emissiveIntensity: 3});
  const tailM = new THREE.MeshStandardMaterial({color: '#f22', emissive: '#ff2010', emissiveIntensity: 3});
  const cars = []; for (let i = 0; i < 14; i++) { const c = new THREE.Group(); mesh(new THREE.BoxGeometry(4.2, 1.4, 1.9), mat('#2a2d33'), 0, 0.8, 0, c);
    mesh(new THREE.BoxGeometry(0.2, 0.3, 1.6), i % 2 ? carM : tailM, 2.15, 0.7, 0, c); scene.add(c); cars.push({c, ph: i * 47 % 640, lane: i % 2 ? -4 : 4, dir: i % 2 ? 1 : -1, fall: 0}); }

  // Containerschiff (Bug zeigt nach -z)
  const ship = new THREE.Group(); scene.add(ship);
  const hullM = mat('#1c2a3a', {roughness: 0.6}), redM = mat('#7a1e1e', {roughness: 0.7}), whiteM = mat('#d9dbde', {roughness: 0.6});
  const hs = new THREE.Shape(); hs.moveTo(-22, 0); hs.lineTo(22, 0); hs.lineTo(22, -110); hs.quadraticCurveTo(20, -132, 0, -138); hs.quadraticCurveTo(-20, -132, -22, -110); hs.lineTo(-22, 0);
  hs.lineTo(-22, 100); hs.quadraticCurveTo(-20, 112, 0, 112); hs.quadraticCurveTo(20, 112, 22, 100); hs.lineTo(22, 0);
  const hullG = new THREE.ExtrudeGeometry(hs, {depth: 22, bevelEnabled: false}); hullG.rotateX(Math.PI / 2); hullG.translate(0, 18, 0);
  mesh(hullG, hullM, 0, 0, 0, ship); mesh(new THREE.BoxGeometry(44.4, 6, 248), redM, 0, -1, -13, ship);
  // Container
  const cg = new THREE.BoxGeometry(2.4, 2.5, 12); const cols = ['#b5452e', '#2d6a9a', '#3f8a52', '#d1a23a', '#7a3f8a', '#8a8f96', '#c9643a', '#2a4a6a'];
  const cont = new THREE.InstancedMesh(cg, new THREE.MeshStandardMaterial({roughness: 0.7}), 3000); { const r = rng(17), m4 = new THREE.Matrix4(), c = new THREE.Color(); let n = 0;
    for (let bay = 0; bay < 15; bay++) for (let row = 0; row < 16; row++) { const layers = 5 + Math.floor(r() * 4); for (let l = 0; l < layers && n < 3000; l++) {
      m4.makeTranslation(-18 + row * 2.45, 19.3 + l * 2.55, -118 + bay * 13); cont.setMatrixAt(n, m4); c.set(cols[Math.floor(r() * cols.length)]); cont.setColorAt(n, c); n++; } } cont.count = n; }
  ship.add(cont);
  // Brücke/Aufbau achtern mit Fenstern, Schornstein
  const winT = canvasTex(256, 256, g => { g.fillStyle = '#d9dbde'; g.fillRect(0, 0, 256, 256); for (let y = 20; y < 256; y += 40) for (let x = 10; x < 256; x += 30) { g.fillStyle = '#ffe1a0'; g.fillRect(x, y, 20, 18); } });
  const winM = new THREE.MeshStandardMaterial({map: winT, emissive: '#ffffff', emissiveMap: winT, emissiveIntensity: 1.2, roughness: 0.6});
  mesh(new THREE.BoxGeometry(40, 26, 14), winM, 0, 31, 82, ship); mesh(new THREE.BoxGeometry(46, 2, 16), whiteM, 0, 45, 82, ship);
  const funnel = mesh(new THREE.BoxGeometry(8, 14, 10), mat('#202a36'), 0, 48, 96, ship);
  // Positionslichter und Decksstrahler
  const navM = [new THREE.MeshStandardMaterial({color: '#f00', emissive: '#ff2020', emissiveIntensity: 4}), new THREE.MeshStandardMaterial({color: '#0f0', emissive: '#20ff40', emissiveIntensity: 4}), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#ffffff', emissiveIntensity: 4})];
  mesh(new THREE.SphereGeometry(0.9, 8, 6), navM[0], -23, 44, 82, ship); mesh(new THREE.SphereGeometry(0.9, 8, 6), navM[1], 23, 44, 82, ship); mesh(new THREE.SphereGeometry(0.9, 8, 6), navM[2], 0, 60, 70, ship);
  const flood = []; for (const z of [-100, -60, -20, 20, 60]) { const l = new THREE.PointLight('#ffd9a0', 9000, 90, 2); l.position.set(0, 46, z); ship.add(l); flood.push(l); }
  const smoke = particles(500, 'smoke'); scene.add(smoke);
  const spray = particles(900, 'smoke'); scene.add(spray);
  const sparks = particles(300, 'flame'); scene.add(sparks);

  // Bahn des Schiffs: geradeaus durch die Mitte, nach dem Blackout dreht es nach rechts ab und treibt gegen den Pfeiler
  const Y = V3(0, 1, 0);
  function shipPose(T) {
    const t = Math.min(T, SHIP_HIT) - 39;
    const drift = smooth(BLACKOUT + 0.8, SHIP_HIT, T);
    let bz = 160 - 25 * t; const bx = lerp(0, PIER + 1, Math.pow(drift, 1.4));
    let yaw = -0.3 * drift;
    if (T > SHIP_HIT) { const k = T - SHIP_HIT; bz -= 3 * (1 - Math.exp(-k * 2)); yaw -= 0.06 * (1 - Math.exp(-k * 2)); }
    const off = V3(0, 0, -138).applyAxisAngle(Y, yaw);
    return {x: bx - off.x, z: bz - off.z, yaw};
  }
  const camera = new THREE.PerspectiveCamera(48, 1080 / 1920, 0.5, 6000); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    // Licht an Bord: aus, kurz flackernd wieder an, endgültig aus
    const on = T < BLACKOUT || (T > BLACKOUT + 1.0 && T < BLACKOUT + 1.5 && Math.sin(T * 60) > 0);
    winM.emissiveIntensity = on ? 1.2 : 0.02; navM.forEach(m => m.emissiveIntensity = on ? 4 : 0); flood.forEach(l => l.intensity = on ? 9000 : 0);
    const sp = shipPose(T); ship.position.set(sp.x, 0, sp.z); ship.rotation.y = sp.yaw;
    // Brücke stürzt ein
    const f1 = clamp((T - SPAN_FALL) / 2.0), f2 = clamp((T - SPAN_FALL - 0.4) / 2.2);
    main.rotation.z = -0.35 * easeIn(f1); main.position.y = DECK - 56 * easeIn(f1); main.position.x = -PIER + 6 * f1;
    right.rotation.z = 0.25 * easeIn(f2); right.position.y = DECK - 54 * easeIn(f2) * 0.85;
    piers[1].rotation.z = -0.5 * easeIn(clamp((T - SHIP_HIT) / 1.4)); piers[1].position.y = -10 * easeIn(clamp((T - SHIP_HIT) / 1.4));
    lampM.emissiveIntensity = T < SPAN_FALL ? 3 : 3 * (1 - smooth(SPAN_FALL, SPAN_FALL + 0.6, T));
    // Autos fahren, auf dem einstürzenden Teil fallen sie mit
    cars.forEach(o => { const x = ((o.ph + T * 22 * o.dir) % 640 + 640) % 640 - 320; const onMain = x > -PIER && x < PIER, onRight = x >= PIER;
      const xf = ((o.ph + SPAN_FALL * 22 * o.dir) % 640 + 640) % 640 - 320; const sx = T > SPAN_FALL ? xf : x;
      let y = DECK + 1.1; if (T > SPAN_FALL && (sx > -PIER)) { const ff = sx < PIER ? f1 : f2; y = DECK + 1.1 - 56 * easeIn(ff); }
      o.c.position.set(sx, y, o.lane); o.c.rotation.y = o.dir > 0 ? 0 : Math.PI; o.c.visible = y > -2; });
    // Schwarzer Rauch aus dem Schornstein beim Blackout
    funnel.updateMatrixWorld(); const fp = funnel.getWorldPosition(new THREE.Vector3());
    updateParticles(smoke, T > BLACKOUT ? [{type: 'smoke', pos: fp.clone().add(V3(0, 8, 0)), r: 3, t0: BLACKOUT, t1: BLACKOUT + 2.5, size: 12, rise: 9, col: [0.05, 0.05, 0.06], alpha: 0.85, share: 1}] : [], T, V3(-6, 0, 2));
    // Aufprall und Einsturz: Gischt
    const imp = V3(PIER, 4, 14);
    updateParticles(spray, T > SHIP_HIT ? [{type: 'burstSmoke', pos: imp, r: 20, t0: SHIP_HIT, size: 18, rise: 4, share: 1},
      {type: 'burstSmoke', pos: V3(0, 2, 0), r: 60, t0: SPAN_FALL + 1.5, size: 26, rise: 6, share: 2}, {type: 'burstSmoke', pos: V3(160, 2, 0), r: 50, t0: SPAN_FALL + 2.0, size: 24, rise: 6, share: 1.5}] : [], T, V3(2, 0, 1));
    updateParticles(sparks, T > SHIP_HIT ? [{type: 'burst', pos: V3(PIER - 4, 30, 8), r: 10, t0: SHIP_HIT, size: 5, power: 1, share: 1}] : [], T);
    // Kamera
    camera.fov = 48;
    if (T < 42.6) { // erhöht hinter dem Schiff: vor ihm die Brücke
      const k = smooth(39, 42.6, T);
      camera.position.set(sp.x + lerp(70, 60, k), lerp(135, 120, k), sp.z + lerp(250, 225, k)); camera.lookAt(sp.x * 0.5 + 6, lerp(30, 34, k), lerp(-60, -30, k));
    } else if (T < SHIP_HIT - 0.3) { // von der Brücke nach unten: der Bug treibt auf den Pfeiler zu
      const k = smooth(42.6, SHIP_HIT, T);
      camera.position.set(lerp(165, 155, k), lerp(48, 44, k), lerp(70, 62, k)); camera.lookAt(lerp(45, 62, k), lerp(22, 24, k), lerp(70, 20, k));
    } else { // weit und erhöht: der Einsturz
      const k = smooth(SHIP_HIT, 48, T);
      camera.position.set(lerp(-170, -190, k) + noise1(T * 6, 1) * 1.2 * (1 - k), lerp(95, 105, k), lerp(190, 215, k)); camera.lookAt(lerp(20, 15, k), lerp(28, 22, k), 0);
    }
    camera.updateProjectionMatrix();
  }};
}
