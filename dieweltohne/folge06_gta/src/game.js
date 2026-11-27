// Das Spiel auf dem Fernseher: eigene, generische Open-World-Szene (Küstenstraße bei Sonnenuntergang, Verfolgungsjagd).
// Kein Nachbau echter Spielgrafik. Gerendert in eine Textur, die der Fernseher zeigt.
import * as THREE from 'three';
import {makeCar, rng, canvasTex, skyDome, lerp} from './lib.js';

export function makeGame(renderer, W = 960, H = 540) {
  const rt = new THREE.WebGLRenderTarget(W, H, {samples: 4});
  rt.texture.colorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog('#f2a374', 60, 420);
  scene.add(skyDome('#3c4f8f', '#f08a6a', '#ffd29a', 600));
  const sun = new THREE.Mesh(new THREE.SphereGeometry(18, 24, 16), new THREE.MeshBasicMaterial({color: '#fff1c8', fog: false})); sun.position.set(-160, 40, -520); scene.add(sun);
  scene.add(new THREE.HemisphereLight('#ffc9a0', '#4a3a5a', 1.3));
  const key = new THREE.DirectionalLight('#ffb27a', 2.6); key.position.set(-120, 60, -200); scene.add(key);
  // Meer
  const sea = new THREE.Mesh(new THREE.PlaneGeometry(2000, 2000), new THREE.MeshStandardMaterial({color: '#2b5f86', roughness: 0.15, metalness: 0.4})); sea.rotation.x = -Math.PI / 2; sea.position.set(-1000 + 40, -0.6, 0); scene.add(sea);
  // Straße (endlos entlang -z) + Strand + Stadtseite
  const road = new THREE.Mesh(new THREE.PlaneGeometry(14, 4000), new THREE.MeshStandardMaterial({color: '#3a3b40', roughness: 0.8})); road.rotation.x = -Math.PI / 2; road.position.set(0, 0, -1800); scene.add(road);
  const lines = canvasTex(64, 512, g => { g.fillStyle = '#000'; g.fillRect(0, 0, 64, 512); g.fillStyle = '#e8e2c8'; g.fillRect(28, 0, 8, 256); });
  lines.wrapT = THREE.RepeatWrapping; lines.repeat.set(1, 300);
  const lm = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 4000), new THREE.MeshBasicMaterial({map: lines, transparent: true, blending: THREE.AdditiveBlending})); lm.rotation.x = -Math.PI / 2; lm.position.set(0, 0.02, -1800); scene.add(lm);
  const sand = new THREE.Mesh(new THREE.PlaneGeometry(40, 4000), new THREE.MeshStandardMaterial({color: '#d9b88c', roughness: 1})); sand.rotation.x = -Math.PI / 2; sand.position.set(-27, -0.05, -1800); scene.add(sand);
  const grass = new THREE.Mesh(new THREE.PlaneGeometry(300, 4000), new THREE.MeshStandardMaterial({color: '#6f7a55', roughness: 1})); grass.rotation.x = -Math.PI / 2; grass.position.set(157, -0.03, -1800); scene.add(grass);
  const r = rng(42);
  // Palmen, Laternen, Häuser
  const trunkM = new THREE.MeshStandardMaterial({color: '#6b4f36', roughness: 1}), leafM = new THREE.MeshStandardMaterial({color: '#2f5a32', roughness: 0.9, side: THREE.DoubleSide});
  for (let z = 0; z > -3800; z -= 22) for (const side of [-1, 1]) {
    const p = new THREE.Group(); p.position.set(side * (9.5 + r() * 1.5), 0, z + r() * 6);
    const h = 9 + r() * 5; const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.35, h, 6), trunkM); tr.position.y = h / 2; tr.rotation.z = (r() - 0.5) * 0.2; p.add(tr);
    for (let k = 0; k < 7; k++) { const l = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 4.2), leafM); l.position.set(0, h, 0); l.rotation.set(-1.0, k / 7 * Math.PI * 2, 0); l.translateY(1.8); p.add(l); }
    scene.add(p);
  }
  const bcols = ['#f0e3cf', '#e7c2a8', '#d8d3c8', '#9fb7c6', '#f2d7b8', '#c9a28a'];
  for (let z = 0; z > -3800; z -= 18 + r() * 14) {
    const w = 10 + r() * 14, h = 8 + r() * 40, dd = 10 + r() * 12;
    const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, dd), new THREE.MeshStandardMaterial({color: bcols[r() * bcols.length | 0], roughness: 0.85}));
    b.position.set(24 + w / 2 + r() * 20, h / 2, z); scene.add(b);
  }
  // Spielerauto + Verfolger
  const car = makeCar(3, {color: '#d23b2c'}); scene.add(car);
  const cop = makeCar(2, {color: '#1d2230', ambulance: false}); scene.add(cop);
  const bl = new THREE.PointLight('#3060ff', 0, 30), rl = new THREE.PointLight('#ff2a2a', 0, 30); cop.add(bl); cop.add(rl); bl.position.set(-0.4, 1.8, 0); rl.position.set(0.4, 1.8, 0);
  const traffic = []; for (let i = 0; i < 14; i++) { const c = makeCar(10 + i); c.position.set(r() < 0.5 ? -3.5 : 3.5, 0, -60 - i * 70 - r() * 30); c.rotation.y = c.position.x > 0 ? 0 : Math.PI; scene.add(c); traffic.push(c); }
  const cam = new THREE.PerspectiveCamera(58, W / H, 0.1, 1500);
  // Einblendungen des Spiels (Minikarte, Fahndungssterne als Punkte) – generisch
  const ui = canvasTex(W, H, () => {});
  const uiCanvas = ui.image, ug = uiCanvas.getContext('2d');
  function drawUI(t, mode) {
    ug.clearRect(0, 0, W, H);
    if (mode === 'game') {
      ug.save(); ug.beginPath(); ug.arc(86, H - 86, 62, 0, 7); ug.clip(); ug.fillStyle = 'rgba(30,40,50,0.75)'; ug.fillRect(0, 0, W, H);
      ug.strokeStyle = 'rgba(255,255,255,0.55)'; ug.lineWidth = 6; ug.beginPath(); ug.moveTo(86, H); ug.lineTo(86 + Math.sin(t) * 10, H - 160); ug.stroke(); ug.restore();
      ug.strokeStyle = 'rgba(255,255,255,0.8)'; ug.lineWidth = 3; ug.beginPath(); ug.arc(86, H - 86, 62, 0, 7); ug.stroke();
      ug.fillStyle = '#fff'; ug.beginPath(); ug.moveTo(86, H - 96); ug.lineTo(78, H - 76); ug.lineTo(94, H - 76); ug.fill();
      for (let i = 0; i < 5; i++) { ug.fillStyle = i < 3 ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.25)'; ug.beginPath(); ug.arc(W - 40 - i * 30, 40, 10, 0, 7); ug.fill(); }
      ug.fillStyle = 'rgba(255,255,255,0.9)'; ug.font = '600 22px Plex'; ug.textAlign = 'right'; ug.fillText('$ 1.284.330', W - 26, 84);
    } else if (mode === 'home') {
      const g2 = ug.createLinearGradient(0, 0, W, H); g2.addColorStop(0, '#0d1b3a'); g2.addColorStop(1, '#14306a'); ug.fillStyle = g2; ug.fillRect(0, 0, W, H);
      for (let i = 0; i < 6; i++) { ug.fillStyle = i === 0 ? 'rgba(255,255,255,0.10)' : 'rgba(255,255,255,0.18)'; ug.fillRect(60 + i * 138, 150, i === 0 ? 180 : 118, i === 0 ? 180 : 118); }
      ug.strokeStyle = 'rgba(255,255,255,0.8)'; ug.lineWidth = 3; ug.strokeRect(60, 150, 180, 180); ug.setLineDash([8, 8]); ug.strokeRect(70, 160, 160, 160); ug.setLineDash([]);
      ug.fillStyle = 'rgba(255,255,255,0.92)'; ug.font = '500 26px Plex'; ug.textAlign = 'left'; ug.fillText('Inhalt nicht gefunden', 60, 380);
      ug.fillStyle = 'rgba(255,255,255,0.55)'; ug.font = '400 20px Plex'; ug.fillText('Das Spiel ist auf diesem Gerät nicht mehr verfügbar.', 60, 414);
      ug.fillStyle = 'rgba(255,255,255,0.7)'; ug.font = '400 20px Plex'; ug.textAlign = 'right'; ug.fillText('23:41', W - 40, 50);
    } else if (mode === 'error') {
      ug.fillStyle = '#0b0c10'; ug.fillRect(0, 0, W, H);
    }
    ui.needsUpdate = true;
  }
  let last = -1;
  return {
    texture: rt.texture, ui,
    // mode: 'game' | 'home' | 'black'
    render(t, mode = 'game') {
      drawUI(t, mode);
      if (mode !== 'game' || t === last) return; last = t;
      const z = -t * 34; car.position.set(Math.sin(t * 0.7) * 2.2 + 1.8, 0, z); car.rotation.y = Math.PI + Math.sin(t * 0.7) * -0.12;
      car.userData.body.rotation.z = Math.sin(t * 0.7 + 0.5) * 0.04;
      cop.position.set(Math.sin((t - 0.6) * 0.7) * 2.0 + 1.8, 0, z + 16); cop.rotation.y = Math.PI;
      const flash = Math.sin(t * 18) > 0; bl.intensity = flash ? 40 : 0; rl.intensity = flash ? 0 : 40;
      traffic.forEach((c, i) => { c.position.z += 0; });
      cam.position.set(car.position.x * 0.6 + 0.8, 3.2 + Math.sin(t * 0.9) * 0.2, z + 9.5); cam.lookAt(car.position.x * 0.8, 1.2, z - 14);
      const old = renderer.getRenderTarget(); const tm = renderer.toneMapping;
      renderer.setRenderTarget(rt); renderer.toneMapping = THREE.NoToneMapping; renderer.render(scene, cam);
      renderer.setRenderTarget(old); renderer.toneMapping = tm;
    },
    // ungefähre Lichtfarbe, die der Bildschirm in den Raum wirft
    light(mode) { return mode === 'game' ? new THREE.Color('#ffb48a') : mode === 'home' ? new THREE.Color('#4f74d8') : new THREE.Color('#000000'); },
  };
}
