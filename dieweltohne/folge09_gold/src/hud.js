// 2D-Einblendungen: Titel, Emblem, Countdowns, Messwerte, Gefahrenstufe, Untertitel
import {CAPTIONS, STAGES, STAGE_OF, VANISH, RETURN, MEDAL_GONE, VISOR_GONE, GLARE, CHIP_DEAD, BLACKOUT, SHIP_HIT, CUBE_LAND, worldLeft} from './timeline.js';
import {clamp, smooth, rng, lerp} from './lib.js';
// Goldflitter: beim Verschwinden stieben Funken auseinander, bei der Rückkehr ziehen sie sich zur Bildmitte zusammen
function goldBurst(g, d, out) { const r = rng(91); for (let i = 0; i < 380; i++) { const x0 = r() * W, y0 = r() * H, s = 2 + r() * 6;
  let x, y, a;
  if (out) { x = x0 + (r() - 0.5) * 700 * d; y = y0 - (150 + r() * 600) * d; a = (1 - d) * (0.5 + r() * 0.5); }
  else { const k = 1 - Math.pow(1 - d, 2); x = lerp(x0, W / 2 + (r() - 0.5) * 120, k); y = lerp(y0, H * 0.45 + (r() - 0.5) * 120, k); a = Math.sin(d * Math.PI) * (0.5 + r() * 0.5); }
  if (y < -20 || y > H + 20) continue;
  g.fillStyle = `rgba(255,${200 + Math.floor(r() * 50)},${80 + Math.floor(r() * 90)},${a})`; g.beginPath(); g.arc(x, y, s, 0, 7); g.fill();
  if (i % 5 === 0) { g.fillRect(x - s * 3, y - 0.8, s * 6, 1.6); g.fillRect(x - 0.8, y - s * 3, 1.6, s * 6); } } }

const ORANGE = '#ffc451';
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
  g.textAlign = 'center'; g.textBaseline = 'middle'; // Goldbarren
  const bar = (y, w) => { g.beginPath(); g.moveTo(-w / 2, y + 14); g.lineTo(w / 2, y + 14); g.lineTo(w / 2 - 9, y - 10); g.lineTo(-w / 2 + 9, y - 10); g.closePath();
    const gr = g.createLinearGradient(0, y - 10, 0, y + 14); gr.addColorStop(0, '#ffe39a'); gr.addColorStop(1, '#d99a1e'); g.fillStyle = gr; g.fill(); };
  bar(-4, 62); bar(-28, 40); bar(-4, 62);
  g.fillStyle = '#fff'; g.font = '400 15px Plex'; g.globalAlpha = a * 0.75; spaced(g, 'GOLD · Au · 79', 0, 52, 2);
  g.restore();
}

export function drawHUD(g, T, shot) {
  g.clearRect(0, 0, W, H);
  // Blitz beim Verschwinden (im All) und bei der Rückkehr des Lichts
  { const d = T - VANISH; if (d > -0.02 && d < 0.9) goldBurst(g, d / 0.9, true); }
  { const d = T - (RETURN - 0.6); if (d > 0 && d < 0.9) goldBurst(g, d / 0.9, false); }
  const vg = g.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);

  // Blendung im All: das ungefilterte Sonnenlicht
  if (shot.id === 'space' && T > GLARE) { const k = smooth(GLARE, GLARE + 0.8, T) * (0.75 + 0.25 * Math.sin(T * 9)) * (1 - 0.8 * smooth(28.2, 28.6, T));
    const gr = g.createRadialGradient(W * 0.5, H * 0.36, 20, W * 0.5, H * 0.36, H * 0.75); gr.addColorStop(0, `rgba(255,255,255,${k})`); gr.addColorStop(0.35, `rgba(255,250,235,${k * 0.85})`); gr.addColorStop(1, `rgba(255,240,210,${k * 0.25})`);
    g.fillStyle = gr; g.fillRect(0, 0, W, H); }
  // Titel
  const ta = clamp(T / 0.4) * (1 - smooth(4.3, 5.0, T));
  if (ta > 0) {
    g.save(); g.globalAlpha = ta; g.textBaseline = 'alphabetic'; g.fillStyle = '#fff';
    g.font = '400 68px Garamond';
    const l1a = 'Was wäre, wenn ', l1b = 'Gold';
    const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
    g.textAlign = 'left'; shadowText(g, l1a, x0, 420); g.fillStyle = ORANGE; shadowText(g, l1b, x0 + w1, 420);
    g.fillStyle = '#fff'; g.textAlign = 'center'; shadowText(g, '10 Sekunden verschwindet?', W / 2, 500);
    g.restore();
  }
  emblem(g, T, clamp(T / 0.4) * (1 - smooth(4.6, 5.2, T)));

  // Countdown-Block links
  let label, value, sub = '', prog, accent = '#fff', alarm = 0;
  const wl = worldLeft(T);
  if (T < VANISH) { label = 'GOLD VERSCHWINDET IN'; value = fmt(VANISH - T); prog = 1 - (VANISH - T) / VANISH; if (VANISH - T < 3.5) alarm = 1; }
  else if (T < RETURN) { label = 'GOLD ZURÜCK IN'; value = fmt(wl); prog = 1 - wl / 10; accent = ORANGE; }
  else { label = 'GOLD'; value = 'ZURÜCK'; prog = 1; }
  const ws = 'GOLD ZURÜCK IN ' + fmt(wl), t = T - shot.t0;
  if (shot.id === 'rap') { label = 'GOLD AM KÖRPER'; value = T < VANISH ? '1.240 g' : '0 g'; sub = ws; alarm = 0; }
  if (shot.id === 'podium') { label = 'GOLD IN DER MEDAILLE'; value = T < MEDAL_GONE ? '6 g' : '0 g'; sub = ws; alarm = T > MEDAL_GONE ? 1 : 0; }
  if (shot.id === 'space') { label = 'GOLDFILTER IM VISIER'; value = T < VISOR_GONE ? 'AKTIV' : 'WEG'; sub = ws; alarm = T > VISOR_GONE ? 1 : 0; }
  if (shot.id === 'coaster') { label = 'HÖHE ÜBER DEM BODEN'; value = Math.round(Math.min(60, 18 + 42 * smooth(31, 33.2, T))) + ' m'; sub = ws; alarm = T > CHIP_DEAD ? 1 : 0; }
  if (shot.id === 'ship') { label = 'ABSTAND ZUR BRÜCKE'; value = T < SHIP_HIT ? Math.max(0, Math.round(150 - 25 * (T - 39))) + ' m' : '0 m'; sub = ws; alarm = T > BLACKOUT ? 1 : 0; }
  if (shot.id === 'cube_drop') { label = 'GOLD IM WÜRFEL'; value = T < CUBE_LAND - 0.3 ? '?' : '220.000 t'; accent = ORANGE; alarm = T > CUBE_LAND ? 1 : 0; }
  if (shot.id === 'cube_night' || shot.id === 'aerial' || shot.id === 'final') { label = 'FUNKTIONIERENDE CHIPS'; value = '0'; prog = 1; accent = '#e5482b'; alarm = 1; }
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
