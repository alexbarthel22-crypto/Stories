import * as THREE from 'three';
import {SHOTS, FPS} from './timeline.js';
import {drawHUD} from './hud.js';

const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true});
renderer.setSize(1080, 1920, false);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const hud = document.getElementById('hud').getContext('2d');

const files = {room: './bedroom.js', winter: './winter.js', festival: './festival.js', parkour: './parkour.js', birds: './birds.js', crane: './crane.js'};
const SET_OF = {intro: 'room', wait: 'room', selfie: 'room', final: 'room', winter: 'winter', street_after: 'winter', festival: 'festival', fest_after: 'festival',
  parkour: 'parkour', birds: 'birds', crane: 'crane'};
// Nur die Sets laden, die gebraucht werden (zum schnellen Testen: ?only=cockpit)
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
