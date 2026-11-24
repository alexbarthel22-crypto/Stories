// Weltall. orbit (Stufe 5): Ohne Schwerkraft fliegt die Erde geradeaus aus ihrer Bahn, die Lufthülle löst sich vom Rand.
// core (Stufe 6): Schnitt durch die Erde – nichts hält den Druck im Inneren mehr zusammen, die Kruste hebt sich (Gedankenexperiment).
// quake (Stufe 7): Die Schwerkraft ist zurück, die Kruste kracht zurück – glühende Risse um die ganze Erde, Vulkane.
import {THREE, mat, mesh, rng, clamp, smooth, lerp, noise1, canvasTex, easeIn, easeOut} from './lib.js';
import {particles, updateParticles, flicker} from './fx.js';
import {VANISH, RETURN, CRASH} from './timeline.js';
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

// Wertrauschen für Kontinente
function makeNoise(seed) { const r = rng(seed); const N = 256, p = new Float32Array(N * N); for (let i = 0; i < N * N; i++) p[i] = r();
  const at = (x, y) => p[((y % N + N) % N) * N + ((x % N + N) % N)];
  const v = (x, y) => { const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi, sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
    return lerp(lerp(at(xi, yi), at(xi + 1, yi), sx), lerp(at(xi, yi + 1), at(xi + 1, yi + 1), sx), sy); };
  return (x, y) => { let s = 0, a = 0.5, f = 1; for (let o = 0; o < 6; o++) { s += a * v(x * f, y * f); a *= 0.5; f *= 2; } return s; }; }

export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#02030a');
  const sunDir = V3(-1, 0.25, 0.35).normalize();
  const key = new THREE.DirectionalLight('#fff6e8', 3.2); key.position.copy(sunDir).multiplyScalar(50); scene.add(key);
  const amb = new THREE.AmbientLight('#1b2238', 0.35); scene.add(amb);
  // Sterne
  { const r = rng(5), n = 2500, P = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const v = V3(r() - 0.5, r() - 0.5, r() - 0.5).normalize().multiplyScalar(300); P.set([v.x, v.y, v.z], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(P, 3)); scene.add(new THREE.Points(g, new THREE.PointsMaterial({color: '#ffffff', size: 1.1, sizeAttenuation: false}))); }
  // Sonne
  const sunTex = canvasTex(256, 256, (g, w) => { const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,255,245,1)'); gr.addColorStop(0.12, 'rgba(255,245,210,1)'); gr.addColorStop(0.3, 'rgba(255,200,110,0.45)'); gr.addColorStop(1, 'rgba(255,150,60,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
  const sunS = new THREE.Sprite(new THREE.SpriteMaterial({map: sunTex, blending: THREE.AdditiveBlending, depthWrite: false})); sunS.position.copy(sunDir).multiplyScalar(120); sunS.scale.setScalar(40); scene.add(sunS);

  // Erde: Farbe, Wolken, Risse (leuchtend)
  const nz = makeNoise(11), nz2 = makeNoise(29);
  const W = 1024, H = 512; const land = new Float32Array(W * H);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const u = x / W * 8, v = y / H * 4; const f = uu => nz(uu + 0.37 * Math.sin(v), v) + 0.25 * nz2(uu * 2, v * 2); land[y * W + x] = ((8 - u) * f(u) + u * f(u - 8)) / 8 - 0.12 * Math.abs(Math.cos(Math.PI * y / H)); }
  const colT = canvasTex(W, H, (g) => { const img = g.createImageData(W, H);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const h = land[y * W + x], lat = Math.abs(y / H - 0.5) * 2, i = (y * W + x) * 4; let c;
      if (lat > 0.86) c = [235, 240, 245]; else if (h < 0.53) { const d = clamp((0.53 - h) * 5); c = [lerp(40, 12, d), lerp(90, 40, d), lerp(150, 105, d)]; }
      else { const dry = clamp((h - 0.6) * 4) * (1 - lat); c = lat > 0.72 ? [200, 205, 200] : [lerp(70, 180, dry), lerp(120, 150, dry), lerp(55, 90, dry)]; }
      img.data[i] = c[0]; img.data[i + 1] = c[1]; img.data[i + 2] = c[2]; img.data[i + 3] = 255; }
    g.putImageData(img, 0, 0); });
  const cloudT = canvasTex(W, H, (g) => { const img = g.createImageData(W, H); const nc = makeNoise(77);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const v = nc(x / W * 12, y / H * 6); const a = clamp((v - 0.52) * 4) * 255; const i = (y * W + x) * 4; img.data[i] = img.data[i + 1] = img.data[i + 2] = 255; img.data[i + 3] = a; }
    g.putImageData(img, 0, 0); });
  // Bruchzonen: einmal erzeugte Pfade, gezeichnet als (a) dunkle Spalten mit Staubsaum (Oberfläche) und (b) sehr feine Glut tief im Spalt
  const paths = []; { const r = rng(41); const gen = (x, y, a, n, wd, depth) => { const pts = [[x, y]]; for (let k = 0; k < n; k++) { a += (r() - 0.5) * 0.7; x += Math.cos(a) * 18; y += Math.sin(a) * 9; pts.push([x, y]);
      if (r() < 0.07 && depth < 2) gen(x, y, a + (r() < 0.5 ? 1 : -1) * (0.6 + r()), Math.floor(n / 2), wd * 0.55, depth + 1); } paths.push({pts, wd}); };
    for (let i = 0; i < 26; i++) gen(r() * 2048, 1024 * (0.15 + r() * 0.7), r() * 7, 30 + Math.floor(r() * 40), 3 + r() * 5, 0); }
  const drawPaths = (g, wMul, style, blur = 0) => { g.lineJoin = 'round'; g.lineCap = 'round'; g.shadowBlur = blur; g.shadowColor = style; g.strokeStyle = style;
    for (const p of paths) for (const off of [-2048, 0, 2048]) { g.lineWidth = p.wd * wMul; g.beginPath(); p.pts.forEach(([x, y], i) => i ? g.lineTo(x + off, y) : g.moveTo(x + off, y)); g.stroke(); } g.shadowBlur = 0; };
  const crackT = canvasTex(2048, 1024, (g, w, h) => { g.fillStyle = '#000'; g.fillRect(0, 0, w, h); drawPaths(g, 0.22, '#ff7a2a'); });
  const riftT = canvasTex(2048, 1024, (g, w, h) => { g.clearRect(0, 0, w, h);
    drawPaths(g, 5.5, 'rgba(176,150,118,0.22)', 18);   // Staubsaum
    drawPaths(g, 2.4, 'rgba(120,96,72,0.55)', 6);      // aufgeworfene Ränder
    drawPaths(g, 1.0, 'rgba(28,18,12,0.95)');          // Spalte
  });
  const earthM = new THREE.MeshStandardMaterial({map: colT, roughness: 0.85, metalness: 0, emissive: '#ffffff', emissiveMap: crackT, emissiveIntensity: 0});
  const earth = new THREE.Group(); scene.add(earth);
  const ball = mesh(new THREE.SphereGeometry(1, 96, 64), earthM, 0, 0, 0, earth); ball.castShadow = ball.receiveShadow = false;
  const cut = mesh(new THREE.SphereGeometry(1, 96, 64, 0, Math.PI * 1.5), new THREE.MeshStandardMaterial({map: colT, roughness: 0.85, emissive: '#ffffff', emissiveMap: crackT, emissiveIntensity: 0, side: THREE.DoubleSide}), 0, 0, 0, earth);
  const riftM = new THREE.MeshStandardMaterial({map: riftT, transparent: true, depthWrite: false, roughness: 1, opacity: 0});
  const rift = mesh(new THREE.SphereGeometry(1.004, 96, 64), riftM, 0, 0, 0, earth); rift.castShadow = false;
  const riftCut = mesh(new THREE.SphereGeometry(1.004, 96, 64, 0, Math.PI * 1.5), riftM, 0, 0, 0, earth); riftCut.castShadow = false;
  const clouds = mesh(new THREE.SphereGeometry(1.012, 64, 48), new THREE.MeshStandardMaterial({map: cloudT, transparent: true, depthWrite: false, roughness: 1}), 0, 0, 0, earth);
  // Atmosphäre: Leuchtsaum (Fresnel)
  const atmoM = new THREE.ShaderMaterial({uniforms: {c: {value: new THREE.Color('#6fb4ff')}, a: {value: 1}, p: {value: 3.2}}, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.BackSide,
    vertexShader: 'varying vec3 n; varying vec3 v; void main(){ n = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position,1.0); v = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }',
    fragmentShader: 'uniform vec3 c; uniform float a; uniform float p; varying vec3 n; varying vec3 v; void main(){ float f = pow(1.0 - abs(dot(n, v)), p); gl_FragColor = vec4(c * f * 1.6, f * a); }'});
  const atmo = mesh(new THREE.SphereGeometry(1.09, 64, 48), atmoM, 0, 0, 0, earth); atmo.castShadow = false;
  const atmo2 = mesh(new THREE.SphereGeometry(1.09, 64, 48), atmoM.clone(), 0, 0, 0, earth); atmo2.castShadow = false;
  const wisps = particles(900, 'smoke'); scene.add(wisps);
  // Schnittflächen: Schichten der Erde
  const layerT = canvasTex(1024, 1024, (g, w) => { const c = w / 2; const ring = (r, a, b) => { const gr = g.createRadialGradient(c, c, r * 0.6, c, c, r); gr.addColorStop(0, a); gr.addColorStop(1, b); g.fillStyle = gr; g.beginPath(); g.arc(c, c, r, 0, 7); g.fill(); };
    ring(c, '#e05a1a', '#8a2a10'); ring(c * 0.985, '#d24a14', '#b43a12'); ring(c * 0.55, '#ffb43a', '#f07a1a'); ring(c * 0.19, '#fffbe0', '#ffd870');
    g.strokeStyle = 'rgba(70,40,25,0.9)'; g.lineWidth = 10; g.beginPath(); g.arc(c, c, c - 5, 0, 7); g.stroke(); });
  const capM = new THREE.MeshStandardMaterial({map: layerT, emissive: '#ffffff', emissiveMap: layerT, emissiveIntensity: 0.55, side: THREE.DoubleSide, roughness: 0.9});
  const caps = new THREE.Group(); earth.add(caps);
  for (const ry of [Math.PI, Math.PI / 2]) { const c = new THREE.Mesh(new THREE.CircleGeometry(1, 96, -Math.PI / 2, Math.PI), capM); c.rotation.y = ry; caps.add(c); }
  // Druckwellen-Ring beim Aufprall
  const ringM = new THREE.MeshBasicMaterial({color: '#ffb070', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide});
  const shock = new THREE.Mesh(new THREE.RingGeometry(1, 1.06, 96), ringM); scene.add(shock);
  // Vulkane / Glut
  const plumes = particles(1000, 'smoke'); scene.add(plumes); const lava = particles(700, 'flame'); scene.add(lava);
  // Mond
  const moonT = canvasTex(256, 128, (g, w, h) => { g.fillStyle = '#9a9a96'; g.fillRect(0, 0, w, h); const r = rng(8); for (let i = 0; i < 120; i++) { g.fillStyle = `rgba(${r() < 0.5 ? 60 : 200},${r() < 0.5 ? 60 : 200},${r() < 0.5 ? 60 : 200},0.25)`; g.beginPath(); g.arc(r() * w, r() * h, 2 + r() * 9, 0, 7); g.fill(); } });
  const moon = mesh(new THREE.SphereGeometry(0.27, 32, 24), new THREE.MeshStandardMaterial({map: moonT, roughness: 1}), 0, 0, 0, scene);
  // Bahn (gestrichelt, gekrümmt) und gerade Linie
  const R0 = 7;
  const arcPts = []; for (let i = -40; i <= 40; i++) { const a = i / 40 * 0.9; arcPts.push(V3(-R0 + R0 * Math.cos(a), 0, R0 * Math.sin(a))); }
  const dotM = new THREE.MeshBasicMaterial({color: '#ffffff', transparent: true, opacity: 0.7});
  const arc = new THREE.Group(); scene.add(arc); arcPts.forEach((p, i) => { if (i % 2) return; const m = new THREE.Mesh(new THREE.SphereGeometry(0.025, 8, 6), dotM); m.position.copy(p); arc.add(m); });
  const strM = new THREE.MeshBasicMaterial({color: '#ffb35a', transparent: true, opacity: 0.9});
  const straight = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 8.2, 8), strM); straight.rotation.x = Math.PI / 2; straight.position.set(0, 0, 3.9); scene.add(straight);
  const tagT = (t, c) => canvasTex(512, 96, (g, w, h) => { g.font = '500 44px Plex, monospace'; g.fillStyle = c; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(t, w / 2, h / 2); });
  const tagOld = new THREE.Sprite(new THREE.SpriteMaterial({map: tagT('ALTE BAHN', '#ffffff'), transparent: true, depthWrite: false})); tagOld.scale.set(1.5, 0.28, 1); scene.add(tagOld);
  const tagNew = new THREE.Sprite(new THREE.SpriteMaterial({map: tagT('GERADEAUS', '#ffb35a'), transparent: true, depthWrite: false})); tagNew.scale.set(1.5, 0.28, 1); scene.add(tagNew);

  const camera = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.01, 1000); scene.add(camera);
  const vSites = (() => { const r = rng(61); return Array.from({length: 26}, () => [r() * 6.28, (r() - 0.5) * 1.5]); })().map(([lon, lat]) => V3(Math.cos(lat) * Math.cos(lon), Math.sin(lat), Math.cos(lat) * Math.sin(lon)));

  return {scene, camera, update(shot, T) {
    const orbit = shot.id === 'orbit', core = shot.id === 'core', quake = shot.id === 'quake';
    earth.rotation.y = core ? 0.03 * (T - 47) : T * 0.03; clouds.rotation.y = T * 0.008;
    // Bahn: Die Erde fährt die Gerade, die alte Bahn krümmt sich weg (überzeichnet)
    const d = orbit ? (T - 39) * 0.32 : 0; earth.position.set(0, 0, d);
    arc.visible = straight.visible = orbit; tagOld.visible = tagNew.visible = false;
    if (orbit) { const a = smooth(39.4, 40.4, T); dotM.opacity = 0.7 * a; strM.opacity = 0.9 * smooth(41.5, 42.5, T); tagOld.material.opacity = a; tagNew.material.opacity = strM.opacity;
      tagOld.position.set(-1.15, 0.15, 5.3); tagNew.position.set(0.6, 0.15, 5.3); }
    moon.visible = orbit; moon.position.set(2.6 + 0.02 * (T - 39), 0.25, -1.2 + d * 1.1); moon.rotation.y = T * 0.02;
    // Atmosphäre löst sich (ab Mitte der Stufe 5), im Kern-Shot schon dünn
    const leak = orbit ? smooth(43, 47, T) : core ? 1 : quake ? 0.35 : 0;
    atmoM.uniforms.a.value = 1 - 0.55 * leak; atmo2.scale.setScalar(1 + 0.35 * leak); atmo2.material.uniforms.a.value = 0.6 * leak * (1 - 0.6 * leak); atmo2.material.uniforms.p.value = 1.8;
    wisps.visible = orbit && T > 43; if (wisps.visible) { const n = wisps.userData.n; const P = wisps.geometry.attributes.position.array, C = wisps.geometry.attributes.aColor.array, S = wisps.geometry.attributes.aSize.array; const r = rng(3);
      for (let i = 0; i < n; i++) { const dir = V3(r() - 0.5, r() - 0.5, r() - 0.5).normalize(); const t = ((T - 43) * (0.6 + r() * 0.6) + r() * 3) % 3; const rad = 1.05 + t * 0.35;
        P[i * 3] = earth.position.x + dir.x * rad; P[i * 3 + 1] = dir.y * rad; P[i * 3 + 2] = earth.position.z + dir.z * rad; S[i] = 0.12 + t * 0.12; C[i * 4] = 0.45; C[i * 4 + 1] = 0.7; C[i * 4 + 2] = 1; C[i * 4 + 3] = 0.12 * (1 - t / 3) * smooth(43, 44.5, T); }
      wisps.geometry.attributes.position.needsUpdate = wisps.geometry.attributes.aColor.needsUpdate = wisps.geometry.attributes.aSize.needsUpdate = true; }
    // Schnitt
    ball.visible = !core; cut.visible = core; caps.visible = core; clouds.visible = !core; atmo.visible = atmo2.visible = !core;
    const swell = core ? 1 + 0.05 * smooth(50.5, 54.8, T) : quake ? 1 + 0.05 * (1 - smooth(CRASH - 0.25, CRASH + 0.05, T)) : 1;
    cut.scale.setScalar(swell); clouds.scale.setScalar(swell); caps.scale.setScalar(1);
    capM.emissiveIntensity = core ? 0.55 + 0.35 * smooth(49, 54, T) * (0.8 + 0.2 * Math.sin(T * 9)) : 0.55;
    const glowK = core ? 0.35 * smooth(51, 54.8, T) : quake ? (T < CRASH ? 0.2 : 0.2 + 0.5 * smooth(CRASH, CRASH + 1.2, T)) * (0.85 + 0.15 * flicker(T, 3)) : 0;
    riftM.opacity = core ? 0.8 * smooth(50.5, 54.5, T) : quake ? (T < CRASH ? 0.7 : 0.7 + 0.3 * smooth(CRASH, CRASH + 1, T)) : 0; rift.visible = !core && riftM.opacity > 0; riftCut.visible = core && riftM.opacity > 0; rift.scale.setScalar(swell); riftCut.scale.setScalar(swell);
    earthM.emissiveIntensity = cut.material.emissiveIntensity = glowK; ball.scale.setScalar(swell);
    // Aufprall: Druckwelle und Vulkane
    shock.visible = quake && T > CRASH && T < CRASH + 2.5; if (shock.visible) { const k = (T - CRASH) / 2.5; shock.scale.setScalar(1 + k * 2.6); ringM.opacity = 0.8 * (1 - k); shock.lookAt(camera.position); }
    plumes.visible = lava.visible = quake && T > CRASH;
    if (quake) { earth.updateMatrixWorld(true); const src = vSites.map((v, i) => earth.localToWorld(v.clone().multiplyScalar(1.0)));
      updateParticles(plumes, src.map((p, i) => ({pos: p, r: 0.05, t0: CRASH + (i % 9) * 0.12, type: 'smoke', size: 0.26, rise: 0.001, alpha: 0.5, col: i % 3 ? [0.55, 0.48, 0.4] : [0.3, 0.26, 0.24]})), T, V3(0, 0, 0));
      // Rauch steigt radial nach außen: Positionen von der Mitte weg schieben
      const P = plumes.geometry.attributes.position.array; for (let i = 0; i < P.length; i += 3) { if (P[i + 1] < -900) continue; const v = V3(P[i], P[i + 1], P[i + 2]); const L = v.length(); if (L > 0.5) { v.multiplyScalar(1 + (L - 0.98) * 0.4 + 0.02); P[i] = v.x; P[i + 1] = v.y; P[i + 2] = v.z; } }
      plumes.geometry.attributes.position.needsUpdate = true;
      updateParticles(lava, src.filter((p, i) => i % 4 === 0).map((p, i) => ({pos: p.clone().multiplyScalar(1.005), r: 0.01, t0: CRASH + i * 0.15, type: 'flame', size: 0.05, power: 0.6, rise: 0.02})), T, V3(0, 0, 0)); }

    // ---------- Kamera ----------
    let pos, lk; camera.fov = 40; camera.up.set(0, 1, 0);
    const sh = a => V3(noise1(T * 12, 1) * a, noise1(T * 12, 2) * a, noise1(T * 12, 3) * a);
    if (orbit) { const k = smooth(39, 47, T); pos = V3(lerp(-1.6, -2.2, k), lerp(3.0, 3.6, k), d + lerp(7.0, 6.2, k)); lk = V3(lerp(-0.5, -0.7, k), lerp(-0.5, -0.4, k), d + lerp(2.4, 2.2, k)); camera.fov = 50; }
    else if (core) { const k = smooth(47, 55, T); const a = lerp(-2.45, -2.15, k); pos = V3(Math.cos(a) * lerp(5.0, 4.3, k), lerp(1.3, 1.0, k), Math.sin(a) * lerp(5.0, 4.3, k)); lk = V3(0, 0, 0); camera.fov = 42;
      if (T > 52.5) pos.add(sh(0.012 * smooth(52.5, 55, T))); }
    else { const k = smooth(64, 72, T); const a = lerp(2.75, 2.35, k); pos = V3(Math.cos(a) * lerp(5.2, 4.4, k), lerp(1.4, 0.9, k), Math.sin(a) * lerp(5.2, 4.4, k)); lk = V3(0, 0, 0); camera.fov = 42;
      if (T > CRASH - 0.1) pos.add(sh(0.06 * Math.exp(-(T - CRASH) * 1.2))); }
    camera.position.copy(pos); camera.lookAt(lk); camera.updateProjectionMatrix();
  }};
}
