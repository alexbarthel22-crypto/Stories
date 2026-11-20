// Glas-Skywalk über einer roten Felsschlucht, 200 m über dem Fluss. Ohne Sand kein Glas:
// Bodenplatten und Glasgeländer verschwinden, die Jugendlichen hängen an den Stahlträgern, Handy, Cap und Rucksack fallen.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, makePerson, posePerson, easeOut, envMap} from './lib.js';
import {SKY_DROP} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const RIM = -5, L0 = -6, L1 = 16, HW = 1.8, DEPTH = 205;
const cx = z => 70 + 25 * Math.sin(z / 180);

function terrainH(x, z) {
  const d = Math.abs(x - cx(z)), half = 75 + 6 * Math.sin(z / 47) + 4 * Math.sin(z / 13);
  const n = Math.sin(x * 0.05 + z * 0.03) * 2 + Math.sin(x * 0.13 - z * 0.07) * 1.2;
  if (d > half) return 1.5 * Math.sin((d - half) * 0.02) * Math.min(1, (d - half) / 30) + n * 0.6 + Math.max(0, (d - half - 300) * 0.15);
  const u = clamp((half - d) / 20); const s = u * 6; const st = Math.floor(s) + smooth(0.7, 1, s - Math.floor(s));
  return -DEPTH * Math.pow(st / 6, 0.95) + n * (1 - u * 0.5);
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const SUN = V3(0.35, 1, 0.5).normalize();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(1800, 32, 16), new THREE.ShaderMaterial({side: THREE.BackSide, depthWrite: false, fog: false, uniforms: {sunDir: {value: SUN}},
    vertexShader: 'varying vec3 v; void main(){ v = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); gl_Position.z = gl_Position.w; }',
    fragmentShader: `varying vec3 v; uniform vec3 sunDir; void main(){ float y = max(v.y, 0.0); vec3 c = mix(vec3(0.86,0.80,0.72), vec3(0.22,0.45,0.82), pow(y, 0.45));
      float s = max(dot(normalize(v), sunDir), 0.0); c += vec3(1.0,0.95,0.8) * (pow(s, 12.0) * 0.25 + pow(s, 600.0) * 4.0); if (v.y < 0.0) c = vec3(0.80,0.70,0.60); gl_FragColor = vec4(c, 1.0); }`}));
  sky.renderOrder = -10; scene.add(sky);
  scene.fog = new THREE.Fog('#d8c4ab', 140, 1500);
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.5;
  scene.add(new THREE.HemisphereLight('#cfe3ff', '#a0603a', 0.9));
  const sun = new THREE.DirectionalLight('#fff3df', 3.2); sun.position.copy(SUN).multiplyScalar(60).add(V3(5, 0, 0)); sun.target.position.set(5, 0, 0);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -28, right: 28, top: 28, bottom: -28, near: 1, far: 160}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.05;
  scene.add(sun, sun.target);
  // Schlucht (Höhenfeld mit Gesteinsschichten)
  const tg = new THREE.PlaneGeometry(1800, 1800, 300, 300); tg.rotateX(-Math.PI / 2);
  const P = tg.attributes.position, col = new Float32Array(P.count * 3), r = rng(4);
  const bands = ['#b4512b', '#c86a3a', '#9a3f24', '#d39a62', '#a8492a', '#c47a48', '#8e3a22'].map(c => new THREE.Color(c));
  for (let i = 0; i < P.count; i++) { const x = P.getX(i), z = P.getZ(i); const h = terrainH(x, z); P.setY(i, h);
    let c; if (h > -1.5) c = new THREE.Color('#b98a5c').lerp(new THREE.Color('#8f7a52'), (Math.sin(x * 0.3) * Math.sin(z * 0.27) + 1) * 0.25);
    else { const b = bands[Math.abs(Math.floor(h / 9 + Math.sin(x * 0.02) * 0.4)) % bands.length]; c = b.clone().multiplyScalar(0.85 + r() * 0.25); if (h < -DEPTH + 6) c = new THREE.Color('#8a6a4a'); }
    col.set([c.r, c.g, c.b], i * 3); }
  tg.setAttribute('color', new THREE.BufferAttribute(col, 3)); tg.computeVertexNormals();
  const terrain = new THREE.Mesh(tg, new THREE.MeshStandardMaterial({vertexColors: true, roughness: 1, flatShading: true})); terrain.receiveShadow = true; scene.add(terrain);
  // Fluss
  const rg = new THREE.PlaneGeometry(26, 1800, 1, 220); rg.rotateX(-Math.PI / 2); { const p = rg.attributes.position; for (let i = 0; i < p.count; i++) p.setX(i, p.getX(i) + cx(p.getZ(i))); }
  const river = mesh(rg, new THREE.MeshStandardMaterial({color: '#3f7c7a', roughness: 0.15, metalness: 0.2}), 0, -DEPTH + 2.2, 0, scene); river.receiveShadow = true;
  // Büsche auf dem Plateau
  { const bush = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 0), mat('#6f7a3c', {flatShading: true, roughness: 1}), 400); const m4 = new THREE.Matrix4(); let k = 0;
    for (let i = 0; i < 1200 && k < 400; i++) { const x = (r() - 0.5) * 900, z = (r() - 0.5) * 900; const h = terrainH(x, z); if (h < -1) continue; const s = 0.6 + r() * 1.4; m4.compose(V3(x, h + s * 0.4, z), new THREE.Quaternion(), V3(s, s * 0.7, s)); bush.setMatrixAt(k++, m4); }
    bush.count = k; bush.castShadow = true; scene.add(bush); }

  // Skywalk: Stahlrahmen, Glasboden, Glasgeländer, Handlauf
  const steel = mat('#5a6068', {metalness: 0.8, roughness: 0.35});
  const add = (geo, m, x, y, z) => { const o = mesh(geo, m, x, y, z, scene); o.castShadow = true; o.receiveShadow = true; return o; };
  for (const z of [-HW, 0, HW]) add(new THREE.BoxGeometry(L1 - L0, 0.3, 0.2), steel, (L0 + L1) / 2, -0.16, z);
  const crossX = []; for (let x = L0 + 1.5; x <= L1 + 0.01; x += 1.5) { add(new THREE.BoxGeometry(0.16, 0.24, HW * 2 + 0.2), steel, x, -0.13, 0); crossX.push(x); }
  add(new THREE.BoxGeometry(0.2, 0.3, HW * 2 + 0.2), steel, L1, -0.16, 0);
  for (const z of [-HW + 0.3, HW - 0.3]) { const b = add(new THREE.BoxGeometry(14, 0.35, 0.35), steel, RIM - 5.2, -4.4, z); b.rotation.z = Math.atan2(4.6, 10); } // Streben in die Felswand
  const glassM = new THREE.MeshStandardMaterial({color: '#bfe6ee', transparent: true, opacity: 0.28, roughness: 0.03, metalness: 0.2, envMapIntensity: 1.5});
  const panes = [];
  for (let x = L0 + 0.75; x < L1; x += 1.5) for (const z of [-HW / 2, HW / 2]) { const g = mesh(new THREE.BoxGeometry(1.42, 0.04, HW - 0.08), glassM, x, 0.0, z, scene); g.receiveShadow = true; panes.push(g); }
  const railGlassM = new THREE.MeshStandardMaterial({color: '#d2eef4', transparent: true, opacity: 0.18, roughness: 0.03, metalness: 0.2, envMapIntensity: 1.5});
  for (let x = L0 + 0.75; x < L1; x += 1.5) for (const z of [-HW - 0.05, HW + 0.05]) panes.push(mesh(new THREE.BoxGeometry(1.42, 1.0, 0.025), railGlassM, x, 0.55, z, scene));
  for (const zz of [-0.9, 0.9]) panes.push(mesh(new THREE.BoxGeometry(0.025, 1.0, 1.75), railGlassM, L1 + 0.05, 0.55, zz, scene));
  for (let x = L0; x <= L1 + 0.01; x += 1.5) for (const z of [-HW - 0.05, HW + 0.05]) add(new THREE.CylinderGeometry(0.035, 0.035, 1.12, 10), steel, x, 0.56, z);
  for (const z of [-HW - 0.05, HW + 0.05]) add(new THREE.CylinderGeometry(0.03, 0.03, L1 - L0, 10), steel, (L0 + L1) / 2, 1.12, z).rotation.z = Math.PI / 2;
  add(new THREE.CylinderGeometry(0.03, 0.03, HW * 2 + 0.1, 10), steel, L1 + 0.05, 1.12, 0).rotation.x = Math.PI / 2;
  // Zugang: Felsplateau mit Holzsteg
  add(new THREE.BoxGeometry(8, 0.2, HW * 2 + 0.4), mat('#7a5a3c', {roughness: 0.9}), L0 - 3.8, -0.05, 0);
  // Glitzern beim Verschwinden
  const glintT = canvasTex(64, 64, (g, w) => { const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.3, 'rgba(230,250,255,0.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const glints = []; for (let i = 0; i < 90; i++) { const sp = new THREE.Sprite(new THREE.SpriteMaterial({map: glintT, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false}));
    sp.userData = {p: V3(L0 + 2 + r() * (L1 - L0 - 2), r() < 0.6 ? 0.02 : 0.1 + r(), (r() - 0.5) * 2 * HW), d: r() * 0.15, s: 0.08 + r() * 0.15}; scene.add(sp); glints.push(sp); }

  // Jugendliche: stehen nahe an Querträgern und fangen sich daran
  const TEENS = [
    {x: crossX[6], z: -0.8, ry: -Math.PI / 2, o: {top: '#e8e2d4', pants: '#2d3a55', hair: '#2a1d15'}, selfie: true},
    {x: crossX[7], z: 0.9, ry: Math.PI / 2, o: {top: '#d94b3d', pants: '#1f2a44', hair: '#c9a35b', longHair: true}, cap: true},
    {x: crossX[8], z: -0.3, ry: Math.PI / 2 + 0.3, o: {top: '#3f6fb5', pants: '#3a3a3a', hair: '#111'}},
    {x: crossX[9], z: 1.1, ry: Math.PI / 2 - 0.5, o: {top: '#2f8f6b', pants: '#5b4636', hair: '#5a3b22', longHair: true}, pack: true},
    {x: crossX[10], z: -1.0, ry: Math.PI / 2 + 0.6, o: {top: '#e2b23a', pants: '#2b4d3a', hair: '#8a5a2b'}},
  ];
  const teens = TEENS.map((d, i) => { const p = makePerson(500 + i * 7, {shortSleeve: true, height: 0.95 + (i % 3) * 0.04, ...d.o}); scene.add(p); p.traverse(o => { if (o.isMesh) o.castShadow = true; }); return {...d, p, i}; });
  // Handy, Cap, Rucksack
  const phone = mesh(new THREE.BoxGeometry(0.075, 0.155, 0.01), mat('#16181c', {metalness: 0.6, roughness: 0.3}), 0, 0, 0, scene);
  const cap = new THREE.Group(); scene.add(cap); mesh(new THREE.SphereGeometry(0.12, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), mat('#111827'), 0, 0, 0, cap); mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.01, 16, 1, false, -Math.PI / 2, Math.PI), mat('#111827'), 0, 0.005, 0.07, cap);
  const pack = mesh(new THREE.BoxGeometry(0.32, 0.42, 0.18), mat('#c2410c', {roughness: 0.8}), 0, 0, 0, scene); pack.castShadow = true;
  const falling = [{o: phone, v: V3(0.6, 2.0, -0.4), spin: V3(9, 4, 6)}, {o: cap, v: V3(1.4, 1.4, 0.8), spin: V3(3, 8, 2)}, {o: pack, v: V3(0.8, 0.4, 0.6), spin: V3(2, 3, 4)}];
  const camera = new THREE.PerspectiveCamera(52, 1080 / 1920, 0.05, 3000);
  const tmp = V3(0, 0, 0);

  // Stehende Pose (vor dem Absacken) und Startpunkte der fallenden Gegenstände – unabhängig vom vorherigen Bild
  function stand(o, T) { const {p, i} = o, u = p.userData; p.rotation.set(0, o.ry, 0); p.position.set(o.x, 0.02, o.z);
    posePerson(p, {look: Math.sin(T * 0.8 + i) * 0.3, holdUp: o.selfie ? 1 : 0});
    if (!o.selfie && i % 2) { u.armL.rotation.x = -1.2; u.armL.rotation.z = -0.6; u.armR.rotation.x = -1.2; u.armR.rotation.z = 0.6; }
    if (o.selfie) { u.armR.rotation.x = -2.0; u.armR.rotation.z = 0.3; u.head.rotation.x = -0.15; }
    p.updateMatrixWorld(true); }
  function itemStarts(T) { teens.forEach(o => { stand(o, T); const u = o.p.userData;
    if (o.selfie) { u.armR.userData.fore.getWorldPosition(tmp); phone.position.copy(tmp).add(V3(0, 0.3, 0)); phone.rotation.set(0, o.ry + Math.PI / 2, 0); }
    if (o.cap) { u.head.getWorldPosition(tmp); cap.position.copy(tmp).add(V3(0, 0.15, 0)); cap.rotation.set(0, o.ry, 0); }
    if (o.pack) { u.torso.getWorldPosition(tmp); pack.position.copy(tmp).add(V3(-Math.sin(o.ry) * 0.2, 0.32, -Math.cos(o.ry) * 0.2)); pack.rotation.set(0, o.ry, 0); } });
    falling.forEach(f => f.p0 = f.o.position.clone()); }
  itemStarts(SKY_DROP - 0.001);

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 0.95;
    const gone = T >= SKY_DROP, d = T - SKY_DROP;
    panes.forEach(p => p.visible = !gone);
    glints.forEach(s => { const a = d - s.userData.d; s.visible = a > 0 && a < 0.5; if (!s.visible) return; const k = Math.sin(a / 0.5 * Math.PI); s.position.copy(s.userData.p).add(V3(0, -a * 1.5, 0)); s.scale.setScalar(s.userData.s * (0.5 + k)); s.material.opacity = k; });
    teens.forEach(o => { const {p, i} = o, u = p.userData; const td = d - i * 0.06;
      p.rotation.set(0, o.ry, 0);
      if (td <= 0) { stand(o, T);
      } else { // Fall und Griff an den Querträger
        const h = 2.07 * u.h, fall = 4.9 * td * td, y = -Math.min(fall, h);
        const caught = fall >= h, tc = td - Math.sqrt(h / 4.9); const bounce = caught ? 0.18 * Math.exp(-tc * 4) * Math.cos(tc * 14) : 0;
        p.position.set(o.x, y + bounce - 0.02, o.z * (caught ? 1 : 1));
        posePerson(p, {walk: T * 7 + i, walkAmp: 0.9 * (caught ? 0.6 + 0.4 * Math.exp(-tc) : 1), armsUp: easeOut(clamp(td / 0.22))});
        u.armL.rotation.z = -2.75; u.armR.rotation.z = 2.75; u.armL.userData.fore.rotation.x = 0; u.armR.userData.fore.rotation.x = 0; u.head.rotation.x = -0.4 + 0.2 * Math.sin(T * 3 + i);
        u.body.rotation.z = Math.sin(T * 2.2 + i) * 0.08 * (caught ? 1 : 0);
      }
      p.updateMatrixWorld(true);
    });
    if (!(d > 0)) itemStarts(T);
    if (d > 0) falling.forEach((f, k) => { const t = Math.max(0, d - k * 0.12); const drag = 0.15;
      f.o.position.set(f.p0.x + f.v.x * t, Math.max(-DEPTH + 3, f.p0.y + f.v.y * t - 4.9 * t * t * (1 - drag * Math.min(t, 3) / 3)), f.p0.z + f.v.z * t);
      f.o.rotation.set(f.spin.x * t, f.spin.y * t, f.spin.z * t); });
    // Kamera: hinter der Gruppe am Felsrand, nach dem Absacken Ruck und Blick in die Tiefe
    const t = T - shot.t0, push = smooth(0, 2, t), sh = d > 0 ? 0.06 * Math.exp(-d * 2.5) : 0, tilt = easeOut(clamp((d - 0.4) / 2.2));
    camera.fov = 55 + 5 * tilt;
    camera.position.set(lerp(1.0, 2.0, push) + 1.5 * tilt + noise1(T * 15, 1) * sh, lerp(3.4, 3.1, push) - 0.6 * tilt + noise1(T * 15, 2) * sh, lerp(9.0, 8.2, push) - 1.2 * tilt + noise1(T * 15, 3) * sh);
    const look = V3(lerp(8.0, 8.5, tilt), lerp(-0.6, -5 - 7 * smooth(1.2, 4.5, d), tilt), lerp(-0.6, -0.8, tilt)); camera.lookAt(look);
    camera.updateProjectionMatrix();
  }};
}
