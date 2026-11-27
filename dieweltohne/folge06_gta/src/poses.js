// Posen für die MakeHuman-Figuren (Richtungen im Körperraum: +z = vorn, +x = links der Figur, +y = oben)
import {lerp, clamp} from './lib.js';

const L = (a, b, k) => a.map((v, i) => lerp(v, b[i], k));
function spine(h, lean, twist = 0, side = 0) {
  h.aim('spine05', [side * 0.2, 1, 0.05 + lean * 0.3]); h.aim('spine04', [side * 0.3, 1, lean * 0.6], twist * 0.2); h.aim('spine03', [side * 0.3, 1, lean * 0.8], twist * 0.2);
  h.aim('spine02', [side * 0.2, 1, lean], twist * 0.3); h.aim('spine01', [side * 0.1, 1, lean * 0.7], twist * 0.3);
}
function head(h, nod = 0, yaw = 0, tilt = 0) {
  h.aim('neck01', [Math.sin(yaw) * 0.1 + tilt * 0.1, 1, 0.2 + nod * 0.3]); h.aim('neck02', [Math.sin(yaw) * 0.15, 1, 0.12 + nod * 0.3]); h.aim('neck03', [Math.sin(yaw) * 0.2 + tilt * 0.2, 1, 0.05 + nod * 0.3]);
  h.aim('head', [tilt * 0.25, 1, -0.05 + nod * 0.5], yaw);
}
// Sitzen auf Bett/Sofakante, Controller in beiden Händen vor dem Bauch.
// o: lean, nod, yaw, grip, hands ('pad' | 'lap' | 'up' | 'phone'), knees (Spreizung), slump
export function sit(h, o = {}) {
  h.pose({}); h.root.updateMatrixWorld(true);
  const lean = o.lean ?? 0.22;
  spine(h, lean, o.twist || 0);
  head(h, o.nod ?? 0, o.yaw ?? 0, o.tilt ?? 0);
  const kn = o.knees ?? 0.14;
  for (const [s, sx] of [['L', 1], ['R', -1]]) {
    h.aim(`upperleg01.${s}`, [sx * kn, -0.12, 1]); h.aim(`upperleg02.${s}`, [sx * kn, -0.06, 1]);
    h.aim(`lowerleg01.${s}`, [sx * kn * 0.3, -1, o.shin ?? 0.1]); h.aim(`lowerleg02.${s}`, [sx * kn * 0.3, -1, o.shin ?? 0.1]);
    h.aim(`foot.${s}`, [sx * 0.12, -0.45, 1]);
    arms(h, s, sx, o);
  }
}
export function arms(h, s, sx, o) {
  const mode = o.hands || 'pad', k = o.handsK ?? 1;
  let ua = [sx * 0.26, -0.86, 0.42], la = [-sx * 0.55, 0.14, 0.85], wr = [-sx * 0.25, 0.08, 1], tw = sx * 0.6, gr = o.grip ?? 0.72;
  if (mode === 'lap') { ua = [sx * 0.2, -0.95, 0.25]; la = [-sx * 0.25, -0.35, 1]; wr = [-sx * 0.1, -0.3, 1]; tw = sx * 0.9; gr = 0.35; }
  if (mode === 'up') { ua = [sx * 0.75, 0.35, 0.35]; la = [sx * 0.25, 1, 0.1]; wr = [sx * 0.15, 1, 0.1]; tw = 0; gr = 0.1; }  // Arme hoch (Wut)
  if (mode === 'head') { ua = [sx * 0.9, 0.2, 0.2]; la = [-sx * 0.45, 0.85, 0.05]; wr = [-sx * 0.8, 0.3, -0.2]; tw = sx * 1.4; gr = 0.3; } // Hände an den Kopf
  if (mode === 'phone' && s === 'R') { ua = [-0.15, -0.6, 0.6]; la = [0.15, 0.75, 0.6]; wr = [0.05, 0.9, 0.3]; tw = -1.2; gr = 0.55; }
  if (mode === 'phone' && s === 'L') { ua = [0.22, -0.92, 0.2]; la = [-0.3, -0.3, 1]; wr = [-0.1, -0.3, 1]; tw = 0.9; gr = 0.4; }
  if (mode === 'give' && s === 'R') { ua = [-0.1, -0.55, 0.8]; la = [-0.05, -0.1, 1]; wr = [0, 0, 1]; tw = -1.6; gr = 0.15; } // Hand ausstrecken, Handfläche oben
  if (mode === 'hang') { ua = [sx * 0.12, -1, 0.02]; la = [sx * 0.02, -1, 0.15]; wr = [sx * 0.02, -1, 0.12]; tw = sx * 1.2; gr = 0.35; }
  if (mode === 'hips') { ua = [sx * 0.6, -0.75, -0.1]; la = [-sx * 0.55, -0.35, 0.6]; wr = [-sx * 0.6, -0.5, 0.3]; tw = sx * 1.2; gr = 0.45; } // Hände in die Hüften
  if (mode === 'brace') { ua = [sx * 0.35, -0.5, 0.8]; la = [sx * 0.1, 0.15, 1]; wr = [sx * 0.05, 0.6, 0.6]; tw = sx * 0.2; gr = 0.05; } // Abwehr: Hände vor
  if (o.armsFrom) { const f = o.armsFrom[s]; if (f) { ua = L(f.ua, ua, k); la = L(f.la, la, k); wr = L(f.wr, wr, k); } }
  h.aim(`upperarm01.${s}`, ua); h.aim(`upperarm02.${s}`, ua);
  h.aim(`lowerarm01.${s}`, la); h.aim(`lowerarm02.${s}`, la);
  h.aim(`wrist.${s}`, wr, tw);
  h.grip(s, gr, 0.3);
  return {ua, la, wr};
}
// Stehen / Gehen. o: walk (Phase), amp, lean, nod, yaw, hands
export function stand(h, o = {}) {
  h.pose({}); h.root.updateMatrixWorld(true);
  const ph = o.walk ?? 0, amp = o.amp ?? 0;
  spine(h, o.lean ?? 0.02, (o.twist ?? 0) + Math.sin(ph) * 0.12 * amp, o.side || 0);
  head(h, o.nod ?? 0, o.yaw ?? 0, o.tilt ?? 0);
  for (const [s, sx, p] of [['L', 1, 0], ['R', -1, Math.PI]]) {
    const sw = Math.sin(ph + p) * 0.45 * amp, kneeB = Math.max(0, Math.sin(ph + p + 1.3)) * 0.9 * amp + (o.crouch || 0);
    h.aim(`upperleg01.${s}`, [sx * 0.05, -1, sw + (o.crouch || 0) * 0.8]); h.aim(`upperleg02.${s}`, [sx * 0.05, -1, sw + (o.crouch || 0) * 0.8]);
    h.aim(`lowerleg01.${s}`, [sx * 0.02, -1, sw - kneeB]); h.aim(`lowerleg02.${s}`, [sx * 0.02, -1, sw - kneeB]);
    h.aim(`foot.${s}`, [sx * 0.08, -0.25 + Math.max(0, -Math.sin(ph + p)) * 0.6 * amp, 1]);
    if (o.hands && o.hands !== 'swing') arms(h, s, sx, o);
    else { const as = -sw * 0.8; h.aim(`upperarm01.${s}`, [sx * 0.12, -1, as]); h.aim(`upperarm02.${s}`, [sx * 0.12, -1, as]); h.aim(`lowerarm01.${s}`, [sx * 0.05, -1, as + 0.25]); h.aim(`lowerarm02.${s}`, [sx * 0.05, -1, as + 0.25]); h.aim(`wrist.${s}`, [sx * 0.04, -1, as + 0.2], sx * 1.3); h.grip(s, 0.3, 0.2); }
  }
}
// Mund öffnen (0..1) über den Kiefer
export function mouth(h, k) { const b = h.B('jaw'); if (b) b.rotation.x = 0; h.turn('jaw', [1, 0, 0], k * 0.32); }
export {clamp};
// Zwei Posen mischen (k 0..1): beide berechnen, Knochen-Quaternionen verschmelzen
export function blend(h, a, b, k) {
  if (k <= 0) return a(); if (k >= 1) return b();
  a(); const qa = h.bones.map(x => x.quaternion.clone());
  b(); h.bones.forEach((x, i) => x.quaternion.copy(qa[i]).slerp(x.quaternion.clone(), k));
}
export const hipY = h => h.d.bones[0].head[1];
