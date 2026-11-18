// Solarpark mittags im Dunkeln: Module liefern nichts mehr, Wechselrichter melden Störung
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex} from './lib.js';
import {skyMaterial} from './beach.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), skyMaterial()); sky.renderOrder = -10; scene.add(sky);
  sky.material.uniforms.day.value = 0; sky.material.uniforms.stars.value = 1;
  scene.fog = new THREE.Fog('#030407', 30, 380);
  scene.add(new THREE.HemisphereLight('#5a6f9c', '#14160f', 0.75));
  { const e = new THREE.Scene(); e.background = new THREE.Color('#1b2a4a'); const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(e, 0.02).texture; scene.environmentIntensity = 1.3; }
  mesh(new THREE.PlaneGeometry(1200, 1200), mat('#1a2414', {roughness: 1}), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
  // Modulreihen (instanziert): Glas spiegelt den Sternenhimmel
  const cellTex = canvasTex(256, 128, (g, w, h) => { g.fillStyle = '#0d1a33'; g.fillRect(0, 0, w, h); g.strokeStyle = '#7c8aa3'; g.lineWidth = 2;
    for (let x = 0; x <= w; x += w / 12) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); } for (let y = 0; y <= h; y += h / 6) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); } });
  cellTex.wrapS = THREE.RepeatWrapping; cellTex.repeat.set(8, 1);
  const pGeo = new THREE.BoxGeometry(40, 0.05, 2.2);
  const panels = new THREE.InstancedMesh(pGeo, new THREE.MeshStandardMaterial({map: cellTex, roughness: 0.12, metalness: 0.6, color: '#c8d2e6'}), 400);
  const legs = new THREE.InstancedMesh(new THREE.BoxGeometry(0.08, 1, 0.08), mat('#8d939b', {metalness: 0.7}), 1600);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion().setFromEuler(new THREE.Euler(0.45, 0, 0)); let pi = 0, li = 0;
  for (let row = 0; row < 40; row++) for (let c = -4; c <= 5; c++) {
    const x = c * 42, z = 30 - row * 6; if (pi >= 400) break;
    m4.compose(V3(x, 1.25, z), q, V3(1, 1, 1)); panels.setMatrixAt(pi++, m4);
    for (const dx of [-18, -6, 6, 18]) if (li < 1600) { m4.compose(V3(x + dx, 0.6, z + 0.3), new THREE.Quaternion(), V3(1, 1.2, 1)); legs.setMatrixAt(li++, m4); }
  }
  panels.count = pi; legs.count = li; scene.add(panels, legs);
  // Wechselrichter-Station mit Status-LEDs und Strahler
  const st = new THREE.Group(); st.position.set(-8, 0, 22); scene.add(st);
  mesh(new THREE.BoxGeometry(6, 2.6, 2.5), mat('#d8dcd8', {roughness: 0.6}), 0, 1.3, 0, st);
  const plate = canvasTex(256, 64, (g, w, h) => { g.fillStyle = '#f2c230'; g.fillRect(0, 0, w, h); g.fillStyle = '#111'; g.font = '600 26px Plex'; g.fillText('⚡ WECHSELRICHTER 7', 14, 42); });
  mesh(new THREE.PlaneGeometry(1.6, 0.4), new THREE.MeshStandardMaterial({map: plate}), 1.2, 2.0, 1.26, st);
  const leds = []; for (let i = 0; i < 6; i++) leds.push(mesh(new THREE.SphereGeometry(0.05, 8, 6), new THREE.MeshStandardMaterial({color: '#111', emissive: '#3bdc6a', emissiveIntensity: 3}), -2.2 + i * 0.25, 1.9, 1.27, st));
  const flood = new THREE.SpotLight('#fff1d6', 260, 60, 0.8, 0.6, 1.3); flood.position.set(-8, 3.2, 23.4); flood.target.position.set(-4, 0, 14); scene.add(flood, flood.target);
  mesh(new THREE.BoxGeometry(0.4, 0.25, 0.2), mat('#222', {emissive: '#fff1d6', emissiveIntensity: 2}), 0, 2.85, 1.3, st);
  const warn = new THREE.PointLight('#ff3020', 0, 14, 1.5); warn.position.set(-8, 3.0, 23.3); scene.add(warn);
  const beacon = mesh(new THREE.SphereGeometry(0.15, 10, 8), new THREE.MeshStandardMaterial({color: '#300', emissive: '#ff2a1a', emissiveIntensity: 0}), 2.6, 2.75, 0.6, st);
  // Zaun, Windräder in der Ferne mit roten Lichtern
  for (let x = -120; x <= 120; x += 3) mesh(new THREE.BoxGeometry(0.05, 2, 0.05), mat('#555'), x, 1, 34, scene);
  mesh(new THREE.BoxGeometry(240, 1.8, 0.01), new THREE.MeshStandardMaterial({color: '#666', transparent: true, opacity: 0.25}), 0, 1, 34, scene);
  const turbines = []; for (const [x, z] of [[-120, -260], [-40, -300], [60, -280], [150, -240]]) {
    const g = new THREE.Group(); g.position.set(x, 0, z); scene.add(g); mesh(new THREE.CylinderGeometry(1.2, 2.2, 90, 12), mat('#c9ccd0'), 0, 45, 0, g);
    const hub = new THREE.Group(); hub.position.set(0, 90, 2.5); g.add(hub); for (let k = 0; k < 3; k++) { const b = mesh(new THREE.BoxGeometry(2, 45, 0.6), mat('#d6d8db'), 0, 22, 0, hub); b.geometry.translate(0, 0, 0); const pv = new THREE.Group(); pv.rotation.z = k * 2.094; pv.add(b); hub.add(pv); }
    const rl = mesh(new THREE.SphereGeometry(1.0, 8, 6), new THREE.MeshBasicMaterial({color: '#ff2a1a', fog: false}), 0, 93, 0, g); turbines.push({hub, rl});
  }
  const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.1, 1500);
  return {scene, camera, update(shot, T) {
    const t = T - shot.t0; renderer.toneMappingExposure = 1.5;
    const fault = smooth(shot.t0 + 2.6, shot.t0 + 3.3, T);
    leds.forEach((l, i) => { const on = fault > i / 6; l.material.emissive.set(on ? '#ff2a1a' : '#3bdc6a'); l.material.emissiveIntensity = on ? (Math.sin(T * 10 + i) > 0 ? 4 : 0.6) : 3; });
    beacon.material.emissiveIntensity = fault > 0.5 ? (Math.sin(T * 9) > 0 ? 6 : 0) : 0; warn.intensity = fault > 0.5 ? (Math.sin(T * 9) > 0 ? 30 : 0) : 0;
    turbines.forEach((tb, i) => { tb.hub.rotation.z = T * 0.6 + i; tb.rl.visible = Math.sin(T * 3 + i) > -0.2; });
    const u = smooth(0, 6.5, t);
    camera.position.set(lerp(12, 0, u), lerp(11, 3.4, u), lerp(62, 33, u)); camera.lookAt(lerp(-6, -8, u), lerp(-2, 1.4, u), lerp(-10, 20, u));
    camera.position.x += noise1(T * 0.8, 3) * 0.08; camera.updateProjectionMatrix();
  }};
}
