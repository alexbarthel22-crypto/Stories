// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Idee: Du wohnst in einem Hochhaus mitten im Meer – nur geht es nicht hoch, sondern 3.640 Etagen nach unten.
// Mit dem gläsernen Aufzug geht es Station für Station bis zum tiefsten Punkt der Erde.
export const FPS = 30, DURATION = 60;
export const FLOOR_H = 3; // Meter pro Etage

export const SHOTS = [
  {id: 'surface', t0: 0, t1: 5, d0: 0, d1: 0},           // Hook: Eingang mitten im Meer – Kamera taucht ab, der Turm geht endlos nach unten
  {id: 'panel', t0: 5, t1: 9, d0: 0, d1: 0},             // Aufzug: der unterste Knopf ist abgeklebt – „NICHT DRÜCKEN“
  {id: 'shallow', t0: 9, t1: 15, d0: 0, d1: 24},         // Etage −3: Fischschwarm, Sonnenstrahlen, kein Netz mehr. Ein Schatten …
  {id: 'whale', t0: 15, t1: 21, d0: 300, d1: 312},       // Pottwal auf Augenhöhe – er schaut nach unten und flieht
  {id: 'squid', t0: 21, t1: 27, d0: 690, d1: 700},       // Riesenkalmar-Arm an der Scheibe – dann geht das Licht aus
  {id: 'dark', t0: 27, t1: 33.5, d0: 1450, d1: 1462},    // Stockdunkel, Leuchten – ein Licht kommt näher: Anglerfisch (in echt winzig)
  {id: 'vent', t0: 33.5, t1: 39.5, d0: 2790, d1: 2800},  // Schwarze Raucher: bis zu rund 400 °C – und es kocht nicht
  {id: 'crack', t0: 39.5, t1: 46.5, d0: 6000, d1: 6012}, // 600 bar – die Scheibe knackt
  {id: 'snail', t0: 46.5, t1: 51, d0: 8326, d1: 8336},   // Der tiefste je gefilmte Fisch. Danach: keiner mehr
  {id: 'bottom', t0: 51, t1: 60, d0: 10880, d1: 10920},  // Ganz unten. Es klopft. Ein Tauchboot bringt die Pizza
];

// Wichtige Momente
export const PRESS = 7.9, START = 9.0, NO_NET = 11.4, SHADOW = 13.2, WHALE_FLEE = 18.6, LIGHTS_OUT = 26.3,
  LURE = 29.2, LIGHTS_ON = 31.8, CRACK = 42.0, ARRIVE = 52.0, KNOCK = 53.3, SUB = 54.4, BOX = 55.5, DELIVERED = 56.2;

export function depthAt(T, shot) {
  if (shot.id === 'bottom') return Math.min(shot.d1, shot.d0 + (shot.d1 - shot.d0) * Math.min(1, (T - shot.t0) / (ARRIVE - shot.t0)));
  if (shot.id === 'shallow') { const k = Math.max(0, (T - START) / (shot.t1 - START)); return shot.d0 + (shot.d1 - shot.d0) * Math.pow(k, 1.3); }
  const k = (T - shot.t0) / (shot.t1 - shot.t0);
  return shot.d0 + (shot.d1 - shot.d0) * k;
}
// Sinkgeschwindigkeit (m/s, für Schwebeteilchen)
export function speedAt(T, shot) {
  if (shot.id === 'surface' || shot.id === 'panel') return 0;
  if (shot.id === 'bottom') return T < ARRIVE ? 6 * (1 - Math.pow((T - shot.t0) / (ARRIVE - shot.t0), 2)) : 0;
  if (shot.id === 'shallow') return T < START ? 0 : 4;
  return (shot.d1 - shot.d0) / (shot.t1 - shot.t0);
}
export const floorOf = d => Math.round(d / FLOOR_H);
// Druck in bar (Meerwasser, grob 0,1 bar pro Meter + 1 bar Luft); am Grund rund 1.086 bar
export const pressure = d => 1 + d * 0.0993;
// Temperatur im westlichen Pazifik (grob): warm oben, ab 1.000 m nur noch wenige Grad, am Grund rund 2,5 °C
const TK = [[0, 28], [50, 27], [150, 22], [300, 13], [500, 8], [700, 6], [1000, 4.5], [1500, 3], [2800, 1.8], [4000, 1.5], [6000, 1.6], [8300, 2.1], [10920, 2.5]];
export function tempAt(d) {
  for (let i = 1; i < TK.length; i++) if (d <= TK[i][0]) { const [a, va] = TK[i - 1], [b, vb] = TK[i]; return va + (vb - va) * (d - a) / (b - a); }
  return 2.5;
}
// Sonnenlicht in Prozent (bei rund 200 m noch etwa 1 %, ab ~1.000 m praktisch nichts)
export const lightAt = d => 100 * Math.exp(-d * 0.023);

export const ZONES = [[0, 'LICHTZONE'], [200, 'DÄMMERZONE'], [1000, 'MITTERNACHTSZONE'], [4000, 'ABGRUND'], [6000, 'TIEFSEEGRABEN']];

export const CAPTIONS = [
  [0.15, 2.3, 'Du wohnst in einem Hochhaus mitten im Meer.'],
  [2.45, 4.85, 'Nur geht es nicht hoch. Sondern runter.'],
  [5.15, 7.1, '3.640 Etagen. Den untersten Knopf hat noch nie jemand gedrückt.'],
  [7.25, 8.85, 'Bis heute.'],
  [9.3, 11.1, 'Gleich unter der Oberfläche: Fische vorm Fenster.'],
  [11.5, 13.0, 'Und kein Netz mehr. Funk kommt durch Meerwasser kaum durch.'],
  [13.35, 14.85, 'Moment. Was war das für ein Schatten?'],
  [15.3, 17.6, 'Ein Pottwal. Er taucht bis über 2.000 Meter tief.'],
  [17.8, 20.8, 'Dann schaut er nach unten. Und haut ab.'],
  [21.3, 23.4, '700 Meter. Hier kommt kaum noch Sonnenlicht an.'],
  [23.6, 25.9, 'Riesenkalmare haben Augen so groß wie ein Teller.'],
  [26.4, 26.95, 'Und dann …'],
  [27.3, 29.0, 'Ab 1.000 Metern ist es für immer dunkel.'],
  [29.2, 31.5, 'Fast alles hier unten leuchtet selbst. Auch das da.'],
  [31.9, 33.35, 'Ein Anglerfisch. In echt nur so groß wie eine Hand.'],
  [33.8, 35.9, '2.800 Meter. Schwarze Raucher.'],
  [36.1, 39.3, 'Hier schießt bis zu 400 °C heißes Wasser raus. Es kocht nicht – der Druck ist zu hoch.'],
  [39.8, 41.8, '6.000 Meter. Auf jedem Zentimeter Glas drücken rund 600 Kilo.'],
  [42.3, 43.6, 'Knack.'],
  [43.9, 46.3, 'Die Scheibe hält. Gerade so.'],
  [46.8, 48.9, '8.336 Meter. Der tiefste Fisch, den je jemand gefilmt hat.'],
  [49.1, 50.85, 'Ab hier gibt es keine Fische mehr.'],
  [51.3, 53.0, 'Etage −3.640. Ganz unten. Totenstille.'],
  [53.4, 54.6, 'Dann klopft es.'],
  [55.9, 57.5, 'Deine Pizza. Die Bestellung ist doch noch rausgegangen.'],
  [57.65, 59.4, 'Lieferzeit: 4 Stunden. Kalt.'],
];
