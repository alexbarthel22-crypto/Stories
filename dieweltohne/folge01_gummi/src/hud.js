// 2D-Einblendungen: Titel, Emblem, Countdown, Untertitel, Schlusskarte
import {CAPTIONS, TAGS, VANISH, RETURN, worldLeft} from './timeline.js';
import {clamp, smooth} from './lib.js';

const ORANGE = '#ff8a3d';
const W = 1080, H = 1920;

function fmt(v) { // 0:05.033
  v = Math.max(0, v); const s = Math.floor(v), ms = Math.floor((v - s) * 1000);
  return `0:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
}
const de = n => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');

function shadowText(g, txt, x, y, blur = 18) {
  g.save(); g.shadowColor = 'rgba(0,0,0,0.75)'; g.shadowBlur = blur; g.shadowOffsetY = 2; g.fillText(txt, x, y); g.restore();
}
function spaced(g, txt, x, y, sp) { // Text mit Zeichenabstand
  g.save(); g.letterSpacing = sp + 'px'; shadowText(g, txt, x, y, 10); g.restore();
}
function wrap(g, text, maxW) {
  const words = text.split(' '); const lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  lines.push(cur); return lines;
}

function emblem(g, T, a, cx = W / 2, cy = 215, r = 105) {
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; g.translate(cx, cy);
  g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 2.5; g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.stroke();
  g.lineWidth = 1.2; g.strokeStyle = 'rgba(255,255,255,0.5)'; g.beginPath(); g.arc(0, 0, r - 12, 0, Math.PI * 2); g.stroke();
  for (let i = 0; i < 60; i++) { const an = i / 60 * Math.PI * 2 + T * 0.15; const l = i % 5 ? 6 : 13; g.beginPath(); g.moveTo(Math.cos(an) * (r - 12), Math.sin(an) * (r - 12)); g.lineTo(Math.cos(an) * (r - 12 - l), Math.sin(an) * (r - 12 - l)); g.stroke(); }
  g.fillStyle = '#fff'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = '500 46px Garamond'; shadowText(g, '(C₅H₈)ₙ', 0, -4, 8);
  g.font = '400 15px Plex'; g.globalAlpha = a * 0.75; spaced(g, 'POLYISOPREN', 0, 38, 3);
  g.restore();
}

export function drawHUD(g, T, shot) {
  g.clearRect(0, 0, W, H);
  if (shot.id === 'end') return drawEnd(g, T - shot.t0);
  // Blitz beim Verschwinden und bei der Rückkehr
  for (const tf of [VANISH, RETURN]) { const d = T - tf; if (d > -0.05 && d < 0.6) { g.fillStyle = `rgba(255,248,235,${clamp(1 - d / 0.6) * 0.7})`; g.fillRect(0, 0, W, H); } }
  // Vignette
  const vg = g.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);

  // Titel im Intro
  const ta = clamp(T / 0.4) * (1 - smooth(4.3, 5.0, T));
  if (ta > 0) {
    g.save(); g.globalAlpha = ta; g.textAlign = 'center'; g.textBaseline = 'alphabetic'; g.fillStyle = '#fff';
    g.font = '400 68px Garamond';
    const l1a = 'Was wäre, wenn es ', l1b = 'Gummi';
    const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
    g.textAlign = 'left'; shadowText(g, l1a, x0, 420); g.fillStyle = ORANGE; shadowText(g, l1b, x0 + w1, 420);
    g.fillStyle = '#fff'; g.textAlign = 'center'; shadowText(g, '10 Sekunden lang nicht gäbe?', W / 2, 500);
    g.restore();
  }
  emblem(g, T, clamp(T / 0.4) * (1 - smooth(4.6, 5.2, T)) + smooth(67.5, 68.5, T) * (1 - smooth(71, 72, T)));

  // Countdown-Block links
  let label, value, sub = TAGS[shot.id] || '', prog;
  if (T < VANISH) { label = 'GUMMI VERSCHWINDET IN'; value = fmt(VANISH - T); prog = 1 - (VANISH - T) / VANISH; }
  else if (T < RETURN) { label = 'GUMMI ZURÜCK IN'; const v = worldLeft(T); value = fmt(v); prog = 1 - v / 10; }
  else if (shot.id === 'back') { label = 'GUMMI'; value = 'ZURÜCK'; prog = 1; sub = 'SCHÄDEN: BLEIBEN'; }
  else { label = '5 MINUTEN SPÄTER'; value = '+5:00'; prog = 1; sub = 'STAU WELTWEIT'; }
  if (shot.id === 'globe') { // Zähler statt Countdown
    const k = smooth(shot.t0 + 0.4, shot.t1 - 1.5, T);
    label = 'FAHRZEUGE OHNE REIFEN'; value = de(1.5e9 * (k * k * (3 - 2 * k))); sub = 'GUMMI ZURÜCK IN ' + fmt(worldLeft(T));
  }
  const x = 64, y = 1000;
  g.save(); g.fillStyle = '#fff';
  // Fortschrittsring
  g.strokeStyle = 'rgba(255,255,255,0.25)'; g.lineWidth = 4; g.beginPath(); g.arc(x + 30, y - 70, 28, 0, Math.PI * 2); g.stroke();
  g.strokeStyle = T >= VANISH && T < RETURN ? ORANGE : '#fff'; g.beginPath(); g.arc(x + 30, y - 70, 28, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * clamp(prog)); g.stroke();
  g.font = '500 25px Plex'; g.textAlign = 'left'; g.textBaseline = 'alphabetic'; spaced(g, label, x, y, 3);
  g.font = '400 92px Garamond'; shadowText(g, value, x - 3, y + 88);
  if (sub) { g.font = '400 21px Plex'; g.globalAlpha = 0.72; spaced(g, sub, x, y + 128, 3); }
  g.restore();

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

function drawEnd(g, t) {
  g.fillStyle = '#111214'; g.fillRect(0, 0, W, H);
  const a = smooth(0, 0.6, t);
  g.save(); g.globalAlpha = a; g.textAlign = 'center'; g.fillStyle = '#f2efe8';
  g.font = '400 66px Garamond';
  const l1a = 'Was wäre, wenn es ', l1b = 'Gummi';
  const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
  g.textAlign = 'left'; g.fillText(l1a, x0, 880); g.fillStyle = ORANGE; g.fillText(l1b, x0 + w1, 880);
  g.fillStyle = '#f2efe8'; g.textAlign = 'center'; g.fillText('10 Sekunden lang nicht gäbe?', W / 2, 960);
  g.globalAlpha = a * smooth(0.6, 1.4, t) * 0.7; g.font = '400 24px Plex'; g.letterSpacing = '2px';
  g.fillText('WAS HÄTTE DICH AM HÄRTESTEN GETROFFEN?', W / 2, 1060);
  g.fillText('SCHREIB ES IN DIE KOMMENTARE.', W / 2, 1100);
  g.globalAlpha = a * smooth(1.2, 2.0, t) * 0.55; g.font = '500 22px Plex'; g.letterSpacing = '8px';
  g.fillText('DIE WELT OHNE', W / 2, 1700);
  g.restore();
}
