// Gemeinsame Helfer für Figuren: Sitzen, Mund (kann sich öffnen)
import {THREE, mat, mesh, posePerson} from './lib.js';

export function seat(p, seatY = 0.5) { // sitzt auf einem Stuhl, Blick in +z (lokal)
  const u = p.userData;
  posePerson(p, {}); p.position.y = seatY - 0.92 * u.h;
  u.legL.rotation.x = u.legR.rotation.x = -1.5; u.legL.userData.knee.rotation.x = u.legR.userData.knee.rotation.x = 1.45;
  u.pl.forEach((g, i) => { const lg = i ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
  u.pl.forEach(g => { g.userData.low.visible = false; });
  if (!u.shins) u.shins = [u.legL, u.legR].map((lg, i) => mesh(new THREE.CapsuleGeometry(0.066, 0.3, 4, 8), u.pl[i].userData.low.material, 0, -0.2, 0, lg.userData.knee));
  u.shins.forEach(s => { s.visible = true; });
}
export function unseat(p) { const u = p.userData; u.pl.forEach(g => { g.userData.low.visible = true; }); if (u.shins) u.shins.forEach(s => { s.visible = false; }); }
// Mund: dunkle Ellipse vorn am Kopf; open 0..1
export function addMouth(p) {
  const u = p.userData; if (u.mouth) return u.mouth;
  const m = mesh(new THREE.SphereGeometry(0.03, 12, 8), mat('#4a1f1f', {roughness: 0.6}), 0, 0.0, 0.1, u.head);
  m.scale.set(1, 0.25, 0.4); m.castShadow = false; u.mouth = m;
  // Augenbrauen (für Reaktionen)
  u.brows = [-1, 1].map(s => { const b = mesh(new THREE.BoxGeometry(0.04, 0.008, 0.01), mat('#2a1d15'), s * 0.042, 0.115, 0.104, u.head); b.castShadow = false; return b; });
  return m;
}
export function mouthOpen(p, k) { const m = p.userData.mouth; if (m) m.scale.set(1 - 0.25 * k, 0.25 + k * 0.9, 0.4); }
export function brows(p, up = 0, angry = 0) { const b = p.userData.brows; if (!b) return; b.forEach((m, i) => { const s = i ? 1 : -1; m.position.y = 0.115 + up * 0.02; m.rotation.z = s * angry * 0.4; }); }
