// Stufe 3: Elektromarkt am Abend, lange Schlange am Tresen. Die Disc in der geöffneten Hülle verschwindet,
// dann jede Disc im Laden. Die Schlange drängt nach vorn, ein Regal kippt, der Alarm geht los.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, easeIn, envMap} from './lib.js';
import {RUSH, SHELF_FALL} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const DISC_OFF = 24.8;

function coverTex(seed) {
  const r = rng(seed);
  return canvasTex(128, 160, (g, w, h) => {
    const hue = Math.floor(r() * 360); const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, `hsl(${hue},70%,45%)`); gr.addColorStop(1, `hsl(${(hue + 60) % 360},70%,25%)`);
    g.fillStyle = gr; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(255,255,255,0.15)'; for (let i = 0; i < 5; i++) { g.beginPath(); g.arc(r() * w, r() * h, 10 + r() * 30, 0, 7); g.fill(); }
    g.fillStyle = '#1060d0'; g.fillRect(0, 0, w, 16); g.fillStyle = '#fff'; g.font = '600 10px Plex'; g.fillText('SPIEL', 6, 12);
  });
}
// Launch-Hülle (eigene Gestaltung): Abendküste, darunter „LAUNCH-EDITION“
const LAUNCH = canvasTex(256, 320, (g, w, h) => {
  const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#11203f'); gr.addColorStop(0.6, '#1f8a8a'); gr.addColorStop(1, '#f0b35a'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
  g.fillStyle = '#0b1020'; for (let i = 0; i < 9; i++) g.fillRect(i * 30, 190 - (i % 4) * 26, 24, 140);
  g.fillStyle = '#1060d0'; g.fillRect(0, 0, w, 26); g.fillStyle = '#fff'; g.font = '600 16px Plex'; g.fillText('SPIEL', 10, 19);
  g.font = '600 26px Plex'; g.textAlign = 'center'; g.fillText('LAUNCH-EDITION', w / 2, h - 24);
});

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#1a1d22');
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.add(new THREE.HemisphereLight('#f4f7ff', '#4a4640', 1.1));
  const key = new THREE.DirectionalLight('#ffffff', 1.4); key.position.set(3, 8, 4); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, {left: -8, right: 8, top: 10, bottom: -6, near: 1, far: 30}); key.shadow.bias = -0.0005; key.shadow.normalBias = 0.03; scene.add(key);
  const alarm = new THREE.PointLight('#ff1a1a', 0, 14, 1.4); alarm.position.set(0, 3.2, 9); scene.add(alarm);
  // Boden, Decke mit Leuchtfeldern, Wände
  const floorT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#c9c6bf'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(0,0,0,0.15)'; g.lineWidth = 2; for (let i = 0; i <= 8; i++) { g.beginPath(); g.moveTo(i * 64, 0); g.lineTo(i * 64, h); g.moveTo(0, i * 64); g.lineTo(w, i * 64); g.stroke(); }
    const r = rng(3); for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(0,0,0,${r() * 0.05})`; g.fillRect(r() * w, r() * h, 2, 2); } });
  floorT.wrapS = floorT.wrapT = THREE.RepeatWrapping; floorT.repeat.set(4, 6);
  const fl = mesh(new THREE.PlaneGeometry(10, 22), new THREE.MeshStandardMaterial({map: floorT, roughness: 0.25, metalness: 0.1}), 0, 0, 6, scene); fl.rotation.x = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(10, 22), mat('#e8e8e6'), 0, 3.6, 6, scene).rotation.x = Math.PI / 2;
  const panelM = new THREE.MeshStandardMaterial({color: '#fff', emissive: '#ffffff', emissiveIntensity: 1.6});
  for (let z = -1; z < 17; z += 2.5) for (const x of [-2.5, 0, 2.5]) mesh(new THREE.PlaneGeometry(1.2, 0.6), panelM, x, 3.59, z, scene).rotation.x = Math.PI / 2;
  const wallM = mat('#d9dce0', {roughness: 0.9});
  mesh(new THREE.BoxGeometry(10, 3.6, 0.1), wallM, 0, 1.8, -2.2, scene);
  for (const x of [-5, 5]) mesh(new THREE.BoxGeometry(0.1, 3.6, 22), wallM, x, 1.8, 6, scene);
  // Eingang hinten: Glasfront mit Nacht, Sicherungsschleusen
  mesh(new THREE.PlaneGeometry(10, 3.6), new THREE.MeshBasicMaterial({color: '#0d1426'}), 0, 1.8, 16.9, scene).rotation.y = Math.PI;
  for (const x of [-1.2, 1.2]) mesh(new THREE.BoxGeometry(0.08, 1.6, 0.5), new THREE.MeshStandardMaterial({color: '#ccc', transparent: true, opacity: 0.5}), x, 0.8, 14.5, scene);
  const beacon = mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.2, 14), new THREE.MeshStandardMaterial({color: '#600', emissive: '#ff0000', emissiveIntensity: 0}), 0, 3.4, 9, scene);
  // Werbebanner über dem Tresen
  const banner = canvasTex(1024, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, 0); gr.addColorStop(0, '#d41f3a'); gr.addColorStop(1, '#7a1ad4'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.fillStyle = '#fff'; g.font = '600 92px Plex'; g.textAlign = 'center'; g.fillText('JETZT ERHÄLTLICH', w / 2, 120); g.font = '500 54px Plex'; g.fillText('LAUNCH-EDITION · 79,99 €', w / 2, 200); });
  mesh(new THREE.PlaneGeometry(4.4, 1.1), new THREE.MeshStandardMaterial({map: banner, emissive: '#fff', emissiveMap: banner, emissiveIntensity: 0.4}), 0, 2.75, -2.14, scene);
  // Tresen mit Kasse
  const counter = new THREE.Group(); scene.add(counter);
  mesh(new RoundedBoxGeometry(3.4, 1.0, 0.75, 2, 0.03), mat('#2c3e66', {roughness: 0.5}), 0, 0.5, 0, counter);
  mesh(new RoundedBoxGeometry(3.5, 0.05, 0.85, 2, 0.02), mat('#efefef', {roughness: 0.3}), 0, 1.02, 0, counter);
  const scr = mesh(new THREE.BoxGeometry(0.4, 0.28, 0.03), mat('#111'), -1.0, 1.32, -0.15, counter); scr.rotation.y = Math.PI + 0.3;
  mesh(new THREE.BoxGeometry(0.1, 0.18, 0.06), mat('#222'), 0.6, 1.12, 0.1, counter);
  // Stapel Launch-Hüllen
  const caseGeo = new THREE.BoxGeometry(0.135, 0.17, 0.015);
  const launchM = [mat('#111'), mat('#111'), mat('#111'), mat('#111'), new THREE.MeshStandardMaterial({map: LAUNCH, roughness: 0.4}), mat('#111')];
  for (let i = 0; i < 9; i++) { const c = mesh(caseGeo, launchM, 1.1 + (i % 3) * 0.16, 1.05 + Math.floor(i / 3) * 0.016, -0.1, counter); c.rotation.x = -Math.PI / 2; c.rotation.z = (i % 2) * 0.08; }
  // Geöffnete Hülle mit Disc vorn am Tresen
  const open = new THREE.Group(); open.position.set(0.05, 1.06, 0.12); scene.add(open);
  mesh(new THREE.BoxGeometry(0.135, 0.006, 0.17), mat('#121316', {roughness: 0.4}), -0.07, 0, 0, open);
  const inner = mesh(new THREE.BoxGeometry(0.135, 0.006, 0.17), mat('#121316', {roughness: 0.4}), 0.07, 0, 0, open);
  const hub = mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.008, 16), mat('#333'), 0.07, 0.006, 0, open); void hub; void inner;
  const cov = mesh(new THREE.PlaneGeometry(0.13, 0.165), new THREE.MeshStandardMaterial({map: LAUNCH, roughness: 0.4}), -0.07, 0.004, 0, open); cov.rotation.x = -Math.PI / 2; cov.rotation.z = Math.PI;
  const discT = canvasTex(256, 256, (g, w, h) => { const cg = g.createConicGradient ? g.createConicGradient(0, 128, 128) : null; if (cg) { ['#e0e6ef', '#f9c9ff', '#c9f1ff', '#fff2c4', '#e0e6ef'].forEach((c, i) => cg.addColorStop(i / 4, c)); g.fillStyle = cg; } else g.fillStyle = '#ddd';
    g.beginPath(); g.arc(128, 128, 126, 0, 7); g.fill(); g.fillStyle = '#9aa0a8'; g.beginPath(); g.arc(128, 128, 30, 0, 7); g.fill(); g.fillStyle = '#121316'; g.beginPath(); g.arc(128, 128, 14, 0, 7); g.fill(); });
  const disc = mesh(new THREE.CircleGeometry(0.06, 48), new THREE.MeshStandardMaterial({map: discT, metalness: 0.9, roughness: 0.15, transparent: true}), 0.07, 0.01, 0, open); disc.rotation.x = -Math.PI / 2;
  const sparkle = mesh(new THREE.CircleGeometry(0.07, 32), new THREE.MeshBasicMaterial({color: '#bfe8ff', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false}), 0.07, 0.012, 0, open); sparkle.rotation.x = -Math.PI / 2;
  // Regale links und rechts mit Spielehüllen; das rechte vordere Regal kippt
  const shelves = [];
  const makeShelf = (x, z, side, seed) => {
    const sh = new THREE.Group(); sh.position.set(x, 0, z); scene.add(sh); const r = rng(seed);
    mesh(new THREE.BoxGeometry(0.5, 2.1, 2.4), mat('#e6e6e6', {roughness: 0.6}), -side * 0.2, 1.05, 0, sh);
    for (let k = 0; k < 5; k++) { mesh(new THREE.BoxGeometry(0.5, 0.03, 2.4), mat('#bfc3c8', {metalness: 0.4}), side * 0.08, 0.35 + k * 0.4, 0, sh);
      for (let i = 0; i < 15; i++) { const cv = coverTex(seed * 100 + k * 20 + i); const box = mesh(caseGeo, [mat('#111'), mat('#111'), mat('#111'), mat('#111'), new THREE.MeshStandardMaterial({map: cv, roughness: 0.5}), mat('#111')], side * 0.12, 0.45 + k * 0.4, -1.1 + i * 0.155, sh);
        box.rotation.y = side * Math.PI / 2; box.rotation.x = (r() - 0.5) * 0.06; } }
    const top = canvasTex(512, 96, (g, w, h) => { g.fillStyle = '#1060d0'; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.font = '600 52px Plex'; g.textAlign = 'center'; g.fillText(['KONSOLEN', 'NEUHEITEN', 'ACTION', 'ZUBEHÖR'][seed % 4], w / 2, 66); });
    const t = mesh(new THREE.PlaneGeometry(2.0, 0.38), new THREE.MeshStandardMaterial({map: top, emissive: '#fff', emissiveMap: top, emissiveIntensity: 0.3}), side * 0.06, 2.35, 0, sh); t.rotation.y = side * Math.PI / 2;
    shelves.push(sh); return sh;
  };
  makeShelf(-3.9, 3.5, 1, 1); makeShelf(-3.9, 7.0, 1, 2); makeShelf(-3.9, 10.5, 1, 3);
  const fallShelf = makeShelf(3.9, 4.6, -1, 4); makeShelf(3.9, 9.5, -1, 6);
  // Fallende Hüllen (aus dem kippenden Regal)
  const loose = []; { const r = rng(9); for (let i = 0; i < 26; i++) { const b = mesh(caseGeo, [mat('#111'), mat('#111'), mat('#111'), mat('#111'), new THREE.MeshStandardMaterial({map: coverTex(500 + i)}), mat('#111')], 0, -5, 0, scene);
    loose.push({b, x: 3.4 - r() * 2.4, z: 3.4 + r() * 2.4, y0: 0.5 + r() * 1.6, d: r() * 0.3, rx: r() * 6, ry: r() * 6}); } }

  // Personal hinter dem Tresen, Kundschlange
  const cashier = makePerson(9, {top: '#d41f3a', pants: '#222'}); cashier.position.set(0.3, 0, -0.75); scene.add(cashier);
  const Q = []; { const r = rng(4); let z = 0.75; for (let i = 0; i < 18; i++) { const p = makePerson(60 + i, {}); scene.add(p); const x = (i % 2 ? 0.25 : -0.2) + (r() - 0.5) * 0.25; Q.push({p, x, z, ph: r() * 6, tx: (r() - 0.5) * 3.2, tz: 0.65 + r() * 1.8, sp: 2 + r() * 1.5, d: r() * 0.4}); z += 0.65 + r() * 0.25; } }
  // Kunde vorne: Hände über der Hülle
  const handM = mat('#d9a47e', {roughness: 0.6});
  void handM;

  const camera = new THREE.PerspectiveCamera(44, 1080 / 1920, 0.03, 200); scene.add(camera);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    // Disc verschwindet
    const dk = smooth(DISC_OFF, DISC_OFF + 0.35, T); disc.material.opacity = 1 - dk; disc.scale.setScalar(1 - 0.2 * dk); disc.visible = dk < 0.999;
    sparkle.material.opacity = Math.sin(dk * Math.PI) * 0.8;
    // Kunden
    Q.forEach((q, i) => { const p = q.p, run = T > RUSH + q.d;
      if (!run) { p.position.set(q.x, 0, q.z); p.rotation.set(0, Math.PI + Math.sin(T * 0.4 + i) * 0.15, 0); posePerson(p, {walk: 0, walkAmp: 0, look: Math.sin(T * 0.7 + q.ph) * 0.3, holdUp: i > 0 && i % 4 === 1 && T > DISC_OFF + 0.6 + i * 0.08 ? 0.5 : 0}); return; }
      const d = T - RUSH - q.d, k = clamp(d * q.sp / Math.max(0.2, Math.hypot(q.x - q.tx, q.z - q.tz)));
      const x = lerp(q.x, q.tx, easeIn(Math.min(1, k * 1.2)) * 0.4 + k * 0.6), z = lerp(q.z, q.tz, k);
      p.position.set(x, 0, z); p.rotation.set(0, Math.PI + Math.atan2(q.tx - q.x, -(q.tz - q.z)) * 0.3, 0);
      posePerson(p, {walk: T * 11 + q.ph, walkAmp: k < 1 ? 1.2 : 0.2, holdUp: k >= 1 && i % 3 !== 2 ? 0.75 + 0.2 * Math.sin(T * 6 + i) : 0}); });
    cashier.rotation.set(0, 0, 0); posePerson(cashier, {look: Math.sin(T) * 0.2, armsUp: T > RUSH + 0.3 ? 0.6 : 0});
    if (T > SHELF_FALL + 0.4) { const k = smooth(SHELF_FALL + 0.4, SHELF_FALL + 1.0, T); cashier.position.y = -0.6 * k; } else cashier.position.y = 0;
    // Regal kippt um die linke Unterkante in den Gang
    const fk = T > SHELF_FALL ? Math.min(1, Math.pow((T - SHELF_FALL) / 0.9, 2)) : 0; fallShelf.rotation.z = fk * 1.35; fallShelf.position.x = 3.9 - fk * 0.4;
    loose.forEach((l, i) => { const d = T - SHELF_FALL - 0.25 - l.d; if (d < 0) { l.b.position.y = -5; return; }
      const y = Math.max(0.01, l.y0 - 4.9 * d * d); l.b.position.set(l.x - d * 0.8, y, l.z + (i % 3 - 1) * d * 0.3); l.b.rotation.set(l.rx + (y > 0.02 ? d * 6 : 0), l.ry, 0); if (y <= 0.02) l.b.rotation.x = Math.PI / 2; });
    // Alarm
    const al = T > RUSH + 0.2 ? (Math.sin(T * 9) > 0 ? 1 : 0.15) : 0; alarm.intensity = al * 30; beacon.material.emissiveIntensity = al * 4;
    // Hände des vorderen Kunden: zucken zurück
    // Kamera: Nahaufnahme der Hülle, dann Zug nach oben/hinten über den Tresen
    const pull = smooth(26.6, 28.4, T), sh = T > SHELF_FALL + 0.8 && T < SHELF_FALL + 1.4 ? 0.02 : 0.003;
    const near = V3(0.28, 1.62, -0.42), far = V3(-0.7, 2.6, -1.7);
    camera.position.lerpVectors(near, far, pull); camera.position.x += noise1(T * 3, 4) * sh; camera.position.y += noise1(T * 3, 7) * sh;
    const ln = V3(0.05, 1.05, 0.25), lf = V3(2.2, 0.95, 5.2); camera.lookAt(new THREE.Vector3().lerpVectors(ln, lf, pull));
    camera.fov = lerp(40, 52, pull); camera.updateProjectionMatrix();
  }};
}
