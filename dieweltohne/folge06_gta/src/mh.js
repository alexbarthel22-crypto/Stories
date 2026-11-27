// Realistische Menschen aus dem CC0-MakeHuman-Grundkörper (vorbereitet mit tools/mh_build.py).
// Knochen sind achsparallel (Ruhelage = Welt-Achsen), Posen werden als Drehungen im Körperraum gesetzt.
import * as THREE from 'three';
import {rng, canvasTex} from './lib.js';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';

const cache = {};
async function load(name) {
  if (!cache[name]) cache[name] = fetch(`../data/${name}.json`).then(r => r.json());
  return cache[name];
}

// Hautporen / Stoff als feine Normalen-Texturen
function noiseNormal(seed, scale, strength, w = 512) {
  const r = rng(seed);
  const c = document.createElement('canvas'); c.width = c.height = w; const g = c.getContext('2d');
  const h = new Float32Array(w * w);
  for (let k = 0; k < scale; k++) { const x = r() * w | 0, y = r() * w | 0, rad = 1 + r() * 2.5; for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) { const d = Math.hypot(dx, dy); if (d < rad) h[((y + dy + w) % w) * w + (x + dx + w) % w] -= (1 - d / rad); } }
  const img = g.createImageData(w, w);
  for (let y = 0; y < w; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x; const dx = (h[y * w + (x + 1) % w] - h[y * w + (x - 1 + w) % w]) * strength, dy = (h[((y + 1) % w) * w + x] - h[((y - 1 + w) % w) * w + x]) * strength;
    const n = new THREE.Vector3(-dx, -dy, 1).normalize();
    img.data[i * 4] = (n.x * 0.5 + 0.5) * 255; img.data[i * 4 + 1] = (n.y * 0.5 + 0.5) * 255; img.data[i * 4 + 2] = (n.z * 0.5 + 0.5) * 255; img.data[i * 4 + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
function knitNormal(w = 256) {
  const c = document.createElement('canvas'); c.width = c.height = w; const g = c.getContext('2d');
  const img = g.createImageData(w, w); const r = rng(5);
  for (let y = 0; y < w; y++) for (let x = 0; x < w; x++) {
    const i = (y * w + x) * 4; const a = Math.sin(x / w * Math.PI * 2 * 64) * 0.35 + Math.sin((x + y * 0.5) / w * Math.PI * 2 * 64) * 0.15, b = Math.sin(y / w * Math.PI * 2 * 48 + Math.sin(x * 0.4) * 0.6) * 0.25 + (r() - 0.5) * 0.15;
    const n = new THREE.Vector3(a, b, 1).normalize();
    img.data[i] = (n.x * 0.5 + 0.5) * 255; img.data[i + 1] = (n.y * 0.5 + 0.5) * 255; img.data[i + 2] = (n.z * 0.5 + 0.5) * 255; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0); const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
let PORES, KNIT, WRINK;
// große, weiche Stofffalten (Normalen), kachelbar
function foldNormal(w = 512) {
  const r = rng(77); const L = []; for (let i = 0; i < 70; i++) L.push([r() * w, r() * w, (r() - 0.5) * 0.9 + Math.PI / 2 * (r() < 0.7 ? 1 : 0), 30 + r() * 110, 3 + r() * 9]);
  const h = new Float32Array(w * w);
  for (const [cx, cy, a, len, wd] of L) for (let dy = -len; dy <= len; dy++) for (let dx = -len; dx <= len; dx++) {
    const u = dx * Math.cos(a) + dy * Math.sin(a), v = -dx * Math.sin(a) + dy * Math.cos(a); if (Math.abs(u) > len || Math.abs(v) > wd * 3) continue;
    const x = ((cx + dx) % w + w) % w | 0, y = ((cy + dy) % w + w) % w | 0; h[y * w + x] += Math.exp(-(v * v) / (wd * wd)) * (1 - Math.abs(u) / len); }
  const c = document.createElement('canvas'); c.width = c.height = w; const g = c.getContext('2d'); const img = g.createImageData(w, w);
  for (let y = 0; y < w; y++) for (let x = 0; x < w; x++) { const dx = (h[y * w + (x + 1) % w] - h[y * w + (x - 1 + w) % w]) * 1.6, dy = (h[((y + 1) % w) * w + x] - h[((y - 1 + w) % w) * w + x]) * 1.6;
    const n = new THREE.Vector3(-dx, -dy, 1).normalize(), i = (y * w + x) * 4; img.data[i] = (n.x * .5 + .5) * 255; img.data[i + 1] = (n.y * .5 + .5) * 255; img.data[i + 2] = (n.z * .5 + .5) * 255; img.data[i + 3] = 255; }
  g.putImageData(img, 0, 0); const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
// Haarsträhnen für Fell-Schalen (Alpha) – mehrere Lagen ergeben Volumen
function hairTex(seed) {
  const w = 512, r = rng(seed);
  return canvasTex(w, w, (g) => {
    g.clearRect(0, 0, w, w);
    for (let i = 0; i < 26000; i++) { const x = r() * w, y = r() * w, a = 0.5 + r() * 0.5; g.fillStyle = `rgba(255,255,255,${a})`; g.fillRect(x, y, 1.2, 1.2 + r() * 2.5); }
  });
}

const SKIN = {light: '#e7b9a0', fair: '#f0c8b0', tan: '#c98e6c', brown: '#93603f', dark: '#5f3b28'};

// Ein Material für den ganzen Körper: Haut, Oberteil, Hose, Socken/Schuhe werden je Pixel nach Bereich gemischt (saubere Säume)
function bodyMaterial(mats) {
  const m = mats.skin.clone(); m.vertexColors = true;
  const U = {wrinkleMap: {value: WRINK}, cTop: {value: mats.top.color}, cBot: {value: mats.bottom.color}, cShoe: {value: mats.shoe.color}, rTop: {value: mats.top.roughness}, rBot: {value: mats.bottom.roughness}, rShoe: {value: mats.shoe.roughness}};
  m.userData.U = U;
  m.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec4 reg; varying vec4 vReg;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvReg = reg;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      uniform vec3 cTop, cBot, cShoe; uniform float rTop, rBot, rShoe; uniform sampler2D wrinkleMap; varying vec4 vReg;
      float cut(float x){ float f = fwidth(x) * 1.2 + 0.002; return smoothstep(0.5 - f, 0.5 + f, x); }`)
      .replace('#include <color_fragment>', `#include <color_fragment>
      float wT = cut(vReg.y / max(1e-3, vReg.x + vReg.y + vReg.z + vReg.w) + 0.5 * (vReg.y > vReg.x ? 0.0 : 0.0));
      float wB = cut(vReg.z / max(1e-3, vReg.x + vReg.y + vReg.z + vReg.w)), wS = cut(vReg.w);
      float wSkin = cut(vReg.x);
      float seam = 1.0 - 0.35 * (smoothstep(0.38, 0.5, vReg.x) * (1.0 - smoothstep(0.5, 0.62, vReg.x)));
      vec3 cloth = cTop; float cw = vReg.y + vReg.z + vReg.w;
      float fb = vReg.z / max(1e-3, cw);
      cloth = mix(cloth, cBot, cut(fb));
      float band = smoothstep(0.18, 0.32, fb) * (1.0 - smoothstep(0.32, 0.5, fb));   // Bündchen am Saum
      cloth *= 1.0 - 0.28 * band;
      float cuff = smoothstep(0.5, 0.62, vReg.x) * (1.0 - smoothstep(0.62, 0.75, vReg.x)); cloth *= 1.0 - 0.0 * cuff;
      cloth = mix(cloth, cShoe, cut(vReg.w / max(1e-3, cw)));
      diffuseColor.rgb = mix(cloth * seam, diffuseColor.rgb, wSkin);
      float clothMix = 1.0 - wSkin;`)
      .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
      float rc = mix(rTop, rBot, cut(vReg.z / max(1e-3, cw))); rc = mix(rc, rShoe, cut(vReg.w / max(1e-3, cw)));
      roughnessFactor = mix(roughnessFactor, rc, clothMix);`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
      { vec3 wn = texture2D(wrinkleMap, vNormalMapUv * 0.12).xyz * 2.0 - 1.0; vec3 wn2 = texture2D(wrinkleMap, vNormalMapUv * 0.5 + 0.37).xyz * 2.0 - 1.0;
        wn = normalize(vec3((wn.xy * 0.8 + wn2.xy * 0.25) * clothMix, 1.0));
        normal = normalize(mix(normal, normalize(tbn * wn), clothMix * 0.9)); }`)
      .replace('#include <lights_physical_fragment>', `#include <lights_physical_fragment>
      material.clearcoat *= 1.0 - clothMix; material.sheenColor = mix(material.sheenColor, vec3(0.35), clothMix);`);
  };
  return m;
}

export async function makeHuman(name, o = {}) {
  WRINK = WRINK || foldNormal(); PORES = PORES || noiseNormal(11, 14000, 0.5); KNIT = KNIT || noiseNormal(23, 22000, 0.8, 256);
  PORES.repeat.set(28, 28); KNIT.repeat.set(14, 14);
  const d = await load(name);
  const root = new THREE.Group();
  // Skelett
  const bones = d.bones.map(b => { const bo = new THREE.Bone(); bo.name = b.name; return bo; });
  d.bones.forEach((b, i) => {
    const h = new THREE.Vector3(...b.head);
    if (b.parent >= 0) { bones[b.parent].add(bones[i]); bones[i].position.copy(h.sub(new THREE.Vector3(...d.bones[b.parent].head))); }
    else bones[i].position.copy(h);
  });
  const rootBone = bones[d.bones.findIndex(b => b.parent < 0)];
  const skeleton = new THREE.Skeleton(bones);
  root.add(rootBone); root.updateMatrixWorld(true); skeleton.calculateInverses();
  const skinCol = new THREE.Color(o.skin ? (SKIN[o.skin] || o.skin) : SKIN.light);
  const mats = {
    skin: new THREE.MeshPhysicalMaterial({color: skinCol, roughness: 0.52, normalMap: PORES, normalScale: new THREE.Vector2(0.12, 0.12), sheen: 0.35, sheenColor: new THREE.Color('#ff9a7a'), sheenRoughness: 0.6, clearcoat: 0.08, clearcoatRoughness: 0.5}),
    top: new THREE.MeshPhysicalMaterial({color: o.top || '#2b2f36', roughness: 0.92, normalMap: KNIT, normalScale: new THREE.Vector2(0.25, 0.25), sheen: 0.6, sheenColor: new THREE.Color(o.top || '#2b2f36').lerp(new THREE.Color('#ffffff'), 0.25), sheenRoughness: 0.8}),
    bottom: new THREE.MeshPhysicalMaterial({color: o.bottom || '#2c3e5c', roughness: 0.85, normalMap: KNIT, normalScale: new THREE.Vector2(0.3, 0.3), sheen: 0.3, sheenColor: new THREE.Color('#8fa4c4')}),
    shoe: new THREE.MeshPhysicalMaterial({color: o.shoe || '#3a3a3e', roughness: 0.95, sheen: 0.4, sheenColor: new THREE.Color('#888')}),
    'helper-upper-teeth': new THREE.MeshPhysicalMaterial({color: '#e8e2d2', roughness: 0.3}),
    'helper-lower-teeth': new THREE.MeshPhysicalMaterial({color: '#e8e2d2', roughness: 0.3}),
    'helper-tongue': new THREE.MeshPhysicalMaterial({color: '#a5524f', roughness: 0.4}),
    lashes: new THREE.MeshStandardMaterial({color: '#140d09', roughness: 0.9, side: THREE.DoubleSide}),
  };
  const meshes = {};
  for (const [k, m] of Object.entries(d.meshes)) {
    if (k === 'scalp' || k.endsWith('-eye') || k === 'lashes') continue;
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(m.pos.flat(), 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(m.uv.flat(), 2));
    g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(m.si.flat(), 4));
    g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(m.sw.flat(), 4));
    g.setIndex(m.idx); if (m.nrm) g.setAttribute('normal', new THREE.Float32BufferAttribute(m.nrm.flat(), 3)); else g.computeVertexNormals();
    if (k === 'body') { // Lippen, Wangen, Augenbrauen: Vertexfarben nach Lage im Gesicht
      const P = g.attributes.position, col = new Float32Array(P.count * 3);
      const mo = new THREE.Vector3(...d.joints['joint-mouth']), ey = d.eyeY, eL = new THREE.Vector3(...d.joints['joint-l-eye']);
      const brow = new THREE.Color(o.hair || '#2a1a10');
      for (let i = 0; i < P.count; i++) {
        const x = P.getX(i), y = P.getY(i), z = P.getZ(i); let c = new THREE.Color(1, 1, 1);
        const lip = Math.exp(-(((y - (mo.y - 0.004)) / 0.009) ** 2) - ((x / 0.026) ** 2)) * (z > mo.z + 0.0 ? 1 : 0);
        c.lerp(new THREE.Color(0.95, 0.62, 0.62), Math.min(1, lip) * 0.8);
        const ax = Math.abs(x), dyB = y - (ey + 0.022 - 0.006 * Math.max(0, (ax - eL.x) / 0.03));
        const browW = Math.exp(-((dyB / 0.005) ** 2)) * (ax > 0.009 && ax < eL.x + 0.03 ? 1 : 0) * (z > eL.z - 0.012 ? 1 : 0) * Math.max(0, Math.min(1, 1 - (ax - eL.x - 0.015) / 0.015)) * Math.min(1, (ax - 0.009) / 0.008);
        c.lerp(brow.clone().multiplyScalar(0.7 / Math.max(0.2, skinCol.r)), Math.min(1, Math.max(0, browW) * 1.3));
        const cheek = Math.exp(-(((y - (ey - 0.03)) / 0.02) ** 2) - (((ax - 0.042) / 0.018) ** 2)) * (z > eL.z - 0.03 ? 1 : 0);
        c.lerp(new THREE.Color(1.04, 0.9, 0.88), cheek * 0.15);
        if (m.ha) c.lerp(brow.clone().multiplyScalar(0.55 / Math.max(0.2, skinCol.r)), m.ha[i] * 0.92);
        col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
      }
      g.setAttribute('color', new THREE.BufferAttribute(col, 3)); mats.skin.vertexColors = true;
    }
    let mm = mats[k] || mats.skin;
    if (k === 'body') { g.setAttribute('reg', new THREE.Float32BufferAttribute(m.reg.flat(), 4)); mm = bodyMaterial(mats); }
    const sm = new THREE.SkinnedMesh(g, mm);
    sm.castShadow = sm.receiveShadow = true; sm.frustumCulled = false;
    sm.bind(skeleton, new THREE.Matrix4());
    root.add(sm); meshes[k] = sm;
  }
  const B = n => bones[d.bones.findIndex(b => b.name === n)];
  // Schuhe: Turnschuh über dem Fuß (Sohle + Obermaterial), am Fuß-Knochen
  if (o.sneakers) {
    const bm = d.meshes.body; const P = bm.pos, Rg = bm.reg;
    for (const [side, sx] of [['L', 1], ['R', -1]]) {
      const bb = new THREE.Box3(); for (let i = 0; i < P.length; i++) if (Rg[i][3] > 0.5 && P[i][0] * sx > 0) bb.expandByPoint(new THREE.Vector3(...P[i]));
      if (bb.isEmpty()) continue; const sz = bb.getSize(new THREE.Vector3()), c = bb.getCenter(new THREE.Vector3());
      const fb = B(`foot.${side}`), fh = new THREE.Vector3(...d.bones.find(b => b.name === `foot.${side}`).head);
      const sh = new THREE.Group(); sh.position.copy(c).sub(fh); fb.add(sh);
      const up = new THREE.MeshPhysicalMaterial({color: o.sneakers, roughness: 0.6, sheen: 0.4, sheenColor: new THREE.Color('#ffffff')});
      const sole = new THREE.MeshStandardMaterial({color: o.sole || '#f1efe9', roughness: 0.7});
      const len = Math.max(sz.z, 0.24) + 0.03, wid = Math.max(sz.x, 0.09) + 0.025;
      const sl = new THREE.Mesh(new RoundedBoxGeometry(wid, 0.035, len, 4, 0.015), sole); sl.position.set(0, -sz.y / 2 + 0.012, 0.005); sh.add(sl);
      const ug = new THREE.SphereGeometry(0.5, 24, 16); ug.scale(wid * 0.98, sz.y * 0.95, len * 1.0); { const pp = ug.attributes.position; for (let i = 0; i < pp.count; i++) { if (pp.getY(i) < 0) pp.setY(i, pp.getY(i) * 0.25); const z = pp.getZ(i); if (z < 0) pp.setY(i, pp.getY(i) + (-z) * 0.5 * sz.y); } ug.computeVertexNormals(); }
      const upper = new THREE.Mesh(ug, up); upper.position.set(0, -sz.y / 2 + 0.03, 0.005); sh.add(upper);
      const lace = new THREE.Mesh(new THREE.BoxGeometry(wid * 0.35, 0.01, len * 0.3), new THREE.MeshStandardMaterial({color: o.lace || '#e9e9e9', roughness: 0.8})); lace.position.set(0, sz.y * 0.32, len * 0.12); lace.rotation.x = 0.35; sh.add(lace);
      sh.traverse(x => { x.castShadow = x.receiveShadow = true; });
    }
  }
  // Augen: Augapfel + Iris + Hornhaut, am Kopf-Knochen
  const head = B('head'), headPos = new THREE.Vector3(...d.bones.find(b => b.name === 'head').head);
  const eyes = [];
  for (const side of ['l', 'r']) {
    const m = d.meshes[`helper-${side}-eye`]; const P = m.pos; const c = new THREE.Vector3();
    P.forEach(p => c.add(new THREE.Vector3(...p))); c.multiplyScalar(1 / P.length);
    let rad = 0; P.forEach(p => rad = Math.max(rad, c.distanceTo(new THREE.Vector3(...p))));
    const eb = B(`eye.${side === 'l' ? 'L' : 'R'}`) || head;
    const ebPos = new THREE.Vector3(...d.bones.find(b => b.name === eb.name).head);
    const eye = new THREE.Group(); eye.position.copy(c.clone().sub(ebPos)); eb.add(eye);
    const ball = new THREE.Mesh(new THREE.SphereGeometry(rad * 0.98, 24, 18), new THREE.MeshPhysicalMaterial({color: '#e9e4dc', roughness: 0.35}));
    eye.add(ball);
    const irisT = canvasTex(128, 128, (g) => { const r = g.createRadialGradient(64, 64, 6, 64, 64, 62); r.addColorStop(0, '#050505'); r.addColorStop(0.26, '#050505'); r.addColorStop(0.3, o.eye || '#5a3a1e'); r.addColorStop(0.8, o.eye || '#3d2814'); r.addColorStop(0.95, '#1a1008'); r.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = r; g.fillRect(0, 0, 128, 128); const q = rng(3); for (let i = 0; i < 90; i++) { const a = q() * 7; g.strokeStyle = `rgba(0,0,0,${0.2 * q()})`; g.beginPath(); g.moveTo(64 + Math.cos(a) * 20, 64 + Math.sin(a) * 20); g.lineTo(64 + Math.cos(a) * 58, 64 + Math.sin(a) * 58); g.stroke(); } });
    const ig = new THREE.SphereGeometry(rad * 0.995, 36, 10, 0, Math.PI * 2, 0, 0.56); ig.rotateX(Math.PI / 2);
    { const ip = ig.attributes.position, iu = ig.attributes.uv, cr = rad * 0.995 * Math.sin(0.56); for (let i = 0; i < ip.count; i++) iu.setXY(i, ip.getX(i) / (2 * cr) + 0.5, ip.getY(i) / (2 * cr) + 0.5); }
    const iris = new THREE.Mesh(ig, new THREE.MeshStandardMaterial({map: irisT, transparent: true, roughness: 0.4, polygonOffset: true, polygonOffsetFactor: -1}));
    eye.add(iris);
    const cornea = new THREE.Mesh(new THREE.SphereGeometry(rad * 1.0, 24, 18), new THREE.MeshPhysicalMaterial({color: '#ffffff', transparent: true, opacity: 0.08, roughness: 0.02, clearcoat: 1, specularIntensity: 1}));
    eye.add(cornea); eyes.push(eye);
  }
  // Haare: Fell-Schalen über der Kopfhaut, starr am Kopf
  const hair = new THREE.Group(); head.add(hair);
  if (o.hairLen !== 0) {
    const s = d.meshes.scalp; const n = o.hairShells || 14, len = o.hairLen || 0.018;
    const hairCol = new THREE.Color(o.hair || '#2a1a10'), tex = hairTex(o.seed || 1);
    const col = []; s.ha.forEach(h => col.push(1, 1, 1, h));
    for (let k = 0; k < n; k++) {
      const f = (k + 1) / n; const pos = [];
      s.pos.forEach((p, i) => { const nn = s.nrm[i]; const l = len * Math.min(1, s.ha[i] * 1.4) * f; pos.push(p[0] + nn[0] * l - headPos.x, p[1] + nn[1] * l - headPos.y - (o.hairDrop || 0) * f * f * Math.max(0, 0.3 - nn[1]), p[2] + nn[2] * l - headPos.z); });
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(s.uv.flat().map(v => v * (o.hairScale || 11)), 2));
      g.setAttribute('color', new THREE.Float32BufferAttribute(col, 4)); g.setIndex(s.idx); g.setAttribute('normal', new THREE.Float32BufferAttribute(s.nrm.flat(), 3));
      const m = new THREE.MeshStandardMaterial({color: hairCol.clone().multiplyScalar(0.45 + 0.65 * f), alphaMap: tex, vertexColors: true, alphaTest: 0.25 + 0.6 * f, roughness: 0.5, side: THREE.DoubleSide});
      m.alphaMap.wrapS = m.alphaMap.wrapT = THREE.RepeatWrapping;
      const me = new THREE.Mesh(g, m); me.castShadow = k < 2; me.receiveShadow = true; hair.add(me);
    }
  }
  const api = {root, bones, skeleton, meshes, eyes, mats, B, d,
    // Pose setzen: {name: [x,y,z]} Eulerwinkel (rad) im Körperraum; Rest bleibt auf 0
    pose(p) {
      bones.forEach(b => b.rotation.set(0, 0, 0));
      for (const [n, r] of Object.entries(p)) { const b = B(n); if (b) b.rotation.set(r[0] || 0, r[1] || 0, r[2] || 0, r[3] || 'XYZ'); }
    },
    look(yaw = 0, pitch = 0) { eyes.forEach(e => e.rotation.set(-pitch, yaw, 0)); },
    // Knochen in eine Welt-Richtung (Körperraum des Root-Objekts) ausrichten; twist dreht um die eigene Achse
    aim(n, dir, twist = 0) {
      const b = B(n); if (!b) return; const bd = d.bones.find(x => x.name === n);
      const rest = new THREE.Vector3(...bd.tail).sub(new THREE.Vector3(...bd.head)).normalize();
      b.parent.updateWorldMatrix(true, false);
      const qp = new THREE.Quaternion(); b.parent.getWorldQuaternion(qp);
      const qr = new THREE.Quaternion(); root.getWorldQuaternion(qr);
      const want = new THREE.Vector3(...dir).normalize().applyQuaternion(qr).applyQuaternion(qp.invert());
      b.quaternion.setFromUnitVectors(rest, want);
      if (twist) b.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(rest, twist));
      b.updateWorldMatrix(false, false);
    },
    // Drehung um eine Achse im Ruhe-Raum des Knochens (zusätzlich)
    turn(n, axis, ang) { const b = B(n); if (b) b.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(...axis).normalize(), ang)); },
    // Finger einrollen: k 0..1, Achse quer zum Finger, Daumen extra
    grip(side, k, thumb = 0.5, spread = 0) {
      const hb = d.bones.find(x => x.name === `wrist.${side}`) || d.bones.find(x => x.name === `hand.${side}`);
      for (let f = 1; f <= 5; f++) for (let j = 1; j <= 3; j++) {
        const n = `finger${f}-${j}.${side}`, b = B(n); if (!b) continue; const bd = d.bones.find(x => x.name === n);
        const dir = new THREE.Vector3(...bd.tail).sub(new THREE.Vector3(...bd.head)).normalize();
        // Handflächen-Normale in Ruhe (A-Pose): nach innen-hinten-unten
        const palm = new THREE.Vector3(0, -1, 0);
        const ax = new THREE.Vector3().crossVectors(dir, palm).normalize();
        const a = f === 1 ? thumb * (j === 1 ? 0.3 : 0.6) : k * (j === 1 ? 1.0 : 1.25);
        b.quaternion.setFromAxisAngle(ax, a);
      }
    },
  };
  return api;
}
