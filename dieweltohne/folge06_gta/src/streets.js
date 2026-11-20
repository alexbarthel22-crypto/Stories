// Stufe 6 und 7: Nachts strömen Millionen Gamer gleichzeitig aus ihren Häusern. GTA 6 kommt zurück, alle laden gleichzeitig neu,
// das Netz bricht zusammen. Bis zum Sonnenaufgang bleibt die ganze Stadt draußen.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, asphaltTex, makePerson, posePerson, makeCar, envMap} from './lib.js';
import {RETURN, NET_DOWN, SUNRISE} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const ROADS_X = [-46, 0, 46], ROADS_Z = [-38, -82, -126, 6]; // Straßenachsen (Breite 14 m inkl. Gehwegen)

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.fog = new THREE.Fog('#0b1020', 40, 260);
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.15;
  const hemi = new THREE.HemisphereLight('#5065a0', '#1a1410', 0.35); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#ffb070', 0); sun.position.set(-30, 20, -200); sun.target.position.set(0, 0, -40);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -80, right: 80, top: 80, bottom: -80, near: 10, far: 400}); sun.shadow.bias = -0.0006; scene.add(sun, sun.target);
  // Himmel: Nacht -> Morgendämmerung
  const skyM = new THREE.ShaderMaterial({side: THREE.BackSide, depthWrite: false, fog: false, uniforms: {k: {value: 0}},
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }',
    fragmentShader: `uniform float k; varying vec3 vP; void main(){ float h = clamp(vP.y, -0.1, 1.0);
      vec3 nTop = vec3(0.02,0.03,0.08), nHor = vec3(0.07,0.09,0.18);
      vec3 dTop = vec3(0.35,0.52,0.82), dHor = vec3(1.0,0.66,0.42);
      float toward = max(0., dot(normalize(vec3(vP.x, 0., vP.z)), normalize(vec3(-0.15, 0., -1.))));
      vec3 top = mix(nTop, dTop, k), hor = mix(nHor, mix(vec3(0.95,0.75,0.6), dHor, toward), k);
      vec3 c = mix(hor, top, pow(h, 0.55));
      float sd = distance(vP, normalize(vec3(-0.15, 0.06, -1.)));
      c += k * vec3(1.0,0.8,0.5) * (smoothstep(0.06, 0.0, sd) * 2.0 + exp(-sd * 6.) * 0.5);
      gl_FragColor = vec4(c, 1.); }`});
  const sky = new THREE.Mesh(new THREE.SphereGeometry(600, 32, 16), skyM); sky.renderOrder = -10; scene.add(sky);
  // Boden: Asphalt
  const aT = asphaltTex(); aT.wrapS = aT.wrapT = THREE.RepeatWrapping; aT.repeat.set(40, 40);
  const ground = mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({map: aT, roughness: 0.9}), 0, 0, -60, scene); ground.rotation.x = -Math.PI / 2;
  // Gehwege und Mittellinien der Hauptstraße
  const sideM = mat('#8a8a86', {roughness: 0.9});
  for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(2.4, 0.15, 200), sideM, s * 5.8, 0.075, -60, scene);
  for (let z = 20; z > -150; z -= 6) mesh(new THREE.PlaneGeometry(0.15, 2.6), mat('#e8e2c8'), 0, 0.01, z, scene).rotation.x = -Math.PI / 2;
  // Häuserblöcke (Blockraster), Fenster leuchten nachts
  const winMats = []; const r0 = rng(31); const doors = [];
  const XS = [[-84.8, -53.2], [-38.8, -7.2], [7.2, 38.8], [53.2, 84.8]], ZS = [[13.2, 40], [-30.8, -1.2], [-74.8, -45.2], [-118.8, -89.2], [-170, -133.2]];
  XS.forEach(([x0, x1], bi) => ZS.forEach(([z0, z1], bj) => {
    const nx = 3, nz = Math.max(2, Math.round((z1 - z0) / 11)), w = (x1 - x0) / nx, d = (z1 - z0) / nz;
    for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) {
      const x = x0 + (i + 0.5) * w, z = z0 + (j + 0.5) * d, h = 10 + r0() * 20 + (Math.abs(x) < 40 ? 6 : 0);
      const m = new THREE.MeshStandardMaterial({map: facadeTex(['#6a5a4a', '#5a5f6a', '#7a6a5a', '#4a5560', '#8a7a68'][(i + j + bi) % 5], 100 + i * 7 + j * 13 + bi * 31 + bj * 17, Math.round(h / 3.2), 3), roughness: 0.85, emissive: '#ffd9a0', emissiveIntensity: 0.5});
      m.emissiveMap = m.map; winMats.push(m);
      const bm = mesh(new THREE.BoxGeometry(w - 0.3, h, d - 0.3), m, x, h / 2, z, scene); bm.castShadow = true;
      mesh(new THREE.BoxGeometry(w, 0.4, d), mat('#3a3a3a'), x, h + 0.2, z, scene);
      if ((bi === 1 && i === 2) || (bi === 2 && i === 0)) doors.push({x: Math.sign(x) * 7.0, z: z + (r0() - 0.5) * d * 0.6});
    }
  }));
  // Leuchttafel an der Ecke
  const BC = document.createElement('canvas'); BC.width = 512; BC.height = 768; const bT = new THREE.CanvasTexture(BC); bT.colorSpace = THREE.SRGBColorSpace;
  const board = mesh(new THREE.PlaneGeometry(6, 9), new THREE.MeshBasicMaterial({map: bT, toneMapped: false}), 6.95, 11, -30, scene); board.rotation.y = -Math.PI / 2;
  mesh(new THREE.BoxGeometry(0.3, 9.4, 6.4), mat('#111'), 7.15, 11, -30, scene);
  const boardL = new THREE.PointLight('#5a8cff', 30, 30, 1.5); boardL.position.set(4, 10, -30); scene.add(boardL);
  // Laternen
  const lamps = []; for (let z = 14; z > -140; z -= 18) for (const s of [-1, 1]) { mesh(new THREE.CylinderGeometry(0.08, 0.1, 6, 8), mat('#2b2f33', {metalness: 0.6}), s * 6.6, 3, z + (s > 0 ? 9 : 0), scene);
    mesh(new THREE.BoxGeometry(1.2, 0.15, 0.4), new THREE.MeshStandardMaterial({color: '#333', emissive: '#ffcf8a', emissiveIntensity: 2}), s * 6.1, 6, z + (s > 0 ? 9 : 0), scene); }
  for (let z = 10; z > -110; z -= 30) { const l = new THREE.PointLight('#ffc27a', 25, 24, 1.6); l.position.set(z % 60 ? 4 : -4, 5.6, z); scene.add(l); lamps.push(l); }
  // Stehende Autos mit Licht
  const cars = []; [[-2.2, -8, 0], [2.2, -16, Math.PI], [-2.2, -22, 0.1], [2.2, -34, Math.PI], [-2.0, -45, 0], [2.4, -52, Math.PI + 0.1], [-2.2, -63, 0], [2.2, -71, Math.PI]].forEach(([x, z, ry], i) => {
    const c = makeCar(i + 1); c.position.set(x, 0, z); c.rotation.y = ry; scene.add(c); cars.push(c); });
  // Instanzierte Menge: kommt aus den Türen und füllt alle Straßen
  const N = 5200, r = rng(8); const crowd = [];
  for (let i = 0; i < N; i++) {
    let tx, tz, sx, sz; const pick = r();
    if (pick < 0.45 && doors.length) { const d = doors[Math.floor(r() * doors.length)]; sx = d.x; sz = d.z; tx = (r() - 0.5) * 12; tz = sz + (r() - 0.5) * 10; }
    else { const alongX = r() < 0.5; if (alongX) { const rx = ROADS_X[Math.floor(r() * 3)]; tx = rx + (r() - 0.5) * 12; tz = 20 - r() * 180; sx = rx + Math.sign(r() - 0.5) * 7.2; sz = tz + (r() - 0.5) * 4; }
      else { const rz = ROADS_Z[Math.floor(r() * ROADS_Z.length)]; tz = rz + (r() - 0.5) * 12; tx = (r() - 0.5) * 150; sz = rz + Math.sign(r() - 0.5) * 7.2; sx = tx + (r() - 0.5) * 4; } }
    crowd.push({sx, sz, tx, tz, te: 48.3 + Math.pow(r(), 0.7) * 9.0, dur: 2 + r() * 2.5, ph: r() * 6, hgt: 0.88 + r() * 0.22, phone: r() < 0.5, sit: r() < 0.55, lie: r() < 0.1, ry: r() * 6});
  }
  const bodyI = new THREE.InstancedMesh(new THREE.CapsuleGeometry(0.22, 0.75, 3, 8), new THREE.MeshStandardMaterial({roughness: 0.8}), N);
  const headI = new THREE.InstancedMesh(new THREE.SphereGeometry(0.13, 10, 8), new THREE.MeshStandardMaterial({roughness: 0.7}), N);
  const phM = new THREE.MeshBasicMaterial({color: '#e8f2ff', toneMapped: false}); const phI = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.1, 0.17), phM, N);
  const tops = ['#2b2f3a', '#3f6fb5', '#24343f', '#7b4fa0', '#d94b3d', '#222', '#555', '#2f8f6b', '#e8e2d4', '#c23b6a', '#3a3a3a'], skins = ['#f1c7a5', '#d9a47e', '#a8714a', '#6b4429', '#e8b894'];
  const c = new THREE.Color(); crowd.forEach((p, i) => { bodyI.setColorAt(i, c.set(tops[i % tops.length])); headI.setColorAt(i, c.set(skins[(i * 7) % skins.length])); });
  bodyI.castShadow = true; [bodyI, headI, phI].forEach(m => { m.frustumCulled = false; }); scene.add(bodyI, headI, phI);
  // Detaillierte Menschen nahe der Kamera: kommen aus der Haustür links
  const near = []; for (let i = 0; i < 14; i++) { const p = makePerson(300 + i, {top: ['#2b2f3a', '#3f6fb5', '#24343f', '#7b4fa0', '#5a3a5e'][i % 5]}); scene.add(p);
    const head = new THREE.Group(); mesh(new THREE.TorusGeometry(0.13, 0.018, 6, 18, Math.PI), mat('#111'), 0, 0.1, 0, head); p.userData.head.add(head); head.visible = i % 3 === 0;
    near.push({p, te: 48.4 + i * 0.45, tx: -3.5 + (i % 5) * 1.6, tz: 4 - Math.floor(i / 5) * 2.2 - (i % 2) * 0.6}); }
  const DOOR = V3(-7.0, 0, 6.0);
  mesh(new THREE.BoxGeometry(0.2, 2.4, 1.6), new THREE.MeshStandardMaterial({color: '#ffd9a0', emissive: '#ffd9a0', emissiveIntensity: 1.2}), -7.1, 1.2, 6.0, scene);

  function drawBoard(T) {
    const g = BC.getContext('2d'), w = 512, h = 768;
    if (T < RETURN) { g.fillStyle = '#05070c'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(90,140,255,0.6)'; g.font = '600 46px Plex'; g.textAlign = 'center'; g.fillText('KEIN SIGNAL', w / 2, h / 2); }
    else if (T < NET_DOWN) { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#11203f'); gr.addColorStop(0.6, '#1f8a8a'); gr.addColorStop(1, '#f0b35a'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = '600 64px Plex'; g.fillText('GTA 6', w / 2, 220); g.font = '600 52px Plex'; g.fillText('IST ZURÜCK', w / 2, 290);
      const pct = Math.min(3, Math.floor((T - RETURN) * 0.8)); g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(60, 480, w - 120, 30); g.fillStyle = '#fff'; g.fillRect(60, 480, (w - 120) * Math.max(0.01, pct / 100), 30);
      g.font = '500 34px Plex'; g.fillText(`Download ${pct} %`, w / 2, 560); }
    else { g.fillStyle = '#2a0608'; g.fillRect(0, 0, w, h); if (Math.sin(T * 6) > -0.2) { g.fillStyle = '#ff3a2a'; g.textAlign = 'center'; g.font = '600 56px Plex'; g.fillText('KEINE', w / 2, h / 2 - 20); g.fillText('VERBINDUNG', w / 2, h / 2 + 50); } }
    bT.needsUpdate = true;
  }

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.1, 900); scene.add(camera);
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), S = V3(1, 1, 1), P = V3(), E = new THREE.Euler();
  return {scene, camera, update(shot, T) {
    const id = shot.id, t = T - shot.t0;
    // Tageszeit
    const dk = smooth(SUNRISE, SUNRISE + 9, T); skyM.uniforms.k.value = dk;
    scene.fog.color.setRGB(lerp(0.043, 0.85, dk), lerp(0.063, 0.68, dk), lerp(0.125, 0.55, dk)); scene.fog.near = lerp(40, 80, dk); scene.fog.far = lerp(260, 420, dk);
    sun.intensity = 4.5 * dk; hemi.intensity = lerp(0.35, 1.5, dk); scene.environmentIntensity = lerp(0.15, 0.5, dk); hemi.color.setRGB(lerp(0.31, 0.75, dk), lerp(0.4, 0.78, dk), lerp(0.63, 0.9, dk));
    winMats.forEach(m => { m.emissiveIntensity = lerp(0.5, 0.05, dk); });
    lamps.forEach(l => { l.intensity = 25 * (1 - dk); }); boardL.intensity = T < NET_DOWN ? 30 : 14 * (1 - dk) + 4;
    boardL.color.set(T >= NET_DOWN ? '#ff3a2a' : '#5a8cff');
    drawBoard(T);
    // Menge
    const netK = T > NET_DOWN ? 1 : 0; phM.color.set(T > RETURN && T < NET_DOWN ? '#bfe0ff' : (netK ? '#ff5a4a' : '#e8f2ff'));
    crowd.forEach((p, i) => {
      if (T < p.te) { P.set(0, -9, 0); M.compose(P, Q, S); bodyI.setMatrixAt(i, M); headI.setMatrixAt(i, M); phI.setMatrixAt(i, M); return; }
      const k = smooth(p.te, p.te + p.dur, T), x = lerp(p.sx, p.tx, k), z = lerp(p.sz, p.tz, k), bob = k < 1 ? Math.abs(Math.sin(T * 9 + p.ph)) * 0.06 : 0;
      const sit = p.sit ? smooth(SUNRISE + 1 + p.ph * 0.5, SUNRISE + 2.5 + p.ph * 0.5, T) : 0, lie = p.lie ? smooth(SUNRISE + 3 + p.ph, SUNRISE + 4 + p.ph, T) : 0;
      const hs = p.hgt * (1 - 0.42 * sit);
      E.set(lie * Math.PI / 2, p.ry, 0); Q.setFromEuler(E);
      P.set(x, (0.62 * hs + bob) * (1 - lie * 0.6), z); S.set(1, hs, 1); M.compose(P, Q, S); bodyI.setMatrixAt(i, M);
      const hy = 1.4 * hs + bob; P.set(x + Math.sin(p.ry) * lie * 0.9, hy * (1 - lie) + 0.2 * lie, z + Math.cos(p.ry) * lie * 0.9); S.set(1, 1, 1); Q.identity(); M.compose(P, Q, S); headI.setMatrixAt(i, M);
      const showPh = p.phone && T > 49 && (T < NET_DOWN + 2.5 || (i % 5 === 0)) && lie < 0.5; P.set(x + 0.18, showPh ? (sit > 0.5 ? 1.0 : 1.8 * p.hgt) : -9, z - 0.12); M.compose(P, Q, S); phI.setMatrixAt(i, M);
    });
    bodyI.instanceMatrix.needsUpdate = headI.instanceMatrix.needsUpdate = phI.instanceMatrix.needsUpdate = true;
    near.forEach((o, i) => { const p = o.p; if (T < o.te) { p.visible = false; return; } p.visible = true;
      const k = smooth(o.te, o.te + 2.4, T); p.position.set(lerp(DOOR.x, o.tx, k), 0.15, lerp(DOOR.z, o.tz, k)); p.rotation.set(0, Math.atan2(o.tx - DOOR.x, o.tz - DOOR.z), 0);
      if (k < 1) posePerson(p, {walk: T * 8 + i, walkAmp: 1}); else { p.rotation.y += Math.sin(T * 0.6 + i) * 0.8; posePerson(p, {look: Math.sin(T + i) * 0.5, holdUp: i % 2 ? 0.55 : 0}); } });
    // Kamera
    camera.fov = 50;
    if (id === 'streets') { const up = smooth(3.5, 9.5, t); camera.position.set(lerp(2.6, 3.5, up), lerp(1.7, 13, up), lerp(13, 22, up)); camera.lookAt(lerp(-4.5, 0, up), lerp(1.6, 1, up), lerp(4, -30, up)); }
    else if (id === 'return') { const k = smooth(0, 8, t); camera.position.set(lerp(-3.5, -3.0, k), lerp(8.5, 9.5, k), lerp(-4, -8, k)); camera.lookAt(lerp(3, 4, k), lerp(5, 6, k), -32); }
    else { const u = smooth(0.5, 13.5, t); camera.position.set(lerp(-2, 8, u), lerp(10, 70, u), lerp(-6, 40, u)); camera.lookAt(0, lerp(0, 4, u), lerp(-40, -150, u)); }
    camera.updateProjectionMatrix();
  }};
}
