// Die Erde bei Nacht über der Arktis: rote Flugbahnen steigen aus Nordamerika auf und ziehen über den Pol nach Osten.
// So zeigt es das Frühwarnsystem – berechnet aus einem Fehler.
import {THREE, rng, clamp, smooth, lerp, noise1, canvasTex} from './lib.js';
import {COUNTER, FLASH0} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const D = Math.PI / 180;
const dirOf = (lat, lon) => V3(Math.cos(lat * D) * Math.cos(lon * D), Math.sin(lat * D), -Math.cos(lat * D) * Math.sin(lon * D));

const LAUNCH = [[47.5, -111.3], [46.4, -104.6], [41.2, -104.9], [48.4, -101.4], [44.1, -103.2]];
const TARGET = [[55.7, 37.6], [59.9, 30.3], [56.8, 60.6], [53.2, 50.1], [55.0, 82.9]];
const T0 = 66; // Beginn der Einstellung (Videozeit)
// Gegenschlag: Startgebiete in Russland -> Ziele in Nordamerika und Europa
const C_LAUNCH = [[56.0, 45.0], [52.5, 55.5], [57.5, 65.0], [51.0, 84.0], [62.0, 40.5], [54.5, 73.0], [58.5, 50.0], [53.5, 60.0], [55.5, 38.0], [60.5, 56.5], [52.0, 45.0]];
const C_TARGET = [[40.7, -74.0], [38.9, -77.0], [41.9, -87.6], [34.0, -118.2], [47.6, -122.3], [29.8, -95.4], [51.5, -0.1], [48.9, 2.3], [52.5, 13.4], [41.9, 12.5], [50.8, 4.4]];
// Einschläge (Reihenfolge der Blitze ab FLASH0)
const CITIES = [[55.7, 37.6], [40.7, -74.0], [51.5, -0.1], [38.9, -77.0], [52.5, 13.4], [59.9, 30.3], [41.9, -87.6], [48.9, 2.3], [56.8, 60.6], [34.0, -118.2], [50.8, 4.4],
  [53.2, 50.1], [47.6, -122.3], [41.9, 12.5], [55.0, 82.9], [29.8, -95.4], [48.1, 11.6], [42.4, -71.1], [53.5, 10.0], [55.8, 49.1], [39.9, -75.2], [40.4, -3.7], [33.7, -84.4],
  [50.1, 8.7], [43.7, -79.4], [45.5, 9.2], [37.8, -122.4], [56.3, 44.0], [52.4, 4.9], [32.8, -96.8]];
const NC = CITIES.length;

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#010205');
  const img = new Image(); img.src = '../tex/earth_night.jpg'; await img.decode();
  const tex = new THREE.Texture(img); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
  const cDir = CITIES.map(([la, lo]) => dirOf(la, lo)), cAge = new Array(NC).fill(-1);
  const earthMat = new THREE.ShaderMaterial({uniforms: {map: {value: tex}, cDir: {value: cDir}, cAge: {value: cAge}},
    vertexShader: 'varying vec2 vUv; varying vec3 vN; varying vec3 vV; varying vec3 vP; void main(){ vUv = uv; vP = normalize(position); vN = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(position,1.); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }',
    fragmentShader: `uniform sampler2D map; uniform vec3 cDir[${NC}]; uniform float cAge[${NC}]; varying vec2 vUv; varying vec3 vN; varying vec3 vV; varying vec3 vP;
      void main(){ vec3 c = texture2D(map, vUv).rgb; float f = pow(1.0 - max(dot(vN, vV), 0.0), 2.5);
        float dark = 1.0; vec3 ember = vec3(0.0);
        for (int i = 0; i < ${NC}; i++) { float ag = cAge[i]; if (ag < 0.0) continue;
          float d = acos(clamp(dot(vP, cDir[i]), -1.0, 1.0)) * 57.2958;
          float rad = 3.0 + 4.5 * smoothstep(0.0, 3.0, ag);
          dark *= mix(1.0, 0.06, smoothstep(rad, rad * 0.45, d) * smoothstep(0.0, 0.25, ag));
          ember += vec3(1.0, 0.38, 0.08) * exp(-d * d / (0.35 + ag * 1.2)) * (0.9 + 0.3 * smoothstep(0.0, 0.3, ag)) * (0.55 + 0.45 * exp(-ag * 0.8)); }
        gl_FragColor = vec4(c * 1.35 * dark + vec3(0.006,0.01,0.02) + vec3(0.05,0.09,0.2) * f + ember, 1.0);
        #include <colorspace_fragment>
      }`});
  const earth = new THREE.Mesh(new THREE.SphereGeometry(1, 160, 120), earthMat); scene.add(earth);
  const atm = new THREE.Mesh(new THREE.SphereGeometry(1.035, 64, 48), new THREE.ShaderMaterial({transparent: true, side: THREE.BackSide, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: 'varying vec3 n; varying vec3 v; void main(){ n=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.); v=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }',
    fragmentShader: 'varying vec3 n; varying vec3 v; void main(){ float f=pow(1.0-abs(dot(n,v)),3.0); gl_FragColor=vec4(0.25,0.4,0.9,1.0)*f*0.9; }'}));
  scene.add(atm);
  // Sterne
  { const r = rng(12), sp = new Float32Array(2500 * 3);
    for (let i = 0; i < 2500; i++) { const v = V3(r() - 0.5, r() - 0.5, r() - 0.5).normalize().multiplyScalar(40); sp.set([v.x, v.y, v.z], i * 3); }
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(sp, 3));
    scene.add(new THREE.Points(sg, new THREE.PointsMaterial({color: '#ffffff', size: 0.04, transparent: true, opacity: 0.7}))); }

  const glowTex = canvasTex(128, 128, (g, w) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,240,220,1)'); gr.addColorStop(0.25, 'rgba(255,90,60,0.7)'); gr.addColorStop(1, 'rgba(255,30,20,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });

  // Flugbahnen: Großkreis mit Höhe, als wachsende Röhre (drawRange)
  const SEG = 160, RAD = 10;
  const makeArc = (la, lo, tgt, i, colCore, colHalo, delay, dur, h) => {
    const a = dirOf(la, lo), b = dirOf(...tgt); const ang = a.angleTo(b);
    const pts = []; for (let k = 0; k <= SEG; k++) { const u = k / SEG;
      const p = new THREE.Vector3().copy(a).multiplyScalar(Math.sin((1 - u) * ang) / Math.sin(ang)).add(b.clone().multiplyScalar(Math.sin(u * ang) / Math.sin(ang)));
      pts.push(p.normalize().multiplyScalar(1.004 + h * Math.sin(u * Math.PI))); }
    const curve = new THREE.CatmullRomCurve3(pts);
    const core = new THREE.Mesh(new THREE.TubeGeometry(curve, SEG, 0.0035, RAD, false), new THREE.MeshBasicMaterial({color: colCore, toneMapped: false}));
    const halo = new THREE.Mesh(new THREE.TubeGeometry(curve, SEG, 0.011, RAD, false), new THREE.MeshBasicMaterial({color: colHalo, transparent: true, opacity: 0.45, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false}));
    // ganze geplante Bahn schwach gestrichelt
    const dash = new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(200)), new THREE.LineDashedMaterial({color: '#ff5040', dashSize: 0.012, gapSize: 0.01, transparent: true, opacity: 0.0}));
    dash.computeLineDistances();
    const head = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false})); head.scale.setScalar(0.07);
    const start = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false}));
    start.position.copy(a.clone().multiplyScalar(1.005)); start.scale.setScalar(0.06);
    scene.add(core, halo, dash, head, start);
    return {curve, core, halo, dash, head, start, delay, dur, a, b};
  };
  const arcs = LAUNCH.map(([la, lo], i) => makeArc(la, lo, TARGET[i], i, '#ffd2c0', '#ff2a14', i * 0.45, 17, 0.12));
  const cr = rng(31);
  const counter = C_LAUNCH.map(([la, lo], i) => { const eu = i >= 6;
    return makeArc(la, lo, C_TARGET[i], i, '#fff4d8', '#ffa020', (COUNTER - T0) + cr() * 2.0, eu ? 9.5 : 13.0, eu ? 0.07 : 0.13); });
  counter.forEach(A => { A.start.material.color.set('#ffd080'); A.start.scale.setScalar(0.0); });
  // Blitze der Einschläge
  const flashTex = canvasTex(128, 128, (g, w) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.2, 'rgba(255,245,200,0.9)'); gr.addColorStop(0.5, 'rgba(255,170,60,0.35)'); gr.addColorStop(1, 'rgba(255,90,20,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const flashes = cDir.map(d => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({map: flashTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false})); sp.position.copy(d.clone().multiplyScalar(1.01)); scene.add(sp); return sp; });
  const fr = rng(57); const fTimes = CITIES.map((_, i) => FLASH0 + i * 0.15 + fr() * 0.08);
  // Radarringe um die Ziele und Abschussgebiet (flach auf der Kugel)
  const ringMat = new THREE.MeshBasicMaterial({color: '#ff4a3a', transparent: true, opacity: 0.5, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false});
  const rings = [];
  const ringAt = (dir, r0, phase) => { for (let k = 0; k < 3; k++) { const m = new THREE.Mesh(new THREE.RingGeometry(0.97, 1, 96), ringMat.clone()); m.position.copy(dir.clone().multiplyScalar(1.003)); m.lookAt(dir.clone().multiplyScalar(2)); scene.add(m); rings.push({m, r0, k, phase}); } };
  ringAt(dirOf(45.5, -105), 0.09, 0);
  TARGET.forEach((t, i) => ringAt(dirOf(...t), 0.05, 1 + i * 0.4));
  // Gitter: Breitenkreise um den Pol (Lagebild-Anmutung)
  const gridMat = new THREE.LineBasicMaterial({color: '#5ab8ff', transparent: true, opacity: 0.18});
  for (const lat of [50, 60, 70, 80]) { const pts = []; for (let k = 0; k <= 180; k++) pts.push(dirOf(lat, k * 2).multiplyScalar(1.006)); scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), gridMat)); }
  for (let lon = 0; lon < 360; lon += 30) { const pts = []; for (let lat = 40; lat <= 90; lat += 2) pts.push(dirOf(lat, lon).multiplyScalar(1.006)); scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), gridMat)); }

  const camera = new THREE.PerspectiveCamera(32, 1080 / 1920, 0.01, 100);
  const growArc = (A, tt, T, i) => {
    const p = clamp((tt - A.delay) / A.dur); const ep = 1 - Math.pow(1 - p, 1.6);
    const n = Math.floor(ep * SEG) * RAD * 6;
    A.core.geometry.setDrawRange(0, n); A.halo.geometry.setDrawRange(0, n);
    A.dash.material.opacity = 0.35 * smooth(0, 1.5, tt - A.delay) * (p < 1 ? 1 : 0);
    A.head.visible = p > 0 && p < 1; A.head.position.copy(A.curve.getPointAt(Math.max(0.001, ep)));
    A.head.scale.setScalar(0.06 + 0.02 * Math.sin(T * 20 + i));
    return p;
  };
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, tt = T - T0; renderer.toneMappingExposure = 1.0;
    arcs.forEach((A, i) => { growArc(A, tt, T, i); A.start.material.opacity = 0.5 + 0.5 * (Math.sin(T * 8 + i) > 0); });
    counter.forEach((A, i) => { const p = growArc(A, tt, T, i); const a = tt - A.delay;
      A.start.scale.setScalar(a > 0 ? 0.05 + 0.12 * Math.exp(-a * 2.5) : 0); A.start.material.opacity = a > 0 ? 0.6 + 0.4 * (Math.sin(T * 9 + i) > 0) : 0; });
    // Einschläge
    flashes.forEach((sp, i) => { const ag = T - fTimes[i]; cAge[i] = ag;
      if (ag < 0) { sp.visible = false; return; } sp.visible = true;
      const k = Math.exp(-ag * 1.6); sp.scale.setScalar(0.06 + 0.5 * (1 - Math.exp(-ag * 9)) * (0.45 + 0.55 * k));
      sp.material.opacity = 0.25 + 0.75 * k; sp.material.color.setRGB(1, 0.55 + 0.45 * k, 0.25 + 0.75 * k * k); });
    earthMat.uniforms.cAge.value = cAge;
    rings.forEach(R => { const u = ((T * 0.6 + R.k / 3 + R.phase) % 1); R.m.scale.setScalar(R.r0 * (0.4 + u * 1.6)); R.m.material.opacity = 0.55 * (1 - u) * (shot.id === 'final' ? 0.4 : 1); });
    if (shot.id === 'final') {
      // weit: Nordamerika unten, Europa und Russland oben; Lichtblitz schüttelt leicht
      const u = smooth(0, 6, t), sh = T > FLASH0 ? 0.012 * Math.exp(-(T - FLASH0) * 0.6) : 0;
      camera.position.copy(dirOf(lerp(64, 66, u), lerp(-20, -16, u)).multiplyScalar(lerp(6.4, 6.1, u)));
      camera.position.x += noise1(T * 12, 1) * sh; camera.position.y += noise1(T * 12, 2) * sh;
      camera.up.copy(dirOf(40, 60)); camera.lookAt(dirOf(60, -25).multiplyScalar(0.55));
      renderer.toneMappingExposure = lerp(1.0, 0.12, smooth(88.6, 89.9, T));
    } else {
      // über der Arktis; ab dem Gegenschlag zurückziehen, damit beide Kontinente sichtbar sind
      const u = smooth(0, 5.5, t), w = smooth(COUNTER - T0 - 0.3, COUNTER - T0 + 3.5, t);
      const from = dirOf(lerp(lerp(60, 64, u), 64, w), lerp(lerp(-48, -42, u), -26, w)).multiplyScalar(lerp(lerp(5.3, 5.0, u), 6.2, w));
      camera.position.copy(from); camera.up.copy(dirOf(lerp(55, 42, w), lerp(50, 60, w)));
      camera.lookAt(dirOf(lerp(64, 60, w), lerp(-50, -28, w)).multiplyScalar(lerp(0.7, 0.55, w)));
    }
    camera.updateProjectionMatrix();
  }};
}
