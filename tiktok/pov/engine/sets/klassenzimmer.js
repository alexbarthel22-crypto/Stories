// Set "klassenzimmer": Klasse 10b am Montagmorgen (Tageslicht). Raum x -5 … 5, z -6 … 6, Höhe 3.2.
// Vorne (-Z) Smartboard + Lehrerpult, rechts (+X) Tür (z -4.5), links (-X) Fensterfront mit Sonne.
// Tische: Spalten x = -3, -0.5, 2 · Reihen z = -2.2, -0.4, 1.4, 3.2 · Stühle bei (x ± 0.35, z + 0.55).
//
// Beat-Effekte (Feld "effekt"):
//   tafel: {ab, modus: "aus"|"video"|"countdown"|"pause"|"geloescht"|"text", von, text}  -> Smartboard
//   handys: s     -> alle Handys auf den Tischen leuchten auf und vibrieren
//   klingel: s    -> Schulgong (nur Lautsprecher-Wackeln; Ton per sfx)
import * as THREE from 'three';
import { toon, ink, inkInstanced, edges, canvasTex, stains, rng } from '../toon.js';

export const info = {
  start: [2.4, 2.0],
  spots: {
    tafel: [0, -6], tuer: [-60, -4], fenster: [90, 4], klasse: [12, -16], decke: [0, 70], boden: [0, -60], pult: [20, -12], hinten: [180, -4],
  },
};
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color();
const BOX = new THREE.BoxGeometry(1, 1, 1);
const X0 = -5, X1 = 5, Z0 = -6, Z1 = 6, H = 3.2;
export const DESKS = []; for (const z of [-2.2, -0.4, 1.4, 3.2]) for (const x of [-3, -0.5, 2]) DESKS.push([x, z]);
function instanced(geo, mat, items, inkW = 0.5) {
  const m = inkW ? inkInstanced(geo, mat, items.length, inkW) : new THREE.InstancedMesh(geo, mat, items.length);
  items.forEach((it, i) => { E.set(it.rx || 0, it.ry || 0, it.rz || 0); Q.setFromEuler(E); m.setMatrixAt(i, M4.compose(P.set(...it.p), Q, S.set(...(it.s || [1, 1, 1])))); if (it.c) m.setColorAt(i, C.set(it.c)); });
  m.castShadow = true; m.receiveShadow = true; return m;
}

export function build(scene, seed = 81, ctx = {}) {
  const beats = ctx.beats || [];
  const r = rng(seed);
  const root = new THREE.Group(); scene.add(root);
  const add = (o) => (root.add(o), o);
  scene.fog = new THREE.Fog('#c8d8e8', 40, 200);
  const glowTex = canvasTex(64, 64, (c, w) => { const g = c.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(0, 0, w, w); });
  const plane = (w, h, tex, x, y, z, ry, opts = {}) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), toon('#ffffff', { map: tex, ...opts }))); m.position.set(x, y, z); m.rotation.y = ry; return m; };

  // ---------- Raum ----------
  const floorTex = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#9a8a74'; c.fillRect(0, 0, w, h); for (let i = 0; i < 2500; i++) { c.fillStyle = ['#a8987e', '#8a7a64', '#b0a088'][(r() * 3) | 0]; c.fillRect(r() * w, r() * h, 2, 2); } stains(c, w, h, r, 8, '60,50,40', 0.2); }, { repeat: [4, 5] });
  const fl = add(new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), toon('#ffffff', { map: floorTex }))); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true;
  const ceil = add(new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), toon('#f0eee8'))); ceil.rotation.x = Math.PI / 2; ceil.position.y = H;
  const paint = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#f2ead8'; c.fillRect(0, 0, w, h); c.fillStyle = '#d8b878'; c.fillRect(0, h * 0.7, w, h * 0.3); stains(c, w, h, r, 8, '90,80,60', 0.12); }, { repeat: [3, 1] });
  const wallM = toon('#ffffff', { map: paint });
  const wall = (w, x, z, ry) => { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, H), wallM)); m.position.set(x, H / 2, z); m.rotation.y = ry; m.receiveShadow = true; return m; };
  wall(X1 - X0, 0, Z0, 0); wall(X1 - X0, 0, Z1, Math.PI); wall(Z1 - Z0, X1, 0, -Math.PI / 2);
  // Fensterfront links: Brüstung + Fensterbänder mit echten Öffnungen
  const seg = (z0, z1, y0, y1) => { const m = add(new THREE.Mesh(new THREE.BoxGeometry(0.2, y1 - y0, z1 - z0), wallM)); m.position.set(X0 - 0.1, (y0 + y1) / 2, (z0 + z1) / 2); m.castShadow = true; m.receiveShadow = true; };
  seg(Z0, Z1, 0, 0.9); seg(Z0, Z1, 2.7, H); const wins = [[-5.4, -2.6], [-2.2, 0.6], [1.0, 3.8]]; let zz = Z0;
  for (const [a, b] of wins) { seg(zz, a, 0.9, 2.7); zz = b; const sill = add(ink(new THREE.BoxGeometry(0.4, 0.05, b - a), toon('#e8e8e8'), 0.3)); sill.position.set(X0 + 0.1, 0.92, (a + b) / 2);
    const blind = add(new THREE.Mesh(new THREE.PlaneGeometry(b - a, 0.5), toon('#ffffff', { map: canvasTex(64, 64, (c, w, h) => { c.fillStyle = '#e8e4d8'; c.fillRect(0, 0, w, h); c.fillStyle = 'rgba(0,0,0,0.12)'; for (let y = 0; y < h; y += 6) c.fillRect(0, y, w, 2); }) }))); blind.position.set(X0 + 0.02, 2.45, (a + b) / 2); blind.rotation.y = Math.PI / 2; }
  seg(zz, Z1, 0.9, 2.7);
  // Pflanzen auf der Fensterbank
  for (const z of [-4.5, -0.8, 2.6]) { const pot = add(ink(new THREE.CylinderGeometry(0.1, 0.08, 0.16, 10), toon('#b8603a'), 0.3)); pot.position.set(X0 + 0.12, 1.02, z); const pl = add(ink(new THREE.IcosahedronGeometry(0.16, 0), toon('#4a8a3a'), 0.3)); pl.position.set(X0 + 0.12, 1.2, z); }
  // Draußen: Schulhof, Bäume, Sonne
  const yard = add(new THREE.Mesh(new THREE.PlaneGeometry(80, 80), toon('#8a8e86'))); yard.rotation.x = -Math.PI / 2; yard.position.set(-45, -0.02, 0);
  for (let i = 0; i < 10; i++) { const t = add(ink(new THREE.IcosahedronGeometry(1.6 + r(), 0), toon(['#5a9a4a', '#6aa84a', '#4a8a3a'][i % 3]), 0.6)); t.position.set(-12 - r() * 18, 3.5 + r(), -14 + r() * 28); const tr = add(ink(new THREE.CylinderGeometry(0.15, 0.2, 3, 6), toon('#6a4a32'), 0.4)); tr.position.set(t.position.x, 1.5, t.position.z); }
  add(edges(ink(new THREE.BoxGeometry(14, 6, 10), toon('#c8a888'), 0.7))).position.set(-30, 3, 8);
  const sunM = new THREE.MeshBasicMaterial({ color: '#fff0c0', map: glowTex, transparent: true, opacity: 0.25, blending: THREE.AdditiveBlending, depthWrite: false });
  for (const [a, b] of wins) { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(1.8, b - a), sunM)); m.rotation.x = -Math.PI / 2; m.position.set(X0 + 1.4, 0.01, (a + b) / 2 + 0.4); }

  // ---------- Vorne: Smartboard, Lehrerpult ----------
  const sbC = document.createElement('canvas'); sbC.width = 1024; sbC.height = 576; const sbT = new THREE.CanvasTexture(sbC); sbT.colorSpace = THREE.SRGBColorSpace;
  add(edges(ink(new THREE.BoxGeometry(3.4, 1.95, 0.08), toon('#2a2a2c'), 0.5))).position.set(0, 1.65, Z0 + 0.04);
  const sb = add(new THREE.Mesh(new THREE.PlaneGeometry(3.2, 1.8), new THREE.MeshBasicMaterial({ map: sbT, toneMapped: false }))); sb.position.set(0, 1.65, Z0 + 0.09);
  const sbL = add(new THREE.PointLight('#a8c8ff', 0, 0, 1.6)); sbL.position.set(0, 1.6, Z0 + 1.5);
  const pult = add(edges(ink(new THREE.BoxGeometry(1.6, 0.76, 0.75), toon('#a8784a'), 0.5))); pult.position.set(-2.8, 0.38, -4.6);
  const lap = add(ink(new THREE.BoxGeometry(0.36, 0.02, 0.25), toon('#3a3a3e'), 0.3)); lap.position.set(-2.6, 0.77, -4.6); const lapS = add(ink(new THREE.BoxGeometry(0.36, 0.24, 0.02), toon('#3a3a3e'), 0.3)); lapS.position.set(-2.6, 0.89, -4.74); lapS.rotation.x = -0.2;
  const mug = add(ink(new THREE.CylinderGeometry(0.045, 0.04, 0.1, 10), toon('#e85a3a'), 0.3)); mug.position.set(-3.3, 0.81, -4.5);
  const globe = add(ink(new THREE.SphereGeometry(0.16, 16, 12), toon('#4a8ad0'), 0.3)); globe.position.set(-3.45, 0.98, -4.8);
  // Poster, Stundenplan, Uhr, Klassenregeln
  const poster = (title, lines, bg, fg) => canvasTex(256, 340, (c, w, h) => { c.fillStyle = bg; c.fillRect(0, 0, w, h); c.fillStyle = fg; c.font = '900 26px Inter, sans-serif'; c.fillText(title, 14, 40); c.font = '600 17px Inter, sans-serif'; lines.forEach((l, i) => c.fillText(l, 14, 80 + i * 26)); });
  plane(0.9, 1.2, poster('KLASSENREGELN', ['1. Wir hören zu.', '2. Wir lachen mit-', '   einander, nicht', '   übereinander.', '3. Niemand wird', '   ausgeschlossen.', '4. Handys aus!'], '#fff6d8', '#2a2a2a'), 2.6, 1.7, Z0 + 0.02, 0);
  plane(0.9, 1.2, poster('IRREGULAR VERBS', ['go – went – gone', 'see – saw – seen', 'tell – told – told', 'hide – hid – hidden', 'lie – lay – lain'], '#d8ecff', '#1a3a6a'), -2.6, 1.7, Z0 + 0.02, 0);
  plane(1.4, 1.0, canvasTex(512, 360, (c, w, h) => { c.fillStyle = '#f8f8f0'; c.fillRect(0, 0, w, h); c.fillStyle = '#111'; c.font = '900 30px Inter, sans-serif'; c.fillText('STUNDENPLAN 10b', 16, 40); const d = ['Mo', 'Di', 'Mi', 'Do', 'Fr'], f = ['De', 'Ma', 'En', 'Bio', 'Sp', 'Ge', 'Ku', 'Ph'];
    d.forEach((x, i) => { c.font = '800 20px Inter, sans-serif'; c.fillText(x, 60 + i * 88, 80); for (let k = 0; k < 6; k++) { c.fillStyle = ['#ffd8d8', '#d8ffd8', '#d8e8ff', '#fff0c8'][(i + k) % 4]; c.fillRect(40 + i * 88, 92 + k * 42, 80, 36); c.fillStyle = '#111'; c.font = '700 18px Inter, sans-serif'; c.fillText(f[(i * 3 + k) % f.length], 54 + i * 88, 116 + k * 42); } }); }), X1 - 0.02, 1.8, 1.0, -Math.PI / 2);
  plane(1.3, 0.9, poster('KLASSENFAHRT', ['BERLIN 2027', '14.–18. Juni', 'Elternabend: Do'], '#ffd84a', '#111'), 0, 1.8, Z1 - 0.02, Math.PI);
  const clkC = document.createElement('canvas'); clkC.width = clkC.height = 128; const clkT = new THREE.CanvasTexture(clkC); clkT.colorSpace = THREE.SRGBColorSpace;
  const clk = add(new THREE.Mesh(new THREE.CircleGeometry(0.26, 24), new THREE.MeshBasicMaterial({ map: clkT }))); clk.position.set(1.0, 2.85, Z0 + 0.03);
  const spk = add(ink(new THREE.BoxGeometry(0.4, 0.25, 0.12), toon('#e8e4dc'), 0.3)); spk.position.set(-1.2, 2.9, Z0 + 0.06);
  // Tür rechts + Garderobe hinten
  const door = add(ink(new THREE.BoxGeometry(0.06, 2.2, 1.0), toon('#8a5a3a'), 0.5)); door.position.set(X1 - 0.03, 1.1, -4.5);
  const hooks = []; for (let k = 0; k < 10; k++) hooks.push({ p: [-3.6 + k * 0.8, 1.55, Z1 - 0.12], s: [0.5, 0.75, 0.15], c: ['#2a4a8a', '#c83a2a', '#3a3a3a', '#e8c020', '#4a8a4a', '#8a4ab0'][k % 6] });
  add(instanced(BOX, toon('#ffffff'), hooks.filter((_, i) => i % 3 !== 2), 0.4));
  // ---------- Tische, Stühle, Rucksäcke, Bücher, Mäppchen, Handys ----------
  const desks = [], chairs = [], bags = [], books = [], phones = [];
  for (const [x, z] of DESKS) {
    desks.push({ p: [x, 0.74, z], s: [1.4, 0.05, 0.6], c: '#d8c8a8' }, { p: [x - 0.66, 0.37, z], s: [0.04, 0.72, 0.55], c: '#6a6e72' }, { p: [x + 0.66, 0.37, z], s: [0.04, 0.72, 0.55], c: '#6a6e72' });
    for (const s of [-1, 1]) { const cx = x + s * 0.35, cz = z + 0.55; chairs.push({ p: [cx, 0.44, cz], s: [0.4, 0.04, 0.4], c: '#2a6ab0' }, { p: [cx, 0.68, cz + 0.2], s: [0.4, 0.42, 0.03], c: '#2a6ab0' });
      if (r() < 0.8) bags.push({ p: [cx + s * 0.3, 0.2, cz], s: [0.28, 0.4, 0.2], ry: r(), c: ['#c83a2a', '#2a2a2a', '#3a8ad0', '#e8c020', '#8a4ab0', '#2a8a6a'][(r() * 6) | 0] });
      if (r() < 0.7) books.push({ p: [cx - s * 0.05, 0.78, z - 0.05], s: [0.22, 0.03, 0.3], ry: (r() - 0.5) * 0.5, c: ['#e84a3a', '#3a7ad0', '#4ac06a', '#f0d040'][(r() * 4) | 0] });
      phones.push({ x: cx + s * 0.15, z: z + 0.12, ph: r() * 6 }); }
  }
  add(instanced(BOX, toon('#ffffff'), desks, 0.4)); add(instanced(BOX, toon('#ffffff'), chairs, 0.3)); add(instanced(BOX, toon('#ffffff'), bags, 0.4)); add(instanced(BOX, toon('#ffffff'), books, 0.3));
  const phM = new THREE.InstancedMesh(new THREE.BoxGeometry(0.07, 0.01, 0.14), new THREE.MeshBasicMaterial({ color: '#ffffff', toneMapped: false }), phones.length); add(phM); phM.frustumCulled = false;
  const phGlow = phones.map((p) => { const g = add(new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: '#9ac8ff', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }))); g.scale.set(0.4, 0.4, 1); g.position.set(p.x, 0.8, p.z); return g; });
  // Staub im Sonnenlicht
  const dust = (() => { const N = 300, pos = new Float32Array(N * 3); for (let i = 0; i < N; i++) pos.set([X0 + 0.3 + Math.random() * 3, 0.5 + Math.random() * 2.4, -5.5 + Math.random() * 10], i * 3);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const m = new THREE.ShaderMaterial({ uniforms: { uT: { value: 0 }, uPx: { value: 768 } }, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: `uniform float uT, uPx; varying float vA; void main(){ vec3 p = position; p.y += sin(uT * 0.3 + position.x * 9.0) * 0.1; p.z += cos(uT * 0.2 + position.y * 7.0) * 0.15; vA = 0.35 + 0.25 * sin(uT + position.z * 20.0); vec4 mv = modelViewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = max(1.0, 0.02 * uPx / -mv.z); }`,
      fragmentShader: `varying float vA; void main(){ float d = length(gl_PointCoord - 0.5); if (d > 0.5) discard; gl_FragColor = vec4(1.0, 0.95, 0.8, vA * (1.0 - d * 2.0)); }` });
    const p = new THREE.Points(g, m); p.frustumCulled = false; add(p); return m; })();
  const roomL = add(new THREE.PointLight('#fff8f0', 2.5, 0, 1.2)); roomL.position.set(0, 2.9, 0);

  // ---------- Smartboard-Zustände ----------
  const tafel = beats.flatMap((b) => (b.effekt?.tafel === undefined ? [] : [].concat(b.effekt.tafel).map((v) => ({ t: b.t0 + (v.ab || 0), ...v })))).sort((a, b) => a.t - b.t);
  const handyT = beats.flatMap((b) => (b.effekt?.handys === undefined ? [] : [b.t0 + (b.effekt.handys === true ? 0 : b.effekt.handys)]));
  const klT = beats.flatMap((b) => (b.effekt?.klingel === undefined ? [] : [b.t0 + (b.effekt.klingel === true ? 0 : b.effekt.klingel)]));
  let sbKey = '';
  const drawBoard = (t) => {
    const st = tafel.filter((x) => t >= x.t).pop(); const mode = st ? st.modus : 'aus';
    const cd = mode === 'countdown' ? Math.max(0, Math.ceil((st.von || 10) - (t - st.t))) : 0;
    const key = `${mode}|${cd}|${mode === 'video' ? Math.floor(t * 4) : 0}|${st ? st.text : ''}`; if (key === sbKey) return; sbKey = key;
    const g = sbC.getContext('2d'); g.textAlign = 'center'; g.textBaseline = 'middle';
    if (mode === 'aus') { g.fillStyle = '#101418'; g.fillRect(0, 0, 1024, 576); g.fillStyle = 'rgba(255,255,255,0.06)'; g.beginPath(); g.moveTo(100, 0); g.lineTo(300, 0); g.lineTo(100, 576); g.lineTo(0, 576); g.fill(); sbL.intensity = 0; }
    else if (mode === 'text') { g.fillStyle = '#f8f8f4'; g.fillRect(0, 0, 1024, 576); g.fillStyle = '#1a3a8a'; g.font = '900 64px Inter, sans-serif'; g.fillText(st.text || '', 512, 288); sbL.intensity = 1.5; }
    else if (mode === 'geloescht') { g.fillStyle = '#0a1a10'; g.fillRect(0, 0, 1024, 576); g.fillStyle = '#4aff8a'; g.font = '900 80px Inter, sans-serif'; g.fillText('VIDEO GELÖSCHT', 512, 260); g.font = '600 32px Inter, sans-serif'; g.fillStyle = '#c8ffd8'; g.fillText(st.text || '', 512, 360); sbL.intensity = 1.5; }
    else { // Video (Nachtsicht vom Geräteraum) + ggf. Countdown/Pause
      g.fillStyle = '#0a160c'; g.fillRect(0, 0, 1024, 576);
      g.strokeStyle = '#3a6a42'; g.lineWidth = 6; g.strokeRect(300, 120, 420, 340); g.fillStyle = '#1a2a1c'; g.fillRect(300, 120, 420, 340); g.fillStyle = '#4a8a52'; g.font = '900 34px Inter, sans-serif'; g.fillText('GERÄTERAUM', 510, 160);
      const k = mode === 'video' ? (t * 0.8) % 1 : 0.6; g.fillStyle = '#2a4a2e'; g.fillRect(300 + k * 120, 180, 420 - k * 240, 280); // Tür schließt
      for (const [x, s] of [[200, 1], [820, 0.9], [880, 1.05]]) { g.fillStyle = '#060a06'; g.beginPath(); g.arc(x, 300, 34 * s, 0, 7); g.fill(); g.fillRect(x - 40 * s, 334, 80 * s, 200); }
      g.fillStyle = '#e8f0e8'; g.font = '700 26px monospace'; g.textAlign = 'left'; g.fillText('MUTPROBE.mp4 · 14.11.2025 23:41', 24, 32); g.textAlign = 'center';
      if (Math.floor(t * 2) % 2 === 0) { g.fillStyle = '#ff3a2a'; g.beginPath(); g.arc(960, 32, 10, 0, 7); g.fill(); }
      g.fillStyle = 'rgba(255,255,255,0.05)'; for (let y = 0; y < 576; y += 6) g.fillRect(0, y, 1024, 2);
      if (mode === 'countdown' || mode === 'pause') { g.fillStyle = 'rgba(0,0,0,0.55)'; g.fillRect(0, 0, 1024, 576); g.fillStyle = mode === 'pause' ? '#ffd84a' : '#ff3a2a'; g.font = '900 220px Inter, sans-serif'; g.font = mode === 'pause' ? '900 140px Inter, sans-serif' : '900 220px Inter, sans-serif'; g.fillText(mode === 'pause' ? 'PAUSE' : String(cd), 512, 300); g.font = '800 34px Inter, sans-serif'; g.fillStyle = '#fff'; g.fillText(st.text || 'Video startet in …', 512, 500); }
      else { g.fillStyle = 'rgba(255,255,255,0.9)'; g.beginPath(); g.moveTo(480, 250); g.lineTo(480, 330); g.lineTo(550, 290); g.closePath(); g.globalAlpha = 0.0; g.fill(); g.globalAlpha = 1; }
      sbL.intensity = 2.2;
    }
    sbT.needsUpdate = true;
  };

  root.userData.update = ({ t = 0, px = 768 }) => {
    drawBoard(t);
    dust.uniforms.uT.value = t; dust.uniforms.uPx.value = px;
    // Handys auf den Tischen
    const ht = handyT.filter((x) => t >= x).pop(), hk = ht !== undefined ? t - ht : -1;
    phones.forEach((p, i) => { const on = hk >= 0 && hk < 6 && hk > (i % 5) * 0.12; const vib = on && hk < 2.5 ? Math.sin(t * 90 + i) * 0.004 : 0; M4.makeTranslation(p.x + vib, 0.775, p.z); phM.setMatrixAt(i, M4); phM.setColorAt(i, C.set(on ? '#cfe4ff' : '#1a1a1c')); phGlow[i].material.opacity = on ? 0.5 : 0; });
    phM.instanceMatrix.needsUpdate = true; phM.instanceColor.needsUpdate = true;
    spk.position.x = -1.2 + (klT.some((k) => t >= k && t < k + 2) ? Math.sin(t * 80) * 0.004 : 0);
    // Uhr: 07:58 + Zeit
    { const g = clkC.getContext('2d'); const mins = 7 * 60 + 58 + t / 60; g.fillStyle = '#fafaf4'; g.beginPath(); g.arc(64, 64, 60, 0, 7); g.fill(); g.lineWidth = 6; g.strokeStyle = '#222'; g.stroke(); g.fillStyle = '#222'; for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; g.fillRect(64 + Math.sin(a) * 47 - 2, 64 - Math.cos(a) * 47 - 5, 4, 10); }
      const hA = (mins / 60 % 12) / 12 * 6.283, mA = (mins % 60) / 60 * 6.283, sA = (t % 60) / 60 * 6.283; g.lineCap = 'round'; g.lineWidth = 7; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(hA) * 28, 64 - Math.cos(hA) * 28); g.stroke(); g.lineWidth = 4; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(mA) * 44, 64 - Math.cos(mA) * 44); g.stroke(); g.strokeStyle = '#c0201a'; g.lineWidth = 2; g.beginPath(); g.moveTo(64, 64); g.lineTo(64 + Math.sin(sA) * 48, 64 - Math.cos(sA) * 48); g.stroke(); clkT.needsUpdate = true; }
  };
  return root;
}
