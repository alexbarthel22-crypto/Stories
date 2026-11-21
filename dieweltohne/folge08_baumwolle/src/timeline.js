// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden verschwindet jede Baumwollfaser der Welt – Kleidung, Geldscheine, Topflappen, Verbandsmull.
// Als sie zurückkommt, ist sie kein Stoff mehr, sondern lose Fasern überall – und lose Baumwolle brennt wie Zunder.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},          // Handy filmt den Kumpel im Skatepark
  {id: 'wait', t0: 3.5, t1: 10},          // Skatepark, Countdown läuft
  {id: 'skate', t0: 10, t1: 17},          // Stufe 1: Jeans und Hoodie weg – mitten im Sprung
  {id: 'cash', t0: 17, t1: 24},           // Stufe 2: Imbiss – der Zwanziger verschwindet beim Bezahlen
  {id: 'kitchen', t0: 24, t1: 31},        // Stufe 3: Topflappen weg – Fritteuse kippt, Fettbrand
  {id: 'vault', t0: 31, t1: 39},          // Stufe 4: Tresor der Zentralbank – Milliarden in Scheinen weg
  {id: 'surgery', t0: 39, t1: 47},        // Stufe 5: Operationssaal – Kompressen und Verbände weg
  {id: 'street_return', t0: 47, t1: 58},  // Stufe 6: Baumwolle zurück – als lose Fasern, die Straße wird weiß
  {id: 'street_fire', t0: 58, t1: 68},    // Stufe 7: Das Feuer aus dem Imbiss erreicht die Fasern
  {id: 'aerial', t0: 68, t1: 80},         // Stufe 7: Luftbild – die Stadt brennt
  {id: 'final', t0: 80, t1: 90},          // Stufe 7: Skatepark, Rauch über der Stadt
];

export const VANISH = 10.0;   // Baumwolle verschwindet
export const RETURN = 50.0;   // Baumwolle zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

const WK = [[10, 10], [17, 9.0], [24, 7.8], [31, 6.4], [39, 4.6], [47, 1.6], [50, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}
// Wichtige Momente (Videozeit) für Bild und Ton
export const NOTE_GONE = 18.6, MITT_GONE = 25.6, POT_DROP = 26.0, FLARE = 26.35, VAULT_ALARM = 31.8, MONITOR_ALARM = 41.5, IGNITE = 59.5;

export const STAGES = ['HARMLOS', 'ÄRGERLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {skate: 1, cash: 2, kitchen: 3, vault: 4, surgery: 5, street_return: 6, street_fire: 7, aerial: 7, final: 7};

export const CAPTIONS = [
  [4.0, 6.8, 'Baumwolle steckt in fast allem, was du anhast.'],
  [7.0, 9.8, 'Was, wenn sie für zehn Sekunden verschwindet?'],
  [10.5, 13.4, 'Jeans: Baumwolle. Hoodie: Baumwolle.'],
  [13.6, 16.8, 'Zum Glück sind seine Boxershorts aus Polyester.'],
  [17.4, 20.4, 'Euro-Scheine sind aus Baumwollpapier.'],
  [20.6, 23.8, 'Bezahlen? Gerade schwierig.'],
  [24.4, 27.4, 'Topflappen, Schürze, Geschirrtuch: Baumwolle.'],
  [27.6, 30.8, 'Und heißes Fett trifft auf die Gasflamme.'],
  [31.4, 34.6, 'Rund 30 Milliarden Euro-Scheine sind im Umlauf.'],
  [34.8, 38.8, 'Dollarscheine: 75 Prozent Baumwolle. Alles weg.'],
  [39.4, 42.6, 'Jedes Jahr gibt es über 300 Millionen Operationen.'],
  [42.8, 46.8, 'Kompressen, Tupfer, Verbände: aus Baumwolle.'],
  [47.4, 49.8, 'Gleich ist es vorbei.'],
  [50.4, 53.4, 'Die Baumwolle ist zurück.'],
  [53.6, 57.6, 'Aber nicht als Stoff. Als lose Fasern. Überall.'],
  [58.4, 61.8, 'Und in der Imbissküche brennt es noch.'],
  [62.0, 67.6, 'Lose Baumwolle brennt wie Zunder.'],
  [68.4, 72.0, 'Jede Stadt der Welt ist jetzt voller Baumwolle.'],
  [72.2, 75.8, 'Rund 25 Millionen Tonnen werden jedes Jahr geerntet.'],
  [76.0, 79.8, 'Ein Funke reicht.'],
  [80.4, 84.2, 'Zehn Sekunden ohne Baumwolle.'],
  [84.4, 88.6, 'Und die Welt steht in Flammen.'],
];
