// Weltall: Die Sonne verschwindet. Ihr letztes Licht breitet sich als Kugelschale aus und ist noch zur Erde unterwegs.
import {THREE, rng, clamp, smooth, lerp, noise1, canvasTex} from './lib.js';
import {VANISH, lightLeft} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build() {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#010103');
  const SUN = V3(-5, 11, -8), EARTH = V3(3.5, -8, -2);
  // Sterne
  const r = rng(31); const n = 5000, sp = new Float32Array(n * 3), sc = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { const v = V3(r() - 0.5, r() - 0.5, r() - 0.5).normalize().multiplyScalar(300); sp.set([v.x, v.y, v.z], i * 3); const b = 0.3 + Math.pow(r(), 3) * 0.9; sc.set([b, b * (0.9 + r() * 0.1), b * (0.85 + r() * 0.2)], i * 3); }
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(sp, 3)); sg.setAttribute('color', new THREE.BufferAttribute(sc, 3));
  const stars = new THREE.Points(sg, new THREE.PointsMaterial({size: 1.1, sizeAttenuation: false, vertexColors: true, transparent: true})); scene.add(stars);
  // Sonne: Granulation, Randverdunklung
  const sunM = new THREE.ShaderMaterial({uniforms: {time: {value: 0}, k: {value: 1}},
    vertexShader: 'varying vec3 n; varying vec3 p; varying vec3 v; void main(){ n = normalize(normalMatrix*normal); p = position; vec4 mv = modelViewMatrix*vec4(position,1.); v = normalize(-mv.xyz); gl_Position = projectionMatrix*mv; }',
    fragmentShader: `varying vec3 n; varying vec3 p; varying vec3 v; uniform float time, k;
      float h(vec3 q){ return fract(sin(dot(q, vec3(12.9898,78.233,37.719)))*43758.5453); }
      float no(vec3 q){ vec3 i=floor(q), f=fract(q); f=f*f*(3.-2.*f);
        return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z); }
      void main(){ float mu = max(dot(n, v), 0.0);
        float g = no(p*6.0 + time*0.3)*0.6 + no(p*14.0 - time*0.5)*0.3 + no(p*30.0)*0.1;
        vec3 c = mix(vec3(1.0,0.45,0.08), vec3(1.0,0.92,0.6), g) * (0.35 + 0.65*pow(mu, 0.5));
        gl_FragColor = vec4(c * 1.7 * k, 1.0); }`});
  const sun = new THREE.Mesh(new THREE.SphereGeometry(3.6, 64, 48), sunM); sun.position.copy(SUN); scene.add(sun);
  const glowTex = canvasTex(256, 256, (g, w) => { const gr = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); gr.addColorStop(0, 'rgba(255,240,200,1)'); gr.addColorStop(0.2, 'rgba(255,200,120,0.6)'); gr.addColorStop(0.5, 'rgba(255,140,60,0.15)'); gr.addColorStop(1, 'rgba(255,120,40,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const corona = new THREE.Sprite(new THREE.SpriteMaterial({map: glowTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})); corona.scale.setScalar(26); corona.position.copy(SUN); scene.add(corona);
  const corona2 = corona.clone(); corona2.material = corona.material.clone(); corona2.scale.setScalar(60); corona2.material.opacity = 0.35; scene.add(corona2);
  // Erde, beleuchtet von der Sonne
  const img = new Image(); img.src = '../tex/earth_day.jpg'; await img.decode();
  const tex = new THREE.Texture(img); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
  const earth = new THREE.Mesh(new THREE.SphereGeometry(3.0, 96, 64), new THREE.MeshStandardMaterial({map: tex, roughness: 0.85, metalness: 0})); earth.position.copy(EARTH); scene.add(earth);
  const atm = new THREE.Mesh(new THREE.SphereGeometry(3.15, 64, 48), new THREE.ShaderMaterial({transparent: true, side: THREE.BackSide, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: {sunPos: {value: SUN}},
    vertexShader: 'varying vec3 n; varying vec3 v; varying vec3 wp; void main(){ n=normalize(mat3(modelMatrix)*normal); vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; v=normalize(cameraPosition-w.xyz); gl_Position=projectionMatrix*viewMatrix*w; }',
    fragmentShader: 'uniform vec3 sunPos; varying vec3 n; varying vec3 v; varying vec3 wp; void main(){ float f=pow(1.0-abs(dot(n,v)),2.5); float l=clamp(dot(n, normalize(sunPos-wp))+0.4,0.0,1.0); gl_FragColor=vec4(0.35,0.6,1.0,1.0)*f*1.6*l; }'}));
  atm.position.copy(EARTH); scene.add(atm);
  const light = new THREE.PointLight("#fff4e0", 14000, 0, 2); light.position.copy(SUN); scene.add(light);
  scene.add(new THREE.AmbientLight('#203050', 0.08));
  // Erdumlaufbahn (gestrichelt)
  const orbit = []; const R = SUN.distanceTo(EARTH);
  const ax1 = EARTH.clone().sub(SUN).normalize(), ax2 = new THREE.Vector3().crossVectors(ax1, V3(1, 0, 0.3)).normalize();
  for (let i = 0; i <= 400; i++) { const a = (i / 400 - 0.5) * 0.9; orbit.push(SUN.clone().addScaledVector(ax1, Math.cos(a) * R).addScaledVector(ax2, Math.sin(a) * R)); }
  const ol = new THREE.Line(new THREE.BufferGeometry().setFromPoints(orbit), new THREE.LineDashedMaterial({color: '#7f9ac0', dashSize: 0.4, gapSize: 0.3, transparent: true, opacity: 0.45})); ol.computeLineDistances(); scene.add(ol);
  // Letztes Licht: Kugelschale um die verschwundene Sonne
  const shell = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), new THREE.ShaderMaterial({transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: {a: {value: 0}},
    vertexShader: 'varying vec3 n; varying vec3 v; void main(){ n=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.); v=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }',
    fragmentShader: 'uniform float a; varying vec3 n; varying vec3 v; void main(){ float f=pow(1.0-abs(dot(n,v)),6.0); gl_FragColor=vec4(1.0,0.8,0.45,1.0)*(f*1.6+0.02)*a; }'}));
  shell.position.copy(SUN); scene.add(shell);
  // Lichtstrahl Sonne -> Erde als feine Linie
  const ray = new THREE.Line(new THREE.BufferGeometry().setFromPoints([SUN, EARTH]), new THREE.LineBasicMaterial({color: '#ffd28a', transparent: true, opacity: 0}));
  scene.add(ray);
  const camera = new THREE.PerspectiveCamera(38, 1080 / 1920, 0.1, 1000);

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, gone = T >= VANISH ? smooth(VANISH, VANISH + 0.18, T) : 0;
    sunM.uniforms.time.value = T; const s = 1 - gone; sun.scale.setScalar(Math.max(0.001, s)); sun.visible = s > 0.01;
    sunM.uniforms.k.value = 1 + 2 * gone;
    corona.material.opacity = (1 - gone) + Math.max(0, 1 - (T - VANISH) / 0.5) * (T >= VANISH ? 1 : 0) * 1.5; corona.scale.setScalar(26 + (T >= VANISH ? (T - VANISH) * 30 : 0));
    corona2.material.opacity = 0.35 * (1 - gone);
    earth.rotation.y = 1.2 + T * 0.03;
    light.intensity = 14000; // das Licht ist noch unterwegs: die Erde bleibt hell
    const frac = 1 - lightLeft(T) / 500;
    shell.scale.setScalar(Math.max(0.01, frac * R)); shell.material.uniforms.a.value = T >= VANISH ? smooth(VANISH, VANISH + 0.4, T) * 0.8 : 0;
    ray.material.opacity = T >= VANISH ? 0.25 * smooth(VANISH + 1, VANISH + 2, T) : 0;
    ol.material.opacity = 0.45 * smooth(VANISH + 1.5, VANISH + 3, T);
    const sh = T >= VANISH ? 0.25 * Math.exp(-(T - VANISH) * 2) : 0;
    camera.position.set(1 + t * 0.2 + noise1(T * 6, 2) * sh, 1 + noise1(T * 6, 5) * sh, 36 - t * 0.5); camera.lookAt(-0.5, 1.0, -5);
    camera.updateProjectionMatrix();
  }};
}
