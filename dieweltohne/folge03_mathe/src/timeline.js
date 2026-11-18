// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden rechnet kein Chip der Welt mehr richtig. Die Folgen eskalieren vom Klassenzimmer bis zum Raketenalarm.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},          // Handy-Blick im Klassenzimmer: Taschenrechner 1 + 1 = 2
  {id: 'class_wait', t0: 3.5, t1: 10},    // Mathearbeit, Lehrer an der Tafel, Countdown läuft
  {id: 'class_glitch', t0: 10, t1: 17},   // Stufe 1: Tafel, Uhr und Rechner zeigen Unsinn, Jubel
  {id: 'street', t0: 17, t1: 24},         // Stufe 2: Stadt, alle Bildschirme spielen verrückt
  {id: 'crossing', t0: 24, t1: 31},       // Stufe 3: alle Ampeln grün, Unfall auf der Kreuzung
  {id: 'bank', t0: 31, t1: 38},           // Stufe 4: Kontostand und Börse stürzen ab
  {id: 'plane', t0: 38, t1: 47},          // Stufe 5: Cockpit im Landeanflug, Instrumente fallen aus
  {id: 'grid', t0: 47, t1: 53},           // Stufe 6: Netz bricht zusammen
  {id: 'bunker', t0: 53, t1: 66},         // Stufe 7: Frühwarnsystem meldet Raketenstart
  {id: 'earth', t0: 66, t1: 78},          // Stufe 7: Flugbahnen auf dem Lagebildschirm
  {id: 'decide', t0: 78, t1: 90},         // Stufe 7: Ein Mensch muss entscheiden
];

export const VANISH = 10.0;   // Mathe verschwindet
export const RETURN = 59.0;   // Mathe zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

const WK = [[10, 10], [17, 9.3], [24, 8.5], [31, 7.6], [38, 6.6], [47, 4.6], [53, 2.6], [59, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}
// Glitch-Stärke 0..1: setzt bei VANISH schlagartig ein, endet bei RETURN
export function glitch(T) { return T >= VANISH && T < RETURN ? 1 : 0; }

// Raketenalarm im Bunker (Videozeit) und Entscheidungsfrist
export const ALARM = 56.0;
export const DECIDE_START = 8 * 60; // Sekunden Entscheidungszeit beim Alarm (Countdown ab ALARM)

export const STAGES = ['HARMLOS', 'UNHEIMLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'BLACKOUT', 'WELTUNTERGANG'];
export const STAGE_OF = {class_glitch: 1, street: 2, crossing: 3, bank: 4, plane: 5, grid: 6, bunker: 7, earth: 7, decide: 7};

export const CAPTIONS = [
  [4.0, 6.6, 'Jeder hat es sich schon mal gewünscht: keine Mathe mehr.'],
  [6.8, 9.8, 'Aber jeder Chip der Welt rechnet. Milliarden Mal pro Sekunde.'],
  [10.5, 13.4, 'Erst mal: Jubel. Die Mathearbeit ist gelaufen.'],
  [13.6, 16.9, 'Doch ohne Mathe rechnet auch kein Computer mehr.'],
  [17.4, 20.4, 'Jedes Handy, jede Uhr, jeder Bildschirm: Unsinn.'],
  [20.6, 23.9, 'Und niemand weiß, warum.'],
  [24.4, 27.4, 'Ampeln werden von Computern geschaltet.'],
  [27.6, 30.9, 'Jetzt zeigen alle Grün. In jede Richtung.'],
  [31.4, 34.4, 'Dein Geld ist nur eine Zahl in einem Computer.'],
  [34.6, 37.9, 'Börsencomputer verkaufen alles. In Millisekunden.'],
  [38.4, 41.6, 'Landeanflug. Moderne Flugzeuge fliegen per Computer.'],
  [41.8, 46.8, 'Die Instrumente zeigen Unsinn. Und der Boden kommt näher.'],
  [47.4, 50.3, 'Kraftwerke werden von Computern geregelt.'],
  [50.5, 52.9, 'Ohne sie bricht das Stromnetz zusammen.'],
  [53.4, 55.8, 'Und in einem Bunker rechnet ein Frühwarnsystem.'],
  [56.2, 58.8, 'Es meldet: Raketenstart.'],
  [59.4, 62.2, 'Die Mathe ist zurück.'],
  [62.4, 65.9, 'Aber der Alarm ist schon raus.'],
  [66.4, 70.2, '1983 meldete ein sowjetischer Computer genau das: fünf Atomraketen.'],
  [70.4, 73.9, 'Es war ein Fehler. Ein Offizier glaubte dem Computer nicht.'],
  [74.1, 77.8, 'Hätte er gemeldet, wäre ein Gegenschlag möglich gewesen.'],
  [78.4, 81.8, 'Heute bleiben für diese Entscheidung nur Minuten.'],
  [82.0, 85.4, 'Zehn Sekunden ohne Mathe.'],
  [85.6, 89.8, 'Und ein Mensch muss entscheiden, ob die Welt untergeht.'],
];

// Nur für die übernommene Strandszene (beach.js liefert hier lediglich das Himmelsmaterial)
export const DARK = 999;
export function lightLeft() { return 0; }
