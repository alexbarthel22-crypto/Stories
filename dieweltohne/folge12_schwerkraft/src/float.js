// Helfer für die Schwerelosigkeit: zappelnde Figuren, Spaghetti, Soßentropfen, frei fliegende Dinge
import {THREE, mat, mesh, rng, clamp, lerp, canvasTex} from './lib.js';

// Arme und Beine rudern (k = Stärke 0..1)
export function flail(p, T, seed = 0, k = 1) {
  const u = p.userData; const s = seed * 1.7;
  u.armL.rotation.x = lerp(u.armL.rotation.x, -1.2 + 0.9 * Math.sin(T * 6.1 + s), k);
  u.armR.rotation.x = lerp(u.armR.rotation.x, -1.0 + 0.9 * Math.sin(T * 5.3 + s + 1.3), k);
  u.armL.rotation.z = lerp(u.armL.rotation.z, -1.1 - 0.5 * Math.sin(T * 4.2 + s), k);
  u.armR.rotation.z = lerp(u.armR.rotation.z, 1.1 + 0.5 * Math.sin(T * 4.7 + s + 2), k);
  u.armL.userData.fore.rotation.x = lerp(u.armL.userData.fore.rotation.x, -0.6 + 0.4 * Math.sin(T * 7 + s), k);
  u.armR.userData.fore.rotation.x = lerp(u.armR.userData.fore.rotation.x, -0.6 + 0.4 * Math.sin(T * 6.4 + s), k);
  u.legL.rotation.x = lerp(u.legL.rotation.x, -0.4 + 0.5 * Math.sin(T * 5.5 + s), k);
  u.legR.rotation.x = lerp(u.legR.rotation.x, -0.4 - 0.5 * Math.sin(T * 5.5 + s), k);
  u.legL.userData.knee.rotation.x = lerp(u.legL.userData.knee.rotation.x, 0.5 + 0.4 * Math.sin(T * 5.5 + s + 1), k);
  u.legR.userData.knee.rotation.x = lerp(u.legR.userData.knee.rotation.x, 0.5 - 0.4 * Math.sin(T * 5.5 + s + 1), k);
  u.pl.forEach((g, i) => { const lg = i ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
}

// Nudel-Textur (für Spaghetti-Knäuel)
export const noodleTex = () => canvasTex(256, 256, (g, w, h) => {
  g.fillStyle = '#e9c46a'; g.fillRect(0, 0, w, h); const r = rng(3);
  for (let i = 0; i < 140; i++) { g.strokeStyle = r() < 0.5 ? 'rgba(255,236,170,0.8)' : 'rgba(170,120,40,0.55)'; g.lineWidth = 3 + r() * 3; g.beginPath();
    let x = r() * w, y = r() * h; g.moveTo(x, y); for (let k = 0; k < 4; k++) { x += (r() - 0.5) * 90; y += (r() - 0.5) * 90; g.quadraticCurveTo(x + (r() - 0.5) * 40, y + (r() - 0.5) * 40, x, y); } g.stroke(); }
  g.fillStyle = 'rgba(190,40,20,0.35)'; for (let i = 0; i < 30; i++) { g.beginPath(); g.arc(r() * w, r() * h, 6 + r() * 14, 0, 7); g.fill(); }
});

// Einzelne Spaghetti als Röhre (schwebend, mit Schwingen)
export function strand(seed, len = 0.35) {
  const r = rng(seed); const pts = [];
  for (let i = 0; i < 7; i++) pts.push(new THREE.Vector3((r() - 0.5) * 0.12, i / 6 * len - len / 2, (r() - 0.5) * 0.12));
  const m = mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 24, 0.0035, 5), mat('#efcf7a', {roughness: 0.45}));
  m.castShadow = false; return m;
}

// Glänzende Soßen-/Cola-Kugel, die im Flug wabbelt
export function blob(color, r = 0.04) {
  const m = mesh(new THREE.SphereGeometry(r, 18, 14), new THREE.MeshPhysicalMaterial({color, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.1}));
  m.castShadow = false; m.userData.r = r; return m;
}
export function wobble(m, T, seed = 0) { const a = 0.18 * Math.sin(T * 9 + seed), b = 0.14 * Math.sin(T * 7 + seed * 2); m.scale.set(1 + a, 1 - a + b, 1 - b); }

// Frei fliegendes Ding: Startposition, Geschwindigkeit, Drehung (keine Schwerkraft, nur geradeaus)
export class Drift {
  constructor(obj, v = new THREE.Vector3(), spin = new THREE.Vector3(), t0 = 0) {
    this.o = obj; this.p0 = obj.position.clone(); this.r0 = obj.rotation.clone(); this.v = v; this.spin = spin; this.t0 = t0;
  }
  at(T) {
    const d = Math.max(0, T - this.t0);
    this.o.position.copy(this.p0).addScaledVector(this.v, d);
    this.o.rotation.set(this.r0.x + this.spin.x * d, this.r0.y + this.spin.y * d, this.r0.z + this.spin.z * d);
    return d;
  }
}
export const clampT = clamp;
