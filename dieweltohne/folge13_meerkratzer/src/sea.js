// Der gläserne Aufzug am Turm – und alles, was draußen vorbeizieht.
// Der Aufzug bleibt im Ursprung; die Tiefe wird über Licht, Nebel, Fassade, Schwebeteilchen und die Begegnungen erzählt.
import {THREE, mat, mesh, rng, clamp, lerp, smooth, easeOut, easeIn, canvasTex, envMap, noise1} from './lib.js';
import {particles} from './fx.js';
import {updateParticles} from './fx.js';
import {depthAt, speedAt, PRESS, START, SHADOW, WHALE_FLEE, LIGHTS_OUT, LURE, LIGHTS_ON, CRACK, ARRIVE, KNOCK, SUB, BOX} from './timeline.js';
import {fishSchool, updateSchool, spermWhale, swimWhale, giantSquid, anglerfish, snailfish, submersible, glowTex, hull} from './creatures.js';

const C = (a, b, k) => new THREE.Color(a).lerp(new THREE.Color(b), clamp(k));
const FOG = [[0, '#1d97b8'], [30, '#127aa1'], [150, '#0a4c78'], [330, '#062c52'], [720, '#02152a'], [1000, '#01070f'], [2500, '#000306'], [11000, '#000204']];
function fogCol(d) { for (let i = 1; i < FOG.length; i++) if (d <= FOG[i][0]) return C(FOG[i - 1][1], FOG[i][1], (d - FOG[i - 1][0]) / (FOG[i][0] - FOG[i - 1][0])); return new THREE.Color(FOG[FOG.length - 1][1]); }

function facadeTex() {
  const r = rng(31);
  const base = canvasTex(256, 1024, (g, w, h) => {
    g.fillStyle = '#2b383e'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 2500; i++) { g.fillStyle = `rgba(255,255,255,${r() * 0.04})`; g.fillRect(r() * w, r() * h, 2, 2); }
    for (let i = 0; i < 60; i++) { g.fillStyle = `rgba(60,90,70,${0.15 + r() * 0.2})`; g.beginPath(); g.ellipse(r() * w, r() * h, 6 + r() * 30, 3 + r() * 10, 0, 0, 7); g.fill(); } // Bewuchs
    for (let y = 0; y < 16; y++) for (let x = 0; x < 4; x++) {
      const px = x * 64 + 8, py = y * 64 + 10;
      g.fillStyle = '#0d181d'; g.fillRect(px, py, 48, 40); g.fillStyle = 'rgba(160,210,230,0.12)'; g.fillRect(px + 2, py + 2, 20, 36);
      g.fillStyle = '#56676e'; g.fillRect(px - 2, py + 40, 52, 5);
    }
  });
  const r2 = rng(33);
  const emi = canvasTex(256, 1024, (g, w, h) => {
    g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < 16; y++) for (let x = 0; x < 4; x++) if (r2() < 0.4) {
      const px = x * 64 + 8, py = y * 64 + 10, warm = r2() < 0.7;
      const gr = g.createLinearGradient(px, py, px, py + 40); gr.addColorStop(0, warm ? '#ffd79a' : '#bfe6ff'); gr.addColorStop(1, warm ? '#d9934a' : '#6fa8d8');
      g.fillStyle = gr; g.fillRect(px, py, 48, 40);
    }
  });
  for (const t of [base, emi]) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
  return {base, emi};
}
function dotTex() { return canvasTex(64, 64, g => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); }); }
function beamTex() { return canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.15, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }); }

function panelTex(pressed) {
  return canvasTex(512, 1280, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, w, 0); gr.addColorStop(0, '#9da3a6'); gr.addColorStop(0.5, '#c3c8ca'); gr.addColorStop(1, '#959b9e'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(3); for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(255,255,255,${r() * 0.12})`; g.fillRect(0, r() * h, w, 1); }
    g.fillStyle = '#1c2124'; g.fillRect(40, 40, w - 80, 120); g.fillStyle = pressed ? '#ffb347' : '#ff9d2e'; g.font = '500 64px Plex'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(pressed ? '▼   0' : '0', w / 2, 102);
    const btn = (x, y, label, lit) => {
      g.fillStyle = '#6d7377'; g.beginPath(); g.arc(x, y, 40, 0, 7); g.fill();
      const b = g.createRadialGradient(x - 10, y - 10, 4, x, y, 36); b.addColorStop(0, lit ? '#fff4d6' : '#e8eaeb'); b.addColorStop(1, lit ? '#ffb347' : '#9aa0a3'); g.fillStyle = b; g.beginPath(); g.arc(x, y, 34, 0, 7); g.fill();
      if (lit) { g.strokeStyle = '#ffcf7a'; g.lineWidth = 6; g.beginPath(); g.arc(x, y, 42, 0, 7); g.stroke(); }
      g.fillStyle = '#2a2f32'; g.font = '500 30px Plex'; g.fillText(label, x + (x < w / 2 ? 0 : 0), y + 64);
    };
    const labels = ['0', '−1', '−2', '−3', '−4', '−5', '−6', '−7'];
    labels.forEach((l, i) => btn(i % 2 ? 360 : 152, 250 + Math.floor(i / 2) * 140, l, false));
    g.fillStyle = '#2a2f32'; g.font = '500 64px Plex'; g.fillText('⋮', w / 2, 830);
    btn(152, 940, '−3.638', false); btn(360, 940, '−3.639', false);
    // der unterste Knopf, abgeklebt
    btn(w / 2, 1120, '', pressed);
    g.save(); g.translate(w / 2, 1120); g.rotate(-0.12);
    g.fillStyle = pressed ? 'rgba(232,206,92,0.55)' : 'rgba(232,206,92,0.95)'; g.fillRect(-200, -38, 400, 76);
    g.fillStyle = '#1a1a1a'; g.font = '500 36px Plex'; g.fillText('NICHT DRÜCKEN', 0, 2); g.restore();
    g.fillStyle = '#2a2f32'; g.font = '500 30px Plex'; g.fillText('−3.640', w / 2, 1215);
  });
}

function rockGeo(seed, detail = 4) {
  const g = new THREE.IcosahedronGeometry(1, detail); const p = g.attributes.position; const r = rng(seed); const a = Array.from({length: 9}, () => r() * 6);
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const k = 1 + 0.18 * Math.sin(x * 3 + a[0]) * Math.sin(y * 2.4 + a[1]) + 0.1 * Math.sin(z * 6 + a[2] + x * 2) + 0.05 * Math.sin(x * 13 + y * 11 + a[3]);
    p.setXYZ(i, x * k, y * k, z * k); }
  g.computeVertexNormals(); return g;
}
function rockWall(seed, w, h, amp) {
  const g = new THREE.PlaneGeometry(w, h, 90, 90); const p = g.attributes.position; const r = rng(seed); const a = Array.from({length: 8}, () => r() * 6);
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i);
    p.setZ(i, amp * (Math.sin(x * 0.21 + a[0]) * Math.sin(y * 0.17 + a[1]) + 0.5 * Math.sin(x * 0.53 + y * 0.31 + a[2]) + 0.25 * Math.sin(x * 1.3 - y * 1.1 + a[3]) + 0.12 * Math.sin(x * 3.1 + y * 2.7 + a[4]))); }
  g.computeVertexNormals(); return g;
}
function rockTex(seed, base) {
  const r = rng(seed);
  const t = canvasTex(512, 512, (g, w, h) => { g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 7000; i++) { const v = r(); g.fillStyle = v < 0.5 ? `rgba(0,0,0,${0.1 + r() * 0.2})` : `rgba(200,190,170,${r() * 0.12})`; g.beginPath(); g.arc(r() * w, r() * h, 1 + r() * 5, 0, 7); g.fill(); } });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
function sedimentTex() {
  const r = rng(61);
  const t = canvasTex(1024, 1024, (g, w, h) => { g.fillStyle = '#8a8274'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 30000; i++) { const v = 100 + r() * 60; g.fillStyle = `rgba(${v},${v - 6},${v - 18},0.35)`; g.fillRect(r() * w, r() * h, 2, 2); }
    for (let i = 0; i < 40; i++) { g.strokeStyle = 'rgba(60,55,45,0.35)'; g.lineWidth = 3; g.beginPath(); let x = r() * w, y = r() * h; g.moveTo(x, y); for (let k = 0; k < 20; k++) { x += Math.cos(k * 0.4 + i) * 12; y += Math.sin(k * 0.3 + i) * 12; g.lineTo(x, y); } g.stroke(); } // Spuren
    for (let i = 0; i < 120; i++) { g.fillStyle = 'rgba(50,45,38,0.4)'; g.beginPath(); g.arc(r() * w, r() * h, 2 + r() * 4, 0, 7); g.fill(); } });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(12, 12); return t;
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(52, 1080 / 1920, 0.01, 400);
  const env = envMap(renderer);
  const fog = new THREE.FogExp2('#127aa1', 0.03); scene.fog = fog;
  const hemi = new THREE.HemisphereLight('#a8e6ff', '#06213a', 1.4); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#d8f6ff', 1.6); sun.position.set(4, 30, -8); scene.add(sun);

  // ---------- Kabine ----------
  const cabin = new THREE.Group(); scene.add(cabin);
  const steel = new THREE.MeshStandardMaterial({color: '#b9bec1', metalness: 0.8, roughness: 0.35, envMap: env});
  const darkM = new THREE.MeshStandardMaterial({color: '#2b3034', metalness: 0.6, roughness: 0.4, envMap: env});
  const floorM = new THREE.MeshStandardMaterial({color: '#3b3d40', roughness: 0.55, metalness: 0.1, envMap: env, envMapIntensity: 0.4});
  mesh(new THREE.BoxGeometry(2.8, 0.1, 2.7), floorM, 0, -0.05, 0, cabin);
  mesh(new THREE.BoxGeometry(2.8, 0.1, 2.7), mat('#d9d8d3', {roughness: 0.6}), 0, 2.78, 0, cabin);
  const lamp = mesh(new THREE.PlaneGeometry(1.7, 1.2), new THREE.MeshBasicMaterial({color: '#fff1d8'}), 0, 2.72, 0, cabin); lamp.rotation.x = Math.PI / 2;
  // Glas vorn und rechts
  const glassM = new THREE.MeshPhysicalMaterial({color: '#bfe2ee', roughness: 0.02, metalness: 0, transparent: true, opacity: 0.08, envMap: env, envMapIntensity: 0.25, depthWrite: false, side: THREE.DoubleSide});
  mesh(new THREE.PlaneGeometry(2.7, 2.75), glassM, 0, 1.37, -1.3, cabin);
  const gr = mesh(new THREE.PlaneGeometry(2.6, 2.75), glassM, 1.35, 1.37, 0, cabin); gr.rotation.y = -Math.PI / 2;
  // Rahmen
  for (const [x, z] of [[-1.35, -1.3], [1.35, -1.3], [1.35, 1.3]]) mesh(new THREE.BoxGeometry(0.09, 2.85, 0.09), darkM, x, 1.37, z, cabin);
  mesh(new THREE.BoxGeometry(2.8, 0.14, 0.1), darkM, 0, 0.07, -1.3, cabin); mesh(new THREE.BoxGeometry(2.8, 0.12, 0.1), darkM, 0, 2.72, -1.3, cabin);
  mesh(new THREE.BoxGeometry(0.1, 0.14, 2.7), darkM, 1.35, 0.07, 0, cabin); mesh(new THREE.BoxGeometry(0.1, 0.12, 2.7), darkM, 1.35, 2.72, 0, cabin);
  // linke Wand (am Turm), Rückwand mit Türen
  mesh(new THREE.BoxGeometry(0.06, 2.8, 2.7), steel, -1.36, 1.37, 0, cabin);
  mesh(new THREE.BoxGeometry(2.7, 2.8, 0.06), steel, 0, 1.37, 1.33, cabin);
  // Haltestangen
  const chrome = new THREE.MeshStandardMaterial({color: '#e8ecef', metalness: 1, roughness: 0.15, envMap: env});
  const hr = mesh(new THREE.CylinderGeometry(0.022, 0.022, 2.5, 12), chrome, 0, 0.95, -1.18, cabin); hr.rotation.z = Math.PI / 2;
  const hr2 = mesh(new THREE.CylinderGeometry(0.022, 0.022, 2.4, 12), chrome, 1.23, 0.95, 0, cabin); hr2.rotation.x = Math.PI / 2;
  // Bedienfeld an der linken Wand, vorn
  const pTex = [panelTex(false), panelTex(true)];
  const panelM = new THREE.MeshStandardMaterial({map: pTex[0], roughness: 0.35, metalness: 0.5, envMap: env, envMapIntensity: 0.6, emissive: '#000000', emissiveMap: pTex[1]});
  const panel = mesh(new THREE.PlaneGeometry(0.34, 0.85), panelM, -1.325, 1.22, -0.7, cabin); panel.rotation.y = Math.PI / 2;
  // Finger, der drückt
  const hand = new THREE.Group(); scene.add(hand);
  const skin = mat('#e0b090', {roughness: 0.6});
  const palm = mesh(new THREE.SphereGeometry(0.045, 18, 14), skin, 0.05, -0.012, 0, hand); palm.scale.set(1.25, 0.95, 0.62);
  const idx = mesh(new THREE.CapsuleGeometry(0.0085, 0.06, 6, 10), skin, -0.03, 0.012, 0, hand); idx.rotation.z = Math.PI / 2;
  for (let i = 0; i < 3; i++) { const f = mesh(new THREE.CapsuleGeometry(0.0085, 0.018, 6, 10), skin, 0.004, -0.01 - i * 0.016, 0.012, hand); f.rotation.set(0.9, 0, Math.PI / 2); }
  const thumb = mesh(new THREE.CapsuleGeometry(0.009, 0.03, 6, 10), skin, 0.02, 0.012, 0.028, hand); thumb.rotation.set(0.3, 0.6, Math.PI / 2);
  const sleeve = mesh(new THREE.CylinderGeometry(0.048, 0.058, 0.3, 18), mat('#24374f', {roughness: 0.95}), 0.25, -0.012, 0, hand); sleeve.rotation.z = Math.PI / 2;
  // Licht innen
  const inLight = new THREE.PointLight('#ffe3bd', 5, 7, 1.5); inLight.position.set(0, 2.45, 0.1); scene.add(inLight);
  const nearL = new THREE.PointLight('#d8ecff', 0, 6, 1.6); nearL.position.set(0.7, 2.95, -1.8); scene.add(nearL);
  // Außenscheinwerfer + Lichtkegel
  const floods = [], beams = []; const bt = beamTex();
  for (const [x, tx] of [[-0.9, -1.5], [0.9, 2.8]]) {
    const s = new THREE.SpotLight('#eaf4ff', 0, 45, 0.5, 0.65, 1.5); s.position.set(x, 2.95, -1.45); s.target.position.set(tx, -3.5, -15); scene.add(s, s.target); floods.push(s);
    const cone = new THREE.Mesh(new THREE.ConeGeometry(4.6, 15, 32, 1, true), new THREE.MeshBasicMaterial({map: bt, color: '#bfe2ff', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false}));
    cone.geometry.translate(0, -7.5, 0); cone.position.copy(s.position); const dir = new THREE.Vector3().subVectors(s.target.position, s.position).normalize();
    cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir); scene.add(cone); beams.push(cone);
  }

  // ---------- Turm (links, Fassade zur Kabine) und Führungsschienen ----------
  const ft = facadeTex(); ft.base.repeat.set(13 / 12.8, 140 / 48); ft.emi.repeat.set(13 / 12.8, 140 / 48);
  const towerM = new THREE.MeshStandardMaterial({map: ft.base, emissiveMap: ft.emi, emissive: '#ffffff', emissiveIntensity: 1.2, roughness: 0.6, metalness: 0.2});
  const tower = mesh(new THREE.BoxGeometry(13, 140, 13), towerM, -1.6 - 6.5, 0, -3 + 6.5, scene);
  const railM = new THREE.MeshStandardMaterial({color: '#6f7a80', metalness: 0.8, roughness: 0.35, envMap: env});
  for (const z of [-1.05, 1.05]) mesh(new THREE.BoxGeometry(0.16, 140, 0.16), railM, -1.5, 0, z, scene);
  const brk = new THREE.InstancedMesh(new THREE.BoxGeometry(0.2, 0.12, 0.5), railM, 80); scene.add(brk); brk.frustumCulled = false;

  // ---------- Schwebeteilchen ("Meeresschnee") ----------
  const NS = 1600, sp = new Float32Array(NS * 3), sb = []; const sr = rng(9);
  for (let i = 0; i < NS; i++) sb.push([lerp(-1.3, 14, sr()), sr() * 40, lerp(-26, -1.45, sr()), sr() * 6]);
  for (let i = 0; i < 300; i++) sb[i][0] = lerp(1.45, 12, sr()), sb[i][2] = lerp(-1.3, 6, sr());
  const sgeo = new THREE.BufferGeometry(); sgeo.setAttribute('position', new THREE.BufferAttribute(sp, 3));
  const snowM = new THREE.PointsMaterial({map: dotTex(), color: '#e4f2f5', size: 0.045, transparent: true, opacity: 0.7, depthWrite: false});
  const snow = new THREE.Points(sgeo, snowM); snow.frustumCulled = false; scene.add(snow);
  // Leuchtpünktchen (Biolumineszenz)
  const bio = particles(500, 'glow'); scene.add(bio); const bioSeed = []; const br = rng(17);
  for (let i = 0; i < 500; i++) bioSeed.push([lerp(-1.3, 9, br()), lerp(-3, 6, br()), lerp(-16, -1.5, br()), br() * 6, br() < 0.7 ? 0 : (br() < 0.5 ? 1 : 2), br()]);
  // Sonnenstrahlen (nur oben)
  const rays = [], rt = beamTex(); const rr = rng(4);
  for (let i = 0; i < 10; i++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(1.5 + rr() * 3, 40), new THREE.MeshBasicMaterial({map: rt, color: '#c9f6ff', transparent: true, opacity: 0.14, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false}));
    m.position.set(lerp(-1, 10, rr()), 8, lerp(-16, -4, rr())); m.rotation.set(0.15, rr() * 3, 0.2); m.geometry.translate(0, -12, 0); scene.add(m); rays.push(m); }

  // ---------- Begegnungen ----------
  const school = fishSchool(340); scene.add(school);
  const whale = spermWhale(); scene.add(whale);
  const squid = giantSquid(); scene.add(squid); squid.userData.arms.forEach(a => scene.add(a.mesh)); scene.add(squid.userData.suck);
  const angler = anglerfish(); scene.add(angler);
  const snail = snailfish(); scene.add(snail);
  const sub = submersible(); scene.add(sub);
  // Schwarze Raucher auf einem Felsabsatz
  const vent = new THREE.Group(); scene.add(vent);
  const basalt = new THREE.MeshStandardMaterial({map: rockTex(5, '#3a3430'), roughness: 0.95, color: '#9a8f86'});
  const ledge = mesh(rockGeo(3), basalt, 4, -9, -17, vent); ledge.scale.set(11, 5, 8);
  const chimneys = [];
  for (const [x, y, z, hgt, s] of [[0.8, -5.2, -12.5, 5.5, 1], [3.8, -4.8, -15.5, 7.5, 2], [6.5, -5.8, -19, 4.2, 3], [-0.6, -5.6, -16, 3.2, 4]]) {
    const pts = []; const r = rng(s * 13);
    for (let i = 0; i <= 16; i++) { const u = i / 16; pts.push(new THREE.Vector2(lerp(0.75, 0.22, Math.pow(u, 0.7)) * (0.8 + 0.4 * r()), u * hgt)); }
    const g = new THREE.LatheGeometry(pts, 20); const p = g.attributes.position; const col = [];
    for (let i = 0; i < p.count; i++) { const px = p.getX(i), py = p.getY(i), pz = p.getZ(i); const n = 1 + 0.18 * Math.sin(py * 3.1 + s) * Math.sin(Math.atan2(pz, px) * 5 + py) + 0.08 * Math.sin(py * 11 + px * 7);
      p.setXYZ(i, px * n, py, pz * n); const k = Math.sin(py * 2.3 + s * 2 + Math.atan2(pz, px) * 3);
      const nz = 0.5 + 0.5 * Math.sin(py * 7.3 + px * 13 + s) * Math.sin(Math.atan2(pz, px) * 7 + py * 2); const c = new THREE.Color('#231e1b').lerp(new THREE.Color(k > 0.75 ? '#6b5536' : '#4a423b'), nz * (k > 0.3 ? 0.9 : 0.35)); col.push(c.r, c.g, c.b); }
    g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.computeVertexNormals();
    const m = mesh(g, new THREE.MeshStandardMaterial({vertexColors: true, roughness: 0.9}), x, y, z, vent); chimneys.push({top: new THREE.Vector3(x, y + hgt, z), s});
  }
  // Röhrenwürmer und weiße Krebse am Fuß
  const worms = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.03, 0.04, 0.6, 6), mat('#e9e4da', {roughness: 0.7}), 60), tips = new THREE.InstancedMesh(new THREE.SphereGeometry(0.06, 8, 6), mat('#c4232b', {roughness: 0.5}), 60);
  { const r = rng(44); const M = new THREE.Matrix4(); for (let i = 0; i < 60; i++) { const c = chimneys[i % 4]; const a = r() * 6.28, d = 0.8 + r() * 0.8; const x = c.top.x + Math.cos(a) * d, z = c.top.z + Math.sin(a) * d; const y = -5.2 + r() * 0.3;
    M.makeRotationFromEuler(new THREE.Euler((r() - 0.5) * 0.5, 0, (r() - 0.5) * 0.5)).setPosition(x, y + 0.3, z); worms.setMatrixAt(i, M); M.makeTranslation(x + 0, y + 0.62, z); tips.setMatrixAt(i, M); } }
  vent.add(worms, tips);
  const smoke = particles(1400, 'smoke'); vent.add(smoke);
  // Grabenwände
  const wallM = new THREE.MeshStandardMaterial({map: rockTex(9, '#38332e'), roughness: 0.95, color: '#8d857c'}); wallM.map.repeat.set(6, 6);
  const wallR = mesh(rockWall(2, 120, 120, 2.4), wallM, 13, 0, -20, scene); wallR.rotation.y = -Math.PI / 2;
  const wallB = mesh(rockWall(7, 140, 120, 3), wallM, 0, 0, -48, scene);
  // Meeresboden ganz unten
  const floor = mesh(new THREE.PlaneGeometry(160, 160, 60, 60), new THREE.MeshStandardMaterial({map: sedimentTex(), roughness: 1, color: '#c9c0b0'}), 0, -1.3, -40, scene); floor.rotation.x = -Math.PI / 2;
  { const p = floor.geometry.attributes.position; for (let i = 0; i < p.count; i++) p.setZ(i, 0.25 * Math.sin(p.getX(i) * 0.3) * Math.sin(p.getY(i) * 0.25) + 0.1 * Math.sin(p.getX(i) * 1.1 + p.getY(i))); floor.geometry.computeVertexNormals(); }
  const cukes = []; // Seegurken
  for (const [x, z, s] of [[1.2, -4.2, 1], [-0.4, -6.5, 0.8], [2.8, -8, 1.1]]) { const c = new THREE.Mesh(hull(0.35 * s, u => { const r = 0.06 * s * Math.sin(Math.PI * clamp(u * 1.05)) + 0.01; return [r, r * 1.1, 2, 0]; }, 16, 12),
    new THREE.MeshPhysicalMaterial({color: '#e7a9a4', roughness: 0.3, transmission: 0.3, transparent: true, opacity: 0.85, clearcoat: 0.6})); c.position.set(x, 0, z); c.rotation.y = x; scene.add(c); cukes.push(c); }

  // ---------- Hilfen ----------
  const show = (o, v) => { o.visible = v; };
  const _M = new THREE.Matrix4(), _v = new THREE.Vector3(), _q = new THREE.Quaternion();

  function setEnv(d, T, shot) {
    const fc = fogCol(d); fog.color.copy(fc); renderer.setClearColor(fc);
    fog.density = lerp(0.03, 0.055, smooth(0, 1200, d));
    const L = Math.exp(-d / 170);
    hemi.intensity = 1.6 * L + 0.02; hemi.color.copy(C('#a8e6ff', '#2c6aa8', d / 400)); sun.intensity = 1.8 * Math.exp(-d / 60);
    rays.forEach((m, i) => { m.visible = d < 60; m.material.opacity = (0.1 + 0.05 * Math.sin(T * 1.2 + i * 1.7)) * (1 - d / 60); });
  }
  function scroll(d) { // Fassade, Halterungen und Teilchen wandern beim Abwärtsfahren nach oben
    ft.base.offset.y = ft.emi.offset.y = -d / 48;
    for (let i = 0; i < 80; i++) { const side = i < 40 ? -1.05 : 1.05; const k = i % 40; const y = (((k * 3.5 + d) % 140) + 140) % 140 - 70;
      _M.makeTranslation(-1.42, y, side); brk.setMatrixAt(i, _M); } brk.instanceMatrix.needsUpdate = true;
  }
  function snowAt(d, T, k = 1) {
    for (let i = 0; i < NS; i++) { const s = sb[i]; const y = (((s[1] + d * k) % 40) + 40) % 40 - 18;
      sp[i * 3] = s[0] + 0.15 * Math.sin(T * 0.4 + s[3]); sp[i * 3 + 1] = y; sp[i * 3 + 2] = s[2] + 0.12 * Math.cos(T * 0.3 + s[3]); }
    sgeo.attributes.position.needsUpdate = true;
  }
  function bioAt(T, d, amount) {
    const P = bio.geometry.attributes.position.array, Cc = bio.geometry.attributes.aColor.array, S = bio.geometry.attributes.aSize.array;
    for (let i = 0; i < 500; i++) { const b = bioSeed[i]; const blink = Math.max(0, Math.sin(T * (0.7 + b[5] * 2.5) + b[3] * 3));
      P[i * 3] = b[0] + 0.3 * Math.sin(T * 0.3 + b[3]); P[i * 3 + 1] = ((b[1] + d * 0.6 + 9) % 9 + 9) % 9 - 3; P[i * 3 + 2] = b[2];
      const col = b[4] === 0 ? [0.3, 0.75, 1.0] : b[4] === 1 ? [0.35, 1.0, 0.7] : [0.65, 0.55, 1.0];
      Cc[i * 4] = col[0]; Cc[i * 4 + 1] = col[1]; Cc[i * 4 + 2] = col[2]; Cc[i * 4 + 3] = amount * Math.pow(blink, 3) * 0.9; S[i] = 0.012 + b[5] * 0.02; }
    bio.geometry.attributes.position.needsUpdate = true; bio.geometry.attributes.aColor.needsUpdate = true; bio.geometry.attributes.aSize.needsUpdate = true;
  }
  function lights(inside, outside, d) {
    inLight.intensity = 5 * inside; lamp.material.color.setScalar(0.12 + 0.88 * inside).multiply(new THREE.Color('#fff1d8'));
    floods.forEach(f => { f.intensity = 260 * outside; }); nearL.intensity = 4 * outside; beams.forEach(b => { b.material.opacity = 0.045 * outside * smooth(80, 400, d); });
    towerM.emissiveIntensity = 1.2 * clamp(inside + 0.2);
  }
  function squidArms(T, k, eyeK) {
    // Kopf und Augen
    const head = new THREE.Vector3(lerp(2.4, 1.15, eyeK) + 0.05 * Math.sin(T * 0.8), lerp(3.6, 2.0, eyeK), lerp(-4.2, -2.45, eyeK));
    squid.position.copy(head); squid.rotation.set(0, -0.2, 1.15 + 0.05 * Math.sin(T * 0.6));
    const arms = squid.userData.arms; const r = rng(5); const suck = squid.userData.suck; let si = 0;
    const base = new THREE.Vector3(-0.35, 0, 0).applyEuler(squid.rotation).add(head);
    arms.forEach((a, i) => {
      const pts = [];
      if (i === 0) { // der Arm an der Scheibe: gleitet schräg nach unten links
        const c0 = new THREE.Vector3(lerp(1.15, -0.5, k), lerp(2.45, 1.15, k), -1.37), dir = new THREE.Vector3(-0.75, -0.66, 0).normalize();
        for (let j = 0; j <= 36; j++) { const u = j / 36;
          if (u < 0.45) { const w = u / 0.45; const ctrl = new THREE.Vector3((base.x + c0.x) / 2 + 0.4, (base.y + c0.y) / 2 + 0.3, (base.z + c0.z) / 2 - 0.4);
            pts.push(new THREE.Vector3().copy(base).multiplyScalar((1 - w) * (1 - w)).addScaledVector(ctrl, 2 * w * (1 - w)).addScaledVector(c0, w * w)); }
          else { const w = (u - 0.45) / 0.55; const p = c0.clone().addScaledVector(dir, w * 1.25); p.x += 0.06 * Math.sin(w * 7 + T * 2) * w; p.y += 0.04 * Math.sin(w * 5 + T * 2.4) * w;
            if (w > 0.85) { const c = (w - 0.85) / 0.15; p.addScaledVector(new THREE.Vector3(0.6, -0.2, -0.3), c * c * 0.25); }
            pts.push(p);
            if (j % 2 === 0 && w < 0.92 && si < 40) { for (const off of [-1, 1]) if (si < 40) { const n = new THREE.Vector3(-dir.y, dir.x, 0).multiplyScalar(off * 0.022 * (1 - w * 0.6));
              const sz = 0.017 * (1 - w * 0.7); _M.compose(_v.copy(p).add(n).setZ(-1.335), _q.identity(), new THREE.Vector3(sz, sz, sz)); suck.setMatrixAt(si++, _M); } } }
        }
      } else {
        const len = i < 8 ? 2.0 + r() * 0.8 : 5.0; const az = r() * 6.28, el = -0.4 - r() * 0.8; const ph = r() * 6;
        const d0 = new THREE.Vector3(Math.cos(az) * 0.6 - 0.5, el, Math.sin(az) * 0.5 + 0.25).normalize();
        for (let j = 0; j <= 36; j++) { const u = j / 36; const p = base.clone().addScaledVector(d0, u * len);
          p.x += 0.35 * u * Math.sin(T * 0.9 + ph + u * 3); p.y += 0.25 * u * Math.sin(T * 0.7 + ph * 2 + u * 4) - u * u * 0.6; p.z += 0.25 * u * Math.cos(T * 0.8 + ph + u * 2);
          if (p.z > -1.42) p.z = -1.42; pts.push(p); }
      }
      a.set(pts, i === 0 ? 0.85 : 1);
    });
    for (; si < 40; si++) { _M.makeScale(0, 0, 0); suck.setMatrixAt(si, _M); }
    suck.instanceMatrix.needsUpdate = true;
    squid.userData.eyes.forEach(e => { e.children[1].position.x = 0.02 * Math.sin(T * 0.5); });
  }

  function update(shot, T) {
    const id = shot.id; const d = depthAt(T, shot); const t = T - shot.t0;
    setEnv(d, T, shot); scroll(d);
    [school, whale, squid, angler, snail, sub, vent, wallR, wallB, floor, hand, bio].forEach(o => show(o, false));
    squid.userData.arms.forEach(a => show(a.mesh, false)); show(squid.userData.suck, false); cukes.forEach(c => show(c, false));
    let inside = 1, outside = 0; snowM.opacity = lerp(0.35, 0.8, smooth(0, 600, d)); snowM.color.set(d < 200 ? '#e4f2f5' : '#d9e3e6');
    let snowK = 1;
    // Standard-Blick aus dem Aufzug
    let cp = new THREE.Vector3(0.15, 1.55, 0.85), lk = new THREE.Vector3(0.25, 1.35, -5), fov = 52;
    panelM.emissive.set('#000000');

    if (id === 'panel') {
      show(hand, true); const pk = smooth(PRESS - 0.6, PRESS, T) - smooth(PRESS + 0.25, PRESS + 0.8, T);
      // Knopf −3.640 liegt auf der Tafel bei v ≈ 0.125 von unten
      const bx = -1.322, by = 1.22 - 0.425 + 0.125 * 0.85 + 0.0, bz = -0.7;
      hand.position.set(bx + lerp(0.25, 0.075, pk), by + 0.0 + lerp(-0.08, 0, smooth(PRESS - 1.4, PRESS - 0.5, T)), bz + 0.005); hand.rotation.set(0, 0, 0);
      hand.visible = T > 6.2; hand.position.y -= (1 - smooth(6.2, 6.9, T)) * 0.25;
      if (T >= PRESS) { panelM.map = pTex[1]; panelM.emissive.set('#ffb347'); panelM.emissiveIntensity = 0.35; } else panelM.map = pTex[0];
      panelM.needsUpdate = true;
      cp = new THREE.Vector3(-0.68, 1.12 + 0.02 * Math.sin(T), -0.42); lk = new THREE.Vector3(-1.32, 1.0 - smooth(5, 8.5, T) * 0.1, -0.72); fov = lerp(44, 36, smooth(5, 9, T));
    } else { panelM.map = pTex[T >= PRESS ? 1 : 0]; panelM.needsUpdate = true; }

    if (id === 'shallow' || id === 'panel') {
      show(school, true); const scare = smooth(SHADOW - 0.1, SHADOW + 0.6, T);
      updateSchool(school, T, new THREE.Vector3(2.2, 1.6 + (d - 6) * 0.4, -6.5), scare);
      // Schatten: der Pottwal zieht hoch oben vorbei
      if (T > SHADOW - 0.5) { show(whale, true); whale.position.set(lerp(16, -10, (T - SHADOW + 0.5) / 2.3), 11 - (d - 20) * 0, -15); whale.rotation.set(0, 0.1, 0.05); swimWhale(whale, T, 0.18); }
      const dim = smooth(SHADOW, SHADOW + 0.5, T) * (1 - smooth(SHADOW + 1.2, SHADOW + 1.9, T)); hemi.intensity *= 1 - 0.45 * dim; sun.intensity *= 1 - 0.7 * dim;
      if (id === 'shallow') { lk.set(0.6 + 0.4 * smooth(SHADOW, SHADOW + 0.8, T), 1.4 + 1.6 * smooth(SHADOW, SHADOW + 0.9, T), -5); }
      snowM.opacity = 0.3;
    }
    if (id === 'whale') {
      show(whale, true); outside = 1;
      const flee = Math.max(0, T - WHALE_FLEE); const look = smooth(17.9, 18.5, T) * (1 - smooth(WHALE_FLEE, WHALE_FLEE + 0.5, T));
      const nx = 6 - 4.1 * t - 6 * flee * flee; whale.position.set(nx, 2.1 + 2.6 * flee * flee + 0.15 * Math.sin(T * 0.7), -8.6 - 1.5 * flee * flee);
      whale.rotation.set(0, -0.38 - 0.25 * smooth(WHALE_FLEE, WHALE_FLEE + 1.5, T), -0.18 * look - 0.55 * smooth(WHALE_FLEE, WHALE_FLEE + 1.2, T));
      swimWhale(whale, T * (1 + 1.8 * smooth(WHALE_FLEE, WHALE_FLEE + 0.6, T)), 0.12 + 0.12 * smooth(WHALE_FLEE, WHALE_FLEE + 0.5, T));
      const eye = new THREE.Vector3(4.35, -0.75, 1.13).applyEuler(whale.rotation).add(whale.position);
      lk.set(lerp(clamp(eye.x, -0.4, 1.4), 0.6, smooth(18.8, 20.5, T)), lerp(eye.y, 2.6, smooth(18.8, 20.5, T)), eye.z); fov = lerp(50, 56, smooth(18.6, 20.5, T));
      cp.set(0.1, 1.55, 0.6);
    }
    if (id === 'squid') {
      outside = 1; squid.userData.arms.forEach(a => show(a.mesh, true)); show(squid, true); show(squid.userData.suck, true);
      squidArms(T, smooth(21.2, 25.2, T), smooth(23.6, 25.6, T));
      lk.set(lerp(0.55, 0.95, smooth(23.5, 25.5, T)), lerp(1.85, 1.9, smooth(23.5, 25.5, T)), -3); fov = lerp(50, 42, smooth(21, 26, T));
      // Licht flackert und geht aus
      if (T > LIGHTS_OUT - 0.5) { const f = T - (LIGHTS_OUT - 0.5); const fl = [0.6, 0.15, 0.9, 0.05, 0.7, 0.0]; const s = fl[Math.min(5, Math.floor(f / 0.1))]; inside = T > LIGHTS_OUT + 0.1 ? 0 : s; outside = inside; }
    }
    if (id === 'dark') {
      inside = 0; outside = 0; show(bio, true); bioAt(T, d, 1);
      show(angler, true);
      const k = easeOut(smooth(LURE, LURE + 2.0, T)); const ap = new THREE.Vector3(lerp(1.6, 0.06, k), lerp(0.9, 1.47, k) + 0.01 * Math.sin(T * 2), lerp(-7.5, -1.42, k));
      angler.position.copy(ap); angler.rotation.set(0.05 * Math.sin(T * 1.3), Math.PI / 2 + 0.25 * (1 - k), 0.06 * Math.sin(T * 1.7));
      angler.userData.light.intensity = T > LURE ? 0.12 : 0; angler.userData.glow.material.opacity = T > LURE ? 0.9 + 0.1 * Math.sin(T * 5) : 0;
      angler.userData.lure.material.color.set(T > LURE ? '#bff4ff' : '#000000');
      const lit = smooth(LIGHTS_ON, LIGHTS_ON + 0.15, T) * (T > LIGHTS_ON + 0.25 || T < LIGHTS_ON + 0.12 ? 1 : 0.3);
      inside = lit; outside = lit;
      cp.set(0.06, 1.5, 0.2); lk.copy(ap).add(new THREE.Vector3(0, 0.005, 0));
      fov = T < LURE ? 30 : lerp(30, 15, smooth(LURE, LURE + 2.1, T)); fov = lerp(fov, 55, easeOut(smooth(LIGHTS_ON + 0.15, LIGHTS_ON + 0.9, T)));
      if (T > LIGHTS_ON) lk.lerp(new THREE.Vector3(0.1, 1.35, -5), smooth(LIGHTS_ON + 0.2, LIGHTS_ON + 1.0, T));
      snowM.opacity = 0.25 + 0.5 * lit;
    }
    if (id === 'vent') {
      outside = 1; show(vent, true); show(wallR, true); show(wallB, true);
      vent.position.y = (d - shot.d0) * 1.0 - 1.5;
      updateParticles(smoke, chimneys.map(c => ({pos: c.top, r: 0.25, t0: -5, type: 'smoke', size: 1.3, rise: 1.3, col: [0.03, 0.028, 0.025], alpha: 0.85, share: c.s === 2 ? 2 : 1})), T, new THREE.Vector3(0.2, 0, 0.1));
      lk.set(2.4, lerp(-1.2, -0.2, smooth(33.5, 39.5, T)), -14); cp.set(0.35, 1.6, 0.4); fov = 54;
      floods[0].target.position.set(1.5, -3, -13); floods[1].target.position.set(4.5, -2.5, -16);
    } else { floods[0].target.position.set(-1.5, -3.5, -15); floods[1].target.position.set(2.8, -3.5, -15); }
    if (id === 'crack') {
      outside = 1; show(wallR, true); show(wallB, true); wallR.position.y = (d - shot.d0); wallB.position.y = (d - shot.d0);
      const sh = Math.max(0, 1 - (T - CRACK) / 0.9) * (T > CRACK ? 1 : 0); cp.x += 0.035 * sh * Math.sin(T * 61); cp.y += 0.03 * sh * Math.sin(T * 47);
      lk.set(0.4, 1.3, -5); fov = lerp(52, 46, smooth(39.5, 46.5, T));
      if (T > CRACK && T < CRACK + 0.25) inside = 0.4 + 0.6 * Math.abs(Math.sin(T * 60));
      snowK = 1;
    }
    if (id === 'snail') {
      outside = 1; show(wallR, true); show(wallB, true); show(snail, true);
      const k = smooth(46.6, 50.8, T); snail.position.set(lerp(-0.6, 1.1, k), 1.3 + 0.05 * Math.sin(T * 1.3), lerp(-2.0, -1.9, k));
      snail.rotation.set(0, Math.PI + 0.15 * Math.sin(T * 1.1), 0.05 * Math.sin(T * 1.7));
      snail.userData.finL.rotation.x = 0.35 * Math.sin(T * 4.5); snail.userData.finR.rotation.x = -0.35 * Math.sin(T * 4.5);
      lk.copy(snail.position).add(new THREE.Vector3(0.1, 0.02, 0)); fov = 32; cp.set(0.1, 1.5, 0.5);
    }
    if (id === 'bottom') {
      outside = 1; show(floor, true); show(wallB, true); cukes.forEach(c => { show(c, true); });
      const rise = shot.d1 - d; floor.position.y = -1.3 - rise; cukes.forEach(c => { c.position.y = -1.22 - rise; });
      const bump = T > ARRIVE ? Math.exp(-(T - ARRIVE) * 5) * Math.sin((T - ARRIVE) * 30) : 0; cp.y += 0.04 * bump;
      lk.set(0.3, lerp(0.6, 1.0, smooth(53, 55, T)), -5);
      const ks = T > KNOCK && T < KNOCK + 0.5 ? Math.exp(-(T - KNOCK) * 12) * Math.sin((T - KNOCK) * 80) : 0; cp.y += 0.006 * ks;
      if (T > KNOCK) lk.y += 0.25 * smooth(KNOCK, KNOCK + 0.6, T) * (1 - smooth(SUB + 0.2, SUB + 1.0, T));
      // Tauchboot senkt sich von oben vor die Scheibe
      show(sub, T > KNOCK - 0.5); sub.scale.setScalar(0.7);
      const down = easeOut(smooth(SUB, BOX - 0.1, T)); sub.position.set(0.4, lerp(6.0, 1.45, down) + 0.03 * Math.sin(T * 1.4), -4.7);
      sub.rotation.set(0, 0.12 - 0.08 * down, 0.02 * Math.sin(T * 0.9));
      const u = sub.userData; const lampOn = T > SUB - 0.2 ? 1 : 0; u.spot.intensity = 140 * lampOn; sub.children.forEach(c => { if (c.isSprite) c.material.opacity = 0.7 * lampOn; });
      const ext = easeOut(smooth(BOX - 0.4, BOX + 0.3, T));
      u.arm.rotation.set(lerp(-0.9, -0.3, ext), 0.15, 0); u.elbow.rotation.set(lerp(1.5, 0.32, ext), 0, 0); u.wrist.rotation.set(-(lerp(-0.9, -0.3, ext) + lerp(1.5, 0.32, ext)), 0, 0);
      u.box.rotation.z = 0.04 * Math.sin(T * 1.1);
      sub.updateMatrixWorld(true); const bw = new THREE.Vector3(); u.box.getWorldPosition(bw); sub.position.x += (0.2 - bw.x) * ext;
      u.pilot.visible = true; u.hand.position.set(0.1 + 0.03 * Math.sin(T * 9), 0.09 + (T > 56 ? 0.02 : -0.06), 0.03);
      lk.set(0.25, lerp(lk.y, 1.35, smooth(SUB, BOX, T)), -5);
      outside = 1; snowM.opacity = 0.5; snowK = 1;
      cp.z = 0.75;
    }
    if (id !== 'bottom' && id !== 'dark') snowK = 1;
    lights(inside, outside, d);
    snowAt(d, T, snowK);
    camera.fov = fov; camera.updateProjectionMatrix();
    cp.x += noise1(T * 0.6, 3) * 0.012; cp.y += noise1(T * 0.6, 7) * 0.01;
    camera.position.copy(cp); camera.lookAt(lk);
  }
  return {scene, camera, update};
}
