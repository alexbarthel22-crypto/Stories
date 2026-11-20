// Parkour auf den Dächern bei Sonnenuntergang. Der Läufer springt über eine 3,2-m-Lücke – mitten im Sprung fällt sein
// Gleichgewichtssinn aus: Er dreht sich in der Luft, verfehlt die Kante und stürzt auf das Vordach vier Meter tiefer.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, skyDome, easeIn, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {VANISH, RETURN, JUMP, MISS} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const RY = 20, GAP0 = 0, GAP1 = 3.2, LOW = 15.6;

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.3;
  scene.fog = new THREE.Fog('#e3a27a', 60, 420);
  scene.add(skyDome('#3c4a8a', '#e88a6a', '#ffc58a', 500));
  // Sonne tief
  const sunDisc = mesh(new THREE.CircleGeometry(14, 40), new THREE.MeshBasicMaterial({color: '#fff1c8', fog: false}), -380, 45, -60, scene); sunDisc.lookAt(0, 20, 0);
  scene.add(new THREE.HemisphereLight('#ffd2b0', '#4a3a50', 1.0));
  const sun = new THREE.DirectionalLight('#ffb070', 3.2); sun.position.set(-40, 14, -8); sun.target.position.set(0, 18, 0);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 90}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.03;
  scene.add(sun, sun.target);

  const roofT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#6d6a66'; g.fillRect(0, 0, w, h); const r = rng(4); for (let i = 0; i < 5000; i++) { const v = 80 + r() * 60; g.fillStyle = `rgba(${v},${v - 4},${v - 8},0.5)`; g.fillRect(r() * w, r() * h, 2, 2); } g.strokeStyle = 'rgba(40,40,40,0.4)'; for (let x = 0; x < w; x += 64) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); } });
  roofT.wrapS = roofT.wrapT = THREE.RepeatWrapping; roofT.repeat.set(4, 4);
  const roofM = new THREE.MeshStandardMaterial({map: roofT, roughness: 0.95});
  const bldg = (x0, x1, z0, z1, h, col, seed) => {
    const ft = facadeTex(col, seed, Math.round(h / 3.2), Math.max(2, Math.round((x1 - x0) / 2.6)));
    const m = mesh(new THREE.BoxGeometry(x1 - x0, h, z1 - z0), [new THREE.MeshStandardMaterial({map: ft, roughness: 0.9}), new THREE.MeshStandardMaterial({map: ft, roughness: 0.9}), roofM, roofM, new THREE.MeshStandardMaterial({map: ft, roughness: 0.9}), new THREE.MeshStandardMaterial({map: ft, roughness: 0.9})], (x0 + x1) / 2, h / 2, (z0 + z1) / 2, scene);
    // Brüstung
    mesh(new THREE.BoxGeometry(x1 - x0, 0.25, 0.25), mat('#8a8580'), (x0 + x1) / 2, h + 0.12, z0 + 0.12, scene);
    mesh(new THREE.BoxGeometry(x1 - x0, 0.25, 0.25), mat('#8a8580'), (x0 + x1) / 2, h + 0.12, z1 - 0.12, scene);
    return m;
  };
  bldg(-26, GAP0, -6, 6, RY, '#b08a70', 3);         // Dach A (Absprung)
  bldg(GAP1, 26, -6, 6, RY, '#9aa3ad', 5);          // Dach B (Landung)
  bldg(GAP0, GAP1, -6, 6, LOW, '#a48c78', 8);        // Anbau in der Lücke, 4 m tiefer
  // Kiesdach auf dem Anbau
  const grav = mesh(new THREE.BoxGeometry(GAP1 - GAP0, 0.05, 12), mat('#8d877e', {roughness: 1}), (GAP0 + GAP1) / 2, LOW + 0.03, 0, scene);
  // Stadt drumherum
  const r = rng(31);
  for (let i = 0; i < 70; i++) { const x = -160 + r() * 320, z = -160 + r() * 320; if (Math.abs(z) < 14 && Math.abs(x) < 40) continue; const w = 8 + r() * 14, d = 8 + r() * 14, h = 10 + r() * 34;
    bldg(x, x + w, z, z + d, h, ['#b6a08a', '#9fa7b0', '#c8b49c', '#8e8a96', '#a58f7c'][i % 5], i + 40); }
  // Dachaufbauten
  const metal = mat('#9da3a8', {metalness: 0.6, roughness: 0.4});
  [[-9, -3], [-16, 2.5], [10, -3.5], [14, 3]].forEach(([x, z]) => { mesh(new RoundedBoxGeometry(1.6, 1.1, 1.2, 2, 0.05), metal, x, RY + 0.55, z, scene); });
  mesh(new THREE.CylinderGeometry(1.2, 1.2, 2.4, 20), mat('#7a5a40'), 18, RY + 2.2, -2, scene);
  for (const x of [-20, 20]) mesh(new THREE.CylinderGeometry(0.04, 0.04, 4, 6), metal, x, RY + 2, 3, scene);

  // Läufer
  const runner = makePerson(77, {top: '#e2482b', pants: '#2b2b2b', hair: '#2a1d15', shortSleeve: false});
  const piv = new THREE.Group(); scene.add(piv); piv.add(runner); runner.position.y = -0.95; // Drehpunkt in der Hüfte
  // Kumpel filmt vom Dach A
  const buddy = makePerson(81, {top: '#3f6fb5', pants: '#1f2a44'}); scene.add(buddy);
  const phone = mesh(new THREE.BoxGeometry(0.08, 0.15, 0.01), mat('#111'), 0, -0.3, 0.05, buddy.userData.armR.userData.fore);
  const dust = particles(200, 'smoke'); scene.add(dust);

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 900);
  return {scene, camera, update(shot, T) {
    const gone = T >= VANISH && T < RETURN; runner.userData.hair.visible = !gone; buddy.userData.hair.visible = !gone;
    const t = T - shot.t0;
    // Lauf: 6 m/s auf x, Absprung bei x=-0.3
    const V = 6.0; let x, y = RY + 0.95, rotZ = 0, rotX = 0, pose = {walk: T * 11, walkAmp: 1.5};
    if (T < JUMP) { x = -0.3 - V * (JUMP - T); rotZ = -0.18; }
    else if (T < MISS) { // Flug in Zeitlupe (halbe Geschwindigkeit)
      const f = (T - JUMP) / (MISS - JUMP); const tp = f * 0.55;
      x = -0.3 + 5.4 * tp; y = RY + 0.95 + 3.4 * tp - 4.9 * tp * tp * 1.6;
      const lost = smooth(0.25, 0.9, f); rotZ = -0.18 - lost * 1.9; rotX = lost * 0.5;
      pose = {walk: 0.8, walkAmp: 0.6 * (1 - lost)};
    } else { // Aufprall an der Kante, Rutschen, Sturz aufs Vordach
      const u = T - MISS;
      if (u < 0.35) { x = 2.62 - u * 0.4; y = RY + 0.12 - u * 1.2; rotZ = -2.1 - u * 1.5; rotX = 0.5; pose = {fall: 0}; }
      else { const v = Math.min(u - 0.35, 0.92); const ff = v / 0.92; x = 2.48 - ff * 0.9; y = lerp(RY - 0.3, LOW + 0.3, ff * ff); rotZ = lerp(-2.6, -Math.PI / 2 - 0.02, smooth(0.6, 1, ff)) - Math.sin(ff * Math.PI) * 0.6; rotX = lerp(0.5, 0, ff); pose = {fall: 0};
        if (u > 1.27) { const k = smooth(1.27, 1.6, u); y = LOW + 0.24 + Math.sin(smooth(1.27, 1.5, u) * Math.PI) * 0.12; rotZ = -Math.PI / 2 + 0.05; rotX = 0; } }
    }
    posePerson(runner, pose);
    if (T >= MISS) { const u = runner.userData; u.armL.rotation.set(-2.6, 0, -0.4); u.armR.rotation.set(-2.4, 0, 0.5); u.legL.rotation.x = 0.3; u.legR.rotation.x = -0.4; u.legR.userData.knee.rotation.x = 0.9;
      if (T > MISS + 1.6) { u.armL.rotation.set(-0.6 + Math.sin(T * 1.5) * 0.2, 0, -0.9); u.armR.rotation.set(-1.2, 0, 0.3); u.head.rotation.x = 0.4 * Math.sin(T * 0.8); } }
    if (T >= JUMP && T < MISS) { const u = runner.userData; u.legL.rotation.x = -0.9; u.legR.rotation.x = 0.4; u.legL.userData.knee.rotation.x = 0.8; u.armL.rotation.x = -2.2; u.armR.rotation.x = -1.4 - smooth(JUMP + 0.3, MISS, T) * 1.4; u.armL.rotation.z = -0.6 * smooth(JUMP + 0.3, MISS, T); }
    piv.position.set(x, y, 0.2); piv.rotation.set(rotX, -Math.PI / 2 + Math.PI, rotZ); // Blick in +x
    piv.rotation.set(0, Math.PI / 2, 0); piv.rotateX(-rotZ); piv.rotateZ(rotX);
    // Kumpel: filmt, kippt dann zur Seite und setzt sich hart hin
    buddy.position.set(-4.8, RY, 1.6); buddy.rotation.set(0, Math.PI / 2 - 0.3, 0);
    const bf = smooth(34.3, 35.2, T); posePerson(buddy, {holdUp: 1 - bf, fall: bf, fallDir: 1, slipSide: 1});
    updateParticles(dust, false ? [{type: 'burstSmoke', pos: V3(1.6, LOW + 0.2, 0.2), r: 0.8, t0: MISS + 1.27, size: 0.5, rise: 0.3, share: 1}] : [], T, V3(0.3, 0, 0.1));
    // Kamera auf Dach B, sieht dem Läufer entgegen; nach dem Sturz Blick nach unten
    camera.fov = 58;
    const down = smooth(MISS + 0.3, MISS + 1.4, T);
    const sh = smooth(MISS, MISS + 0.2, T) * (1 - smooth(MISS + 1.6, MISS + 2.6, T));
    const xr = Math.max(Math.min(x, 2.0), -12);
    camera.position.set(lerp(xr * 0.45 + 2.2, 2.2, down) + noise1(T * 7, 1) * 0.03 * sh, RY + lerp(1.5, 3.2, down) + noise1(T * 6, 2) * 0.03 * sh, lerp(8.5, 7.0, down));
    camera.lookAt(V3(lerp(xr * 0.6 + 1.3, 1.6, down), lerp(RY + 0.2, LOW + 0.4, down), 0.2));
    camera.updateProjectionMatrix();
  }};
}
