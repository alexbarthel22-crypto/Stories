// Erde bei Nacht (NASA Black Marble, gemeinfrei), überall blitzen Funken auf
import {THREE, rng, clamp, smooth, canvasTex, sparkSystem} from './lib.js';

export async function build() {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#020309');
  const img = new Image(); img.src = '../tex/earth_night.jpg'; await img.decode();
  const tex = new THREE.Texture(img); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
  const earth = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), new THREE.MeshBasicMaterial({map: tex}));
  scene.add(earth);
  // Atmosphäre (Fresnel-Leuchten)
  const atm = new THREE.Mesh(new THREE.SphereGeometry(1.06, 64, 48), new THREE.ShaderMaterial({
    transparent: true, side: THREE.BackSide, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: 'varying vec3 n; varying vec3 v; void main(){ n=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.); v=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }',
    fragmentShader: 'varying vec3 n; varying vec3 v; void main(){ float f=pow(1.0-abs(dot(n,v)),3.0); gl_FragColor=vec4(0.35,0.55,1.0,1.0)*f*1.4; }'}));
  scene.add(atm);
  // Sterne
  const r = rng(12); const sp = new Float32Array(3000 * 3);
  for (let i = 0; i < 3000; i++) { const v = new THREE.Vector3(r() - 0.5, r() - 0.5, r() - 0.5).normalize().multiplyScalar(40); sp.set([v.x, v.y, v.z], i * 3); }
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(sp, 3));
  scene.add(new THREE.Points(sg, new THREE.PointsMaterial({color: '#ffffff', size: 0.05, transparent: true, opacity: 0.8})));
  // Funken an hellen Stellen (Städte = Straßen) aus der Textur abtasten
  const c = document.createElement('canvas'); c.width = 960; c.height = 480; const g = c.getContext('2d'); g.drawImage(img, 0, 0, 960, 480);
  const px = g.getImageData(0, 0, 960, 480).data; const pts = [];
  for (let tries = 0; tries < 400000 && pts.length < 2600; tries++) {
    const x = Math.floor(r() * 960), y = Math.floor(r() * 480); const i = (y * 960 + x) * 4;
    if (px[i] + px[i + 1] > 260 && r() < 0.6) { const lon = (x / 960) * Math.PI * 2 - Math.PI, lat = Math.PI / 2 - (y / 480) * Math.PI;
      pts.push([new THREE.Vector3(-Math.cos(lat) * Math.cos(lon), Math.sin(lat), Math.cos(lat) * Math.sin(lon)).multiplyScalar(1.004), r() * 4, 0.3 + r() * 0.6]); }
  }
  const flashes = sparkSystem(pts.length, 0.035); earth.add(flashes);
  const camera = new THREE.PerspectiveCamera(32, 1080 / 1920, 0.01, 100);

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    earth.rotation.y = -2.2 + t * 0.06; earth.rotation.x = 0.35;
    const P = flashes.geometry.attributes.position.array, C = flashes.geometry.attributes.color.array;
    const spread = smooth(0.2, 4.5, t);
    pts.forEach((p, i) => { const on = p[1] / 4 < spread; const ph = (t * 1.3 + p[1] * 7) % 1; const k = on ? Math.max(0, 1 - ph / p[2]) : 0;
      P[i * 3] = p[0].x; P[i * 3 + 1] = p[0].y; P[i * 3 + 2] = p[0].z; C[i * 3] = k; C[i * 3 + 1] = k * 0.55; C[i * 3 + 2] = k * 0.15; });
    flashes.geometry.attributes.position.needsUpdate = true; flashes.geometry.attributes.color.needsUpdate = true;
    camera.position.set(0, 0.1, 4.6 - smooth(0, 7, t) * 0.8); camera.lookAt(0, -0.1, 0); camera.updateProjectionMatrix();
  }};
}
