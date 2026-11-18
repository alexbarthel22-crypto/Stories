// Startrampe in der Abenddämmerung: Rakete hebt ab, eine Dichtung im Booster versagt, Explosion
import {THREE, envMap, mat, mesh, rng, clamp, smooth, lerp, noise1, skyDome} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.environment = envMap(renderer); scene.environmentIntensity = 0.4;
  scene.fog = new THREE.Fog('#c48a74', 300, 2500);
  scene.add(skyDome('#24304f', '#a8697a', '#f0a77c', 3000));
  scene.add(new THREE.HemisphereLight('#f3c2a8', '#2c2a2a', 1.1));
  const sun = new THREE.DirectionalLight('#ffc39a', 1.6); sun.position.set(-500, 200, -300); scene.add(sun);
  // Boden, Meer, Rampe
  mesh(new THREE.PlaneGeometry(6000, 6000), mat('#4c5737', {roughness: 1}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  const sea = mesh(new THREE.PlaneGeometry(6000, 2500), mat('#36506b', {roughness: 0.15, metalness: 0.4}), 0, 0.05, -1900, scene); sea.rotation.x = -Math.PI / 2;
  mesh(new THREE.BoxGeometry(70, 6, 70), mat('#8b8780', {roughness: 0.9}), 0, 3, 0, scene);
  const steel = mat('#8e3b2b', {roughness: 0.7, metalness: 0.4});
  const tower = new THREE.Group(); tower.position.set(-16, 6, 0); scene.add(tower);
  for (const [x, z] of [[-4, -4], [4, -4], [-4, 4], [4, 4]]) mesh(new THREE.BoxGeometry(0.8, 80, 0.8), steel, x, 40, z, tower);
  for (let y = 4; y < 80; y += 6) { mesh(new THREE.BoxGeometry(9, 0.5, 0.5), steel, 0, y, -4, tower); mesh(new THREE.BoxGeometry(9, 0.5, 0.5), steel, 0, y, 4, tower); mesh(new THREE.BoxGeometry(0.5, 0.5, 9), steel, 4, y, 0, tower); }
  const arm = mesh(new THREE.BoxGeometry(10, 2, 2), steel, 8, 55, 0, tower);
  // Rakete: Hauptstufe + 2 Booster
  const white = mat('#f1f1ee', {roughness: 0.45}), dark = mat('#2a2a2c', {roughness: 0.6}), orange = mat('#c96a2a', {roughness: 0.7});
  const rocket = new THREE.Group(); scene.add(rocket);
  mesh(new THREE.CylinderGeometry(4.2, 4.2, 46, 32), orange, 0, 29, 0, rocket);
  mesh(new THREE.ConeGeometry(4.2, 9, 32), orange, 0, 56.5, 0, rocket);
  const boosters = [-1, 1].map(s => {
    const b = new THREE.Group(); b.position.set(s * 6.3, 0, 0); rocket.add(b);
    mesh(new THREE.CylinderGeometry(1.9, 1.9, 40, 24), white, 0, 26, 0, b);
    mesh(new THREE.ConeGeometry(1.9, 5, 24), white, 0, 48.5, 0, b);
    mesh(new THREE.CylinderGeometry(2.0, 2.4, 3, 24), dark, 0, 5.5, 0, b);
    for (const y of [14, 22, 30, 38]) mesh(new THREE.CylinderGeometry(1.95, 1.95, 0.35, 24), dark, 0, y, 0, b); // Segmentfugen mit O-Ringen
    return b;
  });
  const fire = particles(3000, 'flame'); scene.add(fire);
  const smoke = particles(1600, 'smoke'); scene.add(smoke);
  const light = new THREE.PointLight('#ffb070', 0, 600, 1.2); scene.add(light);
  const camera = new THREE.PerspectiveCamera(30, 1080 / 1920, 1, 8000);
  const r = rng(3);
  const debris = Array.from({length: 10}, () => ({dir: V3(r() - 0.5, 0.3 + r() * 0.8, r() - 0.5).normalize(), sp: 25 + r() * 35}));

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    const lift = 1.0, fail = 2.6, boom = 3.15;
    const h = t < lift ? 0 : 3 * Math.pow(t - lift, 2.1);
    rocket.position.set(0, 6 + h, 0); rocket.visible = t < boom + 0.05;
    rocket.rotation.z = t > fail ? 0.03 * (t - fail) : 0;
    arm.rotation.y = smooth(0.2, 1.0, t) * -0.8;
    const top = 6 + h;
    const fx = [], sm = [];
    if (t < boom) {
      for (const s of [-1, 1]) fx.push({type: 'flame', pos: V3(s * 6.3, top + 2, 0), r: 1.6, t0: 0, size: 5, rise: -14, share: 2});
      fx.push({type: 'flame', pos: V3(0, top + 2, 0), r: 2.2, t0: 0, size: 6, rise: -12, share: 2});
      sm.push({type: 'smoke', pos: V3(0, 6, 0), r: 22, t0: -0.5, size: 40, rise: 2.5, share: 3}, {type: 'smoke', pos: V3(30, 4, 0), r: 18, t0: 0.2, size: 35, rise: 1.5, share: 2});
      if (h > 4) sm.push({type: 'smoke', pos: V3(0, top - 6, 0), r: 4, t0: lift + 0.3, size: 16, rise: -4, share: 2});
    }
    if (t > fail && t < boom) fx.push({type: 'flame', pos: V3(6.3 + 2.3, top + 22, 0), r: 0.8, t0: fail, size: 4, rise: 2, power: 1.4, share: 1}); // Flamme aus der Booster-Fuge
    if (t >= boom) {
      const c = V3(0, top + 25, 0);
      fx.push({type: 'burst', pos: c, r: 70, t0: boom, size: 30, rise: 4, power: 0.8, share: 5});
      sm.push({type: 'burstSmoke', pos: c, r: 80, t0: boom + 0.15, size: 50, rise: 3, share: 4});
      debris.forEach((d, i) => { const a = t - boom; const p = c.clone().addScaledVector(d.dir, d.sp * a); p.y -= 4.9 * a * a;
        fx.push({type: 'flame', pos: p, r: 1.5, t0: boom, size: 7, rise: 0, share: 0.3}); sm.push({type: 'smoke', pos: p, r: 2, t0: boom, size: 14, rise: 1, share: 0.3}); });
    }
    updateParticles(fire, fx, t, V3(4, 0, 0)); updateParticles(smoke, sm, t, V3(5, 0, 1));
    light.position.set(0, t >= boom ? top + 25 : top, 30); light.intensity = t >= boom ? 6e4 * Math.exp(-(t - boom) * 1.5) + 6e3 : 6e3 * flicker(T);
    const look = Math.max(40, Math.min(top + 20, 170));
    camera.position.set(-90, 18, 330); camera.lookAt(0, lerp(40, look, smooth(1.2, 3.0, t)), 0);
    camera.fov = 27;
    const sh = t > boom ? 3 * Math.exp(-(t - boom) * 1.2) : 0.3;
    camera.position.x += noise1(T * 5, 2) * sh; camera.position.y += noise1(T * 5, 7) * sh;
    camera.updateProjectionMatrix(); void boosters;
  }};
}
