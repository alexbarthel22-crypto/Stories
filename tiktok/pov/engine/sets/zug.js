// Set "zug": im Inneren des Geisterzugs. Der Wagen steht still (x -1.35 … 1.35, z -7.5 … 7.5, Boden y = 0),
// die Welt draußen (Tunnel, Lampen, Bahnsteig am Anfang) zieht vorbei. Fahrtrichtung = -Z (vorne = Verbindungstür).
// Bahnsteig am Anfang auf der +X-Seite.
//
// Beat-Effekte (Feld "effekt"):
//   fahrt: {ab, v, dauer}      -> Zielgeschwindigkeit v (m/s) in "dauer" Sekunden erreichen (0 = Stillstand)
//   flackern: Sekunden          -> Licht flackert
//   licht_aus: Sekunden         -> Hauptlicht aus, rotes Notlicht an
//   dach: Sekunden | [..]       -> Schlag aufs Dach (Delle wird größer)
//   durchgang: Sekunden         -> Verbindungstür vorne gleitet auf
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, rng } from '../toon.js';

export const info = {
  start: [0.15, -0.4],
  spots: {
    gegenueber: [90, -6], tuer: [-90, -4], fenster: [-90, 0], vorne: [0, -2], hinten: [180, -2], decke: [0, 75], boden: [0, -60],
    durchgang: [0, 0], plan: [-90, 22],
  },
};
const HW = 1.35, L = 15, CH = 2.2;
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
const BOX = new THREE.BoxGeometry(1, 1, 1);
function instanced(geo, mat, items, inkW = 0.5) {
  const m = inkW ? inkInstanced(geo, mat, items.length, inkW) : new THREE.InstancedMesh(geo, mat, items.length);
  items.forEach((it, i) => { E.set(it.rx || 0, it.ry || 0, it.rz || 0); Q.setFromEuler(E); m.setMatrixAt(i, M4.compose(P.set(...it.p), Q, S.set(...(it.s || [1, 1, 1])))); if (it.c) m.setColorAt(i, C.set(it.c)); });
  m.castShadow = true; m.receiveShadow = true; return m;
}

export function build(scene, seed = 31, ctx = {}) {
  const beats = ctx.beats || [];
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o, parent = root) => (parent.add(o), o);
  scene.fog = new THREE.Fog('#06070a', 6, 45); scene.background = new THREE.Color('#040405');
  const glowTex = canvasTex(64, 64, (c, w) => { const g = c.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(0, 0, w, w); });

  // ---------- Fahrprofil vorberechnen ----------
  const T = (beats.length ? beats[beats.length - 1].t1 : 60) + 5, DT = 1 / 30, N = Math.ceil(T / DT) + 2;
  const evs = []; for (const b of beats) for (const e of [].concat(b.effekt?.fahrt || [])) evs.push({ t: b.t0 + (e.ab || 0), v: e.v, d: e.dauer || 3 });
  evs.sort((a, b) => a.t - b.t);
  const vel = new Float32Array(N), pos = new Float32Array(N), acc = new Float32Array(N), bottle = new Float32Array(N);
  { let v = 0, s = 0, from = 0, cur = null, bz = 1.5, bv = 0; let ei = 0;
    for (let i = 0; i < N; i++) { const t = i * DT;
      while (ei < evs.length && evs[ei].t <= t) { cur = { ...evs[ei], from: v }; ei++; }
      const nv = cur ? cur.from + (cur.v - cur.from) * ease((t - cur.t) / cur.d) : 0;
      acc[i] = (nv - v) / DT; v = nv; s += v * DT; vel[i] = v; pos[i] = s;
      bv += acc[i] * 0.55 * DT; bv *= 0.985; bz += bv * DT; if (bz < -7) { bz = -7; bv = -bv * 0.4; } if (bz > 7) { bz = 7; bv = -bv * 0.4; } bottle[i] = bz; } }
  const at = (arr, t) => arr[Math.max(0, Math.min(N - 1, Math.round(t / DT)))];

  // ---------- Wagen ----------
  const car = add(new THREE.Group());
  const yellowIn = toon('#d8cfa8'), panel = toon('#b8b4a0'), blue = toon('#2a4a8a'), steel = toon('#c8c8c8'), dark = toon('#2a2a2c');
  const floorTex = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#4a4a46'; c.fillRect(0, 0, w, h); c.fillStyle = '#3e3e3a'; for (let y = 6; y < h; y += 16) for (let x = 6 + (y % 32 ? 8 : 0); x < w; x += 16) { c.beginPath(); c.arc(x, y, 4, 0, 7); c.fill(); } stains(c, w, h, r, 14, '20,18,14', 0.4); }, { repeat: [2, 12] });
  const floor = add(new THREE.Mesh(new THREE.PlaneGeometry(2 * HW, L), toon('#ffffff', { map: floorTex })), car); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
  const ceil = add(new THREE.Mesh(new THREE.PlaneGeometry(2 * HW, L), toon('#d8d4c4')), car); ceil.rotation.x = Math.PI / 2; ceil.position.y = CH;
  const dent = add(ink(new THREE.SphereGeometry(0.5, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), toon('#c8c4b4'), 0.6), car); dent.rotation.x = Math.PI; dent.position.set(0.1, CH + 0.002, 1.2); dent.scale.set(1, 0.001, 1);
  const segs = [[-L / 2, -5.15], [-3.85, 3.85], [5.15, L / 2]];
  for (const s of [-1, 1]) {
    for (const [z0, z1] of segs) {
      const lo = add(ink(new THREE.BoxGeometry(0.1, 0.9, z1 - z0), panel, 0.6), car); lo.position.set(s * HW, 0.45, (z0 + z1) / 2);
      for (let z = z0 + 0.04; z <= z1; z += (z1 - z0) / Math.max(1, Math.round((z1 - z0) / 1.55))) { const p = add(ink(new THREE.BoxGeometry(0.12, 1.15, 0.1), yellowIn, 0.5), car); p.position.set(s * HW, 1.47, z); }
      const glass = add(new THREE.Mesh(new THREE.PlaneGeometry(z1 - z0, 1.15), new THREE.MeshBasicMaterial({ color: '#9ab4c0', transparent: true, opacity: 0.1, depthWrite: false, side: THREE.DoubleSide })), car); glass.position.set(s * (HW + 0.02), 1.47, (z0 + z1) / 2); glass.rotation.y = Math.PI / 2;
      // Sitzbänke mit Lehne
      const seat = add(ink(new THREE.BoxGeometry(0.5, 0.12, z1 - z0 - 0.2), blue, 0.5), car); seat.position.set(s * (HW - 0.32), 0.45, (z0 + z1) / 2);
      const back = add(ink(new THREE.BoxGeometry(0.1, 0.5, z1 - z0 - 0.2), blue, 0.5), car); back.position.set(s * (HW - 0.1), 0.8, (z0 + z1) / 2);
      const base = add(ink(new THREE.BoxGeometry(0.45, 0.38, z1 - z0 - 0.3), dark, 0.4), car); base.position.set(s * (HW - 0.32), 0.19, (z0 + z1) / 2);
    }
    const up = add(ink(new THREE.BoxGeometry(0.1, CH - 2.05, L), yellowIn, 0.5), car); up.position.set(s * HW, 2.05 + (CH - 2.05) / 2, 0);
    for (const dz of [-4.5, 4.5]) for (const k of [-1, 1]) { // Türen (geschlossen)
      const leaf = add(ink(new THREE.BoxGeometry(0.08, 2.0, 0.64), toon('#c8a42a'), 0.6), car); leaf.position.set(s * HW, 1.0, dz + k * 0.33);
      const w = add(new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.9), new THREE.MeshBasicMaterial({ color: '#9ab4c0', transparent: true, opacity: 0.15, depthWrite: false, side: THREE.DoubleSide })), car); w.position.set(s * (HW + 0.05), 1.35, dz + k * 0.33); w.rotation.y = Math.PI / 2;
      const frameT = add(ink(new THREE.BoxGeometry(0.1, 0.06, 0.5), dark, 0.4), car); frameT.position.set(s * (HW - 0.01), 1.82, dz + k * 0.33); const frameB = frameT.clone(); frameB.position.y = 0.88; car.add(frameB);
    }
  }
  // Stirnwände mit Fenster; vorne Verbindungstür (gleitet auf)
  for (const zs of [-1, 1]) {
    for (const x of [-0.95, 0.95]) { const w = add(ink(new THREE.BoxGeometry(0.8, CH, 0.1), panel, 0.6), car); w.position.set(x, CH / 2, zs * L / 2); }
    const top = add(ink(new THREE.BoxGeometry(1.1, 0.3, 0.1), panel, 0.5), car); top.position.set(0, CH - 0.15, zs * L / 2);
  }
  const conn = add(new THREE.Group(), car); conn.position.set(0, 0, -L / 2);
  const cdoor = ink(new THREE.BoxGeometry(1.1, 1.9, 0.06), toon('#8a8a80'), 0.6); cdoor.position.y = 0.95; conn.add(cdoor);
  const cwin = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.8), new THREE.MeshBasicMaterial({ color: '#2a3036', transparent: true, opacity: 0.35, depthWrite: false })); cwin.position.set(0, 1.35, 0.04); cdoor.add(cwin); cwin.position.y = 0.4;
  const bdoor = add(ink(new THREE.BoxGeometry(1.1, 1.9, 0.06), toon('#8a8a80'), 0.6), car); bdoor.position.set(0, 0.95, L / 2);
  // Nächster Wagen (dunkel, rotes Notlicht) hinter der Verbindungstür
  const next = add(new THREE.Mesh(new THREE.BoxGeometry(2 * HW, CH, 10), toon('#5a3a36', { side: THREE.BackSide })), car); next.position.set(0, CH / 2, -L / 2 - 5.05);
  const nextL = add(new THREE.PointLight('#ff3a2a', 3, 0, 1.4), car); nextL.position.set(0, 1.9, -L / 2 - 4);
  for (const x of [-0.9, 0.9]) { const s2 = add(ink(new THREE.BoxGeometry(0.5, 0.12, 8), blue, 0.4), car); s2.position.set(x, 0.45, -L / 2 - 5); }
  // Haltestangen, Griffe
  for (const x of [-0.85, 0.85]) { const rail = add(new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, L, 6), steel), car); rail.rotation.x = Math.PI / 2; rail.position.set(x, 2.0, 0); }
  for (const dz of [-4.5, 4.5]) for (const x of [-0.6, 0.6]) { const pole = add(new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, CH, 8), steel), car); pole.position.set(x * 0.3, CH / 2, dz + Math.sign(x) * 0.35); }
  const straps = [];
  for (const x of [-0.85, 0.85]) for (let z = -6.8; z <= 6.8; z += 0.65) { const piv = add(new THREE.Group(), car); piv.position.set(x, 2.0, z); const b = ink(new THREE.BoxGeometry(0.025, 0.24, 0.05), toon('#e8e2c8'), 0.3); b.position.y = -0.12; piv.add(b); const ring = ink(new THREE.TorusGeometry(0.06, 0.012, 6, 14), toon('#e8e2c8'), 0.3); ring.position.y = -0.3; ring.rotation.y = Math.PI / 2; piv.add(ring); straps.push({ piv, ph: r() * 6 }); }
  // Licht: Leuchtbänder + 2 Lampen; Notlicht
  const strips = []; for (const x of [-0.45, 0.45]) { const s = add(new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.03, L - 1.5), new THREE.MeshBasicMaterial({ color: '#eaffef' })), car); s.position.set(x, CH - 0.02, 0); strips.push(s); }
  const lights = [-3.5, 3.5].map((z) => { const l = add(new THREE.PointLight('#dfffe8', 3, 0, 1.3), car); l.position.set(0, 1.9, z); return l; });
  const emerg = add(new THREE.PointLight('#ff3020', 0, 0, 1.3), car); emerg.position.set(0, 1.9, 0);
  const emergBox = add(new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.08, 0.12), new THREE.MeshBasicMaterial({ color: '#5a1a14' })), car); emergBox.position.set(0, CH - 0.05, 0);
  // Liniennetz über den Türen, Werbung, Notbremse, Kratzer
  const routeTex = canvasTex(512, 96, (c, w, h) => { c.fillStyle = '#f0ece0'; c.fillRect(0, 0, w, h); c.fillStyle = '#c8302a'; c.fillRect(20, 44, w - 40, 8); c.fillStyle = '#111'; c.font = '900 20px Inter, sans-serif'; c.fillText('LINIE 0 · SONDERFAHRT', 20, 26);
    ['Färberplatz', 'Alter Markt', 'Gaswerk', 'Kanal', 'Umspannwerk Nord'].forEach((n, i) => { const x = 30 + i * 112; c.fillStyle = i === 4 ? '#c8302a' : '#fff'; c.strokeStyle = '#111'; c.lineWidth = 3; c.beginPath(); c.arc(x, 48, 9, 0, 7); c.fill(); c.stroke(); c.fillStyle = '#111'; c.font = `${i === 4 ? 900 : 600} 13px Inter, sans-serif`; c.fillText(n, x - 14, 80); }); });
  for (const dz of [-4.5, 4.5]) for (const s of [-1, 1]) { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.26), toon('#ffffff', { map: routeTex })), car); m.position.set(s * (HW - 0.06), 2.12, dz); m.rotation.y = s > 0 ? -Math.PI / 2 : Math.PI / 2; }
  const ad = (t1, t2, bg, fg) => canvasTex(256, 128, (c, w, h) => { c.fillStyle = bg; c.fillRect(0, 0, w, h); c.fillStyle = fg; c.font = '900 30px Inter, sans-serif'; c.fillText(t1, 14, 50); c.font = '600 18px Inter, sans-serif'; c.fillText(t2, 14, 86); stains(c, w, h, r, 6, '60,50,30', 0.3); });
  [['STADTWERKE', 'Wir halten das Licht an.', '#e8c020', '#111'], ['KAUFHAUS MERKUR', 'Alles unter einem Dach', '#c83a2a', '#fff'], ['FAHRSCHEIN?', 'Schwarzfahren kostet 40 DM', '#2a5a9a', '#fff']]
    .forEach((a, i) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(0.75, 0.38), toon('#ffffff', { map: ad(...a) })), car); m.position.set((i - 1) * 0.0 + (i === 1 ? 0 : 0), 1.45, i === 0 ? L / 2 - 0.06 : -L / 2 + 0.06); if (i !== 0) m.position.x = i === 1 ? -0.95 : 0.95; else m.position.x = 0.95; if (i === 0) m.rotation.y = Math.PI; });
  const brake = add(new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.18, 0.18), new THREE.MeshBasicMaterial({ color: '#d02a20' })), car); brake.position.set(HW - 0.08, 1.95, -3.6);
  const scratch = canvasTex(512, 128, (c, w, h) => { c.clearRect(0, 0, w, h); c.strokeStyle = 'rgba(255,255,255,0.55)'; c.lineWidth = 1.5; for (let i = 0; i < 9; i++) { c.beginPath(); let x = r() * w, y = r() * h; c.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (r() - 0.3) * 40; y += (r() - 0.5) * 30; c.lineTo(x, y); } c.stroke(); } c.font = '700 40px Inter, sans-serif'; c.strokeText('KRAH', 300, 80); });
  for (const s of [-1, 1]) { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(3, 0.75), new THREE.MeshBasicMaterial({ map: scratch, transparent: true, depthWrite: false })), car); m.position.set(s * (HW - 0.02), 1.5, s * 1.5); m.rotation.y = s > 0 ? -Math.PI / 2 : Math.PI / 2; }
  // Zeitung auf dem Sitz, Flasche am Boden
  const paperTex = canvasTex(128, 160, (c, w, h) => { c.fillStyle = '#e8e2cc'; c.fillRect(0, 0, w, h); c.fillStyle = '#111'; c.font = '900 16px Inter, sans-serif'; c.fillText('ABENDBLATT', 10, 22); c.font = '900 13px Inter, sans-serif'; c.fillText('Ingenieur tot –', 10, 48); c.fillText('Unfall im Werk?', 10, 64); c.fillStyle = '#888'; for (let i = 0; i < 6; i++) c.fillRect(10, 76 + i * 12, 100 - r() * 30, 5); c.fillStyle = '#6a6a6a'; c.fillRect(70, 30, 48, 34); });
  const paper = add(new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.004, 0.44), toon('#ffffff', { map: paperTex })), car); paper.position.set(0.95, 0.515, 2.4); paper.rotation.y = 0.4;
  const bottleM = add(new THREE.Group(), car); const bb = ink(new THREE.CylinderGeometry(0.035, 0.04, 0.24, 10), toon('#3a7a3a', { transparent: true, opacity: 0.85 }), 0.5); bb.rotation.x = Math.PI / 2; bottleM.add(bb); const neck = ink(new THREE.CylinderGeometry(0.014, 0.02, 0.08, 8), toon('#3a7a3a'), 0.4); neck.rotation.x = Math.PI / 2; neck.position.z = 0.15; bottleM.add(neck); bottleM.position.set(-0.3, 0.04, 1.5);

  // ---------- Welt draußen: Tunnel + Lampen + Bahnsteig ----------
  const tunTex = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#2a2a26'; c.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 32) { c.fillStyle = 'rgba(0,0,0,0.45)'; c.fillRect(0, y, w, 4); } c.fillStyle = 'rgba(80,70,50,0.5)'; for (let i = 0; i < 6; i++) c.fillRect(r() * w, 0, 3, h); stains(c, w, h, r, 16, '10,10,8', 0.5); stains(c, w, h, r, 6, '70,60,40', 0.3); }, { repeat: [6, 100] });
  const tg = new THREE.CylinderGeometry(3.2, 3.2, 400, 24, 1, true); tg.rotateX(Math.PI / 2);
  const tunnel = add(new THREE.Mesh(tg, toon('#ffffff', { map: tunTex, side: THREE.BackSide }))); tunnel.position.set(0, 0.6, 0);
  const cable = add(new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.08, 400), toon('#3a3a36'))); cable.position.set(-2.9, 1.7, 0);
  const lampN = 24, SP = 18, lampG = new THREE.BoxGeometry(0.15, 0.3, 0.4);
  const lamps = new THREE.InstancedMesh(lampG, new THREE.MeshBasicMaterial({ color: '#ffd890' }), lampN); add(lamps); lamps.frustumCulled = false;
  const lampLight = [-1, 1].map((s) => { const l = add(new THREE.PointLight('#ffcf80', 4, 0, 1.6)); l.position.set(s * 2.7, 1.6, 0); return l; });
  const station = add(new THREE.Group());
  { const tiles = canvasTex(512, 256, (c, w, h) => { c.fillStyle = '#3a3a34'; c.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 32) for (let x = (y / 32) % 2 * 16; x < w + 32; x += 64) { c.fillStyle = '#cfc6a2'; c.fillRect(x - 30, y + 2, 60, 28); } c.fillStyle = '#3a6a4a'; c.fillRect(0, h * 0.6, w, 30); stains(c, w, h, r, 20, '60,50,30', 0.4); }, { repeat: [16, 1] });
    const fl = new THREE.Mesh(new THREE.PlaneGeometry(6, 80), toon('#6a665c')); fl.rotation.x = -Math.PI / 2; fl.position.set(4.6, 0.01, 0); station.add(fl);
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(80, 4.6), toon('#ffffff', { map: tiles })); wall.position.set(7.6, 2.3, 0); wall.rotation.y = -Math.PI / 2; station.add(wall);
    const ce = new THREE.Mesh(new THREE.PlaneGeometry(6.5, 80), toon('#2a2a26')); ce.rotation.x = Math.PI / 2; ce.position.set(4.4, 4.6, 0); station.add(ce);
    for (let z = -35; z <= 35; z += 7) { const p = ink(new THREE.BoxGeometry(0.42, 4.6, 0.42), toon('#3f6a52'), 0.7); p.position.set(5.3, 2.3, z); station.add(p); }
    for (const z of [-20, 0, 20]) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.2, 0.4), new THREE.MeshBasicMaterial({ color: '#ff3a24' })); b.position.set(7.5, 3.4, z); station.add(b); const l = new THREE.PointLight('#ff4a2a', 3, 0, 1.5); l.position.set(7, 3.2, z); station.add(l); }
    const edgeY = new THREE.Mesh(new THREE.PlaneGeometry(0.25, 80), toon('#d8b42a')); edgeY.rotation.x = -Math.PI / 2; edgeY.position.set(2.0, 0.015, 0); station.add(edgeY); }

  // ---------- Ereignisse ----------
  const times = (k) => beats.flatMap((b) => (b.effekt?.[k] === undefined ? [] : [].concat(b.effekt[k]).map((v) => b.t0 + (v === true ? 0 : v))));
  const flick = beats.filter((b) => b.effekt?.flackern).map((b) => ({ t0: b.t0, t1: b.t0 + b.effekt.flackern }));
  const offT = times('licht_aus')[0], roofT = times('dach'), passT = times('durchgang')[0];

  root.userData.update = ({ t = 0, sky }) => {
    if (sky) { const off2 = offT !== undefined && t >= offT; sky.sun.intensity = 0; sky.amb.intensity *= off2 ? 0.28 : 0.38; const d = scene.getObjectByName('sky'); if (d) d.visible = false; }
    const s = at(pos, t), v = at(vel, t), a = at(acc, t);
    // Welt zieht vorbei (Zug fährt nach -Z)
    tunTex.offset.y = (s / 4) % 1; station.position.z = s; station.visible = s < 120; tunnel.visible = cable.visible = s > 46;
    for (let i = 0; i < lampN; i++) { const side = i % 2 ? 1 : -1, z = ((i * SP * 0.5 + s) % (lampN * SP * 0.5)) - lampN * SP * 0.25; M4.makeTranslation(side * 3.0, 1.6, z); lamps.setMatrixAt(i, M4); }
    lamps.instanceMatrix.needsUpdate = true;
    lampLight.forEach((l, k) => { const z = ((s + k * SP * 0.5) % SP) - SP / 2; l.position.z = z; l.intensity = s > 60 ? 4 : 0; });
    // Wagen vibriert beim Fahren, Griffe schwingen, Flasche rollt
    car.position.y = v > 0.5 ? Math.sin(t * 31) * 0.004 * Math.min(1, v / 10) : 0;
    car.rotation.z = Math.sin(t * 1.7) * 0.003 * Math.min(1, v / 10);
    straps.forEach((st) => (st.piv.rotation.x = Math.max(-0.6, Math.min(0.6, a * 0.08)) + Math.sin(t * 1.9 + st.ph) * 0.05 * Math.min(1, v / 8)));
    bottleM.position.z = at(bottle, t); bottleM.rotation.y = 0; bb.rotation.z = bottleM.position.z / 0.04;
    // Licht
    const fl = flick.some((f) => t >= f.t0 && t < f.t1), off = offT !== undefined && t >= offT;
    const on = !off && (!fl || Math.sin(t * 47) + Math.sin(t * 13) > 0.3);
    strips.forEach((m) => m.material.color.set(on ? '#eaffef' : '#3a3e3a')); lights.forEach((l) => (l.intensity = on ? 3 : 0));
    emerg.intensity = off ? 1.5 + Math.sin(t * 3) * 0.3 : 0; emergBox.material.color.set(off ? '#ff3020' : '#5a1a14');
    // Dach-Delle
    const hits = roofT.filter((x) => t >= x).length; const last = roofT.filter((x) => t >= x).pop();
    const bump = last !== undefined ? Math.exp(-(t - last) * 8) * 0.05 : 0; dent.scale.set(1, 0.001 + hits * 0.12 + bump * 2, 1);
    // Verbindungstür
    conn.position.x = passT !== undefined ? ease((t - passT) / 1.0) * 1.15 : 0;
  };
  return root;
}
