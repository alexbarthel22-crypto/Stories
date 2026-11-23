// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden verschwindet jede Muschel der Welt – samt Schale, Perlen und Perlmutt.
// Als sie zurückkommen, landen sie nicht da, wo sie waren: Erst regnet es Muscheln, dann kommen alle zu dem Typen,
// der sich vorhin im Livestream eine Auster gewünscht hat.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},          // Livestream: Er will Austern essen
  {id: 'wait', t0: 3.5, t1: 10},          // Er hebt die Auster an den Mund, Countdown läuft
  {id: 'slurp', t0: 10, t1: 17},          // Stufe 1: Auster weg – er schlürft Luft, Zitrone ins Auge
  {id: 'prom', t0: 17, t1: 24},           // Stufe 2: Abiball-Foto – Perlmuttknöpfe weg, alle Hemden springen auf
  {id: 'terrace', t0: 24, t1: 31},        // Stufe 3: Kellner mit sechs Muscheltöpfen – Tablett wird leicht, Töpfe fliegen
  {id: 'watt', t0: 31, t1: 39},           // Stufe 4: Wattwanderung – Muschelbank weg, alle versinken im Schlick
  {id: 'church', t0: 39, t1: 48},         // Stufe 5: Kirchturm aus Muschelkalk wird löchrig und kippt
  {id: 'rain', t0: 48, t1: 58},           // Stufe 6: Muscheln zurück – sie regnen vom Himmel
  {id: 'back', t0: 58, t1: 68},           // Stufe 7: Zurück im Stream – es rumpelt, das Fenster birst
  {id: 'fill', t0: 68, t1: 78},           // Stufe 7: Das Zimmer läuft mit Muscheln voll
  {id: 'aerial', t0: 78, t1: 84},         // Stufe 7: Luftbild – ein Muschelberg über der Stadt
  {id: 'final', t0: 84, t1: 90},          // Stufe 7: Oben taucht er auf – mit einer Auster auf dem Kopf
];

export const VANISH = 10.0;   // Muscheln verschwinden
export const RETURN = 48.0;   // Muscheln zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

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
export const LEMON = 12.4, POP = 17.5, FLASH = 19.8, TRAY = 24.9, SINK = 32.0, HOLES = 40.0, TILT = 43.4, TOWER_HIT = 45.2,
  WINDOW = 62.6, BURIED = 75.6, HAND_UP = 84.7, HEAD_UP = 85.7, GULP = 88.0;
// Töpfe auf Köpfen (Videozeit der Einschläge)
export const POT_HITS = [25.75, 26.0, 26.25, 26.55, 26.8, 27.35];

export const STAGES = ['HARMLOS', 'PEINLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {slurp: 1, prom: 2, terrace: 3, watt: 4, church: 5, rain: 6, back: 7, fill: 7, aerial: 7, final: 7};

export const CAPTIONS = [
  [4.0, 6.8, 'Livestream. 40.000 Leute schauen ihm beim Austernessen zu.'],
  [7.0, 9.8, 'Bis jede Muschel der Welt verschwindet.'],
  [10.5, 12.3, 'Er schlürft. Nur Luft.'],
  [12.5, 16.8, 'Dafür trifft ihn die Zitrone. Direkt ins Auge.'],
  [17.4, 20.0, 'Abiball. Gruppenfoto. Alle Hemden haben Perlmuttknöpfe.'],
  [20.2, 23.8, 'Perlmutt kommt aus Muscheln. Das Foto bleibt für immer.'],
  [24.4, 27.0, 'Sechs Töpfe Muscheln auf einem Tablett.'],
  [27.2, 30.8, 'Plötzlich wiegt das Tablett fast nichts mehr.'],
  [31.4, 34.6, 'Wattwanderung. Alle stehen auf einer Muschelbank.'],
  [34.8, 38.8, 'Sie war der einzige feste Boden weit und breit.'],
  [39.4, 42.6, 'In Franken sind viele alte Kirchen aus Muschelkalk gebaut.'],
  [42.8, 47.6, 'Er heißt so, weil er voller Muschelschalen steckt.'],
  [48.4, 51.2, 'Die Muscheln sind zurück.'],
  [51.4, 54.4, 'Aber nicht da, wo sie waren.'],
  [54.6, 57.8, 'Jedes Jahr werden rund 18 Millionen Tonnen Muscheln geerntet.'],
  [58.4, 62.2, 'Und einer hat sich vorhin so sehr eine Auster gewünscht.'],
  [62.4, 67.6, 'Das Universum hat zugehört.'],
  [68.4, 72.0, 'Alle Muscheln der Welt. An eine einzige Adresse.'],
  [72.2, 75.4, 'Der Chat dreht komplett durch.'],
  [75.8, 77.8, 'Und er ist weg.'],
  [78.4, 83.6, 'Die halbe Stadt liegt jetzt unter einem Muschelberg.'],
  [84.4, 86.6, 'Zehn Sekunden ohne Muscheln.'],
  [86.8, 88.8, 'Aber er hat endlich seine Auster.'],
];
