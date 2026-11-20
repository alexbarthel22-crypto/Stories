// Festival bei Nacht: Bühne mit LED-Wand, Lichtkegeln, 2000 Menschen springen. Dann: alle taub (Haarzellen weg),
// niemand hält das Gleichgewicht – die Menge kippt von vorne nach hinten um. fest_after: Licht läuft weiter, alle liegen.
import {THREE, RoundedBoxGeometry, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut, makePerson, posePerson, envMap} from './lib.js';
import {particles, updateParticles} from './fx.js';
import {VANISH, RETURN, DEAF, CROWD_FALL} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#05040c');
  scene.fog = new THREE.FogExp2('#120a24', 0.018);
  scene.environment = envMap(renderer); scene.environmentIntensity = 0.08;
  scene.add(new THREE.HemisphereLight('#4a3a8a', '#100818', 0.5));
  const front = new THREE.SpotLight('#ffd6f0', 60, 60, 0.6, 0.5, 1.2); front.position.set(0, 12, -2); front.target.position.set(0, 0, 14); scene.add(front, front.target);
  const wash = [];
  for (const [x, c] of [[-10, '#ff2bd6'], [10, '#22d3ff'], [0, '#8a5cff']]) { const l = new THREE.PointLight(c, 40, 40, 1.5); l.position.set(x, 9, -1); scene.add(l); wash.push(l); }

  // Boden (Wiese, zertrampelt)
  const gT = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#1f2a18'; g.fillRect(0, 0, w, h); const r = rng(3); for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '60,80,40' : '30,24,18'},${r() * 0.6})`; g.fillRect(r() * w, r() * h, 3, 3); } });
  gT.wrapS = gT.wrapT = THREE.RepeatWrapping; gT.repeat.set(20, 20);
  const ground = mesh(new THREE.PlaneGeometry(300, 300), new THREE.MeshStandardMaterial({map: gT, roughness: 1}), 0, 0, 20, scene); ground.rotation.x = -Math.PI / 2;
  // Bühne
  const black = mat('#111216', {roughness: 0.6}), truss = mat('#9aa0a8', {metalness: 0.8, roughness: 0.35});
  mesh(new THREE.BoxGeometry(26, 1.8, 10), black, 0, 0.9, -5, scene);
  for (const x of [-12.5, 12.5]) mesh(new THREE.BoxGeometry(0.5, 14, 0.5), truss, x, 7, -0.5, scene);
  mesh(new THREE.BoxGeometry(26, 0.6, 0.6), truss, 0, 13.5, -0.5, scene);
  mesh(new THREE.BoxGeometry(26, 0.6, 0.6), truss, 0, 13.5, -8, scene);
  for (const x of [-12.5, 12.5]) mesh(new THREE.BoxGeometry(0.6, 0.6, 8), truss, x, 13.5, -4.2, scene);
  // Lautsprechertürme
  for (const x of [-15, 15]) { mesh(new THREE.BoxGeometry(2.5, 9, 2.5), black, x, 4.5, -1, scene); for (let k = 0; k < 6; k++) mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.1, 20), mat('#222'), x, 1.2 + k * 1.4, 0.3, scene).rotation.x = Math.PI / 2; }
  // LED-Wand (Shader)
  const ledU = {time: {value: 0}, k: {value: 1}};
  const led = new THREE.Mesh(new THREE.PlaneGeometry(22, 10), new THREE.ShaderMaterial({uniforms: ledU, fog: false, vertexShader: 'varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader: `uniform float time,k; varying vec2 vUv;
      void main(){ vec2 p=vUv*vec2(44.,20.); vec2 c=fract(p)-0.5; float dot_=smoothstep(0.5,0.3,length(c));
        vec2 q=floor(p)/vec2(44.,20.)-0.5; float r=length(q*vec2(2.2,1.));
        float ring=0.5+0.5*sin(r*18.-time*6.); float sweep=0.5+0.5*sin(q.x*9.+time*3.);
        vec3 col=mix(vec3(1.,0.15,0.75),vec3(0.1,0.8,1.),sweep)*ring + vec3(1.,0.9,0.6)*pow(max(0.,1.-r*2.),3.)*(0.6+0.4*sin(time*8.));
        gl_FragColor=vec4(col*dot_*k*1.4,1.); }`}));
  led.position.set(0, 7.5, -9.6); scene.add(led);
  // DJ-Pult und DJ
  mesh(new RoundedBoxGeometry(4, 1.1, 1.2, 2, 0.05), black, 0, 2.35, -3, scene);
  const djLed = mesh(new THREE.BoxGeometry(3.9, 0.15, 0.02), new THREE.MeshBasicMaterial({color: '#ff2bd6'}), 0, 2.5, -2.39, scene);
  const dj = makePerson(7, {top: '#111', pants: '#222', hair: '#111'}); dj.position.set(0, 1.8, -3.8); dj.scale.setScalar(1.05); scene.add(dj);
  // Lichtkegel
  const beamGeo = new THREE.ConeGeometry(1.4, 30, 24, 1, true); beamGeo.translate(0, -15, 0);
  const beamTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const beams = [];
  const bc = ['#ff2bd6', '#22d3ff', '#ffffff', '#8a5cff', '#22d3ff', '#ff2bd6', '#ffffff', '#ffd22b'];
  for (let i = 0; i < 8; i++) { const m = new THREE.Mesh(beamGeo, new THREE.MeshBasicMaterial({color: bc[i], map: beamTex, transparent: true, opacity: 0.22, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false}));
    m.position.set(-10.5 + i * 3, 13.2, -0.5); scene.add(m); beams.push(m); }
  // Konfetti/Funken? Nebel
  const haze = particles(400, 'smoke'); scene.add(haze);

  // Menge: InstancedMesh aus Teilen
  const N = 1900, r = rng(21);
  const crowd = [];
  for (let i = 0; i < N; i++) {
    const x = (r() - 0.5) * 32, z = 3.0 + Math.pow(r(), 0.8) * 34;
    if (Math.abs(x) < 1.4 && z > 14 && z < 18) continue; // kleine Lücke (Wellenbrecher)
    crowd.push({x, z, yaw: Math.PI + (r() - 0.5) * 0.5, ph: r() * 6.28, up: r() < 0.55, h: 0.92 + r() * 0.16, fallAx: (r() - 0.5) * 2.2, delay: (z - 3) * 0.045 + r() * 0.45, dir: r() < 0.6 ? 1 : -1, sit: r() < 0.25});
  }
  const n = crowd.length;
  const tops = ['#e8e2d4', '#111', '#c23b6a', '#3f6fb5', '#2f8f6b', '#e2b23a', '#7b4fa0', '#e07a2f', '#f2f2f2', '#24343f'];
  const skins = ['#f1c7a5', '#d9a47e', '#a8714f', '#7a4d33', '#f5d3b8'];
  const hairs = ['#2a1d15', '#5a3b22', '#c9a35b', '#111', '#8a5a2b'];
  const mk = (geo, cols) => { const im = new THREE.InstancedMesh(geo, new THREE.MeshStandardMaterial({roughness: 0.8}), n); const c = new THREE.Color(); for (let i = 0; i < n; i++) { c.set(cols[(i * 7 + Math.floor(i / 3)) % cols.length]); im.setColorAt(i, c); } im.castShadow = false; im.frustumCulled = false; scene.add(im); return im; };
  const torsoI = mk(new THREE.CapsuleGeometry(0.19, 0.42, 3, 8), tops);
  const legsI = mk(new THREE.CapsuleGeometry(0.17, 0.62, 3, 8), ['#1f2a44', '#2d3a55', '#3a3a3a', '#5b4636']);
  const headI = mk(new THREE.SphereGeometry(0.12, 12, 10), skins);
  const hairI = mk(new THREE.SphereGeometry(0.128, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.55), hairs);
  const armGeo = new THREE.CapsuleGeometry(0.05, 0.55, 3, 6); armGeo.translate(0, -0.32, 0);
  const armLI = mk(armGeo, skins), armRI = mk(armGeo, skins);
  const phoneLights = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.07, 0.13), new THREE.MeshBasicMaterial({color: '#e8f2ff', side: THREE.DoubleSide}), n); phoneLights.frustumCulled = false; scene.add(phoneLights);
  const M = new THREE.Matrix4(), L = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), S1 = V3(1, 1, 1), P = V3(0, 0, 0), Z = new THREE.Matrix4().makeScale(0, 0, 0);
  const part = (im, i, base, x, y, z, rx = 0, rz = 0, s = 1) => { L.compose(P.set(x, y, z), Q.setFromEuler(E.set(rx, 0, rz)), S1.set(s, s, s)); im.setMatrixAt(i, M.copy(base).multiply(L)); };
  const base = new THREE.Matrix4(), fallM = new THREE.Matrix4();

  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.1, 400);
  return {scene, camera, update(shot, T) {
    const id = shot.id, t = T - shot.t0, after = id === 'fest_after';
    const gone = T >= VANISH && T < RETURN;
    ledU.time.value = T; ledU.k.value = 1;
    beams.forEach((b, i) => { const a = T * (0.9 + i * 0.13) + i; b.rotation.set(Math.sin(a) * 0.5 + 0.35, 0, Math.cos(a * 0.8) * 0.45 + (i - 3.5) * 0.06); b.material.opacity = 0.18 + 0.1 * Math.max(0, Math.sin(T * 4 + i)); });
    wash.forEach((l, i) => l.intensity = 30 + 25 * Math.max(0, Math.sin(T * 3 + i * 2)));
    djLed.material.color.setHSL((T * 0.2) % 1, 0.9, 0.55);
    updateParticles(haze, [{type: 'smoke', pos: V3(0, 2, 10), r: 26, t0: -10, size: 9, rise: 0.3, col: [0.35, 0.25, 0.5], alpha: 0.12, share: 1}], T, V3(0.3, 0, 0.2));
    // DJ
    posePerson(dj, {armsUp: after ? 0 : (T < DEAF + 0.6 ? 0.6 + 0.3 * Math.sin(T * 8) : 0)});
    dj.userData.hair.visible = !gone;
    if (!after && T > CROWD_FALL - 0.6) { const f = smooth(CROWD_FALL - 0.6, CROWD_FALL + 0.6, T); posePerson(dj, {fall: f, fallDir: -1}); }
    if (after) posePerson(dj, {fall: 1, fallDir: -1});
    const deafK = smooth(DEAF + 0.5, DEAF + 1.2, T);
    for (let i = 0; i < n; i++) {
      const c = crowd[i];
      let jump = 0, armUp = c.up ? 1 : 0.15, sway = 0, fall = 0;
      if (!after) {
        jump = Math.max(0, Math.sin(T * Math.PI * 2.1 + c.ph * 0.15)) * 0.22 * (1 - deafK);
        armUp = lerp(c.up ? 0.9 + 0.1 * Math.sin(T * 6 + c.ph) : 0.15, 0.05, deafK);
        sway = deafK * (0.06 + 0.05 * Math.sin(T * 1.7 + c.ph));
        fall = easeIn(clamp((T - CROWD_FALL - c.delay) / 0.9));
      } else { fall = 1; armUp = 0.05; }
      // im Nachher versuchen einige, sich aufzusetzen
      let sitUp = after && c.sit ? 0.55 + 0.25 * Math.sin(t * 0.8 + c.ph) : 0;
      base.compose(P.set(c.x, jump, c.z), Q.setFromEuler(E.set(0, c.yaw, 0)), S1.set(c.h, c.h, c.h));
      const ang = (Math.PI / 2 - 0.08) * fall * (1 - sitUp * 0.8);
      fallM.makeRotationFromEuler(E.set(-ang * c.dir * Math.cos(c.fallAx) + Math.sin(T * 1.3 + c.ph) * sway, 0, ang * Math.sin(c.fallAx) + Math.cos(T * 1.1 + c.ph) * sway));
      base.multiply(fallM);
      part(legsI, i, base, 0, 0.47, 0);
      part(torsoI, i, base, 0, 1.18, 0);
      part(headI, i, base, 0, 1.7, 0);
      if (gone) hairI.setMatrixAt(i, Z); else part(hairI, i, base, 0, 1.72, -0.01, -0.25);
      const au = armUp * 2.7;
      part(armLI, i, base, -0.24, 1.45, 0, 0, -au - 0.1 - fall * 0.8);
      part(armRI, i, base, 0.24, 1.45, 0, 0, au + 0.1 + fall * 0.8);
      if (!after && c.up && i % 9 === 0 && deafK < 1 && fall === 0) { L.compose(P.set(0.3, 1.45 + 0.6 * armUp, 0), Q.identity(), S1.set(1, 1, 1)); phoneLights.setMatrixAt(i, M.copy(base).multiply(L)); }
      else phoneLights.setMatrixAt(i, Z);
    }
    [torsoI, legsI, headI, hairI, armLI, armRI, phoneLights].forEach(im => im.instanceMatrix.needsUpdate = true);
    // Kamera
    camera.fov = 46;
    if (!after) {
      const shake = smooth(CROWD_FALL, CROWD_FALL + 0.5, T) * (1 - smooth(CROWD_FALL + 2, CROWD_FALL + 4, T));
      camera.position.set(16 - t * 0.35 + noise1(T * 9, 1) * 0.04 * shake, 7.5 + noise1(T * 8, 2) * 0.04 * shake, 30 - t * 0.6);
      camera.lookAt(-1, 1.8, 9 - t * 0.3);
    } else {
      const u = smooth(0, 8, t);
      camera.position.set(lerp(6, 3, u), lerp(9, 22, u), lerp(34, 44, u)); camera.lookAt(0, 0.5, lerp(14, 12, u));
    }
    camera.updateProjectionMatrix();
  }};
}
