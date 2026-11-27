// Sein Zimmer bei Nacht: Bett, Fernseher, Konsole, LED-Streifen. Er sitzt auf der Bettkante – Blick zum Fernseher.
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {lerp, smooth, clamp, rng, noise1, canvasTex, envMap, easeOut} from './lib.js';
import {woodFloor, plaster, fabric, carpet, wrinkles, leather} from './tex.js';
import {makeHuman} from './mh.js';
import {sit, stand, mouth, hipY} from './poses.js';
import {makeGame} from './game.js';
import {controller, phone, can, pizzaBox, headset, console_} from './props.js';
import {VANISH, FLASH_ON, POWER_BACK, TV_ON, DOOR, CEIL, TV_OFF} from './timeline.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
function box(w, h, d, m, x, y, z, p, r = 0.01) { const o = new THREE.Mesh(r ? new RoundedBoxGeometry(w, h, d, 2, r) : new THREE.BoxGeometry(w, h, d), m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; p.add(o); return o; }
const std = (c, o = {}) => new THREE.MeshStandardMaterial({color: c, roughness: 0.8, ...o});

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#000');
  const env = envMap(renderer); scene.environment = env; scene.environmentIntensity = 0.04;
  const camera = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.03, 40);
  const R = new THREE.Group(); scene.add(R);
  // ---------- Raum ----------
  const X0 = -1.8, X1 = 1.8, Z0 = -2.0, Z1 = 2.2, HH = 2.5;
  const fl = woodFloor([142, 104, 70], 3);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), new THREE.MeshStandardMaterial({...fl, roughness: 0.55})); floor.material.map.repeat.set(1.4, 1.6); floor.rotation.x = -Math.PI / 2; floor.position.set(0, 0, (Z0 + Z1) / 2); floor.receiveShadow = true; R.add(floor);
  const wallM = new THREE.MeshStandardMaterial({...plaster('#e4dfd6', 4), roughness: 0.92});
  const accM = new THREE.MeshStandardMaterial({...plaster('#3b4250', 6), roughness: 0.9});
  const wall = (w, h, m, pos, ry) => { const o = new THREE.Mesh(new THREE.PlaneGeometry(w, h), m); o.position.copy(pos); o.rotation.y = ry; o.receiveShadow = true; R.add(o); return o; };
  wall(X1 - X0, HH, accM, V(0, HH / 2, Z0), 0);                       // TV-Wand (dunkel gestrichen)
  wall(Z1 - Z0, HH, wallM, V(X0, HH / 2, (Z0 + Z1) / 2), Math.PI / 2); // links (Fenster)
  wall(Z1 - Z0, HH, wallM, V(X1, HH / 2, (Z0 + Z1) / 2), -Math.PI / 2);
  // Rückwand mit Türöffnung (x 0.7..1.6, y 0..2.05)
  const back = new THREE.Group(); R.add(back);
  const bw = (x0, x1, y0, y1) => { const o = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, y1 - y0), wallM); o.position.set((x0 + x1) / 2, (y0 + y1) / 2, Z1); o.rotation.y = Math.PI; o.receiveShadow = true; back.add(o); };
  bw(X0, 0.7, 0, HH); bw(1.6, X1, 0, HH); bw(0.7, 1.6, 2.05, HH);
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(X1 - X0, Z1 - Z0), std('#e8e5df', {roughness: 0.95})); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, HH, (Z0 + Z1) / 2); R.add(ceil);
  // Sockelleisten
  const skM = std('#f2efe9', {roughness: 0.5});
  box(X1 - X0, 0.07, 0.015, skM, 0, 0.035, Z0 + 0.008, R, 0); box(0.015, 0.07, Z1 - Z0, skM, X0 + 0.008, 0.035, (Z0 + Z1) / 2, R, 0); box(0.015, 0.07, Z1 - Z0, skM, X1 - 0.008, 0.035, (Z0 + Z1) / 2, R, 0);
  // Flur hinter der Tür (warmes Licht, wenn Mama kommt)
  const hall = new THREE.Group(); R.add(hall);
  const hallFloor = new THREE.Mesh(new THREE.PlaneGeometry(3, 2), new THREE.MeshStandardMaterial({...woodFloor([150, 112, 76], 8), roughness: 0.5})); hallFloor.rotation.x = -Math.PI / 2; hallFloor.position.set(1.15, 0, Z1 + 1); hall.add(hallFloor);
  const hallWall = new THREE.Mesh(new THREE.PlaneGeometry(3, HH), std('#efe6d8')); hallWall.position.set(1.15, HH / 2, Z1 + 1.4); hallWall.rotation.y = Math.PI; hall.add(hallWall);
  const hallCeil = new THREE.Mesh(new THREE.PlaneGeometry(3, 2), std('#f0ece4')); hallCeil.rotation.x = Math.PI / 2; hallCeil.position.set(1.15, HH, Z1 + 1); hall.add(hallCeil);
  const hallLight = new THREE.PointLight('#ffcf9a', 0, 8, 1.6); hallLight.position.set(1.15, 2.3, Z1 + 0.9); hallLight.castShadow = true; hallLight.shadow.mapSize.set(1024, 1024); hallLight.shadow.bias = -0.002; hall.add(hallLight);
  // Tür (dreht um Scharnier bei x = 0.72)
  const doorPiv = new THREE.Group(); doorPiv.position.set(0.72, 0, Z1); R.add(doorPiv);
  const doorM = std('#f4f1ea', {roughness: 0.45});
  box(0.86, 2.02, 0.04, doorM, 0.43, 1.01, 0.0, doorPiv, 0.004);
  const handle = box(0.12, 0.02, 0.02, std('#b9bcc0', {metalness: 0.9, roughness: 0.25}), 0.76, 1.02, -0.04, doorPiv, 0.004);
  const frameM = std('#f4f1ea', {roughness: 0.5}); box(0.05, 2.08, 0.1, frameM, 0.675, 1.04, Z1, R, 0.004); box(0.05, 2.08, 0.1, frameM, 1.625, 1.04, Z1, R, 0.004); box(1.0, 0.05, 0.1, frameM, 1.15, 2.07, Z1, R, 0.004);
  // Lichtschlitz unter der Tür (bevor sie aufgeht)
  const gap = new THREE.Mesh(new THREE.PlaneGeometry(0.86, 0.012), new THREE.MeshBasicMaterial({color: '#ffcf9a', transparent: true, opacity: 0})); gap.position.set(1.15, 0.006, Z1 - 0.022); gap.rotation.y = Math.PI; R.add(gap);
  // Fenster links mit Jalousie, draußen Stadt bei Nacht
  const winCity = canvasTex(512, 512, g => { const q = rng(17); const gr = g.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, '#05070d'); gr.addColorStop(0.6, '#0c1224'); gr.addColorStop(1, '#1b1d2a'); g.fillStyle = gr; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 18; i++) { const x = q() * 512, w = 30 + q() * 80, h = 120 + q() * 260; g.fillStyle = '#07080c'; g.fillRect(x, 512 - h, w, h); for (let k = 0; k < 40; k++) if (q() < 0.35) { g.fillStyle = q() < 0.7 ? 'rgba(255,200,130,0.9)' : 'rgba(170,200,255,0.8)'; g.fillRect(x + 4 + q() * (w - 10), 512 - h + 6 + q() * (h - 12), 3, 4); } } });
  const outside = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 1.6), new THREE.MeshBasicMaterial({map: winCity, color: '#9aa4b8'})); outside.position.set(X0 - 0.25, 1.45, 1.0); outside.rotation.y = Math.PI / 2; R.add(outside);
  const winFrame = std('#f2f0ec', {roughness: 0.4});
  box(0.08, 0.06, 1.3, winFrame, X0 + 0.03, 0.87, 1.0, R, 0.005); box(0.08, 0.06, 1.3, winFrame, X0 + 0.03, 2.07, 1.0, R, 0.005); box(0.08, 1.26, 0.06, winFrame, X0 + 0.03, 1.47, 0.38, R, 0.005); box(0.08, 1.26, 0.06, winFrame, X0 + 0.03, 1.47, 1.62, R, 0.005);
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.15), new THREE.MeshPhysicalMaterial({color: '#223', roughness: 0.05, transparent: true, opacity: 0.25, metalness: 0.1})); glass.position.set(X0 + 0.02, 1.47, 1.0); glass.rotation.y = Math.PI / 2; R.add(glass);
  // Jalousie halb offen
  const slatM = std('#d9d6cf', {roughness: 0.6, side: THREE.DoubleSide});
  for (let i = 0; i < 22; i++) { const s = new THREE.Mesh(new THREE.BoxGeometry(0.003, 0.045, 1.22), slatM); s.position.set(X0 + 0.07, 2.04 - i * 0.03, 1.0); s.rotation.z = 0.9; s.castShadow = true; if (i < 14) R.add(s); }
  // Vorhang rechts neben dem Fenster
  const curt = new THREE.PlaneGeometry(0.5, 2.3, 24, 8); { const p = curt.attributes.position; for (let i = 0; i < p.count; i++) p.setZ(i, Math.sin(p.getX(i) * 40) * 0.035); curt.computeVertexNormals(); }
  const curtain = new THREE.Mesh(curt, new THREE.MeshStandardMaterial({...fabric('#3c4656', 9, 3), roughness: 0.95, side: THREE.DoubleSide})); curtain.position.set(X0 + 0.12, 1.2, 1.9); curtain.rotation.y = Math.PI / 2; curtain.castShadow = true; R.add(curtain);
  // ---------- Bett ----------
  const bed = new THREE.Group(); R.add(bed);
  const bedM = std('#6e5a48', {roughness: 0.7}); const BX = 0, BZ0 = 0.12, BZ1 = Z1 - 0.02;
  box(1.06, 0.3, BZ1 - BZ0, bedM, BX, 0.17, (BZ0 + BZ1) / 2, bed, 0.01);
  box(1.06, 0.95, 0.06, bedM, BX, 0.48, BZ1 - 0.03, bed, 0.01); // Kopfteil
  const mat = box(0.98, 0.2, BZ1 - BZ0 - 0.08, std('#e9e7e1', {roughness: 0.9}), BX, 0.42, (BZ0 + BZ1) / 2 + 0.01, bed, 0.05);
  // Bettdecke: zerknautschte Fläche über der Matratze
  const dg = new THREE.PlaneGeometry(1.12, 1.55, 60, 80); { const p = dg.attributes.position, q = rng(5); const bumps = []; for (let i = 0; i < 26; i++) bumps.push([q() * 1.1 - 0.55, q() * 1.5 - 0.75, 0.05 + q() * 0.15, 0.02 + q() * 0.05]);
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i); let h = 0.05; for (const [bx, by, r, a] of bumps) h += a * Math.exp(-((x - bx) ** 2 + (y - by) ** 2) / (r * r)); const edge = Math.min(1, (0.56 - Math.abs(x)) / 0.08); h = h * Math.max(0, edge) - (edge < 1 ? (1 - edge) * 0.22 : 0); p.setZ(i, h); }
    dg.computeVertexNormals(); }
  const duvet = new THREE.Mesh(dg, new THREE.MeshStandardMaterial({...fabric('#5f6f86', 11, 4), normalMap: wrinkles(3), normalScale: new THREE.Vector2(0.6, 0.6), roughness: 0.95, side: THREE.DoubleSide}));
  duvet.rotation.x = -Math.PI / 2; duvet.position.set(BX, 0.52, 1.25); duvet.castShadow = duvet.receiveShadow = true; bed.add(duvet);
  const pillow = new THREE.Mesh(new RoundedBoxGeometry(0.6, 0.13, 0.4, 4, 0.06), new THREE.MeshStandardMaterial({...fabric('#dcd8cf', 12, 3), roughness: 0.95})); pillow.position.set(BX - 0.08, 0.6, BZ1 - 0.3); pillow.rotation.set(0.15, 0.1, 0.05); pillow.castShadow = pillow.receiveShadow = true; bed.add(pillow);
  // ---------- TV-Möbel, Fernseher, Konsole, LED ----------
  const TVZ = Z0 + 0.08, TVY = 1.05, TW = 1.23, TH = 0.69;
  const sb = new THREE.MeshStandardMaterial({color: '#e8e5df', roughness: 0.35});
  box(1.7, 0.42, 0.42, sb, 0, 0.23, Z0 + 0.22, R, 0.01); box(1.7, 0.02, 0.43, std('#8a6a4a', {roughness: 0.6}), 0, 0.45, Z0 + 0.22, R, 0.002);
  for (const x of [-0.42, 0.42]) box(0.8, 0.36, 0.005, std('#dfdcd5', {roughness: 0.4}), x, 0.23, Z0 + 0.43, R, 0);
  const tv = new THREE.Group(); tv.position.set(0, TVY, TVZ); R.add(tv);
  box(TW + 0.02, TH + 0.02, 0.03, std('#0b0b0c', {roughness: 0.3, metalness: 0.3}), 0, 0, -0.015, tv, 0.004);
  const game = makeGame(renderer);
  const screenM = new THREE.MeshPhysicalMaterial({color: '#000', emissive: '#ffffff', emissiveMap: game.texture, emissiveIntensity: 1.6, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.05});
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(TW, TH), screenM); screen.position.z = 0.001; tv.add(screen);
  const uiM = new THREE.MeshBasicMaterial({map: game.ui, transparent: true, toneMapped: false, color: new THREE.Color(1.5, 1.5, 1.5)});
  const ui = new THREE.Mesh(new THREE.PlaneGeometry(TW, TH), uiM); ui.position.z = 0.002; tv.add(ui);
  box(0.25, 0.015, 0.2, std('#111', {metalness: 0.5, roughness: 0.4}), 0, -TH / 2 - 0.37 + 0.02, 0.05, tv, 0.003); // Standfuß
  const cons = console_(); cons.position.set(0.62, 0.46, Z0 + 0.2); R.add(cons);
  const led = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.01, 0.01), new THREE.MeshBasicMaterial({color: '#b07bff'})); led.position.set(0, TVY + 0.3, Z0 + 0.03); led.visible = false;
  // Lichter: Bildschirm als Flächenlicht + Spot für Schatten, LED-Glühen an der Wand, Mond durchs Fenster
  const tvLight = new THREE.RectAreaLight('#ffb48a', 6, TW, TH); tvLight.position.set(0, TVY, TVZ + 0.01); tvLight.lookAt(0, TVY, 3); R.add(tvLight);
  const tvSpot = new THREE.SpotLight('#ffb48a', 4, 9, 0.9, 0.9, 1.6); tvSpot.position.set(0, TVY, TVZ + 0.05); tvSpot.target.position.set(0, 0.9, 1.5); R.add(tvSpot); R.add(tvSpot.target);
  tvSpot.castShadow = true; tvSpot.shadow.mapSize.set(2048, 2048); tvSpot.shadow.bias = -0.0008; tvSpot.shadow.radius = 6;
  const ledLight = new THREE.PointLight('#8a48ff', 1.2, 2.2, 1.6); ledLight.position.set(0, TVY + 0.1, Z0 + 0.04); R.add(ledLight);
  const moon = new THREE.RectAreaLight('#8aa6d8', 0.35, 1.2, 1.15); moon.position.set(X0 + 0.05, 1.47, 1.0); moon.lookAt(1, 1.0, 1.0); R.add(moon);
  const ceilLamp = new THREE.PointLight('#fff1dc', 0, 12, 1.4); ceilLamp.position.set(0, HH - 0.25, 0.3); ceilLamp.castShadow = true; ceilLamp.shadow.mapSize.set(1024, 1024); R.add(ceilLamp);
  const lampShade = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 0.14, 32, 1, true), new THREE.MeshStandardMaterial({color: '#f4efe6', emissive: '#fff4e0', emissiveIntensity: 0, side: THREE.DoubleSide, roughness: 0.9})); lampShade.position.set(0, HH - 0.22, 0.3); R.add(lampShade);
  const amb = new THREE.HemisphereLight('#8090b0', '#302820', 0.04); scene.add(amb);
  // ---------- Schreibtisch rechts, Regal, Bilder, Kram ----------
  const deskM = std('#d9d4ca', {roughness: 0.5});
  box(0.7, 0.03, 1.3, deskM, X1 - 0.36, 0.74, -0.8, R, 0.004);
  for (const z of [-1.4, -0.2]) box(0.04, 0.73, 0.6, std('#2a2a2c', {metalness: 0.6, roughness: 0.4}), X1 - 0.36, 0.365, z, R, 0.004);
  const mon = new THREE.Group(); mon.position.set(X1 - 0.25, 0.76, -0.8); mon.rotation.y = -Math.PI / 2; R.add(mon);
  box(0.62, 0.36, 0.03, std('#0d0d0e', {roughness: 0.25}), 0, 0.33, 0, mon, 0.004); box(0.05, 0.2, 0.05, std('#222'), 0, 0.1, -0.05, mon, 0.004); box(0.22, 0.01, 0.16, std('#222'), 0, 0.005, -0.04, mon, 0.003);
  box(0.42, 0.02, 0.14, std('#1a1a1c', {roughness: 0.6}), X1 - 0.48, 0.765, -0.85, R, 0.004); // Tastatur
  // Bürostuhl mit Pulli über der Lehne
  const chair = new THREE.Group(); chair.position.set(X1 - 0.85, 0, -0.75); chair.rotation.y = Math.PI / 2 + 0.5; R.add(chair);
  const leatherM = new THREE.MeshPhysicalMaterial({color: '#1c1c1f', roughness: 0.55, ...leather('#1c1c1f', 2)});
  box(0.5, 0.08, 0.48, leatherM, 0, 0.48, 0, chair, 0.03); box(0.48, 0.7, 0.07, leatherM, 0, 0.9, -0.24, chair, 0.03); box(0.05, 0.4, 0.05, std('#333', {metalness: 0.7, roughness: 0.3}), 0, 0.25, 0, chair, 0.01);
  for (let i = 0; i < 5; i++) { const a = i / 5 * Math.PI * 2; box(0.3, 0.03, 0.04, std('#222'), Math.cos(a) * 0.15, 0.05, Math.sin(a) * 0.15, chair, 0.01).rotation.y = -a; }
  const hoodGeo = new THREE.PlaneGeometry(0.5, 0.5, 20, 20); { const p = hoodGeo.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i); p.setZ(i, Math.sin(x * 18) * 0.015 + (y < 0 ? -y * y * 0.6 : 0)); } hoodGeo.computeVertexNormals(); }
  const hood = new THREE.Mesh(hoodGeo, new THREE.MeshStandardMaterial({...fabric('#8a2c2c', 14, 2), roughness: 0.95, side: THREE.DoubleSide})); hood.position.set(0, 1.05, -0.2); hood.rotation.x = -0.3; hood.castShadow = true; chair.add(hood);
  // Regal mit Büchern über dem Schreibtisch
  box(0.25, 0.02, 1.0, std('#cfc9bf'), X1 - 0.13, 1.55, -0.8, R, 0.003);
  { const q = rng(9); let z = -1.25; const cols = ['#7b2e2e', '#2e4f7b', '#d8c9a8', '#3e6b45', '#222', '#b5893f', '#6b4e7b']; while (z < -0.4) { const w = 0.025 + q() * 0.035, h = 0.18 + q() * 0.08; box(0.16 + q() * 0.04, h, w, std(cols[q() * cols.length | 0], {roughness: 0.8}), X1 - 0.12, 1.56 + h / 2, z + w / 2, R, 0.002); z += w + 0.003; } }
  // Bilderrahmen (abstrakte Drucke)
  const poster = (x, y, z, ry, w, h, seed) => { const t = canvasTex(256, 360, g => { const q = rng(seed); g.fillStyle = '#efe9df'; g.fillRect(0, 0, 256, 360); for (let i = 0; i < 6; i++) { g.fillStyle = ['#d9573b', '#2b4a6f', '#e3b341', '#1d1d1d', '#7aa095'][q() * 5 | 0]; g.beginPath(); g.arc(40 + q() * 176, 60 + q() * 240, 20 + q() * 70, 0, 7); g.fill(); } });
    const f = new THREE.Group(); f.position.set(x, y, z); f.rotation.y = ry; R.add(f); box(w + 0.04, h + 0.04, 0.02, std('#111', {roughness: 0.4}), 0, 0, 0, f, 0.003); const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({map: t, roughness: 0.7})); p.position.z = 0.011; f.add(p);
    const gl = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshPhysicalMaterial({transparent: true, opacity: 0.08, roughness: 0.02, color: '#fff'})); gl.position.z = 0.013; f.add(gl); };
  poster(X1 - 0.01, 1.65, 0.6, -Math.PI / 2, 0.5, 0.7, 4); poster(X1 - 0.01, 1.7, 1.4, -Math.PI / 2, 0.4, 0.56, 7); poster(X0 + 0.01, 1.6, -0.9, Math.PI / 2, 0.6, 0.84, 11);
  // Teppich vor dem Bett
  const rugM = new THREE.MeshStandardMaterial({...carpet('#6d6f74', 5), roughness: 1}); const rug = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.1), rugM); rug.rotation.x = -Math.PI / 2; rug.position.set(0, 0.004, -0.5); rug.receiveShadow = true; R.add(rug);
  // Kram: Dosen, Pizzakarton, Kopfhörer, Socken
  const cans = [can('#1f8f5a', 1), can('#c43b2e', 2, 0.6), can('#1f8f5a', 3), can('#2b5fb0', 4, 0.8)];
  [[0.35, 0.46, Z0 + 0.3], [0.3, 0.06, -0.15], [-0.65, 0.06, -0.25], [0.55, 0.06, -0.6]].forEach(([x, y, z], i) => { cans[i].position.set(x, y, z); if (i === 1) { cans[i].rotation.z = Math.PI / 2; cans[i].position.y = 0.034; } R.add(cans[i]); });
  const pz = pizzaBox(1.9); pz.position.set(-0.55, 0.0, 0.0); pz.rotation.y = 0.4; R.add(pz);
  const hs = headset(); hs.position.set(0.3, 0.6, 0.9); hs.rotation.set(-1.3, 0.4, 0); R.add(hs);
  const ph = phone(); R.add(ph);
  // ---------- Er ----------
  const teen = await makeHuman('teen', {top: '#3a4049', bottom: '#1f2024', shoe: '#2c2c30', hair: '#3a2718', skin: 'light', eye: '#4a3320', hairLen: 0.017, seed: 3});
  R.add(teen.root);
  const pad = controller('#ecebe8'); R.add(pad);
  // ---------- Mama ----------
  const mom = await makeHuman('mom', {top: '#3d5a4b', bottom: '#3a4150', shoe: '#7a6a5e', sneakers: '#c9b8a8', sole: '#e8e2da', hair: '#5a3a24', skin: 'light', eye: '#3e5a4a', hairLen: 0.045, hairDrop: 0.06, seed: 9});
  R.add(mom.root);
  const SEAT = V(0, 0.585, 0.3);
  const tmpQ = new THREE.Quaternion();
  return {scene, camera, update(shot, T) {
    const id = shot.id; const t = T - shot.t0;
    // Zustand des Fernsehers
    let mode = 'game', tvI = 1;
    if (T >= VANISH && T < TV_ON) mode = 'home';
    if (id === 'dark' || (id === 'blast' && T < TV_ON)) { mode = 'off'; }
    if (id === 'vanish') { const k = smooth(VANISH, VANISH + 0.35, T); tvI = k < 1 && T < VANISH + 0.35 ? 0.15 : 1; mode = T < VANISH ? 'game' : 'home'; if (T > VANISH && T < VANISH + 0.25) mode = 'off'; }
    if (id === 'blast' && T >= TV_ON) { mode = 'game'; tvI = 1.0 + 0.6 * Math.exp(-(T - TV_ON) * 2); }
    if (id === 'mom') { mode = T < TV_OFF ? 'game' : 'off'; }
    game.render(T, mode === 'off' ? 'black' : mode);
    const on = mode !== 'off';
    screenM.emissiveIntensity = mode === 'game' ? 1.6 * tvI : 0; uiM.opacity = mode === 'home' ? 1 : mode === 'game' ? 1 : 0;
    uiM.color.setScalar(mode === 'home' ? 1.25 : 1.5);
    const lc = game.light(mode === 'off' ? 'black' : mode); const flick = mode === 'game' ? 0.85 + 0.15 * Math.sin(T * 7.3) * Math.sin(T * 3.1) : 1;
    tvLight.color.copy(lc); tvSpot.color.copy(lc); tvLight.intensity = on ? (mode === 'game' ? 7 : 5) * tvI * flick : 0; tvSpot.intensity = on ? (mode === 'game' ? 5 : 3.5) * tvI * flick : 0;
    // Strom weg (dark): LED, Konsole aus; Stromrückkehr im Blast
    const power = !(id === 'dark' || (id === 'blast' && T < TV_ON - 0.4));
     ledLight.intensity = power ? 1.0 : 0; cons.userData.strip.material.emissiveIntensity = power ? 1.5 : 0;
    // Mama: Tür auf, Flurlicht, dann Deckenlicht
    const doorOpen = id === 'mom' ? easeOut(clamp((T - DOOR) / 0.9)) : 0;
    doorPiv.rotation.y = -doorOpen * 1.45; hallLight.intensity = id === 'mom' ? 14 : 0; gap.material.opacity = id === 'mom' && T < DOOR ? 0.9 : 0; hall.visible = id === 'mom';
    const ce = id === 'mom' ? smooth(CEIL, CEIL + 0.12, T) : 0; ceilLamp.intensity = ce * 4; lampShade.material.emissiveIntensity = ce * 1.2; amb.intensity = 0.04 + ce * 0.25;
    mom.root.visible = id === 'mom' && T > DOOR + 0.2;
    // ---------- Er: Pose ----------
    teen.root.position.set(SEAT.x, SEAT.y - hipY(teen), SEAT.z); teen.root.rotation.set(0, Math.PI, 0);
    let o = {lean: 0.2, nod: -0.02, grip: 0.72, hands: 'pad'};
    const bob = Math.sin(T * 1.3) * 0.02;
    if (id === 'intro' || id === 'play') { o.lean = 0.24 + bob + (id === 'play' ? Math.sin(t * 0.8) * 0.03 : 0); o.yaw = Math.sin(T * 0.7) * 0.04; }
    if (id === 'vanish') { const s = smooth(0.4, 1.2, t), s2 = smooth(3.0, 3.6, t); o.lean = lerp(0.24, 0.42, s) - s2 * 0.25; o.nod = lerp(-0.02, 0.06, s); o.hands = s2 > 0.5 ? 'head' : 'pad'; o.handsK = 1; o.grip = 0.72; }
    if (id === 'dark') { const s = smooth(FLASH_ON - 0.8 - shot.t0, FLASH_ON - shot.t0, t); o.lean = 0.12; o.hands = s > 0.5 ? 'phone' : 'lap'; o.nod = 0.05; }
    if (id === 'blast') { const j = smooth(TV_ON, TV_ON + 0.25, T); o.lean = lerp(0.1, -0.12, j) + Math.exp(-Math.max(0, T - TV_ON) * 4) * 0.08 * (T > TV_ON); o.hands = j > 0.3 ? 'brace' : 'lap'; o.nod = lerp(0.05, -0.12, j); }
    if (id === 'mom') { const s = smooth(DOOR + 0.6, DOOR + 1.4, T); o.lean = 0.1; o.hands = 'pad'; o.yaw = lerp(0, 1.15, s); o.twist = lerp(0, 0.6, s); o.nod = 0.02; }
    sit(teen, o);
    if (id === 'vanish') { mouth(teen, smooth(0.6, 1.4, t) * 0.9); teen.look(0, 0.05); } else if (id === 'blast') mouth(teen, smooth(TV_ON, TV_ON + 0.2, T) * 0.7); else mouth(teen, 0.05);
    if (id === 'mom') teen.look(0.45 * smooth(DOOR + 0.6, DOOR + 1.4, T), 0.1);
    // Controller zwischen den Händen
    teen.root.updateMatrixWorld(true);
    const hl = new THREE.Vector3(), hr = new THREE.Vector3(); teen.B('wrist.L').getWorldPosition(hl); teen.B('wrist.R').getWorldPosition(hr);
    pad.visible = o.hands === 'pad' || o.hands === 'lap';
    if (pad.visible) {
      const mid = hl.clone().add(hr).multiplyScalar(0.5); const fw = new THREE.Vector3(0, 0, -1);
      if (o.hands === 'pad') { pad.position.copy(mid).add(V(0, 0.015, -0.06)); pad.rotation.set(0.55, 0, 0); pad.rotation.y = Math.atan2(hl.x - hr.x, hl.z - hr.z) + Math.PI / 2; pad.rotation.order = 'YXZ'; pad.rotation.x = 0.5; }
      else { pad.position.copy(mid).add(V(0, 0.0, -0.08)); pad.rotation.set(0.1, 0.2, 0); }
    }
    pad.userData.led.material.emissiveIntensity = power ? 2 : 0;
    // Handy: im Dunkeln Taschenlampe
    ph.visible = id === 'dark';
    if (id === 'dark') { teen.B('wrist.R').getWorldPosition(hr); ph.position.copy(hr).add(V(0.0, 0.06, -0.05)); ph.rotation.set(-0.3, 0, 0.15); const fon = smooth(FLASH_ON - 0.05, FLASH_ON + 0.05, T); ph.userData.flash.material.emissiveIntensity = fon * 6; ph.userData.scr.material.emissive.set('#a0b8ff'); ph.userData.scr.material.emissiveIntensity = 0.6; }
    if (!R.userData.flashL) { const fl = new THREE.SpotLight('#eef3ff', 0, 8, 0.7, 0.6, 1.4); fl.castShadow = true; fl.shadow.mapSize.set(1024, 1024); R.add(fl); R.add(fl.target); R.userData.flashL = fl; }
    if (!R.userData.glow) { const gl = new THREE.PointLight('#9fb4ff', 0, 1.2, 2); R.add(gl); R.userData.glow = gl; }
    const glow = R.userData.glow; glow.intensity = id === 'dark' ? 0.12 : 0; if (id === 'dark') glow.position.copy(ph.position).add(V(0, 0, 0.12));
    const flashL = R.userData.flashL; flashL.intensity = id === 'dark' ? smooth(FLASH_ON - 0.05, FLASH_ON + 0.05, T) * 5 : 0;
    if (id === 'dark') { flashL.position.copy(ph.position).add(V(0, 0.05, -0.02)); flashL.target.position.set(Math.sin(T * 0.6) * 0.6, 0.9, -2.0); }
    // ---------- Mama ----------
    if (mom.root.visible) {
      const k = smooth(DOOR + 0.2, DOOR + 1.6, T);
      mom.root.position.set(1.15, 0, lerp(Z1 + 0.7, Z1 - 0.05, k)); mom.root.rotation.y = Math.PI + 0.25;
      stand(mom, {walk: k * 5, amp: (1 - k) * 0.8 + 0.0, hands: T > CEIL + 0.8 ? (T > CEIL + 2.0 ? 'give' : 'hips') : 'swing', handsK: 1, nod: -0.05, yaw: -0.2});
      mouth(mom, T > 83 && T < 86.4 ? 0.25 + 0.25 * Math.abs(Math.sin(T * 9)) : 0);
      mom.look(-0.2, 0.05);
    }
    // ---------- Kamera ----------
    const hand = (a, b) => V(noise1(T * a, 1) * b, noise1(T * a, 7) * b, noise1(T * a, 13) * b * 0.5);
    let pos, look, fov = 40, dof = null, exposure = 1.0, ao = true;
    const head = new THREE.Vector3(); teen.B('head').getWorldPosition(head);
    if (id === 'intro') { // über die rechte Schulter auf den Fernseher
      pos = V(0.28, 1.42, 1.25).add(V(0, -t * 0.02, -t * 0.1)).add(hand(0.7, 0.008)); look = V(-0.02, 0.92, Z0); fov = 50; dof = {focus: 3.2, aperture: 0.0012, maxblur: 0.008}; exposure = 1.15;
    } else if (id === 'play') { // vorne links unten: Gesicht im Fernsehlicht, Zimmer dahinter
      pos = V(-0.75, 1.3, -0.75).add(V(t * 0.025, 0, -t * 0.01)).add(hand(0.6, 0.01)); look = head.clone().add(V(0.05, -0.2, 0)); fov = 40; dof = {focus: pos.distanceTo(head), aperture: 0.0012, maxblur: 0.006}; exposure = 1.25;
    } else if (id === 'vanish') { // von vorne, Höhe Fernseher, langsam ran
      pos = V(0.05, 1.12, -1.05 + t * 0.05).add(hand(0.8, 0.008)); look = head.clone().add(V(0, -0.08, 0)); fov = 34; dof = {focus: pos.distanceTo(head), aperture: 0.0014, maxblur: 0.007}; exposure = 1.35;
    } else if (id === 'dark') {
      pos = V(-0.7, 1.15, -0.45).add(hand(0.5, 0.008)); look = head.clone().add(V(0.1, -0.22, -0.1)); fov = 42; dof = {focus: pos.distanceTo(head), aperture: 0.0012, maxblur: 0.006}; exposure = 1.5;
    } else if (id === 'blast') { // von vorne: dunkel, dann knallt das Fernsehlicht ins Gesicht
      const shake = T > TV_ON ? Math.exp(-(T - TV_ON) * 3) * 0.02 : 0;
      pos = V(0.3, 1.12, -0.95).add(hand(0.5, 0.006)).add(V(Math.sin(T * 40) * shake, Math.cos(T * 37) * shake, 0)); look = head.clone().add(V(-0.05, -0.18, 0)); fov = 44; dof = {focus: pos.distanceTo(head), aperture: 0.0012, maxblur: 0.006}; exposure = T < TV_ON ? 1.5 : 1.1;
    } else if (id === 'mom') { // vom Fernseher aus: er vorne, Tür und Mama dahinter
      pos = V(-0.15, 1.18, -1.4).add(hand(0.5, 0.006)); look = V(0.45, 1.15, 1.6); fov = 42; dof = {focus: 2.6, aperture: 0.0008, maxblur: 0.005}; exposure = T > CEIL ? 0.85 : 1.15;
    }
    camera.position.copy(pos); camera.lookAt(look); camera.fov = fov; camera.updateProjectionMatrix();
    return {dof, exposure, bloom: [0.45, 0.55, 0.8], grain: 0.055, vig: 0.38, ao};
  }};
}
