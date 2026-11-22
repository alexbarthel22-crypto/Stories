// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden verschwindet jedes Stück Fleisch der Welt – auf Grills, Tellern, in Frachtflugzeugen und Zoo-Eimern.
// Lebende Tiere und Menschen sind nicht betroffen. Die Zoo-Löwen sind hungrig, brechen aus – und als das Fleisch zurück ist,
// riechen sie jeden Grill der Stadt.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},          // Handy filmt Papa am Grill
  {id: 'wait', t0: 3.5, t1: 10},          // Grillfest im Garten, Countdown läuft
  {id: 'bbq', t0: 10, t1: 17},            // Stufe 1: Würstchen und Steaks verschwinden vom Grill
  {id: 'date', t0: 17, t1: 24},           // Stufe 2: Erstes Date – unter der Glocke ist der Teller leer
  {id: 'cargo', t0: 24, t1: 31},          // Stufe 3: Frachtjet ohne Fracht – Schwerpunkt verrutscht beim Start
  {id: 'zoo', t0: 31, t1: 39},            // Stufe 4: Fütterung im Zoo – Eimer leer, Löwen werfen sich gegen das Gitter
  {id: 'street', t0: 39, t1: 48},         // Stufe 5: Löwen in der Innenstadt
  {id: 'suburb', t0: 48, t1: 58},         // Stufe 6: Fleisch zurück – auf jedem Grill, die Löwen folgen dem Geruch
  {id: 'back', t0: 58, t1: 68},           // Stufe 7: Papa grillt wieder – ein Löwe am Gartenzaun
  {id: 'lion', t0: 68, t1: 80},           // Stufe 7: Der Löwe springt über den Zaun, alle flüchten ins Haus
  {id: 'final', t0: 80, t1: 90},          // Stufe 7: Blick durch die Terrassentür – der Löwe frisst die Würstchen
];

export const VANISH = 10.0;   // Fleisch verschwindet
export const RETURN = 48.0;   // Fleisch zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

const WK = [[10, 10], [17, 9.0], [24, 7.8], [31, 6.4], [39, 4.6], [48, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}
// Wichtige Momente (Videozeit) für Bild und Ton
export const CLOCHE = 19.2, ROTATE = 25.6, TAILSTRIKE = 26.3, STALL = 28.0, BUCKET = 32.2, FENCE_HIT = 35.4, FENCE_BREAK = 37.4,
  LION_JUMP = 70.2, DOOR_SLAM = 73.8;

export const STAGES = ['HARMLOS', 'PEINLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {bbq: 1, date: 2, cargo: 3, zoo: 4, street: 5, suburb: 6, back: 7, lion: 7, final: 7};

export const CAPTIONS = [
  [4.0, 6.8, 'Samstag, Grillfest. Alles ist perfekt.'],
  [7.0, 9.8, 'Bis jedes Stück Fleisch der Welt verschwindet.'],
  [10.5, 13.4, 'Würstchen weg. Steaks weg. Alles weg.'],
  [13.6, 16.8, 'Der Hund versteht die Welt nicht mehr.'],
  [17.4, 20.4, 'Erstes Date. Er hat das teuerste Steak bestellt.'],
  [20.6, 23.8, 'Der Kellner ist genauso überrascht.'],
  [24.4, 27.4, 'Ein Frachtjet voller Kühlfleisch beim Start.'],
  [27.6, 30.8, 'Fracht weg, Schwerpunkt verschoben. Die Nase schießt hoch.'],
  [31.4, 34.6, 'Fütterungszeit im Zoo. Der Eimer ist leer.'],
  [34.8, 38.8, 'Ein Löwe bekommt im Zoo drei bis fünf Kilo Fleisch am Tag.'],
  [39.4, 42.6, 'Der Zoo liegt mitten in der Stadt.'],
  [42.8, 47.6, 'Und die Löwen haben Hunger.'],
  [48.4, 51.2, 'Das Fleisch ist zurück.'],
  [51.4, 54.4, 'Auf jedem Grill der Stadt.'],
  [54.6, 57.8, 'Und Löwen haben eine sehr gute Nase.'],
  [58.4, 62.2, 'In Deutschland isst jeder im Schnitt 53 Kilo Fleisch im Jahr.'],
  [62.4, 67.6, 'Papa hätte gern wenigstens eine Wurst davon.'],
  [68.4, 72.0, 'Weltweit sind es rund 375 Millionen Tonnen pro Jahr.'],
  [72.2, 75.8, 'Aber dieser Grill gehört jetzt jemand anderem.'],
  [76.0, 79.8, 'Und der teilt nicht.'],
  [80.4, 84.2, 'Zehn Sekunden ohne Fleisch.'],
  [84.4, 88.6, 'Weltuntergang? Für Papa schon.'],
];
