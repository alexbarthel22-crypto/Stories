// Meeresbewohner und das Tauchboot: Fischschwarm, Pottwal, Riesenkalmar, Anglerfisch, Scheibenbauch, Tauchboot mit Pizza
import {THREE, mat, mesh, rng, clamp, lerp, smooth, canvasTex} from './lib.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

// ---------- Hilfen ----------
// Rumpf entlang der x-Achse (Kopf bei x=0, Schwanz bei x=L). prof(u) -> [halbe Höhe, halbe Breite, Rundheit-Exponent, y-Versatz]
export function hull(L, prof, nu = 60, nv = 28) {
  const pos = [], uv = [], idx = [];
  for (let i = 0; i <= nu; i++) { const u = i / nu; const [h, w, ex, yo] = prof(u);
    for (let j = 0; j <= nv; j++) { const a = j / nv * Math.PI * 2; const c = Math.cos(a), s = Math.sin(a);
      const e = 2 / (ex || 2); const y = Math.sign(c) * Math.pow(Math.abs(c), e) * h + (yo || 0), z = Math.sign(s) * Math.pow(Math.abs(s), e) * w;
      pos.push(u * L, y, z); uv.push(j / nv, u); } }
  for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) { const a = i * (nv + 1) + j, b = a + nv + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx);
  g.computeVertexNormals(); return g;
}
// Spitz zulaufender Schlauch mit fester Vertexzahl (für Tentakel, jedes Bild neu gebogen)
export class Tube {
  constructor(n, radial, r0, r1, material) {
    this.n = n; this.radial = radial; this.r0 = r0; this.r1 = r1;
    const g = new THREE.BufferGeometry(); const cnt = (n + 1) * (radial + 1);
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(cnt * 3), 3)); g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(cnt * 3), 3));
    g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(cnt * 2), 2)); const idx = [];
    for (let i = 0; i < n; i++) for (let j = 0; j < radial; j++) { const a = i * (radial + 1) + j, b = a + radial + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
    g.setIndex(idx); this.mesh = new THREE.Mesh(g, material); this.mesh.frustumCulled = false;
  }
  set(points, flat = 1) { // points: n+1 Vector3
    const g = this.mesh.geometry, P = g.attributes.position.array, N = g.attributes.normal.array, U = g.attributes.uv.array;
    const T = new THREE.Vector3(), Nn = new THREE.Vector3(), B = new THREE.Vector3(), up = new THREE.Vector3(0, 0, 1), v = new THREE.Vector3();
    for (let i = 0; i <= this.n; i++) {
      const a = points[Math.max(0, i - 1)], b = points[Math.min(this.n, i + 1)]; T.subVectors(b, a).normalize();
      Nn.crossVectors(T, up); if (Nn.lengthSq() < 1e-6) Nn.set(1, 0, 0); Nn.normalize(); B.crossVectors(T, Nn).normalize();
      const r = lerp(this.r0, this.r1, Math.pow(i / this.n, 0.8));
      for (let j = 0; j <= this.radial; j++) { const an = j / this.radial * Math.PI * 2; const c = Math.cos(an), s = Math.sin(an) * flat;
        v.copy(Nn).multiplyScalar(c).addScaledVector(B, s); const k = (i * (this.radial + 1) + j);
        P[k * 3] = points[i].x + v.x * r; P[k * 3 + 1] = points[i].y + v.y * r; P[k * 3 + 2] = points[i].z + v.z * r;
        v.normalize(); N[k * 3] = v.x; N[k * 3 + 1] = v.y; N[k * 3 + 2] = v.z; U[k * 2] = j / this.radial; U[k * 2 + 1] = i / this.n; }
    }
    g.attributes.position.needsUpdate = true; g.attributes.uv.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere();
  }
}

// ---------- Fischschwarm ----------
export function fishSchool(n = 320) {
  const body = new THREE.SphereGeometry(1, 10, 6); body.scale(0.09, 0.028, 0.016);
  const tail = new THREE.ConeGeometry(0.022, 0.05, 4); tail.rotateZ(Math.PI / 2); tail.scale(1, 1, 0.25); tail.translate(-0.105, 0, 0);
  const geo = mergeGeometries([body.toNonIndexed(), tail.toNonIndexed()]);
  const m = new THREE.MeshStandardMaterial({color: '#c9dbe2', metalness: 0.85, roughness: 0.28, envMapIntensity: 1.6});
  const inst = new THREE.InstancedMesh(geo, m, n); inst.frustumCulled = false;
  const r = rng(12); inst.userData.f = Array.from({length: n}, () => ({R: 1.5 + r() * 3.2, y: (r() - 0.5) * 3.4, ph: r() * 6.28, sp: 0.55 + r() * 0.25, wob: r() * 6, s: 0.8 + r() * 0.5}));
  return inst;
}
const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _p = new THREE.Vector3(), _s = new THREE.Vector3(), _e = new THREE.Euler();
// center: Mittelpunkt des Wirbels, scare: 0..1 (Schwarm schreckt zusammen und weicht aus)
export function updateSchool(inst, T, center, scare = 0) {
  inst.userData.f.forEach((f, i) => {
    const a = f.ph + T * f.sp * (1 + scare * 1.6); const R = f.R * (1 - scare * 0.45);
    _p.set(center.x + Math.cos(a) * R, center.y + f.y * (1 - scare * 0.3) + Math.sin(T * 1.3 + f.wob) * 0.15 - scare * 1.5, center.z + Math.sin(a) * R * 0.8 - scare * 2.5);
    const yaw = -a - Math.PI; _e.set(0, yaw, 0.15 * Math.sin(T * 2 + f.wob)); _q.setFromEuler(_e);
    _s.set(f.s * (1 + 0.06 * Math.sin(T * 14 + f.wob)), f.s, f.s); _m.compose(_p, _q, _s); inst.setMatrixAt(i, _m);
  });
  inst.instanceMatrix.needsUpdate = true;
}

// ---------- Pottwal (14 m) ----------
function whaleSkin() {
  const r = rng(21);
  return canvasTex(512, 1024, (g, w, h) => {
    g.fillStyle = '#4d4c50'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 9000; i++) { const v = 60 + r() * 40; g.fillStyle = `rgba(${v},${v},${v + 4},0.25)`; g.fillRect(r() * w, r() * h, 2 + r() * 3, 1); }
    g.strokeStyle = 'rgba(25,25,28,0.45)'; g.lineWidth = 2;
    for (let i = 0; i < 260; i++) { const y = r() * h; g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= w; x += 32) g.lineTo(x, y + Math.sin(x * 0.03 + i) * 5 + (r() - 0.5) * 4); g.stroke(); }
    for (let i = 0; i < 60; i++) { g.strokeStyle = 'rgba(200,200,205,0.18)'; g.lineWidth = 1 + r() * 2; g.beginPath(); const x = r() * w, y = r() * h * 0.4; g.moveTo(x, y); g.lineTo(x + (r() - 0.5) * 40, y + 30 + r() * 60); g.stroke(); } // Narben (Kalmare!)
  });
}
export function spermWhale() {
  const L = 14; const grp = new THREE.Group();
  const skin = new THREE.MeshStandardMaterial({map: whaleSkin(), roughness: 0.75, metalness: 0.05, color: '#5c5c61'});
  const prof = u => { // Kopf kastig, Körper rund
    const head = u < 0.36; let h, w;
    if (u < 0.03) { const k = u / 0.03; h = lerp(1.05, 1.45, Math.sqrt(k)); w = lerp(0.85, 1.15, Math.sqrt(k)); }
    else if (u < 0.36) { h = 1.5; w = 1.2; }
    else if (u < 0.6) { const k = (u - 0.36) / 0.24; h = lerp(1.5, 1.35, k); w = lerp(1.2, 1.15, k); }
    else { const k = (u - 0.6) / 0.4; h = lerp(1.35, 0.28, Math.pow(k, 0.85)); w = lerp(1.15, 0.22, Math.pow(k, 0.9)); }
    const hump = u > 0.62 && u < 0.7 ? 0.12 * Math.sin((u - 0.62) / 0.08 * Math.PI) : 0;
    return [h + hump, w, head ? 3.0 : lerp(3.0, 2, clamp((u - 0.36) / 0.2)), 0];
  };
  const front = new THREE.Mesh(hull(L * 0.62, u => prof(u * 0.62), 40, 28), skin); grp.add(front);
  const pivot = new THREE.Group(); pivot.position.x = L * 0.62; grp.add(pivot);
  const rear = new THREE.Mesh(hull(L * 0.38, u => prof(0.62 + u * 0.38), 26, 24), skin); pivot.add(rear);
  // Unterkiefer (schmal)
  const jaw = new THREE.Mesh(hull(4.4, u => [lerp(0.16, 0.32, u), lerp(0.18, 0.4, u), 2, 0], 16, 14), mat('#5d5c60', {roughness: 0.8})); jaw.position.set(0.5, -1.35, 0); grp.add(jaw);
  // Fluke
  const fs = new THREE.Shape(); fs.moveTo(0, 0); fs.bezierCurveTo(0.6, 0.6, 1.6, 1.9, 2.3, 2.1); fs.bezierCurveTo(1.7, 1.0, 1.4, 0.3, 1.5, 0); fs.bezierCurveTo(1.4, -0.3, 1.7, -1.0, 2.3, -2.1); fs.bezierCurveTo(1.6, -1.9, 0.6, -0.6, 0, 0);
  const fluke = new THREE.Mesh(new THREE.ExtrudeGeometry(fs, {depth: 0.12, bevelEnabled: true, bevelSize: 0.05, bevelThickness: 0.05, bevelSegments: 2}), skin);
  fluke.rotation.x = Math.PI / 2; fluke.position.set(L * 0.38 - 0.25, 0.06, 0); const flukeP = new THREE.Group(); flukeP.position.x = 0; pivot.add(flukeP); flukeP.add(fluke);
  // Brustflosse
  const fin = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8), skin); fin.scale.set(0.9, 0.08, 0.35); fin.position.set(4.6, -0.9, 1.15); fin.rotation.set(0.5, 0.3, -0.4); grp.add(fin);
  // Auge (klein, auf der Seite zur Kamera, +z)
  const eye = new THREE.Group(); eye.position.set(4.35, -0.75, 1.13); eye.scale.setScalar(1.6); grp.add(eye);
  mesh(new THREE.SphereGeometry(0.11, 16, 12), mat('#2a2526', {roughness: 0.5}), 0, 0, 0, eye).scale.set(1.3, 0.85, 0.4);
  mesh(new THREE.SphereGeometry(0.06, 16, 12), new THREE.MeshPhysicalMaterial({color: '#0a0a0c', roughness: 0.05, clearcoat: 1}), 0.01, 0, 0.035, eye);
  grp.userData = {pivot, flukeP, L};
  return grp;
}
export function swimWhale(w, T, amp = 0.12) { w.userData.pivot.rotation.z = amp * Math.sin(T * 1.6); w.userData.flukeP.rotation.z = amp * 1.4 * Math.sin(T * 1.6 - 0.8); }

// ---------- Riesenkalmar ----------
function squidSkin() {
  const r = rng(41);
  const t = canvasTex(256, 512, (g, w, h) => {
    g.fillStyle = '#a5402c'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 4000; i++) { g.fillStyle = r() < 0.5 ? 'rgba(120,30,25,0.5)' : 'rgba(225,130,95,0.35)'; g.beginPath(); g.arc(r() * w, r() * h, 1 + r() * 3, 0, 7); g.fill(); }
  });
  return t;
}
export function giantSquid() {
  const grp = new THREE.Group(); const skin = new THREE.MeshPhysicalMaterial({map: squidSkin(), roughness: 0.4, clearcoat: 0.6, clearcoatRoughness: 0.3, color: '#ffffff', sheen: 0.5, sheenColor: '#ffb69a', side: THREE.DoubleSide});
  // Mantel: zeigt nach hinten oben (lokal +x)
  const mantle = new THREE.Mesh(hull(2.6, u => { const r = u < 0.15 ? lerp(0.25, 0.34, u / 0.15) : lerp(0.34, 0.05, Math.pow((u - 0.15) / 0.85, 1.6)); return [r, r, 2, 0]; }, 30, 20), skin); grp.add(mantle);
  // Flossen am Mantelende
  const fin = mesh(new THREE.SphereGeometry(1, 12, 8), skin, 2.35, 0, 0, grp); fin.scale.set(0.3, 0.02, 0.32);
  // Kopf mit Augen
  const head = mesh(new THREE.SphereGeometry(0.3, 20, 16), skin, -0.15, 0, 0, grp); head.scale.set(1.2, 0.95, 1.0);
  const eyes = [];
  for (const s of [1, -1]) { const e = new THREE.Group(); e.position.set(-0.18, 0.02, s * 0.27); grp.add(e);
    mesh(new THREE.SphereGeometry(0.135, 24, 18), new THREE.MeshPhysicalMaterial({color: '#c9b98a', roughness: 0.15, metalness: 0.3, clearcoat: 1}), 0, 0, 0, e).scale.set(1, 1, 0.55);
    mesh(new THREE.SphereGeometry(0.085, 20, 14), new THREE.MeshPhysicalMaterial({color: '#050506', roughness: 0.02, clearcoat: 1}), 0, 0, s * 0.05, e).scale.set(1, 1, 0.5);
    eyes.push(e); }
  // 8 Arme + 2 lange Fangarme
  const arms = [];
  for (let i = 0; i < 10; i++) { const tb = new Tube(36, 10, i < 8 ? 0.075 : 0.045, 0.008, skin); grp.add(tb.mesh); arms.push(tb); }
  // Saugnäpfe für den Arm an der Scheibe (weltweit gesetzt)
  const sGeo = new THREE.CylinderGeometry(1, 0.8, 0.5, 14, 1, true); sGeo.rotateX(Math.PI / 2);
  const ring = new THREE.TorusGeometry(1, 0.22, 6, 14);
  const suck = new THREE.InstancedMesh(mergeGeometries([sGeo, ring]), new THREE.MeshPhysicalMaterial({color: '#f0c9b4', roughness: 0.3, clearcoat: 0.8, side: THREE.DoubleSide}), 40); suck.frustumCulled = false;
  grp.userData = {arms, eyes, suck};
  return grp;
}

// ---------- Anglerfisch (etwa handgroß, 15 cm) ----------
export function anglerfish() {
  const grp = new THREE.Group(); const skin = new THREE.MeshStandardMaterial({color: '#17110f', roughness: 0.9});
  const body = mesh(new THREE.SphereGeometry(0.06, 24, 18), skin, 0, 0, 0, grp); body.scale.set(1.15, 1.0, 0.9);
  const tail = mesh(new THREE.ConeGeometry(0.03, 0.07, 10), skin, 0.085, 0, 0, grp); tail.rotation.z = Math.PI / 2;
  const tfin = mesh(new THREE.SphereGeometry(0.03, 10, 6), skin, 0.13, 0, 0, grp); tfin.scale.set(0.6, 1.1, 0.12);
  // Maul: großer Unterkiefer nach vorn (-x)
  const jaw = mesh(new THREE.SphereGeometry(0.05, 20, 12, 0, Math.PI * 2, Math.PI * 0.5, Math.PI * 0.5), skin, -0.03, -0.006, 0, grp); jaw.scale.set(1.3, 0.9, 1.0);
  mesh(new THREE.SphereGeometry(0.045, 18, 10), mat('#0a0606', {roughness: 0.9}), -0.05, -0.003, 0, grp).scale.set(0.5, 0.55, 0.9); // Rachen
  // Zähne: lange, durchscheinende Nadeln
  const toothG = new THREE.ConeGeometry(0.0028, 0.03, 5);
  const teeth = new THREE.InstancedMesh(toothG, new THREE.MeshStandardMaterial({color: '#d9d4c4', roughness: 0.35, transparent: true, opacity: 0.8}), 22);
  const r = rng(8);
  for (let i = 0; i < 22; i++) { const up = i < 9; const n = up ? 9 : 13; const a = ((up ? i : i - 9) + r() * 0.5) / n * Math.PI * 0.9 - Math.PI * 0.45; const len = 0.35 + Math.pow(r(), 2) * 1.3;
    _p.set(-0.07 + Math.abs(Math.sin(a)) * 0.028, up ? 0.01 : -0.02, Math.sin(a) * 0.044);
    _e.set((r() - 0.5) * 0.5, 0, (up ? Math.PI + 0.35 : -0.45) + (r() - 0.5) * 0.4); _q.setFromEuler(_e); _s.set(0.8 + r() * 0.5, len, 0.8 + r() * 0.5); _m.compose(_p, _q, _s); teeth.setMatrixAt(i, _m); }
  grp.add(teeth);
  // Augen: winzig
  for (const s of [1, -1]) mesh(new THREE.SphereGeometry(0.006, 8, 6), mat('#cfd6da', {roughness: 0.2}), -0.04, 0.03, s * 0.035, grp);
  // Angel mit Leuchtköder
  const pts = [new THREE.Vector3(-0.01, 0.055, 0), new THREE.Vector3(-0.04, 0.11, 0), new THREE.Vector3(-0.09, 0.13, 0), new THREE.Vector3(-0.12, 0.11, 0)];
  mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 16, 0.0018, 5), skin, 0, 0, 0, grp);
  const lure = mesh(new THREE.SphereGeometry(0.009, 14, 10), new THREE.MeshBasicMaterial({color: '#bff4ff'}), -0.122, 0.104, 0, grp);
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex(), color: '#7fe3ff', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false}));
  glow.scale.set(0.035, 0.035, 1); lure.add(glow);
  const light = new THREE.PointLight('#8fe8ff', 0.25, 0.3, 2); lure.add(light);
  grp.userData = {lure, glow, light};
  return grp;
}
let _glow = null;
export function glowTex() {
  if (!_glow) _glow = canvasTex(128, 128, (g) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.2, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); });
  return _glow;
}

// ---------- Scheibenbauch (Tiefsee-Schneckenfisch), blass und durchscheinend ----------
export function snailfish() {
  const grp = new THREE.Group();
  const skin = new THREE.MeshStandardMaterial({color: '#f6e0d9', emissive: '#4a3431', roughness: 0.3, transparent: true, opacity: 0.88});
  const body = new THREE.Mesh(hull(0.3, u => { const r = u < 0.25 ? lerp(0.035, 0.05, Math.sqrt(u / 0.25)) : lerp(0.05, 0.004, Math.pow((u - 0.25) / 0.75, 0.9)); return [r, r * 0.8, 2, 0]; }, 30, 16), skin);
  grp.add(body);
  for (const s of [1, -1]) { // flügelartige Brustflossen
    const f = new THREE.Group(); f.position.set(0.07, -0.01, s * 0.035); grp.add(f);
    const m = mesh(new THREE.SphereGeometry(1, 14, 8), skin, 0.02, -0.01, s * 0.04, f); m.scale.set(0.05, 0.006, 0.045); f.userData.s = s; grp.userData[s > 0 ? 'finR' : 'finL'] = f; }
  for (const s of [1, -1]) mesh(new THREE.SphereGeometry(0.007, 10, 8), mat('#141214', {roughness: 0.1}), 0.02, 0.012, s * 0.034, grp); // Augen
  const dors = mesh(new THREE.SphereGeometry(1, 12, 6), skin, 0.18, 0.02, 0, grp); dors.scale.set(0.12, 0.018, 0.004);
  grp.userData.body = body;
  return grp;
}

// ---------- Tauchboot mit Greifarm und Pizzakarton ----------
function pizzaTex() {
  return canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#f3ede0'; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#c62e23'; g.lineWidth = 14; g.strokeRect(24, 24, w - 48, h - 48);
    g.fillStyle = '#c62e23'; g.font = 'bold 118px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('PIZZA', w / 2, h / 2 - 30);
    g.fillStyle = '#2f7d3a'; g.font = 'bold 44px sans-serif'; g.fillText('HEISS & FRISCH', w / 2, h / 2 + 70);
    g.fillStyle = 'rgba(120,90,50,0.25)'; for (let i = 0; i < 6; i++) { g.beginPath(); g.arc(80 + i * 70, 420 + (i % 2) * 20, 18, 0, 7); g.fill(); } // Fettflecken
  });
}
export function submersible() {
  const sub = new THREE.Group();
  const foam = new THREE.MeshStandardMaterial({color: '#f2c12e', roughness: 0.55});
  const frame = new THREE.MeshStandardMaterial({color: '#e6e6e1', roughness: 0.4, metalness: 0.3});
  const dark = new THREE.MeshStandardMaterial({color: '#25292c', roughness: 0.5, metalness: 0.4});
  // Auftriebskörper oben
  const top = mesh(new THREE.BoxGeometry(3.6, 1.0, 2.2), foam, 0, 1.35, 0, sub);
  mesh(new THREE.BoxGeometry(3.7, 0.12, 2.3), frame, 0, 0.8, 0, sub);
  // Druckkugel mit Bullauge (zeigt zur Kamera: +z)
  const sphere = mesh(new THREE.SphereGeometry(0.85, 32, 24), new THREE.MeshStandardMaterial({color: '#d9d9d4', metalness: 0.75, roughness: 0.3}), 0.4, 0, 0.1, sub);
  const port = mesh(new THREE.CylinderGeometry(0.22, 0.26, 0.12, 24), dark, 0.4, 0.05, 0.92, sub); port.rotation.x = Math.PI / 2;
  const win = mesh(new THREE.CircleGeometry(0.17, 24), new THREE.MeshBasicMaterial({color: '#ffcf8a'}), 0.4, 0.05, 0.985, sub);
  // Pilot im Bullauge: Kopf-Silhouette, winkt
  const pilot = new THREE.Group(); pilot.position.set(0.4, 0.0, 0.8); sub.add(pilot);
  mesh(new THREE.SphereGeometry(0.075, 14, 10), mat('#3a2a22'), 0, 0.02, 0, pilot);
  const hand = mesh(new THREE.SphereGeometry(0.03, 10, 8), mat('#d9a47e'), 0.1, 0.09, 0.03, pilot);
  // Rahmen, Kufen, Strahlruder
  for (const x of [-1.6, 1.6]) for (const z of [-0.95, 0.95]) mesh(new THREE.BoxGeometry(0.1, 1.6, 0.1), frame, x, 0.1, z, sub);
  for (const z of [-0.95, 0.95]) mesh(new THREE.BoxGeometry(3.6, 0.1, 0.12), frame, 0, -0.7, z, sub);
  for (const [x, z] of [[-1.85, 0.9], [-1.85, -0.9], [1.85, 0.9], [1.85, -0.9]]) { const th = mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.45, 18, 1, true), dark, x, 0.4, z, sub); th.rotation.z = Math.PI / 2; }
  // Scheinwerferleiste
  const lamps = [];
  for (const x of [-1.2, -0.6, 1.0, 1.5]) { const l = mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.08, 14), new THREE.MeshBasicMaterial({color: '#fffaf0'}), x, 0.72, 1.12, sub); l.rotation.x = Math.PI / 2; lamps.push(l);
    const gl = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex(), color: '#fff2da', transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.85})); gl.scale.set(0.45, 0.45, 1); gl.position.set(x, 0.72, 1.2); sub.add(gl); }
  const spot = new THREE.SpotLight('#fff1dc', 120, 30, 0.6, 0.6, 1.4); spot.position.set(0, 0.7, 1.2); sub.add(spot); sub.add(spot.target); spot.target.position.set(0, -0.5, 8);
  // Greifarm mit Pizzakarton (zeigt nach +z zur Scheibe)
  const arm = new THREE.Group(); arm.position.set(-1.0, -0.35, 1.0); sub.add(arm);
  const seg1 = mesh(new THREE.BoxGeometry(0.14, 0.14, 1.3), frame, 0, 0, 0.65, arm);
  const elbow = new THREE.Group(); elbow.position.set(0, 0, 1.3); arm.add(elbow);
  mesh(new THREE.SphereGeometry(0.1, 12, 10), dark, 0, 0, 0, elbow);
  mesh(new THREE.BoxGeometry(0.12, 0.12, 1.2), frame, 0, 0, 0.6, elbow);
  const wrist = new THREE.Group(); wrist.position.set(0, 0, 1.2); elbow.add(wrist);
  mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.12, 12), dark, 0, 0, 0.03, wrist).rotation.x = Math.PI / 2;
  for (const s of [1, -1]) mesh(new THREE.BoxGeometry(0.04, 0.03, 0.22), dark, s * 0.12, 0, 0.14, wrist);
  // Karton: steht senkrecht, Deckel zur Kamera
  const box = new THREE.Group(); box.position.set(0, 0, 0.3); box.scale.setScalar(1.35); wrist.add(box);
  const pt = pizzaTex(); const card = new THREE.MeshStandardMaterial({color: '#d8cdb6', roughness: 0.9});
  const lid = new THREE.MeshStandardMaterial({map: pt, roughness: 0.85});
  mesh(new THREE.BoxGeometry(0.42, 0.42, 0.05), [card, card, card, card, lid, card], 0, 0, 0, box);
  sub.userData = {arm, elbow, wrist, box, pilot, hand, spot, top, win};
  return sub;
}
