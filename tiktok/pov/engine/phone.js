// Handy: 3D-Gehäuse mit Bildschirm-Textur (Anruf, Alarm, Nachricht, aus).
import * as THREE from 'three';
import { toon, ink } from './toon.js';

const W = 300, H = 620;
export function phoneMesh() {
  const g = new THREE.Group();
  const body = ink(new THREE.BoxGeometry(0.074, 0.152, 0.009), toon('#161618'), 1.1); g.add(body);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.067, 0.143), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }));
  screen.position.z = 0.0052; g.add(screen);
  g.userData.screen = { canvas: c, tex, key: null };
  drawPhone(g, { typ: 'aus' }, 0);
  return g;
}

function roundRect(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }

// spec: {typ:'anruf'|'eingehend'|'alarm'|'nachricht'|'aus', name, status, text, titel}
export function drawPhone(g, spec, t) {
  const S = g.userData.screen; if (!S) return;
  spec = spec || { typ: 'aus' };
  const key = JSON.stringify(spec) + '|' + (spec.typ === 'anruf' || spec.typ === 'eingehend' ? Math.floor(t * 2) : 0);
  if (key === S.key) return; S.key = key;
  const c = S.canvas.getContext('2d');
  c.textAlign = 'center'; c.textBaseline = 'middle';
  const F = (w, s) => `${w} ${s}px Inter, "Liberation Sans", sans-serif`;
  if (spec.typ === 'aus') { c.fillStyle = '#0b0b0d'; c.fillRect(0, 0, W, H); }
  else if (spec.typ === 'anruf' || spec.typ === 'eingehend') {
    c.fillStyle = '#17241f'; c.fillRect(0, 0, W, H);
    c.fillStyle = '#9fb3aa'; c.font = F(600, 16); c.fillText('17:41', W / 2, 26);
    const ring = spec.typ === 'eingehend' ? 1 + Math.sin(t * 8) * 0.06 : 1;
    c.fillStyle = spec.farbe || '#3f7a5c'; c.beginPath(); c.arc(W / 2, 170, 52 * ring, 0, 7); c.fill();
    c.fillStyle = '#e9efe9'; c.font = F(800, 50); c.fillText((spec.name || '?')[0].toUpperCase(), W / 2, 172);
    c.font = F(800, 34); c.fillText(spec.name || '', W / 2, 270);
    c.fillStyle = '#9fb3aa'; c.font = F(500, 19);
    const dots = '.'.repeat(1 + (Math.floor(t * 2) % 3));
    c.fillText((spec.status || (spec.typ === 'eingehend' ? 'Eingehender Anruf' : 'Anruf wird aufgebaut')) + (spec.typ === 'anruf' ? dots : ''), W / 2, 308);
    for (let i = 0; i < 3; i++) { c.fillStyle = '#2c3a35'; c.beginPath(); c.arc(W / 2 + (i - 1) * 80, 430, 26, 0, 7); c.fill(); }
    c.fillStyle = '#d6372f'; c.beginPath(); c.arc(spec.typ === 'eingehend' ? W / 2 - 70 : W / 2, 530, 34, 0, 7); c.fill();
    c.fillStyle = '#fff'; c.fillRect((spec.typ === 'eingehend' ? W / 2 - 70 : W / 2) - 14, 526, 28, 8);
    if (spec.typ === 'eingehend') { c.fillStyle = '#2fb45a'; c.beginPath(); c.arc(W / 2 + 70, 530, 34, 0, 7); c.fill(); }
  } else if (spec.typ === 'alarm') {
    c.fillStyle = '#2a0c0c'; c.fillRect(0, 0, W, H);
    c.fillStyle = '#e1251b'; roundRect(c, 14, 90, W - 28, H - 170, 22); c.fill();
    c.fillStyle = '#ffe9a0'; c.font = F(900, 70); c.fillText('⚠', W / 2, 160);
    c.fillStyle = '#fff'; c.font = F(900, 30);
    const lines = (spec.titel || 'NOTFALL-ALARM').split('\n'); lines.forEach((l, i) => c.fillText(l, W / 2, 240 + i * 36));
    c.font = F(600, 19); wrap(c, spec.text || 'Sofort Schutz suchen.', W / 2, 330, W - 60, 25);
    c.fillStyle = '#fff'; c.font = F(800, 22); c.fillText('OK', W / 2, H - 40);
  } else if (spec.typ === 'nachricht') {
    c.fillStyle = '#f2efe8'; c.fillRect(0, 0, W, H);
    c.fillStyle = '#26323a'; c.fillRect(0, 0, W, 70); c.fillStyle = '#fff'; c.font = F(800, 24); c.fillText(spec.name || 'Chat', W / 2, 40);
    const msgs = Array.isArray(spec.text) ? spec.text : [spec.text || ''];
    let y = 100; c.textAlign = 'left';
    for (const m of msgs) {
      const mine = m.startsWith('>'); const txt = mine ? m.slice(1).trim() : m;
      c.font = F(600, 19); const lines = splitLines(c, txt, W - 110);
      const bh = lines.length * 24 + 20, bw = Math.min(W - 60, Math.max(...lines.map((l) => c.measureText(l).width)) + 28);
      const x = mine ? W - 20 - bw : 20;
      c.fillStyle = mine ? '#c8ecc0' : '#ffffff'; roundRect(c, x, y, bw, bh, 14); c.fill();
      c.fillStyle = '#1d1d1d'; lines.forEach((l, i) => c.fillText(l, x + 14, y + 22 + i * 24)); y += bh + 12;
    }
    c.textAlign = 'center';
  }
  S.tex.needsUpdate = true;
}
function splitLines(c, text, maxW) {
  const out = []; let cur = '';
  for (const w of text.split(' ')) { const n = cur ? cur + ' ' + w : w; if (c.measureText(n).width > maxW && cur) { out.push(cur); cur = w; } else cur = n; }
  if (cur) out.push(cur); return out;
}
function wrap(c, text, x, y, maxW, lh) { splitLines(c, text, maxW).forEach((l, i) => c.fillText(l, x, y + i * lh)); }
