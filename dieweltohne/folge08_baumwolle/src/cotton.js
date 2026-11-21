// Gemeinsame Bausteine für Folge 8: Figuren mit Baumwollkleidung, Baumwollflocken, Geldscheine
import {THREE, mat, mesh, rng, clamp, makePerson, canvasTex} from './lib.js';

// Figur mit Kleidung aus Baumwolle (Jeans, Hoodie oder T-Shirt) über Sachen aus Kunstfaser (Sportshirt, Shorts).
// o.hoodie: Farbe des Hoodies (sonst keiner), o.jeans: Jeans an (Standard true), o.under: Farbe der Shorts
export function cottonPerson(seed, o = {}) {
  const p = makePerson(seed, {shortSleeve: true, pants: o.jeans === false ? (o.pants || '#2b2b2b') : (o.denim || '#3c5a86'), ...o});
  const u = p.userData; const cot = [];
  if (o.hoodie) {
    const hm = mat(o.hoodie, {roughness: 0.95});
    const body = mesh(new THREE.CapsuleGeometry(0.185, 0.36, 4, 12), hm, 0, 0.3, 0, u.torso); body.scale.set(1.15, 1, 0.8); cot.push(body);
    const hood = mesh(new THREE.SphereGeometry(0.15, 14, 10, 0, Math.PI * 2, 0, Math.PI * 0.6), hm, 0, 0.66, -0.09, u.torso); hood.rotation.x = -1.2; hood.scale.set(1, 1, 0.6); cot.push(hood);
    const pocket = mesh(new THREE.BoxGeometry(0.22, 0.09, 0.02), mat(o.hoodie, {roughness: 1}), 0, 0.12, 0.135, u.torso); cot.push(pocket);
    for (const sh of [u.armL, u.armR]) {
      cot.push(mesh(new THREE.CapsuleGeometry(0.064, 0.25, 4, 8), hm, 0, -0.16, 0, sh));
      cot.push(mesh(new THREE.CapsuleGeometry(0.056, 0.22, 4, 8), hm, 0, -0.13, 0, sh.userData.fore));
    }
  }
  // Beine ohne Hose: Haut (bzw. Leggings)
  const legSkin = [];
  for (const lg of [u.legL, u.legR]) { legSkin.push(lg.userData.thighSkin); lg.userData.knee.children.forEach(c => { if (c.isMesh && !c.visible) legSkin.push(c); }); }
  if (o.leggings) legSkin.forEach(m => m.material = mat(o.leggings));
  u.under.scale.set(1.2, 1.25, 0.8);
  u.cotton = {cot, legSkin, jeans: o.jeans !== false};
  return p;
}
// nach posePerson aufrufen: on = Baumwolle vorhanden
export function setCotton(p, on) {
  const u = p.userData, c = u.cotton;
  c.cot.forEach(m => m.visible = on);
  if (c.jeans) { u.pants.visible = on; u.under.visible = !on; c.legSkin.forEach(m => m.visible = !on); }
}

// Weiche, weiße Flocken (Baumwollfasern), die fallen und treiben. box = [x0,x1,y0,y1,z0,z1]
let FT = null;
function flakeTex() {
  if (FT) return FT;
  const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d'); const r = rng(3);
  for (let i = 0; i < 9; i++) { const x = 20 + r() * 24, y = 20 + r() * 24, rad = 8 + r() * 14; const gr = g.createRadialGradient(x, y, 0, x, y, rad);
    gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); }
  FT = new THREE.CanvasTexture(c); return FT;
}
export function flakes(n, box, size = 0.12, color = '#fbf8f1') {
  const r = rng(n + 17); const geo = new THREE.BufferGeometry(); const P = new Float32Array(n * 3);
  const seed = []; for (let i = 0; i < n; i++) seed.push([r(), r(), r(), r(), r()]);
  geo.setAttribute('position', new THREE.BufferAttribute(P, 3));
  const m = new THREE.Points(geo, new THREE.PointsMaterial({size, map: flakeTex(), color, transparent: true, depthWrite: false, opacity: 1, sizeAttenuation: true}));
  m.frustumCulled = false; m.userData = {n, box, seed}; return m;
}
// t = Zeit, fall = Fallgeschwindigkeit (m/s), amount 0..1 sichtbarer Anteil, up: Wärme lässt Flocken steigen
export function updateFlakes(sys, t, fall = 0.8, amount = 1, wind = [0.6, 0.2]) {
  const {n, box, seed} = sys.userData; const P = sys.geometry.attributes.position.array;
  const [x0, x1, y0, y1, z0, z1] = box, H = y1 - y0;
  for (let i = 0; i < n; i++) {
    const s = seed[i];
    if (s[4] > amount) { P[i * 3 + 1] = -999; continue; }
    const y = y1 - (((s[1] * H) + t * fall * (0.6 + s[3] * 0.8)) % H);
    P[i * 3] = x0 + ((s[0] * (x1 - x0) + t * wind[0] + Math.sin(t * 0.9 + s[3] * 20) * 0.4) % (x1 - x0) + (x1 - x0)) % (x1 - x0);
    P[i * 3 + 1] = y; P[i * 3 + 2] = z0 + ((s[2] * (z1 - z0) + t * wind[1] + Math.cos(t * 0.7 + s[3] * 9) * 0.4) % (z1 - z0) + (z1 - z0)) % (z1 - z0);
  }
  sys.geometry.attributes.position.needsUpdate = true;
}

// Bodenschicht aus Baumwollfasern (Textur mit Bauschen)
export function fluffTex(rep = 1) {
  const r = rng(77);
  const t = canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#f2eee6'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 900; i++) { const x = r() * w, y = r() * h, rad = 6 + r() * 26; const gr = g.createRadialGradient(x, y, 0, x, y, rad);
      const v = 220 + r() * 35; gr.addColorStop(0, `rgba(${v},${v},${v - 6},0.9)`); gr.addColorStop(1, `rgba(${v},${v},${v - 6},0)`); g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2); }
    for (let i = 0; i < 400; i++) { g.strokeStyle = `rgba(180,175,165,${0.15 + r() * 0.2})`; g.lineWidth = 1; g.beginPath(); const x = r() * w, y = r() * h; g.moveTo(x, y); g.quadraticCurveTo(x + (r() - 0.5) * 30, y + (r() - 0.5) * 30, x + (r() - 0.5) * 40, y + (r() - 0.5) * 40); g.stroke(); }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep, rep); return t;
}

// Geldschein-Texturen (frei gestaltet, keine echte Banknote)
export function noteTex(kind = 'eur') {
  return canvasTex(256, 128, (g, w, h) => {
    const c = kind === 'eur' ? ['#5aa0d8', '#9cc8ea'] : ['#7a9a6a', '#c4d4b0'];
    const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, c[0]); gr.addColorStop(1, c[1]); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.strokeStyle = 'rgba(255,255,255,0.35)'; for (let i = 0; i < 30; i++) { g.beginPath(); g.arc(70, 64, 8 + i * 3, 0, 7); g.stroke(); }
    g.fillStyle = 'rgba(255,255,255,0.8)'; g.font = '700 54px sans-serif'; g.fillText(kind === 'eur' ? '20' : '100', 160, 80);
    g.fillStyle = 'rgba(0,0,0,0.2)'; g.fillRect(0, 0, w, 8); g.fillRect(0, h - 8, w, 8);
  });
}
