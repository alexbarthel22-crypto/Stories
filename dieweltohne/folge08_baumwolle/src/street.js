// Innenstadt. street_return: Die Baumwolle kommt zurück – nicht als Stoff, sondern als lose Fasern, die wie Schnee auf die Stadt fallen.
// street_fire: Aus dem Imbiss (Fettbrand) springt das Feuer auf die Fasern über; eine Feuerfront rast über den Boden.
// aerial: Luftbild – weitere Brände in der ganzen Stadt, Rauchsäulen.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, facadeTex, asphaltTex, tileTex, skyDome, easeOut, easeIn, posePerson, envMap, makeCar} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {cottonPerson, setCotton, flakes, updateFlakes, fluffTex} from './cotton.js';
import {RETURN, IGNITE} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const SPEED = 6.0; // Ausbreitung der Feuerfront in m/s
// Brandherde: [x, z, Zündzeit]
const IMB = [6.8, -6];
const FIRES = [[IMB[0], IMB[1], IGNITE], [-90, -120, 66.5], [120, -60, 69.0], [-40, -230, 70.5], [70, -200, 71.5], [-150, -40, 72.5], [160, -170, 73.5], [10, -320, 74.0]];

export async function build(renderer) {
  const scene = new THREE.Scene();
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.4;
  scene.fog = new THREE.Fog('#d9dfe4', 80, 600);
  const sky = skyDome('#5b88b8', '#b9cbd8', '#e6e2da', 900); scene.add(sky);
  const hemi = new THREE.HemisphereLight('#e8eef6', '#6a665e', 0.9); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff0dc', 2.4); sun.position.set(-60, 90, 40); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, {left: -60, right: 60, top: 60, bottom: -60, near: 1, far: 300}); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.05; scene.add(sun, sun.target);
  const fireL = new THREE.PointLight('#ff7a2a', 0, 60, 1.3); scene.add(fireL);

  // Boden: Straßen (Asphalt) und Blöcke (Gehweg)
  const asT = asphaltTex(); asT.repeat.set(30, 30);
  mesh(new THREE.PlaneGeometry(1400, 1400), new THREE.MeshStandardMaterial({map: asT, roughness: 0.95}), 0, 0, -150, scene).rotation.x = -Math.PI / 2;
  const swT = tileTex('#a7a49c', '#9c998f'); swT.repeat.set(10, 10);
  const swM = new THREE.MeshStandardMaterial({map: swT, roughness: 0.9});
  // Straßenraster: Hauptstraße x∈[-6,6], Querstraßen alle 48 m
  const facadeCols = ['#b6a08a', '#9fa7b0', '#c8b49c', '#8e8a96', '#a58f7c', '#d1c3ad'];
  const ftex = facadeCols.map((c, i) => facadeTex(c, 60 + i, 7, 5));
  const roofM = mat('#5a5652', {roughness: 0.95});
  const bldgs = [];
  const r = rng(91);
  for (let bx = -5; bx <= 5; bx++) for (let bz = -8; bz <= 2; bz++) {
    const x0 = bx * 48 + 6, x1 = bx * 48 + 42, z0 = bz * 48 - 18, z1 = bz * 48 + 18; // Block 36 x 36
    const cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
    const sw = mesh(new THREE.BoxGeometry(x1 - x0 + 3, 0.15, z1 - z0 + 3), swM, cx, 0.075, cz, scene); sw.castShadow = false;
    // 4 Häuser je Block (Hauptstraßenseite feiner unterteilt)
    const parts = bx === 0 || bx === -1 ? 3 : 2;
    for (let i = 0; i < parts; i++) for (let k = 0; k < 2; k++) {
      const w = (z1 - z0) / parts, d = (x1 - x0) / 2;
      const hx = x0 + d * k + d / 2, hz = z0 + w * i + w / 2, h = 12 + r() * (Math.abs(bx) < 2 ? 18 : 34);
      const ti = Math.floor(r() * 6); const t = ftex[ti].clone(); t.needsUpdate = true; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1, h / 21);
      const fm = new THREE.MeshStandardMaterial({map: ftex[ti], roughness: 0.9, emissive: '#ff6a1a', emissiveMap: ftex[ti], emissiveIntensity: 0});
      const b = mesh(new THREE.BoxGeometry(d - 0.4, h, w - 0.4), [fm, fm, roofM, roofM, fm, fm], hx, h / 2 + 0.15, hz, scene);
      bldgs.push({b, fm, x: hx, z: hz, h, ign: 1e9});
    }
  }
  // Imbiss im Erdgeschoss rechts der Hauptstraße
  const imb = new THREE.Group(); imb.position.set(6.2, 0.15, IMB[1]); scene.add(imb);
  const signT = canvasTex(512, 96, (g, w, h) => { g.fillStyle = '#b8261c'; g.fillRect(0, 0, w, h); g.fillStyle = '#ffd23f'; g.font = '900 60px sans-serif'; g.fillText('IMBISS AM ECK', 22, 70); });
  mesh(new THREE.BoxGeometry(0.2, 0.7, 4.2), new THREE.MeshStandardMaterial({map: signT, emissive: '#ffffff', emissiveMap: signT, emissiveIntensity: 0.3}), -0.1, 3.3, 0, imb).rotation.y = 0;
  const glowM = new THREE.MeshStandardMaterial({color: '#2a1a10', emissive: '#ff7a2a', emissiveIntensity: 2.5});
  mesh(new THREE.PlaneGeometry(3.8, 2.4), glowM, -0.12, 1.4, 0, imb).rotation.y = -Math.PI / 2;
  const awning = mesh(new THREE.BoxGeometry(1.4, 0.08, 4.4), mat('#c0392b'), -0.7, 2.85, 0, imb); awning.rotation.z = -0.25;
  // Parkende Autos, Laternen, Bäume an der Hauptstraße
  const cars = [];
  for (let i = 0; i < 10; i++) { const c = makeCar(i + 3); const side = i % 2 ? 1 : -1; c.position.set(side * 3.3, 0, 14 - i * 9 - (i % 3)); c.rotation.y = side > 0 ? Math.PI : 0; scene.add(c); cars.push(c); }
  const poleM = mat('#2b2f33', {metalness: 0.6});
  for (let z = 22; z > -90; z -= 14) for (const s of [-1, 1]) { mesh(new THREE.CylinderGeometry(0.07, 0.09, 6, 8), poleM, s * 4.9, 3, z + (s > 0 ? 7 : 0), scene); mesh(new THREE.BoxGeometry(1.2, 0.12, 0.3), poleM, s * 4.4, 6, z + (s > 0 ? 7 : 0), scene); }
  const leafM = mat('#55803e', {roughness: 0.9}), trunkM = mat('#5a4330');
  const trees = [];
  for (let z = 16; z > -90; z -= 11) for (const s of [-1, 1]) { if (Math.abs(z - IMB[1]) < 4 && s > 0) continue; const g = new THREE.Group(); g.position.set(s * 5.4, 0.15, z + (s > 0 ? 5 : 0)); scene.add(g);
    mesh(new THREE.CylinderGeometry(0.15, 0.2, 3, 8), trunkM, 0, 1.5, 0, g); const crown = mesh(new THREE.IcosahedronGeometry(1.7, 1), leafM, 0, 4, 0, g); trees.push({g, crown, x: g.position.x, z: g.position.z}); }

  // Faserschicht über der ganzen Stadt, mit Brandringen im Shader
  const U = {uW: {value: 1}, uC: {value: FIRES.map(f => new THREE.Vector3(f[0], f[1], 0))}, uR: {value: FIRES.map(() => -1)}};
  const fluffM = new THREE.MeshStandardMaterial({map: fluffTex(140), roughness: 1, transparent: true, opacity: 0, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1});
  fluffM.onBeforeCompile = sh => {
    sh.uniforms.uC = U.uC; sh.uniforms.uR = U.uR; sh.uniforms.uW = U.uW;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vW;').replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>\nvarying vec3 vW; uniform vec3 uC[${FIRES.length}]; uniform float uR[${FIRES.length}]; uniform float uW;`)
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        float burnt = 0.0, edge = 0.0;
        for (int i = 0; i < ${FIRES.length}; i++) { if (uR[i] < 0.0) continue; float d = length(vW.xz - uC[i].xy);
          float n = sin(vW.x * 0.35 + vW.z * 0.21) * 1.5 + sin(vW.x * 0.11 - vW.z * 0.4) * 2.0; float rr = uR[i] + n;
          burnt = max(burnt, step(d, rr - 3.0 * uW));
          edge = max(edge, smoothstep(rr - 4.5 * uW, rr - 1.5, d) * (1.0 - smoothstep(rr - 0.5, rr + 0.8 * uW, d))); }
        diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.06, 0.05, 0.045), burnt);
        totalEmissiveRadiance += vec3(1.0, 0.42, 0.08) * edge * 5.0 + vec3(0.6, 0.15, 0.02) * burnt * 0.15 * (0.6 + 0.4 * sin(vW.x * 1.7 + vW.z * 1.3));`);
  };
  const fluff = mesh(new THREE.PlaneGeometry(1300, 1300), fluffM, 0, 0.2, -150, scene); fluff.rotation.x = -Math.PI / 2; fluff.castShadow = false; fluff.renderOrder = 1;
  // Bausche auf Autos, Gehwegen, Dächern (nur in Straßennähe)
  const tuftN = 700; const tufts = new THREE.InstancedMesh(new THREE.SphereGeometry(0.5, 10, 8), mat('#f6f3ec', {roughness: 1}), tuftN); tufts.castShadow = true;
  const tuftData = []; { const q = rng(14); for (let i = 0; i < tuftN; i++) { let x, y = 0.15, z, s;
      if (i < 120) { const c = cars[i % cars.length]; x = c.position.x + (q() - 0.5) * 1.6; z = c.position.z + (q() - 0.5) * 3.2; y = 1.45; s = 0.3 + q() * 0.5; }
      else if (i < 520) { x = (q() - 0.5) * 16; z = 30 - q() * 130; s = 0.3 + q() * 1.4; if (Math.abs(x) > 6.5) s *= 1.5; }
      else { const tr = trees[i % trees.length]; x = tr.x + (q() - 0.5) * 2.4; z = tr.z + (q() - 0.5) * 2.4; y = 4 + q() * 1.2; s = 0.4 + q() * 0.6; }
      tuftData.push({x, y, z, s}); } }
  scene.add(tufts);
  const m4 = new THREE.Matrix4(), q4 = new THREE.Quaternion();
  // Schnee aus Fasern
  const snow = flakes(5000, [-30, 30, 0, 30, -60, 40], 0.18); scene.add(snow);
  // Feuer und Rauch
  const fire = particles(3000, 'flame'); scene.add(fire);
  const smoke = particles(1800, 'smoke'); scene.add(smoke);
  // Menschen auf der Straße (Baumwollkleidung ist weg: Shorts und Shirts aus Kunstfaser)
  const people = []; const PP = [[-2, 6, 0.2], [1.5, 3, -0.4], [-4.8, -2, 0.9], [3.2, 9, 2.8], [-1, -10, 0.1], [2.5, -14, -0.2], [-3.5, 12, 0.5]];
  PP.forEach(([x, z, ry], i) => { const p = cottonPerson(400 + i, {hoodie: i % 3 === 0 ? '#7b4fa0' : null, under: ['#e94f6a', '#2f6fd1', '#2b2b2b', '#2fa36b'][i % 4], ponytail: i % 2 === 1}); p.position.set(x, 0.15, z); p.rotation.y = ry; scene.add(p); people.push({p, x, z, ry, d: i * 0.17}); });

  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.1, 2500);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, id = shot.id;
    const back = T >= RETURN - 0.4;
    const cover = smooth(RETURN - 0.4, RETURN + 3.5, T);
    fluffM.opacity = cover * 0.97;
    fluff.position.y = 0.2 + 0.25 * cover;
    // Brandringe
    const R = FIRES.map(f => T > f[2] ? SPEED * (T - f[2]) : -1);
    U.uR.value = R; U.uW.value = id === 'aerial' ? 3.0 : 1.0;
    // Bausche: wachsen beim Rückkommen, verbrennen, wenn der Ring sie erreicht
    tuftData.forEach((d, i) => { let s = d.s * cover; for (let k = 0; k < FIRES.length; k++) if (R[k] > 0) { const dd = Math.hypot(d.x - FIRES[k][0], d.z - FIRES[k][1]); if (dd < R[k] - 2) s = 0; }
      m4.compose(V3(d.x, d.y + 0.2 * cover, d.z), q4, V3(s * 1.4, s * 0.55, s)); tufts.setMatrixAt(i, m4); });
    tufts.instanceMatrix.needsUpdate = true; tufts.visible = cover > 0.01;
    // Häuser fangen Feuer, wenn der Ring sie erreicht
    bldgs.forEach(b => { let ign = 1e9; for (let k = 0; k < FIRES.length; k++) if (R[k] > 0) { const dd = Math.hypot(b.x - FIRES[k][0], b.z - FIRES[k][1]); ign = Math.min(ign, FIRES[k][2] + dd / SPEED); }
      b.ign = ign; const k2 = smooth(ign + 1.0, ign + 5, T); b.fm.emissiveIntensity = k2 * 1.4 * flicker(T, b.x * 0.1); b.fm.color.setScalar(1 - 0.55 * k2); });
    // Fasernschnee: dicht beim Zurückkommen, danach ruhiger; bei Feuer steigen die Flocken (Hitze)
    snow.visible = back && id !== 'aerial';
    const heat = smooth(IGNITE, IGNITE + 4, T);
    updateFlakes(snow, T, lerp(2.2, -0.6, heat), lerp(1, 0.35, smooth(RETURN + 2.5, RETURN + 6, T)), [0.8, 0.4]);
    snow.material.color.set(heat > 0.5 ? '#ffd9b0' : '#fbf8f1');
    // Imbissfenster flackert (Fettbrand drinnen)
    glowM.emissiveIntensity = 2.2 * flicker(T, 5);
    // Feuerquellen: entlang der Ringe, in Kameranähe dicht
    const fs = [], ss = [];
    const cam = camera.position;
    FIRES.forEach((f, k) => { if (R[k] <= 0) return; const n = id === 'aerial' ? 18 : (k === 0 ? 40 : 0);
      for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2 + k; const rr = Math.max(0.5, R[k] - 1.5); const p = V3(f[0] + Math.cos(a) * rr, 0.4, f[1] + Math.sin(a) * rr);
        if (id !== 'aerial' && p.distanceTo(cam) > 70) continue;
        fs.push({type: 'flame', pos: p, r: id === 'aerial' ? 6 : 1.4, t0: f[2], size: id === 'aerial' ? 7 : 1.6, rise: id === 'aerial' ? 6 : 3, power: 1, share: 1}); }
      ss.push({type: 'smoke', pos: V3(f[0], 4, f[1]), r: Math.min(R[k], 40) * 0.6 + 2, t0: f[2] + 0.5, size: id === 'aerial' ? 30 : 10, rise: 6, col: [0.15, 0.13, 0.12], alpha: 0.65, share: k ? 1 : 2}); });
    bldgs.forEach(b => { if (T > b.ign + 2 && (id === 'aerial' ? ss.length < 40 : Math.hypot(b.x - cam.x, b.z - cam.z) < 90 && ss.length < 14)) ss.push({type: 'smoke', pos: V3(b.x, b.h, b.z), r: 4, t0: b.ign + 2, size: 14, rise: 5, col: [0.13, 0.11, 0.1], alpha: 0.6, share: 1});
      if (T > b.ign + 2.5 && fs.length < 160 && (id === 'aerial' || Math.hypot(b.x - cam.x, b.z - cam.z) < 70)) fs.push({type: 'flame', pos: V3(b.x, b.h + 1, b.z), r: 5, t0: b.ign + 2.5, size: id === 'aerial' ? 9 : 5, rise: 5, power: 0.9, share: 1}); });
    if (id !== 'aerial') fs.push({type: 'flame', pos: V3(IMB[0] - 0.4, 1.4, IMB[1]), r: 1.6, t0: 0, size: 1.4, rise: 2.5, power: 0.9, share: 2}); // aus dem Imbissfenster
    updateParticles(fire, fs, T, V3(0.6, 0, 0.3));
    updateParticles(smoke, ss, T, V3(3, 0, 1.2));
    const fk = T > IGNITE ? 1 : 0;
    fireL.position.set(IMB[0] - 2, 3, IMB[1] + Math.min(R[0], 30) * 0.5); fireL.intensity = fk * 2500 * flicker(T, 1) * (id === 'aerial' ? 0 : 1);
    // Himmel verdunkelt sich durch Rauch
    const dark = smooth(IGNITE + 2, 80, T);
    sun.intensity = lerp(2.4, 1.0, dark); sun.color.set(dark > 0.3 ? '#ffb070' : '#fff0dc'); hemi.intensity = lerp(0.9, 0.5, dark);
    scene.fog.color.set(dark > 0.2 ? '#8a7466' : '#d9dfe4'); scene.fog.near = id === 'aerial' ? 140 : lerp(80, 40, dark); scene.fog.far = id === 'aerial' ? 680 : lerp(600, 480, dark);
    sky.material.color.setScalar(lerp(1, 0.6, dark)); sky.material.color.r = lerp(1, 0.95, dark);
    // Menschen
    people.forEach(({p, x, z, ry, d}, i) => {
      const catchK = smooth(RETURN + 0.3 + d, RETURN + 1.2 + d, T);
      const flee = smooth(IGNITE + 1.0 + d, IGNITE + 2.0 + d, T);
      const run = T > IGNITE + 1 + d ? (T - IGNITE - 1 - d) : 0;
      p.position.set(x, 0.15, z + run * 4.2); p.rotation.y = flee > 0.5 ? 0 : ry;
      posePerson(p, {walk: T * 11, walkAmp: flee > 0.5 ? 1.4 : 0, holdUp: 0});
      if (flee < 0.5) { const u = p.userData; u.armL.rotation.x = -2.3 * catchK; u.armR.rotation.x = -2.1 * catchK; u.armL.userData.fore.rotation.x = -0.4 * catchK; u.head.rotation.x = -0.6 * catchK; }
      setCotton(p, false); p.visible = id !== 'aerial';
    });
    // Kamera
    camera.fov = 50;
    if (id === 'street_return') {
      const u = smooth(47, 58, T);
      camera.position.set(lerp(-1.5, -1.0, u) + noise1(T, 2) * 0.03, lerp(1.7, 1.75, u), lerp(24, 19, u)); camera.lookAt(lerp(1.5, 3.0, u), lerp(3.5, 2.4, u), -40);
    } else if (id === 'street_fire') {
      const flee = T > IGNITE + 1.5 ? (T - IGNITE - 1.5) : 0;
      const sh = T > IGNITE ? 0.04 : 0;
      camera.position.set(-2.0 + noise1(T * 8, 1) * sh, 1.7 + noise1(T * 8, 2) * sh + Math.abs(Math.sin(T * 7)) * 0.03 * (flee > 0 ? 1 : 0), 18 + flee * 6.0); camera.lookAt(3.5, 2.2, IMB[1]);
    } else { // aerial
      const u = smooth(68, 80, T);
      camera.position.set(lerp(-20, 40, u), lerp(40, 170, u), lerp(70, 190, u)); camera.lookAt(lerp(0, 0, u), 0, lerp(-30, -120, u));
    }
    camera.updateProjectionMatrix();
    sun.target.position.copy(camera.position).add(V3(0, -camera.position.y, -40)); sun.position.copy(sun.target.position).add(V3(-60, 90, 40));
  }};
}
