// Ego-Perspektive: eigene Arme, Hände, Oberkörper und Füße, die unten ins Bild ragen.
import * as THREE from 'three';
import { toon, ink } from './toon.js';
import { phoneMesh } from './phone.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
export const EYE = 1.62;

// Handposen im Körper-Koordinatensystem (vorne = -Z, rechts = +X). s = Seite (+1 rechts, -1 links)
// p = Handposition, f = Fingerrichtung, u = Handrücken-Richtung, c = [Zeigefinger, restliche Finger] Krümmung
const HANDS = {
  runter: (s) => ({ p: V(s * 0.3, 0.76, 0.02), f: V(0, -1, -0.2), u: V(s, 0, 0), c: [0.4, 0.4] }),
  aufstuetzen: (s) => ({ p: V(s * 0.27, 0.92, -0.58), f: V(s * 0.15, -0.25, -1), u: V(0, 1, 0), c: [0.15, 0.15] }),
  vor: (s) => ({ p: V(s * 0.22, 1.12, -0.5), f: V(s * 0.12, 0.25, -1), u: V(0, 1, 0.25), c: [0.1, 0.1] }),
  zeigen: (s) => (s > 0 ? { p: V(0.2, 1.36, -0.64), f: V(0.15, 0.12, -1), u: V(0, 1, 0), c: [0, 1] } : HANDS.runter(s)),
  handy: (s) => (s > 0 ? phoneGrip(s) : HANDS.runter(s)),
  handy_beide: (s) => phoneGrip(s),
  rennen: (s) => ({ p: V(s * 0.27, 1.0, -0.12), f: V(s * 0.1, 0.6, -1), u: V(s, 0.3, 0), c: [0.9, 0.9] }),
  abwehr: (s) => ({ p: V(s * 0.2, 1.3, -0.42), f: V(s * 0.1, 1, -0.2), u: V(0, 0.2, 1), c: [0, 0] }),
};
// Handy-Platz vor dem Gesicht (Körperkoordinaten). Bildschirm zeigt zum Auge; die Hand liegt dahinter.
export const PHONE_AT = V(0.03, 1.43, -0.29);
const EYE_L = V(0, 1.62, 0.0);
function phoneFrame() {
  const n = EYE_L.clone().sub(PHONE_AT).normalize();
  const up = V(0, 1, 0).addScaledVector(n, -n.y).normalize();
  return { n, up, side: new THREE.Vector3().crossVectors(up, n).normalize() };
}
function phoneGrip(s) {
  const { n, up, side } = phoneFrame();
  // Handfläche hinter dem unteren Drittel, Finger zeigen am Rücken nach oben; links = Daumen/Stütze von der Seite
  const p = PHONE_AT.clone().addScaledVector(n, -0.032).addScaledVector(up, -0.075).addScaledVector(side, s > 0 ? 0.006 : -0.03);
  return { p, f: up.clone().addScaledVector(side, -s * 0.15), u: n.clone().negate(), c: [0.05, 0.08] };
}
export const POV_POSES = Object.keys(HANDS);

export class PovBody {
  constructor(spec = {}) {
    const top = spec.top || '#4f7a3a', skin = spec.skin || '#ecd6bd', pants = spec.pants || '#2c3c5e', shoes = spec.shoes || '#e9e9e9';
    this.root = new THREE.Group();
    const torso = ink(new THREE.CapsuleGeometry(0.19, 0.36, 4, 14), toon(top), 1.2); torso.scale.set(1.15, 1, 0.75); torso.position.set(0, 1.02, 0.13); this.root.add(torso);
    this.legs = [-1, 1].map((s) => {
      const hip = new THREE.Group(); hip.position.set(s * 0.1, 0.84, 0.08); this.root.add(hip);
      const l = ink(new THREE.CapsuleGeometry(0.085, 0.64, 4, 10), toon(pants), 1.2); l.position.y = -0.4; hip.add(l);
      const sh = ink(new THREE.BoxGeometry(0.13, 0.1, 0.29), toon(shoes), 1.2); sh.position.set(0, -0.8, -0.07); hip.add(sh);
      return hip;
    });
    this.arms = [1, -1].map((s) => {
      const sleeve = ink(new THREE.CylinderGeometry(0.058, 0.05, 1, 14), toon(top), 1.3);
      const cuff = ink(new THREE.CylinderGeometry(0.049, 0.049, 0.05, 14), toon(spec.cuff || top), 1.1);
      const hand = this.makeHand(skin, s);
      this.root.add(sleeve, cuff, hand.g);
      return { s, sleeve, cuff, hand, shoulder: V(s * 0.21, 1.3, 0.14) };
    });
    this.phone = phoneMesh(); this.phone.scale.setScalar(1.4); this.root.add(this.phone); this.phone.visible = false;
    this.root.traverse((o) => { if (o.isMesh && !o.material.isShaderMaterial) o.castShadow = true; });
    this._m = new THREE.Matrix4(); this._q = new THREE.Quaternion();
  }
  makeHand(skin, s) {
    const g = new THREE.Group(), m = toon(skin); g.scale.setScalar(1.35);
    const palm = ink(new THREE.BoxGeometry(0.084, 0.03, 0.09), m, 1.3); g.add(palm);
    const fingers = [-0.03, -0.01, 0.01, 0.03].map((x, i) => {
      const piv = new THREE.Group(); piv.position.set(x * -s, 0, -0.043); g.add(piv);
      const len = [0.05, 0.056, 0.053, 0.043][i];
      const f = ink(new THREE.CapsuleGeometry(0.0098, len, 3, 6), m, 1.1); f.rotation.x = -Math.PI / 2; f.position.z = -len / 2; piv.add(f);
      return piv;
    });
    const th = new THREE.Group(); th.position.set(-s * 0.04, -0.004, 0.01); th.rotation.y = s * 0.7; g.add(th);
    const thumb = ink(new THREE.CapsuleGeometry(0.011, 0.04, 3, 6), m, 1.1); thumb.rotation.x = -Math.PI / 2; thumb.position.z = -0.025; th.add(thumb);
    return { g, fingers };
  }
  // state: {pose, prevPose, poseK, t, walk, phone:{...}}
  update(st) {
    const k = ease(st.poseK ?? 1);
    for (const arm of this.arms) {
      const A = (HANDS[st.prevPose] || HANDS.runter)(arm.s), B = (HANDS[st.pose] || HANDS.runter)(arm.s);
      const p = A.p.clone().lerp(B.p, k), f = A.f.clone().normalize().lerp(B.f.clone().normalize(), k).normalize(), u = A.u.clone().normalize().lerp(B.u.clone().normalize(), k);
      // leichtes Zittern / Atmen
      p.y += Math.sin(st.t * 1.7 + arm.s) * 0.006; p.x += Math.sin(st.t * 1.1 + arm.s * 2) * 0.004;
      if (st.walk > 0.1 && (st.pose === 'runter')) p.z += Math.sin(st.t * 7.5 + (arm.s > 0 ? 0 : Math.PI)) * 0.12 * Math.min(1, st.walk);
      if (st.pose === 'rennen') { const ph = st.t * 10 + (arm.s > 0 ? 0 : Math.PI); p.z += Math.sin(ph) * 0.2 * Math.min(1, st.walk); p.y += Math.cos(ph) * 0.07 * Math.min(1, st.walk); }
      // Hand ausrichten: lokale -Z = Fingerrichtung, +Y = Handrücken
      const z = f.clone().negate(), x = new THREE.Vector3().crossVectors(u, z).normalize(), y = new THREE.Vector3().crossVectors(z, x);
      this._m.makeBasis(x, y, z); arm.hand.g.quaternion.setFromRotationMatrix(this._m); arm.hand.g.position.copy(p);
      const c = [A.c[0] + (B.c[0] - A.c[0]) * k, A.c[1] + (B.c[1] - A.c[1]) * k];
      arm.hand.fingers.forEach((fp, i) => (fp.rotation.x = -1.5 * (i === 0 ? c[0] : c[1])));
      // Ärmel von Schulter bis Handgelenk
      const wrist = p.clone().addScaledVector(f, -0.062); // Handgelenk hinter dem Handballen
      const dir = wrist.clone().sub(arm.shoulder), len = dir.length(); dir.normalize();
      arm.sleeve.position.copy(arm.shoulder).addScaledVector(dir, len / 2 - 0.02);
      arm.sleeve.scale.set(1, len - 0.04, 1);
      arm.sleeve.quaternion.setFromUnitVectors(V(0, 1, 0), dir);
      arm.cuff.position.copy(wrist).addScaledVector(dir, -0.04); arm.cuff.quaternion.copy(arm.sleeve.quaternion);
    }
    // Beine laufen
    const w = Math.min(1, (st.walk || 0) / 1.2), ph = st.t * (st.walk > 2.5 ? 10 : 7.5);
    this.legs[0].rotation.x = Math.sin(ph) * 0.45 * w; this.legs[1].rotation.x = -Math.sin(ph) * 0.45 * w;
    this.root.position.y = Math.abs(Math.cos(ph)) * 0.03 * w;
    // Handy in der rechten Hand, Bildschirm zum Auge
    const show = (st.pose === 'handy' || st.pose === 'handy_beide') && k > 0.3;
    this.phone.visible = show;
    if (show) {
      // kleine Handbewegung mitnehmen, damit das Handy nicht "klebt"
      const hp = this.arms[0].hand.g.position, base = phoneGrip(1).p;
      this.phone.position.copy(PHONE_AT).add(hp.clone().sub(base).multiplyScalar(k));
      this.phone.position.lerp(hp, 1 - k);
      this.phone.lookAt(this.root.localToWorld(EYE_L.clone()));
    }
  }
}
