// Handy: 3D-Gehäuse mit Bildschirm-Textur (Anruf, Alarm, Nachricht, aus).
import * as THREE from 'three';
import { toon, ink } from './toon.js';

const W = 300, H = 620;
export function phoneMesh() {
  const g = new THREE.Group();
  const body = ink(new THREE.BoxGeometry(0.074, 0.152, 0.009), toon('#161618'), 1.1); g.add(body);
  const c = document.createElement('canvas'); c.width = W * 2; c.height = H * 2;
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.067, 0.143), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }));
  screen.position.z = 0.0052; g.add(screen);
  g.userData.screen = { canvas: c, tex, key: null };
  drawPhone(g, { typ: 'aus' }, 0);
  return g;
}

function roundRect(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }

// spec: {typ:'anruf'|'eingehend'|'alarm'|'nachricht'|'aus', name, status, text, titel, uhr,
//        nach_und_nach: Sekunden zwischen eingehenden Nachrichten, tippen: "Text, der gerade getippt wird", tipp_ab: Sekunden}
// dt = Sekunden seit dieser Bildschirm erschienen ist
export function drawPhone(g, spec, t, dt = 99) {
  const S = g.userData.screen; if (!S) return;
  spec = spec || { typ: 'aus' };
  const msgs0 = Array.isArray(spec.text) ? spec.text : spec.text ? [spec.text] : [];
  const iv = spec.nach_und_nach || 0;
  const neu0 = spec.neu_ab ?? 0, shown = iv ? Math.min(msgs0.length, neu0 + 1 + Math.floor(Math.max(0, dt - 0.2) / iv)) : msgs0.length;
  const typing = iv && shown < msgs0.length && (dt - 0.2) % iv > iv - 0.9 && !msgs0[shown].startsWith('>');
  const nt = spec.tippen ? Math.max(0, Math.min(spec.tippen.length, Math.floor((dt - (spec.tipp_ab ?? 0.3)) * (spec.tipp_tempo || 14)))) : 0;
  const key = JSON.stringify(spec) + '|' + (spec.typ === 'anruf' || spec.typ === 'eingehend' ? Math.floor(t * 2) : 0) + '|' + shown + '|' + typing + '|' + nt + '|' + (spec.tippen ? Math.floor(t * 2.5) % 2 : 0) + '|' + (spec.typ === 'video' || spec.typ === 'live' ? Math.floor(dt * 8) : 0);
  if (key === S.key) return; S.key = key;
  const c = S.canvas.getContext('2d'); c.setTransform(2, 0, 0, 2, 0, 0);
  c.textAlign = 'center'; c.textBaseline = 'middle';
  const F = (w, s) => `${w} ${s}px Inter, "Liberation Sans", sans-serif`;
  if (spec.typ === 'aus') { c.fillStyle = '#0b0b0d'; c.fillRect(0, 0, W, H); }
  else if (spec.typ === 'anruf' || spec.typ === 'eingehend') {
    c.fillStyle = '#17241f'; c.fillRect(0, 0, W, H);
    c.fillStyle = '#9fb3aa'; c.font = F(600, 16); c.fillText(spec.uhr || '18:26', W / 2, 26);
    const ring = spec.typ === 'eingehend' ? 1 + Math.sin(t * 8) * 0.06 : 1;
    c.fillStyle = spec.farbe || '#3f7a5c'; c.beginPath(); c.arc(W / 2, 170, 52 * ring, 0, 7); c.fill();
    c.fillStyle = '#e9efe9'; c.font = F(800, 50); c.fillText((spec.name || '?')[0].toUpperCase(), W / 2, 172);
    c.font = F(800, 34); c.fillText(spec.name || '', W / 2, 270);
    c.fillStyle = '#9fb3aa'; c.font = F(500, 19);
    const dots = '.'.repeat(1 + (Math.floor(t * 2) % 3));
    c.fillText((spec.status || (spec.typ === 'eingehend' ? 'Eingehender Anruf' : 'Anruf wird aufgebaut')) + (spec.typ === 'anruf' && !spec.status ? dots : ''), W / 2, 308);
    for (let i = 0; i < 3; i++) { c.fillStyle = '#2c3a35'; c.beginPath(); c.arc(W / 2 + (i - 1) * 80, 430, 26, 0, 7); c.fill(); }
    c.fillStyle = '#d6372f'; c.beginPath(); c.arc(spec.typ === 'eingehend' ? W / 2 - 70 : W / 2, 530, 34, 0, 7); c.fill();
    c.fillStyle = '#fff'; c.fillRect((spec.typ === 'eingehend' ? W / 2 - 70 : W / 2) - 14, 526, 28, 8);
    if (spec.typ === 'eingehend') { c.fillStyle = '#2fb45a'; c.beginPath(); c.arc(W / 2 + 70, 530, 34, 0, 7); c.fill(); }
  } else if (spec.typ === 'video') { // Überwachungsvideo (Nachricht mit Video), spielt ab
    c.fillStyle = '#0d0f0e'; c.fillRect(0, 0, W, H);
    c.fillStyle = '#9fb0bb'; c.font = F(600, 13); c.textAlign = 'left'; c.fillText(spec.uhr || '18:44', 14, 13); c.textAlign = 'right'; c.fillText(spec.netz || '▂▄▆ 41%', W - 12, 13); c.textAlign = 'center';
    c.fillStyle = '#e8e8e8'; c.font = F(800, 17); c.fillText(spec.name || 'Unbekannt', W / 2, 44);
    const vx = 10, vy = 150, vw = W - 20, vh = 230, p = Math.min(1, dt / (spec.laenge || 8));
    c.fillStyle = '#26302a'; c.fillRect(vx, vy, vw, vh);
    c.fillStyle = '#3a463e'; c.fillRect(vx + 150, vy + 60, 120, 110); // Schaltschrank
    for (let i = 0; i < 12; i++) { c.fillStyle = (i * 7 + Math.floor(dt * 3)) % 5 === 0 ? '#c8ff8a' : '#55604f'; c.fillRect(vx + 160 + (i % 4) * 26, vy + 72 + Math.floor(i / 4) * 22, 12, 10); }
    c.fillStyle = '#6a7a6a'; c.fillRect(vx + 240, vy + 120 - 30 * Math.min(1, Math.max(0, (p - 0.55) * 4)), 8, 40); // Hebel
    const fx = vx + 60 + Math.min(1, p * 1.6) * 110; // Person geht zum Schrank
    c.fillStyle = '#121512'; c.beginPath(); c.arc(fx, vy + 85, 16, 0, 7); c.fill(); c.fillRect(fx - 20, vy + 102, 40, 80);
    c.strokeStyle = '#121512'; c.lineWidth = 9; c.beginPath(); c.moveTo(fx + 14, vy + 115); c.lineTo(fx + 14 + 40 * Math.min(1, Math.max(0, (p - 0.45) * 3)), vy + 105); c.stroke();
    c.strokeStyle = '#b8c8b8'; c.lineWidth = 2; c.beginPath(); c.arc(fx - 6, vy + 84, 5, 0, 7); c.arc(fx + 8, vy + 84, 5, 0, 7); c.stroke(); // Brille
    c.fillStyle = 'rgba(255,255,255,0.05)'; for (let y = vy; y < vy + vh; y += 4) c.fillRect(vx, y, vw, 1);
    c.fillStyle = '#e8f0e8'; c.font = F(700, 12); c.textAlign = 'left'; c.fillText(spec.titel || 'UMSPANNWERK NORD · CAM 03', vx + 8, vy + 16);
    const sec = 31 + Math.floor(dt); c.fillText((spec.datum || '14.11.2025 23:58:') + String(sec % 60).padStart(2, '0'), vx + 8, vy + vh - 10);
    if (Math.floor(dt * 2) % 2 === 0) { c.fillStyle = '#ff3a2a'; c.beginPath(); c.arc(vx + vw - 40, vy + 14, 5, 0, 7); c.fill(); c.fillStyle = '#ff3a2a'; c.fillText('REC', vx + vw - 32, vy + 18); }
    c.fillStyle = '#333'; c.fillRect(vx, vy + vh + 10, vw, 5); c.fillStyle = '#e8e8e8'; c.fillRect(vx, vy + vh + 10, vw * p, 5);
    c.textAlign = 'center'; c.fillStyle = '#e8e8e8'; c.font = F(700, 22); if (spec.text) wrap(c, spec.text, W / 2, vy + vh + 60, W - 40, 28);
  } else if (spec.typ === 'live') { // Livestream: Bild, LIVE-Badge, Zuschauer, Kommentare, Herzen
    const sz = spec.szene || 'gang';
    const g1 = c.createLinearGradient(0, 0, 0, H); g1.addColorStop(0, '#0a0c14'); g1.addColorStop(1, '#1a1e2a'); c.fillStyle = g1; c.fillRect(0, 0, W, H);
    // stilisiertes Kamerabild
    c.strokeStyle = 'rgba(140,160,200,0.35)'; c.lineWidth = 2;
    if (sz === 'gang') { for (const [x0, x1] of [[0, 120], [W, 180]]) { c.beginPath(); c.moveTo(x0, 80); c.lineTo(x1, 250); c.lineTo(x1, 330); c.lineTo(x0, H); c.stroke(); } c.strokeRect(120, 250, 60, 80); for (let i = 0; i < 6; i++) { c.beginPath(); c.moveTo(0 + i * 8, 120 + i * 40); c.lineTo(110, 270 + i * 9); c.stroke(); } }
    else { c.strokeRect(40, 140, 220, 120); c.fillStyle = 'rgba(60,120,90,0.25)'; c.fillRect(40, 140, 220, 120); c.fillStyle = 'rgba(230,230,230,0.6)'; c.font = F(700, 16); c.fillText('MIA, DU BIST DRAN', W / 2, 200); }
    if (spec.figur) { c.fillStyle = '#05060a'; c.beginPath(); c.arc(W / 2 + 40, 300, 22, 0, 7); c.fill(); c.fillRect(W / 2 + 14, 322, 52, 120); c.fillStyle = '#f0f0f0'; c.fillRect(W / 2 + 30, 296, 5, 4); c.fillRect(W / 2 + 46, 296, 5, 4);
      if (spec.figur === 2) { c.fillStyle = '#2a2018'; c.beginPath(); c.arc(W / 2 - 60, 360, 26, 0, 7); c.fill(); c.fillStyle = '#c84a7a'; c.fillRect(W / 2 - 92, 386, 64, 140); } }
    // Kopfzeile
    c.fillStyle = '#e8304a'; roundRect(c, 12, 22, 52, 24, 5); c.fill(); c.fillStyle = '#fff'; c.font = F(900, 14); c.fillText('LIVE', 38, 35);
    const zv = spec.zuschauer || [100, 100], zk = Math.min(1, dt / (spec.zuschauer_dauer || 6)), zn = Math.round(zv[0] + (zv[1] - zv[0]) * zk);
    c.fillStyle = 'rgba(0,0,0,0.5)'; roundRect(c, 70, 22, 86, 24, 5); c.fill(); c.fillStyle = '#fff'; c.font = F(800, 14); c.fillText('◉ ' + zn.toLocaleString('de-DE'), 113, 35);
    c.textAlign = 'right'; c.font = F(800, 15); c.fillText('@' + (spec.name || 'live'), W - 14, 35); c.textAlign = 'center';
    // Kommentare (von unten)
    const ks = spec.kommentare || [], tp = spec.tempo || 0.9, nk = Math.min(ks.length, (spec.schon || 0) + Math.floor(Math.max(0, dt - 0.2) / tp) + 1);
    const vis = ks.slice(Math.max(0, nk - 6), nk); c.textAlign = 'left';
    vis.forEach(([u, txt], i) => { const y = H - 70 - (vis.length - 1 - i) * 54; const alarm = /!|hinter|wer/i.test(txt);
      c.fillStyle = alarm ? 'rgba(200,30,50,0.55)' : 'rgba(0,0,0,0.45)'; c.font = F(800, 16); const w2 = Math.min(W - 24, Math.max(c.measureText(txt).width, c.measureText(u).width) + 20); roundRect(c, 12, y - 18, w2, 46, 10); c.fill();
      c.fillStyle = '#ffd34a'; c.font = F(800, 13); c.fillText(u, 22, y - 2); c.fillStyle = '#fff'; c.font = F(700, 16); c.fillText(txt.length > 30 ? txt.slice(0, 29) + '…' : txt, 22, y + 17); });
    c.textAlign = 'center';
    for (let i = 0; i < 6; i++) { const ph = (dt * 0.6 + i / 6) % 1; c.fillStyle = `rgba(255,70,110,${1 - ph})`; c.font = F(900, 22); c.fillText('♥', W - 34 + Math.sin(ph * 8 + i) * 10, H - 60 - ph * 260); }
    c.fillStyle = 'rgba(255,255,255,0.15)'; roundRect(c, 12, H - 34, W - 24, 24, 12); c.fill(); c.fillStyle = 'rgba(255,255,255,0.6)'; c.font = F(600, 12); c.fillText('Kommentieren …', 70, H - 22);
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
    c.fillStyle = '#26323a'; c.fillRect(0, 0, W, 78);
    c.fillStyle = '#9fb0bb'; c.font = F(600, 13); c.textAlign = 'left'; c.fillText(spec.uhr || '18:26', 14, 13); c.textAlign = 'right'; c.fillText(spec.netz || '▂▄▆ 41%', W - 12, 13); c.textAlign = 'center';
    c.fillStyle = spec.name === 'Unbekannt' ? '#7a2a2a' : '#4f7d9c'; c.beginPath(); c.arc(38, 48, 17, 0, 7); c.fill();
    c.fillStyle = '#fff'; c.font = F(800, 17); c.fillText(spec.name === 'Unbekannt' ? '?' : (spec.name || '?')[0], 38, 49);
    c.textAlign = 'left'; c.font = F(800, 23); c.fillText(spec.name || 'Chat', 66, 44);
    c.fillStyle = '#9fb0bb'; c.font = F(500, 13); c.fillText(typing ? 'schreibt …' : spec.name === 'Unbekannt' ? 'Unbekannte Nummer' : 'online', 66, 64);
    const keyb = !!spec.tippen, bottom = keyb ? H - 250 : H - 20;
    // Nachrichten von unten nach oben stapeln (wie echte Chats)
    const items = msgs0.slice(0, shown).map((m) => ({ mine: m.startsWith('>'), txt: m.startsWith('>') ? m.slice(1).trim() : m }));
    if (typing) items.push({ dots: true });
    c.font = F(700, 28);
    const lay = items.map((it) => { if (it.dots) return { ...it, lines: [], bw: 70, bh: 40 }; const lines = splitLines(c, it.txt, W - 80); return { ...it, lines, bh: lines.length * 33 + 22, bw: Math.min(W - 50, Math.max(...lines.map((l) => c.measureText(l).width)) + 30) }; });
    let y = bottom - lay.reduce((a, it) => a + it.bh + 12, 0);
    y = Math.max(92, y);
    for (const it of lay) {
      const x = it.mine ? W - 16 - it.bw : 16;
      c.fillStyle = it.mine ? '#c8ecc0' : spec.name === 'Unbekannt' ? '#ffffff' : '#ffffff';
      roundRect(c, x, y, it.bw, it.bh, 15); c.fill(); c.font = F(700, 28);
      if (it.dots) { c.fillStyle = '#8a8a8a'; for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(x + 20 + i * 15, y + 20 - (Math.floor(t * 6) % 3 === i ? 4 : 0), 5, 0, 7); c.fill(); } }
      else { c.fillStyle = '#1d1d1d'; it.lines.forEach((l, i) => c.fillText(l, x + 15, y + 27 + i * 33)); }
      y += it.bh + 12;
    }
    if (keyb) {
      c.fillStyle = '#fff'; c.fillRect(0, H - 250, W, 52); c.strokeStyle = '#ccc'; c.lineWidth = 2; roundRect(c, 10, H - 242, W - 64, 36, 18); c.stroke();
      const txt = spec.tippen.slice(0, nt) + (Math.floor(t * 2.5) % 2 ? '|' : ' ');
      c.fillStyle = '#1d1d1d'; c.font = F(600, 18); c.fillText(txt.length > 24 ? '…' + txt.slice(-23) : txt, 24, H - 224);
      c.fillStyle = '#2f8f5a'; c.beginPath(); c.arc(W - 28, H - 224, 17, 0, 7); c.fill(); c.fillStyle = '#fff'; c.font = F(900, 18); c.textAlign = 'center'; c.fillText('➤', W - 27, H - 223);
      c.fillStyle = '#d4d6db'; c.fillRect(0, H - 198, W, 198);
      const rows = ['qwertzuiop', 'asdfghjkl', 'yxcvbnm'], cur = spec.tippen[nt - 1]?.toLowerCase();
      c.font = F(600, 16);
      rows.forEach((row, ri) => { const kw = 27, x0 = (W - row.length * (kw + 2)) / 2; [...row].forEach((ch, i) => {
        const hot = ch === cur && Math.floor(t * 14) % 2 === 0; c.fillStyle = hot ? '#8a8f99' : '#fff'; roundRect(c, x0 + i * (kw + 2), H - 188 + ri * 46, kw, 40, 5); c.fill();
        c.fillStyle = '#222'; c.textAlign = 'center'; c.fillText(ch, x0 + i * (kw + 2) + kw / 2, H - 167 + ri * 46); }); });
      c.fillStyle = cur === ' ' ? '#8a8f99' : '#fff'; roundRect(c, 70, H - 50, W - 140, 38, 5); c.fill();
    }
    c.textAlign = 'center';
  }
  if (spec.tropfen) { // Regentropfen auf dem Display
    let sd = 7; const rnd = () => ((sd = (sd * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < (spec.tropfen === true ? 16 : spec.tropfen); i++) {
      const x = rnd() * W, y = 90 + rnd() * (H - 120), rr = 4 + rnd() * 9;
      c.fillStyle = 'rgba(160,190,230,0.22)'; c.beginPath(); c.ellipse(x, y, rr, rr * 1.15, 0, 0, 7); c.fill();
      c.strokeStyle = 'rgba(40,60,90,0.35)'; c.lineWidth = 1.5; c.beginPath(); c.ellipse(x, y + 1, rr, rr * 1.15, 0, 0.2, 2.9); c.stroke();
      c.fillStyle = 'rgba(255,255,255,0.75)'; c.beginPath(); c.arc(x - rr * 0.35, y - rr * 0.4, rr * 0.28, 0, 7); c.fill();
      if (rnd() < 0.3) { c.fillStyle = 'rgba(160,190,230,0.18)'; c.fillRect(x - 1.5, y + rr, 3, 8 + rnd() * 20); }
    }
  }
  S.tex.needsUpdate = true;
}
function splitLines(c, text, maxW) {
  const out = []; let cur = '';
  for (const w of text.split(' ')) { const n = cur ? cur + ' ' + w : w; if (c.measureText(n).width > maxW && cur) { out.push(cur); cur = w; } else cur = n; }
  if (cur) out.push(cur); return out;
}
function wrap(c, text, x, y, maxW, lh) { splitLines(c, text, maxW).forEach((l, i) => c.fillText(l, x, y + i * lh)); }
