// Himmel: Farbverlauf (oben Dunkelblau -> Horizont Orange/Rosa), gemalte Wolken, Sonnenglühen.
import * as THREE from 'three';
import { canvasTex, rng } from './toon.js';

export const SKIES = {
  abend: { top: '#2f4590', mid: '#6a5f9e', low: '#f08a5c', horizon: '#ffb47a', sunAz: 0, sunEl: 3, glow: '#ffd29a',
    cloudLit: '#f2846a', cloudShade: '#a56a8a', fog: '#e9a27e', sunColor: '#ffe2c4', sunI: 2.0, amb: '#b6a8c8', ambI: 1.2, sunDir: [0.45, 0.55, 0.7] },
  tag: { top: '#2f6fd6', mid: '#5f9ae6', low: '#a9cdf0', horizon: '#dfeaf2', sunAz: 40, sunEl: 50, glow: '#ffffff',
    cloudLit: '#ffffff', cloudShade: '#b9c6d8', fog: '#c9dbea', sunColor: '#fff6e8', sunI: 2.4, amb: '#c8d6ea', ambI: 1.4, sunDir: [0.4, 0.8, 0.45] },
  daemmerung: { top: '#1d2a52', mid: '#3e4778', low: '#a86a7e', horizon: '#e5937a', sunAz: 0, sunEl: -2, glow: '#f0a080',
    cloudLit: '#c8708a', cloudShade: '#5a4a72', fog: '#8a7090', sunColor: '#d8b0c0', sunI: 1.2, amb: '#7a7fae', ambI: 1.3, sunDir: [0.45, 0.5, 0.75] },
};

export function buildSky(scene, preset = 'abend', seed = 7) {
  const P = SKIES[preset] || SKIES.abend;
  const g = new THREE.Group(); g.name = 'sky';
  const sunDir = new THREE.Vector3().setFromSphericalCoords(1, THREE.MathUtils.degToRad(90 - P.sunEl), THREE.MathUtils.degToRad(180 + P.sunAz));
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      cTop: { value: new THREE.Color(P.top) }, cMid: { value: new THREE.Color(P.mid) }, cLow: { value: new THREE.Color(P.low) },
      cHor: { value: new THREE.Color(P.horizon) }, cGlow: { value: new THREE.Color(P.glow) }, uSun: { value: sunDir },
    },
    vertexShader: `varying vec3 vD; void main(){ vD = normalize(position); vec4 p = modelViewMatrix*vec4(position,1.0); gl_Position = projectionMatrix*p; }`,
    fragmentShader: `
      uniform vec3 cTop,cMid,cLow,cHor,cGlow,uSun; varying vec3 vD;
      void main(){
        float y = vD.y;
        vec3 c = mix(cHor, cLow, smoothstep(-0.02, 0.07, y));
        c = mix(c, cMid, smoothstep(0.07, 0.2, y));
        c = mix(c, cTop, smoothstep(0.18, 0.42, y));
        float s = max(dot(normalize(vD), uSun), 0.0);
        c = mix(c, cGlow, pow(s, 18.0) * 0.55 * (1.0 - smoothstep(0.0, 0.3, y)));
        gl_FragColor = vec4(c,1.0);
        #include <colorspace_fragment>
      }`,
    side: THREE.BackSide, depthWrite: false, fog: false,
  });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(2000, 48, 24), mat);
  dome.renderOrder = -10; dome.frustumCulled = false; g.add(dome);

  // Wolken: weiche, gemalte Schlieren auf großen Flächen, die zur Mitte zeigen
  const r = rng(seed);
  for (let i = 0; i < 14; i++) {
    const tex = canvasTex(512, 160, (ctx, w, h) => {
      ctx.filter = 'blur(5px)';
      for (let k = 0; k < 9; k++) {
        const x = w * (0.15 + r() * 0.7), y = h * (0.35 + r() * 0.35), rx = w * (0.1 + r() * 0.22), ry = h * (0.08 + r() * 0.12);
        ctx.fillStyle = P.cloudShade; ctx.beginPath(); ctx.ellipse(x, y - ry * 0.35, rx, ry, 0, 0, 7); ctx.fill();
        ctx.fillStyle = P.cloudLit; ctx.beginPath(); ctx.ellipse(x + rx * 0.05, y + ry * 0.15, rx * 0.95, ry * 0.85, 0, 0, 7); ctx.fill();
      }
    });
    const az = THREE.MathUtils.degToRad(-80 + r() * 160 + (r() < 0.35 ? 180 : 0)), el = THREE.MathUtils.degToRad(4 + r() * 16);
    const d = 1500, w = 300 + r() * 420;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, w * 0.31), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, fog: false, opacity: 0.92 }));
    m.position.set(Math.sin(az) * Math.cos(el) * d, Math.sin(el) * d, -Math.cos(az) * Math.cos(el) * d);
    m.lookAt(0, m.position.y * 0.6, 0); m.renderOrder = -9; g.add(m);
  }
  scene.add(g);
  scene.background = null;
  scene.fog = new THREE.Fog(P.fog, 120, 1100);

  // Licht: tiefe Sonne + kräftiges Umgebungslicht, damit Schattenseiten nicht absaufen
  const amb = new THREE.HemisphereLight(P.amb, '#7a6a60', P.ambI); scene.add(amb);
  const sun = new THREE.DirectionalLight(P.sunColor, P.sunI);
  sun.position.set(...P.sunDir).multiplyScalar(60); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  const s = sun.shadow.camera; s.left = -30; s.right = 30; s.top = 30; s.bottom = -30; s.near = 1; s.far = 160;
  sun.shadow.bias = -0.0008; sun.shadow.normalBias = 0.05;
  scene.add(sun); scene.add(sun.target);
  return { sun, amb, preset: P };
}
