// Prozedurale Texturen für realistische Oberflächen (Holz, Putz, Stoff, Teppich, Beton …)
import * as THREE from 'three';
import {rng, canvasTex} from './lib.js';

function wrap(t, rx = 1, ry = 1) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx, ry); return t; }
const C = {};
// glattes Wertrauschen (für Maserung / Flecken)
function vnoise(r, w, h, cells) {
  const g = []; for (let i = 0; i < (cells + 1) * (cells + 1); i++) g.push(r());
  return (x, y) => { const fx = x / w * cells, fy = y / h * cells, ix = Math.floor(fx) % cells, iy = Math.floor(fy) % cells, tx = fx - Math.floor(fx), ty = fy - Math.floor(fy);
    const s = t => t * t * (3 - 2 * t); const a = g[iy * (cells + 1) + ix], b = g[iy * (cells + 1) + ix + 1], c = g[(iy + 1) * (cells + 1) + ix], d = g[(iy + 1) * (cells + 1) + ix + 1];
    return (a + (b - a) * s(tx)) * (1 - s(ty)) + (c + (d - c) * s(tx)) * s(ty); };
}
// Laminat / Parkett: Dielen mit Maserung
export function woodFloor(tone = [150, 108, 72], seed = 1) {
  const k = 'wf' + tone + seed; if (C[k]) return C[k];
  const r = rng(seed), W = 1024, H = 1024;
  const map = canvasTex(W, H, (g) => {
    const plankW = W / 5, plankL = H / 1.4;
    for (let col = 0; col < 5; col++) {
      let y0 = -r() * plankL;
      while (y0 < H) {
        const tint = 0.82 + r() * 0.3, n = vnoise(r, plankW, plankL, 6);
        const img = g.createImageData(plankW | 0, Math.ceil(plankL));
        for (let y = 0; y < img.height; y++) for (let x = 0; x < img.width; x++) {
          const grain = Math.sin((x * 0.11 + n(x, y) * 9 + Math.sin(y * 0.004 + col) * 3)) * 0.5 + 0.5;
          const v = tint * (0.86 + grain * 0.12 + (n(x * 3, y * 0.5) - 0.5) * 0.14);
          const i = (y * img.width + x) * 4; img.data[i] = tone[0] * v; img.data[i + 1] = tone[1] * v; img.data[i + 2] = tone[2] * v; img.data[i + 3] = 255;
        }
        g.putImageData(img, col * plankW, y0);
        g.fillStyle = 'rgba(30,18,10,0.55)'; g.fillRect(col * plankW, y0, plankW, 2); g.fillRect(col * plankW, y0, 2, plankL);
        y0 += plankL;
      }
    }
  });
  const rough = canvasTex(256, 256, (g) => { const q = rng(seed + 5); g.fillStyle = '#8a8a8a'; g.fillRect(0, 0, 256, 256); for (let i = 0; i < 3000; i++) { const v = 110 + q() * 60 | 0; g.fillStyle = `rgb(${v},${v},${v})`; g.fillRect(q() * 256, q() * 256, 2 + q() * 10, 1); } });
  rough.colorSpace = THREE.NoColorSpace;
  return (C[k] = {map: wrap(map), roughnessMap: wrap(rough, 3, 3)});
}
// Wandputz / Raufaser: leichte Unebenheit als Normale + Farbe
export function plaster(color = '#e9e5dc', seed = 2) {
  const k = 'pl' + color + seed; if (C[k]) return C[k];
  const r = rng(seed); const base = new THREE.Color(color);
  const map = canvasTex(512, 512, (g) => {
    g.fillStyle = color; g.fillRect(0, 0, 512, 512);
    const n = vnoise(r, 512, 512, 8);
    const img = g.getImageData(0, 0, 512, 512);
    for (let y = 0; y < 512; y++) for (let x = 0; x < 512; x++) { const i = (y * 512 + x) * 4; const v = 0.96 + (n(x, y) - 0.5) * 0.06 + (r() - 0.5) * 0.03; img.data[i] *= v; img.data[i + 1] *= v; img.data[i + 2] *= v; }
    g.putImageData(img, 0, 0);
  });
  const nrm = bumpToNormal(512, (x, y, q) => (q() < 0.04 ? q() : 0), 1.2, seed + 3, 2);
  return (C[k] = {map: wrap(map, 2, 2), normalMap: wrap(nrm, 4, 4)});
}
// Höhenfeld -> Normalenkarte
export function bumpToNormal(w, fn, strength = 1, seed = 1, blur = 1) {
  const q = rng(seed); const h = new Float32Array(w * w);
  for (let y = 0; y < w; y++) for (let x = 0; x < w; x++) h[y * w + x] = fn(x, y, q);
  for (let b = 0; b < blur; b++) { const t = h.slice(); for (let y = 0; y < w; y++) for (let x = 0; x < w; x++) { let s = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) s += t[((y + dy + w) % w) * w + (x + dx + w) % w]; h[y * w + x] = s / 9; } }
  const c = document.createElement('canvas'); c.width = c.height = w; const g = c.getContext('2d'); const img = g.createImageData(w, w);
  for (let y = 0; y < w; y++) for (let x = 0; x < w; x++) {
    const dx = (h[y * w + (x + 1) % w] - h[y * w + (x - 1 + w) % w]) * strength * 4, dy = (h[((y + 1) % w) * w + x] - h[((y - 1 + w) % w) * w + x]) * strength * 4;
    const n = new THREE.Vector3(-dx, -dy, 1).normalize(); const i = (y * w + x) * 4;
    img.data[i] = (n.x * .5 + .5) * 255; img.data[i + 1] = (n.y * .5 + .5) * 255; img.data[i + 2] = (n.z * .5 + .5) * 255; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0); return new THREE.CanvasTexture(c);
}
// Stoff (gewebt): feines Kreuzmuster als Normale, Farbe leicht fleckig
export function fabric(color = '#5b6470', seed = 3, scale = 6) {
  const k = 'fa' + color + seed + scale; if (C[k]) return C[k];
  const r = rng(seed);
  const map = canvasTex(256, 256, (g) => { g.fillStyle = color; g.fillRect(0, 0, 256, 256); const img = g.getImageData(0, 0, 256, 256); const n = vnoise(r, 256, 256, 4);
    for (let i = 0; i < 256 * 256; i++) { const v = 0.93 + (n(i % 256, i / 256 | 0) - 0.5) * 0.12 + (r() - 0.5) * 0.06; img.data[i * 4] *= v; img.data[i * 4 + 1] *= v; img.data[i * 4 + 2] *= v; } g.putImageData(img, 0, 0); });
  const nrm = bumpToNormal(128, (x, y) => (Math.sin(x * Math.PI / 2) * 0.5 + 0.5) * ((y >> 1) % 2 ? 1 : 0.4) + (Math.sin(y * Math.PI / 2) * 0.5 + 0.5) * ((x >> 1) % 2 ? 0.4 : 1), 0.25, seed, 0);
  return (C[k] = {map: wrap(map, 1, 1), normalMap: wrap(nrm, scale * 8, scale * 8)});
}
// Teppich / Flor
export function carpet(color = '#7b7f86', seed = 4) {
  const k = 'ca' + color + seed; if (C[k]) return C[k];
  const r = rng(seed);
  const map = canvasTex(512, 512, (g) => { g.fillStyle = color; g.fillRect(0, 0, 512, 512); for (let i = 0; i < 60000; i++) { const v = (r() - 0.5) * 40; g.fillStyle = `rgba(${v > 0 ? 255 : 0},${v > 0 ? 255 : 0},${v > 0 ? 255 : 0},${Math.abs(v) / 255})`; g.fillRect(r() * 512, r() * 512, 2, 2); } });
  const nrm = bumpToNormal(256, (x, y, q) => q(), 0.6, seed, 1);
  return (C[k] = {map: wrap(map, 2, 2), normalMap: wrap(nrm, 6, 6)});
}
// Beton / Asphalt / Gehweg
export function concrete(color = '#8d8a84', seed = 5, rough = 1) {
  const k = 'co' + color + seed; if (C[k]) return C[k];
  const r = rng(seed); const n = vnoise(r, 512, 512, 10), n2 = vnoise(r, 512, 512, 40);
  const map = canvasTex(512, 512, (g) => { g.fillStyle = color; g.fillRect(0, 0, 512, 512); const img = g.getImageData(0, 0, 512, 512);
    for (let y = 0; y < 512; y++) for (let x = 0; x < 512; x++) { const i = (y * 512 + x) * 4; const v = 0.85 + (n(x, y) - 0.5) * 0.25 + (n2(x, y) - 0.5) * 0.12 + (r() - 0.5) * 0.1 * rough; img.data[i] *= v; img.data[i + 1] *= v; img.data[i + 2] *= v; } g.putImageData(img, 0, 0); });
  const nrm = bumpToNormal(256, (x, y, q) => q() * rough, 0.5, seed, 1);
  return (C[k] = {map: wrap(map), normalMap: wrap(nrm, 4, 4)});
}
// Leder / Kunstleder (Sofa, Stuhl)
export function leather(color = '#2a2725', seed = 6) {
  const k = 'le' + color + seed; if (C[k]) return C[k];
  const nrm = bumpToNormal(256, (x, y, q) => q() < 0.3 ? q() : 0, 0.8, seed, 2);
  return (C[k] = {normalMap: wrap(nrm, 8, 8)});
}
// Knitter-/Faltenkarte für Bettdecke, Kleidung
export function wrinkles(seed = 7, w = 512) {
  const k = 'wr' + seed; if (C[k]) return C[k];
  const r = rng(seed); const lines = []; for (let i = 0; i < 40; i++) lines.push([r() * w, r() * w, r() * Math.PI, 20 + r() * 120, 4 + r() * 10]);
  const nrm = bumpToNormal(w, (x, y) => { let h = 0; for (const [cx, cy, a, len, wd] of lines) { const dx = x - cx, dy = y - cy; const u = dx * Math.cos(a) + dy * Math.sin(a), v = -dx * Math.sin(a) + dy * Math.cos(a); if (Math.abs(u) < len) h += Math.exp(-(v * v) / (wd * wd)) * (1 - Math.abs(u) / len); } return h; }, 0.9, seed, 1);
  return (C[k] = wrap(nrm));
}
export {wrap};
