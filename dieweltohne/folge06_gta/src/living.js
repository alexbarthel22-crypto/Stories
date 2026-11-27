// Wohnzimmer nebenan: Papa auf dem Sofa mit Headset, Fernseher zeigt den Startbildschirm. Er springt auf. Mama in der Tür.
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {lerp, smooth, clamp, rng, noise1, canvasTex, envMap, easeOut} from './lib.js';
import {woodFloor, plaster, fabric, carpet, wrinkles} from './tex.js';
import {makeHuman} from './mh.js';
import {sit, stand, mouth, blend, hipY} from './poses.js';
import {makeGame} from './game.js';
import {controller, headset, can} from './props.js';
import {PAPA_UP} from './timeline.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
function box(w, h, d, m, x, y, z, p, r = 0.01) { const o = new THREE.Mesh(r ? new RoundedBoxGeometry(w, h, d, 3, r) : new THREE.BoxGeometry(w, h, d), m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; p.add(o); return o; }
const std = (c, o = {}) => new THREE.MeshStandardMaterial({color: c, roughness: 0.8, ...o});

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#000');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.05;
  const camera = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.03, 40);
  const R = new THREE.Group(); scene.add(R);
  const X0 = -2.6, X1 = 2.6, Z0 = -2.2, Z1 = 2.8, HH = 2.6;
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), new THREE.MeshStandardMaterial({...woodFloor([120, 86, 58], 12), roughness: 0.45})); floor.material.map.repeat.set(1.6, 1.8); floor.rotation.x = -Math.PI / 2; floor.position.z = (Z0 + Z1) / 2; floor.receiveShadow = true; R.add(floor);
  const wallM = new THREE.MeshStandardMaterial({...plaster('#ddd5c8', 21), roughness: 0.92});
  const wall = (w, h, pos, ry, m = wallM) => { const o = new THREE.Mesh(new THREE.PlaneGeometry(w, h), m); o.position.copy(pos); o.rotation.y = ry; o.receiveShadow = true; R.add(o); return o; };
  wall(X1 - X0, HH, V(0, HH / 2, Z0), 0); wall(Z1 - Z0, HH, V(X0, HH / 2, (Z0 + Z1) / 2), Math.PI / 2); wall(Z1 - Z0, HH, V(X1, HH / 2, (Z0 + Z1) / 2), -Math.PI / 2);
  // Rückwand mit Türöffnung (Flur hell) x 0.9..1.9
  const bw = (x0, x1, y0, y1) => { const o = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, y1 - y0), wallM); o.position.set((x0 + x1) / 2, (y0 + y1) / 2, Z1); o.rotation.y = Math.PI; o.receiveShadow = true; R.add(o); };
  bw(X0, 0.9, 0, HH); bw(1.9, X1, 0, HH); bw(0.9, 1.9, 2.1, HH);
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), std('#ece8e0', {roughness: 0.95})); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, HH, (Z0 + Z1) / 2); R.add(ceil);
  const hallW = new THREE.Mesh(new THREE.PlaneGeometry(3, HH), std('#efe5d4')); hallW.position.set(1.4, HH / 2, Z1 + 1.5); hallW.rotation.y = Math.PI; R.add(hallW);
  const hallF = new THREE.Mesh(new THREE.PlaneGeometry(3, 2), new THREE.MeshStandardMaterial({...woodFloor([130, 96, 64], 13), roughness: 0.5})); hallF.rotation.x = -Math.PI / 2; hallF.position.set(1.4, 0, Z1 + 1); R.add(hallF);
  const hallL = new THREE.PointLight('#ffd3a0', 10, 7, 1.6); hallL.position.set(1.4, 2.3, Z1 + 0.9); hallL.castShadow = true; hallL.shadow.mapSize.set(1024, 1024); R.add(hallL);
  const frameM = std('#f2efe8', {roughness: 0.5}); box(0.05, 2.14, 0.12, frameM, 0.875, 1.07, Z1, R, 0.004); box(0.05, 2.14, 0.12, frameM, 1.925, 1.07, Z1, R, 0.004); box(1.1, 0.05, 0.12, frameM, 1.4, 2.12, Z1, R, 0.004);
  // Fernseher (groß) auf Lowboard an der Vorderwand
  const game = makeGame(renderer);
  const TW = 1.44, TH = 0.81, TVY = 1.12, TVZ = Z0 + 0.06;
  box(2.2, 0.45, 0.45, std('#2b2724', {roughness: 0.55}), 0, 0.26, Z0 + 0.24, R, 0.01);
  const tv = new THREE.Group(); tv.position.set(0, TVY, TVZ); R.add(tv);
  box(TW + 0.02, TH + 0.02, 0.03, std('#0b0b0c', {roughness: 0.3, metalness: 0.3}), 0, 0, -0.015, tv, 0.004);
  const screenM = new THREE.MeshPhysicalMaterial({color: '#000', emissive: '#fff', emissiveIntensity: 0, roughness: 0.1, clearcoat: 1}); const scr = new THREE.Mesh(new THREE.PlaneGeometry(TW, TH), screenM); scr.position.z = 0.001; tv.add(scr);
  const uiM = new THREE.MeshBasicMaterial({map: game.ui, toneMapped: false, color: new THREE.Color(1.25, 1.25, 1.25)}); const ui = new THREE.Mesh(new THREE.PlaneGeometry(TW, TH), uiM); ui.position.z = 0.002; tv.add(ui);
  const tvLight = new THREE.RectAreaLight('#4f74d8', 6, TW, TH); tvLight.position.set(0, TVY, TVZ + 0.01); tvLight.lookAt(0, TVY, 3); R.add(tvLight);
  const tvSpot = new THREE.SpotLight('#4f74d8', 4, 10, 0.9, 0.9, 1.6); tvSpot.position.set(0, TVY, TVZ + 0.05); tvSpot.target.position.set(0, 0.9, 2); R.add(tvSpot, tvSpot.target); tvSpot.castShadow = true; tvSpot.shadow.mapSize.set(2048, 2048); tvSpot.shadow.bias = -0.0008; tvSpot.shadow.radius = 6;
  // Stehlampe (gedimmt, warm) neben dem Sofa
  const lampP = new THREE.Group(); lampP.position.set(-1.65, 0, 1.6); R.add(lampP);
  box(0.03, 1.5, 0.03, std('#1d1d1d', {metalness: 0.7, roughness: 0.3}), 0, 0.75, 0, lampP, 0.005); box(0.3, 0.02, 0.3, std('#1d1d1d', {metalness: 0.7}), 0, 0.01, 0, lampP, 0.005);
  const shade = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.22, 0.28, 32, 1, true), new THREE.MeshStandardMaterial({color: '#f1e6d2', emissive: '#ffcf8a', emissiveIntensity: 0.6, side: THREE.DoubleSide, roughness: 0.9})); shade.position.y = 1.55; lampP.add(shade);
  const lampL = new THREE.PointLight('#ffc27a', 1.6, 6, 1.8); lampL.position.y = 1.5; lampL.castShadow = true; lampL.shadow.mapSize.set(1024, 1024); lampP.add(lampL);
  // Sofa (Stoff), Kissen, Decke
  const sofa = new THREE.Group(); sofa.position.set(0, 0, 1.55); R.add(sofa);
  const sofaM = new THREE.MeshStandardMaterial({...fabric('#5a5f63', 22, 5), roughness: 0.96});
  box(2.2, 0.42, 0.95, sofaM, 0, 0.21, 0, sofa, 0.05); box(2.2, 0.55, 0.22, sofaM, 0, 0.62, 0.38, sofa, 0.08);
  for (const x of [-1.0, 1.0]) box(0.2, 0.62, 0.95, sofaM, x, 0.31, 0, sofa, 0.07);
  for (const x of [-0.45, 0.45]) { const c = box(0.88, 0.14, 0.7, sofaM, x, 0.49, -0.06, sofa, 0.06); c.scale.y = 1; }
  const pil = (x, rz, col) => { const p = new THREE.Mesh(new RoundedBoxGeometry(0.45, 0.42, 0.14, 4, 0.06), new THREE.MeshStandardMaterial({...fabric(col, 23, 3), roughness: 0.95})); p.position.set(x, 0.75, 0.22); p.rotation.set(-0.25, 0, rz); p.castShadow = p.receiveShadow = true; sofa.add(p); };
  pil(-0.78, 0.15, '#b2884f'); pil(0.82, -0.2, '#8a9aa2');
  // Couchtisch mit Chips, Dosen, Fernbedienung
  box(1.1, 0.04, 0.6, std('#6b4a32', {roughness: 0.45}), 0, 0.42, 0.45, R, 0.01); for (const [x, z] of [[-0.5, 0.2], [0.5, 0.2], [-0.5, 0.7], [0.5, 0.7]]) box(0.04, 0.4, 0.04, std('#3c2b1f'), x, 0.2, z, R, 0.005);
  const bowl = new THREE.Mesh(new THREE.SphereGeometry(0.13, 24, 12, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), std('#e9e4da', {roughness: 0.3, side: THREE.DoubleSide})); bowl.position.set(-0.25, 0.57, 0.45); bowl.scale.y = 0.6; R.add(bowl);
  const chips = new THREE.Mesh(new THREE.SphereGeometry(0.11, 16, 8), std('#d9a648', {roughness: 0.7})); chips.position.set(-0.25, 0.5, 0.45); chips.scale.y = 0.4; R.add(chips);
  [can('#c43b2e', 5), can('#1a1a1a', 6)].forEach((c, i) => { c.position.set(0.15 + i * 0.12, 0.5, 0.4 + i * 0.05); R.add(c); });
  // Regal, Pflanze, Bilder, Teppich
  const rug = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.9), new THREE.MeshStandardMaterial({...carpet('#9a8f80', 24), roughness: 1})); rug.rotation.x = -Math.PI / 2; rug.position.set(0, 0.004, 0.5); rug.receiveShadow = true; R.add(rug);
  box(0.4, 1.9, 1.2, std('#e9e5de', {roughness: 0.5}), X1 - 0.21, 0.95, -0.6, R, 0.01);
  { const q = rng(31); for (let sh = 0; sh < 4; sh++) { let z = -1.15; while (z < -0.1) { const w = 0.03 + q() * 0.05, h = 0.2 + q() * 0.1; box(0.25, h, w, std(['#7b2e2e', '#2e4f7b', '#d8c9a8', '#3e6b45', '#b5893f'][q() * 5 | 0], {roughness: 0.8}), X1 - 0.43, 0.3 + sh * 0.45 + h / 2, z, R, 0.002); z += w + 0.01 + (q() < 0.1 ? 0.15 : 0); } } }
  const pot = box(0.32, 0.35, 0.32, std('#c9c2b6', {roughness: 0.6}), X0 + 0.35, 0.175, -1.7, R, 0.05);
  const leafM = new THREE.MeshStandardMaterial({color: '#2f5a32', roughness: 0.7, side: THREE.DoubleSide}); const pl = rng(4);
  for (let i = 0; i < 26; i++) { const l = new THREE.Mesh(new THREE.PlaneGeometry(0.12, 0.42), leafM); l.position.set(X0 + 0.35 + (pl() - 0.5) * 0.2, 0.6 + pl() * 0.9, -1.7 + (pl() - 0.5) * 0.2); l.rotation.set(pl() - 0.5, pl() * 6, pl() - 0.5); l.castShadow = true; R.add(l); }
  const art = canvasTex(400, 280, g => { const gr = g.createLinearGradient(0, 0, 0, 280); gr.addColorStop(0, '#9db7c8'); gr.addColorStop(0.55, '#e6d2ad'); gr.addColorStop(0.56, '#5c6b4e'); gr.addColorStop(1, '#3f4a37'); g.fillStyle = gr; g.fillRect(0, 0, 400, 280); });
  const fr = new THREE.Group(); fr.position.set(X0 + 0.01, 1.6, 0.6); fr.rotation.y = Math.PI / 2; R.add(fr); box(1.04, 0.74, 0.03, std('#1b1b1b'), 0, 0, 0, fr, 0.003); const ap = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 0.7), std('#fff', {map: art, roughness: 0.6})); ap.position.z = 0.016; fr.add(ap);
  scene.add(new THREE.HemisphereLight('#7a88a8', '#2a2018', 0.05));
  // Papa und Mama
  const dad = await makeHuman('dad', {top: '#6c7a5a', bottom: '#2f3c55', shoe: '#2a2a2a', sneakers: '#3a3530', sole: '#2a2622', hair: '#4a3a2c', skin: 'light', eye: '#4a5a6a', hairLen: 0.012, seed: 21});
  R.add(dad.root);
  const mom = await makeHuman('mom', {top: '#3d5a4b', bottom: '#3a4150', shoe: '#7a6a5e', sneakers: '#c9b8a8', sole: '#e8e2da', hair: '#5a3a24', skin: 'light', eye: '#3e5a4a', hairLen: 0.045, hairDrop: 0.06, seed: 9});
  R.add(mom.root);
  const pad = controller('#1e1f22'); R.add(pad);
  const hs = headset(); R.add(hs);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    game.render(T, 'home'); screenM.emissiveIntensity = 0; uiM.opacity = 1;
    const fl = 0.95 + 0.05 * Math.sin(T * 3); tvLight.intensity = 5 * fl; tvSpot.intensity = 3.5 * fl;
    // Papa: sitzt starr, springt bei PAPA_UP auf, Arme hoch, schreit
    const up = smooth(PAPA_UP, PAPA_UP + 0.55, T);
    const sy = 0.56, hy = hipY(dad);
    dad.root.position.set(-0.25, lerp(sy - hy, 0, up) + Math.sin(clamp((T - PAPA_UP) / 0.55) * Math.PI) * 0.06, lerp(1.6, 1.0, up)); dad.root.rotation.set(0, Math.PI, 0);
    const shout = T > PAPA_UP + 0.3;
    blend(dad, () => sit(dad, {lean: 0.1 + Math.sin(T * 0.4) * 0.01, nod: 0.0, hands: 'pad', grip: 0.7, knees: 0.25}),
      () => stand(dad, {lean: -0.08, nod: -0.25, hands: T > PAPA_UP + 0.45 ? 'up' : 'brace', handsK: 1, tilt: Math.sin(T * 5) * 0.05}), up);
    mouth(dad, shout ? 0.75 + 0.2 * Math.sin(T * 13) : 0.08); dad.look(0, up * 0.2);
    // Controller: in den Händen, bis er aufspringt – dann fliegt er aufs Sofa
    dad.root.updateMatrixWorld(true);
    const hl = new THREE.Vector3(), hr = new THREE.Vector3(); dad.B('wrist.L').getWorldPosition(hl); dad.B('wrist.R').getWorldPosition(hr);
    if (up < 0.3) { pad.position.copy(hl).add(hr).multiplyScalar(0.5).add(V(0, 0.015, -0.06)); pad.rotation.set(0.5, Math.atan2(hl.x - hr.x, hl.z - hr.z) + Math.PI / 2, 0, 'YXZ'); }
    else { const k = clamp((T - PAPA_UP - 0.15) / 0.5); pad.position.set(lerp(-0.25, 0.4, k), 0.56 + Math.sin(k * Math.PI) * 0.35, lerp(1.35, 1.5, k)); pad.rotation.set(k * 6, k * 3, 0); }
    // Headset auf dem Kopf
    const hp = new THREE.Vector3(), hq = new THREE.Quaternion(); dad.B('head').getWorldPosition(hp); dad.B('head').getWorldQuaternion(hq);
    hs.position.copy(hp).add(V(0, 0.105, 0).applyQuaternion(hq)); hs.quaternion.copy(hq); hs.scale.setScalar(1.05);
    // Mama in der Tür: Hände in den Hüften, schüttelt den Kopf
    mom.root.position.set(1.4, 0, Z1 - 0.1); mom.root.rotation.y = Math.PI + 0.35;
    stand(mom, {hands: 'hips', yaw: -0.25 + Math.sin(T * 2.2) * 0.12 * smooth(PAPA_UP + 0.5, PAPA_UP + 1.0, T), nod: -0.05, side: 0.05});
    mouth(mom, 0); mom.look(-0.15, 0);
    // Kamera: neben dem Fernseher, auf Papa, Mama hinten in der Tür
    const hh = V(noise1(T * 0.6, 3) * 0.008, noise1(T * 0.6, 5) * 0.008, 0);
    const pos = V(-0.95, 1.25, -1.2).add(V(t * 0.02, 0, t * 0.03)).add(hh);
    const head = new THREE.Vector3(); dad.B('head').getWorldPosition(head);
    const look = V(0.25, lerp(1.1, 1.3, up), 1.5);
    camera.position.copy(pos); camera.lookAt(look); camera.fov = 44; camera.updateProjectionMatrix();
    return {dof: {focus: pos.distanceTo(head), aperture: 0.001, maxblur: 0.006}, exposure: 1.3, bloom: [0.45, 0.55, 0.8], grain: 0.055, vig: 0.38};
  }};
}
