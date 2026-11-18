// Europa bei Nacht (NASA Black Marble): das kontinentaleuropäische Verbundnetz fällt von Deutschland aus Land für Land aus.
// Großbritannien, Irland und Skandinavien hängen an eigenen Netzen und bleiben hell.
import {THREE, rng, clamp, smooth, lerp} from './lib.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const D = Math.PI / 180;

export async function build() {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#010205');
  const img = new Image(); img.src = '../tex/earth_night.jpg'; await img.decode();
  const tex = new THREE.Texture(img); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
  const mat = new THREE.ShaderMaterial({uniforms: {map: {value: tex}, R: {value: 0}, time: {value: 0}},
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }',
    fragmentShader: `uniform sampler2D map; uniform float R, time; varying vec2 vUv;
      float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
      void main(){
        vec3 c = texture2D(map, vUv).rgb;
        float lon = vUv.x*360.0-180.0, lat = vUv.y*180.0-90.0;
        // Winkelabstand von Mitteldeutschland (51N 10E)
        float a = radians(lat), b = radians(lon - 10.0), a0 = radians(51.0);
        float d = degrees(acos(clamp(sin(a)*sin(a0) + cos(a)*cos(a0)*cos(b), -1.0, 1.0)));
        bool grid = lat > 35.5 && lon > -10.0 && lon < 40.0 && !(lat > 50.3 && lon < 1.8) && !(lat > 55.3 && lon > 4.5 && lon < 21.0) && !(lat > 59.6)
          && !(lat > 52.0 && lon > 28.0) && !(lat > 51.5 && lon > 24.0 && !(lat > 54.0 && lon < 27.5));
        float off = grid ? smoothstep(R - 1.5, R - 4.0, d) : 0.0;
        float edge = grid ? (1.0 - smoothstep(0.0, 3.0, abs(d - R + 2.0))) : 0.0;
        float blink = step(0.5, h(floor(vUv*900.0) + floor(time*14.0)));
        float k = mix(1.0, 0.03, off) * mix(1.0, blink, edge * 0.9);
        gl_FragColor = vec4(c * k * 1.25 + vec3(0.004,0.006,0.012), 1.0);
        #include <colorspace_fragment>
      }`});
  const earth = new THREE.Mesh(new THREE.SphereGeometry(1, 128, 96), mat); scene.add(earth);
  const atm = new THREE.Mesh(new THREE.SphereGeometry(1.03, 64, 48), new THREE.ShaderMaterial({transparent: true, side: THREE.BackSide, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: 'varying vec3 n; varying vec3 v; void main(){ n=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.); v=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }',
    fragmentShader: 'varying vec3 n; varying vec3 v; void main(){ float f=pow(1.0-abs(dot(n,v)),3.0); gl_FragColor=vec4(0.25,0.4,0.9,1.0)*f*0.9; }'}));
  scene.add(atm);
  const r = rng(12); const sp = new Float32Array(2000 * 3);
  for (let i = 0; i < 2000; i++) { const v = V3(r() - 0.5, r() - 0.5, r() - 0.5).normalize().multiplyScalar(40); sp.set([v.x, v.y, v.z], i * 3); }
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(sp, 3));
  scene.add(new THREE.Points(sg, new THREE.PointsMaterial({color: '#ffffff', size: 0.04, transparent: true, opacity: 0.7})));
  const camera = new THREE.PerspectiveCamera(30, 1080 / 1920, 0.01, 100);
  // Richtung zu einem Ort auf der Kugel (three.js-Kugel: lon 0 liegt bei +x)
  const dirOf = (lat, lon) => V3(Math.cos(lat * D) * Math.cos(lon * D), Math.sin(lat * D), -Math.cos(lat * D) * Math.sin(lon * D));
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    mat.uniforms.time.value = T; mat.uniforms.R.value = lerp(0, 34, smooth(0.4, shot.t1 - shot.t0 - 0.6, t));
    const look = dirOf(47, 11), from = dirOf(lerp(30, 34, t / 6), lerp(8, 12, t / 6));
    camera.position.copy(from).multiplyScalar(lerp(2.5, 2.25, smooth(0, 6, t))); camera.up.set(0, 1, 0); camera.lookAt(look.multiplyScalar(0.92));
    camera.updateProjectionMatrix();
  }};
}
