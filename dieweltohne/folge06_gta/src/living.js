// Wohnzimmer bei Nacht: Ein Teenager zockt seit dem Launch durch. Das Spiel verschwindet, der Spielstand auch,
// der Controller fliegt in den Fernseher. Am Morgen danach: Download 1 %.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, easeOut, envMap} from './lib.js';
import {VANISH, THROW} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const HIT = THROW + 0.42; // Controller trifft den Fernseher
const RW = 2.6, ZB = -2.0, ZF = 2.8, RH = 2.6;

// Original-Spielbild: Küstenstadt im Sonnenuntergang, Verfolgungsjagd (eigene Gestaltung, keine Spielgrafik)
export function drawChase(g, w, h, T) {
  const sky = g.createLinearGradient(0, 0, 0, h * 0.6); sky.addColorStop(0, '#2a1d5c'); sky.addColorStop(0.5, '#d4467a'); sky.addColorStop(1, '#ffb36b');
  g.fillStyle = sky; g.fillRect(0, 0, w, h);
  g.fillStyle = '#ffe2a0'; g.beginPath(); g.arc(w * 0.62, h * 0.47, h * 0.12, 0, 7); g.fill();
  const r = rng(5), hor = h * 0.52;
  // Skyline
  for (let i = 0; i < 26; i++) { const bw = 20 + r() * 50, bh = 40 + r() * 170, x = (i * 44 + T * 6) % (w + 80) - 60; g.fillStyle = `rgb(${50 + r() * 30},${30 + r() * 20},${80 + r() * 30})`; g.fillRect(x, hor - bh, bw, bh);
    g.fillStyle = 'rgba(255,220,150,0.6)'; for (let k = 0; k < bh / 14; k++) if (r() < 0.4) g.fillRect(x + 4 + r() * (bw - 10), hor - bh + k * 14 + 4, 4, 5); }
  // Meer links, Straße
  g.fillStyle = '#3d2a6e'; g.fillRect(0, hor, w, h - hor);
  g.fillStyle = '#2b2733'; g.beginPath(); g.moveTo(w * 0.47, hor); g.lineTo(w * 0.53, hor); g.lineTo(w * 1.05, h); g.lineTo(-w * 0.05, h); g.fill();
  g.fillStyle = '#e8d070'; for (let i = 0; i < 12; i++) { const u = ((i / 12) + T * 1.8) % 1, z = u * u, y = hor + (h - hor) * z, ww = 2 + 10 * z, hh = 4 + 40 * z; g.fillRect(w / 2 - ww / 2, y, ww, hh); }
  // Palmen beidseits
  for (let i = 0; i < 8; i++) { const u = ((i / 8) + T * 1.8) % 1, z = u * u, side = i % 2 ? 1 : -1, x = w / 2 + side * (w * 0.06 + w * 0.62 * z), y = hor + (h - hor) * z, s = 0.2 + z * 2.2;
    g.strokeStyle = '#1d1426'; g.lineWidth = 5 * s; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + side * 10 * s, y - 60 * s, x + side * 4 * s, y - 120 * s); g.stroke();
    g.fillStyle = '#1d1426'; for (let k = 0; k < 6; k++) { g.save(); g.translate(x + side * 4 * s, y - 120 * s); g.rotate(k * 1.05); g.beginPath(); g.ellipse(26 * s, 0, 30 * s, 6 * s, 0.3, 0, 7); g.fill(); g.restore(); } }
  // Eigenes Auto von hinten (Sportwagen, türkis)
  const cx = w / 2 + Math.sin(T * 1.6) * 60, cy = h * 0.8;
  g.fillStyle = 'rgba(0,0,0,0.35)'; g.beginPath(); g.ellipse(cx, cy + 46, 150, 18, 0, 0, 7); g.fill();
  g.fillStyle = '#18b5b0'; g.beginPath(); g.moveTo(cx - 150, cy + 40); g.lineTo(cx - 140, cy - 10); g.lineTo(cx - 80, cy - 50); g.lineTo(cx + 80, cy - 50); g.lineTo(cx + 140, cy - 10); g.lineTo(cx + 150, cy + 40); g.fill();
  g.fillStyle = '#0d2a33'; g.beginPath(); g.moveTo(cx - 70, cy - 44); g.lineTo(cx + 70, cy - 44); g.lineTo(cx + 100, cy - 12); g.lineTo(cx - 100, cy - 12); g.fill();
  g.fillStyle = '#ff2a3a'; g.fillRect(cx - 135, cy + 2, 60, 12); g.fillRect(cx + 75, cy + 2, 60, 12);
  g.fillStyle = '#111'; g.fillRect(cx - 140, cy + 30, 50, 22); g.fillRect(cx + 90, cy + 30, 50, 22);
  // Verfolger mit Blaulicht
  const px = w / 2 - 210 + Math.sin(T * 1.2 + 1) * 40, py = h * 0.66, bl = Math.sin(T * 22) > 0;
  g.fillStyle = '#e8e8e8'; g.fillRect(px - 50, py - 22, 100, 38); g.fillStyle = '#1b2a4a'; g.fillRect(px - 36, py - 34, 72, 16);
  g.fillStyle = bl ? '#3060ff' : '#ff2030'; g.fillRect(px - 30, py - 42, 26, 8); g.fillStyle = bl ? '#ff2030' : '#3060ff'; g.fillRect(px + 4, py - 42, 26, 8);
  const glow = g.createRadialGradient(px, py - 40, 2, px, py - 40, 120); glow.addColorStop(0, bl ? 'rgba(60,100,255,0.55)' : 'rgba(255,40,60,0.55)'); glow.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = glow; g.fillRect(px - 130, py - 160, 260, 240);
  // Generische Oberfläche: Mission, Tacho, Karte (eigene Gestaltung)
  g.fillStyle = 'rgba(0,0,0,0.45)'; g.beginPath(); g.arc(90, h - 90, 66, 0, 7); g.fill(); g.strokeStyle = 'rgba(255,255,255,0.8)'; g.lineWidth = 3; g.stroke();
  g.strokeStyle = '#7cf'; g.lineWidth = 4; g.beginPath(); g.moveTo(60, h - 60); g.lineTo(100, h - 110); g.lineTo(130, h - 100); g.stroke(); g.fillStyle = '#fff'; g.beginPath(); g.arc(90, h - 90, 6, 0, 7); g.fill();
  g.fillStyle = '#fff'; g.font = '600 26px Plex'; g.textAlign = 'right'; g.fillText(`${Math.round(212 + Math.sin(T * 3) * 6)} km/h`, w - 40, h - 40);
  g.textAlign = 'left'; g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(30, 30, 380, 74); g.fillStyle = '#ffcf4a'; g.font = '600 22px Plex'; g.fillText('MISSION 23 · ENTKOMMEN', 46, 60);
  g.fillStyle = '#fff'; g.font = '400 20px Plex'; g.fillText('Hänge die Verfolger ab.', 46, 90);
  g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(w - 260, 30, 230, 40); g.fillStyle = '#ff4d4d'; g.fillRect(w - 252, 38, 214 * 0.85, 24); g.fillStyle = '#fff'; g.font = '600 18px Plex'; g.fillText('FAHNDUNG', w - 240, 57);
}
// Konsolen-Startbildschirm mit Fehlermeldung (generisch)
export function drawHome(g, w, h, T, k = 1) {
  const bg = g.createLinearGradient(0, 0, w, h); bg.addColorStop(0, '#0a1a3a'); bg.addColorStop(1, '#13306b'); g.fillStyle = bg; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(255,255,255,0.05)'; for (let i = 0; i < 6; i++) { g.beginPath(); g.arc(w * (0.1 + i * 0.18), h * 0.8, 140, 0, 7); g.fill(); }
  g.textAlign = 'left'; g.fillStyle = '#fff'; g.font = '500 20px Plex'; g.fillText('Spiele', 60, 60); g.fillStyle = 'rgba(255,255,255,0.5)'; g.fillText('Medien', 160, 60);
  for (let i = 0; i < 6; i++) { g.fillStyle = i === 0 ? 'rgba(255,255,255,0.08)' : ['#2e5fa8', '#3a8a6a', '#8a3a6a', '#a87a2e', '#4a4a8a', '#2e8aa8'][i]; g.strokeStyle = i === 0 ? 'rgba(255,255,255,0.5)' : 'transparent'; g.lineWidth = 2;
    g.beginPath(); g.roundRect(60 + i * 132, 90, i === 0 ? 160 : 112, i === 0 ? 160 : 112, 12); g.fill(); if (i === 0) { g.setLineDash([8, 6]); g.stroke(); g.setLineDash([]); } }
  g.fillStyle = 'rgba(255,255,255,0.6)'; g.font = '400 50px Plex'; g.textAlign = 'center'; g.fillText('?', 140, 190);
  // Dialog
  g.globalAlpha = k; g.fillStyle = 'rgba(8,12,24,0.92)'; g.beginPath(); g.roundRect(w / 2 - 330, h / 2 - 90, 660, 250, 18); g.fill();
  g.strokeStyle = 'rgba(255,255,255,0.2)'; g.stroke();
  g.fillStyle = '#fff'; g.font = '600 30px Plex'; g.fillText('Spiel nicht gefunden', w / 2, h / 2 - 30);
  g.font = '400 21px Plex'; g.fillStyle = 'rgba(255,255,255,0.8)'; g.fillText('„GTA VI“ ist auf diesem Gerät nicht installiert.', w / 2, h / 2 + 12);
  g.fillText('Gespeicherte Daten: keine', w / 2, h / 2 + 44);
  g.fillStyle = '#2f6dff'; g.beginPath(); g.roundRect(w / 2 - 110, h / 2 + 80, 220, 52, 26); g.fill(); g.fillStyle = '#fff'; g.font = '600 22px Plex'; g.fillText('OK', w / 2, h / 2 + 114);
  g.globalAlpha = 1;
}
export function drawDownload(g, w, h, T, pct, left) {
  const bg = g.createLinearGradient(0, 0, w, h); bg.addColorStop(0, '#0a1a3a'); bg.addColorStop(1, '#13306b'); g.fillStyle = bg; g.fillRect(0, 0, w, h);
  g.textAlign = 'center'; g.fillStyle = '#fff'; g.font = '600 34px Plex'; g.fillText('GTA VI wird heruntergeladen …', w / 2, h / 2 - 60);
  g.fillStyle = 'rgba(255,255,255,0.15)'; g.beginPath(); g.roundRect(w / 2 - 330, h / 2 - 20, 660, 22, 11); g.fill();
  g.fillStyle = '#2f9dff'; g.beginPath(); g.roundRect(w / 2 - 330, h / 2 - 20, Math.max(22, 660 * pct / 100), 22, 11); g.fill();
  g.font = '400 26px Plex'; g.fillStyle = 'rgba(255,255,255,0.85)'; g.fillText(`${pct} %  ·  noch ${left}`, w / 2, h / 2 + 50);
  g.font = '400 20px Plex'; g.fillStyle = 'rgba(255,255,255,0.55)'; g.fillText('Server stark ausgelastet. Bitte habe etwas Geduld.', w / 2, h / 2 + 92);
}

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#05070c');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.12;
  const hemi = new THREE.HemisphereLight('#6c80b8', '#20180f', 0.25); scene.add(hemi);
  const moon = new THREE.DirectionalLight('#7f9cd6', 0.6); moon.position.set(-8, 5, 2); scene.add(moon);
  const lampL = new THREE.PointLight('#ffb45e', 2.2, 5, 1.6); lampL.position.set(2.1, 1.55, 1.9); scene.add(lampL);
  const tvL = new THREE.PointLight('#7aa0ff', 6, 9, 1.0); tvL.position.set(0, 1.1, -0.9); scene.add(tvL);
  const ledL = new THREE.PointLight('#b44dff', 1.5, 3, 1.6); ledL.position.set(0, 0.25, -1.6); scene.add(ledL);
  const sun = new THREE.DirectionalLight('#ffd7a0', 0); sun.position.set(-9, 3.5, 1.5); sun.target.position.set(0.5, 0.4, 0.5);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -4, right: 4, top: 4, bottom: -4, near: 1, far: 25}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.02;
  scene.add(sun, sun.target);

  // Raum
  const floorT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#7a5a3e'; g.fillRect(0, 0, w, h); const r = rng(4);
    for (let y = 0; y < h; y += 40) { g.fillStyle = 'rgba(0,0,0,0.14)'; g.fillRect(0, y, w, 2); for (let i = 0; i < 30; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '255,225,190' : '40,25,12'},${r() * 0.1})`; g.fillRect(r() * w, y + r() * 38, 40 + r() * 140, 2); } } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(3, 3);
  const fl = mesh(new THREE.PlaneGeometry(RW * 2, ZF - ZB), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.5}), 0, 0, (ZB + ZF) / 2, scene); fl.rotation.x = -Math.PI / 2;
  const wallT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#5b6470'; g.fillRect(0, 0, w, h); const r = rng(8); for (let i = 0; i < 2000; i++) { g.fillStyle = `rgba(0,0,0,${r() * 0.04})`; g.fillRect(r() * w, r() * h, 2, 2); } });
  const wallM = new THREE.MeshStandardMaterial({map: wallT, roughness: 0.95});
  mesh(new THREE.PlaneGeometry(RW * 2, ZF - ZB), mat('#2a2d33'), 0, RH, (ZB + ZF) / 2, scene).rotation.x = Math.PI / 2;
  mesh(new THREE.BoxGeometry(RW * 2, RH, 0.1), wallM, 0, RH / 2, ZB - 0.05, scene);
  mesh(new THREE.BoxGeometry(RW * 2, RH, 0.1), wallM, 0, RH / 2, ZF + 0.05, scene);
  mesh(new THREE.BoxGeometry(0.1, RH, ZF - ZB), wallM, RW + 0.05, RH / 2, (ZB + ZF) / 2, scene);
  // linke Wand mit großem Fenster (z -0.6..1.8)
  const wz0 = -0.6, wz1 = 1.8, wy0 = 0.75, wy1 = 2.3;
  const wl = (y0, y1, z0, z1) => mesh(new THREE.BoxGeometry(0.15, y1 - y0, z1 - z0), wallM, -RW - 0.07, (y0 + y1) / 2, (z0 + z1) / 2, scene);
  wl(0, wy0, ZB, ZF); wl(wy1, RH, ZB, ZF); wl(wy0, wy1, ZB, wz0); wl(wy0, wy1, wz1, ZF);
  const frM = mat('#d8d8d4', {roughness: 0.5});
  for (const z of [wz0, (wz0 + wz1) / 2, wz1]) mesh(new THREE.BoxGeometry(0.1, wy1 - wy0, 0.06), frM, -RW, (wy0 + wy1) / 2, z, scene);
  for (const y of [wy0, wy1]) mesh(new THREE.BoxGeometry(0.1, 0.06, wz1 - wz0), frM, -RW, y, (wz0 + wz1) / 2, scene);
  // Blick nach draußen: Nachts Hochhäuser mit Fenstern, morgens heller Himmel
  const night = canvasTex(1024, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#060a18'); gr.addColorStop(1, '#1d2440'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(12); for (let i = 0; i < 18; i++) { const bw = 50 + r() * 90, bh = 120 + r() * 300, x = i * 60 - 20; g.fillStyle = `rgb(${14 + r() * 10},${16 + r() * 10},${26 + r() * 12})`; g.fillRect(x, h - bh, bw, bh);
      for (let yy = h - bh + 10; yy < h - 8; yy += 18) for (let xx = x + 6; xx < x + bw - 8; xx += 14) if (r() < 0.3) { g.fillStyle = r() < 0.5 ? `rgba(120,160,255,${0.5 + r() * 0.4})` : `rgba(255,210,140,${0.5 + r() * 0.4})`; g.fillRect(xx, yy, 7, 9); } } });
  const morning = canvasTex(1024, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#8db8e8'); gr.addColorStop(0.7, '#f6cf9c'); gr.addColorStop(1, '#f9e2bf'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const r = rng(12); for (let i = 0; i < 18; i++) { const bw = 50 + r() * 90, bh = 120 + r() * 300, x = i * 60 - 20; g.fillStyle = `rgb(${150 + r() * 30},${150 + r() * 25},${165 + r() * 20})`; g.fillRect(x, h - bh, bw, bh);
      for (let yy = h - bh + 10; yy < h - 8; yy += 18) for (let xx = x + 6; xx < x + bw - 8; xx += 14) { g.fillStyle = 'rgba(90,110,140,0.5)'; g.fillRect(xx, yy, 7, 9); } } });
  const outN = mesh(new THREE.PlaneGeometry(16, 8), new THREE.MeshBasicMaterial({map: night}), -RW - 5, 1.6, 0.6, scene); outN.rotation.y = Math.PI / 2;
  const outD = mesh(new THREE.PlaneGeometry(16, 8), new THREE.MeshBasicMaterial({map: morning}), -RW - 5, 1.6, 0.6, scene); outD.rotation.y = Math.PI / 2;
  const curtM = new THREE.MeshStandardMaterial({color: '#4a3b35', roughness: 1, side: THREE.DoubleSide});
  for (const [z0, z1] of [[-0.75, -0.25], [1.5, 2.0]]) mesh(new THREE.PlaneGeometry(z1 - z0, 2.35), curtM, -RW + 0.12, 1.3, (z0 + z1) / 2, scene).rotation.y = Math.PI / 2;

  // Sofa (Rücken zur Kamera hinten, Blick nach -z)
  const sofaM = mat('#3e4a5c', {roughness: 0.95});
  const sofa = new THREE.Group(); sofa.position.set(0, 0, 1.15); scene.add(sofa);
  mesh(new RoundedBoxGeometry(2.3, 0.42, 0.95, 3, 0.06), sofaM, 0, 0.21, 0, sofa);
  for (const x of [-0.56, 0.56]) mesh(new RoundedBoxGeometry(1.1, 0.16, 0.85, 3, 0.07), sofaM, x, 0.49, -0.04, sofa);
  mesh(new RoundedBoxGeometry(2.3, 0.62, 0.24, 3, 0.08), sofaM, 0, 0.72, 0.38, sofa);
  for (const x of [-1.08, 1.08]) mesh(new RoundedBoxGeometry(0.22, 0.62, 0.95, 3, 0.08), sofaM, x, 0.42, 0, sofa);
  const pillow = mesh(new RoundedBoxGeometry(0.42, 0.36, 0.14, 3, 0.07), mat('#c97a3a', {roughness: 1}), -0.82, 0.72, 0.22, sofa); pillow.rotation.set(-0.3, 0.2, 0.15);
  const blanket = mesh(new RoundedBoxGeometry(0.7, 0.08, 0.8, 3, 0.04), mat('#7a2f3a', {roughness: 1}), 0.75, 0.6, 0.05, sofa); blanket.rotation.z = 0.06;

  // Couchtisch mit Pizza, Dosen, Chips
  const tbl = new THREE.Group(); tbl.position.set(0, 0, 0.0); scene.add(tbl);
  mesh(new RoundedBoxGeometry(1.2, 0.05, 0.6, 2, 0.02), mat('#2b2420', {roughness: 0.4}), 0, 0.4, 0, tbl);
  for (const [x, z] of [[-0.55, -0.25], [0.55, -0.25], [-0.55, 0.25], [0.55, 0.25]]) mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.4, 8), mat('#111'), x, 0.2, z, tbl);
  const pz = new THREE.Group(); pz.position.set(-0.28, 0.43, 0.02); pz.rotation.y = 0.2; tbl.add(pz);
  mesh(new THREE.BoxGeometry(0.42, 0.03, 0.42), mat('#c8a676'), 0, 0, 0, pz); const lid = mesh(new THREE.BoxGeometry(0.42, 0.01, 0.42), mat('#c8a676'), 0, -0.01, -0.43, pz); lid.rotation.x = 0.05;
  const pizzaT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#d99b4a'; g.beginPath(); g.arc(128, 128, 120, 0, 7); g.fill(); g.fillStyle = '#c9472b'; g.beginPath(); g.arc(128, 128, 104, 0, 7); g.fill();
    g.fillStyle = '#f2d27a'; for (let i = 0; i < 40; i++) { const r = rng(i)(); g.beginPath(); g.arc(128 + Math.cos(i) * r * 90, 128 + Math.sin(i * 1.7) * r * 90, 10, 0, 7); g.fill(); }
    g.fillStyle = '#8a2a20'; for (let i = 0; i < 12; i++) { g.beginPath(); g.arc(128 + Math.cos(i * 2.1) * 70, 128 + Math.sin(i * 2.1) * 60, 12, 0, 7); g.fill(); }
    g.fillStyle = '#c8a676'; g.beginPath(); g.moveTo(128, 128); g.arc(128, 128, 125, 0.2, 1.9); g.fill(); });
  const pzz = mesh(new THREE.PlaneGeometry(0.38, 0.38), new THREE.MeshStandardMaterial({map: pizzaT, roughness: 0.8, transparent: true, alphaTest: 0.1}), 0, 0.017, 0, pz); pzz.rotation.x = -Math.PI / 2;
  const canM = [mat('#16c26a', {metalness: 0.8, roughness: 0.3}), mat('#e8e8e8', {metalness: 0.8, roughness: 0.3}), mat('#1f6fe0', {metalness: 0.8, roughness: 0.3})];
  [[0.25, 0.1, 0], [0.38, -0.12, 1], [0.48, 0.15, 2], [0.12, -0.18, 0]].forEach(([x, z, c], i) => { const cn = mesh(new THREE.CylinderGeometry(0.033, 0.033, 0.12, 16), canM[c], x, 0.485, z, tbl); if (i === 3) { cn.rotation.z = Math.PI / 2; cn.position.y = 0.455; } });
  const chips = mesh(new RoundedBoxGeometry(0.22, 0.05, 0.3, 2, 0.02), mat('#e5b31b', {roughness: 0.5, metalness: 0.4}), 0.35, 0.45, -0.18, tbl); chips.rotation.y = 0.6;
  const head = new THREE.Group(); head.position.set(0.55, 0.45, 1.3); scene.add(head); // Headset auf dem Sofa
  mesh(new THREE.TorusGeometry(0.09, 0.012, 6, 20, Math.PI), mat('#1a1a1a'), 0, 0.05, 0, head).rotation.x = -1.2;

  // TV-Möbel, Konsole, Fernseher
  mesh(new THREE.BoxGeometry(2.0, 0.42, 0.45), mat('#1b1c1f', {roughness: 0.5}), 0, 0.21, ZB + 0.28, scene);
  const ledStrip = mesh(new THREE.BoxGeometry(1.95, 0.01, 0.01), new THREE.MeshStandardMaterial({color: '#111', emissive: '#b44dff', emissiveIntensity: 2.5}), 0, 0.005, ZB + 0.5, scene);
  const cons = new THREE.Group(); cons.position.set(0.7, 0.42, ZB + 0.28); scene.add(cons);
  mesh(new RoundedBoxGeometry(0.1, 0.36, 0.28, 3, 0.03), mat('#e9eaee', {roughness: 0.35}), 0, 0.18, 0, cons);
  const consLed = mesh(new THREE.BoxGeometry(0.004, 0.2, 0.004), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#4da3ff', emissiveIntensity: 3}), 0.052, 0.2, 0.12, cons);
  mesh(new RoundedBoxGeometry(0.7, 0.07, 0.09, 2, 0.02), mat('#141414'), -0.1, 0.46, ZB + 0.36, scene); // Soundbar
  const tv = new THREE.Group(); tv.position.set(0, 1.08, ZB + 0.12); scene.add(tv);
  const tvW = 1.46, tvH = 0.82;
  mesh(new RoundedBoxGeometry(tvW + 0.03, tvH + 0.03, 0.05, 2, 0.01), mat('#0b0b0c', {roughness: 0.3}), 0, 0, -0.025, tv);
  const SC = document.createElement('canvas'); SC.width = 1024; SC.height = 576; const scT = new THREE.CanvasTexture(SC); scT.colorSpace = THREE.SRGBColorSpace; scT.anisotropy = 8;
  const screen = mesh(new THREE.PlaneGeometry(tvW, tvH), new THREE.MeshBasicMaterial({map: scT, toneMapped: false}), 0, 0, 0.002, tv);
  mesh(new THREE.BoxGeometry(0.3, 0.02, 0.2), mat('#202020', {metalness: 0.7}), 0, -0.58 + 0.12, 0.0, tv);
  mesh(new THREE.BoxGeometry(0.05, 0.12, 0.05), mat('#202020', {metalness: 0.7}), 0, -0.49, -0.02, tv);
  // Regal mit Figuren und Pflanze rechts
  const shelf = new THREE.Group(); shelf.position.set(RW - 0.25, 0, ZB + 0.9); scene.add(shelf);
  for (let i = 0; i < 4; i++) mesh(new THREE.BoxGeometry(0.4, 0.03, 0.9), mat('#c9b79a'), 0, 0.3 + i * 0.5, 0, shelf);
  mesh(new THREE.BoxGeometry(0.4, 1.9, 0.03), mat('#c9b79a'), 0, 0.95, -0.45, shelf); mesh(new THREE.BoxGeometry(0.4, 1.9, 0.03), mat('#c9b79a'), 0, 0.95, 0.45, shelf);
  const r0 = rng(17); for (let i = 0; i < 4; i++) for (let k = 0; k < 6; k++) if (r0() < 0.7) mesh(new THREE.BoxGeometry(0.16, 0.2, 0.02 + r0() * 0.03), mat(['#c0392b', '#2f6fb5', '#e5b31b', '#2d2d2d', '#3a8a5a'][Math.floor(r0() * 5)]), -0.05, 0.42 + i * 0.5, -0.38 + k * 0.13, shelf);
  const plant = new THREE.Group(); plant.position.set(-RW + 0.4, 0, ZB + 0.5); scene.add(plant);
  mesh(new THREE.CylinderGeometry(0.16, 0.12, 0.35, 14), mat('#d8d0c4'), 0, 0.17, 0, plant);
  for (let i = 0; i < 9; i++) { const lf = mesh(new THREE.SphereGeometry(0.16, 8, 6), mat('#3f7a3a', {flatShading: true}), Math.cos(i * 2.3) * 0.12, 0.5 + (i % 3) * 0.18, Math.sin(i * 2.3) * 0.12, plant); lf.scale.set(1, 0.5, 0.6); }
  // Stehlampe
  const fl2 = new THREE.Group(); fl2.position.set(2.1, 0, 1.9); scene.add(fl2);
  mesh(new THREE.CylinderGeometry(0.015, 0.015, 1.5, 8), mat('#222'), 0, 0.75, 0, fl2); mesh(new THREE.CylinderGeometry(0.12, 0.2, 0.25, 16, 1, true), new THREE.MeshStandardMaterial({color: '#f1d7b0', emissive: '#ffb45e', emissiveIntensity: 0.6, side: THREE.DoubleSide}), 0, 1.55, 0, fl2);
  // Poster
  const posterT = canvasTex(360, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#ff5f6d'); gr.addColorStop(1, '#2b1055'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.fillStyle = '#1d1426'; for (let i = 0; i < 7; i++) g.fillRect(20 + i * 48, 260 - (i % 3) * 60, 40, 260); g.fillStyle = '#ffe2a0'; g.beginPath(); g.arc(w / 2, 230, 70, 0, 7); g.fill();
    g.fillStyle = '#fff'; g.font = '600 40px Plex'; g.textAlign = 'center'; g.fillText('NEON COAST', w / 2, 470); });
  mesh(new THREE.PlaneGeometry(0.6, 0.85), new THREE.MeshStandardMaterial({map: posterT, roughness: 0.7}), RW - 0.01, 1.6, 0.4, scene).rotation.y = -Math.PI / 2;

  // Der Spieler: Hoodie, auf dem Sofa
  const p = makePerson(41, {top: '#2b2f3a', pants: '#3a3a3a', hair: '#2a1d15', skin: '#d9a47e'}); p.position.set(0.05, 0, 1.12); scene.add(p);
  const u = p.userData;
  const hood = mesh(new THREE.SphereGeometry(0.14, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.5), mat('#2b2f3a', {roughness: 1}), 0, 0.64, -0.1, u.torso); hood.rotation.x = -1.9; hood.scale.set(1.2, 1, 0.7);
  // Controller (in den Händen, als Kind des Oberkörpers) und fliegender Controller
  const ctrlGeo = () => { const c = new THREE.Group(); mesh(new RoundedBoxGeometry(0.16, 0.03, 0.09, 3, 0.012), mat('#1b1d22', {roughness: 0.4}), 0, 0, 0, c);
    for (const x of [-0.06, 0.06]) mesh(new THREE.SphereGeometry(0.03, 10, 8), mat('#1b1d22', {roughness: 0.4}), x, -0.006, 0.035, c);
    mesh(new THREE.BoxGeometry(0.05, 0.002, 0.02), new THREE.MeshStandardMaterial({color: '#fff', emissive: '#4da3ff', emissiveIntensity: 2}), 0, 0.016, -0.03, c); return c; };
  const ctrlHand = ctrlGeo(); ctrlHand.position.set(-0.05, -0.31, 0.03); ctrlHand.rotation.set(0, 0, 1.3); u.armR.userData.fore.add(ctrlHand);
  const ctrlFly = ctrlGeo(); scene.add(ctrlFly);
  const crackT = canvasTex(1024, 576, () => {}); // wird nicht genutzt (Sprünge werden direkt gezeichnet)
  void crackT;

  // Sitzpose: Oberschenkel nach vorn, Unterschenkel nach unten
  function sit(lean = 0, arms = 'hold', k = 0) {
    posePerson(p, {walk: 0, walkAmp: 0});
    u.hips.position.y = 0.52 / u.h; u.body.rotation.x = -0.12 - lean;
    [u.legL, u.legR].forEach((lg, i) => { lg.rotation.x = -1.45; lg.rotation.z = (i ? 0.1 : -0.1); lg.userData.knee.rotation.x = 1.4; });
    u.pl.forEach((g, i) => { const lg = i ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); const a = 1.4;
      g.userData.low.position.set(0, -0.42 - 0.2 * Math.cos(a), -0.2 * Math.sin(a)); g.userData.low.rotation.x = a; });
    if (arms === 'hold') { u.armL.rotation.set(-0.75, 0, 0.25); u.armR.rotation.set(-0.75, 0, -0.25); u.armL.userData.fore.rotation.x = -1.0; u.armR.userData.fore.rotation.x = -1.0; }
  }
  // Sprünge im Display
  function cracks(g, w, h, k) {
    if (k <= 0) return; const r = rng(77), cx = w * 0.58, cy = h * 0.42;
    g.save(); g.globalAlpha = 1;
    const bl = g.createRadialGradient(cx, cy, 5, cx, cy, 260 * k); bl.addColorStop(0, 'rgba(0,0,0,0.95)'); bl.addColorStop(0.5, 'rgba(10,0,30,0.6)'); bl.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = bl; g.fillRect(0, 0, w, h);
    g.strokeStyle = 'rgba(235,240,255,0.85)'; g.lineWidth = 1.5;
    for (let i = 0; i < 26; i++) { let x = cx, y = cy, a = r() * 7; g.beginPath(); g.moveTo(x, y); const L = (120 + r() * 520) * k;
      for (let s = 0; s < L; s += 30) { a += (r() - 0.5) * 0.6; x += Math.cos(a) * 30; y += Math.sin(a) * 30; g.lineTo(x, y); } g.stroke(); }
    for (let i = 0; i < 5; i++) { g.beginPath(); g.arc(cx, cy, (25 + i * 30) * k, 0, 7); g.stroke(); }
    for (let i = 0; i < 6; i++) { g.fillStyle = ['#ff00ff', '#00ffff', '#fff', '#00ff66'][i % 4]; g.fillRect(cx - 300 + i * 97 + r() * 30, 0, 2, h); }
    g.restore();
  }
  function drawTV(T, morning) {
    const g = SC.getContext('2d'), w = SC.width, h = SC.height;
    let lum = 1, col = '#ff8a7a';
    if (morning) { const t = T - 80; drawDownload(g, w, h, T, t < 6 ? 1 : 2, t < 6 ? '9 Std. 41 Min.' : '9 Std. 40 Min.'); col = '#5a8cff'; lum = 0.7; }
    else if (T < VANISH) drawChase(g, w, h, T);
    else if (T < VANISH + 0.5) { drawChase(g, w, h, VANISH); const r = rng(Math.floor(T * 30));
      for (let i = 0; i < 40; i++) { const y = r() * h, hh = 4 + r() * 50; g.drawImage(SC, 0, y, w, hh, (r() - 0.5) * 200, y, w, hh); }
      for (let i = 0; i < 30; i++) { g.fillStyle = ['#ff00ff', '#00ffff', '#000', '#fff'][Math.floor(r() * 4)]; g.fillRect(r() * w, r() * h, r() * 300, 4 + r() * 20); }
      g.fillStyle = `rgba(0,0,0,${(T - VANISH) / 0.5})`; g.fillRect(0, 0, w, h); }
    else if (T < VANISH + 1.4) { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); lum = 0.05; }
    else { drawHome(g, w, h, T, smooth(VANISH + 1.4, VANISH + 1.9, T)); col = '#6f9bff'; lum = 1.0; }
    if (T >= HIT) cracks(g, w, h, Math.min(1, (T - HIT) / 0.12));
    scT.needsUpdate = true; return {lum, col};
  }

  const camera = new THREE.PerspectiveCamera(42, 1080 / 1920, 0.03, 200); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const id = shot.id, t = T - shot.t0, morning = id === 'end';
    const {lum, col} = drawTV(T, morning);
    tvL.color.set(col); tvL.intensity = (morning ? 1.0 : 9) * lum * (T < VANISH ? 0.85 + 0.15 * Math.sin(T * 9) * Math.sin(T * 3.3) : 1);
    // Tageszeit
    outN.visible = !morning; outD.visible = morning;
    sun.intensity = morning ? 2.6 : 0; moon.intensity = morning ? 0 : 0.6; hemi.intensity = morning ? 0.9 : 0.25; hemi.color.set(morning ? '#cfe0ff' : '#6c80b8');
    scene.environmentIntensity = morning ? 0.4 : 0.12; lampL.intensity = morning ? 0 : 2.2; ledStrip.material.emissiveIntensity = morning ? 0.8 : 2.5;
    scene.background.set(morning ? '#c9d8ea' : '#05070c');
    // Spieler
    ctrlFly.visible = false; ctrlHand.visible = true;
    if (morning) { // eingeschlafen, zur Seite gekippt
      sit(0, 'hold'); u.body.rotation.x = 0.18; u.body.rotation.z = 0.08; u.head.rotation.set(-0.55 + Math.sin(T * 1.1) * 0.03, 0, 0.3);
      u.armL.rotation.set(-0.25, 0, 0.12); u.armR.rotation.set(-0.3, 0, -0.15); u.armL.userData.fore.rotation.x = -0.3; u.armR.userData.fore.rotation.x = -0.3; ctrlHand.visible = false;
      ctrlFly.visible = true; ctrlFly.position.set(0.15, 0.015, -1.45); ctrlFly.rotation.set(0, 0.7, Math.PI);
    } else if (T < VANISH + 0.6) {
      sit(0.05); const st = Math.sin(T * 9) * 0.08; u.armL.rotation.y = st; u.armR.rotation.y = st; u.torso.rotation.y = Math.sin(T * 1.6) * 0.12; u.head.rotation.x = 0.15;
    } else if (T < THROW - 0.5) { // erstarrt, beugt sich vor
      const k = smooth(VANISH + 0.6, VANISH + 2.0, T); sit(0.05 - 0.25 * k); u.head.rotation.x = 0.15 + 0.1 * k;
      const q = smooth(VANISH + 1.6, VANISH + 2.2, T); u.armL.rotation.set(lerp(-0.75, -2.7, q), 0, lerp(0.25, 0.5, q)); u.armR.rotation.set(lerp(-0.75, -2.7, q), 0, lerp(-0.25, -0.5, q));
      u.armL.userData.fore.rotation.x = lerp(-1.0, -1.7, q); u.armR.userData.fore.rotation.x = lerp(-1.0, -1.7, q);
    } else { // Wurf
      sit(-0.2); const wind = smooth(THROW - 0.5, THROW - 0.1, T), rel = smooth(THROW - 0.1, THROW + 0.05, T);
      u.armR.rotation.set(lerp(-0.75, -2.9, wind) + rel * 1.9, 0, -0.25); u.armR.userData.fore.rotation.x = lerp(-1.0, -1.6, wind) + rel * 1.4;
      u.torso.rotation.y = -0.4 * wind + 0.5 * rel; u.body.rotation.x = -0.12 + 0.2 * wind - 0.4 * rel;
      if (T >= THROW) { ctrlHand.visible = false; ctrlFly.visible = true;
        const a = V3(0.25, 1.15, 1.25), b = V3(0.27, 1.27, ZB + 0.16), k = clamp((T - THROW) / (HIT - THROW));
        if (T < HIT) { ctrlFly.position.lerpVectors(a, b, k); ctrlFly.position.y += Math.sin(k * Math.PI) * 0.22; ctrlFly.rotation.set(k * 9, k * 4, k * 2); }
        else { const d = T - HIT; const y = Math.max(0.03, 1.27 + 1.2 * d - 4.9 * d * d); ctrlFly.position.set(0.27 + d * 0.3, y, ZB + 0.25 + d * 0.6); ctrlFly.rotation.set(9 + d * 6, 4, 2 + d * 3); }
      }
      const slump = smooth(HIT + 0.8, HIT + 1.8, T); // Hände vors Gesicht, zurück ins Sofa
      if (slump > 0) { u.body.rotation.x = lerp(u.body.rotation.x, 0.25, slump); u.armL.rotation.set(lerp(-0.75, -2.4, slump), 0, 0.3); u.armR.rotation.set(lerp(u.armR.rotation.x, -2.4, slump), 0, -0.3);
        u.armL.userData.fore.rotation.x = -1.9 * slump; u.armR.userData.fore.rotation.x = -1.9 * slump; u.head.rotation.x = -0.25 * slump; }
    }
    // Fernseher wackelt nach dem Treffer
    const dh = T - HIT; tv.rotation.x = dh > 0 && dh < 2 ? -Math.sin(dh * 14) * Math.exp(-dh * 3) * 0.06 : 0;
    // Kamera
    camera.fov = 42;
    if (id === 'intro') { camera.position.set(0.55 - t * 0.02, 1.42, 2.45 - t * 0.06); camera.lookAt(0.0, 1.0, ZB); }
    else if (id === 'wait') { const k = smooth(0, 6.5, t); camera.position.set(lerp(0.95, 0.75, k), lerp(1.95, 1.85, k), lerp(2.75, 2.55, k)); camera.lookAt(-0.05, 0.78, -0.6); }
    else if (id === 'couch') {
      if (T < THROW - 0.7) { const k = smooth(0, 3.5, t); camera.position.set(lerp(-0.6, -0.5, k) + noise1(T, 2) * 0.01, lerp(1.55, 1.48, k), lerp(2.55, 2.3, k)); camera.lookAt(0.2, 0.9, -1.0); }
      else { const k = smooth(THROW - 0.7, shot.t1, T); camera.position.set(lerp(0.75, 0.6, k), lerp(2.15, 2.05, k), lerp(2.7, 2.55, k)); camera.lookAt(0.0, 0.82, -1.0);
        const sh = T > HIT && T < HIT + 0.6 ? (1 - (T - HIT) / 0.6) * 0.012 : 0; camera.position.x += Math.sin(T * 60) * sh; camera.position.y += Math.cos(T * 53) * sh; }
    } else { const k = smooth(0, 10, t); camera.position.set(lerp(0.55, 0.45, k), lerp(2.05, 1.95, k), lerp(2.7, 2.55, k)); camera.lookAt(0.05, 0.55, -0.1); camera.fov = 48; }
    camera.updateProjectionMatrix();
  }};
}
