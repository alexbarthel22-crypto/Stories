// Innenstadt mit Platz. cube_drop: Das Gold kommt zurück – alles auf einmal, als Würfel von 22 m Kantenlänge, der auf den Platz kracht.
// cube_night: Nacht, kein Strom (in keinem Chip steckt mehr Gold), Feuer in Tonnen, Menschenmassen strömen zum Würfel.
// aerial: Luftbild der dunklen Stadt. final: totes Handy in der Hand, davor der Würfel.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, asphaltTex, tileTex, skyDome, easeIn, easeOut, makePerson, posePerson, envMap, makeCar} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {makePhone, makeHands} from './phone.js';
import {GOLD} from './gold.js';
import {RETURN, CUBE_LAND} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const S = 22; // Kantenlänge des Würfels

function darkFacade(base, seed, floors, cols) {
  const r = rng(seed);
  return canvasTex(256, 512, (g, w, h) => {
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 1500; i++) { g.fillStyle = `rgba(0,0,0,${r() * 0.06})`; g.fillRect(r() * w, r() * h, 3, 3); }
    const fh = h / floors, cw = w / cols;
    for (let f = 0; f < floors; f++) for (let c = 0; c < cols; c++) {
      const x = c * cw + cw * 0.22, y = f * fh + fh * 0.2, ww = cw * 0.56, hh = fh * 0.55;
      g.fillStyle = 'rgba(255,255,255,0.25)'; g.fillRect(x - 4, y - 4, ww + 8, hh + 8);
      const grd = g.createLinearGradient(x, y, x + ww, y + hh); grd.addColorStop(0, '#3d4a57'); grd.addColorStop(1, '#1a2028');
      g.fillStyle = grd; g.fillRect(x, y, ww, hh); g.fillStyle = 'rgba(255,255,255,0.12)'; g.fillRect(x + ww / 2 - 1.5, y, 3, hh);
    }
    g.fillStyle = 'rgba(0,0,0,0.3)'; g.fillRect(0, h - fh * 0.9, w, fh * 0.9);
  });
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const env = envMap(renderer); scene.environment = env;
  scene.fog = new THREE.Fog('#c99a7a', 120, 900);
  const skyDusk = skyDome('#2b2f5a', '#c4705a', '#f2b27a', 1500), skyNight = skyDome('#02040a', '#08101f', '#151a28', 1500);
  scene.add(skyDusk, skyNight);
  const hemi = new THREE.HemisphereLight('#ffd0b0', '#3a3440', 0.9); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#ffb070', 2.4); sun.position.set(-120, 60, -80); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -90, right: 90, top: 90, bottom: -90, near: 1, far: 400}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.05; scene.add(sun, sun.target);
  const moon = new THREE.DirectionalLight('#8fa8e0', 0); moon.position.set(80, 120, 60); scene.add(moon);
  // Sterne (nur nachts)
  const stars = (() => { const n = 1500, r = rng(8), P = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const a = r() * Math.PI * 2, e = 0.1 + r() * 1.3; P.set([Math.cos(a) * Math.cos(e) * 1400, Math.sin(e) * 1400, Math.sin(a) * Math.cos(e) * 1400], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); const p = new THREE.Points(g, new THREE.PointsMaterial({color: '#dfe6ff', size: 1.4, sizeAttenuation: false, fog: false})); scene.add(p); return p; })();

  // Boden: Asphalt, Platz mit Pflaster
  const asT = asphaltTex(); asT.repeat.set(40, 40);
  mesh(new THREE.PlaneGeometry(1800, 1800), new THREE.MeshStandardMaterial({map: asT, roughness: 0.95}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const plT = tileTex('#a39a8c', '#958d80'); plT.repeat.set(14, 24);
  mesh(new THREE.BoxGeometry(84, 0.12, 146), new THREE.MeshStandardMaterial({map: plT, roughness: 0.85}), 0, 0.06, 31, scene).castShadow = false;
  // Risse im Pflaster nach dem Aufschlag
  const crackT = canvasTex(1024, 1024, g => { g.clearRect(0, 0, 1024, 1024); const r = rng(5); g.strokeStyle = 'rgba(20,16,12,0.95)';
    for (let i = 0; i < 46; i++) { let a = r() * Math.PI * 2, x = 512 + Math.cos(a) * 250, y = 512 + Math.sin(a) * 250; g.lineWidth = 3 + r() * 6; g.beginPath(); g.moveTo(x, y);
      for (let k = 0; k < 10; k++) { a += (r() - 0.5) * 0.6; const st = 15 + r() * 30; x += Math.cos(a) * st; y += Math.sin(a) * st; g.lineTo(x, y); g.lineWidth *= 0.9; } g.stroke(); } });
  const crackM = new THREE.MeshBasicMaterial({map: crackT, transparent: true, opacity: 0, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2});
  const crack = mesh(new THREE.PlaneGeometry(80, 80), crackM, 0, 0.125, 0, scene); crack.rotation.x = -Math.PI / 2; crack.castShadow = false; crack.receiveShadow = false;
  // Häuserblöcke rund um den Platz
  const facCols = ['#b6a08a', '#9fa7b0', '#c8b49c', '#8e8a96', '#a58f7c', '#d1c3ad'];
  const ftex = facCols.map((c, i) => darkFacade(c, 60 + i, 8, 5)); const roofM = mat('#4a4642', {roughness: 0.95});
  const swT = tileTex('#a7a49c', '#9c998f'); swT.repeat.set(8, 8); const swM = new THREE.MeshStandardMaterial({map: swT, roughness: 0.9});
  { const r = rng(91);
    for (let bx = -6; bx <= 6; bx++) for (let bz = -6; bz <= 6; bz++) {
      if (bx === 0 && (bz === 0 || bz === 1)) continue; // Platz und offene Fläche davor
      const cx = bx * 62, cz = bz * 62, w = 44;
      mesh(new THREE.BoxGeometry(w + 4, 0.15, w + 4), swM, cx, 0.075, cz, scene).castShadow = false;
      for (let i = 0; i < 2; i++) for (let k = 0; k < 2; k++) {
        const hx = cx - w / 4 + i * w / 2, hz = cz - w / 4 + k * w / 2, h = 14 + r() * (Math.abs(bx) + Math.abs(bz) < 3 ? 22 : 40);
        const fm = new THREE.MeshStandardMaterial({map: ftex[Math.floor(r() * 6)], roughness: 0.9});
        mesh(new THREE.BoxGeometry(w / 2 - 0.6, h, w / 2 - 0.6), [fm, fm, roofM, roofM, fm, fm], hx, h / 2 + 0.15, hz, scene);
      }
    } }
  // Parkende Autos und Laternen (ohne Strom)
  const poleM = mat('#2b2f33', {metalness: 0.6});
  { const r = rng(14); for (let i = 0; i < 40; i++) { const c = makeCar(i + 2); const side = i % 4; const d = 46 + (r() - 0.5) * 4, along = -150 + (i * 37) % 300;
      if (side === 0) c.position.set(along, 0, d); else if (side === 1) c.position.set(along, 0, -d); else if (side === 2) c.position.set(d, 0, along); else c.position.set(-d, 0, along);
      c.rotation.y = side < 2 ? Math.PI / 2 : 0; if (Math.abs(c.position.x) < 44 && c.position.z > -44 && c.position.z < 104) continue; scene.add(c); } }
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; const x = Math.cos(a) * 40, z = Math.sin(a) * 40; mesh(new THREE.CylinderGeometry(0.08, 0.1, 6, 8), poleM, x, 3, z, scene); mesh(new THREE.SphereGeometry(0.35, 10, 8), mat('#c9ccd1', {roughness: 0.3}), x, 6.1, z, scene); }

  // Der Würfel
  const cube = mesh(new THREE.BoxGeometry(S, S, S), GOLD, 0, -100, 0, scene);
  // Glitzer, der sich zum Würfel zusammenzieht
  const glintTex = canvasTex(64, 64, g => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,250,220,1)'); gr.addColorStop(0.3, 'rgba(255,210,90,0.8)'); gr.addColorStop(1, 'rgba(255,170,40,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); });
  const NG = 2500, gP = new Float32Array(NG * 3), gSeed = []; { const r = rng(4); for (let i = 0; i < NG; i++) gSeed.push([r() - 0.5, r(), r() - 0.5, r() * Math.PI * 2, r()]); }
  const gGeo = new THREE.BufferGeometry(); gGeo.setAttribute('position', new THREE.BufferAttribute(gP, 3));
  const glit = new THREE.Points(gGeo, new THREE.PointsMaterial({size: 0.9, map: glintTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: '#ffd77a'})); glit.frustumCulled = false; scene.add(glit);

  // Menschen auf dem Platz (nah) und Massen (fern, Instanzen)
  const people = []; { const r = rng(33); for (let i = 0; i < 34; i++) { const p = makePerson(400 + i); const a = r() * Math.PI * 2, d = 17 + r() * 22;
      people.push({p, x: Math.cos(a) * d, z: Math.sin(a) * d, ry: r() * 6.28, d, a, sp: 0.8 + r() * 0.6, ph: r() * 10}); scene.add(p); } }
  const NC = 6000; const crowd = new THREE.InstancedMesh(new THREE.CapsuleGeometry(0.25, 0.9, 3, 6), new THREE.MeshBasicMaterial(), NC); crowd.castShadow = false;
  const cSeed = []; { const r = rng(55), c = new THREE.Color(); for (let i = 0; i < NC; i++) { // Straße (0..3), Startabstand, seitlich
      { const u = r(); cSeed.push([Math.floor(r() * 4), 30 + u * u * 540, (r() - 0.5) * 14, r()]); } c.setHSL(r(), 0.3, 0.035 + r() * 0.05); crowd.setColorAt(i, c); } }
  scene.add(crowd);
  const NT = Math.floor(NC / 10); const torches = new THREE.InstancedMesh(new THREE.SphereGeometry(0.11, 6, 5), new THREE.MeshBasicMaterial({color: '#ffb455'}), NT); torches.castShadow = false; scene.add(torches);
  // Feuertonnen
  const BARRELS = []; { const r = rng(71); for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2 + r() * 0.2, d = 24 + r() * 16; BARRELS.push(V3(Math.cos(a) * d, 0, Math.sin(a) * d)); } }
  BARRELS.forEach(b => mesh(new THREE.CylinderGeometry(0.4, 0.4, 0.9, 12), mat('#3a3028', {metalness: 0.5}), b.x, 0.45, b.z, scene));
  const fireL = BARRELS.filter((_, i) => i % 2 === 0).map(b => { const l = new THREE.PointLight('#ff8a3a', 0, 45, 1.6); l.position.set(b.x, 2.2, b.z); scene.add(l); return l; });
  const fire = particles(900, 'flame'); scene.add(fire);
  const smoke = particles(700, 'smoke'); scene.add(smoke);
  const dust = particles(900, 'smoke'); scene.add(dust);
  // ferne Brände in der Stadt (Luftbild)
  const FAR = [[-180, -240], [210, -120], [-260, 150], [120, 260], [300, 300], [-90, 330], [340, -280]];

  // Kamera, Handy (Schluss)
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 4000); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#1e2126'); const hands = makeHands('#d9a47e', '#2a2f38');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig); rig.position.set(0.0, -0.075, -0.3); rig.rotation.set(-0.12, 0.0, 0.02);
  phone.userData.scr.material.emissiveIntensity = 0; phone.userData.scr.material.color.set('#050608');
  { const g = phone.userData.screenC.getContext('2d'); g.fillStyle = '#030405'; g.fillRect(0, 0, 600, 1300); phone.userData.tex.needsUpdate = true; }

  const m4 = new THREE.Matrix4(), q0 = new THREE.Quaternion();
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id, night = id !== 'cube_drop';
    skyDusk.visible = !night; skyNight.visible = night; stars.visible = night;
    scene.fog.color.set(night ? '#0a0f1a' : '#c99a7a'); scene.fog.near = night ? 60 : 120; scene.fog.far = night ? (id === 'aerial' ? 900 : 420) : 900;
    sun.intensity = night ? 0 : 2.4; moon.intensity = night ? 0.35 : 0; hemi.intensity = night ? 0.14 : 0.9; hemi.color.set(night ? '#6a80b0' : '#ffd0b0');
    scene.environmentIntensity = night ? 0.12 : 0.6;
    // Würfel: erscheint über dem Platz und fällt
    const tA = CUBE_LAND - 1.25;
    let cy = -100; if (T >= tA) { const ft = Math.min(T, CUBE_LAND) - tA; cy = S / 2 + 0.12 + 0.5 * 9.81 * (1.25 * 1.25 - (1.25 - (1.25 - ft)) ** 2 * 0) - 0.5 * 9.81 * ft * ft + 0.5 * 9.81 * 1.25 * 1.25 * 0; cy = S / 2 + 0.12 + 7.66 - 0.5 * 9.81 * ft * ft; }
    if (T >= CUBE_LAND) cy = S / 2 + 0.12 - 0.35 * smooth(CUBE_LAND, CUBE_LAND + 0.3, T);
    cube.position.y = cy;
    const shake = T > CUBE_LAND && T < CUBE_LAND + 1.2 ? (1 - (T - CUBE_LAND) / 1.2) : 0;
    crackM.opacity = smooth(CUBE_LAND, CUBE_LAND + 0.25, T);
    // Glitzer zieht sich zusammen
    { const k = clamp((T - (RETURN - 0.6)) / (tA - (RETURN - 0.6) + 0.15)); glit.visible = T > RETURN - 0.6 && T < tA + 0.25;
      if (glit.visible) { for (let i = 0; i < NG; i++) { const s = gSeed[i], R = lerp(60 + s[4] * 40, 2, easeIn(k)), a = s[3] + k * 4;
        gP[i * 3] = Math.cos(a) * R * (0.4 + s[4]) + s[0] * S * k; gP[i * 3 + 1] = lerp(s[1] * 40, S / 2 + 7.66 + s[1] * 6, k); gP[i * 3 + 2] = Math.sin(a) * R * (0.4 + s[4]) + s[2] * S * k; }
        gGeo.attributes.position.needsUpdate = true; glit.material.opacity = Math.sin(clamp(k) * Math.PI * 0.95 + 0.1); } }
    // Staub beim Aufschlag
    updateParticles(dust, T > CUBE_LAND ? [{type: 'smoke', pos: V3(0, 1.5, 0), r: 30, t0: CUBE_LAND, t1: CUBE_LAND + 1.0, size: 9, rise: 1.2, col: [0.62, 0.54, 0.44], alpha: 0.45, share: 1}] : [], T, V3(1.5, 0, 0.8));
    // Feuer nachts
    const fl = flicker(T, 3);
    fireL.forEach((l, i) => l.intensity = night ? 70 * flicker(T, i) : 0);
    updateParticles(fire, night ? BARRELS.map(b => ({type: 'flame', pos: V3(b.x, 1.0, b.z), r: 0.35, t0: 0, size: 1.3, rise: 2.0, power: 1, share: 1}))
      .concat(id === 'aerial' ? FAR.map(([x, z]) => ({type: 'flame', pos: V3(x, 8, z), r: 9, t0: 0, size: 18, rise: 8, power: 1, share: 3})) : []) : [], T);
    updateParticles(smoke, night ? (id === 'aerial' ? FAR.map(([x, z]) => ({type: 'smoke', pos: V3(x, 14, z), r: 8, t0: -20, size: 30, rise: 9, col: [0.08, 0.07, 0.07], alpha: 0.7, share: 1})) : []) : [], T, V3(1.5, 0, 0.5));
    // Menschen in der Nähe
    people.forEach((o, i) => { const p = o.p;
      if (!night) { // bummeln, nach dem Aufschlag fallen die Nahen um, dann schauen alle hoch und kommen näher
        const walkT = T < CUBE_LAND ? T : CUBE_LAND; let x = o.x + Math.cos(o.ry) * o.sp * walkT * 0.0, z = o.z;
        const fall = o.d < 26 ? smooth(CUBE_LAND + 0.05, CUBE_LAND + 0.7, T) * (1 - smooth(CUBE_LAND + 3.5, CUBE_LAND + 4.5, T)) : 0;
        const appr = smooth(CUBE_LAND + 4.5, 58, T); const dd = lerp(o.d, Math.max(13.5, o.d - 6), appr);
        x = Math.cos(o.a) * dd; z = Math.sin(o.a) * dd;
        p.position.set(x, 0.12, z); const face = Math.atan2(-x, -z); p.rotation.set(0, T < CUBE_LAND ? o.ry + T * 0.2 : face, 0);
        posePerson(p, {walk: T < CUBE_LAND ? T * 4 + o.ph : (appr > 0 && appr < 1 ? T * 4 + o.ph : 0), walkAmp: T < CUBE_LAND ? 1 : appr > 0 && appr < 1 ? 0.6 : 0, fall, fallDir: -1});
        if (T > CUBE_LAND && fall < 0.01) { p.userData.head.rotation.x = -0.5; if (i % 3 === 0) { p.userData.armR.rotation.x = -2.5 * smooth(CUBE_LAND + 1, CUBE_LAND + 2, T); } }
        if (T < CUBE_LAND) { const wx = o.x + Math.sin(o.ry) * 0.6 * (T - 48) * o.sp, wz = o.z + Math.cos(o.ry) * 0.6 * (T - 48) * o.sp; p.position.set(wx, 0.12, wz); p.rotation.y = o.ry; }
      } else { // nachts: dicht gedrängt am Würfel, manche klettern hinauf
        const k = (i * 0.618) % 1, a = o.a, dd = 12.2 + k * 9;
        let x = Math.cos(a) * dd, z = Math.sin(a) * dd; const lim = S / 2 + 0.5; if (Math.abs(x) < lim && Math.abs(z) < lim) { const s = lim / Math.max(Math.abs(x), Math.abs(z)); x *= s; z *= s; }
        p.position.set(x, 0.12, z); p.rotation.set(0, Math.atan2(-x, -z), 0);
        posePerson(p, {walk: T * 3 + o.ph, walkAmp: 0.25, armsUp: i % 4 === 0 ? 0.7 + 0.2 * Math.sin(T * 5 + i) : 0}); p.userData.head.rotation.x = -0.45;
        if (i % 7 === 0) { p.position.set(lerp(-S / 2 + 2, S / 2 - 2, k), S + 0.12, lerp(-S / 2 + 2, S / 2 - 2, (k * 7.3) % 1)); posePerson(p, {armsUp: 0.9}); }
      } });
    // Menschenmassen strömen über die vier Straßen zum Platz
    crowd.visible = night;
    if (night) { for (let i = 0; i < NC; i++) { const s = cSeed[i]; const flow = (T - 44) * 1.6;
        const along = Math.max(26 + s[3] * 18, s[1] - flow * (4 + s[3] * 3)); const lat = s[2];
        let x, z; if (s[0] === 0) { x = 31 + lat; z = along; } else if (s[0] === 1) { x = -31 + lat; z = -along; } else if (s[0] === 2) { x = along; z = 31 + lat; } else { x = -along; z = -31 + lat; }
        if (along < 44) { const a = Math.atan2(z, x) + (s[3] - 0.5) * 3.2; const r = 23 + ((s[3] * 7.31) % 1) * 12; x = Math.cos(a) * r; z = Math.sin(a) * r; }
        const hide = id === 'final' && Math.hypot(x - 2, z - 40) < 5;
        m4.compose(V3(x, 0.8, z), q0, hide ? V3(0.001, 0.001, 0.001) : V3(1, 1, 1)); crowd.setMatrixAt(i, m4);
        if (i % 10 === 0 && i / 10 < NT) { const fl2 = (0.8 + 0.3 * Math.sin(T * 13 + i)) * (id === 'aerial' ? 3.5 : 1); m4.compose(V3(x + 0.2, 2.1, z), q0, V3(fl2, fl2 * 1.3, fl2)); torches.setMatrixAt(i / 10, m4); } }
      crowd.instanceMatrix.needsUpdate = true; torches.instanceMatrix.needsUpdate = true; }
    torches.visible = night;
    // Kamera
    rig.visible = id === 'final'; camera.fov = 50;
    const sh = V3(noise1(T * 25, 1), noise1(T * 25, 2), 0).multiplyScalar(0.25 * shake);
    if (id === 'cube_drop') {
      const k = smooth(CUBE_LAND + 1.5, 58, T);
      camera.fov = 55; camera.position.set(lerp(8, 40, k), lerp(2.0, 9, k), lerp(88, 78, k)).add(sh); camera.lookAt(0, lerp(15, 12, k), 0);
    } else if (id === 'cube_night') {
      const k = smooth(58, 68, T);
      camera.fov = 55; camera.position.set(lerp(-14, 6, k), lerp(1.7, 2.4, k), lerp(62, 54, k)); camera.lookAt(0, lerp(12, 14, k), 0);
    } else if (id === 'aerial') {
      const k = smooth(68, 80, T);
      camera.position.set(lerp(60, 120, k), lerp(60, 320, k), lerp(90, 300, k)); camera.lookAt(0, 8, 0);
    } else { // final: totes Handy, dahinter der Würfel
      camera.position.set(3 + noise1(T, 1) * 0.02, 1.65, 66 + noise1(T, 2) * 0.02); camera.lookAt(0, lerp(7, 11, smooth(80, 89, T)), 0);
    }
    camera.updateProjectionMatrix();
  }};
}
