// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden verschwindet jedes Gramm Gold der Welt – Ketten, Medaillen, Visiere und die hauchdünnen Golddrähte in Chips.
// Als es zurückkommt, landet es nicht dort, wo es war, sondern als ein einziger Würfel mitten in der Stadt (Gedankenexperiment).
// Die Chips bleiben ohne Gold: Nichts Elektronisches funktioniert mehr.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},          // Handy filmt den Rapper auf dem Parkdeck
  {id: 'wait', t0: 3.5, t1: 10},          // Musikvideo-Dreh, Countdown läuft
  {id: 'rap', t0: 10, t1: 17},            // Stufe 1: Kette, Grillz und Ringe weg
  {id: 'podium', t0: 17, t1: 24},         // Stufe 2: Siegerehrung – die Goldmedaille wird zur Silbermedaille
  {id: 'space', t0: 24, t1: 31},          // Stufe 3: Außeneinsatz im All – das Goldvisier ist weg, die Sonne blendet
  {id: 'coaster', t0: 31, t1: 39},        // Stufe 4: Achterbahn – Steuerung tot, der Zug hängt über der Kante
  {id: 'ship', t0: 39, t1: 48},           // Stufe 5: Containerschiff ohne Strom treibt in eine Brücke
  {id: 'cube_drop', t0: 48, t1: 58},      // Stufe 6: Gold zurück – als Würfel mitten in der Stadt
  {id: 'cube_night', t0: 58, t1: 68},     // Stufe 7: Nacht, kein Strom, alle laufen zum Würfel
  {id: 'aerial', t0: 68, t1: 80},         // Stufe 7: Luftbild – dunkle Stadt, Menschenströme, Feuer
  {id: 'final', t0: 80, t1: 90},          // Stufe 7: Totes Handy in der Hand, der Würfel im Hintergrund
];

export const VANISH = 10.0;   // Gold verschwindet
export const RETURN = 48.0;   // Gold zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

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
export const MEDAL_GONE = 18.4, VISOR_GONE = 25.0, GLARE = 26.0, CHIP_DEAD = 33.0, BRAKE = 33.3, BLACKOUT = 40.4, SHIP_HIT = 45.0, SPAN_FALL = 45.6, CUBE_LAND = 49.4;

export const STAGES = ['HARMLOS', 'PEINLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {rap: 1, podium: 2, space: 3, coaster: 4, ship: 5, cube_drop: 6, cube_night: 7, aerial: 7, final: 7};

export const CAPTIONS = [
  [4.0, 6.8, 'Gold glänzt an Ketten, Ringen und Zähnen.'],
  [7.0, 9.8, 'Was, wenn es für zehn Sekunden verschwindet?'],
  [10.5, 13.4, 'Kette weg. Grillz weg. Ringe weg.'],
  [13.6, 16.8, 'Das Musikvideo kann er vergessen.'],
  [17.4, 20.4, 'Eine Goldmedaille besteht fast nur aus Silber.'],
  [20.6, 23.8, 'Nur etwa sechs Gramm sind echtes Gold.'],
  [24.4, 27.4, 'Astronauten-Visiere sind mit Gold beschichtet.'],
  [27.6, 30.8, 'Ohne Gold trifft ihn das volle Sonnenlicht.'],
  [31.4, 34.6, 'In vielen Chips stecken hauchdünne Golddrähte.'],
  [34.8, 38.8, 'Die Steuerung fällt aus. Der Zug stoppt. In 60 Metern Höhe.'],
  [39.4, 42.6, 'Auch ein Containerschiff steuert mit Elektronik.'],
  [42.8, 47.6, '2024 rammte in Baltimore ein Frachter nach einem Stromausfall eine Brücke.'],
  [48.4, 51.2, 'Das Gold ist zurück.'],
  [51.4, 54.4, 'Aber nicht da, wo es war.'],
  [54.6, 57.8, 'Alles Gold, das je gefördert wurde: ein Würfel, 22 Meter breit.'],
  [58.4, 62.2, 'In keinem Chip steckt mehr Gold. Nichts geht mehr an.'],
  [62.4, 67.6, 'Kein Licht. Kein Handy. Kein Netz.'],
  [68.4, 72.0, 'Rund 220.000 Tonnen. Über 20 Billionen Euro wert.'],
  [72.2, 75.8, 'Und jeder Mensch weiß, wo es liegt.'],
  [76.0, 79.8, 'Die ganze Welt ist auf dem Weg hierher.'],
  [80.4, 84.2, 'Zehn Sekunden ohne Gold.'],
  [84.4, 88.6, 'Und die Welt dreht sich nur noch um einen Würfel.'],
];
