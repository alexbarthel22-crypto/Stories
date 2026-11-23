// 2D-Einblendungen: Titel, Emblem, Countdowns, Messwerte, Gefahrenstufe, Untertitel
import {CAPTIONS, STAGES, STAGE_OF, VANISH, RETURN, LEMON, FLASH, TRAY, SINK, HOLES, TOWER_HIT, WINDOW, BURIED, worldLeft} from './timeline.js';
import {clamp, smooth, rng, lerp} from './lib.js';
// Partikelwolke: beim Verschwinden stiebt sie auseinander, bei der Rückkehr zieht sie sich zur Bildmitte zusammen
function shellBurst(g, d, out) { const r = rng(91); for (let i = 0; i < 380; i++) { const x0 = r() * W, y0 = r() * H, s = 2 + r() * 6;
  let x, y, a;
  if (out) { x = x0 + (r() - 0.5) * 700 * d; y = y0 - (150 + r() * 600) * d; a = (1 - d) * (0.5 + r() * 0.5); }
  else { const k = 1 - Math.pow(1 - d, 2); x = lerp(x0, W / 2 + (r() - 0.5) * 120, k); y = lerp(y0, H * 0.45 + (r() - 0.5) * 120, k); a = Math.sin(d * Math.PI) * (0.5 + r() * 0.5); }
  if (y < -20 || y > H + 20) continue;
  const pc = r(); g.fillStyle = pc < 0.4 ? `rgba(40,50,80,${a * 0.85})` : pc < 0.75 ? `rgba(240,232,215,${a * 0.85})` : `rgba(215,225,255,${a * 0.9})`; g.beginPath(); g.arc(x, y, s, 0, 7); g.fill();
  } }

const ORANGE = '#7fd6ff';
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
  g.textAlign = 'center'; g.textBaseline = 'middle'; // Jakobsmuschel
  g.save(); g.translate(0, 8); const sg = g.createRadialGradient(0, 22, 4, 0, 10, 62); sg.addColorStop(0, '#fff6ea'); sg.addColorStop(1, '#e8b48a'); g.fillStyle = sg;
  g.beginPath(); g.moveTo(-10, 26); for (let i = 0; i <= 12; i++) { const an = Math.PI * (1.12 + 0.76 * i / 12); g.lineTo(Math.cos(an) * 52, 26 + Math.sin(an) * 56); } g.lineTo(10, 26); g.closePath(); g.fill();
  g.strokeStyle = 'rgba(150,90,50,0.6)'; g.lineWidth = 2; for (let i = 1; i < 12; i++) { const an = Math.PI * (1.12 + 0.76 * i / 12); g.beginPath(); g.moveTo(0, 24); g.lineTo(Math.cos(an) * 50, 26 + Math.sin(an) * 53); g.stroke(); }
  g.fillStyle = '#e8b48a'; g.fillRect(-16, 24, 32, 10); g.restore();
  g.fillStyle = '#fff'; g.font = '400 15px Plex'; g.globalAlpha = a * 0.75; spaced(g, 'MUSCHELN · 10 s', 0, 58, 2);
  g.restore();
}

const CHAT = [
  [1.0, 'nico_04', 'endlich austern 🦪'], [2.2, 'leaa.mp4', 'wie schmeckt das überhaupt'], [3.4, 'xXjanXx', 'schlürf schlürf'], [4.6, 'mira', 'ich könnte das nie 😭'],
  [5.8, 'kev1n', 'hau rein bro'], [7.0, 'luca.fx', 'der ganze teller??'], [8.2, 'aylin', 'ICH SCHAU SEIT 2 STUNDEN'], [9.2, 'tobi_', 'jetzt jetzt jetzt'],
  [10.3, 'nico_04', 'WO IST DIE AUSTER'], [10.7, 'leaa.mp4', '😂😂😂😂'], [11.1, 'kev1n', 'er schlürft LUFT'], [11.5, 'mira', 'ICH KANN NICHT MEHR'],
  [12.0, 'luca.fx', 'zitrone??'], [12.6, 'aylin', 'DAS AUGE 💀💀'], [13.0, 'tobi_', 'clip it clip it'], [13.5, 'xXjanXx', '😂😂😂'], [14.2, 'nico_04', 'bester stream ever'],
  [15.0, 'leaa.mp4', 'L + zitrone'], [15.8, 'kev1n', 'F im chat'], [16.4, 'mira', '😭😭😭'],
  [58.6, 'tobi_', 'warum so traurig'], [59.6, 'aylin', 'immer noch keine auster?'], [60.6, 'kev1n', 'was wackelt da'], [61.4, 'luca.fx', 'BRO DREH DICH UM'],
  [62.0, 'mira', 'DAS FENSTER'], [62.7, 'nico_04', 'AAAAAAAAA'], [63.0, 'leaa.mp4', '🦪🦪🦪🦪🦪🦪'], [63.4, 'xXjanXx', 'WAS IST DAS'], [63.8, 'kev1n', 'er wollte doch eine 💀'],
  [64.3, 'aylin', 'ICH SCHREIE'], [64.8, 'tobi_', 'ruf wer die feuerwehr'], [65.4, 'luca.fx', 'das sind ALLE muscheln'], [66.0, 'mira', '🦪🦪🦪🦪'], [66.6, 'nico_04', 'bruh'],
  [67.2, 'leaa.mp4', 'guten appetit 😂'], [68.0, 'kev1n', 'er schwimmt'], [68.6, 'xXjanXx', 'SCHWIMM BRO'], [69.2, 'aylin', '🦪🦪🦪🦪🦪🦪🦪'], [69.9, 'tobi_', 'trending #1'],
  [70.5, 'luca.fx', 'das ringlicht 💀'], [71.2, 'mira', 'live dabei gewesen'], [71.9, 'nico_04', '1 MIO ZUSCHAUER'], [72.6, 'leaa.mp4', 'hilfe'], [73.3, 'kev1n', 'er sinkt'],
  [74.0, 'xXjanXx', 'NEIIIN'], [74.6, 'aylin', 'F'], [75.2, 'tobi_', 'F'], [75.8, 'luca.fx', 'F'], [76.4, 'mira', 'F 🦪'], [77.0, 'nico_04', 'F']];
const NAMEC = {nico_04: '#7fd6ff', 'leaa.mp4': '#ff8ad0', xXjanXx: '#ffd23a', mira: '#9dff8a', kev1n: '#ff9a5a', 'luca.fx': '#c9a2ff', aylin: '#ff6b6b', tobi_: '#5affd6'};
function chat(g, T, id) {
  const x0 = 640, w = 400, y1 = 1250;
  const viewers = T < 58 ? 40312 + Math.floor(T * 37) : T < WINDOW ? 52880 + Math.floor((T - 58) * 210) : Math.floor(54000 + 9.8e6 * Math.pow(smooth(WINDOW, 77, T), 1.7));
  g.save();
  // LIVE-Marke und Zuschauer
  g.fillStyle = '#e5263b'; g.beginPath(); g.roundRect(x0 + 168, 600, 86, 40, 8); g.fill();
  g.fillStyle = '#fff'; g.font = '500 24px Plex'; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillText('LIVE', x0 + 183, 621);
  g.fillStyle = 'rgba(0,0,0,0.55)'; g.beginPath(); g.roundRect(x0 + 262, 600, 138, 40, 8); g.fill();
  g.fillStyle = '#fff'; g.font = '400 22px Plex'; g.fillText('👁 ' + de(viewers), x0 + 272, 621);
  // Chat-Nachrichten (die letzten 6)
  const msgs = CHAT.filter(m => m[0] <= T && T - m[0] < (id === 'fill' || id === 'back' ? 6 : 9)).slice(-5);
  g.font = '500 25px Plex'; g.textBaseline = 'alphabetic';
  msgs.forEach((m, i) => { const y = y1 - (msgs.length - 1 - i) * 46; const a = clamp((T - m[0]) / 0.2);
    g.globalAlpha = a; const txt = m[2]; g.font = '500 24px Plex'; const nw = g.measureText(m[1] + ': ').width; g.font = '400 24px Plex'; const tw = g.measureText(txt).width;
    const bx = x0 + w - nw - tw - 26; g.fillStyle = 'rgba(0,0,0,0.5)'; g.beginPath(); g.roundRect(bx, y - 30, nw + tw + 22, 40, 10); g.fill();
    g.font = '500 24px Plex'; g.fillStyle = NAMEC[m[1]] || '#fff'; g.fillText(m[1] + ': ', bx + 11, y - 2); g.font = '400 24px Plex'; g.fillStyle = '#fff'; g.fillText(txt, bx + 11 + nw, y - 2); });
  g.restore();
}

export function drawHUD(g, T, shot) {
  g.clearRect(0, 0, W, H);
  // Blitz beim Verschwinden (im All) und bei der Rückkehr des Lichts
  { const d = T - VANISH; if (d > -0.02 && d < 0.9) shellBurst(g, d / 0.9, true); }
  { const d = T - (RETURN - 0.6); if (d > 0 && d < 0.9) shellBurst(g, d / 0.9, false); }
  // Blitz beim Gruppenfoto, eingefrorenes Foto mit weißem Rahmen
  { const d = T - FLASH; if (d > -0.05 && d < 0.5) { g.fillStyle = `rgba(255,255,255,${0.95 * (1 - clamp(d / 0.5))})`; g.fillRect(0, 0, W, H); }
    if (T > FLASH + 0.15 && T < 23.9) { const k = smooth(FLASH + 0.15, FLASH + 0.5, T) * (1 - smooth(23.4, 23.9, T)); g.save(); g.globalAlpha = k; g.strokeStyle = '#fbfaf5'; g.lineWidth = 46; g.strokeRect(60, 300, W - 120, 1160);
      g.lineWidth = 2; g.strokeStyle = 'rgba(0,0,0,0.25)'; g.strokeRect(37, 277, W - 74, 1206); g.restore(); } }
  const vg = g.createRadialGradient(W / 2, H * 0.48, H * 0.3, W / 2, H * 0.5, H * 0.75);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = vg; g.fillRect(0, 0, W, H);

  // Titel
  const ta = clamp(T / 0.4) * (1 - smooth(4.3, 5.0, T));
  if (ta > 0) {
    g.save(); g.globalAlpha = ta; g.textBaseline = 'alphabetic'; g.fillStyle = '#fff';
    g.font = '400 68px Garamond';
    const l1a = 'Was wäre, wenn ', l1b = 'Muscheln';
    const w1 = g.measureText(l1a).width, w2 = g.measureText(l1b).width, x0 = W / 2 - (w1 + w2) / 2;
    g.textAlign = 'left'; shadowText(g, l1a, x0, 420); g.fillStyle = ORANGE; shadowText(g, l1b, x0 + w1, 420);
    g.fillStyle = '#fff'; g.textAlign = 'center'; shadowText(g, '10 Sekunden verschwinden?', W / 2, 500);
    g.restore();
  }
  emblem(g, T, clamp(T / 0.4) * (1 - smooth(4.6, 5.2, T)));

  // Countdown-Block links
  let label, value, sub = '', prog, accent = '#fff', alarm = 0;
  const wl = worldLeft(T);
  if (T < VANISH) { label = 'MUSCHELN VERSCHWINDEN IN'; value = fmt(VANISH - T); prog = 1 - (VANISH - T) / VANISH; if (VANISH - T < 3.5) alarm = 1; }
  else if (T < RETURN) { label = 'MUSCHELN ZURÜCK IN'; value = fmt(wl); prog = 1 - wl / 10; accent = ORANGE; }
  else { label = 'MUSCHELN'; value = 'ZURÜCK'; prog = 1; }
  const ws = 'MUSCHELN ZURÜCK IN ' + fmt(wl), t = T - shot.t0;
  if (shot.id === 'slurp') { label = 'AUSTERN AUF DEM TELLER'; value = T < VANISH ? '12' : '0'; sub = ws; alarm = 0; }
  if (shot.id === 'prom') { label = 'KNÖPFE AN DEN HEMDEN'; value = '0'; sub = ws; alarm = T > FLASH ? 1 : 0; }
  if (shot.id === 'terrace') { label = 'GEWICHT AUF DEM TABLETT'; value = T < TRAY ? '9,6 kg' : '1,8 kg'; sub = ws; alarm = T > TRAY ? 1 : 0; }
  if (shot.id === 'watt') { label = 'EINGESUNKEN'; value = Math.round(85 * smooth(SINK, SINK + 1.6, T)) + ' cm'; sub = ws; alarm = T > SINK ? 1 : 0; }
  if (shot.id === 'church') { label = 'LÖCHER IM KIRCHTURM'; value = de(Math.floor(48000 * Math.pow(smooth(HOLES, 43.6, T), 1.4))); sub = ws; alarm = T > HOLES ? 1 : 0; }
  if (shot.id === 'rain') { label = 'MUSCHELN VOM HIMMEL'; value = de(Math.floor(1e6 * Math.pow(smooth(48.2, 57.5, T), 2) * 1800)); alarm = 1; accent = ORANGE; }
  if (shot.id === 'intro' || shot.id === 'wait') { /* Standard-Countdown */ }
  if (shot.id === 'back' || shot.id === 'fill') { label = 'AUSTERN FÜR IHN'; value = T < WINDOW ? '0' : de(Math.floor(3e5 * Math.pow(smooth(WINDOW, 77.5, T), 1.6) * 3e4)); alarm = T > WINDOW ? 1 : 0; prog = 1; accent = '#e5482b'; }
  if (shot.id === 'aerial' || shot.id === 'final') { label = 'AUSTERN FÜR IHN'; value = 'ALLE'; alarm = 1; prog = 1; accent = '#e5482b'; }
  if (shot.id === 'rain' && value.length > 12) value = value.slice(0, 13);
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
  // Livestream-Overlay: LIVE, Zuschauerzahl, Chat
  if (['intro', 'wait', 'slurp', 'back', 'fill'].includes(shot.id)) chat(g, T, shot.id);

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
