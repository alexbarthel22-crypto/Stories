import * as THREE from 'three';
import {SHOTS, FPS} from './timeline.js';
import {drawHUD} from './hud.js';

const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true});
renderer.setSize(1080, 1920, false);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const hud = document.getElementById('hud').getContext('2d');

const files = {skate: './skate.js', imbiss: './imbiss.js', vault: './vault.js', surgery: './surgery.js', street: './street.js'};
const SET_OF = {intro: 'skate', wait: 'skate', skate: 'skate', final: 'skate', cash: 'imbiss', kitchen: 'imbiss', vault: 'vault', surgery: 'surgery',
  street_return: 'street', street_fire: 'street', aerial: 'street'};
// Nur die Sets laden, die gebraucht werden (zum schnellen Testen: ?only=vault)
const only = new URLSearchParams(location.search).get('only');
if (only) for (const k of Object.keys(files)) if (!only.split(',').includes(k)) delete files[k];
const sets = {};
for (const [k, file] of Object.entries(files)) {
  try { const m = await import(file); sets[k] = await m.build(renderer); } catch (e) { console.warn('set fehlt', k, e.message); }
}

window.render = f => {
  const T = f / FPS;
  const shot = SHOTS.find(s => T >= s.t0 && T < s.t1) || SHOTS[SHOTS.length - 1];
  const set = sets[SET_OF[shot.id]];
  renderer.toneMappingExposure = 1.0;
  if (set) { set.update(shot, T); renderer.render(set.scene, set.camera); }
  else { renderer.setClearColor('#111214'); renderer.clear(); }
  drawHUD(hud, T, shot);
};
await document.fonts.load('400 40px Garamond'); await document.fonts.load('italic 400 40px Garamond'); await document.fonts.load('500 40px Plex');
await document.fonts.ready;
window.READY = true;
