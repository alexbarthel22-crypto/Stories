// Feuer, Rauch, Explosionen: Partikel mit eigener Größe und Farbe pro Teilchen
import {THREE, rng, clamp} from './lib.js';

const VS = `
attribute vec4 aColor; attribute float aSize; varying vec4 vColor;
void main(){ vColor = aColor; vec4 mv = modelViewMatrix * vec4(position, 1.0);
  gl_PointSize = min(aSize * 1150.0 / max(0.1, -mv.z), 230.0); gl_Position = projectionMatrix * mv; }`;
const FS = `
uniform sampler2D map; varying vec4 vColor;
void main(){ vec4 t = texture2D(map, gl_PointCoord); gl_FragColor = vec4(vColor.rgb * t.rgb, vColor.a * t.a); if (gl_FragColor.a < 0.003) discard; }`;

function softTex(kind) {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
  const r = rng(kind === 'smoke' ? 5 : 9);
  if (kind === 'smoke') { // wolkige Scheibe
    for (let i = 0; i < 14; i++) { const x = 40 + r() * 48, y = 40 + r() * 48, rad = 22 + r() * 30;
      const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, 'rgba(255,255,255,0.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); }
  } else {
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  }
  const t = new THREE.CanvasTexture(c); return t;
}
const TEX = {};

export function particles(n, kind) {
  TEX[kind] = TEX[kind] || softTex(kind);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  geo.setAttribute('aColor', new THREE.BufferAttribute(new Float32Array(n * 4), 4));
  geo.setAttribute('aSize', new THREE.BufferAttribute(new Float32Array(n), 1));
  const m = new THREE.ShaderMaterial({uniforms: {map: {value: TEX[kind]}}, vertexShader: VS, fragmentShader: FS, transparent: true, depthWrite: false,
    blending: kind === 'smoke' ? THREE.NormalBlending : THREE.AdditiveBlending});
  const p = new THREE.Points(geo, m); p.frustumCulled = false; p.userData = {n, kind}; p.renderOrder = kind === 'smoke' ? 2 : 3;
  return p;
}

// Quellen: {pos, r, t0, t1, type:'flame'|'smoke'|'burst'|'burstSmoke', size, rise, power, share}
export function updateParticles(sys, sources, t, wind = new THREE.Vector3(0.6, 0, 0.2)) {
  const {n} = sys.userData; const P = sys.geometry.attributes.position.array, C = sys.geometry.attributes.aColor.array, S = sys.geometry.attributes.aSize.array;
  const total = sources.reduce((a, s) => a + (s.share || 1), 0); let i = 0;
  sources.forEach((s, si) => {
    const cnt = Math.floor(n * (s.share || 1) / total); const r = rng(si * 977 + 11);
    for (let k = 0; k < cnt && i < n; k++, i++) {
      const rx = r() - 0.5, ry = r(), rz = r() - 0.5, rr = r(), rl = r();
      let x = 0, y = -999, z = 0, a = 0, size = 0, cr = 0, cg = 0, cb = 0;
      if (s.type === 'burst' || s.type === 'burstSmoke') {
        const age = t - s.t0 - rr * 0.08; const life = (s.type === 'burst' ? 1.2 : 4.5) + rl * 1.5;
        if (age > 0 && age < life) {
          const dir = new THREE.Vector3(rx, Math.abs(ry - 0.2) + 0.15, rz).normalize();
          const R = s.r * (0.4 + rr * 0.8) * (1 - Math.exp(-age * (s.type === 'burst' ? 5 : 2.2)));
          x = s.pos.x + dir.x * R + wind.x * age; y = s.pos.y + dir.y * R * 0.7 + age * (s.rise || 2) + (s.type === 'burstSmoke' ? age * 1.5 : 0); z = s.pos.z + dir.z * R + wind.z * age;
          const u = age / life;
          if (s.type === 'burst') { size = (s.size || 2) * (0.5 + u * 1.6) * (0.6 + rl * 0.8); const hot = 1 - u; cr = 1; cg = 0.35 + hot * 0.55; cb = 0.08 + hot * 0.4 * hot; a = (1 - u) * (1 - u) * (s.power || 1); }
          else { size = (s.size || 3) * (0.6 + u * 2.2); const v = 0.16 + rl * 0.1; cr = v; cg = v * 0.95; cb = v * 0.9; a = Math.min(1, age * 3) * (1 - u) * 0.55; }
        }
      } else {
        const life = (s.type === 'flame' ? 0.7 : 3.5) + rl * (s.type === 'flame' ? 0.6 : 2.5);
        const ph = ((t * (1 + rr * 0.3) + rr * 13.7) % life); const born = t - ph;
        if (born >= s.t0 && (s.t1 == null || born <= s.t1)) {
          const u = ph / life; a = 1;
          x = s.pos.x + rx * s.r * (1 - u * 0.5) + wind.x * ph * (s.type === 'smoke' ? 1 : 0.2);
          y = s.pos.y + ph * (s.rise || (s.type === 'flame' ? 2.2 : 1.6)) + ry * s.r * 0.3;
          z = s.pos.z + rz * s.r * (1 - u * 0.5) + wind.z * ph;
          if (s.type === 'flame') { size = (s.size || 1) * (1 - u * 0.6) * (0.6 + rl * 0.6); cr = 1; cg = 0.75 - u * 0.5; cb = 0.25 - u * 0.25; a = Math.sin(u * Math.PI) * (s.power || 1) * clamp((t - s.t0) * 2); }
          else { size = (s.size || 2.5) * (0.5 + u * 1.8); const v = 0.17 + rl * 0.1; const col = s.col || [v, v, v * 1.05]; cr = col[0]; cg = col[1]; cb = col[2]; a = Math.sin(u * Math.PI) * (s.alpha || 0.5) * clamp((t - s.t0)); }
        }
      }
      P[i * 3] = x; P[i * 3 + 1] = y; P[i * 3 + 2] = z; S[i] = size;
      C[i * 4] = cr; C[i * 4 + 1] = cg; C[i * 4 + 2] = cb; C[i * 4 + 3] = clamp(a);
    }
  });
  for (; i < n; i++) { P[i * 3 + 1] = -999; C[i * 4 + 3] = 0; }
  sys.geometry.attributes.position.needsUpdate = true; sys.geometry.attributes.aColor.needsUpdate = true; sys.geometry.attributes.aSize.needsUpdate = true;
}

// Flackerndes Licht für Feuer
export function flicker(t, seed = 0) { return 0.75 + 0.25 * Math.sin(t * 17 + seed) * Math.sin(t * 7.3 + seed * 2) + 0.1 * Math.sin(t * 31 + seed); }
