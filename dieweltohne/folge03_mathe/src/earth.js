// Die Erde bei Nacht über der Arktis: rote Flugbahnen steigen aus Nordamerika auf und ziehen über den Pol nach Osten.
// So zeigt es das Frühwarnsystem – berechnet aus einem Fehler.
import {THREE, rng, clamp, smooth, lerp, noise1, canvasTex} from './lib.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const D = Math.PI / 180;
const dirOf = (lat, lon) => V3(Math.cos(lat * D) * Math.cos(lon * D), Math.sin(lat * D), -Math.cos(lat * D) * Math.sin(lon * D));

const LAUNCH = [[47.5, -111.3], [46.4, -104.6], [41.2, -104.9], [48.4, -101.4], [44.1, -103.2]];
const TARGET = [[55.7, 37.6], [59.9, 30.3], [56.8, 60.6], [53.2, 50.1], [55.0, 82.9]];
const T0 = 66; // Beginn der Einstellung (Videozeit)

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#010205');
  const img = new Image(); img.src = '../tex/earth_night.jpg'; await img.decode();
  const tex = new THREE.Texture(img); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
  const earthMat = new THREE.ShaderMaterial({uniforms: {map: {value: tex}},
    vertexShader: 'varying vec2 vUv; varying vec3 vN; varying vec3 vV; void main(){ vUv = uv; vN = normalize(normalMatrix*normal); vec4 mv = modelViewMatrix*vec4(position,1.); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }',
    fragmentShader: `uniform sampler2D map; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ vec3 c = texture2D(map, vUv).rgb; float f = pow(1.0 - max(dot(vN, vV), 0.0), 2.5);
        gl_FragColor = vec4(c * 1.35 + vec3(0.006,0.01,0.02) + vec3(0.05,0.09,0.2) * f, 1.0);
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
  const arcs = LAUNCH.map(([la, lo], i) => {
    const a = dirOf(la, lo), b = dirOf(...TARGET[i]); const ang = a.angleTo(b);
    const pts = []; for (let k = 0; k <= SEG; k++) { const u = k / SEG;
      const p = new THREE.Vector3().copy(a).multiplyScalar(Math.sin((1 - u) * ang) / Math.sin(ang)).add(b.clone().multiplyScalar(Math.sin(u * ang) / Math.sin(ang)));
      pts.push(p.normalize().multiplyScalar(1.004 + 0.12 * Math.sin(u * Math.PI))); }
    const curve = new THREE.CatmullRomCurve3(pts);
    const core = new THREE.Mesh(new THREE.TubeGeometry(curve, SEG, 0.0035, RAD, false), new THREE.MeshBasicMaterial({color: '#ffd2c0', toneMapped: false}));
    const halo = new THREE.Mesh(new THREE.TubeGeometry(curve, SEG, 0.011, RAD, false), new THREE.MeshBasicMaterial({color: '#ff2a14', transparent: true, opacity: 0.45, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false}));
    // ganze geplante Bahn schwach gestrichelt
    const dash = new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(200)), new THREE.LineDashedMaterial({color: '#ff5040', dashSize: 0.012, gapSize: 0.01, transparent: true, opacity: 0.0}));
    dash.computeLineDistances();
    const head = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false})); head.scale.setScalar(0.07);
    const start = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false}));
    start.position.copy(a.clone().multiplyScalar(1.005)); start.scale.setScalar(0.06);
    scene.add(core, halo, dash, head, start);
    return {curve, core, halo, dash, head, start, delay: i * 0.45, a, b};
  });
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
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0; renderer.toneMappingExposure = 1.0;
    arcs.forEach((A, i) => {
      const p = clamp((t - A.delay) / 10.5); const ep = 1 - Math.pow(1 - p, 1.6);
      const n = Math.floor(ep * SEG) * RAD * 6;
      A.core.geometry.setDrawRange(0, n); A.halo.geometry.setDrawRange(0, n);
      A.dash.material.opacity = 0.35 * smooth(0, 1.5, t - A.delay);
      A.head.visible = p > 0 && p < 1; A.head.position.copy(A.curve.getPointAt(Math.max(0.001, ep)));
      A.head.scale.setScalar(0.06 + 0.02 * Math.sin(T * 20 + i));
      A.start.material.opacity = 0.5 + 0.5 * (Math.sin(T * 8 + i) > 0);
    });
    rings.forEach(R => { const u = ((T * 0.6 + R.k / 3 + R.phase) % 1); R.m.scale.setScalar(R.r0 * (0.4 + u * 1.6)); R.m.material.opacity = 0.55 * (1 - u); });
    // Kamera: über der Arktis, Blick schräg auf Nordamerika und Eurasien, langsame Drehung und Annäherung
    const u = smooth(0, 12, t);
    const from = dirOf(lerp(60, 66, u), lerp(-48, -38, u)).multiplyScalar(lerp(5.3, 4.8, u));
    camera.position.copy(from); camera.up.copy(dirOf(55, 50));
    camera.lookAt(dirOf(64, -50).multiplyScalar(0.7));
    camera.updateProjectionMatrix();
  }};
}
