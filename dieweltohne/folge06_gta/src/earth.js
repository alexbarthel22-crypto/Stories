// Europa bei Nacht aus dem All: Region für Region gehen die Lichter aus (Stufe 6).
// Lichter-Textur: NASA „Earth's City Lights“ (gemeinfrei), Kopie aus den three.js-Beispielen.
import * as THREE from 'three';
import {lerp, smooth, noise1} from './lib.js';
import {EU_OUT} from './timeline.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
// Regionen (Breite, Länge) und Reihenfolge des Ausfalls; Spanien/Portugal bleiben diesmal hell
const REG = [[51, 10], [49, 2.5], [52, 5], [50.5, 15], [52, 20], [48, 14], [46.8, 8], [45.5, 10.5], [55.5, 10], [47.5, 19], [44.5, 26], [42.5, 13]];
const OFF = [0.0, 0.5, 0.9, 1.2, 1.6, 1.9, 2.3, 2.7, 3.1, 3.5, 4.2, 4.8];
export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#000');
  const camera = new THREE.PerspectiveCamera(36, 1080 / 1920, 0.01, 100);
  const L = new THREE.TextureLoader();
  const load = u => new Promise(r => L.load(u, t => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; r(t); }));
  const [lights, day] = await Promise.all([load('../data/earth/earth_lights_2048.png'), load('../data/earth/earth_atmos_2048.jpg')]);
  const U = {uT: {value: 0}, uC: {value: REG.map(([la, lo]) => new THREE.Vector2(la, lo))}, uO: {value: OFF.map(o => EU_OUT + o)}};
  const mat = new THREE.MeshStandardMaterial({map: day, color: new THREE.Color(0.05, 0.06, 0.09), emissive: '#ffd9a8', emissiveMap: lights, emissiveIntensity: 1.5, roughness: 0.8});
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, U);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      uniform float uT; uniform vec2 uC[12]; uniform float uO[12];
      float litAt(vec2 uv){ float lat = (uv.y - 0.5) * 180.0, lon = (uv.x - 0.5) * 360.0; float best = 1e9; float off = 1e9;
        for (int i = 0; i < 12; i++){ vec2 d = vec2(lat - uC[i].x, (lon - uC[i].y) * cos(radians(lat))); float dd = dot(d, d); if (dd < best){ best = dd; off = uO[i]; } }
        float inEU = step(best, 30.0);  // nur nahe der Regionszentren (ca. 5,5 Grad)
        float f = uT < off ? 1.0 : (uT < off + 0.3 ? 0.5 + 0.5 * sin(uT * 70.0) : 0.03);
        return mix(1.0, f, inEU); }`)
      .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\n totalEmissiveRadiance *= litAt(vEmissiveMapUv);');
  };
  const earth = new THREE.Mesh(new THREE.SphereGeometry(1, 128, 96), mat); scene.add(earth);
  // Atmosphäre: Randleuchten
  const atm = new THREE.Mesh(new THREE.SphereGeometry(1.025, 96, 64), new THREE.ShaderMaterial({transparent: true, side: THREE.BackSide, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: 'varying vec3 vN; varying vec3 vP; void main(){ vN = normalize(normalMatrix * normal); vec4 p = modelViewMatrix * vec4(position,1.0); vP = p.xyz; gl_Position = projectionMatrix * p; }',
    fragmentShader: 'varying vec3 vN; varying vec3 vP; void main(){ float r = pow(1.0 - abs(dot(normalize(-vP), vN)), 3.0); gl_FragColor = vec4(vec3(0.25,0.45,1.0) * r * 1.4, r); }'}));
  scene.add(atm);
  const sun = new THREE.DirectionalLight('#ffffff', 0.15); sun.position.set(-5, 1, -3); scene.add(sun);
  // Sterne
  const sp = []; for (let i = 0; i < 3000; i++) { const v = new THREE.Vector3().randomDirection().multiplyScalar(40); sp.push(v.x, v.y, v.z); }
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3));
  scene.add(new THREE.Points(sg, new THREE.PointsMaterial({color: '#cfd8ff', size: 1.3, sizeAttenuation: false})));
  // Europa nach vorne drehen: Punkt (Breite, Länge) auf der Kugel
  const ll = (la, lo, r = 1) => { const phi = THREE.MathUtils.degToRad(90 - la), th = THREE.MathUtils.degToRad(lo + 180); return V(-r * Math.sin(phi) * Math.cos(th), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(th)); };
  return {scene, camera, update(shot, T) {
    U.uT.value = T; const k = smooth(47, 55, T);
    const tgt = ll(49, 9); const up = V(0, 1, 0);
    const dir = tgt.clone().normalize();
    const side = new THREE.Vector3().crossVectors(up, dir).normalize();
    const pos = dir.clone().multiplyScalar(lerp(2.35, 2.2, k)).add(side.multiplyScalar(lerp(-0.1, 0.05, k))).add(V(0, -0.55, 0));
    pos.add(V(noise1(T * 0.3, 1) * 0.002, noise1(T * 0.3, 3) * 0.002, 0));
    camera.position.copy(pos); camera.up.set(0, 1, 0); camera.lookAt(tgt.clone().add(V(0, 0.12, 0))); camera.fov = 40; camera.updateProjectionMatrix();
    return {dof: null, exposure: 1.15, bloom: [0.6, 0.4, 0.55], grain: 0.05, vig: 0.45, ao: false};
  }};
}
