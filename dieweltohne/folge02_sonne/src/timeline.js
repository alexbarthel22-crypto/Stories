// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Die Sonne verschwindet, aber ihr Licht ist noch 8:20 unterwegs. Dann 10 Sekunden Nacht – und die Folgen eskalieren.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},           // Strand, Mittag, Handy in der Hand
  {id: 'space', t0: 3.5, t1: 11.5},        // Sonne verschwindet, letztes Licht fliegt zur Erde
  {id: 'wait', t0: 11.5, t1: 18},        // Strand: niemand ahnt etwas, Countdown läuft ab
  {id: 'beach_dark', t0: 18, t1: 24},    // Stufe 1: plötzlich Nacht, Sterne am Mittag
  {id: 'street_dark', t0: 24, t1: 31},   // Stufe 2: Stadt erstarrt
  {id: 'autobahn', t0: 31, t1: 39},      // Stufe 3: Autobahn im Dunkeln, Massenkarambolage
  {id: 'solar', t0: 39, t1: 45.5},       // Stufe 4: Solarstrom fällt auf null
  {id: 'grid', t0: 45.5, t1: 52},        // Stufe 5: Netz bricht zusammen
  {id: 'europe', t0: 52, t1: 58},        // Stufe 5: Europa geht vom Netz
  {id: 'back', t0: 58, t1: 66},          // Stufe 6: Sonne zurück, Strom nicht
  {id: 'night', t0: 66, t1: 78},         // Stufe 7: Abends, Europa im Dunkeln
  {id: 'aerial', t0: 78, t1: 90},        // Stufe 7: Luftbild der dunklen Stadt
];

export const VANISH = 5.0;   // Sonne verschwindet (im All)
export const DARK = 18.0;    // ihr letztes Licht hat die Erde erreicht
export const RETURN = 59.0;  // Licht der zurückgekehrten Sonne kommt an

// 8:20 Lichtlaufzeit, im Zeitraffer bis 3 s vor DARK, dann echtzeit
export function lightLeft(T) {
  if (T <= VANISH) return 500;
  if (T >= DARK) return 0;
  const a = VANISH, b = DARK - 3;
  if (T < b) { const u = (T - a) / (b - a); return 3 + 497 * Math.pow(1 - u, 2.2); }
  return DARK - T;
}

// Weltzeit der 10 Sekunden Dunkelheit, über die Einstellungen gedehnt
const WK = [[18, 10], [24, 9.3], [31, 8.4], [39, 7.0], [45.5, 5.6], [52, 3.6], [58, 0.8], [59, 0]];
export const WORLD_KEYS = WK;
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}

export const STAGES = ['SELTSAM', 'UNHEIMLICH', 'GEFÄHRLICH', 'KRITISCH', 'BLACKOUT', 'KATASTROPHE', 'ZUSAMMENBRUCH'];
export const STAGE_OF = {beach_dark: 1, street_dark: 2, autobahn: 3, solar: 4, grid: 5, europe: 5, back: 6, night: 7, aerial: 7};

export const CAPTIONS = [
  [5.4, 7.6, 'Die Sonne ist weg. Einfach so.'],
  [7.8, 11.3, 'Doch ihr letztes Licht ist noch 8 Minuten und 20 Sekunden zu uns unterwegs.'],
  [11.8, 14.6, 'Hier unten ahnt niemand etwas.'],
  [14.8, 17.7, 'Sie sonnen sich im Licht einer Sonne, die es nicht mehr gibt.'],
  [18.5, 20.9, 'Zwölf Uhr mittags. Schlagartig Nacht.'],
  [21.1, 23.9, 'Und am Himmel: Sterne.'],
  [24.4, 27.3, 'In der Stadt erstarrt alles.'],
  [27.5, 30.9, 'Die Laternen bleiben aus. Es ist ja Mittag.'],
  [31.4, 34.5, 'Autobahn. 130 km/h. Kein Licht.'],
  [34.7, 38.9, 'Einer bremst. Die anderen sehen es zu spät.'],
  [39.4, 42.3, 'Mittags kommt rund die Hälfte unseres Stroms von der Sonne.'],
  [42.5, 45.4, 'Jetzt: null. Von einer Sekunde auf die andere.'],
  [45.9, 48.7, 'Das Netz verkraftet den Ausfall von 3 Gigawatt.'],
  [48.9, 51.9, 'Jetzt fehlen Dutzende. Kraftwerke schalten sich ab.'],
  [52.4, 54.9, 'Ein Land nach dem anderen fällt aus.'],
  [55.1, 57.9, '2025 reichten in Spanien Sekunden für einen Blackout.'],
  [59.5, 61.8, 'Die Sonne ist zurück.'],
  [62.0, 65.9, 'Der Strom nicht. Keine Ampel. Kein Zug. Kein Aufzug.'],
  [66.4, 69.6, 'Abends. Ganz Europa liegt im Dunkeln.'],
  [69.8, 73.4, 'Kein Handynetz. Kein Notruf. Keine Kasse.'],
  [73.6, 77.8, 'Ohne Strom laufen keine Pumpen. Bald kommt kein Wasser mehr.'],
  [78.4, 82.2, 'Ein ganzes Stromnetz neu zu starten dauert Tage.'],
  [82.4, 85.6, 'Und alles nur wegen zehn Sekunden.'],
  [85.9, 89.8, 'Zehn Sekunden ohne Sonne. Und Europa steht still.'],
];
