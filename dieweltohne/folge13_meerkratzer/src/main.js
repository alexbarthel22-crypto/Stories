import {SHOTS, FPS} from './timeline.js';
import {drawHUD} from './hud.js';
// Fotorealistische Fassung: ?bg=<ordner> legt die in Blender gerenderten Bilder unter die Einblendungen
const BG = new URLSearchParams(location.search).get('bg');
if (BG) {
  document.getElementById('gl').style.display = 'none';
  const bgc = document.getElementById('bgc').getContext('2d'); const hud = document.getElementById('hud').getContext('2d');
  const load = src => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error('fehlt ' + src)); im.src = src; });
  window.render = async f => {
    const T = f / FPS; const shot = SHOTS.find(s => T >= s.t0 && T < s.t1) || SHOTS[SHOTS.length - 1];
    const im = await load(`../${BG}/f${String(f).padStart(5, '0')}.png`);
    bgc.imageSmoothingEnabled = true; bgc.imageSmoothingQuality = 'high';
    bgc.globalCompositeOperation = 'source-over'; bgc.filter = 'none'; bgc.globalAlpha = 1; bgc.drawImage(im, 0, 0, 1080, 1920);
    // Bloom: nur die hellen Stellen weich überstrahlen lassen
    bgc.globalCompositeOperation = 'lighter'; bgc.globalAlpha = 0.42; bgc.filter = 'brightness(0.55) contrast(2.6) blur(22px)'; bgc.drawImage(im, 0, 0, 1080, 1920);
    bgc.globalAlpha = 0.3; bgc.filter = 'brightness(0.55) contrast(2.6) blur(6px)'; bgc.drawImage(im, 0, 0, 1080, 1920);
    bgc.globalCompositeOperation = 'source-over'; bgc.globalAlpha = 1; bgc.filter = 'none';
    drawHUD(hud, T, shot, {noCrack: true});
  };
  await document.fonts.load('400 40px Garamond'); await document.fonts.load('italic 400 40px Garamond'); await document.fonts.load('500 40px Plex');
  await document.fonts.ready;
  window.READY = true;
} else {
const THREE = await import('three');

const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true});
renderer.setSize(1080, 1920, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const hud = document.getElementById('hud').getContext('2d');

const files = {surface: './surface.js', sea: './sea.js'};
const SET_OF = {surface: 'surface'};
const only = new URLSearchParams(location.search).get('only');
if (only) for (const k of Object.keys(files)) if (!only.split(',').includes(k)) delete files[k];
const sets = {};
for (const [k, file] of Object.entries(files)) {
  try { const m = await import(file); sets[k] = await m.build(renderer); } catch (e) { console.warn('set fehlt', k, e.message, e.stack); }
}

window.render = f => {
  const T = f / FPS;
  const shot = SHOTS.find(s => T >= s.t0 && T < s.t1) || SHOTS[SHOTS.length - 1];
  const set = sets[SET_OF[shot.id] || 'sea'];
  renderer.toneMappingExposure = 1.0;
  if (set) { set.update(shot, T); renderer.render(set.scene, set.camera); }
  else { renderer.setClearColor('#111214'); renderer.clear(); }
  drawHUD(hud, T, shot);
};
await document.fonts.load('400 40px Garamond'); await document.fonts.load('italic 400 40px Garamond'); await document.fonts.load('500 40px Plex');
await document.fonts.ready;
window.READY = true;
}
