// Nahaufnahme: Handy im Regen, Silikonhülle verschwindet, Wasser dringt ein, Display stirbt
import {THREE, envMap, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, rainSystem, updateRain} from './lib.js';
import {makePhone, makeHands, makeDrops, updateScreen} from './phone.js';

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.environment = envMap(renderer); scene.environmentIntensity = 0.7;
  // unscharfer Straßenhintergrund mit Lichtern (Bokeh)
  const r = rng(4);
  const bg = canvasTex(1024, 2048, (g, w, h) => {
    const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, '#2b3442'); grd.addColorStop(0.6, '#4b5563'); grd.addColorStop(1, '#2a2f36');
    g.fillStyle = grd; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 70; i++) {
      const x = r() * w, y = h * (0.35 + r() * 0.45), rad = 20 + r() * 70;
      const c = ['255,214,150', '255,90,60', '255,240,220', '150,190,255'][Math.floor(r() * 4)];
      const rg = g.createRadialGradient(x, y, 0, x, y, rad); rg.addColorStop(0, `rgba(${c},0.55)`); rg.addColorStop(0.7, `rgba(${c},0.35)`); rg.addColorStop(1, `rgba(${c},0)`);
      g.fillStyle = rg; g.beginPath(); g.arc(x, y, rad, 0, 7); g.fill();
    }
  });
  const bgm = mesh(new THREE.PlaneGeometry(3.2, 6.4), new THREE.MeshBasicMaterial({map: bg, fog: false}), 0, 0, -2.2, scene);
  scene.add(new THREE.HemisphereLight('#cfd8e6', '#383838', 1.6));
  const key = new THREE.DirectionalLight('#ffffff', 1.4); key.position.set(0.6, 1, 1); scene.add(key);
  const camera = new THREE.PerspectiveCamera(35, 1080 / 1920, 0.01, 50);
  const phone = makePhone(); const hand = makeHands();
  const rig = new THREE.Group(); rig.add(phone, hand); scene.add(rig);
  const drops = makeDrops(23, 170);
  const rain = rainSystem(1400, {x0: -0.5, x1: 0.5, y0: -0.6, y1: 0.6, z0: -1.5, z1: 0.25}, 0xcfd8e2, 0.06, 0.5); scene.add(rain);
  // Staub beim Verschwinden der Hülle
  const dust = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({color: '#ff8f84', size: 0.003, transparent: true}));
  const dr = rng(8); const dp = []; for (let i = 0; i < 500; i++) { const e = Math.floor(dr() * 4); const u = dr() - 0.5; dp.push([e < 2 ? (e ? 1 : -1) * 0.039 : u * 0.078, e >= 2 ? (e === 2 ? 1 : -1) * 0.079 : u * 0.158, (dr() - 0.5) * 0.01, dr(), dr(), dr()]); }
  dust.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(500 * 3), 3)); rig.add(dust);

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0, tv = 0.45;
    updateRain(rain, T, 3.2, -0.05);
    const gone = clamp((t - tv) / 0.15);
    phone.userData.caseM.opacity = 1 - gone; phone.userData.cg.visible = gone < 1;
    // Staub fliegt auseinander
    const P = dust.geometry.attributes.position.array; const k = clamp((t - tv) / 0.9);
    dp.forEach((d, i) => { P[i * 3] = d[0] * (1 + k * 0.4) + (d[3] - 0.5) * k * 0.05; P[i * 3 + 1] = d[1] * (1 + k * 0.2) - k * k * 0.05 * d[4]; P[i * 3 + 2] = d[2] + (d[5] - 0.2) * k * 0.06; });
    dust.geometry.attributes.position.needsUpdate = true; dust.visible = t > tv && k < 1; dust.material.opacity = 1 - k;
    updateScreen(phone, drops, {t: T, notify: 1 - smooth(1.0, 1.4, t), wet: 1, ingress: smooth(3.6, 6.2, t) * 0.75,
      glitch: smooth(4.6, 5.6, t) * (1 - smooth(6.25, 6.3, t)), dead: smooth(6.1, 6.3, t) * (Math.floor(T * 20) % 7 === 0 && t < 6.6 ? 0.4 : 1)});
    // Handy dreht sich langsam, damit man den nackten Rand sieht
    const turn = smooth(0.9, 3.0, t) * (1 - smooth(3.2, 4.6, t));
    rig.rotation.set(-0.05 + noise1(T, 2) * 0.01, -0.85 * turn + noise1(T * 0.8, 4) * 0.015, 0.03);
    rig.position.set(0, -0.004, 0);
    camera.position.set(0.0 + noise1(T, 1) * 0.002, 0.004, 0.36 - smooth(3.4, 6.5, t) * 0.09); camera.lookAt(0, 0.0, 0);
    camera.updateProjectionMatrix();
    void bgm; void lerp;
  }};
}
