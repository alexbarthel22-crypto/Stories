// Frühwarnzentrale im Bunker: Erst zeigen alle Bildschirme Rechenmüll, dann meldet das System einen Raketenstart.
// Nach der Rückkehr von Mathe werden die Bildschirme klar – der Alarm bleibt. Am Ende: ein Offizier muss entscheiden.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson} from './lib.js';
import {VANISH, RETURN, ALARM, DECIDE_START} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

// Abschussorte (Nordamerika) und Ziele (Osten), lat/lon
const LAUNCH = [[47.5, -111.3], [46.4, -104.6], [41.2, -104.9], [48.4, -101.4], [44.1, -103.2]];
const TARGET = [[55.7, 37.6], [59.9, 30.3], [56.8, 60.6], [53.2, 50.1], [55.0, 82.9]];

function canvasDyn(w, h) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return {c, g: c.getContext('2d'), t};
}

// Sitzende Pose (Stuhl), s = 0 sitzt, 1 steht
function seat(p, s, look, lean = 0) {
  posePerson(p, {look});
  const u = p.userData, k = 1 - s;
  u.hips.position.y = lerp(0.92, 0.52, k);
  u.legL.rotation.x = u.legR.rotation.x = -1.5 * k;
  u.legL.userData.knee.rotation.x = u.legR.userData.knee.rotation.x = 1.5 * k;
  u.torso.rotation.x = lean * k;
  u.armL.rotation.x = u.armR.rotation.x = lerp(-0.2, -0.95, k);
  u.armL.userData.fore.rotation.x = u.armR.userData.fore.rotation.x = lerp(-0.25, -0.5, k);
  u.pl.forEach((g, i) => { const lg = i ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
}

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#020304');
  scene.fog = new THREE.Fog('#020305', 14, 40);
  const hemi = new THREE.HemisphereLight('#5f7db0', '#101216', 0.22); scene.add(hemi);
  // Betonraum
  const concTex = canvasTex(512, 512, (g, w, h) => { const r = rng(4); g.fillStyle = '#6d6f70'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 4000; i++) { const v = 90 + r() * 40; g.fillStyle = `rgba(${v},${v},${v},0.12)`; g.fillRect(r() * w, r() * h, 2 + r() * 4, 2 + r() * 4); }
    g.strokeStyle = 'rgba(30,30,30,0.35)'; g.lineWidth = 2; for (let y = 0; y < h; y += 128) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
    for (let i = 0; i < 40; i++) { g.fillStyle = 'rgba(40,40,40,0.25)'; g.beginPath(); g.arc(r() * w, r() * h, 3, 0, 7); g.fill(); } });
  concTex.wrapS = concTex.wrapT = THREE.RepeatWrapping; concTex.repeat.set(4, 1.2);
  const conc = new THREE.MeshStandardMaterial({map: concTex, color: '#7a7c80', roughness: 0.95});
  const W = 26, D = 28, H = 7;
  mesh(new THREE.PlaneGeometry(W, D), mat('#26292c', {roughness: 0.6, metalness: 0.2}), 0, 0, -D / 2 + 8, scene).rotation.x = -Math.PI / 2;
  const ceil = mesh(new THREE.PlaneGeometry(W, D), conc, 0, H, -D / 2 + 8, scene); ceil.rotation.x = Math.PI / 2;
  const back = mesh(new THREE.PlaneGeometry(W, H), conc, 0, H / 2, -20, scene);
  const left = mesh(new THREE.PlaneGeometry(D, H), conc, -W / 2, H / 2, -6, scene); left.rotation.y = Math.PI / 2;
  const right = mesh(new THREE.PlaneGeometry(D, H), conc, W / 2, H / 2, -6, scene); right.rotation.y = -Math.PI / 2;
  // Deckenträger und Rohre
  for (let z = -18; z <= 6; z += 4) mesh(new THREE.BoxGeometry(W, 0.5, 0.4), conc, 0, H - 0.25, z, scene);
  for (const x of [-9, -8.6, 8.4]) { const p = mesh(new THREE.CylinderGeometry(0.12, 0.12, D, 10), mat('#4a5a52', {metalness: 0.5, roughness: 0.5}), x, H - 0.8, -6, scene); p.rotation.x = Math.PI / 2; }
  // Gestufter Boden (Ränge)
  for (const [z, y] of [[-1, 0.3], [3.5, 0.6]]) mesh(new THREE.BoxGeometry(W, y, 4.5), mat('#2b2e31', {roughness: 0.7}), 0, y / 2, z + 1.2, scene);

  // Große Lagewand
  const map = new Image(); map.src = '../tex/earth_night.jpg'; await map.decode();
  const WS = canvasDyn(1600, 720); WS.t.anisotropy = 8;
  const wallScreen = new THREE.Mesh(new THREE.PlaneGeometry(14, 6.3), new THREE.MeshBasicMaterial({map: WS.t, toneMapped: false}));
  wallScreen.position.set(0, 3.65, -19.85); scene.add(wallScreen);
  mesh(new THREE.BoxGeometry(14.5, 6.8, 0.2), mat('#111315', {metalness: 0.5}), 0, 3.65, -19.98, scene);
  // Kartengrundlage einmal vorbereiten (Nordhalbkugel, entsättigt, blaugrün)
  const MW = 1600, MH = 720, LAT0 = 82, LAT1 = 8;
  const base = document.createElement('canvas'); base.width = MW; base.height = MH; { const g = base.getContext('2d');
    g.fillStyle = '#020a10'; g.fillRect(0, 0, MW, MH);
    const sy = (90 - LAT0) / 180 * map.height, sh = (LAT0 - LAT1) / 180 * map.height;
    g.filter = 'grayscale(1) brightness(2.2) contrast(1.3)'; g.globalAlpha = 0.85; g.drawImage(map, 0, sy, map.width, sh, 0, 0, MW, MH); g.filter = 'none'; g.globalAlpha = 1;
    g.globalCompositeOperation = 'multiply'; g.fillStyle = '#4fd0ff'; g.fillRect(0, 0, MW, MH); g.globalCompositeOperation = 'source-over';
    g.strokeStyle = 'rgba(90,200,255,0.18)'; g.lineWidth = 1;
    for (let lon = -180; lon <= 180; lon += 15) { const x = (lon + 180) / 360 * MW; g.beginPath(); g.moveTo(x, 0); g.lineTo(x, MH); g.stroke(); }
    for (let lat = 10; lat <= 80; lat += 10) { const y = (LAT0 - lat) / (LAT0 - LAT1) * MH; g.beginPath(); g.moveTo(0, y); g.lineTo(MW, y); g.stroke(); } }
  const P = (lat, lon) => [(lon + 180) / 360 * MW, (LAT0 - lat) / (LAT0 - LAT1) * MH];

  // Konsolen mit Monitoren
  const MON = canvasDyn(256, 160);
  const monMat = new THREE.MeshBasicMaterial({map: MON.t, toneMapped: false});
  const deskM = mat('#3a3f45', {metalness: 0.4, roughness: 0.5}), dark = mat('#15171a', {metalness: 0.3, roughness: 0.6});
  const people = [];
  const rows = [[-4.5, 0, 0], [0, 0.3, 1], [4.5, 0.6, 2]];
  let pid = 0;
  for (const [z, y0, ri] of rows) for (let i = -2; i <= 2; i++) {
    const x = i * 3.6 + (ri % 2) * 0.6;
    const g = new THREE.Group(); g.position.set(x, y0, z); scene.add(g);
    mesh(new THREE.BoxGeometry(2.8, 0.85, 0.9), deskM, 0, 0.42, 0, g);
    mesh(new THREE.BoxGeometry(2.8, 0.05, 1.0), dark, 0, 0.87, 0.02, g);
    for (const dx of [-0.65, 0.65]) { const m = mesh(new THREE.BoxGeometry(1.1, 0.7, 0.06), dark, dx, 1.3, -0.25, g); m.rotation.x = -0.12;
      const s = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 0.6), monMat); s.position.set(dx, 1.3, -0.215); s.rotation.x = -0.12; g.add(s); }
    // Tastatur
    mesh(new THREE.BoxGeometry(0.9, 0.03, 0.3), mat('#202326'), 0, 0.9, 0.2, g);
    // Stuhl
    mesh(new THREE.BoxGeometry(0.55, 0.08, 0.55), mat('#1c1e22'), 0, 0.5, 0.95, g); mesh(new THREE.BoxGeometry(0.55, 0.65, 0.08), mat('#1c1e22'), 0, 0.85, 1.25, g);
    // Monitorlicht auf das Gesicht
    const ml = new THREE.PointLight('#6fb7ff', 1.2, 3.5, 2); ml.position.set(0, 1.35, 0.15); g.add(ml);
    if ((pid * 7 + 3) % 5 !== 0) { // nicht jeder Platz besetzt
      const p = makePerson(100 + pid, {top: ['#3d4a3a', '#2f3b46', '#454a3a'][pid % 3], pants: '#23282c', shoe: '#111', hair: ['#2a1d15', '#111', '#5a3b22', '#8a8a8a'][pid % 4]});
      p.position.set(x, y0, z + 0.95); p.rotation.y = Math.PI; scene.add(p);
      people.push({p, ml, standAt: ALARM + 0.6 + ((pid * 0.37) % 1.4), lookAt: ALARM + 0.15 + ((pid * 0.23) % 0.6), turn: ((pid % 3) - 1) * 0.5, stands: pid % 3 !== 1});
    } else people.push({ml});
    pid++;
  }

  // Wachhabender Offizier mit Tisch, rotem Telefon und Schlüsselschalter
  const desk = new THREE.Group(); desk.position.set(2.2, 0, -9); scene.add(desk);
  mesh(new THREE.BoxGeometry(2.6, 0.95, 1.1), deskM, 0, 0.475, 0, desk);
  mesh(new THREE.BoxGeometry(2.6, 0.05, 1.2), dark, 0, 0.97, 0, desk);
  const panelTex = canvasTex(512, 256, (g, w, h) => {
    g.fillStyle = '#2b2f33'; g.fillRect(0, 0, w, h); g.strokeStyle = '#555'; g.lineWidth = 4; g.strokeRect(6, 6, w - 12, h - 12);
    g.fillStyle = '#d9d9d0'; g.font = '600 26px Plex'; g.fillText('MELDUNG AN', 30, 52); g.fillText('FÜHRUNG', 30, 84);
    g.fillStyle = '#e8c547'; for (let i = 0; i < 6; i++) { g.fillRect(260 + i * 34, 30, 22, 8); g.fillRect(260 + i * 34, 30 + 22, 22, 8); }
    g.fillStyle = '#111'; g.fillRect(30, 120, 180, 100); g.fillStyle = '#ccc'; g.font = '500 20px Plex'; g.fillText('SCHLÜSSEL', 50, 150);
  });
  const panel = mesh(new THREE.BoxGeometry(0.9, 0.06, 0.45), new THREE.MeshStandardMaterial({map: panelTex, roughness: 0.6}), -0.3, 1.0, 0.1, desk);
  panel.material = [dark, dark, new THREE.MeshStandardMaterial({map: panelTex, roughness: 0.6}), dark, dark, dark];
  const btn = mesh(new THREE.CylinderGeometry(0.07, 0.08, 0.05, 20), new THREE.MeshStandardMaterial({color: '#7a0d0d', emissive: '#ff1a10', emissiveIntensity: 0.5}), -0.08, 1.05, 0.12, desk);
  const btnLabel = canvasTex(256, 64, (g, w, h) => { g.fillStyle = '#e9e4d8'; g.fillRect(0, 0, w, h); g.fillStyle = '#a00'; g.font = '700 40px Plex'; g.textAlign = 'center'; g.fillText('MELDEN', w / 2, 46); });
  const bl = mesh(new THREE.PlaneGeometry(0.22, 0.055), new THREE.MeshStandardMaterial({map: btnLabel, emissive: '#ffffff', emissiveMap: btnLabel, emissiveIntensity: 0.25}), -0.08, 1.035, 0.27, desk); bl.rotation.x = -Math.PI / 2;
  mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.01, 20), mat('#c9c2a8', {metalness: 0.6}), -0.08, 1.03, 0.12, desk);
  // Schlüssel
  mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.03, 12), mat('#aaa', {metalness: 0.9, roughness: 0.3}), -0.55, 1.045, 0.18, desk);
  mesh(new THREE.BoxGeometry(0.02, 0.05, 0.06), mat('#ccc', {metalness: 0.9, roughness: 0.3}), -0.55, 1.08, 0.18, desk);
  // rotes Telefon
  const ph = new THREE.Group(); ph.position.set(0.7, 1.0, 0.0); desk.add(ph); const red = mat('#9a1010', {roughness: 0.35});
  mesh(new THREE.BoxGeometry(0.34, 0.12, 0.28), red, 0, 0.06, 0, ph).geometry;
  mesh(new THREE.CapsuleGeometry(0.045, 0.3, 4, 10), red, 0, 0.16, 0, ph).rotation.z = Math.PI / 2;
  mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.01, 18), mat('#e6e1d3'), 0, 0.125, 0.06, ph).rotation.x = -0.3;
  // Notizbuch, Tasse
  mesh(new THREE.BoxGeometry(0.3, 0.02, 0.4), mat('#c8bfa4'), 1.05, 1.0, -0.2, desk).rotation.y = 0.2;
  mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.1, 12), mat('#ddd'), -1.0, 1.03, -0.25, desk);
  const officer = makePerson(7, {top: '#3a4334', pants: '#2a2f28', shoe: '#111', hair: '#3a2a1c', height: 1.02});
  officer.position.set(2.15, 0, -8.35); officer.rotation.y = Math.PI; scene.add(officer);
  // Mütze/Schulterstücke weglassen: generisch. Kragen dunkler
  const deskLamp = new THREE.PointLight('#ffd9a0', 2.2, 4, 2); deskLamp.position.set(1.2, 1.6, -9.2); scene.add(deskLamp);

  // Alarmleuchten: rotierende Rundumlichter an der Decke
  const beacons = [];
  for (const [x, z] of [[-8, -15], [8, -15], [-8, -2], [8, -2], [0, -8]]) {
    const g = new THREE.Group(); g.position.set(x, H - 0.55, z); scene.add(g);
    mesh(new THREE.CylinderGeometry(0.22, 0.25, 0.3, 16), new THREE.MeshStandardMaterial({color: '#550000', emissive: '#ff2010', emissiveIntensity: 0, transparent: true, opacity: 0.9}), 0, 0, 0, g);
    const sp = new THREE.SpotLight('#ff2a14', 0, 28, 0.55, 0.5, 1.2); sp.position.set(0, 0, 0); g.add(sp);
    const tgt = new THREE.Object3D(); g.add(tgt); sp.target = tgt;
    beacons.push({g, sp, tgt, cap: g.children[0]});
  }
  const redFill = new THREE.PointLight('#ff2a1a', 0, 40, 1.2); redFill.position.set(0, 5, -6); scene.add(redFill);
  const screenLight = new THREE.PointLight('#5aa8ff', 30, 30, 1.4); screenLight.position.set(0, 3.5, -16.5); scene.add(screenLight);

  // Partikel (Staub im Licht)
  const dust = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({color: '#aab', size: 0.025, transparent: true, opacity: 0.35, depthWrite: false}));
  { const r = rng(9), a = new Float32Array(1500 * 3); for (let i = 0; i < 1500; i++) a.set([(r() - 0.5) * 20, r() * H, -18 + r() * 24], i * 3); dust.geometry.setAttribute('position', new THREE.BufferAttribute(a, 3)); }
  scene.add(dust);

  // --- Bildschirm-Inhalte ---
  const decideLeft = T => Math.max(0, DECIDE_START - Math.max(0, T - ALARM));
  const fmtMS = v => `${Math.floor(v / 60)}:${String(Math.floor(v % 60)).padStart(2, '0')}`;
  function garbage(r, n) { const ch = '0123456789#%&?∑∫∞≠±÷×√π∆'; let s = ''; for (let i = 0; i < n; i++) s += ch[Math.floor(r() * ch.length)]; return s; }
  function glitchify(g, w, h, r, k) { // verschobene Blöcke, Streifen, Rauschen
    if (k <= 0) return;
    for (let i = 0; i < 14 * k; i++) { const y = r() * h, hh = 4 + r() * 40, dx = (r() - 0.5) * 140 * k; g.drawImage(g.canvas, 0, y, w, hh, dx, y, w, hh); }
    for (let i = 0; i < 6 * k; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '120,220,255' : '255,60,80'},${0.15 + r() * 0.3})`; g.fillRect(r() * w, r() * h, 20 + r() * 300, 2 + r() * 10); }
    g.fillStyle = `rgba(0,0,0,${0.18 * k})`; for (let y = 0; y < h; y += 4) g.fillRect(0, y, w, 1.5);
  }
  function drawWall(T) {
    const g = WS.g, w = MW, h = MH, gl = T >= VANISH && T < RETURN, al = T >= ALARM;
    const r = rng(Math.floor(T * 12) * 97 + 3);
    g.drawImage(base, 0, 0);
    if (al) { g.fillStyle = 'rgba(120,0,0,0.35)'; g.fillRect(0, 0, w, h); }
    // Kopfzeile
    g.fillStyle = al ? 'rgba(160,0,0,0.85)' : 'rgba(10,40,60,0.85)'; g.fillRect(0, 0, w, 56);
    g.font = '500 30px Plex'; g.fillStyle = '#e8f4ff'; g.textBaseline = 'middle';
    g.fillText(gl ? 'LAGEBILD · ' + garbage(r, 10) : 'LAGEBILD · FRÜHWARNSYSTEM', 24, 29);
    g.textAlign = 'right'; g.fillText(gl ? garbage(r, 8) + ' UTC' : '10:' + String(23 + Math.floor((T - 53) / 60)).padStart(2, '0') + ':' + String(Math.floor(T * 1) % 60).padStart(2, '0') + ' UTC', w - 24, 29); g.textAlign = 'left';
    // Satelliten-Tracks / Spuren
    g.strokeStyle = 'rgba(120,220,255,0.35)'; g.lineWidth = 2; g.setLineDash([8, 10]);
    for (let k = 0; k < 3; k++) { g.beginPath(); for (let x = 0; x <= w; x += 20) { const y = h * 0.45 + Math.sin(x / w * 6.28 * 1 + k * 2 + T * 0.05) * h * (0.25 + k * 0.08); x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); }
    g.setLineDash([]);
    if (al) {
      const tA = T - ALARM;
      // Abschussorte und Flugbahnen
      LAUNCH.forEach(([la, lo], i) => {
        const [x0, y0] = P(la, lo), [x1, y1] = P(...TARGET[i]); const ti = tA - i * 0.35; if (ti < 0) return;
        const prog = clamp(ti / 9);
        g.strokeStyle = 'rgba(255,60,40,0.95)'; g.lineWidth = 4; g.beginPath();
        for (let s = 0; s <= 40 * prog; s++) { const u = s / 40, x = lerp(x0, x1 + (x1 < x0 ? MW : 0), u), y = lerp(y0, y1, u) - Math.sin(u * Math.PI) * 260; s ? g.lineTo(x % MW, y) : g.moveTo(x, y); }
        g.stroke();
        const bl = Math.sin(T * 10 + i) > 0;
        g.fillStyle = bl ? '#ff3020' : '#ffb0a0'; g.beginPath(); g.arc(x0, y0, 12, 0, 7); g.fill();
        g.strokeStyle = '#ff3020'; g.lineWidth = 3; g.beginPath(); g.arc(x0, y0, 22 + (ti * 30) % 40, 0, 7); g.stroke();
      });
      // Großer Warnkasten
      const blink = Math.sin(T * 7) > -0.2;
      g.fillStyle = blink ? 'rgba(200,0,0,0.92)' : 'rgba(110,0,0,0.92)'; g.fillRect(w * 0.18, h * 0.62, w * 0.64, 190);
      g.strokeStyle = '#ffd0c0'; g.lineWidth = 5; g.strokeRect(w * 0.18 + 8, h * 0.62 + 8, w * 0.64 - 16, 174);
      g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = '700 84px Plex'; g.fillText('RAKETENSTART', w / 2, h * 0.62 + 72);
      g.font = '500 38px Plex'; g.fillText(`${gl ? garbage(r, 1) : '5'} STARTS ERKANNT · ZUVERLÄSSIGKEIT: ${gl ? garbage(r, 3) : 'HOCH'}`, w / 2, h * 0.62 + 145);
      g.textAlign = 'left';
      // Countdown oben rechts
      g.fillStyle = 'rgba(0,0,0,0.6)'; g.fillRect(w - 470, 76, 450, 120);
      g.fillStyle = '#ffd0c0'; g.font = '500 26px Plex'; g.fillText('ENTSCHEIDUNG IN', w - 450, 106);
      g.fillStyle = '#fff'; g.font = '700 64px Plex'; g.fillText(gl ? garbage(r, 4) : fmtMS(decideLeft(T)), w - 450, 162);
    } else {
      // Ruhige Statusliste (zeigt Unsinn, weil nichts mehr rechnet)
      g.fillStyle = 'rgba(0,20,30,0.7)'; g.fillRect(24, 80, 430, 250); g.font = '400 24px Plex'; g.fillStyle = '#8fe0ff';
      const lines = ['SATELLIT OKO-3   ', 'SATELLIT OKO-7   ', 'RADAR NORD       ', 'RADAR WEST       ', 'BAHNDATEN        ', 'PRÜFSUMME        '];
      lines.forEach((l, i) => g.fillText(l + (gl ? garbage(r, 6) : 'OK'), 40, 116 + i * 36));
    }
    glitchify(g, w, h, r, gl ? 0.9 + 0.1 * Math.sin(T * 9) : 0);
    WS.t.needsUpdate = true;
  }
  function drawMon(T) {
    const g = MON.g, w = 256, h = 160, gl = T >= VANISH && T < RETURN, al = T >= ALARM;
    const r = rng(Math.floor(T * 15) * 31 + 7);
    g.fillStyle = al ? (Math.sin(T * 7) > -0.2 ? '#4a0606' : '#200303') : '#04131c'; g.fillRect(0, 0, w, h);
    g.font = '500 15px Plex'; g.textBaseline = 'top';
    for (let i = 0; i < 8; i++) { g.fillStyle = al ? '#ffb4a0' : '#7fd6ff'; g.fillText(gl ? garbage(r, 18) : (al ? (i % 2 ? 'START ERKANNT' : 'BAHN  ' + (40 + i * 7) + '°N') : 'KANAL ' + i + '   OK  ' + (12 + i)), 10, 8 + i * 18); }
    if (al) { g.fillStyle = '#fff'; g.font = '700 26px Plex'; g.fillText('ALARM', 150, 120); }
    glitchify(g, w, h, r, gl ? 1 : 0);
    MON.t.needsUpdate = true;
  }

  const camera = new THREE.PerspectiveCamera(48, 1080 / 1920, 0.05, 100);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, al = T >= ALARM ? 1 : 0, tA = T - ALARM;
    drawWall(T); drawMon(T);
    renderer.toneMappingExposure = 1.25;
    // Alarmlicht
    const pulse = al ? 0.55 + 0.45 * Math.sin(T * 7) : 0;
    beacons.forEach((b, i) => { const a = T * 4.2 + i * 1.3; b.tgt.position.set(Math.cos(a) * 3, -2.2, Math.sin(a) * 3);
      b.sp.intensity = al ? 170 : 0; b.cap.material.emissiveIntensity = al ? 2.5 + 2 * Math.max(0, Math.cos(a * 1.0)) : 0; });
    redFill.intensity = al ? 22 * pulse : 0;
    screenLight.color.set(al ? '#ff4030' : '#5aa8ff'); screenLight.intensity = al ? 30 : 45;
    hemi.color.set(al ? '#8a3a3a' : '#5f7db0'); hemi.intensity = al ? 0.18 : 0.22;
    people.forEach((q, i) => {
      if (q.ml) { q.ml.color.set(al ? '#ff4a3a' : '#6fb7ff'); q.ml.intensity = al ? 1.2 + pulse : 1.2; }
      if (!q.p) return;
      const s = q.stands ? smooth(q.standAt, q.standAt + 0.9, T) : 0;
      const lk = smooth(q.lookAt, q.lookAt + 0.5, T) * q.turn;
      seat(q.p, s, lk + noise1(T * 0.5, i) * 0.04, 0.15);
      q.p.userData.head.rotation.x = -0.15 * smooth(q.lookAt, q.lookAt + 0.6, T); // Blick hoch zur Lagewand
    });
    // Offizier
    const u = officer.userData;
    posePerson(officer, {look: 0});
    if (shot.id === 'decide') {
      // Hand schwebt über dem Knopf, zittert
      const tr = Math.sin(T * 23) * 0.012 + noise1(T * 3, 5) * 0.02;
      u.armR.rotation.x = -1.05 + tr; u.armR.rotation.z = -0.12; u.armR.userData.fore.rotation.x = -0.65 + tr;
      u.armL.rotation.x = -0.5; u.armL.rotation.z = 0.15; u.armL.userData.fore.rotation.x = -0.9;
      u.torso.rotation.x = 0.22; u.head.rotation.x = 0.25 + noise1(T * 0.7, 2) * 0.03; u.head.rotation.y = -0.15 + 0.12 * smooth(84, 87, T);
    } else {
      const k = smooth(ALARM + 0.1, ALARM + 0.8, T);
      u.armL.rotation.x = u.armR.rotation.x = -0.2; u.head.rotation.x = -0.12 * k; u.torso.rotation.y = 0;
      officer.rotation.y = Math.PI + 0.0;
    }
    // Kamera
    if (shot.id === 'bunker') {
      const u2 = smooth(0, 13, t), sh = al ? 0.012 * (1 - clamp(tA / 3)) : 0;
      camera.fov = 48;
      camera.position.set(lerp(-1.2, 0.4, u2) + noise1(T * 6, 1) * sh, lerp(3.2, 2.6, u2) + noise1(T * 6, 3) * sh, lerp(9.5, 2.5, u2));
      camera.lookAt(lerp(0, 0.8, u2), lerp(3.2, 3.1, u2), -19);
    } else {
      const u2 = smooth(0, 12, t);
      camera.fov = lerp(46, 38, u2);
      camera.position.set(lerp(4.6, 3.7, u2) + noise1(T * 0.6, 4) * 0.02, lerp(2.3, 1.95, u2), lerp(-4.4, -6.3, u2));
      camera.lookAt(lerp(1.6, 2.0, u2), lerp(1.6, 1.35, u2), lerp(-11.5, -9.4, u2));
    }
    camera.updateProjectionMatrix();
  }};
}
