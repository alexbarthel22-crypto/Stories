import * as THREE from 'three';
import {SHOTS, FPS} from './timeline.js';
import {drawHUD} from './hud.js';
import {buildStreet} from './street.js';

const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true});
renderer.setSize(1080, 1920, false);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const hud = document.getElementById('hud').getContext('2d');

const sets = {street: buildStreet(renderer)};
const optional = {kitchen: './kitchen.js', plane: './plane.js', globe: './globe.js', gummy: './gummy.js', rocket: './rocket.js'};
for (const [k, file] of Object.entries(optional)) {
  try { const m = await import(file); sets[k] = await m.build(renderer); } catch (e) { console.warn('set fehlt', k, e.message); }
}
const SET_OF = {intro: 'street', cars_wide: 'street', cars_wheel: 'street', cars_crash: 'street', soles: 'street', pants: 'street', balloons: 'street',
  last: 'street', gas: 'street', rocket: 'rocket', back: 'street', later: 'street', kitchen: 'kitchen', plane: 'plane', globe: 'globe', gummy: 'gummy', phone: 'phone'};
if (sets.street && !sets.phone) { const m = await import('./phoneshot.js').catch(() => null); if (m) sets.phone = await m.build(renderer); }

window.render = f => {
  const T = f / FPS;
  const shot = SHOTS.find(s => T >= s.t0 && T < s.t1) || SHOTS[SHOTS.length - 1];
  const set = sets[SET_OF[shot.id]];
  if (set) { set.update(shot, T); renderer.render(set.scene, set.camera); }
  else { renderer.setClearColor('#111214'); renderer.clear(); }
  drawHUD(hud, T, shot);
};
await document.fonts.load('400 40px Garamond'); await document.fonts.load('italic 400 40px Garamond'); await document.fonts.load('500 40px Plex');
await document.fonts.ready;
window.READY = true;
