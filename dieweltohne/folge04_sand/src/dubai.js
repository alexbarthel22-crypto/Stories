// Dubai am Mittag aus dem Helikopter: Die Palmeninsel aus aufgeschüttetem Sand versinkt Wedel für Wedel,
// danach zerbröseln die Wolkenkratzer (Beton ohne Sand) zu riesigen Staubwolken. Glas gibt es schon keins mehr.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, easeIn, easeOut, noise1, canvasTex} from './lib.js';
import {skyMaterial} from './beach.js';
import {particles, updateParticles} from './fx.js';
import {TOWER_FALL} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const SUN = V3(0.35, 0.85, 0.4).normalize();
const SINK0 = 39.6; // Inselsand beginnt zu verschwinden

// Meer: türkis im Flachwasser, Wellen aus Sinussummen, Gischtflecken (foam-Uniforms)
function seaMat() {
  return new THREE.ShaderMaterial({
    uniforms: {time: {value: 0}, sunDir: {value: SUN}, foam: {value: new Float32Array(4 * 64)}, nFoam: {value: 0}},
    vertexShader: 'varying vec3 wp; void main(){ vec4 w = modelMatrix * vec4(position,1.); wp = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: `
      varying vec3 wp; uniform float time; uniform vec3 sunDir; uniform vec4 foam[64]; uniform int nFoam;
      float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
      float n2(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y); }
      vec2 g(vec2 p, vec2 d, float fr, float sp, float a){ float ph = dot(p, d)*fr + time*sp; return d * cos(ph) * fr * a; }
      void main(){
        vec2 p = wp.xz; vec2 s = vec2(0.0);
        s += g(p, normalize(vec2(0.3,1.0)), 0.06, 0.9, 1.2);
        s += g(p, normalize(vec2(-0.6,1.0)), 0.13, 1.4, 0.5);
        s += g(p, normalize(vec2(0.9,0.4)), 0.31, 2.1, 0.18);
        s += g(p, normalize(vec2(-0.2,-1.0)), 0.7, 3.0, 0.06);
        vec3 n = normalize(vec3(-s.x, 1.0, -s.y));
        vec3 v = normalize(cameraPosition - wp);
        float fres = 0.02 + 0.98 * pow(1.0 - max(dot(n, v), 0.0), 5.0);
        // Flachwasser um die Insel: türkis, weiter draußen tiefblau
        float shallow = 1.0 - smoothstep(250.0, 900.0, length(p - vec2(0.0, -300.0)));
        vec3 water = mix(vec3(0.03,0.22,0.36), vec3(0.18,0.62,0.62), shallow * 0.85);
        water *= 0.85 + 0.25 * n2(p * 0.02);
        vec3 r = reflect(-v, n); float ry = max(r.y, 0.0);
        vec3 skyC = mix(vec3(0.70,0.74,0.76), vec3(0.32,0.52,0.78), pow(ry, 0.5));
        vec3 col = mix(water * (0.6 + 0.4*max(dot(n, sunDir),0.0)), skyC, fres * 0.8);
        float spec = pow(max(dot(r, sunDir), 0.0), 300.0) * 6.0;
        col += vec3(1.0,0.95,0.85) * spec;
        // Gischt / aufgewühltes Wasser an versunkenen Stellen
        float f = 0.0;
        for (int i = 0; i < 64; i++) { if (i >= nFoam) break; vec4 q = foam[i];
          float d = length(p - q.xy) / q.z; f += q.w * smoothstep(1.0, 0.2, d) * (0.45 + 0.55 * n2(p * 0.09 + float(i) * 7.0 + time * 0.8)); }
        col = mix(col, vec3(0.93,0.95,0.94), clamp(f, 0.0, 0.92));
        col = mix(col, vec3(0.45,0.55,0.50), clamp(f, 0.0, 1.0) * 0.0);
        float fogk = 1.0 - exp(-length(cameraPosition - wp) * 0.00022);
        col = mix(col, vec3(0.86,0.83,0.76), fogk * 0.7);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(9000, 48, 24), skyMaterial(SUN)); sky.renderOrder = -10; scene.add(sky);
  scene.fog = new THREE.Fog('#dcd2bf', 1400, 7500);
  scene.add(new THREE.HemisphereLight('#dfe8f2', '#b59a72', 1.1));
  const sun = new THREE.DirectionalLight('#fff1d8', 2.6); sun.position.copy(SUN).multiplyScalar(1000); scene.add(sun);
  const sea = mesh(new THREE.PlaneGeometry(16000, 16000), seaMat(), 0, 0, 0, scene); sea.rotation.x = -Math.PI / 2;

  const sandM = mat('#e2cc9c', {roughness: 0.95}), roadM = mat('#5b5d61', {roughness: 0.8}), greenM = mat('#6f8f4a', {roughness: 0.9});
  // Inselsegmente: jedes Stück versinkt für sich (Wedel von der Spitze zum Stamm)
  const segs = []; const r = rng(17);
  const addSeg = (x, z, len, wid, ry, tSink, villas = true) => {
    const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; scene.add(g);
    mesh(new THREE.BoxGeometry(len, 8, wid), sandM, 0, -2, 0, g);                      // Sand, 2 m über Wasser
    mesh(new THREE.BoxGeometry(len, 0.3, wid * 0.16), roadM, 0, 2.05, 0, g);
    for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(len, 0.25, wid * 0.08), greenM, 0, 2.05, s * wid * 0.13, g);
    const seg = {g, tSink, len, wid, x, z, ry, tilt: [(r() - 0.5) * 0.3, (r() - 0.5) * 0.3], villas: []};
    if (villas) for (let k = 0; k < Math.floor(len / 22); k++) for (const s of [-1, 1]) {
      seg.villas.push({lx: -len / 2 + 11 + k * 22 + (r() - 0.5) * 4, lz: s * wid * 0.32, s, rot: (r() - 0.5) * 0.1, tilt: [(r() - 0.5) * 0.9, (r() - 0.5) * 0.9], dly: r() * 0.4, col: r()}); }
    segs.push(seg); return seg;
  };
  // Stamm
  for (let k = 0; k < 10; k++) addSeg(0, -720 + k * 70 + 35, 70, 90, Math.PI / 2, SINK0 + 3.6 + (9 - k) * 0.2);
  // 16 Wedel: 8 je Seite, leicht zur Spitze geneigt, je 6 Segmente
  for (let i = 0; i < 8; i++) for (const s of [-1, 1]) {
    const zb = -560 + i * 72, ang = s * (0.12 + i * 0.03), L = 300 + Math.sin(i / 7 * Math.PI) * 90;
    const n = 6, sl = L / n;
    for (let j = 0; j < n; j++) {
      const d = 60 + sl * (j + 0.5); const x = s * d * Math.cos(ang), z = zb + d * Math.sin(Math.abs(ang)) * 1;
      addSeg(x, z, sl + 1, 34, -s * Math.abs(ang), SINK0 + (n - 1 - j) * 0.42 + i * 0.16 + (s > 0 ? 0.08 : 0));
    }
  }
  // Krone (Ende des Stamms) und Sichelförmiger Wellenbrecher
  addSeg(0, 70, 140, 140, 0, SINK0 + 3.2);
  for (let k = 0; k < 44; k++) { const a = -2.5 + k / 43 * 5.0, R = 760; const x = Math.sin(a) * R, z = -300 + Math.cos(a) * R;
    addSeg(x, z, R * 5.0 / 43 + 2, 28, a, SINK0 + 0.4 + Math.abs(a) * 0.25 + r() * 0.2, false); }
  // Villen, Pools, Palmen als Instanzen (Matrix je Bild aus dem Segment berechnet)
  const nV = segs.reduce((a, s) => a + s.villas.length, 0);
  const vColors = ['#f3efe6', '#ece2cf', '#e9e9e4', '#f6eadb'];
  const villa = new THREE.InstancedMesh(new THREE.BoxGeometry(16, 7, 12), new THREE.MeshStandardMaterial({roughness: 0.6}), nV);
  const roof = new THREE.InstancedMesh(new THREE.BoxGeometry(17, 0.8, 13), mat('#c9a77a', {roughness: 0.7}), nV);
  const pool = new THREE.InstancedMesh(new THREE.BoxGeometry(9, 0.3, 5), new THREE.MeshStandardMaterial({color: '#3fc6d8', roughness: 0.1, emissive: '#0d4a55', emissiveIntensity: 0.4}), nV);
  const trunkI = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.4, 0.6, 9, 6), mat('#8a6a48'), nV);
  const crownI = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(3.2, 0), mat('#4f7a3a', {flatShading: true}), nV);
  { let i = 0; const c = new THREE.Color(); segs.forEach(s => s.villas.forEach(v => { villa.setColorAt(i++, c.set(vColors[Math.floor(v.col * 4)])); })); }
  scene.add(villa, roof, pool, trunkI, crownI);

  // Skyline an der Küste: Wolkenkratzer ohne Glas – nur Geschossplatten, Kern und Stützen
  const towers = []; const rt = rng(5);
  for (let k = 0; k < 34; k++) {
    const x = -1500 + k * 95 + (rt() - 0.5) * 50, z = -980 - rt() * 380, H = 130 + rt() * 230, W = 28 + rt() * 22;
    towers.push({x, z, H, W, tc: TOWER_FALL + rt() * 2.4, dur: 2.2 + rt() * 1.2});
  }
  towers.push({x: 260, z: -1150, H: 820, W: 85, tc: TOWER_FALL + 1.1, dur: 3.0, needle: true});
  const slabG = new THREE.BoxGeometry(1, 1, 1);
  let nSlab = 0; towers.forEach(t => { t.floors = Math.floor(t.H / (t.needle ? 9 : 7)); nSlab += t.floors; });
  const slabs = new THREE.InstancedMesh(slabG, mat('#c8c3b8', {roughness: 0.85}), nSlab);
  const cores = new THREE.InstancedMesh(slabG, mat('#9b968c', {roughness: 0.9}), towers.length);
  const cols = new THREE.InstancedMesh(slabG, mat('#b4aea3', {roughness: 0.9}), towers.length * 4);
  const darkI = new THREE.InstancedMesh(slabG, mat('#6a655c', {roughness: 1}), towers.length);   // dunkles Inneres zwischen den Platten
  const rubble = new THREE.InstancedMesh(new THREE.ConeGeometry(1, 1, 10), mat('#bfb39d', {roughness: 1}), towers.length);
  scene.add(slabs, cores, cols, darkI, rubble);
  const spire = mesh(new THREE.CylinderGeometry(0.5, 4, 120, 8), mat('#cfd3d6', {metalness: 0.6, roughness: 0.4}), 0, 0, 0, scene);
  // Wüste und Stadtboden hinter der Küste
  const desert = mesh(new THREE.PlaneGeometry(16000, 7000), mat('#d9c39a', {roughness: 1}), 0, 0.5, -1000 - 3500 + 300, scene); desert.rotation.x = -Math.PI / 2;
  const cityGround = mesh(new THREE.PlaneGeometry(3600, 700), mat('#b9ae9a', {roughness: 1}), 0, 0.8, -1250, scene); cityGround.rotation.x = -Math.PI / 2;
  const lowRise = new THREE.InstancedMesh(slabG, mat('#d8cfbf', {roughness: 0.9}), 260); { const m4 = new THREE.Matrix4(); const rr = rng(9);
    for (let i = 0; i < 260; i++) { const w = 20 + rr() * 30, h = 8 + rr() * 30; m4.compose(V3(-1800 + rr() * 3600, h / 2, -900 - rr() * 900), new THREE.Quaternion(), V3(w, h, w * (0.6 + rr()))); lowRise.setMatrixAt(i, m4); } }
  scene.add(lowRise);

  const dust = particles(4200, 'smoke'); scene.add(dust);
  const spray = particles(1400, 'smoke'); scene.add(spray);
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 5, 20000);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), one = V3(1, 1, 1);
  const segMat = new THREE.Matrix4(), loc = new THREE.Matrix4(), tmp = new THREE.Matrix4();

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.0;
    sea.material.uniforms.time.value = T;
    // Segmente versinken
    const foam = sea.material.uniforms.foam.value; let nf = 0;
    const sprays = [];
    segs.forEach(s => {
      const u = clamp((T - s.tSink) / 1.6);
      s.g.position.y = -16 * easeIn(u) - 2.5 * u;
      s.g.rotation.x = s.tilt[0] * u; s.g.rotation.z = s.tilt[1] * u;
      s.g.visible = u < 1;
      const a = T - s.tSink;
      if (a > -0.05 && a < 4.5 && nf < 64 && s.villas.length) { foam.set([s.x, s.z, s.len * 0.75 + 15, clamp(a * 2.5) * (1 - clamp((a - 1.5) / 3)) * 1.1], nf * 4); nf++; }
      if (a > 0 && a < 0.8 && s.villas.length && sprays.length < 30) sprays.push(s);
    });
    sea.material.uniforms.nFoam.value = nf;
    updateParticles(spray, sprays.length ? sprays.map(s => ({type: 'smoke', pos: V3(s.x, 2, s.z), r: s.len * 0.45, t0: s.tSink, t1: s.tSink + 0.5, size: 40, rise: 9, col: [0.92, 0.94, 0.95], alpha: 0.75, share: 1})) : [], T, V3(4, 0, 2));
    // Villen-Instanzen: folgen ihrem Segment, kippen zusätzlich
    let i = 0;
    segs.forEach(s => {
      s.g.updateMatrixWorld(); segMat.copy(s.g.matrixWorld);
      const u = clamp((T - s.tSink) / 1.6);
      s.villas.forEach(v => {
        const k = clamp((T - s.tSink - v.dly * 0.3) / 1.2);
        e.set(v.tilt[0] * k, v.rot, v.tilt[1] * k); q.setFromEuler(e);
        const vis = u < 1 ? 1 : 0;
        loc.compose(V3(v.lx, 5.5 - 4 * easeIn(k), v.lz), q, one); tmp.multiplyMatrices(segMat, loc); m4.copy(tmp); if (!vis) m4.makeScale(0, 0, 0); villa.setMatrixAt(i, m4);
        loc.compose(V3(v.lx, 9.3 - 4 * easeIn(k), v.lz), q, one); tmp.multiplyMatrices(segMat, loc); if (!vis) tmp.makeScale(0, 0, 0); roof.setMatrixAt(i, tmp);
        loc.compose(V3(v.lx + 2, 2.1, v.lz + v.s * -9.5), q, one); tmp.multiplyMatrices(segMat, loc); if (!vis) tmp.makeScale(0, 0, 0); pool.setMatrixAt(i, tmp);
        loc.compose(V3(v.lx - 8, 6.5, v.lz + v.s * -10), q, one); tmp.multiplyMatrices(segMat, loc); if (!vis) tmp.makeScale(0, 0, 0); trunkI.setMatrixAt(i, tmp);
        loc.compose(V3(v.lx - 8, 11.5, v.lz + v.s * -10), q, V3(1, 0.7, 1)); tmp.multiplyMatrices(segMat, loc); if (!vis) tmp.makeScale(0, 0, 0); crownI.setMatrixAt(i, tmp);
        i++;
      });
    });
    for (const im of [villa, roof, pool, trunkI, crownI]) im.instanceMatrix.needsUpdate = true;
    // Türme: Front fällt von oben nach unten, Platten darüber stapeln sich auf der Front
    let si = 0; const dustSrc = [];
    towers.forEach((t, ti) => {
      const u = clamp((T - t.tc) / t.dur), f = t.H * (1 - easeIn(u)); // Höhe der Einsturzfront
      const shrink = t.needle ? 1 : 1;
      for (let k = 0; k < t.floors; k++) {
        const y0 = (k + 1) * t.H / t.floors; let y = y0, vis = 1;
        if (y0 > f) { const above = k - Math.floor(f / (t.H / t.floors)); y = f + above * 0.9; vis = above < 14 ? 1 : 0; }
        const w = t.needle ? t.W * (1 - 0.82 * (y0 / t.H)) * (1 - 0.05 * (k % 6 === 0)) : t.W;
        if (!vis || u >= 1) m4.makeScale(0, 0, 0); else m4.compose(V3(t.x + (y0 > f ? noise1(T * 6, k) * 1.5 : 0), y, t.z), q.identity(), V3(w * shrink, 1.8, w));
        slabs.setMatrixAt(si++, m4);
      }
      const hh = Math.max(0.01, f);
      m4.compose(V3(t.x, hh / 2, t.z), q.identity(), V3(t.W * (t.needle ? 0.3 : 0.35), hh, t.W * (t.needle ? 0.3 : 0.35))); cores.setMatrixAt(ti, u >= 1 ? m4.makeScale(0, 0, 0) : m4);
      m4.compose(V3(t.x, hh / 2 - 0.5, t.z), q.identity(), V3(t.W * 0.94, hh, t.W * 0.94)); darkI.setMatrixAt(ti, u >= 1 || t.needle ? m4.makeScale(0, 0, 0) : m4);
      for (let c = 0; c < 4; c++) { const ox = (c & 1 ? 0.5 : -0.5) * t.W * (t.needle ? 0.5 : 0.98), oz = (c & 2 ? 0.5 : -0.5) * t.W * (t.needle ? 0.5 : 0.98);
        m4.compose(V3(t.x + ox, hh / 2, t.z + oz), q.identity(), V3(1.6, hh, 1.6)); cols.setMatrixAt(ti * 4 + c, u >= 1 || t.needle ? m4.makeScale(0, 0, 0) : m4); }
      const rh = t.H * 0.12 * smooth(0, 1, u), rw = t.W * (0.8 + 1.2 * u);
      m4.compose(V3(t.x, rh / 2, t.z), q.identity(), V3(rw, Math.max(0.01, rh), rw)); rubble.setMatrixAt(ti, m4);
      if (T > t.tc - 0.05) {
        const sc = t.needle ? 1.8 : 1;
        dustSrc.push({type: 'smoke', pos: V3(t.x, 10, t.z), r: t.W * 2.2 * sc, t0: t.tc, size: 260 * sc, rise: 14, col: [0.80, 0.72, 0.58], alpha: 0.85, share: t.needle ? 3 : 1});
        if (u < 1) dustSrc.push({type: 'smoke', pos: V3(t.x, f, t.z), r: t.W * 1.1 * sc, t0: t.tc, t1: t.tc + t.dur, size: 160 * sc, rise: 2, col: [0.86, 0.79, 0.66], alpha: 0.8, share: t.needle ? 2 : 0.6});
      }
      if (t.needle) { spire.position.set(t.x, f + 60 - 30 * u, t.z); spire.rotation.z = 0.5 * easeIn(u); spire.visible = u < 0.95; }
    });
    for (const im of [slabs, cores, cols, darkI, rubble]) im.instanceMatrix.needsUpdate = true;
    updateParticles(dust, dustSrc, T, V3(14, 0, 6));
    // Kamera: Helikopter kreist langsam, leichte Unruhe
    const t = T - shot.t0, a = lerp(0.62, 0.36, smooth(0, 8, t)), R = lerp(1050, 950, t / 8), sh = 1 + (T > TOWER_FALL ? 2 : 0);
    camera.position.set(Math.sin(a) * R + noise1(T * 1.3, 1) * 3 * sh, lerp(430, 380, t / 8) + noise1(T * 1.1, 2) * 3 * sh, -250 + Math.cos(a) * R);
    camera.lookAt(lerp(-40, 40, t / 8), lerp(-40, 70, smooth(1.5, 6, t)), lerp(-420, -640, smooth(1.5, 6, t)));
    camera.updateProjectionMatrix();
  }};
}
