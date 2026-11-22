// Stilisierter Löwe (Blick in +z): Rumpf, Kopf mit Mähne, Unterkiefer, vier Beine mit Knie, Schwanz mit Quaste.
// poseLion(l, {gait, run, leap, roar, crouch, lie, eat, look, tailWag})
import {THREE, mat, mesh, clamp, lerp} from './lib.js';

export function makeLion(seed = 1, o = {}) {
  const fur = mat(o.fur || '#c89a5a', {roughness: 0.95}), light = mat(o.light || '#e2c18c', {roughness: 0.95});
  const mane = mat(o.mane || '#7a4a22', {roughness: 1}), dark = mat('#2a1c14', {roughness: 0.8}), nose = mat('#3a2620', {roughness: 0.5});
  const male = o.male !== false, sc = o.scale || 1;
  const root = new THREE.Group();
  const body = new THREE.Group(); body.scale.setScalar(sc); root.add(body);
  const hips = new THREE.Group(); hips.position.set(0, 0.95, -0.55); body.add(hips);      // Becken (Drehpunkt hinten)
  const chest = new THREE.Group(); chest.position.set(0, 0.98, 0.5); body.add(chest);      // Brust (Drehpunkt vorn)
  const trunk = mesh(new THREE.CapsuleGeometry(0.33, 1.0, 6, 14), fur, 0, 0, 0, body); trunk.rotation.x = Math.PI / 2; trunk.position.set(0, 0.97, 0); trunk.scale.set(1, 1, 0.92);
  mesh(new THREE.SphereGeometry(0.31, 14, 10), light, 0, 0.82, 0.05, body).scale.set(0.95, 0.6, 1.7);   // heller Bauch
  mesh(new THREE.SphereGeometry(0.36, 14, 10), fur, 0, 0.02, 0, chest).scale.set(1, 1.05, 1);           // Schulterpartie
  mesh(new THREE.SphereGeometry(0.34, 14, 10), fur, 0, 0.02, 0, hips).scale.set(1, 1, 1.05);
  // Kopf
  const neck = new THREE.Group(); neck.position.set(0, 0.18, 0.28); chest.add(neck);
  const head = new THREE.Group(); head.position.set(0, 0.16, 0.28); neck.add(head);
  if (male) { const mn = mesh(new THREE.IcosahedronGeometry(0.5, 2), mane, 0, -0.02, -0.12, head); mn.scale.set(1.0, 1.05, 0.8);
    const p = mn.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const v = new THREE.Vector3().fromBufferAttribute(p, i); const k = 1 + 0.12 * Math.sin(v.x * 23 + v.y * 17) * Math.cos(v.z * 19); p.setXYZ(i, v.x * k, v.y * k, v.z * k); } mn.geometry.computeVertexNormals(); }
  else { mesh(new THREE.SphereGeometry(0.2, 10, 8), fur, 0, 0, -0.08, head).scale.set(1, 1, 1.2); }
  mesh(new THREE.SphereGeometry(0.24, 16, 12), fur, 0, 0.02, 0.02, head).scale.set(0.95, 0.95, 1.05);
  const muzzle = mesh(new THREE.SphereGeometry(0.13, 12, 10), light, 0, -0.06, 0.2, head); muzzle.scale.set(1.05, 0.8, 1.0);
  mesh(new THREE.SphereGeometry(0.045, 8, 6), nose, 0, -0.01, 0.31, head).scale.set(1.3, 0.8, 0.8);
  for (const s of [-1, 1]) { mesh(new THREE.SphereGeometry(0.03, 8, 6), dark, s * 0.09, 0.08, 0.2, head); // Augen
    const ear = mesh(new THREE.SphereGeometry(0.065, 8, 6), fur, s * 0.15, 0.2, -0.02, head); ear.scale.set(1, 1, 0.5); }
  const jaw = new THREE.Group(); jaw.position.set(0, -0.1, 0.08); head.add(jaw);
  mesh(new THREE.SphereGeometry(0.1, 10, 8), light, 0, -0.02, 0.12, jaw).scale.set(1, 0.55, 1.1);
  const mouth = mesh(new THREE.SphereGeometry(0.085, 10, 8), mat('#5a1c1c', {roughness: 0.6}), 0, -0.07, 0.17, head); mouth.scale.set(1, 0.3, 0.9);
  for (const s of [-1, 1]) mesh(new THREE.ConeGeometry(0.012, 0.05, 6), mat('#f4efe2'), s * 0.05, -0.09, 0.27, head).rotation.x = Math.PI;
  // Beine
  const leg = (parent, x, z, front) => {
    const up = new THREE.Group(); up.position.set(x, -0.05, z); parent.add(up);
    mesh(new THREE.CapsuleGeometry(0.11, 0.32, 4, 10), fur, 0, -0.22, 0, up);
    const knee = new THREE.Group(); knee.position.y = -0.46; up.add(knee);
    mesh(new THREE.CapsuleGeometry(0.075, 0.3, 4, 10), fur, 0, -0.2, 0, knee);
    const paw = mesh(new THREE.SphereGeometry(0.09, 10, 8), light, 0, -0.42, 0.04, knee); paw.scale.set(1, 0.6, 1.3);
    up.userData = {knee, front}; return up;
  };
  const fl = leg(chest, -0.2, 0.02, true), fr = leg(chest, 0.2, 0.02, true), bl = leg(hips, -0.2, -0.05, false), br = leg(hips, 0.2, -0.05, false);
  // Schwanz
  const tail = new THREE.Group(); tail.position.set(0, 0.12, -0.32); hips.add(tail);
  const segs = []; let par = tail;
  for (let i = 0; i < 5; i++) { const s = new THREE.Group(); s.position.z = i ? -0.17 : 0; par.add(s); mesh(new THREE.CapsuleGeometry(0.035, 0.13, 3, 6), fur, 0, 0, -0.08, s).rotation.x = Math.PI / 2; segs.push(s); par = s; }
  mesh(new THREE.SphereGeometry(0.07, 8, 6), dark, 0, 0, -0.2, par).scale.set(1, 1, 1.4);
  root.userData = {body, hips, chest, neck, head, jaw, legs: [fl, fr, bl, br], tail, segs, sc};
  root.traverse(m => { if (m.isMesh) { m.castShadow = true; m.receiveShadow = false; } });
  return root;
}

// gait: Phase (Radiant), run: 0 = Schritt, 1 = Galopp; leap 0..1 (Sprung), roar 0..1, crouch 0..1, lie 0..1, eat 0..1, look (Kopf drehen)
export function poseLion(l, {gait = 0, walk = 0, run = 0, leap = 0, roar = 0, crouch = 0, lie = 0, eat = 0, look = 0, lookUp = 0, tailWag = 0, t = 0} = {}) {
  const u = l.userData, [fl, fr, bl, br] = u.legs;
  const amp = walk * lerp(0.42, 0.85, run);
  const ph = [0, Math.PI * lerp(1, 0.25, run), Math.PI * lerp(0.5, 0.9, run) + Math.PI, Math.PI * lerp(1.5, 1.15, run) + Math.PI];
  u.legs.forEach((lg, i) => { const s = Math.sin(gait + ph[i]); lg.rotation.x = s * amp; lg.userData.knee.rotation.x = (lg.userData.front ? -1 : 1) * Math.max(0, Math.cos(gait + ph[i])) * amp * 1.1; lg.rotation.z = 0; });
  u.body.position.set(0, Math.abs(Math.sin(gait)) * 0.06 * walk * (0.4 + run), 0); u.body.rotation.set(Math.sin(gait) * 0.08 * run * walk, 0, 0);
  u.chest.position.y = 0.98; u.hips.position.y = 0.95; u.chest.rotation.x = 0; u.hips.rotation.x = 0;
  u.neck.rotation.set(0, look * 0.7, 0); u.head.rotation.set(-lookUp * 0.5, look * 0.4, 0);
  // Ducken (Lauern) / Hinlegen
  const c = clamp(crouch + lie * 0.6);
  if (c > 0) { u.body.position.y -= c * 0.38; u.legs.forEach(lg => { lg.rotation.x += lg.userData.front ? -0.5 * c : 0.7 * c; lg.userData.knee.rotation.x += lg.userData.front ? 1.1 * c : -1.3 * c; }); u.neck.rotation.x = 0.25 * crouch; }
  if (lie > 0) { u.body.position.y -= lie * 0.22; u.legs.forEach(lg => { if (lg.userData.front) { lg.rotation.x = lerp(lg.rotation.x, -1.35, lie); lg.userData.knee.rotation.x = lerp(lg.userData.knee.rotation.x, 0.1, lie); } else { lg.rotation.x = lerp(lg.rotation.x, 1.45, lie); lg.userData.knee.rotation.x = lerp(lg.userData.knee.rotation.x, -1.6, lie); } }); }
  if (eat > 0) { u.neck.rotation.x = lerp(u.neck.rotation.x, 0.75, eat); u.head.rotation.x = lerp(u.head.rotation.x, 0.35 + 0.12 * Math.sin(t * 6), eat); }
  // Sprung: Hinterbeine strecken, Vorderbeine nach vorn, Körper kippt
  if (leap > 0) { const k = Math.sin(clamp(leap) * Math.PI);
    u.body.rotation.x = lerp(-0.45, 0.35, clamp(leap)) * k; fl.rotation.x = fr.rotation.x = -1.2 * k; fl.userData.knee.rotation.x = fr.userData.knee.rotation.x = -0.3 * k;
    bl.rotation.x = br.rotation.x = 1.0 * k; bl.userData.knee.rotation.x = br.userData.knee.rotation.x = 0.2 * k; }
  // Brüllen
  u.jaw.rotation.x = 0.55 * roar; u.head.rotation.x -= 0.35 * roar;
  // Schwanz
  u.segs.forEach((s, i) => { s.rotation.x = (i === 0 ? -0.9 : 0.25) + 0.05 * Math.sin(t * 2 + i); s.rotation.y = Math.sin(t * (2 + tailWag * 5) - i * 0.6) * (0.12 + tailWag * 0.3); });
}
