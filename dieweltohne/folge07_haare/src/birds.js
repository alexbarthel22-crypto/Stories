// Abenddämmerung über einem Platz in der Altstadt. Ein riesiger Starenschwarm zieht seine Muster (Murmuration).
// Vögel hören und halten ihr Gleichgewicht ebenfalls mit Haarzellen: Der Schwarm zerfällt, die Vögel trudeln vom Himmel.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, skyDome, makePerson, posePerson, makeCar, tileTex, envMap} from './lib.js';
import {VANISH, RETURN, FLOCK_BREAK} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.25;
  scene.fog = new THREE.Fog('#c9876e', 80, 520);
  scene.add(skyDome('#2c3570', '#b5677a', '#ffb37a', 600));
  scene.add(new THREE.HemisphereLight('#f7c2a4', '#3a3040', 1.1));
  const sun = new THREE.DirectionalLight('#ffa060', 2.0); sun.position.set(-60, 18, -40); sun.target.position.set(0, 0, 0);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -30, right: 30, top: 30, bottom: -30, near: 1, far: 160}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.03;
  scene.add(sun, sun.target);
  // Platz
  const tt = tileTex('#a39a8f', '#958c82'); tt.repeat.set(30, 30);
  const ground = mesh(new THREE.PlaneGeometry(240, 240), new THREE.MeshStandardMaterial({map: tt, roughness: 0.85}), 0, 0, 0, scene); ground.rotation.x = -Math.PI / 2;
  // Häuser rund um den Platz (Altstadt, Giebel)
  const r = rng(17);
  const ring = (cx, cz, along, n, face) => { let o = -n / 2 * 7; for (let i = 0; i < n; i++) { const w = 6 + r() * 3, h = 12 + r() * 9; const col = ['#d8b48a', '#c98d6e', '#e2cfa8', '#b9a28a', '#d6a37c', '#c4b49a'][Math.floor(r() * 6)];
    const ft = facadeTex(col, Math.floor(r() * 99), Math.round(h / 3.2), 3); const x = along === 'x' ? cx + o + w / 2 : cx, z = along === 'x' ? cz : cz + o + w / 2;
    const b = mesh(new THREE.BoxGeometry(along === 'x' ? w - 0.15 : 9, h, along === 'x' ? 9 : w - 0.15), new THREE.MeshStandardMaterial({map: ft, roughness: 0.9}), x, h / 2, z, scene);
    const roof = mesh(new THREE.CylinderGeometry(0.01, (along === 'x' ? w : 9) * 0.6, 4, 4, 1), mat('#7a3a2a', {roughness: 0.8}), x, h + 2, z, scene); roof.rotation.y = Math.PI / 4; roof.scale.set(1, 1, along === 'x' ? 1.4 : 0.8);
    o += w; } };
  ring(0, -34, 'x', 10, 1); ring(-30, 0, 'z', 8, 1); ring(30, 0, 'z', 8, -1);
  // Kirchturm
  mesh(new THREE.BoxGeometry(7, 42, 7), new THREE.MeshStandardMaterial({map: facadeTex('#b8a88e', 7, 10, 2), roughness: 0.9}), -8, 21, -44, scene);
  mesh(new THREE.ConeGeometry(5.2, 18, 4), mat('#3f6a5a', {metalness: 0.4, roughness: 0.5}), -8, 51, -44, scene).rotation.y = Math.PI / 4;
  // Brunnen
  mesh(new THREE.CylinderGeometry(3.2, 3.4, 0.7, 32), mat('#bdb3a5'), 4, 0.35, -8, scene);
  mesh(new THREE.CylinderGeometry(0.4, 0.5, 2.6, 16), mat('#bdb3a5'), 4, 1.3, -8, scene);
  // Autos und Menschen auf dem Platz (alle schon benommen: sitzen, hocken)
  [[12, -18, 0.4, 2], [-14, -14, -0.3, 6], [18, 6, 1.4, 4]].forEach(([x, z, ry, s]) => { const c = makeCar(s); c.position.set(x, 0, z); c.rotation.y = ry; scene.add(c); });
  const people = [[-3, 6, 0.4], [2.5, 4, -0.5], [-6, -2, 1.2], [7, 1, -1.0], [0, -3, 2.5]].map(([x, z, ry], i) => { const p = makePerson(60 + i); p.position.set(x, 0, z); p.rotation.y = ry; scene.add(p); return p; });

  // Schwarm
  const N = 6500, rb = rng(5);
  const birds = [];
  for (let i = 0; i < N; i++) { const u = rb() * 2 - 1, ph = rb() * 6.283, rr = Math.cbrt(rb()); birds.push({u, ph, rr, fl: rb() * 6.28, tb: FLOCK_BREAK + rb() * 1.4, spin: (rb() - 0.5) * 18, sx: (rb() - 0.5) * 8, sz: (rb() - 0.3) * 9, flut: rb(), land: rb()}); }
  const bodyGeo = new THREE.SphereGeometry(0.09, 6, 4); bodyGeo.scale(0.7, 0.6, 1.6);
  const wingGeo = new THREE.BufferGeometry(); wingGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0, 0, 0.08, 0.34, 0, -0.02, 0, 0, -0.1]), 3)); wingGeo.computeVertexNormals();
  const bm = new THREE.MeshStandardMaterial({color: '#1a1714', roughness: 0.7, side: THREE.DoubleSide});
  const bodyI = new THREE.InstancedMesh(bodyGeo, bm, N), wL = new THREE.InstancedMesh(wingGeo, bm, N), wR = new THREE.InstancedMesh(wingGeo, bm, N);
  [bodyI, wL, wR].forEach(im => { im.frustumCulled = false; scene.add(im); });
  const M = new THREE.Matrix4(), B = new THREE.Matrix4(), L = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = V3(0, 0, 0), S = V3(1, 1, 1), up = V3(0, 1, 0);
  const flockPos = (b, T) => { // Murmuration: verformte, wandernde Wolke
    const c = V3(Math.sin(T * 0.21) * 22, 50 + Math.sin(T * 0.33) * 6, -30 + Math.cos(T * 0.17) * 10);
    const s = Math.sqrt(1 - b.u * b.u); let x = s * Math.cos(b.ph), y = b.u, z = s * Math.sin(b.ph);
    const R = 26 * b.rr; const w = Math.sin(T * 0.8 + x * 2.2) * 0.45 + Math.sin(T * 0.53 + z * 3.1) * 0.3;
    return V3(c.x + x * R * (1.6 + w), c.y + y * R * 0.5 * (1 + 0.6 * Math.sin(T * 0.7 + x * 3)) + w * 6, c.z + z * R * (1 - w * 0.5));
  };
  const camera = new THREE.PerspectiveCamera(55, 1080 / 1920, 0.1, 1200);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, gone = T >= VANISH && T < RETURN;
    people.forEach((p, i) => { posePerson(p, {}); const u = p.userData; u.hair.visible = !gone;
      p.position.y = -0.5; u.legL.rotation.x = -1.4; u.legR.rotation.x = -1.35; u.legL.userData.knee.rotation.x = 1.6; u.legR.userData.knee.rotation.x = 1.5;
      u.head.rotation.x = -0.5 + smooth(FLOCK_BREAK + 1, FLOCK_BREAK + 3, T) * 0.3; u.torso.rotation.z = Math.sin(T * 0.8 + i) * 0.15;
      u.armL.rotation.set(-0.3, 0, -0.6); u.armR.rotation.set(T > FLOCK_BREAK + 1.5 + i * 0.3 ? -2.6 : -0.3, 0, 0.6); });
    for (let i = 0; i < N; i++) {
      const b = birds[i]; let p, yaw, pitch = 0, roll = 0, flap;
      const p0 = flockPos(b, T), p1 = flockPos(b, T + 0.05); const v = p1.clone().sub(p0);
      if (T < b.tb) { p = p0; yaw = Math.atan2(v.x, v.z); pitch = -Math.atan2(v.y, Math.hypot(v.x, v.z)); flap = Math.sin(T * 26 + b.fl) * 0.7; }
      else { // Absturz: Anfangsgeschwindigkeit des Schwarms, dann Fallen mit Luftwiderstand, Trudeln
        const d = T - b.tb; const vt = 14; const fallY = vt * (d - (vt / 9.8) * (1 - Math.exp(-9.8 * d / vt)));
        const pb = flockPos(b, b.tb), vb = flockPos(b, b.tb + 0.05).sub(pb).multiplyScalar(20);
        p = V3(pb.x + vb.x * (1 - Math.exp(-d * 1.2)) / 1.2 + b.sx * d, pb.y - fallY, pb.z + vb.z * (1 - Math.exp(-d * 1.2)) / 1.2 + b.sz * d);
        yaw = b.ph + d * b.spin; pitch = d * b.spin * 0.7; roll = d * b.spin * 0.4; flap = b.flut < 0.4 ? Math.sin(T * 30 + b.fl) * 0.9 : 0.9;
        if (p.y < 0.06) { p.y = 0.06; pitch = 0; roll = 1.4 * (b.land < 0.5 ? 1 : -1); flap = 0.2; yaw = b.ph; } // liegt auf dem Boden
      }
      B.compose(P.copy(p), Q.setFromEuler(E.set(pitch, yaw, roll, 'YXZ')), S.set(1.5, 1.5, 1.5));
      bodyI.setMatrixAt(i, B);
      L.makeRotationZ(flap); wL.setMatrixAt(i, M.copy(B).multiply(L));
      L.makeRotationZ(Math.PI - flap); wR.setMatrixAt(i, M.copy(B).multiply(L));
    }
    [bodyI, wL, wR].forEach(im => im.instanceMatrix.needsUpdate = true);
    // Kamera: schaut hoch zum Schwarm, folgt dann dem Fall bis auf den Platz
    camera.fov = 55;
    const dn = smooth(FLOCK_BREAK + 0.8, shot.t1 - 0.6, T);
    camera.position.set(1.5 + noise1(T * 1.2, 1) * 0.05, 1.7 + noise1(T, 2) * 0.03, 16 - t * 0.2);
    camera.lookAt(lerp(Math.sin(T * 0.21) * 18, 0, dn), lerp(46, 0.5, dn), lerp(-28, -12, dn));
    camera.updateProjectionMatrix();
  }};
}
