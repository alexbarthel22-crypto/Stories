// Realistischeres Auto: Seitenprofil extrudiert, Dach verjüngt, Klarlack, Felgen, echte Scheinwerfer-Spots
import * as THREE from 'three';
const V = (x, y, z) => new THREE.Vector3(x, y, z);
export function makeCar2(o = {}) {
  const L = 4.5, W = 1.82, color = o.color || '#2d3036';
  const car = new THREE.Group(), body = new THREE.Group(); car.add(body);
  const paint = new THREE.MeshPhysicalMaterial({color, metalness: 0.6, roughness: 0.35, clearcoat: 1, clearcoatRoughness: 0.06});
  const hx = L / 2, s = new THREE.Shape();
  s.moveTo(-hx, 0.36); s.lineTo(-hx, 0.72); s.bezierCurveTo(-hx, 0.86, -hx + 0.2, 0.92, -hx + 0.5, 0.95);
  s.lineTo(-hx + 1.15, 1.0); s.bezierCurveTo(-hx + 1.55, 1.38, -hx + 1.7, 1.44, -hx + 2.0, 1.45); s.lineTo(hx - 1.55, 1.44);
  s.bezierCurveTo(hx - 1.3, 1.42, hx - 1.05, 1.1, hx - 0.85, 1.0); s.lineTo(hx - 0.25, 0.92); s.bezierCurveTo(hx - 0.05, 0.88, hx, 0.8, hx, 0.62); s.lineTo(hx, 0.36);
  // Radausschnitte
  s.lineTo(hx - 0.55, 0.36); s.absarc(hx - 0.95, 0.36, 0.4, 0, Math.PI, false); s.lineTo(-hx + 1.35, 0.36); s.absarc(-hx + 0.95, 0.36, 0.4, 0, Math.PI, false); s.lineTo(-hx, 0.36);
  const g = new THREE.ExtrudeGeometry(s, {depth: W - 0.16, bevelEnabled: true, bevelThickness: 0.08, bevelSize: 0.08, bevelSegments: 5, curveSegments: 18, steps: 6});
  g.translate(0, 0, -(W - 0.16) / 2);
  { const p = g.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i), z = p.getZ(i); const k = y > 1.0 ? 1 - (y - 1.0) / 0.45 * 0.2 : 1; p.setZ(i, z * k); } g.computeVertexNormals(); }
  g.rotateY(-Math.PI / 2); // Länge entlang z, vorne = +z
  const shell = new THREE.Mesh(g, paint); shell.castShadow = shell.receiveShadow = true; body.add(shell);
  // Scheiben: etwas kleiner als die Dachlinie, dunkel spiegelnd
  const gs = new THREE.Shape(); gs.moveTo(-hx + 1.2, 1.02); gs.bezierCurveTo(-hx + 1.55, 1.34, -hx + 1.7, 1.4, -hx + 2.0, 1.41); gs.lineTo(hx - 1.55, 1.4); gs.bezierCurveTo(hx - 1.32, 1.38, hx - 1.1, 1.1, hx - 0.9, 1.02);
  const gg = new THREE.ExtrudeGeometry(gs, {depth: W - 0.05, bevelEnabled: false, curveSegments: 16}); gg.translate(0, 0, -(W - 0.05) / 2);
  { const p = gg.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i), z = p.getZ(i); const k = y > 1.0 ? 1 - (y - 1.0) / 0.45 * 0.2 : 1; p.setZ(i, z * k); } gg.computeVertexNormals(); }
  gg.rotateY(-Math.PI / 2);
  const glass = new THREE.Mesh(gg, new THREE.MeshPhysicalMaterial({color: '#0b0f14', metalness: 0.2, roughness: 0.04, clearcoat: 1})); body.add(glass);
  // Scheinwerfer, Rückleuchten, Kennzeichen, Grill
  const headM = new THREE.MeshStandardMaterial({color: '#fff', emissive: '#f4f6ff', emissiveIntensity: 3});
  const tailM = new THREE.MeshStandardMaterial({color: '#600', emissive: '#ff1a10', emissiveIntensity: 2.5});
  for (const x of [-0.62, 0.62]) {
    const h = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.08, 0.06), headM); h.position.set(x, 0.8, hx + 0.03); body.add(h);
    const t = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.08, 0.05), tailM); t.position.set(x, 0.86, -hx - 0.03); body.add(t);
  }
  const grill = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.16, 0.04), new THREE.MeshStandardMaterial({color: '#111', roughness: 0.5, metalness: 0.5})); grill.position.set(0, 0.6, hx + 0.05); body.add(grill);
  const plate = new THREE.Mesh(new THREE.BoxGeometry(0.52, 0.11, 0.01), new THREE.MeshStandardMaterial({color: '#e8e8e4', roughness: 0.4})); plate.position.set(0, 0.47, hx + 0.08); body.add(plate);
  // Räder
  const tireM = new THREE.MeshStandardMaterial({color: '#151515', roughness: 0.85}), rimM = new THREE.MeshStandardMaterial({color: '#b9bcc2', metalness: 0.95, roughness: 0.25});
  const wheels = [];
  for (const [x, z] of [[-0.8, hx - 0.95], [0.8, hx - 0.95], [-0.8, -hx + 0.95], [0.8, -hx + 0.95]]) {
    const w = new THREE.Group(); w.position.set(x, 0.33, z); car.add(w); const sp = new THREE.Group(); w.add(sp);
    const tire = new THREE.Mesh(new THREE.TorusGeometry(0.25, 0.085, 14, 32), tireM); tire.rotation.y = Math.PI / 2; tire.scale.set(1, 1, 2.3); tire.castShadow = true; sp.add(tire);
    const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.21, 0.18, 32), rimM); rim.rotation.z = Math.PI / 2; sp.add(rim);
    for (let k = 0; k < 5; k++) { const spk = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.36, 0.05), rimM); spk.position.x = Math.sign(x) * 0.095; spk.rotation.x = k * Math.PI * 2 / 5; sp.add(spk); }
    wheels.push(sp);
  }
  // Licht
  const beams = [];
  for (const x of [-0.62, 0.62]) { const sl = new THREE.SpotLight('#f0f4ff', o.beam ?? 60, 40, 0.5, 0.5, 1.5); sl.position.set(x, 0.8, hx + 0.1); sl.target.position.set(x * 1.5, 0.2, hx + 12); sl.castShadow = x < 0; if (sl.castShadow) { sl.shadow.mapSize.set(1024, 1024); sl.shadow.bias = -0.001; } body.add(sl); body.add(sl.target); beams.push(sl); }
  const tailL = new THREE.PointLight('#ff2010', 0.6, 3); tailL.position.set(0, 0.85, -hx - 0.3); body.add(tailL);
  car.userData = {body, wheels, beams, tailM, tailL, L};
  return car;
}
