// 2D-Einblendungen: Aufzugsanzeige, Tiefenmesser, Handy-Benachrichtigungen, Sprung in der Scheibe, Untertitel
import {CAPTIONS, SHOTS, ZONES, depthAt, floorOf, pressure, tempAt, lightAt, NO_NET, CRACK, KNOCK, DELIVERED, START} from './timeline.js';
import {clamp, smooth, rng, lerp, easeOut} from './lib.js';

const W = 1080, H = 1920, AMBER = '#ffb347';
const de = n => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
const dec = (n, k) => n.toFixed(k).replace('.', ',');

function shadowText(g, txt, x, y, blur = 18) { g.save(); g.shadowColor = 'rgba(0,0,0,0.75)'; g.shadowBlur = blur; g.shadowOffsetY = 2; g.fillText(txt, x, y); g.restore(); }
function spaced(g, txt, x, y, sp) { g.save(); g.letterSpacing = sp + 'px'; shadowText(g, txt, x, y, 10); g.restore(); }
function wrap(g, text, maxW) { const words = text.split(' '); const lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } lines.push(cur); return lines; }

// angezeigte Tiefe: nach jedem Schnitt rollt der Zähler schnell von der letzten Station zur neuen
function shownDepth(T, shot) {
  const i = SHOTS.indexOf(shot); const d = depthAt(T, shot);
  if (i <= 2) return d;
  const prev = SHOTS[i - 1]; const p = depthAt(prev.t1 - 0.001, prev); const k = easeOut(clamp((T - shot.t0) / 0.75));
  return lerp(p, d, k);
}

function liftDisplay(g, T, shot, d, a) {
  if (a <= 0) return;
  g.save(); g.globalAlpha = a;
  const x = W / 2, y = 175, w = 560, h = 190;
  g.fillStyle = 'rgba(12,14,16,0.78)'; g.beginPath(); g.roundRect(x - w / 2, y - h / 2, w, h, 22); g.fill();
  g.strokeStyle = 'rgba(255,179,71,0.35)'; g.lineWidth = 2; g.stroke();
  g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = 'rgba(255,200,140,0.75)'; g.font = '500 24px Plex'; spaced(g, 'ETAGE', x, y - 62, 6);
  const moving = shot.id !== 'panel' && !(shot.id === 'bottom' && T > 52) && T > START - 0.1;
  const fl = floorOf(d); const txt = fl === 0 ? '0' : '−' + de(fl);
  g.save(); g.shadowColor = 'rgba(255,160,60,0.9)'; g.shadowBlur = 24; g.fillStyle = AMBER; g.font = '500 104px Plex'; g.fillText(txt, x + 26, y + 18); g.restore();
  if (moving) { const bob = (T * 2.2) % 1; g.fillStyle = `rgba(255,179,71,${0.4 + 0.6 * (1 - bob)})`; g.beginPath(); const ax = x - w / 2 + 62, ay = y + 4 + bob * 18; g.moveTo(ax - 22, ay - 14); g.lineTo(ax + 22, ay - 14); g.lineTo(ax, ay + 14); g.fill(); }
  // Messwerte
  const cells = [['TIEFE', de(d) + ' m'], ['DRUCK', de(pressure(d)) + ' bar'], ['WASSER', dec(tempAt(d), 1) + ' °C'], ['LICHT', (() => { const L = lightAt(d); return L >= 1 ? de(L) + ' %' : L >= 0.01 ? dec(L, 2) + ' %' : '0 %'; })()]];
  const cw = 236, y2 = y + h / 2 + 52; const x0 = W / 2 - cw * 2;
  g.fillStyle = 'rgba(12,14,16,0.62)'; g.beginPath(); g.roundRect(x0 - 10, y2 - 38, cw * 4 + 20, 82, 16); g.fill();
  cells.forEach(([l, v], i) => { const cx = x0 + cw * i + cw / 2; g.fillStyle = 'rgba(255,255,255,0.6)'; g.font = '500 17px Plex'; spaced(g, l, cx, y2 - 16, 3);
    g.fillStyle = l === 'DRUCK' && d > 3000 ? '#ff8a6a' : '#fff'; g.font = '500 29px Plex'; shadowText(g, v, cx, y2 + 16, 6); });
  g.restore();
}

function gauge(g, T, d, a) {
  if (a <= 0) return;
  const x = 58, y0 = 470, y1 = 1230, pos = dd => y0 + (y1 - y0) * Math.sqrt(dd / 10920);
  g.save(); g.globalAlpha = a;
  const grd = g.createLinearGradient(0, y0, 0, y1); grd.addColorStop(0, '#5fd3f0'); grd.addColorStop(0.18, '#1f6fae'); grd.addColorStop(0.35, '#123a6a'); grd.addColorStop(1, '#05070c');
  g.fillStyle = grd; g.beginPath(); g.roundRect(x - 7, y0, 14, y1 - y0, 7); g.fill(); g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = 1.5; g.stroke();
  g.textAlign = 'left'; g.textBaseline = 'middle'; g.font = '500 15px Plex';
  ZONES.forEach(([z, n], i) => { const yy = pos(z); g.fillStyle = 'rgba(255,255,255,0.55)'; g.fillRect(x + 10, yy, 14, 2);
    const next = i < ZONES.length - 1 ? pos(ZONES[i + 1][0]) : y1; const on = d >= z && (i === ZONES.length - 1 || d < ZONES[i + 1][0]);
    g.fillStyle = on ? '#fff' : 'rgba(255,255,255,0.45)'; g.save(); g.translate(x + 30, (yy + next) / 2); g.rotate(-Math.PI / 2); g.textAlign = 'center'; g.letterSpacing = '3px';
    if (next - yy > 60) g.fillText(n, 0, 0); g.restore(); });
  const yy = pos(d); g.fillStyle = AMBER; g.shadowColor = 'rgba(255,160,60,0.9)'; g.shadowBlur = 14;
  g.beginPath(); g.moveTo(x - 12, yy); g.lineTo(x - 30, yy - 12); g.lineTo(x - 30, yy + 12); g.fill();
  g.restore();
}

function card(g, a, y, title, line, icon, bars, status) {
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; const x = 110, w = 860, h = 132; const yy = y - (1 - a) * 30;
  g.fillStyle = 'rgba(248,248,250,0.94)'; g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowBlur = 30; g.beginPath(); g.roundRect(x, yy, w, h, 30); g.fill(); g.shadowBlur = 0;
  // Icon: Pizzastück
  g.save(); g.translate(x + 66, yy + h / 2); g.fillStyle = '#ffb347'; g.beginPath(); g.roundRect(-38, -38, 76, 76, 18); g.fill();
  if (icon === 'pizza') { g.fillStyle = '#f6d27a'; g.beginPath(); g.moveTo(-22, -20); g.lineTo(24, -12); g.lineTo(-10, 26); g.closePath(); g.fill(); g.fillStyle = '#c9402c';
    for (const [px, py] of [[-8, -6], [6, -6], [-6, 8]]) { g.beginPath(); g.arc(px, py, 5, 0, 7); g.fill(); } g.fillStyle = '#d9a24f'; g.fillRect(-23, -24, 48, 7); }
  g.restore();
  g.textAlign = 'left'; g.textBaseline = 'alphabetic'; g.fillStyle = '#1b1d20'; g.font = '500 30px Plex'; g.fillText(title, x + 130, yy + 54);
  g.fillStyle = status === 'err' ? '#d63b2f' : status === 'ok' ? '#2f9b4b' : '#5a5f66'; g.font = '400 27px Plex'; g.fillText(line, x + 130, yy + 98);
  if (bars != null) { for (let i = 0; i < 4; i++) { g.fillStyle = i < bars ? '#1b1d20' : 'rgba(0,0,0,0.15)'; g.fillRect(x + w - 120 + i * 20, yy + 66 - i * 12, 13, 18 + i * 12); }
    if (bars === 0) { g.strokeStyle = '#d63b2f'; g.lineWidth = 5; g.beginPath(); g.moveTo(x + w - 126, yy + 30); g.lineTo(x + w - 40, yy + 92); g.stroke(); } }
  g.restore();
}

// Sprung in der Scheibe (bleibt bis zum Ende)
const CR = (() => { const r = rng(77); const segs = []; const ox = 800, oy = 640;
  const grow = (x, y, ang, len, depth, t0) => { let px = x, py = y; const n = 5 + Math.floor(r() * 4);
    for (let i = 0; i < n; i++) { const a = ang + (r() - 0.5) * 0.7; const l = len / n * (0.6 + r() * 0.8); const nx = px + Math.cos(a) * l, ny = py + Math.sin(a) * l;
      segs.push([px, py, nx, ny, t0 + (i / n) * 0.22 * (depth + 1), depth]); if (depth < 2 && r() < 0.35) grow(nx, ny, a + (r() < 0.5 ? 0.7 : -0.7), len * 0.45, depth + 1, t0 + (i / n) * 0.2); px = nx; py = ny; } };
  for (let i = 0; i < 7; i++) grow(ox, oy, i / 7 * Math.PI * 2 + r() * 0.4, 110 + r() * 170, 0, 0);
  const rings = []; for (let k = 1; k <= 3; k++) { const pts = []; for (let i = 0; i <= 18; i++) { const a = i / 18 * Math.PI * 2; const rr = k * 26 + r() * 10; pts.push([ox + Math.cos(a) * rr, oy + Math.sin(a) * rr]); } rings.push(pts); }
  return {segs, rings, ox, oy}; })();
function crack(g, T) {
  const t = T - CRACK; if (t < 0) return;
  g.save(); g.lineCap = 'round';
  for (const [x0, y0, x1, y1, t0, dp] of CR.segs) { const k = clamp((t - t0) / 0.06); if (k <= 0) continue;
    const xe = lerp(x0, x1, k), ye = lerp(y0, y1, k);
    g.strokeStyle = 'rgba(20,30,36,0.55)'; g.lineWidth = 4.5 - dp; g.beginPath(); g.moveTo(x0 + 1.5, y0 + 1.5); g.lineTo(xe + 1.5, ye + 1.5); g.stroke();
    g.strokeStyle = 'rgba(235,248,255,0.85)'; g.lineWidth = 2.4 - dp * 0.6; g.beginPath(); g.moveTo(x0, y0); g.lineTo(xe, ye); g.stroke(); }
  const rk = clamp(t / 0.3); g.strokeStyle = `rgba(235,248,255,${0.7 * rk})`; g.lineWidth = 1.6;
  CR.rings.forEach(pts => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke(); });
  const gr = g.createRadialGradient(CR.ox, CR.oy, 0, CR.ox, CR.oy, 40); gr.addColorStop(0, 'rgba(255,255,255,0.7)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.beginPath(); g.arc(CR.ox, CR.oy, 40, 0, 7); g.fill();
  g.restore();
}

export function drawHUD(g, T, shot, opt = {}) {
  g.clearRect(0, 0, W, H);
  const id = shot.id;
  // Eintauchen: weißer Schaum-Blitz
  { const d = T - 2.25; if (d > -0.05 && d < 0.45) { g.fillStyle = `rgba(225,245,255,${0.75 * (1 - clamp(d / 0.45))})`; g.fillRect(0, 0, W, H); } }
  const vg = g.createRadialGradient(W / 2, H * 0.46, H * 0.28, W / 2, H * 0.5, H * 0.78); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.5)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);
  if (id !== 'surface' && id !== 'panel' && !opt.noCrack) crack(g, T);

  const d = shownDepth(T, shot);
  const ua = smooth(5.0, 5.5, T);
  liftDisplay(g, T, shot, d, ua); gauge(g, T, d, smooth(9.0, 9.6, T));

  // Handy: Pizza bestellen – und das Netz ist weg
  { const a = smooth(9.5, 9.85, T) * (1 - smooth(13.6, 14.0, T)); const bars = T < 10.5 ? 4 : T < NO_NET ? Math.max(0, 3 - Math.floor((T - 10.5) / 0.3)) : 0;
    if (a > 0) card(g, a, 420, 'Pizza Salami · an Etage −3.640', T < NO_NET ? 'Bestellung wird gesendet' + '.'.repeat(1 + Math.floor(T * 3) % 3) : 'Kein Netz. Bestellung hängt fest.', 'pizza', bars, T < NO_NET ? '' : 'err'); }
  { const a = smooth(DELIVERED, DELIVERED + 0.35, T) * (1 - smooth(59.0, 59.5, T)); if (a > 0) card(g, a, 420, 'Pizza Salami · Etage −3.640', 'Zugestellt. Lieferzeit: 4 Std. 02 Min.', 'pizza', null, 'ok'); }
  // Klopfen
  if (T > KNOCK - 0.05 && T < KNOCK + 1.1) { const a = smooth(KNOCK - 0.05, KNOCK + 0.05, T) * (1 - smooth(KNOCK + 0.8, KNOCK + 1.1, T));
    g.save(); g.globalAlpha = a; g.fillStyle = '#fff'; g.font = 'italic 400 58px Garamond'; g.textAlign = 'center'; shadowText(g, '*klopf*', 330, 520); if (T > KNOCK + 0.3) shadowText(g, '*klopf*', 720, 470); g.restore(); }

  // Untertitel
  for (const [a, b, txt] of CAPTIONS) {
    if (T < a - 0.1 || T > b + 0.1) continue;
    const al = smooth(a - 0.1, a + 0.2, T) * (1 - smooth(b - 0.2, b + 0.1, T));
    const big = txt === 'Knack.' || txt === 'Bis heute.' || txt === 'Und dann …';
    g.save(); g.globalAlpha = al; g.textAlign = 'center'; g.font = big ? 'italic 400 78px Garamond' : 'italic 400 54px Garamond';
    const lines = wrap(g, txt, 900); const cy = 1420;
    const bg = g.createRadialGradient(W / 2, cy, 30, W / 2, cy, 540); bg.addColorStop(0, 'rgba(0,0,0,0.62)'); bg.addColorStop(1, 'rgba(0,0,0,0)');
    g.save(); g.translate(W / 2, cy); g.scale(1, 0.34); g.translate(-W / 2, -cy); g.fillStyle = bg; g.fillRect(0, cy - 540, W, 1080); g.restore(); g.fillStyle = '#fff';
    lines.forEach((l, i) => shadowText(g, l, W / 2, cy + 12 + i * 64 - (lines.length - 1) * 32 + (1 - al) * 10, 22));
    g.restore();
  }
  const fo = smooth(59.0, 59.95, T);
  if (fo > 0) { g.save(); g.globalAlpha = fo; g.fillStyle = '#000'; g.fillRect(0, 0, W, H); g.restore(); }
}
