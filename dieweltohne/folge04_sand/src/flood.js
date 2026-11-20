// Niederländische Küste am Mittag: Die Dünen (Sand) verschwinden, die Nordsee liegt höher als das Land
// und rollt als Wasserwand über Polder, Straße und Dorf. Der Kirchturm kippt.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, easeIn, easeOut, noise1, canvasTex} from './lib.js';
import {skyMaterial} from './beach.js';
import {particles, updateParticles} from './fx.js';
import {DUNE_BREAK} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const SUN = V3(-0.3, 0.75, -0.6).normalize();
const PL = -5;                 // Polderhöhe (unter dem Meeresspiegel 0)
const LEVEL = PL + 4.2;        // Wasserstand hinter der Front
// Position der Wasserfront (Abstand vom Dünenrand in Metern)
export function frontX(T) { const t = T - DUNE_BREAK - 0.35; if (t <= 0) return 0; return 260 * t - 9 * t * t; }

function noiseGLSL() {
  return `float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
  float n2(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y); }
  float fbm(vec2 p){ return n2(p)*0.5 + n2(p*2.1)*0.25 + n2(p*4.3)*0.125; }`;
}
// Nordsee: grau-grün, kurze Wellen, Schaumkronen
function seaMat() {
  return new THREE.ShaderMaterial({uniforms: {time: {value: 0}, sunDir: {value: SUN}},
    vertexShader: 'varying vec3 wp; void main(){ vec4 w = modelMatrix * vec4(position,1.); wp = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: `varying vec3 wp; uniform float time; uniform vec3 sunDir; ${noiseGLSL()}
      vec2 g(vec2 p, vec2 d, float fr, float sp, float a){ float ph = dot(p, d)*fr + time*sp; return d * cos(ph) * fr * a; }
      void main(){ vec2 p = wp.xz; vec2 s = vec2(0.0);
        s += g(p, normalize(vec2(1.0,0.2)), 0.09, 1.3, 1.4); s += g(p, normalize(vec2(1.0,-0.5)), 0.21, 2.0, 0.5); s += g(p, normalize(vec2(0.6,0.8)), 0.5, 3.0, 0.15);
        vec3 n = normalize(vec3(-s.x, 1.0, -s.y)); vec3 v = normalize(cameraPosition - wp);
        float fres = 0.02 + 0.98 * pow(1.0 - max(dot(n, v), 0.0), 5.0);
        vec3 water = vec3(0.10,0.22,0.24) * (0.8 + 0.3 * fbm(p * 0.01));
        vec3 r = reflect(-v, n); vec3 skyC = mix(vec3(0.72,0.78,0.84), vec3(0.36,0.52,0.72), pow(max(r.y,0.0), 0.5));
        vec3 col = mix(water, skyC, fres * 0.7) + vec3(1.0,0.96,0.9) * pow(max(dot(r, sunDir), 0.0), 250.0) * 3.0;
        // Schaumkronen und Brandung am Strand (x nahe 0)
        float wc = smoothstep(0.78, 0.9, fbm(p * 0.035 + vec2(time * 0.15, 0.0))) * 0.6;
        float surf = smoothstep(-90.0, -5.0, wp.x) * (0.5 + 0.5 * sin(wp.x * 0.25 + time * 2.2 + fbm(p*0.05)*4.0));
        col = mix(col, vec3(0.92,0.94,0.94), clamp(wc + surf * 0.55, 0.0, 0.9));
        float fogk = 1.0 - exp(-length(cameraPosition - wp) * 0.00025); col = mix(col, vec3(0.80,0.84,0.88), fogk);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`});
}
// Flutwasser über dem Polder: endet an der Front, dort Wasserwand mit Gischt
function floodMat() {
  return new THREE.ShaderMaterial({uniforms: {time: {value: 0}, front: {value: 0}, sunDir: {value: SUN}}, transparent: false,
    vertexShader: `uniform float front, time; varying vec3 wp; varying float dfront; ${noiseGLSL()}
      void main(){ vec4 w = modelMatrix * vec4(position,1.); float f = front + 0.5 * (sin(w.z * 0.011) * 0.5 + sin(w.z * 0.029 + 2.0) * 0.3 + sin(w.z * 0.067 + 4.0) * 0.2) * 80.0;
        float d = f - w.x; dfront = d;
        float wall = d > 0.0 ? (1.0 - exp(-d / 6.0)) * exp(-d / 40.0) * 14.0 * clamp(1.3 - (front - 220.0) / 1600.0, 0.45, 1.0) : 0.0;
        w.y = ${LEVEL.toFixed(2)} + wall + sin(w.x * 0.08 - time * 4.0 + w.z * 0.03) * 0.5 + (d < 0.0 ? -20.0 : 0.0);
        wp = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform float time; uniform vec3 sunDir; varying vec3 wp; varying float dfront; ${noiseGLSL()}
      void main(){ if (dfront < 0.0) discard;
        vec3 water = mix(vec3(0.46,0.34,0.17), vec3(0.24,0.19,0.11), smoothstep(0.0, 600.0, dfront)) * (0.75 + 0.4 * fbm(vec2(wp.x * 0.012 - time * 1.2, wp.z * 0.05)));
        float foam = smoothstep(55.0, 0.0, dfront) * (0.6 + 0.4 * fbm(wp.xz * 0.09 - vec2(time * 2.5, 0.0)));
        foam += smoothstep(0.62, 0.8, fbm(vec2(wp.x * 0.015 - time * 1.6, wp.z * 0.08))) * 0.55 * (1.0 - smoothstep(300.0, 900.0, dfront) * 0.5);
        vec3 col = mix(water, vec3(0.90,0.90,0.86), clamp(foam, 0.0, 0.95));
        col *= 0.75 + 0.35 * max(dot(normalize(cross(dFdx(wp), dFdy(wp))) * -1.0, sunDir), 0.0);
        float fogk = 1.0 - exp(-length(cameraPosition - wp) * 0.00025); col = mix(col, vec3(0.80,0.84,0.88), fogk);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`});
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(9000, 48, 24), skyMaterial(SUN)); sky.renderOrder = -10; scene.add(sky);
  scene.fog = new THREE.Fog('#cdd7e0', 900, 6000);
  scene.add(new THREE.HemisphereLight('#dfe8f2', '#6f7a55', 1.15));
  const sun = new THREE.DirectionalLight('#fff3dc', 2.4); sun.position.copy(SUN).multiplyScalar(1000); scene.add(sun);
  const sea = mesh(new THREE.PlaneGeometry(8000, 12000), seaMat(), -4000 - 20, 0, 0, scene); sea.rotation.x = -Math.PI / 2;
  // Polder: Felder mit Gräben
  const fieldT = canvasTex(1024, 1024, (g, w, h) => { const r = rng(3);
    for (let y = 0; y < h; y += 64) for (let x = 0; x < w; x += 128) { const c = ['#6f9a45', '#7da552', '#5f8c3c', '#93ad5a', '#8a9e48', '#6b9440'][Math.floor(r() * 6)]; g.fillStyle = c; g.fillRect(x, y, 128, 64);
      for (let k = 0; k < 40; k++) { g.fillStyle = `rgba(0,0,0,${r() * 0.06})`; g.fillRect(x + r() * 128, y + r() * 64, 6, 2); } }
    g.strokeStyle = '#4b6f7c'; g.lineWidth = 3; for (let y = 0; y <= h; y += 64) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
    g.lineWidth = 2; for (let x = 0; x <= w; x += 128) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); } });
  fieldT.wrapS = fieldT.wrapT = THREE.RepeatWrapping; fieldT.repeat.set(6, 10);
  const polder = mesh(new THREE.PlaneGeometry(4000, 8000), new THREE.MeshStandardMaterial({map: fieldT, roughness: 1}), 2000 + 0, PL, 0, scene); polder.rotation.x = -Math.PI / 2;
  // Deich-Unterbau unter den Dünen (Klei, bleibt) und Dünengürtel als Höhenfeld
  const duneW = 220, duneGeo = new THREE.PlaneGeometry(duneW, 8000, 60, 600); duneGeo.rotateX(-Math.PI / 2);
  { const p = duneGeo.attributes.position; const r = rng(4); for (let i = 0; i < p.count; i++) { const x = p.getX(i) + duneW / 2, z = p.getZ(i);
      const prof = Math.sin(clamp(x / duneW) * Math.PI); const hgt = PL + (prof * (26 + 10 * Math.sin(z * 0.013) + 7 * Math.sin(z * 0.041 + 1) + 5 * Math.sin(x * 0.07 + z * 0.023) + 3 * r())) + (x < 40 ? lerp(5, 0, x / 40) * 0 : 0);
      p.setY(i, Math.max(hgt, x < 30 ? lerp(-1.5, PL + 6, x / 30) : hgt)); } duneGeo.computeVertexNormals(); }
  const duneT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#d9c79c'; g.fillRect(0, 0, w, h); const r = rng(8);
    for (let i = 0; i < 2600; i++) { const x = r() * w, y = r() * h; g.strokeStyle = `rgba(${90 + r() * 40},${120 + r() * 30},${60 + r() * 20},${0.35 + r() * 0.4})`; g.lineWidth = 1.2; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (r() - 0.5) * 6, y - 5 - r() * 8); g.stroke(); }
    for (let i = 0; i < 4000; i++) { g.fillStyle = `rgba(255,250,230,${r() * 0.2})`; g.fillRect(r() * w, r() * h, 2, 2); } });
  duneT.wrapS = duneT.wrapT = THREE.RepeatWrapping; duneT.repeat.set(4, 140);
  const dunes = mesh(duneGeo, new THREE.MeshStandardMaterial({map: duneT, roughness: 1}), duneW / 2, 0, 0, scene);
  const beach = mesh(new THREE.PlaneGeometry(60, 8000), mat('#e2d2aa', {roughness: 1}), -20, -0.4, 0, scene); beach.rotation.x = -Math.PI / 2; beach.rotation.y = 0;
  const clay = mesh(new THREE.PlaneGeometry(duneW + 60, 8000), mat('#5d5547', {roughness: 1}), duneW / 2 - 20, PL - 0.05, 0, scene); clay.rotation.x = -Math.PI / 2; // freigelegter Boden
  // Flutwasser
  const floodGeo = new THREE.PlaneGeometry(3600, 6000, 240, 240); floodGeo.rotateX(-Math.PI / 2);
  const flood = new THREE.Mesh(floodGeo, floodMat()); flood.position.set(1800 - 20, 0, 0); flood.frustumCulled = false; scene.add(flood);
  // Straße mit Autos, Kühe, Bäume, Höfe
  const X0 = duneW; // Polder beginnt hier
  const road = mesh(new THREE.PlaneGeometry(10, 8000), mat('#4a4c50', {roughness: 0.9}), X0 + 330, PL + 0.05, 0, scene); road.rotation.x = -Math.PI / 2;
  const r = rng(11);
  const cars = []; const carCols = ['#c8102e', '#f2f2f2', '#2b5fa8', '#1d1d1f', '#e5b31b', '#8a9099'];
  for (let i = 0; i < 14; i++) { const g = new THREE.Group(); const c = carCols[i % 6]; mesh(new THREE.BoxGeometry(2, 1.2, 4.4), mat(c, {metalness: 0.4, roughness: 0.4}), 0, 0.6, 0, g); mesh(new THREE.BoxGeometry(1.8, 0.7, 2.2), mat('#22262c', {roughness: 0.2}), 0, 1.45, -0.2, g);
    g.userData = {z0: -900 + i * 130 + r() * 40, v: (i % 2 ? 1 : -1) * (18 + r() * 6), lane: i % 2 ? 2 : -2, sp: r() * 6}; scene.add(g); cars.push(g); }
  const cowGeo = new THREE.BoxGeometry(1.0, 1.4, 2.4), cows = new THREE.InstancedMesh(cowGeo, new THREE.MeshStandardMaterial({roughness: 0.9}), 90); scene.add(cows);
  const cowPos = []; { const c = new THREE.Color(); for (let i = 0; i < 90; i++) { cowPos.push([X0 + 120 + r() * 900, -700 + r() * 1400, r() * 6]); cows.setColorAt(i, c.set(r() < 0.6 ? '#f1efe8' : '#222')); } }
  const treeG = new THREE.IcosahedronGeometry(5, 0), trees = new THREE.InstancedMesh(treeG, mat('#45682f', {flatShading: true, roughness: 0.9}), 180); scene.add(trees);
  const treePos = []; for (let i = 0; i < 180; i++) { const along = i < 120; treePos.push(along ? [X0 + 345 + (i % 2) * -30, -1500 + (i >> 1) * 50, 0] : [X0 + 200 + r() * 1400, -1500 + r() * 3000, 0]); }
  // Windmühlen: klassische Mühlen und moderne Windräder
  const mills = []; for (const [x, z] of [[X0 + 230, -200], [X0 + 520, 360], [X0 + 900, -380]]) {
    const g = new THREE.Group(); g.position.set(x, PL, z); scene.add(g);
    mesh(new THREE.CylinderGeometry(4, 7, 24, 8), mat('#5a4636', {roughness: 0.9}), 0, 12, 0, g); mesh(new THREE.ConeGeometry(5, 7, 8), mat('#3b3f44'), 0, 27, 0, g);
    const hub = new THREE.Group(); hub.position.set(0, 25, 5.5); hub.rotation.y = 0; g.add(hub);
    for (let k = 0; k < 4; k++) { const arm = new THREE.Group(); arm.rotation.z = k * Math.PI / 2; hub.add(arm); mesh(new THREE.BoxGeometry(2.6, 15, 0.3), mat('#e9e2d0', {roughness: 0.9}), 0, 8, 0, arm); }
    g.rotation.y = -0.9; mills.push({g, hub}); }
  const turbines = []; for (let i = 0; i < 7; i++) { const g = new THREE.Group(); g.position.set(X0 + 1600 + i * 220, PL, -1300 + i * 380); scene.add(g);
    mesh(new THREE.CylinderGeometry(1.6, 2.6, 100, 10), mat('#e7e9ec'), 0, 50, 0, g); const hub = new THREE.Group(); hub.position.set(0, 100, 3); g.add(hub);
    for (let k = 0; k < 3; k++) { const arm = new THREE.Group(); arm.rotation.z = k * 2.094; hub.add(arm); mesh(new THREE.BoxGeometry(2.4, 50, 0.6), mat('#eef0f2'), 0, 25, 0, arm); }
    g.rotation.y = -0.9; turbines.push(hub); }
  // Dorf: Backsteinhäuser mit Satteldach, Kirche mit Turm
  const VX = X0 + 700, VZ = 80; const houses = [];
  const brick = ['#8b3e2f', '#9a4b34', '#7d3a2c', '#a55a3e'];
  for (let i = 0; i < 60; i++) { const g = new THREE.Group(); const x = VX + (r() - 0.5) * 360, z = VZ + (r() - 0.5) * 420; if (Math.hypot(x - VX, z - VZ) < 30) continue;
    g.position.set(x, PL, z); g.rotation.y = Math.round(r()) * Math.PI / 2 + (r() - 0.5) * 0.1; scene.add(g);
    const w = 8 + r() * 4, d = 10 + r() * 5, hh = 6 + r() * 3;
    const body = mesh(new THREE.BoxGeometry(w, hh, d), mat(brick[i % 4], {roughness: 0.9}), 0, hh / 2, 0, g);
    const roofG = new THREE.CylinderGeometry(0.01, w * 0.62, 4.5, 4, 1); roofG.rotateY(Math.PI / 4); const rf = mesh(roofG, mat(r() < 0.5 ? '#3a3d42' : '#8c3a26', {roughness: 0.8}), 0, hh + 2.25, 0, g); rf.scale.set(1, 1, d / w * 1.0);
    for (const s of [-1, 1]) for (let k = 0; k < 3; k++) mesh(new THREE.PlaneGeometry(1.3, 1.6), mat('#141516'), s * (w / 2 + 0.02), hh * 0.55, -d / 3 + k * d / 3, g).rotation.y = s * Math.PI / 2; // leere Fensterlöcher
    houses.push({g, x, z, hh, tilt: [(r() - 0.5) * 0.8, (r() - 0.5) * 0.8], sink: 2 + r() * 2}); }
  const church = new THREE.Group(); church.position.set(VX, PL, VZ); scene.add(church);
  mesh(new THREE.BoxGeometry(14, 12, 30), mat('#8a4632', {roughness: 0.9}), 0, 6, 8, church);
  const nave = new THREE.CylinderGeometry(0.01, 10.5, 7, 4, 1); nave.rotateY(Math.PI / 4); mesh(nave, mat('#3a3d42'), 0, 15.5, 8, church).scale.set(1, 1, 2.1);
  const tower = new THREE.Group(); tower.position.set(0, 0, -9); church.add(tower);
  mesh(new THREE.BoxGeometry(8, 34, 8), mat('#8f4a33', {roughness: 0.9}), 0, 17, 0, tower); mesh(new THREE.ConeGeometry(6.2, 22, 4), mat('#3b4a44', {metalness: 0.3}), 0, 45, 0, tower).rotation.y = Math.PI / 4;
  mesh(new THREE.PlaneGeometry(4, 4), mat('#e8e2cf'), 0, 26, 4.02, tower);
  // Partikel: Sand-Staub der Dünen, Gischt an der Front, Ziegelstaub
  const dust = particles(2200, 'smoke'); scene.add(dust);
  const spray = particles(3600, 'smoke'); scene.add(spray);
  const bdust = particles(900, 'smoke'); scene.add(bdust);
  const camera = new THREE.PerspectiveCamera(52, 1080 / 1920, 2, 20000);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
  const fbmJS = z => 0.5 * (Math.sin(z * 0.011) * 0.5 + Math.sin(z * 0.029 + 2) * 0.3 + Math.sin(z * 0.067 + 4) * 0.2); // grobe Nachbildung der Frontkrümmung
  const wet = (x, T) => x - X0 < frontX(T) ? 1 : 0;
  const arrival = x => { // Zeit, zu der die Front die Stelle x erreicht
    for (let T = DUNE_BREAK; T < 70; T += 0.02) if (frontX(T) >= x - X0) return T; return 99; };

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.0;
    sea.material.uniforms.time.value = T; flood.material.uniforms.time.value = T;
    const F = frontX(T); flood.material.uniforms.front.value = X0 - 20 + F + 20; flood.visible = T > DUNE_BREAK + 0.3;
    flood.material.uniforms.front.value = F + X0 - (1800 - 20) - (X0 - 1800 + 20) ; // in Weltkoordinaten (Shader nutzt w.x)
    flood.material.uniforms.front.value = X0 + F;
    // Dünen verschwinden: sacken weg und lösen sich in Staub auf
    const dk = smooth(DUNE_BREAK, DUNE_BREAK + 0.5, T);
    dunes.scale.y = 1 - dk; dunes.position.y = PL * dk; dunes.visible = dk < 0.99; beach.visible = T < DUNE_BREAK + 0.1;
    updateParticles(dust, T > DUNE_BREAK - 0.05 ? Array.from({length: 12}, (_, i) => ({type: 'smoke', pos: V3(duneW * 0.5, PL + 8, -1500 + i * 250), r: 120, t0: DUNE_BREAK, t1: DUNE_BREAK + 0.5, size: 90, rise: 6, col: [0.86, 0.78, 0.62], alpha: 0.7, share: 1})) : [], T, V3(10, 0, 0));
    // Gischt an der Front
    const sp = [];
    if (T > DUNE_BREAK + 0.3) for (let i = 0; i < 80; i++) { const z = -1400 + i * 35 + Math.sin(i * 7.1) * 15, back = Math.abs(Math.sin(i * 2.7)) * 50; sp.push({type: 'smoke', pos: V3(X0 + F - 4 - back + fbmJS(z) * 80, LEVEL + 5 + back * 0.05, z), r: 22, t0: DUNE_BREAK + 0.3, size: 22 + 10 * Math.abs(Math.sin(i * 3.3)), rise: 6, col: [0.9, 0.88, 0.82], alpha: 0.32, share: 1}); }
    updateParticles(spray, sp, T, V3(25, 0, 0));
    // Mühlen und Windräder drehen sich
    mills.forEach((m, i) => { m.hub.rotation.z = T * 0.9 + i; const a = arrival(m.g.position.x); const k = smooth(a + 0.3, a + 2.5, T); m.g.rotation.z = 0.5 * easeIn(k) * (i % 2 ? 1 : -1); m.g.position.y = PL - 3 * k; });
    turbines.forEach((h, i) => { h.rotation.z = T * 0.7 + i * 2; });
    // Autos: fahren, werden von der Wasserwand erfasst und mitgerissen
    cars.forEach((c, i) => { const u = c.userData; const a = arrival(X0 + 330); const k = clamp((T - a) / 2.2);
      const z = u.z0 + u.v * (Math.min(T, a) - 47) ; c.position.set(X0 + 330 + u.lane + 90 * easeOut(k) + noise1(T * 3, i) * k * 2, PL + 0.1 + (LEVEL - PL - 0.4) * Math.min(1, k * 3) * 0.6, z + k * 20 * (i % 2 ? 1 : -1));
      c.rotation.set(k * 0.6 * (i % 2 ? 1 : -1), (u.v > 0 ? 0 : Math.PI) + k * 2.2 * (i % 3 - 1), k * 0.4); c.visible = k < 1; });
    // Kühe verschwinden im Wasser
    cowPos.forEach(([x, z, ph], i) => { const w = wet(x, T); e.set(0, ph, w ? 1.2 : 0); q.setFromEuler(e);
      m4.compose(V3(x, w ? LEVEL - 1.2 : PL + 0.75, z), q, V3(1, 1, 1)); cows.setMatrixAt(i, m4); });
    cows.instanceMatrix.needsUpdate = true;
    treePos.forEach(([x, z], i) => { const a = arrival(x); const k = smooth(a, a + 1.5, T) * (i % 3 === 0 ? 1 : 0.3); e.set(0, 0, 1.2 * k); q.setFromEuler(e);
      m4.compose(V3(x, PL + 7 - 3 * k, z), q, V3(1, 1.4, 1)); trees.setMatrixAt(i, m4); });
    trees.instanceMatrix.needsUpdate = true;
    // Häuser: die Welle reißt Wände ein (Mörtel ohne Sand hält nicht)
    const bd = [];
    houses.forEach((h, i) => { const a = arrival(h.x); const k = smooth(a + 0.1, a + 1.6, T);
      h.g.rotation.x = h.tilt[0] * k; h.g.rotation.z = h.tilt[1] * k; h.g.position.y = PL - h.sink * k; h.g.scale.y = 1 - 0.55 * easeIn(k);
      if (T > a && bd.length < 16 && T < a + 2.5) bd.push({type: 'smoke', pos: V3(h.x, PL + 5, h.z), r: 8, t0: a + 0.1, t1: a + 1, size: 18, rise: 3, col: [0.62, 0.42, 0.33], alpha: 0.6, share: 1}); });
    // Kirchturm kippt um ~55,5
    const ck = easeIn(clamp((T - 55.3) / 1.5)); tower.rotation.x = ck * 1.35; tower.position.y = -2 * ck;
    if (T > 55.2) bd.push({type: 'smoke', pos: V3(VX, PL + 10, VZ - 12), r: 14, t0: 55.3, size: 32, rise: 4, col: [0.6, 0.45, 0.36], alpha: 0.7, share: 2});
    updateParticles(bdust, bd, T, V3(8, 0, 0));
    // Kamera: Drohne über dem Meer, schaut ins Land, fährt langsam vor
    const t = T - shot.t0, u = smooth(0, 10, t), sh = T > DUNE_BREAK && T < DUNE_BREAK + 1.2 ? 1.5 : 0.3;
    camera.position.set(lerp(-320, -120, u) + noise1(T * 1.4, 1) * sh, lerp(210, 170, u) + noise1(T * 1.2, 2) * sh, lerp(260, 160, u));
    camera.lookAt(lerp(520, 760, u), lerp(-40, -25, u), lerp(-20, 40, u));
    camera.updateProjectionMatrix();
  }};
}
