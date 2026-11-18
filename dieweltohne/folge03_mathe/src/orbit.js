// Erdumlaufbahn: Satelliten berechnen ihre Bahn nicht mehr. Steuerdüsen feuern wirr, zwei Satelliten kollidieren, Trümmerwolke.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex} from './lib.js';
import {ORBIT_HIT} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#000003');
  const SUN = V3(0.45, -0.45, 0.8).normalize();
  const sun = new THREE.DirectionalLight('#fff6e8', 3.2); sun.position.copy(SUN).multiplyScalar(100); scene.add(sun);
  scene.add(new THREE.HemisphereLight('#4a78c0', '#05070c', 0.6)); // Erdschein von oben
  { const e = new THREE.Scene(); e.background = new THREE.Color('#3a5a8a'); const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(e, 0.02).texture; scene.environmentIntensity = 0.8; }
  // Sterne
  { const r = rng(9), n = 3000, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const v = V3(r() - 0.5, r() - 0.5, r() - 0.5).normalize().multiplyScalar(800); p.set([v.x, v.y, v.z], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({color: '#ffffff', size: 1.4, sizeAttenuation: false, transparent: true, opacity: 0.8}))); }
  // Erde (oben im Bild)
  const img = new Image(); img.src = '../tex/earth_day.jpg'; await img.decode();
  const et = new THREE.Texture(img); et.colorSpace = THREE.SRGBColorSpace; et.anisotropy = 8; et.needsUpdate = true;
  const EC = V3(0, 92, -70), ER = 70;
  const earth = mesh(new THREE.SphereGeometry(ER, 128, 96), new THREE.MeshStandardMaterial({map: et, roughness: 0.85, metalness: 0}), EC.x, EC.y, EC.z, scene);
  earth.rotation.set(0.9, -1.2, 0.3);
  const atm = new THREE.Mesh(new THREE.SphereGeometry(ER * 1.025, 96, 64), new THREE.ShaderMaterial({transparent: true, side: THREE.BackSide, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: 'varying vec3 n; varying vec3 v; void main(){ n=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.); v=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }',
    fragmentShader: 'varying vec3 n; varying vec3 v; void main(){ float f=pow(1.0-abs(dot(n,v)),2.5); gl_FragColor=vec4(0.35,0.6,1.0,1.0)*f*1.1; }'}));
  atm.position.copy(EC); scene.add(atm);

  // Satellit: Goldfolie, Solarflügel, Parabolantenne
  const foil = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#c9952f'; g.fillRect(0, 0, w, h); const r = rng(3);
    for (let i = 0; i < 260; i++) { g.fillStyle = `rgba(${r() < 0.5 ? '255,230,150' : '90,55,10'},${0.15 + r() * 0.3})`; g.beginPath(); g.moveTo(r() * w, r() * h); for (let k = 0; k < 3; k++) g.lineTo(r() * w, r() * h); g.fill(); } });
  const cells = canvasTex(512, 256, (g, w, h) => { g.fillStyle = '#0d1d4a'; g.fillRect(0, 0, w, h);
    for (let x = 0; x < w; x += 32) for (let y = 0; y < h; y += 32) { const gr = g.createLinearGradient(x, y, x + 32, y + 32); gr.addColorStop(0, '#22397a'); gr.addColorStop(1, '#0b1636'); g.fillStyle = gr; g.fillRect(x + 2, y + 2, 28, 28); }
    g.strokeStyle = '#9aa7c4'; g.lineWidth = 3; g.strokeRect(1, 1, w - 2, h - 2); });
  const foilM = new THREE.MeshStandardMaterial({map: foil, metalness: 0.65, roughness: 0.4, color: '#ffffff'});
  const cellM = new THREE.MeshStandardMaterial({map: cells, metalness: 0.2, roughness: 0.45, side: THREE.DoubleSide});
  const whiteM = mat('#e8e8e4', {roughness: 0.5}), steel = mat('#9aa0a8', {metalness: 0.8, roughness: 0.35});
  function satellite(scale, seed) {
    const g = new THREE.Group(); g.scale.setScalar(scale);
    mesh(new THREE.BoxGeometry(1.6, 1.6, 2.2), foilM, 0, 0, 0, g);
    mesh(new THREE.BoxGeometry(1.64, 0.3, 2.24), whiteM, 0, 0.7, 0, g);
    const wings = [];
    for (const s of [-1, 1]) { mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.4, 8), steel, s * 1.5, 0, 0, g).rotation.z = Math.PI / 2;
      const w = new THREE.Group(); w.position.set(s * 2.2, 0, 0); g.add(w);
      for (let k = 0; k < 3; k++) mesh(new THREE.BoxGeometry(2.0, 0.04, 1.8), cellM, s * (1.05 + k * 2.05), 0, 0, w);
      wings.push(w); }
    const dish = mesh(new THREE.SphereGeometry(0.9, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.32), whiteM, 0, 0, 1.6, g); dish.rotation.x = -Math.PI / 2; dish.material = whiteM.clone(); dish.material.side = THREE.DoubleSide;
    mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.9, 6), steel, 0, 0, 1.65, g).rotation.x = Math.PI / 2;
    for (const [x, y] of [[0.5, -0.8], [-0.5, -0.8]]) mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.4, 6), steel, x, y - 0.6, -0.5, g);
    g.userData = {wings};
    return g;
  }
  const sat = satellite(1, 1); sat.position.set(0, 0, 0); scene.add(sat);
  const sat2 = satellite(0.7, 2); scene.add(sat2);
  // Steuerdüsen: Gasstrahlen als additive Kegel
  const jetTex = canvasTex(32, 128, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0.95)'); gr.addColorStop(0.4, 'rgba(200,220,255,0.4)'); gr.addColorStop(1, 'rgba(200,220,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const JETS = [[0.8, 0.8, -1.1, 1, 0, 0], [-0.8, 0.8, -1.1, -1, 0, 0], [0.8, -0.8, 1.1, 0, -1, 0], [-0.8, -0.8, -1.1, 0, 0, -1], [0.8, 0.8, 1.1, 0, 1, 0], [-0.8, -0.8, 1.1, 0, 0, 1]];
  const jets = JETS.map(([x, y, z, dx, dy, dz]) => { const c = new THREE.Mesh(new THREE.ConeGeometry(0.22, 1.6, 12, 1, true), new THREE.MeshBasicMaterial({map: jetTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide}));
    c.geometry.translate(0, -0.8, 0); c.geometry.rotateX(Math.PI); c.position.set(x, y, z); c.quaternion.setFromUnitVectors(V3(0, -1, 0), V3(dx, dy, dz)); sat.add(c); return c; });
  // Satellitenschwarm (Lichtpunkte, ziehen in einer Kette, geraten aus der Formation)
  const NSW = 160; const swp = new Float32Array(NSW * 3); const swg = new THREE.BufferGeometry(); swg.setAttribute('position', new THREE.BufferAttribute(swp, 3));
  const swarm = new THREE.Points(swg, new THREE.PointsMaterial({color: '#fff4dc', size: 3.2, sizeAttenuation: false, transparent: true, opacity: 0.95})); swarm.frustumCulled = false; scene.add(swarm);
  const swr = rng(17); const swd = Array.from({length: NSW}, (_, i) => [i, swr() - 0.5, swr() - 0.5, swr() - 0.5, swr() * 6]);
  // Trümmer
  const ND = 700; const debris = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 0.05, 1), new THREE.MeshStandardMaterial({metalness: 0.7, roughness: 0.35}), ND);
  const dr = rng(33); const dd = [];
  for (let i = 0; i < ND; i++) { const panel = dr() < 0.6; debris.setColorAt(i, new THREE.Color(panel ? (dr() < 0.5 ? '#2a4590' : '#9aa7c4') : (dr() < 0.6 ? '#d9a640' : '#e8e8e4')));
    const v = V3(dr() - 0.5, dr() - 0.5, dr() - 0.5).normalize().multiplyScalar(1.5 + Math.pow(dr(), 2) * 9);
    dd.push({o: V3((dr() - 0.5) * 2, (dr() - 0.5) * 1, (dr() - 0.5) * 2), v, s: 0.04 + Math.pow(dr(), 3) * 0.38, w: V3(dr() * 9, dr() * 9, dr() * 9)}); }
  debris.frustumCulled = false; scene.add(debris);
  // Blitz
  const flashTex = canvasTex(128, 128, (g, w) => { const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,230,190,0.7)'); gr.addColorStop(1, 'rgba(255,180,120,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const flash = new THREE.Sprite(new THREE.SpriteMaterial({map: flashTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false})); scene.add(flash);
  const flashL = new THREE.PointLight('#ffe6c0', 0, 60, 1.5); scene.add(flashL);
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.05, 2000);
  const HITP = V3(-3.2, -0.2, 0.6); // Einschlagstelle: linker Flügel

  return {scene, camera, update(shot, T) {
    renderer.toneMappingExposure = 1.05;
    const t = T - shot.t0, a = T - ORBIT_HIT;
    earth.rotation.y = -1.2 + T * 0.004;
    // Taumeln: Düsen feuern wirr, Drehung nimmt zu; nach dem Einschlag starker Drall
    const spin = smooth(47.5, 50, T) * 0.25 + (a > 0 ? 0.45 * (1 - Math.exp(-a * 3)) : 0);
    sat.rotation.set(1.15 + Math.sin(T * 0.7) * 0.05 + spin * (T - 47) * 0.35, -0.35 + spin * (T - 47) * 0.5, 0.25 + spin * (T - 47) * 0.25);
    sat.position.set(0, 0, 0).addScaledVector(V3(1.2, 0.4, -0.6), a > 0 ? (1 - Math.exp(-a * 2)) * 1.5 : 0);
    jets.forEach((j, i) => { const on = noise1(T * 4 + i * 3, i) > 0.15 && a < 1.5; j.visible = on; j.scale.set(1, 0.6 + 0.6 * Math.abs(noise1(T * 25, i + 5)), 1); });
    // linker Flügel zerbricht beim Einschlag
    sat.userData.wings[0].visible = a < 0;
    // zweiter Satellit nähert sich und verschwindet im Einschlag
    sat2.visible = a < 0.03;
    if (sat2.visible) { const p = HITP.clone().add(V3(-26, 6, -14).multiplyScalar(Math.max(0, -a) / 3)); sat2.position.copy(p); sat2.rotation.set(T * 0.9, T * 1.3, 0.4); }
    // Trümmer
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
    dd.forEach((d, i) => { if (a < 0) { m4.makeScale(0, 0, 0); debris.setMatrixAt(i, m4); return; }
      const p = HITP.clone().add(d.o).addScaledVector(d.v, a).addScaledVector(V3(-2, 0.5, -1), a * 0.6);
      e.set(d.w.x * a, d.w.y * a, d.w.z * a); q.setFromEuler(e); m4.compose(p, q, V3(d.s, d.s, d.s)); debris.setMatrixAt(i, m4); });
    debris.instanceMatrix.needsUpdate = true;
    const fk = a > 0 ? Math.exp(-a * 3.5) : 0;
    flash.position.copy(HITP); flash.material.opacity = fk; flash.scale.setScalar(4 + (1 - fk) * 10 + fk * 16); flash.visible = a > 0;
    flashL.position.copy(HITP).add(V3(0, 1, 2)); flashL.intensity = 3000 * fk;
    // Schwarm
    swd.forEach(([i, x, y, z, ph], k) => { const off = smooth(47, 53, T);
      const s = i / NSW; const base = V3(-60 + s * 120 + T * 2.5, 22 + s * 18, -60 - s * 30);
      base.add(V3(x * 14, y * 10, z * 8).multiplyScalar(off)).add(V3(Math.sin(T * 2 + ph), Math.cos(T * 1.7 + ph), 0).multiplyScalar(off * 0.8));
      swp.set([base.x, base.y, base.z], k * 3); });
    swg.attributes.position.needsUpdate = true;
    // Kamera: langsame Fahrt, Erschütterung beim Einschlag
    const u = smooth(0, 6, t), sh = a > 0 ? 0.25 * Math.exp(-a * 2.5) : 0;
    camera.position.set(lerp(4.0, 2.5, u) + noise1(T * 12, 1) * sh, lerp(-3.0, -2.4, u) + noise1(T * 12, 2) * sh, lerp(13, 11.5, u));
    camera.lookAt(lerp(-0.8, -1.2, u), lerp(0.2, 0.0, u), 0);
    camera.updateProjectionMatrix();
  }};
}
