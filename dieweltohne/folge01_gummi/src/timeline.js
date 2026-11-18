// Zentrale Zeitleiste (Sekunden im Video). Wird auch von der Tonmischung gelesen (timeline.json).
export const FPS = 30, DURATION = 90;

// Szenen: welches Set, welcher Bildausschnitt
export const SHOTS = [
  {id: 'intro', t0: 0, t1: 4.2},          // POV Handy im Regen, Straße
  {id: 'cars_wide', t0: 4.2, t1: 8.4},    // Reifen verschwinden
  {id: 'cars_wheel', t0: 8.4, t1: 10.8},  // Felge schleift, Funken, Stahldrähte
  {id: 'cars_crash', t0: 10.8, t1: 13},   // Auffahrunfall
  {id: 'phone', t0: 13, t1: 20},          // Handyhülle weg, Wasser dringt ein
  {id: 'soles', t0: 20, t1: 27},          // Sohlen weg, Leute rutschen aus
  {id: 'pants', t0: 27, t1: 33},          // Gummizug weg, Hosen rutschen
  {id: 'balloons', t0: 33, t1: 40},       // Luftballons, Haargummi
  {id: 'kitchen', t0: 40, t1: 47},        // Rohrdichtungen, Waschmaschine
  {id: 'plane', t0: 47, t1: 55},          // Landung auf Felgen
  {id: 'globe', t0: 55, t1: 62},          // 1,5 Mrd. Fahrzeuge
  {id: 'gummy', t0: 62, t1: 68},          // Gummibärchen bleiben
  {id: 'last', t0: 68, t1: 70},           // letzte Sekunden, Straße
  {id: 'back', t0: 70, t1: 78},           // Gummi zurück: Reifen liegen hinter den Autos
  {id: 'later', t0: 78, t1: 85},          // 5 Minuten später, Luftbild Stau
  {id: 'end', t0: 85, t1: 90},            // Schlusskarte
];

export const VANISH = 5.0, RETURN = 70.0;

// Weltzeit-Countdown (Sekunden bis der Gummi zurückkommt) an Stützstellen
const WK = [[5, 10], [8.4, 9.55], [13, 9.1], [20, 8.2], [27, 7.3], [33, 6.5], [40, 5.6], [47, 4.6], [55, 3.5], [62, 1.8], [68, 0.3], [70, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}

export const TAGS = {
  cars_wide: 'REIFEN', cars_wheel: 'REIFEN', cars_crash: 'REIFEN', phone: 'DICHTUNGEN', soles: 'SCHUHSOHLEN',
  pants: 'GUMMIZÜGE', balloons: 'LATEX', kitchen: 'ROHRDICHTUNGEN', plane: 'FLUGZEUGREIFEN', globe: 'WELTWEIT',
  gummy: 'GELATINE', last: 'LETZTE SEKUNDEN',
};

export const CAPTIONS = [
  [5.5, 8.3, 'Ein Autoreifen ist vor allem eins: Gummi.'],
  [8.6, 10.7, 'Übrig bleiben nur die Stahldrähte.'],
  [10.9, 12.9, 'Bremsen? Bringt nichts mehr.'],
  [13.4, 16.3, 'Die Silikonhülle: weg.'],
  [16.5, 19.8, 'Wasserdicht war es nur wegen winziger Gummidichtungen.'],
  [20.5, 23.5, 'Fast jede Schuhsohle ist aus Gummi.'],
  [23.7, 26.8, 'Und der Boden ist nass.'],
  [27.4, 30.0, 'Jeder Gummizug.'],
  [30.2, 32.8, 'In jeder Hose.'],
  [33.4, 36.6, 'Luftballons sind aus Latex – Naturkautschuk.'],
  [36.8, 39.8, 'Haargummis übrigens auch.'],
  [40.4, 43.6, 'Jede Dichtung in jeder Wasserleitung.'],
  [43.8, 46.8, 'Alle gleichzeitig.'],
  [47.4, 50.8, 'Genau jetzt setzt ein Flugzeug auf.'],
  [51.0, 54.8, 'Auf blanken Felgen.'],
  [55.4, 58.6, 'Weltweit gibt es rund 1,5 Milliarden Fahrzeuge.'],
  [58.8, 61.8, 'Keins davon hat noch Reifen.'],
  [62.4, 65.0, 'Gummibärchen? Bleiben.'],
  [65.2, 67.8, 'Die sind aus Gelatine – nicht aus Gummi.'],
  [70.6, 73.8, 'Der Gummi kehrt zurück. Genau dorthin, wo er war.'],
  [74.0, 77.8, 'Die Autos sind längst weitergerutscht.'],
  [78.4, 81.4, 'Jede Straße ist blockiert.'],
  [81.6, 84.8, 'Auch die Krankenwagen stehen auf kaputten Felgen.'],
];

// Sekunden, in denen der Countdown tickt (für den Ton)
export function tickTimes() {
  const out = []; let last = 10;
  for (let f = Math.round(VANISH * FPS); f <= Math.round(RETURN * FPS); f++) {
    const v = worldLeft(f / FPS);
    if (Math.floor(v * 10) < Math.floor(last * 10)) out.push(+(f / FPS).toFixed(3));
    last = v;
  }
  return out;
}
