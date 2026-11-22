// Set "leitwarte": Leitwarte des Umspannwerks (Finale). Raum x -8 … 8, z -6 … 6, Höhe 3.8.
// Vorne (-Z) großes Fenster zum Hof, links (-X) die Netz-Schalttafel, rechts (+X) Eingangstür (z = 3.5) und Serverschränke,
// hinten (+Z) der NOT-AUS (x = -4). Hauptpult in der Mitte (z = -3.5), Blick zum Fenster.
//
// Beat-Effekte (Feld "effekt"):
//   uebernahme: {ab, von, bis, dauer}   -> Fortschritt der Netzübernahme (Prozent) auf Pult und Schalttafel
//   klopfen_fenster: s                  -> (nur Ton) – dafür: sfx
//   notaus: s                           -> Glas splittert, alles aus, rotes Notlicht
//   polizei: s                          -> Blaulicht draußen, Streifenwagen im Hof
//   morgen: {ab, dauer}                 -> Sonnenaufgang: Himmel wird hell, warmes Licht im Raum
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, rng } from '../toon.js';
import { car } from './aussicht.js';

export const info = {
  start: [7.0, 3.5],
  spots: {
    fenster: [0, 0], pult: [10, -12], tafel: [90, 6], tuer: [-90, -4], notaus: [130, -2], server: [-60, -4], decke: [0, 70], boden: [0, -60], stadt: [20, 2],
  },
};
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
const BOX = new THREE.BoxGeometry(1, 1, 1);
const X0 = -8, X1 = 8, Z0 = -6, Z1 = 6, H = 3.8;
function instanced(geo, mat, items, inkW = 0.5) {
  const m = inkW ? inkInstanced(geo, mat, items.length, inkW) : new THREE.InstancedMesh(geo, mat, items.length);
  items.forEach((it, i) => { E.set(it.rx || 0, it.ry || 0, it.rz || 0); Q.setFromEuler(E); m.setMatrixAt(i, M4.compose(P.set(...it.p), Q, S.set(...(it.s || [1, 1, 1])))); if (it.c) m.setColorAt(i, C.set(it.c)); });
  m.castShadow = true; m.receiveShadow = true; return m;
}
const canvasScreen = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return { c, t, g: c.getContext('2d') }; };

export function build(scene, seed = 51, ctx = {}) {
  const beats = ctx.beats || [];
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o) => (root.add(o), o);
  scene.fog = new THREE.Fog('#1a1e2c', 40, 400);
  const glowTex = canvasTex(64, 64, (c, w) => { const g = c.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(0, 0, w, w); });

  // ---------- Raum ----------
  const floorTex = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#5a5e62'; c.fillRect(0, 0, w, h); c.strokeStyle = 'rgba(30,32,36,0.6)'; c.lineWidth = 2; for (let i = 0; i <= 4; i++) { c.beginPath(); c.moveTo(0, i * 64); c.lineTo(w, i * 64); c.stroke(); c.beginPath(); c.moveTo(i * 64, 0); c.lineTo(i * 64, h); c.stroke(); } stains(c, w, h, r, 12, '20,20,24', 0.35); }, { repeat: [8, 6] });
  const fl = add(new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), toon('#ffffff', { map: floorTex }))); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true;
  const ceil = add(new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), toon('#c8c8c0'))); ceil.rotation.x = Math.PI / 2; ceil.position.y = H;
  const wallTex = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#d8d4c4'; c.fillRect(0, 0, w, h); c.fillStyle = '#7a8a9a'; c.fillRect(0, h * 0.72, w, h * 0.28); stains(c, w, h, r, 10, '80,70,50', 0.2); }, { repeat: [4, 1] });
  const wallM = toon('#ffffff', { map: wallTex });
  const wall = (w, h, x, y, z, ry) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallM)); m.position.set(x, y, z); m.rotation.y = ry; m.receiveShadow = true; return m; };
  wall(Z1 - Z0, H, X0, H / 2, 0, Math.PI / 2); wall(Z1 - Z0, H, X1, H / 2, 0, -Math.PI / 2); wall(X1 - X0, H, 0, H / 2, Z1, Math.PI);
  // Fensterwand vorne: Brüstung, Sturz, Pfosten, Glas
  add(edges(ink(new THREE.BoxGeometry(X1 - X0, 1.0, 0.25), toon('#9aa2a8'), 0.6))).position.set(0, 0.5, Z0);
  add(edges(ink(new THREE.BoxGeometry(X1 - X0, H - 3.2, 0.25), toon('#9aa2a8'), 0.6))).position.set(0, 3.2 + (H - 3.2) / 2, Z0);
  for (let x = X0; x <= X1; x += 2.67) add(ink(new THREE.BoxGeometry(0.12, 2.2, 0.2), toon('#3a3e44'), 0.4)).position.set(x, 2.1, Z0);
  const glass = add(new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, 2.2), new THREE.MeshBasicMaterial({ color: '#a8c0d8', transparent: true, opacity: 0.08, depthWrite: false, side: THREE.DoubleSide }))); glass.position.set(0, 2.1, Z0);
  // Deckenleuchten
  const panels = []; for (const x of [-5, 0, 5]) for (const z of [-3, 2]) { const m = add(new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.05, 0.6), new THREE.MeshBasicMaterial({ color: '#f0f4f0' }))); m.position.set(x, H - 0.03, z); panels.push(m); }
  const roomL = [[-4, 0], [4, 0]].map(([x, z]) => { const l = add(new THREE.PointLight('#e8f0ff', 3, 0, 1.3)); l.position.set(x, H - 0.4, z); return l; });

  // ---------- Netz-Schalttafel (links) ----------
  const mimic = canvasScreen(1024, 480);
  const mimicM = add(new THREE.Mesh(new THREE.PlaneGeometry(10, 2.6), new THREE.MeshBasicMaterial({ map: mimic.t, toneMapped: false }))); mimicM.position.set(X0 + 0.09, 2.1, -0.5); mimicM.rotation.y = Math.PI / 2;
  add(ink(new THREE.BoxGeometry(0.1, 2.8, 10.2), toon('#2a2e34'), 0.5)).position.set(X0 + 0.02, 2.1, -0.5);
  const mimicL = add(new THREE.PointLight('#6ab0ff', 2.5, 0, 1.5)); mimicL.position.set(X0 + 1.5, 2.1, -0.5);
  const nodes = []; for (let i = 0; i < 28; i++) nodes.push([80 + r() * 860, 70 + r() * 330]);
  const links = []; nodes.forEach((n, i) => { const d = nodes.map((m, j) => [Math.hypot(m[0] - n[0], m[1] - n[1]), j]).sort((a, b) => a[0] - b[0]); links.push([i, d[1][1]], [i, d[2][1]]); });
  // ---------- Hauptpult mit Monitoren ----------
  const desk = (x, z, w, ry = 0) => { const g = new THREE.Group(); add(g); g.position.set(x, 0, z); g.rotation.y = ry;
    const top = ink(new THREE.BoxGeometry(w, 0.06, 0.9), toon('#5a6068'), 0.5); top.position.y = 0.78; g.add(edges(top));
    const body = ink(new THREE.BoxGeometry(w, 0.75, 0.7), toon('#8a9098'), 0.5); body.position.set(0, 0.38, 0.05); g.add(body);
    const kb = ink(new THREE.BoxGeometry(0.5, 0.03, 0.18), toon('#2a2a2c'), 0.3); kb.position.set(0, 0.825, 0.2); g.add(kb);
    return g; };
  const console = desk(0, -3.5, 3.4);
  const mainScr = canvasScreen(768, 256);
  const mon = (g, x, w, h, tex, tilt = 0) => { const f = ink(new THREE.BoxGeometry(w + 0.08, h + 0.08, 0.1), toon('#1a1a1c'), 0.4); f.position.set(x, 0.8 + h / 2 + 0.12, -0.2); f.rotation.y = -tilt; g.add(f); const s = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false })); s.position.z = 0.051; f.add(s); return s; };
  const mainMon = mon(console, 0, 1.5, 0.5, mainScr.t);
  const sideScr = canvasScreen(256, 192);
  const sideMons = [mon(console, -1.2, 0.6, 0.45, sideScr.t, -0.3), mon(console, 1.2, 0.6, 0.45, sideScr.t, 0.3)];
  const consoleL = add(new THREE.PointLight('#7ab8ff', 2.2, 0, 1.6)); consoleL.position.set(0, 1.6, -2.4);
  // weitere Arbeitsplätze mit alten Röhrenmonitoren, Stühlen, Tassen, Telefon
  const crtScr = canvasTex(128, 96, (c, w, h) => { c.fillStyle = '#062010'; c.fillRect(0, 0, w, h); c.fillStyle = '#3aff7a'; c.font = '10px monospace'; for (let i = 0; i < 8; i++) c.fillText(['SAMMELSCHIENE 1', 'T1 110/20kV OK', 'T2 110/20kV OK', 'LS 14  AUS', 'FELD 7  EIN', 'NOTSTROM: AKKU', 'FREQ 50.01 Hz', '> _'][i], 6, 14 + i * 11); });
  const crts = []; const deskPos = [[-4.5, -3.2, 0], [4.2, -3.2, 0], [-4.5, 1.5, Math.PI / 2]];
  for (const [x, z, ry] of deskPos) { const d = desk(x, z, 2.2, ry); for (const dx of [-0.5, 0.5]) { const crt = ink(new THREE.BoxGeometry(0.5, 0.42, 0.45), toon('#c8c4b4'), 0.5); crt.position.set(dx, 1.03, -0.1); d.add(crt); const s = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.3), new THREE.MeshBasicMaterial({ map: crtScr })); s.position.set(dx, 1.05, 0.13); d.add(s); crts.push(s); } const mug = ink(new THREE.CylinderGeometry(0.045, 0.04, 0.1, 10), toon(['#c83a2a', '#e8e4d8', '#2a5a9a'][(r() * 3) | 0]), 0.3); mug.position.set(0.85, 0.86, 0.15); d.add(mug); for (let k = 0; k < 3; k++) { const p = new THREE.Mesh(new THREE.BoxGeometry(0.21, 0.004, 0.29), toon('#ece6d4')); p.position.set(-0.8 + k * 0.08, 0.815 + k * 0.004, -0.15); p.rotation.y = r(); d.add(p); } }
  const chair = (x, z, ry) => { const g = new THREE.Group(); add(g); g.position.set(x, 0, z); g.rotation.y = ry; const s = ink(new THREE.BoxGeometry(0.5, 0.08, 0.5), toon('#2a2a2e'), 0.4); s.position.y = 0.48; g.add(s); const b = ink(new THREE.BoxGeometry(0.48, 0.55, 0.07), toon('#2a2a2e'), 0.4); b.position.set(0, 0.8, 0.24); g.add(b); const post = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.44, 6), toon('#555')); post.position.y = 0.24; g.add(post); for (let k = 0; k < 5; k++) { const leg = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.03, 0.04), toon('#444')); leg.position.set(Math.cos(k * 1.256) * 0.15, 0.03, Math.sin(k * 1.256) * 0.15); leg.rotation.y = -k * 1.256; g.add(leg); } };
  chair(-4.5, -2.2, 0.3); chair(4.2, -2.3, -0.4); chair(-3.6, 1.6, 1.2); chair(1.6, -1.8, 2.2);
  const phone = add(ink(new THREE.BoxGeometry(0.22, 0.08, 0.18), toon('#b81a14'), 0.4)); phone.position.set(-1.3, 0.85, -3.4);
  const ext = add(ink(new THREE.CylinderGeometry(0.09, 0.09, 0.55, 12), toon('#d0201a'), 0.5)); ext.position.set(X1 - 0.2, 0.6, 0.8);
  const clockC = canvasScreen(128, 128); const clk = add(new THREE.Mesh(new THREE.CircleGeometry(0.3, 24), new THREE.MeshBasicMaterial({ map: clockC.t }))); clk.position.set(0, 3.45, Z1 - 0.03); clk.rotation.y = Math.PI;
  // ---------- Serverschränke (rechts) ----------
  const racks = [], leds = [];
  for (let i = 0; i < 5; i++) { const z = -3.6 + i * 0.75; const rk = add(edges(ink(new THREE.BoxGeometry(0.9, 2.1, 0.7), toon('#2a2e34'), 0.6))); rk.position.set(5.6, 1.05, z); racks.push(rk); for (let k = 0; k < 14; k++) leds.push({ p: [5.13, 0.4 + k * 0.12, z - 0.25 + (k % 3) * 0.2], s: [0.01, 0.03, 0.03], ph: r() * 10, k: leds.length }); }
  const ledMesh = add(new THREE.InstancedMesh(BOX, new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false }), leds.length)); ledMesh.frustumCulled = false;
  leds.forEach((l, i) => { ledMesh.setMatrixAt(i, M4.compose(P.set(...l.p), Q.identity(), S.set(...l.s))); ledMesh.setColorAt(i, C.set('#3aff6a')); });
  const cableTray = add(ink(new THREE.BoxGeometry(0.5, 0.08, 4.2), toon('#6a6a62'), 0.4)); cableTray.position.set(5.6, 3.3, -2.1);
  // ---------- Eingangstür + NOT-AUS ----------
  const door = add(ink(new THREE.BoxGeometry(0.08, 2.2, 1.2), toon('#3a5a7a'), 0.6)); door.position.set(X1 - 0.04, 1.1, 3.5);
  const exitTex = canvasTex(256, 96, (c, w, h) => { c.fillStyle = '#1a9a4a'; c.fillRect(0, 0, w, h); c.fillStyle = '#fff'; c.font = '900 34px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('NOTAUSGANG', w / 2 + 18, h / 2); c.fillRect(20, 30, 20, 40); });
  const exitS = add(new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.3, 0.8), new THREE.MeshBasicMaterial({ map: exitTex }))); exitS.position.set(X1 - 0.05, 2.5, 3.5);
  const naBox = add(new THREE.Group()); naBox.position.set(-4, 1.45, Z1 - 0.06);
  naBox.add(ink(new THREE.BoxGeometry(0.6, 0.6, 0.1), toon('#e8c020'), 0.5));
  const naBtn = ink(new THREE.CylinderGeometry(0.13, 0.13, 0.1, 18), toon('#d0201a'), 0.5); naBtn.rotation.x = Math.PI / 2; naBtn.position.z = -0.08; naBox.add(naBtn);
  const naGlass = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.5, 0.02), new THREE.MeshBasicMaterial({ color: '#c8e0f0', transparent: true, opacity: 0.3, depthWrite: false })); naGlass.position.z = -0.16; naBox.add(naGlass);
  const naSign = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.3), toon('#ffffff', { map: canvasTex(256, 72, (c, w, h) => { c.fillStyle = '#d0201a'; c.fillRect(0, 0, w, h); c.fillStyle = '#fff'; c.font = '900 44px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('NOT-AUS', w / 2, h / 2 + 2); }) })); naSign.position.set(0, 0.5, -0.06); naSign.rotation.y = Math.PI; naBox.add(naSign);
  const shards = []; for (let i = 0; i < 14; i++) { const s = new THREE.Mesh(new THREE.BoxGeometry(0.04 + r() * 0.06, 0.04 + r() * 0.06, 0.005), new THREE.MeshBasicMaterial({ color: '#d0e8f8', transparent: true, opacity: 0.6 })); s.visible = false; add(s); shards.push({ s, v: [(r() - 0.5) * 2, r() * 1.5, -0.5 - r() * 1.5], rot: r() * 10 }); }
  const emerg = add(new THREE.PointLight('#ff3020', 0, 0, 1.3)); emerg.position.set(0, 3.2, 2);
  const emergBox = add(new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.12, 0.2), new THREE.MeshBasicMaterial({ color: '#4a1410' }))); emergBox.position.set(0, H - 0.07, 2);

  // ---------- Draußen: Hof, Trafos, Flutlicht, Stadt, Polizei ----------
  const yard = add(new THREE.Mesh(new THREE.PlaneGeometry(200, 120), toon('#4a4a46'))); yard.rotation.x = -Math.PI / 2; yard.position.set(0, -0.02, -66);
  const outBoxes = []; for (const [x, z] of [[-9, -16], [9, -18], [-10, -30], [10, -34]]) outBoxes.push({ p: [x, 1.9, z], s: [3.2, 3.8, 4.2], c: '#7a8278' });
  add(instanced(BOX, toon('#ffffff'), outBoxes, 0.6));
  const fence = add(new THREE.Mesh(new THREE.PlaneGeometry(60, 2.6), new THREE.MeshBasicMaterial({ color: '#7a8088', transparent: true, opacity: 0.35, side: THREE.DoubleSide }))); fence.position.set(0, 1.3, -46);
  const floodG = []; for (const [x, z] of [[-11, -14], [11, -12], [-11, -40], [11, -42]]) { const m = add(new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.18, 9, 8), toon('#6a6e72'))); m.position.set(x, 4.5, z); const g = add(new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: '#fff2d0', transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }))); g.scale.set(2.2, 2.2, 1); g.position.set(x, 9, z); floodG.push(g); }
  const yardL = add(new THREE.PointLight('#fff0d0', 30, 60, 1.2)); yardL.position.set(0, 9, -20);
  const city = []; const cityW = [];
  for (let i = 0; i < 90; i++) { const x = (r() - 0.5) * 300, z = -90 - r() * 160, w = 8 + r() * 12, h = 10 + r() * 45; city.push({ p: [x, h / 2, z], s: [w, h, 8], c: ['#3a4054', '#444a5e', '#353a4a'][(r() * 3) | 0] }); for (let k = 0; k < h / 4; k++) if (r() < 0.55) cityW.push([x + (r() - 0.5) * w * 0.8, 2 + r() * (h - 3), z + 4.1]); }
  add(instanced(BOX, toon('#ffffff'), city, 0.3));
  const cw = add(new THREE.InstancedMesh(new THREE.PlaneGeometry(1.0, 1.3), new THREE.MeshBasicMaterial({ color: '#ffd890', toneMapped: false }), cityW.length)); cw.frustumCulled = false;
  cityW.forEach((p, i) => { cw.setMatrixAt(i, M4.makeTranslation(...p)); cw.setColorAt(i, C.set(i % 3 ? '#ffd890' : '#fff2c8')); });
  // Streifenwagen mit Blaulicht
  const cops = [], copLights = [];
  for (const [x, z, ry] of [[-3, -14, 0.4], [4, -16, -0.3], [0, -24, 0.1]]) { const c = add(car('#e8e8e8', r)); c.position.set(x, 0, z); c.rotation.y = ry; c.visible = false;
    const stripe = new THREE.Mesh(new THREE.BoxGeometry(4.32, 0.18, 1.87), toon('#2a8a4a')); stripe.position.y = 0.75; c.add(stripe);
    const bar = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.12, 1.2), new THREE.MeshBasicMaterial({ color: '#2a5aff' })); bar.position.set(-0.3, 1.72, 0); c.add(bar); cops.push({ c, bar }); }
  for (const [x, z, col] of [[-3, -13, '#2a5aff'], [4, -15, '#ff2a2a'], [0, -22, '#2a5aff']]) { const l = add(new THREE.PointLight(col, 0, 0, 1.3)); l.position.set(x, 2.2, z); copLights.push(l); }
  const blueWash = add(new THREE.PointLight('#3a6aff', 0, 0, 1.4)); blueWash.position.set(0, 2.5, -6.8);

  // ---------- Ereignisse ----------
  const ev = (k) => beats.filter((b) => b.effekt?.[k] !== undefined).map((b) => ({ t0: b.t0, v: b.effekt[k] }));
  const ueb = ev('uebernahme').map(({ t0, v }) => ({ t: t0 + (v.ab || 0), von: v.von ?? 0, bis: v.bis ?? 100, d: v.dauer || 60 }));
  const naT = ev('notaus').map(({ t0, v }) => t0 + (v === true ? 0 : v))[0], polT = ev('polizei').map(({ t0, v }) => t0 + (v === true ? 0 : v))[0];
  const morgen = ev('morgen').map(({ t0, v }) => ({ t: t0 + (v.ab || 0), d: v.dauer || 4 }))[0];
  const pct = (t) => { let p = null; for (const u of ueb) if (t >= u.t) p = u.von + (u.bis - u.von) * Math.min(1, (t - u.t) / u.d); return p; };
  const DAWN = { cTop: new THREE.Color('#4a6ab0'), cMid: new THREE.Color('#8a8ac0'), cLow: new THREE.Color('#f0a080'), cHor: new THREE.Color('#ffc080'), cGlow: new THREE.Color('#fff0c0') };
  let lastK = '';
  const draw = (t, p, off, ok) => {
    const k = `${p === null ? -1 : Math.floor(p)}|${off}|${ok}|${Math.floor(t * 4)}`; if (k === lastK) return; lastK = k;
    // Schalttafel
    let g = mimic.g; g.fillStyle = off ? '#050505' : '#0c1620'; g.fillRect(0, 0, 1024, 480);
    if (!off) {
      const frac = ok ? 0 : (p || 0) / 100;
      links.forEach(([a, b], i) => { const red = (i / links.length) < frac; g.strokeStyle = red ? '#ff3a2a' : '#3aff7a'; g.lineWidth = red ? 5 : 3; g.beginPath(); g.moveTo(...nodes[a]); g.lineTo(...nodes[b]); g.stroke(); });
      nodes.forEach(([x, y], i) => { g.fillStyle = (i / nodes.length) < frac ? '#ff5a3a' : '#c8ffd8'; g.fillRect(x - 7, y - 7, 14, 14); });
      g.fillStyle = '#e8f0ff'; g.font = '900 34px Inter, sans-serif'; g.fillText('STADTNETZ · SCHALTBILD', 24, 44);
      g.fillStyle = ok ? '#3aff7a' : '#ff3a2a'; g.font = '900 40px "Courier New", monospace'; g.textAlign = 'right'; g.fillText(ok ? 'NETZ STABIL' : `ÜBERNAHME ${Math.floor(p || 0)}%`, 1000, 460); g.textAlign = 'left';
    }
    mimic.t.needsUpdate = true;
    // Hauptmonitor
    g = mainScr.g; g.fillStyle = off ? '#020202' : '#08101c'; g.fillRect(0, 0, 768, 256);
    if (!off) {
      if (ok) { g.fillStyle = '#3aff7a'; g.font = '900 48px "Courier New", monospace'; g.fillText('SYSTEM SAUBER', 140, 140); }
      else { g.fillStyle = '#ff6a3a'; g.font = '900 36px "Courier New", monospace'; g.fillText(`NETZÜBERNAHME ${Math.floor(p || 0)}%`, 30, 60); g.fillStyle = '#333'; g.fillRect(30, 90, 700, 30); g.fillStyle = '#ff3a2a'; g.fillRect(30, 90, 7 * (p || 0), 30);
        g.fillStyle = '#6ab0ff'; g.font = '18px monospace'; for (let i = 0; i < 5; i++) g.fillText(`> zugriff ${['WASSER', 'KLINIK', 'AMPELN', 'BAHN', 'NORD'][(i + Math.floor(t * 2)) % 5]} ... ${Math.floor(t * 37 + i * 13) % 100}%`, 30, 150 + i * 22); }
    }
    mainScr.t.needsUpdate = true;
    g = sideScr.g; g.fillStyle = off ? '#020202' : '#0a1a2a'; g.fillRect(0, 0, 256, 192); if (!off) { g.strokeStyle = '#3a8ad0'; g.lineWidth = 3; g.beginPath(); for (let j = 0; j < 24; j++) g.lineTo(j * 11, 100 + Math.sin(j * 0.7 + t * 3) * 40); g.stroke(); } sideScr.t.needsUpdate = true;
    // Wanduhr
    g = clockC.g; g.fillStyle = '#f0ece0'; g.beginPath(); g.arc(64, 64, 60, 0, 7); g.fill(); g.strokeStyle = '#222'; g.lineWidth = 6; g.stroke();
    const mins = ok && morgen && t > morgen.t ? 6 * 60 + 12 : 1 + Math.floor(t / 60), hA = (mins / 60) / 12 * 6.283, mA = (mins % 60) / 60 * 6.283, sA = (t % 60) / 60 * 6.283;
    g.lineCap = 'round'; g.lineWidth = 7; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(hA) * 28, 64 - Math.cos(hA) * 28); g.stroke(); g.lineWidth = 4; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(mA) * 44, 64 - Math.cos(mA) * 44); g.stroke(); g.strokeStyle = '#c0201a'; g.lineWidth = 2; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(sA) * 48, 64 - Math.cos(sA) * 48); g.stroke(); clockC.t.needsUpdate = true;
  };

  root.userData.update = ({ t = 0, sky }) => {
    const off = naT !== undefined && t >= naT, mk = morgen ? ease((t - morgen.t) / morgen.d) : 0, ok = mk > 0;
    if (sky) {
      sky.amb.intensity *= off && !ok ? 0.22 : 0.45 + mk * 0.6; sky.sun.intensity = sky.sun.intensity * 0.3 + mk * 1.6; if (mk > 0) sky.sun.color.set('#ffd8a0');
      const dome = scene.getObjectByName('sky')?.children[0]; if (dome && mk > 0) for (const k of Object.keys(DAWN)) dome.material.uniforms[k].value.lerp(DAWN[k], mk);
    }
    draw(t, pct(t), off && !ok, ok);
    // Raumlicht: anfangs Notbetrieb (halb), nach NOT-AUS rot, am Morgen wieder an
    const roomOn = !off || ok;
    panels.forEach((m, i) => m.material.color.set(roomOn && (ok || i % 2 === 0) ? '#f0f4f0' : '#3a3c3a')); roomL.forEach((l) => (l.intensity = roomOn ? (ok ? 2 : 2.4) : 0));
    consoleL.intensity = off && !ok ? 0 : 2.2; mimicL.intensity = off && !ok ? 0 : 2.5; [mainMon, ...sideMons, ...crts].forEach((s) => s.material.color.set(off && !ok ? '#111' : '#fff'));
    emerg.intensity = off && !ok ? 2.4 + Math.sin(t * 4) * 0.4 : 0; emergBox.material.color.set(off && !ok ? '#ff3020' : '#4a1410');
    // Server-LEDs
    leds.forEach((l, i) => ledMesh.setColorAt(i, C.set(off && !ok ? '#100' : (Math.sin(t * (3 + (i % 7)) + l.ph) > 0.2 ? (i % 9 === 0 ? '#ffb020' : '#3aff6a') : '#0a2a10')))); ledMesh.instanceColor.needsUpdate = true;
    // NOT-AUS: Glas splittert, Knopf gedrückt
    const nk = naT !== undefined ? t - naT : -1; naGlass.visible = nk < 0; naBtn.position.z = nk >= 0 ? -0.04 : -0.08;
    shards.forEach(({ s, v, rot }) => { s.visible = nk >= 0 && nk < 1.5; if (!s.visible) return; const k = nk; s.position.set(-4 + v[0] * k * 0.4, Math.max(0.01, 1.45 + v[1] * k - 4.9 * k * k), Z1 - 0.2 + v[2] * k * 0.4); s.rotation.set(rot * k, rot * k * 0.7, 0); });
    // Polizei
    const pk = polT !== undefined ? t - polT : -1; cops.forEach(({ c, bar }, i) => { c.visible = pk >= 0; bar.material.color.set(Math.floor(t * 6 + i) % 2 ? '#2a5aff' : '#ff2a2a'); });
    copLights.forEach((l, i) => (l.intensity = pk >= 0 && !ok ? (Math.floor(t * 6 + i) % 2 ? 40 : 0) : 0));
    blueWash.intensity = pk >= 0 && !ok ? (Math.floor(t * 5) % 2 ? 6 : 1) : 0;
    floodG.forEach((g) => (g.material.opacity = ok ? 0.15 : 0.7)); yardL.intensity = ok ? 0 : 30;
  };
  return root;
}
