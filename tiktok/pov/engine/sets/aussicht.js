// Set "aussicht": Aussichtspunkt auf einem Hügel über einer Großstadt.
// Vorne (-Z): Mauer mit Geländer, Abhang, Häusermeer, Skyline. Hinten (+Z): Straße mit Reihenhäusern.
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, cracks, specks, rng } from '../toon.js';

export const info = {
  start: [0, -1.5],
  // benannte Blickrichtungen (Grad): yaw links positiv, pitch hoch positiv
  spots: {
    stadt: [0, -10], skyline: [-14, -4], abhang: [10, -30], strasse: [180, -6], haeuser: [175, 4],
    links: [80, -8], rechts: [-80, -8], boden: [0, -62], himmel: [0, 38],
  },
};

const flatDark = new THREE.MeshBasicMaterial({ color: '#2a2a30' });
const PAL_CITY = ['#ebe5da', '#ddd0bd', '#cdb9a2', '#f1ece3', '#bcae9f', '#d9c4aa', '#aab2b8', '#c9937a', '#e2d6c6'];
const PAL_ROOF = ['#7d5d4c', '#5f5c66', '#8c6c57', '#6e4a3e', '#9a8a7c'];
const PAL_TREE = ['#c86c3c', '#d99d3d', '#7e8c3c', '#a9472f', '#b8822f', '#6d7d3a'];
const PAL_CARS = ['#e9e6df', '#2d3a4a', '#b8b8b2', '#7a2a24', '#3f6b4a', '#d8a83a'];
const PAL_ROW = ['#e8c7a6', '#cfd8c1', '#e8d8a4', '#c69f7a', '#d8b3ae', '#a9b9c9', '#e3e0d6'];

export function build(scene, seed = 3, ctx = {}) {
  const beats = ctx.beats || [], story = ctx.story || {};
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o) => (root.add(o), o);

  // ---------- Gehweg (vorne) ----------
  const walkTex = canvasTex(1024, 1024, (c, w, h) => {
    c.fillStyle = '#d8ccb3'; c.fillRect(0, 0, w, h);
    stains(c, w, h, r, 26, '90,80,70', 0.22);
    c.strokeStyle = 'rgba(70,60,50,0.55)'; c.lineWidth = 3;
    for (let i = 0; i <= 4; i++) { c.beginPath(); c.moveTo(0, i * h / 4); c.lineTo(w, i * h / 4); c.stroke(); c.beginPath(); c.moveTo(i * w / 4, 0); c.lineTo(i * w / 4, h); c.stroke(); }
    cracks(c, w, h, r, 10, 2);
    specks(c, w, h, r, 40, ['#c9662f', '#a3452a', '#d89a3a', '#6b4a2a', '#3a3a3a']);
  }, { repeat: [20, 1] });
  const walk = add(new THREE.Mesh(new THREE.PlaneGeometry(120, 6), toon('#ffffff', { map: walkTex })));
  walk.rotation.x = -Math.PI / 2; walk.position.set(0, 0, 0.6); walk.receiveShadow = true;

  // Bordstein + Straße + gegenüberliegender Gehweg
  add(edges(ink(new THREE.BoxGeometry(120, 0.16, 0.3, 240), toon('#bdb5a6'), 0.6))).position.set(0, 0.0, 3.65);
  const roadTex = canvasTex(1024, 512, (c, w, h) => {
    c.fillStyle = '#62646b'; c.fillRect(0, 0, w, h); stains(c, w, h, r, 30, '30,30,35', 0.3);
    c.strokeStyle = 'rgba(25,25,28,0.6)'; c.lineWidth = 2; cracks(c, w, h, r, 6, 2);
    c.fillStyle = '#e7c34a'; c.fillRect(0, h * 0.49, w, h * 0.02);
  }, { repeat: [10, 1] });
  const road = add(new THREE.Mesh(new THREE.PlaneGeometry(120, 7.2), toon('#ffffff', { map: roadTex })));
  road.rotation.x = -Math.PI / 2; road.position.set(0, -0.08, 7.4); road.receiveShadow = true;
  const walk2 = add(new THREE.Mesh(new THREE.PlaneGeometry(120, 3.2), toon('#ffffff', { map: walkTex })));
  walk2.rotation.x = -Math.PI / 2; walk2.position.set(0, 0, 12.6); walk2.receiveShadow = true;
  add(edges(ink(new THREE.BoxGeometry(120, 0.16, 0.3, 240), toon('#bdb5a6'), 0.6))).position.set(0, 0, 11.05);
  // Gullydeckel
  const man = add(ink(new THREE.CylinderGeometry(0.35, 0.35, 0.02, 20), toon('#3d3c3e'), 0.5)); man.position.set(-2.5, -0.06, 6);

  // ---------- Mauer mit Geländer ----------
  const stoneTex = canvasTex(512, 128, (c, w, h) => {
    c.fillStyle = '#dcc9a3'; c.fillRect(0, 0, w, h); stains(c, w, h, r, 10, '120,95,60', 0.25);
    c.strokeStyle = 'rgba(80,60,40,0.5)'; c.lineWidth = 2;
    for (let y = 0; y < h; y += 32) { c.beginPath(); c.moveTo(0, y); c.lineTo(w, y); c.stroke(); for (let x = (y / 32) % 2 * 32; x < w; x += 64) { c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 32); c.stroke(); } }
  }, { repeat: [60, 1] });
  const wall = add(edges(ink(new THREE.BoxGeometry(120, 0.8, 0.42, 240), toon('#ffffff', { map: stoneTex }), 0.8)));
  wall.position.set(0, 0.4, -2.35);
  const cap = add(edges(ink(new THREE.BoxGeometry(120, 0.08, 0.55, 240), toon('#e8dcc2'), 0.6))); cap.position.set(0, 0.84, -2.35);
  // Eisengeländer hinter der Mauer
  // Eisenzaun an der Hangkante (Instanzen = schnell)
  const NBAR = 500, bars = new THREE.InstancedMesh(new THREE.BoxGeometry(0.025, 1.0, 0.025), toon('#1d1d20'), NBAR);
  for (let i = 0; i < NBAR; i++) bars.setMatrixAt(i, new THREE.Matrix4().makeTranslation(-63 + i * 0.25, 0.5, -2.66));
  bars.castShadow = true; add(bars);
  for (const y of [0.98]) { const rl = add(ink(new THREE.BoxGeometry(126, 0.045, 0.045, 250), toon('#1d1d20'), 0.6)); rl.position.set(0, y, -2.66); }

  // ---------- Grünstreifen + Abhang ----------
  const grass = add(new THREE.Mesh(new THREE.PlaneGeometry(120, 0.5), toon('#6c9346'))); grass.rotation.x = -Math.PI / 2; grass.position.set(0, 0.0, -2.8); grass.receiveShadow = true;
  const slopeTex = canvasTex(512, 512, (c, w, h) => { c.fillStyle = '#86813f'; c.fillRect(0, 0, w, h); stains(c, w, h, r, 40, '60,70,30', 0.35); stains(c, w, h, r, 20, '170,110,60', 0.3); }, { repeat: [12, 8] });
  const DROP = 70, RUN = 42, Z0 = -3.0, slopeLen = Math.hypot(RUN, DROP);
  const slope = add(new THREE.Mesh(new THREE.PlaneGeometry(260, slopeLen), toon('#ffffff', { map: slopeTex })));
  slope.rotation.x = -Math.PI / 2 - Math.atan2(DROP, RUN); slope.position.set(0, -DROP / 2, Z0 - RUN / 2);
  // Bäume am Abhang + im Tal
  const treeGeo = new THREE.IcosahedronGeometry(1, 0);
  const cityMat = toon('#ffffff', { noCache: true }), dimmable = [cityMat];
  const NT = 260, trees = inkInstanced(treeGeo, cityMat, NT, 0.7);
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), S = new THREE.Vector3(), Pv = new THREE.Vector3(), C = new THREE.Color();
  for (let i = 0; i < NT; i++) {
    let x, y, z, s;
    if (i < 90) { z = Z0 - 2 - r() * (RUN - 2); x = (r() - 0.5) * 200; y = -DROP * (Z0 - z) / RUN + 1; s = 1.6 + r() * 2.4; }
    else { const a = (r() - 0.5) * 2.6, d = 100 + r() * 700; x = Math.sin(a) * d; z = -Math.cos(a) * d; y = -68; s = 3 + r() * 3; }
    Q.setFromEuler(new THREE.Euler(r() * 3, r() * 3, 0)); S.set(s, s * 0.85, s); Pv.set(x, y, z);
    trees.setMatrixAt(i, M.compose(Pv, Q, S)); trees.setColorAt(i, C.set(PAL_TREE[(r() * PAL_TREE.length) | 0]));
  }
  add(trees);

  // ---------- Häusermeer ----------
  const ground = add(new THREE.Mesh(new THREE.CircleGeometry(2600, 64), toon('#c4896a'))); ground.rotation.x = -Math.PI / 2; ground.position.y = -70.2;
  const lights = [];
  const NB = 4200, box = new THREE.BoxGeometry(1, 1, 1); box.translate(0, 0.5, 0);
  const city = inkInstanced(box, cityMat, NB, 0.45);
  const roofGeo = new THREE.ConeGeometry(0.75, 1, 4, 1); roofGeo.rotateY(Math.PI / 4); roofGeo.translate(0, 0.5, 0);
  const roofs = inkInstanced(roofGeo, cityMat, NB, 0.4);
  let nb = 0, nr = 0;
  for (let i = 0; i < NB * 3 && nb < NB; i++) {
    const a = (r() - 0.5) * 3.4, d = 50 + Math.pow(r(), 0.8) * 900;
    const x = Math.sin(a) * d, z = -Math.cos(a) * d;
    if (z > -50) continue;
    if (Math.abs(z + 520) < 22 && x > -400) continue; // Fluss
    const w = 5 + r() * 9, dd = 5 + r() * 9, h = 3 + r() * 8;
    Q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), a + (r() < 0.5 ? 0 : Math.PI / 2) + (r() - 0.5) * 0.2);
    city.setMatrixAt(nb, M.compose(Pv.set(x, -70, z), Q, S.set(w, h, dd)));
    city.setColorAt(nb, C.set(PAL_CITY[(r() * PAL_CITY.length) | 0])); nb++;
    // beleuchtete Fenster (zur Kamera zeigende Seite)
    const nl = r() < 0.65 ? 1 + ((r() * 3) | 0) : 0, toO = Math.atan2(-x, -z), half = Math.max(w, dd) / 2 + 0.8 + d * 0.004;
    for (let k = 0; k < nl; k++) { const lat = (r() - 0.5) * w * 0.8; lights.push(x + Math.sin(toO) * half + Math.cos(toO) * lat, -69 + r() * h * 0.85, z + Math.cos(toO) * half - Math.sin(toO) * lat, 3.2 + r() * 2.0); }
    if (r() < 0.55) {
      roofs.setMatrixAt(nr, M.compose(Pv.set(x, -70 + h, z), Q, S.set(w, 2 + r() * 2.5, dd)));
      roofs.setColorAt(nr, C.set(PAL_ROOF[(r() * PAL_ROOF.length) | 0])); nr++;
    }
  }
  city.count = nb; city.userData.hull.count = nb; roofs.count = nr; roofs.userData.hull.count = nr;
  city.castShadow = roofs.castShadow = false; add(city); add(roofs);
  // Fluss
  const river = add(new THREE.Mesh(new THREE.PlaneGeometry(1400, 40), toon('#7f95ad'))); river.rotation.x = -Math.PI / 2; river.position.set(300, -69.9, -520);
  dimmable.push(ground.material, river.material);

  // ---------- Skyline ----------
  const skyline = new THREE.Group(); add(skyline);
  const PAL_SKY = ['#a3b6ca', '#c4ccd4', '#8195ae', '#d7d1c4', '#b8c2cc', '#9aa6a0'];
  const winTex = canvasTex(64, 256, (c, w, h) => {
    c.fillStyle = '#fff'; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(40,50,70,0.35)';
    for (let y = 6; y < h; y += 12) c.fillRect(0, y, w, 4);
  }, { repeat: [3, 6] });
  for (let i = 0; i < 34; i++) {
    const a = THREE.MathUtils.degToRad(-14 + (r() - 0.5) * 16), d = 560 + r() * 90;
    const hgt = 30 + Math.pow(r(), 1.6) * 150, w = 14 + r() * 18;
    const sm = toon(PAL_SKY[i % PAL_SKY.length], { map: winTex, noCache: true }); dimmable.push(sm);
    const m = edges(ink(new THREE.BoxGeometry(w, hgt, w * (0.7 + r() * 0.5)), sm, 0.6), 20);
    m.position.set(Math.sin(a) * d, -70 + hgt / 2, -Math.cos(a) * d); m.rotation.y = a; m.castShadow = false; skyline.add(m);
    for (let yy = 4; yy < hgt - 3; yy += 3.2) for (let c = -2; c <= 2; c++) if (r() < 0.42) {
      const off = w * 0.62 + 3.5, px = m.position.x - Math.sin(a) * off + Math.cos(a) * c * w * 0.18, pz = m.position.z + Math.cos(a) * off + Math.sin(a) * c * w * 0.18;
      lights.push(px, -70 + yy, pz, 3.0);
    }
    if (r() < 0.3) { const t = ink(new THREE.ConeGeometry(w * 0.45, hgt * 0.18, 4), toon('#8a96a8'), 0.5); t.position.set(m.position.x, -70 + hgt + hgt * 0.09, m.position.z); t.rotation.y = a + Math.PI / 4; skyline.add(t); }
  }

  // ---------- Reihenhäuser hinter der Straße ----------
  const winLit = new THREE.MeshBasicMaterial({ color: '#ffd98a' }), winDark = toon('#3b4656'), litWins = [];
  let x = -60;
  while (x < 60) {
    const w = 5.5 + r() * 3.5, h = 6.5 + r() * 4, col = PAL_ROW[(r() * PAL_ROW.length) | 0];
    const house = edges(ink(new THREE.BoxGeometry(w - 0.1, h, 9, 4, 4, 4), toon(col), 0.9));
    house.position.set(x + w / 2, h / 2, 18.7); add(house);
    const corn = edges(ink(new THREE.BoxGeometry(w, 0.35, 9.4), toon('#8a7a6a'), 0.6)); corn.position.set(x + w / 2, h + 0.1, 18.7); add(corn);
    for (let fy = 0; fy < 2; fy++) for (let fx = 0; fx < 2; fx++) {
      const lit = r() < 0.45, win = edges(ink(new THREE.BoxGeometry(1.1, 1.5, 0.1), lit ? winLit : winDark, 0.5));
      win.position.set(x + w * (0.3 + fx * 0.42), 2.3 + fy * 3, 14.15); add(win);
      if (lit) { litWins.push({ m: win, d: r() }); const fr = new THREE.Mesh(new THREE.BoxGeometry(0.06, 1.5, 0.12), flatDark); fr.position.copy(win.position); add(fr); }
    }
    const door = ink(new THREE.BoxGeometry(1.0, 2.1, 0.1), toon('#5a3b2b'), 0.5); door.position.set(x + w * 0.5, 1.05, 14.15); add(door);
    x += w;
  }
  // Fensterlichter als Punkte (gehen beim Stromausfall wellenartig aus)
  const lightPts = makeLights(lights, r); add(lightPts);
  const lampOn = new THREE.MeshBasicMaterial({ color: '#ffe9a8' }), lampOff = toon('#77786f');
  const lamps = [];
  // Laternen
  for (let lx = -48; lx <= 48; lx += 16) {
    const p = ink(new THREE.CylinderGeometry(0.06, 0.08, 4.6, 8), toon('#2a2a2c'), 0.6); p.position.set(lx, 2.3, 3.3); add(p);
    const l = ink(new THREE.BoxGeometry(0.35, 0.45, 0.35), lampOn, 0.6); l.position.set(lx, 4.7, 3.3); add(l); lamps.push(l);
  }
  // Straßenbäume
  for (let tx = -44; tx <= 44; tx += 14 + r() * 6) {
    const tr = ink(new THREE.CylinderGeometry(0.12, 0.18, 3, 7), toon('#5a3e2c'), 0.7); tr.position.set(tx, 1.5, 12.2); add(tr);
    for (let k = 0; k < 3; k++) {
      const cr = ink(new THREE.IcosahedronGeometry(1.1 + r() * 0.6, 0), toon(PAL_TREE[(r() * PAL_TREE.length) | 0]), 0.8);
      cr.position.set(tx + (r() - 0.5) * 1.4, 3.4 + r() * 1.2, 12.2 + (r() - 0.5) * 1.4); cr.rotation.set(r() * 3, r() * 3, 0); add(cr);
    }
  }
  // Autos
  add(car('#c43a2e', r)).position.set(-9, 0, 5.4);
  const c2 = add(car('#e9e6df', r)); c2.position.set(13, 0, 9.4); c2.rotation.y = Math.PI;
  const c3 = add(car('#6d8fb0', r)); c3.position.set(27, 0, 5.4);
  // Fließender Verkehr: Beat-Feld "auto": {spur: 1|2, farbe, ab, tempo} -> fährt zur Zeit t0+ab an x=0 vorbei
  const traffic = [];
  for (const b of beats) for (const a of [].concat(b.auto || [])) {
    const cg = add(car(a.farbe || PAL_CARS[traffic.length % PAL_CARS.length], r)); const lane = a.spur === 2 ? 2 : 1;
    cg.position.set(0, 0, lane === 1 ? 6.0 : 8.9); cg.rotation.y = lane === 1 ? 0 : Math.PI; cg.visible = false;
    const lights = headlights(cg); traffic.push({ g: cg, tc: b.t0 + (a.ab || 0), v: (a.tempo || 13) * (lane === 1 ? 1 : -1), lights });
  }
  // Mülltonne
  const bin = add(edges(ink(new THREE.CylinderGeometry(0.3, 0.27, 0.95, 14), toon('#2f5f9a'), 0.7))); bin.position.set(6, 0.47, 3.0);

  // pro Frame: Stromausfall-Zustand setzen. blackout = Sekunden seit Beginn (oder < 0), dur = Dauer der Welle
  const flick = beats.filter((b) => b.effekt?.flackern).map((b) => ({ t0: b.t0 + (b.effekt.flackern_ab || 0), t1: b.t0 + (b.effekt.flackern_ab || 0) + b.effekt.flackern }));
  const animBirds = birds(add, r), animLeaves = leaves(add, r, story.start || info.start), animPlane = plane(add);
  const hb = beats.find((b) => b.effekt?.hubschrauber), animHeli = heli(add, hb ? { t0: hb.t0 + (hb.effekt.hubschrauber.ab || 0), ...hb.effekt.hubschrauber } : null);
  root.userData.update = ({ blackout = -1, dur = 3, px = 768, t = 0 }) => {
    const u = lightPts.material.uniforms; u.uT.value = blackout; u.uDur.value = dur; u.uPx.value = px; u.uTime.value = t;
    const off = blackout >= dur * 0.85 || (blackout >= dur * 0.7 && Math.sin(t * 50) > 0);
    lamps.forEach((l) => (l.material = off ? lampOff : lampOn));
    // Stadt wird nach und nach dunkler/bläulicher
    const k = blackout < 0 ? 0 : Math.min(1, blackout / (dur * 1.2));
    dimmable.forEach((m) => { if (!m.userData.base) m.userData.base = m.color.clone(); m.color.copy(m.userData.base).lerp(DIM, k * 0.86); });
    litWins.forEach((w) => (w.m.material = blackout >= dur * (0.3 + w.d * 0.5) ? winDark : winLit));
    // flackernde Laternen (Beat-Effekt "flackern": Sekunden)
    const fl = flick.find((f) => t >= f.t0 && t < f.t1);
    if (fl && !off) lamps.forEach((l, i) => { const h = Math.sin(t * 31 + i * 7) + Math.sin(t * 53 + i * 3) + (Math.sin(t * 7 + i) > 0.6 ? 2 : 0); l.material = h > 1.2 ? lampOff : lampOn; });
    // Verkehr
    for (const c of traffic) { const x = (t - c.tc) * c.v; c.g.visible = Math.abs(x) < 70; c.g.position.x = x; c.lights.visible = k > 0.2 || story.himmel === 'daemmerung'; c.g.children.forEach((w) => { if (w.userData.wheel) w.rotation.y = -x / 0.36; }); }
    animBirds(t, blackout); animLeaves(t); animPlane(t); animHeli(t, k);
    const fog = root.parent?.fog; if (fog) { if (!fog.userData) fog.userData = {}; if (!fog.userData.base) fog.userData.base = fog.color.clone(); fog.color.copy(fog.userData.base).lerp(FOG_DIM, k * 0.8); }
  };
  return root;
}

const DIM = new THREE.Color('#1a2040'), FOG_DIM = new THREE.Color('#4a3f5e');
function makeLights(arr, r) {
  const n = arr.length / 4, pos = new Float32Array(n * 3), size = new Float32Array(n), delay = new Float32Array(n), seed = new Float32Array(n);
  const cx = Math.sin(-14 * Math.PI / 180) * 600, cz = -Math.cos(-14 * Math.PI / 180) * 600;
  for (let i = 0; i < n; i++) {
    pos.set([arr[i * 4], arr[i * 4 + 1], arr[i * 4 + 2]], i * 3); size[i] = arr[i * 4 + 3];
    delay[i] = Math.min(1, Math.hypot(arr[i * 4] - cx, arr[i * 4 + 2] - cz) / 900) * 0.8 + r() * 0.15; seed[i] = r() * 100;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  g.setAttribute('aDelay', new THREE.BufferAttribute(delay, 1)); g.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
  const m = new THREE.ShaderMaterial({
    uniforms: { uT: { value: -1 }, uDur: { value: 3 }, uPx: { value: 768 }, uTime: { value: 0 } },
    vertexShader: `attribute float aSize, aDelay, aSeed; uniform float uT, uDur, uPx, uTime; varying float vOn; varying float vSeed;
      void main(){ vec4 mv = modelViewMatrix * vec4(position,1.0); gl_Position = projectionMatrix * mv;
        gl_PointSize = max(1.5, aSize * uPx / -mv.z);
        float k = aDelay * uDur; vOn = 1.0;
        if (uT >= 0.0) { if (uT > k) vOn = 0.0; else if (uT > k - 0.3) vOn = step(0.0, sin(uTime * 47.0 + aSeed)); }
        vSeed = aSeed; }`,
    fragmentShader: `varying float vOn; varying float vSeed;
      void main(){ if (vOn < 0.5) discard; vec2 c = gl_PointCoord - 0.5; if (max(abs(c.x), abs(c.y)) > 0.42) discard;
        vec3 col = mix(vec3(1.0,0.83,0.45), vec3(1.0,0.93,0.7), fract(vSeed));
        gl_FragColor = vec4(col, 1.0);
        #include <colorspace_fragment>
      }`,
  });
  const p = new THREE.Points(g, m); p.frustumCulled = false; return p;
}

export function car(color, r) {
  const g = new THREE.Group();
  const body = edges(ink(new THREE.BoxGeometry(4.3, 0.75, 1.85), toon(color), 0.9)); body.position.y = 0.65; g.add(body);
  const cab = edges(ink(new THREE.BoxGeometry(2.1, 0.65, 1.7), toon(color), 0.9)); cab.position.set(-0.3, 1.33, 0); g.add(cab);
  const glass = ink(new THREE.BoxGeometry(2.0, 0.5, 1.74), toon('#4a5a6e'), 0); glass.position.set(-0.3, 1.36, 0); g.add(glass);
  for (const [x, z] of [[-1.4, 0.9], [1.4, 0.9], [-1.4, -0.9], [1.4, -0.9]]) {
    const w = ink(new THREE.CylinderGeometry(0.36, 0.36, 0.26, 16), toon('#1e1e20'), 0.7); w.rotation.x = Math.PI / 2; w.position.set(x, 0.36, z); g.add(w);
    const hub = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.27), toon('#9a9a9a')); hub.position.copy(w.position); hub.rotation.x = Math.PI / 2; hub.userData.wheel = true; g.add(hub);
  }
  return g;
}

// ---------- Details, die sich bewegen ----------
const BEAM = new THREE.MeshBasicMaterial({ color: '#fff3c4', transparent: true, opacity: 0.16, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });
export function headlights(g, len = 9, front = 2.15) {
  const grp = new THREE.Group(); g.add(grp);
  for (const z of [-0.6, 0.6]) {
    const l = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.16, 0.34), new THREE.MeshBasicMaterial({ color: '#fff6d6' })); l.position.set(front, 0.72, z); g.add(l);
    const cone = new THREE.Mesh(new THREE.ConeGeometry(1.6, len, 20, 1, true), BEAM); cone.rotation.z = Math.PI / 2; cone.position.set(front + len / 2, 0.55, z); grp.add(cone);
  }
  return grp;
}
function birds(add, r) {
  // kleiner Vogelschwarm über dem Abhang; flattert, kreist, fliegt beim Stromausfall auf und davon
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute([-0.5, 0.25, 0, 0, 0, 0.12, 0, 0, -0.12, 0.5, 0.25, 0, 0, 0, -0.12, 0, 0, 0.12], 3));
  const N = 18, m = new THREE.InstancedMesh(geo, new THREE.MeshBasicMaterial({ color: '#221c26', side: THREE.DoubleSide }), N); add(m); m.frustumCulled = false;
  const B = Array.from({ length: N }, () => ({ ph: r() * 6.28, rad: 9 + r() * 7, h: 6 + r() * 6, sp: 0.18 + r() * 0.08, fl: 9 + r() * 4, off: [(r() - 0.5) * 6, (r() - 0.5) * 3] }));
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), P = new THREE.Vector3(), S = new THREE.Vector3(), E = new THREE.Euler();
  return (t, bo) => {
    B.forEach((b, i) => {
      const a = b.ph + t * b.sp, flee = bo > 0 ? bo : 0;
      P.set(-8 + Math.cos(a) * b.rad + b.off[0], b.h + Math.sin(t * 0.7 + i) * 0.8 + flee * flee * 2.2, -26 + Math.sin(a) * b.rad * 0.6 + b.off[1] - flee * 9);
      E.set(0, -a, Math.sin(t * 0.9 + i) * 0.3); Q.setFromEuler(E);
      const flap = Math.sin(t * (flee ? 16 : b.fl) + i * 1.3); S.set(0.9, flap * 1.1, 0.9);
      m.setMatrixAt(i, M.compose(P, Q, S));
    });
    m.instanceMatrix.needsUpdate = true;
  };
}
function leaves(add, r, start) {
  // Herbstlaub, das der Wind über den Gehweg treibt
  const N = 70, geo = new THREE.PlaneGeometry(0.09, 0.06), m = new THREE.InstancedMesh(geo, toon('#ffffff', { side: THREE.DoubleSide, noCache: true }), N);
  const C = new THREE.Color(), L = Array.from({ length: N }, () => ({ x: r() * 40, z: start[1] + (r() - 0.3) * 5.5, sp: 0.6 + r() * 1.6, ph: r() * 6.28, spin: 2 + r() * 6 }));
  L.forEach((l, i) => m.setColorAt(i, C.set(PAL_TREE[(r() * PAL_TREE.length) | 0])));
  m.receiveShadow = true; add(m); m.frustumCulled = false;
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), P = new THREE.Vector3(), S = new THREE.Vector3(1, 1, 1), E = new THREE.Euler();
  return (t) => {
    const gust = 0.6 + 0.4 * Math.sin(t * 0.37) * Math.sin(t * 0.23 + 1);
    L.forEach((l, i) => {
      const x = ((l.x + t * l.sp * gust * 1.4) % 40) - 20 + start[0];
      const hop = Math.max(0, Math.sin(t * l.sp * 3 + l.ph)) * 0.18 * gust;
      P.set(x, 0.02 + hop, l.z + Math.sin(t * 0.8 + l.ph) * 0.3);
      E.set(-Math.PI / 2 + Math.sin(t * l.spin + l.ph) * hop * 6, t * l.spin * 0.3 + l.ph, 0); Q.setFromEuler(E);
      m.setMatrixAt(i, M.compose(P, Q, S));
    });
    m.instanceMatrix.needsUpdate = true;
  };
}
function plane(add) {
  // Flugzeug hoch am Himmel mit Blinklicht
  const g = new THREE.Group(); add(g);
  const mat = new THREE.MeshBasicMaterial({ color: '#3a3550', fog: false });
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(1.4, 16, 4, 8), mat); body.rotation.z = Math.PI / 2; g.add(body);
  const wing = new THREE.Mesh(new THREE.BoxGeometry(4, 0.3, 26), mat); g.add(wing);
  const tail = new THREE.Mesh(new THREE.BoxGeometry(2.5, 4, 0.3), mat); tail.position.set(-8, 2, 0); g.add(tail);
  const blink = new THREE.Mesh(new THREE.SphereGeometry(1.6, 8, 6), new THREE.MeshBasicMaterial({ color: '#ff3b30', fog: false })); blink.position.y = -1.6; g.add(blink);
  return (t) => { g.position.set(-700 + t * 9, 420, -1300); blink.visible = (t % 1.2) < 0.12; };
}
export function heli(add, H) {
  if (!H) return () => {};
  // Polizeihubschrauber mit Suchscheinwerfer, der über die dunkle Stadt streicht
  const g = new THREE.Group(); add(g); g.visible = false;
  const dark = toon('#2a3442'), stripe = toon('#d9dde3');
  const body = ink(new THREE.SphereGeometry(1.5, 16, 12), dark, 1.0); body.scale.set(1.6, 1, 1); g.add(body);
  const band = ink(new THREE.SphereGeometry(1.52, 16, 12, 0, Math.PI * 2, 1.3, 0.35), stripe, 0.6); band.scale.set(1.6, 1, 1); g.add(band);
  const boom = ink(new THREE.CylinderGeometry(0.22, 0.4, 5, 8), dark, 0.8); boom.rotation.z = Math.PI / 2; boom.position.x = -4; g.add(boom);
  const fin = ink(new THREE.BoxGeometry(0.9, 1.4, 0.15), dark, 0.6); fin.position.set(-6.3, 0.6, 0); g.add(fin);
  const rotor = new THREE.Mesh(new THREE.BoxGeometry(11, 0.06, 0.35), new THREE.MeshBasicMaterial({ color: '#141418', transparent: true, opacity: 0.75 })); rotor.position.y = 1.4; g.add(rotor);
  const rotor2 = rotor.clone(); rotor2.rotation.y = Math.PI / 2; rotor.add(rotor2);
  for (const z of [-0.9, 0.9]) { const sk = ink(new THREE.BoxGeometry(3.2, 0.1, 0.12), dark, 0.5); sk.position.set(0, -1.4, z); g.add(sk); }
  const red = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 6), new THREE.MeshBasicMaterial({ color: '#ff2a2a', fog: false })); red.position.set(-6.4, 1.3, 0); g.add(red);
  const beamPivot = new THREE.Group(); beamPivot.position.set(1.8, -1.2, 0); g.add(beamPivot);
  const beamMat = new THREE.MeshBasicMaterial({ color: '#f3f6ff', transparent: true, opacity: 0.13, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false });
  const cone = new THREE.Mesh(new THREE.ConeGeometry(9, 90, 24, 1, true), beamMat); cone.position.y = -45; beamPivot.add(cone);
  const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.45, 10, 8), new THREE.MeshBasicMaterial({ color: '#ffffff', fog: false })); lamp.position.copy(beamPivot.position); g.add(lamp);
  const von = new THREE.Vector3(...(H.von || [160, 40, -160])), nach = new THREE.Vector3(...(H.nach || [-40, 25, -70])), dur = H.dauer || 14;
  return (t) => {
    const k = (t - H.t0) / dur; g.visible = k >= 0; if (k < 0) return;
    const e = Math.min(1, k); const ee = 1 - (1 - e) * (1 - e);
    g.position.lerpVectors(von, nach, ee); g.position.y += Math.sin(t * 1.3) * 0.4;
    const dir = nach.clone().sub(von); g.rotation.set(0, Math.atan2(-dir.z, dir.x), -0.12 * (1 - e) + Math.sin(t * 0.8) * 0.03);
    rotor.rotation.y = t * 31;
    beamPivot.rotation.set(Math.sin(t * 0.7) * 0.45, 0, -0.5 + Math.sin(t * 0.43) * 0.35);
    red.visible = (t % 1.0) < 0.15;
  };
}
