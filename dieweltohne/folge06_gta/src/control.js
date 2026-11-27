// Netzleitstelle bei Nacht: Videowand mit Netzkarte, Frequenzanzeige steigt. Zwei Leute an den Pulten (von hinten).
import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
import {lerp, smooth, clamp, rng, noise1, envMap} from './lib.js';
import {carpet, plaster, concrete} from './tex.js';
import {makeHuman} from './mh.js';
import {sit, stand, mouth, blend, hipY} from './poses.js';
import {FREQ0} from './timeline.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const std = (c, o = {}) => new THREE.MeshStandardMaterial({color: c, roughness: 0.8, ...o});
function box(w, h, d, m, x, y, z, p, r = 0) { const o = new THREE.Mesh(r ? new RoundedBoxGeometry(w, h, d, 2, r) : new THREE.BoxGeometry(w, h, d), m); o.position.set(x, y, z); o.castShadow = o.receiveShadow = true; p.add(o); return o; }
const de = (v, k) => v.toFixed(k).replace('.', ',');
export function freqAt(T) { const k = smooth(FREQ0, 38.5, T); return 50 + 0.21 * k * k + (T > FREQ0 ? Math.sin(T * 9) * 0.004 * k : Math.sin(T * 3) * 0.002); }

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#020306');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.03;
  const camera = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.05, 80);
  const R = new THREE.Group(); scene.add(R);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 14), new THREE.MeshStandardMaterial({...carpet('#2a2e36', 51), roughness: 1})); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; R.add(floor);
  const wallM = new THREE.MeshStandardMaterial({...plaster('#3a3f48', 52), roughness: 0.95});
  for (const [w, pos, ry] of [[16, V(0, 2.2, -5.5), 0], [14, V(-8, 2.2, 1.5), Math.PI / 2], [14, V(8, 2.2, 1.5), -Math.PI / 2], [16, V(0, 2.2, 8.5), Math.PI]]) { const o = new THREE.Mesh(new THREE.PlaneGeometry(w, 4.4), wallM); o.position.copy(pos); o.rotation.y = ry; o.receiveShadow = true; R.add(o); }
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(16, 14), std('#1c1f25')); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, 4.4, 1.5); R.add(ceil);
  // Videowand (gebogen, 3 Segmente) mit Leinwand-Textur
  const WC = document.createElement('canvas'); WC.width = 2400; WC.height = 900; const wg = WC.getContext('2d');
  const wtex = new THREE.CanvasTexture(WC); wtex.colorSpace = THREE.SRGBColorSpace; wtex.anisotropy = 8;
  const vw = new THREE.Mesh(new THREE.PlaneGeometry(8, 3), new THREE.MeshBasicMaterial({map: wtex, toneMapped: false, color: new THREE.Color(1.1, 1.1, 1.1)}));
  vw.position.set(0, 2.3, -5.45); R.add(vw);
  box(8.2, 3.2, 0.1, std('#0b0c0e', {roughness: 0.4}), 0, 2.3, -5.52, R, 0);
  // Netz-Knoten der Karte (fest)
  const q = rng(61); const nodes = []; for (let i = 0; i < 60; i++) nodes.push([120 + q() * 1100, 120 + q() * 680]); const edges = []; nodes.forEach((a, i) => { const d = nodes.map((b, j) => [Math.hypot(a[0] - b[0], a[1] - b[1]), j]).sort((x, y) => x[0] - y[0]); edges.push([i, d[1][1]], [i, d[2][1]]); });
  function drawWall(T) {
    const g = wg; g.fillStyle = '#05080f'; g.fillRect(0, 0, 2400, 900);
    const alarm = T > 35.2, blink = alarm && Math.sin(T * 9) > 0;
    // linke Hälfte: Netzkarte
    g.fillStyle = '#0a1426'; g.fillRect(20, 20, 1320, 860);
    g.lineWidth = 3; edges.forEach(([a, b], k) => { const hot = alarm && k % 5 === 0; g.strokeStyle = hot ? (blink ? '#ff3b30' : '#ff9f0a') : '#2f9e6a'; g.beginPath(); g.moveTo(...nodes[a]); g.lineTo(...nodes[b]); g.stroke(); });
    nodes.forEach(([x, y], k) => { g.fillStyle = alarm && k % 7 === 0 ? '#ff3b30' : '#7ee0b0'; g.beginPath(); g.arc(x, y, 7, 0, 7); g.fill(); });
    g.fillStyle = 'rgba(255,255,255,0.7)'; g.font = '500 30px Plex'; g.fillText('ÜBERTRAGUNGSNETZ · ÜBERSICHT', 50, 70);
    // rechte Hälfte: Frequenz groß + Kurve
    const f = freqAt(T);
    g.fillStyle = '#0b0f18'; g.fillRect(1360, 20, 1020, 860);
    g.fillStyle = 'rgba(255,255,255,0.75)'; g.font = '500 34px Plex'; g.fillText('NETZFREQUENZ', 1400, 90);
    g.fillStyle = f > 50.1 ? (blink ? '#ff453a' : '#ffd60a') : '#e8f7ff'; g.font = '500 190px Plex'; g.fillText(de(f, 3), 1400, 300); g.font = '500 70px Plex'; g.fillText('Hz', 2160, 300);
    g.strokeStyle = 'rgba(255,255,255,0.25)'; g.lineWidth = 2; g.strokeRect(1400, 360, 940, 360);
    g.strokeStyle = 'rgba(255,255,255,0.35)'; g.setLineDash([10, 10]); const y50 = 360 + 360 * 0.75; g.beginPath(); g.moveTo(1400, y50); g.lineTo(2340, y50); g.stroke(); g.setLineDash([]);
    g.fillStyle = 'rgba(255,255,255,0.5)'; g.font = '400 26px Plex'; g.fillText('50,000', 1410, y50 - 10); g.fillText('50,200', 1410, 360 + 360 * 0.75 - 0.2 / 0.27 * 360 + 26);
    g.strokeStyle = f > 50.1 ? '#ff9f0a' : '#64d2ff'; g.lineWidth = 5; g.beginPath();
    for (let i = 0; i <= 120; i++) { const tt = T - 6 + i * 0.05; const v = freqAt(tt); const x = 1400 + i / 120 * 940, y = y50 - (v - 50) / 0.27 * 360; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
    if (alarm) { g.fillStyle = blink ? '#ff3b30' : '#8a1a14'; g.fillRect(1400, 760, 940, 90); g.fillStyle = '#fff'; g.font = '500 44px Plex'; g.fillText('ALARM  ÜBERFREQUENZ', 1440, 822); }
    else { g.fillStyle = '#1f6f4a'; g.fillRect(1400, 760, 940, 90); g.fillStyle = '#d9ffe9'; g.font = '500 44px Plex'; g.fillText('STATUS  NORMAL', 1440, 822); }
    wtex.needsUpdate = true;
  }
  const wallLight = new THREE.RectAreaLight('#8fb8ff', 6, 9, 3); wallLight.position.set(0, 2.25, -5.3); wallLight.lookAt(0, 1.2, 4); R.add(wallLight);
  const alarmLight = new THREE.RectAreaLight('#ff3b30', 0, 4, 3); alarmLight.position.set(2.5, 2.25, -5.25); alarmLight.lookAt(2.5, 1.2, 4); R.add(alarmLight);
  // Pulte mit Monitoren (2 Reihen)
  const deskM = std('#262a31', {roughness: 0.6}), topM = std('#3a3f47', {roughness: 0.45});
  const monM = q2 => new THREE.MeshBasicMaterial({map: q2, toneMapped: false, color: new THREE.Color(0.9, 0.9, 0.9)});
  const monTex = (seed) => { const c = document.createElement('canvas'); c.width = 320; c.height = 200; const g = c.getContext('2d'); const r = rng(seed); g.fillStyle = '#071021'; g.fillRect(0, 0, 320, 200); g.strokeStyle = '#3ad08a'; g.lineWidth = 2; g.beginPath(); for (let x = 0; x < 320; x += 8) g.lineTo(x, 120 + Math.sin(x * 0.05 + seed) * 30 + (r() - 0.5) * 10); g.stroke(); g.fillStyle = 'rgba(255,255,255,0.6)'; for (let i = 0; i < 6; i++) g.fillRect(14, 14 + i * 14, 60 + r() * 120, 6); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  const monitors = [];
  for (const [row, z] of [[0, 0.6]]) for (let i = -2; i <= 2; i++) {
    const x = i * 1.55; box(1.5, 0.75, 0.8, deskM, x, 0.375, z, R, 0.01); box(1.55, 0.03, 0.85, topM, x, 0.765, z, R, 0.005);
    for (let m = -1; m <= 1; m++) { const mg = new THREE.Group(); mg.position.set(x + m * 0.48, 0.79, z - 0.25); mg.rotation.y = -m * 0.25; R.add(mg); box(0.46, 0.29, 0.03, std('#0c0d0f'), 0, 0.24, 0, mg, 0.004); const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.27), monM(monTex(row * 20 + i * 3 + m + 10))); scr.position.set(0, 0.24, 0.0155); mg.add(scr); monitors.push(scr); box(0.04, 0.12, 0.04, std('#222'), 0, 0.06, -0.03, mg, 0); }
    const ml = new THREE.RectAreaLight('#7fa8e8', 1.5, 1.4, 0.3); ml.position.set(x, 1.03, z - 0.22); ml.lookAt(x, 1.0, z + 2); R.add(ml);
  }
  // Stühle + zwei Leute
  const chairM = std('#15161a', {roughness: 0.6});
  const chair = (x, z) => { const c = new THREE.Group(); c.position.set(x, 0, z); R.add(c); box(0.5, 0.08, 0.5, chairM, 0, 0.48, 0, c, 0.03); box(0.48, 0.65, 0.07, chairM, 0, 0.88, 0.26, c, 0.03); box(0.05, 0.42, 0.05, std('#333', {metalness: 0.7}), 0, 0.24, 0, c, 0); return c; };
  chair(0.25, 1.25); chair(-0.75, 1.3);
  const op1 = await makeHuman('op1', {top: '#e6e3dc', bottom: '#2a2f3a', shoe: '#222', sneakers: '#1c1c1c', sole: '#1c1c1c', hair: '#141210', skin: 'fair', hairLen: 0.012, seed: 41}); R.add(op1.root);
  const op2 = await makeHuman('op2', {top: '#3c4a6a', bottom: '#2a2a2e', shoe: '#222', sneakers: '#1c1c1c', sole: '#1c1c1c', hair: '#6a4a2a', skin: 'light', hairLen: 0.04, hairDrop: 0.05, seed: 43}); R.add(op2.root);
  // Notleuchte (rotes Drehlicht) über der Tür
  const beacon = new THREE.SpotLight('#ff2a1a', 0, 14, 0.4, 0.5, 1.2); beacon.position.set(5.5, 3.9, 6); R.add(beacon, beacon.target);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0; drawWall(T);
    const alarm = T > 35.2, blink = alarm && Math.sin(T * 9) > 0;
    alarmLight.intensity = alarm ? (blink ? 5 : 1.5) : 0; wallLight.intensity = 5;
    beacon.intensity = alarm ? 60 : 0; beacon.target.position.set(5.5 + Math.cos(T * 6) * 4, 0, 6 + Math.sin(T * 6) * 4);
    // op1 sitzt, beugt sich vor; steht bei 36 auf
    const up = smooth(36.0, 36.7, T);
    op1.root.position.set(0.25, lerp(0.53 - hipY(op1), 0, up), lerp(1.25, 0.95, up)); op1.root.rotation.y = Math.PI;
    blend(op1, () => sit(op1, {lean: 0.12 + smooth(33, 35, T) * 0.15, hands: 'lap', nod: -0.1, knees: 0.15}), () => stand(op1, {lean: 0.2, nod: -0.2, hands: 'hang'}), up);
    op1.look(0, 0.2);
    op2.root.position.set(-0.75, 0.53 - hipY(op2), 1.3); op2.root.rotation.y = Math.PI + 0.25;
    sit(op2, {lean: 0.15, hands: alarm ? 'phone' : 'lap', nod: -0.12, yaw: alarm ? 0.3 : 0, knees: 0.12});
    mouth(op2, alarm ? 0.2 + 0.2 * Math.abs(Math.sin(T * 8)) : 0);
    // Kamera: langsame Fahrt von hinten über die Pulte zur Videowand
    const hh = V(noise1(T * 0.5, 4) * 0.01, noise1(T * 0.5, 6) * 0.01, 0);
    const k = smooth(31, 39, T);
    const pos = V(lerp(0.0, 2.15, k), lerp(1.55, 1.95, k), lerp(3.3, 1.0, k)).add(hh); const look = V(lerp(0.15, 2.15, k), lerp(1.2, 2.45, k), -5.4);
    camera.position.copy(pos); camera.lookAt(look); camera.fov = lerp(50, 44, k); camera.updateProjectionMatrix();
    return {dof: {focus: lerp(2.3, 6.5, smooth(0.35, 0.8, k)), aperture: 0.0008, maxblur: 0.005}, exposure: 1.2, bloom: [0.5, 0.6, 0.75], grain: 0.06, vig: 0.42};
  }};
}
