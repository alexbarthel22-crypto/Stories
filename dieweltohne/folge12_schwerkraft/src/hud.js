// 2D-Einblendungen: Titel, Emblem, Countdowns, Messwerte, Gefahrenstufe, Untertitel
import {CAPTIONS, STAGES, STAGE_OF, VANISH, RETURN, JUMP, BONK, BOMB, BUMP, SAUCE_HIT, CRASH, CRACK, PUD, worldLeft} from './timeline.js';
import {clamp, smooth, rng, lerp} from './lib.js';
// Staubkörnchen: beim Verschwinden schweben sie nach oben weg, bei der Rückkehr prasseln sie nach unten
function dustBurst(g, d, up) { const r = rng(91); for (let i = 0; i < 300; i++) { const x0 = r() * W, y0 = r() * H, s = 2 + r() * 5;
  const v = 200 + r() * 900; const y = up ? y0 - v * d * d : y0 + v * 2.2 * d * d; const x = x0 + (r() - 0.5) * 60 * d; const a = Math.sin(d * Math.PI) * (0.35 + r() * 0.5);
  if (y < -20 || y > H + 20) continue; g.fillStyle = `rgba(235,240,255,${a})`; g.beginPath(); g.arc(x, y, s, 0, 7); g.fill();
  if (!up) { g.strokeStyle = `rgba(235,240,255,${a * 0.6})`; g.lineWidth = s * 0.7; g.beginPath(); g.moveTo(x, y); g.lineTo(x, y - 40 * d); g.stroke(); } } }

const ORANGE = '#b49cff';
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
  g.textAlign = 'center'; g.textBaseline = 'middle'; // Planet mit Pfeil nach unten (Schwerkraft)
  const pg = g.createRadialGradient(-14, -8, 4, 0, 6, 44); pg.addColorStop(0, '#cfe3ff'); pg.addColorStop(1, '#4b6fae'); g.fillStyle = pg; g.beginPath(); g.arc(0, 14, 34, 0, 7); g.fill();
  g.strokeStyle = 'rgba(255,255,255,0.8)'; g.lineWidth = 2; g.beginPath(); g.ellipse(0, 14, 56, 13, -0.2, 0, 7); g.stroke();
  const bob = 4 * Math.sin(T * 3); g.fillStyle = '#ff6b5a'; g.beginPath(); g.arc(0, -52 + bob, 10, 0, 7); g.fill(); g.fillStyle = '#5bbf5a'; g.fillRect(-1, -66 + bob, 3, 7);
  g.strokeStyle = '#fff'; g.lineWidth = 2.5; g.beginPath(); g.moveTo(0, -38 + bob); g.lineTo(0, -24); g.moveTo(-6, -30); g.lineTo(0, -23); g.lineTo(6, -30); g.stroke();
  g.fillStyle = '#fff'; g.font = '400 15px Plex'; g.globalAlpha = a * 0.75; spaced(g, 'SCHWERKRAFT · 10 s', 0, 72, 2);
  g.restore();
}

export function drawHUD(g, T, shot) {
  g.clearRect(0, 0, W, H);
  { const d = T - VANISH; if (d > -0.02 && d < 1.2) dustBurst(g, d / 1.2, true); }
  { const d = T - RETURN; if (d > -0.02 && d < 0.8) dustBurst(g, d / 0.8, false); }
  // Rotes Aufblitzen beim großen Beben
  { const d = T - CRASH; if (d > -0.03 && d < 0.6) { g.fillStyle = `rgba(255,150,90,${0.55 * (1 - clamp(d / 0.6))})`; g.fillRect(0, 0, W, H); } }
  const vg = g.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);

  // Titel
  const ta = clamp(T / 0.4) * (1 - smooth(4.3, 5.0, T));
  if (ta > 0) {
    g.save(); g.globalAlpha = ta; g.textBaseline = 'alphabetic'; g.fillStyle = '#fff';
    g.font = '400 68px Garamond';
    const l1a = 'Was wäre, wenn die ', l1b = 'Schwerkraft';
    const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
    g.textAlign = 'left'; shadowText(g, l1a, x0, 420); g.fillStyle = ORANGE; shadowText(g, l1b, x0 + w1, 420);
    g.fillStyle = '#fff'; g.textAlign = 'center'; shadowText(g, '10 Sekunden verschwindet?', W / 2, 500);
    g.restore();
  }
  emblem(g, T, clamp(T / 0.4) * (1 - smooth(4.6, 5.2, T)));

  // Countdown-Block links
  let label, value, sub = '', prog, accent = '#fff', alarm = 0;
  const wl = worldLeft(T);
  if (T < VANISH) { label = 'SCHWERKRAFT WEG IN'; value = fmt(VANISH - T); prog = 1 - (VANISH - T) / VANISH; if (VANISH - T < 3.5) alarm = 1; }
  else if (T < RETURN) { label = 'SCHWERKRAFT ZURÜCK IN'; value = fmt(wl); prog = 1 - wl / 10; accent = ORANGE; }
  else { label = 'SCHWERKRAFT'; value = 'ZURÜCK'; prog = 1; }
  const ws = 'SCHWERKRAFT ZURÜCK IN ' + fmt(wl), t = T - shot.t0;
  const m1 = v => dec(Math.max(0, v), 1) + ' m';
  if (shot.id === 'mensa') { label = 'SCHWEBENDE SPAGHETTI'; value = de(Math.floor(2400 * smooth(VANISH, 16.5, T))); sub = ws; alarm = T > SAUCE_HIT ? 1 : 0; }
  if (shot.id === 'gym') { label = 'HÖHE ÜBER DEM KORB'; value = m1(Math.min(3.6, Math.max(0, 2.17 * (T - JUMP) - 1.2))); sub = ws; alarm = T > BONK ? 1 : 0; }
  if (shot.id === 'pool') { label = 'ENTFERNUNG ZUM WASSER'; { const d = Math.max(0, T - BOMB), h = 10.1 + 0.5 * d, z = Math.max(0, -5.4 + 3 * d - 6); value = m1(Math.hypot(h, z)); } sub = ws; alarm = T > BOMB + 1 ? 1 : 0; }
  if (shot.id === 'bus') { label = 'BUS ÜBER DER STRASSE'; value = m1(T < BUMP ? 0 : (T - BUMP) * 1.25); sub = ws; alarm = T > BUMP ? 1 : 0; }
  if (shot.id === 'orbit') { label = 'ABWEICHUNG VON DER BAHN'; value = de(Math.min(300, 300 * (10 - wl) / 10)) + ' km'; sub = ws; alarm = 1; }
  if (shot.id === 'core') { label = 'DRUCK IM ERDKERN'; value = '3,5 Mio. bar'; sub = ws; alarm = 1; }
  if (shot.id.startsWith('drop')) { label = 'SCHWERKRAFT'; value = 'ZURÜCK'; alarm = 1; accent = '#e5482b'; }
  if (shot.id === 'quake' || shot.id === 'city') { label = 'BEBEN AUF DER GANZEN ERDE'; value = T < CRASH ? 'GLEICH' : 'JETZT'; alarm = 1; accent = '#e5482b'; }
  if (shot.id === 'final') { label = 'PUDDING'; value = T < PUD ? 'VERMISST' : 'GERETTET'; alarm = T < PUD ? 1 : 0; accent = '#4cc76a'; }
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
