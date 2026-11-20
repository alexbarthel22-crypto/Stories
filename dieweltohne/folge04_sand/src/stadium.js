// Fußballstadion, 87. Minute: Glas und Chips sind seit T=10 weg (Videowand und Banden tot).
// Bei STAND_FALL zerbröselt der Beton der Tribünen – Ränge sacken ab, Staub, das Stahldach hängt durch, ein Flutlichtmast kippt.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson} from './lib.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {particles, updateParticles} from './fx.js';
import {STAND_FALL} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const MAST_T = 34.3, MAST_HIT = 36.55; // Flutlichtmast kippt, schlägt auf

export async function build(renderer) {
  const scene = new THREE.Scene();
  // Himmel
  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 32, 16), new THREE.ShaderMaterial({side: THREE.BackSide, depthWrite: false, fog: false,
    vertexShader: 'varying vec3 p; void main(){ p = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }',
    fragmentShader: 'varying vec3 p; void main(){ float h = clamp(p.y, 0., 1.); vec3 c = mix(vec3(0.78,0.86,0.95), vec3(0.30,0.52,0.86), pow(h, 0.6)); gl_FragColor = vec4(c, 1.); }'}));
  sky.renderOrder = -10; scene.add(sky);
  scene.fog = new THREE.Fog('#c9d6e4', 160, 700);
  scene.add(new THREE.HemisphereLight('#d6e6f8', '#6a6050', 0.85));
  const sun = new THREE.DirectionalLight('#fff2da', 2.6); sun.position.set(-70, 95, -60); sun.target.position.set(0, 0, -30);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -110, right: 110, top: 110, bottom: -110, near: 10, far: 400}); sun.shadow.bias = -0.0006; sun.shadow.normalBias = 0.05;
  scene.add(sun, sun.target);
  { const e = new THREE.Scene(); e.background = new THREE.Color('#a9c2dc'); const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(e, 0.02).texture; scene.environmentIntensity = 0.5; }

  // Rasen mit Streifen und Linien
  const pitchT = canvasTex(2048, 1400, (g, w, h) => {
    const mx = 150, my = 130; // Rand (Spielfeld 105 x 68 in der Mitte)
    for (let i = 0; i < 18; i++) { g.fillStyle = i % 2 ? '#3a7a35' : '#43873b'; g.fillRect(i * w / 18, 0, w / 18 + 1, h); }
    const r = rng(3); for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '20,60,20' : '120,170,90'},${r() * 0.08})`; g.fillRect(r() * w, r() * h, 3, 3); }
    const X = x => mx + x / 105 * (w - 2 * mx), Y = y => my + y / 68 * (h - 2 * my), S = (w - 2 * mx) / 105;
    g.strokeStyle = 'rgba(250,250,245,0.92)'; g.lineWidth = 5;
    g.strokeRect(X(0), Y(0), X(105) - X(0), Y(68) - Y(0));
    g.beginPath(); g.moveTo(X(52.5), Y(0)); g.lineTo(X(52.5), Y(68)); g.stroke();
    g.beginPath(); g.arc(X(52.5), Y(34), 9.15 * S, 0, 7); g.stroke();
    for (const [a, s] of [[0, 1], [105, -1]]) { g.strokeRect(Math.min(X(a), X(a + s * 16.5)), Y(13.85), 16.5 * S, 40.3 * S); g.strokeRect(Math.min(X(a), X(a + s * 5.5)), Y(24.85), 5.5 * S, 18.3 * S);
      g.beginPath(); g.arc(X(a + s * 11), Y(34), 9.15 * S, s > 0 ? -0.93 : Math.PI - 0.93, s > 0 ? 0.93 : Math.PI + 0.93); g.stroke(); }
  });
  const pitch = mesh(new THREE.PlaneGeometry(105 * 2048 / (2048 - 300), 68 * 1400 / (1400 - 260)), new THREE.MeshStandardMaterial({map: pitchT, roughness: 0.95}), 0, 0, 0, scene);
  pitch.rotation.x = -Math.PI / 2; pitch.receiveShadow = true; pitch.castShadow = false;
  const apron = mesh(new THREE.PlaneGeometry(1400, 1400), mat('#6d6a62', {roughness: 1}), 0, -0.02, 0, scene); apron.rotation.x = -Math.PI / 2; apron.receiveShadow = true;
  // Tore
  const white = mat('#f4f4f2', {roughness: 0.4});
  for (const s of [-1, 1]) { const g = new THREE.Group(); g.position.set(s * 52.5, 0, 0); scene.add(g);
    for (const z of [-3.66, 3.66]) mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.44, 8), white, 0, 1.22, z, g);
    mesh(new THREE.CylinderGeometry(0.06, 0.06, 7.32, 8), white, 0, 2.44, 0, g).rotation.x = Math.PI / 2;
    const net = mesh(new THREE.BoxGeometry(2, 2.44, 7.32), new THREE.MeshStandardMaterial({color: '#ffffff', transparent: true, opacity: 0.18, depthWrite: false}), s * 1, 1.22, 0, g); net.castShadow = false; }

  // ---------- Tribünen aus Beton ----------
  const concrete = new THREE.MeshStandardMaterial({color: '#b9b3a8', roughness: 0.92});
  const concreteDark = mat('#8f8a80', {roughness: 0.95});
  const fanGeo = (() => { const b = new THREE.BoxGeometry(0.44, 0.62, 0.3); b.translate(0, 0.31, 0); const h = new THREE.BoxGeometry(0.22, 0.24, 0.22); h.translate(0, 0.76, 0);
    const a = new THREE.BoxGeometry(0.1, 0.4, 0.1); a.translate(0.2, 0.85, 0); return mergeGeometries([b, h, a]); })();
  const timeU = {value: 0}, jumpU = {value: 1};
  const fanM = new THREE.MeshStandardMaterial({roughness: 0.8});
  fanM.onBeforeCompile = sh => { sh.uniforms.time = timeU; sh.uniforms.jump = jumpU;
    sh.vertexShader = 'uniform float time; uniform float jump;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\n  float ph = float(gl_InstanceID) * 1.37; transformed.y += jump * max(0.0, sin(time * 6.5 + ph)) * 0.14;'); };
  const pieces = []; // Tribünenstücke, die einzeln einstürzen
  const r = rng(17);
  // Ein Rang-Stück: Stufenplatte, Stützen, Fans. Lokal: Vorderkante entlang x bei z=0, Ränge steigen nach -z.
  function tierPiece(parent, x0, width, {rows, d, rise, h0, upper, home}) {
    const g = new THREE.Group(); g.position.x = x0 + width / 2; parent.add(g);
    const sh = new THREE.Shape(); sh.moveTo(0, h0 - 1.3); sh.lineTo(0, h0);
    for (let i = 0; i < rows; i++) { sh.lineTo(i * d + d, h0 + i * rise); sh.lineTo(i * d + d, h0 + (i + 1) * rise); }
    const D = rows * d, Y = h0 + rows * rise; sh.lineTo(D, Y - 1.4); sh.lineTo(0, h0 - 1.3);
    const geo = new THREE.ExtrudeGeometry(sh, {depth: width - 0.12, bevelEnabled: false}); geo.rotateY(Math.PI / 2); geo.translate(-width / 2 + 0.06, 0, 0);
    // rotateY(+90°): Profil-x -> -z? (x' = z, z' = -x): Profil nach hinten = -z
    const slab = new THREE.Mesh(geo, concrete); slab.castShadow = slab.receiveShadow = true; g.add(slab);
    // Front- und Seitenwand, Mundloch (Aufgang) dunkel
    mesh(new THREE.BoxGeometry(width - 0.1, h0 - 1.3 + 0.1, 0.4), concreteDark, 0, (h0 - 1.3) / 2, -0.2, g);
    if (!upper && r() < 0.5) mesh(new THREE.BoxGeometry(2.2, 2.2, 0.2), mat('#1b1b1d'), (r() - 0.5) * (width - 3), h0 + 3 * rise + 1.1, -(3 * d + 0.12), g);
    // Stützen unter der Platte
    for (const u of [0.35, 0.7, 0.98]) { const zz = -u * D, yy = h0 + u * rows * rise - 1.4; for (const xx of [-width / 2 + 0.6, width / 2 - 0.6]) { const c = mesh(new THREE.BoxGeometry(0.7, Math.max(0.5, yy), 0.7), concreteDark, xx, Math.max(0.5, yy) / 2, zz, g); c.castShadow = true; } }
    // Fans
    const per = Math.floor((width - 0.4) / 0.56), fans = new THREE.InstancedMesh(fanGeo, fanM, rows * per); let n = 0;
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), col = new THREE.Color();
    for (let i = 0; i < rows; i++) for (let k = 0; k < per; k++) {
      if (r() < 0.04) continue;
      const x = -width / 2 + 0.3 + k * 0.56 + (r() - 0.5) * 0.1, y = h0 + i * rise, z = -(i * d + d * 0.55);
      q.setFromEuler(new THREE.Euler(0, (r() - 0.5) * 0.4, (r() - 0.5) * 0.1)); m4.compose(V3(x, y, z), q, V3(1, 0.9 + r() * 0.2, 1)); fans.setMatrixAt(n, m4);
      const v = r(); col.set(home === 'away' ? (v < 0.65 ? '#1f4fb8' : v < 0.85 ? '#f2f2f2' : '#23262b') : (v < 0.5 ? '#d1202c' : v < 0.78 ? '#f4f4f0' : v < 0.9 ? '#2a2c31' : '#e2b23a'));
      fans.setColorAt(n++, col);
    }
    fans.count = n; fans.castShadow = true; fans.instanceColor.needsUpdate = true; g.add(fans);
    const p = {g, slab, D, Y, h0, width, upper, tf: 0}; pieces.push(p); return p;
  }
  // Haupttribüne (gegenüber der Kamera) – Unterrang und Oberrang, 24 Stücke à 5 m
  const main = new THREE.Group(); main.position.set(0, 0, -37); scene.add(main);
  const lowerCfg = {rows: 22, d: 0.8, rise: 0.42, h0: 2.2, upper: false}, upperCfg = {rows: 22, d: 0.85, rise: 0.62, h0: 0, upper: true};
  const upperG = new THREE.Group(); upperG.position.set(0, 15.5, -20.5); main.add(upperG);
  for (let i = 0; i < 24; i++) { const x0 = -60 + i * 5, away = i >= 20 ? 'away' : 'home';
    const a = tierPiece(main, x0, 5, {...lowerCfg, home: away}); a.idx = i;
    const b = tierPiece(upperG, x0, 5, {...upperCfg, home: away}); b.idx = i; }
  // Rückwand zwischen den Rängen (Logen, ohne Glas: leere Öffnungen) und Rückseite
  for (let i = 0; i < 24; i++) { const x0 = -60 + i * 5;
    const w = mesh(new THREE.BoxGeometry(5, 4.2, 1.0), concrete, x0 + 2.5, 13.3, -37 - 18.2, scene); w.castShadow = true;
    mesh(new THREE.BoxGeometry(3.6, 1.8, 1.05), mat('#202124'), x0 + 2.5, 13.6, -37 - 18.15, scene); }
  // Umlauf hinter dem Unterrang (dunkel, schließt die Lücke zum Himmel)
  mesh(new THREE.BoxGeometry(124, 16, 2), mat('#4a4741', {roughness: 1}), 0, 8, -37 - 19.5, scene).receiveShadow = true;
  mesh(new THREE.BoxGeometry(124, 0.4, 20), mat('#55524b'), 0, 0.2, -47, scene);
  // Seitentribüne links (hinter dem Tor), 10 Stücke
  const left = new THREE.Group(); left.position.set(-58, 0, 0); left.rotation.y = Math.PI / 2; scene.add(left);
  for (let i = 0; i < 12; i++) { const p = tierPiece(left, -30 + i * 5, 5, {rows: 26, d: 0.8, rise: 0.5, h0: 2.2, upper: false, home: 'home'}); p.idx = i; p.side = true; }
  // Choreo-Banner auf dem Oberrang
  const choreoT = canvasTex(1024, 512, (g, w, h) => { g.fillStyle = '#c8102e'; g.fillRect(0, 0, w, h); g.fillStyle = '#f5f5f0';
    for (let i = 0; i < 9; i++) { g.save(); g.translate(i * w / 8 - 60, 0); g.rotate(0.35); g.fillRect(0, -100, 40, h + 300); g.restore(); }
    g.fillStyle = '#f5f5f0'; g.font = '700 92px Plex'; g.textAlign = 'center'; g.fillText('UNSERE STADT', w / 2, 200); g.fillText('UNSER VEREIN', w / 2, 330);
    g.strokeStyle = '#111'; g.lineWidth = 10; g.strokeRect(10, 10, w - 20, h - 20); });
  const choreo = [];
  for (let i = 0; i < 6; i++) { const pc = pieces.find(p => p.upper && p.idx === 9 + i);
    const tex = choreoT.clone(); tex.needsUpdate = true; tex.repeat.set(1 / 6, 1); tex.offset.set(i / 6, 0);
    const len = Math.hypot(22 * 0.85, 22 * 0.62); const pl = new THREE.Mesh(new THREE.PlaneGeometry(5, len), new THREE.MeshStandardMaterial({map: tex, roughness: 0.8, side: THREE.DoubleSide}));
    pl.position.set(0, 22 * 0.62 / 2 + 1.25, -22 * 0.85 / 2); pl.rotation.x = -Math.atan2(22 * 0.62, 22 * 0.85) + Math.PI / 2 - Math.PI / 2; pl.rotation.x = -(Math.PI / 2 - Math.atan2(22 * 0.62, 22 * 0.85));
    pc.g.add(pl); choreo.push(pl); }
  // Dach auf Stahlfachwerk (Stahl hat keinen Sand – bleibt, hängt aber durch)
  const steel = mat('#d4d7db', {metalness: 0.7, roughness: 0.4});
  const roof = new THREE.Group(); roof.position.set(0, 47, -37 - 52); main.parent.add(roof); // Drehpunkt hinten oben
  for (let x = -60; x <= 60; x += 7.5) {
    const tr = new THREE.Group(); tr.position.x = x; roof.add(tr);
    const L = 56; const top = mesh(new THREE.BoxGeometry(0.45, 0.45, L), steel, 0, 1.5, L / 2, tr); top.rotation.x = 0.06; top.castShadow = true;
    const bot = mesh(new THREE.BoxGeometry(0.35, 0.35, L * 0.75), steel, 0, -2.2, L * 0.75 / 2, tr); bot.castShadow = true;
    for (let k = 0; k < 9; k++) { const zz = k * L * 0.75 / 8; const v = mesh(new THREE.BoxGeometry(0.2, 3.9 - zz * 0.05, 0.2), steel, 0, -0.3, zz, tr); const dg = mesh(new THREE.BoxGeometry(0.16, 5, 0.16), steel, 0, -0.3, zz + 2.6, tr); dg.rotation.x = 0.85; }
  }
  const roofSheet = mesh(new THREE.BoxGeometry(124, 0.3, 54), new THREE.MeshStandardMaterial({color: '#eef0f2', roughness: 0.6, metalness: 0.2, side: THREE.DoubleSide}), 0, 2.0, 27, roof); roofSheet.rotation.x = 0.06; roofSheet.castShadow = true;
  // Stahlstützen hinten
  for (let x = -60; x <= 60; x += 15) mesh(new THREE.BoxGeometry(1.0, 47, 1.0), steel, x, 23.5, -37 - 52, scene).castShadow = true;
  // Flutlichtmast (Stahl auf Betonfundament)
  const mast = new THREE.Group(); mast.position.set(-50, 0, -60); scene.add(mast);
  const mastH = 58; for (const [a, b] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const l = mesh(new THREE.BoxGeometry(0.35, mastH, 0.35), steel, a * 1.1, mastH / 2, b * 1.1, mast); l.rotation.z = -a * 0.012; l.rotation.x = b * 0.012; l.castShadow = true; }
  for (let y = 3; y < mastH; y += 3.2) { const c = mesh(new THREE.BoxGeometry(2.6, 0.12, 0.12), steel, 0, y, 1.1, mast); c.rotation.z = 0.8; const c2 = mesh(new THREE.BoxGeometry(0.12, 0.12, 2.6), steel, 1.1, y, 0, mast); c2.rotation.x = 0.8; }
  const bank = new THREE.Group(); bank.position.set(0, mastH + 2, 0.6); bank.rotation.x = 0.35; mast.add(bank);
  mesh(new THREE.BoxGeometry(9, 5.2, 0.6), mat('#3a3d42', {metalness: 0.6}), 0, 0, 0, bank);
  for (let i = 0; i < 24; i++) mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.25, 12), mat('#c9ccd0', {metalness: 0.8, roughness: 0.2}), -3.6 + (i % 6) * 1.45, -1.9 + Math.floor(i / 6) * 1.25, 0.35, bank).rotation.x = Math.PI / 2;
  mesh(new THREE.BoxGeometry(4, 1.4, 4), concrete, -50, 0.5, -60, scene);
  // Videowand (Glas/Chips weg: schwarz, Rahmen leer) und LED-Banden (tot)
  const screen = new THREE.Group(); screen.position.set(-34, 0, -18); screen.rotation.y = 0.9; scene.add(screen);
  for (const xx of [-6, 6]) mesh(new THREE.BoxGeometry(0.8, 26, 0.8), steel, xx, 13, 0, screen);
  mesh(new THREE.BoxGeometry(16, 9, 1.2), mat('#2c2e33', {metalness: 0.5}), 0, 26, 0, screen);
  const dead = canvasTex(512, 288, (g, w, h) => { g.fillStyle = '#060607'; g.fillRect(0, 0, w, h); const q = rng(4);
    for (let i = 0; i < 260; i++) { g.fillStyle = `rgba(${90 + q() * 60},${80 + q() * 50},${60 + q() * 40},${0.25 + q() * 0.4})`; g.fillRect(q() * w, q() * h, 2 + q() * 10, 1 + q() * 3); } // nackte Platinenreste
    g.strokeStyle = 'rgba(160,160,165,0.6)'; g.lineWidth = 3; for (let x = 0; x < w; x += 64) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); } for (let y = 0; y < h; y += 72) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); } });
  mesh(new THREE.PlaneGeometry(15, 8.2), new THREE.MeshStandardMaterial({map: dead, roughness: 0.9}), 0, 26, 0.62, screen);
  const boards = new THREE.Group(); scene.add(boards);
  for (let x = -55; x < 55; x += 6) { const b = mesh(new THREE.BoxGeometry(5.9, 0.95, 0.3), mat('#121315', {roughness: 0.6}), x + 3, 0.5, -35.6, boards); b.castShadow = true;
    mesh(new THREE.PlaneGeometry(5.6, 0.75), new THREE.MeshStandardMaterial({map: dead, roughness: 0.9}), x + 3, 0.5, -35.44, boards); }
  for (let z = -30; z < 30; z += 6) { const b = mesh(new THREE.BoxGeometry(0.3, 0.95, 5.9), mat('#121315'), -56, 0.5, z + 3, boards); }
  // Spieler, Schiedsrichter, Ball
  const players = [];
  const home = {top: '#d1202c', pants: '#f4f4f0', shortSleeve: true}, away = {top: '#1f4fb8', pants: '#1a2a55', shortSleeve: true};
  for (let i = 0; i < 16; i++) { const t = i < 8 ? home : away; const p = makePerson(500 + i, {...t, height: 1.0 + r() * 0.08}); p.traverse(o => { if (o.isMesh) o.castShadow = true; }); scene.add(p);
    players.push({p, x0: -20 + r() * 40, z0: -24 + r() * 34, ph: r() * 6, dx: (r() - 0.5) * 2, run: r() * 0.4, side: r() < 0.5 ? -1 : 1}); }
  { const p = makePerson(77, {top: '#111', pants: '#111', shortSleeve: true}); scene.add(p); players.push({p, x0: 4, z0: -8, ph: 1, dx: 0.5, run: 0.2, side: 1, ref: true}); }
  const ballT = canvasTex(256, 128, (g, w, h) => { g.fillStyle = '#fafafa'; g.fillRect(0, 0, w, h); g.fillStyle = '#222'; const q = rng(2); for (let i = 0; i < 14; i++) { g.beginPath(); g.arc(q() * w, q() * h, 10, 0, 7); g.fill(); } });
  const ball = mesh(new THREE.SphereGeometry(0.11, 16, 12), new THREE.MeshStandardMaterial({map: ballT, roughness: 0.5}), 0, 0.11, 0, scene); ball.castShadow = true;

  // Betonbrocken und Staub
  const NCH = 1600, chunks = new THREE.InstancedMesh(new THREE.DodecahedronGeometry(0.6, 0), concrete, NCH); chunks.castShadow = true; scene.add(chunks);
  const ch = []; const rc = rng(55);
  for (let i = 0; i < NCH; i++) { const p = pieces[i % pieces.length]; ch.push({p, u: rc(), v: rc(), w: rc(), dly: rc() * 0.9, vx: (rc() - 0.5) * 3, vz: 1 + rc() * 4, s: 0.4 + rc() * 1.6, spin: V3(rc() * 6, rc() * 6, rc() * 6)}); }
  const dust = particles(7000, 'smoke'); scene.add(dust);
  // Einsturz-Reihenfolge: von unten nach oben, Mitte zuerst
  pieces.forEach(p => { p.tf = STAND_FALL + (p.side ? 0.9 + Math.abs(p.idx - 6) * 0.08 : Math.abs(p.idx - 11.5) * 0.06) + (p.upper ? 0.45 : 0) + rng(p.idx * 7 + (p.upper ? 3 : 1))() * 0.2; });

  const camera = new THREE.PerspectiveCamera(58, 1080 / 1920, 0.5, 2000);
  const wp = new THREE.Vector3();
  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.0;
    timeU.value = T; jumpU.value = T < STAND_FALL ? 0.6 : 0;
    // Tribünenstücke
    pieces.forEach(p => {
      const a = T - p.tf;
      if (a <= 0) { p.g.position.y = 0; p.g.rotation.set(0, 0, 0); p.g.scale.set(1, 1, 1); p.slab.material = concrete; return; }
      const drop = Math.min(p.upper ? 22 : p.Y * 0.75, 0.5 * 9.8 * a * a);
      p.g.position.y = -drop; const k = clamp(drop / (p.upper ? 22 : p.Y * 0.75));
      p.g.rotation.x = (p.upper ? 0.5 : 0.3) * k + Math.sin(p.idx * 3.1) * 0.05 * k; p.g.rotation.z = Math.sin(p.idx * 1.7 + (p.upper ? 1 : 0)) * 0.12 * k;
      p.g.scale.y = 1 - 0.35 * k; // zerbröselt
    });
    // Brocken
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
    ch.forEach((c, i) => {
      const a = T - c.p.tf - c.dly * 0.5;
      if (a <= 0) { m4.makeScale(0, 0, 0); chunks.setMatrixAt(i, m4); return; }
      // Startpunkt auf der Platte (Weltkoordinaten über die Gruppe)
      c.p.g.updateWorldMatrix(true, false);
      wp.set((c.u - 0.5) * c.p.width, c.p.h0 + c.v * (c.p.Y - c.p.h0) * 0.9, -c.v * c.p.D).applyMatrix4(c.p.g.matrixWorld);
      const y0 = wp.y; let y = y0 - 4.9 * a * a * 0.3; const x = wp.x + c.vx * a * 0.6, z = wp.z + c.vz * a * 0.7;
      y = Math.max(0.3 * c.s, y + 1.2 - a * 0.5);
      e.set(c.spin.x * a, c.spin.y * a, c.spin.z * a); q.setFromEuler(e); m4.compose(V3(x, y, z), q, V3(c.s, c.s * 0.7, c.s)); chunks.setMatrixAt(i, m4);
    });
    chunks.instanceMatrix.needsUpdate = true;
    // Staub: aus jeder Sektion beim Einsturz, große Wolke, Mast-Aufschlag
    const src = [];
    pieces.forEach((p, k) => { if (p.side || T < p.tf - 0.1) return; const x = -57.5 + p.idx * 5, v = 0.58 + (k % 5) * 0.035;
      if (p.upper) src.push({type: 'smoke', pos: V3(x, 16, -66), r: 6, t0: p.tf + 0.1, t1: p.tf + 2.4, size: 7 + (k % 3) * 2, rise: 2.6 + (k % 4) * 0.7, col: [v + 0.05, v, v - 0.07], alpha: 0.6, share: 1});
      else src.push({type: 'smoke', pos: V3(x, 2, -45), r: 5, t0: p.tf, t1: p.tf + 2.0, size: 8 + (k % 3) * 3, rise: 2.2 + (k % 4) * 0.7, col: [v + 0.06, v, v - 0.08], alpha: 0.6, share: 1}); });
    for (let i = 0; i < 4; i++) src.push({type: 'smoke', pos: V3(-64, 4, -22 + i * 14), r: 7, t0: STAND_FALL + 1.0 + i * 0.1, t1: STAND_FALL + 2.5, size: 9, rise: 2.4, col: [0.66, 0.61, 0.53], alpha: 0.7, share: 0.8});
    src.push({type: 'smoke', pos: V3(-12, 1, -34), r: 26, t0: STAND_FALL + 0.6, t1: STAND_FALL + 5, size: 14, rise: 1.6, col: [0.72, 0.67, 0.59], alpha: 0.5, share: 2.0});
    src.push({type: 'smoke', pos: V3(-28, 1, -30), r: 8, t0: MAST_HIT, t1: MAST_HIT + 0.8, size: 8, rise: 2.0, col: [0.7, 0.65, 0.57], alpha: 0.7, share: 0.8});
    if (T > STAND_FALL - 0.2) updateParticles(dust, src, T, V3(1.2, 0, 1.6)); else updateParticles(dust, [], T);
    // Dach sackt hinten-vorn ab, Flutlichtmast kippt
    const rk = smooth(STAND_FALL + 0.4, STAND_FALL + 3.2, T);
    roof.rotation.x = 0.2 * rk + Math.sin(T * 5) * 0.006 * rk; roof.rotation.z = 0.03 * rk;
    const ma = Math.max(0, T - MAST_T), ang = Math.min(1.42, 0.5 * 0.56 * ma * ma);
    mast.rotation.set(ang * 0.75, 0, -ang * 0.66);
    const bounce = T > MAST_HIT ? Math.sin((T - MAST_HIT) * 18) * Math.exp(-(T - MAST_HIT) * 6) * 0.03 : 0; mast.rotation.x += bounce;
    // Spieler: Spiel läuft, dann stehen bleiben und weglaufen
    const flee = T - STAND_FALL - 0.3;
    players.forEach((o, i) => {
      const t = T - 31; let x = o.x0 + o.dx * t * 2.2 + Math.sin(t * 0.9 + o.ph) * 1.5, z = o.z0 + Math.cos(t * 0.7 + o.ph) * 1.2, walk = T * 9 + o.ph, amp = 0.7, look = 0;
      let ry = Math.atan2(o.dx, 0.3);
      if (flee > 0) { const run = Math.max(0, flee - o.run); z += run * run * 1.6 + run * 2.5; x += o.side * run * 1.2; ry = Math.atan2(o.side * 0.4, 1); walk = T * 15 + o.ph; amp = run > 0 ? 1.2 : 0.1; look = run > 0 ? 0 : 0; if (run <= 0) { ry = Math.PI; amp = 0; } }
      o.p.position.set(x, 0, z); o.p.rotation.y = ry; posePerson(o.p, {walk, walkAmp: amp});
      if (flee > 0 && flee - o.run < 0.4) { const u = o.p.userData; u.armL.rotation.x = -2.0; u.armR.rotation.x = -2.0; u.armL.userData.fore.rotation.x = -1.5; u.armR.userData.fore.rotation.x = -1.5; } // Hände an den Kopf
    });
    { const t = T - 31; const a = players[2].p.position, b = players[11].p.position, u = (Math.sin(t * 1.3) + 1) / 2; ball.position.set(lerp(a.x, b.x, u) + 0.5, 0.11 + Math.abs(Math.sin(t * 4)) * (flee > 0 ? 0.6 : 0.15), lerp(a.z, b.z, u)); if (flee > 0) ball.position.z += flee * 0.8; ball.rotation.x = t * 8; }
    // Kamera: erhöhte TV-Position auf der Gegengerade
    const u = smooth(31, 39, T);
    const shk = (T > STAND_FALL ? 0.35 * Math.exp(-(T - STAND_FALL) * 0.9) : 0) + (T > MAST_HIT ? 0.3 * Math.exp(-(T - MAST_HIT) * 3) : 0);
    camera.position.set(lerp(-10, -5, u) + noise1(T * 11, 1) * shk, lerp(7, 6, u) + noise1(T * 11, 2) * shk, lerp(30, 24, u));
    camera.lookAt(lerp(-3, -1, u), lerp(20, 19, u), -50);
    camera.updateProjectionMatrix();
  }};
}
