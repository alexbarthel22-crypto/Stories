// Set "turnhalle": Schulturnhalle bei Nacht. Halle x -12 … 12, z -18 … 18, Höhe 8.
// Eingang hinten (z = +18), Tribüne links (x -12 … -8, oberste Stufe y = 2.4), Sprossenwand + Geräteraum (Rolltor z -6 … -2) rechts,
// vorne (z = -18) Anzeigetafel + Basketballkorb. Notausgang mit Kette rechts vorne.
//
// Beat-Effekte (Feld "effekt"):
//   strahler: {ab, tempo}        -> Hallenstrahler gehen Reihe für Reihe mit einem Klonk an
//   dunkel: s                    -> alle Strahler aus
//   anzeige: {ab, text, rot}     -> Text auf der Anzeigetafel (Laufschrift, wenn lang)
//   ball: s                      -> Basketball springt aus dem Dunkeln heran und rollt vor die Füße
//   rolltor: s                   -> Rolltor des Geräteraums fährt hoch
//   blitz: s                     -> kurzer Lichtblitz (Strahler flackern)
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, rng } from '../toon.js';

export const info = {
  start: [0, 16.5],
  spots: {
    halle: [0, -2], tribuene: [70, 14], anzeige: [0, 18], korb: [0, 12], geraeteraum: [-70, -2], eingang: [180, -4], decke: [0, 70], boden: [0, -60], seile: [-20, 20],
  },
};
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
const BOX = new THREE.BoxGeometry(1, 1, 1);
const X0 = -12, X1 = 12, Z0 = -18, Z1 = 18, H = 8;
function instanced(geo, mat, items, inkW = 0.5) {
  const m = inkW ? inkInstanced(geo, mat, items.length, inkW) : new THREE.InstancedMesh(geo, mat, items.length);
  items.forEach((it, i) => { E.set(it.rx || 0, it.ry || 0, it.rz || 0); Q.setFromEuler(E); m.setMatrixAt(i, M4.compose(P.set(...it.p), Q, S.set(...(it.s || [1, 1, 1])))); if (it.c) m.setColorAt(i, C.set(it.c)); });
  m.castShadow = true; m.receiveShadow = true; return m;
}

export function build(scene, seed = 71, ctx = {}) {
  const beats = ctx.beats || [];
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o) => (root.add(o), o);
  scene.fog = new THREE.Fog('#0a0c14', 18, 70);
  const glowTex = canvasTex(64, 64, (c, w) => { const g = c.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(0, 0, w, w); });
  const plane = (w, h, tex, x, y, z, ry, opts = {}) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), toon('#ffffff', { map: tex, ...opts }))); m.position.set(x, y, z); m.rotation.y = ry; return m; };

  // ---------- Parkett mit Spielfeldlinien ----------
  const floorTex = canvasTex(1024, 1536, (c, w, h) => {
    c.fillStyle = '#c89a62'; c.fillRect(0, 0, w, h);
    for (let x = 0; x < w; x += 16) for (let y = (x / 16 % 4) * 40; y < h; y += 160) { c.fillStyle = ['#c49660', '#cfa26a', '#bf9058', '#d2a870'][(r() * 4) | 0]; c.fillRect(x, y, 15, 158); }
    c.fillStyle = 'rgba(0,0,0,0.25)'; for (let x = 0; x < w; x += 16) c.fillRect(x, 0, 1, h);
    const sx = w / 24, sz = h / 36, X = (x) => (x + 12) * sx, Z = (z) => (z + 18) * sz;
    c.lineWidth = 6; c.strokeStyle = '#f0f0f0'; c.strokeRect(X(-10), Z(-16), 20 * sx, 32 * sz); c.beginPath(); c.moveTo(X(-10), Z(0)); c.lineTo(X(10), Z(0)); c.stroke(); c.beginPath(); c.arc(X(0), Z(0), 2 * sx, 0, 7); c.stroke();
    c.strokeStyle = '#2a6ad0'; c.lineWidth = 6; for (const zz of [-16, 16]) { c.beginPath(); c.arc(X(0), Z(zz), 6.5 * sx, zz < 0 ? 0 : Math.PI, zz < 0 ? Math.PI : 2 * Math.PI); c.stroke(); c.strokeRect(X(-2.4), zz < 0 ? Z(-16) : Z(10.2), 4.8 * sx, 5.8 * sz); }
    c.strokeStyle = '#e0302a'; c.lineWidth = 5; c.strokeRect(X(-4.5), Z(-9), 9 * sx, 18 * sz); c.strokeStyle = '#2aa04a'; c.strokeRect(X(-11.2), Z(-17.2), 22.4 * sx, 34.4 * sz);
    c.fillStyle = 'rgba(255,255,255,0.08)'; c.fillRect(X(-3), 0, 6 * sx, h); stains(c, w, h, r, 14, '60,40,20', 0.18);
  });
  const fl = add(new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), toon('#ffffff', { map: floorTex }))); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true;
  // Wände (unten Prallschutz, oben Ziegel/Beton), Decke mit Fachwerkträgern
  const wallTex = canvasTex(512, 512, (c, w, h) => { c.fillStyle = '#d8d4cc'; c.fillRect(0, 0, w, h); c.strokeStyle = 'rgba(80,70,60,0.25)'; c.lineWidth = 2; for (let y = 0; y < h; y += 24) { c.beginPath(); c.moveTo(0, y); c.lineTo(w, y); c.stroke(); for (let x = (y / 24 % 2) * 32; x < w; x += 64) { c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 24); c.stroke(); } } c.fillStyle = '#3a6aa0'; c.fillRect(0, h * 0.75, w, h * 0.25); c.fillStyle = 'rgba(0,0,0,0.25)'; for (let x = 0; x < w; x += 64) c.fillRect(x, h * 0.75, 3, h * 0.25); stains(c, w, h, r, 10, '70,60,50', 0.2); }, { repeat: [6, 1] });
  const wallM = toon('#ffffff', { map: wallTex });
  const wall = (w, x, z, ry) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, H), wallM)); m.position.set(x, H / 2, z); m.rotation.y = ry; m.receiveShadow = true; };
  wall(Z1 - Z0, X0, 0, Math.PI / 2); wall(Z1 - Z0, X1, 0, -Math.PI / 2); wall(X1 - X0, 0, Z0, 0); wall(X1 - X0, 0, Z1, Math.PI);
  const ceil = add(new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), toon('#8a8a86'))); ceil.rotation.x = Math.PI / 2; ceil.position.y = H;
  const truss = []; for (let z = -15; z <= 15; z += 5) { truss.push({ p: [0, H - 0.4, z], s: [24, 0.3, 0.25], c: '#5a6068' }); for (let x = -11; x <= 11; x += 2) truss.push({ p: [x, H - 0.8, z], s: [0.08, 0.8, 0.08], rz: (x % 4 ? 0.5 : -0.5), c: '#5a6068' }); truss.push({ p: [0, H - 1.2, z], s: [24, 0.15, 0.15], c: '#5a6068' }); }
  add(instanced(BOX, toon('#ffffff'), truss, 0.3));
  // hohe Fenster (Mondlicht)
  for (const [x, ry] of [[X0 + 0.02, Math.PI / 2], [X1 - 0.02, -Math.PI / 2]]) for (let z = -14; z <= 14; z += 4) { const w = add(new THREE.Mesh(new THREE.PlaneGeometry(3, 1.6), new THREE.MeshBasicMaterial({ color: '#2a3a66' }))); w.position.set(x, 6.3, z); w.rotation.y = ry; const f = add(new THREE.Mesh(new THREE.PlaneGeometry(0.08, 1.6), new THREE.MeshBasicMaterial({ color: '#1a1a1a' }))); f.position.set(x + Math.sign(-x) * 0.01, 6.3, z); f.rotation.y = ry; }
  const moonM = new THREE.MeshBasicMaterial({ color: '#7a9ad8', map: glowTex, transparent: true, opacity: 0.16, blending: THREE.AdditiveBlending, depthWrite: false });
  for (let z = -14; z <= 14; z += 4) { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(2.6, 3.4), moonM)); m.rotation.x = -Math.PI / 2; m.position.set(4 + (z % 8 ? 0.5 : -0.3), 0.01, z + 1); }

  // ---------- Tribüne links ----------
  const tiers = [], seats = []; const PAL = ['#c83a2a', '#2a6ab0', '#e8c020'];
  for (let k = 0; k < 4; k++) { const y = 0.6 * (k + 1), x = -8.45 - k * 0.9; tiers.push({ p: [x - (3 - k) * 0, y / 2, -2], s: [0.9, y, 22], c: '#8a8e94' }); for (let z = -12.5; z <= 8.5; z += 0.55) seats.push({ p: [x + 0.15, y + 0.12, z], s: [0.42, 0.24, 0.42], c: PAL[(k + Math.floor(z * 2)) % 3] }); }
  add(instanced(BOX, toon('#ffffff'), tiers, 0.5)); add(instanced(BOX, toon('#ffffff'), seats, 0.3));
  for (let z = -13; z <= 9; z += 1.5) { const p = add(new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.0, 6), toon('#c8c8c8'))); p.position.set(-7.95, 0.5, z); } const rail = add(new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 22, 6), toon('#c8c8c8'))); rail.rotation.x = Math.PI / 2; rail.position.set(-7.95, 1.0, -2);
  // Banner + Wimpel
  const banner = (txt, bg, fg) => canvasTex(512, 96, (c, w, h) => { c.fillStyle = bg; c.fillRect(0, 0, w, h); c.fillStyle = fg; c.font = '900 52px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(txt, w / 2, h / 2 + 2); });
  plane(5, 0.9, banner('TSV NORD', '#c83a2a', '#fff'), X0 + 0.03, 4.4, -2, Math.PI / 2); plane(5, 0.9, banner('SPORTFEST 2026', '#2a6ab0', '#ffd84a'), X1 - 0.03, 4.6, 8, -Math.PI / 2);
  for (let i = 0; i < 12; i++) { const m = add(new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.5, 3), toon(PAL[i % 3]))); m.rotation.x = Math.PI; m.position.set(-11 + i * 2, H - 1.6, Z1 - 0.5); }

  // ---------- Anzeigetafel + Korb vorne ----------
  const scC = document.createElement('canvas'); scC.width = 1024; scC.height = 320; const scT = new THREE.CanvasTexture(scC); scT.colorSpace = THREE.SRGBColorSpace;
  add(edges(ink(new THREE.BoxGeometry(5.4, 1.9, 0.3), toon('#1a1a1c'), 0.6))).position.set(0, 5.6, Z0 + 0.15);
  const sc = add(new THREE.Mesh(new THREE.PlaneGeometry(5.0, 1.56), new THREE.MeshBasicMaterial({ map: scT, toneMapped: false }))); sc.position.set(0, 5.6, Z0 + 0.31);
  const scGlow = add(new THREE.PointLight('#ff4a2a', 0, 0, 1.6)); scGlow.position.set(0, 5.4, Z0 + 2);
  const hoop = (z, s) => { const g = new THREE.Group(); add(g); g.position.set(0, 0, z);
    const board = ink(new THREE.BoxGeometry(1.8, 1.05, 0.05), new THREE.MeshBasicMaterial({ color: '#e8f0f8', transparent: true, opacity: 0.7 }), 0.6); board.position.set(0, 3.55, 0); g.add(board);
    const sq = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.45), new THREE.MeshBasicMaterial({ color: '#d0302a', wireframe: true })); sq.position.set(0, 3.3, s * 0.03); g.add(sq);
    const ring = ink(new THREE.TorusGeometry(0.23, 0.02, 6, 18), toon('#e8501a'), 0.4); ring.rotation.x = Math.PI / 2; ring.position.set(0, 3.05, s * 0.28); g.add(ring);
    const net = new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.15, 0.4, 12, 2, true), new THREE.MeshBasicMaterial({ color: '#f0f0f0', wireframe: true })); net.position.set(0, 2.85, s * 0.28); g.add(net);
    const arm = ink(new THREE.BoxGeometry(0.1, 0.1, 1.2), toon('#3a3a3a'), 0.4); arm.position.set(0, 4.2, -s * 0.6); g.add(arm); return g; };
  hoop(Z0 + 1.3, 1); hoop(Z1 - 1.3, -1);
  // Hallenuhr
  const clk = add(new THREE.Mesh(new THREE.CircleGeometry(0.4, 24), new THREE.MeshBasicMaterial({ map: canvasTex(128, 128, (c) => { c.fillStyle = '#f0ece0'; c.beginPath(); c.arc(64, 64, 60, 0, 7); c.fill(); c.lineWidth = 6; c.strokeStyle = '#222'; c.stroke(); c.lineWidth = 6; c.beginPath(); c.moveTo(64, 64); c.lineTo(64, 24); c.stroke(); c.lineWidth = 4; c.beginPath(); c.moveTo(64, 64); c.lineTo(76, 22); c.stroke(); }) }))); clk.position.set(6, 5.6, Z0 + 0.04);

  // ---------- Rechte Seite: Sprossenwand, Seile, Geräteraum mit Rolltor, Notausgang mit Kette ----------
  const bars = []; for (let z = 4; z <= 14; z += 1.0) { bars.push({ p: [X1 - 0.2, 1.4, z], s: [0.1, 2.8, 0.1], c: '#c8a060' }); } for (let y = 0.25; y < 2.8; y += 0.2) for (let z = 4.5; z <= 13.5; z += 1.0) bars.push({ p: [X1 - 0.22, y, z], s: [0.05, 0.05, 0.98], c: '#d8b070' });
  add(instanced(BOX, toon('#ffffff'), bars, 0.3));
  const ropes = []; for (const x of [3, 4, 5]) { const piv = add(new THREE.Group()); piv.position.set(x, H - 1.2, -2); const rope = ink(new THREE.CylinderGeometry(0.03, 0.03, 6.2, 6), toon('#c8a878'), 0.3); rope.position.y = -3.1; piv.add(rope); const knot = ink(new THREE.SphereGeometry(0.06, 8, 6), toon('#b89868'), 0.3); knot.position.y = -6.1; piv.add(knot); ropes.push({ piv, ph: r() * 6 }); }
  const gr = add(new THREE.Mesh(new THREE.BoxGeometry(4, 3.2, 5), toon('#3a3a36', { side: THREE.BackSide }))); gr.position.set(X1 + 2.5, 1.6, -4);
  const grStuff = [{ p: [X1 + 3.5, 0.3, -5.5], s: [1.4, 0.6, 2], c: '#2a5aa0' }, { p: [X1 + 3.5, 0.75, -5.5], s: [1.4, 0.3, 2], c: '#2a5aa0' }, { p: [X1 + 1.5, 0.5, -2.8], s: [0.9, 1.0, 1.2], c: '#a8784a' }];
  add(instanced(BOX, toon('#ffffff'), grStuff, 0.4));
  const roll = add(new THREE.Mesh(new THREE.PlaneGeometry(4, 3.0), toon('#ffffff', { map: canvasTex(128, 128, (c, w, h) => { c.fillStyle = '#8a9098'; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(0,0,0,0.3)'; for (let y = 0; y < h; y += 8) c.fillRect(0, y, w, 2); c.fillStyle = '#e8c020'; c.font = '900 16px Inter, sans-serif'; c.fillText('GERÄTERAUM', 12, 64); }) })));
  roll.rotation.y = -Math.PI / 2; roll.position.set(X1 - 0.03, 1.5, -4);
  const grLight = add(new THREE.PointLight('#ff9a50', 0, 0, 1.5)); grLight.position.set(X1 + 2, 2.5, -4);
  const exitDoor = add(ink(new THREE.BoxGeometry(0.08, 2.3, 1.6), toon('#5a7a9a'), 0.5)); exitDoor.position.set(X1 - 0.05, 1.15, -14);
  const chain = []; for (let k = 0; k < 14; k++) chain.push({ p: [X1 - 0.14, 1.1 + Math.sin(k / 13 * Math.PI) * -0.15, -14.6 + k * 0.09], s: [1, 1, 1], ry: (k % 2) * Math.PI / 2, c: '#9a9a9a' });
  add(instanced(new THREE.TorusGeometry(0.035, 0.01, 4, 8), toon('#ffffff'), chain, 0));
  const padlock = add(ink(new THREE.BoxGeometry(0.06, 0.1, 0.08), toon('#c8a020'), 0.3)); padlock.position.set(X1 - 0.16, 0.92, -14);
  const exitS = add(new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.3, 0.8), new THREE.MeshBasicMaterial({ map: canvasTex(256, 96, (c, w, h) => { c.fillStyle = '#1a9a4a'; c.fillRect(0, 0, w, h); c.fillStyle = '#fff'; c.font = '900 34px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('NOTAUSGANG', w / 2 + 18, h / 2); c.fillRect(20, 30, 20, 40); }) }))); exitS.position.set(X1 - 0.05, 2.6, -14);
  // Eingangstür hinten
  for (const x of [-0.6, 0.6]) { const d = add(ink(new THREE.BoxGeometry(1.15, 2.3, 0.08), toon('#5a7a9a'), 0.5)); d.position.set(x, 1.15, Z1 - 0.05); }
  // Matten, Kasten, Bänke, Ballwagen, Hütchen, Flasche, Jacke
  const props = [{ p: [8, 0.25, 12], s: [2, 0.5, 3], c: '#2a5aa0' }, { p: [8, 0.65, 12], s: [2, 0.3, 3], c: '#2a5aa0' }, { p: [8, 0.95, 12.2], s: [2, 0.3, 2.6], c: '#3a6ab0' },
    { p: [6, 0.3, -10], s: [1.2, 0.6, 0.5], c: '#b8865a' }, { p: [6, 0.75, -10], s: [1.1, 0.3, 0.48], c: '#b8865a' }, { p: [6, 1.0, -10], s: [1.0, 0.2, 0.46], c: '#e8e0d0' },
    { p: [X1 - 0.8, 0.3, 0], s: [0.25, 0.04, 4], c: '#c8a060' }, { p: [X0 + 4.5, 0.3, 12], s: [0.25, 0.04, 4], c: '#c8a060' }];
  add(instanced(BOX, toon('#ffffff'), props, 0.5));
  const cart = add(edges(ink(new THREE.BoxGeometry(1.0, 0.8, 0.7), toon('#4a4a4a', { wireframe: false }), 0.4))); cart.position.set(9, 0.5, 2);
  const balls = []; for (let k = 0; k < 9; k++) balls.push({ p: [8.7 + (k % 3) * 0.3, 1.0 + Math.floor(k / 3) * 0.05, 1.8 + Math.floor(k / 3) * 0.2], s: [1, 1, 1], c: ['#e8701a', '#f0f0f0', '#e8c020'][k % 3] });
  add(instanced(new THREE.SphereGeometry(0.12, 10, 8), toon('#ffffff'), balls, 0.3));
  const cones = []; for (let k = 0; k < 6; k++) cones.push({ p: [-4 + k * 1.6, 0.15, 6], s: [1, 1, 1], c: '#f07a1a' }); add(instanced(new THREE.ConeGeometry(0.12, 0.3, 10), toon('#ffffff'), cones, 0.3));
  const bottle = add(ink(new THREE.CylinderGeometry(0.04, 0.04, 0.22, 10), toon('#2a8ad0'), 0.3)); bottle.position.set(-6.5, 0.11, 8.6);
  const jacket = add(ink(new THREE.BoxGeometry(0.6, 0.06, 0.45), toon('#2a6a4a'), 0.3)); jacket.position.set(-8.4, 0.63, 6.0); jacket.rotation.y = 0.3;

  // ---------- Strahler ----------
  const spots = []; for (const z of [12, 4, -4, -12]) for (const x of [-6, 0, 6]) { const m = add(new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.1, 0.7), new THREE.MeshBasicMaterial({ color: '#2a2a2a' }))); m.position.set(x, H - 1.35, z); const g = add(new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: '#fff8e0', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }))); g.scale.set(1.8, 1.8, 1); g.position.set(x, H - 1.45, z); spots.push({ m, g, z }); }
  const rowL = [12, 4, -4, -12].map((z) => { const l = add(new THREE.PointLight('#fff4e0', 0, 0, 1.2)); l.position.set(0, H - 2, z); return { l, z }; });
  // Basketball (animiert)
  const ballTex = canvasTex(128, 64, (c, w, h) => { c.fillStyle = '#d8651a'; c.fillRect(0, 0, w, h); c.strokeStyle = '#2a1a10'; c.lineWidth = 3; for (const x of [32, 64, 96]) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, h); c.stroke(); } c.beginPath(); c.moveTo(0, h / 2); c.lineTo(w, h / 2); c.stroke(); });
  const ball = add(ink(new THREE.SphereGeometry(0.12, 16, 12), toon('#ffffff', { map: ballTex }), 0.4)); ball.position.set(0, 0.12, -30); ball.visible = false;

  // ---------- Ereignisse ----------
  const ev = (k) => beats.flatMap((b) => (b.effekt?.[k] === undefined ? [] : [].concat(b.effekt[k]).map((v) => ({ t0: b.t0, v }))));
  const lightEv = ev('strahler').map(({ t0, v }) => ({ t: t0 + (v.ab || 0), tempo: v.tempo || 1.5 }));
  const darkT = ev('dunkel').map(({ t0, v }) => t0 + (v === true ? 0 : v));
  const anz = ev('anzeige').map(({ t0, v }) => ({ t: t0 + (v.ab || 0), text: v.text, rot: v.rot !== false }));
  const ballT = ev('ball').map(({ t0, v }) => t0 + (v === true ? 0 : v))[0], rollT = ev('rolltor').map(({ t0, v }) => t0 + (v === true ? 0 : v))[0], flashT = ev('blitz').map(({ t0, v }) => t0 + (v === true ? 0 : v));
  let scKey = '';
  const drawBoard = (t) => {
    const a = anz.filter((x) => t >= x.t).pop(); const on = !!a; const txt = a ? a.text : 'HEIM 0 : 0 GAST';
    const long = txt.length > 18, off = long ? Math.floor((t - (a ? a.t : 0)) * 9) % (txt.length + 20) : 0;
    const key = `${txt}|${off}|${on}|${Math.floor(t * 3) % 2}`; if (key === scKey) return; scKey = key;
    const g = scC.getContext('2d'); g.fillStyle = '#0a0a0c'; g.fillRect(0, 0, 1024, 320);
    const tc = document.createElement('canvas'); tc.width = 256; tc.height = 32; const tg = tc.getContext('2d'); tg.fillStyle = '#000'; tg.fillRect(0, 0, 256, 32); tg.fillStyle = '#fff'; tg.font = '900 22px "Courier New", monospace'; tg.textBaseline = 'middle';
    if (long) tg.fillText(txt, 256 - off * 13, 16); else { tg.textAlign = 'center'; tg.fillText(txt, 128, 16); }
    const px = tg.getImageData(0, 0, 256, 32).data; const col = on ? (a.rot ? '#ff3a2a' : '#ffb020') : '#3a1a10';
    for (let y = 0; y < 32; y++) for (let x = 0; x < 256; x++) { const v = px[(y * 256 + x) * 4]; g.fillStyle = v > 100 ? col : '#1a0e0a'; g.fillRect(x * 4, y * 10 + 2, 3, 7); }
    scT.needsUpdate = true; scGlow.intensity = on ? 3 : 0;
  };

  root.userData.update = ({ t = 0, sky }) => {
    if (sky) { sky.amb.intensity *= 0.3; sky.sun.intensity *= 0.4; }
    // Strahler
    const ld = darkT.filter((d) => t >= d).pop(), le = lightEv.filter((e) => t >= e.t && (ld === undefined || e.t > ld)).pop();
    const fl = flashT.some((f) => t >= f && t < f + 0.35);
    spots.forEach((s, i) => { const row = Math.floor(i / 3); let on = le ? (t - le.t) * le.tempo >= row + 0.2 * (i % 3) : false; if (fl) on = Math.sin(t * 70 + i) > 0; s.on = on; s.m.material.color.set(on ? '#fffaf0' : '#2a2a2a'); s.g.material.opacity = on ? 0.6 : 0; });
    rowL.forEach((R2, k) => { const n = spots.slice(k * 3, k * 3 + 3).filter((s) => s.on).length; R2.l.intensity = 9 * n / 3; });
    drawBoard(t);
    ropes.forEach((R2) => (R2.piv.rotation.x = Math.sin(t * 0.6 + R2.ph) * 0.04, R2.piv.rotation.z = Math.sin(t * 0.43 + R2.ph) * 0.03));
    // Ball: springt von vorne aus dem Dunkeln heran und rollt aus
    if (ballT !== undefined && t >= ballT) { const k = t - ballT; const z = -16 + Math.min(1, k / 3.2) * 18.5 - (k > 3.2 ? 0 : 0); const bounce = Math.abs(Math.sin(k * 3.4)) * 1.6 * Math.exp(-k * 0.9); ball.visible = true; ball.position.set(Math.sin(k * 0.6) * 0.4, 0.12 + bounce, Math.min(2.5, z)); ball.rotation.x = -k * 6 * Math.exp(-k * 0.3); }
    // Rolltor
    const rk = rollT !== undefined ? ease((t - rollT) / 2.5) : 0; roll.position.y = 1.5 + rk * 2.6; roll.scale.y = 1 - rk * 0.8; grLight.intensity = rk * 2.5;
  };
  return root;
}
