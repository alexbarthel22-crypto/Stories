// Stadtdetails: Läden mit Schildern, Balkone, Dächer, Straßenmöbel, Skyline, Passanten
import {THREE, mat, mesh, rng, clamp, canvasTex, makePerson, posePerson} from './lib.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

const SHOPS = [['BÄCKEREI', '#7a4b2a'], ['APOTHEKE', '#c8102e'], ['CAFÉ', '#2f4f3f'], ['KIOSK', '#1f3b6e'], ['BLUMEN', '#5d7a2f'], ['FRISEUR', '#3a3a3a'],
  ['DÖNER', '#b5651d'], ['BUCHHANDLUNG', '#5a2d5e'], ['OPTIKER', '#1d5c7a'], ['SPÄTI', '#8a1f3d'], ['BANK', '#1c3d6b'], ['ELEKTRO', '#d0a020'], ['METZGEREI', '#7d1b1b'], ['EISCAFÉ', '#d96aa0']];
const signCache = {};
export const LIT = []; // Schaufenster und Schilder: leuchten nur mit Strom
function signTex(text, color) {
  const k = text + color; if (signCache[k]) return signCache[k];
  return (signCache[k] = canvasTex(512, 96, (g, w, h) => {
    g.fillStyle = color; g.fillRect(0, 0, w, h);
    g.fillStyle = 'rgba(255,255,255,0.12)'; g.fillRect(0, 0, w, 8);
    g.fillStyle = '#f7f3e8'; g.font = '600 54px Plex'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, w / 2, h / 2 + 3);
  }));
}
const shopWinTex = canvasTex(256, 128, (g, w, h) => { // Schaufenster mit Auslage
  const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, '#2b3036'); grd.addColorStop(1, '#4b4336'); g.fillStyle = grd; g.fillRect(0, 0, w, h);
  const r = rng(4); for (let i = 0; i < 40; i++) { g.fillStyle = `hsl(${r() * 360},40%,${40 + r() * 30}%)`; g.fillRect(r() * w, h * 0.55 + r() * h * 0.4, 6 + r() * 18, 6 + r() * 20); }
  g.fillStyle = 'rgba(255,240,210,0.18)'; g.fillRect(0, 0, w, h * 0.5);
  g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 3; g.beginPath(); g.moveTo(20, 10); g.lineTo(90, 70); g.stroke();
});
const posterTex = canvasTex(256, 512, (g, w, h) => { // Litfaßsäule
  g.fillStyle = '#e9e2cf'; g.fillRect(0, 0, w, h); const r = rng(8);
  for (let i = 0; i < 6; i++) { g.fillStyle = ['#d94b3d', '#2f6fb5', '#f2c230', '#2f8f6b', '#222', '#c23b6a'][i]; g.fillRect(8 + (i % 2) * 124, 8 + Math.floor(i / 2) * 168, 116, 160);
    g.fillStyle = 'rgba(255,255,255,0.85)'; g.font = '600 26px Plex'; g.fillText(['KONZERT', 'ZIRKUS', 'SALE', 'KINO', 'THEATER', 'FEST'][i], 18 + (i % 2) * 124, 50 + Math.floor(i / 2) * 168); void r; }
});

// Fassade schmücken: Laden im Erdgeschoss, Balkone, Dach
export function decorateBuilding(scene, s, z, w, h, d, r) {
  const fx = s * 11.5; // Fassadenebene
  const g = new THREE.Group(); scene.add(g);
  const k = SHOPS[Math.floor(r() * SHOPS.length)];
  // Schaufenster, Tür, Schild
  const win = mesh(new THREE.PlaneGeometry(w * 0.62, 2.1), new THREE.MeshStandardMaterial({map: shopWinTex, roughness: 0.08, metalness: 0.3, emissive: '#ffe2b0', emissiveMap: shopWinTex, emissiveIntensity: 0}), fx - s * 0.03, 1.35, z + w * 0.42, g);
  win.rotation.y = -s * Math.PI / 2; win.castShadow = false;
  mesh(new THREE.BoxGeometry(0.12, 2.3, 0.12), mat('#2b2b2b'), fx - s * 0.05, 1.35, z + w * 0.42 - w * 0.31, g);
  const door = mesh(new THREE.PlaneGeometry(1.1, 2.2), mat('#3b2a1e', {roughness: 0.6}), fx - s * 0.03, 1.25, z + w * 0.86, g); door.rotation.y = -s * Math.PI / 2;
  const sign = mesh(new THREE.PlaneGeometry(Math.min(5, w * 0.55), 0.62), new THREE.MeshStandardMaterial({map: signTex(k[0], k[1]), roughness: 0.6, emissive: '#ffffff', emissiveMap: signTex(k[0], k[1]), emissiveIntensity: 0.15}), fx - s * 0.06, 2.85, z + w * 0.42, g);
  sign.rotation.y = -s * Math.PI / 2;
  LIT.push(win.material, sign.material);
  if (r() < 0.6) { // Markise
    const aw = mesh(new THREE.BoxGeometry(1.5, 0.06, w * 0.62), mat(k[1], {roughness: 0.85}), fx - s * 0.75, 2.5, z + w * 0.42, g); aw.rotation.z = s * 0.28;
  }
  // Balkone
  const floors = Math.round(h / 3.3);
  for (let f = 1; f < floors; f++) for (let c = 0; c < Math.round(w / 3); c++) {
    if (r() > 0.35) continue;
    const by = f * (h / floors) - 0.15, bz = z + (c + 0.5) * (w / Math.round(w / 3));
    mesh(new THREE.BoxGeometry(0.9, 0.12, 1.6), mat('#cfc8bb'), fx - s * 0.45, by, bz, g);
    mesh(new THREE.BoxGeometry(0.04, 0.75, 1.6), mat('#2d2f33', {metalness: 0.6}), fx - s * 0.88, by + 0.42, bz, g);
    if (r() < 0.4) mesh(new THREE.SphereGeometry(0.22, 8, 6), mat('#4f7a3a', {flatShading: true}), fx - s * 0.5, by + 0.3, bz + 0.4, g);
  }
  // Dach: Kamine, Antennen
  for (let i = 0; i < 2; i++) if (r() < 0.7) mesh(new THREE.BoxGeometry(0.6, 1.2, 0.6), mat('#8a5a44'), fx + s * (2 + r() * 6), h + 0.6, z + r() * w, g);
  if (r() < 0.5) { const a = mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.2, 5), mat('#444'), fx + s * 3, h + 1.1, z + w / 2, g); a.castShadow = false;
    mesh(new THREE.BoxGeometry(0.05, 0.05, 1.2), mat('#444'), fx + s * 3, h + 1.9, z + w / 2, g); }
  g.traverse(o => { if (o.isMesh) { o.matrixAutoUpdate = false; o.updateMatrix(); } });
}

// Straßenmöbel entlang beider Gehwege
export function addStreetFurniture(scene) {
  const r = rng(31); const dark = mat('#2c2f33', {metalness: 0.5, roughness: 0.5}); const furniture = [];
  const add = (s, z, kind) => {
    const x = s * 7.55; const g = new THREE.Group(); g.position.set(x, 0.15, z); scene.add(g); furniture.push(g);
    if (kind === 0) { // Bank
      mesh(new THREE.BoxGeometry(0.45, 0.06, 1.8), mat('#7a5534', {roughness: 0.7}), 0, 0.45, 0, g);
      mesh(new THREE.BoxGeometry(0.06, 0.45, 1.8), mat('#7a5534'), s * 0.22, 0.7, 0, g);
      for (const dz of [-0.75, 0.75]) mesh(new THREE.BoxGeometry(0.4, 0.45, 0.06), dark, 0, 0.22, dz, g);
    } else if (kind === 1) { // Mülleimer
      mesh(new THREE.CylinderGeometry(0.22, 0.2, 0.8, 12), mat('#e36a1e', {roughness: 0.6}), 0, 0.4, 0, g);
    } else if (kind === 2) { // Fahrradständer mit Rädern
      for (let i = 0; i < 2; i++) {
        const b = new THREE.Group(); b.position.set(0, 0, i * 0.7 - 0.35); g.add(b);
        const col = mat(['#1f6fb2', '#c0392b', '#2d2d2d', '#3a8a5a'][Math.floor(r() * 4)], {metalness: 0.5});
        for (const dx of [-0.5, 0.5]) { const w = mesh(new THREE.TorusGeometry(0.33, 0.025, 6, 20), mat('#111'), dx, 0.35, 0, b); }
        mesh(new THREE.BoxGeometry(1.0, 0.04, 0.04), col, 0, 0.6, 0, b).rotation.z = 0.05;
        mesh(new THREE.BoxGeometry(0.04, 0.5, 0.04), col, 0.1, 0.45, 0, b).rotation.z = -0.3;
        mesh(new THREE.BoxGeometry(0.22, 0.05, 0.1), mat('#222'), 0.05, 0.82, 0, b);
        b.rotation.y = Math.PI / 2;
      }
    } else if (kind === 3) { // Poller
      for (let i = -1; i <= 1; i++) mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.8, 8), dark, 0, 0.4, i * 1.2, g);
    } else if (kind === 4) { // Hydrant
      mesh(new THREE.CylinderGeometry(0.12, 0.14, 0.7, 10), mat('#c8102e'), 0, 0.35, 0, g); mesh(new THREE.SphereGeometry(0.12, 10, 8), mat('#c8102e'), 0, 0.72, 0, g);
    } else if (kind === 5) { // Litfaßsäule
      g.position.x = s * 8.6;
      mesh(new THREE.CylinderGeometry(0.75, 0.75, 3, 20), new THREE.MeshStandardMaterial({map: posterTex, roughness: 0.8}), 0, 1.6, 0, g);
      mesh(new THREE.CylinderGeometry(0.85, 0.8, 0.3, 20), mat('#2d4a3a'), 0, 3.2, 0, g); mesh(new THREE.ConeGeometry(0.7, 0.5, 20), mat('#2d4a3a'), 0, 3.6, 0, g);
    } else if (kind === 6) { // Straßenschild
      mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.8, 6), dark, 0, 1.4, 0, g);
      const t = signTex('BAHNHOFSTR.', '#f2f2f2'); const sm = mesh(new THREE.PlaneGeometry(1.2, 0.25), new THREE.MeshStandardMaterial({map: t}), 0, 2.6, 0, g); sm.rotation.y = Math.PI / 2;
    } else if (kind === 7) { // Blumenkübel
      mesh(new THREE.BoxGeometry(0.8, 0.5, 0.8), mat('#9a9590'), 0, 0.25, 0, g); mesh(new THREE.IcosahedronGeometry(0.42, 0), mat('#5d8a3a', {flatShading: true}), 0, 0.7, 0, g);
    }
    g.traverse(o => { if (o.isMesh) { o.matrixAutoUpdate = false; o.updateMatrix(); } }); g.updateMatrixWorld(true);
  };
  for (let z = -170; z < 170; z += 6) for (const s of [-1, 1]) {
    if (Math.abs(z % 18) < 1.5) continue; // Laternen
    if (s > 0 && z > 24 && z < 36) continue; // Bushaltestelle
    add(s, z + r() * 2, [0, 1, 2, 3, 4, 7, 1, 6][Math.floor(r() * 8)]);
  }
  for (const [s, z] of [[1, -40], [-1, 20], [1, 75], [-1, -90], [1, 140]]) add(s, z, 5);
  // Zebrastreifen
  for (let i = 0; i < 9; i++) { const p = mesh(new THREE.PlaneGeometry(0.6, 3.2), new THREE.MeshStandardMaterial({color: '#ecece6', roughness: 0.5, transparent: true, opacity: 0.9}), -5.6 + i * 1.4, 0.006, -16, scene); p.rotation.x = -Math.PI / 2; p.rotation.z = Math.PI / 2; p.castShadow = false; }
  // Skyline in der Ferne (ohne Nebel, dafür in Dunstfarbe)
  const haze = new THREE.MeshBasicMaterial({color: '#8f99a5', fog: false}), haze2 = new THREE.MeshBasicMaterial({color: '#a3acb6', fog: false});
  for (let i = 0; i < 26; i++) { const hh = 20 + r() * 70; const b = new THREE.Mesh(new THREE.BoxGeometry(14 + r() * 18, hh, 14), i % 2 ? haze : haze2); b.position.set(-130 + i * 10 + r() * 6, hh / 2, -330 - r() * 60); b.renderOrder = -5; scene.add(b); }
  const tower = new THREE.Group(); tower.position.set(55, 0, -420); scene.add(tower);
  const tm = new THREE.MeshBasicMaterial({color: '#8a949f', fog: false});
  for (const [geo, y] of [[new THREE.CylinderGeometry(2.2, 4, 200, 12), 100], [new THREE.SphereGeometry(13, 20, 16), 205], [new THREE.CylinderGeometry(0.8, 1.6, 60, 8), 245]]) {
    const m = new THREE.Mesh(geo, tm); m.position.y = y; tower.add(m);
  }
  return {skyline: [haze, haze2, tm], furniture};
}

// Passanten im Hintergrund
export function makeCrowd(scene, n = 26) {
  const r = rng(77); const walkers = [];
  const umbM = ['#1f3b6e', '#2d2d2d', '#8c2f2f', '#2f6b4f', '#e2b23a'];
  for (let i = 0; i < n; i++) {
    const p = makePerson(200 + i, {}); scene.add(p);
    let umb = null;
    if (r() < 0.45) { umb = new THREE.Group(); mesh(new THREE.ConeGeometry(0.62, 0.28, 10, 1, true), mat(umbM[i % 5], {side: THREE.DoubleSide, roughness: 0.6}), 0, 0, 0, umb); mesh(new THREE.CylinderGeometry(0.01, 0.01, 0.8, 5), mat('#222'), 0, -0.4, 0, umb); scene.add(umb); }
    const s = r() < 0.5 ? -1 : 1;
    walkers.push({p, umb, s, x: s * (8.0 + r() * 2.8), z0: -120 + r() * 240, v: (r() < 0.5 ? -1 : 1) * (1.1 + r() * 0.4), ph: r() * 6, fate: r()});
  }
  return walkers;
}
// mode: 'walk' (vor dem Verschwinden), 'chaos' (danach: manche liegen, andere stehen erschrocken), 'none'
export function updateCrowd(walkers, T, mode, avoid = []) {
  walkers.forEach((w, i) => {
    if (mode === 'none') { w.p.visible = false; if (w.umb) w.umb.visible = false; return; }
    const len = 240; let z = ((w.z0 + 120 + (mode === 'walk' ? T : Math.min(T, 5)) * w.v) % len + len) % len - 120;
    const near = avoid.some(a => Math.hypot(a.x - w.x, a.z - z) < (a.r || 2.5));
    w.p.visible = !near; if (w.umb) w.umb.visible = !near && !(mode === 'chaos' && w.fate < 0.35);
    if (near) return;
    w.p.position.set(w.x, 0.15, z); w.p.rotation.set(0, w.v > 0 ? 0 : Math.PI, 0);
    if (mode === 'walk') posePerson(w.p, {walk: T * 5 + w.ph, holdUp: w.umb ? 0.55 : 0});
    else if (w.fate < 0.35) posePerson(w.p, {fall: 1, slipSide: i % 2 ? 1 : -1});
    else { w.p.rotation.y += Math.sin(i) * 1.2; posePerson(w.p, {walk: 0, walkAmp: 0, look: Math.sin(T * 0.8 + i) * 0.6, holdUp: w.umb ? 0.55 : 0}); }
    if (w.umb && w.umb.visible) { w.umb.position.set(w.x + (w.v > 0 ? 0.25 : -0.25) * 0, 2.05 * w.p.userData.h + 0.15, z); w.umb.rotation.set(0.1, 0, 0); }
    void clamp;
  });
}
