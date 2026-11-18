// Comic-Look: Toon-Materialien mit harten Farbstufen, Tusche-Umrisse (Inverted Hull)
// und handgemalte Canvas-Texturen.
import * as THREE from 'three';
import { mergeVertices } from '../node_modules/three/examples/jsm/utils/BufferGeometryUtils.js';

// --- Zufall mit festem Seed, damit jedes Rendering identisch aussieht ---
export function rng(seed = 1) {
  let s = seed >>> 0;
  return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

// --- Toon-Material: 3 Helligkeitsstufen wie bei Cel-Shading ---
let gradient = null;
function gradientMap() {
  if (gradient) return gradient;
  const d = new Uint8Array([95, 95, 95, 255, 170, 170, 170, 255, 255, 255, 255, 255]);
  gradient = new THREE.DataTexture(d, 3, 1, THREE.RGBAFormat);
  gradient.minFilter = gradient.magFilter = THREE.NearestFilter; gradient.needsUpdate = true;
  return gradient;
}
const matCache = new Map();
export function toon(color, opts = {}) {
  const key = !opts.map && !opts.noCache ? String(color) + (opts.side || '') : null;
  if (key && matCache.has(key)) return matCache.get(key);
  const { noCache, ...o } = opts;
  const m = new THREE.MeshToonMaterial({ color, gradientMap: gradientMap(), ...o });
  if (key) matCache.set(key, m);
  return m;
}
export function flat(color, opts = {}) { return new THREE.MeshBasicMaterial({ color, ...opts }); }

// --- Umrisse: zweite, nach außen geschobene Hülle, nur Rückseiten, schwarz ---
// Die Dicke wächst mit der Entfernung zur Kamera -> Linien bleiben auf dem Bild etwa gleich breit.
const hullMats = new Map();
export function hullMaterial(width = 1, color = 0x141414) {
  const key = width + '_' + color;
  if (hullMats.has(key)) return hullMats.get(key);
  const m = new THREE.ShaderMaterial({
    uniforms: { uW: { value: 0.0072 * width }, uMin: { value: 0.0022 * width }, uColor: { value: new THREE.Color(color) } },
    vertexShader: `
      uniform float uW; uniform float uMin;
      void main(){
        vec4 lp = vec4(position,1.0); vec3 n = normal;
        #ifdef USE_INSTANCING
          lp = instanceMatrix * lp; n = mat3(instanceMatrix) * n;
        #endif
        vec4 wp = modelMatrix * lp;
        vec3 wn = normalize(mat3(modelMatrix) * n);
        float d = distance(wp.xyz, cameraPosition);
        wp.xyz += wn * max(uMin, uW * d);
        gl_Position = projectionMatrix * viewMatrix * wp;
      }`,
    fragmentShader: `uniform vec3 uColor; void main(){ gl_FragColor = vec4(uColor,1.0); }`,
    side: THREE.BackSide,
  });
  hullMats.set(key, m);
  return m;
}
const hullGeos = new WeakMap();
function hullGeometry(g) {
  if (hullGeos.has(g)) return hullGeos.get(g);
  let h = g.clone(); h.deleteAttribute('uv'); h.deleteAttribute('normal'); if (h.attributes.uv1) h.deleteAttribute('uv1');
  h = mergeVertices(h, 1e-4); h.computeVertexNormals();
  hullGeos.set(g, h); return h;
}
// Gibt ein Mesh mit Umriss zurück (Gruppe aus Füllung + Hülle)
export function ink(geometry, material, width = 1, { shadow = true, receive = true } = {}) {
  const mesh = new THREE.Mesh(geometry, material);
  mesh.castShadow = shadow; mesh.receiveShadow = receive;
  if (width > 0) {
    const hull = new THREE.Mesh(hullGeometry(geometry), hullMaterial(width));
    hull.castShadow = false; hull.receiveShadow = false; hull.raycast = () => {};
    mesh.add(hull);
  }
  return mesh;
}
export function inkInstanced(geometry, material, count, width = 1) {
  const im = new THREE.InstancedMesh(geometry, material, count);
  const hull = new THREE.InstancedMesh(hullGeometry(geometry), hullMaterial(width), count);
  hull.instanceMatrix = im.instanceMatrix; // gleiche Matrizen
  im.add(hull); im.userData.hull = hull;
  return im;
}
// Dünne Tuschelinien an harten Kanten (für Gebäude, Mauern, Autos)
const lineMat = new THREE.LineBasicMaterial({ color: 0x1a1a1a });
export function edges(mesh, angle = 35) {
  const l = new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry, angle), lineMat);
  mesh.add(l); return mesh;
}

// --- Handgemalte Texturen ---
export function canvasTex(w, h, draw, { repeat = null, srgb = true } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
  return t;
}
// Flecken (weiche, dunkle Kleckse) wie Schmutz/Wasserflecken
export function stains(ctx, w, h, r, n, color, alpha) {
  for (let i = 0; i < n; i++) {
    const x = r() * w, y = r() * h, rad = (0.03 + r() * 0.12) * w;
    for (const [dx, dy] of [[0, 0], [w, 0], [-w, 0], [0, h], [0, -h]]) {
      const g = ctx.createRadialGradient(x + dx, y + dy, 0, x + dx, y + dy, rad);
      g.addColorStop(0, `rgba(${color},${alpha * (0.4 + r() * 0.6)})`); g.addColorStop(1, `rgba(${color},0)`);
      ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(x + dx, y + dy, rad, rad * (0.5 + r() * 0.5), r() * 3, 0, 7); ctx.fill();
    }
  }
}
export function cracks(ctx, w, h, r, n, lw = 2) {
  ctx.strokeStyle = 'rgba(40,35,30,0.75)'; ctx.lineWidth = lw; ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    let x = r() * w, y = r() * h, a = r() * 6.28; ctx.beginPath(); ctx.moveTo(x, y);
    const k = 3 + (r() * 5 | 0);
    for (let j = 0; j < k; j++) { a += (r() - 0.5) * 1.4; x += Math.cos(a) * w * 0.03; y += Math.sin(a) * h * 0.03; ctx.lineTo(x, y); }
    ctx.stroke();
  }
}
// verstreutes Laub / Krümel
export function specks(ctx, w, h, r, n, colors) {
  for (let i = 0; i < n; i++) {
    ctx.fillStyle = colors[(r() * colors.length) | 0];
    ctx.save(); ctx.translate(r() * w, r() * h); ctx.rotate(r() * 6.28);
    const s = 3 + r() * 6; ctx.beginPath(); ctx.ellipse(0, 0, s, s * 0.55, 0, 0, 7); ctx.fill(); ctx.restore();
  }
}
