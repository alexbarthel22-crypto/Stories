import * as THREE from 'three';
import {RectAreaLightUniformsLib} from 'three/addons/lights/RectAreaLightUniformsLib.js';
import {SHOTS, FPS} from './timeline.js';
import {drawHUD} from './hud.js';
import {makePost} from './post.js';

RectAreaLightUniformsLib.init();
const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('gl'), antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance'});
renderer.setSize(1080, 1920, false);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const post = makePost(renderer);
const hud = document.getElementById('hud').getContext('2d');

const files = {room: './room.js', living: './living.js', street: './street.js', control: './control.js', city: './city.js', earth: './earth.js', test: './test.js'};
export const SET_OF = {intro: 'room', play: 'room', vanish: 'room', papa: 'living', street: 'street', control: 'control', city: 'city', europe: 'earth', dark: 'room', back: 'city', blast: 'room', mom: 'room', test: 'test'};
const only = new URLSearchParams(location.search).get('only');
if (only) for (const k of Object.keys(files)) if (!only.split(',').includes(k)) delete files[k];
const sets = {};
for (const [k, file] of Object.entries(files)) {
  try { const m = await import(file); sets[k] = await m.build(renderer); } catch (e) { if (!/Failed to fetch|404|Cannot find/.test(e.message)) console.warn('set fehlt', k, e.message, e.stack); }
}
window.render = f => {
  const T = f / FPS;
  const shot = only === 'test' ? {id: 'test', t0: 0, t1: 90} : (SHOTS.find(s => T >= s.t0 && T < s.t1) || SHOTS[SHOTS.length - 1]);
  const set = sets[SET_OF[shot.id]];
  if (set) { const o = set.update(shot, T) || {}; renderer.toneMappingExposure = o.exposure ?? 1.0; post.render(set.scene, set.camera, T, o); }
  else { renderer.setRenderTarget(null); renderer.setClearColor('#111214'); renderer.clear(); }
  drawHUD(hud, T, shot);
};
await document.fonts.load('400 40px Garamond'); await document.fonts.load('500 40px Plex'); await document.fonts.ready;
window.READY = true;
