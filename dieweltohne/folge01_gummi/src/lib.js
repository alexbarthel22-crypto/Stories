import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
export {THREE, RoundedBoxGeometry};
let _env = null;
export function envMap(renderer) { if (!_env) { const pm = new THREE.PMREMGenerator(renderer); _env = pm.fromScene(new RoomEnvironment(), 0.04).texture; } return _env; }

// ---------- Hilfsfunktionen ----------
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const easeOut = t => 1 - Math.pow(1 - clamp(t), 3);
export const easeIn = t => Math.pow(clamp(t), 3);
export function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
// deterministisches Rauschen für Kamerawackeln
export function noise1(t, seed = 0) {
  return Math.sin(t * 1.7 + seed) * 0.5 + Math.sin(t * 3.1 + seed * 2.3) * 0.3 + Math.sin(t * 7.3 + seed * 0.7) * 0.2;
}

const matCache = new Map();
export function mat(color, o = {}) {
  const key = color + JSON.stringify(o);
  if (!matCache.has(key)) matCache.set(key, new THREE.MeshStandardMaterial({color, roughness: 0.75, metalness: 0, ...o}));
  return matCache.get(key);
}
export function mesh(geo, material, x = 0, y = 0, z = 0, parent) {
  const m = new THREE.Mesh(geo, material); m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  if (parent) parent.add(m);
  return m;
}

// ---------- Texturen ----------
export function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  return t;
}
export function facadeTex(base, seed, floors = 6, cols = 4) {
  const r = rng(seed);
  return canvasTex(256, 512, (g, w, h) => {
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 1500; i++) { g.fillStyle = `rgba(0,0,0,${r() * 0.05})`; g.fillRect(r() * w, r() * h, 3, 3); }
    const fh = h / floors, cw = w / cols;
    for (let f = 0; f < floors; f++) for (let c = 0; c < cols; c++) {
      const x = c * cw + cw * 0.22, y = f * fh + fh * 0.2, ww = cw * 0.56, hh = fh * 0.55;
      g.fillStyle = 'rgba(255,255,255,0.35)'; g.fillRect(x - 4, y - 4, ww + 8, hh + 8);
      const lit = r() < 0.35;
      const grd = g.createLinearGradient(x, y, x + ww, y + hh);
      grd.addColorStop(0, lit ? '#f3d9a0' : '#3d4a57'); grd.addColorStop(1, lit ? '#c9a466' : '#1d252e');
      g.fillStyle = grd; g.fillRect(x, y, ww, hh);
      g.fillStyle = 'rgba(255,255,255,0.18)'; g.fillRect(x + ww / 2 - 1.5, y, 3, hh); g.fillRect(x, y + hh * 0.4, ww, 3);
      g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(x - 6, y + hh + 4, ww + 12, 5);
    }
    g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(0, h - fh * 0.9, w, fh * 0.9); // Erdgeschoss dunkler
  });
}
export function asphaltTex() {
  const r = rng(3);
  const t = canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = '#3a3c40'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 40000; i++) { const v = 40 + r() * 50; g.fillStyle = `rgba(${v},${v},${v + 4},0.5)`; g.fillRect(r() * w, r() * h, 2, 2); }
    for (let i = 0; i < 25; i++) { g.fillStyle = 'rgba(15,16,18,0.35)'; g.beginPath(); g.ellipse(r() * w, r() * h, 40 + r() * 140, 20 + r() * 60, r() * 3, 0, 7); g.fill(); }
    for (let i = 0; i < 12; i++) { g.strokeStyle = 'rgba(20,20,22,0.6)'; g.lineWidth = 2; g.beginPath(); let x = r() * w, y = r() * h; g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (r() - 0.5) * 80; y += (r() - 0.5) * 80; g.lineTo(x, y); } g.stroke(); }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
export function tileTex(c1 = '#9a9a96', c2 = '#8b8b87') {
  const r = rng(9);
  const t = canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#6f6f6b'; g.fillRect(0, 0, w, h);
    const s = 64;
    for (let y = 0; y < h; y += s) for (let x = 0; x < w; x += s) {
      const v = r() * 18 - 9; g.fillStyle = r() < 0.5 ? c1 : c2; g.fillRect(x + 2, y + 2, s - 4, s - 4);
      g.fillStyle = `rgba(${v > 0 ? 255 : 0},${v > 0 ? 255 : 0},${v > 0 ? 255 : 0},${Math.abs(v) / 100})`; g.fillRect(x + 2, y + 2, s - 4, s - 4);
    }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}

// ---------- Himmel ----------
export function skyDome(top, mid, bottom, radius = 400) {
  const tex = canvasTex(16, 512, (g, w, h) => {
    const grd = g.createLinearGradient(0, 0, 0, h);
    grd.addColorStop(0, top); grd.addColorStop(0.55, mid); grd.addColorStop(1, bottom);
    g.fillStyle = grd; g.fillRect(0, 0, w, h);
  });
  const m = new THREE.Mesh(new THREE.SphereGeometry(radius, 32, 16), new THREE.MeshBasicMaterial({map: tex, side: THREE.BackSide, fog: false, depthWrite: false}));
  m.renderOrder = -10; return m;
}

// ---------- Menschen ----------
const SKIN = ['#f1c7a5', '#d9a47e', '#a8714f', '#7a4d33', '#f5d3b8'];
const HAIR = ['#2a1d15', '#5a3b22', '#c9a35b', '#111', '#8a5a2b', '#b8b8b8'];
const TOPS = ['#e2b23a', '#d94b3d', '#3f6fb5', '#2f8f6b', '#e8e2d4', '#7b4fa0', '#e07a2f', '#24343f', '#c23b6a', '#4aa3c7'];
const PANTS = ['#2d3a55', '#3a3a3a', '#5b4636', '#1f2a44', '#6b6f75', '#2b4d3a'];
export function makePerson(seed, o = {}) {
  const r = rng(seed * 7919 + 13);
  const pick = a => a[Math.floor(r() * a.length)];
  const skin = mat(o.skin || pick(SKIN)), top = mat(o.top || pick(TOPS)), pantsM = mat(o.pants || pick(PANTS));
  const hairM = mat(o.hair || pick(HAIR), {roughness: 0.9});
  const shoeM = mat(o.shoe || (r() < 0.5 ? '#f2f2f2' : '#2a2a2a')), soleM = mat(o.sole || '#ece6da', {roughness: 0.95});
  const h = o.height || (0.92 + r() * 0.16);
  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body); // dreht sich beim Fallen
  body.scale.setScalar(h);
  const hips = new THREE.Group(); hips.position.y = 0.92; body.add(hips);
  const torso = new THREE.Group(); hips.add(torso);
  mesh(new THREE.CapsuleGeometry(0.17, 0.36, 4, 10), top, 0, 0.3, 0, torso).scale.set(1.15, 1, 0.75);
  const head = new THREE.Group(); head.position.y = 0.78; torso.add(head);
  mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.1, 8), skin, 0, -0.08, 0, head);
  mesh(new THREE.SphereGeometry(0.115, 16, 12), skin, 0, 0.06, 0, head).scale.set(0.95, 1.08, 1);
  const hair = mesh(new THREE.SphereGeometry(0.122, 16, 12, 0, Math.PI * 2, 0, Math.PI * (o.longHair ? 0.75 : 0.55)), hairM, 0, 0.08, -0.01, head);
  hair.rotation.x = -0.25;
  let ponytail = null;
  if (o.ponytail) { // Zopf mit Haargummi
    ponytail = new THREE.Group(); ponytail.position.set(0, 0.1, -0.11); head.add(ponytail);
    ponytail.userData.band = mesh(new THREE.TorusGeometry(0.03, 0.012, 6, 12), mat('#e0457b'), 0, 0, -0.01, ponytail);
    mesh(new THREE.CapsuleGeometry(0.035, 0.16, 4, 8), hairM, 0, -0.1, -0.03, ponytail);
    ponytail.userData.loose = mesh(new THREE.SphereGeometry(0.16, 12, 10, 0, Math.PI * 2, 0, Math.PI * 0.7), hairM, 0, -0.02, 0.1, ponytail);
    ponytail.userData.loose.visible = false;
  }
  // Augen
  for (const s of [-1, 1]) mesh(new THREE.SphereGeometry(0.014, 8, 6), mat('#1a1a1a'), s * 0.04, 0.08, 0.105, head);
  const arm = s => {
    const sh = new THREE.Group(); sh.position.set(s * 0.25, 0.56, 0); torso.add(sh);
    mesh(new THREE.CapsuleGeometry(0.055, 0.25, 4, 8), top, 0, -0.16, 0, sh);
    const fore = new THREE.Group(); fore.position.y = -0.32; sh.add(fore);
    mesh(new THREE.CapsuleGeometry(0.048, 0.22, 4, 8), o.shortSleeve ? skin : top, 0, -0.13, 0, fore);
    mesh(new THREE.SphereGeometry(0.05, 8, 6), skin, 0, -0.29, 0, fore);
    sh.userData.fore = fore; return sh;
  };
  const armL = arm(-1), armR = arm(1);
  // Hose (separat, kann rutschen) und Beine
  const pants = new THREE.Group(); hips.add(pants);
  mesh(new THREE.CapsuleGeometry(0.16, 0.08, 4, 10), pantsM, 0, 0.0, 0, pants).scale.set(1.1, 1, 0.75);
  const waist = mesh(new THREE.TorusGeometry(0.155, 0.022, 6, 18), mat(o.pants || '#2d3a55', {roughness: 0.9}), 0, 0.09, 0, pants);
  waist.rotation.x = Math.PI / 2; waist.scale.set(1.12, 0.78, 1);
  const under = mesh(new THREE.CapsuleGeometry(0.15, 0.04, 4, 10), mat(o.under || '#e94f6a'), 0, -0.02, 0, hips);
  under.scale.set(1.12, 1, 0.74); under.visible = false;
  const leg = s => {
    const hip = new THREE.Group(); hip.position.set(s * 0.1, -0.04, 0); hips.add(hip);
    const thighSkin = mesh(new THREE.CapsuleGeometry(0.07, 0.3, 4, 8), skin, 0, -0.2, 0, hip); thighSkin.visible = false;
    const knee = new THREE.Group(); knee.position.y = -0.42; hip.add(knee);
    mesh(new THREE.CapsuleGeometry(0.058, 0.3, 4, 8), skin, 0, -0.2, 0, knee).visible = false;
    const shoe = new THREE.Group(); shoe.position.set(0, -0.42, 0.04); knee.add(shoe);
    mesh(new RoundedBoxGeometry(0.11, 0.08, 0.24, 2, 0.03), shoeM, 0, 0.02, 0, shoe);
    const sole = mesh(new THREE.BoxGeometry(0.115, 0.035, 0.25), soleM, 0, -0.035, 0, shoe);
    hip.userData = {knee, shoe, sole, thighSkin};
    return hip;
  };
  const legL = leg(-1), legR = leg(1);
  // Hosenbeine (gehören zur Hose, folgen den Beinen außer beim Rutschen)
  const pl = [legL, legR].map((lg, i) => {
    const g = new THREE.Group(); pants.add(g);
    const up = mesh(new THREE.CapsuleGeometry(0.078, 0.3, 4, 8), pantsM, 0, -0.2, 0, g);
    const low = mesh(new THREE.CapsuleGeometry(0.068, 0.32, 4, 8), pantsM, 0, -0.62, 0, g);
    g.userData = {up, low}; return g;
  });
  root.userData = {body, hips, torso, head, armL, armR, legL, legR, pants, pl, under, ponytail, h, soles: [legL.userData.sole, legR.userData.sole]};
  return root;
}
// Pose: walk (Phase), fall (0..1 nach hinten), pantsDrop (0..1)
export function posePerson(p, {walk = 0, walkAmp = 1, fall = 0, fallDir = 1, pantsDrop = 0, armsUp = 0, holdUp = 0, look = 0, slipSide = 0} = {}) {
  const u = p.userData;
  const sw = Math.sin(walk) * 0.5 * walkAmp * (1 - fall);
  const bob = Math.abs(Math.cos(walk)) * 0.025 * walkAmp * (1 - fall);
  u.legL.rotation.x = sw; u.legR.rotation.x = -sw;
  u.legL.userData.knee.rotation.x = Math.max(0, -Math.sin(walk + 0.6)) * 0.7 * walkAmp;
  u.legR.userData.knee.rotation.x = Math.max(0, Math.sin(walk + 0.6)) * 0.7 * walkAmp;
  u.armL.rotation.x = -sw * 0.8; u.armR.rotation.x = sw * 0.8;
  u.armL.rotation.z = -0.08; u.armR.rotation.z = 0.08;
  u.armL.userData.fore.rotation.x = -0.25; u.armR.userData.fore.rotation.x = -0.25;
  u.hips.position.y = 0.92 + bob; u.body.rotation.set(0, 0, 0); u.body.position.set(0, 0, 0);
  u.torso.rotation.set(0, look, 0); u.head.rotation.set(0, 0, 0);
  if (holdUp > 0) { // Arm hoch (Ballon halten / Handy)
    u.armR.rotation.x = lerp(u.armR.rotation.x, -2.6, holdUp); u.armR.userData.fore.rotation.x = lerp(-0.25, -0.2, holdUp);
  }
  if (fall > 0) { // Ausrutschen: Füße rutschen nach vorn, Körper kippt um die Füße nach hinten und liegt dann auf dem Boden
    const f = clamp(fall);
    const tip = easeIn(clamp((f - 0.08) / 0.62));                       // Kippen beschleunigt wie im freien Fall
    const land = clamp((f - 0.7) / 0.3);                                  // Aufprall und Nachfedern
    const bounce = Math.sin(land * Math.PI * 2) * Math.exp(-land * 4) * 0.08 * (land > 0);
    const rot = -(Math.PI / 2 - 0.04) * tip + bounce;
    u.body.rotation.x = rot * fallDir; u.body.rotation.z = slipSide * tip * 0.18;
    u.body.position.z = 0.5 * easeOut(clamp(f / 0.45));                    // Füße schießen nach vorn
    u.body.position.y = 0.15 * Math.sin(-rot);                            // Rücken liegt auf, nicht im Boden
    const kick = Math.sin(clamp(f / 0.75) * Math.PI);                     // Beine fliegen hoch und fallen zurück
    u.legL.rotation.x = -0.15 - kick * 1.0; u.legR.rotation.x = -0.35 - kick * 0.7;
    u.legL.userData.knee.rotation.x = 0.15 + kick * 0.3; u.legR.userData.knee.rotation.x = 0.5;
    u.armL.rotation.x = lerp(-0.3, -1.4, tip) - kick * 0.8; u.armR.rotation.x = lerp(-0.3, -1.1, tip) - kick * 0.9;
    u.armL.rotation.z = -0.2 - tip * 0.9; u.armR.rotation.z = 0.2 + tip * 0.9;
    u.head.rotation.x = 0.35 * tip - bounce * 2; u.hips.position.y = 0.92;
  }
  if (armsUp > 0) { u.armL.rotation.z = -armsUp * 2.4; u.armR.rotation.z = armsUp * 2.4; }
  // Hose
  const d = clamp(pantsDrop);
  u.pants.position.y = -d * 0.66;
  u.pl.forEach((g, i) => {
    const lg = i ? u.legR : u.legL;
    g.position.copy(lg.position); g.rotation.copy(lg.rotation);
    g.userData.up.scale.y = lerp(1, 0.3, d); g.userData.up.position.y = lerp(-0.2, -0.05, d);
    g.userData.low.scale.set(lerp(1, 1.35, d), lerp(1, 0.55, d), lerp(1, 1.35, d)); g.userData.low.position.y = lerp(-0.62, -0.25, d);
    lg.userData.thighSkin.visible = d > 0.15;
  });
  u.under.visible = d > 0.05;
  if (d > 0) { u.armL.rotation.x = lerp(u.armL.rotation.x, -0.5, d); u.armR.rotation.x = lerp(u.armR.rotation.x, -0.5, d); u.armL.rotation.z = -0.25 * d; u.armR.rotation.z = 0.25 * d; u.torso.rotation.x = 0.25 * d; }
}

// ---------- Autos ----------
const CAR_COLORS = ['#c8102e', '#f2f2f2', '#2b5fa8', '#8a9099', '#e5b31b', '#3a6b4a', '#d9d4c7', '#2a2b2e', '#6fa3c9'];
const FIRST = ['#c8102e', '#eeeeea', '#2b5fa8', '#e5b31b', '#8a9099', '#3a6b4a'];
export function makeCar(seed, o = {}) {
  const r = rng(seed * 31 + 5);
  const color = o.color || (seed <= FIRST.length ? FIRST[seed - 1] : CAR_COLORS[Math.floor(r() * CAR_COLORS.length)]);
  const L = o.long || 4.2, W = 1.8;
  const car = new THREE.Group(); const body = new THREE.Group(); car.add(body);
  const paint = mat(color, {roughness: 0.3, metalness: 0.15});
  // Seitenprofil extrudiert
  const s = new THREE.Shape();
  const hx = L / 2;
  s.moveTo(-hx, 0.32); s.lineTo(-hx, 0.78); s.quadraticCurveTo(-hx + 0.05, 0.86, -hx + 0.3, 0.88);
  s.lineTo(-hx + 1.05, 0.92); s.lineTo(-hx + 1.55, 1.38); s.lineTo(hx - 1.35, 1.4); s.lineTo(hx - 0.7, 0.98);
  s.lineTo(hx - 0.15, 0.9); s.quadraticCurveTo(hx, 0.85, hx, 0.7); s.lineTo(hx, 0.32); s.lineTo(-hx, 0.32);
  const g = new THREE.ExtrudeGeometry(s, {depth: W, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.06, bevelSegments: 3, curveSegments: 8});
  g.translate(0, 0, -W / 2); g.rotateY(-Math.PI / 2); // Länge entlang z (vorne = +z)
  mesh(g, paint, 0, 0, 0, body);
  const glass = mat('#16202b', {roughness: 0.05, metalness: 0.9});
  const gs = new THREE.Shape();
  gs.moveTo(-hx + 1.12, 0.96); gs.lineTo(-hx + 1.58, 1.34); gs.lineTo(hx - 1.38, 1.36); gs.lineTo(hx - 0.8, 0.99);
  const gg = new THREE.ExtrudeGeometry(gs, {depth: W + 0.14, bevelEnabled: false}); gg.translate(0, 0, -(W + 0.14) / 2); gg.rotateY(-Math.PI / 2);
  mesh(gg, glass, 0, 0, 0, body);
  const lamp = mat('#fff6d8', {emissive: '#fff1c4', emissiveIntensity: 2});
  const tail = mat('#ff2a1a', {emissive: '#ff2010', emissiveIntensity: 1.6});
  for (const sx of [-0.65, 0.65]) {
    mesh(new THREE.BoxGeometry(0.34, 0.12, 0.06), lamp, sx, 0.72, hx + 0.05, body);
    mesh(new THREE.BoxGeometry(0.34, 0.1, 0.06), tail, sx, 0.76, -hx - 0.05, body);
  }
  mesh(new THREE.BoxGeometry(W + 0.05, 0.12, 0.12), mat('#222', {roughness: 0.6}), 0, 0.38, hx + 0.04, body);
  mesh(new THREE.BoxGeometry(W + 0.05, 0.12, 0.12), mat('#222', {roughness: 0.6}), 0, 0.38, -hx - 0.04, body);
  if (o.ambulance) {
    mesh(new THREE.BoxGeometry(W + 0.1, 0.18, L * 0.9), mat('#e8501f'), 0, 0.6, 0, body);
    const bl = mat('#2a6bff', {emissive: '#2a6bff', emissiveIntensity: 0});
    car.userData.blue = [mesh(new THREE.BoxGeometry(0.5, 0.12, 0.2), bl, -0.4, 1.47, 0.3, body), mesh(new THREE.BoxGeometry(0.5, 0.12, 0.2), bl.clone(), 0.4, 1.47, 0.3, body)];
  }
  // Räder
  const wheels = [];
  const tireM = mat('#141414', {roughness: 0.92, transparent: true});
  const rimM = mat('#c9ccd1', {roughness: 0.25, metalness: 0.9});
  const wireM = mat('#9a9ea4', {roughness: 0.35, metalness: 0.9, transparent: true});
  for (const [x, z] of [[-0.82, 1.32], [0.82, 1.32], [-0.82, -1.3], [0.82, -1.3]]) {
    const w = new THREE.Group(); w.position.set(x, 0.34, z); car.add(w);
    const spin = new THREE.Group(); w.add(spin);
    const tire = mesh(new THREE.TorusGeometry(0.24, 0.1, 10, 24), tireM, 0, 0, 0, spin); tire.rotation.y = Math.PI / 2; tire.scale.set(1, 1, 1.9);
    const rim = mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.2, 20), rimM, 0, 0, 0, spin); rim.rotation.z = Math.PI / 2;
    for (let k = 0; k < 5; k++) { const sp = mesh(new THREE.BoxGeometry(0.03, 0.36, 0.05), mat('#8d9096', {metalness: 0.9, roughness: 0.3}), Math.sign(x) * 0.105, 0, 0, spin); sp.rotation.x = k * Math.PI * 2 / 5; }
    // Stahlgürtel, sichtbar wenn der Gummi weg ist
    const wires = new THREE.Group(); spin.add(wires); wires.visible = false;
    for (let k = -2; k <= 2; k++) { const t = mesh(new THREE.TorusGeometry(0.33, 0.006, 4, 40), wireM, k * 0.035, 0, 0, wires); t.rotation.y = Math.PI / 2; }
    wheels.push({w, spin, tire, wires, wireM});
  }
  car.userData = {body, wheels, tireM, color, L};
  return car;
}
// Reifen verschwinden lassen: v=0 normal, 1 = weg. drop = Absenkung der Karosserie
export function carNoRubber(car, v, wiresLeft = 1) {
  const u = car.userData;
  u.tireM.opacity = 1 - clamp(v * 3);
  u.wheels.forEach(wh => { wh.tire.visible = v < 0.34; wh.wires.visible = v > 0.05 && wiresLeft > 0.02; wh.wireM.opacity = wiresLeft; });
}

// ---------- Partikel: Funken, Regen, Spritzer ----------
const sparkTex = canvasTex(64, 64, (g, w) => { const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, 'rgba(255,255,240,1)'); r.addColorStop(0.25, 'rgba(255,200,90,0.9)'); r.addColorStop(1, 'rgba(255,90,0,0)'); g.fillStyle = r; g.fillRect(0, 0, w, w); });
export function sparkSystem(n = 600, size = 0.12) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  const m = new THREE.Points(geo, new THREE.PointsMaterial({size, map: sparkTex, vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending}));
  m.frustumCulled = false; m.userData.n = n; return m;
}
// Funken aus Emittern: emitters = [{pos:Vector3, dir:Vector3, rate, t0, t1}], t = Zeit in s
export function updateSparks(sys, emitters, t, gravity = 9.8) {
  const P = sys.geometry.attributes.position.array, C = sys.geometry.attributes.color.array;
  const n = sys.userData.n; let i = 0;
  const per = Math.floor(n / Math.max(1, emitters.length));
  emitters.forEach((e, ei) => {
    const r = rng(ei * 101 + 7);
    for (let k = 0; k < per && i < n; k++, i++) {
      const life = 0.25 + r() * 0.45, birth = e.t0 + r() * (e.t1 - e.t0 + life);
      const phase = ((t - birth) % life + life) % life; // wiederkehrend
      const born = t - phase;
      const ok = born >= e.t0 && born <= e.t1 && t >= e.t0;
      const a = phase;
      const vx = e.dir.x * (3 + r() * 6) + (r() - 0.5) * 3, vy = e.dir.y * (2 + r() * 4) + r() * 2.5, vz = e.dir.z * (3 + r() * 6) + (r() - 0.5) * 3;
      const p = e.pos instanceof Function ? e.pos(born) : e.pos;
      P[i * 3] = ok ? p.x + vx * a : 0; P[i * 3 + 1] = ok ? Math.max(0.01, p.y + vy * a - gravity * a * a / 2) : -99; P[i * 3 + 2] = ok ? p.z + vz * a : 0;
      const fade = ok ? 1 - a / life : 0;
      C[i * 3] = fade; C[i * 3 + 1] = fade * (0.55 + r() * 0.35); C[i * 3 + 2] = fade * 0.25;
    }
  });
  for (; i < n; i++) P[i * 3 + 1] = -99;
  sys.geometry.attributes.position.needsUpdate = true; sys.geometry.attributes.color.needsUpdate = true;
}
export function rainSystem(n, box, color = 0xaab4c0, len = 0.5, opacity = 0.45) {
  const r = rng(77);
  const base = [];
  for (let i = 0; i < n; i++) base.push([box.x0 + r() * (box.x1 - box.x0), r(), box.z0 + r() * (box.z1 - box.z0), 0.8 + r() * 0.4]);
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 6), 3));
  const m = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({color, transparent: true, opacity, depthWrite: false}));
  m.frustumCulled = false; m.userData = {base, box, len};
  return m;
}
export function updateRain(m, t, speed = 14, wind = -0.12) {
  const {base, box, len} = m.userData; const P = m.geometry.attributes.position.array; const H = box.y1 - box.y0;
  base.forEach((b, i) => {
    const y = box.y0 + (((b[1] * H - t * speed * b[3]) % H) + H) % H;
    P[i * 6] = b[0] + wind * (y - box.y0); P[i * 6 + 1] = y; P[i * 6 + 2] = b[2];
    P[i * 6 + 3] = b[0] + wind * (y + len - box.y0); P[i * 6 + 4] = y + len; P[i * 6 + 5] = b[2];
  });
  m.geometry.attributes.position.needsUpdate = true;
}
// Ringförmige Einschläge von Regentropfen auf dem Boden
const ringTex = canvasTex(64, 64, (g, w) => { g.strokeStyle = 'rgba(220,230,240,0.9)'; g.lineWidth = 3; g.beginPath(); g.arc(32, 32, 26, 0, 7); g.stroke(); });
export function splashSystem(n, box) {
  const r = rng(91); const items = [];
  const geo = new THREE.PlaneGeometry(1, 1); geo.rotateX(-Math.PI / 2);
  const inst = new THREE.InstancedMesh(geo, new THREE.MeshBasicMaterial({map: ringTex, transparent: true, depthWrite: false, opacity: 0.5}), n);
  for (let i = 0; i < n; i++) items.push([box.x0 + r() * (box.x1 - box.x0), box.z0 + r() * (box.z1 - box.z0), r(), 0.25 + r() * 0.2]);
  inst.userData = {items, y: box.y || 0.012}; inst.frustumCulled = false; return inst;
}
const _m4 = new THREE.Matrix4(), _q = new THREE.Quaternion(), _v = new THREE.Vector3(), _s = new THREE.Vector3();
export function updateSplash(inst, t) {
  const {items, y} = inst.userData;
  items.forEach((it, i) => {
    const ph = ((t / it[3] + it[2]) % 1);
    _s.setScalar(0.02 + ph * 0.22); _v.set(it[0], y, it[1]);
    _m4.compose(_v, _q, _s); inst.setMatrixAt(i, _m4);
  });
  inst.instanceMatrix.needsUpdate = true;
}
