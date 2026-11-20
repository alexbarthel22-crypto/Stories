// Ostseestrand am Mittag mit Beachvolleyball. Um 12:00 verschwindet der Sand: alles fällt einen Meter tief auf Lehm und Steine, das Meer läuft nach.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, easeOut, noise1, canvasTex, makePerson, posePerson} from './lib.js';
import {makePhone, makeHands, updateScreen} from './phone.js';
import {VANISH} from './timeline.js';
const DROP = 1.0; // so tief liegt der Strand ohne Sand
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

  // Strandleben (alles, was auf dem Sand liegt, kommt in eine Gruppe, die beim Verschwinden fällt)
  const nBefore = scene.children.length;
  const r = rng(8);
  const korbCols = [['#1f5fae', '#ffffff'], ['#e8323c', '#ffffff'], ['#2f9e74', '#ffffff'], ['#f2c230', '#ffffff'], ['#1f5fae', '#f2c230']];
  for (let i = 0; i < 14; i++) { const c = korbCols[i % 5]; const x = (i < 7 ? -30 + i * 3.4 : 7 + (i - 7) * 3.4) + (r() - 0.5); const z = 13 + (i % 3) * 3.2 + r(); if (Math.hypot(x - 7.5, z - 22) < 11) continue; strandkorb(scene, x, z, Math.PI + (r() - 0.5) * 0.4, c[0], c[1]); }
  const umbs = [[-7, 9, '#e8323c', '#ffffff'], [6, 7, '#1f5fae', '#ffffff'], [13, 13, '#f2c230', '#2f9e74'], [-14, 14, '#ff7a2f', '#ffffff'], [-3, 4, '#e86aa6', '#ffffff']];
  const inCourt = (x, z) => Math.abs(x) < 6 && z > -0.5 && z < 17;
  umbs.filter(([x, z]) => !inCourt(x, z)).forEach(([x, z, a, b]) => umbrella(scene, x, z, a, b, (r() - 0.5) * 0.15));
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
  spots.filter(([x, z]) => !inCourt(x, z)).concat([[-13, 15.5], [12.5, 15.8], [-20, 9], [18, 10]]).forEach(([x, z], i) => {
    const tc = [['#e8323c', '#ffffff'], ['#1f5fae', '#f2c230'], ['#2f9e74', '#ffffff'], ['#e86aa6', '#ffffff'], ['#ff7a2f', '#1f5fae']][i % 5];
    const ry = (r() - 0.5) * 0.5; towel(scene, x, z, ry, tc[0], tc[1]);
    const p = bather(i, r); p.position.set(x, 0, z + 0.85); p.rotation.y = Math.PI + ry; scene.add(p);
    // Handy für die Taschenlampe
    const ph = mesh(new THREE.BoxGeometry(0.075, 0.15, 0.01), mat('#111'), 0, -0.33, 0.04, p.userData.armR.userData.fore);
    const glow = mesh(new THREE.PlaneGeometry(0.06, 0.13), new THREE.MeshBasicMaterial({color: '#bcd6ff'}), 0, 0, 0.006, ph); glow.visible = false;
    bathers.push({p, ph, glow, delay: 0.5 + r() * 1.8, sit: r() < 0.25 ? 1 : 0, look: (r() - 0.5) * 0.6});
  });
  // Kinder an der Sandburg
  const castle = scene.children.filter((o, k) => k >= nBefore && o.isMesh && o.material.color && o.material.color.getHexString() === 'd6be8e');
  const kids = [0, 1].map(i => { const k = bather(20 + i, r); k.scale.setScalar(0.62); k.position.set(2.6 + i * 1.2, 0, 3.0 + i * 0.9); k.rotation.y = i ? -2.2 : 2.0; scene.add(k); return k; });
  // Taschenlampen-Kegel (sichtbare Lichtstrahlen)
  const beamTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0.0)'); gr.addColorStop(0.15, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const beams = bathers.map(() => { const b = new THREE.Mesh(new THREE.ConeGeometry(0.9, 6, 20, 1, true), new THREE.MeshBasicMaterial({map: beamTex, color: '#cfe0ff', transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide})); b.geometry.translate(0, -3, 0); scene.add(b); return b; });
  const flash = [0, 1, 2, 3].map(() => { const l = new THREE.SpotLight('#dfe9ff', 0, 30, 0.45, 0.6, 1.5); scene.add(l, l.target); return l; });
  // Beachvolleyballfeld: Netz, Pfosten, Linienbänder, vier Spieler
  const court = new THREE.Group(); court.position.set(0, 0, 8); scene.add(court);
  const tapeM = mat('#2a62c9', {roughness: 0.6});
  for (const [x, z, w, d] of [[-4, 0, 0.05, 16], [4, 0, 0.05, 16], [0, -8, 8, 0.05], [0, 8, 8, 0.05]]) mesh(new THREE.BoxGeometry(w, 0.01, d + 0.05), tapeM, x, 0.006, z, court);
  for (const x of [-4.6, 4.6]) mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.6, 10), mat('#e8e8e4', {metalness: 0.6}), x, 1.3, 0, court);
  const netT = canvasTex(512, 64, (g, w, h) => { g.strokeStyle = 'rgba(20,20,20,0.9)'; g.lineWidth = 2; for (let x = 0; x <= w; x += 8) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); } for (let y = 0; y <= h; y += 8) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
    g.fillStyle = '#1f5fae'; g.fillRect(0, 0, w, 7); g.fillRect(0, h - 5, w, 5); });
  const net = mesh(new THREE.PlaneGeometry(9.2, 1.0), new THREE.MeshStandardMaterial({map: netT, transparent: true, alphaTest: 0.3, side: THREE.DoubleSide}), 0, 2.0, 0, court);
  const players = [[-1.5, -5], [1.8, -3], [-1.2, 3.5], [1.5, 5.5]].map(([x, z], i) => { const p = bather(30 + i, r); p.position.set(x, 0, z); p.rotation.y = z < 0 ? 0 : Math.PI; court.add(p); return p; });
  const vbT = canvasTex(128, 64, (g, w, h) => { g.fillStyle = '#f4f1e8'; g.fillRect(0, 0, w, h); g.fillStyle = '#2a62c9'; g.fillRect(0, 10, w, 12); g.fillStyle = '#f2c230'; g.fillRect(0, 38, w, 12); });
  const vball = mesh(new THREE.SphereGeometry(0.16, 18, 14), new THREE.MeshStandardMaterial({map: vbT, roughness: 0.5}), 0, 2, 8, scene);
  // Ballwechsel: Treffpunkte der Spieler (Feldkoordinaten), alle 1,3 s ein Schlag
  const HITS = [0, 2, 3, 1, 0, 2, 1, 3, 2, 0, 1, 2, 3, 0];
  const hitPos = i => { const pl = players[HITS[i % HITS.length]]; return V3(pl.position.x, 2.4, pl.position.z * 0.92 + 8); };
  // Was unter dem Sand liegt: Lehm, Steine, Muscheln, Verlorenes
  const rockT = canvasTex(1024, 1024, (g, w, h) => { g.fillStyle = '#6b5e4e'; g.fillRect(0, 0, w, h); const q = rng(17);
    for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${40 + q() * 60},${35 + q() * 50},${30 + q() * 40},${0.25 + q() * 0.5})`; g.beginPath(); g.ellipse(q() * w, q() * h, 1 + q() * 9, 1 + q() * 6, q() * 3, 0, 7); g.fill(); }
    for (let i = 0; i < 420; i++) { const x = q() * w, y = q() * h, s = 2 + q() * 7; g.fillStyle = `hsl(${30 + q() * 20},${10 + q() * 15}%,${35 + q() * 25}%)`; g.beginPath(); g.ellipse(x, y, s, s * 0.7, q() * 3, 0, 7); g.fill(); g.fillStyle = 'rgba(255,255,255,0.25)'; g.fillRect(x - s * 0.3, y - s * 0.4, s * 0.4, s * 0.25); }
    for (let i = 0; i < 40; i++) { g.fillStyle = 'rgba(80,110,130,0.35)'; g.beginPath(); g.ellipse(q() * w, q() * h, 20 + q() * 60, 8 + q() * 20, q() * 3, 0, 7); g.fill(); } });
  rockT.wrapS = rockT.wrapT = THREE.RepeatWrapping; rockT.repeat.set(10, 6);
  const rock = mesh(new THREE.PlaneGeometry(200, 120, 80, 40), new THREE.MeshStandardMaterial({map: rockT, roughness: 0.75}), 0, -DROP, 58, scene); rock.rotation.x = -Math.PI / 2;
  rock.geometry.attributes.position.array.set(sand.geometry.attributes.position.array); rock.geometry.computeVertexNormals(); rock.receiveShadow = true;
  const lost = []; { const q = rng(23); const items = [['#c9a227', 0.012, 0.012, 0.012, 'sphere'], ['#222', 0.15, 0.02, 0.06, 'box'], ['#d8d8d8', 0.03, 0.01, 0.03, 'sphere'], ['#1c1c1c', 0.075, 0.008, 0.15, 'box'], ['#3a7d44', 0.07, 0.07, 0.25, 'cyl']];
    for (let i = 0; i < 60; i++) { const [c, a, b, d, k] = items[i % items.length]; const g = k === 'sphere' ? new THREE.SphereGeometry(a * 2, 8, 6) : k === 'cyl' ? new THREE.CylinderGeometry(a * 0.5, a * 0.5, d, 8) : new THREE.BoxGeometry(a, b, d);
      const m = mesh(g, mat(c, {metalness: k === 'sphere' && c === '#c9a227' ? 0.9 : 0.2, roughness: 0.4}), (q() - 0.5) * 30, -DROP + 0.02, 1 + q() * 16, scene); m.rotation.set(k === 'cyl' ? Math.PI / 2 : 0, q() * 6, 0); m.visible = false; lost.push(m); } }
  // Wasser läuft über die Kante nach
  const rushM = new THREE.MeshStandardMaterial({color: '#3d7f95', roughness: 0.15, metalness: 0.2, transparent: true, opacity: 0.85});
  const rush = mesh(new THREE.PlaneGeometry(200, 1), rushM, 0, -DROP + 0.05, 0, scene); rush.rotation.x = -Math.PI / 2; rush.castShadow = false;
  const fall = mesh(new THREE.PlaneGeometry(200, DROP), new THREE.MeshBasicMaterial({map: foamTex, transparent: true, opacity: 0.9, depthWrite: false}), 0, -DROP / 2, 0.2, scene); fall.castShadow = false;
  const dust = mesh(new THREE.PlaneGeometry(200, 3), new THREE.MeshBasicMaterial({color: '#d9c08e', transparent: true, opacity: 0, depthWrite: false}), 0, 0.5, 9, scene);
  // alles auf dem Sand in eine Gruppe
  const dropG = new THREE.Group(); scene.add(dropG);
  scene.children.slice(nBefore).filter(o => o !== dropG && o !== vball && o !== rock && o !== rush && o !== fall && o !== dust && !lost.includes(o) && !o.isLight && !(o.isMesh && o.material.blending === THREE.AdditiveBlending)).forEach(o => dropG.attach(o));
  // Möwen
  const gulls = Array.from({length: 7}, (_, i) => { const g = gull(); scene.add(g); g.userData.ph = r() * 6; g.userData.path = [(r() - 0.5) * 40, 7 + r() * 9, -4 - r() * 20, 2 + r() * 2]; return g; });

  // Handy-POV fürs Intro
  const camera = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.02, 2000); scene.add(camera);
  const phone = makePhone(); phone.userData.caseM.color.set('#f4d9a8'); const hands = makeHands('#e3b08e', '#e3b08e');
  const rig = new THREE.Group(); rig.add(phone, hands); camera.add(rig);
  rig.position.set(0.02, -0.07, -0.29); rig.rotation.set(-0.12, 0.04, -0.03);
  const RT = new THREE.WebGLRenderTarget(432, 936); RT.texture.colorSpace = THREE.SRGBColorSpace;
  const phoneCam = new THREE.PerspectiveCamera(62, 432 / 936, 0.05, 2000);
  const uiC = document.createElement('canvas'); uiC.width = 432; uiC.height = 936; const uiT = new THREE.CanvasTexture(uiC); uiT.colorSpace = THREE.SRGBColorSpace;
  const pw = phone.userData.pw, phh = phone.userData.ph;
  const live = mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: RT.texture, toneMapped: false}), 0, 0, 0.0052, phone);
  const ui = mesh(new THREE.PlaneGeometry(pw * 0.93, phh * 0.955), new THREE.MeshBasicMaterial({map: uiT, transparent: true, toneMapped: false}), 0, 0, 0.0056, phone);
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
    const t = T - shot.t0, gone = T >= VANISH, td = T - VANISH;
    sky.material.uniforms.day.value = 1; sky.material.uniforms.stars.value = 0;
    seaM.uniforms.time.value = T; seaM.uniforms.day.value = 1;
    sun.intensity = 2.6; hemi.intensity = 0.9; night.intensity = 0; scene.environmentIntensity = 0.6; renderer.toneMappingExposure = 1.0;
    // Fall: in 0,45 s einen Meter tief, kleiner Rückprall
    const fallY = gone ? -Math.min(DROP, 4.9 * td * td) + (td > 0.45 ? Math.sin(Math.min(1, (td - 0.45) / 0.25) * Math.PI) * 0.06 : 0) : 0;
    dropG.position.y = fallY; sand.visible = !gone; wet.visible = !gone; castle.forEach(c => c.visible = !gone); lost.forEach(l => l.visible = gone);
    foams.forEach((f, i) => { const ph = (T * 0.22 + i / 3) % 1; f.position.z = lerp(-5, 1.4, Math.sin(ph * Math.PI)); f.material.opacity = 0.75 - ph * 0.3; f.visible = !gone; });
    wet.position.z = 0.5 + Math.sin(T * 0.8) * 0.6;
    const flow = gone ? clamp(td / 6) : 0; rush.visible = fall.visible = gone;
    rush.scale.y = 0.5 + 9 * Math.pow(flow, 0.7); rush.position.z = rush.scale.y / 2; foamTex.offset.y = -T * 2;
    dust.material.opacity = gone ? 0.35 * Math.exp(-td * 1.5) * clamp(td * 8) : 0;
    flag.rotation.y = Math.sin(T * 3) * 0.25;
    ball.position.set(-2.5 + Math.sin(T * 1.3) * 2, 0.2 + Math.abs(Math.sin(T * 2.6)) * 1.6, 6.5 + Math.cos(T * 1.3) * 0.6);
    gulls.forEach((g, i) => { const [x0, y0, z0, sp] = g.userData.path; const flee = gone ? td * 5 : 0;
      g.position.set(x0 + Math.sin(T * 0.25 * sp / 2 + g.userData.ph) * 12 + flee * (i % 2 ? 1 : -1), y0 + Math.sin(T * 0.7 + i) * 0.6 + flee * 0.5, z0 - flee);
      g.rotation.y = Math.cos(T * 0.25 * sp / 2 + g.userData.ph) > 0 ? -Math.PI / 2 : Math.PI / 2;
      const fl = Math.sin(T * (gone ? 14 : 5) + i) * (gone ? 0.8 : 0.35); g.userData.wings[0].rotation.z = -fl; g.userData.wings[1].rotation.z = fl; });
    // Badegäste: liegen, nach dem Fall richten sie sich erschrocken auf
    bathers.forEach((b, i) => { const a = gone ? smooth(VANISH + 0.6 + b.delay * 0.4, VANISH + 1.3 + b.delay * 0.4, T) : 0;
      poseBeach(b.p, (1 - b.sit) * (1 - a), {look: b.look * a}); b.glow.visible = false; beams[i].material.opacity = 0; });
    flash.forEach(l => l.intensity = 0);
    kids.forEach((k, i) => { poseBeach(k, 0, {prop: 0.6}); k.userData.armR.rotation.x = -0.6 + Math.sin(T * 6 + i) * 0.3 * (gone ? 0 : 1); });
    // Volleyball: Ballwechsel, bei VANISH fliegt der Ball weiter und springt auf dem Lehm
    const HT = 1.3, k = Math.floor(T / HT), u = T / HT - k;
    let bp;
    const a0 = hitPos(k), a1 = hitPos(k + 1);
    if (!gone || T < VANISH + 0.2) { bp = a0.clone().lerp(a1, u); bp.y = lerp(a0.y, a1.y, u) + Math.sin(u * Math.PI) * 3.2; }
    else { const kv = Math.floor(VANISH / HT), uv = VANISH / HT - kv; const p0 = hitPos(kv), p1 = hitPos(kv + 1), dt = T - VANISH;
      const vx = (p1.x - p0.x) / HT, vz = (p1.z - p0.z) / HT; let vy = (Math.cos(uv * Math.PI) * Math.PI * 3.2) / HT;
      const x0 = lerp(p0.x, p1.x, uv), z0 = lerp(p0.z, p1.z, uv), y0 = p0.y + Math.sin(uv * Math.PI) * 3.2;
      let y = y0 + vy * dt - 4.9 * dt * dt; const floor = -DROP + 0.11;
      if (y < floor) { const tl = (vy + Math.sqrt(vy * vy + 19.6 * (y0 - floor))) / 9.8, d2 = dt - tl, v2 = (vy - 9.8 * tl) * -0.55; y = Math.max(floor, floor + v2 * d2 - 4.9 * d2 * d2); }
      bp = V3(x0 + vx * Math.min(dt, 2.5) * 0.8, y, z0 + vz * Math.min(dt, 2.5) * 0.8); }
    vball.position.copy(bp); vball.rotation.set(T * 7, T * 3, 0);
    players.forEach((p, i) => { const u2 = p.userData; posePerson(p, {});
      if (!gone) { const next = HITS[(k + 1) % HITS.length] === i, near = next ? smooth(0.55, 0.95, u) : 0;
        p.position.y = next ? Math.max(0, Math.sin(clamp((u - 0.7) / 0.3) * Math.PI) * 0.45) : 0;
        u2.armL.rotation.x = -0.6 - near * 2.2; u2.armR.rotation.x = -0.6 - near * 2.4; u2.legL.userData.knee.rotation.x = u2.legR.userData.knee.rotation.x = 0.4 * (1 - near);
        u2.hips.position.y = 0.92 - 0.1 * (1 - near); }
      else { const sit = smooth(VANISH + 0.35, VANISH + 0.6, T) * (i % 2 ? 1 : 0.6); p.position.y = 0;
        u2.body.rotation.x = -0.9 * sit * (i === 1 ? 1 : 0); u2.armL.rotation.z = -1.4 * smooth(VANISH + 0.1, VANISH + 0.3, T); u2.armR.rotation.z = 1.4 * smooth(VANISH + 0.1, VANISH + 0.3, T);
        u2.legL.userData.knee.rotation.x = u2.legR.userData.knee.rotation.x = 0.9 * sit; u2.hips.position.y = 0.92 - 0.35 * sit;
        if (T > VANISH + 2.5) { u2.armL.rotation.z = -0.3; u2.armR.rotation.z = 0.3; u2.armL.rotation.x = -1.4; u2.head.rotation.x = 0.4; } } });
    // Kamera
    rig.visible = shot.id === 'intro';
    if (shot.id === 'intro') {
      camera.fov = 50; camera.position.set(2.2 + Math.sin(t * 0.4) * 0.05, 1.6 + noise1(T, 3) * 0.01, 19.5 - t * 0.12); camera.lookAt(0.3, 1.6, 6);
      // Handykamera filmt das Spiel
      phoneCam.position.copy(camera.position).add(V3(0.03, -0.08, -0.3)); phoneCam.lookAt(bp.x * 0.5, 1.8, 8); phoneCam.updateProjectionMatrix();
      rig.visible = false; renderer.setRenderTarget(RT); renderer.render(scene, phoneCam); renderer.setRenderTarget(null); rig.visible = true;
      const g = uiC.getContext('2d'); g.clearRect(0, 0, 432, 936); g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(0, 0, 432, 70); g.fillRect(0, 800, 432, 136);
      g.fillStyle = '#ff3b30'; g.beginPath(); g.arc(150, 38, 9, 0, 7); g.fill(); g.fillStyle = '#fff'; g.font = '500 22px Plex'; g.textAlign = 'left'; g.fillText(`REC 00:0${Math.floor(t + 4)}`, 166, 46);
      g.strokeStyle = '#fff'; g.lineWidth = 6; g.beginPath(); g.arc(216, 868, 36, 0, 7); g.stroke(); g.fillStyle = '#ff3b30'; g.beginPath(); g.roundRect(198, 850, 36, 36, 6); g.fill();
      g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 1; for (const x of [144, 288]) { g.beginPath(); g.moveTo(x, 70); g.lineTo(x, 800); g.stroke(); } for (const y of [313, 556]) { g.beginPath(); g.moveTo(0, y); g.lineTo(432, y); g.stroke(); }
      uiT.needsUpdate = true;
    } else if (shot.id === 'wait') {
      const u3 = smooth(0, 6.5, t);
      camera.fov = 50; camera.position.set(lerp(9, 7.5, u3), lerp(3.6, 3.2, u3), lerp(25, 22, u3)); camera.lookAt(lerp(-0.5, 0, u3), lerp(0.9, 0.8, u3), 6);
    } else { // beach_drop: Kamera (in der Hand eines Zuschauers) fällt mit
      const sh = gone ? 0.06 * Math.exp(-td * 2) : 0;
      camera.fov = 50; camera.position.set(7.5 - smooth(1.5, 7, t) * 1.5 + noise1(T * 12, 1) * sh, 3.2 + fallY + noise1(T * 12, 2) * sh, 22 - smooth(1.5, 7, t) * 2); camera.lookAt(0, 0.8 + fallY * 0.8, 6);
    }
    camera.updateProjectionMatrix();
  }};
}
