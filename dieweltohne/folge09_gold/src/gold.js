// Gemeinsames: Goldmaterial, Schmuck am Körper, Glitzer beim Verschwinden
import {THREE, mat, mesh, rng, clamp} from './lib.js';

export const GOLD = new THREE.MeshStandardMaterial({color: '#ffc451', metalness: 1, roughness: 0.18, emissive: '#3a2200', emissiveIntensity: 0.25});
export const SILVER = new THREE.MeshStandardMaterial({color: '#d8dde2', metalness: 1, roughness: 0.22});

// Kette mit Anhänger, Grillz, Ringe, Uhr, Ohrstecker an einer Figur aus makePerson
export function bling(p) {
  const u = p.userData, items = [];
  // Kette: Glieder entlang einer U-Kurve vor der Brust
  const chain = new THREE.Group(); u.torso.add(chain);
  const linkG = new THREE.TorusGeometry(0.016, 0.0065, 6, 10);
  for (let i = 0; i <= 26; i++) {
    const s = -1 + i / 13; const x = 0.115 * s, y = 0.66 - 0.2 * (1 - s * s), z = 0.075 + 0.06 * (1 - s * s);
    const l = mesh(linkG, GOLD, x, y, z, chain); l.rotation.set(i % 2 ? Math.PI / 2 : 0, 0, Math.atan2(-0.4 * s, 1)); l.castShadow = false;
  }
  const pend = mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.012, 24), GOLD, 0, 0.42, 0.14, chain); pend.rotation.x = Math.PI / 2;
  mesh(new THREE.TorusGeometry(0.045, 0.006, 6, 24), GOLD, 0, 0.42, 0.147, chain);
  // zweite, kürzere Kette
  for (let i = 0; i <= 18; i++) { const s = -1 + i / 9; mesh(new THREE.SphereGeometry(0.009, 6, 5), GOLD, 0.09 * s, 0.68 - 0.1 * (1 - s * s), 0.085 + 0.04 * (1 - s * s), chain).castShadow = false; }
  items.push(chain);
  // Grillz und Zähne darunter
  const teeth = mesh(new THREE.BoxGeometry(0.05, 0.014, 0.012), mat('#f4f1ea', {roughness: 0.4}), 0, 0.0, 0.106, u.head); teeth.castShadow = false;
  const grill = mesh(new THREE.BoxGeometry(0.054, 0.017, 0.012), GOLD, 0, 0.0, 0.108, u.head); grill.castShadow = false; items.push(grill);
  const mouth = mesh(new THREE.BoxGeometry(0.062, 0.03, 0.008), mat('#3a1a16'), 0, 0.0, 0.1, u.head); mouth.castShadow = false;
  // Ohrstecker
  for (const s of [-1, 1]) items.push(mesh(new THREE.SphereGeometry(0.012, 8, 6), GOLD, s * 0.112, 0.04, 0, u.head));
  // Ringe und Uhr
  for (const arm of [u.armL, u.armR]) {
    const f = arm.userData.fore;
    const w = mesh(new THREE.TorusGeometry(0.052, 0.014, 8, 18), GOLD, 0, -0.22, 0, f); w.rotation.x = Math.PI / 2; items.push(w);
    for (let k = 0; k < 2; k++) { const r = mesh(new THREE.TorusGeometry(0.03, 0.009, 6, 14), GOLD, 0, -0.3 - k * 0.02, 0.01, f); r.rotation.x = Math.PI / 2; items.push(r); }
  }
  return {items, chain, grill, teeth};
}
export function setBling(b, on) { b.items.forEach(o => o.visible = on); }

// Goldglitzer: Punkte, die beim Verschwinden auseinanderstieben (dir=1) oder beim Zurückkommen zusammenfliegen (dir=-1)
const glintTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
  const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, 'rgba(255,250,220,1)'); r.addColorStop(0.3, 'rgba(255,210,90,0.8)'); r.addColorStop(1, 'rgba(255,170,40,0)');
  g.fillStyle = r; g.fillRect(0, 0, 64, 64); g.fillStyle = 'rgba(255,255,240,0.9)'; g.fillRect(31, 4, 2, 56); g.fillRect(4, 31, 56, 2); return new THREE.CanvasTexture(c); })();
export function glitter(n, size = 0.05) {
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  const m = new THREE.Points(geo, new THREE.PointsMaterial({size, map: glintTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, color: '#ffd77a'}));
  m.frustumCulled = false; m.userData = {n, seeds: (() => { const r = rng(n * 7 + 3); const a = []; for (let i = 0; i < n; i++) a.push([r() - 0.5, r() - 0.5, r() - 0.5, r()]); return a; })()};
  return m;
}
// pts: Array von Vector3 (Herkunftsorte), spread: Radius, age: Sekunden seit dem Ereignis, life: Dauer
export function updateGlitter(sys, pts, age, life = 0.9, spread = 0.6, rise = 0.6) {
  const P = sys.geometry.attributes.position.array, {n, seeds} = sys.userData;
  const on = age >= 0 && age < life && pts.length;
  sys.visible = !!on; if (!on) return;
  const k = age / life; sys.material.opacity = 1 - k * k;
  for (let i = 0; i < n; i++) {
    const s = seeds[i], p = pts[i % pts.length], d = spread * (0.2 + k * (0.6 + s[3]));
    P[i * 3] = p.x + s[0] * d * 2; P[i * 3 + 1] = p.y + s[1] * d * 2 + rise * k; P[i * 3 + 2] = p.z + s[2] * d * 2;
  }
  sys.geometry.attributes.position.needsUpdate = true;
}
