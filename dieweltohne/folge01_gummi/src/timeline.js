// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: von harmlos bis Weltuntergang, Stufe für Stufe schlimmer.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 4.2},          // POV Handy im Regen
  {id: 'balloons', t0: 4.2, t1: 10},      // Stufe 1: Luftballons, Haargummi
  {id: 'gummy', t0: 10, t1: 14.5},        // Stufe 1: Gummibärchen bleiben
  {id: 'pants', t0: 14.5, t1: 20},        // Stufe 2: Hosen rutschen
  {id: 'soles', t0: 20, t1: 26.5},        // Stufe 3: Ausrutschen
  {id: 'phone', t0: 26.5, t1: 32.5},      // Stufe 4: Handy läuft voll
  {id: 'cars_wide', t0: 32.5, t1: 36.5},  // Stufe 5: Autos auf Felgen
  {id: 'cars_wheel', t0: 36.5, t1: 38.5},
  {id: 'cars_crash', t0: 38.5, t1: 41.5},
  {id: 'kitchen', t0: 41.5, t1: 47},      // Stufe 5: Wasserrohre
  {id: 'gas', t0: 47, t1: 54},            // Stufe 6: Gas + Funken = Explosion
  {id: 'plane', t0: 54, t1: 61},          // Stufe 6: Flugzeug, Fahrwerk bricht
  {id: 'rocket', t0: 61, t1: 66.5},       // Stufe 7: Rakete explodiert
  {id: 'globe', t0: 66.5, t1: 70},        // Stufe 7: die Welt brennt
  {id: 'back', t0: 70, t1: 78},           // Gummi zurück, Straße brennt
  {id: 'later', t0: 78, t1: 85},          // 5 Minuten später, Luftbild bei Nacht
  {id: 'end', t0: 85, t1: 90},
];

export const VANISH = 5.0, RETURN = 70.0;

const WK = [[5, 10], [10, 9.3], [14.5, 8.8], [20, 8.2], [26.5, 7.5], [32.5, 6.8], [41.5, 5.6], [47, 4.8], [54, 3.6], [61, 2.4], [66.5, 1.2], [70, 0]];
export const WORLD_KEYS = WK;
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}

export const STAGES = ['HARMLOS', 'PEINLICH', 'SCHMERZHAFT', 'TEUER', 'GEFÄHRLICH', 'TÖDLICH', 'WELTUNTERGANG'];
export const STAGE_OF = {balloons: 1, gummy: 1, pants: 2, soles: 3, phone: 4, cars_wide: 5, cars_wheel: 5, cars_crash: 5, kitchen: 5, gas: 6, plane: 6, rocket: 7, globe: 7, back: 7, later: 7};

export const CAPTIONS = [
  [5.4, 7.5, 'Luftballons sind aus Naturkautschuk. Weg.'],
  [7.7, 9.9, 'Haargummis auch. Noch ist alles harmlos.'],
  [10.3, 12.3, 'Gummibärchen? Bleiben.'],
  [12.4, 14.4, 'Die sind aus Gelatine.'],
  [14.9, 17.2, 'Jeder Gummizug in jeder Hose.'],
  [17.4, 19.9, 'Peinlich. Aber das ist erst der Anfang.'],
  [20.4, 23.2, 'Fast jede Schuhsohle ist aus Gummi.'],
  [23.4, 26.4, 'Auf nassem Boden hält jetzt nichts mehr.'],
  [26.9, 29.4, 'Die Silikonhülle: weg.'],
  [29.6, 32.4, 'Und jede Dichtung im Inneren. Wasser läuft hinein.'],
  [32.9, 36.4, 'Ein Autoreifen ist vor allem eins: Gummi.'],
  [36.6, 38.4, 'Übrig bleiben die Stahldrähte.'],
  [38.6, 41.4, 'Bremsen? Bringt nichts mehr.'],
  [41.9, 44.4, 'Jede Dichtung in jeder Wasserleitung.'],
  [44.6, 46.9, 'Alle gleichzeitig.'],
  [47.4, 50.2, 'Auch Gasleitungen sind mit Gummiringen abgedichtet.'],
  [50.4, 53.9, 'Und auf der Straße fliegen Funken.'],
  [54.4, 57.4, 'Genau jetzt setzt ein Flugzeug auf.'],
  [57.6, 60.9, 'Ohne Reifen bricht das Fahrwerk.'],
  [61.4, 63.9, '1986 zerstörte ein einziger Gummiring die Challenger.'],
  [64.0, 66.4, 'Jetzt versagen alle auf einmal.'],
  [66.8, 69.9, 'Überall auf der Welt. Gleichzeitig.'],
  [70.6, 73.8, 'Der Gummi ist zurück.'],
  [74.0, 77.8, 'Aber die Welt brennt.'],
  [78.4, 81.4, 'Fünf Minuten später: Jede Straße ist blockiert.'],
  [81.6, 84.8, 'Kein Krankenwagen kommt durch. Alle stehen auf Felgen.'],
];
