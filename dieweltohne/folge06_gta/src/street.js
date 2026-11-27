// Straße vor dem Haus, nachts: Er geht seit Release zum ersten Mal raus – direkt auf die Fahrbahn. Ein Auto macht eine Vollbremsung.
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {lerp, smooth, clamp, rng, noise1, canvasTex, envMap, easeOut} from './lib.js';
import {concrete, plaster, bumpToNormal, wrap} from './tex.js';
import {makeHuman} from './mh.js';
import {stand, mouth} from './poses.js';
import {makeCar2} from './car.js';
import {phone} from './props.js';
import {BRAKE, STOP} from './timeline.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const std = (c, o = {}) => new THREE.MeshStandardMaterial({color: c, roughness: 0.8, ...o});
function box(w, h, d, m, x, y, z, p, r = 0) { const o = new THREE.Mesh(r ? new RoundedBoxGeometry(w, h, d, 2, r) : new THREE.BoxGeometry(w, h, d), m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; p.add(o); return o; }

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#05070c');
  scene.fog = new THREE.FogExp2('#0a0e18', 0.035);
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.03;
  const camera = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.05, 200);
  const R = new THREE.Group(); scene.add(R);
  // Fahrbahn entlang x (z 0..7), Gehweg z -3..0, Hausfront bei z = -3
  const asp = concrete('#2c2d30', 41, 1.3);
  const road = new THREE.Mesh(new THREE.PlaneGeometry(120, 7.4), new THREE.MeshStandardMaterial({map: asp.map, normalMap: asp.normalMap, roughness: 0.55, metalness: 0.05})); road.material.map.repeat.set(24, 1.5); road.material.normalMap.repeat.set(60, 4);
  road.rotation.x = -Math.PI / 2; road.position.set(0, 0, 3.7); road.receiveShadow = true; R.add(road);
  // nasse Flecken (Pfützen) als glatte Bereiche
  const wet = canvasTex(512, 128, g => { const q = rng(5); g.fillStyle = '#000'; g.fillRect(0, 0, 512, 128); for (let i = 0; i < 30; i++) { const r = g.createRadialGradient(0, 0, 0, 0, 0, 1); g.save(); g.translate(q() * 512, q() * 128); g.scale(20 + q() * 60, 6 + q() * 14); r.addColorStop(0, 'rgba(255,255,255,0.9)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.beginPath(); g.arc(0, 0, 1, 0, 7); g.fill(); g.restore(); } });
  wet.colorSpace = THREE.NoColorSpace;
  const puddle = new THREE.Mesh(new THREE.PlaneGeometry(120, 7.4), new THREE.MeshStandardMaterial({color: '#08090b', roughness: 0.04, metalness: 0.3, alphaMap: wet, transparent: true, opacity: 0.85})); puddle.rotation.x = -Math.PI / 2; puddle.position.set(0, 0.004, 3.7); puddle.material.alphaMap.repeat.set(6, 1); puddle.material.alphaMap.wrapS = THREE.RepeatWrapping; R.add(puddle);
  // Mittellinie
  for (let x = -60; x < 60; x += 6) { const m = new THREE.Mesh(new THREE.PlaneGeometry(3, 0.12), std('#d8d4c4', {roughness: 0.6})); m.rotation.x = -Math.PI / 2; m.position.set(x, 0.006, 3.7); R.add(m); }
  // Bordstein + Gehweg (Platten)
  const curb = box(120, 0.14, 0.18, std('#8a8780', {roughness: 0.85}), 0, 0.07, -0.09, R);
  const tiles = canvasTex(512, 512, g => { const q = rng(9); g.fillStyle = '#5c5a55'; g.fillRect(0, 0, 512, 512); for (let y = 0; y < 512; y += 128) for (let x = 0; x < 512; x += 128) { const v = 0.85 + q() * 0.2; g.fillStyle = `rgb(${120 * v},${117 * v},${110 * v})`; g.fillRect(x + 3, y + 3, 122, 122); } });
  const walk = new THREE.Mesh(new THREE.PlaneGeometry(120, 3.0), new THREE.MeshStandardMaterial({map: tiles, normalMap: concrete('#777', 42).normalMap, roughness: 0.8})); walk.material.map.repeat.set(80, 2); walk.material.map.wrapS = walk.material.map.wrapT = THREE.RepeatWrapping;
  walk.rotation.x = -Math.PI / 2; walk.position.set(0, 0.14, -1.5); walk.receiveShadow = true; R.add(walk);
  // gegenüberliegende Seite: Gehweg + Häuser
  const walk2 = walk.clone(); walk2.position.set(0, 0.14, 8.9); R.add(walk2); box(120, 0.14, 0.18, std('#8a8780'), 0, 0.07, 7.45, R);
  // Hausfassaden (Altbau-Reihe) mit Fenstern, einige erleuchtet
  const facade = (z, ry, seed) => {
    const q = rng(seed);
    for (let x = -40; x < 40; x += 9) {
      const h = 13 + q() * 4, col = ['#b8a58c', '#9f8f7c', '#c9b9a0', '#8e8478', '#a89580'][q() * 5 | 0];
      const tex = canvasTex(256, 384, g => { g.fillStyle = col; g.fillRect(0, 0, 256, 384); for (let i = 0; i < 2000; i++) { g.fillStyle = `rgba(0,0,0,${q() * 0.05})`; g.fillRect(q() * 256, q() * 384, 2, 2); }
        for (let f = 0; f < 4; f++) for (let c = 0; c < 3; c++) { const wx = 26 + c * 80, wy = 30 + f * 88, lit = q() < 0.3; g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(wx - 5, wy - 5, 54, 74); g.fillStyle = lit ? (q() < 0.6 ? '#f3c98a' : '#9ab4e8') : '#1b2029'; g.fillRect(wx, wy, 44, 64); g.fillStyle = 'rgba(255,255,255,0.4)'; g.fillRect(wx + 21, wy, 2, 64); g.fillRect(wx, wy + 22, 44, 2); } });
      const em = canvasTex(256, 384, g => { g.fillStyle = '#000'; g.fillRect(0, 0, 256, 384); });
      const m = new THREE.MeshStandardMaterial({map: tex, roughness: 0.9, emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: 0.0});
      const b = new THREE.Mesh(new THREE.BoxGeometry(9, h, 10), m); b.position.set(x + 4.5, h / 2 + 0.14, z + (ry ? 5 : -5)); b.receiveShadow = true; R.add(b);
      // Fenster leuchten: zusätzliche Fläche mit emissiver Maske
      const glow = canvasTex(256, 384, g => { const q2 = rng(seed * 7 + x); g.fillStyle = '#000'; g.fillRect(0, 0, 256, 384); });
    }
  };
  facade(-3.0, 0, 3); facade(10.4, 1, 7);
  // Hauseingang: Tür mit Licht (er kommt heraus)
  const doorX = 1.2;
  const entry = new THREE.Group(); entry.position.set(doorX, 0.14, -3.0); R.add(entry);
  box(1.4, 2.5, 0.25, std('#6e6255', {roughness: 0.7}), 0, 1.25, 0.05, entry);
  const doorPiv = new THREE.Group(); doorPiv.position.set(-0.55, 0, 0.18); entry.add(doorPiv);
  box(1.1, 2.2, 0.06, std('#3a2a20', {roughness: 0.5}), 0.55, 1.1, 0, doorPiv);
  const inner = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 2.2), new THREE.MeshBasicMaterial({color: '#ffd9a6'})); inner.position.set(0, 1.1, 0.12); entry.add(inner);
  const entryL = new THREE.PointLight('#ffcf94', 3, 6, 1.8); entryL.position.set(0, 2.6, 0.7); entry.add(entryL);
  const lampBox = box(0.3, 0.12, 0.15, std('#222', {emissive: '#ffd59a', emissiveIntensity: 2}), 0, 2.65, 0.3, entry);
  // Straßenlaternen
  const lamp = x => { const g = new THREE.Group(); g.position.set(x, 0.14, -0.6); R.add(g); box(0.1, 6, 0.1, std('#3a3d42', {metalness: 0.6, roughness: 0.4}), 0, 3, 0, g); box(0.15, 0.08, 1.4, std('#3a3d42', {metalness: 0.6}), 0, 6, 0.65, g);
    const head = box(0.3, 0.06, 0.5, std('#fff', {emissive: '#ffd7a0', emissiveIntensity: 3}), 0, 5.95, 1.2, g); const sl = new THREE.SpotLight('#ffc98a', 120, 22, 1.0, 0.6, 1.7); sl.position.set(0, 5.9, 1.2); sl.target.position.set(0, 0, 2.5); g.add(sl, sl.target); sl.castShadow = true; sl.shadow.mapSize.set(1024, 1024); sl.shadow.bias = -0.0008; return g; };
  lamp(-9); lamp(9); lamp(-27); lamp(27);
  // geparkte Autos auf der Gegenseite
  [[-14, '#6b6f75'], [-7, '#8a1e1e'], [6, '#e9e7e2'], [15, '#1f2b3d']].forEach(([x, c]) => { const pc = makeCar2({color: c, beam: 0}); pc.rotation.y = -Math.PI / 2; pc.position.set(x, 0, 6.4); pc.userData.beams.forEach(b => { b.intensity = 0; b.castShadow = false; }); pc.userData.tailM.emissiveIntensity = 0.0; pc.userData.tailL.intensity = 0; pc.traverse(o => { if (o.material && o.material.emissive && o.material.emissiveIntensity > 3) o.material = o.material.clone(), o.material.emissiveIntensity = 0; }); R.add(pc); });
  scene.add(new THREE.HemisphereLight('#3a4a70', '#1a1510', 0.12));
  // Das Auto, das bremst (fährt in +x)
  const car = makeCar2({color: '#3b4250', beam: 90}); car.rotation.y = Math.PI / 2; R.add(car);
  // Er
  const guy = await makeHuman('guy', {top: '#5b6b7e', bottom: '#1d1f24', shoe: '#e6e3dc', sneakers: '#ecebe6', hair: '#141110', skin: 'brown', eye: '#2a1a10', hairLen: 0.008, hairScale: 16, seed: 31});
  R.add(guy.root);
  const ph = phone(); R.add(ph);
  // Fahrplan: v0 = 8.5 m/s (≈30 km/h), Bremsung ab BRAKE, Stillstand bei STOP, Stoßstange 0.35 m vor ihm
  const GX = doorX + 0.3, GZ = 2.0, v0 = 8.5, tb = STOP - BRAKE, a = v0 / tb, sb = v0 * tb / 2;
  const stopX = GX - 0.35 - car.userData.L / 2 - 0.05;
  const carX = T => T < BRAKE ? stopX - sb - v0 * (BRAKE - T) : T < STOP ? stopX - sb + v0 * (T - BRAKE) - a * (T - BRAKE) ** 2 / 2 : stopX;
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    // Er: kommt aus der Tür (24.0–25.4), geht über den Gehweg zur Straße (bis 26.3), Blick aufs Handy, dann Schreck
    const k1 = smooth(24.2, 26.4, T);
    const path = [V(doorX, 0.14, -2.7), V(GX, 0.14, -0.4), V(GX, 0, 0.6), V(GX, 0, GZ)];
    const u = clamp((T - 24.2) / 2.6) * 3; const i0 = Math.min(2, Math.floor(u)); const p = path[i0].clone().lerp(path[i0 + 1], u - i0);
    // Bordsteinkante: sanft runter
    guy.root.position.copy(p); guy.root.position.y = lerp(0.14, 0, smooth(-0.2, 0.2, p.z)); guy.root.rotation.y = 0.05;
    const walking = T > 24.2 && T < 26.85, scare = smooth(26.65, 26.95, T);
    const ph2 = (T - 24.2) * 7.2;
    stand(guy, {walk: ph2, amp: walking ? 0.85 : 0, lean: 0.06 - scare * 0.1, nod: lerp(0.35, -0.05, scare), yaw: lerp(0.0, -1.1, scare), hands: scare > 0.4 ? 'brace' : 'phone', handsK: 1, twist: -scare * 0.5});
    mouth(guy, scare * (0.5 + 0.2 * Math.sin(T * 11)));
    guy.look(lerp(0, -0.4, scare), lerp(0.4, 0, scare));
    guy.root.updateMatrixWorld(true);
    const hr = new THREE.Vector3(), hq = new THREE.Quaternion(); guy.B('wrist.R').getWorldPosition(hr); guy.B('wrist.R').getWorldQuaternion(hq);
    ph.visible = scare < 0.5; ph.position.copy(hr).add(V(0.0, 0.07, 0.05)); ph.rotation.set(-1.0, 0, 0); ph.userData.scr.material.emissive.set('#cfe0ff'); ph.userData.scr.material.emissiveIntensity = 1.2;
    // Auto
    const cx = carX(T); car.position.set(cx, 0, GZ); const dv = T < BRAKE ? 1 : T < STOP ? 1 - (T - BRAKE) / tb : 0;
    car.userData.wheels.forEach(w => w.rotation.x = -cx / 0.33);
    const nose = T > BRAKE && T < STOP + 0.5 ? (T < STOP ? 0.035 * smooth(BRAKE, BRAKE + 0.2, T) : 0.035 * Math.cos((T - STOP) * 14) * Math.exp(-(T - STOP) * 6)) : 0;
    car.userData.body.rotation.x = nose; car.userData.tailM.emissiveIntensity = T > BRAKE ? 8 : 2.5; car.userData.tailL.intensity = T > BRAKE ? 3 : 0.6;
    // Kamera: Gehweg, folgt ihm; beim Bremsen tief, Scheinwerfer im Bild
    const hh = V(noise1(T * 0.8, 2) * 0.01, noise1(T * 0.8, 4) * 0.01, 0);
    let pos, look, fov = 38;
    const head = new THREE.Vector3(); guy.B('head').getWorldPosition(head);
    if (T < 26.4) { pos = V(GX - 0.5, 1.6, 4.9).add(V(t * 0.05, 0, -t * 0.12)).add(hh); look = head.clone().add(V(0, -0.25, 0)); fov = 34; }
    else { const k = smooth(26.4, 27.0, T); const sh = T > STOP ? Math.exp(-(T - STOP) * 5) * 0.015 : 0;
      pos = V(GX + lerp(0.6, 2.0, k), lerp(1.35, 1.35, k), lerp(4.6, 7.0, k)).add(hh).add(V(Math.sin(T * 47) * sh, Math.cos(T * 39) * sh, 0)); look = V(GX - lerp(0.0, 1.1, k), lerp(1.25, 0.95, k), GZ); fov = lerp(34, 40, k); }
    camera.position.copy(pos); camera.lookAt(look); camera.fov = fov; camera.updateProjectionMatrix();
    return {dof: {focus: pos.distanceTo(head), aperture: 0.0009, maxblur: 0.006}, exposure: 1.45, bloom: [0.45, 0.5, 0.9], grain: 0.06, vig: 0.4};
  }};
}
