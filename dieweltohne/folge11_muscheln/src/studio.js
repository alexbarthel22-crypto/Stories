// Streamer-Zimmer: Livestream "Austern essen". Stufe 1: Die Auster verschwindet vor seinem Mund – er schlürft Luft, die Zitrone spritzt ins Auge.
// back / fill: Alle Muscheln der Welt kommen zu ihm – das Fenster birst, das Zimmer läuft voll, er versinkt.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {seat, unseat, addMouth, mouthOpen, brows} from './people.js';
import {shellSwarm, oysterHalf, heapTex, shellMats} from './shells.js';
import {VANISH, LEMON, WINDOW, BURIED} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

// Füllhöhe der Muscheln im Zimmer (m)
export function level(T) { return T < WINDOW + 0.4 ? 0 : 0.38 * smooth(WINDOW + 0.4, 68, T) + 1.9 * Math.pow(smooth(68, 77.6, T), 1.15); }
const WIN = {x0: 0.05, x1: 0.85, y0: 1.18, y1: 1.98, z: -1.5};

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.35;
  scene.background = new THREE.Color('#0d0b14');
  const hemi = new THREE.HemisphereLight('#c9c4ff', '#2a2230', 0.45); scene.add(hemi);
  const ring = new THREE.PointLight('#fff3e8', 9, 6, 1.6); ring.position.set(0.15, 1.35, 1.2); scene.add(ring);
  const key = new THREE.SpotLight('#fff0e0', 14, 8, 0.8, 0.7, 1.4); key.position.set(-0.9, 2.4, 1.4); key.target.position.set(0, 1.0, -0.3); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); scene.add(key, key.target);
  const ledP = new THREE.PointLight('#a24cff', 6, 4, 1.5); ledP.position.set(-0.6, 2.0, -1.2); scene.add(ledP);
  const ledC = new THREE.PointLight('#2fd2ff', 4, 4, 1.5); ledC.position.set(1.4, 0.6, -1.2); scene.add(ledC);
  const dayL = new THREE.SpotLight('#cfe2ff', 6, 7, 0.9, 0.8, 1.5); dayL.position.set(0.45, 1.6, -2.6); dayL.target.position.set(0, 0.8, 0.5); scene.add(dayL, dayL.target);

  // Raum 4.4 x 4.4 m
  const floorT = canvasTex(512, 512, (g, w, h) => { const r = rng(2); for (let i = 0; i < 12; i++) { const v = 120 + r() * 25; g.fillStyle = `rgb(${v + 25},${v + 5},${v - 25})`; g.fillRect(0, i * 43, w, 42); g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(0, i * 43 + 41, w, 2); } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(4, 4);
  mesh(new THREE.PlaneGeometry(4.6, 4.6), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.55}), 0, 0, 0.6, scene).rotation.x = -Math.PI / 2;
  const wallM = mat('#2b2838', {roughness: 0.9}), wallM2 = mat('#34303f', {roughness: 0.9});
  // Rückwand mit Fensterloch (aus vier Teilen)
  const bw = (x0, x1, y0, y1) => mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, 0.12), wallM, (x0 + x1) / 2, (y0 + y1) / 2, WIN.z - 0.06, scene);
  bw(-2.3, WIN.x0, 0, 3); bw(WIN.x1, 2.3, 0, 3); bw(WIN.x0, WIN.x1, 0, WIN.y0); bw(WIN.x0, WIN.x1, WIN.y1, 3);
  mesh(new THREE.BoxGeometry(0.12, 3, 4.6), wallM2, -2.3, 1.5, 0.75, scene); mesh(new THREE.BoxGeometry(0.12, 3, 4.6), wallM2, 2.3, 1.5, 0.75, scene);
  mesh(new THREE.BoxGeometry(4.6, 0.1, 4.6), mat('#24212d'), 0, 3.05, 0.75, scene);
  // Fenster: Rahmen, Scheibe, draußen Himmel und Nachbarhaus
  const frameM = mat('#e8e6e2', {roughness: 0.5});
  for (const [x, y, w, h] of [[(WIN.x0 + WIN.x1) / 2, WIN.y0, WIN.x1 - WIN.x0 + 0.08, 0.06], [(WIN.x0 + WIN.x1) / 2, WIN.y1, WIN.x1 - WIN.x0 + 0.08, 0.06], [WIN.x0, (WIN.y0 + WIN.y1) / 2, 0.06, WIN.y1 - WIN.y0], [WIN.x1, (WIN.y0 + WIN.y1) / 2, 0.06, WIN.y1 - WIN.y0], [(WIN.x0 + WIN.x1) / 2, (WIN.y0 + WIN.y1) / 2, 0.04, WIN.y1 - WIN.y0]])
    mesh(new THREE.BoxGeometry(w, h, 0.08), frameM, x, y, WIN.z - 0.02, scene);
  const glassM = new THREE.MeshPhysicalMaterial({color: '#bcd4ea', transparent: true, opacity: 0.22, roughness: 0.05});
  const pane = mesh(new THREE.PlaneGeometry(WIN.x1 - WIN.x0, WIN.y1 - WIN.y0), glassM, (WIN.x0 + WIN.x1) / 2, (WIN.y0 + WIN.y1) / 2, WIN.z - 0.03, scene);
  const outT = canvasTex(256, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#7fa8d8'); gr.addColorStop(1, '#d8e6f2'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.fillStyle = '#b9a58c'; g.fillRect(150, 90, 106, 166); g.fillStyle = '#6d7d8c'; for (let y = 105; y < 250; y += 36) for (let x = 162; x < 250; x += 30) g.fillRect(x, y, 16, 22); });
  const outside = mesh(new THREE.PlaneGeometry(3, 2.2), new THREE.MeshBasicMaterial({map: outT}), 0.45, 1.6, -2.6, scene);
  // Muschelwand draußen (ab dem Bersten sieht man durchs Fenster nur noch Muscheln)
  const hT = heapTex(5, 1024, 6000); hT.repeat.set(3, 3);
  const heapM = new THREE.MeshStandardMaterial({map: hT, roughness: 0.75, color: '#d8d8dc'});
  const outHeap = mesh(new THREE.PlaneGeometry(3, 2.4), heapM, 0.45, 1.5, -1.75, scene); outHeap.visible = false;
  // LED-Streifen, Regal mit Figuren, Poster
  const ledM = new THREE.MeshBasicMaterial({color: '#b35cff'});
  mesh(new THREE.BoxGeometry(4.4, 0.025, 0.02), ledM, 0, 2.35, WIN.z + 0.01, scene);
  const shelfM = mat('#1a1820', {roughness: 0.5});
  const shelf = new THREE.Group(); scene.add(shelf); shelf.position.set(-0.55, 1.62, WIN.z + 0.12);
  mesh(new THREE.BoxGeometry(0.9, 0.03, 0.22), shelfM, 0, 0, 0, shelf);
  const toys = []; { const r = rng(5); for (let i = 0; i < 5; i++) { const t = new THREE.Group(); t.position.set(-0.36 + i * 0.18, 0.015, 0); shelf.add(t);
    const c = ['#ff5a7a', '#5ad1ff', '#ffd23a', '#8aff6a', '#ff9a3a'][i];
    mesh(new THREE.CylinderGeometry(0.035, 0.04, 0.1, 10), mat(c, {roughness: 0.4}), 0, 0.05, 0, t); mesh(new THREE.SphereGeometry(0.04, 12, 10), mat(c, {roughness: 0.4}), 0, 0.13, 0, t); toys.push(t); } }
  const posterT = canvasTex(256, 360, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, '#ff4fa3'); gr.addColorStop(1, '#5a2bff'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.fillStyle = 'rgba(255,255,255,0.85)'; g.font = 'bold 64px sans-serif'; g.textAlign = 'center'; g.fillText('EAT', w / 2, 140); g.fillText('LIVE', w / 2, 215); g.fillText('LOVE', w / 2, 290); });
  mesh(new THREE.PlaneGeometry(0.5, 0.7), new THREE.MeshStandardMaterial({map: posterT, roughness: 0.6}), -1.2, 1.55, WIN.z + 0.01, scene);
  // Schreibtisch, Stuhl, Mikrofonarm
  const deskM = mat('#121216', {roughness: 0.35}), padM = mat('#2a2a35', {roughness: 0.9});
  const desk = new THREE.Group(); scene.add(desk);
  mesh(new RoundedBoxGeometry(1.7, 0.05, 0.75, 2, 0.015), deskM, 0, 0.74, 0.2, desk);
  for (const x of [-0.8, 0.8]) mesh(new THREE.BoxGeometry(0.05, 0.72, 0.65), deskM, x, 0.36, 0.2, desk);
  mesh(new THREE.BoxGeometry(1.2, 0.004, 0.45), padM, 0, 0.768, 0.22, desk);
  const chair = new THREE.Group(); chair.position.set(0, 0, -0.55); scene.add(chair);
  const chairM = mat('#16161c', {roughness: 0.55}), chairR = mat('#d22b5a', {roughness: 0.55});
  mesh(new RoundedBoxGeometry(0.55, 0.1, 0.5, 2, 0.04), chairM, 0, 0.47, 0.1, chair); mesh(new RoundedBoxGeometry(0.55, 0.85, 0.1, 2, 0.04), chairM, 0, 0.95, -0.17, chair);
  mesh(new RoundedBoxGeometry(0.12, 0.6, 0.11, 2, 0.04), chairR, -0.16, 1.0, -0.12, chair); mesh(new RoundedBoxGeometry(0.12, 0.6, 0.11, 2, 0.04), chairR, 0.16, 1.0, -0.12, chair);
  mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.4, 8), chairM, 0, 0.22, 0.1, chair); mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.04, 5), chairM, 0, 0.04, 0.1, chair);
  const mic = new THREE.Group(); mic.position.set(-0.55, 0.77, 0.1); scene.add(mic);
  mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.55, 6), chairM, 0, 0.27, 0, mic).rotation.z = 0.25;
  const arm2 = mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.45, 6), chairM, 0.12, 0.6, -0.05, mic); arm2.rotation.z = -1.1;
  mesh(new THREE.CapsuleGeometry(0.035, 0.1, 4, 10), mat('#202028', {roughness: 0.4}), 0.32, 0.5, -0.08, mic).rotation.z = 0.3;
  // Ringlicht neben der Kamera (sichtbar in der weiten Einstellung)
  const ringG = new THREE.Group(); ringG.position.set(0.75, 0, 1.25); scene.add(ringG);
  mesh(new THREE.CylinderGeometry(0.012, 0.012, 1.45, 6), chairM, 0, 0.72, 0, ringG);
  const ringHead = new THREE.Group(); ringHead.position.y = 1.5; ringG.add(ringHead);
  mesh(new THREE.TorusGeometry(0.2, 0.025, 10, 40), new THREE.MeshBasicMaterial({color: '#fff8ee'}), 0, 0, 0, ringHead).rotation.y = 0.5;
  // Teller mit Eis, Austern, Zitrone
  const M = shellMats();
  const plate = new THREE.Group(); plate.position.set(0.05, 0.77, 0.24); scene.add(plate);
  mesh(new THREE.CylinderGeometry(0.2, 0.17, 0.025, 36), mat('#d9dde2', {metalness: 0.9, roughness: 0.25}), 0, 0.012, 0, plate);
  { const r = rng(12); const iceM = new THREE.MeshPhysicalMaterial({color: '#e8f4ff', roughness: 0.1, transmission: 0.4, thickness: 0.02});
    const ice = new THREE.InstancedMesh(new THREE.BoxGeometry(0.012, 0.008, 0.011), iceM, 200); const o = new THREE.Object3D();
    for (let i = 0; i < 200; i++) { const a = r() * 7, d = Math.sqrt(r()) * 0.18; o.position.set(Math.cos(a) * d, 0.024 + r() * 0.006, Math.sin(a) * d); o.rotation.set(r() * 3, r() * 3, r() * 3); o.scale.setScalar(0.6 + r()); o.updateMatrix(); ice.setMatrixAt(i, o.matrix); }
    plate.add(ice); }
  const oysters = []; for (let i = 0; i < 11; i++) { const a = i / 11 * Math.PI * 2, d = i % 2 ? 0.13 : 0.1; const o = oysterHalf(plate); o.position.set(Math.cos(a) * d, 0.03, Math.sin(a) * d); o.rotation.y = -a + Math.PI / 2; o.scale.setScalar(1.25); oysters.push(o); }
  const held = oysterHalf(scene); held.scale.setScalar(1.5);
  const lemonM = mat('#f3d530', {roughness: 0.5}), lemonIn = mat('#fff3a8', {roughness: 0.6});
  const lemon = new THREE.Group(); scene.add(lemon);
  mesh(new THREE.SphereGeometry(0.035, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2), lemonM, 0, 0, 0, lemon).scale.y = 0.9;
  mesh(new THREE.CircleGeometry(0.034, 14), lemonIn, 0, 0.001, 0, lemon).rotation.x = -Math.PI / 2;
  // Streamer (Hoodie, Headset)
  const guy = makePerson(1101, {skin: '#e2b28c', top: '#ff7a3d', pants: '#22262e', hair: '#2a1d15', height: 1.0});
  scene.add(guy); addMouth(guy);
  const hs = mesh(new THREE.TorusGeometry(0.13, 0.014, 8, 24, Math.PI), mat('#111', {roughness: 0.4}), 0, 0.08, -0.005, guy.userData.head);
  for (const s of [-1, 1]) mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.03, 16), mat('#111'), s * 0.13, 0.05, 0, guy.userData.head).rotation.z = Math.PI / 2;
  // Zitronensaft (Tropfen) und Glassplitter
  const juice = particles(160, 'spark');
  const shards = new THREE.InstancedMesh(new THREE.BoxGeometry(0.06, 0.04, 0.004), glassM.clone(), 60); shards.material.opacity = 0.55; shards.frustumCulled = false; scene.add(juice, shards);
  // Muschelflut: Schwarm, Oberfläche
  const N = 7200; const swarm = shellSwarm(N, scene, {scale: 1.5});
  const flood = new THREE.Group(); scene.add(flood);
  const surfT = heapTex(8, 1024, 6000); surfT.repeat.set(4, 4);
  const surf = mesh(new THREE.PlaneGeometry(4.6, 4.6, 60, 60), new THREE.MeshStandardMaterial({map: surfT, roughness: 0.7, color: '#d6d6da'}), 0, 0, 0.6, flood);
  surf.rotation.x = -Math.PI / 2; surf.castShadow = false;
  { const p = surf.geometry.attributes.position; const r = rng(3); for (let i = 0; i < p.count; i++) p.setZ(i, (r() - 0.5) * 0.04 + 0.03 * Math.sin(p.getX(i) * 5) * Math.cos(p.getY(i) * 4)); surf.geometry.computeVertexNormals(); }
  // Bahndaten der Muscheln (Start im Fenster, Flug ins Zimmer)
  const R = rng(77); const flight = [];
  for (let i = 0; i < N; i++) {
    const u = i / N, tb = WINDOW + 0.05 + Math.pow(u, 0.9) * (77.4 - WINDOW);
    const p0 = V3(lerp(WIN.x0 + 0.05, WIN.x1 - 0.05, R()), lerp(WIN.y0 + 0.05, WIN.y1 - 0.05, R()), WIN.z + 0.05);
    const v = V3((R() - 0.6) * 2.4, 0.4 + R() * 1.6, 1.6 + R() * 3.2);
    flight.push({tb, p0, v, rx: R() * 6, ry: R() * 6, rz: R() * 6, spin: (R() - 0.5) * 18, jit: R()});
  }
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 60); scene.add(camera);
  const smokeD = particles(160, 'smoke'); scene.add(smokeD);
  const o3 = new THREE.Object3D();

  return {scene, camera, update(shot, T) {
    const id = shot.id, t = T - shot.t0, gu = guy.userData;
    const L = level(T);
    // ---- Streamer ----
    guy.position.set(0, 0, -0.42); guy.rotation.set(0, 0, 0); seat(guy, 0.52); guy.visible = true;
    mouthOpen(guy, 0); brows(guy, 0, 0); gu.head.rotation.set(0, 0, 0); gu.torso.rotation.set(0, 0, 0);
    gu.armL.rotation.set(-0.55, 0, -0.12); gu.armL.userData.fore.rotation.x = -1.0; gu.armR.rotation.set(-0.55, 0, 0.12); gu.armR.userData.fore.rotation.x = -1.0;
    held.visible = false; lemon.position.set(0.26, 0.775, 0.28); lemon.rotation.set(0, 0, 0);
    oysters.forEach(o => { o.visible = T < VANISH; });
    const handR = () => { guy.updateMatrixWorld(true); return gu.armR.userData.fore.localToWorld(V3(0, -0.3, 0.02)); };
    const handL = () => { guy.updateMatrixWorld(true); return gu.armL.userData.fore.localToWorld(V3(0, -0.3, 0.02)); };
    if (T < 17) {
      // Auster greifen (4.6-5.4), zeigen (5.6-8.2), zum Mund (8.4-9.7), Kopf in den Nacken, schlürfen
      const grab = smooth(4.6, 5.3, T), show = smooth(5.5, 6.2, T) * (1 - smooth(8.3, 8.9, T)), toM = smooth(8.4, 9.7, T);
      gu.armR.rotation.x = lerp(-0.55, -0.95, grab) - show * 0.55 - toM * 0.95; gu.armR.rotation.z = 0.12 - show * 0.25 + toM * 0.28;
      gu.armR.userData.fore.rotation.x = lerp(-1.0, -0.6, grab) - show * 0.7 - toM * 1.2;
      const back = smooth(9.3, 9.9, T) * (1 - smooth(11.2, 11.8, T));
      gu.head.rotation.x = -0.45 * back; gu.torso.rotation.x = -0.1 * back;
      const slurp = T > 9.7 && T < 11.3 ? 0.5 + 0.5 * Math.abs(Math.sin((T - 9.7) * 9)) : 0;
      mouthOpen(guy, Math.max(smooth(8.9, 9.5, T) * (T < 11.3 ? 1 : 0) * 0.7, slurp));
      brows(guy, smooth(5.5, 6, T) * (1 - smooth(8, 8.5, T)) * 0.7, 0);
      if (T > 4.85 && T < VANISH) { held.visible = true; const h = handR(); held.position.copy(h).add(V3(-0.02, 0.03, 0.06)); held.rotation.set(0.9 * show - toM * 0.9, 0.3, 0.2); }
      if (T < 4.85) oysters[0].visible = T < VANISH;
      else oysters[0].visible = false;
      // Verwirrt auf die leere Hand schauen
      const conf = smooth(11.2, 11.7, T) * (1 - smooth(LEMON - 0.3, LEMON, T));
      if (T > 11.2) { gu.armR.rotation.x = lerp(gu.armR.rotation.x, -1.5, conf); gu.armR.userData.fore.rotation.x = lerp(gu.armR.userData.fore.rotation.x, -1.2, conf); gu.head.rotation.x += 0.35 * conf; brows(guy, conf, 0); mouthOpen(guy, 0.3 * conf); }
      // Zitrone: linke Hand nimmt sie (11.6-12.1) und drückt (LEMON) – der Saft spritzt ins Auge
      const lg = smooth(11.5, 12.0, T), sq = smooth(12.0, LEMON, T);
      if (T > 11.5) { gu.armL.rotation.x = lerp(-0.55, -1.3, lg) - sq * 0.4; gu.armL.rotation.z = -0.12 + sq * 0.35; gu.armL.userData.fore.rotation.x = lerp(-1.0, -1.1, lg) - sq * 0.4;
        const h = handL(); if (T > 11.8) { lemon.position.copy(h).add(V3(0.0, 0.03, 0.03)); lemon.rotation.set(-1.2 * sq, 0, -0.4 * sq); } }
      // Auge zu, Hände vors Gesicht, wippen
      const pain = smooth(LEMON + 0.1, LEMON + 0.5, T);
      if (pain > 0) { gu.armL.rotation.x = lerp(gu.armL.rotation.x, -2.2, pain); gu.armL.rotation.z = lerp(gu.armL.rotation.z, 0.5, pain); gu.armL.userData.fore.rotation.x = lerp(gu.armL.userData.fore.rotation.x, -1.6, pain);
        gu.armR.rotation.x = lerp(gu.armR.rotation.x, -2.0, pain); gu.armR.rotation.z = lerp(gu.armR.rotation.z, -0.35, pain); gu.armR.userData.fore.rotation.x = lerp(gu.armR.userData.fore.rotation.x, -1.7, pain);
        gu.torso.rotation.x = pain * (0.15 + 0.12 * Math.sin(T * 9)); gu.torso.rotation.z = pain * 0.12 * Math.sin(T * 5); mouthOpen(guy, pain * (0.6 + 0.3 * Math.sin(T * 13))); brows(guy, 0.6 * pain, 0); }
    }
    // Saft: gelbe Tropfen fliegen zum rechten Auge (eigene Kurve)
    { const P = juice.geometry.attributes.position.array, C = juice.geometry.attributes.aColor.array, S = juice.geometry.attributes.aSize.array; const r = rng(4);
      const a0 = (T > 11.8 && T < LEMON + 1.2) ? handL().add(V3(0, 0.05, 0.03)) : null; guy.updateMatrixWorld(true); const eye = gu.head.localToWorld(V3(0.04, 0.08, 0.11));
      for (let i = 0; i < 160; i++) { const d = LEMON + r() * 0.25, u = clamp((T - d) / 0.28), live = a0 && T > d && T < d + 0.6;
        const p = live ? V3().lerpVectors(a0, eye.clone().add(V3((r() - 0.5) * 0.05, (r() - 0.5) * 0.04, 0.02)), u).add(V3(0, Math.sin(u * Math.PI) * 0.08, 0)) : V3(0, -99, 0);
        P[i * 3] = p.x; P[i * 3 + 1] = p.y; P[i * 3 + 2] = p.z; S[i] = 0.006 + r() * 0.006; C[i * 4] = 1; C[i * 4 + 1] = 0.95; C[i * 4 + 2] = 0.4; C[i * 4 + 3] = live ? (u < 1 ? 0.9 : 0.9 * (1 - clamp((T - d - 0.28) / 0.3))) : 0; }
      juice.geometry.attributes.position.needsUpdate = juice.geometry.attributes.aColor.needsUpdate = juice.geometry.attributes.aSize.needsUpdate = true; }

    // ---- Rückkehr: Rumpeln, Fenster birst, Flut ----
    const rumble = smooth(60.3, 62.5, T) * (T < 78 ? 1 : 0);
    toys.forEach((ty, i) => { const k = T > WINDOW ? 1 : 0; ty.rotation.z = rumble * 0.12 * Math.sin(T * 31 + i * 2); ty.position.y = 0.015 + rumble * 0.008 * Math.abs(Math.sin(T * 27 + i)); ty.visible = L < 1.55 || k === 0; });
    shelf.position.x = -0.55 + rumble * 0.004 * Math.sin(T * 40);
    pane.visible = T < WINDOW; outHeap.visible = T >= WINDOW; outside.visible = T < WINDOW;
    if (id === 'back') {
      const sad = smooth(58.2, 59.2, T) * (1 - smooth(61.0, 61.4, T));
      gu.torso.rotation.x = 0.25 * sad; gu.head.rotation.x = 0.3 * sad; gu.armL.rotation.x = -0.9; gu.armR.rotation.x = -0.9; gu.armL.userData.fore.rotation.x = -1.4; gu.armR.userData.fore.rotation.x = -1.4; brows(guy, 0.3 * sad, 0); mouthOpen(guy, 0.15 * sad);
      const turn = smooth(61.0, 61.6, T); gu.torso.rotation.y = 0.9 * turn; gu.head.rotation.y = 0.6 * turn; brows(guy, turn, 0); mouthOpen(guy, 0.2 + 0.6 * smooth(62.4, 62.8, T));
      // Getroffen: kippt mit dem Stuhl nach hinten
      const hit = smooth(63.0, 64.2, T);
      if (hit > 0) { unseat(guy); posePerson(guy, {fall: hit, fallDir: 1, armsUp: 0.6 * hit}); guy.rotation.y = 0; guy.position.set(0, 0.3 * (1 - hit), -0.42 - 0.25 * hit); addMouth(guy); mouthOpen(guy, 0.9); chair.rotation.x = -1.4 * easeIn(hit); chair.position.y = 0.0; }
      else chair.rotation.x = 0;
    } else chair.rotation.x = 0;
    if (id === 'fill') { // er strampelt oben auf den Muscheln, versinkt dann
      unseat(guy); posePerson(guy, {armsUp: 0.75 + 0.25 * Math.sin(T * 7)}); addMouth(guy);
      const sink = smooth(73.2, BURIED, T);
      guy.position.set(-0.25 + 0.15 * Math.sin(T * 0.8), L - 1.0 - sink * 1.1, 0.05); guy.rotation.set(0.1 * Math.sin(T * 3), 0.35 + 0.2 * Math.sin(T * 1.3), 0.12 * Math.sin(T * 4));
      gu.armL.rotation.x = -0.6 + 0.6 * Math.sin(T * 8); gu.armR.rotation.x = -0.6 + 0.6 * Math.sin(T * 8 + 2); mouthOpen(guy, 0.7 + 0.3 * Math.sin(T * 11)); brows(guy, 1, 0);
      if (T > BURIED + 0.3) guy.visible = false;
    }
    if (id === 'intro' || id === 'wait' || id === 'slurp') chair.rotation.x = 0;
    ringHead.rotation.z = 0; ringG.rotation.x = -1.45 * easeIn(smooth(70.2, 71.0, T)); ringG.visible = L < 2.0;
    // Glassplitter
    { const r = rng(6); for (let i = 0; i < 60; i++) { const dt = T - WINDOW; const v = V3((r() - 0.5) * 2, 0.5 + r() * 1.5, 1 + r() * 3);
        if (dt > 0 && dt < 1.5) { o3.position.set(lerp(WIN.x0, WIN.x1, r()) + v.x * dt, lerp(WIN.y0, WIN.y1, r()) + v.y * dt - 4.9 * dt * dt, WIN.z + v.z * dt); o3.rotation.set(dt * 9 * r(), dt * 7, r()); o3.scale.setScalar(o3.position.y > L ? 1 : 0.0001); }
        else { o3.position.set(0, -99, 0); o3.scale.setScalar(0.0001); r(); r(); r(); r(); r(); }
        o3.updateMatrix(); shards.setMatrixAt(i, o3.matrix); } shards.instanceMatrix.needsUpdate = true; }
    // Muschel-Schwarm
    const live = T >= WINDOW && T < 78;
    for (let i = 0; i < N; i++) {
      const f = flight[i]; const dt = T - f.tb;
      if (!live || dt < 0) { swarm.hide(i); continue; }
      // Landezeit: y0 + vy t - 4.9 t^2 = Lland
      const Ll = level(f.tb + 0.5) + 0.02; const a = 4.9, b = -f.v.y, c = Ll - f.p0.y; const tl = (-b + Math.sqrt(Math.max(0, b * b - 4 * a * c))) / (2 * a);
      let x = f.p0.x + f.v.x * Math.min(dt, tl), z = f.p0.z + f.v.z * Math.min(dt, tl), y;
      x = clamp(x, -2.15, 2.15); z = clamp(z, WIN.z + 0.1, 2.9);
      if (dt < tl) { y = f.p0.y + f.v.y * dt - a * dt * dt; swarm.set(i, x, y, z, f.rx + dt * f.spin, f.ry + dt * f.spin * 0.7, f.rz, 1); }
      else { y = Math.max(Ll, L) + f.jit * 0.03; if (y > L + 0.06) y = L + f.jit * 0.03; swarm.set(i, x, y, z, f.rx * 0.2, f.ry, f.rz * 0.2, 1); }
    }
    swarm.commit(); swarm.visible = live;
    flood.visible = L > 0.005 && T < 78; surf.position.y = L;
    updateParticles(smokeD, T > WINDOW && T < 78 ? [{type: 'smoke', pos: V3(0.45, 1.5, -1.2), r: 0.6, t0: WINDOW, size: 0.9, rise: 0.15, col: [0.7, 0.68, 0.66], alpha: 0.18, share: 1}] : [], T, V3(0.1, 0, 0.4));
    // ---- Kamera ----
    camera.fov = 50;
    let pos, tgt; const shake = (rumble * 0.012 + (T > WINDOW && T < 78 ? 0.01 : 0));
    if (id === 'intro' || id === 'wait' || id === 'slurp' || id === 'back') {
      pos = V3(0.02, 1.38, 1.75); tgt = V3(0, 1.08, -0.4);
      if (id === 'intro') { pos = V3(0.05, 1.45, 2.2); tgt = V3(0, 1.02, -0.4); }
      if (id === 'wait') { const k = smooth(3.5, 9.5, T); pos = V3(lerp(0.05, 0.02, k), lerp(1.45, 1.38, k), lerp(2.2, 1.75, k)); tgt = V3(0, lerp(1.02, 1.08, k), -0.4); }
      // Meme-Zoom auf sein Gesicht (zweimal: Luft schlürfen, Zitrone)
      if (id === 'slurp') { const z1 = smooth(11.0, 11.15, T) * (1 - smooth(11.9, 12.05, T)), z2 = smooth(LEMON + 0.25, LEMON + 0.4, T);
        const zz = Math.max(z1, z2 * (1 - smooth(15.6, 16.4, T))); camera.fov = 50 - 30 * zz; tgt = V3(0, lerp(1.08, 1.36, zz), -0.4); }
      if (id === 'back') { const w = smooth(62.8, 64.5, T); pos = V3(lerp(0.02, 0.6, w), lerp(1.38, 1.6, w), lerp(1.75, 2.4, w)); tgt = V3(lerp(0, 0.1, w), lerp(1.08, 0.9, w), -0.4); }
    } else { // fill
      const k = smooth(68, 77.6, T);
      pos = V3(lerp(0.6, 0.3, k), Math.min(2.85, Math.max(1.6, L + 0.62)), lerp(2.4, 2.1, k)); tgt = V3(lerp(-0.1, -0.2, k), Math.max(0.8, L - 0.1), lerp(-0.4, 0, k));
    }
    pos.add(V3(noise1(T * 3, 1) * shake, noise1(T * 3, 4) * shake, 0)); camera.position.copy(pos); camera.lookAt(tgt);
    camera.updateProjectionMatrix();
  }};
}
