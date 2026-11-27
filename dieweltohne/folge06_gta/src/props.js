// Kleine Requisiten: Controller, Handy, Dosen, Pizzakarton, Kopfhörer, Konsole
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {canvasTex, rng} from './lib.js';

const plastic = (c, r = 0.45) => new THREE.MeshPhysicalMaterial({color: c, roughness: r, clearcoat: 0.3, clearcoatRoughness: 0.4});
export function controller(color = '#e8e8ea') {
  const g = new THREE.Group(); const m = plastic(color), dark = plastic('#17181b', 0.5);
  const body = new THREE.Mesh(new RoundedBoxGeometry(0.15, 0.03, 0.07, 4, 0.014), m); g.add(body);
  for (const s of [-1, 1]) { const grip = new THREE.Mesh(new THREE.CapsuleGeometry(0.019, 0.05, 6, 12), m); grip.position.set(s * 0.055, -0.006, 0.04); grip.rotation.set(Math.PI / 2 - 0.35, 0, s * 0.35); g.add(grip); }
  const pad = new THREE.Mesh(new RoundedBoxGeometry(0.05, 0.006, 0.03, 2, 0.003), dark); pad.position.set(0, 0.016, -0.008); g.add(pad);
  for (const [x, z] of [[-0.03, 0.012], [0.02, 0.018]]) { const st = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.012, 16), dark); st.position.set(x, 0.019, z); g.add(st); }
  const led = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.002, 0.004), new THREE.MeshStandardMaterial({color: '#4a7dff', emissive: '#4a7dff', emissiveIntensity: 2})); led.position.set(0, 0.0165, -0.025); g.add(led);
  g.userData.led = led;
  g.traverse(o => { o.castShadow = true; o.receiveShadow = true; });
  return g;
}
export function phone() {
  const g = new THREE.Group();
  const b = new THREE.Mesh(new RoundedBoxGeometry(0.072, 0.152, 0.008, 3, 0.006), plastic('#1c1d20', 0.3)); g.add(b);
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.066, 0.145), new THREE.MeshStandardMaterial({color: '#000', emissive: '#000', roughness: 0.1})); scr.position.z = 0.0042; g.add(scr);
  const flash = new THREE.Mesh(new THREE.CircleGeometry(0.004, 12), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#fff', emissiveIntensity: 0})); flash.position.set(0.022, 0.06, -0.0045); flash.rotation.y = Math.PI; g.add(flash);
  g.userData = {scr, flash}; return g;
}
// Getränkedose ohne Marke: Farbe + Streifen
export function can(color = '#1f8f5a', seed = 1, crushed = 0) {
  const r = rng(seed);
  const t = canvasTex(256, 128, g => { g.fillStyle = color; g.fillRect(0, 0, 256, 128); g.fillStyle = 'rgba(255,255,255,0.85)'; g.fillRect(0, 50 + r() * 10, 256, 8); g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(0, 80, 256, 20); });
  const m = new THREE.MeshPhysicalMaterial({map: t, metalness: 0.7, roughness: 0.3, clearcoat: 0.6});
  const geo = new THREE.CylinderGeometry(0.033, 0.033, 0.115, 24, 6); const p = geo.attributes.position;
  if (crushed) for (let i = 0; i < p.count; i++) { const y = p.getY(i); const k = 1 - crushed * Math.exp(-(((y) / 0.03) ** 2)) * (0.3 + 0.2 * Math.sin(Math.atan2(p.getZ(i), p.getX(i)) * 5)); p.setX(i, p.getX(i) * k); p.setZ(i, p.getZ(i) * k); }
  geo.computeVertexNormals();
  const c = new THREE.Mesh(geo, m); c.castShadow = c.receiveShadow = true;
  const top = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.033, 0.006, 24), new THREE.MeshStandardMaterial({color: '#c9ccd0', metalness: 0.9, roughness: 0.3})); top.position.y = 0.06; c.add(top);
  return c;
}
export function pizzaBox(open = 0) {
  const g = new THREE.Group(); const card = new THREE.MeshStandardMaterial({color: '#c9a77a', roughness: 0.95});
  const tex = canvasTex(256, 256, gg => { gg.fillStyle = '#d0ae80'; gg.fillRect(0, 0, 256, 256); gg.strokeStyle = 'rgba(120,40,30,0.7)'; gg.lineWidth = 6; gg.beginPath(); gg.arc(128, 128, 70, 0, 7); gg.stroke(); gg.fillStyle = 'rgba(120,40,30,0.7)'; gg.font = 'bold 34px Plex'; gg.textAlign = 'center'; gg.fillText('PIZZA', 128, 140); });
  const base = new THREE.Mesh(new THREE.BoxGeometry(0.33, 0.04, 0.33), card); base.position.y = 0.02; g.add(base);
  const lid = new THREE.Group(); lid.position.set(0, 0.04, -0.165); g.add(lid);
  const lm = new THREE.Mesh(new THREE.BoxGeometry(0.33, 0.006, 0.33), [card, card, new THREE.MeshStandardMaterial({map: tex, roughness: 0.95}), card, card, card]); lm.position.z = 0.165; lid.add(lm);
  lid.rotation.x = -open;
  if (open) { // zwei Stücke Rest
    const crust = new THREE.MeshStandardMaterial({color: '#b77b3e', roughness: 0.9}), top = new THREE.MeshStandardMaterial({color: '#c8502f', roughness: 0.6});
    for (let i = 0; i < 2; i++) { const s = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.012, 16, 1, false, i * 0.8, 0.75), top); s.position.set(0.0, 0.047, 0.0); g.add(s); }
  }
  g.traverse(o => { o.castShadow = true; o.receiveShadow = true; }); return g;
}
export function headset() {
  const g = new THREE.Group(); const m = plastic('#202124', 0.5), pad = new THREE.MeshStandardMaterial({color: '#151515', roughness: 0.95});
  const band = new THREE.Mesh(new THREE.TorusGeometry(0.09, 0.012, 8, 32, Math.PI), m); g.add(band);
  for (const s of [-1, 1]) { const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.035, 24), m); cup.rotation.z = Math.PI / 2; cup.position.set(s * 0.09, -0.01, 0); g.add(cup); const p = new THREE.Mesh(new THREE.TorusGeometry(0.035, 0.012, 8, 24), pad); p.rotation.y = Math.PI / 2; p.position.set(s * 0.07, -0.01, 0); g.add(p); }
  g.traverse(o => { o.castShadow = true; o.receiveShadow = true; }); return g;
}
// generische Konsole (stehend), ohne Markendesign
export function console_() {
  const g = new THREE.Group();
  const b = new THREE.Mesh(new RoundedBoxGeometry(0.1, 0.36, 0.26, 3, 0.012), plastic('#1a1b1e', 0.35)); b.position.y = 0.18; g.add(b);
  const strip = new THREE.Mesh(new THREE.BoxGeometry(0.004, 0.3, 0.004), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#ffffff', emissiveIntensity: 1.5})); strip.position.set(0.051, 0.18, 0.125); g.add(strip);
  g.userData.strip = strip; g.traverse(o => { o.castShadow = true; o.receiveShadow = true; }); return g;
}
