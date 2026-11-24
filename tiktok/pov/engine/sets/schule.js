// Set "schule": Schulflur bei Nacht + Bio-Raum. Flur x -2.2 … 2.2, z +10 … -22 (Blick nach -Z = den Gang hinunter).
// Links Spinde, rechts Fenster (Mondlicht), Klassentür 10b (z = 5) und Bio-Raum (Tür z = -16, Raum x 2.2 … 9, z -21 … -12).
//
// Beat-Effekte (Feld "effekt"):
//   lichter: {ab, von: z, nach: z, tempo}  -> Bewegungsmelder: Deckenlichter springen nacheinander an (tempo = Lampen/s)
//   dunkel: s                              -> alle Lichter aus
//   kamera: s                              -> Überwachungskamera folgt ab jetzt dem Spieler (rote LED)
//   spind: s                               -> Spind 47 schwingt langsam auf
//   klingel: s                             -> Schulglocke rasselt (2.5 s)
//   kreide: {ab, dauer}                    -> Schrift erscheint Buchstabe für Buchstabe an der Tafel
//   skelett: s                             -> Skelett dreht den Kopf zum Spieler und hebt den Arm
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, rng } from '../toon.js';

export const info = {
  start: [0, 8],
  spots: {
    gang: [0, -2], zurueck: [180, -4], spinde: [70, -8], fenster: [-70, 4], kamera: [-20, 32], decke: [0, 70], boden: [0, -60],
    biotuer: [-25, -4], tafel: [0, 2], skelett: [-20, -2], aquarium: [-120, -10], uhr: [0, 20],
  },
};
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
const BOX = new THREE.BoxGeometry(1, 1, 1);
const HW = 2.2, ZA = 10, ZB = -22, H = 3.2;
function instanced(geo, mat, items, inkW = 0.5) {
  const m = inkW ? inkInstanced(geo, mat, items.length, inkW) : new THREE.InstancedMesh(geo, mat, items.length);
  items.forEach((it, i) => { E.set(it.rx || 0, it.ry || 0, it.rz || 0); Q.setFromEuler(E); m.setMatrixAt(i, M4.compose(P.set(...it.p), Q, S.set(...(it.s || [1, 1, 1])))); if (it.c) m.setColorAt(i, C.set(it.c)); });
  m.castShadow = true; m.receiveShadow = true; return m;
}

export function build(scene, seed = 61, ctx = {}) {
  const beats = ctx.beats || [];
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o) => (root.add(o), o);
  scene.fog = new THREE.Fog('#0c0f1a', 14, 60);
  const glowTex = canvasTex(64, 64, (c, w) => { const g = c.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(0, 0, w, w); });
  const glow = (col, size, op) => { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: col, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false, fog: false })); m.scale.set(size, size, 1); return m; };
  const plane = (w, h, tex, x, y, z, ry, opts = {}) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), toon('#ffffff', { map: tex, ...opts }))); m.position.set(x, y, z); m.rotation.y = ry; return m; };

  // ---------- Flur: Boden, Decke, Wände ----------
  const lino = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#6a7a6e'; c.fillRect(0, 0, w, h); for (let i = 0; i < 2500; i++) { c.fillStyle = ['#7a8a7e', '#5a6a5e', '#8a9a8a', '#4a5a50'][(r() * 4) | 0]; c.fillRect(r() * w, r() * h, 2, 2); } c.fillStyle = 'rgba(255,255,255,0.07)'; c.fillRect(w * 0.42, 0, w * 0.16, h); stains(c, w, h, r, 8, '30,30,26', 0.25); }, { repeat: [3, 20] });
  const floor = add(new THREE.Mesh(new THREE.PlaneGeometry(2 * HW, ZA - ZB), toon('#ffffff', { map: lino }))); floor.rotation.x = -Math.PI / 2; floor.position.z = (ZA + ZB) / 2; floor.receiveShadow = true;
  const ceil = add(new THREE.Mesh(new THREE.PlaneGeometry(2 * HW, ZA - ZB), toon('#c8c4b8'))); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, H, (ZA + ZB) / 2);
  const paint = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#e8e2d0'; c.fillRect(0, 0, w, h); c.fillStyle = '#6a8ab0'; c.fillRect(0, h * 0.68, w, h * 0.32); c.fillStyle = '#3a5a80'; c.fillRect(0, h * 0.67, w, 6); stains(c, w, h, r, 10, '80,70,50', 0.18); }, { repeat: [10, 1] });
  const wallM = toon('#ffffff', { map: paint });
  const lw = add(new THREE.Mesh(new THREE.PlaneGeometry(ZA - ZB, H), wallM)); lw.position.set(-HW, H / 2, (ZA + ZB) / 2); lw.rotation.y = Math.PI / 2; lw.receiveShadow = true;
  // rechte Wand mit Fensteröffnungen (z -1 … -9) und zwei Türen (z 5 und -16)
  const rwSeg = (z0, z1, y0, y1) => { const m = add(new THREE.Mesh(new THREE.BoxGeometry(0.2, y1 - y0, z1 - z0), toon('#ffffff', { map: paint }))); m.position.set(HW + 0.1, (y0 + y1) / 2, (z0 + z1) / 2); m.receiveShadow = true; m.castShadow = true; return m; };
  const WIN = [[-1.2, -3.8], [-4.4, -7.0], [-7.6, -10.2]];
  rwSeg(5.6, ZA, 0, H); rwSeg(4.4, 5.6, 2.3, H); rwSeg(-1.2, 4.4, 0, H);
  WIN.forEach(([a, b], i) => { rwSeg(b, a, 0, 1.0); rwSeg(b, a, 2.6, H); if (i < WIN.length - 1) rwSeg(WIN[i + 1][0], b, 0, H); });
  rwSeg(-15.4, -10.2, 0, H); rwSeg(-16.6, -15.4, 2.3, H); rwSeg(ZB, -16.6, 0, H);
  for (const [a, b] of WIN) { const fr = add(ink(new THREE.BoxGeometry(0.12, 0.08, a - b), toon('#e8e8e8'), 0.4)); fr.position.set(HW, 1.8, (a + b) / 2); const g = add(new THREE.Mesh(new THREE.PlaneGeometry(a - b, 1.6), new THREE.MeshBasicMaterial({ color: '#a8c0e0', transparent: true, opacity: 0.1, depthWrite: false, side: THREE.DoubleSide }))); g.position.set(HW + 0.05, 1.8, (a + b) / 2); g.rotation.y = Math.PI / 2; }
  // Draußen vor den Fenstern: Schulhof, Bäume, Turnhalle
  const yard = add(new THREE.Mesh(new THREE.PlaneGeometry(60, 60), toon('#3a3e44'))); yard.rotation.x = -Math.PI / 2; yard.position.set(32, -0.01, -5);
  for (let i = 0; i < 8; i++) { const t = add(ink(new THREE.IcosahedronGeometry(1.6 + r(), 0), toon('#2a3a2e'), 0.6)); t.position.set(9 + r() * 14, 3 + r(), -12 + r() * 22); const tr = add(ink(new THREE.CylinderGeometry(0.15, 0.2, 3, 6), toon('#3a2a22'), 0.4)); tr.position.set(t.position.x, 1.5, t.position.z); }
  add(edges(ink(new THREE.BoxGeometry(12, 7, 20), toon('#9a8a7a'), 0.7))).position.set(30, 3.5, -6);
  // Stirnwände: hinten Doppeltür mit Notausgang, vorne Treppenhaustür
  for (const [z, ry] of [[ZB, 0], [ZA, Math.PI]]) { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(2 * HW, H), wallM)); m.position.set(0, H / 2, z); m.rotation.y = ry; }
  for (const x of [-0.6, 0.6]) { const d = add(ink(new THREE.BoxGeometry(1.15, 2.3, 0.08), toon('#5a7a9a'), 0.5)); d.position.set(x, 1.15, ZB + 0.05); const w = add(new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.9), new THREE.MeshBasicMaterial({ color: '#1a2030' }))); w.position.set(x, 1.6, ZB + 0.1); const bar = add(ink(new THREE.BoxGeometry(0.9, 0.06, 0.08), toon('#c8c8c8'), 0.3)); bar.position.set(x, 1.0, ZB + 0.13); }
  const exitTex = canvasTex(256, 96, (c, w, h) => { c.fillStyle = '#1a9a4a'; c.fillRect(0, 0, w, h); c.fillStyle = '#fff'; c.font = '900 34px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('NOTAUSGANG', w / 2 + 18, h / 2); c.fillRect(20, 30, 20, 40); });
  const exitS = add(new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.3, 0.06), new THREE.MeshBasicMaterial({ map: exitTex }))); exitS.position.set(0, 2.6, ZB + 0.06); add(glow('#30ff80', 1.6, 0.35)).position.set(0, 2.6, ZB + 0.3);
  const banner = plane(4.2, 0.35, canvasTex(1024, 84, (c, w, h) => { c.fillStyle = '#2a4a7a'; c.fillRect(0, 0, w, h); c.fillStyle = '#ffd84a'; c.font = '900 44px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('WILLKOMMEN AN DER GESAMTSCHULE NORD', w / 2, h / 2 + 2); }), 0, 3.0, ZB + 0.04, 0);
  // Wanduhr über der Tür
  const clkC = document.createElement('canvas'); clkC.width = clkC.height = 128; const clkT = new THREE.CanvasTexture(clkC); clkT.colorSpace = THREE.SRGBColorSpace;
  const clk = add(new THREE.Mesh(new THREE.CircleGeometry(0.28, 24), new THREE.MeshBasicMaterial({ map: clkT }))); clk.position.set(-1.6, 2.6, ZB + 0.05);
  add(ink(new THREE.CylinderGeometry(0.3, 0.3, 0.05, 24), toon('#2a2a2a'), 0.4)).rotation.x = Math.PI / 2; root.children[root.children.length - 1].position.set(-1.6, 2.6, ZB + 0.02);

  // ---------- Spinde (links) ----------
  const lockers = [], vents = [], locks = [];
  const ventTex = canvasTex(64, 256, (c, w, h) => { c.fillStyle = '#ffffff'; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(0,0,0,0.35)'; for (let y = 14; y < 60; y += 8) c.fillRect(12, y, 40, 4); for (let y = 200; y < 246; y += 8) c.fillRect(12, y, 40, 4); c.strokeStyle = 'rgba(0,0,0,0.4)'; c.lineWidth = 3; c.strokeRect(2, 2, w - 4, h - 4); });
  let spindZ = -2.25, nLock = 0;
  for (let z = 8.5; z > -15; z -= 0.5) { nLock++; const col = (Math.floor((z + 20) / 3) % 2) ? '#3a6aa0' : '#2a8a8a';
    if (Math.abs((z - 0.25) - spindZ) < 0.01) continue; lockers.push({ p: [-HW + 0.25, 0.95, z - 0.25], s: [0.5, 1.9, 0.48], c: col }); locks.push({ p: [-HW + 0.51, 1.0, z - 0.42], s: [0.03, 0.08, 0.05], c: '#c8c8c8' }); }
  add(instanced(BOX, toon('#ffffff', { map: ventTex }), lockers, 0.4)); add(instanced(BOX, toon('#ffffff'), locks, 0));
  const lockTop = add(ink(new THREE.BoxGeometry(0.5, 0.1, 23.6), toon('#2a4a6a'), 0.4)); lockTop.position.set(-HW + 0.25, 1.95, -3.3);
  // Aufkleber + Nummern
  const sticker = (txt, bg, fg) => canvasTex(96, 96, (c, w, h) => { c.fillStyle = bg; c.beginPath(); c.arc(w / 2, h / 2, 44, 0, 7); c.fill(); c.fillStyle = fg; c.font = '900 22px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(txt, w / 2, h / 2 + 1); });
  [['BVB', '#f0d020', '#111'], ['★', '#e84a8a', '#fff'], ['LOL', '#3ac0e8', '#fff'], ['☮', '#7ac04a', '#fff'], ['GG', '#9a4ae8', '#fff'], ['♥', '#e83a3a', '#fff'], ['SK8', '#111', '#f0f0f0']]
    .forEach((s, i) => plane(0.16, 0.16, sticker(...s), -HW + 0.505, 1.2 + r() * 0.5, 7 - i * 3.1 - r(), Math.PI / 2, { transparent: true, alphaTest: 0.5 }));
  const numTex = canvasTex(64, 32, (c, w, h) => { c.fillStyle = '#e8e8e0'; c.fillRect(0, 0, w, h); c.fillStyle = '#111'; c.font = '900 22px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('47', w / 2, h / 2 + 1); });
  // Spind 47 mit Tür, die aufschwingt
  const sp = add(new THREE.Group()); sp.position.set(-HW + 0.5, 0, spindZ - 0.25);
  const spBody = add(ink(new THREE.BoxGeometry(0.48, 1.9, 0.48), toon('#1a1a1e', { side: THREE.BackSide }), 0)); spBody.position.set(-HW + 0.25, 0.95, spindZ - 0.25);
  const spDoor = ink(new THREE.BoxGeometry(0.03, 1.88, 0.48), toon('#ffffff', { map: ventTex, color: '#3a6aa0' }), 0.4); spDoor.position.set(0.0, 0.95, 0.24); sp.add(spDoor);
  const spNum = new THREE.Mesh(new THREE.PlaneGeometry(0.12, 0.06), toon('#ffffff', { map: numTex })); spNum.position.set(0.02, 1.75, 0.24); spNum.rotation.y = Math.PI / 2; sp.add(spNum);
  const photoIn = plane(0.18, 0.24, canvasTex(64, 84, (c, w, h) => { c.fillStyle = '#f4f1e8'; c.fillRect(0, 0, w, h); c.fillStyle = '#5a6a7a'; c.fillRect(5, 5, w - 10, h - 24); c.fillStyle = '#d8b898'; c.beginPath(); c.arc(32, 32, 11, 0, 7); c.fill(); c.fillStyle = '#c84a7a'; c.fillRect(20, 44, 24, 16); c.strokeStyle = '#d0201a'; c.lineWidth = 4; c.beginPath(); c.moveTo(8, 8); c.lineTo(56, 60); c.moveTo(56, 8); c.lineTo(8, 60); c.stroke(); c.fillStyle = '#111'; c.font = '700 10px Inter, sans-serif'; c.fillText('MIA', 22, 78); }), -HW + 0.04, 1.4, spindZ - 0.25, Math.PI / 2); photoIn.scale.set(1.6, 1.6, 1);

  // ---------- Rechte Wand: Schwarzes Brett, Pokalvitrine, Bilder, Brunnen, Feuerlöscher ----------
  const corkTex = canvasTex(512, 300, (c, w, h) => { c.fillStyle = '#b8864a'; c.fillRect(0, 0, w, h); stains(c, w, h, r, 20, '90,60,20', 0.3);
    const fly = (x, y, w2, h2, bg, lines, rot) => { c.save(); c.translate(x, y); c.rotate(rot); c.fillStyle = bg; c.fillRect(0, 0, w2, h2); c.fillStyle = '#111'; lines.forEach((l, i) => { c.font = `${i ? 600 : 900} ${i ? 14 : 20}px Inter, sans-serif`; c.fillText(l, 8, 26 + i * 20); }); c.fillStyle = '#e03a2a'; c.beginPath(); c.arc(w2 / 2, 6, 5, 0, 7); c.fill(); c.restore(); };
    fly(20, 20, 140, 110, '#ffe04a', ['SCHULPARTY!', 'Fr 20 Uhr', 'Aula · DJ Kev'], -0.05); fly(180, 30, 130, 90, '#f0f0f0', ['THEATER-AG', 'Proben Do', 'Raum 214'], 0.04);
    fly(330, 20, 160, 120, '#ffb0c8', ['VERMISST:', 'schwarzes Handy', 'bitte bei Mia 10b'], -0.03); fly(40, 160, 150, 110, '#a8e0ff', ['Mathe-Nachhilfe', '5€/Std', 'Tel. abreißen ↓'], 0.03);
    fly(220, 150, 120, 120, '#c8f0a0', ['ABI 2027', 'Mottowoche!', '#legenden'], -0.06); fly(360, 165, 130, 100, '#fff', ['Wer war das?', 'Toiletten 2. OG', '– Hausmeister'], 0.05); });
  plane(2.6, 1.5, corkTex, HW - 0.01, 1.7, 1.4, -Math.PI / 2);
  add(ink(new THREE.BoxGeometry(0.05, 1.6, 2.7), toon('#6a4a2a'), 0.4)).position.set(HW - 0.02, 1.7, 1.4);
  const caseG = add(new THREE.Group()); caseG.position.set(HW - 0.3, 0, 8.2);
  caseG.add(ink(new THREE.BoxGeometry(0.55, 2.0, 1.6), toon('#5a3a2a', { side: THREE.BackSide }), 0)).position.y = 1.0;
  for (let k = 0; k < 6; k++) { const cup = ink(new THREE.CylinderGeometry(0.08, 0.04, 0.22, 10), toon('#e8c040'), 0.3); cup.position.set(-0.05, 0.75 + Math.floor(k / 3) * 0.55, -0.5 + (k % 3) * 0.5); caseG.add(cup); const b = ink(new THREE.BoxGeometry(0.12, 0.06, 0.12), toon('#2a2a2a'), 0.2); b.position.set(-0.05, 0.62 + Math.floor(k / 3) * 0.55, -0.5 + (k % 3) * 0.5); caseG.add(b); }
  for (const y of [0.58, 1.13]) { const sh = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.03, 1.55), new THREE.MeshBasicMaterial({ color: '#c0d8e8', transparent: true, opacity: 0.4 })); sh.position.y = y; caseG.add(sh); }
  const caseGlass = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.9), new THREE.MeshBasicMaterial({ color: '#b0d0e8', transparent: true, opacity: 0.12, depthWrite: false, side: THREE.DoubleSide })); caseGlass.position.set(-0.28, 1.0, 0); caseGlass.rotation.y = Math.PI / 2; caseG.add(caseGlass);
  const art = (seed2) => canvasTex(128, 160, (c, w, h) => { const rr = rng(seed2); c.fillStyle = '#fffaf0'; c.fillRect(0, 0, w, h); for (let i = 0; i < 7; i++) { c.fillStyle = ['#e84a3a', '#3a8ae8', '#f0c020', '#4ac06a', '#a04ae8'][(rr() * 5) | 0]; c.beginPath(); c.ellipse(rr() * w, rr() * h, 10 + rr() * 30, 8 + rr() * 24, rr() * 3, 0, 7); c.fill(); } c.fillStyle = '#111'; c.font = '700 12px Inter, sans-serif'; c.fillText('Kl. 5' + 'abc'[(rr() * 3) | 0], 8, h - 8); });
  for (let i = 0; i < 4; i++) plane(0.5, 0.62, art(seed + i), HW - 0.01, 1.75, -11.0 - i * 0.65 - (i > 1 ? 0.2 : 0), -Math.PI / 2);
  const fount = add(ink(new THREE.BoxGeometry(0.35, 0.25, 0.5), toon('#c8ccd0'), 0.4)); fount.position.set(HW - 0.2, 0.95, -13.8);
  const ext = add(ink(new THREE.CylinderGeometry(0.09, 0.09, 0.55, 12), toon('#d0201a'), 0.4)); ext.position.set(-HW + 0.6, 0.3, -15.5);
  // Klassentür 10b
  const door10 = add(ink(new THREE.BoxGeometry(0.06, 2.25, 1.15), toon('#8a5a3a'), 0.5)); door10.position.set(HW + 0.05, 1.12, 5.0);
  plane(0.3, 0.16, canvasTex(96, 48, (c, w, h) => { c.fillStyle = '#e8e4d4'; c.fillRect(0, 0, w, h); c.fillStyle = '#111'; c.font = '900 26px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('10b', w / 2, h / 2 + 1); }), HW - 0.01, 2.0, 4.0, -Math.PI / 2);

  // ---------- Deckenlampen (Bewegungsmelder), Kamera, Glocke, Lautsprecher ----------
  const lamps = []; for (let z = 8; z >= -20; z -= 3) { const m = add(new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.05, 1.3), new THREE.MeshBasicMaterial({ color: '#3a3c3a' }))); m.position.set(0, H - 0.03, z); lamps.push({ m, z }); }
  const segL = [6, -2, -10, -18].map((z) => { const l = add(new THREE.PointLight('#e8f0f0', 0, 0, 1.4)); l.position.set(0, H - 0.4, z); return { l, z }; });
  const cam = add(new THREE.Group()); cam.position.set(HW - 0.3, H - 0.25, -6.2);
  const camBody = ink(new THREE.BoxGeometry(0.16, 0.14, 0.32), toon('#e8e8e8'), 0.4); cam.add(camBody); const lensM = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.04, 12), toon('#111')); lensM.rotation.x = Math.PI / 2; lensM.position.z = -0.17; cam.add(lensM);
  const camLed = new THREE.Mesh(new THREE.SphereGeometry(0.018, 6, 4), new THREE.MeshBasicMaterial({ color: '#3a0a0a' })); camLed.position.set(0.05, 0.05, -0.16); cam.add(camLed);
  const camArm = add(ink(new THREE.BoxGeometry(0.05, 0.25, 0.05), toon('#c8c8c8'), 0.3)); camArm.position.set(HW - 0.3, H - 0.12, -6.2);
  const bell = add(new THREE.Group()); bell.position.set(-HW + 0.08, 2.45, 2.4);
  const bellDome = ink(new THREE.SphereGeometry(0.16, 14, 8, 0, Math.PI * 2, 0, Math.PI / 2), toon('#c8201a'), 0.4); bellDome.rotation.z = -Math.PI / 2; bell.add(bellDome);
  const pa = add(ink(new THREE.CylinderGeometry(0.22, 0.22, 0.06, 16), toon('#e8e4dc'), 0.4)); pa.position.set(0, H - 0.03, -4.5);
  const paGrill = add(new THREE.Mesh(new THREE.CircleGeometry(0.18, 16), toon('#5a5a5a'))); paGrill.rotation.x = Math.PI / 2; paGrill.position.set(0, H - 0.065, -4.5);
  // Mondlicht-Flecken auf dem Boden (unter den Fenstern)
  const moonM = new THREE.MeshBasicMaterial({ color: '#7a9ad8', map: glowTex, transparent: true, opacity: 0.22, blending: THREE.AdditiveBlending, depthWrite: false });
  for (const [a, b] of WIN) { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(2.0, a - b), moonM)); m.rotation.x = -Math.PI / 2; m.position.set(0.6, 0.01, (a + b) / 2 - 0.3); }

  // ---------- Bio-Raum ----------
  const BX0 = HW + 0.2, BX1 = 9, BZ0 = -21, BZ1 = -12;
  const bfl = add(new THREE.Mesh(new THREE.PlaneGeometry(BX1 - BX0, BZ1 - BZ0), toon('#ffffff', { map: lino }))); bfl.rotation.x = -Math.PI / 2; bfl.position.set((BX0 + BX1) / 2, 0.002, (BZ0 + BZ1) / 2); bfl.receiveShadow = true;
  const broom = add(new THREE.Mesh(new THREE.BoxGeometry(BX1 - BX0, H, BZ1 - BZ0), toon('#ffffff', { map: paint, side: THREE.BackSide }))); broom.position.set((BX0 + BX1) / 2, H / 2, (BZ0 + BZ1) / 2); broom.receiveShadow = true;
  // Tür (offen) zum Bio-Raum
  const bioDoor = add(new THREE.Group()); bioDoor.position.set(HW + 0.1, 0, -16.6); const bd = ink(new THREE.BoxGeometry(0.06, 2.25, 1.15), toon('#8a5a3a'), 0.5); bd.position.set(0, 1.12, 0.6); bioDoor.add(bd); bioDoor.rotation.y = 1.3;
  plane(0.42, 0.16, canvasTex(128, 48, (c, w, h) => { c.fillStyle = '#e8e4d4'; c.fillRect(0, 0, w, h); c.fillStyle = '#2a7a3a'; c.font = '900 26px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('BIO 2', w / 2, h / 2 + 1); }), HW - 0.01, 2.05, -14.9, -Math.PI / 2);
  // Tafel mit Kreideschrift
  const boardC = document.createElement('canvas'); boardC.width = 1024; boardC.height = 360; const boardT = new THREE.CanvasTexture(boardC); boardT.colorSpace = THREE.SRGBColorSpace;
  const board = add(new THREE.Mesh(new THREE.PlaneGeometry(3.6, 1.26), new THREE.MeshBasicMaterial({ map: boardT, color: '#9aa69e' }))); board.position.set(5.6, 1.6, BZ0 + 0.06);
  add(ink(new THREE.BoxGeometry(3.75, 1.4, 0.05), toon('#6a4a2a'), 0.4)).position.set(5.6, 1.6, BZ0 + 0.01);
  // Poster
  const poster = (title, draw) => canvasTex(256, 340, (c, w, h) => { c.fillStyle = '#f4f0e4'; c.fillRect(0, 0, w, h); c.fillStyle = '#1a3a6a'; c.font = '900 24px Inter, sans-serif'; c.fillText(title, 14, 34); draw(c, w, h); });
  plane(0.9, 1.2, poster('PERIODENSYSTEM', (c) => { for (let y = 0; y < 7; y++) for (let x = 0; x < 9; x++) if (!(y < 2 && x > 0 && x < 8)) { c.fillStyle = ['#f0a0a0', '#a0d0f0', '#c0f0a0', '#f0e0a0'][(x + y) % 4]; c.fillRect(14 + x * 25, 60 + y * 34, 22, 30); } }), BX1 - 0.01, 1.8, -14.0, -Math.PI / 2);
  plane(0.9, 1.2, poster('DIE ZELLE', (c) => { c.fillStyle = '#c8f0c8'; c.beginPath(); c.ellipse(128, 190, 100, 120, 0, 0, 7); c.fill(); c.fillStyle = '#8a4ab0'; c.beginPath(); c.arc(128, 190, 34, 0, 7); c.fill(); c.fillStyle = '#e8a040'; for (let i = 0; i < 6; i++) { c.beginPath(); c.ellipse(70 + i * 22, 120 + (i % 2) * 140, 14, 7, i, 0, 7); c.fill(); } }), BX1 - 0.01, 1.8, -16.2, -Math.PI / 2);
  plane(0.9, 1.2, poster('DER MENSCH', (c) => { c.strokeStyle = '#c83a2a'; c.lineWidth = 6; c.beginPath(); c.arc(128, 90, 26, 0, 7); c.moveTo(128, 116); c.lineTo(128, 230); c.moveTo(80, 150); c.lineTo(176, 150); c.moveTo(128, 230); c.lineTo(96, 320); c.moveTo(128, 230); c.lineTo(160, 320); c.stroke(); }), BX0 + 0.25, 1.8, BZ1 - 0.01, Math.PI);
  // Tische + Stühle (Reihen), Mikroskope
  const desks = [], chairs = [];
  for (let row = 0; row < 3; row++) for (let col = 0; col < 2; col++) { const x = 4.0 + col * 2.6, z = -18.2 + row * 2.0; desks.push({ p: [x, 0.74, z], s: [2.0, 0.05, 0.7], c: '#c8b090' }); desks.push({ p: [x, 0.37, z + 0.2], s: [1.9, 0.7, 0.05], c: '#8a8e92' }); for (const dx of [-0.5, 0.5]) chairs.push({ p: [x + dx, 0.45, z + 0.6], s: [0.42, 0.05, 0.42], c: '#3a6ab0' }, { p: [x + dx, 0.7, z + 0.8], s: [0.42, 0.45, 0.04], c: '#3a6ab0' }); }
  add(instanced(BOX, toon('#ffffff'), desks, 0.4)); add(instanced(BOX, toon('#ffffff'), chairs, 0.3));
  for (const [x, z] of [[3.6, -18.3], [6.6, -16.3], [4.4, -14.2]]) { const g = new THREE.Group(); add(g); g.position.set(x, 0.77, z); const base = ink(new THREE.BoxGeometry(0.16, 0.03, 0.2), toon('#2a2a2a'), 0.3); g.add(base); const arm = ink(new THREE.CylinderGeometry(0.02, 0.02, 0.28, 6), toon('#2a2a2a'), 0.3); arm.position.set(0, 0.14, 0.06); g.add(arm); const tube = ink(new THREE.CylinderGeometry(0.03, 0.025, 0.16, 8), toon('#e8e8e8'), 0.3); tube.position.set(0, 0.26, 0.0); tube.rotation.x = -0.4; g.add(tube); }
  // Skelett
  const sk = add(new THREE.Group()); sk.position.set(7.6, 0, -20.0); sk.rotation.y = -0.4;
  const bone = toon('#efe8d4');
  const stand = ink(new THREE.CylinderGeometry(0.25, 0.3, 0.05, 12), toon('#3a3a3a'), 0.3); stand.position.y = 0.03; sk.add(stand);
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 1.0, 6), toon('#3a3a3a')); pole.position.y = 0.5; sk.add(pole);
  const spine = ink(new THREE.CylinderGeometry(0.03, 0.035, 0.6, 8), bone, 0.4); spine.position.y = 1.25; sk.add(spine);
  for (let i = 0; i < 6; i++) { const rib = ink(new THREE.TorusGeometry(0.12 - Math.abs(i - 2) * 0.012, 0.012, 5, 14, Math.PI * 1.6), bone, 0.3); rib.rotation.set(Math.PI / 2, 0, Math.PI * 0.7); rib.position.set(0, 1.18 + i * 0.07, 0.02); sk.add(rib); }
  const pelvis = ink(new THREE.TorusGeometry(0.1, 0.035, 6, 12), bone, 0.4); pelvis.rotation.x = Math.PI / 2; pelvis.position.y = 0.95; sk.add(pelvis);
  const skHead = new THREE.Group(); skHead.position.y = 1.72; sk.add(skHead);
  const skull = ink(new THREE.SphereGeometry(0.1, 14, 10), bone, 0.5); skull.scale.set(0.9, 1.05, 1); skHead.add(skull);
  const jaw = ink(new THREE.BoxGeometry(0.1, 0.04, 0.08), bone, 0.3); jaw.position.set(0, -0.09, 0.03); skHead.add(jaw);
  for (const s of [-1, 1]) { const eye = new THREE.Mesh(new THREE.SphereGeometry(0.027, 8, 6), new THREE.MeshBasicMaterial({ color: '#0a0a0a' })); eye.position.set(s * 0.035, 0.01, 0.085); skHead.add(eye); }
  const limb = (a, b, rad = 0.022) => { const v = new THREE.Vector3(...b).sub(new THREE.Vector3(...a)); const m = ink(new THREE.CylinderGeometry(rad, rad, v.length(), 6), bone, 0.3); m.position.set(...a).addScaledVector(v, 0.5); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.normalize()); return m; };
  for (const s of [-1, 1]) { sk.add(limb([s * 0.08, 0.93, 0], [s * 0.09, 0.5, 0.02], 0.025)); sk.add(limb([s * 0.09, 0.5, 0.02], [s * 0.09, 0.08, 0], 0.022)); }
  const skArmL = new THREE.Group(); skArmL.position.set(-0.16, 1.5, 0); sk.add(skArmL); skArmL.add(limb([0, 0, 0], [0, -0.3, 0])); skArmL.add(limb([0, -0.3, 0], [0, -0.58, 0.04], 0.018));
  const skArmR = new THREE.Group(); skArmR.position.set(0.16, 1.5, 0); sk.add(skArmR); skArmR.add(limb([0, 0, 0], [0, -0.3, 0])); skArmR.add(limb([0, -0.3, 0], [0, -0.58, 0.04], 0.018));
  // Aquarium mit Fischen und Blasen (leuchtet blau)
  const aqT = add(ink(new THREE.BoxGeometry(0.5, 0.8, 1.2), toon('#5a4a3a'), 0.4)); aqT.position.set(BX1 - 0.4, 0.4, -13.2);
  const aq = add(new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.45, 1.0), new THREE.MeshBasicMaterial({ color: '#2a8ab8', transparent: true, opacity: 0.45 }))); aq.position.set(BX1 - 0.4, 1.03, -13.2);
  const aqL = add(new THREE.PointLight('#3a9ae8', 2.5, 0, 1.6)); aqL.position.set(BX1 - 0.9, 1.2, -13.2);
  const fish = [0, 1, 2].map((i) => { const f = add(new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.04, 0.08), new THREE.MeshBasicMaterial({ color: ['#ff8a2a', '#ffd84a', '#ff4a6a'][i] }))); return f; });
  const bubbles = Array.from({ length: 10 }, (_, i) => { const b = add(new THREE.Mesh(new THREE.SphereGeometry(0.012, 6, 4), new THREE.MeshBasicMaterial({ color: '#d8f0ff' }))); return { b, ph: i / 10 }; });
  for (const [a, b] of [[-13.0, -15.0], [-17.0, -19.0]]) { const w = add(new THREE.Mesh(new THREE.PlaneGeometry(a - b, 1.5), new THREE.MeshBasicMaterial({ color: '#1a2a4a' }))); w.position.set(BX1 - 0.02, 1.8, (a + b) / 2); w.rotation.y = -Math.PI / 2; const moon = add(new THREE.Mesh(new THREE.CircleGeometry(0.12, 16), new THREE.MeshBasicMaterial({ color: '#f0f0e0' }))); moon.position.set(BX1 - 0.03, 2.2, (a + b) / 2 + 0.4); moon.rotation.y = -Math.PI / 2; }
  const bioL = add(new THREE.PointLight('#8aa0d8', 1.2, 0, 1.5)); bioL.position.set(6, 2.6, -16);

  // ---------- Ereignisse ----------
  const ev = (k) => beats.filter((b) => b.effekt?.[k] !== undefined).map((b) => ({ t0: b.t0, v: b.effekt[k] }));
  const lightEv = ev('lichter').map(({ t0, v }) => ({ t: t0 + (v.ab || 0), von: v.von ?? 9, nach: v.nach ?? -21, tempo: v.tempo || 4 }));
  const darkT = ev('dunkel').map(({ t0, v }) => t0 + (v === true ? 0 : v));
  const camT = ev('kamera').map(({ t0, v }) => t0 + (v === true ? 0 : v))[0], spindT = ev('spind').map(({ t0, v }) => t0 + (v === true ? 0 : v))[0];
  const bellT = ev('klingel').map(({ t0, v }) => t0 + (v === true ? 0 : v)), skT = ev('skelett').map(({ t0, v }) => t0 + (v === true ? 0 : v))[0];
  const chalk = ev('kreide').map(({ t0, v }) => ({ t: t0 + (v.ab || 0), d: v.dauer || 3, text: v.text || 'MIA, DU BIST DRAN.' }))[0];
  const lampOn = (z, t) => { let on = false, last = -1; for (const e of lightEv) if (t >= e.t && e.t > last) { last = e.t; } for (const d of darkT) if (t >= d && d > last) return false;
    for (const e of lightEv) { if (t < e.t) continue; const dir = Math.sign(e.nach - e.von) || -1, idx = (z - e.von) * dir; const between = idx >= -0.1 && (z - e.nach) * dir <= 0.1; if (between && (t - e.t) * e.tempo * 3 >= idx) on = true; }
    return on; };
  const lastDark = (t) => darkT.filter((d) => t >= d).pop();
  let boardKey = '';
  root.userData.update = ({ t = 0, eye, sky }) => {
    if (sky) { sky.amb.intensity *= 0.35; if (eye) { sky.sun.position.set(eye.x + 30, 32, eye.z - 6); sky.sun.target.position.set(eye.x, 0, eye.z); sky.sun.target.updateMatrixWorld(); } sky.sun.intensity *= 1.4; sky.sun.color.set('#a8c0ff'); }
    // Lampen: an, wenn ein Licht-Ereignis sie erreicht hat und danach kein "dunkel" kam
    const ld = lastDark(t);
    lamps.forEach((L) => { let on = false; for (const e of lightEv) { if (t < e.t || (ld !== undefined && ld > e.t)) continue; const dir = Math.sign(e.nach - e.von) || -1; const idx = (L.z - e.von) * dir; if (idx >= -0.1 && (L.z - e.nach) * dir <= 0.1 && (t - e.t) * e.tempo * 3 >= idx) { const k = (t - e.t) * e.tempo * 3 - idx; on = k > 0.6 || Math.sin(k * 60) > 0; } } L.on = on; L.m.material.color.set(on ? '#f0f8f4' : '#3a3c3a'); });
    segL.forEach((S2) => { const near = lamps.filter((L) => Math.abs(L.z - S2.z) < 4.1); const f = near.filter((L) => L.on).length / near.length; S2.l.intensity = 2.4 * f; });
    // Kamera folgt
    if (camT !== undefined && t >= camT && eye) { const k = Math.min(1, (t - camT) / 0.8); const dx = eye.x - cam.position.x, dz = eye.z - cam.position.z, dy = eye.y - cam.position.y; const yaw = Math.atan2(-dx, -dz), pit = Math.atan2(dy, Math.hypot(dx, dz)); cam.rotation.set(pit * k, yaw * k + (1 - k) * 0.6, 0, 'YXZ'); camLed.material.color.set(Math.floor(t * 2) % 2 ? '#ff2a1a' : '#6a0a0a'); }
    else { cam.rotation.set(-0.3, 0.6 + Math.sin(t * 0.3) * 0.4, 0, 'YXZ'); camLed.material.color.set('#3a0a0a'); }
    // Spind
    sp.rotation.y = spindT !== undefined ? ease((t - spindT) / 3.0) * 1.7 : 0;
    // Glocke
    const ringing = bellT.some((b) => t >= b && t < b + 2.6); bellDome.position.x = ringing ? Math.sin(t * 90) * 0.01 : 0;
    // Uhr: 23:58 + Zeit
    { const g = clkC.getContext('2d'); const mins = 23 * 60 + 57 + t / 30; g.fillStyle = '#f2efe6'; g.beginPath(); g.arc(64, 64, 60, 0, 7); g.fill(); g.lineWidth = 6; g.strokeStyle = '#222'; g.stroke(); g.fillStyle = '#222'; for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; g.fillRect(64 + Math.sin(a) * 47 - 2, 64 - Math.cos(a) * 47 - 5, 4, 10); }
      const hA = (mins / 60 % 12) / 12 * 6.283, mA = (mins % 60) / 60 * 6.283, sA = (t % 60) / 60 * 6.283; g.lineCap = 'round'; g.lineWidth = 7; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(hA) * 28, 64 - Math.cos(hA) * 28); g.stroke(); g.lineWidth = 4; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(mA) * 44, 64 - Math.cos(mA) * 44); g.stroke(); g.strokeStyle = '#c0201a'; g.lineWidth = 2; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(sA) * 48, 64 - Math.cos(sA) * 48); g.stroke(); clkT.needsUpdate = true; }
    // Tafel: Kreide erscheint
    { const n = chalk ? Math.max(0, Math.min(chalk.text.length, Math.floor((t - chalk.t) / chalk.d * chalk.text.length))) : 0; const k = `${n}`; if (k !== boardKey) { boardKey = k; const g = boardC.getContext('2d'); g.fillStyle = '#2a4a3a'; g.fillRect(0, 0, 1024, 360); g.fillStyle = 'rgba(255,255,255,0.08)'; for (let i = 0; i < 30; i++) g.fillRect((i * 97) % 1024, (i * 53) % 360, 120, 18);
      g.fillStyle = 'rgba(240,240,230,0.55)'; g.font = '600 28px "Comic Sans MS", Inter, sans-serif'; g.fillText('Mitose: Prophase → Metaphase → Anaphase → Telophase', 40, 50);
      g.fillStyle = '#f4f4ec'; g.font = '900 96px "Comic Sans MS", Inter, sans-serif'; g.textAlign = 'center'; g.fillText(chalk ? chalk.text.slice(0, n) : '', 512, 220); g.textAlign = 'left'; boardT.needsUpdate = true; } }
    // Skelett
    const sk2 = skT !== undefined ? ease((t - skT) / 1.4) : 0; skHead.rotation.y = sk2 * 0.9; skHead.rotation.x = sk2 * 0.15; skArmR.rotation.z = sk2 * 1.9; skArmR.rotation.x = -sk2 * 0.4;
    // Aquarium
    fish.forEach((f, i) => f.position.set(BX1 - 0.4 + Math.sin(t * 0.7 + i) * 0.1, 0.95 + i * 0.08, -13.2 + Math.sin(t * (0.5 + i * 0.2) + i * 2) * 0.4));
    bubbles.forEach(({ b, ph }) => { const k = (t * 0.5 + ph) % 1; b.position.set(BX1 - 0.4 + Math.sin(ph * 20) * 0.08, 0.82 + k * 0.42, -13.6 + ph * 0.2); });
  };
  return root;
}
