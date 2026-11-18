// Cockpit im Landeanflug bei Nacht: Die Flugrechner liefern Unsinn, die Anzeigen spielen verrückt,
// das Flugzeug kippt ab und stürzt auf die Lichter der Stadt zu (Schnitt vor dem Aufprall).
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex} from './lib.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const D = Math.PI / 180;

// Zeitpunkte relativ zum Beginn der Einstellung (für Ton: absolute Zeit = 38 + t)
export const CK = {WARN: 1.2, ROLL: 1.6, PULLUP: 4.0, DIVE: 5.0};

// ---------- Flugbahn (deterministisch, fest integriert) ----------
const ROLL = t => (42 * smooth(CK.ROLL, 5, t) + 26 * smooth(5, 9, t)) * D + noise1(t * 2.3, 5) * 0.05 * smooth(1.5, 4, t);
const PITCH = t => (1.8 - 9 * smooth(CK.ROLL + 0.4, 5, t) - 24 * smooth(4.5, 9, t)) * D + noise1(t * 1.9, 8) * 0.03 * smooth(1.5, 4, t);
function flight(t) {
  let x = 0, y = 400, z = 400 / Math.tan(3 * D), yaw = 0; const dt = 1 / 120;
  for (let s = 0; s < t; s += dt) {
    const r = ROLL(s), V = 72 + 3.5 * s * s * 0.25, gam = -3 * D - 30 * D * smooth(2.4, 8, s);
    yaw -= 9.81 * Math.tan(Math.min(r, 1.2)) / V * dt * 0.8;
    x += Math.sin(-yaw) * Math.cos(gam) * V * dt; z -= Math.cos(yaw) * Math.cos(gam) * V * dt; y += Math.sin(gam) * V * dt;
  }
  return {x, y, z, yaw, roll: ROLL(t), pitch: PITCH(t), V: 72 + 3.5 * t * t * 0.25};
}

// ---------- Lichtpunkte (Stadt, Pistenbefeuerung) ----------
function lightPoints(pos, col, size, opt = {}) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setAttribute('col', new THREE.Float32BufferAttribute(col, 3));
  geo.setAttribute('size', new THREE.Float32BufferAttribute(size, 1));
  if (opt.phase) geo.setAttribute('phase', new THREE.Float32BufferAttribute(opt.phase, 1));
  else geo.setAttribute('phase', new THREE.Float32BufferAttribute(new Float32Array(size.length).fill(-1), 1));
  const m = new THREE.ShaderMaterial({
    uniforms: {focal: {value: 1200}, time: {value: 0}, maxPx: {value: opt.maxPx || 14}, gain: {value: opt.gain || 1}, fogL: {value: opt.fogL || 16000}},
    vertexShader: `uniform float focal, time, maxPx, fogL; attribute vec3 col; attribute float size, phase; varying vec3 vC; varying float vA;
      void main(){ vec4 mv = modelViewMatrix * vec4(position, 1.); float d = -mv.z; float px = size * focal / max(d, 1.);
        float a = clamp(px / 1.6, 0.0, 1.0) * exp(-d / fogL);
        if (phase >= 0.0) { float p = fract(time * 2.0 - phase); a *= smoothstep(0.08, 0.0, p) * 1.0; }
        gl_PointSize = clamp(px, 1.6, maxPx); vC = col; vA = a; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform float gain; varying vec3 vC; varying float vA;
      void main(){ vec2 q = gl_PointCoord - 0.5; float r = length(q) * 2.0; if (r > 1.0) discard;
        float a = exp(-r * r * 5.0) + 0.6 * exp(-r * r * 40.0); gl_FragColor = vec4(vC * a * vA * gain, 1.0); }`,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending});
  const p = new THREE.Points(geo, m); p.frustumCulled = false; return p;
}
// Dichte der Stadt (0..1)
function density(x, z) {
  const c1 = Math.hypot((x - 1500) / 11000, (z - 3000) / 10000), c2 = Math.hypot((x + 7000) / 5000, (z - 9000) / 4500), c3 = Math.hypot((x - 8000) / 4000, (z + 4000) / 4000);
  let d = Math.max(1 - c1, 0.8 * (1 - c2), 0.7 * (1 - c3), 0) * 1.3;
  d *= 0.6 + 0.4 * Math.sin(x * 0.0011 + Math.sin(z * 0.0007) * 2) * Math.sin(z * 0.0013 + 1.3);
  if (Math.abs(x + 300) < 1300 && z < 900 && z > -3800) d *= 0.04; // Flughafengelände
  if (Math.abs(x - 900 - Math.sin(z * 0.0004) * 1500) < 160) d = 0; // Fluss
  return clamp(d * 1.6);
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#020308');
  // Himmel: Abendrot knapp über dem Horizont, darüber tiefes Blau mit Sternen
  const sky = new THREE.Mesh(new THREE.SphereGeometry(40000, 48, 24), new THREE.ShaderMaterial({side: THREE.BackSide, depthWrite: false, fog: false,
    vertexShader: 'varying vec3 vP; void main(){ vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }',
    fragmentShader: `varying vec3 vP; float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
      void main(){ vec3 d = normalize(vP); float e = d.y; float ahead = 0.5 + 0.5 * dot(normalize(d.xz + 1e-4), normalize(vec2(-0.4, -1.0)));
        vec3 top = vec3(0.006, 0.010, 0.030), mid = vec3(0.04, 0.035, 0.10), hor = mix(vec3(0.10, 0.05, 0.09), vec3(0.55, 0.20, 0.08), ahead * ahead);
        vec3 c = mix(hor, mid, smoothstep(0.0, 0.08, e)); c = mix(c, top, smoothstep(0.06, 0.5, e));
        c += vec3(0.20, 0.09, 0.03) * exp(-max(e, 0.0) * 60.0) * ahead; // Glut am Horizont
        if (e < 0.0) c = mix(hor * 0.6, vec3(0.03, 0.025, 0.03), smoothstep(0.0, -0.05, e));
        vec2 g = floor(vec2(atan(d.z, d.x) * 300.0, e * 600.0)); float s = h(g); c += vec3(0.8, 0.85, 1.0) * step(0.9985, s) * smoothstep(0.05, 0.3, e) * (0.4 + 0.6 * h(g + 3.1));
        gl_FragColor = vec4(c, 1.0); }`}));
  scene.add(sky);
  // Boden mit Lichtglocke über der Stadt
  const glow = canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
    const im = g.getImageData(0, 0, w, h);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const x = (i / w - 0.5) * 50000, z = (j / h - 0.5) * 50000; const d = density(x, z);
      const k = (j * w + i) * 4; im.data[k] = 255 * d * 0.55; im.data[k + 1] = 255 * d * 0.30; im.data[k + 2] = 255 * d * 0.14; im.data[k + 3] = 255; }
    g.putImageData(im, 0, 0); g.filter = 'blur(3px)'; g.drawImage(g.canvas, 0, 0);
  });
  // Detailtextur einer Kachel Stadt (4 x 4 Blöcke à 170 m): Straßen mit Laternen, Dächer, Fenster, Autos
  const detail = canvasTex(1024, 1024, (g, w, h) => {
    const r = rng(33); g.fillStyle = '#040405'; g.fillRect(0, 0, w, h); const B = w / 4;
    for (let bx = 0; bx < 4; bx++) for (let bz = 0; bz < 4; bz++) {
      const x0 = bx * B + 10, z0 = bz * B + 10, park = r() < 0.12;
      if (park) { g.fillStyle = '#060805'; g.fillRect(x0, z0, B - 20, B - 20); continue; }
      for (let i = 0; i < 7; i++) { const bw = 30 + r() * 70, bh = 30 + r() * 70, x = x0 + r() * (B - 20 - bw), z = z0 + r() * (B - 20 - bh);
        g.fillStyle = `rgb(${12 + r() * 10},${12 + r() * 10},${14 + r() * 12})`; g.fillRect(x, z, bw, bh);
        for (let k = 0; k < bw * bh / 140; k++) { g.fillStyle = r() < 0.7 ? 'rgba(255,205,140,0.85)' : 'rgba(200,220,255,0.8)'; g.fillRect(x + r() * bw, z + r() * bh, 2, 2); } }
    }
    for (let i = 0; i <= 4; i++) { const p = i * B;
      for (const [x, y, ww, hh] of [[p - 5, 0, 10, h], [0, p - 5, w, 10]]) { g.fillStyle = 'rgba(120,62,22,0.9)'; g.fillRect(x, y, ww, hh); }
      for (let q = 0; q < w; q += 26) { for (const [x, y] of [[p - 9, q], [p + 7, q + 13], [q, p - 9], [q + 13, p + 7]]) { const gr = g.createRadialGradient(x, y, 0, x, y, 9); gr.addColorStop(0, 'rgba(255,190,110,1)'); gr.addColorStop(1, 'rgba(255,140,40,0)'); g.fillStyle = gr; g.fillRect(x - 9, y - 9, 18, 18); } }
      for (let q = 0; q < w; q += 9) if (r() < 0.25) { const red = r() < 0.5; g.fillStyle = red ? '#ff2a18' : '#fff3d8'; g.fillRect(p + (red ? -3 : 1), q, 2, 3); g.fillRect(q, p + (red ? -3 : 1), 3, 2); }
    }
  });
  detail.wrapS = detail.wrapT = THREE.RepeatWrapping; detail.anisotropy = 16;
  const groundMat = new THREE.ShaderMaterial({uniforms: {glow: {value: glow}, detail: {value: detail}, fogC: {value: new THREE.Color('#120d16')}},
    vertexShader: 'varying vec3 vW; varying vec2 vUv; void main(){ vUv = uv; vec4 w = modelMatrix * vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: `uniform sampler2D glow, detail; uniform vec3 fogC; varying vec3 vW; varying vec2 vUv;
      void main(){ vec3 gl = texture2D(glow, vUv).rgb; float dens = clamp(gl.r * 2.6, 0.0, 1.0);
        vec3 d1 = texture2D(detail, vW.xz / 680.0).rgb, d2 = texture2D(detail, vW.zx / 1130.0 + 0.37).rgb;
        vec3 c = max(d1, d2 * 0.8) * dens * 1.7 + gl * 0.22;
        float dist = length(vW - cameraPosition); float f = 1.0 - exp(-pow(dist * 0.000075, 2.0));
        gl_FragColor = vec4(mix(c, fogC, f), 1.0); }`});
  const ground = mesh(new THREE.PlaneGeometry(50000, 50000), groundMat, 0, 0, 0, scene);
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = false; ground.castShadow = false;
  scene.fog = new THREE.FogExp2('#120d16', 0.000075);

  // Stadtlichter: Straßenraster mit Laternen, Hauptstraßen, Fenster, Autos
  {
    const P = [], C = [], S = [], r = rng(77);
    const sod = [1.0, 0.62, 0.28], led = [0.85, 0.9, 1.0], warm = [1.0, 0.82, 0.55];
    for (let gx = -24000; gx < 24000; gx += 170) for (let gz = -24000; gz < 24000; gz += 170) {
      const d = density(gx, gz); if (d < 0.05 || r() > d * 1.2) continue;
      const c = (Math.sin(gx * 0.0003) + Math.cos(gz * 0.00025)) > 0 ? sod : led;
      for (let k = 0; k < 170; k += 34) { // zwei Straßen pro Block
        if (r() < d) { P.push(gx + k, 4, gz); C.push(...c); S.push(5); }
        if (r() < d) { P.push(gx, 4, gz + k); C.push(...c); S.push(5); }
      }
      const nw = Math.floor(d * 6); for (let k = 0; k < nw; k++) { P.push(gx + 20 + r() * 130, 3 + r() * 30, gz + 20 + r() * 130); const w = r() < 0.7 ? warm : led; C.push(w[0] * 0.7, w[1] * 0.7, w[2] * 0.7); S.push(3.5); }
    }
    // Hauptstraßen und Autobahn (hell, durchgehend)
    for (const [ax, az, bx, bz, c] of [[-20000, 3000, 20000, 1500, sod], [-3000, 20000, 5000, -20000, sod], [6000, 18000, 9000, -18000, led], [-16000, -9000, 18000, -6000, sod]]) {
      const n = Math.hypot(bx - ax, bz - az) / 25; for (let i = 0; i < n; i++) { const u = i / n, x = lerp(ax, bx, u), z = lerp(az, bz, u); if (Math.abs(x + 300) < 1300 && z < 900 && z > -3800) continue;
        P.push(x - 12, 5, z); C.push(...c); S.push(7); P.push(x + 12, 5, z); C.push(...c); S.push(7);
        if (r() < 0.35) { P.push(x + (r() < 0.5 ? -4 : 4), 1, z); const red = r() < 0.5; C.push(red ? 1 : 1, red ? 0.1 : 0.95, red ? 0.08 : 0.85); S.push(3.5); } }
    }
    // Hochhäuser mit roten Warnlichtern
    for (let i = 0; i < 60; i++) { const x = 2500 + (r() - 0.5) * 6000, z = -1500 + (r() - 0.5) * 5000; if (density(x, z) < 0.5) continue; P.push(x, 120 + r() * 120, z); C.push(1, 0.08, 0.05); S.push(9); }
    const city = lightPoints(P, C, S, {maxPx: 9, gain: 1.4}); scene.add(city); scene.userData.city = city;
  }
  // Pistenbefeuerung: Anflugbefeuerung mit Lauffeuer, Schwelle grün, Ränder weiß, Ende rot, PAPI
  {
    const P = [], C = [], S = [], PH = [];
    const add = (x, z, c, s, ph = -1) => { P.push(x, 1.2, z); C.push(...c); S.push(s); PH.push(ph); };
    const W = [1.0, 0.92, 0.78], G = [0.2, 1.0, 0.45], R = [1.0, 0.12, 0.08];
    for (let z = 30; z <= 900; z += 30) { for (let k = -2; k <= 2; k++) add(k * 1.2, z, W, 3); if (z === 300) for (let k = -15; k <= 15; k++) add(k * 1.5, z, W, 3); add(0, z, [1, 1, 1], 6, 1 - z / 900); }
    for (let k = -22; k <= 22; k++) add(k, 0, G, 3.2);
    for (let z = 0; z >= -3000; z -= 60) { add(-23, z, W, 3); add(23, z, W, 3); }
    for (let z = -15; z >= -3000; z -= 15) add(0, z, z < -2100 ? (Math.floor(-z / 15) % 2 ? R : W) : W, 2);
    for (let z = -30; z >= -900; z -= 30) for (const s of [-1, 1]) for (let k = 0; k < 3; k++) add(s * (10 + k * 1.5), z, W, 1.6);
    for (let k = -22; k <= 22; k++) add(k, -3000, R, 3);
    for (let k = 0; k < 4; k++) add(-40 - k * 9, -300, k < 2 ? R : W, 4.5);
    // Rollwege blau, Vorfeld mit Terminal
    for (let z = -100; z >= -2900; z -= 40) add(-160, z, [0.2, 0.35, 1.0], 2.2);
    const rr = rng(5); for (let i = 0; i < 260; i++) { P.push(-700 + rr() * 500, 2 + rr() * 18, -600 - rr() * 1800); C.push(1, 0.85, 0.6); S.push(3); PH.push(-1); }
    const rw = lightPoints(P, C, S, {phase: PH, maxPx: 16, gain: 2.2, fogL: 20000}); scene.add(rw); scene.userData.rw = rw;
  }
  // Ein paar Wolkenfetzen unterhalb der Reiseflughöhe, von unten orange angeleuchtet
  const cloudTex = canvasTex(256, 128, (g, w, h) => { const r = rng(9); for (let i = 0; i < 40; i++) { const x = 30 + r() * 196, y = 40 + r() * 50, rad = 20 + r() * 30; const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, 'rgba(255,255,255,0.22)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); } });
  { const r = rng(21); for (let i = 0; i < 26; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({map: cloudTex, color: '#6a4a48', transparent: true, opacity: 0.55, depthWrite: false, fog: true}));
    s.position.set((r() - 0.5) * 3000, 330 + r() * 260, 7000 - r() * 9000); s.scale.set(500 + r() * 600, 140 + r() * 120, 1); scene.add(s); } }

  // ---------- Cockpit (lokale Koordinaten: x rechts, y oben, -z nach vorn, Augen der Piloten bei y=0) ----------
  const ac = new THREE.Group(); scene.add(ac);
  const shell = mat('#2a2d32', {roughness: 0.7}), dark = mat('#141619', {roughness: 0.8}), panelM = mat('#33373d', {roughness: 0.6}), trim = mat('#5a5f66', {roughness: 0.5, metalness: 0.3});
  // Glareshield (Blendschutz) mit FCU und Warnleuchten
  mesh(new THREE.BoxGeometry(2.1, 0.09, 0.5), dark, 0, -0.27, -0.86, ac);
  mesh(new THREE.BoxGeometry(2.1, 0.11, 0.03), shell, 0, -0.30, -0.6, ac);
  const fcuC = document.createElement('canvas'); fcuC.width = 1024; fcuC.height = 96; const fcuT = new THREE.CanvasTexture(fcuC); fcuT.colorSpace = THREE.SRGBColorSpace;
  mesh(new THREE.PlaneGeometry(1.0, 0.094), new THREE.MeshStandardMaterial({map: fcuT, emissive: '#ffffff', emissiveMap: fcuT, emissiveIntensity: 0.9, roughness: 0.5}), 0, -0.30, -0.583, ac);
  const warnLights = [];
  for (const sx of [-0.78, 0.78]) {
    const mw = new THREE.MeshStandardMaterial({color: '#300', emissive: '#ff1a10', emissiveIntensity: 0.2}); warnLights.push(mw);
    mesh(new THREE.BoxGeometry(0.06, 0.045, 0.02), mw, sx, -0.298, -0.585, ac);
    const mc = new THREE.MeshStandardMaterial({color: '#320', emissive: '#ffa010', emissiveIntensity: 0.15}); warnLights.push(mc);
    mesh(new THREE.BoxGeometry(0.06, 0.045, 0.02), mc, sx + (sx < 0 ? 0.08 : -0.08), -0.298, -0.585, ac);
  }
  // Instrumententafel mit sechs Bildschirmen
  mesh(new THREE.BoxGeometry(2.1, 0.5, 0.06), panelM, 0, -0.58, -0.96, ac).rotation.x = -0.12;
  const screens = {};
  const mkScreen = (name, x, y, z, w = 0.2, h = 0.2) => {
    const c = document.createElement('canvas'); c.width = 512; c.height = 512; const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    const m = mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({map: t, toneMapped: false}), x, y, z, ac); m.rotation.x = -0.12;
    mesh(new THREE.BoxGeometry(w + 0.03, h + 0.03, 0.015), dark, x, y - 0.001, z - 0.009, ac).rotation.x = -0.12;
    screens[name] = {c, g: c.getContext('2d'), t, m}; return screens[name];
  };
  mkScreen('ndL', -0.74, -0.47, -0.92); mkScreen('pfdL', -0.47, -0.465, -0.92, 0.24, 0.24); mkScreen('ewd', 0, -0.465, -0.92, 0.24, 0.24); mkScreen('sd', 0, -0.70, -0.89);
  mkScreen('pfdR', 0.47, -0.465, -0.92, 0.24, 0.24); mkScreen('ndR', 0.74, -0.47, -0.92);
  // Mittelkonsole (Pedestal) mit Schubhebeln
  mesh(new THREE.BoxGeometry(0.42, 0.28, 1.1), panelM, 0, -0.86, -0.35, ac);
  const pedC = canvasTex(256, 512, (g, w, h) => { g.fillStyle = '#2c3036'; g.fillRect(0, 0, w, h); const r = rng(4);
    for (let y = 20; y < h; y += 44) for (let x = 14; x < w - 20; x += 38) { g.fillStyle = '#16181b'; g.fillRect(x, y, 26, 22); if (r() < 0.4) { g.fillStyle = r() < 0.5 ? '#3fd16a' : '#e8e8e8'; g.fillRect(x + 6, y + 6, 14, 4); } } });
  mesh(new THREE.PlaneGeometry(0.4, 1.05), new THREE.MeshStandardMaterial({map: pedC, emissive: '#ffffff', emissiveMap: pedC, emissiveIntensity: 0.25}), 0, -0.719, -0.35, ac).rotation.x = -Math.PI / 2;
  const levers = []; for (const sx of [-0.06, 0.06]) { const l = new THREE.Group(); l.position.set(sx, -0.72, -0.55); ac.add(l); mesh(new THREE.BoxGeometry(0.03, 0.18, 0.03), trim, 0, 0.09, 0, l); mesh(new THREE.BoxGeometry(0.07, 0.035, 0.05), dark, 0, 0.18, 0, l); l.rotation.x = -0.35; levers.push(l); }
  // Rahmen: Mittelstrebe, Seitenstreben, Decke mit Overhead-Panel, Seitenwände
  const post = (x, w, ang) => { const p = mesh(new THREE.BoxGeometry(w, 0.98, 0.07), shell, x, 0.2, -0.96, ac); p.rotation.x = 0.35; p.rotation.z = ang; return p; };
  post(0, 0.07, 0); post(-0.66, 0.11, -0.12); post(0.66, 0.11, 0.12); post(-1.02, 0.14, -0.35); post(1.02, 0.14, 0.35);
  mesh(new THREE.BoxGeometry(2.4, 0.08, 0.1), shell, 0, 0.64, -0.8, ac);                // oberer Fensterrahmen
  mesh(new THREE.BoxGeometry(2.4, 0.06, 0.08), shell, 0, -0.235, -1.06, ac);              // unterer Fensterrahmen
  mesh(new THREE.BoxGeometry(2.6, 0.3, 0.6), shell, 0, 0.82, -0.7, ac);                     // Stirn über den Scheiben
  mesh(new THREE.PlaneGeometry(2.6, 3.2), dark, 0, -1.0, 0, ac).rotation.x = -Math.PI / 2; // Boden
  // Sonnenblenden (getönt, hochgeklappt) und Standby-Kompass an der Mittelstrebe
  for (const sx of [-0.45, 0.45]) { const v = mesh(new THREE.BoxGeometry(0.5, 0.2, 0.01), new THREE.MeshStandardMaterial({color: '#1d2a22', transparent: true, opacity: 0.85, roughness: 0.3}), sx, 0.6, -0.72, ac); v.rotation.x = -0.9; }
  mesh(new THREE.BoxGeometry(0.09, 0.08, 0.07), dark, 0, 0.56, -0.86, ac);
  mesh(new THREE.CircleGeometry(0.028, 16), new THREE.MeshStandardMaterial({color: '#ddd', emissive: '#ffe8c0', emissiveIntensity: 0.3}), 0, 0.56, -0.824, ac);
  mesh(new THREE.BoxGeometry(2.6, 0.3, 0.1), dark, 0, -0.95, -0.95, ac);                   // Fußraum vorn
  for (const s of [-1, 1]) { const w = mesh(new THREE.BoxGeometry(0.06, 2.0, 2.6), shell, s * 1.25, -0.05, 0.1, ac); w.rotation.z = s * 0.12;
    const side = mesh(new THREE.BoxGeometry(0.05, 0.4, 0.3), dark, s * 1.08, -0.42, -0.4, ac); }
  const ovC = canvasTex(512, 1024, (g, w, h) => { g.fillStyle = '#3a3e45'; g.fillRect(0, 0, w, h); const r = rng(8);
    for (let y = 30; y < h - 30; y += 120) { g.strokeStyle = '#5c616a'; g.lineWidth = 3; g.strokeRect(16, y - 10, w - 32, 110); g.fillStyle = '#d9dde3'; g.font = '14px Plex'; g.fillText(['ELEC', 'HYD', 'FUEL', 'AIR COND', 'ANTI ICE', 'EXT LT', 'APU', 'SIGNS'][Math.floor(y / 120) % 8], 26, y + 6);
      for (let x = 30; x < w - 40; x += 62) { g.fillStyle = '#1d1f23'; g.fillRect(x, y + 20, 44, 40); g.strokeStyle = '#8a9099'; g.lineWidth = 2; g.strokeRect(x, y + 20, 44, 40);
        if (r() < 0.25) { g.fillStyle = r() < 0.6 ? '#ffb020' : '#4aa8ff'; g.fillRect(x + 6, y + 26, 32, 10); } g.fillStyle = '#bfc4cb'; g.fillRect(x + 18, y + 66, 8, 16); } } });
  const ovM = new THREE.MeshStandardMaterial({map: ovC, emissive: '#ffffff', emissiveMap: ovC, emissiveIntensity: 0.12, roughness: 0.6});
  const ov = mesh(new THREE.PlaneGeometry(0.9, 1.5), ovM, 0, 0.78, -0.05, ac); ov.rotation.x = Math.PI / 2 + 0.28;
  mesh(new THREE.PlaneGeometry(2.6, 2.4), shell, 0, 0.9, 0.4, ac).rotation.x = Math.PI / 2;
  // Sitze und Piloten (von hinten, Hemd mit Schulterklappen, Headset)
  const shirt = mat('#c3cdd8', {roughness: 0.85}), skin = mat('#c99777'), hairs = [mat('#2b211b', {roughness: 0.9}), mat('#8a8d91', {roughness: 0.9})];
  const pilots = [];
  for (const [s, hi] of [[-1, 1], [1, 0]]) {
    const g = new THREE.Group(); g.position.set(s * 0.47, 0.05, 0.1); ac.add(g);
    mesh(new THREE.BoxGeometry(0.5, 0.55, 0.12), mat('#3a3330', {roughness: 0.95}), 0, -0.62, 0.22, g);           // Rückenlehne
        const body = new THREE.Group(); g.add(body);
    mesh(new THREE.CapsuleGeometry(0.15, 0.3, 4, 12), shirt, 0, -0.42, 0.02, body).scale.set(1.25, 1, 0.75);
    for (const e of [-1, 1]) { mesh(new THREE.BoxGeometry(0.1, 0.012, 0.06), mat('#111'), e * 0.16, -0.2, 0.02, body); mesh(new THREE.BoxGeometry(0.1, 0.006, 0.062), mat('#d8b24a', {metalness: 0.8, roughness: 0.3}), e * 0.16, -0.193, 0.02, body); }
    const head = new THREE.Group(); head.position.set(0, -0.04, 0.0); body.add(head);
    mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.1, 10), skin, 0, -0.09, 0, head);
    mesh(new THREE.SphereGeometry(0.11, 18, 14), skin, 0, 0.03, 0, head).scale.set(0.92, 1.1, 1);
    mesh(new THREE.SphereGeometry(0.117, 18, 14, 0, Math.PI * 2, 0, Math.PI * 0.62), hairs[hi], 0, 0.04, 0.012, head).rotation.x = -0.35;
    const band = mesh(new THREE.TorusGeometry(0.12, 0.012, 6, 20, Math.PI), mat('#1a1a1a'), 0, 0.04, 0, head);
    for (const e of [-1, 1]) mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.035, 14), mat('#202022'), e * 0.115, 0.0, 0, head).rotation.z = Math.PI / 2;
    const mic = mesh(new THREE.BoxGeometry(0.008, 0.008, 0.12), mat('#202022'), s * -0.0 + -s * 0.1, -0.05, -0.06, head); mic.rotation.y = s * 0.6;
    // Arme: Kapitän links am Sidestick, rechte Hand am Schubhebel; Erster Offizier umgekehrt
    const arms = [];
    for (const e of [-1, 1]) { const sh = new THREE.Group(); sh.position.set(e * 0.21, -0.25, 0.0); body.add(sh);
      mesh(new THREE.CapsuleGeometry(0.05, 0.24, 4, 8), shirt, 0, -0.15, 0, sh); const fore = new THREE.Group(); fore.position.y = -0.3; sh.add(fore);
      mesh(new THREE.CapsuleGeometry(0.044, 0.22, 4, 8), shirt, 0, -0.12, 0, fore); mesh(new THREE.SphereGeometry(0.048, 10, 8), skin, 0, -0.27, 0, fore);
      sh.rotation.x = 0.55; fore.rotation.x = 0.9; sh.rotation.z = e * 0.1; arms.push({sh, fore, e}); }
    pilots.push({g, body, head, arms, s});
  }
  // Sidesticks
  for (const s of [-1, 1]) { const st = new THREE.Group(); st.position.set(s * 0.92, -0.62, -0.35); ac.add(st); mesh(new THREE.CylinderGeometry(0.018, 0.022, 0.16, 10), dark, 0, 0.08, 0, st); }
  // Lichter im Cockpit
  scene.add(new THREE.AmbientLight('#4a5a7a', 0.25));
  const dispLight = new THREE.PointLight('#9fc2ff', 1.2, 2.5, 1.5); dispLight.position.set(0, -0.35, -0.6); ac.add(dispLight);
  const flood = new THREE.PointLight('#ffcf9a', 0.35, 2.5, 1.5); flood.position.set(0, 0.2, 0.6); ac.add(flood);
  const redL = new THREE.PointLight('#ff2010', 0, 3, 1.4); redL.position.set(0, -0.2, -0.55); ac.add(redL);
  const cityBounce = new THREE.PointLight('#ff9a50', 0.6, 4, 1.2); cityBounce.position.set(0, 0.3, -1.4); ac.add(cityBounce);

  const camera = new THREE.PerspectiveCamera(68, 1080 / 1920, 0.02, 60000);
  ac.add(camera);

  // ---------- Bildschirminhalte ----------
  const GL = '7#%Ø9?∑Ξ&@!0x▒▓'; let R = rng(1);
  const junk = n => { let s = ''; for (let i = 0; i < n; i++) s += GL[Math.floor(R() * GL.length)]; return s; };
  const num = (v, k) => R() < k * 0.85 ? junk(String(v).length) : String(v);
  function glitchSlices(sc, k) {
    const {g, c} = sc; const n = Math.floor(k * 6);
    for (let i = 0; i < n; i++) { const y = R() * 512, h = 6 + R() * 50; g.drawImage(c, 0, y, 512, h, (R() - 0.5) * 120 * k, y, 512, h); }
    if (R() < k * 0.3) { g.fillStyle = `rgba(${R() < 0.5 ? '255,0,80' : '0,255,200'},0.25)`; g.fillRect(0, R() * 512, 512, 8 + R() * 30); }
  }
  function pfd(sc, st, k, t, T) {
    const {g} = sc; g.save(); g.fillStyle = '#000'; g.fillRect(0, 0, 512, 512);
    const roll = st.roll + (R() - 0.5) * k * k * 1.6, pitch = st.pitch / D + (R() - 0.5) * k * 40;
    // künstlicher Horizont
    g.save(); g.beginPath(); g.rect(130, 80, 252, 290); g.clip(); g.translate(256, 225); g.rotate(-roll); g.translate(0, pitch * 7);
    g.fillStyle = '#1f78d6'; g.fillRect(-500, -900, 1000, 900); g.fillStyle = '#7d4f22'; g.fillRect(-500, 0, 1000, 900);
    g.strokeStyle = '#fff'; g.lineWidth = 3; g.beginPath(); g.moveTo(-500, 0); g.lineTo(500, 0); g.stroke();
    g.lineWidth = 2; g.fillStyle = '#fff'; g.font = '16px Plex'; for (let p = -30; p <= 30; p += 5) { if (!p) continue; const y = -p * 7, w = p % 10 ? 22 : 50; g.beginPath(); g.moveTo(-w, y); g.lineTo(w, y); g.stroke(); if (!(p % 10)) g.fillText(num(Math.abs(p), k), w + 6, y + 5); }
    g.restore();
    g.strokeStyle = '#ffd60a'; g.lineWidth = 6; g.beginPath(); g.moveTo(170, 225); g.lineTo(225, 225); g.lineTo(225, 240); g.moveTo(342, 225); g.lineTo(287, 225); g.lineTo(287, 240); g.stroke(); g.fillStyle = '#ffd60a'; g.fillRect(250, 220, 12, 10);
    // Fahrttanzeige und Höhenmesser
    const spd = Math.round(st.V * 1.944), alt = Math.round(st.y * 3.28);
    for (const [x0, val, step, scale] of [[40, spd, 10, 4], [400, alt, 100, 0.5]]) {
      g.fillStyle = '#3c3f44'; g.fillRect(x0, 80, 78, 290); g.fillStyle = '#fff'; g.font = '19px Plex'; g.textAlign = 'right';
      const off = k > 0.4 ? (R() - 0.5) * 400 * k : 0;
      for (let v = Math.floor((val - 300) / step) * step; v < val + 300; v += step) { const y = 225 - (v - val + off) * scale * (step === 10 ? 1 : 1); if (y < 88 || y > 365) continue; g.fillText(num(v, k), x0 + 66, y + 6); g.fillRect(x0 + 70, y, 8, 2); }
      g.fillStyle = '#000'; g.fillRect(x0 + 4, 205, 74, 40); g.strokeStyle = '#ffd60a'; g.lineWidth = 2; g.strokeRect(x0 + 4, 205, 74, 40);
      g.fillStyle = k > 0.3 && R() < 0.5 ? '#ff3b30' : '#3cff6a'; g.font = '500 24px Plex'; g.fillText(num(val, k), x0 + 72, 234);
      if (k > 0.45 && Math.sin(T * 12) > 0) { g.fillStyle = '#ff2a1a'; g.font = '600 30px Plex'; g.textAlign = 'center'; g.fillText(step === 10 ? 'SPD' : 'ALT', x0 + 39, 150); }
    }
    g.textAlign = 'center'; g.fillStyle = '#3cff6a'; g.font = '18px Plex';
    g.fillText(k > 0.6 ? junk(5) + '  ' + junk(3) + '  ' + junk(4) : 'SPEED   G/S   LOC', 256, 40); g.fillStyle = '#fff'; g.fillText(k > 0.2 ? 'AP ' + junk(2) : 'AP1  A/THR', 256, 64);
    g.fillStyle = '#3c3f44'; g.fillRect(150, 420, 212, 50); g.fillStyle = '#fff'; g.font = '20px Plex'; g.fillText(num(String(Math.round(((-st.yaw / D) % 360 + 360 + 260) % 360)).padStart(3, '0'), k), 256, 452);
    if (k > 0.5 && t > CK.ROLL) { g.fillStyle = '#ff2a1a'; g.font = '600 34px Plex'; if (Math.sin(T * 9) > -0.2) g.fillText('ATT', 256, 140); }
    if (t > CK.PULLUP && Math.sin(T * 7) > -0.3) { g.fillStyle = '#ff1a10'; g.fillRect(150, 255, 212, 60); g.fillStyle = '#fff'; g.font = '700 40px Plex'; g.fillText('PULL UP', 256, 299); }
    g.restore(); glitchSlices(sc, k);
  }
  function nd(sc, st, k, t, T) {
    const {g} = sc; g.save(); g.fillStyle = '#000'; g.fillRect(0, 0, 512, 512);
    g.translate(256, 400); g.rotate(-st.yaw + (R() - 0.5) * k * 2);
    g.strokeStyle = '#fff'; g.lineWidth = 2; g.beginPath(); g.arc(0, 0, 300, -Math.PI * 0.85, -Math.PI * 0.15); g.stroke();
    g.font = '18px Plex'; g.fillStyle = '#fff'; g.textAlign = 'center';
    for (let a = 0; a < 36; a++) { const an = a * 10 * D - Math.PI / 2; g.save(); g.rotate(an + Math.PI / 2); g.fillRect(-1, -300, 2, a % 3 ? 10 : 18); if (!(a % 3)) g.fillText(num(String(a).padStart(2, '0'), k), 0, -270); g.restore(); }
    // Terrain-Anzeige (EGPWS): grün, gelb, rot je näher der Boden
    const terr = smooth(2.5, 7, t); const rr = rng(Math.floor(T * 6));
    for (let i = 0; i < 260; i++) { const x = (rr() - 0.5) * 520, y = -rr() * 330; const v = rr() + terr * 0.9 - (-y) / 600; g.fillStyle = v > 1.2 ? '#ff2a1a' : v > 0.9 ? '#ffd60a' : v > 0.6 ? '#1fa64a' : 'rgba(0,0,0,0)'; g.fillRect(x, y, 6, 6); }
    g.strokeStyle = '#ff3cff'; g.lineWidth = 3; g.beginPath(); g.moveTo(0, 0); g.lineTo(0, -320); g.stroke();
    g.fillStyle = '#25d8ff'; g.font = '16px Plex'; g.fillText(k > 0.3 ? junk(5) : 'RW25R', 14, -200);
    g.restore();
    g.fillStyle = '#ffd60a'; g.beginPath(); g.moveTo(256, 385); g.lineTo(244, 415); g.lineTo(268, 415); g.fill();
    g.fillStyle = '#3cff6a'; g.font = '18px Plex'; g.textAlign = 'left'; g.fillText('GS ' + num(Math.round(st.V * 1.944), k), 16, 30); g.fillText('TAS ' + num(Math.round(st.V * 1.95), k), 16, 54);
    if (t > CK.PULLUP && Math.sin(T * 7) > -0.3) { g.fillStyle = '#ff2a1a'; g.font = '600 26px Plex'; g.textAlign = 'center'; g.fillText('TERRAIN AHEAD', 256, 480); }
    glitchSlices(sc, k);
  }
  function ewd(sc, st, k, t, T) {
    const {g} = sc; g.fillStyle = '#000'; g.fillRect(0, 0, 512, 512);
    for (const cx of [140, 372]) { g.strokeStyle = '#fff'; g.lineWidth = 3; g.beginPath(); g.arc(cx, 120, 80, Math.PI * 0.8, Math.PI * 2.1); g.stroke();
      const n1 = 0.55 + (k > 0.3 ? (R() - 0.5) * k : 0); g.strokeStyle = '#3cff6a'; g.lineWidth = 5; g.beginPath(); g.moveTo(cx, 120); g.lineTo(cx + Math.cos(Math.PI * (0.8 + n1 * 1.3)) * 70, 120 + Math.sin(Math.PI * (0.8 + n1 * 1.3)) * 70); g.stroke();
      g.fillStyle = '#3cff6a'; g.font = '500 30px Plex'; g.textAlign = 'center'; g.fillText(num((n1 * 100).toFixed(1), k), cx, 190); }
    g.fillStyle = '#fff'; g.fillRect(16, 262, 480, 2);
    const lines = [['F/CTL ELAC 1+2 FAULT', '#ff2a1a', CK.WARN], ['NAV ALT DISAGREE', '#ffb020', CK.WARN + 0.5], ['F/CTL DIRECT LAW', '#ff2a1a', CK.ROLL + 0.3], ['NAV ADR 1+2+3 FAULT', '#ffb020', CK.ROLL + 1.1], ['ENG 1+2 FADEC FAULT', '#ff2a1a', CK.PULLUP - 0.5], [junk(18), '#ff2a1a', CK.PULLUP + 0.6]];
    g.textAlign = 'left'; g.font = '500 25px Plex'; let y = 300;
    for (const [txt, c, at] of lines) { if (t < at) continue; g.fillStyle = c; if (!(c === '#ff2a1a' && t - at < 1.2 && Math.sin(T * 14) < -0.2)) g.fillText(R() < k * 0.2 ? junk(txt.length) : txt, 22, y); y += 34; }
    if (t < CK.WARN) { g.fillStyle = '#3cff6a'; g.font = '22px Plex'; g.fillText('LDG LDG GEAR DN', 22, 300); g.fillText('SIGNS ON  SPLRS ARM', 22, 334); }
    glitchSlices(sc, k * 0.8);
  }
  function sd(sc, st, k, t, T) {
    const {g} = sc; g.fillStyle = '#000'; g.fillRect(0, 0, 512, 512); g.strokeStyle = '#fff'; g.lineWidth = 2; g.font = '22px Plex'; g.fillStyle = '#25d8ff'; g.textAlign = 'center'; g.fillText('F/CTL', 256, 40);
    for (const [x, y] of [[90, 140], [420, 140], [90, 300], [420, 300], [256, 420]]) { g.strokeRect(x - 50, y - 40, 100, 80); g.fillStyle = k > 0.3 && R() < 0.6 ? '#ffb020' : '#3cff6a'; g.fillText(k > 0.2 ? junk(4) : 'ELAC', x, y + 8); }
    g.strokeStyle = '#3cff6a'; g.beginPath(); g.moveTo(140, 140); g.lineTo(370, 140); g.stroke(); glitchSlices(sc, k);
  }
  function fcu(T, k) {
    const g = fcuC.getContext('2d'); g.fillStyle = '#2b2f35'; g.fillRect(0, 0, 1024, 96);
    for (const [x, lab, v] of [[60, 'SPD', '145'], [300, 'HDG', '253'], [560, 'ALT', '3000'], [800, 'V/S', '-0700']]) {
      g.fillStyle = '#d8dde3'; g.font = '16px Plex'; g.fillText(lab, x, 22); g.fillStyle = '#0b0b0b'; g.fillRect(x - 6, 30, 150, 50);
      g.fillStyle = '#ff9a2a'; g.font = '500 38px Plex'; g.fillText(R() < k * 0.9 ? junk(v.length) : v, x, 70); }
    fcuT.needsUpdate = true;
  }

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0; renderer.toneMappingExposure = 1.25;
    R = rng(Math.floor(T * 15) * 31 + 7);
    const st = flight(t);
    // Flugzeuglage
    const shakeA = 0.004 + 0.03 * smooth(1.4, 6, t);
    ac.position.set(st.x, st.y, st.z);
    ac.rotation.set(0, 0, 0); ac.rotation.order = 'YXZ';
    ac.rotation.y = st.yaw; ac.rotation.x = st.pitch + noise1(T * 13, 2) * shakeA * 0.5; ac.rotation.z = -st.roll + noise1(T * 11, 9) * shakeA * 0.4;
    // Kamera: Notsitz hinter den Piloten
    camera.position.set(noise1(T * 17, 1) * shakeA * 0.4, 0.1 + noise1(T * 19, 3) * shakeA * 0.6, 1.15);
    camera.rotation.set(-0.05 + noise1(T * 15, 4) * shakeA * 0.6, noise1(T * 12, 6) * shakeA * 0.3, noise1(T * 9, 7) * shakeA * 0.2);
    camera.updateProjectionMatrix();
    sky.position.copy(ac.position);
    const focal = 960 / Math.tan(camera.fov * D / 2);
    for (const p of [scene.userData.city, scene.userData.rw]) { p.material.uniforms.focal.value = focal; p.material.uniforms.time.value = T; }
    // Anzeigen
    const k = clamp(0.12 + 0.5 * smooth(0.6, CK.ROLL, t) + 0.4 * smooth(3, 6, t));
    pfd(screens.pfdL, st, k, t, T); pfd(screens.pfdR, st, clamp(k + 0.1), t, T + 0.37); nd(screens.ndL, st, k, t, T); nd(screens.ndR, st, k, t, T + 0.2); ewd(screens.ewd, st, k, t, T); sd(screens.sd, st, k, t, T); fcu(T, k);
    for (const s of Object.values(screens)) { s.t.needsUpdate = true; s.m.visible = !(k > 0.5 && R() < 0.04); }
    const blink = t > CK.WARN && Math.sin(T * 10) > 0 ? 1 : 0;
    warnLights.forEach((m, i) => { m.emissiveIntensity = i % 2 ? (t > CK.WARN + 0.4 ? 0.2 + 2.5 * blink : 0.15) : 0.2 + 5 * blink; });
    redL.intensity = blink * 1.6 * (t > CK.WARN ? 1 : 0);
    // Piloten reagieren: ziehen am Sidestick, lehnen sich gegen die Schräglage
    pilots.forEach(({body, head, arms, s}, i) => {
      const pull = smooth(CK.ROLL + 0.3 + i * 0.4, CK.ROLL + 1.2 + i * 0.4, t);
      body.rotation.z = st.roll * 0.12 + noise1(T * 8, i) * shakeA * 2; body.rotation.x = -0.08 * pull;
      head.rotation.y = s * -0.15 + (t > CK.WARN ? Math.sin(T * 1.7 + i) * 0.18 : 0) * (1 - pull * 0.5); head.rotation.x = -0.1 * pull;
      for (const a of arms) { const stick = a.e === s; a.sh.rotation.x = 0.55 + (stick ? 0.25 * pull + noise1(T * 10, i + a.e) * 0.08 * pull : 0.1); a.sh.rotation.z = a.e * (stick ? 0.25 : -0.1); a.fore.rotation.x = 0.9 - (stick ? 0.3 * pull : 0); }
    });
    levers.forEach(l => { l.rotation.x = -0.35 - 0.4 * smooth(CK.PULLUP - 0.3, CK.PULLUP + 0.4, t); });
  }};
}
