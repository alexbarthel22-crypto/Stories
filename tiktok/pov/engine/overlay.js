// 2D-Einblendungen: Ort/Zeit oben links, Untertitel, Benachrichtigungskarte, Schwarzblende.
const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

export class Overlay {
  constructor(el, story) {
    this.el = el; this.story = story;
    el.innerHTML = '<div class="fade"></div><div class="loc"></div><div class="cap"></div><div class="notif"></div><div class="ende"></div>';
    this.loc = el.querySelector('.loc'); this.cap = el.querySelector('.cap'); this.notif = el.querySelector('.notif'); this.fade = el.querySelector('.fade'); this.ende = el.querySelector('.ende');
    this.capY = story.untertitel_y ?? 0.6;
    this.last = {};
  }
  set(key, node, html) { if (this.last[key] !== html) { node.innerHTML = html; this.last[key] = html; } }
  update(t, s) {
    // Ort / Zeit
    const L = s.label;
    if (L) {
      const [title, sub] = Array.isArray(L) ? L : [L.titel, L.unter];
      this.loc.className = 'loc' + (L.klein || this.story.label_klein ? ' small' : '');
      this.set('loc', this.loc, `<div class="t">${esc(title || '')}</div><div class="bar"></div><div class="s">${esc(sub || '')}</div>`);
      this.loc.style.opacity = 1;
    } else this.loc.style.opacity = 0;
    // Untertitel
    let html = '', col = '#fff', k = 1;
    for (const l of s.lines) {
      if (t < l.t0 || t >= l.t1 || !l.caps.length) continue;
      for (const c of l.caps) if (t >= c.t0 && t < c.t1) { html = c.text; k = Math.min(1, (t - c.t0) / 0.08); }
      col = l.color || s.cast?.[l.who]?.farbe || (l.who === 'ich' ? '#ffffff' : '#ffd43b');
    }
    for (const c of s.caps) if (t >= c.t0 && t < c.t1) { html = c.text; col = c.color; }
    this.set('cap', this.cap, esc(html));
    this.cap.style.color = col; this.cap.style.top = Math.round(1920 * this.capY) + 'px';
    this.cap.style.transform = `translateY(-50%) scale(${0.9 + 0.1 * k})`;
    // Benachrichtigung (fährt von oben rein)
    const n = s.notify;
    if (n) {
      const v = n.v, a = Math.min(1, (t - n.t0) / 0.25), b = Math.min(1, (n.t1 - t) / 0.25), k2 = Math.min(a, b);
      this.set('notif', this.notif, `<div class="h"><i>${esc(v.icon || '📞')}</i>${esc(v.titel || '')}</div><div class="b">${esc(v.text || '')}</div>`);
      this.notif.style.display = 'block'; this.notif.style.transform = `translateY(${(1 - k2) * -260}px)`;
    } else this.notif.style.display = 'none';
    this.fade.style.opacity = s.fade || 0;
    // Abspann-Karte "FORTSETZUNG FOLGT" (bleibt bis zum Schluss)
    const E = s.ende;
    if (E) {
      this.set('ende', this.ende, `<div class="t">${esc(E.text)}</div><div class="bar"></div>${E.unter ? `<div class="s">${esc(E.unter)}</div>` : ''}`);
      const a = Math.min(1, E.k / 0.5);
      this.ende.style.opacity = a; this.ende.style.transform = `translate(-50%,-50%) scale(${1.08 - 0.08 * Math.min(1, E.k / 3)})`;
      this.ende.querySelector('.bar').style.width = Math.round(Math.min(1, Math.max(0, (E.k - 0.3) / 0.8)) * 420) + 'px';
      this.ende.style.letterSpacing = (0.08 + 0.04 * Math.min(1, E.k / 3)).toFixed(3) + 'em';
    } else this.ende.style.opacity = 0;
  }
}
