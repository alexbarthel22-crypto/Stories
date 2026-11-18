// Set "gasse": enge Altstadtgasse bei Nacht, Gewitter + Regen, Stromausfall (nur Kerzen in den Fenstern).
// Die Gasse läuft entlang Z: hinten (+Z) Einfahrt von der Straße, vorne (-Z) Ende mit Querstraße.
// Rechts (x = +2.6) die grüne Tür (z -2.2..-1.0) zu einem Hinterzimmer mit Kerzen und einer Pinnwand.
//
// Beat-Effekte (Feld "effekt"):
//   blitz: Sekunden (oder Liste)          -> Blitz + Himmel leuchtet auf
//   katze: Sekunden                       -> Katze springt von der Mülltonne und rennt weg, Deckel klappert
//   tuer_auf: Sekunden, tuer_zu: Sekunden -> grüne Tür knarrt auf / knallt zu
//   hubschrauber: {ab, dauer, von, nach}  -> Hubschrauber mit Suchscheinwerfer über den Dächern
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, cracks, rng } from '../toon.js';
import { car, heli } from './aussicht.js';

export const info = {
  start: [-0.4, 0.0],
  spots: {
    gasse: [0, -4], ende: [0, 0], einfahrt: [180, -6], tuer: [-47, -3], links: [90, -6], rechts: [-90, -6],
    tonnen: [20, -7], himmel: [8, 55], fenster: [62, 22], boden: [0, -60], zimmer: [-90, -4], pinnwand: [-90, 2],
  },
};

const W = 2.6; // halbe Gassenbreite
const PAL_WALL = ['#d9c7a5', '#c7a98c', '#b9c2b0', '#d8b79a', '#a9b4bf', '#cfae86', '#c49a86', '#e0d2b4'];
const PAL_SHUT = ['#4f7a5a', '#6a7f96', '#7a4f3a', '#8a8a5a', '#5a6a7a', '#9a5a4a'];
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
const BOX = new THREE.BoxGeometry(1, 1, 1);

function instanced(geo, mat, items, inkW = 0.6) {
  if (!items.length) return null;
  const m = inkW ? inkInstanced(geo, mat, items.length, inkW) : new THREE.InstancedMesh(geo, mat, items.length);
  items.forEach((it, i) => {
    E.set(it.rx || 0, it.ry || 0, it.rz || 0); Q.setFromEuler(E);
    m.setMatrixAt(i, M4.compose(P.set(...it.p), Q, S.set(...(it.s || [1, 1, 1]))));
    if (it.c) m.setColorAt(i, C.set(it.c));
  });
  m.castShadow = true; m.receiveShadow = true; return m;
}

export function build(scene, seed = 11, ctx = {}) {
  const beats = ctx.beats || [];
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o) => (root.add(o), o);
  scene.fog = new THREE.Fog('#1a1f36', 14, 75);
  const L = { frame: [], glass: [], lit: [], bar: [], shutter: [], sill: [], box: [], plant: [], slab: [], rail: [], ac: [], door: [], step: [], pipe: [], plate: [] };
  // Fassaden-Element: side -1 links, +1 rechts; out = Abstand von der Wand in die Gasse; s = [Breite, Höhe, Tiefe]
  const put = (list, side, z, y, out, s, c, extra = {}) => list.push({ p: [side * (W - out), y, z], ry: side < 0 ? Math.PI / 2 : -Math.PI / 2, s, c, ...extra });

  const glowTex = canvasTex(64, 128, (c, w, h) => { const g = c.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.save(); c.scale(1, h / w); c.fillRect(0, 0, w, w); c.restore(); });
  // ---------- Boden: nasses Kopfsteinpflaster ----------
  const cobble = canvasTex(512, 512, (c, w, h) => {
    c.fillStyle = '#2c3146'; c.fillRect(0, 0, w, h);
    const sh = ['#4f5873', '#48506a', '#56607d', '#434a63', '#5a5f78', '#4b5470'];
    for (let y = 0, row = 0; y < h; y += 32, row++) for (let x = -(row % 2) * 16; x < w; x += 32) {
      const sw = 26 + r() * 4, shh = 25 + r() * 4;
      c.fillStyle = sh[(r() * sh.length) | 0]; c.beginPath(); c.roundRect(x + 3, y + 3, sw, shh, 9); c.fill();
      c.fillStyle = 'rgba(160,175,220,0.28)'; c.beginPath(); c.ellipse(x + 12, y + 10, 7, 3.5, -0.3, 0, 7); c.fill();
      if (r() < 0.25) { c.fillStyle = 'rgba(255,190,120,0.18)'; c.beginPath(); c.ellipse(x + 18, y + 16, 5, 2, 0, 0, 7); c.fill(); }
    }
    stains(c, w, h, r, 14, '15,18,30', 0.35);
  }, { repeat: [3, 25] });
  const ground = add(new THREE.Mesh(new THREE.PlaneGeometry(2 * W, 44), toon('#ffffff', { map: cobble })));
  ground.rotation.x = -Math.PI / 2; ground.position.set(0, 0, -8); ground.receiveShadow = true;
  // Rinne in der Mitte mit Gullys
  const gut = add(new THREE.Mesh(new THREE.PlaneGeometry(0.35, 44), toon('#262a3a'))); gut.rotation.x = -Math.PI / 2; gut.position.set(0.5, 0.004, -8); gut.receiveShadow = true;
  const grateTex = canvasTex(64, 64, (c, w, h) => { c.fillStyle = '#16181f'; c.fillRect(0, 0, w, h); c.fillStyle = '#4a4f60'; for (let i = 4; i < w; i += 10) c.fillRect(i, 4, 4, h - 8); });
  for (const z of [4, -12, -24]) { const g = add(ink(new THREE.BoxGeometry(0.5, 0.02, 0.7), toon('#ffffff', { map: grateTex }), 0.4)); g.position.set(0.5, 0.01, z); }
  // Straßen (Einfahrt hinten, Querstraße vorne)
  const asph = canvasTex(512, 256, (c, w, h) => { c.fillStyle = '#2b2f3e'; c.fillRect(0, 0, w, h); stains(c, w, h, r, 20, '10,12,20', 0.4); c.strokeStyle = 'rgba(10,10,15,0.6)'; c.lineWidth = 2; cracks(c, w, h, r, 6, 2); c.fillStyle = 'rgba(220,220,200,0.6)'; for (let x = 0; x < w; x += 80) c.fillRect(x, h * 0.48, 44, 6); }, { repeat: [6, 1] });
  for (const z of [18.5, -34]) { const s = add(new THREE.Mesh(new THREE.PlaneGeometry(80, 8), toon('#ffffff', { map: asph }))); s.rotation.x = -Math.PI / 2; s.position.set(0, -0.02, z); s.receiveShadow = true; }
  for (const z of [14.2, 22.8, -29.8, -38.2]) add(edges(ink(new THREE.BoxGeometry(80, 0.14, 0.3, 80), toon('#7a7f90'), 0.5))).position.set(0, 0.0, z);
  const walkG = new THREE.PlaneGeometry(80, 6); for (const z of [26, -41]) { const s = add(new THREE.Mesh(walkG, toon('#ffffff', { map: cobble }))); s.rotation.x = -Math.PI / 2; s.position.set(0, 0.01, z); }
  // Pfützen (spiegeln den Himmel)
  const pudMat = new THREE.MeshBasicMaterial({ color: '#3a4470' }), pudHi = new THREE.MeshBasicMaterial({ color: '#7c86b8', transparent: true, opacity: 0.55 });
  const puddles = [[-1.3, -2.6, 1.0, 0.6], [1.4, 1.8, 0.8, 0.45], [-0.6, -7.5, 1.3, 0.7], [1.2, -10.4, 0.9, 0.5], [-1.5, -15, 1.1, 0.6], [0.4, -19.5, 1.4, 0.55], [-0.9, 6.2, 0.9, 0.5], [0.6, 10.2, 1.2, 0.6], [-1.2, -24, 1.0, 0.5]];
  for (const [x, z, a, b] of puddles) {
    const p = add(new THREE.Mesh(new THREE.CircleGeometry(1, 24), pudMat)); p.rotation.x = -Math.PI / 2; p.scale.set(a, b, 1); p.position.set(x, 0.006, z);
    const h = add(new THREE.Mesh(new THREE.CircleGeometry(1, 16), pudHi)); h.rotation.x = -Math.PI / 2; h.scale.set(a * 0.35, b * 0.18, 1); h.position.set(x - a * 0.3, 0.008, z - b * 0.3);
  }

  // ---------- Häuser links und rechts ----------
  const plaster = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#ffffff'; c.fillRect(0, 0, w, h); stains(c, w, h, r, 18, '80,70,60', 0.22); stains(c, w, h, r, 6, '40,50,40', 0.18); c.strokeStyle = 'rgba(60,50,40,0.5)'; cracks(c, w, h, r, 4, 1.5); }, { repeat: [3, 4] });
  const streak = canvasTex(256, 512, (c, w, h) => { c.fillStyle = '#ffffff'; c.fillRect(0, 0, w, h); for (let i = 0; i < 26; i++) { const x = r() * w, len = h * (0.2 + r() * 0.6); const g = c.createLinearGradient(0, 0, 0, len); g.addColorStop(0, 'rgba(40,40,50,0.35)'); g.addColorStop(1, 'rgba(40,40,50,0)'); c.fillStyle = g; c.fillRect(x, 0, 3 + r() * 8, len); } stains(c, w, h, r, 10, '70,60,50', 0.2); }, { repeat: [2, 1] });
  const slats = canvasTex(64, 128, (c, w, h) => { c.fillStyle = '#ffffff'; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(0,0,0,0.28)'; for (let y = 4; y < h; y += 9) c.fillRect(2, y, w - 4, 3); c.strokeStyle = 'rgba(0,0,0,0.4)'; c.lineWidth = 3; c.strokeRect(1, 1, w - 2, h - 2); });
  const litWins = [], downpipes = [], ledges = [];
  const room = { z0: -6, z1: 2 }; // Gebäude mit der grünen Tür (rechts) wird separat gebaut
  for (const side of [-1, 1]) {
    let z = 14.0;
    while (z > -30) {
      let len = 5 + r() * 3.5; if (z - len < -30) len = z + 30;
      const z0 = z - len, z1 = z;
      if (side > 0 && z1 > room.z0 && z0 < room.z1) { // Lücke für das Türhaus
        if (z1 > room.z1) { buildHouse(side, room.z1, z1); } z = room.z0; continue;
      }
      buildHouse(side, z0, z1); z = z0;
    }
  }
  function buildHouse(side, z0, z1) {
    const len = z1 - z0, h = 10 + r() * 5.5, col = PAL_WALL[(r() * PAL_WALL.length) | 0], zc = (z0 + z1) / 2;
    const m = add(edges(ink(new THREE.BoxGeometry(9, h, len - 0.04), toon(col, { map: plaster, noCache: true }), 0.8)));
    m.position.set(side * (W + 4.5), h / 2, zc);
    const streaks = add(new THREE.Mesh(new THREE.PlaneGeometry(len - 0.1, h * 0.6), toon(col, { map: streak, transparent: true, opacity: 0.6, noCache: true })));
    streaks.position.set(side * (W - 0.005), h * 0.7, zc); streaks.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
    // Sockel, Gesims, Dachtraufe, Regenrinne
    put(L.box, side, zc, 0.5, 0.05, [len, 1.0, 0.12], '#6f6a66');
    put(L.box, side, zc, h - 0.05, 0.16, [len, 0.32, 0.36], '#8a8078');
    put(L.box, side, zc, 3.05, 0.06, [len, 0.14, 0.14], '#9a9088');
    const eave = add(edges(ink(new THREE.BoxGeometry(1.4, 0.12, len + 0.04), toon('#5c3a32'), 0.7))); eave.position.set(side * (W - 0.15) + side * 0.25, h + 0.35, zc); eave.rotation.z = side * 0.5;
    const gutter = add(ink(new THREE.CylinderGeometry(0.075, 0.075, len, 8), toon('#6d6a70'), 0.6)); gutter.rotation.x = Math.PI / 2; gutter.position.set(side * (W - 0.55), h + 0.05, zc);
    const pz = z0 + 0.35 + r() * 0.2;
    L.pipe.push({ p: [side * (W - 0.13), (h + 0.35) / 2, pz], s: [1, h - 0.35, 1] });
    L.pipe.push({ p: [side * (W - 0.25), 0.33, pz], rz: Math.PI / 2, s: [1, 0.28, 1] });
    downpipes.push([side * (W - 0.4), 0.3, pz]);
    // Fenster
    const n = Math.max(1, Math.floor((len - 1.2) / 2.3)), step = len / n;
    for (let fl = 0; fl < 5; fl++) {
      const y = fl === 0 ? 1.4 : 1.1 + fl * 3.0 + 0.4; if (y > h - 1.6) break;
      for (let i = 0; i < n; i++) {
        const z = z0 + step * (i + 0.5);
        if (fl === 0) { // Erdgeschoss: Haustür oder vergittertes Fenster
          if (i % 2 === 0) { put(L.door, side, z, 1.12, 0.02, [1.05, 2.24, 0.1], ['#4a3424', '#3a4a5a', '#5a2a24', '#2a4a3a'][(r() * 4) | 0]); put(L.step, side, z, 0.08, 0.25, [1.3, 0.16, 0.5], '#8a8580'); put(L.plate, side, z + 0.7, 1.6, 0.02, [0.16, 0.12, 0.02], '#2a4a8a'); put(L.frame, side, z, 2.35, 0.05, [1.2, 0.1, 0.12], '#d8d0c0'); }
          else { put(L.frame, side, z, 1.5, 0.04, [1.1, 1.2, 0.1], '#d8d0c0'); put(L.glass, side, z, 1.5, 0.06, [0.9, 1.0, 0.04], '#141a2a'); for (let k = -2; k <= 2; k++) put(L.bar, side, z + k * 0.18, 1.5, 0.12, [0.03, 1.1, 0.03], '#1a1a1c'); }
          continue;
        }
        const balc = fl === 2 && r() < 0.35, lit = r() < 0.2, wh = balc ? 2.1 : 1.5, wy = balc ? y - 0.3 : y;
        put(L.frame, side, z, wy, 0.04, [1.15, wh + 0.1, 0.1], '#e5ddcc');
        if (lit) { const k = L.lit.length; put(L.lit, side, z, wy, 0.0, [0.95, wh - 0.1, 0.04], '#ffb45a'); litWins.push({ k, ph: r() * 10, p: [side * (W - 0.1), wy, z] }); }
        else put(L.glass, side, z, wy, 0.05, [0.95, wh - 0.1, 0.04], r() < 0.5 ? '#1b2236' : '#232a40');
        put(L.bar, side, z, wy, 0.085, [0.05, wh - 0.1, 0.05], '#e5ddcc'); put(L.bar, side, z, wy + 0.15, 0.085, [0.95, 0.05, 0.05], '#e5ddcc');
        const closed = !lit && r() < 0.3, sc = PAL_SHUT[(r() * PAL_SHUT.length) | 0];
        for (const s2 of [-1, 1]) put(L.shutter, side, z + s2 * (closed ? 0.25 : 0.8) * (side < 0 ? -1 : 1), wy, closed ? 0.11 : 0.06, [0.5, wh, 0.05], sc, closed ? {} : { ry: (side < 0 ? Math.PI / 2 : -Math.PI / 2) + s2 * 0.25 * side });
        if (balc) {
          put(L.slab, side, z, wy - wh / 2 - 0.05, 0.45, [1.9, 0.12, 0.9], '#9a9590');
          put(L.rail, side, z, wy - wh / 2 + 0.9, 0.86, [1.9, 0.05, 0.05], '#1d1d20');
          for (let k = 0; k <= 12; k++) put(L.rail, side, z - 0.9 + k * 0.15, wy - wh / 2 + 0.45, 0.86, [0.025, 0.85, 0.025], '#1d1d20');
          for (const s2 of [-1, 1]) put(L.rail, side, z + s2 * 0.93, wy - wh / 2 + 0.9, 0.45, [0.05, 0.05, 0.85], '#1d1d20');
          if (r() < 0.7) for (let k = 0; k < 3; k++) { put(L.box, side, z - 0.6 + k * 0.6, wy - wh / 2 + 0.17, 0.6, [0.26, 0.26, 0.26], '#b0603a'); put(L.plant, side, z - 0.6 + k * 0.6, wy - wh / 2 + 0.42, 0.6, [0.25, 0.25, 0.25], ['#4a7a3a', '#6a8a3a', '#3a6a4a', '#9a3a4a'][(r() * 4) | 0]); }
        } else {
          put(L.sill, side, z, wy - wh / 2 - 0.05, 0.12, [1.3, 0.08, 0.24], '#d0c8b8');
          if (r() < 0.3) { put(L.box, side, z, wy - wh / 2 + 0.06, 0.16, [1.0, 0.2, 0.22], '#a05a3a'); for (let k = 0; k < 4; k++) put(L.plant, side, z - 0.36 + k * 0.24, wy - wh / 2 + 0.22, 0.16, [0.18, 0.16, 0.16], ['#4a7a3a', '#6a8a3a', '#c84a6a', '#e0c04a'][(r() * 4) | 0]); }
          if (r() < 0.15) put(L.ac, side, z + 0.9 * (r() < 0.5 ? 1 : -1), wy - 0.75, 0.2, [0.8, 0.5, 0.35], '#c8cac8');
        }
        ledges.push([side * (W - 0.12), wy - wh / 2 - 0.05, z]);
      }
    }
  }

  // ---------- Das Türhaus (rechts) mit Hinterzimmer ----------
  const D0 = -2.2, D1 = -1.0, DH = 2.3, RH = 3.4, RX = 8.2, RZ0 = -4.6, RZ1 = 1.2;
  {
    const col = '#c7b28c', mat = toon(col, { map: plaster, noCache: true }), h = 13.5;
    const piece = (z0, z1, y0, y1) => { const m = add(edges(ink(new THREE.BoxGeometry(0.3, y1 - y0, z1 - z0), mat, 0.8))); m.position.set(W + 0.15, (y0 + y1) / 2, (z0 + z1) / 2); return m; };
    piece(room.z0, D0, 0, RH); piece(D1, room.z1, 0, RH); piece(D0, D1, DH, RH);
    const up = add(edges(ink(new THREE.BoxGeometry(9.4, h - RH, room.z1 - room.z0), mat, 0.8))); up.position.set(W + 4.7, RH + (h - RH) / 2, (room.z0 + room.z1) / 2);
    const back = add(ink(new THREE.BoxGeometry(3.8, RH, room.z1 - room.z0), mat, 0.6)); back.position.set(RX + 0.1 + 1.9, RH / 2, (room.z0 + room.z1) / 2);
    put(L.box, 1, (room.z0 + room.z1) / 2, 0.5, 0.05, [room.z1 - room.z0, 1.0, 0.12], '#6f6a66');
    put(L.box, 1, (room.z0 + room.z1) / 2, h - 0.05, 0.16, [room.z1 - room.z0, 0.32, 0.36], '#8a8078');
    const eave = add(edges(ink(new THREE.BoxGeometry(1.4, 0.12, room.z1 - room.z0), toon('#5c3a32'), 0.7))); eave.position.set(W + 0.1, h + 0.35, (room.z0 + room.z1) / 2); eave.rotation.z = 0.5;
    for (let fl = 1; fl < 4; fl++) for (const z of [-4.4, -1.6, 0.9]) {
      const y = 1.5 + fl * 3.0; put(L.frame, 1, z, y, 0.04, [1.15, 1.6, 0.1], '#e5ddcc'); put(L.glass, 1, z, y, 0.05, [0.95, 1.4, 0.04], '#1b2236');
      put(L.sill, 1, z, y - 0.8, 0.12, [1.3, 0.08, 0.24], '#d0c8b8');
      for (const s2 of [-1, 1]) put(L.shutter, 1, z + s2 * 0.8 * -1, y, 0.06, [0.5, 1.5, 0.05], '#4f7a5a', { ry: -Math.PI / 2 - s2 * 0.25 });
    }
    // Türrahmen, Hausnummer, Klingel
    put(L.frame, 1, (D0 + D1) / 2, DH + 0.06, 0.04, [1.4, 0.14, 0.14], '#d8d0c0');
    put(L.frame, 1, D0 - 0.06, DH / 2, 0.04, [0.12, DH, 0.14], '#d8d0c0'); put(L.frame, 1, D1 + 0.06, DH / 2, 0.04, [0.12, DH, 0.14], '#d8d0c0');
    put(L.step, 1, (D0 + D1) / 2, 0.06, 0.25, [1.4, 0.12, 0.5], '#8a8580');
    const numTex = canvasTex(64, 64, (c, w, h) => { c.fillStyle = '#1f4f8f'; c.fillRect(0, 0, w, h); c.strokeStyle = '#fff'; c.lineWidth = 4; c.strokeRect(4, 4, w - 8, h - 8); c.fillStyle = '#fff'; c.font = '900 34px Inter, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('13', w / 2, h / 2 + 2); });
    const num = add(new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.22), toon('#ffffff', { map: numTex }))); num.position.set(W - 0.02, 2.0, D1 + 0.35); num.rotation.y = -Math.PI / 2;
    put(L.plate, 1, D1 + 0.3, 1.25, 0.03, [0.08, 0.18, 0.03], '#b0a070');
  }
  // Die grüne Tür (Scharnier an z = D0, öffnet ins Zimmer)
  const doorTex = canvasTex(128, 256, (c, w, h) => {
    c.fillStyle = '#2f6b4a'; c.fillRect(0, 0, w, h); c.strokeStyle = 'rgba(0,0,0,0.45)'; c.lineWidth = 5;
    c.strokeRect(14, 16, w - 28, h * 0.4); c.strokeRect(14, h * 0.5, w - 28, h * 0.42);
    stains(c, w, h, r, 10, '200,210,190', 0.25); stains(c, w, h, r, 8, '20,30,20', 0.3);
    c.fillStyle = 'rgba(220,210,180,0.35)'; for (let i = 0; i < 9; i++) { c.beginPath(); c.ellipse(r() * w, r() * h, 3 + r() * 6, 2 + r() * 4, r() * 3, 0, 7); c.fill(); }
  });
  const hinge = add(new THREE.Group()); hinge.position.set(W + 0.15, 0, D0);
  const door = ink(new THREE.BoxGeometry(0.07, DH - 0.02, D1 - D0 - 0.04), toon('#ffffff', { map: doorTex }), 0.8); door.position.set(0, DH / 2, (D1 - D0) / 2); hinge.add(door);
  const knob = ink(new THREE.SphereGeometry(0.04, 10, 8), toon('#c9a54a'), 0.5); knob.position.set(-0.07, 1.05, D1 - D0 - 0.16); hinge.add(knob);
  const spill = add(new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.5), new THREE.MeshBasicMaterial({ color: '#ffb060', map: glowTex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }))); spill.rotation.x = -Math.PI / 2; spill.position.set(W - 1.1, 0.012, (D0 + D1) / 2);
  const underDoor = add(new THREE.Mesh(new THREE.PlaneGeometry(0.5, 1.1), new THREE.MeshBasicMaterial({ color: '#ff9a40', transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, depthWrite: false }))); underDoor.rotation.x = -Math.PI / 2; underDoor.position.set(W - 0.25, 0.011, (D0 + D1) / 2);

  // Hinterzimmer
  const wallpaper = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#7a6a52'; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(50,40,30,0.35)'; for (let y = 0; y < h; y += 32) for (let x = (y / 32) % 2 * 16; x < w; x += 32) { c.beginPath(); c.ellipse(x + 8, y + 12, 4, 8, 0, 0, 7); c.fill(); } stains(c, w, h, r, 10, '40,30,20', 0.35); }, { repeat: [3, 2] });
  const wallM = toon('#ffffff', { map: wallpaper, side: THREE.BackSide });
  const roomBox = add(new THREE.Mesh(new THREE.BoxGeometry(RX - (W + 0.3), RH - 0.01, RZ1 - RZ0), wallM)); roomBox.position.set((W + 0.3 + RX) / 2, RH / 2, (RZ0 + RZ1) / 2); roomBox.receiveShadow = true;
  const planks = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#5a3e2a'; c.fillRect(0, 0, w, h); for (let x = 0; x < w; x += 32) { c.fillStyle = r() < 0.5 ? '#4e3524' : '#654631'; c.fillRect(x + 1, 0, 30, h); c.fillStyle = 'rgba(0,0,0,0.5)'; c.fillRect(x, 0, 2, h); c.fillRect(x, r() * h, 32, 2); } stains(c, w, h, r, 8, '20,10,5', 0.35); }, { repeat: [3, 3] });
  const floor = add(new THREE.Mesh(new THREE.PlaneGeometry(RX - W - 0.3, RZ1 - RZ0), toon('#ffffff', { map: planks }))); floor.rotation.x = -Math.PI / 2; floor.position.set((W + 0.3 + RX) / 2, 0.005, (RZ0 + RZ1) / 2); floor.receiveShadow = true;
  // Pinnwand mit Fotos, Karte, roten Fäden
  const board = canvasTex(1024, 640, (c, w, h) => {
    c.fillStyle = '#a8794a'; c.fillRect(0, 0, w, h); stains(c, w, h, r, 30, '80,50,20', 0.3);
    c.fillStyle = '#e9e2cc'; c.fillRect(360, 160, 330, 250); c.strokeStyle = '#8aa0b8'; c.lineWidth = 3;
    for (let i = 0; i < 12; i++) { c.beginPath(); c.moveTo(360 + r() * 330, 160); c.lineTo(360 + r() * 330, 410); c.stroke(); c.beginPath(); c.moveTo(360, 160 + r() * 250); c.lineTo(690, 160 + r() * 250); c.stroke(); }
    c.fillStyle = '#6aa0d0'; c.fillRect(360, 300, 330, 18); c.fillStyle = '#222'; c.font = '700 22px Inter, sans-serif'; c.fillText('STADTWERKE – UMSPANNWERK NORD', 368, 186);
    const photo = (x, y, w2, h2, label, face) => {
      c.save(); c.translate(x, y); c.rotate((r() - 0.5) * 0.12);
      c.fillStyle = '#f4f1e8'; c.fillRect(0, 0, w2, h2); c.fillStyle = '#5a6470'; c.fillRect(8, 8, w2 - 16, h2 - 40);
      if (face) { c.fillStyle = '#d8b898'; c.beginPath(); c.arc(w2 / 2, h2 * 0.36, w2 * 0.17, 0, 7); c.fill(); c.fillStyle = '#3a2a20'; c.fillRect(w2 / 2 - w2 * 0.2, h2 * 0.58, w2 * 0.4, h2 * 0.2); }
      c.fillStyle = '#111'; c.font = '700 20px Inter, sans-serif'; c.textAlign = 'center'; c.fillText(label, w2 / 2, h2 - 12); c.restore();
    };
    photo(70, 60, 150, 180, 'JENS', true); photo(800, 70, 150, 180, 'TOBI', true); photo(90, 380, 150, 180, '?', true); photo(780, 380, 170, 190, 'M. KRAUSE', true);
    c.strokeStyle = '#d0201a'; c.lineWidth = 7; c.beginPath(); c.ellipse(145, 150, 90, 110, 0, 0, 7); c.stroke();
    // Zeitungsausschnitt + Uhrzeit
    c.fillStyle = '#ece6d4'; c.save(); c.translate(400, 440); c.rotate(-0.04); c.fillRect(0, 0, 270, 160); c.fillStyle = '#111'; c.font = '900 30px Inter, sans-serif'; c.fillText('STROMAUSFALL', 14, 42); c.font = '700 22px Inter, sans-serif'; c.fillText('Sabotage oder Unfall?', 14, 74); c.fillStyle = '#888'; for (let i = 0; i < 4; i++) c.fillRect(14, 92 + i * 16, 230 - r() * 60, 7); c.restore();
    c.fillStyle = '#fff59a'; c.save(); c.translate(560, 40); c.rotate(0.06); c.fillRect(0, 0, 150, 100); c.fillStyle = '#c0201a'; c.font = '900 44px Inter, sans-serif'; c.fillText('18:30', 12, 66); c.restore();
    // rote Fäden zwischen Pins
    const pins = [[145, 70], [875, 80], [165, 390], [865, 390], [520, 230], [630, 60], [530, 450]];
    c.strokeStyle = '#d0201a'; c.lineWidth = 3;
    for (const [a, b] of [[0, 4], [1, 4], [2, 4], [3, 4], [0, 5], [5, 4], [6, 4], [0, 3]]) { c.beginPath(); c.moveTo(...pins[a]); c.lineTo(...pins[b]); c.stroke(); }
    for (const [x, y] of pins) { c.fillStyle = '#e02a20'; c.beginPath(); c.arc(x, y, 9, 0, 7); c.fill(); c.fillStyle = '#ff9a90'; c.beginPath(); c.arc(x - 3, y - 3, 3, 0, 7); c.fill(); }
  });
  const pin = add(new THREE.Mesh(new THREE.PlaneGeometry(3.4, 2.1), toon('#ffffff', { map: board }))); pin.position.set(RX - 0.06, 1.75, -1.6); pin.rotation.y = -Math.PI / 2;
  const pinFrame = add(ink(new THREE.BoxGeometry(0.05, 2.2, 3.5), toon('#4a3020'), 0.6)); pinFrame.position.set(RX - 0.01, 1.75, -1.6);
  // Tisch, Stuhl, Kerzen, Papiere, Regal, Uhr, Glühbirne
  const wood = toon('#6a4a32');
  const tbl = add(edges(ink(new THREE.BoxGeometry(1.6, 0.07, 0.9), wood, 0.7))); tbl.position.set(5.7, 0.8, 0.35);
  for (const [dx, dz] of [[-0.72, -0.38], [0.72, -0.38], [-0.72, 0.38], [0.72, 0.38]]) { const l = add(ink(new THREE.BoxGeometry(0.06, 0.8, 0.06), wood, 0.6)); l.position.set(5.7 + dx, 0.4, 0.35 + dz); }
  const chair = new THREE.Group(); add(chair); chair.position.set(4.7, 0, 0.55); chair.rotation.y = 0.4;
  { const s = ink(new THREE.BoxGeometry(0.45, 0.05, 0.45), wood, 0.6); s.position.y = 0.46; chair.add(s); const b = ink(new THREE.BoxGeometry(0.45, 0.5, 0.05), wood, 0.6); b.position.set(0, 0.72, 0.2); chair.add(b); for (const [dx, dz] of [[-0.2, -0.2], [0.2, -0.2], [-0.2, 0.2], [0.2, 0.2]]) { const l = ink(new THREE.BoxGeometry(0.04, 0.46, 0.04), wood, 0.5); l.position.set(dx, 0.23, dz); chair.add(l); } }
  const paper = toon('#ece6d4');
  for (let i = 0; i < 7; i++) { const p = add(new THREE.Mesh(new THREE.BoxGeometry(0.21, 0.004, 0.29), paper)); p.position.set(5.3 + r() * 0.9, 0.837 + i * 0.003, 0.15 + r() * 0.4); p.rotation.y = (r() - 0.5) * 1.2; }
  const photoTex = canvasTex(64, 80, (c, w, h) => { c.fillStyle = '#f4f1e8'; c.fillRect(0, 0, w, h); c.fillStyle = '#7a8a9a'; c.fillRect(5, 5, w - 10, h - 22); c.fillStyle = '#d8b898'; c.beginPath(); c.arc(22, 30, 8, 0, 7); c.fill(); c.beginPath(); c.arc(44, 36, 6, 0, 7); c.fill(); });
  const fphoto = add(ink(new THREE.BoxGeometry(0.16, 0.2, 0.02), toon('#ffffff', { map: photoTex }), 0.5)); fphoto.position.set(6.25, 0.93, 0.62); fphoto.rotation.set(-0.2, -0.9, 0);
  const flames = [];
  const candleMat = toon('#efe6cf'), flameMat = new THREE.MeshBasicMaterial({ color: '#ffc04a' }), coreMat = new THREE.MeshBasicMaterial({ color: '#fff6d0' });
  const candle = (x, y, z, hh) => {
    const c = add(ink(new THREE.CylinderGeometry(0.03, 0.032, hh, 10), candleMat, 0.6)); c.position.set(x, y + hh / 2, z);
    const f = add(new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.07, 8), flameMat)); f.position.set(x, y + hh + 0.04, z);
    const k = new THREE.Mesh(new THREE.SphereGeometry(0.009, 6, 4), coreMat); k.position.y = -0.02; f.add(k); flames.push({ f, ph: r() * 10 });
  };
  candle(5.5, 0.835, 0.25, 0.18); candle(5.62, 0.835, 0.42, 0.12); candle(5.4, 0.835, 0.5, 0.24); candle(RX - 0.4, 0, RZ1 - 0.5, 0.3); candle(RX - 0.55, 0, RZ1 - 0.4, 0.2);
  const roomLight = add(new THREE.PointLight('#ffa850', 7, 0, 1.6)); roomLight.position.set(5.5, 1.25, 0.35);
  const shelf = add(edges(ink(new THREE.BoxGeometry(1.8, 1.8, 0.35), wood, 0.6))); shelf.position.set(4.3, 0.9, RZ1 - 0.2);
  const books = [];
  for (let row = 0; row < 3; row++) for (let i = 0; i < 9; i++) books.push({ p: [3.5 + i * 0.18 + r() * 0.02, 0.35 + row * 0.55, RZ1 - 0.22], s: [0.12, 0.3 + r() * 0.12, 0.24], c: ['#7a2a24', '#2a4a6a', '#4a6a3a', '#8a7a4a', '#3a3a3a', '#6a4a7a'][(r() * 6) | 0] });
  add(instanced(BOX, toon('#ffffff'), books, 0.4));
  const radio = add(edges(ink(new THREE.BoxGeometry(0.45, 0.28, 0.2), toon('#5a3a2a'), 0.6))); radio.position.set(4.6, 1.95, RZ1 - 0.2);
  const dial = add(new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.08), new THREE.MeshBasicMaterial({ color: '#ffcf6a' }))); dial.position.set(4.6, 1.98, RZ1 - 0.305); dial.rotation.y = Math.PI;
  const clockTex = canvasTex(128, 128, (c, w) => { c.fillStyle = '#efe8d8'; c.beginPath(); c.arc(64, 64, 60, 0, 7); c.fill(); c.lineWidth = 6; c.strokeStyle = '#2a2a2a'; c.stroke(); c.fillStyle = '#222'; for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; c.fillRect(64 + Math.sin(a) * 48 - 2, 64 - Math.cos(a) * 48 - 5, 4, 10); } c.save(); c.translate(64, 64); c.rotate(6.283 * 6.5 / 12); c.fillRect(-3, -30, 6, 30); c.restore(); c.save(); c.translate(64, 64); c.rotate(0); c.fillRect(-2, -44, 4, 44); c.restore(); });
  const clock = add(ink(new THREE.CylinderGeometry(0.22, 0.22, 0.05, 24), toon('#3a2a1a'), 0.6)); clock.rotation.x = Math.PI / 2; clock.position.set(5.6, 2.5, RZ0 + 0.03);
  const face = add(new THREE.Mesh(new THREE.CircleGeometry(0.2, 24), toon('#ffffff', { map: clockTex }))); face.position.set(5.6, 2.5, RZ0 + 0.06);
  const sec = add(new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.17, 0.004), new THREE.MeshBasicMaterial({ color: '#b01a14' }))); sec.geometry.translate(0, 0.07, 0); sec.position.set(5.6, 2.5, RZ0 + 0.07);
  const bulb = add(ink(new THREE.SphereGeometry(0.06, 10, 8), toon('#c8c4b0'), 0.5)); bulb.position.set(5.2, RH - 0.55, -1.6);
  const cord = add(new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.5, 4), toon('#111'))); cord.position.set(5.2, RH - 0.27, -1.6);
  const boxes = []; for (let i = 0; i < 5; i++) boxes.push({ p: [RX - 0.5 - (i % 2) * 0.1, 0.22 + Math.floor(i / 2) * 0.42, RZ0 + 0.5 + (i % 2) * 0.55], s: [0.6, 0.42, 0.5], ry: r() * 0.3, c: '#b08a5a' });
  add(instanced(BOX, toon('#ffffff'), boxes, 0.6));

  // ---------- Details in der Gasse ----------
  // Mülltonnen, Säcke, Kartons, Fahrrad, Kiste mit Flaschen, Poller
  const binM = toon('#3a5a3a');
  const bins = [[-2.1, -3.6], [-2.1, -4.5]].map(([x, z], i) => { const b = add(edges(ink(new THREE.BoxGeometry(0.75, 1.05, 0.72), i ? toon('#2f4f7a') : binM, 0.8))); b.position.set(x, 0.53, z); return b; });
  const lidPivot = add(new THREE.Group()); lidPivot.position.set(-2.45, 1.07, -3.6);
  const lid = ink(new THREE.BoxGeometry(0.8, 0.06, 0.76), binM, 0.7); lid.position.set(0.4, 0.03, 0); lidPivot.add(lid);
  const lid2 = add(ink(new THREE.BoxGeometry(0.8, 0.06, 0.76), toon('#2f4f7a'), 0.7)); lid2.position.set(-2.1, 1.08, -4.5);
  const bags = []; for (let i = 0; i < 5; i++) bags.push({ p: [-1.9 + r() * 0.4, 0.22, -5.4 - r() * 0.9], s: [0.45, 0.42, 0.45], rx: r(), ry: r() * 3, c: '#16171b' });
  add(instanced(new THREE.IcosahedronGeometry(0.6, 1), toon('#ffffff'), bags, 0.7));
  const cartons = [{ p: [2.15, 0.25, 6.0], s: [0.6, 0.5, 0.5], ry: 0.3, c: '#a8845a' }, { p: [2.2, 0.68, 6.1], s: [0.45, 0.36, 0.4], ry: -0.2, c: '#b8946a' }, { p: [-2.15, 0.2, 9.0], s: [0.5, 0.4, 0.6], ry: 0.1, c: '#9a7a50' }];
  add(instanced(BOX, toon('#ffffff'), cartons, 0.6));
  const crate = add(edges(ink(new THREE.BoxGeometry(0.4, 0.3, 0.3), toon('#c8a020'), 0.6))); crate.position.set(-2.2, 0.15, -12.4);
  const bottles = []; for (let i = 0; i < 12; i++) bottles.push({ p: [-2.35 + (i % 4) * 0.1, 0.36, -12.5 + Math.floor(i / 4) * 0.1], s: [1, 1, 1], c: '#2a5a2a' });
  add(instanced(new THREE.CylinderGeometry(0.025, 0.03, 0.16, 6), toon('#ffffff'), bottles, 0.3));
  const bike = bicycle(); bike.position.set(2.35, 0, 3.6); bike.rotation.y = Math.PI / 2 + 0.05; add(bike);
  for (const x of [-1.5, 0, 1.5]) { const p = add(ink(new THREE.CylinderGeometry(0.08, 0.1, 0.8, 10), toon('#5a5a60'), 0.6)); p.position.set(x, 0.4, 13.6); const c = add(new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.085, 0.08, 10), toon('#c84a3a'))); c.position.set(x, 0.66, 13.6); }
  // Graffiti + Plakate
  const tag = (txt, cols) => canvasTex(512, 256, (c, w, h) => {
    c.clearRect(0, 0, w, h); c.font = '900 120px Inter, "Liberation Sans", sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.lineJoin = 'round';
    c.save(); c.translate(w / 2, h / 2); c.rotate(-0.08); c.lineWidth = 26; c.strokeStyle = cols[2]; c.strokeText(txt, 0, 0); c.lineWidth = 12; c.strokeStyle = cols[1]; c.strokeText(txt, 0, 0); c.fillStyle = cols[0]; c.fillText(txt, 0, 0);
    c.fillStyle = cols[1]; for (let i = 0; i < 8; i++) c.fillRect(-150 + r() * 300, 40 + r() * 20, 4, 20 + r() * 40); c.restore();
  });
  const decal = (tex, w, h, side, z, y, op = 0.92) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), toon('#ffffff', { map: tex, transparent: true, opacity: op, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 }))); m.position.set(side * (W - 0.015), y, z); m.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2; return m; };
  decal(tag('NOX', ['#e84a8a', '#1a1a2a', '#f0f0f0']), 2.4, 1.2, -1, -9.5, 1.1);
  decal(tag('KIEZ', ['#4ad0c0', '#1a1a2a', '#f0e04a']), 2.2, 1.1, 1, -14.5, 1.0);
  decal(tag('WACH AUF', ['#f0d040', '#2a1a1a', '#d0302a']), 2.6, 1.3, -1, 4.5, 2.2, 0.85);
  const poster = (lines, bg, fg) => canvasTex(128, 180, (c, w, h) => { c.fillStyle = bg; c.fillRect(0, 0, w, h); c.fillStyle = fg; c.textAlign = 'center'; lines.forEach((l, i) => { c.font = `900 ${i ? 16 : 26}px Inter, sans-serif`; c.fillText(l, w / 2, 40 + i * 26); }); c.fillStyle = 'rgba(0,0,0,0.25)'; c.beginPath(); c.moveTo(w, h); c.lineTo(w - 40, h); c.lineTo(w, h - 50); c.fill(); });
  [[['LIVE', 'Club Kessel', 'Sa 23 Uhr'], '#d04a2a', '#fff'], [['ZIMMER', 'gesucht', '☎ 0176…'], '#f0ece0', '#222'], [['ACHTUNG', 'Bauarbeiten', 'Umspannwerk'], '#f0c020', '#111'], [['FLOHMARKT', 'Sonntag', 'Färberplatz'], '#3a7ac0', '#fff']]
    .forEach(([l, bg, fg], i) => decal(poster(l, bg, fg), 0.6, 0.85, i % 2 ? 1 : -1, -6.5 - i * 2.2 + (i % 2) * 0.8, 1.6 + (r() - 0.5) * 0.2));
  // Hängendes Schild "Café Mond"
  const signTex = canvasTex(256, 160, (c, w, h) => { c.fillStyle = '#1f2a44'; c.fillRect(0, 0, w, h); c.strokeStyle = '#d8b860'; c.lineWidth = 8; c.strokeRect(8, 8, w - 16, h - 16); c.fillStyle = '#f0d880'; c.beginPath(); c.arc(70, 80, 34, 0, 7); c.fill(); c.fillStyle = '#1f2a44'; c.beginPath(); c.arc(86, 70, 30, 0, 7); c.fill(); c.fillStyle = '#f0d880'; c.font = '900 36px Inter, sans-serif'; c.fillText('CAFÉ', 116, 72); c.fillText('MOND', 116, 112); });
  const arm = add(ink(new THREE.BoxGeometry(1.1, 0.05, 0.05), toon('#1a1a1c'), 0.5)); arm.position.set(W - 0.55, 3.75, -9.2);
  const signPivot = add(new THREE.Group()); signPivot.position.set(W - 0.75, 3.72, -9.2);
  const sign = ink(new THREE.BoxGeometry(0.75, 0.48, 0.05), toon('#ffffff', { map: signTex }), 0.6); sign.position.y = -0.3; signPivot.add(sign);
  // Wandlaternen (aus), Leitungen, Lichterkette (aus), Wäscheleinen
  const lanterns = [];
  for (const [side, z] of [[-1, 2], [1, -6.8], [-1, -12.5], [1, -19], [-1, -25]]) {
    put(L.rail, side, z, 3.6, 0.2, [0.05, 0.05, 0.4], '#1a1a1c');
    const lt = add(ink(new THREE.CylinderGeometry(0.12, 0.08, 0.32, 6), toon('#3a3a40'), 0.6)); lt.position.set(side * (W - 0.4), 3.45, z); lanterns.push(lt);
  }
  const wire = (x0, y0, z0, x1, y1, z1, sag, rad = 0.01, col = '#141416') => {
    const pts = []; for (let i = 0; i <= 10; i++) { const k = i / 10; pts.push(new THREE.Vector3(x0 + (x1 - x0) * k, y0 + (y1 - y0) * k - Math.sin(Math.PI * k) * sag, z0 + (z1 - z0) * k)); }
    const m = add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 16, rad, 4), toon(col))); m.castShadow = true; return pts;
  };
  wire(-W, 8.8, -3, W, 9.2, -5, 0.4); wire(-W, 11, -11, W, 10.5, -8, 0.5); wire(-W, 7.5, -20, W, 7.9, -21, 0.3);
  const bulbs = [];
  for (const [a, b] of [[[-W, 5.6, 1], [W, 5.4, -4]], [[W, 5.4, -4], [-W, 5.7, -9]], [[-W, 5.7, -9], [W, 5.5, -14]], [[W, 5.5, -14], [-W, 5.6, -19]]]) {
    const pts = wire(...a, ...b, 0.35, 0.008);
    pts.forEach((p, i) => { if (i % 2) bulbs.push({ p: [p.x, p.y - 0.06, p.z], s: [1, 1.3, 1], c: ['#c8b890', '#a8b8c8', '#c8a8a8', '#b8c8a8'][i % 4] }); });
  }
  add(instanced(new THREE.SphereGeometry(0.04, 6, 4), toon('#ffffff'), bulbs, 0.3));
  // Wäsche, die im Wind schaukelt
  const laundry = [];
  const cloth = (kind, col) => canvasTex(128, 128, (c, w, h) => {
    c.clearRect(0, 0, w, h); c.fillStyle = col;
    if (kind === 0) { c.beginPath(); c.moveTo(20, 6); c.lineTo(108, 6); c.lineTo(126, 40); c.lineTo(100, 48); c.lineTo(98, 124); c.lineTo(30, 124); c.lineTo(28, 48); c.lineTo(2, 40); c.closePath(); c.fill(); }
    else if (kind === 1) { c.beginPath(); c.moveTo(24, 4); c.lineTo(104, 4); c.lineTo(112, 124); c.lineTo(72, 124); c.lineTo(64, 50); c.lineTo(56, 124); c.lineTo(16, 124); c.closePath(); c.fill(); }
    else { c.fillRect(4, 4, w - 8, h - 8); c.fillStyle = 'rgba(255,255,255,0.35)'; for (let i = 10; i < h; i += 24) c.fillRect(4, i, w - 8, 8); }
    c.fillStyle = 'rgba(0,0,0,0.18)'; c.fillRect(0, 0, w, 10);
  });
  for (const [z0, z1, y] of [[-6.5, -7.2, 7.6], [-15.5, -15.0, 6.6]]) {
    const pts = wire(-W, y, z0, W, y + 0.2, z1, 0.25, 0.007, '#d8d8d8');
    for (let i = 1; i < 10; i += 1.6) {
      const k = Math.floor(i), p = pts[k], kind = (r() * 3) | 0, w = kind === 2 ? 0.9 : 0.55, h = kind === 2 ? 0.9 : 0.6;
      const piv = add(new THREE.Group()); piv.position.copy(p); piv.rotation.y = Math.atan2(z1 - z0, 2 * W) * -1;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), toon('#ffffff', { map: cloth(kind, ['#d84a4a', '#4a7ad8', '#f0f0e8', '#e8c84a', '#6ab07a', '#c87ab0'][(r() * 6) | 0]), transparent: true, alphaTest: 0.5, side: THREE.DoubleSide }));
      m.position.y = -h / 2; m.castShadow = true; piv.add(m); laundry.push({ piv, ph: r() * 6 });
    }
  }
  // Nachbarin mit Kerze im Fenster (Silhouette)
  const silTex = canvasTex(128, 160, (c, w, h) => { c.clearRect(0, 0, w, h); c.fillStyle = '#120c0a'; c.beginPath(); c.arc(64, 62, 26, 0, 7); c.fill(); c.beginPath(); c.moveTo(14, h); c.quadraticCurveTo(20, 96, 64, 92); c.quadraticCurveTo(108, 96, 114, h); c.fill(); c.beginPath(); c.ellipse(64, 46, 34, 22, 0, 3.3, 6.1); c.fill(); });
  const wl = litWins.find((w) => w.p[0] < 0 && w.p[2] < -5 && w.p[2] > -16) || litWins[0];
  let sil = null;
  if (wl) { sil = add(new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.9), new THREE.MeshBasicMaterial({ map: silTex, transparent: true, depthWrite: false }))); sil.position.set(Math.sign(wl.p[0]) * (W - 0.03), wl.p[1] - 0.25, wl.p[2]); sil.rotation.y = wl.p[0] < 0 ? Math.PI / 2 : -Math.PI / 2; }
  // warme Spiegelungen der Kerzenfenster auf dem nassen Pflaster
  const refl = [];
  const reflMat = new THREE.MeshBasicMaterial({ color: '#ff9a40', map: glowTex, transparent: true, opacity: 0.22, blending: THREE.AdditiveBlending, depthWrite: false });
  for (const w of litWins) { if (w.p[1] > 8) continue; const m = add(new THREE.Mesh(new THREE.PlaneGeometry(0.5, 2.6), reflMat.clone())); m.rotation.x = -Math.PI / 2; m.position.set(w.p[0] * 0.55, 0.009, w.p[2]); refl.push({ m, w }); }

  // instanzierte Fassadenteile hinzufügen
  add(instanced(BOX, toon('#ffffff'), L.frame, 0.5)); add(instanced(BOX, toon('#ffffff'), L.glass, 0));
  add(instanced(BOX, toon('#ffffff'), L.bar, 0)); add(instanced(BOX, toon('#ffffff', { map: slats }), L.shutter, 0.5));
  add(instanced(BOX, toon('#ffffff'), L.sill, 0.5)); add(instanced(BOX, toon('#ffffff'), L.box, 0.5));
  add(instanced(new THREE.IcosahedronGeometry(0.6, 0), toon('#ffffff'), L.plant, 0.5)); add(instanced(BOX, toon('#ffffff'), L.slab, 0.6));
  add(instanced(BOX, toon('#ffffff'), L.rail, 0)); add(instanced(BOX, toon('#ffffff'), L.ac, 0.6));
  add(instanced(BOX, toon('#ffffff'), L.door, 0.6)); add(instanced(BOX, toon('#ffffff'), L.step, 0.5)); add(instanced(BOX, toon('#ffffff'), L.plate, 0));
  add(instanced(new THREE.CylinderGeometry(0.06, 0.06, 1, 8), toon('#ffffff'), L.pipe.map((p) => ({ ...p, c: '#6d6a70' })), 0.5));
  const litMesh = add(instanced(BOX, new THREE.MeshBasicMaterial({ color: '#ffffff' }), L.lit, 0));

  // Querstraße hinten + vorne: Häuserfronten, damit die Gasse nicht ins Leere schaut
  for (const [z, dir] of [[-45, 1], [33, -1]]) {
    let x = -40;
    while (x < 40) {
      const w = 6 + r() * 5, h = 10 + r() * 7;
      const m = add(edges(ink(new THREE.BoxGeometry(w, h, 8), toon(PAL_WALL[(r() * PAL_WALL.length) | 0], { map: plaster, noCache: true }), 0.8))); m.position.set(x + w / 2, h / 2, z);
      for (let fy = 0; fy < 3; fy++) for (let fx = 0; fx < 2; fx++) {
        const lit = r() < 0.15, wz = z + dir * 4.05;
        const g = add(ink(new THREE.BoxGeometry(1.0, 1.4, 0.08), lit ? new THREE.MeshBasicMaterial({ color: '#ffb45a' }) : toon('#1b2236'), 0.4)); g.position.set(x + w * (0.3 + fx * 0.4), 3 + fy * 3, wz);
      }
      x += w;
    }
  }
  // Blöcke hinter den Gassenhäusern (sichtbar von den Straßen aus)
  for (const sx of [-1, 1]) {
    let z = 14;
    while (z > -30) { const len = Math.min(z + 30, 6 + r() * 6), h = 11 + r() * 6;
      const m = add(edges(ink(new THREE.BoxGeometry(28, h, len - 0.05), toon(PAL_WALL[(r() * PAL_WALL.length) | 0], { map: plaster, noCache: true }), 0.8))); m.position.set(sx * (11.6 + 14), h / 2, z - len / 2);
      for (let fx = 0; fx < 4; fx++) for (let fy = 0; fy < 3; fy++) if (r() < 0.8) { const lit = r() < 0.12; const g = add(new THREE.Mesh(new THREE.BoxGeometry(1.0, 1.4, 0.08), lit ? new THREE.MeshBasicMaterial({ color: '#ffb45a' }) : toon('#1b2236'))); g.position.set(sx * (12.6 + fx * 6), 3 + fy * 3, z + 0.05); }
      z -= len; }
  }
  // Auto mit Warnblinker an der Einfahrt + Pfütze, in der es orange blinkt
  const parked = add(car('#3f5a7a', r)); parked.position.set(-6.5, 0, 17.2);
  const blinkMat = new THREE.MeshBasicMaterial({ color: '#ffa020' }), blinkOff = toon('#7a5020');
  const blinkers = [];
  for (const [x, z] of [[-2.17, -0.75], [-2.17, 0.75], [2.17, -0.75], [2.17, 0.75]]) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.12, 0.2), blinkMat); b.position.set(x, 0.75, z); parked.add(b); blinkers.push(b); }
  const blinkGlow = add(new THREE.Mesh(new THREE.PlaneGeometry(6, 3.5), new THREE.MeshBasicMaterial({ color: '#ff8a10', map: glowTex, transparent: true, opacity: 0.25, blending: THREE.AdditiveBlending, depthWrite: false }))); blinkGlow.rotation.x = -Math.PI / 2; blinkGlow.position.set(-6.5, 0.01, 17.2);
  // Gullydampf
  const steam = steamFx(add, [1.7, 0.02, -8.5]);
  { const g = add(ink(new THREE.BoxGeometry(0.6, 0.02, 0.6), toon('#ffffff', { map: grateTex }), 0.4)); g.position.set(1.7, 0.012, -8.5); }
  // Wasser aus den Fallrohren
  const streams = [];
  const streamTex = canvasTex(32, 128, (c, w, h) => { c.clearRect(0, 0, w, h); for (let i = 0; i < 14; i++) { c.fillStyle = `rgba(200,215,255,${0.3 + r() * 0.5})`; c.fillRect(4 + r() * 20, r() * h, 3 + r() * 4, 10 + r() * 30); } }, { repeat: [1, 1] });
  streamTex.wrapT = THREE.RepeatWrapping;
  for (const [x, y, z] of downpipes) {
    const m = add(new THREE.Mesh(new THREE.PlaneGeometry(0.1, 0.3), new THREE.MeshBasicMaterial({ map: streamTex, transparent: true, depthWrite: false, side: THREE.DoubleSide })));
    m.position.set(x - Math.sign(x) * 0.05, y - 0.15, z); m.rotation.y = Math.PI / 2; streams.push(m);
  }
  // Regen, Spritzer, Blitz
  const rainFx = rain(add, 5200), splash = splashes(add, 1100, downpipes);
  const bolt = lightningBolt(add, r);
  // Katze auf der Mülltonne
  const cat = makeCat(); cat.position.set(-2.1, 1.11, -4.5); cat.rotation.y = 0.9; add(cat);
  // Hubschrauber
  const hb = beats.find((b) => b.effekt?.hubschrauber), animHeli = heli(add, hb ? { t0: hb.t0 + (hb.effekt.hubschrauber.ab || 0), ...hb.effekt.hubschrauber } : null);

  // ---------- Zeitpunkte aus den Beats ----------
  const flashes = [], catT = [], doorEv = [];
  for (const b of beats) {
    const e = b.effekt || {};
    if (e.blitz !== undefined) for (const a of [].concat(e.blitz)) flashes.push(b.t0 + (a === true ? 0 : a));
    if (e.katze !== undefined) catT.push(b.t0 + (e.katze === true ? 0 : e.katze));
    if (e.tuer_auf !== undefined) doorEv.push({ t: b.t0 + (e.tuer_auf === true ? 0 : e.tuer_auf), open: true });
    if (e.tuer_zu !== undefined) doorEv.push({ t: b.t0 + (e.tuer_zu === true ? 0 : e.tuer_zu), open: false });
  }
  doorEv.sort((a, b) => a.t - b.t);
  const flashAt = (t) => { let f = 0; for (const t0 of flashes) { const d = t - t0; if (d < 0 || d > 1.2) continue; f = Math.max(f, d < 0.07 ? 1 : d < 0.16 ? 0.25 : d < 0.24 ? 0.95 : 0.95 * Math.exp(-(d - 0.24) * 7)); } return f; };
  const FLASH = new THREE.Color('#a8b4ff');
  const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));

  root.userData.update = ({ t = 0, eye, sky, px = 768 }) => {
    // Blitz
    const f = flashAt(t);
    if (sky) {
      sky.amb.intensity += f * 3.2; sky.sun.intensity += f * 2.5;
      const dome = scene.getObjectByName('sky')?.children[0]; if (dome && f > 0) for (const k of ['cTop', 'cMid', 'cLow', 'cHor']) dome.material.uniforms[k].value.lerp(FLASH, f * 0.75);
      // drinnen ist es dunkler (nur Kerzenlicht)
      const inside = eye && eye.x > W + 0.25 ? 1 : 0; sky.amb.intensity *= 1 - inside * 0.4; sky.sun.intensity *= 1 - inside * 0.5;
    }
    bolt.visible = f > 0.5;
    // Regen + Spritzer
    if (eye) { rainFx.uniforms.uEye.value.copy(eye); splash.uniforms.uEye.value.copy(eye); }
    rainFx.uniforms.uT.value = t; splash.uniforms.uT.value = t; splash.uniforms.uPx.value = px; steam.uniforms.uT.value = t; steam.uniforms.uPx.value = px;
    streamTex.offset.y = (t * 2.2) % 1;
    // Kerzen flackern (Fenster, Zimmer)
    const fl = (ph) => 0.78 + 0.12 * Math.sin(t * 9.1 + ph) + 0.08 * Math.sin(t * 23.7 + ph * 2.3) + (Math.sin(t * 3.1 + ph) > 0.93 ? -0.2 : 0);
    if (litMesh) { litWins.forEach((w) => litMesh.setColorAt(w.k, C.set('#ffb04a').multiplyScalar(fl(w.ph)))); litMesh.instanceColor.needsUpdate = true; }
    refl.forEach(({ m, w }) => (m.material.opacity = 0.32 * fl(w.ph)));
    flames.forEach(({ f: fm, ph }) => { const k = fl(ph); fm.scale.set(1, 0.8 + k * 0.4, 1); fm.rotation.z = Math.sin(t * 5 + ph) * 0.12; });
    roomLight.intensity = 9 * fl(1.3);
    if (sil) { sil.position.y = wl.p[1] - 0.25 + Math.sin(t * 0.6) * 0.03; sil.position.z = wl.p[2] + Math.sin(t * 0.35) * 0.12; }
    // Wäsche + Schild im Wind
    const gust = 0.5 + 0.5 * Math.sin(t * 0.31) * Math.sin(t * 0.17 + 1);
    laundry.forEach((l) => (l.piv.rotation.x = (Math.sin(t * 2.1 + l.ph) * 0.18 + 0.12) * (0.6 + gust)));
    signPivot.rotation.x = Math.sin(t * 1.4) * 0.16 * (0.5 + gust);
    // Warnblinker
    const on = (t % 0.9) < 0.42; blinkers.forEach((b) => (b.material = on ? blinkMat : blinkOff)); blinkGlow.visible = on;
    // Uhr im Zimmer
    sec.rotation.z = -Math.floor(t) * Math.PI / 30;
    // Katze
    const ct = catT.length ? t - catT[0] : -1;
    if (ct < 0) { cat.position.set(-2.1, 1.11, -4.5); cat.rotation.y = 0.9 + Math.sin(t * 0.5) * 0.15; cat.userData.tail.rotation.z = Math.sin(t * 2.2) * 0.5; lidPivot.rotation.z = 0; }
    else {
      const j = Math.min(1, ct / 0.45); // Sprung
      const x = -2.1 + j * 1.0, y = 1.11 * (1 - j) + Math.sin(Math.PI * j) * 0.6, z = -4.5 - j * 0.6 - Math.max(0, ct - 0.45) * 7.5;
      cat.position.set(x + Math.max(0, ct - 0.45) * 0.4, Math.max(0, y), z); cat.rotation.y = Math.PI; cat.userData.legs.forEach((l, i) => (l.rotation.x = Math.sin(t * 24 + i * 1.6) * 0.8 * (ct > 0.45 ? 1 : 0)));
      cat.visible = z > -32;
      // Deckel fliegt auf, fällt wieder zu und klappert nach
      const lk = ct - 0.08; lidPivot.rotation.z = lk < 0 ? 0 : lk < 0.25 ? 1.3 * Math.sin(Math.PI / 2 * lk / 0.25) : lk < 0.6 ? 1.3 * (1 - ease((lk - 0.25) / 0.35)) : Math.abs(Math.sin((lk - 0.6) * 18)) * 0.12 * Math.exp(-(lk - 0.6) * 5);
    }
    // Tür
    let open = 0;
    { let o = 0; for (const e of doorEv) { if (t < e.t) break; if (e.open) o = ease((t - e.t) / 2.4) * 1.8; else { const prev = o; o = prev * (1 - ease((t - e.t) / 0.22)); } } open = o; }
    hinge.rotation.y = open; spill.material.opacity = Math.min(1, open / 1.5) * 0.32 * fl(2); underDoor.material.opacity = open > 0.05 ? 0 : 0.3 * fl(2);
    animHeli(t, 1);
  };
  return root;
}

// ---------- Hilfsobjekte ----------
function bicycle() {
  const g = new THREE.Group(), m = toon('#b83a2a'), tire = toon('#151515');
  for (const x of [-0.52, 0.52]) { const w = ink(new THREE.TorusGeometry(0.33, 0.03, 6, 20), tire, 0.4); w.position.set(x, 0.35, 0); g.add(w); }
  const bar = (a, b, rad = 0.02) => { const v = new THREE.Vector3(...b).sub(new THREE.Vector3(...a)); const c = ink(new THREE.CylinderGeometry(rad, rad, v.length(), 6), m, 0.4); c.position.set(...a).addScaledVector(v, 0.5); c.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.normalize()); g.add(c); };
  bar([-0.52, 0.35, 0], [-0.05, 0.35, 0]); bar([-0.05, 0.35, 0], [0.4, 0.75, 0]); bar([-0.52, 0.35, 0], [-0.15, 0.78, 0]); bar([-0.15, 0.78, 0], [0.4, 0.75, 0]); bar([-0.05, 0.35, 0], [-0.15, 0.78, 0]); bar([0.52, 0.35, 0], [0.4, 0.85, 0]);
  bar([0.4, 0.85, -0.25], [0.4, 0.85, 0.25], 0.018);
  const seat = ink(new THREE.BoxGeometry(0.22, 0.05, 0.1), toon('#1a1a1a'), 0.4); seat.position.set(-0.17, 0.83, 0); g.add(seat);
  g.rotation.z = 0.06; return g;
}
function makeCat() {
  const g = new THREE.Group(), m = toon('#141418');
  const body = ink(new THREE.CapsuleGeometry(0.09, 0.22, 4, 8), m, 0.8); body.rotation.x = Math.PI / 2; body.position.set(0, 0.17, 0); g.add(body);
  const head = ink(new THREE.SphereGeometry(0.075, 10, 8), m, 0.8); head.position.set(0, 0.28, 0.17); g.add(head);
  for (const s of [-1, 1]) {
    const ear = ink(new THREE.ConeGeometry(0.03, 0.06, 4), m, 0.5); ear.position.set(s * 0.04, 0.35, 0.16); g.add(ear);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.016, 8, 6), new THREE.MeshBasicMaterial({ color: '#d8f05a' })); eye.position.set(s * 0.03, 0.29, 0.235); g.add(eye);
    const pupil = new THREE.Mesh(new THREE.BoxGeometry(0.005, 0.02, 0.005), new THREE.MeshBasicMaterial({ color: '#000' })); pupil.position.set(s * 0.03, 0.29, 0.25); g.add(pupil);
  }
  const tail = new THREE.Group(); tail.position.set(0, 0.18, -0.17); g.add(tail);
  const tl = ink(new THREE.CapsuleGeometry(0.018, 0.22, 3, 6), m, 0.5); tl.position.y = 0.11; tl.rotation.x = -0.3; tail.add(tl);
  const legs = [[-0.05, 0.1], [0.05, 0.1], [-0.05, -0.1], [0.05, -0.1]].map(([x, z]) => { const p = new THREE.Group(); p.position.set(x, 0.12, z); g.add(p); const l = ink(new THREE.CapsuleGeometry(0.018, 0.08, 3, 6), m, 0.5); l.position.y = -0.06; p.add(l); return p; });
  g.userData = { tail, legs }; return g;
}
function rain(add, N) {
  // Regenstreifen um die Kamera herum (Gitter wird mitgeführt); nur über offenen Flächen (nicht in Häusern)
  const pos = new Float32Array(N * 6), end = new Float32Array(N * 2), sd = new Float32Array(N * 2);
  for (let i = 0; i < N; i++) { const x = Math.random(), y = Math.random(), z = Math.random(), s = Math.random(); pos.set([x, y, z, x, y, z], i * 6); end[i * 2 + 1] = 1; sd[i * 2] = sd[i * 2 + 1] = s; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aEnd', new THREE.BufferAttribute(end, 1)); g.setAttribute('aSeed', new THREE.BufferAttribute(sd, 1));
  const m = new THREE.ShaderMaterial({
    uniforms: { uT: { value: 0 }, uEye: { value: new THREE.Vector3() } }, transparent: true, depthWrite: false,
    vertexShader: `attribute float aEnd, aSeed; uniform float uT; uniform vec3 uEye; varying float vA;
      void main(){ vec3 p = position * vec3(18.0, 16.0, 18.0);
        p.y = mod(p.y - uT * (10.0 + aSeed * 4.0), 16.0) - 3.0 + 0.0;
        p.x = uEye.x + mod(p.x - uEye.x - 9.0 + uT * 0.6, 18.0) - 9.0;
        p.z = uEye.z + mod(p.z - uEye.z - 9.0, 18.0) - 9.0;
        p += aEnd * vec3(0.04, -0.5 - aSeed * 0.25, 0.0);
        float open = (abs(p.x) < 2.55 || p.z > 14.0 || p.z < -30.0) ? 1.0 : 0.0;
        if (p.x > 2.6 && p.x < 8.4 && p.z > -6.0 && p.z < 2.0) open = 0.0;
        vA = open * (0.25 + aSeed * 0.3) * (1.0 - aEnd * 0.6);
        gl_Position = projectionMatrix * viewMatrix * vec4(p, 1.0); }`,
    fragmentShader: `varying float vA; void main(){ if (vA < 0.01) discard; gl_FragColor = vec4(0.72, 0.8, 1.0, vA); }`,
  });
  const l = new THREE.LineSegments(g, m); l.frustumCulled = false; l.renderOrder = 5; add(l); return m;
}
function splashes(add, N, fixed) {
  // kleine Ringe/Spritzer auf dem Boden; ein Teil fest unter den Fallrohren
  const nf = fixed.length * 6, n = N + nf, pos = new Float32Array(n * 3), sd = new Float32Array(n), fx = new Float32Array(n);
  for (let i = 0; i < N; i++) { pos.set([Math.random(), 0.02, Math.random()], i * 3); sd[i] = Math.random(); }
  fixed.forEach((p, k) => { for (let j = 0; j < 6; j++) { const i = N + k * 6 + j; pos.set([p[0] + (Math.random() - 0.5) * 0.25, 0.02, p[2] + (Math.random() - 0.5) * 0.25], i * 3); sd[i] = Math.random(); fx[i] = 1; } });
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aSeed', new THREE.BufferAttribute(sd, 1)); g.setAttribute('aFix', new THREE.BufferAttribute(fx, 1));
  const m = new THREE.ShaderMaterial({
    uniforms: { uT: { value: 0 }, uEye: { value: new THREE.Vector3() }, uPx: { value: 768 } }, transparent: true, depthWrite: false,
    vertexShader: `attribute float aSeed, aFix; uniform float uT, uPx; uniform vec3 uEye; varying float vA; varying float vPh;
      void main(){ vec3 p = position;
        float rate = aFix > 0.5 ? 4.0 : 1.6;
        float cyc = uT * rate + aSeed * 7.0; float ph = fract(cyc); float id = floor(cyc);
        if (aFix < 0.5) { vec2 o = fract(vec2(position.x, position.z) + vec2(fract(id * 0.618), fract(id * 0.382)));
          p.x = uEye.x + o.x * 14.0 - 7.0; p.z = uEye.z + o.y * 14.0 - 7.0; }
        float open = (abs(p.x) < 2.5 || p.z > 14.2 || p.z < -29.8) ? 1.0 : 0.0;
        if (p.x > 2.6 && p.x < 8.4 && p.z > -6.0 && p.z < 2.0) open = 0.0;
        vA = open * (1.0 - ph) * (aFix > 0.5 ? 0.8 : 0.55); vPh = ph;
        vec4 mv = modelViewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv;
        gl_PointSize = max(1.0, (0.06 + ph * 0.16) * (aFix > 0.5 ? 1.6 : 1.0) * uPx / -mv.z); }`,
    fragmentShader: `varying float vA; varying float vPh; void main(){ vec2 c = (gl_PointCoord - 0.5) * vec2(1.0, 2.6); float d = length(c);
        float ring = smoothstep(0.5, 0.42, d) * smoothstep(0.22 + vPh * 0.15, 0.32 + vPh * 0.15, d);
        float a = ring * vA; if (a < 0.02) discard; gl_FragColor = vec4(0.78, 0.85, 1.0, a); }`,
  });
  const p = new THREE.Points(g, m); p.frustumCulled = false; p.renderOrder = 4; add(p); return m;
}
function steamFx(add, at) {
  const N = 46, pos = new Float32Array(N * 3), sd = new Float32Array(N);
  for (let i = 0; i < N; i++) { pos.set(at, i * 3); sd[i] = i / N; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aSeed', new THREE.BufferAttribute(sd, 1));
  const m = new THREE.ShaderMaterial({
    uniforms: { uT: { value: 0 }, uPx: { value: 768 } }, transparent: true, depthWrite: false,
    vertexShader: `attribute float aSeed; uniform float uT, uPx; varying float vA;
      void main(){ float ph = fract(uT * 0.22 + aSeed); vec3 p = position + vec3(sin(aSeed * 40.0 + uT) * 0.25 * ph + ph * 0.5, ph * 3.6, cos(aSeed * 31.0) * 0.3 * ph);
        vA = sin(3.1416 * ph) * 0.13; vec4 mv = modelViewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = (0.35 + ph * 1.2) * uPx / -mv.z; }`,
    fragmentShader: `varying float vA; void main(){ float d = length(gl_PointCoord - 0.5); float a = smoothstep(0.5, 0.0, d) * vA; if (a < 0.01) discard; gl_FragColor = vec4(0.5, 0.54, 0.68, a); }`,
  });
  const p = new THREE.Points(g, m); p.frustumCulled = false; p.renderOrder = 6; add(p); return m;
}
function lightningBolt(add, r) {
  // gezackter Blitz am Himmel über dem Gassenende
  const g = new THREE.Group(); add(g); g.visible = false;
  const mat = new THREE.MeshBasicMaterial({ color: '#eef2ff', fog: false });
  let p = new THREE.Vector3(-30, 330, -420);
  const seg = (a, b, w) => { const v = b.clone().sub(a); const m = new THREE.Mesh(new THREE.BoxGeometry(w, v.length(), w * 0.3), mat); m.position.copy(a).addScaledVector(v, 0.5); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.normalize()); g.add(m); };
  for (let i = 0; i < 12; i++) {
    const n = p.clone().add(new THREE.Vector3((r() - 0.5) * 50, -24 - r() * 10, 0)); seg(p, n, 3.2);
    if (r() < 0.35) { const b = n.clone().add(new THREE.Vector3((r() - 0.5) * 60, -30, 0)); seg(n, b, 1.6); }
    p = n;
  }
  return g;
}
