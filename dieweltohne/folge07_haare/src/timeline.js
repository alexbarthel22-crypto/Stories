// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden verschwindet jedes Haar der Welt – auch Wolle, Fell und die Sinneshärchen der Haarzellen im Innenohr.
// Ohne Haarzellen: kein Hören, kein Gleichgewicht. Die Haare kommen zurück, die Haarzellen nicht (Säugetiere bilden sie nicht nach).
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},          // Selfie-Video: Haare werfen vor der Handykamera
  {id: 'wait', t0: 3.5, t1: 10},          // weiter Selfie, Countdown läuft
  {id: 'selfie', t0: 10, t1: 17},         // Stufe 1: Glatze, keine Augenbrauen, Nacktkatze
  {id: 'winter', t0: 17, t1: 24},         // Stufe 2: Wollpullover, Mützen, Schals weg – im Schnee
  {id: 'festival', t0: 24, t1: 31},       // Stufe 3: Festival – alle taub, die Menge kippt um
  {id: 'parkour', t0: 31, t1: 38},        // Stufe 4: Parkour-Sprung zwischen zwei Dächern
  {id: 'birds', t0: 38, t1: 46},          // Stufe 5: Starenschwarm fällt vom Himmel
  {id: 'crane', t0: 46, t1: 56},          // Stufe 6: Kranführer verliert das Gleichgewicht – Kran stürzt
  {id: 'fest_after', t0: 56, t1: 64},     // Stufe 7: Haare zurück – aber alles bleibt still
  {id: 'street_after', t0: 64, t1: 76},   // Stufe 7: Straße – niemand kann mehr gerade stehen
  {id: 'final', t0: 76, t1: 90},          // Stufe 7: zurück im Zimmer – Haare da, Gehör weg
];

export const VANISH = 10.0;   // Haare verschwinden
export const RETURN = 56.0;   // Haare zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

const WK = [[10, 10], [17, 9.3], [24, 8.4], [31, 7.4], [38, 6.2], [46, 4.2], [56, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}
// Wichtige Momente (Videozeit) für Bild und Ton
export const DEAF = 24.0;          // ab hier: Welt wird still (Ton gedämpft)
export const CROWD_FALL = 26.2;    // Festival: Menge kippt
export const JUMP = 33.0, MISS = 34.1;           // Parkour: Absprung, verfehlte Kante
export const FLOCK_BREAK = 40.6;   // Schwarm bricht auseinander
export const SWING = 49.0, CRANE_HIT = 51.6, CRANE_FALL = 52.6;  // Kran

export const STAGES = ['PEINLICH', 'ÄRGERLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {selfie: 1, winter: 2, festival: 3, parkour: 4, birds: 5, crane: 6, fest_after: 7, street_after: 7, final: 7};

export const CAPTIONS = [
  [4.0, 6.8, 'Rund 100.000 Haare auf dem Kopf. Perfekt gestylt.'],
  [7.0, 9.8, 'Was, wenn alle Haare der Welt verschwinden? Nur zehn Sekunden.'],
  [10.5, 13.4, 'Weg. Alle. Auch Augenbrauen und Wimpern.'],
  [13.6, 16.8, 'Und die Katze? Ist jetzt eine Nacktkatze.'],
  [17.4, 20.4, 'Wolle ist auch nur Haar. Von Schafen.'],
  [20.6, 23.8, 'Pullover, Mützen, Schals: weg. Bei minus fünf Grad.'],
  [24.4, 27.4, 'Doch im Innenohr sitzen Haarzellen mit winzigen Sinneshärchen.'],
  [27.6, 30.8, 'Ohne sie hört niemand etwas. Und keiner hält das Gleichgewicht.'],
  [31.4, 34.4, 'Dein Gleichgewichtssinn sitzt im Innenohr.'],
  [34.6, 37.8, 'Mitten im Sprung weiß dein Körper nicht mehr, wo oben ist.'],
  [38.4, 41.6, 'Auch Vögel hören und balancieren mit Haarzellen.'],
  [41.8, 45.8, 'Zehntausende Stare verlieren gleichzeitig die Orientierung.'],
  [46.4, 49.8, 'Ein Kranführer, 80 Meter über der Stadt.'],
  [50.0, 55.8, 'Er weiß nicht mehr, wo oben ist. Die Last schwingt weiter.'],
  [56.4, 59.6, 'Die Haare sind zurück.'],
  [59.8, 63.8, 'Aber Haarzellen wachsen beim Menschen nicht nach.'],
  [64.4, 67.8, 'Rund 15.000 pro Ohr. Für immer weg.'],
  [68.0, 71.8, 'Laufen klappt nur noch mit Blick auf den Boden.'],
  [72.0, 75.8, 'Es gibt etwa eine Million Cochlea-Implantate. Wir bräuchten acht Milliarden.'],
  [76.4, 79.8, 'Kein Gespräch. Keine Musik. Nie wieder.'],
  [80.2, 84.0, 'Zehn Sekunden ohne Haare.'],
  [84.4, 89.4, 'Und die Welt bleibt für immer still.'],
];
