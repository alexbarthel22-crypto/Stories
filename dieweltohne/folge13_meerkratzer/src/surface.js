// Hook: Ein Hauseingang mitten im offenen Meer. Die Kamera taucht ab – und der Turm geht endlos nach unten.
import {THREE, mat, mesh, rng, clamp, lerp, smooth, easeIn, easeOut, canvasTex, skyDome, envMap, noise1} from './lib.js';

function facadeTex() { // Fensterraster, ein Teil der Wohnungen ist beleuchtet
  const r = rng(31);
  const base = canvasTex(256, 1024, (g, w, h) => {
    g.fillStyle = '#2c3a40'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 2500; i++) { g.fillStyle = `rgba(255,255,255,${r() * 0.04})`; g.fillRect(r() * w, r() * h, 2, 2); }
    for (let y = 0; y < 16; y++) for (let x = 0; x < 4; x++) {
      const px = x * 64 + 8, py = y * 64 + 10;
      g.fillStyle = '#0e1a20'; g.fillRect(px, py, 48, 40);
      g.fillStyle = 'rgba(160,210,230,0.15)'; g.fillRect(px + 2, py + 2, 20, 36);
      g.fillStyle = '#56676e'; g.fillRect(px - 2, py + 40, 52, 5);
    }
  });
  const r2 = rng(32);
  const emi = canvasTex(256, 1024, (g, w, h) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < 16; y++) for (let x = 0; x < 4; x++) if (r2() < 0.45) {
      const px = x * 64 + 8, py = y * 64 + 10; const warm = r2() < 0.7;
      const gr = g.createLinearGradient(px, py, px, py + 40); gr.addColorStop(0, warm ? '#ffd79a' : '#bfe6ff'); gr.addColorStop(1, warm ? '#d9934a' : '#6fa8d8');
      g.fillStyle = gr; g.fillRect(px, py, 48, 40);
    }
  });
  for (const t of [base, emi]) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1, 40); }
  return {base, emi};
}

function rayTex() {
  return canvasTex(64, 512, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const gx = g.createLinearGradient(0, 0, w, 0); gx.addColorStop(0, 'rgba(0,0,0,1)'); gx.addColorStop(0.5, 'rgba(0,0,0,0)'); gx.addColorStop(1, 'rgba(0,0,0,1)');
    g.globalCompositeOperation = 'destination-out'; g.fillStyle = gx; g.fillRect(0, 0, w, h);
  });
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.1, 3000);
  const env = envMap(renderer); scene.environment = env;
  const sky = skyDome('#3f86c8', '#9cc9e8', '#d9ecf5', 1500); scene.add(sky);
  const sun = new THREE.DirectionalLight('#fff3dc', 2.6); sun.position.set(60, 120, 40); scene.add(sun);
  const hemi = new THREE.HemisphereLight('#bfe3ff', '#0d4a5e', 1.0); scene.add(hemi);
  const fogAir = new THREE.Fog('#cfe6f2', 120, 1400), fogSea = new THREE.FogExp2('#0f6f8e', 0.03);

  // Meeresoberfläche mit Wellen
  const segs = 180, size = 700;
  const seaGeo = new THREE.PlaneGeometry(size, size, segs, segs); seaGeo.rotateX(-Math.PI / 2);
  const base = Float32Array.from(seaGeo.attributes.position.array);
  const seaMat = new THREE.MeshStandardMaterial({color: '#0f5872', roughness: 0.1, metalness: 0.15, envMapIntensity: 1.2, side: THREE.DoubleSide, transparent: true, opacity: 0.96});
  const sea = new THREE.Mesh(seaGeo, seaMat); scene.add(sea);
  const waveH = (x, z, t) => 0.35 * Math.sin(x * 0.12 + t * 1.1) + 0.22 * Math.sin(z * 0.17 - t * 1.4 + 1.3) + 0.12 * Math.sin((x + z) * 0.31 + t * 2.1) + 0.05 * Math.sin(x * 0.9 - z * 0.7 + t * 3.3);

  // Plattform mit gläsernem Eingang (ragt knapp aus dem Wasser)
  const conc = mat('#c9c6be', {roughness: 0.85});
  const top = new THREE.Group(); scene.add(top);
  mesh(new THREE.CylinderGeometry(9, 9.4, 3.2, 48), conc, 0, -1.0, 0, top);
  mesh(new THREE.TorusGeometry(9.05, 0.08, 6, 64), mat('#e9e9e4', {metalness: 0.6, roughness: 0.3}), 0, 1.65, 0, top).rotation.x = Math.PI / 2;
  for (let i = 0; i < 24; i++) { const a = i / 24 * Math.PI * 2; mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.0, 6), mat('#e9e9e4', {metalness: 0.6, roughness: 0.3}), Math.cos(a) * 9.05, 1.1, Math.sin(a) * 9.05, top); }
  const glass = new THREE.MeshPhysicalMaterial({color: '#9fc7d6', roughness: 0.05, metalness: 0.1, transparent: true, opacity: 0.35, envMapIntensity: 1.5});
  mesh(new THREE.CylinderGeometry(3.2, 3.2, 3.4, 40, 1, true), glass, 0, 2.3, 0, top);
  mesh(new THREE.CylinderGeometry(3.6, 3.6, 0.3, 40), mat('#f1efe9', {roughness: 0.5}), 0, 4.1, 0, top);
  for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2; mesh(new THREE.BoxGeometry(0.1, 3.4, 0.1), mat('#30383c', {metalness: 0.7, roughness: 0.35}), Math.cos(a) * 3.2, 2.3, Math.sin(a) * 3.2, top); }
  // Aufzugtür im Inneren (warm beleuchtet)
  const lift = mesh(new THREE.BoxGeometry(1.6, 2.6, 0.2), mat('#c9a467', {metalness: 0.8, roughness: 0.25}), 0, 1.9, -1.2, top);
  const inner = new THREE.PointLight('#ffd9a0', 6, 8, 1.6); inner.position.set(0, 3.4, 0); top.add(inner);
  mesh(new THREE.BoxGeometry(2.2, 0.06, 0.6), mat('#30383c', {metalness: 0.7}), 0, 0.62, 3.6, top); // Stufe zum Steg
  // kleiner Steg mit Boot
  mesh(new THREE.BoxGeometry(2.0, 0.2, 9), mat('#8a6a4a', {roughness: 0.9}), 0, 0.45, 12.5, top);
  for (const z of [9, 12, 15]) for (const x of [-0.9, 0.9]) mesh(new THREE.CylinderGeometry(0.12, 0.12, 2.4, 8), mat('#5b4636'), x, -0.6, z, top);
  const boat = new THREE.Group(); top.add(boat); boat.position.set(2.6, 0.1, 14);
  mesh(new THREE.BoxGeometry(1.6, 0.6, 4.2), mat('#f2f2ee', {roughness: 0.4}), 0, 0, 0, boat);
  mesh(new THREE.BoxGeometry(1.2, 0.5, 1.2), mat('#2c4a63', {roughness: 0.4}), 0, 0.5, -0.4, boat);

  // Der Turm unter Wasser: quadratischer Schaft, der in die Tiefe verschwindet
  const tx = facadeTex(); const H = 1400;
  const shaftMat = new THREE.MeshStandardMaterial({map: tx.base, emissiveMap: tx.emi, emissive: '#ffffff', emissiveIntensity: 1.4, roughness: 0.6, metalness: 0.2});
  const shaft = mesh(new THREE.BoxGeometry(13, H, 13), shaftMat, 0, -2.6 - H / 2, 0); scene.add(shaft);
  // Fensterbänder skalieren: 1 Etage = 3 m
  tx.base.repeat.set(1, H / 48); tx.emi.repeat.set(1, H / 48);
  // Rippen an den Kanten
  for (const [x, z] of [[-6.6, -6.6], [6.6, -6.6], [-6.6, 6.6], [6.6, 6.6]]) mesh(new THREE.BoxGeometry(0.5, H, 0.5), mat('#5d6a70', {metalness: 0.5, roughness: 0.4}), x, -2.6 - H / 2, z, scene);
  // Gläserner Aufzug an der Vorderseite (leuchtet)
  const cab = new THREE.Group(); scene.add(cab);
  mesh(new THREE.BoxGeometry(2.4, 2.8, 2.0), new THREE.MeshStandardMaterial({color: '#ffe2b0', emissive: '#ffcf8a', emissiveIntensity: 1.2, transparent: true, opacity: 0.85}), 0, 0, 0, cab);
  const cabL = new THREE.PointLight('#ffd49a', 30, 18, 1.8); cab.add(cabL);
  cab.position.set(0, -14, 7.6);
  mesh(new THREE.BoxGeometry(0.25, H, 0.25), mat('#7b878c', {metalness: 0.8, roughness: 0.3}), -1.5, -2.6 - H / 2, 6.8, scene);
  mesh(new THREE.BoxGeometry(0.25, H, 0.25), mat('#7b878c', {metalness: 0.8, roughness: 0.3}), 1.5, -2.6 - H / 2, 6.8, scene);

  // Lichtstrahlen unter Wasser
  const rays = [], rt = rayTex(); const rr = rng(4);
  for (let i = 0; i < 14; i++) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(3 + rr() * 5, 70), new THREE.MeshBasicMaterial({map: rt, color: '#bff3ff', transparent: true, opacity: 0.16, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false}));
    m.position.set((rr() - 0.5) * 50, -35, (rr() - 0.5) * 40 + 10); m.rotation.set(0.12, rr() * 3, 0.18); scene.add(m); rays.push(m);
  }
  // Luftblasen beim Eintauchen
  const nb = 260, bpos = new Float32Array(nb * 3), bseed = []; const br = rng(77);
  for (let i = 0; i < nb; i++) bseed.push([br() * 2 - 1, br(), br() * 2 - 1, 0.5 + br()]);
  const bgeo = new THREE.BufferGeometry(); bgeo.setAttribute('position', new THREE.BufferAttribute(bpos, 3));
  const bubbles = new THREE.Points(bgeo, new THREE.PointsMaterial({map: canvasTex(64, 64, g => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 30); gr.addColorStop(0, 'rgba(255,255,255,0.2)'); gr.addColorStop(0.7, 'rgba(255,255,255,0.5)'); gr.addColorStop(0.85, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); }), color: '#e8fbff', size: 0.09, transparent: true, opacity: 0.9, depthWrite: false}));
  bubbles.frustumCulled = false; scene.add(bubbles);
  // Schwebeteilchen unter Wasser
  const ns = 900, spos = new Float32Array(ns * 3); const sr = rng(5);
  for (let i = 0; i < ns; i++) { spos[i * 3] = (sr() - 0.5) * 50; spos[i * 3 + 1] = -sr() * 80; spos[i * 3 + 2] = (sr() - 0.5) * 50 + 15; }
  const sgeo = new THREE.BufferGeometry(); sgeo.setAttribute('position', new THREE.BufferAttribute(spos, 3));
  const snow = new THREE.Points(sgeo, new THREE.PointsMaterial({map: canvasTex(64, 64, g => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 30); gr.addColorStop(0, 'rgba(255,255,255,0.2)'); gr.addColorStop(0.7, 'rgba(255,255,255,0.5)'); gr.addColorStop(0.85, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); }), color: '#cdeef7', size: 0.06, transparent: true, opacity: 0.5, depthWrite: false})); scene.add(snow);

  const DIVE = 2.25;
  function update(shot, T) {
    // Wellen
    const p = seaGeo.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = base[i * 3], z = base[i * 3 + 2]; p.setY(i, waveH(x, z, T)); }
    p.needsUpdate = true; seaGeo.computeVertexNormals();
    boat.position.y = 0.1 + waveH(2.6, 14, T) * 0.8; boat.rotation.z = 0.05 * Math.sin(T * 1.3);
    cab.position.y = -14 - Math.max(0, T - 2.5) * 2.2;

    // Kamera: Anflug von oben – Eintauchen – Blick am Turm hinab
    let pos, look;
    if (T < 1.9) {
      const k = easeOut(T / 1.9);
      pos = new THREE.Vector3(lerp(-30, -16, k), lerp(14, 4.5, k), lerp(34, 24, k)); look = new THREE.Vector3(0, lerp(2.5, 0.5, k), 0);
    } else if (T < 2.9) {
      const k = (T - 1.9) / 1.0;
      pos = new THREE.Vector3(lerp(-16, -14, k), lerp(4.5, -5, easeIn(k)), lerp(24, 21, k)); look = new THREE.Vector3(0, lerp(0.5, -8, k), 0);
    } else {
      const k = smooth(2.9, 5.0, T);
      pos = new THREE.Vector3(lerp(-14, -9, k), lerp(-5, -26, k), lerp(21, 18, k)); look = new THREE.Vector3(0, lerp(-8, -70, k), lerp(0, 4, k));
    }
    pos.x += noise1(T, 2) * 0.12; pos.y += noise1(T, 5) * 0.08;
    camera.position.copy(pos); camera.lookAt(look);
    const under = camera.position.y < waveH(camera.position.x, camera.position.z, T) - 0.05;
    scene.fog = under ? fogSea : fogAir; sky.visible = !under;
    seaMat.color.set(under ? '#7fd8ea' : '#0f5872'); seaMat.emissive.set(under ? '#3aa6c6' : '#000000'); seaMat.opacity = under ? 0.8 : 0.96;
    sun.intensity = under ? 0.9 : 2.6; hemi.color.set(under ? '#7fd3ea' : '#bfe3ff'); hemi.intensity = under ? 1.4 : 1.0;
    renderer.setClearColor(under ? '#0f6f8e' : '#cfe6f2');
    rays.forEach((m, i) => { m.visible = under; m.material.opacity = 0.12 + 0.06 * Math.sin(T * 1.3 + i); });
    snow.visible = under;
    // Blasen
    const d = T - DIVE; bubbles.visible = d > 0 && d < 2.6;
    if (bubbles.visible) for (let i = 0; i < nb; i++) { const s = bseed[i];
      bpos[i * 3] = camera.position.x + s[0] * 1.6 + Math.sin(T * 6 + i) * 0.05; bpos[i * 3 + 2] = camera.position.z + s[2] * 1.6 - 1.2;
      bpos[i * 3 + 1] = camera.position.y - 1.5 + s[1] * 3 + d * d * s[3] * 3.5; }
    bgeo.attributes.position.needsUpdate = true;
  }
  return {scene, camera, update};
}
