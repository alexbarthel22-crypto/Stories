// Mensa, Spaghetti-Tag. intro/wait: Er dreht die größte Gabel seines Lebens.
// mensa (Stufe 1): Die Schwerkraft ist weg – Spaghetti, Soße, Tabletts und alle Leute schweben. Die Soße landet im Gesicht seines Kumpels.
// final: Nach dem Beben. Alles ist runtergekommen – nur sein Pudding klebt noch an der Decke und fällt ihm genau in die Hand.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {seat, unseat, addMouth, mouthOpen, brows} from './people.js';
import {particles, updateParticles} from './fx.js';
import {flail, noodleTex, strand, blob, wobble, Drift} from './float.js';
import {VANISH, SAUCE_HIT, PUD} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const CEIL = 3.4;

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.background = new THREE.Color('#e9ecef');
  const hemi = new THREE.HemisphereLight('#f6f8ff', '#8d7f6c', 1.0); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff1d8', 2.4); sun.position.set(-9, 7, 3); sun.target.position.set(0, 0, 0); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30}); scene.add(sun, sun.target);
  const fillL = new THREE.PointLight('#fff8ee', 8, 14, 1.3); fillL.position.set(1.5, 3.0, 1.5); scene.add(fillL);

  // ---------- Raum 14 x 14 m ----------
  const floorT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#c7c0b2'; g.fillRect(0, 0, w, h); const r = rng(4);
    for (let i = 0; i < 1400; i++) { g.fillStyle = `rgba(${80 + r() * 60},${70 + r() * 50},${60 + r() * 40},0.14)`; g.fillRect(r() * w, r() * h, 2 + r() * 4, 2 + r() * 4); }
    g.strokeStyle = 'rgba(0,0,0,0.13)'; g.lineWidth = 2; for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * 128, 0); g.lineTo(i * 128, h); g.moveTo(0, i * 128); g.lineTo(w, i * 128); g.stroke(); } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(7, 7);
  mesh(new THREE.PlaneGeometry(14, 14), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.55}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const wallM = mat('#f1efe6', {roughness: 0.95}), accent = mat('#f29e4c', {roughness: 0.9}), steel = mat('#9aa3ab', {metalness: 0.6, roughness: 0.35});
  mesh(new THREE.BoxGeometry(14, CEIL, 0.12), wallM, 0, CEIL / 2, -7, scene);
  mesh(new THREE.BoxGeometry(14, CEIL, 0.12), wallM, 0, CEIL / 2, 7, scene);
  mesh(new THREE.BoxGeometry(0.12, CEIL, 14), wallM, 7, CEIL / 2, 0, scene);
  mesh(new THREE.BoxGeometry(14, 1.1, 0.02), accent, 0, 0.55, 6.93, scene); mesh(new THREE.BoxGeometry(0.02, 1.1, 14), accent, 6.93, 0.55, 0, scene);
  const ceil = mesh(new THREE.BoxGeometry(14, 0.1, 14), mat('#f7f7f4'), 0, CEIL + 0.05, 0, scene); ceil.castShadow = false;
  // Fensterfront links
  mesh(new THREE.BoxGeometry(0.12, 0.8, 14), wallM, -7, 0.4, 0, scene); mesh(new THREE.BoxGeometry(0.12, 0.5, 14), wallM, -7, CEIL - 0.25, 0, scene);
  for (let z = -6.5; z <= 6.6; z += 2.6) mesh(new THREE.BoxGeometry(0.16, CEIL, 0.18), mat('#dad6cc'), -7, CEIL / 2, z, scene);
  const outT = canvasTex(1024, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#8fc0ee'); gr.addColorStop(1, '#e8f2fa'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(9); for (let i = 0; i < 50; i++) { g.fillStyle = `rgb(${55 + r() * 40},${115 + r() * 50},${55 + r() * 30})`; g.beginPath(); g.arc(r() * w, h * 0.72 + r() * 70, 26 + r() * 50, 0, 7); g.fill(); } });
  mesh(new THREE.PlaneGeometry(14, 2.4), new THREE.MeshBasicMaterial({map: outT}), -7.5, 1.95, 0, scene).rotation.y = Math.PI / 2;
  // Deckenleuchten
  const lampM = mat('#ffffff', {emissive: '#fffaf0', emissiveIntensity: 1.4});
  const lamps = [];
  for (const x of [-4.5, -1.5, 1.5, 4.5]) for (const z of [-4.5, -1.5, 1.5, 4.5]) { const l = mesh(new THREE.BoxGeometry(1.2, 0.05, 0.3), lampM, x, CEIL - 0.03, z, scene); l.castShadow = false; lamps.push(l); }
  // Essensausgabe hinten
  const counter = new THREE.Group(); counter.position.set(0, 0, -6.3); scene.add(counter);
  mesh(new THREE.BoxGeometry(8, 0.95, 0.8), steel, 0, 0.475, 0, counter); mesh(new THREE.BoxGeometry(8, 0.05, 0.4), mat('#cfd5da', {metalness: 0.7, roughness: 0.2}), 0, 1.35, 0.1, counter);
  for (let i = 0; i < 6; i++) mesh(new THREE.BoxGeometry(0.6, 0.15, 0.35), mat(['#d8432f', '#e9c46a', '#7fa650', '#d8432f', '#c07a3c', '#e9c46a'][i]), -3 + i * 1.2, 1.0, 0, counter);
  const signT = canvasTex(1024, 192, (g, w, h) => { g.fillStyle = '#2f3a45'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.font = '700 92px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('HEUTE: SPAGHETTI 🍝', w / 2, h / 2 + 4); });
  mesh(new THREE.PlaneGeometry(3.6, 0.68), new THREE.MeshStandardMaterial({map: signT, roughness: 0.6}), 0, 2.45, -6.93, scene);

  // ---------- Tische, Bänke, Tabletts ----------
  const wood = mat('#d9c09a', {roughness: 0.55}), legM = mat('#5f6870', {metalness: 0.5, roughness: 0.4});
  const trayCols = ['#2f8f6b', '#d8432f', '#3f6fb5', '#e9a23b'];
  const nT = noodleTex(); const noodleM = new THREE.MeshStandardMaterial({map: nT, roughness: 0.55});
  const plateM = mat('#fbfbf8', {roughness: 0.3}), sauceC = '#b8261a';
  const drifts = []; const tables = []; const r = rng(17);
  function trayWith(x, z, rotY, big = false) {
    const g = new THREE.Group(); g.position.set(x, 0.775, z); g.rotation.y = rotY; scene.add(g);
    mesh(new RoundedBoxGeometry(0.46, 0.02, 0.34, 2, 0.008), mat(trayCols[Math.floor(r() * 4)], {roughness: 0.4}), 0, 0, 0, g);
    mesh(new THREE.CylinderGeometry(0.13, 0.1, 0.025, 24), plateM, -0.05, 0.022, 0, g);
    const nest = mesh(new THREE.SphereGeometry(0.085, 16, 10), noodleM, -0.05, 0.05, 0, g); nest.scale.set(1, 0.42, 1);
    if (!big) for (let k = 0; k < 2; k++) mesh(new THREE.SphereGeometry(0.02, 10, 8), mat('#6b3a22', {roughness: 0.7}), -0.07 + k * 0.04, 0.075, 0.02, g);
    const cup = mesh(new THREE.CylinderGeometry(0.035, 0.03, 0.1, 16), mat(r() < 0.5 ? '#e5edf3' : '#d8432f', {roughness: 0.4}), 0.15, 0.06, -0.08, g);
    const drink = blob(r() < 0.5 ? '#3a1d10' : '#f2a33a', 0.03); drink.material.transparent = true; drink.material.opacity = 0.85; g.add(drink); drink.position.set(0.15, 0.1, -0.08); drink.visible = false;
    return {g, cup, nest, drink, s: r() * 9, vy: 0.04 + r() * 0.05};
  }
  for (const tx of [-3.2, 0, 3.2]) {
    const t = new THREE.Group(); t.position.set(tx, 0, 0); scene.add(t); tables.push(t);
    mesh(new THREE.BoxGeometry(1.0, 0.05, 6.4), wood, 0, 0.75, 0, t);
    for (const z of [-2.9, 2.9]) for (const x of [-0.35, 0.35]) mesh(new THREE.BoxGeometry(0.05, 0.73, 0.05), legM, x, 0.365, z, t);
    for (const s of [-1, 1]) { const b = new THREE.Group(); b.position.set(tx + s * 0.78, 0, 0); scene.add(b); mesh(new THREE.BoxGeometry(0.35, 0.05, 6.2), wood, 0, 0.45, 0, b); for (const z of [-2.8, 2.8]) mesh(new THREE.BoxGeometry(0.05, 0.43, 0.05), legM, 0, 0.215, z, b); }
  }
  // ---------- Leute ----------
  const people = [];
  const GX = 0.78, GZ = 0.0; // er: rechts am mittleren Tisch, Blick nach -x
  const FX = -0.78, FZ = 0.0; // sein Kumpel gegenüber
  for (const tx of [-3.2, 0, 3.2]) for (const s of [-1, 1]) for (const z of [-2.4, -1.2, 0, 1.2, 2.4]) {
    const x = tx + s * 0.78;
    if (Math.abs(x - GX) < 0.01 && z === GZ) continue;
    if (Math.abs(x - FX) < 0.01 && z === FZ) continue;
    if (r() < 0.25) continue;
    const p = makePerson(800 + people.length * 11, {height: 0.95 + r() * 0.08, longHair: r() < 0.45, ponytail: r() < 0.15}); addMouth(p); scene.add(p);
    const tr = trayWith(tx + s * 0.25, z, 0);
    people.push({p, x, z, face: -s, vy: 0.05 + r() * 0.12, vx: (r() - 0.5) * 0.08, vz: (r() - 0.5) * 0.08, spin: (r() - 0.5) * 0.5, seed: r() * 10, tr});
    drifts.push(new Drift(tr.g, V3((r() - 0.5) * 0.05, 0.03 + r() * 0.08, (r() - 0.5) * 0.05), V3((r() - 0.5) * 0.4, (r() - 0.5) * 0.6, (r() - 0.5) * 0.4), VANISH));
  }
  // Einer hatte gerade gejubelt (Sprung) – er segelt direkt zur Decke
  const jumper = makePerson(3301, {top: '#7b4fa0', height: 1.02}); addMouth(jumper); scene.add(jumper);
  // Er und sein Kumpel
  const guy = makePerson(1207, {skin: '#e2b28c', top: '#ff7a3d', pants: '#22262e', hair: '#2a1d15', height: 1.0}); addMouth(guy); scene.add(guy);
  const fr = makePerson(1331, {skin: '#c99068', top: '#3f6fb5', pants: '#2b2f3a', hair: '#111', height: 1.0}); addMouth(fr); scene.add(fr);
  for (const s of [-1, 1]) mesh(new THREE.TorusGeometry(0.026, 0.005, 6, 16), mat('#111'), s * 0.042, 0.08, 0.112, fr.userData.head); // Brille
  // Aufsicht mit Kaffeetasse
  const tea = makePerson(2209, {skin: '#f0c7a8', top: '#a04a5a', pants: '#3a3f4a', hair: '#b8b8b8', height: 1.05}); addMouth(tea); scene.add(tea);
  const mug = mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.1, 16), mat('#fbfbf8'), 0, 0, 0, scene);
  const coffee = blob('#4a2a14', 0.035); scene.add(coffee);
  // Sein Tablett: Riesenteller Spaghetti, Gabel mit Riesenknäuel, Soße, Cola, Pudding
  const mine = trayWith(0.28, 0, 0, true);
  const sauce = blob(sauceC, 0.045); scene.add(sauce);
  const fork = new THREE.Group(); scene.add(fork);
  mesh(new THREE.BoxGeometry(0.012, 0.2, 0.006), mat('#c9ccd1', {metalness: 0.9, roughness: 0.2}), 0, -0.1, 0, fork);
  const ball = mesh(new THREE.SphereGeometry(0.055, 16, 12), noodleM, 0, 0.01, 0, fork);
  const forkStrands = [0, 1, 2, 3].map(i => { const s = strand(40 + i, 0.16); s.position.set((i - 1.5) * 0.02, -0.07, 0); fork.add(s); return s; });
  const pudding = new THREE.Group(); scene.add(pudding);
  mesh(new THREE.CylinderGeometry(0.04, 0.032, 0.07, 18), mat('#f6f1e6', {roughness: 0.4}), 0, 0, 0, pudding);
  mesh(new THREE.CylinderGeometry(0.038, 0.038, 0.006, 18), mat('#5b3216', {roughness: 0.35}), 0, 0.033, 0, pudding);
  const spoon = mesh(new THREE.BoxGeometry(0.008, 0.12, 0.004), mat('#c9ccd1', {metalness: 0.9, roughness: 0.2}), 0.01, 0.06, 0, pudding); spoon.rotation.z = 0.3;
  // schwebende Extras: einzelne Spaghetti, Fleischbällchen, Soßentropfen
  const extras = [];
  for (let i = 0; i < 26; i++) { const s = strand(100 + i, 0.22 + r() * 0.15); s.position.set(lerp(-3.8, 3.8, r()), 0.85 + r() * 0.2, lerp(-2.8, 2.8, r())); scene.add(s);
    extras.push({o: s, d: new Drift(s, V3((r() - 0.5) * 0.1, 0.08 + r() * 0.2, (r() - 0.5) * 0.1), V3(r() * 0.8, r() * 0.8, r() * 0.8), VANISH), kind: 's'}); }
  for (let i = 0; i < 18; i++) { const b = blob(i % 3 ? sauceC : '#6b3a22', 0.012 + r() * 0.02); b.position.set(lerp(-3.8, 3.8, r()), 0.85, lerp(-2.8, 2.8, r())); scene.add(b);
    extras.push({o: b, d: new Drift(b, V3((r() - 0.5) * 0.12, 0.1 + r() * 0.22, (r() - 0.5) * 0.12), V3(0, 0, 0), VANISH), kind: 'b', seed: i}); }
  // Nahe bei ihm: ein paar Spaghetti direkt im Bild
  for (let i = 0; i < 10; i++) { const s = strand(300 + i, 0.25); s.position.set(0.1 + r() * 0.4, 0.86, -0.25 + r() * 0.5); scene.add(s);
    extras.push({o: s, d: new Drift(s, V3((r() - 0.5) * 0.08, 0.12 + r() * 0.12, (r() - 0.5) * 0.08), V3(r(), r(), r()), VANISH), kind: 's'}); }

  // Krümel (Brot, Croutons) und lose Stühle, die driften
  const crumbG = new THREE.BufferGeometry(); const crumbN = 600, crumbP0 = new Float32Array(crumbN * 3), crumbV = new Float32Array(crumbN * 3);
  for (let i = 0; i < crumbN; i++) { crumbP0.set([lerp(-3.8, 3.8, r()), 0.79 + r() * 0.05, lerp(-2.9, 2.9, r())], i * 3); crumbV.set([(r() - 0.5) * 0.05, 0.02 + r() * 0.12, (r() - 0.5) * 0.05], i * 3); }
  crumbG.setAttribute('position', new THREE.BufferAttribute(new Float32Array(crumbN * 3), 3));
  const crumbs = new THREE.Points(crumbG, new THREE.PointsMaterial({color: '#c9a46a', size: 0.012, sizeAttenuation: true})); crumbs.frustumCulled = false; scene.add(crumbs);
  const chairs = []; for (let i = 0; i < 7; i++) { const c = new THREE.Group(); const x = [-4.6, -1.6, 1.6, 4.6, -4.6, 4.6, 1.6][i], z = [-3.6, 3.5, -3.6, 3.4, 1.2, -1.0, 3.6][i]; c.position.set(x, 0, z); scene.add(c);
    const cm = mat(['#e86f2c', '#2f8f6b', '#3f6fb5'][i % 3], {roughness: 0.5}); mesh(new THREE.BoxGeometry(0.42, 0.04, 0.42), cm, 0, 0.45, 0, c); mesh(new THREE.BoxGeometry(0.42, 0.4, 0.04), cm, 0, 0.68, -0.2, c);
    for (const [a, b] of [[-0.18, -0.18], [0.18, -0.18], [-0.18, 0.18], [0.18, 0.18]]) mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.45, 6), legM, a, 0.225, b, c);
    chairs.push({c, v: V3((r() - 0.5) * 0.12, 0.04 + r() * 0.1, (r() - 0.5) * 0.12), w: V3((r() - 0.5) * 0.4, (r() - 0.5) * 0.6, (r() - 0.5) * 0.4), p0: c.position.clone(), r0: r() * 6}); }
  // Decke über dem Pudding: Soßenflecken, klebende Spaghetti, ein Tablett, Lampe
  const ceilMess = new THREE.Group(); scene.add(ceilMess);
  const splatT = canvasTex(256, 256, (g, w, h) => { const R = rng(13); g.clearRect(0, 0, w, h); g.fillStyle = 'rgba(140,32,20,0.92)'; g.beginPath(); g.arc(128, 128, 46, 0, 7); g.fill();
    for (let i = 0; i < 9; i++) { const a = R() * 7, d = 34 + R() * 30, rr = 6 + R() * 12; g.beginPath(); g.arc(128 + Math.cos(a) * d, 128 + Math.sin(a) * d, rr, 0, 7); g.fill(); g.lineWidth = rr * 0.8; g.strokeStyle = 'rgba(140,32,20,0.92)'; g.beginPath(); g.moveTo(128, 128); g.lineTo(128 + Math.cos(a) * d, 128 + Math.sin(a) * d); g.stroke(); }
    g.fillStyle = 'rgba(255,190,170,0.25)'; g.beginPath(); g.arc(112, 112, 16, 0, 7); g.fill(); });
  for (let i = 0; i < 6; i++) { const sp = mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshStandardMaterial({map: splatT, transparent: true, depthWrite: false, roughness: 0.3}), (r() - 0.5) * 1.3, -0.003 - i * 0.0005, (r() - 0.5) * 1.3, ceilMess); sp.rotation.set(Math.PI / 2, 0, r() * 6); sp.scale.setScalar(0.14 + r() * 0.16); sp.castShadow = false; }
  for (let i = 0; i < 14; i++) { const st = strand(700 + i, 0.25 + r() * 0.2); st.position.set((r() - 0.5) * 1.2, -0.02 - r() * 0.12, (r() - 0.5) * 1.2); st.rotation.set(Math.PI / 2 * (0.6 + r() * 0.5), r() * 3, 0); ceilMess.add(st); }
  { const tr = mesh(new RoundedBoxGeometry(0.46, 0.02, 0.34, 2, 0.008), mat('#d8432f', {roughness: 0.4}), 0.55, -0.012, -0.35, ceilMess); tr.rotation.y = 0.5;
    for (let k = 0; k < 3; k++) mesh(new THREE.SphereGeometry(0.022, 10, 8), mat('#6b3a22', {roughness: 0.7}), -0.4 + k * 0.08, -0.025, 0.3 + k * 0.05, ceilMess); }
  const mlamp = mesh(new THREE.BoxGeometry(1.2, 0.05, 0.3), lampM, -0.5, -0.03, 0.45, ceilMess); mlamp.castShadow = false;
  // ---------- Finale: Chaos (nach dem Beben) ----------
  const mess = new THREE.Group(); scene.add(mess); mess.visible = false;
  const plaster = mat('#d9d6cf', {roughness: 1});
  for (let i = 0; i < 70; i++) { const s = 0.05 + r() * 0.25; const m = mesh(new THREE.DodecahedronGeometry(s, 0), plaster, lerp(-5, 5, r()), s * 0.5, lerp(-4, 4, r()), mess); m.rotation.set(r() * 3, r() * 3, r() * 3); m.scale.y = 0.4; }
  for (let i = 0; i < 40; i++) { const b = mesh(new THREE.CircleGeometry(0.05 + r() * 0.14, 14), mat(sauceC, {roughness: 0.2}), lerp(-4.5, 4.5, r()), 0.004 + i * 0.0001, lerp(-3.5, 3.5, r()), mess); b.rotation.x = -Math.PI / 2; b.castShadow = false; }
  for (let i = 0; i < 24; i++) { const n = mesh(new THREE.SphereGeometry(0.08, 10, 8), noodleM, lerp(-4.5, 4.5, r()), 0.02, lerp(-3.5, 3.5, r()), mess); n.scale.set(1.4, 0.3, 1); }
  // Spaghetti-Hauben für die Köpfe
  const hat = () => { const h = mesh(new THREE.SphereGeometry(0.13, 14, 10, 0, Math.PI * 2, 0, Math.PI * 0.55), noodleM); h.castShadow = false; const g = new THREE.Group(); g.add(h); for (let k = 0; k < 5; k++) { const s = strand(500 + k, 0.18); s.position.set((k - 2) * 0.05, -0.05, 0.08 - (k % 2) * 0.16); g.add(s); } return g; };
  const guyHat = hat(); guy.userData.head.add(guyHat); guyHat.position.set(0, 0.09, -0.01); guyHat.visible = false;
  const frHat = hat(); fr.userData.head.add(frHat); frHat.position.set(0, 0.09, -0.01); frHat.visible = false;
  const splat = mesh(new THREE.SphereGeometry(0.09, 16, 10), new THREE.MeshPhysicalMaterial({color: sauceC, roughness: 0.15, clearcoat: 1}), 0, 0.05, 0.1, fr.userData.head); splat.scale.set(1, 0.85, 0.28); splat.visible = false; splat.castShadow = false;
  const dust = particles(500, 'smoke'); scene.add(dust);
  const fallenLamp = mesh(new THREE.BoxGeometry(1.2, 0.05, 0.3), lampM, 1.5, 2.3, 1.5, mess); fallenLamp.rotation.z = 0.9;

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 80); scene.add(camera);
  const headPos = (p, off = V3(0, 0.06, 0.08)) => { p.updateMatrixWorld(true); return p.userData.head.localToWorld(off.clone()); };
  const handPos = (p, side = 1) => { p.updateMatrixWorld(true); return (side < 0 ? p.userData.armL : p.userData.armR).userData.fore.localToWorld(V3(0, -0.29, 0)); };
  const FORK_UP = 0.55; // m/s – so schnell hebt er die Gabel, als die Schwerkraft verschwindet

  function poseGuy(T) {
    const u = guy.userData, dT = Math.max(0, T - VANISH), g0 = smooth(VANISH, VANISH + 0.6, T);
    unseat(guy); seat(guy, 0.47); guy.position.set(GX, guy.position.y, GZ); guy.rotation.set(0, -Math.PI / 2, 0);
      // Gabel drehen (rechte Hand), dann ab 9,4 s hochheben
      const lift = T < 9.4 ? 0 : T < VANISH ? (T - 9.4) / 0.6 * 0.22 : 0.22 + FORK_UP * dT;
      const tw = T < 9.4 ? Math.sin(T * 5) * 0.06 : 0;
      u.armR.rotation.set(-0.9 - Math.min(0.9, lift * 2.5) + tw, 0, 0.05); u.armR.userData.fore.rotation.x = -0.9 - Math.min(0.6, lift * 1.6);
      u.armL.rotation.set(-0.6, 0, -0.1); u.armL.userData.fore.rotation.x = -1.0;
      u.head.rotation.set(0.35 - Math.min(0.9, lift * 1.2), 0, 0); mouthOpen(guy, T > 8.6 && T < VANISH + 1.6 ? 0.85 : 0.1); brows(guy, T > VANISH ? 1 : 0.3, 0);
      if (dT > 0) { guy.position.y += 0.08 * dT * g0; guy.rotation.z = 0.03 * dT; }
      if (T > VANISH + 1.6) { const k = smooth(VANISH + 1.6, VANISH + 2.6, T); flail(guy, T, 5, k); u.head.rotation.x = lerp(u.head.rotation.x, -0.2, k); mouthOpen(guy, 0.6 + 0.3 * Math.sin(T * 9)); }
    return T < 9.4 ? Math.sin(T * 5) * 0.06 : 0;
  }
  return {scene, camera, update(shot, T) {
    const fin = shot.id === 'final';
    const g0 = smooth(VANISH, VANISH + 0.6, T) * (fin ? 0 : 1); // Schwerelosigkeit „sichtbar“
    const dT = Math.max(0, T - VANISH);
    mess.visible = fin; guyHat.visible = fin; frHat.visible = fin;
    // Licht im Finale: staubig, schräg, wärmer
    hemi.intensity = fin ? 0.55 : 1.0; sun.color.set(fin ? '#ffcf9a' : '#fff1d8'); sun.intensity = fin ? 2.0 : 2.4; scene.background.set(fin ? '#9b8a78' : '#e9ecef');
    lamps.forEach((l, i) => { l.material.emissiveIntensity = fin ? (i % 3 ? 0.1 : 0.9 + 0.5 * Math.sin(T * 23 + i)) : 1.4; l.visible = !(fin && (i === 9 || i === 6)); });
    // ---- Leute an den Tischen ----
    people.forEach((q, i) => { const p = q.p;
      unseat(p); seat(p, 0.47); p.rotation.set(0, q.face * Math.PI / 2, 0);
      const u = p.userData;
      u.armR.rotation.set(-0.9 + Math.sin(T * 3 + q.seed) * 0.05, 0, 0.1); u.armR.userData.fore.rotation.x = -0.8; u.armL.rotation.set(-0.7, 0, -0.1); u.armL.userData.fore.rotation.x = -0.9;
      u.head.rotation.set(0.25 + 0.05 * Math.sin(T * 0.7 + q.seed), 0.2 * Math.sin(T * 0.4 + q.seed), 0); mouthOpen(p, 0.2 * Math.max(0, Math.sin(T * 5 + q.seed)));
      p.position.x = q.x; p.position.z = q.z;
      if (fin) { // sitzen benommen am Boden, Spaghetti überall
        const rr = rng(i * 7 + 3); p.position.set(q.x + (rr() - 0.5) * 0.8, p.position.y - 0.42, q.z + (rr() - 0.5) * 0.6); p.rotation.y += (rr() - 0.5) * 2;
        u.legL.rotation.x = u.legR.rotation.x = -1.4; u.legL.userData.knee.rotation.x = u.legR.userData.knee.rotation.x = 0.15;
        u.pl.forEach((g, k) => { const lg = k ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
        u.head.rotation.set(0.1, 0.3 * Math.sin(T * 0.5 + q.seed), 0.1); brows(p, 0.7, 0); mouthOpen(p, 0.3);
        q.tr.g.visible = false; return; }
      q.tr.g.visible = true;
      if (dT > 0) { const k = g0; const d = dT;
        p.position.y += q.vy * d * k; p.position.x += q.vx * d * k; p.position.z += q.vz * d * k;
        p.rotation.z = q.spin * d * 0.3 * k; p.rotation.x = q.spin * d * 0.2 * k;
        flail(p, T, q.seed, smooth(VANISH + 0.3, VANISH + 1.3, T)); brows(p, k, 0); mouthOpen(p, 0.5 + 0.3 * Math.sin(T * 8 + q.seed) * k); }
    });
    drifts.forEach(d => { if (!fin) d.at(T); });
    people.forEach(q => { const d = q.tr.drink; d.visible = !fin && T > VANISH; if (d.visible) { d.position.set(0.15, 0.1 + q.tr.vy * dT, -0.08); wobble(d, T, q.tr.s); d.scale.multiplyScalar(smooth(VANISH, VANISH + 0.8, T)); } });
    { const P = crumbG.attributes.position.array; for (let i = 0; i < crumbN * 3; i++) P[i] = crumbP0[i] + crumbV[i] * dT; crumbG.attributes.position.needsUpdate = true; crumbs.visible = !fin; }
    chairs.forEach(ch => { if (fin) { ch.c.position.set(ch.p0.x, 0.0, ch.p0.z); ch.c.rotation.set(Math.PI / 2 * (ch.r0 > 3 ? 1 : 0), ch.r0, 0); if (ch.r0 > 3) ch.c.position.y = 0.21; return; }
      ch.c.position.copy(ch.p0).addScaledVector(ch.v, dT); ch.c.rotation.set(ch.w.x * dT, ch.r0 + ch.w.y * dT, ch.w.z * dT); });
    extras.forEach(e => { e.o.visible = !fin && T > VANISH; if (!fin) { e.d.at(T); if (e.kind === 'b') wobble(e.o, T, e.seed); } });
    // ---- Springer (jubelt bei 9,6 s, fliegt mit 1,1 m/s weiter nach oben) ----
    { const p = jumper; unseat(p); posePerson(p, {armsUp: 1}); p.rotation.set(0, 0.6, 0); const t0 = 9.6;
      const jy = T < t0 ? 0 : T < VANISH ? 1.1 * (T - t0) - 4.9 * (T - t0) ** 2 : 1.1 * (VANISH - t0) - 4.9 * (VANISH - t0) ** 2 + (1.1 - 9.8 * (VANISH - t0)) * (T - VANISH);
      p.position.set(-1.9, Math.min(CEIL - 1.95, Math.max(0, jy)), -3.9); p.visible = !fin;
      if (T > VANISH + 0.5) { flail(p, T, 4, 0.6); p.rotation.x = 0.2 * Math.sin(T); } mouthOpen(p, 0.8); brows(p, 1, 0); }
    // ---- Aufsicht mit Kaffee ----
    { const p = tea; unseat(p); posePerson(p, {}); p.position.set(-1.6, 0, -1.6); p.rotation.set(0, 0.8, 0); const u = p.userData;
      u.armR.rotation.set(-1.2, 0, 0.15); u.armR.userData.fore.rotation.x = -0.9;
      if (fin) { p.position.set(-1.4, -0.42, -1.4); seat(p, 0.0); p.position.y = -0.47; mouthOpen(p, 0.5); brows(p, 0, 1); mug.visible = false; coffee.visible = false; }
      else {
        if (dT > 0) { p.position.y += 0.06 * dT * g0; flail(p, T, 7, smooth(VANISH + 0.6, VANISH + 1.6, T) * 0.7); brows(p, 1, 0); mouthOpen(p, 0.6); }
        mug.visible = true; mug.position.copy(handPos(p)); mug.rotation.set(0, 0, 0);
        coffee.visible = T > VANISH; const cp = mug.position.clone().add(V3(0, 0.08 + 0.09 * dT, 0.02 * dT)); coffee.position.copy(cp); wobble(coffee, T, 3); coffee.scale.multiplyScalar(1 + 0.25 * smooth(VANISH, VANISH + 2, T)); }
    }
    // ---- Kumpel ----
    { const p = fr, u = p.userData; unseat(p); seat(p, 0.47); p.position.set(FX, p.position.y, FZ); p.rotation.set(0, Math.PI / 2, 0);
      u.armL.rotation.set(-0.8, 0, -0.1); u.armL.userData.fore.rotation.x = -1.0; u.armR.rotation.set(-0.7, 0, 0.2); u.armR.userData.fore.rotation.x = -1.2;
      u.head.rotation.set(0.05, 0, 0); mouthOpen(p, 0.25 * Math.max(0, Math.sin(T * 6))); brows(p, 0, 0);
      splat.visible = (T > SAUCE_HIT && !fin) || fin;
      if (fin) { p.position.set(-0.6, -0.0, 0.5); seat(p, 0.0); p.position.y = -0.47; p.rotation.set(0, 1.9, 0); u.legL.userData.knee.rotation.x = u.legR.userData.knee.rotation.x = 0.2; u.pl.forEach((g, k) => { const lg = k ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); }); brows(p, 0, 1); mouthOpen(p, 0.1); }
      else if (dT > 0) { p.position.y += 0.07 * dT * g0; p.rotation.z = -0.04 * dT; flail(p, T, 2, smooth(VANISH + 0.5, VANISH + 1.5, T) * (T < SAUCE_HIT ? 1 : 0.4)); brows(p, 1, 0); mouthOpen(p, T < SAUCE_HIT ? 0.7 : 0.15);
        if (T > SAUCE_HIT) { const k = smooth(SAUCE_HIT, SAUCE_HIT + 0.25, T); u.head.rotation.x = -0.35 * k * (1 - 0.5 * smooth(SAUCE_HIT + 0.6, SAUCE_HIT + 1.6, T)); u.armL.rotation.x = lerp(u.armL.rotation.x, -2.4, k); u.armR.rotation.x = lerp(u.armR.rotation.x, -2.4, k); u.armL.rotation.z = -0.4; u.armR.rotation.z = 0.4; } }
    }
    // ---- Er ----
    const u = guy.userData;
    if (!fin) {
      const tw = poseGuy(T), dT0 = dT;
      // Gabel: erst in der Hand, ab VANISH fliegt sie mit 0,55 m/s weiter nach oben
      const hp = handPos(guy);
      if (T < VANISH) { fork.position.copy(hp).add(V3(-0.03, 0.08, 0)); fork.rotation.set(0, 0, 0.25 + tw); }
      else { poseGuy(VANISH - 0.001); const p0 = handPos(guy).add(V3(-0.03, 0.08, 0)); poseGuy(T); fork.position.copy(p0).add(V3(-0.04 * dT, FORK_UP * dT, 0.01 * dT)); fork.rotation.set(0.3 * dT, 0.5 * dT, 0.25 + 0.4 * dT); }
      fork.visible = true; forkStrands.forEach((s, i) => { s.rotation.z = 0.3 * Math.sin(T * 4 + i) * (T > VANISH ? 1 : 0.2); });
      // Teller wird angestoßen (12,8 s), Soße fliegt zum Kumpel
      const bump = 12.8;
      mine.g.position.set(0.28, 0.775 + (dT > 0 ? 0.05 * dT : 0) + (T > bump ? 0.25 * (T - bump) : 0), 0 + (T > bump ? -0.08 * (T - bump) : 0)); mine.g.rotation.set(T > bump ? 0.7 * (T - bump) : 0.04 * dT, 0, T > bump ? 0.9 * (T - bump) : 0.03 * dT);
      const s0 = V3(0.23, 0.86 + 0.05 * Math.min(dT, 2.8), 0);
      if (T < bump) { sauce.position.copy(s0); sauce.scale.set(1.3, 0.35 + 0.65 * smooth(VANISH, VANISH + 1.5, T), 1.3); sauce.visible = true; if (T > VANISH) wobble(sauce, T, 1); }
      else if (T < SAUCE_HIT) { const k = (T - bump) / (SAUCE_HIT - bump); const tgt = headPos(fr, V3(0, 0.05, 0.1)); sauce.position.lerpVectors(s0, tgt, k); sauce.position.y += Math.sin(k * Math.PI) * 0.04; wobble(sauce, T, 1); sauce.visible = true; }
      else sauce.visible = false;
      // Pudding schwebt langsam hoch und dreht sich
      pudding.position.set(0.42, 0.81 + 0.16 * dT, 0.12 - 0.01 * dT); pudding.rotation.set(0.25 * dT, 0, 0.6 * dT); pudding.visible = true;
      mine.cup.visible = true;
      dust.visible = false;
    } else {
      // ---- Finale: er sitzt am Boden an der Bank, Spaghetti auf dem Kopf ----
      unseat(guy); posePerson(guy, {}); guy.position.set(0.9, -0.62, 0.35); guy.rotation.set(0, -2.1, 0);
      u.legL.rotation.x = u.legR.rotation.x = -1.45; u.legL.userData.knee.rotation.x = 0.1; u.legR.userData.knee.rotation.x = 0.35; u.pl.forEach((g, k) => { const lg = k ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
      u.torso.rotation.x = -0.15; u.armL.rotation.set(-0.2, 0, -0.35); u.armL.userData.fore.rotation.x = -0.2;
      // Hand hoch (Pudding auffangen), dann löffeln
      const reach = smooth(PUD - 1.4, PUD - 0.9, T), eat = smooth(PUD + 1.0, PUD + 1.5, T);
      u.armR.rotation.set(lerp(-0.2, -1.6, reach), 0, lerp(0.35, 0.15, reach)); u.armR.userData.fore.rotation.x = lerp(-0.2, -0.5, reach);
      if (eat > 0) { u.armR.rotation.x = lerp(-1.6, -1.1, eat); u.armR.userData.fore.rotation.x = lerp(-0.5, -1.5, eat); u.armL.rotation.x = lerp(-0.2, -1.3, eat); u.armL.userData.fore.rotation.x = lerp(-0.2, -1.4, eat); }
      const lookUp = smooth(83.6, 84.4, T) * (1 - smooth(PUD + 0.2, PUD + 0.8, T));
      u.head.rotation.set(-0.7 * lookUp + 0.15, 0, 0); brows(guy, lookUp > 0.3 ? 1 : 0.4, 0); mouthOpen(guy, T > PUD + 1.6 ? 0.25 + 0.2 * Math.max(0, Math.sin(T * 7)) : lookUp * 0.6);
      // Pudding: klebt kopfüber an der Decke, fällt bei PUD genau in die Hand
      guy.updateMatrixWorld(true); const hp = handPos(guy);
      const top = V3(hp.x, CEIL - 0.04, hp.z), fall = clamp((T - (PUD - 0.75)) / 0.75);
      ceilMess.visible = true; ceilMess.position.set(top.x, CEIL, top.z);
      if (T < PUD - 0.75) { pudding.position.copy(top); pudding.rotation.set(Math.PI, 0, 0.1 * Math.sin(T * 3) * smooth(83, 85, T)); }
      else if (T < PUD) { pudding.position.lerpVectors(top, hp.clone().add(V3(0, 0.05, 0)), easeIn(fall)); pudding.rotation.set(Math.PI * (1 - easeOut(fall)) + 0.2 * Math.sin(fall * 9), 0, 0); }
      else { pudding.position.copy(hp).add(V3(0, 0.05 - 0.02 * Math.exp(-(T - PUD) * 8) * Math.sin((T - PUD) * 40), 0)); pudding.rotation.set(0, 0, 0); }
      pudding.visible = true; fork.visible = false; sauce.visible = false; mine.g.visible = false;
      dust.visible = true;
      updateParticles(dust, [{pos: V3(0, 1.8, 0), r: 9, t0: 70, type: 'smoke', size: 2.8, rise: 0.05, alpha: 0.12, col: [0.85, 0.75, 0.62]}], T, V3(0.05, 0, 0.02));
    }
    if (!fin) { mine.g.visible = true; ceilMess.visible = false; }

    // ---------- Kamera ----------
    camera.fov = 50; let pos, tgt; camera.up.set(0, 1, 0);
    const shake = (a, s = 0) => V3(noise1(T * 9, s) * a, noise1(T * 9, s + 3) * a, noise1(T * 9, s + 6) * a);
    if (shot.id === 'intro') { const k = smooth(0, 3.5, T); pos = V3(lerp(3.6, 3.0, k), lerp(2.3, 2.0, k), lerp(4.6, 3.8, k)); tgt = V3(0.2, 1.0, 0); camera.fov = 46; }
    else if (shot.id === 'wait' || (shot.id === 'mensa' && T < 12.6)) { // über die Schulter des Kumpels auf ihn
      const k = smooth(3.5, 12.6, T); pos = V3(lerp(-1.55, -1.25, k), lerp(1.5, 1.6, k), lerp(0.75, 0.55, k)); tgt = V3(GX - 0.1, lerp(1.2, 1.55, smooth(VANISH, 12.6, T)), 0.02); camera.fov = lerp(40, 46, smooth(VANISH, 12.6, T)); }
    else if (T < 15.0) { // Gegenschuss: Kumpel – Soße kommt geflogen
      const k = smooth(12.6, 15.0, T); const fh = headPos(fr, V3(0, 0, 0)); pos = V3(lerp(0.05, -0.1, k), fh.y + 0.12, lerp(1.25, 1.05, k)); tgt = fh.clone().add(V3(0.12, -0.08, -0.05)); camera.fov = lerp(44, 38, k);
      if (T > SAUCE_HIT) pos.add(shake(0.012 * (1 - smooth(SAUCE_HIT, SAUCE_HIT + 0.5, T)), 3)); }
    else if (!fin) { // weit oben: alle schweben aus den Bänken
      const k = smooth(15, 17, T); pos = V3(lerp(5.9, 5.5, k), lerp(2.2, 2.4, k), lerp(2.4, 2.0, k)); tgt = V3(1.2, 1.45, -0.6); camera.fov = 52; }
    else { // Finale
      if (T < 83.6) { const k = smooth(80, 83.6, T); pos = V3(lerp(-2.6, -1.4, k), lerp(1.8, 1.25, k), lerp(-1.6, -0.9, k)).add(shake(0.006, 1)); tgt = V3(0.6, 0.55, 0.3); camera.fov = 46; }
      else if (T < PUD - 0.2) { const k = smooth(83.6, 85.2, T); pos = V3(-0.5, 1.0, -0.4); tgt = V3().lerpVectors(V3(0.75, 0.6, 0.35), pudding.position, k); camera.fov = lerp(46, 16, k); }
      else { const k = smooth(PUD - 0.2, PUD + 0.6, T); pos = V3(lerp(-0.5, -0.2, k), lerp(1.0, 0.95, k), lerp(-0.4, -0.15, k)); tgt = V3().lerpVectors(pudding.position, guy.userData.head.localToWorld(V3(0, -0.05, 0)), smooth(PUD, PUD + 0.8, T)); camera.fov = lerp(16, 40, smooth(PUD - 0.2, PUD + 0.6, T));
        if (T > PUD && T < PUD + 0.4) pos.add(shake(0.01, 5)); }
    }
    camera.position.copy(pos); camera.lookAt(tgt); camera.updateProjectionMatrix();
  }};
}
