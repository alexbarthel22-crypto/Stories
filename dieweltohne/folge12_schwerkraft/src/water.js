// Schwebendes Wasser: viele wabernde Wasserkugeln (instanziert), die ohne Schwerkraft aufsteigen und zerfallen
// und mit der Schwerkraft als Platzregen zurückfallen. Dazu Gischt (weiche Partikel) und Regenstreifen.
import {THREE, rng, clamp, lerp, smooth, envMap} from './lib.js';

let _waterM = null;
export function waterMat(renderer) {
  if (!_waterM) _waterM = new THREE.MeshPhysicalMaterial({color: '#4fa9d6', roughness: 0.02, metalness: 0.1, clearcoat: 1, clearcoatRoughness: 0.02,
    transparent: true, opacity: 0.32, envMap: renderer ? envMap(renderer) : null, envMapIntensity: 1.6, ior: 1.33, specularIntensity: 1, depthWrite: false});
  return _waterM;
}
// Etwas unregelmäßige Kugel (sieht weniger nach Spielzeug aus)
function lumpy(seed, detail = 3) {
  const g = new THREE.IcosahedronGeometry(1, detail); const p = g.attributes.position; const r = rng(seed);
  const a = [r() * 6, r() * 6, r() * 6];
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const k = 1 + 0.12 * Math.sin(x * 3 + a[0]) * Math.sin(y * 2.5 + a[1]) + 0.08 * Math.sin(z * 4 + a[2]); p.setXYZ(i, x * k, y * k, z * k); }
  g.computeVertexNormals(); return g;
}
// box: {x0,x1,y0,y1,z0,z1} = Startvolumen (Wasserkörper), n Kugeln, Größen rMin..rMax
export function waterBlobs(renderer, n, box, o = {}) {
  const r = rng(o.seed || 7);
  const inst = new THREE.InstancedMesh(lumpy(o.seed || 7, 2), waterMat(renderer), n); inst.frustumCulled = false; inst.castShadow = false; inst.receiveShadow = false; inst.renderOrder = 4;
  const items = [];
  for (let i = 0; i < n; i++) {
    const big = r() < (o.bigShare || 0.08);
    const rad = big ? lerp(o.rBig0 || 0.5, o.rBig1 || 1.4, r()) : lerp(o.rMin || 0.03, o.rMax || 0.3, Math.pow(r(), 2.2));
    items.push({p: new THREE.Vector3(lerp(box.x0, box.x1, r()), lerp(box.y0, box.y1, r()), lerp(box.z0, box.z1, r())),
      v: new THREE.Vector3((r() - 0.5) * (o.vx || 0.15), lerp(o.vy0 || 0.05, o.vy1 || 0.5, r()) * (big ? 0.5 : 1), (r() - 0.5) * (o.vz || 0.15)),
      rad, ph: r() * 9, w: 2 + r() * 3, delay: r() * (o.delay || 0.6)});
  }
  inst.userData = {items, box};
  return inst;
}
const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _e = new THREE.Euler(), _s = new THREE.Vector3(), _p = new THREE.Vector3();
// rise: Sekunden seit dem Abheben (<=0: liegt noch im Becken = unsichtbar), fall: Sekunden seit Rückkehr der Schwerkraft (null = keine), floorY
export function updateBlobs(inst, rise, fall = null, floorY = 0, riseOffset = 0) {
  const {items} = inst.userData;
  items.forEach((it, i) => {
    const t = Math.max(0, rise - it.delay);
    _q.identity();
    if (rise <= it.delay * 0.5) { _s.setScalar(0.0001); _m.compose(it.p, _q, _s); inst.setMatrixAt(i, _m); return; }
    _p.copy(it.p).addScaledVector(it.v, t + riseOffset);
    const grow = smooth(0, 0.6, t);
    const wob = 0.16 * Math.sin(t * it.w + it.ph), wob2 = 0.12 * Math.sin(t * it.w * 0.7 + it.ph * 2);
    let sx = 1 + wob, sy = 1 - wob + wob2, sz = 1 - wob2;
    if (fall != null && fall > 0) { const vy = 9.8 * fall; _p.y -= 4.9 * fall * fall; const st = clamp(1 + vy * 0.09, 1, 3.2); sy = st; sx = sz = 1 / Math.sqrt(st);
      if (_p.y < floorY) { _s.setScalar(0.0001); _m.compose(_p, _q, _s); inst.setMatrixAt(i, _m); return; } }
    _s.set(sx, sy, sz).multiplyScalar(it.rad * grow);
    if (fall != null && fall > 0) _q.identity(); else { _e.set(it.ph + t * 0.3, it.ph * 0.7 + t * 0.2, 0); _q.setFromEuler(_e); }
    _m.compose(_p, _q, _s); inst.setMatrixAt(i, _m);
  });
  inst.instanceMatrix.needsUpdate = true;
}

// Platsch: Wasserkrone (offener, aufreißender Zylinder) + Gischt (weiche Partikel) + Tropfen, t = Sekunden seit Aufprall
import {particles, updateParticles} from './fx.js';
const foamTex = () => { const c = document.createElement('canvas'); c.width = 256; c.height = 128; const g = c.getContext('2d'); const r = rng(4);
  const gr = g.createLinearGradient(0, 0, 0, 128); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.25, 'rgba(240,250,255,0.75)'); gr.addColorStop(1, 'rgba(200,235,250,0.55)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 128);
  g.globalCompositeOperation = 'destination-out'; for (let i = 0; i < 260; i++) { g.beginPath(); g.arc(r() * 256, r() * 70, 2 + r() * 9, 0, 7); g.fill(); }
  for (let i = 0; i < 40; i++) { g.fillRect(r() * 256, 0, 2 + r() * 6, 20 + r() * 50); }
  const t = new THREE.CanvasTexture(c); t.wrapS = THREE.RepeatWrapping; t.repeat.set(3, 1); return t; };
export function splashFX(scene, size = 1) {
  const crownM = new THREE.MeshStandardMaterial({map: foamTex(), transparent: true, depthWrite: false, side: THREE.DoubleSide, roughness: 0.3, opacity: 1});
  const crown = new THREE.Mesh(new THREE.CylinderGeometry(1, 0.7, 1, 40, 1, true), crownM); crown.renderOrder = 5; scene.add(crown);
  const spray = particles(700, 'smoke'); spray.material.blending = THREE.NormalBlending; scene.add(spray);
  return {update(t, pos) {
    const vis = t > 0 && t < 2.6; crown.visible = spray.visible = vis; if (!vis) return;
    const up = Math.min(1, t / 0.35), dn = clamp((t - 0.45) / 0.9);
    crown.position.set(pos.x, pos.y + 0.5 * size * (1.6 * up - 1.8 * dn * dn), pos.z); crown.scale.set(size * (0.6 + 1.6 * Math.sqrt(t)), size * (0.3 + 1.6 * up) * (1 - 0.7 * dn), size * (0.6 + 1.6 * Math.sqrt(t)));
    crownM.opacity = 1 - clamp((t - 0.6) / 0.9);
    updateParticles(spray, [{pos, r: 1.5 * size, t0: 0, type: 'burstSmoke', size: 0.35 * size, rise: -1.2, alpha: 0.5, col: [0.92, 0.97, 1.0]}], t, new THREE.Vector3(0.2, 0, 0));
  }};
}
