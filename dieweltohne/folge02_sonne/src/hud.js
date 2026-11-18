// 2D-Einblendungen: Titel, Emblem, Countdowns, Messwerte, Gefahrenstufe, Untertitel
import {CAPTIONS, STAGES, STAGE_OF, VANISH, DARK, RETURN, lightLeft, worldLeft} from './timeline.js';
import {clamp, smooth} from './lib.js';

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
  g.strokeStyle = '#fff'; g.lineWidth = 4; g.beginPath(); g.arc(0, -8, 30, 0, Math.PI * 2); g.stroke();
  g.fillStyle = '#fff'; g.beginPath(); g.arc(0, -8, 6, 0, Math.PI * 2); g.fill();
  g.font = '400 15px Plex'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.globalAlpha = a * 0.75; spaced(g, 'SONNE · 5.772 K', 0, 46, 3);
  g.restore();
}

export function drawHUD(g, T, shot) {
  g.clearRect(0, 0, W, H);
  // Blitz beim Verschwinden (im All) und bei der Rückkehr des Lichts
  for (const [tf, c] of [[VANISH, '255,250,235'], [RETURN, '255,246,220']]) { const d = T - tf; if (d > -0.05 && d < 0.8) { g.fillStyle = `rgba(${c},${clamp(1 - d / 0.8) * 0.8})`; g.fillRect(0, 0, W, H); } }
  const vg = g.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);

  // Titel
  const ta = clamp(T / 0.4) * (1 - smooth(4.3, 5.0, T));
  if (ta > 0) {
    g.save(); g.globalAlpha = ta; g.textBaseline = 'alphabetic'; g.fillStyle = '#fff';
    g.font = '400 68px Garamond';
    const l1a = 'Was wäre, wenn die ', l1b = 'Sonne';
    const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
    g.textAlign = 'left'; shadowText(g, l1a, x0, 420); g.fillStyle = ORANGE; shadowText(g, l1b, x0 + w1, 420);
    g.fillStyle = '#fff'; g.textAlign = 'center'; shadowText(g, '10 Sekunden verschwindet?', W / 2, 500);
    g.restore();
  }
  emblem(g, T, clamp(T / 0.4) * (1 - smooth(4.6, 5.2, T)));

  // Countdown-Block links
  let label, value, sub = '', prog, accent = '#fff', alarm = 0;
  const wl = worldLeft(T);
  if (T < VANISH) { label = 'SONNE VERSCHWINDET IN'; value = fmt(VANISH - T); prog = 1 - (VANISH - T) / VANISH; }
  else if (T < DARK) { label = 'DUNKELHEIT ERREICHT DIE ERDE IN'; const v = lightLeft(T); value = fmt(v); prog = 1 - v / 500; accent = ORANGE; if (v < 3.5) alarm = 1; }
  else if (T < RETURN) { label = 'SONNE ZURÜCK IN'; value = fmt(wl); prog = 1 - wl / 10; accent = ORANGE; }
  else if (shot.id === 'back') { label = 'SONNE'; value = 'ZURÜCK'; prog = 1; }
  else { label = 'OHNE STROM SEIT'; const h = 5 * 3600 + 47 * 60 + 12 + (T - 66) * (shot.id === 'aerial' ? 1 : 1);
    value = `${Math.floor(h / 3600)}:${String(Math.floor(h / 60) % 60).padStart(2, '0')}:${String(Math.floor(h) % 60).padStart(2, '0')} h`; prog = 1; accent = '#e5482b'; }
  if (shot.id === 'solar') { // Tageskurve des Solarstroms: Anstieg bis Mittag, dann senkrecht auf null
    const p = clamp((T - shot.t0 - 0.2) / 3.1), a = smooth(shot.t0, shot.t0 + 0.4, T);
    const X0 = 90, X1 = 990, Y0 = 640, Y1 = 330, xs = h => X0 + (h - 5) / 10 * (X1 - X0), ys = v => Y0 - v / 50 * (Y0 - Y1);
    g.save(); g.globalAlpha = a; g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 2;
    g.beginPath(); g.moveTo(X0, Y0); g.lineTo(X1, Y0); g.stroke();
    g.fillStyle = 'rgba(255,255,255,0.75)'; g.font = '400 21px Plex'; g.textAlign = 'center';
    for (const hh of [6, 8, 10, 12, 14]) { g.fillText(`${hh}:00`, xs(hh), Y0 + 34); g.beginPath(); g.moveTo(xs(hh), Y0); g.lineTo(xs(hh), Y0 + 8); g.stroke(); }
    g.textAlign = 'left'; g.font = '500 22px Plex'; spaced(g, 'SOLARSTROM HEUTE · GIGAWATT', X0, Y1 - 30, 3);
    const curve = h => h < 12 ? 43.7 * Math.pow(Math.sin(clamp((h - 5.5) / 13) * Math.PI), 1.6) / Math.pow(Math.sin((6.5 / 13) * Math.PI), 1.6) : 0;
    const hEnd = 5.5 + p * 8.5; const grd = g.createLinearGradient(0, Y1, 0, Y0); grd.addColorStop(0, 'rgba(255,176,46,0.45)'); grd.addColorStop(1, 'rgba(255,176,46,0.02)');
    g.beginPath(); g.moveTo(xs(5.5), Y0);
    for (let h = 5.5; h <= Math.min(hEnd, 12); h += 0.05) g.lineTo(xs(h), ys(curve(h)));
    if (hEnd >= 12) { g.lineTo(xs(12), ys(43.7)); g.lineTo(xs(12), Y0); g.lineTo(xs(Math.min(hEnd, 14.5)), Y0); }
    g.lineTo(xs(Math.min(hEnd, 12)), Y0); g.closePath(); g.fillStyle = grd; g.fill();
    g.strokeStyle = ORANGE; g.lineWidth = 5; g.beginPath(); g.moveTo(xs(5.5), ys(0));
    for (let h = 5.5; h <= Math.min(hEnd, 12); h += 0.05) g.lineTo(xs(h), ys(curve(h)));
    if (hEnd >= 12) { g.strokeStyle = ORANGE; g.stroke(); g.strokeStyle = '#ff3b30'; g.beginPath(); g.moveTo(xs(12), ys(43.7)); g.lineTo(xs(12), Y0); g.lineTo(xs(Math.min(hEnd, 14.5)), Y0); }
    g.stroke();
    if (hEnd >= 12) { g.fillStyle = '#ff3b30'; g.font = '500 24px Plex'; g.textAlign = 'center'; spaced(g, '12:00', xs(12), Y1 - 2, 2); }
    g.restore();
    const k = smooth(shot.t0 + 2.5, shot.t0 + 2.75, T);
    label = 'SOLARSTROM DEUTSCHLAND'; value = dec(43.7 * (1 - k) + (k < 1 ? Math.sin(T * 40) * 0.05 : 0), 1) + ' GW'; sub = 'SONNE ZURÜCK IN ' + fmt(wl); alarm = k > 0.5 ? 1 : 0;
  }
  if (shot.id === 'grid') {
    const t = T - shot.t0, f = 50 - 2.5 * smooth(0.3, 4.2, t) - 0.04 * Math.sin(t * 13);
    label = 'NETZFREQUENZ'; value = t > 4.4 ? 'ABSCHALTUNG' : dec(Math.max(47.5, f), 2) + ' Hz'; sub = 'SONNE ZURÜCK IN ' + fmt(wl); alarm = t > 1.2 ? 1 : 0;
  }
  if (shot.id === 'europe') {
    const k = smooth(shot.t0 + 0.4, shot.t1 - 0.6, T);
    label = 'MENSCHEN OHNE STROM'; value = de(4e8 * k); sub = 'SONNE ZURÜCK IN ' + fmt(wl); alarm = 1;
  }
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
  if (shot.id === 'night') { const a = smooth(66, 66.3, T) * (1 - smooth(68.2, 68.7, T)); if (a > 0) { g.save(); g.globalAlpha = a; g.fillStyle = '#fff'; g.textAlign = 'center'; g.font = '500 30px Plex'; spaced(g, 'FÜNF STUNDEN SPÄTER', W / 2, 330, 8); g.restore(); } }

  // Untertitel
  for (const [a, b, txt] of CAPTIONS) {
    if (T < a - 0.1 || T > b + 0.1) continue;
    const al = smooth(a - 0.1, a + 0.25, T) * (1 - smooth(b - 0.25, b + 0.1, T));
    g.save(); g.globalAlpha = al; g.textAlign = 'center'; g.font = 'italic 400 54px Garamond';
    const lines = wrap(g, txt, 880);
    const bg = g.createRadialGradient(W / 2, 1380, 30, W / 2, 1380, 520); bg.addColorStop(0, 'rgba(0,0,0,0.38)'); bg.addColorStop(1, 'rgba(0,0,0,0)');
    g.save(); g.translate(W / 2, 1380); g.scale(1, 0.32); g.translate(-W / 2, -1380); g.fillStyle = bg; g.fillRect(0, 1380 - 520, W, 1040); g.restore(); g.fillStyle = '#fff';
    lines.forEach((l, i) => shadowText(g, l, W / 2, 1390 + i * 64 - (lines.length - 1) * 32 + (1 - al) * 10, 22));
    g.restore();
  }
}
