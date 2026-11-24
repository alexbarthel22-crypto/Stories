// Realistischer Erdriss quer über eine Straße: zwei Schollen mit Schichtaufbau (Asphalt, Tragschicht, Kies, Erdreich),
// die auseinanderreißen und gegeneinander versetzt werden. Dazu aufgeworfene Asphaltplatten, Haarrisse, gebrochene Rohre,
// bröckelnde Kanten, fallender Schutt und Staubfahnen. Glut nur ganz schwach tief unten.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, canvasTex, easeOut, easeIn} from './lib.js';
import {particles, updateParticles} from './fx.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

// o: {x0, x1, z0, z1, cx (Risslinie), depth, seed}
export function makeFissure(scene, o) {
  const r = rng(o.seed || 3); const D = o.depth || 3.2, Z0 = o.z0, Z1 = o.z1, X0 = o.x0, X1 = o.x1, CX = o.cx;
  const root = new THREE.Group(); scene.add(root);
  // Risslinie (lokal, relativ zu CX)
  const line = []; for (let z = Z0 - 0.01; z <= Z1 + 0.01; z += 0.3) line.push(new THREE.Vector2(0.75 * Math.sin(z * 0.42 + 1) + 0.3 * Math.sin(z * 1.6) + 0.22 * (r() - 0.5), z));
  line[line.length - 1].y = Z1 + 0.01;
  // Oberfläche: Gras – Gehweg – Bordstein – Fahrbahn – … (Textur läuft entlang z)
  const topT = canvasTex(512, 2048, (g, w, h) => { const zz = v => (v - (Z0 - 0.01)) / (Z1 - Z0 + 0.02) * h; const R = rng(5);
    const band = (a, b, f) => { const y0 = h - zz(b), y1 = h - zz(a); f(y0, y1 - y0); };
    band(Z0, -7.2, (y, hh) => { g.fillStyle = '#56803a'; g.fillRect(0, y, w, hh); for (let i = 0; i < 2500; i++) { g.fillStyle = `rgba(${40 + R() * 60},${90 + R() * 60},${30 + R() * 30},0.6)`; g.fillRect(R() * w, y + R() * hh, 2, 3); } });
    band(7.2, Z1, (y, hh) => { g.fillStyle = '#56803a'; g.fillRect(0, y, w, hh); for (let i = 0; i < 2500; i++) { g.fillStyle = `rgba(${40 + R() * 60},${90 + R() * 60},${30 + R() * 30},0.6)`; g.fillRect(R() * w, y + R() * hh, 2, 3); } });
    for (const [a, b] of [[-7.2, -5.25], [5.25, 7.2]]) band(a, b, (y, hh) => { g.fillStyle = '#b5b0a6'; g.fillRect(0, y, w, hh); g.strokeStyle = 'rgba(60,55,50,0.35)'; g.lineWidth = 2; for (let x = 0; x < w; x += 34) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + hh); g.stroke(); } for (let k = 1; k < 4; k++) { g.beginPath(); g.moveTo(0, y + k * hh / 4); g.lineTo(w, y + k * hh / 4); g.stroke(); } });
    for (const [a, b] of [[-5.25, -5.0], [5.0, 5.25]]) band(a, b, (y, hh) => { g.fillStyle = '#d6d2c8'; g.fillRect(0, y, w, hh); });
    band(-5.0, 5.0, (y, hh) => { g.fillStyle = '#3c3d40'; g.fillRect(0, y, w, hh); for (let i = 0; i < 26000; i++) { const v = 35 + R() * 55; g.fillStyle = `rgba(${v},${v},${v + 3},0.55)`; g.fillRect(R() * w, y + R() * hh, 2, 2); }
      for (let i = 0; i < 18; i++) { g.fillStyle = 'rgba(20,20,22,0.25)'; g.beginPath(); g.ellipse(R() * w, y + R() * hh, 20 + R() * 60, 10 + R() * 30, R() * 3, 0, 7); g.fill(); }
      g.fillStyle = '#ecebe4'; for (let x = 0; x < w; x += 128) g.fillRect(x, y + hh / 2 - 5, 64, 10); });
  });
  topT.wrapS = THREE.RepeatWrapping; topT.repeat.set(1 / 8, 1 / (Z1 - Z0 + 0.02)); topT.offset.set(0, -(Z0 - 0.01) / (Z1 - Z0 + 0.02));
  // Seitenwände: Schichten (v = Tiefe 0..D; Canvas-Unterkante = oben wegen flipY)
  const sideT = canvasTex(512, 1024, (g, w, h) => { const R = rng(9); const Y = d => h - d / D * h; // d = Tiefe in m
    const lay = (a, b, col, grain, gs) => { g.fillStyle = col; g.fillRect(0, Y(b), w, Y(a) - Y(b)); for (let i = 0; i < grain; i++) { const v = R(); g.fillStyle = `rgba(${v < 0.5 ? 255 : 0},${v < 0.5 ? 255 : 0},${v < 0.5 ? 255 : 0},${0.05 + R() * 0.12})`; const s = gs * (0.4 + R()); g.beginPath(); g.ellipse(R() * w, lerp(Y(b), Y(a), R()), s, s * 0.7, R() * 3, 0, 7); g.fill(); } };
    lay(0, 0.14, '#2c2c2e', 1800, 2.2);                 // Asphaltdecke
    lay(0.14, 0.24, '#3a3a3a', 900, 2.6);               // Binderschicht
    lay(0.24, 0.6, '#8a8378', 2600, 4.5);               // Schottertragschicht
    lay(0.6, 1.1, '#a39780', 2200, 3.5);                // Frostschutzkies
    lay(1.1, 2.2, '#6e5236', 2800, 3.0);                // Erdreich
    lay(2.2, D, '#4a3524', 2400, 3.0);                  // tieferer Lehm
    g.fillStyle = 'rgba(0,0,0,0.28)'; for (let i = 0; i < 60; i++) { g.fillRect(R() * w, Y(R() * D), 1 + R() * 2, 20 + R() * 80); } // Bruchrillen
    const gr = g.createLinearGradient(0, Y(1.2), 0, Y(D)); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.55)'); g.fillStyle = gr; g.fillRect(0, Y(D), w, Y(1.2) - Y(D)); });
  sideT.wrapS = THREE.RepeatWrapping; sideT.repeat.set(0.6, -1 / D); sideT.offset.set(0, 1 / D);
  const topM = new THREE.MeshStandardMaterial({map: topT, roughness: 0.92}), sideM = new THREE.MeshStandardMaterial({map: sideT, roughness: 1});
  const slab = (pts) => { const sh = new THREE.Shape(pts); const geo = new THREE.ExtrudeGeometry(sh, {depth: D, bevelEnabled: false, steps: 1});
    geo.rotateX(Math.PI / 2); // Form (x, z) -> oben y = 0, nach unten bis -D
    const m = new THREE.Mesh(geo, [topM, sideM]); m.castShadow = m.receiveShadow = true; return m; };
  // Linke Scholle: von X0 bis zur Risslinie; rechte: von der Risslinie bis X1 (lokal: Riss bei x ≈ 0)
  const L = [new THREE.Vector2(X0 - CX, Z0), ...line.map(p => p.clone()), new THREE.Vector2(X0 - CX, Z1)];
  const Rr = [new THREE.Vector2(X1 - CX, Z1), ...line.slice().reverse().map(p => p.clone()), new THREE.Vector2(X1 - CX, Z0)];
  // (Shape liegt in x/y; nach rotateX(+90°) ist Shape-y = Welt-z und die Extrusion zeigt nach unten)
  const left = new THREE.Group(), right = new THREE.Group(); root.add(left, right);
  const lm = slab(L), rm = slab(Rr); left.add(lm); right.add(rm);
  // Gesteinsboden tief unten, sehr schwache Glut
  const bottom = mesh(new THREE.PlaneGeometry(6, Z1 - Z0), new THREE.MeshStandardMaterial({color: '#1c140e', roughness: 1, emissive: '#5a1d06', emissiveIntensity: 0}), 0.3, -D + 0.02, (Z0 + Z1) / 2, root); bottom.rotation.x = -Math.PI / 2;
  const ember = new THREE.PointLight('#ff6a20', 0, 6, 2); ember.position.set(0.4, -D + 0.4, 0); root.add(ember);
  // Rohre: Wasserleitung (grau) und Leerrohr (orange) quer durch den Riss, gebrochen
  const pipes = [];
  for (const [zz, y, rad, col] of [[1.8, -1.35, 0.16, '#8c9196'], [-2.6, -0.78, 0.07, '#e07a2a'], [3.9, -1.0, 0.1, '#3d5f8a']]) {
    for (const [g, s] of [[left, -1], [right, 1]]) { const lx = line.reduce((a, p) => Math.abs(p.y - zz) < Math.abs(a.y - zz) ? p : a).x;
      const len = 3.2; const p = mesh(new THREE.CylinderGeometry(rad, rad, len, 18, 1, true), mat(col, {roughness: 0.5, side: THREE.DoubleSide}), lx + s * (len / 2 - 0.25 - 0.15 * (s > 0 ? 1 : 0)), y, zz, g); p.rotation.z = Math.PI / 2;
      mesh(new THREE.CylinderGeometry(rad * 0.82, rad * 0.82, len - 0.02, 14, 1, true), mat('#141414', {side: THREE.BackSide}), p.position.x, y, zz, g).rotation.z = Math.PI / 2; pipes.push(p); } }
  // Aufgeworfene Asphaltplatten am Rand der linken Scholle
  const plateM = [mat('#38393c', {roughness: 0.95}), mat('#2b2b2d', {roughness: 1})];
  const plates = [];
  for (let i = 0; i < 9; i++) { const zz = lerp(-4.6, 4.6, (i + r() * 0.6) / 9); const lx = line.reduce((a, p) => Math.abs(p.y - zz) < Math.abs(a.y - zz) ? p : a).x;
    const piv = new THREE.Group(); piv.position.set(lx - 0.9 - r() * 0.5, 0.0, zz); left.add(piv);
    const w = 0.6 + r() * 0.7, d = 0.5 + r() * 0.6; const pl = mesh(new THREE.BoxGeometry(w, 0.14, d), plateM[i % 2], w / 2, -0.07, 0, piv); pl.rotation.y = (r() - 0.5) * 0.4;
    plates.push({piv, ang: 0.15 + r() * 0.35, yaw: (r() - 0.5) * 0.4, t: r() * 0.8}); }
  // Haarrisse auf beiden Schollen (dunkle, verästelte Linien, wachsen)
  const hairM = mat('#141210', {roughness: 1});
  const hair = [];
  for (let i = 0; i < 40; i++) { const side = i % 2 ? right : left, sgn = i % 2 ? 1 : -1; const zz = lerp(-5, 5, r());
    const g = new THREE.Group(); g.position.set(sgn * (0.6 + r() * 0.4), 0.006, zz); side.add(g); let x = 0, z = 0, a = sgn > 0 ? (r() - 0.5) * 1.2 : Math.PI + (r() - 0.5) * 1.2;
    const n = 6 + Math.floor(r() * 8); for (let k = 0; k < n; k++) { const Ls = 0.25 + r() * 0.6; a += (r() - 0.5) * 0.9; const wd = 0.022 * (1 - k / n) + 0.006; const m = mesh(new THREE.BoxGeometry(Ls, 0.012, wd), hairM, x + Math.cos(a) * Ls / 2, 0, z + Math.sin(a) * Ls / 2, g); m.rotation.y = -a; m.castShadow = false; x += Math.cos(a) * Ls; z += Math.sin(a) * Ls; }
    hair.push({g, t: r()}); }
  // Bröckelnde Brocken (fallen in den Spalt)
  const chunkM = [mat('#2f2f31', {roughness: 1}), mat('#7b6a55', {roughness: 1}), mat('#8f8576', {roughness: 1})];
  const chunks = []; for (let i = 0; i < 70; i++) { const zz = lerp(Z0 + 0.5, Z1 - 0.5, r()); const lx = line.reduce((a, p) => Math.abs(p.y - zz) < Math.abs(a.y - zz) ? p : a).x; const s = 0.06 + r() * 0.22;
    const m = mesh(new THREE.DodecahedronGeometry(s, 0), chunkM[i % 3], 0, -99, 0, root); chunks.push({m, x: lx, z: zz, side: i % 2 ? 1 : -1, t0: r() * 5, y0: -r() * 0.8, spin: V3(r() * 5, r() * 5, r() * 5)}); }
  const dust = particles(1400, 'smoke'); dust.material.blending = THREE.NormalBlending; root.add(dust);
  const dustSrc = line.filter((p, i) => i % 4 === 0);

  return {root, left, right, line, update(T, t0, on = true) {
    root.visible = on; if (!on) return;
    const t = T - t0; // Sekunden seit dem Aufreißen
    const open = t <= 0 ? 0 : easeOut(clamp(t / 1.3)) + 0.12 * clamp((t - 1.3) / 5);
    const gap = 1.05 * open, drop = -0.55 * open, jolt = t > 0 && t < 1.5 ? 0.03 * Math.sin(t * 40) * (1 - t / 1.5) : 0;
    right.position.set(gap, drop + jolt, 0.18 * open); right.rotation.set(0.0, -0.025 * open, -0.05 * open);
    left.position.set(-0.08 * open, 0.12 * open - jolt, 0); left.rotation.set(0, 0, 0.035 * open);
    plates.forEach(p => { const k = easeOut(clamp((t - p.t * 0.6) / 0.7)); p.piv.rotation.set(0, p.yaw * k, p.ang * k); });
    hair.forEach(h => { const k = clamp((t + 0.6 - h.t * 1.5) / 1.2); h.g.scale.set(k + 0.001, 1, k + 0.001); h.g.visible = k > 0; });
    bottom.material.emissiveIntensity = 0.25 * smooth(0.8, 3, t); ember.intensity = 0.5 * smooth(0.8, 3, t) * (0.85 + 0.15 * Math.sin(T * 7));
    // Brocken lösen sich von den Kanten und fallen
    chunks.forEach(c => { const tt = t - c.t0 * (c.t0 < 1 ? 0.5 : 1) - 0.3; if (tt < 0 || open < 0.2) { c.m.visible = false; return; } c.m.visible = true;
      const base = c.side > 0 ? right.position : left.position; const x = c.x + base.x + c.side * 0.04; const y = Math.max(-D + 0.15, c.y0 + base.y - 4.9 * tt * tt);
      c.m.position.set(x + c.side * 0.12 * tt * (y > -D + 0.2 ? 1 : 0), y, c.z + base.z); c.m.rotation.set(c.spin.x * tt, c.spin.y * tt, c.spin.z * tt); });
    // Staubfahnen aus dem Spalt
    if (t > 0) updateParticles(dust, [
      ...dustSrc.map((p, i) => ({pos: V3(p.x + gap * 0.5, -0.4, p.y), r: 0.5, t0: t0 + (i % 3) * 0.1, type: 'smoke', size: 2.0, rise: 1.1, alpha: 0.45, col: [0.62, 0.55, 0.46]})),
      ...dustSrc.filter((p, i) => i % 2 === 0).map((p, i) => ({pos: V3(p.x + gap * 0.5, 0.0, p.y), r: 1.4, t0: t0 + 0.05 * i, type: 'burstSmoke', size: 2.2, rise: 0.8, alpha: 0.42, col: [0.66, 0.6, 0.5]}))], T, V3(0.5, 0, 0.3));
    dust.visible = t > 0;
  }};
}
