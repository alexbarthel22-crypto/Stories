// Ostseestrand am Mittag: Strandkörbe, Sonnenschirme, Badegäste. Dann wird es schlagartig Nacht.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, easeOut, noise1, canvasTex, makePerson, posePerson} from './lib.js';
import {makePhone, makeHands, updateScreen} from './phone.js';
import {DARK, VANISH, lightLeft} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const SUN_DIR = V3(0.12, 0.36, -1).normalize();

// Himmel mit Sonne, Sternen und Milchstraße, überblendbar Tag -> Nacht
export function skyMaterial(SUN_DIR = V3(0.12, 0.36, -1).normalize()) {
  return new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {day: {value: 1}, sunDir: {value: SUN_DIR}, sunOn: {value: 1}, stars: {value: 0}},
    vertexShader: 'varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); gl_Position.z = gl_Position.w; }',
    fragmentShader: `
      varying vec3 vDir; uniform float day, sunOn, stars; uniform vec3 sunDir;
      float h(vec3 p){ return fract(sin(dot(p, vec3(127.1,311.7,74.7)))*43758.5453); }
      float n3(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
        return mix(mix(mix(h(i),h(i+vec3(1,0,0)),f.x),mix(h(i+vec3(0,1,0)),h(i+vec3(1,1,0)),f.x),f.y),
                   mix(mix(h(i+vec3(0,0,1)),h(i+vec3(1,0,1)),f.x),mix(h(i+vec3(0,1,1)),h(i+vec3(1,1,1)),f.x),f.y),f.z); }
      void main(){
        vec3 d = normalize(vDir); float y = max(d.y, 0.0);
        vec3 dayC = mix(vec3(0.46,0.64,0.86), vec3(0.04,0.17,0.52), pow(y, 0.4));
        float s = max(dot(d, sunDir), 0.0);
        dayC += vec3(1.0,0.92,0.75) * (pow(s, 8.0)*0.12 + pow(s, 80.0)*0.5 + pow(s, 1500.0)*3.0) * sunOn;
        dayC += vec3(1.0,0.98,0.92) * smoothstep(0.99972, 0.99986, s) * 30.0 * sunOn;
        vec3 col = dayC * day;
        // Nacht: tiefes Blau am Horizont, schwarz oben
        vec3 nightC = mix(vec3(0.020,0.028,0.050), vec3(0.004,0.006,0.014), pow(y, 0.5));
        // Milchstraße: Band schräg über den Himmel
        vec3 ax = normalize(vec3(0.55, 0.35, 0.76)); float band = 1.0 - abs(dot(d, ax));
        float mw = pow(band, 10.0) * (0.45 + 0.9 * n3(d*9.0) * n3(d*23.0+3.0));
        float dust = pow(band, 22.0) * smoothstep(0.45, 0.75, n3(d*14.0+7.0));
        nightC += vec3(0.42,0.44,0.55) * mw * 0.32 - vec3(0.05) * dust;
        // Sterne
        vec3 q = d * 420.0; vec3 c = floor(q); float r = h(c);
        float st = smoothstep(0.9965, 1.0, r) * smoothstep(0.45, 0.0, length(fract(q)-0.5));
        float st2 = smoothstep(0.985, 1.0, h(floor(d*900.0))) * 0.35 * (0.6 + mw*3.0);
        nightC += vec3(0.9,0.93,1.0) * (st * 2.2 + st2) * smoothstep(0.0, 0.08, d.y);
        col = mix(nightC * stars, col, day);
        if (d.y < 0.0) col *= 0.6;
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
}

// Meer: Wellen aus Sinussummen, Sonnenglitzern, Spiegelung des Himmels
function seaMaterial() {
  return new THREE.ShaderMaterial({
    uniforms: {time: {value: 0}, day: {value: 1}, sunDir: {value: SUN_DIR}, sunOn: {value: 1}, lights: {value: 0}},
    vertexShader: 'varying vec3 wp; void main(){ vec4 w = modelMatrix * vec4(position,1.); wp = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: `
      varying vec3 wp; uniform float time, day, sunOn, lights; uniform vec3 sunDir;
      vec2 g(vec2 p, vec2 dir, float fr, float sp, float a){ float ph = dot(p, dir)*fr + time*sp; return dir * cos(ph) * fr * a; }
      void main(){
        vec2 p = wp.xz; vec2 s = vec2(0.0);
        s += g(p, normalize(vec2(0.2,1.0)), 0.35, 1.2, 0.30);
        s += g(p, normalize(vec2(-0.5,1.0)), 0.8, 1.9, 0.12);
        s += g(p, normalize(vec2(0.9,0.6)), 1.9, 2.8, 0.05);
        s += g(p, normalize(vec2(-0.2,-1.0)), 4.3, 4.1, 0.022);
        s += g(p, normalize(vec2(0.7,-0.4)), 9.0, 6.0, 0.010);
        vec3 n = normalize(vec3(-s.x, 1.0, -s.y));
        vec3 v = normalize(cameraPosition - wp);
        float fres = 0.04 + 0.96 * pow(1.0 - max(dot(n, v), 0.0), 5.0);
        vec3 deep = vec3(0.03,0.16,0.24), shallow = vec3(0.10,0.42,0.46);
        float dist = clamp(-wp.z / 25.0, 0.0, 1.0);
        vec3 water = mix(shallow, deep, dist);
        vec3 r = reflect(-v, n); float ry = max(r.y, 0.0);
        vec3 skyC = mix(vec3(0.52,0.68,0.86), vec3(0.10,0.30,0.66), pow(ry, 0.45));
        vec3 col = mix(water * (0.5 + 0.5*max(dot(n, sunDir),0.0)), skyC, fres);
        float spec = pow(max(dot(r, sunDir), 0.0), 350.0) * 40.0 + pow(max(dot(r, sunDir), 0.0), 40.0) * 0.6;
        col += vec3(1.0,0.93,0.8) * spec * sunOn;
        vec3 night = vec3(0.006,0.009,0.016) + vec3(0.05,0.06,0.09) * fres * 0.6;
        col = mix(night, col, day);
        float fogk = 1.0 - exp(-length(cameraPosition - wp) * 0.0018);
        col = mix(col, mix(vec3(0.02,0.03,0.05)*0.6, vec3(0.52,0.68,0.86), day), fogk);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
}

function sandTex() {
  const r = rng(21);
  const t = canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = '#e3cfa4'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 90000; i++) { const v = r(); g.fillStyle = v < 0.5 ? `rgba(120,95,60,${r() * 0.18})` : `rgba(255,250,235,${r() * 0.25})`; g.fillRect(r() * w, r() * h, 1 + r() * 2, 1 + r() * 2); }
    for (let i = 0; i < 160; i++) { const x = r() * w, y = r() * h; g.fillStyle = 'rgba(150,120,80,0.10)'; g.beginPath(); g.ellipse(x, y, 7, 12, r() * 3, 0, 7); g.fill(); } // Fußspuren
    for (let i = 0; i < 40; i++) { g.strokeStyle = 'rgba(160,130,90,0.12)'; g.lineWidth = 3; g.beginPath(); const y = r() * h; g.moveTo(0, y); for (let x = 0; x < w; x += 40) g.lineTo(x, y + Math.sin(x * 0.02 + i) * 8); g.stroke(); }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
function stripeTex(c1, c2, n = 8, vertical = true) {
  return canvasTex(256, 256, (g, w, h) => { for (let i = 0; i < n; i++) { g.fillStyle = i % 2 ? c2 : c1; vertical ? g.fillRect(i * w / n, 0, w / n + 1, h) : g.fillRect(0, i * h / n, w, h / n + 1); } });
}

// Strandkorb: das typische Ostsee-Möbel
function strandkorb(scene, x, z, ry, c1, c2) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; scene.add(g);
  const wicker = mat('#cdb487', {roughness: 0.95}), wood = mat('#f2efe6', {roughness: 0.7});
  const canvas = new THREE.MeshStandardMaterial({map: stripeTex(c1, c2, 10), roughness: 0.85});
  mesh(new THREE.BoxGeometry(1.35, 0.42, 0.95), wood, 0, 0.21, 0, g);                        // Sockel
  mesh(new THREE.BoxGeometry(1.25, 0.1, 0.7), mat('#2f4a6b', {roughness: 0.9}), 0, 0.47, 0.08, g); // Sitzpolster
  mesh(new THREE.BoxGeometry(1.35, 1.0, 0.12), wicker, 0, 0.92, -0.42, g);                    // Rücken
  for (const s of [-1, 1]) mesh(new THREE.BoxGeometry(0.1, 0.62, 0.9), wicker, s * 0.66, 0.73, 0, g); // Armlehnen
  const hood = mesh(new THREE.CylinderGeometry(0.7, 0.7, 0.95, 20, 1, true, -Math.PI / 2, Math.PI), canvas, 0, 1.35, -0.02, g);
  hood.rotation.x = Math.PI / 2; hood.rotation.z = Math.PI / 2; hood.scale.set(1, 1, 0.75); hood.material.side = THREE.DoubleSide;
  mesh(new THREE.BoxGeometry(1.4, 0.06, 1.0), wood, 0, 0.44, 0, g);
  return g;
}
function umbrella(scene, x, z, c1, c2, tilt) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.z = tilt; scene.add(g);
  mesh(new THREE.CylinderGeometry(0.025, 0.025, 2.3, 8), mat('#eeeeee', {metalness: 0.5}), 0, 1.15, 0, g);
  const top = mesh(new THREE.ConeGeometry(1.25, 0.45, 16, 1, true), new THREE.MeshStandardMaterial({map: stripeTex(c1, c2, 16), side: THREE.DoubleSide, roughness: 0.8}), 0, 2.2, 0, g);
  return g;
}
function towel(scene, x, z, ry, c1, c2) {
  const t = mesh(new THREE.PlaneGeometry(0.9, 1.9), new THREE.MeshStandardMaterial({map: stripeTex(c1, c2, 6, false), roughness: 1}), x, 0.012, z, scene);
  t.rotation.x = -Math.PI / 2; t.rotation.z = ry; t.castShadow = false; return t;
}
function gull() {
  const g = new THREE.Group(); const w = mat('#f4f4f2'), gr = mat('#9aa0a6');
  mesh(new THREE.CapsuleGeometry(0.09, 0.32, 4, 8), w, 0, 0, 0, g).rotation.x = Math.PI / 2;
  const wings = [-1, 1].map(s => { const p = new THREE.Group(); p.position.x = s * 0.06; g.add(p); mesh(new THREE.BoxGeometry(0.62, 0.015, 0.2), gr, s * 0.31, 0, 0, p); mesh(new THREE.BoxGeometry(0.2, 0.016, 0.14), mat('#2a2a2a'), s * 0.66, 0, -0.02, p); return p; });
  g.userData.wings = wings; return g;
}

// Badegast: Badekleidung statt Straßenkleidung
const SKINS = ['#f1c7a5', '#d9a47e', '#a8714f', '#f5d3b8', '#e3b08e', '#7a4d33'];
const SUITS = ['#e8323c', '#1f5fae', '#f2c230', '#1a1a1a', '#2f9e74', '#e86aa6', '#ff7a2f', '#ffffff'];
function bather(i, r) {
  const skin = SKINS[i % SKINS.length], suit = SUITS[Math.floor(r() * SUITS.length)], male = i % 2 === 0;
  const p = makePerson(100 + i, {skin, top: male ? skin : suit, pants: suit, shortSleeve: true});
  const u = p.userData, skinM = mat(skin);
  u.armL.children[0].material = skinM; u.armR.children[0].material = skinM;
  u.pl.forEach(g => { g.userData.up.material = skinM; g.userData.low.material = skinM; });
  // Füße barfuß
  [u.legL, u.legR].forEach(l => l.userData.shoe.children.forEach(m => { m.material = skinM; }));
  return p;
}
// Sitzen / Liegen auf dem Handtuch. lie=1 liegt auf dem Rücken, 0 sitzt aufrecht
function poseBeach(p, lie, {phone = 0, look = 0, prop = 0} = {}) {
  posePerson(p, {});
  const u = p.userData;
  u.hips.position.y = 0.13;
  u.legL.rotation.x = u.legR.rotation.x = -Math.PI / 2 + 0.08;
  u.legL.userData.knee.rotation.x = u.legR.userData.knee.rotation.x = 0.1 + (1 - lie) * 0.5;
  u.legL.rotation.z = -0.06; u.legR.rotation.z = 0.06;
  u.torso.rotation.x = lerp(-0.15, -Math.PI / 2 + 0.06, lie) + prop * 0.35;
  u.torso.rotation.y = look * (1 - lie);
  u.head.rotation.x = lie * 0.15 - (1 - lie) * 0.25; // im Sitzen nach oben schauen
  u.armL.rotation.x = lerp(0.5, 0.05, lie); u.armR.rotation.x = lerp(0.5, 0.05, lie);
  u.armL.rotation.z = -0.25 - lie * 0.25; u.armR.rotation.z = 0.25 + lie * 0.25;
  u.armL.userData.fore.rotation.x = -0.2; u.armR.userData.fore.rotation.x = -0.2;
  if (phone > 0) { u.armR.rotation.x = lerp(u.armR.rotation.x, -1.9 - (1 - lie) * 0.4, phone); u.armR.rotation.z = lerp(0.25, 0.05, phone); u.armR.userData.fore.rotation.x = -0.4 * phone; }
  u.pl.forEach((g, i) => { const lg = i ? u.legR : u.legL; g.position.copy(lg.position); g.rotation.copy(lg.rotation); });
}

export async function build(renderer) {
  const scene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), skyMaterial()); sky.renderOrder = -10; scene.add(sky);
  // Umgebungslicht aus einem einfachen Taghimmel
  const envScene = new THREE.Scene(); envScene.background = new THREE.Color('#9fc4ea');
  envScene.add(new THREE.Mesh(new THREE.SphereGeometry(10, 16, 8), new THREE.MeshBasicMaterial({color: '#e8d9b8', side: THREE.BackSide})));
  const pm = new THREE.PMREMGenerator(renderer); const env = pm.fromScene(envScene, 0.02).texture;
  scene.environment = env;
  const hemi = new THREE.HemisphereLight('#bcd8f5', '#d8c29a', 0.9); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff1d8', 3.2); sun.position.copy(SUN_DIR).multiplyScalar(80); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, {left: -30, right: 30, top: 30, bottom: -30, near: 1, far: 200}); sun.shadow.bias = -0.0004;
  scene.add(sun, sun.target); sun.target.position.set(0, 0, 10);
  const night = new THREE.HemisphereLight('#3a4f7a', '#0a0a0a', 0); scene.add(night);

  // Sand, nasser Streifen, Meer, Gischt
  const st = sandTex(); st.repeat.set(14, 10);
  const sand = mesh(new THREE.PlaneGeometry(200, 120, 80, 40), new THREE.MeshStandardMaterial({map: st, roughness: 1}), 0, 0, 58, scene); sand.rotation.x = -Math.PI / 2; sand.castShadow = false;
  const pos = sand.geometry.attributes.position; for (let i = 0; i < pos.count; i++) { const x = pos.getX(i), y = pos.getY(i); const wz = 58 - y; pos.setZ(i, Math.max(0, wz - 30) * 0.05 + Math.sin(x * 0.2) * Math.sin(y * 0.15) * 0.08 * clamp((wz - 2) / 10)); } sand.geometry.computeVertexNormals();
  const wet = mesh(new THREE.PlaneGeometry(200, 4), new THREE.MeshStandardMaterial({color: '#a88f63', roughness: 0.25, metalness: 0.1, transparent: true, opacity: 0.85}), 0, 0.006, 0.5, scene); wet.rotation.x = -Math.PI / 2; wet.castShadow = false;
  const seaM = seaMaterial();
  const sea = new THREE.Mesh(new THREE.PlaneGeometry(2400, 1200), seaM); sea.rotation.x = -Math.PI / 2; sea.position.set(0, 0.0, -598); scene.add(sea);
  const foamTex = canvasTex(512, 64, (g, w, h) => { const r = rng(4); for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(255,255,255,${0.2 + r() * 0.6})`; g.beginPath(); g.ellipse(r() * w, h * 0.5 + (r() - 0.5) * h * 0.6, 2 + r() * 8, 1 + r() * 3, 0, 0, 7); g.fill(); } });
  foamTex.wrapS = THREE.RepeatWrapping; foamTex.repeat.set(20, 1);
  const foams = [0, 1, 2].map(i => { const f = mesh(new THREE.PlaneGeometry(200, 1.2), new THREE.MeshBasicMaterial({map: foamTex, transparent: true, depthWrite: false, opacity: 0.8}), 0, 0.02, -1 - i * 3, scene); f.rotation.x = -Math.PI / 2; f.castShadow = false; return f; });

  // Strandleben
  const r = rng(8);
  const korbCols = [['#1f5fae', '#ffffff'], ['#e8323c', '#ffffff'], ['#2f9e74', '#ffffff'], ['#f2c230', '#ffffff'], ['#1f5fae', '#f2c230']];
  for (let i = 0; i < 14; i++) { const c = korbCols[i % 5]; const x = (i < 7 ? -30 + i * 3.4 : 7 + (i - 7) * 3.4) + (r() - 0.5); strandkorb(scene, x, 13 + (i % 3) * 3.2 + r(), Math.PI + (r() - 0.5) * 0.4, c[0], c[1]); }
  const umbs = [[-7, 9, '#e8323c', '#ffffff'], [6, 7, '#1f5fae', '#ffffff'], [13, 13, '#f2c230', '#2f9e74'], [-14, 14, '#ff7a2f', '#ffffff'], [-3, 4, '#e86aa6', '#ffffff']];
  umbs.forEach(([x, z, a, b]) => umbrella(scene, x, z, a, b, (r() - 0.5) * 0.15));
  // DLRG-Turm
  const tower = new THREE.Group(); tower.position.set(-19, 0, 6); scene.add(tower);
  for (const [x, z] of [[-0.8, -0.8], [0.8, -0.8], [-0.8, 0.8], [0.8, 0.8]]) mesh(new THREE.BoxGeometry(0.12, 3, 0.12), mat('#f2efe6'), x, 1.5, z, tower);
  mesh(new THREE.BoxGeometry(2, 1.4, 2), mat('#d8352a'), 0, 3.7, 0, tower);
  mesh(new THREE.BoxGeometry(2.1, 0.35, 2.1), mat('#f2c230'), 0, 4.55, 0, tower);
  mesh(new THREE.BoxGeometry(1.6, 0.6, 0.05), mat('#1c2630', {roughness: 0.1, metalness: 0.6}), 0, 3.8, -1.01, tower);
  const flag = mesh(new THREE.PlaneGeometry(0.8, 0.5), new THREE.MeshStandardMaterial({color: '#d8352a', side: THREE.DoubleSide}), 0.45, 5.9, 0, tower);
  mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.6, 6), mat('#ddd'), 0, 5.5, 0, tower);
  // Sandburg, Eimer, Ball, Kühlbox
  mesh(new THREE.CylinderGeometry(0.5, 0.65, 0.4, 12), mat('#d6be8e', {roughness: 1}), 3.2, 0.2, 3.6, scene);
  for (let k = 0; k < 4; k++) mesh(new THREE.CylinderGeometry(0.14, 0.17, 0.35, 10), mat('#d6be8e', {roughness: 1}), 3.2 + Math.cos(k * 1.57) * 0.45, 0.55, 3.6 + Math.sin(k * 1.57) * 0.45, scene);
  mesh(new THREE.CylinderGeometry(0.14, 0.11, 0.22, 12), mat('#2f8fe0'), 4.2, 0.11, 3.3, scene);
  const ball = mesh(new THREE.SphereGeometry(0.2, 16, 12), new THREE.MeshStandardMaterial({map: stripeTex('#e8323c', '#ffffff', 6), roughness: 0.4}), -2.5, 0.2, 6.5, scene);
  mesh(new THREE.BoxGeometry(0.6, 0.38, 0.4), mat('#2f6fd0'), 7.6, 0.19, 9.4, scene);
  // Segelboote am Horizont
  for (const [x, z] of [[-60, -160], [45, -230], [140, -300]]) { const b = new THREE.Group(); b.position.set(x, 0, z); scene.add(b); mesh(new THREE.BoxGeometry(5, 0.8, 1.4), mat('#f4f4f2'), 0, 0.4, 0, b); const s = mesh(new THREE.ConeGeometry(2.2, 7, 3), mat('#ffffff'), 0, 4.5, 0, b); s.scale.z = 0.08; }

  // Badegäste auf Handtüchern
  const bathers = [];
  const spots = [[-4.5, 7.5], [-2.8, 10.5], [1.0, 9.0], [4.2, 6.8], [8.5, 10.2], [-9.5, 11], [-12, 8], [11.5, 7.5], [-1.0, 12.5], [5.5, 4.0], [-6, 4.5], [14.5, 4], [-16, 4.5], [0.6, 5.2]];
  spots.forEach(([x, z], i) => {
    const tc = [['#e8323c', '#ffffff'], ['#1f5fae', '#f2c230'], ['#2f9e74', '#ffffff'], ['#e86aa6', '#ffffff'], ['#ff7a2f', '#1f5fae']][i % 5];
    const ry = (r() - 0.5) * 0.5; towel(scene, x, z, ry, tc[0], tc[1]);
    const p = bather(i, r); p.position.set(x, 0, z + 0.85); p.rotation.y = Math.PI + ry; scene.add(p);
    // Handy für die Taschenlampe
    const ph = mesh(new THREE.BoxGeometry(0.075, 0.15, 0.01), mat('#111'), 0, -0.33, 0.04, p.userData.armR.userData.fore);
    const glow = mesh(new THREE.PlaneGeometry(0.06, 0.13), new THREE.MeshBasicMaterial({color: '#bcd6ff'}), 0, 0, 0.006, ph); glow.visible = false;
    bathers.push({p, ph, glow, delay: 0.5 + r() * 1.8, sit: r() < 0.25 ? 1 : 0, look: (r() - 0.5) * 0.6});
  });
  // Kinder an der Sandburg
  const kids = [0, 1].map(i => { const k = bather(20 + i, r); k.scale.setScalar(0.62); k.position.set(2.6 + i * 1.2, 0, 3.0 + i * 0.9); k.rotation.y = i ? -2.2 : 2.0; scene.add(k); return k; });
  // Taschenlampen-Kegel (sichtbare Lichtstrahlen)
  const beamTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0.0)'); gr.addColorStop(0.15, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const beams = bathers.map(() => { const b = new THREE.Mesh(new THREE.ConeGeometry(0.9, 6, 20, 1, true), new THREE.MeshBasicMaterial({map: beamTex, color: '#cfe0ff', transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide})); b.geometry.translate(0, -3, 0); scene.add(b); return b; });
  const flash = [0, 1, 2, 3].map(() => { const l = new THREE.SpotLight('#dfe9ff', 0, 30, 0.45, 0.6, 1.5); scene.add(l, l.target); return l; });
  // Möwen
  const gulls = Array.from({length: 7}, (_, i) => { const g = gull(); scene.add(g); g.userData.ph = r() * 6; g.userData.path = [(r() - 0.5) * 40, 7 + r() * 9, -4 - r() * 20, 2 + r() * 2]; return g; });

  // Handy-POV fürs Intro
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 2000); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#f4d9a8'); const hands = makeHands('#e3b08e', '#e3b08e');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig);
  rig.position.set(0.02, -0.07, -0.29); rig.rotation.set(-0.12, 0.04, -0.03);
  const grains = (() => { const q = rng(5); return Array.from({length: 120}, () => [q() * 600, q() * 1300, 1 + q() * 3.5, q()]); })();

  function drawPhone(g, st, SW, SH) {
    const gr = g.createLinearGradient(0, 0, 0, SH); gr.addColorStop(0, '#3b8fd9'); gr.addColorStop(0.6, '#8cc7f0'); gr.addColorStop(1, '#f7e3b5');
    g.fillStyle = gr; g.fillRect(0, 0, SW, SH);
    g.fillStyle = '#fff'; g.textAlign = 'center';
    g.font = '500 30px Plex'; g.fillText('Samstag, 12. Juli', SW / 2, 220);
    g.font = '300 150px Garamond'; g.fillText(st.clock, SW / 2, 380);
    g.font = '500 24px Plex'; g.textAlign = 'left'; g.fillText(st.clock, 40, 52); g.textAlign = 'right'; g.fillText('5G  71%', SW - 40, 52);
    // Wetter-Widget
    g.fillStyle = 'rgba(255,255,255,0.28)'; g.beginPath(); g.roundRect(40, 450, SW - 80, 230, 34); g.fill();
    g.fillStyle = '#ffd34d'; g.beginPath(); g.arc(130, 565, 48, 0, 7); g.fill();
    g.strokeStyle = '#ffd34d'; g.lineWidth = 7; for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4; g.beginPath(); g.moveTo(130 + Math.cos(a) * 62, 565 + Math.sin(a) * 62); g.lineTo(130 + Math.cos(a) * 80, 565 + Math.sin(a) * 80); g.stroke(); }
    g.fillStyle = '#fff'; g.textAlign = 'left'; g.font = '400 96px Garamond'; g.fillText('31°', 230, 590);
    g.font = '500 24px Plex'; g.fillText('Sonnig · UV-Index 8', 230, 630); g.fillText('Warnemünde', 230, 500);
  }
  function overlay(g, SW, SH) { // Sandkörner und Sonnencreme-Schlieren auf dem Glas
    g.save(); g.globalAlpha = 0.18; g.strokeStyle = '#fff'; g.lineWidth = 26; g.beginPath(); g.moveTo(80, 1150); g.quadraticCurveTo(260, 980, 480, 1060); g.stroke(); g.restore();
    for (const [x, y, s, v] of grains) { g.fillStyle = `rgba(${200 + v * 40},${170 + v * 40},${120 + v * 30},0.95)`; g.beginPath(); g.ellipse(x, y, s, s * 0.8, v * 3, 0, 7); g.fill(); g.fillStyle = 'rgba(255,255,255,0.7)'; g.fillRect(x - s * 0.4, y - s * 0.5, s * 0.5, s * 0.4); }
    const lg = g.createLinearGradient(0, 0, SW, SH); lg.addColorStop(0.35, 'rgba(255,255,255,0)'); lg.addColorStop(0.45, 'rgba(255,255,255,0.22)'); lg.addColorStop(0.55, 'rgba(255,255,255,0)'); g.fillStyle = lg; g.fillRect(0, 0, SW, SH); // Sonnenreflex
  }

  return {scene, camera, update(shot, T) {
    const t = T - shot.t0;
    const dk = T >= DARK ? 1 : 0;                               // Licht ist schlagartig weg
    const day = 1 - dk;
    sky.material.uniforms.day.value = day; sky.material.uniforms.stars.value = dk ? smooth(DARK + 0.3, DARK + 2.5, T) : 0;
    seaM.uniforms.time.value = T; seaM.uniforms.day.value = day;
    sun.intensity = 2.6 * day; hemi.intensity = 0.9 * day; night.intensity = dk ? 0.05 + 0.1 * smooth(DARK + 0.3, DARK + 3, T) : 0;
    scene.environmentIntensity = day * 0.6 + dk * 0.02;
    renderer.toneMappingExposure = dk ? 1.35 : 1.0;
    wet.position.z = 0.5 + Math.sin(T * 0.8) * 0.6;
    foams.forEach((f, i) => { const ph = (T * 0.22 + i / 3) % 1; f.position.z = lerp(-5, 1.4, Math.sin(ph * Math.PI)); f.material.opacity = (0.75 - ph * 0.3) * (day + dk * 0.08); });
    flag.rotation.y = Math.sin(T * 3) * 0.25;
    ball.position.set(-2.5 + Math.sin(T * 1.3) * 2, 0.2 + Math.abs(Math.sin(T * 2.6)) * 1.6 * day, 6.5 + Math.cos(T * 1.3) * 0.6);
    // Möwen: fliegen ruhig, bei Dunkelheit davon
    gulls.forEach((g, i) => { const [x0, y0, z0, sp] = g.userData.path; const flee = dk ? (T - DARK) * 6 : 0;
      g.position.set(x0 + Math.sin(T * 0.25 * sp / 2 + g.userData.ph) * 12 + flee * (i % 2 ? 1 : -1), y0 + Math.sin(T * 0.7 + i) * 0.6 + flee * 0.6, z0 - flee);
      g.rotation.y = Math.cos(T * 0.25 * sp / 2 + g.userData.ph) > 0 ? -Math.PI / 2 : Math.PI / 2;
      const fl = Math.sin(T * (dk ? 16 : 5) + i) * (dk ? 0.8 : 0.35); g.userData.wings[0].rotation.z = -fl; g.userData.wings[1].rotation.z = fl; g.visible = !dk || T < DARK + 4; });
    // Badegäste
    let fi = 0;
    bathers.forEach((b, i) => {
      const a = dk ? smooth(DARK + 0.25 + b.delay * 0.4, DARK + 0.9 + b.delay * 0.4, T) : 0;
      const ph = dk ? smooth(DARK + 1.3 + b.delay, DARK + 1.8 + b.delay, T) : 0;
      poseBeach(b.p, (1 - b.sit) * (1 - a), {phone: ph, look: b.look});
      b.glow.visible = ph > 0.5;
      const beam = beams[i]; beam.material.opacity = ph > 0.5 ? 0.07 : 0;
      if (ph > 0.5) {
        const wp = new THREE.Vector3(); b.ph.getWorldPosition(wp);
        const dir = new THREE.Vector3(Math.sin(b.look + T * 0.4 + i) * 0.5, 0.25 + 0.2 * Math.sin(T * 0.6 + i), -1).normalize();
        beam.position.copy(wp); beam.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir);
        if (fi < flash.length) { const l = flash[fi++]; l.position.copy(wp); l.target.position.copy(wp).addScaledVector(dir, 10); l.intensity = 30; }
      }
    });
    for (; fi < flash.length; fi++) flash[fi].intensity = 0;
    kids.forEach((k, i) => { poseBeach(k, 0, {prop: 0.6}); k.userData.armR.rotation.x = -0.6 + Math.sin(T * 6 + i) * 0.3 * day; });

    // Kamera
    rig.visible = shot.id === 'intro';
    if (shot.id === 'intro') {
      camera.fov = 50; camera.position.set(1.0 + Math.sin(t * 0.4) * 0.05, 1.05 + noise1(T, 3) * 0.01, 16.5 - t * 0.12); camera.lookAt(-0.5, 1.6, -10);
      const s = Math.floor(51 * 60 + 40 + t);
      updateScreen(phone, [], {t: T, noDrops: true, clock: `11:${String(Math.floor(s / 60) % 60).padStart(2, '0')}`, custom: drawPhone, overlay});
    } else if (shot.id === 'wait') {
      const u = smooth(0, 6.5, t);
      camera.fov = 42; camera.position.set(lerp(-3, 1.5, u), lerp(3.4, 1.8, u), lerp(27, 18.5, u)); camera.lookAt(lerp(-1, 0.5, u), lerp(1.2, 1.5, u), -6);
    } else { // beach_dark: ruhig, Blick hebt sich zu den Sternen
      const u = smooth(0.8, 5.8, t);
      camera.fov = 46; camera.position.set(1.5, 1.8 + u * 0.2, 18.5 - u * 0.6); camera.lookAt(0.5, lerp(1.5, 7.5, u), lerp(-6, -10, u));
      camera.position.x += noise1(T * 0.7, 4) * 0.03;
    }
    camera.updateProjectionMatrix();
  }};
}
