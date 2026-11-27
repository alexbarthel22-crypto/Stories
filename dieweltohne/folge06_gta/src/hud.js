// 2D-Einblendungen: Titel, Emblem, Countdown, Messwerte, Gefahrenstufe, Untertitel
import {CAPTIONS, STAGES, STAGE_OF, VANISH, RETURN, PAPA_UP, BRAKE, STOP, FREQ0, CITY_OUT, EU_OUT, FLASH_ON, POWER_BACK, TV_ON, DOOR, worldLeft} from './timeline.js';
import {clamp, smooth, lerp} from './lib.js';

const ACC = '#ff6fb1';
const W = 1080, H = 1920;
function fmt(v) { v = Math.max(0, v); const m = Math.floor(v / 60), s = Math.floor(v - m * 60), ms = Math.floor((v - Math.floor(v)) * 1000); return `${m}:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`; }
const de = n => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
const dec = (n, k) => n.toFixed(k).replace('.', ',');
function shadowText(g, txt, x, y, blur = 18) { g.save(); g.shadowColor = 'rgba(0,0,0,0.75)'; g.shadowBlur = blur; g.shadowOffsetY = 2; g.fillText(txt, x, y); g.restore(); }
function spaced(g, txt, x, y, sp) { g.save(); g.letterSpacing = sp + 'px'; shadowText(g, txt, x, y, 10); g.restore(); }
function wrap(g, text, maxW) { const words = text.split(' '); const lines = []; let cur = ''; for (const w of words) { const t = cur ? cur + ' ' + w : w; if (g.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } lines.push(cur); return lines; }
// Emblem: Controller-Symbol mit Skala
function emblem(g, T, a, cx = W / 2, cy = 215, r = 105) {
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; g.translate(cx, cy);
  g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 2.5; g.beginPath(); g.arc(0, 0, r, 0, Math.PI * 2); g.stroke();
  g.lineWidth = 1.2; g.strokeStyle = 'rgba(255,255,255,0.5)'; g.beginPath(); g.arc(0, 0, r - 12, 0, Math.PI * 2); g.stroke();
  for (let i = 0; i < 60; i++) { const an = i / 60 * Math.PI * 2 + T * 0.15; const l = i % 5 ? 6 : 13; g.beginPath(); g.moveTo(Math.cos(an) * (r - 12), Math.sin(an) * (r - 12)); g.lineTo(Math.cos(an) * (r - 12 - l), Math.sin(an) * (r - 12 - l)); g.stroke(); }
  // Controller
  g.fillStyle = 'rgba(255,255,255,0.92)'; g.beginPath(); g.roundRect(-46, -14, 92, 30, 14); g.fill();
  g.beginPath(); g.ellipse(-36, 16, 16, 24, 0.35, 0, 7); g.fill(); g.beginPath(); g.ellipse(36, 16, 16, 24, -0.35, 0, 7); g.fill();
  g.fillStyle = '#20232b'; g.fillRect(-36, -2, 16, 5); g.fillRect(-30.5, -8, 5, 16); for (const [x, y] of [[30, -6], [38, 1], [30, 8], [22, 1]]) { g.beginPath(); g.arc(x, y, 3.5, 0, 7); g.fill(); }
  g.fillStyle = '#fff'; g.font = '400 15px Plex'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.globalAlpha = a * 0.75; spaced(g, 'GTA 6 · 10 s', 0, 72, 2);
  g.restore();
}
export function drawHUD(g, T, shot) {
  g.clearRect(0, 0, W, H);
  if (!shot || shot.id === 'test') return;
  // Bildstörung beim Verschwinden
  { const d = T - VANISH; if (d > -0.02 && d < 0.35) { g.fillStyle = `rgba(255,255,255,${0.25 * (1 - d / 0.35)})`; for (let i = 0; i < 40; i++) g.fillRect(0, (Math.sin(i * 91.7 + T * 300) * 0.5 + 0.5) * H, W, 3 + (i % 4) * 4); } }
  // Fernseher an: weißer Blitz
  { const d = T - TV_ON; if (d > -0.02 && d < 0.4) { g.fillStyle = `rgba(255,250,240,${0.45 * (1 - d / 0.4)})`; g.fillRect(0, 0, W, H); } }
  const vg = g.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.38)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);
  // Titel
  const ta = clamp(T / 0.4) * (1 - smooth(4.3, 5.0, T));
  if (ta > 0) {
    g.save(); g.globalAlpha = ta; g.textBaseline = 'alphabetic'; g.fillStyle = '#fff'; g.font = '400 68px Garamond';
    const l1a = 'Was wäre, wenn ', l1b = 'GTA 6';
    const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
    g.textAlign = 'left'; shadowText(g, l1a, x0, 420); g.fillStyle = ACC; shadowText(g, l1b, x0 + w1, 420);
    g.fillStyle = '#fff'; g.textAlign = 'center'; shadowText(g, '10 Sekunden verschwindet?', W / 2, 500);
    g.restore();
  }
  emblem(g, T, clamp(T / 0.4) * (1 - smooth(4.6, 5.2, T)));
  // Countdown-Block links
  let label, value, sub = '', prog, accent = '#fff', alarm = 0;
  const wl = worldLeft(T);
  if (T < VANISH) { label = 'GTA 6 WEG IN'; value = fmt(VANISH - T); prog = 1 - (VANISH - T) / VANISH; if (VANISH - T < 3.5) alarm = 1; }
  else if (T < RETURN) { label = 'GTA 6 ZURÜCK IN'; value = fmt(wl); prog = 1 - wl / 10; accent = ACC; }
  else { label = 'GTA 6'; value = 'ZURÜCK'; prog = 1; }
  const ws = 'GTA 6 ZURÜCK IN ' + fmt(wl); const t = T - shot.t0;
  if (shot.id === 'vanish') { label = 'LETZTER SPEICHERSTAND'; value = T < 12.8 ? '…' : 'VOR 3 STD.'; sub = ws; alarm = T > 12.8 ? 1 : 0; }
  if (shot.id === 'papa') { label = 'PAPAS SPIELZEIT HEUTE'; value = '4 STD. 41 MIN.'; sub = ws; alarm = T > PAPA_UP ? 1 : 0; }
  if (shot.id === 'street') { const d = T < BRAKE ? null : T < STOP ? lerp(6.3, 0.35, ((T - BRAKE) / (STOP - BRAKE)) ** 0.5) : 0.35; label = 'ABSTAND ZUM AUTO'; value = d === null ? '–' : dec(d, 2) + ' m'; sub = ws; alarm = T > BRAKE ? 1 : 0; }
  if (shot.id === 'control') { const k = smooth(FREQ0, 38.5, T); label = 'WEGGEFALLENER VERBRAUCH'; value = 'MILLIONEN KONSOLEN'; sub = ws; alarm = T > 35.2 ? 1 : 0; }
  if (shot.id === 'city') { label = 'STADT OHNE STROM'; value = Math.round(100 * clamp((T - CITY_OUT) / 6.7)) + ' %'; sub = ws; alarm = 1; accent = '#e5482b'; }
  if (shot.id === 'europe') { label = 'EUROPA IM DUNKELN'; value = T < EU_OUT ? '–' : 'HALB'; sub = ws; alarm = 1; accent = '#e5482b'; }
  if (shot.id === 'dark') { label = 'STROM'; value = 'WEG'; alarm = 1; accent = '#e5482b'; }
  if (shot.id === 'back') { label = 'STROM'; value = T < POWER_BACK ? 'WEG' : 'KOMMT ZURÜCK'; alarm = T < POWER_BACK ? 1 : 0; accent = '#4cc76a'; }
  if (shot.id === 'blast') { label = 'LAUTSTÄRKE'; value = T < TV_ON ? '–' : '100 %'; alarm = T > TV_ON ? 1 : 0; accent = '#e5482b'; }
  if (shot.id === 'mom') { label = 'KONSOLE'; value = T < 83 ? 'NOCH DA' : 'BIS WEIHNACHTEN WEG'; alarm = T > 83 ? 1 : 0; accent = '#e5482b'; }
  const x = 64, y = 1000;
  g.save(); g.fillStyle = '#fff';
  g.strokeStyle = 'rgba(255,255,255,0.25)'; g.lineWidth = 4; g.beginPath(); g.arc(x + 30, y - 70, 28, 0, Math.PI * 2); g.stroke();
  g.strokeStyle = accent; g.beginPath(); g.arc(x + 30, y - 70, 28, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * clamp(prog)); g.stroke();
  g.font = '500 25px Plex'; g.textAlign = 'left'; g.textBaseline = 'alphabetic'; spaced(g, label, x, y, 3);
  const blink = alarm ? 0.55 + 0.45 * (Math.sin(T * 12) > -0.3 ? 1 : 0) : 1;
  g.fillStyle = alarm ? `rgba(255,${Math.round(120 + 135 * (1 - alarm * 0.6))},${Math.round(90 * (1 - alarm))},${blink})` : '#fff';
  g.font = value.length > 14 ? '400 62px Garamond' : value.length > 10 ? '400 76px Garamond' : '400 92px Garamond'; shadowText(g, value, x - 3, y + 88);
  g.fillStyle = '#fff';
  if (sub) { g.font = '400 21px Plex'; g.globalAlpha = 0.72; spaced(g, sub, x, y + 128, 3); g.globalAlpha = 1; }
  g.restore();
  // Gefahrenstufe
  const st = STAGE_OF[shot.id] || 0;
  if (st) {
    const yb = y + (sub ? 160 : 128), cols = ['#4cc76a', '#a5d34a', '#e8d13a', '#f3a531', '#f07a2a', '#e5482b', '#c4161c'];
    g.save();
    for (let i = 0; i < 7; i++) { const on = i < st, pulse = on && i === st - 1 ? 0.75 + 0.25 * Math.sin(T * 8) : 1; g.globalAlpha = on ? pulse : 0.22; g.fillStyle = on ? cols[i] : '#ffffff'; g.beginPath(); g.roundRect(x + i * 46, yb, 40, 10, 3); g.fill(); }
    g.globalAlpha = 1; g.fillStyle = cols[st - 1]; g.font = '500 23px Plex'; spaced(g, `STUFE ${st}/7 · ${STAGES[st - 1]}`, x, yb + 44, 3);
    g.restore();
  }
  // Ortsmarken oben
  const place = {intro: '23:40 · SEIN ZIMMER', play: '23:40 · SEIN ZIMMER', vanish: '23:41 · SEIN ZIMMER', papa: '23:41 · WOHNZIMMER', street: '23:41 · VOR DER HAUSTÜR', control: '23:41 · NETZLEITSTELLE', city: '23:41 · DIE STADT', europe: '23:41 · EUROPA', dark: '23:52 · SEIN ZIMMER', back: '2:13 · DIE STADT', blast: '2:13 · SEIN ZIMMER', mom: '2:13 · SEIN ZIMMER'}[shot.id];
  if (place && T > 5.2) { const a = smooth(shot.t0 + 0.1, shot.t0 + 0.5, T) * (1 - smooth(shot.t1 - 0.4, shot.t1, T)); g.save(); g.globalAlpha = a * 0.85; g.fillStyle = '#fff'; g.font = '500 24px Plex'; g.textAlign = 'left'; spaced(g, place, 64, 150, 4); g.restore(); }
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
  const fo = smooth(88.9, 89.9, T);
  if (fo > 0) { g.save(); g.globalAlpha = fo; g.fillStyle = '#000'; g.fillRect(0, 0, W, 99999); g.restore(); }
}
