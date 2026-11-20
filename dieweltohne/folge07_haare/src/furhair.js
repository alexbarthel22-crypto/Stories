// Haare, Fell und Gesicht in Nahaufnahme
import {THREE, mat, mesh, rng, lerp} from './lib.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

// Viele Haarsträhnen als eine Geometrie. pts(r, i) liefert die Kontrollpunkte einer Strähne.
export function strandMesh(n, seed, pts, {radius = 0.006, cols = ['#3a2416', '#5a3a22', '#2a190f'], seg = 14, taper = 0.35} = {}) {
  const r = rng(seed), geos = [];
  for (let i = 0; i < n; i++) {
    const c = new THREE.CatmullRomCurve3(pts(r, i));
    const g = new THREE.TubeGeometry(c, seg, radius * (0.7 + r() * 0.6), 4, false);
    // zur Spitze dünner
    const p = g.attributes.position, cnt = p.count, ring = 5;
    for (let k = 0; k < cnt; k++) { const s = Math.floor(k / ring) / seg; const cp = c.getPointAt(Math.min(1, s)); const f = lerp(1, taper, s);
      p.setXYZ(k, cp.x + (p.getX(k) - cp.x) * f, cp.y + (p.getY(k) - cp.y) * f, cp.z + (p.getZ(k) - cp.z) * f); }
    const col = new THREE.Color(cols[Math.floor(r() * cols.length)]); col.offsetHSL(0, 0, (r() - 0.5) * 0.06);
    const ca = new Float32Array(cnt * 3); for (let k = 0; k < cnt; k++) { const s = Math.floor(k / ring) / seg; ca[k * 3] = col.r * (0.8 + s * 0.35); ca[k * 3 + 1] = col.g * (0.8 + s * 0.35); ca[k * 3 + 2] = col.b * (0.8 + s * 0.3); }
    g.setAttribute('color', new THREE.BufferAttribute(ca, 3)); g.deleteAttribute('uv');
    geos.push(g);
  }
  const m = new THREE.Mesh(mergeGeometries(geos), new THREE.MeshStandardMaterial({vertexColors: true, roughness: 0.55, metalness: 0.05}));
  m.castShadow = true; m.receiveShadow = true; return m;
}

// Fell: viele kleine Kegel auf einer Ellipsoid-Oberfläche (InstancedMesh)
export function furCoat(n, seed, {rx, ry, rz, len = 0.03, width = 0.008, cols = ['#d98a3a', '#e8a55a', '#b86a28'], dir = new THREE.Vector3(0, -0.4, -1), center = new THREE.Vector3()} = {}) {
  const geo = new THREE.ConeGeometry(width, len, 4, 1); geo.translate(0, len / 2, 0);
  const im = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({roughness: 0.9}), n);
  const r = rng(seed), m = new THREE.Matrix4(), q = new THREE.Quaternion(), up = new THREE.Vector3(0, 1, 0), c = new THREE.Color();
  for (let i = 0; i < n; i++) {
    const u = r() * 2 - 1, ph = r() * Math.PI * 2, s = Math.sqrt(1 - u * u);
    const nrm = new THREE.Vector3(s * Math.cos(ph), u, s * Math.sin(ph));
    const pos = new THREE.Vector3(nrm.x * rx, nrm.y * ry, nrm.z * rz).add(center);
    const nn = new THREE.Vector3(nrm.x / rx, nrm.y / ry, nrm.z / rz).normalize();
    const d = nn.clone().multiplyScalar(0.6).add(dir.clone().normalize().multiplyScalar(0.55)).normalize();
    q.setFromUnitVectors(up, d); const sc = 0.7 + r() * 0.6;
    m.compose(pos, q, new THREE.Vector3(sc, sc, sc)); im.setMatrixAt(i, m);
    c.set(cols[Math.floor(r() * cols.length)]); im.setColorAt(i, c);
  }
  im.castShadow = true; im.receiveShadow = true; return im;
}

// Detailliertes Gesicht (Kopf zeigt nach +z). Gibt Gruppe mit Teilen zurück.
export function makeHead({skin = '#e9b996', hair = ['#4a2c18', '#6a4024', '#3a2112'], iris = '#5a3a1e', seed = 3, longHair = true} = {}) {
  const head = new THREE.Group();
  const sk = mat(skin, {roughness: 0.55});
  const skull = mesh(new THREE.SphereGeometry(0.1, 40, 32), sk, 0, 0, 0, head); skull.scale.set(0.9, 1.12, 1.0);
  const jaw = mesh(new THREE.SphereGeometry(0.075, 32, 24), sk, 0, -0.06, 0.018, head); jaw.scale.set(0.95, 0.8, 1.0);
  const nose = mesh(new THREE.SphereGeometry(0.0105, 16, 12), sk, 0, -0.016, 0.1, head); nose.scale.set(1.1, 0.9, 1.0);
  mesh(new THREE.ConeGeometry(0.0075, 0.032, 12), sk, 0, 0.0, 0.097, head).rotation.x = 0.4;
  for (const s of [-1, 1]) { const ear = mesh(new THREE.SphereGeometry(0.022, 16, 12), sk, s * 0.09, -0.005, 0.0, head); ear.scale.set(0.45, 1.2, 0.8); }
  const neck = mesh(new THREE.CylinderGeometry(0.045, 0.052, 0.14, 20), sk, 0, -0.15, -0.01, head);
  // Lippen und Mund
  const lipM = mat('#c98478', {roughness: 0.45});
  const lipU = mesh(new THREE.CapsuleGeometry(0.0048, 0.026, 6, 10), lipM, 0, -0.051, 0.097, head); lipU.rotation.z = Math.PI / 2;
  const lipL = mesh(new THREE.CapsuleGeometry(0.0058, 0.022, 6, 10), lipM, 0, -0.061, 0.095, head); lipL.rotation.z = Math.PI / 2;
  const mouth = mesh(new THREE.SphereGeometry(0.016, 16, 10), mat('#3a1414', {roughness: 0.9}), 0, -0.056, 0.093, head); mouth.scale.set(1.0, 0.1, 0.5);
  // Augen
  const eyes = [], lids = [], lashes = [], brows = [];
  const browM = mat(hair[0], {roughness: 0.8}), lashM = mat('#140c08', {roughness: 0.8});
  for (const s of [-1, 1]) {
    const e = new THREE.Group(); e.position.set(s * 0.034, 0.008, 0.087); head.add(e);
    mesh(new THREE.SphereGeometry(0.0125, 20, 16), mat('#efe9e4', {roughness: 0.5}), 0, 0, 0, e);
    mesh(new THREE.CircleGeometry(0.0068, 20), mat(iris, {roughness: 0.7}), 0, 0, 0.0126, e);
    mesh(new THREE.CircleGeometry(0.0032, 16), mat('#0a0a0a', {roughness: 0.6}), 0, 0, 0.0128, e);
    const hl = mesh(new THREE.CircleGeometry(0.0016, 8), new THREE.MeshBasicMaterial({color: '#ffffff'}), 0.0025, 0.0025, 0.0129, e);
    eyes.push(e);
    const lid = mesh(new THREE.SphereGeometry(0.0131, 20, 12, 0, Math.PI * 2, 0, Math.PI * 0.3), sk, 0, 0, 0, e); lid.rotation.x = 0.7; lids.push(lid);
    // Wimpern: kleine gebogene Härchen am Lidrand
    const lg = new THREE.Group(); e.add(lg);
    { const lc = new THREE.EllipseCurve(0, 0, 0.0128, 0.0128, 0.15, Math.PI - 0.15); const pts = lc.getPoints(16).map(p => new THREE.Vector3(p.x, p.y * 0.62 + 0.002, 0.0118 - Math.abs(p.x) * 0.25));
      mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 20, 0.0011, 5, false), lashM, 0, 0, 0, lg).castShadow = false;
      for (let k = 0; k < 9; k++) { const a = -0.95 + k / 8 * 1.9; const l = mesh(new THREE.CylinderGeometry(0.0003, 0.0005, 0.005, 4), lashM, Math.sin(a) * 0.012, 0.0095, 0.0105, lg); l.rotation.set(-1.0, 0, -a * 0.5); l.castShadow = false; } }
    lashes.push(lg);
    // Augenbraue
    const bc = new THREE.QuadraticBezierCurve3(new THREE.Vector3(s * 0.014, 0.03, 0.099), new THREE.Vector3(s * 0.034, 0.04, 0.097), new THREE.Vector3(s * 0.054, 0.032, 0.083));
    const b = mesh(new THREE.TubeGeometry(bc, 16, 0.0032, 6, false), browM, 0, 0, 0, head); b.scale.set(1, 1, 1); brows.push(b);
  }
  // Haare: Kappe + Strähnen
  const hairG = new THREE.Group(); head.add(hairG);
  const cap = mesh(new THREE.SphereGeometry(0.103, 40, 24, 0, Math.PI * 2, 0, Math.PI * 0.55), mat(hair[0], {roughness: 0.7}), 0, 0.006, -0.006, hairG); cap.scale.set(0.93, 1.12, 1.03); cap.rotation.x = -0.75;
  const cap2 = mesh(new THREE.SphereGeometry(0.1035, 40, 20, 0, Math.PI * 2, 0, Math.PI * 0.36), mat(hair[0], {roughness: 0.7}), 0, 0.006, -0.004, hairG); cap2.scale.set(0.93, 1.12, 1.03); cap2.rotation.x = -0.12;
  const strands = strandMesh(longHair ? 1100 : 300, seed, (r, i) => {
    const ph = Math.PI * (0.15 + r() * 1.7) + Math.PI / 2; // nicht übers Gesicht (vorne = +z ausgespart)
    const th = 0.15 + r() * 0.55;
    const x0 = Math.cos(ph) * Math.sin(th) * 0.098, z0 = Math.sin(ph) * Math.sin(th) * 0.1 - 0.004, y0 = Math.cos(th) * 0.113 + 0.008;
    const out = 1.0 + r() * 0.12, L = longHair ? 0.28 + r() * 0.12 : 0.05;
    let side = Math.atan2(z0, x0); const lim = 0.3; // vorne: zur Seite hin fallen, nie übers Gesicht
    if (Math.sin(side) > Math.sin(lim)) side = x0 >= 0 ? lim * (0.4 + r() * 0.6) : Math.PI - lim * (0.4 + r() * 0.6);
    const p = [new THREE.Vector3(x0, y0, z0), new THREE.Vector3(x0 * 1.1 * out, y0 * 0.8 + 0.01, z0 * 1.1 * out - 0.004)];
    const ox = Math.cos(side) * 0.115 * out, oz = Math.sin(side) * 0.1 * out - 0.01;
    p.push(new THREE.Vector3(ox, -0.04, oz), new THREE.Vector3(ox * 1.05 + (r() - 0.5) * 0.02, -0.04 - L * 0.5, oz * 1.05), new THREE.Vector3(ox * 1.15 + (r() - 0.5) * 0.04, -0.04 - L, oz * 1.1 + (r() - 0.5) * 0.03));
    return p;
  }, {radius: 0.0032, cols: hair});
  hairG.add(strands);
  // Pony / Scheitel vorne
  const fringe = strandMesh(160, seed + 5, (r, i) => { const s = i % 3 ? 1 : -1; const a = r();
    return [new THREE.Vector3(-0.02 + s * 0.005, 0.113, 0.02 + a * 0.02), new THREE.Vector3(s * (0.03 + a * 0.02), 0.108, 0.078), new THREE.Vector3(s * (0.07 + a * 0.01), 0.075, 0.075), new THREE.Vector3(s * 0.098, 0.03, 0.03), new THREE.Vector3(s * (0.112 + r() * 0.015), -0.06 - r() * 0.15, -0.01)]; }, {radius: 0.0032, cols: hair});
  hairG.add(fringe);
  head.userData = {skull, eyes, lids, lashes, brows, hairG, mouth, lipU, lipL, neck, sk};
  return head;
}
