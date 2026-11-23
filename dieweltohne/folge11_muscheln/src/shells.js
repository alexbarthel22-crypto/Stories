// Muscheln: Miesmuschel (blauschwarz, länglich), Herzmuschel (hell, gerippt), Auster (grau, flach, unregelmäßig).
// Dazu Perlmutt-Material, eine Textur für ganze Muschelhaufen und ein Schwarm aus Instanzen für Regen, Fluten und Berge.
import {THREE, rng, canvasTex} from './lib.js';

let _geo = null, _mats = null;
export function shellGeos() {
  if (_geo) return _geo;
  // Miesmuschel: zugespitztes Ellipsoid (Länge ~7 cm)
  const mus = new THREE.SphereGeometry(1, 14, 10); { const p = mus.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), k = 1 - 0.45 * Math.max(0, x); p.setXYZ(i, x * 0.036, p.getY(i) * 0.013 * k, p.getZ(i) * 0.018 * k); } mus.computeVertexNormals(); }
  // Herzmuschel: gerippte Halbkugel (~4 cm)
  const coc = new THREE.SphereGeometry(1, 18, 8, 0, Math.PI * 2, 0, Math.PI / 2); { const p = coc.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), a = Math.atan2(z, x), rib = 1 + 0.06 * Math.cos(a * 16);
      p.setXYZ(i, x * 0.022 * rib, y * 0.014, z * 0.02 * rib); } coc.computeVertexNormals(); }
  // Auster: flache, unregelmäßige Schale (~9 cm)
  const oys = new THREE.CylinderGeometry(1, 0.85, 1, 16, 1); { const p = oys.attributes.position; const r = rng(4);
    const wob = Array.from({length: 17}, () => 0.8 + r() * 0.35);
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), a = Math.atan2(z, x);
      const k = wob[Math.round(((a + Math.PI) / (Math.PI * 2)) * 16) % 16];
      p.setXYZ(i, x * 0.045 * k, y * 0.014 + (Math.abs(x) + Math.abs(z)) * 0.0, z * 0.032 * k); } oys.computeVertexNormals(); }
  _geo = {mus, coc, oys}; return _geo;
}
export function shellMats() {
  if (_mats) return _mats;
  const ribT = canvasTex(256, 64, (g, w, h) => { g.fillStyle = '#efe4d2'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 32; i++) { g.fillStyle = i % 2 ? 'rgba(160,120,80,0.35)' : 'rgba(255,255,255,0.3)'; g.fillRect(i * 8, 0, 4, h); }
    for (let y = 0; y < h; y += 9) { g.fillStyle = 'rgba(150,110,70,0.25)'; g.fillRect(0, y, w, 2); } });
  const oysT = canvasTex(256, 256, (g, w, h) => { const r = rng(9); g.fillStyle = '#9a958a'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 26; i++) { g.strokeStyle = `rgba(${r() < 0.5 ? '70,66,58' : '200,195,185'},0.5)`; g.lineWidth = 2 + r() * 4; g.beginPath(); g.ellipse(w / 2, h / 2, 20 + i * 4.5, 14 + i * 3.6, r() * 0.3, 0, 7); g.stroke(); } });
  _mats = {
    mus: new THREE.MeshPhysicalMaterial({color: '#1f2738', roughness: 0.32, clearcoat: 0.6, clearcoatRoughness: 0.3, sheen: 0.4, sheenColor: new THREE.Color('#5a5a9a')}),
    coc: new THREE.MeshStandardMaterial({map: ribT, roughness: 0.6}),
    oys: new THREE.MeshStandardMaterial({map: oysT, roughness: 0.9}),
    nacre: new THREE.MeshPhysicalMaterial({color: '#f2eee8', roughness: 0.18, metalness: 0.05, iridescence: 1, iridescenceIOR: 1.6, iridescenceThicknessRange: [200, 700], clearcoat: 1}),
    pearl: new THREE.MeshPhysicalMaterial({color: '#fbf7f0', roughness: 0.12, iridescence: 0.7, iridescenceIOR: 1.5, iridescenceThicknessRange: [250, 550], clearcoat: 1, sheen: 0.5, sheenColor: new THREE.Color('#ffd9e6')}),
  };
  return _mats;
}
// Textur für große Muschelhaufen (aus der Ferne)
export function heapTex(seed = 3, size = 1024, n = 5200) {
  const r = rng(seed);
  const t = canvasTex(size, size, (g, w, h) => { g.fillStyle = '#5b5c63'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < n; i++) { const x = r() * w, y = r() * h, s = 0.6 + r() * 0.8, k = r(), a = r() * Math.PI;
      g.save(); g.translate(x, y); g.rotate(a);
      if (k < 0.5) { const gr = g.createLinearGradient(-10 * s, 0, 10 * s, 0); gr.addColorStop(0, '#1b2130'); gr.addColorStop(0.5, '#3c4560'); gr.addColorStop(1, '#141822');
        g.fillStyle = gr; g.beginPath(); g.ellipse(0, 0, 13 * s, 5 * s, 0, 0, 7); g.fill(); g.fillStyle = 'rgba(150,160,200,0.35)'; g.beginPath(); g.ellipse(-2 * s, -1.5 * s, 7 * s, 1.2 * s, 0, 0, 7); g.fill(); }
      else if (k < 0.78) { g.fillStyle = '#e9dcc4'; g.beginPath(); g.arc(0, 0, 7 * s, 0, 7); g.fill(); g.strokeStyle = 'rgba(150,110,70,0.5)'; g.lineWidth = 1;
        for (let j = -3; j <= 3; j++) { g.beginPath(); g.moveTo(0, 6 * s); g.lineTo(j * 2 * s, -6.5 * s); g.stroke(); } }
      else { g.fillStyle = r() < 0.5 ? '#a19b90' : '#8b867c'; g.beginPath(); g.ellipse(0, 0, 11 * s, 8 * s, 0, 0, 7); g.fill(); g.strokeStyle = 'rgba(230,225,215,0.5)'; g.lineWidth = 1.5; g.beginPath(); g.ellipse(0, 0, 7 * s, 5 * s, 0, 0, 7); g.stroke(); }
      g.fillStyle = 'rgba(0,0,0,0.18)'; g.beginPath(); g.ellipse(2 * s, 3 * s, 9 * s, 3 * s, 0, 0, 7); g.fill();
      g.restore(); } });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
// Schwarm: n Muscheln als drei Instanz-Meshes. set(i, x, y, z, rx, ry, rz, s) setzt Muschel i; hide(i) versteckt sie.
const _o = new THREE.Object3D();
export function shellSwarm(n, parent, {scale = 1, shadows = false} = {}) {
  const G = shellGeos(), M = shellMats();
  const per = Math.ceil(n / 3);
  const inst = [new THREE.InstancedMesh(G.mus, M.mus, per), new THREE.InstancedMesh(G.coc, M.coc, per), new THREE.InstancedMesh(G.oys, M.oys, per)];
  inst.forEach(m => { m.castShadow = shadows; m.receiveShadow = true; m.frustumCulled = false; parent.add(m); });
  const api = {n, inst,
    set(i, x, y, z, rx = 0, ry = 0, rz = 0, s = 1) { _o.position.set(x, y, z); _o.rotation.set(rx, ry, rz); _o.scale.setScalar(s * scale); _o.updateMatrix(); inst[i % 3].setMatrixAt(Math.floor(i / 3), _o.matrix); },
    hide(i) { _o.position.set(0, -999, 0); _o.scale.setScalar(0.0001); _o.updateMatrix(); inst[i % 3].setMatrixAt(Math.floor(i / 3), _o.matrix); },
    commit() { inst.forEach(m => { m.instanceMatrix.needsUpdate = true; }); },
    set visible(v) { inst.forEach(m => { m.visible = v; }); },
  };
  return api;
}
// Austernhälfte mit Perlmutt innen (zum Essen auf dem Teller)
export function oysterHalf(parent) {
  const M = shellMats(); const g = new THREE.Group();
  const outer = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 8, 0, Math.PI * 2, Math.PI * 0.62, Math.PI * 0.38), M.oys); outer.scale.set(0.05, 0.03, 0.036);
  const inner = new THREE.Mesh(new THREE.SphereGeometry(0.97, 20, 8, 0, Math.PI * 2, Math.PI * 0.64, Math.PI * 0.36), M.nacre); inner.scale.set(0.05, 0.03, 0.036);
  inner.material = M.nacre.clone(); inner.material.side = THREE.BackSide;
  outer.material = M.oys.clone(); outer.material.side = THREE.DoubleSide;
  outer.position.y = inner.position.y = 0.03; outer.castShadow = true;
  const meat = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 8), new THREE.MeshPhysicalMaterial({color: '#c9bba0', roughness: 0.25, clearcoat: 0.8}));
  meat.scale.set(0.032, 0.006, 0.022); meat.position.y = 0.006;
  g.add(outer, inner, meat); g.userData = {outer, inner, meat}; if (parent) parent.add(g); return g;
}
