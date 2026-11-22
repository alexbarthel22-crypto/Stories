// Set "umspannwerk": Umspannwerk Nord kurz vor Mitternacht. Notstrom: Flutlicht, Leitwarte, Countdown.
// Weg entlang Z: Tor bei z = +20, Leitwarte bei z = -25. Transformatoren links/rechts, Schaltschrank mit zwei Schlüsseln
// rechts am Weg (x = 2.2, Schlüssel bei z = -7.0 und -9.0). Die dunkle Stadt liegt links (-X) hinter dem Zaun.
//
// Beat-Effekte (Feld "effekt"):
//   countdown: Sekunden         -> Anzeige springt auf diesen Wert und zählt herunter
//   funken: s | [s, …]          -> Überschlag an einem Isolator (Funken + Lichtblitz)
//   flutlicht: s                -> alle Flutlichter schalten mit einem Schlag hell
//   schluessel: s               -> beide Schlüssel drehen sich
//   knall: s                    -> riesiger Überschlag: weißer Blitz, alles kurz dunkel
//   licht_an: s                 -> die Stadt bekommt ihr Licht zurück (Welle von innen nach außen)
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, cracks, rng } from '../toon.js';

export const info = {
  start: [0.3, 16],
  spots: {
    weg: [0, -4], warte: [0, 4], tor: [180, -4], stadt: [90, 2], schrank: [-42, -3], trafo: [-60, 6], himmel: [0, 55], links: [90, -4], rechts: [-90, -4], boden: [0, -60],
  },
};
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
const BOX = new THREE.BoxGeometry(1, 1, 1);
function instanced(geo, mat, items, inkW = 0.5) {
  const m = inkW ? inkInstanced(geo, mat, items.length, inkW) : new THREE.InstancedMesh(geo, mat, items.length);
  items.forEach((it, i) => { E.set(it.rx || 0, it.ry || 0, it.rz || 0); Q.setFromEuler(E); m.setMatrixAt(i, M4.compose(P.set(...it.p), Q, S.set(...(it.s || [1, 1, 1])))); if (it.c) m.setColorAt(i, C.set(it.c)); });
  m.castShadow = true; m.receiveShadow = true; return m;
}

export function build(scene, seed = 41, ctx = {}) {
  const beats = ctx.beats || [];
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o) => (root.add(o), o);
  scene.fog = new THREE.Fog('#141826', 30, 320);
  const glowTex = canvasTex(64, 64, (c, w) => { const g = c.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(0, 0, w, w); });
  const glow = (col, size, op = 0.5) => { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: col, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false, fog: false })); m.scale.set(size, size, 1); return m; };

  // ---------- Boden: Schotter, Betonweg, Pfützen ----------
  const gravel = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#4a4a46'; c.fillRect(0, 0, w, h); for (let i = 0; i < 1800; i++) { c.fillStyle = ['#5e5c56', '#3e3e3a', '#6a6860', '#34342f'][(r() * 4) | 0]; c.beginPath(); c.ellipse(r() * w, r() * h, 1.5 + r() * 2.5, 1 + r() * 2, r() * 3, 0, 7); c.fill(); } stains(c, w, h, r, 10, '20,20,18', 0.4); }, { repeat: [30, 30] });
  const ground = add(new THREE.Mesh(new THREE.PlaneGeometry(120, 120), toon('#ffffff', { map: gravel }))); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true;
  const conc = canvasTex(256, 512, (c, w, h) => { c.fillStyle = '#8a8880'; c.fillRect(0, 0, w, h); c.strokeStyle = 'rgba(40,38,34,0.6)'; c.lineWidth = 3; for (let y = 0; y < h; y += 128) { c.beginPath(); c.moveTo(0, y); c.lineTo(w, y); c.stroke(); } stains(c, w, h, r, 20, '40,38,30', 0.35); cracks(c, w, h, r, 6, 2); }, { repeat: [1, 12] });
  const path = add(new THREE.Mesh(new THREE.PlaneGeometry(3.2, 50), toon('#ffffff', { map: conc }))); path.rotation.x = -Math.PI / 2; path.position.set(0, 0.01, -3); path.receiveShadow = true;
  const pud = new THREE.MeshBasicMaterial({ color: '#22283a' }), pudHi = new THREE.MeshBasicMaterial({ color: '#5a6488', transparent: true, opacity: 0.5 });
  for (const [x, z, a] of [[-2.6, 8, 1.2], [2.8, 2, 0.9], [-1.8, -12, 1.4], [3.5, -16, 1.0], [-3.2, -3, 0.8]]) { const p = add(new THREE.Mesh(new THREE.CircleGeometry(1, 20), pud)); p.rotation.x = -Math.PI / 2; p.scale.set(a, a * 0.55, 1); p.position.set(x, 0.015, z); const h = add(new THREE.Mesh(new THREE.CircleGeometry(1, 12), pudHi)); h.rotation.x = -Math.PI / 2; h.scale.set(a * 0.3, a * 0.12, 1); h.position.set(x - a * 0.3, 0.018, z - 0.2); }

  // ---------- Transformatoren ----------
  const insul = []; // Isolatorspitzen (für Funken)
  const trafo = (x, z, rot) => {
    const g = new THREE.Group(); add(g); g.position.set(x, 0, z); g.rotation.y = rot;
    const tank = ink(new THREE.BoxGeometry(3.2, 3.0, 4.2), toon('#7a8278'), 0.9); tank.position.y = 1.9; g.add(edges(tank));
    const base = ink(new THREE.BoxGeometry(3.8, 0.4, 4.8), toon('#9a9890'), 0.7); base.position.y = 0.2; g.add(base);
    const fins = []; for (let k = 0; k < 9; k++) fins.push({ p: [1.75, 1.9, -1.8 + k * 0.45], s: [0.35, 2.6, 0.06], c: '#6a726a' }, { p: [-1.75, 1.9, -1.8 + k * 0.45], s: [0.35, 2.6, 0.06], c: '#6a726a' });
    g.add(instanced(BOX, toon('#ffffff'), fins, 0.3));
    const cons = ink(new THREE.CylinderGeometry(0.45, 0.45, 2.4, 14), toon('#7a8278'), 0.7); cons.rotation.x = Math.PI / 2; cons.position.set(0, 3.9, -1.0); g.add(cons);
    for (let k = -1; k <= 1; k++) { // Durchführungen mit Isolator-Scheiben
      const bush = new THREE.Group(); bush.position.set(k * 0.9, 3.4, 0.8); g.add(bush);
      for (let j = 0; j < 7; j++) { const d = ink(new THREE.CylinderGeometry(0.2, 0.2, 0.06, 14), toon('#8a5a3a'), 0.4); d.position.y = 0.15 + j * 0.2; bush.add(d); }
      const core = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 1.6, 8), toon('#7a4a2a')); core.position.y = 0.8; bush.add(core);
      const cap = ink(new THREE.CylinderGeometry(0.1, 0.1, 0.12, 8), toon('#b8b8b0'), 0.4); cap.position.y = 1.65; bush.add(cap);
      insul.push(bush.localToWorld ? null : null); g.updateMatrixWorld(true); insul[insul.length - 1] = cap.getWorldPosition(new THREE.Vector3());
    }
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.6), toon('#ffffff', { map: warnTex })); sign.position.set(0, 1.9, 2.12); g.add(sign);
    const plate = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.4), toon('#ffffff', { map: canvasTex(256, 72, (c, w, h) => { c.fillStyle = '#e8e4d4'; c.fillRect(0, 0, w, h); c.fillStyle = '#111'; c.font = '900 30px Inter, sans-serif'; c.fillText(`T${(r() * 9 + 1) | 0} · 110/20 kV`, 12, 46); }) })); plate.position.set(0, 2.7, 2.12); g.add(plate);
  };
  const warnTex = canvasTex(128, 128, (c, w, h) => { c.fillStyle = '#f0c020'; c.beginPath(); c.moveTo(w / 2, 8); c.lineTo(w - 6, h - 10); c.lineTo(6, h - 10); c.closePath(); c.fill(); c.lineWidth = 7; c.strokeStyle = '#111'; c.stroke(); c.fillStyle = '#111'; c.beginPath(); c.moveTo(70, 34); c.lineTo(48, 74); c.lineTo(64, 74); c.lineTo(54, 104); c.lineTo(84, 62); c.lineTo(68, 62); c.lineTo(80, 34); c.closePath(); c.fill(); });
  for (const [x, z] of [[-6.5, 8], [6.5, 8], [-6.5, -2], [6.8, -16], [-6.5, -14]]) trafo(x, z, x < 0 ? Math.PI / 2 : -Math.PI / 2);
  // ---------- Stahlportale mit Leitungen (Gitter aus dünnen Balken) ----------
  const steel = toon('#8a9088'), bars = [];
  const beam = (a, b, t = 0.12) => { const v = new THREE.Vector3(...b).sub(new THREE.Vector3(...a)); const len = v.length(); Q.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.clone().normalize()); E.setFromQuaternion(Q); bars.push({ p: [a[0] + v.x / 2, a[1] + v.y / 2, a[2] + v.z / 2], rx: E.x, ry: E.y, rz: E.z, s: [t, len, t] }); };
  const tower = (x, z, h) => { const w = 0.7; for (const [dx, dz] of [[-w, -w], [w, -w], [w, w], [-w, w]]) beam([x + dx, 0, z + dz], [x + dx * 0.6, h, z + dz * 0.6]); for (let y = 1.5; y < h; y += 1.6) { beam([x - w, y, z - w], [x + w, y + 1.6, z - w], 0.06); beam([x + w, y, z + w], [x - w, y + 1.6, z + w], 0.06); beam([x - w, y, z + w], [x - w, y + 1.6, z - w], 0.06); beam([x + w, y, z - w], [x + w, y + 1.6, z + w], 0.06); } };
  for (const z of [3, -10]) { tower(-9, z, 10); tower(9, z, 10); beam([-9, 10, z - 0.5], [9, 10, z - 0.5], 0.22); beam([-9, 10, z + 0.5], [9, 10, z + 0.5], 0.22); for (let x = -8; x <= 8; x += 2) { beam([x, 10, z - 0.5], [x + 2, 10, z + 0.5], 0.06); } }
  add(instanced(BOX, steel, bars, 0.35));
  // Isolatorketten + durchhängende Leitungen zwischen Portalen und zu den Trafos
  const wireMat = toon('#2a2a2a');
  const wire = (a, b, sag) => { const pts = []; for (let i = 0; i <= 12; i++) { const k = i / 12; pts.push(new THREE.Vector3(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k - Math.sin(Math.PI * k) * sag, a[2] + (b[2] - a[2]) * k)); } add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 20, 0.025, 4), wireMat)); };
  for (const x of [-4, 0, 4]) { wire([x, 9.2, 3], [x, 9.2, -10], 0.9); wire([x, 9.2, 3], [x, 9.2, 60], 3.5); wire([x, 9.2, -10], [x, 9.2, -60], 3.5); for (const z of [3, -10]) { const chain = add(ink(new THREE.CylinderGeometry(0.12, 0.12, 0.8, 8), toon('#8a5a3a'), 0.4)); chain.position.set(x, 9.6, z); } }
  for (const [tx, tz] of [[-6.5, 8], [6.5, 8], [-6.5, -2], [6.8, -16]]) wire([tx * 0.7, 5.2, tz], [Math.sign(tx) * 4, 9.2, tz > 0 ? 3 : -10], 0.5);
  // Ferne Strommasten
  for (let i = 0; i < 6; i++) { const z = -70 - i * 45, x = 10 + Math.sin(i) * 8; const pylon = []; const h = 30; for (const [dx, dz] of [[-2, -2], [2, -2], [2, 2], [-2, 2]]) { const v = [x + dx * 0.25 - (x + dx), h, 0]; } const m = add(edges(ink(new THREE.CylinderGeometry(0.4, 2.4, h, 4, 1, true), toon('#5a6070', { side: THREE.DoubleSide, wireframe: false }), 0.3))); m.position.set(x, h / 2, z); const arm = add(ink(new THREE.BoxGeometry(12, 0.4, 0.4), toon('#5a6070'), 0.3)); arm.position.set(x, h - 4, z); }

  // ---------- Zaun mit Stacheldraht, Tor, Warnschilder ----------
  const meshTex = canvasTex(128, 128, (c, w, h) => { c.clearRect(0, 0, w, h); c.strokeStyle = 'rgba(190,195,200,0.85)'; c.lineWidth = 2; for (let i = -h; i < w; i += 16) { c.beginPath(); c.moveTo(i, 0); c.lineTo(i + h, h); c.stroke(); c.beginPath(); c.moveTo(i + h, 0); c.lineTo(i, h); c.stroke(); } }, { repeat: [20, 1] });
  const fenceMat = new THREE.MeshBasicMaterial({ map: meshTex, transparent: true, alphaTest: 0.3, side: THREE.DoubleSide, color: '#9aa0a8' });
  const fence = (x0, z0, x1, z1) => { const len = Math.hypot(x1 - x0, z1 - z0); const m = add(new THREE.Mesh(new THREE.PlaneGeometry(len, 2.6), fenceMat.clone())); m.material.map = meshTex.clone(); m.material.map.repeat.set(len / 1.2, 1); m.material.map.needsUpdate = true; m.position.set((x0 + x1) / 2, 1.3, (z0 + z1) / 2); m.rotation.y = -Math.atan2(z1 - z0, x1 - x0);
    for (let k = 0; k <= len; k += 3) { const px = x0 + (x1 - x0) * k / len, pz = z0 + (z1 - z0) * k / len; const post = add(ink(new THREE.CylinderGeometry(0.05, 0.05, 3.0, 6), toon('#6a6e72'), 0.4)); post.position.set(px, 1.5, pz); }
    for (const y of [2.75, 2.9, 3.0]) { const wv = add(new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, len, 4), toon('#5a5a5a'))); wv.rotation.z = Math.PI / 2; wv.rotation.y = -Math.atan2(z1 - z0, x1 - x0); wv.position.set((x0 + x1) / 2, y, (z0 + z1) / 2); }
    for (let k = 4; k < len; k += 12) { const s2 = add(new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.5), toon('#ffffff', { map: warnTex, side: THREE.DoubleSide }))); s2.position.set(x0 + (x1 - x0) * k / len, 1.6, z0 + (z1 - z0) * k / len); s2.rotation.y = m.rotation.y; } };
  fence(-14, 20, -2, 20); fence(2, 20, 14, 20); fence(-14, 20, -14, -32); fence(14, 20, 14, -32); fence(-14, -32, 14, -32);
  const gateL = add(new THREE.Group()); gateL.position.set(-2, 0, 20); const gateR = add(new THREE.Group()); gateR.position.set(2, 0, 20);
  for (const [g, s] of [[gateL, 1], [gateR, -1]]) { const m = new THREE.Mesh(new THREE.PlaneGeometry(2, 2.4), fenceMat); m.position.set(s, 1.3, 0); g.add(m); const fr = ink(new THREE.BoxGeometry(2, 0.06, 0.06), toon('#6a6e72'), 0.3); fr.position.set(s, 2.5, 0); g.add(fr); const fr2 = fr.clone(); fr2.position.y = 0.1; g.add(fr2); }
  const bigSign = add(new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.0), toon('#ffffff', { map: canvasTex(512, 196, (c, w, h) => { c.fillStyle = '#f0ece0'; c.fillRect(0, 0, w, h); c.fillStyle = '#c8201a'; c.fillRect(0, 0, w, 50); c.fillStyle = '#fff'; c.font = '900 36px Inter, sans-serif'; c.fillText('HOCHSPANNUNG', 14, 38); c.fillStyle = '#111'; c.font = '900 44px Inter, sans-serif'; c.fillText('LEBENSGEFAHR', 14, 108); c.font = '700 26px Inter, sans-serif'; c.fillText('Umspannwerk Nord · Stadtwerke', 14, 160); }), side: THREE.DoubleSide }))); bigSign.position.set(-5, 2.0, 19.95);

  // ---------- Schaltschrank mit zwei Schlüsseln + Display ----------
  const cab = add(new THREE.Group()); cab.position.set(2.2, 0, -8);
  cab.add(edges(ink(new THREE.BoxGeometry(0.8, 2.2, 3.4), toon('#8a908a'), 0.8))).position.y = 1.1;
  const scrCanvas = document.createElement('canvas'); scrCanvas.width = 512; scrCanvas.height = 160; const scrTex = new THREE.CanvasTexture(scrCanvas); scrTex.colorSpace = THREE.SRGBColorSpace;
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.47), new THREE.MeshBasicMaterial({ map: scrTex, toneMapped: false })); scr.position.set(-0.41, 1.75, 0); scr.rotation.y = -Math.PI / 2; cab.add(scr);
  const keys = [];
  for (const dz of [1.0, -1.0]) {
    const plate = ink(new THREE.CylinderGeometry(0.13, 0.13, 0.04, 16), toon('#2a2a2a'), 0.4); plate.rotation.z = Math.PI / 2; plate.position.set(-0.42, 1.15, dz); cab.add(plate);
    const key = new THREE.Group(); key.position.set(-0.46, 1.15, dz); cab.add(key);
    const bow = ink(new THREE.BoxGeometry(0.03, 0.12, 0.16), toon('#d8b040'), 0.4); bow.position.x = -0.06; key.add(bow);
    const shaft = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.02, 0.03), toon('#c8a030')); key.add(shaft);
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), new THREE.MeshBasicMaterial({ color: '#ff2a1a' })); led.position.set(-0.41, 1.4, dz); cab.add(led);
    keys.push({ key, led });
    const lab = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.1), toon('#ffffff', { map: canvasTex(128, 32, (c, w, h) => { c.fillStyle = '#e8e4d4'; c.fillRect(0, 0, w, h); c.fillStyle = '#111'; c.font = '900 18px Inter, sans-serif'; c.fillText(dz > 0 ? 'SCHLÜSSEL A' : 'SCHLÜSSEL B', 8, 22); }) })); lab.position.set(-0.415, 0.95, dz); lab.rotation.y = -Math.PI / 2; cab.add(lab);
  }
  const cabSign = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.5), toon('#ffffff', { map: warnTex })); cabSign.position.set(-0.41, 0.55, 0); cabSign.rotation.y = -Math.PI / 2; cab.add(cabSign);
  const cabLight = add(new THREE.PointLight('#8ab8ff', 2.5, 0, 1.6)); cabLight.position.set(1.4, 1.9, -8);

  // ---------- Leitwarte (Gebäude mit Bildschirmen) ----------
  const bld = add(edges(ink(new THREE.BoxGeometry(18, 6, 8), toon('#b8b0a0'), 0.8))); bld.position.set(0, 3, -28);
  const wallCanvas = document.createElement('canvas'); wallCanvas.width = 1024; wallCanvas.height = 300; const wallTex = new THREE.CanvasTexture(wallCanvas); wallTex.colorSpace = THREE.SRGBColorSpace;
  const win = add(new THREE.Mesh(new THREE.PlaneGeometry(10, 2.6), new THREE.MeshBasicMaterial({ map: wallTex, toneMapped: false }))); win.position.set(0, 3.4, -23.96);
  const winFrame = add(ink(new THREE.BoxGeometry(10.3, 2.9, 0.1), toon('#3a3a3a'), 0.5)); winFrame.position.set(0, 3.4, -24.02);
  const doorB = add(ink(new THREE.BoxGeometry(1.4, 2.4, 0.1), toon('#3a5a7a'), 0.5)); doorB.position.set(6.5, 1.2, -23.95);
  const roofSign = add(new THREE.Mesh(new THREE.PlaneGeometry(8, 1.0), toon('#ffffff', { map: canvasTex(512, 64, (c, w, h) => { c.fillStyle = '#1f3a6a'; c.fillRect(0, 0, w, h); c.fillStyle = '#f0e0a0'; c.font = '900 40px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('LEITWARTE · UMSPANNWERK NORD', w / 2, h / 2 + 2); }) }))); roofSign.position.set(0, 5.5, -23.95);
  const warteLight = add(new THREE.PointLight('#6aa8ff', 4, 0, 1.4)); warteLight.position.set(0, 3, -21);

  // ---------- Flutlichtmasten ----------
  const floods = [];
  for (const [x, z, tx, tz] of [[-11, 14, -2, 4], [11, 12, 2, 2], [-11, -18, -1, -9], [11, -20, 2, -10]]) {
    const mast = add(ink(new THREE.CylinderGeometry(0.12, 0.18, 9, 8), toon('#6a6e72'), 0.5)); mast.position.set(x, 4.5, z);
    const head = add(ink(new THREE.BoxGeometry(0.9, 0.5, 0.4), toon('#3a3a3a'), 0.5)); head.position.set(x, 9.0, z); head.lookAt(tx, 0, tz);
    const lens = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 0.4), new THREE.MeshBasicMaterial({ color: '#fff6dc' })); lens.position.z = 0.21; head.add(lens);
    const g = add(glow('#fff2d0', 1.6, 0.6)); g.position.set(x, 9.0, z);
    const sp = add(new THREE.SpotLight('#fff0d0', 0, 60, 0.55, 0.6, 1.0)); sp.position.set(x, 9, z); sp.target.position.set(tx, 0, tz); add(sp.target);
    const cone = add(new THREE.Mesh(new THREE.ConeGeometry(4.5, 11, 20, 1, true), new THREE.MeshBasicMaterial({ color: '#fff2d0', transparent: true, opacity: 0.06, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false })));
    const dir = new THREE.Vector3(tx - x, -9, tz - z).normalize(); cone.position.set(x, 9, z).addScaledVector(dir, 5.5); cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir);
    floods.push({ lens, g, sp, cone, x, z });
  }
  // Motten um die Flutlichter
  const moths = new THREE.InstancedMesh(new THREE.SphereGeometry(0.03, 4, 3), new THREE.MeshBasicMaterial({ color: '#f0e8d0' }), 40); add(moths); moths.frustumCulled = false;
  const MO = Array.from({ length: 40 }, (_, i) => ({ f: i % 4, ph: r() * 10, rad: 0.3 + r() * 0.8, sp: 3 + r() * 5 }));

  // ---------- Stadt hinter dem Zaun (links, -X) ----------
  const cityWins = [], cityBoxes = [];
  for (let i = 0; i < 140; i++) {
    const x = -30 - r() * 160, z = 40 - r() * 150, w = 6 + r() * 10, h = 8 + r() * 40, d = 6 + r() * 10;
    cityBoxes.push({ p: [x, h / 2, z], s: [w, h, d], c: ['#3a4054', '#444a5e', '#353a4a'][(r() * 3) | 0] });
    for (let k = 0; k < 4 + h / 5; k++) if (r() < 0.6) cityWins.push({ p: [x + w / 2 + 0.05, 2 + r() * (h - 3), z + (r() - 0.5) * d * 0.8], d: Math.hypot(x + 30, z + 10) });
  }
  add(instanced(BOX, toon('#ffffff'), cityBoxes, 0.3));
  const cw = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.9, 1.2), new THREE.MeshBasicMaterial({ color: '#ffffff', side: THREE.DoubleSide, toneMapped: false }), cityWins.length); add(cw); cw.frustumCulled = false;
  cityWins.forEach((wv, i) => { E.set(0, Math.PI / 2, 0); Q.setFromEuler(E); cw.setMatrixAt(i, M4.compose(P.set(...wv.p), Q, S.set(1, 1, 1))); cw.setColorAt(i, C.set('#1a1e2a')); });
  const skyGlow = add(new THREE.Mesh(new THREE.PlaneGeometry(400, 60), new THREE.MeshBasicMaterial({ color: '#ff9a50', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, fog: false, map: glowTex }))); skyGlow.position.set(-150, 20, -30); skyGlow.rotation.y = Math.PI / 2;

  // ---------- Nebel, Funken ----------
  const mist = (() => { const N = 60, pos = new Float32Array(N * 3); for (let i = 0; i < N; i++) pos.set([(Math.random() - 0.5) * 26, 0.4 + Math.random() * 1.2, 18 - Math.random() * 44], i * 3);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const m = new THREE.ShaderMaterial({ uniforms: { uT: { value: 0 }, uPx: { value: 768 } }, transparent: true, depthWrite: false,
      vertexShader: `uniform float uT, uPx; varying float vA; void main(){ vec3 p = position; p.x += sin(uT * 0.08 + position.z) * 2.0; vec4 mv = modelViewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = 5.0 * uPx / -mv.z; vA = 0.07; }`,
      fragmentShader: `varying float vA; void main(){ float d = length(gl_PointCoord - 0.5); float a = smoothstep(0.5, 0.0, d) * vA; if (a < 0.005) discard; gl_FragColor = vec4(0.6, 0.65, 0.8, a); }` });
    const p = new THREE.Points(g, m); p.frustumCulled = false; add(p); return m; })();
  const SPK = 90, spkPos = new Float32Array(SPK * 3), spkVel = [];
  const spkGeo = new THREE.BufferGeometry(); spkGeo.setAttribute('position', new THREE.BufferAttribute(spkPos, 3));
  const sparks = new THREE.Points(spkGeo, new THREE.PointsMaterial({ color: '#d8ecff', size: 0.09, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false })); sparks.frustumCulled = false; add(sparks);
  for (let i = 0; i < SPK; i++) spkVel.push([(r() - 0.5) * 6, r() * 5, (r() - 0.5) * 6, 0.4 + r() * 0.8]);
  const arc = add(glow('#c8e4ff', 3, 0)); const arcL = add(new THREE.PointLight('#bfe0ff', 0, 0, 1.4));

  // ---------- Ereignisse ----------
  const times = (k) => beats.flatMap((b) => (b.effekt?.[k] === undefined ? [] : [].concat(b.effekt[k]).map((v) => b.t0 + (v === true ? 0 : v))));
  const cds = beats.filter((b) => b.effekt?.countdown !== undefined).map((b) => ({ t: b.t0 + (b.effekt.countdown_ab || 0), v: b.effekt.countdown }));
  const sparkT = times('funken'), floodT = times('flutlicht')[0], keyT = times('schluessel')[0], bangT = times('knall')[0], onT = times('licht_an')[0];
  const cdAt = (t) => { let v = null; for (const c of cds) if (t >= c.t) v = Math.max(0, c.v - (t - c.t)); return v; };
  const fmt = (s) => { s = Math.ceil(s); return `00:${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`; };
  let lastKey = '';
  const drawScreens = (t, cd, done) => {
    const k = `${cd === null ? '-' : Math.ceil(cd)}|${done}|${Math.floor(t * 2) % 2}`; if (k === lastKey) return; lastKey = k;
    const blink = Math.floor(t * 2) % 2 === 0;
    let c = scrCanvas.getContext('2d'); c.fillStyle = '#05080c'; c.fillRect(0, 0, 512, 160);
    c.textAlign = 'center'; c.textBaseline = 'middle';
    if (done) { c.fillStyle = '#4aff8a'; c.font = '900 52px "Courier New", monospace'; c.fillText('GELÖSCHT', 256, 80); }
    else { c.fillStyle = cd !== null && cd < 60 ? (blink ? '#ff3a2a' : '#a01a12') : '#ff7a2a'; c.font = '900 72px "Courier New", monospace'; c.fillText(cd === null ? '--:--:--' : fmt(cd), 256, 70); c.font = '700 22px "Courier New", monospace'; c.fillStyle = '#8ab8ff'; c.fillText('NETZÜBERNAHME', 256, 132); }
    scrTex.needsUpdate = true;
    c = wallCanvas.getContext('2d'); c.fillStyle = '#0a1420'; c.fillRect(0, 0, 1024, 300);
    for (let i = 0; i < 4; i++) { const x = 20 + i * 250; c.fillStyle = '#102a44'; c.fillRect(x, 20, 230, 150); c.strokeStyle = '#3a8ad0'; c.lineWidth = 3; c.beginPath(); for (let j = 0; j < 20; j++) c.lineTo(x + j * 12, 100 + Math.sin(j * 0.9 + i + Math.floor(t * 2)) * 30); c.stroke(); c.fillStyle = '#8ac8ff'; c.font = '700 18px monospace'; c.textAlign = 'left'; c.fillText(['NETZ NORD', 'NETZ SÜD', 'WASSER', 'KLINIKEN'][i], x + 8, 40); }
    c.textAlign = 'center'; c.fillStyle = done ? '#4aff8a' : '#ff3a2a'; c.font = '900 80px "Courier New", monospace'; c.fillText(done ? 'SYSTEM FREI' : (cd === null ? '' : fmt(cd)), 512, 245);
    wallTex.needsUpdate = true;
  };

  root.userData.update = ({ t = 0, sky, px = 768 }) => {
    const bang = bangT !== undefined ? t - bangT : -1, flash = bang >= 0 && bang < 0.6 ? 1 - bang / 0.6 : 0, dark = bang >= 0.3 && (onT === undefined || t < onT);
    const lit = onT !== undefined && t >= onT, litK = lit ? ease((t - onT) / 3) : 0;
    if (sky) { sky.amb.intensity *= (dark ? 0.3 : 0.6) + flash * 8; sky.sun.intensity *= 0.6; }
    mist.uniforms.uT.value = t; mist.uniforms.uPx.value = px;
    // Countdown
    const cd = cdAt(t), done = keyT !== undefined && t >= keyT + 0.5; drawScreens(t, cd, done);
    // Flutlicht: zwei laufen von Anfang an schwach, ab "flutlicht" alle voll
    floods.forEach((f, i) => { const full = floodT !== undefined && t >= floodT; const on = !dark && (full || i % 2 === 0); const k = on ? (full ? 1 : 0.45) : 0;
      f.sp.intensity = 38 * k * (lit ? 1.1 : 1); f.g.material.opacity = 0.6 * k; f.cone.visible = false; f.lens.material.color.set(on ? '#fff6dc' : '#3a3a36'); });
    { const gk = floodT !== undefined ? ease((t - floodT + 0.4) / 1.6) : 0; gateL.rotation.y = gk * 1.5; gateR.rotation.y = -gk * 1.5; }
    warteLight.intensity = dark ? 0 : 4; cabLight.intensity = dark ? 0 : 2.5; win.material.color.set(dark ? '#111' : '#fff'); scr.material.color.set(dark ? '#111' : '#fff');
    // Schlüssel
    const kk = keyT !== undefined ? ease((t - keyT) / 0.35) : 0; keys.forEach(({ key, led }) => { key.rotation.x = kk * Math.PI / 2; led.material.color.set(kk > 0.9 ? '#3aff6a' : '#ff2a1a'); });
    // Motten
    MO.forEach((m, i) => { const f = floods[m.f]; const a = t * m.sp + m.ph; P.set(f.x + Math.cos(a) * m.rad, 8.8 + Math.sin(a * 1.7) * 0.4, f.z + Math.sin(a) * m.rad); moths.setMatrixAt(i, M4.makeTranslation(P.x, P.y, P.z)); });
    moths.instanceMatrix.needsUpdate = true;
    // Funken (gelegentlich + bei Effekt + beim Knall)
    let src = null, age = 9;
    for (const st of sparkT) if (t >= st && t - st < 1.2) { src = insul[(Math.floor(st * 7) % insul.length)]; age = t - st; }
    if (!src) { const cyc = t % 9.3; if (cyc < 0.5) { src = insul[Math.floor(t / 9.3) % insul.length]; age = cyc; } }
    if (bang >= 0 && bang < 1.5) { src = new THREE.Vector3(2.0, 2.0, -8); age = bang; }
    if (src) { for (let i = 0; i < SPK; i++) { const v = spkVel[i], a = age * (bang >= 0 && bang < 1.5 ? 1 : 1.4); spkPos.set([src.x + v[0] * a, src.y + v[1] * a - 4.9 * a * a, src.z + v[2] * a], i * 3); } sparks.visible = age < 0.9; sparks.material.opacity = Math.max(0, 1 - age / 0.9); spkGeo.attributes.position.needsUpdate = true;
      const fa = age < 0.15 ? 1 - age / 0.15 : 0; arc.position.copy(src); arc.material.opacity = fa; arcL.position.copy(src); arcL.intensity = fa * (bang >= 0 ? 60 : 12); } else { sparks.visible = false; arc.material.opacity = 0; arcL.intensity = 0; }
    // Stadt: dunkel, ab "licht_an" Welle von innen nach außen
    let ch = false; cityWins.forEach((wv, i) => { const on = lit && (t - onT) * 40 > wv.d * 0.6 + (i % 7) * 2; const col = on ? (i % 3 ? '#ffd890' : '#fff2c8') : '#1a1e2a'; cw.setColorAt(i, C.set(col)); ch = true; }); if (ch) cw.instanceColor.needsUpdate = true;
    skyGlow.material.opacity = 0.25 * litK;
  };
  return root;
}
