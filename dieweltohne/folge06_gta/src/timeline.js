// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Einen Tag nach dem Launch verschwindet GTA 6 für 10 Sekunden von jeder Konsole, jeder Disc, jedem Server und jedem Stream.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},        // Über die Schulter: Verfolgungsjagd auf dem Fernseher
  {id: 'wait', t0: 3.5, t1: 10},        // Wohnzimmer bei Nacht, Countdown läuft
  {id: 'couch', t0: 10, t1: 17},        // Stufe 1: Spiel weg, Spielstand weg, Controller fliegt
  {id: 'stream', t0: 17, t1: 24},       // Stufe 2: Handy im Bett, Livestream mit 2 Mio. Zuschauern wird schwarz
  {id: 'store', t0: 24, t1: 31},        // Stufe 3: Elektromarkt, Discs leer, die Schlange stürmt den Tresen
  {id: 'server', t0: 31, t1: 39},       // Stufe 4: Rechenzentrum überhitzt, Brand, Löschgas
  {id: 'square', t0: 39, t1: 48},       // Stufe 5: Launch-Party, Riesenleinwand stürzt, Massenpanik
  {id: 'streets', t0: 48, t1: 58},      // Stufe 6: Millionen Gamer strömen gleichzeitig auf die Straßen
  {id: 'return', t0: 58, t1: 66},       // Stufe 7: GTA 6 zurück – alle laden gleichzeitig neu, das Netz bricht zusammen
  {id: 'dawn', t0: 66, t1: 80},         // Stufe 7: Sonnenaufgang, die ganze Stadt ist draußen
  {id: 'end', t0: 80, t1: 90},          // Stufe 7: Morgens im Wohnzimmer: Download 1 %
];

export const VANISH = 10.0;   // GTA 6 verschwindet
export const RETURN = 58.0;   // GTA 6 zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

const WK = [[10, 10], [17, 9.3], [24, 8.4], [31, 7.4], [39, 6.0], [48, 4.0], [58, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}
// Wichtige Momente (Videozeit) für Bild und Ton
export const THROW = 13.6, STREAM_BLACK = 18.6, RUSH = 27.4, SHELF_FALL = 28.6, OVERHEAT = 33.8, FIRE = 35.6, GAS = 37.2,
  WALL_BLACK = 40.6, WALL_FALL = 43.4, NET_DOWN = 61.5, SUNRISE = 66.0;

export const STAGES = ['HARMLOS', 'ÄRGERLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {couch: 1, stream: 2, store: 3, server: 4, square: 5, streets: 6, return: 7, dawn: 7, end: 7};

export const CAPTIONS = [
  [4.0, 6.8, 'GTA 6 ist seit gestern draußen.'],
  [7.0, 9.8, 'Geschätzt 24,5 Millionen Kopien bis zum Launchtag.'],
  [10.5, 13.3, 'Und plötzlich: weg. Von jeder Konsole der Welt.'],
  [13.5, 16.8, 'Der Spielstand auch. Die ganze Nacht durchgezockt.'],
  [17.4, 20.4, 'Gerade schauen Millionen Menschen GTA-Livestreams.'],
  [20.6, 23.8, 'Mitten im Stream: schwarzer Bildschirm.'],
  [24.4, 27.4, 'Im Laden ist jede Disc plötzlich leer.'],
  [27.6, 30.8, 'Und die Schlange wartet seit Stunden.'],
  [31.4, 34.6, 'Jede Konsole fragt gleichzeitig die Server: Wo ist mein Spiel?'],
  [34.8, 38.8, 'Kein Rechenzentrum ist für so einen Ansturm gebaut.'],
  [39.4, 42.6, 'Launch-Party in der Innenstadt. 40.000 Fans.'],
  [42.8, 45.2, 'Auf der Riesenleinwand: nur noch ein Fehler. Alle drängen nach vorn.'],
  [45.4, 47.8, 'Dann reißt die Halterung.'],
  [48.4, 51.8, 'Millionen Gamer stehen gleichzeitig auf.'],
  [52.0, 57.8, 'Und gehen zum ersten Mal seit dem Launch vor die Tür.'],
  [58.4, 61.2, 'GTA 6 ist zurück.'],
  [61.4, 65.8, 'Aber jetzt laden alle gleichzeitig neu. Das Netz bricht zusammen.'],
  [66.4, 69.8, 'Der Download dauert Stunden.'],
  [70.0, 73.8, 'Also bleiben alle draußen. Die ganze Nacht.'],
  [74.0, 79.8, 'Für Gamer ist das der Weltuntergang.'],
  [80.4, 84.2, 'Zehn Sekunden ohne GTA 6.'],
  [84.4, 88.6, 'Und die ganze Welt musste raus.'],
];
