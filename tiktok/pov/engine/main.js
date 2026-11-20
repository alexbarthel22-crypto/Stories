// Hauptprogramm: baut Szene aus der Timeline (build/<story>/timeline.json) und rendert Frame für Frame.
// Im Browser: window.render(frame) zeichnet genau diesen Frame (deterministisch, beliebige Reihenfolge).
import * as THREE from 'three';
import { FisheyeCamera } from './fisheye.js';
import { buildSky } from './sky.js';
import { Character } from './chars.js';
import { PovBody, EYE } from './pov.js';
import { drawPhone } from './phone.js';
import { Overlay } from './overlay.js';
import * as SETS from './sets/index.js';

const D2R = Math.PI / 180;
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const wrapA = (a) => { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; };

const q = new URLSearchParams(location.search);
const scale = +(q.get('scale') || 1);
const TL = await (await fetch(`../build/${q.get('story')}/timeline.json?${Date.now()}`)).json();
const ST = TL.story;
// Deutsche Feldnamen aus der Story -> interne Namen
const spec = (c = {}) => ({ ...c, face: c.schaut, skin: c.haut, top: c.oberteil, pants: c.hose, hair: c.haare, hairStyle: c.frisur, eyes: c.augen, glasses: c.brille, shoes: c.schuhe, detail: c.details, look_h: c.blickhoehe });
ST.cast = Object.fromEntries(Object.entries(ST.cast || {}).map(([k, v]) => [k, spec(v)]));
ST.sky = ST.himmel; ST.look = ST.blick; ST.label_klein = ST.ort_klein;
TL.beats.forEach((b) => Object.assign(b, { look: b.blick, turn: b.drehung, cut: b.schnitt, pose: b.pose, mood: b.stimmung, face: b.schaut, walk: b.laufen, walk_dur: b.laufzeit, phone: b.handy, label: b.ort, notify: b.meldung, fade: b.blende, text_color: b.text_farbe, look_delay: b.blick_verzoegerung, pose_delay: b.pose_verzoegerung }));
const FPS = TL.fps;

// ---------- Renderer ----------
const W = Math.round(1080 * scale), H = Math.round(1920 * scale);
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
canvas.style.width = '1080px'; canvas.style.height = '1920px';
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap; renderer.shadowMap.autoUpdate = false;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const cam = new FisheyeCamera(renderer, { size: Math.round((ST.cube || 1152) * scale), fov: ST.fov || 140 });

const scene = new THREE.Scene();
const sky = buildSky(scene, ST.sky || 'abend', ST.seed || 7);
const set = SETS[ST.set || 'aussicht'];
const setRoot = set.build(scene, ST.seed || 3, { story: { ...ST, start: ST.cast?.ich?.pos }, beats: TL.beats });
const spots = { ...set.info.spots, ...(ST.spots || {}) };

// ---------- Darsteller ----------
const cast = {};
const me = ST.cast?.ich || {};
const pov = new PovBody(me); scene.add(pov.root);
for (const [name, spec] of Object.entries(ST.cast || {})) {
  if (name === 'ich') continue;
  const c = new Character(name, spec); scene.add(c.root); cast[name] = c;
}
const overlay = new Overlay(document.getElementById('ui'), ST);

// ---------- Tracks aus den Beats ----------
const beats = TL.beats, lines = TL.lines;
const actors = ['ich', ...Object.keys(cast)];
const startPos = (n) => { const p = n === 'ich' ? me.pos || set.info.start : ST.cast[n].pos || [0, -1.5]; return [p[0], p[1]]; };
const tracks = { look: [], pose: {}, mood: {}, face: {}, walk: {}, phone: [], label: [], notify: [], fade: [], cap: [], shake: [], black: [], blackout: null, fov: [{ t: -1, v: ST.fov || 140, dur: 0 }] };
actors.forEach((a) => { tracks.pose[a] = [{ t: -1, v: a === 'ich' ? me.pose || 'runter' : ST.cast[a].pose || 'idle' }]; tracks.mood[a] = [{ t: -1, v: ST.cast[a]?.mood || null }]; tracks.face[a] = [{ t: -1, v: a === 'ich' ? null : ST.cast[a].face || 'ich' }]; tracks.walk[a] = []; });
const pos0 = Object.fromEntries(actors.map((a) => [a, startPos(a)]));
const cur = Object.fromEntries(actors.map((a) => [a, startPos(a)]));
tracks.look.push({ t: -1, v: ST.look || 'stadt', dur: 0, cut: true });
for (const b of beats) {
  if (b.look !== undefined) tracks.look.push({ t: b.t0 + (b.look_delay || 0), v: b.look, dur: b.turn ?? 0.75, cut: !!b.cut });
  for (const [a, v] of Object.entries(b.pose || {})) tracks.pose[a]?.push({ t: b.t0 + (b.pose_delay || 0), v });
  for (const [a, v] of Object.entries(b.mood || {})) tracks.mood[a]?.push({ t: b.t0, v });
  for (const [a, v] of Object.entries(b.face || {})) tracks.face[a]?.push({ t: b.t0, v });
  for (const [a, w0] of Object.entries(b.walk || {})) {
    if (!tracks.walk[a]) continue;
    // laufen: {"name": [x,z]} oder {"name": {"nach": [x,z], "zeit": s, "ab": s}}
    const to = Array.isArray(w0) ? w0 : w0.nach, t0w = b.t0 + (Array.isArray(w0) ? 0 : w0.ab || 0);
    const from = cur[a].slice(); const d = Math.hypot(to[0] - from[0], to[1] - from[1]);
    const dur = (Array.isArray(w0) ? null : w0.zeit) || b.walk_dur || Math.max(0.5, d / 1.3);
    tracks.walk[a].push({ t0: t0w, t1: t0w + dur, from, to }); cur[a] = to.slice();
  }
  if (b.phone !== undefined) tracks.phone.push({ t: b.t0, v: b.phone });
  if (b.label !== undefined) tracks.label.push({ t: b.t0, v: b.label });
  if (b.notify) tracks.notify.push({ t0: b.t0, t1: b.t0 + (b.notify.dauer || 3), v: b.notify });
  for (const k of Object.keys(b)) if (b[k] === undefined) delete b[k];
  if (b.fade) tracks.fade.push({ t: b.t0, dur: b.fade === true ? 0.6 : b.fade });
  if (b.schuetteln) tracks.shake.push({ t: b.t0 + (b.schuetteln_ab || 0), amp: b.schuetteln });
  const isLast = b === beats[beats.length - 1];
  if (b.schwarz) tracks.black.push({ t0: b.t0, t1: isLast ? 1e9 : b.t1 });
  if (b.ende) tracks.ende = { t0: b.t0 + (b.ende_ab ?? 0.4), text: b.ende === true ? 'FORTSETZUNG FOLGT' : b.ende, unter: b.ende_unter };
  if (b.zoom !== undefined) tracks.fov.push({ t: b.t0 + (b.zoom_ab || 0), v: b.zoom || ST.fov || 140, dur: b.zoom_dauer ?? 1.0 });
  if (b.effekt?.stromausfall) tracks.blackout = { t: b.t0 + (b.effekt.ab || 0), dur: b.effekt.stromausfall };
  if (b.text) tracks.cap.push({ t0: b.t0, t1: isLast ? 1e9 : b.t1, text: b.text, color: b.text_color || '#ffffff' });
}
const at = (tr, t) => { let v = tr[0]?.v, ti = -1, pv = v; for (const e of tr) { if (e.t <= t) { pv = v; v = e.v; ti = e.t; } else break; } return { v, t: ti, prev: pv }; };

function posAt(a, t) {
  let p = pos0[a], speed = 0, dir = null;
  for (const w of tracks.walk[a]) {
    if (t >= w.t1) p = w.to;
    else if (t >= w.t0) {
      const k = (t - w.t0) / (w.t1 - w.t0), e = ease(k);
      p = [w.from[0] + (w.to[0] - w.from[0]) * e, w.from[1] + (w.to[1] - w.from[1]) * e];
      speed = Math.hypot(w.to[0] - w.from[0], w.to[1] - w.from[1]) / (w.t1 - w.t0) * 6 * k * (1 - k) * (k > 0.05 && k < 0.95 ? 1 : 0.4);
      dir = Math.atan2(w.to[0] - w.from[0], w.to[1] - w.from[1]);
    }
  }
  return { p, speed, dir };
}
function talkAt(a, t) {
  for (const l of lines) if (l.who === a && t >= l.t0 && t < l.t1) { const i = Math.floor((t - l.t0) * FPS); return l.env[Math.min(i, l.env.length - 1)] || 0; }
  return 0;
}
// Ziel einer Blickrichtung -> [yaw, pitch] in Rad
function lookTarget(v, t, eye) {
  if (Array.isArray(v)) return [v[0] * D2R, v[1] * D2R];
  if (cast[v]) {
    const P = posAt(v, t).p, dx = P[0] - eye.x, dz = P[1] - eye.z, dy = (ST.cast[v].look_h ?? 1.28) - eye.y;
    return [Math.atan2(-dx, -dz), Math.atan2(dy, Math.hypot(dx, dz)) - 4 * D2R];
  }
  const s = spots[v] || [0, -8]; return [s[0] * D2R, s[1] * D2R];
}
function lookAt(t, eye) {
  // vorwärts durchgehen, Startwerte jeder Drehung merken
  let yaw = 0, pitch = 0;
  const L = tracks.look;
  for (let i = 0; i < L.length; i++) {
    const e = L[i]; if (e.t > t) break;
    const [ty, tp] = lookTarget(e.v, t, eye);
    if (e.cut || e.dur <= 0) { yaw = ty; pitch = tp; }
    else {
      // Startwert = Blick am Beginn dieser Drehung
      const [sy, sp] = i > 0 ? lookAtUntil(i, e.t) : [ty, tp];
      const k = ease((t - e.t) / e.dur);
      yaw = sy + wrapA(ty - sy) * k; pitch = sp + (tp - sp) * k;
    }
  }
  return [yaw, pitch];
}
const memo = new Map();
function lookAtUntil(i, t) {
  const key = i; if (memo.has(key)) return memo.get(key);
  const ep = posAt('ich', t).p, eye = new THREE.Vector3(ep[0], EYE, ep[1]);
  // Blick unmittelbar vor Eintrag i
  const L = tracks.look; let yaw = 0, pitch = 0;
  for (let j = 0; j < i; j++) {
    const e = L[j]; const [ty, tp] = lookTarget(e.v, t, eye);
    if (e.cut || e.dur <= 0 || j === 0) { yaw = ty; pitch = tp; }
    else { const [sy, sp] = lookAtUntil(j, e.t); const k = ease((t - e.t) / e.dur); yaw = sy + wrapA(ty - sy) * k; pitch = sp + (tp - sp) * k; }
  }
  const r = [yaw, pitch]; memo.set(key, r); return r;
}

// ---------- Ein Frame ----------
const eye = new THREE.Vector3();
const flatCam = new THREE.PerspectiveCamera(+(q.get('flat') || 70), W / H, 0.03, 3000);
window.TOTAL_FRAMES = Math.ceil(TL.total * FPS);
window.render = (f) => {
  const t = f / FPS;
  // Ich
  const mp = posAt('ich', t);
  eye.set(mp.p[0], EYE, mp.p[1]);
  let [yaw, pitch] = lookAt(t, eye);
  // Handkamera-Wackeln + Laufen
  const wob = ST.wackeln ?? 1;
  yaw += (Math.sin(t * 0.63) * 0.7 + Math.sin(t * 1.71) * 0.25) * D2R * wob;
  pitch += (Math.sin(t * 0.91 + 1) * 0.5 + Math.sin(t * 2.3) * 0.15) * D2R * wob;
  let roll = Math.sin(t * 0.53) * 0.6 * D2R * wob + (mp.speed ? Math.sin(t * 7.5) * 0.8 * D2R : 0);
  for (const sh of tracks.shake) { const k = t - sh.t; if (k >= 0 && k < 3) { const a = sh.amp * Math.exp(-k * 1.6) * D2R * 3; yaw += Math.sin(k * 37) * a; pitch += Math.sin(k * 29 + 1) * a; roll += Math.sin(k * 23 + 2) * a * 0.6; } }
  if (mp.speed) { const run = mp.speed > 2.5; eye.y += Math.abs(Math.sin(t * (run ? 10 : 7.5))) * (run ? 0.07 : 0.035); roll += run ? Math.sin(t * 10) * 1.6 * D2R : 0; pitch += run ? Math.sin(t * 20) * 0.6 * D2R : 0; }
  cam.yaw = yaw; cam.pitch = pitch; cam.roll = roll;
  { let f = tracks.fov[0].v; for (const e of tracks.fov) { if (e.t > t) break; const k = e.dur > 0 ? ease((t - e.t) / e.dur) : 1; f = f + (e.v - f) * k; } cam.fov = f; }
  const pp = at(tracks.pose.ich, t);
  { // Blick aufs Handy: Bild zoomt etwas heran, damit der Bildschirm lesbar ist
    const hk = (v) => v === 'handy' || v === 'handy_beide', e = ease((t - pp.t) / 0.6);
    const pk = hk(pp.v) ? (hk(pp.prev) ? 1 : e) : hk(pp.prev) ? 1 - e : 0;
    cam.fov += (Math.min(cam.fov, ST.handy_fov ?? 96) - cam.fov) * pk; }
  pov.root.position.set(mp.p[0], 0, mp.p[1]); pov.root.rotation.y = yaw; pov.root.updateMatrixWorld(true);
  pov.update({ t, pose: pp.v, prevPose: pp.prev, poseK: (t - pp.t) / 0.45, walk: mp.speed });
  const phE = at(tracks.phone, t), ph = phE.v;
  if (pov.phone.visible) drawPhone(pov.phone, ph, t, t - phE.t);
  // Andere Figuren
  for (const [n, c] of Object.entries(cast)) {
    const P = posAt(n, t);
    c.root.position.set(P.p[0], 0, P.p[1]);
    const fv = at(tracks.face[n], t).v;
    let facing;
    if (P.dir !== null && P.speed > 0.05 && !c.spec.faehrt) facing = P.dir;
    else if (fv === 'ich' || !fv) facing = Math.atan2(eye.x - P.p[0], eye.z - P.p[1]);
    else if (cast[fv]) { const Q = posAt(fv, t).p; facing = Math.atan2(Q[0] - P.p[0], Q[1] - P.p[1]); }
    else { const s = Array.isArray(fv) ? fv : spots[fv] || [0, 0]; facing = s[0] * D2R + Math.PI; }
    const cp = at(tracks.pose[n], t);
    c.update({ t, talk: talkAt(n, t), pose: cp.v, prevPose: cp.prev, poseK: (t - cp.t) / 0.4, facing, walk: c.spec.faehrt ? 0 : P.speed, mood: at(tracks.mood[n], t).v, blinkOff: n.length * 0.37, funk: lines.some((l) => l.funk && t >= l.t0 && t < l.t1) });
    if (c.phone.visible) drawPhone(c.phone, c.spec.handy_bild || { typ: 'nachricht', name: 'Jens', text: ['18:30.', 'Schau hin, Jens.'] }, t);
  }
  // Sonne folgt dem Spieler (Schattenbereich)
  sky.sun.target.position.set(eye.x, 0, eye.z); sky.sun.position.copy(sky.sun.target.position).add(new THREE.Vector3(...sky.preset.sunDir).multiplyScalar(60));
  sky.sun.target.updateMatrixWorld();
  scene.getObjectByName('sky').position.set(eye.x, 0, eye.z);
  const bo = tracks.blackout;
  { const nk = bo ? Math.min(1, Math.max(0, (t - bo.t) / (bo.dur * 1.4))) * (ST.nacht ?? 0.55) : 0;
    if (!sky.base) sky.base = { sun: sky.sun.intensity, amb: sky.amb.intensity, u: Object.fromEntries(['cTop', 'cMid', 'cLow', 'cHor', 'cGlow'].map((k) => [k, scene.getObjectByName('sky').children[0].material.uniforms[k].value.clone()])) };
    sky.sun.intensity = sky.base.sun * (1 - nk * 0.85); sky.amb.intensity = sky.base.amb * (1 - nk * 0.6);
    const U = scene.getObjectByName('sky').children[0].material.uniforms, NIGHT = new THREE.Color('#0b0f22');
    for (const k of Object.keys(sky.base.u)) U[k].value.copy(sky.base.u[k]).lerp(NIGHT, nk * 0.75);
    scene.getObjectByName('sky').children.forEach((o, i) => { if (i && o.material) o.material.opacity = 0.92 * (1 - nk * 0.55); }); }
  setRoot?.userData?.update?.({ blackout: bo ? t - bo.t : -1, dur: bo ? bo.dur : 3, t, eye, sky, yaw, px: q.get('flat') ? (H / 2) / Math.tan(+(q.get('flat')) * D2R / 2) : cam.rt.width / 2 });
  if (q.get('flat')) {
    flatCam.position.copy(eye); flatCam.rotation.set(pitch, yaw, roll, 'YXZ'); flatCam.updateMatrixWorld();
    renderer.shadowMap.needsUpdate = true; renderer.setRenderTarget(null); renderer.render(scene, flatCam);
  } else cam.render(scene, eye, t);
  // Einblendungen
  const fd = tracks.fade.find((e) => t >= e.t - e.dur && t < e.t + e.dur);
  let fade = fd ? 1 - Math.abs(t - fd.t) / fd.dur : 0;
  if (tracks.black.some((e) => t >= e.t0 && t < e.t1)) fade = 1;
  overlay.update(t, { ende: tracks.ende && t >= tracks.ende.t0 ? { ...tracks.ende, k: t - tracks.ende.t0 } : null, lines, label: at(tracks.label, t).v, notify: tracks.notify.find((n) => t >= n.t0 && t < n.t1), fade, caps: tracks.cap, cast: ST.cast });
};
window.SCENE = scene; window.THREE = THREE; window.FLATCAM = flatCam; window.CAM = cam;
window.READY = true;
