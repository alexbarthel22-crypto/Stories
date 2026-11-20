// Set "ubahn": stillgelegter U-Bahnhof "Färberplatz" unter der Altstadt, nur Notbeleuchtung.
// Bahnsteig: x -4.5 … 1.6 (Boden y = 0), Gleis: x 1.6 … 7.5 (Gleisbett y = -1.15, Gleismitte x = 3.75).
// Bahnsteig von z = +32 (Wartungsleiter / Schacht) bis z = -45 (Tunnelmund). Säulenreihe bei x = -1.0.
//
// Beat-Effekte (Feld "effekt"):
//   zug: {ab, dauer, von, nach}   -> Zug fährt aus dem Tunnel ein (z der Zugmitte, gleiche Kurve wie "laufen")
//   zug_tueren: Sekunden           -> Zugtüren gleiten auf
//   ratten: Sekunden               -> Rattenrudel huscht über den Bahnsteig
//   flackern: Sekunden             -> Notlichter + Neonröhre flackern heftig
//   luke: Sekunden                 -> Luke oben im Schacht geht auf (Licht fällt herein)
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, cracks, rng } from '../toon.js';
import { headlights } from './aussicht.js';

export const info = {
  start: [-2.6, 29.5],
  spots: {
    bahnsteig: [0, -4], tunnel: [0, -2], leiter: [180, 20], schacht: [180, 60], gleis: [-90, -18], wand: [90, -2],
    schild: [-90, 6], uhr: [0, 18], boden: [0, -60], zug: [-90, -4], decke: [0, 70],
  },
};

const PX0 = -4.5, PX1 = 1.6, TX = 3.75, TY = -1.15, WALL = 7.5, CEIL = 4.6, Z0 = 32, Z1 = -45;
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
const BOX = new THREE.BoxGeometry(1, 1, 1);
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
function instanced(geo, mat, items, inkW = 0.5) {
  if (!items.length) return new THREE.Group();
  const m = inkW ? inkInstanced(geo, mat, items.length, inkW) : new THREE.InstancedMesh(geo, mat, items.length);
  items.forEach((it, i) => { E.set(it.rx || 0, it.ry || 0, it.rz || 0); Q.setFromEuler(E); m.setMatrixAt(i, M4.compose(P.set(...it.p), Q, S.set(...(it.s || [1, 1, 1])))); if (it.c) m.setColorAt(i, C.set(it.c)); });
  m.castShadow = true; m.receiveShadow = true; return m;
}

export function build(scene, seed = 21, ctx = {}) {
  const beats = ctx.beats || [];
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o) => (root.add(o), o);
  scene.fog = new THREE.Fog('#07080c', 9, 62); scene.background = new THREE.Color('#050507');
  const glowTex = canvasTex(64, 64, (c, w) => { const g = c.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(0, 0, w, w); });
  const glow = (col, size, op = 0.5) => { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: col, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false, fog: false })); m.scale.set(size, size, 1); return m; };

  // ---------- Texturen ----------
  const tiles = (base, band) => canvasTex(512, 512, (c, w, h) => {
    c.fillStyle = '#3a3a34'; c.fillRect(0, 0, w, h);
    for (let y = 0; y < h; y += 32) for (let x = (y / 32) % 2 * 16; x < w + 32; x += 64) { c.fillStyle = r() < 0.06 ? '#9a9888' : base; c.fillRect(x - 32 + 2, y + 2, 60, 28); c.fillStyle = 'rgba(255,255,255,0.12)'; c.fillRect(x - 30, y + 3, 56, 4); }
    if (band) { c.fillStyle = band; c.fillRect(0, h * 0.62, w, 40); c.fillStyle = 'rgba(0,0,0,0.3)'; for (let x = 0; x < w; x += 64) c.fillRect(x, h * 0.62, 2, 40); }
    stains(c, w, h, r, 26, '60,50,30', 0.35); stains(c, w, h, r, 10, '30,40,30', 0.3);
    for (let i = 0; i < 14; i++) { const x = r() * w, len = h * (0.1 + r() * 0.5); const g = c.createLinearGradient(0, 0, 0, len); g.addColorStop(0, 'rgba(70,60,40,0.4)'); g.addColorStop(1, 'rgba(70,60,40,0)'); c.fillStyle = g; c.fillRect(x, 0, 3 + r() * 6, len); }
    c.strokeStyle = 'rgba(20,20,15,0.6)'; cracks(c, w, h, r, 5, 1.5);
  }, { repeat: [12, 1] });
  const floorTex = canvasTex(512, 512, (c, w, h) => {
    c.fillStyle = '#6a665c'; c.fillRect(0, 0, w, h); c.strokeStyle = 'rgba(30,28,24,0.6)'; c.lineWidth = 2;
    for (let i = 0; i <= 8; i++) { c.beginPath(); c.moveTo(0, i * 64); c.lineTo(w, i * 64); c.stroke(); c.beginPath(); c.moveTo(i * 64, 0); c.lineTo(i * 64, h); c.stroke(); }
    stains(c, w, h, r, 30, '30,28,22', 0.4); cracks(c, w, h, r, 8, 2);
    c.fillStyle = 'rgba(200,190,160,0.12)'; for (let i = 0; i < 300; i++) c.fillRect(r() * w, r() * h, 2, 2);
  }, { repeat: [2, 26] });
  const gravel = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#2a2824'; c.fillRect(0, 0, w, h); for (let i = 0; i < 1600; i++) { c.fillStyle = ['#4a463e', '#3a3832', '#5a554a', '#26241f'][(r() * 4) | 0]; c.beginPath(); c.ellipse(r() * w, r() * h, 2 + r() * 3, 1.5 + r() * 2, r() * 3, 0, 7); c.fill(); } stains(c, w, h, r, 12, '10,10,8', 0.5); }, { repeat: [3, 60] });

  // ---------- Bahnsteig, Gleis, Wände, Decke ----------
  const len = Z0 - Z1, zc = (Z0 + Z1) / 2;
  const floor = add(new THREE.Mesh(new THREE.PlaneGeometry(PX1 - PX0, len), toon('#ffffff', { map: floorTex }))); floor.rotation.x = -Math.PI / 2; floor.position.set((PX0 + PX1) / 2, 0, zc); floor.receiveShadow = true;
  const edge = add(edges(ink(new THREE.BoxGeometry(0.4, 1.15, len, 1, 1, 40), toon('#8a8576'), 0.6))); edge.position.set(PX1 - 0.2, -0.575, zc);
  const yl = add(new THREE.Mesh(new THREE.PlaneGeometry(0.25, len), toon('#d8b42a'))); yl.rotation.x = -Math.PI / 2; yl.position.set(PX1 - 0.55, 0.004, zc);
  const dots = []; for (let z = Z1 + 0.5; z < Z0; z += 0.6) dots.push({ p: [PX1 - 0.55, 0.01, z], s: [0.04, 0.012, 0.04], c: '#a8861a' });
  add(instanced(new THREE.CylinderGeometry(1, 1, 1, 6), toon('#ffffff'), dots, 0));
  const bed = add(new THREE.Mesh(new THREE.PlaneGeometry(WALL - PX1, 260), toon('#ffffff', { map: gravel }))); bed.rotation.x = -Math.PI / 2; bed.position.set((PX1 + WALL) / 2, TY, -30); bed.receiveShadow = true;
  const sleepers = []; for (let z = -170; z < 110; z += 0.75) sleepers.push({ p: [TX, TY + 0.06, z], s: [2.6, 0.12, 0.24], c: r() < 0.5 ? '#3a2e22' : '#463828' });
  add(instanced(BOX, toon('#ffffff'), sleepers, 0));
  for (const x of [TX - 0.72, TX + 0.72]) { const rail = add(ink(new THREE.BoxGeometry(0.07, 0.16, 280), toon('#8a8a8e'), 0.5)); rail.position.set(x, TY + 0.2, -30); }
  const third = add(ink(new THREE.BoxGeometry(0.25, 0.12, 280), toon('#c8a020'), 0.5)); third.position.set(TX + 1.6, TY + 0.35, -30);
  // Wände (Fliesen), Decke mit Trägern, Kabelpritschen
  const backWall = add(new THREE.Mesh(new THREE.PlaneGeometry(len, CEIL), toon('#ffffff', { map: tiles('#d8cfae', '#3a6a4a') }))); backWall.position.set(PX0, CEIL / 2, zc); backWall.rotation.y = Math.PI / 2; backWall.receiveShadow = true;
  const farWall = add(new THREE.Mesh(new THREE.PlaneGeometry(len + 4, CEIL - TY), toon('#ffffff', { map: tiles('#cfc6a2', '#3a6a4a') }))); farWall.position.set(WALL, (CEIL + TY) / 2, zc); farWall.rotation.y = -Math.PI / 2;
  const ceilM = toon('#3a3a36'); const ceilPl = (x0, x1, z0, z1) => { const c = add(new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, z1 - z0), ceilM)); c.rotation.x = Math.PI / 2; c.position.set((x0 + x1) / 2, CEIL, (z0 + z1) / 2); };
  ceilPl(PX0, WALL, Z1, Z0 - 1.45); ceilPl(PX0, -3.7, Z0 - 1.45, Z0); ceilPl(-2.3, WALL, Z0 - 1.45, Z0);
  const beams = []; for (let z = Z1; z <= Z0; z += 3.5) beams.push({ p: [(PX0 + WALL) / 2, CEIL - 0.18, z], s: [WALL - PX0, 0.36, 0.3], c: '#4a5048' });
  add(instanced(BOX, toon('#ffffff'), beams, 0.6));
  for (const [x, y] of [[PX0 + 0.2, 3.9], [WALL - 0.2, 3.7], [WALL - 0.2, 3.45]]) { const tray = add(ink(new THREE.BoxGeometry(0.3, 0.08, len), toon('#5a5a52'), 0.5)); tray.position.set(x, y, zc); const cab = add(new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, len, 6), toon('#1a1a1a'))); cab.rotation.x = Math.PI / 2; cab.position.set(x, y + 0.08, zc); }
  // lose hängende Kabel
  for (let i = 0; i < 6; i++) { const z = Z1 + 6 + r() * (len - 12), x = PX0 + 0.5 + r() * 5; const pts = []; for (let k = 0; k <= 8; k++) { const t = k / 8; pts.push(new THREE.Vector3(x + t * 1.6, CEIL - 0.1 - Math.sin(Math.PI * t) * (0.6 + r() * 0.5), z + t * 0.3)); } add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 12, 0.018, 4), toon('#151515'))); }
  // Stirnwände über den Tunnelmündern + Tunnel
  for (const [z, s] of [[Z0, 1], [Z1, -1]]) {
    const w1 = add(new THREE.Mesh(new THREE.PlaneGeometry(PX1 - PX0, CEIL), toon('#ffffff', { map: tiles('#d0c8a8', null) }))); w1.position.set((PX0 + PX1) / 2, CEIL / 2, z); w1.rotation.y = s > 0 ? Math.PI : 0;
    const w2 = add(new THREE.Mesh(new THREE.PlaneGeometry(WALL - PX1, CEIL - 2.9), toon('#2f2f2a'))); w2.position.set((PX1 + WALL) / 2, 2.9 + (CEIL - 2.9) / 2, z); w2.rotation.y = s > 0 ? Math.PI : 0;
  }
  const tunnelGeo = new THREE.CylinderGeometry(3.4, 3.4, 1, 24, 1, true); tunnelGeo.rotateX(Math.PI / 2);
  const tunTex = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#2a2a26'; c.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 16) { c.fillStyle = 'rgba(0,0,0,0.35)'; c.fillRect(0, y, w, 2); } stains(c, w, h, r, 20, '10,10,8', 0.5); stains(c, w, h, r, 8, '60,50,30', 0.3); }, { repeat: [6, 20] });
  for (const [z0, z1] of [[Z1, -175], [Z0, 115]]) { const t = add(new THREE.Mesh(tunnelGeo, toon('#ffffff', { map: tunTex, side: THREE.BackSide }))); t.scale.set(1, 1, Math.abs(z1 - z0)); t.position.set(TX, TY + 0.6, (z0 + z1) / 2); }
  for (const z of [-175, 115]) { const cap = add(new THREE.Mesh(new THREE.PlaneGeometry(8, 8), new THREE.MeshBasicMaterial({ color: '#000000' }))); cap.position.set(TX, 0, z); if (z > 0) cap.rotation.y = Math.PI; }

  // ---------- Säulen mit Nieten, Graffiti ----------
  const pillars = [];
  for (let z = Z0 - 4; z > Z1 + 2; z -= 7) pillars.push(z);
  const pilTex = canvasTex(64, 256, (c, w, h) => { c.fillStyle = '#ffffff'; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(0,0,0,0.35)'; for (let y = 8; y < h; y += 18) { c.beginPath(); c.arc(8, y, 2.5, 0, 7); c.fill(); c.beginPath(); c.arc(w - 8, y, 2.5, 0, 7); c.fill(); } stains(c, w, h, r, 8, '90,60,30', 0.45); });
  for (const z of pillars) {
    const p = add(edges(ink(new THREE.BoxGeometry(0.42, CEIL, 0.42), toon('#3f6a52', { map: pilTex }), 0.8))); p.position.set(-1.0, CEIL / 2, z);
    const base = add(ink(new THREE.BoxGeometry(0.6, 0.25, 0.6), toon('#2f4a3a'), 0.6)); base.position.set(-1.0, 0.125, z);
  }
  // ---------- Bahnsteig-Möbel ----------
  const bench = (z) => { const g = new THREE.Group(); add(g); g.position.set(PX0 + 0.45, 0, z); const w = toon('#7a4e2c'); for (let k = 0; k < 4; k++) { const s = ink(new THREE.BoxGeometry(0.11, 0.04, 1.8), w, 0.4); s.position.set(-0.15 + k * 0.12, 0.45, 0); g.add(s); } for (let k = 0; k < 2; k++) { const b = ink(new THREE.BoxGeometry(0.04, 0.11, 1.8), w, 0.4); b.position.set(-0.32, 0.65 + k * 0.14, 0); g.add(b); } for (const dz of [-0.75, 0.75]) { const l = ink(new THREE.BoxGeometry(0.5, 0.45, 0.06), toon('#2a2a2a'), 0.4); l.position.set(-0.05, 0.22, dz); g.add(l); } return g; };
  [20, 6, -8, -22, -36].forEach((z, i) => { const b = bench(z + 3.5); if (i === 2) { b.rotation.z = 0.08; b.children[1].rotation.x = 0.3; } });
  const bins = []; for (const z of [24, 10, -4, -18, -32]) bins.push({ p: [PX0 + 0.3, 0.45, z], s: [0.45, 0.9, 0.45], c: '#c8501e' });
  add(instanced(new THREE.CylinderGeometry(0.5, 0.45, 1, 10), toon('#ffffff'), bins, 0.6));
  // Fahrkartenautomat + Kiosk mit Rolladen
  const automat = add(edges(ink(new THREE.BoxGeometry(0.5, 1.8, 0.9), toon('#c84a2a'), 0.7))); automat.position.set(PX0 + 0.25, 0.9, 16);
  const automatScr = add(new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.35), toon('#1a2230'))); automatScr.position.set(PX0 + 0.51, 1.3, 16); automatScr.rotation.y = Math.PI / 2;
  const kioskTex = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#7a7a72'; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(0,0,0,0.3)'; for (let y = 0; y < h; y += 10) c.fillRect(0, y, w, 3); c.font = '900 52px Inter, sans-serif'; c.fillStyle = '#e8507a'; c.strokeStyle = '#111'; c.lineWidth = 8; c.save(); c.translate(w / 2, h / 2); c.rotate(-0.15); c.textAlign = 'center'; c.strokeText('KRAH', 0, 0); c.fillText('KRAH', 0, 0); c.restore(); });
  const kiosk = add(edges(ink(new THREE.BoxGeometry(1.2, 2.6, 3.2), toon('#ffffff', { map: kioskTex }), 0.7))); kiosk.position.set(PX0 + 0.6, 1.3, -14);
  const kioskSign = add(new THREE.Mesh(new THREE.PlaneGeometry(3.2, 0.45), toon('#ffffff', { map: canvasTex(512, 72, (c, w, h) => { c.fillStyle = '#1f3a6a'; c.fillRect(0, 0, w, h); c.fillStyle = '#f0e0a0'; c.font = '900 46px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('ZEITUNGEN · TABAK', w / 2, h / 2 + 2); }) }))); kioskSign.position.set(PX0 + 1.21, 2.75, -14); kioskSign.rotation.y = Math.PI / 2;
  // Zeitungen am Boden, Pfützen
  const papers = []; for (let i = 0; i < 14; i++) papers.push({ p: [PX0 + 0.6 + r() * 4.5, 0.006 + i * 0.0005, Z1 + 4 + r() * (len - 8)], s: [0.42, 0.003, 0.6], ry: r() * 3, c: r() < 0.7 ? '#d8d0b8' : '#b8b098' });
  add(instanced(BOX, toon('#ffffff'), papers, 0));
  const pudMat = new THREE.MeshBasicMaterial({ color: '#1a1e26' });
  const drips = [[-2.4, 12.5], [0.4, 3.2], [-3.2, -9.5], [-0.2, -15.5], [-2.0, -27.5], [0.8, 20.5]];
  for (const [x, z] of drips) { const p = add(new THREE.Mesh(new THREE.CircleGeometry(1, 20), pudMat)); p.rotation.x = -Math.PI / 2; p.scale.set(0.7 + r() * 0.5, 0.45 + r() * 0.3, 1); p.position.set(x, 0.008, z); }
  // ---------- Schilder, Plakate, Uhr ----------
  const nameTex = canvasTex(1024, 160, (c, w, h) => { c.fillStyle = '#1d3f7a'; c.fillRect(0, 0, w, h); c.strokeStyle = '#e8e8e0'; c.lineWidth = 10; c.strokeRect(10, 10, w - 20, h - 20); c.fillStyle = '#f2f2ea'; c.font = '900 100px Inter, "Liberation Sans", sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('FÄRBERPLATZ', w / 2, h / 2 + 6); stains(c, w, h, r, 12, '80,60,30', 0.35); });
  const sign = (x, z, ry, s = 1) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(4.2 * s, 0.66 * s), toon('#ffffff', { map: nameTex }))); m.position.set(x, 2.7, z); m.rotation.y = ry; return m; };
  for (const z of [22, -2, -26]) { sign(WALL - 0.02, z, -Math.PI / 2, 1.3); sign(PX0 + 0.02, z + 7, Math.PI / 2); }
  const poster = (title, sub, bg, fg, year) => canvasTex(256, 360, (c, w, h) => { c.fillStyle = bg; c.fillRect(0, 0, w, h); c.fillStyle = fg; c.textAlign = 'center'; c.font = '900 40px Inter, sans-serif'; c.fillText(title, w / 2, 90); c.font = '700 24px Inter, sans-serif'; c.fillText(sub, w / 2, 140); c.fillStyle = 'rgba(255,255,255,0.25)'; c.beginPath(); c.arc(w / 2, 240, 60, 0, 7); c.fill(); c.fillStyle = fg; c.font = '700 22px Inter, sans-serif'; c.fillText(year, w / 2, 335); stains(c, w, h, r, 10, '60,50,30', 0.4); c.fillStyle = 'rgba(0,0,0,0.5)'; c.beginPath(); c.moveTo(w, 0); c.lineTo(w - 70, 0); c.lineTo(w, 90); c.fill(); });
  const posters = [['KINO APOLLO', 'Der Weiße Hai', '#2a3a6a', '#f0d040', '1979'], ['KAUFHAUS MERKUR', 'Sommerschluss', '#c83a2a', '#fff', '1980'], ['STADTWERKE', 'Strom für alle', '#e8c020', '#1a1a1a', '1981'], ['FAHR MIT!', 'U-Bahn – schneller ans Ziel', '#2a7a4a', '#fff', '1978'], ['BADEN IM SEE', 'Strandbad Süd', '#4a9ad0', '#fff', '1980']];
  for (let i = 0; i < 9; i++) { const p = posters[i % posters.length]; const m = add(new THREE.Mesh(new THREE.PlaneGeometry(1.6, 2.25), toon('#ffffff', { map: poster(...p) }))); m.position.set(WALL - 0.03, 1.6, 26 - i * 8 + 3.5); m.rotation.y = -Math.PI / 2; }
  const mapTex = canvasTex(512, 300, (c, w, h) => { c.fillStyle = '#f0ece0'; c.fillRect(0, 0, w, h); const cols = ['#d03a2a', '#2a6ad0', '#2aa04a', '#e0a020']; cols.forEach((col, k) => { c.strokeStyle = col; c.lineWidth = 8; c.beginPath(); let x = 20, y = 40 + k * 60; c.moveTo(x, y); for (let i = 0; i < 6; i++) { x += 80; y += (r() - 0.5) * 70; c.lineTo(x, y); } c.stroke(); }); c.fillStyle = '#111'; c.font = '900 26px Inter, sans-serif'; c.fillText('LINIENNETZ 1981', 20, h - 16); c.fillStyle = '#d03a2a'; c.beginPath(); c.arc(260, 150, 12, 0, 7); c.fill(); c.font = '700 16px Inter, sans-serif'; c.fillText('Sie sind hier', 278, 156); stains(c, w, h, r, 10, '80,60,30', 0.3); });
  const map = add(new THREE.Mesh(new THREE.PlaneGeometry(2.4, 1.4), toon('#ffffff', { map: mapTex }))); map.position.set(PX0 + 0.03, 1.6, 2); map.rotation.y = Math.PI / 2;
  // Bahnhofsuhr (steht auf 18:30)
  const clockTex = canvasTex(128, 128, (c, w) => { c.fillStyle = '#f2efe4'; c.beginPath(); c.arc(64, 64, 60, 0, 7); c.fill(); c.lineWidth = 7; c.strokeStyle = '#1a1a1a'; c.stroke(); c.fillStyle = '#111'; for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; c.fillRect(64 + Math.sin(a) * 46 - 3, 64 - Math.cos(a) * 46 - 7, 6, 14); } c.lineCap = 'round'; c.strokeStyle = '#111'; c.lineWidth = 8; c.beginPath(); c.moveTo(64, 64); c.lineTo(64 + Math.sin(6.283 * 6.5 / 12) * 28, 64 - Math.cos(6.283 * 6.5 / 12) * 28); c.stroke(); c.lineWidth = 5; c.beginPath(); c.moveTo(64, 64); c.lineTo(64, 106); c.stroke(); });
  const clk = add(new THREE.Group()); clk.position.set(-1.0, 3.6, 4);
  const clkBody = ink(new THREE.CylinderGeometry(0.42, 0.42, 0.12, 24), toon('#1a1a1a'), 0.6); clkBody.rotation.x = Math.PI / 2; clk.add(clkBody);
  for (const s of [1, -1]) { const f = new THREE.Mesh(new THREE.CircleGeometry(0.38, 24), toon('#ffffff', { map: clockTex })); f.position.z = s * 0.065; if (s < 0) f.rotation.y = Math.PI; clk.add(f); }
  const clkRod = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.6, 6), toon('#1a1a1a')); clkRod.position.y = 0.7; clk.add(clkRod);
  // Notausgang-Schild + Wartungsleiter + Schacht am Ende z = +32
  const exitTex = canvasTex(256, 96, (c, w, h) => { c.fillStyle = '#1a9a4a'; c.fillRect(0, 0, w, h); c.fillStyle = '#fff'; c.font = '900 34px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('NOTAUSGANG', w / 2 + 18, h / 2); c.fillRect(20, 30, 20, 40); });
  const exitSign = add(new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.34, 0.08), new THREE.MeshBasicMaterial({ map: exitTex }))); exitSign.position.set(-1.6, 3.4, Z0 - 0.06);
  const exitGlow = add(glow('#30ff80', 2.2, 0.35)); exitGlow.position.set(-1.6, 3.4, Z0 - 0.3);
  const ladder = new THREE.Group(); add(ladder); ladder.position.set(-3.0, 0, Z0 - 0.25);
  for (const x of [-0.25, 0.25]) { const s = ink(new THREE.BoxGeometry(0.05, 9.5, 0.05), toon('#6a6a62'), 0.5); s.position.set(x, 4.75, 0); ladder.add(s); }
  for (let y = 0.3; y < 9.4; y += 0.3) { const rung = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.5, 6), toon('#6a6a62')); rung.rotation.z = Math.PI / 2; rung.position.set(0, y, 0); ladder.add(rung); }
  // Schacht in der Decke über der Leiter
  const shaft = add(new THREE.Mesh(new THREE.BoxGeometry(1.4, 5, 1.4), toon('#2a2a26', { side: THREE.BackSide }))); shaft.position.set(-3.0, CEIL + 2.5, Z0 - 0.7);
  const hatchPiv = add(new THREE.Group()); hatchPiv.position.set(-3.7, CEIL + 5.0, Z0 - 0.7);
  const hatch = ink(new THREE.BoxGeometry(1.4, 0.08, 1.4), toon('#4a4a44'), 0.6); hatch.position.set(0.7, 0, 0); hatchPiv.add(hatch);
  const shaftLight = add(new THREE.Mesh(new THREE.ConeGeometry(0.9, 5.5, 16, 1, true), new THREE.MeshBasicMaterial({ color: '#ffe0b0', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false }))); shaftLight.position.set(-3.0, CEIL + 2.2, Z0 - 0.7);
  // Signal am Tunnelmund (rot -> grün, wenn der Zug kommt)
  const sigPost = add(ink(new THREE.BoxGeometry(0.3, 0.8, 0.2), toon('#1a1a1a'), 0.6)); sigPost.position.set(WALL - 0.6, 1.4, Z1 - 1);
  const sigRed = add(new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), new THREE.MeshBasicMaterial({ color: '#ff2a1a' }))); sigRed.position.set(WALL - 0.6, 1.6, Z1 - 0.88);
  const sigGreen = add(new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), new THREE.MeshBasicMaterial({ color: '#20ff60' }))); sigGreen.position.set(WALL - 0.6, 1.3, Z1 - 0.88);
  const sigGlowR = add(glow('#ff3020', 1.2, 0.6)); sigGlowR.position.copy(sigRed.position); const sigGlowG = add(glow('#30ff70', 1.4, 0.7)); sigGlowG.position.copy(sigGreen.position);

  // ---------- Licht: Notlampen (rot), eine flackernde Neonröhre ----------
  const emerg = [];
  for (const [x, z] of [[PX0 + 0.08, 18], [PX0 + 0.08, -6], [PX0 + 0.08, -30], [WALL - 0.08, 6], [WALL - 0.08, -18]]) {
    const box = add(new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.2, 0.4), new THREE.MeshBasicMaterial({ color: '#ff3a24' }))); box.position.set(x, 3.4, z);
    const g = add(glow('#ff3a24', 2.4, 0.45)); g.position.set(x + (x < 0 ? 0.2 : -0.2), 3.4, z);
    const l = add(new THREE.PointLight('#ff4a2a', 3.8, 0, 1.5)); l.position.set(x + (x < 0 ? 0.5 : -0.5), 3.2, z);
    emerg.push({ box, g, l, ph: r() * 10 });
  }
  const tubes = []; for (let z = Z0 - 6; z > Z1; z -= 7) tubes.push({ p: [-1.0, CEIL - 0.42, z + 3.5], s: [0.12, 0.08, 1.8], c: '#8a8a84' });
  add(instanced(BOX, toon('#ffffff'), tubes, 0.4));
  const neon = add(new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.06, 1.7), new THREE.MeshBasicMaterial({ color: '#e8fff4' }))); neon.position.set(-1.0, CEIL - 0.47, -0.5);
  const neonL = add(new THREE.PointLight('#d8fff0', 0, 0, 1.6)); neonL.position.set(-1.0, CEIL - 0.8, -0.5);
  const neonG = add(glow('#c8ffe8', 3.5, 0)); neonG.position.set(-1.0, CEIL - 0.6, -0.5);
  // Spinnweben
  for (let i = 0; i < 10; i++) { const z = Z1 + r() * len; const web = add(new THREE.Mesh(new THREE.PlaneGeometry(0.8, 0.8), new THREE.MeshBasicMaterial({ map: canvasTex(128, 128, (c, w) => { c.strokeStyle = 'rgba(220,220,210,0.55)'; c.lineWidth = 1.2; for (let k = 0; k < 7; k++) { c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.cos(k / 6 * 1.57) * w, Math.sin(k / 6 * 1.57) * w); c.stroke(); } for (let rr = 15; rr < w; rr += 15) { c.beginPath(); c.arc(0, 0, rr, 0, 1.57); c.stroke(); } }), transparent: true, depthWrite: false, side: THREE.DoubleSide }))); web.position.set(PX0 + 0.02, CEIL - 0.4, z); web.rotation.set(0, Math.PI / 2, Math.PI); }

  // ---------- Tropfen von der Decke ----------
  const dropMat = new THREE.MeshBasicMaterial({ color: '#9ab0c8', transparent: true, opacity: 0.8 });
  const dropMeshes = drips.map(([x, z], i) => { const d = add(new THREE.Mesh(new THREE.SphereGeometry(0.018, 6, 4), dropMat)); d.scale.y = 2.2; d.userData = { x, z, per: 1.3 + (i % 3) * 0.45, ph: i * 0.37 }; return d; });
  const ringGeo = new THREE.RingGeometry(0.7, 1, 20), ringMat = new THREE.MeshBasicMaterial({ color: '#8aa0c0', transparent: true, depthWrite: false, side: THREE.DoubleSide });
  const rings = drips.map(([x, z]) => { const m = add(new THREE.Mesh(ringGeo, ringMat.clone())); m.rotation.x = -Math.PI / 2; m.position.set(x, 0.012, z); return m; });
  // Staub im Licht
  const dust = (() => { const N = 700, pos = new Float32Array(N * 3); for (let i = 0; i < N; i++) pos.set([Math.random(), Math.random(), Math.random()], i * 3);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const m = new THREE.ShaderMaterial({ uniforms: { uT: { value: 0 }, uEye: { value: new THREE.Vector3() }, uPx: { value: 768 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: `uniform float uT, uPx; uniform vec3 uEye; varying float vA; void main(){ vec3 p = position * vec3(10.0, 4.2, 10.0);
        p.x += sin(uT * 0.3 + position.y * 20.0) * 0.4; p.y = mod(p.y + uT * 0.05, 4.2) + 0.1; p.z += cos(uT * 0.25 + position.x * 17.0) * 0.4;
        p.x = uEye.x + mod(p.x - uEye.x + 5.0, 10.0) - 5.0; p.z = uEye.z + mod(p.z - uEye.z + 5.0, 10.0) - 5.0;
        vA = 0.25 + 0.2 * sin(uT * 2.0 + position.z * 50.0); vec4 mv = modelViewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = max(1.0, 0.025 * uPx / -mv.z); }`,
      fragmentShader: `varying float vA; void main(){ float d = length(gl_PointCoord - 0.5); if (d > 0.5) discard; gl_FragColor = vec4(0.9, 0.85, 0.7, vA * (1.0 - d * 2.0)); }` });
    const p = new THREE.Points(g, m); p.frustumCulled = false; add(p); return m; })();

  // ---------- Ratten ----------
  const ratGeo = new THREE.CapsuleGeometry(0.08, 0.2, 3, 6); ratGeo.rotateX(Math.PI / 2);
  const NR = 7, rats = inkInstanced(ratGeo, toon('#2a2420'), NR, 0.5); add(rats); rats.frustumCulled = false;
  const tailGeo = new THREE.CylinderGeometry(0.006, 0.012, 0.16, 4); tailGeo.rotateX(Math.PI / 2); tailGeo.translate(0, 0, -0.16);
  const tails = new THREE.InstancedMesh(tailGeo, toon('#c89a8a'), NR); add(tails); tails.frustumCulled = false;
  const ratEyes = new THREE.InstancedMesh(new THREE.SphereGeometry(0.012, 6, 4), new THREE.MeshBasicMaterial({ color: '#ff5a3a' }), NR * 2); add(ratEyes); ratEyes.frustumCulled = false;

  // ---------- Der Zug ----------
  const train = new THREE.Group(); add(train); train.visible = false;
  const yellow = toon('#d8b43a'), grey = toon('#6a6a68'), dark = toon('#1c1e22'), inner = toon('#b8c8b8', { side: THREE.BackSide });
  const doorLeaves = [], carLights = [];
  const destTex = canvasTex(256, 48, (c, w, h) => { c.fillStyle = '#111'; c.fillRect(0, 0, w, h); c.fillStyle = '#ffa020'; c.font = '900 30px "Courier New", monospace'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('SONDERFAHRT', w / 2, h / 2 + 2); });
  for (let k = 0; k < 2; k++) {
    const car = new THREE.Group(); car.position.z = -k * 15.6; train.add(car);
    const L = 15, Wd = 2.7, xs = -Wd / 2; // Plattform-Seite = -X (lokal)
    const low = ink(new THREE.BoxGeometry(Wd, 1.0, L), yellow, 0.8); low.position.y = -0.45; car.add(low);
    const top = ink(new THREE.BoxGeometry(Wd, 0.55, L), yellow, 0.8); top.position.y = 2.15; car.add(top);
    const roof = ink(new THREE.BoxGeometry(Wd - 0.2, 0.2, L), grey, 0.6); roof.position.y = 2.52; car.add(roof);
    const stripe = new THREE.Mesh(new THREE.BoxGeometry(Wd + 0.02, 0.12, L), toon('#2a5a3a')); stripe.position.y = 0.0; car.add(stripe);
    const skirt = ink(new THREE.BoxGeometry(Wd - 0.3, 0.5, L - 1), dark, 0.5); skirt.position.y = -1.1; car.add(skirt);
    // Fenstersäulen + Türen auf beiden Seiten
    for (const side of [-1, 1]) {
      for (let z = -L / 2 + 0.25; z <= L / 2; z += 1.6) { const doorZone = [-4.5, 4.5].some((d) => Math.abs(z - d) < 0.9); if (doorZone) continue; const p = ink(new THREE.BoxGeometry(0.06, 1.35, 0.22), yellow, 0.5); p.position.set(side * Wd / 2, 1.2, z); car.add(p); }
      for (const [g0, g1] of [[-L / 2, -5.25], [-3.75, 3.75], [5.25, L / 2]]) { const glass = new THREE.Mesh(new THREE.PlaneGeometry(g1 - g0, 1.35), new THREE.MeshBasicMaterial({ color: '#cfe8dc', transparent: true, opacity: 0.14, depthWrite: false, side: THREE.DoubleSide })); glass.position.set(side * (Wd / 2 + 0.005), 1.2, (g0 + g1) / 2); glass.rotation.y = Math.PI / 2; car.add(glass); }
      for (const dz of [-4.5, 4.5]) for (const s of [-1, 1]) {
        const leaf = ink(new THREE.BoxGeometry(0.06, 2.2, 0.68), toon('#c8a42a'), 0.6); leaf.position.set(side * (Wd / 2 + 0.02), 0.65, dz + s * 0.35); car.add(leaf);
        const win = new THREE.Mesh(new THREE.PlaneGeometry(0.45, 0.8), new THREE.MeshBasicMaterial({ color: '#d8f0e4', transparent: true, opacity: 0.35 })); win.position.set(side * 0.035, 0.45, 0); win.rotation.y = Math.PI / 2; leaf.add(win);
        if (side < 0) doorLeaves.push({ leaf, z0: dz + s * 0.35, s });
      }
    }
    // Innenraum: Wände, Deckenlicht, Sitze, Haltestangen
    const inBox = new THREE.Mesh(new THREE.BoxGeometry(Wd - 0.12, 2.0, L - 0.1), inner); inBox.position.y = 0.95; car.add(inBox);
    const floorIn = new THREE.Mesh(new THREE.PlaneGeometry(Wd - 0.12, L - 0.1), toon('#4a4a44')); floorIn.rotation.x = -Math.PI / 2; floorIn.position.y = 0.0; car.add(floorIn);
    for (const x of [-0.6, 0.6]) { const lamp = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.04, L - 1), new THREE.MeshBasicMaterial({ color: '#e8fff2' })); lamp.position.set(x, 1.92, 0); car.add(lamp); }
    const cl = new THREE.PointLight('#d8ffe8', 6, 0, 1.4); cl.position.set(0, 1.7, 0); car.add(cl); carLights.push(cl);
    for (let z = -6.5; z <= 6.5; z += 1.3) { if (Math.abs(Math.abs(z) - 4.5) < 0.8) continue; for (const x of [-0.95, 0.95]) { const seat = ink(new THREE.BoxGeometry(0.5, 0.12, 0.9), toon('#2a4a8a'), 0.4); seat.position.set(x, 0.45, z); car.add(seat); const back = ink(new THREE.BoxGeometry(0.08, 0.6, 0.9), toon('#2a4a8a'), 0.4); back.position.set(x * 1.25, 0.75, z); car.add(back); } }
    for (const z of [-4.5, 4.5]) { const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.95, 6), toon('#c8c8c8')); pole.position.set(0, 0.97, z); car.add(pole); }
    if (k === 0) { // Front: Scheinwerfer, Zielanzeige, Frontscheibe
      const front = ink(new THREE.BoxGeometry(Wd, 3.2, 0.12), yellow, 0.8); front.position.set(0, 0.85, L / 2 + 0.05); car.add(front);
      const ws = new THREE.Mesh(new THREE.PlaneGeometry(2.1, 0.9), new THREE.MeshBasicMaterial({ color: '#203040' })); ws.position.set(0, 1.35, L / 2 + 0.12); car.add(ws);
      const dest = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.26), new THREE.MeshBasicMaterial({ map: destTex })); dest.position.set(0, 2.05, L / 2 + 0.12); car.add(dest);
      const hl = new THREE.Group(); hl.rotation.y = -Math.PI / 2; hl.position.set(0, -0.3, 0); car.add(hl); headlights(hl, 16, L / 2 + 0.15);
      const spot = new THREE.SpotLight('#fff2cc', 40, 40, 0.45, 0.5, 1.2); spot.position.set(0, 0.3, L / 2 + 0.3); spot.target.position.set(0, -0.5, L / 2 + 12); car.add(spot); car.add(spot.target); carLights.push(spot);
    } else { for (const s of [-0.8, 0.8]) { const tl = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.14, 0.05), new THREE.MeshBasicMaterial({ color: '#ff2a1a' })); tl.position.set(s, -0.2, -L / 2 - 0.05); car.add(tl); } const back = ink(new THREE.BoxGeometry(Wd, 3.2, 0.12), yellow, 0.8); back.position.set(0, 0.85, -L / 2 - 0.02); car.add(back); }
    for (let j = -1; j <= 1; j += 2) for (const zz of [-5, 5]) { const bogie = ink(new THREE.BoxGeometry(2.2, 0.35, 2.2), dark, 0.5); bogie.position.set(0, -1.35, zz); car.add(bogie); }
  }
  train.position.set(TX, 0, -200);

  // ---------- Zeitpunkte ----------
  const ev = (k) => beats.filter((b) => b.effekt?.[k] !== undefined).map((b) => ({ b, v: b.effekt[k] }));
  const zug = ev('zug').map(({ b, v }) => ({ t0: b.t0 + (v.ab || 0), dur: v.dauer || 10, von: v.von ?? -150, nach: v.nach ?? -16 }))[0];
  const doorT = ev('zug_tueren').map(({ b, v }) => b.t0 + (v === true ? 0 : v))[0];
  const ratT = ev('ratten').map(({ b, v }) => b.t0 + (v === true ? 0 : v));
  const flick = ev('flackern').map(({ b, v }) => ({ t0: b.t0 + (b.effekt.flackern_ab || 0), t1: b.t0 + (b.effekt.flackern_ab || 0) + v }));
  const lukeT = ev('luke').map(({ b, v }) => b.t0 + (v === true ? 0 : v))[0];
  const RAT = Array.from({ length: NR }, (_, i) => ({ z: 14 - i * 6 + r() * 3, ph: r() * 20, per: 9 + r() * 7, sp: 2.2 + r() * 1.2, dir: r() < 0.5 ? 1 : -1 }));

  root.userData.update = ({ t = 0, eye, sky, px = 768 }) => {
    if (sky) { sky.sun.intensity = 0; sky.amb.intensity *= 0.42; const d = scene.getObjectByName('sky'); if (d) d.visible = false; }
    if (eye) dust.uniforms.uEye.value.copy(eye);
    dust.uniforms.uT.value = t; dust.uniforms.uPx.value = px;
    // Flackern (Beat) + Neonröhre, die von selbst immer wieder aufzuckt
    const fl = flick.some((f) => t >= f.t0 && t < f.t1);
    const nOn = fl ? Math.sin(t * 61) + Math.sin(t * 23) > 0.6 : (t % 6.3 < 0.12 || (t % 6.3 > 0.25 && t % 6.3 < 0.32) || (t % 11.7 > 4 && t % 11.7 < 4.08));
    neon.material.color.set(nOn ? '#e8fff4' : '#5a6460'); neonL.intensity = nOn ? 9 : 0; neonG.material.opacity = nOn ? 0.5 : 0;
    emerg.forEach((e) => { const on = fl ? Math.sin(t * 37 + e.ph * 3) > -0.2 : true; const k = on ? 0.85 + 0.15 * Math.sin(t * 2.1 + e.ph) : 0.05; e.l.intensity = 3.8 * k; e.g.material.opacity = 0.45 * k; e.box.material.color.setRGB(1 * k, 0.23 * k, 0.14 * k); });
    // Tropfen
    dropMeshes.forEach((d, i) => { const { x, z, per, ph } = d.userData; const k = ((t + ph) % per) / per, fallT = 0.55; const tf = k * per;
      d.visible = tf < fallT; d.position.set(x, CEIL - 0.1 - (tf / fallT) ** 2 * (CEIL - 0.1), z);
      const rk = (tf - fallT) / 0.6; rings[i].visible = rk > 0 && rk < 1; rings[i].scale.setScalar(0.03 + rk * 0.25); rings[i].material.opacity = 0.7 * (1 - rk); });
    // Ratten: huschen gelegentlich die Wand entlang; beim Effekt ein Rudel quer über den Bahnsteig
    for (let i = 0; i < NR; i++) {
      const R0 = RAT[i]; let x, z, a, vis = false;
      const burst = ratT.find((t0) => t >= t0 + i * 0.12 && t < t0 + i * 0.12 + 3.2);
      if (burst !== undefined) { const k = t - burst - i * 0.12; x = PX0 + 0.3 + k * 2.4; z = (eye ? eye.z : 0) - 1.8 + i * 0.35 + Math.sin(k * 9 + i) * 0.15; a = Math.PI / 2; vis = x < PX1 + 0.3; }
      else { const k = ((t + R0.ph) % R0.per); if (k < 3.5) { x = PX0 + 0.15; z = R0.z + R0.dir * k * R0.sp; a = R0.dir > 0 ? 0 : Math.PI; vis = true; } }
      const y = vis ? 0.05 + Math.abs(Math.sin(t * 30 + i)) * 0.015 : -50;
      E.set(0, a || 0, 0); Q.setFromEuler(E); P.set(x || 0, y, z || 0); S.set(1, 1, 1); M4.compose(P, Q, S);
      rats.setMatrixAt(i, M4); E.set(0, (a || 0) + Math.sin(t * 14 + i) * 0.4, 0); Q.setFromEuler(E); tails.setMatrixAt(i, M4.compose(P, Q, S));
      for (const s of [-1, 1]) { const ex = (x || 0) + Math.sin(a || 0) * 0.11 + Math.cos(a || 0) * s * 0.025, ez = (z || 0) + Math.cos(a || 0) * 0.11 - Math.sin(a || 0) * s * 0.025; ratEyes.setMatrixAt(i * 2 + (s > 0 ? 1 : 0), M4.compose(P.set(ex, y + 0.03, ez), Q.identity(), S.set(1, 1, 1))); }
    }
    rats.instanceMatrix.needsUpdate = true; tails.instanceMatrix.needsUpdate = true; ratEyes.instanceMatrix.needsUpdate = true;
    // Luke
    const lk = lukeT !== undefined ? ease((t - lukeT) / 0.5) : 0; hatchPiv.rotation.z = lk * 1.9; shaftLight.material.opacity = lk * 0.28;
    // Zug
    if (zug) {
      const k = (t - zug.t0) / zug.dur; train.visible = k > -0.01;
      train.position.z = zug.von + (zug.nach - zug.von) * ease(k);
      const moving = k > 0 && k < 1; train.position.y = moving ? Math.sin(t * 23) * 0.012 : 0; train.rotation.z = moving ? Math.sin(t * 3.1) * 0.004 : 0;
      const sig = k > -0.3; sigRed.visible = sigGlowR.visible = !sig; sigGreen.visible = sigGlowG.visible = sig;
      const lightsOn = !fl || Math.sin(t * 41) > 0; carLights.forEach((l) => (l.visible = true, l.intensity = lightsOn ? (l.isSpotLight ? 40 : 6) : 0.3));
      const dk = doorT !== undefined ? ease((t - doorT) / 1.2) : 0; doorLeaves.forEach((d) => (d.leaf.position.z = d.z0 + d.s * dk * 0.66));
    } else { sigGreen.visible = sigGlowG.visible = false; }
  };
  return root;
}
