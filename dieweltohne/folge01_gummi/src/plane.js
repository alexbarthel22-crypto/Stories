// Landebahn in der Abenddämmerung: Flugzeug setzt ohne Reifen auf
import {particles, updateParticles, flicker} from './fx.js';
import {THREE, envMap, mat, mesh, rng, clamp, smooth, lerp, easeOut, noise1, canvasTex, asphaltTex, skyDome, sparkSystem, updateSparks} from './lib.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

function makePlane() {
  const p = new THREE.Group(); const body = new THREE.Group(); p.add(body);
  const white = mat('#f3f4f6', {roughness: 0.35, metalness: 0.2}), grey = mat('#9aa1aa', {metalness: 0.7, roughness: 0.35}), blue = mat('#1f4e8c', {roughness: 0.4});
  const f = mesh(new THREE.CapsuleGeometry(2, 30, 8, 24), white, 0, 0, 0, body); f.rotation.z = Math.PI / 2; f.scale.set(1, 1, 1);
  mesh(new THREE.CylinderGeometry(2.02, 2.02, 30, 24, 1, true, Math.PI * 0.6, Math.PI * 0.8), blue, 0, 0, 0, body).rotation.z = Math.PI / 2;
  // Fensterreihe
  for (let i = 0; i < 26; i++) for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(0.28, 0.38, 0.05), mat('#1b2430', {roughness: 0.1, metalness: 0.6}), -11 + i * 0.9, 0.7, s * 1.97, body);
  mesh(new THREE.BoxGeometry(1.2, 0.5, 2.6), mat('#141a22', {roughness: 0.05, metalness: 0.8}), 16.1, 0.9, 0, body);
  // Flügel
  const ws = new THREE.Shape(); ws.moveTo(0, 0); ws.lineTo(-5.5, 17); ws.lineTo(-7.2, 17); ws.lineTo(-6.5, 0);
  for (const s of [-1, 1]) { const g = new THREE.ExtrudeGeometry(ws, {depth: 0.35, bevelEnabled: false}); const w = mesh(g, grey, 3, -0.9, 0, body); w.rotation.x = s * Math.PI / 2; if (s < 0) w.position.y = -0.55;
    const eng = mesh(new THREE.CylinderGeometry(1.0, 0.85, 4.2, 20), white, 1.0, -2.0, s * 6.5, body); eng.rotation.z = Math.PI / 2;
    mesh(new THREE.CircleGeometry(0.85, 20), mat('#222', {metalness: 0.8}), 3.12, -2.0, s * 6.5, body).rotation.y = Math.PI / 2; }
  // Leitwerk
  const ts = new THREE.Shape(); ts.moveTo(0, 0); ts.lineTo(-4, 7); ts.lineTo(-6, 7); ts.lineTo(-5.5, 0);
  const tail = mesh(new THREE.ExtrudeGeometry(ts, {depth: 0.3, bevelEnabled: false}), blue, -11, 1.4, -0.15, body);
  const hs = new THREE.Shape(); hs.moveTo(0, 0); hs.lineTo(-2.5, 6); hs.lineTo(-3.6, 6); hs.lineTo(-3.8, 0);
  for (const s of [-1, 1]) { const h = mesh(new THREE.ExtrudeGeometry(hs, {depth: 0.2, bevelEnabled: false}), grey, -12.5, 0.4, 0, body); h.rotation.x = s * Math.PI / 2; }
  // Fahrwerk: Felgen + Reifen (Reifen sind beim Anflug schon weg)
  const gear = [];
  const tireM = mat('#121212', {roughness: 0.9}), rimM = mat('#cfd3d8', {metalness: 0.95, roughness: 0.2});
  const strutM = mat('#b9bec5', {metalness: 0.9, roughness: 0.3});
  for (const [gx, gz, n] of [[1.5, -2.6, 4], [1.5, 2.6, 4], [13.5, 0, 2]]) {
    mesh(new THREE.CylinderGeometry(0.16, 0.16, 2.4, 10), strutM, gx, -2.9, gz, body);
    for (let k = 0; k < n; k++) {
      const wx = gx + (n === 4 ? (k < 2 ? -0.6 : 0.6) : 0), wz = gz + (k % 2 ? 0.45 : -0.45);
      const w = new THREE.Group(); w.position.set(wx, -4.1, wz); body.add(w);
      mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.34, 20), rimM, 0, 0, 0, w).rotation.x = Math.PI / 2;
      const tire = mesh(new THREE.TorusGeometry(0.55, 0.2, 10, 24), tireM, 0, 0, 0, w); tire.scale.z = 1.4;
      gear.push({w, tire, wx, wz});
    }
  }
  p.userData = {body, gear};
  return p;
}

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.fog = new THREE.Fog('#c98e7a', 80, 700);
  scene.add(skyDome('#3c4a72', '#c77b67', '#f2b48a', 900));
  scene.add(new THREE.HemisphereLight('#f6c4a4', '#3d3a3a', 1.3));
  const sun = new THREE.DirectionalLight('#ffc89a', 1.8); sun.position.set(-200, 60, -150); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -60, right: 60, top: 60, bottom: -60, far: 600}); scene.add(sun); scene.add(sun.target);
  // Gras + Landebahn
  const grass = mesh(new THREE.PlaneGeometry(3000, 3000), mat('#5f6b3e', {roughness: 1}), 0, -0.02, 0, scene); grass.rotation.x = -Math.PI / 2;
  const asp = asphaltTex(); asp.repeat.set(60, 3);
  const rw = mesh(new THREE.PlaneGeometry(2400, 45), new THREE.MeshStandardMaterial({map: asp, roughness: 0.6, color: '#8a8a8a'}), 0, 0, 0, scene); rw.rotation.x = -Math.PI / 2;
  for (let x = -1200; x < 1200; x += 30) { const l = mesh(new THREE.PlaneGeometry(18, 0.9), mat('#eeeeea'), x, 0.01, 0, scene); l.rotation.x = -Math.PI / 2; }
  for (const z of [-21, 21]) { const l = mesh(new THREE.PlaneGeometry(2400, 0.8), mat('#eeeeea'), 0, 0.01, z, scene); l.rotation.x = -Math.PI / 2; }
  for (let i = 0; i < 6; i++) for (const s of [-1, 1]) { const l = mesh(new THREE.PlaneGeometry(40, 3), mat('#eeeeea'), -60 + i * 8 * 0, 0.01, s * (5 + i * 2.6), scene); l.rotation.x = -Math.PI / 2; l.position.x = -40; }
  const edge = mat('#fff3c4', {emissive: '#ffe08a', emissiveIntensity: 3});
  for (let x = -1200; x < 1200; x += 30) for (const z of [-24, 24]) mesh(new THREE.SphereGeometry(0.12, 8, 6), edge, x, 0.2, z, scene);
  // Tower und Hangars in der Ferne
  mesh(new THREE.CylinderGeometry(3, 4, 40, 10), mat('#9a9590'), -120, 20, -260, scene);
  mesh(new THREE.CylinderGeometry(9, 6, 7, 10), mat('#2a3138', {metalness: 0.6, roughness: 0.2}), -120, 43, -260, scene);
  for (let i = 0; i < 4; i++) mesh(new THREE.BoxGeometry(60, 18, 40), mat('#b8b6b0'), 60 + i * 75, 9, -230, scene);
  const plane = makePlane(); scene.add(plane);
  const sparks = sparkSystem(3500, 0.35); scene.add(sparks);
  const smokeM = new THREE.MeshBasicMaterial({color: '#bfb6ad', transparent: true, opacity: 0.0, depthWrite: false});
  const smoke = []; for (let i = 0; i < 40; i++) { const s = mesh(new THREE.SphereGeometry(1, 10, 8), smokeM.clone(), 0, 0, 0, scene); s.castShadow = false; smoke.push(s); }
  const camera = new THREE.PerspectiveCamera(45, 1080 / 1920, 0.1, 3000);

  const fire = particles(2400, 'flame'); scene.add(fire);
  const smokeP = particles(1200, 'smoke'); scene.add(smokeP);
  const fl = new THREE.PointLight('#ff7a2a', 0, 120, 1.5); scene.add(fl);
  smoke.forEach(s => s.visible = false);

  // Flugbahn: Aufsetzen auf Felgen bei td, Fahrwerk bricht bei tc, Rumpf schleift
  const td = 1.9, tcol = 3.3, v0 = 26, dec = 3.0;
  const px = t => t < td ? -60 + v0 * t : -60 + v0 * td + v0 * (t - td) - 0.5 * dec * (t - td) ** 2;
  const groundY = 4.1 + 0.42, bellyY = 3.05; // nach dem Einknicken liegen die Triebwerke auf
  const py = t => {
    if (t < td) return groundY + Math.pow((td - t) / td, 1.6) * 12;
    if (t < tcol) return groundY + Math.max(0, Math.sin((t - td) * 5) * Math.exp(-(t - td) * 2.5) * 0.5);
    const k = clamp((t - tcol) / 0.35); return lerp(groundY, bellyY, k * k) + (k >= 1 ? Math.sin((t - tcol) * 14) * Math.exp(-(t - tcol - 0.35) * 5) * 0.12 : 0);
  };
  const V = new THREE.Vector3();

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    const x = px(t);
    plane.position.set(x, py(t), t > tcol ? -Math.pow(t - tcol, 2) * 0.35 : 0);
    plane.rotation.set(t > tcol ? 0.06 * clamp((t - tcol) / 0.5) : 0, t > tcol ? -0.05 * Math.pow(clamp((t - tcol) / 3), 1.5) : 0, t < td ? 0.07 : (t < tcol ? 0.03 : 0.03 - 0.05 * clamp((t - tcol) / 0.4)));
    // Fahrwerk knickt ein
    const gk = clamp((t - tcol) / 0.3);
    plane.userData.gear.forEach(g => { g.tire.visible = false; g.w.position.y = -4.1 + gk * 2.2; g.w.rotation.z = gk * 1.2; });
    plane.updateMatrixWorld(true);
    const engs = [-1, 1].map(s => plane.localToWorld(V.set(1.0, -2.9, s * 6.5)).clone());
    const em = [];
    if (t >= td && t < tcol) plane.userData.gear.forEach((g, i) => { if (i % 2) return; em.push({pos: tb => V3(px(tb) + g.wx, 0.05, g.wz), dir: V3(-1.6, 0.35, (g.wz > 0 ? 0.25 : -0.25)), t0: td, t1: tcol + 0.2}); });
    if (t >= tcol) engs.forEach((e, i) => { em.push({pos: tb => V3(px(tb) + 1.0, 0.1, e.z), dir: V3(-1.8, 0.5, i ? 0.3 : -0.3), t0: tcol + 0.25, t1: 99}); em.push({pos: tb => V3(px(tb) - 2, 0.1, 0), dir: V3(-1.8, 0.4, 0), t0: tcol + 0.25, t1: 99}); });
    updateSparks(sparks, em, t, 6);
    const fx = [], sm = [];
    if (t >= tcol + 0.5) {
      engs.forEach((e, i) => { fx.push({type: 'flame', pos: e.clone().add(V3(-2.5, 0.3, 0)), r: 1.8 + (t - tcol) * 0.6, t0: tcol + 0.5 + i * 0.3, size: 2.6, rise: 3, share: 2}); sm.push({type: 'smoke', pos: e.clone().add(V3(-6, 2, 0)), r: 2, t0: tcol + 0.7, size: 9, rise: 4, share: 1}); });
      fx.push({type: 'burst', pos: engs[1].clone(), r: 7, t0: tcol + 1.9, size: 5, rise: 3, power: 1.3, share: 2});
    }
    updateParticles(fire, fx, t, V3(-6, 0, 0)); updateParticles(smokeP, sm, t, V3(-8, 0, 0));
    fl.position.copy(engs[1]).add(V3(0, 3, 0)); fl.intensity = t > tcol + 0.5 ? (t > tcol + 1.9 && t < tcol + 2.4 ? 4000 : 900) * flicker(T) : 0;
    if (t < 3.0) { // seitlich, tief an der Landebahn
      camera.position.set(-4 + t * 2.5, 1.6, 42); camera.lookAt(x * 0.6 + 4, 4.5, 0); camera.fov = 45;
    } else { // schräg vorn, Kamera schwenkt mit
      camera.position.set(x + 30 - (t - 3) * 3, 2.2, 30); camera.lookAt(x - 2, 2.5, 0); camera.fov = 44;
    }
    const sh = t > td && t < td + 0.8 ? 0.1 : (t > tcol && t < tcol + 1.5 ? 0.25 * (1 - (t - tcol) / 1.5) : 0.02);
    camera.position.x += noise1(T * 6, 1) * sh; camera.position.y += noise1(T * 6, 3) * sh;
    fl.visible = fl.intensity > 0; camera.updateProjectionMatrix();
  }};
}
