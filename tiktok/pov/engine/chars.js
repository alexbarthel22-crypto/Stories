// Figuren im Comic-Stil: einfache Körperformen mit dicken Umrissen, große runde Augen,
// Mund mit 3 Formen (Lippensynchron), Gesten über Gelenkwinkel.
import * as THREE from 'three';
import { toon, ink, edges, canvasTex, flat } from './toon.js';
import { phoneMesh } from './phone.js';
import { headlights } from './sets/aussicht.js';

const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const lerp = (a, b, k) => a + (b - a) * k;

// ---------- Gesichts-Texturen ----------
function eyeTex(iris, glasses) {
  return canvasTex(128, 128, (c, w) => {
    const m = w / 2;
    c.fillStyle = '#fbfaf5'; c.beginPath(); c.arc(m, m, 44, 0, 7); c.fill();
    if (iris === 'leer') { c.fillStyle = '#050507'; c.beginPath(); c.arc(m, m, 40, 0, 7); c.fill(); c.lineWidth = 7; c.strokeStyle = '#151515'; c.stroke(); c.fillStyle = 'rgba(255,255,255,0.8)'; c.beginPath(); c.arc(m - 10, m - 10, 4, 0, 7); c.fill(); return; }
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
  leuchten: { R: [-1.25, -0.12, -0.25], L: [0.05, 0.1, -0.2] },
  rennen: { R: [-0.3, 0.15, -1.6], L: [-0.3, 0.15, -1.6] },
  haende_tasche: { R: [0.12, 0.05, -0.55], L: [0.12, 0.05, -0.55] },
  funken: { R: [-0.35, -0.55, -2.1], L: [0.05, 0.1, -0.25] },
  kerze: { R: [-0.7, -0.25, -1.2], L: [0.05, 0.1, -0.2] },
  schirm: { R: [-0.55, -0.2, -1.35], L: [0.05, 0.1, -0.2] },
  sitzen: { R: [-0.45, 0.12, -0.7], L: [-0.45, 0.12, -0.7] },
  flehen: { R: [-0.75, -0.2, -0.9], L: [-0.75, -0.2, -0.9] },
};
export const POSE_NAMES = Object.keys(POSES);

export class Character {
  constructor(name, spec) {
    this.name = name; this.spec = spec;
    if (spec.typ === 'transporter') return this.buildVan(spec);
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
    if (spec.taschenlampe) {
      const fl = (this.flash = new THREE.Group()); fl.position.set(0, -0.33, 0.02); this.arms[1].el.add(fl);
      fl.add(ink(new THREE.CylinderGeometry(0.022, 0.03, 0.17, 10), toon('#1a1a1a'), 0.8));
      const lens = new THREE.Mesh(new THREE.CircleGeometry(0.045, 12), new THREE.MeshBasicMaterial({ color: '#fffbe8' })); lens.rotation.x = Math.PI / 2; lens.position.y = -0.087; fl.add(lens);
      const beam = new THREE.Mesh(new THREE.ConeGeometry(1.4, 9, 20, 1, true), new THREE.MeshBasicMaterial({ color: '#fff4cc', transparent: true, opacity: 0.3, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false }));
      beam.position.y = -4.6; fl.add(beam); fl.visible = false;
      if (spec.licht) { // echte Lichtquelle: beleuchtet Wände und Boden im Dunkeln
        this.flashLight = new THREE.SpotLight('#fff1d0', 0, 22, 0.42, 0.55, 1.3); this.flashLight.position.set(0, -0.09, 0); fl.add(this.flashLight);
        this.flashLight.target.position.set(0, -5, 0); fl.add(this.flashLight.target);
      }
    }
    if (spec.funkgeraet) { // Funkgerät an der Brust, rote LED blinkt
      const fg = (this.radio = new THREE.Group()); fg.position.set(-0.075, 1.21, 0.112); fg.rotation.x = -0.12; body.add(fg);
      fg.add(ink(new THREE.BoxGeometry(0.06, 0.11, 0.035), toon('#1b1c1f'), 0.7));
      const ant = ink(new THREE.CylinderGeometry(0.006, 0.009, 0.08, 6), toon('#111'), 0.5); ant.position.set(0.018, 0.09, 0); fg.add(ant);
      const grill = new THREE.Mesh(new THREE.PlaneGeometry(0.04, 0.04), flat('#3a3c42')); grill.position.set(0, -0.02, 0.0185); fg.add(grill);
      this.led = new THREE.Mesh(new THREE.SphereGeometry(0.009, 8, 6), new THREE.MeshBasicMaterial({ color: '#ff2a1a' })); this.led.position.set(-0.016, 0.04, 0.019); fg.add(this.led);
    }
    if (spec.kerze) { // Kerze vor der Brust, wirft warmes Licht aufs Gesicht (sichtbar in Pose "kerze")
      const k = (this.candle = new THREE.Group()); k.position.set(-0.11, 1.2, 0.42); body.add(k);
      k.add(ink(new THREE.CylinderGeometry(0.055, 0.05, 0.015, 14), toon('#b08a3a'), 0.6));
      const c = ink(new THREE.CylinderGeometry(0.02, 0.021, 0.13, 10), toon('#efe6cf'), 0.6); c.position.y = 0.072; k.add(c);
      this.flame = new THREE.Mesh(new THREE.ConeGeometry(0.016, 0.065, 8), new THREE.MeshBasicMaterial({ color: '#ffc04a' })); this.flame.position.y = 0.175; k.add(this.flame);
      const core = new THREE.Mesh(new THREE.SphereGeometry(0.008, 6, 4), new THREE.MeshBasicMaterial({ color: '#fff6d0' })); core.position.y = -0.018; this.flame.add(core);
      this.candleLight = new THREE.PointLight('#ffae55', 0, 0, 1.4); this.candleLight.position.set(0, 0.24, 0.05); k.add(this.candleLight); k.visible = false;
    }
    if (spec.schirm) { // Regenschirm
      const u = (this.umbrella = new THREE.Group()); u.position.set(-0.13, 1.25, 0.2); body.add(u);
      const stick = ink(new THREE.CylinderGeometry(0.008, 0.008, 0.85, 6), toon('#222'), 0.5); stick.position.y = 0.42; u.add(stick);
      const can = ink(new THREE.ConeGeometry(0.6, 0.28, 10, 1, true), toon(spec.schirm === true ? '#2a2a3a' : spec.schirm, { side: THREE.DoubleSide, noCache: true }), 0.8); can.position.y = 0.9; u.add(can);
    }
    this.phone = phoneMesh(); this.phone.scale.setScalar(0.9); this.phone.visible = false;
    this.phone.position.set(0, -0.33, 0.03); this.phone.rotation.set(-Math.PI / 2 + 0.3, 0, Math.PI);
    this.arms[0].el.add(this.phone);
    g.traverse((o) => { if (o.isMesh && o.material && !o.material.isShaderMaterial && !o.material.transparent) o.castShadow = true; });
  }

  buildVan(spec) {
    // dunkler Transporter: fährt über "laufen", Räder drehen, Scheinwerfer an
    const g = (this.root = new THREE.Group()); const col = spec.farbe_auto || '#1c1f24';
    const v = (this.van = new THREE.Group()); g.add(v);
    const body = edges(ink(new THREE.BoxGeometry(5.2, 1.9, 2.0, 8, 2, 2), toon(col), 1.0)); body.position.y = 1.35; v.add(body);
    const nose = edges(ink(new THREE.BoxGeometry(0.9, 1.05, 1.96), toon(col), 1.0)); nose.position.set(2.95, 0.92, 0); v.add(nose);
    const ws = ink(new THREE.BoxGeometry(0.1, 0.75, 1.8), toon('#2b3644'), 0.6); ws.position.set(2.62, 1.85, 0); ws.rotation.z = -0.35; v.add(ws);
    for (const z of [-1.01, 1.01]) { const sw = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.6, 0.02), toon('#2b3644')); sw.position.set(2.0, 1.85, z); v.add(sw); }
    const door = new THREE.Mesh(new THREE.BoxGeometry(0.02, 1.5, 0.02), new THREE.MeshBasicMaterial({ color: '#08080a' })); door.position.set(0.3, 1.3, 1.01); v.add(door);
    this.wheels = [];
    for (const [x, z] of [[-1.7, 0.95], [1.9, 0.95], [-1.7, -0.95], [1.9, -0.95]]) {
      const w = ink(new THREE.CylinderGeometry(0.42, 0.42, 0.3, 16), toon('#121214'), 0.7); w.rotation.x = Math.PI / 2; w.position.set(x, 0.42, z); v.add(w);
      const hub = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.08, 0.31), toon('#777')); hub.position.copy(w.position); hub.rotation.x = Math.PI / 2; v.add(hub); this.wheels.push(hub);
    }
    this.beams = headlights(v, 11, 3.42);
    const tail = [-1, 1].map((s) => { const l = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.3, 0.18), new THREE.MeshBasicMaterial({ color: '#ff2a1a' })); l.position.set(-2.62, 1.0, s * 0.85); v.add(l); return l; });
    this.isVan = true; this.dist = 0; this.lastT = 0;
    this.phone = new THREE.Group(); this.phone.visible = false;
    g.traverse((o) => { if (o.isMesh && o.material && !o.material.isShaderMaterial && !o.material.transparent) o.castShadow = true; });
    return this;
  }
  updateVan(s) {
    if (s.walk > 0.05 || this.face === undefined) this.face = s.walk > 0.05 ? s.facing : (this.spec.richtung ?? 90) * Math.PI / 180;
    this.root.rotation.y = this.face - Math.PI / 2; // Modell zeigt nach +X
    const sp = s.walk || 0; this.wheels.forEach((w) => (w.rotation.y = -s.t * sp / 0.42));
    this.van.rotation.z = -Math.min(0.04, sp * 0.004) + (sp < 0.3 && sp > 0.02 ? 0.03 : 0); // Nicken beim Bremsen
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
    if (this.isVan) return this.updateVan(s);
    const t = s.t;
    this.root.rotation.y = s.facing;
    // Atmen / Gewicht verlagern
    const br = Math.sin(t * 1.9 + (s.blinkOff || 0));
    this.body.position.y = br * 0.004;
    this.body.rotation.z = Math.sin(t * 0.45 + (s.blinkOff || 0)) * 0.015;
    // Laufen
    const run = (s.walk || 0) > 2.6, ph = t * (run ? 11 : 7.5), w = Math.min(1, (s.walk || 0) / 1.2) * (run ? 1.5 : 1);
    this.body.rotation.x = run ? 0.18 : 0;
    this.legs[0].rotation.x = Math.sin(ph) * 0.5 * w; this.legs[1].rotation.x = -Math.sin(ph) * 0.5 * w;
    if (s.pose === 'sitzen') { this.legs.forEach((l) => (l.rotation.x = -1.45)); this.body.position.y -= 0.4; }
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
    if (this.flash) { this.flash.visible = s.pose === 'leuchten' && k > 0.4; if (this.flashLight) this.flashLight.intensity = this.flash.visible ? 30 : 0; }
    if (this.led) this.led.visible = s.funk ? Math.floor(t * 8) % 2 === 0 : (t + (s.blinkOff || 0)) % 1.3 < 0.16;
    if (this.candle) { const on = s.pose === 'kerze' && k > 0.35; this.candle.visible = on; const fl = 0.8 + 0.12 * Math.sin(t * 9.3) + 0.08 * Math.sin(t * 21.1);
      this.flame.scale.set(1, 0.8 + fl * 0.4, 1); this.flame.rotation.z = Math.sin(t * 4.7) * 0.1; this.candleLight.intensity = on ? 1.6 * fl * Math.min(1, (k - 0.35) * 3) : 0; }
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
