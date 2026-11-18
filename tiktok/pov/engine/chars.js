// Figuren im Comic-Stil: einfache Körperformen mit dicken Umrissen, große runde Augen,
// Mund mit 3 Formen (Lippensynchron), Gesten über Gelenkwinkel.
import * as THREE from 'three';
import { toon, ink, canvasTex, flat } from './toon.js';
import { phoneMesh } from './phone.js';

const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const lerp = (a, b, k) => a + (b - a) * k;

// ---------- Gesichts-Texturen ----------
function eyeTex(iris, glasses) {
  return canvasTex(128, 128, (c, w) => {
    const m = w / 2;
    c.fillStyle = '#fbfaf5'; c.beginPath(); c.arc(m, m, 44, 0, 7); c.fill();
    c.lineWidth = 7; c.strokeStyle = '#151515'; c.stroke();
    c.fillStyle = iris; c.beginPath(); c.arc(m, m + 2, 24, 0, 7); c.fill();
    c.lineWidth = 3; c.strokeStyle = 'rgba(20,30,40,0.7)'; c.stroke();
    c.fillStyle = '#111'; c.beginPath(); c.arc(m, m + 2, 10, 0, 7); c.fill();
    c.fillStyle = '#fff'; c.beginPath(); c.arc(m - 8, m - 7, 5, 0, 7); c.fill();
    if (glasses) { c.lineWidth = 5; c.strokeStyle = '#2a2a2a'; c.beginPath(); c.arc(m, m, 58, 0, 7); c.stroke(); }
  });
}
function mouthTex(level) {
  return canvasTex(128, 96, (c, w, h) => {
    c.lineCap = 'round'; c.strokeStyle = '#1a1212'; c.lineWidth = 6;
    if (level === 0) { c.beginPath(); c.moveTo(w * 0.28, h * 0.5); c.quadraticCurveTo(w * 0.5, h * 0.56, w * 0.72, h * 0.5); c.stroke(); return; }
    const rx = level === 1 ? 20 : 26, ry = level === 1 ? 11 : 24;
    c.fillStyle = '#4a1f22'; c.beginPath(); c.ellipse(w / 2, h / 2, rx, ry, 0, 0, 7); c.fill(); c.stroke();
    if (level === 2) { c.fillStyle = '#c45a5a'; c.beginPath(); c.ellipse(w / 2, h / 2 + ry * 0.55, rx * 0.6, ry * 0.3, 0, 0, 7); c.fill(); }
  });
}
const browTex = canvasTex(128, 32, (c, w, h) => { c.strokeStyle = '#2a1e16'; c.lineWidth = 7; c.lineCap = 'round'; c.beginPath(); c.moveTo(12, h * 0.65); c.quadraticCurveTo(w / 2, h * 0.2, w - 12, h * 0.6); c.stroke(); });
const noseTex = canvasTex(64, 64, (c) => { c.strokeStyle = 'rgba(40,25,20,0.8)'; c.lineWidth = 4; c.lineCap = 'round'; c.beginPath(); c.moveTo(30, 14); c.quadraticCurveTo(24, 40, 36, 44); c.stroke(); });

function decal(tex, w, h) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4 }));
  m.renderOrder = 2; return m;
}

// ---------- Posen: Gelenkwinkel (Rad). sx = Schulter vor/zurück, sz = seitlich, ex = Ellbogen ----------
// R = rechter Arm, L = linker Arm (aus Sicht der Figur)
const POSES = {
  idle: { R: [0.05, 0.1, -0.2], L: [0.05, 0.1, -0.2] },
  arme_verschraenkt: { R: [-0.55, -0.25, -1.9], L: [-0.5, -0.25, -1.95] },
  erklaeren: { R: [-0.45, 0.05, -1.15], L: [0.05, 0.1, -0.25] },
  zeigen: { R: [-1.45, -0.15, -0.05], L: [0.05, 0.1, -0.2] },
  winken: { R: [-0.3, 2.5, -0.6], L: [0.05, 0.1, -0.2] },
  achselzucken: { R: [-0.35, 0.45, -1.3], L: [-0.35, 0.45, -1.3] },
  handy: { R: [-0.55, -0.1, -1.75], L: [0.05, 0.1, -0.25] },
  aufstuetzen: { R: [-0.85, 0.1, -0.35], L: [-0.85, 0.1, -0.35] },
  haende_hoch: { R: [-0.4, 2.6, -0.3], L: [-0.4, 2.6, -0.3] },
};
export const POSE_NAMES = Object.keys(POSES);

export class Character {
  constructor(name, spec) {
    this.name = name; this.spec = spec;
    const skin = spec.skin || '#ecdcc6', top = spec.top || '#8b2525', pants = spec.pants || '#1e2433', hairC = spec.hair || '#b98a4e', shoes = spec.shoes || '#1b1b1b';
    const g = (this.root = new THREE.Group());
    const body = (this.body = new THREE.Group()); g.add(body);
    // Beine (Pivot an der Hüfte)
    this.legs = [-1, 1].map((s) => {
      const hip = new THREE.Group(); hip.position.set(s * 0.1, 0.86, 0); body.add(hip);
      const leg = ink(new THREE.CapsuleGeometry(0.072, 0.66, 4, 10), toon(pants), 1.2); leg.position.y = -0.41; hip.add(leg);
      const shoe = ink(new THREE.BoxGeometry(0.12, 0.09, 0.27), toon(shoes), 1); shoe.position.set(0, -0.82, 0.05); hip.add(shoe);
      return hip;
    });
    // Oberkörper
    const torso = ink(new THREE.CapsuleGeometry(0.16, 0.4, 4, 14), toon(top), 1.3); torso.scale.set(1.12, 1, 0.68); torso.position.y = 1.12; body.add(torso);
    if (spec.detail !== 'none') {
      const dm = flat('#141414');
      for (const [x, y] of [[-0.035, 1.24], [0.035, 1.24], [-0.035, 1.13], [0.035, 1.13]]) {
        const d = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.07, 0.01), dm); d.position.set(x, y, 0.112); body.add(d);
      }
    }
    if (spec.mantel) {
      const coat = ink(new THREE.CylinderGeometry(0.19, 0.25, 0.55, 16), toon(top), 1.3); coat.scale.z = 0.75; coat.position.y = 0.62; body.add(coat);
      const lap = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.5, 0.01), flat('#141414')); lap.position.set(0, 0.95, 0.118); body.add(lap);
    }
    const neck = ink(new THREE.CylinderGeometry(0.05, 0.055, 0.12, 10), toon(skin), 0.9); neck.position.y = 1.47; body.add(neck);
    const collar = ink(new THREE.TorusGeometry(0.075, 0.025, 6, 16), toon(top), 0.8); collar.rotation.x = Math.PI / 2; collar.position.y = 1.43; body.add(collar);
    // Kopf
    const head = (this.head = new THREE.Group()); head.position.y = 1.6; body.add(head);
    const skull = ink(new THREE.SphereGeometry(0.12, 24, 18), toon(skin), 1.3); skull.scale.set(1, 1.12, 1); head.add(skull);
    const ears = [-1, 1].map((s) => { const e = ink(new THREE.SphereGeometry(0.028, 10, 8), toon(skin), 0.8); e.scale.set(0.5, 1, 0.8); e.position.set(s * 0.118, 0.0, 0); head.add(e); return e; });
    this.hair(spec.hairStyle || 'bob', hairC, head);
    // Augen, Brauen, Nase, Mund
    const et = eyeTex(spec.eyes || '#9cc7e0', !!spec.glasses);
    this.eyes = [-1, 1].map((s) => { const e = decal(et, 0.074, 0.074); e.position.set(s * 0.047, 0.014, 0.113); e.rotation.y = s * 0.38; head.add(e); return e; });
    this.brows = [-1, 1].map((s) => { const b = decal(browTex, 0.06, 0.016); b.position.set(s * 0.047, 0.062, 0.108); b.rotation.y = s * 0.38; head.add(b); return b; });
    const nose = decal(noseTex, 0.03, 0.03); nose.position.set(0, -0.022, 0.121); head.add(nose);
    this.mouthTex = [0, 1, 2].map(mouthTex);
    this.mouth = decal(this.mouthTex[0], 0.085, 0.064); this.mouth.position.set(0, -0.068, 0.108); this.mouth.rotation.x = -0.25; head.add(this.mouth);
    // Arme (Schulter -> Ellbogen -> Hand)
    this.arms = [-1, 1].map((s) => {
      const sh = new THREE.Group(); sh.position.set(s * 0.2, 1.38, 0); body.add(sh);
      const up = ink(new THREE.CapsuleGeometry(0.05, 0.25, 4, 10), toon(top), 1.2); up.position.y = -0.15; sh.add(up);
      const el = new THREE.Group(); el.position.y = -0.3; sh.add(el);
      const lo = ink(new THREE.CapsuleGeometry(0.045, 0.23, 4, 10), toon(top), 1.2); lo.position.y = -0.13; el.add(lo);
      const hand = ink(new THREE.SphereGeometry(0.052, 12, 10), toon(skin), 1); hand.scale.set(0.75, 1.15, 0.5); hand.position.y = -0.3; el.add(hand);
      const thumb = ink(new THREE.CapsuleGeometry(0.014, 0.03, 3, 6), toon(skin), 0.8); thumb.position.set(-s * 0.03, -0.27, 0.02); thumb.rotation.z = -s * 0.6; el.add(thumb);
      return { sh, el, hand, side: s };
    });
    this.phone = phoneMesh(); this.phone.scale.setScalar(0.9); this.phone.visible = false;
    this.phone.position.set(0, -0.33, 0.03); this.phone.rotation.set(-Math.PI / 2 + 0.3, 0, Math.PI);
    this.arms[0].el.add(this.phone);
    g.traverse((o) => { if (o.isMesh && o.material && !o.material.isShaderMaterial && !o.material.transparent) o.castShadow = true; });
  }

  hair(style, color, head) {
    const m = toon(color, { side: THREE.DoubleSide, noCache: true });
    if (style === 'none') return;
    const capLen = style === 'kurz' ? 1.62 : 1.78;
    const cap = ink(new THREE.SphereGeometry(0.129, 24, 14, 0, Math.PI * 2, 0, capLen), m, 1.1);
    cap.scale.set(1.04, 1.13, 1.06); cap.rotation.x = -0.58; cap.position.set(0, 0.012, -0.004); head.add(cap);
    if (style === 'bob' || style === 'lang') {
      const len = style === 'lang' ? 0.36 : 0.17;
      const geo = new THREE.CylinderGeometry(0.138, style === 'lang' ? 0.15 : 0.16, len, 20, 1, true, Math.PI / 3.1, Math.PI * 2 - (2 * Math.PI) / 3.1);
      const curtain = ink(geo, m, 1.1); curtain.position.set(0, -len / 2 + 0.035, -0.01); head.add(curtain);
    }
    if (style === 'zopf') {
      const tail = ink(new THREE.CapsuleGeometry(0.045, 0.2, 4, 8), m, 1); tail.position.set(0, -0.08, -0.15); tail.rotation.x = 0.4; head.add(tail);
    }
  }

  // state: {t, talk(0..1), pose, prevPose, poseK, facing(rad), walk(speed m/s), headYaw, blinkOff}
  update(s) {
    const t = s.t;
    this.root.rotation.y = s.facing;
    // Atmen / Gewicht verlagern
    const br = Math.sin(t * 1.9 + (s.blinkOff || 0));
    this.body.position.y = br * 0.004;
    this.body.rotation.z = Math.sin(t * 0.45 + (s.blinkOff || 0)) * 0.015;
    // Laufen
    const ph = t * 7.5, w = Math.min(1, (s.walk || 0) / 1.2);
    this.legs[0].rotation.x = Math.sin(ph) * 0.5 * w; this.legs[1].rotation.x = -Math.sin(ph) * 0.5 * w;
    this.body.position.y += Math.abs(Math.cos(ph)) * 0.025 * w;
    // Arme: Pose mischen
    const A = POSES[s.prevPose] || POSES.idle, B = POSES[s.pose] || POSES.idle, k = ease(s.poseK ?? 1);
    this.arms.forEach((arm, i) => {
      const a = i === 0 ? A.R : A.L, b = i === 0 ? B.R : B.L;
      let sx = lerp(a[0], b[0], k), sz = lerp(a[1], b[1], k), ex = lerp(a[2], b[2], k);
      if (w > 0 && (s.pose === 'idle')) sx += (i === 0 ? -1 : 1) * Math.sin(ph) * 0.35 * w;
      if (s.pose === 'winken' && i === 0) ex += Math.sin(t * 9) * 0.35 * k;
      if (s.pose === 'erklaeren' && i === 0) { sx += Math.sin(t * 3.1) * 0.06 * (s.talk > 0.05 ? 1 : 0.3); ex += Math.sin(t * 4.3) * 0.08; }
      arm.sh.rotation.set(sx, 0, arm.side * sz);
      arm.el.rotation.set(ex, 0, 0);
    });
    this.phone.visible = s.pose === 'handy' && k > 0.5;
    // Kopf: leicht nicken beim Reden, zur Kamera drehen
    this.head.rotation.set(Math.sin(t * 5.2) * 0.04 * (s.talk > 0.05 ? 1 : 0) + (s.headPitch || 0), s.headYaw || 0, Math.sin(t * 0.7) * 0.03);
    // Blinzeln
    const bl = (t + (s.blinkOff || 0) * 3) % 3.6 < 0.11 ? 0.1 : 1;
    this.eyes.forEach((e) => (e.scale.y = bl));
    // Mund
    const lv = s.talk > 0.42 ? 2 : s.talk > 0.13 ? 1 : 0;
    if (this.mouth.material.map !== this.mouthTex[lv]) this.mouth.material.map = this.mouthTex[lv];
    // Brauen (Emotion)
    const browY = s.mood === 'angst' ? 0.072 : s.mood === 'wuetend' ? 0.054 : 0.062;
    this.brows.forEach((b, i) => { b.position.y = browY; b.rotation.z = s.mood === 'wuetend' ? (i ? 0.35 : -0.35) : s.mood === 'angst' ? (i ? -0.25 : 0.25) : 0; });
  }
}
