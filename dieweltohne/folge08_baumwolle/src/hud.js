// 2D-Einblendungen: Titel, Emblem, Countdowns, Messwerte, Gefahrenstufe, Untertitel
import {CAPTIONS, STAGES, STAGE_OF, VANISH, RETURN, NOTE_GONE, FLARE, VAULT_ALARM, MONITOR_ALARM, IGNITE, worldLeft} from './timeline.js';
import {clamp, smooth, rng} from './lib.js';
// Baumwollflocken: beim Verschwinden lösen sie sich auf und wehen weg, bei der Rückkehr schneien sie herein
function fluffBurst(g, d, out) { const r = rng(91); for (let i = 0; i < 420; i++) { const x0 = r() * W, y0 = r() * H, vx = (r() - 0.3) * 900, vy = (out ? -1 : 1) * (200 + r() * 700), s = 3 + r() * 9;
  const k = out ? d : 1 - d; const x = x0 + vx * k, y = y0 + vy * k; const a = out ? 1 - d : d; if (y < -20 || y > H + 20) continue;
  g.fillStyle = `rgba(255,253,248,${a * 0.85})`; g.beginPath(); g.arc(x, y, s, 0, 7); g.arc(x + s * 0.8, y - s * 0.3, s * 0.7, 0, 7); g.arc(x - s * 0.7, y + s * 0.2, s * 0.6, 0, 7); g.fill(); } }

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
  g.fillStyle = '#fff'; g.textAlign = 'center'; g.textBaseline = 'middle'; // Baumwollkapsel
  for (const [x, y, rr] of [[0, -22, 17], [-17, -8, 16], [17, -8, 16], [-9, -30, 13], [9, -30, 13], [0, -6, 15]]) { g.beginPath(); g.arc(x, y, rr, 0, Math.PI * 2); g.fill(); }
  g.fillStyle = '#7a5a3a'; g.beginPath(); g.moveTo(-20, 8); g.lineTo(0, 22); g.lineTo(20, 8); g.lineTo(0, 12); g.closePath(); g.fill(); g.fillRect(-2, 20, 4, 12);
  g.fillStyle = '#fff'; g.font = '400 15px Plex'; g.globalAlpha = a * 0.75; spaced(g, 'BAUMWOLLE · CELLULOSE', 0, 52, 2);
  g.restore();
}

export function drawHUD(g, T, shot) {
  g.clearRect(0, 0, W, H);
  // Blitz beim Verschwinden (im All) und bei der Rückkehr des Lichts
  { const d = T - VANISH; if (d > -0.02 && d < 0.9) fluffBurst(g, d / 0.9, true); }
  { const d = T - (RETURN - 0.6); if (d > 0 && d < 0.8) fluffBurst(g, d / 0.8, false); }
  const vg = g.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);

  // Titel
  const ta = clamp(T / 0.4) * (1 - smooth(4.3, 5.0, T));
  if (ta > 0) {
    g.save(); g.globalAlpha = ta; g.textBaseline = 'alphabetic'; g.fillStyle = '#fff';
    g.font = '400 68px Garamond';
    const l1a = 'Was wäre, wenn ', l1b = 'Baumwolle';
    const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
    g.textAlign = 'left'; shadowText(g, l1a, x0, 420); g.fillStyle = ORANGE; shadowText(g, l1b, x0 + w1, 420);
    g.fillStyle = '#fff'; g.textAlign = 'center'; shadowText(g, '10 Sekunden verschwindet?', W / 2, 500);
    g.restore();
  }
  emblem(g, T, clamp(T / 0.4) * (1 - smooth(4.6, 5.2, T)));

  // Countdown-Block links
  let label, value, sub = '', prog, accent = '#fff', alarm = 0;
  const wl = worldLeft(T);
  if (T < VANISH) { label = 'BAUMWOLLE VERSCHWINDET IN'; value = fmt(VANISH - T); prog = 1 - (VANISH - T) / VANISH; if (VANISH - T < 3.5) alarm = 1; }
  else if (T < RETURN) { label = 'BAUMWOLLE ZURÜCK IN'; value = fmt(wl); prog = 1 - wl / 10; accent = ORANGE; }
  else { label = 'BAUMWOLLE'; value = 'ZURÜCK'; prog = 1; }
  const ws = 'BAUMWOLLE ZURÜCK IN ' + fmt(wl), t = T - shot.t0;
  if (shot.id === 'cash') { label = 'BARGELD IN DER KASSE'; value = T < NOTE_GONE ? '845 €' : '0 €'; sub = ws; alarm = T > NOTE_GONE ? 1 : 0; }
  if (shot.id === 'kitchen') { label = 'FETTTEMPERATUR'; value = '180 °C'; sub = ws; alarm = T > FLARE ? 1 : 0; }
  if (shot.id === 'vault') { label = 'EURO-SCHEINE VERSCHWUNDEN'; const k = smooth(31.2, 37.5, T); value = k < 1 ? de(30e9 * k) : '30 MRD.'; sub = ws; alarm = T > VAULT_ALARM ? 1 : 0; }
  if (shot.id === 'surgery') { label = 'PULS'; const k = smooth(MONITOR_ALARM, 46.5, T); value = Math.round(78 + 64 * k) + ' / min'; sub = ws; alarm = T > MONITOR_ALARM ? 1 : 0; }
  if (shot.id === 'street_fire') { label = 'BRENNENDE STRASSEN'; value = T < IGNITE ? '0' : de(1 + 40 * Math.pow(smooth(IGNITE, 68, T), 1.6)); alarm = T > IGNITE ? 1 : 0; accent = '#e5482b'; }
  if (shot.id === 'aerial' || shot.id === 'final') { label = 'BRENNENDE STÄDTE WELTWEIT'; value = de(shot.id === 'final' ? 10000 : 3 + 9997 * Math.pow(smooth(68.5, 79.5, T), 2)); prog = 1; accent = '#e5482b'; alarm = 1; }
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
  // Abblende zum Schluss
  const fo = smooth(88.9, 89.9, T);
  if (fo > 0) { g.save(); g.globalAlpha = fo; g.fillStyle = '#000'; g.fillRect(0, 0, W, 99999); g.restore(); }
}
