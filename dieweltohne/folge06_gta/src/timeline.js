// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Eine Woche nach dem Release (19.11.2026) verschwindet GTA 6 für 10 Sekunden – um 23:41 Uhr.
// Millionen Konsolen gehen gleichzeitig aus. Gedankenexperiment: Das Stromnetz verkraftet den Sprung nicht.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},      // Über die Schulter: Verfolgungsjagd auf dem Fernseher
  {id: 'play', t0: 3.5, t1: 10},      // Sein Gesicht im Fernsehlicht, Controller in den Händen
  {id: 'vanish', t0: 10, t1: 17},     // Stufe 1: Spiel weg – Startbildschirm, blaues Licht, Schock
  {id: 'papa', t0: 17, t1: 24},       // Stufe 2: Nebenan – Papa springt vom Sofa, Mama in der Tür
  {id: 'street', t0: 24, t1: 31},     // Stufe 3: Er geht seit Release zum ersten Mal raus – Auto bremst
  {id: 'control', t0: 31, t1: 39},    // Stufe 4: Netzleitstelle – Frequenz steigt
  {id: 'city', t0: 39, t1: 47},       // Stufe 5: Stadt von oben – Viertel für Viertel dunkel
  {id: 'europe', t0: 47, t1: 55},     // Stufe 6: Europa bei Nacht – die Lichter gehen aus
  {id: 'dark', t0: 55, t1: 64},       // Stufe 7: Sein Zimmer, stockdunkel – Handylicht
  {id: 'back', t0: 64, t1: 72},       // Stufe 7: Der Strom kommt zurück
  {id: 'blast', t0: 72, t1: 80},      // Stufe 7: Fernseher springt an – volle Lautstärke
  {id: 'mom', t0: 80, t1: 90},        // Stufe 7: Mama in der Tür
];
export const VANISH = 10.0;    // Spiel weg
export const RETURN = 55.0;    // Spiel wieder da (Weltzeit 10 s, über die Einstellungen gedehnt)
const WK = [[10, 10], [17, 9.0], [24, 7.8], [31, 6.4], [39, 4.6], [47, 2.4], [55, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) { const [a, va] = WK[i - 1], [b, vb] = WK[i]; return va + (vb - va) * (T - a) / (b - a); }
  return 0;
}
// Wichtige Momente
export const PAPA_UP = 18.6, BRAKE = 26.6, STOP = 28.2, FREQ0 = 32.0, CITY_OUT = 40.5, EU_OUT = 48.4, LIGHT_OFF = 39.2,
  FLASH_ON = 58.6, POWER_BACK = 66.0, TV_ON = 73.6, DOOR = 81.0, CEIL = 82.4, TV_OFF = 84.6;

export const STAGES = ['HARMLOS', 'PEINLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {vanish: 1, papa: 2, street: 3, control: 4, city: 5, europe: 6, dark: 7, back: 7, blast: 7, mom: 7};

export const CAPTIONS = [
  [3.9, 6.6, 'Eine Woche nach Release.'],
  [6.8, 9.8, 'Noch eine Mission. Dann schlafen. Ganz sicher.'],
  [10.5, 12.8, 'Weg. Einfach weg.'],
  [13.0, 16.7, 'Letzter Speicherstand: vor drei Stunden.'],
  [17.4, 20.2, 'Nebenan: Papa. „Ich spiel nur kurz mit.“'],
  [20.5, 23.7, 'Er spielt seit 19 Uhr.'],
  [24.4, 27.0, 'Er war seit Release nicht mehr draußen.'],
  [27.3, 30.8, 'Im echten Leben gibt es keinen Neustart.'],
  [31.4, 34.8, 'Jede Konsole zieht beim Zocken rund 200 Watt.'],
  [35.0, 38.8, 'Millionen gehen gleichzeitig aus. Dem Stromnetz fehlt plötzlich Verbrauch.'],
  [39.4, 42.8, 'Gedankenexperiment: Kraftwerke schalten sich zum Schutz ab.'],
  [43.0, 46.8, 'Ein Viertel nach dem anderen wird dunkel.'],
  [47.4, 50.8, 'Im April 2025 fiel in Spanien und Portugal stundenlang der Strom aus.'],
  [51.0, 54.7, 'Diesmal: halb Europa.'],
  [55.4, 58.4, 'Die zehn Sekunden sind längst vorbei.'],
  [58.7, 63.6, 'GTA 6 ist zurück. Der Strom nicht.'],
  [64.4, 67.2, '2:13 Uhr.'],
  [67.5, 71.6, 'Der Strom kommt zurück. Viertel für Viertel.'],
  [72.4, 75.6, 'Und mit ihm: der Fernseher.'],
  [75.8, 79.6, 'Auf voller Lautstärke.'],
  [80.6, 82.6, 'Mama.'],
  [83.0, 86.4, '„Konsole. Sofort. Bis Weihnachten.“'],
  [86.7, 89.7, 'Das war der echte Weltuntergang.'],
];
