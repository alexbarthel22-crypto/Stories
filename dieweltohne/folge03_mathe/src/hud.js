// 2D-Einblendungen: Titel, Emblem, Countdowns, Messwerte, Gefahrenstufe, Untertitel
import {CAPTIONS, STAGES, STAGE_OF, VANISH, RETURN, ALARM, DECIDE_START, TRAIN_HIT, ORBIT_HIT, COUNTER, IGNITION, FLASH0, worldLeft} from './timeline.js';
import {clamp, smooth, rng} from './lib.js';
const GLC = '0123456789+−×÷=∞√∑∫πΔ≠≈%#?!'.split('');
// Ziffern verrutschen, solange die Mathe fehlt
function garble(txt, T, k = 0.35) { const r = rng(Math.floor(T * 14) * 13 + 5); return txt.split('').map(c => /[0-9]/.test(c) && r() < k ? GLC[Math.floor(r() * GLC.length)] : c).join(''); }
function glitchBars(g, T, amt) { const r = rng(Math.floor(T * 30) + 77); for (let i = 0; i < 14 * amt; i++) { const y = r() * H, h = 3 + r() * 60;
  g.fillStyle = ['rgba(0,255,140,0.35)', 'rgba(255,0,180,0.35)', 'rgba(60,140,255,0.4)', 'rgba(255,255,255,0.5)', 'rgba(0,0,0,0.6)'][Math.floor(r() * 5)]; g.fillRect((r() - 0.5) * 200, y, W + 200, h); } }

const ORANGE = '#ffb02e';
const W = 1080, H = 1920;

function fmt(v) { // 0:05.033 oder 8:20.000
  v = Math.max(0, v); const m = Math.floor(v / 60), s = Math.floor(v - m * 60), ms = Math.floor((v - Math.floor(v)) * 1000);
  return `${m}:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
}
const de = n => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
const dec = (n, k) => n.toFixed(k).replace('.', ',');

function shadowText(g, txt, x, y, blur = 18) {
  g.save(); g.shadowColor = 'rgba(0,0,0,0.75)'; g.shadowBlur = blur; g.shadowOffsetY = 2; g.fillText(txt, x, y); g.restore();
}
function spaced(g, txt, x, y, sp) {
  g.save(); g.letterSpacing = sp + 'px'; shadowText(g, txt, x, y, 10); g.restore();
}
function wrap(g, text, maxW) {
  const words = text.split(' '); const lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  lines.push(cur); return lines;
}

// Emblem: astronomisches Sonnenzeichen ☉ mit Skala
function emblem(g, T, a, cx = W / 2, cy = 215, r = 105) {
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; g.translate(cx, cy);
  g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 2.5; g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.stroke();
  g.lineWidth = 1.2; g.strokeStyle = 'rgba(255,255,255,0.5)'; g.beginPath(); g.arc(0, 0, r - 12, 0, Math.PI * 2); g.stroke();
  for (let i = 0; i < 60; i++) { const an = i / 60 * Math.PI * 2 + T * 0.15; const l = i % 5 ? 6 : 13; g.beginPath(); g.moveTo(Math.cos(an) * (r - 12), Math.sin(an) * (r - 12)); g.lineTo(Math.cos(an) * (r - 12 - l), Math.sin(an) * (r - 12 - l)); g.stroke(); }
  g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = 8;
  g.fillStyle = '#fff'; g.font = 'italic 400 76px Garamond'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('π', 0, -12);
  g.font = '400 15px Plex'; g.globalAlpha = a * 0.75; spaced(g, 'MATHE · 1 + 1 = 2', 0, 46, 3);
  g.restore();
}

export function drawHUD(g, T, shot) {
  g.clearRect(0, 0, W, H);
  // Blitz beim Verschwinden (im All) und bei der Rückkehr des Lichts
  for (const tf of [VANISH, RETURN]) { const d = T - tf; if (d > -0.05 && d < 0.6) glitchBars(g, T, 3 * (1 - d / 0.6)); }
  if (T > VANISH && T < RETURN) { const r = rng(Math.floor(T * 3)); if (r() < 0.22) glitchBars(g, T, 0.6); }
  { const d = T - ALARM; if (d > 0 && d < 0.5) { g.fillStyle = `rgba(255,30,20,${0.45 * (1 - d / 0.5)})`; g.fillRect(0, 0, W, H); } }
  const vg = g.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);

  // Titel
  const ta = clamp(T / 0.4) * (1 - smooth(4.3, 5.0, T));
  if (ta > 0) {
    g.save(); g.globalAlpha = ta; g.textBaseline = 'alphabetic'; g.fillStyle = '#fff';
    g.font = '400 68px Garamond';
    const l1a = 'Was wäre, wenn die ', l1b = 'Mathe';
    const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
    g.textAlign = 'left'; shadowText(g, l1a, x0, 420); g.fillStyle = ORANGE; shadowText(g, l1b, x0 + w1, 420);
    g.fillStyle = '#fff'; g.textAlign = 'center'; shadowText(g, '10 Sekunden verschwindet?', W / 2, 500);
    g.restore();
  }
  emblem(g, T, clamp(T / 0.4) * (1 - smooth(4.6, 5.2, T)));

  // Countdown-Block links
  let label, value, sub = '', prog, accent = '#fff', alarm = 0;
  const wl = worldLeft(T);
  if (T < VANISH) { label = 'MATHE VERSCHWINDET IN'; value = fmt(VANISH - T); prog = 1 - (VANISH - T) / VANISH; if (VANISH - T < 3.5) alarm = 1; }
  else if (T < RETURN) { label = 'MATHE ZURÜCK IN'; value = garble(fmt(wl), T); prog = 1 - wl / 10; accent = ORANGE; }
  else if (T < ALARM + 6) { label = 'MATHE'; value = 'ZURÜCK'; prog = 1; }
  if (T >= ALARM && T >= RETURN + 0.0 && (shot.id === 'bunker' || (shot.id === 'earth' && T < COUNTER))) {
    label = 'ENTSCHEIDUNG IN'; value = fmt(DECIDE_START - (T - ALARM)).slice(0, -4); prog = (T - ALARM) / DECIDE_START; accent = '#e5482b'; alarm = 1; sub = 'RAKETENSTART GEMELDET'; }
  else if (T >= ALARM && T < RETURN) sub = 'RAKETENSTART GEMELDET';
  const ws = 'MATHE ZURÜCK IN ' + garble(fmt(wl), T, 0.2);
  if (shot.id === 'bank') {
    const t = T - shot.t0, k = smooth(3.6, 6.4, t), a = smooth(3.4, 3.8, t);
    if (a > 0) { // DAX-Kurve: ruhiger Vormittag, dann senkrechter Absturz
      const X0 = 90, X1 = 990, Y0 = 640, Y1 = 330; g.save(); g.globalAlpha = a;
      g.fillStyle = 'rgba(0,0,0,0.45)'; g.beginPath(); g.roundRect(X0 - 40, Y1 - 80, X1 - X0 + 80, Y0 - Y1 + 140, 20); g.fill();
      g.textAlign = 'left'; g.fillStyle = '#fff'; g.font = '500 22px Plex'; spaced(g, 'DAX · HEUTE', X0, Y1 - 36, 3);
      const n = 200, pts = []; const r = rng(31); let v = 0.8;
      for (let i = 0; i < n; i++) { v += (r() - 0.5) * 0.03; const x = X0 + i / n * (X1 - X0) * 0.75; pts.push([x, Y1 + (1 - v) * (Y0 - Y1)]); }
      g.strokeStyle = '#4cc76a'; g.lineWidth = 4; g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke();
      const [lx, ly] = pts[n - 1]; g.strokeStyle = '#ff3b30'; g.lineWidth = 5; g.beginPath(); g.moveTo(lx, ly);
      for (let i = 0; i <= 30 * k; i++) { const u = i / 30; g.lineTo(lx + u * (X1 - lx) * 0.9, ly + Math.pow(u, 0.5) * (Y0 - ly - 10) + Math.sin(i * 2.3) * 12); } g.stroke();
      g.restore();
      label = 'DAX'; value = de(24183 - 14760 * k) + ' Pkt.'; sub = ws; alarm = k > 0.05 ? 1 : 0;
      if (k > 0) { g.save(); g.fillStyle = '#ff3b30'; g.font = '500 30px Plex'; g.textAlign = 'right'; spaced(g, '−' + dec(61 * k, 1) + ' %', 990, 300, 2); g.restore(); }
    }
  }
  if (shot.id === 'plane') {
    const t = T - shot.t0, alt = 1310 - 850 * Math.pow(smooth(1.2, 9, t), 1.4);
    label = 'FLUGHÖHE'; value = garble(de(alt) + ' ft', T, 0.25); sub = ws; alarm = t > 2 ? 1 : 0;
  }
  if (shot.id === 'train') { // Abstand der Züge (beide ca. 100 km/h)
    const d = Math.max(0, (TRAIN_HIT - T) * 56);
    label = 'ABSTAND DER ZÜGE'; value = T < TRAIN_HIT ? garble(de(d) + ' m', T, 0.15) : 'KOLLISION'; sub = ws; alarm = T > TRAIN_HIT - 2.5 ? 1 : 0; }
  if (shot.id === 'orbit') {
    const k = smooth(shot.t0 + 0.3, shot.t1 - 0.3, T);
    label = 'SATELLITEN AUSSER KONTROLLE'; value = de(10400 * k); sub = ws; alarm = T > ORBIT_HIT ? 1 : 0; }
  if (shot.id === 'earth' && T >= COUNTER) {
    label = 'RAKETEN IN DER LUFT'; value = de(5 + Math.floor(180 * smooth(COUNTER, shot.t1, T))); sub = 'GEGENSCHLAG'; prog = 1; accent = '#e5482b'; alarm = 1; }
  if (shot.id === 'launch') {
    label = 'EINSCHLAG IN'; value = fmt(30 * 60 - Math.max(0, T - IGNITION)).slice(0, -4); sub = 'GEGENSCHLAG'; prog = 1; accent = '#e5482b'; alarm = 1; }
  if (shot.id === 'final') {
    label = 'EINSCHLÄGE'; value = de(Math.max(0, Math.floor((T - FLASH0) / 0.15) + (T >= FLASH0 ? 1 : 0)) * 7); sub = ''; prog = 1; accent = '#e5482b'; alarm = 1; }
  const x = 64, y = 1000;
  g.save(); g.fillStyle = '#fff';
  g.strokeStyle = 'rgba(255,255,255,0.25)'; g.lineWidth = 4; g.beginPath(); g.arc(x + 30, y - 70, 28, 0, Math.PI * 2); g.stroke();
  g.strokeStyle = accent; g.beginPath(); g.arc(x + 30, y - 70, 28, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * clamp(prog)); g.stroke();
  g.font = '500 25px Plex'; g.textAlign = 'left'; g.textBaseline = 'alphabetic'; spaced(g, label, x, y, 3);
  const blink = alarm ? 0.55 + 0.45 * (Math.sin(T * 12) > -0.3 ? 1 : 0) : 1;
  g.fillStyle = alarm ? `rgba(255,${Math.round(120 + 135 * (1 - alarm * 0.6))},${Math.round(90 * (1 - alarm))},${blink})` : '#fff';
  g.font = value.length > 10 ? '400 80px Garamond' : '400 92px Garamond'; shadowText(g, value, x - 3, y + 88);
  g.fillStyle = '#fff';
  if (sub) { g.font = '400 21px Plex'; g.globalAlpha = 0.72; spaced(g, sub, x, y + 128, 3); g.globalAlpha = 1; }
  g.restore();
  // Gefahrenstufe
  const st = STAGE_OF[shot.id] || 0;
  if (st) {
    const yb = y + (sub ? 160 : 128), cols = ['#4cc76a', '#a5d34a', '#e8d13a', '#f3a531', '#f07a2a', '#e5482b', '#c4161c'];
    g.save();
    for (let i = 0; i < 7; i++) {
      const on = i < st, pulse = on && i === st - 1 ? 0.75 + 0.25 * Math.sin(T * 8) : 1;
      g.globalAlpha = on ? pulse : 0.22; g.fillStyle = on ? cols[i] : '#ffffff';
      g.beginPath(); g.roundRect(x + i * 46, yb, 40, 10, 3); g.fill();
    }
    g.globalAlpha = 1; g.fillStyle = cols[st - 1]; g.font = '500 23px Plex';
    spaced(g, `STUFE ${st}/7 · ${STAGES[st - 1]}`, x, yb + 44, 3);
    g.restore();
  }
  // "5 Stunden später" Einblendung
  if (shot.id === 'final') { const a = smooth(84, 84.3, T) * (1 - smooth(86.4, 86.9, T)); if (a > 0) { g.save(); g.globalAlpha = a; g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = '500 30px Plex'; spaced(g, '30 MINUTEN SPÄTER', W / 2, 330, 8); g.restore(); } }
  if (shot.id === 'earth') { const a = smooth(66, 66.3, T) * (1 - smooth(68.6, 69.1, T)); if (a > 0) { g.save(); g.globalAlpha = a; g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = '500 30px Plex'; spaced(g, '26. SEPTEMBER 1983', W / 2, 330, 8); g.restore(); } }

  // Untertitel
  for (const [a, b, txt] of CAPTIONS) {
    if (T < a - 0.1 || T > b + 0.1) continue;
    const al = smooth(a - 0.1, a + 0.25, T) * (1 - smooth(b - 0.25, b + 0.1, T));
    g.save(); g.globalAlpha = al; g.textAlign = 'center'; g.font = 'italic 400 54px Garamond';
    const lines = wrap(g, txt, 880);
    const bg = g.createRadialGradient(W / 2, 1380, 30, W / 2, 1380, 520); bg.addColorStop(0, 'rgba(0,0,0,0.6)'); bg.addColorStop(1, 'rgba(0,0,0,0)');
    g.save(); g.translate(W / 2, 1380); g.scale(1, 0.32); g.translate(-W / 2, -1380); g.fillStyle = bg; g.fillRect(0, 1380 - 520, W, 1040); g.restore(); g.fillStyle = '#fff';
    lines.forEach((l, i) => shadowText(g, l, W / 2, 1390 + i * 64 - (lines.length - 1) * 32 + (1 - al) * 10, 22));
    g.restore();
  }
}
