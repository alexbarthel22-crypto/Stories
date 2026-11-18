// Handy mit Händen, Silikonhülle und Display als Canvas-Textur mit Regentropfen
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp} from './lib.js';

const SW = 600, SH = 1300; // Display-Auflösung
export function makePhone() {
  const g = new THREE.Group();
  const pw = 0.072, ph = 0.152, pd = 0.008;
  // Gerät: Aluminiumrahmen + Glas
  mesh(new RoundedBoxGeometry(pw, ph, pd, 4, 0.009), mat('#3b3f45', {metalness: 0.9, roughness: 0.3}), 0, 0, 0, g);
  const content = document.createElement('canvas'); content.width = SW; content.height = SH; // Inhalt ohne Tropfen
  const screenC = document.createElement('canvas'); screenC.width = SW; screenC.height = SH; // mit Tropfen
  const tex = new THREE.CanvasTexture(screenC); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const scr = mesh(new THREE.PlaneGeometry(pw * 0.93, ph * 0.955), new THREE.MeshPhysicalMaterial({map: tex, emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: 0.9, roughness: 0.08, clearcoat: 1, clearcoatRoughness: 0.02, metalness: 0}), 0, 0, pd / 2 + 0.0004, g);
  // Silikonhülle (Gummi)
  const caseM = mat('#ff6f61', {roughness: 0.85, transparent: true});
  const cg = new THREE.Group(); g.add(cg);
  mesh(new RoundedBoxGeometry(pw + 0.006, ph + 0.006, 0.004, 4, 0.004), caseM, 0, 0, -pd / 2 - 0.002, cg);
  for (const [x, y, w, h] of [[-(pw / 2 + 0.002), 0, 0.004, ph + 0.006], [pw / 2 + 0.002, 0, 0.004, ph + 0.006], [0, ph / 2 + 0.002, pw + 0.006, 0.004], [0, -(ph / 2 + 0.002), pw + 0.006, 0.004]])
    mesh(new RoundedBoxGeometry(w, h, pd + 0.004, 2, 0.0018), caseM, x, y, 0, cg);
  // Kamera auf der Rückseite
  mesh(new THREE.CylinderGeometry(0.007, 0.007, 0.003, 16), mat('#111', {roughness: 0.2}), -0.022, 0.058, -pd / 2 - 0.003, g).rotation.x = Math.PI / 2;
  g.userData = {content, screenC, tex, scr, caseM, cg, pw, ph};
  return g;
}

// Eine Hand hält das Handy von hinten: Finger umgreifen den rechten Rand, Daumen links
export function makeHands(skin = '#e3b08e', sleeve = '#2a3442') {
  const s = mat(skin, {roughness: 0.62}), sl = mat(sleeve, {roughness: 0.9});
  const h = new THREE.Group();
  mesh(new RoundedBoxGeometry(0.07, 0.08, 0.022, 3, 0.01), s, 0.006, -0.05, -0.017, h);          // Handfläche hinter dem Handy
  const wrist = mesh(new THREE.CylinderGeometry(0.024, 0.028, 0.06, 12), s, 0.01, -0.1, -0.03, h); wrist.rotation.x = 0.5;
  const arm = mesh(new THREE.CylinderGeometry(0.033, 0.037, 0.22, 14), sl, 0.012, -0.2, -0.085, h); arm.rotation.x = 0.5;
  for (let i = 0; i < 4; i++) { // Fingerkuppen am rechten Rand
    const f = mesh(new THREE.CapsuleGeometry(0.0078, 0.016, 4, 8), s, 0.04, -0.012 - i * 0.017, 0.001, h); f.rotation.z = Math.PI / 2 + 0.15; f.scale.set(1, 1, 0.9);
  }
  const th = mesh(new THREE.CapsuleGeometry(0.009, 0.03, 4, 8), s, -0.038, -0.045, 0.002, h); th.rotation.z = -0.35; // Daumen links
  return h;
}

// Tropfen auf dem Display
export function makeDrops(seed, n) {
  const r = rng(seed); const d = [];
  for (let i = 0; i < n; i++) d.push({x: r() * SW, y: r() * SH, r: 3 + Math.pow(r(), 3) * 30, t0: r() * 4, run: r() < 0.12 ? 60 + r() * 140 : 0, wob: r() * 6});
  return d;
}

function drawContent(g, st) {
  const {t, mode, glitch = 0, dead = 0, notify = 0} = st;
  // Hintergrundbild: Abendhimmel
  const grd = g.createLinearGradient(0, 0, 0, SH); grd.addColorStop(0, '#1d2b4a'); grd.addColorStop(0.55, '#6b4d79'); grd.addColorStop(1, '#e48f6a');
  g.fillStyle = grd; g.fillRect(0, 0, SW, SH);
  g.fillStyle = 'rgba(255,255,255,0.08)'; for (let i = 0; i < 6; i++) { g.beginPath(); g.arc(80 + i * 95, 1000 + Math.sin(i) * 60, 160, 0, 7); g.fill(); }
  g.fillStyle = '#fff'; g.textAlign = 'center';
  g.font = '500 30px Plex'; g.fillText('Dienstag, 18. November', SW / 2, 220);
  g.font = '300 150px Garamond'; g.fillText('17:42', SW / 2, 380);
  g.font = '500 24px Plex'; g.textAlign = 'left'; g.fillText('17:42', 40, 52); g.textAlign = 'right'; g.fillText('5G  84%', SW - 40, 52);
  if (notify > 0) { // Mitteilung
    const y = 470 + (1 - notify) * -60;
    g.globalAlpha = clamp(notify); g.fillStyle = 'rgba(245,245,248,0.88)';
    g.beginPath(); g.roundRect(30, y, SW - 60, 150, 30); g.fill();
    g.fillStyle = '#ff8a3d'; g.beginPath(); g.roundRect(55, y + 25, 56, 56, 14); g.fill();
    g.fillStyle = '#111'; g.font = '500 23px Plex'; g.textAlign = 'left'; g.fillText('EILMELDUNG', 130, y + 48);
    g.font = '400 27px Plex'; g.fillText('Gummi verschwindet', 130, y + 88); g.fillText('in wenigen Sekunden.', 130, y + 122);
    g.fillStyle = '#777'; g.font = '400 20px Plex'; g.textAlign = 'right'; g.fillText('jetzt', SW - 55, y + 48);
    g.globalAlpha = 1;
  }
  if (glitch > 0) { // Wasserschaden: Farbbalken und Streifen
    const r = rng(Math.floor(t * 24) + 3);
    for (let i = 0; i < 18 * glitch; i++) {
      const y = r() * SH, h = 4 + r() * 70; g.drawImage(g.canvas, 0, y, SW, h, (r() - 0.5) * 120 * glitch, y, SW, h);
      g.fillStyle = ['rgba(0,255,120,0.5)', 'rgba(255,0,200,0.5)', 'rgba(60,120,255,0.5)', 'rgba(255,255,255,0.7)'][Math.floor(r() * 4)];
      g.fillRect(0, r() * SH, SW, 2 + r() * 10 * glitch);
    }
    for (let x = 0; x < SW; x += 7 + Math.floor(r() * 30)) if (r() < 0.3 * glitch) { g.fillStyle = `rgba(${r() * 255},${r() * 255},255,0.6)`; g.fillRect(x, 0, 2, SH); }
  }
  if (dead > 0) { g.fillStyle = `rgba(0,0,0,${dead})`; g.fillRect(0, 0, SW, SH); }
}

// Zeichnet Inhalt + Tropfen (jeder Tropfen zeigt den Inhalt verkleinert und gespiegelt wie eine Linse)
export function updateScreen(phone, drops, st) {
  const {content, screenC, tex} = phone.userData;
  const cg = content.getContext('2d'); drawContent(cg, st);
  const g = screenC.getContext('2d'); g.drawImage(content, 0, 0);
  const t = st.t, wet = st.wet ?? 1;
  for (const d of drops) {
    if (d.t0 / 4 > wet) continue;
    let y = d.y, x = d.x;
    if (d.run) { const p = ((t * 40 + d.t0 * 50) % (d.run + 300)); y = d.y + Math.min(p, d.run); x += Math.sin(p * 0.05 + d.wob) * 3;
      g.strokeStyle = 'rgba(255,255,255,0.12)'; g.lineWidth = d.r * 0.6; g.beginPath(); g.moveTo(d.x, d.y); g.lineTo(x, y); g.stroke(); }
    const r = d.r * (st.dropScale || 1);
    g.save(); g.beginPath(); g.ellipse(x, y, r, r * 0.92, 0, 0, Math.PI * 2); g.clip();
    // Linse: Umgebung um den Tropfen, 3x verkleinert, gespiegelt
    g.translate(x, y); g.scale(-1, -1);
    g.drawImage(content, x - r * 3, y - r * 3, r * 6, r * 6, -r, -r, r * 2, r * 2);
    g.restore();
    // dunkler Rand unten, Glanzpunkt oben
    const rg = g.createRadialGradient(x - r * 0.25, y - r * 0.3, r * 0.1, x, y, r * 1.05);
    rg.addColorStop(0, 'rgba(255,255,255,0)'); rg.addColorStop(0.75, 'rgba(0,0,0,0.05)'); rg.addColorStop(1, 'rgba(0,0,0,0.45)');
    g.fillStyle = rg; g.beginPath(); g.ellipse(x, y, r, r * 0.92, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = 'rgba(255,255,255,0.85)'; g.beginPath(); g.ellipse(x - r * 0.35, y - r * 0.4, r * 0.22, r * 0.14, -0.6, 0, Math.PI * 2); g.fill();
    g.fillStyle = 'rgba(255,255,255,0.25)'; g.beginPath(); g.ellipse(x + r * 0.3, y + r * 0.55, r * 0.35, r * 0.1, 0, 0, Math.PI * 2); g.fill();
  }
  // Wasser dringt am Rand ein (Schliere unter dem Glas)
  if (st.ingress > 0) {
    const k = st.ingress;
    const lg = g.createLinearGradient(0, SH, 0, SH - 700 * k);
    lg.addColorStop(0, 'rgba(120,170,210,0.75)'); lg.addColorStop(0.6, 'rgba(120,170,210,0.25)'); lg.addColorStop(1, 'rgba(120,170,210,0)');
    g.fillStyle = lg; g.beginPath(); g.moveTo(0, SH);
    for (let x = 0; x <= SW; x += 20) g.lineTo(x, SH - 700 * k + Math.sin(x * 0.02 + t * 2) * 40 * k + Math.sin(x * 0.07) * 20);
    g.lineTo(SW, SH); g.fill();
  }
  tex.needsUpdate = true;
}
