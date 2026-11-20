// Stufe 2: Nachts im Bett, Handy in der Hand: Ein Livestream mit 2,1 Mio. Zuschauern. Das Spiel verschwindet mitten im Stream,
// der Chat explodiert. Gegenüber gehen in den Wohnungen die Lichter an.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, envMap} from './lib.js';
import {makePhone, makeHands, updateScreen} from './phone.js';
import {drawChase, drawHome} from './living.js';
import {STREAM_BLACK} from './timeline.js';

const NAMES = ['lena_xo', 'BigMo', 'krasserTyp', 'mia.gg', 'noob_master', 'Jonas2009', 'svenja', 'TTV_kev', 'paul.exe', 'lilly', 'Kaan_07', 'zocker_tom', 'emma.lua', 'NightFox', 'ben_ok', 'aylin', 'xXSniperXx', 'leonie_', 'fynn', 'Mats'];
const CALM = ['den kriegen die nie 😂', 'LINKS LINKS LINKS', 'wie schnell ist das auto', 'grafik ist krank', 'ich hab 6 std geschlafen seit launch', 'W stream', 'nimm die brücke!', 'bester launch ever', 'gg', 'die palmen 😍'];
const PANIC = ['???', 'WAS', 'NEIN NEIN NEIN', 'bei mir auch weg!!!', 'mein spielstand 😭', 'F', 'F', 'F', 'ALLES WEG', 'server down??', 'ist das ein bug', 'mein spiel ist gelöscht', 'WTF', 'ich weine', 'refresh!!!', 'BEI MIR AUCH', '😭😭😭', 'disc ist leer???'];

function drawStream(g, st, SW, SH) {
  const T = st.t, black = T >= STREAM_BLACK, r = rng(5);
  g.fillStyle = '#0e0e12'; g.fillRect(0, 0, SW, SH);
  // Statusleiste
  g.fillStyle = '#fff'; g.font = '500 22px Plex'; g.textAlign = 'left'; g.fillText('02:14', 34, 44); g.textAlign = 'right'; g.fillText('5G  23%', SW - 34, 44);
  // Video (16:9)
  const vy = 80, vh = Math.round(SW * 9 / 16);
  const vc = document.createElement('canvas'); vc.width = 1024; vc.height = 576; const v = vc.getContext('2d');
  if (!black) drawChase(v, 1024, 576, T);
  else if (T < STREAM_BLACK + 0.5) { drawChase(v, 1024, 576, STREAM_BLACK); const q = rng(Math.floor(T * 30)); for (let i = 0; i < 40; i++) { v.fillStyle = ['#f0f', '#0ff', '#000', '#fff'][Math.floor(q() * 4)]; v.fillRect(q() * 1024, q() * 576, q() * 400, 4 + q() * 30); }
    v.fillStyle = `rgba(0,0,0,${(T - STREAM_BLACK) / 0.5})`; v.fillRect(0, 0, 1024, 576); }
  else if (T < STREAM_BLACK + 1.2) { v.fillStyle = '#000'; v.fillRect(0, 0, 1024, 576); }
  else drawHome(v, 1024, 576, T, 1);
  g.drawImage(vc, 0, vy, SW, vh);
  // Webcam des (erfundenen) Streamers: Silhouette mit Headset
  const cx = SW - 120, cy = vy + vh - 100;
  g.fillStyle = '#2a2140'; g.fillRect(cx - 60, cy - 60, 150, 150); g.strokeStyle = '#a970ff'; g.lineWidth = 3; g.strokeRect(cx - 60, cy - 60, 150, 150);
  const panic = black ? smooth(STREAM_BLACK + 0.3, STREAM_BLACK + 0.8, T) : 0, jump = panic * Math.abs(Math.sin(T * 9)) * 6;
  g.fillStyle = '#e0b090'; g.beginPath(); g.arc(cx + 15, cy + 5 - jump, 34, 0, 7); g.fill(); g.fillStyle = '#3a2a1e'; g.beginPath(); g.arc(cx + 15, cy - 5 - jump, 35, Math.PI, 0); g.fill();
  g.fillStyle = '#4b3b7a'; g.beginPath(); g.ellipse(cx + 15, cy + 90 - jump, 60, 45, 0, Math.PI, 0); g.fill();
  g.strokeStyle = '#111'; g.lineWidth = 7; g.beginPath(); g.arc(cx + 15, cy - 2 - jump, 40, Math.PI * 1.05, Math.PI * 1.95); g.stroke(); g.fillStyle = '#111'; g.fillRect(cx - 30, cy - 5 - jump, 12, 26); g.fillRect(cx + 48, cy - 5 - jump, 12, 26);
  g.fillStyle = '#111'; g.beginPath(); g.arc(cx + 3, cy + 2 - jump, 3.5, 0, 7); g.arc(cx + 27, cy + 2 - jump, 3.5, 0, 7); g.fill();
  if (panic > 0) { g.beginPath(); g.ellipse(cx + 15, cy + 22 - jump, 9, 12 * panic, 0, 0, 7); g.fill(); // Mund auf, Hände am Kopf
    g.fillStyle = '#e0b090'; g.beginPath(); g.arc(cx - 26, cy - 22 - jump, 13 * panic, 0, 7); g.arc(cx + 56, cy - 22 - jump, 13 * panic, 0, 7); g.fill(); }
  else { g.strokeStyle = '#111'; g.lineWidth = 3; g.beginPath(); g.arc(cx + 15, cy + 14, 9, 0.2, Math.PI - 0.2); g.stroke(); }
  // Kanalzeile
  const iy = vy + vh + 20;
  g.fillStyle = '#e91916'; g.beginPath(); g.roundRect(24, iy, 74, 34, 6); g.fill(); g.fillStyle = '#fff'; g.font = '600 20px Plex'; g.textAlign = 'center'; g.fillText('LIVE', 61, iy + 24);
  const k = smooth(STREAM_BLACK + 0.4, STREAM_BLACK + 5.4, T), viewers = (2.1 - 1.7 * Math.pow(k, 0.7)).toFixed(1).replace('.', ',');
  g.textAlign = 'left'; g.fillStyle = '#ff5c5c'; g.fillText(`● ${viewers} Mio. Zuschauer`, 112, iy + 24);
  g.fillStyle = '#fff'; g.font = '600 26px Plex'; g.fillText('NeonRider_Live', 24, iy + 72); g.fillStyle = 'rgba(255,255,255,0.6)'; g.font = '400 20px Plex'; g.fillText('TAG 2 · DURCHZOCKEN BIS ZUM ENDE', 24, iy + 102);
  // Chat
  const top = iy + 130; g.fillStyle = '#18181b'; g.fillRect(0, top, SW, SH - top);
  g.save(); g.beginPath(); g.rect(0, top, SW, SH - top - 90); g.clip();
  const rate = black ? 22 : 4, lines = 40; const base = Math.floor(T * rate) + (black ? 800 : 0);
  for (let i = 0; i < lines; i++) { const idx = base - i, q = rng(idx * 7919 + 104729); q(); q(); const y = SH - 120 - i * 40 - ((T * rate) % 1) * 40; if (y < top) break;
    const name = NAMES[Math.floor(q() * NAMES.length)], hue = Math.floor(q() * 360);
    const pool = black && idx > 800 + Math.floor((STREAM_BLACK + 0.4) * 22) ? PANIC : CALM; const msg = pool[Math.floor(q() * pool.length)];
    g.font = '600 22px Plex'; g.fillStyle = `hsl(${hue},80%,65%)`; g.fillText(name + ':', 24, y); const nw = g.measureText(name + ': ').width;
    g.font = pool === PANIC && q() < 0.5 ? '600 24px Plex' : '400 22px Plex'; g.fillStyle = '#efeff1'; g.fillText(msg, 24 + nw, y); }
  g.restore();
  // Eingabefeld
  g.fillStyle = '#26262c'; g.beginPath(); g.roundRect(20, SH - 78, SW - 40, 54, 27); g.fill(); g.fillStyle = 'rgba(255,255,255,0.4)'; g.font = '400 21px Plex'; g.fillText('Nachricht senden', 44, SH - 44);
  // Herzen/Emotes steigen auf
  if (black) for (let i = 0; i < 14; i++) { const q = rng(i + 50), a = (T * 0.9 + q()) % 1; g.globalAlpha = 1 - a; g.font = '40px sans-serif'; g.fillText(['😭', '💀', '😱'][i % 3], SW - 90 + q() * 50, top + 300 - a * 260); }
  g.globalAlpha = 1; void r;
}

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#04060c');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.06;
  const hemi = new THREE.HemisphereLight('#5a6c9c', '#100c08', 0.18); scene.add(hemi);
  const phoneL = new THREE.PointLight('#c8d4ff', 1.6, 2.5, 1.5); scene.add(phoneL);
  const street = new THREE.PointLight('#ffb070', 2, 9, 1.5); street.position.set(1.5, 2.6, -3.4); scene.add(street);
  // Bett: Decke (Hügel), Kissen, Wand mit Fenster vorn
  const blanketG = new THREE.PlaneGeometry(2.2, 2.4, 40, 40); blanketG.rotateX(-Math.PI / 2);
  { const p = blanketG.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); p.setY(i, 0.12 * Math.sin(x * 3.1 + z * 1.3) + 0.08 * Math.sin(z * 4.2) + 0.25 * Math.exp(-((x - 0.1) ** 2) * 6 - ((z - 0.3) ** 2) * 1.5)); } blanketG.computeVertexNormals(); }
  const blT = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#3b4d6e'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(255,255,255,0.08)'; g.lineWidth = 6; for (let i = 0; i < 12; i++) { g.beginPath(); g.moveTo(i * 24, 0); g.lineTo(i * 24, h); g.stroke(); } });
  mesh(blanketG, new THREE.MeshStandardMaterial({map: blT, roughness: 1}), 0, 0.45, -0.9, scene);
  mesh(new THREE.BoxGeometry(2.4, 0.5, 2.6), mat('#2a2420'), 0, 0.2, -0.9, scene);
  const wallM = mat('#2e3440', {roughness: 0.95});
  const WZ = -2.3, wx0 = -0.9, wx1 = 0.9, wy0 = 0.9, wy1 = 2.3;
  const wl = (x0, x1, y0, y1) => mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, 0.15), wallM, (x0 + x1) / 2, (y0 + y1) / 2, WZ, scene);
  wl(-3, 3, 0, wy0); wl(-3, 3, wy1, 3); wl(-3, wx0, wy0, wy1); wl(wx1, 3, wy0, wy1);
  for (const x of [wx0, 0, wx1]) mesh(new THREE.BoxGeometry(0.06, wy1 - wy0, 0.12), mat('#d8d8d4'), x, (wy0 + wy1) / 2, WZ + 0.02, scene);
  mesh(new THREE.BoxGeometry(wx1 - wx0, 0.06, 0.2), mat('#d8d8d4'), 0, wy0, WZ + 0.05, scene);
  // Haus gegenüber: Fensterraster als Canvas, wird jedes Bild neu gezeichnet
  const FC = document.createElement('canvas'); FC.width = 1024; FC.height = 1024; const fT = new THREE.CanvasTexture(FC); fT.colorSpace = THREE.SRGBColorSpace;
  const front = mesh(new THREE.PlaneGeometry(26, 26), new THREE.MeshBasicMaterial({map: fT}), 0, 6, -22, scene);
  const sky = mesh(new THREE.PlaneGeometry(80, 40), new THREE.MeshBasicMaterial({color: '#0b1226'}), 0, 10, -40, scene); void sky; void front;
  const WIN = []; { const r = rng(21); for (let row = 0; row < 14; row++) for (let col = 0; col < 12; col++) WIN.push({row, col, tv: r() < 0.45, lit: r() < 0.25, wake: STREAM_BLACK + 0.6 + r() * 4.5, person: r() < 0.5, ph: r() * 6}); }
  function drawFront(T) {
    const g = FC.getContext('2d'); g.fillStyle = '#1a1c24'; g.fillRect(0, 0, 1024, 1024);
    for (const w of WIN) { const x = 30 + w.col * 82, y = 30 + w.row * 70; let c = '#07080c';
      const black = T >= STREAM_BLACK + 0.2 + (w.ph % 1) * 0.6;
      if (w.tv) c = black ? '#2b4fa8' : (Math.sin(T * 7 + w.ph) > 0 ? '#7a63d8' : '#5a83ff');
      if (w.lit) c = '#d9a05a';
      const wake = T > w.wake; if (wake && w.tv) c = '#f2c27a';
      g.fillStyle = c; g.fillRect(x, y, 52, 46);
      if (wake && w.tv && w.person) { g.fillStyle = '#20140c'; const yy = y + 46 - 32; g.beginPath(); g.arc(x + 26 + Math.sin(T * 3 + w.ph) * 6, yy, 8, 0, 7); g.fill(); g.fillRect(x + 16 + Math.sin(T * 3 + w.ph) * 6, yy + 8, 20, 30); }
      g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(x + 25, y, 2, 46); }
    fT.needsUpdate = true;
  }

  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.02, 200); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#1d1f24'); const hands = makeHands('#d9a47e', '#5a3a5e');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig); rig.scale.setScalar(1.0);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    drawFront(T);
    updateScreen(phone, [], {t: T, noDrops: true, custom: drawStream});
    // Kamera: im Bett halb aufgerichtet, Blick aufs Handy, später hebt sich der Blick zum Fenster
    const look = smooth(3.6, 5.6, t), shake = T > STREAM_BLACK ? 0.004 : 0.001;
    camera.position.set(0.05 + noise1(T * 2, 1) * shake, 1.05 + look * 0.12, 0.35);
    camera.rotation.set(lerp(-0.42, -0.02, look), 0.04, 0);
    rig.position.set(0.012, lerp(-0.045, -0.2, look), -0.2); rig.rotation.set(lerp(0.2, -0.3, look), 0, 0.02);
    phoneL.position.copy(camera.position).add(new THREE.Vector3(0, -0.3, -0.35)); phoneL.intensity = T >= STREAM_BLACK + 0.5 && T < STREAM_BLACK + 1.2 ? 0.3 : 1.6;
    camera.updateProjectionMatrix();
  }};
}
