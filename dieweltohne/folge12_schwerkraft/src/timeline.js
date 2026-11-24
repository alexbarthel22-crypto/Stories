// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden ist die Schwerkraft weg. Alles, was sich gerade bewegt, fliegt einfach weiter.
// Als sie zurückkommt, fällt alles gleichzeitig herunter – und die Erde selbst fällt in sich zusammen.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},         // Mensa, Spaghetti-Tag
  {id: 'wait', t0: 3.5, t1: 10},         // Er will gerade die Riesengabel in den Mund schieben
  {id: 'mensa', t0: 10, t1: 17},         // Stufe 1: Spaghetti, Soße, Tabletts und Leute schweben
  {id: 'gym', t0: 17, t1: 24},           // Stufe 2: Sportunterricht – sein erster Dunk hört nicht auf
  {id: 'pool', t0: 24, t1: 31},          // Stufe 3: Freibad – Arschbombe vom Zehner, er kommt nie unten an
  {id: 'bus', t0: 31, t1: 39},           // Stufe 4: Schulbus über eine Bodenwelle auf der Brücke – er hebt ab
  {id: 'orbit', t0: 39, t1: 47},         // Stufe 5: Die Erde fliegt geradeaus aus ihrer Bahn, die Luft löst sich
  {id: 'core', t0: 47, t1: 55},          // Stufe 6: Im Erdinneren hält nichts mehr den Druck zusammen
  {id: 'drop_bus', t0: 55, t1: 58},      // Stufe 7: Schwerkraft zurück – der Bus fällt in den Fluss
  {id: 'drop_gym', t0: 58, t1: 61},      // Stufe 7: er fällt von der Hallendecke
  {id: 'drop_pool', t0: 61, t1: 64},     // Stufe 7: er landet im Planschbecken
  {id: 'quake', t0: 64, t1: 72},         // Stufe 7: Die Erdkruste kracht zurück – die ganze Erde bebt
  {id: 'city', t0: 72, t1: 80},          // Stufe 7: An der Brücke: Risse, Rauch, roter Himmel
  {id: 'final', t0: 80, t1: 90},         // Stufe 7: Zurück in der Mensa – nur der Pudding hat überlebt
];

export const VANISH = 10.0;   // Schwerkraft weg
export const RETURN = 55.0;   // Schwerkraft zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

const WK = [[10, 10], [17, 9.0], [24, 7.8], [31, 6.4], [39, 4.6], [47, 2.4], [55, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}
// Wichtige Momente (Videozeit) für Bild und Ton
export const SAUCE_HIT = 14.3, JUMP = 17.9, BONK = 20.3, BOMB = 25.2, BUMP = 32.4,
  BUS_SPLASH = 56.2, GYM_LAND = 59.4, POOL_LAND = 62.6, CRASH = 64.6, CRACK = 73.4, PUD = 86.2;

export const STAGES = ['HARMLOS', 'PEINLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {mensa: 1, gym: 2, pool: 3, bus: 4, orbit: 5, core: 6, drop_bus: 7, drop_gym: 7, drop_pool: 7, quake: 7, city: 7, final: 7};

export const CAPTIONS = [
  [4.0, 6.6, 'Mittagspause. Spaghetti-Tag.'],
  [6.8, 9.8, 'Er hat die größte Gabel seines Lebens gedreht.'],
  [10.3, 12.6, 'Ohne Schwerkraft fällt nichts mehr runter.'],
  [12.8, 14.1, 'Auch keine Soße.'],
  [14.5, 16.8, 'Jede Bewegung schickt alles einfach weiter.'],
  [17.4, 19.8, 'Sport. Sein erster Dunk überhaupt.'],
  [20.0, 23.8, 'Er hört nicht mehr auf zu steigen. Die ganze Klasse filmt.'],
  [24.4, 27.0, 'Freibad. Arschbombe vom Zehner.'],
  [27.2, 30.8, 'Nur: Das Becken ist leer. Das Wasser schwebt längst in der Luft.'],
  [31.4, 34.6, 'Schulbus. Eine kleine Bodenwelle auf der Brücke.'],
  [34.8, 38.8, 'Das war kein Hüpfer. Das war ein Start.'],
  [39.4, 42.8, 'Die Erde rast mit rund 30 Kilometern pro Sekunde um die Sonne.'],
  [43.0, 46.8, 'Ohne Schwerkraft geht es geradeaus. Und die Luft hält nichts mehr fest.'],
  [47.4, 50.8, 'Im Erdkern herrscht ein Druck von rund 3,5 Millionen bar.'],
  [51.0, 54.6, 'Gedankenexperiment: Ohne Schwerkraft hält ihn nichts mehr zusammen.'],
  [55.3, 57.8, 'Die Schwerkraft ist zurück.'],
  [58.2, 60.8, 'Alles, was schwebt, kommt runter.'],
  [61.2, 63.8, 'Gleichzeitig.'],
  [64.8, 68.2, 'Auch die Erdkruste, die sich angehoben hat.'],
  [68.4, 71.8, 'Die ganze Erde bebt auf einmal.'],
  [72.4, 75.8, 'Überall reißt der Boden auf.'],
  [76.0, 79.6, 'Zehn Sekunden ohne Schwerkraft.'],
  [80.6, 84.2, 'Die Mensa. Alles ist runtergekommen.'],
  [84.4, 86.0, 'Fast alles.'],
  [86.8, 89.0, 'Die Welt ist kaputt. Aber sein Pudding hat überlebt.'],
];
